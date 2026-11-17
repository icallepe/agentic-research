"use strict";
// Flujo interactivo y animado del producto. Usa los datos reales de cada informe (window.DEMO_DATA):
// las decisiones del supervisor, las quejas que encontro, las cifras que calculo el codigo.
(() => {
  const DATA = window.DEMO_DATA;
  const root = document.querySelector(".flow");
  if (!DATA?.informes?.length || !root) return;

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const svg = $("#flow-svg");

  // ---------- Geometria del diagrama (viewBox 1100 x 400) ----------
  const NODES = {
    pregunta:     { x: 0,   y: 155, w: 140, h: 80,  t: "Pregunta",  s: "un tema" },
    supervisor:   { x: 210, y: 145, w: 160, h: 100, t: "Supervisor",   s: "decide quién actúa" },
    investigador: { x: 470, y: 40,  w: 180, h: 70,  t: "Investigador", s: "busca quejas" },
    analista:     { x: 470, y: 160, w: 180, h: 70,  t: "Analista",     s: "cuenta con código" },
    redactor:     { x: 470, y: 280, w: 180, h: 70,  t: "Redactor",     s: "escribe con citas" },
    revision:     { x: 740, y: 145, w: 160, h: 100, t: "Revisión",     s: "una persona decide" },
    informe:      { x: 950, y: 155, w: 150, h: 80,  t: "Informe",      s: "con citas" },
  };
  const EDGES = {
    "p-s":   { d: "M140 195 H210" },
    "s-i":   { d: "M370 170 C425 170 425 68 470 68" },
    "i-s":   { d: "M470 84 C415 84 415 182 370 182" },
    "s-a":   { d: "M370 190 H470" },
    "a-s":   { d: "M470 204 H370" },
    "s-w":   { d: "M370 208 C425 208 425 308 470 308" },
    "w-s":   { d: "M470 324 C415 324 415 222 370 222" },
    "s-r":   { d: "M290 245 V385 H820 V245", label: "cuando termina", lx: 555, ly: 376 },
    "r-inf": { d: "M900 195 H950" },
    "r-s":   { d: "M820 145 V14 H290 V145", label: "pedir cambios", lx: 555, ly: 30 },
  };

  function drawSvg() {
    const edges = Object.entries(EDGES).map(([id, e]) =>
      `<path class="edge" id="e-${id}" d="${e.d}" marker-end="url(#arr)"/>` +
      (e.label ? `<text class="edge-label" x="${e.lx}" y="${e.ly}" text-anchor="middle">${e.label}</text>` : "")).join("");
    const COLOR = { pregunta: "ink", supervisor: "ink", investigador: "blue", analista: "green", redactor: "yellow", revision: "red", informe: "ink" };
    const nodes = Object.entries(NODES).map(([id, n]) =>
      `<g class="node c-${COLOR[id]}" id="n-${id}">
        <rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="18"/>
        <text class="t" x="${n.x + n.w / 2}" y="${n.y + n.h / 2 - 2}" text-anchor="middle">${n.t}</text>
        <text class="s" x="${n.x + n.w / 2}" y="${n.y + n.h / 2 + 20}" text-anchor="middle">${n.s}</text>
        <g class="ck"><circle cx="${n.x + n.w - 4}" cy="${n.y + 4}" r="13"/><text x="${n.x + n.w - 4}" y="${n.y + 10}" text-anchor="middle">✓</text></g>
      </g>`).join("");
    svg.innerHTML = `<defs>
        <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" class="arrow"/></marker>
      </defs>${edges}${nodes}<circle id="packet" r="9" style="display:none"/>`;
  }

  // ---------- Pasos: texto y datos reales segun el informe elegido ----------
  const LABELS = ["Pregunta", "Supervisor", "Investigador", "Supervisor", "Analista", "Supervisor", "Redactor", "Supervisor", "Revisión", "Informe"];
  function buildSteps(r) {
    const pasos = r.pasos_supervisor || [];
    const decision = (k) => {
      const p = pasos[k];
      return p ? `<p class="real"><span>Decisión real en este ejemplo</span> → <b>${esc(p.ruta)}</b>: «${esc(p.motivo)}»</p>` : "";
    };
    const temas = (r.conteos?.temas || []).slice(0, 3);
    const first = r.quejas_citadas?.[0];
    const nCites = (r.borrador.match(/\[[^\]]*queja[^\]]*\]/gi) || []).length;
    const heads = [...r.borrador.matchAll(/^#{2,3}\s+(.+)$/gm)].map((m) => m[1].replace(/\*/g, "")).slice(0, 5);
    const sup = (title, body, k) => ({ node: "supervisor", title, io: "Entra: lo que ya está hecho · Sale: a quién le toca",
      body: `<p>${body}</p>${decision(k)}` });
    return [
      { node: "pregunta", edge: null, title: "1 · Tú pides un tema", io: "Entra: tu pregunta · Sale: la pregunta, tal cual",
        body: `<p>Escribes qué quieres saber, con tus palabras.</p><p class="real"><span>Tema de este ejemplo</span> «${esc(r.tema)}»</p>` },
      { ...sup("2 · El supervisor reparte el trabajo", "Mira qué hay hecho y decide quién actúa. Si el modelo se equivoca (por ejemplo, intenta redactar sin investigar), <b>reglas en código lo corrigen</b>.", 0), edge: "p-s" },
      { node: "investigador", edge: "s-i", title: "3 · El investigador busca quejas", io: "Entra: el tema · Sale: quejas relevantes",
        body: `<p>Busca en las ${DATA.total_quejas} quejas las que se parecen al tema, por significado y no solo por palabras exactas.</p>
          <p class="real"><span>En este ejemplo</span> consultó <b>${r.quejas_consultadas}</b> quejas${first ? `, entre ellas la <b>queja ${esc(first.id)}</b> de ${esc(first.empresa)}` : ""}.</p>` },
      { ...sup("4 · Vuelve al supervisor", "Ya hay evidencia. El supervisor comprueba qué falta y decide el siguiente paso.", 1), edge: "i-s" },
      { node: "analista", edge: "s-a", title: "5 · El analista mide, con código", io: "Entra: la evidencia · Sale: cifras exactas",
        body: `<p>Aquí <b>el modelo no cuenta nada</b>. Los conteos y porcentajes los calcula código sobre todas las quejas, así una cifra no depende de que el LLM «cuente bien».</p>
          ${temas.length ? `<p class="real"><span>Calculado por código</span> ${temas.map((t) => `<b>${esc(t.tema)}</b>: ${t.quejas} quejas (${String(t.porcentaje).replace(".", ",")} %)`).join(" · ")}</p>` : ""}` },
      { ...sup("6 · Otra vez el supervisor", "Hay evidencia y análisis: toca escribir.", 2), edge: "a-s" },
      { node: "redactor", edge: "s-w", title: "7 · El redactor escribe el borrador", io: "Entra: evidencia y cifras · Sale: borrador con citas",
        body: `<p>Escribe solo con lo que recibió, y <b>cita la fuente de cada afirmación</b> con el identificador de la queja. No puede inventar cifras: las toma tal cual de las contribuciones.</p>
          <p class="real"><span>En este ejemplo</span> escribió <b>${nCites}</b> citas <code>[queja N]</code>${heads.length ? ` en las secciones: ${heads.map(esc).join(" · ")}` : ""}.</p>` },
      { ...sup("8 · El supervisor cierra el trabajo", "Hay borrador, así que el flujo puede terminar y pasar a una persona.", 3), edge: "w-s" },
      { node: "revision", edge: "s-r", title: "9 · Una persona revisa", io: "Entra: el borrador · Sale: aprobado, o vuelta con tu comentario",
        body: `<p>El flujo <b>se detiene</b> hasta que alguien decide. Si pides cambios, tu comentario vuelve al supervisor y los agentes repiten el trabajo. El estado se guarda para poder retomarlo.</p>
          <div class="actions"><button type="button" class="btn primary small" data-flow="approve">Aprobar</button><button type="button" class="btn small" data-flow="changes">Pedir cambios</button></div>` },
      { node: "informe", edge: "r-inf", title: "10 · Informe listo, con citas", io: "Entra: el borrador aprobado · Sale: el informe",
        body: `<p>Cada cita es un botón: lleva a la queja original, con su empresa, tema y fecha. Así puedes comprobar cualquier afirmación en un clic.</p>
          <div class="actions"><a class="btn primary small" href="#informe=${esc(r.id)}" data-flow="open">Abrir este informe</a></div>` },
    ];
  }

  // ---------- Estado y animacion ----------
  let ex = DATA.informes[0].id, steps = buildSteps(DATA.informes[0]), idx = 0, playing = false, timer = 0, raf = 0, vuelta = 1;
  const packet = () => $("#packet", svg);

  function sendPacket(edgeId, dur = 950) {
    cancelAnimationFrame(raf);
    const pk = packet(), path = edgeId && $("#e-" + edgeId, svg);
    if (!pk) return;
    if (!path || reduce) { pk.style.display = "none"; return; }
    const L = path.getTotalLength(), t0 = performance.now();
    pk.style.display = "";
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / dur), e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      const p = path.getPointAtLength(L * e);
      pk.setAttribute("cx", p.x); pk.setAttribute("cy", p.y);
      if (k < 1) raf = requestAnimationFrame(tick); else setTimeout(() => { pk.style.display = "none"; }, 180);
    };
    raf = requestAnimationFrame(tick);
  }

  function paint() {
    const s = steps[idx];
    Object.keys(NODES).forEach((id) => {
      const g = $("#n-" + id, svg), visited = steps.slice(0, idx).some((x) => x.node === id);
      g.classList.toggle("active", s.node === id);
      g.classList.toggle("done", visited && s.node !== id);
    });
    const seen = new Set(steps.slice(0, idx).map((x) => x.edge).filter(Boolean));
    Object.keys(EDGES).forEach((id) => {
      const el = $("#e-" + id, svg);
      el.classList.toggle("on", s.edge === id);
      el.classList.toggle("seen", seen.has(id) && s.edge !== id);
    });
    $("#flow-steps").innerHTML = steps.map((_, i) =>
      `<li><button type="button" data-i="${i}" ${i === idx ? 'aria-current="step"' : ""} class="${i < idx ? "past" : ""}" aria-label="Paso ${i + 1}: ${LABELS[i]}"><span class="num">${i + 1}</span><span class="lab">${LABELS[i]}</span></button></li>`).join("");
    const d = $("#flow-detail");
    d.innerHTML = `<div class="in">
        ${vuelta > 1 ? `<p class="turn">Vuelta ${vuelta}: los agentes repiten el trabajo con tu comentario.</p>` : ""}
        <h3>${s.title}</h3>${s.body}<p class="io">${s.io}</p></div>`;
    const stage = $(".flow-stage", root), nd = NODES[s.node];
    if (stage.scrollWidth > stage.clientWidth + 4) {       // pantalla estrecha: centrar el nodo activo
      const cx = (nd.x + nd.w / 2) / 1100 * svg.clientWidth;
      stage.scrollTo({ left: cx - stage.clientWidth / 2, behavior: reduce ? "auto" : "smooth" });
    }
    $("#flow-prev").disabled = idx === 0;
    $("#flow-next").disabled = idx === steps.length - 1;
    const pb = $("#flow-play");
    pb.textContent = playing ? "⏸ Pausar" : idx === steps.length - 1 ? "↻ Repetir" : "▶ Reproducir";
    pb.setAttribute("aria-label", playing ? "Pausar" : idx === steps.length - 1 ? "Repetir el flujo" : "Reproducir");
    d.setAttribute("aria-live", playing ? "off" : "polite");
  }

  function go(i, { packetToo = true } = {}) {
    idx = Math.max(0, Math.min(steps.length - 1, i));
    paint();
    if (packetToo) sendPacket(steps[idx].edge);
    schedule();
  }
  function schedule() {
    clearTimeout(timer);
    if (!playing) return;
    if (idx >= steps.length - 1) { playing = false; paint(); return; }
    timer = setTimeout(() => go(idx + 1), reduce ? 4500 : 3600);
  }
  function play() { if (idx >= steps.length - 1) { vuelta = 1; idx = 0; } playing = true; go(idx, { packetToo: true }); }
  function pause() { playing = false; clearTimeout(timer); paint(); }

  function chooseExample(id) {
    const r = DATA.informes.find((x) => x.id === id) || DATA.informes[0];
    ex = r.id; steps = buildSteps(r); vuelta = 1;
    $("#flow-ex").innerHTML = DATA.informes.map((x) => `<button type="button" data-ex="${esc(x.id)}" aria-pressed="${x.id === ex}">${esc(x.titulo)}</button>`).join("");
    go(0);
  }

  // ---------- Eventos ----------
  root.addEventListener("click", (e) => {
    const t = e.target.closest("button, a[data-flow]");
    if (!t) return;
    if (t.dataset.ex) return chooseExample(t.dataset.ex);
    if (t.dataset.i !== undefined) { playing = false; return go(+t.dataset.i); }
    if (t.id === "flow-play") return playing ? pause() : play();
    if (t.id === "flow-prev") { playing = false; return go(idx - 1); }
    if (t.id === "flow-next") { playing = false; return go(idx + 1); }
    if (t.dataset.flow === "approve") { playing = false; return go(idx + 1); }
    if (t.dataset.flow === "changes") {
      playing = false; sendPacket("r-s", 1300);
      setTimeout(() => { vuelta += 1; go(1); }, reduce ? 0 : 1300);
      return;
    }
    if (t.dataset.flow === "open") setTimeout(() => document.getElementById("informes")?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }), 120);
  });

  // ---------- Inicio ----------
  drawSvg();
  chooseExample(ex);
  if (!reduce && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((en) => en.isIntersecting)) { io.disconnect(); if (idx === 0 && !playing) play(); }
    }, { threshold: 0.45 });
    io.observe(root);
  }
})();
