# ArtNotes — Fase 1: rapporto sulle fondamenta

Data: **6 novembre 2026**.
Allegato: [FASE1_matrice_fonti.md](FASE1_matrice_fonti.md), con dettaglio per fonte e marcatori [P] provato, [D] documentato, [?] da verificare.

---

## 1. Esito in breve

1. **Le fonti museali con licenza CC0 (Met, AIC) sono una base solida** per i dati catalografici. Non contengono però analisi né bibliografia: lo strato «conoscenza» (specifica, §6.2) andrà costruito in redazione.
2. **Fra le fonti esistono discordanze su dati centrali.** Sullo stesso dipinto il Met scrive «Attributed to Lucia Anguissola», Wikidata «anonimo» senza fonti. L'attribuzione va quindi conservata fonte per fonte e la scelta di quella mostrata va motivata (§9.3).
3. **La qualità delle immagini varia moltissimo**, da 30000 × 21851 px a 680 × 694 px, fino a un'opera disponibile solo in bianco e nero. Il visualizzatore e i testi devono dichiarare questi limiti.
4. **Per le opere italiane poco note la fonte più ricca è ICCD/ArCo**: attribuzione preferita con criterio, bibliografia con figura, notizie storiche, iscrizioni. Ma **licenza dei dati e condizioni delle immagini non sono chiarite**. È il principale nodo aperto.
5. **Un'interfaccia citata nella specifica non esiste più nella forma prevista.** La ricerca v1 del Met è stata ritirata il 1° ottobre 2026. Conferma che le dipendenze esterne vanno verificate a ogni fase.

---

## 2. Metodo

- Documentazione ufficiale letta dove raggiungibile: Met, Wikidata, Commons. Le pagine di AIC, Europeana e catalogo ICCD hanno rifiutato il client automatico (403/401) e sono segnate come **non lette**.
- Prove dirette su un campione di **9 opere** e di alcune ricerche, distribuite fra opere famose e opere poco documentate (§3).
- Nessuna importazione estesa, nessun dato salvato nel progetto, nessuno schema creato (specifica, §22).
- Le dimensioni delle immagini sono state misurate sui file scaricati. Il bianco e nero dell'immagine di bottega di Bellini è stato verificato sui pixel: tutti i canali sono identici.

---

## 3. Campione esaminato

| Opera | Fonte principale | Fascia di documentazione | Note emerse |
|---|---|---|---|
| Pieter Bruegel il Vecchio, *The Harvesters*, 1565 | Met 435809 · Wikidata Q776175 | Alta | 86 asserzioni Wikidata, 24 voci Wikipedia, 11 immagini Met. Su Commons esiste una fotografia diversa da 30000 × 21851 px |
| Johannes Vermeer, *Young Woman with a Water Pitcher*, ca. 1662 | Met 437881 · Q386453 | Alta | Data testuale «ca. 1662» con intervallo 1657–1667 |
| Georges Seurat, *A Sunday on La Grande Jatte — 1884* | AIC 27992 | Alta | Data «1884–86, border added 1888–89». Due licenze nello stesso record |
| Lorenzo Lotto, pannello di predella con *Santa Lucia in ginocchio sulla tomba di Sant'Agata*, post 1525–ante 1532, Jesi | ArCo 1100139305-2 | Media (in rete), alta (nella scheda) | Attribuzione preferita con criterio, bibliografia con figura, notizie storiche |
| Attribuito a Lucia Anguissola, *Portrait of a Man*, ca. 1560 | Met 436749 · Q19914251 | Scarsa | **Attribuzione in conflitto**, immagine 680 × 694 px, 0 voci Wikipedia |
| Bottega di Giovanni Bellini, *The Circumcision*, 1511 | Met 435643 · Q19905123 | Scarsa | **Unica immagine in bianco e nero** |
| Pittore italiano (?), *Portrait of a Man in Profile* | Met 436472 · Q19913061 | Scarsa | Data testuale vuota ma intervallo 1520–1530. Autore con «?» |
| Seguace di Rembrandt, *Portrait of a Man («The Auctioneer»)*, «probably ca. 1658–62» | Met 437406 | Scarsa | Data con doppia qualificazione («probably», «ca.») |
| Attribuito a Jean-Augustin Franquelin, *The Mariner's Wife* | Met 438619 | Scarsa | Pittore «Paris 1798–1839», intervallo 1820–1839, ma `isPublicDomain = false`, nessuna immagine e nessuna nota sui diritti. Il campo sembra riflettere la disponibilità dell'immagine più che lo stato giuridico dell'opera: da verificare, non da interpretare |

Le opere poco note del campione sono quasi tutte del Met. Per le opere italiane poco note conviene cercare in ArCo appena la licenza sarà chiarita.

---

## 4. Risultati per tema

### 4.1 Identità e attribuzioni

- Il Met conserva la qualificazione dell'attribuzione in un campo separato (`artistPrefix`). Valori osservati: «Attributed to», «Workshop of», «Follower of», «Style of», «?».
- Wikidata la rappresenta con qualificatori (P1774 «bottega di», P3831 ruolo), ma in almeno un caso la perde: per Q19914251 l'autore è anonimo, senza riferimenti.
- ArCo distingue esplicitamente un'**attribuzione preferita** («maggiormente accreditata o convincente») e ne indica il criterio («bibliografia»).
- **Conseguenza:** il modello deve avere un'entità *Attribuzione* con fonte, qualificazione originale e criterio, distinta dall'opera. L'attribuzione mostrata in evidenza è una scelta editoriale documentata, non il risultato di una fusione automatica.

### 4.2 Date

- Tutte le fonti provate conservano la formulazione originale («ca. 1662», «probably ca. 1658–62», «post 1525-ante 1532», «1884–86, border added 1888–89»).
- Met e AIC aggiungono un intervallo numerico.
- In un record Met l'intervallo esiste senza testo: va trattato come stima catalografica e non presentato come data documentata.
- **Conseguenza:** conservare la data come *testo originale* più *intervallo per la ricerca*, più la provenienza di entrambi (§10).

### 4.3 Immagini

- La stessa opera ha fotografie diverse su fonti diverse. Per *The Harvesters*: file Met da 3,0 MB, file Commons «Google Art Project» da 223 MB. Le annotazioni devono essere legate alla **specifica fotografia** e alla sua versione (§8.2).
- Il dettaglio realmente esplorabile dipende dalla fonte. Per il ritratto attribuito ad Anguissola, sia il Met sia Commons offrono solo 680 × 694 px. Lo zoom deve fermarsi lì, senza ingrandimenti generati (§8.1).
- Un'immagine in bianco e nero rende impossibile un'analisi del colore. La scheda deve dirlo invece di omettere la sezione senza spiegazione.
- Né il Met né Commons risultano offrire IIIF Image API. Lo offre AIC, che però blocca i client automatici: la prova da browser va fatta in Fase 2.
- **Conseguenza:** l'entità *Immagine* registra fonte, file esatto, dimensioni, colore o bianco e nero, crediti, diritti e versione. Per le immagini riutilizzabili servirà generare tile in proprio.

### 4.4 Diritti

- Bisogna tenere distinti tre livelli:
  - diritti sui **metadati** (CC0 per Met, AIC e Wikidata; CC BY per la sola `description` di AIC);
  - diritti sulla **fotografia** (per file su Commons, per record su Europeana);
  - diritti sull'**opera rappresentata**.
- Il campo `dc:rights` di ArCo indica la proprietà del bene, non la licenza: un esempio concreto di campo che una normalizzazione ingenua interpreterebbe male.
- Per i beni culturali italiani le riproduzioni sono soggette anche alla disciplina del Codice dei beni culturali. Il punto va verificato su fonti normative prima di pubblicare immagini provenienti da cataloghi italiani.

### 4.5 Ricerca

- Europeana mostra il rischio dei nomi ambigui: «Lotto» restituisce un gioco da tavolo. Anche con il filtro per autore, i risultati sono soprattutto stampe e derivazioni.
- **Conseguenza:** la ricerca interna deve lavorare su identità dell'artista e varianti del nome già risolte nel catalogo, non su testo libero inviato alle fonti esterne (§10).

---

## 5. Stile narrativo per opere famose e opere poco documentate

Hai chiesto di includere sia opere molto documentate sia opere con pochi dati, per definire uno stile narrativo «alla LLM» che resti credibile e affidabile mostrando il contesto. Il campione conferma che il contrasto è reale ed è utile per la demo. Contiene però un rischio da affrontare in modo esplicito.

### 5.1 Il rischio

Un modello linguistico scrive con la stessa fluidità sia quando ha venti fonti sia quando ne ha una. Sulle opere poco note la prosa scorrevole tende a colmare i vuoti con elementi plausibili: committenti, intenzioni dell'artista, identità del ritrattato. **La credibilità percepita aumenta proprio mentre l'affidabilità diminuisce.** Il caso Anguissola lo mostra: un testo «naturale» direbbe «il ritratto di Lucia Anguissola», cancellando sia il «attributed to» del Met sia il dissenso di Wikidata.

### 5.2 La regola proposta

La credibilità deve nascere da una **base documentale visibile**, non dal tono. In pratica:

1. **Ogni frase appartiene a un registro dichiarato**, mostrato all'utente con un'etichetta testuale e non solo con un colore (§17):
   - *Documentato*: dato o affermazione con citazione puntuale;
   - *Interpretazione*: tesi attribuita a un autore o a un'istituzione;
   - *Osservazione*: ciò che si vede in **questa** fotografia, verificabile dall'utente guardando;
   - *Ipotesi*: confronto o lettura proposta, formulata al condizionale e motivata;
   - *Lacuna*: ciò che non è noto o non è nelle fonti disponibili.
2. **Le fonti discordanti si mostrano, non si risolvono nel testo.**
3. **Con poche fonti cambia il peso della narrazione, non la sua sicurezza.** Per le opere poco note il racconto si sposta sull'*osservazione guidata*, che è verificabile, e sulla dichiarazione dei limiti. Non si allunga il contesto storico generico.
4. **Vietato** introdurre committenti, provenienze, identità dei soggetti, intenzioni dell'artista o datazioni non presenti nelle fonti. Vietati anche aggettivi di certezza come «indubbiamente» o «chiaramente» riferiti ad attribuzioni.
5. **Il testo generato porta sempre l'etichetta di origine AI**, anche dopo la revisione umana (§9.2). Il revisore viene indicato con nome, data e versione.
6. Accanto al testo, un riquadro **«Su cosa si basa questa scheda»** mostra separatamente i quattro indicatori di copertura (§9.4): dati catalografici, approfondimenti documentati, annotazioni, revisione.

### 5.3 Esempio costruito solo sui dati raccolti

Opera: *Portrait of a Man*, Met 436749. Le osservazioni visive sono state prodotte da un modello sulla fotografia del Met (680 × 694 px) e **non sono state revisionate**.

> **Documentato** · Met, scheda 436749, consultata il 6/11/2026
> Il Metropolitan Museum presenta questo piccolo ritratto come *attribuito* a Lucia Anguissola (Cremona, 1536/38 – ca. 1565). «Attribuito» indica una proposta, non una certezza.
>
> **Fonte discordante** · Wikidata Q19914251
> Wikidata registra invece l'autore come anonimo, senza citare fonti a sostegno.
>
> **Documentato** · Met
> È un tondo a olio su rame di 12,4 cm di diametro, datato «ca. 1560».
>
> **Osservazione** · su questa fotografia · generata da AI, non revisionata
> Un uomo con barba rossiccia, a mezzo busto, veste di scuro con una gorgiera bianca increspata. Lo sfondo è verde e uniforme; a destra della figura si vede un'ombra proiettata. In basso la mano destra stringe un oggetto bianco, forse un fazzoletto: alla risoluzione disponibile non è identificabile con certezza. Lungo il bordo superiore si notano piccole perdite di colore.
>
> **Lacuna**
> Le fonti consultate non indicano chi sia l'uomo ritratto, né la committenza, la provenienza o una bibliografia. La fotografia disponibile non permette di esaminare la stesura da vicino.

Il testo non contiene nulla che non stia nelle fonti o nell'immagine. Resta comunque leggibile e incuriosisce, perché trasforma l'incertezza in materia di osservazione.

### 5.4 Cosa va verificato

Lo stile va provato con lettori reali nelle Fasi 2 e 4. Domande da porre:

- le etichette aiutano o appesantiscono la lettura?
- il lettore ricorda correttamente che l'attribuzione è incerta?
- un registro più discorsivo, con le etichette raccolte a margine, mantiene la stessa chiarezza?

Non fisso soglie numeriche prima di una misura iniziale (§21).

---

## 6. Criteri di selezione delle dieci opere

Proposta:

1. **Tre fasce di documentazione**: circa 4 opere ben documentate, 3 intermedie e 3 scarse. Per le scarse, almeno una con attribuzione discussa e una con immagine limitata.
2. **Coerenza didattica**: un tema che permetta confronti motivati.
3. **Immagini riutilizzabili e ad alta risoluzione** per almeno le opere ben documentate, perché il visualizzatore va provato su dettagli reali.
4. **Varietà di fonti**, così da mettere alla prova l'importazione su strutture diverse.
5. **Almeno un oggetto non pittorico** in una fase successiva, per verificare che il modello non presupponga un dipinto (§7). Le fotografie di sculture escono dalla regola PD-Art di Commons.

**Tema candidato, da confermare:** «Il Cinquecento fra Italia e Fiandre: ritratto, racconto, bottega». Cinque opere del campione rientrano già:

- Bruegel, *The Harvesters*;
- Lotto, pannello di predella di Jesi;
- attribuito ad Anguissola, *Portrait of a Man*;
- bottega di Bellini, *The Circumcision*;
- pittore italiano, *Portrait of a Man in Profile*.

Coprono già le tre fasce, compresi i casi difficili: attribuzione in conflitto, immagine in bianco e nero, bassa risoluzione. Le altre cinque vanno individuate. Vermeer e Seurat restano utili come prove tecniche ma sono fuori tema.

---

## 7. Decisioni tecniche aperte

| Decisione | Stato | Orientamento proposto, da provare |
|---|---|---|
| Web app responsive | Da confermare da parte tua (§15) | Coerente con l'uso da computer e telefono |
| Linguaggio e database | Candidati Python e PostgreSQL | Adatti: PostgreSQL permette di conservare i payload originali in JSON accanto ai dati normalizzati |
| Framework | Aperto | Valutare per primo un framework con pannello di amministrazione e gestione dei ruoli già pronti, perché redazione, revisione e pubblicazione sono requisiti centrali. Confronto pratico in Fase 2 |
| Visualizzatore | Aperto | Provare un visualizzatore a tile compatibile con IIIF e uno strato di annotazione in formato Web Annotation, su una sola opera. Versioni e licenze da verificare al momento della scelta |
| Tile delle immagini | Aperto | Met e Commons non offrono IIIF: servono derivate generate in proprio, solo per immagini riutilizzabili |
| Formato delle annotazioni | Aperto | Coordinate normalizzate legate alla versione dell'immagine. Web Annotation come formato di scambio, se la prova lo conferma |
| ICCD/ArCo | **Bloccante per le opere italiane** | Richiedere o trovare la dichiarazione ufficiale di licenza dei dati e delle immagini |
| Tutor AI | Rinviato alla Fase 5 | Nessuna decisione ora |

Non servono, a oggi, motori vettoriali, database a grafo o microservizi. ArCo è un grafo, ma basta interrogarlo in fase di importazione.

---

## 8. Rischi principali

1. **Licenze italiane non chiarite**: potrebbero escludere proprio le opere poco note più interessanti.
2. **Narrazione AI troppo sicura** sulle opere scarse (§5.1).
3. **Fusioni sbagliate fra record** se si unisce per titolo: «Portrait of a Man» compare più volte nel solo campione.
4. **Dipendenze esterne che cambiano**, come il ritiro della ricerca v1 del Met.
5. **Immagini inadatte allo zoom** per alcune opere scelte.

---

## 9. Prove non eseguite e limiti

- Documentazione di AIC, Europeana e catalogo ICCD non letta (403/401).
- IIIF di AIC non provato da browser.
- Europeana provata solo con la chiave dimostrativa.
- Nessuna verifica delle condizioni normative italiane sulle riproduzioni.
- Termini e condizioni di Met e AIC non letti per intero.
- Non provati: SPARQL di Wikidata, dump, aggiornamenti incrementali reali.
- Rijksmuseum, NGA, Cleveland, Getty e Iconclass non esaminati.
- Il campione è piccolo (9 opere) e sbilanciato sul Met: i risultati indicano problemi reali ma non ne misurano la frequenza.

---

## 10. Passo successivo

**Decisioni prese il 6/11/2026:**

1. Web app responsive **per ora**. In futuro l'obiettivo è un'app vera e propria. Ne segue che dati e servizi vanno tenuti indipendenti dall'interfaccia web, perché un'app nativa possa riusarli.
2. Tema approvato: «Il Cinquecento fra Italia e Fiandre», con tre fasce di documentazione.
3. Registri narrativi con etichette approvati (§5.2).

Domande originarie:

1. Confermare la **web app responsive**.
2. Confermare o cambiare il **tema** (§6) e approvare le tre fasce di documentazione.
3. Approvare la **regola dei registri narrativi** (§5.2), o indicare quanto deve essere discorsiva.

Proposta per la Fase 2:

- **Prototipo completo su *The Harvesters***: immagine ad alta risoluzione, dati ricchi, pubblico dominio. Serve a provare zoom, annotazioni, collegamento testo-immagine, tastiera e telefono.
- **Una scheda testuale di prova sull'opera attribuita ad Anguissola**, per valutare lo stile narrativo nel caso scarso.
- In parallelo, cercare la dichiarazione ufficiale di licenza ICCD.
