import requests
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

# Test login
print('=== Login ===')
login_data = {
    'enrollment_number': 'KA/2234/2020',
    'password': 'test123'
}
login_response = requests.post(f'{BASE_URL}/login', json=login_data)
print(f'Login response: {login_response.status_code}')
print(f'Login data: {login_response.json()}')
print(f'Cookies: {login_response.cookies}')

# Create session with cookies
session = requests.Session()
session.cookies.update(login_response.cookies)

# Test GET /cases/deadlines directly
print('\n=== Testing GET /cases/deadlines ===')
print(f'URL: {BASE_URL}/cases/deadlines')
response = session.get(f'{BASE_URL}/cases/deadlines')
print(f'Response status: {response.status_code}')
print(f'Response headers: {response.headers}')
if response.status_code == 200:
    print(f'Response data: {response.json()}')
else:
    print(f'Response text: {response.text[:500]}')