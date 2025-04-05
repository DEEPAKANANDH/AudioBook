import streamlit as st
import pdfplumber
from gtts import gTTS
import os
from tempfile import NamedTemporaryFile
from googletrans import Translator

# Supported language map
LANGUAGES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Tamil": "ta",
    "Hindi": "hi"
}

# Extract text from specific pages
def extract_text_from_pdf(uploaded_file, start_page, end_page):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)
        start = max(0, start_page - 1)
        end = min(end_page, total_pages)
        for page in pdf.pages[start:end]:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Translate text if needed
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return text  # fallback to original

# Convert text to audio
def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    temp_file = NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# Streamlit UI
st.set_page_config(page_title="PDF to Audiobook", layout="centered")
st.title("📘 PDF to Audiobook")
st.markdown("Convert your PDF into an audiobook with multi-language support!")

uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)
        st.success(f"Uploaded PDF with {total_pages} pages.")

        start_page = st.number_input("Start Page", min_value=1, max_value=total_pages, value=1)
        end_page = st.number_input("End Page", min_value=start_page, max_value=total_pages, value=total_pages)

        language = st.selectbox("🌐 Select Language", list(LANGUAGES.keys()))
        lang_code = LANGUAGES[language]

        if st.button("🎧 Generate Audiobook"):
            with st.spinner("Processing..."):
                text = extract_text_from_pdf(uploaded_file, start_page, end_page)
                if not text.strip():
                    st.error("No text found in selected pages.")
                else:
                    translated_text = translate_text(text, lang_code)
                    audio_path = text_to_speech(translated_text, lang_code)
                    st.audio(audio_path)
                    with open(audio_path, "rb") as f:
                        st.download_button("⬇️ Download MP3", f, file_name="audiobook.mp3", mime="audio/mpeg")
                    os.remove(audio_path)
