<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Eseguire OpenClaw con Lemonade Server come backend

## Panoramica

[**OpenClaw**](https://openclaw.ai/) è un agente AI autonomo in grado di scrivere ed eseguire codice, gestire file e portare a termine attività complesse su più passaggi per tuo conto. A differenza di un assistente di chat che si limita a rispondere alle domande, OpenClaw esegue azioni reali sul tuo sistema, il che significa che ha bisogno di un backend AI veloce e capace, in grado di tenere il passo con un ciclo agentico impegnativo.

[**Lemonade Server**](https://lemonade-server.ai/) è quel backend. Si tratta di un server di inferenza locale open source che esegue modelli GenAI direttamente sul tuo hardware e li espone tramite l'API OpenAI, uno standard del settore.

Insieme, formano uno stack di agenti AI completamente locale: Lemonade gestisce l'inferenza del modello, mentre OpenClaw fornisce il ciclo agentico che trasforma gli output del modello in azioni reali.

> **Prima di continuare:** OpenClaw è un agente AI altamente autonomo. Fornire a qualsiasi agente AI l'accesso al tuo sistema può portare a risultati imprevedibili o indesiderati. Procedi solo se comprendi i rischi e sei disposto ad accettare che un software autonomo agisca per tuo conto.

---

## Cosa imparerai

Al termine di questa guida sarai in grado di:

- Conoscere **Lemonade Server**
- **Installare OpenClaw** e **configurarlo per usare Lemonade Server** come backend AI.
- **Avviare il gateway di OpenClaw** e confermare che il tuo agente è pronto per l'uso.
- **Collegare un canale di comunicazione** (Discord o Telegram) in modo da poter chattare con il tuo agente da qualsiasi dispositivo.

---

## Impostazione della configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificare gli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

<!-- @os:linux -->
- Un PC con **Ubuntu 24.04+** o una distribuzione Linux compatibile basata su Debian con `apt-get`
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opzionale, per l'isolamento sandbox di OpenClaw)
- **~10–30 GB di spazio libero su disco** per i pesi del modello
<!-- @os:end -->

<!-- @os:windows -->
- Un PC con **Windows 10/11**
- Almeno **12 GB di RAM** (64 GB+ consigliati per modelli più grandi)
- **~10–30 GB di spazio libero su disco** per i pesi del modello
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opzionale, per l'isolamento sandbox di OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Scaricare e caricare il modello consigliato

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

Il modello ha una lunghezza di contesto predefinita di 262.144 token. Se riscontri errori di memoria insufficiente (OOM), valuta la possibilità di ridurre la finestra di contesto. Tuttavia, poiché Qwen3.6 sfrutta un contesto esteso per attività complesse, consigliamo di mantenere una lunghezza di contesto di almeno 128K token per preservare le capacità di ragionamento.

> **Suggerimento: disabilita il "thinking" per risposte più rapide dell'agente:** Qwen3.6-35B-A3B viene eseguito in modalità thinking per impostazione predefinita, il che aggiunge latenza prima di ogni risposta. Nei cicli agentici questo overhead si accumula rapidamente. Il repository [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornisce una configurazione già pronta che disabilita il thinking. Per utilizzarla, scarica il file e importalo:
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

Eseguiamo OpenClaw all'interno di WSL (consigliato) e lo colleghiamo a Lemonade in esecuzione nativa su Windows. Questo ti offre un ambiente shell Linux per OpenClaw, mantenendo al contempo l'accelerazione GPU di Lemonade sul lato Windows.

### Installare WSL e Ubuntu

Apri PowerShell come amministratore e installa il kernel WSL:

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

Esci da WSL e riavvialo:

```powershell
exit
wsl --shutdown
wsl
```

### Collegare Lemonade da Windows a WSL

WSL2 è eseguito in una rete virtuale. Lemonade su Windows si associa a `127.0.0.1`, che WSL non può raggiungere direttamente. Un proxy di porta di Windows inoltra il traffico dall'IP del gateway WSL al localhost di Windows.

**Trova l'IP del gateway WSL** (esegui all'interno di WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Aggiungi il proxy di porta** (esegui in PowerShell come amministratore, sostituendo `<WSL-Gateway-IP>` con il tuo IP del gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Nota: se riscontri un errore `netsh: command not found`, prova a utilizzare il nome eseguibile esplicito - `netsh.exe`

**Aggiungi una regola del firewall** (nella stessa finestra PowerShell con privilegi elevati):

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

#### Mantenere il bridge funzionante dopo un riavvio

La regola `netsh portproxy` sopravvive ai riavvii, ma l'IP del gateway WSL può cambiare dopo `wsl --shutdown` o un riavvio. Quando ciò accade, il proxy continua a puntare al vecchio IP e Lemonade diventa irraggiungibile da WSL. Se ciò accade, utilizza una delle opzioni seguenti.

**Opzione 1 (consigliata) — Ripara automaticamente il bridge.** Per evitare di doverlo fare manualmente ogni volta, utilizza un'attività pianificata che controlla il bridge a ogni avvio e accesso e lo ricostruisce solo quando l'IP del gateway è cambiato. Consulta la [guida alla riparazione automatica del bridge WSL di Lemonade](assets/RepairLemonadeWslBridge.md).


**Opzione 2 — Ripara il bridge manualmente.** Innanzitutto, ottieni l'IP del gateway WSL corrente eseguendo questo comando all'interno di WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copia questo valore; lo utilizzerai al posto di `<new-WSL-Gateway-IP>` qui sotto.

Quindi, in una **PowerShell con privilegi elevati** (esegui come amministratore), elenca le regole esistenti, elimina solo la regola Lemonade obsoleta e aggiungine una nuova con l'IP corrente:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Nell'output di `show all`, la regola Lemonade obsoleta è la voce il cui indirizzo di connessione è `127.0.0.1` sulla porta `13305`; il suo indirizzo di ascolto è il tuo `<old-WSL-Gateway-IP>`. Eliminando in base a quell'indirizzo si rimuove solo questa regola, lasciando invariate le altre regole di port-proxy presenti sulla macchina.

La regola del firewall aggiunta durante la configurazione è associata alla porta `13305` (non all'IP), quindi continua a funzionare e non è necessario ricrearla.

> **Raccomandazione:** Per evitare problemi con il gateway, consigliamo vivamente la seguente configurazione della shell:
> - I **comandi Windows** dovrebbero essere eseguiti in **PowerShell**
> - I **comandi della distribuzione WSL** dovrebbero essere eseguiti in un **Prompt dei comandi** (eseguito come **Amministratore**)

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

## Installare e configurare OpenClaw

### Installare OpenClaw
<!-- @os:windows -->
> Esegui i comandi di questa sezione all'interno del tuo **terminale WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Il flag `--no-onboard` salta la procedura guidata di configurazione interattiva; configurerai manualmente il backend del modello nel passaggio successivo, il che ti offre un controllo preciso su quale modello e server vengono utilizzati.

Apri un nuovo terminale e conferma l'installazione:

```bash
openclaw --version
```

> **Suggerimento:** Se dopo l'installazione visualizzi `command not found`, aggiungi la directory globale bin di npm al tuo PATH:
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


### Configurare OpenClaw per Utilizzare Lemonade

Esegui la procedura di onboarding non interattiva di OpenClaw.
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

> **Dimensionamento della finestra di contesto di OpenClaw:** La compattazione di OpenClaw si attiva quando `contextTokens > contextWindow − reserveTokens`. Il valore predefinito di `reserveTokensFloor` è 20.000 token, un limite minimo che sovrascrive `reserveTokens` quando questo è inferiore, quindi qualsiasi contesto del modello sotto circa 37k attiverà un ciclo di compattazione infinito. Imposta una riserva bassa e disabilita il limite minimo una sola volta nella tua configurazione e questo si applicherà a ogni modello, senza necessità di regolazioni per singolo modello:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` è un *limite minimo* (una protezione minima), non la riserva stessa; impostare solo il limite minimo non ha alcun effetto. `reserveTokensFloor: 0` disabilita la protezione in modo che il valore più basso di `reserveTokens` venga accettato.
>
> **Quando applicarlo:** Utilizza questa configurazione se la finestra di contesto effettiva del tuo modello è inferiore a circa 37k, sia perché il modello è piccolo (ad es. 8k, 16k, 32k) sia perché lo hai intenzionalmente limitato a un valore inferiore (ad es. caricando un modello da 128k ma impostando il contesto a 16k in Lemonade). Senza questa configurazione, OpenClaw entra in un ciclo di compattazione infinito all'avvio.
>
> **Modelli con contesto ampio a piena capacità:** Puoi tranquillamente saltare questo passaggio. I valori predefiniti funzionano bene: la compattazione si attiverà ben prima che la finestra si riempia e il modello avrà ampio spazio per generare risposte lunghe. Se applichi comunque questa configurazione, tieni presente che `reserveTokens: 4096` limita la lunghezza della risposta a circa 4k token, il che potrebbe troncare la generazione di file lunghi o piani dettagliati.
>
> **Dove aggiungere questa configurazione:** Inserisci il blocco `compaction` all'interno di `agents.defaults` nel tuo `openclaw.json` (solitamente in `~/.openclaw/openclaw.json`):
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
> Il resto della tua configurazione (gateway, channels, models, ecc.) rimane invariato; è necessario aggiungere solo la chiave `compaction`.
### (Consigliato) Abilita la sandboxing con Docker

OpenClaw può instradare tutte le operazioni sui file e sul codice dell'agente attraverso un container Docker isolato invece di eseguirle direttamente sul tuo host. Questo limita il raggio d'azione di qualsiasi azione non intenzionale alla sandbox, lasciando intatti il filesystem e la rete del tuo host.

Compila l'immagine della sandbox una sola volta (Docker deve essere installato):

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

Per impostazione predefinita, i container sandbox **non hanno accesso alla rete**. Consulta il [riferimento alla sandboxing](https://docs.openclaw.ai/gateway/sandboxing) per i bind mount e le sostituzioni di rete.

> #### Risoluzione dei problemi: Docker Permission Denied
> 
> Se ricevi "permission denied" durante l'esecuzione dei comandi Docker:
> 
> **Passo 1: aggiungi il tuo utente al gruppo docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Passo 2: se l'errore persiste, applica la correzione permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Quindi **riavvia** il tuo sistema.
> 
> **Correzione temporanea rapida** (viene ripristinata al riavvio):
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
## (Consigliato) Integrazione di OpenClaw con i servizi Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) fornisce un servizio di crawling web ed estrazione dei contenuti self-hosted in grado di superare queste sfide e sbloccare tutto il potenziale dell'automazione di OpenClaw.

In questa configurazione, OpenClaw viene eseguito come un insieme di container Docker gestiti con Podman. Per semplificare la gestione del ciclo di vita e l'avvio automatico, registriamo Firecrawl come servizio `systemd` a livello utente che orchestra lo stack Podman Compose sottostante. Ciò consente a OpenClaw di avviare il gateway, arrestarlo e verificare il servizio Firecrawl utilizzando i normali comandi `systemctl --user` invece di interagire direttamente con i container.

Per semplificare, abbiamo suddiviso l'intero processo in quattro passaggi:

---

### 1. Registra il servizio di sistema
Vai nella directory di configurazione utente di systemd:
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
Se l'operazione riesce, dovresti vedere il seguente output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contiene collegamenti simbolici ai servizi configurati per l'avvio automatico.

### 2. Configura Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) è ideale per chi ha bisogno del pieno controllo sul proprio ambiente di scraping ed elaborazione dei dati, ma comporta il compromesso di uno sforzo aggiuntivo di manutenzione e configurazione.

Inizia clonando il repository:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crea il file `.env` nella directory radice `/firecrawl`: 
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
Una volta fatto, scarica il file Compose di OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) e posizionalo nella directory radice `/firecrawl`:

> Questa convenzione è necessaria affinché `systemd` possa individuare e avviare il servizio correttamente, come specificato in `WorkingDirectory=${HOME}/firecrawl`.

> Puoi sempre espandere lo stack aggiungendo servizi Firecrawl aggiuntivi secondo necessità. L'elenco completo dei servizi disponibili si trova nel file ufficiale [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Avvia il servizio OpenClaw tramite Firecrawl

Prima di cedere il controllo a `systemd`, verifica che tutto funzioni correttamente eseguendo manualmente lo stack:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Se tutto è configurato correttamente, dovresti vedere avviarsi il container OpenClaw e l'output della riga di comando dovrebbe apparire simile a questo:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Una volta verificato, riporta lo stack in stato di arresto prima di procedere:
```bash
podman compose -f openclaw-compose.yaml down
```
Prima di avviare il servizio, devi assicurarti che siano impostati la proprietà e i permessi corretti sulla directory `firecrawl` e sul relativo file `.env`.
Questo è essenziale affinché il servizio possa scrivere le tue credenziali all'avvio.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Ora che tutto è stato verificato, avvia il servizio tramite `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Le azioni di OpenClaw](https://docs.openclaw.ai/) sono accessibili dall'interno del container interattivo, e la Dashboard Web è disponibile sullo stesso host e porta all'indirizzo http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Ottenere il tuo `OPENCLAW_GATEWAY_TOKEN`

Una volta che il servizio è attivo e funzionante, noterai una nuova directory `.openclaw` creata nella tua cartella home (~/.openclaw). Questa directory è bloccata per impostazione predefinita, quindi dovrai sbloccarla per recuperare il tuo token del gateway.

1. Concedi l'accesso alla directory:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Leggi il tuo token del gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Individua il valore `OPENCLAW_GATEWAY_TOKEN` nell'output.

3. Apri la dashboard del gateway nel tuo browser all'indirizzo http://127.0.0.1:18789. Incolla il tuo token quando richiesto per autenticarti.

Per arrestare il servizio, esegui:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Avviare il gateway OpenClaw

Il gateway è il processo OpenClaw che gestisce il ciclo dell'agente e serve la dashboard:

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

Poiché il gateway si collega al loopback, la dashboard esegue l'autenticazione automatica quando viene aperta dalla stessa macchina, non è necessario inserire alcun token o approvare alcun dispositivo per l'accesso locale. Dovresti vedere la dashboard di OpenClaw con il tuo modello Lemonade elencato come backend attivo.

> Se hai abilitato il sandboxing, puoi verificarlo chiedendo all'agente di eseguire `run hostname` dalla dashboard. Se vedi un breve ID container invece del nome host della tua macchina, il sandbox funziona.

**Congratulazioni, hai costruito uno stack di agenti AI completamente locale da zero.**

> **Ti serve il token del gateway?** Esegui `openclaw dashboard --no-open` per stampare l'URL della dashboard con il token incorporato (tenta anche di copiarlo negli appunti). In alternativa, il token si trova in `gateway.auth.token` all'interno di `~/.openclaw/openclaw.json`.

**Accedere alla dashboard da un altro dispositivo (tramite tunnel SSH)**

Se OpenClaw viene eseguito su una macchina remota, puoi raggiungere la sua dashboard dalla tua macchina locale tramite un tunnel SSH. Il tunnel inoltra la porta del gateway (`18789`) in modo che il tuo browser locale possa comunicare con il gateway remoto tramite `127.0.0.1`.

1. Dalla tua **macchina locale**, connettiti alla macchina remota una volta e accetta la richiesta di conferma dell'impronta digitale in modo che l'host venga aggiunto ai tuoi host conosciuti:

   ```bash
   ssh user@<host-ip>
   ```

2. Ancora sulla tua **macchina locale**, apri il tunnel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Nota:** Dopo aver inserito la password, il terminale non mostra alcun output e sembra bloccato. Questo è previsto: il flag `-N` indica a SSH di non eseguire alcun comando remoto, quindi si limita a mantenere aperto il tunnel. Lascia in esecuzione questo terminale.

3. Sulla tua **macchina locale**, apri un browser e vai su `http://127.0.0.1:18789`.

4. Sulla **macchina remota**, stampa il token del gateway e incollalo nel browser per accedere:

   ```bash
   openclaw dashboard --no-open
   ```

   Questo stampa l'URL della dashboard con il token incorporato; copia il token per accedere. (Il token è inoltre memorizzato in `gateway.auth.token` all'interno di `~/.openclaw/openclaw.json`.)

> **Approvare un dispositivo remoto:** Quando apri la dashboard da un'altra macchina o da un telefono, il browser potrebbe mostrare un ID di richiesta. Sulla **macchina remota**, elenca le richieste in sospeso:
> ```bash
> openclaw devices list
> ```
> Quindi approva la richiesta corrispondente:
> ```bash
> openclaw devices approve <requestId>
> ```
> Questo è necessario solo per dispositivi remoti o secondari; l'accesso in loopback dalla stessa macchina si autentica automaticamente. Consulta la documentazione su [Accesso remoto](https://docs.openclaw.ai/gateway/remote) per i dettagli.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Facoltativo: collegare un canale di comunicazione

Una volta avviato il gateway, puoi raggiungere il tuo agente locale da qualsiasi dispositivo. Scegli l'opzione più adatta alla tua configurazione. OpenClaw supporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) e altri canali; consulta l'elenco completo su [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opzione A: Discord

Discord richiede un server in cui **tu abbia accesso da amministratore** per aggiungere un bot. Se condividi server ma non ne possiedi uno, usa l'Opzione B (Telegram).

#### Crea un account Discord e un server

Se non hai un account Discord, registrati su [discord.com](https://discord.com). Hai anche bisogno di un server di cui sei amministratore; creane uno cliccando sull'icona **+** nella barra laterale di Discord e selezionando **Crea il mio server**. Va bene anche un server privato.

#### Crea un'applicazione Discord e un bot

1. Vai al [Discord Developer Portal](https://discord.com/developers/applications) e clicca su **New Application**. Assegnale un nome (ad es. "openclaw-bot").
2. Nella barra laterale, clicca su **Bot**. Imposta uno username per il bot.
3. Sempre nella pagina Bot, scorri fino a **Privileged Gateway Intents** e abilita:
   - **Message Content Intent** (obbligatorio)
   - **Server Members Intent** (consigliato)
4. Torna in alto e clicca su **Reset Token** per generare il token del tuo bot. Copialo.

#### Aggiungi il bot al tuo server

1. Nella barra laterale, clicca su **OAuth2/ URL Generator**.
2. In **Scopes**, abilita `bot` e `applications.commands`.
3. In **Bot Permissions**, abilita: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copia l'URL generato, incollalo nel tuo browser, seleziona il tuo server e conferma. Il bot dovrebbe ora comparire nell'elenco dei membri del tuo server.

#### Raccogli i tuoi ID

Abilita la modalità sviluppatore in Discord (**Impostazioni utente/ Avanzate/ Modalità sviluppatore**), quindi:
- Clic destro sull'icona del tuo server: **Copia ID server**
- Clic destro sul tuo avatar: **Copia ID utente**

#### Consenti i DM dai membri del server

Clic destro sull'icona del tuo server/ **Impostazioni privacy**/ attiva **Messaggi diretti**. Questo consente al bot di inviarti messaggi diretti, necessario per il passaggio di pairing.

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

> **Non affidarti a chiedere all'agente di configurare questo.** Quando il sandboxing è abilitato, l'agente non può scrivere in `~/.openclaw/openclaw.json` dall'interno del sandbox; usa invece i comandi CLI sopra riportati sull'host.

Riavvia il gateway in modo che rilevi la nuova configurazione del canale:

```bash
openclaw gateway run --bind loopback --port 18789
```

Dovresti vedere `logged in to discord as <bot-name>` nell'output del gateway entro pochi secondi.
#### Abbina il tuo account Discord

Invia un messaggio diretto al bot su Discord. Risponderà con un breve codice di associazione.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approvalo sulla macchina su cui è in esecuzione OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> I codici di associazione scadono dopo un'ora.

Ora puoi chattare con il tuo agente direttamente da Discord e affidare attività al tuo hardware locale.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opzione B: Telegram

Telegram è più semplice di Discord per la maggior parte degli utenti, non richiede un server né l'accesso da amministratore.

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

Riavvia il gateway, quindi invia un messaggio qualsiasi al tuo bot su Telegram. Approva l'associazione:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

I codici di associazione scadono dopo un'ora. Ora puoi chattare con il tuo agente tramite messaggi diretti su Telegram.

---

## Prossimi passi

Ora che il tuo agente può ricevere comandi dal tuo telefono e agire sulla tua macchina locale, ecco tre direzioni che vale la pena esplorare:

1. **Riepilogo del mercato azionario**: Programma OpenClaw per recuperare dati da API finanziarie a intervalli fissi, riassumere i movimenti della giornata con il tuo modello locale e inviare un riepilogo al tuo telefono ogni mattina tramite il canale scelto.

2. **Monitor per il fine-tuning**: Avvia da remoto un job di addestramento tramite Telegram o Discord, quindi fai in modo che l'agente segua il log di addestramento e riporti periodicamente i valori di loss, l'utilizzo della GPU e l'utilizzo del disco al tuo telefono. Se l'esecuzione si blocca o la VRAM ha un picco, lo scopri immediatamente senza dover essere davanti alla macchina.

3. **IOT con un VLM locale**: Punta una telecamera verso la porta d'ingresso, esegui un modello di visione su Lemonade e fai in modo che OpenClaw analizzi i frame su richiesta o in base a un trigger. Chiedi "sono arrivati pacchi oggi?" dal tuo telefono e ottieni una risposta diretta dal tuo hardware.

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