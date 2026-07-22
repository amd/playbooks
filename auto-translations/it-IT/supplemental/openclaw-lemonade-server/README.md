<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Esegui OpenClaw con Lemonade Server come backend

## Panoramica

[**OpenClaw**](https://openclaw.ai/) è un agente AI autonomo in grado di scrivere ed eseguire codice, gestire file e portare a termine attività complesse a più fasi per tuo conto. A differenza di un assistente di chat che si limita a rispondere alle domande, OpenClaw esegue azioni reali sul tuo sistema, il che significa che ha bisogno di un backend AI veloce e capace, in grado di stare al passo con un ciclo d'agente impegnativo.

[**Lemonade Server**](https://lemonade-server.ai/) è proprio quel backend. Si tratta di un server di inferenza locale open-source che esegue modelli GenAI direttamente sul tuo hardware ed espone tali modelli tramite l'API OpenAI, ormai standard del settore.

Insieme, i due formano uno stack di agenti AI completamente locale: Lemonade si occupa dell'inferenza del modello, mentre OpenClaw fornisce il ciclo d'agente che trasforma gli output del modello in azioni reali.

> **Prima di continuare:** OpenClaw è un agente AI altamente autonomo. Concedere a qualsiasi agente AI l'accesso al proprio sistema può portare a risultati imprevedibili o non voluti. Procedi solo se comprendi i rischi e ti senti a tuo agio nel far agire software autonomo per tuo conto.

---

## Cosa imparerai

Al termine di questa guida sarai in grado di:

- Conoscere **Lemonade Server**
- **Installare OpenClaw** e **configurarlo per utilizzare Lemonade Server** come backend AI.
- **Avviare il gateway di OpenClaw** e verificare che il tuo agente sia pronto per lavorare.
- **Collegare un canale di comunicazione** (Discord o Telegram) per poter chattare con il tuo agente da qualsiasi dispositivo.

---

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

<!-- @os:linux -->
- Un PC con **Ubuntu 24.04+** o una distribuzione Linux compatibile basata su Debian con `apt-get`
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opzionale, per il sandboxing di OpenClaw)

- **~10–30 GB di spazio libero su disco** per i pesi del modello
<!-- @os:end -->
<!-- @os:windows -->
- Un PC con **Windows 10/11**
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- **~10–30 GB di spazio libero su disco** per i pesi del modello
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opzionale, per il sandboxing di OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Scarica e carica il modello consigliato

Il modello consigliato per questa guida è **Qwen3.6-35B-A3B-GGUF** di Unsloth, un solido modello MoE con una finestra di contesto di 263k token, particolarmente adatto ai carichi di lavoro degli agenti. Questo modello utilizza la quantizzazione UD-Q4_K_XL. Scaricalo ora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Quindi caricalo con una finestra di contesto ampia e salva questa impostazione per le esecuzioni future:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Il modello ha una lunghezza di contesto predefinita di 262.144 token. Se riscontri errori di memoria insufficiente (OOM), valuta di ridurre la finestra di contesto. Tuttavia, poiché Qwen3.6 sfrutta un contesto esteso per attività complesse, si consiglia di mantenere una lunghezza di contesto di almeno 128K token per preservare le capacità di ragionamento.

> **Suggerimento: disabilita la modalità di ragionamento (thinking) per risposte dell'agente più rapide:** Qwen3.6-35B-A3B viene eseguito in modalità di ragionamento per impostazione predefinita, il che aggiunge latenza prima di ogni risposta. Nei cicli d'agente questo overhead si accumula rapidamente. Il repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornisce una configurazione già pronta che disabilita la modalità di ragionamento. Per utilizzarla, scarica il file e importalo:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
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

## Configurazione di WSL

Eseguiamo OpenClaw all'interno di WSL (opzione consigliata) e lo colleghiamo a Lemonade in esecuzione nativa su Windows. Questo ti offre un ambiente shell Linux per OpenClaw, mantenendo al contempo l'accelerazione GPU di Lemonade sul lato Windows.

### Installa WSL e Ubuntu

Apri PowerShell come amministratore e installa il kernel WSL:

```powershell
wsl --install --no-distribution
```

Quindi installa Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Abilita systemd in WSL

Esegui questo comando all'interno del terminale Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Riavvia WSL:

```powershell
wsl --shutdown
wsl
```

### Collega Lemonade da Windows a WSL

WSL2 viene eseguito in una rete virtuale. Lemonade su Windows si associa a `127.0.0.1`, che WSL non è in grado di raggiungere direttamente. Un proxy di porta Windows inoltra il traffico dall'IP del gateway WSL al localhost di Windows.

**Trova l'IP del gateway WSL** (esegui all'interno di WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Aggiungi il proxy di porta** (esegui in PowerShell come amministratore, sostituendo `<WSL-Gateway-IP>` con l'IP del gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Aggiungi una regola del firewall** (stessa PowerShell con privilegi elevati):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifica da WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se hai già caricato il modello Qwen3.6-35B-A3B-GGUF nel passaggio precedente, dovresti vedere un output JSON simile a questo:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> La regola `netsh portproxy` sopravvive ai riavvii, ma l'IP del gateway WSL può cambiare dopo `wsl --shutdown`. Se Lemonade diventa irraggiungibile da WSL dopo un riavvio, recupera l'IP del gateway aggiornato e aggiorna il proxy con questo nuovo IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Installazione e configurazione di OpenClaw

### Installa OpenClaw
<!-- @os:windows -->
> Esegui i comandi di questa sezione all'interno del tuo **terminale WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Il flag `--no-onboard` salta la procedura guidata di configurazione interattiva: configurerai manualmente il backend del modello nel passaggio successivo, il che ti offre un controllo preciso su quale modello e server vengono utilizzati.

Apri un nuovo terminale e conferma l'installazione:

```bash
openclaw --version
```

> **Suggerimento:** se dopo l'installazione visualizzi `command not found`, aggiungi la directory bin globale di npm al tuo PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Per rendere questa modifica permanente, aggiungi la riga precedente al tuo file `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### Configura OpenClaw per Utilizzare Lemonade

Esegui l'onboarding non interattivo di OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Questo comando scrive la configurazione di OpenClaw in `~/.openclaw/openclaw.json`.

> **Dimensionamento della finestra di contesto di OpenClaw:** la compattazione di OpenClaw si attiva quando `contextTokens > contextWindow − reserveTokens`. Il valore predefinito di `reserveTokensFloor` è 20.000 token, una soglia minima che sovrascrive `reserveTokens` quando quest'ultimo è inferiore, quindi qualsiasi contesto del modello inferiore a circa 37k attiverà un ciclo infinito di compattazione. Imposta una riserva bassa e disabilita la soglia una sola volta nella tua configurazione: si applicherà a ogni modello, senza bisogno di regolazioni per singolo modello:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` è una *soglia minima* (una protezione minima), non la riserva stessa: impostare solo la soglia minima non ha alcun effetto. `reserveTokensFloor: 0` disabilita la protezione in modo che il valore più basso di `reserveTokens` venga accettato.
>
> **Quando applicare questa configurazione:** utilizza questa configurazione se la finestra di contesto effettiva del tuo modello è inferiore a circa 37k, sia perché il modello è piccolo (ad es. 8k, 16k, 32k), sia perché hai intenzionalmente limitato il contesto a un valore più basso (ad es. caricando un modello da 128k ma impostando il contesto a 16k in Lemonade). Senza questa configurazione, OpenClaw entra in un ciclo infinito di compattazione all'avvio.
>
> **Modelli a contesto ampio con contesto completo:** puoi saltare completamente questo passaggio. I valori predefiniti funzionano correttamente, la compattazione si attiverà ben prima che la finestra si riempia e il modello avrà ampio spazio per generare risposte lunghe. Se decidi comunque di applicare questa configurazione, tieni presente che `reserveTokens: 4096` limita la lunghezza della risposta a circa 4k token, il che potrebbe troncare la generazione di file lunghi o piani dettagliati.
>
> **Dove aggiungere questa configurazione:** inserisci il blocco `compaction` all'interno di `agents.defaults` nel tuo `openclaw.json` (di solito in `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Il resto della tua configurazione (gateway, canali, modelli, ecc.) rimane invariato: è necessario aggiungere solo la chiave `compaction`.

### (Consigliato) Abilita il Sandboxing Docker

OpenClaw può instradare tutte le operazioni dell'agente su file e codice attraverso un container Docker isolato invece di eseguirle direttamente sul tuo host. Questo limita il raggio d'azione di qualsiasi operazione non intenzionale al sandbox, lasciando intatti il filesystem e la rete del tuo host.

Crea l'immagine del sandbox una sola volta (Docker deve essere installato):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Esegui questo comando per aggiungere la chiave `sandbox` all'interno del blocco `agents.defaults` esistente in `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Per impostazione predefinita, i container sandbox **non hanno accesso alla rete**. Consulta il [riferimento sul sandboxing](https://docs.openclaw.ai/gateway/sandboxing) per i bind mount e le sostituzioni di rete.

> #### Risoluzione dei problemi: Permesso negato da Docker
> 
> Se ricevi il messaggio "permission denied" durante l'esecuzione dei comandi Docker:
> 
> **Passaggio 1: Aggiungi il tuo utente al gruppo docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Passaggio 2: Se l'errore persiste, applica la correzione permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Quindi **riavvia** il sistema.
> 
> **Soluzione temporanea rapida** (si ripristina dopo il riavvio):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Consigliato) Integrazione di OpenClaw con i Servizi Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) fornisce un servizio di crawling web e di estrazione dei contenuti self-hosted che può aggirare queste difficoltà e sbloccare il pieno potenziale dell'automazione di OpenClaw. 

In questa configurazione, OpenClaw viene eseguito come un insieme di container Docker gestiti con Podman. Per semplificare la gestione del ciclo di vita e l'avvio automatico, registriamo Firecrawl come servizio `systemd` a livello utente che orchestra lo stack Podman Compose sottostante. Questo consente a OpenClaw di avviare il gateway, arrestarlo e verificare il servizio Firecrawl utilizzando i normali comandi `systemctl --user` invece di interagire direttamente con i container. 

Per semplicità, abbiamo suddiviso l'intero processo in quattro passaggi:

---

### 1. Registra il servizio di sistema
Vai alla directory di configurazione utente di systemd:
```bash
cd ~/.config/systemd/user
```
Crea e apri un nuovo file chiamato `firecrawl.service`.
```bash
nano firecrawl.service
```
Copia e incolla la seguente configurazione:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
A questo punto, il servizio è stato definito ma non ancora registrato con `systemd`. 
Assicurati che il nome del file corrisponda esattamente a quello creato sopra, quindi esegui:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Se l'operazione va a buon fine, dovresti vedere il seguente output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contiene i collegamenti simbolici ai servizi configurati per l'avvio automatico.
### 2. Configura Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) è ideale per chi ha bisogno del pieno controllo sui propri ambienti di scraping ed elaborazione dei dati, ma comporta un compromesso in termini di ulteriori sforzi di manutenzione e configurazione.

Inizia clonando il repository:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crea il file `.env` nella directory principale `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Distribuisci OpenClaw con Podman Compose

Prima di procedere, assicurati di aver scaricato l'ultima immagine Docker di OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Fatto ciò, scarica il file Compose di OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) e posizionalo nella directory principale `/firecrawl`:

> Questa convenzione è necessaria affinché `systemd` possa individuare e avviare correttamente il servizio, come specificato in `WorkingDirectory=${HOME}/firecrawl`.

> Puoi sempre espandere lo stack aggiungendo ulteriori servizi Firecrawl secondo necessità. L'elenco completo dei servizi disponibili è disponibile nel file ufficiale [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Avvia il servizio OpenClaw tramite Firecrawl 

Prima di affidare il controllo a `systemd`, verifica che tutto funzioni correttamente eseguendo lo stack manualmente:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Se tutto è configurato correttamente, dovresti vedere il container OpenClaw avviarsi e l'output della riga di comando dovrebbe assomigliare a questo:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Una volta verificato, arresta nuovamente lo stack prima di procedere:
```bash
podman compose -f openclaw-compose.yaml down
```
Prima di avviare il servizio, devi assicurarti che la proprietà e i permessi corretti siano impostati sulla directory `firecrawl` e sul relativo file `.env`. 
Questo è essenziale affinché il servizio possa scrivere le tue credenziali all'avvio.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Ora che tutto è stato verificato, avvia il servizio tramite `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Le OpenClaw Actions](https://docs.openclaw.ai/) sono accessibili dall'interno del container interattivo, e il Web Dashboard è disponibile sullo stesso host e porta all'indirizzo http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Ottenere il tuo `OPENCLAW_GATEWAY_TOKEN`

Una volta che il servizio è attivo e funzionante, noterai una nuova directory `.openclaw` creata nella tua cartella home (~/.openclaw). Questa directory è bloccata per impostazione predefinita, quindi dovrai sbloccarla per recuperare il tuo token di gateway.

1. Concedi l'accesso alla directory:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Leggi il tuo token di gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Individua il valore `OPENCLAW_GATEWAY_TOKEN` nell'output.

3. Apri il dashboard del gateway nel tuo browser all'indirizzo http://127.0.0.1:18789. Incolla il tuo token quando richiesto per autenticarti.

Per interrompere il servizio, esegui:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Avvia il Gateway OpenClaw

Il gateway è il processo OpenClaw che gestisce il ciclo dell'agente e serve il dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Per aprire il dashboard, esegui questo comando in un secondo terminale mentre il gateway è ancora in esecuzione:

```bash
openclaw dashboard
```

Poiché il gateway si collega al loopback, il dashboard si autentica automaticamente quando viene aperto dalla stessa macchina, non è necessario inserire un token o approvare il dispositivo per l'accesso locale. Dovresti vedere il dashboard di OpenClaw con il tuo modello Lemonade elencato come backend attivo.

> Se hai abilitato il sandboxing, puoi verificarlo chiedendo all'agente di eseguire `run hostname` dal dashboard. Se vedi un breve ID container invece del nome host della tua macchina, il sandbox funziona correttamente.

**Congratulazioni, hai creato uno stack di agenti AI completamente locale da zero.**

> **Hai bisogno del token del gateway?** Esegui `openclaw dashboard --no-open` per stampare l'URL del dashboard con il token incorporato (tenta anche di copiarlo negli appunti). In alternativa, il token si trova in `gateway.auth.token` all'interno di `~/.openclaw/openclaw.json`.
>
> **Approvare un dispositivo remoto:** Quando apri il dashboard da una seconda macchina o da un telefono, il browser mostra un ID richiesta. Sulla macchina che esegue il gateway, esegui:
> ```bash
> openclaw devices approve <requestId>
> ```
> Questo è necessario solo per dispositivi remoti o secondari; l'accesso loopback dalla stessa macchina si autentica automaticamente.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opzionale: Collega un Canale di Comunicazione

Una volta che il gateway è in esecuzione, puoi raggiungere il tuo agente locale da qualsiasi dispositivo. Scegli l'opzione più adatta alla tua configurazione. OpenClaw supporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) e altri canali; consulta l'elenco completo su [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opzione A: Discord

Discord richiede un server in cui **tu abbia accesso come amministratore** per aggiungere un bot. Se condividi dei server ma non ne possiedi uno, usa l'Opzione B (Telegram).

#### Crea un account e un server Discord

Se non hai un account Discord, registrati su [discord.com](https://discord.com). Hai anche bisogno di un server in cui sei amministratore: creane uno cliccando sull'icona **+** nella barra laterale di Discord e selezionando **Crea un server personale**. Un server privato va benissimo.

#### Crea un'applicazione e un bot Discord

1. Vai al [Discord Developer Portal](https://discord.com/developers/applications) e fai clic su **New Application**. Assegnagli un nome (ad es. "openclaw-bot").
2. Nella barra laterale, fai clic su **Bot**. Imposta un nome utente per il bot.
3. Sempre nella pagina Bot, scorri fino a **Privileged Gateway Intents** e abilita:
   - **Message Content Intent** (obbligatorio)
   - **Server Members Intent** (consigliato)
4. Scorri di nuovo verso l'alto e fai clic su **Reset Token** per generare il token del tuo bot. Copialo.

#### Aggiungi il bot al tuo server

1. Nella barra laterale, fai clic su **OAuth2/ URL Generator**.
2. In **Scopes**, abilita `bot` e `applications.commands`.
3. In **Bot Permissions**, abilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia l'URL generato, incollalo nel tuo browser, seleziona il tuo server e conferma. Il bot dovrebbe ora apparire nell'elenco dei membri del tuo server.
#### Raccogli i tuoi ID

Abilita la Modalità sviluppatore in Discord (**Impostazioni utente/ Avanzate/ Modalità sviluppatore**), quindi:
- Fai clic destro sull'icona del tuo server: **Copia ID server**
- Fai clic destro sul tuo avatar: **Copia ID utente**

#### Consenti i DM dai membri del server

Fai clic destro sull'icona del tuo server/ **Impostazioni privacy**/ attiva **Messaggi diretti**. Questo permette al bot di inviarti DM, il che è necessario per la fase di associazione.

#### Configura OpenClaw per Discord

Salva il token del tuo bot come variabile d'ambiente, quindi crea un unico file di patch che abiliti Discord, faccia riferimento al token e inserisca il tuo server nella allowlist. Sostituisci `<server_id>` e `<user_id>` con gli ID raccolti sopra.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Non fare affidamento sul chiedere all'agente di configurare questo.** Quando il sandboxing è abilitato, l'agente non può scrivere su `~/.openclaw/openclaw.json` dall'interno della sandbox, usa invece i comandi CLI sopra sull'host.

Riavvia il gateway in modo che rilevi la nuova configurazione del canale:

```bash
openclaw gateway run --bind loopback --port 18789
```

Dovresti vedere `logged in to discord as <bot-name>` nell'output del gateway entro pochi secondi.

#### Associa il tuo account Discord

Invia un DM al bot in Discord. Risponderà con un breve codice di associazione.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approvalo sulla macchina su cui gira OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> I codici di associazione scadono dopo un'ora.

Ora puoi chattare con il tuo agente direttamente da Discord e delegare attività al tuo hardware locale.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opzione B: Telegram

Telegram è più semplice di Discord per la maggior parte degli utenti, non richiede un server né accesso da amministratore.

#### Crea un bot Telegram

1. Apri Telegram e invia un messaggio a **@BotFather**.
2. Invia `/newbot` e segui le istruzioni. Salva il token del bot che ti viene fornito.

#### Configura OpenClaw per Telegram

Salva il token come variabile d'ambiente:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Aggiungi la configurazione del canale a `~/.openclaw/openclaw.json` (oppure applicala tramite la dashboard):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Riavvia il gateway, poi invia al tuo bot un qualsiasi messaggio su Telegram. Approva l'associazione:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

I codici di associazione scadono dopo un'ora. Ora puoi chattare con il tuo agente tramite DM su Telegram.

---

## Passaggi successivi

Ora che il tuo agente può ricevere comandi dal tuo telefono e agire sulla tua macchina locale, ecco tre direzioni che vale la pena esplorare:

1. **Riepilogo del mercato azionario**: Pianifica OpenClaw per recuperare dati da API finanziarie a intervalli fissi, riassumere i movimenti della giornata con il tuo modello locale e inviare un digest al tuo telefono ogni mattina tramite il canale scelto.

2. **Monitor del fine-tuning**: Avvia un job di training da remoto tramite Telegram o Discord, quindi fai in modo che l'agente segua il log di training e riporti al tuo telefono valori periodici di loss, utilizzo della GPU e uso del disco. Se l'esecuzione si blocca o la VRAM ha un picco, lo scopri immediatamente senza dover essere davanti alla macchina.

3. **IOT con un VLM locale**: Punta una telecamera sulla tua porta d'ingresso, esegui un modello di visione su Lemonade e fai in modo che OpenClaw analizzi i fotogrammi su richiesta o in base a un trigger. Chiedi "sono arrivati pacchi oggi?" dal tuo telefono e ottieni una risposta diretta dal tuo stesso hardware.

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