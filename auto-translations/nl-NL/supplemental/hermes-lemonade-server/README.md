<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Hermes Agent lokaal uitvoeren met Lemonade Server

## Overzicht

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) is een zelflerende AI-agent gebouwd door Nous Research. Het heeft een ingebouwde leerlus, creëert vaardigheden op basis van ervaring, bouwt een blijvend geheugen op van wie u bent over verschillende sessies heen, en kan geplande automatiseringen namens u uitvoeren. In tegenstelling tot een eenvoudige chatassistent onderneemt Hermes echte acties: het uitvoeren van shellopdrachten, het schrijven van bestanden, het browsen op het web en het delegeren van parallelle werkstromen naar subagenten.

[**Lemonade Server**](https://lemonade-server.ai/) is de lokale inferentiebackend die dit aandrijft. Het is een open-source server die GenAI-modellen rechtstreeks op uw AMD-hardware uitvoert en deze beschikbaar stelt via de industriestandaard OpenAI API.

Samen vormen ze een volledig lokale AI-agentstack: Lemonade verzorgt de modelinferentie op uw GPU, en Hermes biedt de agentlus, geheugen, vaardigheden en messaginggateway.

> **Voordat u verdergaat:** Hermes Agent is een sterk autonome AI-agent. Het geven van toegang aan een AI-agent tot uw systeem kan leiden tot onvoorspelbare of onbedoelde resultaten. Ga alleen verder als u de risico's begrijpt en er comfortabel mee bent dat autonome software namens u handelt.

---

## Wat u zult leren

Aan het einde van dit playbook kunt u het volgende:

- **Hermes Agent installeren** en deze richten op **Lemonade Server** als AI-backend.
- **(Aanbevolen) Docker/Podman-sandboxing inschakelen** om de acties van de agent te isoleren van uw host.
- **De Hermes-gateway starten** en bevestigen dat uw agent gereed is.
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
- Een pc met **Ubuntu 24.04+** of een compatibele Debian-gebaseerde Linux-distributie met `apt-get`
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- **~10–30 GB vrije schijfruimte** voor modelgewichten
- [Podman](https://podman.io/docs/installation) (optioneel, voor sandboxing van Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Een pc met **Windows 10/11**
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- **~10–30 GB vrije schijfruimte** voor modelgewichten
- Podman (optioneel, voor sandboxing van Hermes Agent). Installeer binnen WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman is vooraf geïnstalleerd op Halo Box en er is geen installatie nodig
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Het aanbevolen model ophalen en laden

Het aanbevolen model voor dit playbook is **Qwen3.6-35B-A3B-GGUF** van Unsloth, een sterk MoE-model met een contextvenster van 263k tokens dat goed geschikt is voor agentworkloads. Dit model gebruikt UD-Q4_K_XL-kwantisatie. Haal het nu op:

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

Het model heeft een standaard contextlengte van 262.144 tokens. Als u out-of-memory (OOM)-fouten tegenkomt, overweeg dan om het contextvenster te verkleinen.

> **Tip: Schakel denken uit voor snellere agentreacties:** Qwen3.6-35B-A3B draait standaard in denkmodus, wat vóór elke reactie latentie toevoegt. Voor agentlussen loopt deze overhead snel op. De [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) repository biedt een kant-en-klare configuratie die denken uitschakelt. Download hiervoor het bestand en importeer het:
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

## WSL instellen

We voeren Hermes Agent uit binnen WSL en verbinden het met Lemonade die native op Windows draait. Dit geeft u een Linux-shellomgeving voor Hermes terwijl de GPU-versnelling van Lemonade aan de Windows-kant blijft.

### WSL en Ubuntu installeren

Open PowerShell als Administrator en installeer de WSL-kernel:

```powershell
wsl --install --no-distribution
```

Installeer vervolgens Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Systemd inschakelen in WSL

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

### Lemonade bruggen van Windows naar WSL

WSL2 draait in een virtueel netwerk. Lemonade op Windows bindt zich aan `127.0.0.1`, wat WSL niet rechtstreeks kan bereiken. Een Windows-poortproxy stuurt verkeer door van het WSL-gatewayadres naar Windows localhost.

**Zoek uw WSL-gatewayadres** (voer uit binnen WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Voeg de poortproxy toe** (voer uit in PowerShell als Administrator, vervang `<WSL-Gateway-IP>` door uw WSL-gatewayadres):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Voeg een firewallregel toe** (dezelfde verhoogde PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifieer vanuit WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Als u het Qwen3.6-35B-A3B-GGUF-model al hebt geladen in de vorige stap, zou u JSON-uitvoer moeten zien met een lijst van uw geladen model.

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

> De `netsh portproxy`-regel blijft behouden na herstarten, maar het WSL-gatewayadres kan veranderen na `wsl --shutdown`. Als Lemonade onbereikbaar wordt vanuit WSL na een herstart, haal dan het bijgewerkte gatewayadres op en werk de proxy bij met dit nieuwe adres.

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

## Hermes Agent installeren

<!-- @os:windows -->
> Voer de opdrachten in dit gedeelte uit binnen uw **WSL-terminal**, tenzij anders aangegeven.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

De vlag `--skip-setup` slaat de interactieve installatiewizard over, zodat u de modelbackend handmatig kunt configureren in de volgende stap.

Herlaad uw shell:

```bash
source ~/.bashrc
```

Bevestig de installatie:

```bash
hermes --version
```

Voer een zelfdiagnose uit om alle afhankelijkheden te controleren:

```bash
hermes doctor
```

> **Tip:** Als u `command not found` ziet na installatie, voeg Hermes dan toe aan uw PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Om dit permanent te maken, voegt u de bovenstaande regel toe aan uw `~/.bashrc` of `~/.zshrc`.

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
## Configureer Hermes voor gebruik met Lemonade

Hermes slaat zijn modelconfiguratie op in `~/.hermes/config.yaml`. U kunt ofwel de interactieve `hermes model`-picker gebruiken, of de configuratie rechtstreeks schrijven.

### Optie 1: Interactieve picker

<!-- @os:windows -->
> Voer het volgende uit binnen uw **WSL-terminal**.
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

Wanneer u dit wordt gevraagd:

1. Selecteer **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** gebruik het WSL-gateway-IP: voer `ip route show default | awk '{print $3}' | head -1` uit binnen WSL om dit op te halen, en voer vervolgens `http://<WSL-Gateway-IP>:13305/api/v1` in
<!-- @os:end -->
3. **API-sleutel:** `lemonade`
4. **API-compatibiliteitsmodus:** `1` (Auto-detect)
5. **Selecteer model:** kies `Qwen3.6-35B-A3B-GGUF` uit de lijst
6. **Contextlengte in tokens:** `262144`
7. **Weergavenaam:** `local-lemonade` (of een naam naar keuze)

`hermes model` slaat zowel de actieve modelselectie op als een benoemde `custom_providers`-vermelding die de contextlengte samen met het endpoint opslaat. Het resultaat in `~/.hermes/config.yaml` ziet er als volgt uit:

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

### Optie 2: Configuratie rechtstreeks schrijven

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

Haal binnen uw WSL-terminal het IP-adres van de Windows-host op en schrijf de configuratie:

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

## (Aanbevolen) Podman-sandboxing inschakelen

Hermes Agent kan alle shell- en bestandsbewerkingen van de agent via een geïsoleerde container laten verlopen in plaats van deze rechtstreeks op uw host uit te voeren. Dit beperkt de impact van onbedoelde acties tot de sandbox, zodat het bestandssysteem en netwerk van uw host ongewijzigd blijven.

Bouw een lichtgewicht sandbox-image:

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
Ga naar uw WSL-terminal:

```powershell
wsl -d Ubuntu-24.04
```

Bouw vervolgens een lichtgewicht sandbox-image:

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

Configureer vervolgens Hermes om Podman als container-runtime te gebruiken en stel de terminal-backend in:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> De `terminal.backend` blijft `docker`.
> `HERMES_DOCKER_BINARY` is wat Hermes vertelt om Podman als runtime te gebruiken in plaats van Docker.

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

Hermes zal nu een persistente sandbox-container opstarten en alle `terminal`- en bestandsgereedschap-aanroepen hierdoorheen leiden. De container deelt de levensduur van het Hermes-proces, wordt hergebruikt voor alle tool-aanroepen, en wordt vernietigd wanneer Hermes wordt afgesloten.

> **Controleer of de sandbox werkt:** Start Hermes (`hermes`) en vraag het om `run hostname` uit te voeren - u zou een korte container-ID moeten zien in plaats van de hostnaam van uw machine. U kunt het ook vragen om `rm -rf <path-to-a-dummy-file/folder>` uit te voeren: Hermes bevestigt de verwijdering, maar de map blijft aanwezig op uw host. Het commando werd uitgevoerd binnen de geïsoleerde `$HOME` van de container, niet die van u.

> **Sterkere isolatie nodig?** Hermes biedt ook een officiële Docker-image (`nousresearch/hermes-agent`) die het volledige agentproces binnen een container uitvoert - gateway, tools, en al het overige. Zie de [Hermes Docker-documentatie](https://hermes-agent.nousresearch.com/docs/user-guide/docker) voor installatiedetails.

---

<!-- @os:linux -->
## (Aanbevolen) Hermes-integratie met Firecrawl-services

Hermes kan websites doorzoeken en inhoud extraheren met behulp van zijn ingebouwde webtools. Veel moderne websites gebruiken echter botdetectiesystemen, die eenvoudige HTTP-verzoeken blokkeren en in plaats daarvan uitdagingspagina's retourneren in plaats van de daadwerkelijke inhoud. Hierdoor kan Hermes mogelijk geen betrouwbare informatie extraheren van deze sites.

Om deze beperking te overwinnen, biedt [Firecrawl](https://docs.firecrawl.dev/introduction) een zelf gehoste web-crawling- en content-extractieservice die deze uitdagingen kan omzeilen en het volledige potentieel van Hermes-automatisering ontgrendelt.

In deze opstelling draait Firecrawl als een set Docker-containers die worden beheerd met Podman. Om het levenscyclusbeheer en automatisch opstarten te vereenvoudigen, registreren we Firecrawl als een gebruikersniveau-`systemd`-service die de onderliggende Podman Compose-stack orkestreert. Hierdoor kan Hermes de Firecrawl-service starten, stoppen en verifiëren met standaard `systemctl --user`-commando's in plaats van rechtstreeks met containers te werken.

Om het overzichtelijk te houden, hebben we het hele proces opgesplitst in vier stappen:

---

### 1. Registreer de systeemservice
Navigeer naar de systemd-gebruikersconfiguratiemap:
```bash
cd ~/.config/systemd/user
```
Maak een nieuw bestand aan met de naam `firecrawl.service` en open het.
```bash
nano firecrawl.service
```
Kopieer en plak de volgende configuratie:
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
Op dit punt is de service gedefinieerd maar nog niet geregistreerd bij `systemd`.
Zorg ervoor dat de bestandsnaam exact overeenkomt met wat u hierboven hebt gemaakt, en voer vervolgens uit:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Als dit gelukt is, ziet u de volgende uitvoer:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` bevat symbolische links naar services die zijn geconfigureerd om automatisch te starten.

### 2. Configureer Firecrawl voor uw service

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) is ideaal voor wie volledige controle wil over de scraping- en gegevensverwerkingsomgeving, maar dit gaat gepaard met extra onderhouds- en configuratie-inspanningen.

Begin met het klonen van de repository:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Maak `.env` aan in de root van de `/firecrawl`-map:
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
> Stel `BULL_AUTH_KEY` in op een sterk geheim, vooral bij een implementatie die bereikbaar is vanuit niet-vertrouwde netwerken.
### 3. Hermes implementeren via Compose

Zorg er, voordat u verdergaat, voor dat u de nieuwste Hermes Docker-image hebt gepulld:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Zodra dat is gedaan, downloadt u het Hermes Compose-bestand [hermes-compose.yaml](assets/hermes-compose.yaml) en plaatst u het in de hoofdmap `/firecrawl`:

> Deze conventie is vereist zodat `systemd` de service correct kan vinden en starten, zoals opgegeven in `WorkingDirectory=${HOME}/firecrawl`.

> U kunt de stack altijd uitbreiden door extra Firecrawl-services toe te voegen indien nodig. De volledige lijst met beschikbare services vindt u in het officiële [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)-bestand.

### 4. Start de Hermes-service via Firecrawl 

Voordat u de controle overdraagt aan `systemd`, controleert u eerst of alles correct werkt door de stack handmatig uit te voeren:
```bash
podman compose -f hermes-compose.yaml up -d
```
Als alles correct is geconfigureerd, ziet u de Hermes-container opstarten en zou de uitvoer op de opdrachtregel er ongeveer zo uit moeten zien:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Sluit de stack, zodra u dit hebt geverifieerd, weer af voordat u verdergaat:
```bash
podman compose -f hermes-compose.yaml down
```
Nu alles is geverifieerd, start u de service via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[De Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) is toegankelijk vanuit de interactieve container, en het webdashboard is op dezelfde host en poort beschikbaar op http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Om de service te stoppen, voert u het volgende uit:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Start rechtstreeks een interactieve CLI-sessie: 

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

**Gefeliciteerd, u hebt een volledig lokale AI-agentstack gebouwd.**

### Webdashboard

Hermes bevat een browsergebaseerde interface voor het beheren van configuratie, API-sleutels, modellen, sessies, geheugen en cron-taken. Open een tweede terminal terwijl de gateway of CLI actief is en start deze met:

```bash
hermes dashboard
```

Hiermee wordt een lokale server gestart en wordt `http://127.0.0.1:9119` in uw browser geopend. Raadpleeg de [dashboarddocumentatie](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) voor de volledige functiereferentie.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Optioneel: een communicatiekanaal koppelen

Zodra de gateway actief is, kunt u vanaf elk apparaat toegang krijgen tot uw lokale agent. Hermes ondersteunt [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) en andere platforms

---

### Discord

Voor Discord is een server vereist waarop **u beheerderstoegang hebt** om een bot toe te voegen. Als u servers deelt maar er zelf geen bezit, gebruikt u in plaats daarvan Telegram.

#### Een Discord-applicatie en -bot maken

1. Ga naar het [Discord Developer Portal](https://discord.com/developers/applications) en klik op **New Application**. Geef het een naam (bijvoorbeeld "hermes-bot").
2. Klik in de zijbalk op **Bot**. Stel een gebruikersnaam in voor de bot.
3. Blijf op de Bot-pagina, scroll naar **Privileged Gateway Intents** en schakel het volgende in:
   - **Message Content Intent** (vereist)
   - **Server Members Intent** (aanbevolen)
4. Scroll terug naar boven en klik op **Reset Token** om uw bot-token te genereren. Kopieer deze.

#### De bot aan uw server toevoegen

1. Klik in de zijbalk op **OAuth2 / URL Generator**.
2. Schakel onder **Scopes** `bot` en `applications.commands` in.
3. Schakel onder **Bot Permissions** het volgende in: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieer de gegenereerde URL, plak deze in uw browser, selecteer uw server en bevestig.

#### Uw ID's verzamelen en DM's toestaan

Schakel Developer Mode in Discord in (**User Settings / Advanced / Developer Mode**), en ga vervolgens als volgt te werk:
- Klik met de rechtermuisknop op uw server-icoon: **Copy Server ID**
- Klik met de rechtermuisknop op uw eigen avatar: **Copy User ID**

Klik met de rechtermuisknop op uw server-icoon / **Privacy Settings** / schakel **Direct Messages** in. Dit is vereist voor de koppelingsstap.

#### Hermes configureren voor Discord

Voeg het volgende toe aan `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Start vervolgens de gateway:

```bash
hermes gateway
```

De bot zou binnen enkele seconden online moeten komen in Discord. Stuur er een bericht naar, hetzij een DM, hetzij in een kanaal dat de bot kan zien.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Een Telegram-bot maken

1. Open Telegram en stuur een bericht naar **@BotFather**.
2. Stuur `/newbot` en volg de instructies. Bewaar het bot-token dat u ontvangt.

#### Hermes configureren voor Telegram

Voeg het volgende toe aan `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Weet u uw Telegram-gebruikers-ID niet?** Stuur een bericht naar [@userinfobot](https://t.me/userinfobot) in Telegram, dan antwoordt deze met uw numerieke ID.

Start vervolgens de gateway:

```bash
hermes gateway
```

Stuur uw bot een bericht in Telegram om te testen. U kunt nu met uw agent chatten via een Telegram-DM. Raadpleeg de [volledige installatiehandleiding voor Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) voor webhookmodus en geavanceerde opties.

---

## Volgende stappen

Nu uw agent opdrachten van uw telefoon kan ontvangen en daarop kan reageren op uw lokale machine, volgen hier drie richtingen die het verkennen waard zijn:

1. **Geautomatiseerd onderzoeksoverzicht**: Plan Hermes zo in dat het elke ochtend het web doorzoekt naar onderwerpen die u interesseren, de bevindingen samenvat met uw lokale model en een overzicht naar uw telefoon stuurt via Telegram of Discord, dit alles draaiend op uw eigen hardware zonder cloudkosten.

2. **Codebeoordeling op aanvraag**: Wijs Hermes naar een GitHub-repository, vraag het om openstaande pull requests te beoordelen en laat het opmerkingen of een samenvatting terugsturen naar uw chat. Met de Docker-terminalbackend worden alle git-bewerkingen binnen de sandbox uitgevoerd, zodat uw host schoon blijft.

3. **Lokale bestandsassistent**: Geef Hermes toegang tot een werkmap en vraag het om bestanden op aanvraag te organiseren, hernoemen, samenvatten of transformeren vanaf uw telefoon. Omdat de Docker-terminalbackend alle schrijfbewerkingen beperkt tot de sandbox-werkruimte, worden onbedoelde destructieve bewerkingen ingeperkt.