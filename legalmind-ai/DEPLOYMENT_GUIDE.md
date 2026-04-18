# LegalMind AI - Deployment Guide

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+ 
- pip package manager
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Step 1: Clone & Setup

```bash
cd legalmind-ai/backend
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create `.env` file in `backend/` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///legalmind.db

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Server
PORT=5000
DEBUG=True
```

### Step 5: Initialize Database

The database will auto-create on first run, but you can manually initialize:

```bash
python
>>> from app import create_app
>>> from app.models import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### Step 6: Run the Application

```bash
python run.py
```

Access at: **http://localhost:5000**

---

## 📝 Test User Registration

Use these pre-seeded Bar Council records for testing:

| Enrollment Number | Name | State |
|-------------------|------|-------|
| MH/1234/2020 | Raj Kumar | Maharashtra |
| MH/5678/2019 | Priya Singh | Maharashtra |
| DL/1001/2021 | Amit Verma | Delhi |
| KA/2234/2020 | Dr. Seema Gupta | Karnataka |
| TN/3456/2018 | V. Raman | Tamil Nadu |
| GJ/7788/2022 | Nirali Shah | Gujarat |

**Registration Steps:**
1. Go to `/register`
2. Enter one of the above enrollment numbers
3. Enter the exact name (case-insensitive)
4. Select matching state
5. Choose password
6. System validates and assigns "Verified" badge

---

## 🔧 Feature Testing Checklist

### F1-F2: Authentication
- [ ] Register with valid enrollment number
- [ ] Verify "Verified" badge appears
- [ ] Test invalid enrollment format
- [ ] Attempt duplicate registration (should fail)
- [ ] Login with credentials
- [ ] Verify RLS (can't access other user's cases)

### F3: Case Management
- [ ] Create new case
- [ ] View case dashboard
- [ ] Update case details
- [ ] Delete case
- [ ] Verify cascade delete (deadlines/documents removed)

### F4: Deadline Tracker
- [ ] Add deadline to case
- [ ] View calendar with deadlines
- [ ] Check color coding (red/amber/green)
- [ ] Get 7-day alert list
- [ ] Mark deadline as completed

### F5: Document Upload
- [ ] Upload PDF to case
- [ ] Verify text extraction
- [ ] Check FAISS indexing (metadata JSON updated)
- [ ] Delete document
- [ ] Verify vector cleanup

### F6: AI Case Assistant
- [ ] Open case detail page
- [ ] Send chat message
- [ ] Verify context injection (case details in response)
- [ ] Check RAG retrieval (document snippets cited)
- [ ] View chat history

### F7: Legal Research
- [ ] Use research tool
- [ ] Query: "What is Section 420 IPC?"
- [ ] Verify section citations in response
- [ ] Check structured formatting

### F8: Document Drafter
- [ ] Select case
- [ ] Choose template (Legal Notice, FIR, etc.)
- [ ] Verify case data auto-populated
- [ ] Review Gemini-generated content
- [ ] Test all 5 templates

### F9: Section Suggester
- [ ] Describe incident in plain language
- [ ] Example: "Someone stole my laptop from office"
- [ ] Verify JSON response with sections
- [ ] Check bailable/cognizable status
- [ ] Review recommended actions

### F10: Risk Scoring
- [ ] Click "Calculate Risk" on case
- [ ] Verify score components breakdown
- [ ] Add/remove deadlines and recalculate
- [ ] Upload documents and check score change
- [ ] Test batch calculation for all cases

---

## 🌐 Production Deployment (Render/Heroku)

### Option 1: Render (Recommended)

1. **Create Web Service**
   - Repository: Link GitHub repo
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.run:app`

2. **Environment Variables**
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-strong-key>
   GEMINI_API_KEY=<your-api-key>
   DATABASE_URL=<postgresql-url>
   ```

3. **Add PostgreSQL Database**
   - Render Dashboard > New > PostgreSQL
   - Copy connection URL to `DATABASE_URL`

4. **Deploy**
   - Render auto-deploys on git push

### Option 2: Heroku

```bash
# Install Heroku CLI
heroku login

# Create app
heroku create legalmind-ai

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set GEMINI_API_KEY=your-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Initialize database
heroku run python
>>> from app import create_app
>>> from app.models import db
>>> app = create_app('production')
>>> with app.app_context():
...     db.create_all()
```

### Production Requirements

Create `Procfile` in root:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT --chdir backend run:app
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

---

## 📊 Database Migrations (Production)

For schema changes, use Flask-Migrate:

```bash
pip install Flask-Migrate

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Add new column"

# Apply migration
flask db upgrade
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   - Add to `.gitignore`
   - Use environment variables in production

2. **Strong SECRET_KEY**
   ```python
   import secrets
   secrets.token_hex(32)
   ```

3. **HTTPS Only (Production)**
   ```python
   SESSION_COOKIE_SECURE = True
   SESSION_COOKIE_HTTPONLY = True
   ```

4. **Rate Limiting**
   ```bash
   pip install Flask-Limiter
   ```

5. **CORS Configuration**
   - Restrict allowed origins in production

---

## 📈 Monitoring & Logging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Track Metrics
- Gemini API usage (token count)
- FAISS index size
- Database query performance
- Case/deadline creation rates

---

## 🐛 Troubleshooting

### Issue: FAISS not found
```bash
pip install faiss-cpu
```

### Issue: PyMuPDF import error
```bash
pip install --upgrade PyMuPDF
```

### Issue: Gemini API errors
- Check API key is valid
- Verify internet connection
- Check rate limits (60 requests/min for free tier)

### Issue: Database locked (SQLite)
- Switch to PostgreSQL for production
- SQLite doesn't support concurrent writes

---

## 📞 Support

- **Documentation**: See `FEATURES.md` for detailed feature specs
- **Tech Stack**: See `docs/TECH_STACK.md`
- **Issues**: Open GitHub issue

**Production-Ready Deployment Complete! 🎉**
