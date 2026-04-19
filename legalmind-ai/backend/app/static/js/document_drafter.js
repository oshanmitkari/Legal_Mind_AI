/**
 * F8: Document Drafter - Client-side Interface
 */

let draftForm, loadingOverlay, generatedDocument, documentContent;

document.addEventListener('DOMContentLoaded', function() {
    draftForm = document.getElementById('draftForm');
    loadingOverlay = document.getElementById('loadingOverlay');
    generatedDocument = document.getElementById('generatedDocument');
    documentContent = document.getElementById('documentContent');
    
    if (draftForm) {
        draftForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await generateDocument();
        });
    }
});

async function generateDocument() {
    const caseId = document.getElementById('caseId').value;
    const templateType = document.getElementById('templateType').value;
    
    if (!caseId || !templateType) {
        alert('Please select both case and template type');
        return;
    }
    
    loadingOverlay.style.display = 'block';
    generatedDocument.style.display = 'none';
    
    try {
        const response = await fetch('/ai/draft', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                case_id: parseInt(caseId),
                template_type: templateType
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayDocument(data);
        } else {
            alert('Error: ' + (data.error || 'Failed to generate document'));
        }
    } catch (error) {
        alert('Failed to generate document: ' + error.message);
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function displayDocument(data) {
    // Format the document with proper spacing
    const formattedDoc = data.document.replace(/\n/g, '<br>');
    documentContent.innerHTML = formattedDoc;
    generatedDocument.style.display = 'block';
    generatedDocument.scrollIntoView({behavior: 'smooth'});
}

function exportDocument() {
    const content = documentContent.innerText;
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `legal_document_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
