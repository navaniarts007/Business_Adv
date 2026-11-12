// Vyapar Mitra front-end: profiles, ask/answer, knowledge base, history. No build step.
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

const SEGMENT_LABELS = {
  farmer: "Farmer", artisan: "Artisan", retail: "Shop / vendor",
  msme: "MSME", startup: "Startup", company: "Company",
};

const SUGGESTIONS = {
  farmer: [
    "Should I sell my tomatoes this week or wait? Check nearby mandi prices and the weather.",
    "Which crop will give the best profit next season on my land?",
    "Which government schemes and loans can I get as a small farmer?",
    "How do I start selling directly to city buyers or through e-NAM?",
  ],
  artisan: [
    "How can I sell my handmade products online and get a better price?",
    "Am I eligible for PM Vishwakarma? What will I get?",
    "Which exhibitions or buyers near me buy crafts like mine?",
  ],
  retail: [
    "How can my shop compete with quick-commerce apps?",
    "Which products sell best in my area this festival season?",
    "How can I get a small loan for stock without collateral?",
  ],
  msme: [
    "How do I get a collateral-free loan to expand my unit?",
    "My buyer delays payment by 90 days. What can I do?",
    "How can I start exporting my products? Step by step.",
    "Which government tenders on GeM fit my business?",
  ],
  startup: [
    "Is there real market demand for my idea? Research competitors and market size.",
    "Which grants and seed funds can I apply for right now?",
    "How should I price my SaaS product for Indian SMEs?",
    "What registrations and compliance do I need in year one?",
  ],
  company: [
    "Give me a growth strategy for the next 12 months with numbers.",
    "Which PLI or state incentives apply to my sector?",
    "Should we raise funds through an SME IPO, a bank loan or private equity?",
    "What is our compliance calendar for this financial year?",
  ],
};

const SPEECH_LANG = {
  English: "en-IN", Tamil: "ta-IN", Hindi: "hi-IN", Telugu: "te-IN", Kannada: "kn-IN", Malayalam: "ml-IN",
  Marathi: "mr-IN", Bengali: "bn-IN", Gujarati: "gu-IN", Punjabi: "pa-IN", Odia: "or-IN",
};

const state = { profiles: [], profile: null, segment: "farmer", status: null };

// ---------------- theme: light by default, toggle to dark ----------------
function initTheme() {
  const saved = store.get("theme");
  // Default to light (user asked for light theme); respect a saved choice otherwise.
  document.documentElement.dataset.theme = saved === "dark" ? "dark" : "light";
}
function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  store.set("theme", next);
}
$("#theme-toggle").addEventListener("click", toggleTheme);
initTheme();

// ---------------- helpers ----------------
async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : res.statusText);
  return data;
}
const esc = (s = "") => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const safeUrl = (u) => (/^https?:\/\//i.test(u) ? u : "#");
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch {} },
};

// Small markdown renderer (headings, lists, tables, bold/italic, links, code, quotes).
function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
}
function markdown(src = "") {
  const lines = src.replace(/\r/g, "").split("\n");
  let html = "", list = null, para = [];
  const flushPara = () => { if (para.length) { html += `<p>${inline(para.join(" "))}</p>`; para = []; } };
  const closeList = () => { if (list) { html += `</${list}>`; list = null; } };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const t = line.trim();
    if (!t) { flushPara(); closeList(); continue; }
    let m;
    if ((m = t.match(/^(#{1,4})\s+(.*)$/))) { flushPara(); closeList(); html += `<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`; continue; }
    if (/^(-{3,}|\*{3,})$/.test(t)) { flushPara(); closeList(); html += "<hr>"; continue; }
    if (t.startsWith("|") && lines[i + 1] && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
      flushPara(); closeList();
      const cells = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => inline(c.trim()));
      html += `<div class="table-wrap"><table><thead><tr>${cells(t).map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>`;
      i += 2;
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        html += `<tr>${cells(lines[i]).map((c) => `<td>${c}</td>`).join("")}</tr>`; i++;
      }
      i--; html += "</tbody></table></div>"; continue;
    }
    if ((m = t.match(/^[-*•]\s+(.*)$/)) || (m = t.match(/^\d+[.)]\s+(.*)$/))) {
      flushPara();
      const type = /^\d/.test(t) ? "ol" : "ul";
      if (list !== type) { closeList(); html += `<${type}>`; list = type; }
      html += `<li>${inline(m[1])}</li>`; continue;
    }
    if (t.startsWith(">")) { flushPara(); closeList(); html += `<blockquote>${inline(t.replace(/^>\s?/, ""))}</blockquote>`; continue; }
    closeList(); para.push(t);
  }
  flushPara(); closeList();
  return html;
}

// ---------------- status ----------------
async function loadStatus() {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 10000);
  try {
    state.status = await api("/api/status", { signal: ctrl.signal });
    const el = $("#status");
    el.classList.add(state.status.ai_enabled ? "live" : "offline");
    $("#status-text").textContent = state.status.ai_enabled
      ? `Live research · ${state.status.model}`
      : "Offline · local knowledge only";
  } catch (err) {
    $("#status-text").textContent =
      err && err.name === "AbortError"
        ? "Server taking too long — check your connection, then reload"
        : "Server not reachable — is it running on port 8000?";
    console.error("status failed:", err);
  } finally {
    clearTimeout(timer);
  }
}
// Failsafe: never leave the badge stuck on "Connecting…".
setTimeout(() => {
  const t = $("#status-text");
  if (t && /connecting/i.test(t.textContent || "")) {
    t.textContent = "Server not reachable — reload the page (Ctrl+Shift+R)";
  }
}, 12000);

// ---------------- profiles ----------------
function renderSegmentPicker() {
  const fs = $("#segment-picker");
  $$(".seg", fs).forEach((b) => b.remove());
  for (const [key, label] of Object.entries(SEGMENT_LABELS)) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "seg"; b.textContent = label; b.dataset.seg = key;
    b.setAttribute("aria-pressed", String(key === state.segment));
    b.onclick = () => { state.segment = key; renderSegmentPicker(); renderSuggestions(); };
    fs.appendChild(b);
  }
  $('#profile-form [name="segment"]').value = state.segment;
}

function fillForm(p) {
  const f = $("#profile-form");
  for (const name of ["name", "business", "location", "state", "language", "stage", "turnover", "details"]) {
    f.elements[name].value = p ? (p[name] || "") : (name === "language" ? "English" : "");
  }
  state.segment = p ? p.segment : state.segment;
  renderSegmentPicker();
  renderSuggestions();
  $("#save-profile").textContent = p ? "Update profile" : "Save profile";
}

function renderProfileSelect() {
  const sel = $("#profile-select");
  sel.innerHTML = `<option value="">Guest</option>` +
    state.profiles.map((p) => `<option value="${p.id}">${esc(p.name)} · ${SEGMENT_LABELS[p.segment] || p.segment}</option>`).join("");
  sel.value = state.profile ? state.profile.id : "";
}

async function loadProfiles(selectId) {
  state.profiles = await api("/api/profiles");
  const id = selectId ?? Number(store.get("profileId"));
  state.profile = state.profiles.find((p) => p.id === id) || null;
  renderProfileSelect();
  fillForm(state.profile);
}

$("#profile-select").addEventListener("change", (e) => {
  state.profile = state.profiles.find((p) => p.id === Number(e.target.value)) || null;
  store.set("profileId", state.profile ? state.profile.id : "");
  fillForm(state.profile);
  if (!$("#panel-history").hidden) loadHistory();
});

$("#new-profile").addEventListener("click", () => {
  state.profile = null; renderProfileSelect(); fillForm(null);
  $('#profile-form [name="name"]').focus();
});

$("#profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target));
  body.segment = state.segment;
  const btn = $("#save-profile");
  btn.disabled = true;
  try {
    const saved = state.profile
      ? await api(`/api/profiles/${state.profile.id}`, { method: "PUT", body })
      : await api("/api/profiles", { method: "POST", body });
    store.set("profileId", saved.id);
    await loadProfiles(saved.id);
    btn.textContent = "Saved ✓";
    setTimeout(() => (btn.textContent = "Update profile"), 1400);
  } catch (err) {
    alertCard(`Could not save profile: ${err.message}`);
  } finally { btn.disabled = false; }
});

// ---------------- advisor ----------------
function renderSuggestions() {
  const box = $("#suggestions");
  box.innerHTML = "";
  for (const s of SUGGESTIONS[state.segment] || []) {
    const b = document.createElement("button");
    b.className = "chip"; b.type = "button"; b.textContent = s;
    b.onclick = () => { $("#question").value = s; $("#question").focus(); };
    box.appendChild(b);
  }
}

function answerCard(data, { deletable = false } = {}) {
  const node = $("#answer-tpl").content.firstElementChild.cloneNode(true);
  const stamp = $(".stamp", node);
  stamp.textContent = { quick: "Advice", research: "Research", nearby: "Near me" }[data.mode] || data.mode;
  stamp.classList.add(data.mode);
  $(".q", node).textContent = data.question;
  $(".md", node).innerHTML = markdown(data.answer);
  $(".queries", node).innerHTML = (data.search_queries || []).map((q) => `<span class="qchip">${esc(q)}</span>`).join("");
  $(".sources", node).innerHTML = (data.sources || []).map((s) =>
    `<a class="source ${esc(s.kind || "web")}" href="${esc(safeUrl(s.url))}" target="_blank" rel="noopener" title="${esc(s.url)}">${esc(s.title)}</a>`
  ).join("");
  if (data.search_widget) {
    // Google requires showing Search Suggestions with grounded answers; it is isolated in a sandboxed frame.
    const f = document.createElement("iframe");
    f.sandbox = "allow-popups allow-popups-to-escape-sandbox";
    f.srcdoc = `<base target="_blank">${data.search_widget}`;
    $(".search-widget", node).appendChild(f);
  }
  const when = data.created_at ? new Date(data.created_at.replace(" ", "T") + "Z").toLocaleString() : "just now";
  $(".meta", node).textContent = `${when} · ${data.model || ""}${data.cached ? " · from local cache" : ""}`;
  $(".speak", node).onclick = (e) => speak($(".md", node).innerText, e.currentTarget);
  $(".copy", node).onclick = async (e) => {
    try { await navigator.clipboard.writeText(data.answer); e.currentTarget.textContent = "Copied ✓"; } catch {}
  };
  $(".download-btn", node).onclick = () => {
    const blob = new Blob([`# ${data.question}\n\n${data.answer}\n\n---\n${$(".meta", node).textContent}\n`], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `vyapar-mitra-${(data.mode || "answer").replace(/\W+/g, "-")}.md`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };
  $(".print-btn", node).onclick = () => window.print();
  if (deletable && data.id) {
    const del = $(".del", node); del.hidden = false;
    del.onclick = async () => { await api(`/api/history/${data.id}`, { method: "DELETE" }); node.remove(); };
  }
  return node;
}

function alertCard(msg) {
  const node = document.createElement("article");
  node.className = "answer error";
  node.innerHTML = `<div class="md"><p>${esc(msg)}</p></div>`;
  $("#answers").prepend(node);
}

function getPosition() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(null);
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
      () => resolve(null), { timeout: 8000, maximumAge: 600000 },
    );
  });
}

async function ask() {
  const q = $("#question").value.trim();
  if (q.length < 2) { $("#question").focus(); return; }
  const mode = $('input[name="mode"]:checked').value;
  const btn = $("#ask");
  btn.disabled = true;

  const wait = document.createElement("article");
  wait.className = "answer";
  wait.innerHTML = `<div class="thinking"><span class="bars"><i></i><i></i><i></i></span>
    <span>${mode === "research" ? "Researching the web and writing your report… (20-60 s)" : mode === "nearby" ? "Looking for places near you…" : "Searching and thinking…"}</span></div>`;
  $("#answers").prepend(wait);

  try {
    const body = { question: q, mode, profile_id: state.profile ? state.profile.id : null };
    if (mode === "nearby") Object.assign(body, (await getPosition()) || {});
    const data = await api("/api/ask", { method: "POST", body });
    wait.replaceWith(answerCard(data, { deletable: true }));
    $("#question").value = "";
  } catch (err) {
    wait.remove();
    alertCard(`Sorry, something went wrong: ${err.message}`);
  } finally { btn.disabled = false; }
}
$("#ask").addEventListener("click", ask);
$("#question").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) ask(); });

// ---------------- voice ----------------
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const currentLang = () => SPEECH_LANG[$('#profile-form [name="language"]').value] || "en-IN";
if (Recognition) {
  let rec = null;
  $("#mic").addEventListener("click", () => {
    if (rec) { rec.stop(); return; }
    rec = new Recognition();
    rec.lang = currentLang(); rec.interimResults = true;
    const base = $("#question").value;
    rec.onresult = (e) => {
      $("#question").value = (base ? base + " " : "") + [...e.results].map((r) => r[0].transcript).join(" ");
    };
    rec.onend = () => { rec = null; $("#mic").classList.remove("listening"); };
    $("#mic").classList.add("listening");
    rec.start();
  });
} else {
  $("#mic").hidden = true;
}

function speak(text, btn) {
  if (!("speechSynthesis" in window)) return;
  if (speechSynthesis.speaking) { speechSynthesis.cancel(); btn.textContent = "▶ Listen"; return; }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = currentLang();
  u.onend = () => (btn.textContent = "▶ Listen");
  btn.textContent = "■ Stop";
  speechSynthesis.speak(u);
}

// ---------------- knowledge ----------------
async function loadKnowledge() {
  const q = $("#kb-search").value.trim();
  const seg = $("#kb-segment").value;
  const items = await api(`/api/knowledge?q=${encodeURIComponent(q)}&segment=${encodeURIComponent(seg)}`);
  const list = $("#kb-list");
  if (!items.length) { list.innerHTML = `<p class="empty">Nothing found. Try other words or add a local entry.</p>`; return; }
  list.innerHTML = items.map((k, i) => `
    <article class="kb-card" style="animation-delay:${Math.min(i, 12) * 30}ms">
      <div class="kb-tags">
        <span class="tag">${esc(k.segment === "all" ? "All" : SEGMENT_LABELS[k.segment] || k.segment)}</span>
        <span class="tag">${esc(k.category)}</span>
        ${k.custom ? '<span class="tag custom">Local</span>' : ""}
      </div>
      <h4>${esc(k.title)}</h4>
      <p>${esc(k.summary)}</p>
      <dl>
        ${k.eligibility ? `<dt>Who</dt><dd>${esc(k.eligibility)}</dd>` : ""}
        ${k.benefits ? `<dt>Benefit</dt><dd>${esc(k.benefits)}</dd>` : ""}
        ${k.how_to_apply ? `<dt>How</dt><dd>${esc(k.how_to_apply)}</dd>` : ""}
      </dl>
      <div class="kb-actions">
        ${k.url ? `<a href="${esc(safeUrl(k.url))}" target="_blank" rel="noopener">Official site ↗</a>` : ""}
        <button class="link" type="button" data-ask="${esc(k.title)}">Ask about this →</button>
        ${k.custom ? `<button class="link" type="button" data-del="${k.id}">Delete</button>` : ""}
      </div>
    </article>`).join("");
}
$("#kb-list").addEventListener("click", async (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.dataset.ask) {
    switchTab("advisor");
    $("#question").value = `Explain "${t.dataset.ask}" for my business: am I eligible, what exactly will I get, and what are the latest rules and steps to apply?`;
    $("#question").focus();
  } else if (t.dataset.del) {
    await api(`/api/knowledge/${t.dataset.del}`, { method: "DELETE" });
    loadKnowledge();
  }
});
let kbTimer;
$("#kb-search").addEventListener("input", () => { clearTimeout(kbTimer); kbTimer = setTimeout(loadKnowledge, 250); });
$("#kb-segment").addEventListener("change", loadKnowledge);
$("#kb-add-toggle").addEventListener("click", () => { $("#kb-form").hidden = !$("#kb-form").hidden; });
$("#kb-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/api/knowledge", { method: "POST", body: Object.fromEntries(new FormData(e.target)) });
    e.target.reset(); e.target.hidden = true; loadKnowledge();
  } catch (err) { window.console.error(err); $(".hint", e.target).textContent = `Could not save: ${err.message}`; }
});

// ---------------- history ----------------
async function loadHistory() {
  const pid = state.profile ? state.profile.id : "";
  const items = await api(`/api/history${pid ? `?profile_id=${pid}` : ""}`);
  const list = $("#history-list");
  list.innerHTML = "";
  if (!items.length) { list.innerHTML = `<p class="empty">No questions asked yet${state.profile ? ` for ${esc(state.profile.name)}` : ""}.</p>`; return; }
  items.forEach((it) => list.appendChild(answerCard(it, { deletable: true })));
}

// ---------------- dictionary (from dictionary/ folder) ----------------
const DICT_QUICK = ["GST", "Udyam", "MUDRA", "CAC", "MVP", "e-NAM", "GeM", "FPO", "DBT", "ZED"];
function renderDictQuick() {
  const box = $("#dict-quick");
  if (!box) return;
  box.innerHTML = "";
  DICT_QUICK.forEach((w) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "dict-cat"; b.textContent = w;
    b.setAttribute("aria-pressed", "false");
    b.onclick = () => { $("#dict-search").value = w; loadDictionary(); };
    box.appendChild(b);
  });
}
async function loadDictionary() {
  const q = $("#dict-search").value.trim();
  const cat = $("#dict-category").value;
  let items = [];
  try {
    items = await api(`/api/dictionary?q=${encodeURIComponent(q)}&category=${encodeURIComponent(cat)}`);
  } catch { items = []; }
  const list = $("#dict-list");
  if (!items.length) { list.innerHTML = `<p class="empty">No terms found. Try GST, mandi, loan, MVP…</p>`; return; }
  list.innerHTML = items.map((k, i) => `
    <article class="kb-card" style="animation-delay:${Math.min(i, 12) * 30}ms">
      <div class="kb-tags">
        <span class="tag">${esc(k.category || "")}</span>
        ${(k.related || []).slice(0, 2).map((r) => `<span class="tag">${esc(r)}</span>`).join("")}
      </div>
      <h4>${esc(k.term)}</h4>
      <p class="dict-meaning">${esc(k.meaning_simple || "")}</p>
      ${k.use_it ? `<p class="dict-use">${esc(k.use_it)}</p>` : ""}
      <div class="kb-actions">
        <button class="link" type="button" data-ask-term="${esc(k.term)}">Ask advisor →</button>
      </div>
    </article>`).join("");
}
let dictTimer;
$("#dict-search").addEventListener("input", () => { clearTimeout(dictTimer); dictTimer = setTimeout(loadDictionary, 250); });
$("#dict-category").addEventListener("change", loadDictionary);
$("#dict-list").addEventListener("click", (e) => {
  const t = e.target.closest("button[data-ask-term]");
  if (!t) return;
  switchTab("advisor");
  $("#question").value = `Explain "${t.dataset.askTerm}" in simple words for my business (${state.profile ? state.profile.business : state.segment}): what it means, whether I need it, and exact next steps.`;
  $("#question").focus();
});

// ---------------- startup toolkit (special startup features) ----------------
async function loadStartup() {
  let playbooks = [];
  try { playbooks = await api("/api/startup-toolkit"); } catch { playbooks = []; }
  const list = $("#startup-list");
  const cards = playbooks.map((p) => `
    <article class="tool-card">
      <h4>${esc(p.title)}</h4>
      <ol>${(p.steps || []).map((s) => `<li>${esc(s)}</li>`).join("")}</ol>
      <div class="form-actions">
        <button class="btn ink" type="button" data-playbook="${esc(p.prompt || p.title)}">Ask advisor →</button>
      </div>
    </article>`).join("");
  list.innerHTML = cards;
  renderCalculator();
}
$("#startup-list").addEventListener("click", (e) => {
  const t = e.target.closest("button[data-playbook]");
  if (!t) return;
  const fill = (s) => s
    .replace("{business}", (state.profile && state.profile.business) || state.segment)
    .replace("{stage}", (state.profile && state.profile.stage) || "idea")
    .replace("{location}", (state.profile && (state.profile.location + " " + state.profile.state)) || "India");
  switchTab("advisor");
  $("#question").value = fill(t.dataset.playbook);
  ask();
});

// ---------------- profit calculator ----------------
function calcNumbers() {
  const cost = Number($("#calc-cost").value || 0);
  const price = Number($("#calc-price").value || 0);
  const units = Number($("#calc-units").value || 0);
  const fixed = Number($("#calc-fixed").value || 0);
  const profitUnit = price - cost;
  const margin = price > 0 ? (profitUnit / price) * 100 : 0;
  const monthly = profitUnit * units - fixed;
  const breakeven = profitUnit > 0 ? Math.ceil(fixed / profitUnit) : Infinity;
  return { cost, price, units, fixed, profitUnit, margin, monthly, breakeven };
}
function renderCalculator() {
  const el = $("#calc-result");
  if (!el) return;
  const c = calcNumbers();
  const inr = (n) => "₹" + (isFinite(n) ? n.toLocaleString("en-IN", { maximumFractionDigits: 0 }) : "—");
  el.innerHTML = `Profit/unit <strong>${inr(c.profitUnit)}</strong> · Margin <strong>${c.margin.toFixed(1)}%</strong><br>
    Monthly profit <strong>${inr(c.monthly)}</strong> · Break-even <strong>${isFinite(c.breakeven) ? c.breakeven + " units" : "never at this price"}</strong>
    ${c.margin < 20 ? "<br>⚠️ Margin below 20% - raise price or cut cost before scaling." : ""}`;
}
["calc-cost", "calc-price", "calc-units", "calc-fixed"].forEach((id) =>
  document.getElementById(id).addEventListener("input", renderCalculator));
$("#calc-ask").addEventListener("click", () => {
  const c = calcNumbers();
  switchTab("advisor");
  $("#question").value = `My cost is ₹${c.cost}/unit, price ₹${c.price}, ${c.units} units/month, fixed cost ₹${c.fixed}. Margin is ${c.margin.toFixed(1)}%. Is this pricing right for my segment (${state.segment})? How do I improve profit without losing customers?`;
  ask();
});

// ---------------- tabs ----------------
function switchTab(name) {
  $$(".tab").forEach((t) => { const on = t.dataset.tab === name; t.classList.toggle("active", on); t.setAttribute("aria-selected", on); });
  $$(".panel").forEach((p) => { p.hidden = p.id !== `panel-${name}`; });
  document.querySelector(`.tab[data-tab="${name}"]`)?.scrollIntoView({ block: "nearest", inline: "nearest" });
  store.set("tab", name);
  if (name === "knowledge") loadKnowledge();
  if (name === "history") loadHistory();
  if (name === "dictionary") { renderDictQuick(); loadDictionary(); }
  if (name === "startup") loadStartup();
}
$$(".tab").forEach((t) => t.addEventListener("click", () => switchTab(t.dataset.tab)));

// ---------------- init ----------------
(async function init() {
  const segOptions = Object.entries(SEGMENT_LABELS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
  $("#kb-segment").insertAdjacentHTML("beforeend", segOptions);
  $("#kb-form-segment").insertAdjacentHTML("beforeend", segOptions);
  renderSegmentPicker();
  renderSuggestions();
  await Promise.all([loadStatus(), loadProfiles().catch(() => {})]);
  const tab = store.get("tab");
  if (tab && tab !== "advisor") switchTab(tab);
})();
