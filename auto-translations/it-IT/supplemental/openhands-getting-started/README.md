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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Panoramica

[OpenHands](https://github.com/All-Hands-AI/OpenHands) è un agente software AI
in grado di scrivere codice, eseguire comandi, navigare sul web e modificare
file in un workspace reale. Invece di copiare i suggerimenti da una finestra di
chat, si indirizza l'agente verso una cartella di progetto e lo si lascia fare
il lavoro: implementare una funzionalità, correggere un bug, scrivere test o
spiegare una codebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) è l'interfaccia
browser consigliata per eseguire OpenHands. Un singolo comando `agent-canvas`
avvia insieme il server dell'agente, il backend di automazione e il frontend
web, consentendo di gestire una conversazione con l'agente direttamente dal
browser.

Per mantenere tutto sul sistema AMD, l'agente comunica con un modello locale
servito da Lemonade Server. Lemonade espone tale modello tramite un'API
compatibile con OpenAI, quindi Agent Canvas può configurarlo come qualsiasi
altro endpoint in stile OpenAI, mentre il modello, il codice e il contesto
della conversazione rimangono tutti sulla macchina.

In questo playbook, avvierai un modello locale, lancerai Agent Canvas, lo
punterai verso quel modello ed eseguirai il tuo primo task di programmazione su
una cartella di progetto reale.

## Cosa imparerai

- Come avviare Lemonade Server e verificare che un modello locale risponda alle
  richieste di chat
- Come installare e avviare Agent Canvas dal pacchetto npm
- Come configurare Agent Canvas per utilizzare un modello Lemonade locale come
  LLM
- Come avviare una conversazione OpenHands e osservare l'agente modificare file
  ed eseguire comandi in un workspace
- Come esaminare le modifiche apportate dall'agente e indirizzarlo con
  messaggi di follow-up

## Concetti principali

| Concetto | Cos'è | Dove si inserisce in questo playbook |
| --- | --- | --- |
| Lemonade Server | Una piattaforma locale di serving per LLM realizzata per hardware AMD, che espone un'API compatibile con OpenAI. I tuoi dati non lasciano mai la tua macchina. | Esegue il modello che alimenta l'agente. |
| OpenHands | Un agente software AI che legge e modifica file, esegue comandi shell e naviga sul web all'interno di un workspace. | L'agente che si guida dalla chat. |
| Agent Canvas | L'interfaccia browser e il backend che eseguono le conversazioni OpenHands e mostrano le chiamate agli strumenti e le modifiche ai file. | Avvia lo stack e ospita la conversazione. |
| Workspace | La cartella di progetto che l'agente è autorizzato a leggere e modificare. | L'oggetto delle modifiche e dei comandi dell'agente. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> I flussi di lavoro con agenti di coding traggono vantaggio da un modello e da
> una finestra di contesto più grandi. Utilizza almeno 32 GB di memoria di
> sistema e preferisci 64 GB o più per i modelli GGUF più grandi.
<!-- @device:end -->

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Prerequisiti


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

È necessario:

- Lemonade Server installato e in grado di servire il modello sottostante.

<!-- @os:linux -->
- Node.js 22.12 o versione successiva e `npm` (utilizzati dalla CLI
  `agent-canvas`).
- `uv`, il gestore di pacchetti Python utilizzato da Agent Canvas per gestire
  l'ambiente del server dell'agente. Se il sistema non lo possiede già,
  installalo seguendo la [guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/)
  prima di avviare Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installato e in esecuzione. Su Windows, lo stack di Agent Canvas viene
  eseguito dall'immagine Docker pubblicata, che include Node.js, `uv` e il
  pacchetto `@openhands/agent-canvas`, quindi non è necessario installarli
  sull'host.
<!-- @os:end -->

- Una cartella di progetto su cui lavorare. Può essere qualsiasi repository
  git locale o directory di codice su cui desideri che l'agente lavori.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Avviare Lemonade Server

Avvia il modello dalla CLI di Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Scegli un modello adatto al tuo hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) è un modello di coding potente ma richiede un ampio pool di memoria. Se il tuo dispositivo ha memoria o VRAM GPU limitate, scegli invece un modello GGUF più piccolo dalla libreria di modelli Lemonade e utilizza quell'ID modello in tutto il playbook.

> **Nota:** Il primo `lemonade run` scarica il modello se non è già presente, operazione che può richiedere del tempo a seconda delle dimensioni del modello e della connessione.

Lemonade espone un'API compatibile con OpenAI all'indirizzo:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verificare il modello locale

Conferma che Lemonade possa servire il modello selezionato:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Quindi invia una piccola richiesta di chat:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. Installare e avviare Agent Canvas

<!-- @os:linux -->
Installa globalmente il pacchetto pubblicato di Agent Canvas:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Poi avvia l'intero stack da un terminale:

```bash
agent-canvas
```

Per impostazione predefinita, Agent Canvas si avvia su `http://localhost:8000`. Apri quell'URL nel
tuo browser. La porta non è speciale: se 8000 è già in uso, passa una
porta libera qualsiasi con `--port` (o `-p`) quando avvii Agent Canvas:

```bash
agent-canvas --port 3000
```

Quindi apri `http://localhost:3000` invece. Il backend locale predefinito dovrebbe apparire
come integro nella schermata iniziale.

Il comando `agent-canvas` avvia insieme il server dell'agente, il backend di automazione e
il frontend web. Ti serve solo questo comando per eseguire OpenHands
in locale.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Su Windows, esegui l'immagine container pubblicata di Agent Canvas con Docker Desktop.
L'immagine include il Server Agente, il backend di automazione e il frontend web, quindi
non è necessario installare Node.js, `uv` o la CLI sull'host.

Per prima cosa, crea le cartelle di configurazione e workspace che il container monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Scarica l'immagine pubblicata (è pubblica, quindi non è richiesto alcun login):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Poi avvia lo stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Apri `http://localhost:8000/canvas` nel tuo browser. Se la porta 8000 è già in
uso, mappa una porta host diversa, ad esempio `-p 8080:8000`, e apri
`http://localhost:8080/canvas` invece.

> **Nota:** Il primo avvio inizializza il Server Agente all'interno del container,
> quindi potrebbe volerci un minuto o due prima che il backend risulti integro.

Il mount `.openhands` mantiene il tuo profilo LLM e le impostazioni tra i riavvii
del container. Il resto di questa guida configura tutto tramite l'interfaccia di Agent
Canvas nel tuo browser.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Configurare l'LLM locale

Al primo avvio, Agent Canvas apre un flusso di onboarding. In quel flusso:

1. Mantieni **OpenHands** selezionato come agente e fai clic su **Next**.
2. In **Set up your LLM**, seleziona **Advanced**.
3. Mantieni **Authentication** impostato su **API key**.
4. Imposta **Custom Model** su `openai/Qwen3.6-35B-A3B-GGUF`.
5. Imposta **Base URL** su `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Su Windows lo stack viene eseguito in un container, che non può raggiungere l'host su
   > `127.0.0.1`. Usa invece `http://host.docker.internal:13305/api/v1` in modo che
   > l'agente containerizzato possa raggiungere Lemonade in esecuzione sull'host Windows.
   <!-- @os:end -->
6. Per **API Key**, inserisci un segnaposto non vuoto qualsiasi, come `lemonade-local`.
   Lemonade non richiede una chiave reale, ma il client OpenHands ha bisogno di un valore
   da inviare.
7. Fai clic su **Next**.

Le impostazioni Advanced completate dovrebbero avere questo aspetto. Il campo della chiave API è
mascherato dall'interfaccia.

![Impostazioni avanzate LLM al primo utilizzo di Agent Canvas con il modello Lemonade e l'URL base locale](assets/01-llm-advanced-settings.png)

Agent Canvas salva questi valori come profilo LLM. Se la tua versione ti chiede di
assegnare un nome a quel profilo, usa un nome senza spazi come `lemonade-local`. Se cambi
modello in seguito, apri **Settings > LLM** e aggiorna gli stessi campi Advanced. Puoi
passare da un profilo salvato all'altro dalla casella di chat con il comando `/model`.

## 5. Aprire un Workspace

L'agente può leggere e modificare solo i file all'interno di un workspace che scegli. Prima di
avviare un'attività, indica ad Agent Canvas la tua cartella di progetto:

1. Dalla schermata iniziale, scegli **Open Workspace**.
2. Seleziona la cartella che contiene il tuo progetto (ad esempio, un repository git
   su cui vuoi che l'agente lavori).
3. Avvia una nuova conversazione in quel workspace.

Tutto ciò che l'agente fa — leggere file, eseguire comandi, modificare codice — è
limitato a quel workspace.

![Schermata iniziale di Agent Canvas dopo l'onboarding](assets/02-agent-canvas-home.png)

## 6. Eseguire la prima attività di codifica

Con il workspace aperto e l'LLM locale selezionato, digita un'attività concreta nella
chat. Una buona prima attività è piccola e verificabile, ad esempio:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Osserva la sequenza temporale della conversazione. OpenHands:

- Leggerà il workspace per comprendere la struttura.
- Creerà `hello.py` con la funzione richiesta e il blocco di test.
- Eventualmente eseguirà `python3 hello.py` per verificare l'output.
- Riporterà in chat cosa ha fatto e l'eventuale output dei comandi.

Dovresti vedere comparire il nuovo file nel workspace, e il messaggio finale dell'agente
dovrebbe descrivere la modifica apportata. Questo è il momento clou: l'agente
ha scritto ed eseguito codice reale nella cartella del tuo progetto.

## 7. Rivedere e guidare l'agente

Dopo che l'agente ha completato un passaggio, rivedi il suo lavoro prima di accettare quello successivo:

- **Modifiche ai file**: usa il browser dei file del workspace o la vista diff dell'agente per
  vedere esattamente cosa è stato aggiunto, modificato o eliminato.
- **Output dei comandi**: espandi qualsiasi comando eseguito dall'agente per vedere stdout, stderr
  e il codice di uscita.
- **Follow-up**: se il risultato non è quello desiderato, rispondi nella stessa
  conversazione con una correzione. L'agente mantiene il contesto precedente e
  itera sugli stessi file.

Ad esempio, se il test non ha stampato il saluto atteso, rispondi:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

L'agente rileggerà il file, eseguirà il comando, diagnosticherà il problema e modificherà
di nuovo il file — tutto nella stessa conversazione.
## Risoluzione dei problemi

<!-- @os:linux -->
- **`agent-canvas` non è presente in PATH:** reinstallare con
  `npm install -g @openhands/agent-canvas` e verificare che la directory
  binaria globale di npm sia presente in PATH prima di poter avviare
  `agent-canvas` da un nuovo terminale.
- **`npm install -g` non riesce con un errore di autorizzazioni:** configurare
  una directory globale npm di proprietà dell'utente, quindi riaprire il
  terminale e installare nuovamente Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` non è presente:** installarlo seguendo
  [la guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas utilizza `uv` per gestire l'ambiente Python del server dell'agente.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` o `docker run` non riesce a connettersi:** assicurarsi che
  Docker Desktop sia in esecuzione (la sua icona a forma di balena si trova
  nella barra delle applicazioni) e che il motore abbia terminato l'avvio.
  `docker version` dovrebbe stampare sia una sezione Client che una sezione Server.
- **Il container si avvia ma il backend non diventa mai integro:** il primo
  avvio inizializza l'Agent Server all'interno del container; attendere uno o
  due minuti, quindi controllare `docker logs <container>` per eventuali errori.
- **Il container non riesce a raggiungere Lemonade:** il container raggiunge
  l'host tramite `host.docker.internal`. Verificare che Lemonade sia in
  esecuzione sull'host Windows con `lemonade status` e utilizzare
  `http://host.docker.internal:13305/api/v1` come Base URL durante la
  configurazione dell'LLM.
<!-- @os:end -->

- **L'interfaccia utente si carica ma il backend risulta non integro:**
  attendere uno o due minuti affinché il server dell'agente termini l'avvio,
  quindi aggiornare la pagina. Se continua a risultare non integro, riavviare
  lo stack e controllare i log per eventuali errori.
- **Le richieste di chat a Lemonade falliscono con un errore di connessione:**
  verificare che `curl -fsS "http://127.0.0.1:13305/api/v1/health"` vada a
  buon fine e che Lemonade stia ancora servendo il modello con `lemonade status`.
- **L'agente restituisce un errore relativo alla lunghezza del contesto o al
  limite di token:** avviare una nuova conversazione in modo che l'agente non
  porti con sé una cronologia eccessiva. Se il problema persiste, riavviare
  Lemonade con un `ctx_size` maggiore rispetto al valore predefinito di 65536
  (ad esempio `ctx_size=131072`), compatibilmente con la memoria disponibile.
- **L'agente produce modifiche di scarsa qualità o incomplete:** passare a un
  modello più grande in Lemonade, oppure assegnare all'agente un'attività più
  piccola e concreta, lasciandola completare prima di richiedere la modifica
  successiva.

## Passaggi successivi

- Provare un'attività più complessa nello stesso workspace, ad esempio
  aggiungendo un file di unit test o risolvendo un bug noto, e rivedere il
  diff prodotto dall'agente prima di mantenere la modifica.
- Collegare un server MCP come GitHub o Slack in **Customize**, in modo che
  l'agente possa leggere le issue o pubblicare aggiornamenti mentre lavora.
- Salvare più profili LLM (un modello piccolo e veloce e un modello più grande
  e potente) e passare dall'uno all'altro con `/model` durante la conversazione.
- Passare a [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) per
  trasformare i cicli di sviluppo ricorrenti in esecuzioni dell'agente
  pianificate o attivate da eventi.

## Risorse

- [Documentazione OpenHands](https://docs.openhands.dev/)
- [Panoramica di Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configurazione di Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profili LLM e configurazione dei modelli](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentazione di Lemonade Server](https://lemonade-server.ai/docs)

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