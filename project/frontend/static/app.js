/**
 * SoilSense Platform — app.js
 * Comprehensive Frontend Controller
 */
"use strict";

/* ══════════════════ GLOBAL STATE ══════════════════════════ */
let lastPayload     = null;
let lastCnnResult   = null;
let lastWeather     = null;
let currentLang     = "en";
let currentDatasetPage = 1;
let datasetSearchTimer = null;
let leafletMapInstance = null;
let mapMarkers = [];

// Mini Chart instances on Dashboard
let miniChartHealthInstance   = null;
let miniChartRainfallInstance = null;

// Full Page Chart instances
let chartHealthInstance = null;
let chartPhInstance     = null;
let chartYieldInstance  = null;

// Crop Economic & Agronomic Database (Profit, Duration, Water, Season)
const CROP_AGRO_ECONOMICS = {
  "muskmelon":  { profit: "₹85,000 / acre", days: "80 – 90 days",  water: "Low to Moderate", season: "Zaid / Summer", emoji: "🍈" },
  "watermelon": { profit: "₹75,000 / acre", days: "85 – 95 days",  water: "Low to Moderate", season: "Zaid / Summer", emoji: "🍉" },
  "tomato":     { profit: "₹95,000 / acre", days: "70 – 85 days",  water: "Moderate",        season: "All Season",    emoji: "🍅" },
  "maize":      { profit: "₹60,000 / acre", days: "95 – 110 days", water: "Moderate",        season: "Kharif / Rabi", emoji: "🌽" },
  "rice":       { profit: "₹55,000 / acre", days: "115 – 135 days",water: "High (Flooded)",  season: "Kharif",        emoji: "🌾" },
  "cotton":     { profit: "₹70,000 / acre", days: "150 – 180 days",water: "Moderate",        season: "Kharif",        emoji: "☁️" },
  "grapes":     { profit: "₹1,80,000 / acre", days: "Perennial",   water: "Drip Irrigation", season: "Rabi / Summer", emoji: "🍇" },
  "banana":     { profit: "₹1,40,000 / acre", days: "11 – 12 months", water: "High",         season: "Perennial",     emoji: "🍌" },
  "mango":      { profit: "₹1,20,000 / acre", days: "Perennial",   water: "Moderate",        season: "Summer",        emoji: "🥭" },
  "orange":     { profit: "₹1,10,000 / acre", days: "Perennial",   water: "Moderate",        season: "Winter / Spring", emoji: "🍊" },
  "apple":      { profit: "₹2,00,000 / acre", days: "Perennial",   water: "Moderate",        season: "Autumn",        emoji: "🍎" },
  "chickpea":   { profit: "₹48,000 / acre", days: "90 – 105 days", water: "Low (Rainfed)",   season: "Rabi",          emoji: "🫘" },
  "kidneybeans":{ profit: "₹52,000 / acre", days: "100 – 120 days",water: "Moderate",        season: "Kharif / Rabi", emoji: "🫘" },
  "pigeonpeas": { profit: "₹50,000 / acre", days: "140 – 180 days",water: "Low (Drought Hardy)", season: "Kharif",   emoji: "🌱" },
  "mothbeans":  { profit: "₹38,000 / acre", days: "65 – 75 days",  water: "Very Low",        season: "Kharif",        emoji: "🌿" },
  "mungbean":   { profit: "₹42,000 / acre", days: "60 – 70 days",  water: "Low",             season: "Kharif / Zaid", emoji: "🌱" },
  "blackgram":  { profit: "₹44,000 / acre", days: "70 – 80 days",  water: "Low to Moderate", season: "Kharif",        emoji: "🫘" },
  "lentil":     { profit: "₹46,000 / acre", days: "105 – 120 days",water: "Low",             season: "Rabi",          emoji: "🥣" },
  "pomegranate":{ profit: "₹1,60,000 / acre", days: "Perennial",   water: "Low to Moderate", season: "Perennial",     emoji: "🍎" },
  "papaya":     { profit: "₹1,30,000 / acre", days: "9 – 10 months", water: "High",          season: "All Season",    emoji: "🍈" },
  "coconut":    { profit: "₹90,000 / acre", days: "Perennial",     water: "High",            season: "Coastal",       emoji: "🥥" },
  "jute":       { profit: "₹48,000 / acre", days: "120 – 150 days",water: "High",            season: "Kharif",        emoji: "🧵" },
  "coffee":     { profit: "₹1,50,000 / acre", days: "Perennial",   water: "High (Hill Humus)",season: "Perennial",    emoji: "☕" }
};

// Risk Alert Solutions Database
const RISK_SOLUTIONS = {
  "disease": {
    title: "🛡️ Fungal Disease & Blast Management Solution",
    steps: [
      "Spray systemic fungicide (e.g. Tricyclazole @ 0.6g/L or Carbendazim 50 WP @ 1g/L) during early morning.",
      "Avoid excess nitrogenous fertilizer (Urea) application during cloudy, humid spells.",
      "Ensure proper row spacing (minimum 15-20cm) to facilitate cross-ventilation and sunlight penetration.",
      "Remove and burn infected leaf debris from field borders to prevent spore spreading."
    ]
  },
  "moisture": {
    title: "💧 Waterlogging & Excess Moisture Mitigation",
    steps: [
      "Open lateral surface drainage trenches (30cm deep) every 10–12 meters across slope.",
      "Suspend scheduled drip or sprinkler irrigation immediately for the next 48–72 hours.",
      "Apply gypsum (200 kg/ha) in heavy clay soils to enhance soil flocculation and water infiltration.",
      "Monitor root zone for phytophthora root rot symptoms and apply Trichoderma viride bio-fungicide."
    ]
  },
  "pest": {
    title: "🐛 Integrated Pest Management (IPM) Protocol",
    steps: [
      "Install yellow sticky traps (10 traps/acre) and pheromone traps for early borer/fly detection.",
      "Spray 5% Neem Seed Kernel Extract (NSKE) or Azadirachtin (1500 ppm @ 3ml/L) as eco-friendly deterrent.",
      "Conserve natural predators such as ladybird beetles and chrysoperla in field borders.",
      "Rotate active chemical insecticides with different modes of action to prevent pest resistance."
    ]
  },
  "nutrient": {
    title: "🧪 Soil pH & Nutrient Imbalance Treatment",
    steps: [
      "For acidic soils (pH < 6.0): Apply agricultural lime or dolomite @ 2.5 tons/ha 3 weeks before sowing.",
      "For alkaline soils (pH > 7.8): Apply gypsum @ 3 tons/ha along with green manuring (Dhaincha/Sunhemp).",
      "Apply customized basal NPK fertilizers based on SoilSense recommendation rather than blanket application.",
      "Incorporate bio-fertilizers: Rhizobium for pulses, Azotobacter for cereals, and PSB for phosphorus mobilization."
    ]
  }
};

// Agricultural Research Stations Database
const RESEARCH_STATIONS = [
  {
    name: "Ratnagiri Agro-Station",
    region: "Coastal Konkan Zone",
    lat: 16.9902, lon: 73.3120,
    soilType: "Laterite / Red Coastal Soil",
    ph: 5.8, n: 45, p: 35, k: 40,
    temp: 28.0, humidity: 82.0, rainfall: 220.0,
    health: 74,
    crops: ["Rice", "Coconut", "Mango", "Cashew"],
    description: "Humid coastal climate with heavy precipitation and acidic, well-drained laterite soil."
  },
  {
    name: "Pune Agro-Research Center",
    region: "Western Maharashtra Plateau",
    lat: 18.5204, lon: 73.8567,
    soilType: "Medium Black Loamy Soil",
    ph: 6.8, n: 70, p: 48, k: 50,
    temp: 25.5, humidity: 62.0, rainfall: 85.0,
    health: 84,
    crops: ["Sugarcane", "Cotton", "Soybean", "Maize", "Grapes"],
    description: "Fertile basaltic plateau soil with balanced nutrient retention and moderate rainfall."
  },
  {
    name: "Nagpur Agro-Institute",
    region: "Vidarbha Black Soil Basin",
    lat: 21.1458, lon: 79.0882,
    soilType: "Deep Black Clay (Regur)",
    ph: 7.4, n: 80, p: 55, k: 60,
    temp: 32.0, humidity: 48.0, rainfall: 95.0,
    health: 86,
    crops: ["Cotton", "Orange", "Soybean", "Pigeonpeas"],
    description: "Deep clayey black cotton soil with high cation-exchange capacity and hot semi-arid climate."
  },
  {
    name: "Nashik Horticultural Station",
    region: "Northern Maharashtra Basin",
    lat: 19.9975, lon: 73.7898,
    soilType: "Red & Black Mixed Loam",
    ph: 6.5, n: 60, p: 52, k: 58,
    temp: 24.0, humidity: 58.0, rainfall: 75.0,
    health: 88,
    crops: ["Grapes", "Onion", "Pomegranate", "Wheat", "Tomato"],
    description: "Premier horticultural zone with friable loam, high potassium availability, and sunny climate."
  },
  {
    name: "Kolhapur Sugarcane Research",
    region: "Panchganga Fertile Basin",
    lat: 16.7050, lon: 74.2433,
    soilType: "Alluvial & Rich Black Soil",
    ph: 7.1, n: 85, p: 60, k: 65,
    temp: 26.0, humidity: 70.0, rainfall: 130.0,
    health: 91,
    crops: ["Sugarcane", "Rice", "Soybean", "Jowar", "Banana"],
    description: "High-yield riverine black alluvial soil with abundant irrigation and high organic matter."
  }
];

// Multi-Language Localization Dictionary
const I18N_DICTIONARY = {
  hi: {
    badge_ai: "एआई प्लेटफॉर्म",
    brand_sub: "सटीक मृदा जांच एवं फसल अनुशंसा प्रणाली",
    nav_dashboard: "डैशबोर्ड",
    nav_analysis: "मृदा जांच",
    nav_simulation: "सिमुलेशन स्टूडियो",
    nav_comparative: "तुलनात्मक विश्लेषण",
    nav_timeseries: "समय-श्रृंखला",
    nav_geomap: "भू-स्थानिक नक्शा",
    nav_correlations: "सहसंबंध",
    nav_dataset: "डेटासेट एवं निर्यात",
    nav_notes: "लैब नोट्स",
    nav_weather: "मौसम",
    nav_reports: "रिपोर्ट्स",
    dash_welcome_title: "सॉइलसेंस एआई में आपका स्वागत है 🌱",
    dash_welcome_sub: "रैंडम फॉरेस्ट मशीन लर्निंग (99.3% सटीकता), लाइव मौसम पूर्वानुमान और सटीक कृषि सलाह।",
    qa_new_test: "नई मृदा जांच",
    qa_compare_reports: "रिपोर्ट तुलना",
    qa_crop_guide: "फसल गाइड",
    qa_simulation: "सिम्युलेटर",
    card_soil_health: "मृदा स्वास्थ्य स्कोर",
    health_good_status: "उत्कृष्ट जैव-रासायनिक संतुलन",
    card_recommended_crops: "सर्वोत्तम अनुशंसित फसलें",
    card_microclimate_alerts: "सक्रिय कृषि जोखिम चेतावनी",
    badge_best: "सर्वोत्तम",
    badge_alt: "विकल्प",
    btn_view_solution: "समाधान देखें →",
    chart_health_trend_title: "मृदा स्वास्थ्य रुझान (पिछली 5 जांचें)",
    chart_rainfall_trend_title: "साप्ताहिक वर्षा एवं नमी रुझान",
    weather_lookup_title: "लाइव कृषि-मौसम स्टेशन",
    btn_fetch: "मौसम जांचें",
    btn_use_weather: "लाइव मौसम डेटा का उपयोग करें →",
    soil_tips_title: "सटीक मृदा सुधार सलाह",
    btn_run_analysis: "मृदा जांच शुरू करें",
    btn_export_pdf: "पीडीएफ रिपोर्ट बनाएं",
    btn_save_note: "नोट सहेजें",
    report_upload_title: "मृदा जांच रिपोर्ट से स्वतः भरें",
    report_upload_sub: "सभी मापदंडों को स्वतः भरने के लिए मृदा स्वास्थ्य कार्ड या प्रयोगशाला रिपोर्ट (PDF / छवि / CSV) अपलोड करें।"
  },
  mr: {
    badge_ai: "एआय प्लॅटफॉर्म",
    brand_sub: "अचूक माती परीक्षण व पीक शिफारस प्रणाली",
    nav_dashboard: "डॅशबोर्ड",
    nav_analysis: "माती परीक्षण",
    nav_simulation: "सिम्युलेशन स्टुडिओ",
    nav_comparative: "तुलनात्मक विश्लेषण",
    nav_timeseries: "वेळ-मालिका",
    nav_geomap: "भू-स्थानिक नकाशा",
    nav_correlations: "सहसंबंध",
    nav_dataset: "डेटासेट व निर्यात",
    nav_notes: "लॅब नोट्स",
    nav_weather: "हवामान",
    nav_reports: "अहवाल",
    dash_welcome_title: "सॉइलसेन्स एआय मध्ये आपले स्वागत आहे 🌱",
    dash_welcome_sub: "रँडम फॉरेस्ट मशिन लर्निंग (९९.३% अचूकता), थेट हवामान आणि अचूक कृषी सल्ला.",
    qa_new_test: "नवीन माती तपासणी",
    qa_compare_reports: "अहवाल तुलना",
    qa_crop_guide: "पीक मार्गदर्शक",
    qa_simulation: "सिम्युलेटर",
    card_soil_health: "माती आरोग्य निर्देशांक",
    health_good_status: "उत्कृष्ट जैव-रासायनिक संतुलन",
    card_recommended_crops: "सर्वोत्तम शिफारस केलेली पिके",
    card_microclimate_alerts: "सक्रिय कृषी धोका इशारे",
    badge_best: "सर्वोत्तम",
    badge_alt: "पर्याय",
    btn_view_solution: "उपाय पहा →",
    chart_health_trend_title: "माती आरोग्य कल (मागील ५ चाचण्या)",
    chart_rainfall_trend_title: "साप्ताहिक पाऊस व ओलावा कल",
    weather_lookup_title: "थेट कृषी-हवामान केंद्र",
    btn_fetch: "हवामान मिळवा",
    btn_use_weather: "थेट हवामान माहिती वापरा →",
    soil_tips_title: "अचूक माती सुधारणा सल्ला",
    btn_run_analysis: "माती परीक्षण सुरू करा",
    btn_export_pdf: "पीडीएफ अहवाल डाऊनलोड करा",
    btn_save_note: "नोंद जतन करा",
    report_upload_title: "माती तपासणी अहवालातून आपोआप भरा",
    report_upload_sub: "सर्व मापदंड आपोआप भरण्यासाठी माती आरोग्य पत्रिका किंवा प्रयोगशाळा अहवाल (PDF / प्रतिमा / CSV) अपलोड करा."
  },
  gu: { badge_ai: "AI પ્લેટફોર્મ", nav_dashboard: "ડૅશબોર્ડ", nav_analysis: "જમીન વિશ્લેષણ", qa_new_test: "નવી જમીન ચકાસણી", qa_crop_guide: "પાક માર્ગદર્શિકા", card_soil_health: "જમીન આરોગ્ય સ્કોર", btn_run_analysis: "જમીન વિશ્લેષણ ચલાવો" },
  te: { badge_ai: "AI ప్లాట్‌ఫాం", nav_dashboard: "డాష్‌బోర్డ్", nav_analysis: "నేల విశ్లేషణ", qa_new_test: "కొత్త నేల పరీక్ష", card_soil_health: "నేల ఆరోగ్య స్కోరు", btn_run_analysis: "నేల విశ్లేషణను ప్రారంభించండి" },
  ta: { badge_ai: "AI தளம்", nav_dashboard: "டாஷ்போர்டு", nav_analysis: "மண் பகுப்பாய்வு", qa_new_test: "புதிய மண் சோதனை", card_soil_health: "மண் ஆரோக்கிய மதிப்பீடு", btn_run_analysis: "மண் பகுப்பாய்வு செய்க" },
  bn: { badge_ai: "AI প্ল্যাটফর্ম", nav_dashboard: "ড্যাশবোর্ড", nav_analysis: "মাটি পরীক্ষা", qa_new_test: "নতুন মাটি পরীক্ষা", card_soil_health: "মাটির স্বাস্থ্য স্কোর", btn_run_analysis: "মাটি পরীক্ষা করুন" },
  es: { badge_ai: "PLATAFORMA IA", nav_dashboard: "Panel", nav_analysis: "Análisis de Suelo", qa_new_test: "Nuevo Análisis", card_soil_health: "Índice de Salud", btn_run_analysis: "Analizar Suelo" }
};


/* ══════════════════ PAGE ROUTING ═════════════════════════ */
const PAGES = [
  "dashboard", "analysis", "experiment", "comparative",
  "timeseries", "mapping", "correlation", "dataset",
  "notes", "weather", "reports"
];

function showPage(name) {
  PAGES.forEach(p => {
    const el = document.getElementById("page-" + p);
    if (el) el.classList.toggle("active", p === name);
    document.querySelectorAll(`[data-page='${p}']`).forEach(btn => {
      btn.classList.toggle("active", p === name);
    });
  });
  window.scrollTo({ top: 0, behavior: "smooth" });

  if (name === "dashboard")   initDashboard();
  if (name === "experiment")  initExperimentPage();
  if (name === "comparative") initComparativePage();
  if (name === "timeseries")  initTimeSeriesPage();
  if (name === "mapping")     initMappingPage();
  if (name === "correlation") initCorrelationPage();
  if (name === "dataset")     fetchDatasetPreview(1);
  if (name === "notes")       renderResearchNotes();
  if (name === "weather")     initWeatherPage();
  if (name === "reports")     renderReports();
}


/* ══════════════════ INITIALIZATION ════════════════════════ */
document.addEventListener("DOMContentLoaded", () => {
  setupImageUploadHandler();
  setupReportUploadHandler();
  setupEventListeners();
  initDashboard();
  showPage("dashboard");

  // Auto-fetch default location weather on startup (Pune or saved location)
  const defaultLoc = loadSettings().defaultLocation || "Pune";
  const dashInp = document.getElementById("dash-location-input");
  if (dashInp && !dashInp.value) dashInp.value = defaultLoc;
  dashFetchWeather(defaultLoc);
});

function setupEventListeners() {
  const dashInp = document.getElementById("dash-location-input");
  if (dashInp) {
    dashInp.addEventListener("keydown", e => {
      if (e.key === "Enter") {
        e.preventDefault();
        dashFetchWeather();
      }
    });
  }

  const fullInp = document.getElementById("weather-location-input");
  if (fullInp) {
    fullInp.addEventListener("keydown", e => {
      if (e.key === "Enter") {
        e.preventDefault();
        fullFetchWeather();
      }
    });
  }
}


/* ══════════════════ 1. DASHBOARD CONTROLLER ════════════════ */
function initDashboard() {
  const last = getLastAnalysis();
  if (last) {
    document.getElementById("dash-health-score").innerHTML = `${last.health.score} <small>/100</small>`;
    const badge = document.getElementById("dash-health-badge");
    badge.textContent = last.health.level;
    badge.className = "badge badge-" + (last.health.level === "Excellent" || last.health.level === "Good" ? "success" : "warning");
    document.getElementById("dash-health-status").textContent = last.health.summary || "Balanced biochemical status";

    renderDashboardTopCrops(last.crops);
    renderSoilTipsCard(last.soil_params, last.health);
  } else {
    renderDashboardTopCrops([
      { crop: "muskmelon", probability: 88.5 },
      { crop: "tomato", probability: 76.2 },
      { crop: "maize", probability: 64.0 }
    ]);
    renderSoilTipsCard({ ph: 6.8, n: 65, p: 48, k: 45 }, { score: 78, level: "Good" });
  }

  renderMiniGraphs();
}

function renderDashboardTopCrops(crops) {
  const wrap = document.getElementById("dashTopCropsList");
  if (!wrap || !crops || !crops.length) return;

  wrap.innerHTML = "";
  crops.slice(0, 3).forEach((c, idx) => {
    const cropName = c.crop.toLowerCase();
    const info = CROP_AGRO_ECONOMICS[cropName] || { profit: "₹65,000 / ac", days: "90d", emoji: "🌱" };
    const isBest = idx === 0;

    const row = document.createElement("div");
    row.className = `top-crop-row ${isBest ? 'best-crop' : ''}`;
    row.innerHTML = `
      <span class="tcr-name">
        ${info.emoji} ${c.crop.charAt(0).toUpperCase() + c.crop.slice(1)}
        <span class="${isBest ? 'badge-best' : 'badge-alt'}">${isBest ? 'BEST' : 'ALT'}</span>
      </span>
      <span class="tcr-profit">${info.profit}</span>
      <span class="tcr-days">${info.days}</span>
    `;
    wrap.appendChild(row);
  });
}

function renderSoilTipsCard(params, health) {
  const container = document.getElementById("dashSoilTipsContainer");
  const phBadge = document.getElementById("soilTipsPhBadge");
  if (!container || !params) return;

  const ph = params.ph || 6.8;
  let phStatus = "Optimal 👍";
  let phBadgeClass = "badge-success";

  if (ph < 6.0) {
    phStatus = "Acidic ⚠️";
    phBadgeClass = "badge-warning";
  } else if (ph > 7.5) {
    phStatus = "Alkaline ⚠️";
    phBadgeClass = "badge-warning";
  }

  if (phBadge) {
    phBadge.textContent = `pH ${ph} (${phStatus})`;
    phBadge.className = `badge ${phBadgeClass}`;
  }

  container.innerHTML = "";

  let tip1 = {
    icon: "🌱",
    title: "Organic Matter & Compost:",
    desc: "Incorporate 2-3 tons/ha of decomposed Farmyard Manure (FYM) monthly to maintain soil structure and bio-activity."
  };
  if (ph < 6.0) {
    tip1 = {
      icon: "🍋",
      title: "Acidic Soil Amendment:",
      desc: "Soil pH is below 6.0. Apply agricultural lime (calcium carbonate @ 1.5 tons/ha) to gradually neutralize acidity."
    };
  } else if (ph > 7.5) {
    tip1 = {
      icon: "🧪",
      title: "Alkalinity Reduction:",
      desc: "Soil pH is high (>7.5). Incorporate gypsum @ 2 tons/ha and grow green manure crops to enhance soil acidity."
    };
  }

  const tip2 = {
    icon: "💧",
    title: "Maintain 60–70% Root Zone Moisture:",
    desc: "Consistent moisture level facilitates potassium uptake and minimizes fruit-cracking in ripening crops."
  };

  const tip3 = {
    icon: "🪵",
    title: "Mulch with Crop Residues:",
    desc: "Reduces surface evapotranspiration by up to 35% and maintains cool soil microbiome during sunny hours."
  };

  [tip1, tip2, tip3].forEach(t => {
    container.innerHTML += `
      <div class="tip-item">
        <span class="tip-icon">${t.icon}</span>
        <div class="tip-text">
          <strong>${t.title}</strong>
          <p>${t.desc}</p>
        </div>
      </div>
    `;
  });
}


/* ══════════════════ 2. MINI GRAPHS ON DASHBOARD ════════════ */
function renderMiniGraphs() {
  if (typeof Chart === "undefined") return;

  const ctxHealth = document.getElementById("miniChartHealth")?.getContext("2d");
  if (ctxHealth) {
    if (miniChartHealthInstance) miniChartHealthInstance.destroy();
    miniChartHealthInstance = new Chart(ctxHealth, {
      type: "line",
      data: {
        labels: ["Test #1", "Test #2", "Test #3", "Test #4", "Test #5 (Latest)"],
        datasets: [{
          label: "Soil Health Score",
          data: [68, 72, 74, 76, 78],
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.15)",
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: "#10b981"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { min: 50, max: 100, grid: { color: "#f1f5f9" } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  const ctxRain = document.getElementById("miniChartRainfall")?.getContext("2d");
  if (ctxRain) {
    if (miniChartRainfallInstance) miniChartRainfallInstance.destroy();
    miniChartRainfallInstance = new Chart(ctxRain, {
      type: "bar",
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{
          label: "Precipitation (mm)",
          data: [1.2, 0.0, 4.5, 3.1, 6.2, 2.5, 1.0],
          backgroundColor: "#3b82f6",
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
          x: { grid: { display: false } }
        }
      }
    });
  }
}


/* ══════════════════ 3. EXPANDED RISK ALERTS & SOLUTIONS ════ */
let currentAlertFilter = "all";

function filterRiskAlerts(category) {
  currentAlertFilter = category;
  const box = document.getElementById("dashRiskAlertBox");
  if (!box) return;

  const alerts = {
    all: {
      title: "High Atmospheric Humidity (82%)",
      msg: "Elevated humidity (>80%) and warmth may trigger fungal spore blast in vegetable foliage.",
      type: "disease"
    },
    disease: {
      title: "Fungal Spore & Foliar Blast Risk",
      msg: "Humid tropical climate creates optimal incubation for leaf mildew and powdery blast.",
      type: "disease"
    },
    moisture: {
      title: "Root Zone Waterlogging Hazard",
      msg: "Clay soil drainage index is slow. Precipitation exceeding 25mm may induce root hypoxia.",
      type: "moisture"
    },
    pest: {
      title: "Fruit Borer & Sucking Pest Alert",
      msg: "Warm night temperatures (+22°C) accelerate aphid and whitefly lifecycle reproduction.",
      type: "pest"
    },
    nutrient: {
      title: "Phosphorus Lock-in Risk",
      msg: "Soil pH deviations reduce available ortho-phosphate uptake by young crop roots.",
      type: "nutrient"
    }
  };

  const selected = alerts[category] || alerts.all;
  document.getElementById("raTitle").textContent = selected.title;
  document.getElementById("raMsg").textContent   = selected.msg;
}

function openAlertSolutionModal() {
  const modal = document.getElementById("alert-solution-modal");
  const title = document.getElementById("solutionModalTitle");
  const body  = document.getElementById("solutionModalBody");
  if (!modal) return;

  const category = currentAlertFilter === "all" ? "disease" : currentAlertFilter;
  const sol = RISK_SOLUTIONS[category] || RISK_SOLUTIONS.disease;

  title.textContent = sol.title;
  body.innerHTML = `
    <p style="margin-bottom:12px;color:#475569">Recommended scientific treatment and immediate on-field steps:</p>
    <ol style="padding-left:20px;line-height:1.7;color:#1e293b">
      ${sol.steps.map(s => `<li>${s}</li>`).join("")}
    </ol>
  `;
  modal.classList.add("open");
}
function closeAlertSolutionModal() {
  document.getElementById("alert-solution-modal")?.classList.remove("open");
}


/* ══════════════════ CROP GUIDE MODAL ═══════════════════════ */
function openCropGuideModal() {
  const modal = document.getElementById("crop-guide-modal");
  const body  = document.getElementById("cropGuideModalBody");
  if (!modal) return;

  let html = `
    <div style="overflow-x:auto">
      <table class="param-table">
        <thead>
          <tr>
            <th>Crop</th>
            <th>Optimal Season</th>
            <th>Est. Profit / Acre</th>
            <th>Growth Days</th>
            <th>Water Demand</th>
          </tr>
        </thead>
        <tbody>
  `;
  Object.entries(CROP_AGRO_ECONOMICS).forEach(([crop, info]) => {
    html += `
      <tr>
        <td><strong>${info.emoji} ${crop.toUpperCase()}</strong></td>
        <td><span class="badge badge-info">${info.season}</span></td>
        <td><strong style="color:#166534">${info.profit}</strong></td>
        <td>${info.days}</td>
        <td>${info.water}</td>
      </tr>
    `;
  });
  html += `</tbody></table></div>`;

  body.innerHTML = html;
  modal.classList.add("open");
}
function closeCropGuideModal() {
  document.getElementById("crop-guide-modal")?.classList.remove("open");
}


/* ══════════════════ 5. WEATHER CONTROLLER ══════════════════ */
async function dashFetchWeather(customLoc = null) {
  const locInput = document.getElementById("dash-location-input");
  const loc = customLoc || locInput?.value.trim() || "Pune";

  try {
    const s = loadSettings();
    let url = `/weather?location=${encodeURIComponent(loc)}`;
    if (s.apiKey) url += `&api_key=${encodeURIComponent(s.apiKey)}`;

    const res  = await fetch(url);
    const data = await res.json();

    if (data.success && data.weather && data.location) {
      lastWeather = data.weather;
      renderDashboardWeather(data);
      renderMiniWeatherResult(data);
    }
  } catch (err) {
    console.warn("Weather fetch fallback:", err);
  }
}

function renderDashboardWeather(data) {
  const w = data.weather;
  const loc = data.location;

  document.getElementById("dashWeatherCity").textContent = `${loc.name}, ${loc.region}`;
  document.getElementById("dashWeatherTemp").textContent = `${w.temperature}°C`;
  document.getElementById("dashWeatherCond").textContent = w.condition;
  document.getElementById("dashWeatherHumidity").textContent = `${w.humidity}%`;
  document.getElementById("dashWeatherIconEmoji").textContent = w.icon_emoji || "🌤️";

  if (w.tomorrow) {
    document.getElementById("dashTomorrowForecast").innerHTML = `
      <span>📅 Tomorrow: <strong>${w.tomorrow.temp_max}°C / ${w.tomorrow.temp_min}°C</strong> (${w.tomorrow.rainfall}mm rain, ${w.tomorrow.chance_of_rain}%)</span>
    `;
  }

  if (w.farming_tip) {
    document.getElementById("dashFarmingTipText").textContent = w.farming_tip;
  }
}

function renderMiniWeatherResult(data) {
  const el = document.getElementById("dash-weather-result");
  if (!el) return;

  const w = data.weather;
  const loc = data.location;

  el.innerHTML = `
    <div class="mini-weather-telemetry-box">
      <div class="mwt-main">
        <span class="mwt-emoji">${w.icon_emoji || '🌤️'}</span>
        <div>
          <div class="mwt-temp">${w.temperature}°C</div>
          <div class="mwt-cond">${w.condition} • ${loc.name}, ${loc.region}</div>
        </div>
      </div>
      <div class="mwt-grid">
        <div class="mwt-item"><span class="mwt-lbl">Humidity</span><strong>${w.humidity}%</strong></div>
        <div class="mwt-item"><span class="mwt-lbl">Precipitation</span><strong>${w.rainfall} mm</strong></div>
        <div class="mwt-item"><span class="mwt-lbl">Wind Speed</span><strong>${w.wind_kph} km/h</strong></div>
        <div class="mwt-item"><span class="mwt-lbl">Feels Like</span><strong>${w.feels_like}°C</strong></div>
      </div>
      ${w.tomorrow ? `
      <div class="mwt-tomorrow">
        📅 <strong>Tomorrow's Forecast:</strong> ${w.tomorrow.temp_max}°C / ${w.tomorrow.temp_min}°C • ${w.tomorrow.condition} (${w.tomorrow.rainfall}mm rain, ${w.tomorrow.chance_of_rain}%)
      </div>` : ''}
      ${w.farming_tip ? `
      <div class="mwt-tip">
        💡 <strong>Smart Advisory:</strong> ${w.farming_tip}
      </div>` : ''}
    </div>
  `;

  const btn = document.getElementById("dash-use-weather-btn");
  if (btn) btn.style.display = "block";
}

async function fullFetchWeather() {
  const loc = document.getElementById("weather-location-input")?.value.trim();
  if (!loc) { showToast("Enter a location name", true); return; }

  showLoading(`Fetching agro-weather for ${loc}…`);
  try {
    const s = loadSettings();
    let url = `/weather?location=${encodeURIComponent(loc)}`;
    if (s.apiKey) url += `&api_key=${encodeURIComponent(s.apiKey)}`;

    const res  = await fetch(url);
    const data = await res.json();
    hideLoading();

    if (data.success) {
      lastWeather = data.weather;
      renderFullWeatherPage(data);
      showToast(`🌤️ Weather loaded for ${data.location.name}!`);
    } else {
      showToast(data.error || "Weather fetch failed", true);
    }
  } catch (err) {
    hideLoading();
    showToast(err.message, true);
  }
}

function renderFullWeatherPage(data) {
  const w   = data.weather;
  const loc = data.location;

  document.getElementById("w-icon-emoji").textContent = w.icon_emoji || "🌤️";
  document.getElementById("w-temp").textContent       = `${w.temperature}°C`;
  document.getElementById("w-cond").textContent       = w.condition;
  document.getElementById("w-loc").textContent        = `${loc.name}, ${loc.region}, ${loc.country}`;
  document.getElementById("w-humidity").textContent   = `${w.humidity} %`;
  document.getElementById("w-rainfall").textContent   = `${w.rainfall} mm`;
  document.getElementById("w-feels").textContent      = `${w.feels_like}°C`;
  document.getElementById("w-wind").textContent       = `${w.wind_kph} km/h`;
  document.getElementById("w-uv").textContent         = w.uv;
  document.getElementById("w-cloud").textContent      = `${w.cloud} %`;

  document.getElementById("weather-result-section").style.display = "block";
}

function useWeatherInAnalysis() {
  if (!lastWeather) { showToast("Fetch weather first!", true); return; }
  document.getElementById("temperature").value = lastWeather.temperature;
  document.getElementById("humidity").value    = lastWeather.humidity;
  document.getElementById("rainfall").value    = lastWeather.rainfall;

  const strip = document.getElementById("weather-autofill-strip");
  if (strip) strip.style.display = "flex";

  showPage("analysis");
  showToast("✅ Weather variables copied to Analysis form!");
}

function initWeatherPage() {
  if (lastWeather) {
    renderFullWeatherPage({ weather: lastWeather, location: { name: "Current Station", region: "Maharashtra", country: "India" } });
  }
}


/* ══════════════════ 7. “ASK SOILSENSE” CHATBOT ════════════ */
let chatbotOpen = false;

function toggleChatBot() {
  chatbotOpen = !chatbotOpen;
  const win = document.getElementById("chatWindow");
  if (win) win.style.display = chatbotOpen ? "flex" : "none";
}

function askChatbotQuestion(query) {
  document.getElementById("chatInput").value = query;
  sendChatMessage();
}

function sendChatMessage() {
  const inp = document.getElementById("chatInput");
  const msgStream = document.getElementById("chatMessages");
  const text = inp.value.trim();
  if (!text) return;

  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble user-bubble";
  userBubble.textContent = text;
  msgStream.appendChild(userBubble);
  inp.value = "";
  msgStream.scrollTop = msgStream.scrollHeight;

  setTimeout(() => {
    const reply = generateChatbotReply(text);
    const botBubble = document.createElement("div");
    botBubble.className = "chat-bubble bot-bubble";
    botBubble.innerHTML = reply;
    msgStream.appendChild(botBubble);
    msgStream.scrollTop = msgStream.scrollHeight;
  }, 400);
}

function generateChatbotReply(query) {
  const q = query.toLowerCase();

  if (q.includes("best crop") || q.includes("which crop")) {
    const top = lastPayload?.crops?.[0]?.crop || "Muskmelon";
    return `🌾 Based on current soil & weather telemetry, <strong>${top.toUpperCase()}</strong> is your highest yielding candidate (est. profit <strong>₹85,000/ac</strong>). Alternatives include <strong>Tomato</strong> and <strong>Maize</strong>.`;
  }
  if (q.includes("fertility") || q.includes("increase soil") || q.includes("improve soil")) {
    return `🌱 <strong>To boost soil fertility:</strong><br/>1. Apply 2-3 tons/ha of Farmyard Manure (FYM) or vermicompost.<br/>2. Practice green manuring with <em>Dhaincha</em> or <em>Sunhemp</em>.<br/>3. Maintain NPK balance according to soil test (avoid excessive urea).`;
  }
  if (q.includes("acidic") || q.includes("ph low") || q.includes("ph < 6")) {
    return `🍋 <strong>Acidic Soil Correction:</strong><br/>Apply agricultural lime (calcium carbonate) or dolomite @ 1.5–2 tons/acre 3 weeks before planting. Avoid acidic fertilizers like ammonium sulfate.`;
  }
  if (q.includes("moisture") || q.includes("water") || q.includes("irrigation")) {
    return `💧 <strong>Ideal Soil Moisture:</strong><br/>Maintain 60%–70% of field capacity in the root zone. During flowering and fruit setting, avoid water stress to prevent blossom drop.`;
  }
  if (q.includes("fungal") || q.includes("disease") || q.includes("pest")) {
    return `⚠️ <strong>Pest & Disease Advice:</strong><br/>High humidity (>80%) accelerates blast spores. Spray Tricyclazole @ 0.6g/L or 5% Neem extract (NSKE) during early morning.`;
  }

  return `🌿 <strong>SoilSense Advice:</strong> Ensure soil pH is maintained between 6.0 and 7.5 for maximum nutrient bioavailability. You can also test different scenarios in our <strong>Simulation Studio</strong>!`;
}


/* ══════════════════ 8. MULTI-LANGUAGE TRANSLATION ═══════════ */
async function changeLanguage(targetLang) {
  currentLang = targetLang;
  showToast(`🌐 Switching language to ${targetLang.toUpperCase()}…`);

  const langDict = I18N_DICTIONARY[targetLang] || {};

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (langDict[key]) {
      el.textContent = langDict[key];
    }
  });

  if (targetLang !== "en" && Object.keys(langDict).length < 5) {
    try {
      await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "Soil Health Index", target_lang: targetLang })
      });
    } catch (e) {}
  }

  showToast(`✅ Platform language: ${targetLang.toUpperCase()}`);
}


/* ══════════════════ 9. INSTANT CNN IMAGE CLASSIFIER ═════════ */
function setupImageUploadHandler() {
  const uploadZone = document.getElementById("uploadZone");
  const fileInput  = document.getElementById("soilImageInput");
  if (!uploadZone || !fileInput) return;

  uploadZone.addEventListener("click", () => fileInput.click());
  uploadZone.addEventListener("dragover", e => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
  uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
  uploadZone.addEventListener("drop", e => {
    e.preventDefault();
    uploadZone.classList.remove("drag-over");
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith("image/")) handleSoilImageUpload(f);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleSoilImageUpload(fileInput.files[0]);
  });
}

async function handleSoilImageUpload(file) {
  const uploadPlaceholder = document.getElementById("uploadPlaceholder");
  const imagePreview      = document.getElementById("imagePreview");
  const uploadZone        = document.getElementById("uploadZone");
  const fileInput         = document.getElementById("soilImageInput");

  const reader = new FileReader();
  reader.onload = e => {
    imagePreview.src = e.target.result;
    imagePreview.style.display = "block";
    uploadPlaceholder.style.display = "none";
    uploadZone.classList.add("has-image");
  };
  reader.readAsDataURL(file);

  try {
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
  } catch (e) {}

  showToast("🔍 Classifying soil image with PyTorch CNN…");
  try {
    const fd = new FormData();
    fd.append("image", file);
    const res  = await fetch("/classify-image", { method: "POST", body: fd });
    const data = await res.json();

    if (data.success && data.cnn_result) {
      lastCnnResult = data.cnn_result;
      renderInstantImageResult(data.cnn_result);
      showToast(`✅ Detected: ${data.cnn_result.soil_type} Soil (${data.cnn_result.confidence}%)`);
    }
  } catch (err) {
    console.error("Image classification error:", err);
  }
}

function renderInstantImageResult(cnn) {
  const box = document.getElementById("instantImageResult");
  if (!box) return;
  box.style.display = "block";

  document.getElementById("instantSoilType").textContent = `${cnn.soil_type} Soil`;
  document.getElementById("instantConfidence").textContent = `${cnn.confidence}% Confidence (${cnn.method})`;

  const profile = cnn.profile || {};
  document.getElementById("instantSoilDesc").textContent = profile.description || "Classified from spectral/CNN features.";
  document.getElementById("traitTexture").textContent = `Texture: ${profile.texture || 'Medium'}`;
  document.getElementById("traitDrainage").textContent = `Drainage: ${profile.drainage || 'Balanced'}`;
  document.getElementById("traitRetention").textContent = `Retention: ${profile.nutrient_retention || 'Moderate'}`;
}


/* ══════════════════ 9B. REPORT UPLOAD & PARAMETER EXTRACTION ═════════ */
function setupReportUploadHandler() {
  const dropzone  = document.getElementById("reportDropzone");
  const fileInput = document.getElementById("reportFileInput");
  const browseBtn = document.getElementById("reportBrowseBtn");
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", (e) => {
    if (e.target !== fileInput) fileInput.click();
  });

  if (browseBtn) {
    browseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  dropzone.addEventListener("dragover", e => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("drag-over");
  });

  dropzone.addEventListener("drop", e => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) handleReportUpload(file);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) {
      handleReportUpload(fileInput.files[0]);
    }
  });
}

async function handleReportUpload(file) {
  if (!file) return;

  const contentEl = document.getElementById("reportDropzoneContent");
  const loadingEl = document.getElementById("reportLoading");
  const loadText  = document.getElementById("reportLoadingText");

  if (contentEl) contentEl.style.display = "none";
  if (loadingEl) loadingEl.style.display = "flex";
  if (loadText)  loadText.textContent = `Scanning "${file.name}" & extracting soil data…`;

  showToast(`📑 Uploading & scanning ${file.name}…`);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const endpoints = ["/api/upload-report", "/upload-report"];
    let res = null;
    let data = null;

    for (const ep of endpoints) {
      try {
        res = await fetch(ep, { method: "POST", body: formData });
        if (res.ok) {
          data = await res.json();
          break;
        }
      } catch (err) {}
    }

    if (!data) {
      throw new Error((res && res.statusText) || "Failed to parse report file.");
    }

    if (data.success && data.extracted_data && Object.keys(data.extracted_data).length > 0) {
      applyExtractedParameters(data.extracted_data, data.metadata || {}, data.filename, data.summary);
    } else {
      showToast(data.summary || `No parameters recognized in ${file.name}. Please verify file format.`, true);
    }

  } catch (err) {
    console.error("Report upload error:", err);
    showToast(`❌ Error parsing report: ${err.message || "Network error"}`, true);
  } finally {
    if (contentEl) contentEl.style.display = "flex";
    if (loadingEl) loadingEl.style.display = "none";
    const fileInput = document.getElementById("reportFileInput");
    if (fileInput) fileInput.value = "";
  }
}

async function loadSampleReport(sampleId) {
  const contentEl = document.getElementById("reportDropzoneContent");
  const loadingEl = document.getElementById("reportLoading");
  const loadText  = document.getElementById("reportLoadingText");

  if (contentEl) contentEl.style.display = "none";
  if (loadingEl) loadingEl.style.display = "flex";
  if (loadText)  loadText.textContent = "Loading sample report data…";

  showToast("📑 Ingesting sample test report…");

  try {
    const endpoints = ["/api/upload-report", "/upload-report"];
    let res = null;
    let data = null;

    for (const ep of endpoints) {
      try {
        res = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sample_id: sampleId })
        });
        if (res.ok) {
          data = await res.json();
          break;
        }
      } catch (err) {}
    }

    if (!data || !data.success) {
      throw new Error((data && data.error) || "Sample report not found.");
    }

    applyExtractedParameters(data.extracted_data, data.metadata || {}, data.filename, data.summary);

  } catch (err) {
    console.error("Sample load error:", err);
    showToast(`❌ Error: ${err.message || "Failed to load sample report."}`, true);
  } finally {
    if (contentEl) contentEl.style.display = "flex";
    if (loadingEl) loadingEl.style.display = "none";
  }
}

function applyExtractedParameters(data, metadata, filename, summary) {
  const fields = ["ph", "n", "p", "k", "temperature", "humidity", "rainfall"];
  let count = 0;

  fields.forEach(f => {
    if (data[f] !== undefined && data[f] !== null) {
      const input = document.getElementById(f);
      const tag   = document.getElementById(`tag-${f}`);
      if (input) {
        input.value = data[f];
        input.classList.remove("autofill-highlight");
        // Force reflow for CSS animation re-trigger
        void input.offsetWidth;
        input.classList.add("autofill-highlight");
      }
      if (tag) {
        tag.style.display = "inline-block";
        tag.textContent = "Report";
      }
      count++;
    }
  });

  // If soil type was identified in metadata, update instant image preview
  if (metadata && metadata.soil_type) {
    const box = document.getElementById("instantImageResult");
    const title = document.getElementById("instantSoilType");
    const conf = document.getElementById("instantConfidence");
    const desc = document.getElementById("instantSoilDesc");
    if (box && title) {
      box.style.display = "block";
      title.textContent = metadata.soil_type;
      if (conf) conf.textContent = "Extracted from Soil Report";
      if (desc) desc.textContent = `Report indicates: ${metadata.soil_type}.`;
    }
  }

  // Update Result Banner
  const banner = document.getElementById("reportResultBanner");
  const rrbMeta = document.getElementById("rrbMeta");
  const rrbTags = document.getElementById("rrbTags");

  if (banner) {
    banner.style.display = "flex";

    // Meta line
    let metaHtml = `<strong>Source:</strong> <code>${filename || 'Soil Report'}</code>`;
    if (metadata && metadata.farmer_name) metaHtml += ` • <strong>Farmer:</strong> ${metadata.farmer_name}`;
    if (metadata && metadata.sample_id) metaHtml += ` • <strong>ID:</strong> ${metadata.sample_id}`;
    if (metadata && metadata.location) metaHtml += ` • <strong>Location:</strong> ${metadata.location}`;
    if (rrbMeta) rrbMeta.innerHTML = metaHtml;

    // Tags
    if (rrbTags) {
      let tagsHtml = "";
      if (data.ph !== undefined) tagsHtml += `<span class="rrb-tag">pH: ${data.ph}</span>`;
      if (data.n !== undefined)  tagsHtml += `<span class="rrb-tag">N: ${data.n} kg/ha</span>`;
      if (data.p !== undefined)  tagsHtml += `<span class="rrb-tag">P: ${data.p} kg/ha</span>`;
      if (data.k !== undefined)  tagsHtml += `<span class="rrb-tag">K: ${data.k} kg/ha</span>`;
      if (data.temperature !== undefined) tagsHtml += `<span class="rrb-tag">Temp: ${data.temperature}°C</span>`;
      if (data.humidity !== undefined)    tagsHtml += `<span class="rrb-tag">Humidity: ${data.humidity}%</span>`;
      if (data.rainfall !== undefined)    tagsHtml += `<span class="rrb-tag">Rain: ${data.rainfall} mm</span>`;
      if (metadata && metadata.soil_type) tagsHtml += `<span class="rrb-tag meta-tag">🌱 ${metadata.soil_type}</span>`;
      if (metadata && metadata.organic_carbon !== undefined) tagsHtml += `<span class="rrb-tag meta-tag">OC: ${metadata.organic_carbon}%</span>`;
      if (metadata && metadata.electrical_conductivity !== undefined) tagsHtml += `<span class="rrb-tag meta-tag">EC: ${metadata.electrical_conductivity} dS/m</span>`;
      rrbTags.innerHTML = tagsHtml;
    }
  }

  showToast(`✅ Auto-filled ${count} parameters from ${filename || 'report'}!`);
}

function dismissReportBanner(e) {
  if (e) e.stopPropagation();
  const banner = document.getElementById("reportResultBanner");
  if (banner) banner.style.display = "none";
  const fields = ["ph", "n", "p", "k", "temperature", "humidity", "rainfall"];
  fields.forEach(f => {
    const tag = document.getElementById(`tag-${f}`);
    if (tag) tag.style.display = "none";
  });
}


/* ══════════════════ 10. SOIL ANALYSIS PIPELINE ═════════════ */
function getFormValues() {
  return {
    ph:          parseFloat(document.getElementById("ph").value),
    n:           parseFloat(document.getElementById("n").value),
    p:           parseFloat(document.getElementById("p").value),
    k:           parseFloat(document.getElementById("k").value),
    temperature: parseFloat(document.getElementById("temperature").value),
    humidity:    parseFloat(document.getElementById("humidity").value),
    rainfall:    parseFloat(document.getElementById("rainfall").value),
    lang:        currentLang || "en",
  };
}

function validateForm(v) {
  for (const f of ["ph","n","p","k","temperature","humidity","rainfall"]) {
    if (isNaN(v[f])) { showToast("Enter a valid numeric value for " + f.toUpperCase(), true); return false; }
  }
  if (v.ph < 0 || v.ph > 14) { showToast("pH must be 0–14", true); return false; }
  if (v.humidity < 0 || v.humidity > 100) { showToast("Humidity must be 0–100 %", true); return false; }
  return true;
}

async function analyzeSoil() {
  const vals = getFormValues();
  if (!validateForm(vals)) return;

  showLoading("Running ensemble ML crop prediction & XAI diagnostics…");
  try {
    const fileInput = document.getElementById("soilImageInput");
    const imageFile = fileInput?.files[0] || null;

    const [predictResult, cnnResult] = await Promise.all([
      fetchPredict(vals),
      imageFile && !lastCnnResult ? fetchClassifyImage(imageFile) : Promise.resolve(lastCnnResult),
    ]);

    lastPayload   = predictResult;
    lastCnnResult = cnnResult || lastCnnResult;
    hideLoading();

    renderFullAnalysisResults(predictResult, lastCnnResult);
    document.getElementById("reportBtn").disabled = false;
    saveLastAnalysis(predictResult);
    recordAnalysisHistory(predictResult);
    initDashboard();
    showToast("✅ Full diagnostic & ML evaluation complete!");

  } catch (err) {
    hideLoading();
    showToast("❌ " + (err.message || "Analysis failed"), true);
  }
}

async function fetchPredict(vals) {
  const res  = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vals)
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.error || "Prediction failed");
  return data;
}

async function fetchClassifyImage(file) {
  try {
    const fd = new FormData();
    fd.append("image", file);
    const res  = await fetch("/classify-image", { method: "POST", body: fd });
    const data = await res.json();
    return data.success ? data.cnn_result : null;
  } catch { return null; }
}

function renderFullAnalysisResults(data, cnn) {
  document.getElementById("emptyState").style.display  = "none";
  document.getElementById("resultsWrap").style.display = "block";

  renderDetailedParameterBreakdown(data.health);
  renderHealthScoreGauge(data.health);
  renderXaiInsights(data.xai, data.crops);
  renderCropsList(data.crops);
  renderFertilizerAndAdvisory(data.fertilizer, data.advisory);
  renderIrrigationAndAlerts(data.irrigation, data.alerts);
}

function renderDetailedParameterBreakdown(health) {
  const tbody = document.getElementById("paramBreakdownBody");
  const barsGrid = document.getElementById("paramBarsGrid");
  if (!tbody || !health.parameters) return;

  tbody.innerHTML = "";
  barsGrid.innerHTML = "";

  health.parameters.forEach(p => {
    let badgeClass = "badge-success";
    if (p.status_code === "low" || p.status_code === "high") badgeClass = "badge-warning";
    if (p.status_code === "excess" || p.status.includes("Deficient")) badgeClass = "badge-danger";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${p.name}</strong><div style="font-size:0.75rem;color:#6b7280">${p.role}</div></td>
      <td><strong>${p.value} ${p.unit}</strong></td>
      <td>${p.normal_range}</td>
      <td><span class="badge ${badgeClass}">${p.status}</span></td>
      <td><strong>${p.score}</strong> / 25</td>
    `;
    tbody.appendChild(tr);

    const barItem = document.createElement("div");
    barItem.className = "param-bar-item";
    barItem.innerHTML = `
      <div class="pbi-head">
        <span>${p.name}</span>
        <span><strong>${p.value} ${p.unit}</strong> <small>(Normal: ${p.normal_min}–${p.normal_max})</small></span>
      </div>
      <div class="pbi-track">
        <div class="pbi-optimal-band" style="left:25%;width:40%"></div>
        <div class="pbi-fill pbi-${p.status_code}" style="width:${Math.min(100, Math.max(8, p.gauge_pct))}%"></div>
      </div>
    `;
    barsGrid.appendChild(barItem);
  });
}

function renderHealthScoreGauge(h) {
  document.getElementById("scoreNum").textContent = h.score;
  const arc = document.getElementById("healthArc");
  const levelColors = { Excellent: "#10b981", Good: "#3b82f6", Moderate: "#f59e0b", Poor: "#ef4444" };
  arc.style.stroke = levelColors[h.level] || "#10b981";
  
  setTimeout(() => {
    arc.style.transition = "stroke-dashoffset 1.1s ease";
    arc.style.strokeDashoffset = 314 - (h.score / 100) * 314;
  }, 100);

  const lvl = document.getElementById("healthLevelLbl");
  lvl.textContent = h.level;
  lvl.className   = "health-level-label lvl-" + h.level.toLowerCase();

  document.getElementById("healthLevelHeading").textContent = `${h.level} Soil Health Profile`;
  document.getElementById("healthSummaryText").textContent = h.summary || "Balanced biochemical status supporting high crop yield potential.";
}

function renderXaiInsights(xai, crops) {
  const container = document.getElementById("xaiCropsExplanationList");
  const barsWrap  = document.getElementById("featureImportanceBars");
  if (!container) return;

  container.innerHTML = "";
  const explanations = xai?.crop_explanations || [];

  explanations.forEach(exp => {
    const card = document.createElement("div");
    card.className = "xai-explanation-item";
    card.innerHTML = `
      <div class="xai-item-head">
        <div class="xai-crop-title">
          <span class="xai-rank">#${exp.rank}</span>
          <strong>${exp.crop.toUpperCase()}</strong>
        </div>
        <span class="xai-prob-badge">${exp.probability}% Match</span>
      </div>
      <p class="xai-reason-text">💡 <strong>Why selected:</strong> ${exp.reason}</p>
      <div class="xai-drivers">
        <span class="driver-label">Key Drivers:</span>
        ${exp.key_drivers.map(d => `<span class="driver-tag">${d.toUpperCase()}</span>`).join("")}
      </div>
    `;
    container.appendChild(card);
  });

  if (barsWrap && xai?.feature_importance) {
    barsWrap.innerHTML = "";
    Object.entries(xai.feature_importance).forEach(([feat, weight]) => {
      const bar = document.createElement("div");
      bar.className = "feat-bar-item";
      bar.innerHTML = `
        <div class="fbi-lbl"><span>${feat.toUpperCase()}</span><span>${weight}%</span></div>
        <div class="fbi-track"><div class="fbi-fill" style="width:${weight}%"></div></div>
      `;
      barsWrap.appendChild(bar);
    });
  }
}

function renderCropsList(crops) {
  const wrap = document.getElementById("cropRecCards");
  if (!wrap) return;
  wrap.innerHTML = "";

  crops.forEach((c, idx) => {
    const info = CROP_AGRO_ECONOMICS[c.crop.toLowerCase()] || { profit: "₹65,000 / ac", days: "90d", emoji: "🌱" };
    const card = document.createElement("div");
    card.className = "crop-card " + (idx === 0 ? "crop-top" : "");
    card.innerHTML = `
      <div class="crop-card-inner">
        <span class="crop-emoji">${info.emoji}</span>
        <div class="crop-details">
          <h4>${c.crop.charAt(0).toUpperCase() + c.crop.slice(1)}</h4>
          <p class="crop-prob-text">Match: <strong>${c.probability}%</strong> • Profit: <strong style="color:#166534">${info.profit}</strong></p>
        </div>
      </div>
      <div class="crop-bar-track"><div class="crop-bar-fill" style="width:${c.probability}%"></div></div>
    `;
    wrap.appendChild(card);
  });
}

function renderFertilizerAndAdvisory(fertilizer, advisory) {
  const fertWrap = document.getElementById("fertilizerRecList");
  const advWrap  = document.getElementById("advisoryRecList");
  if (fertWrap) {
    fertWrap.innerHTML = "";
    if (fertilizer && fertilizer.length) {
      fertilizer.forEach(f => {
        fertWrap.innerHTML += `<div class="fert-item">🧪 <strong>${f.nutrient}:</strong> ${f.suggestion}</div>`;
      });
    } else {
      fertWrap.innerHTML = `<div class="fert-item">✨ Soil NPK values are well-balanced. Standard maintenance dosing recommended.</div>`;
    }
  }

  if (advWrap) {
    advWrap.innerHTML = "";
    if (advisory && advisory.length) {
      advisory.forEach(a => {
        advWrap.innerHTML += `<div class="advisory-chip">🌱 ${a}</div>`;
      });
    }
  }
}

function renderIrrigationAndAlerts(irrigation, alerts) {
  const irrBox = document.getElementById("irrigationAdviceBox");
  const altBox = document.getElementById("alertsContainer");

  if (irrBox && irrigation) {
    irrBox.innerHTML = `
      <h4>💧 Irrigation Recommendation: ${irrigation.level || 'Standard'}</h4>
      <p>${irrigation.action || 'Maintain normal scheduled irrigation cycles.'}</p>
    `;
  }

  if (altBox) {
    altBox.innerHTML = "";
    if (alerts && alerts.length) {
      alerts.forEach(al => {
        altBox.innerHTML += `
          <div class="alert-box alert-${al.level || 'warning'}">
            <strong>⚠️ ${al.title || 'Notice'}:</strong> ${al.message}
          </div>
        `;
      });
    } else {
      altBox.innerHTML = `<div class="alert-box alert-success">✅ No significant agro-climatic stress risks detected.</div>`;
    }
  }
}


/* ══════════════════ SIMULATION STUDIO ══════════════════════ */
let expDebounceTimer = null;

function initExperimentPage() {
  onExperimentSliderChange();
}

function loadExperimentPreset(presetKey) {
  const presets = {
    arid:     { ph: 7.8, n: 35, p: 25, k: 35, rainfall: 35, temp: 33.0, humidity: 32 },
    acidic:   { ph: 5.2, n: 50, p: 30, k: 40, rainfall: 140, temp: 24.0, humidity: 75 },
    high_n:   { ph: 6.6, n: 120, p: 55, k: 50, rainfall: 90, temp: 26.0, humidity: 65 },
    monsoon:  { ph: 6.4, n: 70, p: 45, k: 40, rainfall: 240, temp: 25.0, humidity: 88 },
    optimal:  { ph: 6.7, n: 75, p: 50, k: 50, rainfall: 100, temp: 25.5, humidity: 68 }
  };

  const p = presets[presetKey];
  if (!p) return;

  document.getElementById("exp-ph").value       = p.ph;
  document.getElementById("exp-n").value        = p.n;
  document.getElementById("exp-p").value        = p.p;
  document.getElementById("exp-k").value        = p.k;
  document.getElementById("exp-rainfall").value = p.rainfall;
  document.getElementById("exp-temp").value     = p.temp;
  document.getElementById("exp-humidity").value = p.humidity;

  onExperimentSliderChange();
  showToast(`🧪 Loaded "${presetKey.toUpperCase()}" simulation preset!`);
}

function onExperimentSliderChange() {
  const ph       = parseFloat(document.getElementById("exp-ph").value);
  const n        = parseFloat(document.getElementById("exp-n").value);
  const p        = parseFloat(document.getElementById("exp-p").value);
  const k        = parseFloat(document.getElementById("exp-k").value);
  const rainfall = parseFloat(document.getElementById("exp-rainfall").value);
  const temp     = parseFloat(document.getElementById("exp-temp").value);
  const humidity = parseFloat(document.getElementById("exp-humidity").value);

  document.getElementById("exp-ph-val").textContent       = ph.toFixed(1);
  document.getElementById("exp-n-val").textContent        = n;
  document.getElementById("exp-p-val").textContent        = p;
  document.getElementById("exp-k-val").textContent        = k;
  document.getElementById("exp-rainfall-val").textContent = rainfall;
  document.getElementById("exp-temp-val").textContent     = temp.toFixed(1);
  document.getElementById("exp-humidity-val").textContent = humidity;

  clearTimeout(expDebounceTimer);
  expDebounceTimer = setTimeout(() => {
    runExperimentPrediction(ph, n, p, k, temp, humidity, rainfall);
  }, 120);
}

async function runExperimentPrediction(ph, n, p, k, temperature, humidity, rainfall) {
  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ph, n, p, k, temperature, humidity, rainfall })
    });
    const data = await res.json();
    if (!data.success) return;

    document.getElementById("expScoreVal").textContent = `${data.health.score} / 100`;
    const scoreLvl = document.getElementById("expScoreLvl");
    scoreLvl.textContent = data.health.level;
    scoreLvl.className = "badge badge-" + (data.health.level === "Excellent" || data.health.level === "Good" ? "success" : "warning");

    const topCrop = data.crops[0] || { crop: "—", probability: 0 };
    document.getElementById("expTopCropVal").textContent = topCrop.crop.charAt(0).toUpperCase() + topCrop.crop.slice(1);
    document.getElementById("expTopCropProb").textContent = `${topCrop.probability}% Match`;

    const topExp = data.xai?.crop_explanations?.[0];
    document.getElementById("expXaiReason").textContent = topExp ? `"${topExp.reason}"` : "Optimal agronomic threshold alignment.";

    const barsWrap = document.getElementById("expProbShiftBars");
    barsWrap.innerHTML = "";
    data.crops.forEach(c => {
      barsWrap.innerHTML += `
        <div class="exp-prob-item">
          <div class="epi-lbl"><span>${c.crop.toUpperCase()}</span><strong>${c.probability}%</strong></div>
          <div class="epi-track"><div class="epi-fill" style="width:${c.probability}%"></div></div>
        </div>
      `;
    });

    const metersWrap = document.getElementById("expParamMeters");
    metersWrap.innerHTML = "";
    data.health.parameters.forEach(param => {
      metersWrap.innerHTML += `
        <div class="param-bar-item">
          <div class="pbi-head"><span>${param.name}</span><span>${param.value} ${param.unit} (${param.status})</span></div>
          <div class="pbi-track"><div class="pbi-fill pbi-${param.status_code}" style="width:${param.gauge_pct}%"></div></div>
        </div>
      `;
    });

  } catch (err) {
    console.error("Experiment prediction error:", err);
  }
}

function transferExpToAnalysis() {
  document.getElementById("ph").value          = document.getElementById("exp-ph").value;
  document.getElementById("n").value           = document.getElementById("exp-n").value;
  document.getElementById("p").value           = document.getElementById("exp-p").value;
  document.getElementById("k").value           = document.getElementById("exp-k").value;
  document.getElementById("rainfall").value    = document.getElementById("exp-rainfall").value;
  document.getElementById("temperature").value = document.getElementById("exp-temp").value;
  document.getElementById("humidity").value    = document.getElementById("exp-humidity").value;

  showPage("analysis");
  showToast("✅ Simulation parameters loaded into Analysis form!");
}

function saveExpAsNote() {
  const ph   = document.getElementById("exp-ph").value;
  const n    = document.getElementById("exp-n").value;
  const rain = document.getElementById("exp-rainfall").value;
  const crop = document.getElementById("expTopCropVal").textContent;
  const score= document.getElementById("expScoreVal").textContent;

  saveResearchNoteDirect(
    `Simulation: pH ${ph} | ${rain}mm Rainfall`,
    `Experimental trial outcome: Optimal candidate shifted to ${crop} with health score ${score}. Simulated under N=${n}, P=${document.getElementById("exp-p").value}, K=${document.getElementById("exp-k").value}.`,
    ["Simulation", "Experiment", crop]
  );
}


/* ══════════════════ COMPARATIVE ANALYSIS ═══════════════════ */
function initComparativePage() {
  renderLocationComparison();
  renderHistoricalRunsComparison();
  renderCropComparison();
}

function switchCompTab(tabName) {
  document.querySelectorAll(".comp-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".comp-section").forEach(s => s.classList.remove("active"));

  const targetSec = document.getElementById("comp-sec-" + tabName);
  if (targetSec) targetSec.classList.add("active");

  const activeBtn = Array.from(document.querySelectorAll(".comp-tab")).find(b => b.getAttribute("onclick").includes(tabName));
  if (activeBtn) activeBtn.classList.add("active");
}

function renderLocationComparison() {
  const locAName = document.getElementById("comp-loc-a").value;
  const locBName = document.getElementById("comp-loc-b").value;

  const locA = RESEARCH_STATIONS.find(s => s.name.includes(locAName)) || RESEARCH_STATIONS[0];
  const locB = RESEARCH_STATIONS.find(s => s.name.includes(locBName)) || RESEARCH_STATIONS[1];

  const grid = document.getElementById("locationCompGrid");
  if (!grid) return;

  grid.innerHTML = `
    <div class="comp-col-card">
      <div class="comp-col-header">
        <h4>${locA.name}</h4>
        <span class="badge badge-primary">${locA.region}</span>
      </div>
      <p class="section-subtext">${locA.description}</p>
      <table class="comp-metric-table">
        <tr><td>Soil Type</td><td><strong>${locA.soilType}</strong></td></tr>
        <tr><td>Soil pH</td><td><strong>${locA.ph}</strong></td></tr>
        <tr><td>Nitrogen (N)</td><td><strong>${locA.n} kg/ha</strong></td></tr>
        <tr><td>Phosphorus (P)</td><td><strong>${locA.p} kg/ha</strong></td></tr>
        <tr><td>Potassium (K)</td><td><strong>${locA.k} kg/ha</strong></td></tr>
        <tr><td>Avg Precipitation</td><td><strong>${locA.rainfall} mm</strong></td></tr>
        <tr><td>Soil Health Score</td><td><span class="badge badge-success">${locA.health}/100</span></td></tr>
        <tr><td>Top Suitable Crops</td><td><strong>${locA.crops.join(", ")}</strong></td></tr>
      </table>
    </div>

    <div class="comp-col-card">
      <div class="comp-col-header">
        <h4>${locB.name}</h4>
        <span class="badge badge-info">${locB.region}</span>
      </div>
      <p class="section-subtext">${locB.description}</p>
      <table class="comp-metric-table">
        <tr><td>Soil Type</td><td><strong>${locB.soilType}</strong></td></tr>
        <tr><td>Soil pH</td><td><strong>${locB.ph}</strong> ${getDeltaBadge(locB.ph, locA.ph, "")}</td></tr>
        <tr><td>Nitrogen (N)</td><td><strong>${locB.n} kg/ha</strong> ${getDeltaBadge(locB.n, locA.n, "kg")}</td></tr>
        <tr><td>Phosphorus (P)</td><td><strong>${locB.p} kg/ha</strong> ${getDeltaBadge(locB.p, locA.p, "kg")}</td></tr>
        <tr><td>Potassium (K)</td><td><strong>${locB.k} kg/ha</strong> ${getDeltaBadge(locB.k, locA.k, "kg")}</td></tr>
        <tr><td>Avg Precipitation</td><td><strong>${locB.rainfall} mm</strong> ${getDeltaBadge(locB.rainfall, locA.rainfall, "mm")}</td></tr>
        <tr><td>Soil Health Score</td><td><span class="badge badge-success">${locB.health}/100</span> ${getDeltaBadge(locB.health, locA.health, "pts")}</td></tr>
        <tr><td>Top Suitable Crops</td><td><strong>${locB.crops.join(", ")}</strong></td></tr>
      </table>
    </div>
  `;
}

function getDeltaBadge(valB, valA, unit) {
  const diff = Math.round((valB - valA) * 10) / 10;
  if (diff === 0) return `<span class="delta-neutral">0 ${unit}</span>`;
  if (diff > 0)  return `<span class="delta-pos">+${diff} ${unit}</span>`;
  return `<span class="delta-neg">${diff} ${unit}</span>`;
}

function renderHistoricalRunsComparison() {
  const wrap = document.getElementById("runsCompTableWrap");
  if (!wrap) return;

  const history = getAnalysisHistory();
  if (history.length < 2) {
    wrap.innerHTML = `<p class="muted-hint">Requires at least 2 analysis sessions to plot comparative deltas. Run another analysis session.</p>`;
    return;
  }

  const cur  = history[0];
  const prev = history[1];

  wrap.innerHTML = `
    <table class="comp-metric-table">
      <thead>
        <tr>
          <th>Metric / Parameter</th>
          <th>Previous Run (${prev.date || 'Run 1'})</th>
          <th>Current Run (${cur.date || 'Run 2'})</th>
          <th>Observed Delta</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Soil Health Score</td><td><strong>${prev.health?.score || '—'} / 100</strong></td><td><strong>${cur.health?.score || '—'} / 100</strong></td><td>${getDeltaBadge(cur.health?.score || 0, prev.health?.score || 0, 'pts')}</td></tr>
        <tr><td>Soil pH</td><td><strong>${prev.soil_params?.ph || '—'}</strong></td><td><strong>${cur.soil_params?.ph || '—'}</strong></td><td>${getDeltaBadge(cur.soil_params?.ph || 0, prev.soil_params?.ph || 0, '')}</td></tr>
        <tr><td>Nitrogen (N)</td><td><strong>${prev.soil_params?.n || '—'} kg/ha</strong></td><td><strong>${cur.soil_params?.n || '—'} kg/ha</strong></td><td>${getDeltaBadge(cur.soil_params?.n || 0, prev.soil_params?.n || 0, 'kg')}</td></tr>
        <tr><td>Phosphorus (P)</td><td><strong>${prev.soil_params?.p || '—'} kg/ha</strong></td><td><strong>${cur.soil_params?.p || '—'} kg/ha</strong></td><td>${getDeltaBadge(cur.soil_params?.p || 0, prev.soil_params?.p || 0, 'kg')}</td></tr>
        <tr><td>Potassium (K)</td><td><strong>${prev.soil_params?.k || '—'} kg/ha</strong></td><td><strong>${cur.soil_params?.k || '—'} kg/ha</strong></td><td>${getDeltaBadge(cur.soil_params?.k || 0, prev.soil_params?.k || 0, 'kg')}</td></tr>
        <tr><td>Top Crop Candidate</td><td><strong>${prev.crops?.[0]?.crop || '—'}</strong></td><td><strong>${cur.crops?.[0]?.crop || '—'}</strong></td><td><span class="badge badge-info">Complete</span></td></tr>
      </tbody>
    </table>
  `;
}

function renderCropComparison() {
  const cropA = document.getElementById("comp-crop-a").value.toLowerCase();
  const cropB = document.getElementById("comp-crop-b").value.toLowerCase();

  const benchA = CROP_AGRO_ECONOMICS[cropA] || { profit: "₹65,000 / ac", days: "90d", season: "All", water: "Moderate" };
  const benchB = CROP_AGRO_ECONOMICS[cropB] || { profit: "₹65,000 / ac", days: "90d", season: "All", water: "Moderate" };

  const wrap = document.getElementById("cropCompTableWrap");
  if (!wrap) return;

  wrap.innerHTML = `
    <table class="comp-metric-table">
      <thead>
        <tr>
          <th>Factor</th>
          <th>${cropA.toUpperCase()} Profile</th>
          <th>${cropB.toUpperCase()} Profile</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Estimated Profit</td><td><strong style="color:#166534">${benchA.profit}</strong></td><td><strong style="color:#166534">${benchB.profit}</strong></td></tr>
        <tr><td>Growth Duration</td><td><strong>${benchA.days}</strong></td><td><strong>${benchB.days}</strong></td></tr>
        <tr><td>Cultivation Season</td><td><span class="badge badge-primary">${benchA.season}</span></td><td><span class="badge badge-info">${benchB.season}</span></td></tr>
        <tr><td>Water Demand</td><td><strong>${benchA.water}</strong></td><td><strong>${benchB.water}</strong></td></tr>
      </tbody>
    </table>
  `;
}


/* ══════════════════ TIME-SERIES CHARTS ═════════════════════ */
function initTimeSeriesPage() {
  if (typeof Chart === "undefined") return;

  const ctxHealth = document.getElementById("chartSoilHealth")?.getContext("2d");
  if (ctxHealth) {
    if (chartHealthInstance) chartHealthInstance.destroy();
    chartHealthInstance = new Chart(ctxHealth, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [
          {
            label: "Soil Health Index",
            data: [72, 74, 75, 73, 70, 78, 84, 86, 83, 80, 78, 76],
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            tension: 0.35,
            fill: true,
            pointRadius: 4
          },
          {
            label: "Optimal Benchmark (80+)",
            data: [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80],
            borderColor: "#94a3b8",
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 50, max: 100 } } }
    });
  }

  const ctxPh = document.getElementById("chartPhVariation")?.getContext("2d");
  if (ctxPh) {
    if (chartPhInstance) chartPhInstance.destroy();
    chartPhInstance = new Chart(ctxPh, {
      type: "line",
      data: {
        labels: ["Trial 1", "Trial 2", "Trial 3", "Trial 4", "Trial 5", "Trial 6", "Trial 7", "Trial 8"],
        datasets: [
          {
            label: "Measured Soil pH",
            data: [6.2, 6.4, 6.5, 6.8, 6.7, 6.5, 6.6, 6.5],
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.15)",
            tension: 0.3,
            fill: true,
            pointRadius: 5
          },
          {
            label: "Neutral (7.0)",
            data: [7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
            borderColor: "#ef4444",
            borderDash: [4, 4],
            pointRadius: 0
          }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 4.5, max: 9.0 } } }
    });
  }

  const ctxYield = document.getElementById("chartRainfallYield")?.getContext("2d");
  if (ctxYield) {
    if (chartYieldInstance) chartYieldInstance.destroy();
    chartYieldInstance = new Chart(ctxYield, {
      type: "line",
      data: {
        labels: ["20mm", "50mm", "80mm", "110mm", "140mm", "170mm", "200mm", "230mm", "260mm", "300mm"],
        datasets: [
          { label: "Rice Suitability (%)", data: [10, 25, 45, 65, 82, 94, 98, 95, 90, 85], borderColor: "#10b981", tension: 0.4 },
          { label: "Muskmelon Suitability (%)", data: [92, 95, 88, 65, 40, 20, 10, 5, 0, 0], borderColor: "#f59e0b", tension: 0.4 },
          { label: "Cotton / Maize Suitability (%)", data: [40, 70, 94, 96, 85, 70, 50, 35, 20, 10], borderColor: "#6366f1", tension: 0.4 }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } } }
    });
  }
}


/* ══════════════════ GEOSPATIAL MAP (LEAFLET) ═══════════════ */
let selectedStation = RESEARCH_STATIONS[1];

function initMappingPage() {
  setTimeout(() => {
    renderLeafletMap();
  }, 100);
}

function renderLeafletMap() {
  const mapDiv = document.getElementById("geoLeafletMap");
  if (!mapDiv || typeof L === "undefined") return;

  if (leafletMapInstance) {
    leafletMapInstance.invalidateSize();
    return;
  }

  leafletMapInstance = L.map("geoLeafletMap").setView([18.5204, 75.0], 7);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "© OpenStreetMap contributors | SoilSense"
  }).addTo(leafletMapInstance);

  mapMarkers = [];
  RESEARCH_STATIONS.forEach(station => {
    const marker = L.marker([station.lat, station.lon]).addTo(leafletMapInstance);
    marker.bindPopup(`<strong>${station.name}</strong><br/>${station.soilType}<br/>Health: ${station.health}/100`);
    marker.on("click", () => {
      selectStation(station);
    });
    mapMarkers.push(marker);
  });

  selectStation(selectedStation);
}

function selectStation(station) {
  selectedStation = station;
  document.getElementById("stationName").textContent        = station.name;
  document.getElementById("stationSoilType").textContent    = station.soilType;
  document.getElementById("stationDescription").textContent = station.description;
  document.getElementById("stPh").textContent               = station.ph;
  document.getElementById("stNPK").textContent              = `${station.n} - ${station.p} - ${station.k}`;
  document.getElementById("stRainfall").textContent         = `${station.rainfall} mm`;
  document.getElementById("stHealth").textContent           = `${station.health} / 100`;

  const cropsWrap = document.getElementById("stCrops");
  if (cropsWrap) {
    cropsWrap.innerHTML = station.crops.map(c => `<span class="crop-pill">${c}</span>`).join("");
  }
}

function loadStationIntoAnalysis() {
  if (!selectedStation) return;
  document.getElementById("ph").value          = selectedStation.ph;
  document.getElementById("n").value           = selectedStation.n;
  document.getElementById("p").value           = selectedStation.p;
  document.getElementById("k").value           = selectedStation.k;
  document.getElementById("rainfall").value    = selectedStation.rainfall;
  document.getElementById("temperature").value = selectedStation.temp;
  document.getElementById("humidity").value    = selectedStation.humidity;

  showPage("analysis");
  showToast(`✅ Loaded ${selectedStation.name} telemetry into Analysis form!`);
}


/* ══════════════════ CORRELATION MATRIX ═════════════════════ */
async function initCorrelationPage() {
  try {
    const res  = await fetch("/analytics/correlation");
    const data = await res.json();
    if (data.success) {
      renderCorrelationHeatmap(data.features, data.matrix);
      renderCorrelationInsights(data.insights);
    }
  } catch (err) {
    console.error("Correlation fetch error:", err);
  }
}

function renderCorrelationHeatmap(features, matrix) {
  const wrap = document.getElementById("corrHeatmapWrap");
  if (!wrap || !features || !matrix) return;

  let html = `<table class="corr-table"><thead><tr><th>Feature</th>`;
  features.forEach(f => { html += `<th>${f.toUpperCase()}</th>`; });
  html += `</tr></thead><tbody>`;

  features.forEach(f1 => {
    html += `<tr><td><strong>${f1.toUpperCase()}</strong></td>`;
    features.forEach(f2 => {
      const val = matrix[f1]?.[f2] ?? 0;
      const colorStyle = getCorrelationColor(val);
      html += `<td style="${colorStyle}">${val > 0 ? "+" : ""}${val}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  wrap.innerHTML = html;
}

function getCorrelationColor(r) {
  if (r === 1.0) return "background:#10b981;color:#fff;font-weight:700;";
  if (r > 0.5)   return "background:rgba(16, 185, 129, 0.5);color:#064e3b;font-weight:700;";
  if (r > 0.15)  return "background:rgba(16, 185, 129, 0.2);color:#064e3b;";
  if (r < -0.4)  return "background:rgba(239, 68, 68, 0.4);color:#7f1d1d;font-weight:700;";
  if (r < -0.15) return "background:rgba(239, 68, 68, 0.2);color:#7f1d1d;";
  return "background:#f8fafc;color:#475569;";
}

function renderCorrelationInsights(insights) {
  const wrap = document.getElementById("corrInsightsList");
  if (!wrap || !insights) return;
  wrap.innerHTML = "";
  insights.forEach((ins, idx) => {
    wrap.innerHTML += `
      <div class="insight-card">
        <span class="insight-num">${idx + 1}</span>
        <p>${ins}</p>
      </div>
    `;
  });
}


/* ══════════════════ DATASET PREVIEW ════════════════════════ */
function debounceDatasetSearch() {
  clearTimeout(datasetSearchTimer);
  datasetSearchTimer = setTimeout(() => {
    fetchDatasetPreview(1);
  }, 300);
}

async function fetchDatasetPreview(page = 1) {
  currentDatasetPage = page;
  const search = document.getElementById("datasetSearchInp")?.value.trim() || "";
  try {
    const url = `/dataset/preview?page=${page}&limit=15&crop=${encodeURIComponent(search)}`;
    const res  = await fetch(url);
    const data = await res.json();

    if (data.success) {
      renderDatasetTable(data.rows, (page - 1) * 15 + 1);
      document.getElementById("datasetPageIndicator").textContent = `Page ${data.page} of ${data.total_pages}`;
      document.getElementById("datasetRecordCount").textContent   = `Showing ${data.rows.length} of ${data.total} samples`;
      document.getElementById("btnPrevPage").disabled = data.page <= 1;
      document.getElementById("btnNextPage").disabled = data.page >= data.total_pages;
    }
  } catch (err) {
    console.error("Dataset preview error:", err);
  }
}

function renderDatasetTable(rows, startIdx) {
  const tbody = document.getElementById("datasetTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";
  if (!rows || !rows.length) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:#6b7280">No dataset records match the filter.</td></tr>`;
    return;
  }
  rows.forEach((r, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${startIdx + idx}</td>
      <td>${r.N}</td>
      <td>${r.P}</td>
      <td>${r.K}</td>
      <td>${r.temperature}°C</td>
      <td>${r.humidity}%</td>
      <td>${r.ph}</td>
      <td>${r.rainfall} mm</td>
      <td><span class="badge badge-primary">${r.label}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function changeDatasetPage(delta) {
  fetchDatasetPreview(currentDatasetPage + delta);
}


/* ══════════════════ RESEARCH LAB NOTES ═════════════════════ */
async function renderResearchNotes() {
  try {
    const res  = await fetch("/api/research-notes");
    const data = await res.json();
    const notes = data.success ? data.notes : [];

    const container = document.getElementById("notesContainer");
    if (!container) return;

    if (!notes.length) {
      container.innerHTML = `<p class="muted-hint">No laboratory notes recorded yet. Write your first diagnostic observation.</p>`;
      return;
    }

    container.innerHTML = "";
    notes.forEach(n => {
      const card = document.createElement("div");
      card.className = "note-card";
      card.innerHTML = `
        <div class="note-card-head">
          <h4>${n.title}</h4>
          <button class="note-del-btn" onclick="deleteResearchNote('${n.id}')" title="Delete Note">✕</button>
        </div>
        <div class="note-meta">
          <span>👤 ${n.author || 'Agronomist'}</span>
          <span>📅 ${n.created_at || 'Just now'}</span>
          ${n.top_crop && n.top_crop !== '—' ? `<span>🌾 Crop: ${n.top_crop}</span>` : ''}
        </div>
        <p class="note-content-text">${n.content}</p>
        <div class="note-tags">
          ${(n.tags || []).map(t => `<span class="note-tag">#${t}</span>`).join("")}
        </div>
      `;
      container.appendChild(card);
    });

  } catch (err) {
    console.error("Notes render error:", err);
  }
}

async function saveResearchNote() {
  const title   = document.getElementById("noteTitle").value.trim();
  const author  = document.getElementById("noteAuthor").value.trim();
  const tagsRaw = document.getElementById("noteTags").value.trim();
  const content = document.getElementById("noteContent").value.trim();

  if (!title || !content) {
    showToast("Please enter both a title and observation content.", true);
    return;
  }

  const tags = tagsRaw ? tagsRaw.split(",").map(t => t.trim()) : ["Observation"];

  await saveResearchNoteDirect(title, content, tags, author);
  document.getElementById("noteTitle").value = "";
  document.getElementById("noteContent").value = "";
  renderResearchNotes();
}

async function saveResearchNoteDirect(title, content, tags, author = "Dr. Anuja Patil") {
  try {
    const payload = {
      title,
      content,
      tags,
      author,
      soil_params: lastPayload?.soil_params || {},
      top_crop: lastPayload?.crops?.[0]?.crop || "—",
      health_score: lastPayload?.health?.score || 0
    };
    const res  = await fetch("/api/research-notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast("💾 Saved note to Agronomic Notebook!");
      if (document.getElementById("page-notes")?.classList.contains("active")) {
        renderResearchNotes();
      }
    }
  } catch (err) {
    showToast("Note save failed.", true);
  }
}

async function deleteResearchNote(id) {
  try {
    const res = await fetch(`/api/research-notes?id=${encodeURIComponent(id)}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("🗑️ Note removed.");
      renderResearchNotes();
    }
  } catch (e) {
    showToast("Delete failed", true);
  }
}

function saveToResearchNotesFromCurrent() {
  if (!lastPayload) {
    showToast("Run soil analysis first to save snapshot.", true);
    return;
  }
  const topCrop = lastPayload.crops[0]?.crop || "Selected Crop";
  const p = lastPayload.soil_params;
  saveResearchNoteDirect(
    `Diagnostic Run: ${topCrop.toUpperCase()} Suitability`,
    `Evaluation conducted: pH=${p.ph}, N=${p.n}, P=${p.p}, K=${p.k} kg/ha. Health Score: ${lastPayload.health.score}/100. Match: ${lastPayload.crops[0]?.probability}%.`,
    ["Diagnostic", topCrop, "Field Run"]
  );
}

function exportNotesMarkdown() {
  fetch("/api/research-notes")
    .then(r => r.json())
    .then(data => {
      const notes = data.notes || [];
      let md = "# SoilSense Research Notes\n\n";
      notes.forEach(n => {
        md += `## ${n.title}\n**Author:** ${n.author} | **Date:** ${n.created_at} | **Tags:** ${n.tags.join(", ")}\n\n${n.content}\n\n---\n\n`;
      });
      const blob = new Blob([md], { type: "text/markdown" });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `SoilSense_Notes_${Date.now()}.md`;
      a.click();
    });
}


/* ══════════════════ PDF REPORT EXPORT ══════════════════════ */
async function generateReport() {
  if (!lastPayload) { showToast("Run an analysis first.", true); return; }

  showLoading("Compiling research PDF report…");
  try {
    const res  = await fetch("/generate-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...lastPayload,
        cnn_result: lastCnnResult,
        lang: currentLang || "en"
      })
    });
    const data = await res.json();
    hideLoading();

    if (data.success && data.download_url) {
      saveReportToHistory(data.filename, data.download_url);
      window.open(data.download_url, "_blank");
      showToast("📄 PDF Report downloaded!");
      showPage("reports");
    } else {
      showToast("Report error: " + (data.error || "Unknown"), true);
    }
  } catch (err) {
    hideLoading();
    showToast("PDF generation failed.", true);
  }
}

function saveReportToHistory(filename, url) {
  const reports = getSavedReports();
  reports.unshift({
    filename,
    url,
    date: new Date().toLocaleString(),
    health: lastPayload?.health?.score || "—",
    crop: lastPayload?.crops?.[0]?.crop || "—"
  });
  localStorage.setItem("ss_reports_history", JSON.stringify(reports.slice(0, 30)));
}

function getSavedReports() {
  try { return JSON.parse(localStorage.getItem("ss_reports_history") || "[]"); } catch { return []; }
}

function renderReports() {
  const container = document.getElementById("reportsListContainer");
  if (!container) return;
  const reports = getSavedReports();

  if (!reports.length) {
    container.innerHTML = `<p class="muted-hint">No reports generated in this session yet. Run an analysis and click <strong>Generate PDF</strong>.</p>`;
    return;
  }

  container.innerHTML = `
    <table class="dataset-table">
      <thead>
        <tr>
          <th>Document</th>
          <th>Generated Timestamp</th>
          <th>Health Index</th>
          <th>Recommended Crop</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${reports.map(r => `
          <tr>
            <td><strong>${r.filename}</strong></td>
            <td>${r.date}</td>
            <td><span class="badge badge-success">${r.health}/100</span></td>
            <td><strong>${r.crop}</strong></td>
            <td><a href="${r.url}" class="btn btn-outline btn-sm" download>📥 Download PDF</a></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}


/* ══════════════════ STORAGE & SETTINGS ═════════════════════ */
function saveLastAnalysis(data) {
  try { localStorage.setItem("ss_last_analysis", JSON.stringify(data)); } catch (e) {}
}
function getLastAnalysis() {
  try { return JSON.parse(localStorage.getItem("ss_last_analysis") || "null"); } catch { return null; }
}

function recordAnalysisHistory(data) {
  try {
    const history = getAnalysisHistory();
    history.unshift({
      ...data,
      date: new Date().toLocaleTimeString()
    });
    localStorage.setItem("ss_analysis_history", JSON.stringify(history.slice(0, 20)));
  } catch (e) {}
}

function getAnalysisHistory() {
  try { return JSON.parse(localStorage.getItem("ss_analysis_history") || "[]"); } catch { return []; }
}

function openSettings() {
  const s = loadSettings();
  document.getElementById("inp-api-key").value      = s.apiKey || "";
  document.getElementById("inp-def-location").value = s.defaultLocation || "";
  document.getElementById("settings-modal").classList.add("open");
}
function closeSettings() {
  document.getElementById("settings-modal").classList.remove("open");
}
function saveSettings() {
  const apiKey = document.getElementById("inp-api-key").value.trim();
  const defLoc = document.getElementById("inp-def-location").value.trim();
  localStorage.setItem("ss_api_key", apiKey);
  localStorage.setItem("ss_def_location", defLoc);
  closeSettings();
  showToast("✅ Settings saved!");
}
function loadSettings() {
  return {
    apiKey:          localStorage.getItem("ss_api_key") || "",
    defaultLocation: localStorage.getItem("ss_def_location") || "",
  };
}


/* ══════════════════ TOAST & OVERLAYS ═══════════════════════ */
let toastTimer = null;
function showToast(msg, isError = false) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.className   = "toast" + (isError ? " toast-error" : " toast-success") + " show";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.className = "toast"; }, 3400);
}

function showLoading(msg = "Processing agronomic calculations…") {
  const overlay = document.getElementById("loadingOverlay");
  const text    = document.getElementById("loadingMsg");
  if (text) text.textContent = msg;
  if (overlay) overlay.style.display = "flex";
}
function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "none";
}
