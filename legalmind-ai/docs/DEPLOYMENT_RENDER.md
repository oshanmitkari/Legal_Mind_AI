# Deployment Guide — Render

## Step-by-Step Deployment to Render

### Prerequisites
- GitHub account with legalmind-ai repository
- Render account (free: https://render.com)
- GEMINI_API_KEY from Google AI Studio (https://aistudio.google.com/app/apikey)

---

## Step 1: Prepare GitHub Repository

1. Ensure code is pushed to main branch:
```bash
cd d:\legalmind-ai
git add .
git commit -m "Initial LegalMind AI setup"
git push origin main
```

2. Verify `.gitignore` exists (blocks `venv/`, `.env`, `*.db`)

---

## Step 2: Create Render Web Service

1. Go to **https://render.com**
2. Sign up or login with GitHub
3. Click **New +** → **Web Service**
4. Select your `legalmind-ai` repository
5. Configure:

| Setting | Value |
|---------|-------|
| **Name** | legalmind-ai |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `cd backend && python run.py` |
| **Instance Type** | Free |

6. Click **Create Web Service**

---

## Step 3: Add Environment Variables

In Render dashboard, go to **Environment**:

```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///legalmind.db
```

**How to generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Step 4: Configure Database (Optional)

Render Free tier doesn't persist files. To keep SQLite data:

### Option A: Use Render Disk (Recommended for Hackathon)
1. Go to **Settings** → **Disks**
2. Add disk: Mount path `/data`
3. Update `config.py`:
```python
import os
db_path = os.environ.get('DATABASE_PATH', '/data/legalmind.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
```

### Option B: Migrate to PostgreSQL (Post-Hackathon)
```python
# Update DATABASE_URL environment variable
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@host/legalmind'
```

---

## Step 5: Verify Deployment

1. Render auto-deploys on git push
2. Visit https://legalmind-ai.onrender.com
3. Check logs in Render dashboard if issues occur

---

## Step 6: Test Features

### Test F1 (Advocate Verification)
```
POST /auth/register
{
  "enrollment_number": "MH/1234/2020",
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "password": "secure_password",
  "state": "Maharashtra"
}
```

### Test F2 (Login)
```
POST /auth/login
{
  "email": "raj@example.com",
  "password": "secure_password"
}
```

### Test F3 (Create Case)
```
POST /cases
{
  "case_number": "CASE/2024/001",
  "client_name": "John Doe",
  "case_type": "Criminal"
}
```

---

## Monitoring & Logs

**View live logs:**
```bash
# In Render dashboard → Logs tab
# Or use Render CLI:
render logs legalmind-ai
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure `requirements.txt` has all imports |
| Port error | Change `PORT` env var; Render uses 5000 by default |
| Database locked | SQLite is light; use Render Disk or upgrade to PostgreSQL |
| GEMINI_API_KEY missing | Add to Environment in Render dashboard |

---

## Scaling to Production

**When ready to scale beyond hackathon:**

1. **Database:** Migrate from SQLite to PostgreSQL
   ```bash
   pip install psycopg2-binary
   # Update DATABASE_URL in Render
   ```

2. **File Storage:** Move uploads to AWS S3
   ```python
   import boto3
   s3 = boto3.client('s3')
   ```

3. **Caching:** Add Redis for session management
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
   ```

4. **Monitoring:** Integrate Sentry for error tracking
   ```bash
   pip install sentry-sdk
   sentry_sdk.init(dsn="your-sentry-dsn")
   ```

---

## Rollback Deployment

If deployment fails:

1. Render keeps previous version running
2. Fix code locally, push to main
3. Render auto-redeploys in 2-3 minutes

---

**Need help?** Check Render docs: https://render.com/docs
