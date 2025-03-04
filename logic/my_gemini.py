import os
# secrets
from dotenv import load_dotenv
# gemini
from google import genai
from google.genai import types

def ask(context, question, gemini_api_key=None):
    load_dotenv()
    if gemini_api_key is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(
        api_key=gemini_api_key,
    )
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
                    in this context: {context}, {question}
                    """
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    buffer_data = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # print(chunk.text, end="")
        buffer_data += chunk.text
    return buffer_data
