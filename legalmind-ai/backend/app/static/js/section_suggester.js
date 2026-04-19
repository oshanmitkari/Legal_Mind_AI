/**
 * F9: Section Suggester - Client-side Interface
 */

let suggesterForm, loadingOverlay, results, incidentDescription;

document.addEventListener('DOMContentLoaded', function() {
    suggesterForm = document.getElementById('suggesterForm');
    loadingOverlay = document.getElementById('loadingOverlay');
    results = document.getElementById('results');
    incidentDescription = document.getElementById('incidentDescription');
    
    if (suggesterForm) {
        suggesterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await suggestSections();
        });
    }
});

async function suggestSections() {
    const incident = incidentDescription.value.trim();
    
    if (!incident) {
        alert('Please describe the incident');
        return;
    }
    
    loadingOverlay.style.display = 'block';
    results.style.display = 'none';
    
    try {
        const response = await fetch('/ai/suggest-sections', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({incident: incident})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            alert('Error: ' + (data.error || 'Failed to analyze incident'));
        }
    } catch (error) {
        alert('Failed to analyze: ' + error.message);
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function displayResults(data) {
    const analysis = data.analysis;
    
    // Display primary sections
    const primarySections = document.getElementById('primarySections');
    if (typeof analysis === 'object' && analysis.primary_sections) {
        primarySections.innerHTML = analysis.primary_sections.map(section => `
            <div class="alert alert-success mb-2">
                <h6 class="mb-1"><strong>${escapeHtml(section.section || 'N/A')}</strong></h6>
                <p class="mb-1 small">${escapeHtml(section.description || '')}</p>
                <p class="mb-0 small text-muted">Punishment: ${escapeHtml(section.punishment || 'N/A')}</p>
            </div>
        `).join('');
    } else {
        // Fallback for text response
        primarySections.innerHTML = `<div class="alert alert-info">${escapeHtml(String(analysis))}</div>`;
    }
    
    // Display classification
    const classification = document.getElementById('classification');
    if (typeof analysis === 'object' && analysis.offense_classification) {
        const cls = analysis.offense_classification;
        classification.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <strong>Bailable:</strong> ${cls.bailable ? '✅ Yes' : '❌ No'}
                </div>
                <div class="col-md-4">
                    <strong>Cognizable:</strong> ${cls.cognizable ? '✅ Yes' : '❌ No'}
                </div>
                <div class="col-md-4">
                    <strong>Compoundable:</strong> ${cls.compoundable ? '✅ Yes' : '❌ No'}
                </div>
            </div>
            <div class="mt-3">
                <strong>Triable By:</strong> ${escapeHtml(cls.triable_by || 'N/A')}
            </div>
        `;
    } else {
        classification.innerHTML = '<p class="text-muted">Classification information not available</p>';
    }
    
    // Display recommended actions
    const actions = document.getElementById('actions');
    if (typeof analysis === 'object' && analysis.recommended_actions) {
        actions.innerHTML = '<ul class="mb-0">' + 
            analysis.recommended_actions.map(action => 
                `<li>${escapeHtml(action)}</li>`
            ).join('') + 
            '</ul>';
    } else {
        actions.innerHTML = '<p class="text-muted">No specific actions recommended</p>';
    }
    
    results.style.display = 'block';
    results.scrollIntoView({behavior: 'smooth'});
}

function fillExample(text) {
    incidentDescription.value = text;
    incidentDescription.focus();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
