import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv('d:/PaperAmbulance/backend/.env')

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    print("Available Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
