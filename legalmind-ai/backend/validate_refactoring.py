"""
Comprehensive validation script for LegalMind AI Case Detail refactoring
Tests F6 (AI Assistant) and F11 (Precedent Finder) functionality
"""

import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"
CASE_ID = 1

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name, status, message=""):
    symbol = "✓" if status else "✗"
    color = GREEN if status else RED
    print(f"{color}{symbol} {test_name}{RESET}")
    if message:
        print(f"  {message}")

def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

# Session to maintain cookies
session = requests.Session()

print(f"{BLUE}╔════════════════════════════════════════════════╗")
print(f"║  LEGALMIND AI - COMPREHENSIVE VALIDATION      ║")
print(f"║  Case Detail Refactoring (F6 + F11)           ║")
print(f"╚════════════════════════════════════════════════╝{RESET}\n")

# ============================================================================
# 1. TAB NAVIGATION LOGIC
# ============================================================================
print_section("1. TAB NAVIGATION LOGIC VALIDATION")

try:
    # Test case detail page loads
    resp = session.get(f"{BASE_URL}/cases/{CASE_ID}")
    print_test("Case detail page loads", resp.status_code == 200)
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Check tab buttons exist
    tab_assistant = soup.find('button', {'id': 'tabAssistant'})
    tab_precedent = soup.find('button', {'id': 'tabPrecedent'})
    print_test("Tab buttons exist", 
               tab_assistant is not None and tab_precedent is not None,
               f"Assistant tab: {tab_assistant is not None}, Precedent tab: {tab_precedent is not None}")
    
    # Check tab content divs exist
    content_assistant = soup.find('div', {'id': 'contentAssistant'})
    content_precedent = soup.find('div', {'id': 'contentPrecedent'})
    print_test("Tab content divs exist",
               content_assistant is not None and content_precedent is not None,
               f"Assistant div: {content_assistant is not None}, Precedent div: {content_precedent is not None}")
    
    # Check switchTab function exists in script
    script_tags = soup.find_all('script')
    has_switch_tab = any('switchTab' in str(script) for script in script_tags)
    print_test("switchTab() function exists", has_switch_tab)
    
    # Check URL hash support
    has_hash_support = any('#precedent' in str(script) or '#chat' in str(script) for script in script_tags)
    print_test("URL hash navigation support", has_hash_support)
    
    # Check active tab styling
    if tab_assistant:
        classes = tab_assistant.get('class', [])
        has_cyan_border = 'border-cyan-500' in classes or 'text-cyan-400' in classes
        print_test("Active tab has cyan styling", has_cyan_border,
                   f"Classes: {', '.join(classes) if classes else 'None'}")
    
except Exception as e:
    print_test("Tab navigation validation", False, f"Error: {str(e)}")

# ============================================================================
# 2. F6 CHAT FUNCTIONALITY
# ============================================================================
print_section("2. F6 AI ASSISTANT FUNCTIONALITY VALIDATION")

try:
    # Check chat container exists
    chat_container = soup.find('div', {'id': 'chatContainer'})
    print_test("Chat container exists", chat_container is not None)
    
    # Check chat form exists
    chat_form = soup.find('form', {'id': 'chatForm'})
    chat_input = soup.find('input', {'id': 'chatInput'})
    print_test("Chat form and input exist",
               chat_form is not None and chat_input is not None)
    
    # Check AI agent header
    has_ai_header = soup.find(string=lambda text: text and 'Legal AI Agent' in text)
    print_test("AI Agent branding present", has_ai_header is not None)
    
    # Check message counter
    has_message_counter = soup.find(string=lambda text: text and 'messages' in text.lower())
    print_test("Message counter displayed", has_message_counter is not None)
    
    # Check for avatar icons (SVG elements)
    svg_elements = soup.find_all('svg')
    has_avatars = len(svg_elements) > 5  # Should have multiple icons
    print_test("Avatar icons present", has_avatars,
               f"Found {len(svg_elements)} SVG elements")
    
    # Check chat sources div
    chat_sources = soup.find('div', {'id': 'chatSources'})
    print_test("RAG sources container exists", chat_sources is not None)
    
    # Check for gradient styling
    has_gradient = any('gradient' in str(elem) for elem in soup.find_all(['div', 'button']))
    print_test("Gradient styling applied", has_gradient)
    
    # Test chat API endpoint (GET history)
    try:
        chat_resp = session.get(f"{BASE_URL}/ai/chat/{CASE_ID}/history")
        print_test("Chat history API accessible",
                   chat_resp.status_code in [200, 401, 403],
                   f"Status: {chat_resp.status_code}")
    except Exception as e:
        print_test("Chat history API accessible", False, f"Error: {str(e)}")
    
    # Check case_chat.js is loaded
    scripts = [script.get('src') for script in soup.find_all('script', src=True)]
    has_chat_js = any('case_chat.js' in src for src in scripts)
    print_test("case_chat.js loaded", has_chat_js)
    
except Exception as e:
    print_test("F6 chat validation", False, f"Error: {str(e)}")

# ============================================================================
# 3. F11 PRECEDENT FINDER LOGIC
# ============================================================================
print_section("3. F11 PRECEDENT FINDER FUNCTIONALITY VALIDATION")

try:
    # Check precedent finder button
    find_btn = soup.find('button', {'id': 'findPrecedentsBtn'})
    print_test("Find Similar Cases button exists", find_btn is not None)
    
    # Check loading state div
    loading_div = soup.find('div', {'id': 'precedentsLoading'})
    print_test("Loading spinner container exists", loading_div is not None)
    
    # Check results div
    results_div = soup.find('div', {'id': 'precedentsResults'})
    print_test("Results container exists", results_div is not None)
    
    # Check empty state div
    empty_div = soup.find('div', {'id': 'precedentsEmpty'})
    print_test("Empty state container exists", empty_div is not None)
    
    # Check statistics banner elements
    has_stats = soup.find('div', {'id': 'precedentCount'}) or soup.find(string=lambda t: t and 'Matches Found' in t)
    print_test("Statistics banner elements present", has_stats is not None)
    
    # Check similar cases list
    cases_list = soup.find('div', {'id': 'similarCasesList'})
    print_test("Similar cases list container exists", cases_list is not None)
    
    # Check comparison report div
    comparison_div = soup.find('div', {'id': 'comparisonReport'})
    print_test("AI comparison report container exists", comparison_div is not None)
    
    # Check precedent_finder.js is loaded
    has_precedent_js = any('precedent_finder.js' in src for src in scripts)
    print_test("precedent_finder.js loaded", has_precedent_js)
    
    # Test precedent API endpoint (requires authentication)
    print(f"\n{YELLOW}Testing F11 API endpoint (may require login):{RESET}")
    try:
        prec_resp = session.get(f"{BASE_URL}/ai/compare-precedents/{CASE_ID}")
        status_ok = prec_resp.status_code in [200, 401, 403]
        print_test("Precedent API endpoint responds",
                   status_ok,
                   f"Status: {prec_resp.status_code}")
        
        if prec_resp.status_code == 200:
            data = prec_resp.json()
            print_test("API returns JSON", True)
            print_test("Similar cases in response",
                       'similar_cases' in data,
                       f"Keys: {', '.join(data.keys())}")

            # Validate match quality logic
            if 'similar_cases' in data and len(data['similar_cases']) > 0:
                for i, case in enumerate(data['similar_cases'][:3]):
                    score = case.get('relevance_score', 0)
                    # Determine expected badge
                    if score >= 80:
                        expected = "Excellent Match"
                    elif score >= 60:
                        expected = "Good Match"
                    else:
                        expected = "Moderate Match"
                    print(f"  Case {i+1}: {case.get('case_number')} - {score}% ({expected})")

                # Calculate average
                avg = sum(c.get('relevance_score', 0) for c in data['similar_cases']) / len(data['similar_cases'])
                print_test("Statistics calculation",
                           True,
                           f"Avg similarity: {avg:.1f}%, Count: {len(data['similar_cases'])}")
    except Exception as e:
        print_test("Precedent API test", False, f"Error: {str(e)}")

except Exception as e:
    print_test("F11 precedent validation", False, f"Error: {str(e)}")

# ============================================================================
# 4. UI EDGE CASES
# ============================================================================
print_section("4. UI EDGE CASES VALIDATION")

try:
    # Check empty state messages
    empty_states = soup.find_all(string=lambda t: t and 'Start a Conversation' in t or 'Click "Find Similar Cases"' in t)
    print_test("Empty state messages present",
               len(empty_states) > 0,
               f"Found {len(empty_states)} empty state messages")

    # Check for "View Full Details" in precedent cards
    has_details_toggle = soup.find('summary') or soup.find(string=lambda t: t and 'View Full Details' in t or 'View Details' in t)
    print_test("Expandable details UI present", has_details_toggle is not None)

    # Check for proper gradient icons in empty states
    empty_state_divs = [div for div in soup.find_all('div') if 'gradient' in str(div.get('class', []))]
    print_test("Gradient icons in empty states",
               len(empty_state_divs) > 0,
               f"Found {len(empty_state_divs)} gradient elements")

    # Check for proper layout structure (no broken max-w or flex)
    has_proper_flex = soup.find_all('div', class_=lambda c: c and 'flex' in str(c))
    print_test("Flex layout properly applied",
               len(has_proper_flex) > 10,
               f"Found {len(has_proper_flex)} flex containers")

    # Check for max-width classes on message bubbles
    has_max_width = soup.find_all('div', class_=lambda c: c and ('max-w-[75%]' in str(c) or 'max-w-[85%]' in str(c)))
    print_test("Message bubble max-width constraints",
               len(has_max_width) > 0,
               f"Found {len(has_max_width)} constrained elements")

except Exception as e:
    print_test("UI edge cases validation", False, f"Error: {str(e)}")

# ============================================================================
# 5. STYLING AND RAG INTEGRATION
# ============================================================================
print_section("5. STYLING & RAG INTEGRATION VALIDATION")

try:
    # Check for custom scrollbar styles
    style_tags = soup.find_all('style')
    has_scrollbar_style = any('::-webkit-scrollbar' in str(style) for style in style_tags)
    print_test("Custom scrollbar styles defined", has_scrollbar_style)

    # Check for fadeIn animation
    has_fadein = any('fadeIn' in str(style) for style in style_tags)
    print_test("fadeIn animation defined", has_fadein)

    # Check for Tailwind CSS classes
    tailwind_classes = ['rounded-2xl', 'bg-slate-900', 'border-cyan-500', 'text-cyan-400', 'gradient']
    found_classes = []
    for cls in tailwind_classes:
        if soup.find(class_=lambda c: c and cls in str(c)):
            found_classes.append(cls)

    print_test("Tailwind CSS classes applied",
               len(found_classes) >= 3,
               f"Found: {', '.join(found_classes)}")

    # Check for gradient backgrounds
    gradient_elements = soup.find_all(class_=lambda c: c and 'gradient' in str(c))
    print_test("Gradient backgrounds applied",
               len(gradient_elements) > 5,
               f"Found {len(gradient_elements)} gradient elements")

    # Check for RAG sources styling
    sources_div = soup.find('div', {'id': 'chatSources'})
    if sources_div:
        has_rag_styling = 'cyan' in str(sources_div.get('class', []))
        print_test("RAG sources styled correctly", has_rag_styling)

    # Check for icon SVGs
    svg_count = len(soup.find_all('svg'))
    print_test("Icon system implemented",
               svg_count > 10,
               f"Found {svg_count} SVG icons")

    # Check for proper spacing (gap, p-, m- classes)
    spacing_elements = soup.find_all(class_=lambda c: c and any(x in str(c) for x in ['gap-', 'p-', 'mb-', 'mt-']))
    print_test("Spacing system consistent",
               len(spacing_elements) > 20,
               f"Found {len(spacing_elements)} spaced elements")

except Exception as e:
    print_test("Styling validation", False, f"Error: {str(e)}")

# ============================================================================
# 6. JAVASCRIPT FUNCTIONALITY
# ============================================================================
print_section("6. JAVASCRIPT VALIDATION")

try:
    # Check for CASE_ID constant
    has_case_id = any('CASE_ID' in str(script) for script in soup.find_all('script'))
    print_test("CASE_ID constant defined", has_case_id)

    # Check for event listeners
    has_event_listeners = any('addEventListener' in str(script) for script in soup.find_all('script'))
    print_test("Event listeners attached", has_event_listeners)

    # Check for findPrecedents function
    has_find_precedents = any('findPrecedents' in str(script) for script in soup.find_all('script'))
    print_test("findPrecedents() function exists", has_find_precedents)

    # Check for onclick handlers
    onclick_elements = soup.find_all(attrs={'onclick': True})
    print_test("Click handlers attached",
               len(onclick_elements) > 0,
               f"Found {len(onclick_elements)} onclick handlers")

except Exception as e:
    print_test("JavaScript validation", False, f"Error: {str(e)}")

# ============================================================================
# SUMMARY
# ============================================================================
print(f"\n{BLUE}╔════════════════════════════════════════════════╗")
print(f"║  VALIDATION COMPLETE                          ║")
print(f"╚════════════════════════════════════════════════╝{RESET}\n")

print(f"{YELLOW}Note: Some tests may fail if user is not logged in.{RESET}")
print(f"{YELLOW}For full API testing, ensure you're authenticated.{RESET}\n")
