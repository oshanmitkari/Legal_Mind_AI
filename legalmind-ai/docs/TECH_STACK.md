# Tech Stack Architecture — LegalMind AI

## Overview
A lightweight, AI-first legal workflow platform optimized for hackathon & solo developer deployment with minimal ops overhead.

---

## Layer-by-Layer Tech Stack

### **1. Frontend Layer**
**Technology:** HTML 5 + Bootstrap 5 + Vanilla JavaScript

**Why This Stack:**
- ✅ **Zero Build Setup** — No Node.js, webpack, or complicated tooling
- ✅ **Browser Compatibility** — Works on judges' laptops without installation
- ✅ **Fast to Build** — HTML templates + CSS grid for rapid UI development
- ✅ **Live Reload** — Flask development server auto-reloads on template changes
- ❌ **Not React/Vue** — Overkill for a legal app; adds deployment complexity

**Key Features:**
- Modal dialogs for case creation/editing
- Real-time deadline color coding (CSS)
- Collapsible chat UI for AI assistant
- Responsive mobile-friendly design
- Calendar widget for deadline tracking

---

### **2. Backend Layer**
**Technology:** Flask 2.3 (Python)

**Why Python + Flask:**
- ✅ **Your Team's Expertise** — Assumes Python-fluent developers
- ✅ **AI Integration Ready** — Google Gemini Python SDK works seamlessly
- ✅ **Lightweight** — ~50KB core, no heavy dependencies initially
- ✅ **Session Management** — Flask-Login perfectly handles lawyer auth
- ✅ **Quick to Deploy** — Single `run.py` entry point
- ❌ **Not FastAPI** — Overkill; session/auth less intuitive
- ❌ **Not Django** — Too heavyweight for hackathon timeline

**Advantages for LegalMind:**
- Decorator-based route protection (`@login_required`)
- Blueprint architecture matches feature branches (auth.py, cases.py, ai_assistant.py, etc.)
- Flask-SQLAlchemy ORM keeps database code readable

---

### **3. LLM / AI Layer**
**Technology:** Google Gemini 1.5 Flash API

**Why Gemini (Not GPT-4 / Claude):**
- ✅ **Free Tier:** 60 requests/minute = sufficient for 10 lawyers
- ✅ **Fast Responses:** Flash model gives <2s latency
- ✅ **Indian Law Context:** Trained on India-specific legal documents
- ✅ **Built for Text + Multimodal:** Can process scanned FIRs as images (future)
- ✅ **Cost:** $0 for hackathon, $0.075/1M input tokens at scale
- ❌ **Not GPT-4:** $20/month for API; slower; overkill for legal research
- ❌ **Not Claude:** No free tier; requires credit card upfront

**Model Selection:**
- `gemini-pro` = fastest for chat/research
- Fallback to `gemini-pro-vision` for document OCR (future F5 enhancement)

---

### **4. Orchestration / RAG Layer**
**Technology:** LangChain 0.0.270

**Why LangChain (Not Direct API Calls):**
- ✅ **Prompt Templates** — Reusable templates for each feature (F6, F7, F8, F9)
- ✅ **Memory Management** — Handles chat context automatically
- ✅ **RAG Pipeline** — Bridges FAISS → Gemini seamlessly
- ✅ **Chains** — Composes multi-step workflows (upload → embed → retrieve → generate)
- ❌ **Not Manual Calls:** Would require 4x more boilerplate code

**LangChain Usage in LegalMind:**
```python
# F7: Legal Research RAG
retriever = faiss_retriever.as_retriever()
chain = RetrievalQA.from_chain_type(llm=gemini, retriever=retriever)
result = chain.run("What is the bail provision for NDPS cases?")
```

---

### **5. Vector Database / Embeddings**
**Technology:** FAISS (Facebook AI Similarity Search)

**Why FAISS (Not Pinecone / Weaviate):**
- ✅ **Zero Server Cost** — Runs locally, persists to disk as `.faiss` file
- ✅ **Instant Setup** — No API key, no authentication, no network latency
- ✅ **Perfect for Hackathon** — Embed Indian law PDFs once, query forever
- ✅ **Portable** — Serializes to a single file, check into Git
- ❌ **Not Pinecone:** $0.04/1K vectors × 10K Indian law chunks = $400/month at scale
- ❌ **Not Milvus:** Requires Docker/K8s; overkill

**Implementation Details:**
- Pre-load IPC (Indian Penal Code), CrPC, CPC, IBC, IT Act PDFs
- LangChain → PyMuPDF (extract text) → FAISS (embed + index)
- One-time setup: ~5 minutes

**FAISS Index Structure:**
```
legalmind-ai/backend/data/
├── indian_laws.faiss       # Vector index of all statute texts
├── metadata.json           # Maps index IDs to source documents
└── law_documents/          # Raw PDFs
    ├── ipc_sections.pdf
    ├── crpc_codes.pdf
    ├── cpc_rules.pdf
    ├── ibc_insolvency.pdf
    └── it_act.pdf
```

---

### **6. Document Processing Layer**
**Technology:** PyMuPDF (fitz)

**Why PyMuPDF (Not pdfplumber / pypdf2):**
- ✅ **Fastest:** C-based, handles 100+ pages in <1s
- ✅ **Scanned PDFs:** OCR-ready (future enhancement via Vision)
- ✅ **Extraction Accuracy:** >95% text recovery even for complex layouts
- ✅ **Minimal Deps:** Single compiled binary
- ❌ **Not pdfplumber:** Slower, text extraction less reliable
- ❌ **Not pypdf2:** Deprecated; lacks OCR

**F5 Implementation:**
```python
# User uploads case.pdf
pdf = fitz.open('case.pdf')
text = ""
for page in pdf:
    text += page.get_text()  # Extract as markdown

# Split & embed
chunks = text_splitter.split_text(text)  # LangChain
embeddings = embed_fn(chunks)  # OpenAI / Gemini embeddings
faiss_index.add(embeddings)  # Store in FAISS
```

---

### **7. Database Layer**
**Technology:** SQLite + SQLAlchemy ORM

**Why SQLite (Not PostgreSQL / MongoDB):**
- ✅ **Zero Setup:** Uses single `legalmind.db` file
- ✅ **Portable:** Checkin to Git, deploy anywhere
- ✅ **Perfect for Team:** No database credentials to manage
- ✅ **Sufficient Scale:** Handles 1000s of cases without issues
- ✅ **SQLAlchemy:** Easy migration to PostgreSQL later if needed
- ❌ **Not PostgreSQL:** Requires container; adds 30min setup time
- ❌ **Not MongoDB:** No ACID guarantees; risky for legal data

**Schema (as defined in models.py):**
- `users` — Lawyers with advocate verification badge
- `cases` — Client cases with CRUD
- `documents` — Uploaded PDFs with text + FAISS reference
- `deadlines` — Court dates with color-coded alerts
- `chat_messages` — Persistent conversation history per case
- `risk_scores` — Dynamic 0–100 risk gauge per case

---

### **8. File Upload Storage**
**Technology:** Local filesystem (backend/uploads/)

**Why Local (Not S3):**
- ✅ **Hackathon Timeline:** No AWS account setup needed
- ✅ **Free:** Unlimited file storage locally
- ✅ **Privacy:** PDFs stay on your machine (important for lawyer confidentiality)
- ✅ **Easy Testing:** Create test cases with local PDF fixtures

**For Production (Post-Hackathon):**
```python
# Migrate to S3:
import boto3
s3 = boto3.client('s3')
s3.upload_file('case.pdf', 'legalmind-bucket', 'cases/case_123/case.pdf')
```

---

### **9. Deployment Layer**
**Platform:** Render (render.com)

**Why Render (Not Heroku / Railway / Vercel):**
- ✅ **Free Tier:** 750 hours/month (enough for 1 continuous web service)
- ✅ **Git Integration:** Auto-deploy on git push to main
- ✅ **SQLite Support:** Can persist SQLite via Render Disk (optional upgrade)
- ✅ **Environment Secrets:** Built-in secret management for GEMINI_API_KEY
- ✅ **No Credit Card:** Truly free to start
- ❌ **Not Heroku:** Removed free tier; $7/month minimum now
- ❌ **Not Railway:** Less generous free tier

**Deployment Instructions:**
```bash
# 1. Push code to GitHub
git push origin main

# 2. Create Render account (render.com)
# 3. Connect GitHub repo
# 4. Create new Web Service
#    - Build: pip install -r backend/requirements.txt
#    - Start: cd backend && python run.py
#    - Port: 5000
# 5. Add environment variables (GEMINI_API_KEY, DATABASE_URL, SECRET_KEY)
# 6. Deploy! 🚀
```

**Live URL Example:**
```
https://legalmind-ai.onrender.com
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
│  HTML Templates (Jinja2) + Bootstrap 5 + Vanilla JS      │
│  (auth/register.html, cases/dashboard.html, etc.)        │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP REST API
                       ↓
┌─────────────────────────────────────────────────────────┐
│                    FLASK BACKEND                         │
│  Routes: auth.py, cases.py, documents.py, ai_assistant  │
│  Models: User, Case, Document, Deadline, ChatMessage    │
│  Utilities: AdvocateVerifier, RiskCalculator            │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   ┌────────┐  ┌────────┐  ┌──────────┐
   │ SQLite │  │ FAISS  │  │ LangChain│
   │Database│  │ Index  │  │ Gemini   │
   └────────┘  └────────┘  └──────────┘
                    │          │
                    └────┬─────┘
                         ↓
            ┌────────────────────────┐
            │  Google Gemini API     │
            │ (F6, F7, F8, F9: AI)   │
            └────────────────────────┘
```

---

## Implementation Timeline

| Phase | Features | Tech | Time |
|-------|----------|------|------|
| **Phase 1** | F1, F2 (Auth) | Flask-Login, Werkzeug | 2h |
| **Phase 2** | F3, F4, F5 (Cases, Deadlines, PDFs) | SQLAlchemy, PyMuPDF | 4h |
| **Phase 3** | F6, F7 (AI Chat + Research) | Gemini, LangChain | 3h |
| **Phase 4** | F8, F9 (Document Drafter + Section Suggester) | Gemini templates | 2h |
| **Phase 5** | F10 (Risk Scoring) | RiskCalculator utility | 1h |
| **Phase 6** | Deployment to Render | Git + Environment setup | 1h |
| **Total** | All 10 Features | Full Stack | **13 hours** |

---

## Why This Stack Wins Hackathons

✅ **Fast Build:** Minimal tooling setup, get to features in 30min  
✅ **AI-First:** Gemini integration is trivial (1 API call)  
✅ **Scalable Demo:** Works for 1 lawyer or 100 lawyers  
✅ **Deployable:** One git push = live for judges to test  
✅ **Cost Zero:** No infrastructure bills during hackathon  
✅ **Code Simple:** 95% Python, no TypeScript/build steps  
✅ **Legal-Ready:** Secure (HTTPS), session-based auth, encrypted configs  
✅ **Team-Friendly:** Parallel development (5 people, 5 features)

---

## Appendix: Dependency Sizes

```
Flask           0.5 MB
SQLAlchemy      2.1 MB
LangChain       15  MB
google-genai    8   MB
FAISS           45  MB
PyMuPDF         12  MB
─────────────────────
Total: ~83 MB (acceptable)
```

All dependencies are pure Python (no system libraries needed).

---

## Monitoring & Observability

**Logging:**
- Flask development logger (console output)
- Database query logs in `app.logger`

**Error Tracking (Optional):**
- Render built-in error notifications
- Add Sentry integration later if needed

---

**Last Updated:** April 18, 2026  
**Status:** Ready for Hackathon Build
