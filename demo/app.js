"use strict";
// Demo estatica e interactiva. Lee window.DEMO_DATA (data/reports.js, generado por scripts/export_demo.py).
// Sin llamadas a ninguna API. Todo texto que viene de los datos se escapa (o se inserta con textContent).
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const DATA = window.DEMO_DATA;

  if (!DATA?.muestra?.length || !DATA?.informes?.length) {
    $("#informe").innerHTML = '<p class="empty">No hay datos. Ejecuta <code>scripts/export_demo.py</code> para generar <code>demo/data/reports.js</code>.</p>';
    return;
  }

  // ---------- Datos ----------
  const M = DATA.muestra.map((q) => ({ ...q, anio: q.fecha.slice(0, 4), low: `${q.id} ${q.empresa} ${q.tema} ${q.texto}`.toLowerCase() }));
  const BYID = new Map(M.map((q) => [q.id, q]));
  const REPORTS = DATA.informes;
  const years = M.map((q) => +q.anio);
  const Y0 = Math.min(...years), Y1 = Math.max(...years);
  const YEARS = Array.from({ length: Y1 - Y0 + 1 }, (_, i) => String(Y0 + i));
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const stacked = () => matchMedia("(max-width: 1100px)").matches;
  const TOPN = 8;

  // ---------- Estado (vive en la URL: se puede compartir una vista) ----------
  const S = { informe: REPORTS[0].id, tema: "", empresa: "", anio: "", q: "", sel: "", ctx: "informe", solo: false, shown: 12, tables: {} };
  const DIMS = ["tema", "empresa", "anio"];

  function readHash() {
    const h = location.hash.replace(/^#\/?/, "");
    if (h && !h.includes("=")) return false;           // ancla normal (#datos): no tocar el estado
    const p = new URLSearchParams(h);
    S.informe = REPORTS.some((r) => r.id === p.get("informe")) ? p.get("informe") : REPORTS[0].id;
    S.tema = p.get("tema") || ""; S.empresa = p.get("empresa") || ""; S.anio = p.get("anio") || "";
    S.q = (p.get("q") || "").toLowerCase();
    S.sel = BYID.has(p.get("queja")) ? p.get("queja") : "";
    return true;
  }
  function writeHash() {
    const p = new URLSearchParams();
    if (S.informe !== REPORTS[0].id) p.set("informe", S.informe);
    DIMS.forEach((d) => S[d] && p.set(d, S[d]));
    if (S.q) p.set("q", S.q);
    if (S.sel) p.set("queja", S.sel);
    if (!p.toString() && !location.hash) return;
    const next = p.toString() ? "#" + p.toString() : location.pathname + location.search;
    try { history.replaceState(null, "", next); } catch (e) { /* file:// en algunos navegadores */ }
  }

  // ---------- Filtros cruzados ----------
  const pass = (q, ex) =>
    (ex === "tema" || !S.tema || q.tema === S.tema) &&
    (ex === "empresa" || !S.empresa || q.empresa === S.empresa) &&
    (ex === "anio" || !S.anio || q.anio === S.anio) &&
    (!S.q || q.low.includes(S.q));
  const view = (ex) => M.filter((q) => pass(q, ex));         // `ex`: dimension que ese grafico no filtra (para compararla)
  const tally = (list, key) => {
    const m = new Map();
    list.forEach((q) => m.set(q[key], (m.get(q[key]) || 0) + 1));
    return [...m.entries()].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0])));
  };
  const anyFilter = () => DIMS.some((d) => S[d]) || !!S.q;
  const pct = (n, t) => (t ? (100 * n / t).toFixed(1).replace(".", ",").replace(/,0$/, "") : "0");
  const en = (s) => `<span lang="en">${esc(s)}</span>`;
  const report = () => REPORTS.find((r) => r.id === S.informe) || REPORTS[0];
  const citedIds = (r) => r.quejas_citadas.map((q) => q.id);

  // ---------- Markdown minimo y seguro (escapa primero) ----------
  function inline(s) {
    s = esc(s).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
    return s.replace(/\[([^\]]*?queja\s+\d[^\]]*?)\]/gi, (_, inner) =>
      [...inner.matchAll(/queja\s+(\d+)/gi)].map((m) => BYID.has(m[1])
        ? `<button type="button" class="cite" data-cite="${m[1]}" aria-pressed="${S.sel === m[1]}" aria-label="Ver la queja ${m[1]}">queja ${m[1]}</button>`
        : `<span class="cite missing" title="Este ID no existe en los datos: cita no verificada">queja ${m[1]} ✗</span>`).join(" "));
  }
  function markdown(src) {
    const out = []; let list = null, liOpen = false, sub = false;
    const closeSub = () => { if (sub) { out.push("</ul>"); sub = false; } };
    const closeItem = () => { closeSub(); if (liOpen) { out.push("</li>"); liOpen = false; } };
    const close = () => { closeItem(); if (list) { out.push(`</${list}>`); list = null; } };
    for (const raw of src.split("\n")) {
      const line = raw.trimEnd(); let m;
      if (!line.trim()) continue;
      if ((m = line.match(/^(#{1,4})\s+(.*)$/))) { close(); const l = Math.min(m[1].length + 1, 4); out.push(`<h${l}>${inline(m[2])}</h${l}>`); }
      else if ((m = line.match(/^(\s*)[-*•]\s+(.*)$/))) {
        if (m[1].length >= 2 && list) { if (!sub) { out.push("<ul>"); sub = true; } out.push(`<li>${inline(m[2])}</li>`); }
        else { if (list !== "ul") { close(); out.push("<ul>"); list = "ul"; } else closeItem(); out.push(`<li>${inline(m[2])}`); liOpen = true; }
      } else if ((m = line.match(/^\s*(\d+)[.)]\s+(.*)$/))) {
        if (list !== "ol") { close(); out.push("<ol>"); list = "ol"; } else closeItem();
        out.push(`<li value="${m[1]}">${inline(m[2])}`); liOpen = true;
      } else { close(); out.push(`<p>${inline(line)}</p>`); }
    }
    close();
    return out.join("\n");
  }

  // ---------- Tooltip (un solo elemento; contenido con textContent) ----------
  const tipEl = $("#tip");
  function showTip(x, y, value, label, note) {
    tipEl.replaceChildren();
    const v = document.createElement("strong"); v.textContent = value;
    const l = document.createElement("span"); l.textContent = label;
    tipEl.append(v, l);
    if (note) { tipEl.append(document.createElement("br")); const n = document.createElement("span"); n.textContent = note; tipEl.append(n); }
    tipEl.hidden = false;
    const r = tipEl.getBoundingClientRect();
    tipEl.style.left = Math.max(8, Math.min(x + 14, innerWidth - r.width - 8)) + "px";
    tipEl.style.top = Math.max(8, Math.min(y - r.height - 10, innerHeight - r.height - 8)) + "px";
  }
  const hideTip = () => { tipEl.hidden = true; };

  // ---------- 1 · Ejemplo del hero (una afirmacion real con su cita) ----------
  function renderExample() {
    const top = tally(M, "tema")[0];
    let rep = REPORTS.find((r) => r.quejas_citadas.some((q) => q.tema === top[0])) || REPORTS[0];
    const q = rep.quejas_citadas.find((x) => x.tema === top[0]) || rep.quejas_citadas[0];
    const txt = q.texto.replace(/\s+/g, " ");
    $("#example").innerHTML = `<span class="tag">Una afirmación del informe, con su prueba</span>
      <blockquote>El ${pct(top[1], M.length)} % de las quejas son del tipo «${en(top[0])}» <button type="button" class="cite" data-cite="${q.id}" data-go="informes" data-rep="${esc(rep.id)}" aria-label="Ver la queja ${q.id}">queja ${q.id}</button></blockquote>
      <div class="src" lang="en"><b>${esc(q.empresa)}</b> · ${esc(q.fecha)}<br>«${esc(txt.slice(0, 150))}${txt.length > 150 ? "…" : ""}»</div>
      <figcaption>Cada cita es un botón: te lleva a la queja real.</figcaption>`;
  }

  // ---------- 3 · KPIs ----------
  function renderKpis(cur) {
    const f = anyFilter();
    const kpi = (label, dim) => {
      const top = tally(cur, dim)[0];
      if (!top) return `<div class="card kpi"><div class="label">${label}</div><div class="value">—</div><p class="meta">Sin quejas con estos filtros</p></div>`;
      return `<div class="card kpi"><div class="label">${label}</div>
        <div class="value">${pct(top[1], cur.length)} %</div>
        <button type="button" class="name" data-filter="${dim}" data-value="${esc(top[0])}" aria-pressed="${S[dim] === top[0]}">${en(top[0])}</button>
        <div class="share" role="img" aria-label="${top[1]} de ${cur.length} quejas"><i style="width:${(100 * top[1] / cur.length).toFixed(1)}%"></i></div>
        <p class="meta">${top[1]} de ${cur.length} quejas</p></div>`;
    };
    $("#kpis").innerHTML = `<div class="card kpi"><div class="label">${f ? "Quejas en la selección" : "Quejas en la muestra"}</div>
        <div class="big">${cur.length}</div>
        <p class="meta">${f ? `de ${M.length} en la muestra` : `Transferencias de dinero · ${Y0}–${Y1}`}</p></div>
      ${kpi("Tema más frecuente", "tema")}${kpi("Empresa con más quejas", "empresa")}`;
  }

  // ---------- Grafico de area: quejas por año ----------
  function monotone(p) {
    const n = p.length; if (n < 2) return `M${p[0][0]},${p[0][1]}`;
    const dx = [], s = [], m = [];
    for (let i = 0; i < n - 1; i++) { dx[i] = p[i + 1][0] - p[i][0]; s[i] = (p[i + 1][1] - p[i][1]) / dx[i]; }
    m[0] = s[0]; m[n - 1] = s[n - 2];
    for (let i = 1; i < n - 1; i++) m[i] = s[i - 1] * s[i] <= 0 ? 0 : (s[i - 1] + s[i]) / 2;
    for (let i = 0; i < n - 1; i++) {
      if (s[i] === 0) { m[i] = 0; m[i + 1] = 0; continue; }
      const a = m[i] / s[i], b = m[i + 1] / s[i], h = a * a + b * b;
      if (h > 9) { const t = 3 / Math.sqrt(h); m[i] = t * a * s[i]; m[i + 1] = t * b * s[i]; }
    }
    let d = `M${p[0][0]},${p[0][1]}`;
    for (let i = 0; i < n - 1; i++) d += `C${p[i][0] + dx[i] / 3},${p[i][1] + m[i] * dx[i] / 3} ${p[i + 1][0] - dx[i] / 3},${p[i + 1][1] - m[i + 1] * dx[i] / 3} ${p[i + 1][0]},${p[i + 1][1]}`;
    return d;
  }
  const niceTop = (max) => {
    if (max <= 0) return { top: 4, step: 1 };
    const step = [1, 2, 5, 10, 20, 25, 50, 100].find((s) => max / s <= 4) || 100;
    return { top: Math.ceil(max / step) * step, step };
  };

  const plot = $("#p-anio");
  let areaGeo = null;
  function renderArea() {
    const base = view("anio");
    const counts = YEARS.map((y) => ({ k: y, n: base.filter((q) => q.anio === y).length }));
    areaGeo = { ...(areaGeo || {}), counts, total: base.length };
    renderTable("anio", "Quejas por año", ["Año", "Quejas"], counts.map((c) => [c.k, c.n]), `Muestra de ${M.length} quejas`);
    const W = plot.clientWidth;
    if (!W || plot.hidden) return;
    const H = Math.max(plot.clientHeight, 190), m = { l: 34, r: 12, t: 26, b: 28 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const { top, step } = niceTop(Math.max(...counts.map((c) => c.n)));
    const x = (i) => m.l + 14 + i * (iw - 28) / Math.max(counts.length - 1, 1);
    const y = (v) => m.t + ih - (v / top) * ih;
    const pts = counts.map((c, i) => [x(i), y(c.n)]);
    const line = monotone(pts), area = `${line}L${pts.at(-1)[0]},${y(0)}L${pts[0][0]},${y(0)}Z`;
    const selIdx = S.anio ? YEARS.indexOf(S.anio) : -1;
    const cq = BYID.get(S.sel), cqIdx = cq ? YEARS.indexOf(cq.anio) : -1;
    const maxN = Math.max(...counts.map((c) => c.n)), maxI = counts.findIndex((c) => c.n === maxN);
    const bw = (iw - 28) / Math.max(counts.length - 1, 1) * 0.8;
    const every = W < 380 ? 2 : 1;
    let g = "";
    for (let v = 0; v <= top; v += step) g += `<line class="${v ? "grid-line" : "axis-line"}" x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 8}" y="${y(v) + 4}" text-anchor="end">${v}</text>`;
    counts.forEach((c, i) => { if (i % every === 0) g += `<text x="${x(i)}" y="${H - 6}" text-anchor="middle">${c.k}</text>`; });
    plot.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" aria-hidden="true">
      ${g}
      ${selIdx >= 0 ? `<rect class="band" x="${x(selIdx) - bw / 2}" y="${m.t}" width="${bw}" height="${ih}" rx="8"/>` : ""}
      <path class="area" d="${area}"/><path class="line" d="${line}"/>
      ${counts.map((c, i) => `<circle class="mk" cx="${x(i)}" cy="${y(c.n)}" r="${i === selIdx ? 6 : 4}"/>`).join("")}
      ${cqIdx >= 0 ? `<circle class="ring" cx="${x(cqIdx)}" cy="${y(counts[cqIdx].n)}" r="9"/>` : ""}
      ${maxN > 0 ? `<text class="val-label" x="${x(maxI)}" y="${y(maxN) - 14}" text-anchor="middle">${maxN}</text>` : ""}
      <line class="hair" id="hair" y1="${m.t}" y2="${m.t + ih}" style="display:none"/>
    </svg>`;
    areaGeo.xs = counts.map((_, i) => x(i)); areaGeo.y = (n) => y(n); areaGeo.w = W; areaGeo.h = plot.clientHeight;
    if (areaGeo.focus != null) moveHover(areaGeo.focus, false);
  }
  function moveHover(i, fromPointer, ev) {
    const svg = plot.querySelector("svg"); if (!svg || !areaGeo?.xs) return;
    i = Math.max(0, Math.min(areaGeo.counts.length - 1, i));
    const c = areaGeo.counts[i], r = svg.getBoundingClientRect();
    const hair = $("#hair", svg);
    hair.setAttribute("x1", areaGeo.xs[i]); hair.setAttribute("x2", areaGeo.xs[i]); hair.style.display = "";
    const tx = fromPointer && ev ? ev.clientX : r.left + areaGeo.xs[i], ty = fromPointer && ev ? ev.clientY : r.top + areaGeo.y(c.n);
    showTip(tx, ty, `${c.n} ${c.n === 1 ? "queja" : "quejas"}`, `en ${c.k}`, areaGeo.total ? `${pct(c.n, areaGeo.total)} % de la selección` : "");
  }
  function leaveHover() { hideTip(); const h = $("#hair", plot); if (h) h.style.display = "none"; }
  function nearest(ev) {
    const r = plot.querySelector("svg").getBoundingClientRect(), px = ev.clientX - r.left;
    return areaGeo.xs.reduce((b, v, i) => (Math.abs(v - px) < Math.abs(areaGeo.xs[b] - px) ? i : b), 0);
  }
  plot.addEventListener("pointermove", (e) => { if (areaGeo?.xs) { areaGeo.focus = null; moveHover(nearest(e), true, e); } });
  plot.addEventListener("pointerleave", () => leaveHover());
  plot.addEventListener("click", (e) => { if (areaGeo?.xs) toggle("anio", YEARS[nearest(e)]); });
  plot.addEventListener("keydown", (e) => {
    if (!areaGeo?.xs) return;
    const n = areaGeo.counts.length, cur = areaGeo.focus ?? (S.anio ? YEARS.indexOf(S.anio) : 0);
    if (e.key === "ArrowRight") areaGeo.focus = Math.min(n - 1, cur + 1);
    else if (e.key === "ArrowLeft") areaGeo.focus = Math.max(0, cur - 1);
    else if (e.key === "Home") areaGeo.focus = 0;
    else if (e.key === "End") areaGeo.focus = n - 1;
    else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); return toggle("anio", YEARS[cur]); }
    else return;
    e.preventDefault(); moveHover(areaGeo.focus, false);
  });
  plot.addEventListener("focus", () => { if (areaGeo?.xs && areaGeo.focus == null) { areaGeo.focus = S.anio ? YEARS.indexOf(S.anio) : 0; moveHover(areaGeo.focus, false); } });
  plot.addEventListener("blur", () => { if (areaGeo) areaGeo.focus = null; leaveHover(); });
  new ResizeObserver(() => {
    if (areaGeo && plot.clientWidth && (plot.clientWidth !== areaGeo.w || plot.clientHeight !== areaGeo.h)) renderArea();
  }).observe(plot);

  // ---------- Barras horizontales ----------
  function renderBars(id, dim, entries, total, label) {
    const host = $("#p-" + id), selV = S[dim], cq = BYID.get(S.sel);
    const top = entries.slice(0, TOPN);
    if (selV && !top.some((e) => e[0] === selV)) { const e = entries.find((x) => x[0] === selV); if (e) top.push(e); }
    renderTable(id, label, [dim === "tema" ? "Tema" : "Empresa", "Quejas", "% de la selección"], entries.map(([k, n]) => [k, n, pct(n, total) + " %"]), "");
    if (!top.length) { host.innerHTML = '<p class="empty">Sin quejas con estos filtros.</p>'; return; }
    const max = Math.max(...top.map((e) => e[1]), 1);
    host.innerHTML = top.map(([name, n]) => `<button type="button" class="row${selV && name !== selV ? " dim" : ""}" aria-pressed="${name === selV}" data-filter="${dim}" data-value="${esc(name)}" data-n="${n}" data-total="${total}">
        <span class="lab">${cq && cq[dim] === name ? '<i class="dot" title="Contiene la queja abierta" aria-hidden="true"></i>' : ""}${en(name)}</span>
        <span class="num">${n} · ${pct(n, total)} %</span>
        <span class="track"><i data-w="${(100 * n / max).toFixed(1)}" style="width:${reduceMotion ? (100 * n / max).toFixed(1) : 0}%"></i></span></button>`).join("");
    host.dataset.total = entries.length;
    host.insertAdjacentHTML("beforeend", '<p class="more-note" hidden></p>');
    fitBars(host);
    if (!reduceMotion) requestAnimationFrame(() => $$(".track i", host).forEach((i) => { i.style.width = i.dataset.w + "%"; }));
  }
  // Muestra solo las filas que caben enteras (nada queda cortado) y avisa de cuantas quedan en la tabla
  function fitBars(host) {
    const rows = $$(".row", host), note = $(".more-note", host), total = +host.dataset.total || rows.length;
    if (!rows.length || !note || host.hidden) return;
    rows.forEach((r) => { r.hidden = false; });
    note.hidden = true;
    let shown = rows.length;
    while (shown > 3 && host.scrollHeight > host.clientHeight + 1) {
      rows[--shown].hidden = true;
      note.hidden = false;
      note.textContent = `+${total - shown} más en «Ver tabla»`;
    }
  }
  ["#p-tema", "#p-empresa"].forEach((id) => new ResizeObserver(() => requestAnimationFrame(() => fitBars($(id)))).observe($(id)));
  document.addEventListener("pointermove", (e) => { const r = e.target.closest?.(".row"); if (r) rowTip(r, e.clientX, e.clientY); });
  document.addEventListener("pointerout", (e) => { if (e.target.closest?.(".row")) hideTip(); });
  document.addEventListener("focusin", (e) => { const r = e.target.closest?.(".row"); if (r) { const b = r.getBoundingClientRect(); rowTip(r, b.left + b.width / 2, b.top); } });
  document.addEventListener("focusout", (e) => { if (e.target.closest?.(".row")) hideTip(); });
  function rowTip(r, x, y) {
    const n = +r.dataset.n, t = +r.dataset.total;
    showTip(x, y, `${n} ${n === 1 ? "queja" : "quejas"}`, r.dataset.value, `${pct(n, t)} % de la selección`);
  }

  // ---------- Tablas equivalentes ----------
  function renderTable(id, caption, heads, rows, note) {
    const host = $("#t-" + id); if (!host) return;
    host.innerHTML = `<table><caption>${esc(caption)}${note ? " · " + esc(note) : ""}</caption><thead><tr>${heads.map((h) => `<th scope="col">${esc(h)}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((r) => `<tr>${r.map((c, i) => (i === 0 ? `<th scope="row">${esc(c)}</th>` : `<td class="n">${esc(c)}</td>`)).join("")}</tr>`).join("")}</tbody></table>`;
  }
  function applyTables() {
    ["anio", "tema", "empresa"].forEach((id) => {
      const on = !!S.tables[id], btn = $(`[data-table="${id}"]`);
      $("#t-" + id).hidden = !on;
      $("#p-" + id).hidden = on;
      btn.setAttribute("aria-pressed", String(on)); btn.textContent = on ? "Ver gráfico" : "Ver tabla";
    });
  }

  // ---------- 4 · Informe ----------
  function renderPills() {
    $("#pills").innerHTML = REPORTS.map((r) => `<button type="button" data-rep="${esc(r.id)}" aria-pressed="${r.id === S.informe}">${esc(r.titulo)}</button>`).join("");
  }
  function renderReport() {
    const r = report();
    const miss = r.ids_inexistentes?.length ? `<p class="warn">Aviso: el agente citó ${r.ids_inexistentes.length} ID(s) que no existen en los datos (${esc(r.ids_inexistentes.join(", "))}); se marcan con ✗.</p>` : "";
    const keep = $("#informe").scrollTop;
    $("#informe").innerHTML = `<h1>${esc(r.titulo)}</h1>
      <p class="meta">Tema: ${esc(r.tema)} · ${r.quejas_consultadas} quejas consultadas · ${r.quejas_citadas.length} citadas · generado el ${esc(DATA.generado)}</p>
      ${miss}<div class="draft">${markdown(r.borrador)}</div>
      <section class="review" aria-labelledby="rev-h"><h2 id="rev-h">Revisión humana</h2>
        <p class="sub">En el sistema real el flujo se detiene aquí hasta que una persona decide.</p>
        <div class="actions"><button type="button" class="btn primary small" data-act="approve">Aprobar</button><button type="button" class="btn small" data-act="changes">Pedir cambios</button></div>
        <div class="demo-msg" id="demo-msg" role="status" hidden></div></section>`;
    $("#informe").scrollTop = keep;
  }

  // ---------- 5 · Lista de quejas ----------
  let LIST_IDS = [];
  function hl(text) {
    if (!S.q) return esc(text);
    const low = text.toLowerCase(); let out = "", i = 0, j;
    while ((j = low.indexOf(S.q, i)) !== -1) { out += esc(text.slice(i, j)) + "<mark>" + esc(text.slice(j, j + S.q.length)) + "</mark>"; i = j + S.q.length; }
    return out + esc(text.slice(i));
  }
  function snippet(q, n) {
    const t = q.texto.replace(/\s+/g, " ");
    let a = 0;
    if (S.q) { const i = t.toLowerCase().indexOf(S.q); if (i > 60) a = i - 40; }
    return (a ? "…" : "") + hl(t.slice(a, a + n)) + (a + n < t.length ? "…" : "");
  }
  function renderList(cur) {
    const r = report(), cited = new Set(citedIds(r));
    let list = [...cur].sort((a, b) => b.fecha.localeCompare(a.fecha) || a.id.localeCompare(b.id));
    if (S.solo) list = list.filter((q) => cited.has(q.id));
    LIST_IDS = list.map((q) => q.id);
    const shown = list.slice(0, S.shown);
    const chips = [
      ...DIMS.filter((d) => S[d]).map((d) => `<button type="button" class="chip" data-filter="${d}" data-value="${esc(S[d])}" aria-label="Quitar filtro ${esc(S[d])}">${esc(S[d])} <span aria-hidden="true">✕</span></button>`),
      S.q ? `<button type="button" class="chip" data-act="clearq" aria-label="Quitar búsqueda">«${esc(S.q)}» <span aria-hidden="true">✕</span></button>` : "",
    ].join("");
    const target = $("#lista"), keep = target.scrollTop;
    target.innerHTML = `<header class="card-head"><div><h3>${list.length} ${list.length === 1 ? "queja" : "quejas"}</h3>
        <p class="sub">${S.solo ? `Las citadas en «${esc(r.titulo)}»` : "En la selección actual"}. Pulsa una para ver el texto original.</p>
        ${chips ? `<div class="chips">${chips}</div>` : ""}</div>
        <label class="toggle"><input type="checkbox" data-act="solo" ${S.solo ? "checked" : ""}> Solo las citadas en el informe</label></header>
      ${shown.length ? shown.map((q) => `<button type="button" class="q-row" data-sel="${q.id}" aria-pressed="${S.sel === q.id}">
          <span class="q-ico" aria-hidden="true"><svg viewBox="0 0 20 20" width="20" height="20"><path d="M5 3.5h7l3 3V16a.5.5 0 0 1-.5.5h-9.5A.5.5 0 0 1 5 16V3.5Z M12 3.5v3h3 M7.5 10h5 M7.5 13h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/></svg></span>
          <span><span class="t">${hl(q.empresa)}</span><br><span class="s">${en(q.tema)} · ${esc(q.fecha)}</span><br><span class="x" lang="en">${snippet(q, 120)}</span></span>
          ${cited.has(q.id) ? '<span class="chip static">citada</span>' : `<span class="s">${esc(q.estado)}</span>`}</button>`).join("")
        : '<p class="empty">Ninguna queja coincide con estos filtros.</p>'}
      ${list.length > shown.length ? `<button type="button" class="btn small more" data-act="more">Mostrar más (${list.length - shown.length})</button>` : ""}`;
    target.scrollTop = keep;
  }

  // ---------- Evidencia (panel fijo al lado, en Informes y en Quejas) ----------
  function renderEvidence() {
    $$("[data-ev]").forEach((el) => {
      const ctx = el.dataset.ev, r = report();
      const ids = ctx === "informe" ? citedIds(r) : LIST_IDS;
      const q = BYID.get(S.sel);
      if (!q) {
        el.innerHTML = ctx === "informe"
          ? `<h4 class="eyebrow">Evidencia</h4><p class="hint">Pulsa una cita <b>[queja N]</b> del informe para leer aquí la queja original, con su empresa, tema y fecha.</p>
             <h4 class="eyebrow">Citadas en este informe (${ids.length})</h4>
             <div class="q-list">${ids.map((id) => { const x = BYID.get(id); return x ? `<button type="button" data-sel="${id}" data-ctx="informe">queja ${id}<small>${esc(x.empresa)} · ${esc(x.fecha)}</small></button>` : ""; }).join("")}</div>`
          : `<h4 class="eyebrow">Evidencia</h4><p class="hint">Elige una queja de la lista para leerla completa. Es el texto original, tal como lo escribió el cliente.</p>`;
        return;
      }
      const i = ids.indexOf(q.id);
      el.innerHTML = `<div class="q-id"><span>ID ${esc(q.id)}${i >= 0 ? ` · ${i + 1} de ${ids.length}` : ""}</span><button type="button" class="q-clear" data-act="clearsel" aria-label="Cerrar la queja">✕</button></div>
        <h3 class="q-title">${en(q.tema)}</h3>
        <dl class="q-meta"><dt>Empresa</dt><dd>${esc(q.empresa)}</dd><dt>Fecha</dt><dd>${esc(q.fecha)}</dd><dt>Estado</dt><dd>${esc(q.estado)}</dd></dl>
        <p class="q-text" lang="en">${hl(q.texto)}</p>
        <p class="q-note">Texto original en inglés. Los datos personales están anonimizados («XXXX»).</p>
        <div class="q-actions">
          <button type="button" class="btn small" data-filter="tema" data-value="${esc(q.tema)}">Filtrar por este tema</button>
          <button type="button" class="btn small" data-filter="empresa" data-value="${esc(q.empresa)}">Filtrar por esta empresa</button>
          <button type="button" class="btn small" data-filter="anio" data-value="${q.anio}">Filtrar por ${q.anio}</button></div>
        <div class="q-nav">
          <button type="button" class="btn small" data-nav="-1" data-ctx="${ctx}" ${i <= 0 ? "disabled" : ""}>← Anterior</button>
          <button type="button" class="btn small" data-nav="1" data-ctx="${ctx}" ${i < 0 || i >= ids.length - 1 ? "disabled" : ""}>Siguiente →</button></div>`;
    });
  }
  function openQueja(id, ctx) {
    S.sel = id; if (ctx) S.ctx = ctx;
    render();
    if (stacked()) requestAnimationFrame(() => $(`[data-ev="${S.ctx}"]`)?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "nearest" }));
  }

  // ---------- Filtros ----------
  function toggle(dim, value) { S[dim] = S[dim] === value ? "" : value; S.shown = 12; render(); }
  function fillSelects() {
    const t = tally(M, "tema"), c = tally(M, "empresa").slice(0, 30);
    if (S.empresa && !c.some((e) => e[0] === S.empresa)) c.push([S.empresa, M.filter((q) => q.empresa === S.empresa).length]);
    const opt = (v, label, cur) => `<option value="${esc(v)}"${v === cur ? " selected" : ""}>${esc(label)}</option>`;
    $("#f-tema").innerHTML = opt("", "Todos", S.tema) + t.map(([k, n]) => opt(k, `${k} (${n})`, S.tema)).join("");
    $("#f-empresa").innerHTML = opt("", "Todas", S.empresa) + c.map(([k, n]) => opt(k, `${k} (${n})`, S.empresa)).join("");
    $("#f-anio").innerHTML = opt("", "Todos", S.anio) + YEARS.map((y) => opt(y, y, S.anio)).join("");
  }

  // ---------- Pintado completo ----------
  let pending = false;
  function render() { if (!pending) { pending = true; queueMicrotask(draw); } }
  const SEL = "[data-filter],[data-cite],[data-sel],[data-rep],[data-table],[data-act],[data-nav]";
  function sigOf(el) { const a = el?.closest?.(SEL); return a ? { ...a.dataset, tag: a.tagName } : null; }
  function refocus(sig) {
    if (!sig) return;
    const cand = $$(SEL).find((e) => e.tagName === sig.tag && Object.keys(sig).every((k) => k === "tag" || e.dataset[k] === sig[k]));
    cand?.focus({ preventScroll: true });
  }
  function draw() {
    pending = false;
    const sig = sigOf(document.activeElement);
    const cur = view();
    fillSelects();
    DIMS.forEach((d) => $("#f-" + d).classList.toggle("on", !!S[d]));
    $("#clear").hidden = !anyFilter();
    $("#count").textContent = `${cur.length} de ${M.length} quejas${anyFilter() ? " en la selección." : "."}`;
    renderKpis(cur);
    renderArea();
    renderBars("tema", "tema", tally(view("tema"), "tema"), view("tema").length, "Temas de las quejas");
    renderBars("empresa", "empresa", tally(view("empresa"), "empresa"), view("empresa").length, "Quejas por empresa");
    applyTables();
    renderPills(); renderReport(); renderList(cur); renderEvidence();
    writeHash();
    if (sig) refocus(sig);
  }

  // ---------- Eventos ----------
  document.addEventListener("click", (e) => {
    const t = e.target.closest("button, input[data-act]");
    if (!t) return;
    const d = t.dataset;
    if (d.go) {                                        // ejemplo del hero: abre esa queja en Informes
      S.informe = d.rep || S.informe; S.sel = d.cite; S.ctx = "informe"; render();
      return $("#informes").scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    }
    if (d.rep) { S.informe = d.rep; S.sel = ""; S.ctx = "informe"; return render(); }
    if (d.filter) return toggle(d.filter, d.value);
    if (d.cite) return openQueja(d.cite, "informe");
    if (d.sel) return openQueja(d.sel, d.ctx || (t.closest("#lista") ? "quejas" : "informe"));
    if (d.table) { S.tables[d.table] = !S.tables[d.table]; return render(); }
    if (d.nav) {
      const ids = d.ctx === "informe" ? citedIds(report()) : LIST_IDS, i = ids.indexOf(S.sel) + Number(d.nav);
      if (ids[i]) { S.sel = ids[i]; render(); }
      return;
    }
    if (d.act === "more") { S.shown += 12; return render(); }
    if (d.act === "solo") { S.solo = t.checked; S.shown = 12; return render(); }
    if (d.act === "clearsel") { S.sel = ""; return render(); }
    if (d.act === "clearq") { S.q = ""; $("#q").value = ""; return render(); }
    if (d.act === "approve" || d.act === "changes") {
      const msg = $("#demo-msg");
      const real = d.act === "approve"
        ? "Aprobar llama a <code>PATCH /jobs/{id}/review</code> con <code>{\"action\": \"approve\"}</code> y el flujo termina."
        : "Pedir cambios llama a <code>PATCH /jobs/{id}/review</code> con <code>{\"action\": \"changes\", \"feedback\": \"...\"}</code> y los agentes repiten la investigación con ese comentario.";
      msg.innerHTML = `<b>Demostración:</b> aquí no se envía nada. En la versión real, ${real}`; msg.hidden = false;
    }
  });
  DIMS.forEach((d) => $("#f-" + d).addEventListener("change", (e) => { S[d] = e.target.value; S.shown = 12; render(); }));
  $("#clear").addEventListener("click", () => { DIMS.forEach((d) => (S[d] = "")); S.q = ""; $("#q").value = ""; S.shown = 12; render(); });
  let qTimer;
  $("#q").addEventListener("input", (e) => { clearTimeout(qTimer); qTimer = setTimeout(() => { S.q = e.target.value.trim().toLowerCase(); S.shown = 12; render(); }, 150); });
  addEventListener("hashchange", () => { if (readHash()) { $("#q").value = S.q; render(); } });

  // ---------- Navegacion: seccion activa ----------
  const links = $$(".dots a"), navLinks = $$(".nav-links a[href^='#']");
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((en_) => {
      if (!en_.isIntersecting) return;
      const id = en_.target.id;
      links.forEach((a) => a.classList.toggle("on", a.dataset.s === id));
      navLinks.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + id));
    });
  }, { threshold: 0.55 });
  $$(".screen").forEach((s) => spy.observe(s));

  // ---------- Evaluacion y fuente ----------
  const evals = DATA.evaluacion ?? [];
  $("#eval-intro").textContent = evals.length
    ? "Preguntas con respuesta conocida. Las seis primeras se calculan con código; las demás se revisan a mano."
    : "Sin preguntas de evaluación: ejecuta scripts/eval_truth.py y vuelve a exportar.";
  $("#eval-table tbody").innerHTML = evals.map((r) =>
    `<tr><td>${r.n}</td><td>${esc(r.pregunta)}</td><td>${esc(r.correcta)}</td><td>${r.resultado ? esc(r.resultado) : '<span class="sub">Pendiente</span>'}</td></tr>`).join("");
  function fitEval() {
    const wrap = $(".table-wrap"), rows = $$("#eval-table tbody tr"), note = $("#eval-more");
    if (!wrap || !rows.length) return;
    rows.forEach((r) => { r.hidden = false; }); note.hidden = true;
    let shown = rows.length;
    while (shown > 3 && wrap.scrollHeight > wrap.clientHeight + 1) {
      rows[--shown].hidden = true; note.hidden = false;
      note.textContent = `+${rows.length - shown} preguntas más, en docs/eval_question.md del repositorio.`;
    }
  }
  new ResizeObserver(() => requestAnimationFrame(fitEval)).observe($(".table-wrap"));
  $("#source-note").textContent = `Datos: ${M.length} quejas de transferencias de dinero, muestra de ${DATA.fuente}. Informes generados el ${DATA.generado} con el agente real; esta página no llama a ningún modelo.`;

  // ---------- Inicio ----------
  readHash();
  $("#q").value = S.q;
  renderExample();
  draw();
})();
