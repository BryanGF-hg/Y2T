const LS_KEY = "yt_files_v1";
let state = {
  files: [],        // localStorage cache
  server: [],       // DB list
  activeId: null,   // video_id DB
  activeLocalId: null
};

const $ = (id) => document.getElementById(id);

function loadLocal() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "[]"); }
  catch { return []; }
}
function saveLocal(files) {
  localStorage.setItem(LS_KEY, JSON.stringify(files));
}

function uid() { return Math.random().toString(16).slice(2) + Date.now().toString(16); }

async function api(path, opts={}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function refreshServer() {
  state.server = await api("/api/videos");
}

function mergeLists() {
  // Simple: muestra server, y si no hay server, muestra local
  // (puedes hacer merge por youtube_url si quieres)
  return state.server.length ? state.server.map(v => ({
    type: "server",
    id: v.id,
    title: v.title || "(sin título)",
    youtube_url: v.youtube_url,
    transcript: v.transcript || "",
    transcript_translated: v.transcript_translated || "",
    target_lang: v.target_lang || ""
  })) : state.files.map(f => ({...f, type:"local"}));
}

function renderList() {
  const list = $("filesList");
  list.innerHTML = "";
  const items = mergeLists();

  items.forEach(item => {
    const li = document.createElement("li");
    li.className = (item.type === "server" && item.id === state.activeId) ? "active" : "";
    li.innerHTML = `
      <div><strong>${escapeHtml(item.title)}</strong></div>
      <div style="opacity:.8;font-size:12px;word-break:break-all">${escapeHtml(item.youtube_url)}</div>
      <div style="opacity:.6;font-size:12px;margin-top:6px">${item.type === "server" ? "DB" : "Local"}</div>
    `;
    li.onclick = () => selectItem(item);
    list.appendChild(li);
  });
}

function escapeHtml(s) {
  return (s ?? "").toString().replace(/[&<>"']/g, m => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;" }[m]));
}

function selectItem(item) {
  if (item.type === "server") {
    state.activeId = item.id;
    $("titleField").value = item.title || "";
    $("transcriptField").value = item.transcript_translated || item.transcript || "";
  } else {
    state.activeLocalId = item.localId;
    $("titleField").value = item.title || "";
    $("transcriptField").value = item.transcript || "";
  }
  renderList();
}

async function addItem() {
  const input = $("ytInput").value.trim();
  const target_lang = $("langSelect").value || null;
  if (!input) return;

  // 1) guardar en localStorage (siempre)
  state.files = loadLocal();
  const localItem = { localId: uid(), title: input.slice(0, 60), youtube_url: input, transcript: "", createdAt: new Date().toISOString() };
  state.files.unshift(localItem);
  saveLocal(state.files);

  // 2) guardar en DB
  try {
    const created = await api("/api/videos", { method:"POST", body: JSON.stringify({ youtube_url: input, target_lang }) });
    await refreshServer();
    state.activeId = created.id;
  } catch (e) {
    console.warn("No se pudo crear en DB:", e.message);
  }

  $("ytInput").value = "";
  renderList();
}

async function scrapeActive() {
  if (!state.activeId) {
    alert("Selecciona primero un item de DB (o crea uno).");
    return;
  }
  try {
    const updated = await api(`/api/videos/${state.activeId}/scrape`, { method:"POST" });
    $("titleField").value = updated.title || "";
    $("transcriptField").value = updated.transcript_translated || updated.transcript || "";
    await refreshServer();
    renderList();
  } catch (e) {
    alert("Scrape falló:\n" + e.message);
  }
}

async function saveEdits() {
  if (!state.activeId) { alert("Selecciona un item DB para guardar."); return; }
  const payload = {
    title: $("titleField").value,
    transcript: $("transcriptField").value
  };
  try {
    await api(`/api/videos/${state.activeId}`, { method:"PUT", body: JSON.stringify(payload) });
    await refreshServer();
    renderList();
  } catch (e) {
    alert("Guardar falló:\n" + e.message);
  }
}

async function deleteActive() {
  if (!state.activeId) { alert("Selecciona un item DB para eliminar."); return; }
  try {
    await api(`/api/videos/${state.activeId}`, { method:"DELETE" });
    state.activeId = null;
    $("titleField").value = "";
    $("transcriptField").value = "";
    await refreshServer();
    renderList();
  } catch (e) {
    alert("Eliminar falló:\n" + e.message);
  }
}

function openModal() {
  const title = $("titleField").value || "Transcript";
  const body = $("transcriptField").value || "";
  $("modalTitle").innerText = title;
  $("modalBody").innerText = body;
  $("modal").classList.remove("hidden");
}
function closeModal() { $("modal").classList.add("hidden"); }

async function init() {
  state.files = loadLocal();
  try { await refreshServer(); } catch { /* offline DB */ }
  renderList();

  $("btnAdd").onclick = addItem;
  $("btnScrape").onclick = scrapeActive;
  $("btnSaveEdit").onclick = saveEdits;
  $("btnDelete").onclick = deleteActive;
  $("btnModal").onclick = openModal;
  $("btnCloseModal").onclick = closeModal;
  $("btnReload").onclick = async () => { await refreshServer(); renderList(); };

  // cerrar modal click fuera
  $("modal").onclick = (e) => { if (e.target.id === "modal") closeModal(); };
}

init();
