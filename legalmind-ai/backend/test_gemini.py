"""Test Gemini API connectivity"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Gemini API...")
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

try:
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content('Say "API Working"')
    print(f"✓ API Key is VALID")
    print(f"✓ Response: {response.text[:100]}")
except Exception as e:
    error_msg = str(e)
    if '403' in error_msg or 'API key not valid' in error_msg:
        print("✗ API Key INVALID or REVOKED")
    elif '404' in error_msg:
        print("✗ Model not found")
    else:
        print(f"✗ Error: {error_msg[:200]}")
