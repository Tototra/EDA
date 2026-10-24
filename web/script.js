const SETTINGS = { alpha: 0.3, k: 4 };
const GOAL = 3;
let last = null;
let votes = {};
let reached = false;
let people = [];

const $ = id => document.getElementById(id);

async function post(url, body) {
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json();
}

function screen(id) {
  for (const s of document.querySelectorAll(".screen")) s.hidden = s.id !== id;
  $("tab-discover").classList.toggle("active", id === "discover");
  $("tab-foryou").classList.toggle("active", id === "foryou");
  $("tab-personas").classList.toggle("active", id === "personas");
  window.scrollTo(0, 0);
}

function poster(f, size = "w185") {
  const img = f.poster ? `<img src="${f.poster.replace("w185", size)}" alt="${f.title}" loading="lazy">` : `<span>${f.title}</span>`;
  return `<div class="poster" title="${f.title} (${f.year})">${img}</div>`;
}

function rail(films) {
  return `<div class="rail">${films.map(f => poster(f)).join("")}</div>`;
}

function pick(t, i, label) {
  return `
    <section class="row">
      <div class="row-head"><h2>${label} n°${i + 1} · ${t.name}</h2></div>
      ${rail(t.films)}
    </section>`;
}

function progress(n) {
  $("progress").innerHTML = Array.from({ length: GOAL }, (_, i) => `<span class="${i < n ? "on" : ""}"></span>`).join("");
  $("hint").textContent = n < GOAL ? `Encore ${GOAL - n} univers à trouver` : "Tes univers sont prêts";
  $("tab-foryou").disabled = n === 0;
}

async function start() {
  reached = false;
  $("tab-discover").disabled = false;
  $("goal").hidden = false;
  show(await post("/api/start", { settings: SETTINGS }));
}

function show(data) {
  last = data;
  progress(data.liked);
  if (!data.proposals.length || (data.liked >= GOAL && !reached)) {
    reached = data.liked >= GOAL;
    return forYou();
  }
  discover();
}

function discover() {
  votes = {};
  $("rows").innerHTML = last.proposals.map(r => `
    <section class="row" id="row${r.id}">
      <div class="row-head">
        <h2>${r.name}</h2>
        <button class="pill yes" onclick="vote(${r.id}, 1)">J'aime</button>
        <button class="pill no" onclick="vote(${r.id}, -1)">Pas pour moi</button>
      </div>
      ${rail(r.films)}
    </section>`).join("") || `<p class="muted">Tu as vu tous les univers.</p>`;
  screen("discover");
}

function vote(id, v) {
  votes[id] = votes[id] === v ? 0 : v;
  $("row" + id).className = "row" + (votes[id] === 1 ? " liked" : votes[id] === -1 ? " disliked" : "");
}

async function next() {
  const liked = last.proposals.filter(r => votes[r.id] === 1).map(r => r.id);
  const passed = last.proposals.filter(r => votes[r.id] === -1).map(r => r.id);
  show(await post("/api/feedback", { liked, passed, settings: SETTINGS }));
}

async function forYou() {
  const top = await post("/api/best", {});
  const hero = top[0];
  $("hero-name").textContent = hero.name;
  $("hero-films").textContent = hero.films.slice(0, 4).map(f => f.title).join(" · ");
  $("hero-posters").innerHTML = hero.films.slice(0, 3).map(f => poster(f, "w342")).join("");
  const backdrop = hero.films.find(f => f.poster);
  $("hero").style.setProperty("--bg", backdrop ? `url(${backdrop.poster.replace("w185", "w342")})` : "none");
  $("picks").innerHTML = top.map((t, i) => pick(t, i, "Ton univers")).join("");
  screen("foryou");
}

async function personas() {
  people = await (await fetch("/api/personas")).json();
  $("persona-rows").innerHTML = people.map(p => `
    <section class="row">
      <div class="row-head">
        <h2>${p.name}</h2>
        <button class="pill" onclick="play(${p.id})">Voir sa partie</button>
      </div>
      ${rail(p.films)}
    </section>`).join("");
  $("persona-list").hidden = false;
  $("persona-game").hidden = true;
  screen("personas");
}

function verdict(r) {
  return `
    <section class="row ${r.liked ? "liked" : "disliked"}">
      <div class="row-head">
        <h2>${r.name}</h2>
        <span class="pill ${r.liked ? "yes" : "no"}">${r.liked ? "J'aime" : "Pas pour moi"}</span>
      </div>
      ${rail(r.films)}
    </section>`;
}

async function play(n) {
  const data = await post(`/api/persona/${n}`, {});
  $("persona-name").textContent = people[n].name;
  $("persona-rounds").innerHTML =
    data.rounds.map((t, i) => `<h2 class="round">Tour ${i + 1}</h2>${t.map(verdict).join("")}`).join("") +
    `<h2 class="round">Pour ${people[n].name.split(",")[0]}</h2>${data.best.map((t, i) => pick(t, i, "Univers")).join("")}`;
  $("persona-list").hidden = true;
  $("persona-game").hidden = false;
  window.scrollTo(0, 0);
}

fetch("/api/wall").then(r => r.json()).then(urls => {
  $("wall").innerHTML = urls.map(u => `<img src="${u}" alt="">`).join("");
});

$("start").onclick = start;
$("next").onclick = next;
$("refine").onclick = () => { reached = last.liked >= GOAL; discover(); };
$("tab-discover").onclick = () => { reached = last.liked >= GOAL; discover(); };
$("tab-foryou").onclick = forYou;
$("tab-personas").onclick = personas;
$("persona-back").onclick = personas;
$("logo").onclick = () => { $("goal").hidden = true; screen("intro"); };
