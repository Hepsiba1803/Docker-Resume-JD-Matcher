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
  const uploadIcon = button.querySelector('.upload-icon');
  
  if (e.target.files.length > 0) {
    button.classList.add('has-file');
    fileName.textContent = e.target.files[0].name;
    uploadIcon.textContent = '✅';
    
    // Add success animation
    button.style.transform = 'scale(1.02)';
    setTimeout(() => {
      button.style.transform = '';
    }, 200);
  } else {
    button.classList.remove('has-file');
    fileName.textContent = '';
    uploadIcon.textContent = '📄';
  }
});

jdFileInput.addEventListener('change', function(e) {
  const button = document.getElementById('jdButton');
  const fileName = document.getElementById('jdFileName');
  const uploadIcon = button.querySelector('.upload-icon');
  
  if (e.target.files.length > 0) {
    button.classList.add('has-file');
    fileName.textContent = e.target.files[0].name;
    uploadIcon.textContent = '✅';
    
    // Add success animation
    button.style.transform = 'scale(1.02)';
    setTimeout(() => {
      button.style.transform = '';
    }, 200);
  } else {
    button.classList.remove('has-file');
    fileName.textContent = '';
    uploadIcon.textContent = '📋';
  }
});

// Add click handlers for file input buttons
document.getElementById('resumeButton').addEventListener('click', function() {
  resumeFileInput.click();
});

document.getElementById('jdButton').addEventListener('click', function() {
  jdFileInput.click();
});

// Add drag and drop functionality
function setupDragAndDrop(buttonId, inputId) {
  const button = document.getElementById(buttonId);
  const input = document.getElementById(inputId);
  
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    button.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  ['dragenter', 'dragover'].forEach(eventName => {
    button.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    button.addEventListener(eventName, unhighlight, false);
  });
  
  function highlight(e) {
    button.style.borderColor = '#4299e1';
    button.style.backgroundColor = '#ebf8ff';
  }
  
  function unhighlight(e) {
    button.style.borderColor = '';
    button.style.backgroundColor = '';
  }
  
  button.addEventListener('drop', handleDrop, false);
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      input.files = files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
}

// Initialize drag and drop for both file inputs
setupDragAndDrop('resumeButton', 'resumeFile');
setupDragAndDrop('jdButton', 'jdFile');

// Sanitize object key
function sanitizeKey(key) {
  return key.replace(/\s+/g, '_');
}

// Helper function to convert long suggestions to bullet points
function formatLongSuggestions(longSuggestions) {
  if (!longSuggestions || longSuggestions.length === 0) {
    return '';
  }

  // Convert array of long suggestions to bullet points
  const bulletPoints = longSuggestions.map(suggestion => {
    // Split long suggestion into sentences for better readability
    const sentences = suggestion.split('. ').filter(s => s.trim().length > 0);
    
    if (sentences.length === 1) {
      // If it's just one sentence, return as single bullet point
      return `<li>${sentences[0].trim()}${sentences[0].endsWith('.') ? '' : '.'}</li>`;
    } else {
      // If multiple sentences, create a main bullet with sub-points
      const mainPoint = sentences[0] + '.';
      const subPoints = sentences.slice(1).map(s => 
        `<li class="sub-point">${s.trim()}${s.endsWith('.') ? '' : '.'}</li>`
      ).join('');
      
      return `<li>${mainPoint}${subPoints ? `<ul class="sub-list">${subPoints}</ul>` : ''}</li>`;
    }
  }).join('');

  return bulletPoints;
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


    // MODIFIED SECTION: Special handling for missingkeywords section
    if (key === "missingkeywords") {
      // For keyword section, show missing keywords first, then suggestion with spacing
      if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
        missingHTML = `
          <div class="suggestions">
            <strong>Missing Keywords:</strong>
            <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
          </div>
        `;
      }
      
      suggestionsHTML = `
        <div class="suggestions" style="margin-top: 1rem;">
          <strong>Suggestions:</strong>
          <p style="margin-top: 0.5rem;">💡 Add these terms somewhere in your resume to improve ATS compatibility</p>
        </div>
      `;
    } else {
      // For all other sections, use the original logic
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
      
      // Handle missing keywords for other sections
      if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
        missingHTML = `
          <div class="suggestions">
            <strong>Missing Keywords:</strong>
            <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
          </div>
        `;
      }
    }
    // END MODIFIED SECTION

    if (Array.isArray(item.long_suggestions) && item.long_suggestions.length > 0) {
      const tid = `${sanitizeKey(key)}-tooltip`;
      const formattedLongSuggestions = formatLongSuggestions(item.long_suggestions);
      
      tooltipHTML = `
        <div class="tooltip-wrapper">
          <span class="tooltip-toggle" tabindex="0" role="button" aria-expanded="false" aria-controls="${tid}" onclick="toggleTooltip('${tid}')">💬 View Details</span>
          <div class="tooltip-content" id="${tid}" role="region" aria-live="polite">
            <ul class="detailed-suggestions">${formattedLongSuggestions}</ul>
          </div>
        </div>
      `;
    }

    card.innerHTML = header + score + missingHTML + suggestionsHTML + tooltipHTML;
    resultsContainer.appendChild(card);
  });
}