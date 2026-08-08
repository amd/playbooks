<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Kør OpenClaw med Lemonade Server som backend

## Oversigt

[**OpenClaw**](https://openclaw.ai/) er en autonom AI-agent, der kan skrive og køre kode, administrere filer og arbejde sig igennem komplekse opgaver med flere trin på dine vegne. I modsætning til en chatassistent, der blot besvarer spørgsmål, udfører OpenClaw reelle handlinger på dit system, hvilket betyder, at den har brug for en hurtig og kompetent AI-backend, der kan følge med i en krævende agentloop.

[**Lemonade Server**](https://lemonade-server.ai/) er den backend. Det er en open source lokal inferensserver, der kører GenAI-modeller direkte på din hardware og gør dem tilgængelige gennem den branchestandard OpenAI API.

Sammen udgør de en fuldt lokal AI-agentstack: Lemonade håndterer modelinferens, og OpenClaw leverer agentloopet, der omdanner modeloutput til reelle handlinger.

> **Før du fortsætter:** OpenClaw er en meget autonom AI-agent. At give en AI-agent adgang til dit system kan resultere i uforudsigelige eller utilsigtede resultater. Fortsæt kun, hvis du forstår risiciene og er tryg ved, at autonom software handler på dine vegne.

---

## Hvad du vil lære

Når du er færdig med denne playbook, vil du kunne:

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
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Valgfrit, til sandboxing af OpenClaw)
- **~10–30 GB ledig diskplads** til modelvægte
<!-- @os:end -->

<!-- @os:windows -->
- En pc, der kører **Windows 10/11**
- Mindst **12 GB RAM** (64 GB+ anbefales til større modeller)
- **~10–30 GB ledig diskplads** til modelvægte
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Valgfrit, til sandboxing af OpenClaw)
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

Den anbefalede model til denne playbook er **Qwen3.6-35B-A3B-GGUF** fra Unsloth, en stærk MoE-model med et kontekstvindue på 263k tokens, som passer godt til agentopgaver. Denne model bruger UD-Q4_K_XL-kvantisering. Hent den nu:

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

Modellen har som standard en kontekstlængde på 262.144 tokens. Hvis du støder på fejl med manglende hukommelse (OOM), kan du overveje at reducere kontekstvinduet. Da Qwen3.6 dog udnytter udvidet kontekst til komplekse opgaver, anbefaler vi at bevare en kontekstlængde på mindst 128K tokens for at bevare tænkeevnen.

> **Tip: Deaktiver tænkning for hurtigere agentsvar:** Qwen3.6-35B-A3B kører som standard i tænketilstand, hvilket tilføjer latenstid før hvert svar. For agentloops akkumuleres denne overhead hurtigt. Repositoriet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) indeholder en færdiglavet konfiguration, der deaktiverer tænkning. For at bruge den, download filen og importer den:
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

Vi kører OpenClaw inde i WSL (anbefales) og forbinder den til Lemonade, som kører nativt på Windows. Dette giver dig et Linux-shellmiljø til OpenClaw, samtidig med at Lemonades GPU-acceleration bevares på Windows-siden.

### Installer WSL og Ubuntu

Åbn PowerShell som administrator, og installer WSL-kernen:

```powershell
wsl --install --no-distribution
```

Installer derefter Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Aktivér systemd i WSL

Kør dette inde i Ubuntu-terminalen:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Afslut WSL, og genstart det:

```powershell
exit
wsl --shutdown
wsl
```

### Bro Lemonade fra Windows ind i WSL

WSL2 kører i et virtuelt netværk. Lemonade på Windows binder til `127.0.0.1`, som WSL ikke kan nå direkte. En Windows-portproxy videresender trafik fra WSL-gatewayens IP til Windows-localhost.

**Find din WSL-gateway-IP** (kør inde i WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Tilføj portproxyen** (kør i PowerShell som administrator, og erstat `<WSL-Gateway-IP>` med din WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Bemærk: Hvis du støder på en `netsh: command not found`-fejl, kan du prøve at bruge det eksplicitte eksekverbare navn i stedet - `netsh.exe`

**Tilføj en firewallregel** (samme forhøjede PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Bekræft fra WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Hvis du allerede har indlæst Qwen3.6-35B-A3B-GGUF-modellen i det foregående trin, bør du se JSON-output som dette:

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

#### Sådan holdes broen kørende efter en genstart

Reglen for `netsh portproxy` overlever genstarter, men WSL-gateway-IP'en kan ændre sig efter `wsl --shutdown` eller en genstart. Når det sker, peger proxyen stadig på den gamle IP, og Lemonade bliver utilgængelig fra WSL. Hvis det sker, kan du bruge en af mulighederne nedenfor.

**Mulighed 1 (anbefalet) — Reparér broen automatisk.** For at undgå at gøre dette manuelt hver gang kan du bruge en planlagt opgave, der tjekker broen ved hver opstart og login og kun genopbygger den, når gateway-IP'en er ændret. Se [guiden til automatisk reparation af Lemonade WSL-broen](assets/RepairLemonadeWslBridge.md).


**Mulighed 2 — Reparér broen manuelt.** Først skal du hente den aktuelle WSL-gateway-IP ved at køre dette inde i WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopiér denne værdi; du vil bruge den i stedet for `<new-WSL-Gateway-IP>` nedenfor.

Åbn derefter en **forhøjet PowerShell** (Kør som administrator), vis de eksisterende regler, slet kun den forældede Lemonade-regel, og tilføj en ny med den aktuelle IP:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

I outputtet fra `show all` er den forældede Lemonade-regel den post, hvis connect-adresse er `127.0.0.1` på port `13305`; dens listen-adresse er din `<old-WSL-Gateway-IP>`. Ved at slette efter den adresse fjernes kun denne regel, mens eventuelle andre port-proxy-regler på din maskine forbliver urørte.

Firewall-reglen, du tilføjede under opsætningen, er bundet til port `13305` (ikke IP'en), så den bliver ved med at virke og skal ikke genoprettes.

> **Anbefaling:** For at undgå gateway-problemer anbefaler vi kraftigt følgende shell-konfiguration:
> - **Windows-kommandoer** bør udføres i **PowerShell**
> - **WSL-distro-kommandoer** bør udføres i en **kommandoprompt** (kørt som **administrator**)

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

## Installér og konfigurér OpenClaw

### Installér OpenClaw
<!-- @os:windows -->
> Kør kommandoerne i dette afsnit inde i din **WSL-terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaget `--no-onboard` springer den interaktive opsætningsguide over, du vil konfigurere model-backenden manuelt i næste trin, hvilket giver dig præcis kontrol over, hvilken model og server der bruges.

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


### Konfigurér OpenClaw til at bruge Lemonade

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

> **Størrelse af OpenClaws context window:** OpenClaws komprimering udløses, når `contextTokens > contextWindow − reserveTokens`. Standardværdien for `reserveTokensFloor` er 20.000 tokens, en bundgrænse, der tilsidesætter `reserveTokens`, når den er lavere, så enhver modelkontekst under ~37k vil udløse en uendelig komprimeringssløjfe. Sæt en lav reserve og deaktivér bundgrænsen én gang i din konfiguration, så gælder det for hver model, ingen behov for indstilling pr. model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` er en *bundgrænse* (minimumsbeskyttelse), ikke selve reserven, så det at sætte kun bundgrænsen har ingen effekt. `reserveTokensFloor: 0` deaktiverer beskyttelsen, så den lavere `reserveTokens` accepteres.
>
> **Hvornår denne konfiguration skal anvendes:** Brug denne konfiguration, hvis din models effektive context window er under ~37k, enten fordi modellen er lille (f.eks. 8k, 16k, 32k), eller fordi du med vilje har begrænset den til en lavere værdi (f.eks. indlæser en 128k-model, men sætter konteksten til 16k i Lemonade). Uden det går OpenClaw ind i en uendelig komprimeringssløjfe ved opstart.
>
> **Modeller med stor kontekst ved fuld kontekst:** Du kan springe dette helt over. Standardværdierne fungerer fint, komprimering vil ske godt før vinduet fyldes op, og modellen har rigelig plads til at generere lange svar. Hvis du alligevel anvender det, skal du være opmærksom på, at `reserveTokens: 4096` begrænser svarlængden til ~4k tokens, hvilket kan afskære lang filgenerering eller detaljerede planer.
>
> **Hvor dette skal tilføjes:** Placér blokken `compaction` inde i `agents.defaults` i din `openclaw.json` (normalt i `~/.openclaw/openclaw.json`):
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
### (Anbefalet) Aktiver Docker Sandboxing

OpenClaw kan dirigere alle agentens fil- og kodeoperationer gennem en isoleret Docker-container i stedet for at køre dem direkte på din host. Dette begrænser konsekvenserne af enhver utilsigtet handling til sandkassen og efterlader din værtsmaskines filsystem og netværk urørt.

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

Kør dette for at tilføje nøglen `sandbox` inde i den eksisterende `agents.defaults`-blok i `~/.openclaw/openclaw.json`:

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

Sandbox-containere har som standard **ingen netværksadgang**. Se [sandboxing-referencen](https://docs.openclaw.ai/gateway/sandboxing) for bind mounts og netværksoverstyringer.

> #### Fejlfinding: Docker-tilladelse nægtet
> 
> Hvis du får "permission denied", når du kører Docker-kommandoer:
> 
> **Trin 1: Tilføj din bruger til docker-gruppen**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
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
> **Hurtig midlertidig løsning** (nulstilles efter genstart):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) leverer en selv-hostet web crawling- og indholdsudtrækningstjeneste, der kan omgå disse udfordringer og frigøre det fulde potentiale af OpenClaw-automatisering. 

I denne opsætning kører OpenClaw som et sæt Docker-containere administreret med Podman. For at forenkle livscyklusstyring og automatisk opstart registrerer vi Firecrawl som en brugerniveau-`systemd`-tjeneste, der orkestrerer den underliggende Podman Compose-stak. Dette gør det muligt for OpenClaw at starte gateway'en, stoppe og verificere Firecrawl-tjenesten ved hjælp af standard `systemctl --user`-kommandoer i stedet for at interagere direkte med containerne. 

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
Kopiér og indsæt følgende konfiguration:
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

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) er ideel for dem, der har brug for fuld kontrol over deres scraping- og databehandlingsmiljøer, men medfører til gengæld ekstra vedligeholdelse og konfigurationsarbejde.

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
### 3. Implementer OpenClaw med Podman Compose

Før du fortsætter, skal du sikre dig, at du har hentet det nyeste OpenClaw Docker-image:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Når det er gjort, skal du downloade OpenClaw Compose-filen [openclaw-compose.yaml](assets/openclaw-compose.yaml) og placere den i rodmappen `/firecrawl`:

> Denne konvention er nødvendig, for at `systemd` korrekt kan finde og starte tjenesten som angivet i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan altid udvide stakken ved at tilføje yderligere Firecrawl-tjenester efter behov. Den fulde liste over tilgængelige tjenester findes i den officielle [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Start OpenClaw-tjenesten via Firecrawl 

Før du overdrager kontrollen til `systemd`, skal du validere, at alt fungerer korrekt ved at køre stakken manuelt:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Hvis alt er konfigureret korrekt, bør du se OpenClaw-containeren starte op, og dit kommandolinjeoutput bør ligne dette:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Når du har verificeret dette, skal du lukke stakken ned igen, før du fortsætter:
```bash
podman compose -f openclaw-compose.yaml down
```
Før du starter tjenesten, skal du sikre dig, at der er sat korrekt ejerskab og rettigheder på mappen `firecrawl` og dens `.env`-fil. 
Dette er afgørende for, at tjenesten kan skrive dine legitimationsoplysninger ved opstart.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nu hvor alt er valideret, skal du starte tjenesten via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw-handlingerne](https://docs.openclaw.ai/) er tilgængelige fra den interaktive container, og webdashboardet er tilgængeligt på samme host og port på http://127.0.0.1:18789.
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
Find værdien for `OPENCLAW_GATEWAY_TOKEN` i outputtet.

3. Åbn gateway-dashboardet i din browser på http://127.0.0.1:18789. Indsæt din token, når du bliver bedt om at autentificere.

For at stoppe tjenesten skal du køre:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Start OpenClaw Gateway

Gatewayen er den OpenClaw-proces, der styrer agent-loopet og betjener dashboardet:

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

For at åbne dashboardet skal du køre dette i en anden terminal, mens gatewayen stadig kører:

```bash
openclaw dashboard
```

Fordi gatewayen binder til loopback, autentificerer dashboardet automatisk, når det åbnes fra den samme maskine, og der kræves ingen tokenindtastning eller enhedsgodkendelse for lokal adgang. Du bør se OpenClaw-dashboardet med din Lemonade-model opført som den aktive backend.

> Hvis du har aktiveret sandboxing, kan du bekræfte det ved at bede agenten om at `run hostname` fra dashboardet. Hvis du ser et kort container-id i stedet for din maskines værtsnavn, virker sandboxen.

**Tillykke, du har bygget en fuldt lokal AI-agentstak fra bunden.**

> **Har du brug for gateway-tokenet?** Kør `openclaw dashboard --no-open` for at udskrive dashboard-URL'en med tokenet indlejret (det forsøger også at kopiere det til din udklipsholder). Alternativt findes tokenet under `gateway.auth.token` i `~/.openclaw/openclaw.json`.

**Adgang til dashboardet fra en anden enhed (via SSH-tunnel)**

Hvis OpenClaw kører på en fjernmaskine, kan du tilgå dashboardet fra din lokale maskine gennem en SSH-tunnel. Tunnelen videresender gateway-porten (`18789`), så din lokale browser kan kommunikere med den fjerne gateway over `127.0.0.1`.

1. Fra din **lokale maskine** skal du oprette forbindelse til fjernmaskinen én gang og acceptere fingeraftryksprompten, så værten tilføjes til dine kendte værter:

   ```bash
   ssh user@<host-ip>
   ```

2. Stadig på din **lokale maskine** skal du åbne SSH-tunnelen:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Bemærk:** Efter du har indtastet din adgangskode, viser terminalen ingen output og ser ud til at hænge. Dette er forventet: `-N`-flaget fortæller SSH ikke at køre nogen fjernkommando, så den holder blot tunnelen åben. Lad denne terminal fortsætte med at køre.

3. På din **lokale maskine** skal du åbne en browser og gå til `http://127.0.0.1:18789`.

4. På **fjernmaskinen** skal du udskrive gateway-tokenet og indsætte det i browseren for at logge ind:

   ```bash
   openclaw dashboard --no-open
   ```

   Dette udskriver dashboard-URL'en med tokenet indlejret; kopiér tokenet for at logge ind. (Tokenet gemmes også under `gateway.auth.token` i `~/.openclaw/openclaw.json`.)

> **Godkendelse af en fjernenhed:** Når du åbner dashboardet fra en anden maskine eller telefon, kan browseren vise et anmodnings-id. På **fjernmaskinen** skal du liste de afventende anmodninger:
> ```bash
> openclaw devices list
> ```
> Godkend derefter den matchende anmodning:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dette er kun nødvendigt for fjern- eller sekundære enheder; loopback-adgang fra den samme maskine autentificerer automatisk. Se dokumentationen [Remote Access](https://docs.openclaw.ai/gateway/remote) for flere detaljer.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valgfrit: Tilslut en kommunikationskanal

Når gatewayen kører, kan du tilgå din lokale agent fra enhver enhed. Vælg den mulighed, der passer til din opsætning. OpenClaw understøtter [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) og andre kanaler, se den fulde liste på [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Mulighed A: Discord

Discord kræver en server, hvor **du har administratoradgang** for at tilføje en bot. Hvis du deler servere, men ikke ejer en, kan du bruge mulighed B (Telegram) i stedet.

#### Opret en Discord-konto og -server

Hvis du ikke har en Discord-konto, kan du tilmelde dig på [discord.com](https://discord.com). Du skal også bruge en server, hvor du er administrator; opret én ved at klikke på **+**-ikonet i Discord-sidebaren og vælge **Create My Own**. En privat server er fint.

#### Opret en Discord-applikation og bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications), og klik på **New Application**. Giv den et navn (f.eks. "openclaw-bot").
2. Klik på **Bot** i sidebaren. Angiv et brugernavn til botten.
3. Stadig på Bot-siden skal du rulle ned til **Privileged Gateway Intents** og aktivere:
   - **Message Content Intent** (påkrævet)
   - **Server Members Intent** (anbefalet)
4. Rul tilbage op, og klik på **Reset Token** for at generere dit bot-token. Kopiér det.

#### Tilføj botten til din server

1. Klik på **OAuth2/ URL Generator** i sidebaren.
2. Under **Scopes** skal du aktivere `bot` og `applications.commands`.
3. Under **Bot Permissions** skal du aktivere: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopiér den genererede URL, indsæt den i din browser, vælg din server, og bekræft. Botten bør nu vises i din servers medlemsliste.

#### Indsaml dine ID'er

Aktivér udviklertilstand i Discord (**User Settings/ Advanced/ Developer Mode**), og gør derefter følgende:
- Højreklik på dit server-ikon: **Copy Server ID**
- Højreklik på dit eget avatar: **Copy User ID**

#### Tillad DM'er fra servermedlemmer

Højreklik på dit server-ikon/ **Privacy Settings**/ slå **Direct Messages** til. Dette gør det muligt for botten at sende dig en DM, hvilket er påkrævet i parringstrinnet.

#### Konfigurer OpenClaw til Discord

Gem dit bot-token som en miljøvariabel, og opret derefter en enkelt patch-fil, der aktiverer Discord, refererer til tokenet og tilføjer din server til allowlisten. Erstat `<server_id>` og `<user_id>` med de ID'er, du indsamlede ovenfor.

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

> **Stol ikke på at bede agenten om at konfigurere dette.** Når sandboxing er aktiveret, kan agenten ikke skrive til `~/.openclaw/openclaw.json` inde fra sandboxen, brug i stedet CLI-kommandoerne ovenfor på værten.

Genstart gatewayen, så den registrerer den nye kanalkonfiguration:

```bash
openclaw gateway run --bind loopback --port 18789
```

Du bør se `logged in to discord as <bot-name>` i gateway-outputtet inden for få sekunder.
#### Par din Discord-konto

Send bottet en DM på Discord. Det svarer med en kort parringskode.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Godkend den på maskinen, der kører OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Parringskoder udløber efter en time.

Du kan nu chatte med din agent direkte fra Discord og lade opgaver blive udført af din lokale hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Mulighed B: Telegram

Telegram er enklere end Discord for de fleste brugere, det kræver ingen server og ingen admin-adgang.

#### Opret en Telegram-bot

1. Åbn Telegram og send en besked til **@BotFather**.
2. Send `/newbot` og følg vejledningen. Gem den bot-token, du får.

#### Konfigurer OpenClaw til Telegram

Gem tokenet som en miljøvariabel:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Tilføj kanalkonfigurationen til `~/.openclaw/openclaw.json` (eller ret den via dashboardet):

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

Genstart gatewayen, og send derefter din bot en besked på Telegram. Godkend parringen:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Parringskoder udløber efter en time. Du kan nu chatte med din agent via Telegram DM.

---

## Næste skridt

Nu hvor din agent kan modtage kommandoer fra din telefon og handle på din lokale maskine, er her tre retninger, det er værd at udforske:

1. **Aktiemarkedsopsummering**: Planlæg OpenClaw til at hente data fra finansielle API'er med faste intervaller, opsummere dagens bevægelser med din lokale model, og send et sammendrag til din telefon hver morgen via din valgte kanal.

2. **Overvågning af fine-tuning**: Start et træningsjob eksternt via Telegram eller Discord, og lad derefter agenten følge træningsloggen og rapportere periodiske tabsværdier, GPU-udnyttelse og diskforbrug tilbage til din telefon. Hvis kørslen går i stå, eller VRAM-forbruget stiger pludseligt, får du besked med det samme uden at skulle være ved maskinen.

3. **IoT med en lokal VLM**: Ret et kamera mod din hoveddør, kør en visionsmodel på Lemonade, og lad OpenClaw analysere billeder efter behov eller ved en udløser. Spørg "kom der nogen pakker i dag?" fra din telefon og få et direkte svar fra din egen hardware.

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