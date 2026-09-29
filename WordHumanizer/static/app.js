(() => {
  const $ = (id) => document.getElementById(id);
  let file = null;
  let jobId = null;
  let timer = null;
  let config = null;

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);

  async function loadConfig() {
    config = await (await fetch("/api/config")).json();
    const lang = $("language");
    for (const [code, name] of Object.entries(config.languages)) {
      lang.add(new Option(name, code, false, code === config.default_language));
    }
    for (const style of config.rewrite_styles) {
      $("rewrite_style").add(new Option(style[0].toUpperCase() + style.slice(1), style));
    }
    if (!config.rewrite_available) {
      const box = document.querySelector('[data-opt="rewrite"]');
      box.disabled = true;
      $("rewrite-row").title = "Set REWRITE_PROVIDER in .env to enable rewriting";
      $("rewrite-row").insertAdjacentHTML("beforeend", ' <span class="hint">(not configured)</span>');
    }
    toggleStyle();
  }

  function toggleStyle() {
    const on = document.querySelector('[data-opt="rewrite"]').checked;
    $("style-row").classList.toggle("hidden", !on);
  }

  function applyMode() {
    const standard = $("mode").value === "standard";
    const set = (opt, value) => { document.querySelector(`[data-opt="${opt}"]`).checked = value; };
    set("protect_numbers", !standard);
    set("auto_detect_terms", !standard);
    set("process_headings", standard);
  }

  function pick(f) {
    if (!f) return;
    if (!/\.(docx|doc)$/i.test(f.name)) {
      $("error").textContent = "Please choose a .docx or .doc file.";
      return;
    }
    if (config && f.size > config.max_upload_mb * 1024 * 1024) {
      $("error").textContent = `The file is larger than ${config.max_upload_mb} MB.`;
      return;
    }
    file = f;
    $("error").textContent = "";
    $("drop-text").innerHTML = `<strong>${esc(f.name)}</strong><br>${(f.size / 1024).toFixed(0)} KB — click to change`;
    $("go").disabled = false;
  }

  function collectOptions() {
    const options = {
      language: $("language").value,
      mode: $("mode").value,
      rewrite_style: $("rewrite_style").value,
      protected_terms: $("terms").value,
      skip_capitalized_spelling: $("mode").value === "academic",
    };
    document.querySelectorAll("[data-opt]").forEach((el) => { options[el.dataset.opt] = el.checked; });
    return options;
  }

  async function start() {
    if (!file) return;
    $("go").disabled = true;
    $("error").textContent = "";
    const body = new FormData();
    body.append("file", file);
    body.append("options", JSON.stringify(collectOptions()));
    try {
      const res = await fetch("/api/jobs", { method: "POST", body });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      jobId = data.id;
      $("upload-card").classList.add("hidden");
      $("progress-card").classList.remove("hidden");
      $("job-name").textContent = file.name;
      poll();
    } catch (err) {
      $("error").textContent = err.message;
      $("go").disabled = false;
    }
  }

  async function poll() {
    clearTimeout(timer);
    try {
      const res = await fetch(`/api/jobs/${jobId}`);
      const job = await res.json();
      if (!res.ok) throw new Error(job.detail || "Job lost");
      $("bar-fill").style.width = `${Math.round(job.progress * 100)}%`;
      $("status").textContent = `${Math.round(job.progress * 100)}% — ${job.message}`;
      if (job.status === "done") return showResult(job);
      if (job.status === "failed" || job.status === "cancelled") {
        reset();
        $("error").textContent = job.status === "failed" ? `Processing failed: ${job.error}` : "Cancelled.";
        return;
      }
      timer = setTimeout(poll, 1000);
    } catch (err) {
      reset();
      $("error").textContent = err.message;
    }
  }

  function stat(value, label) {
    return `<div class="stat"><b>${esc(value)}</b><span>${esc(label)}</span></div>`;
  }

  function showResult(job) {
    const r = job.report;
    $("progress-card").classList.add("hidden");
    $("result-card").classList.remove("hidden");
    const p = r.protected || {};
    const g = r.corrections_by_group || {};
    const locked = Object.entries(p).filter(([k]) => k.startsWith("format:")).reduce((a, [, v]) => a + v, 0);
    $("stats").innerHTML = [
      stat(r.processed, "paragraphs processed"),
      stat(r.skipped, "paragraphs skipped"),
      stat(r.corrections, "corrections"),
      stat(`${g.grammar || 0} / ${g.spelling || 0}`, "grammar / spelling"),
      stat(`${g.punctuation || 0} / ${g.style || 0}`, "punctuation / style"),
      stat(r.rewritten, "paragraphs rewritten"),
      stat(p.citation || 0, "citations protected"),
      stat((p.url || 0) + (p.doi || 0) + (p.email || 0), "URLs protected"),
      stat(p.term || 0, "terms protected"),
      stat(locked, "locked runs (links, fields…)"),
      stat(r.document.tables, "tables"),
      stat(`${Math.round(r.duration_seconds)} s`, "processing time"),
    ].join("");
    $("download").href = `/api/jobs/${job.id}/download`;
    $("download").textContent = `Download ${job.output_filename}`;
    $("download-report").href = `/api/jobs/${job.id}/report?format=txt`;
    $("checks").innerHTML = r.checks.map((c) =>
      `<li class="${c.passed ? "" : "fail"}">${esc(c.check)}${c.detail ? ` — ${esc(c.detail)}` : ""}</li>`).join("");
    const notes = [...r.errors, ...r.warnings];
    $("warnings-box").classList.toggle("hidden", notes.length === 0);
    $("warnings").innerHTML = notes.map((w) => `<li>${esc(w)}</li>`).join("");
    $("change-count").textContent = `(${r.changes.length})`;
    $("changes").innerHTML = r.changes.length ? r.changes.map((c) => c.type === "rewrite"
      ? `<div class="change"><div class="meta">${esc(c.location)} · rewrite</div><del>${esc(c.before)}</del><br><ins>${esc(c.after)}</ins></div>`
      : `<div class="change"><div class="meta">${esc(c.location)} · ${esc(c.group)} · ${esc(c.message)}</div>` +
        `${esc(c.context).replace(esc(c.before), `<del>${esc(c.before)}</del><ins>${esc(c.after)}</ins>`)}</div>`
    ).join("") : '<p class="muted">No changes were needed.</p>';
  }

  function reset() {
    clearTimeout(timer);
    $("progress-card").classList.add("hidden");
    $("result-card").classList.add("hidden");
    $("upload-card").classList.remove("hidden");
    $("go").disabled = !file;
    $("bar-fill").style.width = "0";
  }

  const drop = $("drop");
  ["dragenter", "dragover"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", (ev) => pick(ev.dataTransfer.files[0]));
  $("file").addEventListener("change", (ev) => pick(ev.target.files[0]));
  $("go").addEventListener("click", start);
  $("mode").addEventListener("change", applyMode);
  document.querySelector('[data-opt="rewrite"]').addEventListener("change", toggleStyle);
  $("cancel").addEventListener("click", async () => {
    if (jobId) await fetch(`/api/jobs/${jobId}`, { method: "DELETE" });
    reset();
    $("error").textContent = "Cancelled.";
  });
  $("again").addEventListener("click", () => {
    if (jobId) fetch(`/api/jobs/${jobId}`, { method: "DELETE" });
    jobId = null;
    reset();
  });

  loadConfig().catch(() => { $("error").textContent = "Cannot reach the server."; });
})();
