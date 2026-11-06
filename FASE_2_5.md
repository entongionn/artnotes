ArtNotes — Fase 2.5: Discovery & Learning Experience
Data: 6 novembre 2026
Stato: proposta progettuale da validare
Opera pilota: Pieter Bruegel il Vecchio, The Harvesters (I mietitori), Metropolitan Museum of Art, object ID 435809
Dipendenze: Fase 1, Fase 2, prototipo/README.md
Fase successiva: Fase 3 — modello dati, redazione e pubblicazione
1. Visione
ArtNotes non è soltanto un catalogo digitale né un'alternativa alle audioguide museali: è un ambiente in cui un'opera può essere scoperta, studiata e usata come punto di partenza creativo. Il nucleo è un patrimonio di conoscenza documentato e revisionabile; le esperienze si adattano all'intenzione del visitatore.

Promessa: non soltanto dire che cosa mostra un'opera, ma aiutare a capire come osservarla, perché viene interpretata in un certo modo e dove conduce la curiosità.

Principio editoriale: la divulgazione non deve degradare il rigore; il rigore non deve rendere l'esperienza inaccessibile.
1.1 Posizionamento
ArtNotes deve distinguersi per l'integrazione di:
1. esplorazione visiva ancorata a regioni dell'immagine;
2. spiegazioni con evidenze, attribuzioni, lacune e livelli di certezza;
3. percorsi narrativi adattati all'intento;
4. discovery di contenuti esterni con provenienza e ranking spiegabili;
5. apprendimento attivo, confronto fra interpretazioni e collegamenti tra opere.
Non rivendicare unicità assoluta: zoom, annotazioni, audioguide, quiz e raccomandazioni esistono già. L'ipotesi distintiva è la loro integrazione editoriale e didattica, da verificare con utenti e analisi competitiva.
2. Punto di ingresso: «Che cosa vuoi scoprire oggi?»
All'apertura di un'opera, presentare una scelta semplice, modificabile in qualsiasi momento:
Modalità	Microcopy	Obiettivo
Sono curioso	«Fammi vedere qualcosa che non avrei notato.»	Suscitare interesse e facilitare la scoperta
Voglio approfondire	«Aiutami a capire come si costruisce un'interpretazione.»	Studiare, verificare e argomentare
Cerco ispirazione	«Mostrami idee, connessioni e reinterpretazioni.»	Alimentare ricerca e creatività


2.1 Requisiti UX
- Nessuna registrazione obbligatoria per esplorare.
- La scelta cambia l'ordine e il modo di presentare i contenuti, non i fatti sottostanti.
- Cambio di modalità sempre disponibile, senza perdere opera, zoom o dettaglio selezionato.
- Un URL condiviso può includere opera, modalità e annotazione (?modo=curioso#a05), senza confliggere con ?modo=pubblico esistente: separare vista=pubblico|redazione da percorso=curioso|studio|ispirazione con compatibilità retroattiva.
- Funzionalità essenziali accessibili con tastiera e screen reader; nessun significato affidato soltanto ai colori.
- Percorso iniziale breve e facoltativo; nessuna interfaccia infantilizzante.
- Nessuna personalizzazione opaca o profilazione invasiva: preferenze locali/esplicite e cancellabili.
3. Modalità «Sono curioso»
3.1 Esperienza
Percorsi brevi (indicativamente 2–5 minuti) con dettagli sorprendenti, domande di osservazione, narrazione visiva e contenuti esterni pertinenti. Ogni tappa inquadra una regione e offre una via verso l'approfondimento documentato.

Esempio su I mietitori: «Dove cade per primo il tuo sguardo?» → selezione della zona → spiegazione della composizione → domanda successiva → eventuale video pertinente con link alla piattaforma originale.
3.2 ArtNotes Pulse — contenuti social contestualizzati
Una sezione di discovery che seleziona e reindirizza a contenuti pubblici di terzi, senza fingere che siano contenuti propri o scientificamente verificati.

Categorie iniziali:
- L'opera raccontata: divulgazione e spiegazioni.
- Dettagli da scoprire: osservazioni puntuali sull'immagine.
- Arte e cultura pop: rimandi contemporanei e reinterpretazioni.
- Conversazioni sull'opera: discussioni e letture diverse.
Ogni suggerimento mostra piattaforma, autore, titolo, lingua, data se disponibile, ragione della pertinenza, eventuale dettaglio collegato, etichetta di affidabilità e collegamento alla fonte originale. Popolarità non equivale ad accuratezza.
3.3 Confine tra fatto e intrattenimento
I contenuti social sono risorse esterne, non prove accademiche per definizione. Un video che afferma qualcosa di controverso non aggiorna automaticamente la scheda scientifica. Se la pertinenza è solo tematica, dichiararlo («collegamento al tema della vita rurale, non analisi diretta dell'opera»).
4. Modalità «Voglio approfondire»
4.1 Esperienza
Percorso di osservazione attiva e studio critico, utilizzando le sezioni, le fonti e i registri narrativi della Fase 2.

Sequenza suggerita:
1. Osserva: l'utente descrive un dettaglio senza ricevere subito la spiegazione.
2. Formula: propone una domanda o ipotesi interpretativa.
3. Confronta: legge interpretazioni documentate, eventuali alternative e limiti delle fonti.
4. Verifica: esamina citazioni, provenienza delle affermazioni e stato di revisione.
5. Collega: confronta altre opere o contesti con relazioni motivate.
6. Rielabora: produce una breve argomentazione o una scheda personale.
Non trattare come errore una lettura diversa ma ragionevolmente argomentata. Distinguere sempre osservazione, inferenza, interpretazione e fatto documentato.
4.2 Funzioni accademiche candidate
- Mappa delle evidenze: affermazione → fonte → dettaglio → grado di certezza.
- Interpretazioni concorrenti: più letture, ciascuna con bibliografia e stato editoriale.
- Confronto visivo: due opere affiancate; distinguere analogia formale e influenza storicamente documentata.
- Laboratorio attributivo: autore, datazione, provenienza, restauro, lacune e ipotesi.
- Tutor socratico opzionale: domande graduate, senza inventare riferimenti o attribuire consenso inesistente.
L'AI può assistere nella formulazione e nel recupero di contenuti già verificati; non deve promuovere automaticamente una propria risposta a conoscenza pubblicata.
5. Modalità «Cerco ispirazione»
5.1 Esperienza
L'opera è un nodo di un atlante creativo: colori, composizione, atmosfera, soggetti, gesti, tecniche e rimandi contemporanei.

Percorsi possibili:
- «Altre opere con una composizione simile»;
- «Come è stato rappresentato questo tema in epoche diverse?»;
- «Dalla pittura alla fotografia e al cinema»;
- «Reinterpretazioni di artisti e creator»;
- «Crea un taccuino di riferimenti», con link e attribuzioni.
5.2 Regole
Distinguere le connessioni documentate (influenza o citazione provata), interpretative (somiglianze argomentate) e algoritmiche (somiglianza visiva calcolata). Nessun legame storico va dedotto automaticamente da una semplice somiglianza estetica.

Per le opere e i contenuti di terzi, rispettare licenze, attribuzione e condizioni di riutilizzo. Preferire link ed embed ufficiali ove consentiti.
6. Motore di discovery e raccomandazione
6.1 Pipeline
Opera canonica (Met ID / Wikidata ID)
    ↓
Varianti del titolo, autore, lingue, temi, regioni
    ↓
Ricerca tramite API ufficiali / fonti autorizzate
    ↓
Raccolta di metadati minimi e deduplicazione
    ↓
Filtro di pertinenza: opera esatta / dettaglio / tema / analogia
    ↓
Controlli qualità, diritti, disponibilità, sicurezza
    ↓
Ranking specifico per modalità + diversità di fonti
    ↓
Revisione editoriale dei suggerimenti prioritari
    ↓
ArtNotes Pulse → collegamento alla piattaforma originale
6.2 Strategie di recupero
Usare identificativi e varianti multilingue, evitando omonimie. Una corrispondenza per parole chiave è soltanto un candidato. La classificazione semantica può suggerire relazioni ma deve produrre una motivazione verificabile.

MVP: iniziare da YouTube, previa verifica aggiornata di API, quote, termini e modalità consentite di presentazione. TikTok, Instagram e Reddit sono espansioni condizionate alla disponibilità di accessi ufficiali e diritti appropriati. Non progettare il servizio sulla dipendenza da scraping indiscriminato.
6.3 Ranking spiegabile
Punteggio sperimentale, non formula definitiva:

score = 0,35 pertinenza + 0,25 qualità + 0,15 corrispondenza_intento + 0,10 diversità + 0,10 freschezza + 0,05 segnali_di_interesse

Pesi da calibrare con giudizi umani. Le metriche di engagement non sostituiscono pertinenza e accuratezza. Applicare prima filtri vincolanti su disponibilità, policy, contenuti ingannevoli e idoneità: un punteggio alto non deve aggirarli.

Spiegare il motivo di ogni suggerimento: «Parla direttamente dell'opera», «Approfondisce il dettaglio a05», «Collegamento tematico: raccolto», «Somiglianza visiva non verificata storicamente».
6.4 Collegamento alle regioni
La relazione fra un contenuto esterno e un'annotazione è esplicita e revisionabile: external_content_id → annotation_id, con tipo di relazione, confidenza, motivazione, fonte del collegamento e stato di revisione. Un contenuto può essere collegato a più regioni; nessuna regione è obbligatoria.
6.5 Aggiornamento e degrado controllato
- Cache di metadati consentiti, con scadenze e rispetto delle condizioni della piattaforma.
- Verifica periodica di video rimossi, privati o non più incorporabili.
- Se un'API non è disponibile, mostrare contenuti già validi quando consentito o un messaggio trasparente; non inventare risultati.
- Non esporre chiavi API nel client.
- Minimizzare dati personali e telemetria; niente raccolta di profili dei creator oltre quanto necessario e consentito.
6.6 Integrazione YouTube — specifica MVP
Scopo: proporre video e Shorts realmente pertinenti all'opera e ai suoi dettagli, con collegamento alla pagina YouTube originale. Non ospitare copie dei video e non confondere un creator con una fonte scientifica.

Flusso di recupero (lato server):
1. Generare query da titolo canonico, traduzioni, varianti, autore, data e identificativi dell'opera; aggiungere query tematiche separate e chiaramente marcate (es. vita contadina nel Cinquecento).
2. Interrogare YouTube Data API v3, con search.list per candidati di tipo video e videos.list per metadati, stato e disponibilità. Le quote e i campi effettivamente utilizzabili vanno verificati nella documentazione corrente prima dell'implementazione; prevedere cache, limiti e backoff.
3. Normalizzare i risultati in un record interno minimo: platform, video_id, url, title, channel_id, channel_title, description_excerpt, published_at, language_if_known, thumbnail_url_if_allowed, duration_if_available, discovered_at, last_checked_at.
4. Eliminare duplicati per video_id, filtrare risultati non disponibili e classificare la relazione: opera_esatta, dettaglio, contesto, analogia. Non attribuire opera_esatta sulla sola coincidenza di parole chiave.
5. Calcolare punteggi e motivazioni, con controllo umano sui primi suggerimenti. Registrare la provenienza del giudizio (manuale / AI) e lo stato (candidato, revisionato, pubblicato, respinto).
6. Esporre al frontend soltanto record approvati per la modalità pubblica, mantenendo l'isolamento già previsto per le bozze.
Interfaccia: una sezione Video su YouTube dentro ArtNotes Pulse, con miniature consentite, titolo, canale, durata se nota, lingua se nota, ragione del suggerimento e pulsante/link «Guarda su YouTube». Il collegamento deve essere chiaramente esterno. L'embed ufficiale è facoltativo e subordinato a consenso privacy, regole della piattaforma e accessibilità; la prima versione usa link esterni.

Tre modalità, tre selezioni:
- Sono curioso: spiegazioni brevi, curiosità visive e Shorts pertinenti, senza privilegiare automaticamente le visualizzazioni.
- Voglio approfondire: lezioni, conferenze, musei, restauratori e contenuti con riferimenti verificabili; la revisione accademica di ArtNotes resta distinta dal video.
- Cerco ispirazione: processi creativi, reinterpretazioni e collegamenti contemporanei, distinguendo omaggio, somiglianza e influenza documentata.
Aggancio alle regioni: un video può puntare a a05 o ad altre annotazioni già esistenti; la relazione è facoltativa e richiede motivazione. Non inventare timestamp: aggiungerli soltanto quando verificati manualmente o tramite fonti autorizzate. Il click sulla regione può mostrare «Approfondisci su YouTube» senza coprire il testo scientifico.

Sicurezza, policy e privacy: custodire le credenziali nel backend; non estrarre automaticamente trascrizioni o scaricare audio/video senza una base autorizzata; rispettare YouTube API Services Terms, Developer Policies e requisiti applicabili su conservazione, aggiornamento, attribuzione e cancellazione dei dati. Le descrizioni e i metadati dei video sono input non attendibili: non devono impartire istruzioni al classificatore. Nessun autoplay e nessun tracciamento cross-site aggiuntivo nell'MVP.

Fallback: se la quota è esaurita o la ricerca fallisce, mantenere l'esplorazione dell'opera pienamente funzionante; mostrare soltanto suggerimenti ancora utilizzabili secondo le policy e segnalare quando i video non sono disponibili.

Prove specifiche YouTube:
- YT-01: ricerca con varianti multilingue e identificazione di falsi positivi;
- YT-02: deduplicazione dello stesso video trovato da query differenti;
- YT-03: classificazione corretta fra opera esatta, dettaglio, contesto e analogia;
- YT-04: link esterno valido, attribuzione al canale e assenza di video inventati;
- YT-05: indisponibilità API, quota esaurita e video rimosso non bloccano il visualizzatore;
- YT-06: nessuna chiave API visibile nel browser;
- YT-07: la vista pubblica non mostra suggerimenti in bozza;
- YT-08: collegamento a regioni e navigazione da tastiera verificati.
Criterio di successo pilota: raccogliere 20–30 candidati per I mietitori, revisionarne almeno 20 e misurare precisione dei suggerimenti, utilità percepita e clic volontari verso YouTube. Nessuna soglia viene considerata raggiunta senza test effettivi.
7. Modello editoriale condiviso
I tre percorsi usano un'unica base di conoscenza: non tre versioni contraddittorie della stessa opera.

Ogni unità informativa conserva: identificativo, opera, eventuale regione, contenuto, registro narrativo, fonti, origine AI/umana, revisore, stato editoriale, versione e data. Le esperienze aggiungono un livello di presentazione (ordine, durata, domande, stile narrativo), non modificano silenziosamente il contenuto validato.

Per i collegamenti esterni conservare anche piattaforma, URL canonico, identificativo esterno, autore mostrato, lingua, tipo di relazione, motivazione, data di verifica e stato di disponibilità. Evitare il salvataggio di media non autorizzati.

Modalità pubblica: nessun contenuto in bozza, non revisionato o scaduto deve apparire come contenuto pubblicato. I suggerimenti esterni devono avere una policy editoriale distinta e visibile.
8. Integrazione con la Fase 2
Da conservare senza regressioni: OpenSeadragon 4.1.1, limite zoom 1,5×, 14 regioni e 4 livelli, collegamenti bidirezionali, deep link #a05, registri narrativi, copertura, scheda fonti/diritti, controlli di revisione, modalità pubblica e 12 prove automatiche esistenti.

Estensioni incrementali:
1. Schermata di selezione percorso e comando persistente per cambiarlo.
2. Configurazioni narrative per modalità, referenziate ai blocchi e alle annotazioni esistenti.
3. Un percorso guidato per ciascuna modalità su 435809.
4. ArtNotes Pulse con dataset curato manualmente prima dell'automazione.
5. Link tra suggerimenti esterni e regioni.
6. Strumentazione anonima/minimizzata per test d'uso, previa informativa adeguata.
Evitare ora: migrazione prematura a PostgreSQL, raccomandatore complesso, profili permanenti, feed infinito, app native e supporto simultaneo a tutte le piattaforme.
9. Prototipo MVP e criteri di accettazione
ID	Requisito	Criterio verificabile
UX-01	Scelta delle tre modalità	Visibili e selezionabili da mobile e desktop
UX-02	Cambio percorso	Opera, regione e zoom conservati
UX-03	Navigazione accessibile	Tastiera, focus, nomi accessibili, riduzione movimento
CUR-01	Percorso curioso	Almeno 3 tappe collegate a regioni
STU-01	Percorso studio	Almeno 1 domanda, 1 interpretazione e 1 fonte consultabile
ISP-01	Percorso ispirazione	Almeno 3 connessioni etichettate per tipo
PUL-01	Discovery esterna	20–30 candidati raccolti o curati; nessun risultato inventato
PUL-02	Pertinenza	Valutazione manuale cieca di almeno 20 suggerimenti
PUL-03	Trasparenza	Piattaforma, autore, motivo e link esterno visibili
PUL-04	Region linking	Almeno 3 contenuti collegati a regioni esistenti
YT-01–08	Integrazione YouTube	Tutte le prove specifiche della §6.6 superate
EDI-01	Integrità scientifica	Nessuna bozza esposta come affermazione revisionata
REG-01	Regressioni	Tutte le prove della Fase 2 continuano a passare


I numeri sono obiettivi di prototipazione, non risultati già raggiunti.
10. Validazione con utenti
10.1 Campione esplorativo
Coinvolgere indicativamente 15–20 persone, distribuite tra curiosi non specialisti, studenti e appassionati avanzati. È uno studio qualitativo: non consente inferenze statistiche sulla popolazione globale.
10.2 Protocollo
1. Registrare familiarità con l'arte e motivazione della visita.
2. Far scegliere liberamente una modalità, senza spiegazioni aggiuntive.
3. Osservare completamento, incomprensioni e cambi di percorso.
4. Verificare se distinguono fatto documentato, ipotesi e contenuto esterno.
5. Chiedere di descrivere un dettaglio e motivare una propria interpretazione.
6. Testare se comprendono perché un contenuto social è stato consigliato.
7. Raccogliere desiderio di continuare e utilità percepita; quando possibile, fare un breve richiamo dopo alcuni giorni.
10.3 Metriche
- Tasso di scelta e completamento dei percorsi.
- Tempo alla prima interazione significativa (non massimizzare il tempo trascorso).
- Capacità di identificare e spiegare un dettaglio.
- Capacità di distinguere fonti, ipotesi e opinioni.
- Precisione@5 dei suggerimenti, valutata da revisori umani con rubriche condivise.
- Percentuale di link non disponibili e di classificazioni errate.
- Utilità percepita, interesse a tornare e feedback qualitativo.
Definire soglie decisionali prima dei test; non modificare retroattivamente i criteri per dichiarare successo.
11. Ruoli e responsabilità
Ruolo	Responsabilità
Responsabile tecnico/prodotto	UX, architettura, pipeline, test, privacy, integrazione
Storico dell'arte	Revisione scientifica, bibliografia, criteri interpretativi, qualità didattica
Revisore editoriale	Tono, chiarezza, etichette, collegamenti esterni, coerenza
Utenti pilota	Comprensibilità, utilità, problemi di interazione e accessibilità


Una revisione umana non è automaticamente una certificazione scientifica: registrare competenze, ambito e decisione del revisore.
12. Rischi e mitigazioni
Rischio	Mitigazione
App percepita come aggregatore social	Collegare ogni suggerimento a un'esperienza sull'opera e a un motivo esplicito
Errori o allucinazioni AI	Fonti, registri, revisione e separazione tra suggerimenti e conoscenza pubblicata
Dipendenza da piattaforme esterne	Provider modulari, cache conforme, fallback, diversificazione
Costi editoriali non scalabili	Percorsi riusabili, strumenti di revisione, priorità a opere campione
Personalizzazione invasiva	Intento esplicito, preferenze locali, raccolta minima
Bassa accessibilità	Test con dispositivi e tecnologie assistive reali
Collegamenti culturali arbitrari	Tipizzazione: documentato, interpretativo, algoritmico
Diritti e licenze	Link/embed consentiti, attribuzioni e audit delle fonti


13. Piano di esecuzione
Sprint A — Esperienza
- Definire copy, wireframe e cambio modalità.
- Preparare tre percorsi su I mietitori riutilizzando le regioni.
- Testare la navigazione senza contenuti social.
Sprint B — Discovery controllata
- Curare manualmente 20–30 contenuti candidati da fonti consentite.
- Etichettare relazione, pertinenza, lingua, affidabilità e regione.
- Prototipare ArtNotes Pulse con reindirizzamento esterno.
Sprint C — Automazione sperimentale
- Implementare prima il connettore YouTube Data API v3 lato server e i test YT-01–08.
- Verificare condizioni e quote dell'API scelta.
- Implementare recupero, deduplica e classificazione dei candidati.
- Confrontare ranking automatico e giudizi dei revisori.
Sprint D — Ricerca utenti e decisione
- Eseguire test qualitativi e verifiche di accessibilità reali.
- Correggere i problemi critici.
- Decidere quali entità e workflow consolidare nella Fase 3.
14. Decisioni da prendere prima della Fase 3
- Quale modalità produce il maggior valore, per quale pubblico e con quale evidenza?
- ArtNotes Pulse deve essere moderato interamente o parzialmente automatizzato?
- Quali relazioni fra opere e contenuti richiedono revisione scientifica?
- Quali dati servono davvero al pannello redazionale?
- Qual è il modello sostenibile di produzione e aggiornamento dei contenuti?
- Quale primo segmento scegliere: studenti, appassionati o istituzioni?
15. Definizione di completamento della Fase 2.5
La fase è conclusa solo quando le tre modalità sono percorribili sulla stessa opera, la discovery esterna è trasparente e valutata, i contenuti scientifici non perdono tracciabilità, le regressioni della Fase 2 sono assenti e sono disponibili risultati documentati di test con utenti.

Output per la Fase 3: inventario delle entità osservate (percorsi, tappe, domande, evidenze, relazioni, contenuti esterni, revisioni), decisioni editoriali, requisiti prioritari e problemi irrisolti. Lo schema PostgreSQL dovrà derivare da questi dati, non anticiparli.
Sintesi: ArtNotes unisce tre porte d'ingresso — curiosità, approfondimento e ispirazione — a una sola base di conoscenza verificabile. La Fase 2.5 serve a dimostrare che questa esperienza funziona, prima di industrializzarla.