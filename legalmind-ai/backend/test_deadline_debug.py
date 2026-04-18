import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

# Test login
print('=== Logging in ===')
login_data = {
    'enrollment_number': 'KA/2234/2020',
    'password': 'test123'
}
login_response = requests.post(f'{BASE_URL}/login', json=login_data)
session = requests.Session()
session.cookies.update(login_response.cookies)

# Test creating a case with deadline
print('\n=== Test 1: Create case with deadline ===')
deadline = (datetime.utcnow() + timedelta(days=-5)).isoformat()
print(f'Sending deadline_date: {deadline}')

case_data = {
    'case_number': f'TEST-{int(datetime.utcnow().timestamp())}',
    'client_name': 'Test Client',
    'case_type': 'Civil',
    'description': 'Test case',
    'deadline_date': deadline
}
print(f'POST body: {json.dumps(case_data, indent=2)}')

response = session.post(f'{BASE_URL}/cases/', json=case_data)
print(f'Response status: {response.status_code}')
print(f'Response body: {response.json()}')

# Get the case details
if response.status_code == 201:
    case_id = response.json().get('id')
    print(f'\n=== Test 2: Get case {case_id} details ===')
    
    case_response = session.get(f'{BASE_URL}/cases/{case_id}')
    print(f'Response status: {case_response.status_code}')
    case_details = case_response.json()
    print(f'Deadline date from DB: {case_details.get("deadline_date")}')
    print(f'Deadline status: {case_details.get("deadline_status")}')
    print(f'Deadline color: {case_details.get("deadline_color")}')