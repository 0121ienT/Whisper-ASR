import streamlit as st
from transformers import pipeline
import tempfile
import os
import time

st.title("🗣️ Voice to Text (PhoWhisper - Tiếng Việt)")

@st.cache_resource
def load_model():
    return pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")

transcriber = load_model()

# Tải file âm thanh
uploaded_file = st.file_uploader("📂 Tải lên file WAV", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')

    # Ghi file tạm để xử lý
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.write("🧠 Đang nhận dạng giọng nói...")

    try:
        result = transcriber(tmp_path)
        st.success("✅ Nhận dạng hoàn tất!")
        placeholder = st.empty()
        display_text = ""
        for char in result["text"]:
            display_text += char
            placeholder.text_area("📜 Văn bản nhận được:", display_text, height=200)
            time.sleep(0.03)
    except Exception as e:
        st.error(f"❌ Lỗi xử lý: {e}")
    finally:
        os.remove(tmp_path)
