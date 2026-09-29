<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Spuštění agenta Hermes Agent lokálně pomocí Lemonade Server

## Přehled

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) je samoučící se AI agent vytvořený společností Nous Research. Má vestavěnou učební smyčku, vytváří dovednosti na základě zkušeností, buduje trvalou paměť o tom, kdo jste, napříč relacemi, a může vaším jménem spouštět naplánované automatizace. Na rozdíl od jednoduchého chatovacího asistenta Hermes provádí skutečné akce: spouští příkazy shellu, zapisuje soubory, prohlíží web a deleguje paralelní pracovní postupy na podagenty.

[**Lemonade Server**](https://lemonade-server.ai/) je lokální inferenční backend, který ho pohání. Jedná se o open-source server, který spouští GenAI modely přímo na vašem hardwaru AMD a zpřístupňuje je prostřednictvím standardního rozhraní OpenAI API.

Společně tvoří plně lokální zásobník AI agenta: Lemonade se stará o inferenci modelu na vašem GPU a Hermes poskytuje smyčku agenta, paměť, dovednosti a bránu pro zasílání zpráv.

> **Než budete pokračovat:** Hermes Agent je vysoce autonomní AI agent. Poskytnutí přístupu k vašemu systému jakémukoli AI agentovi může vést k nepředvídatelným nebo nezamýšleným výsledkům. Pokračujte pouze tehdy, pokud rozumíte rizikům a jste s tím, že za vás jedná autonomní software, srozuměni.

---

## Co se naučíte

Na konci tohoto průvodce budete schopni:

- **Nainstalovat Hermes Agent** a nasměrovat ho na **Lemonade Server** jako svůj AI backend.
- **(Doporučeno) Povolit sandboxing pomocí Docker/Podman** k izolaci akcí agenta od hostitele.
- **Spustit bránu Hermes** a ověřit, že je váš agent připraven.
- **Připojit komunikační kanál** (Discord nebo Telegram), abyste mohli se svým agentem komunikovat z jakéhokoli zařízení.

---

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @os:linux -->
- PC se systémem **Ubuntu 24.04+** nebo kompatibilní linuxovou distribucí založenou na Debianu s nástrojem `apt-get`
- Alespoň **12 GB RAM** (doporučeno 64 GB+ pro větší modely)
- **~10–30 GB volného místa na disku** pro váhy modelů
- [Podman](https://podman.io/docs/installation) (Volitelné, pro sandboxing Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- PC se systémem **Windows 10/11**
- Alespoň **12 GB RAM** (doporučeno 64 GB+ pro větší modely)
- **~10–30 GB volného místa na disku** pro váhy modelů
- Podman (Volitelné, pro sandboxing Hermes Agent). Nainstalujte uvnitř WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman je předinstalován na Halo Box a není nutné žádné nastavení
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stáhněte a načtěte doporučený model

Doporučeným modelem pro tohoto průvodce je **Qwen3.6-35B-A3B-GGUF** od Unsloth, výkonný MoE model s kontextovým oknem o velikosti 263 tisíc tokenů, který je dobře vhodný pro pracovní zátěže agentů. Tento model používá kvantizaci UD-Q4_K_XL. Stáhněte ho nyní:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Poté ho načtěte s velkým kontextovým oknem a uložte toto nastavení pro budoucí spuštění:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model má výchozí délku kontextu 262 144 tokenů. Pokud narazíte na chyby nedostatku paměti (OOM), zvažte zmenšení kontextového okna.

> **Tip: Vypněte přemýšlení pro rychlejší odpovědi agenta:** Qwen3.6-35B-A3B ve výchozím nastavení běží v režimu přemýšlení, který před každou odpovědí přidává latenci. U smyček agenta se tato režie rychle hromadí. Repozitář [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje předpřipravenou konfiguraci, která přemýšlení vypne. Chcete-li ji použít, stáhněte soubor a naimportujte jej:
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

## Nastavení WSL

Hermes Agent spouštíme uvnitř WSL a připojujeme ho k Lemonade, který běží nativně ve Windows. To vám poskytne prostředí Linux shellu pro Hermes a zároveň zachová GPU akceleraci Lemonade na straně Windows.

### Instalace WSL a Ubuntu

Otevřete PowerShell jako správce a nainstalujte jádro WSL:

```powershell
wsl --install --no-distribution
```

Poté nainstalujte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Povolení systemd ve WSL

Spusťte toto uvnitř terminálu Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Restartujte WSL:

```powershell
wsl --shutdown
wsl
```

### Přemostění Lemonade z Windows do WSL

WSL2 běží ve virtuální síti. Lemonade ve Windows se váže na `127.0.0.1`, který WSL nemůže přímo dosáhnout. Proxy portu Windows přeposílá provoz z gateway IP adresy WSL na Windows localhost.

**Zjistěte gateway IP adresu WSL** (spusťte uvnitř WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Přidejte proxy portu** (spusťte v PowerShellu jako správce, nahraďte `<WSL-Gateway-IP>` svou gateway IP adresou WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Přidejte pravidlo brány firewall** (stejný elevovaný PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ověřte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Pokud jste v předchozím kroku již načetli model Qwen3.6-35B-A3B-GGUF, měli byste vidět výstup JSON s výpisem vašeho načteného modelu.

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

> Pravidlo `netsh portproxy` přetrvá restarty, ale gateway IP adresa WSL se může po `wsl --shutdown` změnit. Pokud se Lemonade po restartu stane z WSL nedostupným, zjistěte aktualizovanou gateway IP adresu a aktualizujte proxy touto novou IP adresou.

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

## Instalace Hermes Agent

<!-- @os:windows -->
> Příkazy v této části spouštějte uvnitř svého **terminálu WSL**, pokud není uvedeno jinak.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Příznak `--skip-setup` přeskočí interaktivního průvodce nastavením, abyste mohli backend modelu nakonfigurovat ručně v dalším kroku.

Znovu načtěte svůj shell:

```bash
source ~/.bashrc
```

Ověřte instalaci:

```bash
hermes --version
```

Spusťte vlastní diagnostiku ke kontrole všech závislostí:

```bash
hermes doctor
```

> **Tip:** Pokud se po instalaci zobrazí `command not found`, přidejte Hermes do své PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Aby bylo toto nastavení trvalé, přidejte výše uvedený řádek do svého `~/.bashrc` nebo `~/.zshrc`.

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
## Konfigurace Hermes pro použití Lemonade

Hermes ukládá konfiguraci modelu do souboru `~/.hermes/config.yaml`. Můžete použít buď interaktivní výběr pomocí `hermes model`, nebo zapsat konfiguraci přímo.

### Možnost 1: Interaktivní výběr

<!-- @os:windows -->
> Následující příkaz spusťte uvnitř svého **terminálu WSL**.
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
2. **API base URL:** použijte IP adresu brány WSL: spuštěním `ip route show default | awk '{print $3}' | head -1` uvnitř WSL ji zjistíte, poté zadejte `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** ze seznamu vyberte `Qwen3.6-35B-A3B-GGUF`
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (nebo libovolný název dle vašeho výběru)

Příkaz `hermes model` uloží jak aktivní výběr modelu, tak pojmenovanou položku `custom_providers`, která spolu s koncovým bodem uchovává i délku kontextu. Výsledek v souboru `~/.hermes/config.yaml` vypadá takto:

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

### Možnost 2: Zápis konfigurace přímo

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

Uvnitř terminálu WSL zjistěte IP adresu hostitele Windows a zapište konfiguraci:

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

## (Doporučeno) Povolení sandboxingu pomocí Podman

Hermes Agent dokáže směrovat veškeré operace agenta se shellem a soubory přes izolovaný kontejner, místo aby je spouštěl přímo na vašem hostiteli. Tím se dopad jakékoli neúmyslné akce omezí pouze na sandbox, zatímco souborový systém a síť vašeho hostitele zůstanou nedotčené.

Sestavte odlehčený sandboxový image:

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
Otevřete svůj terminál WSL:

```powershell
wsl -d Ubuntu-24.04
```

Poté sestavte odlehčený sandboxový image:

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

Poté nakonfigurujte Hermes tak, aby jako kontejnerový runtime používal Podman, a nastavte backend terminálu:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` zůstává nastaven na `docker`.
> `HERMES_DOCKER_BINARY` je to, co říká Hermes, aby jako runtime použil místo toho Podman.

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

Hermes nyní spustí trvalý sandboxový kontejner a bude přes něj směrovat veškerá volání `terminal` a souborových nástrojů. Kontejner sdílí životní cyklus s procesem Hermes, je opakovaně používán pro všechna volání nástrojů a je zničen při ukončení Hermes.

> **Ověřte, že sandbox funguje:** Spusťte Hermes (`hermes`) a požádejte ho, aby spustil `run hostname` – měli byste vidět krátké ID kontejneru místo hostname vašeho počítače. Můžete ho také požádat, aby provedl `rm -rf <path-to-a-dummy-file/folder>`: Hermes potvrdí smazání, ale složka zůstane na vašem hostiteli i nadále. Příkaz totiž proběhl uvnitř izolovaného `$HOME` kontejneru, nikoli ve vašem.

> **Potřebujete silnější izolaci?** Hermes také poskytuje oficiální Docker image (`nousresearch/hermes-agent`), který spouští celý proces agenta uvnitř kontejneru – gateway, nástroje, vše. Podrobnosti o nastavení najdete v [dokumentaci Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Doporučeno) Integrace Hermes se službami Firecrawl

Hermes dokáže procházet a extrahovat obsah z webových stránek pomocí svých vestavěných webových nástrojů. Mnoho moderních webových stránek však používá systémy detekce botů, které blokují jednoduché HTTP požadavky a namísto skutečného obsahu vrací výzvové (challenge) stránky. V důsledku toho Hermes nemusí být schopen spolehlivě extrahovat informace z těchto stránek.

Aby bylo možné toto omezení překonat, poskytuje [Firecrawl](https://docs.firecrawl.dev/introduction) samostatně hostovanou službu pro procházení webu a extrakci obsahu, která dokáže tyto výzvy obejít a odemknout plný potenciál automatizace Hermes.

V tomto nastavení běží Firecrawl jako sada Docker kontejnerů spravovaných pomocí Podman. Pro zjednodušení správy životního cyklu a automatického spouštění registrujeme Firecrawl jako uživatelskou službu `systemd`, která orchestruje podkladový zásobník Podman Compose. Díky tomu může Hermes spouštět, zastavovat a ověřovat službu Firecrawl pomocí standardních příkazů `systemctl --user` namísto přímé interakce s kontejnery.

Pro jednoduchost jsme celý proces rozdělili do čtyř kroků:

---

### 1. Registrace systémové služby
Přejděte do adresáře uživatelské konfigurace systemd:
```bash
cd ~/.config/systemd/user
```
Vytvořte a otevřete nový soubor s názvem `firecrawl.service`.
```bash
nano firecrawl.service
```
Zkopírujte a vložte následující konfiguraci:
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
V tuto chvíli je služba definována, ale zatím není registrována u `systemd`.
Ujistěte se, že název souboru přesně odpovídá tomu, který jste vytvořili výše, a poté spusťte:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Pokud vše proběhlo úspěšně, měli byste vidět následující výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby, které jsou nakonfigurovány tak, aby se spouštěly automaticky.

### 2. Konfigurace Firecrawl pro vaši službu

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideální pro ty, kdo potřebují plnou kontrolu nad svým prostředím pro scraping a zpracování dat, což je ovšem vykoupeno zvýšenými nároky na údržbu a konfiguraci.

Začněte naklonováním repozitáře:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Vytvořte soubor `.env` v kořenovém adresáři `/firecrawl`:
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
> Nastavte `BULL_AUTH_KEY` na silné tajemství, zejména u jakéhokoli nasazení dostupného z nedůvěryhodných sítí.
### 3. Nasazení Hermes přes Compose

Než budete pokračovat, ujistěte se, že jste stáhli nejnovější Docker image Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Jakmile to bude hotové, stáhněte soubor Compose pro Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) a umístěte jej do kořenového adresáře `/firecrawl`:

> Tato konvence je nutná, aby `systemd` mohl správně najít a spustit službu tak, jak je uvedeno v `WorkingDirectory=${HOME}/firecrawl`.

> Zásobník můžete kdykoli rozšířit přidáním dalších služeb Firecrawl podle potřeby. Úplný seznam dostupných služeb naleznete v oficiálním souboru [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spuštění služby Hermes prostřednictvím Firecrawl 

Než předáte řízení nástroji `systemd`, ověřte, že vše funguje správně, spuštěním zásobníku ručně:
```bash
podman compose -f hermes-compose.yaml up -d
```
Pokud je vše nakonfigurováno správně, měli byste vidět, že se kontejner Hermes spustil, a výstup na příkazovém řádku by měl vypadat podobně jako tento:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Po ověření zásobník před pokračováním opět vypněte:
```bash
podman compose -f hermes-compose.yaml down
```
Nyní, když je vše ověřeno, spusťte službu prostřednictvím `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) je přístupné zevnitř interaktivního kontejneru a webový panel je dostupný na stejném hostiteli a portu na adrese http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Chcete-li službu zastavit, spusťte:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Spusťte přímo interaktivní relaci CLI: 

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

**Gratulujeme, sestavili jste plně lokální zásobník AI agenta.**

### Webový panel

Hermes obsahuje uživatelské rozhraní ve webovém prohlížeči pro správu konfigurace, klíčů API, modelů, relací, paměti a plánovaných úloh (cron jobs). Otevřete druhý terminál, zatímco běží brána nebo CLI, a spusťte jej pomocí:

```bash
hermes dashboard
```

Tím se spustí místní server a v prohlížeči se otevře `http://127.0.0.1:9119`. Úplný přehled funkcí naleznete v [dokumentaci k panelu](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Volitelné: Připojení komunikačního kanálu

Jakmile brána běží, můžete se ke svému lokálnímu agentovi připojit z libovolného zařízení. Hermes podporuje [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) a další

---

### Discord

Discord vyžaduje server, na kterém **máte přístup administrátora**, abyste mohli přidat bota. Pokud sdílíte servery, ale žádný nevlastníte, použijte místo toho Telegram.

#### Vytvoření aplikace a bota v Discordu

1. Přejděte na [Discord Developer Portal](https://discord.com/developers/applications) a klikněte na **New Application**. Zadejte název (např. „hermes-bot“).
2. V postranním panelu klikněte na **Bot**. Nastavte uživatelské jméno bota.
3. Na stejné stránce Bot přejděte dolů na **Privileged Gateway Intents** a povolte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (doporučené)
4. Přejděte zpět nahoru a klikněte na **Reset Token**, čímž vygenerujete token bota. Zkopírujte jej.

#### Přidání bota na váš server

1. V postranním panelu klikněte na **OAuth2 / URL Generator**.
2. V části **Scopes** povolte `bot` a `applications.commands`.
3. V části **Bot Permissions** povolte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Zkopírujte vygenerovanou adresu URL, vložte ji do prohlížeče, vyberte svůj server a potvrďte.

#### Získání ID a povolení soukromých zpráv

Povolte v Discordu vývojářský režim (**User Settings / Advanced / Developer Mode**) a poté:
- Klikněte pravým tlačítkem na ikonu serveru: **Copy Server ID**
- Klikněte pravým tlačítkem na svůj avatar: **Copy User ID**

Klikněte pravým tlačítkem na ikonu serveru / **Privacy Settings** / zapněte možnost **Direct Messages**. To je nutné pro krok párování.

#### Konfigurace Hermes pro Discord

Do souboru `~/.hermes/.env` přidejte následující:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Poté spusťte bránu:

```bash
hermes gateway
```

Bot by se měl v Discordu během několika sekund objevit online. Pošlete mu zprávu, ať už jako soukromou zprávu, nebo v kanálu, který vidí.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Vytvoření bota v Telegramu

1. Otevřete Telegram a napište zprávu **@BotFather**.
2. Odešlete `/newbot` a postupujte podle pokynů. Uložte si token bota, který obdržíte.

#### Konfigurace Hermes pro Telegram

Do souboru `~/.hermes/.env` přidejte následující:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Neznáte své uživatelské ID v Telegramu?** Napište zprávu botovi [@userinfobot](https://t.me/userinfobot) v Telegramu, odpoví vám vaším číselným ID.

Poté spusťte bránu:

```bash
hermes gateway
```

Pro otestování pošlete svému botovi jakoukoli zprávu v Telegramu. Nyní si můžete se svým agentem povídat prostřednictvím soukromých zpráv v Telegramu. Úplný návod na nastavení webhooku a pokročilé možnosti naleznete v [kompletním průvodci nastavením Telegramu](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Další kroky

Nyní, když váš agent dokáže přijímat příkazy z vašeho telefonu a jednat na vašem lokálním počítači, zde jsou tři směry, které stojí za prozkoumání:

1. **Automatizovaný souhrn výzkumu**: Naplánujte, aby Hermes každé ráno prohledával web ohledně témat, která vás zajímají, shrnul zjištění pomocí vašeho lokálního modelu a odeslal souhrn do vašeho telefonu prostřednictvím Telegramu nebo Discordu, to vše běžící na vašem vlastním hardwaru bez jakýchkoli nákladů na cloud.

2. **Recenze kódu na vyžádání**: Nasměrujte Hermes na repozitář GitHub, požádejte jej o kontrolu otevřených pull requestů a nechte jej publikovat komentáře nebo souhrn zpět do vašeho chatu. Díky backendu terminálu v Dockeru probíhají všechny operace git uvnitř sandboxu, takže váš hostitelský systém zůstává čistý.

3. **Lokální asistent pro soubory**: Poskytněte Hermesu přístup k pracovnímu adresáři a požádejte jej, aby na vyžádání z vašeho telefonu organizoval, přejmenovával, shrnoval nebo transformoval soubory. Protože backend terminálu v Dockeru omezuje všechny zápisy na pracovní prostor sandboxu, náhodné destruktivní operace zůstávají izolované.