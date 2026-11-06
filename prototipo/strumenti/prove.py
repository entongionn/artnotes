"""Prove automatiche sulla composizione della scheda (criteri §21 della specifica).

Uso:
    python strumenti/prove.py
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import componi  # noqa: E402

ID = "435809"


class ProveScheda(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
