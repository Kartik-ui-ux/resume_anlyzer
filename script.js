document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const resumeFile = document.getElementById("resume").files[0];
  const jobDesc = document.getElementById("jobDesc").value.trim();
  const spinner = document.getElementById("spinner");
  const resultsSection = document.getElementById("results");

  if (!resumeFile) {
    alert("Please upload a resume file.");
    return;
  }

  // Show spinner, hide results
  spinner.style.display = "flex";
  resultsSection.style.display = "none";

  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDesc);

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    spinner.style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    // Fade in results
    resultsSection.style.opacity = 0;
    resultsSection.style.display = "block";
    setTimeout(() => {
      resultsSection.style.transition = "opacity 0.6s cubic-bezier(.4,0,.2,1)";
      resultsSection.style.opacity = 1;
    }, 50);

    document.getElementById("summary").textContent = data.summary;
    document.getElementById("score").textContent = `${data.score} / 10`;
    document.getElementById("match_score").textContent =
      data.match_score !== null ? `Job Match: ${data.match_score}%` : "";


    // Show keywords, probability, and template
    const feedbackList = document.getElementById("feedback");
    let keywordsDiv = document.getElementById("keywords");
    if (!keywordsDiv) {
      keywordsDiv = document.createElement("div");
      keywordsDiv.id = "keywords";
      keywordsDiv.className = "keywords-section";
      resultsSection.insertBefore(keywordsDiv, feedbackList);
    }
    let probHtml = data.probability !== undefined ? `<h2>📈 Selection Probability</h2><p>${data.probability}%</p>` : "";
    let templateHtml = data.template ? `<h2>📄 Resume Template Suggestion</h2><p><b>${data.template}</b></p><pre style='white-space:pre-wrap;'>${data.template_text || ""}</pre>` : "";
    keywordsDiv.innerHTML = `
      <h2>🔑 Top Keywords</h2><p>${(data.keywords || []).join(", ")}</p>
      ${probHtml}
      ${templateHtml}
    `;

    feedbackList.innerHTML = "";
    (data.feedback || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      feedbackList.appendChild(li);
    });

    // Download button
    document.getElementById("downloadBtn").onclick = async () => {
      const res = await fetch("/download-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        alert("Failed to download report.");
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Resume_Report.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    };
    // Accessibility: focus results
    resultsSection.setAttribute("tabindex", "-1");
    resultsSection.focus();
  } catch (err) {
    spinner.style.display = "none";
    alert("Something went wrong: " + err.message);
  }
});
