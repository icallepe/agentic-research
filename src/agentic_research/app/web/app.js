"use strict";

// ---------- modo demo e idioma ----------
const DEMO = Boolean(window.DEMO_MODE) || new URLSearchParams(location.search).has("demo");

const I18N = {
  es: {
    skip: "Saltar al contenido", reportsAria: "Informes", newReport: "Nuevo informe", historyAria: "Historial",
    historyH: "Historial", themeAria: "Cambiar tema", themeBtn: "Tema", openHistory: "Abrir historial",
    noReports: "Aún no hay informes. Crea el primero.",
    "status.queued": "En cola", "status.running": "Investigando", "status.resuming": "Aplicando cambios",
    "status.awaiting_review": "Pendiente de revisión", "status.completed": "Aprobado",
    "status.no_results": "Sin resultados", "status.failed": "Error",
    "agent.researcher.title": "Investigar", "agent.researcher.desc": "Busca evidencia en tus documentos",
    "agent.analyst.title": "Analizar", "agent.analyst.desc": "Mide la solidez de la evidencia y sus contradicciones",
    "agent.synthesizer.title": "Redactar", "agent.synthesizer.desc": "Escribe el informe citando las fuentes",
    reviewStepTitle: "Tu revisión", reviewStepDesc: "Aprobarás el borrador o pedirás cambios",
    stepDone: "Completado", stepSkipped: "Omitido por el supervisor",
    justNow: "ahora mismo",
    sections: ["hallazgos", "riesgos", "recomendaciones"],
    examples: ["abandono en el registro de la app", "motivos de contacto con soporte", "resultados del benchmark frente a la competencia"],
    newTitle: "¿Qué quieres investigar?",
    newLead: "Un equipo de agentes busca en tus documentos, analiza la evidencia y redacta un informe con las fuentes citadas. Tú das el visto bueno al final.",
    topicLabel: "Tema", topicHint: "Una pregunta o un tema concreto funciona mejor que uno muy amplio.",
    topicPh: "Ej.: abandono en el registro de la app", topicErr: "Escribe al menos 3 caracteres.", examplesAria: "Ejemplos",
    detailLabel: "Nivel de detalle", detailHint: "Controla cuánto se desarrolla cada sección.",
    low: "Breve", lowSub: "Lo esencial", high: "Detallado", highSub: "Con cifras y fuentes",
    sectionsLabel: "Secciones del informe", sectionsHint: "Se redactarán en este orden. Pulsa Enter para añadir una.",
    addPh: "+ añadir", addAria: "Añadir sección", removeAria: "Quitar {name}",
    submit: "Investigar", sending: "Enviando…", shortcut: "para enviar", needSection: "Añade al menos una sección.",
    draftN: "Borrador {n}", supervisor: "Supervisor",
    deciding: "El supervisor está decidiendo el siguiente paso…", waitingWorker: "Esperando a que un worker tome el trabajo…",
    slow: "Lleva un rato en cola. Comprueba que el worker está en marcha:",
    decisionsN: "Decisiones del supervisor ({n})", stepN: "Paso {n}", howReached: "Cómo se llegó a este borrador ({n} decisiones)",
    progressAria: "Progreso",
    sourcesH: "Fuentes", sourcesHint: "Pulsa una cita del texto para ver el fragmento que la respalda.",
    noSources: "Este informe no tiene fuentes asociadas.", fragOne: "fragmento", fragMany: "fragmentos",
    toReview: "Borrador para revisar", approvedReport: "Informe aprobado", copy: "Copiar", download: "Descargar .md",
    copied: "Informe copiado", copyFail: "No se pudo copiar", citeMissing: "«{name}» no aparece entre los fragmentos recuperados.",
    reviewQ: "¿Qué te parece el borrador?", approve: "Aprobar informe", requestChanges: "Pedir cambios",
    whatChange: "¿Qué debería cambiar?", fbPh: "Ej.: añade el dato del SMS y explica la contradicción entre fuentes",
    fbErr: "Cuéntanos qué cambiar para poder aplicarlo.", sendChanges: "Enviar cambios",
    toastApproved: "Informe aprobado", toastChanges: "Cambios enviados, preparando un nuevo borrador",
    noResultsH: "No se encontró información", noResultsP: "Los agentes no hallaron evidencia suficiente en los documentos para redactar un informe sobre este tema.", tryOther: "Probar con otro tema",
    failedH: "Algo salió mal", failedP: "El trabajo se interrumpió. Puedes reintentarlo con los mismos parámetros.", retry: "Reintentar",
    notFoundH: "No encontramos este informe", notFoundP: "Puede que el enlace sea incorrecto o que el trabajo haya caducado.", createReport: "Crear un informe",
    loadFailH: "No se pudo cargar", connErr: "No se pudo conectar con el servidor.",
    demoTag: "Demo", demoText: "Datos simulados, sin servidor. El sistema real ejecuta agentes de LangGraph sobre tus documentos.", demoLink: "Ver en GitHub",
  },
  en: {
    skip: "Skip to content", reportsAria: "Reports", newReport: "New report", historyAria: "History",
    historyH: "History", themeAria: "Toggle theme", themeBtn: "Theme", openHistory: "Open history",
    noReports: "No reports yet. Create the first one.",
    "status.queued": "Queued", "status.running": "Researching", "status.resuming": "Applying changes",
    "status.awaiting_review": "Awaiting review", "status.completed": "Approved",
    "status.no_results": "No results", "status.failed": "Error",
    "agent.researcher.title": "Research", "agent.researcher.desc": "Searches your documents for evidence",
    "agent.analyst.title": "Analyze", "agent.analyst.desc": "Weighs the evidence and spots contradictions",
    "agent.synthesizer.title": "Write", "agent.synthesizer.desc": "Writes the report citing its sources",
    reviewStepTitle: "Your review", reviewStepDesc: "You will approve the draft or ask for changes",
    stepDone: "Done", stepSkipped: "Skipped by the supervisor",
    justNow: "just now",
    sections: ["findings", "risks", "recommendations"],
    examples: ["drop-off during app sign-up", "why people contact support", "benchmark results against competitors"],
    newTitle: "What do you want to research?",
    newLead: "A team of agents searches your documents, analyzes the evidence and writes a report with cited sources. You sign off at the end.",
    topicLabel: "Topic", topicHint: "A specific question or topic works better than a very broad one.",
    topicPh: "E.g. drop-off during app sign-up", topicErr: "Write at least 3 characters.", examplesAria: "Examples",
    detailLabel: "Level of detail", detailHint: "Controls how much each section is developed.",
    low: "Brief", lowSub: "Just the essentials", high: "Detailed", highSub: "With figures and sources",
    sectionsLabel: "Report sections", sectionsHint: "They will be written in this order. Press Enter to add one.",
    addPh: "+ add", addAria: "Add section", removeAria: "Remove {name}",
    submit: "Start research", sending: "Sending…", shortcut: "to submit", needSection: "Add at least one section.",
    draftN: "Draft {n}", supervisor: "Supervisor",
    deciding: "The supervisor is deciding the next step…", waitingWorker: "Waiting for a worker to pick up the job…",
    slow: "It has been queued for a while. Check that the worker is running:",
    decisionsN: "Supervisor decisions ({n})", stepN: "Step {n}", howReached: "How this draft was reached ({n} decisions)",
    progressAria: "Progress",
    sourcesH: "Sources", sourcesHint: "Click a citation in the text to see the passage that backs it.",
    noSources: "This report has no linked sources.", fragOne: "passage", fragMany: "passages",
    toReview: "Draft to review", approvedReport: "Approved report", copy: "Copy", download: "Download .md",
    copied: "Report copied", copyFail: "Could not copy", citeMissing: "“{name}” is not among the retrieved passages.",
    reviewQ: "What do you think of the draft?", approve: "Approve report", requestChanges: "Request changes",
    whatChange: "What should change?", fbPh: "E.g. add the SMS figure and explain the contradiction between sources",
    fbErr: "Tell us what to change so we can apply it.", sendChanges: "Send changes",
    toastApproved: "Report approved", toastChanges: "Changes sent, preparing a new draft",
    noResultsH: "No information found", noResultsP: "The agents did not find enough evidence in the documents to write a report on this topic.", tryOther: "Try another topic",
    failedH: "Something went wrong", failedP: "The job was interrupted. You can retry it with the same parameters.", retry: "Retry",
    notFoundH: "We could not find this report", notFoundP: "The link may be wrong or the job may have expired.", createReport: "Create a report",
    loadFailH: "Could not load", connErr: "Could not reach the server.",
    demoTag: "Demo", demoText: "Simulated data, no server. The real system runs LangGraph agents over your documents.", demoLink: "View on GitHub",
  },
};

let lang = new URLSearchParams(location.search).get("lang") || localStorage.getItem("lang") || (DEMO ? "en" : (navigator.language || "").toLowerCase().startsWith("es") ? "es" : "en");
if (!I18N[lang]) lang = "en";
const list = (key) => I18N[lang][key]; // textos que son listas (t() devuelve siempre string)
const t = (key, vars = {}) => String(I18N[lang][key] ?? key).replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");

// ---------- utilidades ----------
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ESC[c]);

const STATUS_CLS = {
  queued: "run", running: "run", resuming: "run", awaiting_review: "review",
  completed: "done", no_results: "fail", failed: "fail",
};
const statusLabel = (s) => (I18N[lang][`status.${s}`] ? t(`status.${s}`) : s);
const ACTIVE = new Set(["queued", "running", "resuming"]);
const AGENT_IDS = ["researcher", "analyst", "synthesizer"];

function ago(epoch) {
  if (!epoch) return "";
  const rtf = new Intl.RelativeTimeFormat(lang, { numeric: "auto" });
  const s = Math.round(epoch - Date.now() / 1000);
  const abs = Math.abs(s);
  if (abs < 45) return t("justNow");
  if (abs < 3600) return rtf.format(Math.round(s / 60), "minute");
  if (abs < 86400) return rtf.format(Math.round(s / 3600), "hour");
  return rtf.format(Math.round(s / 86400), "day");
}

function toast(msg, isErr = false) {
  const el = document.createElement("div");
  el.className = "toast" + (isErr ? " err" : "");
  el.textContent = msg;
  $("#toasts").append(el);
  setTimeout(() => el.remove(), isErr ? 6000 : 3200);
}

async function api(path, opts = {}) {
  if (DEMO) return window.demoApi(path, opts, lang);
  let res;
  try {
    res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  } catch {
    throw new Error(t("connErr"));
  }
  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") msg = body.detail;
      else if (Array.isArray(body.detail)) msg = body.detail.map((d) => d.msg).join(". ");
    } catch { /* cuerpo no JSON */ }
    throw Object.assign(new Error(msg), { status: res.status });
  }
  return res.json();
}

// ---------- markdown mínimo y seguro (escapa antes de transformar) ----------
function inline(text) {
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, "$1<em>$2</em>");
  // [archivo.md] o [a.md, b.md] -> chips de cita clicables
  return text.replace(/\[([^\]]+?)\]/g, (m, inner) => {
    const parts = inner.split(/[,;]\s*/).map((s) => s.trim());
    const looksLikeFiles = parts.every((p) => /^[\w.\-]+\.\w{1,5}$/.test(p));
    return looksLikeFiles
      ? parts.map((p) => `<button type="button" class="cite" data-file="${p}">${p}</button>`).join(" ")
      : m;
  });
}

function markdown(src) {
  let html = "", list = null, para = [];
  const flushP = () => { if (para.length) { html += `<p>${inline(para.join(" "))}</p>`; para = []; } };
  const flushL = () => { if (list) { html += `</${list}>`; list = null; } };
  for (const raw of esc(src).split("\n")) {
    const line = raw.trimEnd();
    let m;
    if (!line.trim()) { flushP(); flushL(); continue; }
    if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
      flushP(); flushL();
      const lv = Math.min(m[1].length + 1, 4);
      html += `<h${lv}>${inline(m[2])}</h${lv}>`;
    } else if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
      flushP(); flushL(); html += "<hr>";
    } else if ((m = line.match(/^\s*[-*•]\s+(.*)$/))) {
      flushP();
      if (list !== "ul") { flushL(); html += "<ul>"; list = "ul"; }
      html += `<li>${inline(m[1])}</li>`;
    } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
      flushP();
      if (list !== "ol") { flushL(); html += "<ol>"; list = "ol"; }
      html += `<li>${inline(m[1])}</li>`;
    } else {
      flushL(); para.push(line.trim());
    }
  }
  flushP(); flushL();
  return html;
}

// ---------- estado ----------
const view = $("#view");
let jobList = [];
let current = { id: null, job: null, sig: "", timer: null, token: 0 };
let ui = { feedbackOpen: false, feedback: "" };

const prefs = {
  get detail() { return localStorage.getItem("detail") || "low"; },
  get sections() {
    try { return JSON.parse(localStorage.getItem("sections")) || list("sections"); } catch { return list("sections"); }
  },
};

function currentRoute() {
  const [a, b] = location.hash.replace(/^#\/?/, "").split("/");
  return a === "job" && b ? { name: "job", id: b } : { name: "new" };
}

function stopPolling() {
  clearTimeout(current.timer);
  current.token++;
}

// ---------- historial (sidebar) ----------
function renderHistory() {
  const id = currentRoute().id;
  const ul = $("#history");
  if (!jobList.length) {
    ul.innerHTML = `<li class="empty">${esc(t("noReports"))}</li>`;
    return;
  }
  ul.innerHTML = jobList.map((j) => `<li><a href="#/job/${esc(j.id)}" ${j.id === id ? 'aria-current="page"' : ""}>
      <span class="t">${esc(j.topic)}</span>
      <span class="m"><span class="dot ${STATUS_CLS[j.status] ?? ""}" aria-hidden="true"></span>${esc(statusLabel(j.status))}${j.created_at ? " · " + esc(ago(j.created_at)) : ""}</span>
    </a></li>`).join("");
}

async function refreshHistory() {
  try { jobList = await api("/jobs?limit=50"); renderHistory(); } catch { /* el historial es opcional */ }
}

// ---------- vista: nuevo informe ----------
function renderNew() {
  stopPolling();
  let sections = [...prefs.sections];
  view.innerHTML = `
    <h1 class="page-title" tabindex="-1">${esc(t("newTitle"))}</h1>
    <p class="lead">${esc(t("newLead"))}</p>
    <form class="card form" id="new-form" novalidate>
      <div class="field">
        <label for="topic">${esc(t("topicLabel"))}</label>
        <p class="hint" id="topic-hint">${esc(t("topicHint"))}</p>
        <textarea id="topic" rows="3" aria-describedby="topic-hint topic-err" placeholder="${esc(t("topicPh"))}" maxlength="400" required></textarea>
        <div class="field-error" id="topic-err" role="alert"></div>
        <div class="suggestions" aria-label="${esc(t("examplesAria"))}">${list("examples").map((e) => `<button type="button" data-ex="${esc(e)}">${esc(e)}</button>`).join("")}</div>
      </div>
      <fieldset class="field" style="border:0;padding:0;margin:0">
        <legend class="label" style="padding:0">${esc(t("detailLabel"))}</legend>
        <p class="hint">${esc(t("detailHint"))}</p>
        <div class="segmented" role="radiogroup">
          <input type="radio" name="detail" id="d-low" value="low" ${prefs.detail === "low" ? "checked" : ""}><label for="d-low">${esc(t("low"))}<small>${esc(t("lowSub"))}</small></label>
          <input type="radio" name="detail" id="d-high" value="high" ${prefs.detail === "high" ? "checked" : ""}><label for="d-high">${esc(t("high"))}<small>${esc(t("highSub"))}</small></label>
        </div>
      </fieldset>
      <div class="field">
        <span class="label" id="sec-label">${esc(t("sectionsLabel"))}</span>
        <p class="hint">${esc(t("sectionsHint"))}</p>
        <div class="chips" id="chips" aria-labelledby="sec-label"></div>
      </div>
      <div class="form-actions">
        <button class="btn primary" type="submit" id="submit">${esc(t("submit"))}</button>
        <span class="hint" style="margin:0"><kbd>Ctrl</kbd> + <kbd>Enter</kbd> ${esc(t("shortcut"))}</span>
      </div>
    </form>`;

  const chips = $("#chips");
  const drawChips = () => {
    chips.innerHTML = sections.map((s, i) => `<span class="chip">${esc(s)}<button type="button" data-i="${i}" aria-label="${esc(t("removeAria", { name: s }))}">×</button></span>`).join("")
      + `<input class="input chip-input" id="chip-new" placeholder="${esc(t("addPh"))}" aria-label="${esc(t("addAria"))}" maxlength="40">`;
  };
  const addSection = (v) => {
    v = v.trim().toLowerCase();
    if (v && !sections.includes(v) && sections.length < 8) sections.push(v);
    drawChips(); $("#chip-new").focus();
  };
  drawChips();
  chips.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-i]");
    if (b) { sections.splice(+b.dataset.i, 1); drawChips(); $("#chip-new").focus(); }
  });
  chips.addEventListener("keydown", (e) => {
    if (e.target.id !== "chip-new") return;
    if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addSection(e.target.value.replace(",", "")); }
    else if (e.key === "Backspace" && !e.target.value && sections.length) { sections.pop(); drawChips(); $("#chip-new").focus(); }
  });
  chips.addEventListener("focusout", (e) => {
    if (e.target.id === "chip-new" && e.target.value.trim()) addSection(e.target.value);
  });

  const topic = $("#topic"), err = $("#topic-err"), form = $("#new-form");
  $(".suggestions").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-ex]");
    if (b) { topic.value = b.dataset.ex; err.textContent = ""; topic.focus(); }
  });
  topic.addEventListener("input", () => { err.textContent = ""; });
  topic.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) form.requestSubmit(); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = topic.value.trim();
    if (text.length < 3) { err.textContent = t("topicErr"); topic.focus(); return; }
    if (!sections.length) { toast(t("needSection"), true); return; }
    const detail = form.detail.value;
    const btn = $("#submit");
    btn.disabled = true; btn.textContent = t("sending");
    try {
      const r = await api("/jobs", { method: "POST", body: JSON.stringify({ topic: text, sections, detail_level: detail }) });
      localStorage.setItem("detail", detail);
      localStorage.setItem("sections", JSON.stringify(sections));
      ui = { feedbackOpen: false, feedback: "" };
      await refreshHistory();
      location.hash = `#/job/${r.job_id}`;
    } catch (ex) {
      toast(ex.message, true);
      btn.disabled = false; btn.textContent = t("submit");
    }
  });
  topic.focus();
}

// ---------- vista: job ----------
function pipeline(job) {
  const trace = job.trace || [];
  const rev = trace.reduce((m, e) => Math.max(m, e.revision ?? 0), 0);
  const evs = trace.filter((e) => (e.revision ?? 0) === rev);
  const done = new Set(evs.filter((e) => e.kind === "agent_done").map((e) => e.agent));
  const decisions = evs.filter((e) => e.kind === "supervisor");
  const last = evs[evs.length - 1];
  const active = last && last.kind === "supervisor" && AGENT_IDS.includes(last.route) ? last.route : null;
  const reason = {};
  decisions.forEach((d) => { reason[d.route] = d; });
  return { evs, done, decisions, active, reason };
}

function decisionsList(decisions) {
  return `<ol>${decisions.map((d) => `<li>${esc(t("stepN", { n: d.step }))}: <code>${esc(d.route)}</code> — ${esc(d.reason)}</li>`).join("")}</ol>`;
}

function stepsHtml(job) {
  const p = pipeline(job);
  const running = ACTIVE.has(job.status);
  const items = AGENT_IDS.map((id, i) => {
    let state = "pending", note = t(`agent.${id}.desc`);
    if (p.done.has(id)) { state = "done"; note = t("stepDone"); }
    else if (running && p.active === id) { state = "active"; note = note + "…"; }
    else if (p.done.has("synthesizer") && id === "analyst") { state = "done"; note = t("stepSkipped"); }
    const d = p.reason[id];
    const why = d && state !== "pending" ? `<div class="why"><b>${esc(t("supervisor"))}:</b> ${esc(d.reason)}</div>` : "";
    const bullet = state === "done" ? "✓" : state === "active" ? '<span class="spinner" aria-hidden="true"></span>' : i + 1;
    return `<li class="step ${state}" ${state === "active" ? 'aria-current="step"' : ""}>
      <span class="bullet">${bullet}</span>
      <div><h3>${esc(t(`agent.${id}.title`))}</h3><p>${esc(note)}</p>${why}</div></li>`;
  });
  items.push(`<li class="step pending"><span class="bullet">4</span><div><h3>${esc(t("reviewStepTitle"))}</h3><p>${esc(t("reviewStepDesc"))}</p></div></li>`);
  const waiting = running && !p.active
    ? `<p class="meta" style="margin-bottom:16px">${esc(job.status === "queued" ? t("waitingWorker") : t("deciding"))}</p>` : "";
  const slow = !DEMO && job.status === "queued" && job.created_at && Date.now() / 1000 - job.created_at > 20
    ? `<div class="notice" role="note">${esc(t("slow"))} <code>uv run agentic-research serve</code></div>` : "";
  const log = p.decisions.length ? `<details class="log" ${running ? "open" : ""}>
      <summary>${esc(t("decisionsN", { n: p.decisions.length }))}</summary>${decisionsList(p.decisions)}</details>` : "";
  return `${waiting}<ol class="steps" aria-live="polite">${items.join("")}</ol>${slow}${log}`;
}

function sourcesHtml(job) {
  const src = job.sources?.length ? job.sources : (job.references || []).map((f) => ({ file: f, excerpt: "" }));
  const by = new Map();
  for (const s of src) {
    if (!by.has(s.file)) by.set(s.file, []);
    if (s.excerpt && !by.get(s.file).includes(s.excerpt)) by.get(s.file).push(s.excerpt);
  }
  if (!by.size) return `<p class="meta">${esc(t("noSources"))}</p>`;
  return [...by].map(([file, ex]) => `<details class="src" data-src="${esc(file)}">
    <summary><span>${esc(file)}</span><span class="n">${ex.length ? ex.length + " " + esc(t(ex.length === 1 ? "fragOne" : "fragMany")) : ""}</span></summary>
    ${ex.map((x) => `<blockquote>${esc(x)}</blockquote>`).join("")}</details>`).join("");
}

function metaLine(job) {
  const bits = [];
  if (job.detail_level) bits.push(t(job.detail_level === "high" ? "high" : "low"));
  if (job.sections?.length) bits.push(job.sections.join(" · "));
  if (job.created_at) bits.push(ago(job.created_at));
  return bits.map(esc).join(" &nbsp;·&nbsp; ");
}

function headHtml(job) {
  const rev = job.revision > 0 ? `<span class="badge">${esc(t("draftN", { n: job.revision + 1 }))}</span>` : "";
  return `<header class="job-head">
    <div class="badges"><span class="badge ${STATUS_CLS[job.status] ?? ""}"><span class="dot" aria-hidden="true"></span>${esc(statusLabel(job.status))}</span>${rev}</div>
    <h1 class="page-title" tabindex="-1">${esc(job.topic)}</h1>
    <p class="meta">${metaLine(job)}</p></header>`;
}

function paperHtml(job, readonly) {
  return `<div class="workspace">
    <article class="card paper">
      <div class="paper-bar"><span>${esc(t(readonly ? "approvedReport" : "toReview"))}</span>
        <span class="actions">
          <button class="btn ghost sm" type="button" id="copy-btn">${esc(t("copy"))}</button>
          <button class="btn ghost sm" type="button" id="dl-btn">${esc(t("download"))}</button>
        </span></div>
      <div class="prose" id="prose">${markdown(job.draft || "")}</div>
    </article>
    <aside class="card sources" aria-label="${esc(t("sourcesH"))}">
      <h2>${esc(t("sourcesH"))}</h2><p class="meta">${esc(t("sourcesHint"))}</p>
      ${sourcesHtml(job)}
    </aside></div>`;
}

function reviewHtml() {
  return `<section class="card review-panel" aria-labelledby="rev-h">
    <h2 id="rev-h">${esc(t("reviewQ"))}</h2>
    <div class="review-actions">
      <button class="btn primary" type="button" id="approve-btn">${esc(t("approve"))}</button>
      <button class="btn" type="button" id="changes-btn" aria-expanded="${ui.feedbackOpen}" aria-controls="changes">${esc(t("requestChanges"))}</button>
    </div>
    <div class="changes" id="changes" ${ui.feedbackOpen ? "" : "hidden"}>
      <label for="feedback" class="label" style="font-weight:600">${esc(t("whatChange"))}</label>
      <textarea id="feedback" rows="3" placeholder="${esc(t("fbPh"))}" aria-describedby="fb-err">${esc(ui.feedback)}</textarea>
      <div class="field-error" id="fb-err" role="alert"></div>
      <div><button class="btn primary" type="button" id="send-changes" ${ui.feedback.trim() ? "" : "disabled"}>${esc(t("sendChanges"))}</button></div>
    </div></section>`;
}

function stepsLogOnly(job) {
  const decisions = pipeline(job).decisions;
  if (!decisions.length) return "";
  return `<details class="log"><summary>${esc(t("howReached", { n: decisions.length }))}</summary>${decisionsList(decisions)}</details>`;
}

function bodyHtml(job) {
  switch (job.status) {
    case "queued": case "running": case "resuming":
      return `<section class="card progress" aria-label="${esc(t("progressAria"))}">${stepsHtml(job)}</section>`;
    case "awaiting_review":
      return paperHtml(job, false) + reviewHtml() + (job.trace?.length ? `<div style="margin-top:20px;max-width:760px">${stepsLogOnly(job)}</div>` : "");
    case "completed":
      return paperHtml(job, true) + (job.trace?.length ? `<div style="margin-top:20px;max-width:760px">${stepsLogOnly(job)}</div>` : "");
    case "no_results":
      return `<div class="card empty-state"><h2>${esc(t("noResultsH"))}</h2><p>${esc(t("noResultsP"))}</p>
        <a class="btn primary" href="#/new">${esc(t("tryOther"))}</a></div>`;
    case "failed":
      return `<div class="card empty-state"><h2>${esc(t("failedH"))}</h2><p>${esc(t("failedP"))}</p>
        <button class="btn primary" type="button" id="retry-btn">${esc(t("retry"))}</button></div>
        ${job.error ? `<div class="error-box" role="alert">${esc(job.error)}</div>` : ""}`;
    default:
      return "";
  }
}

function renderJob(first) {
  const job = current.job;
  view.innerHTML = headHtml(job) + bodyHtml(job);
  bindJob(job);
  if (first) $("#view h1")?.focus({ preventScroll: true });
}

function bindJob(job) {
  const prose = $("#prose");
  if (prose) {
    prose.addEventListener("click", (e) => {
      const c = e.target.closest(".cite");
      if (!c) return;
      const f = c.dataset.file.toLowerCase();
      const box = $$(".src").find((el) => el.dataset.src.toLowerCase() === f);
      if (!box) { toast(t("citeMissing", { name: c.dataset.file }), true); return; }
      box.open = true;
      box.scrollIntoView({ block: "nearest", behavior: "smooth" });
      box.classList.remove("flash"); void box.offsetWidth; box.classList.add("flash");
    });
    $("#copy-btn").addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(job.draft); toast(t("copied")); } catch { toast(t("copyFail"), true); }
    });
    $("#dl-btn").addEventListener("click", () => {
      const blob = new Blob([`# ${job.topic}\n\n${job.draft}\n`], { type: "text/markdown" });
      const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `report-${job.id}.md` });
      a.click(); URL.revokeObjectURL(a.href);
    });
  }
  $("#approve-btn")?.addEventListener("click", () => submitReview("approve"));
  $("#changes-btn")?.addEventListener("click", () => {
    ui.feedbackOpen = !ui.feedbackOpen;
    $("#changes").hidden = !ui.feedbackOpen;
    $("#changes-btn").setAttribute("aria-expanded", ui.feedbackOpen);
    if (ui.feedbackOpen) $("#feedback").focus();
  });
  const fb = $("#feedback");
  if (fb) {
    fb.addEventListener("input", () => {
      ui.feedback = fb.value;
      $("#send-changes").disabled = !fb.value.trim();
      $("#fb-err").textContent = "";
    });
    fb.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && fb.value.trim()) submitReview("changes"); });
    $("#send-changes").addEventListener("click", () => submitReview("changes"));
  }
  $("#retry-btn")?.addEventListener("click", async (e) => {
    e.target.disabled = true;
    try {
      const r = await api("/jobs", { method: "POST", body: JSON.stringify({ topic: job.topic, sections: job.sections, detail_level: job.detail_level }) });
      await refreshHistory();
      location.hash = `#/job/${r.job_id}`;
    } catch (ex) { toast(ex.message, true); e.target.disabled = false; }
  });
}

async function submitReview(action) {
  const feedback = ui.feedback.trim();
  if (action === "changes" && !feedback) { $("#fb-err").textContent = t("fbErr"); return; }
  $$(".review-panel button").forEach((b) => (b.disabled = true));
  try {
    await api(`/jobs/${current.id}/review`, { method: "PATCH", body: JSON.stringify({ action, feedback }) });
    toast(t(action === "approve" ? "toastApproved" : "toastChanges"));
    ui = { feedbackOpen: false, feedback: "" };
    current.sig = "";
    poll(current.id, true);
    refreshHistory();
  } catch (ex) {
    toast(ex.message, true);
    $$(".review-panel button").forEach((b) => (b.disabled = false));
    $("#send-changes").disabled = !ui.feedback.trim();
  }
}

function jobSkeleton() {
  view.innerHTML = `<div class="skeleton" style="width:110px;height:22px;border-radius:999px"></div>
    <div class="skeleton" style="width:70%;height:38px;margin-top:14px"></div>
    <div class="skeleton" style="width:40%;margin-top:12px"></div>
    <div class="card" style="margin-top:28px;padding:26px;max-width:760px;display:grid;gap:14px">
      <div class="skeleton"></div><div class="skeleton" style="width:90%"></div><div class="skeleton" style="width:60%"></div></div>`;
}

async function poll(id, first = false) {
  const token = ++current.token;
  clearTimeout(current.timer);
  try {
    const job = await api(`/jobs/${encodeURIComponent(id)}`);
    if (token !== current.token) return;
    current.job = job;
    const sig = JSON.stringify([job.status, job.revision, job.trace?.length ?? 0, job.error]);
    if (sig !== current.sig) {
      const firstPaint = current.sig === "" && first !== "keep";
      current.sig = sig;
      renderJob(firstPaint);
      refreshHistory();
    }
    if (ACTIVE.has(job.status)) current.timer = setTimeout(() => poll(id), DEMO ? 500 : 1500);
  } catch (ex) {
    if (token !== current.token) return;
    if (ex.status === 404) {
      view.innerHTML = `<div class="card empty-state"><h2>${esc(t("notFoundH"))}</h2><p>${esc(t("notFoundP"))}</p>
        <a class="btn primary" href="#/new">${esc(t("createReport"))}</a></div>`;
      return;
    }
    if (!current.job) {
      view.innerHTML = `<div class="card empty-state"><h2>${esc(t("loadFailH"))}</h2><p>${esc(ex.message)}</p>
        <button class="btn primary" type="button" id="reload">${esc(t("retry"))}</button></div>`;
      $("#reload").addEventListener("click", () => { jobSkeleton(); poll(id, true); });
      return;
    }
    current.timer = setTimeout(() => poll(id), 4000); // fallo transitorio: seguimos intentando
  }
}

function renderRoute() {
  const r = currentRoute();
  closeDrawer();
  renderHistory();
  if (r.name === "new") { renderNew(); window.scrollTo(0, 0); return; }
  stopPolling();
  current = { id: r.id, job: null, sig: "", timer: null, token: current.token };
  ui = { feedbackOpen: false, feedback: "" };
  jobSkeleton();
  window.scrollTo(0, 0);
  poll(r.id, true);
}

// ---------- chrome: idioma, tema y menú móvil ----------
function applyStaticText() {
  document.documentElement.lang = lang;
  document.title = "Agentic Research";
  $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", t(el.dataset.i18nAria)));
  $$(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
  $("#demo-banner").hidden = !DEMO;
}

function setLang(next) {
  if (next === lang) return;
  lang = next;
  localStorage.setItem("lang", lang);
  applyStaticText();
  if (currentRoute().name === "new") {
    const keep = $("#topic")?.value;
    renderNew();
    if (keep) $("#topic").value = keep;
  } else {
    current.sig = "";
    poll(current.id, "keep"); // vuelve a pedir el job: en la demo el contenido depende del idioma
  }
  refreshHistory();
}
$(".lang").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-lang]");
  if (b) setLang(b.dataset.lang);
});

function closeDrawer() {
  $("#sidebar").classList.remove("open");
  $("#scrim").hidden = true;
  $("#menu-btn").setAttribute("aria-expanded", "false");
}
$("#menu-btn").addEventListener("click", () => {
  const open = $("#sidebar").classList.toggle("open");
  $("#scrim").hidden = !open;
  $("#menu-btn").setAttribute("aria-expanded", open);
});
$("#scrim").addEventListener("click", closeDrawer);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });
$("#theme-btn").addEventListener("click", () => {
  const now = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = now === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("theme", next);
});

applyStaticText();
window.addEventListener("hashchange", renderRoute);
if (!location.hash) history.replaceState(null, "", "#/new");
renderRoute();
refreshHistory();
setInterval(refreshHistory, 8000);
