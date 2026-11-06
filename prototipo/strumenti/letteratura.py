"""Connettore bibliografico: letteratura accademica, testi universitari e fonti primarie.

Uso:
    python strumenti/letteratura.py openalex <chiave>             # OpenAlex (CC0): articoli, libri, tesi
    python strumenti/letteratura.py hal <chiave>                  # HAL, archivio aperto francese
    python strumenti/letteratura.py doi <chiave>                  # risolve i DOI della bibliografia del museo
    python strumenti/letteratura.py testo <id> <url> [licenza]    # testo di una pagina o di un PDF ad accesso aperto
    python strumenti/letteratura.py wikisource <id> <lingua> <pagina>

Regola: una fonte sostiene un'affermazione solo se il passo pertinente è stato
letto. I candidati trovati qui sono metadati: entrano nel registro delle fonti
(dati/bibliografia/<chiave>.json) solo dopo la cura, con il livello di lettura
dichiarato: «testo completo», «abstract», «non consultato».

File prodotti:
    dati/fonti/openalex/, dati/fonti/hal/      risposte grezze (OpenAlex CC0; HAL metadati aperti)
    dati/bibliografia/<chiave>.candidati.json  candidati normalizzati, da curare
    dati/testi/<id>.txt + .json                testo estratto e metadati di acquisizione
"""

from __future__ import annotations

import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

VERSIONE = "0.1.0"
USER_AGENT = f"ArtNotes-Prototype/{VERSIONE} (research prototype)"
RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"


def _ora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _scarica(url: str, accetta: str = "*/*") -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accetta})
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and tentativo < 2:
                time.sleep(3 * (tentativo + 1))
                continue
            raise
    raise RuntimeError("irraggiungibile")


def _leggi(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _scrivi(p: Path, dati) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def manifesto(chiave: str) -> dict:
    return _leggi(DATI / "opere" / f"{chiave}.json")


# ---------- OpenAlex ----------

CAMPI_OA = "id,doi,display_name,publication_year,type,language,cited_by_count,open_access,best_oa_location,primary_location,authorships,abstract_inverted_index"


def abstract_da_indice(indice: dict | None) -> str | None:
    if not indice:
        return None
    pos = [(p, parola) for parola, ps in indice.items() for p in ps]
    return " ".join(parola for _, parola in sorted(pos))


def normalizza_openalex(w: dict) -> dict:
    loc = w.get("primary_location") or {}
    oa = w.get("best_oa_location") or {}
    istituzioni = sorted({i["display_name"] for a in w.get("authorships", []) for i in a.get("institutions", [])})
    return {
        "fonte": "openalex",
        "id": w["id"].rsplit("/", 1)[-1],
        "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
        "titolo": w.get("display_name"),
        "anno": w.get("publication_year"),
        "tipo": w.get("type"),
        "lingua": w.get("language"),
        "autori": [a["author"]["display_name"] for a in w.get("authorships", [])][:8],
        "istituzioni": istituzioni[:6],
        "sede": ((loc.get("source") or {}).get("display_name")),
        "citazioni": w.get("cited_by_count"),
        "accesso_aperto": w.get("open_access", {}).get("is_oa"),
        "stato_oa": w.get("open_access", {}).get("oa_status"),
        "url_oa": oa.get("pdf_url") or oa.get("landing_page_url"),
        "licenza_oa": oa.get("license"),
        "abstract": abstract_da_indice(w.get("abstract_inverted_index")),
    }


def openalex(chiave: str, per_query: int = 50) -> Path:
    m = manifesto(chiave)
    grezzi, visti = [], {}
    for q in m["query_letteratura"]:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"search": q, "per-page": per_query, "select": CAMPI_OA})
        risposta = json.loads(_scarica(url, "application/json")[0])
        grezzi.append({"query": q, "url": url, "payload": risposta})
        for pos, w in enumerate(risposta.get("results", []), 1):
            rec = visti.setdefault(w["id"], {**normalizza_openalex(w), "trovato_da": []})
            rec["trovato_da"].append({"q": q, "posizione": pos})
        time.sleep(0.3)
    ora = _ora()
    _scrivi(DATI / "fonti" / "openalex" / f"{chiave}.json",
            {"acquisizione": {"fonte": "openalex", "data": ora, "connettore": f"letteratura.py {VERSIONE}", "licenza": "CC0"},
             "ricerche": grezzi})
    return _unisci_candidati(chiave, "openalex", list(visti.values()), ora)


# ---------- HAL ----------

def hal(chiave: str, righe: int = 40) -> Path:
    m = manifesto(chiave)
    grezzi, visti = [], {}
    campi = "halId_s,title_s,authFullName_s,producedDateY_i,docType_s,uri_s,fileMain_s,doiId_s,abstract_s,structName_s,language_s,openAccess_bool,licence_s"
    for q in m.get("query_hal", []):
        url = "https://api.archives-ouvertes.fr/search/?" + urllib.parse.urlencode({"q": q, "fl": campi, "rows": righe, "wt": "json"})
        risposta = json.loads(_scarica(url, "application/json")[0])
        grezzi.append({"query": q, "url": url, "payload": risposta})
        for pos, d in enumerate(risposta.get("response", {}).get("docs", []), 1):
            rec = visti.setdefault(d["halId_s"], {
                "fonte": "hal",
                "id": d["halId_s"],
                "doi": d.get("doiId_s"),
                "titolo": (d.get("title_s") or [""])[0],
                "anno": d.get("producedDateY_i"),
                "tipo": d.get("docType_s"),
                "lingua": (d.get("language_s") or [None])[0],
                "autori": (d.get("authFullName_s") or [])[:8],
                "istituzioni": (d.get("structName_s") or [])[:6],
                "sede": "HAL",
                "citazioni": None,
                "accesso_aperto": bool(d.get("fileMain_s")) or d.get("openAccess_bool"),
                "stato_oa": "green" if d.get("fileMain_s") else None,
                "url_oa": d.get("fileMain_s") or d.get("uri_s"),
                "licenza_oa": d.get("licence_s"),
                "abstract": (d.get("abstract_s") or [None])[0],
                "trovato_da": [],
            })
            rec["trovato_da"].append({"q": q, "posizione": pos})
        time.sleep(0.3)
    ora = _ora()
    _scrivi(DATI / "fonti" / "hal" / f"{chiave}.json",
            {"acquisizione": {"fonte": "hal", "data": ora, "connettore": f"letteratura.py {VERSIONE}"}, "ricerche": grezzi})
    return _unisci_candidati(chiave, "hal", list(visti.values()), ora)


# ---------- bibliografia del museo: DOI ----------

def doi(chiave: str) -> Path:
    """Estrae i DOI dalla bibliografia della scheda del museo e li risolve con OpenAlex."""
    m = manifesto(chiave)
    if m["istituzione"]["tipo"] != "louvre":
        raise SystemExit("solo per schede del Louvre (campo bibliography)")
    rec = _leggi(DATI / "fonti" / "louvre" / f"{m['istituzione']['id']}.json")["payload"]
    trovati = []
    for b in rec.get("bibliography", []):
        rif = html.unescape(b.get("bibliographyRef", ""))
        mt = re.search(r"10\.\d{4,9}/[^\s<>\"]+", rif)
        if not mt:
            continue
        d = mt.group(0).rstrip(".,;)")
        try:
            w = json.loads(_scarica(f"https://api.openalex.org/works/doi:{urllib.parse.quote(d)}?select={CAMPI_OA}", "application/json")[0])
            trovati.append({**normalizza_openalex(w), "trovato_da": [{"q": "bibliografia del museo", "posizione": None}],
                            "riferimento_museo": rif[:300]})
        except urllib.error.HTTPError:
            trovati.append({"fonte": "doi", "id": d, "doi": d, "titolo": rif[:200], "accesso_aperto": None,
                            "trovato_da": [{"q": "bibliografia del museo", "posizione": None}], "nota": "DOI non trovato in OpenAlex"})
        time.sleep(0.3)
    print(f"{len(rec.get('bibliography', []))} voci bibliografiche, {len(trovati)} con DOI")
    return _unisci_candidati(chiave, "bibliografia-museo", trovati, _ora())


def _unisci_candidati(chiave: str, origine: str, nuovi: list, ora: str) -> Path:
    p = DATI / "bibliografia" / f"{chiave}.candidati.json"
    esistenti = _leggi(p)["candidati"] if p.exists() else []
    per_chiave = {(c["fonte"], c["id"]): c for c in esistenti}
    for c in nuovi:
        per_chiave[(c["fonte"], c["id"])] = {**c, "aggiornato_il": ora}
    tutti = sorted(per_chiave.values(), key=lambda c: (not c.get("accesso_aperto"), -(c.get("citazioni") or 0)))
    _scrivi(p, {"opera": chiave, "nota": "Candidati da curare: metadati, non fonti lette.", "candidati": tutti})
    n_oa = sum(1 for c in nuovi if c.get("accesso_aperto"))
    print(f"{origine}: {len(nuovi)} candidati ({n_oa} ad accesso aperto) -> {p.relative_to(RADICE)}")
    return p


# ---------- testi ----------

def _html_a_testo(t: str) -> str:
    t = re.sub(r"(?is)<(script|style|nav|header|footer|aside|form|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</h\d>|</li>|</div>|</blockquote>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def testo(ident: str, url: str, licenza: str = "da verificare") -> Path:
    corpo, tipo = _scarica(url)
    if "pdf" in tipo or url.lower().endswith(".pdf") or corpo[:5] == b"%PDF-":
        from pypdf import PdfReader
        lettore = PdfReader(io.BytesIO(corpo))
        contenuto = "\n\n".join(f"[p. {i + 1}]\n{(p.extract_text() or '').strip()}" for i, p in enumerate(lettore.pages))
        formato = f"pdf, {len(lettore.pages)} pagine"
    else:
        contenuto = _html_a_testo(corpo.decode("utf-8", "replace"))
        formato = "html"
    cartella = DATI / "testi"
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / f"{ident}.txt").write_text(contenuto, encoding="utf-8")
    _scrivi(cartella / f"{ident}.json", {"id": ident, "url": url, "formato": formato, "licenza": licenza,
                                         "sha256": hashlib.sha256(corpo).hexdigest(), "acquisito_il": _ora(),
                                         "caratteri": len(contenuto), "connettore": f"letteratura.py {VERSIONE}"})
    print(f"{ident}: {formato}, {len(contenuto)} caratteri -> dati/testi/{ident}.txt")
    return cartella / f"{ident}.txt"


def wikisource(ident: str, lingua: str, pagina: str) -> Path:
    url = f"https://{lingua}.wikisource.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "parse", "page": pagina, "prop": "text", "format": "json", "formatversion": 2})
    d = json.loads(_scarica(url, "application/json")[0])
    if "error" in d:
        raise SystemExit(f"Wikisource: {d['error'].get('info')}")
    contenuto = _html_a_testo(d["parse"]["text"])
    cartella = DATI / "testi"
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / f"{ident}.txt").write_text(contenuto, encoding="utf-8")
    _scrivi(cartella / f"{ident}.json", {"id": ident, "url": f"https://{lingua}.wikisource.org/wiki/{urllib.parse.quote(pagina)}",
                                         "url_dati": url, "formato": "wikisource", "licenza": "testo in pubblico dominio; trascrizione Wikisource CC BY-SA",
                                         "acquisito_il": _ora(), "caratteri": len(contenuto), "connettore": f"letteratura.py {VERSIONE}"})
    print(f"{ident}: {len(contenuto)} caratteri -> dati/testi/{ident}.txt")
    return cartella / f"{ident}.txt"


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] in ("openalex", "hal", "doi"):
        {"openalex": openalex, "hal": hal, "doi": doi}[a[0]](a[1])
    elif len(a) in (3, 4) and a[0] == "testo":
        testo(a[1], a[2], *(a[3:]))
    elif len(a) == 4 and a[0] == "wikisource":
        wikisource(a[1], a[2], a[3])
    else:
        print(__doc__)
        sys.exit(1)
