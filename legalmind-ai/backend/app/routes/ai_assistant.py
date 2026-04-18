"""F6, F7, F8, F9: AI Features - Gemini integration for legal assistance"""
from flask import Blueprint, request, jsonify
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Case, ChatMessage, Document
from app.services.document_search_service import retrieve_case_document_snippets
import google.generativeai as genai
from flask import current_app
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
    """F7: Legal Research (RAG) - Query Indian legal codes"""
    current_user = get_current_user()
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are an expert Indian legal researcher. A lawyer is asking for legal information.

Query: {query}

Provide research based on Indian legal codes (IPC, CrPC, CPC, IBC, IT Act):
1. Relevant sections with exact numbers
2. Key provisions and requirements
3. Penalties or consequences if applicable
4. Recent judicial interpretations if relevant
5. Practical implications for lawyers

Format your response with clear section headings."""
        
        response = model.generate_content(prompt)
        research_result = response.text
        
    except Exception as e:
        return jsonify({'error': f'Research error: {str(e)}'}), 500
    
    return jsonify({
        'query': query,
        'research': research_result
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
    """F9: Section Suggester - Map incident to IPC/CrPC/IT Act sections"""
    current_user = get_current_user()
    data = request.get_json()
    incident_description = data.get('incident', '')
    
    if not incident_description:
        return jsonify({'error': 'Empty incident description'}), 400
    
    try:
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are an expert in Indian criminal and technology law. Analyze the following incident and map it to applicable sections.

Incident Description: {incident_description}

Provide:
1. Primary sections that MUST apply (IPC/CrPC/IT Act/POCSO/NDPS)
2. Secondary/supporting sections
3. Bailable or Non-bailable status
4. Cognizable or Non-cognizable status
5. Recommended court type (Magistrate/Sessions/etc.)
6. Suggested next legal steps

Format as structured JSON with clear fields."""
        
        response = model.generate_content(prompt)
        suggestion = response.text
        
    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500
    
    return jsonify({
        'incident': incident_description,
        'analysis': suggestion
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
    """Draft legal notice template"""
    return "LEGAL NOTICE DRAFT\n\n" + case_context + "\n\n[Notice content to be generated by Gemini API]"

def _draft_fir(case_context):
    """Draft FIR template"""
    return "FIR DRAFT\n\n" + case_context + "\n\n[FIR content to be generated by Gemini API]"

def _draft_affidavit(case_context):
    """Draft affidavit template"""
    return "AFFIDAVIT DRAFT\n\n" + case_context + "\n\n[Affidavit content to be generated by Gemini API]"

def _draft_bail_application(case_context):
    """Draft bail application template"""
    return "BAIL APPLICATION DRAFT\n\n" + case_context + "\n\n[Bail application content to be generated by Gemini API]"

def _draft_contract(case_context):
    """Draft contract template"""
    return "CONTRACT DRAFT\n\n" + case_context + "\n\n[Contract content to be generated by Gemini API]"
