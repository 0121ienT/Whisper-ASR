import asyncio
import io
import numpy as np
import wave
import websockets
import sounddevice as sd
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
from transformers import pipeline
from base64 import b64decode
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")

async def process_audio(audio_chunk : bytes):
    """Process audio chunk and return transcribed text."""
    with open("./output/audio.wav", "wb") as f:
        f.write(audio_chunk)
    return transcriber("./output/audio.wav")["text"]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            audio_chunk = b64decode(data)
            text = await process_audio(audio_chunk)
            print(3)
            if text:
                await websocket.send_text(text)
            else:
                await websocket.send_text("")
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "Speech Recognition WebSocket Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)