"""Connettore YouTube Data API v3 per ArtNotes Pulse (Fase 2.5).

Uso:
    python strumenti/youtube.py query 435809      # mostra le query, senza chiamare l'API
    python strumenti/youtube.py cerca 435809      # search.list + videos.list: candidati da curare
    python strumenti/youtube.py verifica 435809   # videos.list sui soli video curati

Gira solo da linea di comando (o da un job lato server): la chiave non va mai
nel sito. Viene letta, in quest'ordine, da:
    - variabile d'ambiente YOUTUBE_API_KEY
    - file ~/.artnotes/youtube_api_key.txt

File prodotti:
    dati/fonti/youtube/<id>_<data>.json        payload grezzi (esclusi da git)
    dati/esterni/youtube/<id>.candidati.json   candidati normalizzati da curare (esclusi da git)
    dati/esterni/youtube/<id>.metadati.json    metadati minimi dei soli video curati

Il connettore non classifica: la relazione con l'opera la decide la cura
redazionale (dati/esterni/<id>.json). Una parola chiave nel titolo è solo un
indizio, registrato in «indizi».

Costo in quota (unità giornaliere, predefinito 10.000): search.list 100 per
query, videos.list 1 ogni 50 video.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

VERSIONE = "0.1.0"
USER_AGENT = f"ArtNotes-Prototype/{VERSIONE} (research prototype)"
API = "https://www.googleapis.com/youtube/v3"

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
FILE_CHIAVE = Path.home() / ".artnotes" / "youtube_api_key.txt"

# Secondo le policy per sviluppatori dei servizi API di YouTube i dati
# conservati vanno aggiornati periodicamente: dopo questo intervallo un record
# non riverificato non è più mostrato in modalità pubblica.
VALIDITA_GIORNI = 30
LINGUE_TITOLI = ("en", "it", "fr", "de", "nl", "es")


class ErroreYouTube(Exception):
    """Errore dell'API. Il messaggio non contiene mai la chiave."""


# ---------- chiave e chiamate ----------

def leggi_chiave() -> str:
    k = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not k and FILE_CHIAVE.exists():
        k = FILE_CHIAVE.read_text(encoding="utf-8").strip()
    if not k:
        raise ErroreYouTube(f"chiave mancante: imposta YOUTUBE_API_KEY o crea {FILE_CHIAVE}")
    return k


def url_senza_chiave(url: str) -> str:
    parti = urllib.parse.urlsplit(url)
    q = [(k, "REDATTA" if k == "key" else v) for k, v in urllib.parse.parse_qsl(parti.query)]
    return urllib.parse.urlunsplit(parti._replace(query=urllib.parse.urlencode(q)))


def chiama(metodo: str, parametri: dict, chiave: str) -> tuple[dict, str]:
    """Restituisce (risposta, url senza chiave). Riprova con attesa crescente su 429/5xx."""
    url = f"{API}/{metodo}?" + urllib.parse.urlencode({**parametri, "key": chiave})
    pulito = url_senza_chiave(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read()), pulito
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8", "replace")
            motivo = ""
            try:
                motivo = json.loads(corpo)["error"]["errors"][0]["reason"]
            except Exception:
                pass
            if (e.code == 429 or e.code >= 500) and tentativo < 3:
                time.sleep(2 ** tentativo)
                continue
            # quotaExceeded, keyInvalid, ecc.: messaggio senza URL né chiave.
            raise ErroreYouTube(f"{metodo}: HTTP {e.code} {motivo}".strip()) from None
        except urllib.error.URLError as e:
            if tentativo < 3:
                time.sleep(2 ** tentativo)
                continue
            raise ErroreYouTube(f"{metodo}: rete non raggiungibile ({e.reason})") from None
    raise ErroreYouTube(f"{metodo}: tentativi esauriti")


# ---------- query ----------

def _leggi(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def query_per_opera(object_id: str) -> list[dict]:
    """Query dai dati canonici: titolo del museo, titoli delle voci Wikipedia
    collegate all'elemento Wikidata (varianti multilingue), serie di appartenenza."""
    met = _leggi(DATI / "fonti" / "met" / f"{object_id}.json")["payload"]
    qid = met["objectWikidata_URL"].rsplit("/", 1)[-1]
    ent = _leggi(DATI / "fonti" / "wikidata" / f"{qid}.json")["payload"]["entita"]
    autore = met["artistDisplayName"].split()[-1] if met.get("artistDisplayName") else ""
    # «Pieter Bruegel the Elder» -> «Bruegel»
    for parola in met.get("artistDisplayName", "").split():
        if parola.lower().startswith("brueg") or parola.lower().startswith("breug"):
            autore = parola
    titoli: dict[str, str] = {"met": met["title"]}
    for lingua in LINGUE_TITOLI:
        s = ent.get("sitelinks", {}).get(f"{lingua}wiki", {}).get("title")
        if s:
            titoli[lingua] = re.sub(r"\s*\(.*?\)\s*", " ", s).strip()
    lab = ent.get("labels", {}).get("it", {}).get("value")
    if lab:
        titoli.setdefault("it-label", lab)

    query, viste = [], set()
    for origine, t in titoli.items():
        testo = t if autore.lower() in t.lower() else f"{autore} {t}"
        if testo.lower() in viste:
            continue
        viste.add(testo.lower())
        query.append({"q": testo, "tipo": "opera", "origine": f"titolo {origine}"})

    # Varianti aggiunte dalla redazione, ciascuna con la sua motivazione.
    cura = DATI / "esterni" / f"{object_id}.json"
    if cura.exists():
        for v in _leggi(cura).get("query_aggiuntive", []):
            if v["q"].lower() not in viste:
                viste.add(v["q"].lower())
                query.append({"q": v["q"], "tipo": v.get("tipo", "opera"), "origine": f"redazione: {v['motivazione']}"})

    # Query tematiche, marcate come tali: non cercano l'opera ma il suo contesto.
    for a in ent.get("claims", {}).get("P361", []):
        sid = a["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
        f = DATI / "fonti" / "wikidata" / f"{sid}.json"
        if sid and f.exists():
            serie = _leggi(f)["payload"]["entita"].get("labels", {}).get("en", {}).get("value")
            if serie:
                query.append({"q": f"{autore} {serie}", "tipo": "tematica", "origine": f"serie Wikidata {sid}"})
    return query


# ---------- normalizzazione ----------

def durata_secondi(iso: str | None) -> int | None:
    if not iso:
        return None
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return None
    g, h, mi, s = (int(x or 0) for x in m.groups())
    return ((g * 24 + h) * 60 + mi) * 60 + s


def indizi(record: dict, termini: list[str]) -> list[str]:
    """Dove compaiono i termini cercati. È un indizio, non una classificazione."""
    out = []
    for campo in ("titolo", "estratto_descrizione"):
        testo = (record.get(campo) or "").lower()
        trovati = [t for t in termini if t.lower() in testo]
        if trovati:
            out.append(f"{campo}: {', '.join(sorted(set(trovati)))}")
    return out


def normalizza(video: dict, ora: str) -> dict:
    sn, cd, st = video.get("snippet", {}), video.get("contentDetails", {}), video.get("status", {})
    stats = video.get("statistics", {})
    vid = video["id"]
    blocchi = cd.get("regionRestriction", {})
    disponibile = st.get("privacyStatus") == "public" and st.get("uploadStatus") in (None, "processed")
    return {
        "piattaforma": "youtube",
        "video_id": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "titolo": sn.get("title"),
        "canale_id": sn.get("channelId"),
        "canale": sn.get("channelTitle"),
        "estratto_descrizione": (sn.get("description") or "")[:400],
        "pubblicato_il": sn.get("publishedAt"),
        "lingua": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
        "miniatura": (sn.get("thumbnails", {}).get("medium") or sn.get("thumbnails", {}).get("default") or {}).get("url"),
        "durata_s": durata_secondi(cd.get("duration")),
        "visualizzazioni": int(stats["viewCount"]) if "viewCount" in stats else None,
        "incorporabile": st.get("embeddable"),
        "bloccato_in": blocchi.get("blocked", []),
        "disponibile": disponibile,
        "scoperto_il": ora,
        "verificato_il": ora,
        # La relazione con l'opera NON è decisa qui.
        "relazione": None,
    }


def unisci(risultati_ricerca: list[tuple[dict, dict]]) -> dict[str, dict]:
    """Deduplica per video_id: lo stesso video trovato da più query resta uno,
    con l'elenco delle query che lo hanno trovato e la posizione migliore."""
    visti: dict[str, dict] = {}
    for query, risposta in risultati_ricerca:
        for pos, item in enumerate(risposta.get("items", []), start=1):
            vid = item.get("id", {}).get("videoId")
            if not vid:
                continue
            v = visti.setdefault(vid, {"video_id": vid, "trovato_da": [], "posizione_migliore": pos})
            v["trovato_da"].append({"q": query["q"], "tipo": query["tipo"], "posizione": pos})
            v["posizione_migliore"] = min(v["posizione_migliore"], pos)
    return visti


def scaduto(record: dict, adesso: datetime | None = None) -> bool:
    adesso = adesso or datetime.now(timezone.utc)
    t = record.get("verificato_il")
    if not t:
        return True
    return adesso - datetime.fromisoformat(t) > timedelta(days=VALIDITA_GIORNI)


# ---------- comandi ----------

def _ora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _videos_list(ids: list[str], chiave: str) -> tuple[list[dict], list[dict]]:
    items, chiamate = [], []
    for i in range(0, len(ids), 50):
        r, url = chiama(
            "videos",
            {"part": "snippet,contentDetails,status,statistics", "id": ",".join(ids[i : i + 50]), "maxResults": 50},
            chiave,
        )
        items += r.get("items", [])
        chiamate.append({"url": url, "payload": r})
    return items, chiamate


def cerca(object_id: str, per_query: int = 25) -> Path:
    chiave = leggi_chiave()
    ora = _ora()
    query = query_per_opera(object_id)
    grezzi, risultati = [], []
    for q in query:
        r, url = chiama(
            "search",
            {"part": "snippet", "type": "video", "q": q["q"], "maxResults": per_query, "safeSearch": "strict"},
            chiave,
        )
        grezzi.append({"query": q, "url": url, "payload": r})
        risultati.append((q, r))
    visti = unisci(risultati)
    items, chiamate = _videos_list(list(visti), chiave)

    termini = sorted({w for q in query if q["tipo"] == "opera" for w in [q["q"]]})
    candidati = []
    for v in items:
        rec = normalizza(v, ora)
        rec.update(trovato_da=visti[v["id"]]["trovato_da"], posizione_migliore=visti[v["id"]]["posizione_migliore"])
        rec["indizi"] = indizi(rec, termini + ["harvesters", "mietitur", "mietitori", "moisson", "kornernte", "oogst", "segadores", "cosecha"])
        candidati.append(rec)
    # Video trovati dalla ricerca ma non restituiti da videos.list: rimossi o privati.
    mancanti = sorted(set(visti) - {v["id"] for v in items})
    candidati.sort(key=lambda r: (r["posizione_migliore"], -len(r["trovato_da"])))

    cartella = DATI / "fonti" / "youtube"
    cartella.mkdir(parents=True, exist_ok=True)
    timbro = ora.replace(":", "").replace("-", "")[:15]
    (cartella / f"{object_id}_{timbro}.json").write_text(
        json.dumps(
            {
                "acquisizione": {"fonte": "youtube-data-api-v3", "data": ora, "connettore": f"youtube.py {VERSIONE}"},
                "ricerche": grezzi,
                "videos": chiamate,
            },
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    uscita = DATI / "esterni" / "youtube" / f"{object_id}.candidati.json"
    uscita.parent.mkdir(parents=True, exist_ok=True)
    uscita.write_text(
        json.dumps(
            {
                "opera": f"met:{object_id}",
                "generato_il": ora,
                "query": query,
                "unita_quota_stimate": 100 * len(query) + len(chiamate),
                "non_restituiti_da_videos_list": mancanti,
                "candidati": candidati,
            },
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    print(f"{len(query)} query, {sum(len(r.get('items', [])) for _, r in risultati)} risultati, "
          f"{len(candidati)} video unici, {len(mancanti)} non disponibili -> {uscita.relative_to(RADICE)}")
    return uscita


def verifica(object_id: str) -> Path:
    """Aggiorna i metadati dei soli video curati. Un video rimosso o privato
    resta nel file con disponibile=false: non viene cancellato in silenzio."""
    chiave = leggi_chiave()
    ora = _ora()
    cura = _leggi(DATI / "esterni" / f"{object_id}.json")
    # Minimizzazione: solo i video non respinti, senza descrizione (non serve al sito).
    ids = [c["video_id"] for c in cura["contenuti"] if c["piattaforma"] == "youtube" and c["stato"] != "respinto"]
    items, _ = _videos_list(ids, chiave)
    trovati = {v["id"]: normalizza(v, ora) for v in items}
    file_meta = DATI / "esterni" / "youtube" / f"{object_id}.metadati.json"
    precedenti = _leggi(file_meta)["video"] if file_meta.exists() else {}
    video = {}
    for vid in ids:
        if vid in trovati:
            rec = trovati[vid]
            rec["scoperto_il"] = precedenti.get(vid, {}).get("scoperto_il", ora)
        else:
            rec = {**precedenti.get(vid, {"video_id": vid, "piattaforma": "youtube"}),
                   "disponibile": False, "verificato_il": ora, "nota": "non restituito da videos.list: rimosso, privato o inesistente"}
        rec.pop("relazione", None)
        rec.pop("estratto_descrizione", None)
        video[vid] = rec
    file_meta.parent.mkdir(parents=True, exist_ok=True)
    file_meta.write_text(
        json.dumps(
            {
                "opera": f"met:{object_id}",
                "nota": "Metadati minimi restituiti da YouTube Data API v3 (videos.list) per i soli video curati. "
                        f"Da riverificare entro {VALIDITA_GIORNI} giorni.",
                "verificato_il": ora,
                "video": video,
            },
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    n_ok = sum(1 for v in video.values() if v.get("disponibile"))
    print(f"{len(ids)} video curati, {n_ok} disponibili -> {file_meta.relative_to(RADICE)}")
    return file_meta


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("query", "cerca", "verifica"):
        print(__doc__)
        sys.exit(1)
    comando, oid = sys.argv[1], sys.argv[2]
    try:
        if comando == "query":
            for q in query_per_opera(oid):
                print(f"[{q['tipo']}] {q['q']}   ({q['origine']})")
        else:
            {"cerca": cerca, "verifica": verifica}[comando](oid)
    except ErroreYouTube as e:
        print("ERRORE YouTube:", e)
        sys.exit(2)
