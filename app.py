import streamlit as st
import os
from gtts import gTTS
import tempfile

try:
    import openai
except:
    st.warning("OpenAI module not installed.")

st.set_page_config(page_title="AI Video Generator", layout="wide")

def generate_tts(text, lang='en'):
    tts = gTTS(text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def transcribe_audio_whisper(audio_path):
    import openai
    openai.api_key = st.secrets["openai_api_key"]  # Use secrets in Streamlit Cloud
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def generate_image(prompt):
    try:
        import openai
        openai.api_key = st.secrets["openai_api_key"]
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        return response['data'][0]['url']
    except:
        return "https://via.placeholder.com/1024x576.png?text=AI+Image"

st.title("🎬 AI Image + Audio Generator (Streamlit Compatible)")

choice = st.radio("Choose input mode", ["Text Prompt", "Voice Upload"])

if choice == "Text Prompt":
    text = st.text_area("Enter your script or prompt")
    lang = st.selectbox("Language", ["en", "hi", "kn"])
    if st.button("Generate Audio & Image"):
        with st.spinner("Generating TTS..."):
            audio_path = generate_tts(text, lang=lang)
            st.audio(audio_path)

        with st.spinner("Generating Image..."):
            img_url = generate_image(text)
            st.image(img_url, caption="AI Generated Image", width=512)

        st.download_button("Download Audio", open(audio_path, "rb"), file_name="voice.mp3")

elif choice == "Voice Upload":
    audio_file = st.file_uploader("Upload voiceover (MP3/WAV)")
    if audio_file:
        with open("uploaded_audio.mp3", "wb") as f:
            f.write(audio_file.read())
        st.audio("uploaded_audio.mp3")

        if st.button("Transcribe with Whisper"):
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio_whisper("uploaded_audio.mp3")
                st.text_area("Transcribed Text", value=transcript)
                img_url = generate_image(transcript)
                st.image(img_url, caption="AI Generated Image", width=512)
                
