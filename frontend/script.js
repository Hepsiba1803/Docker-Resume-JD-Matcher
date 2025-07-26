// Helper: toggle tooltip visibility
function toggleTooltip(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.toggle('visible');
  }
}

const uploadForm = document.getElementById('uploadForm');
const resumeFileInput = document.getElementById('resumeFile');
const jdTextInput = document.getElementById('jdText');
const statusEl = document.getElementById('status');
const resultsContainer = document.getElementById('results');
const analyzeBtn = document.getElementById('analyzeBtn');

// Utility: sanitize key for id usage (replace spaces with underscores)
function sanitizeKey(key) {
  return key.replace(/\s+/g, '_');
}

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  statusEl.classList.remove('status-success');
  statusEl.textContent = '';
  resultsContainer.classList.add('placeholder');
  resultsContainer.textContent = "Results will be shown here after analysis.";
  resultsContainer.style.pointerEvents = 'none'; // disable interactions during upload

  // Validate inputs
  if (!resumeFileInput.files.length) {
    statusEl.textContent = "Please upload a resume file.";
    return;
  }
  if (!jdTextInput.value.trim()) {
    statusEl.textContent = "Please enter a job description.";
    return;
  }

  // Check file extension
  const file = resumeFileInput.files[0];
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];
  if (!allowedTypes.includes(file.type)) {
    statusEl.textContent = "Invalid resume file format. Please upload PDF or DOCX.";
    return;
  }

  // Disable button and show spinner
  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `<div class="spinner" aria-hidden="true"></div> Analyzing...`;

  // Prepare form data
  const formData = new FormData();
  formData.append('resume', file);
  // Instead of file for JD, send text field content as a Blob with .txt extension:
  formData.append('job_description', new Blob([jdTextInput.value.trim()], {type: 'text/plain'}), 'job_description.txt');

  try {
    const response = await fetch('/api/match-files', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    const result = await response.json();
    if (!result) {
      throw new Error("No results returned from server.");
    }

    statusEl.textContent = "Analysis complete.";
    statusEl.classList.add('status-success');
    resultsContainer.classList.remove('placeholder');
    resultsContainer.style.pointerEvents = 'auto';

    showResults(result);
  } catch (err) {
    console.error(err);
    statusEl.textContent = err.message || "Error uploading files or processing response.";
    resultsContainer.classList.add('placeholder');
    resultsContainer.textContent = "Results will be shown here after analysis.";
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Match";
  }
});


function showResults(results) {
  resultsContainer.innerHTML = "";

  const keys = [
    "total",
    "missingkeywords",
    "sections",
    "formatting",
    "content quality",
    "context",
  ];

  keys.forEach((key) => {
    const item = results[key];
    if (!item) return;

    const card = document.createElement("div");
    card.className = "score-card";

    const header = `<div class="score-header">${item.type}</div>`;
    const score = `<div>Score: <span class="score-value">${item.score}</span></div>`;

    // Handle missing keywords section specifically
    let missingHTML = "";
    if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
      missingHTML = `
        <div class="suggestions">
          <strong>Missing Keywords:</strong>
          <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
        </div>
      `;
    }

    const safeKey = sanitizeKey(key);

    let suggestionsHTML = "";
    let tooltipHTML = "";

    if ((key === "context" || key === "content quality") &&
        Array.isArray(item.short_suggestions) && item.short_suggestions.length > 0) {

      suggestionsHTML = `
        <div class="suggestions">
          <strong>Suggestions:</strong>
          <ul>${item.short_suggestions.map(s => `<li>${s}</li>`).join("")}</ul>
        </div>
      `;

      if (Array.isArray(item.long_suggestions) && item.long_suggestions.length > 0) {
        const tid = `${safeKey}-tooltip`;
        tooltipHTML = `
          <div class="tooltip-wrapper">
            <span class="tooltip-toggle" tabindex="0" role="button" aria-expanded="false" aria-controls="${tid}" onclick="toggleTooltip('${tid}')">💬 Details</span>
            <div class="tooltip-content" id="${tid}" role="region" aria-live="polite">
              <ul>${item.long_suggestions.map(s => `<li>${s}</li>`).join("")}</ul>
            </div>
          </div>
        `;
      }
    } else {
      const suggestionsList = item.suggestions || item.short_suggestions;

      if (Array.isArray(suggestionsList) && suggestionsList.length > 0) {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <ul>${suggestionsList.map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
        `;
      } else if (typeof suggestionsList === 'string') {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <p>${suggestionsList}</p>
          </div>
        `;
      }
    }

    card.innerHTML = header + score + suggestionsHTML + tooltipHTML + missingHTML;
    resultsContainer.appendChild(card);
  });
}
