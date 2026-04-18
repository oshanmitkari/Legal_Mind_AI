# LegalMind AI - Startup Instructions

## ✅ Environment Setup Complete!

Your virtual environment has been created and core dependencies are installed.

### What's Been Done:

1. ✅ **Virtual Environment Created**: `venv/` directory in backend
2. ✅ **Pip Upgraded**: Latest pip, setuptools, wheel
3. ✅ **Core Flask Packages Installed**:
   - Flask 2.3.2
   - Flask-SQLAlchemy 3.0.5
   - Flask-Login 0.6.2
   - Flask-Cors 4.0.0
   - Werkzeug 2.3.6
   - All dependencies (Jinja2, SQLAlchemy, etc.)

4. ⏳ **AI Packages Installing** (in progress):
   - google-generativeai (for Gemini AI)
   - numpy (for numerical operations)

### Next Steps to Run the Application:

#### Option 1: Wait for AI Packages  (Recommended)

The AI packages are currently installing. Once complete (check PowerShell window), run:

```powershell
cd c:\Users\oshan\Desktop\legalmind-ai\legalmind-ai\backend
.\venv\Scripts\Activate.ps1
python run.py
```

#### Option 2: Run Without AI Features (Immediate)

If you want to start the app immediately without waiting, you can run with basic features (F1-F4 will work, F6-F9 AI features will be disabled):

```powershell
cd c:\Users\oshan\Desktop\legalmind-ai\legalmind-ai\backend
.\venv\Scripts\Activate.ps1
python run.py
```

The app will start even without google-generativeai. AI features will show errors but the core system (auth, case management, deadlines) will function.

### After Application Starts:

1. Open browser: **http://localhost:5000**
2. Register with test credentials:
   - Enrollment: `MH/1234/2020`
   - Name: `Raj Kumar`
   - State: `Maharashtra`
   - Password: (any password)

### Install Remaining Packages Later:

If AI packages didn't finish installing, you can install them anytime:

```powershell
.\venv\Scripts\Activate.ps1
pip install google-generativeai numpy
```

### Troubleshooting:

**If venv activation fails in PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**Or use Command Prompt (cmd.exe) instead:**
```cmd
cd c:\Users\oshan\Desktop\legalmind-ai\legalmind-ai\backend
venv\Scripts\activate.bat
python run.py
```

### Features Available Without AI Packages:

- ✅ F1: Advocate Verification
- ✅ F2: Secure Login
- ✅ F3: Case Management
- ✅ F4: Deadline Tracking
- ❌ F5: Document Upload (needs PyMuPDF)
- ❌ F6: AI Chat (needs Gemini)
- ❌ F7: Legal Research (needs Gemini)
- ❌ F8: Document Drafter (needs Gemini)
- ❌ F9: Section Suggester (needs Gemini)
- ✅ F10: Risk Scoring (basic version works, AI analysis needs Gemini)

### When All Packages Are Installed:

You'll have full access to all 10 features. The installation is still running in the background.

---

**Status**: Core backend is ready. AI features will be enabled once google-generativeai finishes installing.
