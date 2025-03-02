import streamlit as st
import json
# import scrape # Assuming scrape is not implemented for now
# import voice # Assuming voice is not implemented for now
import speech_recognition as sr # Keeping the import, might use later

# Simulated scraping function that returns survey questions.
def get_list_of_questions(website_url):
    try:
        # In your actual implementation, you'll call:
        # questions = scrape.get_list_of_questions(website_url)
        # return questions
        pass # Remove the actual scrape call for simulation
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


st.title("Survey Assistant")

# User provides the URL for the external survey.
survey_url = st.text_input("Enter the survey URL:")
survey_url = "https://docs.google.com/forms/d/e/1FAIpQLSevpX3IMNw07QMPJgj7-Q6EZTBXLMR4E50RiyyXp9h65edJOA/viewform"

if survey_url:
    # Get the list of questions from the survey page.
    questions = get_list_of_questions(survey_url)

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
        st.write("This mode will simulate Gemini for voice-based survey completion.")

        if 'current_question_index_voice' not in st.session_state:
            st.session_state['current_question_index_voice'] = 0
        if 'voice_responses' not in st.session_state:
            st.session_state['voice_responses'] = {}
        if 'voice_mode_form_visible' not in st.session_state:
            st.session_state['voice_mode_form_visible'] = False

        current_question_index = st.session_state['current_question_index_voice']

        if not st.session_state['voice_mode_form_visible']: # Voice question mode
            if 0 <= current_question_index < len(questions):
                current_question_data = questions[current_question_index]
                q_text = current_question_data["question"]
                q_type = current_question_data["question type"].lower()
                q_answers_choices = current_question_data.get("answer", [])

                st.subheader(f"Question {current_question_index + 1}/{len(questions)}")
                st.write(f"**{q_text}**")

                if q_type == "multiple choice":
                    if q_text not in st.session_state['voice_responses']:
                        st.session_state['voice_responses'][q_text] = None  # Initialize if not answered yet
                    voice_answer_key = f"voice_answer_{current_question_index}"
                    st.session_state['voice_responses'][q_text] = st.radio("Select an option:", q_answers_choices, key=voice_answer_key, index = q_answers_choices.index(st.session_state['voice_responses'][q_text]) if st.session_state['voice_responses'][q_text] in q_answers_choices else 0 if q_answers_choices else None ) if st.session_state['voice_responses'][q_text] else st.radio("Select an option:", q_answers_choices, key=voice_answer_key)

                elif q_type == "checkboxes":
                    if q_text not in st.session_state['voice_responses']:
                        st.session_state['voice_responses'][q_text] = [] # Initialize if not answered yet
                    voice_answer_key = f"voice_answer_{current_question_index}"
                    st.session_state['voice_responses'][q_text] = st.multiselect("Select options:", q_answers_choices, key=voice_answer_key, default=st.session_state['voice_responses'][q_text])

                else: # short answer, paragraph, or default
                    if q_text not in st.session_state['voice_responses']:
                        st.session_state['voice_responses'][q_text] = "" # Initialize if not answered yet
                    voice_answer_key = f"voice_answer_{current_question_index}"
                    st.session_state['voice_responses'][q_text] = st.text_area("Your answer:", key=voice_answer_key, value=st.session_state['voice_responses'][q_text])


                col1, col2, col3 = st.columns([1, 1, 1]) # creates three columns

                if col1.button("Previous Question", disabled=current_question_index == 0):
                    st.session_state['current_question_index_voice'] -= 1
                    st.rerun() # Rerun to update UI immediately


                if col2.button("Next Question", disabled=current_question_index == len(questions) - 1):
                    st.session_state['current_question_index_voice'] += 1
                    st.rerun() # Rerun to update UI immediately

                if col3.button("Finish Voice Input"):
                    st.session_state['voice_mode_form_visible'] = True # Show the form
                    st.rerun() # Rerun to update UI immediately


            elif current_question_index >= len(questions): # After last question, but before form show (just in case of direct index manipulation)
                st.write("You have answered all the questions in voice mode. Click 'Finish Voice Input' to review and submit.")
                if st.button("Finish Voice Input (Again)"): # Redundant button for safety
                    st.session_state['voice_mode_form_visible'] = True
                    st.rerun()

        if st.session_state['voice_mode_form_visible']: # Show Form after voice input
            st.header("Review and Edit Your Voice Responses")
            with st.form("voice_survey_form_review"):
                review_responses = {}
                for idx, q in enumerate(questions):
                    q_text = q["question"]
                    q_type = q["question type"].lower()

                    if q_type == "short answer":
                        review_responses[q_text] = st.text_input(q_text, value=st.session_state['voice_responses'].get(q_text, ""), key=f"review_q_{idx}")
                    elif q_type == "paragraph":
                        review_responses[q_text] = st.text_area(q_text, value=st.session_state['voice_responses'].get(q_text, ""), key=f"review_q_{idx}")
                    elif q_type == "multiple choice":
                        review_responses[q_text] = st.radio(q_text, q["answer"], key=f"review_q_{idx}") # value argument removed
                    elif q_type == "checkboxes":
                        review_responses[q_text] = st.multiselect(q_text, q["answer"], default=st.session_state['voice_responses'].get(q_text, []), key=f"review_q_{idx}")
                    else:
                        review_responses[q_text] = st.text_input(q_text, value=st.session_state['voice_responses'].get(q_text, ""), key=f"review_q_{idx}")

                submitted_voice = st.form_submit_button("Submit Voice Responses")
                if submitted_voice:
                    st.write("Your voice assisted responses:")
                    st.json(review_responses)
                    # Here you would add code to store and autofill the external survey with voice responses.