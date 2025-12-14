# backend/app/services/diary_service.py (ASYNC VERSION)

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession # Use AsyncSession
from datetime import date
from typing import List, Optional

# Import SQLAlchemy Models and Pydantic Schemas
from ..db import models
from ..schemas import entry as schemas 
from . import ai_service # Import the AI Service to orchestrate the flow


# ====================================================================
# A. CORE ENTRY CRUD OPERATIONS (ASYNC)
# ====================================================================

async def get_entry_by_key(db: AsyncSession, user_id: int, entry_date: date, diary_id: int) -> Optional[models.Entry]:
    """
    Retrieves a single entry based on the unique combination of user, date, and diary.
    """
    stmt = select(models.Entry).filter(
        models.Entry.user_id == user_id,
        models.Entry.entry_date == entry_date,
        models.Entry.diary_id == diary_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_entry_by_date(db: AsyncSession, user_id: int, entry_date: date) -> Optional[models.Entry]:
    """
    Retrieves the first entry for a given user on a given date (used to check if any entry exists).
    """
    stmt = select(models.Entry).filter(
        models.Entry.user_id == user_id,
        models.Entry.entry_date == entry_date
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_entry(db: AsyncSession, user_id: int, entry_data: schemas.EntryCreate) -> models.Entry:
    """
    Creates a new diary entry in the database.
    """
    db_entry = models.Entry(
        user_id=user_id,
        content=entry_data.content,
        entry_date=entry_data.entry_date,
        diary_id=entry_data.diary_id
    )
    db.add(db_entry)
    await db.commit() # Await commit
    await db.refresh(db_entry) # Await refresh
    return db_entry

async def update_entry(db: AsyncSession, entry_id: int, new_content: str) -> Optional[models.Entry]:
    """
    Updates the content of an existing diary entry (used for same-day modification).
    """
    stmt = update(models.Entry).where(models.Entry.id == entry_id).values(content=new_content).returning(models.Entry)
    
    result = await db.execute(stmt)
    await db.commit()
    
    # We must fetch the updated object for the return value
    updated_entry = result.scalars().first() 
    return updated_entry

async def get_entries_by_date(db: AsyncSession, user_id: int, entry_date: date) -> List[models.Entry]:
    """
    Retrieves all entries for a specific user on a specific date (across all diaries).
    """
    stmt = select(models.Entry).filter(
        models.Entry.user_id == user_id,
        models.Entry.entry_date == entry_date
    ).order_by(models.Entry.id) # Simple ordering
    
    result = await db.execute(stmt)
    return result.scalars().all()


# ====================================================================
# B. AI ORCHESTRATION FUNCTIONS (NO CHANGE NEEDED HERE)
# ====================================================================

async def get_transcription(audio_file) -> str:
    """Wrapper for the STT function in ai_service."""
    return await ai_service.get_transcription(audio_file)

async def integrate_new_content(new_transcript: str, existing_content: str) -> str:
    """Wrapper for the LLM integration function."""
    return await ai_service.integrate_new_content(new_transcript, existing_content)

async def generate_initial_entry(transcript: str) -> str:
    """Wrapper for the LLM initial generation function."""
    return await ai_service.generate_initial_entry(transcript)

async def refine_entry(current_content: str, selected_text: str, user_instruction: str) -> str:
    """Wrapper for the LLM refinement function."""
    return await ai_service.refine_entry(current_content, selected_text, user_instruction)

async def get_recent_entries(db: AsyncSession, user_id: int, limit: int = 10, offset: int = 0) -> List[models.Entry]:
    """Retrieves recent diary entries for a user, ordered by date descending."""
    stmt = select(models.Entry).filter(
        models.Entry.user_id == user_id
    ).order_by(models.Entry.entry_date.desc()).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()



# ====================================================================
# C. DIARY CRUD (ASYNC)
# ====================================================================

async def get_diaries_for_user(db: AsyncSession, user_id: int) -> List[models.Diary]:
    """Retrieves all diaries belonging to a user."""
    stmt = select(models.Diary).filter(models.Diary.owner_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_diary(db: AsyncSession, user_id: int, diary_data: schemas.DiaryBase) -> models.Diary:
    """Creates a new diary."""
    db_diary = models.Diary(
        owner_id=user_id,
        name=diary_data.name,
        description=diary_data.description
    )
    db.add(db_diary)
    await db.commit()
    await db.refresh(db_diary)
    return db_diary