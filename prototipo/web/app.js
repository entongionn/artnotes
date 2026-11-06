/* ArtNotes — prototipo Fase 2.
 * Legge solo la scheda composta (api/opere/<id>.json): nessuna dipendenza
 * dalla struttura interna dei dati o delle fonti. */
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
const LIVELLI_INIZIALI = new Set(["osservazione"]);

const stato = {
  scheda: null,
  viewer: null,
  overlay: new Map(),   // id annotazione -> elemento
  selezionata: null,
  livelliAttivi: new Set(LIVELLI_INIZIALI),
  sezione: null,
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
  for (const f of figli.flat()) if (f !== null && f !== undefined) n.append(f.nodeType ? f : String(f));
  return n;
};

const movimentoRidotto = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const animazioniAttive = () => $("#animazioni").checked;

function dataIt(iso) {
  if (!iso) return "";
  const [a, m, g] = iso.slice(0, 10).split("-");
  return `${g}/${m}/${a}`;
}

/* ---------- avvio ---------- */

async function avvia() {
  const parametri = new URLSearchParams(location.search);
  const id = parametri.get("opera") || "435809";
  const pubblico = parametri.get("modo") === "pubblico";
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

  intestazione(scheda);
  banner(scheda);
  copertura(scheda);
  visualizzatore(scheda);
  livelli(scheda);
  elenco(scheda);
  schede(scheda);

  const daHash = location.hash.slice(1);
  if (daHash && scheda.annotazioni.some((a) => a.id === daHash)) seleziona(daHash, { daUrl: true });
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
      "Anteprima redazionale: tutti i testi e le regioni sono bozze generate da AI e non revisionate. Non sono visibili in modalità pubblica.";
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

function seleziona(id, { daUrl = false } = {}) {
  const a = stato.scheda.annotazioni.find((x) => x.id === id);
  if (!a) return;
  stato.selezionata = id;
  if (!stato.livelliAttivi.has(a.categoria)) {
    stato.livelliAttivi.add(a.categoria);
    const box = document.querySelector(`#livelli input[value="${a.categoria}"]`);
    if (box) box.checked = true;
  }
  aggiornaVisibilita();
  evidenzia(id);
  if (stato.viewer?.world.getItemCount()) inquadra(a);
  else stato.viewer?.addOnceHandler("open", () => inquadra(a));
  mostraDettaglio(a);
  if (!daUrl) history.replaceState(null, "", `#${id}`);
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

  const collegati = (a.collegamenti || [])
    .map((id) => stato.scheda.annotazioni.find((x) => x.id === id))
    .filter(Boolean);
  if (collegati.length) {
    d.append(
      el("p", { class: "meta" }, "Dettagli collegati:"),
      el("div", {}, collegati.map((c) => el("button", { type: "button", class: "collegamento", onclick: () => seleziona(c.id) }, c.titolo)))
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

function blocco(b, origineDefault, statoDefault, revisioneDefault) {
  const reg = REGISTRI[b.registro];
  const origine = b.origine || origineDefault;
  const revisione = b.revisione ?? revisioneDefault;
  const statoTesto = { bozza: "Bozza", in_revisione: "In revisione", pubblicato: "Pubblicato", da_aggiornare: "Da aggiornare" }[
    b.stato || statoDefault
  ];
  const fonti = (b.fonti || []).map((r) => {
    const f = stato.scheda.fonti[r.fonte];
    return el("span", {}, f?.url ? el("a", { href: f.url, target: "_blank", rel: "noopener" }, descriviFonte(r)) : descriviFonte(r));
  });
  const righeFonti = [];
  fonti.forEach((f, i) => { if (i) righeFonti.push("; "); righeFonti.push(f); });

  return el(
    "div",
    { class: `blocco reg-${b.registro}` },
    el("span", { class: "badge" }, el("span", { "aria-hidden": "true" }, reg.segno), reg.etichetta),
    el("p", {}, b.testo),
    righeFonti.length ? el("p", { class: "meta" }, "Base: ", ...righeFonti) : null,
    el(
      "p",
      { class: "meta" },
      origine?.tipo === "ai"
        ? `Testo generato da AI (${origine.modello}), ${dataIt(origine.data)}`
        : `Testo redazionale`,
      ` · ${statoTesto || "stato non indicato"} · `,
      revisione ? `Revisionato da ${revisione.revisore}, ${dataIt(revisione.data)}` : "Non revisionato"
    )
  );
}

/* ---------- sezioni a schede ---------- */

function schede(s) {
  const elencoSezioni = [
    { id: "catalogo", titolo: "Catalogo" },
    ...s.sezioni.map((x) => ({ id: x.id, titolo: x.titolo })),
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

  const sez = stato.scheda.sezioni.find((x) => x.id === id);
  box.append(el("h2", {}, sez.titolo));
  if (!sez.blocchi.length) box.append(el("p", { class: "vuoto" }, "Nessun contenuto pubblicato in questa sezione."));
  for (const b of sez.blocchi) {
    box.append(blocco(b, b.origine, b.stato, b.revisione));
    if (b.mostra_elenco) box.append(tabellaWikidata(b.mostra_elenco));
  }
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
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && stato.selezionata) deseleziona();
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
