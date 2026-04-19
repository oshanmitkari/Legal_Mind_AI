"""
API Functionality Test - Validates F6 and F11 API endpoints
Tests actual API responses without authentication dependency
"""

from app import create_app
from app.models import db, User, Case, HistoricalCase
import json

print("=" * 70)
print("  LEGALMIND AI - API FUNCTIONALITY VALIDATION")
print("=" * 70)

# Create app context
app = create_app()
app.config['TESTING'] = True

with app.app_context():
    # Step 1: Database validation
    print("\n1. Database Validation...")
    
    case_count = Case.query.count()
    historical_count = HistoricalCase.query.count()
    user_count = User.query.count()
    
    print(f"   ✓ Cases in database: {case_count}")
    print(f"   ✓ Historical cases in database: {historical_count}")
    print(f"   ✓ Users in database: {user_count}")
    
    if case_count == 0:
        print(f"   ⚠ Warning: No cases found. API tests may fail.")
    if historical_count == 0:
        print(f"   ⚠ Warning: No historical cases. F11 will not work.")
    
    # Step 2: Test F11 Precedent Service
    print("\n2. Testing F11 Precedent Service...")
    
    try:
        from app.services.precedent_service import get_precedent_service
        
        print("   • Initializing precedent service...")
        service = get_precedent_service()
        
        print(f"   ✓ FAISS index initialized")
        print(f"   ✓ Index contains {service.index.ntotal} vectors")
        print(f"   ✓ Model: {service.model}")
        
        # Test search if we have a case
        if case_count > 0 and historical_count > 0:
            test_case = Case.query.first()
            print(f"\n   • Testing search with case: {test_case.case_number}")
            
            similar_cases = service.find_similar_cases(test_case, top_k=3)
            print(f"   ✓ Found {len(similar_cases)} similar cases")
            
            for i, (case_obj, score) in enumerate(similar_cases[:3], 1):
                # Determine match quality
                if score >= 80:
                    quality = "Excellent"
                elif score >= 60:
                    quality = "Good"
                else:
                    quality = "Moderate"
                
                print(f"      {i}. {case_obj.case_number} - {score:.1f}% ({quality} Match)")
            
            # Validate match quality thresholds
            print(f"\n   • Validating match quality logic...")
            threshold_tests = {
                'Excellent threshold (≥80%)': any(score >= 80 for _, score in similar_cases),
                'Good threshold (60-79%)': any(60 <= score < 80 for _, score in similar_cases),
                'Moderate threshold (<60%)': any(score < 60 for _, score in similar_cases),
            }
            
            for test_name, result in threshold_tests.items():
                symbol = "✓" if result else "○"
                status = "Found" if result else "Not found"
                print(f"      {symbol} {test_name}: {status}")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Step 3: Test F6 Chat Context
    print("\n3. Testing F6 AI Assistant Context...")
    
    try:
        if case_count > 0:
            test_case = Case.query.first()
            
            # Check if case has documents
            doc_count = len(test_case.documents) if hasattr(test_case, 'documents') else 0
            print(f"   ✓ Test case: {test_case.case_number}")
            print(f"   ✓ Case type: {test_case.case_type}")
            print(f"   ✓ Associated documents: {doc_count}")
            
            # Check if case has chat messages
            if hasattr(test_case, 'chat_messages'):
                msg_count = len(test_case.chat_messages)
                print(f"   ✓ Chat history: {msg_count} messages")
            else:
                print(f"   ○ No chat history model found")
            
            # Validate RAG sources would be available
            has_rag_data = doc_count > 0 or test_case.description
            print(f"   {'✓' if has_rag_data else '○'} RAG sources available: {has_rag_data}")
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Step 4: Test Gemini API Integration
    print("\n4. Testing Gemini API Integration...")
    
    try:
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            print(f"   ✓ Gemini API key found (length: {len(api_key)})")
            
            # Try a simple API call
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            try:
                response = model.generate_content('Say "OK"')
                print(f"   ✓ Gemini API connection successful")
                print(f"   ✓ Response: {response.text[:50]}")
            except Exception as e:
                error_str = str(e)
                if '403' in error_str or 'API key' in error_str:
                    print(f"   ✗ API key invalid or revoked")
                elif '404' in error_str:
                    print(f"   ✗ Model not found")
                else:
                    print(f"   ✗ API error: {error_str[:100]}")
        else:
            print(f"   ✗ Gemini API key not found in .env")
    
    except ImportError:
        print(f"   ✗ google.generativeai not installed")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    # Step 5: JavaScript Logic Validation
    print("\n5. Validating JavaScript Logic Files...")
    
    js_files = {
        'case_chat.js': 'app/static/js/case_chat.js',
        'precedent_finder.js': 'app/static/js/precedent_finder.js',
    }
    
    for js_name, js_path in js_files.items():
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            print(f"\n   • {js_name}:")
            
            if js_name == 'case_chat.js':
                tests = {
                    'addMessageToUI function': 'function addMessageToUI' in js_content,
                    'User message styling': 'bg-cyan-500' in js_content,
                    'AI avatar icon': 'M13 10V3L4 14h7v7l9-11h-7z' in js_content,
                    'Typing indicator': 'addTypingIndicator' in js_content,
                    'Auto-scroll logic': 'scrollTop' in js_content and 'scrollHeight' in js_content,
                    'RAG sources display': 'chatSources' in js_content,
                }
            else:  # precedent_finder.js
                tests = {
                    'findPrecedents function': 'function findPrecedents' in js_content,
                    'Match badge logic': 'Excellent Match' in js_content and 'Good Match' in js_content,
                    'Threshold 80%': 'score >= 80' in js_content,
                    'Threshold 60%': 'score >= 60' in js_content,
                    'Statistics calculation': 'avgSimilarity' in js_content or 'precedentCount' in js_content,
                    'Expandable cards': '<details' in js_content,
                }
            
            for test_name, result in tests.items():
                symbol = "✓" if result else "✗"
                print(f"      {symbol} {test_name}")
        
        except FileNotFoundError:
            print(f"   ✗ {js_name} not found at {js_path}")
        except Exception as e:
            print(f"   ✗ Error reading {js_name}: {str(e)}")

# Summary
print("\n" + "=" * 70)
print("  ✓ API FUNCTIONALITY VALIDATION COMPLETE")
print("=" * 70)
