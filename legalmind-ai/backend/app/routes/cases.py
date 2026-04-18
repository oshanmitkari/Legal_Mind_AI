"""F3: Case Command Center - Case CRUD operations"""
from flask import Blueprint, request, jsonify, render_template
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Case, Deadline, Document, ChatMessage
from app.utils.risk_calculator import RiskCalculator
from datetime import datetime, timedelta

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """F3: Case Command Center - Display all cases with Bootstrap 5 UI"""
    current_user = get_current_user()
    page = request.args.get('page', 1, type=int)

    if current_user.is_admin:
        cases = Case.query.paginate(page=page, per_page=10)
    else:
        cases = Case.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=10)

    upcoming_deadlines = _get_user_deadline_count(current_user.id, current_user.is_admin)

    # Use Bootstrap 5 template
    return render_template(
        'cases/dashboard_bootstrap.html',
        cases=cases.items,
        pagination=cases,
        current_user=current_user,
        upcoming_deadlines=upcoming_deadlines,
    )

@cases_bp.route('/', methods=['GET'])
@login_required
def list_cases():
    """API: Get all cases (JSON)"""
    current_user = get_current_user()
    if current_user.is_admin:
        cases = Case.query.all()
    else:
        cases = Case.query.filter_by(user_id=current_user.id).all()
    
    return jsonify([{
        'id': c.id,
        'case_number': c.case_number,
        'client_name': c.client_name,
        'case_type': c.case_type,
        'status': c.status,
        'risk_score': c.risk_score,
        'created_at': c.created_at.isoformat(),
        'next_deadline': _get_next_deadline(c.id)
    } for c in cases]), 200

@cases_bp.route('/', methods=['POST'])
@login_required
def create_case():
    """F3: Create new case"""
    current_user = get_current_user()
    data = request.get_json()
    
    required_fields = ['case_number', 'client_name', 'case_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check duplicate case number
    if Case.query.filter_by(case_number=data['case_number']).first():
        return jsonify({'error': 'Case number already exists'}), 400
    
    # Parse deadline_date if provided
    deadline_date = None
    if 'deadline_date' in data and data['deadline_date']:
        try:
            deadline_date = datetime.fromisoformat(data['deadline_date'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid deadline_date format. Use ISO format.'}), 400
    
    case = Case(
        user_id=current_user.id,
        case_number=data['case_number'],
        client_name=data['client_name'],
        case_type=data['case_type'],
        description=data.get('description', ''),
        status=data.get('status', 'open'),
        deadline_date=deadline_date
    )
    
    db.session.add(case)
    db.session.commit()
    
    return jsonify({
        'id': case.id,
        'message': 'Case created successfully'
    }), 201

@cases_bp.route('/deadlines', methods=['GET'])
@login_required
def get_deadlines():
    """Get all cases with deadline status (red/amber/green)"""
    current_user = get_current_user()
    
    if current_user.is_admin:
        cases = Case.query.filter(Case.deadline_date != None).all()
    else:
        cases = Case.query.filter(
            Case.user_id == current_user.id,
            Case.deadline_date != None
        ).all()
    
    deadlines = []
    for case in cases:
        status_name, color = case.get_deadline_status()
        deadlines.append({
            'case_id': case.id,
            'case_number': case.case_number,
            'client_name': case.client_name,
            'deadline': case.deadline_date.isoformat() if case.deadline_date else None,
            'status': status_name,
            'color': color
        })
    
    # Sort by deadline date (nearest first)
    deadlines.sort(key=lambda x: x['deadline'] if x['deadline'] else '')
    
    return jsonify(deadlines), 200

@cases_bp.route('/<int:case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    """Get specific case details as HTML or JSON."""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization check - only owner can access
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if _prefers_html():
        documents = Document.query.filter_by(case_id=case_id).order_by(Document.uploaded_at.desc()).all()
        deadlines = Deadline.query.filter_by(case_id=case_id).order_by(Deadline.due_date).all()
        chat_messages = ChatMessage.query.filter_by(case_id=case_id).order_by(ChatMessage.created_at).all()
        return render_template(
            'cases/detail.html',
            case=case,
            current_user=current_user,
            documents=documents,
            deadlines=deadlines,
            chat_messages=chat_messages,
        )
    
    deadline_status, color = case.get_deadline_status() if case.deadline_date else ('safe', 'green')
    
    return jsonify({
        'id': case.id,
        'user_id': case.user_id,
        'client_name': case.client_name,
        'case_type': case.case_type,
        'description': case.description,
        'status': case.status.lower(),  # Return lowercase for consistency
        'risk_score': case.risk_score,
        'deadline_date': case.deadline_date.isoformat() if case.deadline_date else None,
        'deadline_status': deadline_status,
        'deadline_color': color,
        'created_at': case.created_at.isoformat(),
        'updated_at': case.updated_at.isoformat()
    }), 200

@cases_bp.route('/<int:case_id>', methods=['PUT'])
@login_required
def update_case(case_id):
    """F3: Update case"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization check
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    case.client_name = data.get('client_name', case.client_name)
    case.case_type = data.get('case_type', case.case_type)
    case.description = data.get('description', case.description)
    case.status = data.get('status', case.status)
    
    # Update deadline_date if provided
    if 'deadline_date' in data:
        if data['deadline_date']:
            try:
                case.deadline_date = datetime.fromisoformat(data['deadline_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return jsonify({'error': 'Invalid deadline_date format. Use ISO format.'}), 400
        else:
            case.deadline_date = None
    
    case.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Case updated successfully'}), 200

@cases_bp.route('/<int:case_id>', methods=['DELETE'])
@login_required
def delete_case(case_id):
    """Delete case - only owner can access"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization check - only owner can access
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(case)
    db.session.commit()
    
    return jsonify({'message': 'Case deleted successfully'}), 200

def _get_next_deadline(case_id):
    """Helper: Get nearest upcoming deadline"""
    deadline = Deadline.query.filter(
        Deadline.case_id == case_id,
        Deadline.is_completed == False
    ).order_by(Deadline.due_date).first()
    
    return deadline.due_date.isoformat() if deadline else None


def _get_user_deadline_count(user_id, is_admin):
    """Count incomplete deadlines due in the next seven days."""
    now = datetime.utcnow()
    soon = now.replace(microsecond=0) if now.microsecond else now
    week_from_now = soon + timedelta(days=7)

    query = Deadline.query.filter(
        Deadline.is_completed == False,
        Deadline.due_date <= week_from_now
    )
    if not is_admin:
        query = query.join(Case).filter(Case.user_id == user_id)

    return query.count()


def _prefers_html():
    """Return True when the request is from a browser expecting HTML."""
    return (
        request.args.get('format') != 'json'
        and request.accept_mimetypes.best == 'text/html'
    )
