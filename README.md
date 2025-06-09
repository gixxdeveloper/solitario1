# README - SOLITARIO

Questo file descrive il mio progetto del gioco Solitario (Klondike) scritto in Python.

# Come avviare il progetto

1. Installare Python 3 se non è già installato
2. Installare la libreria colorama:
   
   pip install colorama
   
3. Avviare il gioco con il comando:
   
   python solitario.py
   
   oppure fare doppio click sul file solitario.py salvato e poi cliccare run
   
   altrimenti/metodo consigliato: scrivi nel terminale: python o python3, e poi digiti spazio successivamente trascina 
   il file solitario.py nel terminale e infine clicca invio.

- Istruzioni per l'utente

# Regole del gioco
- L'obiettivo è spostare tutte le carte nelle pile finali, ordinate per seme da Asso a Re.
- Nelle colonne le carte devono essere disposte in ordine decrescente alternando colori rossi e neri.
- Solo i Re possono essere posizionati in colonne vuote.
- Gli Assi vanno nelle pile finali, seguiti da carte dello stesso seme in ordine crescente.

### Modalità di gioco
- Normale: modalità classica senza limiti.
- A tempo: devi completare il gioco entro 10 minuti.
- Difficile: meno carte scoperte all'inizio.

### Personalizzazione
- Puoi scegliere il tema dei colori delle carte (Classico, Blu/Verde, Chiaro).
- Puoi scegliere il retro delle carte e i simboli dei semi.
- Tutte le opzioni sono accessibili dal menu principale.

### Tutorial interattivo
- Alla prima esecuzione viene mostrato un tutorial passo-passo.
- Puoi rivedere il tutorial in qualsiasi momento scegliendo l'opzione 6 dal menu principale.

### AI Consigliatore integrata
- Durante la partita puoi chiedere uno o piu suggerimenti all’AI integrata premendo il tasto 0.
- L’AI analizzerà la situazione attuale e proporrà la mossa migliore disponibile, oppure segnalerà se non ci sono mosse utili.
- Il suggerimento viene mostrato direttamente a schermo e puoi decidere se seguirlo o meno.

### Comandi di gioco
- 0: Chiedi un consiglio all’AI integrata.
- 1: Pesca una carta dal mazzo.
- 2 [colonna_da] [colonna_a]: Sposta una o più carte tra colonne (es: 2 1 5).
  - Puoi spostare solo sequenze scoperte in ordine decrescente e alternando i colori.
  - Solo un Re può essere spostato su una colonna vuota.
- 3 scarti: Sposta la carta dagli scarti alla pila finale.
- 3 colonna [num]: Sposta la carta scoperta in cima a una colonna nella pila finale (es: 3 colonna 4).
- 4 [colonna]: Sposta la carta scoperta dagli scarti alla colonna scelta (es: 4 3).
- 5: Salva partita.
- 6: Carica partita.
- 7: Aiuto (mostra regole e comandi).
- 8: Esci dalla partita.
- 9: Torna al menu principale.

## Menu principale

- 1. Nuova partita (Normale)
- 2. Nuova partita (A tempo)
- 3. Nuova partita (Difficile)
- 4. Carica partita
- 5. Cambia tema e personalizzazione
- 6. Rivedi il tutorial
- 7. Esci

## Descrizione delle classi e metodi

### Classe Carta
Rappresenta una singola carta da gioco.

Attributi:
- seme: Il seme della carta (♠, ♥, ♦, ♣)
- valore: Il valore della carta (A, 2-10, J, Q, K)
- scoperta: Se la carta è visibile al giocatore
- tema, retro, simboli: Attributi per la personalizzazione grafica

Metodi:
- __repr__(): Mostra la carta con il colore e simbolo giusto in base al tema scelto
- valore_numerico(): Converte valori come A, J, Q, K in numeri
- to_dict(): Converte la carta in dizionario per salvare
- from_dict(): Crea una carta da un dizionario

### Classe Solitario
Gestisce tutta la logica del gioco.

Metodi principali:
- _prepara_gioco(): Dispone le carte iniziali
- mostra(): Visualizza il gioco
- pesca(): Pesca una carta dal mazzo
- sposta_colonna(): Sposta carte tra colonne
- sposta_a_finale(): Sposta una carta nella pila finale
- controlla_vittoria(): Verifica se il gioco è vinto
- salva_partita(): Salva su file JSON
- carica_partita(): Carica da file JSON
- mostra_aiuto(): Mostra regole e comandi
- verifica_obiettivi(): Verifica obiettivi raggiunti
- suggerisci_mossa(): Analizza la situazione e suggerisce la mossa migliore (AI consigliatore)

### Funzioni esterne
- trova_salvataggi(): Cerca i file di salvataggio
- mostra_tutorial(): Mostra il tutorial interattivo
- tutorial_gia_visto(), segna_tutorial_visto(): Gestiscono la visualizzazione del tutorial
- main(): Funzione principale che gestisce tutto il gioco

---
Creato da Gianni Nesti