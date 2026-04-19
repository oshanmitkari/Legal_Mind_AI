"""F4: Deadline Tracker - Calendar and alert management"""
from flask import Blueprint, request, jsonify, render_template
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Deadline, Case
from datetime import datetime, timedelta
import calendar
import logging

# F4: Import deadline notifier for email alerts
from app.services.deadline_notifier import get_deadline_notifier

logger = logging.getLogger(__name__)
deadlines_bp = Blueprint('deadlines', __name__)

@deadlines_bp.route('/', methods=['GET'])
@deadlines_bp.route('/calendar', methods=['GET'])
@login_required
def view_calendar():
    """F4: Deadline Tracker - Calendar view"""
    current_user = get_current_user()
    month = request.args.get('month', datetime.utcnow().month, type=int)
    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = min(max(month, 1), 12)

    if current_user.is_admin:
        deadlines = Deadline.query.filter_by(is_completed=False).all()
    else:
        # Get deadline for user's cases only
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        case_ids = [c.id for c in user_cases]
        deadlines = Deadline.query.filter(
            Deadline.case_id.in_(case_ids),
            Deadline.is_completed == False
        ).all()
    
    cal = calendar.Calendar(firstweekday=6)
    month_weeks = cal.monthdatescalendar(year, month)
    deadlines_by_day = {}
    for deadline in deadlines:
        key = deadline.due_date.date().isoformat()
        deadlines_by_day.setdefault(key, []).append(deadline)

    previous_month = (month - 1) or 12
    previous_year = year - 1 if month == 1 else year
    next_month = (month % 12) + 1
    next_year = year + 1 if month == 12 else year
    overdue_count = sum(1 for deadline in deadlines if deadline.due_date < datetime.utcnow())

    return render_template(
        'deadlines/calendar.html',
        deadlines=deadlines,
        current_user=current_user,
        month=month,
        year=year,
        month_name=calendar.month_name[month],
        month_weeks=month_weeks,
        deadlines_by_day=deadlines_by_day,
        previous_month=previous_month,
        previous_year=previous_year,
        next_month=next_month,
        next_year=next_year,
        today=datetime.utcnow().date(),
        overdue_count=overdue_count,
    )

@deadlines_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    """F4: Get 7-day alert list with color coding"""
    current_user = get_current_user()
    if current_user.is_admin:
        deadlines = Deadline.query.filter_by(is_completed=False).all()
    else:
        user_cases = Case.query.filter_by(user_id=current_user.id).all()
        case_ids = [c.id for c in user_cases]
        deadlines = Deadline.query.filter(
            Deadline.case_id.in_(case_ids),
            Deadline.is_completed == False
        ).all()
    
    # Filter to next 7 days + overdue
    now = datetime.utcnow()
    week_from_now = now + timedelta(days=7)
    
    alerts = []
    for deadline in deadlines:
        if deadline.due_date <= week_from_now:
            alerts.append({
                'id': deadline.id,
                'title': deadline.title,
                'case_number': deadline.case.case_number,
                'due_date': deadline.due_date.isoformat(),
                'deadline_type': deadline.deadline_type,
                'color': deadline.status_color(),
                'priority': deadline.priority,
                'days_until': (deadline.due_date - now).days
            })
    
    # Sort by due date
    alerts.sort(key=lambda x: x['due_date'])
    
    return jsonify(alerts), 200

@deadlines_bp.route('/', methods=['POST'])
@login_required
def create_deadline():
    """Add deadline to case"""
    current_user = get_current_user()
    data = request.get_json()
    case_id = data.get('case_id')
    
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        due_date = datetime.fromisoformat(data.get('due_date'))
    except:
        return jsonify({'error': 'Invalid date format'}), 400
    
    deadline = Deadline(
        case_id=case_id,
        title=data.get('title', ''),
        due_date=due_date,
        deadline_type=data.get('deadline_type', 'Court Date'),
        priority=data.get('priority', 'medium')
    )

    db.session.add(deadline)
    db.session.commit()

    # F4: Check if deadline is within 2 days and send immediate notification
    notifier = get_deadline_notifier()
    notification_sent = notifier.check_single_deadline_on_create_or_update(deadline)

    response_data = {
        'id': deadline.id,
        'message': 'Deadline created',
        'color': deadline.status_color(),
        'notification_sent': notification_sent
    }

    if notification_sent:
        logger.info(f"Email notification sent for new deadline {deadline.id}")

    return jsonify(response_data), 201

@deadlines_bp.route('/<int:deadline_id>', methods=['PUT'])
@login_required
def update_deadline(deadline_id):
    """Update deadline - triggers risk score recalculation if completed"""
    current_user = get_current_user()
    deadline = Deadline.query.get_or_404(deadline_id)
    case = deadline.case

    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Track if due_date was updated
    due_date_changed = False
    if 'due_date' in data:
        try:
            new_due_date = datetime.fromisoformat(data['due_date'])
            if deadline.due_date != new_due_date:
                due_date_changed = True
                deadline.due_date = new_due_date
        except:
            return jsonify({'error': 'Invalid date format'}), 400

    # F4 Integration: Track if deadline completion status changed
    completion_changed = False
    if 'is_completed' in data:
        if deadline.is_completed != data['is_completed']:
            completion_changed = True
        deadline.is_completed = data['is_completed']

    deadline.title = data.get('title', deadline.title)
    deadline.priority = data.get('priority', deadline.priority)

    db.session.commit()

    # F4: Trigger risk score recalculation if deadline was completed
    if completion_changed:
        from app.utils.risk_calculator import RiskCalculator
        deadline_score = RiskCalculator.calculate_deadline_score(case)
        case.risk_score = deadline_score  # Simplified - full calc would use all components
        db.session.commit()

    # F4: Check if updated deadline is now within 2 days and send notification
    notification_sent = False
    if due_date_changed and not deadline.is_completed:
        notifier = get_deadline_notifier()
        notification_sent = notifier.check_single_deadline_on_create_or_update(deadline)
        if notification_sent:
            logger.info(f"Email notification sent for updated deadline {deadline.id}")

    return jsonify({
        'message': 'Deadline updated',
        'risk_recalculated': completion_changed,
        'notification_sent': notification_sent
    }), 200

@deadlines_bp.route('/<int:deadline_id>', methods=['DELETE'])
@login_required
def delete_deadline(deadline_id):
    """Delete deadline"""
    current_user = get_current_user()
    deadline = Deadline.query.get_or_404(deadline_id)
    case = deadline.case
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(deadline)
    db.session.commit()
    
    return jsonify({'message': 'Deadline deleted'}), 200

