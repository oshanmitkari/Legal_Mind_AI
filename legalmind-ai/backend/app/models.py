from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class StateBarCouncilRecord(db.Model):
    """Prototype State Bar Council registry used for advocate verification demos."""
    __tablename__ = 'state_bar_council_records'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=False)
    advocate_name = db.Column(db.String(150), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    council_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StateBarCouncilRecord {self.enrollment_number}>'

class User(db.Model):
    """F1 & F2: Lawyer user with advocate verification"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=False)  # MH/1234/2020
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)  # F4: Email for deadline notifications
    password_hash = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Advocate verification badge
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cases = db.relationship('Case', backref='lawyer', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    deadline_notifications = db.relationship('DeadlineNotification', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.name}>'

class Case(db.Model):
    """F3: Case Command Center - Core case entity"""
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    case_number = db.Column(db.String(100), unique=True, nullable=False)
    client_name = db.Column(db.String(150), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)  # Criminal, Civil, etc.
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')  # open, closed
    risk_score = db.Column(db.Float, default=0.0)  # F10: Risk Scoring Engine
    deadline_date = db.Column(db.DateTime, nullable=True)  # Case deadline for deadline tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='case', lazy=True, cascade='all, delete-orphan')
    deadlines = db.relationship('Deadline', backref='case', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='case', lazy=True, cascade='all, delete-orphan')
    
    def get_deadline_status(self):
        """Calculate deadline status as 'overdue', 'due_soon', or 'safe'.
        Returns tuple of (status_name, color_code)"""
        if not self.deadline_date:
            return 'safe', 'green'
        
        from datetime import timedelta
        now = datetime.utcnow()
        days_until = (self.deadline_date - now).days
        
        if days_until < 0:
            return 'overdue', 'red'
        elif days_until < 3:
            return 'due_soon', 'amber'
        else:
            return 'safe', 'green'
    
    def __repr__(self):
        return f'<Case {self.case_number}>'

class Document(db.Model):
    """F5: PDF Upload & Analysis - Uploaded documents with FAISS embeddings"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    document_type = db.Column(db.String(100))  # FIR, Contract, Judgment, etc.
    text_content = db.Column(db.Text)  # Extracted via PyMuPDF
    faiss_index_id = db.Column(db.String(255))  # Reference to FAISS vector store
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class Deadline(db.Model):
    """F4: Deadline Tracker - Court dates and compliance events"""
    __tablename__ = 'deadlines'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    deadline_type = db.Column(db.String(50))  # Court Date, Filing Deadline, etc.
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    notifications = db.relationship('DeadlineNotification', backref='deadline', lazy=True, cascade='all, delete-orphan')
    
    def status_color(self):
        """Return color code: red (overdue), amber (3 days), green (safe)"""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        days_until = (self.due_date - now).days
        
        if days_until < 0:
            return 'red'  # Overdue
        elif days_until <= 3:
            return 'amber'  # Due within 3 days
        else:
            return 'green'  # Safe
    
    def __repr__(self):
        return f'<Deadline {self.title}>'

class ChatMessage(db.Model):
    """F6: AI Case Assistant - Chat conversation history"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_type = db.Column(db.String(20))  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'

class RiskScore(db.Model):
    """F10: Risk Scoring Engine - Dynamic risk assessment per case"""
    __tablename__ = 'risk_scores'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, unique=True)
    deadline_score = db.Column(db.Float, default=0.0)  # 0-100 based on proximity
    document_completeness = db.Column(db.Float, default=0.0)  # 0-100 based on uploads
    document_strength = db.Column(db.Float, default=0.0)  # 0-100 Gemini analysis
    case_analysis_score = db.Column(db.Float, default=0.0)  # 0-100 from AI
    overall_score = db.Column(db.Float, default=0.0)  # Weighted average
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<RiskScore case_id={self.case_id} score={self.overall_score}>'


class HistoricalCase(db.Model):
    """F11: Legal Precedent & Case Similarity Engine - Historical case database"""
    __tablename__ = 'historical_cases'

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), nullable=False, unique=True)
    case_type = db.Column(db.String(50), nullable=False)  # Criminal, Civil, Corporate, Family, Labor
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)  # Detailed case description for similarity matching
    outcome = db.Column(db.Text, nullable=False)  # Final judgment/outcome
    key_sections = db.Column(db.String(500))  # Applicable law sections
    court = db.Column(db.String(200))  # Court name
    judgment_date = db.Column(db.DateTime, nullable=False)
    relevance_score = db.Column(db.Float, default=0.0)  # Computed similarity score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'case_number': self.case_number,
            'case_type': self.case_type,
            'title': self.title,
            'description': self.description,
            'outcome': self.outcome,
            'key_sections': self.key_sections,
            'court': self.court,
            'judgment_date': self.judgment_date.strftime('%Y-%m-%d') if self.judgment_date else None,
            'relevance_score': round(self.relevance_score, 2)
        }

    def __repr__(self):
        return f'<HistoricalCase {self.case_number}>'


class DeadlineNotification(db.Model):
    """
    F4: Deadline Notification Tracker
    Records when deadline alert emails are sent to advocates
    """
    __tablename__ = 'deadline_notifications'

    id = db.Column(db.Integer, primary_key=True)
    deadline_id = db.Column(db.Integer, db.ForeignKey('deadlines.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # e.g., '2_day_alert', '1_day_alert', 'overdue'
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    email_sent = db.Column(db.Boolean, default=False)
    email_address = db.Column(db.String(150), nullable=True)
    error_message = db.Column(db.Text, nullable=True)  # Store any error that occurred

    def __repr__(self):
        return f'<DeadlineNotification {self.notification_type} for Deadline {self.deadline_id}>'
