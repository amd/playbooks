<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Esecuzione di Hermes Agent in locale con Lemonade Server

## Panoramica

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) è un agente AI capace di auto-miglioramento, sviluppato da Nous Research. Dispone di un ciclo di apprendimento integrato, crea competenze a partire dall'esperienza, costruisce una memoria persistente su chi sei tra una sessione e l'altra, e può eseguire automazioni pianificate per tuo conto. A differenza di un semplice assistente di chat, Hermes compie azioni reali: esegue comandi shell, scrive file, naviga sul web e delega flussi di lavoro paralleli a subagenti.

[**Lemonade Server**](https://lemonade-server.ai/) è il backend di inferenza locale che lo alimenta. È un server open-source che esegue modelli GenAI direttamente sul tuo hardware AMD e li espone tramite l'API standard di settore OpenAI.

Insieme formano uno stack di agenti AI completamente locale: Lemonade gestisce l'inferenza dei modelli sulla tua GPU, mentre Hermes fornisce il ciclo dell'agente, la memoria, le competenze e il gateway di messaggistica.

> **Prima di continuare:** Hermes Agent è un agente AI altamente autonomo. Concedere a qualsiasi agente AI l'accesso al tuo sistema può comportare risultati imprevedibili o non voluti. Procedi solo se comprendi i rischi e ti senti a tuo agio con software autonomo che agisce per tuo conto.

---

## Cosa imparerai

Al termine di questa guida sarai in grado di:

- **Installare Hermes Agent** e configurarlo per usare **Lemonade Server** come backend AI.
- **(Consigliato) Abilitare il sandboxing con Docker/Podman** per isolare le azioni dell'agente dal tuo sistema host.
- **Avviare il gateway Hermes** e verificare che il tuo agente sia pronto.
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
- **~10–30 GB di spazio libero su disco** per i pesi del modello
- [Podman](https://podman.io/docs/installation) (Opzionale, per il sandboxing di Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Un PC con **Windows 10/11**
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- **~10–30 GB di spazio libero su disco** per i pesi del modello
- Podman (Opzionale, per il sandboxing di Hermes Agent). Da installare all'interno di WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman è preinstallato su Halo Box e non richiede alcuna configurazione
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Scaricare e caricare il modello consigliato

Il modello consigliato per questa guida è **Qwen3.6-35B-A3B-GGUF** di Unsloth, un potente modello MoE con una finestra di contesto di 263k token, particolarmente adatto ai carichi di lavoro degli agenti. Questo modello utilizza la quantizzazione UD-Q4_K_XL. Scaricalo ora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Quindi caricalo con un'ampia finestra di contesto e salva questa impostazione per le esecuzioni future:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Il modello ha una lunghezza di contesto predefinita di 262.144 token. Se riscontri errori di memoria insufficiente (OOM), valuta di ridurre la finestra di contesto.

> **Suggerimento: disabilita la modalità di ragionamento per risposte dell'agente più rapide:** Qwen3.6-35B-A3B viene eseguito per impostazione predefinita in modalità di ragionamento (thinking mode), il che aggiunge latenza prima di ogni risposta. Nei cicli degli agenti questo overhead si accumula rapidamente. Il repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornisce una configurazione già pronta che disabilita il ragionamento. Per utilizzarla, scarica il file e importalo:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Eseguiamo Hermes Agent all'interno di WSL e lo colleghiamo a Lemonade in esecuzione nativa su Windows. Questo ti offre un ambiente shell Linux per Hermes, mantenendo al contempo l'accelerazione GPU di Lemonade sul lato Windows.

### Installazione di WSL e Ubuntu

Apri PowerShell come Amministratore e installa il kernel WSL:

```powershell
wsl --install --no-distribution
```

Quindi installa Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Abilitare systemd in WSL

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

### Collegare Lemonade da Windows a WSL

WSL2 è eseguito in una rete virtuale. Lemonade su Windows si associa a `127.0.0.1`, che WSL non può raggiungere direttamente. Un proxy di porta di Windows inoltra il traffico dall'IP gateway di WSL al localhost di Windows.

**Trova il tuo IP gateway di WSL** (esegui all'interno di WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Aggiungi il proxy di porta** (esegui in PowerShell come Amministratore, sostituendo `<WSL-Gateway-IP>` con il tuo IP gateway di WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Aggiungi una regola del firewall** (stesso PowerShell con privilegi elevati):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifica da WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se hai già caricato il modello Qwen3.6-35B-A3B-GGUF nel passaggio precedente, dovresti vedere un output JSON che elenca il modello caricato.

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

> La regola `netsh portproxy` sopravvive ai riavvii, ma l'IP gateway di WSL può cambiare dopo `wsl --shutdown`. Se Lemonade diventa irraggiungibile da WSL dopo un riavvio, ottieni l'IP gateway aggiornato e aggiorna il proxy con questo nuovo IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Installare Hermes Agent

<!-- @os:windows -->
> Esegui i comandi di questa sezione all'interno del tuo **terminale WSL**, salvo diversa indicazione.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Il flag `--skip-setup` salta la procedura guidata di configurazione interattiva, così potrai configurare manualmente il backend del modello nel passaggio successivo.

Ricarica la tua shell:

```bash
source ~/.bashrc
```

Conferma l'installazione:

```bash
hermes --version
```

Esegui una diagnostica automatica per verificare tutte le dipendenze:

```bash
hermes doctor
```

> **Suggerimento:** Se dopo l'installazione visualizzi `command not found`, aggiungi Hermes al tuo PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Per rendere questa modifica permanente, aggiungi la riga sopra al tuo `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Configura Hermes per usare Lemonade

Hermes memorizza la sua configurazione del modello in `~/.hermes/config.yaml`. Puoi usare il selettore interattivo `hermes model` oppure scrivere direttamente la configurazione.

### Opzione 1: Selettore interattivo

<!-- @os:windows -->
> Esegui quanto segue all'interno del tuo **terminale WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Quando richiesto:

1. Seleziona **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **URL base API:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **URL base API:** usa l'IP del gateway WSL: esegui `ip route show default | awk '{print $3}' | head -1` all'interno di WSL per ottenerlo, poi inserisci `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **Chiave API:** `lemonade`
4. **Modalità di compatibilità API:** `1` (Rilevamento automatico)
5. **Seleziona modello:** scegli `Qwen3.6-35B-A3B-GGUF` dall'elenco
6. **Lunghezza del contesto in token:** `262144`
7. **Nome visualizzato:** `local-lemonade` (o qualsiasi nome tu preferisca)

`hermes model` salva sia la selezione del modello attivo sia una voce `custom_providers` denominata che memorizza la lunghezza del contesto insieme all'endpoint. Il risultato in `~/.hermes/config.yaml` sarà simile a questo:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Opzione 2: Scrivi direttamente la configurazione

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

All'interno del tuo terminale WSL, ottieni l'IP dell'host Windows e scrivi la configurazione:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Consigliato) Abilita il sandboxing con Podman

Hermes Agent può instradare tutte le operazioni di shell e file dell'agente attraverso un container isolato invece di eseguirle direttamente sul tuo host. Questo limita il raggio d'azione di qualsiasi azione non intenzionale al sandbox, lasciando intatti il filesystem e la rete del tuo host.

Crea un'immagine sandbox leggera:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Entra nel tuo terminale WSL:

```powershell
wsl -d Ubuntu-24.04
```

Poi, crea un'immagine sandbox leggera:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Poi configura Hermes per usare Podman come runtime dei container e imposta il backend del terminale:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> Il `terminal.backend` rimane `docker`.
> `HERMES_DOCKER_BINARY` è ciò che indica a Hermes di usare invece Podman come runtime.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes ora avvierà un container sandbox persistente e instraderà tutte le chiamate `terminal` e agli strumenti per i file attraverso di esso. Il container condivide la durata del processo Hermes, viene riutilizzato per tutte le chiamate agli strumenti e viene distrutto quando Hermes termina.

> **Verifica che il sandbox funzioni:** Avvia Hermes (`hermes`) e chiedigli di `run hostname` - dovresti vedere un breve ID del container invece del nome host della tua macchina. Puoi anche chiedergli di `rm -rf <path-to-a-dummy-file/folder>`: Hermes confermerà l'eliminazione, ma la cartella sarà ancora presente sul tuo host. Il comando è stato eseguito all'interno della `$HOME` isolata del container, non della tua.

> **Hai bisogno di un isolamento più forte?** Hermes offre anche un'immagine Docker ufficiale (`nousresearch/hermes-agent`) che esegue l'intero processo dell'agente all'interno di un container - gateway, strumenti e tutto il resto. Consulta la [documentazione Docker di Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) per i dettagli di configurazione.

---

<!-- @os:linux -->
## (Consigliato) Integrazione di Hermes con i servizi Firecrawl

Hermes può navigare ed estrarre contenuti dai siti web utilizzando i suoi strumenti web integrati. Tuttavia, molti siti web moderni utilizzano sistemi di rilevamento dei bot, che bloccano le semplici richieste HTTP e restituiscono pagine di verifica invece del contenuto effettivo. Di conseguenza, Hermes potrebbe non essere in grado di estrarre in modo affidabile le informazioni da questi siti.

Per superare questa limitazione, [Firecrawl](https://docs.firecrawl.dev/introduction) offre un servizio di web crawling ed estrazione dei contenuti self-hosted in grado di bypassare queste verifiche e sbloccare il pieno potenziale dell'automazione di Hermes.

In questa configurazione, Firecrawl viene eseguito come un insieme di container Docker gestiti con Podman. Per semplificare la gestione del ciclo di vita e l'avvio automatico, registriamo Firecrawl come servizio `systemd` a livello utente che orchestra lo stack Podman Compose sottostante. Questo permette a Hermes di avviare, arrestare e verificare il servizio Firecrawl utilizzando i comandi standard `systemctl --user` invece di interagire direttamente con i container.

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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
A questo punto, il servizio è stato definito ma non ancora registrato con `systemd`. 
Assicurati che il nome del file corrisponda esattamente a quello creato sopra, poi esegui:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Se l'operazione va a buon fine, dovresti vedere il seguente output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contiene i collegamenti simbolici ai servizi configurati per l'avvio automatico.

### 2. Configura Firecrawl per il tuo servizio

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) è ideale per chi ha bisogno del pieno controllo sui propri ambienti di scraping ed elaborazione dei dati, ma comporta il compromesso di uno sforzo aggiuntivo di manutenzione e configurazione.

Inizia clonando il repository:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crea `.env` nella directory radice `/firecrawl`:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Imposta `BULL_AUTH_KEY` su un secret robusto, specialmente per qualsiasi implementazione raggiungibile da reti non affidabili.
### 3. Distribuzione di Hermes tramite Compose

Prima di andare avanti, assicurati di aver scaricato l'ultima immagine Docker di Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Fatto ciò, scarica il file Compose di Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) e posizionalo nella directory principale `/firecrawl`:

> Questa convenzione è necessaria affinché `systemd` possa individuare e avviare correttamente il servizio, come specificato in `WorkingDirectory=${HOME}/firecrawl`.

> Puoi sempre espandere lo stack aggiungendo ulteriori servizi Firecrawl secondo necessità. L'elenco completo dei servizi disponibili è consultabile nel file ufficiale [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Avvio del servizio Hermes tramite Firecrawl 

Prima di affidare il controllo a `systemd`, verifica che tutto funzioni correttamente eseguendo lo stack manualmente:
```bash
podman compose -f hermes-compose.yaml up -d
```
Se tutto è configurato correttamente, dovresti vedere il container Hermes avviarsi e l'output della riga di comando dovrebbe apparire simile a questo:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Una volta verificato, arresta lo stack prima di procedere:
```bash
podman compose -f hermes-compose.yaml down
```
Ora che tutto è stato verificato, avvia il servizio tramite `systemd`:
```bash
systemctl --user start firecrawl.service
```
[L'API di Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) è accessibile dall'interno del container interattivo, e la Dashboard Web è disponibile sullo stesso host e porta all'indirizzo http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Per fermare il servizio, esegui:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Nativo

Avvia direttamente una sessione CLI interattiva: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Congratulazioni, hai creato uno stack di agenti AI completamente locale.**

### Dashboard Web

Hermes include un'interfaccia utente basata su browser per gestire configurazione, chiavi API, modelli, sessioni, memoria e attività pianificate (cron job). Apri un secondo terminale mentre il gateway o la CLI sono in esecuzione e avviala con:

```bash
hermes dashboard
```

Questo avvia un server locale e apre `http://127.0.0.1:9119` nel tuo browser. Consulta la [documentazione della dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) per il riferimento completo delle funzionalità.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opzionale: Collegare un canale di comunicazione

Una volta avviato il gateway, puoi raggiungere il tuo agente locale da qualsiasi dispositivo. Hermes supporta [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) e altri

---

### Discord

Discord richiede un server in cui **tu abbia accesso come amministratore** per aggiungere un bot. Se condividi server ma non ne possiedi uno, usa invece Telegram.

#### Creare un'applicazione e un bot Discord

1. Vai al [Discord Developer Portal](https://discord.com/developers/applications) e fai clic su **New Application**. Assegnale un nome (ad esempio "hermes-bot").
2. Nella barra laterale, fai clic su **Bot**. Imposta un nome utente per il bot.
3. Sempre nella pagina Bot, scorri fino a **Privileged Gateway Intents** e abilita:
   - **Message Content Intent** (obbligatorio)
   - **Server Members Intent** (consigliato)
4. Torna in alto e fai clic su **Reset Token** per generare il token del tuo bot. Copialo.

#### Aggiungere il bot al tuo server

1. Nella barra laterale, fai clic su **OAuth2 / URL Generator**.
2. In **Scopes**, abilita `bot` e `applications.commands`.
3. In **Bot Permissions**, abilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia l'URL generato, incollalo nel tuo browser, seleziona il tuo server e conferma.

#### Raccogliere i tuoi ID e consentire i messaggi diretti

Abilita la Modalità Sviluppatore in Discord (**User Settings / Advanced / Developer Mode**), quindi:
- Fai clic destro sull'icona del tuo server: **Copy Server ID**
- Fai clic destro sul tuo avatar: **Copy User ID**

Fai clic destro sull'icona del tuo server / **Privacy Settings** / attiva **Direct Messages**. Questo è necessario per la fase di associazione (pairing).

#### Configurare Hermes per Discord

Aggiungi quanto segue a `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Quindi avvia il gateway:

```bash
hermes gateway
```

Il bot dovrebbe risultare online su Discord entro pochi secondi. Invia un messaggio, sia in DM che in un canale che può vedere.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Creare un bot Telegram

1. Apri Telegram e invia un messaggio a **@BotFather**.
2. Invia `/newbot` e segui le istruzioni. Salva il token del bot che ti viene fornito.

#### Configurare Hermes per Telegram

Aggiungi quanto segue a `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Non conosci il tuo ID utente Telegram?** Invia un messaggio a [@userinfobot](https://t.me/userinfobot) su Telegram, ti risponderà con il tuo ID numerico.

Quindi avvia il gateway:

```bash
hermes gateway
```

Invia al tuo bot un messaggio qualsiasi su Telegram per testarlo. Ora puoi chattare con il tuo agente tramite DM Telegram. Consulta la [guida completa alla configurazione di Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) per la modalità webhook e le opzioni avanzate.

---

## Prossimi passi

Ora che il tuo agente può ricevere comandi dal tuo telefono e agire sulla tua macchina locale, ecco tre direzioni che vale la pena esplorare:

1. **Digest di ricerca automatizzato**: Pianifica Hermes per cercare sul web gli argomenti che ti interessano ogni mattina, riassumere i risultati con il tuo modello locale e inviare un digest al tuo telefono tramite Telegram o Discord, il tutto in esecuzione sul tuo hardware senza costi cloud.

2. **Revisione del codice su richiesta**: Punta Hermes su un repository GitHub, chiedigli di rivedere le pull request aperte e fagli pubblicare commenti o un riepilogo nella tua chat. Con il backend terminale Docker, tutte le operazioni git vengono eseguite all'interno della sandbox, mantenendo pulito il tuo host.

3. **Assistente file locale**: Concedi a Hermes l'accesso a una directory di lavoro e chiedigli di organizzare, rinominare, riassumere o trasformare file su richiesta dal tuo telefono. Poiché il backend terminale Docker confina tutte le scritture all'interno dello spazio di lavoro sandbox, le operazioni distruttive accidentali sono contenute.