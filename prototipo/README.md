# ArtNotes — prototipo (Fasi 2 e 2.5)

Due opere: Pieter Bruegel il Vecchio, *I mietitori* (Met 435809), e Leonardo, *La Gioconda* (Louvre, `?opera=gioconda`). Per ciascuna:

- un **racconto a scene**, leggibile come testo con note alle fonti oppure come **visita guidata** a schermo intero: la camera segue la narrazione, le etichette compaiono al momento giusto, il racconto esce dal quadro per mostrare l'autore o altre opere;
- immagine esplorabile, livelli di lettura e annotazioni collegate al testo, con registri etichettati (Fase 2);
- tre percorsi di visita, connessioni tipizzate con altre opere, video suggeriti (ArtNotes Pulse, per ora solo sui Mietitori) e un taccuino locale (Fase 2.5);
- un **registro delle fonti** per categoria (museo, fonte d'epoca, letteratura, laboratorio, dati collaborativi, immagini), ciascuna con il livello di lettura dichiarato. Una fonte non letta non può sostenere nessuna frase: la composizione si ferma.

## Avvio

Requisiti: Python 3 con Pillow. Il browser carica OpenSeadragon 4.1.1 da cdnjs, quindi serve la connessione.

```
cd progetti/Galleria_Arte/prototipo/web
python -m http.server 8765 --bind 127.0.0.1
```

Poi aprire:

- <http://127.0.0.1:8765/> — anteprima redazionale, con la scelta «Che cosa vuoi scoprire oggi?»;
- <http://127.0.0.1:8765/?opera=gioconda> — la Gioconda; il pulsante «▶ Visita guidata» apre la visita a schermo intero (Esc per uscire, ←/→ frasi, PagSu/PagGiù scene, barra spaziatrice per la pausa);
- <http://127.0.0.1:8765/?percorso=curioso> — un percorso (`curioso`, `studio`, `ispirazione`, `libera`);
- <http://127.0.0.1:8765/?percorso=studio&tappa=s4#a13> — percorso, tappa e dettaglio insieme, da condividere;
- <http://127.0.0.1:8765/?vista=pubblico> — vista del lettore: solo contenuti pubblicati, oggi nessuno. Il vecchio `?modo=pubblico` funziona ancora;
- <http://127.0.0.1:8765/#a13> — apre direttamente un dettaglio.

## Ricostruire i dati

```
python strumenti/importa.py met 435809                          # payload Met, immagine, tile Deep Zoom
python strumenti/importa.py louvre cl010062370                  # scheda del Louvre (testi Etalab; foto non riusate)
python strumenti/importa.py immagine-commons "File.jpg" chiave  # immagine di lavoro da Commons + tile
python strumenti/importa.py wikidata Q12418                     # payload Wikidata con etichette
python strumenti/importa.py commons "File.jpg"                  # licenza e miniatura locale da Commons
python strumenti/letteratura.py openalex gioconda               # candidati bibliografici (OpenAlex, CC0)
python strumenti/letteratura.py hal gioconda                    # candidati dall'archivio aperto HAL
python strumenti/letteratura.py testo <id> <url> [licenza]      # testo di un articolo o pagina ad accesso aperto
python strumenti/letteratura.py wikisource <id> it "<pagina>"   # fonte d'epoca da Wikisource
python strumenti/youtube.py cerca 435809                        # candidati da YouTube (circa 800 unità di quota)
python strumenti/youtube.py verifica 435809                     # riverifica i soli video curati (1 unità)
python strumenti/componi.py --tutte                             # compone tutte le opere e l'indice
python strumenti/prove.py                                       # 49 prove automatiche
```

I candidati bibliografici sono solo metadati: una fonte entra nel registro curato (`dati/bibliografia/<opera>.json`) con il livello di lettura effettivo. I testi completi scaricati restano in locale (`dati/testi/*.txt`, esclusi da git); nel repository restano i metadati di acquisizione con l'impronta SHA-256.

L'importazione si può ripetere: non crea duplicati e non rigenera le tile se l'immagine non è cambiata (stessa impronta SHA-256).

### Chiave YouTube

`youtube.py` legge la chiave da `YOUTUBE_API_KEY` oppure da `~/.artnotes/youtube_api_key.txt`, cioè fuori dal repository. La chiave non va mai nel sito: lo script scrive solo i metadati dei video curati e il sito li legge già composti. I messaggi d'errore e i payload salvati non contengono la chiave: negli URL compare `key=REDATTA`.

I metadati vanno riverificati entro 30 giorni (`youtube.py verifica`). Dopo quel termine un video resta visibile solo in anteprima, con l'avviso «da ricontrollare», e sparisce dalla vista pubblica.

## Struttura

| Percorso | Contenuto | Strato |
|---|---|---|
| `dati/opere/` | Configurazione di ogni opera: istituzione, Wikidata, immagine, query | Identità |
| `dati/racconti/` | Racconto a scene: frasi con registro, fonti, regione, uscite dal quadro | Narrazione |
| `dati/bibliografia/` | Registro curato delle fonti con categoria e livello di lettura | Fonti |
| `dati/testi/` | Testi acquisiti (solo metadati nel repository) | Fonti |
| `dati/fonti/` | Payload originali con URL, data e versione del connettore (Met, Louvre, Wikidata, Commons, SPARQL) | Catalogo (record di fonte) |
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
