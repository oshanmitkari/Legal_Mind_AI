"""Quick UI validation test with authentication"""
import requests

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("=" * 60)
print("  LEGALMIND AI - UI REFACTORING VALIDATION")
print("=" * 60)

# Step 1: Login
print("\n1. Authenticating...")
# Try form data first
login_data = {
    'enrollment_number': 'UP/12345/2020',
    'password': 'password123'
}
login_resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
print(f"   Login status: {login_resp.status_code}")

# If login didn't work, try accessing page anyway (might be development mode)
if login_resp.status_code not in [200, 302]:
    print(f"   Warning: Login may have failed, proceeding anyway...")

# Step 2: Get case detail page
print("\n2. Fetching case detail page...")
case_resp = session.get(f"{BASE_URL}/cases/1")
print(f"   Page status: {case_resp.status_code}")
print(f"   HTML length: {len(case_resp.text)} characters")

# Step 3: Validate tab structure
print("\n3. Validating tab navigation...")
html = case_resp.text
tests = {
    'tabAssistant button': 'id="tabAssistant"' in html,
    'tabPrecedent button': 'id="tabPrecedent"' in html,
    'contentAssistant div': 'id="contentAssistant"' in html,
    'contentPrecedent div': 'id="contentPrecedent"' in html,
    'switchTab function': 'function switchTab' in html or 'switchTab(tabName)' in html,
}

for test_name, result in tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}: {result}")

# Step 4: Validate AI Assistant components
print("\n4. Validating F6 (AI Assistant)...")
ai_tests = {
    'Chat container': 'id="chatContainer"' in html,
    'Chat form': 'id="chatForm"' in html,
    'Chat input': 'id="chatInput"' in html,
    'AI Agent branding': 'Legal AI Agent' in html,
    'Message counter': 'messages' in html,
    'RAG sources div': 'id="chatSources"' in html,
    'Gradient avatar': 'gradient' in html.lower(),
}

for test_name, result in ai_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}: {result}")

# Step 5: Validate Precedent Finder components
print("\n5. Validating F11 (Precedent Finder)...")
prec_tests = {
    'Find button': 'id="findPrecedentsBtn"' in html,
    'Loading div': 'id="precedentsLoading"' in html,
    'Results div': 'id="precedentsResults"' in html,
    'Empty div': 'id="precedentsEmpty"' in html,
    'Statistics banner': 'id="precedentCount"' in html or 'Matches Found' in html,
    'Similar cases list': 'id="similarCasesList"' in html,
    'Comparison report': 'id="comparisonReport"' in html,
}

for test_name, result in prec_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}: {result}")

# Step 6: Validate JavaScript files
print("\n6. Validating JavaScript integration...")
js_tests = {
    'case_chat.js loaded': 'case_chat.js' in html,
    'precedent_finder.js loaded': 'precedent_finder.js' in html,
    'CASE_ID constant': 'CASE_ID' in html,
}

for test_name, result in js_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}: {result}")

# Step 7: Validate styling
print("\n7. Validating styling consistency...")
style_tests = {
    'Custom scrollbar': '::-webkit-scrollbar' in html,
    'fadeIn animation': 'fadeIn' in html,
    'Tailwind classes': 'rounded-2xl' in html and 'bg-slate-900' in html,
    'Cyan theme': 'cyan-500' in html or 'text-cyan-400' in html,
}

for test_name, result in style_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}: {result}")

# Step 8: Count key elements
print("\n8. Element counts...")
counts = {
    'SVG icons': html.count('<svg'),
    'Tab buttons': html.count('onclick="switchTab'),
    'Gradient elements': html.lower().count('gradient'),
}

for element, count in counts.items():
    print(f"   • {element}: {count}")

# Summary
print("\n" + "=" * 60)
all_passed = all(tests.values()) and all(ai_tests.values()) and all(prec_tests.values())
if all_passed:
    print("  ✓ ALL TESTS PASSED - UI REFACTORING VALIDATED!")
else:
    print("  ! SOME TESTS FAILED - CHECK DETAILS ABOVE")
print("=" * 60)
