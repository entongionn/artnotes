# ArtNotes — Fase 2: prototipo dell'esperienza visiva

Data: **6 novembre 2026**. Opera: Pieter Bruegel il Vecchio, *The Harvesters* (Met 435809).
Istruzioni d'uso: [prototipo/README.md](prototipo/README.md).

---

## 1. Risultati

Ora c'è un'opera completa ed esplorabile:

- **Visualizzatore** a tile (OpenSeadragon 4.1.1, formato Deep Zoom generato in proprio dalla fotografia Met da 3811 × 2809 px):
  - zoom, spostamento, adattamento alla finestra, schermo intero e miniatura di navigazione;
  - lo zoom si ferma a 1,5 volte la risoluzione reale e l'interfaccia dichiara che nessun dettaglio viene ricostruito.
- **14 regioni** rettangolari in quattro **livelli** attivabili separatamente: osservazione guidata (7), iconografia (3), composizione (2), tecnica (2). All'avvio è attivo solo il primo livello, per non sovrapporre tutto.
- **Collegamento testo-immagine** in entrambe le direzioni:
  - un clic su una regione apre il testo;
  - la scelta di un dettaglio dall'elenco o da una sezione inquadra la regione;
  - i dettagli collegati rimandano l'uno all'altro;
  - ogni dettaglio ha un indirizzo proprio (`#a05`), quindi si può condividere e riprendere.
- **Elenco testuale** di tutti i dettagli: si raggiungono senza cercare le regioni sull'immagine.
- **Registri narrativi** approvati, su ogni blocco di testo:
  - etichetta con testo e simbolo, non solo colore;
  - base documentale con le fonti;
  - origine «generato da AI»;
  - stato e revisione.
- **Riquadro di copertura** con le quattro dimensioni separate (§9.4).
- **Scheda di catalogo** con ogni dato affiancato alla sua fonte, nella formulazione originale. Mostra l'attribuzione in evidenza con la motivazione e i diritti separati per metadati, fotografia e opera.
- **Modalità pubblica** (`?modo=pubblico`): mostra solo i contenuti pubblicati. Oggi nessuno lo è, quindi il lettore vede solo il catalogo e un avviso.

### Cosa mostra l'opera sul metodo

- **Dati che le fonti non danno.** Nell'angolo in basso a destra si leggono le lettere «BRVEGE…». L'API del Met non riporta iscrizioni. Il dettaglio a13 lo mostra come *osservazione* più *lacuna* e non come dato.
- **Ipotesi calcolate e dichiarate.** Il Met documenta strisce aggiunte al pannello, da 119 × 162 cm contro 116,5 × 159,5 cm originali. La regione a14 ne colloca una calcolandola dalle misure, ed è etichettata come *ipotesi* non verificata sull'immagine.
- **Fonti deboli segnalate.** Dei 7 proprietari elencati da Wikidata solo 2 hanno un riferimento. La tabella in «Contesto» lo dice riga per riga.
- **Lacune esplicite.** Senza il testo critico del Met (pagina irraggiungibile, errore 429), le sezioni dichiarano cosa manca invece di riempirlo.

## 2. File creati

| File | Ruolo |
|---|---|
| [prototipo/strumenti/importa.py](prototipo/strumenti/importa.py) | Importazione ripetibile da Met e Wikidata: payload originali, immagine, tile, impronta SHA-256 |
| [prototipo/strumenti/componi.py](prototipo/strumenti/componi.py) | Validazione e composizione della scheda: è il confine dell'API |
| [prototipo/strumenti/prove.py](prototipo/strumenti/prove.py) | 12 prove automatiche |
| [prototipo/dati/contenuti/435809.json](prototipo/dati/contenuti/435809.json) | 16 blocchi di testo in 6 sezioni |
| [prototipo/dati/annotazioni/435809.json](prototipo/dati/annotazioni/435809.json) | 14 regioni legate all'impronta dell'immagine |
| `prototipo/dati/fonti/`, `prototipo/dati/immagini/` | Payload e metadati dell'immagine (generati) |
| [prototipo/web/](prototipo/web/) | Interfaccia: `index.html`, `app.js`, `style.css`, tile, scheda composta |
| [prototipo/README.md](prototipo/README.md) | Avvio e struttura |

Ho anche aggiornato [FASE1_rapporto.md](FASE1_rapporto.md) (§10) con le decisioni prese.

## 3. Prove eseguite

**Prove automatiche** (`strumenti/prove.py`, 12 su 12 superate):

- la modalità pubblica esclude le bozze e mostra solo ciò che è pubblicato;
- cambiare l'immagine marca tutte le regioni «da riverificare»;
- le coordinate restano dentro l'immagine e le regioni che escono vengono rifiutate;
- vengono rifiutati i blocchi «documentato» senza fonti, quelli con fonti inesistenti e i registri non validi;
- l'origine AI è presente su ogni blocco e annotazione;
- la concordanza delle attribuzioni si calcola sugli identificativi e non sui nomi. Questa prova è nata da un errore reale: il primo confronto per nome trattava «the Elder» e «il Vecchio» come autori diversi.

**Prove nel browser** (Chrome headless pilotato via DevTools Protocol), **tutte superate**:

| Criterio §21 | Esito |
|---|---|
| Telefono (390 × 844, tocco) | Nessuno scorrimento orizzontale (larghezza 390 = 390). Pagina e dettaglio leggibili |
| Tastiera | Ordine di tabulazione: link di salto, comandi, visualizzatore, livelli, dettagli, schede. Invio su un dettaglio porta il focus al titolo del testo. Esc chiude e riporta il focus al dettaglio. Le frecce scorrono le schede |
| Coerenza delle regioni | Verificata a occhio su screenshot a vista intera, da telefono e con forte ingrandimento (a13): le regioni restano sui soggetti |
| Livelli | 7 regioni visibili all'avvio, 10 dopo l'attivazione dell'iconografia |
| Movimento ridotto | Con `prefers-reduced-motion` le animazioni partono disattivate |
| Indirizzi | `#a13` apre il dettaglio. Anche il cambio di hash a pagina aperta funziona |
| Modalità pubblica | 0 regioni, 0 blocchi, avviso esplicito |
| Errori | Nessun errore o eccezione in console |

Durante le prove ho corretto diversi problemi:

- le regioni dei livelli disattivati restavano visibili;
- su telefono le etichette sovrapposte coprivano l'opera;
- l'elenco usciva dallo schermo;
- dopo Esc il focus si perdeva;
- il cambio di hash non era gestito;
- il favicon dava 404.

## 4. Limiti e prove non eseguite

- **Nessun contenuto è revisionato da una persona.** Regioni e osservazioni sono state tracciate dall'AI guardando la fotografia: una revisione umana è il prossimo controllo necessario.
- Nessuna prova su un telefono reale né con uno screen reader reale (NVDA, VoiceOver). Le prove di tastiera e telefono sono emulate.
- Lo stato «da riverificare» è provato nella composizione ma non visualizzato in uno screenshot.
- Regioni solo rettangolari: punti e poligoni non sono ancora supportati.
- Annotazioni nel formato interno, con selettore Media Fragments `xywh=percent:`. L'esportazione completa in Web Annotation non è implementata.
- OpenSeadragon arriva da CDN: senza rete il visualizzatore non parte.
- Nessuna prova con utenti reali sullo stile narrativo (§5.4 del rapporto di Fase 1).
- La fotografia ad altissima risoluzione su Commons (30000 px) non è stata usata. È una fotografia diversa e richiederebbe nuove regioni.

## 5. Passo successivo

Prima di passare alla Fase 3 propongo due cose:

1. **Una tua revisione del prototipo.** Apri le pagine e dimmi se lo stile delle etichette, la densità dei testi e il comportamento dei livelli funzionano. Puoi anche correggere o rifiutare singole osservazioni: il primo flusso di revisione reale ci dirà che cosa serve al pannello redazionale.
2. **La seconda opera, quella attribuita ad Anguissola**, come prova del caso scarso (bassa risoluzione, attribuzione discordante). La struttura attuale dovrebbe reggerla senza modifiche: è una verifica utile prima di definire lo schema del database.

Fase 3: schema PostgreSQL basato sui dati osservati, migrazioni, pannello minimo per testi e regioni, flusso bozza → revisione → pubblicazione.
