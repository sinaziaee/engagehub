import os
# secrets
from dotenv import load_dotenv
# scraper
from firecrawl import FirecrawlApp
# gemini
import base64
from google import genai
from google.genai import types

def scrape_data(website_url, api_key):
    app = FirecrawlApp(api_key=api_key)
    scrape_result = app.scrape_url(website_url, params={'formats': ['markdown', 'html']})
    return scrape_result

def extract_data(scraped_result, api_key):
    client = genai.Client(
        api_key=api_key,
    )
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""This is the scraped data of a website <{scraped_result}>, 
                    try to understand it and generate a summary.
                    Write it in raw text format."""
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

def main():
    load_dotenv()
    api_key=os.getenv("SCRAPE_API_KEY")
    website_url = "https://www.canada.ca/en/environment-climate-change/corporate/transparency/consultations/export-control-list-amendments.html"
    scrape_result = scrape_data(website_url, api_key)
    # Extract data from the scraped result:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    extracted_data = extract_data(scrape_result, gemini_api_key)
    print(extracted_data)

main()
