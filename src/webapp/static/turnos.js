/* turnos.js — Flujo publico de reserva de turnos por hospital/slug */

const PS = {
  slug: null,
  centroId: null,
  data: null,
  especialidad: null,
  medico: null,
  horario: null,
  precioInfo: null,
};

const $p = (s) => document.querySelector(s);
const $$p = (s) => Array.from(document.querySelectorAll(s));

function showToast(msg) {
  const t = $p("#pubToast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2200);
}

async function api(path) {
  const r = await fetch(path);
  const d = await r.json();
  if (!r.ok) throw new Error(d.error || "Error de API");
  return d;
}

function text(v) {
  return v == null || v === "" ? "-" : String(v);
}

/* ---- Init ---- */
async function init() {
  PS.slug = window.location.pathname.replace(/^\//, "").split("/")[0];
  if (!PS.slug) {
    PS.slug = new URLSearchParams(window.location.search).get("slug") || "";
  }
  if (!PS.slug) {
    $p("#hospitalAddress").textContent = "No se especifico un hospital";
    return;
  }
  try {
    const data = await api("/api/dashboard");
    PS.data = data;
    const centro = data.centros.find(c => c.slug === PS.slug);
    if (!centro) {
      $p("#hospitalAddress").textContent = `Hospital "${PS.slug}" no encontrado`;
      return;
    }
    PS.centroId = centro.id;
    $p("#hospitalName").textContent = centro.nombre;
    $p("#hospitalAddress").textContent = `${centro.direccion} - ${centro.distrito} | Tel: ${centro.telefono}`;
    renderEspecialidades();
  } catch (e) {
    $p("#hospitalAddress").textContent = "Error conectando con la plataforma";
  }
}

/* ---- Pasos ---- */
function goTo(step) {
  ["stepEspecialidades", "stepMedicos", "stepHorarios", "stepConfirmar", "stepExito"]
    .forEach(id => $p(`#${id}`).classList.add("hidden"));
  const panels = {
    1: "stepEspecialidades",
    2: "stepMedicos",
    3: "stepHorarios",
    4: "stepConfirmar",
    5: "stepExito",
  };
  $p(`#${panels[step]}`).classList.remove("hidden");

  $$(".pub-step").forEach(el => {
    const s = Number(el.dataset.step);
    el.classList.remove("active", "done");
    if (s === step) el.classList.add("active");
    else if (s < step) el.classList.add("done");
  });
}

/* ---- Paso 1: Especialidades ---- */
function renderEspecialidades() {
  const medicosCentro = PS.data.medicos.filter(m => m.centro_id === PS.centroId);
  const especialidadMap = {};
  for (const m of medicosCentro) {
    const esp = m.especialidad;
    if (!esp) continue;
    if (!especialidadMap[esp.id]) {
      especialidadMap[esp.id] = { esp, medicos: [], cupos: 0 };
    }
    especialidadMap[esp.id].medicos.push(m);
    const disp = PS.data.disponibilidad.find(d => d.medico && d.medico.id === m.id);
    if (disp) especialidadMap[esp.id].cupos += disp.cupos_libres;
  }

  const grid = $p("#especialidadesGrid");
  const especialidades = Object.values(especialidadMap);

  if (especialidades.length === 0) {
    grid.innerHTML = `<p style="color:var(--muted);grid-column:1/-1;">No hay especialidades disponibles en este hospital</p>`;
    return;
  }

  grid.innerHTML = especialidades.map(({ esp, medicos, cupos }) => `
    <div class="pub-card" data-esp-id="${esp.id}">
      <strong>${text(esp.nombre)}</strong>
      <span>${medicos.length} medico(s) disponible(s)</span>
      <div class="pub-card-badge">${cupos} turno(s) libre(s)</div>
    </div>
  `).join("");

  $$(".pub-card[data-esp-id]").forEach(card => {
    card.addEventListener("click", () => {
      const espId = Number(card.dataset.espId);
      PS.especialidad = especialidadMap[espId];
      goTo(2);
      renderMedicos();
    });
  });
}

/* ---- Paso 2: Medicos ---- */
function renderMedicos() {
  const grid = $p("#medicosGrid");
  const { esp, medicos } = PS.especialidad;

  grid.innerHTML = medicos.map(m => {
    const disp = PS.data.disponibilidad.find(d => d.medico && d.medico.id === m.id);
    const cupos = disp ? disp.cupos_libres : 0;
    const precio = disp ? disp.precio_estimado : 0;
    const cupoClass = cupos > 3 ? "disponibles" : cupos > 0 ? "pocos" : "llenos";
    return `
      <div class="pub-card" data-med-id="${m.id}">
        <strong>${text(m.nombre)}</strong>
        <span>Matricula: ${text(m.matricula)}</span>
        <span class="pub-card-cupos ${cupoClass}">${cupos} cupo(s) disponible(s)</span>
        <span class="pub-card-price">${precio > 0 ? "$" + Number(precio).toLocaleString("es-AR") : "Gratuito (publico)"}</span>
      </div>
    `;
  }).join("");

  $$(".pub-card[data-med-id]").forEach(card => {
    card.addEventListener("click", () => {
      const medId = Number(card.dataset.medId);
      PS.medico = medicos.find(m => m.id === medId);
      goTo(3);
      renderHorarios();
    });
  });
}

/* ---- Paso 3: Horarios ---- */
function renderHorarios() {
  const grid = $p("#horariosGrid");
  const agendas = PS.data.agendas.filter(a => a.medico_id === PS.medico.id);

  if (agendas.length === 0) {
    grid.innerHTML = `<p style="color:var(--muted);grid-column:1/-1;">No hay horarios configurados para este medico</p>`;
    return;
  }

  const disp = PS.data.disponibilidad.find(d => d.medico && d.medico.id === PS.medico.id);
  const cupos = disp ? disp.cupos_libres : 0;
  const precio = disp ? disp.precio_estimado : 0;

  grid.innerHTML = agendas.map(a => `
    <div class="pub-card" data-agenda-id="${a.id}">
      <strong>${text(a.dia_semana)}</strong>
      <span>Horario: ${text(a.hora_inicio)} - ${text(a.hora_fin)}</span>
      <span>Duracion: ${a.duracion_minutos} min</span>
      <span class="pub-card-cupos ${cupos > 3 ? 'disponibles' : cupos > 0 ? 'pocos' : 'llenos'}">${cupos} cupo(s)</span>
      <span class="pub-card-price">${precio > 0 ? "$" + Number(precio).toLocaleString("es-AR") : "Gratuito"}</span>
    </div>
  `).join("");

  $$(".pub-card[data-agenda-id]").forEach(card => {
    card.addEventListener("click", () => {
      const agendaId = Number(card.dataset.agendaId);
      PS.horario = agendas.find(a => a.id === agendaId);
      goTo(4);
      renderConfirmacion();
    });
  });
}

/* ---- Paso 4: Confirmar ---- */
function renderConfirmacion() {
  const sum = $p("#confirmSummary");
  const precio = PS.data.disponibilidad.find(d => d.medico && d.medico.id === PS.medico.id);

  sum.innerHTML = `
    <h3>Resumen del turno</h3>
    <div class="summary-line"><span class="summary-label">Hospital</span><span class="summary-value">${$p("#hospitalName").textContent}</span></div>
    <div class="summary-line"><span class="summary-label">Especialidad</span><span class="summary-value">${text(PS.especialidad.esp.nombre)}</span></div>
    <div class="summary-line"><span class="summary-label">Medico</span><span class="summary-value">${text(PS.medico.nombre)}</span></div>
    <div class="summary-line"><span class="summary-label">Dia</span><span class="summary-value">${text(PS.horario.dia_semana)}</span></div>
    <div class="summary-line"><span class="summary-label">Horario</span><span class="summary-value">${text(PS.horario.hora_inicio)} - ${text(PS.horario.hora_fin)}</span></div>
    <div class="summary-line"><span class="summary-label">Precio base</span><span class="summary-value">${precio && precio.precio_estimado > 0 ? "$" + Number(precio.precio_estimado).toLocaleString("es-AR") : "Gratuito"}</span></div>
  `;

  $p("#precioEstimado").classList.add("hidden");
}

/* ---- Calcular precio al escribir motivo ---- */
let precioTimer = null;
$p("#confirmForm").addEventListener("input", (e) => {
  if (e.target.name !== "motivo") return;
  clearTimeout(precioTimer);
  precioTimer = setTimeout(calcularPrecio, 400);
});

async function calcularPrecio() {
  const motivo = $p("#confirmForm").elements.motivo.value.trim();
  if (!motivo) {
    $p("#precioEstimado").classList.add("hidden");
    return;
  }
  try {
    const result = await fetch("/api/calcular_precio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        medico_id: PS.medico.id,
        motivo: motivo,
      }),
    }).then(r => r.json());

    PS.precioInfo = result;
    const box = $p("#precioEstimado");
    box.classList.remove("hidden");
    $p("#precioValue").textContent = result.estimated_price > 0
      ? "$" + Number(result.estimated_price).toLocaleString("es-AR")
      : "Gratuito";
    $p("#precioRange").textContent = result.range
      ? `Rango estimado: $${Number(result.range[0]).toLocaleString("es-AR")} - $${Number(result.range[1]).toLocaleString("es-AR")}`
      : "";
  } catch (e) {
    $p("#precioEstimado").classList.add("hidden");
  }
}

/* ---- Submit confirmar ---- */
$p("#confirmForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const fd = new FormData(form);

  try {
    // 1. Crear o buscar paciente
    const pacienteData = {
      dni: fd.get("dni").trim(),
      nombre: fd.get("nombre").trim(),
      telefono: fd.get("telefono").trim(),
      distrito: fd.get("distrito").trim(),
      obra_social: fd.get("obra_social")?.trim() || "Sin obra social",
    };

    // Intentar crear paciente
    let pacienteId;
    try {
      const pRes = await fetch("/api/pacientes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pacienteData),
      }).then(r => r.json());
      if (pRes.error && pRes.error.includes("Ya existe")) {
        // Buscar paciente existente
        const existente = PS.data.pacientes.find(p => p.dni === pacienteData.dni);
        if (!existente) throw new Error("No se pudo encontrar el paciente");
        pacienteId = existente.id;
      } else {
        pacienteId = pRes.id;
      }
    } catch (err) {
      if (err.message.includes("Ya existe")) {
        const existente = PS.data.pacientes.find(p => p.dni === pacienteData.dni);
        if (!existente) throw new Error("No se pudo encontrar el paciente");
        pacienteId = existente.id;
      } else {
        throw err;
      }
    }

    // 2. Calcular fecha del proximo dia de la semana del horario
    const diasMap = { "lunes": 1, "martes": 2, "miercoles": 3, "jueves": 4, "viernes": 5, "sabado": 6, "domingo": 0 };
    const diaTarget = diasMap[PS.horario.dia_semana.toLowerCase()];
    const hoy = new Date();
    let fechaTurno = new Date(hoy);
    while (fechaTurno.getDay() !== diaTarget || fechaTurno <= hoy) {
      fechaTurno.setDate(fechaTurno.getDate() + 1);
    }
    const fechaStr = fechaTurno.toISOString().split("T")[0];

    // 3. Crear turno
    const precioEst = PS.precioInfo ? PS.precioInfo.estimated_price : 0;
    const turnoRes = await fetch("/api/turnos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paciente_id: pacienteId,
        medico_id: PS.medico.id,
        fecha: fechaStr,
        hora: PS.horario.hora_inicio,
        motivo: fd.get("motivo").trim(),
        precio: precioEst,
      }),
    }).then(r => r.json());

    if (turnoRes.error) throw new Error(turnoRes.error);

    // 4. Mostrar exito
    goTo(5);
    $p("#exitoDetalle").innerHTML = `
      <strong>${PS.medico.nombre}</strong> - ${PS.especialidad.esp.nombre}<br>
      ${PS.horario.dia_semana} ${PS.horario.hora_inicio} - ${fechaStr}<br>
      ${precioEst > 0 ? "Precio: $" + Number(precioEst).toLocaleString("es-AR") : "Gratuito"}<br>
      <small>Turno ID: #${turnoRes.id || "N/A"}</small>
    `;
  } catch (err) {
    showToast("Error: " + err.message);
  }
});

/* ---- Botones de volver ---- */
$p("#backMedicos")?.addEventListener("click", () => { goTo(1); });
$p("#backHorarios")?.addEventListener("click", () => { goTo(2); });
$p("#backConfirmar")?.addEventListener("click", () => { goTo(3); });
$p("#nuevoTurno")?.addEventListener("click", () => {
  PS.especialidad = null;
  PS.medico = null;
  PS.horario = null;
  PS.precioInfo = null;
  $p("#confirmForm").reset();
  $p("#precioEstimado").classList.add("hidden");
  goTo(1);
});

init();
