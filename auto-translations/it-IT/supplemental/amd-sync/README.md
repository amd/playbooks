<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Sviluppo remoto con AMD Sync

## Panoramica

**AMD Sync** trasforma il tuo laptop in una cabina di comando remota per l'AMD Ryzen™ AI Halo. Salta la configurazione manuale di SSH, chiavi e IDE — installa AMD Sync e ottieni l'accesso con un clic a un terminale remoto, VS Code, JupyterLab e una dashboard live di GPU/CPU/memoria sul Ryzen AI Halo.

La tua macchina locale rimane familiare; ogni comando, notebook e modello viene eseguito sul Ryzen AI Halo.

> **Suggerimento**: Questa pagina conterrà tutti i nuovi aggiornamenti relativi ad AMDSync.

## Cosa Imparerai

- Ad abilitare SSH sul Ryzen AI Halo e a connetterti ad esso da AMD Sync
- Ad avviare VS Code, Terminal, JupyterLab e Live Metrics collegati al Ryzen AI Halo con un clic
- A organizzare il lavoro remoto usando le cartelle di progetto gestite da AMD Sync

---

## Concetti Fondamentali

AMD Sync ha due lati: un **client** (il tuo laptop, che esegue l'app AMD Sync) e un **server** (il Ryzen AI Halo, che esegue un server SSH verso cui AMD Sync crea un tunnel). Tutto ciò che avvii da AMD Sync — VS Code, un terminale, un notebook — si apre localmente ma viene eseguito sul Ryzen AI Halo.

> **Client supportati:** Windows 11 e Linux. macOS non è supportato.

---

## Passo 1 — Abilita SSH sul Ryzen AI Halo


> **Nota:** Su Windows, il Ryzen AI Halo viene fornito con il server SSH *disattivato per impostazione predefinita*. Su Linux, viene fornito con il server SSH *attivato per impostazione predefinita*.

1. Sul Ryzen AI Halo, apri l'**AMD Ryzen™ AI Developer Center**.
2. Vai alla scheda **Remote**.
3. Attiva **SSH Server**.
4. Prendi nota dell'**IP Address**, della **Port** e dello **Username** mostrati sotto **Server Information** — li incollerai in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Nota:** Questo è l'AMD Developer Center per Windows. Quello per Linux potrebbe avere un'interfaccia utente diversa, ma funzionalità remote simili.

> **Suggerimento:** AMD Sync richiede la **password di accesso del sistema operativo** dell'utente, non una password del Developer Center.

---

## Passo 2 — Installa AMD Sync sul Tuo Client

AMD Sync funziona su Windows 11 e Linux. Scarica il programma di installazione per il tuo sistema operativo, quindi segui i passaggi seguenti. Dopo l'installazione, fai clic su **Accept & Install** nella schermata **Get Started** — AMD Sync si avvia automaticamente al termine.

### Windows

[Scarica AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Fai doppio clic su `AMDSyncInstaller.exe`.
2. Fai clic su **Accept & Install**.

> Se Windows Firewall mostra una richiesta, consenti l'accesso alla rete ad AMD Sync affinché possa raggiungere il Ryzen AI Halo tramite SSH.

### Linux

Fai clic sul link per scaricare il formato che preferisci:

| Formato | Download | Comando di installazione |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Nota:** Ubuntu App Center potrebbe segnalare un `.deb` aperto localmente come *"Potenzialmente non sicuro."* Si tratta dell'avviso standard per qualsiasi programma di installazione locale di terze parti. Se il doppio clic sul `.deb` non funziona, usa il comando da terminale sopra riportato.

---

## Passo 3 — Connettiti al Tuo Ryzen AI Halo

Al primo avvio, AMD Sync mostra il modulo **Add a Remote Device**. Compilalo utilizzando i valori dalla scheda **Remote** del Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Note |
|-------|-------|
| **Device Name** *(opzionale)* | Un'etichetta descrittiva come `Ryzen AI Halo`. Il valore predefinito è `Device 1`, `Device 2`, … |
| **Hostname or IP** | Dalla scheda Remote |
| **SSH Port** | Dalla scheda Remote (solo numeri) |
| **Username** | Il nome del tuo account del sistema operativo sul Ryzen AI Halo |
| **Password** | La tua password di accesso del sistema operativo — mascherata durante la digitazione |

Fai clic su **Add Device**. Dopo una breve schermata di caricamento, vedrai **"Connection Successful"** e atterrerai sulla vista principale, che risiede nella tua system tray. Fai clic al di fuori della finestra per chiuderla; AMD Sync continua a funzionare in background ed è raggiungibile con un solo clic.

> **Se la connessione fallisce,** AMD Sync torna al modulo mantenendo i valori inseriti. Le cause più comuni sono l'SSH disabilitato sul Ryzen AI Halo, la password errata, oppure i due dispositivi collegati a reti diverse.

---

## Passo 4 — Avvia il Tuo Primo Strumento Remoto

La vista principale offre cinque componenti attivabili con un clic — tutti disponibili indipendentemente dal sistema operativo su cui girano il client e il Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | Cosa fa |
|-----------|--------------|
| **Directory** | Sceglie la cartella sul Ryzen AI Halo in cui verranno aperti VS Code, Terminal e JupyterLab. Il valore predefinito è uno spazio di lavoro gestito `Documents/AMD_Sync`. |
| **VS Code** | Apre VS Code localmente con un tunnel SSH verso la cartella selezionata. |
| **Terminal** | Apre un terminale locale connesso via SSH al Ryzen AI Halo, nella cartella selezionata. |
| **JupyterLab** | Avvia un progetto notebook connesso via SSH al Ryzen AI Halo, limitato alla cartella selezionata. |
| **Live Metrics** | Visualizzazione in tempo reale dell'utilizzo di GPU, memoria e CPU sul Ryzen AI Halo. |

### Prova VS Code

Per il tuo primo avvio, prova **VS Code**.

1. Lascia **Directory** sul valore predefinito `~/Documents/AMD_Sync`.
2. Fai clic su **VS Code**.
3. AMD Sync crea `Documents/AMD_Sync/Project_1` sul Ryzen AI Halo e apre VS Code localmente, con un tunnel verso di essa.

Ora stai modificando file che risiedono sul Ryzen AI Halo utilizzando la tua configurazione locale di VS Code. Crea `helloworld.py`, aggiungi `print("hello world")`, apri il terminale integrato (`` Ctrl + ` ``) ed eseguilo:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barra di stato mostra **SSH: Linux** — a conferma che il tuo codice viene eseguito sul Ryzen AI Halo, non sul tuo laptop.
### Prova il Terminal

Fai clic su **Terminal** per accedere alla stessa cartella tramite SSH senza staccare le mani dalla tastiera.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Su Windows, il terminale predefinito è **PowerShell** — passa a **Windows Command Prompt** dal menu Impostazioni se preferisci. Su Linux, AMD Sync utilizza il terminale predefinito del sistema.

---

## Come funziona la Directory

Il menu a discesa **Directory** è il controllo singolo più importante in AMD Sync — decide dove atterra ogni strumento che avvii sul Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predefinita)** — Avviare VS Code o JupyterLab da qui crea automaticamente una nuova cartella di progetto (`Project_1`, `Project_2`, … per VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … per JupyterLab).
- **Cartelle di progetto esistenti** — Qualsiasi sottocartella diretta di `AMD_Sync` (incluse le cartelle create manualmente sul Ryzen AI Halo) appare nel menu a discesa. L'ultima cartella utilizzata diventa quella predefinita la volta successiva.
- **Percorsi personalizzati** — Digita qualsiasi percorso assoluto per aprire una cartella altrove sul Ryzen AI Halo. AMD Sync si limita ad *aprirla* — non creerà cartelle al di fuori di `AMD_Sync`, e i percorsi personalizzati non vengono salvati tra una sessione e l'altra.

Se un percorso personalizzato non funziona, AMD Sync ti spiega il motivo: sintassi non valida, cartella inesistente, oppure il percorso punta a un file.

---

## Metriche in tempo reale e JupyterLab

- **Metriche in tempo reale** — Una dashboard in tempo reale dell'utilizzo di GPU, memoria e CPU. Il modo più rapido per confermare che un'esecuzione di addestramento remota stia effettivamente utilizzando l'hardware.
- **JupyterLab** — Un progetto notebook completo connesso via SSH al Ryzen AI Halo, con un proprio terminale integrato per combinare celle notebook e comandi shell senza uscire dall'interfaccia.

---

## Impostazioni e dispositivi multipli

Il menu **Impostazioni** ha tre schede:

| Scheda | Cosa copre |
|-----|----------------|
| **Devices** | Elenca ogni Ryzen AI Halo a cui ti sei connesso con successo. Riconnetti, modifica le credenziali o aggiungi un nuovo dispositivo. |
| **Information** | Link alla documentazione e al supporto del forum. |
| **Customize** | Riposiziona l'app sul desktop, cambia tipo di terminale (solo Windows) e verifica la presenza di aggiornamenti di AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo di terminale (Windows)** — Scegli tra **PowerShell** (predefinito) e **Windows Command Prompt**.
- **Tipo di terminale (Linux)** — È disponibile solo il terminale predefinito del sistema.
- **Aggiornamenti dell'app** — Questa scheda è il punto giusto per verificare e installare nuove versioni di AMD Sync direttamente dall'interfaccia; non è necessario un updater separato.

> Un dispositivo appare in **Devices** solo dopo una prima connessione riuscita, così i tentativi falliti non affollano l'elenco.

---

## Risoluzione dei problemi

- **La connessione fallisce immediatamente** — Verifica che il server SSH sia abilitato nella scheda **Remote** del Developer Center sul Ryzen AI Halo.
- **Errore di password errata** — Usa la tua **password di accesso del sistema operativo** sul Ryzen AI Halo, non le password prese dal Developer Center.
- **Il pulsante VS Code non fa nulla** — Installa VS Code sulla tua macchina client da [code.visualstudio.com](https://code.visualstudio.com).
- **Icona di AMD Sync mancante nella tray (Linux/GNOME)** — Installa e abilita l'estensione AppIndicator.
- **Il file `.deb` non si apre dal file manager** — Usa `sudo apt install ./AMDSyncInstaller.deb` da un terminale.
- **La configurazione ricompare a ogni avvio (Linux)**: sblocca il tuo keyring di accesso, oppure avvia con `--password-store=gnome-libsecret`, quindi rifai la configurazione una volta.

---