ArtNotes — Atlante interattivo di storia dell’arte
Specifica di prodotto e guida alla progettazione
Stato: proposta progettuale, non descrizione di funzionalità già implementate.
Obiettivo: costruire un grande archivio di opere d’arte che permetta di scoprirle, osservarle, comprenderle e studiarle attraverso immagini interattive e contenuti documentati.
Nome: ArtNotes è un nome di lavoro, modificabile.
1. Visione
Realizzare una galleria digitale a tutto tondo, con una solida chiave accademica e un’esperienza capace di appassionare anche chi parte senza conoscenze specialistiche.

Ogni opera deve diventare un ambiente di esplorazione: l’utente può osservare l’immagine, selezionare dettagli, leggere spiegazioni, approfondire il contesto, confrontare altre opere e fare domande sui materiali disponibili.

L’ambizione è un catalogo molto ampio, arricchito progressivamente. L’estensione del catalogo e la profondità dei contenuti sono dimensioni distinte: non tutte le opere avranno fin dall’inizio lo stesso livello di approfondimento.

La qualità si misura nella capacità di aiutare una persona a osservare e comprendere un’opera, oltre che nell’accuratezza dei dati.
2. Rapporto con la precedente idea ArtNotes AI
La galleria interattiva diventa il centro del prodotto. Importazione degli appunti e generazione di dispense Word restano sviluppi successivi, collegati allo stesso catalogo.

Non rendere necessario caricare un documento per esplorare le opere. Non subordinare la progettazione della galleria al motore di esportazione Word.

Se esiste già un repository, analizzarlo prima di intervenire. Conservare moduli utili, dati, migrazioni e funzionalità esistenti. Non riscrivere il software senza motivazione.
3. Pubblico e obiettivi
Pubblico	Esigenza	Risposta del prodotto
Appassionato	Scoprire opere e capire cosa osservare	Percorsi introduttivi e lettura visiva guidata
Studente	Collegare immagini, concetti e contesto	Schede documentate, confronti e raccolte di studio
Docente o divulgatore	Preparare materiali e percorsi	Selezioni commentate e contenuti citabili
Redattore o storico dell’arte	Curare e verificare contenuti	Strumenti editoriali, fonti e revisioni


La prima versione deve privilegiare studenti e appassionati adulti. Le funzioni per istituzioni e classi possono essere aggiunte dopo la validazione del nucleo principale.
4. Principi inderogabili
1. Non inventare dati, attribuzioni, bibliografie, licenze o risultati di verifica.
2. Distinguere dati documentati, interpretazioni critiche, osservazioni visive e contenuti generati dall’AI.
3. Mantenere la provenienza delle informazioni e rendere consultabili le fonti.
4. Conservare incertezze e controversie: un’attribuzione discussa non diventa certa attraverso la normalizzazione.
5. Non presentare una risposta AI come revisione scientifica.
6. Rendere utile il catalogo anche senza il tutor AI.
7. Non richiedere uno stile accademico complesso per offrire rigore accademico.
8. Separare dati del catalogo, contenuti editoriali e annotazioni personali.
9. Progettare per la crescita senza introdurre infrastrutture non giustificate.
5. Esperienza principale
Il flusso di riferimento è:
1. L’utente cerca un’opera oppure entra da un percorso tematico.
2. Apre una scheda con immagine, informazioni essenziali e stato dei contenuti.
3. Esplora i dettagli e attiva livelli di lettura.
4. Legge analisi con riferimenti alle fonti.
5. Confronta l’opera con altre selezionate e comprende il motivo del collegamento.
6. Se desidera, interroga il tutor sui materiali disponibili.
7. Salva opere e annotazioni in una raccolta di studio.
La consultazione di base non deve obbligare a creare un account. Valutare l’account per salvataggi personali e sincronizzazione.
6. I tre strati del sistema
6.1 Catalogo
Descrive l’identità dell’opera: titoli, autori, attribuzioni, date, tecnica, materiali, dimensioni, istituzione, identificativi e immagini.
6.2 Conoscenza storico-artistica
Contiene analisi, bibliografia, contesto, letture iconografiche, interpretazioni e relazioni fra opere. Ogni contributo conserva autore, fonti, stato editoriale e versioni.
6.3 Annotazioni visive
Collega regioni di una specifica immagine a spiegazioni, fonti e confronti. Consente di esplorare l’opera attraverso i suoi dettagli.

Questi strati devono essere distinti ma collegati. Una modifica all’immagine non deve alterare silenziosamente il significato delle annotazioni.
7. Scheda dell’opera
Prevedere sezioni progressive:
- In breve: dati essenziali e introduzione comprensibile.
- Osserva: dettagli selezionabili e domande per guidare lo sguardo.
- Analisi: composizione, luce, colore, spazio, tecnica e materiali, dove pertinenti.
- Iconografia: soggetti, attributi, simboli e interpretazioni documentate.
- Contesto: committenza, destinazione, funzione e ambiente storico-culturale, quando noti.
- Confronti: opere collegate con spiegazione del rapporto.
- Fonti: schede istituzionali, riferimenti bibliografici e crediti.
Non tutte le sezioni sono applicabili a ogni oggetto. Il modello deve poter estendersi oltre la pittura, senza fingere che una fotografia di una scultura rappresenti tutte le sue viste.
8. Interazione con le immagini
8.1 Visualizzatore
Supportare zoom, spostamento, adattamento alla finestra e apertura dei dettagli. Mostrare soltanto il dettaglio consentito dalla risoluzione disponibile, senza simulare informazioni mancanti attraverso immagini generate.
8.2 Punti e regioni interattive
Le annotazioni possono essere punti, rettangoli o poligoni. Devono contenere:
- Immagine di riferimento e sua versione.
- Coordinate e sistema di riferimento esplicito.
- Titolo del dettaglio.
- Categoria dell’annotazione.
- Spiegazione e riferimenti documentali.
- Autore, revisore, stato e date di modifica.
- Eventuali opere o approfondimenti collegati.
Usare coordinate normalizzate rispetto all’immagine di riferimento e conservare le informazioni necessarie per ricostruirle. Zoom e ridimensionamento non devono spostare le regioni sull’opera.

Un cambio di ritaglio, orientamento o fotografia richiede una nuova verifica delle annotazioni.
8.3 Livelli di lettura
Consentire l’attivazione separata di livelli quali composizione, iconografia, tecnica e osservazione guidata. Evitare di sovrapporre tutte le annotazioni contemporaneamente.

Non generare automaticamente schemi compositivi presentandoli come analisi accertate. Le interpretazioni grafiche pubblicate devono essere curate e motivate.
8.4 Collegamento fra testo e immagine
Selezionando un approfondimento, il visualizzatore evidenzia la regione corrispondente. Selezionando la regione, si apre il contenuto pertinente. L’utente deve poter consultare il testo senza animazioni obbligatorie.
8.5 Domande su una regione
In una fase successiva, permettere all’utente di selezionare una zona e porre una domanda. Il sistema trasmette al tutor l’identità dell’opera, la regione, le annotazioni pertinenti e le fonti disponibili.

Quando viene impiegata analisi visiva automatica, distinguere l’osservazione proposta dal modello dall’identificazione documentata. In mancanza di riscontri, dichiarare il limite.
9. Rigorosità accademica ed editoriale
9.1 Provenienza
Le informazioni controverse o centrali per un’analisi devono avere riferimenti sufficientemente precisi: autore, titolo, anno, pagina o sezione, oppure collegamento istituzionale e data di consultazione.

Un collegamento generico alla home page di un museo non supporta automaticamente un’interpretazione.
9.2 Stati editoriali
Distinguere almeno: bozza, in revisione, pubblicato e da aggiornare. Un contenuto generato dall’AI deve conservare tale origine anche dopo la revisione.

La revisione deve indicare chi l’ha svolta, quando e su quale versione. Non attribuire qualifiche professionali non verificate.
9.3 Disaccordi
Consentire più interpretazioni attribuite ai rispettivi autori. Conservare separatamente datazioni e attribuzioni provenienti da fonti diverse, documentando la scelta di quella mostrata in evidenza.
9.4 Livelli di copertura
Mostrare separatamente:
- Presenza dei dati catalografici.
- Presenza di approfondimenti documentati.
- Presenza di annotazioni interattive.
- Stato e ambito della revisione umana.
Non trattare queste dimensioni come un unico punteggio di verità. Una scheda può essere annotata ma ancora in revisione.
10. Ricerca e scoperta
Prevedere ricerca per titolo, artista, varianti dei nomi, soggetto e identificativo. Aggiungere filtri per cronologia, tecnica, istituzione, località e disponibilità dei contenuti soltanto quando i dati lo permettono.

Conservare la formulazione originale di date e attribuzioni. Un filtro cronologico deve gestire intervalli e approssimazioni.

Le ricerche ordinarie devono interrogare il catalogo applicativo. Le fonti esterne servono all’importazione, all’aggiornamento e al recupero mirato dei dati.

La prima versione deve gestire paginazione e caricamento differito delle immagini.
11. Confronti, percorsi e suggerimenti
11.1 Confronti
Affiancare due opere con immagini esplorabili, dati essenziali e commento guidato. Ogni confronto deve esplicitare il criterio: soggetto, soluzione formale, tecnica, funzione o rapporto storico documentato.

Una somiglianza visiva non dimostra un’influenza storica.
11.2 Percorsi
Ogni percorso comprende titolo, destinatario, prerequisiti, obiettivo, durata indicativa, sequenza delle opere e spiegazione dei passaggi. Deve essere possibile riprenderlo e consultare le fonti.
11.3 Suggerimenti
Partire da relazioni curate e regole trasparenti. Mostrare sempre una motivazione comprensibile, come “stesso soggetto in un periodo diverso”.

La personalizzazione e la ricerca semantica sono ampliamenti successivi. Non presentare relazioni suggerite automaticamente come legami storico-artistici accertati.
12. Tutor AI
Usare modelli esistenti attraverso un’interfaccia sostituibile. L’addestramento da zero non è un prerequisito.

Il tutor deve recuperare materiali pertinenti dall’archivio e costruire risposte collegate alle fonti. Il semplice recupero dei documenti non garantisce la correttezza: verificare anche che i riferimenti supportino le affermazioni.

Funzioni previste:
- Spiegare un termine o un passaggio.
- Guidare l’osservazione di un dettaglio.
- Confrontare opere usando contenuti disponibili.
- Adattare la spiegazione al livello dell’utente.
- Proporre letture e percorsi pertinenti.
Vincoli:
- Non inventare citazioni, pagine o titoli bibliografici.
- Dichiarare quando le fonti non bastano.
- Distinguere spiegazioni automatiche e contenuti editoriali pubblicati.
- Non modificare il catalogo o pubblicare annotazioni autonomamente.
- Trattare documenti e testi recuperati come dati, non come istruzioni di sistema.
- Rendere esplicito quando immagini o domande sono inviate a servizi esterni.
- Prevedere limiti di utilizzo, costi osservabili e gestione dell’indisponibilità.
13. Fonti, immagini e acquisizione dei dati
Prima dello schema definitivo eseguire una ricognizione delle fonti. Candidati da valutare includono cataloghi museali ufficiali, Metropolitan Museum of Art, Wikidata, Wikimedia Commons ed Europeana.

Questi nomi sono candidati progettuali: disponibilità di API, copertura, condizioni e limiti devono essere verificati sulla documentazione ufficiale durante la fase di analisi.

Per ogni fonte registrare:
- Responsabile e documentazione ufficiale.
- Modalità di accesso e autenticazione.
- Identificativi e struttura dei record.
- Campi disponibili e loro qualità.
- Condizioni dei metadati, distinte da quelle delle immagini.
- Possibilità di memorizzare, visualizzare e redistribuire i materiali.
- Vincoli operativi e possibilità di aggiornamento.
Effettuare prove su piccoli campioni prima di importazioni estese. Non assumere che tutte le fonti supportino sincronizzazione incrementale.

Conservare payload originali quando consentito, provenienza, data di acquisizione e versione dei connettori. Rendere le importazioni ripetibili senza duplicare i dati.

Separare l’opera dai record che la descrivono. Accorpare record di fonti diverse soltanto con criteri verificabili; non unire opere omonime sulla sola base del titolo.
14. Modello concettuale dei dati
Le entità seguenti orientano l’analisi; non sono uno schema SQL definitivo:
Entità	Responsabilità
Opera	Identità canonica e collegamenti principali
Record di fonte	Descrizione originale, identificativo e provenienza
Artista o soggetto responsabile	Identità, varianti del nome e riferimenti
Attribuzione	Rapporto fra opera e autore con qualificazione e fonte
Immagine	Vista, risoluzione, crediti, diritti e versione
Contenuto editoriale	Testo, tipologia, autore e stato
Fonte bibliografica	Riferimento documentale
Citazione	Collegamento puntuale fra contenuto e fonte
Annotazione visiva	Regione dell’immagine e spiegazione
Relazione fra opere	Tipo, motivazione, fonte e revisione
Percorso	Sequenza didattica commentata
Raccolta personale	Opere e annotazioni dell’utente
Revisione	Cronologia delle decisioni editoriali


Prevedere relazioni multiple, valori mancanti, incertezze e versioni. Separare lo stato del contenuto dalla sua provenienza.
15. Architettura proposta
Per favorire consultazione da computer e telefono, assumere come base una web app responsive. Questa è una scelta progettuale da confermare prima dell’implementazione, non una decisione già approvata dall’utente.

Separare:
1. Interfaccia di consultazione e visualizzatore.
2. Servizi applicativi e autorizzazioni.
3. Catalogo e contenuti editoriali.
4. Gestione delle immagini e delle miniature.
5. Importazioni ed elaborazioni in background.
6. Recupero documentale e tutor AI.
7. Pannello di redazione.
Python e PostgreSQL sono basi candidate coerenti con la precedente specifica. Selezionare framework e visualizzatore dopo prove mirate; non introdurre un motore vettoriale, un database a grafo o microservizi soltanto per l’ambizione di crescita.

Valutare standard interoperabili per immagini e annotazioni, inclusi IIIF e Web Annotation, verificando compatibilità e necessità reali.

Definire API, migrazioni, backup e confini dei moduli. Il visualizzatore non deve dipendere direttamente dalla struttura interna del database.
16. Redazione e gestione dei contenuti
Prevedere un pannello per:
- Correggere dati mantenendo la provenienza originale.
- Gestire immagini, crediti e disponibilità.
- Scrivere analisi e associare citazioni.
- Disegnare regioni interattive.
- Creare confronti e percorsi.
- Revisionare e pubblicare versioni.
- Ricevere segnalazioni e ritirare contenuti problematici.
Distinguere ruoli di amministratore, redattore, revisore e lettore. Le raccolte personali restano separate dal catalogo pubblico.

Una bozza AI non deve apparire pubblicamente per errore.
17. Accessibilità e usabilità
Le spiegazioni devono essere consultabili anche tramite un elenco testuale delle annotazioni, senza dover individuare piccoli punti sull’immagine.

Prevedere navigazione da tastiera, gestione del focus, contrasto leggibile, descrizioni delle immagini e controlli utilizzabili su telefono. Non affidare il significato soltanto al colore.

Distinguere descrizione visiva accessibile e interpretazione storico-artistica. Evitare animazioni obbligatorie e sovrapposizioni che nascondano l’opera.
18. Prestazioni, diritti e affidabilità
Non scaricare preventivamente tutte le immagini ad alta risoluzione. Usare miniature e caricamento progressivo secondo le condizioni delle fonti.

Conservare separatamente diritti sui dati, sull’opera rappresentata e sulla fotografia. La pubblicazione online di un’immagine non implica automaticamente facoltà di riutilizzo.

Gestire collegamenti interrotti, rimozioni delle immagini e correzioni delle schede. Conservare l’identità dell’opera anche quando una risorsa esterna non è disponibile.

Proteggere credenziali e contenuti personali. Validare importazioni e file, limitare operazioni costose e registrare gli errori senza esporre dati sensibili.

Per il lancio pubblico, completare una verifica delle condizioni applicabili ai materiali effettivamente usati.
19. Prima versione dimostrativa
Obiettivo: dimostrare che esplorare un’opera attraverso dettagli e fonti migliora la comprensione.

Ambito proposto:
- Dieci opere scelte con coerenza didattica.
- Ricerca essenziale e catalogo espandibile.
- Schede con fonti e stato editoriale.
- Immagini esplorabili con annotazioni curate pertinenti.
- Due percorsi brevi.
- Confronto guidato fra coppie selezionate.
- Tutor limitato al corpus disponibile, dopo la validazione del recupero delle fonti.
- Pannello minimo per gestire testi e annotazioni.
Le quantità sono obiettivi di lavoro, non dichiarazioni di materiale già disponibile.

Il catalogo di massa, il riconoscimento visivo libero, le audioguide, le funzioni d’esame e la generazione Word completa restano successivi.
20. Piano di sviluppo
Fase 1 — Verifica delle fondamenta
Analizzare l’eventuale repository. Definire pubblico iniziale, esperienza principale e criteri di scelta delle opere. Verificare fonti e immagini con campioni limitati. Consegnare una matrice delle fonti e un rapporto sulle decisioni tecniche aperte.
Fase 2 — Prototipo dell’esperienza visiva
Realizzare una sola opera completa: immagine, zoom, annotazioni, testo collegato e fonti. Verificarla su computer, telefono e con navigazione da tastiera prima di estenderla.
Fase 3 — Catalogo e strumenti editoriali
Definire lo schema sulla base dei dati osservati. Implementare migrazioni, importazione, ricerca, versioni e flusso di pubblicazione. Ampliare il prototipo alle opere selezionate.
Fase 4 — Percorsi e confronti
Pubblicare percorsi curati e confronti motivati. Verificare con utenti reali se le spiegazioni aiutano a leggere dettagli precedentemente ignorati.
Fase 5 — Tutor documentato
Integrare recupero delle fonti e risposte con riferimenti. Provare domande risolvibili, ambigue, fuori corpus e con premesse errate. Misurare qualità e costi prima di ampliare l’accesso.
Fase 6 — Crescita controllata
Aumentare opere e fonti. Automatizzare attività ripetitive, preservando revisioni e provenienza. Valutare personalizzazione, audio, appunti e dispense sulla base dell’utilizzo reale.
21. Verifica e criteri di accettazione
Area	Verifica richiesta
Identità	Record omonimi non vengono uniti senza riscontri
Importazione	Ripetere un’importazione non crea duplicati
Immagini	Crediti e condizioni restano collegati alla risorsa corretta
Annotazioni	Regioni coerenti dopo zoom e ridimensionamento
Versioni	Cambiare immagine segnala la necessità di verificare le annotazioni
Redazione	Solo le versioni pubblicate sono visibili ai lettori
Fonti	Le citazioni aprono il riferimento pertinente
Tutor	Nessuna risposta verificata viene dichiarata tale senza controllo
Lacune	Materiali insufficienti producono una dichiarazione esplicita del limite
Accessibilità	I contenuti essenziali sono raggiungibili senza usare il mouse
Studio	Un utente sa spiegare dettagli e collegamenti dopo il percorso


Preparare un insieme stabile di opere, annotazioni e domande per la valutazione. Documentare errori, falsi collegamenti, riferimenti non pertinenti e prove non eseguite.

Prima di fissare soglie quantitative, raccogliere una misura iniziale. Non inventare percentuali di accuratezza.
22. Istruzioni per l’eventuale agente di sviluppo
Questo documento è una specifica da applicare quando viene esplicitamente richiesto di iniziare lo sviluppo.
- Iniziare dalla Fase 1; non implementare tutto in un’unica modifica.
- Verificare documentazione ufficiale e condizioni aggiornate delle dipendenze e delle fonti.
- Non creare lo schema definitivo prima dell’analisi dei campioni.
- Preferire la soluzione più semplice che soddisfa i requisiti verificati.
- Mantenere separate raccolta dei dati, interpretazione AI e pubblicazione editoriale.
- Non dichiarare funzionalità completate senza implementazione e verifica.
- Al termine di ogni fase indicare risultati, file modificati, prove, limiti e passo successivo.
23. Definizione finale del prodotto
ArtNotes è un atlante digitale interattivo che collega opere, dettagli visivi e conoscenza storico-artistica documentata. La sua ambizione è rendere un archivio molto ampio uno strumento per sviluppare curiosità, capacità di osservazione e competenze di studio.

Principio guida: ogni spiegazione deve aiutare a vedere meglio l’opera, e ogni approfondimento deve rendere riconoscibile la propria base documentale.