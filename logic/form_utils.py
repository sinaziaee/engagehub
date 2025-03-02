import os
import csv
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def save_responses_to_csv(survey_url, responses, questions):
    """
    Save user responses to a CSV file named after the form.
    
    Args:
        survey_url (str): URL of the Google Form
        responses (dict): Dictionary of responses with question index as key
        questions (list): List of question dictionaries
    
    Returns:
        str: Path to the saved CSV file
    """
    # Extract a sanitized form name from the URL
    form_name = survey_url.split('/')[-2] if '/' in survey_url else "survey"
    csv_filename = f"{form_name}.csv"
    
    # Prepare data for CSV
    row_data = {}
    
    # Add all questions and responses
    for idx, question in enumerate(questions):
        q_text = question["question"]
        response = responses.get(idx, "")
        
        # Handle different response types
        if isinstance(response, list):
            # Join multiple selections with a semicolon
            response = "; ".join(str(item) for item in response)
        
        row_data[q_text] = response
    
    # Check if the CSV file exists already
    file_exists = os.path.isfile(csv_filename)
    
    # Create or append to the CSV file
    mode = 'a' if file_exists else 'w'
    with open(csv_filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row_data.keys())
        
        # Write header if creating new file
        if not file_exists:
            writer.writeheader()
        
        # Write the response row
        writer.writerow(row_data)
    
    return csv_filename

def submit_google_form(survey_url, responses, questions):
    """
    Automatically fill and submit a Google Form using Selenium.
    
    Args:
        survey_url (str): URL of the Google Form
        responses (dict): Dictionary of responses with question index as key
        questions (list): List of question dictionaries
    
    Returns:
        bool: True if submission was successful, False otherwise
    """
    try:
        # Setup Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set up webdriver with Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Open the Google Form
        driver.get(survey_url)
        
        # Wait for the form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )
        
        # Process each question and fill in the response
        for idx, question in enumerate(questions):
            q_type = question["question type"].lower()
            response = responses.get(idx, "")
            
            # Skip if no response
            if not response:
                continue
            
            try:
                # Different element handling based on question type
                if q_type in ["short answer", "paragraph"]:
                    # Find the text input element
                    input_element = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")[idx]
                    input_element.clear()
                    input_element.send_keys(response)
                    
                elif q_type == "multiple choice":
                    # Find and click the appropriate radio button
                    # Google Forms uses divs with role="radio" for radio options
                    options = driver.find_elements(By.CSS_SELECTOR, f"div[role='radiogroup'] div[role='radio']")
                    for option in options:
                        option_text = option.find_element(By.CSS_SELECTOR, "span").text.strip()
                        if option_text == response:
                            option.click()
                            break
                            
                elif q_type == "checkboxes":
                    # Handle multiple selections
                    if isinstance(response, str) and ";" in response:
                        responses_list = [r.strip() for r in response.split(";")]
                    elif isinstance(response, list):
                        responses_list = response
                    else:
                        responses_list = [response]
                    
                    # Find and click all appropriate checkboxes
                    checkboxes = driver.find_elements(By.CSS_SELECTOR, f"div[role='group'] div[role='checkbox']")
                    for checkbox in checkboxes:
                        checkbox_text = checkbox.find_element(By.CSS_SELECTOR, "span").text.strip()
                        if checkbox_text in responses_list:
                            checkbox.click()
            
            except (NoSuchElementException, IndexError) as e:
                print(f"Error filling question {idx}: {str(e)}")
                continue
        
        # Find and click the submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "div[role='button'][jsaction*='submit']")
        submit_button.click()
        
        # Wait for submission confirmation page
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains("formResponse")
            )
            success = True
        except TimeoutException:
            success = False
        
        # Close the browser
        driver.quit()
        
        return success
        
    except Exception as e:
        print(f"Error submitting form: {str(e)}")
        return False

def get_form_name(survey_url):
    """
    Extract a human-readable form name from the Google Form URL.
    
    Args:
        survey_url (str): URL of the Google Form
        
    Returns:
        str: A human-readable name for the form
    """
    try:
        # Use Selenium to fetch the form title
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(survey_url)
        
        # Wait for the form to load and get its title
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='heading']"))
        )
        
        title_element = driver.find_element(By.CSS_SELECTOR, "div[role='heading']")
        form_title = title_element.text.strip()
        
        driver.quit()
        
        # Clean the title for use as a filename
        form_title = ''.join(c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in form_title)
        form_title = form_title.replace(' ', '_')
        
        return form_title
    
    except Exception as e:
        print(f"Error getting form title: {str(e)}")
        # Fallback to URL-based name
        form_id = survey_url.split('/')[-2] if '/' in survey_url else "survey"
        return f"form_{form_id}"

def load_existing_responses(csv_filepath):
    """
    Load existing responses from a CSV file.
    
    Args:
        csv_filepath (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing previous responses
    """
    if os.path.exists(csv_filepath):
        try:
            return pd.read_csv(csv_filepath)
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def responses_dict_to_row(responses, questions):
    """
    Convert the responses dictionary to a format suitable for CSV rows.
    
    Args:
        responses (dict): Dictionary of responses with question index as key
        questions (list): List of question dictionaries
        
    Returns:
        dict: A dictionary mapping question text to response
    """
    row_data = {}
    
    for idx, question in enumerate(questions):
        q_text = question["question"]
        response = responses.get(idx, "")
        
        # Handle different response types
        if isinstance(response, list):
            response = "; ".join(str(item) for item in response)
        
        row_data[q_text] = response
    
    return row_data