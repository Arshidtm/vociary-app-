# backend/app/api/endpoints.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List

# Import models, schemas, services, and database utilities
from ..db.database import get_db_async
from ..db import models
from ..schemas import entry as schemas
from ..services import diary_service
from .deps import get_current_user 

# Define the API router
router = APIRouter(
    prefix="/entries",
    tags=["Entries"],
    responses={404: {"description": "Not found"}},
)

@router.post("/refine", response_model=schemas.RefinementResponse)
async def refine_entry(
    request: schemas.RefinementRequest,
    current_user: models.User = Depends(get_current_user),
):
    """
    Refines a diary entry based on user instructions (comment on selected text).
    """
    try:
        updated_text = await diary_service.refine_entry(
            current_content=request.current_content,
            selected_text=request.selected_text,
            user_instruction=request.user_instruction
        )
        return schemas.RefinementResponse(updated_content=updated_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {e}")

# ====================================================================
# 1. AUDIO PROCESSING & PREVIEW (Initial Flow)
# ====================================================================

@router.post("/process_audio", response_model=schemas.EntryUpdatePreview)
async def process_new_audio(
    audio_file: UploadFile = File(..., description="Audio recording of the day's events"),
    current_user: models.User = Depends(get_current_user),
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
    existing_entry = await diary_service.get_entry_by_date(db, user_id=current_user.id, entry_date=today)
    
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
        diaries = await diary_service.get_diaries_for_user(db, current_user.id)
        if not diaries:
             # Create a default diary if none exists (Auto-provisioning)
             default_diary = models.Diary(
                owner_id=current_user.id,
                name="My Daily Reflections",
                description="The primary diary for daily voice entries."
             )
             db.add(default_diary)
             await db.commit()
             await db.refresh(default_diary)
             diary_id = default_diary.id
        else:
            diary_id = diaries[0].id 
        
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
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Commits the final, user-verified diary entry to the database.
    Handles both creation and updating based on date/user/diary_id.
    """
    
    # Check if an entry already exists for the unique key (user_id, entry_date, diary_id)
    entry = await diary_service.get_entry_by_key(
        db, 
        user_id=current_user.id, 
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
            user_id=current_user.id, 
            entry_data=entry_data
        )
        return new_entry


# ====================================================================
# 3. UTILITY ENDPOINTS
# ====================================================================

@router.get("/history", response_model=List[schemas.Entry])
async def read_entry_history(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Retrieves the user's recent diary entries (for the Book View).
    """
    entries = await diary_service.get_recent_entries(db, user_id=current_user.id, limit=limit, offset=skip)
    return entries

@router.get("/{entry_date}", response_model=List[schemas.Entry])
async def read_entries_by_date(
    entry_date: date,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Retrieves all diary entries for a specific date and user (across all diaries).
    """
    entries = await diary_service.get_entries_by_date(db, user_id=current_user.id, entry_date=entry_date)
    return entries

@router.get("/history", response_model=List[schemas.Entry])
async def read_entry_history(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Retrieves the user's recent diary entries (for the Book View).
    """
    entries = await diary_service.get_recent_entries(db, user_id=current_user.id, limit=limit, offset=skip)
    return entries

# ====================================================================
# 4. REFLECTION & INSIGHTS (New Feature)
# ====================================================================

from pydantic import BaseModel

class ReflectionResponse(BaseModel):
    mood_score: int
    mood_emoji: str
    takeaways: List[str]
    action_item: str

@router.post("/reflect/{entry_id}", response_model=ReflectionResponse)
async def generate_reflection(
    entry_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Generates AI-powered insights for a specific journal entry.
    """
    # 1. Fetch the entry
    entry = await db.get(models.Entry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this entry")

    # 2. Call AI Service
    from ..services import ai_service
    try:
        insights = await ai_service.generate_daily_reflection(entry.content)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {e}")