<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Questo playbook richiede un minimo di **32GB** di memoria di sistema.
<!-- @device:end -->

## Panoramica

Gli agenti di codifica sono strumenti potenti che supportano gli sviluppatori attraverso la collaborazione con agenti AI basati su Large Language Model (LLM). Possono essere integrati nell'ambiente di sviluppo, come il terminale o VS Code, consentendo un'integrazione fluida nel flusso di lavoro dello sviluppatore.

Questo tutorial mostra come utilizzare Cline, VS Code e LM Studio per eseguire un agente di codifica interamente sulla propria macchina locale.

## Cosa Imparerai

* Come eseguire VS Code con l'agente di codifica Cline per supportare le attività di ingegneria del software.
* Come configurare Cline per comunicare con LM Studio per l'inferenza locale degli agenti di codifica.
* Come utilizzare agenti di codifica locali per risolvere attività reali di ingegneria del software.

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software
> **Nota**: Se VS Code non è installato, puoi installarlo tramite Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

<!-- @require:lmstudio,vscode -->

## Avvio e Configurazione di LM Studio

Utilizzeremo LM Studio per servire l'LLM che alimenta l'agente di codifica.

- Nella barra di ricerca, cerca `LM Studio` e avvia l'applicazione. Verrai accolto dalla seguente pagina.

![Schermata iniziale di LM Studio](assets/initial-lm-studio.png)

Successivamente, dobbiamo caricare l'LLM sul sistema. Utilizzeremo il modello `Qwen3-Coder-30B-A3B` con una lunghezza di contesto ampia. (Usa la scheda Modello per installarlo se non lo hai già fatto).
- Fai clic sulla barra di ricerca nella parte superiore della finestra di LM Studio o premi `CTRL+L`. Fai clic sull'interruttore `Manually choose model load parameters` e poi fai clic sul modello Qwen3-Coder-30B-A3B.
- Cambia la lunghezza del contesto da `4096` a `32768` e assicurati che `GPU Offload` sia al massimo. Poi fai clic su `Load Model`.

![Selezione del modello](assets/model-list-zoomed.png)

Utilizziamo una lunghezza di contesto ampia affinché l'agente possa elaborare basi di codice di grandi dimensioni e ricordare le modifiche apportate.

![Configurazione del modello](assets/selecting-model-zoomed.png)

Successivamente, dobbiamo abilitare il server di LM Studio.
- Fai clic sulla scheda Developer o premi `CTRL+2` in LM Studio sulla sinistra.
- Controlla l'interruttore di stato e assicurati che sia impostato su `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Stato del server](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Avvio e Configurazione di VS Code

Installeremo l'estensione Cline in VS Code e la collegheremo al server LM Studio appena creato.
- Nella barra di ricerca, cerca `VS Code` e avvia l'applicazione.
- Fai clic sull'icona `Extensions` nella colonna sinistra di VS Code e cerca `Cline`. Poi fai clic sul pulsante `Install`.

![Installazione dell'estensione Cline](assets/installing-cline-vscode-extension.png)

- Sulla sinistra dovrebbe essere presente un'icona Cline. Fai clic su di essa per aprire Cline. Apparirà una finestra che chiede `How will you use Cline?` Poiché utilizzeremo un LLM locale in esecuzione tramite LM Studio, seleziona `Bring my own API Key` e fai clic su `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Creazione account](assets/cline-how-will-you-use-cline-zoomed.png)

Successivamente, dobbiamo configurare Cline per comunicare con il server LM Studio che abbiamo configurato.
- Imposta il provider API su `LM Studio` e il modello su `Qwen3-Coder-30B-A3B-GGUF`.

>**Suggerimento**: Potrebbero essere disponibili modelli più recenti. Valuta la possibilità di scaricare e passare ai modelli Qwen3.6 se lo desideri.


![Configurazione del modello](assets/cline-model-configuration-zoomed.png)

## Creazione del tuo primo progetto

Usiamo il nostro agente locale per creare un sito web! Apri VSCode in una directory a tua scelta dove Cline creerà i file.
- Per farlo, vai su `File -> Open Folder` in alto a sinistra di VS Code e scegli una cartella come `Documents`.

![Cartella vuota in VS Code](assets/open-cline-test.png)

Ora siamo pronti a fornire un prompt all'agente di codifica locale.
- Fai clic sull'estensione Cline nella colonna sinistra e inserisci un prompt per avviare l'agente. Come esempio, utilizziamo il seguente prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

L'agente inizierà quindi a creare file in base al prompt. Come utente, puoi osservare il codice generato in VS Code come mostrato di seguito. Potrebbe essere necessario fare clic su `Save` ogni volta che Cline desidera creare un file.

![Generazione di codice con Cline](assets/cline-code-generation.png)

Dopo aver generato il software, l'agente ha completato il suo lavoro e puoi eseguire l'applicazione. In questo caso, l'agente ha scritto tre file: `index.html`, `script.js` e `styles.css`. Semplicemente facendo doppio clic sul file HTML possiamo caricare e interagire con il sito web generato.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Passi Successivi

Dopo aver generato il sito web, puoi continuare a lavorare con Cline per migliorarlo. Due possibili miglioramenti sono:

- **Documentazione**: Fornire all'agente il prompt `Add a README` è tutto ciò che serve affinché l'agente generi un file `README.md` che documenta il sito web.
- **Animazione**: Fornisci al modello il prompt `Add an animation that visually represents a large language model running on a laptop.` per aggiungere un'animazione al sito web.

Incoraggiamo il lettore a provare a generare altre applicazioni con questa configurazione. Di seguito alcuni esempi divertenti che abbiamo provato:

- **Giochi Arcade Retrò**: Prova altri prompt. Può essere divertente far creare all'agente giochi in stile retrò in Python usando il pacchetto `PyGame` con il seguente prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Analisi dei Dati**: Un'area in cui gli agenti di codifica sono particolarmente utili è quella degli script e dell'analisi dei dati. Questo è un prompt per mostrare la capacità del modello locale di generare software di analisi dei dati per la visualizzazione dei prezzi azionari:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Risorse

Di seguito alcune risorse aggiuntive per saperne di più sugli agenti di codifica, Cline e l'esecuzione di carichi di lavoro su

* Ulteriori informazioni sulla partnership e l'integrazione AMD LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD che illustra come eseguire Cline su AMD Ryzen™ AI e Radeon™ Graphics Cards: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog di Cline sull'esecuzione di agenti di codifica locali su AI PC: https://cline.bot/blog/local-models-amd