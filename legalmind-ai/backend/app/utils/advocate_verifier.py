"""F1: Advocate Verification - Three-tier validation system"""
import re
from app.models import StateBarCouncilRecord

class AdvocateVerifier:
    """Validates Bar Council enrollment numbers and cross-checks registry"""
    
    # Pattern: MH/1234/2020 format
    ENROLLMENT_PATTERN = r'^[A-Z]{2}/\d{4}/\d{4}$'
    
    def verify(self, enrollment_number, name, state):
        """
        Three-tier verification:
        1. Format check (regex pattern)
        2. Registry match (name + state)
        3. Duplicate check is handled by the registration route
        
        Returns: (is_valid, error_message, verified_badge)
        """
        if not self._validate_format(enrollment_number):
            return False, 'Invalid enrollment number format. Expected: MH/1234/2020', False
        
        record = self.find_record(enrollment_number, state)
        if not record:
            return False, 'Enrollment number was not found in the selected State Bar Council registry', False

        if record.advocate_name.lower() != name.lower():
            return False, 'Enrollment details do not match Bar Council registry', False
        
        return True, 'Verification successful', True
    
    def _validate_format(self, enrollment_number):
        """Tier 1: Validate regex pattern"""
        return bool(re.match(self.ENROLLMENT_PATTERN, enrollment_number))
    
    def find_record(self, enrollment_number, state):
        """Find a registry record by enrollment number and state."""
        return StateBarCouncilRecord.query.filter_by(
            enrollment_number=enrollment_number.upper(),
            state=state.strip()
        ).first()
