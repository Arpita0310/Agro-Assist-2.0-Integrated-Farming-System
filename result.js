const data = JSON.parse(localStorage.getItem("agroResult"));

if (!data) {
  document.getElementById("plans").innerHTML = "No data found";
} else {

  // ================= HEADER =================
  document.getElementById("locationBox").innerHTML = `
    <div class="plan-card">
      <h3>${data.location?.district}</h3>
      <p><b>Zone:</b> ${data.location?.zone}</p>
      <p><b>Season:</b> ${data.input?.season}</p>
      <p><b>Temperature:</b> ${data.weather?.temperature}°C</p>
      <p><b>Soil pH:</b> ${data.soil?.ph}</p>
    </div>
  `;

  // ================= INCOME CHART =================
  new Chart(document.getElementById("incomeChart"), {
    type: "bar",
    data: {
      labels: data.plans.map(p => p.id),
      datasets: [{
        label: "Income Comparison",
        data: data.plans.map(p => p.metrics.income),
        backgroundColor: ["#2e7d32","#f9a825","#1565c0"]
      }]
    }
  });

  // ================= PLAN CARDS =================
  let html = "";

  data.plans.forEach(p => {

    html += `
    <div class="plan-card">

      <h3>${p.id} ⭐ ${p.score}</h3>

      <div class="section-box">
        <p><b>Crops:</b> ${p.crops.join(", ")}</p>
        <p><b>Tree:</b> ${p.tree}</p>
        <p><b>Flower:</b> ${p.flower}</p>
      </div>

      <div class="section-box">
        <p><b>Livestock:</b> ${p.livestock}</p>
        <p><b>Dairy:</b> ${p.dairy}</p>
      </div>

    </div>
    `;
  });

  document.getElementById("plans").innerHTML = html;

  // ================= EXTRA SYSTEMS =================
  document.getElementById("extras").innerHTML = `
    <div class="plan-card">
      <h3>🌾 Cropping Pattern</h3>
      <p>Mixed crop rotation recommended to maintain soil fertility and increase yield stability.</p>
    </div>

    <div class="plan-card">
      <h3>💧 Water Harvesting System</h3>
      <p>Construct farm ponds + drip irrigation suggested for water efficiency.</p>
    </div>

    <div class="plan-card">
      <h3>♻ Biogas + Manure System</h3>
      <p>Livestock waste → Biogas + Organic fertilizer cycle recommended.</p>
    </div>
  `;

  // ================= GOVT SUBSIDY =================
  document.getElementById("subsidyBox").innerHTML = `
    <div class="subsidy">
      <h3> Govt Subsidy Eligibility</h3>
      <p>PM-Kisan Samman Nidhi</p>
      <p>  Micro Irrigation Subsidy (up to 55%)</p>
      <p> Soil Health Card Scheme</p>
      <p> NABARD Farm Infrastructure Support</p>
    </div>
  `;

}

// ================= AI CHAT =================
document.getElementById("aiChatBtn").onclick = () => {
  const box = document.getElementById("chatBox");
  box.style.display = box.style.display === "block" ? "none" : "block";
};

document.getElementById("chatInput").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    const val = e.target.value;

    document.getElementById("chatLog").innerHTML += `
      <p><b>You:</b> ${val}</p>
      <p><b>AI:</b> This feature will be enhanced with ML chatbot soon.</p>
    `;

    e.target.value = "";
  }
});