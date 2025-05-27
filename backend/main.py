import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel
import openai
import os
from tempfile import NamedTemporaryFile
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI - replace with your actual API key
openai.api_key = os.getenv("OPENAI_API_KEYs")

# Constants for Simli API
SIMLI_SESSION_ID = os.getenv("SIMLI_SESSION_ID")
SIMLI_TOKEN = os.getenv("SIMLI_TOKEN")

# Define request models
class TextToSpeech(BaseModel):
    text: str
    voice_id: str = "default"

class TextRequest(BaseModel):
    text: str

@app.get("/api/room-url")
async def get_room_url():
    """
    Python function to fetch the room URL from Simli API
    """
    try:
        url = f"https://api.simli.ai/session/{SIMLI_SESSION_ID}/{SIMLI_TOKEN}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"API request failed with status: {response.status_code}")
            
        data = response.json()
        return {"roomUrl": data.get("roomUrl")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/avatar-speak")
async def avatar_speak(tts: TextToSpeech):
    """
    Make the avatar in the Simli room speak a given text
    """
    try:
        url = f"https://api.simli.ai/session/{SIMLI_SESSION_ID}/{SIMLI_TOKEN}/speak"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        data = {
            "text": tts.text,
            "voiceId": tts.voice_id
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"API request failed with status: {response.status_code}")
            
        return {"success": True, "message": "Avatar is speaking the text"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-response")
async def generate_response(request: TextRequest):
    """
    Generate a response from OpenAI based on user input
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or another suitable model
            messages=[
                {"role": "system", "content": "You are a helpful assistant speaking through a digital avatar. Keep responses concise and engaging, ideally under 3 sentences."},
                {"role": "user", "content": request.text}
            ],
            max_tokens=150
        )
        
        generated_text = response.choices[0].message.content
        return {"response": generated_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

@app.post("/api/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Convert speech from an audio file to text
    """
    try:
        # Save the uploaded file temporarily
        with NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            audio_content = await audio_file.read()
            temp_file.write(audio_content)
        
        # Use speech recognition to convert to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {str(e)}")

@app.post("/api/complete-conversation-flow")
async def complete_conversation_flow(audio_file: UploadFile = File(...)):
    """
    Complete workflow: Speech → Text → OpenAI → Avatar speaks
    """
    try:
        # Step 1: Convert speech to text
        speech_result = await speech_to_text(audio_file)
        user_text = speech_result["text"]
        
        # Step 2: Generate response with OpenAI
        ai_response = await generate_response(TextRequest(text=user_text))
        response_text = ai_response["response"]
        
        # Step 3: Make avatar speak the response
        await avatar_speak(TextToSpeech(text=response_text))
        
        return {
            "user_input": user_text,
            "ai_response": response_text,
            "status": "Avatar is speaking the response"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)