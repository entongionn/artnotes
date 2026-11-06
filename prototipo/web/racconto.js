/* ArtNotes — racconto e visita guidata.
 * Lettura: prosa continua con note numerate alle fonti.
 * Visita: schermo intero, la camera segue il racconto frase per frase, le etichette
 * compaiono con la narrazione, il racconto può uscire dal quadro (autore, altre opere).
 * Usa le funzioni di app.js (stato, el, $, annotazione, mostraRegione, dataIt, animazioniAttive). */
"use strict";

const SEGNI_FRASE = { documentato: "", interpretazione: "◆", ipotesi: "▲", osservazione: "●", lacuna: "○", raccordo: "" };
const NOMI_FRASE = { documentato: "Documentato", interpretazione: "Interpretazione di una fonte", ipotesi: "Ipotesi",
  osservazione: "Osservazione sull'immagine", lacuna: "Lacuna", raccordo: "Raccordo narrativo" };

function nomeFonteBreve(id) {
  const f = stato.scheda.fonti[id];
  return f?.breve || f?.titolo?.split(",")[0] || id;
}

function testoNota(fr) {
  return (fr.f || []).map((r) => {
    const f = stato.scheda.fonti[r.fonte];
    const letto = f?.lettura && f.lettura !== "testo completo" ? f.lettura : null;
    const nota = r.nota && r.nota !== letto ? ` (${r.nota})` : "";
    return `${nomeFonteBreve(r.fonte)}${nota}${letto ? ` — letto: ${letto}` : ""}`;
  }).join("; ");
}

/* ---------- lettura ---------- */

function renderRacconto(box, { scene = null, compatto = false } = {}) {
  const r = stato.scheda.racconto;
  if (!r) return box.append(el("p", { class: "vuoto" }, "Per quest'opera non c'è ancora un racconto."));
  const scelte = scene ? r.scene.filter((s) => scene.includes(s.id)) : r.scene;
  const art = el("article", { class: "racconto" });
  if (!compatto) {
    art.append(
      el("h2", {}, r.titolo),
      el("p", { class: "sottotitolo-racconto" }, r.sottotitolo),
      el("div", { class: "azioni" },
        el("button", { type: "button", class: "primario", onclick: () => apriVisita(r.scene[0].id) }, "▶ Visita guidata a schermo intero"),
        el("span", { class: "meta" }, `${r.scene.length} scene · ${r.durata}`)),
      legendaRacconto(r)
    );
  }
  for (const s of scelte) art.append(renderScena(s, { compatto }));
  box.append(art);
}

function legendaRacconto(r) {
  return el("details", { class: "legenda" },
    el("summary", {}, "Come leggere il racconto"),
    el("p", {}, "Il testo normale è documentato da una fonte. I segni nelle note dicono di che tipo è ogni frase: ",
      el("strong", {}, "◆"), " interpretazione di una fonte, ", el("strong", {}, "●"), " osservazione sull'immagine, ",
      el("strong", {}, "▲"), " ipotesi, ", el("strong", {}, "○"), " lacuna. Il corsivo segna ipotesi e lacune. ",
      "Il pulsante ", el("strong", {}, "◉"), " mostra il dettaglio sull'immagine."),
    el("p", { class: "meta" },
      r.origine?.tipo === "ai" ? `Racconto generato da AI (${r.origine.modello}), ${dataIt(r.origine.data)}` : "Racconto redazionale",
      ` · ${r.stato === "pubblicato" ? "pubblicato" : "bozza, non revisionato"} · ${r.note_totali} note alle fonti. `,
      "Solo le fonti effettivamente lette possono sostenere una frase: il livello di lettura (testo completo, passi, abstract) è indicato in nota."));
}

function renderScena(s, { compatto = false } = {}) {
  const r = stato.scheda.racconto;
  const n = r.scene.indexOf(s) + 1;
  const sez = el("section", { class: "scena", id: `scena-${s.id}` },
    el(compatto ? "h3" : "h3", { class: "titolo-scena" }, el("span", { class: "numero-scena" }, `${n}`), s.titolo));
  let p = el("p", { class: "prosa" });
  const note = [];
  for (const fr of s.frasi) {
    if (fr.fuori) {
      // La figura interrompe il paragrafo: si chiude quello corrente e se ne apre uno nuovo.
      if (p.childNodes.length) sez.append(p);
      p = el("p", { class: "prosa" });
      sez.append(figuraFuori(fr.fuori, true));
    }
    const span = el("span", { class: `frase f-${fr.r}` }, fr.t);
    p.append(span);
    if (fr.nota) {
      note.push(fr);
      p.append(el("sup", {}, el("a", {
        href: `#nota-${fr.nota}`, class: "rimando", "aria-label": `Nota ${fr.nota}: ${NOMI_FRASE[fr.r]}`,
        onclick: (e) => { e.preventDefault(); apriNota(fr.nota); },
      }, `${SEGNI_FRASE[fr.r]}${fr.nota}`)));
    } else if (fr.r !== "raccordo") {
      p.append(el("sup", { class: "segno-solo", title: NOMI_FRASE[fr.r] }, SEGNI_FRASE[fr.r]));
    }
    if (fr.a) {
      p.append(" ", el("button", {
        type: "button", class: "vai-regione", title: `Mostra sull'immagine: ${fr.etichetta}`,
        "aria-label": `Mostra sull'immagine: ${fr.etichetta}`, onclick: () => mostraRegione(fr.a),
      }, "◉"));
    }
    p.append(" ");
  }
  sez.append(p);
  if (note.length) {
    sez.append(el("details", { class: "note-scena", id: `note-${s.id}` },
      el("summary", {}, `Fonti di questa scena · ${note.length} ${note.length === 1 ? "nota" : "note"}`),
      el("ol", {}, note.map((fr) => el("li", { id: `nota-${fr.nota}`, value: fr.nota, tabindex: "-1" },
        el("span", { class: "tipo-nota" }, `${SEGNI_FRASE[fr.r]} ${NOMI_FRASE[fr.r]}`),
        fr.certezza ? el("span", { class: `certezza cert-${fr.certezza.livello}` }, ` · ${fr.certezza.testo}`) : null,
        el("br"),
        ...fr.f.flatMap((ref, i) => {
          const f = stato.scheda.fonti[ref.fonte];
          const letto = f?.lettura && f.lettura !== "testo completo" ? f.lettura : null;
          return [i ? "; " : "", f?.url ? el("a", { href: f.url, target: "_blank", rel: "noopener" }, f.titolo) : (f?.titolo || ref.fonte),
            ref.nota && ref.nota !== letto ? ` (${ref.nota})` : "", letto ? el("span", { class: "meta" }, ` — letto: ${letto}`) : ""];
        }))))));
  }
  if (compatto) {
    sez.append(el("div", { class: "azioni" },
      el("button", { type: "button", class: "primario", onclick: () => apriVisita(s.id, { soloScena: true }) }, "▶ Guarda questa scena sull'immagine")));
  }
  return sez;
}

function apriNota(n) {
  const li = document.getElementById(`nota-${n}`);
  if (!li) return;
  li.closest("details").open = true;
  li.focus({ preventScroll: true });
  li.scrollIntoView({ behavior: animazioniAttive() ? "smooth" : "auto", block: "center" });
  li.classList.add("evidenziata");
  setTimeout(() => li.classList.remove("evidenziata"), 1800);
}

function figuraFuori(fu, inline) {
  const s = fu.scheda;
  const img = s.immagine;
  const date = s.nascita ? `${s.nascita}–${s.morte || ""}` : (s.date || []).map((d) => d.valore).filter(Boolean)[0];
  return el("figure", { class: inline ? "fuori-inline" : "fuori-grande" },
    img ? el("img", { src: img.src, alt: fu.didascalia || s.nome || s.titolo, loading: "lazy" }) : el("div", { class: "senza-immagine" }, "Immagine non disponibile"),
    el("figcaption", {},
      el("strong", {}, fu.didascalia || s.nome || s.titolo),
      date ? el("span", {}, ` · ${date}`) : null,
      el("span", { class: "meta" }, " · ",
        el("a", { href: `https://www.wikidata.org/wiki/${s.wikidata}`, target: "_blank", rel: "noopener" }, `Wikidata ${s.wikidata}`),
        img ? [" · ", el("a", { href: img.pagina, target: "_blank", rel: "noopener" }, `immagine: Commons, ${img.licenza}`)] : null)));
}

/* ---------- visita guidata ---------- */

const visita = {
  attiva: false, viewer: null, scena: 0, frase: -1, timer: null, inPausa: false, voce: false,
  soloScena: false, overlay: null, ritornoFocus: null, chiaveListener: null,
};

function costruisciVisita() {
  if (document.getElementById("visita")) return;
  const voceDisponibile = "speechSynthesis" in window;
  const dlg = el("div", { id: "visita", class: "visita", role: "dialog", "aria-modal": "true", "aria-labelledby": "visita-titolo", hidden: true },
    el("div", { id: "visita-visore", class: "visita-visore" }),
    el("aside", { id: "visita-fuori", class: "visita-fuori", hidden: true }),
    el("div", { class: "visita-pannello" },
      el("p", { class: "visita-avanzamento", id: "visita-avanzamento" }),
      el("h2", { id: "visita-titolo" }),
      el("p", { id: "visita-testo", class: "visita-testo", "aria-live": "polite" }),
      el("p", { id: "visita-fonte", class: "visita-fonte" }),
      el("div", { class: "visita-comandi", role: "toolbar", "aria-label": "Comandi della visita" },
        el("button", { type: "button", id: "v-scena-prec", title: "Scena precedente (PagSu)", onclick: () => vaiScena(visita.scena - 1) }, "« Scena"),
        el("button", { type: "button", id: "v-prec", title: "Frase precedente (←)", onclick: () => vaiFrase(visita.frase - 1) }, "‹ Frase"),
        el("button", { type: "button", id: "v-play", class: "v-play", title: "Pausa o riprendi (barra spaziatrice)", onclick: commutaPausa }, "Pausa"),
        el("button", { type: "button", id: "v-succ", title: "Frase successiva (→)", onclick: () => vaiFrase(visita.frase + 1) }, "Frase ›"),
        el("button", { type: "button", id: "v-scena-succ", title: "Scena successiva (PagGiù)", onclick: () => vaiScena(visita.scena + 1) }, "Scena »"),
        voceDisponibile ? el("button", { type: "button", id: "v-voce", "aria-pressed": "false", onclick: commutaVoce }, "Voce") : null,
        el("button", { type: "button", id: "v-esci", class: "v-esci", onclick: chiudiVisita }, "Esci ✕"))));
  document.body.append(dlg);
}

function apriVisita(idScena, { soloScena = false } = {}) {
  costruisciVisita();
  const r = stato.scheda.racconto;
  visita.ritornoFocus = document.activeElement;
  visita.soloScena = soloScena;
  visita.attiva = true;
  visita.inPausa = false;
  const dlg = document.getElementById("visita");
  dlg.hidden = false;
  document.body.classList.add("visita-aperta");
  try { dlg.requestFullscreen?.().catch(() => {}); } catch { /* schermo intero non consentito */ }
  if (!visita.viewer) {
    const img = stato.scheda.immagine;
    visita.viewer = OpenSeadragon({
      element: document.getElementById("visita-visore"),
      tileSources: img.dzi, showNavigationControl: false, showNavigator: false,
      maxZoomPixelRatio: 1.5, visibilityRatio: 0.8, animationTime: animazioniAttive() ? 1.6 : 0, springStiffness: 5,
      gestureSettingsMouse: { clickToZoom: false }, gestureSettingsTouch: { pinchRotate: false },
    });
  } else {
    visita.viewer.animationTime = animazioniAttive() ? 1.6 : 0;
  }
  const parti = () => {
    visita.scena = Math.max(0, r.scene.findIndex((s) => s.id === idScena));
    visita.frase = -1;
    iniziaScena();
  };
  if (visita.viewer.world.getItemCount()) parti(); else visita.viewer.addOnceHandler("open", parti);
  aggiornaPlay();
  visita.chiaveListener = (e) => {
    if (!visita.attiva) return;
    if (e.key === "Escape") { e.preventDefault(); chiudiVisita(); }
    else if (e.key === " " && !e.target.closest("button")) { e.preventDefault(); commutaPausa(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); vaiFrase(visita.frase + 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); vaiFrase(visita.frase - 1); }
    else if (e.key === "PageDown") { e.preventDefault(); vaiScena(visita.scena + 1); }
    else if (e.key === "PageUp") { e.preventDefault(); vaiScena(visita.scena - 1); }
    else if (e.key === "Tab") trappolaFocus(e, dlg);
  };
  document.addEventListener("keydown", visita.chiaveListener, true);
  document.getElementById("v-play").focus();
}

function trappolaFocus(e, dlg) {
  const f = [...dlg.querySelectorAll("button, a[href]")].filter((x) => !x.closest("[hidden]"));
  if (!f.length) return;
  const i = f.indexOf(document.activeElement);
  if (e.shiftKey && i <= 0) { e.preventDefault(); f.at(-1).focus(); }
  else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
}

function chiudiVisita() {
  visita.attiva = false;
  clearTimeout(visita.timer);
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  document.removeEventListener("keydown", visita.chiaveListener, true);
  togliEtichetta();
  document.getElementById("visita").hidden = true;
  document.body.classList.remove("visita-aperta");
  if (document.fullscreenElement) document.exitFullscreen?.().catch(() => {});
  visita.ritornoFocus?.focus?.();
}

function scenaCorrente() { return stato.scheda.racconto.scene[visita.scena]; }

function iniziaScena() {
  const s = scenaCorrente();
  const r = stato.scheda.racconto;
  document.getElementById("visita-titolo").textContent = s.titolo;
  document.getElementById("visita-avanzamento").textContent = `Scena ${visita.scena + 1} di ${r.scene.length} · ${r.titolo}`;
  document.getElementById("visita-testo").replaceChildren();
  document.getElementById("visita-fonte").textContent = "";
  nascondiFuori();
  togliEtichetta();
  inquadraVisita(s.inquadra?.tipo === "regione" ? s.inquadra.regione : null);
  visita.frase = -1;
  clearTimeout(visita.timer);
  visita.timer = setTimeout(() => vaiFrase(0), animazioniAttive() ? 1400 : 300);
}

function vaiScena(i) {
  const r = stato.scheda.racconto;
  if (visita.soloScena && i !== visita.scena) return i > visita.scena ? fineVisita() : iniziaScena();
  if (i < 0) i = 0;
  if (i >= r.scene.length) return fineVisita();
  visita.scena = i;
  iniziaScena();
}

function fineVisita() {
  clearTimeout(visita.timer);
  togliEtichetta();
  nascondiFuori();
  inquadraVisita(null);
  document.getElementById("visita-titolo").textContent = visita.soloScena ? "Fine della scena" : "Fine della visita";
  document.getElementById("visita-testo").replaceChildren(
    el("span", {}, visita.soloScena ? "Puoi continuare nel percorso o rivedere la scena." : "Tutte le frasi hanno una nota alle fonti nel racconto da leggere. "),
    el("button", { type: "button", class: "collegamento", onclick: () => { visita.soloScena = false; vaiScena(0); } }, "Ricomincia"),
    " ",
    el("button", { type: "button", class: "collegamento", onclick: chiudiVisita }, "Torna all'opera"));
  document.getElementById("visita-fonte").textContent = "";
  visita.inPausa = true;
  aggiornaPlay();
}

function vaiFrase(i) {
  const s = scenaCorrente();
  clearTimeout(visita.timer);
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  if (i < 0) return vaiScena(visita.scena - 1);
  if (i >= s.frasi.length) return vaiScena(visita.scena + 1);
  visita.frase = i;
  const fr = s.frasi[i];
  const testo = document.getElementById("visita-testo");
  // Le frasi precedenti della scena restano, attenuate: il racconto si legge come un paragrafo.
  testo.querySelectorAll(".attuale").forEach((x) => x.classList.remove("attuale"));
  testo.replaceChildren(...s.frasi.slice(0, i + 1).map((x, j) =>
    el("span", { class: `v-frase f-${x.r}${j === i ? " attuale" : ""}` }, x.t, x.nota ? el("sup", {}, `${SEGNI_FRASE[x.r]}${x.nota}`) : null, " ")));
  testo.scrollTop = testo.scrollHeight;
  document.getElementById("visita-fonte").textContent = fr.nota
    ? `${NOMI_FRASE[fr.r]} · ${testoNota(fr)}` : (fr.r !== "raccordo" ? NOMI_FRASE[fr.r] : "");

  if (fr.fuori) {
    mostraFuori(fr.fuori);
  } else {
    nascondiFuori();
    if (fr.a) {
      inquadraVisita(fr.a);
      mostraEtichetta(fr.a, fr.etichetta);
    } else if (!s.frasi.slice(0, i).some((x) => x.a)) {
      togliEtichetta();
    }
  }
  programma(fr);
}

function programma(fr) {
  if (visita.inPausa) return;
  if (visita.voce && "speechSynthesis" in window) {
    const u = new SpeechSynthesisUtterance(fr.t);
    u.lang = "it-IT";
    const v = speechSynthesis.getVoices().find((x) => x.lang?.startsWith("it"));
    if (v) u.voice = v;
    u.onend = () => { if (visita.attiva && !visita.inPausa) visita.timer = setTimeout(() => vaiFrase(visita.frase + 1), 500); };
    speechSynthesis.speak(u);
    return;
  }
  const durata = Math.min(15000, Math.max(3800, fr.t.length * 62)) + (fr.fuori ? 1500 : 0) + (fr.a ? 900 : 0);
  visita.timer = setTimeout(() => vaiFrase(visita.frase + 1), durata);
}

function commutaPausa() {
  visita.inPausa = !visita.inPausa;
  aggiornaPlay();
  clearTimeout(visita.timer);
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  if (!visita.inPausa) {
    if (visita.frase < 0) vaiFrase(0);
    else programma(scenaCorrente().frasi[visita.frase]);
  }
}

function aggiornaPlay() {
  const b = document.getElementById("v-play");
  if (!b) return;
  b.textContent = visita.inPausa ? "▶ Riprendi" : "Pausa";
}

function commutaVoce() {
  visita.voce = !visita.voce;
  document.getElementById("v-voce").setAttribute("aria-pressed", String(visita.voce));
  if (!visita.voce && "speechSynthesis" in window) speechSynthesis.cancel();
  if (!visita.inPausa && visita.frase >= 0) { clearTimeout(visita.timer); programma(scenaCorrente().frasi[visita.frase]); }
}

function rettangoloRegione(idA, margineRel = 0.45) {
  const a = annotazione(idA);
  const img = stato.scheda.immagine;
  const asp = img.altezza / img.larghezza;
  const r = a.regione_normalizzata;
  const m = Math.max(r.w, r.h * asp) * margineRel;
  return new OpenSeadragon.Rect(r.x - m, r.y * asp - m, r.w + 2 * m, r.h * asp + 2 * m);
}

/* Allunga il rettangolo verso il basso della quota coperta dal pannello del testo:
 * così il dettaglio resta nella parte libera dello schermo. */
function conSpazioPannello(rett) {
  const pannello = document.querySelector(".visita-pannello");
  const visore = document.getElementById("visita-visore");
  const quota = Math.min(0.55, (pannello?.offsetHeight || 0) / (visore?.offsetHeight || 1));
  return new OpenSeadragon.Rect(rett.x, rett.y, rett.width, rett.height / (1 - quota));
}

function inquadraVisita(idA) {
  const v = visita.viewer;
  if (!v) return;
  const img = stato.scheda.immagine;
  const rett = idA && annotazione(idA)
    ? rettangoloRegione(idA)
    : new OpenSeadragon.Rect(0, 0, 1, img.altezza / img.larghezza);
  v.viewport.fitBounds(conSpazioPannello(rett), !animazioniAttive());
}

function mostraEtichetta(idA, testo) {
  togliEtichetta();
  const a = annotazione(idA);
  if (!a) return;
  const img = stato.scheda.immagine;
  const asp = img.altezza / img.larghezza;
  const r = a.regione_normalizzata;
  const nodo = el("div", { class: "v-regione", "aria-hidden": "true" }, el("span", { class: "v-etichetta" }, testo));
  visita.viewer.addOverlay({ element: nodo, location: new OpenSeadragon.Rect(r.x, r.y * asp, r.w, r.h * asp) });
  visita.overlay = nodo;
  requestAnimationFrame(() => nodo.classList.add("visibile"));
}

function togliEtichetta() {
  if (visita.overlay && visita.viewer) {
    try { visita.viewer.removeOverlay(visita.overlay); } catch { /* già rimosso */ }
  }
  visita.overlay = null;
}

function mostraFuori(fu) {
  const box = document.getElementById("visita-fuori");
  box.replaceChildren(el("p", { class: "fuori-etichetta" }, fu.tipo === "persona" ? "Fuori dal quadro · persona" : "Fuori dal quadro · altra opera"),
    figuraFuori(fu, false));
  box.hidden = false;
  document.getElementById("visita").classList.add("con-fuori");
  togliEtichetta();
  inquadraVisita(null);
}

function nascondiFuori() {
  const box = document.getElementById("visita-fuori");
  if (box) box.hidden = true;
  document.getElementById("visita")?.classList.remove("con-fuori");
}
