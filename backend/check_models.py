import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load the API key from the .env file
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
    exit()

# 2. Configure the Google SDK
genai.configure(api_key=api_key)

print("Fetching available Gemini models...\n")

try:
    # 3. Fetch and filter the models
    available_models = genai.list_models()
    
    print("--- Models Supporting Text/JSON Generation ---")
    for m in available_models:
        # We only care about models that can generate content (not just embedding models)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
            
    print("----------------------------------------------\n")
    
except Exception as e:
    print(f"Failed to fetch models: {e}")