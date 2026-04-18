"""F5: PDF Upload & Analysis - Document ingestion with FAISS"""
from flask import Blueprint, request, jsonify
from app.utils.auth_utils import login_required, get_current_user
from app.models import Document, Case
from flask import current_app
from app.services.document_service import ingest_pdf_document, delete_document_assets

documents_bp = Blueprint('documents', __name__)

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@documents_bp.route('/<int:case_id>', methods=['GET'])
@login_required
def list_documents(case_id):
    """Get all documents for a case"""
    current_user = get_current_user()
    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    documents = Document.query.filter_by(case_id=case_id).all()
    
    return jsonify([{
        'id': d.id,
        'filename': d.filename,
        'document_type': d.document_type,
        'uploaded_at': d.uploaded_at.isoformat(),
        'text_length': len(d.text_content) if d.text_content else 0
    } for d in documents]), 200

@documents_bp.route('/<int:case_id>/upload', methods=['POST'])
@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload_document(case_id=None):
    """F5: Upload PDF - Extract text and create FAISS embedding"""
    current_user = get_current_user()
    if case_id is None:
        case_id = request.form.get('case_id', type=int)
        if not case_id:
            return jsonify({'error': 'case_id is required'}), 400

    case = Case.query.get_or_404(case_id)
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files allowed'}), 400

    try:
        result = ingest_pdf_document(
            upload_file=file,
            case_id=case_id,
            upload_folder=current_app.config['UPLOAD_FOLDER'],
            index_directory=current_app.config['FAISS_INDEX_PATH'],
            document_type=request.form.get('document_type', 'General'),
        )
    except Exception as e:
        return jsonify({'error': f'Failed to index document: {str(e)}'}), 400
    
    return jsonify({
        'id': result.document.id,
        'message': 'Document uploaded successfully',
        'text_length': result.text_length,
        'chunk_count': result.chunk_count,
        'faiss_index_id': result.document.faiss_index_id,
    }), 201

@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    """Delete document"""
    current_user = get_current_user()
    document = Document.query.get_or_404(doc_id)
    case = document.case
    
    # Authorization
    if not current_user.is_admin and case.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    delete_document_assets(
        document=document,
        index_directory=current_app.config['FAISS_INDEX_PATH'],
    )
    
    return jsonify({'message': 'Document deleted'}), 200
