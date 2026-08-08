<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Kørsel af Hermes Agent lokalt med Lemonade Server

## Oversigt

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) er en selvforbedrende AI-agent bygget af Nous Research. Den har en indbygget læringssløjfe, den opbygger færdigheder ud fra erfaring, opbygger en vedvarende hukommelse om hvem du er på tværs af sessioner, og kan køre planlagte automatiseringer på dine vegne. I modsætning til en simpel chatassistent tager Hermes reelle handlinger: kører shell-kommandoer, skriver filer, browser på nettet og uddelegerer parallelle arbejdsstrømme til subagenter.

[**Lemonade Server**](https://lemonade-server.ai/) er den lokale inferens-backend, der driver den. Det er en open source-server, der kører GenAI-modeller direkte på din AMD-hardware og eksponerer dem gennem den branchestandardiserede OpenAI API.

Sammen udgør de en fuldt lokal AI-agent-stak: Lemonade håndterer modelinferens på din GPU, og Hermes leverer agentsløjfen, hukommelsen, færdighederne og messaging-gatewayen.

> **Før du fortsætter:** Hermes Agent er en meget autonom AI-agent. At give en AI-agent adgang til dit system kan resultere i uforudsigelige eller utilsigtede resultater. Fortsæt kun, hvis du forstår risiciene og er tryg ved, at autonom software handler på dine vegne.

---

## Hvad du vil lære

Ved slutningen af denne vejledning vil du kunne:

- **Installere Hermes Agent** og pege den mod **Lemonade Server** som sin AI-backend.
- **(Anbefalet) Aktivere Docker/Podman-sandboxing** for at isolere agentens handlinger fra din host.
- **Starte Hermes-gatewayen** og bekræfte, at din agent er klar.
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
- **~10-30 GB ledig diskplads** til modelvægte
- [Podman](https://podman.io/docs/installation) (Valgfrit, til sandboxing af Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- En pc, der kører **Windows 10/11**
- Mindst **12 GB RAM** (64 GB+ anbefales til større modeller)
- **~10-30 GB ledig diskplads** til modelvægte
- Podman (Valgfrit, til sandboxing af Hermes Agent). Installer inde i WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman er forudinstalleret på Halo Box, og ingen opsætning er nødvendig
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hent og indlæs den anbefalede model

Den anbefalede model til denne vejledning er **Qwen3.6-35B-A3B-GGUF** fra Unsloth, en stærk MoE-model med et 263k-token kontekstvindue, som er velegnet til agentarbejdsbelastninger. Denne model bruger UD-Q4_K_XL-kvantisering. Hent den nu:

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

Modellen har en standard kontekstlængde på 262.144 tokens. Hvis du støder på out-of-memory (OOM)-fejl, kan du overveje at reducere kontekstvinduet.

> **Tip: Deaktiver tænkning for hurtigere agentsvar:** Qwen3.6-35B-A3B kører som standard i tænketilstand, hvilket tilføjer ventetid før hvert svar. For agentsløjfer akkumuleres denne overhead hurtigt. Repoet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tilbyder en færdiglavet konfiguration, der deaktiverer tænkning. For at bruge den skal du downloade filen og importere den:
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

## Opsætning af WSL

Vi kører Hermes Agent inde i WSL og forbinder den til Lemonade, der kører nativt på Windows. Dette giver dig et Linux-shellmiljø til Hermes, mens Lemonades GPU-acceleration bevares på Windows-siden.

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

### Bro fra Windows til WSL for Lemonade

WSL2 kører i et virtuelt netværk. Lemonade på Windows binder til `127.0.0.1`, som WSL ikke kan tilgå direkte. En Windows-portproxy videresender trafik fra WSL-gateway-IP'en til Windows localhost.

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

**Bekræft fra WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Hvis du allerede har indlæst modellen Qwen3.6-35B-A3B-GGUF i det forrige trin, bør du se JSON-output, der viser din indlæste model.

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

> `netsh portproxy`-reglen overlever genstarter, men WSL-gateway-IP'en kan ændre sig efter `wsl --shutdown`. Hvis Lemonade bliver utilgængelig fra WSL efter en genstart, skal du hente den opdaterede gateway-IP og opdatere proxyen med denne nye IP.

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
> Kør kommandoerne i dette afsnit inde i din **WSL-terminal**, medmindre andet er angivet.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Flaget `--skip-setup` springer den interaktive opsætningsguide over, så du kan konfigurere modelbackenden manuelt i det næste trin.

Genindlæs din shell:

```bash
source ~/.bashrc
```

Bekræft installationen:

```bash
hermes --version
```

Kør en selvdiagnose for at tjekke alle afhængigheder:

```bash
hermes doctor
```

> **Tip:** Hvis du ser `command not found` efter installationen, skal du tilføje Hermes til din PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> For at gøre dette permanent skal du tilføje linjen ovenfor til din `~/.bashrc` eller `~/.zshrc`.

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
## Konfigurer Hermes til at bruge Lemonade

Hermes gemmer sin modelkonfiguration i `~/.hermes/config.yaml`. Du kan enten bruge den interaktive `hermes model`-vælger eller skrive konfigurationen direkte.

### Mulighed 1: Interaktiv vælger

<!-- @os:windows -->
> Kør følgende inde i din **WSL-terminal**.
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

Når du bliver bedt om det:

1. Vælg **Custom endpoint (indtast URL manuelt)**
<!-- @os:linux -->
2. **API-basis-URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API-basis-URL:** brug WSL-gateway-IP'en: kør `ip route show default | awk '{print $3}' | head -1` inde i WSL for at få den, og indtast derefter `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API-nøgle:** `lemonade`
4. **API-kompatibilitetstilstand:** `1` (Auto-detect)
5. **Vælg model:** vælg `Qwen3.6-35B-A3B-GGUF` fra listen
6. **Kontekstlængde i tokens:** `262144`
7. **Visningsnavn:** `local-lemonade` (eller et hvilket som helst navn, du foretrækker)

`hermes model` gemmer både det aktive modelvalg og en navngivet `custom_providers`-post, der gemmer kontekstlængden sammen med endpointet. Resultatet i `~/.hermes/config.yaml` ser sådan ud:

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

### Mulighed 2: Skriv konfigurationen direkte

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

Inde i din WSL-terminal skal du hente Windows-værtens IP og skrive konfigurationen:

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

## (Anbefalet) Aktiver Podman-sandboxing

Hermes Agent kan dirigere alle agentens shell- og filoperationer gennem en isoleret container i stedet for at køre dem direkte på din vært. Dette begrænser konsekvenserne af enhver utilsigtet handling til sandboxen og efterlader din værts filsystem og netværk uberørt.

Byg et letvægts-sandbox-image:

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
Gå ind i din WSL-terminal:

```powershell
wsl -d Ubuntu-24.04
```

Byg derefter et letvægts-sandbox-image:

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

Konfigurer derefter Hermes til at bruge Podman som container-runtime, og indstil terminal-backend'en:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` er stadig `docker`.
> `HERMES_DOCKER_BINARY` er det, der fortæller Hermes at bruge Podman som runtime i stedet.

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

Hermes vil nu starte en vedvarende sandbox-container og dirigere alle `terminal`- og filværktøjskald gennem den. Containeren deler levetid med Hermes-processen, genbruges til alle værktøjskald og destrueres, når Hermes afsluttes.

> **Bekræft, at sandboxen fungerer:** Start Hermes (`hermes`), og bed den om at `run hostname` - du skulle se et kort container-ID i stedet for din maskines værtsnavn. Du kan også bede den om at `rm -rf <path-to-a-dummy-file/folder>`: Hermes vil bekræfte sletningen, men mappen vil stadig være på din vært. Kommandoen blev kørt inde i containerens isolerede `$HOME`, ikke din.

> **Har du brug for stærkere isolation?** Hermes tilbyder også et officielt Docker-image (`nousresearch/hermes-agent`), der kører hele agentprocessen inde i en container - gateway, værktøjer og det hele. Se [Hermes' Docker-dokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/docker) for detaljer om opsætning.

---

<!-- @os:linux -->
## (Anbefalet) Hermes-integration med Firecrawl-tjenester

Hermes kan gennemse og udtrække indhold fra websites ved hjælp af sine indbyggede webværktøjer. Mange moderne websites bruger dog bot-detektionssystemer, som blokerer simple HTTP-anmodninger og returnerer challenge-sider i stedet for det faktiske indhold. Som følge heraf kan Hermes muligvis ikke pålideligt udtrække information fra disse sites.

For at overvinde denne begrænsning tilbyder [Firecrawl](https://docs.firecrawl.dev/introduction) en selv-hostet web crawling- og indholdsudtrækningstjeneste, der kan omgå disse udfordringer og frigøre det fulde potentiale i Hermes-automatisering. 

I denne opsætning kører Firecrawl som et sæt Docker-containere, der administreres med Podman. For at forenkle livscyklushåndtering og automatisk opstart registrerer vi Firecrawl som en brugerniveau-`systemd`-tjeneste, der orkestrerer den underliggende Podman Compose-stack. Dette gør det muligt for Hermes at starte, stoppe og verificere Firecrawl-tjenesten ved hjælp af standard `systemctl --user`-kommandoer i stedet for at interagere direkte med containerne.

For at holde det enkelt har vi opdelt hele processen i fire trin:

---

### 1. Registrer systemtjenesten
Naviger til systemd-brugerkonfigurationsmappen:
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
På dette tidspunkt er tjenesten blevet defineret, men endnu ikke registreret hos `systemd`. 
Sørg for, at filnavnet nøjagtigt matcher det, du oprettede ovenfor, og kør derefter:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Hvis det lykkes, skulle du se følgende output:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` indeholder symbolske links til tjenester, der er konfigureret til at starte automatisk.

### 2. Konfigurer Firecrawl til din tjeneste

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) er ideel for dem, der har brug for fuld kontrol over deres scraping- og databehandlingsmiljøer, men kommer med den ulempe, at det kræver ekstra vedligeholdelse og konfiguration.

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
> Sæt `BULL_AUTH_KEY` til en stærk hemmelighed, især ved enhver deployment, der kan tilgås fra utroværdige netværk.
### 3. Deployering af Hermes via Compose

Før du går videre, skal du sikre dig, at du har hentet det nyeste Hermes Docker-image:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Når det er gjort, downloades Hermes Compose-filen [hermes-compose.yaml](assets/hermes-compose.yaml), som placeres i rodmappen `/firecrawl`:

> Denne konvention er nødvendig, for at `systemd` kan finde og starte tjenesten korrekt, som angivet i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan altid udvide stakken ved at tilføje yderligere Firecrawl-tjenester efter behov. Den fulde liste over tilgængelige tjenester findes i den officielle [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Start Hermes-tjenesten via Firecrawl 

Før du overlader kontrollen til `systemd`, skal du validere, at alt fungerer korrekt ved at køre stakken manuelt:
```bash
podman compose -f hermes-compose.yaml up -d
```
Hvis alt er konfigureret korrekt, bør du se Hermes-containeren starte op, og din kommandolinje-output bør se nogenlunde sådan ud:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Når det er verificeret, skal du lukke stakken ned igen, før du fortsætter:
```bash
podman compose -f hermes-compose.yaml down
```
Nu hvor alt er valideret, starter du tjenesten via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Hermes API'et](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) er tilgængeligt fra den interaktive container, og Web Dashboard er tilgængeligt på samme host og port på http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

For at stoppe tjenesten skal du køre:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Start en interaktiv CLI-session direkte: 

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

**Tillykke, du har bygget en fuldt lokal AI-agentstak.**

### Web Dashboard

Hermes inkluderer en browserbaseret UI til styring af konfiguration, API-nøgler, modeller, sessioner, hukommelse og cron-jobs. Åbn en anden terminal, mens gatewayen eller CLI'en kører, og start den med:

```bash
hermes dashboard
```

Dette starter en lokal server og åbner `http://127.0.0.1:9119` i din browser. Se [dashboard-dokumentationen](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) for den fulde funktionsreference.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Valgfrit: Tilslut en kommunikationskanal

Når gatewayen kører, kan du tilgå din lokale agent fra enhver enhed. Hermes understøtter [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) og andre

---

### Discord

Discord kræver en server, hvor **du har administratoradgang** til at tilføje en bot. Hvis du deler servere, men ikke ejer en, kan du bruge Telegram i stedet.

#### Opret en Discord-applikation og bot

1. Gå til [Discord Developer Portal](https://discord.com/developers/applications), og klik på **New Application**. Giv den et navn (f.eks. "hermes-bot").
2. Klik på **Bot** i sidepanelet. Angiv et brugernavn til botten.
3. Fortsat på Bot-siden skal du scrolle ned til **Privileged Gateway Intents** og aktivere:
   - **Message Content Intent** (påkrævet)
   - **Server Members Intent** (anbefalet)
4. Scroll tilbage op, og klik på **Reset Token** for at generere din bot-token. Kopiér den.

#### Tilføj botten til din server

1. Klik på **OAuth2 / URL Generator** i sidepanelet.
2. Under **Scopes** skal du aktivere `bot` og `applications.commands`.
3. Under **Bot Permissions** skal du aktivere: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopiér den genererede URL, indsæt den i din browser, vælg din server, og bekræft.

#### Indsaml dine ID'er, og tillad DM'er

Aktivér Developer Mode i Discord (**User Settings / Advanced / Developer Mode**), og gør derefter følgende:
- Højreklik på dit server-ikon: **Copy Server ID**
- Højreklik på din egen avatar: **Copy User ID**

Højreklik på dit server-ikon / **Privacy Settings** / slå **Direct Messages** til. Dette er nødvendigt for parringstrinnet.

#### Konfigurer Hermes til Discord

Tilføj følgende til `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Start derefter gatewayen:

```bash
hermes gateway
```

Botten bør komme online i Discord i løbet af få sekunder. Send den en besked, enten en DM eller i en kanal, den kan se.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Opret en Telegram-bot

1. Åbn Telegram, og send en besked til **@BotFather**.
2. Send `/newbot`, og følg vejledningen. Gem bot-tokenet, du får udleveret.

#### Konfigurer Hermes til Telegram

Tilføj følgende til `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Kender du ikke dit Telegram-bruger-ID?** Send en besked til [@userinfobot](https://t.me/userinfobot) i Telegram, så svarer den med dit numeriske ID.

Start derefter gatewayen:

```bash
hermes gateway
```

Send din bot en besked i Telegram for at teste. Du kan nu chatte med din agent via Telegram DM. Se den [fulde Telegram-opsætningsguide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) for webhook-tilstand og avancerede indstillinger.

---

## Næste skridt

Nu hvor din agent kan modtage kommandoer fra din telefon og udføre handlinger på din lokale maskine, er her tre retninger, det kan være værd at udforske:

1. **Automatiseret forskningsopsummering**: Planlæg Hermes til at søge på nettet efter emner, du interesserer dig for, hver morgen, opsummere resultaterne med din lokale model og sende en opsummering til din telefon via Telegram eller Discord, alt sammen kørende på din egen hardware uden cloud-omkostninger.

2. **Kodegennemgang på forlangende**: Peg Hermes på et GitHub-repository, bed den om at gennemgå åbne pull requests, og lad den poste kommentarer eller en opsummering tilbage til din chat. Med Docker-terminal-backenden kører alle git-operationer inde i sandboxen, hvilket holder din host ren.

3. **Lokal filassistent**: Giv Hermes adgang til en arbejdsmappe, og bed den om at organisere, omdøbe, opsummere eller transformere filer på forlangende fra din telefon. Fordi Docker-terminal-backenden begrænser alle skrivninger til sandbox-arbejdsområdet, forbliver eventuelle utilsigtede destruktive handlinger indesluttet.