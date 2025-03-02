import streamlit as st
import json
import scrape
import voice
import speech_recognition as sr
from datetime import datetime

# Simulated scraping function that returns survey questions.
def get_list_of_questions(website_url):
    try:
        questions = scrape.get_list_of_questions(website_url)
        return questions
    except Exception as e:
        st.error(f"Failed to fetch questions: {e}")
        sample_response = """
        [
            {"question": "What is your name?", "question type": "Short Answer", "answer": []},
            {"question": "Will you attend the Christmas Party?", "question type": "Multiple Choice", "answer": ["Yes, I'll be there", "Sorry, can't make it"]},
            {"question": "How many of you are attending?", "question type": "Short Answer", "answer": []},
            {"question": "Would you like to bring a dish to share? If yes, what type of dish?", "question type": "Checkboxes", "answer": ["Mains", "Salad", "Dessert", "Drinks", "Sides/Appetizers", "Other:"]},
            {"question": "Do you have any allergies or dietary restrictions?", "question type": "Short Answer", "answer": []},
            {"question": "What are your suggestions for the food we should order for the party?", "question type": "Paragraph", "answer": []}
        ]
        """
        return json.loads(sample_response)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Recording... Please speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    try:
        response_text = recognizer.recognize_google(audio)
        st.success("Recording complete!")
        return response_text
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

st.title("Survey Assistant")

# Get the survey URL (for demo purposes, we use a default value)
survey_url = st.text_input("Enter the survey URL:", value="https://docs.google.com/forms/d/e/1FAIpQLSevpX3IMNw07QMPJgj7-Q6EZTBXLMR4E50RiyyXp9h65edJOA/viewform")

if survey_url:
    questions = get_list_of_questions(survey_url)
    
    st.header("Normal Survey Filling with Voice Input")
    
    responses = {}
    for idx, q in enumerate(questions):
        q_text = q["question"]
        q_type = q["question type"].lower()
        voice_enabled_types = ["short answer", "paragraph", "date", "time"]
        
        if q_type in voice_enabled_types:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                voice_key = f"voice_q_{idx}"
                counter_key = f"update_counter_q_{idx}"
                widget_key = f"q_{idx}_{st.session_state.get(counter_key, 0)}"
                default_val = st.session_state.get(voice_key, "")
                
                if q_type == "paragraph":
                    responses[q_text] = st.text_area(q_text, value=default_val, key=widget_key)
                elif q_type == "date":
                    responses[q_text] = st.date_input(q_text, key=widget_key)
                elif q_type == "time":
                    responses[q_text] = st.time_input(q_text, key=widget_key)
                else:
                    responses[q_text] = st.text_input(q_text, value=default_val, key=widget_key)
            with col2:
                if st.button("🎤", key=f"record_{idx}"):
                    response_text = recognize_speech()
                    if response_text:
                        st.session_state[voice_key] = response_text
                        st.session_state[counter_key] = st.session_state.get(counter_key, 0) + 1
                        st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
        else:
            if q_type == "multiple choice":
                responses[q_text] = st.radio(q_text, q["answer"], key=f"q_{idx}")
            elif q_type == "checkboxes":
                responses[q_text] = st.multiselect(q_text, q["answer"], key=f"q_{idx}")
            else:
                responses[q_text] = st.text_input(q_text, key=f"q_{idx}")
    
    if st.button("Submit Responses"):
        st.success("Your responses have been captured:")
        st.json(responses)
        # Here you can add code to store or forward the responses.