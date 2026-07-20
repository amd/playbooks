<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# OpenClaw uitvoeren met Lemonade Server als backend

## Overzicht

[**OpenClaw**](https://openclaw.ai/) is een autonome AI-agent die code kan schrijven en uitvoeren, bestanden kan beheren en complexe taken met meerdere stappen namens u kan uitvoeren. In tegenstelling tot een chatassistent die alleen vragen beantwoordt, onderneemt OpenClaw daadwerkelijke acties op uw systeem, wat betekent dat het een snelle, capabele AI-backend nodig heeft die de veeleisende agentlus kan bijbenen.

[**Lemonade Server**](https://lemonade-server.ai/) is die backend. Het is een open-source lokale inferentieserver die GenAI-modellen rechtstreeks op uw hardware uitvoert en ze beschikbaar stelt via de industriestandaard OpenAI API.

Samen vormen ze een volledig lokale AI-agentstack: Lemonade verzorgt de modelinferentie en OpenClaw biedt de agentlus die modeluitvoer omzet in daadwerkelijke acties.

> **Voordat u verdergaat:** OpenClaw is een zeer autonome AI-agent. Het geven van toegang tot uw systeem aan een AI-agent kan leiden tot onvoorspelbare of onbedoelde resultaten. Ga alleen verder als u de risico's begrijpt en er comfortabel mee bent dat autonome software namens u handelt.

---

## Wat u leert

Aan het einde van dit playbook kunt u:

- Meer te weten komen over **Lemonade Server**
- **OpenClaw installeren** en **het instellen op Lemonade Server** als AI-backend.
- **De OpenClaw-gateway starten** en bevestigen dat uw agent klaar is om te werken.
- **Een communicatiekanaal verbinden** (Discord of Telegram) zodat u vanaf elk apparaat met uw agent kunt chatten.

---

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

<!-- @os:linux -->
- Een pc met **Ubuntu 24.04+** of een compatibele op Debian gebaseerde Linux-distributie met `apt-get`
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (optioneel, voor het sandboxen van OpenClaw)

- **~10-30 GB vrije schijfruimte** voor modelgewichten
<!-- @os:end -->
<!-- @os:windows -->
- Een pc met **Windows 10/11**
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- **~10-30 GB vrije schijfruimte** voor modelgewichten
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (optioneel, voor het sandboxen van OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Het aanbevolen model ophalen en laden

Het aanbevolen model voor dit playbook is **Qwen3.6-35B-A3B-GGUF** van Unsloth, een krachtig MoE-model met een contextvenster van 263k tokens dat goed geschikt is voor agent-werklasten. Dit model gebruikt UD-Q4_K_XL-kwantisering. Haal het nu op:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Laad het vervolgens met een groot contextvenster en sla deze instelling op voor toekomstige uitvoeringen:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Het model heeft standaard een contextlengte van 262.144 tokens. Als u out-of-memory (OOM) fouten tegenkomt, overweeg dan om het contextvenster te verkleinen. Omdat Qwen3.6 echter uitgebreide context gebruikt voor complexe taken, adviseren wij om een contextlengte van ten minste 128K tokens aan te houden om het denkvermogen te behouden.

> **Tip: Denkmodus uitschakelen voor snellere agent-reacties:** Qwen3.6-35B-A3B draait standaard in denkmodus, wat vóór elke reactie extra latentie toevoegt. Bij agentlussen loopt deze overhead snel op. De repo [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) biedt een kant-en-klare configuratie die denken uitschakelt. Om deze te gebruiken, downloadt u het bestand en importeert u het:
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

## WSL instellen

We voeren OpenClaw uit binnen WSL (aanbevolen) en verbinden het met Lemonade dat native op Windows draait. Dit geeft u een Linux-shellomgeving voor OpenClaw, terwijl de GPU-versnelling van Lemonade aan de Windows-kant blijft.

### WSL en Ubuntu installeren

Open PowerShell als beheerder en installeer de WSL-kernel:

```powershell
wsl --install --no-distribution
```

Installeer vervolgens Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### systemd inschakelen in WSL

Voer dit uit binnen de Ubuntu-terminal:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Start WSL opnieuw:

```powershell
wsl --shutdown
wsl
```

### Lemonade van Windows naar WSL bruggen

WSL2 draait in een virtueel netwerk. Lemonade op Windows bindt aan `127.0.0.1`, wat WSL niet rechtstreeks kan bereiken. Een Windows-poortproxy stuurt verkeer van het WSL-gateway-IP door naar Windows localhost.

**Zoek uw WSL-gateway-IP** (voer uit binnen WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Voeg de poortproxy toe** (voer uit in PowerShell als beheerder, waarbij u `<WSL-Gateway-IP>` vervangt door uw WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Voeg een firewallregel toe** (dezelfde verhoogde PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Controleer vanuit WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Als u het model Qwen3.6-35B-A3B-GGUF al in de vorige stap heeft geladen, ziet u JSON-uitvoer zoals deze:

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

> De `netsh portproxy`-regel overleeft herstarts, maar het WSL-gateway-IP kan veranderen na `wsl --shutdown`. Als Lemonade niet meer bereikbaar is vanuit WSL na een herstart, haalt u het bijgewerkte gateway-IP op en werkt u de proxy bij met dit nieuwe IP.

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

## OpenClaw installeren en configureren

### OpenClaw installeren
<!-- @os:windows -->
> Voer de opdrachten in deze sectie uit binnen uw **WSL-terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

De vlag `--no-onboard` slaat de interactieve installatiewizard over; u configureert de modelbackend handmatig in de volgende stap, wat u nauwkeurige controle geeft over welk model en welke server worden gebruikt.

Open een nieuwe terminal en bevestig de installatie:

```bash
openclaw --version
```

> **Tip:** Als u na de installatie `command not found` ziet, voeg dan de globale bin-directory van npm toe aan uw PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Om dit permanent te maken, voegt u de bovenstaande regel toe aan uw `~/.bashrc`- of `~/.zshrc`-bestand.

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
### OpenClaw configureren om Lemonade te gebruiken

Voer de niet-interactieve onboarding van OpenClaw uit.
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

Dit commando schrijft de configuratie van OpenClaw naar `~/.openclaw/openclaw.json`.

> **Formaat van het contextvenster van OpenClaw:** de compactie van OpenClaw wordt geactiveerd wanneer `contextTokens > contextWindow − reserveTokens`. De standaard `reserveTokensFloor` is 20.000 tokens, een ondergrens die `reserveTokens` overschrijft wanneer die lager is, dus elk modelcontext onder ~37k activeert een oneindige compactielus. Stel eenmalig in je configuratie een lage reserve in en schakel de ondergrens uit, en dit geldt dan voor elk model, zonder afstemming per model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` is een *ondergrens* (minimale bescherming), niet de reserve zelf; alleen de ondergrens instellen heeft geen effect. `reserveTokensFloor: 0` schakelt de bescherming uit zodat de lagere `reserveTokens` wordt geaccepteerd.
>
> **Wanneer dit toe te passen:** gebruik deze configuratie als het effectieve contextvenster van je model onder ~37k ligt, hetzij omdat het model klein is (bijv. 8k, 16k, 32k), hetzij omdat je het bewust hebt beperkt tot een lagere waarde (bijv. een 128k-model laden maar de context instellen op 16k in Lemonade). Zonder dit komt OpenClaw bij het opstarten in een oneindige compactielus terecht.
>
> **Modellen met een groot contextvenster op volledige context:** dit kun je volledig overslaan. De standaardinstellingen werken prima, compactie treedt in werking ruim voordat het venster vol raakt en het model heeft voldoende ruimte om lange antwoorden te genereren. Als je dit toch toepast, houd er dan rekening mee dat `reserveTokens: 4096` de antwoordlengte beperkt tot ~4k tokens, wat het genereren van lange bestanden of gedetailleerde plannen kan afkappen.
>
> **Waar dit toe te voegen:** plaats het blok `compaction` binnen `agents.defaults` in je `openclaw.json` (meestal op `~/.openclaw/openclaw.json`):
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
> De rest van je configuratie (gateway, kanalen, modellen, enz.) blijft ongewijzigd, alleen de sleutel `compaction` hoeft te worden toegevoegd.

### (Aanbevolen) Docker Sandboxing inschakelen

OpenClaw kan alle bestands- en codebewerkingen van de agent via een geïsoleerde Docker-container laten verlopen in plaats van deze direct op je host uit te voeren. Dit beperkt de impact van elke onbedoelde actie tot de sandbox, waardoor het bestandssysteem en netwerk van je host onaangetast blijven.

Bouw de sandboximage eenmalig (Docker moet geïnstalleerd zijn):

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

Voer dit uit om de sleutel `sandbox` toe te voegen binnen het bestaande blok `agents.defaults` in `~/.openclaw/openclaw.json`:

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

Sandboxcontainers hebben standaard **geen netwerktoegang**. Zie de [sandboxing-referentie](https://docs.openclaw.ai/gateway/sandboxing) voor bind mounts en netwerk-overrides.

> #### Probleemoplossing: Docker-toestemming geweigerd
> 
> Als je "permission denied" krijgt bij het uitvoeren van Docker-commando's:
> 
> **Stap 1: Voeg je gebruiker toe aan de docker-groep**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Stap 2: Als de fout aanhoudt, pas de permanente oplossing toe**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> **Start** je systeem daarna opnieuw op.
> 
> **Snelle tijdelijke oplossing** (wordt teruggezet na een herstart):
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

### De OpenClaw Gateway starten

De gateway is het OpenClaw-proces dat de agent-loop beheert en het dashboard bedient:

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

Om het dashboard te openen, voer dit uit in een tweede terminal terwijl de gateway nog actief is:

```bash
openclaw dashboard
```

Omdat de gateway aan loopback gebonden is, verifieert het dashboard zich automatisch wanneer het vanaf dezelfde machine wordt geopend, er is geen tokeninvoer of apparaatgoedkeuring nodig voor lokale toegang. Je zou nu het OpenClaw-dashboard moeten zien met je Lemonade-model vermeld als actieve backend.

> Als je sandboxing hebt ingeschakeld, kun je dit verifiëren door de agent te vragen `run hostname` uit te voeren vanuit het dashboard. Als je een korte container-ID ziet in plaats van de hostnaam van je machine, werkt de sandbox.

**Gefeliciteerd, je hebt vanaf nul een volledig lokale AI-agentstack gebouwd.**

> **Heb je de gateway-token nodig?** Voer `openclaw dashboard --no-open` uit om de dashboard-URL met daarin de token af te drukken (er wordt ook geprobeerd deze naar je klembord te kopiëren). Als alternatief bevindt de token zich op `gateway.auth.token` in `~/.openclaw/openclaw.json`.
>
> **Een extern apparaat goedkeuren:** wanneer je het dashboard opent vanaf een tweede machine of telefoon, toont de browser een aanvraag-ID. Voer op de machine waarop de gateway draait het volgende uit:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dit is alleen nodig voor externe of secundaire apparaten, toegang via loopback vanaf dezelfde machine verifieert zichzelf automatisch.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optioneel: Een communicatiekanaal koppelen

Zodra de gateway actief is, kun je je lokale agent vanaf elk apparaat bereiken. Kies de optie die bij jouw situatie past. OpenClaw ondersteunt [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) en andere kanalen, zie de volledige lijst op [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Optie A: Discord

Voor Discord is een server nodig waar **jij beheerdersrechten hebt** om een bot toe te voegen. Als je servers deelt maar er geen bezit, gebruik dan in plaats daarvan Optie B (Telegram).
#### Maak een Discord-account en server aan

Als je geen Discord-account hebt, meld je dan aan op [discord.com](https://discord.com). Je hebt ook een server nodig waarvan je beheerder bent; maak er een door op het **+**-icoon in de Discord-zijbalk te klikken en **Create My Own** te selecteren. Een privéserver volstaat.

#### Maak een Discord-applicatie en bot aan

1. Ga naar het [Discord Developer Portal](https://discord.com/developers/applications) en klik op **New Application**. Geef het een naam (bijv. "openclaw-bot").
2. Klik in de zijbalk op **Bot**. Stel een gebruikersnaam in voor de bot.
3. Scroll op dezelfde Bot-pagina naar **Privileged Gateway Intents** en schakel in:
   - **Message Content Intent** (vereist)
   - **Server Members Intent** (aanbevolen)
4. Scroll terug naar boven en klik op **Reset Token** om je bot-token te genereren. Kopieer deze.

#### Voeg de bot toe aan je server

1. Klik in de zijbalk op **OAuth2/ URL Generator**.
2. Schakel onder **Scopes** `bot` en `applications.commands` in.
3. Schakel onder **Bot Permissions** het volgende in: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieer de gegenereerde URL, plak deze in je browser, selecteer je server en bevestig. De bot zou nu moeten verschijnen in de ledenlijst van je server.

#### Verzamel je ID's

Schakel Developer Mode in bij Discord (**User Settings/ Advanced/ Developer Mode**), en doe vervolgens het volgende:
- Rechtsklik op je server-icoon: **Copy Server ID**
- Rechtsklik op je eigen avatar: **Copy User ID**

#### Sta DM's van servermedewerkers toe

Rechtsklik op je server-icoon/ **Privacy Settings**/ schakel **Direct Messages** in. Hierdoor kan de bot je een DM sturen, wat nodig is voor de koppelingsstap.

#### Configureer OpenClaw voor Discord

Sla je bot-token op als omgevingsvariabele en maak vervolgens één patchbestand aan dat Discord inschakelt, naar de token verwijst en je server op de allowlist zet. Vervang `<server_id>` en `<user_id>` door de hierboven verzamelde ID's.

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

> **Vertrouw er niet op dat je de agent vraagt dit te configureren.** Wanneer sandboxing is ingeschakeld, kan de agent niet schrijven naar `~/.openclaw/openclaw.json` vanuit de sandbox; gebruik in plaats daarvan de bovenstaande CLI-commando's op de host.

Herstart de gateway zodat deze de nieuwe kanaalconfiguratie oppikt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Je zou binnen enkele seconden `logged in to discord as <bot-name>` moeten zien in de gateway-output.

#### Koppel je Discord-account

Stuur de bot een DM in Discord. Deze antwoordt met een korte koppelcode.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Keur dit goed op de machine waarop OpenClaw draait:
```bash
openclaw pairing approve discord <CODE>
```

> Koppelcodes verlopen na een uur.

Je kunt nu direct vanuit Discord met je agent chatten en taken uitbesteden aan je lokale hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Optie B: Telegram

Telegram is voor de meeste gebruikers eenvoudiger dan Discord; er is geen server en geen beheerderstoegang voor nodig.

#### Maak een Telegram-bot aan

1. Open Telegram en stuur een bericht naar **@BotFather**.
2. Stuur `/newbot` en volg de aanwijzingen. Bewaar het bot-token dat je krijgt.

#### Configureer OpenClaw voor Telegram

Sla het token op als omgevingsvariabele:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Voeg de kanaalconfiguratie toe aan `~/.openclaw/openclaw.json` (of patch deze via het dashboard):

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

Herstart de gateway en stuur je bot vervolgens een willekeurig bericht in Telegram. Keur de koppeling goed:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Koppelcodes verlopen na een uur. Je kunt nu via Telegram-DM met je agent chatten.

---

## Volgende stappen

Nu je agent commando's kan ontvangen vanaf je telefoon en actie kan ondernemen op je lokale machine, zijn hier drie richtingen die het waard zijn om te verkennen:

1. **Samenvatter van de aandelenmarkt**: Plan OpenClaw in om op vaste intervallen data op te halen bij financiële API's, de bewegingen van de dag samen te vatten met je lokale model en elke ochtend een overzicht naar je telefoon te sturen via het door jou gekozen kanaal.

2. **Fine-tuning monitor**: Start op afstand een trainingsjob via Telegram of Discord, en laat de agent vervolgens het trainingslog volgen en periodiek de loss-waarden, GPU-gebruik en schijfgebruik terugmelden naar je telefoon. Als de run vastloopt of het VRAM-gebruik piekt, kom je dat direct te weten zonder bij de machine te hoeven zijn.

3. **IOT met een lokaal VLM**: Richt een camera op je voordeur, draai een visiemodel op Lemonade en laat OpenClaw op verzoek of op basis van een trigger frames analyseren. Vraag vanaf je telefoon "zijn er vandaag pakketjes bezorgd?" en krijg een rechtstreeks antwoord van je eigen hardware.