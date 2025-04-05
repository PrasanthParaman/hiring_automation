# main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS
import os

from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Init FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup LLM
llm = ChatOpenAI(temperature=0.7)

# Keep simple history for now
conversation_history = []

class Input(BaseModel):
    user_input: str

@app.post("/interview")
async def interview(input: Input):
    global conversation_history

    # Create prompt with a basic history format
    conversation_history.append({"role": "user", "content": input.user_input})

    # Get response from the model
    response = llm.invoke(conversation_history)

    # Save response to history
    conversation_history.append({"role": "assistant", "content": response.content})

    # Text-to-speech
    tts = gTTS(text=response.content, lang="en")
    tts.save("response.mp3")

    return JSONResponse(content={"response": response.content})

@app.get("/speak")
async def speak():
    if os.path.exists("response.mp3"):
        return FileResponse("response.mp3", media_type="audio/mpeg")
    return JSONResponse(content={"error": "Audio not found"}, status_code=404)