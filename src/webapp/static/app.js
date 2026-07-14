const state = {
  data: null,
  search: "",
  editingCentroId: null,
  editingPacienteId: null,
  editingTurnoId: null,
  editingMedicoId: null
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
  const token = localStorage.getItem('salud_token');
  const headers = { "Content-Type": "application/json" };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const response = await fetch(path, {
    headers,
    ...options
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Operacion no completada");
  }
  return payload;
}

async function loadDashboard() {
  const centroId = localStorage.getItem("salud_centroid") || "";
  const url = centroId ? `/api/dashboard?centro_id=${centroId}` : "/api/dashboard";
  state.data = await api(url);
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
  // populate center filter
  const currentCentro = localStorage.getItem("salud_centroid") || "";
  const centerSelect = $("#centerFilter");
  if (centerSelect) {
    const options = ["<option value=''>Todos los centros</option>", ...state.data.centros.map(c => `<option value="${c.id}" ${String(c.id) === currentCentro ? 'selected' : ''}>${c.nombre}</option>`)]
      .join("");
    centerSelect.innerHTML = options;
    centerSelect.addEventListener("change", async (e) => {
      const val = e.target.value || "";
      localStorage.setItem("salud_centroid", String(val));
      await loadDashboard();
      showToast("Filtro de centro aplicado");
    });
  }

  const pacienteOptions = state.data.pacientes
    .map((p) => `<option value="${p.id}">${p.nombre} - DNI ${p.dni}</option>`)
    .join("");
  $("#turnoPaciente").innerHTML = pacienteOptions;
  $("#documentoPaciente").innerHTML = pacienteOptions;

  // Populate medico form selects
  const centroOptions = state.data.centros
    .map((c) => `<option value="${c.id}">${c.nombre}</option>`)
    .join("");
  $("#medicoCentro").innerHTML = centroOptions;

  const especialidadOptions = state.data.especialidades
    .map((e) => `<option value="${e.id}">${e.nombre}</option>`)
    .join("");
  $("#medicoEspecialidad").innerHTML = especialidadOptions;

  // Populate symptom dropdown (new for single-hospital model)
  const sintomaOptions = ["<option value=''>Seleccionar síntoma...</option>", ...state.data.sintomas.map(s => `<option value="${s.id}" data-especialidad-id="${s.especialidad_id}">${s.descripcion} - ${s.especialidad ? s.especialidad.nombre : 'N/A'} (Prioridad: ${s.prioridad})</option>`)].join("");
  $("#turnoSintoma").innerHTML = sintomaOptions;
  
  // Add symptom change listener to auto-select doctor
  $("#turnoSintoma").addEventListener("change", (e) => {
    const selectedOption = e.target.selectedOptions[0];
    if (selectedOption && selectedOption.value) {
      const especialidadId = parseInt(selectedOption.dataset.especialidadId);
      const edadPaciente = parseInt($("#turnoEdadPaciente").value) || 0;
      
      // Si el paciente es menor de 10 años, derivar a pediatra
      if (edadPaciente > 0 && edadPaciente < 10) {
        const pediatraEspecialidad = state.data.especialidades.find(e => e.nombre.toLowerCase() === "pediatria");
        if (pediatraEspecialidad) {
          const medicosPediatria = state.data.medicos.filter(m => m.especialidad && m.especialidad.id === pediatraEspecialidad.id);
          if (medicosPediatria.length > 0) {
            $("#turnoMedico").value = medicosPediatria[0].id;
            updateTurnoEstimatedPrice();
            updateHorariosDisponibles();
            showToast(`Paciente menor de 10 años: Derivado a Pediatría`);
            return;
          }
        }
      }
      
      // Para pacientes mayores de 10 años o sin edad especificada, usar la especialidad del síntoma
      const medicosEspecialidad = state.data.medicos.filter(m => m.especialidad && m.especialidad.id === especialidadId);
      if (medicosEspecialidad.length > 0) {
        $("#turnoMedico").value = medicosEspecialidad[0].id;
        updateTurnoEstimatedPrice();
        updateHorariosDisponibles();
        showToast(`Especialidad seleccionada: ${medicosEspecialidad[0].especialidad.nombre}`);
      }
    }
  });

  // Add doctor change listener to update available horarios
  $("#turnoMedico").addEventListener("change", () => {
    updateTurnoEstimatedPrice();
    updateHorariosDisponibles();
  });

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
  updateHorariosDisponibles(); // Inicializar horarios disponibles al cargar
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
  
  // Agrupar disponibilidad por médico
  const disponibilidadPorMedico = {};
  rows.forEach((item) => {
    const medicoId = item.medico?.id || 0;
    if (!disponibilidadPorMedico[medicoId]) {
      disponibilidadPorMedico[medicoId] = {
        medico: item.medico,
        horarios: []
      };
    }
    disponibilidadPorMedico[medicoId].horarios.push(item);
  });

  // Generar fechas específicas para los próximos 7 días
  const fechas = [];
  const diasSemana = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  for (let i = 0; i < 7; i++) {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + i);
    fechas.push({
      fecha: fecha.toISOString().split('T')[0],
      diaSemana: diasSemana[fecha.getDay()]
    });
  }

  $("#disponibilidadList").innerHTML = Object.values(disponibilidadPorMedico).map((grupo) => {
    const medico = grupo.medico;
    const horarios = grupo.horarios;
    
    // Filtrar horarios disponibles para los próximos 7 días
    const horariosDisponibles = fechas.map((fechaInfo) => {
      const horariosDia = horarios.filter((h) => h.dia_semana === fechaInfo.diaSemana);
      if (horariosDia.length === 0) return null;
      
      return `
        <div class="fecha-disponibilidad">
          <strong>${fechaInfo.fecha} (${fechaInfo.diaSemana})</strong>
          ${horariosDia.map((h) => `
            <div class="horario-slot">
              <span>${h.hora_inicio} - ${h.hora_fin}</span>
              <span>Cupos: ${h.cupos_libres}/${h.cupo_diario}</span>
              <span>Precio: $${Number(h.precio_estimado || 0).toLocaleString("es-AR")}</span>
            </div>
          `).join("")}
        </div>
      `;
    }).filter(Boolean).join("");

    return `
      <article class="record availability-row">
        <div class="medico-header">
          <strong>${text(medico?.nombre)}</strong>
          <span>${text(medico?.especialidad?.nombre)} - ${text(medico?.centro?.nombre)}</span>
        </div>
        <div class="medico-disponibilidad">
          ${horariosDisponibles || "<span class='no-disponible'>Sin disponibilidad para los próximos 7 días</span>"}
        </div>
      </article>
    `;
  }).join("");
}

function renderPacientes() {
  const rows = state.data.pacientes
    .filter((p) => matchesSearch(p.nombre, p.dni, p.distrito, p.obra_social));
  
  $("#pacientesCount").textContent = `${rows.length} registros`;
  $("#pacientesList").innerHTML = rows.map((p) => {
    const centro = state.data.centros.find(c => c.id === Number(p.centro_id));
    const centroNombre = centro ? centro.nombre : "Sin centro";
    return `
    <article class="record">
      <strong>${p.nombre}</strong>
      <span>DNI ${p.dni} - ${p.distrito} - ${p.telefono} - ${p.obra_social}</span>
      <span class="centro-info">${centroNombre}</span>
      <button class="secondary edit-paciente" type="button" data-id="${p.id}">Editar</button>
    </article>
  `}).join("");

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
          ${medicos.map((m) => `
            <p>
              ${m.nombre} - ${m.especialidad?.nombre || "General"}
              <button class="secondary edit-medico" type="button" data-id="${m.id}" style="margin-left: 10px; font-size: 12px;">Editar</button>
            </p>
          `).join("")}
        </div>
        <button class="secondary edit-centro" type="button" data-id="${c.id}">Editar centro</button>
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

  $$(".edit-medico").forEach((button) => {
    button.addEventListener("click", () => {
      const medico = state.data.medicos.find((m) => m.id === Number(button.dataset.id));
      if (!medico) return;
      const form = $("#medicoForm");
      const fields = form.elements;
      state.editingMedicoId = medico.id;
      $("#medicoFormTitle").textContent = "Editar medico";
      fields.id.value = medico.id;
      fields.nombre.value = medico.nombre;
      fields.centro_id.value = medico.centro_id;
      fields.especialidad_id.value = medico.especialidad_id;
      fields.telefono.value = medico.telefono;
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

  $("#forceSaveData").addEventListener("click", async () => {
    try {
      const result = await api("/api/persistence/force-save", { method: "POST", body: "{}" });
      if (result.success) {
        showToast("Datos guardados exitosamente");
      } else {
        showToast("Error: " + result.message);
      }
    } catch (e) {
      showToast("Error al forzar guardado: " + e.message);
    }
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
    
    // Agregar centro_id del hospital seleccionado
    const centroId = localStorage.getItem("salud_centroid");
    if (centroId) {
      payload.centro_id = Number(centroId);
    } else {
      // Si no hay centro seleccionado, usar el primer centro disponible
      if (state.data.centros && state.data.centros.length > 0) {
        payload.centro_id = state.data.centros[0].id;
      } else {
        showToast("Error: No hay centros disponibles");
        return;
      }
    }
    
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

  $("#medicoForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = formDataToObject(event.target);
    delete payload.id;
    // Agregar centro_id del hospital seleccionado
    const centroId = localStorage.getItem("salud_centroid");
    if (centroId) {
      payload.centro_id = Number(centroId);
    } else if (state.data.centros && state.data.centros.length > 0) {
      payload.centro_id = state.data.centros[0].id;
    } else {
      showToast("Error: No hay centros disponibles");
      return;
    }
    const path = state.editingMedicoId ? `/api/medicos/${state.editingMedicoId}` : "/api/medicos";
    const medico = await api(path, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    
    // Si se especificaron horarios de trabajo, crear una agenda
    if (payload.dia_semana && payload.hora_inicio && payload.hora_fin) {
      const agendaPayload = {
        medico_id: medico.id,
        dia_semana: payload.dia_semana,
        hora_inicio: payload.hora_inicio,
        hora_fin: payload.hora_fin,
        duracion_minutos: parseInt(payload.duracion_minutos) || 30,
        cupo_diario: parseInt(payload.cupo_diario) || 8
      };
      await api("/api/agendas", {
        method: "POST",
        body: JSON.stringify(agendaPayload)
      });
    }
    
    resetMedicoForm();
    await loadDashboard();
    showToast("Medico guardado");
  });

  $("#cancelMedicoEdit").addEventListener("click", resetMedicoForm);

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

function updateHorariosDisponibles() {
  const medicoId = $("#turnoMedico").value;
  const select = $("#turnoHorarioDisponible");
  
  if (!medicoId) {
    select.innerHTML = "<option value=''>Seleccionar horario disponible...</option>";
    return;
  }

  const medicoDisponibilidad = state.data.disponibilidad?.filter((item) => item.medico.id === Number(medicoId)) || [];
  
  if (medicoDisponibilidad.length === 0) {
    select.innerHTML = "<option value=''>Sin horarios disponibles</option>";
    return;
  }

  const diasSemana = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  const fechas = [];
  for (let i = 0; i < 7; i++) {
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + i);
    fechas.push({
      fecha: fecha.toISOString().split('T')[0],
      diaSemana: diasSemana[fecha.getDay()]
    });
  }

  const horariosOptions = ["<option value=''>Seleccionar horario disponible...</option>"];
  
  fechas.forEach((fechaInfo) => {
    const horariosDia = medicoDisponibilidad.filter((h) => h.dia_semana === fechaInfo.diaSemana);
    horariosDia.forEach((h) => {
      if (h.cupos_libres > 0) {
        horariosOptions.push(
          `<option value="${fechaInfo.fecha}|${h.hora_inicio}" data-precio="${h.precio_estimado}">${fechaInfo.fecha} (${fechaInfo.diaSemana}) - ${h.hora_inicio} - $${Number(h.precio_estimado || 0).toLocaleString("es-AR")} (${h.cupos_libres} cupos)</option>`
        );
      }
    });
  });

  select.innerHTML = horariosOptions.join("");
}

// Add listener to auto-fill fecha and hora when selecting horario disponible
$("#turnoHorarioDisponible").addEventListener("change", (e) => {
  const selected = e.target.selectedOptions[0];
  if (selected && selected.value) {
    const [fecha, hora] = selected.value.split("|");
    $("#turnoForm").elements.fecha.value = fecha;
    $("#turnoForm").elements.hora.value = hora;
    $("#turnoForm").elements.precio.value = selected.dataset.precio || 0;
  }
});

function resetCentroForm() {
  const form = $("#centroForm");
  state.editingCentroId = null;
  form.reset();
  form.elements.id.value = "";
  $("#centroFormTitle").textContent = "Centro de salud";
}

function resetMedicoForm() {
  const form = $("#medicoForm");
  state.editingMedicoId = null;
  form.reset();
  form.elements.id.value = "";
  $("#medicoFormTitle").textContent = "Medico";
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
