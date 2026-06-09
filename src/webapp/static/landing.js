// Landing page for hospital-specific access
// This page is shown when a patient accesses the hospital's custom domain

const API_BASE = "/api";

// Load hospital configuration
async function loadHospitalConfig() {
  try {
    const response = await fetch(`${API_BASE}/configuracion-hospital`);
    const config = await response.json();
    
    if (config && config.length > 0) {
      const hospital = config[0];
      document.getElementById("hospitalName").textContent = hospital.nombre_hospital;
      document.getElementById("hospitalWelcome").textContent = hospital.mensaje_bienvenida || "Bienvenido al sistema de turnos";
      document.getElementById("hospitalPhone").textContent = hospital.telefono || "3825-422100";
      document.getElementById("hospitalEmail").textContent = hospital.email || "turnos@hospitalchilecito.gov.ar";
      
      // Apply hospital branding colors
      if (hospital.color_primario) {
        document.documentElement.style.setProperty("--primary", hospital.color_primario);
      }
    }
  } catch (error) {
    console.error("Error loading hospital config:", error);
  }
}

// Load symptoms for selection
async function loadSymptoms() {
  try {
    const response = await fetch(`${API_BASE}/sintomas`);
    const symptoms = await response.json();
    
    const symptomList = document.getElementById("symptomList");
    symptomList.innerHTML = symptoms.map(symptom => `
      <div class="symptom-card" data-symptom="${symptom.descripcion}" data-especialidad="${symptom.especialidad_id}">
        <div class="symptom-icon">🩺</div>
        <h3>${symptom.descripcion}</h3>
        <p>Especialidad: ${symptom.especialidad_nombre}</p>
        <button class="select-symptom-btn" onclick="selectSymptom('${symptom.descripcion}', ${symptom.especialidad_id})">
          Seleccionar
        </button>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error loading symptoms:", error);
  }
}

// Load specialties
async function loadSpecialties() {
  try {
    const response = await fetch(`${API_BASE}/especialidades`);
    const specialties = await response.json();
    
    const specialtyList = document.getElementById("specialtyList");
    specialtyList.innerHTML = specialties.map(specialty => `
      <div class="specialty-card">
        <h3>${specialty.nombre}</h3>
        <p>${specialty.descripcion || "Especialidad médica"}</p>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error loading specialties:", error);
  }
}

// Load availability for next 7 days
async function loadAvailability() {
  try {
    const response = await fetch(`${API_BASE}/disponibilidad`);
    const availability = await response.json();
    
    // Group by doctor and show next 7 days
    const availabilityList = document.getElementById("availabilityList");
    availabilityList.innerHTML = availability.slice(0, 10).map(item => `
      <div class="availability-card">
        <h3>${item.medico?.nombre}</h3>
        <p>${item.medico?.especialidad?.nombre}</p>
        <div class="time-slots">
          <span class="time-slot">${item.hora_inicio} - ${item.hora_fin}</span>
          <span class="cupos">Cupos: ${item.cupos_libres}/${item.cupo_diario}</span>
          <span class="price">$${Number(item.precio_estimado || 0).toLocaleString("es-AR")}</span>
        </div>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error loading availability:", error);
  }
}

// Load pricing information
async function loadPricing() {
  try {
    const response = await fetch(`${API_BASE}/tipos-consulta`);
    const types = await response.json();
    
    const pricingList = document.getElementById("pricingList");
    pricingList.innerHTML = types.map(type => `
      <div class="pricing-card">
        <h3>${type.nombre}</h3>
        <p>${type.descripcion || ""}</p>
      </div>
    `).join("");
  } catch (error) {
    console.error("Error loading pricing:", error);
  }
}

// Select symptom and redirect to booking
function selectSymptom(symptom, especialidadId) {
  // Store selection in sessionStorage
  sessionStorage.setItem("selectedSymptom", symptom);
  sessionStorage.setItem("selectedEspecialidadId", especialidadId);
  
  // Redirect to main booking page
  window.location.href = "/static/index.html";
}

// Initialize landing page
async function initLanding() {
  await loadHospitalConfig();
  await loadSymptoms();
  await loadSpecialties();
  await loadAvailability();
  await loadPricing();
}

// Run on page load
document.addEventListener("DOMContentLoaded", initLanding);
