# 🔐 LegalMind AI - Login Credentials & Access Guide

## ✅ Server Status: RUNNING

**URL**: http://localhost:5000  
**Status**: ✅ Active and ready  
**Port**: 5000

---

## 👤 YOUR EXISTING ACCOUNT

You already have a registered account!

### Login Credentials:
```
Enrollment Number: MH/1234/2020
Name: Raj Kumar
Password: (the password YOU created during registration)
```

**Note**: I don't have access to your password. Use the password you set when you registered.

---

## 🚀 HOW TO ACCESS THE APPLICATION

### Step 1: Login
1. **Browser is already open** at: http://localhost:5000/login
2. Enter your credentials:
   - **Enrollment Number**: `MH/1234/2020`
   - **Password**: `<your password>`
3. Click **Login**

### Step 2: Access Dashboard
After login, you'll be redirected to the dashboard automatically, or go to:
```
http://localhost:5000/cases/dashboard
```

---

## 🔑 FORGOT YOUR PASSWORD?

Since this is a local development setup, here's how to reset:

### Option 1: Register a New User
Use a different test enrollment number:
```
Enrollment: MH/5678/2019
Name: Priya Singh
State: Maharashtra
Password: test123
```

### Option 2: Reset Database (Fresh Start)
```powershell
cd c:\Users\oshan\Desktop\legalmind-ai\legalmind-ai\backend

# Delete the database
Remove-Item legalmind.db

# Restart server (it will recreate the database)
python run.py

# Then register again
```

---

## 📋 ADDITIONAL TEST ACCOUNTS

You can register with any of these verified Bar Council enrollments:

| Enrollment | Name | State | Status |
|------------|------|-------|--------|
| **MH/1234/2020** | Raj Kumar | Maharashtra | ✅ Already registered |
| MH/5678/2019 | Priya Singh | Maharashtra | Available |
| DL/1001/2021 | Amit Verma | Delhi | Available |
| KA/2234/2020 | Dr. Seema Gupta | Karnataka | Available |
| TN/3456/2018 | V. Raman | Tamil Nadu | Available |
| GJ/7788/2022 | Nirali Shah | Gujarat | Available |

**To register a new account:**
1. Go to: http://localhost:5000/register
2. Choose any enrollment from above
3. Enter the EXACT name shown
4. Select the matching state
5. Create your password
6. Click "Create Account"

---

## 🎯 WHAT TO TEST AFTER LOGIN

### Test F7: Legal Research (Easy - No case needed)
```
1. Login first
2. Go to: http://localhost:5000/ai/research
3. Type query: "What is Section 420 IPC?"
4. Click "Research"
5. See AI-powered legal analysis!
```

### Test F6: AI Case Assistant (Need to create case first)
```
1. Login
2. Go to dashboard: http://localhost:5000/cases/dashboard
3. Create a new case:
   - Case Number: CR/420/2024
   - Client Name: Test Client
   - Type: Criminal
   - Description: Fraud case
4. Click on the case
5. Scroll to chat interface
6. Ask: "What evidence should I collect?"
```

### Test Other Features
- **F3: Dashboard**: http://localhost:5000/cases/dashboard
- **F4: Deadlines**: http://localhost:5000/deadlines/
- **F10: Risk Scoring**: Click "Calculate Risk" on any case
- **Profile**: http://localhost:5000/profile

---

## 🐛 TROUBLESHOOTING

### Can't Login?
**Issue**: "Invalid credentials" error  
**Solution**: 
- Make sure Enrollment Number is EXACT: `MH/1234/2020`
- Password is case-sensitive
- If still fails, register with a new enrollment number

### Page Not Loading?
**Issue**: "Cannot connect" error  
**Solution**: 
- Check if server is running (look for Terminal 41511)
- Restart server if needed:
  ```powershell
  cd backend
  .\venv\Scripts\Activate.ps1
  python run.py
  ```

### Registration Fails?
**Issue**: "Verification failed"  
**Solution**:
- Name must EXACTLY match the enrollment
- `MH/1234/2020` → `Raj Kumar` (not raj kumar or RAJ KUMAR)
- State must match enrollment prefix

---

## 📊 YOUR ACCOUNT DETAILS

From the database, here's your account info:

```
User ID: 1
Name: Raj Kumar
Enrollment: MH/1234/2020
State: Maharashtra
Verified: ✅ Yes
Admin: No
```

---

## 🎉 QUICK START CHECKLIST

- [x] Server is running ✅
- [x] You have a registered account ✅
- [ ] Login at http://localhost:5000/login
- [ ] Test F7: Legal Research
- [ ] Create a case
- [ ] Test F6: AI Chat
- [ ] Upload a PDF document
- [ ] Calculate risk score

---

## 🔗 IMPORTANT URLS

**Main Access**:
- Login: http://localhost:5000/login
- Dashboard: http://localhost:5000/cases/dashboard
- Legal Research: http://localhost:5000/ai/research

**After Creating a Case**:
- Case Detail: http://localhost:5000/cases/1
- AI Chat: (embedded in case detail)

---

## ⚙️ SERVER INFORMATION

**Status**: ✅ Running on Terminal 41511  
**Started**: Successfully  
**API Key**: ✅ Configured  
**Database**: ✅ Created (1 user registered)  
**FAISS**: ✅ Law index built (39 sections)

---

## 📝 NOTES

1. **Password**: I cannot see your password. Use what you set during registration.
2. **Security**: All passwords are hashed and cannot be retrieved.
3. **Local Only**: This is running on your machine only (not accessible from internet).
4. **Auto-save**: All data saves automatically to `legalmind.db` file.

---

## 🎯 NEXT STEPS

### RIGHT NOW:
1. **Login** using enrollment `MH/1234/2020` and your password
2. Browser is already open at login page
3. Start testing features!

### IF YOU FORGOT PASSWORD:
Register with a new enrollment number (see "Additional Test Accounts" above)

---

**Your application is LIVE and ready to use!** 🚀

**Login at: http://localhost:5000/login**

**Enrollment**: `MH/1234/2020`  
**Password**: `<your password>`
