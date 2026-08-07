<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Spuštění OpenClaw s Lemonade Server jako backendem

## Přehled

[**OpenClaw**](https://openclaw.ai/) je autonomní AI agent, který dokáže psát a spouštět kód, spravovat soubory a vykonávat za vás komplexní vícekrokové úkoly. Na rozdíl od chatovacího asistenta, který pouze odpovídá na dotazy, OpenClaw provádí na vašem systému skutečné akce, což znamená, že potřebuje rychlý a schopný AI backend, který dokáže držet krok s náročnou smyčkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je právě takovým backendem. Jedná se o open-source lokální inferenční server, který spouští GenAI modely přímo na vašem hardwaru a zpřístupňuje je prostřednictvím standardního OpenAI API.

Společně tvoří plně lokální AI agentní zásobník: Lemonade se stará o inferenci modelu a OpenClaw poskytuje agentní smyčku, která proměňuje výstupy modelu ve skutečné akce.

> **Než budete pokračovat:** OpenClaw je vysoce autonomní AI agent. Poskytnutí přístupu k vašemu systému jakémukoli AI agentovi může vést k nepředvídatelným nebo nezamýšleným výsledkům. Pokračujte pouze v případě, že rozumíte rizikům a jste smířeni s tím, že autonomní software bude jednat vaším jménem.

---

## Co se naučíte

Na konci tohoto playbooku budete schopni:

- Seznámit se s **Lemonade Server**
- **Nainstalovat OpenClaw** a **nasměrovat jej na Lemonade Server** jako svůj AI backend.
- **Spustit gateway OpenClaw** a ověřit, že je váš agent připraven k práci.
- **Připojit komunikační kanál** (Discord nebo Telegram), abyste mohli s agentem komunikovat z libovolného zařízení.

---

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových požadavků

<!-- @os:linux -->
- Počítač se systémem **Ubuntu 24.04+** nebo kompatibilní distribucí Linuxu založenou na Debianu s nástrojem `apt-get`
- Alespoň **12 GB RAM** (u větších modelů se doporučuje 64 GB+)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (volitelné, pro sandboxování OpenClaw)
- **~10–30 GB volného místa na disku** pro váhy modelu
<!-- @os:end -->

<!-- @os:windows -->
- Počítač se systémem **Windows 10/11**
- Alespoň **12 GB RAM** (u větších modelů se doporučuje 64 GB+)
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

Doporučeným modelem pro tento playbook je **Qwen3.6-35B-A3B-GGUF** od Unsloth, výkonný MoE model s kontextovým oknem 263k tokenů, který se dobře hodí pro agentní úlohy. Tento model používá kvantizaci UD-Q4_K_XL. Nyní jej stáhněte:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Poté jej načtěte s velkým kontextovým oknem a toto nastavení uložte pro budoucí spuštění:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má výchozí délku kontextu 262 144 tokenů. Pokud narazíte na chyby způsobené nedostatkem paměti (OOM), zvažte zmenšení kontextového okna. Protože však Qwen3.6 využívá rozšířený kontext pro složité úlohy, doporučujeme zachovat délku kontextu alespoň 128 K tokenů, aby byly zachovány schopnosti „přemýšlení“.

> **Tip: Vypněte režim přemýšlení pro rychlejší odpovědi agenta:** Qwen3.6-35B-A3B ve výchozím nastavení běží v režimu přemýšlení, což přidává latenci před každou odpovědí. U agentních smyček se tato režie rychle kumuluje. Repozitář [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje připravenou konfiguraci, která režim přemýšlení vypíná. Chcete-li ji použít, stáhněte soubor a naimportujte jej:
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

OpenClaw spouštíme uvnitř WSL (doporučeno) a připojujeme jej k Lemonade, který běží nativně na Windows. Díky tomu získáte pro OpenClaw prostředí linuxového shellu, přičemž GPU akcelerace Lemonade zůstává na straně Windows.

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

Ukončete WSL a restartujte jej:

```powershell
exit
wsl --shutdown
wsl
```

### Propojení Lemonade z Windows do WSL

WSL2 běží ve virtuální síti. Lemonade na Windows se váže na `127.0.0.1`, což WSL nemůže přímo dosáhnout. Windows port proxy přeposílá provoz z gateway IP adresy WSL na localhost systému Windows.

**Zjištění gateway IP adresy WSL** (spusťte uvnitř WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Přidání port proxy** (spusťte v PowerShellu jako správce, přičemž `<WSL-Gateway-IP>` nahraďte gateway IP adresou vašeho WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Poznámka: Pokud narazíte na chybu `netsh: command not found`, zkuste místo toho použít explicitní název spustitelného souboru – `netsh.exe`

**Přidání pravidla brány firewall** (stejný elevovaný PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ověření z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Pokud jste v předchozím kroku již načetli model Qwen3.6-35B-A3B-GGUF, měli byste vidět JSON výstup podobný tomuto:

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

#### Udržení mostu funkčního po restartu

Pravidlo `netsh portproxy` přežije restart, ale IP adresa brány WSL se může po `wsl --shutdown` nebo restartu změnit. Když k tomu dojde, proxy stále ukazuje na starou IP adresu a Lemonade se stane z WSL nedostupným. Pokud se to stane, použijte jednu z níže uvedených možností.

**Možnost 1 (doporučeno) — Automatická oprava mostu.** Abyste to nemuseli dělat ručně pokaždé, použijte naplánovanou úlohu, která zkontroluje most při každém spuštění a přihlášení a přestaví ho pouze tehdy, když se IP adresa brány změnila. Viz [průvodce automatickou opravou mostu Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Možnost 2 — Manuální oprava mostu.** Nejprve zjistěte aktuální IP adresu brány WSL spuštěním tohoto uvnitř WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Zkopírujte tuto hodnotu; použijete ji místo `<new-WSL-Gateway-IP>` níže.

Poté v **PowerShellu se zvýšenými oprávněními** (spusťte jako správce) vypište existující pravidla, smažte pouze zastaralé pravidlo Lemonade a přidejte nové s aktuální IP adresou:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Ve výstupu `show all` je zastaralé pravidlo Lemonade ten záznam, jehož adresa připojení (connect address) je `127.0.0.1` na portu `13305`; jeho adresa naslouchání (listen address) je vaše `<old-WSL-Gateway-IP>`. Smazáním podle této adresy odstraníte pouze toto pravidlo a ostatní pravidla port-proxy na vašem počítači zůstanou nedotčena.

Pravidlo brány firewall, které jste přidali během nastavení, je vázáno na port `13305` (nikoli na IP adresu), takže funguje i nadále a není třeba ho znovu vytvářet.

> **Doporučení:** Abyste se vyhnuli problémům s bránou, důrazně doporučujeme následující konfiguraci shellu:
> - **Příkazy Windows** by měly být spouštěny v **PowerShellu**
> - **Příkazy distribuce WSL** by měly být spouštěny v **příkazovém řádku** (spuštěném jako **správce**)

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
> Příkazy v této části spouštějte uvnitř vašeho **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Příznak `--no-onboard` přeskočí interaktivního průvodce nastavením, backend modelu nakonfigurujete ručně v dalším kroku, což vám dává přesnou kontrolu nad tím, který model a server se používají.

Otevřete nový terminál a potvrďte instalaci:

```bash
openclaw --version
```

> **Tip:** Pokud se po instalaci zobrazí `command not found`, přidejte globální bin adresář npm do vaší proměnné PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby to bylo trvalé, přidejte výše uvedený řádek do souboru `~/.bashrc` nebo `~/.zshrc`.

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

Spusťte neinteraktivní úvodní nastavení (onboarding) OpenClaw.
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

> **Velikost kontextového okna OpenClaw:** Komprimace (compaction) OpenClaw se spustí, když `contextTokens > contextWindow − reserveTokens`. Výchozí hodnota `reserveTokensFloor` je 20 000 tokenů, což je spodní hranice, která přepíše `reserveTokens`, pokud je nižší, takže jakýkoli kontext modelu pod ~37k spustí nekonečnou smyčku komprimace. Nastavte nízkou rezervu a jednou vypněte spodní hranici ve vaší konfiguraci a bude se to vztahovat na každý model, není třeba žádné ladění pro jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodní hranice* (minimální pojistka), nikoli samotná rezerva, nastavení pouze spodní hranice nemá žádný účinek. `reserveTokensFloor: 0` vypne tuto pojistku, takže je akceptována nižší hodnota `reserveTokens`.
>
> **Kdy toto použít:** Tuto konfiguraci použijte, pokud je efektivní velikost kontextového okna vašeho modelu pod ~37k, buď proto, že je model malý (např. 8k, 16k, 32k), nebo protože jste jej záměrně omezili na nižší hodnotu (např. načítáte model se 128k, ale v Lemonade nastavíte kontext na 16k). Bez toho vstoupí OpenClaw při spuštění do nekonečné smyčky komprimace.
>
> **Modely s velkým kontextem při plném kontextu:** Toto můžete zcela přeskočit. Výchozí hodnoty fungují dobře, komprimace se spustí ještě předtím, než se okno zaplní, a model má dostatek prostoru pro generování dlouhých odpovědí. Pokud toto přesto použijete, mějte na paměti, že `reserveTokens: 4096` omezuje délku odpovědi na ~4k tokenů, což může useknout generování dlouhých souborů nebo podrobných plánů.
>
> **Kam toto přidat:** Umístěte blok `compaction` uvnitř `agents.defaults` ve vašem souboru `openclaw.json` (obvykle na `~/.openclaw/openclaw.json`):
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
> Zbytek vaší konfigurace (gateway, kanály, modely atd.) zůstává beze změny, je třeba přidat pouze klíč `compaction`.
### (Doporučeno) Povolení sandboxingu v Dockeru

OpenClaw dokáže směrovat všechny operace agenta se soubory a kódem přes izolovaný kontejner Docker, místo aby je spouštěl přímo na vašem hostiteli. Tím se dopad jakékoli nezamýšlené akce omezí na sandbox a souborový systém a síť vašeho hostitele zůstanou nedotčené.

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

Spuštěním tohoto příkazu přidáte klíč `sandbox` uvnitř existujícího bloku `agents.defaults` v souboru `~/.openclaw/openclaw.json`:

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

Kontejnery sandboxu ve výchozím nastavení **nemají přístup k síti**. Podrobnosti o bind mounts a přepsání síťového nastavení naleznete v [referenci k sandboxingu](https://docs.openclaw.ai/gateway/sandboxing).

> #### Řešení problémů: Docker – přístup odepřen
> 
> Pokud se při spouštění příkazů Docker zobrazí chyba „permission denied“:
> 
> **Krok 1: Přidejte svého uživatele do skupiny docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Krok 2: Pokud chyba přetrvává, použijte trvalé řešení**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Poté **restartujte** systém.
> 
> **Rychlé dočasné řešení** (po restartu se vrátí do původního stavu):
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
## (Doporučeno) Integrace OpenClaw se službami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) poskytuje samostatně hostovanou službu pro procházení webu a extrakci obsahu, která dokáže obejít tyto překážky a odemknout plný potenciál automatizace OpenClaw. 

V tomto nastavení OpenClaw běží jako sada kontejnerů Docker spravovaných pomocí Podman. Pro zjednodušení správy životního cyklu a automatického spouštění registrujeme Firecrawl jako uživatelskou službu `systemd`, která orchestruje podkladový zásobník Podman Compose. To umožňuje OpenClaw spustit gateway, zastavit ho a ověřit službu Firecrawl pomocí standardních příkazů `systemctl --user` namísto přímé interakce s kontejnery. 

Pro zachování jednoduchosti jsme celý postup rozdělili do čtyř kroků:

---

### 1. Registrace systémové služby
Přejděte do konfiguračního adresáře uživatele systemd:
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
V tomto okamžiku byla služba definována, ale ještě nebyla zaregistrována v `systemd`. 
Ujistěte se, že název souboru přesně odpovídá tomu, který jste vytvořili výše, a poté spusťte:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Pokud je vše úspěšné, měli byste vidět následující výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby, které jsou nakonfigurovány ke spouštění automaticky.

### 2. Konfigurace Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideální pro ty, kteří potřebují plnou kontrolu nad svým prostředím pro scraping a zpracování dat, ale je spojen s dodatečnou náročností na údržbu a konfiguraci.

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
# FIRECRAWL_API_KEY="" # optional
```
### 3. Nasazení OpenClaw pomocí Podman Compose

Než budete pokračovat, ujistěte se, že jste stáhli nejnovější image OpenClaw Docker:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Jakmile je to hotovo, stáhněte soubor OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) a umístěte ho do kořenového adresáře `/firecrawl`:

> Tato konvence je vyžadována, aby `systemd` mohl lokalizovat a správně spustit službu podle specifikace `WorkingDirectory=${HOME}/firecrawl`.

> Zásobník můžete kdykoli rozšířit přidáním dalších služeb Firecrawl podle potřeby. Úplný seznam dostupných služeb naleznete v oficiálním souboru [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spuštění služby OpenClaw prostřednictvím Firecrawl 

Než předáte kontrolu systému `systemd`, ověřte, že vše funguje správně, ručním spuštěním zásobníku:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Pokud je vše nakonfigurováno správně, měli byste vidět, že kontejner OpenClaw naběhl, a výstup příkazové řádky by měl vypadat podobně takto:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po ověření zásobník opět vypněte, než budete pokračovat:
```bash
podman compose -f openclaw-compose.yaml down
```
Před spuštěním služby musíte zajistit, že adresář `firecrawl` a jeho soubor `.env` mají nastavená správná vlastnictví a oprávnění. 
To je nezbytné, aby služba mohla při spuštění zapsat vaše přihlašovací údaje.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nyní, když je vše ověřeno, spusťte službu prostřednictvím `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akce OpenClaw](https://docs.openclaw.ai/) jsou dostupné z interaktivního kontejneru a webový dashboard je k dispozici na stejném hostiteli a portu na adrese http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Získání vašeho `OPENCLAW_GATEWAY_TOKEN`

Jakmile je služba spuštěna a funkční, všimnete si nového adresáře `.openclaw`, který byl vytvořen ve vaší domovské složce (~/.openclaw). Tento adresář je ve výchozím nastavení uzamčen, takže jej budete muset odemknout, abyste získali svůj gateway token.

1. Udělte přístup k adresáři:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Přečtěte si svůj gateway token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Vyhledejte hodnotu `OPENCLAW_GATEWAY_TOKEN` ve výstupu.

3. Otevřete gateway dashboard ve svém prohlížeči na adrese http://127.0.0.1:18789. Vložte svůj token, až budete vyzváni k ověření.

Chcete-li službu zastavit, spusťte:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Spuštění OpenClaw Gateway

Gateway je proces OpenClaw, který spravuje smyčku agenta a obsluhuje dashboard:

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

Chcete-li otevřít dashboard, spusťte tento příkaz v druhém terminálu, zatímco gateway stále běží:

```bash
openclaw dashboard
```

Protože se gateway váže na loopback, dashboard se při otevření ze stejného počítače automaticky autentizuje, pro místní přístup není potřeba zadávat token ani schvalovat zařízení. Měli byste vidět dashboard OpenClaw s vaším modelem Lemonade uvedeným jako aktivní backend.

> Pokud jste povolili sandboxing, můžete jej ověřit tak, že požádáte agenta, aby z dashboardu spustil `run hostname`. Pokud se místo hostname vašeho počítače zobrazí krátké ID kontejneru, sandbox funguje správně.

**Gratulujeme, sestavili jste plně lokální AI agentní stack od základu.**

> **Potřebujete token gateway?** Spusťte `openclaw dashboard --no-open`, čímž se vypíše URL adresa dashboardu s vloženým tokenem (příkaz se také pokusí token zkopírovat do schránky). Alternativně je token uložen v `gateway.auth.token` v souboru `~/.openclaw/openclaw.json`.

**Přístup k dashboardu z jiného zařízení (přes SSH tunel)**

Pokud OpenClaw běží na vzdáleném počítači, můžete se k jeho dashboardu dostat z místního počítače prostřednictvím SSH tunelu. Tunel přeposílá port gateway (`18789`), takže váš místní prohlížeč může komunikovat se vzdálenou gateway přes `127.0.0.1`.

1. Ze svého **místního počítače** se jednou připojte ke vzdálenému počítači a přijměte výzvu s otiskem klíče, aby byl hostitel přidán mezi vaše známé hostitele:

   ```bash
   ssh user@<host-ip>
   ```

2. Stále na svém **místním počítači** otevřete SSH tunel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Poznámka:** Po zadání hesla terminál nezobrazí žádný výstup a bude vypadat, že „visí“. To je očekávané chování: příznak `-N` říká SSH, aby nespouštěl žádný vzdálený příkaz, takže pouze udržuje tunel otevřený. Ponechte tento terminál běžet.

3. Na svém **místním počítači** otevřete prohlížeč a přejděte na `http://127.0.0.1:18789`.

4. Na **vzdáleném počítači** vypište token gateway a vložte jej do prohlížeče pro přihlášení:

   ```bash
   openclaw dashboard --no-open
   ```

   Tím se vypíše URL adresa dashboardu s vloženým tokenem; zkopírujte token pro přihlášení. (Token je také uložen v `gateway.auth.token` v souboru `~/.openclaw/openclaw.json`.)

> **Schválení vzdáleného zařízení:** Když otevřete dashboard z jiného počítače nebo telefonu, prohlížeč může zobrazit ID požadavku. Na **vzdáleném počítači** vypište čekající požadavky:
> ```bash
> openclaw devices list
> ```
> Poté schvalte odpovídající požadavek:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potřeba pouze pro vzdálená nebo sekundární zařízení; přístup přes loopback ze stejného počítače se autentizuje automaticky. Podrobnosti naleznete v dokumentaci [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Volitelné: Připojení komunikačního kanálu

Jakmile gateway běží, můžete se ke svému místnímu agentovi dostat z libovolného zařízení. Vyberte možnost, která vyhovuje vašemu nastavení. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a další kanály, kompletní seznam naleznete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord vyžaduje server, na kterém **máte oprávnění administrátora** pro přidání bota. Pokud sdílíte servery, ale žádný nevlastníte, použijte místo toho Možnost B (Telegram).

#### Vytvoření účtu a serveru na Discordu

Pokud nemáte účet na Discordu, zaregistrujte se na [discord.com](https://discord.com). Budete také potřebovat server, na kterém jste administrátorem, vytvořte jej kliknutím na ikonu **+** v postranním panelu Discordu a výběrem **Create My Own**. Soukromý server je v pořádku.

#### Vytvoření aplikace a bota na Discordu

1. Přejděte do [Discord Developer Portal](https://discord.com/developers/applications) a klikněte na **New Application**. Zadejte mu název (např. „openclaw-bot“).
2. V postranním panelu klikněte na **Bot**. Nastavte uživatelské jméno bota.
3. Stále na stránce Bot přejděte dolů na **Privileged Gateway Intents** a povolte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (doporučeno)
4. Přejděte zpět nahoru a klikněte na **Reset Token** pro vygenerování tokenu vašeho bota. Zkopírujte jej.

#### Přidání bota na váš server

1. V postranním panelu klikněte na **OAuth2/ URL Generator**.
2. V sekci **Scopes** povolte `bot` a `applications.commands`.
3. V sekci **Bot Permissions** povolte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Zkopírujte vygenerovanou URL adresu, vložte ji do prohlížeče, vyberte svůj server a potvrďte. Bot by se nyní měl objevit v seznamu členů vašeho serveru.

#### Získání vašich ID

Povolte Developer Mode na Discordu (**User Settings/ Advanced/ Developer Mode**), poté:
- Klikněte pravým tlačítkem na ikonu vašeho serveru: **Copy Server ID**
- Klikněte pravým tlačítkem na svůj avatar: **Copy User ID**

#### Povolení DM od členů serveru

Klikněte pravým tlačítkem na ikonu vašeho serveru/ **Privacy Settings**/ přepněte **Direct Messages**. Tím umožníte botovi posílat vám DM, což je vyžadováno pro krok párování.

#### Konfigurace OpenClaw pro Discord

Uložte token vašeho bota jako proměnnou prostředí, poté vytvořte jeden patch soubor, který povolí Discord, odkáže se na token a povolí (allowlist) váš server. Nahraďte `<server_id>` a `<user_id>` ID získanými výše.

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

> **Nespoléhejte na to, že požádáte agenta o konfiguraci tohoto nastavení.** Pokud je povolen sandboxing, agent nemůže zapisovat do `~/.openclaw/openclaw.json` zevnitř sandboxu, místo toho použijte na hostiteli výše uvedené CLI příkazy.

Restartujte gateway, aby se projevila nová konfigurace kanálu:

```bash
openclaw gateway run --bind loopback --port 18789
```

V rámci několika sekund byste ve výstupu gateway měli vidět `logged in to discord as <bot-name>`.
#### Spárujte svůj účet Discord

Napište botovi zprávu (DM) na Discordu. Odpoví krátkým párovacím kódem.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schvalte jej na počítači, na kterém běží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnost párovacích kódů vyprší po jedné hodině.

Nyní můžete komunikovat se svým agentem přímo z Discordu a přesouvat úlohy na svůj lokální hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je pro většinu uživatelů jednodušší než Discord, nevyžaduje žádný server ani přístup administrátora.

#### Vytvoření bota pro Telegram

1. Otevřete Telegram a napište zprávu **@BotFather**.
2. Odešlete `/newbot` a postupujte podle pokynů. Uložte si token bota, který obdržíte.

#### Konfigurace OpenClaw pro Telegram

Uložte token jako proměnnou prostředí:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Přidejte konfiguraci kanálu do `~/.openclaw/openclaw.json` (nebo ji upravte prostřednictvím řídicího panelu):

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

Restartujte bránu (gateway) a poté pošlete svému botovi jakoukoli zprávu na Telegramu. Schvalte spárování:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnost párovacích kódů vyprší po jedné hodině. Nyní můžete komunikovat se svým agentem prostřednictvím zpráv (DM) na Telegramu.

---

## Další kroky

Nyní, když váš agent dokáže přijímat příkazy z vašeho telefonu a jednat na vašem lokálním počítači, zde jsou tři směry, které stojí za prozkoumání:

1. **Souhrny akciového trhu**: Naplánujte, aby OpenClaw v pravidelných intervalech stahoval data z finančních API, shrnul dnešní vývoj pomocí vašeho lokálního modelu a každé ráno odeslal souhrn do vašeho telefonu prostřednictvím zvoleného kanálu.

2. **Sledování doladění (fine-tuningu)**: Spusťte trénovací úlohu vzdáleně přes Telegram nebo Discord a nechte agenta sledovat trénovací log a pravidelně hlásit hodnoty ztráty (loss), vytížení GPU a využití disku zpět do vašeho telefonu. Pokud se běh zasekne nebo dojde ke skokovému nárůstu VRAM, dozvíte se to okamžitě, aniž byste museli být u počítače.

3. **IOT s lokálním VLM**: Namiřte kameru na vaše vchodové dveře, spusťte model pro rozpoznávání obrazu na Lemonade a nechte OpenClaw analyzovat snímky na vyžádání nebo na základě spouštěče. Zeptejte se ze svého telefonu „Přišly dnes nějaké balíky?" a dostanete přímou odpověď od vlastního hardwaru.

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