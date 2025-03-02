import streamlit as st
import json
import scrape
import speech_recognition as sr
import threading
import time

# Simulated scraping function that returns survey questions.
def get_list_of_questions(website_url):
    try:
        # In your actual implementation, you'll call:
        questions = scrape.get_list_of_questions(website_url)
        return questions
    except Exception as e:
        print(e)
        # For now, we simulate with a sample response.
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

# Safe version of the speak function to avoid the "run loop already started" error
def safe_speak(text):
    try:
        # Import voice module only when needed
        import voice
        
        # Use a flag to check if the function has been called recently
        if 'last_speak_time' not in st.session_state:
            st.session_state.last_speak_time = 0
        
        # Only allow speaking if at least 1 second has passed since last call
        current_time = time.time()
        if current_time - st.session_state.last_speak_time > 1:
            # Use a separate thread to prevent blocking the Streamlit app
            def speak_thread():
                try:
                    voice.speak(text)
                except Exception as e:
                    st.error(f"TTS Error: {str(e)}")
            
            threading.Thread(target=speak_thread).start()
            st.session_state.last_speak_time = current_time
            return True
        return False
    except Exception as e:
        st.warning(f"Could not use text-to-speech: {str(e)}")
        return False

# Speech to text function
def speech_to_text(audio_data):
    try:
        import voice
        return voice.speech_to_text(audio_data, voice.speech_recognizer)
    except Exception as e:
        st.error(f"Speech recognition error: {str(e)}")
        return ""

# Initialize session state variables
def init_session_state(questions):
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'review_mode' not in st.session_state:
        st.session_state.review_mode = False
    if 'questions' not in st.session_state:
        st.session_state.questions = questions
    if 'question_read' not in st.session_state:
        st.session_state.question_read = set()
    if 'page_loaded_time' not in st.session_state:
        st.session_state.page_loaded_time = time.time()
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = {}

# Navigation functions
def go_to_next_question():
    if st.session_state.current_question_idx < len(st.session_state.questions) - 1:
        st.session_state.current_question_idx += 1
        # Reset page load time for the new question
        st.session_state.page_loaded_time = time.time()
    else:
        st.session_state.review_mode = True

def go_to_prev_question():
    if st.session_state.current_question_idx > 0:
        st.session_state.current_question_idx -= 1
        # Reset page load time for the new question
        st.session_state.page_loaded_time = time.time()

def toggle_recording():
    st.session_state.is_recording = not st.session_state.is_recording

def submit_form():
    st.session_state.submitted = True

st.title("Survey Assistant")

# User provides the URL for the external survey.
survey_url = st.text_input("Enter the survey URL:")
# Using a default URL for demonstration
if not survey_url:
    survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSevpX3IMNw07QMPJgj7-Q6EZTBXLMR4E50RiyyXp9h65edJOA/viewform"

if survey_url:
    # Get the list of questions from the survey page.
    questions = get_list_of_questions(survey_url)
    
    # Initialize session state
    init_session_state(questions)
    
    # Let the user choose a mode.
    mode = st.radio("Select mode", ["Normal Filling", "Voice Assisted"])
    
    if mode == "Normal Filling":
        st.header("Normal Survey Filling")
        # Dynamically generate a form based on the questions.
        with st.form("normal_survey_form"):
            responses = {}
            for idx, q in enumerate(questions):
                q_text = q["question"]
                q_type = q["question type"].lower()
                # Create the appropriate input widget based on question type.
                if q_type == "short answer":
                    responses[q_text] = st.text_input(q_text, key=f"q_{idx}")
                elif q_type == "paragraph":
                    responses[q_text] = st.text_area(q_text, key=f"q_{idx}")
                elif q_type == "multiple choice":
                    responses[q_text] = st.radio(q_text, q["answer"], key=f"q_{idx}")
                elif q_type == "checkboxes":
                    responses[q_text] = st.multiselect(q_text, q["answer"], key=f"q_{idx}")
                else:
                    # Default fallback widget.
                    responses[q_text] = st.text_input(q_text, key=f"q_{idx}")
                    
            submitted = st.form_submit_button("Submit Responses")
            if submitted:
                st.write("Your responses:")
                st.json(responses)
                # Here you would add code to store the responses and autofill the external survey.
                
    elif mode == "Voice Assisted":
        st.header("Voice Assisted Survey Filling")

        # Review mode shows all answers for final review
        if st.session_state.review_mode:
            st.subheader("Review Your Responses")
            
            edited_responses = {}
            with st.form("review_form"):
                for idx, q in enumerate(st.session_state.questions):
                    q_text = q["question"]
                    q_type = q["question type"].lower()
                    
                    # Get current response value (or empty default)
                    current_value = st.session_state.responses.get(idx, "")
                    
                    st.write(f"**Question {idx+1}:** {q_text}")
                    
                    # Create editable fields based on question type
                    if q_type == "short answer":
                        edited_responses[idx] = st.text_input(f"Answer {idx+1}", value=current_value, key=f"review_{idx}")
                    elif q_type == "paragraph":
                        edited_responses[idx] = st.text_area(f"Answer {idx+1}", value=current_value, key=f"review_{idx}")
                    elif q_type == "multiple choice":
                        # Find default index
                        default_idx = q["answer"].index(current_value) if current_value in q["answer"] else 0
                        edited_responses[idx] = st.radio(f"Answer {idx+1}", q["answer"], index=default_idx, key=f"review_{idx}")
                    elif q_type == "checkboxes":
                        # Convert string representation to list if needed
                        if isinstance(current_value, str) and current_value.startswith('['):
                            try:
                                current_value = json.loads(current_value.replace("'", "\""))
                            except:
                                current_value = []
                        if not isinstance(current_value, list):
                            current_value = [current_value] if current_value else []
                        edited_responses[idx] = st.multiselect(f"Answer {idx+1}", q["answer"], default=current_value, key=f"review_{idx}")
                
                # Back button and submit button
                cols = st.columns(2)
                with cols[0]:
                    if st.form_submit_button("Back to Questions"):
                        st.session_state.review_mode = False
                        st.session_state.current_question_idx = len(st.session_state.questions) - 1
                        st.experimental_rerun()
                
                with cols[1]:
                    submitted = st.form_submit_button("Submit Final Responses")
                    if submitted:
                        # Update responses with edited values
                        for idx, response in edited_responses.items():
                            st.session_state.responses[idx] = response
                        
                        st.success("Survey submitted successfully!")
                        st.write("Your final responses:")
                        
                        # Display final responses in a more user-friendly format
                        final_responses = {}
                        for idx, response in st.session_state.responses.items():
                            question = st.session_state.questions[idx]["question"]
                            final_responses[question] = response
                        
                        st.json(final_responses)
                
        else:
            # Single question display mode
            current_idx = st.session_state.current_question_idx
            current_q = st.session_state.questions[current_idx]
            
            # Progress indicator
            progress = (current_idx + 1) / len(st.session_state.questions)
            st.progress(progress)
            st.write(f"Question {current_idx + 1} of {len(st.session_state.questions)}")
            
            # Display current question in a card-like container
            st.markdown(f"""
            <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 20px;">
                <h3>{current_q["question"]}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create the appropriate input widget based on question type
            q_type = current_q["question type"].lower()
            current_response = st.session_state.responses.get(current_idx, "")
            
            # Auto-read question after a 1-second delay
            question_key = f"q_{current_idx}"
            current_time = time.time()
            
            # Check if we need to read this question
            if (question_key not in st.session_state.question_read and 
                current_time - st.session_state.page_loaded_time > 1):
                
                # Try to speak the question
                if safe_speak(current_q["question"]):
                    st.session_state.question_read.add(question_key)
            
            # Add a manual button for re-reading the question if needed
            if st.button("🔊 Read Question Again", key=f"read_btn_{current_idx}"):
                safe_speak(current_q["question"])
            
            # Display different input methods based on question type
            if q_type in ["short answer", "paragraph"]:
                # For text input questions, we use voice-to-text
                text_input_type = st.text_area if q_type == "paragraph" else st.text_input
                
                # Get transcribed text if available or use current response
                current_text = st.session_state.transcribed_text.get(current_idx, current_response)
                
                # Create the text input field
                text_response = text_input_type("Your answer", value=current_text, key=f"answer_{current_idx}")
                
                # Update transcribed text if manually edited
                if text_response != current_text:
                    st.session_state.transcribed_text[current_idx] = text_response
                
                # Voice recording UI
                cols = st.columns([1, 1])
                with cols[0]:
                    # Voice recording button with different states
                    if st.session_state.is_recording:
                        if st.button("🛑 Stop Recording", key=f"stop_{current_idx}"):
                            toggle_recording()
                    else:
                        if st.button("🎤 Start Recording", key=f"start_{current_idx}"):
                            toggle_recording()
                
                # If recording is active, capture and transcribe voice
                if st.session_state.is_recording:
                    st.write("🔴 Recording... Speak now")
                    
                    try:
                        # Import here to avoid loading until needed
                        import speech_recognition as sr
                        recognizer = sr.Recognizer()
                        
                        # Capture audio from the microphone
                        with sr.Microphone() as source:
                            # Adjust for ambient noise
                            recognizer.adjust_for_ambient_noise(source, duration=1)
                            
                            # Display a spinner while recording
                            with st.spinner("Listening..."):
                                audio = recognizer.listen(source, timeout=5)
                                
                            # Convert speech to text
                            response_text = speech_to_text(audio)
                            
                            # Update the text in session state for the current question
                            if response_text:
                                # Get the current text
                                current_text = st.session_state.transcribed_text.get(current_idx, "")
                                
                                # Append or set the new text
                                if current_text:
                                    st.session_state.transcribed_text[current_idx] = current_text + " " + response_text
                                else:
                                    st.session_state.transcribed_text[current_idx] = response_text
                                
                                # Stop recording after successful transcription
                                st.session_state.is_recording = False
                                st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error recording: {str(e)}")
                        st.session_state.is_recording = False
                
                # Save the response when navigating
                st.session_state.responses[current_idx] = text_response
                
            elif q_type == "multiple choice":
                # For multiple choice, we just read the question and wait for selection
                options = current_q["answer"]
                selected_option = st.radio(
                    "Select one option:", 
                    options, 
                    index=options.index(current_response) if current_response in options else 0,
                    key=f"radio_{current_idx}"
                )
                
                # Save the response
                if selected_option != st.session_state.responses.get(current_idx, ""):
                    st.session_state.responses[current_idx] = selected_option
                
            elif q_type == "checkboxes":
                # For checkboxes, similar to multiple choice
                options = current_q["answer"]
                
                # Handle different formats of current_response
                if isinstance(current_response, str) and current_response.startswith('['):
                    try:
                        current_response = json.loads(current_response.replace("'", "\""))
                    except:
                        current_response = []
                
                if not isinstance(current_response, list):
                    current_response = [current_response] if current_response else []
                
                selected_options = st.multiselect(
                    "Select all that apply:", 
                    options, 
                    default=current_response,
                    key=f"multi_{current_idx}"
                )
                
                # Save the response
                if selected_options != st.session_state.responses.get(current_idx, ""):
                    st.session_state.responses[current_idx] = selected_options
            
            # Navigation buttons
            cols = st.columns(3)
            with cols[0]:
                if st.button("⬅️ Previous", disabled=current_idx == 0):
                    go_to_prev_question()
                    st.experimental_rerun()
            
            with cols[2]:
                next_btn_text = "Review All ➡️" if current_idx == len(st.session_state.questions) - 1 else "Next ➡️"
                if st.button(next_btn_text):
                    go_to_next_question()
                    st.experimental_rerun()