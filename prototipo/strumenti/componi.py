"""Compone la scheda JSON letta dal visualizzatore (il «contratto» dell'API).

Uso:
    python strumenti/componi.py 435809                 # anteprima redazionale: include le bozze
    python strumenti/componi.py 435809 --pubblico      # solo contenuti con stato «pubblicato»

L'interfaccia web, e in futuro un'app nativa, legge soltanto il file prodotto
qui (web/api/opere/<id>.json), mai i payload delle fonti né la struttura dei
dati redazionali.

Se un'annotazione è stata tracciata su una fotografia diversa da quella
attuale (impronta SHA-256 differente), viene marcata «da_riverificare».
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
USCITA = RADICE / "web" / "api" / "opere"
WEB = RADICE / "web"

REGISTRI = {"documentato", "interpretazione", "osservazione", "ipotesi", "lacuna"}
CATEGORIE = {"osservazione", "iconografia", "composizione", "tecnica"}
STATI = {"bozza", "in_revisione", "pubblicato", "da_aggiornare"}
RE_REGIONE = re.compile(r"^xywh=percent:([\d.]+),([\d.]+),([\d.]+),([\d.]+)$")

# --- Fase 2.5: percorsi, connessioni, contenuti esterni ---
PERCORSI = ("curioso", "studio", "ispirazione")
TIPI_TAPPA = {"scelta", "scopri", "scrivi", "leggi", "evidenze", "connessioni", "pulse", "rielabora", "scena"}
# Categorie di fonte e livelli di lettura: una fonte «non consultata» non può sostenere affermazioni.
CATEGORIE_FONTE = {
    "istituzione": "Scheda del museo",
    "letteratura": "Letteratura critica e universitaria",
    "scientifica": "Studio scientifico di laboratorio",
    "primaria": "Fonte d'epoca",
    "collaborativa": "Base di dati collaborativa",
    "classificazione": "Sistema di classificazione",
    "immagine": "Riproduzione fotografica",
    "divulgazione": "Divulgazione",
}
LETTURE = {"testo completo", "passi pertinenti", "abstract", "non consultato"}
REGISTRI_FRASE = REGISTRI | {"raccordo"}
TIPI_CONNESSIONE = {"documentata", "interpretativa", "algoritmica"}
RELAZIONI_ESTERNE = {
    "opera_esatta": "Parla direttamente dell'opera",
    "dettaglio": "Approfondisce un dettaglio",
    "contesto": "Contesto: serie, pittore, epoca",
    "analogia": "Collegamento tematico, non analisi dell'opera",
    "falso_positivo": "Non pertinente",
}
STATI_ESTERNI = {"candidato", "revisionato", "pubblicato", "respinto"}
AFFIDABILITA = {
    "istituzionale": (1.0, "Istituzione culturale"),
    "editoriale": (0.8, "Editore o emittente"),
    "divulgazione": (0.6, "Divulgazione indipendente"),
    "da_verificare": (0.3, "Affermazioni da verificare"),
}
CATEGORIE_PULSE = {
    "opera_raccontata": "L'opera raccontata",
    "dettagli": "Dettagli da scoprire",
    "cultura_pop": "Arte e cultura pop",
    "conversazioni": "Conversazioni sull'opera",
}
# Punteggio sperimentale della Fase 2.5 (§6.3): pesi da calibrare con giudizi umani.
PESI = {"pertinenza": 0.35, "qualita": 0.25, "intento": 0.15, "diversita": 0.10, "freschezza": 0.10, "interesse": 0.05}
PERTINENZA = {"opera_esatta": 1.0, "dettaglio": 0.9, "contesto": 0.6, "analogia": 0.4}
VALIDITA_ESTERNI_GIORNI = 30


class ErroreValidazione(Exception):
    pass


def _leggi(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _valore_wd(asserzione, etichette):
    v = asserzione["mainsnak"].get("datavalue", {}).get("value")
    if isinstance(v, dict) and "id" in v:
        return etichette.get(v["id"]) or v["id"]
    if isinstance(v, dict) and "time" in v:
        return v["time"].lstrip("+")[:4]
    if isinstance(v, dict) and "amount" in v:
        return v["amount"].lstrip("+")
    if asserzione["mainsnak"].get("snaktype") == "somevalue":
        return "(valore sconosciuto)"
    return v


def _qualificatori_wd(asserzione, etichette):
    out = {}
    for prop, lista in asserzione.get("qualifiers", {}).items():
        vals = []
        for q in lista:
            v = q.get("datavalue", {}).get("value")
            if isinstance(v, dict) and "id" in v:
                vals.append(etichette.get(v["id"]) or v["id"])
            elif isinstance(v, dict) and "time" in v:
                vals.append(v["time"].lstrip("+")[:4])
            else:
                vals.append(str(v))
        out[prop] = vals
    return out


def registro_fonti(met, wd, img):
    acq_met, acq_wd = met["acquisizione"], wd["acquisizione"]
    return {
        "met-435809": {
            "titolo": "The Metropolitan Museum of Art, Collection API, oggetto 435809",
            "breve": "Met, scheda",
            "categoria": "istituzione",
            "tipo": "scheda istituzionale (dati strutturati)",
            "url": met["payload"]["objectURL"],
            "url_dati": acq_met["url"],
            "consultato": acq_met["data"][:10],
            "licenza": "CC0 (metadati)",
            "note": f"metadataDate della fonte: {met['payload'].get('metadataDate', '')[:10]}",
        },
        "wikidata-Q776175": {
            "titolo": "Wikidata, elemento Q776175",
            "breve": "Wikidata",
            "categoria": "collaborativa",
            "tipo": "base di conoscenza collaborativa",
            "url": "https://www.wikidata.org/wiki/Q776175",
            "url_dati": acq_wd["url"],
            "consultato": acq_wd["data"][:10],
            "licenza": "CC0",
            "note": "Molte asserzioni non hanno riferimenti: vanno lette come dato da verificare.",
        },
        "iconclass": {
            "titolo": "Iconclass, notazioni 47I14, 23E43, 23D43, 41C, 25H",
            "breve": "Iconclass",
            "categoria": "classificazione",
            "tipo": "sistema di classificazione iconografica",
            "url": "https://iconclass.org/47I14",
            "consultato": "2026-11-06",
            "licenza": "da verificare",
            "note": "Etichette italiane lette da iconclass.org. Le notazioni provengono da Wikidata.",
        },
        "foto-met-DP119115": {
            "titolo": f"Fotografia {img['file_fotografia']} ({img['larghezza']} × {img['altezza']} px)",
            "breve": "Fotografia del Met",
            "categoria": "immagine",
            "tipo": "immagine di riferimento per le osservazioni visive",
            "url": img["url_originale"],
            "consultato": img["acquisita_il"][:10],
            "licenza": img["diritti"]["fotografia"],
            "note": f"SHA-256 {img['sha256'][:12]}…",
        },
    }


def catalogo(met, wd):
    p = met["payload"]
    ent, et = wd["payload"]["entita"], wd["payload"]["etichette"]
    c = ent.get("claims", {})

    def refs(a):
        return len(a.get("references", []))

    def id_wd(url):
        return url.rstrip("/").rsplit("/", 1)[-1] if url else None

    costituente = (p.get("constituents") or [{}])[0]
    attribuzioni = [
        {
            "fonte": "met-435809",
            "autore": p["artistDisplayName"],
            "id_wikidata": id_wd(costituente.get("constituentWikidata_URL")),
            "qualifica_originale": p.get("artistPrefix") or "",
            "nota_biografica": p.get("artistDisplayBio", ""),
            "ulan": p.get("artistULAN_URL", ""),
        }
    ] + [
        {
            "fonte": "wikidata-Q776175",
            "autore": _valore_wd(a, et),
            "id_wikidata": a["mainsnak"].get("datavalue", {}).get("value", {}).get("id"),
            "qualifica_originale": "; ".join(
                f"{k}: {', '.join(v)}" for k, v in _qualificatori_wd(a, et).items()
            ),
            "riferimenti": refs(a),
        }
        for a in c.get("P170", [])
    ]
    # Concordanza per identità (non per nome) e per qualifica.
    ids = [a["id_wikidata"] for a in attribuzioni]
    if None in ids:
        esito = " Concordanza fra fonti non verificabile: manca un identificativo."
    elif len(set(ids)) == 1 and len({bool(a["qualifica_originale"]) for a in attribuzioni}) == 1:
        esito = " Wikidata indica la stessa persona, senza qualifiche diverse."
    else:
        esito = " ATTENZIONE: le fonti non concordano su autore o qualifica."
    datazioni = [
        {
            "fonte": "met-435809",
            "testo_originale": p.get("objectDate", ""),
            "intervallo": [p.get("objectBeginDate"), p.get("objectEndDate")],
        }
    ] + [
        {"fonte": "wikidata-Q776175", "testo_originale": _valore_wd(a, et), "riferimenti": refs(a)}
        for a in c.get("P571", [])
    ]
    return {
        "titoli": [
            {"fonte": "met-435809", "valore": p["title"], "lingua": "en"},
            {
                "fonte": "wikidata-Q776175",
                "valore": ent.get("labels", {}).get("it", {}).get("value"),
                "lingua": "it",
            },
        ],
        "attribuzioni": attribuzioni,
        "attribuzione_in_evidenza": {
            "fonte": "met-435809",
            "motivazione": "Scheda dell'istituzione che conserva l'opera." + esito,
        },
        "datazioni": datazioni,
        "tecnica": [{"fonte": "met-435809", "valore": p.get("medium")}],
        "dimensioni": [{"fonte": "met-435809", "valore": p.get("dimensions")}],
        "istituzione": [
            {
                "fonte": "met-435809",
                "valore": p.get("repository"),
                "inventario": p.get("accessionNumber"),
                "linea_di_credito": p.get("creditLine"),
            }
        ],
        "identificativi": {
            "met": str(p["objectID"]),
            "wikidata": ent["id"],
            "ulan_artista": p.get("artistULAN_URL", ""),
        },
        "soggetti_wikidata": [
            {"valore": _valore_wd(a, et), "riferimenti": refs(a)} for a in c.get("P180", [])
        ],
        "proprietari_wikidata": [
            {
                "valore": _valore_wd(a, et),
                "qualificatori": {
                    {"P580": "dal", "P582": "fino al"}.get(k, k): v
                    for k, v in _qualificatori_wd(a, et).items()
                },
                "riferimenti": refs(a),
            }
            for a in c.get("P127", [])
        ],
    }


def _verifica_fonti(rif_fonti, fonti, dove):
    """Ogni fonte citata deve esistere ed essere stata letta: niente affermazioni
    appoggiate a testi non consultati."""
    for f in rif_fonti:
        if f["fonte"] not in fonti:
            raise ErroreValidazione(f"{dove}: fonte sconosciuta {f['fonte']!r}")
        if fonti[f["fonte"]].get("lettura") == "non consultato":
            raise ErroreValidazione(f"{dove}: la fonte {f['fonte']!r} non è stata consultata e non può sostenere un'affermazione")


def _verifica_blocchi(blocchi, fonti, dove):
    for b in blocchi:
        if b.get("registro") not in REGISTRI:
            raise ErroreValidazione(f"{dove}: registro non valido {b.get('registro')!r}")
        if not b.get("testo", "").strip():
            raise ErroreValidazione(f"{dove}: testo vuoto")
        _verifica_fonti(b.get("fonti", []), fonti, dove)
        if b["registro"] in ("documentato", "interpretazione") and not b.get("fonti"):
            raise ErroreValidazione(f"{dove}: blocco «{b['registro']}» senza fonti")


# ---------- opere da istituzioni diverse ----------

def manifesto(chiave: str) -> dict:
    p = DATI / "opere" / f"{chiave}.json"
    if p.exists():
        return _leggi(p)
    return {"chiave": chiave, "id": f"met:{chiave}", "istituzione": {"tipo": "met", "id": chiave}, "immagine": f"met_{chiave}"}


def _fonte_immagine(img: dict, ident: str, breve: str) -> dict:
    return {
        ident: {
            "titolo": f"Fotografia {img['file_fotografia']} ({img['larghezza']} × {img['altezza']} px)",
            "breve": breve,
            "categoria": "immagine",
            "tipo": "immagine di riferimento per le osservazioni visive",
            "url": img["url_originale"],
            "consultato": img["acquisita_il"][:10],
            "licenza": img["diritti"]["fotografia"],
            "note": f"{img['vista']}. SHA-256 {img['sha256'][:12]}…",
        }
    }


def registro_fonti_louvre(lv: dict, wd: dict, img: dict, qid: str) -> dict:
    p, acq = lv["payload"], lv["acquisizione"]
    ark = p["arkId"]
    inv = next((o["value"] for o in p.get("objectNumber", []) if o.get("type") == "Numéro principal"), ark)
    aggiornato = (p.get("modified ") or p.get("modified") or "")[:10]
    comune = {
        "url": p["url"],
        "url_dati": acq["url"],
        "consultato": acq["data"][:10],
        "licenza": f"Licence Ouverte Etalab (testi del Louvre, aggiornati il {aggiornato})",
    }
    out = {
        f"louvre-{ark}": {
            **comune,
            "titolo": f"Musée du Louvre, scheda {inv} ({ark})",
            "breve": "Louvre, scheda",
            "categoria": "istituzione",
            "tipo": "scheda istituzionale (dati strutturati)",
            "lettura": "testo completo",
            "note": f"Ultimo aggiornamento della scheda: {aggiornato}. Le fotografie del Louvre (© GrandPalaisRmn) non sono riusate.",
        },
        f"louvre-{ark}-commento": {
            **comune,
            "titolo": "Vincent Delieuvin, commento alla scheda del Louvre (luglio 2021)",
            "breve": "Delieuvin (Louvre), 2021",
            "categoria": "letteratura",
            "tipo": "letteratura critica: commento del conservatore",
            "lettura": "testo completo",
            "note": "Campo «objectHistory» della scheda, firmato dal conservatore.",
        },
        f"wikidata-{qid}": {
            "titolo": f"Wikidata, elemento {qid}",
            "breve": "Wikidata",
            "categoria": "collaborativa",
            "tipo": "base di conoscenza collaborativa",
            "url": f"https://www.wikidata.org/wiki/{qid}",
            "url_dati": wd["acquisizione"]["url"],
            "consultato": wd["acquisizione"]["data"][:10],
            "licenza": "CC0",
        },
    }
    out.update(_fonte_immagine(img, f"foto-{img['id']}", "Fotografia (Commons)"))
    return out


def _attribuzioni_wd(c: dict, et: dict, fonte: str) -> list:
    return [
        {
            "fonte": fonte,
            "autore": _valore_wd(a, et),
            "id_wikidata": a["mainsnak"].get("datavalue", {}).get("value", {}).get("id"),
            "qualifica_originale": "; ".join(f"{k}: {', '.join(v)}" for k, v in _qualificatori_wd(a, et).items()),
            "riferimenti": len(a.get("references", [])),
        }
        for a in c.get("P170", [])
    ]


def _parti_wikidata(ent: dict, et: dict) -> dict:
    c = ent.get("claims", {})
    refs = lambda a: len(a.get("references", []))
    return {
        "soggetti_wikidata": [{"valore": _valore_wd(a, et), "riferimenti": refs(a)} for a in c.get("P180", [])],
        "proprietari_wikidata": [
            {"valore": _valore_wd(a, et),
             "qualificatori": {{"P580": "dal", "P582": "fino al"}.get(k, k): v for k, v in _qualificatori_wd(a, et).items()},
             "riferimenti": refs(a)}
            for a in c.get("P127", [])
        ],
    }


def catalogo_louvre(lv: dict, wd: dict, qid: str) -> dict:
    p = lv["payload"]
    ark = p["arkId"]
    f_lv, f_wd = f"louvre-{ark}", f"wikidata-{qid}"
    ent, et = wd["payload"]["entita"], wd["payload"]["etichette"]
    c = ent.get("claims", {})
    creatore = (p.get("creator") or [{}])[0]
    attribuzioni = [{
        "fonte": f_lv,
        "autore": creatore.get("label"),
        "id_wikidata": creatore.get("wikidata") or None,
        "qualifica_originale": creatore.get("attributionLevel", ""),
    }] + _attribuzioni_wd(c, et, f_wd)
    ids = [a["id_wikidata"] for a in attribuzioni]
    if None in ids:
        esito = " Concordanza fra fonti non verificabile: manca un identificativo."
    elif len(set(ids)) == 1:
        esito = " Wikidata indica la stessa persona."
    else:
        esito = " ATTENZIONE: le fonti non concordano sull'autore."
    data = (p.get("dateCreated") or [{}])[0]
    dim = {d["type"]: d["displayDimension"] for d in p.get("dimension", [])}
    acq = (p.get("acquisitionDetails") or [{}])[0]
    anno_acq = ((acq.get("dates") or [{}])[0]).get("value")
    titoli = [{"fonte": f_lv, "valore": t["value"], "lingua": "fr", "tipo": t.get("type")} for t in p.get("denominationTitle", [])]
    titoli.append({"fonte": f_wd, "valore": ent.get("labels", {}).get("it", {}).get("value"), "lingua": "it"})
    return {
        "titoli": titoli,
        "attribuzioni": attribuzioni,
        "attribuzione_in_evidenza": {"fonte": f_lv, "motivazione": "Scheda dell'istituzione che conserva l'opera." + esito},
        "datazioni": [{"fonte": f_lv, "testo_originale": p.get("displayDateCreated", "").split(":", 1)[-1].strip(),
                       "intervallo": [data.get("startYear"), data.get("endYear")]}]
                     + [{"fonte": f_wd, "testo_originale": _valore_wd(a, et), "riferimenti": len(a.get("references", []))} for a in c.get("P571", [])],
        "tecnica": [{"fonte": f_lv, "valore": p.get("materialsAndTechniques")}],
        "dimensioni": [{"fonte": f_lv, "valore": "; ".join(f"{k}: {v}" for k, v in dim.items())}],
        "istituzione": [{
            "fonte": f_lv,
            "valore": p.get("heldBy"),
            "inventario": ", ".join(o["value"] for o in p.get("objectNumber", [])),
            "linea_di_credito": f"{acq.get('mode', '')} ({anno_acq})" if anno_acq else acq.get("mode", ""),
        }],
        "identificativi": {"louvre": ark, "wikidata": qid},
        **_parti_wikidata(ent, et),
    }


def fonti_bibliografia(chiave: str) -> dict:
    """Registro curato della letteratura: ogni voce dichiara tipo e livello di lettura."""
    p = DATI / "bibliografia" / f"{chiave}.json"
    if not p.exists():
        return {}
    out = {}
    for f in _leggi(p)["fonti"]:
        if f.get("lettura") not in LETTURE:
            raise ErroreValidazione(f"bibliografia {f['id']}: livello di lettura non valido {f.get('lettura')!r}")
        if f.get("categoria") not in CATEGORIE_FONTE:
            raise ErroreValidazione(f"bibliografia {f['id']}: categoria non valida {f.get('categoria')!r}")
        out[f["id"]] = {k: v for k, v in f.items() if k != "id"}
    return out


def bibliografia_museo(manif: dict) -> list:
    if manif["istituzione"]["tipo"] != "louvre":
        return []
    p = _leggi(DATI / "fonti" / "louvre" / f"{manif['istituzione']['id']}.json")["payload"]
    voci = [{"riferimento": _senza_html(b.get("bibliographyRef", "")).replace("&lt;", "<").replace("&gt;", ">"),
             "anno": b.get("bibliographyDate"), "pagine": b.get("bibliographyDetail")} for b in p.get("bibliography", [])]
    return sorted(voci, key=lambda v: str(v["anno"] or ""), reverse=True)


def scheda_persona_wd(qid: str, fonti: dict) -> dict:
    d = _leggi(DATI / "fonti" / "wikidata" / f"{qid}.json")
    e, et = d["payload"]["entita"], d["payload"]["etichette"]
    c = e.get("claims", {})
    anno = lambda k: next((_valore_wd(a, et) for a in c.get(k, [])), None)
    base = scheda_opera_wd(qid, fonti)
    return {"wikidata": qid, "fonte": f"wikidata-{qid}", "nome": base["titolo"],
            "nascita": anno("P569"), "morte": anno("P570"), "immagine": base["immagine"]}


# ---------- Fase 2.5: fonti aggiuntive e opere collegate ----------

def _senza_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def fonti_aggiuntive() -> dict:
    """Altri elementi Wikidata e file Commons acquisiti con importa.py."""
    out = {}
    for p in sorted((DATI / "fonti" / "wikidata").glob("Q*.json")):
        d = _leggi(p)
        e = d["payload"]["entita"]
        lab = (e.get("labels", {}).get("it") or e.get("labels", {}).get("en") or {}).get("value") or p.stem
        out[f"wikidata-{p.stem}"] = {
            "titolo": f"Wikidata, elemento {p.stem} ({lab})",
            "breve": f"Wikidata {p.stem}",
            "categoria": "collaborativa",
            "tipo": "base di conoscenza collaborativa",
            "url": f"https://www.wikidata.org/wiki/{p.stem}",
            "url_dati": d["acquisizione"]["url"],
            "consultato": d["acquisizione"]["data"][:10],
            "licenza": "CC0",
        }
    cartella_q = DATI / "fonti" / "wikidata-sparql"
    for p in sorted(cartella_q.glob("*.json")) if cartella_q.exists() else []:
        d = _leggi(p)
        out[f"wikidata-sparql-{p.stem}"] = {
            "titolo": f"Wikidata, interrogazione SPARQL «{p.stem}» del {d['acquisizione']['data'][:10]}",
            "breve": "Wikidata (query)",
            "categoria": "collaborativa",
            "tipo": "risultato datato di una query su base collaborativa",
            "url": d["acquisizione"]["url"],
            "consultato": d["acquisizione"]["data"][:10],
            "licenza": "CC0",
            "note": f"{len(d['payload']['risultati'])} righe.",
        }
    cartella = DATI / "fonti" / "commons"
    for p in sorted(cartella.glob("*.json")) if cartella.exists() else []:
        d = _leggi(p)
        info = d["payload"]["pagina"]["imageinfo"][0]
        meta = info.get("extmetadata", {})
        v = lambda k: _senza_html((meta.get(k) or {}).get("value", ""))
        out[f"commons-{p.stem}"] = {
            "titolo": f"Wikimedia Commons, {d['payload']['file']}",
            "breve": "Commons",
            "categoria": "immagine",
            "tipo": "riproduzione fotografica",
            "url": info["descriptionurl"],
            "url_dati": d["acquisizione"]["url"],
            "consultato": d["acquisizione"]["data"][:10],
            "licenza": v("LicenseShortName") or "da verificare",
            "note": f"{info['width']} × {info['height']} px. Crediti: {v('Credit')[:160] or 'non indicati'}",
        }
    return out


def _id_commons(nome_file: str) -> str:
    return hashlib.sha1(nome_file.encode("utf-8")).hexdigest()[:12]


def scheda_opera_wd(qid: str, fonti: dict) -> dict:
    """Dati essenziali di un'opera collegata, ciascuno con il conteggio dei riferimenti."""
    p = DATI / "fonti" / "wikidata" / f"{qid}.json"
    if not p.exists():
        raise ErroreValidazione(f"opera collegata {qid}: elemento Wikidata non acquisito")
    d = _leggi(p)
    e, et = d["payload"]["entita"], d["payload"]["etichette"]
    c = e.get("claims", {})
    refs = lambda a: len(a.get("references", []))
    voci = lambda k: [{"valore": _valore_wd(a, et), "riferimenti": refs(a)} for a in c.get(k, [])]
    titolo = (e.get("labels", {}).get("it") or e.get("labels", {}).get("en") or {}).get("value") or qid
    immagine, avvisi = None, []
    file_p18 = [a["mainsnak"]["datavalue"]["value"] for a in c.get("P18", []) if a["mainsnak"].get("datavalue")]
    if file_p18:
        ident = _id_commons(file_p18[0])
        if (WEB / "immagini" / "confronti" / f"{ident}.jpg").exists() and f"commons-{ident}" in fonti:
            immagine = {
                "src": f"immagini/confronti/{ident}.jpg",
                "fonte": f"commons-{ident}",
                "licenza": fonti[f"commons-{ident}"]["licenza"],
                "pagina": fonti[f"commons-{ident}"]["url"],
            }
    if len(file_p18) > 1:
        avvisi.append("Wikidata associa più immagini a questo elemento: quella mostrata è la prima.")
    collezioni = []
    for a in c.get("P195", []):
        q = _qualificatori_wd(a, et)
        valore = _valore_wd(a, et)
        if a["mainsnak"].get("snaktype") == "somevalue":
            valore = f"{q.get('P2868', ['collezione'])[0]}, nome non indicato"
        quando = q.get("P585") or [f"{x}–{y}" for x, y in zip(q.get("P580", ["?"]), q.get("P582", ["?"]))
                                   if "P580" in q or "P582" in q]
        collezioni.append({"valore": valore + (f" ({', '.join(quando)})" if quando else ""), "riferimenti": refs(a)})
    if len({x["valore"] for x in collezioni}) > 1:
        avvisi.append("Wikidata elenca più collezioni, anche di momenti diversi: collocazione attuale da verificare.")
    return {
        "wikidata": qid,
        "fonte": f"wikidata-{qid}",
        "titolo": titolo,
        "autori": voci("P170"),
        "date": voci("P571"),
        "collezioni": collezioni,
        "iconclass": [a["mainsnak"]["datavalue"]["value"] for a in c.get("P1257", []) if a["mainsnak"].get("datavalue")],
        "immagine": immagine,
        "avvisi": avvisi,
    }


def connessioni(object_id: str, qid_opera: str, fonti: dict, ids_annotazioni: set, pubblico: bool) -> list:
    p = DATI / "connessioni" / f"{object_id}.json"
    if not p.exists():
        return []
    dati = _leggi(p)
    origine = dati["origine_predefinita"]
    base_iconclass = set(scheda_opera_wd(qid_opera, fonti)["iconclass"]) if (DATI / "fonti" / "wikidata" / f"{qid_opera}.json").exists() else set()
    out, visti = [], set()
    for k in dati["connessioni"]:
        dove = f"connessione {k['id']}"
        if k["id"] in visti:
            raise ErroreValidazione(f"{dove}: identificativo duplicato")
        visti.add(k["id"])
        if k["tipo"] not in TIPI_CONNESSIONE:
            raise ErroreValidazione(f"{dove}: tipo non valido {k['tipo']!r}")
        if k["stato"] not in STATI:
            raise ErroreValidazione(f"{dove}: stato non valido {k['stato']!r}")
        _verifica_blocchi(k["blocchi"], fonti, dove)
        registri = {b["registro"] for b in k["blocchi"]}
        # Il tipo dichiarato deve essere sostenuto dai blocchi.
        if k["tipo"] == "documentata" and not any(b["registro"] == "documentato" and b.get("fonti") for b in k["blocchi"]):
            raise ErroreValidazione(f"{dove}: una connessione documentata richiede un blocco «documentato» con fonti")
        if k["tipo"] == "interpretativa" and not registri & {"ipotesi", "interpretazione"}:
            raise ErroreValidazione(f"{dove}: una connessione interpretativa richiede un'ipotesi o un'interpretazione")
        if k["tipo"] == "algoritmica" and "calcolo" not in k:
            raise ErroreValidazione(f"{dove}: una connessione algoritmica richiede il metodo di calcolo")
        for a in k.get("annotazioni", []):
            if a not in ids_annotazioni:
                raise ErroreValidazione(f"{dove}: annotazione inesistente {a!r}")
        if pubblico and k["stato"] != "pubblicato":
            continue
        voce = {
            **{x: k[x] for x in ("id", "tipo", "relazione", "titolo", "stato")},
            "annotazioni": k.get("annotazioni", []),
            "blocchi": k["blocchi"],
            "origine": k.get("origine", origine),
            "revisione": k.get("revisione"),
            "opere": [scheda_opera_wd(q, fonti) for q in k.get("opere", [])],
        }
        if k["tipo"] == "algoritmica" and k["calcolo"]["metodo"] == "sparql_basati_su":
            righe = _leggi(DATI / "fonti" / "wikidata-sparql" / f"{k['calcolo']['snapshot']}.json")["payload"]["risultati"]
            opere: dict[str, dict] = {}
            utile = lambda b, c: b.get(c, {}).get("value", "") if not b.get(c, {}).get("value", "").startswith("http") else ""
            for b in righe:
                q = b["item"]["value"].rsplit("/", 1)[-1]
                o = opere.setdefault(q, {"wikidata": q, "titolo": utile(b, "itemLabel") or q, "autori": set(), "anni": set(), "collezioni": set()})
                if utile(b, "creatorLabel"):
                    o["autori"].add(utile(b, "creatorLabel"))
                if b.get("data"):
                    o["anni"].add(int(b["data"]["value"][:5].lstrip("+").rstrip("-")))
                if utile(b, "collezioneLabel"):
                    o["collezioni"].add(utile(b, "collezioneLabel"))
            elenco = sorted(
                ({**o, "autori": sorted(o["autori"]), "anno": min(o["anni"]) if o["anni"] else None, "collezioni": sorted(o["collezioni"])}
                 for o in opere.values()),
                key=lambda o: (o["anno"] is None, o["anno"] or 0))
            for o in elenco:
                o.pop("anni")
            secoli: dict[str, int] = {}
            for o in elenco:
                nomi_secoli = {14: "Quattrocento", 15: "Cinquecento", 16: "Seicento", 17: "Settecento",
                               18: "Ottocento", 19: "Novecento", 20: "Duemila"}
                chiave_s = nomi_secoli.get(o["anno"] // 100, f"anno {o['anno']}") if o["anno"] else "senza data"
                secoli[chiave_s] = secoli.get(chiave_s, 0) + 1
            voce["calcolo"] = {
                **k["calcolo"],
                "elenco": elenco,
                "per_secolo": secoli,
                "spiegazione": (f"Wikidata collega {len(elenco)} elementi alla Gioconda con «basato su» (P144). "
                                "Le immagini non sono mostrate: molte riproduzioni hanno licenze da verificare e alcune opere moderne sono protette."),
            }
            out.append(voce)
            continue
        if k["tipo"] == "algoritmica":
            calc = k["calcolo"]
            if calc["metodo"] != "iconclass_condivise":
                raise ErroreValidazione(f"{dove}: metodo di calcolo sconosciuto {calc['metodo']!r}")
            risultati = []
            for q in calc["candidati"]:
                altra = scheda_opera_wd(q, fonti)
                comuni = sorted(base_iconclass & set(altra["iconclass"]))
                if len(comuni) >= calc["soglia"]:
                    unione = base_iconclass | set(altra["iconclass"])
                    risultati.append({
                        "opera": altra,
                        "in_comune": comuni,
                        "jaccard": round(len(comuni) / len(unione), 2),
                    })
            risultati.sort(key=lambda r: (-len(r["in_comune"]), -r["jaccard"]))
            voce["calcolo"] = {
                **calc,
                "notazioni_opera": sorted(base_iconclass),
                "esaminati": len(calc["candidati"]),
                "risultati": risultati,
                "spiegazione": (
                    f"Su {len(calc['candidati'])} opere esaminate, {len(risultati)} condividono almeno "
                    f"{calc['soglia']} notazioni Iconclass con quest'opera. Indice di Jaccard = notazioni in comune / notazioni totali delle due opere."
                ),
            }
        out.append(voce)
    return out


# ---------- Fase 2.5: contenuti esterni (ArtNotes Pulse) ----------

def _anni_da(iso: str | None, adesso: datetime) -> float | None:
    if not iso:
        return None
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (adesso - t).days / 365.25


def _componenti(c: dict, m: dict, percorso: str, adesso: datetime) -> dict | None:
    """Componenti del punteggio, ciascuna fra 0 e 1. None se il contenuto non è adatto al percorso."""
    if percorso not in c["percorsi"]:
        return None
    d = m.get("durata_s") or 0
    if percorso == "curioso":
        intento = 1.0 if d <= 360 else 0.6 if d <= 900 else 0.2
    elif percorso == "studio":
        intento = 1.0 if d >= 300 else 0.6 if d >= 120 else 0.3
    else:
        intento = 1.0 if c["relazione"] in ("analogia", "contesto") or c["categoria"] == "cultura_pop" else 0.6
    anni = _anni_da(m.get("pubblicato_il"), adesso)
    freschezza = 0.5 if anni is None else max(0.2, 1 - anni / 10)
    viste = m.get("visualizzazioni")
    interesse = 0.0 if viste is None else min(1.0, math.log10(viste + 1) / 6)
    return {
        "pertinenza": PERTINENZA[c["relazione"]],
        "qualita": AFFIDABILITA[c["affidabilita"]][0],
        "intento": intento,
        "freschezza": round(freschezza, 2),
        "interesse": round(interesse, 2),
    }


def classifica(contenuti: list, percorso: str, adesso: datetime) -> list:
    """Ordinamento avido: a ogni passo sceglie il punteggio più alto, con la
    diversità calcolata rispetto ai canali già scelti."""
    candidati = []
    for c in contenuti:
        comp = _componenti(c, c, percorso, adesso)
        if comp:
            candidati.append((c, comp))
    scelti, canali = [], set()
    while candidati:
        migliori = []
        for c, comp in candidati:
            tutte = {**comp, "diversita": 0.0 if c["canale_id"] in canali else 1.0}
            punteggio = sum(PESI[k] * v for k, v in tutte.items())
            migliori.append((round(punteggio, 3), c, tutte))
        migliori.sort(key=lambda x: (-x[0], x[1]["video_id"]))
        punteggio, c, tutte = migliori[0]
        scelti.append({"id": c["video_id"], "punteggio": punteggio, "componenti": tutte})
        canali.add(c["canale_id"])
        candidati = [x for x in candidati if x[0]["video_id"] != c["video_id"]]
    return scelti


def pulse(object_id: str, ids_annotazioni: set, pubblico: bool, adesso: datetime | None = None) -> dict:
    adesso = adesso or datetime.now(timezone.utc)
    politica = (
        "ArtNotes Pulse segnala contenuti pubblici di terzi. Non sono contenuti di ArtNotes e non sono verificati "
        "scientificamente: ogni suggerimento dice perché è stato scelto e che cosa lo collega all'opera. "
        "La popolarità pesa poco (5%) e non equivale ad accuratezza. I video non sono incorporati: "
        "i link aprono la piattaforma originale. Le miniature sono caricate dai server di YouTube."
    )
    vuoto = {"politica": politica, "contenuti": [], "selezioni": {p: [] for p in PERCORSI}, "conteggi": {}, "pesi": PESI}
    f = DATI / "esterni" / f"{object_id}.json"
    if not f.exists():
        return {**vuoto, "stato_fonte": "assente"}
    cura = _leggi(f)
    fm = DATI / "esterni" / "youtube" / f"{object_id}.metadati.json"
    meta = _leggi(fm)["video"] if fm.exists() else None
    giudizio_def = cura.get("giudizio_predefinito")
    conteggi = {"curati": 0, "respinti": 0, "non_disponibili": 0, "da_ricontrollare": 0, "non_pubblicati": 0}
    contenuti, visti = [], set()
    for c in cura["contenuti"]:
        vid = c.get("video_id", "")
        dove = f"contenuto esterno {vid}"
        if vid in visti:
            raise ErroreValidazione(f"{dove}: duplicato")
        visti.add(vid)
        if c.get("piattaforma") != "youtube" or not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            raise ErroreValidazione(f"{dove}: piattaforma o identificativo non validi")
        if c["relazione"] not in RELAZIONI_ESTERNE:
            raise ErroreValidazione(f"{dove}: relazione non valida {c['relazione']!r}")
        if c["stato"] not in STATI_ESTERNI:
            raise ErroreValidazione(f"{dove}: stato non valido {c['stato']!r}")
        if c["affidabilita"] not in AFFIDABILITA or c["categoria"] not in CATEGORIE_PULSE:
            raise ErroreValidazione(f"{dove}: affidabilità o categoria non valide")
        if not set(c["percorsi"]) <= set(PERCORSI):
            raise ErroreValidazione(f"{dove}: percorso sconosciuto")
        if not c.get("motivazione", "").strip() or not c.get("evidenza"):
            raise ErroreValidazione(f"{dove}: ogni classificazione richiede motivazione ed evidenza")
        if c["relazione"] == "falso_positivo" and c["stato"] != "respinto":
            raise ErroreValidazione(f"{dove}: un falso positivo può essere solo respinto")
        for a in c["annotazioni"]:
            if a["id"] not in ids_annotazioni:
                raise ErroreValidazione(f"{dove}: annotazione inesistente {a['id']!r}")
            if not a.get("motivazione", "").strip():
                raise ErroreValidazione(f"{dove}: il collegamento a {a['id']} richiede una motivazione")
        if c["stato"] == "respinto":
            conteggi["respinti"] += 1
            continue
        conteggi["curati"] += 1
        if meta is None:
            continue
        m = meta.get(vid)
        if m is None:
            # Nessun video senza metadati restituiti dalla piattaforma: niente risultati inventati.
            raise ErroreValidazione(f"{dove}: nessun metadato verificato (eseguire youtube.py verifica)")
        if not m.get("disponibile"):
            conteggi["non_disponibili"] += 1
            continue
        verificato = datetime.fromisoformat(m["verificato_il"])
        scaduto = adesso - verificato > timedelta(days=VALIDITA_ESTERNI_GIORNI)
        if scaduto:
            conteggi["da_ricontrollare"] += 1
        if pubblico and (c["stato"] != "pubblicato" or scaduto):
            conteggi["non_pubblicati"] += 1
            continue
        contenuti.append({
            "piattaforma": "youtube",
            "video_id": vid,
            # URL costruito dall'identificativo, mai preso dal testo della cura.
            "url": f"https://www.youtube.com/watch?v={vid}",
            "titolo": m["titolo"],
            "canale": m["canale"],
            "canale_id": m["canale_id"],
            "canale_url": f"https://www.youtube.com/channel/{m['canale_id']}",
            "durata_s": m.get("durata_s"),
            "lingua": m.get("lingua"),
            "pubblicato_il": m.get("pubblicato_il"),
            "visualizzazioni": m.get("visualizzazioni"),
            "miniatura": m.get("miniatura") if (m.get("miniatura") or "").startswith("https://i.ytimg.com/") else None,
            "verificato_il": m["verificato_il"],
            "da_ricontrollare": scaduto,
            "relazione": c["relazione"],
            "relazione_testo": RELAZIONI_ESTERNE[c["relazione"]],
            "evidenza": c["evidenza"],
            "motivazione": c["motivazione"],
            "affidabilita": c["affidabilita"],
            "affidabilita_testo": AFFIDABILITA[c["affidabilita"]][1],
            "avvertenze": c.get("avvertenze", []),
            "categoria": c["categoria"],
            "categoria_testo": CATEGORIE_PULSE[c["categoria"]],
            "percorsi": c["percorsi"],
            "annotazioni": c["annotazioni"],
            "stato": c["stato"],
            "giudizio": c.get("giudizio", giudizio_def),
        })
    stato_fonte = "metadati_mancanti" if meta is None else "ok"
    return {
        **vuoto,
        "stato_fonte": stato_fonte,
        "verificato_il": _leggi(fm)["verificato_il"] if meta is not None else None,
        "contenuti": contenuti,
        "selezioni": {p: classifica(contenuti, p, adesso) for p in PERCORSI},
        "conteggi": conteggi,
    }


# ---------- Fase 2.5: percorsi ----------

def certezza(b: dict, registro_fonti: dict | None = None) -> dict:
    """Grado di certezza di un blocco, derivato da registro e categoria delle fonti (§4.2)."""
    r = b["registro"]
    if r == "lacuna":
        return {"livello": "non_nota", "testo": "Non nota: lacuna dichiarata"}
    if r == "ipotesi":
        return {"livello": "proposta", "testo": "Proposta, non documentata"}
    if r == "osservazione":
        return {"livello": "verificabile", "testo": "Verificabile guardando l'immagine"}
    fonti = b.get("fonti", [])
    registro_fonti = registro_fonti or {}
    cat = lambda f: registro_fonti.get(f["fonte"], {}).get("categoria") or (
        "istituzione" if f["fonte"].startswith(("met-", "louvre-")) else
        "collaborativa" if f["fonte"].startswith("wikidata-") else None)
    categorie = {cat(f) for f in fonti}
    autorevoli = categorie & {"istituzione", "letteratura", "scientifica", "primaria"}
    # Fonti indipendenti: esclusi i dati collaborativi e le immagini; scheda e commento dello stesso museo contano uno.
    indipendenti = len({f["fonte"].split("-commento")[0] for f in fonti if cat(f) not in ("collaborativa", "immagine")})
    if not autorevoli:
        return {"livello": "da_verificare", "testo": "Dato di una base collaborativa senza riferimenti: da verificare"}
    if r == "interpretazione" and autorevoli == {"istituzione"} and "collaborativa" in categorie:
        return {"livello": "da_verificare", "testo": "Classificazione di catalogo, in parte senza riferimenti"}
    if indipendenti >= 2:
        return {"livello": "concorde", "testo": f"{indipendenti} fonti indipendenti concordano"}
    if "letteratura" in categorie or "scientifica" in categorie:
        return {"livello": "letteratura", "testo": "Sostenuto dalla letteratura"}
    if "primaria" in categorie:
        return {"livello": "primaria", "testo": "Attestato da una fonte d'epoca"}
    if "istituzione" in categorie:
        return {"livello": "istituzionale", "testo": "Dato dell'istituzione che conserva l'opera"}
    return {"livello": "attribuito", "testo": "Attribuito a una fonte"}


# ---------- racconto e visita guidata ----------

def racconto(chiave: str, fonti: dict, annotazioni: dict, pubblico: bool) -> dict | None:
    """Racconto a scene: ogni frase porta registro e fonti; può inquadrare una regione,
    far comparire un'etichetta o uscire dal quadro verso una persona o un'altra opera."""
    p = DATI / "racconti" / f"{chiave}.json"
    if not p.exists():
        return None
    r = _leggi(p)
    if r["stato"] not in STATI:
        raise ErroreValidazione("racconto: stato non valido")
    nota = 0
    scene, viste = [], set()
    for s in r["scene"]:
        dove = f"racconto, scena {s.get('id')}"
        if s["id"] in viste:
            raise ErroreValidazione(f"{dove}: identificativo duplicato")
        viste.add(s["id"])
        inq = s.get("inquadra", {"tipo": "intera"})
        if inq["tipo"] == "regione" and inq.get("regione") not in annotazioni:
            raise ErroreValidazione(f"{dove}: regione inesistente {inq.get('regione')!r}")
        frasi = []
        for i, fr in enumerate(s["frasi"]):
            dove_f = f"{dove}, frase {i + 1}"
            if fr.get("r") not in REGISTRI_FRASE:
                raise ErroreValidazione(f"{dove_f}: registro non valido {fr.get('r')!r}")
            if not fr.get("t", "").strip():
                raise ErroreValidazione(f"{dove_f}: testo vuoto")
            _verifica_fonti(fr.get("f", []), fonti, dove_f)
            if fr["r"] in ("documentato", "interpretazione") and not fr.get("f"):
                raise ErroreValidazione(f"{dove_f}: frase «{fr['r']}» senza fonti")
            if fr.get("a") and fr["a"] not in annotazioni:
                raise ErroreValidazione(f"{dove_f}: regione inesistente {fr['a']!r}")
            voce = dict(fr)
            if fr.get("f"):
                nota += 1
                voce["nota"] = nota
                voce["certezza"] = certezza({"registro": fr["r"] if fr["r"] != "raccordo" else "documentato", "fonti": fr["f"]}, fonti)
            if fr.get("a"):
                voce["etichetta"] = fr.get("etichetta") or annotazioni[fr["a"]]["titolo"]
            if fr.get("fuori"):
                fu = fr["fuori"]
                if fu["tipo"] not in ("persona", "opera"):
                    raise ErroreValidazione(f"{dove_f}: uscita dal quadro di tipo sconosciuto")
                scheda = scheda_persona_wd(fu["wikidata"], fonti) if fu["tipo"] == "persona" else scheda_opera_wd(fu["wikidata"], fonti)
                voce["fuori"] = {**fu, "scheda": scheda}
            frasi.append(voce)
        usate = sorted({f["fonte"] for fr in frasi for f in fr.get("f", [])})
        scene.append({**{k: v for k, v in s.items() if k != "frasi"}, "inquadra": inq, "frasi": frasi, "fonti_scena": usate})
    if pubblico and r["stato"] != "pubblicato":
        return None
    return {**{k: v for k, v in r.items() if k != "scene"}, "scene": scene, "note_totali": nota}


def percorsi(object_id: str, blocchi: dict, annotazioni: dict, ids_connessioni: set,
             ids_esterni: set, pubblico: bool, fonti: dict | None = None, ids_scene: set = frozenset()) -> list:
    p = DATI / "percorsi" / f"{object_id}.json"
    if not p.exists():
        return []
    dati = _leggi(p)
    origine = dati["origine_predefinita"]
    out = []
    for perc in dati["percorsi"]:
        if perc["id"] not in PERCORSI:
            raise ErroreValidazione(f"percorso sconosciuto {perc['id']!r}")
        if perc["stato"] not in STATI:
            raise ErroreValidazione(f"percorso {perc['id']}: stato non valido")
        tappe, viste = [], set()
        for t in perc["tappe"]:
            dove = f"percorso {perc['id']}, tappa {t.get('id')}"
            if t["id"] in viste:
                raise ErroreValidazione(f"{dove}: identificativo duplicato")
            viste.add(t["id"])
            if t["tipo"] not in TIPI_TAPPA:
                raise ErroreValidazione(f"{dove}: tipo non valido {t['tipo']!r}")
            richiesti = {
                "scelta": ("domanda", "scelte"), "scopri": ("annotazione",), "scrivi": ("consegna", "nota"),
                "leggi": ("blocchi",), "evidenze": ("righe",), "connessioni": ("connessioni",),
                "pulse": (), "rielabora": ("consegna", "nota"), "scena": ("scena",),
            }[t["tipo"]]
            for campo in richiesti:
                if not t.get(campo):
                    raise ErroreValidazione(f"{dove}: campo obbligatorio mancante {campo!r}")
            rif_annot = ([t["annotazione"]] if t.get("annotazione") else []) + t.get("scelte", [])
            rif_blocchi = t.get("blocchi", [])
            for r in t.get("righe", []):
                (rif_annot if r in annotazioni else rif_blocchi).append(r)
            for a in rif_annot:
                if a not in annotazioni:
                    raise ErroreValidazione(f"{dove}: annotazione inesistente {a!r}")
            for b in rif_blocchi:
                if b not in blocchi:
                    raise ErroreValidazione(f"{dove}: blocco inesistente {b!r}")
            for k in t.get("connessioni", []):
                if k not in ids_connessioni:
                    raise ErroreValidazione(f"{dove}: connessione inesistente {k!r}")
            if t["tipo"] == "scena" and t["scena"] not in ids_scene:
                raise ErroreValidazione(f"{dove}: scena del racconto inesistente {t['scena']!r}")
            if t.get("pulse_categoria") and t["pulse_categoria"] not in CATEGORIE_PULSE:
                raise ErroreValidazione(f"{dove}: categoria Pulse sconosciuta")
            voce = dict(t)
            if t["tipo"] == "evidenze":
                righe = []
                for r in t["righe"]:
                    if r in annotazioni:
                        a = annotazioni[r]
                        for b in a["blocchi"]:
                            righe.append({"rif": r, "dettaglio": r, "titolo": a["titolo"], "registro": b["registro"],
                                          "testo": b["testo"], "fonti": b.get("fonti", []), "certezza": certezza(b, fonti)})
                    else:
                        b = blocchi[r]
                        righe.append({"rif": r, "dettaglio": None, "titolo": None, "registro": b["registro"],
                                      "testo": b["testo"], "fonti": b.get("fonti", []), "certezza": certezza(b, fonti)})
                voce["righe_risolte"] = righe
            tappe.append(voce)
        if pubblico and perc["stato"] != "pubblicato":
            continue
        out.append({**{k: perc[k] for k in ("id", "titolo", "invito", "durata", "stato")},
                    "origine": perc.get("origine", origine), "tappe": tappe})
    return out


def componi(object_id: str, pubblico: bool = False) -> dict:
    man = manifesto(object_id)
    ist = man["istituzione"]
    img = _leggi(DATI / "immagini" / f"{man['immagine']}.json")
    if ist["tipo"] == "met":
        met = _leggi(DATI / "fonti" / "met" / f"{ist['id']}.json")
        qid = met["payload"]["objectWikidata_URL"].rsplit("/", 1)[-1]
        wd = _leggi(DATI / "fonti" / "wikidata" / f"{qid}.json")
        base = registro_fonti(met, wd, img)
        cat = catalogo(met, wd)
        base_ids = {"met-435809", f"wikidata-{qid}", "foto-met-DP119115"}
        testo_catalogo = "Dati essenziali presenti (Met, Wikidata)."
    elif ist["tipo"] == "louvre":
        lv = _leggi(DATI / "fonti" / "louvre" / f"{ist['id']}.json")
        qid = man["wikidata"]
        wd = _leggi(DATI / "fonti" / "wikidata" / f"{qid}.json")
        base = registro_fonti_louvre(lv, wd, img, qid)
        cat = catalogo_louvre(lv, wd, qid)
        base_ids = {f"louvre-{ist['id']}", f"wikidata-{qid}", f"foto-{img['id']}"}
        testo_catalogo = "Dati essenziali presenti (Louvre, Wikidata)."
    else:
        raise ErroreValidazione(f"istituzione non supportata {ist['tipo']!r}")
    contenuti = _leggi(DATI / "contenuti" / f"{object_id}.json")
    annot = _leggi(DATI / "annotazioni" / f"{object_id}.json")
    fonti = {**fonti_aggiuntive(), **fonti_bibliografia(object_id), **base}

    def visibile(stato):
        if stato not in STATI:
            raise ErroreValidazione(f"stato non valido {stato!r}")
        return stato == "pubblicato" or not pubblico

    origine_c = contenuti["origine_predefinita"]
    sezioni = []
    for s in contenuti["sezioni"]:
        _verifica_blocchi(s["blocchi"], fonti, f"sezione {s['id']}")
        blocchi = [
            {**b, "origine": b.get("origine", origine_c), "revisione": b.get("revisione")}
            for b in s["blocchi"]
            if visibile(b["stato"])
        ]
        sezioni.append({**s, "blocchi": blocchi})

    rif = annot["immagine_riferimento"]
    stessa_immagine = rif["sha256"] == img["sha256"]
    origine_a = annot["origine_predefinita"]
    annotazioni = []
    for a in annot["annotazioni"]:
        if a["categoria"] not in CATEGORIE:
            raise ErroreValidazione(f"annotazione {a['id']}: categoria {a['categoria']!r}")
        m = RE_REGIONE.match(a["regione"])
        if not m:
            raise ErroreValidazione(f"annotazione {a['id']}: regione non valida")
        x, y, w, h = map(float, m.groups())
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > 100.001 or y + h > 100.001:
            raise ErroreValidazione(f"annotazione {a['id']}: regione fuori dall'immagine")
        _verifica_blocchi(a["blocchi"], fonti, f"annotazione {a['id']}")
        if not visibile(a["stato"]):
            continue
        annotazioni.append(
            {
                **a,
                "regione_normalizzata": {"x": x / 100, "y": y / 100, "w": w / 100, "h": h / 100},
                "immagine_riferimento": rif["id"],
                "verifica_immagine": "valida" if stessa_immagine else "da_riverificare",
                "origine": a.get("origine", origine_a),
                "revisione": a.get("revisione"),
            }
        )

    # Fase 2.5: livelli di presentazione e collegamenti, sulla stessa base di conoscenza.
    tutte_annot = {a["id"]: a for a in annot["annotazioni"]}
    tutti_blocchi_sez = {b["id"]: b for s in contenuti["sezioni"] for b in s["blocchi"] if "id" in b}
    conn = connessioni(object_id, qid, fonti, set(tutte_annot), pubblico)
    ids_conn_tutte = {k["id"] for k in _leggi(DATI / "connessioni" / f"{object_id}.json")["connessioni"]} \
        if (DATI / "connessioni" / f"{object_id}.json").exists() else set()
    esterni = pulse(object_id, set(tutte_annot), pubblico)
    racc = racconto(object_id, fonti, tutte_annot, pubblico)
    ids_scene = {sc["id"] for sc in _leggi(DATI / "racconti" / f"{object_id}.json")["scene"]} \
        if (DATI / "racconti" / f"{object_id}.json").exists() else set()
    perc = percorsi(object_id, tutti_blocchi_sez, tutte_annot, ids_conn_tutte,
                    {c["video_id"] for c in esterni["contenuti"]}, pubblico, fonti, ids_scene)

    tutti_blocchi = [b for s in sezioni for b in s["blocchi"]] + [
        b for a in annotazioni for b in a["blocchi"]
    ]
    revisionati = [x for x in tutti_blocchi if x.get("revisione")]
    n_interp = sum(1 for b in tutti_blocchi if b["registro"] == "interpretazione")
    n_critiche = sum(
        1 for b in tutti_blocchi
        if b["registro"] == "interpretazione"
        and any(fonti.get(f["fonte"], {}).get("categoria") in ("letteratura", "scientifica") for f in b.get("fonti", []))
    )
    copertura = {
        "catalogo": testo_catalogo,
        "approfondimenti_documentati": (
            f"{n_interp} {'interpretazione attribuita' if n_interp == 1 else 'interpretazioni attribuite'} a fonti, "
            f"{n_critiche} da letteratura critica."
            + (" Testo critico ancora assente." if not n_critiche else "")
        ),
        "annotazioni": f"{len(annotazioni)} regioni, nessuna revisionata."
        if not any(a.get("revisione") for a in annotazioni)
        else f"{len(annotazioni)} regioni.",
        "revisione_umana": "Nessun contenuto revisionato."
        if not revisionati
        else f"{len(revisionati)} blocchi revisionati.",
    }

    return {
        "schema": "artnotes-prototipo/0.1",
        "generato_il": datetime.now().isoformat(timespec="seconds"),
        "modalita": "pubblico" if pubblico else "anteprima_redazionale",
        "opera": {"id": man["id"], "chiave": object_id, "catalogo": cat},
        "immagine": {
            k: img[k]
            for k in (
                "id", "sha256", "larghezza", "altezza", "a_colori", "vista",
                "diritti", "crediti", "dzi", "file_fotografia",
            )
        },
        "copertura": copertura,
        "sezioni": sezioni,
        "annotazioni": annotazioni,
        "racconto": racc,
        "percorsi": perc,
        "connessioni": conn,
        "pulse": esterni,
        "fonti": _fonti_citate(fonti, sezioni, annotazioni, conn, racc, base_ids),
        "bibliografia_museo": bibliografia_museo(man),
    }


def _fonti_citate(fonti, sezioni, annotazioni, conn, racc, base_ids) -> dict:
    """Solo le fonti effettivamente citate, più quelle di catalogo e dell'immagine."""
    usate = set(base_ids)
    if racc:
        for sc in racc["scene"]:
            for fr in sc["frasi"]:
                usate |= {f["fonte"] for f in fr.get("f", [])}
                if fr.get("fuori"):
                    usate.add(fr["fuori"]["scheda"]["fonte"])
                    if fr["fuori"]["scheda"].get("immagine"):
                        usate.add(fr["fuori"]["scheda"]["immagine"]["fonte"])
    for gruppo in ([b for s in sezioni for b in s["blocchi"]], [b for a in annotazioni for b in a["blocchi"]],
                   [b for k in conn for b in k["blocchi"]]):
        for b in gruppo:
            usate |= {f["fonte"] for f in b.get("fonti", [])}
    for k in conn:
        for o in k["opere"] + [r["opera"] for r in k.get("calcolo", {}).get("risultati", [])]:
            usate.add(o["fonte"])
            if o["immagine"]:
                usate.add(o["immagine"]["fonte"])
    return {k: v for k, v in fonti.items() if k in usate}


def scrivi(chiave: str, pubblico: bool) -> dict:
    scheda = componi(chiave, pubblico)
    USCITA.mkdir(parents=True, exist_ok=True)
    nome = f"{chiave}{'.pubblico' if pubblico else ''}.json"
    (USCITA / nome).write_text(json.dumps(scheda, ensure_ascii=False, indent=2), encoding="utf-8")
    scene = len(scheda["racconto"]["scene"]) if scheda["racconto"] else 0
    print(
        f"scheda scritta: web/api/opere/{nome} - {len(scheda['annotazioni'])} annotazioni - "
        f"{sum(len(s['blocchi']) for s in scheda['sezioni'])} blocchi - {scene} scene - modalita {scheda['modalita']}"
    )
    return scheda


def scrivi_tutte() -> None:
    """Compone tutte le opere con un manifesto e scrive l'indice letto dal selettore."""
    indice = []
    for p in sorted((DATI / "opere").glob("*.json")):
        chiave = p.stem
        s = scrivi(chiave, False)
        scrivi(chiave, True)
        c = s["opera"]["catalogo"]
        titolo_it = next((t["valore"] for t in c["titoli"] if t.get("lingua") == "it" and t.get("valore")), c["titoli"][0]["valore"])
        autore_wd = next((a["autore"] for a in c["attribuzioni"] if a["fonte"].startswith("wikidata-")), c["attribuzioni"][0]["autore"])
        indice.append({"chiave": chiave, "id": s["opera"]["id"], "titolo": titolo_it, "autore": autore_wd,
                       "data": c["datazioni"][0]["testo_originale"]})
    (USCITA / "indice.json").write_text(json.dumps({"opere": indice}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("indice scritto:", ", ".join(o["chiave"] for o in indice))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--tutte" in sys.argv:
        scrivi_tutte()
    elif len(args) == 1:
        scrivi(args[0], "--pubblico" in sys.argv)
    else:
        print(__doc__)
        sys.exit(1)
