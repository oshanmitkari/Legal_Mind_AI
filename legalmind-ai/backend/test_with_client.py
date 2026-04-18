from app import create_app

app = create_app('testing')
with app.test_client() as client:
    # Register and login
    register_resp = client.post('/register', json={
        'enrollment_number': 'TN/3456/2018',
        'name': 'V. Raman',
        'state': 'Tamil Nadu',
        'password': 'test123'
    })
    print(f'Register: {register_resp.status_code}')
    
    login_resp = client.post('/login', json={
        'enrollment_number': 'TN/3456/2018',
        'password': 'test123'
    })
    print(f'Login: {login_resp.status_code}')
    
    # Test /cases/deadlines
    deadlines_resp = client.get('/cases/deadlines')
    print(f'GET /cases/deadlines: {deadlines_resp.status_code}')
    if deadlines_resp.status_code == 200:
        print(f'Data: {deadlines_resp.json}')
    else:
        print(f'Error: {deadlines_resp.data[:200]}')