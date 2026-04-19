"""
Fix missing case_number for existing cases in the database
"""
from app import create_app, db
from app.models import Case
from datetime import datetime

app = create_app()

with app.app_context():
    print("Fixing cases with missing case_number...")
    
    # Find all cases
    cases = Case.query.all()
    
    updated_count = 0
    for case in cases:
        if not case.case_number or case.case_number.strip() == '':
            # Generate case number based on case type and ID
            year = case.created_at.year
            case_type_prefix = case.case_type[:3].upper()  # First 3 letters of case type
            
            new_case_number = f"{case_type_prefix}/{year}/{case.id:04d}"
            
            print(f"Updating Case ID {case.id}: Setting case_number to {new_case_number}")
            
            case.case_number = new_case_number
            case.updated_at = datetime.utcnow()
            
            updated_count += 1
    
    if updated_count > 0:
        db.session.commit()
        print(f"\n✅ Successfully updated {updated_count} case(s)")
    else:
        print("\n✅ All cases already have case_number set")
    
    # Display all cases
    print("\n" + "="*70)
    print("CURRENT CASES IN DATABASE:")
    print("="*70)
    
    all_cases = Case.query.all()
    for case in all_cases:
        print(f"ID: {case.id}")
        print(f"  Case Number: {case.case_number}")
        print(f"  Client: {case.client_name}")
        print(f"  Type: {case.case_type}")
        print(f"  Status: {case.status}")
        print(f"  Risk Score: {case.risk_score}")
        if case.deadline_date:
            status, color = case.get_deadline_status()
            print(f"  Deadline: {case.deadline_date.strftime('%Y-%m-%d %H:%M')} ({status})")
        print(f"  Created: {case.created_at.strftime('%Y-%m-%d')}")
        print("-" * 70)
