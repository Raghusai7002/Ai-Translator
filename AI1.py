import streamlit as st
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import os
import PyPDF2  # For PDF file handling
from io import StringIO  # For text file handling

# Initialize translator
translator = Translator()

# Language mapping (full names to language codes)
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Hindi": "hi",
    "Arabic": "ar",
    # Indian Languages
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Odia": "or",
    "Urdu": "ur",
    "Sanskrit": "sa",
}

# Function to convert text to speech
def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save("translated_audio.mp3")
    audio_file = open("translated_audio.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")
    os.remove("translated_audio.mp3")  # Clean up the file

# Function to capture voice input
def capture_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Speak now...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Sorry, there was an issue with the speech recognition service.")
    return None

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from a text file
def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# Streamlit app
st.title("TransLingua - Text, Voice, and Document Translation Tool")
st.write("""
Translate text, voice input, or entire documents into multiple languages seamlessly. 
Upload a document, input text, or speak, select the target language, and get the translation with audio output.
""")

# Input method selection
input_option = st.radio("Choose input method:", ("Text", "Voice", "Document"))

input_text = ""
if input_option == "Text":
    input_text = st.text_area("Enter text to translate:", height=200)
elif input_option == "Voice":
    if st.button("Start Voice Input"):
        input_text = capture_voice_input()
        if input_text:
            st.write(f"**You said:** {input_text}")
else:  # Document input
    uploaded_file = st.file_uploader("Upload a document (PDF or TXT):", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            input_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            input_text = extract_text_from_txt(uploaded_file)
        st.write("**Extracted Text:**")
        st.info(input_text)

# Target language selection
target_lang = st.selectbox("Select target language:", list(LANGUAGES.keys()))

# Translate button
if st.button("Translate"):
    if input_text:
        try:
            # Detect source language
            detected_lang = translator.detect(input_text).lang
            source_lang_name = [k for k, v in LANGUAGES.items() if v == detected_lang][0]

            # Perform translation
            translation = translator.translate(
                input_text, 
                src=detected_lang,  # Automatically detect source language
                dest=LANGUAGES[target_lang]  # Use language code for target
            )

            # Display results
            st.subheader("Translation Results:")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Detected Source Language:** {source_lang_name}")
                st.info(input_text)
            with col2:
                st.write(f"**Translated Text ({target_lang}):**")
                st.success(translation.text)

            # Convert translated text to speech
            st.write("---")
            st.write("**Listen to the translation:**")
            text_to_speech(translation.text, LANGUAGES[target_lang])
        except Exception as e:
            st.error(f"An error occurred during translation: {e}")
    else:
        st.warning("Please provide input text, use voice input, or upload a document.")

# Footer
st.write("---")
st.write("© 2023 TransLingua. Powered by Streamlit, Google Translate API, and gTTS.")