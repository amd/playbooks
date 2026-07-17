<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Spuštění OpenClaw s Lemonade Server jako backendem

## Přehled

[**OpenClaw**](https://openclaw.ai/) je autonomní AI agent, který dokáže psát a spouštět kód, spravovat soubory a zvládat složité vícekrokové úkoly vaším jménem. Na rozdíl od chatovacího asistenta, který pouze odpovídá na otázky, OpenClaw provádí skutečné akce ve vašem systému – to znamená, že potřebuje rychlý a schopný AI backend, který zvládne náročnou smyčku agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je právě takovým backendem. Jde o open-source lokální inferenční server, který spouští GenAI modely přímo na vašem hardwaru a zpřístupňuje je prostřednictvím průmyslově standardního OpenAI API.

Společně tvoří plně lokální stack AI agenta: Lemonade zajišťuje inferenci modelu a OpenClaw poskytuje smyčku agenta, která převádí výstupy modelu na skutečné akce.

> **Než budete pokračovat:** OpenClaw je vysoce autonomní AI agent. Poskytnutí přístupu jakéhokoli AI agenta k vašemu systému může vést k nepředvídatelným nebo nezamýšleným výsledkům. Pokračujte pouze v případě, že rozumíte rizikům a jste srozuměni s tím, že autonomní software jedná vaším jménem.

---

## Co se naučíte

Po dokončení tohoto návodu budete schopni:

- Dozvědět se více o **Lemonade Server**
- **Nainstalovat OpenClaw** a **nasměrovat jej na Lemonade Server** jako jeho AI backend.
- **Spustit bránu OpenClaw** a ověřit, že je váš agent připraven k práci.
- **Připojit komunikační kanál** (Discord nebo Telegram), abyste mohli chatovat se svým agentem z libovolného zařízení.

---

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @os:linux -->
- PC s **Ubuntu 24.04+** nebo kompatibilní distribucí Linuxu založenou na Debianu s `apt-get`
- Alespoň **12 GB RAM** (doporučeno 64 GB+ pro větší modely)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (volitelné, pro izolaci OpenClaw v sandboxu)

- **~10–30 GB volného místa na disku** pro váhy modelu
<!-- @os:end -->
<!-- @os:windows -->
- PC s **Windows 10/11**
- Alespoň **12 GB RAM** (doporučeno 64 GB+ pro větší modely)
- **~10–30 GB volného místa na disku** pro váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (volitelné, pro izolaci OpenClaw v sandboxu)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Stažení a načtení doporučeného modelu

Doporučeným modelem pro tento návod je **Qwen3.6-35B-A3B-GGUF** od Unsloth – silný MoE model s kontextovým oknem 263k tokenů, který je vhodný pro úlohy agentů. Tento model používá kvantizaci UD-Q4_K_XL. Stáhněte jej nyní:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Poté jej načtěte s velkým kontextovým oknem a uložte toto nastavení pro budoucí spuštění:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má výchozí délku kontextu 262 144 tokenů. Pokud narazíte na chyby nedostatku paměti (OOM), zvažte zmenšení kontextového okna. Protože však Qwen3.6 využívá rozšířený kontext pro složité úkoly, doporučujeme zachovat délku kontextu alespoň 128K tokenů, aby byly zachovány schopnosti uvažování.

> **Tip: Zakažte uvažování pro rychlejší odpovědi agenta:** Qwen3.6-35B-A3B ve výchozím nastavení běží v režimu uvažování, což přidává latenci před každou odpovědí. V smyčkách agentů se tato režie rychle hromadí. Repozitář [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovou konfiguraci, která uvažování vypíná. Chcete-li ji použít, stáhněte soubor a importujte jej:
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

## Nastavení WSL

OpenClaw spouštíme uvnitř WSL (doporučeno) a připojujeme jej k Lemonade běžícímu nativně na Windows. Tím získáte prostředí linuxového shellu pro OpenClaw, přičemž GPU akcelerace Lemonade zůstane na straně Windows.

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

WSL2 běží ve virtuální síti. Lemonade na Windows se váže na `127.0.0.1`, které WSL nemůže přímo dosáhnout. Proxy port Windows přesměrovává provoz z IP adresy brány WSL na localhost Windows.

**Zjistěte IP adresu brány WSL** (spusťte uvnitř WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Přidejte proxy port** (spusťte v PowerShellu jako správce, nahraďte `<WSL-Gateway-IP>` IP adresou vaší brány WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Přidejte pravidlo brány firewall** (stejný PowerShell se zvýšenými oprávněními):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ověřte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Pokud jste v předchozím kroku již načetli model Qwen3.6-35B-A3B-GGUF, měli byste vidět výstup JSON podobný tomuto:

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

> Pravidlo `netsh portproxy` přežije restartování, ale IP adresa brány WSL se může změnit po `wsl --shutdown`. Pokud se Lemonade stane po restartu z WSL nedostupným, zjistěte aktualizovanou IP adresu brány a aktualizujte proxy touto novou IP adresou.

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

## Instalace a konfigurace OpenClaw

### Instalace OpenClaw
<!-- @os:windows -->
> Příkazy v této části spouštějte uvnitř svého **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Příznak `--no-onboard` přeskočí interaktivního průvodce nastavením – backend modelu nakonfigurujete ručně v dalším kroku, což vám dává přesnou kontrolu nad tím, který model a server se použijí.

Otevřete nový terminál a potvrďte instalaci:

```bash
openclaw --version
```

> **Tip:** Pokud po instalaci vidíte `command not found`, přidejte globální adresář bin npm do své proměnné PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Chcete-li toto nastavení zachovat trvale, přidejte výše uvedený řádek do souboru `~/.bashrc` nebo `~/.zshrc`.

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


### Konfigurace OpenClaw pro použití Lemonade

Spusťte neinteraktivní onboarding OpenClaw.
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

Tento příkaz zapíše konfiguraci OpenClaw do `~/.openclaw/openclaw.json`.

> **Velikost kontextového okna OpenClaw:** Kompakce OpenClaw se spustí, když `contextTokens > contextWindow − reserveTokens`. Výchozí hodnota `reserveTokensFloor` je 20 000 tokenů – spodní hranice, která přepíše `reserveTokens`, pokud je nižší – takže jakýkoli kontext modelu pod ~37k spustí nekonečnou smyčku kompakce. Nastavte nízkou rezervu a jednou zakažte spodní hranici ve své konfiguraci a toto nastavení se použije pro každý model bez nutnosti ladění pro jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodní hranice* (minimální ochrana), nikoli samotná rezerva – nastavení pouze spodní hranice nemá žádný efekt. `reserveTokensFloor: 0` ochranu deaktivuje, takže nižší hodnota `reserveTokens` je přijata.
>
> **Kdy toto použít:** Tuto konfiguraci použijte, pokud je efektivní kontextové okno vašeho modelu pod ~37k, buď proto, že model je malý (např. 8k, 16k, 32k), nebo proto, že jste jej záměrně omezili na nižší hodnotu (např. načtení modelu 128k, ale nastavení kontextu na 16k v Lemonade). Bez tohoto nastavení OpenClaw při spuštění vstoupí do nekonečné smyčky kompakce.
>
> **Velké kontextové modely při plném kontextu:** Toto můžete zcela přeskočit. Výchozí nastavení funguje dobře – kompakce se spustí ještě před zaplněním okna a model má dostatek prostoru pro generování dlouhých odpovědí. Pokud toto nastavení přesto použijete, mějte na paměti, že `reserveTokens: 4096` omezuje délku odpovědi na ~4k tokenů, což může přerušit dlouhé generování souborů nebo podrobné plány.
>
> **Kam toto přidat:** Umístěte blok `compaction` do `agents.defaults` ve vašem `openclaw.json` (obvykle na `~/.openclaw/openclaw.json`):
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
> Zbytek vaší konfigurace (brána, kanály, modely atd.) zůstává nezměněn – přidat je třeba pouze klíč `compaction`.

### (Doporučeno) Povolení izolace v Docker sandboxu

OpenClaw může směrovat všechny operace agenta se soubory a kódem přes izolovaný Docker kontejner, místo aby je spouštěl přímo na vašem hostiteli. Tím se omezí dosah jakékoli nezamýšlené akce na sandbox, přičemž souborový systém a síť hostitele zůstanou nedotčeny.

Jednou sestavte obraz sandboxu (Docker musí být nainstalován):

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

Spusťte toto, abyste přidali klíč `sandbox` do existujícího bloku `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Kontejnery sandboxu nemají ve výchozím nastavení **žádný přístup k síti**. Informace o připojení svazků a přepsání sítě naleznete v [referenci sandboxingu](https://docs.openclaw.ai/gateway/sandboxing).

> #### Řešení problémů: Odepřeno oprávnění Docker
> 
> Pokud při spouštění příkazů Docker dostanete chybu „permission denied":
> 
> **Krok 1: Přidejte svého uživatele do skupiny docker**
> 
> ```bash
> sudo groupadd docker                    # Vytvořte skupinu, pokud neexistuje
> sudo usermod -aG docker $USER           # Přidejte se do skupiny
> newgrp docker                           # Aktivujte změnu
> docker run hello-world                  # Otestujte
> ```
> 
> **Krok 2: Pokud chyba přetrvává, použijte trvalou opravu**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Poté **restartujte** systém.
> 
> **Rychlá dočasná oprava** (po restartu se resetuje):
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

### Spuštění brány OpenClaw

Brána je proces OpenClaw, který spravuje smyčku agenta a obsluhuje dashboard:

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

Chcete-li otevřít dashboard, spusťte toto v druhém terminálu, zatímco brána stále běží:

```bash
openclaw dashboard
```

Protože se brána váže na loopback, dashboard se při otevření ze stejného počítače automaticky ověří – není potřeba zadávat token ani schvalovat zařízení pro lokální přístup. Měli byste vidět dashboard OpenClaw s vaším modelem Lemonade uvedeným jako aktivní backend.

> Pokud jste povolili sandboxing, můžete jej ověřit tak, že agenta požádáte o `run hostname` z dashboardu. Pokud místo názvu hostitele vašeho počítače vidíte krátké ID kontejneru, sandbox funguje.

**Gratulujeme, vybudovali jste plně lokální stack AI agenta od základu.**

> **Potřebujete token brány?** Spusťte `openclaw dashboard --no-open`, abyste vytiskli URL dashboardu s vloženým tokenem (zároveň se pokusí zkopírovat jej do schránky). Alternativně je token dostupný na `gateway.auth.token` v `~/.openclaw/openclaw.json`.
>
> **Schválení vzdáleného zařízení:** Když otevřete dashboard z druhého počítače nebo telefonu, prohlížeč zobrazí ID požadavku. Zpět na počítači, kde běží brána, spusťte:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potřeba pouze pro vzdálená nebo sekundární zařízení – přístup přes loopback ze stejného počítače se ověřuje automaticky.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Volitelné: Připojení komunikačního kanálu

Jakmile brána běží, můžete se ke svému lokálnímu agentovi dostat z libovolného zařízení. Vyberte si možnost, která vyhovuje vašemu nastavení. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a další kanály – úplný seznam naleznete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord vyžaduje server, kde **máte přístup správce** pro přidání bota. Pokud sdílíte servery, ale žádný nevlastníte, použijte místo toho možnost B (Telegram).

#### Vytvoření účtu Discord a serveru

Pokud nemáte účet Discord, zaregistrujte se na [discord.com](https://discord.com). Potřebujete také server, kde jste správcem – vytvořte jej kliknutím na ikonu **+** v postranním panelu Discordu a výběrem **Create My Own**. Soukromý server je v pořádku.

#### Vytvoření aplikace Discord a bota

1. Přejděte na [Discord Developer Portal](https://discord.com/developers/applications) a klikněte na **New Application**. Zadejte název (např. „openclaw-bot").
2. V postranním panelu klikněte na **Bot**. Nastavte uživatelské jméno bota.
3. Stále na stránce Bot přejděte dolů na **Privileged Gateway Intents** a povolte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (doporučeno)
4. Přejděte zpět nahoru a klikněte na **Reset Token** pro vygenerování tokenu bota. Zkopírujte jej.

#### Přidání bota na váš server

1. V postranním panelu klikněte na **OAuth2/ URL Generator**.
2. V části **Scopes** povolte `bot` a `applications.commands`.
3. V části **Bot Permissions** povolte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Zkopírujte vygenerovanou URL, vložte ji do prohlížeče, vyberte svůj server a potvrďte. Bot by se nyní měl zobrazit v seznamu členů vašeho serveru.

#### Získání vašich ID

Povolte Vývojářský režim v Discordu (**Uživatelská nastavení/ Pokročilé/ Vývojářský režim**), poté:
- Klikněte pravým tlačítkem na ikonu serveru: **Copy Server ID**
- Klikněte pravým tlačítkem na svůj avatar: **Copy User ID**

#### Povolení přímých zpráv od členů serveru

Klikněte pravým tlačítkem na ikonu serveru/ **Nastavení soukromí**/ zapněte **Direct Messages**. Tím umožníte botovi posílat vám přímé zprávy, což je vyžadováno pro krok párování.

#### Konfigurace OpenClaw pro Discord

Uložte token bota jako proměnnou prostředí, poté vytvořte jeden soubor záplaty, který povolí Discord, odkazuje na token a přidá váš server na seznam povolených. Nahraďte `<server_id>` a `<user_id>` výše získanými ID.

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

> **Nespoléhejte na to, že agenta požádáte o tuto konfiguraci.** Pokud je povolen sandboxing, agent nemůže zapisovat do `~/.openclaw/openclaw.json` zevnitř sandboxu – místo toho použijte výše uvedené příkazy CLI na hostiteli.

Restartujte bránu, aby načetla novou konfiguraci kanálu:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ve výstupu brány by se během několika sekund mělo zobrazit `logged in to discord as <bot-name>`.

#### Párování vašeho účtu Discord

Pošlete botovi přímou zprávu v Discordu. Bot odpoví krátkým párovacím kódem.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schvalte jej na počítači, kde běží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Párovací kódy vyprší po jedné hodině.

Nyní můžete chatovat se svým agentem přímo z Discordu a přenášet úkoly na svůj lokální hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je pro většinu uživatelů jednodušší než Discord – nevyžaduje žádný server ani přístup správce.

#### Vytvoření Telegram bota

1. Otevřete Telegram a napište **@BotFather**.
2. Pošlete `/newbot` a postupujte podle pokynů. Uložte token bota, který vám poskytne.

#### Konfigurace OpenClaw pro Telegram

Uložte token jako proměnnou prostředí:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Přidejte konfiguraci kanálu do `~/.openclaw/openclaw.json` (nebo ji upravte přes dashboard):

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

Restartujte bránu, poté pošlete svému botovi libovolnou zprávu v Telegramu. Schvalte párování:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Párovací kódy vyprší po jedné hodině. Nyní můžete chatovat se svým agentem prostřednictvím přímých zpráv v Telegramu.

---

## Další kroky

Nyní, když váš agent může přijímat příkazy z vašeho telefonu a jednat na vašem lokálním počítači, stojí za to prozkoumat tři směry:

1. **Shrnutí akciového trhu**: Naplánujte OpenClaw tak, aby v pevných intervalech načítal data z finančních API, shrnoval pohyby dne pomocí vašeho lokálního modelu a každé ráno odesílal přehled na váš telefon prostřednictvím zvoleného kanálu.

2. **Monitor doladění**: Spusťte tréninkovou úlohu vzdáleně přes Telegram nebo Discord, poté nechte agenta sledovat tréninkový log a pravidelně hlásit hodnoty ztrát, využití GPU a místa na disku zpět na váš telefon. Pokud se běh zastaví nebo VRAM prudce vzroste, dozvíte se to okamžitě, aniž byste museli být u počítače.

3. **IoT s lokálním VLM**: Namiřte kameru na přední dveře, spusťte vizuální model na Lemonade a nechte OpenClaw analyzovat snímky na vyžádání nebo na základě spouštěče. Zeptejte se „přišly dnes nějaké balíčky?" ze svého telefonu a získejte přímou odpověď z vlastního hardwaru.