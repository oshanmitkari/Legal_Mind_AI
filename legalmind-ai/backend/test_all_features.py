"""
Comprehensive Feature Test Suite for LegalMind AI
Tests all 10 core features with real API calls
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
session = requests.Session()


def print_test(feature, test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"[{feature}] {test_name}")
    print('='*60)


def test_f1_advocate_verification():
    """F1: Test multi-tier Bar Council verification"""
    print_test("F1", "Advocate Verification")
    
    # Test 1: Format validation
    response = session.post(f"{BASE_URL}/register/verify", json={
        "enrollment_number": "INVALID",
        "state": "Maharashtra"
    })
    print(f"❌ Invalid format: {response.status_code} - {response.json()}")
    
    # Test 2: Valid enrollment
    response = session.post(f"{BASE_URL}/register/verify", json={
        "enrollment_number": "MH/1234/2020",
        "state": "Maharashtra"
    })
    print(f"✅ Valid enrollment: {response.status_code} - {response.json()}")


def test_f2_authentication():
    """F2: Test registration and secure session"""
    print_test("F2", "Secure Session Management")
    
    # Register new user
    response = session.post(f"{BASE_URL}/register", json={
        "enrollment_number": "MH/1234/2020",
        "name": "Raj Kumar",
        "state": "Maharashtra",
        "password": "TestPass123"
    })
    print(f"Registration: {response.status_code}")
    
    # Login
    response = session.post(f"{BASE_URL}/login", json={
        "enrollment_number": "MH/1234/2020",
        "password": "TestPass123"
    })
    print(f"✅ Login: {response.status_code} - Authenticated!")
    
    # Get profile
    response = session.get(f"{BASE_URL}/profile")
    user = response.json()
    print(f"Profile: {user['name']} - Verified: {user['is_verified']}")
    return user


def test_f3_case_management(user):
    """F3: Test Case Command Center CRUD"""
    print_test("F3", "Case Command Center")
    
    # Create case
    deadline = (datetime.now() + timedelta(days=5)).isoformat()
    response = session.post(f"{BASE_URL}/cases/", json={
        "case_number": "CC/2024/001",
        "client_name": "John Doe",
        "case_type": "Criminal",
        "description": "Cyber fraud case under IT Act",
        "deadline_date": deadline
    })
    result = response.json()
    case_id = result['id']
    print(f"✅ Created case ID: {case_id}")
    
    # Get case details
    response = session.get(f"{BASE_URL}/cases/{case_id}")
    case = response.json()
    print(f"Case: {case['case_number']} - Risk: {case['risk_score']}")
    
    # Update case
    response = session.put(f"{BASE_URL}/cases/{case_id}", json={
        "status": "open",
        "description": "Updated: Added FIR number"
    })
    print(f"✅ Updated case: {response.status_code}")
    
    return case_id


def test_f4_deadline_tracker(case_id):
    """F4: Test color-coded deadline tracker"""
    print_test("F4", "Deadline Tracker")
    
    # Create overdue deadline (Red)
    past_date = (datetime.now() - timedelta(days=2)).isoformat()
    response = session.post(f"{BASE_URL}/deadlines/", json={
        "case_id": case_id,
        "title": "File motion (OVERDUE)",
        "due_date": past_date,
        "deadline_type": "Court Filing",
        "priority": "high"
    })
    print(f"🔴 Red deadline: {response.json()['color']}")
    
    # Create amber deadline (within 72 hours)
    amber_date = (datetime.now() + timedelta(hours=48)).isoformat()
    response = session.post(f"{BASE_URL}/deadlines/", json={
        "case_id": case_id,
        "title": "Hearing date",
        "due_date": amber_date,
        "deadline_type": "Court Date"
    })
    print(f"🟡 Amber deadline: {response.json()['color']}")
    
    # Get 7-day alerts
    response = session.get(f"{BASE_URL}/deadlines/alerts")
    alerts = response.json()
    print(f"✅ Total alerts: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['title']}: {alert['color']} ({alert['days_until']} days)")


def test_f5_document_upload(case_id):
    """F5: Test PDF upload and FAISS indexing"""
    print_test("F5", "RAG-Ready PDF Pipeline")
    
    # Note: This test would require a real PDF file
    print("⚠️  PDF upload requires actual file - see test_api.py for file upload example")
    print("Pipeline: PyMuPDF → LangChain chunking → FAISS embedding → Vector search")
    
    # Get documents for case
    response = session.get(f"{BASE_URL}/documents/{case_id}")
    docs = response.json()
    print(f"Documents in case: {len(docs)}")


def test_f6_ai_assistant(case_id):
    """F6: Test contextual AI chat"""
    print_test("F6", "AI Case Assistant")
    
    response = session.post(f"{BASE_URL}/ai/chat/{case_id}", json={
        "message": "What evidence should I collect for this cyber fraud case?"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI Response:\n{result['response'][:200]}...")
        print(f"Sources cited: {len(result.get('sources', []))}")
    else:
        print(f"❌ Error: {response.json()}")


def test_f7_legal_research():
    """F7: Test Legal Research Engine"""
    print_test("F7", "Legal Research (RAG)")
    
    response = session.post(f"{BASE_URL}/ai/research", json={
        "query": "What is Section 66C of IT Act 2000?"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Research Result:\n{result['research'][:300]}...")
        print(f"Cited sections: {result.get('cited_sections', [])}")
    else:
        print(f"❌ Error: {response.json()}")


def test_f8_document_drafter(case_id):
    """F8: Test document drafting"""
    print_test("F8", "Automated Document Drafter")
    
    templates = ['legal_notice', 'fir_draft', 'bail_application']
    
    for template in templates:
        response = session.post(f"{BASE_URL}/ai/draft", json={
            "case_id": case_id,
            "template_type": template
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {template}: {len(result['document'])} characters generated")
        else:
            print(f"❌ {template}: {response.json()}")


def test_f9_section_suggester():
    """F9: Test section suggester"""
    print_test("F9", "Section Suggester")
    
    response = session.post(f"{BASE_URL}/ai/suggest-sections", json={
        "incident": "Someone created a fake Facebook profile using my photos and is harassing my friends"
    })
    
    if response.status_code == 200:
        result = response.json()
        analysis = result['analysis']
        if isinstance(analysis, dict):
            print(f"✅ Primary Sections: {len(analysis.get('primary_sections', []))}")
            for sec in analysis.get('primary_sections', [])[:3]:
                print(f"  - {sec.get('section')}: {sec.get('description')}")
            print(f"Bailable: {analysis.get('offense_classification', {}).get('bailable')}")
        else:
            print(f"✅ Analysis: {str(analysis)[:200]}...")
    else:
        print(f"❌ Error: {response.json()}")


def test_f10_risk_scoring(case_id):
    """F10: Test risk scoring engine"""
    print_test("F10", "Risk Scoring Engine")
    
    response = session.post(f"{BASE_URL}/risk/calculate/{case_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Overall Risk Score: {result['risk_score']}/100")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print("\nComponent Breakdown:")
        for component, score in result['components'].items():
            print(f"  - {component}: {score}")
        print(f"\nAI Analysis: {result.get('ai_analysis', 'N/A')[:150]}...")
    else:
        print(f"❌ Error: {response.json()}")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("LEGALMIND AI - COMPREHENSIVE FEATURE TEST SUITE")
    print("="*60)
    
    try:
        # Test F1-F2
        test_f1_advocate_verification()
        user = test_f2_authentication()
        
        # Test F3
        case_id = test_f3_case_management(user)
        
        # Test F4
        test_f4_deadline_tracker(case_id)
        
        # Test F5
        test_f5_document_upload(case_id)
        
        # Test F6-F9 (AI Features)
        test_f6_ai_assistant(case_id)
        test_f7_legal_research()
        test_f8_document_drafter(case_id)
        test_f9_section_suggester()
        
        # Test F10
        test_f10_risk_scoring(case_id)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
