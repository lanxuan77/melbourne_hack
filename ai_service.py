import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)



def generate_adapted_lesson(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    
    return response.text