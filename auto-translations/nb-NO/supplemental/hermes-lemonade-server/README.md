<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Kjøre Hermes Agent lokalt med Lemonade Server

## Oversikt

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) er en selvforbedrende AI-agent bygget av Nous Research. Den har en innebygd læringsløkke, den skaper ferdigheter fra erfaring, bygger et vedvarende minne om hvem du er på tvers av økter, og kan kjøre planlagte automatiseringer på dine vegne. I motsetning til en enkel chat-assistent, utfører Hermes reelle handlinger: kjører shell-kommandoer, skriver filer, surfer på nettet, og delegerer parallelle arbeidsflyter til underagenter.

[**Lemonade Server**](https://lemonade-server.ai/) er den lokale inferens-backenden som driver den. Det er en åpen kildekode-server som kjører GenAI-modeller direkte på din AMD-maskinvare og eksponerer dem gjennom det bransjestandardiserte OpenAI API-et.

Sammen utgjør de en fullstendig lokal AI-agent-stakk: Lemonade håndterer modellinferens på GPU-en din, og Hermes tilbyr agentløkken, minne, ferdigheter og meldingsgateway.

> **Før du fortsetter:** Hermes Agent er en svært autonom AI-agent. Å gi en AI-agent tilgang til systemet ditt kan føre til uforutsigbare eller utilsiktede utfall. Fortsett kun hvis du forstår risikoen og er komfortabel med at autonom programvare handler på dine vegne.

---

## Hva du vil lære

Ved slutten av denne oppskriften vil du kunne:

- **Installere Hermes Agent** og peke den mot **Lemonade Server** som AI-backend.
- **(Anbefalt) Aktivere Docker/Podman-sandboxing** for å isolere agentens handlinger fra vertsmaskinen din.
- **Starte Hermes-gatewayen** og bekrefte at agenten din er klar.
- **Koble til en kommunikasjonskanal** (Discord eller Telegram) slik at du kan chatte med agenten din fra hvilken som helst enhet.

---

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

<!-- @os:linux -->
- En PC som kjører **Ubuntu 24.04+** eller en kompatibel Debian-basert Linux-distribusjon med `apt-get`
- Minst **12 GB RAM** (64 GB+ anbefales for større modeller)
- **~10–30 GB ledig diskplass** til modellvekter
- [Podman](https://podman.io/docs/installation) (valgfritt, for sandboxing av Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- En PC som kjører **Windows 10/11**
- Minst **12 GB RAM** (64 GB+ anbefales for større modeller)
- **~10–30 GB ledig diskplass** til modellvekter
- Podman (valgfritt, for sandboxing av Hermes Agent). Installer inne i WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman er forhåndsinstallert på Halo Box, og ingen oppsett er nødvendig
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hent og last inn den anbefalte modellen

Den anbefalte modellen for denne oppskriften er **Qwen3.6-35B-A3B-GGUF** fra Unsloth, en sterk MoE-modell med et kontekstvindu på 263k tokens som er godt egnet for agentarbeidsbelastninger. Denne modellen bruker UD-Q4_K_XL-kvantisering. Hent den nå:

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

Modellen har en standard kontekstlengde på 262 144 tokens. Hvis du støter på feil relatert til tomt minne (OOM), bør du vurdere å redusere kontekstvinduet.

> **Tips: Deaktiver «thinking» for raskere agentresponser:** Qwen3.6-35B-A3B kjører i thinking-modus som standard, noe som tilfører latens før hver respons. For agentløkker akkumuleres denne overheaden raskt. Repoet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tilbyr en ferdig konfigurasjon som deaktiverer thinking. For å bruke den, last ned filen og importer den:
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

## Sett opp WSL

Vi kjører Hermes Agent inne i WSL og kobler den til Lemonade som kjører nativt på Windows. Dette gir deg et Linux-skallmiljø for Hermes samtidig som Lemonades GPU-akselerasjon beholdes på Windows-siden.

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

### Bygg bro mellom Lemonade fra Windows og WSL

WSL2 kjører i et virtuelt nettverk. Lemonade på Windows binder seg til `127.0.0.1`, som WSL ikke kan nå direkte. En Windows-portproxy videresender trafikk fra WSL-gateway-IP-en til Windows localhost.

**Finn WSL-gateway-IP-en din** (kjør inne i WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Legg til portproxyen** (kjør i PowerShell som administrator, erstatt `<WSL-Gateway-IP>` med din WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Legg til en brannmurregel** (samme heve PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Bekreft fra WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Hvis du allerede har lastet inn Qwen3.6-35B-A3B-GGUF-modellen i det forrige trinnet, bør du se JSON-utdata som lister opp den innlastede modellen din.

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

> `netsh portproxy`-regelen overlever omstarter, men WSL-gateway-IP-en kan endre seg etter `wsl --shutdown`. Hvis Lemonade blir utilgjengelig fra WSL etter en omstart, hent den oppdaterte gateway-IP-en og oppdater proxyen med denne nye IP-en.

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

## Installer Hermes Agent

<!-- @os:windows -->
> Kjør kommandoene i denne seksjonen inne i **WSL-terminalen** din med mindre annet er angitt.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Flagget `--skip-setup` hopper over den interaktive oppsettsveiviseren slik at du kan konfigurere modellbackenden manuelt i neste trinn.

Last inn skallet ditt på nytt:

```bash
source ~/.bashrc
```

Bekreft installasjonen:

```bash
hermes --version
```

Kjør en selvdiagnose for å sjekke alle avhengigheter:

```bash
hermes doctor
```

> **Tips:** Hvis du ser `command not found` etter installasjonen, legg Hermes til i PATH-en din:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> For å gjøre dette permanent, legg linjen over til i `~/.bashrc` eller `~/.zshrc`.

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
## Konfigurer Hermes til å bruke Lemonade

Hermes lagrer modellkonfigurasjonen sin i `~/.hermes/config.yaml`. Du kan enten bruke den interaktive `hermes model`-velgeren eller skrive konfigurasjonen direkte.

### Alternativ 1: Interaktiv velger

<!-- @os:windows -->
> Kjør følgende inne i **WSL-terminalen** din.
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

Når du blir bedt om det:

1. Velg **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** bruk WSL-gateway-IP-en: kjør `ip route show default | awk '{print $3}' | head -1` inne i WSL for å få den, og skriv deretter inn `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** velg `Qwen3.6-35B-A3B-GGUF` fra listen
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (eller et navn du foretrekker)

`hermes model` lagrer både det aktive modellvalget og en navngitt `custom_providers`-oppføring som lagrer kontekstlengden sammen med endepunktet. Resultatet i `~/.hermes/config.yaml` ser slik ut:

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

### Alternativ 2: Skriv konfigurasjonen direkte

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

Inne i WSL-terminalen din, hent Windows-vertens IP og skriv konfigurasjonen:

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

## (Anbefalt) Aktiver Podman-sandkassing

Hermes Agent kan rute alle agentens skall- og filoperasjoner gjennom en isolert container i stedet for å kjøre dem direkte på verten din. Dette begrenser skadeomfanget av eventuelle utilsiktede handlinger til sandkassen, og lar filsystemet og nettverket på verten din være urørt.

Bygg et lettvekts sandkasse-image:

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
Gå inn i WSL-terminalen din:

```powershell
wsl -d Ubuntu-24.04
```

Bygg deretter et lettvekts sandkasse-image:

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

Konfigurer deretter Hermes til å bruke Podman som container-runtime og angi terminal-backend:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` er fortsatt `docker`.
> `HERMES_DOCKER_BINARY` er det som forteller Hermes å bruke Podman som runtime i stedet.

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

Hermes vil nå starte en vedvarende sandkasse-container og rute alle `terminal`- og filverktøykall gjennom den. Containeren deler levetid med Hermes-prosessen, gjenbrukes på tvers av alle verktøykall, og blir ødelagt når Hermes avsluttes.

> **Verifiser at sandkassen fungerer:** Start Hermes (`hermes`) og be den om å `run hostname` - du bør se en kort container-ID i stedet for maskinens vertsnavn. Du kan også be den om å `rm -rf <path-to-a-dummy-file/folder>`: Hermes vil bekrefte slettingen, men mappen vil fortsatt være på verten din. Kommandoen kjørte inne i containerens isolerte `$HOME`, ikke din.

> **Trenger du sterkere isolasjon?** Hermes tilbyr også et offisielt Docker-image (`nousresearch/hermes-agent`) som kjører hele agentprosessen inne i en container - gateway, verktøy og alt. Se [Hermes Docker-dokumentasjonen](https://hermes-agent.nousresearch.com/docs/user-guide/docker) for oppsettdetaljer.

---

<!-- @os:linux -->
## (Anbefalt) Hermes-integrasjon med Firecrawl-tjenester

Hermes kan bla gjennom og hente ut innhold fra nettsteder ved hjelp av sine innebygde nettverktøy. Mange moderne nettsteder bruker imidlertid bot-deteksjonssystemer, som blokkerer enkle HTTP-forespørsler og returnerer utfordringssider i stedet for det faktiske innholdet. Som et resultat kan Hermes være ute av stand til å pålitelig hente ut informasjon fra disse nettstedene.

For å overkomme denne begrensningen tilbyr [Firecrawl](https://docs.firecrawl.dev/introduction) en selvhostet nettcrawling- og innholdsuthentingstjeneste som kan omgå disse utfordringene og låse opp det fulle potensialet til Hermes-automatisering.

I dette oppsettet kjører Firecrawl som et sett med Docker-containere administrert med Podman. For å forenkle livssyklusadministrasjonen og automatisk oppstart registrerer vi Firecrawl som en brukernivå `systemd`-tjeneste som orkestrerer den underliggende Podman Compose-stakken. Dette lar Hermes starte, stoppe og verifisere Firecrawl-tjenesten ved hjelp av standard `systemctl --user`-kommandoer i stedet for å samhandle direkte med containere.

For å holde ting enkelt har vi delt opp hele prosessen i fire trinn:

---

### 1. Registrer systemtjenesten
Naviger til systemd-brukerkonfigurasjonskatalogen:
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
På dette tidspunktet er tjenesten definert, men ikke ennå registrert hos `systemd`.
Sørg for at filnavnet stemmer nøyaktig overens med det du opprettet ovenfor, og kjør deretter:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Hvis det lykkes, bør du se følgende output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` inneholder symbolske lenker til tjenester som er konfigurert til å starte automatisk.

### 2. Konfigurer Firecrawl for tjenesten din

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) er ideelt for dem som trenger full kontroll over sine skraping- og databehandlingsmiljøer, men kommer med avveiningen av ekstra vedlikeholds- og konfigurasjonsarbeid.

Start med å klone repositoriet:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Opprett `.env` i rotkatalogen `/firecrawl`:
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
> Sett `BULL_AUTH_KEY` til en sterk hemmelighet, spesielt på enhver distribusjon som er tilgjengelig fra usikrede nettverk.
### 3. Distribuere Hermes via Compose

Før du går videre, sørg for at du har hentet det nyeste Hermes Docker-bildet:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Når det er gjort, laster du ned Hermes Compose-filen [hermes-compose.yaml](assets/hermes-compose.yaml) og plasserer den i rotkatalogen `/firecrawl`:

> Denne konvensjonen er nødvendig for at `systemd` skal kunne finne og starte tjenesten riktig, slik det er angitt i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan alltid utvide stakken ved å legge til flere Firecrawl-tjenester etter behov. Den fullstendige listen over tilgjengelige tjenester finner du i den offisielle [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Start Hermes-tjenesten gjennom Firecrawl 

Før du overlater kontrollen til `systemd`, bør du validere at alt fungerer riktig ved å kjøre stakken manuelt:
```bash
podman compose -f hermes-compose.yaml up -d
```
Hvis alt er riktig konfigurert, skal du se Hermes-containeren komme opp, og kommandolinjeutskriften din skal ligne på dette:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Når det er bekreftet, tar du stakken ned igjen før du fortsetter:
```bash
podman compose -f hermes-compose.yaml down
```
Nå som alt er validert, starter du tjenesten gjennom `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Hermes API-et](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) er tilgjengelig fra innsiden av den interaktive containeren, og webdashbordet er tilgjengelig på samme vert og port på http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

For å stoppe tjenesten kjører du:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Start en interaktiv CLI-økt direkte: 

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

**Gratulerer, du har bygget en fullstendig lokal AI-agentstakk.**

### Web Dashboard

Hermes inkluderer et nettleserbasert brukergrensesnitt for å administrere konfigurasjon, API-nøkler, modeller, økter, minne og cron-jobber. Åpne en ny terminal mens gatewayen eller CLI-en kjører, og start det med:

```bash
hermes dashboard
```

Dette starter en lokal server og åpner `http://127.0.0.1:9119` i nettleseren din. Se [dokumentasjonen for dashbordet](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) for den fullstendige funksjonsreferansen.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Valgfritt: Koble til en kommunikasjonskanal

Når gatewayen kjører, kan du nå din lokale agent fra hvilken som helst enhet. Hermes støtter [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) og andre

---

### Discord

Discord krever en server der **du har administratortilgang** for å legge til en bot. Hvis du deler servere, men ikke eier en, bruker du Telegram i stedet.

#### Opprett en Discord-applikasjon og bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications) og klikk på **New Application**. Gi den et navn (f.eks. «hermes-bot»).
2. Klikk på **Bot** i sidepanelet. Angi et brukernavn for boten.
3. Fortsatt på Bot-siden, bla ned til **Privileged Gateway Intents** og aktiver:
   - **Message Content Intent** (påkrevd)
   - **Server Members Intent** (anbefalt)
4. Bla opp igjen og klikk på **Reset Token** for å generere bot-tokenet ditt. Kopier det.

#### Legg boten til på serveren din

1. Klikk på **OAuth2 / URL Generator** i sidepanelet.
2. Under **Scopes** aktiverer du `bot` og `applications.commands`.
3. Under **Bot Permissions** aktiverer du: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopier den genererte URL-en, lim den inn i nettleseren din, velg serveren din og bekreft.

#### Samle inn ID-ene dine og tillat DM-er

Aktiver utviklermodus i Discord (**User Settings / Advanced / Developer Mode**), og deretter:
- Høyreklikk på serverikonet ditt: **Copy Server ID**
- Høyreklikk på ditt eget avatarbilde: **Copy User ID**

Høyreklikk på serverikonet ditt / **Privacy Settings** / slå på **Direct Messages**. Dette er nødvendig for paringstrinnet.

#### Konfigurer Hermes for Discord

Legg til følgende i `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Start deretter gatewayen:

```bash
hermes gateway
```

Boten skal komme på nett i Discord i løpet av noen sekunder. Send den en melding, enten en DM eller i en kanal den kan se.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Opprett en Telegram-bot

1. Åpne Telegram og send en melding til **@BotFather**.
2. Send `/newbot` og følg instruksjonene. Lagre bot-tokenet du får.

#### Konfigurer Hermes for Telegram

Legg til følgende i `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Vet du ikke din Telegram-bruker-ID?** Send en melding til [@userinfobot](https://t.me/userinfobot) i Telegram, den vil svare med din numeriske ID.

Start deretter gatewayen:

```bash
hermes gateway
```

Send boten din en melding i Telegram for å teste. Du kan nå chatte med agenten din via Telegram-DM. Se [den fullstendige oppsettsguiden for Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) for webhook-modus og avanserte alternativer.

---

## Neste steg

Nå som agenten din kan motta kommandoer fra telefonen din og utføre handlinger på din lokale maskin, er her tre retninger verdt å utforske:

1. **Automatisert forskningssammendrag**: Planlegg at Hermes skal søke på nettet etter emner du bryr deg om hver morgen, oppsummere funnene med din lokale modell, og sende et sammendrag til telefonen din via Telegram eller Discord, alt kjørende på din egen maskinvare uten skykostnader.

2. **Kodegjennomgang på forespørsel**: Pek Hermes mot et GitHub-repositorium, be den om å gjennomgå åpne pull requests, og la den legge inn kommentarer eller et sammendrag tilbake i chatten din. Med Docker-terminalbackenden kjører alle git-operasjoner inne i sandkassen, noe som holder verten din ren.

3. **Lokal filassistent**: Gi Hermes tilgang til en arbeidskatalog og be den om å organisere, gi nytt navn til, oppsummere eller transformere filer på forespørsel fra telefonen din. Fordi Docker-terminalbackenden begrenser alle skriveoperasjoner til sandkasse-arbeidsområdet, holdes utilsiktede destruktive operasjoner under kontroll.