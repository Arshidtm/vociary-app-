# backend/app/api/endpoints.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession # Use AsyncSession
from datetime import date
from typing import List

# Import models, schemas, services, and database utilities
from ..db.database import get_db_async # <-- Use the async dependency
from ..db import models
from ..schemas import entry as schemas
from ..services import diary_service

# Define the API router
router = APIRouter(
    prefix="/entries",
    tags=["Entries"],
    responses={404: {"description": "Not found"}},
)

# --- Dependency Placeholder ---
# We need this to ensure the API works for now, before full auth is implemented.
async def get_current_user_id(db: AsyncSession = Depends(get_db_async)):
    # --- TEMPORARY MOCK ---
    # In a real app, this would be secured by JWT/OAuth.
    # For now, we ensure a user with ID 1 exists, or create a mock user.
    user = await db.get(models.User, 1) 
    
    if not user:
        # Create a mock user (and a default diary) for development purposes
        mock_user = models.User(
            id=1, 
            email="test@aurajournal.dev", 
            username="AuraUser", 
            hashed_password="mock"
        )
        db.add(mock_user)
        
        default_diary = models.Diary(
            owner_id=1,
            name="My Daily Reflections",
            description="The primary diary for daily voice entries."
        )
        db.add(default_diary)
        
        await db.commit()
        print("Created MOCK User and Default Diary with ID 1.")
        
    return 1 # Always return the hardcoded user ID for now


# ====================================================================
# 1. AUDIO PROCESSING & PREVIEW (Initial Flow)
# ====================================================================

@router.post("/process_audio", response_model=schemas.EntryUpdatePreview)
async def process_new_audio(
    audio_file: UploadFile = File(..., description="Audio recording of the day's events"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Accepts an audio file, transcribes it, and generates/updates a diary entry preview.
    """
    
    # 1. Transcribe Audio (STT Service call)
    try:
        transcript = await diary_service.get_transcription(audio_file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Transcription failed: {e}"
        )
    
    # 2. Check for Existing Entry (We'll check for ANY entry for the day first)
    today = date.today()
    existing_entry = await diary_service.get_entry_by_date(db, user_id=current_user_id, entry_date=today)
    
    # 3. Use LLM to Process/Integrate Content
    if existing_entry:
        # Modification Flow: Integrate new content into the existing entry's content
        original_content = existing_entry.content
        updated_content = await diary_service.integrate_new_content(transcript, original_content)
        diary_id = existing_entry.diary_id
    else:
        # Initial Flow: Generate a summary from the raw transcript
        original_content = ""
        updated_content = await diary_service.generate_initial_entry(transcript)
        # Assuming the first diary found is the default one (ID 1), or we use a fallback
        diaries = await diary_service.get_diaries_for_user(db, current_user_id)
        if not diaries:
             raise HTTPException(status_code=500, detail="No diaries found for user.")
        diary_id = diaries[0].id # Assign to the first diary found
        
    return schemas.EntryUpdatePreview(
        original_content=original_content,
        updated_preview_content=updated_content,
        entry_date=today,
        diary_id=diary_id
    )


# ====================================================================
# 2. COMMIT ENTRY (Final Flow)
# ====================================================================

@router.post("/commit", response_model=schemas.Entry)
async def commit_diary_entry(
    entry_data: schemas.EntryCreate, # Contains final content and selected diary_id
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Commits the final, user-verified diary entry to the database.
    Handles both creation and updating based on date/user/diary_id.
    """
    
    # Check if an entry already exists for the unique key (user_id, entry_date, diary_id)
    entry = await diary_service.get_entry_by_key(
        db, 
        user_id=current_user_id, 
        entry_date=entry_data.entry_date, 
        diary_id=entry_data.diary_id
    )

    if entry:
        # UPDATE existing entry (Same-day modification)
        updated_entry = await diary_service.update_entry(
            db=db, 
            entry_id=entry.id, 
            new_content=entry_data.content
        )
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Entry not found during update.")
        return updated_entry
    else:
        # CREATE new entry (Initial save)
        new_entry = await diary_service.create_entry(
            db=db, 
            user_id=current_user_id, 
            entry_data=entry_data
        )
        return new_entry


# ====================================================================
# 3. UTILITY ENDPOINTS
# ====================================================================

@router.get("/{entry_date}", response_model=List[schemas.Entry])
async def read_entries_by_date(
    entry_date: date,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Retrieves all diary entries for a specific date and user (across all diaries).
    """
    entries = await diary_service.get_entries_by_date(db, user_id=current_user_id, entry_date=entry_date)
    return entries