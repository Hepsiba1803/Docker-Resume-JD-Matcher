document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  const resultsContainer = document.getElementById("results");
  const statusEl = document.getElementById("status");

  const showResults = (results) => {
    resultsContainer.innerHTML = "";

    const keys = [
      "total",
      "missingkeywords",
      "sections",
      "formatting",
      "content_quality",
      "context",
    ];

    keys.forEach((key) => {
      const item = results[key];
      if (!item) return;

      const card = document.createElement("div");
      card.className = "score-card";

      const header = `<div class="score-header">${item.type}</div>`;
      const score = `<div>Score: <span class="score-value">${item.score}</span></div>`;

      // Missing Keywords
      let missingHTML = "";
      if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
        missingHTML = `
          <div class="suggestions">
            <strong>Missing Keywords:</strong>
            <ul>${item.missing_keywords.map(k => `<li>${k}</li>`).join("")}</ul>
          </div>
        `;
      }

      // Short Suggestions
      let suggestionsHTML = "";
      const shortList = item.short_suggestions || item.suggestions;
      if (Array.isArray(shortList)) {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <ul>${shortList.map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
        `;
      } else if (typeof shortList === "string") {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <p>${shortList}</p>
          </div>
        `;
      }

      // Long Suggestions
      let tooltipHTML = "";
      if (Array.isArray(item.long_suggestions) && item.long_suggestions.length > 0) {
        const tid = `${key}-tooltip`;
        tooltipHTML = `
          <div class="tooltip-wrapper">
            <span class="tooltip-toggle" onclick="toggleTooltip('${tid}')">💬 Details</span>
            <div class="tooltip-content" id="${tid}">
              <ul>${item.long_suggestions.map(s => `<li>${s}</li>`).join("")}</ul>
            </div>
          </div>
        `;
      }

      card.innerHTML = header + score + suggestionsHTML + tooltipHTML + missingHTML;
      resultsContainer.appendChild(card);
    });
  };

  uploadForm.onsubmit = async (e) => {
    e.preventDefault();
    resultsContainer.innerHTML = "";
    statusEl.innerHTML = '<span class="loading">Uploading and analyzing...</span>';

    const resume = document.getElementById("resumeFile").files[0];
    const jd = document.getElementById("jdFile").files[0];

    if (!resume || !jd) {
      statusEl.innerHTML = '<span class="error">Please select both files.</span>';
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jd);

    try {
      const res = await fetch("/api/match-files", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Server error: " + res.statusText);
      const data = await res.json();
      showResults(data);
      statusEl.innerHTML = '<span class="loading">Done!</span>';
    } catch (err) {
      statusEl.innerHTML = `<span class="error">Error: ${err.message}</span>`;
    }
  };
});

function toggleTooltip(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle("visible");
}
