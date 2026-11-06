# ArtNotes — Fase 2.5: percorsi, connessioni e ArtNotes Pulse

Data: **6 novembre 2026**. Opera: Pieter Bruegel il Vecchio, *The Harvesters* (Met 435809).
Riferimenti: specifica [FASE_2_5.md](FASE_2_5.md), istruzioni d'uso in [prototipo/README.md](prototipo/README.md).

Questa iterazione copre gli Sprint A e B della specifica e la parte tecnica dello Sprint C, cioè il connettore YouTube con le prove YT-01…08. Mancano il confronto fra ranking automatico e giudizi umani, la valutazione cieca (PUL-02) e i test con utenti (Sprint D): richiedono persone.

**Tutto ciò che è stato aggiunto è una bozza generata da AI e non revisionata**: percorsi, connessioni, classificazioni dei video. Nella vista pubblica non compare nulla.

---

## 1. Che cosa c'è ora

- **Scelta iniziale «Che cosa vuoi scoprire oggi?»**:
  - tre porte d'ingresso, più «Esplora liberamente»;
  - un comando sempre visibile per cambiare percorso;
  - cambiare percorso non tocca immagine, zoom né dettaglio selezionato.
- **Indirizzi condivisibili**: `?percorso=studio&tappa=s4#a13`.
  - La vista è un parametro separato: `vista=pubblico`. Il vecchio `?modo=pubblico` funziona ancora.
  - Nota per la specifica: l'esempio `?modo=curioso#a05` della §2.1 contraddice la regola scritta subito dopo. Ho seguito la regola.
- **Tre percorsi su un'unica base di conoscenza**:
  - le tappe richiamano blocchi, regioni e connessioni esistenti per identificativo, senza copiarli;
  - il testo proprio delle tappe è solo presentazione: domande, consegne, raccordi.

| Percorso | Tappe | Che cosa fa |
|---|---|---|
| **Sono curioso** (≈3 min) | 6 | «Dove cade il tuo sguardo?», poi quattro dettagli da trovare prima di vedere la risposta (brocca nel grano, chi porta da bere, l'uomo che dorme, le lettere nell'angolo). Chiude con 4 video. |
| **Voglio approfondire** (≈15 min) | 6 | Osserva (nota scritta, poi confronto) → Formula → Confronta (interpretazione, ipotesi, lacuna, letture esterne non verificate) → Verifica (mappa delle evidenze con grado di certezza) → Collega → Rielabora (nota e taccuino scaricabile). |
| **Cerco ispirazione** | 5 | La serie dei Mesi, una veduta «allo specchio», le «Estate» di Brueghel il Giovane, le somiglianze calcolate, altri sguardi in video. |

- **Connessioni con altre opere**, ciascuna etichettata per tipo:
  - **documentata**: la serie dei Mesi, cioè le altre 4 tavole secondo Wikidata;
  - **documentata**: le due «Estate» di Pieter Brueghel il Giovane, registrate da Wikidata come derivate;
  - **interpretativa**: la somiglianza compositiva con *Cacciatori nella neve*, ipotesi dell'AI fatta guardando le due immagini;
  - **calcolata**: le notazioni Iconclass in comune. Su 5 opere esaminate, *Fienagione* e *Summer: the wheat harvest* ne condividono 3.
  - Ogni opera collegata ha la miniatura (Wikimedia Commons, pubblico dominio), i dati con il conteggio dei riferimenti e gli avvisi sui dati incerti.
- **ArtNotes Pulse**: 27 video di YouTube.
  - Ogni scheda mostra canale, durata, lingua, anno, relazione con l'opera, affidabilità della fonte e motivo della scelta.
  - Dichiara anche: «classificato da AI su titolo, descrizione e canale; video non guardato».
  - Il punteggio è scomposto nelle sei componenti della §6.3.
  - I link aprono YouTube: nessun video incorporato e nessuna riproduzione automatica.
- **Video collegati alle regioni**: 12 video, su 11 regioni diverse. Nel dettaglio di una regione compaiono sotto il testo scientifico («Approfondisci su YouTube»), in un elemento chiuso.
- **Taccuino**:
  - raccoglie dettagli, connessioni, video e le note del percorso di studio;
  - resta nel browser, si scarica in Markdown e si cancella;
  - niente account e niente dati inviati.

## 2. Criteri di accettazione (§9)

| ID | Esito | Come è stato verificato |
|---|---|---|
| UX-01 | ✅ | Chrome headless a 390 px e a 1440 px: scelta visibile, nessuno scorrimento orizzontale |
| UX-02 | ✅ | Zoom e centro identici prima e dopo due cambi di percorso (3,7981 · 0,2175 · 0,6007); regione e `#a05` conservati |
| UX-03 | 🟡 | Tastiera, focus, nomi accessibili, annunci (`aria-live`) e riduzione del movimento provati in Chrome. **Non provato con screen reader né su dispositivi reali** |
| CUR-01 | ✅ | 5 tappe su regioni (una a scelta fra 3) |
| STU-01 | ✅ | 2 consegne di scrittura, 1 interpretazione attribuita, fonti con link |
| ISP-01 | ✅ | 4 connessioni, 3 tipi diversi |
| PUL-01 | ✅ | 118 candidati raccolti, 34 giudicati, 27 tenuti e 7 respinti con motivo; tutti verificati con `videos.list` |
| PUL-02 | ❌ | Richiede una valutazione cieca da parte di persone |
| PUL-03 | ✅ | Piattaforma, canale, motivo e link esterno visibili su ogni scheda |
| PUL-04 | ✅ | 12 video collegati a regioni esistenti, ciascun collegamento motivato |
| YT-01…08 | ✅ | Prove automatiche e nel browser (§4) |
| EDI-01 | ✅ | La vista pubblica non mostra percorsi, connessioni né video: sono tutti bozze o candidati |
| REG-01 | ✅ | Le 12 prove della Fase 2 e lo script di controllo nel browser della Fase 2 passano senza modifiche |

## 3. Che cosa ha insegnato l'opera

1. **Un'asserzione con riferimento può comunque non reggere allo sguardo.**
   - Wikidata registra le due «Estate» di Brueghel il Giovane come «basate su» *I mietitori*, e per una delle due cita RKDimages.
   - Messe accanto, però, le immagini mostrano un'altra composizione. Ritornano alcuni motivi: il pasto, i covoni, una figura distesa.
   - La scheda riporta il dato, l'osservazione e la lacuna («in che senso "basate"?»). È esattamente il caso per cui servono registri separati.
2. **La ricerca per titolo è rumorosa in modo prevedibile.**
   - La query francese «Bruegel La Moisson» ha prodotto 3 dei 5 falsi positivi: un ristorante, un cimitero militare, un video sulla domesticazione delle piante.
   - La query tematica «Labours of the months» ha trovato «Bruegel», un centro studi di economia.
   - Serve misurare la precisione per query e scartare le query peggiori.
3. **Molti risultati recenti sono contenuti prodotti in serie.**
   - Ci sono Shorts del 2026 con affermazioni sensazionali («un'impronta digitale nascosta», «una pulitura ha rivelato la firma») e animazioni con AI dichiarate.
   - L'etichetta «Affermazioni da verificare» li separa senza dichiararli falsi.
4. **La deduplicazione per identificativo non basta.** Lo stesso canale ha pubblicato due video quasi identici a un giorno di distanza; li ha intercettati solo la cura.
5. **Il punteggio va calibrato con giudizi umani, come previsto dalla specifica.**
   - In «Cerco ispirazione» il primo posto va a un video animato con AI con affermazioni da verificare (0,76), perché la pertinenza pesa più dell'affidabilità.
   - In «Voglio approfondire» il secondo posto va a una lettura simbolica senza fonti (0,87).
   - Sono esattamente i casi che la valutazione PUL-02 deve giudicare.
6. **Il percorso di studio è povero dove manca la letteratura.**
   - L'unica «interpretazione» del corpus è una classificazione di catalogo, non un testo critico.
   - La tappa «Confronta» funziona come esercizio di metodo, ma resta sottile finché non entrano fonti critiche (il commento e la bibliografia del Met, ancora irraggiungibili).

## 4. Prove

`python strumenti/prove.py`: **41 prove, tutte superate** (12 della Fase 2 e 29 nuove). Le nuove coprono:

- **YT-01:**
  - query in 7 varianti (titoli delle voci Wikipedia collegate, più una variante redazionale);
  - query tematiche marcate come tali;
  - il connettore non classifica;
  - un falso positivo può essere solo respinto.
- **YT-02:** lo stesso video trovato da due query resta uno; un doppione nella cura viene rifiutato.
- **YT-03:** relazioni ammesse; ogni classificazione richiede motivazione ed evidenza.
- **YT-04:**
  - un video senza metadati verificati viene rifiutato (niente risultati inventati);
  - l'URL è costruito dall'identificativo;
  - il canale è sempre attribuito.
- **YT-05:**
  - un video rimosso viene escluso;
  - senza file dei metadati la scheda si compone lo stesso e Pulse si svuota;
  - i dati più vecchi di 30 giorni vengono segnalati ed esclusi dalla vista pubblica;
  - gli errori dell'API non contengono la chiave.
- **YT-06:** nessuna chiave, né forma `AIza…`, nei file del sito e nei dati pubblicati.
- **YT-07:** la vista pubblica mostra solo ciò che è pubblicato.
- **YT-08:** un collegamento a una regione inesistente o senza motivazione viene rifiutato.
- **Percorsi e connessioni:**
  - riferimenti inesistenti rifiutati;
  - il tipo di connessione deve essere sostenuto dai blocchi;
  - il calcolo Iconclass dà i risultati attesi;
  - la mappa delle evidenze copre tutti i gradi di certezza.
- **Punteggio:** ogni valore è la somma pesata delle sue componenti; la diversità scende a 0 per un canale già scelto.

Nel browser (Chrome headless, script nella cartella temporanea della sessione):

- tutti e tre i percorsi completi;
- il collegamento da Pulse a una regione con la tastiera (YT-08);
- un guasto simulato dei metadati: Pulse mostra un messaggio, l'opera resta esplorabile (YT-05);
- nessuna chiave nelle risorse caricate (YT-06);
- il taccuino (aggiunta, salvataggio delle note, cancellazione in due passi);
- nessun errore in console.

## 5. File nuovi e modificati

| File | Ruolo |
|---|---|
| `prototipo/strumenti/youtube.py` | Connettore YouTube Data API v3: query, ricerca, verifica. Gira da riga di comando; chiave fuori dal repository |
| `prototipo/strumenti/importa.py` | In più: `commons`, per licenza e miniatura locale |
| `prototipo/strumenti/componi.py` | In più: percorsi, connessioni, Pulse, grado di certezza, punteggio; solo le fonti citate |
| `prototipo/strumenti/prove.py` | 41 prove |
| `prototipo/dati/percorsi/435809.json` | Tre percorsi |
| `prototipo/dati/connessioni/435809.json` | Quattro connessioni |
| `prototipo/dati/esterni/435809.json` | Cura di Pulse: 27 tenuti e 7 respinti, con motivo |
| `prototipo/dati/esterni/youtube/435809.metadati.json` | Metadati minimi dei soli video tenuti |
| `prototipo/dati/fonti/wikidata/*.json`, `…/commons/*.json` | Serie, tavole, derivazioni, bibliografia; licenze delle immagini |
| `prototipo/dati/contenuti/435809.json` | Nuovi blocchi b33 (due chiavi di lettura di catalogo) e b43 (appartenenza alla serie); b50 aggiornato |
| `prototipo/web/*` | Interfaccia della Fase 2.5 |

Restano solo in locale, esclusi da git:
- le risposte grezze di YouTube;
- l'elenco completo dei 118 candidati con le descrizioni.

Nel repository va solo ciò che il sito mostra.

## 6. Limiti e cose da sapere

- **Le classificazioni dei video sono fatte senza guardarli.** Ogni giudizio dice su che cosa si basa. Il passo successivo è la revisione umana di almeno 20 video (PUL-02).
- **Le miniature dei video arrivano dai server di YouTube** (`i.ytimg.com`, senza referrer). È dichiarato nella politica di Pulse. Se si vuole zero traffico verso terzi prima di un clic, le miniature vanno caricate solo su richiesta.
- **Condizioni d'uso dell'API YouTube**: le regole su conservazione, aggiornamento e attribuzione sono state applicate come le descrive la specifica (30 giorni, link alla fonte, nessuna copia dei video). Il testo aggiornato delle Developer Policies non è stato riletto in questa sessione: va fatto prima di rendere pubblico Pulse.
- **Accessibilità**: provata con tastiera ed emulazione nel browser, non con tecnologie assistive reali (UX-03 parziale).
- **Quota usata oggi**: circa 810 unità su 10.000 (8 ricerche da 100 unità più alcune chiamate da 1 unità).

## 7. Seconda iterazione: racconto, fonti più ampie, visita guidata, Gioconda

Questa iterazione nasce da tre osservazioni:
- le fonti erano troppo poche;
- la narrazione era scarsa, frammentata e poco coinvolgente;
- serviva una guida interattiva sull'immagine.

Per verificarla ho aggiunto un'opera molto più famosa: la Gioconda.

**Che cosa è cambiato:**
- **Racconto a scene** per entrambe le opere. Prosa continua, con note numerate alle fonti e un segno per il tipo di frase (◆ interpretazione, ● osservazione, ▲ ipotesi, ○ lacuna).
  - Origine AI e stato di revisione compaiono una sola volta, in testa al racconto e alle sezioni, non più su ogni blocco.
  - Un pulsante ◉ dentro il testo inquadra il dettaglio sull'immagine.
- **Visita guidata a schermo intero.**
  - La camera segue la narrazione frase per frase, e lo zoom si sposta sul dettaglio quando il racconto ci si sofferma.
  - L'etichetta compare insieme alla frase e il resto del quadro viene oscurato.
  - Quando il racconto cita l'autore o un'altra opera esce dal quadro e ne mostra l'immagine (sono 7 uscite nella Gioconda).
  - Comandi da tastiera, voce narrante facoltativa (sintesi vocale del browser) e niente animazioni con "movimento ridotto".
- **Strato bibliografico.** C'è un connettore per OpenAlex, HAL, Wikisource e testi ad accesso aperto, e un registro curato per ogni opera.
  - Ogni fonte dichiara categoria e **livello di lettura** (testo completo, passi pertinenti, abstract, non consultato).
  - **La composizione rifiuta qualunque frase appoggiata a una fonte non consultata.**
- **Più istituzioni.** Il motore non dipende più dal Met: la Gioconda arriva dal Louvre, i cui testi sono sotto Licence Ouverte Etalab, con l'immagine da Commons (scansione C2RMF non ritoccata).
- **Certezza più fine.** Oltre a "dato dell'istituzione" e "da verificare" ora distingue "sostenuto dalla letteratura", "attestato da una fonte d'epoca" e "N fonti indipendenti concordano".

| | I mietitori | La Gioconda |
|---|---|---|
| Fonti nel registro | 24 | 32 |
| di cui letteratura, laboratorio, fonti d'epoca | 4 | 14 |
| Frasi del racconto / note | 42 / 32 | 76 / 67 |
| Interpretazioni da letteratura critica | 0 | 7 |
| Frasi con 2+ fonti indipendenti concordi | 1 | 10 |
| Candidati bibliografici ad accesso aperto pertinenti | 78, di cui più di metà sull'omonimo centro studi «Bruegel» | 103 |

**Fonti nuove effettivamente lette:**
- **Gioconda:**
  - Vasari, *Vite* (Wikisource);
  - il commento del conservatore del Louvre (Delieuvin, 2021);
  - Probst, Biblioteca universitaria di Heidelberg, sulla nota di Vespucci del 1503;
  - lo studio sullo spolvero di Cotte e Simonot (HAL);
  - gli abstract di studi delle università di Firenze, Bologna, Urbino, della Calabria, Milano-Bicocca e Sheffield Hallam, del CNRS e del C2RMF.
- **Mietitori:**
  - van Mander, *Schilder-boeck* (1604);
  - gli abstract di una tesi di dottorato dell'Università del Maryland e di due articoli sulla serie delle stagioni.

**Che cosa si è visto:**
- **La fama porta letteratura e fa il racconto.** Per la Gioconda la scheda del museo contiene un saggio critico firmato. Per i Mietitori il commento del Met resta irraggiungibile (errore 429) e il racconto si appoggia su van Mander, sui dati e sull'osservazione. La differenza si legge nella tabella sopra.
- **Le fonti non sempre concordano, e il racconto lo mostra:**
  - Vasari contro de Beatis sul committente;
  - il Louvre, che non cita lo studio sullo spolvero;
  - l'Università di Bologna, che attribuisce a Leonardo anche la Gioconda di Isleworth;
  - l'Università di Urbino, che riconosce nel paesaggio il Montefeltro, mentre il Louvre non adotta nessuna identificazione.
- **Le tracce materiali si vedono sulla fotografia**, quando la fonte le descrive con precisione: la fenditura di 11 cm, il ricamo e l'orlo del velo. Il ponte invece no: la regione è segnata come stima.
- **Su YouTube la Gioconda produce meno falsi positivi ma più rumore di popolarità.**
  - 72 titoli pertinenti su 76.
  - I video più visti sono "challenge" e video virali da 23–30 milioni di visualizzazioni.
  - Una puntata Rai è ricaricata da un canale di terzi.
  - Ci sono anche i canali del Louvre, di Smarthistory e di ARTE.
  - La cura dei video della Gioconda non è ancora fatta.
- **Limiti:**
  - le parafrasi di van Mander dall'olandese del 1604 sono dell'AI e vanno controllate su un'edizione critica;
  - Smarthistory e la pagina del Met rifiutano l'accesso automatico;
  - i libri a pagamento della bibliografia del Louvre (52 voci) sono elencati ma non letti.

## 8. Da decidere prima della Fase 3

1. **Chi revisiona** percorsi, connessioni e video, e con quale rubrica. Finché nulla passa a «pubblicato», il sito pubblico mostra solo il catalogo.
2. Se i contenuti «da verificare» debbano essere **esclusi** da alcuni percorsi, oppure solo **penalizzati** nel punteggio.
3. Se togliere o riformulare le query più rumorose («La Moisson», «Labours of the months»).
4. Il protocollo della valutazione cieca (PUL-02): posso preparare un foglio con i 27 video anonimizzati e una rubrica di pertinenza.
5. La correzione della §2.1 nella specifica (`percorso=` al posto di `modo=`).
