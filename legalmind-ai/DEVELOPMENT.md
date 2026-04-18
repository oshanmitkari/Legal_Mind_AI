# LegalMind AI - Development Guide

## Quick Start

### 1. Prerequisites
```bash
Python 3.9+
pip
Git
VS Code (optional)
```

### 2. Clone & Setup
```bash
git clone https://github.com/avaleajay170/legalmind-ai.git
cd legalmind-ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

### 4. Run Application
```bash
python run.py
# Visit http://localhost:5000
```

---

## Feature Development Checklist

### ✅ Phase 1: Authentication (F1, F2)
- [x] Database models (User, Advocate verification badge)
- [x] Registration route with three-tier verification
- [x] Login route with Flask-Login
- [x] HTML templates (register, login)
- [ ] Test with advocate registry data

### ✅ Phase 2: Case Management (F3, F4, F5)
- [x] Case model and CRUD routes
- [x] Deadline model with color-coding
- [x] Document upload with PyMuPDF
- [x] HTML templates (dashboard, detail, calendar)
- [ ] FAISS vector embedding
- [ ] Test file uploads

### ✅ Phase 3: AI Features (F6, F7, F8, F9)
- [x] AI assistant routes with Gemini integration
- [x] Legal research RAG
- [x] Document drafter templates
- [x] Section suggester
- [ ] Test Gemini API calls
- [ ] Fine-tune prompts

### ✅ Phase 4: Risk Scoring (F10)
- [x] RiskCalculator utility
- [x] Risk score API endpoint
- [ ] Test scoring algorithms

### ⬜ Phase 5: Frontend UI
- [x] Basic templates
- [ ] Complete all template pages
- [ ] Chat UI refinement
- [ ] Mobile responsiveness

### ⬜ Phase 6: Deployment
- [ ] Push to GitHub
- [ ] Deploy to Render
- [ ] Test live URL

---

## Testing Guide

### Test F1 (Advocate Verification)
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_number": "MH/1234/2020",
    "name": "Raj Kumar",
    "state": "Maharashtra",
    "email": "raj@example.com",
    "password": "test123"
  }'
```

Expected: `200 OK` with "verified": true

### Test F3 (Create Case)
```bash
curl -X POST http://localhost:5000/cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "CASE/2024/001",
    "client_name": "John Doe",
    "case_type": "Criminal"
  }'
```

### Test F6 (AI Chat)
```bash
curl -X POST http://localhost:5000/ai/chat/1 \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the charges in this case?"}'
```

---

## File Structure

```
legalmind-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # App factory
│   │   ├── models.py             # Database models
│   │   ├── routes/
│   │   │   ├── auth.py           # F1, F2
│   │   │   ├── cases.py          # F3
│   │   │   ├── deadlines.py      # F4
│   │   │   ├── documents.py      # F5
│   │   │   └── ai_assistant.py   # F6-F9
│   │   ├── services/             # Business logic (to be added)
│   │   ├── utils/
│   │   │   ├── advocate_verifier.py  # F1 verification
│   │   │   └── risk_calculator.py    # F10
│   │   ├── templates/
│   │   │   ├── auth/
│   │   │   ├── cases/
│   │   │   └── deadlines/
│   │   └── static/
│   │       └── css/
│   ├── data/
│   │   ├── advocate_registry.json
│   │   └── law_documents/        # Indian law PDFs (to be added)
│   ├── config.py
│   ├── run.py
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── TECH_STACK.md
│   ├── DEPLOYMENT_RENDER.md
│   └── API_SPEC.md               # (to be added)
└── README.md
```

---

## Next Steps

1. **Add FAISS vector store** (F5, F7):
   - Load Indian law PDFs
   - Create embedding index
   - Test retrieval

2. **Refine Gemini prompts** (F6-F9):
   - Test with real cases
   - Improve section suggestions
   - Fine-tune document drafts

3. **Complete Frontend**:
   - Add remaining templates
   - Improve mobile UI
   - Add form validation

4. **Test & Deploy**:
   - Run integration tests
   - Push to GitHub
   - Deploy to Render
   - Get feedback from judges

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 5000 in use | Change to `PORT=5001 python run.py` |
| GEMINI_API_KEY error | Add to `.env` and restart |
| `ImportError: No module named 'app'` | Ensure you're in `backend/` folder |

---

## Contacts & Resources

- **Gemini API Docs:** https://ai.google.dev/
- **Flask Docs:** https://flask.palletsprojects.com/
- **FAISS:** https://github.com/facebookresearch/faiss
- **Render Docs:** https://render.com/docs
- **LangChain:** https://python.langchain.com/

---

**Last Updated:** April 18, 2026  
**Status:** Initial Setup Complete ✅
