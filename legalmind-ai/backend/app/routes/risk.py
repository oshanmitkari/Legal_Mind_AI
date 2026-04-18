"""F10: Risk Scoring Engine - Auto-calculate and update risk scores"""
from flask import Blueprint, request, jsonify
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Case, RiskScore, Document, Deadline
from app.utils.risk_calculator import RiskCalculator
from datetime import datetime
import google.generativeai as genai
from flask import current_app
import os

risk_bp = Blueprint('risk', __name__)


def _initialize_gemini():
    """Initialize Gemini API"""
    api_key = current_app.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    return genai


@risk_bp.route('/calculate/<int:case_id>', methods=['POST'])
@login_required
def calculate_risk_score(case_id):
    """F10: Calculate comprehensive risk score for a case
    
    Risk Score Components (0-100):
    - Deadline Proximity (35%): Based on upcoming deadlines
    - Document Completeness (25%): Percentage of required documents
    - Document Strength (25%): Quality/quantity of evidence
    - AI Analysis (15%): Gemini-powered sentiment and strength assessment
    """
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Calculate individual scores
    deadline_score = RiskCalculator.calculate_deadline_score(case)
    documents = Document.query.filter_by(case_id=case_id).all()
    completeness_score = RiskCalculator.calculate_document_completeness(case)
    strength_score = RiskCalculator.calculate_document_strength(documents)
    
    # AI-powered analysis score
    analysis_score = 0.0
    ai_analysis = ""
    
    if documents:
        try:
            analysis_score, ai_analysis = _gemini_case_strength_analysis(case, documents)
        except Exception as e:
            ai_analysis = f"AI analysis unavailable: {str(e)}"
    
    # Calculate overall weighted score
    overall_score = RiskCalculator.calculate_overall_score(
        deadline_score,
        completeness_score,
        strength_score,
        analysis_score
    )
    
    # Update or create RiskScore record
    risk_record = RiskScore.query.filter_by(case_id=case_id).first()
    if not risk_record:
        risk_record = RiskScore(case_id=case_id)
        db.session.add(risk_record)
    
    risk_record.deadline_score = deadline_score
    risk_record.document_completeness = completeness_score
    risk_record.document_strength = strength_score
    risk_record.case_analysis_score = analysis_score
    risk_record.overall_score = overall_score
    risk_record.last_updated = datetime.utcnow()
    
    # Update case table
    case.risk_score = overall_score
    case.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'case_id': case_id,
        'risk_score': overall_score,
        'components': {
            'deadline_score': round(deadline_score, 2),
            'document_completeness': round(completeness_score, 2),
            'document_strength': round(strength_score, 2),
            'ai_analysis_score': round(analysis_score, 2)
        },
        'ai_analysis': ai_analysis,
        'risk_level': _get_risk_level(overall_score),
        'last_updated': risk_record.last_updated.isoformat()
    }), 200


@risk_bp.route('/batch-calculate', methods=['POST'])
@login_required
def batch_calculate_risk():
    """Calculate risk scores for all user's cases"""
    current_user = get_current_user()
    
    if current_user.is_admin:
        cases = Case.query.all()
    else:
        cases = Case.query.filter_by(user_id=current_user.id).all()
    
    results = []
    for case in cases:
        try:
            deadline_score = RiskCalculator.calculate_deadline_score(case)
            completeness_score = RiskCalculator.calculate_document_completeness(case)
            documents = Document.query.filter_by(case_id=case.id).all()
            strength_score = RiskCalculator.calculate_document_strength(documents)
            
            overall_score = RiskCalculator.calculate_overall_score(
                deadline_score, completeness_score, strength_score, 0.0
            )
            
            # Update case risk score
            case.risk_score = overall_score
            
            # Update or create RiskScore record
            risk_record = RiskScore.query.filter_by(case_id=case.id).first()
            if not risk_record:
                risk_record = RiskScore(case_id=case.id)
                db.session.add(risk_record)
            
            risk_record.deadline_score = deadline_score
            risk_record.document_completeness = completeness_score
            risk_record.document_strength = strength_score
            risk_record.overall_score = overall_score
            risk_record.last_updated = datetime.utcnow()
            
            results.append({
                'case_id': case.id,
                'case_number': case.case_number,
                'risk_score': overall_score
            })
        except Exception as e:
            results.append({
                'case_id': case.id,
                'error': str(e)
            })
    
    db.session.commit()
    
    return jsonify({
        'message': f'Calculated risk scores for {len(results)} cases',
        'results': results
    }), 200


def _gemini_case_strength_analysis(case, documents):
    """Use Gemini to analyze case strength and return score 0-100"""
    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare case summary
        doc_summary = "\n".join([
            f"- {d.document_type}: {len(d.text_content or '')} chars"
            for d in documents[:5]
        ])
        
        prompt = f"""You are an Indian legal expert analyzing case strength.

Case Details:
- Type: {case.case_type}
- Status: {case.status}
- Description: {case.description}

Documents Available:
{doc_summary}

Analyze the case strength and return ONLY a number between 0-100 where:
- 0-30: Weak case (insufficient evidence, weak legal grounds)
- 31-60: Moderate case (some evidence, unclear outcome)
- 61-85: Strong case (good evidence, solid legal basis)
- 86-100: Very strong case (compelling evidence, clear precedents)

Return ONLY the number, nothing else."""

        response = model.generate_content(prompt)
        score_text = response.text.strip()
        
        # Extract number from response
        import re
        numbers = re.findall(r'\d+', score_text)
        if numbers:
            score = min(max(float(numbers[0]), 0.0), 100.0)
            return score, score_text
        
        return 50.0, "Unable to parse AI analysis"
        
    except Exception as e:
        return 50.0, f"AI analysis failed: {str(e)}"


def _get_risk_level(score):
    """Convert numeric score to risk level label"""
    if score >= 75:
        return 'critical'
    elif score >= 50:
        return 'high'
    elif score >= 25:
        return 'medium'
    else:
        return 'low'
