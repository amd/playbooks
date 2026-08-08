<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Kör Hermes Agent lokalt med Lemonade Server

## Översikt

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) är en självförbättrande AI-agent byggd av Nous Research. Den har en inbyggd inlärningsloop, den skapar färdigheter utifrån erfarenhet, bygger upp ett bestående minne av vem du är mellan sessioner och kan köra schemalagda automatiseringar åt dig. Till skillnad från en enkel chattassistent utför Hermes verkliga handlingar: kör skalkommandon, skriver filer, surfar på webben och delegerar parallella arbetsflöden till underagenter.

[**Lemonade Server**](https://lemonade-server.ai/) är den lokala inferens-backend som driver den. Det är en öppen källkodsserver som kör GenAI-modeller direkt på din AMD-hårdvara och exponerar dem via det branschstandardiserade OpenAI API:et.

Tillsammans utgör de en helt lokal AI-agentstack: Lemonade hanterar modellinferens på din GPU, och Hermes tillhandahåller agentloopen, minnet, färdigheterna och meddelandegatewayen.

> **Innan du fortsätter:** Hermes Agent är en mycket autonom AI-agent. Att ge en AI-agent åtkomst till ditt system kan leda till oförutsägbara eller oavsiktliga resultat. Fortsätt endast om du förstår riskerna och känner dig bekväm med att autonom programvara agerar å dina vägnar.

---

## Vad du kommer att lära dig

Efter att ha slutfört den här guiden kommer du att kunna:

- **Installera Hermes Agent** och koppla den till **Lemonade Server** som dess AI-backend.
- **(Rekommenderas) Aktivera Docker/Podman-sandlådor** för att isolera agentens åtgärder från din värddator.
- **Starta Hermes-gatewayen** och bekräfta att din agent är redo.
- **Ansluta en kommunikationskanal** (Discord eller Telegram) så att du kan chatta med din agent från vilken enhet som helst.

---

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvaruförutsättningar

<!-- @os:linux -->
- En dator som kör **Ubuntu 24.04+** eller en kompatibel Debian-baserad Linux-distribution med `apt-get`
- Minst **12 GB RAM** (64 GB+ rekommenderas för större modeller)
- **~10–30 GB ledigt diskutrymme** för modellvikter
- [Podman](https://podman.io/docs/installation) (Valfritt, för sandlådekörning av Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- En dator som kör **Windows 10/11**
- Minst **12 GB RAM** (64 GB+ rekommenderas för större modeller)
- **~10–30 GB ledigt diskutrymme** för modellvikter
- Podman (Valfritt, för sandlådekörning av Hermes Agent). Installera inuti WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman är förinstallerat på Halo Box och ingen konfiguration krävs
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hämta och läs in den rekommenderade modellen

Den rekommenderade modellen för den här guiden är **Qwen3.6-35B-A3B-GGUF** från Unsloth, en kraftfull MoE-modell med ett kontextfönster på 263k token som passar väl för agentarbetsbelastningar. Denna modell använder UD-Q4_K_XL-kvantisering. Hämta den nu:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Läs sedan in den med ett stort kontextfönster och spara den inställningen för framtida körningar:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Modellen har en standardkontextlängd på 262 144 token. Om du stöter på fel med slut på minne (OOM) kan du överväga att minska kontextfönstret.

> **Tips: Inaktivera tänkande för snabbare agentsvar:** Qwen3.6-35B-A3B körs i tänkarläge som standard, vilket lägger till fördröjning innan varje svar. I agentloopar ackumuleras denna overhead snabbt. Repositoriet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tillhandahåller en färdig konfiguration som inaktiverar tänkande. För att använda den, hämta filen och importera den:
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

## Konfigurera WSL

Vi kör Hermes Agent inuti WSL och ansluter den till Lemonade som körs nativt på Windows. Detta ger dig en Linux-skalmiljö för Hermes samtidigt som Lemonades GPU-acceleration bibehålls på Windows-sidan.

### Installera WSL och Ubuntu

Öppna PowerShell som administratör och installera WSL-kärnan:

```powershell
wsl --install --no-distribution
```

Installera sedan Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Aktivera systemd i WSL

Kör detta i Ubuntu-terminalen:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Starta om WSL:

```powershell
wsl --shutdown
wsl
```

### Koppla samman Lemonade från Windows till WSL

WSL2 körs i ett virtuellt nätverk. Lemonade på Windows binder till `127.0.0.1`, vilket WSL inte kan nå direkt. En Windows-portproxy vidarebefordrar trafik från WSL-gatewayens IP-adress till Windows localhost.

**Hitta din WSL-gatewayens IP-adress** (kör inuti WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lägg till portproxyn** (kör i PowerShell som administratör och ersätt `<WSL-Gateway-IP>` med din WSL-gatewayens IP-adress):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Lägg till en brandväggsregel** (samma upphöjda PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifiera från WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Om du redan har läst in modellen Qwen3.6-35B-A3B-GGUF i föregående steg bör du se en JSON-utmatning som visar din inlästa modell.

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

> Regeln `netsh portproxy` överlever omstarter, men WSL-gatewayens IP-adress kan ändras efter `wsl --shutdown`. Om Lemonade blir onåbar från WSL efter en omstart, hämta den uppdaterade gateway-IP-adressen och uppdatera proxyn med den nya adressen.

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

## Installera Hermes Agent

<!-- @os:windows -->
> Kör kommandona i det här avsnittet i din **WSL-terminal** om inget annat anges.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Flaggan `--skip-setup` hoppar över den interaktiva installationsguiden så att du kan konfigurera modellbackenden manuellt i nästa steg.

Läs om ditt skal:

```bash
source ~/.bashrc
```

Bekräfta installationen:

```bash
hermes --version
```

Kör en självdiagnostik för att kontrollera alla beroenden:

```bash
hermes doctor
```

> **Tips:** Om du ser `command not found` efter installationen, lägg till Hermes i din PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> För att göra detta permanent, lägg till raden ovan i din `~/.bashrc` eller `~/.zshrc`.

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
## Konfigurera Hermes för att använda Lemonade

Hermes lagrar sin modellkonfiguration i `~/.hermes/config.yaml`. Du kan antingen använda den interaktiva `hermes model`-väljaren eller skriva konfigurationen direkt.

### Alternativ 1: Interaktiv väljare

<!-- @os:windows -->
> Kör följande i din **WSL-terminal**.
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

När du uppmanas:

1. Välj **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** använd WSL-gatewayens IP: kör `ip route show default | awk '{print $3}' | head -1` inuti WSL för att hämta den, ange sedan `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** välj `Qwen3.6-35B-A3B-GGUF` från listan
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (eller valfritt namn du föredrar)

`hermes model` sparar både det aktiva modellvalet och en namngiven `custom_providers`-post som lagrar kontextlängden tillsammans med slutpunkten. Resultatet i `~/.hermes/config.yaml` ser ut så här:

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

### Alternativ 2: Skriv konfigurationen direkt

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

Hämta Windows-värdens IP inuti din WSL-terminal och skriv konfigurationen:

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

## (Rekommenderat) Aktivera Podman-sandboxning

Hermes Agent kan dirigera alla agentens skal- och filoperationer genom en isolerad container istället för att köra dem direkt på din värd. Detta begränsar konsekvenserna av oavsiktliga åtgärder till sandlådan, vilket lämnar ditt värdfilsystem och nätverk opåverkat.

Bygg en lättviktig sandbox-avbildning:

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
Öppna din WSL-terminal:

```powershell
wsl -d Ubuntu-24.04
```

Bygg sedan en lättviktig sandbox-avbildning:

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

Konfigurera sedan Hermes att använda Podman som containerkörningsmiljö och ställ in terminalbackend:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` är fortfarande `docker`.
> `HERMES_DOCKER_BINARY` är det som talar om för Hermes att använda Podman som körningsmiljö istället.

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

Hermes kommer nu att starta en beständig sandbox-container och dirigera alla `terminal`- och filverktygsanrop genom den. Containern delar livslängd med Hermes-processen, återanvänds för alla verktygsanrop och förstörs när Hermes avslutas.

> **Verifiera att sandlådan fungerar:** Starta Hermes (`hermes`) och be den att `run hostname` - du bör se ett kort container-ID istället för din dators värdnamn. Du kan också be den att `rm -rf <path-to-a-dummy-file/folder>`: Hermes bekräftar borttagningen, men mappen finns fortfarande kvar på din värd. Kommandot kördes inuti containerns isolerade `$HOME`, inte din egen.

> **Behöver du starkare isolering?** Hermes tillhandahåller även en officiell Docker-avbildning (`nousresearch/hermes-agent`) som kör hela agentprocessen inuti en container - gateway, verktyg och allt. Se [Hermes Docker-dokumentationen](https://hermes-agent.nousresearch.com/docs/user-guide/docker) för installationsdetaljer.

---

<!-- @os:linux -->
## (Rekommenderat) Hermes-integration med Firecrawl-tjänster

Hermes kan bläddra och extrahera innehåll från webbplatser med hjälp av sina inbyggda webbverktyg. Många moderna webbplatser använder dock system för botdetektering, som blockerar enkla HTTP-förfrågningar och returnerar utmaningssidor istället för det faktiska innehållet. Som ett resultat kan Hermes vara oförmögen att pålitligt extrahera information från dessa webbplatser.

För att övervinna denna begränsning tillhandahåller [Firecrawl](https://docs.firecrawl.dev/introduction) en självhostad webbcrawlings- och innehållsextraktionstjänst som kan kringgå dessa utmaningar och frigöra Hermes automatiseringens fulla potential.

I denna installation körs Firecrawl som en uppsättning Docker-containrar hanterade med Podman. För att förenkla livscykelhantering och automatisk uppstart registrerar vi Firecrawl som en användarnivå-`systemd`-tjänst som orkestrerar den underliggande Podman Compose-stacken. Detta gör att Hermes kan starta, stoppa och verifiera Firecrawl-tjänsten med standard `systemctl --user`-kommandon istället för att interagera direkt med containrarna.

För att hålla det enkelt har vi delat upp hela processen i fyra steg:

---

### 1. Registrera systemtjänsten
Navigera till katalogen för systemd-användarkonfiguration:
```bash
cd ~/.config/systemd/user
```
Skapa och öppna en ny fil som heter `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopiera och klistra in följande konfiguration:
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
Vid denna punkt har tjänsten definierats men ännu inte registrerats hos `systemd`.
Se till att filnamnet matchar exakt det du skapade ovan, kör sedan:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Om det lyckas bör du se följande utdata:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` innehåller symboliska länkar till tjänster som är konfigurerade att starta automatiskt.

### 2. Konfigurera Firecrawl för din tjänst

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) är idealisk för de som behöver full kontroll över sina scraping- och databehandlingsmiljöer, men kommer med kompromissen av ytterligare underhåll och konfigurationsarbete.

Börja med att klona repositoryt:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Skapa `.env` i rotkatalogen `/firecrawl`:
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
> Ställ in `BULL_AUTH_KEY` till en stark hemlighet, särskilt vid alla distributioner som är nåbara från opålitliga nätverk.
### 3. Distribuera Hermes via Compose

Innan du går vidare, se till att du har hämtat den senaste Hermes Docker-avbildningen:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
När det är klart, ladda ner Hermes Compose-filen [hermes-compose.yaml](assets/hermes-compose.yaml) och placera den i rotkatalogen `/firecrawl`:

> Denna konvention krävs för att `systemd` ska kunna hitta och starta tjänsten korrekt enligt vad som anges i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan alltid utöka stacken genom att lägga till fler Firecrawl-tjänster efter behov. Den fullständiga listan över tillgängliga tjänster finns i den officiella [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Starta Hermes-tjänsten via Firecrawl 

Innan du överlämnar kontrollen till `systemd`, kontrollera att allt fungerar korrekt genom att köra stacken manuellt:
```bash
podman compose -f hermes-compose.yaml up -d
```
Om allt är korrekt konfigurerat bör du se Hermes-behållaren starta och kommandoradsutmatningen bör se ut ungefär så här:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

När du har verifierat detta, ta ner stacken innan du fortsätter:
```bash
podman compose -f hermes-compose.yaml down
```
Nu när allt är verifierat, starta tjänsten via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) är tillgängligt inifrån den interaktiva behållaren, och webbdashboarden finns tillgänglig på samma värd och port på http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

För att stoppa tjänsten, kör:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Starta en interaktiv CLI-session direkt: 

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

**Grattis, du har byggt en helt lokal AI-agentstack.**

### Webbdashboard

Hermes innehåller ett webbläsarbaserat gränssnitt för att hantera konfiguration, API-nycklar, modeller, sessioner, minne och cron-jobb. Öppna en andra terminal medan gatewayen eller CLI:n körs och starta det med:

```bash
hermes dashboard
```

Detta startar en lokal server och öppnar `http://127.0.0.1:9119` i din webbläsare. Se [dashboard-dokumentationen](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) för den fullständiga funktionsreferensen.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Valfritt: Anslut en kommunikationskanal

När gatewayen körs kan du nå din lokala agent från valfri enhet. Hermes stöder [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) och andra

---

### Discord

Discord kräver en server där **du har administratörsbehörighet** för att lägga till en bot. Om du delar servrar men inte äger någon, använd Telegram istället.

#### Skapa en Discord-applikation och bot

1. Gå till [Discord Developer Portal](https://discord.com/developers/applications) och klicka på **New Application**. Ge den ett namn (t.ex. "hermes-bot").
2. I sidofältet klickar du på **Bot**. Ange ett användarnamn för boten.
3. Fortfarande på Bot-sidan, bläddra ner till **Privileged Gateway Intents** och aktivera:
   - **Message Content Intent** (krävs)
   - **Server Members Intent** (rekommenderas)
4. Bläddra tillbaka upp och klicka på **Reset Token** för att generera din bot-token. Kopiera den.

#### Lägg till boten på din server

1. I sidofältet klickar du på **OAuth2 / URL Generator**.
2. Under **Scopes**, aktivera `bot` och `applications.commands`.
3. Under **Bot Permissions**, aktivera: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopiera den genererade URL:en, klistra in den i din webbläsare, välj din server och bekräfta.

#### Samla in dina ID:n och tillåt DM

Aktivera utvecklarläge i Discord (**User Settings / Advanced / Developer Mode**), sedan:
- Högerklicka på din serverikon: **Copy Server ID**
- Högerklicka på din egen avatar: **Copy User ID**

Högerklicka på din serverikon / **Privacy Settings** / aktivera **Direct Messages**. Detta krävs för parkopplingssteget.

#### Konfigurera Hermes för Discord

Lägg till följande i `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Starta sedan gatewayen:

```bash
hermes gateway
```

Boten bör komma online i Discord inom några sekunder. Skicka ett meddelande till den, antingen ett DM eller i en kanal den kan se.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Skapa en Telegram-bot

1. Öppna Telegram och skicka ett meddelande till **@BotFather**.
2. Skicka `/newbot` och följ anvisningarna. Spara boten-token du får.

#### Konfigurera Hermes för Telegram

Lägg till följande i `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Vet du inte ditt Telegram-användar-ID?** Skicka ett meddelande till [@userinfobot](https://t.me/userinfobot) i Telegram, så svarar den med ditt numeriska ID.

Starta sedan gatewayen:

```bash
hermes gateway
```

Skicka ett meddelande till din bot i Telegram för att testa. Du kan nu chatta med din agent via Telegram DM. Se [den fullständiga installationsguiden för Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) för webhook-läge och avancerade alternativ.

---

## Nästa steg

Nu när din agent kan ta emot kommandon från din telefon och agera på din lokala dator, här är tre riktningar värda att utforska:

1. **Automatiserat forskningssammandrag**: Schemalägg Hermes att söka på webben efter ämnen du bryr dig om varje morgon, sammanfatta resultaten med din lokala modell och skicka ett sammandrag till din telefon via Telegram eller Discord, allt körande på din egen hårdvara utan molnkostnader.

2. **Kodgranskning på begäran**: Peka Hermes mot ett GitHub-repository, be den granska öppna pull requests, och låt den posta kommentarer eller en sammanfattning tillbaka till din chatt. Med Docker-terminalens backend körs alla git-operationer inuti sandlådan, vilket håller din värddator ren.

3. **Lokal filassistent**: Ge Hermes tillgång till en arbetskatalog och be den organisera, byta namn på, sammanfatta eller omvandla filer på begäran från din telefon. Eftersom Docker-terminalens backend begränsar alla skrivningar till sandlådans arbetsyta, hålls oavsiktliga destruktiva operationer under kontroll.