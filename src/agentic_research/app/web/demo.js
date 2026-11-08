"use strict";
// Backend simulado para la demo publica: misma interfaz, sin API, worker ni Redis.
// El estado de cada job es una funcion del tiempo transcurrido, asi no hacen falta timers.
(() => {
  const STEP = 1500;      // ms entre eventos de la traza
  const QUEUED = 1200;    // ms en cola antes de empezar
  const RESUMING = 700;   // ms hasta que arranca una nueva revision
  const KEY = "demoJobs";
  const SECTIONS = { en: ["findings", "risks", "recommendations"], es: ["hallazgos", "riesgos", "recomendaciones"] };

  const T = {
    en: {
      seed: "Drop-off during app sign-up",
      topicShort: "Write at least 3 characters.",
      notAwaiting: "This job is not waiting for review.",
      notFound: "Job not found",
      feedbackReq: "Feedback is required when requesting changes.",
      r1: "No research yet, so only the researcher can act.",
      r1b: "Reviewer feedback needs fresh evidence: researching again.",
      r2: "There is evidence to assess before writing.",
      r3: "Research and analysis are ready; time to write the report.",
      r4: "A draft exists, so the flow can finish.",
      noteH: "Reviewer note",
      noteP: (f) => `Changes requested: “${f}”. In the real system the agents re-run the research with this feedback and rewrite the report.`,
      draft: `## Findings
- **38%** of new users drop off at the SMS verification step [analytics.md].
- Interviewees say the code *takes too long* to arrive [interviews.md, support.md].

## Risks
The 2025 report puts drop-off at 31% [report2025.md], which contradicts the analytics figure and lowers confidence in the trend.

## Recommendations
1. Offer email verification as an alternative to SMS.
2. Measure SMS delivery time per carrier.
3. Re-run the funnel analysis with a single definition of "drop-off".

## Uncertainties
- The two sources use different time windows.
- There is no data on users who retry the verification.`,
      sources: [
        { file: "analytics.md", excerpt: "38% of users abandon the sign-up flow at the SMS verification step." },
        { file: "interviews.md", excerpt: "\"The code took more than two minutes and I got tired of waiting.\"" },
        { file: "support.md", excerpt: "Tickets about SMS not received: 212 in the last quarter." },
        { file: "report2025.md", excerpt: "Sign-up drop-off was 31% in 2025, measured over the full year." },
      ],
    },
    es: {
      seed: "Abandono en el registro de la app",
      topicShort: "Escribe al menos 3 caracteres.",
      notAwaiting: "Este trabajo no está esperando revisión.",
      notFound: "Job no encontrado",
      feedbackReq: "El comentario es obligatorio al pedir cambios.",
      r1: "Aún no hay investigación, así que solo puede actuar el investigador.",
      r1b: "El comentario del revisor requiere evidencia nueva: se investiga de nuevo.",
      r2: "Hay evidencia que valorar antes de redactar.",
      r3: "Investigación y análisis listos; toca redactar el informe.",
      r4: "Ya hay borrador, así que el flujo puede terminar.",
      noteH: "Nota del revisor",
      noteP: (f) => `Cambios pedidos: «${f}». En el sistema real los agentes repiten la investigación con este comentario y reescriben el informe.`,
      draft: `## Hallazgos
- El **38%** de los usuarios nuevos abandona en el paso de verificación por SMS [analitica.md].
- En las entrevistas dicen que el código *tarda demasiado* en llegar [entrevistas.md, soporte.md].

## Riesgos
El informe de 2025 sitúa el abandono en el 31% [informe2025.md], lo que contradice a la analítica y reduce la confianza en la tendencia.

## Recomendaciones
1. Ofrecer verificación por correo como alternativa al SMS.
2. Medir el tiempo de entrega del SMS por operadora.
3. Repetir el análisis del embudo con una única definición de "abandono".

## Incertidumbres
- Las dos fuentes usan ventanas de tiempo distintas.
- No hay datos de usuarios que reintentan la verificación.`,
      sources: [
        { file: "analitica.md", excerpt: "El 38% de los usuarios abandona el registro en el paso de verificación por SMS." },
        { file: "entrevistas.md", excerpt: "\"El código tardó más de dos minutos y me cansé de esperar.\"" },
        { file: "soporte.md", excerpt: "Tickets por SMS no recibido: 212 en el último trimestre." },
        { file: "informe2025.md", excerpt: "El abandono en el registro fue del 31% en 2025, medido sobre todo el año." },
      ],
    },
  };

  const events = (rev, c) => [
    { kind: "supervisor", step: 1, route: "researcher", reason: rev ? c.r1b : c.r1 },
    { kind: "agent_done", agent: "researcher" },
    { kind: "supervisor", step: 2, route: "analyst", reason: c.r2 },
    { kind: "agent_done", agent: "analyst" },
    { kind: "supervisor", step: 3, route: "synthesizer", reason: c.r3 },
    { kind: "agent_done", agent: "synthesizer" },
    { kind: "supervisor", step: 4, route: "finish", reason: c.r4 },
  ].map((e) => ({ ...e, revision: rev }));
  const NEV = 7;

  const now = Date.now();
  const seed = () => [{
    id: "sample", topic: null, sections: null, detail_level: "high",
    created_at: now / 1000 - 86400, runs: [{ start: now - 86400000, rev: 0 }], feedbacks: [], approved: true,
  }];
  const load = () => { try { return JSON.parse(sessionStorage.getItem(KEY)); } catch { return null; } };
  const jobs = load() ?? seed();
  const save = () => sessionStorage.setItem(KEY, JSON.stringify(jobs));

  function view(job, lang) {
    const c = T[lang];
    const t = Date.now();
    const trace = [];
    let complete = true, lead = QUEUED, elapsed = 0;
    job.runs.forEach((r, i) => {
      lead = r.rev === 0 ? QUEUED : RESUMING;
      elapsed = t - r.start;
      const n = elapsed < lead ? 0 : Math.min(NEV, Math.floor((elapsed - lead) / STEP) + 1);
      trace.push(...events(r.rev, c).slice(0, n));
      complete = n === NEV;
    });
    const last = job.runs[job.runs.length - 1];
    let status;
    if (job.approved) status = "completed";
    else if (!complete) status = elapsed < lead ? (last.rev === 0 ? "queued" : "resuming") : "running";
    else status = "awaiting_review";

    const rev = complete ? last.rev : Math.max(0, last.rev - 1);
    const out = {
      id: job.id, status, topic: job.topic ?? c.seed, sections: job.sections ?? SECTIONS[lang],
      detail_level: job.detail_level, created_at: job.created_at, revision: rev, trace,
    };
    if (status === "awaiting_review" || status === "completed") {
      const fb = job.feedbacks[last.rev - 1];
      out.draft = c.draft + (last.rev > 0 ? `\n\n## ${c.noteH}\n${c.noteP(fb)}` : "");
      out.sources = c.sources;
      out.references = c.sources.map((s) => s.file);
    }
    return out;
  }

  const fail = (message, status) => Object.assign(new Error(message), { status });

  window.demoApi = async (path, opts = {}, lang = "en") => {
    const c = T[lang];
    await new Promise((r) => setTimeout(r, 120 + Math.random() * 180)); // latencia de red simulada
    const method = (opts.method || "GET").toUpperCase();
    const body = opts.body ? JSON.parse(opts.body) : {};
    const [p] = path.split("?");
    let m;

    if (p === "/jobs" && method === "GET") {
      return [...jobs].sort((a, b) => b.created_at - a.created_at).map((j) => view(j, lang));
    }
    if (p === "/jobs" && method === "POST") {
      const topic = String(body.topic || "").trim();
      if (topic.length < 3) throw fail(c.topicShort, 422);
      const id = "d" + Math.random().toString(36).slice(2, 8);
      jobs.push({
        id, topic, sections: body.sections?.length ? body.sections : SECTIONS[lang],
        detail_level: body.detail_level || "low", created_at: Date.now() / 1000,
        runs: [{ start: Date.now(), rev: 0 }], feedbacks: [], approved: false,
      });
      save();
      return { job_id: id, status: "queued" };
    }
    if ((m = p.match(/^\/jobs\/([^/]+)$/)) && method === "GET") {
      const job = jobs.find((j) => j.id === decodeURIComponent(m[1]));
      if (!job) throw fail(c.notFound, 404);
      return view(job, lang);
    }
    if ((m = p.match(/^\/jobs\/([^/]+)\/review$/)) && method === "PATCH") {
      const job = jobs.find((j) => j.id === decodeURIComponent(m[1]));
      if (!job) throw fail(c.notFound, 404);
      if (view(job, lang).status !== "awaiting_review") throw fail(c.notAwaiting, 409);
      if (body.action === "approve") job.approved = true;
      else {
        if (!String(body.feedback || "").trim()) throw fail(c.feedbackReq, 422);
        job.feedbacks.push(body.feedback.trim());
        job.runs.push({ start: Date.now(), rev: job.runs.length });
      }
      save();
      return { job_id: job.id, status: "resuming" };
    }
    throw fail("Not found", 404);
  };
})();
