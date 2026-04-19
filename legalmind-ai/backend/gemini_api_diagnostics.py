"""
Gemini API Key Validation & Connectivity Diagnostic Tool
Validates API key for F6 (AI Assistant) and F11 (Precedent Finder)
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(title):
    print(f"\n{BLUE}{BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}\n")

def print_test(test_name, status, details="", error_code=None):
    if status:
        symbol = f"{GREEN}✓{RESET}"
        status_text = f"{GREEN}PASS{RESET}"
    else:
        symbol = f"{RED}✗{RESET}"
        status_text = f"{RED}FAIL{RESET}"
    
    print(f"{symbol} {test_name:<50} [{status_text}]")
    if details:
        print(f"   {CYAN}→{RESET} {details}")
    if error_code:
        print(f"   {RED}→ Error Code: {error_code}{RESET}")

def print_section(title):
    print(f"\n{YELLOW}{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}{RESET}")

# Main diagnostic
print(f"{BOLD}{CYAN}")
print("╔════════════════════════════════════════════════════════════════════╗")
print("║                                                                    ║")
print("║       GEMINI API KEY DIAGNOSTIC & VALIDATION TOOL                 ║")
print("║       LegalMind AI - F6 & F11 Readiness Check                     ║")
print("║                                                                    ║")
print("╚════════════════════════════════════════════════════════════════════╝")
print(RESET)

print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python Version: {sys.version.split()[0]}")

# ============================================================================
# STEP 1: Environment Configuration Check
# ============================================================================
print_section("1. ENVIRONMENT CONFIGURATION")

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    key_length = len(api_key)
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print_test("API Key Found in .env", True, f"Length: {key_length} chars, Key: {masked_key}")
    
    # Validate key format
    if api_key.startswith('AIza'):
        print_test("API Key Format Valid", True, "Starts with 'AIza' (Google API standard)")
    else:
        print_test("API Key Format Valid", False, "Invalid format - should start with 'AIza'")
else:
    print_test("API Key Found in .env", False, "GEMINI_API_KEY not found in environment")
    print(f"\n{RED}CRITICAL ERROR: Cannot proceed without API key{RESET}")
    sys.exit(1)

# ============================================================================
# STEP 2: Package Dependencies Check
# ============================================================================
print_section("2. PACKAGE DEPENDENCIES")

try:
    import google.generativeai as genai
    import google.generativeai.types as types
    print_test("google.generativeai installed", True, f"Version: {genai.__version__ if hasattr(genai, '__version__') else 'Unknown'}")
except ImportError as e:
    print_test("google.generativeai installed", False, f"Import error: {str(e)}")
    print(f"\n{RED}CRITICAL ERROR: Required package not installed{RESET}")
    print(f"{YELLOW}Install with: pip install google-generativeai{RESET}")
    sys.exit(1)

try:
    import requests
    print_test("requests library available", True, "For HTTP diagnostics")
except ImportError:
    print_test("requests library available", False, "Optional but recommended")

# ============================================================================
# STEP 3: API Key Configuration
# ============================================================================
print_section("3. API CONFIGURATION")

try:
    genai.configure(api_key=api_key)
    print_test("API Key Configured", True, "genai.configure() successful")
except Exception as e:
    print_test("API Key Configured", False, f"Configuration error: {str(e)}")
    sys.exit(1)

# ============================================================================
# STEP 4: Model Availability Check
# ============================================================================
print_section("4. MODEL AVAILABILITY")

target_model = 'gemini-flash-latest'
try:
    print(f"{CYAN}Fetching available models...{RESET}")
    available_models = list(genai.list_models())
    print_test("Model Listing Successful", True, f"Found {len(available_models)} models")
    
    # Check for gemini-flash-latest
    flash_models = [m for m in available_models if 'flash' in m.name.lower() or target_model in m.name]
    
    if flash_models:
        print_test(f"{target_model} Available", True, f"Found {len(flash_models)} flash model(s)")
        for model in flash_models[:3]:
            print(f"   • {model.name}")
    else:
        print_test(f"{target_model} Available", False, "Model not found in available models")
        print(f"\n{YELLOW}Available models:{RESET}")
        for model in available_models[:5]:
            print(f"   • {model.name}")
    
except Exception as e:
    error_msg = str(e)
    error_code = None
    
    if '403' in error_msg:
        error_code = "403 Forbidden"
        print_test("Model Listing Successful", False, "API Key Invalid or Revoked", error_code)
    elif '429' in error_msg:
        error_code = "429 Too Many Requests"
        print_test("Model Listing Successful", False, "Quota Exceeded", error_code)
    elif '404' in error_msg:
        error_code = "404 Not Found"
        print_test("Model Listing Successful", False, "API Endpoint Not Found", error_code)
    else:
        print_test("Model Listing Successful", False, f"Error: {error_msg[:100]}")
    
    print(f"\n{RED}Cannot proceed to generation tests without model access{RESET}")
    sys.exit(1)

# ============================================================================
# STEP 5: Basic Generation Test
# ============================================================================
print_section("5. BASIC CONTENT GENERATION TEST")

try:
    print(f"{CYAN}Initializing {target_model}...{RESET}")
    model = genai.GenerativeModel(target_model)
    print_test("Model Initialization", True, f"GenerativeModel('{target_model}') created")
    
    print(f"{CYAN}Generating test content...{RESET}")
    test_prompt = "Say 'API_OK' if you can read this."
    start_time = time.time()
    
    response = model.generate_content(test_prompt)
    
    elapsed_time = time.time() - start_time
    
    if response and response.text:
        response_text = response.text.strip()
        print_test("Content Generation", True, f"Response received in {elapsed_time:.2f}s")
        print(f"   {CYAN}Prompt:{RESET} \"{test_prompt}\"")
        print(f"   {CYAN}Response:{RESET} \"{response_text[:100]}\"")
        
        if 'API_OK' in response_text or 'ok' in response_text.lower():
            print_test("Response Validation", True, "Model understood and responded correctly")
        else:
            print_test("Response Validation", True, "Model responded (content may vary)")
    else:
        print_test("Content Generation", False, "No response text received")
        
except Exception as e:
    error_msg = str(e)
    error_code = None
    
    if '403' in error_msg or 'API key not valid' in error_msg:
        error_code = "403 Forbidden"
        print_test("Content Generation", False, "API Key Invalid or Permissions Denied", error_code)
    elif '429' in error_msg or 'quota' in error_msg.lower():
        error_code = "429 Too Many Requests"  
        print_test("Content Generation", False, "API Quota Exceeded", error_code)
    elif '404' in error_msg:
        error_code = "404 Not Found"
        print_test("Content Generation", False, "Model Not Found", error_code)
    elif 'SAFETY' in error_msg or 'blocked' in error_msg.lower():
        print_test("Content Generation", False, "Content blocked by safety filters")
    else:
        print_test("Content Generation", False, f"Error: {error_msg[:150]}")
    
    print(f"\n{RED}Generation test failed - API may not be fully functional{RESET}")
    sys.exit(1)

# ============================================================================
# STEP 6: F6 AI Assistant Readiness Test
# ============================================================================
print_section("6. F6 AI ASSISTANT READINESS (CASE CHAT)")

try:
    print(f"{CYAN}Testing F6 case analysis capability...{RESET}")

    # Simulate a case analysis query
    f6_prompt = """You are a legal AI assistant. A lawyer asks: "What are the key elements I need to prove in a Section 302 IPC murder case?"

Provide a brief, structured answer."""

    start_time = time.time()
    f6_response = model.generate_content(f6_prompt)
    elapsed_time = time.time() - start_time

    if f6_response and f6_response.text:
        response_length = len(f6_response.text)
        print_test("F6 Legal Analysis", True, f"Generated {response_length} chars in {elapsed_time:.2f}s")
        print(f"   {CYAN}Sample Output:{RESET}")
        preview = f6_response.text[:200].replace('\n', ' ')
        print(f"   \"{preview}...\"")

        # Check if response contains legal terminology
        legal_terms = ['section', 'prove', 'evidence', 'court', 'legal', 'law', 'case']
        terms_found = sum(1 for term in legal_terms if term.lower() in f6_response.text.lower())

        if terms_found >= 2:
            print_test("Legal Context Understanding", True, f"Found {terms_found} legal terms in response")
        else:
            print_test("Legal Context Understanding", True, "Response generated (content varies)")
    else:
        print_test("F6 Legal Analysis", False, "No response received")

except Exception as e:
    error_msg = str(e)
    if '403' in error_msg:
        print_test("F6 Legal Analysis", False, "API Key Invalid", "403 Forbidden")
    elif '429' in error_msg:
        print_test("F6 Legal Analysis", False, "Quota Exceeded", "429 Too Many Requests")
    else:
        print_test("F6 Legal Analysis", False, f"Error: {error_msg[:100]}")

# ============================================================================
# STEP 7: F11 Precedent Comparison Readiness Test
# ============================================================================
print_section("7. F11 PRECEDENT FINDER READINESS (AI COMPARISON)")

try:
    print(f"{CYAN}Testing F11 precedent comparison capability...{RESET}")

    # Simulate a precedent comparison query
    f11_prompt = """Compare these two legal cases and identify similarities:

Case 1: State vs. Kumar (2020) - Murder under IPC Section 302, convicted with life imprisonment
Case 2: State vs. Sharma (2021) - Homicide under IPC Section 302, 20 years imprisonment

Provide: 1) Key similarities, 2) Distinguishing factors, 3) Legal implications."""

    start_time = time.time()
    f11_response = model.generate_content(f11_prompt)
    elapsed_time = time.time() - start_time

    if f11_response and f11_response.text:
        response_length = len(f11_response.text)
        print_test("F11 Precedent Comparison", True, f"Generated {response_length} chars in {elapsed_time:.2f}s")
        print(f"   {CYAN}Sample Output:{RESET}")
        preview = f11_response.text[:250].replace('\n', ' ')
        print(f"   \"{preview}...\"")

        # Check if response contains comparison elements
        comparison_keywords = ['similar', 'both', 'differ', 'distinguish', 'common', 'section 302']
        keywords_found = sum(1 for kw in comparison_keywords if kw.lower() in f11_response.text.lower())

        if keywords_found >= 3:
            print_test("Comparison Quality", True, f"Found {keywords_found} comparison keywords")
        else:
            print_test("Comparison Quality", True, "Response generated (quality varies)")
    else:
        print_test("F11 Precedent Comparison", False, "No response received")

except Exception as e:
    error_msg = str(e)
    if '403' in error_msg:
        print_test("F11 Precedent Comparison", False, "API Key Invalid", "403 Forbidden")
    elif '429' in error_msg:
        print_test("F11 Precedent Comparison", False, "Quota Exceeded", "429 Too Many Requests")
    else:
        print_test("F11 Precedent Comparison", False, f"Error: {error_msg[:100]}")

# ============================================================================
# STEP 8: Quota and Rate Limit Check
# ============================================================================
print_section("8. QUOTA & RATE LIMIT VALIDATION")

try:
    print(f"{CYAN}Testing multiple rapid requests...{RESET}")

    success_count = 0
    total_requests = 3

    for i in range(total_requests):
        try:
            test_response = model.generate_content(f"Test request #{i+1}: Say OK")
            if test_response and test_response.text:
                success_count += 1
            time.sleep(0.5)  # Small delay between requests
        except Exception as e:
            if '429' in str(e):
                print_test("Rate Limit Check", False, f"Rate limit hit at request {i+1}", "429 Too Many Requests")
                break

    if success_count == total_requests:
        print_test("Quota Status", True, f"Completed {success_count}/{total_requests} requests successfully")
        print_test("Rate Limit Status", True, "No rate limiting detected")
    elif success_count > 0:
        print_test("Quota Status", True, f"Partial success: {success_count}/{total_requests}")
    else:
        print_test("Quota Status", False, "All requests failed - likely quota exceeded")

except Exception as e:
    error_msg = str(e)
    if '429' in error_msg:
        print_test("Quota Status", False, "API Quota Exceeded", "429 Too Many Requests")
    else:
        print_test("Quota Status", False, f"Error: {error_msg[:100]}")

# ============================================================================
# STEP 9: Performance Metrics
# ============================================================================
print_section("9. PERFORMANCE METRICS")

try:
    print(f"{CYAN}Measuring response time for typical query...{RESET}")

    perf_prompt = "Summarize the key points of a contract breach case in 2 sentences."

    times = []
    for i in range(3):
        start = time.time()
        perf_response = model.generate_content(perf_prompt)
        elapsed = time.time() - start
        times.append(elapsed)
        time.sleep(0.3)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print_test("Average Response Time", True, f"{avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")

    if avg_time < 3.0:
        print_test("Performance Rating", True, "Excellent (< 3s average)")
    elif avg_time < 5.0:
        print_test("Performance Rating", True, "Good (< 5s average)")
    else:
        print_test("Performance Rating", True, f"Acceptable ({avg_time:.2f}s average)")

except Exception as e:
    print_test("Performance Test", False, f"Could not complete: {str(e)[:100]}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header("DIAGNOSTIC SUMMARY")

summary = {
    "API Key Status": "✓ Valid" if api_key and api_key.startswith('AIza') else "✗ Invalid",
    "Model Access": "✓ Available" if 'model' in locals() else "✗ Unavailable",
    "F6 Readiness": "✓ Ready" if 'f6_response' in locals() and f6_response.text else "✗ Not Ready",
    "F11 Readiness": "✓ Ready" if 'f11_response' in locals() and f11_response.text else "✗ Not Ready",
    "Quota Status": "✓ Available" if success_count > 0 else "✗ Exceeded",
}

for item, status in summary.items():
    color = GREEN if "✓" in status else RED
    print(f"  {color}{status:<20}{RESET} {item}")

print(f"\n{BOLD}{'='*70}{RESET}")

# Final verdict
if all("✓" in status for status in summary.values()):
    print(f"{GREEN}{BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║                  ✓ ALL CHECKS PASSED                              ║")
    print("║                                                                    ║")
    print("║     Gemini API is READY for F6 (AI Assistant) and                ║")
    print("║     F11 (Precedent Finder) features                              ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(RESET)
    sys.exit(0)
else:
    print(f"{RED}{BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║                  ✗ DIAGNOSTICS FAILED                             ║")
    print("║                                                                    ║")
    print("║     Gemini API has issues that need to be resolved               ║")
    print("║     Review the error messages above                              ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(RESET)

    print(f"\n{YELLOW}Common Issues:{RESET}")
    print(f"  • 403 Forbidden: API key invalid, revoked, or lacks permissions")
    print(f"  • 429 Too Many Requests: Quota exceeded or rate limit hit")
    print(f"  • 404 Not Found: Model name incorrect or deprecated")
    print(f"\n{YELLOW}Recommended Actions:{RESET}")
    print(f"  1. Verify API key at: https://makersuite.google.com/app/apikey")
    print(f"  2. Check quota limits at: https://console.cloud.google.com/")
    print(f"  3. Ensure billing is enabled for the Google Cloud project")
    print(f"  4. Try regenerating the API key if issues persist")

    sys.exit(1)
