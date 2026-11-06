"""Prove automatiche sulla composizione della scheda (criteri §21 della specifica).

Uso:
    python strumenti/prove.py
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import componi  # noqa: E402
import youtube  # noqa: E402

ID = "435809"


class Base(unittest.TestCase):
    """Ogni prova lavora su una copia temporanea dei dati."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(componi.DATI, self.tmp / "dati")
        self._dati_originali = componi.DATI
        componi.DATI = self.tmp / "dati"

    def tearDown(self):
        componi.DATI = self._dati_originali
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _modifica(self, rel, funzione):
        p = componi.DATI / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        funzione(d)
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class ProveScheda(Base):
    """Fase 2: composizione della scheda."""

    # Redazione: solo le versioni pubblicate sono visibili ai lettori.
    def test_modalita_pubblica_esclude_le_bozze(self):
        s = componi.componi(ID, pubblico=True)
        self.assertEqual(s["annotazioni"], [])
        self.assertTrue(all(not sez["blocchi"] for sez in s["sezioni"]))
        self.assertTrue(s["opera"]["catalogo"]["attribuzioni"])  # il catalogo resta visibile

    def test_modalita_pubblica_mostra_i_pubblicati(self):
        def pubblica_a01(d):
            d["annotazioni"][0]["stato"] = "pubblicato"
        self._modifica(f"annotazioni/{ID}.json", pubblica_a01)
        s = componi.componi(ID, pubblico=True)
        self.assertEqual([a["id"] for a in s["annotazioni"]], ["a01"])

    # Versioni: cambiare immagine segnala la necessità di riverificare.
    def test_cambio_immagine_marca_da_riverificare(self):
        self._modifica(f"immagini/met_{ID}.json", lambda d: d.update(sha256="0" * 64))
        s = componi.componi(ID)
        self.assertTrue(s["annotazioni"])
        self.assertTrue(all(a["verifica_immagine"] == "da_riverificare" for a in s["annotazioni"]))

    def test_stessa_immagine_regioni_valide(self):
        s = componi.componi(ID)
        self.assertTrue(all(a["verifica_immagine"] == "valida" for a in s["annotazioni"]))

    # Annotazioni: coordinate normalizzate dentro l'immagine.
    def test_coordinate_normalizzate(self):
        for a in componi.componi(ID)["annotazioni"]:
            r = a["regione_normalizzata"]
            self.assertGreaterEqual(r["x"], 0)
            self.assertGreaterEqual(r["y"], 0)
            self.assertLessEqual(r["x"] + r["w"], 1.00001, a["id"])
            self.assertLessEqual(r["y"] + r["h"], 1.00001, a["id"])

    def test_regione_fuori_immagine_rifiutata(self):
        self._modifica(
            f"annotazioni/{ID}.json",
            lambda d: d["annotazioni"][0].update(regione="xywh=percent:90,90,20,20"),
        )
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    # Fonti: un blocco «documentato» deve citare almeno una fonte nota.
    def test_documentato_senza_fonti_rifiutato(self):
        def togli(d):
            d["sezioni"][0]["blocchi"][0]["fonti"] = []
        self._modifica(f"contenuti/{ID}.json", togli)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_fonte_sconosciuta_rifiutata(self):
        def inventa(d):
            d["sezioni"][0]["blocchi"][0]["fonti"] = [{"fonte": "libro-inesistente"}]
        self._modifica(f"contenuti/{ID}.json", inventa)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_registro_non_valido_rifiutato(self):
        self._modifica(
            f"contenuti/{ID}.json",
            lambda d: d["sezioni"][0]["blocchi"][0].update(registro="certo"),
        )
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    # Origine AI conservata su ogni blocco.
    def test_origine_ai_presente_ovunque(self):
        s = componi.componi(ID)
        blocchi = [b for sez in s["sezioni"] for b in sez["blocchi"]]
        self.assertTrue(blocchi)
        self.assertTrue(all(b["origine"]["tipo"] == "ai" for b in blocchi))
        self.assertTrue(all(a["origine"]["tipo"] == "ai" for a in s["annotazioni"]))

    # Identità: la concordanza delle attribuzioni si basa sugli identificativi.
    def test_attribuzione_discordante_segnalata(self):
        def cambia_autore(d):
            d["payload"]["entita"]["claims"]["P170"][0]["mainsnak"]["datavalue"]["value"]["id"] = "Q1"
        self._modifica("fonti/wikidata/Q776175.json", cambia_autore)
        mot = componi.componi(ID)["opera"]["catalogo"]["attribuzione_in_evidenza"]["motivazione"]
        self.assertIn("non concordano", mot)

    def test_attribuzione_concordante(self):
        mot = componi.componi(ID)["opera"]["catalogo"]["attribuzione_in_evidenza"]["motivazione"]
        self.assertIn("stessa persona", mot)


class ProveFase25(Base):
    """Percorsi, connessioni e ArtNotes Pulse (Fase 2.5, §6.6 e §9)."""

    def setUp(self):
        super().setUp()
        self._yt_dati = youtube.DATI
        youtube.DATI = componi.DATI

    def tearDown(self):
        youtube.DATI = self._yt_dati
        super().tearDown()

    def _cura(self, funzione):
        self._modifica(f"esterni/{ID}.json", funzione)

    def _meta(self, funzione):
        self._modifica(f"esterni/youtube/{ID}.metadati.json", funzione)

    # --- requisiti dei percorsi (§9) ---
    def test_tre_percorsi_presenti(self):
        s = componi.componi(ID)
        self.assertEqual([p["id"] for p in s["percorsi"]], ["curioso", "studio", "ispirazione"])

    def test_cur01_almeno_tre_tappe_su_regioni(self):
        s = componi.componi(ID)
        p = next(p for p in s["percorsi"] if p["id"] == "curioso")
        scene = {sc["id"]: sc for sc in (s["racconto"] or {}).get("scene", [])}
        def su_regione(t):
            if t.get("annotazione") or t.get("scelte"):
                return True
            sc = scene.get(t.get("scena"))
            return bool(sc and (sc["inquadra"].get("regione") or any(f.get("a") for f in sc["frasi"])))
        self.assertGreaterEqual(sum(1 for t in p["tappe"] if su_regione(t)), 3)

    def test_stu01_domanda_interpretazione_fonte(self):
        s = componi.componi(ID)
        p = next(p for p in s["percorsi"] if p["id"] == "studio")
        self.assertTrue(any(t["tipo"] == "scrivi" for t in p["tappe"]))
        blocchi = {b["id"]: b for sez in s["sezioni"] for b in sez["blocchi"]}
        letti = [blocchi[b] for t in p["tappe"] if t["tipo"] == "leggi" for b in t["blocchi"]]
        self.assertTrue(any(b["registro"] == "interpretazione" for b in letti))
        fonti = [f["fonte"] for b in letti for f in b.get("fonti", [])]
        self.assertTrue(any(s["fonti"][f].get("url") for f in fonti))

    def test_isp01_tre_connessioni_di_tipo_diverso(self):
        s = componi.componi(ID)
        p = next(p for p in s["percorsi"] if p["id"] == "ispirazione")
        ids = {k for t in p["tappe"] for k in t.get("connessioni", [])}
        tipi = {k["tipo"] for k in s["connessioni"] if k["id"] in ids}
        self.assertGreaterEqual(len(ids), 3)
        self.assertEqual(tipi, {"documentata", "interpretativa", "algoritmica"})

    def test_tappa_con_riferimento_inesistente_rifiutata(self):
        self._modifica(f"percorsi/{ID}.json", lambda d: d["percorsi"][0]["tappe"][1].update(annotazione="a99"))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_mappa_evidenze_con_certezza(self):
        s = componi.componi(ID)
        righe = [r for p in s["percorsi"] for t in p["tappe"] if t["tipo"] == "evidenze" for r in t["righe_risolte"]]
        self.assertTrue(righe)
        livelli = {r["certezza"]["livello"] for r in righe}
        self.assertTrue({"istituzionale", "da_verificare", "proposta", "non_nota"} <= livelli)

    # --- connessioni ---
    def test_connessione_documentata_senza_fonti_rifiutata(self):
        def togli(d):
            d["connessioni"][0]["blocchi"] = [b for b in d["connessioni"][0]["blocchi"] if b["registro"] != "documentato"]
        self._modifica(f"connessioni/{ID}.json", togli)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_connessione_interpretativa_richiede_ipotesi(self):
        def cambia(d):
            k = next(k for k in d["connessioni"] if k["tipo"] == "interpretativa")
            for b in k["blocchi"]:
                b["registro"] = "osservazione"
        self._modifica(f"connessioni/{ID}.json", cambia)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_connessione_algoritmica_calcolata(self):
        k = next(k for k in componi.componi(ID)["connessioni"] if k["tipo"] == "algoritmica")
        trovate = {r["opera"]["wikidata"]: r["in_comune"] for r in k["calcolo"]["risultati"]}
        self.assertEqual(set(trovate), {"Q1213437", "Q114707348"})
        self.assertTrue(all(len(v) >= k["calcolo"]["soglia"] for v in trovate.values()))

    # --- YT-01: varianti multilingue e falsi positivi ---
    def test_yt01_query_multilingue_e_tematiche_separate(self):
        q = youtube.query_per_opera(ID)
        opera = [x["q"] for x in q if x["tipo"] == "opera"]
        self.assertGreaterEqual(len(opera), 5)
        self.assertIn("Bruegel Die Kornernte", opera)
        self.assertTrue(any(x["tipo"] == "tematica" for x in q))

    def test_yt01_il_connettore_non_classifica(self):
        v = {"id": "AAAAAAAAAAA", "snippet": {"title": "Bruegel The Harvesters", "channelId": "c", "channelTitle": "c"},
             "status": {"privacyStatus": "public", "uploadStatus": "processed"}, "contentDetails": {"duration": "PT4M2S"}}
        r = youtube.normalizza(v, "2026-11-06T00:00:00+00:00")
        self.assertIsNone(r["relazione"])
        self.assertEqual(r["durata_s"], 242)

    def test_yt01_falso_positivo_solo_respinto(self):
        def riapri(d):
            next(c for c in d["contenuti"] if c["relazione"] == "falso_positivo")["stato"] = "candidato"
        self._cura(riapri)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    # --- YT-02: deduplicazione ---
    def test_yt02_stesso_video_da_query_diverse(self):
        r1 = {"items": [{"id": {"videoId": "AAAAAAAAAAA"}}, {"id": {"videoId": "BBBBBBBBBBB"}}]}
        r2 = {"items": [{"id": {"videoId": "AAAAAAAAAAA"}}]}
        visti = youtube.unisci([({"q": "uno", "tipo": "opera"}, r1), ({"q": "due", "tipo": "opera"}, r2)])
        self.assertEqual(len(visti), 2)
        self.assertEqual([t["q"] for t in visti["AAAAAAAAAAA"]["trovato_da"]], ["uno", "due"])

    def test_yt02_video_duplicato_nella_cura_rifiutato(self):
        self._cura(lambda d: d["contenuti"].append(dict(d["contenuti"][0])))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    # --- YT-03: classificazione ---
    def test_yt03_relazione_non_valida_rifiutata(self):
        self._cura(lambda d: d["contenuti"][0].update(relazione="forse"))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_yt03_classificazione_senza_evidenza_rifiutata(self):
        self._cura(lambda d: d["contenuti"][0].update(evidenza=[]))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    # --- YT-04: link valido, attribuzione, nessun video inventato ---
    def test_yt04_video_senza_metadati_rifiutato(self):
        def inventa(d):
            d["contenuti"].append({**d["contenuti"][0], "video_id": "ZZZZZZZZZZZ"})
        self._cura(inventa)
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_yt04_url_costruito_e_canale_attribuito(self):
        for v in componi.componi(ID)["pulse"]["contenuti"]:
            self.assertEqual(v["url"], f"https://www.youtube.com/watch?v={v['video_id']}")
            self.assertTrue(v["canale"] and v["canale_url"].startswith("https://www.youtube.com/channel/"))
            self.assertTrue(v["motivazione"] and v["relazione_testo"])

    # --- YT-05: indisponibilità ---
    def test_yt05_video_rimosso_escluso(self):
        vid = componi.componi(ID)["pulse"]["contenuti"][0]["video_id"]
        self._meta(lambda d: d["video"][vid].update(disponibile=False))
        p = componi.componi(ID)["pulse"]
        self.assertNotIn(vid, [v["video_id"] for v in p["contenuti"]])
        self.assertEqual(p["conteggi"]["non_disponibili"], 1)

    def test_yt05_metadati_assenti_non_bloccano_la_scheda(self):
        (componi.DATI / "esterni" / "youtube" / f"{ID}.metadati.json").unlink()
        s = componi.componi(ID)
        self.assertEqual(s["pulse"]["stato_fonte"], "metadati_mancanti")
        self.assertEqual(s["pulse"]["contenuti"], [])
        self.assertEqual(len(s["annotazioni"]), 14)
        self.assertTrue(s["percorsi"])

    def test_yt05_dati_scaduti_segnalati_e_fuori_dal_pubblico(self):
        vecchio = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(timespec="seconds")
        self._meta(lambda d: [v.update(verificato_il=vecchio) for v in d["video"].values()])
        self._cura(lambda d: [c.update(stato="pubblicato") for c in d["contenuti"] if c["stato"] == "candidato"])
        self.assertTrue(all(v["da_ricontrollare"] for v in componi.componi(ID)["pulse"]["contenuti"]))
        self.assertEqual(componi.componi(ID, pubblico=True)["pulse"]["contenuti"], [])

    def test_yt05_errore_api_senza_chiave_nel_messaggio(self):
        import io
        import urllib.error
        corpo = b'{"error":{"errors":[{"reason":"quotaExceeded"}]}}'
        errore = urllib.error.HTTPError("https://x/?key=SEGRETA", 403, "Forbidden", {}, io.BytesIO(corpo))
        self.addCleanup(errore.close)
        with mock.patch("urllib.request.urlopen", side_effect=errore):
            with self.assertRaises(youtube.ErroreYouTube) as ctx:
                youtube.chiama("search", {"q": "x"}, "SEGRETA")
        self.assertIn("quotaExceeded", str(ctx.exception))
        self.assertNotIn("SEGRETA", str(ctx.exception))
        self.assertNotIn("SEGRETA", youtube.url_senza_chiave("https://x/search?q=1&key=SEGRETA"))

    # --- YT-06: nessuna chiave nel sito né nei dati pubblicati ---
    def test_yt06_nessuna_chiave_nei_file_pubblicati(self):
        chiave = youtube.FILE_CHIAVE.read_text(encoding="utf-8").strip() if youtube.FILE_CHIAVE.exists() else None
        modello = re.compile(r"AIza[0-9A-Za-z_-]{35}")
        cartelle = [componi.WEB, self._dati_originali / "esterni", self._dati_originali / "percorsi"]
        for cartella in cartelle:
            for f in cartella.rglob("*"):
                if f.suffix not in {".js", ".json", ".html", ".css", ".md"} or "candidati" in f.name:
                    continue
                testo = f.read_text(encoding="utf-8", errors="ignore")
                self.assertIsNone(modello.search(testo), f)
                if chiave:
                    self.assertNotIn(chiave, testo, f)

    # --- YT-07: la vista pubblica non mostra bozze ---
    def test_yt07_pubblico_senza_suggerimenti_in_bozza(self):
        s = componi.componi(ID, pubblico=True)
        self.assertEqual(s["pulse"]["contenuti"], [])
        self.assertEqual(s["percorsi"], [])
        self.assertEqual(s["connessioni"], [])

    def test_yt07_pubblico_mostra_solo_i_pubblicati(self):
        vid = componi.componi(ID)["pulse"]["contenuti"][0]["video_id"]
        self._cura(lambda d: next(c for c in d["contenuti"] if c["video_id"] == vid).update(stato="pubblicato"))
        s = componi.componi(ID, pubblico=True)
        self.assertEqual([v["video_id"] for v in s["pulse"]["contenuti"]], [vid])

    # --- YT-08 (lato dati): collegamenti alle regioni motivati ---
    def test_yt08_collegamento_a_regione_inesistente_rifiutato(self):
        self._cura(lambda d: d["contenuti"][0]["annotazioni"].append({"id": "a99", "motivazione": "x"}))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_yt08_collegamento_senza_motivazione_rifiutato(self):
        self._cura(lambda d: d["contenuti"][0]["annotazioni"].append({"id": "a01", "motivazione": ""}))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(ID)

    def test_pul04_almeno_tre_contenuti_collegati_a_regioni(self):
        p = componi.componi(ID)["pulse"]
        self.assertGreaterEqual(sum(1 for v in p["contenuti"] if v["annotazioni"]), 3)

    # --- punteggio spiegabile (§6.3) ---
    def test_punteggio_spiegabile_e_diversita(self):
        p = componi.componi(ID)["pulse"]
        for percorso, sel in p["selezioni"].items():
            canali = set()
            for s in sel:
                self.assertEqual(set(s["componenti"]), set(componi.PESI))
                atteso = sum(componi.PESI[k] * v for k, v in s["componenti"].items())
                self.assertAlmostEqual(s["punteggio"], atteso, places=2)
                canale = next(v["canale_id"] for v in p["contenuti"] if v["video_id"] == s["id"])
                self.assertEqual(s["componenti"]["diversita"], 0.0 if canale in canali else 1.0)
                canali.add(canale)


class ProveRacconto(Base):
    """Racconto a scene, fonti lette, opere di istituzioni diverse (Louvre)."""

    G = "gioconda"

    def test_gioconda_composta_dal_louvre(self):
        s = componi.componi(self.G)
        c = s["opera"]["catalogo"]
        self.assertEqual(s["opera"]["id"], "louvre:cl010062370")
        self.assertIn("INV 779", c["istituzione"][0]["inventario"])
        self.assertIn("stessa persona", c["attribuzione_in_evidenza"]["motivazione"])
        self.assertEqual(len(s["bibliografia_museo"]), 52)
        self.assertEqual(len(s["annotazioni"]), 19)

    def test_racconto_ogni_frase_documentata_ha_fonti(self):
        for chiave in (ID, self.G):
            r = componi.componi(chiave)["racconto"]
            for sc in r["scene"]:
                for fr in sc["frasi"]:
                    if fr["r"] in ("documentato", "interpretazione"):
                        self.assertTrue(fr.get("f"), (chiave, sc["id"], fr["t"][:40]))

    def test_frase_documentata_senza_fonti_rifiutata(self):
        self._modifica(f"racconti/{self.G}.json", lambda d: d["scene"][0]["frasi"][1].update(f=[]))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(self.G)

    def test_fonte_non_consultata_non_sostiene_affermazioni(self):
        self._modifica(f"racconti/{self.G}.json",
                       lambda d: d["scene"][0]["frasi"][1].update(f=[{"fonte": "smarthistory-monalisa"}]))
        with self.assertRaises(componi.ErroreValidazione) as ctx:
            componi.componi(self.G)
        self.assertIn("non è stata consultata", str(ctx.exception))

    def test_regione_inesistente_nel_racconto_rifiutata(self):
        self._modifica(f"racconti/{self.G}.json", lambda d: d["scene"][1]["frasi"][0].update(a="g99"))
        with self.assertRaises(componi.ErroreValidazione):
            componi.componi(self.G)

    def test_uscite_dal_quadro_risolte(self):
        r = componi.componi(self.G)["racconto"]
        fuori = [fr["fuori"] for sc in r["scene"] for fr in sc["frasi"] if fr.get("fuori")]
        self.assertGreaterEqual(len(fuori), 5)
        for fu in fuori:
            self.assertTrue(fu["scheda"]["immagine"], fu["wikidata"])
            self.assertTrue(fu["scheda"]["immagine"]["licenza"])

    def test_pubblico_nasconde_il_racconto_in_bozza(self):
        s = componi.componi(self.G, pubblico=True)
        self.assertIsNone(s["racconto"])
        self.assertEqual(s["annotazioni"], [])

    def test_certezza_concorde_solo_con_fonti_indipendenti(self):
        reg = componi.componi(self.G)["fonti"]
        due = {"registro": "documentato", "fonti": [{"fonte": "louvre-cl010062370-commento"}, {"fonte": "probst-2008"}]}
        stesso_museo = {"registro": "documentato", "fonti": [{"fonte": "louvre-cl010062370-commento"}, {"fonte": "louvre-cl010062370"}]}
        self.assertEqual(componi.certezza(due, reg)["livello"], "concorde")
        self.assertNotEqual(componi.certezza(stesso_museo, reg)["livello"], "concorde")


if __name__ == "__main__":
    unittest.main(verbosity=2)
