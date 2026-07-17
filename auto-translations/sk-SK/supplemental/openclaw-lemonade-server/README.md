<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Spustite OpenClaw s Lemonade Server ako backendom

## Prehľad

[**OpenClaw**](https://openclaw.ai/) je autonómny AI agent, ktorý dokáže písať a spúšťať kód, spravovať súbory a zvládať zložité viacstupňové úlohy vo vašom mene. Na rozdiel od chatovacieho asistenta, ktorý len odpovedá na otázky, OpenClaw vykonáva skutočné akcie vo vašom systéme – čo znamená, že potrebuje rýchly a schopný AI backend, ktorý dokáže udržať krok s náročnou slučkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je práve takýto backend. Je to open-source lokálny inferenčný server, ktorý spúšťa modely GenAI priamo na vašom hardvéri a sprístupňuje ich prostredníctvom priemyselne štandardného OpenAI API.

Spolu tvoria plne lokálny zásobník AI agenta: Lemonade zabezpečuje inferenciu modelu a OpenClaw poskytuje slučku agenta, ktorá premieňa výstupy modelu na skutočné akcie.

> **Skôr než budete pokračovať:** OpenClaw je vysoko autonómny AI agent. Poskytnutie prístupu akéhokoľvek AI agenta k vášmu systému môže viesť k nepredvídateľným alebo neúmyselným výsledkom. Pokračujte iba vtedy, ak rozumiete rizikám a ste ochotní akceptovať, že autonómny softvér koná vo vašom mene.

---

## Čo sa naučíte

Po dokončení tohto návodu budete schopní:

- Dozvedieť sa o **Lemonade Server**
- **Nainštalovať OpenClaw** a **nasmerovať ho na Lemonade Server** ako jeho AI backend.
- **Spustiť bránu OpenClaw** a potvrdiť, že váš agent je pripravený pracovať.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli chatovať so svojím agentom z akéhokoľvek zariadenia.

---

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:linux -->
- PC s operačným systémom **Ubuntu 24.04+** alebo kompatibilnou distribúciou Linuxu založenou na Debiane s `apt-get`
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Voliteľné, na izoláciu OpenClaw)

- **~10–30 GB voľného miesta na disku** pre váhy modelu
<!-- @os:end -->
<!-- @os:windows -->
- PC s operačným systémom **Windows 10/11**
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10–30 GB voľného miesta na disku** pre váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Voliteľné, na izoláciu OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stiahnite a načítajte odporúčaný model

Odporúčaný model pre tento návod je **Qwen3.6-35B-A3B-GGUF** od Unsloth, silný model MoE s kontextovým oknom 263k tokenov, ktorý je vhodný pre záťaže agentov. Tento model používa kvantizovaciu metódu UD-Q4_K_XL. Stiahnite ho teraz:

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

Predvolená dĺžka kontextu modelu je 262 144 tokenov. Ak narazíte na chyby nedostatku pamäte (OOM), zvážte zníženie kontextového okna. Keďže však Qwen3.6 využíva rozšírený kontext pre zložité úlohy, odporúčame zachovať dĺžku kontextu aspoň 128K tokenov, aby sa zachovali schopnosti myslenia.

> **Tip: Vypnite myslenie pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B štandardne beží v režime myslenia, čo pred každou odpoveďou pridáva latenciu. V slučkách agentov sa táto réžia rýchlo hromadí. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá myslenie vypína. Ak ju chcete použiť, stiahnite súbor a importujte ho:
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

OpenClaw spúšťame vo vnútri WSL (odporúčané) a pripájame ho k Lemonade bežiacemu natívne na Windows. Tým získate prostredie linuxového shellu pre OpenClaw, pričom GPU akcelerácia Lemonade zostáva na strane Windows.

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

Spustite toto vo vnútri terminálu Ubuntu:

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

WSL2 beží vo virtuálnej sieti. Lemonade na Windows sa viaže na `127.0.0.1`, ktorý WSL nemôže priamo dosiahnuť. Proxy port Windows presmeruje prevádzku z IP adresy brány WSL na localhost Windows.

**Nájdite IP adresu brány WSL** (spustite vo vnútri WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte proxy port** (spustite v PowerShell ako správca, nahraďte `<WSL-Gateway-IP>` IP adresou vašej brány WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Pridajte pravidlo brány firewall** (rovnaký PowerShell so zvýšenými oprávneniami):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Overte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ak ste v predchádzajúcom kroku už načítali model Qwen3.6-35B-A3B-GGUF, mali by ste vidieť výstup JSON podobný tomuto:

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

> Pravidlo `netsh portproxy` prežije reštarty, ale IP adresa brány WSL sa môže zmeniť po `wsl --shutdown`. Ak sa Lemonade stane nedostupným z WSL po reštarte, získajte aktualizovanú IP adresu brány a aktualizujte proxy s touto novou IP adresou.

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
> Príkazy v tejto časti spúšťajte vo vnútri vášho **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Príznak `--no-onboard` preskočí interaktívneho sprievodcu nastavením – backend modelu nakonfigurujete manuálne v nasledujúcom kroku, čo vám dáva presnú kontrolu nad tým, ktorý model a server sa použijú.

Otvorte nový terminál a potvrďte inštaláciu:

```bash
openclaw --version
```

> **Tip:** Ak po inštalácii vidíte `command not found`, pridajte globálny adresár bin npm do vašej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby bola táto zmena trvalá, pridajte vyššie uvedený riadok do súboru `~/.bashrc` alebo `~/.zshrc`.

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


### Konfigurácia OpenClaw na používanie Lemonade

Spustite neinteraktívne zavádzanie OpenClaw.
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

> **Veľkosť kontextového okna OpenClaw:** Kompakcia OpenClaw sa spustí, keď `contextTokens > contextWindow − reserveTokens`. Predvolená hodnota `reserveTokensFloor` je 20 000 tokenov – spodná hranica, ktorá prepíše `reserveTokens`, keď je nižšia – takže akýkoľvek kontext modelu pod ~37k spustí nekonečnú slučku kompakcie. Nastavte nízku rezervu a jednorazovo vypnite spodnú hranicu vo vašej konfigurácii a toto nastavenie sa vzťahuje na každý model bez potreby ladenia pre jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodná hranica* (minimálna ochrana), nie samotná rezerva – nastavenie iba spodnej hranice nemá žiadny efekt. `reserveTokensFloor: 0` vypína ochranu, takže nižšia hodnota `reserveTokens` je akceptovaná.
>
> **Kedy to použiť:** Použite túto konfiguráciu, ak je efektívne kontextové okno vášho modelu pod ~37k, buď preto, že model je malý (napr. 8k, 16k, 32k), alebo preto, že ste ho zámerne obmedzili na nižšiu hodnotu (napr. načítanie modelu 128k, ale nastavenie kontextu na 16k v Lemonade). Bez toho OpenClaw pri spustení vstúpi do nekonečnej slučky kompakcie.
>
> **Veľké kontextové modely pri plnom kontexte:** Toto môžete úplne preskočiť. Predvolené nastavenia fungujú dobre – kompakcia sa spustí ešte pred naplnením okna a model má dostatok priestoru na generovanie dlhých odpovedí. Ak to predsa len použijete, majte na pamäti, že `reserveTokens: 4096` obmedzuje dĺžku odpovede na ~4k tokenov, čo môže prerušiť dlhé generovanie súborov alebo podrobné plány.
>
> **Kde to pridať:** Umiestnite blok `compaction` do `agents.defaults` vo vašom `openclaw.json` (zvyčajne na `~/.openclaw/openclaw.json`):
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
> Zvyšok vašej konfigurácie (brána, kanály, modely atď.) zostáva nezmenený – treba pridať iba kľúč `compaction`.

### (Odporúčané) Povolenie izolácie Docker

OpenClaw môže smerovať všetky operácie agenta so súbormi a kódom cez izolovaný kontajner Docker namiesto ich priameho spúšťania na vašom hostiteľovi. Tým sa obmedzí dosah akejkoľvek neúmyselnej akcie na sandbox, pričom súborový systém a sieť vášho hostiteľa zostanú nedotknuté.

Jednorazovo zostavte obraz sandboxu (Docker musí byť nainštalovaný):

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

Kontajnery sandboxu štandardne **nemajú prístup k sieti**. Pozrite si [referenciu sandboxingu](https://docs.openclaw.ai/gateway/sandboxing) pre bind mounty a prepísanie sieťových nastavení.

> #### Riešenie problémov: Docker – prístup zamietnutý
>
> Ak pri spúšťaní príkazov Docker dostanete chybu „permission denied":
>
> **Krok 1: Pridajte svojho používateľa do skupiny docker**
>
> ```bash
> sudo groupadd docker                    # Vytvorte skupinu, ak je to potrebné
> sudo usermod -aG docker $USER           # Pridajte sa do skupiny
> newgrp docker                           # Aktivujte zmenu
> docker run hello-world                  # Otestujte to
> ```
>
> **Krok 2: Ak chyba pretrváva, použite trvalú opravu**
>
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
>
> Potom **reštartujte** váš systém.
>
> **Rýchla dočasná oprava** (resetuje sa po reštarte):
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

### Spustenie brány OpenClaw

Brána je proces OpenClaw, ktorý spravuje slučku agenta a obsluhuje dashboard:

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

Ak chcete otvoriť dashboard, spustite toto v druhom termináli, kým brána stále beží:

```bash
openclaw dashboard
```

Keďže sa brána viaže na loopback, dashboard sa pri otvorení z rovnakého počítača automaticky overí – nie je potrebné zadávať token ani schvaľovať zariadenie pre lokálny prístup. Mali by ste vidieť dashboard OpenClaw s vaším modelom Lemonade uvedeným ako aktívny backend.

> Ak ste povolili sandboxing, môžete ho overiť tak, že požiadate agenta, aby z dashboardu `spustil hostname`. Ak namiesto názvu hostiteľa vášho počítača vidíte krátke ID kontajnera, sandbox funguje.

**Gratulujeme, vytvorili ste plne lokálny zásobník AI agenta od základov.**

> **Potrebujete token brány?** Spustite `openclaw dashboard --no-open`, aby sa vytlačila URL adresa dashboardu s vloženým tokenom (zároveň sa pokúsi skopírovať ho do schránky). Alternatívne sa token nachádza na `gateway.auth.token` v `~/.openclaw/openclaw.json`.
>
> **Schválenie vzdialeného zariadenia:** Keď otvoríte dashboard z druhého počítača alebo telefónu, prehliadač zobrazí ID žiadosti. Späť na počítači, kde beží brána, spustite:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potrebné iba pre vzdialené alebo sekundárne zariadenia – prístup cez loopback z rovnakého počítača sa overuje automaticky.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Keď brána beží, môžete sa k svojmu lokálnemu agentovi dostať z akéhokoľvek zariadenia. Vyberte si možnosť, ktorá vyhovuje vášmu nastaveniu. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a ďalšie kanály – úplný zoznam nájdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnosť A: Discord

Discord vyžaduje server, kde **máte prístup správcu**, aby ste mohli pridať bota. Ak zdieľate servery, ale nevlastníte žiadny, použite namiesto toho Možnosť B (Telegram).

#### Vytvorenie účtu Discord a servera

Ak nemáte účet Discord, zaregistrujte sa na [discord.com](https://discord.com). Potrebujete tiež server, kde ste správcom – vytvorte ho kliknutím na ikonu **+** v bočnom paneli Discord a výberom **Create My Own**. Súkromný server je v poriadku.

#### Vytvorenie aplikácie Discord a bota

1. Prejdite na [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte názov (napr. „openclaw-bot").
2. V bočnom paneli kliknite na **Bot**. Nastavte používateľské meno pre bota.
3. Stále na stránke Bot, posuňte sa na **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Posuňte sa späť nahor a kliknite na **Reset Token**, aby ste vygenerovali token bota. Skopírujte ho.

#### Pridanie bota na váš server

1. V bočnom paneli kliknite na **OAuth2/ URL Generator**.
2. V časti **Scopes** povoľte `bot` a `applications.commands`.
3. V časti **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú URL adresu, vložte ju do prehliadača, vyberte váš server a potvrďte. Bot by sa teraz mal objaviť v zozname členov vášho servera.

#### Získanie vašich ID

Povoľte Režim vývojára v Discord (**User Settings/ Advanced/ Developer Mode**), potom:
- Kliknite pravým tlačidlom na ikonu vášho servera: **Copy Server ID**
- Kliknite pravým tlačidlom na váš vlastný avatar: **Copy User ID**

#### Povolenie priamych správ od členov servera

Kliknite pravým tlačidlom na ikonu vášho servera/ **Privacy Settings**/ zapnite **Direct Messages**. Tým umožníte botovi posielať vám priame správy, čo je potrebné pre krok párovania.

#### Konfigurácia OpenClaw pre Discord

Uložte token bota ako premennú prostredia, potom vytvorte jeden súbor záplaty, ktorý povolí Discord, odkazuje na token a pridá váš server na zoznam povolených. Nahraďte `<server_id>` a `<user_id>` ID získanými vyššie.

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

> **Nespoliehajte sa na to, že agent to nakonfiguruje.** Keď je sandboxing povolený, agent nemôže zapisovať do `~/.openclaw/openclaw.json` zvnútra sandboxu – namiesto toho použite vyššie uvedené príkazy CLI na hostiteľovi.

Reštartujte bránu, aby načítala novú konfiguráciu kanála:

```bash
openclaw gateway run --bind loopback --port 18789
```

V priebehu niekoľkých sekúnd by ste mali vo výstupe brány vidieť `logged in to discord as <bot-name>`.

#### Párovanie vášho účtu Discord

Pošlite botovi priamu správu v Discord. Bot odpovie krátkym párovacím kódom.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schváľte ho na počítači, kde beží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Párovací kód vyprší po jednej hodine.

Teraz môžete chatovať so svojím agentom priamo z Discord a preniesť úlohy na váš lokálny hardvér.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnosť B: Telegram

Telegram je pre väčšinu používateľov jednoduchší ako Discord – nevyžaduje žiadny server ani prístup správcu.

#### Vytvorenie bota Telegram

1. Otvorte Telegram a napíšte správu **@BotFather**.
2. Pošlite `/newbot` a postupujte podľa pokynov. Uložte token bota, ktorý dostanete.

#### Konfigurácia OpenClaw pre Telegram

Uložte token ako premennú prostredia:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Pridajte konfiguráciu kanála do `~/.openclaw/openclaw.json` (alebo ju záplatujte cez dashboard):

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

Reštartujte bránu, potom pošlite botovi akúkoľvek správu v Telegram. Schváľte párovanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Párovací kód vyprší po jednej hodine. Teraz môžete chatovať so svojím agentom prostredníctvom priamej správy v Telegram.

---

## Ďalšie kroky

Teraz, keď váš agent môže prijímať príkazy z vášho telefónu a konať na vašom lokálnom počítači, tu sú tri smery, ktoré stojí za to preskúmať:

1. **Sumarizátor akciového trhu**: Naplánujte OpenClaw, aby v pevnom intervale získaval dáta z finančných API, sumarizoval pohyby dňa pomocou vášho lokálneho modelu a každé ráno posielal prehľad na váš telefón prostredníctvom zvoleného kanála.

2. **Monitor dolaďovania**: Spustite trénovaciu úlohu na diaľku cez Telegram alebo Discord, potom nechajte agenta sledovať trénovací log a pravidelne hlásiť hodnoty straty, využitie GPU a využitie disku späť na váš telefón. Ak sa beh zastaví alebo VRAM prudko stúpne, dozviete sa to okamžite bez toho, aby ste museli byť pri počítači.

3. **IoT s lokálnym VLM**: Nasmerujte kameru na vaše predné dvere, spustite vizuálny model na Lemonade a nechajte OpenClaw analyzovať snímky na požiadanie alebo na základe spúšťača. Opýtajte sa „prišli dnes nejaké balíky?" z vášho telefónu a získajte priamu odpoveď z vášho vlastného hardvéru.