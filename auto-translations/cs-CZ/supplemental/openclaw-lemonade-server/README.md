<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Spuštění OpenClaw se serverem Lemonade Server jako backendem

## Přehled

[**OpenClaw**](https://openclaw.ai/) je autonomní AI agent, který dokáže psát a spouštět kód, spravovat soubory a řešit za vás komplexní vícekrokové úlohy. Na rozdíl od chatovacího asistenta, který pouze odpovídá na otázky, OpenClaw provádí ve vašem systému skutečné akce, což znamená, že potřebuje rychlý a schopný AI backend, který dokáže držet krok s náročnou smyčkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je právě tímto backendem. Jedná se o open-source lokální inferenční server, který spouští GenAI modely přímo na vašem hardwaru a zpřístupňuje je prostřednictvím standardního OpenAI API.

Společně tvoří plně lokální AI agentní zásobník: Lemonade se stará o inferenci modelu a OpenClaw poskytuje smyčku agenta, která přeměňuje výstupy modelu na skutečné akce.

> **Než budete pokračovat:** OpenClaw je vysoce autonomní AI agent. Poskytnutí přístupu k vašemu systému jakémukoli AI agentovi může vést k nepředvídatelným nebo nezamýšleným výsledkům. Pokračujte pouze v případě, že rozumíte rizikům a jste s tím, aby za vás jednal autonomní software, srozuměni.

---

## Co se naučíte

Na konci tohoto průvodce budete schopni:

- Seznámit se se **serverem Lemonade Server**
- **Nainstalovat OpenClaw** a **nasměrovat ho na Lemonade Server** jako svůj AI backend.
- **Spustit bránu OpenClaw** a potvrdit, že je váš agent připraven k práci.
- **Připojit komunikační kanál** (Discord nebo Telegram), abyste mohli s agentem chatovat z libovolného zařízení.

---

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @os:linux -->
- PC se systémem **Ubuntu 24.04+** nebo kompatibilní distribucí Linuxu založenou na Debianu s `apt-get`
- Alespoň **12 GB RAM** (u větších modelů doporučeno 64 GB+)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (volitelné, pro sandboxování OpenClaw)

- **~10–30 GB volného místa na disku** pro váhy modelu
<!-- @os:end -->
<!-- @os:windows -->
- PC se systémem **Windows 10/11**
- Alespoň **12 GB RAM** (u větších modelů doporučeno 64 GB+)
- **~10–30 GB volného místa na disku** pro váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (volitelné, pro sandboxování OpenClaw)
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

Doporučeným modelem pro tohoto průvodce je **Qwen3.6-35B-A3B-GGUF** od Unsloth, výkonný MoE model s kontextovým oknem o velikosti 263 000 tokenů, který je dobře vhodný pro agentní úlohy. Tento model používá kvantizaci UD-Q4_K_XL. Stáhněte si ho nyní:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Poté ho načtěte s velkým kontextovým oknem a toto nastavení uložte pro budoucí použití:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má výchozí délku kontextu 262 144 tokenů. Pokud narazíte na chyby způsobené nedostatkem paměti (OOM), zvažte zmenšení kontextového okna. Protože však Qwen3.6 využívá rozšířený kontext pro komplexní úlohy, doporučujeme zachovat délku kontextu alespoň 128K tokenů, aby byly zachovány schopnosti přemýšlení.

> **Tip: Vypnutí přemýšlení pro rychlejší odpovědi agenta:** Qwen3.6-35B-A3B ve výchozím nastavení běží v režimu přemýšlení, což před každou odpovědí přidává latenci. U agentních smyček se tato režie rychle nabaluje. Repozitář [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje předpřipravenou konfiguraci, která přemýšlení vypíná. Chcete-li ji použít, stáhněte soubor a naimportujte ho:
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

OpenClaw spouštíme uvnitř WSL (doporučeno) a propojujeme ho s Lemonade běžícím nativně ve Windows. Díky tomu získáte pro OpenClaw prostředí Linuxového shellu a přitom si zachováte GPU akceleraci Lemonade na straně Windows.

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

Spusťte toto v terminálu Ubuntu:

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

WSL2 běží ve virtuální síti. Lemonade ve Windows se váže na `127.0.0.1`, na kterou se WSL nemůže dostat přímo. Windows port proxy přesměruje provoz z brány WSL IP na localhost Windows.

**Zjištění IP adresy brány WSL** (spusťte uvnitř WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Přidání port proxy** (spusťte v PowerShellu jako správce, nahraďte `<WSL-Gateway-IP>` svou IP adresou brány WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Přidání pravidla brány firewall** (stejný PowerShell se zvýšenými oprávněními):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ověření z WSL**:

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

> Pravidlo `netsh portproxy` přežije restart, ale IP adresa brány WSL se může po `wsl --shutdown` změnit. Pokud se po restartu Lemonade z WSL stane nedostupným, zjistěte aktuální IP adresu brány a aktualizujte proxy touto novou IP adresou.

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

Příznak `--no-onboard` přeskočí interaktivního průvodce nastavením, backend modelu nakonfigurujete ručně v dalším kroku, což vám poskytuje přesnou kontrolu nad tím, který model a server se používá.

Otevřete nový terminál a potvrďte instalaci:

```bash
openclaw --version
```

> **Tip:** Pokud se po instalaci zobrazí `command not found`, přidejte globální bin adresář npm do PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby bylo toto nastavení trvalé, přidejte výše uvedený řádek do svého souboru `~/.bashrc` nebo `~/.zshrc`.

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
### Nastavení OpenClaw pro použití Lemonade

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

Tento příkaz zapíše konfiguraci OpenClaw do souboru `~/.openclaw/openclaw.json`.

> **Nastavení velikosti kontextového okna v OpenClaw:** Komprese (compaction) v OpenClaw se spustí, když `contextTokens > contextWindow − reserveTokens`. Výchozí hodnota `reserveTokensFloor` je 20 000 tokenů – jde o dolní hranici, která přepíše `reserveTokens`, pokud je nižší, takže jakýkoli kontext modelu pod ~37 tisíc tokenů způsobí nekonečnou smyčku komprese. Nastavte ve své konfiguraci nízkou rezervu a jednou vypněte tuto dolní hranici a bude platit pro všechny modely, bez nutnosti ladění pro jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *dolní hranice* (minimální ochrana), nikoli samotná rezerva – nastavení pouze této hranice nemá žádný účinek. `reserveTokensFloor: 0` tuto ochranu vypne, takže se přijme nižší hodnota `reserveTokens`.
>
> **Kdy toto použít:** Použijte tuto konfiguraci, pokud je efektivní velikost kontextového okna vašeho modelu nižší než ~37 tisíc tokenů, ať už proto, že je model malý (např. 8k, 16k, 32k), nebo proto, že jste kontext záměrně omezili na nižší hodnotu (např. načítáte model se 128k, ale v Lemonade nastavíte kontext na 16k). Bez tohoto nastavení OpenClaw při spuštění vstoupí do nekonečné smyčky komprese.

>
> **Modely s velkým kontextem při plné velikosti kontextu:** Toto můžete zcela přeskočit. Výchozí hodnoty fungují dobře, komprese se spustí ještě před zaplněním okna a model má dostatek prostoru pro generování dlouhých odpovědí. Pokud toto přesto použijete, mějte na paměti, že `reserveTokens: 4096` omezuje délku odpovědi na přibližně 4k tokenů, což může přerušit generování dlouhých souborů nebo podrobných plánů.
>
> **Kam toto přidat:** Umístěte blok `compaction` uvnitř `agents.defaults` ve svém souboru `openclaw.json` (obvykle na `~/.openclaw/openclaw.json`):
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
> Zbytek vaší konfigurace (gateway, kanály, modely atd.) zůstává beze změny, přidat je třeba pouze klíč `compaction`.

### (Doporučeno) Povolení sandboxingu pomocí Dockeru

OpenClaw může směrovat všechny operace agenta se soubory a kódem přes izolovaný kontejner Docker, místo aby je spouštěl přímo na vašem hostiteli. Tím se dopad jakékoli neúmyslné akce omezí pouze na sandbox a souborový systém i síť vašeho hostitele zůstanou nedotčeny.

Sestavte image sandboxu jednou (Docker musí být nainstalován):

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

Tímto přidáte klíč `sandbox` do stávajícího bloku `agents.defaults` v souboru `~/.openclaw/openclaw.json`:

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

Kontejnery sandboxu ve výchozím nastavení **nemají přístup k síti**. Podrobnosti o připojení svazků (bind mounts) a přepsání síťových nastavení najdete v [referenční dokumentaci k sandboxingu](https://docs.openclaw.ai/gateway/sandboxing).

> #### Řešení problémů: Docker – přístup odepřen
> 
> Pokud se vám při spouštění příkazů Dockeru zobrazí chyba „permission denied“:
> 
> **Krok 1: Přidejte svého uživatele do skupiny docker**
> 
> ```bash
> sudo groupadd docker                    # Vytvoří skupinu, pokud je třeba
> sudo usermod -aG docker $USER           # Přidá vás do skupiny
> newgrp docker                           # Aktivuje změnu
> docker run hello-world                  # Otestuje ji
> ```
> 
> **Krok 2: Pokud chyba přetrvává, použijte trvalé řešení**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Poté systém **restartujte**.
> 
> **Rychlé dočasné řešení** (po restartu se resetuje):
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

### Spuštění brány (Gateway) OpenClaw

Gateway je proces OpenClaw, který řídí smyčku agenta a poskytuje řídicí panel (dashboard):

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

Chcete-li otevřít řídicí panel, spusťte toto v druhém terminálu, zatímco gateway stále běží:

```bash
openclaw dashboard
```

Protože se gateway připojuje na loopback, řídicí panel se při otevření ze stejného počítače automaticky autentizuje – pro místní přístup není potřeba zadávat token ani schvalovat zařízení. Měli byste vidět řídicí panel OpenClaw s vaším modelem Lemonade uvedeným jako aktivní backend.

> Pokud jste povolili sandboxing, můžete jej ověřit tak, že agenta v řídicím panelu požádáte, aby spustil `run hostname`. Pokud se místo hostitelského názvu vašeho počítače zobrazí krátké ID kontejneru, sandbox funguje.

**Gratulujeme, právě jste od základu sestavili plně lokální zásobník AI agenta.**

> **Potřebujete token gateway?** Spusťte `openclaw dashboard --no-open`, čímž se vypíše URL adresa řídicího panelu s vloženým tokenem (příkaz se také pokusí token zkopírovat do schránky). Případně token najdete v `gateway.auth.token` v souboru `~/.openclaw/openclaw.json`.
>
> **Schválení vzdáleného zařízení:** Když otevřete řídicí panel z druhého počítače nebo telefonu, prohlížeč zobrazí ID požadavku. Zpět na počítači, na kterém běží gateway, spusťte:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je nutné pouze pro vzdálená nebo sekundární zařízení, přístup přes loopback ze stejného počítače se autentizuje automaticky.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Volitelné: Připojení komunikačního kanálu

Jakmile gateway běží, můžete ke svému lokálnímu agentovi přistupovat z jakéhokoli zařízení. Vyberte možnost, která odpovídá vašemu nastavení. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a další kanály, úplný seznam najdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord vyžaduje server, na kterém **máte administrátorský přístup**, abyste mohli přidat bota. Pokud sdílíte servery, ale žádný nevlastníte, použijte místo toho možnost B (Telegram).
#### Vytvořte si účet a server na Discordu

Pokud nemáte účet na Discordu, zaregistrujte se na [discord.com](https://discord.com). Budete také potřebovat server, na kterém jste administrátorem – vytvořte ho kliknutím na ikonu **+** v postranním panelu Discordu a výběrem možnosti **Create My Own**. Postačí soukromý server.

#### Vytvořte aplikaci a bota na Discordu

1. Přejděte na [Discord Developer Portal](https://discord.com/developers/applications) a klikněte na **New Application**. Zadejte název (např. „openclaw-bot“).
2. V postranním panelu klikněte na **Bot**. Nastavte uživatelské jméno bota.
3. Na stránce Bot přejděte dolů na **Privileged Gateway Intents** a povolte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (doporučené)
4. Přejděte zpět nahoru a klikněte na **Reset Token**, čímž vygenerujete token bota. Zkopírujte si ho.

#### Přidejte bota na svůj server

1. V postranním panelu klikněte na **OAuth2/ URL Generator**.
2. V sekci **Scopes** povolte `bot` a `applications.commands`.
3. V sekci **Bot Permissions** povolte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Zkopírujte vygenerovanou adresu URL, vložte ji do prohlížeče, vyberte svůj server a potvrďte. Bot by se nyní měl objevit v seznamu členů vašeho serveru.

#### Získejte svá ID

Zapněte v Discordu vývojářský režim (**User Settings/ Advanced/ Developer Mode**) a poté:
- klikněte pravým tlačítkem na ikonu vašeho serveru: **Copy Server ID**
- klikněte pravým tlačítkem na svůj avatar: **Copy User ID**

#### Povolte soukromé zprávy od členů serveru

Klikněte pravým tlačítkem na ikonu serveru/ **Privacy Settings**/ zapněte přepínač **Direct Messages**. Tím bot získá možnost vám poslat soukromou zprávu, což je nutné pro krok párování.

#### Nakonfigurujte OpenClaw pro Discord

Uložte token bota jako proměnnou prostředí a poté vytvořte jeden patch soubor, který povolí Discord, odkáže na token a přidá váš server na seznam povolených. Nahraďte `<server_id>` a `<user_id>` ID získanými výše.

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

> **Nespoléhejte na to, že požádáte agenta, aby toto nakonfiguroval.** Když je zapnutý sandboxing, agent nemůže zevnitř sandboxu zapisovat do `~/.openclaw/openclaw.json` – místo toho použijte na hostitelském počítači výše uvedené příkazy CLI.

Restartujte gateway, aby se načetla nová konfigurace kanálu:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ve výstupu gateway byste během několika sekund měli vidět `logged in to discord as <bot-name>`.

#### Spárujte svůj účet na Discordu

Napište botovi soukromou zprávu na Discordu. Odpoví krátkým párovacím kódem.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schvalte ho na počítači, na kterém běží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnost párovacích kódů vyprší po jedné hodině.

Nyní si můžete s agentem povídat přímo z Discordu a přesouvat úlohy na svůj místní hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je pro většinu uživatelů jednodušší než Discord, nevyžaduje server ani administrátorský přístup.

#### Vytvořte bota na Telegramu

1. Otevřete Telegram a napište zprávu **@BotFather**.
2. Odešlete `/newbot` a postupujte podle pokynů. Uložte si token bota, který dostanete.

#### Nakonfigurujte OpenClaw pro Telegram

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

Restartujte gateway a poté pošlete svému botovi jakoukoli zprávu na Telegramu. Schvalte párování:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnost párovacích kódů vyprší po jedné hodině. Nyní si můžete s agentem povídat prostřednictvím soukromých zpráv na Telegramu.

---

## Další kroky

Nyní, když váš agent dokáže přijímat příkazy z vašeho telefonu a jednat na vašem místním počítači, zde jsou tři směry, které stojí za prozkoumání:

1. **Sumarizátor akciového trhu**: Naplánujte, aby OpenClaw v pravidelném intervalu stahoval data z finančních API, shrnul denní pohyby pomocí vašeho lokálního modelu a každé ráno posílal souhrn na váš telefon přes vámi zvolený kanál.

2. **Monitor doladění (fine-tuning)**: Spusťte vzdáleně trénovací úlohu přes Telegram nebo Discord a nechte agenta sledovat trénovací log a periodicky hlásit hodnoty loss, využití GPU a stav disku zpět na váš telefon. Pokud se běh zasekne nebo dojde ke skoku ve využití VRAM, dozvíte se to okamžitě, aniž byste museli být u počítače.

3. **IOT s lokálním VLM**: Namiřte kameru na vaše vchodové dveře, spusťte model pro počítačové vidění na Lemonade a nechte OpenClaw analyzovat snímky na vyžádání nebo na základě spouštěče. Zeptejte se ze svého telefonu „přišly dnes nějaké balíky?“ a dostanete jasnou odpověď přímo z vlastního hardwaru.