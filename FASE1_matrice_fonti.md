# ArtNotes — Fase 1: matrice delle fonti

Data di consultazione e prove: **6 novembre 2026**.
Documento collegato: [FASE1_rapporto.md](FASE1_rapporto.md).

## Come leggere questa matrice

Ogni informazione porta uno di questi marcatori:

- **[P]** verificato con una prova diretta su un campione (richiesta HTTP eseguita, risposta osservata);
- **[D]** dichiarato dalla documentazione ufficiale consultata, non verificato con una prova;
- **[?]** non determinato: va verificato prima di qualsiasi uso pubblico.

Le prove sono state eseguite senza account e senza chiavi personali, con un client identificato come `ArtNotes-Phase1-SourceSurvey/0.1`. Per Europeana è stata usata la chiave dimostrativa pubblica `api2demo`, non adatta a un uso reale.

Nessuna di queste note costituisce parere legale. Le condizioni d'uso vanno rilette al momento dell'importazione e prima del lancio pubblico (specifica, §18).

---

## Sintesi

| Fonte | Accesso | Metadati | Immagini | IIIF | Aggiornamento incrementale | Ruolo proposto |
|---|---|---|---|---|---|---|
| **Metropolitan Museum of Art** — Collection API | REST, nessuna chiave [D][P] | CC0 [D] | Pubblico dominio se `isPublicDomain = true` [D] | Non menzionato [D] | Sì, filtro `metadataDate` [D] | Fonte primaria per opere del Met |
| **Art Institute of Chicago** — API | REST, nessuna chiave [P] | CC0, ma campo `description` CC BY 4.0 [P] | Per opera, `is_public_domain` [P] | Sì, server IIIF Image API 2 [P], ma bloccato a richieste da script [P] | [?] | Fonte primaria per opere AIC |
| **Wikidata** | SPARQL, REST, Action API, dump [D][P] | CC0 [D] | Nessuna (rimanda a Commons) | — | Recent Changes stream, dump [D] | Identità e collegamenti fra fonti; mai fonte unica per l'attribuzione |
| **Wikimedia Commons** | Action API (`imageinfo` + `extmetadata`) [P] | Licenza diversa per ogni file [D][P] | Licenza diversa per ogni file [D][P] | Non nativo [?] | [?] | Immagini alternative ad alta risoluzione, solo dopo controllo per file |
| **Europeana** — Search/Record API | REST, chiave obbligatoria [P] | [?] (pagina documentazione non raggiungibile, 403) | Per record, campo `rights` eterogeneo [P] | [?] | [?] | Scoperta di materiali correlati, non catalogo primario dei dipinti |
| **ICCD — Catalogo generale dei beni culturali / ArCo** | SPARQL `dati.cultura.gov.it/sparql` [P] | **[?] contraddittorio** | **[?]** | Non osservato [P] | [?] | Fonte molto ricca per opere italiane poco note, **bloccata fino a chiarimento delle licenze** |

---

## 1. Metropolitan Museum of Art — Collection API

| Voce | Rilevazione |
|---|---|
| Responsabile e documentazione | The Metropolitan Museum of Art. Documentazione: <https://metmuseum.github.io/> [D]. Contatto: openaccess@metmuseum.org [D]. |
| Accesso e autenticazione | Nessuna registrazione o chiave [D], confermato [P]. Limite dichiarato: 80 richieste al secondo [D]. |
| Endpoint | `/v1/objects` (elenco ID, filtri `metadataDate` e `departmentIds`), `/v1/objects/{id}`, `/v1/departments`, `/v1.1/search` [D]. **La vecchia `/v1/search` è stata ritirata il 1° ottobre 2026**: oggi risponde con un messaggio che rimanda a `/v1.1/search` [P]. La ricerca v1.1 è paginata: `limit` massimo 500, `offset + limit` non oltre 10.000 [D]. |
| Identificativi | `objectID`, `accessionNumber`. Collegamenti esterni per opera e artista: Wikidata e Getty ULAN (`objectWikidata_URL`, `artistWikidata_URL`, `artistULAN_URL`) [P]. |
| Campi utili e qualità | Titolo, artista con **`artistPrefix`** («Attributed to», «Workshop of», «Follower of», «Style of», «?») [P]. Data come testo originale (`objectDate`, es. «ca. 1662», «probably ca. 1658–62») e come intervallo numerico (`objectBeginDate`/`objectEndDate`) [P]. Tecnica, dimensioni testuali e strutturate, credit line, tag collegati a Getty AAT e Wikidata, `metadataDate` [P]. **Nessun testo critico o bibliografia** nell'API [P]. |
| Problemi di qualità osservati | `objectDate` vuoto mentre l'intervallo numerico è presente (436472: vuoto, ma 1520–1530) [P]. In un caso il nome del costituente incorpora la qualifica («Attributed to Lucia Anguissola») ed è privo di collegamenti Wikidata/ULAN (436749) [P]. |
| Condizioni dei metadati | CC0 [D]. Uso dell'API soggetto ai termini e condizioni del Met [D]. |
| Condizioni delle immagini | Immagini ad alta risoluzione per le opere in pubblico dominio, indicate da `isPublicDomain`. Per le opere protette, `rightsAndReproduction` riporta la linea di credito [D]. |
| Memorizzare, visualizzare, redistribuire | Coerente con CC0 e pubblico dominio [D]. Termini e condizioni da rileggere prima dell'importazione [?]. |
| Immagini: risoluzione osservata | *The Harvesters*: originale 3,0 MB, 10 immagini aggiuntive [P]. *Portrait of a Man*, attribuito a Lucia Anguissola: originale **680 × 694 px** [P]. *The Circumcision*, bottega di Giovanni Bellini: unica immagine **in bianco e nero**, 3755 × 2475 px [P]. |
| IIIF | Non menzionato nella documentazione [D]. Servono tile o derivate generate in proprio. |
| Aggiornamento | Incrementale con `metadataDate` [D]. Ogni record ha il proprio `metadataDate` [P]. |
| Campione provato | 437881, 435809, 436749, 435643, 436472, 437406, 438619 (nessuna immagine, `isPublicDomain = false` senza note sui diritti), più una ricerca v1.1 su «attributed to» (dipartimento 11, 40 risultati scorsi) [P]. |

## 2. Art Institute of Chicago — API

| Voce | Rilevazione |
|---|---|
| Responsabile e documentazione | Art Institute of Chicago, <https://api.artic.edu/docs/>. La pagina di documentazione ha risposto 403 al client automatico: **la documentazione non è stata letta** [P]. |
| Accesso | `GET /api/v1/artworks/{id}?fields=…` funziona senza chiave [P]. |
| Campi | `date_start`/`date_end` più `date_display` testuale (es. «1884–86, border added 1888–89»), `artist_display`, tecnica, dimensioni, credit line, `is_public_domain`, `image_id` [P]. |
| Condizioni dei metadati | La risposta stessa dichiara: campo `description` sotto CC BY 4.0, tutti gli altri dati CC0, più i Terms and Conditions di artic.edu [P]. Conseguenza: **i due regimi di licenza vanno conservati separatamente anche all'interno dello stesso record**. |
| Immagini e IIIF | La risposta indica un server IIIF Image API 2 (`https://www.artic.edu/iiif/2`) [P]. Le richieste da script a `info.json` hanno ricevuto una pagina di verifica anti-bot (Cloudflare) [P]. Il funzionamento da browser, cioè dal visualizzatore, **non è stato provato** [?]. |
| Aggiornamento, limiti, dump | [?] Da leggere nella documentazione. |
| Campione provato | 27992 (*A Sunday on La Grande Jatte — 1884*) [P]. |

## 3. Wikidata

| Voce | Rilevazione |
|---|---|
| Responsabile e documentazione | Wikimedia Foundation e comunità Wikidata. <https://www.wikidata.org/wiki/Wikidata:Data_access> [D]. |
| Accesso | Query Service SPARQL, REST API (ancora in sviluppo), Action API (fino a 50 entità per richiesta), GraphQL, dump, Recent Changes stream [D]. Action API provata [P]. |
| Regole operative | User-Agent descrittivo, risposte compresse, niente raffiche di richieste concorrenti. Con risposta 429 va rispettato `Retry-After`. Con l'Action API si usa `maxlag`. Per grandi volumi si usano i dump [D]. |
| Condizioni dei dati | Dati strutturati CC0. Attribuzione non obbligatoria ma incoraggiata [D]. |
| Qualità osservata: copertura | Forte disparità [P]. *Mietitura* (Bruegel, Q776175): 86 asserzioni, 24 voci Wikipedia collegate, 28 asserzioni «raffigura». *Portrait of a Man* attribuito ad Anguissola (Q19914251): 18 asserzioni, **0 voci Wikipedia**, autore **senza riferimenti**. |
| Qualità osservata: attribuzione | **Conflitto** [P]. Il Met scrive «Attributed to Lucia Anguissola». Wikidata registra l'autore come valore sconosciuto, con ruolo «anonimo» (P3831 = Q4233718) e senza riferimenti. Per la bottega di Bellini (Q19905123) usa invece il qualificatore P1774 «bottega di». |
| Ruolo proposto | Ponte fra identificativi (Met, ULAN, Commons) e fonte di etichette multilingue. **Mai fonte unica di un'attribuzione**: l'attribuzione si conserva fonte per fonte. |
| Campione provato | Q776175, Q386453, Q19914251, Q19913061, Q19905123 [P]. |

## 4. Wikimedia Commons

| Voce | Rilevazione |
|---|---|
| Responsabile e documentazione | Wikimedia Foundation e comunità. <https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia> [D]. |
| Accesso | Action API `prop=imageinfo&iiprop=url\|size\|extmetadata`. Restituisce licenza, autore, credito e se l'attribuzione è richiesta [P]. |
| Condizioni | **Licenza diversa per ogni file**, da verificare file per file. Nessuna garanzia sullo stato dei diritti. Possibili vincoli non legati al diritto d'autore (personalità, marchi). Si accredita il creatore, non chi ha caricato il file [D]. |
| PD-Art | Le riproduzioni fedeli di opere bidimensionali in pubblico dominio sono trattate come prive di nuovo diritto d'autore, sulla base della sentenza statunitense *Bridgeman v. Corel*. La pagina avverte che altri Paesi possono valutare diversamente. **Non vale per le fotografie di opere tridimensionali**, come le sculture [D]. |
| Hotlinking | Possibile ma «non raccomandato» [D]. |
| Qualità osservata | *The Harvesters*, file «Google Art Project»: **30000 × 21851 px, 223 MB**, pubblico dominio [P]. È una fotografia diversa da quella del Met, quindi un'altra versione dell'immagine. *Portrait of a Man*, file donato dal Met: CC0, 680 × 694 px, la stessa bassa risoluzione del Met [P]. |
| IIIF | Non osservato un servizio IIIF nativo [?]. |
| Ruolo proposto | Fonte alternativa di immagini, dopo controllo della licenza di ogni file e registrazione della fotografia esatta usata. |

## 5. Europeana

| Voce | Rilevazione |
|---|---|
| Responsabile e documentazione | Europeana Foundation. Le pagine di documentazione consultate (`pro.europeana.eu`, wiki Confluence) non sono state lette (403 o contenuto non restituito) [P]. |
| Accesso | `api.europeana.eu/record/v2/search.json` con parametro `wskey` obbligatorio. Provato con la chiave dimostrativa [P]. Per un uso reale serve una chiave propria [?]. |
| Qualità osservata | Ricerca libera «Lotto»: il primo risultato è un **gioco da tavolo** di un museo estone [P]. Ricerca `who:"Lotto, Lorenzo"` con `TYPE:IMAGE`: 81 risultati, quasi tutti **stampe, fotografie e derivazioni** («nach Lorenzo Lotto») e non i dipinti [P]. |
| Condizioni | Campo `rights` per record, molto eterogeneo: Public Domain Mark, ma anche RightsStatements «In Copyright» [P]. Licenza dei metadati aggregati [?]. |
| Ruolo proposto | Ricerca mirata di materiali correlati (stampe di traduzione, fotografie storiche, documentazione). Non è adatta come catalogo primario dei dipinti. |

## 6. ICCD — Catalogo generale dei beni culturali / ArCo

| Voce | Rilevazione |
|---|---|
| Responsabile | Istituto Centrale per il Catalogo e la Documentazione (Ministero della Cultura). ArCo è il knowledge graph sviluppato con ISTC-CNR [D, fonti secondarie]. |
| Accesso | Endpoint SPARQL `https://dati.cultura.gov.it/sparql` (il vecchio `dati.beniculturali.it/sparql` reindirizza qui) [P]. Il sito `catalogo.beniculturali.it` ha risposto **401** al client automatico, anche sulla pagina delle note legali [P]. |
| Dimensione | 2.278.836 risorse di tipo `HistoricOrArtisticProperty` [P]. |
| Campi e qualità | Molto ricchi anche per opere poco note. Sul campione (pannello di predella di Lorenzo Lotto, Jesi, scheda 1100139305-2) [P]: **attribuzione «preferita» separata**, con criterio di interpretazione («bibliografia»). Datazione testuale («post 1525-ante 1532»). Notizie storiche. Soggetto e descrizione iconografica. Iscrizioni. Stato di conservazione. Interventi. Localizzazioni storiche. Bibliografia con autore, anno e nota puntuale («fig. 40»). Collegamento all'opera d'insieme. Immagine di documentazione. |
| Attenzione | Il campo `dc:rights` contiene la **condizione giuridica di proprietà** («proprietà Ente pubblico territoriale»), **non una licenza** [P]. |
| Condizioni dei metadati | **[?] Contraddittorie.** Fonti secondarie indicano CC BY-SA 4.0 per il knowledge graph e CC BY-NC-SA per i contenuti del portale. Nell'endpoint, la proprietà `dct:license` compare su circa 2.150 soggetti con licenze diverse (CC0, CC BY 3.0/4.0, CC BY-SA) [P], ma non sulla scheda provata. Non è stata letta alcuna dichiarazione ufficiale applicabile alle schede. |
| Condizioni delle immagini | **[?]** Le immagini su `sigecweb.beniculturali.it` sono scaricabili (campione 270 KB) [P]. Le condizioni di riuso non sono state trovate. Per i beni culturali italiani la riproduzione è regolata anche dal Codice dei beni culturali, oltre che dal diritto d'autore: va verificato con fonti normative e, prima del lancio, con un consulente. |
| Ruolo proposto | Fonte molto promettente per le opere italiane poco documentate, cioè proprio la fascia scarsa richiesta. **Uso limitato all'analisi interna finché licenze e condizioni delle immagini non sono chiarite.** |

---

## Fonti non ancora esaminate (candidate)

Non provate in questa fase:

- Rijksmuseum;
- National Gallery of Art di Washington (open data);
- Cleveland Museum of Art (Open Access);
- Getty ULAN e AAT come vocabolari, già referenziati dal Met;
- Iconclass, già referenziato da Wikidata;
- cataloghi dei musei italiani con portali propri.

Vanno valutate solo se la selezione delle opere lo richiede.
