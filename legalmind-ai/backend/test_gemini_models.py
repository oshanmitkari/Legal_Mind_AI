"""
Test script to find the correct Gemini model name that works with v1beta API
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ No API key found!")
    exit(1)

print(f"✅ API Key loaded: {api_key[:10]}...")
genai.configure(api_key=api_key)

print("\n" + "="*70)
print("AVAILABLE MODELS WITH generateContent SUPPORT")
print("="*70)

available_models = []
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        available_models.append(m.name)
        print(f"  ✓ {m.name}")

print("\n" + "="*70)
print("TESTING EACH MODEL")
print("="*70)

# Test models to try (various naming conventions)
test_models = [
    # Exact names from list_models
    *available_models,
    # Common variations
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-pro',
    'gemini-flash',
]

# Remove duplicates
test_models = list(set(test_models))

working_models = []

for model_name in test_models:
    # Extract just the model name without 'models/' prefix
    short_name = model_name.replace('models/', '')
    
    print(f"\nTesting: {short_name}")
    try:
        model = genai.GenerativeModel(short_name)
        response = model.generate_content("Say hello in 2 words")
        print(f"  ✅ SUCCESS! Response: {response.text[:50]}")
        working_models.append(short_name)
        # Found a working model, use this one!
        break
    except Exception as e:
        error_msg = str(e)
        if 'quota' in error_msg.lower():
            print(f"  ⚠️  QUOTA EXCEEDED (but model exists!)")
            working_models.append(short_name)
            break
        elif '404' in error_msg or 'not found' in error_msg.lower():
            print(f"  ❌ 404 Not Found")
        elif 'leaked' in error_msg.lower():
            print(f"  ❌ API Key Leaked")
            exit(1)
        else:
            print(f"  ❌ Error: {error_msg[:80]}")

print("\n" + "="*70)
print("RESULTS")
print("="*70)

if working_models:
    print(f"\n✅ WORKING MODEL FOUND: {working_models[0]}")
    print(f"\nUse this in your code:")
    print(f"  model = genai.GenerativeModel('{working_models[0]}')")
else:
    print("\n❌ No working models found!")
    print("\nAvailable models from API:")
    for m in available_models:
        print(f"  - {m}")
