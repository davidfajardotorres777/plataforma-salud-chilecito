const chatMessages = document.querySelector("#chatMessages");
const botForm = document.querySelector("#botForm");
const botInput = document.querySelector("#botInput");

function appendMessage(role, text, payload = {}) {
  const item = document.createElement("article");
  item.className = `chat-message ${role}`;

  const label = document.createElement("span");
  label.className = "chat-role";
  label.textContent = role === "user" ? "Vos" : "Bot IA";

  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";
  bubble.textContent = text;

  item.append(label, bubble);

  if (payload.documento) {
    item.append(renderDocument(payload.documento));
  }

  if (payload.suggestions?.length) {
    item.append(renderSuggestions(payload.suggestions));
  }

  chatMessages.append(item);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return item;
}

function renderSuggestions(suggestions) {
  const box = document.createElement("div");
  box.className = "suggestions";
  suggestions.slice(0, 4).forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = suggestion;
    button.addEventListener("click", () => sendCommand(suggestion));
    box.append(button);
  });
  return box;
}

function renderDocument(documento) {
  const wrap = document.createElement("div");
  wrap.className = "bot-document";

  const title = document.createElement("strong");
  title.textContent = `${documento.nombre_archivo} (${documento.mime_type})`;
  wrap.append(title);

  if (!documento.data_url) {
    const empty = document.createElement("p");
    empty.textContent = "El documento no trajo vista previa en esta respuesta.";
    wrap.append(empty);
    return wrap;
  }

  if (documento.mime_type?.startsWith("image/")) {
    const image = document.createElement("img");
    image.src = documento.data_url;
    image.alt = documento.nombre_archivo;
    wrap.append(image);
    return wrap;
  }

  if (documento.mime_type === "application/pdf") {
    const frame = document.createElement("iframe");
    frame.src = documento.data_url;
    frame.title = documento.nombre_archivo;
    wrap.append(frame);
    return wrap;
  }

  if (documento.mime_type?.startsWith("text/")) {
    const pre = document.createElement("pre");
    pre.textContent = decodeBase64Text(documento.contenido_base64 || "");
    wrap.append(pre);
    return wrap;
  }

  const link = document.createElement("a");
  link.href = documento.data_url;
  link.download = documento.nombre_archivo;
  link.textContent = "Descargar documento";
  wrap.append(link);
  return wrap;
}

function decodeBase64Text(value) {
  try {
    const raw = atob(value);
    const bytes = Uint8Array.from(raw, (char) => char.charCodeAt(0));
    return new TextDecoder("utf-8").decode(bytes);
  } catch (error) {
    return "No se pudo decodificar el texto del documento.";
  }
}

async function sendCommand(command) {
  const message = command.trim();
  if (!message) {
    return;
  }
  appendMessage("user", message);
  botInput.value = "";
  botInput.focus();

  const loading = appendMessage("bot", "Procesando...");
  try {
    const response = await fetch("/api/bot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    loading.remove();
    appendMessage("bot", data.reply || "Listo.", data);
  } catch (error) {
    loading.remove();
    appendMessage("bot", "No pude conectar con el servidor local. Verifica que la plataforma siga iniciada.");
  }
}

botForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendCommand(botInput.value);
});

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => sendCommand(button.dataset.command));
});

appendMessage(
  "bot",
  "Hola. Podes pedirme acciones reales sobre la plataforma: listar datos, crear pacientes, editar turnos, eliminar un turno o ver documentos.",
  { suggestions: ["resumen", "listar pacientes", "listar turnos", "ayuda"] },
);
