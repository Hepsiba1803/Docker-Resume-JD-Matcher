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

    // Determine which suggestion lists to use
    // context and content_quality have both short_suggestions and long_suggestions
    // others have only one suggestions list (either 'suggestions' or 'short_suggestions')
    let suggestionsHTML = "";
    let tooltipHTML = "";

    if ((key === "context" || key === "content_quality") &&
        Array.isArray(item.short_suggestions) && item.short_suggestions.length > 0) {
      // Context and content_quality: show short suggestions
      suggestionsHTML = `
        <div class="suggestions">
          <strong>Suggestions:</strong>
          <ul>${item.short_suggestions.map(s => `<li>${s}</li>`).join("")}</ul>
        </div>
      `;

      // Show long suggestions if exist for Details toggle
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
    } else {
      // For other sections: get suggestions either from 'suggestions' or 'short_suggestions'
      const suggestionsList = item.suggestions || item.short_suggestions;

      if (Array.isArray(suggestionsList) && suggestionsList.length > 0) {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <ul>${suggestionsList.map(s => `<li>${s}</li>`).join("")}</ul>
          </div>
        `;
      } else if (typeof suggestionsList === "string") {
        suggestionsHTML = `
          <div class="suggestions">
            <strong>Suggestions:</strong>
            <p>${suggestionsList}</p>
          </div>
        `;
      }
      // No details toggle here since no long suggestions expected
    }

    card.innerHTML = header + score + suggestionsHTML + tooltipHTML + missingHTML;
    resultsContainer.appendChild(card);
  });
};
