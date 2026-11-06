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

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
USCITA = RADICE / "web" / "api" / "opere"

REGISTRI = {"documentato", "interpretazione", "osservazione", "ipotesi", "lacuna"}
CATEGORIE = {"osservazione", "iconografia", "composizione", "tecnica"}
STATI = {"bozza", "in_revisione", "pubblicato", "da_aggiornare"}
RE_REGIONE = re.compile(r"^xywh=percent:([\d.]+),([\d.]+),([\d.]+),([\d.]+)$")


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
            "tipo": "scheda istituzionale (dati strutturati)",
            "url": met["payload"]["objectURL"],
            "url_dati": acq_met["url"],
            "consultato": acq_met["data"][:10],
            "licenza": "CC0 (metadati)",
            "note": f"metadataDate della fonte: {met['payload'].get('metadataDate', '')[:10]}",
        },
        "wikidata-Q776175": {
            "titolo": "Wikidata, elemento Q776175",
            "tipo": "base di conoscenza collaborativa",
            "url": "https://www.wikidata.org/wiki/Q776175",
            "url_dati": acq_wd["url"],
            "consultato": acq_wd["data"][:10],
            "licenza": "CC0",
            "note": "Molte asserzioni non hanno riferimenti: vanno lette come dato da verificare.",
        },
        "iconclass": {
            "titolo": "Iconclass, notazioni 47I14, 23E43, 23D43, 41C, 25H",
            "tipo": "sistema di classificazione iconografica",
            "url": "https://iconclass.org/47I14",
            "consultato": "2026-11-06",
            "licenza": "da verificare",
            "note": "Etichette italiane lette da iconclass.org. Le notazioni provengono da Wikidata.",
        },
        "foto-met-DP119115": {
            "titolo": f"Fotografia {img['file_fotografia']} ({img['larghezza']} × {img['altezza']} px)",
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


def _verifica_blocchi(blocchi, fonti, dove):
    for b in blocchi:
        if b.get("registro") not in REGISTRI:
            raise ErroreValidazione(f"{dove}: registro non valido {b.get('registro')!r}")
        if not b.get("testo", "").strip():
            raise ErroreValidazione(f"{dove}: testo vuoto")
        for f in b.get("fonti", []):
            if f["fonte"] not in fonti:
                raise ErroreValidazione(f"{dove}: fonte sconosciuta {f['fonte']!r}")
        if b["registro"] == "documentato" and not b.get("fonti"):
            raise ErroreValidazione(f"{dove}: blocco «documentato» senza fonti")


def componi(object_id: str, pubblico: bool = False) -> dict:
    met = _leggi(DATI / "fonti" / "met" / f"{object_id}.json")
    qid = met["payload"]["objectWikidata_URL"].rsplit("/", 1)[-1]
    wd = _leggi(DATI / "fonti" / "wikidata" / f"{qid}.json")
    img = _leggi(DATI / "immagini" / f"met_{object_id}.json")
    contenuti = _leggi(DATI / "contenuti" / f"{object_id}.json")
    annot = _leggi(DATI / "annotazioni" / f"{object_id}.json")
    fonti = registro_fonti(met, wd, img)

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

    tutti_blocchi = [b for s in sezioni for b in s["blocchi"]] + [
        b for a in annotazioni for b in a["blocchi"]
    ]
    revisionati = [x for x in tutti_blocchi if x.get("revisione")]
    copertura = {
        "catalogo": "Dati essenziali presenti (Met, Wikidata).",
        "approfondimenti_documentati": (
            f"{sum(1 for b in tutti_blocchi if b['registro'] == 'interpretazione')} interpretazioni "
            "con fonte bibliografica. Testo critico ancora assente."
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
        "opera": {"id": f"met:{object_id}", "catalogo": catalogo(met, wd)},
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
        "fonti": fonti,
    }


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        sys.exit(1)
    pubblico = "--pubblico" in sys.argv
    scheda = componi(args[0], pubblico)
    USCITA.mkdir(parents=True, exist_ok=True)
    nome = f"{args[0]}{'.pubblico' if pubblico else ''}.json"
    (USCITA / nome).write_text(json.dumps(scheda, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"scheda scritta: web/api/opere/{nome} - {len(scheda['annotazioni'])} annotazioni - "
        f"{sum(len(s['blocchi']) for s in scheda['sezioni'])} blocchi - modalita {scheda['modalita']}"
    )
