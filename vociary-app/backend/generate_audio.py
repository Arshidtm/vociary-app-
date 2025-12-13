from gtts import gTTS
import os

text = "Hello, this is a test entry for the Voicary application. I am feeling productive and happy today. I hope to complete the database integration successfully."
tts = gTTS(text=text, lang='en')
tts.save("test_audio.mp3")
print("test_audio.mp3 created successfully.")
