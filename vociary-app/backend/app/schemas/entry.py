from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from pydantic import ConfigDict

# --- 1. User Schemas ---

class UserBase(BaseModel):
    """Base schema for user creation (e.g., used for registration)"""
    email: str
    username: str

class User(UserBase):
    """Schema for user data retrieved from the database"""
    id: int
    # is_active: bool = True

    # class Config:
    #     # Allows Pydantic to read ORM objects (e.g., SQLAlchemy models)
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)


# --- 2. Diary Schemas (For multiple personal diaries) ---

class DiaryBase(BaseModel):
    """Base schema for creating a new specific diary"""
    name: str  # e.g., "Personal Thoughts", "Work Log", "Travel"
    description: Optional[str] = None

class Diary(DiaryBase):
    """Schema for a diary retrieved from the database"""
    id: int
    owner_id: int

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)
# --- 3. Entry Schemas (The core diary content) ---

class EntryBase(BaseModel):
    """Base schema for the generated diary content before saving (used for preview)"""
    content: str
    diary_id: int
    entry_date: date  # Must be the current date as per requirement

class EntryCreate(EntryBase):
    """Schema for the final request to commit the entry"""
    # No changes from EntryBase, but explicitly named for the POST request
    pass

class Entry(EntryBase):
    """Schema for a complete entry retrieved from the database"""
    id: int
    user_id: int
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

# --- 4. Special Schema for Audio Processing Request ---

class AudioProcessRequest(BaseModel):
    """Schema for the initial request when a user uploads audio"""
    # Note: The actual audio file will be handled separately via FastAPI's File/UploadFile,
    # but this schema can hold any associated metadata.
    user_id: int
    # Optionally, a hint for the LLM
    mood_hint: Optional[str] = None 


# --- 5. Special Schema for Update Preview ---

class EntryUpdatePreview(BaseModel):
    """Schema to send back to the user to show the update before committing"""
    original_content: str
    updated_preview_content: str
    entry_date: date
    diary_id: int