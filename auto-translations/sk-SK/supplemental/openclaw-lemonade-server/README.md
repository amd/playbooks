<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré kroky, príkazy, súbory na stiahnutie alebo dostupnosť produktov sa môžu vo vašom jazyku alebo regióne líšiť. Ak sa vám niečo zdá nesprávne, považujte pôvodný anglický playbook za zdroj pravdivých informácií.
<!-- auto-translated-disclaimer:end -->

# Spustenie OpenClaw s Lemonade Server ako backendom

## Prehľad

[**OpenClaw**](https://openclaw.ai/) je autonómny AI agent, ktorý dokáže písať a spúšťať kód, spravovať súbory a spracovávať komplexné viackrokové úlohy vo vašom mene. Na rozdiel od chatového asistenta, ktorý len odpovedá na otázky, OpenClaw vykonáva skutočné akcie vo vašom systéme, čo znamená, že potrebuje rýchly a schopný AI backend, ktorý dokáže držať krok s náročnou slučkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je práve takýto backend. Je to open-source lokálny inferenčný server, ktorý spúšťa GenAI modely priamo na vašom hardvéri a sprístupňuje ich prostredníctvom priemyselne štandardného OpenAI API.

Spolu tvoria plne lokálny AI agentný stack: Lemonade sa stará o inferenciu modelu a OpenClaw poskytuje agentnú slučku, ktorá premieňa výstupy modelu na skutočné akcie.

> **Predtým, než budete pokračovať:** OpenClaw je vysoko autonómny AI agent. Poskytnutie prístupu k vášmu systému akémukoľvek AI agentovi môže viesť k nepredvídateľným alebo neúmyselným výsledkom. Pokračujte iba vtedy, ak rozumiete rizikám a ste ochotní akceptovať, že vo vašom mene bude konať autonómny softvér.

---

## Čo sa naučíte

Na konci tohto návodu budete schopní:

- Zoznámiť sa s **Lemonade Server**
- **Nainštalovať OpenClaw** a **nasmerovať ho na Lemonade Server** ako svoj AI backend.
- **Spustiť bránu OpenClaw** a potvrdiť, že váš agent je pripravený na prácu.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli so svojím agentom komunikovať z akéhokoľvek zariadenia.

---

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:linux -->
- PC so systémom **Ubuntu 24.04+** alebo kompatibilnou distribúciou Linuxu založenou na Debiane s `apt-get`
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (voliteľné, na sandboxovanie OpenClaw)

- **~10–30 GB voľného miesta na disku** pre váhy modelu
<!-- @os:end -->
<!-- @os:windows -->
- PC so systémom **Windows 10/11**
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10–30 GB voľného miesta na disku** pre váhy modelu
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

Odporúčaným modelom pre tento návod je **Qwen3.6-35B-A3B-GGUF** od Unsloth, silný MoE model s kontextovým oknom 263k tokenov, ktorý je vhodný na agentné úlohy. Tento model používa kvantizáciu UD-Q4_K_XL. Stiahnite ho teraz:

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

Model má predvolenú dĺžku kontextu 262 144 tokenov. Ak sa stretnete s chybami spôsobenými nedostatkom pamäte (OOM), zvážte zníženie kontextového okna. Keďže však Qwen3.6 využíva rozšírený kontext pri komplexných úlohách, odporúčame zachovať dĺžku kontextu aspoň 128K tokenov, aby sa zachovali schopnosti uvažovania.

> **Tip: Vypnite uvažovanie pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B beží predvolene v režime uvažovania, čo pridáva latenciu pred každou odpoveďou. Pri agentných slučkách sa táto réžia rýchlo nakumuluje. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá vypína uvažovanie. Ak ju chcete použiť, stiahnite súbor a importujte ho:
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

OpenClaw spúšťame vnútri WSL (odporúčané) a pripájame ho k Lemonade bežiacemu natívne vo Windows. Toto vám poskytuje prostredie Linux shellu pre OpenClaw, pričom zachováva GPU akceleráciu Lemonade na strane Windows.

### Inštalácia WSL a Ubuntu

Otvorte PowerShell ako správca a nainštalujte jadro WSL:

```powershell
wsl --install --no-distribution
```

Potom nainštalujte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Povolenie systemd v WSL

Spustite toto v termináli Ubuntu:

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

### Prepojenie Lemonade z Windows do WSL

WSL2 beží vo virtuálnej sieti. Lemonade vo Windows sa viaže na `127.0.0.1`, ktorú WSL nedokáže priamo dosiahnuť. Windows port proxy presmeruje prevádzku z gateway IP adresy WSL na Windows localhost.

**Nájdite svoju gateway IP adresu WSL** (spustite vnútri WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte port proxy** (spustite v PowerShelli ako správca, pričom nahraďte `<WSL-Gateway-IP>` vašou gateway IP adresou WSL):

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

Ak ste v predchádzajúcom kroku už načítali model Qwen3.6-35B-A3B-GGUF, mali by ste vidieť výstup JSON ako je tento:

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

> Pravidlo `netsh portproxy` prežije reštarty, ale gateway IP adresa WSL sa môže po `wsl --shutdown` zmeniť. Ak sa Lemonade po reštarte stane nedostupným z WSL, zistite aktualizovanú gateway IP adresu a aktualizujte proxy touto novou IP adresou.

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
> Príkazy v tejto časti spúšťajte vo svojom **termináli WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Príznak `--no-onboard` preskočí interaktívneho sprievodcu nastavením, backend modelu nakonfigurujete manuálne v ďalšom kroku, čo vám poskytuje presnú kontrolu nad tým, ktorý model a server sa použije.

Otvorte nový terminál a potvrďte inštaláciu:

```bash
openclaw --version
```

> **Tip:** Ak sa po inštalácii zobrazí `command not found`, pridajte globálny bin adresár npm do vašej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby ste to zachovali natrvalo, pridajte vyššie uvedený riadok do vášho súboru `~/.bashrc` alebo `~/.zshrc`.

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

Spustite neinteraktívne onboarding OpenClaw.
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

> **Veľkosť kontextového okna OpenClaw:** Kompresia OpenClaw sa spustí, keď `contextTokens > contextWindow − reserveTokens`. Predvolená hodnota `reserveTokensFloor` je 20 000 tokenov, čo je spodná hranica, ktorá prepíše `reserveTokens`, ak je nižšia, takže akýkoľvek kontext modelu pod ~37k spustí nekonečnú slučku kompresie. Nastavte nízku rezervu a raz vypnite spodnú hranicu vo vašej konfigurácii a platí to pre každý model, bez potreby ladenia pre jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodná hranica* (minimálna poistka), nie samotná rezerva, nastavenie iba tejto hranice nemá žiadny efekt. `reserveTokensFloor: 0` vypne túto poistku, takže sa akceptuje nižšia hodnota `reserveTokens`.
>
> **Kedy toto použiť:** Použite túto konfiguráciu, ak je efektívne kontextové okno vášho modelu menšie ako ~37k, buď preto, že je model malý (napr. 8k, 16k, 32k), alebo preto, že ste ho úmyselne obmedzili na nižšiu hodnotu (napr. načítanie modelu so 128k, ale nastavenie kontextu na 16k v Lemonade). Bez toho OpenClaw pri spustení vstúpi do nekonečnej slučky kompresie.
>
> **Modely s veľkým kontextom pri plnom kontexte:** Toto môžete úplne preskočiť. Predvolené hodnoty fungujú dobre, kompresia sa spustí ešte pred zaplnením okna a model má dostatok priestoru na generovanie dlhých odpovedí. Ak toto predsa len použijete, majte na pamäti, že `reserveTokens: 4096` obmedzuje dĺžku odpovede na ~4k tokenov, čo môže orezať dlhšie generovanie súborov alebo podrobné plány.
>
> **Kam toto pridať:** Umiestnite blok `compaction` do `agents.defaults` vo vašom súbore `openclaw.json` (zvyčajne v `~/.openclaw/openclaw.json`):
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
> Zvyšok vašej konfigurácie (gateway, channels, models atď.) zostáva nezmenený, potrebné je pridať iba kľúč `compaction`.

### (Odporúčané) Povoliť sandboxing v Docker

OpenClaw dokáže smerovať všetky operácie agenta so súbormi a kódom cez izolovaný kontajner Docker namiesto ich priameho spúšťania na vašom hostiteľskom systéme. Tým sa obmedzí dosah akejkoľvek neúmyselnej akcie na sandbox, pričom systém súborov a sieť vášho hostiteľa zostanú nedotknuté.

Zostavte obraz sandboxu raz (Docker musí byť nainštalovaný):

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

Kontajnery sandboxu nemajú predvolene **žiadny prístup k sieti**. Pozrite si [referenciu k sandboxingu](https://docs.openclaw.ai/gateway/sandboxing) pre bind mounty a prepísanie sieťových nastavení.

> #### Riešenie problémov: Docker Permission Denied
> 
> Ak sa vám pri spúšťaní príkazov Docker zobrazí „permission denied“:
> 
> **Krok 1: Pridajte svojho používateľa do skupiny docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Krok 2: Ak chyba pretrváva, použite trvalú opravu**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Potom systém **reštartujte**.
> 
> **Rýchla dočasná oprava** (po reštarte sa vráti späť):
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
## (Odporúčané) Integrácia OpenClaw so službami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) poskytuje samostatne hostovanú službu na prehľadávanie webu a extrakciu obsahu, ktorá dokáže obísť tieto obmedzenia a odomknúť plný potenciál automatizácie OpenClaw.

V tomto nastavení beží OpenClaw ako sada kontajnerov Docker spravovaných pomocou Podman. Na zjednodušenie správy životného cyklu a automatického spúšťania registrujeme Firecrawl ako používateľskú `systemd` službu, ktorá orchestruje podkladový zásobník Podman Compose. To umožňuje OpenClaw spúšťať gateway, zastavovať a overovať službu Firecrawl pomocou štandardných príkazov `systemctl --user` namiesto priamej interakcie s kontajnermi.

Aby sme veci zjednodušili, rozdelili sme celý proces do štyroch krokov:

---

### 1. Registrácia systémovej služby
Prejdite do adresára s konfiguráciou používateľského systemd:
```bash
cd ~/.config/systemd/user
```
Vytvorte a otvorte nový súbor s názvom `firecrawl.service`.
```bash
nano firecrawl.service
```
Skopírujte a vložte nasledujúcu konfiguráciu:
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
V tomto bode je služba definovaná, ale ešte nie je zaregistrovaná v `systemd`.
Uistite sa, že názov súboru presne zodpovedá tomu, ktorý ste vytvorili vyššie, a potom spustite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ak je operácia úspešná, mali by ste vidieť nasledujúci výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby, ktoré sú nakonfigurované tak, aby sa spúšťali automaticky.
### 2. Konfigurácia Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideálny pre tých, ktorí potrebujú plnú kontrolu nad svojím prostredím na scraping a spracovanie údajov, no prináša so sebou aj kompromis v podobe dodatočnej údržby a konfiguračného úsilia.

Začnite naklonovaním repozitára:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Vytvorte súbor `.env` v koreňovom adresári `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Nasadenie OpenClaw pomocou Podman Compose

Predtým, než budete pokračovať, uistite sa, že máte stiahnutý najnovší Docker obraz OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Po dokončení stiahnite súbor OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) a umiestnite ho do koreňového adresára `/firecrawl`:

> Táto konvencia je potrebná na to, aby `systemd` dokázal správne nájsť a spustiť službu podľa nastavenia `WorkingDirectory=${HOME}/firecrawl`.

> Zásobník môžete kedykoľvek rozšíriť pridaním ďalších služieb Firecrawl podľa potreby. Úplný zoznam dostupných služieb nájdete v oficiálnom súbore [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spustenie služby OpenClaw prostredníctvom Firecrawl 

Predtým, než odovzdáte kontrolu nástroju `systemd`, overte, že všetko funguje správne manuálnym spustením zásobníka:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ak je všetko správne nakonfigurované, mal by sa spustiť kontajner OpenClaw a výstup na príkazovom riadku by mal vyzerať približne takto:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po overení zásobník opäť vypnite, kým budete pokračovať:
```bash
podman compose -f openclaw-compose.yaml down
```
Pred spustením služby musíte zabezpečiť správne vlastníctvo a oprávnenia pre adresár `firecrawl` a jeho súbor `.env`. 
Toto je nevyhnutné na to, aby služba mohla pri spustení zapísať vaše prihlasovacie údaje.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Teraz, keď je všetko overené, spustite službu prostredníctvom `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akcie OpenClaw](https://docs.openclaw.ai/) sú prístupné priamo z interaktívneho kontajnera a webový dashboard je dostupný na rovnakom hostiteľovi a porte na adrese http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Získanie vášho `OPENCLAW_GATEWAY_TOKEN`

Po spustení služby si všimnete, že vo vašom domovskom adresári bol vytvorený nový adresár `.openclaw` (~/.openclaw). Tento adresár je štandardne uzamknutý, takže ho budete musieť odomknúť, aby ste získali svoj token brány.

1. Udeľte prístup k adresáru:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Prečítajte si svoj token brány:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Vo výstupe nájdite hodnotu `OPENCLAW_GATEWAY_TOKEN`.

3. Otvorte dashboard brány vo svojom prehliadači na adrese http://127.0.0.1:18789. Po vyzvaní na autentifikáciu vložte svoj token.

Ak chcete službu zastaviť, spustite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Spustenie brány OpenClaw

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

Ak chcete otvoriť dashboard, spustite v druhom termináli nasledujúce, kým brána stále beží:

```bash
openclaw dashboard
```

Keďže brána je viazaná na loopback, dashboard sa pri otvorení z toho istého počítača automaticky autentifikuje, nie je potrebné zadávať token ani schvaľovať zariadenie pre lokálny prístup. Mali by ste vidieť dashboard OpenClaw s vaším modelom Lemonade uvedeným ako aktívny backend.

> Ak ste zapli sandboxing, môžete si to overiť tak, že v dashboarde požiadate agenta, aby spustil `run hostname`. Ak sa zobrazí krátke ID kontajnera namiesto názvu hostiteľa vášho počítača, sandbox funguje správne.

**Gratulujeme, vytvorili ste od základov plne lokálny AI agentný zásobník.**

> **Potrebujete token brány?** Spustite `openclaw dashboard --no-open`, aby sa vypísala URL adresa dashboardu spolu so zabudovaným tokenom (súčasne sa pokúsi skopírovať ho do schránky). Alternatívne sa token nachádza pod `gateway.auth.token` v súbore `~/.openclaw/openclaw.json`.
>
> **Schválenie vzdialeného zariadenia:** Keď otvoríte dashboard z druhého počítača alebo telefónu, prehliadač zobrazí identifikátor požiadavky. Späť na počítači, na ktorom beží brána, spustite:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potrebné len pre vzdialené alebo sekundárne zariadenia, prístup cez loopback z rovnakého počítača sa autentifikuje automaticky.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Po spustení brány môžete pristupovať k svojmu lokálnemu agentovi z akéhokoľvek zariadenia. Vyberte možnosť, ktorá vyhovuje vášmu nastaveniu. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a ďalšie kanály, úplný zoznam nájdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnosť A: Discord

Discord vyžaduje server, na ktorom **máte administrátorský prístup**, aby ste mohli pridať bota. Ak zdieľate servery, no žiadny nevlastníte, použite namiesto toho možnosť B (Telegram).

#### Vytvorenie účtu a servera Discord

Ak nemáte účet Discord, zaregistrujte sa na [discord.com](https://discord.com). Potrebujete tiež server, na ktorom ste administrátorom, vytvorte ho kliknutím na ikonu **+** na bočnom paneli Discordu a výberom možnosti **Create My Own**. Súkromný server postačuje.

#### Vytvorenie aplikácie a bota Discord

1. Prejdite na [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte názov (napr. „openclaw-bot“).
2. V bočnom paneli kliknite na **Bot**. Nastavte používateľské meno bota.
3. Stále na stránke Bot prejdite nižšie na **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Posuňte sa späť nahor a kliknite na **Reset Token**, čím vygenerujete token svojho bota. Skopírujte ho.

#### Pridanie bota na váš server

1. V bočnom paneli kliknite na **OAuth2/ URL Generator**.
2. V časti **Scopes** povoľte `bot` a `applications.commands`.
3. V časti **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú URL adresu, vložte ju do prehliadača, vyberte svoj server a potvrďte. Bot by sa teraz mal objaviť v zozname členov vášho servera.
#### Získajte svoje ID

Povoľte režim pre vývojárov v Discorde (**User Settings/ Advanced/ Developer Mode**), potom:
- Kliknite pravým tlačidlom na ikonu svojho servera: **Copy Server ID**
- Kliknite pravým tlačidlom na svoj vlastný avatar: **Copy User ID**

#### Povoľte súkromné správy od členov servera

Kliknite pravým tlačidlom na ikonu svojho servera/ **Privacy Settings**/ zapnite **Direct Messages**. Toto umožní botovi poslať vám súkromnú správu, čo je potrebné pre krok párovania.

#### Nakonfigurujte OpenClaw pre Discord

Uložte token svojho bota ako premennú prostredia, potom vytvorte jeden patch súbor, ktorý zapne Discord, odkazuje na token a povolí váš server v zozname povolených. Nahraďte `<server_id>` a `<user_id>` identifikátormi zozbieranými vyššie.

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

> **Nespoliehajte sa na to, že požiadate agenta o túto konfiguráciu.** Keď je zapnutý sandboxing, agent nemôže zapisovať do `~/.openclaw/openclaw.json` zvnútra sandboxu, namiesto toho použite vyššie uvedené CLI príkazy na hostiteľskom počítači.

Reštartujte gateway, aby sa načítala nová konfigurácia kanála:

```bash
openclaw gateway run --bind loopback --port 18789
```

Do niekoľkých sekúnd by ste mali vo výstupe gateway vidieť `logged in to discord as <bot-name>`.

#### Spárujte svoj účet Discord

Pošlite botovi súkromnú správu v Discorde. Odpovie krátkym párovacím kódom.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schváľte to na počítači, na ktorom beží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnosť párovacích kódov vyprší po jednej hodine.

Teraz môžete komunikovať so svojím agentom priamo z Discordu a presúvať úlohy na váš lokálny hardvér.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnosť B: Telegram

Telegram je pre väčšinu používateľov jednoduchší ako Discord, nevyžaduje server ani administrátorský prístup.

#### Vytvorte bota pre Telegram

1. Otvorte Telegram a napíšte správu botovi **@BotFather**.
2. Odošlite `/newbot` a postupujte podľa pokynov. Uložte si token bota, ktorý vám poskytne.

#### Nakonfigurujte OpenClaw pre Telegram

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

Reštartujte gateway a potom pošlite svojmu botovi ľubovoľnú správu v Telegrame. Schváľte párovanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnosť párovacích kódov vyprší po jednej hodine. Teraz môžete komunikovať so svojím agentom prostredníctvom súkromných správ v Telegrame.

---

## Ďalšie kroky

Teraz, keď váš agent dokáže prijímať príkazy z vášho telefónu a vykonávať ich na vašom lokálnom počítači, tu sú tri smery, ktoré stoja za preskúmanie:

1. **Zhrnutie akciového trhu**: Naplánujte, aby OpenClaw v pravidelných intervaloch sťahoval dáta z finančných API, zhrnul dnešný vývoj pomocou vášho lokálneho modelu a každé ráno posielal súhrn na váš telefón cez vami zvolený kanál.

2. **Monitorovanie doladenia (fine-tuning)**: Spustite trénovaciu úlohu na diaľku cez Telegram alebo Discord a nechajte agenta sledovať tréningový log a pravidelne posielať späť na váš telefón hodnoty straty (loss), využitie GPU a stav disku. Ak sa beh zastaví alebo dôjde k skokovému nárastu VRAM, dozviete sa to okamžite bez toho, aby ste museli byť pri počítači.

3. **IoT s lokálnym VLM**: Namierte kameru na svoje vchodové dvere, spustite vizuálny model na Lemonade a nechajte OpenClaw analyzovať snímky na požiadanie alebo pri spustení spúšťača. Opýtajte sa „prišli dnes nejaké balíky?“ zo svojho telefónu a dostanete jasnú odpoveď z vlastného hardvéru.

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