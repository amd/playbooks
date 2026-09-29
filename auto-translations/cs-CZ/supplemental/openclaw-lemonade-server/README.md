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

[**OpenClaw**](https://openclaw.ai/) je autonomní AI agent, který dokáže psát a spouštět kód, spravovat soubory a procházet komplexními vícekrokovými úlohami vaším jménem. Na rozdíl od chatovacího asistenta, který pouze odpovídá na otázky, OpenClaw provádí skutečné akce ve vašem systému, což znamená, že potřebuje rychlý, výkonný AI backend, který dokáže držet krok s náročnou smyčkou agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je tímto backendem. Jedná se o open-source lokální inferenční server, který spouští GenAI modely přímo na vašem hardwaru a zpřístupňuje je prostřednictvím standardního OpenAI API.

Společně tvoří plně lokální zásobník pro AI agenty: Lemonade se stará o inferenci modelu a OpenClaw poskytuje smyčku agenta, která proměňuje výstupy modelu ve skutečné akce.

> **Než budete pokračovat:** OpenClaw je vysoce autonomní AI agent. Udělení přístupu k vašemu systému jakémukoli AI agentovi může vést k nepředvídatelným nebo nezamýšleným výsledkům. Pokračujte pouze tehdy, pokud rizikům rozumíte a jste smíření s tím, že autonomní software bude jednat vaším jménem.

---

## Co se naučíte

Na konci tohoto průvodce budete schopni:

- Seznámit se s **Lemonade Server**
- **Nainstalovat OpenClaw** a **nasměrovat jej na Lemonade Server** jako svůj AI backend.
- **Spustit bránu OpenClaw** a ověřit, že je váš agent připraven k práci.
- **Připojit komunikační kanál** (Discord nebo Telegram), abyste mohli se svým agentem komunikovat z libovolného zařízení.

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
- PC se systémem **Ubuntu 24.04+** nebo kompatibilní distribucí Linuxu založenou na Debianu s `apt-get`
- Alespoň **12 GB RAM** (u větších modelů se doporučuje 64 GB+)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (volitelné, pro izolování OpenClaw v sandboxu)
- **přibližně 10–30 GB volného místa na disku** pro váhy modelu
<!-- @os:end -->

<!-- @os:windows -->
- PC se systémem **Windows 10/11**
- Alespoň **12 GB RAM** (u větších modelů se doporučuje 64 GB+)
- **přibližně 10–30 GB volného místa na disku** pro váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (volitelné, pro izolování OpenClaw v sandboxu)
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

Doporučeným modelem pro tohoto průvodce je **Qwen3.6-35B-A3B-GGUF** od Unsloth, výkonný MoE model s kontextovým oknem o velikosti 263 tisíc tokenů, který je velmi vhodný pro úlohy agentů. Tento model používá kvantizaci UD-Q4_K_XL. Stáhněte jej nyní:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Poté jej načtěte s velkým kontextovým oknem a toto nastavení uložte pro budoucí spouštění:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má výchozí délku kontextu 262 144 tokenů. Pokud narazíte na chyby způsobené nedostatkem paměti (OOM), zvažte snížení velikosti kontextového okna. Protože však Qwen3.6 využívá rozšířený kontext pro složité úlohy, doporučujeme zachovat délku kontextu alespoň 128 K tokenů, aby byly zachovány schopnosti „přemýšlení“.

> **Tip: Vypněte „přemýšlení“ pro rychlejší odpovědi agenta:** Qwen3.6-35B-A3B ve výchozím nastavení běží v režimu přemýšlení, což před každou odpovědí přidává latenci. U smyček agenta se tato režie rychle nabaluje. Repozitář [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje připravenou konfiguraci, která přemýšlení vypíná. Chcete-li ji použít, stáhněte soubor a importujte jej:
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

### Povolení systemd v WSL

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

### Přemostění Lemonade z Windows do WSL

WSL2 běží ve virtuální síti. Lemonade na Windows se váže na `127.0.0.1`, kam WSL nemá přímý přístup. Windows port proxy přeposílá provoz z gateway IP adresy WSL na Windows localhost.

**Zjistěte gateway IP adresu WSL** (spusťte uvnitř WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Přidejte port proxy** (spusťte v PowerShellu jako správce, nahraďte `<WSL-Gateway-IP>` vaší gateway IP adresou WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Poznámka: Pokud narazíte na chybu `netsh: command not found`, zkuste místo toho použít explicitní název spustitelného souboru – `netsh.exe`

**Přidejte pravidlo brány firewall** (stejný PowerShell se zvýšenými oprávněními):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ověřte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Pokud jste v předchozím kroku již načetli model Qwen3.6-35B-A3B-GGUF, měli byste vidět výstup ve formátu JSON podobný tomuto:

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

Pravidlo `netsh portproxy` přežije restart, ale IP adresa brány WSL se může po `wsl --shutdown` nebo restartu změnit. Když k tomu dojde, proxy stále ukazuje na starou IP adresu a Lemonade se z WSL stane nedostupným. Pokud k tomu dojde, použijte jednu z níže uvedených možností.

**Možnost 1 (doporučeno) — Automatická oprava mostu.** Abyste to nemuseli dělat ručně pokaždé, použijte naplánovanou úlohu, která kontroluje most při každém spuštění a přihlášení a znovu jej sestaví pouze v případě, že se IP adresa brány změnila. Viz [průvodce automatickou opravou mostu Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Možnost 2 — Ruční oprava mostu.** Nejprve zjistěte aktuální IP adresu brány WSL spuštěním následujícího příkazu uvnitř WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Zkopírujte si tuto hodnotu; použijete ji místo `<new-WSL-Gateway-IP>` níže.

Poté v **PowerShellu se zvýšenými oprávněními** (Spustit jako správce) vypište existující pravidla, odstraňte pouze zastaralé pravidlo Lemonade a přidejte nové s aktuální IP adresou:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Ve výstupu `show all` je zastaralé pravidlo Lemonade záznam, jehož připojovací adresa je `127.0.0.1` na portu `13305`; jeho naslouchací adresa je vaše `<old-WSL-Gateway-IP>`. Odstraněním podle této adresy odstraníte pouze toto pravidlo a ostatní pravidla port-proxy na vašem počítači zůstanou nedotčena.

Pravidlo brány firewall, které jste přidali při nastavení, je vázáno na port `13305` (nikoli na IP adresu), takže funguje i nadále a není potřeba jej znovu vytvářet.

> **Doporučení:** Abyste se vyhnuli problémům s bránou, důrazně doporučujeme následující konfiguraci shellu:
> - **Příkazy pro Windows** by měly být spouštěny v **PowerShellu**
> - **Příkazy pro distribuci WSL** by měly být spouštěny v **příkazovém řádku** (spuštěném jako **správce**)

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
> Příkazy v této sekci spouštějte uvnitř svého **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Příznak `--no-onboard` přeskočí interaktivního průvodce nastavením, model backend nakonfigurujete ručně v dalším kroku, což vám dává přesnou kontrolu nad tím, jaký model a server se používají.

Otevřete nový terminál a potvrďte instalaci:

```bash
openclaw --version
```

> **Tip:** Pokud se po instalaci zobrazí `command not found`, přidejte globální bin adresář npm do proměnné PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby byla tato změna trvalá, přidejte výše uvedený řádek do souboru `~/.bashrc` nebo `~/.zshrc`.

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

> **Velikost kontextového okna OpenClaw:** Komprimace OpenClaw se spustí, když `contextTokens > contextWindow − reserveTokens`. Výchozí hodnota `reserveTokensFloor` je 20 000 tokenů, což je spodní hranice, která přepíše `reserveTokens`, pokud je nižší, takže jakýkoli kontext modelu pod ~37 tisíc spustí nekonečnou smyčku komprimace. Nastavte nízkou rezervu a jednou v konfiguraci zakažte spodní hranici a bude platit pro každý model, bez nutnosti ladění pro jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodní hranice* (minimální pojistka), nikoli samotná rezerva, nastavení pouze spodní hranice nemá žádný účinek. `reserveTokensFloor: 0` zakáže pojistku, takže je přijata nižší hodnota `reserveTokens`.
>
> **Kdy toto použít:** Použijte tuto konfiguraci, pokud je efektivní kontextové okno vašeho modelu menší než ~37 tisíc, ať už proto, že je model malý (např. 8k, 16k, 32k), nebo protože jste jej záměrně omezili na nižší hodnotu (např. nahráváte 128k model, ale nastavíte kontext na 16k v Lemonade). Bez tohoto nastavení vstoupí OpenClaw při spuštění do nekonečné smyčky komprimace.
>
> **Modely s velkým kontextem při plném kontextu:** Toto můžete zcela přeskočit. Výchozí hodnoty fungují dobře, komprimace se spustí ještě dříve, než se okno zaplní, a model má dostatek prostoru pro generování dlouhých odpovědí. Pokud toto přesto použijete, mějte na paměti, že `reserveTokens: 4096` omezuje délku odpovědi na ~4k tokenů, což může způsobit useknutí generování dlouhého souboru nebo podrobných plánů.
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
> Zbytek vaší konfigurace (brána, kanály, modely atd.) zůstává beze změny, potřeba je přidat pouze klíč `compaction`.
### (Doporučeno) Povolte sandboxing pomocí Dockeru

OpenClaw dokáže směrovat veškeré souborové a kódové operace agenta přes izolovaný kontejner Docker namísto jejich přímého spouštění na vašem hostiteli. Tím se rozsah dopadu jakékoli nezamýšlené akce omezí pouze na sandbox, zatímco souborový systém a síť hostitele zůstanou nedotčeny.

Sestavte sandboxový image jednou (Docker musí být nainstalován):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Spusťte toto pro přidání klíče `sandbox` uvnitř stávajícího bloku `agents.defaults` v souboru `~/.openclaw/openclaw.json`:

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

Sandboxové kontejnery standardně **nemají přístup k síti**. Podrobnosti o bind mounts a přepsání síťových nastavení najdete v [referenční dokumentaci sandboxingu](https://docs.openclaw.ai/gateway/sandboxing).

> #### Řešení problémů: Docker Permission Denied
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
> Poté systém **restartujte**.
> 
> **Rychlé dočasné řešení** (po restartu se vrátí zpět):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) poskytuje samostatně hostovanou službu pro procházení webu a extrakci obsahu, která dokáže obejít tato omezení a odemknout plný potenciál automatizace OpenClaw.

V tomto nastavení běží OpenClaw jako sada kontejnerů Docker spravovaných pomocí Podman. Pro zjednodušení správy životního cyklu a automatického spouštění registrujeme Firecrawl jako uživatelskou službu `systemd`, která orchestruje podkladový zásobník Podman Compose. Díky tomu může OpenClaw spouštět gateway, zastavovat ho a ověřovat službu Firecrawl pomocí standardních příkazů `systemctl --user` namísto přímé interakce s kontejnery.

Pro zachování přehlednosti jsme celý proces rozdělili do čtyř kroků:

---

### 1. Registrace systémové služby
Přejděte do konfiguračního adresáře uživatelské instance systemd:
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
V tuto chvíli je služba definována, ale ještě není zaregistrována v `systemd`.
Ujistěte se, že název souboru přesně odpovídá tomu, který jste vytvořili výše, a poté spusťte:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Pokud vše proběhne úspěšně, měli byste vidět následující výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby, které jsou nakonfigurovány tak, aby se spouštěly automaticky.

### 2. Konfigurace Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideální pro ty, kteří potřebují plnou kontrolu nad svým prostředím pro scraping a zpracování dat, avšak s sebou nese kompromis v podobě dodatečné údržby a konfigurace.

Začněte naklonováním repozitáře:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Vytvořte soubor `.env` v adresáři `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Nasazení OpenClaw pomocí Podman Compose

Než budete pokračovat, ujistěte se, že jste stáhli nejnovější Docker image OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Jakmile to bude hotovo, stáhněte soubor Compose pro OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) a umístěte ho do kořenového adresáře `/firecrawl`:

> Tato konvence je nutná, aby `systemd` mohl podle nastavení `WorkingDirectory=${HOME}/firecrawl` správně vyhledat a spustit službu.

> Zásobník můžete kdykoli rozšířit o další služby Firecrawl podle potřeby. Úplný seznam dostupných služeb najdete v oficiálním souboru [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spuštění služby OpenClaw přes Firecrawl

Než předáte řízení systému `systemd`, ověřte, že vše funguje správně, ručním spuštěním zásobníku:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Pokud je vše správně nakonfigurováno, měli byste vidět, jak se spouští kontejner OpenClaw, a výstup příkazové řádky by měl vypadat podobně takto:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po ověření zásobník znovu ukončete, než budete pokračovat:
```bash
podman compose -f openclaw-compose.yaml down
```
Před spuštěním služby se musíte ujistit, že jsou na adresáři `firecrawl` a jeho souboru `.env` nastaveny správné vlastnictví a oprávnění.
To je nezbytné, aby služba mohla při spuštění zapsat vaše přihlašovací údaje.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nyní, když je vše ověřeno, spusťte službu přes `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akce OpenClaw](https://docs.openclaw.ai/) jsou dostupné zevnitř interaktivního kontejneru a webový dashboard je dostupný na stejném hostiteli a portu na adrese http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Získání vašeho tokenu `OPENCLAW_GATEWAY_TOKEN`

Jakmile je služba spuštěna a běží, všimnete si nového adresáře `.openclaw` vytvořeného ve vaší domovské složce (~/.openclaw). Tento adresář je standardně uzamčen, takže je třeba jej odemknout, abyste získali token gateway.

1. Udělte přístup k adresáři:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Přečtěte si svůj token gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Ve výstupu vyhledejte hodnotu `OPENCLAW_GATEWAY_TOKEN`.

3. Otevřete si dashboard gateway ve svém prohlížeči na adrese http://127.0.0.1:18789. Po zobrazení výzvy k ověření vložte svůj token.

Pro zastavení služby spusťte:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Spuštění brány OpenClaw (Gateway)

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

Chcete-li otevřít dashboard, spusťte toto ve druhém terminálu, zatímco gateway stále běží:

```bash
openclaw dashboard
```

Protože se gateway připojuje na loopback, dashboard se při otevření ze stejného počítače automaticky autentizuje, pro místní přístup není potřeba zadávat token ani schvalovat zařízení. Měli byste vidět dashboard OpenClaw s vaším modelem Lemonade uvedeným jako aktivní backend.

> Pokud jste povolili sandboxing, můžete jej ověřit tak, že požádáte agenta, aby z dashboardu spustil `run hostname`. Pokud místo hostname vašeho počítače uvidíte krátké ID kontejneru, sandbox funguje.

**Gratulujeme, vytvořili jste zcela lokální sadu AI agenta od základu.**

> **Potřebujete token gateway?** Spusťte `openclaw dashboard --no-open`, čímž se vypíše URL dashboardu se zabudovaným tokenem (také se pokusí zkopírovat jej do schránky). Alternativně je token uložen pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.

**Přístup k dashboardu z jiného zařízení (přes SSH tunel)**

Pokud OpenClaw běží na vzdáleném počítači, můžete se k jeho dashboardu dostat z místního počítače prostřednictvím SSH tunelu. Tunel přesměruje port gateway (`18789`), aby váš místní prohlížeč mohl komunikovat se vzdálenou gateway přes `127.0.0.1`.

1. Ze svého **místního počítače** se jednou připojte ke vzdálenému počítači a potvrďte výzvu k otisku (fingerprint), aby byl hostitel přidán do vašich known hosts:

   ```bash
   ssh user@<host-ip>
   ```

2. Stále na svém **místním počítači** otevřete SSH tunel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Poznámka:** Po zadání hesla terminál nezobrazí žádný výstup a zdá se, že „zamrzl“. To je očekávané chování: příznak `-N` říká SSH, aby nespouštěl žádný vzdálený příkaz, takže pouze udržuje tunel otevřený. Nechte tento terminál běžet.

3. Na svém **místním počítači** otevřete prohlížeč a přejděte na `http://127.0.0.1:18789`.

4. Na **vzdáleném počítači** vypište token gateway a vložte jej do prohlížeče pro přihlášení:

   ```bash
   openclaw dashboard --no-open
   ```

   Tím se vypíše URL dashboardu se zabudovaným tokenem; zkopírujte token pro přihlášení. (Token je také uložen pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.)

> **Schválení vzdáleného zařízení:** Když otevřete dashboard z jiného počítače nebo telefonu, prohlížeč může zobrazit ID požadavku. Na **vzdáleném počítači** vypište čekající požadavky:
> ```bash
> openclaw devices list
> ```
> Poté schvalte odpovídající požadavek:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potřeba pouze pro vzdálená nebo sekundární zařízení; přístup přes loopback ze stejného počítače se autentizuje automaticky. Podrobnosti najdete v dokumentaci [Vzdálený přístup](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Volitelné: Připojení komunikačního kanálu

Jakmile gateway běží, můžete se ke svému místnímu agentovi dostat z jakéhokoli zařízení. Vyberte možnost, která vyhovuje vašemu nastavení. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a další kanály, kompletní seznam najdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord vyžaduje server, na kterém **máte administrátorský přístup** pro přidání bota. Pokud sdílíte servery, ale žádný nevlastníte, použijte místo toho možnost B (Telegram).

#### Vytvoření účtu a serveru na Discordu

Pokud nemáte účet Discord, zaregistrujte se na [discord.com](https://discord.com). Také potřebujete server, na kterém jste administrátorem, vytvořte jej kliknutím na ikonu **+** v postranním panelu Discordu a výběrem **Create My Own**. Soukromý server je v pořádku.

#### Vytvoření aplikace a bota na Discordu

1. Přejděte na [Discord Developer Portal](https://discord.com/developers/applications) a klikněte na **New Application**. Zadejte název (např. „openclaw-bot“).
2. V postranním panelu klikněte na **Bot**. Nastavte uživatelské jméno bota.
3. Stále na stránce Bot přejděte dolů na **Privileged Gateway Intents** a povolte:
   - **Message Content Intent** (vyžadováno)
   - **Server Members Intent** (doporučeno)
4. Přejděte zpět nahoru a klikněte na **Reset Token** pro vygenerování tokenu bota. Zkopírujte jej.

#### Přidání bota na váš server

1. V postranním panelu klikněte na **OAuth2/ URL Generator**.
2. V sekci **Scopes** povolte `bot` a `applications.commands`.
3. V sekci **Bot Permissions** povolte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Zkopírujte vygenerovanou URL, vložte ji do prohlížeče, vyberte svůj server a potvrďte. Bot by se nyní měl objevit v seznamu členů vašeho serveru.

#### Získání vašich ID

Povolte Developer Mode v Discordu (**User Settings/ Advanced/ Developer Mode**), poté:
- Klikněte pravým tlačítkem na ikonu serveru: **Copy Server ID**
- Klikněte pravým tlačítkem na svůj avatar: **Copy User ID**

#### Povolení DM od členů serveru

Klikněte pravým tlačítkem na ikonu serveru/ **Privacy Settings**/ přepněte **Direct Messages**. Toto umožní botovi vám poslat DM, což je vyžadováno pro krok párování.

#### Konfigurace OpenClaw pro Discord

Uložte token svého bota jako proměnnou prostředí, poté vytvořte jeden patch soubor, který povolí Discord, odkazuje na token a přidá váš server na allowlist. Nahraďte `<server_id>` a `<user_id>` ID získanými výše.

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

> **Nespoléhejte na to, že požádáte agenta, aby toto nakonfiguroval.** Pokud je povolen sandboxing, agent nemůže zapisovat do `~/.openclaw/openclaw.json` zevnitř sandboxu, místo toho použijte výše uvedené příkazy CLI na hostiteli.

Restartujte gateway, aby se projevila nová konfigurace kanálu:

```bash
openclaw gateway run --bind loopback --port 18789
```

Během několika sekund byste měli ve výstupu gateway vidět `logged in to discord as <bot-name>`.
#### Spárujte svůj účet Discord

Pošlete botovi zprávu v Discordu. Odpoví krátkým párovacím kódem.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schvalte jej na počítači, na kterém běží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnost párovacích kódů vyprší po jedné hodině.

Nyní můžete komunikovat se svým agentem přímo z Discordu a přesouvat úkoly na svůj lokální hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je pro většinu uživatelů jednodušší než Discord, nevyžaduje žádný server ani přístup administrátora.

#### Vytvoření bota v Telegramu

1. Otevřete Telegram a napište zprávu **@BotFather**.
2. Odešlete `/newbot` a postupujte podle pokynů. Uložte si token bota, který obdržíte.

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

Restartujte gateway a poté pošlete svému botovi jakoukoli zprávu v Telegramu. Schvalte párování:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnost párovacích kódů vyprší po jedné hodině. Nyní můžete komunikovat se svým agentem přes soukromé zprávy v Telegramu.

---

## Další kroky

Nyní, když váš agent dokáže přijímat příkazy z vašeho telefonu a jednat na vašem lokálním počítači, zde jsou tři směry, které stojí za prozkoumání:

1. **Souhrn akciového trhu**: Naplánujte OpenClaw tak, aby v pevném intervalu stahoval data z finančních API, shrnul pohyby dne pomocí vašeho lokálního modelu a každé ráno vám poslal souhrn do telefonu přes vybraný kanál.

2. **Monitor jemného ladění (fine-tuning)**: Spusťte trénovací úlohu vzdáleně přes Telegram nebo Discord a nechte agenta sledovat trénovací log a pravidelně vám do telefonu hlásit hodnoty ztráty, vytížení GPU a využití disku. Pokud se běh zasekne nebo dojde ke špičce ve VRAM, dozvíte se to okamžitě, aniž byste museli být u počítače.

3. **IOT s lokálním VLM**: Namiřte kameru na vaše vchodové dveře, spusťte vizuální model na Lemonade a nechte OpenClaw analyzovat snímky na vyžádání nebo při spuštění triggeru. Zeptejte se ze svého telefonu „přišly dnes nějaké balíky?“ a dostanete přímou odpověď z vlastního hardwaru.

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