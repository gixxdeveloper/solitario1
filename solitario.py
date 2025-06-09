import random
import os
import sys
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

SEMI = ['♠', '♥', '♦', '♣']
VALORI = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
COLORI = {'♠': 'N', '♣': 'N', '♥': 'R', '♦': 'R'}

class Carta:
    def __init__(self, seme, valore):
        self.seme = seme
        self.valore = valore
        self.scoperta = False

    def __repr__(self):
        if not self.scoperta:
            return "##"
        simbolo = f"{self.valore}{self.seme}"
        # Personalizzazione colori
        tema = getattr(self, 'tema', 'classico')
        if hasattr(self, 'tema') and self.tema == "blu_verde":
            if self.seme in ['♥', '♦']:
                return Fore.BLUE + simbolo + Style.RESET_ALL
            else:
                return Fore.GREEN + simbolo + Style.RESET_ALL
        elif hasattr(self, 'tema') and self.tema == "chiaro":
            return Fore.BLACK + simbolo + Style.RESET_ALL
        else:  # classico
            if self.seme in ['♥', '♦']:
                return Fore.RED + simbolo + Style.RESET_ALL
            return simbolo

    def valore_numerico(self):
        """Restituisce il valore numerico della carta per i confronti"""
        if self.valore == 'A':
            return 1
        elif self.valore == 'J':
            return 11
        elif self.valore == 'Q':
            return 12
        elif self.valore == 'K':
            return 13
        else:
            return int(self.valore)
        
    def to_dict(self):
        """Converte la carta in un dizionario per il salvataggio"""
        return {
            'seme': self.seme,
            'valore': self.valore,
            'scoperta': self.scoperta
        }
        
    @classmethod
    def from_dict(cls, data):
        """Crea una carta da un dizionario"""
        carta = cls(data['seme'], data['valore'])
        carta.scoperta = data['scoperta']
        return carta

class Solitario:
    def __init__(self, modalita="normale", tema="classico", tempo_limite=None):
        self.mazzo = [Carta(seme, valore) for seme in SEMI for valore in VALORI]
        random.shuffle(self.mazzo)
        self.colonne = [[] for _ in range(7)]
        self.pile_finali = {seme: [] for seme in SEMI}
        self.riserva = []
        self.scarti = []
        self.punteggio = 0
        self.tempo_inizio = time.time()
        self.mosse = 0
        self.modalita = modalita
        self.tema = tema
        if modalita == "tempo":
            self.tempo_limite = tempo_limite if tempo_limite is not None else 600
        else:
            self.tempo_limite = None
        self._prepara_gioco()

    def _prepara_gioco(self):
        for i in range(7):
            for j in range(i + 1):
                carta = self.mazzo.pop()
                if j == i:
                    carta.scoperta = True
                elif self.modalita == "difficile":
                    carta.scoperta = False  # Meno carte scoperte in modalità difficile
                self.colonne[i].append(carta)
        self.riserva = self.mazzo[:]
        self.mazzo = []

    def mostra(self):
        os.system("cls" if os.name == "nt" else "clear")
        tempo_trascorso = int(time.time() - self.tempo_inizio)
        if self.modalita == "tempo":
            tempo_rimanente = max(0, self.tempo_limite - tempo_trascorso)
            minuti = tempo_rimanente // 60
            secondi = tempo_rimanente % 60
            tempo_str = f"Tempo: {minuti:02d}:{secondi:02d}"
        else:
            minuti = tempo_trascorso // 60
            secondi = tempo_trascorso % 60
            tempo_str = f"Tempo: {minuti:02d}:{secondi:02d}"

        print(f"╔═══════════════════════════════════════════════════════════════╗")
        print(f"║ SOLITARIO ({self.modalita.upper()})    Punteggio: {self.punteggio:<5} "
              f"{tempo_str} Mosse: {self.mosse:<3} ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝")
        
        if self.modalita == "tempo" and tempo_rimanente == 0:
            print("\n⏰ TEMPO SCADUTO! Hai perso la partita.")
            input("\nPremi INVIO per terminare...")
            exit()

        print("\n📌 PILE FINALI:")
        for seme in SEMI:
            pila = self.pile_finali[seme]
            cima = pila[-1] if pila else '__'
            if isinstance(cima, Carta) and cima.seme in ['♥', '♦']:
                cima = Fore.RED + str(cima) + Style.RESET_ALL
            print(f"{seme}: {cima}", end='   ')
        
        print("\n\n📌 RISERVA:")
        scarto = self.scarti[-1] if self.scarti else '__'
        print(f"Scarti: {scarto}")
        print(f"Carte nel mazzo: {len(self.riserva)}")
        
        self.mostra_colonne()

    def mostra_colonne(self):
        print("\n📌 COLONNE:")
        for i, col in enumerate(self.colonne):
            print(f"{Fore.YELLOW}Colonna {i+1}:{Style.RESET_ALL}", end=' ')
            for carta in col:
                carta.tema = self.tema  # <--- AGGIUNTA QUI
                print(f"{carta} ", end='')
            print()

    def pesca(self):
        """Pesca una carta dal mazzo"""
        if not self.riserva:
            if not self.scarti:
                print("Nessuna carta da pescare o rigirare.")
                return False
            # Mescola gli scarti prima di rigirarli (versione facilitata)
            random.shuffle(self.scarti)
            self.riserva = self.scarti[::-1]
            for c in self.riserva:
                c.scoperta = False
            self.scarti.clear()
            print("Mazzo rigirato e mescolato.")
            self.mosse += 1
            return True
        if self.riserva:
            carta = self.riserva.pop()
            carta.scoperta = True
            self.scarti.append(carta)
            self.mosse += 1
            return True
        return False

    def sposta_colonna(self, da_idx, a_idx, da_scarti=False):
        """Sposta carte tra colonne o dagli scarti a una colonna"""
        # Validazione indici
        if not (0 <= a_idx < 7):
            print("Indice colonna di destinazione non valido.")
            return False
            
        a = self.colonne[a_idx]
        
        # Caso speciale: spostamento dagli scarti
        if da_scarti:
            if not self.scarti:
                print("Nessuna carta da spostare negli scarti.")
                return False
                
            carta = self.scarti[-1]
            
            # Verifica condizioni di spostamento
            if not a:  # Colonna vuota
                if carta.valore == 'K':
                    self.colonne[a_idx].append(carta)
                    self.scarti.pop()
                    self.mosse += 1
                    self.punteggio += 5
                    return True
                else:
                    print("Solo un Re può essere spostato in una colonna vuota.")
                    return False
            else:  # Colonna con carte
                cima = a[-1]
                if COLORI[cima.seme] != COLORI[carta.seme] and carta.valore_numerico() == cima.valore_numerico() - 1:
                    self.colonne[a_idx].append(carta)
                    self.scarti.pop()
                    self.mosse += 1
                    self.punteggio += 5
                    return True
                else:
                    print("Ordine o colore non valido per lo spostamento.")
                    return False
        
        # Spostamento tra colonne
        if not (0 <= da_idx < 7):
            print("Indice colonna di origine non valido.")
            return False
            
        da = self.colonne[da_idx]
        
        if not da:
            print("Colonna di origine vuota.")
            return False
            
        # Trova il primo indice di carta scoperta
        for i in range(len(da)):
            if da[i].scoperta:
                gruppo = da[i:]
                
                # Verifica se si può spostare nella colonna di destinazione
                if not a:  # Colonna vuota
                    if gruppo[0].valore == 'K':
                        self.colonne[a_idx] += gruppo
                        self.colonne[da_idx] = da[:i]
                        self._scopri_ultima(da_idx)
                        self.mosse += 1
                        self.punteggio += 3
                        return True
                    else:
                        print("Solo un Re può essere spostato in una colonna vuota.")
                        return False
                else:  # Colonna con carte
                    cima = a[-1]
                    if COLORI[cima.seme] != COLORI[gruppo[0].seme] and gruppo[0].valore_numerico() == cima.valore_numerico() - 1:
                        self.colonne[a_idx] += gruppo
                        self.colonne[da_idx] = da[:i]
                        self._scopri_ultima(da_idx)
                        self.mosse += 1
                        self.punteggio += 3
                        return True
                    else:
                        print("Ordine o colore non valido per lo spostamento.")
                        return False
                        
        print("Nessuna carta scoperta da spostare.")
        return False

    def _scopri_ultima(self, idx):
        """Scopre l'ultima carta di una colonna"""
        if self.colonne[idx]:
            self.colonne[idx][-1].scoperta = True

    def sposta_a_finale(self, origine, idx=None):
        """Sposta una carta nella pila finale"""
        if origine == "scarti":
            if not self.scarti:
                print("Nessuna carta negli scarti.")
                return False
            carta = self.scarti[-1]
        elif origine == "colonna":
            if not (0 <= idx < 7) or not self.colonne[idx]:
                print("Colonna vuota o indice non valido.")
                return False
            carta = self.colonne[idx][-1]
            if not carta.scoperta:
                print("La carta non è scoperta.")
                return False
        else:
            print("Origine non valida.")
            return False

        pila = self.pile_finali[carta.seme]
        if (not pila and carta.valore == 'A') or (pila and carta.valore_numerico() == pila[-1].valore_numerico() + 1):
            pila.append(carta)
            if origine == "scarti":
                self.scarti.pop()
            else:
                self.colonne[idx].pop()
                self._scopri_ultima(idx)
            self.mosse += 1
            self.punteggio += 10
            return True
        else:
            print(f"Carta non posizionabile nella pila finale. Serviva: {'A' if not pila else VALORI[pila[-1].valore_numerico()]}.")
            return False

    def controlla_vittoria(self):
        """Verifica se il gioco è stato vinto"""
        return all(len(p) == 13 for p in self.pile_finali.values())
        
    def salva_partita(self, nome_file=None):
        """Salva lo stato attuale della partita"""
        if nome_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_file = f"solitario_salvataggio_{timestamp}.json"
        
        dati = {
            'riserva': [carta.to_dict() for carta in self.riserva],
            'scarti': [carta.to_dict() for carta in self.scarti],
            'colonne': [[carta.to_dict() for carta in colonna] for colonna in self.colonne],
            'pile_finali': {seme: [carta.to_dict() for carta in pila] for seme, pila in self.pile_finali.items()},
            'punteggio': self.punteggio,
            'mosse': self.mosse,
            'tempo_gioco': int(time.time() - self.tempo_inizio),
            'modalita': self.modalita,
            'tema': self.tema,
            'tempo_limite': self.tempo_limite   # <--- AGGIUNTA QUI
        }
        
        try:
            with open(nome_file, 'w', encoding='utf-8') as f:
                json.dump(dati, f, ensure_ascii=False, indent=2)
            print(f"Partita salvata in: {nome_file}")
            return True
        except Exception as e:
            print(f"Errore durante il salvataggio: {e}")
            return False
    
    @classmethod
    def carica_partita(cls, nome_file):
        """Carica una partita salvata"""
        try:
            with open(nome_file, 'r', encoding='utf-8') as f:
                dati = json.load(f)
            
            gioco = cls.__new__(cls)
            # Inizializza attributi di default (come fa __init__)
            gioco.mazzo = []
            gioco.colonne = [[] for _ in range(7)]
            gioco.pile_finali = {seme: [] for seme in SEMI}
            gioco.riserva = []
            gioco.scarti = []
            gioco.punteggio = 0
            gioco.tempo_inizio = time.time()
            gioco.mosse = 0
            gioco.modalita = dati.get('modalita', 'normale')
            gioco.tema = dati.get('tema', 'classico')
            gioco.tempo_limite = dati.get('tempo_limite', 600 if gioco.modalita == "tempo" else None)

            # Sovrascrivi con i dati del salvataggio
            gioco.riserva = [Carta.from_dict(c) for c in dati['riserva']]
            gioco.scarti = [Carta.from_dict(c) for c in dati['scarti']]
            gioco.colonne = [[Carta.from_dict(c) for c in colonna] for colonna in dati['colonne']]
            gioco.pile_finali = {seme: [Carta.from_dict(c) for c in pila] for seme, pila in dati['pile_finali'].items()}
            gioco.punteggio = dati['punteggio']
            gioco.mosse = dati['mosse']
            gioco.tempo_inizio = time.time() - dati['tempo_gioco']

            print(f"Partita caricata da: {nome_file}")
            return gioco
        except Exception as e:
            print(f"Errore durante il caricamento: {e}")
            return None

    def mostra_aiuto(self):
        """Mostra le regole e i comandi del gioco"""
        print("\n" + "="*60)
        print("REGOLE DEL SOLITARIO (KLONDIKE)")
        print("="*60)
        print("• L'obiettivo è spostare tutte le carte nelle pile finali, ordinate per seme")
        print("  da Asso a Re.")
        print("• Nelle colonne, le carte devono essere disposte in ordine decrescente")
        print("  alternando colori rossi e neri.")
        print("• Solo i Re possono essere posizionati in colonne vuote.")
        print("• Gli Assi vanno nelle pile finali, seguiti dalle carte dello stesso seme")
        print("  in ordine crescente.")
        print("\nCOMANDI:")
        print("0 - Consiglio  🤖 SOLITARIO AI 🤖")
        print("1 - Pesca una carta")
        print("2 [colonna_da] [colonna_a] - Sposta carte tra colonne")
        print("3 scarti - Sposta carta dagli scarti alla pila finale")
        print("3 colonna [num] - Sposta carta dalla colonna alla pila finale")
        print("4 [colonna] - Sposta dagli scarti alla colonna indicata")
        print("5 - Salva partita")
        print("6 - Carica partita")
        print("7 - Aiuto (mostra questo menu)")
        print("8 - Esci")
        print("9 - Torna al menu principale")  # <--- AGGIUNTA QUI
        print("="*60)

    def verifica_obiettivi(self):
        """Verifica se il giocatore ha raggiunto un obiettivo."""
        if self.mosse <= 50:
            print("\n🎯 Obiettivo raggiunto: Hai completato il gioco in meno di 50 mosse!")
        if self.punteggio >= 500:
            print("\n🎯 Obiettivo raggiunto: Hai superato i 500 punti!")
        if self.modalita == "tempo" and int(time.time() - self.tempo_inizio) <= self.tempo_limite:
            print("\n🎯 Obiettivo raggiunto: Hai completato il gioco entro il tempo limite!")

    def consiglia_mossa(self):
        """Suggerisce la prossima mossa migliore in base alla situazione attuale."""
        # 1. Prova a spostare una carta scoperta nelle pile finali
        for idx, col in enumerate(self.colonne):
            if col and col[-1].scoperta:
                carta = col[-1]
                pila = self.pile_finali[carta.seme]
                if (not pila and carta.valore == 'A') or (pila and carta.valore_numerico() == pila[-1].valore_numerico() + 1):
                    return (f"Sposta la carta {carta} dalla colonna {idx+1} alla pila finale. "
                            f"[3 colonna {idx+1}]")
        # 2. Prova a spostare dagli scarti alla pila finale
        if self.scarti:
            carta = self.scarti[-1]
            pila = self.pile_finali[carta.seme]
            if (not pila and carta.valore == 'A') or (pila and carta.valore_numerico() == pila[-1].valore_numerico() + 1):
                return f"Sposta la carta {carta} dagli scarti alla pila finale. [3 scarti]"
        # 3. Prova a spostare dagli scarti a una colonna
        if self.scarti:
            carta = self.scarti[-1]
            for idx, col in enumerate(self.colonne):
                if not col and carta.valore == 'K':
                    return f"Sposta il Re {carta} dagli scarti alla colonna vuota {idx+1}. [4 {idx+1}]"
                elif col and COLORI[col[-1].seme] != COLORI[carta.seme] and carta.valore_numerico() == col[-1].valore_numerico() - 1:
                    return f"Sposta la carta {carta} dagli scarti alla colonna {idx+1}. [4 {idx+1}]"
        # 4. Prova a spostare tra colonne
        for da_idx, col in enumerate(self.colonne):
            for i in range(len(col)):
                if col[i].scoperta:
                    gruppo = col[i:]
                    for a_idx, dest in enumerate(self.colonne):
                        if da_idx == a_idx:
                            continue
                        # EVITA di suggerire lo spostamento su una colonna vuota se il gruppo è l'intera colonna
                        if not dest and gruppo[0].valore == 'K' and i > 0:
                            return (f"Sposta il gruppo {', '.join(str(c) for c in gruppo)} dalla colonna {da_idx+1} "
                                    f"alla colonna vuota {a_idx+1}. [2 {da_idx+1} {a_idx+1}]")
                        elif dest and COLORI[dest[-1].seme] != COLORI[gruppo[0].seme] and gruppo[0].valore_numerico() == dest[-1].valore_numerico() - 1:
                            return (f"Sposta il gruppo {', '.join(str(c) for c in gruppo)} dalla colonna {da_idx+1} "
                                    f"alla colonna {a_idx+1}. [2 {da_idx+1} {a_idx+1}]")
                    break
        # 5. Se nessuna mossa, consiglia di pescare
        if self.riserva:
            return "Pesca una carta dal mazzo. [1]"
        return "Nessuna mossa consigliata: valuta di pescare o rimescolare gli scarti."

def trova_salvataggi():
    """Trova tutti i file di salvataggio nella directory corrente"""
    salvataggi = []
    for file in os.listdir():
        if file.endswith(".json"):
            salvataggi.append(file)
    return salvataggi

def mostra_tutorial():
    print("\n" + "="*60)
    print("🎓 BENVENUTO AL TUTORIAL INTERATTIVO DEL SOLITARIO 🎓")
    print("="*60)
    input("Premi INVIO per continuare...")
    print("\nNel solitario, l'obiettivo è spostare tutte le carte nelle pile finali, ordinate per seme da Asso a Re.")
    input("Premi INVIO per vedere come si pesca una carta...")
    print("\n[1] PESCA: Digita '1' per pescare una carta dal mazzo. La carta pescata finirà negli scarti.")
    input("Premi INVIO per continuare...")

    print("\n[2] SPOSTA: Digita '2 [da] [a]' per spostare una o più carte tra colonne.")
    print(" - [da] è il numero della colonna di partenza, [a] quello di arrivo (es: 2 1 3 sposta da colonna 1 a colonna 3).")
    print(" - Puoi spostare solo gruppi di carte scoperte in sequenza decrescente e alternando i colori (rosso/nero).")
    print(" - Solo un Re può essere spostato su una colonna vuota.")
    input("Premi INVIO per continuare...")

    print("\n[3] FINALE: Digita '3 scarti' per spostare la carta dagli scarti alla pila finale,")
    print("   oppure '3 colonna [num]' per spostare la carta scoperta in cima a una colonna nella pila finale.")
    print(" - Le pile finali vanno costruite per seme, dall'Asso al Re.")
    input("Premi INVIO per continuare...")

    print("\n[4] SPOSTA DAGLI SCARTI: Digita '4 [colonna]' per spostare la carta scoperta dagli scarti alla colonna scelta.")
    print(" - Anche qui valgono le regole di alternanza colore e sequenza decrescente.")
    input("Premi INVIO per continuare...")

    print("\nPuoi sempre digitare '7' per rivedere l'aiuto durante la partita.")
    input("Premi INVIO per terminare il tutorial...")
    print("\nBuon divertimento!")
    print("="*60)
    input("Premi INVIO per iniziare a giocare...")

def tutorial_gia_visto():
    return os.path.exists(".tutorial_solitario_visto")

def segna_tutorial_visto():
    with open(".tutorial_solitario_visto", "w") as f:
        f.write("visto")

def main():
    # Ridimensiona il terminale a 102x27 (funziona su molti terminali, non tutti)
    if os.name == "nt":
        os.system('mode con: cols=102 lines=27')
    else:
        # Il comando seguente funziona su molti terminali Linux/macOS (non su tutti, ma su Terminal e iTerm sì)
        os.system('printf "\\033[8;28;102t"')
    tema = "classico"
    gioco = None  # <--- AGGIUNTA QUI
    # Menu iniziale
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║     ███████╗ ██████╗ ██╗     ██╗████████╗ █████╗ ██████╗ ██╗ ██████╗      ║")
        print("║     ██╔════╝██╔═══██╗██║     ██║╚══██╔══╝██╔══██╗██╔══██╗██║██╔═══██╗     ║")
        print("║     ███████╗██║   ██║██║     ██║   ██║   ███████║██████╔╝██║██║   ██║     ║")
        print("║     ╚════██║██║   ██║██║     ██║   ██║   ██╔══██║██╔══██╗██║██║   ██║     ║")
        print("║     ███████║╚██████╔╝███████╗██║   ██║   ██║  ██║██║  ██║██║╚██████╔╝     ║")
        print("║     ╚══════╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝      ║")
        print("╚═══════════════════════════════════════════════════════════════════════════╝")
        print("\n1. Nuova partita (Normale)")
        print("2. Nuova partita (A tempo)")
        print("3. Nuova partita (Difficile)")
        print("4. Carica partita")
        print("5. Cambia tema")
        print("6. Rivedi il tutorial")  # <--- AGGIUNTA QUI
        print("7. Esci")  # <-- Ora è l'ultima voce

        scelta = input("\nScegli un'opzione: ").strip()
        
        if scelta == "1":
            gioco = Solitario(tema=tema)
            break
        elif scelta == "2":
            print("\nScegli il tempo massimo:")
            print("1. 5 minuti")
            print("2. 10 minuti")
            print("3. 15 minuti")
            t = input("Seleziona (1-3): ").strip()
            if t == "1":
                tempo_limite = 300
            elif t == "3":
                tempo_limite = 900
            else:
                tempo_limite = 600
            gioco = Solitario(modalita="tempo", tema=tema, tempo_limite=tempo_limite)
            break
        elif scelta == "3":
            gioco = Solitario(modalita="difficile", tema=tema)
            break
        elif scelta == "4":
            salvataggi = trova_salvataggi()
            if not salvataggi:
                print("\nNessun salvataggio trovato. Premi INVIO per tornare al menu...")
                input()
                continue

            while True:
                print("\nSalvataggi disponibili:")
                for i, s in enumerate(salvataggi, 1):
                    print(f"{i}. {s}")
                print("0. Torna indietro")
                print("D. Elimina un salvataggio")

                scelta_salva = input("\nSeleziona un salvataggio da caricare (numero), oppure 'D' per eliminare: ").strip().lower()
                if scelta_salva == "0":
                    break
                elif scelta_salva == "d":
                    try:
                        idx_del = int(input("Digita il numero della partita da eliminare: ")) - 1
                        if 0 <= idx_del < len(salvataggi):
                            nome_file = salvataggi[idx_del]
                            os.remove(nome_file)
                            print(f"Salvataggio '{nome_file}' eliminato.")
                            salvataggi = trova_salvataggi()
                            if not salvataggi:
                                print("Nessun altro salvataggio rimasto. Premi INVIO per tornare al menu...")
                                input()
                                gioco = None  # <--- AGGIUNTA QUI
                                break
                        else:
                            print("Indice non valido.")
                    except (ValueError, OSError):
                        print("Errore nell'eliminazione.")
                else:
                    try:
                        idx = int(scelta_salva) - 1
                        if 0 <= idx < len(salvataggi):
                            gioco = Solitario.carica_partita(salvataggi[idx])
                            if gioco:
                                break
                            else:
                                print("Errore nel caricamento del salvataggio. Premi INVIO per tornare al menu...")
                                input()
                                break
                        else:
                            print("Indice non valido. Premi INVIO per continuare...")
                            input()
                    except ValueError:
                        print("Inserisci un numero valido o 'D'. Premi INVIO per continuare...")
                        input()
            if gioco:
                break
        elif scelta == "5":
            print("\nTemi disponibili:")
            print("1. Classico (rosso/nero)")
            print("2. Blu/Verde")
            print("3. Chiaro")
            t = input("Scegli il tema (1-3): ").strip()
            if t == "2":
                tema = "blu_verde"
            elif t == "3":
                tema = "chiaro"
            else:
                tema = "classico"
        elif scelta == "6":
            mostra_tutorial()
            input("Premi INVIO per tornare al menu...")
        elif scelta == "7":
            print("Grazie per aver giocato! Arrivederci.")
            return
        else:
            print("Opzione non valida. Premi INVIO per riprovare...")
            input()

    # Dopo aver creato l'oggetto gioco e PRIMA del ciclo principale:
    if not tutorial_gia_visto():
        mostra_tutorial()
        segna_tutorial_visto()
    gioco.mostra_aiuto()
    input("\nPremi INVIO per iniziare a giocare...")
    
    # Loop principale di gioco
    while True:
        # Controllo del tempo per la modalità a tempo
        if gioco.modalita == "tempo":
            tempo_trascorso = int(time.time() - gioco.tempo_inizio)
            tempo_rimanente = max(0, gioco.tempo_limite - tempo_trascorso)
            if tempo_rimanente == 0:
                print("\n⏰ TEMPO SCADUTO! Hai perso la partita.")
                input("\nPremi INVIO per terminare...")
                break

        gioco.mostra()
        if gioco.controlla_vittoria():
            tempo_totale = int(time.time() - gioco.tempo_inizio)
            minuti = tempo_totale // 60
            secondi = tempo_totale % 60
            print("\n🏆 HAI VINTO! 🏆")
            print(f"Punteggio finale: {gioco.punteggio}")
            print(f"Mosse totali: {gioco.mosse}")
            print(f"Tempo impiegato: {minuti}:{secondi:02d}")
            gioco.verifica_obiettivi()  # Verifica gli obiettivi
            input("\nPremi INVIO per terminare...")
            break
            
        print("\nComandi:")
        print(" [0] 🤖 Consiglio automatico SOLITARIO AI 🤖 ")
        print(" [1] Pesca carta")
        print(" [2] Sposta da colonna a colonna (es: 2 1 5)")
        print(" [3] Sposta carta a pila finale (es: 3 scarti / 3 colonna 4)")
        print(" [4] Sposta dagli scarti a colonna (es: 4 3)")
        print(" [5] Salva partita  [6] Carica partita  [7] Aiuto  [8] Esci  [9] Menu principale")

        # --- MESSAGGIO DI SCONFITTA SOTTO I COMANDI ---
        consiglio = gioco.consiglia_mossa()
        if consiglio.startswith("Nessuna mossa") and not gioco.riserva:
            print("\n❌ Non ci sono più mosse possibili e il mazzo è finito.")
            print("💀 HAI PERSO! 💀")
        # ------------------------------------------------

        scelta = input("Comando: ").strip().lower()
        
        if scelta == "0":
            consiglio = gioco.consiglia_mossa()
            print("\n🤖 Consiglio: " + consiglio)
            if consiglio.startswith("Nessuna mossa") and not gioco.riserva:
                print("\n❌ Non ci sono più mosse possibili e il mazzo è finito.")
                print("💀 HAI PERSO! 💀")
                input("\nPremi INVIO per terminare la partita...")
                break
            elif consiglio.startswith("Nessuna mossa"):
                print("⚠️  Non ci sono più mosse possibili. La partita potrebbe essere bloccata, prova a ripescare ma dei dubbi per te.")
        elif scelta == "1":
            gioco.pesca()
        elif scelta.startswith("2"):
            try:
                parti = scelta.split()
                if len(parti) == 3:
                    gioco.sposta_colonna(int(parti[1])-1, int(parti[2])-1)
                else:
                    print("Formato non valido. Usa: 2 [da] [a]")
            except (ValueError, IndexError):
                print("Parametri non validi. Usa numeri per le colonne.")
        elif scelta.startswith("3"):
            try:
                parti = scelta.split()
                if len(parti) == 2 and parti[1] == "scarti":
                    gioco.sposta_a_finale("scarti")
                elif len(parti) == 3 and parti[1] == "colonna":
                    gioco.sposta_a_finale("colonna", int(parti[2]) - 1)
                else:
                    print("Formato non valido. Esempio: 3 scarti o 3 colonna 4")
            except (ValueError, IndexError):
                print("Comando non valido.")
        elif scelta.startswith("4"):
            try:
                _, colonna = scelta.split()
                gioco.sposta_colonna(0, int(colonna)-1, da_scarti=True)
            except (ValueError, IndexError):
                print("Formato non valido. Usa: 4 [colonna]")
        elif scelta == "5":
            nome_file = input("Inserisci un nome per il salvataggio (senza estensione, lascia vuoto per nome automatico): ").strip()
            if nome_file:
                if not nome_file.endswith(".json"):
                    nome_file += ".json"
                gioco.salva_partita(nome_file)
            else:
                gioco.salva_partita()
        elif scelta == "6":
            salvataggi = trova_salvataggi()
            if not salvataggi:
                print("Nessun salvataggio trovato.")
            else:
                print("\nSalvataggi disponibili:")
                for i, s in enumerate(salvataggi, 1):
                    print(f"{i}. {s}")
                try:
                    idx = int(input("\nSeleziona un salvataggio (0 per annullare): ")) - 1
                    if idx == -1:
                        continue
                    if 0 <= idx < len(salvataggi):
                        nuovo_gioco = Solitario.carica_partita(salvataggi[idx])
                        if nuovo_gioco:
                            gioco = nuovo_gioco
                    else:
                        print("Indice non valido.")
                except ValueError:
                    print("Inserisci un numero valido.")
        elif scelta == "7":
            gioco.mostra_aiuto()
        elif scelta == "8":
            if input("Sei sicuro di voler uscire? (s/n): ").lower() == 's':
                print("Partita terminata.")
                break
        elif scelta == "9":
            print("Torno al menu principale...")
            input("Premi INVIO per continuare...")
            main()  # <--- RICHIAMA IL MENU PRINCIPALE
            return
        else:
            print("Comando sconosciuto. Premi 7 per visualizzare l'aiuto.")
    
        input("\nPremi INVIO per continuare...")

if __name__ == "__main__":
    main()
