import ast
import json
import scrape

def read_prompt_file(prompt_file_path):
    with open(prompt_file_path, 'r') as f:
        return f.read().strip()

def parse_question_string(question_str):
    # Split the string into three parts based on semicolon
    parts = [part.strip() for part in question_str.split(";")]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts in question string, got {len(parts)}: {question_str}")
    
    question_text = parts[0]
    question_type = parts[1]
    # Convert the options string (third part) into a list using ast.literal_eval
    try:
        options = ast.literal_eval(parts[2])
    except Exception as e:
        raise ValueError(f"Error parsing options list from {parts[2]}: {e}")
    
    return [question_text, question_type, options]

def convert_text_to_list(text):
    # Convert the whole string into a Python list structure
    try:
        data = ast.literal_eval(text)
    except Exception as e:
        raise ValueError(f"Error parsing input text: {e}")
    
    # Process each inner list and each question string within it
    result = []
    for inner_list in data:
        parsed_inner = [parse_question_string(q) for q in inner_list]
        result.append(parsed_inner)
    return result

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

