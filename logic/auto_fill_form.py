import os
import time
import random
import pandas as pd
import requests
import google.generativeai as genai
import my_gemini

# Set up Gemini API
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

# Form submission URL (replace with your form's action URL)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdTYUTWzI9BgNWJaTE3ddoruDJx3bCkZCfOMAU6zxOBDtvb2g/formResponse"

def generate_answer(question):
    # For open text questions, use the generative model
    context = """
    I am filling park canada survey form. Please answer the following questions. Use simple answers with only one raw text format.
    """
    response = my_gemini.ask(context, question)
    return response

def choose_option(options):
    # Randomly select one of the provided options
    return random.choice(options)

def choose_rating():
    # Return a random rating from 1 to 5 as a string
    return str(random.randint(1, 5))

def submit_form():
    # Define valid options for fields based on the form HTML
    age_group_options = ["Under 18", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"]
    gender_options = ["Male", "Female", "Non-binary/Other", "Prefer not to say"]
    visit_frequency_options = ["Daily", "Weekly", "Monthly", "A few times a year", "Rarely/Never"]
    parks_visited_options = ["Nose Hill Park", "Fish Creek Provincial Park", "Confederation Park", "Other"]
    purpose_options = [
        "Exercise/Walking/Running",
        "Picnicking/Relaxing",
        "Social gatherings/Events",
        "Dog walking",
        "Sports and recreational activities",
        "Enjoying nature/Scenery",
        "Other"
    ]
    travel_method_options = ["Walking", "Cycling", "Driving", "Public transit", "Other"]
    amenities_used_options = [
        "Walking/Running trails",
        "Playgrounds",
        "Sports fields/courts",
        "Picnic areas",
        "Restrooms",
        "Water fountains",
        "Dog parks",
        "Community event spaces",
        "Other"
    ]
    
    # Answer each question appropriately:
    age_group = choose_option(age_group_options)
    gender = choose_option(gender_options)
    neighborhood = generate_answer("What is your neighborhood or area? Say something randomly in Calgary")
    visit_frequency = choose_option(visit_frequency_options)
    parks_visited = choose_option(parks_visited_options)
    purpose = choose_option(purpose_options)
    
    time.sleep(5)  # Optional delay between calls
    travel_method = choose_option(travel_method_options)
    cleanliness_rating = choose_rating()
    safety_rating = choose_rating()
    accessibility = generate_answer("How accessible are the park facilities and amenities to you?")
    amenities_used = choose_option(amenities_used_options)
    improvements = generate_answer("What improvements or new amenities would you like to see in Calgary parks?")
    time.sleep(5)
    
    # For events, the form expects a yes/no answer and (if yes) additional experience text.
    events_participated = "Yes"  # Preselecting 'Yes' for participation
    event_experience = generate_answer("Please describe your experience participating in organized events or programs at the parks.")
    
    concerns = generate_answer("Do you have any concerns or challenges when using the parks?")
    comments = generate_answer("Any additional comments or suggestions?")
    
    form_data = {
        "age_group": age_group,
        "gender": gender,
        "neighborhood": neighborhood,
        "visit_frequency": visit_frequency,
        "parks_visited": parks_visited,
        "purpose": purpose,
        "travel_method": travel_method,
        "cleanliness_rating": cleanliness_rating,
        "safety_rating": safety_rating,
        "accessibility": accessibility,
        "amenities_used": amenities_used,
        "improvements": improvements,
        "events_participated": events_participated,
        "event_experience": event_experience,
        "concerns": concerns,
        "comments": comments,
    }
    
    return form_data

def submit_form_multiple_times(n):
    file_path = "form_responses.csv"
    # Check if file exists to determine whether to write headers
    file_exists = os.path.exists(file_path)
    
    for i in range(n):
        print(f"Submitting form {i+1}...")
        time.sleep(10)  # Delay between submissions
        form_data = submit_form()
        print(form_data)
        
        # Convert the form data to a DataFrame and append it to the CSV file.
        new_row_df = pd.DataFrame([form_data])
        new_row_df.to_csv(file_path, mode='a', header=not file_exists, index=False)
        # After the first write, the file will exist so subsequent writes won't include the header.
        file_exists = True

# Example usage: Submit the form 500 times
submit_form_multiple_times(500)
