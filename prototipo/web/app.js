/* ArtNotes — prototipo Fase 2.5.
 * Legge solo la scheda composta (api/opere/<id>.json): nessuna dipendenza
 * dalla struttura interna dei dati o delle fonti.
 *
 * Parametri dell'indirizzo:
 *   vista=redazione|pubblico   (compatibile con il vecchio modo=pubblico)
 *   percorso=curioso|studio|ispirazione|libera
 *   tappa=<id tappa>
 *   #aNN                        dettaglio selezionato
 */
"use strict";

const REGISTRI = {
  documentato: { etichetta: "Documentato", segno: "■" },
  interpretazione: { etichetta: "Interpretazione", segno: "◆" },
  osservazione: { etichetta: "Osservazione", segno: "●" },
  ipotesi: { etichetta: "Ipotesi", segno: "▲" },
  lacuna: { etichetta: "Lacuna", segno: "○" },
};
const CATEGORIE = {
  osservazione: "Osservazione guidata",
  iconografia: "Iconografia",
  composizione: "Composizione",
  tecnica: "Tecnica",
};
const TIPI_CONNESSIONE = {
  documentata: { etichetta: "Connessione documentata", segno: "■", spiega: "rapporto registrato da una fonte" },
  interpretativa: { etichetta: "Connessione interpretativa", segno: "◆", spiega: "somiglianza argomentata, non prova storica" },
  algoritmica: { etichetta: "Connessione calcolata", segno: "≈", spiega: "calcolata dai dati, non dallo sguardo" },
};
const PERCORSI = ["curioso", "studio", "ispirazione"];
const ETICHETTE_PERCORSO = { curioso: "Sono curioso", studio: "Voglio approfondire", ispirazione: "Cerco ispirazione", libera: "Esplora liberamente" };
const NOMI_COMPONENTI = {
  pertinenza: "Pertinenza all'opera", qualita: "Affidabilità della fonte", intento: "Adatto al percorso",
  diversita: "Varietà dei canali", freschezza: "Data di pubblicazione", interesse: "Popolarità",
};
const LINGUE = { it: "italiano", en: "inglese", fr: "francese", de: "tedesco", es: "spagnolo", nl: "olandese", ru: "russo", zxx: "senza parlato" };
const LIVELLI_INIZIALI = new Set(["osservazione"]);

const stato = {
  scheda: null,
  viewer: null,
  overlay: new Map(),   // id annotazione -> elemento
  selezionata: null,
  livelliAttivi: new Set(LIVELLI_INIZIALI),
  sezione: null,
  vista: "redazione",
  percorso: null,       // null = scelta iniziale
  tappaPer: {},         // percorso -> id tappa corrente
  rivelate: new Set(),  // "percorso:tappa" già rivelate
  scelte: {},           // "percorso:tappa" -> annotazione scelta
  ordinePulse: null,
};

const $ = (s) => document.querySelector(s);
const el = (tag, attrs = {}, ...figli) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const f of figli.flat()) if (f !== null && f !== undefined && f !== false) n.append(f.nodeType ? f : String(f));
  return n;
};

const movimentoRidotto = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const animazioniAttive = () => $("#animazioni").checked;

function dataIt(iso) {
  if (!iso) return "";
  const [a, m, g] = iso.slice(0, 10).split("-");
  return `${g}/${m}/${a}`;
}
function durata(s) {
  if (s === null || s === undefined) return null;
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = String(s % 60).padStart(2, "0");
  return h ? `${h}:${String(m).padStart(2, "0")}:${x}` : `${m}:${x}`;
}
const lingua = (c) => (c ? LINGUE[c.split("-")[0]] || c : null);
const annuncia = (t) => { $("#annuncio").textContent = ""; setTimeout(() => { $("#annuncio").textContent = t; }, 30); };

/* ---------- taccuino locale ---------- */

const chiaveTaccuino = () => `artnotes:taccuino:${stato.scheda.opera.id}`;
function leggiTaccuino() {
  try {
    const t = JSON.parse(localStorage.getItem(chiaveTaccuino()) || "null");
    if (t && Array.isArray(t.voci) && t.note) return t;
  } catch { /* archiviazione non disponibile */ }
  return { voci: [], note: {} };
}
function scriviTaccuino(t) {
  try { localStorage.setItem(chiaveTaccuino(), JSON.stringify(t)); return true; } catch { return false; }
}
function aggiungiAlTaccuino(voce, bottone) {
  const t = leggiTaccuino();
  if (!t.voci.some((v) => v.tipo === voce.tipo && v.id === voce.id)) t.voci.push({ ...voce, aggiunto_il: new Date().toISOString() });
  const ok = scriviTaccuino(t);
  if (bottone) {
    bottone.textContent = ok ? "Nel taccuino ✓" : "Taccuino non disponibile in questo browser";
    bottone.disabled = true;
  }
  annuncia(ok ? `«${voce.titolo}» aggiunto al taccuino.` : "Il taccuino non è disponibile in questo browser.");
}
const nelTaccuino = (tipo, id) => leggiTaccuino().voci.some((v) => v.tipo === tipo && v.id === id);
function bottoneTaccuino(voce) {
  const gia = nelTaccuino(voce.tipo, voce.id);
  const b = el("button", { type: "button", class: "secondario", disabled: gia }, gia ? "Nel taccuino ✓" : "Aggiungi al taccuino");
  b.addEventListener("click", () => aggiungiAlTaccuino(voce, b));
  return b;
}

/* ---------- avvio ---------- */

async function avvia() {
  const parametri = new URLSearchParams(location.search);
  const id = parametri.get("opera") || "435809";
  stato.vista = parametri.get("vista") === "pubblico" || parametri.get("modo") === "pubblico" ? "pubblico" : "redazione";
  const pubblico = stato.vista === "pubblico";
  const p = parametri.get("percorso");
  stato.percorso = PERCORSI.includes(p) || p === "libera" ? p : null;
  if (PERCORSI.includes(p) && parametri.get("tappa")) stato.tappaPer[p] = parametri.get("tappa");
  $("#animazioni").checked = !movimentoRidotto();

  let scheda;
  try {
    const r = await fetch(`api/opere/${encodeURIComponent(id)}${pubblico ? ".pubblico" : ""}.json`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    scheda = await r.json();
  } catch (e) {
    $("#titolo").textContent = "Scheda non disponibile";
    $("#sottotitolo").textContent = `Impossibile caricare la scheda (${e.message}). Avvia il server locale dalla cartella web.`;
    return;
  }
  stato.scheda = scheda;
  scheda.percorsi ??= [];
  scheda.connessioni ??= [];
  scheda.pulse ??= { contenuti: [], selezioni: {}, conteggi: {}, stato_fonte: "assente", politica: "" };
  if (stato.percorso && stato.percorso !== "libera" && !percorsoDati(stato.percorso)) stato.percorso = null;

  intestazione(scheda);
  banner(scheda);
  copertura(scheda);
  visualizzatore(scheda);
  livelli(scheda);
  elenco(scheda);
  schede(scheda);
  commutatore();
  renderPercorso();

  const daHash = location.hash.slice(1);
  if (daHash && scheda.annotazioni.some((a) => a.id === daHash)) seleziona(daHash, { daUrl: true });
}

function aggiornaUrl() {
  const q = new URLSearchParams(location.search);
  q.delete("modo");
  if (stato.vista === "pubblico") q.set("vista", "pubblico"); else q.delete("vista");
  if (stato.percorso) q.set("percorso", stato.percorso); else q.delete("percorso");
  const t = PERCORSI.includes(stato.percorso) ? tappaCorrente()?.id : null;
  if (t) q.set("tappa", t); else q.delete("tappa");
  const s = q.toString();
  history.replaceState(null, "", location.pathname + (s ? `?${s}` : "") + location.hash);
}

function intestazione(s) {
  const c = s.opera.catalogo;
  const evid = c.attribuzioni.find((a) => a.fonte === c.attribuzione_in_evidenza.fonte) || c.attribuzioni[0];
  const titoloIt = c.titoli.find((t) => t.lingua === "it");
  const titoloOrig = c.titoli.find((t) => t.fonte === c.attribuzione_in_evidenza.fonte) || c.titoli[0];
  $("#titolo").textContent = titoloOrig.valore;
  const data = c.datazioni[0]?.testo_originale || "data non indicata";
  $("#sottotitolo").textContent =
    `${evid.qualifica_originale ? evid.qualifica_originale + " " : ""}${evid.autore} · ${data}` +
    (titoloIt?.valore ? ` · titolo italiano (Wikidata): «${titoloIt.valore}»` : "");
  document.title = `${titoloOrig.valore} — ArtNotes`;
}

function banner(s) {
  const b = $("#banner");
  if (s.modalita === "anteprima_redazionale") {
    b.textContent =
      "Anteprima redazionale: testi, regioni, percorsi e suggerimenti sono bozze generate da AI e non revisionate. Non sono visibili in modalità pubblica.";
  } else if (!s.annotazioni.length && s.sezioni.every((x) => !x.blocchi.length)) {
    b.textContent = "Modalità pubblica: per quest'opera non ci sono ancora contenuti pubblicati. Sono visibili solo i dati di catalogo.";
  }
}

function copertura(s) {
  const dl = $("#copertura");
  const voci = [
    ["Dati di catalogo", s.copertura.catalogo],
    ["Approfondimenti documentati", s.copertura.approfondimenti_documentati],
    ["Annotazioni interattive", s.copertura.annotazioni],
    ["Revisione umana", s.copertura.revisione_umana],
  ];
  for (const [k, v] of voci) dl.append(el("dt", {}, k), el("dd", {}, v));
}

/* ---------- visualizzatore ---------- */

function visualizzatore(s) {
  const img = s.immagine;
  $("#visore").setAttribute(
    "aria-label",
    `Immagine esplorabile: ${s.opera.catalogo.titoli[0].valore}. Fotografia ${img.file_fotografia}. ` +
      "Usa i comandi sopra per lo zoom e l'elenco dei dettagli sotto per raggiungere le regioni."
  );
  $("#info-immagine").textContent =
    `Fotografia ${img.file_fotografia} · ${img.larghezza} × ${img.altezza} px · ${img.a_colori ? "a colori" : "in bianco e nero"} · ` +
    `${img.vista} · ${img.crediti}. Lo zoom si ferma alla risoluzione della fotografia: nessun dettaglio è ricostruito.`;

  const viewer = OpenSeadragon({
    element: $("#visore"),
    tileSources: img.dzi,
    showNavigationControl: false,
    showNavigator: true,
    navigatorPosition: "BOTTOM_RIGHT",
    maxZoomPixelRatio: 1.5,
    visibilityRatio: 0.8,
    animationTime: animazioniAttive() ? 0.9 : 0,
    springStiffness: 8,
    gestureSettingsMouse: { clickToZoom: false, dblClickToZoom: true },
    gestureSettingsTouch: { pinchRotate: false },
  });
  stato.viewer = viewer;

  const aspetto = img.altezza / img.larghezza;
  viewer.addHandler("open", () => {
    for (const a of s.annotazioni) {
      const r = a.regione_normalizzata;
      const nodo = el(
        "div",
        {
          class: `regione cat-${a.categoria}${a.verifica_immagine === "da_riverificare" ? " da-riverificare" : ""}`,
          "aria-hidden": "true",
          title: a.titolo,
        },
        el("span", { class: "etichetta-regione" }, a.titolo)
      );
      viewer.addOverlay({
        element: nodo,
        location: new OpenSeadragon.Rect(r.x, r.y * aspetto, r.w, r.h * aspetto),
      });
      new OpenSeadragon.MouseTracker({
        element: nodo,
        clickHandler: (e) => {
          if (e.quick) seleziona(a.id);
        },
      });
      stato.overlay.set(a.id, nodo);
    }
    aggiornaVisibilita();
    if (stato.selezionata) evidenzia(stato.selezionata);
  });

  $("#zoom-piu").addEventListener("click", () => zoom(1.6));
  $("#zoom-meno").addEventListener("click", () => zoom(1 / 1.6));
  $("#adatta").addEventListener("click", () => viewer.viewport.goHome(!animazioniAttive()));
  $("#schermo").addEventListener("click", () => viewer.setFullScreen(!viewer.isFullPage()));
  $("#animazioni").addEventListener("change", () => {
    viewer.animationTime = animazioniAttive() ? 0.9 : 0;
  });
}

function zoom(f) {
  const v = stato.viewer.viewport;
  v.zoomBy(f);
  v.applyConstraints(!animazioniAttive());
  if (!animazioniAttive()) v.update?.();
}

function inquadra(a) {
  const img = stato.scheda.immagine;
  const aspetto = img.altezza / img.larghezza;
  const r = a.regione_normalizzata;
  const margine = Math.max(r.w, r.h * aspetto) * 0.35;
  const rett = new OpenSeadragon.Rect(
    r.x - margine, r.y * aspetto - margine, r.w + 2 * margine, r.h * aspetto + 2 * margine
  );
  stato.viewer.viewport.fitBounds(rett, !animazioniAttive());
}

/* ---------- livelli ed elenco ---------- */

function livelli(s) {
  const contenitore = $("#livelli");
  for (const [cat, nome] of Object.entries(CATEGORIE)) {
    const n = s.annotazioni.filter((a) => a.categoria === cat).length;
    const box = el("input", {
      type: "checkbox",
      value: cat,
      checked: stato.livelliAttivi.has(cat),
      onchange: (e) => {
        e.target.checked ? stato.livelliAttivi.add(cat) : stato.livelliAttivi.delete(cat);
        aggiornaVisibilita();
      },
    });
    contenitore.append(
      el("label", { class: `cat-${cat}` }, box, el("span", { class: "campione", "aria-hidden": "true" }), `${nome} (${n})`)
    );
  }
}

function elenco(s) {
  const ol = $("#elenco");
  if (!s.annotazioni.length) {
    ol.append(el("li", { class: "vuoto" }, "Nessun dettaglio disponibile."));
  }
  for (const a of s.annotazioni) {
    ol.append(
      el(
        "li",
        { "data-id": a.id, "data-cat": a.categoria },
        el(
          "button",
          { type: "button", onclick: () => seleziona(a.id) },
          el("span", { class: `campione cat-${a.categoria}`, "aria-hidden": "true" }),
          el("span", {}, a.titolo, el("span", { class: "cat-testo" }, CATEGORIE[a.categoria]))
        )
      )
    );
  }
  aggiornaVisibilita();
}

function aggiornaVisibilita() {
  let visibili = 0;
  for (const a of stato.scheda.annotazioni) {
    const attiva = stato.livelliAttivi.has(a.categoria) || stato.selezionata === a.id;
    stato.overlay.get(a.id)?.classList.toggle("nascosta", !attiva);
    const li = document.querySelector(`#elenco li[data-id="${a.id}"]`);
    li?.classList.toggle("nascosta", !stato.livelliAttivi.has(a.categoria));
    if (stato.livelliAttivi.has(a.categoria)) visibili++;
  }
  $("#conteggio").textContent = `(${visibili} di ${stato.scheda.annotazioni.length})`;
}

/* ---------- selezione ---------- */

const annotazione = (id) => stato.scheda.annotazioni.find((x) => x.id === id);

function attivaRegione(a, { daUrl = false } = {}) {
  stato.selezionata = a.id;
  if (!stato.livelliAttivi.has(a.categoria)) {
    stato.livelliAttivi.add(a.categoria);
    const box = document.querySelector(`#livelli input[value="${a.categoria}"]`);
    if (box) box.checked = true;
  }
  aggiornaVisibilita();
  evidenzia(a.id);
  if (stato.viewer?.world.getItemCount()) inquadra(a);
  else stato.viewer?.addOnceHandler("open", () => inquadra(a));
  if (!daUrl) history.replaceState(null, "", `${location.pathname}${location.search}#${a.id}`);
}

function seleziona(id, { daUrl = false } = {}) {
  const a = annotazione(id);
  if (!a) return;
  attivaRegione(a, { daUrl });
  mostraDettaglio(a);
}

/* Inquadra ed evidenzia una regione senza aprire la scheda di dettaglio:
 * usata dai percorsi, che mostrano i testi nella tappa. */
function mostraRegione(id) {
  const a = annotazione(id);
  if (!a) return;
  $("#dettaglio").hidden = true;
  attivaRegione(a);
  if (window.innerWidth <= 900) $("#visore").scrollIntoView({ behavior: animazioniAttive() ? "smooth" : "auto", block: "center" });
}

function evidenzia(id) {
  for (const [k, nodo] of stato.overlay) nodo.classList.toggle("selezionata", k === id);
  document.querySelectorAll("#elenco button").forEach((b) => b.removeAttribute("aria-current"));
  document.querySelector(`#elenco li[data-id="${id}"] button`)?.setAttribute("aria-current", "true");
}

function deseleziona() {
  const precedente = stato.selezionata;
  stato.selezionata = null;
  for (const nodo of stato.overlay.values()) nodo.classList.remove("selezionata");
  document.querySelectorAll("#elenco button").forEach((b) => b.removeAttribute("aria-current"));
  $("#dettaglio").hidden = true;
  aggiornaVisibilita();
  stato.viewer.viewport.goHome(!animazioniAttive());
  history.replaceState(null, "", location.pathname + location.search);
  // Il focus torna al dettaglio da cui si era partiti, se è nell'elenco visibile.
  const voce = document.querySelector(`#elenco li[data-id="${precedente}"]:not(.nascosta) button`);
  (voce || $("#pannello")).focus();
}

function mostraDettaglio(a) {
  const d = $("#dettaglio");
  d.replaceChildren();
  d.append(
    el("p", { class: "meta" }, `${CATEGORIE[a.categoria]} · dettaglio ${a.id}`),
    el("h2", { id: "titolo-dettaglio", tabindex: "-1" }, a.titolo)
  );
  if (a.domanda) d.append(el("p", { class: "domanda" }, a.domanda));
  if (a.verifica_immagine === "da_riverificare") {
    d.append(
      el("p", { class: "avviso" },
        "Regione da riverificare: è stata tracciata su un'altra versione dell'immagine e potrebbe non corrispondere.")
    );
  }
  for (const b of a.blocchi) d.append(blocco(b, a.origine, a.stato, a.revisione));

  const collegati = (a.collegamenti || []).map(annotazione).filter(Boolean);
  if (collegati.length) {
    d.append(
      el("p", { class: "meta" }, "Dettagli collegati:"),
      el("div", {}, collegati.map((c) => el("button", { type: "button", class: "collegamento", onclick: () => seleziona(c.id) }, c.titolo)))
    );
  }
  // Contenuti esterni collegati: dopo il testo, senza coprirlo.
  const esterni = esterniPerRegione(a.id);
  if (esterni.length) {
    d.append(
      el("details", { class: "esterni-regione" },
        el("summary", {}, `Approfondisci su YouTube (${esterni.length}, contenuti esterni)`),
        el("ul", {}, esterni.map(({ v, motivo }) =>
          el("li", {},
            linkEsterno(v),
            el("span", { class: "meta" }, ` · ${v.canale} · ${v.relazione_testo}. Collegamento: ${motivo}.`)))))
    );
  }
  d.append(
    el("div", { class: "azioni" },
      el("button", {
        type: "button",
        onclick: () => {
          $("#visore").scrollIntoView({ behavior: animazioniAttive() ? "smooth" : "auto", block: "center" });
          inquadra(a);
        },
      }, "Mostra sull'immagine"),
      bottoneTaccuino({ tipo: "dettaglio", id: a.id, titolo: a.titolo }),
      el("button", { type: "button", onclick: deseleziona }, "Chiudi e torna all'opera intera"))
  );
  d.hidden = false;
  $("#titolo-dettaglio").focus({ preventScroll: window.innerWidth > 900 });
}

/* ---------- blocchi testuali ---------- */

function descriviFonte(rif) {
  const f = stato.scheda.fonti[rif.fonte];
  if (!f) return rif.fonte;
  const parti = [f.titolo];
  if (rif.campi?.length) parti.push(`campi: ${rif.campi.join(", ")}`);
  if (rif.nota) parti.push(rif.nota);
  return parti.join(" — ");
}

function righeFonti(fonti) {
  const out = [];
  (fonti || []).forEach((r, i) => {
    const f = stato.scheda.fonti[r.fonte];
    if (i) out.push("; ");
    out.push(el("span", {}, f?.url ? el("a", { href: f.url, target: "_blank", rel: "noopener" }, descriviFonte(r)) : descriviFonte(r)));
  });
  return out;
}

function riga_origine(origine, statoTesto, revisione) {
  const stati = { bozza: "Bozza", in_revisione: "In revisione", pubblicato: "Pubblicato", da_aggiornare: "Da aggiornare" };
  return el(
    "p",
    { class: "meta" },
    origine?.tipo === "ai" ? `Testo generato da AI (${origine.modello}), ${dataIt(origine.data)}` : "Testo redazionale",
    ` · ${stati[statoTesto] || "stato non indicato"} · `,
    revisione ? `Revisionato da ${revisione.revisore}, ${dataIt(revisione.data)}` : "Non revisionato"
  );
}

function blocco(b, origineDefault, statoDefault, revisioneDefault) {
  const reg = REGISTRI[b.registro];
  const fonti = righeFonti(b.fonti);
  return el(
    "div",
    { class: `blocco reg-${b.registro}` },
    el("span", { class: "badge" }, el("span", { "aria-hidden": "true" }, reg.segno), reg.etichetta),
    el("p", {}, b.testo),
    fonti.length ? el("p", { class: "meta" }, "Base: ", ...fonti) : null,
    riga_origine(b.origine || origineDefault, b.stato || statoDefault, b.revisione ?? revisioneDefault)
  );
}

function bloccoPerId(id) {
  for (const s of stato.scheda.sezioni) {
    const b = s.blocchi.find((x) => x.id === id);
    if (b) return b;
  }
  return null;
}

/* ---------- percorsi ---------- */

const percorsoDati = (id) => stato.scheda.percorsi.find((p) => p.id === id);
function tappaCorrente() {
  const p = percorsoDati(stato.percorso);
  if (!p) return null;
  return p.tappe.find((t) => t.id === stato.tappaPer[p.id]) || p.tappe[0];
}

function commutatore() {
  const nav = $("#commutatore");
  nav.replaceChildren();
  if (!stato.scheda.percorsi.length) { nav.hidden = true; return; }
  nav.hidden = false;
  nav.append(el("span", { class: "etichetta-commutatore", id: "etichetta-commutatore" }, "Percorso:"));
  for (const id of [...PERCORSI.filter(percorsoDati), "libera"]) {
    nav.append(el("button", {
      type: "button",
      "data-percorso": id,
      "aria-pressed": String(stato.percorso === id),
      onclick: () => cambiaPercorso(id),
    }, ETICHETTE_PERCORSO[id]));
  }
}

/* Cambiare percorso non tocca immagine, zoom né dettaglio selezionato (UX-02). */
function cambiaPercorso(id) {
  stato.percorso = id;
  document.querySelectorAll("#commutatore button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.percorso === id)));
  renderPercorso();
  aggiornaUrl();
  if (stato.sezione === "pulse") apriSezione("pulse");
  const t = tappaCorrente();
  annuncia(id === "libera" ? "Esplorazione libera." :
    `Percorso ${ETICHETTE_PERCORSO[id]}: tappa ${percorsoDati(id).tappe.indexOf(t) + 1} di ${percorsoDati(id).tappe.length}, ${t.titolo}.`);
}

function vaiATappa(id, { focus = true } = {}) {
  stato.tappaPer[stato.percorso] = id;
  renderPercorso();
  aggiornaUrl();
  if (focus) $("#titolo-percorso")?.focus();
}

function renderPercorso() {
  const box = $("#percorso");
  box.replaceChildren();
  box.hidden = false;
  if (stato.percorso === "libera") { box.hidden = true; return; }
  if (!stato.scheda.percorsi.length) {
    box.append(
      el("h2", { id: "titolo-percorso", tabindex: "-1" }, "Che cosa vuoi scoprire oggi?"),
      el("p", { class: "vuoto" }, stato.vista === "pubblico"
        ? "In modalità pubblica non ci sono ancora percorsi pubblicati per quest'opera. Puoi esplorare l'immagine e i dati di catalogo."
        : "Per quest'opera non ci sono ancora percorsi.")
    );
    return;
  }
  if (!stato.percorso) return sceltaIniziale(box);

  const p = percorsoDati(stato.percorso);
  const t = tappaCorrente();
  const i = p.tappe.indexOf(t);
  box.append(
    el("p", { class: "meta" }, `${p.titolo} · ${p.durata} · tappa ${i + 1} di ${p.tappe.length}`),
    el("h2", { id: "titolo-percorso", tabindex: "-1" }, t.titolo),
    el("ol", { class: "tappe-elenco", "aria-label": "Tappe del percorso" },
      p.tappe.map((x, j) => el("li", {},
        el("button", {
          type: "button",
          "aria-current": x.id === t.id ? "step" : null,
          onclick: () => vaiATappa(x.id),
        }, `${j + 1}. ${x.titolo}`))))
  );
  const corpo = el("div", { class: "tappa" });
  if (t.raccordo && !["scelta"].includes(t.tipo)) corpo.append(el("p", { class: "raccordo" }, t.raccordo));
  ({ scelta: tappaScelta, scopri: tappaScopri, scrivi: tappaScrivi, leggi: tappaLeggi, evidenze: tappaEvidenze,
     connessioni: tappaConnessioni, pulse: tappaPulse, rielabora: tappaRielabora })[t.tipo](corpo, t, p);
  box.append(corpo);

  const nav = el("div", { class: "navigazione-tappe" });
  if (i > 0) nav.append(el("button", { type: "button", onclick: () => vaiATappa(p.tappe[i - 1].id) }, "← Indietro"));
  if (i < p.tappe.length - 1) nav.append(el("button", { type: "button", class: "primario", onclick: () => vaiATappa(p.tappe[i + 1].id) }, "Avanti →"));
  else nav.append(...PERCORSI.filter((x) => x !== p.id && percorsoDati(x)).map((x) =>
    el("button", { type: "button", onclick: () => cambiaPercorso(x) }, `Prova: ${ETICHETTE_PERCORSO[x]}`)));
  box.append(nav, el("p", { class: "meta" },
    p.origine?.tipo === "ai" ? `Percorso proposto dall'AI (${p.origine.modello}), ${dataIt(p.origine.data)}` : "Percorso redazionale",
    ` · ${p.stato === "pubblicato" ? "Pubblicato" : "Bozza, non revisionato"}. Il percorso cambia l'ordine e le domande, non i contenuti.`));
}

function sceltaIniziale(box) {
  box.append(
    el("h2", { id: "titolo-percorso", tabindex: "-1" }, "Che cosa vuoi scoprire oggi?"),
    el("div", { class: "scelte-percorso" },
      PERCORSI.filter(percorsoDati).map((id) => {
        const p = percorsoDati(id);
        return el("button", { type: "button", class: "scelta-percorso", onclick: () => cambiaPercorso(id) },
          el("strong", {}, p.titolo), el("span", {}, `«${p.invito}»`), el("span", { class: "meta" }, `${p.tappe.length} tappe · ${p.durata}`));
      })),
    el("p", { class: "meta" },
      "Puoi cambiare percorso in qualsiasi momento: l'immagine, lo zoom e il dettaglio scelto restano dove sono. ",
      el("button", { type: "button", class: "collegamento", onclick: () => cambiaPercorso("libera") }, "Esplora liberamente"))
  );
}

function rivelata(t) { return stato.rivelate.has(`${stato.percorso}:${t.id}`); }
function rivela(t) { stato.rivelate.add(`${stato.percorso}:${t.id}`); }

function testiAnnotazione(a) {
  return [
    ...a.blocchi.map((b) => blocco(b, a.origine, a.stato, a.revisione)),
    ...(a.verifica_immagine === "da_riverificare"
      ? [el("p", { class: "avviso" }, "Regione da riverificare sull'immagine attuale.")] : []),
  ];
}

function tappaScelta(corpo, t) {
  const chiave = `${stato.percorso}:${t.id}`;
  corpo.append(el("p", { class: "domanda" }, t.domanda));
  const gruppo = el("div", { class: "scelte", role: "group", "aria-label": t.domanda });
  for (const id of t.scelte) {
    const a = annotazione(id);
    if (!a) continue;
    gruppo.append(el("button", {
      type: "button",
      "aria-pressed": String(stato.scelte[chiave] === id),
      onclick: () => {
        stato.scelte[chiave] = id;
        rivela(t);
        mostraRegione(id);
        renderPercorso();
        $("#esito-scelta")?.focus();
      },
    }, a.titolo));
  }
  corpo.append(gruppo);
  if (rivelata(t)) {
    const scelta = annotazione(stato.scelte[chiave]);
    corpo.append(
      el("p", { class: "raccordo", id: "esito-scelta", tabindex: "-1" },
        scelta ? `Hai scelto: ${scelta.titolo}. ` : "", t.raccordo || ""),
      ...(t.blocchi || []).map(bloccoPerId).filter(Boolean).map((b) => blocco(b, b.origine, b.stato, b.revisione))
    );
  }
}

function tappaScopri(corpo, t) {
  const a = annotazione(t.annotazione);
  if (!a) return corpo.append(el("p", { class: "vuoto" }, "Dettaglio non disponibile."));
  corpo.append(el("p", { class: "domanda" }, t.domanda || a.domanda || `Cerca sull'immagine: ${a.titolo}.`));
  if (!rivelata(t)) {
    corpo.append(
      el("p", { class: "meta" }, "Cerca sull'immagine con lo zoom, poi controlla."),
      el("button", { type: "button", class: "primario", onclick: () => { rivela(t); mostraRegione(a.id); renderPercorso(); $("#esito-scopri")?.focus(); } },
        "Mostra dov'è e che cosa dicono le fonti")
    );
    return;
  }
  corpo.append(
    el("p", { class: "meta", id: "esito-scopri", tabindex: "-1" }, `Dettaglio ${a.id} · ${CATEGORIE[a.categoria]}`),
    ...testiAnnotazione(a),
    el("div", { class: "azioni" },
      el("button", { type: "button", onclick: () => mostraRegione(a.id) }, "Inquadra di nuovo"),
      bottoneTaccuino({ tipo: "dettaglio", id: a.id, titolo: a.titolo })),
    elencoEsterniRegione(a.id)
  );
}

function areaNota(t) {
  const id = `nota-${stato.percorso}-${t.nota}`;
  const area = el("textarea", { id, rows: "5" });
  area.value = leggiTaccuino().note[t.nota] || "";
  let timer;
  area.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const tac = leggiTaccuino();
      tac.note[t.nota] = area.value;
      const ok = scriviTaccuino(tac);
      $(`#${id}-stato`).textContent = ok ? "Salvata in questo browser." : "Questo browser non permette di salvare la nota.";
    }, 400);
  });
  return el("div", { class: "campo-nota" },
    el("label", { for: id }, t.consegna),
    area,
    el("p", { class: "meta", id: `${id}-stato`, "aria-live": "polite" },
      "La nota resta solo in questo browser: non viene inviata a nessuno. Puoi scaricarla o cancellarla dal taccuino."));
}

function tappaScrivi(corpo, t) {
  const a = t.annotazione ? annotazione(t.annotazione) : null;
  if (a) corpo.append(el("div", { class: "azioni" },
    el("button", { type: "button", onclick: () => mostraRegione(a.id) }, `Mostra la zona: ${a.titolo}`)));
  corpo.append(areaNota(t));
  if (a && t.rivela) {
    if (!rivelata(t)) {
      corpo.append(el("button", { type: "button", class: "primario", onclick: () => { rivela(t); renderPercorso(); $("#esito-scrivi")?.focus(); } },
        "Confronta con l'osservazione di ArtNotes"));
    } else {
      corpo.append(el("p", { class: "meta", id: "esito-scrivi", tabindex: "-1" },
        "L'osservazione di ArtNotes su questa zona. Non è «la risposta giusta»: confrontala con la tua."), ...testiAnnotazione(a));
    }
  }
}

function tappaLeggi(corpo, t) {
  for (const b of (t.blocchi || []).map(bloccoPerId).filter(Boolean)) corpo.append(blocco(b, b.origine, b.stato, b.revisione));
  if (t.pulse_categoria) {
    const lista = selezionePulse(stato.percorso).filter((v) => v.categoria === t.pulse_categoria).slice(0, 3);
    if (lista.length) corpo.append(el("p", { class: "raccordo" }, t.raccordo_pulse || ""), ...lista.map((v) => schedaEsterno(v)));
  }
}

/* Nome breve della fonte per tabelle compatte; la citazione completa resta nel titolo del link. */
function fontiBrevi(fonti) {
  const out = [];
  (fonti || []).forEach((r, i) => {
    const f = stato.scheda.fonti[r.fonte];
    const breve = r.fonte.startsWith("met-") ? "Met (scheda)"
      : r.fonte.startsWith("foto-") ? "Fotografia del Met"
      : r.fonte.startsWith("wikidata-") ? `Wikidata ${r.fonte.slice(9)}`
      : r.fonte.startsWith("commons-") ? "Commons" : (f?.titolo.split(",")[0] || r.fonte);
    const nota = /senza riferimenti/.test(r.nota || "") ? " (senza riferimenti)" : "";
    if (i) out.push("; ");
    out.push(f?.url ? el("a", { href: f.url, target: "_blank", rel: "noopener", title: descriviFonte(r) }, breve) : breve, nota);
  });
  return out;
}

function tappaEvidenze(corpo, t) {
  const tab = el("table", { class: "tabella evidenze" },
    el("caption", { class: "meta", style: "text-align:left" }, "Mappa delle evidenze: affermazione → fonte → dettaglio → grado di certezza"),
    el("thead", {}, el("tr", {}, ["Affermazione", "Registro", "Base", "Dettaglio", "Certezza"].map((x) => el("th", { scope: "col" }, x)))),
    el("tbody", {}, (t.righe_risolte || []).map((r) => {
      const reg = REGISTRI[r.registro];
      const fonti = fontiBrevi(r.fonti);
      return el("tr", {},
        el("td", { "data-col": "Affermazione" }, r.titolo ? el("strong", {}, `${r.titolo}: `) : null, r.testo.length > 170 ? r.testo.slice(0, 167) + "…" : r.testo),
        el("td", { "data-col": "Registro" }, el("span", { class: `badge reg-${r.registro}` }, el("span", { "aria-hidden": "true" }, reg.segno), reg.etichetta)),
        el("td", { "data-col": "Base", class: "meta" }, fonti.length ? fonti : "nessuna fonte"),
        el("td", { "data-col": "Dettaglio" }, r.dettaglio
          ? el("button", { type: "button", class: "collegamento", onclick: () => mostraRegione(r.dettaglio) }, r.dettaglio) : "—"),
        el("td", { "data-col": "Certezza" }, el("span", { class: `certezza cert-${r.certezza.livello}` }, r.certezza.testo)));
    })));
  corpo.append(tab);
}

function tappaConnessioni(corpo, t) {
  for (const id of t.connessioni) {
    const k = stato.scheda.connessioni.find((x) => x.id === id);
    if (k) corpo.append(schedaConnessione(k));
  }
}

function tappaPulse(corpo, t) {
  const lista = selezionePulse(stato.percorso).slice(0, t.quanti || 4);
  if (!lista.length) return corpo.append(el("p", { class: "vuoto" }, messaggioPulseVuoto()));
  corpo.append(...lista.map((v) => schedaEsterno(v)));
  corpo.append(el("p", { class: "meta" },
    el("button", { type: "button", class: "collegamento", onclick: () => { apriSezione("pulse"); $("#tab-pulse").focus(); } },
      "Tutti i suggerimenti e come sono scelti")));
}

function tappaRielabora(corpo, t) {
  corpo.append(areaNota(t), el("div", { class: "azioni" },
    el("button", { type: "button", class: "primario", onclick: scaricaTaccuino }, "Scarica il taccuino (.md)"),
    el("button", { type: "button", onclick: () => { apriSezione("taccuino"); $("#tab-taccuino").focus(); } }, "Apri il taccuino")));
}

/* ---------- connessioni ---------- */

function schedaOpera(o) {
  const autori = o.autori.map((x) => x.valore).join(", ") || "autore non indicato";
  const date = [...new Set(o.date.map((x) => x.valore))].join(", ") || "data non indicata";
  const coll = o.collezioni.map((x) => x.valore).filter(Boolean);
  return el("figure", { class: "opera-collegata" },
    o.immagine
      ? el("img", { src: o.immagine.src, alt: `${o.titolo}, ${autori}, ${date}`, loading: "lazy", width: "240", height: "170" })
      : el("div", { class: "senza-immagine" }, "Immagine non disponibile"),
    el("figcaption", {},
      el("strong", {}, o.titolo),
      el("span", {}, `${autori} · ${date}`),
      coll.length ? el("span", {}, coll.slice(0, 2).join("; ") + (coll.length > 2 ? "; …" : "")) : null,
      ...o.avvisi.map((a) => el("span", { class: "avviso" }, a)),
      el("span", { class: "meta" },
        el("a", { href: `https://www.wikidata.org/wiki/${o.wikidata}`, target: "_blank", rel: "noopener" }, `Wikidata ${o.wikidata}`),
        o.immagine ? [" · Immagine: ", el("a", { href: o.immagine.pagina, target: "_blank", rel: "noopener" }, `Commons, ${o.immagine.licenza}`)] : null)));
}

function schedaConnessione(k) {
  const tipo = TIPI_CONNESSIONE[k.tipo];
  const art = el("article", { class: `connessione con-${k.tipo}` },
    el("p", { class: "tipo-connessione" }, el("span", { "aria-hidden": "true" }, tipo.segno), ` ${tipo.etichetta} · ${k.relazione}`),
    el("h3", {}, k.titolo),
    el("p", { class: "meta" }, `Tipo: ${tipo.spiega}.`));
  for (const b of k.blocchi) art.append(blocco(b, k.origine, k.stato, k.revisione));
  if (k.opere.length) art.append(el("div", { class: "opere" }, k.opere.map(schedaOpera)));
  if (k.calcolo) {
    art.append(el("p", {}, k.calcolo.spiegazione));
    art.append(el("p", { class: "meta" }, `Notazioni di quest'opera: ${k.calcolo.notazioni_opera.join(", ")}`));
    for (const r of k.calcolo.risultati) {
      art.append(el("div", { class: "risultato-calcolo" },
        schedaOpera(r.opera),
        el("p", {}, `In comune: `, ...r.in_comune.flatMap((c, i) => [i ? ", " : "",
          el("a", { href: `https://iconclass.org/${encodeURIComponent(c)}`, target: "_blank", rel: "noopener" }, c)]),
          ` · indice di Jaccard ${String(r.jaccard).replace(".", ",")}`)));
    }
  }
  if (k.annotazioni?.length) {
    art.append(el("p", { class: "meta" }, "Sull'immagine: ",
      ...k.annotazioni.map(annotazione).filter(Boolean).map((a) =>
        el("button", { type: "button", class: "collegamento", onclick: () => mostraRegione(a.id) }, a.titolo))));
  }
  art.append(el("div", { class: "azioni" }, bottoneTaccuino({ tipo: "connessione", id: k.id, titolo: k.titolo, sottotipo: k.tipo })));
  return art;
}

/* ---------- ArtNotes Pulse ---------- */

const esterno = (id) => stato.scheda.pulse.contenuti.find((v) => v.video_id === id);
function selezionePulse(percorso) {
  const sel = stato.scheda.pulse.selezioni?.[percorso];
  return sel ? sel.map((s) => ({ ...esterno(s.id), _punteggio: s })).filter((v) => v.video_id) : [];
}
function esterniPerRegione(idA) {
  return stato.scheda.pulse.contenuti.flatMap((v) => {
    const l = v.annotazioni.find((x) => x.id === idA);
    return l ? [{ v, motivo: l.motivazione }] : [];
  });
}
function messaggioPulseVuoto() {
  const p = stato.scheda.pulse;
  if (stato.vista === "pubblico") return "In modalità pubblica non ci sono ancora suggerimenti esterni revisionati.";
  if (p.stato_fonte === "metadati_mancanti") return "I suggerimenti esterni non sono disponibili: i metadati dei video non sono stati verificati. L'esplorazione dell'opera funziona comunque.";
  if (p.stato_fonte === "assente") return "Per quest'opera non ci sono ancora suggerimenti esterni.";
  return "Nessun suggerimento per questo percorso.";
}
function linkEsterno(v) {
  return el("a", { href: v.url, target: "_blank", rel: "noopener noreferrer", class: "link-esterno" },
    v.titolo, el("span", { class: "nascosto" }, " (apre YouTube, sito esterno)"), el("span", { "aria-hidden": "true" }, " ↗"));
}
function elencoEsterniRegione(idA) {
  const lista = esterniPerRegione(idA);
  if (!lista.length) return null;
  return el("details", { class: "esterni-regione" },
    el("summary", {}, `Approfondisci su YouTube (${lista.length}, contenuti esterni)`),
    el("ul", {}, lista.map(({ v, motivo }) => el("li", {}, linkEsterno(v), el("span", { class: "meta" }, ` · ${v.canale}. Collegamento: ${motivo}.`)))));
}

function schedaEsterno(v) {
  const info = [v.canale, durata(v.durata_s), lingua(v.lingua), v.pubblicato_il?.slice(0, 4), "YouTube"].filter(Boolean).join(" · ");
  const art = el("article", { class: "esterno" },
    v.miniatura ? el("img", { src: v.miniatura, alt: "", loading: "lazy", referrerpolicy: "no-referrer", width: "160", height: "90" }) : null,
    el("div", { class: "esterno-testo" },
      el("h3", {}, linkEsterno(v)),
      el("p", { class: "meta" }, info),
      el("p", { class: "etichette" },
        el("span", { class: `etichetta rel-${v.relazione}` }, v.relazione_testo),
        el("span", { class: `etichetta aff-${v.affidabilita}` }, v.affidabilita_testo)),
      el("p", {}, el("strong", {}, "Perché te lo suggeriamo: "), v.motivazione),
      ...v.avvertenze.map((a) => el("p", { class: "avviso" }, `Attenzione: ${a}.`)),
      v.da_ricontrollare ? el("p", { class: "avviso" }, "Disponibilità da ricontrollare: ultima verifica oltre 30 giorni fa.") : null,
      v.annotazioni.length ? el("p", { class: "meta" }, "Collegato ai dettagli: ",
        ...v.annotazioni.map((l) => annotazione(l.id)).filter(Boolean).map((a) =>
          el("button", { type: "button", class: "collegamento", onclick: () => mostraRegione(a.id), title: v.annotazioni.find((l) => l.id === a.id).motivazione }, a.titolo))) : null,
      v._punteggio ? el("details", { class: "punteggio" },
        el("summary", {}, `Punteggio ${v._punteggio.punteggio.toFixed(2).replace(".", ",")}: come è calcolato`),
        el("table", { class: "tabella" },
          el("thead", {}, el("tr", {}, el("th", { scope: "col" }, "Componente"), el("th", { scope: "col" }, "Valore"), el("th", { scope: "col" }, "Peso"))),
          el("tbody", {}, Object.entries(v._punteggio.componenti).map(([k, x]) =>
            el("tr", {}, el("td", {}, NOMI_COMPONENTI[k] || k), el("td", {}, x.toFixed(2).replace(".", ",")),
              el("td", {}, `${Math.round((stato.scheda.pulse.pesi?.[k] || 0) * 100)}%`)))))) : null,
      el("p", { class: "meta" },
        `${v.stato === "pubblicato" ? "Revisionato e pubblicato" : "Candidato, non revisionato"} · ` +
        `${v.giudizio?.tipo === "ai" ? `classificato da AI (${v.giudizio.modello}) su ${v.giudizio.base}` : "classificazione redazionale"} · ` +
        `disponibilità verificata il ${dataIt(v.verificato_il)}`),
      el("div", { class: "azioni" },
        el("a", { href: v.url, target: "_blank", rel: "noopener noreferrer", class: "bottone" }, "Guarda su YouTube",
          el("span", { class: "nascosto" }, " (sito esterno)"), el("span", { "aria-hidden": "true" }, " ↗")),
        bottoneTaccuino({ tipo: "video", id: v.video_id, titolo: v.titolo, url: v.url, canale: v.canale }))));
  return art;
}

function sezionePulse(box) {
  const p = stato.scheda.pulse;
  box.append(el("h2", {}, "ArtNotes Pulse"), el("p", { class: "politica" }, p.politica));
  if (!p.contenuti.length) return box.append(el("p", { class: "vuoto" }, messaggioPulseVuoto()));
  const c = p.conteggi || {};
  box.append(el("p", { class: "meta" },
    `${p.contenuti.length} video selezionati fra i candidati della ricerca; ${c.respinti ?? 0} scartati con motivazione (fuori tema, doppioni, omonimie). ` +
    `Metadati verificati con YouTube Data API il ${dataIt(p.verificato_il)}.`));
  const ordine = stato.ordinePulse || (PERCORSI.includes(stato.percorso) ? stato.percorso : "curioso");
  const sel = el("select", { id: "ordine-pulse", onchange: (e) => { stato.ordinePulse = e.target.value; apriSezione("pulse"); $("#ordine-pulse").focus(); } },
    ...PERCORSI.map((x) => el("option", { value: x, selected: x === ordine }, ETICHETTE_PERCORSO[x])),
    el("option", { value: "categorie", selected: ordine === "categorie" }, "Tutti, per categoria"));
  box.append(el("p", {}, el("label", { for: "ordine-pulse" }, "Selezione per il percorso: "), sel));
  if (ordine === "categorie") {
    const gruppi = {};
    for (const v of p.contenuti) (gruppi[v.categoria_testo] ||= []).push(v);
    for (const [nome, lista] of Object.entries(gruppi)) box.append(el("h3", { class: "gruppo" }, `${nome} (${lista.length})`), ...lista.map((v) => schedaEsterno(v)));
  } else {
    const lista = selezionePulse(ordine);
    box.append(el("p", { class: "meta" }, `${lista.length} suggerimenti adatti a «${ETICHETTE_PERCORSO[ordine]}», in ordine di punteggio. ` +
      "A parità di merito, un canale già presente scende: la diversità vale il 10%."));
    box.append(...lista.map((v) => schedaEsterno(v)));
  }
}

/* ---------- taccuino ---------- */

function testoTaccuino() {
  const t = leggiTaccuino();
  const s = stato.scheda;
  const titolo = s.opera.catalogo.titoli[0].valore;
  const indirizzo = location.origin + location.pathname;
  const righe = [`# Taccuino — ${titolo}`, "", `Esportato da ArtNotes il ${dataIt(new Date().toISOString())}. Opera: ${s.opera.id}.`, ""];
  const nomi = { osserva: "Che cosa ho osservato", ipotesi: "La mia domanda o ipotesi", lettura: "La mia lettura" };
  const note = Object.entries(t.note).filter(([, v]) => v && v.trim());
  if (note.length) {
    righe.push("## Le mie note", "");
    for (const [k, v] of note) righe.push(`### ${nomi[k] || k}`, "", v.trim(), "");
  }
  if (t.voci.length) {
    righe.push("## Riferimenti salvati", "");
    for (const v of t.voci) {
      if (v.tipo === "video") righe.push(`- Video (contenuto esterno, non verificato da ArtNotes): «${v.titolo}», ${v.canale}. ${v.url}`);
      else if (v.tipo === "connessione") righe.push(`- Connessione ${TIPI_CONNESSIONE[v.sottotipo]?.etichetta.toLowerCase().replace("connessione ", "") || ""}: ${v.titolo}. ${indirizzo}?percorso=ispirazione`);
      else righe.push(`- Dettaglio ${v.id}: ${v.titolo}. ${indirizzo}#${v.id}`);
    }
    righe.push("");
  }
  righe.push("## Avvertenza", "",
    "I testi di ArtNotes citati in questo prototipo sono bozze generate da AI e non revisionate. " +
    "Immagine e metadati dell'opera: The Metropolitan Museum of Art, Open Access (CC0). Dati: Wikidata (CC0). " +
    "Immagini delle opere collegate: Wikimedia Commons (licenze indicate nella scheda).", "");
  return righe.join("\n");
}

function scaricaTaccuino() {
  const blob = new Blob([testoTaccuino()], { type: "text/markdown;charset=utf-8" });
  const a = el("a", { href: URL.createObjectURL(blob), download: `taccuino-artnotes-${stato.scheda.opera.id.replace(":", "-")}.md` });
  document.body.append(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  annuncia("Taccuino scaricato.");
}

function sezioneTaccuino(box) {
  const t = leggiTaccuino();
  box.append(el("h2", {}, "Taccuino"),
    el("p", { class: "meta" }, "Il taccuino resta solo in questo browser: niente account, niente invio di dati. Puoi scaricarlo o cancellarlo quando vuoi."));
  const note = Object.entries(t.note).filter(([, v]) => v && v.trim());
  if (!note.length && !t.voci.length) {
    box.append(el("p", { class: "vuoto" }, "Il taccuino è vuoto. Aggiungi dettagli, connessioni o video con «Aggiungi al taccuino», oppure scrivi nelle tappe del percorso «Voglio approfondire»."));
    return;
  }
  const nomi = { osserva: "Che cosa ho osservato", ipotesi: "La mia domanda o ipotesi", lettura: "La mia lettura" };
  for (const [k, v] of note) box.append(el("h3", {}, nomi[k] || k), el("p", { class: "nota-salvata" }, v));
  if (t.voci.length) {
    box.append(el("h3", {}, `Riferimenti salvati (${t.voci.length})`), el("ul", { class: "voci-taccuino" }, t.voci.map((v) =>
      el("li", {},
        v.tipo === "video" ? [el("a", { href: v.url, target: "_blank", rel: "noopener noreferrer" }, v.titolo), ` · ${v.canale} · video esterno`]
          : v.tipo === "dettaglio" ? el("button", { type: "button", class: "collegamento", onclick: () => seleziona(v.id) }, `Dettaglio: ${v.titolo}`)
          : `Connessione: ${v.titolo}`))));
  }
  const cancella = el("button", { type: "button" }, "Cancella il taccuino");
  cancella.addEventListener("click", () => {
    if (cancella.dataset.conferma !== "1") {
      cancella.dataset.conferma = "1";
      cancella.textContent = "Conferma: cancella tutto";
      return;
    }
    try { localStorage.removeItem(chiaveTaccuino()); } catch { /* niente da cancellare */ }
    annuncia("Taccuino cancellato.");
    apriSezione("taccuino");
    $("#tab-taccuino").focus();
  });
  box.append(el("div", { class: "azioni" },
    el("button", { type: "button", class: "primario", onclick: scaricaTaccuino }, "Scarica (.md)"), cancella));
}

/* ---------- sezioni a schede ---------- */

function schede(s) {
  const elencoSezioni = [
    { id: "catalogo", titolo: "Catalogo" },
    ...s.sezioni.map((x) => ({ id: x.id, titolo: x.titolo })),
    { id: "pulse", titolo: "Pulse" },
    { id: "taccuino", titolo: "Taccuino" },
    { id: "fonti", titolo: "Fonti" },
  ];
  const barra = $("#schede");
  elencoSezioni.forEach((sez, i) => {
    barra.append(
      el("button", {
        type: "button",
        role: "tab",
        id: `tab-${sez.id}`,
        "aria-controls": "contenuto-scheda",
        "aria-selected": "false",
        tabindex: "-1",
        onclick: () => apriSezione(sez.id),
        onkeydown: (e) => {
          const tasti = { ArrowRight: 1, ArrowLeft: -1 };
          if (!(e.key in tasti)) return;
          const j = (i + tasti[e.key] + elencoSezioni.length) % elencoSezioni.length;
          apriSezione(elencoSezioni[j].id);
          $(`#tab-${elencoSezioni[j].id}`).focus();
        },
      }, sez.titolo)
    );
  });
  apriSezione("in-breve");
}

function apriSezione(id) {
  stato.sezione = id;
  document.querySelectorAll("#schede [role=tab]").forEach((b) => {
    const attiva = b.id === `tab-${id}`;
    b.setAttribute("aria-selected", String(attiva));
    b.tabIndex = attiva ? 0 : -1;
  });
  const box = $("#contenuto-scheda");
  box.setAttribute("aria-labelledby", `tab-${id}`);
  box.replaceChildren();
  if (id === "catalogo") return sezioneCatalogo(box);
  if (id === "fonti") return sezioneFonti(box);
  if (id === "pulse") return sezionePulse(box);
  if (id === "taccuino") return sezioneTaccuino(box);

  const sez = stato.scheda.sezioni.find((x) => x.id === id);
  box.append(el("h2", {}, sez.titolo));
  if (!sez.blocchi.length) box.append(el("p", { class: "vuoto" }, "Nessun contenuto pubblicato in questa sezione."));
  for (const b of sez.blocchi) {
    box.append(blocco(b, b.origine, b.stato, b.revisione));
    if (b.mostra_elenco) box.append(tabellaWikidata(b.mostra_elenco));
  }
  if (sez.mostra_connessioni) for (const k of stato.scheda.connessioni) box.append(schedaConnessione(k));
  if (sez.livello_annotazioni) {
    const pertinenti = stato.scheda.annotazioni.filter((a) => a.categoria === sez.livello_annotazioni);
    if (pertinenti.length) {
      box.append(
        el("p", { class: "meta" }, `Dettagli sull'immagine (${CATEGORIE[sez.livello_annotazioni]}):`),
        el("div", {}, pertinenti.map((a) =>
          el("button", { type: "button", class: "collegamento", onclick: () => seleziona(a.id) }, a.domanda ? `${a.titolo} — ${a.domanda}` : a.titolo)))
      );
    }
  }
}

function tabellaWikidata(chiave) {
  const righe = stato.scheda.opera.catalogo[chiave] || [];
  const conQualificatori = chiave === "proprietari_wikidata";
  return el(
    "table",
    { class: "tabella" },
    el("caption", { class: "meta", style: "text-align:left" },
      chiave === "soggetti_wikidata" ? "Soggetti raffigurati secondo Wikidata (P180)" : "Proprietari secondo Wikidata (P127), nell'ordine di Wikidata"),
    el("thead", {}, el("tr", {}, el("th", {}, "Valore"), conQualificatori ? el("th", {}, "Periodo") : null, el("th", {}, "Riferimenti"))),
    el("tbody", {}, righe.map((r) =>
      el("tr", {},
        el("td", {}, r.valore),
        conQualificatori ? el("td", {}, Object.entries(r.qualificatori || {}).map(([k, v]) => `${k} ${v.join(", ")}`).join("; ") || "—") : null,
        el("td", {}, r.riferimenti ? `${r.riferimenti}` : el("span", { class: "avviso" }, "nessuno"))
      )))
  );
}

function sezioneCatalogo(box) {
  const c = stato.scheda.opera.catalogo;
  const nomeFonte = (id) => stato.scheda.fonti[id]?.titolo.split(",")[0] || id;
  box.append(
    el("h2", {}, "Catalogo"),
    el("p", { class: "meta" }, "Ogni dato è mostrato con la fonte da cui proviene, nella formulazione originale. Se le fonti divergono, i valori restano separati."),
  );
  const tab = (titolo, righe, colonne) =>
    el("table", { class: "tabella" },
      el("caption", { style: "text-align:left;font-weight:600" }, titolo),
      el("thead", {}, el("tr", {}, colonne.map(([n]) => el("th", {}, n)))),
      el("tbody", {}, righe.map((r) => el("tr", {}, colonne.map(([, f]) => el("td", {}, f(r) ?? "—"))))));

  box.append(
    tab("Titolo", c.titoli, [["Valore", (r) => r.valore], ["Lingua", (r) => r.lingua], ["Fonte", (r) => nomeFonte(r.fonte)]]),
    tab("Attribuzione", c.attribuzioni, [
      ["Autore", (r) => r.autore],
      ["Qualifica originale", (r) => r.qualifica_originale || "nessuna"],
      ["Fonte", (r) => nomeFonte(r.fonte) + (r.riferimenti !== undefined ? ` (riferimenti: ${r.riferimenti})` : "")],
    ]),
    el("p", { class: "meta" }, `In evidenza: ${nomeFonte(c.attribuzione_in_evidenza.fonte)}. ${c.attribuzione_in_evidenza.motivazione}`),
    tab("Datazione", c.datazioni, [
      ["Testo originale", (r) => r.testo_originale || "(vuoto)"],
      ["Intervallo per la ricerca", (r) => (r.intervallo ? r.intervallo.join("–") : "—")],
      ["Fonte", (r) => nomeFonte(r.fonte)],
    ]),
    tab("Tecnica e dimensioni", [...c.tecnica.map((x) => ({ ...x, k: "Tecnica" })), ...c.dimensioni.map((x) => ({ ...x, k: "Dimensioni" }))], [
      ["Voce", (r) => r.k], ["Valore (testo originale)", (r) => r.valore], ["Fonte", (r) => nomeFonte(r.fonte)],
    ]),
    tab("Istituzione", c.istituzione, [
      ["Sede", (r) => r.valore], ["Inventario", (r) => r.inventario], ["Linea di credito", (r) => r.linea_di_credito],
    ])
  );
  const img = stato.scheda.immagine;
  box.append(
    tab("Diritti (separati per livello)", [
      { k: "Metadati", v: img.diritti.metadati },
      { k: "Fotografia", v: img.diritti.fotografia },
      { k: "Opera rappresentata", v: img.diritti.opera },
    ], [["Livello", (r) => r.k], ["Condizione", (r) => r.v]]),
    el("p", { class: "meta" }, `Condizioni verificate il ${dataIt(img.diritti.verificato_il)}. Immagine di riferimento: ${img.id} (SHA-256 ${img.sha256.slice(0, 12)}…).`)
  );
}

function sezioneFonti(box) {
  box.append(el("h2", {}, "Fonti"));
  for (const [id, f] of Object.entries(stato.scheda.fonti)) {
    box.append(
      el("div", { class: "fonte" },
        el("h3", {}, f.url ? el("a", { href: f.url, target: "_blank", rel: "noopener" }, f.titolo) : f.titolo),
        el("p", { class: "meta" }, `${f.tipo} · consultata il ${dataIt(f.consultato)} · licenza: ${f.licenza}`),
        f.note ? el("p", { class: "meta" }, f.note) : null,
        el("p", { class: "meta" }, `Identificativo interno: ${id}`))
    );
  }
  if (stato.scheda.pulse.contenuti.length) {
    box.append(el("div", { class: "fonte" },
      el("h3", {}, "YouTube Data API v3"),
      el("p", { class: "meta" },
        `Metadati dei video suggeriti in Pulse (titolo, canale, durata, lingua, data, disponibilità). Verificati il ${dataIt(stato.scheda.pulse.verificato_il)}. ` +
        "Sono contenuti esterni, non fonti dei testi di ArtNotes.")));
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape" || !stato.selezionata) return;
  if (e.target.closest?.("textarea, input, select")) return;
  deseleziona();
});

window.addEventListener("hashchange", () => {
  if (!stato.scheda) return;
  const id = location.hash.slice(1);
  if (stato.scheda.annotazioni.some((a) => a.id === id)) {
    if (id !== stato.selezionata) seleziona(id, { daUrl: true });
  } else if (stato.selezionata) {
    deseleziona();
  }
});

avvia();
