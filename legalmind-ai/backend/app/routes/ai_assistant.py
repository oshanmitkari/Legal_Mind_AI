"""F6, F7, F8, F9: AI Features - Gemini integration for legal assistance"""
from flask import Blueprint, request, jsonify
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Case, ChatMessage, Document
from app.services.document_search_service import retrieve_case_document_snippets
import google.generativeai as genai
from flask import current_app
from datetime import datetime
import os

ai_bp = Blueprint('ai', __name__)

# Initialize Gemini
def _initialize_gemini():
    api_key = current_app.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    return genai

@ai_bp.route('/chat/<int:case_id>', methods=['POST'])
@login_required
def ai_chat(case_id):
    """F6: AI Case Assistant - Context-aware chat"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get case context
    case_context = _get_case_context(case)
    retrieved_sources = []
    try:
        retrieved_sources = retrieve_case_document_snippets(
            index_directory=current_app.config['FAISS_INDEX_PATH'],
            case_id=case_id,
            query_text=user_message,
            top_k=3,
        )
    except Exception:
        retrieved_sources = []

    evidence_context = _format_retrieved_sources(retrieved_sources)
    
    # Call Gemini
    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are a legal assistant. A lawyer is asking you about their case.

Case Context:
{case_context}

Retrieved Document Evidence:
{evidence_context}

Lawyer's Question: {user_message}

Provide a detailed, case-specific legal response based on the case context provided. Use the retrieved document evidence when available, and clearly ground your answer in the actual case details, uploaded documents, and Indian law where applicable."""
        
        response = model.generate_content(prompt)
        assistant_message = response.text
        
    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500
    
    # Save messages to history
    user_msg = ChatMessage(
        case_id=case_id,
        user_id=current_user.id,
        message_type='user',
        content=user_message
    )
    
    assistant_msg = ChatMessage(
        case_id=case_id,
        user_id=current_user.id,
        message_type='assistant',
        content=assistant_message
    )
    
    db.session.add(user_msg)
    db.session.add(assistant_msg)
    db.session.commit()
    
    return jsonify({
        'response': assistant_message,
        'message_id': assistant_msg.id,
        'sources': [{
            'document_id': source.document_id,
            'filename': source.filename,
            'document_type': source.document_type,
            'chunk_index': source.chunk_index,
            'snippet': source.snippet,
        } for source in retrieved_sources]
    }), 200

@ai_bp.route('/research', methods=['POST'])
@login_required
def legal_research():
    """F7: Legal Research (RAG) - Query Indian legal codes

    Enhanced version with structured citations and section references.
    Future enhancement: Add RAG from pre-loaded FAISS index of Indian statutes.
    """
    current_user = get_current_user()
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Empty query'}), 400

    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""You are an expert Indian legal researcher with deep knowledge of IPC, CrPC, CPC, IBC, IT Act, and Constitution of India.

Research Query: {query}

Provide comprehensive legal research with:

## 1. PRIMARY APPLICABLE SECTIONS
List exact section numbers with Act name (e.g., "Section 420 IPC", "Section 138 NI Act")

## 2. DETAILED PROVISIONS
Explain each section's scope, requirements, and conditions

## 3. PENALTIES & CONSEQUENCES
State punishment, bail status (bailable/non-bailable), cognizable status, and compoundability

## 4. LANDMARK JUDGMENTS
Cite 2-3 important Supreme Court or High Court cases with citation format

## 5. PRACTICAL GUIDANCE
Procedural steps, documentation required, and common pitfalls

## 6. RELATED SECTIONS
Cross-reference connected provisions that may apply

Use professional legal language. Cite section numbers accurately. Format with markdown headings."""

        response = model.generate_content(prompt)
        research_result = response.text

        # Extract section references for structured response
        import re
        sections = re.findall(r'Section\s+\d+[A-Z]*\s+[A-Z]{2,}', research_result)

    except Exception as e:
        return jsonify({'error': f'Research error: {str(e)}'}), 500

    return jsonify({
        'query': query,
        'research': research_result,
        'cited_sections': list(set(sections)) if sections else [],
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/draft', methods=['POST'])
@login_required
def draft_document():
    """F8: Document Drafter - Auto-fill templates"""
    current_user = get_current_user()
    data = request.get_json()
    case_id = data.get('case_id')
    template_type = data.get('template_type')  # Legal Notice, FIR, Affidavit, Bail, Contract
    
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    case_context = _get_case_context(case)
    
    templates = {
        'legal_notice': _draft_legal_notice,
        'fir_draft': _draft_fir,
        'affidavit': _draft_affidavit,
        'bail_application': _draft_bail_application,
        'contract': _draft_contract
    }
    
    if template_type not in templates:
        return jsonify({'error': 'Invalid template type'}), 400
    
    try:
        drafted_document = templates[template_type](case_context)
    except Exception as e:
        return jsonify({'error': f'Drafting error: {str(e)}'}), 500
    
    return jsonify({
        'template': template_type,
        'document': drafted_document,
        'format': ['pdf', 'docx']
    }), 200

@ai_bp.route('/suggest-sections', methods=['POST'])
@login_required
def suggest_sections():
    """F9: Section Suggester - Map incident to IPC/CrPC/IT Act sections

    Returns structured analysis with applicable legal sections.
    """
    current_user = get_current_user()
    data = request.get_json()
    incident_description = data.get('incident', '')

    if not incident_description:
        return jsonify({'error': 'Empty incident description'}), 400

    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""You are an expert Indian criminal law analyst. Analyze this incident and provide ONLY a valid JSON response.

Incident: {incident_description}

Return ONLY this JSON structure (no markdown, no explanation):
{{
  "primary_sections": [
    {{"section": "420 IPC", "description": "Cheating and dishonestly inducing delivery of property", "punishment": "Up to 7 years + fine"}},
    {{"section": "120B IPC", "description": "Criminal conspiracy", "punishment": "As per main offense"}}
  ],
  "secondary_sections": [
    {{"section": "Section number Act", "description": "Brief description"}}
  ],
  "offense_classification": {{
    "bailable": false,
    "cognizable": true,
    "compoundable": false,
    "triable_by": "Magistrate First Class / Sessions Court"
  }},
  "recommended_actions": [
    "File FIR under mentioned sections",
    "Collect documentary evidence",
    "Record witness statements"
  ],
  "case_strength": "Strong/Moderate/Weak",
  "additional_notes": "Any important procedural requirements or caveats"
}}"""

        response = model.generate_content(prompt)
        suggestion_text = response.text.strip()

        # Try to parse as JSON
        import json
        # Remove markdown code blocks if present
        if suggestion_text.startswith('```'):
            suggestion_text = suggestion_text.split('```')[1]
            if suggestion_text.startswith('json'):
                suggestion_text = suggestion_text[4:]
            suggestion_text = suggestion_text.strip()

        try:
            suggestion_json = json.loads(suggestion_text)
        except json.JSONDecodeError:
            # Fallback to text response
            suggestion_json = {
                'analysis': suggestion_text,
                'primary_sections': [],
                'note': 'AI returned unstructured response'
            }

    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

    return jsonify({
        'incident': incident_description,
        'analysis': suggestion_json,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@ai_bp.route('/chat/<int:case_id>/history', methods=['GET'])
@login_required
def chat_history(case_id):
    """Get chat conversation history"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = ChatMessage.query.filter_by(case_id=case_id).order_by(ChatMessage.created_at).all()
    
    return jsonify([{
        'id': m.id,
        'type': m.message_type,
        'content': m.content,
        'timestamp': m.created_at.isoformat()
    } for m in messages]), 200

# Helper functions
def _get_case_context(case):
    """Build full case context for AI"""
    documents = Document.query.filter_by(case_id=case.id).all()
    doc_text = "\n".join([f"[{d.document_type}]\n{d.text_content[:500]}..." 
                          for d in documents[:3]])  # Limit to first 3
    
    context = f"""
Case Number: {case.case_number}
Client Name: {case.client_name}
Case Type: {case.case_type}
Status: {case.status}
Description: {case.description}

Documents:
{doc_text}
"""
    return context


def _format_retrieved_sources(sources):
    """Format retrieved document snippets for inclusion in the prompt."""
    if not sources:
        return "No indexed document evidence was retrieved for this question."

    formatted = []
    for source in sources:
        formatted.append(
            f"[{source.filename} | {source.document_type} | chunk {source.chunk_index + 1}]\n"
            f"{source.snippet}"
        )
    return "\n\n".join(formatted)

def _draft_legal_notice(case_context):
    """Draft legal notice template using Gemini"""
    _initialize_gemini()
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""You are a senior Indian advocate. Draft a formal Legal Notice based on the following case information:

{case_context}

Create a complete, professionally formatted Legal Notice including:
1. Header with sender/receiver details
2. Subject line
3. Numbered facts and grievances
4. Legal basis citing relevant sections
5. Demand for action within 15 days
6. Consequences of non-compliance
7. Formal closing

Use proper Indian legal notice formatting and professional language."""

    response = model.generate_content(prompt)
    return response.text


def _draft_fir(case_context):
    """Draft FIR template using Gemini"""
    _initialize_gemini()
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""You are an Indian police officer. Draft a First Information Report (FIR) based on:

{case_context}

Create a structured FIR document with:
1. Date, time, and police station details
2. Complainant information
3. Detailed narrative of the incident
4. Applicable IPC/CrPC sections
5. Witnesses (if any)
6. Preliminary investigation notes
7. Officer signature block

Use official FIR format as per CrPC guidelines."""

    response = model.generate_content(prompt)
    return response.text


def _draft_affidavit(case_context):
    """Draft affidavit template using Gemini"""
    _initialize_gemini()
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""You are an Indian advocate preparing a court affidavit. Draft a sworn affidavit based on:

{case_context}

Structure:
1. Header: "AFFIDAVIT" with court details
2. Deponent details
3. Numbered paragraphs with sworn statements
4. Verification clause
5. Oath/declaration section
6. Signature blocks for deponent and notary

Use proper affidavit format as per Indian Evidence Act."""

    response = model.generate_content(prompt)
    return response.text


def _draft_bail_application(case_context):
    """Draft bail application using Gemini"""
    _initialize_gemini()
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""You are a criminal defense lawyer in India. Draft a Bail Application based on:

{case_context}

Include:
1. Court and case number
2. Applicant (accused) details
3. Grounds for bail (with CrPC Section 437/439 reference)
4. Merits: no prior criminal record, roots in community, etc.
5. Undertakings and conditions
6. Prayer for interim/regular bail
7. Advocate signature

Draft in formal court petition format."""

    response = model.generate_content(prompt)
    return response.text


def _draft_contract(case_context):
    """Draft contract template using Gemini"""
    _initialize_gemini()
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""You are a contracts lawyer in India. Draft a legal contract based on:

{case_context}

Structure:
1. Title and date
2. Parties (with complete details)
3. Recitals (WHEREAS clauses)
4. Terms and conditions (numbered clauses)
5. Payment terms
6. Termination clauses
7. Dispute resolution and jurisdiction
8. Signature blocks

Ensure compliance with Indian Contract Act, 1872."""

    response = model.generate_content(prompt)
    return response.text
