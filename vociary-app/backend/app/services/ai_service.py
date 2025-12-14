# backend/app/services/ai_service.py

from fastapi import UploadFile
import httpx 
from typing import Optional
from ..core.settings import settings # <-- Securely import settings
import io

# --- Configuration is now loaded from settings ---
GROQ_API_KEY = settings.GROQ_API_KEY
LLM_TRANSCRIPTION_MODEL = settings.STT_MODEL_NAME
LLM_GENERATION_MODEL = settings.LLM_MODEL_NAME


# ====================================================================
# 1. Speech-to-Text (STT) Function (USING GROQ API)
# ====================================================================

async def get_transcription(audio_file: UploadFile) -> str:
    """
    Sends the audio file to the Groq ASR service and returns the raw text transcript.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Placeholder for development without API key
        return "Today was a really long day. I had a big presentation, and it went much better than I expected. I felt a lot of relief afterwards, and I celebrated with a nice cup of tea."

    try:
        audio_data = await audio_file.read()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            audio_io = io.BytesIO(audio_data)
            
            files = {
                'file': (audio_file.filename, audio_io, audio_file.content_type)
            }
            data = {"model": LLM_TRANSCRIPTION_MODEL}
            
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions", 
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("text", "Error: No text returned.")

    except httpx.HTTPStatusError as e:
        raise Exception(f"Groq STT call failed with status {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during transcription: {e}")


# ====================================================================
# 2. LLM Core Function (Generic Call - GROQ)
# ====================================================================

async def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Handles the asynchronous API call to the Groq LLM for text generation/integration.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Placeholder response for development
        return f"[[GROQ MOCK OUTPUT]]: The refined entry should be:\n\n{user_prompt[:200]}..."

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": LLM_GENERATION_MODEL, 
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
            }
            
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']

    except httpx.HTTPStatusError as e:
        raise Exception(f"Groq LLM call failed: {e.response.text}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during LLM call: {e}")


# ====================================================================
# 3. LLM Task-Specific Functions
# ====================================================================

async def generate_initial_entry(transcript: str) -> str:
    """
    Analyzes a raw transcript and generates a coherent, reflective diary entry.
    """
    system_prompt = (
        "You are an empathetic, reflective journal AI. Your task is to analyze the user's raw transcript "
        "of their day and synthesize it into a coherent, personal, first-person diary entry. "
        "Focus on emotions, key events, and future tasks. Maintain a warm, thoughtful tone."
    )
    user_prompt = f"Raw Transcript to be transformed into a diary entry:\n\n{transcript}"
    
    return await _call_llm(system_prompt, user_prompt)

async def integrate_new_content(new_transcript: str, existing_entry: str) -> str:
    """
    Integrates a new audio transcript into an existing diary entry for the same day.
    """
    system_prompt = (
        "The user has added new reflections to an existing diary entry for today. "
        "Your task is to seamlessly integrate the 'New Content' into the 'Existing Entry' "
        "to create a single, cohesive, updated diary entry. Do not lose any information "
        "from the existing entry, only enhance and update it with the new content."
    )
    user_prompt = (
        f"Existing Entry:\n---\n{existing_entry}\n---\n\n"
        f"New Content to Integrate:\n---\n{new_transcript}\n---"
    )

    return await _call_llm(system_prompt, user_prompt)

async def refine_entry(current_content: str, selected_text: str, user_instruction: str) -> str:
    """
    Refines the diary entry based on specific user instructions applied to a selected segment.
    """
    system_prompt = (
        "You are an expert editor for a personal diary. Your goal is to modify the 'Current Entry' "
        "based on the user's specific instruction. "
        "The user has highlighted a specific part of the text ('Selected Text') and provided an "
        "instruction ('User Instruction/Comment') on how to change it. "
        "You must rewrite the entry to incorporate this change naturally. "
        "Maintain the original voice and context. Return ONLY the fully updated entry text."
    )
    
    user_prompt = (
        f"Current Entry:\n---\n{current_content}\n---\n\n"
        f"Selected Text (to be changed): \"{selected_text}\"\n"
        f"User Instruction/Comment: \"{user_instruction}\"\n\n"
        f"Please provide the updated full entry:"
    )

    return await _call_llm(system_prompt, user_prompt)

async def generate_daily_reflection(entry_text: str) -> dict:
    """
    Analyzes the complete diary entry to generate structured insights:
    - Mood Score (1-10) & Emoji
    - Key Takeaways (List)
    - Action Item (Single actionable step)
    """
    import json
    
    system_prompt = (
        "You are an insightful personal growth assistant. Analyze the user's diary entry and "
        "extract structured insights. You must return ONLY a valid JSON object with the following keys:\n"
        "- 'mood_score': an integer from 1 (lowest) to 10 (highest).\n"
        "- 'mood_emoji': a single emoji representing the dominant mood.\n"
        "- 'takeaways': a list of 3 brief, bullet-point style takeaways/observations.\n"
        "- 'action_item': a single, concrete, actionable step for tomorrow based on the entry.\n\n"
        "Do not include any markdown formatting (like ```json), just the raw JSON string."
    )
    user_prompt = f"Diary Entry to Analyze:\n\n{entry_text}"

    response_text = await _call_llm(system_prompt, user_prompt)
    
    # Clean up POTENTIAL markdown backticks if the model ignores instruction
    cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "mood_score": 5,
            "mood_emoji": "😐",
            "takeaways": ["Could not parse insights.", "Please try again later.", "Keep journaling!"],
            "action_item": "Reflect on your day manually."
        }