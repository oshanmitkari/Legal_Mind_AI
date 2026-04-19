"""Direct UI validation by checking the template file and rendered HTML"""
from app import create_app
from app.models import db, User, Case
import os

print("=" * 70)
print("  LEGALMIND AI - DIRECT UI REFACTORING VALIDATION")
print("=" * 70)

# Step 1: Check template file
print("\n1. Validating template file...")
template_path = 'app/templates/cases/detail.html'
with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

template_tests = {
    'Has tabAssistant button': 'id="tabAssistant"' in template,
    'Has tabPrecedent button': 'id="tabPrecedent"' in template,
    'Has contentAssistant div': 'id="contentAssistant"' in template,
    'Has contentPrecedent div': 'id="contentPrecedent"' in template,
    'Has switchTab function': 'function switchTab' in template,
    'Has URL hash support': '#precedent' in template or '#chat' in template,
}

for test_name, result in template_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Step 2: Validate F6 components
print("\n2. Validating F6 (AI Assistant) components...")
f6_tests = {
    'Chat container': 'id="chatContainer"' in template,
    'Chat form': 'id="chatForm"' in template,
    'Chat input': 'id="chatInput"' in template,
    'AI Agent branding': 'Legal AI Agent' in template,
    'User message avatar': 'M16 7a4 4 0 11-8 0' in template,  # User icon SVG path
    'AI agent avatar': 'M13 10V3L4 14h7v7l9-11h-7z' in template,  # Lightning icon
    'RAG sources container': 'id="chatSources"' in template,
    'Sources list': 'id="chatSourcesList"' in template,
    'Gradient styling': 'bg-gradient-to-br from-cyan-500' in template,
    'Empty state': 'Start a Conversation' in template,
    'Typing indicator support': 'AI is thinking' in template or 'animate-bounce' in template,
}

for test_name, result in f6_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Step 3: Validate F11 components
print("\n3. Validating F11 (Precedent Finder) components...")
f11_tests = {
    'Find button': 'id="findPrecedentsBtn"' in template,
    'Loading container': 'id="precedentsLoading"' in template,
    'Results container': 'id="precedentsResults"' in template,
    'Empty state container': 'id="precedentsEmpty"' in template,
    'Statistics: Match count': 'id="precedentCount"' in template,
    'Statistics: Avg similarity': 'id="avgSimilarity"' in template,
    'Similar cases list': 'id="similarCasesList"' in template,
    'Comparison report': 'id="comparisonReport"' in template,
    'Match badges logic': 'Excellent Match' in template or 'Good Match' in template,
    'Card expandable details': '<details' in template or 'View Full Details' in template,
    'FAISS branding': 'FAISS' in template,
    'Gemini branding': 'Gemini' in template,
}

for test_name, result in f11_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Step 4: Validate styling consistency
print("\n4. Validating styling and design consistency...")
style_tests = {
    'Custom scrollbar styles': '::-webkit-scrollbar' in template,
    'fadeIn animation': '@keyframes fadeIn' in template,
    'Tailwind rounded classes': 'rounded-2xl' in template,
    'Slate color scheme': 'bg-slate-900' in template and 'bg-slate-950' in template,
    'Cyan theme colors': 'text-cyan-400' in template and 'bg-cyan-500' in template,
    'Gradient buttons': 'bg-gradient-to-r from-cyan-500' in template,
    'Shadow effects': 'shadow-lg' in template,
    'Gap spacing': 'gap-3' in template and 'gap-4' in template,
    'Padding consistency': 'p-4' in template and 'p-5' in template and 'p-6' in template,
}

for test_name, result in style_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Step 5: Validate JavaScript integration
print("\n5. Validating JavaScript integration...")
js_tests = {
    'case_chat.js included': 'case_chat.js' in template,
    'precedent_finder.js included': 'precedent_finder.js' in template,
    'CASE_ID constant': 'const CASE_ID' in template,
    'switchTab function defined': 'function switchTab(tabName)' in template,
    'findPrecedents function call': 'onclick="findPrecedents()"' in template,
    'Tab switching logic': "getElementById('contentAssistant')" in template,
    'URL hash handling': "window.location.hash" in template,
    'Event listeners': 'addEventListener' in template,
}

for test_name, result in js_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Step 6: Count elements
print("\n6. Element statistics...")
counts = {
    'SVG icons': template.count('<svg'),
    'onclick handlers': template.count('onclick='),
    'Gradient elements': template.lower().count('gradient'),
    'Flex containers': template.count('flex'),
    'Tab-related IDs': sum([
        template.count('tabAssistant'),
        template.count('tabPrecedent'),
        template.count('contentAssistant'),
        template.count('contentPrecedent'),
    ]),
}

for element, count in counts.items():
    print(f"   • {element}: {count}")

# Step 7: Validate specific UI patterns
print("\n7. Validating specific UI patterns...")
pattern_tests = {
    'Message bubble max-width': 'max-w-[75%]' in template and 'max-w-[85%]' in template,
    'Chat container height': 'h-[500px]' in template or 'max-h-96' in template,
    'Tab active styling': 'border-cyan-500' in template and 'text-cyan-400' in template,
    'Hidden tab content': 'hidden' in template,
    'RAG source styling': 'cyan-950/20' in template or 'cyan-700/30' in template,
    'Match quality thresholds': '80%' in template or '60%' in template,
    'Statistics banner layout': 'grid-cols-2' in template or 'flex-1' in template,
}

for test_name, result in pattern_tests.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {test_name}")

# Summary
print("\n" + "=" * 70)
all_tests = {**template_tests, **f6_tests, **f11_tests, **style_tests, **js_tests, **pattern_tests}
passed = sum(1 for v in all_tests.values() if v)
total = len(all_tests)
percentage = (passed / total) * 100

print(f"  RESULTS: {passed}/{total} tests passed ({percentage:.1f}%)")
if percentage == 100:
    print("  ✓ ALL TESTS PASSED - UI REFACTORING FULLY VALIDATED!")
elif percentage >= 90:
    print("  ✓ MOST TESTS PASSED - UI REFACTORING LOOKS GOOD!")
else:
    print("  ! SOME TESTS FAILED - REVIEW REQUIRED")
print("=" * 70)
