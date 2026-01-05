async function getRecommendations() {
  const campaignId = document.getElementById("campaignId").value;
  const errorDiv = document.getElementById("error");
  const tableBody = document.getElementById("resultsBody");

  errorDiv.textContent = "";
  tableBody.innerHTML = "";

  if (!campaignId) {
    errorDiv.textContent = "Please enter a Campaign ID.";
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/recommend/${campaignId}`
    );

    if (!response.ok) {
      throw new Error("No recommendations found.");
    }

    const data = await response.json();

    data.recommendations.forEach(rec => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${rec.rank}</td>
        <td>${rec.channel_name || "N/A"}</td>
        <td>${rec.score.toFixed(3)}</td>
        <td>${rec.confidence.toFixed(2)}</td>
      `;

      tableBody.appendChild(row);
    });

  } catch (error) {
    errorDiv.textContent = error.message;
  }
}
