"""Authentication service layer for LegalMind AI."""
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, StateBarCouncilRecord
from app.utils.advocate_verifier import AdvocateVerifier

verifier = AdvocateVerifier()


SAMPLE_BAR_COUNCIL_RECORDS = [
    {
        'enrollment_number': 'MH/1234/2020',
        'advocate_name': 'Raj Kumar',
        'state': 'Maharashtra',
        'council_name': 'Maharashtra State Bar Council',
    },
    {
        'enrollment_number': 'MH/5678/2019',
        'advocate_name': 'Priya Singh',
        'state': 'Maharashtra',
        'council_name': 'Maharashtra State Bar Council',
    },
    {
        'enrollment_number': 'DL/1001/2021',
        'advocate_name': 'Amit Verma',
        'state': 'Delhi',
        'council_name': 'Bar Council of Delhi',
    },
    {
        'enrollment_number': 'KA/2234/2020',
        'advocate_name': 'Dr. Seema Gupta',
        'state': 'Karnataka',
        'council_name': 'Karnataka State Bar Council',
    },
    {
        'enrollment_number': 'TN/3456/2018',
        'advocate_name': 'V. Raman',
        'state': 'Tamil Nadu',
        'council_name': 'Bar Council of Tamil Nadu and Puducherry',
    },
    {
        'enrollment_number': 'GJ/7788/2022',
        'advocate_name': 'Nirali Shah',
        'state': 'Gujarat',
        'council_name': 'Bar Council of Gujarat',
    },
]


def find_user_by_enrollment(enrollment_number: str):
    """Return a User record by enrollment number."""
    return User.query.filter_by(enrollment_number=enrollment_number).first()


def register_user(enrollment_number: str, name: str, state: str, password: str):
    """Register a new verified advocate.

    Returns a tuple of (payload, status_code).
    """
    enrollment_number = enrollment_number.upper()

    if find_user_by_enrollment(enrollment_number):
        return {'error': 'Enrollment number already registered'}, 400

    is_valid, error_msg, verified_badge = verifier.verify(enrollment_number, name, state)
    if not is_valid:
        return {'error': error_msg}, 400

    user = User(
        enrollment_number=enrollment_number,
        name=name.strip(),
        password_hash=generate_password_hash(password),
        state=state.strip(),
        is_verified=verified_badge,
    )

    db.session.add(user)
    db.session.commit()

    return {
        'message': 'Registration successful',
        'enrollment_number': enrollment_number,
        'is_verified': True,
    }, 201


def authenticate_user(enrollment_number: str, password: str):
    """Authenticate advocate credentials and return User if valid."""
    enrollment_number = enrollment_number.upper()
    user = find_user_by_enrollment(enrollment_number)

    if user and check_password_hash(user.password_hash, password):
        return user

    return None


def verify_enrollment_preview(enrollment_number: str, state: str):
    """Prototype registry lookup used by the live registration UI."""
    enrollment_number = enrollment_number.upper().strip()
    state = state.strip()

    if not verifier._validate_format(enrollment_number):
        return {
            'verified': False,
            'message': 'Enrollment format should look like MH/1234/2020.',
        }, 400

    record = verifier.find_record(enrollment_number, state)
    if not record:
        return {
            'verified': False,
            'message': 'No matching record was found in the selected State Bar Council database.',
        }, 404

    return {
        'verified': True,
        'message': 'Enrollment found in the prototype State Bar Council database.',
        'advocate_name': record.advocate_name,
        'council_name': record.council_name,
        'status': record.status,
    }, 200


def seed_state_bar_council_records():
    """Seed prototype State Bar Council records for judge demos."""
    existing_numbers = {
        record.enrollment_number
        for record in StateBarCouncilRecord.query.with_entities(StateBarCouncilRecord.enrollment_number).all()
    }

    created = False
    for sample in SAMPLE_BAR_COUNCIL_RECORDS:
        if sample['enrollment_number'] in existing_numbers:
            continue
        db.session.add(StateBarCouncilRecord(**sample))
        created = True

    if created:
        db.session.commit()
