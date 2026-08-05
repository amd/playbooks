<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Sviluppo remoto con AMD Sync

## Panoramica

**AMD Sync** trasforma il tuo laptop in una postazione di controllo remota per l'AMD Ryzen™ AI Halo. Salta la configurazione manuale di SSH, chiavi e IDE: installa AMD Sync e ottieni l'accesso con un clic a un terminale remoto, VS Code, JupyterLab e a una dashboard live di GPU/CPU/memoria sul Ryzen AI Halo.

Il tuo computer locale rimane familiare; ogni comando, notebook e modello viene eseguito sul Ryzen AI Halo.

> **Suggerimento**: questa pagina conterrà tutti i nuovi aggiornamenti di AMDSync.

## Cosa imparerai

- Abilitare SSH sul Ryzen AI Halo e connettersi ad esso da AMD Sync
- Avviare VS Code, Terminale, JupyterLab e Live Metrics collegati al Ryzen AI Halo con un clic
- Organizzare il lavoro remoto utilizzando le cartelle di progetto gestite di AMD Sync

---

## Concetti fondamentali

AMD Sync ha due lati: un **client** (il tuo laptop, su cui è in esecuzione l'app AMD Sync) e un **server** (il Ryzen AI Halo, su cui è in esecuzione un server SSH a cui AMD Sync si collega tramite tunnel). Tutto ciò che avvii da AMD Sync — VS Code, un terminale, un notebook — si apre localmente ma viene eseguito sul Ryzen AI Halo.

> **Client supportati:** Windows 11 e Linux. macOS non è supportato.

---

## Passaggio 1 — Abilitare SSH sul Ryzen AI Halo


> **Nota:** su Windows, il Ryzen AI Halo viene fornito con il server SSH *disattivato per impostazione predefinita*. Su Linux, viene fornito con il server SSH *attivato per impostazione predefinita*.

1. Sul Ryzen AI Halo, apri **AMD Ryzen™ AI Developer Center**.
2. Vai alla scheda **Remote**.
3. Attiva **SSH Server**.
4. Prendi nota di **IP Address**, **Port** e **Username** mostrati in **Server Information**: li incollerai in AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Nota:** questo è l'AMD Developer Center per Windows. Quello per Linux potrebbe avere un'interfaccia diversa, ma una funzionalità remota simile.

> **Suggerimento:** AMD Sync richiede la **password di accesso del sistema operativo** di quell'utente, non una password del Developer Center.

---

## Passaggio 2 — Installare AMD Sync sul tuo client

AMD Sync funziona su Windows 11 e Linux. Scarica il programma di installazione per il tuo sistema operativo, quindi segui i passaggi riportati di seguito. Dopo l'installazione, fai clic su **Accept & Install** nella schermata **Get Started** — AMD Sync si avvia automaticamente al termine.

### Windows

[Scarica AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Fai doppio clic su `AMDSyncInstaller.exe`.
2. Fai clic su **Accept & Install**.

> Se Windows Firewall mostra una richiesta, consenti l'accesso alla rete ad AMD Sync in modo che possa raggiungere il Ryzen AI Halo tramite SSH.

### Linux

Fai clic sul link per scaricare il formato preferito:

| Formato | Download | Comando di installazione |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Nota:** Ubuntu App Center potrebbe segnalare un file `.deb` aperto localmente come *"Potenzialmente non sicuro."* Si tratta dell'avviso standard per qualsiasi programma di installazione locale di terze parti. Se il doppio clic sul file `.deb` non funziona, utilizza il comando da terminale riportato sopra.

---

## Passaggio 3 — Connettersi al tuo Ryzen AI Halo

Al primo avvio, AMD Sync mostra il modulo **Add a Remote Device**. Compilalo utilizzando i valori dalla scheda **Remote** del Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Note |
|-------|-------|
| **Device Name** *(facoltativo)* | Un'etichetta descrittiva come `Ryzen AI Halo`. Il valore predefinito è `Device 1`, `Device 2`, … |
| **Hostname or IP** | Dalla scheda Remote |
| **SSH Port** | Dalla scheda Remote (solo numeri) |
| **Username** | Il nome del tuo account del sistema operativo sul Ryzen AI Halo |
| **Password** | La password di accesso del tuo sistema operativo — mascherata durante la digitazione |

Fai clic su **Add Device**. Dopo una breve schermata di caricamento, vedrai **"Connection Successful"** e arriverai alla schermata principale, che si trova nella barra delle applicazioni di sistema. Fai clic al di fuori della finestra per chiuderla; AMD Sync continua a essere in esecuzione ed è a portata di un clic.

> **Se la connessione non riesce,** AMD Sync torna al modulo con i valori inseriti mantenuti. Le cause più comuni sono l'SSH disattivato sul Ryzen AI Halo, la password errata, oppure i due dispositivi che si trovano su reti diverse.

---

## Passaggio 4 — Avviare il tuo primo strumento remoto

La schermata principale offre cinque componenti attivabili con un clic — tutti disponibili indipendentemente dal sistema operativo su cui sono in esecuzione il client e il Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | Funzione |
|-----------|--------------|
| **Directory** | Sceglie la cartella sul Ryzen AI Halo in cui verranno aperti VS Code, Terminale e JupyterLab. Il valore predefinito è uno spazio di lavoro gestito `Documents/AMD_Sync`. |
| **VS Code** | Apre VS Code localmente con un tunnel SSH verso la cartella selezionata. |
| **Terminal** | Apre un terminale locale connesso tramite SSH al Ryzen AI Halo, nella cartella selezionata. |
| **JupyterLab** | Avvia un progetto notebook connesso tramite SSH al Ryzen AI Halo, limitato alla cartella selezionata. |
| **Live Metrics** | Vista in tempo reale dell'utilizzo di GPU, memoria e CPU sul Ryzen AI Halo. |

### Prova VS Code

Per il tuo primo avvio, prova **VS Code**.

1. Lascia **Directory** sul valore predefinito `~/Documents/AMD_Sync`.
2. Fai clic su **VS Code**.
3. AMD Sync crea `Documents/AMD_Sync/Project_1` sul Ryzen AI Halo e apre VS Code localmente, collegato tramite tunnel a tale cartella.

Ora stai modificando file che si trovano sul Ryzen AI Halo con la tua configurazione locale di VS Code. Crea `helloworld.py`, aggiungi `print("hello world")`, apri il terminale integrato (`` Ctrl + ` ``) ed eseguilo:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

La barra di stato mostra **SSH: Linux** — la prova che il tuo codice viene eseguito sul Ryzen AI Halo e non sul tuo laptop.
### Prova il Terminale

Fai clic su **Terminale** per accedere alla stessa cartella tramite SSH senza staccare le mani dalla tastiera.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Su Windows, il terminale predefinito è **PowerShell** — passa a **Prompt dei comandi di Windows** dal menu Impostazioni se preferisci. Su Linux, AMD Sync utilizza il terminale predefinito del sistema.

---

## Come funziona la Directory

Il menu a discesa **Directory** è il controllo più importante di AMD Sync — decide dove atterra ogni strumento che avvii sul Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (predefinito)** — Avviare VS Code o JupyterLab da qui crea automaticamente una nuova cartella di progetto (`Project_1`, `Project_2`, … per VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … per JupyterLab).
- **Cartelle di progetto esistenti** — Ogni sottocartella diretta di `AMD_Sync` (incluse le cartelle create manualmente sul Ryzen AI Halo) appare nel menu a discesa. L'ultima cartella utilizzata diventa quella predefinita per la volta successiva.
- **Percorsi personalizzati** — Digita qualsiasi percorso assoluto per aprire una cartella altrove sul Ryzen AI Halo. AMD Sync si limita ad *aprirla* — non creerà cartelle al di fuori di `AMD_Sync`, e i percorsi personalizzati non vengono salvati tra le sessioni.

Se un percorso personalizzato non funziona, AMD Sync ti spiega il motivo: sintassi non valida, cartella inesistente, oppure il percorso punta a un file.

---

## Metriche in tempo reale e JupyterLab

- **Metriche in tempo reale** — Una dashboard live dell'utilizzo di GPU, memoria e CPU. Il modo più rapido per confermare che un'esecuzione di training remota stia effettivamente utilizzando l'hardware.
- **JupyterLab** — Un progetto notebook completo connesso via SSH al Ryzen AI Halo, con un proprio terminale integrato per combinare celle notebook e comandi shell senza uscire dall'interfaccia.

---

## Impostazioni e dispositivi multipli

Il menu **Impostazioni** ha tre schede:

| Scheda | Cosa copre |
|-----|----------------|
| **Dispositivi** | Elenca ogni Ryzen AI Halo a cui ti sei connesso con successo. Riconnetti, modifica le credenziali o aggiungi un nuovo dispositivo. |
| **Informazioni** | Link alla documentazione e al supporto del forum. |
| **Personalizza** | Riposiziona l'app sul desktop, cambia il tipo di terminale (solo Windows) e controlla gli aggiornamenti di AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo di terminale (Windows)** — Scegli tra **PowerShell** (predefinito) e **Prompt dei comandi di Windows**.
- **Tipo di terminale (Linux)** — È disponibile solo il terminale predefinito del sistema.
- **Aggiornamenti dell'app** — Questa scheda è il posto giusto per verificare e installare nuove versioni di AMD Sync direttamente dall'interfaccia; non è necessario alcun aggiornatore separato.

> Un dispositivo appare in **Dispositivi** solo dopo una prima connessione riuscita, così i tentativi falliti non ingombrano l'elenco.

---

## Risoluzione dei problemi

- **La connessione fallisce immediatamente** — Verifica che il server SSH sia abilitato nella scheda **Remote** del Developer Center sul Ryzen AI Halo.
- **Errore di password errata** — Usa la tua **password di accesso del sistema operativo** sul Ryzen AI Halo, non le password prese dal Developer Center.
- **Il pulsante VS Code non fa nulla** — Installa VS Code sulla tua macchina client da [code.visualstudio.com](https://code.visualstudio.com).
- **Icona di AMD Sync mancante nella barra (Linux/GNOME)** — Installa e abilita l'estensione AppIndicator.
- **Il file `.deb` non si apre dal file manager** — Usa `sudo apt install ./AMDSyncInstaller.deb` da un terminale.

---