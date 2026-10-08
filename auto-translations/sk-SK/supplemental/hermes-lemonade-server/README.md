<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Spustenie agenta Hermes lokálne pomocou Lemonade Server

## Prehľad

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) je samozdokonaľujúci sa AI agent vytvorený spoločnosťou Nous Research. Má zabudovanú učiacu slučku, vytvára si zručnosti na základe skúseností, buduje si trvalú pamäť o tom, kto ste, naprieč reláciami, a dokáže vo vašom mene spúšťať naplánované automatizácie. Na rozdiel od jednoduchého chatovacieho asistenta Hermes vykonáva skutočné akcie: spúšťa príkazy shellu, zapisuje súbory, prehliada web a deleguje paralelné pracovné postupy na podagentov.

[**Lemonade Server**](https://lemonade-server.ai/) je lokálny inferenčný backend, ktorý ho poháňa. Je to open-source server, ktorý spúšťa GenAI modely priamo na vašom hardvéri AMD a sprístupňuje ich prostredníctvom štandardného API OpenAI.

Spolu tvoria plne lokálny zásobník AI agenta: Lemonade sa stará o inferenciu modelu na vašej GPU a Hermes poskytuje slučku agenta, pamäť, zručnosti a bránu na odosielanie správ.

> **Skôr než budete pokračovať:** Hermes Agent je vysoko autonómny AI agent. Poskytnutie prístupu k vášmu systému akémukoľvek AI agentovi môže viesť k nepredvídateľným alebo neúmyselným výsledkom. Pokračujte iba vtedy, ak rozumiete rizikám a ste spokojní s tým, že vo vašom mene koná autonómny softvér.

---

## Čo sa naučíte

Na konci tohto návodu budete schopní:

- **Nainštalovať Hermes Agent** a nasmerovať ho na **Lemonade Server** ako svoj AI backend.
- **(Odporúčané) Povoliť sandboxing Docker/Podman**, aby ste izolovali akcie agenta od vášho hostiteľského systému.
- **Spustiť bránu Hermes** a potvrdiť, že je váš agent pripravený.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli so svojím agentom chatovať z akéhokoľvek zariadenia.

---

<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:linux -->
- PC so systémom **Ubuntu 24.04+** alebo kompatibilnou distribúciou Linuxu založenou na Debiane s `apt-get`
- Aspoň **12 GB pamäte RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10–30 GB voľného miesta na disku** pre váhy modelu
- [Podman](https://podman.io/docs/installation) (voliteľné, pre sandboxing agenta Hermes)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- PC so systémom **Windows 10/11**
- Aspoň **12 GB pamäte RAM** (odporúča sa 64 GB+ pre väčšie modely)
- **~10–30 GB voľného miesta na disku** pre váhy modelu
- Podman (voliteľné, pre sandboxing agenta Hermes). Nainštalujte vnútri WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman je predinštalovaný na Halo Box a nevyžaduje žiadne nastavenie
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stiahnutie a načítanie odporúčaného modelu

Odporúčaným modelom pre tento návod je **Qwen3.6-35B-A3B-GGUF** od spoločnosti Unsloth, výkonný MoE model s kontextovým oknom 263k tokenov, ktorý je dobre vhodný na agentové úlohy. Tento model používa kvantizáciu UD-Q4_K_XL. Stiahnite si ho teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Potom ho načítajte s veľkým kontextovým oknom a uložte toto nastavenie pre budúce spustenia:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model má predvolenú dĺžku kontextu 262 144 tokenov. Ak sa stretnete s chybami nedostatku pamäte (OOM), zvážte zníženie kontextového okna.

> **Tip: Vypnite režim rozmýšľania pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B predvolene beží v režime rozmýšľania, čo pred každou odpoveďou pridáva latenciu. Pri agentových slučkách sa táto réžia rýchlo kumuluje. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá vypína rozmýšľanie. Ak ju chcete použiť, stiahnite si súbor a importujte ho:
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

Hermes Agent spúšťame vnútri WSL a pripájame ho k Lemonade, ktorý beží natívne na Windows. Vďaka tomu máte pre Hermes prostredie Linux shellu, pričom GPU akcelerácia Lemonade zostáva na strane Windows.

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

WSL2 beží vo virtuálnej sieti. Lemonade na Windows je naviazaný na `127.0.0.1`, čo WSL nedokáže priamo dosiahnuť. Port proxy v systéme Windows presmerováva prevádzku z gateway IP adresy WSL na localhost v systéme Windows.

**Zistite svoju gateway IP adresu WSL** (spustite vnútri WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte port proxy** (spustite v PowerShelli ako správca, pričom `<WSL-Gateway-IP>` nahraďte vašou gateway IP adresou WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Pridajte pravidlo brány firewall** (v tom istom zvýšenom okne PowerShellu):

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

> Pravidlo `netsh portproxy` prežije reštart, ale gateway IP adresa WSL sa môže po `wsl --shutdown` zmeniť. Ak sa Lemonade stane po reštarte z WSL nedostupným, zistite aktualizovanú gateway IP adresu a aktualizujte proxy touto novou adresou.

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
> Príkazy v tejto časti spúšťajte vnútri svojho **terminálu WSL**, pokiaľ nie je uvedené inak.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Príznak `--skip-setup` preskočí interaktívneho sprievodcu nastavením, takže backend modelu môžete nakonfigurovať manuálne v nasledujúcom kroku.

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
> Aby to bolo trvalé, pridajte vyššie uvedený riadok do svojho súboru `~/.bashrc` alebo `~/.zshrc`.

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
## Konfigurácia Hermes na používanie Lemonade

Hermes ukladá konfiguráciu modelu v súbore `~/.hermes/config.yaml`. Môžete buď použiť interaktívny výber `hermes model`, alebo napísať konfiguráciu priamo.

### Možnosť 1: Interaktívny výber

<!-- @os:windows -->
> Spustite nasledujúce v rámci vášho **WSL terminálu**.
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

Keď sa zobrazí výzva:

1. Vyberte **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** použite IP adresu WSL brány: spustite `ip route show default | awk '{print $3}' | head -1` vnútri WSL na jej získanie, potom zadajte `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** vyberte `Qwen3.6-35B-A3B-GGUF` zo zoznamu
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (alebo akýkoľvek názov, ktorý uprednostňujete)

`hermes model` uloží výber aktívneho modelu aj pomenovaný záznam `custom_providers`, ktorý uchováva dĺžku kontextu spolu s koncovým bodom. Výsledok v `~/.hermes/config.yaml` vyzerá takto:

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

### Možnosť 2: Napísanie konfigurácie priamo

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

Vnútri vášho WSL terminálu získajte IP adresu hostiteľa Windows a napíšte konfiguráciu:

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

## (Odporúčané) Povolenie sandboxingu Podman

Hermes Agent dokáže smerovať všetky operácie agenta s príkazovým riadkom a súbormi cez izolovaný kontajner namiesto ich priameho spúšťania na vašom hostiteľovi. Toto obmedzuje dosah akejkoľvek neúmyselnej akcie na sandbox, čím ponecháva súborový systém a sieť vášho hostiteľa nedotknuté.

Vytvorte ľahký obraz sandboxu:

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
Vstúpte do vášho WSL terminálu:

```powershell
wsl -d Ubuntu-24.04
```

Potom vytvorte ľahký obraz sandboxu:

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

Potom nakonfigurujte Hermes na používanie Podman ako kontajnerového runtime a nastavte backend terminálu:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` je stále `docker`.
> `HERMES_DOCKER_BINARY` je to, čo hovorí Hermes, aby namiesto toho použil ako runtime Podman.

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

Hermes teraz spustí trvalý kontajner sandboxu a bude cez neho smerovať všetky volania `terminal` a nástrojov na prácu so súbormi. Kontajner zdieľa životnosť procesu Hermes, je opakovane používaný pri všetkých volaniach nástrojov a je zničený pri ukončení Hermes.

> **Overte, že sandbox funguje:** Spustite Hermes (`hermes`) a požiadajte ho, aby spustil `run hostname` - mali by ste vidieť krátke ID kontajnera namiesto hostiteľského názvu vášho počítača. Môžete ho tiež požiadať o `rm -rf <path-to-a-dummy-file/folder>`: Hermes potvrdí odstránenie, ale priečinok bude stále vo vašom hostiteľovi. Príkaz bol spustený vnútri izolovaného `$HOME` kontajnera, nie vo vašom.

> **Potrebujete silnejšiu izoláciu?** Hermes tiež poskytuje oficiálny Docker obraz (`nousresearch/hermes-agent`), ktorý spúšťa celý proces agenta vnútri kontajnera - gateway, nástroje a všetko ostatné. Podrobnosti o nastavení nájdete v [dokumentácii Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Odporúčané) Integrácia Hermes so službami Firecrawl

Hermes dokáže prehliadať a extrahovať obsah z webových stránok pomocou svojich vstavaných webových nástrojov. Mnohé moderné webové stránky však používajú systémy na detekciu botov, ktoré blokujú jednoduché HTTP požiadavky a namiesto skutočného obsahu vracajú stránky s výzvou (challenge pages). V dôsledku toho nemusí byť Hermes schopný spoľahlivo extrahovať informácie z týchto stránok.

Na prekonanie tohto obmedzenia poskytuje [Firecrawl](https://docs.firecrawl.dev/introduction) samostatne hostovanú službu na prehľadávanie webu a extrakciu obsahu, ktorá dokáže obísť tieto výzvy a odomknúť plný potenciál automatizácie Hermes.

V tomto nastavení beží Firecrawl ako súbor Docker kontajnerov spravovaných pomocou Podman. Na zjednodušenie správy životného cyklu a automatického spúšťania registrujeme Firecrawl ako používateľskú `systemd` službu, ktorá orchestruje základný zásobník Podman Compose. Toto umožňuje Hermes spúšťať, zastavovať a overovať službu Firecrawl pomocou štandardných príkazov `systemctl --user` namiesto priamej interakcie s kontajnermi.

Aby sme to zjednodušili, celý proces sme rozdelili do štyroch krokov:

---

### 1. Registrácia systémovej služby
Prejdite do adresára s konfiguráciou používateľa systemd:
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
V tomto bode je služba definovaná, ale ešte nie je zaregistrovaná v `systemd`.
Uistite sa, že názov súboru presne zodpovedá tomu, ktorý ste vytvorili vyššie, potom spustite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ak je to úspešné, mali by ste vidieť nasledujúci výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` obsahuje symbolické odkazy na služby, ktoré sú nakonfigurované na automatické spustenie.

### 2. Konfigurácia Firecrawl pre vašu službu

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideálny pre tých, ktorí potrebujú plnú kontrolu nad svojím prostredím na scraping a spracovanie dát, no prináša so sebou kompromis v podobe dodatočnej údržby a konfiguračného úsilia.

Začnite naklonovaním repozitára:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Vytvorte `.env` v koreňovom adresári `/firecrawl`:
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
> Nastavte `BULL_AUTH_KEY` na silné tajomstvo, obzvlášť pri akomkoľvek nasadení dostupnom z nedôveryhodných sietí.
### 3. Nasadenie Hermes cez Compose

Pred pokračovaním sa uistite, že máte stiahnutý najnovší Docker image Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Po dokončení si stiahnite súbor Compose pre Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) a umiestnite ho do koreňového adresára `/firecrawl`:

> Toto pomenovanie je potrebné na to, aby `systemd` dokázal nájsť a spustiť službu podľa špecifikácie `WorkingDirectory=${HOME}/firecrawl`.

> Zásobník môžete kedykoľvek rozšíriť o ďalšie služby Firecrawl podľa potreby. Úplný zoznam dostupných služieb nájdete v oficiálnom súbore [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spustenie služby Hermes prostredníctvom Firecrawl 

Pred odovzdaním riadenia službe `systemd` overte, že všetko funguje správne, manuálnym spustením zásobníka:
```bash
podman compose -f hermes-compose.yaml up -d
```
Ak je všetko správne nakonfigurované, mal by sa zobraziť spustený kontajner Hermes a výstup príkazového riadka by mal vyzerať podobne ako tento:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Po overení zásobník pred pokračovaním opäť vypnite:
```bash
podman compose -f hermes-compose.yaml down
```
Teraz, keď je všetko overené, spustite službu prostredníctvom `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API rozhranie Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) je dostupné z interaktívneho kontajnera a webový dashboard je dostupný na rovnakom hostiteľovi a porte na adrese http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Službu zastavíte príkazom:
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

**Gratulujeme, vybudovali ste plne lokálny zásobník AI agenta.**

### Webový dashboard

Hermes obsahuje webové rozhranie na správu konfigurácie, API kľúčov, modelov, relácií, pamäte a plánovaných úloh (cron jobs). Otvorte druhý terminál, kým beží gateway alebo CLI, a spustite ho pomocou:

```bash
hermes dashboard
```

Týmto sa spustí lokálny server a vo vašom prehliadači sa otvorí adresa `http://127.0.0.1:9119`. Úplný prehľad funkcií nájdete v [dokumentácii k dashboardu](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Keď gateway beží, môžete sa k svojmu lokálnemu agentovi pripojiť z akéhokoľvek zariadenia. Hermes podporuje [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) a ďalšie

---

### Discord

Discord vyžaduje server, na ktorom **máte administrátorský prístup**, aby ste mohli pridať bota. Ak zdieľate servery, ale žiadny nevlastníte, použite namiesto toho Telegram.

#### Vytvorenie Discord aplikácie a bota

1. Prejdite na [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte názov (napr. „hermes-bot").
2. V bočnom paneli kliknite na **Bot**. Nastavte pre bota používateľské meno.
3. Na stránke Bot sa posuňte nadol k sekcii **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Vráťte sa nahor a kliknite na **Reset Token**, čím vygenerujete token bota. Skopírujte si ho.

#### Pridanie bota na váš server

1. V bočnom paneli kliknite na **OAuth2 / URL Generator**.
2. V sekcii **Scopes** povoľte `bot` a `applications.commands`.
3. V sekcii **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú URL adresu, vložte ju do prehliadača, vyberte svoj server a potvrďte.

#### Získanie ID a povolenie priamych správ

Povoľte v Discorde režim pre vývojárov (**User Settings / Advanced / Developer Mode**), potom:
- Kliknite pravým tlačidlom na ikonu vášho servera: **Copy Server ID**
- Kliknite pravým tlačidlom na svoj vlastný avatar: **Copy User ID**

Kliknite pravým tlačidlom na ikonu servera / **Privacy Settings** / zapnite **Direct Messages**. Toto je potrebné pre krok párovania.

#### Konfigurácia Hermes pre Discord

Pridajte nasledujúce do `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Potom spustite gateway:

```bash
hermes gateway
```

Bot by sa mal v Discorde spustiť online v priebehu niekoľkých sekúnd. Pošlite mu správu, buď priamu správu, alebo v kanáli, ktorý vidí.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Vytvorenie Telegram bota

1. Otvorte Telegram a napíšte správu botovi **@BotFather**.
2. Odošlite `/newbot` a postupujte podľa pokynov. Uložte si token bota, ktorý vám bot poskytne.

#### Konfigurácia Hermes pre Telegram

Pridajte nasledujúce do `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Nepoznáte svoje Telegram ID používateľa?** Napíšte správu [@userinfobot](https://t.me/userinfobot) v Telegrame,  odpovie vám vaším číselným ID.

Potom spustite gateway:

```bash
hermes gateway
```

Na otestovanie pošlite svojmu botovi akúkoľvek správu v Telegrame. Teraz môžete komunikovať so svojím agentom prostredníctvom priamych správ v Telegrame. Pre webhook režim a pokročilé možnosti si pozrite [úplného sprievodcu nastavením Telegramu](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Ďalšie kroky

Teraz, keď váš agent dokáže prijímať príkazy z telefónu a konať na vašom lokálnom počítači, tu sú tri smery, ktoré stojí za to preskúmať:

1. **Automatizovaný prehľad výskumu**: Naplánujte, aby Hermes každé ráno vyhľadával na webe témy, ktoré vás zaujímajú, zhrnul zistenia pomocou vášho lokálneho modelu a odoslal súhrn do telefónu cez Telegram alebo Discord, to všetko bežiace na vašom vlastnom hardvéri bez akýchkoľvek nákladov na cloud.

2. **Kontrola kódu na vyžiadanie**: Nasmerujte Hermes na repozitár GitHub, požiadajte ho o kontrolu otvorených pull requestov a nechajte ho zverejniť komentáre alebo súhrn späť do vášho chatu. Vďaka backendu terminálu Docker prebiehajú všetky operácie git vnútri sandboxu, čím zostáva váš hostiteľský systém čistý.

3. **Lokálny asistent pre súbory**: Poskytnite Hermes prístup k pracovnému adresáru a požiadajte ho, aby na vyžiadanie z telefónu organizoval, premenovával, zhrnul alebo transformoval súbory. Keďže backend terminálu Docker obmedzuje všetky zápisy na pracovný priestor sandboxu, náhodné deštruktívne operácie sú obmedzené.