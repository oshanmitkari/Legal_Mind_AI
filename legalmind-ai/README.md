# LegalMind AI 🧠⚖️

**Production-Grade AI Legal Assistant for Indian Lawyers**

An AI-powered legal workflow system featuring advocate verification, AI case assistance, risk scoring, deadline tracking, and automated document drafting. All 10 core features fully implemented and tested.

[![Flask](https://img.shields.io/badge/Flask-2.3-blue)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## ✨ Features (All Implemented & Production-Ready)

### 🔐 Authentication & Access Control
- **F1. Multi-Tier Advocate Verification** ✅
  - Regex validation (`MH/1234/2020` format)
  - Bar Council registry cross-reference
  - Duplicate prevention with "Verified" badge

- **F2. Secure Session Management with RLS** ✅
  - Flask session-based authentication
  - Row-Level Security on all queries
  - `@login_required` decorator protection

### 📁 Case Management System
- **F3. Case Command Center** ✅
  - Professional Bootstrap 5 dashboard
  - Case cards with client info, status, risk gauge
  - Real-time deadline countdown
  - Full CRUD with pagination

- **F4. Color-Coded Deadline Tracker** ✅
  - 🔴 Red (Overdue) / 🟡 Amber (≤72hrs) / 🟢 Green (4+ days)
  - Full calendar view with month navigation
  - 7-day alert list
  - Deadline CRUD per case

- **F5. RAG-Ready PDF Pipeline** ✅
  - PyMuPDF text extraction
  - LangChain recursive text splitting
  - FAISS vector indexing (per-case isolation)
  - Semantic search for RAG context

### 🤖 AI-Powered Features (Gemini 1.5 Flash)
- **F6. Contextual AI Case Assistant** ✅
  - RAG-enhanced chat with case metadata
  - Document snippet injection
  - Chat history persistence
  - Source attribution

- **F7. Legal Research Engine** ✅
  - Structured prompts for Indian law (IPC, CrPC, IT Act)
  - Section citation extraction
  - Landmark judgment references
  - Practical guidance output

- **F8. Automated Document Drafter** ✅
  - **5 Templates**: Legal Notice, FIR, Affidavit, Bail Application, Contract
  - Auto-population with case data
  - Gemini-generated legal body
  - Edit-before-export workflow

- **F9. Plain-Language Section Suggester** ✅
  - Incident description → IPC/CrPC sections
  - Structured JSON output
  - Bailable/cognizable status
  - Recommended legal actions

### 📊 Analytics & Risk Assessment
- **F10. Risk Scoring Engine (0-100)** ✅
  - **35%** Deadline proximity
  - **25%** Document completeness
  - **25%** Document strength (content volume)
  - **15%** AI sentiment/strength analysis
  - Visual gauge with color gradient
  - Batch recalculation API

## 🚀 Quick Start

```bash
# 1. Clone repository
cd legalmind-ai/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Add your GEMINI_API_KEY

# 5. Run application
python run.py
```

Access at: **http://localhost:5000**

**Test Credentials:**
- Enrollment: `MH/1234/2020`
- Name: `Raj Kumar`
- State: `Maharashtra`
- Password: `<any password you choose>`

📖 **Full deployment guide:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
📋 **Feature specifications:** See [FEATURES.md](FEATURES.md)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask 2.3 | Web framework with Blueprints |
| **Database** | SQLAlchemy + SQLite | ORM with cascade delete, upgradeable to PostgreSQL |
| **AI/LLM** | Google Gemini 1.5 Flash | Legal text generation & analysis |
| **Vector Store** | FAISS (CPU) | Local document embeddings |
| **Orchestration** | LangChain | Text chunking & RAG pipeline |
| **Document Processing** | PyMuPDF (fitz) | PDF text extraction |
| **Frontend** | Bootstrap 5.3 | Dark theme with responsive grid |
| **Icons** | Bootstrap Icons | Professional icon set |
| **Session** | Flask Sessions | Secure cookie-based auth |

## 📂 Project Structure

```
legalmind-ai/
├── backend/
│   ├── app/
│   │   ├── models.py                    # 7 database models (User, Case, Deadline, etc.)
│   │   ├── routes/
│   │   │   ├── auth.py                  # F1-F2: Registration, login, profile
│   │   │   ├── cases.py                 # F3: CRUD, dashboard
│   │   │   ├── deadlines.py             # F4: Calendar, alerts
│   │   │   ├── documents.py             # F5: PDF upload, FAISS indexing
│   │   │   ├── ai_assistant.py          # F6-F9: Chat, research, drafter, suggester
│   │   │   └── risk.py                  # F10: Risk calculation API
│   │   ├── services/
│   │   │   ├── auth_service.py          # Multi-tier verification logic
│   │   │   ├── document_service.py      # PyMuPDF extraction + FAISS
│   │   │   └── document_search_service.py  # RAG retrieval
│   │   ├── utils/
│   │   │   ├── advocate_verifier.py     # Regex + registry validation
│   │   │   ├── auth_utils.py            # @login_required, RLS
│   │   │   ├── risk_calculator.py       # 4-component risk algorithm
│   │   │   └── vector_store.py          # FAISS wrapper (chunking, embeddings)
│   │   ├── templates/
│   │   │   ├── base.html                # Bootstrap 5 base layout
│   │   │   ├── auth/                    # Login, register, profile
│   │   │   ├── cases/                   # Dashboard, detail view
│   │   │   └── deadlines/               # Calendar view
│   │   └── static/css/                  # Custom styles
│   ├── data/
│   │   ├── advocate_registry.json       # Prototype Bar Council DB
│   │   └── faiss_index/                 # FAISS vectors + metadata JSON
│   ├── uploads/                         # PDF storage (case_<id>/)
│   ├── config.py                        # Flask config classes
│   ├── run.py                           # Entry point
│   ├── requirements.txt                 # Python dependencies
│   └── .env.example                     # Environment template
├── FEATURES.md                          # Detailed feature specifications
├── DEPLOYMENT_GUIDE.md                  # Production deployment steps
├── DEVELOPMENT.md                       # Developer notes
└── README.md                            # This file
```

---

## 🔌 API Endpoints

### Authentication
```http
POST /register                 # Register with Bar Council verification
POST /register/verify          # Live verification check
POST /login                    # Authenticate advocate
GET  /logout                   # Logout
GET  /profile                  # Get current user profile
```

### Case Management (F3)
```http
GET  /cases/dashboard          # HTML dashboard
GET  /cases/                   # JSON list of cases
POST /cases/                   # Create new case
GET  /cases/<id>               # Case details (HTML/JSON)
PUT  /cases/<id>               # Update case
DELETE /cases/<id>             # Delete case
GET  /cases/deadlines          # Cases with deadline status
```

### Deadlines (F4)
```http
GET  /deadlines/calendar       # Calendar view (HTML)
GET  /deadlines/alerts         # 7-day alert list (JSON)
POST /deadlines/               # Create deadline
PUT  /deadlines/<id>           # Update/complete deadline
DELETE /deadlines/<id>         # Delete deadline
```

### Documents (F5)
```http
POST /documents/<case_id>/upload  # Upload PDF (triggers FAISS indexing)
GET  /documents/<case_id>         # List case documents
DELETE /documents/<doc_id>        # Delete document + vectors
```

### AI Features (F6-F9)
```http
# F6: AI Case Assistant
POST /ai/chat/<case_id>           # Send message (RAG-enhanced)
GET  /ai/chat/<case_id>/history   # Get conversation

# F7: Legal Research
POST /ai/research                 # Query Indian legal codes
Body: {"query": "What is Section 420 IPC?"}

# F8: Document Drafter
POST /ai/draft                    # Generate legal document
Body: {"case_id": 1, "template_type": "bail_application"}

# F9: Section Suggester
POST /ai/suggest-sections         # Map incident to sections
Body: {"incident": "Someone hacked my email"}
```

### Risk Scoring (F10)
```http
POST /risk/calculate/<case_id>    # Calculate risk score
POST /risk/batch-calculate         # Recalculate all cases
```

**Authentication:** All endpoints (except `/register`, `/login`) require `@login_required`
**Authorization:** Row-Level Security enforced on all case/deadline/document operations

## Setup Instructions

### Prerequisites
- Python 3.9+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/avaleajay170/legalmind-ai.git
cd legalmind-ai
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Gemini API key and other configs
```

5. Run the application:
```bash
python run.py
```

The app will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register with Bar Council enrollment number
- `POST /auth/login` - Login
- `GET /auth/logout` - Logout

### Case Management
- `GET /cases` - List all cases
- `POST /cases` - Create new case
- `GET /cases/<id>` - View case details
- `PUT /cases/<id>` - Update case
- `DELETE /cases/<id>` - Archive case

### Documents
- `POST /cases/<id>/upload` - Upload PDF
- `GET /cases/<id>/documents` - List case documents

### AI Features
- `POST /cases/<id>/chat` - AI assistant chat
- `POST /research` - Legal research query
- `POST /draft` - Generate legal document
- `POST /suggest-sections` - Get applicable sections

### Deadlines
- `GET /deadlines` - View all deadlines
- `POST /cases/<id>/deadline` - Add deadline

## Database Models

- **User** - Lawyers with verified badge
- **Case** - Client cases with status
- **Document** - Uploaded PDFs with vector embeddings
- **Deadline** - Court dates and compliance events
- **ChatMessage** - Conversation history
- **RiskScore** - Case risk assessments

## Contributing

1. Create feature branch: `git checkout -b feature/F-name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to GitHub: `git push origin feature/F-name`
4. Create Pull Request

## License

Proprietary - LegalMind AI

## Contact

For support, contact: team@legalmind-ai.com
