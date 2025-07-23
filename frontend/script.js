// script.js

const showResults = (results) => {
  const container = document.getElementById('results');
  container.innerHTML = '';

  results.forEach(item => {
    const card = document.createElement('div');
    card.className = 'score-card';

    // Build Suggestions HTML
    let suggestionHTML = '';
    if (Array.isArray(item.suggestions)) {
      suggestionHTML = '<ul>' + item.suggestions.map(s => `<li>${s}</li>`).join('') + '</ul>';
    } else {
      suggestionHTML = `<p>${item.suggestions}</p>`;
    }

    // Build Missing Keywords HTML only if present
    let missingHTML = '';
    if ('missing_keywords' in item && Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
      missingHTML = `
        <div class="suggestions">
          <strong>Missing Keywords:</strong>
          <ul>
            ${item.missing_keywords.map(k => `<li>${k}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    // Final HTML for one card
    card.innerHTML = `
      <div class="score-header">${item.type}</div>
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
    {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error('Server error: ' + response.statusText);

    const data = await response.json();

    // Ensure it's always treated as an array
    const resultsArray = Array.isArray(data) ? data : Object.values(data);

    showResults(resultsArray);
    document.getElementById('status').innerHTML = '<span class="loading">Done!</span>';
  } catch (err) {
    document.getElementById('status').innerHTML = '<span class="error">Error: ' + err.message + '</span>';
  }
};
