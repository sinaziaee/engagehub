import ast

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