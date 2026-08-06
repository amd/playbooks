<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Spustenie Hermes Agent lokálne so serverom Lemonade Server

## Prehľad

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) je samozdokonaľujúci sa AI agent vytvorený spoločnosťou Nous Research. Má vstavanú učiacu slučku, vytvára zručnosti na základe skúseností, buduje si trvalú pamäť o tom, kto ste, naprieč reláciami, a môže vo vašom mene spúšťať naplánované automatizácie. Na rozdiel od jednoduchého chatového asistenta Hermes vykonáva reálne akcie: spúšťa príkazy shellu, zapisuje súbory, prehľadáva web a deleguje paralelné pracovné toky na subagentov.

[**Lemonade Server**](https://lemonade-server.ai/) je lokálny inferenčný backend, ktorý ho poháňa. Je to open-source server, ktorý spúšťa modely GenAI priamo na vašom hardvéri AMD a sprístupňuje ich prostredníctvom priemyselne štandardného OpenAI API.

Spolu tvoria plne lokálny stack AI agenta: Lemonade sa stará o inferenciu modelu na vašom GPU a Hermes poskytuje slučku agenta, pamäť, zručnosti a bránu na odosielanie správ.

> **Skôr než budete pokračovať:** Hermes Agent je vysoko autonómny AI agent. Poskytnutie prístupu k vášmu systému akémukoľvek AI agentovi môže viesť k nepredvídateľným alebo nezamýšľaným výsledkom. Pokračujte iba vtedy, ak rozumiete rizikám a ste zmierení s tým, že softvér bude autonómne konať vo vašom mene.

---

## Čo sa naučíte

Na konci tohto sprievodcu budete schopní:

- **Nainštalovať Hermes Agent** a nasmerovať ho na **Lemonade Server** ako svoj AI backend.
- **(Odporúčané) Povoliť sandboxing pomocou Docker/Podman**, aby ste izolovali akcie agenta od hostiteľského systému.
- **Spustiť bránu Hermes** a potvrdiť, že váš agent je pripravený.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli so svojím agentom komunikovať z akéhokoľvek zariadenia.

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
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
- [Podman](https://podman.io/docs/installation) (voliteľné, pre sandboxing Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- PC so systémom **Windows 10/11**
- Aspoň **12 GB RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
- Podman (voliteľné, pre sandboxing Hermes Agent). Nainštalujte v rámci WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman je predinštalovaný na Halo Box a nie je potrebné žiadne nastavenie
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stiahnutie a načítanie odporúčaného modelu

Odporúčaný model pre tohto sprievodcu je **Qwen3.6-35B-A3B-GGUF** od Unsloth, silný model MoE s kontextovým oknom 263k tokenov, ktorý je dobre vhodný pre pracovné zaťaženia agentov. Tento model používa kvantizáciu UD-Q4_K_XL. Stiahnite ho teraz:

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

Model má predvolenú dĺžku kontextu 262 144 tokenov. Ak sa stretnete s chybami nedostatku pamäte (OOM), zvážte zmenšenie kontextového okna.

> **Tip: Vypnite režim uvažovania pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B beží predvolene v režime uvažovania (thinking mode), čo pridáva latenciu pred každou odpoveďou. Pri slučkách agentov sa táto réžia rýchlo kumuluje. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá vypína uvažovanie. Ak ju chcete použiť, stiahnite súbor a importujte ho:
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

## Nastavenie WSL

Hermes Agent spúšťame v rámci WSL a pripájame ho k Lemonade, ktorý beží natívne vo Windows. Vďaka tomu máte pre Hermes prostredie shellu Linux a zároveň si zachovávate GPU akceleráciu Lemonade na strane Windows.

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

### Premostenie Lemonade z Windows do WSL

WSL2 beží vo virtuálnej sieti. Lemonade vo Windows sa viaže na `127.0.0.1`, ku ktorému sa WSL nemôže priamo pripojiť. Proxy portu Windows presmeruje prevádzku z brány WSL IP na Windows localhost.

**Zistite svoju IP adresu brány WSL** (spustite v rámci WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte proxy portu** (spustite v PowerShell ako správca, pričom `<WSL-Gateway-IP>` nahraďte svojou IP adresou brány WSL):

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

Ak ste v predchádzajúcom kroku už načítali model Qwen3.6-35B-A3B-GGUF, mali by ste vidieť výstup JSON so zoznamom vášho načítaného modelu.

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

> Pravidlo `netsh portproxy` prežije reštarty, ale IP adresa brány WSL sa môže po `wsl --shutdown` zmeniť. Ak sa Lemonade po reštarte stane z WSL nedostupným, získajte aktualizovanú IP adresu brány a aktualizujte proxy touto novou IP adresou.

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

## Inštalácia Hermes Agent

<!-- @os:windows -->
> Príkazy v tejto časti spúšťajte v rámci vášho **terminálu WSL**, pokiaľ nie je uvedené inak.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Príznak `--skip-setup` preskočí interaktívneho sprievodcu nastavením, aby ste mohli v ďalšom kroku nakonfigurovať model backend manuálne.

Znova načítajte svoj shell:

```bash
source ~/.bashrc
```

Potvrďte inštaláciu:

```bash
hermes --version
```

Spustite samodiagnostiku na kontrolu všetkých závislostí:

```bash
hermes doctor
```

> **Tip:** Ak sa po inštalácii zobrazí `command not found`, pridajte Hermes do svojej PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Aby ste to urobili trvalé, pridajte vyššie uvedený riadok do svojho `~/.bashrc` alebo `~/.zshrc`.

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
## Nakonfigurujte Hermes na používanie Lemonade

Hermes ukladá konfiguráciu modelu v `~/.hermes/config.yaml`. Môžete buď použiť interaktívny výber pomocou `hermes model`, alebo môžete konfiguráciu zapísať priamo.

### Možnosť 1: Interaktívny výber

<!-- @os:windows -->
> Nasledujúci príkaz spustite vo vašom **WSL termináli**.
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

Po zobrazení výzvy:

1. Vyberte **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** použite IP adresu brány WSL: spustite `ip route show default | awk '{print $3}' | head -1` vo WSL, aby ste ju získali, potom zadajte `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Automatická detekcia)
5. **Select model:** zo zoznamu vyberte `Qwen3.6-35B-A3B-GGUF`
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (alebo akýkoľvek iný názov podľa vášho výberu)

`hermes model` uloží tak aktívny výber modelu, ako aj pomenovanú položku `custom_providers`, ktorá spolu s endpointom uchováva aj dĺžku kontextu. Výsledok v `~/.hermes/config.yaml` vyzerá takto:

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

### Možnosť 2: Priamy zápis konfigurácie

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

Vo vašom WSL termináli získajte IP adresu hostiteľa so systémom Windows a zapíšte konfiguráciu:

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

## (Odporúčané) Povolenie sandboxingu pomocou Podman

Hermes Agent dokáže smerovať všetky operácie agenta so shellom a súbormi cez izolovaný kontajner namiesto ich priameho spúšťania na vašom hostiteľovi. Tým sa dopad akejkoľvek nezamýšľanej akcie obmedzí len na sandbox, pričom súborový systém a sieť vášho hostiteľa zostanú nedotknuté.

Vytvorte odľahčený sandboxový obraz:

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
Otvorte WSL terminál:

```powershell
wsl -d Ubuntu-24.04
```

Potom vytvorte odľahčený sandboxový obraz:

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

Potom nakonfigurujte Hermes tak, aby ako kontajnerový runtime používal Podman, a nastavte backend terminálu:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` zostáva `docker`.
> `HERMES_DOCKER_BINARY` je to, čo hovorí Hermesu, aby namiesto tohto runtime používal Podman.

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

Hermes teraz spustí trvalý sandboxový kontajner a bude cez neho smerovať všetky volania nástrojov `terminal` a súborových nástrojov. Kontajner zdieľa životný cyklus procesu Hermes, je opätovne používaný pri všetkých volaniach nástrojov a je zničený pri ukončení Hermesu.

> **Overte, že sandbox funguje:** Spustite Hermes (`hermes`) a požiadajte ho, aby spustil `run hostname` – mali by ste vidieť krátke ID kontajnera namiesto hostiteľského názvu vášho počítača. Môžete ho tiež požiadať o `rm -rf <path-to-a-dummy-file/folder>`: Hermes potvrdí odstránenie, no priečinok bude na vašom hostiteľovi stále existovať. Príkaz sa vykonal v izolovanom `$HOME` kontajnera, nie vo vašom.

> **Potrebujete silnejšiu izoláciu?** Hermes tiež poskytuje oficiálny Docker obraz (`nousresearch/hermes-agent`), ktorý spúšťa celý proces agenta vnútri kontajnera – vrátane brány, nástrojov a všetkého ostatného. Podrobnosti o nastavení nájdete v [dokumentácii k Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Odporúčané) Integrácia Hermes so službami Firecrawl

Hermes dokáže prehliadať a extrahovať obsah z webových stránok pomocou svojich vstavaných webových nástrojov. Mnohé moderné webové stránky však používajú systémy na detekciu botov, ktoré blokujú jednoduché HTTP požiadavky a namiesto skutočného obsahu vracajú stránky s výzvou (challenge pages). V dôsledku toho nemusí byť Hermes schopný spoľahlivo extrahovať informácie z takýchto stránok.

Na prekonanie tohto obmedzenia poskytuje [Firecrawl](https://docs.firecrawl.dev/introduction) samostatne hostovanú službu na prehľadávanie webu a extrakciu obsahu, ktorá dokáže tieto prekážky obísť a odomknúť plný potenciál automatizácie s Hermesom.

V tomto nastavení Firecrawl beží ako sada Docker kontajnerov spravovaných pomocou Podman. Aby sme zjednodušili správu životného cyklu a automatické spúšťanie, registrujeme Firecrawl ako používateľskú `systemd` službu, ktorá orchestruje príslušný Podman Compose stack. Vďaka tomu môže Hermes spúšťať, zastavovať a overovať službu Firecrawl pomocou štandardných príkazov `systemctl --user` namiesto priamej interakcie s kontajnermi.

Aby sme veci zjednodušili, rozdelili sme celý proces na štyri kroky:

---

### 1. Registrácia systémovej služby
Prejdite do adresára s používateľskou konfiguráciou systemd:
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
V tomto bode je služba definovaná, no ešte nebola zaregistrovaná v `systemd`.
Uistite sa, že názov súboru presne zodpovedá tomu, ktorý ste vytvorili vyššie, a potom spustite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ak bude úspešný, mali by ste vidieť nasledujúci výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby, ktoré sú nakonfigurované na automatické spustenie.

### 2. Konfigurácia Firecrawl pre vašu službu

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideálny pre tých, ktorí potrebujú úplnú kontrolu nad svojím prostredím na scraping a spracovanie dát, no za cenu dodatočnej údržby a konfiguračného úsilia.

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
> Nastavte `BULL_AUTH_KEY` na silné tajomstvo, najmä pri akomkoľvek nasadení dostupnom z nedôveryhodných sietí.
### 3. Nasadenie Hermesu prostredníctvom Compose

Predtým než budete pokračovať, uistite sa, že máte stiahnutý najnovší Docker obraz Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Po dokončení stiahnite súbor Hermes Compose [hermes-compose.yaml](assets/hermes-compose.yaml) a umiestnite ho do koreňového adresára `/firecrawl`:

> Tento postup je potrebný na to, aby `systemd` dokázal správne nájsť a spustiť službu podľa nastavenia `WorkingDirectory=${HOME}/firecrawl`.

> Zásobník môžete kedykoľvek rozšíriť pridaním ďalších služieb Firecrawl podľa potreby. Úplný zoznam dostupných služieb nájdete v oficiálnom súbore [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spustenie služby Hermes prostredníctvom Firecrawl

Predtým než odovzdáte riadenie nástroju `systemd`, overte, že všetko funguje správne, manuálnym spustením zásobníka:
```bash
podman compose -f hermes-compose.yaml up -d
```
Ak je všetko nakonfigurované správne, mal by sa spustiť kontajner Hermes a výstup v príkazovom riadku by mal vyzerať približne takto:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Po overení pred pokračovaním zásobník znova vypnite:
```bash
podman compose -f hermes-compose.yaml down
```
Teraz, keď je všetko overené, spustite službu prostredníctvom `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) je dostupné z vnútra interaktívneho kontajnera a webový dashboard je dostupný na rovnakom hostiteľovi a porte na adrese http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Ak chcete službu zastaviť, spustite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Spustite interaktívnu CLI reláciu priamo:

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

**Gratulujeme, vytvorili ste plne lokálny zásobník AI agenta.**

### Webový dashboard

Hermes obsahuje webové rozhranie na správu konfigurácie, API kľúčov, modelov, relácií, pamäte a plánovaných úloh (cron). Otvorte druhý terminál, kým beží gateway alebo CLI, a spustite ho pomocou:

```bash
hermes dashboard
```

Týmto sa spustí lokálny server a v prehliadači sa otvorí `http://127.0.0.1:9119`. Úplný prehľad funkcií nájdete v [dokumentácii dashboardu](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Keď gateway beží, môžete sa k svojmu lokálnemu agentovi pripojiť z akéhokoľvek zariadenia. Hermes podporuje [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) a ďalšie

---

### Discord

Discord vyžaduje server, na ktorom **máte administrátorský prístup**, aby ste mohli pridať bota. Ak zdieľate servery, ale žiadny nevlastníte, použite namiesto toho Telegram.

#### Vytvorenie aplikácie a bota v Discorde

1. Prejdite na [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte mu názov (napr. „hermes-bot“).
2. V bočnom paneli kliknite na **Bot**. Nastavte používateľské meno bota.
3. Na tej istej stránke Bot prejdite nižšie k položke **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Vráťte sa hore a kliknite na **Reset Token**, čím vygenerujete token bota. Skopírujte ho.

#### Pridanie bota na váš server

1. V bočnom paneli kliknite na **OAuth2 / URL Generator**.
2. V časti **Scopes** povoľte `bot` a `applications.commands`.
3. V časti **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú URL adresu, vložte ju do prehliadača, vyberte svoj server a potvrďte.

#### Získanie identifikátorov a povolenie súkromných správ

Zapnite v Discorde vývojársky režim (**User Settings / Advanced / Developer Mode**), potom:
- Kliknite pravým tlačidlom na ikonu svojho servera: **Copy Server ID**
- Kliknite pravým tlačidlom na svoj vlastný avatar: **Copy User ID**

Kliknite pravým tlačidlom na ikonu servera / **Privacy Settings** / zapnite **Direct Messages**. Toto je nevyhnutné pre krok párovania.

#### Konfigurácia Hermesu pre Discord

Do súboru `~/.hermes/.env` pridajte nasledujúce:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Potom spustite gateway:

```bash
hermes gateway
```

Bot by sa mal v Discorde spustiť do niekoľkých sekúnd. Pošlite mu správu, buď priamu správu (DM), alebo v kanáli, ktorý vidí.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Vytvorenie bota v Telegrame

1. Otvorte Telegram a napíšte správu používateľovi **@BotFather**.
2. Odošlite `/newbot` a postupujte podľa pokynov. Uložte si token bota, ktorý dostanete.

#### Konfigurácia Hermesu pre Telegram

Do súboru `~/.hermes/.env` pridajte nasledujúce:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Nepoznáte svoje ID používateľa v Telegrame?** Napíšte správu používateľovi [@userinfobot](https://t.me/userinfobot) v Telegrame, odpovie vám vaším číselným ID.

Potom spustite gateway:

```bash
hermes gateway
```

Na otestovanie pošlite svojmu botovi ľubovoľnú správu v Telegrame. Teraz môžete so svojím agentom komunikovať prostredníctvom priamych správ v Telegrame. Podrobný návod na nastavenie webhookového režimu a pokročilé možnosti nájdete v [úplnom sprievodcovi nastavením Telegramu](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Ďalšie kroky

Teraz, keď váš agent dokáže prijímať príkazy z vášho telefónu a konať na vašom lokálnom počítači, tu sú tri smery, ktoré stoja za preskúmanie:

1. **Automatizovaný výskumný prehľad**: Naplánujte Hermesu, aby každé ráno vyhľadal na webe témy, ktoré vás zaujímajú, zhrnul zistenia pomocou vášho lokálneho modelu a odoslal prehľad do vášho telefónu cez Telegram alebo Discord, pričom všetko beží na vlastnom hardvéri bez akýchkoľvek nákladov na cloud.

2. **Kontrola kódu na požiadanie**: Nasmerujte Hermes na repozitár na GitHube, požiadajte ho o kontrolu otvorených pull requestov a nechajte ho zverejniť komentáre alebo zhrnutie späť do vášho chatu. Vďaka backendu terminálu Docker prebiehajú všetky operácie git vnútri sandboxu, čím zostáva váš hostiteľský systém čistý.

3. **Lokálny asistent pre súbory**: Poskytnite Hermesu prístup k pracovnému adresáru a požiadajte ho, aby na požiadanie z vášho telefónu organizoval, premenovával, zhŕňal alebo transformoval súbory. Keďže backend terminálu Docker obmedzuje všetky zápisy na pracovný priestor sandboxu, náhodné deštruktívne operácie sú tak izolované.