<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Esegui OpenClaw con Lemonade Server come backend

## Panoramica

[**OpenClaw**](https://openclaw.ai/) è un agente AI autonomo in grado di scrivere ed eseguire codice, gestire file e portare a termine attività complesse a più fasi per tuo conto. A differenza di un assistente di chat che si limita a rispondere alle domande, OpenClaw esegue azioni reali sul tuo sistema, il che significa che necessita di un backend AI veloce e capace, in grado di stare al passo con un ciclo di agente impegnativo.

[**Lemonade Server**](https://lemonade-server.ai/) è quel backend. Si tratta di un server di inferenza locale open source che esegue modelli GenAI direttamente sul tuo hardware e li espone tramite l'API standard del settore OpenAI.

Insieme, formano uno stack di agenti AI completamente locale: Lemonade gestisce l'inferenza dei modelli e OpenClaw fornisce il ciclo dell'agente che trasforma gli output del modello in azioni reali.

> **Prima di continuare:** OpenClaw è un agente AI altamente autonomo. Concedere a qualsiasi agente AI l'accesso al tuo sistema può portare a risultati imprevedibili o non intenzionali. Procedi solo se comprendi i rischi e sei a tuo agio con un software autonomo che agisce per tuo conto.

---

## Cosa imparerai

Alla fine di questo playbook sarai in grado di:

- Conoscere **Lemonade Server**
- **Installare OpenClaw** e **configurarlo per utilizzare Lemonade Server** come backend AI.
- **Avviare il gateway di OpenClaw** e verificare che il tuo agente sia pronto per lavorare.
- **Collegare un canale di comunicazione** (Discord o Telegram) in modo da poter chattare con il tuo agente da qualsiasi dispositivo.

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

- **Circa 10–30 GB di spazio libero su disco** per i pesi del modello
<!-- @os:end -->
<!-- @os:windows -->
- Un PC con **Windows 10/11**
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- **Circa 10–30 GB di spazio libero su disco** per i pesi del modello
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

Il modello consigliato per questo playbook è **Qwen3.6-35B-A3B-GGUF** di Unsloth, un solido modello MoE con una finestra di contesto di 263k token, particolarmente adatto ai carichi di lavoro degli agenti. Questo modello utilizza la quantizzazione UD-Q4_K_XL. Scaricalo ora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Quindi caricalo con un'ampia finestra di contesto e salva questa impostazione per gli utilizzi futuri:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Il modello ha una lunghezza di contesto predefinita di 262.144 token. Se riscontri errori di memoria esaurita (OOM), valuta di ridurre la finestra di contesto. Tuttavia, poiché Qwen3.6 sfrutta il contesto esteso per attività complesse, ti consigliamo di mantenere una lunghezza di contesto di almeno 128K token per preservare le capacità di ragionamento.

> **Suggerimento: disattiva il ragionamento per risposte dell'agente più rapide:** Qwen3.6-35B-A3B viene eseguito in modalità di ragionamento per impostazione predefinita, il che aggiunge latenza prima di ogni risposta. Nei cicli degli agenti, questo sovraccarico si accumula rapidamente. Il repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornisce una configurazione già pronta che disattiva il ragionamento. Per utilizzarla, scarica il file e importalo:
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

## Configura WSL

Eseguiamo OpenClaw all'interno di WSL (consigliato) e lo colleghiamo a Lemonade in esecuzione nativa su Windows. Questo ti offre un ambiente shell Linux per OpenClaw, mantenendo al contempo l'accelerazione GPU di Lemonade sul lato Windows.

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

WSL2 viene eseguito in una rete virtuale. Lemonade su Windows si associa a `127.0.0.1`, a cui WSL non può accedere direttamente. Un proxy di porta di Windows inoltra il traffico dall'IP del gateway WSL a localhost di Windows.

**Trova l'IP del gateway WSL** (esegui all'interno di WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Aggiungi il proxy di porta** (esegui in PowerShell come amministratore, sostituendo `<WSL-Gateway-IP>` con l'IP del gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Aggiungi una regola del firewall** (nello stesso PowerShell con privilegi elevati):

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

> La regola `netsh portproxy` sopravvive ai riavvii, ma l'IP del gateway WSL può cambiare dopo `wsl --shutdown`. Se Lemonade diventa irraggiungibile da WSL dopo un riavvio, ottieni l'IP del gateway aggiornato e aggiorna il proxy con questo nuovo IP.

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

## Installa e configura OpenClaw

### Installa OpenClaw
<!-- @os:windows -->
> Esegui i comandi di questa sezione all'interno del tuo **terminale WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Il flag `--no-onboard` salta la procedura guidata di configurazione interattiva; configurerai manualmente il backend del modello nel passaggio successivo, il che ti offre un controllo preciso su quale modello e server vengono utilizzati.

Apri un nuovo terminale e verifica l'installazione:

```bash
openclaw --version
```

> **Suggerimento:** se dopo l'installazione visualizzi `command not found`, aggiungi la directory bin globale di npm al tuo PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Per rendere questa modifica permanente, aggiungi la riga sopra al tuo file `~/.bashrc` o `~/.zshrc`.

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
### Configura OpenClaw per Usare Lemonade

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

> **Dimensionamento della finestra di contesto di OpenClaw:** la compattazione di OpenClaw si attiva quando `contextTokens > contextWindow − reserveTokens`. Il valore predefinito di `reserveTokensFloor` è 20.000 token, un limite minimo che sovrascrive `reserveTokens` quando quest'ultimo è inferiore, quindi qualsiasi contesto del modello sotto i ~37k causerà un ciclo infinito di compattazione. Imposta una riserva bassa e disabilita il limite minimo una volta nella tua configurazione e verrà applicato a ogni modello, senza necessità di regolazioni per singolo modello:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` è un *limite minimo* (una protezione minima), non la riserva stessa; impostare solo il limite minimo non ha alcun effetto. `reserveTokensFloor: 0` disabilita la protezione così da accettare il valore più basso di `reserveTokens`.
>
> **Quando applicarlo:** usa questa configurazione se la finestra di contesto effettiva del tuo modello è inferiore a ~37k, sia perché il modello è piccolo (ad es. 8k, 16k, 32k), sia perché hai intenzionalmente limitato il contesto a un valore più basso (ad es. caricando un modello da 128k ma impostando il contesto a 16k in Lemonade). Senza questa impostazione, OpenClaw entra in un ciclo infinito di compattazione all'avvio.

>
> **Modelli con contesto ampio a piena capacità:** puoi saltare completamente questo passaggio. I valori predefiniti funzionano correttamente, la compattazione si attiverà ben prima che la finestra si riempia e il modello avrà ampio spazio per generare risposte lunghe. Se decidi comunque di applicarlo, tieni presente che `reserveTokens: 4096` limita la lunghezza della risposta a circa 4k token, il che potrebbe troncare la generazione di file lunghi o piani dettagliati.
>
> **Dove aggiungere questa configurazione:** posiziona il blocco `compaction` all'interno di `agents.defaults` nel tuo `openclaw.json` (solitamente in `~/.openclaw/openclaw.json`):
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
> Il resto della tua configurazione (gateway, canali, modelli, ecc.) rimane invariato, è necessario aggiungere solo la chiave `compaction`.

### (Consigliato) Abilita il Sandboxing con Docker

OpenClaw può instradare tutte le operazioni dell'agente su file e codice attraverso un container Docker isolato invece di eseguirle direttamente sul tuo host. Questo limita il raggio d'azione di qualsiasi operazione non intenzionale al sandbox, lasciando intatti il filesystem e la rete del tuo host.

Crea l'immagine sandbox una sola volta (Docker deve essere installato):

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

Esegui questo comando per aggiungere la chiave `sandbox` all'interno del blocco esistente `agents.defaults` in `~/.openclaw/openclaw.json`:

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

> #### Risoluzione dei problemi: Permesso Negato da Docker
> 
> Se ricevi "permission denied" durante l'esecuzione dei comandi Docker:
> 
> **Passo 1: Aggiungi il tuo utente al gruppo docker**
> 
> ```bash
> sudo groupadd docker                    # Crea il gruppo se necessario
> sudo usermod -aG docker $USER           # Aggiungi te stesso al gruppo
> newgrp docker                           # Attiva la modifica
> docker run hello-world                  # Testalo
> ```
> 
> **Passo 2: Se l'errore persiste, applica la correzione permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Poi **riavvia** il sistema.
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

### Avvia il Gateway di OpenClaw

Il gateway è il processo di OpenClaw che gestisce il ciclo dell'agente e serve la dashboard:

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

Per aprire la dashboard, esegui questo comando in un secondo terminale mentre il gateway è ancora in esecuzione:

```bash
openclaw dashboard
```

Poiché il gateway si collega al loopback, la dashboard si autentica automaticamente quando viene aperta dalla stessa macchina, senza necessità di inserire un token o approvare il dispositivo per l'accesso locale. Dovresti vedere la dashboard di OpenClaw con il tuo modello Lemonade elencato come backend attivo.

> Se hai abilitato il sandboxing, puoi verificarlo chiedendo all'agente di `run hostname` dalla dashboard. Se vedi un breve ID container invece del nome host della tua macchina, il sandbox sta funzionando.

**Congratulazioni, hai costruito da zero uno stack di agenti AI completamente locale.**

> **Ti serve il token del gateway?** Esegui `openclaw dashboard --no-open` per stampare l'URL della dashboard con il token incorporato (tenta anche di copiarlo negli appunti). In alternativa, il token si trova in `gateway.auth.token` in `~/.openclaw/openclaw.json`.
>
> **Approvazione di un dispositivo remoto:** quando apri la dashboard da una seconda macchina o da un telefono, il browser mostra un ID di richiesta. Sulla macchina che esegue il gateway, esegui:
> ```bash
> openclaw devices approve <requestId>
> ```
> Questo è necessario solo per dispositivi remoti o secondari, l'accesso loopback dalla stessa macchina si autentica automaticamente.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opzionale: Collega un Canale di Comunicazione

Una volta che il gateway è in esecuzione, puoi raggiungere il tuo agente locale da qualsiasi dispositivo. Scegli l'opzione più adatta alla tua configurazione. OpenClaw supporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), e altri canali; consulta l'elenco completo su [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opzione A: Discord

Discord richiede un server su cui **hai accesso come amministratore** per aggiungere un bot. Se condividi server ma non ne possiedi uno, usa invece l'Opzione B (Telegram).
#### Crea un account Discord e un server

Se non hai un account Discord, registrati su [discord.com](https://discord.com). Ti serve anche un server in cui sei amministratore: creane uno cliccando sull'icona **+** nella barra laterale di Discord e selezionando **Crea un mio server**. Un server privato va benissimo.

#### Crea un'applicazione Discord e un bot

1. Vai al [Discord Developer Portal](https://discord.com/developers/applications) e clicca su **New Application**. Assegnagli un nome (ad esempio "openclaw-bot").
2. Nella barra laterale, clicca su **Bot**. Imposta un nome utente per il bot.
3. Sempre nella pagina Bot, scorri fino a **Privileged Gateway Intents** e abilita:
   - **Message Content Intent** (obbligatorio)
   - **Server Members Intent** (consigliato)
4. Torna in alto e clicca su **Reset Token** per generare il token del tuo bot. Copialo.

#### Aggiungi il bot al tuo server

1. Nella barra laterale, clicca su **OAuth2/ URL Generator**.
2. In **Scopes**, abilita `bot` e `applications.commands`.
3. In **Bot Permissions**, abilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia l'URL generato, incollalo nel browser, seleziona il tuo server e conferma. Il bot dovrebbe ora comparire nell'elenco membri del tuo server.

#### Raccogli i tuoi ID

Abilita la Modalità sviluppatore in Discord (**Impostazioni utente/ Avanzate/ Modalità sviluppatore**), quindi:
- Fai clic destro sull'icona del tuo server: **Copia ID server**
- Fai clic destro sul tuo avatar: **Copia ID utente**

#### Consenti i DM dai membri del server

Fai clic destro sull'icona del tuo server/ **Impostazioni privacy**/ attiva **Messaggi diretti**. Questo permette al bot di inviarti messaggi diretti, cosa necessaria per la fase di pairing.

#### Configura OpenClaw per Discord

Memorizza il token del tuo bot come variabile d'ambiente, quindi crea un unico file di patch che abiliti Discord, faccia riferimento al token e inserisca il tuo server nella allowlist. Sostituisci `<server_id>` e `<user_id>` con gli ID raccolti sopra.

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

> **Non fare affidamento sul chiedere all'agente di configurare questo.** Quando il sandboxing è abilitato, l'agente non può scrivere su `~/.openclaw/openclaw.json` dall'interno del sandbox: usa invece i comandi CLI sopra riportati sull'host.

Riavvia il gateway in modo che rilevi la nuova configurazione del canale:

```bash
openclaw gateway run --bind loopback --port 18789
```

Dovresti vedere `logged in to discord as <bot-name>` nell'output del gateway entro pochi secondi.

#### Effettua il pairing del tuo account Discord

Invia un DM al bot in Discord. Risponderà con un breve codice di pairing.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approvalo sulla macchina su cui gira OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> I codici di pairing scadono dopo un'ora.

Ora puoi chattare con il tuo agente direttamente da Discord e delegare attività al tuo hardware locale.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opzione B: Telegram

Telegram è più semplice di Discord per la maggior parte degli utenti: non richiede un server né accesso da amministratore.

#### Crea un bot Telegram

1. Apri Telegram e invia un messaggio a **@BotFather**.
2. Invia `/newbot` e segui le istruzioni. Salva il token del bot che ti viene fornito.

#### Configura OpenClaw per Telegram

Memorizza il token come variabile d'ambiente:

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

Riavvia il gateway, quindi invia al tuo bot un qualsiasi messaggio su Telegram. Approva il pairing:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

I codici di pairing scadono dopo un'ora. Ora puoi chattare con il tuo agente tramite DM su Telegram.

---

## Prossimi passi

Ora che il tuo agente può ricevere comandi dal tuo telefono e agire sulla tua macchina locale, ecco tre direzioni interessanti da esplorare:

1. **Riassuntore del mercato azionario**: Pianifica OpenClaw per recuperare dati da API finanziarie a intervalli fissi, riassumere gli andamenti della giornata con il tuo modello locale e inviare un digest al tuo telefono ogni mattina tramite il canale scelto.

2. **Monitor per il fine-tuning**: Avvia da remoto un job di training tramite Telegram o Discord, quindi fai in modo che l'agente segua il log di training e riporti periodicamente al tuo telefono i valori di loss, l'utilizzo della GPU e lo spazio su disco. Se l'esecuzione si blocca o la VRAM ha un picco, lo scopri immediatamente senza dover essere davanti alla macchina.

3. **IOT con un VLM locale**: Punta una telecamera verso la porta d'ingresso, esegui un modello di visione su Lemonade e fai in modo che OpenClaw analizzi i fotogrammi su richiesta o al verificarsi di un trigger. Chiedi "sono arrivati pacchi oggi?" dal tuo telefono e ottieni una risposta diretta dal tuo stesso hardware.