# backend/tests/test_entries.py

import pytest
from httpx import AsyncClient
from datetime import date
import io
import json

# Mark all tests as asynchronous
pytestmark = pytest.mark.anyio 

# Mock Data (Matches the mock user creation in endpoints.py)
MOCK_USER_ID = 1 
MOCK_DIARY_ID = 1

# ====================================================================
# A. Test Audio Processing Endpoint
# ====================================================================

async def test_process_audio_first_entry(client: AsyncClient):
    """
    Test the flow for creating the first entry of the day: 
    Audio -> Mock Transcription -> Mock LLM Generation.
    """
    
    url = "/api/v1/entries/process_audio"
    
    # 1. Simulate an audio file upload
    # The file content doesn't matter since the service is mocked
    file_data = b"mock audio content"
    files = {'audio_file': ('test_audio.mp3', io.BytesIO(file_data), 'audio/mp3')}
    
    response = await client.post(url, files=files)
    
    assert response.status_code == 200
    data = response.json()
    
    # 2. Check the response structure and mocked content
    expected_transcript = "The presentation was great. I also ate a delicious sandwich for lunch."
    expected_content = f"Refined entry based on: {expected_transcript}"
    
    assert data["entry_date"] == date.today().isoformat()
    assert data["diary_id"] == MOCK_DIARY_ID
    assert data["original_content"] == ""
    assert data["updated_preview_content"] == expected_content

# ====================================================================
# B. Test Commit (Create) Endpoint
# ====================================================================

async def test_commit_new_entry(client: AsyncClient):
    """
    Test committing a new entry (creation path).
    """
    url = "/api/v1/entries/commit"
    today = date.today().isoformat()
    
    new_entry_data = {
        "content": "This is the final, user-approved entry content.",
        "entry_date": today,
        "diary_id": MOCK_DIARY_ID 
    }
    
    response = await client.post(url, json=new_entry_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check if entry was created correctly
    assert data["content"] == new_entry_data["content"]
    assert data["user_id"] == MOCK_USER_ID
    assert "id" in data # Check for primary key
    
# ====================================================================
# C. Test Commit (Update) Endpoint (Requires previous creation)
# ====================================================================

async def test_commit_existing_entry_updates(client: AsyncClient):
    """
    Test committing an entry for the same key (update path).
    This relies on the rollback to run clean after the previous test.
    """
    # 1. Create an entry first (setup for the update)
    today = date.today().isoformat()
    initial_content = "First entry of the day."
    
    await client.post(
        "/api/v1/entries/commit", 
        json={"content": initial_content, "entry_date": today, "diary_id": MOCK_DIARY_ID}
    )

    # 2. Now attempt to commit again with the same keys (This should trigger an UPDATE)
    new_content = "This is the updated and finalized entry content."
    update_data = {
        "content": new_content,
        "entry_date": today,
        "diary_id": MOCK_DIARY_ID 
    }
    
    response = await client.post("/api/v1/entries/commit", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check if the content was updated
    assert data["content"] == new_content
    
    # 3. Read the entry back to confirm only one exists (Optional but good)
    read_response = await client.get(f"/api/v1/entries/{today}")
    assert read_response.status_code == 200
    assert len(read_response.json()) == 1 

# ====================================================================
# D. Test Read Entries Endpoint
# ====================================================================

async def test_read_entries_by_date(client: AsyncClient):
    """
    Test retrieving all entries for a given date.
    """
    # Create two entries for the read test
    today = date.today().isoformat()
    
    await client.post(
        "/api/v1/entries/commit", 
        json={"content": "Test Entry 1", "entry_date": today, "diary_id": MOCK_DIARY_ID}
    )
    
    # Since we only mocked one diary, let's just commit one to keep it simple.
    
    read_response = await client.get(f"/api/v1/entries/{today}")
    
    assert read_response.status_code == 200
    entries = read_response.json()
    
    # Assert that one entry was returned (the one created in the setup of this test)
    assert len(entries) == 1
    assert entries[0]["content"] == "Test Entry 1"