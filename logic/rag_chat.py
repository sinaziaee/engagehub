import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from typing import List, Dict, Any
import tempfile
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Configure page
# st.set_page_config(page_title="CSV Chat Assistant", layout="wide")

# Get the absolute path of the current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir == '':  # In some environments, __file__ might not work as expected
    current_dir = os.getcwd()

# File paths configuration with absolute paths
CSV_FILE_1_PATH = os.path.join(current_dir, "form_responses.csv")
CSV_FILE_2_PATH = os.path.join(current_dir, "park_reviews.csv")
CSV_FILE_1_NAME = "dataset1"  # Name to identify the first dataset
CSV_FILE_2_NAME = "dataset2"  # Name to identify the second dataset

# Set up session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up session state for conversation memory
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "answer any question without showing code and in a concise manner"}
    ]

# Function to check file paths
def check_file_path(filepath):
    """Debug helper to check if a file exists and return detailed info"""
    exists = os.path.exists(filepath)
    parent_dir = os.path.dirname(filepath)
    parent_exists = os.path.exists(parent_dir)
    
    result = {
        "filepath": filepath,
        "exists": exists,
        "parent_dir": parent_dir,
        "parent_exists": parent_exists
    }
    
    if parent_exists:
        result["parent_contents"] = os.listdir(parent_dir)
    
    return result

# Set up session state for the dataframes
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}
    # Try to load dataframes on startup
    try:
        if os.path.exists(CSV_FILE_1_PATH):
            st.session_state.dataframes[CSV_FILE_1_NAME] = pd.read_csv(CSV_FILE_1_PATH)
            print("File found")
        else:
            print("File not found")
        if os.path.exists(CSV_FILE_2_PATH):
            st.session_state.dataframes[CSV_FILE_2_NAME] = pd.read_csv(CSV_FILE_2_PATH)
            print("File found")
        else:
            print("File not found")
    except Exception as e:
        print(f"Error loading CSV files: {str(e)}")

def get_dataframe_info(df: pd.DataFrame, df_name: str) -> str:
    """Generate information about the dataframe structure"""
    info = f"DataFrame '{df_name}' information:\n"
    info += f"- Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
    info += f"- Columns: {', '.join(df.columns.tolist())}\n"
    
    # Sample data (first 5 rows)
    info += f"\nSample data (first 5 rows):\n"
    info += df.head(5).to_string()
    
    # Data types
    info += f"\n\nData types:\n"
    for col in df.columns:
        info += f"- {col}: {df[col].dtype}\n"
    
    return info

def format_conversation_history(conversation_history: List[Dict[str, str]]) -> str:
    """Format conversation history for inclusion in the prompt"""
    if not conversation_history:
        return ""
    
    formatted_history = "Previous conversation:\n"
    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        formatted_history += f"{role.capitalize()}: {content}\n"
    
    return formatted_history + "\n"

def generate_gemini_response(prompt: str, dataframes: Dict[str, pd.DataFrame], conversation_history: List[Dict[str, str]]) -> str:
    """Generate response using Gemini model with conversation history"""
    # Prepare context about available dataframes
    context = "You are a helpful assistant that answers questions about CSV data. You have access to the following dataframes:\n\n"
    
    for name, df in dataframes.items():
        context += get_dataframe_info(df, name) + "\n\n"
    
    context += "Important instructions:\n"
    context += "1. Provide specific, data-driven answers based on the available information.\n"
    context += "2. If asked to perform analysis or visualizations, explain how you would approach it with Python code.\n"
    context += "3. IMPORTANT: Maintain conversation context. Reference and build upon previous questions and answers as appropriate.\n"
    context += "4. If a question refers to 'it', 'that', or other pronouns, interpret them in context of the conversation history.\n\n"
    
    # Include conversation history in the context
    conversation_context = format_conversation_history(conversation_history)
    
    # Combine context, conversation history, and user prompt
    full_prompt = context + conversation_context + "Current user question: " + prompt
    
    try:
        response = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21').generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def execute_query(query: str, dataframes: Dict[str, pd.DataFrame], conversation_history: List[Dict[str, str]]) -> str:
    """Execute a query against the dataframes with conversation context"""
    try:
        # Use the Gemini model with conversation history
        response = generate_gemini_response(query, dataframes, conversation_history)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # st.title("CSV Chat Assistant with Gemini")
    st.title("Ask from public Data")
    
    if not st.session_state.dataframes:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir == '':  # In some environments, __file__ might not work as expected
            current_dir = os.getcwd()

        # File paths configuration with absolute paths
        CSV_FILE_1_PATH = os.path.join(current_dir, "form_responses.csv")
        CSV_FILE_2_PATH = os.path.join(current_dir, "park_reviews.csv")
        CSV_FILE_1_NAME = "dataset1"  # Name to identify the first dataset
        CSV_FILE_2_NAME = "dataset2"  # Name to identify the second dataset
        st.session_state.dataframes[CSV_FILE_1_NAME] = pd.read_csv(CSV_FILE_1_PATH)
        st.session_state.dataframes[CSV_FILE_2_NAME] = pd.read_csv(CSV_FILE_2_PATH)
        print("No datasets loaded. Check file paths at the top of the code.")
    else:
        pass

    api_key = API_KEY
    if api_key:
        try:
            genai.configure(api_key=api_key)
            print("API key configured successfully!")
        except Exception as e:
            print(f"Error configuring API key: {str(e)}")
        
    
    if not api_key:
        st.warning("Please enter your Google API key in the sidebar to continue.")
        return
    
    if not st.session_state.dataframes:
        st.warning("No CSV files were loaded. Please check the file paths specified in the code.")
        return
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask something about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = execute_query(prompt, st.session_state.dataframes, st.session_state.conversation_history)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.conversation_history.append({"role": "assistant", "content": response})

        # Limit conversation history length to prevent token limits
        if len(st.session_state.conversation_history) > 11:  # Keep initial prompt + last 5 exchanges (10 messages)
            # Keep the system message (first message) and the last 10 messages
            st.session_state.conversation_history = [st.session_state.conversation_history[0]] + st.session_state.conversation_history[-10:]

if __name__ == "__main__":
    main()