const state = {
  data: null,
  search: ""
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function text(value) {
  return value === undefined || value === null || value === "" ? "-" : String(value);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Operacion no completada");
  }
  return payload;
}

async function loadDashboard() {
  state.data = await api("/api/dashboard");
  render();
  $("#apiStatus").textContent = "API local conectada";
}

function render() {
  renderMetrics();
  fillSelects();
  renderTurnos();
  renderPacientes();
  renderCentros();
  renderDocumentos();
}

function renderMetrics() {
  const m = state.data.metricas;
  $("#metricCentros").textContent = m.centros;
  $("#metricPacientes").textContent = m.pacientes;
  $("#metricPendientes").textContent = m.turnos_pendientes;
  $("#metricConfirmados").textContent = m.turnos_confirmados;
  $("#metricDocumentos").textContent = m.documentos;
}

function fillSelects() {
  const pacienteOptions = state.data.pacientes
    .map((p) => `<option value="${p.id}">${p.nombre} - DNI ${p.dni}</option>`)
    .join("");
  $("#turnoPaciente").innerHTML = pacienteOptions;
  $("#documentoPaciente").innerHTML = pacienteOptions;

  $("#turnoMedico").innerHTML = state.data.medicos
    .map((m) => {
      const centro = m.centro ? m.centro.nombre : "Sin centro";
      const especialidad = m.especialidad ? m.especialidad.nombre : "Sin especialidad";
      return `<option value="${m.id}">${m.nombre} - ${especialidad} - ${centro}</option>`;
    })
    .join("");
}

function matchesSearch(...values) {
  if (!state.search) return true;
  const haystack = values.map((v) => text(v).toLowerCase()).join(" ");
  return haystack.includes(state.search);
}

function renderTurnos() {
  const rows = state.data.turnos
    .filter((t) => matchesSearch(t.paciente?.nombre, t.medico?.nombre, t.centro?.nombre, t.estado))
    .sort((a, b) => `${a.fecha} ${a.hora}`.localeCompare(`${b.fecha} ${b.hora}`));

  $("#turnosCount").textContent = `${rows.length} registros`;
  $("#turnosBody").innerHTML = rows.map((t) => `
    <tr>
      <td>${t.fecha} ${t.hora}</td>
      <td>${text(t.paciente?.nombre)}<br><small>DNI ${text(t.paciente?.dni)}</small></td>
      <td>${text(t.medico?.nombre)}<br><small>${text(t.medico?.especialidad?.nombre)}</small></td>
      <td>${text(t.centro?.nombre)}<br><small>${text(t.centro?.distrito)}</small></td>
      <td><span class="status ${t.estado}">${t.estado}</span></td>
      <td>
        <select class="estado-select" data-id="${t.id}">
          ${["PENDIENTE", "CONFIRMADO", "ATENDIDO", "CANCELADO", "AUSENTE"].map((e) =>
            `<option ${e === t.estado ? "selected" : ""}>${e}</option>`
          ).join("")}
        </select>
      </td>
    </tr>
  `).join("");

  $$(".estado-select").forEach((select) => {
    select.addEventListener("change", async (event) => {
      const id = event.target.dataset.id;
      const estado = event.target.value;
      await api(`/api/turnos/${id}/estado`, {
        method: "POST",
        body: JSON.stringify({ estado })
      });
      showToast("Estado actualizado");
      await loadDashboard();
    });
  });
}

function renderPacientes() {
  const rows = state.data.pacientes
    .filter((p) => matchesSearch(p.nombre, p.dni, p.distrito, p.obra_social));
  $("#pacientesCount").textContent = `${rows.length} registros`;
  $("#pacientesList").innerHTML = rows.map((p) => `
    <article class="record">
      <strong>${p.nombre}</strong>
      <span>DNI ${p.dni} - ${p.distrito} - ${p.telefono} - ${p.obra_social}</span>
    </article>
  `).join("");
}

function renderCentros() {
  $("#centrosList").innerHTML = state.data.centros.map((c) => {
    const medicos = state.data.medicos.filter((m) => m.centro_id === c.id);
    return `
      <article class="center-item">
        <strong>${c.nombre}</strong>
        <span>${c.tipo} - ${c.distrito} - ${c.telefono}</span>
        <div class="mini-list">
          ${medicos.map((m) => `<p>${m.nombre} - ${m.especialidad?.nombre || "General"}</p>`).join("")}
        </div>
      </article>
    `;
  }).join("");
}

function renderDocumentos() {
  const rows = state.data.documentos
    .filter((d) => matchesSearch(d.paciente?.nombre, d.tipo, d.nombre_archivo));
  $("#documentosCount").textContent = `${rows.length} archivos`;
  $("#documentosList").innerHTML = rows.length ? rows.map((d) => `
    <article class="record">
      <strong>${d.nombre_archivo}</strong>
      <span>${d.tipo} - ${text(d.paciente?.nombre)} - ${d.tamano_bytes} bytes</span>
    </article>
  `).join("") : `<article class="record"><strong>Sin documentos cargados</strong><span>Adjuntos locales del paciente</span></article>`;
}

function formDataToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2200);
}

function wireEvents() {
  $$(".nav-tab").forEach((button) => {
    button.addEventListener("click", () => {
      $$(".nav-tab").forEach((b) => b.classList.remove("active"));
      $$(".view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      $(`#view-${button.dataset.view}`).classList.add("active");
    });
  });

  $("#globalSearch").addEventListener("input", (event) => {
    state.search = event.target.value.trim().toLowerCase();
    render();
  });

  $("#refreshData").addEventListener("click", async () => {
    await loadDashboard();
    showToast("Datos actualizados");
  });

  $("#resetData").addEventListener("click", async () => {
    await api("/api/reset", { method: "POST", body: "{}" });
    await loadDashboard();
    showToast("Datos demo reiniciados");
  });

  $("#pacienteForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api("/api/pacientes", {
      method: "POST",
      body: JSON.stringify(formDataToObject(event.target))
    });
    event.target.reset();
    await loadDashboard();
    showToast("Paciente guardado");
  });

  $("#turnoForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api("/api/turnos", {
      method: "POST",
      body: JSON.stringify(formDataToObject(event.target))
    });
    event.target.reset();
    await loadDashboard();
    showToast("Turno reservado");
  });

  $("#documentoForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = formDataToObject(form);
    const file = form.archivo.files[0];
    data.nombre_archivo = file.name;
    data.contenido_base64 = await fileToBase64(file);
    delete data.archivo;
    await api("/api/documentos", {
      method: "POST",
      body: JSON.stringify(data)
    });
    form.reset();
    await loadDashboard();
    showToast("Documento adjuntado");
  });
}

wireEvents();
loadDashboard().catch((error) => {
  $("#apiStatus").textContent = "API no disponible";
  showToast(error.message);
});
