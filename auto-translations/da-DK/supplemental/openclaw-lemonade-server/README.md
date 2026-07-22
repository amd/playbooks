<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Kør OpenClaw med Lemonade Server som backend

## Oversigt

[**OpenClaw**](https://openclaw.ai/) er en autonom AI-agent, der kan skrive og køre kode, administrere filer og arbejde sig igennem komplekse flertrinsopgaver på dine vegne. I modsætning til en chatassistent, der blot besvarer spørgsmål, udfører OpenClaw reelle handlinger på dit system, hvilket betyder, at den har brug for en hurtig, kompetent AI-backend, der kan følge med i en krævende agent-loop.

[**Lemonade Server**](https://lemonade-server.ai/) er den backend. Det er en open source lokal inferensserver, der kører GenAI-modeller direkte på din hardware og eksponerer dem gennem det branchestandardiserede OpenAI API.

Sammen udgør de en fuldt lokal AI-agentstak: Lemonade håndterer modelinferens, og OpenClaw leverer agent-loopet, der omsætter modeloutput til reelle handlinger.

> **Før du fortsætter:** OpenClaw er en yderst autonom AI-agent. At give en AI-agent adgang til dit system kan resultere i uforudsigelige eller utilsigtede resultater. Fortsæt kun, hvis du forstår risiciene og er tryg ved, at autonom software handler på dine vegne.

---

## Hvad du vil lære

Ved afslutningen af denne playbook vil du kunne:

- Lære om **Lemonade Server**
- **Installere OpenClaw** og **pege den mod Lemonade Server** som dens AI-backend.
- **Starte OpenClaw-gatewayen** og bekræfte, at din agent er klar til at arbejde.
- **Forbinde en kommunikationskanal** (Discord eller Telegram), så du kan chatte med din agent fra enhver enhed.

---

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

<!-- @os:linux -->
- En pc, der kører **Ubuntu 24.04+** eller en kompatibel Debian-baseret Linux-distribution med `apt-get`
- Mindst **12 GB RAM** (64 GB+ anbefales til større modeller)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (valgfrit, til sandboxing af OpenClaw)

- **~10-30 GB ledig diskplads** til modelvægte
<!-- @os:end -->
<!-- @os:windows -->
- En pc, der kører **Windows 10/11**
- Mindst **12 GB RAM** (64 GB+ anbefales til større modeller)
- **~10-30 GB ledig diskplads** til modelvægte
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (valgfrit, til sandboxing af OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hent og indlæs den anbefalede model

Den anbefalede model til denne playbook er **Qwen3.6-35B-A3B-GGUF** fra Unsloth, en stærk MoE-model med et 263k-token kontekstvindue, der er velegnet til agentarbejdsbelastninger. Denne model bruger UD-Q4_K_XL-kvantisering. Hent den nu:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Indlæs den derefter med et stort kontekstvindue, og gem denne indstilling til fremtidige kørsler:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modellen har en standard kontekstlængde på 262.144 tokens. Hvis du oplever fejl på grund af manglende hukommelse (OOM), kan du overveje at reducere kontekstvinduet. Fordi Qwen3.6 dog udnytter udvidet kontekst til komplekse opgaver, anbefaler vi at bevare en kontekstlængde på mindst 128K tokens for at bevare tænkeevnen.

> **Tip: Deaktiver tænkning for hurtigere agentsvar:** Qwen3.6-35B-A3B kører som standard i tænketilstand, hvilket tilføjer latenstid før hvert svar. For agent-loops akkumuleres denne overhead hurtigt. Repoet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) indeholder en færdiglavet konfiguration, der deaktiverer tænkning. For at bruge den skal du downloade filen og importere den:
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

## Opsætning af WSL

Vi kører OpenClaw inde i WSL (anbefalet) og forbinder den til Lemonade, der kører nativt på Windows. Dette giver dig et Linux-skalmiljø til OpenClaw, mens Lemondes GPU-acceleration bevares på Windows-siden.

### Installer WSL og Ubuntu

Åbn PowerShell som administrator, og installer WSL-kernen:

```powershell
wsl --install --no-distribution
```

Installer derefter Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Aktiver systemd i WSL

Kør dette inde i Ubuntu-terminalen:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Genstart WSL:

```powershell
wsl --shutdown
wsl
```

### Broforbind Lemonade fra Windows til WSL

WSL2 kører i et virtuelt netværk. Lemonade på Windows binder til `127.0.0.1`, som WSL ikke kan nå direkte. En Windows-portproxy videresender trafik fra WSL-gatewayens IP til Windows localhost.

**Find din WSL-gateway-IP** (kør inde i WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Tilføj portproxyen** (kør i PowerShell som administrator, og erstat `<WSL-Gateway-IP>` med din WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Tilføj en firewallregel** (samme forhøjede PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verificer fra WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Hvis du allerede har indlæst Qwen3.6-35B-A3B-GGUF-modellen i det foregående trin, skal du se JSON-output som dette:

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

> Reglen for `netsh portproxy` overlever genstarter, men WSL-gateway-IP'en kan ændre sig efter `wsl --shutdown`. Hvis Lemonade bliver utilgængelig fra WSL efter en genstart, skal du hente den opdaterede gateway-IP og opdatere proxyen med denne nye IP.

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

## Installer og konfigurer OpenClaw

### Installer OpenClaw
<!-- @os:windows -->
> Kør kommandoerne i dette afsnit inde i din **WSL-terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaget `--no-onboard` springer den interaktive opsætningsguide over, du konfigurerer modelbackenden manuelt i næste trin, hvilket giver dig præcis kontrol over, hvilken model og server der bruges.

Åbn en ny terminal, og bekræft installationen:

```bash
openclaw --version
```

> **Tip:** Hvis du ser `command not found` efter installationen, skal du tilføje npm's globale bin-mappe til din PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> For at gøre dette permanent skal du tilføje linjen ovenfor til din `~/.bashrc`- eller `~/.zshrc`-fil.

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
### Konfigurer OpenClaw til at bruge Lemonade

Kør OpenClaws ikke-interaktive onboarding.
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

Denne kommando skriver OpenClaws konfiguration til `~/.openclaw/openclaw.json`.

> **Størrelse på OpenClaws kontekstvindue:** OpenClaws komprimering udløses, når `contextTokens > contextWindow − reserveTokens`. Standardværdien for `reserveTokensFloor` er 20.000 tokens, en nedre grænse, der tilsidesætter `reserveTokens`, når denne er lavere, så enhver modelkontekst under ca. 37k vil udløse en uendelig komprimeringssløjfe. Angiv en lav reserve og deaktiver den nedre grænse én gang i din konfiguration, så gælder det for alle modeller, uden behov for tilpasning pr. model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` er en *nedre grænse* (minimumsbeskyttelse), ikke selve reserven, så det har ingen effekt kun at angive den nedre grænse. `reserveTokensFloor: 0` deaktiverer beskyttelsen, så den lavere `reserveTokens` accepteres.
>
> **Hvornår dette skal anvendes:** Brug denne konfiguration, hvis din models effektive kontekstvindue er under ca. 37k, enten fordi modellen er lille (f.eks. 8k, 16k, 32k), eller fordi du bevidst har begrænset den til en lavere værdi (f.eks. indlæser en model på 128k, men angiver konteksten til 16k i Lemonade). Uden dette går OpenClaw ind i en uendelig komprimeringssløjfe ved opstart.
>
> **Modeller med stort kontekstvindue ved fuld kontekst:** Du kan springe dette helt over. Standardindstillingerne fungerer fint, komprimering vil træde i kraft længe før vinduet er fyldt, og modellen har rigelig plads til at generere lange svar. Hvis du alligevel anvender det, skal du være opmærksom på, at `reserveTokens: 4096` begrænser svarlængden til ca. 4k tokens, hvilket kan afkorte generering af lange filer eller detaljerede planer.
>
> **Hvor dette skal tilføjes:** Placer blokken `compaction` inde i `agents.defaults` i din `openclaw.json` (normalt placeret på `~/.openclaw/openclaw.json`):
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
> Resten af din konfiguration (gateway, channels, models osv.) forbliver uændret, kun nøglen `compaction` skal tilføjes.

### (Anbefalet) Aktiver Docker-sandboxing

OpenClaw kan lede alle agentens fil- og kodehandlinger gennem en isoleret Docker-container i stedet for at køre dem direkte på din vært. Dette begrænser konsekvenserne af enhver utilsigtet handling til sandboxen, så din værts filsystem og netværk forbliver uberørt.

Byg sandbox-imaget én gang (Docker skal være installeret):

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

Kør dette for at tilføje nøglen `sandbox` inde i den eksisterende blok `agents.defaults` i `~/.openclaw/openclaw.json`:

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

Sandbox-containere har som standard **ingen netværksadgang**. Se [referencen om sandboxing](https://docs.openclaw.ai/gateway/sandboxing) for bind mounts og netværksoverrides.

> #### Fejlfinding: Docker Permission Denied
> 
> Hvis du får "permission denied", når du kører Docker-kommandoer:
> 
> **Trin 1: Tilføj din bruger til docker-gruppen**
> 
> ```bash
> sudo groupadd docker                    # Opret gruppe hvis nødvendigt
> sudo usermod -aG docker $USER           # Tilføj dig selv til gruppen
> newgrp docker                           # Aktiver ændringen
> docker run hello-world                  # Test det
> ```
> 
> **Trin 2: Hvis fejlen fortsætter, anvend den permanente løsning**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Genstart derefter dit system.
> 
> **Hurtig midlertidig løsning** (nulstilles ved genstart):
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
## (Anbefalet) OpenClaw-integration med Firecrawl-tjenester

[Firecrawl](https://docs.firecrawl.dev/introduction) leverer en selvhostet web crawling- og indholdsudtrækningstjeneste, der kan omgå disse udfordringer og frigøre det fulde potentiale af OpenClaw-automatisering.

I denne opsætning kører OpenClaw som et sæt Docker-containere administreret med Podman. For at forenkle livscyklushåndtering og automatisk opstart registrerer vi Firecrawl som en brugerniveau `systemd`-tjeneste, der orkestrerer den underliggende Podman Compose-stak. Dette gør det muligt for OpenClaw at starte gatewayen, stoppe og verificere Firecrawl-tjenesten ved hjælp af standard `systemctl --user`-kommandoer i stedet for at interagere direkte med containere.

For at holde det enkelt har vi opdelt hele processen i fire trin:

---

### 1. Registrer systemtjenesten
Naviger til systemd's brugerkonfigurationsmappe:
```bash
cd ~/.config/systemd/user
```
Opret og åbn en ny fil kaldet `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopier og indsæt følgende konfiguration:
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
På dette tidspunkt er tjenesten blevet defineret, men endnu ikke registreret hos `systemd`.
Sørg for, at filnavnet nøjagtigt matcher det, du oprettede ovenfor, og kør derefter:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Hvis det lykkes, bør du se følgende output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` indeholder symbolske links til tjenester, der er konfigureret til at starte automatisk.
### 2. Konfigurer Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) er ideel for dem, der har brug for fuld kontrol over deres scraping- og databehandlingsmiljøer, men kommer med den kompromis, at det kræver ekstra vedligeholdelse og konfiguration.

Start med at klone repositoriet:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Opret `.env` i rodmappen `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Deploy OpenClaw med Podman Compose

Før du går videre, skal du sikre dig, at du har hentet det nyeste OpenClaw Docker-image:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Når det er gjort, download OpenClaw Compose-filen [openclaw-compose.yaml](assets/openclaw-compose.yaml) og placer den i rodmappen `/firecrawl`:

> Denne konvention er nødvendig for, at `systemd` kan finde og starte tjenesten korrekt som angivet i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan altid udvide stacken ved at tilføje yderligere Firecrawl-tjenester efter behov. Den fulde liste over tilgængelige tjenester findes i den officielle [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Start OpenClaw-tjenesten gennem Firecrawl 

Før du overlader kontrollen til `systemd`, skal du validere, at alt fungerer korrekt ved at køre stacken manuelt:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Hvis alt er konfigureret korrekt, bør du se OpenClaw-containeren komme op, og dit kommandolinjeoutput bør ligne dette:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Når du har verificeret det, skal du lukke stacken ned igen, før du fortsætter:
```bash
podman compose -f openclaw-compose.yaml down
```
Før du starter tjenesten, skal du sikre dig, at der er angivet korrekt ejerskab og tilladelser for mappen `firecrawl` og dens `.env`-fil. 
Dette er afgørende for, at tjenesten kan skrive dine legitimationsoplysninger ved opstart.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nu hvor alt er valideret, skal du starte tjenesten gennem `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw-handlingerne](https://docs.openclaw.ai/) er tilgængelige fra den interaktive container, og webdashboardet er tilgængeligt på samme vært og port på http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Sådan får du din `OPENCLAW_GATEWAY_TOKEN`

Når tjenesten er oppe at køre, vil du bemærke, at der er oprettet en ny `.openclaw`-mappe i din hjemmemappe (~/.openclaw). Denne mappe er som standard låst, så du skal låse den op for at hente din gateway-token.

1. Giv adgang til mappen:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Læs din gateway-token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Find værdien `OPENCLAW_GATEWAY_TOKEN` i outputtet.

3. Åbn gateway-dashboardet i din browser på http://127.0.0.1:18789. Indsæt din token, når du bliver bedt om at autentificere.

For at stoppe tjenesten skal du køre:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Start OpenClaw Gateway

Gatewayen er den OpenClaw-proces, der styrer agent-loopet og server dashboardet:

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

For at åbne dashboardet, kør dette i en anden terminal, mens gatewayen stadig kører:

```bash
openclaw dashboard
```

Fordi gatewayen bindes til loopback, autentificerer dashboardet automatisk, når det åbnes fra samme maskine, der kræves ingen token-indtastning eller enhedsgodkendelse for lokal adgang. Du bør se OpenClaw-dashboardet med din Lemonade-model listet som den aktive backend.

> Hvis du har aktiveret sandboxing, kan du verificere det ved at bede agenten om at `run hostname` fra dashboardet. Hvis du ser et kort container-ID i stedet for din maskines værtsnavn, fungerer sandboxen.

**Tillykke, du har bygget en fuldt lokal AI-agentstack fra bunden.**

> **Har du brug for gateway-token'en?** Kør `openclaw dashboard --no-open` for at udskrive dashboard-URL'en med tokenet indlejret (den forsøger også at kopiere det til din udklipsholder). Alternativt findes tokenet under `gateway.auth.token` i `~/.openclaw/openclaw.json`.
>
> **Godkendelse af en fjernenhed:** Når du åbner dashboardet fra en anden maskine eller telefon, viser browseren et anmodnings-ID. Tilbage på maskinen, der kører gatewayen, skal du køre:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dette er kun nødvendigt for fjern- eller sekundære enheder, loopback-adgang fra samme maskine autentificerer automatisk.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valgfrit: Tilslut en kommunikationskanal

Når gatewayen kører, kan du tilgå din lokale agent fra enhver enhed. Vælg den mulighed, der passer til din opsætning. OpenClaw understøtter [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) og andre kanaler, se den fulde liste på [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Mulighed A: Discord

Discord kræver en server, hvor **du har administratoradgang** for at tilføje en bot. Hvis du deler servere, men ikke ejer nogen, skal du bruge Mulighed B (Telegram) i stedet.

#### Opret en Discord-konto og -server

Hvis du ikke har en Discord-konto, kan du oprette dig på [discord.com](https://discord.com). Du skal også bruge en server, hvor du er administrator. Opret en ved at klikke på **+**-ikonet i Discord-sidebjælken og vælge **Create My Own**. En privat server er fint.

#### Opret en Discord-applikation og bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications), og klik på **New Application**. Giv den et navn (f.eks. "openclaw-bot").
2. Klik på **Bot** i sidebjælken. Angiv et brugernavn til botten.
3. Bliv på Bot-siden, rul ned til **Privileged Gateway Intents**, og aktivér:
   - **Message Content Intent** (påkrævet)
   - **Server Members Intent** (anbefalet)
4. Rul tilbage op, og klik på **Reset Token** for at generere din bot-token. Kopiér den.

#### Tilføj botten til din server

1. Klik på **OAuth2/ URL Generator** i sidebjælken.
2. Under **Scopes** skal du aktivere `bot` og `applications.commands`.
3. Under **Bot Permissions** skal du aktivere: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopiér den genererede URL, indsæt den i din browser, vælg din server, og bekræft. Botten bør nu vises på din servers medlemsliste.
#### Saml dine ID'er

Aktivér udviklertilstand i Discord (**Brugerindstillinger/ Avanceret/ Udviklertilstand**), og:
- Højreklik på dit serverikon: **Kopiér server-ID**
- Højreklik på din egen avatar: **Kopiér bruger-ID**

#### Tillad DM'er fra servermedlemmer

Højreklik på dit serverikon/ **Privatlivsindstillinger**/ slå **Direkte beskeder** til. Dette gør det muligt for botten at sende dig en DM, hvilket er nødvendigt for parringstrinnet.

#### Konfigurer OpenClaw til Discord

Gem dit bot-token som en miljøvariabel, og opret derefter en enkelt patch-fil, der aktiverer Discord, refererer til tokenet og tilføjer din server til allowlisten. Erstat `<server_id>` og `<user_id>` med de ID'er, du samlede ovenfor.

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

> **Stol ikke på at bede agenten om at konfigurere dette.** Når sandboxing er aktiveret, kan agenten ikke skrive til `~/.openclaw/openclaw.json` inde fra sandboxen; brug i stedet CLI-kommandoerne ovenfor på værtsmaskinen.

Genstart gatewayen, så den registrerer den nye kanalkonfiguration:

```bash
openclaw gateway run --bind loopback --port 18789
```

Du bør se `logged in to discord as <bot-name>` i gateway-outputtet inden for et par sekunder.

#### Par din Discord-konto

Send en DM til botten i Discord. Den vil svare med en kort parringskode.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Godkend den på den maskine, der kører OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Parringskoder udløber efter en time.

Du kan nu chatte med din agent direkte fra Discord og overlade opgaver til din lokale hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Mulighed B: Telegram

Telegram er enklere end Discord for de fleste brugere, det kræver ingen server og ingen administratoradgang.

#### Opret en Telegram-bot

1. Åbn Telegram, og send en besked til **@BotFather**.
2. Send `/newbot`, og følg vejledningen. Gem det bot-token, du får.

#### Konfigurer OpenClaw til Telegram

Gem tokenet som en miljøvariabel:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Tilføj kanalkonfigurationen til `~/.openclaw/openclaw.json` (eller patch den via dashboardet):

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

Genstart gatewayen, og send derefter en besked til din bot i Telegram. Godkend parringen:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Parringskoder udløber efter en time. Du kan nu chatte med din agent via Telegram-DM.

---

## Næste skridt

Nu hvor din agent kan modtage kommandoer fra din telefon og udføre handlinger på din lokale maskine, er her tre retninger, der er værd at udforske:

1. **Opsummering af aktiemarkedet**: Planlæg OpenClaw til at hente data fra finansielle API'er med faste intervaller, opsummere dagens bevægelser med din lokale model, og send et resumé til din telefon hver morgen via din valgte kanal.

2. **Overvågning af finjustering**: Start et træningsjob eksternt via Telegram eller Discord, og lad agenten følge træningsloggen og rapportere periodiske loss-værdier, GPU-udnyttelse og diskforbrug tilbage til din telefon. Hvis kørslen går i stå, eller VRAM-forbruget stiger kraftigt, får du besked med det samme uden at skulle være ved maskinen.

3. **IOT med en lokal VLM**: Ret et kamera mod din hoveddør, kør en synsmodel på Lemonade, og lad OpenClaw analysere billeder på anmodning eller ved en udløser. Spørg "er der ankommet nogen pakker i dag?" fra din telefon og få et klart svar fra din egen hardware.

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