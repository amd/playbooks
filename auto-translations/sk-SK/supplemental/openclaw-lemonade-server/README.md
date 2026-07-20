<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Spustenie OpenClaw s Lemonade Server ako backendom

## Prehľad

[**OpenClaw**](https://openclaw.ai/) je autonómny AI agent, ktorý dokáže písať a spúšťať kód, spravovať súbory a vykonávať komplexné viacúrovňové úlohy vo vašom mene. Na rozdiel od chatového asistenta, ktorý len odpovedá na otázky, OpenClaw vykonáva skutočné akcie vo vašom systéme, čo znamená, že potrebuje rýchly a výkonný AI backend, ktorý dokáže držať krok s náročnou slučkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je práve takýto backend. Ide o open-source lokálny inferenčný server, ktorý spúšťa GenAI modely priamo na vašom hardvéri a sprístupňuje ich prostredníctvom priemyselne štandardného OpenAI API.

Spolu tvoria plne lokálny AI agentový stack: Lemonade sa stará o inferenciu modelu a OpenClaw poskytuje slučku agenta, ktorá premieňa výstupy modelu na skutočné akcie.

> **Skôr než budete pokračovať:** OpenClaw je vysoko autonómny AI agent. Poskytnutie prístupu k vášmu systému akémukoľvek AI agentovi môže viesť k nepredvídateľným alebo neúmyselným výsledkom. Pokračujte iba v prípade, že rozumiete rizikám a ste zmierení s tým, že softvér bude autonómne konať vo vašom mene.

---

## Čo sa naučíte

Na konci tohto návodu budete schopní:

- Zoznámiť sa s **Lemonade Server**
- **Nainštalovať OpenClaw** a **nasmerovať ho na Lemonade Server** ako svoj AI backend.
- **Spustiť gateway OpenClaw** a potvrdiť, že váš agent je pripravený na prácu.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli komunikovať so svojím agentom z ľubovoľného zariadenia.

---

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:linux -->
- PC so systémom **Ubuntu 24.04+** alebo kompatibilnou distribúciou Linuxu založenou na Debiane s `apt-get`
- Minimálne **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (voliteľné, na sandboxovanie OpenClaw)

- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
<!-- @os:end -->
<!-- @os:windows -->
- PC so systémom **Windows 10/11**
- Minimálne **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (voliteľné, na sandboxovanie OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stiahnutie a načítanie odporúčaného modelu

Odporúčaným modelom pre tento návod je **Qwen3.6-35B-A3B-GGUF** od Unsloth, silný MoE model s kontextovým oknom 263k tokenov, ktorý je vhodný pre agentové úlohy. Tento model používa kvantizáciu UD-Q4_K_XL. Stiahnite si ho teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Potom ho načítajte s veľkým kontextovým oknom a uložte toto nastavenie pre budúce spustenia:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má predvolenú kontextovú dĺžku 262 144 tokenov. Ak narazíte na chyby nedostatku pamäte (OOM), zvážte zmenšenie kontextového okna. Keďže však Qwen3.6 využíva rozšírený kontext pre komplexné úlohy, odporúčame zachovať kontextovú dĺžku aspoň 128K tokenov, aby sa zachovali schopnosti uvažovania.

> **Tip: Vypnite uvažovanie pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B beží predvolene v režime uvažovania, čo pridáva latenciu pred každou odpoveďou. Pri slučkách agenta sa táto réžia rýchlo kumuluje. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá vypína uvažovanie. Ak ju chcete použiť, stiahnite si súbor a importujte ho:
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

## Nastavenie WSL

OpenClaw spúšťame vnútri WSL (odporúčané) a pripájame ho k Lemonade, ktorý beží natívne na Windows. To vám poskytne linuxové shellové prostredie pre OpenClaw a zároveň zachová GPU akceleráciu Lemonade na strane Windows.

### Inštalácia WSL a Ubuntu

Otvorte PowerShell ako správca a nainštalujte jadro WSL:

```powershell
wsl --install --no-distribution
```

Potom nainštalujte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Povolenie systemd vo WSL

Spustite toto vnútri terminálu Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Reštartujte WSL:

```powershell
wsl --shutdown
wsl
```

### Premostenie Lemonade z Windows do WSL

WSL2 beží vo virtuálnej sieti. Lemonade na Windows je viazaný na `127.0.0.1`, ku ktorému sa WSL nemôže dostať priamo. Port proxy vo Windows presmeruje prevádzku z gateway IP WSL na localhost Windows.

**Zistite vašu gateway IP WSL** (spustite vnútri WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte port proxy** (spustite v PowerShell ako správca, pričom `<WSL-Gateway-IP>` nahraďte vašou gateway IP WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Pridajte pravidlo brány firewall** (rovnaký zvýšený PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Overte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ak ste už v predchádzajúcom kroku načítali model Qwen3.6-35B-A3B-GGUF, mali by ste vidieť JSON výstup podobný tomuto:

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

> Pravidlo `netsh portproxy` prežije reštarty, ale gateway IP WSL sa môže po `wsl --shutdown` zmeniť. Ak sa Lemonade po reštarte stane nedostupným z WSL, zistite aktualizovanú gateway IP a aktualizujte proxy touto novou IP.

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

## Inštalácia a konfigurácia OpenClaw

### Inštalácia OpenClaw
<!-- @os:windows -->
> Príkazy v tejto časti spúšťajte vnútri vášho **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Príznak `--no-onboard` preskočí interaktívneho sprievodcu nastavením, backend modelu nakonfigurujete manuálne v ďalšom kroku, čo vám poskytne presnú kontrolu nad tým, ktorý model a server sa použijú.

Otvorte nový terminál a potvrďte inštaláciu:

```bash
openclaw --version
```

> **Tip:** Ak sa po inštalácii zobrazí `command not found`, pridajte globálny bin adresár npm do PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ak to chcete zachovať natrvalo, pridajte vyššie uvedený riadok do súboru `~/.bashrc` alebo `~/.zshrc`.

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
### Konfigurácia OpenClaw na použitie Lemonade

Spustite neinteraktívne onboardingovanie OpenClaw.
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

Tento príkaz zapíše konfiguráciu OpenClaw do `~/.openclaw/openclaw.json`.

> **Nastavenie veľkosti kontextového okna v OpenClaw:** Kompaktovanie v OpenClaw sa spúšťa, keď `contextTokens > contextWindow − reserveTokens`. Predvolená hodnota `reserveTokensFloor` je 20 000 tokenov – ide o dolnú hranicu, ktorá prepíše `reserveTokens`, ak je nižšia, takže akýkoľvek kontext modelu pod ~37k spustí nekonečnú slučku kompaktovania. Nastavte v konfigurácii nízku rezervu a raz zakážte túto hranicu, a bude platiť pre každý model bez potreby ladenia pre jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *dolná hranica* (minimálna poistka), nie samotná rezerva – nastavenie iba hranice nemá žiadny efekt. `reserveTokensFloor: 0` zakáže túto poistku, takže sa akceptuje nižšia hodnota `reserveTokens`.
>
> **Kedy toto použiť:** Túto konfiguráciu použite, ak je efektívne kontextové okno vášho modelu menšie ako ~37k, či už preto, že model je malý (napr. 8k, 16k, 32k), alebo preto, že ste ho zámerne obmedzili na nižšiu hodnotu (napr. načítanie modelu so 128k, ale nastavenie kontextu v Lemonade na 16k). Bez toho OpenClaw pri spustení vstúpi do nekonečnej slučky kompaktovania.
>
> **Modely s veľkým kontextom pri plnom kontexte:** Toto môžete úplne preskočiť. Predvolené hodnoty fungujú dobre, kompaktovanie sa spustí ešte pred zaplnením okna a model má dostatok priestoru na generovanie dlhých odpovedí. Ak toto predsa len použijete, majte na pamäti, že `reserveTokens: 4096` obmedzí dĺžku odpovede na približne 4k tokenov, čo môže orezať dlhé generovanie súborov alebo podrobné plány.
>
> **Kam toto pridať:** Umiestnite blok `compaction` do `agents.defaults` vo vašom súbore `openclaw.json` (zvyčajne na `~/.openclaw/openclaw.json`):
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
> Zvyšok vašej konfigurácie (gateway, kanály, modely atď.) zostáva nezmenený, pridať treba iba kľúč `compaction`.

### (Odporúčané) Povolenie sandboxingu v Docker

OpenClaw dokáže smerovať všetky operácie agenta so súbormi a kódom cez izolovaný Docker kontajner namiesto ich priameho spúšťania na vašom hostiteľskom systéme. Tým sa dosah akejkoľvek neúmyselnej akcie obmedzí na sandbox, pričom súborový systém a sieť vášho hostiteľa zostanú nedotknuté.

Zostavte sandboxový image raz (Docker musí byť nainštalovaný):

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

Spustite toto, aby ste pridali kľúč `sandbox` do existujúceho bloku `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Sandboxové kontajnery predvolene **nemajú prístup k sieti**. Bind mounty a prepísanie sieťových nastavení nájdete v [referencii k sandboxingu](https://docs.openclaw.ai/gateway/sandboxing).

> #### Riešenie problémov: Docker – prístup zamietnutý
> 
> Ak sa vám pri spúšťaní príkazov Docker zobrazí chyba „permission denied“:
> 
> **Krok 1: Pridajte svojho používateľa do skupiny docker**
> 
> ```bash
> sudo groupadd docker                    # Vytvorenie skupiny, ak je potrebné
> sudo usermod -aG docker $USER           # Pridanie seba samého do skupiny
> newgrp docker                           # Aktivovanie zmeny
> docker run hello-world                  # Otestovanie
> ```
> 
> **Krok 2: Ak chyba pretrváva, použite trvalé riešenie**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Potom **reštartujte** systém.
> 
> **Rýchle dočasné riešenie** (po reštarte sa vynuluje):
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

### Spustenie brány OpenClaw (Gateway)

Gateway je proces OpenClaw, ktorý spravuje slučku agenta a poskytuje dashboard:

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

Ak chcete otvoriť dashboard, spustite toto v druhom termináli, kým gateway stále beží:

```bash
openclaw dashboard
```

Keďže gateway je viazaný na loopback, dashboard sa pri otvorení z toho istého počítača automaticky autentifikuje – na lokálny prístup nie je potrebné zadávať token ani schvaľovať zariadenie. Mali by ste vidieť dashboard OpenClaw s vaším modelom Lemonade uvedeným ako aktívny backend.

> Ak ste povolili sandboxing, môžete to overiť tak, že požiadate agenta, aby z dashboardu spustil `run hostname`. Ak sa namiesto názvu hostiteľa vášho počítača zobrazí krátke ID kontajnera, sandbox funguje.

**Blahoželáme, vytvorili ste od základov plne lokálny AI agentový stack.**

> **Potrebujete token pre gateway?** Spustite `openclaw dashboard --no-open`, čím sa vypíše URL adresa dashboardu so zabudovaným tokenom (tiež sa pokúsi skopírovať ho do schránky). Alternatívne sa token nachádza pod `gateway.auth.token` v súbore `~/.openclaw/openclaw.json`.
>
> **Schvaľovanie vzdialeného zariadenia:** Keď otvoríte dashboard z druhého počítača alebo telefónu, prehliadač zobrazí ID požiadavky. Späť na počítači, na ktorom beží gateway, spustite:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potrebné iba pre vzdialené alebo sekundárne zariadenia, prístup z loopbacku na tom istom počítači sa autentifikuje automaticky.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Po spustení gateway sa dostanete k svojmu lokálnemu agentovi z ľubovoľného zariadenia. Vyberte možnosť, ktorá vyhovuje vášmu nastaveniu. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a ďalšie kanály, úplný zoznam nájdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnosť A: Discord

Discord vyžaduje server, na ktorom **máte administrátorský prístup**, aby ste mohli pridať bota. Ak zdieľate servery, ale žiadny nevlastníte, použite namiesto toho možnosť B (Telegram).
#### Vytvorenie účtu a servera Discord

Ak nemáte účet Discord, zaregistrujte sa na [discord.com](https://discord.com). Potrebujete tiež server, na ktorom máte administrátorské práva. Vytvorte ho kliknutím na ikonu **+** na bočnom paneli Discordu a výberom možnosti **Create My Own**. Súkromný server postačuje.

#### Vytvorenie aplikácie a bota Discord

1. Prejdite do [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte mu názov (napr. „openclaw-bot").
2. Na bočnom paneli kliknite na **Bot**. Nastavte používateľské meno bota.
3. Na stránke Bot posuňte nadol na **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Posuňte sa späť nahor a kliknite na **Reset Token**, čím vygenerujete token vášho bota. Skopírujte si ho.

#### Pridanie bota na váš server

1. Na bočnom paneli kliknite na **OAuth2/ URL Generator**.
2. V sekcii **Scopes** povoľte `bot` a `applications.commands`.
3. V sekcii **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú adresu URL, vložte ju do prehliadača, vyberte svoj server a potvrďte. Bot by sa teraz mal zobraziť v zozname členov vášho servera.

#### Získanie vašich ID

Povoľte Developer Mode v Discorde (**User Settings/ Advanced/ Developer Mode**), potom:
- kliknite pravým tlačidlom na ikonu vášho servera: **Copy Server ID**
- kliknite pravým tlačidlom na svoj avatar: **Copy User ID**

#### Povolenie súkromných správ od členov servera

Kliknite pravým tlačidlom na ikonu vášho servera/ **Privacy Settings**/ zapnite **Direct Messages**. Toto umožní botovi poslať vám súkromnú správu, čo je potrebné pre krok párovania.

#### Konfigurácia OpenClaw pre Discord

Uložte token vášho bota ako premennú prostredia, potom vytvorte jeden patch súbor, ktorý zapne Discord, odkazuje na token a pridá váš server do zoznamu povolených. Nahraďte `<server_id>` a `<user_id>` ID získanými vyššie.

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

> **Nespoliehajte sa na to, že o túto konfiguráciu požiadate agenta.** Keď je povolený sandboxing, agent nemôže zapisovať do `~/.openclaw/openclaw.json` zvnútra sandboxu, namiesto toho použite vyššie uvedené CLI príkazy na hostiteľovi.

Reštartujte gateway, aby prevzal novú konfiguráciu kanála:

```bash
openclaw gateway run --bind loopback --port 18789
```

V priebehu niekoľkých sekúnd by sa mal vo výstupe gateway zobraziť riadok `logged in to discord as <bot-name>`.

#### Spárovanie vášho účtu Discord

Napíšte botovi súkromnú správu v Discorde. Odpovie krátkym párovacím kódom.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schváľte ho na počítači, na ktorom beží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnosť párovacích kódov vyprší po jednej hodine.

Teraz môžete chatovať so svojím agentom priamo z Discordu a presúvať úlohy na svoj lokálny hardvér.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnosť B: Telegram

Telegram je pre väčšinu používateľov jednoduchší ako Discord, nevyžaduje žiadny server ani administrátorský prístup.

#### Vytvorenie bota Telegram

1. Otvorte Telegram a napíšte správu **@BotFather**.
2. Odošlite `/newbot` a postupujte podľa pokynov. Uložte si token bota, ktorý dostanete.

#### Konfigurácia OpenClaw pre Telegram

Uložte token ako premennú prostredia:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Pridajte konfiguráciu kanála do `~/.openclaw/openclaw.json` (alebo ju upravte cez dashboard):

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

Reštartujte gateway, potom pošlite svojmu botovi ľubovoľnú správu v Telegrame. Schváľte párovanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnosť párovacích kódov vyprší po jednej hodine. Teraz môžete chatovať so svojím agentom prostredníctvom súkromných správ v Telegrame.

---

## Ďalšie kroky

Teraz, keď váš agent dokáže prijímať príkazy z vášho telefónu a vykonávať ich na vašom lokálnom počítači, tu sú tri smery, ktoré stojí za to preskúmať:

1. **Súhrn burzového trhu**: Naplánujte, aby OpenClaw v pravidelných intervaloch získaval dáta z finančných API, zhrnul denné pohyby pomocou vášho lokálneho modelu a odosielal súhrn na váš telefón každé ráno prostredníctvom vami zvoleného kanála.

2. **Monitorovanie fine-tuningu**: Spustite tréningovú úlohu na diaľku cez Telegram alebo Discord a nechajte agenta sledovať tréningový log a pravidelne hlásiť hodnoty loss, využitie GPU a stav disku na váš telefón. Ak sa beh zasekne alebo dôjde k skoku VRAM, dozviete sa to okamžite bez toho, aby ste museli byť pri počítači.

3. **IOT s lokálnym VLM**: Nasmerujte kameru na vaše vstupné dvere, spustite vision model na Lemonade a nechajte OpenClaw analyzovať snímky na požiadanie alebo pri spustení. Opýtajte sa „prišli dnes nejaké balíky?" zo svojho telefónu a dostanete priamu odpoveď z vlastného hardvéru.