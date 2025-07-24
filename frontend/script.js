// script.js

const showResults = (results) => {
  const container = document.getElementById('results');
  container.innerHTML = '';

  results.forEach(item => {
    const card = document.createElement('div');
    card.className = 'score-card';

    // Suggestions
    let suggestionHTML = '';
    if (item.short_suggestions && Array.isArray(item.short_suggestions)) {
      suggestionHTML = '<ul>' + item.short_suggestions.map(s => `<li>${s}</li>`).join('') + '</ul>';
    } else if (item.suggestions) {
      if (Array.isArray(item.suggestions)) {
        suggestionHTML = '<ul>' + item.suggestions.map(s => `<li>${s}</li>`).join('') + '</ul>';
      } else {
        suggestionHTML = `<p>${item.suggestions}</p>`;
      }
    }

    // Missing keywords
    let missingHTML = '';
    if (item.missing_keywords && item.missing_keywords.length > 0) {
      missingHTML = `
        <div class="suggestions">
          <strong>Missing Keywords:</strong>
          <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join('')}</ul>
        </div>
      `;
    }

    // Tooltip icon if long suggestions exist
    let tooltipIcon = '';
    if (item.long_suggestions && item.long_suggestions.length > 0) {
      tooltipIcon = `<span class="tooltip-icon" onclick="showTooltipModal(${JSON.stringify(item.long_suggestions).replace(/"/g, '&quot;')})">
        <i class="fas fa-question-circle"></i>
      </span>`;
    }

    card.innerHTML = `
      <div class="score-header">
        ${item.type} ${tooltipIcon}
      </div>
      <div>Score: <span class="score-value">${item.score}</span></div>
      <div class="suggestions">
        <strong>Suggestions:</strong>
        ${suggestionHTML}
      </div>
      ${missingHTML}
    `;

    container.appendChild(card);
  });
};

function showTooltipModal(suggestions) {
  const modal = document.getElementById('tooltipModal');
  const content = document.getElementById('tooltipContent');
  content.innerHTML = '<ul>' + suggestions.map(s => `<li>${s}</li>`).join('') + '</ul>';
  modal.style.display = 'block';
}

function closeModal() {
  document.getElementById('tooltipModal').style.display = 'none';
}

document.getElementById('uploadForm').onsubmit = async function (e) {
  e.preventDefault();
  document.getElementById('results').innerHTML = '';
  document.getElementById('status').innerHTML = '<span class="loading">Uploading and analyzing...</span>';

  const resumeFile = document.getElementById('resumeFile').files[0];
  const jdFile = document.getElementById('jdFile').files[0];
  if (!resumeFile || !jdFile) {
    document.getElementById('status').innerHTML = '<span class="error">Please select both files.</span>';
    return;
  }

  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('job_description', jdFile);

  try {
    const response = await fetch('/api/match-files', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Server error: ' + response.statusText);
    const data = await response.json();
    const resultsArray = Array.isArray(data) ? data : Object.values(data);
    showResults(resultsArray);
    document.getElementById('status').innerHTML = '<span class="loading">Done!</span>';
  } catch (err) {
    document.getElementById('status').innerHTML = '<span class="error">Error: ' + err.message + '</span>';
  }
};
