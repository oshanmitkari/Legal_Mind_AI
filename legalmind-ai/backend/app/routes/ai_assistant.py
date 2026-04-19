"""F6, F7, F8, F9: AI Features - Gemini integration for legal assistance"""
from flask import Blueprint, request, jsonify, render_template
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Case, ChatMessage, Document
from app.services.document_search_service import retrieve_case_document_snippets
import google.generativeai as genai
from flask import current_app
from datetime import datetime
import os

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/research', methods=['GET'])
@login_required
def research_page():
    """F7: Render legal research UI page"""
    current_user = get_current_user()
    return render_template('research/index.html', current_user=current_user)


@ai_bp.route('/draft', methods=['GET'])
@login_required
def draft_page():
    """F8: Render document drafter UI page"""
    from app.models import Case
    current_user = get_current_user()
    # Get user's cases for dropdown
    if current_user.is_admin:
        cases = Case.query.all()
    else:
        cases = Case.query.filter_by(user_id=current_user.id).all()
    return render_template('drafter/index.html', current_user=current_user, cases=cases)


@ai_bp.route('/suggest-sections', methods=['GET'])
@login_required
def suggest_sections_page():
    """F9: Render section suggester UI page"""
    current_user = get_current_user()
    return render_template('suggester/index.html', current_user=current_user)


# Initialize Gemini
def _initialize_gemini():
    # Try system environment first (most secure), then .env file
    api_key = os.environ.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    else:
        raise RuntimeError("GEMINI_API_KEY not found. Set it as system environment variable.")
    return genai

@ai_bp.route('/chat/<int:case_id>', methods=['POST'])
@login_required
def ai_chat(case_id):
    """F6: AI Case Assistant - Context-aware chat with conversation history"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)

    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # Step 1: Aggregate ALL case data
    case_context = _get_comprehensive_case_context(case, current_user)

    # Step 2: Retrieve conversation history for context
    conversation_history = ChatMessage.query.filter_by(
        case_id=case_id
    ).order_by(ChatMessage.created_at.asc()).limit(20).all()  # Last 20 messages

    # Step 3: Retrieve relevant document snippets using FAISS
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

    # Step 4: Construct comprehensive system prompt
    system_prompt = f"""You are a specialized legal AI assistant for Case {case.case_number}. You have deep knowledge of this specific case and must provide context-aware, actionable legal advice.

IMPORTANT: Your responses MUST be grounded in the actual facts of this case, not generic legal information. Reference specific details from the case context, uploaded documents, and conversation history.

{case_context}

RETRIEVED DOCUMENT EVIDENCE (from case files):
{evidence_context if evidence_context else "No specific document evidence retrieved for this query."}

INSTRUCTIONS:
1. Always reference specific case details (client name, case type, deadlines, documents)
2. If document evidence is available, cite it explicitly
3. Provide actionable next steps specific to this case
4. Flag any critical deadlines or risks
5. Use Indian legal framework when applicable (IPC, CrPC, CPC, etc.)
"""

    # Step 5: Build conversation history for Gemini
    conversation_context = []
    for msg in conversation_history:
        conversation_context.append({
            'role': 'user' if msg.message_type == 'user' else 'model',
            'parts': [msg.content]
        })

    # Step 6: Call Gemini with full context
    try:
        _initialize_gemini()
        model = genai.GenerativeModel(
            'gemini-flash-latest',
            system_instruction=system_prompt
        )

        # Start chat with history
        chat = model.start_chat(history=conversation_context)

        # Send new message
        response = chat.send_message(user_message)
        assistant_message = response.text

    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500

    # Step 7: Save conversation to database
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
        'history_count': len(conversation_history),
        'sources': [{
            'document_id': source.document_id,
            'filename': source.filename,
            'document_type': source.document_type,
            'chunk_index': source.chunk_index,
            'snippet': source.snippet,
        } for source in retrieved_sources]
    }), 200


@ai_bp.route('/chat/<int:case_id>/history', methods=['GET'])
@login_required
def get_chat_history(case_id):
    """F6: Get chat history for a case - Persistence feature"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)

    # Authorization - RLS enforcement
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Retrieve all messages for this case, ordered by time
    messages = ChatMessage.query.filter_by(case_id=case_id).order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        'case_id': case_id,
        'case_number': case.case_number,
        'message_count': len(messages),
        'messages': [{
            'id': msg.id,
            'message_type': msg.message_type,  # 'user' or 'assistant'
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
        } for msg in messages]
    }), 200

@ai_bp.route('/research', methods=['POST'])
@login_required
def legal_research():
    """F7: Legal Research (RAG) - Query Indian legal codes with FAISS retrieval

    Uses pre-loaded FAISS index of Indian statutes (IPC, CrPC, CPC, IBC, IT Act)
    """
    current_user = get_current_user()
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Empty query'}), 400

    try:
        # F7: Retrieve relevant sections from law FAISS index
        from app.utils.law_index_builder import search_law_index
        import os

        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        law_index_dir = os.path.join(backend_dir, 'data', 'law_faiss_index')

        # Get top 5 relevant law sections
        try:
            relevant_sections = search_law_index(law_index_dir, query, top_k=5)
            rag_context = "\n\n".join([
                f"**{section['section_title']}**\n{section['text']}"
                for section in relevant_sections
            ])
        except FileNotFoundError:
            # Fallback if index not built
            rag_context = "Law index not available - using general knowledge"
            relevant_sections = []

        # Build enhanced prompt with RAG context
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""You are an expert Indian legal researcher analyzing a query using the provided legal statutes.

Research Query: {query}

Retrieved Relevant Sections from Indian Law:
{rag_context}

Based on the retrieved sections and your legal knowledge, provide comprehensive research with:

## 1. PRIMARY APPLICABLE SECTIONS
List exact section numbers with Act name (e.g., "Section 420 IPC", "Section 138 NI Act")

## 2. DETAILED PROVISIONS
Explain each section's scope, requirements, and conditions from the retrieved text

## 3. PENALTIES & CONSEQUENCES
State punishment, bail status (bailable/non-bailable), cognizable status, and compoundability

## 4. PRACTICAL IMPLICATIONS
Procedural steps for lawyers, documentation required, and common pitfalls

## 5. RELATED SECTIONS
Cross-reference connected provisions that may apply

Use professional legal language. Cite section numbers accurately from retrieved text. Format with markdown headings."""

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
        'retrieved_sections': [
            {
                'title': s['section_title'],
                'relevance': s['relevance_score']
            } for s in relevant_sections
        ] if relevant_sections else [],
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
        model = genai.GenerativeModel('gemini-flash-latest')
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
    """Build full case context for AI - F6: Enhanced with deadlines (Legacy function)"""
    from app.models import Deadline

    # Get documents
    documents = Document.query.filter_by(case_id=case.id).all()
    doc_text = "\n".join([f"[{d.document_type}]\n{d.text_content[:500]}..."
                          for d in documents[:3]])  # Limit to first 3

    # Get upcoming deadlines
    deadlines = Deadline.query.filter_by(case_id=case.id, is_completed=False).order_by(Deadline.due_date.asc()).limit(5).all()
    deadline_text = "\n".join([
        f"- {d.title} (Due: {d.due_date.strftime('%Y-%m-%d %H:%M')}, Priority: {d.priority}, Type: {d.deadline_type})"
        for d in deadlines
    ]) if deadlines else "No upcoming deadlines"

    context = f"""
Case Number: {case.case_number}
Client Name: {case.client_name}
Case Type: {case.case_type}
Status: {case.status}
Description: {case.description}
Risk Score: {case.risk_score}/100

Upcoming Deadlines:
{deadline_text}

Documents Uploaded:
{doc_text if doc_text else "No documents uploaded yet"}
"""
    return context


def _get_comprehensive_case_context(case, current_user):
    """F6: Build COMPREHENSIVE case context with ALL aggregated data

    Aggregates:
    - Case description and metadata
    - Client details
    - All uploaded documents with extracted text
    - All deadlines and important dates
    - Case notes (if any)
    - Lawyer information
    - Risk assessment data
    """
    from app.models import Deadline, RiskScore
    from datetime import datetime

    # === CASE METADATA ===
    case_metadata = f"""
═══════════════════════════════════════════════════════════════
CASE INFORMATION
═══════════════════════════════════════════════════════════════
Case Number: {case.case_number}
Case Type: {case.case_type}
Status: {case.status.upper()}
Created: {case.created_at.strftime('%Y-%m-%d')}
Last Updated: {case.updated_at.strftime('%Y-%m-%d %H:%M')}
"""

    # === CLIENT DETAILS ===
    client_info = f"""
CLIENT INFORMATION
═══════════════════════════════════════════════════════════════
Client Name: {case.client_name}
"""

    # === LAWYER DETAILS ===
    lawyer_info = f"""
LAWYER ASSIGNED
═══════════════════════════════════════════════════════════════
Advocate: {current_user.name}
Enrollment No: {current_user.enrollment_number}
State: {current_user.state}
Verified: {'✓ Yes' if current_user.is_verified else '✗ No'}
"""

    # === CASE DESCRIPTION ===
    description_section = f"""
CASE DESCRIPTION
═══════════════════════════════════════════════════════════════
{case.description if case.description else "No description provided."}
"""

    # === RISK ASSESSMENT ===
    risk_data = RiskScore.query.filter_by(case_id=case.id).first()
    risk_section = f"""
RISK ASSESSMENT
═══════════════════════════════════════════════════════════════
Overall Risk Score: {case.risk_score}/100
"""
    if risk_data:
        risk_section += f"""Deadline Risk: {risk_data.deadline_score}/100
Document Completeness: {risk_data.document_completeness}/100
Document Strength: {risk_data.document_strength}/100
Last Assessed: {risk_data.last_updated.strftime('%Y-%m-%d %H:%M')}
"""

    # === DEADLINES ===
    deadlines = Deadline.query.filter_by(case_id=case.id).order_by(Deadline.due_date.asc()).all()
    deadline_section = f"""
DEADLINES & IMPORTANT DATES
═══════════════════════════════════════════════════════════════
Total Deadlines: {len(deadlines)}
"""
    if deadlines:
        now = datetime.utcnow()
        for dl in deadlines[:10]:  # Show top 10
            status = "✓ COMPLETED" if dl.is_completed else "⏰ PENDING"
            days_until = (dl.due_date - now).days
            urgency = ""
            if not dl.is_completed:
                if days_until < 0:
                    urgency = "🔴 OVERDUE"
                elif days_until <= 3:
                    urgency = "🟡 URGENT (Due soon!)"
                else:
                    urgency = "🟢 Safe"

            deadline_section += f"""
  [{status}] {dl.title}
  Type: {dl.deadline_type}
  Due: {dl.due_date.strftime('%Y-%m-%d %H:%M')} {urgency}
  Priority: {dl.priority.upper()}
"""
    else:
        deadline_section += "\nNo deadlines set for this case.\n"

    # === UPLOADED DOCUMENTS ===
    documents = Document.query.filter_by(case_id=case.id).all()
    doc_section = f"""
UPLOADED DOCUMENTS
═══════════════════════════════════════════════════════════════
Total Documents: {len(documents)}
"""
    if documents:
        for doc in documents:
            text_preview = doc.text_content[:300] + "..." if doc.text_content and len(doc.text_content) > 300 else (doc.text_content or "No text extracted")
            doc_section += f"""
  📄 {doc.filename}
  Type: {doc.document_type or 'Unknown'}
  Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d')}
  Extracted Text Preview:
  {text_preview}
  ---
"""
    else:
        doc_section += "\nNo documents uploaded yet.\n"

    # === COMBINE ALL CONTEXT ===
    full_context = f"""{case_metadata}{client_info}{lawyer_info}{description_section}{risk_section}{deadline_section}{doc_section}
═══════════════════════════════════════════════════════════════
END OF CASE CONTEXT
═══════════════════════════════════════════════════════════════
"""

    return full_context


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
    model = genai.GenerativeModel('gemini-flash-latest')

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
    model = genai.GenerativeModel('gemini-flash-latest')

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
    model = genai.GenerativeModel('gemini-flash-latest')

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
    model = genai.GenerativeModel('gemini-flash-latest')

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
    model = genai.GenerativeModel('gemini-flash-latest')

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


# ============================================================================
# F11: LEGAL PRECEDENT & CASE SIMILARITY ENGINE
# ============================================================================

@ai_bp.route('/compare-precedents/<int:case_id>', methods=['GET'])
@login_required
def compare_precedents(case_id):
    """F11: Find similar historical precedents and generate AI comparison analysis

    Returns:
        JSON with similar cases and AI-generated comparison report
    """
    from app.services.precedent_service import find_similar_precedents
    from app.models import HistoricalCase

    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)

    # Authorization check (RLS)
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        # Step 1: Find top 3 similar precedents using FAISS
        similar_cases = find_similar_precedents(case_id, top_k=3)

        if not similar_cases:
            return jsonify({
                'error': 'No similar precedents found',
                'similar_cases': [],
                'comparison_report': 'No historical precedents available for comparison.'
            }), 200

        # Step 2: Build comprehensive context for AI analysis
        current_case_context = f"""
CURRENT CASE DETAILS:
Case Number: {case.case_number if case.case_number else 'CASE-' + str(case.id)}
Case Type: {case.case_type}
Client: {case.client_name}
Description: {case.description}
Status: {case.status}
Risk Score: {case.risk_score}/100
"""

        # Format similar cases for AI
        precedents_context = ""
        precedent_summaries = []

        for idx, (hist_case, similarity_score) in enumerate(similar_cases, 1):
            precedents_context += f"""
PRECEDENT {idx} (Similarity: {similarity_score:.1f}%):
Case Number: {hist_case.case_number}
Title: {hist_case.title}
Case Type: {hist_case.case_type}
Description: {hist_case.description}
Outcome: {hist_case.outcome}
Key Sections: {hist_case.key_sections}
Court: {hist_case.court}
Judgment Date: {hist_case.judgment_date.strftime('%Y-%m-%d')}
---
"""
            # Store for response
            precedent_summaries.append(hist_case.to_dict())

        # Step 3: Generate AI comparison analysis using Gemini
        _initialize_gemini()
        model = genai.GenerativeModel('gemini-flash-latest')

        comparison_prompt = f"""You are an expert legal analyst specializing in Indian law. Analyze the current case against the provided historical precedents.

{current_case_context}

HISTORICAL PRECEDENTS FOUND (Ranked by Similarity):
{precedents_context}

TASK:
Provide a comprehensive comparison analysis addressing:

1. **Similarity Analysis**: Explain WHY these precedents were matched (common facts, legal issues, case types)

2. **Legal Overlaps**: Identify which legal provisions, statutes, or sections are common across these cases

3. **Outcome Patterns**: Analyze how the historical cases were decided and what factors influenced those outcomes

4. **Strategic Implications**: Based on these precedents, what legal strategy should be adopted for the current case?

5. **Distinguishing Factors**: Highlight any key differences that might affect applicability

6. **Recommended Actions**: Specific next steps based on how similar cases were handled

Format your analysis clearly with headings and bullet points. Be specific and cite the precedent case numbers when making references.
"""

        response = model.generate_content(comparison_prompt)
        comparison_report = response.text

        # Step 4: Return results
        return jsonify({
            'success': True,
            'current_case': {
                'id': case.id,
                'case_number': case.case_number if case.case_number else f'CASE-{case.id}',
                'case_type': case.case_type,
                'client_name': case.client_name,
                'description': case.description,
                'status': case.status,
                'risk_score': case.risk_score
            },
            'similar_cases': precedent_summaries,
            'comparison_report': comparison_report,
            'precedent_count': len(similar_cases)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in precedent comparison: {str(e)}")
        return jsonify({
            'error': f'Failed to generate precedent comparison: {str(e)}'
        }), 500
