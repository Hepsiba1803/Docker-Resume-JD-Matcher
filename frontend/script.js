// Toggle Tooltip
function toggleTooltip(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.toggle('visible');
  }
}

const uploadForm = document.getElementById('uploadForm');
const resumeFileInput = document.getElementById('resumeFile');
const jdFileInput = document.getElementById('jdFile');
const statusEl = document.getElementById('status');
const resultsContainer = document.getElementById('results');
const analyzeBtn = document.getElementById('analyzeBtn');

// File input handlers for visual feedback
resumeFileInput.addEventListener('change', function(e) {
  const button = document.getElementById('resumeButton');
  const fileName = document.getElementById('resumeFileName');
  
  if (e.target.files.length > 0) {
    button.classList.add('has-file');
    fileName.textContent = e.target.files[0].name;
    button.querySelector('.upload-icon').textContent = '✅';
  } else {
    button.classList.remove('has-file');
    fileName.textContent = '';
    button.querySelector('.upload-icon').textContent = '📄';
  }
});

jdFileInput.addEventListener('change', function(e) {
  const button = document.getElementById('jdButton');
  const fileName = document.getElementById('jdFileName');
  
  if (e.target.files.length > 0) {
    button.classList.add('has-file');
    fileName.textContent = e.target.files[0].name;
    button.querySelector('.upload-icon').textContent = '✅';
  } else {
    button.classList.remove('has-file');
    fileName.textContent = '';
    button.querySelector('.upload-icon').textContent = '📋';
  }
});

// Sanitize object key
function sanitizeKey(key) {
  return key.replace(/\s+/g, '_');
}

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Reset UI
  statusEl.classList.remove('status-success');
  statusEl.textContent = '';
  resultsContainer.classList.add('placeholder');
  resultsContainer.textContent = "Results will be shown here after analysis.";
  resultsContainer.style.pointerEvents = 'none';

  // Validate fields
  if (!resumeFileInput.files.length) {
    statusEl.textContent = "Please upload a resume file.";
    return;
  }
  if (!jdFileInput.files.length) {
    statusEl.textContent = "Please upload a job description file.";
    return;
  }

  const resumeFile = resumeFileInput.files[0];
  const jdFile = jdFileInput.files[0];

  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  if (!allowedTypes.includes(resumeFile.type)) {
    statusEl.textContent = "Invalid resume file format. Please upload PDF or DOCX.";
    return;
  }

  if (!allowedTypes.includes(jdFile.type)) {
    statusEl.textContent = "Invalid job description file format. Please upload PDF or DOCX.";
    return;
  }

  // Show spinner
  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `<div class="spinner" aria-hidden="true"></div> Analyzing...`;

  // Prepare request
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('job_description', jdFile);

  try {
    const response = await fetch('/api/match-files', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error(`Upload failed with status ${response.status}`);

    const result = await response.json();
    if (!result) throw new Error("No results returned from server.");

    statusEl.textContent = "Analysis complete.";
    statusEl.classList.add('status-success');
    resultsContainer.classList.remove('placeholder');
    resultsContainer.style.pointerEvents = 'auto';

    renderResults(result);
  } catch (err) {
    statusEl.textContent = err.message || "Error processing the request.";
    resultsContainer.classList.add('placeholder');
    resultsContainer.textContent = "Results will be shown here after analysis.";
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Match";
  }
});

function renderResults(results) {
  resultsContainer.innerHTML = "";

  const keys = ["total", "missingkeywords", "sections", "formatting", "content quality", "context"];
  const emojiMap = {
    total: "🎯",
    missingkeywords: "❌",
    sections: "📄",
    formatting: "🛠️",
    "content quality": "✍️",
    context: "🧩"
  };

  keys.forEach((key) => {
    const item = results[key];
    if (!item) return;

    const card = document.createElement("div");
    card.className = "score-card";

    const header = `<div class="score-header">${emojiMap[key] || ""} ${item.type}</div>`;
    const score = `<div>Score: <span class="score-value">${item.score}</span></div>`;

    let missingHTML = "";
    if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
      missingHTML = `
        <div class="suggestions">
          <strong>Missing Keywords:</strong>
          <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
        </div>
      `;
    }

    let suggestionsHTML = "";
    let tooltipHTML = "";

    const suggestionsList = item.short_suggestions || item.suggestions;
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

    if (Array.isArray(item.long_suggestions) && item.long_suggestions.length > 0) {
      const tid = `${sanitizeKey(key)}-tooltip`;
      tooltipHTML = `
        <div class="tooltip-wrapper">
          <span class="tooltip-toggle" tabindex="0" role="button" aria-expanded="false" aria-controls="${tid}" onclick="toggleTooltip('${tid}')">💬 View Details</span>
          <div class="tooltip-content" id="${tid}" role="region" aria-live="polite">
            <ul>${item.long_suggestions.map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
        </div>
      `;
    }

    card.innerHTML = header + score + suggestionsHTML + tooltipHTML + missingHTML;
    resultsContainer.appendChild(card);
  });
}