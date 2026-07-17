<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Eseguire OpenClaw con Lemonade Server come backend

## Panoramica

[**OpenClaw**](https://openclaw.ai/) è un agente AI autonomo in grado di scrivere ed eseguire codice, gestire file e portare a termine attività complesse a più fasi per conto dell'utente. A differenza di un assistente chat che si limita a rispondere a domande, OpenClaw compie azioni reali sul sistema, il che significa che ha bisogno di un backend AI veloce e capace, in grado di stare al passo con un ciclo agente impegnativo.

[**Lemonade Server**](https://lemonade-server.ai/) è quel backend. È un server di inferenza locale open-source che esegue modelli GenAI direttamente sull'hardware dell'utente e li espone tramite l'API OpenAI standard del settore.

Insieme, formano uno stack di agenti AI completamente locale: Lemonade gestisce l'inferenza del modello, mentre OpenClaw fornisce il ciclo agente che trasforma gli output del modello in azioni reali.

> **Prima di continuare:** OpenClaw è un agente AI altamente autonomo. Concedere a qualsiasi agente AI l'accesso al proprio sistema può comportare risultati imprevedibili o indesiderati. Procedere solo se si comprendono i rischi e si è a proprio agio con software autonomo che agisce per proprio conto.

---

## Cosa Imparerai

Al termine di questo playbook sarai in grado di:

- Conoscere **Lemonade Server**
- **Installare OpenClaw** e **puntarlo a Lemonade Server** come backend AI.
- **Avviare il gateway OpenClaw** e confermare che l'agente è pronto a lavorare.
- **Connettere un canale di comunicazione** (Discord o Telegram) per chattare con il proprio agente da qualsiasi dispositivo.

---

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificare gli Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

<!-- @os:linux -->
- Un PC con **Ubuntu 24.04+** o una distribuzione Linux basata su Debian compatibile con `apt-get`
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

## Scaricare e Caricare il Modello Consigliato

Il modello consigliato per questo playbook è **Qwen3.6-35B-A3B-GGUF** di Unsloth, un potente modello MoE con una finestra di contesto di 263k token, particolarmente adatto ai carichi di lavoro degli agenti. Questo modello utilizza la quantizzazione UD-Q4_K_XL. Scaricarlo ora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Quindi caricarlo con una finestra di contesto ampia e salvare tale impostazione per le esecuzioni future:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Il modello ha una lunghezza di contesto predefinita di 262.144 token. In caso di errori di memoria insufficiente (OOM), considerare la riduzione della finestra di contesto. Tuttavia, poiché Qwen3.6 sfrutta il contesto esteso per attività complesse, si consiglia di mantenere una lunghezza di contesto di almeno 128K token per preservare le capacità di ragionamento.

> **Suggerimento: Disabilitare il thinking per risposte dell'agente più veloci:** Qwen3.6-35B-A3B viene eseguito in modalità thinking per impostazione predefinita, il che aggiunge latenza prima di ogni risposta. Nei cicli agente questo overhead si accumula rapidamente. Il repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornisce una configurazione già pronta che disabilita il thinking. Per utilizzarla, scaricare il file e importarlo:
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

## Configurare WSL

Eseguiamo OpenClaw all'interno di WSL (consigliato) e lo connettiamo a Lemonade in esecuzione nativamente su Windows. Questo fornisce un ambiente shell Linux per OpenClaw mantenendo l'accelerazione GPU di Lemonade sul lato Windows.

### Installare WSL e Ubuntu

Aprire PowerShell come Amministratore e installare il kernel WSL:

```powershell
wsl --install --no-distribution
```

Quindi installare Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Abilitare systemd in WSL

Eseguire questo comando nel terminale Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Riavviare WSL:

```powershell
wsl --shutdown
wsl
```

### Collegare Lemonade da Windows a WSL

WSL2 viene eseguito in una rete virtuale. Lemonade su Windows si associa a `127.0.0.1`, che WSL non può raggiungere direttamente. Un proxy di porta Windows inoltra il traffico dall'IP del gateway WSL al localhost di Windows.

**Trovare l'IP del gateway WSL** (eseguire all'interno di WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Aggiungere il proxy di porta** (eseguire in PowerShell come Amministratore, sostituendo `<WSL-Gateway-IP>` con il proprio IP del gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Aggiungere una regola firewall** (stesso PowerShell elevato):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verificare da WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se il modello Qwen3.6-35B-A3B-GGUF è già stato caricato nel passaggio precedente, si dovrebbe vedere un output JSON simile a questo:

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

> La regola `netsh portproxy` sopravvive ai riavvii, ma l'IP del gateway WSL può cambiare dopo `wsl --shutdown`. Se Lemonade diventa irraggiungibile da WSL dopo un riavvio, ottenere l'IP del gateway aggiornato e aggiornare il proxy con questo nuovo IP.

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

## Installare e Configurare OpenClaw

### Installare OpenClaw
<!-- @os:windows -->
> Eseguire i comandi in questa sezione all'interno del **terminale WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Il flag `--no-onboard` salta la procedura guidata di configurazione interattiva; il backend del modello verrà configurato manualmente nel passaggio successivo, il che offre un controllo preciso su quale modello e server vengono utilizzati.

Aprire un nuovo terminale e confermare l'installazione:

```bash
openclaw --version
```

> **Suggerimento:** Se viene visualizzato `command not found` dopo l'installazione, aggiungere la directory bin globale di npm al PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Per rendere questa modifica permanente, aggiungere la riga sopra al file `~/.bashrc` o `~/.zshrc`.

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


### Configurare OpenClaw per Utilizzare Lemonade

Eseguire l'onboarding non interattivo di OpenClaw.
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

> **Dimensionamento della finestra di contesto di OpenClaw:** La compattazione di OpenClaw si attiva quando `contextTokens > contextWindow − reserveTokens`. Il valore predefinito di `reserveTokensFloor` è 20.000 token, un limite minimo che sovrascrive `reserveTokens` quando è inferiore, quindi qualsiasi contesto del modello inferiore a ~37k attiverà un ciclo di compattazione infinito. Impostare una riserva bassa e disabilitare il limite minimo una volta nella configurazione e si applicherà a ogni modello, senza necessità di ottimizzazione per singolo modello:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` è un *limite minimo* (guardia minima), non la riserva stessa; impostare solo il limite minimo non ha alcun effetto. `reserveTokensFloor: 0` disabilita la guardia in modo che il valore inferiore di `reserveTokens` venga accettato.
>
> **Quando applicare questa configurazione:** Utilizzare questa configurazione se la finestra di contesto effettiva del modello è inferiore a ~37k, sia perché il modello è piccolo (ad es. 8k, 16k, 32k) sia perché è stata intenzionalmente limitata a un valore inferiore (ad es. caricando un modello da 128k ma impostando il contesto a 16k in Lemonade). Senza di essa, OpenClaw entra in un ciclo di compattazione infinito all'avvio.
>
> **Modelli con contesto ampio al contesto completo:** È possibile saltare questa configurazione del tutto. I valori predefiniti funzionano correttamente, la compattazione si attiverà ben prima che la finestra si riempia e il modello avrà ampio spazio per generare risposte lunghe. Se si applica comunque, tenere presente che `reserveTokens: 4096` limita la lunghezza della risposta a ~4k token, il che potrebbe interrompere la generazione di file lunghi o piani dettagliati.
>
> **Dove aggiungere questa configurazione:** Inserire il blocco `compaction` all'interno di `agents.defaults` nel file `openclaw.json` (solitamente in `~/.openclaw/openclaw.json`):
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
> Il resto della configurazione (gateway, canali, modelli, ecc.) rimane invariato; è necessario aggiungere solo la chiave `compaction`.

### (Consigliato) Abilitare il Sandboxing Docker

OpenClaw può instradare tutte le operazioni su file e codice dell'agente attraverso un container Docker isolato anziché eseguirle direttamente sull'host. Questo limita il raggio d'azione di qualsiasi azione indesiderata al sandbox, lasciando intatti il filesystem e la rete dell'host.

Costruire l'immagine sandbox una volta (Docker deve essere installato):

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

Eseguire questo comando per aggiungere la chiave `sandbox` all'interno del blocco `agents.defaults` esistente in `~/.openclaw/openclaw.json`:

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

I container sandbox non hanno **accesso alla rete** per impostazione predefinita. Consultare il [riferimento al sandboxing](https://docs.openclaw.ai/gateway/sandboxing) per i bind mount e le sostituzioni di rete.

> #### Risoluzione dei problemi: Permesso Docker Negato
> 
> Se si riceve "permission denied" durante l'esecuzione dei comandi Docker:
> 
> **Passaggio 1: Aggiungere il proprio utente al gruppo docker**
> 
> ```bash
> sudo groupadd docker                    # Crea il gruppo se necessario
> sudo usermod -aG docker $USER           # Aggiunge l'utente al gruppo
> newgrp docker                           # Attiva la modifica
> docker run hello-world                  # Verifica
> ```
> 
> **Passaggio 2: Se l'errore persiste, applicare la correzione permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Quindi **riavviare** il sistema.
> 
> **Correzione temporanea rapida** (si azzera dopo il riavvio):
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

### Avviare il Gateway OpenClaw

Il gateway è il processo OpenClaw che gestisce il ciclo agente e serve la dashboard:

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

Per aprire la dashboard, eseguire questo comando in un secondo terminale mentre il gateway è ancora in esecuzione:

```bash
openclaw dashboard
```

Poiché il gateway si associa al loopback, la dashboard si autentica automaticamente quando viene aperta dalla stessa macchina; non è necessario inserire token o approvare dispositivi per l'accesso locale. Si dovrebbe vedere la dashboard di OpenClaw con il modello Lemonade elencato come backend attivo.

> Se il sandboxing è stato abilitato, è possibile verificarlo chiedendo all'agente di `run hostname` dalla dashboard. Se viene visualizzato un breve ID container invece del nome host della macchina, il sandbox funziona correttamente.

**Congratulazioni, hai costruito uno stack di agenti AI completamente locale da zero.**

> **Hai bisogno del token del gateway?** Eseguire `openclaw dashboard --no-open` per stampare l'URL della dashboard con il token incorporato (tenta anche di copiarlo negli appunti). In alternativa, il token si trova in `gateway.auth.token` nel file `~/.openclaw/openclaw.json`.
>
> **Approvare un dispositivo remoto:** Quando si apre la dashboard da una seconda macchina o da un telefono, il browser visualizza un ID richiesta. Sulla macchina che esegue il gateway, eseguire:
> ```bash
> openclaw devices approve <requestId>
> ```
> Questo è necessario solo per dispositivi remoti o secondari; l'accesso loopback dalla stessa macchina si autentica automaticamente.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opzionale: Connettere un Canale di Comunicazione

Una volta che il gateway è in esecuzione, è possibile raggiungere il proprio agente locale da qualsiasi dispositivo. Scegliere l'opzione più adatta alla propria configurazione. OpenClaw supporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) e altri canali; consultare l'elenco completo su [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opzione A: Discord

Discord richiede un server in cui **si dispone dell'accesso come amministratore** per aggiungere un bot. Se si condividono server ma non se ne possiede uno, utilizzare l'Opzione B (Telegram).

#### Creare un account e un server Discord

Se non si dispone di un account Discord, registrarsi su [discord.com](https://discord.com). È necessario anche un server in cui si è amministratori; crearne uno facendo clic sull'icona **+** nella barra laterale di Discord e selezionando **Crea il mio**. Un server privato va bene.

#### Creare un'applicazione e un bot Discord

1. Andare al [Portale Sviluppatori Discord](https://discord.com/developers/applications) e fare clic su **Nuova Applicazione**. Assegnarle un nome (ad es. "openclaw-bot").
2. Nella barra laterale, fare clic su **Bot**. Impostare un nome utente per il bot.
3. Sempre nella pagina Bot, scorrere fino a **Privileged Gateway Intents** e abilitare:
   - **Message Content Intent** (obbligatorio)
   - **Server Members Intent** (consigliato)
4. Scorrere verso l'alto e fare clic su **Reset Token** per generare il token del bot. Copiarlo.

#### Aggiungere il bot al server

1. Nella barra laterale, fare clic su **OAuth2/ URL Generator**.
2. In **Scopes**, abilitare `bot` e `applications.commands`.
3. In **Bot Permissions**, abilitare: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiare l'URL generato, incollarlo nel browser, selezionare il server e confermare. Il bot dovrebbe ora apparire nell'elenco dei membri del server.

#### Raccogliere gli ID

Abilitare la Modalità Sviluppatore in Discord (**Impostazioni Utente/ Avanzate/ Modalità Sviluppatore**), quindi:
- Fare clic con il tasto destro sull'icona del server: **Copia ID Server**
- Fare clic con il tasto destro sul proprio avatar: **Copia ID Utente**

#### Consentire i messaggi diretti dai membri del server

Fare clic con il tasto destro sull'icona del server/ **Impostazioni Privacy**/ attivare **Messaggi Diretti**. Questo consente al bot di inviare messaggi diretti, necessario per il passaggio di abbinamento.

#### Configurare OpenClaw per Discord

Salvare il token del bot come variabile d'ambiente, quindi creare un singolo file di patch che abilita Discord, fa riferimento al token e inserisce il server nella lista consentita. Sostituire `<server_id>` e `<user_id>` con gli ID raccolti in precedenza.

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

> **Non fare affidamento sull'agente per configurare questo.** Quando il sandboxing è abilitato, l'agente non può scrivere in `~/.openclaw/openclaw.json` dall'interno del sandbox; utilizzare i comandi CLI sopra indicati sull'host.

Riavviare il gateway in modo che rilevi la nuova configurazione del canale:

```bash
openclaw gateway run --bind loopback --port 18789
```

Entro pochi secondi si dovrebbe vedere `logged in to discord as <bot-name>` nell'output del gateway.

#### Abbinare il proprio account Discord

Inviare un messaggio diretto al bot in Discord. Il bot risponderà con un breve codice di abbinamento.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approvarlo sulla macchina che esegue OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> I codici di abbinamento scadono dopo un'ora.

Ora è possibile chattare con il proprio agente direttamente da Discord e delegare attività all'hardware locale.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opzione B: Telegram

Telegram è più semplice di Discord per la maggior parte degli utenti: non richiede server né accesso come amministratore.

#### Creare un bot Telegram

1. Aprire Telegram e inviare un messaggio a **@BotFather**.
2. Inviare `/newbot` e seguire le istruzioni. Salvare il token del bot fornito.

#### Configurare OpenClaw per Telegram

Salvare il token come variabile d'ambiente:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Aggiungere la configurazione del canale a `~/.openclaw/openclaw.json` (o applicarla tramite la dashboard):

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

Riavviare il gateway, quindi inviare qualsiasi messaggio al bot in Telegram. Approvare l'abbinamento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

I codici di abbinamento scadono dopo un'ora. Ora è possibile chattare con il proprio agente tramite messaggio diretto su Telegram.

---

## Passi Successivi

Ora che il proprio agente può ricevere comandi dal telefono e agire sulla macchina locale, ecco tre direzioni che vale la pena esplorare:

1. **Riepilogatore del mercato azionario**: Pianificare OpenClaw per recuperare dati dalle API finanziarie a intervalli fissi, riassumere i movimenti della giornata con il modello locale e inviare un riepilogo al telefono ogni mattina tramite il canale scelto.

2. **Monitor di fine-tuning**: Avviare un job di addestramento da remoto tramite Telegram o Discord, quindi fare in modo che l'agente segua il log di addestramento e riporti periodicamente i valori di loss, l'utilizzo della GPU e l'utilizzo del disco sul telefono. Se l'esecuzione si blocca o la VRAM aumenta improvvisamente, si viene avvisati immediatamente senza dover essere fisicamente alla macchina.

3. **IOT con un VLM locale**: Puntare una telecamera verso la porta d'ingresso, eseguire un modello vision su Lemonade e fare in modo che OpenClaw analizzi i fotogrammi su richiesta o su un trigger. Chiedere "sono arrivati dei pacchi oggi?" dal telefono e ottenere una risposta diretta dal proprio hardware.