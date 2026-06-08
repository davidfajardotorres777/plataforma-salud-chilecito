const state = {
  data: null,
  search: "",
  editingCentroId: null,
  editingPacienteId: null,
  editingTurnoId: null
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function text(value) {
  return value === undefined || value === null || value === "" ? "-" : String(value);
}

function escapeHtml(value) {
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
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
  renderDisponibilidad();
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
      const slot = state.data.disponibilidad?.find((item) => item.medico.id === m.id);
      const precio = slot ? slot.precio_estimado : 0;
      return `<option value="${m.id}" data-precio="${precio}">${m.nombre} - ${especialidad} - ${centro}</option>`;
    })
    .join("");
  updateTurnoEstimatedPrice();
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
      <td class="actions-cell">
        <select class="estado-select" data-id="${t.id}">
          ${["PENDIENTE", "CONFIRMADO", "ATENDIDO", "CANCELADO", "AUSENTE"].map((e) =>
            `<option ${e === t.estado ? "selected" : ""}>${e}</option>`
          ).join("")}
        </select>
        <button class="secondary edit-turno" type="button" data-id="${t.id}">Editar</button>
        <button class="danger delete-turno" type="button" data-id="${t.id}">Eliminar</button>
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

  $$(".edit-turno").forEach((button) => {
    button.addEventListener("click", () => {
      const turno = state.data.turnos.find((t) => t.id === Number(button.dataset.id));
      if (!turno) return;
      const form = $("#turnoForm");
      const fields = form.elements;
      state.editingTurnoId = turno.id;
      $("#turnoFormTitle").textContent = "Editar turno";
      fields.id.value = turno.id;
      fields.paciente_id.value = turno.paciente_id;
      fields.medico_id.value = turno.medico_id;
      fields.fecha.value = turno.fecha;
      fields.hora.value = turno.hora;
      fields.precio.value = turno.precio;
      fields.estado.value = turno.estado;
      fields.motivo.value = turno.motivo;
      fields.paciente_id.focus();
    });
  });

  $$(".delete-turno").forEach((button) => {
    button.addEventListener("click", async () => {
      const turno = state.data.turnos.find((t) => t.id === Number(button.dataset.id));
      if (!turno) return;
      const ok = confirm(`Eliminar el turno de ${turno.paciente?.nombre || "paciente"} del ${turno.fecha} ${turno.hora}?`);
      if (!ok) return;
      await api(`/api/turnos/${turno.id}/eliminar`, {
        method: "POST",
        body: "{}"
      });
      resetTurnoForm();
      await loadDashboard();
      showToast("Turno eliminado");
    });
  });
}

function renderDisponibilidad() {
  const rows = state.data.disponibilidad || [];
  $("#disponibilidadList").innerHTML = rows.map((item) => `
    <article class="record availability-row">
      <strong>${item.dia_semana} ${item.hora_inicio}-${item.hora_fin}</strong>
      <span>${text(item.medico?.nombre)} - ${text(item.medico?.especialidad?.nombre)} - ${text(item.medico?.centro?.nombre)}</span>
      <span>Cupos ${item.cupos_libres}/${item.cupo_diario} - Precio estimado $${Number(item.precio_estimado || 0).toLocaleString("es-AR")}</span>
    </article>
  `).join("");
}

function renderPacientes() {
  const rows = state.data.pacientes
    .filter((p) => matchesSearch(p.nombre, p.dni, p.distrito, p.obra_social));
  $("#pacientesCount").textContent = `${rows.length} registros`;
  $("#pacientesList").innerHTML = rows.map((p) => `
    <article class="record">
      <strong>${p.nombre}</strong>
      <span>DNI ${p.dni} - ${p.distrito} - ${p.telefono} - ${p.obra_social}</span>
      <button class="secondary edit-paciente" type="button" data-id="${p.id}">Editar</button>
    </article>
  `).join("");

  $$(".edit-paciente").forEach((button) => {
    button.addEventListener("click", () => {
      const paciente = state.data.pacientes.find((p) => p.id === Number(button.dataset.id));
      if (!paciente) return;
      const form = $("#pacienteForm");
      const fields = form.elements;
      state.editingPacienteId = paciente.id;
      $("#pacienteFormTitle").textContent = "Editar paciente";
      fields.id.value = paciente.id;
      fields.dni.value = paciente.dni;
      fields.nombre.value = paciente.nombre;
      fields.telefono.value = paciente.telefono;
      fields.distrito.value = paciente.distrito;
      fields.obra_social.value = paciente.obra_social;
      fields.dni.focus();
    });
  });
}

function renderCentros() {
  $("#centrosList").innerHTML = state.data.centros.map((c) => {
    const medicos = state.data.medicos.filter((m) => m.centro_id === c.id);
    return `
      <article class="center-item">
        <strong>${c.nombre}</strong>
        <span>${c.tipo} - ${c.distrito} - ${c.telefono}</span>
        <p>${c.direccion}</p>
        <div class="mini-list">
          ${medicos.map((m) => `<p>${m.nombre} - ${m.especialidad?.nombre || "General"}</p>`).join("")}
        </div>
        <button class="secondary edit-centro" type="button" data-id="${c.id}">Editar</button>
      </article>
    `;
  }).join("");

  $$(".edit-centro").forEach((button) => {
    button.addEventListener("click", () => {
      const centro = state.data.centros.find((c) => c.id === Number(button.dataset.id));
      if (!centro) return;
      const form = $("#centroForm");
      const fields = form.elements;
      state.editingCentroId = centro.id;
      $("#centroFormTitle").textContent = "Editar centro";
      fields.id.value = centro.id;
      fields.nombre.value = centro.nombre;
      fields.direccion.value = centro.direccion;
      fields.distrito.value = centro.distrito;
      fields.telefono.value = centro.telefono;
      fields.tipo.value = centro.tipo;
      fields.nombre.focus();
    });
  });
}

function renderDocumentos() {
  const rows = state.data.documentos
    .filter((d) => matchesSearch(d.paciente?.nombre, d.tipo, d.nombre_archivo));
  $("#documentosCount").textContent = `${rows.length} archivos`;
  $("#documentosList").innerHTML = rows.length ? rows.map((d) => `
    <article class="record">
      <strong>${d.nombre_archivo}</strong>
      <span>${d.tipo} - ${text(d.paciente?.nombre)} - ${text(d.mime_type)} - ${d.tamano_bytes} bytes</span>
      <button class="secondary view-documento" type="button" data-id="${d.id}">Ver documento</button>
    </article>
  `).join("") : `<article class="record"><strong>Sin documentos cargados</strong><span>Adjuntos locales del paciente</span></article>`;

  $$(".view-documento").forEach((button) => {
    button.addEventListener("click", () => openDocument(button.dataset.id));
  });
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
    const payload = formDataToObject(event.target);
    delete payload.id;
    const path = state.editingPacienteId ? `/api/pacientes/${state.editingPacienteId}` : "/api/pacientes";
    await api(path, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    resetPacienteForm();
    await loadDashboard();
    showToast("Paciente guardado");
  });

  $("#cancelPacienteEdit").addEventListener("click", resetPacienteForm);

  $("#centroForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = formDataToObject(event.target);
    delete payload.id;
    const path = state.editingCentroId ? `/api/centros/${state.editingCentroId}` : "/api/centros";
    await api(path, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    resetCentroForm();
    await loadDashboard();
    showToast("Centro guardado");
  });

  $("#cancelCentroEdit").addEventListener("click", resetCentroForm);

  $("#turnoForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = formDataToObject(event.target);
    delete payload.id;
    const path = state.editingTurnoId ? `/api/turnos/${state.editingTurnoId}` : "/api/turnos";
    await api(path, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    resetTurnoForm();
    await loadDashboard();
    showToast("Turno reservado");
  });

  $("#cancelTurnoEdit").addEventListener("click", resetTurnoForm);

  $("#turnoMedico").addEventListener("change", updateTurnoEstimatedPrice);

  $("#documentoForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const data = formDataToObject(form);
    const file = form.archivo.files[0];
    data.nombre_archivo = file.name;
    data.mime_type = file.type || "application/octet-stream";
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

  $("#closeDocument").addEventListener("click", () => $("#documentDialog").close());
}

function resetPacienteForm() {
  const form = $("#pacienteForm");
  state.editingPacienteId = null;
  form.reset();
  form.elements.id.value = "";
  form.elements.obra_social.value = "Sin obra social";
  $("#pacienteFormTitle").textContent = "Paciente";
}

function resetTurnoForm() {
  const form = $("#turnoForm");
  state.editingTurnoId = null;
  form.reset();
  form.elements.id.value = "";
  form.elements.precio.value = 0;
  $("#turnoFormTitle").textContent = "Nuevo turno";
  updateTurnoEstimatedPrice();
}

function updateTurnoEstimatedPrice() {
  const select = $("#turnoMedico");
  const selected = select.options[select.selectedIndex];
  const form = $("#turnoForm");
  if (!selected || state.editingTurnoId) return;
  form.elements.precio.value = selected.dataset.precio || 0;
}

function resetCentroForm() {
  const form = $("#centroForm");
  state.editingCentroId = null;
  form.reset();
  form.elements.id.value = "";
  $("#centroFormTitle").textContent = "Centro de salud";
}

async function openDocument(id) {
  const doc = await api(`/api/documentos/${id}`);
  $("#documentTitle").textContent = doc.nombre_archivo;
  $("#documentMeta").textContent = `${doc.tipo} - ${text(doc.paciente?.nombre)} - ${doc.mime_type} - ${doc.tamano_bytes} bytes`;
  const preview = $("#documentPreview");
  const mime = doc.mime_type || "application/octet-stream";
  if (mime.startsWith("image/")) {
    preview.innerHTML = `<img src="${doc.data_url}" alt="${escapeHtml(doc.nombre_archivo)}">`;
  } else if (mime === "application/pdf") {
    preview.innerHTML = `<iframe title="${escapeHtml(doc.nombre_archivo)}" src="${doc.data_url}"></iframe>`;
  } else if (mime.startsWith("text/") || mime.includes("json")) {
    const bytes = Uint8Array.from(atob(doc.contenido_base64), (char) => char.charCodeAt(0));
    const content = new TextDecoder("utf-8").decode(bytes);
    preview.innerHTML = `<pre>${escapeHtml(content)}</pre>`;
  } else {
    preview.innerHTML = `
      <div class="empty-preview">
        <strong>Vista previa no disponible para este tipo de archivo</strong>
        <a download="${escapeHtml(doc.nombre_archivo)}" href="${doc.data_url}">Descargar archivo</a>
      </div>
    `;
  }
  $("#documentDialog").showModal();
}

wireEvents();
loadDashboard().catch((error) => {
  $("#apiStatus").textContent = "API no disponible";
  showToast(error.message);
});
