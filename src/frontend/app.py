import streamlit as st
import sounddevice as sd
import numpy as np
import asyncio
import websockets
import base64
import queue
import threading
import time
import wave
import io

from config import SAMPLE_RATE, CHUNK_DURATION, CHUNK_SIZE

st.title("Realtime Speech Recognition")

WS_URL = "ws://localhost:8000/ws"

audio_queue = queue.Queue()

recording = False

def audio_callback(input, frames, time, status):
    """Callback function for audio recording."""
    if recording:
        audio_queue.put(input.copy())

def record_audio():
    """Record audio and put chunks into queue."""
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback,
        blocksize=CHUNK_SIZE
    )
    with stream:
        while recording:
            time.sleep(0.1)

async def send_audio_to_websocket():
    """Send audio chunks to WebSocket and receive transcribed text."""
    async with websockets.connect(WS_URL) as websocket:
        while recording:
            try:
                # Get audio chunk from queue
                if not audio_queue.empty():
                    audio_chunk = audio_queue.get()
                    
                    # Convert to WAV format and encode to base64
                    audio_chunk = (audio_chunk * 32768).astype(np.int16)
                    wav_io = io.BytesIO()
                    with wave.open(wav_io, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # 16-bit
                        wf.setframerate(SAMPLE_RATE)
                        wf.writeframes(audio_chunk.tobytes())
                    wav_bytes = wav_io.getvalue()
                    encoded = base64.b64encode(wav_bytes).decode('utf-8')
                    await websocket.send(encoded)
                    text = await websocket.recv()
                    if text:
                        st.session_state.transcription.append(text)
                    
            except Exception as e:
                st.error(f"WebSocket error: {e}")
                break
            await asyncio.sleep(0.1)

def start_recording():
    """Start recording and WebSocket communication."""
    global recording
    recording = True
    st.session_state.transcription = []
    
    # Start audio recording in a separate thread
    threading.Thread(target=record_audio, daemon=True).start()
    
    # Run WebSocket communication
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_audio_to_websocket())

def stop_recording():
    """Stop recording."""
    global recording
    recording = False

# Initialize session state
if 'transcription' not in st.session_state:
    st.session_state.transcription = []

# UI controls
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Recording"):
        start_recording()
with col2:
    if st.button("Stop Recording"):
        stop_recording()

# Display transcription
st.subheader("Transcription")
for text in st.session_state.transcription:
    st.write(text)