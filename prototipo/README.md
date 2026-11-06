# ArtNotes — prototipo della Fase 2

Una sola opera completa: Pieter Bruegel il Vecchio, *The Harvesters* (Met 435809). Comprende immagine esplorabile, livelli di lettura, annotazioni collegate al testo, registri narrativi etichettati e fonti.

## Avvio

Requisiti: Python 3 con Pillow. Il browser carica OpenSeadragon 4.1.1 da cdnjs, quindi serve la connessione.

```
cd progetti/Galleria_Arte/prototipo/web
python -m http.server 8765 --bind 127.0.0.1
```

Poi aprire:

- <http://127.0.0.1:8765/> — anteprima redazionale (mostra le bozze);
- <http://127.0.0.1:8765/?modo=pubblico> — vista del lettore: solo contenuti pubblicati, oggi nessuno;
- <http://127.0.0.1:8765/#a13> — apre direttamente un dettaglio.

## Ricostruire i dati

```
python strumenti/importa.py met 435809        # payload Met, immagine, tile Deep Zoom
python strumenti/importa.py wikidata Q776175  # payload Wikidata con etichette
python strumenti/componi.py 435809            # web/api/opere/435809.json (anteprima)
python strumenti/componi.py 435809 --pubblico # web/api/opere/435809.pubblico.json
python strumenti/prove.py                     # 12 prove automatiche
```

L'importazione si può ripetere: non crea duplicati e non rigenera le tile se l'immagine non è cambiata (stessa impronta SHA-256).

## Struttura

| Percorso | Contenuto | Strato (specifica §6) |
|---|---|---|
| `dati/fonti/` | Payload originali con URL, data e versione del connettore | Catalogo (record di fonte) |
| `dati/immagini/` | Versione dell'immagine: impronta, dimensioni, colore, diritti separati per livello | Catalogo (immagine) |
| `dati/contenuti/` | Testi per sezione, a blocchi, con registro, fonti, origine e stato | Conoscenza |
| `dati/annotazioni/` | Regioni in coordinate percentuali legate all'impronta dell'immagine | Annotazioni visive |
| `strumenti/componi.py` | Valida e compone la scheda letta dall'interfaccia | Confine dell'API |
| `web/` | Interfaccia: legge solo `web/api/opere/*.json` | Consultazione |
| `originali/` | File immagine sorgente, da non pubblicare | — |

L'interfaccia non conosce la struttura di `dati/`: legge solo la scheda composta. Una futura app nativa potrà leggere lo stesso formato.

## Cosa è e cosa non è

- **Tutti i testi e le regioni sono bozze generate da AI e non revisionate.** In modalità pubblica non compaiono.
- Il testo critico e la bibliografia del Met mancano: la pagina del museo ha risposto 429 durante la preparazione. Il prototipo dichiara la lacuna invece di colmarla.
- Le regioni sono soltanto rettangoli. Punti e poligoni non sono ancora supportati.
- Non ci sono backend, database, account né pannello redazionale: arriveranno nella Fase 3.
