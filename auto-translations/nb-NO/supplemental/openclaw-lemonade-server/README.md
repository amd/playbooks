<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Kjøre OpenClaw med Lemonade Server som backend

## Oversikt

[**OpenClaw**](https://openclaw.ai/) er en autonom AI-agent som kan skrive og kjøre kode, håndtere filer og jobbe seg gjennom komplekse flertrinnsoppgaver på dine vegne. I motsetning til en chatassistent som bare svarer på spørsmål, utfører OpenClaw reelle handlinger på systemet ditt, noe som betyr at den trenger en rask, kapabel AI-backend som kan følge tempoet i en krevende agentløkke.

[**Lemonade Server**](https://lemonade-server.ai/) er den backenden. Det er en åpen kildekode-basert lokal inferensserver som kjører GenAI-modeller direkte på maskinvaren din og eksponerer dem gjennom det bransjestandardiserte OpenAI API-et.

Sammen utgjør de en fullstendig lokal AI-agentstack: Lemonade håndterer modellinferens, og OpenClaw leverer agentløkken som omgjør modellutdata til reelle handlinger.

> **Før du fortsetter:** OpenClaw er en svært autonom AI-agent. Å gi en AI-agent tilgang til systemet ditt kan føre til uforutsigbare eller utilsiktede utfall. Fortsett bare hvis du forstår risikoen og er komfortabel med at autonom programvare handler på dine vegne.

---

## Hva du vil lære

Ved slutten av denne veiledningen vil du kunne:

- Lære om **Lemonade Server**
- **Installere OpenClaw** og **peke den mot Lemonade Server** som sin AI-backend.
- **Starte OpenClaw-gatewayen** og bekrefte at agenten din er klar til å jobbe.
- **Koble til en kommunikasjonskanal** (Discord eller Telegram) slik at du kan chatte med agenten din fra hvilken som helst enhet.

---

## Konfigurere minneinnstillinger

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk for programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

<!-- @os:linux -->
- En PC som kjører **Ubuntu 24.04+** eller en kompatibel Debian-basert Linux-distribusjon med `apt-get`
- Minst **12 GB RAM** (64 GB+ anbefales for større modeller)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Valgfritt, for sandboksing av OpenClaw)

- **~10–30 GB ledig diskplass** for modellvekter
<!-- @os:end -->
<!-- @os:windows -->
- En PC som kjører **Windows 10/11**
- Minst **12 GB RAM** (64 GB+ anbefales for større modeller)
- **~10–30 GB ledig diskplass** for modellvekter
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Valgfritt, for sandboksing av OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hent og last inn den anbefalte modellen

Den anbefalte modellen for denne veiledningen er **Qwen3.6-35B-A3B-GGUF** fra Unsloth, en sterk MoE-modell med et 263k-token kontekstvindu som er godt egnet til agentarbeidslaster. Denne modellen bruker UD-Q4_K_XL-kvantisering. Hent den nå:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Last den deretter inn med et stort kontekstvindu og lagre denne innstillingen for fremtidige kjøringer:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modellen har en standard kontekstlengde på 262 144 tokens. Hvis du støter på minneproblemer (OOM-feil), bør du vurdere å redusere kontekstvinduet. Fordi Qwen3.6 utnytter utvidet kontekst for komplekse oppgaver, anbefaler vi imidlertid å opprettholde en kontekstlengde på minst 128K tokens for å bevare tenkeevnen.

> **Tips: Deaktiver tenking for raskere agentrespons:** Qwen3.6-35B-A3B kjører i tenkemodus som standard, noe som legger til forsinkelse før hvert svar. For agentløkker akkumuleres denne overheaden raskt. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json)-repoet gir en ferdiglaget konfigurasjon som deaktiverer tenking. For å bruke den, last ned filen og importer den:
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

## Sette opp WSL

Vi kjører OpenClaw inne i WSL (Anbefalt) og kobler den til Lemonade som kjører nativt på Windows. Dette gir deg et Linux-skallmiljø for OpenClaw samtidig som Lemonades GPU-akselerasjon beholdes på Windows-siden.

### Installer WSL og Ubuntu

Åpne PowerShell som administrator og installer WSL-kjernen:

```powershell
wsl --install --no-distribution
```

Installer deretter Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Aktiver systemd i WSL

Kjør dette inne i Ubuntu-terminalen:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Start WSL på nytt:

```powershell
wsl --shutdown
wsl
```

### Bygg bro mellom Lemonade fra Windows til WSL

WSL2 kjører i et virtuelt nettverk. Lemonade på Windows binder til `127.0.0.1`, som WSL ikke kan nå direkte. En Windows-portproxy videresender trafikk fra WSL-gatewayens IP til Windows localhost.

**Finn WSL-gatewayens IP** (kjør inne i WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Legg til portproxyen** (kjør i PowerShell som administrator, og erstatt `<WSL-Gateway-IP>` med din WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Legg til en brannmurregel** (samme forhøyede PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifiser fra WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Hvis du allerede har lastet inn Qwen3.6-35B-A3B-GGUF-modellen i forrige trinn, bør du se JSON-utdata som dette:

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

> `netsh portproxy`-regelen overlever omstarter, men WSL-gatewayens IP kan endre seg etter `wsl --shutdown`. Hvis Lemonade blir utilgjengelig fra WSL etter en omstart, hent den oppdaterte gateway-IP-en og oppdater proxyen med denne nye IP-en.

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
> Kjør kommandoene i denne delen inne i **WSL-terminalen**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard`-flagget hopper over den interaktive oppsettveiviseren, du vil konfigurere modellbackenden manuelt i neste trinn, noe som gir deg presis kontroll over hvilken modell og server som brukes.

Åpne en ny terminal og bekreft installasjonen:

```bash
openclaw --version
```

> **Tips:** Hvis du ser `command not found` etter installasjonen, legg til npms globale bin-katalog i PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> For å gjøre dette permanent, legg til linjen ovenfor i `~/.bashrc`- eller `~/.zshrc`-filen din.

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
### Konfigurer OpenClaw til å bruke Lemonade

Kjør OpenClaws ikke-interaktive onboarding.
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

Denne kommandoen skriver OpenClaws konfigurasjon til `~/.openclaw/openclaw.json`.

> **Størrelse på OpenClaws kontekstvindu:** OpenClaws komprimering utløses når `contextTokens > contextWindow − reserveTokens`. Standard `reserveTokensFloor` er 20 000 tokener, en nedre grense som overstyrer `reserveTokens` når den er lavere, så enhver modellkontekst under ca. 37k vil utløse en uendelig komprimeringssløyfe. Sett en lav reserve og deaktiver den nedre grensen én gang i konfigurasjonen din, så gjelder det for alle modeller, ingen tilpasning per modell er nødvendig:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` er en *nedre grense* (minimumsvern), ikke selve reserven, å kun sette den nedre grensen har ingen effekt. `reserveTokensFloor: 0` deaktiverer vernet slik at den lavere `reserveTokens` godtas.
>
> **Når du bør bruke dette:** Bruk denne konfigurasjonen hvis modellens effektive kontekstvindu er under ca. 37k, enten fordi modellen er liten (f.eks. 8k, 16k, 32k), eller fordi du bevisst har begrenset den til en lavere verdi (f.eks. lastet inn en 128k-modell, men satt konteksten til 16k i Lemonade). Uten dette vil OpenClaw gå inn i en uendelig komprimeringssløyfe ved oppstart.
>
> **Store kontekstmodeller med full kontekst:** Du kan hoppe over dette helt. Standardinnstillingene fungerer fint, komprimering vil starte godt før vinduet fylles, og modellen har god plass til å generere lange svar. Hvis du likevel bruker dette, vær oppmerksom på at `reserveTokens: 4096` begrenser svarlengden til ca. 4k tokener, noe som kan kutte av lang filgenerering eller detaljerte planer.
>
> **Hvor du skal legge til dette:** Plasser `compaction`-blokken inne i `agents.defaults` i din `openclaw.json` (vanligvis på `~/.openclaw/openclaw.json`):
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
> Resten av konfigurasjonen din (gateway, channels, models, osv.) forblir uendret, kun `compaction`-nøkkelen må legges til.

### (Anbefalt) Aktiver Docker-sandkasse

OpenClaw kan rute alle agentens fil- og kodeoperasjoner gjennom en isolert Docker-container i stedet for å kjøre dem direkte på verten din. Dette begrenser konsekvensene av enhver utilsiktet handling til sandkassen, og lar filsystemet og nettverket på verten forbli uberørt.

Bygg sandkassebildet én gang (Docker må være installert):

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

Kjør dette for å legge til `sandbox`-nøkkelen inne i den eksisterende `agents.defaults`-blokken i `~/.openclaw/openclaw.json`:

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

Sandkassecontainere har **ingen nettverkstilgang** som standard. Se [referansen for sandkassing](https://docs.openclaw.ai/gateway/sandboxing) for bindemonteringer og nettverksoverstyringer.

> #### Feilsøking: Docker-tillatelse nektet
> 
> Hvis du får «permission denied» når du kjører Docker-kommandoer:
> 
> **Trinn 1: Legg brukeren din til docker-gruppen**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Trinn 2: Hvis feilen vedvarer, bruk den permanente løsningen**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Deretter **starter du systemet på nytt**.
> 
> **Rask midlertidig løsning** (tilbakestilles ved omstart):
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
## (Anbefalt) OpenClaw-integrasjon med Firecrawl-tjenester

[Firecrawl](https://docs.firecrawl.dev/introduction) tilbyr en selvhostet tjeneste for nettkrabbing og innholdsuthenting som kan omgå disse utfordringene og frigjøre det fulle potensialet til OpenClaw-automatisering.

I dette oppsettet kjører OpenClaw som et sett med Docker-containere administrert med Podman. For å forenkle livssyklushåndtering og automatisk oppstart registrerer vi Firecrawl som en brukerbasert `systemd`-tjeneste som orkestrerer den underliggende Podman Compose-stacken. Dette lar OpenClaw starte gatewayen, stoppe og verifisere Firecrawl-tjenesten ved hjelp av standard `systemctl --user`-kommandoer i stedet for å interagere direkte med containerne.

For å holde det enkelt har vi delt hele prosessen inn i fire trinn:

---

### 1. Registrer systemtjenesten
Naviger til konfigurasjonskatalogen for systemd-brukeren:
```bash
cd ~/.config/systemd/user
```
Opprett og åpne en ny fil kalt `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopier og lim inn følgende konfigurasjon:
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
På dette tidspunktet er tjenesten definert, men ennå ikke registrert hos `systemd`.
Sørg for at filnavnet stemmer nøyaktig overens med det du opprettet ovenfor, og kjør deretter:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Hvis det lykkes, bør du se følgende utdata:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` inneholder symbolske lenker til tjenester som er konfigurert til å starte automatisk.
### 2. Konfigurer Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) er ideelt for de som trenger full kontroll over sine skraping- og databehandlingsmiljøer, men det medfører ekstra kostnader knyttet til vedlikehold og konfigurasjon.

Start med å klone repositoriet:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Opprett `.env` i rot-mappen `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Distribuer OpenClaw med Podman Compose

Før du går videre, sørg for at du har hentet det nyeste OpenClaw Docker-avbildet:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Når dette er gjort, laster du ned OpenClaw Compose-filen [openclaw-compose.yaml](assets/openclaw-compose.yaml) og plasserer den i rot-mappen `/firecrawl`:

> Denne konvensjonen er nødvendig for at `systemd` skal kunne finne og starte tjenesten korrekt, slik det er angitt i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan alltid utvide stacken ved å legge til flere Firecrawl-tjenester etter behov. Den fullstendige listen over tilgjengelige tjenester finner du i den offisielle [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Start OpenClaw-tjenesten gjennom Firecrawl 

Før du overlater kontrollen til `systemd`, bør du bekrefte at alt fungerer korrekt ved å kjøre stacken manuelt:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Hvis alt er konfigurert riktig, skal du se OpenClaw-containeren starte opp, og kommandolinjeutdataene dine bør ligne på dette:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Når dette er bekreftet, tar du ned stacken igjen før du fortsetter:
```bash
podman compose -f openclaw-compose.yaml down
```
Før du starter tjenesten, må du sørge for at riktig eierskap og tillatelser er satt på `firecrawl`-mappen og dens `.env`-fil. 
Dette er avgjørende for at tjenesten skal kunne skrive legitimasjonen din ved oppstart.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nå som alt er bekreftet, starter du tjenesten via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw-handlingene](https://docs.openclaw.ai/) er tilgjengelige fra den interaktive containeren, og Web Dashboard er tilgjengelig på samme vert og port på http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Skaffe `OPENCLAW_GATEWAY_TOKEN`

Når tjenesten er oppe og kjører, vil du legge merke til at en ny `.openclaw`-mappe er opprettet i hjemmemappen din (~/.openclaw). Denne mappen er låst som standard, så du må låse den opp for å hente gateway-tokenet ditt.

1. Gi tilgang til mappen:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Les gateway-tokenet ditt:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Finn verdien `OPENCLAW_GATEWAY_TOKEN` i utdataene.

3. Åpne gateway-dashbordet i nettleseren din på http://127.0.0.1:18789. Lim inn tokenet ditt når du blir bedt om å autentisere.

For å stoppe tjenesten, kjør:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Start OpenClaw-gatewayen

Gatewayen er OpenClaw-prosessen som administrerer agent-loopen og betjener dashbordet:

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

For å åpne dashbordet, kjør dette i en andre terminal mens gatewayen fortsatt kjører:

```bash
openclaw dashboard
```

Fordi gatewayen bindes til loopback, autentiserer dashbordet automatisk når det åpnes fra samme maskin, det kreves ingen tokeninntasting eller enhetsgodkjenning for lokal tilgang. Du skal se OpenClaw-dashbordet med Lemonade-modellen din oppført som aktiv backend.

> Hvis du har aktivert sandkasse-funksjonalitet, kan du verifisere dette ved å be agenten om å `run hostname` fra dashbordet. Hvis du ser en kort container-ID i stedet for maskinens vertsnavn, fungerer sandkassen.

**Gratulerer, du har bygget en fullstendig lokal AI-agentstack fra bunnen av.**

> **Trenger du gateway-tokenet?** Kjør `openclaw dashboard --no-open` for å skrive ut dashboard-URL-en med tokenet innebygd (det forsøker også å kopiere det til utklippstavlen din). Alternativt finner du tokenet under `gateway.auth.token` i `~/.openclaw/openclaw.json`.
>
> **Godkjenne en ekstern enhet:** Når du åpner dashbordet fra en annen maskin eller telefon, viser nettleseren en forespørsels-ID. Tilbake på maskinen som kjører gatewayen, kjør:
> ```bash
> openclaw devices approve <requestId>
> ```
> Dette er kun nødvendig for eksterne eller sekundære enheter, loopback-tilgang fra samme maskin autentiserer automatisk.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valgfritt: Koble til en kommunikasjonskanal

Når gatewayen kjører, kan du nå din lokale agent fra hvilken som helst enhet. Velg alternativet som passer for oppsettet ditt. OpenClaw støtter [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), og andre kanaler, se den fullstendige listen på [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Alternativ A: Discord

Discord krever en server der **du har administratortilgang** for å legge til en bot. Hvis du deler servere, men ikke eier en, bruk Alternativ B (Telegram) i stedet.

#### Opprett en Discord-konto og server

Hvis du ikke har en Discord-konto, registrer deg på [discord.com](https://discord.com). Du trenger også en server der du er administrator. Opprett en ved å klikke på **+**-ikonet i Discord-sidepanelet og velge **Create My Own**. En privat server er greit.

#### Opprett en Discord-applikasjon og bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications) og klikk **New Application**. Gi den et navn (f.eks. «openclaw-bot»).
2. I sidepanelet klikker du på **Bot**. Angi et brukernavn for boten.
3. Fortsatt på Bot-siden, bla ned til **Privileged Gateway Intents** og aktiver:
   - **Message Content Intent** (påkrevd)
   - **Server Members Intent** (anbefalt)
4. Bla tilbake opp og klikk **Reset Token** for å generere bot-tokenet ditt. Kopier det.

#### Legg boten til på serveren din

1. I sidepanelet klikker du på **OAuth2/ URL Generator**.
2. Under **Scopes** aktiverer du `bot` og `applications.commands`.
3. Under **Bot Permissions** aktiverer du: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopier den genererte URL-en, lim den inn i nettleseren din, velg serveren din, og bekreft. Boten skal nå vises i medlemslisten til serveren din.
#### Samle inn ID-ene dine

Aktiver utviklermodus i Discord (**User Settings/ Advanced/ Developer Mode**), og deretter:
- Høyreklikk på serverikonet ditt: **Copy Server ID**
- Høyreklikk på din egen avatar: **Copy User ID**

#### Tillat DM-er fra servermedlemmer

Høyreklikk på serverikonet ditt/ **Privacy Settings**/ slå på **Direct Messages**. Dette lar boten sende deg DM-er, noe som kreves for paringstrinnet.

#### Konfigurer OpenClaw for Discord

Lagre bot-tokenet ditt som en miljøvariabel, og opprett deretter en enkelt patch-fil som aktiverer Discord, refererer til tokenet, og setter serveren din på allowlisten. Erstatt `<server_id>` og `<user_id>` med ID-ene du samlet inn ovenfor.

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

> **Ikke stol på å be agenten om å konfigurere dette.** Når sandboxing er aktivert, kan ikke agenten skrive til `~/.openclaw/openclaw.json` fra innsiden av sandboxen, bruk CLI-kommandoene ovenfor på verten i stedet.

Start gatewayen på nytt slik at den tar i bruk den nye kanalkonfigurasjonen:

```bash
openclaw gateway run --bind loopback --port 18789
```

Du bør se `logged in to discord as <bot-name>` i gateway-utdataen innen noen få sekunder.

#### Par Discord-kontoen din

Send en DM til boten i Discord. Den vil svare med en kort paringskode.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Godkjenn den på maskinen som kjører OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Paringskoder utløper etter én time.

Du kan nå chatte med agenten din direkte fra Discord og avlaste oppgaver til din lokale maskinvare.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Alternativ B: Telegram

Telegram er enklere enn Discord for de fleste brukere, det krever ingen server og ingen administratortilgang.

#### Opprett en Telegram-bot

1. Åpne Telegram og send en melding til **@BotFather**.
2. Send `/newbot` og følg instruksjonene. Lagre bot-tokenet du får.

#### Konfigurer OpenClaw for Telegram

Lagre tokenet som en miljøvariabel:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Legg til kanalkonfigurasjonen i `~/.openclaw/openclaw.json` (eller patch den via dashbordet):

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

Start gatewayen på nytt, og send deretter boten din en melding i Telegram. Godkjenn paringen:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Paringskoder utløper etter én time. Du kan nå chatte med agenten din via Telegram DM.

---

## Neste steg

Nå som agenten din kan motta kommandoer fra telefonen din og utføre handlinger på den lokale maskinen din, er her tre retninger det er verdt å utforske:

1. **Aksjemarkedssammendrag**: Planlegg OpenClaw til å hente data fra finansielle API-er med et fast intervall, oppsummer dagens bevegelser med den lokale modellen din, og send et sammendrag til telefonen din hver morgen via den valgte kanalen din.

2. **Overvåking av finjustering**: Start en treningsjobb eksternt via Telegram eller Discord, og la deretter agenten følge treningsloggen og rapportere periodiske tapsverdier, GPU-utnyttelse og diskbruk tilbake til telefonen din. Hvis kjøringen stopper opp eller VRAM-bruken øker brått, får du vite det umiddelbart uten å måtte være ved maskinen.

3. **IOT med en lokal VLM**: Rett et kamera mot inngangsdøren din, kjør en synsmodell på Lemonade, og la OpenClaw analysere bilderammer på forespørsel eller ved en utløser. Spør "kom det noen pakker i dag?" fra telefonen din og få et rett svar fra din egen maskinvare.

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