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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Questo playbook richiede un minimo di **32GB** di memoria di sistema.
<!-- @device:end -->

## Panoramica

Gli agenti di programmazione sono strumenti potenti che permettono agli sviluppatori di collaborare con agenti AI basati su Large Language Model (LLM). Possono essere integrati nell'ambiente di sviluppo, come il terminale o VS Code, consentendo un'integrazione fluida nel flusso di lavoro dello sviluppatore.

Questo tutorial mostra come utilizzare Cline, VS Code e LM Studio per eseguire un agente di programmazione interamente sulla propria macchina locale.

## Cosa Imparerai

* Come eseguire VS Code con l'agente di programmazione Cline per assistere nelle attività di ingegneria del software.
* Come configurare Cline per comunicare con LM Studio per l'inferenza locale degli agenti di programmazione.
* Come utilizzare gli agenti di programmazione locali per risolvere problemi reali di ingegneria del software. 

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software
> **Nota**: Se VS Code non è installato, è possibile installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

<!-- @require:lmstudio,vscode -->

## Avvio e Configurazione di LM Studio

Utilizzeremo LM Studio per servire l'LLM che alimenta l'agente di programmazione.

- Nella barra di ricerca, cerca `LM Studio` e avvia l'applicazione. Ti verrà mostrata la seguente pagina.

![Schermata iniziale di LM Studio](assets/initial-lm-studio.png)

Successivamente, dobbiamo caricare l'LLM sul sistema. Utilizzeremo il modello `Qwen3-Coder-30B-A3B` con una lunghezza di contesto elevata. (Utilizza la scheda Model per installarlo se non l'hai già fatto).
- Fai clic sulla barra di ricerca nella parte superiore della finestra di LM Studio oppure premi `CTRL+L`. Fai clic sull'interruttore `Manually choose model load parameters` e poi fai clic sul modello Qwen3-Coder-30B-A3B.
- Cambia la lunghezza del contesto da `4096` a `32768` e assicurati che `GPU Offload` sia al massimo. Poi, fai clic su `Load Model`

![Selezione del modello](assets/model-list-zoomed.png)

Utilizziamo una lunghezza di contesto elevata in modo che l'agente possa elaborare codebase di grandi dimensioni e ricordare le modifiche apportate.

![Configurazione del modello](assets/selecting-model-zoomed.png)

Successivamente, dobbiamo abilitare il Server di LM Studio. 
- Fai clic sulla scheda Developer o premi `CTRL+2` in LM Studio a sinistra.
- Verifica l'interruttore di stato e assicurati che sia impostato su `Running`.

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
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Avvio e Configurazione di VS Code

Installeremo l'estensione Cline in VS Code e la collegheremo al server LM Studio appena creato.
- Nella barra di ricerca, cerca `VS Code` e avvia l'applicazione.
- Fai clic sull'icona `Extensions` nella colonna sinistra di VS Code e cerca `Cline`. Poi, fai clic sul pulsante `Install`. 

![Installazione dell'estensione Cline](assets/installing-cline-vscode-extension.png)

- Dovrebbe comparire un'icona di Cline sulla sinistra. Fai clic su di essa per aprire Cline. Comparirà una finestra che chiede `How will you use Cline?` Poiché utilizzeremo un LLM locale in esecuzione tramite LM Studio, seleziona `Bring my own API Key` e premi `Continue`. 

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

![Creazione dell'account](assets/cline-how-will-you-use-cline-zoomed.png)

Successivamente, dobbiamo configurare Cline per comunicare con il server LM Studio che abbiamo appena impostato. 
- Imposta l'API Provider su `LM Studio` e il modello su `Qwen3-Coder-30B-A3B-GGUF`. 

>**Suggerimento**: Potrebbero essere disponibili modelli più recenti. Valuta di scaricare e passare ai modelli Qwen3.6 se lo desideri.


![Configurazione del modello](assets/cline-model-configuration-zoomed.png)

## Creazione del tuo primo progetto

Utilizziamo il nostro agente locale per creare un sito web! Apri VSCode in una directory a tua scelta dove Cline creerà i file.
- Per farlo, vai su `File -> Open Folder` nella parte superiore sinistra di VS Code e scegli una cartella come `Documents`.

![Cartella vuota in VS Code](assets/open-cline-test.png)

Ora siamo pronti a fornire un prompt all'agente di programmazione locale. 
- Fai clic sull'estensione Cline nella colonna sinistra e inserisci un prompt per avviare l'agente. Ad esempio, utilizziamo il seguente prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

L'agente inizierà quindi a creare file in base al prompt. Come utente, puoi osservare la generazione del codice in VS Code come mostrato di seguito. Potrebbe essere necessario fare clic su `Save` ogni volta che Cline vuole creare un file. 

![Generazione del codice con Cline](assets/cline-code-generation.png)

Dopo aver generato il software, l'agente ha completato il compito ed è possibile eseguire l'applicazione. In questo caso, l'agente ha scritto tre file: `index.html`, `script.js` e `styles.css`. Facendo semplicemente doppio clic sul file HTML possiamo caricare e interagire con il sito web generato.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
## Prossimi Passi

Dopo aver generato il sito web, puoi continuare a lavorare con Cline per migliorarlo. Due possibili miglioramenti sono:

- **Documentazione**: Richiedere all'agente `Add a README` è tutto ciò che serve affinché l'agente generi un file `README.md` che documenti il sito web.
- **Animazione**: Richiedi al modello `Add an animation that visually represents a large language model running on a laptop.` per generare un'animazione da aggiungere al sito web.

Incoraggiamo il lettore a provare a generare altre applicazioni utilizzando questa configurazione. Di seguito sono riportati alcuni esempi divertenti che abbiamo provato:

- **Giochi Arcade Retrò**: Prova altri prompt. Può anche essere divertente far creare all'agente giochi in stile retrò in Python utilizzando il pacchetto `PyGame` con il seguente prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Analisi dei Dati**: Un'area in cui gli agenti di coding sono particolarmente utili è quella dello scripting e dell'analisi dei dati. Questo è un prompt per mostrare la capacità del modello locale di generare software di analisi dati per la visualizzazione dei prezzi azionari:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Risorse

Di seguito sono riportate alcune risorse aggiuntive per saperne di più sugli Agenti di Coding, Cline e sull'esecuzione di carichi di lavoro su 

* Maggiori informazioni sulla partnership e integrazione tra AMD e LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog di AMD che illustra come eseguire Cline su schede AMD Ryzen™ AI e Radeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog di Cline sull'esecuzione locale di agenti di coding su AI PC: https://cline.bot/blog/local-models-amd