import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def test_register():
    """Test user registration"""
    data = {
        'enrollment_number': 'DL/1001/2021',
        'name': 'Amit Verma',
        'state': 'Delhi',
        'password': 'test123'
    }
    response = requests.post(f'{BASE_URL}/register', json=data)
    print(f'Register response: {response.status_code}')
    print(f'Register data: {response.json()}')
    return response

def test_login():
    """Test user login"""
    data = {
        'enrollment_number': 'DL/1001/2021',
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

def test_create_case(session, suffix='', deadline_offset=0):
    """Test creating a case with optional deadline"""
    deadline_date = None
    if deadline_offset != 0:
        deadline_date = (datetime.utcnow() + timedelta(days=deadline_offset)).isoformat()
    
    data = {
        'case_number': f'CASE-{suffix}',
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
    print(f'Get deadlines data: {response.json()}')
    return response

if __name__ == '__main__':
    # Test registration
    test_register()

    # Test login
    login_response = test_login()

    # Create session with cookies
    session = requests.Session()
    if login_response.status_code == 200:
        # Copy cookies from login response
        session.cookies.update(login_response.cookies)

        # Test cases endpoints
        print('\n--- Testing cases listing ---')
        test_cases_list(session)
        
        print('\n--- Creating case 1 with overdue deadline (5 days ago) ---')
        create_response1 = test_create_case(session, '002', -5)

        print('\n--- Creating case 2 with due soon deadline (1 day) ---')
        create_response2 = test_create_case(session, '003', 1)

        print('\n--- Creating case 3 with safe deadline (10 days) ---')
        create_response3 = test_create_case(session, '004', 10)

        print('\n--- Creating case 4 without deadline ---')
        create_response4 = test_create_case(session, '005', 0)

        print('\n--- Testing GET /cases/deadlines ---')
        test_get_deadlines(session)

        # Test get specific case with deadline
        if create_response1.status_code == 201:
            case_data = create_response1.json()
            case_id = case_data.get('id')

            print(f'\n--- Getting case {case_id} details ---')
            response = session.get(f'{BASE_URL}/cases/{case_id}')
            print(f'Get case response: {response.status_code}')
            print(f'Get case data: {response.json()}')