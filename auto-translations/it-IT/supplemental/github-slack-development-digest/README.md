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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Panoramica

Gli sviluppatori dedicano molto tempo a piccoli cicli ricorrenti: revisionare pull request etichettate, rispondere ai commenti su GitHub, smistare nuovi issue, trasformare i thread di Slack in note di standup o follow-up di incidenti, e tenere traccia di segnali di release o ricerca.
Ogni ciclo è familiare, ma richiede comunque giudizio: raccogliere il contesto giusto, decidere cosa conta e pubblicare un aggiornamento chiaro dove il team già lavora.

Le [automazioni OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) trasformano questi cicli in conversazioni agent pianificate o attivate da eventi: esecuzioni in cui un agente software AI può leggere il contesto, chiamare strumenti e produrre un aggiornamento.
I modelli di automazione condivisi nel catalogo delle estensioni OpenHands seguono questo schema per la revisione delle pull request GitHub, il monitoraggio dei repository, il triage degli issue Linear, i retrospettive sugli incidenti, i digest di standup Slack e i brief di ricerca: un'automazione si attiva, utilizza integrazioni configurate come GitHub o Slack per recuperare il contesto, ragiona su quel contesto con un large language model (LLM) e scrive un risultato.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) è il piano di controllo locale per creare e testare queste automazioni.
In questo playbook esegue un OpenHands Agent Server, il processo backend che esegue le conversazioni agent, e collega l'agente a servizi esterni come GitHub e Slack.

Per mantenere il flusso di lavoro sul tuo sistema AMD, l'agente comunica con un modello locale servito da Lemonade Server.
Lemonade espone quel modello tramite un'API compatibile con OpenAI, così Agent Canvas può configurarlo come un endpoint remoto in stile OpenAI, mentre il modello, il prompt e il contesto del flusso di lavoro rimangono locali.

In questo playbook, costruirai un'automazione concreta: un digest di sviluppo pianificato da GitHub a Slack.
Utilizza GitHub per ispezionare l'attività recente del repository, Slack per pubblicare il digest, chiamate API di Agent Canvas per configurare e testare l'automazione, e Lemonade per eseguire l'LLM localmente.

![Diagramma dell'architettura che mostra GitHub MCP, automazione OpenHands, Lemonade Server e Slack MCP](assets/00-architecture-overview.png)

## Cosa Imparerai

- Come avviare Lemonade Server e verificare che un modello locale risponda alle richieste di chat
- Come avviare Agent Canvas e puntare il suo Agent Server verso un LLM locale
- Come installare i server GitHub e Slack Model Context Protocol (MCP) tramite l'API dell'Agent Server
- Come creare e avviare un'automazione OpenHands pianificata che pubblica un digest di sviluppo su Slack
- Come risolvere i problemi più comuni relativi ai modelli locali e alle automazioni

## Concetti Fondamentali

| Concetto | Cos'è | Dove si inserisce in questo playbook |
| --- | --- | --- |
| Lemonade Server | Una piattaforma di serving LLM locale costruita per hardware AMD che espone un'API compatibile con OpenAI. I tuoi dati non lasciano mai la tua macchina. | Esegue il modello che alimenta l'agente. |
| OpenHands Agent Server | Il processo backend che esegue le conversazioni agent di OpenHands. | Ospita l'agente, il suo profilo LLM e i suoi server MCP. |
| Agent Canvas | Il piano di controllo locale per OpenHands che esegue Agent Server e una UI per ispezionare le esecuzioni dell'agente. | Avvia i backend e fornisce l'API che chiami. |
| Server MCP | Un server Model Context Protocol che fornisce a un agente strumenti per un servizio esterno come GitHub o Slack. | Permette all'agente di leggere da GitHub e scrivere su Slack. |
| Automazione OpenHands | Una conversazione agent pianificata o attivata da eventi che recupera il contesto, ragiona su di esso e scrive un risultato da qualche parte. | Il digest da GitHub a Slack che costruisci qui. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> I flussi di lavoro degli agenti di coding beneficiano di un modello più grande e di una finestra di contesto più ampia.
> Usa almeno 32 GB di memoria di sistema, e preferisci 64 GB o più per modelli GGUF più grandi.
<!-- @device:end -->

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti del Software

<!-- @require:software-update -->
<!-- @device:end -->

## Prerequisiti

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Hai bisogno di:

- Lemonade Server installato seguendo la [guida all'installazione di Lemonade](https://lemonade-server.ai/docs/guide/install/) standard.

<!-- @os:linux -->
- Node.js 22.12 o successivo e `npm`, usati per installare la CLI pubblicata di Agent Canvas ed eseguire server MCP con `npx`.
- `uv`, il gestore di pacchetti Python che Agent Canvas utilizza per costruire l'ambiente dell'Agent Server. Se non è già installato, installalo dalla [guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/).
- Un pacchetto `@openhands/agent-canvas` pubblicato recentemente con impostazioni agent basate su schema, `LLMSummarizingCondenserSettings.max_tokens` e supporto LLM `custom_tokenizer`.
- Il pacchetto Python `transformers` disponibile nell'ambiente dell'Agent Server. È necessario per il conteggio dei token basato su chat-template quando è impostato `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop per Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installato e in esecuzione. Su Windows, lo stack di Agent Canvas viene eseguito dall'immagine Docker pubblicata, che include Node.js, `uv`, `transformers` e il pacchetto `@openhands/agent-canvas`, quindi non è necessario installarli sull'host.
<!-- @os:end -->

- Un token GitHub con accesso in lettura al repository che vuoi riassumere.
- Un token bot Slack (`xoxb-...`) con accesso in scrittura chat (`chat:write`) e accesso in lettura ai canali.
- Un ID team Slack (`T...`).
- Un ID canale Slack (`C...`) dove dovrebbe essere pubblicato il digest.

Invita l'app Slack nel canale di destinazione prima di testare l'automazione.
## Variabili utilizzate in questo playbook

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Queste due variabili vengono utilizzate dai comandi di verifica riportati di seguito.
Il modello, il tokenizer e le altre impostazioni LLM vengono inseriti direttamente nell'interfaccia utente di Agent Canvas nei passaggi successivi, quindi i loro valori letterali sono mostrati in linea dove necessario.

I seguenti valori vengono inseriti nell'interfaccia utente di Agent Canvas nei passaggi successivi.
Impostali qui in modo da poterli copiare:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Utilizza un valore esplicito `owner/repo` per `GITHUB_REPO_FILTER`.
I caratteri jolly ampi a livello di organizzazione possono restituire un contesto MCP troppo esteso per i modelli locali.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Avviare Lemonade Server

Avvia il modello dalla CLI di Lemonade:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Scegli un modello adatto al tuo hardware.** `Qwen3.6-35B-A3B-GGUF` (circa 20 GB) è un modello valido per questo workflow, ma richiede un ampio pool di memoria.
> Se il tuo dispositivo ha memoria o VRAM GPU limitata, scegli un modello GGUF più piccolo dalla libreria di modelli Lemonade e utilizza quell'ID modello (e il tokenizer corrispondente) in tutto questo playbook.

> **Nota:** il primo `lemonade run` scarica il modello se non è già presente, operazione che può richiedere del tempo a seconda delle dimensioni del modello e della tua connessione.

Lemonade espone un'API compatibile con OpenAI all'indirizzo:

```text
http://127.0.0.1:13305/api/v1
```

Facoltativo: se Agent Canvas o l'automation runner non si trovano sulla stessa macchina, pubblica l'endpoint di Lemonade tramite un tunnel sicuro e utilizza l'URL HTTPS come URL base dell'LLM.
[ngrok](https://ngrok.com/) espone una porta locale su internet tramite un URL HTTPS sicuro; richiede un account ngrok gratuito, e devi sostituire `YOUR_NGROK_DOMAIN.ngrok-free.dev` con il tuo dominio riservato:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificare il modello locale

Conferma che Lemonade possa servire il modello selezionato:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Quindi invia una piccola richiesta di chat:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Quindi invia una piccola richiesta di chat:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Se viene restituito un array `choices`, Lemonade è pronto per Agent Canvas.

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
  "max_tokens": 64
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

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Avviare Agent Canvas

<!-- @os:linux -->
Installa il pacchetto Agent Canvas pubblicato e avvia lo stack completo:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se l'installazione globale di npm non riesce a causa di un errore di autorizzazione, consulta la voce relativa alla risoluzione dei problemi di autorizzazione npm riportata di seguito.

Per impostazione predefinita, Agent Canvas si avvia su `http://localhost:8000`.
Apri quell'URL nel tuo browser.
La porta non è speciale: se la 8000 è già in uso, specifica una porta libera qualsiasi con `--port` (o `-p`).
Il backend locale predefinito dovrebbe apparire come integro nella schermata principale.

> **Nota:** il primo avvio compila l'ambiente Python gestito da `uv` dell'Agent Server, quindi possono essere necessari alcuni minuti prima che il backend risulti integro.

Il comando `agent-canvas` avvia insieme il server degli agenti, il backend di automazione e il frontend web.
Ti serve solo questo comando per eseguire OpenHands localmente.
Il resto di questo playbook configura tutto tramite l'interfaccia utente di Agent Canvas nel tuo browser.
<!-- @os:end -->

<!-- @os:windows -->
Su Windows, esegui l'immagine container di Agent Canvas pubblicata con Docker Desktop.
L'immagine include l'Agent Server, il backend di automazione e il frontend web, quindi non è necessario installare Node.js, `uv` o la CLI sull'host.

Innanzitutto, crea le cartelle di configurazione e workspace montate dal container:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Scarica l'immagine pubblicata (circa 6 GB; è pubblica, quindi non è richiesto alcun login):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Quindi avvia lo stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Apri `http://localhost:8000/canvas` nel tuo browser.
Se la porta 8000 è già in uso, mappa una porta host diversa, ad esempio `-p 8080:8000`, e apri invece `http://localhost:8080/canvas`.

> **Nota:** il primo avvio compila l'ambiente dell'Agent Server all'interno del container, quindi possono essere necessari alcuni minuti prima che il backend risulti integro.

Il mount `.openhands` mantiene persistenti il tuo profilo LLM, i server MCP e le automazioni tra i riavvii del container.
Il resto di questo playbook configura tutto tramite l'interfaccia utente di Agent Canvas nel tuo browser all'indirizzo `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. Configura l'LLM locale nell'interfaccia utente

Al primo avvio, Agent Canvas apre un flusso di onboarding.
In tale flusso:

1. Mantieni **OpenHands** selezionato come agente e fai clic su **Next**.
2. In **Set up your LLM**, seleziona **Advanced**.
3. Mantieni **Authentication** impostato su **API key**.
4. Imposta **Custom Model** su `openai/Qwen3.6-35B-A3B-GGUF`.
5. Imposta **Base URL** su `http://127.0.0.1:13305/api/v1`.
6. Per **API Key**, inserisci un segnaposto non vuoto qualsiasi, ad esempio `lemonade-local`. Lemonade non richiede una chiave reale, ma il client OpenHands necessita di un valore da inviare.

<!-- @os:windows -->
> **Windows (Docker):** l'Agent Server viene eseguito all'interno del container, quindi imposta **Base URL** su `http://host.docker.internal:13305/api/v1` invece di `http://127.0.0.1:13305/api/v1`.
> Dall'interno del container, `127.0.0.1` corrisponde al container stesso; `host.docker.internal` raggiunge Lemonade in esecuzione sull'host Windows, e Docker Desktop fornisce automaticamente quel nome host.
<!-- @os:end -->

I campi di connessione dovrebbero avere questo aspetto.
Il campo della chiave API è mascherato dall'interfaccia utente.

![Impostazioni avanzate LLM al primo utilizzo di Agent Canvas con il modello Lemonade e l'URL base locale](assets/01-llm-advanced-settings.png)

Quindi seleziona **All** e imposta i campi aggiuntivi per il modello locale:

1. Scorri fino a **Custom Tokenizer** e impostalo su `Qwen/Qwen3.6-35B-A3B`.
2. Scorri fino a **LiteLLM Extra Body** e impostalo su `{"enable_thinking": true}`.
3. Fai clic su **Next**.

![Scheda All delle impostazioni LLM al primo utilizzo di Agent Canvas con il tokenizer personalizzato di Qwen](assets/02-llm-all-tokenizer-settings.png)

![Scheda All delle impostazioni LLM al primo utilizzo di Agent Canvas con il corpo extra di LiteLLM configurato](assets/03-llm-all-extra-body-settings.png)

Le impostazioni dell'LLM dovrebbero mostrare:

| Campo | Valore |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Il prefisso `openai/` indica a LiteLLM di utilizzare la formattazione delle richieste compatibile con OpenAI verso l'endpoint Lemonade.
Il tokenizer personalizzato è il tokenizer Hugging Face originale per il modello GGUF; consente a OpenHands di contare gli stessi token del template di chat visti dal server del modello locale.
L'attuale modulo LLM per il primo utilizzo non mostra le impostazioni del condenser.
Se la tua build di Agent Canvas espone in seguito le impostazioni del condenser in **Settings > LLM**, usa `llm_summarizing` e imposta il numero massimo di token al di sotto della finestra di contesto di Lemonade, ad esempio `56000`.

## 5. Installa i server MCP di GitHub e Slack

Nell'interfaccia utente di Agent Canvas, apri **Customize** (oppure **Settings > MCP**) per aggiungere i server MCP che forniscono all'agente gli strumenti per GitHub e Slack.
I valori dei token vengono inviati solo al tuo Agent Server locale e vengono salvati come impostazioni crittografate.

<!-- @os:windows -->
> **Windows (Docker):** i comandi del server MCP `npx` riportati di seguito vengono eseguiti all'interno del container, che include già Node.js, quindi non è necessario installare nulla di aggiuntivo sull'host.
> Poiché `.openhands` è montato, i server MCP e i relativi token persistono tra i riavvii del container.
<!-- @os:end -->

### Server MCP di GitHub

Aggiungi un nuovo server MCP con queste impostazioni:

| Campo | Valore |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = il tuo token GitHub |

Usa un token GitHub con accesso in lettura al repository che desideri riassumere.

### Server MCP di Slack

Aggiungi un secondo server MCP con queste impostazioni:

| Campo | Valore |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = l'ID del tuo canale di digest |

Imposta `SLACK_CHANNEL_IDS` sull'ID del canale di digest (lo stesso valore di `SLACK_DIGEST_CHANNEL`) in modo che l'agente non debba scorrere ogni canale Slack.

Dopo aver aggiunto entrambi i server, usa il pulsante **Test** su ciascuno per confermare che si connetta e pubblicizzi gli strumenti.
Il server GitHub dovrebbe elencare gli strumenti GitHub, e il server Slack dovrebbe elencare gli strumenti Slack.

![Pagina MCP di Agent Canvas con i server GitHub e Slack installati](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Crea l'automazione del digest

Nell'interfaccia utente di Agent Canvas, apri la pagina **Automations** e crea una nuova automazione:

1. Scegli **Create automation** e seleziona il tipo **Prompt preset**.
2. Imposta **Name** su `GitHub Development Digest to Slack`.
3. Imposta **Prompt** sul testo seguente, sostituendo i segnaposto del repository e del canale con i tuoi valori:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Imposta **Trigger** su **Cron** con la pianificazione `0 9 * * 1-5` (ore 9 nei giorni feriali) e imposta **Timezone** sul tuo fuso orario, ad esempio `America/New_York`.
5. Imposta **Timeout** su `900` secondi.
6. Salva l'automazione.

La pagina dei dettagli dell'automazione mostra la nuova automazione con il suo trigger cron e l'entrypoint prompt-preset generato.

![Dettaglio dell'automazione di Agent Canvas dopo la creazione](assets/05-automation-created.png)
## 7. Testare l'automazione

Dalla pagina dei dettagli dell'automazione nell'interfaccia utente di Agent Canvas:

1. Fai clic su **Run now** (o **Dispatch**) per eseguire immediatamente l'automazione una volta.
2. Osserva l'elenco delle esecuzioni nella stessa pagina. L'ultima esecuzione dovrebbe passare allo stato `COMPLETED`.
3. Apri il tuo canale Slack di destinazione. Dovrebbe contenere il digest generato.

Non è necessario attendere l'attivazione della pianificazione cron: **Run now** attiva un'esecuzione su richiesta, così puoi verificare che il prompt, le connessioni MCP e la pubblicazione su Slack funzionino tutti correttamente prima di affidarti alla pianificazione.

![Esecuzione dell'automazione di Agent Canvas completata con successo](assets/06-automation-run-completed.png)

![Canale Slack che mostra il digest OpenHands generato](assets/07-slackbot-message.png)

## Risoluzione dei problemi

<!-- @os:windows -->
- **La porta 8000 di Docker è già in uso:** mappa una porta host diversa, ad esempio `docker run ... -p 8080:8000 ...`, e apri `http://localhost:8080/canvas`.
- **`docker pull` non riesce con un errore di credenziali** (ad esempio, "A specified logon session does not exist"): esegui il pull da una sessione Windows interattiva, oppure effettua un pre-pull dell'immagine. L'immagine è pubblica, quindi non è richiesto alcun `docker login`.
- **L'interfaccia utente si carica ma il backend non è integro:** il primo avvio compila l'ambiente di Agent Server all'interno del container. Attendi un minuto e aggiorna la pagina, quindi controlla `docker logs <container>` per verificare l'avanzamento.
- **Agent Canvas non riesce a raggiungere Lemonade dal container:** imposta il **Base URL** dell'LLM su `http://host.docker.internal:13305/api/v1` (non `127.0.0.1`), e verifica che Lemonade sia in esecuzione sull'host Windows.
<!-- @os:end -->

- **Lemonade non è attivo:** riavvialo con il comando `lemonade run "${LEMONADE_MODEL}"` indicato al passaggio 1, quindi ripeti il controllo dello stato di salute.
- **`npm install -g` non riesce con un errore di autorizzazioni:** su Linux o WSL, configura una directory npm globale di proprietà dell'utente, aggiungila al file di avvio della tua shell, quindi installa nuovamente Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Se utilizzi `zsh`, aggiungi la stessa riga `export PATH=...` a `~/.zshrc` anziché a `~/.bashrc`.
- **Agent Canvas rifiuta le impostazioni LLM dopo aver impostato `custom_tokenizer`:** installa `transformers` nell'ambiente Python di Agent Server, riavvia Agent Canvas se necessario e riprova a salvare le impostazioni LLM. OpenHands richiede Transformers per caricare il modello di chat del tokenizer quando è impostato `custom_tokenizer`.
- **Agent Canvas non riesce a raggiungere Lemonade:** verifica `curl -fsS "${LEMONADE_BASE_URL}/health"` e conferma che l'URL di base inserito nel modulo LLM al primo utilizzo o in **Settings > LLM** corrisponda all'endpoint locale in esecuzione o al tunnel HTTPS.
- **Le impostazioni LLM non sono state salvate:** assicurati di aver fatto clic su **Next** dopo aver inserito i valori. Riapri **Settings > LLM** per confermare che i valori siano stati salvati.
- **Il GitHub MCP non riesce a visualizzare i repository privati:** verifica che il token GitHub abbia accesso in lettura al repository di destinazione e che il pulsante **Test** dell'MCP in **Customize** mostri gli strumenti GitHub.
- **Slack riesce a leggere i canali ma non può pubblicare:** invita l'app Slack nel canale di destinazione e conferma che il bot disponga di `chat:write`.
- **L'automazione elenca troppi canali Slack:** utilizza un ID canale Slack e imposta `SLACK_CHANNEL_IDS` sul server MCP di Slack in **Customize**.
- **L'esecuzione dell'automazione non riesce o supera il contesto:** verifica che Lemonade sia stato avviato con `ctx_size=65536`, conferma che l'LLM di OpenHands abbia `custom_tokenizer` impostato, e utilizza un repository esplicito con i set di risultati GitHub limitati a 3-5 elementi. Se la tua build di Agent Canvas espone le impostazioni del condenser, imposta il numero massimo di token del condenser al di sotto della finestra di contesto di Lemonade.

## Passaggi successivi

- Aggiungi un digest settimanale limitato alle release.
- Aggiungi un'automazione attivata da eventi GitHub per avvisi più rapidi su PR o push.
- Instrada lo stesso digest verso Notion, Linear o un altro strumento basato su MCP.

## Risorse

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentazione di Lemonade Server](https://lemonade-server.ai/docs)
- [Repository delle estensioni OpenHands](https://github.com/OpenHands/extensions)
- [Server Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacchetto Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->