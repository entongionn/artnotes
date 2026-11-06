"""Importazione ripetibile delle fonti per il prototipo ArtNotes (Fase 2).

Uso:
    python strumenti/importa.py met 435809
    python strumenti/importa.py wikidata Q776175

Per ogni fonte salva il payload originale con i metadati di acquisizione
(URL, data, versione del connettore). Per un oggetto Met scarica anche
l'immagine principale e genera le tile Deep Zoom.

Rieseguire il comando non crea duplicati: i file sono indicizzati per
identificativo della fonte, e l'immagine per impronta SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

VERSIONE_CONNETTORE = "0.1.0"
USER_AGENT = f"ArtNotes-Prototype/{VERSIONE_CONNETTORE} (research prototype)"

RADICE = Path(__file__).resolve().parent.parent
DIR_FONTI = RADICE / "dati" / "fonti"
DIR_IMMAGINI = RADICE / "dati" / "immagini"
DIR_ORIGINALI = RADICE / "originali"  # file sorgente, esclusi dalla pubblicazione
DIR_TILE = RADICE / "web" / "immagini"

TILE = 254
OVERLAP = 1


def _scarica(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for tentativo in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and tentativo < 2:
                attesa = int(e.headers.get("Retry-After", "5"))
                time.sleep(min(attesa, 30))
                continue
            raise
    raise RuntimeError("irraggiungibile")


def _ora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _salva_payload(fonte: str, ident: str, url: str, payload) -> Path:
    cartella = DIR_FONTI / fonte
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / f"{ident}.json"
    busta = {
        "acquisizione": {
            "fonte": fonte,
            "identificativo": ident,
            "url": url,
            "data": _ora(),
            "connettore": f"importa.py {VERSIONE_CONNETTORE}",
        },
        "payload": payload,
    }
    percorso.write_text(json.dumps(busta, ensure_ascii=False, indent=2), encoding="utf-8")
    return percorso


def genera_dzi(sorgente: Path, destinazione: Path) -> tuple[int, int]:
    """Genera una piramide Deep Zoom (DZI) con Pillow."""
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(sorgente).convert("RGB")
    w, h = im.size
    livello_max = math.ceil(math.log2(max(w, h)))
    cartella_tile = destinazione.with_name(destinazione.stem + "_files")
    for livello in range(livello_max, -1, -1):
        scala = 2 ** (livello - livello_max)
        lw, lh = max(1, math.ceil(w * scala)), max(1, math.ceil(h * scala))
        img_liv = im if (lw, lh) == (w, h) else im.resize((lw, lh), Image.LANCZOS)
        d = cartella_tile / str(livello)
        d.mkdir(parents=True, exist_ok=True)
        for col in range(math.ceil(lw / TILE)):
            for riga in range(math.ceil(lh / TILE)):
                x0 = col * TILE - (OVERLAP if col else 0)
                y0 = riga * TILE - (OVERLAP if riga else 0)
                x1 = min(lw, (col + 1) * TILE + OVERLAP)
                y1 = min(lh, (riga + 1) * TILE + OVERLAP)
                img_liv.crop((x0, y0, x1, y1)).save(d / f"{col}_{riga}.jpg", quality=88)
    destinazione.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008" Format="jpg" '
        f'Overlap="{OVERLAP}" TileSize="{TILE}"><Size Width="{w}" Height="{h}"/></Image>\n',
        encoding="utf-8",
    )
    return w, h


def importa_met(object_id: str) -> None:
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    rec = json.loads(_scarica(url))
    print("payload salvato:", _salva_payload("met", object_id, url, rec))

    url_img = rec.get("primaryImage")
    if not url_img:
        print("nessuna immagine principale: niente da scaricare")
        return
    if not rec.get("isPublicDomain"):
        print("isPublicDomain = false: immagine non scaricata")
        return

    dati = _scarica(url_img)
    impronta = hashlib.sha256(dati).hexdigest()
    corto = impronta[:12]
    DIR_ORIGINALI.mkdir(parents=True, exist_ok=True)
    originale = DIR_ORIGINALI / f"met_{object_id}_{corto}.jpg"
    if not originale.exists():
        originale.write_bytes(dati)

    dzi = DIR_TILE / corto / "immagine.dzi"
    if dzi.exists():
        print("tile già presenti per questa versione:", corto)
        from PIL import Image
        w, h = Image.open(originale).size
    else:
        dzi.parent.mkdir(parents=True, exist_ok=True)
        w, h = genera_dzi(originale, dzi)
        print("tile generate:", dzi)

    from PIL import Image
    modo = Image.open(originale).convert("RGB").resize((64, 64))
    b = modo.tobytes()
    colore = any(max(b[i : i + 3]) - min(b[i : i + 3]) > 4 for i in range(0, len(b), 3))

    DIR_IMMAGINI.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": f"met-{object_id}-{corto}",
        "sha256": impronta,
        "fonte": "met",
        "record_fonte": object_id,
        "url_originale": url_img,
        "file_fotografia": url_img.rsplit("/", 1)[-1],
        "larghezza": w,
        "altezza": h,
        "a_colori": colore,
        "vista": "recto, intero",
        "diritti": {
            "metadati": "CC0 (Met Open Access)",
            "fotografia": "pubblico dominio secondo isPublicDomain = true (Met Open Access)",
            "opera": "pubblico dominio (opera del 1565)",
            "verificato_il": datetime.now().date().isoformat(),
        },
        "crediti": "The Metropolitan Museum of Art, Open Access",
        "acquisita_il": _ora(),
        "dzi": f"immagini/{corto}/immagine.dzi",
    }
    (DIR_IMMAGINI / f"met_{object_id}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("immagine registrata:", meta["id"], f"{w}x{h}", "colore" if colore else "bianco e nero")


def importa_wikidata(qid: str) -> None:
    url = (
        "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
        f"&props=labels|claims|sitelinks&languages=it|en&ids={qid}"
    )
    ent = json.loads(_scarica(url))["entities"][qid]
    # Etichette degli elementi citati, per mostrare valori leggibili.
    ids = set()
    for asserzioni in ent.get("claims", {}).values():
        for a in asserzioni:
            v = a["mainsnak"].get("datavalue", {}).get("value")
            if isinstance(v, dict) and str(v.get("id", "")).startswith("Q"):
                ids.add(v["id"])
            for qual in a.get("qualifiers", {}).values():
                for q in qual:
                    qv = q.get("datavalue", {}).get("value")
                    if isinstance(qv, dict) and str(qv.get("id", "")).startswith("Q"):
                        ids.add(qv["id"])
    etichette = {}
    lista = sorted(ids)
    for i in range(0, len(lista), 50):
        u = (
            "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
            "&props=labels&languages=it|en&ids=" + "|".join(lista[i : i + 50])
        )
        for k, v in json.loads(_scarica(u))["entities"].items():
            lab = v.get("labels", {})
            etichette[k] = (lab.get("it") or lab.get("en") or {}).get("value")
        time.sleep(0.5)
    print("payload salvato:", _salva_payload("wikidata", qid, url, {"entita": ent, "etichette": etichette}))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("met", "wikidata"):
        print(__doc__)
        sys.exit(1)
    {"met": importa_met, "wikidata": importa_wikidata}[sys.argv[1]](sys.argv[2])
