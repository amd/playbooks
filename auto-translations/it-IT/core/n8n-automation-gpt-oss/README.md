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

## Panoramica

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Questo playbook richiede un minimo di **32GB** di memoria di sistema.
<!-- @device:end -->

n8n è una piattaforma di automazione dei flussi di lavoro che consente di collegare app e servizi utilizzando un editor visivo basato su nodi.

Questo playbook illustra come configurare un riepilogatore di notizie finanziarie basato sull'IA che estrae dati dalla sezione business di AP News, ne ricava i titoli principali e utilizza un LLM locale in esecuzione sul proprio sistema per generare un riepilogo orientato agli investitori.

## Cosa imparerai

- Come installare e avviare n8n
- Importare e configurare un flusso di lavoro predefinito
- Connettersi a Lemonade utilizzando l'integrazione nativa di n8n
- Comprendere i nodi del flusso di lavoro e il flusso dei dati

## Cos'è Lemonade?

[Lemonade](https://lemonade-server.ai) è una piattaforma di servizio LLM locale creata per hardware AMD. Fornisce un'API compatibile con OpenAI che viene eseguita interamente sulla propria macchina: i dati non lasciano mai il dispositivo.

In questo playbook, utilizziamo Lemonade per servire un LLM locale a cui n8n si connette per eseguire attività basate sull'IA.

n8n include un **nodo Lemonade nativo** (`Lemonade Chat Model`) che offre un'integrazione di prima classe, senza bisogno di configurazione manuale. Questo rende semplice collegare il proprio LLM locale ai flussi di lavoro di automazione.

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Installazione di n8n
<!-- @os:windows -->
Installa n8n a livello globale utilizzando npm.

> **Nota**: potresti visualizzare alcuni avvisi npm. Questo è normale.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Suggerimento**: gli utenti Windows potrebbero dover modificare i criteri di esecuzione di PowerShell (ad esempio,
> impostandolo su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi di PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problema di PATH**: se `n8n --version` restituisce comando non trovato, assicurati che la directory bin globale di npm sia inclusa nel `PATH` utente. Il percorso di installazione predefinito è `C:\Users\<username>\AppData\Roaming\npm`. 
> Aggiungilo al percorso utente (Modifica le variabili di ambiente di sistema > Variabili di ambiente > Modifica percorso utente) e ricarica il terminale. 

<!-- @os:end -->

<!-- @os:linux -->
Utilizzeremo ora il servizio Podman per containerizzare la nostra installazione di n8n.

Scarica quanto segue in una directory a tua scelta: [compose.yml](assets/compose.yml)

In quella directory, esegui il seguente comando:
```bash
podman compose up -d
```

Questo dovrebbe installare n8n e scrivere su uno storage persistente.

Avvia n8n digitando `localhost:5678` nella barra degli indirizzi del browser.
<!-- @os:end -->

<!-- @os:windows -->
## Avvio di n8n

Avvia n8n dal terminale:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n avvia un server web locale. Premi `'o'` oppure apri il browser su `http://localhost:5678` per accedere all'editor.
<!-- @os:end -->


> **Suggerimento**: mantieni aperta la finestra del terminale mentre utilizzi n8n. Chiuderla potrebbe interrompere il server.

## Avvio di Lemonade

Lemonade è il server locale che eseguirà un modello e si collegherà a n8n. 

<!-- @os:linux -->
Apri la GUI di Lemonade facendo clic sull'icona di Lemonade nella barra delle applicazioni. Da qui puoi sfogliare modelli, backend e caricare i modelli preinstallati.
<!-- @os:end -->

<!-- @os:windows -->
Apri la GUI di Lemonade facendo clic sull'icona di Lemonade. Fai clic con il tasto destro sull'icona nella barra delle applicazioni per aprire l'app. Quindi, puoi aggiungere modelli, backend e caricare i modelli preinstallati.
<!-- @os:end -->

>**Suggerimento**: una volta avviata, la GUI di Lemonade è accessibile anche all'indirizzo http://localhost:13305

In alternativa, puoi aprire un terminale ed eseguire `lemonade list` per vedere quali modelli sono installati. Quindi, esegui:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Configurazione del flusso di lavoro

### Passaggio 1: registrati o accedi a n8n

Quando apri n8n per la prima volta, ti verrà chiesto di creare un account o di accedere:

1. Apri `http://localhost:5678` nel tuo browser
2. Crea un nuovo account locale con la tua email, oppure accedi se ne hai già uno
3. Una volta effettuato l'accesso, vedrai la dashboard di n8n

> **Suggerimento**: se resti bloccato fuori dal tuo account, prova `n8n user-management:reset`

### Passaggio 2: importa il flusso di lavoro

Abbiamo fornito un flusso di lavoro predefinito che puoi importare direttamente:

1. Scarica il seguente file del flusso di lavoro: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Fai clic su **Start from Scratch** per aprire l'editor del flusso di lavoro. In alternativa, fai clic sul pulsante + in alto a sinistra, quindi su **Add workflow**.
3. Fai clic sul menu **...** (tre puntini) nella barra in alto a destra e seleziona **Import from file**
4. Seleziona il file `financial-news-workflow.json` scaricato
5. Il flusso di lavoro apparirà sull'area di lavoro
### Passaggio 3: Comprendere il workflow

Il workflow importato contiene 9 nodi collegati:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nodo | Scopo |
|------|---------|
| **When clicking 'Execute workflow'** | Trigger manuale per avviare il workflow |
| **Fetch Financial News Webpage** | Richiesta HTTP GET a `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Nodo Wait per garantire che il contenuto della pagina sia completamente caricato |
| **Extract News Headlines & Text** | Nodo HTML che estrae titoli, articoli selezionati dalla redazione, notizie principali e notizie regionali utilizzando selettori CSS |
| **Clean Extracted News Data** | Nodo Set che combina tutti i dati estratti in un unico campo di testo |
| **AI Financial News Summarizer** | AI Agent che elabora le notizie con un prompt di sistema da analista finanziario |
| **Lemonade Chat Model** | Si connette al server Lemonade locale su cui è in esecuzione l'LLM |
| **Structured Output Parser** | Formatta l'output dell'AI come JSON strutturato |
| **Convert to File** | Converte il riepilogo in un file scaricabile |

### Passaggio 4: Configurare le credenziali Lemonade

Prima di eseguire il workflow, è necessario collegarlo al server Lemonade locale:

1. Fai doppio clic sul nodo **Lemonade Chat Model** in n8n
2. Nel menu a tendina **Credential to connect with** seleziona **Create New Credential**
3. Inserisci i valori nella tabella sottostante e fai clic su save.
4. Scegli il modello pertinente che hai caricato in Lemonade Server.

  | Campo | Valore |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Nota**: Prima di eseguire il test, esegui `lemonade status` in un terminale per confermare che il server Lemonade sia in esecuzione.
<!-- @device:halo_box -->
> Questo workflow utilizza GPT-OSS-120B, preinstallato in Lemonade. Puoi cambiarlo con altri modelli caricati nelle impostazioni del nodo Lemonade Chat Model.
<!-- @device:end -->

### Passaggio 5: Testare il workflow

1. Assicurati che Lemonade sia in esecuzione con un modello caricato
2. Fai clic su **Execute workflow** nella parte inferiore centrale del canvas
3. Osserva l'esecuzione di ogni nodo da sinistra a destra: diventano verdi al completamento
4. Fai doppio clic sul nodo **AI Financial News Summarizer** per vedere il riepilogo generato nel pannello inferiore.
5. Fai doppio clic sul nodo **Convert to File** per scaricare il file di testo corrispondente nel pannello inferiore.

## Comprendere l'AI Agent

L'AI Financial News Summarizer utilizza un prompt di sistema progettato per l'analisi finanziaria:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

L'agente riceve i dati puliti delle notizie e restituisce un riepilogo strutturato con il sentiment di mercato.

### Salvare il workflow

Fai clic sul nome del workflow in alto e rinominalo se lo desideri. I workflow vengono salvati automaticamente durante il lavoro.

## Prossimi passi

- **Pianifica l'automazione**: Sostituisci il Manual Trigger con uno **Schedule Trigger** per l'esecuzione giornaliera
- **Invia notifiche**: Aggiungi un nodo **Discord**, **Slack** o **Email** per ricevere i riepiloghi
- **Prova modelli diversi**: Cambia il modello nel nodo Lemonade Chat Model per sperimentare con diversi LLM
- **Personalizza l'estrazione**: Modifica i selettori CSS del nodo HTML Extract per mirare a diverse sezioni di notizie
- **Prova backend diversi**: n8n supporta anche [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio e altri backend LLM locali

### Esplora i modelli n8n

n8n dispone di centinaia di modelli di workflow predefiniti. Sfoglia la libreria ufficiale di modelli su:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Cerca "AI", "LLM" o "automation" per trovare workflow che puoi importare e personalizzare.

Per maggiori informazioni, consulta la [Documentazione n8n](https://docs.n8n.io/).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->