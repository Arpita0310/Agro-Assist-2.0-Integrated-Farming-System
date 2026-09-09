const STATES_DISTRICTS = {
  "Uttar Pradesh": ["Agra","Aligarh","Allahabad","Ambedkar Nagar","Amethi","Amroha","Auraiya","Azamgarh","Baghpat","Bahraich","Ballia","Balrampur","Banda","Barabanki","Bareilly","Basti","Bijnor","Budaun","Bulandshahr","Chandauli","Chitrakoot","Deoria","Etah","Etawah","Faizabad","Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar","Ghaziabad","Ghazipur","Gonda","Gorakhpur","Hamirpur","Hapur","Hardoi","Hathras","Jalaun","Jaunpur","Jhansi","Kannauj","Kanpur Dehat","Kanpur Nagar","Kasganj","Kaushambi","Kushinagar","Lakhimpur Kheri","Lalitpur","Lucknow","Maharajganj","Mahoba","Mainpuri","Mathura","Mau","Meerut","Mirzapur","Moradabad","Muzaffarnagar","Pilibhit","Pratapgarh","Raebareli","Rampur","Saharanpur","Sambhal","Sant Kabir Nagar","Shahjahanpur","Shamli","Shravasti","Siddharthnagar","Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi"],
  "Madhya Pradesh": ["Agar Malwa","Alirajpur","Anuppur","Ashoknagar","Balaghat","Barwani","Betul","Bhind","Bhopal","Burhanpur","Chhatarpur","Chhindwara","Damoh","Datia","Dewas","Dhar","Dindori","Guna","Gwalior","Harda","Hoshangabad","Indore","Jabalpur","Jhabua","Katni","Khandwa","Khargone","Mandla","Mandsaur","Morena","Narsinghpur","Neemuch","Niwari","Panna","Raisen","Rajgarh","Ratlam","Rewa","Sagar","Satna","Sehore","Seoni","Shahdol","Shajapur","Sheopur","Shivpuri","Sidhi","Singrauli","Tikamgarh","Ujjain","Umaria","Vidisha"],
  "Bihar": ["Araria","Arwal","Aurangabad","Banka","Begusarai","Bhagalpur","Bhojpur","Buxar","Darbhanga","East Champaran","Gaya","Gopalganj","Jamui","Jehanabad","Kaimur","Katihar","Khagaria","Kishanganj","Lakhisarai","Madhepura","Madhubani","Munger","Muzaffarpur","Nalanda","Nawada","Patna","Purnia","Rohtas","Saharsa","Samastipur","Saran","Sheikhpura","Sheohar","Sitamarhi","Siwan","Supaul","Vaishali","West Champaran"],
  "West Bengal": ["Alipurduar","Bankura","Birbhum","Cooch Behar","Dakshin Dinajpur","Darjeeling","Hooghly","Howrah","Jalpaiguri","Jhargram","Kalimpong","Kolkata","Malda","Murshidabad","Nadia","North 24 Parganas","Paschim Bardhaman","Paschim Medinipur","Purba Bardhaman","Purba Medinipur","Purulia","South 24 Parganas","Uttar Dinajpur"]
};

document.addEventListener("DOMContentLoaded", () => {

  const stateSelect = document.getElementById("state");
  const districtSelect = document.getElementById("district");
  const form = document.getElementById("farmForm");
  const submitBtn = form.querySelector("button");

  const landInput = document.getElementById("landArea"); // ✅ NEW

  // ================= STATES =================
  function loadStates() {
    stateSelect.innerHTML = `<option value="">Select State</option>`;
    Object.keys(STATES_DISTRICTS).forEach(s => {
      let opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      stateSelect.appendChild(opt);
    });
  }

  // ================= DISTRICTS =================
  function loadDistricts(state) {
    districtSelect.innerHTML = `<option value="">Select District</option>`;
    (STATES_DISTRICTS[state] || []).forEach(d => {
      let opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      districtSelect.appendChild(opt);
    });
  }

  loadStates();

  stateSelect.addEventListener("change", () => {
    loadDistricts(stateSelect.value);
  });

  // ❌ AUTO COMPLETE REMOVED COMPLETELY

  // ================= FORM SUBMIT =================
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      state: stateSelect.value,
      district: districtSelect.value,
      budget: document.getElementById("budget").value,
      season: document.getElementById("season").value,
      land_area: landInput.value   // ✅ NEW ADDED
    };

    if (!payload.state || !payload.district) {
      alert("Select state and district");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Generating...";

    try {
      const res = await fetch("/get_recommendation", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      localStorage.setItem("agroResult", JSON.stringify({
        location: data.location,
        input: payload,
        plans: data.plans,
        weather: data.weather,
        soil: data.soil,
        graph: data.graph
      }));

      window.location.href = "/result";

    } catch (err) {
      alert("Server error");
    }

    submitBtn.disabled = false;
    submitBtn.innerText = "Generate Smart Plan";
  });

});


