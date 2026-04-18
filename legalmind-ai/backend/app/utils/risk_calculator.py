"""F10: Risk Scoring Engine - Dynamic risk assessment"""
from datetime import datetime, timedelta
from app.models import Deadline, Document

class RiskCalculator:
    """Calculates 0-100 risk score from multiple factors"""
    
    @staticmethod
    def calculate_deadline_score(case):
        """Score based on deadline proximity - higher = more risk"""
        deadlines = Deadline.query.filter_by(case_id=case.id, is_completed=False).all()
        
        if not deadlines:
            return 0.0
        
        now = datetime.utcnow()
        score = 0.0
        
        for deadline in deadlines:
            days_until = (deadline.due_date - now).days
            
            if days_until < 0:
                score += 100  # Overdue = max risk
            elif days_until <= 3:
                score += 80  # Due within 3 days
            elif days_until <= 7:
                score += 50  # Due within week
            elif days_until <= 14:
                score += 25  # Due within 2 weeks
            else:
                score += 5   # Safe
        
        # Average across deadlines
        return min(score / len(deadlines), 100.0)
    
    @staticmethod
    def calculate_document_completeness(case):
        """Score based on how many documents uploaded"""
        doc_count = Document.query.filter_by(case_id=case.id).count()
        
        # Expected: FIR, Evidence, Motion, Judgment = 4 docs
        expected_docs = 4
        completeness = min((doc_count / expected_docs) * 100, 100.0)
        
        return completeness
    
    @staticmethod
    def calculate_document_strength(documents):
        """Score based on PDF size/quality (proxy for evidence strength)"""
        if not documents:
            return 0.0
        
        total_size = sum(len(doc.text_content or '') for doc in documents)
        
        # Heuristic: strong document has >5000 chars
        strength_per_doc = min((total_size / len(documents)) / 5000 * 100, 100.0)
        
        return strength_per_doc
    
    @staticmethod
    def calculate_overall_score(deadline_score, completeness_score, 
                               document_strength_score, analysis_score=0.0):
        """Weighted average of all components"""
        weights = {
            'deadline': 0.35,
            'completeness': 0.25,
            'strength': 0.25,
            'analysis': 0.15
        }
        
        overall = (
            deadline_score * weights['deadline'] +
            completeness_score * weights['completeness'] +
            document_strength_score * weights['strength'] +
            analysis_score * weights['analysis']
        )
        
        return round(overall, 2)
