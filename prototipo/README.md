# ArtNotes — prototipo (Fasi 2 e 2.5)

Una sola opera completa: Pieter Bruegel il Vecchio, *The Harvesters* (Met 435809). Comprende immagine esplorabile, livelli di lettura, annotazioni collegate al testo, registri narrativi etichettati e fonti (Fase 2). Ci sono poi tre percorsi di visita, connessioni con altre opere, i video suggeriti di ArtNotes Pulse e un taccuino locale (Fase 2.5).

## Avvio

Requisiti: Python 3 con Pillow. Il browser carica OpenSeadragon 4.1.1 da cdnjs, quindi serve la connessione.

```
cd progetti/Galleria_Arte/prototipo/web
python -m http.server 8765 --bind 127.0.0.1
```

Poi aprire:

- <http://127.0.0.1:8765/> — anteprima redazionale, con la scelta «Che cosa vuoi scoprire oggi?»;
- <http://127.0.0.1:8765/?percorso=curioso> — un percorso (`curioso`, `studio`, `ispirazione`, `libera`);
- <http://127.0.0.1:8765/?percorso=studio&tappa=s4#a13> — percorso, tappa e dettaglio insieme, da condividere;
- <http://127.0.0.1:8765/?vista=pubblico> — vista del lettore: solo contenuti pubblicati, oggi nessuno. Il vecchio `?modo=pubblico` funziona ancora;
- <http://127.0.0.1:8765/#a13> — apre direttamente un dettaglio.

## Ricostruire i dati

```
python strumenti/importa.py met 435809            # payload Met, immagine, tile Deep Zoom
python strumenti/importa.py wikidata Q776175      # payload Wikidata con etichette (anche Q3855265, Q500985, ...)
python strumenti/importa.py commons "File.jpg"    # licenza e miniatura locale da Wikimedia Commons
python strumenti/youtube.py query 435809          # mostra le query, senza chiamare l'API
python strumenti/youtube.py cerca 435809          # candidati da YouTube (circa 800 unità di quota)
python strumenti/youtube.py verifica 435809       # riverifica i soli video curati (1 unità)
python strumenti/componi.py 435809                # web/api/opere/435809.json (anteprima)
python strumenti/componi.py 435809 --pubblico     # web/api/opere/435809.pubblico.json
python strumenti/prove.py                         # 41 prove automatiche
```

L'importazione si può ripetere: non crea duplicati e non rigenera le tile se l'immagine non è cambiata (stessa impronta SHA-256).

### Chiave YouTube

`youtube.py` legge la chiave da `YOUTUBE_API_KEY` oppure da `~/.artnotes/youtube_api_key.txt`, cioè fuori dal repository. La chiave non va mai nel sito: lo script scrive solo i metadati dei video curati e il sito li legge già composti. I messaggi d'errore e i payload salvati non contengono la chiave: negli URL compare `key=REDATTA`.

I metadati vanno riverificati entro 30 giorni (`youtube.py verifica`). Dopo quel termine un video resta visibile solo in anteprima, con l'avviso «da ricontrollare», e sparisce dalla vista pubblica.

## Struttura

| Percorso | Contenuto | Strato |
|---|---|---|
| `dati/fonti/` | Payload originali con URL, data e versione del connettore (Met, Wikidata, Commons) | Catalogo (record di fonte) |
| `dati/fonti/youtube/` | Risposte grezze di YouTube: solo in locale, escluse da git | Fonte esterna |
| `dati/immagini/` | Versione dell'immagine: impronta, dimensioni, colore, diritti separati per livello | Catalogo (immagine) |
| `dati/contenuti/` | Testi per sezione, a blocchi, con registro, fonti, origine e stato | Conoscenza |
| `dati/annotazioni/` | Regioni in coordinate percentuali legate all'impronta dell'immagine | Annotazioni visive |
| `dati/connessioni/` | Legami con altre opere, tipizzati: documentato, interpretativo, calcolato | Conoscenza (relazioni) |
| `dati/percorsi/` | Tappe dei tre percorsi: ordine, domande, consegne. Richiamano i contenuti per identificativo | Presentazione |
| `dati/esterni/` | Cura di ArtNotes Pulse: relazione, motivo, affidabilità, regioni collegate, stato | Contenuti esterni |
| `dati/esterni/youtube/` | Metadati minimi dei video curati (i candidati restano esclusi da git) | Contenuti esterni |
| `strumenti/componi.py` | Valida e compone la scheda letta dall'interfaccia | Confine dell'API |
| `web/` | Interfaccia: legge solo `web/api/opere/*.json` | Consultazione |
| `web/immagini/confronti/` | Miniature delle opere collegate (Commons, pubblico dominio) | Consultazione |
| `originali/` | File immagine sorgente, da non pubblicare | — |

L'interfaccia non conosce la struttura di `dati/`: legge solo la scheda composta. Una futura app nativa potrà leggere lo stesso formato.

## Cosa è e cosa non è

- **Tutti i testi, le regioni, i percorsi, le connessioni e le classificazioni dei video sono bozze generate da AI e non revisionate.** In modalità pubblica non compaiono.
- I video sono stati classificati leggendo titolo, descrizione e canale, **senza guardarli**. Ogni scheda lo dichiara.
- Il taccuino e le note restano nel browser (`localStorage`): niente account e niente invio di dati. Si possono scaricare in Markdown o cancellare.
- Il testo critico e la bibliografia del Met mancano: la pagina del museo ha risposto 429 durante la preparazione. Il prototipo dichiara la lacuna invece di colmarla.
- Le regioni sono soltanto rettangoli. Punti e poligoni non sono ancora supportati.
- Non ci sono backend, database, account né pannello redazionale: arriveranno nella Fase 3.
