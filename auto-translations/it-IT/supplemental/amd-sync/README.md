<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Sviluppo Remoto con AMD Sync

## Panoramica

**AMD Sync** trasforma il tuo laptop in una postazione di controllo remota per AMD Ryzen™ AI Halo. Dimentica la configurazione manuale di SSH, chiavi e IDE — installa AMD Sync e ottieni accesso con un solo clic a un terminale remoto, VS Code, JupyterLab e un dashboard in tempo reale di GPU/CPU/memoria su Ryzen AI Halo.

Il tuo computer locale rimane familiare; ogni comando, notebook e modello viene eseguito su Ryzen AI Halo.

> **Suggerimento**: Questa pagina conterrà tutti i nuovi aggiornamenti di AMDSync.

## Cosa Imparerai

- Abilitare SSH su Ryzen AI Halo e connettersi ad esso da AMD Sync
- Avviare VS Code, Terminal, JupyterLab e Live Metrics su Ryzen AI Halo con un solo clic
- Organizzare il lavoro remoto utilizzando le cartelle di progetto gestite da AMD Sync

---

## Concetti Fondamentali

AMD Sync ha due componenti: un **client** (il tuo laptop, che esegue l'app AMD Sync) e un **server** (Ryzen AI Halo, che esegue un server SSH nel quale AMD Sync effettua il tunneling). Tutto ciò che avvii da AMD Sync — VS Code, un terminale, un notebook — si apre localmente ma viene eseguito su Ryzen AI Halo.

> **Client supportati:** Windows 11 e Linux. macOS non è supportato.

---

## Passaggio 1 — Abilitare SSH su Ryzen AI Halo


> **Nota:** Su Windows, Ryzen AI Halo viene fornito con il server SSH *disattivato per impostazione predefinita*. Su Linux, viene fornito con il server SSH *attivato per impostazione predefinita*.

1. Su Ryzen AI Halo, apri **AMD Ryzen™ AI Developer Center**.
2. Vai alla scheda **Remote**.
3. Attiva **SSH Server**.
4. Prendi nota di **IP Address**, **Port** e **Username** mostrati in **Server Information** — li incollerai in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Nota:** Questo è AMD Developer Center per Windows. Quello per Linux potrebbe avere un'interfaccia diversa, ma funzionalità remote simili.

> **Suggerimento:** AMD Sync richiede la **password di accesso al sistema operativo** di quell'utente, non una password di Developer Center.

---

## Passaggio 2 — Installare AMD Sync sul Client

AMD Sync funziona su Windows 11 e Linux. Scarica il programma di installazione per il tuo sistema operativo, quindi segui i passaggi seguenti. Dopo l'installazione, fai clic su **Accept & Install** nella schermata **Get Started** — AMD Sync si avvia automaticamente al termine.

### Windows

[Scarica AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Fai doppio clic su `AMDSyncInstaller.exe`.
2. Fai clic su **Accept & Install**.

> Se Windows Firewall ti chiede conferma, consenti l'accesso alla rete ad AMD Sync in modo che possa raggiungere Ryzen AI Halo tramite SSH.

### Linux

Fai clic sul link per scaricare il formato preferito:

| Formato | Download | Comando di installazione |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Nota:** Ubuntu App Center potrebbe segnalare un file `.deb` aperto localmente come *"Potenzialmente non sicuro."* Questo è l'avviso standard per qualsiasi programma di installazione locale di terze parti. Se il doppio clic sul file `.deb` non funziona, utilizza il comando da terminale indicato sopra.

---

## Passaggio 3 — Connettersi a Ryzen AI Halo

Al primo avvio, AMD Sync mostra il modulo **Add a Remote Device**. Compilalo utilizzando i valori dalla scheda **Remote** di Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Note |
|-------|-------|
| **Device Name** *(opzionale)* | Un'etichetta descrittiva come `Ryzen AI Halo`. Il valore predefinito è `Device 1`, `Device 2`, … |
| **Hostname or IP** | Dalla scheda Remote |
| **SSH Port** | Dalla scheda Remote (solo numeri) |
| **Username** | Il nome del tuo account di sistema operativo su Ryzen AI Halo |
| **Password** | La password di accesso al sistema operativo — mascherata durante la digitazione |

Fai clic su **Add Device**. Dopo una breve schermata di caricamento, vedrai **"Connection Successful"** e accederai alla vista principale, che risiede nella barra delle applicazioni. Fai clic fuori dalla finestra per chiuderla; AMD Sync rimane in esecuzione ed è accessibile con un solo clic.

> **Se la connessione non riesce,** AMD Sync torna al modulo con i valori inseriti preservati. Le cause più comuni sono SSH disabilitato su Ryzen AI Halo, password errata o i due dispositivi su reti diverse.

---

## Passaggio 4 — Avviare il Primo Strumento Remoto

La vista principale offre cinque componenti accessibili con un solo clic — tutti disponibili indipendentemente dal sistema operativo in esecuzione sul client e su Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | Funzione |
|-----------|--------------|
| **Directory** | Seleziona la cartella su Ryzen AI Halo in cui VS Code, Terminal e JupyterLab si apriranno. Il valore predefinito è un'area di lavoro gestita `Documents/AMD_Sync`. |
| **VS Code** | Apre VS Code localmente con un tunnel SSH nella cartella selezionata. |
| **Terminal** | Apre un terminale locale connesso tramite SSH a Ryzen AI Halo, nella cartella selezionata. |
| **JupyterLab** | Avvia un progetto notebook connesso tramite SSH a Ryzen AI Halo, limitato alla cartella selezionata. |
| **Live Metrics** | Vista in tempo reale dell'utilizzo di GPU, memoria e CPU su Ryzen AI Halo. |

### Prova VS Code

Per il primo avvio, prova **VS Code**.

1. Lascia **Directory** sul valore predefinito `~/Documents/AMD_Sync`.
2. Fai clic su **VS Code**.
3. AMD Sync crea `Documents/AMD_Sync/Project_1` su Ryzen AI Halo e apre VS Code localmente, con tunneling al suo interno.

Ora stai modificando file che risiedono su Ryzen AI Halo con la tua configurazione locale di VS Code. Crea `helloworld.py`, aggiungi `print("hello world")`, apri il terminale integrato (`` Ctrl + ` ``), ed eseguilo:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barra di stato mostra **SSH: Linux** — la prova che il tuo codice è in esecuzione su Ryzen AI Halo, non sul tuo laptop.

### Prova il Terminale

Fai clic su **Terminal** per accedere alla stessa cartella tramite SSH senza lasciare la tastiera.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Su Windows, il terminale predefinito è **PowerShell** — passa a **Windows Command Prompt** dal menu Impostazioni se preferisci. Su Linux, AMD Sync utilizza il terminale di sistema predefinito.

---

## Come Funziona la Directory

Il menu a discesa **Directory** è il controllo più importante in AMD Sync — determina dove ogni strumento avviato atterrerà su Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predefinito)** — Avviare VS Code o JupyterLab da qui crea automaticamente una nuova cartella di progetto (`Project_1`, `Project_2`, … per VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … per JupyterLab).
- **Cartelle di progetto esistenti** — Qualsiasi sottocartella diretta di `AMD_Sync` (incluse le cartelle create manualmente su Ryzen AI Halo) appare nel menu a discesa. L'ultima cartella utilizzata diventa quella predefinita la volta successiva.
- **Percorsi personalizzati** — Digita qualsiasi percorso assoluto per aprire una cartella in un'altra posizione su Ryzen AI Halo. AMD Sync si limita ad *aprirla* — non creerà cartelle al di fuori di `AMD_Sync`, e i percorsi personalizzati non vengono salvati tra le sessioni.

Se un percorso personalizzato non funziona, AMD Sync ti indica il motivo: sintassi non valida, cartella inesistente o percorso che punta a un file.

---

## Live Metrics e JupyterLab

- **Live Metrics** — Un dashboard in tempo reale dell'utilizzo di GPU, memoria e CPU. Il modo più rapido per confermare che un'esecuzione di addestramento remota stia effettivamente utilizzando l'hardware.
- **JupyterLab** — Un progetto notebook completo connesso tramite SSH a Ryzen AI Halo, con un terminale integrato per combinare celle notebook e comandi shell senza uscire dall'interfaccia.

---

## Impostazioni e Dispositivi Multipli

Il menu **Settings** ha tre schede:

| Scheda | Contenuto |
|-----|----------------|
| **Devices** | Elenca tutti i Ryzen AI Halo a cui ti sei connesso con successo. Riconnetti, modifica le credenziali o aggiungi un nuovo dispositivo. |
| **Information** | Link alla documentazione e al supporto del forum. |
| **Customize** | Riposiziona l'app sul desktop, cambia il tipo di terminale (solo Windows) e verifica gli aggiornamenti di AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo di terminale (Windows)** — Scegli tra **PowerShell** (predefinito) e **Windows Command Prompt**.
- **Tipo di terminale (Linux)** — È disponibile solo il terminale di sistema predefinito.
- **Aggiornamenti dell'app** — Questa scheda è il posto giusto per verificare e installare nuove versioni di AMD Sync dall'interno dell'interfaccia; non è necessario un programma di aggiornamento separato.

> Un dispositivo appare in **Devices** solo dopo una prima connessione riuscita, quindi i tentativi falliti non ingombrano l'elenco.

---

## Risoluzione dei Problemi

- **La connessione fallisce immediatamente** — Verifica che il server SSH sia abilitato nella scheda **Remote** di Ryzen AI Halo in Developer Center.
- **Errore di password errata** — Utilizza la **password di accesso al sistema operativo** su Ryzen AI Halo, non le password di Developer Center.
- **Il pulsante VS Code non fa nulla** — Installa VS Code sul tuo computer client da [code.visualstudio.com](https://code.visualstudio.com).
- **Icona AMD Sync nella barra delle applicazioni mancante (Linux/GNOME)** — Installa e abilita l'estensione AppIndicator.
- **Il file `.deb` non si apre dal file manager** — Utilizza `sudo apt install ./AMDSyncInstaller.deb` da un terminale.

---