
import streamlit as st
import os
from moviepy.editor import *
from gtts import gTTS
import tempfile

try:
    import openai
    from PIL import Image
except:
    st.warning("Whisper and AI image generation modules not installed.")

st.set_page_config(page_title="AI Video Generator", layout="wide")

def clean_temp():
    folder = "temp"
    if os.path.exists(folder):
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))

def generate_tts(text, lang='en'):
    tts = gTTS(text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def transcribe_audio_whisper(audio_path):
    import openai
    openai.api_key = "sk-..."  # Optional: Replace with your key
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def generate_image(prompt):
    try:
        import openai
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        return response['data'][0]['url']
    except:
        return "https://via.placeholder.com/1024x576.png?text=AI+Image"

def make_video_with_image_and_audio(image_url, audio_path):
    clip = ImageClip(image_url).set_duration(10)
    audio = AudioFileClip(audio_path)
    clip = clip.set_audio(audio)
    clip.write_videofile("final_video.mp4", fps=24)

st.title("🎬 Final AI Video Generator")

choice = st.radio("Choose input mode", ["Text Prompt", "Voice Upload"])

if choice == "Text Prompt":
    text = st.text_area("Enter your video script or prompt")
    lang = st.selectbox("Language", ["en", "hi", "kn"])
    if st.button("Generate Video"):
        st.info("Generating TTS...")
        audio_path = generate_tts(text, lang=lang)
        st.success("TTS generated")
        st.info("Generating Image...")
        img_url = generate_image(text)
        st.image(img_url, width=512)
        st.info("Creating video...")
        make_video_with_image_and_audio(img_url, audio_path)
        st.success("Final video created!")
        st.video("final_video.mp4")

elif choice == "Voice Upload":
    audio_file = st.file_uploader("Upload voiceover (MP3/WAV)")
    if audio_file:
        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_file.read())
        st.audio("temp_audio.mp3")
        if st.button("Transcribe with Whisper"):
            transcript = transcribe_audio_whisper("temp_audio.mp3")
            st.text_area("Transcribed Text", value=transcript)
            img_url = generate_image(transcript)
            st.image(img_url)
            st.info("Creating video...")
            make_video_with_image_and_audio(img_url, "temp_audio.mp3")
            st.success("Final video created!")
            st.video("final_video.mp4")
