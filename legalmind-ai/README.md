# LegalMind AI

An AI-powered legal workflow assistant designed to streamline and automate the end-to-end case lifecycle for legal professionals.

## Features

### Category 1: Authentication & Access
- **F1. Advocate Verification** - Bar Council enrollment validation with registry cross-check
- **F2. Lawyer-Only Login** - Session-based authentication with role-based access control

### Category 2: Case Management
- **F3. Case Command Center** - Centralized case dashboard with CRUD operations
- **F4. Deadline Tracker** - Calendar view with color-coded deadline alerts
- **F5. PDF Upload & Analysis** - Document ingestion with vector embedding (FAISS)

### Category 3: AI Features
- **F6. AI Case Assistant** - Context-aware Gemini chat for case-specific queries
- **F7. Legal Research (RAG)** - Retrieval-augmented generation over Indian legal codes
- **F8. Document Drafter** - Auto-fill templates for legal documents
- **F9. Section Suggester** - Incident-to-IPC/CrPC section mapping

### Category 4: Analytics
- **F10. Risk Scoring Engine** - Dynamic risk assessment gauge per case

## Tech Stack

- **Backend**: Flask 2.3
- **Database**: SQLAlchemy + SQLite (upgradeable to PostgreSQL)
- **AI/LLM**: Google Gemini API
- **Vector Store**: FAISS
- **Document Processing**: PyMuPDF + LangChain
- **Frontend**: Flask Templates + Bootstrap + Vanilla JS

## Project Structure

```
legalmind-ai/
├── backend/
│   ├── app/
│   │   ├── models.py           # Database models
│   │   ├── routes/             # Feature routes
│   │   ├── services/           # Business logic
│   │   ├── utils/              # Helper functions
│   │   ├── templates/          # HTML templates
│   │   ├── static/             # CSS/JS
│   │   └── __init__.py         # App factory
│   ├── data/                   # Data files (registry, law PDFs)
│   ├── config.py               # Configuration
│   ├── run.py                  # Entry point
│   └── requirements.txt        # Dependencies
├── docs/                       # Documentation
└── README.md
```

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
