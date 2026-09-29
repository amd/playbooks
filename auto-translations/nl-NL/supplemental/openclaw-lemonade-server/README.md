<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Voer OpenClaw uit met Lemonade Server als backend

## Overzicht

[**OpenClaw**](https://openclaw.ai/) is een autonome AI-agent die code kan schrijven en uitvoeren, bestanden kan beheren en complexe meerstapstaken namens jou kan uitvoeren. In tegenstelling tot een chatassistent die alleen vragen beantwoordt, onderneemt OpenClaw daadwerkelijke acties op je systeem, wat betekent dat het een snelle, krachtige AI-backend nodig heeft die de veeleisende agent-lus kan bijbenen.

[**Lemonade Server**](https://lemonade-server.ai/) is die backend. Het is een open-source lokale inferentieserver die GenAI-modellen direct op je hardware uitvoert en deze beschikbaar stelt via de industriestandaard OpenAI API.

Samen vormen ze een volledig lokale AI-agentstack: Lemonade verzorgt de modelinferentie en OpenClaw biedt de agent-lus die modeluitvoer omzet in daadwerkelijke acties.

> **Voordat je verdergaat:** OpenClaw is een zeer autonome AI-agent. Het geven van toegang tot je systeem aan een AI-agent kan onvoorspelbare of onbedoelde resultaten opleveren. Ga alleen verder als je de risico's begrijpt en het ermee eens bent dat autonome software namens jou handelt.

---

## Wat je zult leren

Aan het einde van dit playbook kun je het volgende:

- Meer te weten komen over **Lemonade Server**
- **OpenClaw installeren** en **het naar Lemonade Server laten wijzen** als AI-backend.
- **De OpenClaw-gateway starten** en bevestigen dat je agent klaar is om te werken.
- **Een communicatiekanaal verbinden** (Discord of Telegram) zodat je vanaf elk apparaat met je agent kunt chatten.

---

<!-- @device:halo_box,halo,stx,krk -->
## De geheugenconfiguratie instellen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software vereisten installeren

<!-- @os:linux -->
- Een pc met **Ubuntu 24.04+** of een compatibele Debian-gebaseerde Linux-distributie met `apt-get`
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Optioneel, voor het sandboxen van OpenClaw)
- **~10–30 GB vrije schijfruimte** voor modelgewichten
<!-- @os:end -->

<!-- @os:windows -->
- Een pc met **Windows 10/11**
- Ten minste **12 GB RAM** (64 GB+ aanbevolen voor grotere modellen)
- **~10–30 GB vrije schijfruimte** voor modelgewichten
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Optioneel, voor het sandboxen van OpenClaw)
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

Het aanbevolen model voor dit playbook is **Qwen3.6-35B-A3B-GGUF** van Unsloth, een sterk MoE-model met een contextvenster van 263k tokens dat goed geschikt is voor agentwerkbelastingen. Dit model gebruikt UD-Q4_K_XL-kwantisering. Haal het nu op:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Laad het vervolgens met een groot contextvenster en sla die instelling op voor toekomstige runs:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Het model heeft standaard een contextlengte van 262.144 tokens. Als je out-of-memory-fouten (OOM) tegenkomt, kun je overwegen het contextvenster te verkleinen. Omdat Qwen3.6 echter gebruikmaakt van uitgebreide context voor complexe taken, raden we aan een contextlengte van minstens 128K tokens aan te houden om de denkcapaciteiten te behouden.

> **Tip: Schakel denken uit voor snellere agentreacties:** Qwen3.6-35B-A3B draait standaard in denkmodus, wat vóór elke reactie extra latentie toevoegt. Bij agent-lussen loopt deze overhead snel op. De [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) repository biedt een kant-en-klare configuratie die denken uitschakelt. Om deze te gebruiken, download je het bestand en importeer je het:
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

We voeren OpenClaw uit binnen WSL (Aanbevolen) en verbinden het met Lemonade dat native op Windows draait. Dit geeft je een Linux-shellomgeving voor OpenClaw, terwijl Lemonade's GPU-versnelling aan de Windows-kant behouden blijft.

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

Voer dit uit in de Ubuntu-terminal:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Sluit WSL af en start het opnieuw:

```powershell
exit
wsl --shutdown
wsl
```

### Lemonade overbruggen van Windows naar WSL

WSL2 draait in een virtueel netwerk. Lemonade op Windows bindt aan `127.0.0.1`, wat WSL niet direct kan bereiken. Een Windows-poortproxy stuurt verkeer door van het WSL-gateway-IP naar Windows localhost.

**Zoek je WSL-gateway-IP** (voer uit binnen WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Voeg de poortproxy toe** (voer uit in PowerShell als Administrator, en vervang `<WSL-Gateway-IP>` door je WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Opmerking: Als je een `netsh: command not found`-fout tegenkomt, probeer dan in plaats daarvan de expliciete uitvoerbare naam te gebruiken - `netsh.exe`

**Voeg een firewallregel toe** (dezelfde verhoogde PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Controleer vanuit WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Als je het Qwen3.6-35B-A3B-GGUF-model al hebt geladen in de vorige stap, zou je JSON-uitvoer moeten zien zoals deze:

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

#### De brug werkend houden na een herstart

De `netsh portproxy`-regel overleeft herstarten, maar het WSL-gateway-IP kan wijzigen na `wsl --shutdown` of een herstart. Wanneer dat gebeurt, wijst de proxy nog steeds naar het oude IP en wordt Lemonade onbereikbaar vanuit WSL. Gebruik in dat geval een van de onderstaande opties.

**Optie 1 (aanbevolen) — Herstel de brug automatisch.** Om dit niet elke keer handmatig te hoeven doen, gebruikt u een geplande taak die de brug bij elke opstart en aanmelding controleert en deze alleen herbouwt wanneer het gateway-IP is gewijzigd. Zie de [handleiding voor automatisch herstel van de Lemonade WSL-brug](assets/RepairLemonadeWslBridge.md).


**Optie 2 — Herstel de brug handmatig.** Haal eerst het huidige WSL-gateway-IP op door dit binnen WSL uit te voeren:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopieer deze waarde; u gebruikt deze in plaats van `<new-WSL-Gateway-IP>` hieronder.

Vervolgens, in een **verhoogde PowerShell** (uitvoeren als administrator), geeft u de bestaande regels weer, verwijdert u alleen de verouderde Lemonade-regel en voegt u een nieuwe toe met het huidige IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

In de uitvoer van `show all` is de verouderde Lemonade-regel het item waarvan het connect-adres `127.0.0.1` is op poort `13305`; het listen-adres is uw `<old-WSL-Gateway-IP>`. Door op dat adres te verwijderen, wordt alleen deze regel verwijderd en blijven eventuele andere port-proxyregels op uw machine ongewijzigd.

De firewallregel die u tijdens de installatie hebt toegevoegd, is gebonden aan poort `13305` (niet aan het IP), dus deze blijft werken en hoeft niet opnieuw te worden aangemaakt.

> **Aanbeveling:** Om gateway-problemen te voorkomen, raden we de volgende shell-configuratie sterk aan:
> - **Windows-opdrachten** moeten worden uitgevoerd in **PowerShell**
> - **WSL-distro-opdrachten** moeten worden uitgevoerd in een **Command Prompt** (uitgevoerd als **Administrator**)

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
> Voer de opdrachten in deze sectie uit in uw **WSL-terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

De `--no-onboard`-vlag slaat de interactieve installatiewizard over, u configureert de modelbackend handmatig in de volgende stap, wat u nauwkeurige controle geeft over welk model en welke server worden gebruikt.

Open een nieuwe terminal en bevestig de installatie:

```bash
openclaw --version
```

> **Tip:** Als u `command not found` ziet na de installatie, voeg dan de globale bin-directory van npm toe aan uw PATH:
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

Deze opdracht schrijft de configuratie van OpenClaw naar `~/.openclaw/openclaw.json`.

> **Grootte van het OpenClaw-contextvenster:** De compactie van OpenClaw wordt geactiveerd wanneer `contextTokens > contextWindow − reserveTokens`. De standaard `reserveTokensFloor` is 20.000 tokens, een ondergrens die `reserveTokens` overschrijft wanneer deze lager is, dus elke modelcontext onder ~37k activeert een oneindige compactielus. Stel eenmalig een lage reserve in en schakel de ondergrens uit in uw configuratie, en het geldt voor elk model, geen per-model afstemming nodig:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` is een *ondergrens* (minimale bescherming), niet de reserve zelf; alleen de ondergrens instellen heeft geen effect. `reserveTokensFloor: 0` schakelt de bescherming uit, zodat de lagere `reserveTokens` wordt geaccepteerd.
>
> **Wanneer dit toe te passen:** Gebruik deze configuratie als het effectieve contextvenster van uw model onder ~37k ligt, hetzij omdat het model klein is (bijv. 8k, 16k, 32k) hetzij omdat u het opzettelijk hebt beperkt tot een lagere waarde (bijv. een model van 128k laden maar de context instellen op 16k in Lemonade). Zonder dit komt OpenClaw bij het opstarten in een oneindige compactielus terecht.
>
> **Modellen met een groot context bij volledige context:** U kunt dit volledig overslaan. De standaardinstellingen werken prima, compactie treedt in werking ruim voordat het venster vol raakt en het model heeft voldoende ruimte om lange antwoorden te genereren. Als u dit toch toepast, houd er dan rekening mee dat `reserveTokens: 4096` de responslengte beperkt tot ~4k tokens, wat het genereren van lange bestanden of gedetailleerde plannen kan afknijpen.
>
> **Waar dit toe te voegen:** Plaats het `compaction`-blok binnen `agents.defaults` in uw `openclaw.json` (meestal in `~/.openclaw/openclaw.json`):
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
> De rest van uw configuratie (gateway, channels, models, enz.) blijft ongewijzigd, alleen de `compaction`-sleutel hoeft te worden toegevoegd.
### (Aanbevolen) Docker Sandboxing inschakelen

OpenClaw kan alle bestands- en codebewerkingen van de agent via een geïsoleerde Docker-container laten verlopen in plaats van deze rechtstreeks op uw host uit te voeren. Dit beperkt de impact van elke onbedoelde actie tot de sandbox, zodat uw hostbestandssysteem en netwerk onaangeroerd blijven.

Bouw de sandbox-image eenmalig (Docker moet geïnstalleerd zijn):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Voer dit uit om de `sandbox`-sleutel toe te voegen binnen het bestaande `agents.defaults`-blok in `~/.openclaw/openclaw.json`:

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

Sandboxcontainers hebben standaard **geen netwerktoegang**. Zie de [sandboxing-referentie](https://docs.openclaw.ai/gateway/sandboxing) voor bind mounts en netwerkoverschrijvingen.

> #### Probleemoplossing: Docker Permission Denied
> 
> Als u "permission denied" krijgt bij het uitvoeren van Docker-opdrachten:
> 
> **Stap 1: Voeg uw gebruiker toe aan de docker-groep**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Stap 2: Als de fout blijft optreden, pas de permanente oplossing toe**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> **Herstart** vervolgens uw systeem.
> 
> **Snelle tijdelijke oplossing** (wordt gereset na herstart):
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
## (Aanbevolen) OpenClaw-integratie met Firecrawl-services

[Firecrawl](https://docs.firecrawl.dev/introduction) biedt een selfhosted webcrawl- en content-extractieservice die deze uitdagingen kan omzeilen en het volledige potentieel van OpenClaw-automatisering ontsluit.

In deze opzet draait OpenClaw als een reeks Docker-containers die worden beheerd met Podman. Om het levenscyclusbeheer en automatisch opstarten te vereenvoudigen, registreren we Firecrawl als een gebruikersniveau-`systemd`-service die de onderliggende Podman Compose-stack orkestreert. Hierdoor kan OpenClaw de gateway starten, stoppen en de Firecrawl-service verifiëren met standaard `systemctl --user`-opdrachten, in plaats van rechtstreeks met containers te interageren.

Om het overzichtelijk te houden, hebben we het hele proces opgesplitst in vier stappen:

---

### 1. Registreer de systeemservice
Navigeer naar de systemd-gebruikersconfiguratiemap:
```bash
cd ~/.config/systemd/user
```
Maak een nieuw bestand met de naam `firecrawl.service` en open dit.
```bash
nano firecrawl.service
```
Kopieer en plak de volgende configuratie:
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
Op dit punt is de service gedefinieerd, maar nog niet geregistreerd bij `systemd`.
Zorg ervoor dat de bestandsnaam exact overeenkomt met wat u hierboven hebt gemaakt, en voer dan uit:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Bij succes ziet u de volgende uitvoer:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` bevat symbolische koppelingen naar services die zijn geconfigureerd om automatisch te starten.

### 2. Firecrawl configureren

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) is ideaal voor wie volledige controle wil over hun scraping- en gegevensverwerkingsomgevingen, maar dit brengt extra onderhouds- en configuratie-inspanningen met zich mee.

Begin met het klonen van de repository:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Maak een `.env`-bestand in de `/firecrawl`-map:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. OpenClaw implementeren met Podman Compose

Zorg er, voordat u verdergaat, voor dat u de nieuwste OpenClaw Docker-image hebt opgehaald:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Zodra dat gedaan is, download het OpenClaw Compose-bestand [openclaw-compose.yaml](assets/openclaw-compose.yaml) en plaats dit in de hoofdmap `/firecrawl`:

> Deze conventie is vereist zodat `systemd` de service correct kan vinden en starten, zoals opgegeven in `WorkingDirectory=${HOME}/firecrawl`.

> U kunt de stack altijd uitbreiden door indien nodig extra Firecrawl-services toe te voegen. De volledige lijst met beschikbare services vindt u in het officiële [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. De OpenClaw-service via Firecrawl starten

Voordat u de controle overdraagt aan `systemd`, valideert u eerst dat alles correct werkt door de stack handmatig uit te voeren:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Als alles correct is geconfigureerd, ziet u de OpenClaw-container opstarten en zou uw opdrachtregeluitvoer er ongeveer zo uit moeten zien:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Zodra dit geverifieerd is, sluit u de stack weer af voordat u verdergaat:
```bash
podman compose -f openclaw-compose.yaml down
```
Voordat u de service start, moet u ervoor zorgen dat het juiste eigendom en de juiste rechten zijn ingesteld op de map `firecrawl` en het bijbehorende `.env`-bestand.
Dit is essentieel zodat de service uw referenties bij het opstarten kan wegschrijven.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nu alles gevalideerd is, start u de service via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[De OpenClaw Actions](https://docs.openclaw.ai/) zijn toegankelijk vanuit de interactieve container, en het webdashboard is beschikbaar op dezelfde host en poort op http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Uw `OPENCLAW_GATEWAY_TOKEN` verkrijgen

Zodra de service actief is, ziet u een nieuwe map `.openclaw` die is aangemaakt in uw thuismap (~/.openclaw). Deze map is standaard vergrendeld, dus u moet deze ontgrendelen om uw gateway-token op te halen.

1. Geef toegang tot de map:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lees uw gateway-token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Zoek de waarde `OPENCLAW_GATEWAY_TOKEN` in de uitvoer.

3. Open het gateway-dashboard in uw browser op http://127.0.0.1:18789. Plak uw token wanneer u wordt gevraagd te authenticeren.

Om de service te stoppen, voert u het volgende uit:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Start de OpenClaw Gateway

De gateway is het OpenClaw-proces dat de agentlus beheert en het dashboard bedient:

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

Om het dashboard te openen, voer je dit uit in een tweede terminal terwijl de gateway nog draait:

```bash
openclaw dashboard
```

Omdat de gateway bindt aan loopback, authenticeert het dashboard automatisch wanneer het vanaf dezelfde machine wordt geopend, er is geen token-invoer of apparaatgoedkeuring nodig voor lokale toegang. Je zou het OpenClaw-dashboard moeten zien met je Lemonade-model als actieve backend.

> Als je sandboxing hebt ingeschakeld, kun je dit verifiëren door de agent te vragen `run hostname` uit te voeren vanuit het dashboard. Als je een korte container-ID ziet in plaats van de hostnaam van je machine, werkt de sandbox.

**Gefeliciteerd, je hebt vanaf nul een volledig lokale AI-agentstack gebouwd.**

> **Gateway-token nodig?** Voer `openclaw dashboard --no-open` uit om de dashboard-URL met het ingesloten token af te drukken (het probeert dit ook naar je klembord te kopiëren). Als alternatief staat het token bij `gateway.auth.token` in `~/.openclaw/openclaw.json`.

**Toegang tot het Dashboard vanaf een Ander Apparaat (via SSH-tunnel)**

Als OpenClaw op een externe machine draait, kun je het dashboard vanaf je lokale machine bereiken via een SSH-tunnel. De tunnel leidt de gateway-poort (`18789`) door zodat je lokale browser met de externe gateway kan communiceren via `127.0.0.1`.

1. Maak vanaf je **lokale machine** eenmalig verbinding met de externe machine en accepteer de fingerprint-prompt zodat de host aan je known hosts wordt toegevoegd:

   ```bash
   ssh user@<host-ip>
   ```

2. Open nog steeds op je **lokale machine** de SSH-tunnel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Let op:** Nadat je je wachtwoord hebt ingevoerd, toont de terminal geen uitvoer en lijkt deze vast te lopen. Dit is normaal: de `-N`-vlag vertelt SSH om geen extern commando uit te voeren, dus het houdt alleen de tunnel open. Laat deze terminal actief.

3. Open op je **lokale machine** een browser en ga naar `http://127.0.0.1:18789`.

4. Druk op de **externe machine** het gateway-token af en plak het in de browser om in te loggen:

   ```bash
   openclaw dashboard --no-open
   ```

   Dit drukt de dashboard-URL met het ingesloten token af; kopieer het token om in te loggen. (Het token staat ook opgeslagen bij `gateway.auth.token` in `~/.openclaw/openclaw.json`.)

> **Een extern apparaat goedkeuren:** Wanneer je het dashboard opent vanaf een andere machine of telefoon, kan de browser een aanvraag-ID tonen. Toon op de **externe machine** de openstaande aanvragen:
> ```bash
> openclaw devices list
> ```
> Keur vervolgens de bijbehorende aanvraag goed:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dit is alleen nodig voor externe of secundaire apparaten; loopback-toegang vanaf dezelfde machine authenticeert automatisch. Zie de [Externe Toegang](https://docs.openclaw.ai/gateway/remote)-documentatie voor meer informatie.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optioneel: Verbind een Communicatiekanaal

Zodra de gateway draait, kun je je lokale agent bereiken vanaf elk apparaat. Kies de optie die bij jouw situatie past. OpenClaw ondersteunt [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) en andere kanalen, zie de volledige lijst op [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Optie A: Discord

Discord vereist een server waarop **jij beheerdersrechten hebt** om een bot toe te voegen. Als je servers deelt maar er geen bezit, gebruik dan Optie B (Telegram).

#### Een Discord-account en -server aanmaken

Als je nog geen Discord-account hebt, meld je dan aan op [discord.com](https://discord.com). Je hebt ook een server nodig waarop je beheerder bent, maak er een aan door op het **+**-icoon in de Discord-zijbalk te klikken en **Create My Own** te selecteren. Een privéserver volstaat.

#### Een Discord-applicatie en -bot aanmaken

1. Ga naar het [Discord Developer Portal](https://discord.com/developers/applications) en klik op **New Application**. Geef het een naam (bijv. "openclaw-bot").
2. Klik in de zijbalk op **Bot**. Stel een gebruikersnaam in voor de bot.
3. Scroll nog steeds op de Bot-pagina naar **Privileged Gateway Intents** en schakel in:
   - **Message Content Intent** (vereist)
   - **Server Members Intent** (aanbevolen)
4. Scroll terug omhoog en klik op **Reset Token** om je bot-token te genereren. Kopieer het.

#### De bot toevoegen aan je server

1. Klik in de zijbalk op **OAuth2/ URL Generator**.
2. Schakel onder **Scopes** `bot` en `applications.commands` in.
3. Schakel onder **Bot Permissions** in: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopieer de gegenereerde URL, plak deze in je browser, selecteer je server en bevestig. De bot zou nu moeten verschijnen in de ledenlijst van je server.

#### Verzamel je ID's

Schakel Ontwikkelaarsmodus in Discord in (**Gebruikersinstellingen/ Geavanceerd/ Ontwikkelaarsmodus**), en:
- Klik met de rechtermuisknop op je server-icoon: **Copy Server ID**
- Klik met de rechtermuisknop op je eigen avatar: **Copy User ID**

#### DM's van serverleden toestaan

Klik met de rechtermuisknop op je server-icoon/ **Privacy Settings**/ schakel **Direct Messages** in. Dit staat de bot toe om je een DM te sturen, wat nodig is voor de koppelstap.

#### OpenClaw configureren voor Discord

Sla je bot-token op als omgevingsvariabele, maak vervolgens één patchbestand aan dat Discord inschakelt, naar het token verwijst en je server op de allowlist zet. Vervang `<server_id>` en `<user_id>` door de hierboven verzamelde ID's.

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

> **Vertrouw er niet op om de agent te vragen dit te configureren.** Wanneer sandboxing is ingeschakeld, kan de agent niet naar `~/.openclaw/openclaw.json` schrijven vanuit de sandbox, gebruik in plaats daarvan de bovenstaande CLI-commando's op de host.

Herstart de gateway zodat deze de nieuwe kanaalconfiguratie oppikt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Je zou binnen enkele seconden `logged in to discord as <bot-name>` moeten zien in de gateway-uitvoer.
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

Je kunt nu rechtstreeks vanuit Discord chatten met je agent en taken uitbesteden aan je lokale hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Optie B: Telegram

Telegram is voor de meeste gebruikers eenvoudiger dan Discord, het vereist geen server en geen beheerderstoegang.

#### Maak een Telegram-bot aan

1. Open Telegram en stuur een bericht naar **@BotFather**.
2. Verstuur `/newbot` en volg de aanwijzingen. Bewaar de bot-token die je krijgt.

#### Configureer OpenClaw voor Telegram

Sla de token op als omgevingsvariabele:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Voeg de kanaalconfiguratie toe aan `~/.openclaw/openclaw.json` (of pas deze aan via het dashboard):

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

Herstart de gateway en stuur je bot vervolgens een bericht in Telegram. Keur de koppeling goed:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Koppelcodes verlopen na een uur. Je kunt nu via Telegram-DM chatten met je agent.

---

## Volgende stappen

Nu je agent commando's van je telefoon kan ontvangen en acties op je lokale machine kan uitvoeren, zijn hier drie richtingen die het waard zijn om te verkennen:

1. **Samenvatter van de aandelenmarkt**: Plan OpenClaw in om met vaste tussenpozen gegevens op te halen bij financiële API's, de bewegingen van de dag samen te vatten met je lokale model, en elke ochtend een overzicht naar je telefoon te sturen via je gekozen kanaal.

2. **Monitor voor fine-tuning**: Start op afstand een trainingstaak via Telegram of Discord, en laat de agent het trainingslogboek volgen en periodiek verlieswaarden, GPU-gebruik en schijfruimtegebruik terugmelden naar je telefoon. Als de run vastloopt of het VRAM-gebruik piekt, weet je dit meteen zonder bij de machine te hoeven zijn.

3. **IOT met een lokaal VLM**: Richt een camera op je voordeur, draai een visiemodel op Lemonade, en laat OpenClaw op verzoek of bij een trigger beelden analyseren. Vraag "zijn er vandaag pakketjes bezorgd?" vanaf je telefoon en krijg een rechtstreeks antwoord van je eigen hardware.

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