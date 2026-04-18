import requests
import json
from datetime import datetime, timedelta
import uuid

BASE_URL = 'http://127.0.0.1:5000'

def test_register():
    """Test user registration"""
    data = {
        'enrollment_number': 'KA/2234/2020',
        'name': 'Dr. Seema Gupta',
        'state': 'Karnataka',
        'password': 'test123'
    }
    response = requests.post(f'{BASE_URL}/register', json=data)
    print(f'Register response: {response.status_code}')
    print(f'Register data: {response.json()}')
    return response

def test_login():
    """Test user login"""
    data = {
        'enrollment_number': 'KA/2234/2020',
        'password': 'test123'
    }
    response = requests.post(f'{BASE_URL}/login', json=data)
    print(f'Login response: {response.status_code}')
    print(f'Login data: {response.json()}')
    return response

def test_cases_list(session):
    """Test getting cases list"""
    response = session.get(f'{BASE_URL}/cases/')
    print(f'Cases list response: {response.status_code}')
    print(f'Cases list data: {response.json()}')
    return response

def test_create_case(session, deadline_offset=None):
    """Test creating a case with optional deadline"""
    deadline_date = None
    if deadline_offset is not None:
        deadline_date = (datetime.utcnow() + timedelta(days=deadline_offset)).isoformat()
    
    unique_id = str(uuid.uuid4())[:8]
    data = {
        'case_number': f'CASE-{unique_id}',
        'client_name': 'John Doe',
        'case_type': 'Civil',
        'description': 'Test case description',
        'risk_score': 5
    }
    
    if deadline_date:
        data['deadline_date'] = deadline_date
    
    response = session.post(f'{BASE_URL}/cases/', json=data)
    print(f'Create case response: {response.status_code}')
    print(f'Create case data: {response.json()}')
    return response

def test_get_deadlines(session):
    """Test getting all deadlines"""
    response = session.get(f'{BASE_URL}/cases/deadlines')
    print(f'Get deadlines response: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Get deadlines: Found {len(data)} cases with deadlines')
        for deadline in data:
            print(f"  - Case {deadline['case_id']}: {deadline['case_number']} - Status: {deadline['status']} ({deadline['color']})")
    else:
        print(f'Get deadlines error: {response.text}')
    return response

if __name__ == '__main__':
    # Test registration
    print('=== Registration ===')
    test_register()

    # Test login
    print('\n=== Login ===')
    login_response = test_login()

    # Create session with cookies
    session = requests.Session()
    if login_response.status_code == 200:
        # Copy cookies from login response
        session.cookies.update(login_response.cookies)

        # Test cases endpoints
        print('\n=== Testing cases listing ===')
        test_cases_list(session)
        
        print('\n=== Creating case 1: OVERDUE (5 days ago) ===')
        create_response1 = test_create_case(session, -5)

        print('\n=== Creating case 2: DUE SOON (1 day from now) ===')
        create_response2 = test_create_case(session, 1)

        print('\n=== Creating case 3: SAFE (10 days from now) ===')
        create_response3 = test_create_case(session, 10)

        print('\n=== Creating case 4: NO DEADLINE ===')
        create_response4 = test_create_case(session)

        print('\n=== Testing GET /cases/deadlines ===')
        deadlines_response = test_get_deadlines(session)

        # Test get specific case with deadline
        if create_response1.status_code == 201:
            case_data = create_response1.json()
            case_id = case_data.get('id')

            print(f'\n=== Getting case {case_id} details ===')
            response = session.get(f'{BASE_URL}/cases/{case_id}')
            print(f'Get case response: {response.status_code}')
            case_details = response.json()
            print(f'Case details:')
            print(f'  - ID: {case_details.get("id")}')
            print(f'  - Case Number: {case_details.get("case_number")}')
            print(f'  - Deadline: {case_details.get("deadline_date")}')
            print(f'  - Deadline Status: {case_details.get("deadline_status")}')
            print(f'  - Deadline Color: {case_details.get("deadline_color")}')