/**
 * F11: Legal Precedent & Case Similarity Engine - Frontend
 */

let precedentData = null;

async function findPrecedents() {
    const loadingEl = document.getElementById('precedentsLoading');
    const emptyEl = document.getElementById('precedentsEmpty');
    const resultsEl = document.getElementById('precedentsResults');
    const btnEl = document.getElementById('findPrecedentsBtn');
    
    // Show loading state
    loadingEl.classList.remove('hidden');
    emptyEl.classList.add('hidden');
    resultsEl.classList.add('hidden');
    btnEl.disabled = true;
    btnEl.textContent = 'Searching...';
    
    try {
        const response = await fetch(`/ai/compare-precedents/${CASE_ID}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to find precedents');
        }
        
        precedentData = data;
        displayPrecedents(data);
        
    } catch (error) {
        console.error('Error finding precedents:', error);
        alert('Failed to find similar precedents: ' + error.message);
        emptyEl.classList.remove('hidden');
    } finally {
        loadingEl.classList.add('hidden');
        btnEl.disabled = false;
        btnEl.textContent = 'Refresh Results';
    }
}

function displayPrecedents(data) {
    const similarCasesList = document.getElementById('similarCasesList');
    const comparisonReport = document.getElementById('comparisonReport');
    const resultsEl = document.getElementById('precedentsResults');
    const emptyEl = document.getElementById('precedentsEmpty');

    if (!data.similar_cases || data.similar_cases.length === 0) {
        emptyEl.classList.remove('hidden');
        return;
    }

    // Calculate average similarity
    const avgSim = data.similar_cases.reduce((sum, c) => sum + c.relevance_score, 0) / data.similar_cases.length;
    document.getElementById('avgSimilarity').textContent = avgSim.toFixed(1) + '%';
    document.getElementById('precedentCount').textContent = data.similar_cases.length;
    
    // Display similar cases with modern card design
    similarCasesList.innerHTML = data.similar_cases.map((precedent, index) => {
        // Determine match level for color coding
        const score = precedent.relevance_score;
        let matchBadge, matchColor;
        if (score >= 80) {
            matchBadge = 'Excellent Match';
            matchColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
        } else if (score >= 60) {
            matchBadge = 'Good Match';
            matchColor = 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
        } else {
            matchBadge = 'Moderate Match';
            matchColor = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
        }

        return `
        <article class="group rounded-2xl border border-slate-700 bg-gradient-to-br from-slate-900 to-slate-950 p-5 transition-all hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10">
            <div class="mb-3 flex items-start justify-between gap-3">
                <div class="flex items-start gap-3 flex-1">
                    <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 text-sm font-bold text-white shadow-lg">
                        ${index + 1}
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="mb-1 font-bold text-white text-base truncate">${escapeHtml(precedent.case_number)}</h3>
                        <p class="text-sm leading-relaxed text-slate-300 line-clamp-2">${escapeHtml(precedent.title)}</p>
                    </div>
                </div>
                <div class="flex flex-col items-end gap-2 shrink-0">
                    <div class="flex items-center gap-1 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-600/20 px-3 py-1 text-xs font-bold text-cyan-300">
                        <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                        </svg>
                        ${precedent.relevance_score}%
                    </div>
                    <span class="rounded border ${matchColor} px-2 py-0.5 text-xs font-semibold">
                        ${matchBadge}
                    </span>
                </div>
            </div>

            <div class="mb-3 grid grid-cols-2 gap-3 rounded-xl border border-slate-700/50 bg-slate-950/50 p-3 text-xs">
                <div>
                    <p class="mb-1 font-medium text-slate-500">Type</p>
                    <p class="font-semibold text-white">${precedent.case_type}</p>
                </div>
                <div>
                    <p class="mb-1 font-medium text-slate-500">Court</p>
                    <p class="font-semibold text-white truncate">${escapeHtml(precedent.court)}</p>
                </div>
                <div>
                    <p class="mb-1 font-medium text-slate-500">Date</p>
                    <p class="font-semibold text-white">${precedent.judgment_date}</p>
                </div>
                <div>
                    <p class="mb-1 font-medium text-slate-500">Sections</p>
                    <p class="font-semibold text-cyan-400 truncate">${escapeHtml(precedent.key_sections || 'N/A')}</p>
                </div>
            </div>

            <details class="group/details">
                <summary class="flex cursor-pointer items-center justify-between rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-cyan-400 transition-colors hover:border-cyan-500/50 hover:bg-slate-900">
                    <span>View Full Details</span>
                    <svg class="h-4 w-4 transition-transform group-open/details:rotate-180" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                    </svg>
                </summary>
                <div class="mt-3 space-y-3 rounded-xl border border-slate-700/50 bg-slate-900/30 p-4">
                    <div>
                        <div class="mb-2 flex items-center gap-2">
                            <svg class="h-4 w-4 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Case Description</p>
                        </div>
                        <p class="text-sm leading-relaxed text-slate-300">${escapeHtml(precedent.description)}</p>
                    </div>
                    <div class="border-t border-slate-700 pt-3">
                        <div class="mb-2 flex items-center gap-2">
                            <svg class="h-4 w-4 text-emerald-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <p class="text-xs font-bold uppercase tracking-wide text-emerald-400">Judgment Outcome</p>
                        </div>
                        <p class="text-sm font-medium text-emerald-300">${escapeHtml(precedent.outcome)}</p>
                    </div>
                </div>
            </details>
        </article>
    `;
    }).join('');
    
    // Display AI comparison report with markdown formatting
    comparisonReport.innerHTML = formatMarkdownToHTML(data.comparison_report);
    
    // Show results
    resultsEl.classList.remove('hidden');
    emptyEl.classList.add('hidden');
    
    // Scroll to results
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function formatMarkdownToHTML(markdown) {
    if (!markdown) return '';
    
    let html = markdown
        // Headers
        .replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold text-cyan-300 mt-4 mb-2">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-white mt-6 mb-3">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-white mt-6 mb-3">$1</h1>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
        // Bullet lists
        .replace(/^\* (.*$)/gim, '<li class="ml-4">$1</li>')
        .replace(/^- (.*$)/gim, '<li class="ml-4">$1</li>')
        // Numbered lists
        .replace(/^\d+\. (.*$)/gim, '<li class="ml-4">$1</li>')
        // Wrap consecutive <li> in <ul>
        .replace(/(<li.*<\/li>\n?)+/g, function(match) {
            return '<ul class="list-disc space-y-1 my-2">' + match + '</ul>';
        })
        // Line breaks
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-load on page if needed
document.addEventListener('DOMContentLoaded', function() {
    // Optional: Auto-find precedents on page load
    // findPrecedents();
});
