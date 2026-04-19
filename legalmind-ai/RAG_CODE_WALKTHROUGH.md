# 🔍 RAG Pipeline - Code Walkthrough

## Quick Reference Guide to RAG Implementation

---

## 📁 **FILE 1: Vector Store Core**

**Location**: `app/utils/vector_store.py`

### **Function 1: Text Chunking**
```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """
    Splits document text into overlapping chunks
    
    Example:
    Input: "This is a long legal document with many sections..."
    Output: [
        "This is a long legal document with many...",  # 0-1000
        "...many sections and important details...",   # 850-1850 (overlap 150)
        "...important details and evidence..."         # 1700-2700
    ]
    """
```

**Why overlap?** If a key fact is at character 1000, chunking without overlap would split it. Overlap ensures facts aren't cut off.

---

### **Function 2: Create Embeddings**
```python
def embed_texts(texts: List[str], dimension: int = 128) -> np.ndarray:
    """
    Convert text chunks to 128-dimensional vectors using SHA256 hashing
    
    Example:
    Input: ["Section 302 IPC murder", "Evidence fingerprints"]
    
    Process for "Section 302 IPC murder":
    1. Tokenize: ["section", "302", "ipc", "murder"]
    2. For each token:
       - Hash "section" with SHA256
       - Extract bucket index from first 4 bytes
       - Add weighted value to vector[bucket]
    3. Normalize vector (L2 norm)
    
    Output: np.array of shape (2, 128)
    [
        [0.0, 1.2, 0.0, -0.8, ...],  # Vector for "Section 302..."
        [0.5, 0.0, 1.1, 0.0, ...]    # Vector for "Evidence..."
    ]
    """
```

**Key Point**: Same text ALWAYS produces same vector (deterministic). No API calls needed!

---

### **Function 3: Index Document**
```python
def add_document(
    index_directory: str,
    case_id: int,
    document_id: int,
    file_path: str,
    text: str
) -> VectorizedDocument:
    """
    Add a document to FAISS index
    
    Flow:
    1. Chunk text (1000 chars, 150 overlap)
    2. Create embeddings for all chunks
    3. Assign vector IDs (e.g., 1, 2, 3, ...)
    4. Add vectors to FAISS index
    5. Save metadata to JSON
    
    Example:
    add_document(
        index_directory='data/faiss_index',
        case_id=1,
        document_id=5,
        file_path='/uploads/evidence.pdf',
        text='<extracted PDF text>'
    )
    
    Creates:
    • FAISS vectors for each chunk
    • Metadata entry linking vector ID → document
    """
```

**Storage Structure**:
```json
{
  "next_vector_id": 100,
  "documents": {
    "doc-5": {
      "document_id": 5,
      "case_id": 1,
      "file_path": "/uploads/evidence.pdf",
      "chunk_count": 12,
      "vector_ids": [88, 89, 90, 91, ..., 99]
    }
  },
  "chunks": {
    "88": {
      "document_id": 5,
      "case_id": 1,
      "chunk_index": 0,
      "text": "The evidence shows that fingerprints..."
    }
  }
}
```

---

### **Function 4: Search Chunks**
```python
def search_similar_chunks(
    index_directory: str,
    query_text: str,
    case_id: int,
    top_k: int = 5
) -> List[RetrievedChunk]:
    """
    Search FAISS index for relevant chunks
    
    Example Query: "What evidence do I have?"
    
    Process:
    1. Embed query: "What evidence..." → [0.3, 1.1, 0.0, ...]
    2. FAISS search: Find 25 nearest vectors
    3. Filter by case_id (only this case's chunks)
    4. Return top 5 matches
    
    Result:
    [
        RetrievedChunk(
            vector_id=88,
            document_id=5,
            case_id=1,
            chunk_index=0,
            text="The evidence shows fingerprints...",
            score=0.85
        ),
        ...
    ]
    """
```

---

## 📁 **FILE 2: Document Search Service**

**Location**: `app/services/document_search_service.py`

```python
def retrieve_case_document_snippets(
    index_directory: str,
    case_id: int,
    query_text: str,
    top_k: int = 3
) -> List[RetrievedDocumentSnippet]:
    """
    High-level retrieval API
    
    Calls: vector_store.search_similar_chunks()
    Then: Enriches results with Document metadata from database
    
    Example:
    snippets = retrieve_case_document_snippets(
        index_directory='data/faiss_index',
        case_id=1,
        query_text="What evidence do I have?",
        top_k=3
    )
    
    Returns:
    [
        RetrievedDocumentSnippet(
            document_id=5,
            filename="evidence.pdf",
            document_type="Evidence",
            chunk_index=0,
            snippet="The evidence shows...",
            score=0.85
        ),
        ...
    ]
    """
```

---

## 📁 **FILE 3: AI Assistant Route (Main RAG Orchestrator)**

**Location**: `app/routes/ai_assistant.py`

### **Endpoint**: `POST /ai/chat/<case_id>/send`

**Full Code Flow**:

```python
@ai_bp.route('/chat/<int:case_id>/send', methods=['POST'])
@login_required
def send_chat_message(case_id):
    # 1. Get user input
    data = request.get_json()
    user_message = data.get('message', '')
    
    # 2. Get case from database
    case = Case.query.get_or_404(case_id)
    
    # 3. Build comprehensive case context
    case_context = _get_comprehensive_case_context(case, current_user)
    # Returns ~3000-5000 char string with:
    # - Case metadata (number, type, dates)
    # - Client/lawyer info
    # - Risk scores
    # - All deadlines
    # - All documents with previews
    
    # 4. Get conversation history (last 20 messages)
    conversation_history = ChatMessage.query.filter_by(
        case_id=case_id
    ).order_by(ChatMessage.created_at.asc()).limit(20).all()
    
    # 5. FAISS retrieval - THE RAG MAGIC!
    retrieved_sources = retrieve_case_document_snippets(
        index_directory=current_app.config['FAISS_INDEX_PATH'],
        case_id=case_id,
        query_text=user_message,
        top_k=3  # Get top 3 relevant chunks
    )
    
    # 6. Build augmented prompt
    system_role = """You are a senior Indian advocate AI assistant specializing in 
    case analysis. Provide accurate, citation-backed legal advice."""
    
    # Format retrieved chunks
    retrieved_text = ""
    for snippet in retrieved_sources:
        retrieved_text += f"""
        Document: {snippet.filename} ({snippet.document_type})
        Relevance: {snippet.score:.2f}
        Content: {snippet.snippet}
        ---
        """
    
    # Combine everything into mega-prompt
    full_prompt = f"""
    {system_role}
    
    CASE CONTEXT:
    {case_context}
    
    RETRIEVED DOCUMENT EVIDENCE (RAG):
    {retrieved_text}
    
    CONVERSATION HISTORY:
    {format_conversation_history(conversation_history)}
    
    CURRENT USER QUESTION:
    {user_message}
    
    Please provide a comprehensive answer based on the case context and retrieved evidence.
    """
    
    # 7. Call Gemini API
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(full_prompt)
    ai_response = response.text
    
    # 8. Extract source documents
    sources = [snippet.filename for snippet in retrieved_sources]
    
    # 9. Save to database
    new_message = ChatMessage(
        case_id=case_id,
        user_id=current_user.id,
        sender='user',
        message=user_message
    )
    db.session.add(new_message)
    
    ai_message = ChatMessage(
        case_id=case_id,
        user_id=current_user.id,
        sender='ai',
        message=ai_response
    )
    db.session.add(ai_message)
    db.session.commit()
    
    # 10. Return JSON
    return jsonify({
        'response': ai_response,
        'sources': sources  # List of filenames used
    }), 200
```

---

### **Function: Get Comprehensive Case Context**

**Location**: `app/routes/ai_assistant.py` line 452

```python
def _get_comprehensive_case_context(case: Case, user: User) -> str:
    """
    Aggregates ALL case data into a structured text block
    
    Returns formatted string like:
    '''
    CASE INFORMATION:
    Case Number: CJ/1010
    Case Type: Criminal
    Status: Active
    Filed Date: 2024-01-15
    
    CLIENT DETAILS:
    Client Name: Rajesh Kumar
    
    LAWYER DETAILS:
    Advocate: Priya Sharma
    Enrollment: MH/12345/2020
    State: Maharashtra
    
    CASE DESCRIPTION:
    This is a criminal case involving alleged murder under Section 302 IPC...
    
    RISK ASSESSMENT:
    Overall Risk Score: 75.3%
    Deadline Risk: High (3 overdue deadlines)
    Document Completeness: 80%
    
    UPCOMING DEADLINES (3):
    1. ⏰ URGENT - Court Hearing (Due: 2024-04-20, 2 days away)
    2. 🔴 OVERDUE - Evidence Submission (Was due: 2024-04-15)
    3. 🟢 Filing Deadline (Due: 2024-05-01, 12 days away)
    
    UPLOADED DOCUMENTS (5):
    1. evidence.pdf (Evidence, uploaded 2024-04-01)
       Preview: "The fingerprints found on the weapon match..."
    2. witness_statement.pdf (Witness Statement, uploaded 2024-04-02)
       Preview: "I witnessed the accused at the scene..."
    '''
    """
```

---

## 🎯 **COMPLETE EXAMPLE**

### **User Asks**: "What evidence do I have against the accused?"

### **Backend Process**:

1. **Get case context** → 3500 chars of case data
2. **Get history** → Last 20 chat messages
3. **FAISS search**:
   - Embed query: "What evidence do I have against the accused?"
   - Search index: Find top 3 matching chunks
   - Result:
     ```
     1. evidence.pdf chunk 2 (score: 0.85)
        "The forensic report shows fingerprints matching the accused..."
     
     2. evidence.pdf chunk 5 (score: 0.78)
        "DNA samples collected from the crime scene..."
     
     3. witness_statement.pdf chunk 3 (score: 0.72)
        "The witness identified the accused in a police lineup..."
     ```

4. **Build prompt** (8000 chars total):
   ```
   You are a senior advocate...
   
   CASE CONTEXT: [3500 chars]
   
   RETRIEVED EVIDENCE:
   - evidence.pdf: "fingerprints matching accused..."
   - evidence.pdf: "DNA samples..."
   - witness_statement.pdf: "witness identified..."
   
   USER QUESTION: What evidence do I have?
   ```

5. **Gemini generates**:
   ```
   Based on the uploaded evidence.pdf and witness statements, you have:
   
   1. FORENSIC EVIDENCE:
      - Fingerprints matching the accused (evidence.pdf)
      - DNA samples from crime scene (evidence.pdf)
   
   2. WITNESS TESTIMONY:
      - Eyewitness identification (witness_statement.pdf)
   
   This constitutes strong circumstantial evidence under IPC Section 302.
   ```

6. **Return to UI**:
   ```json
   {
     "response": "Based on the uploaded evidence.pdf...",
     "sources": ["evidence.pdf", "witness_statement.pdf"]
   }
   ```

---

## ✅ **KEY TAKEAWAYS**

1. **RAG = Context + Retrieval + Generation**
2. **FAISS** handles vector similarity search (offline, fast)
3. **SHA256 embeddings** = deterministic, no API costs
4. **Chunking** = 1000 chars with 150 overlap
5. **Top-K** = Return 3 most relevant chunks
6. **Prompt augmentation** = Combine context + chunks + question
7. **Gemini** generates answer based on REAL documents

**Result**: AI answers are grounded in actual case files, not hallucinations! 🎯

---

**Files to Study**:
1. `app/utils/vector_store.py` - Core vector operations
2. `app/services/document_search_service.py` - Retrieval wrapper
3. `app/routes/ai_assistant.py` - RAG orchestration

**Total RAG Pipeline**: ~800 lines of code
**Status**: ✅ Fully implemented and working
