const showResults = (results) => {
  const container = document.getElementById("results");
  container.innerHTML = "";

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

    // Handle missing keywords if present
    let missingHTML = "";
    if (Array.isArray(item.missing_keywords) && item.missing_keywords.length > 0) {
      missingHTML = `
        <div class="suggestions">
          <strong>Missing Keywords:</strong>
          <ul>
            ${item.missing_keywords.map((k) => `<li>${k}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    // Handle short suggestions (array or string)
    let suggestionsHTML = "";
    const shortList = item.short_suggestions || item.suggestions;

    if (Array.isArray(shortList)) {
      suggestionsHTML = `
        <div class="suggestions">
          <strong>Suggestions:</strong>
          <ul>
            ${shortList.map((s) => `<li>${s}</li>`).join("")}
          </ul>
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

    // Long suggestions (toggleable tooltip)
    let tooltipHTML = "";
    if (Array.isArray(item.long_suggestions)) {
      const tooltipId = `${key}-tooltip`;
      tooltipHTML = `
        <div class="tooltip-wrapper">
          <span class="tooltip-toggle" onclick="toggleTooltip('${tooltipId}')">💬 Details</span>
          <div class="tooltip-content" id="${tooltipId}">
            <ul>
              ${item.long_suggestions.map((s) => `<li>${s}</li>`).join("")}
            </ul>
          </div>
        </div>
      `;
    }

    card.innerHTML = header + score + suggestionsHTML + tooltipHTML + missingHTML;
    container.appendChild(card);
  });
};

function toggleTooltip(id) {
  const el = document.getElementById(id);
  el.classList.toggle("visible");
}

document.getElementById("uploadForm").onsubmit = async function (e) {
  e.preventDefault();

  document.getElementById("results").innerHTML = "";
  document.getElementById("status").innerHTML =
    '<span class="loading">Uploading and analyzing...</span>';

  const resumeFile = document.getElementById("resumeFile").files[0];
  const jdFile = document.getElementById("jdFile").files[0];

  if (!resumeFile || !jdFile) {
    document.getElementById("status").innerHTML =
      '<span class="error">Please select both files.</span>';
    return;
  }

  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jdFile);

  try {
    const response = await fetch("/api/match-files", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Server error: " + response.statusText);

    const data = await response.json();
    showResults(data);
    document.getElementById("status").innerHTML = '<span class="loading">Done!</span>';
  } catch (err) {
    document.getElementById("status").innerHTML =
      '<span class="error">Error: ' + err.message + "</span>";
  }
};
