document.addEventListener("DOMContentLoaded", () => {
  let currentMode = "regex";

  const regexBtn = document.getElementById("regexBtn");
  const semanticBtn = document.getElementById("semanticBtn");
  const runBtn = document.getElementById("runBtn");
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("resultText");
  const historyBox = document.getElementById("historyBox");
  const historyContent = document.getElementById("historyContent");
  const textInput = document.getElementById("inputText");
  const patternInput = document.getElementById("pattern");

  // Mode toggle buttons
  regexBtn.addEventListener("click", () => {
    currentMode = "regex";
    regexBtn.classList.add("active");
    semanticBtn.classList.remove("active");
    patternInput.placeholder = "e.g. \\d+ or [A-Z]+";
  });

  semanticBtn.addEventListener("click", () => {
    currentMode = "semantic";
    semanticBtn.classList.add("active");
    regexBtn.classList.remove("active");
    patternInput.placeholder = "e.g. happy or positive";
  });

  // Run search
  runBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();
    const pattern = patternInput.value.trim();

    if (!text || !pattern) {
      alert("Please enter both text and pattern/keyword.");
      return;
    }

    const url = currentMode === "regex" ? "/search" : "/semantic";
    const payload = currentMode === "regex"
      ? { pattern, text }
      : { keyword: pattern, text };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      // Show results
      resultBox.classList.remove("hidden");
      resultText.textContent = data.matches?.length
        ? (currentMode === "semantic"
            ? data.matches.map(m => `${m.word} (${m.similarity})`).join("\n")
            : data.matches.join("\n"))
        : "No matches found.";

      // Show history
      if (data.history && data.history.length) {
        historyBox.classList.remove("hidden");
        historyContent.innerHTML = data.history.map(h => `
          <div class="history-item">
            <strong>${h.pattern}</strong> → ${h.matches} matches
            <small>(${h.timestamp})</small>
          </div>
        `).join("");
      }
    } catch (err) {
      resultBox.classList.remove("hidden");
      resultText.textContent = `Error: ${err.message}`;
    }
  });
});