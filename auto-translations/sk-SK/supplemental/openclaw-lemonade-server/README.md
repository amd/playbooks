<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Spustenie OpenClaw s Lemonade Server ako backendom

## Prehľad

[**OpenClaw**](https://openclaw.ai/) je autonómny AI agent, ktorý dokáže písať a spúšťať kód, spravovať súbory a vykonávať za vás zložité viackrokové úlohy. Na rozdiel od chatového asistenta, ktorý iba odpovedá na otázky, OpenClaw vykonáva na vašom systéme skutočné akcie, čo znamená, že potrebuje rýchly a schopný AI backend, ktorý zvládne náročnú slučku agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je práve takýto backend. Ide o open-source lokálny inferenčný server, ktorý spúšťa GenAI modely priamo na vašom hardvéri a sprístupňuje ich prostredníctvom priemyselne štandardného OpenAI API.

Spolu tvoria plne lokálny AI agentský stack: Lemonade sa stará o inferenciu modelu a OpenClaw poskytuje slučku agenta, ktorá premieňa výstupy modelu na skutočné akcie.

> **Predtým, než budete pokračovať:** OpenClaw je vysoko autonómny AI agent. Poskytnutie prístupu k vášmu systému akémukoľvek AI agentovi môže viesť k nepredvídateľným alebo neúmyselným výsledkom. Pokračujte iba vtedy, ak rozumiete rizikám a ste s tým, že softvér koná autonómne vo vašom mene, uzrozumení.

---

## Čo sa naučíte

Na konci tohto sprievodcu budete vedieť:

- Zoznámiť sa s **Lemonade Server**
- **Nainštalovať OpenClaw** a **nasmerovať ho na Lemonade Server** ako svoj AI backend.
- **Spustiť bránu OpenClaw** a potvrdiť, že váš agent je pripravený na prácu.
- **Pripojiť komunikačný kanál** (Discord alebo Telegram), aby ste mohli chatovať so svojím agentom z akéhokoľvek zariadenia.

---

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Skontrolovať aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @os:linux -->
- PC so systémom **Ubuntu 24.04+** alebo kompatibilná distribúcia Linuxu založená na Debiane s `apt-get`
- Aspoň **12 GB RAM** (pre väčšie modely sa odporúča 64 GB+)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (voliteľné, na izoláciu OpenClaw)
- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
<!-- @os:end -->

<!-- @os:windows -->
- PC so systémom **Windows 10/11**
- Aspoň **12 GB RAM** (pre väčšie modely sa odporúča 64 GB+)
- **~10 – 30 GB voľného miesta na disku** pre váhy modelu
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (voliteľné, na izoláciu OpenClaw)
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

Odporúčaný model pre tohto sprievodcu je **Qwen3.6-35B-A3B-GGUF** od Unsloth, výkonný MoE model s kontextovým oknom 263k tokenov, ktorý sa dobre hodí na agentské úlohy. Tento model používa kvantizáciu UD-Q4_K_XL. Stiahnite ho teraz:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Potom ho načítajte s veľkým kontextovým oknom a uložte toto nastavenie pre budúce spúšťania:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model má predvolenú dĺžku kontextu 262 144 tokenov. Ak sa stretnete s chybami nedostatku pamäte (OOM), zvážte zmenšenie kontextového okna. Keďže však Qwen3.6 využíva rozšírený kontext pre zložité úlohy, odporúčame zachovať dĺžku kontextu aspoň 128 K tokenov, aby sa zachovali schopnosti uvažovania.

> **Tip: Vypnite uvažovanie pre rýchlejšie odpovede agenta:** Qwen3.6-35B-A3B beží predvolene v režime uvažovania, čo pridáva latenciu pred každou odpoveďou. Pri agentských slučkách sa táto réžia rýchlo kumuluje. Repozitár [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) poskytuje hotovú konfiguráciu, ktorá vypína uvažovanie. Ak ju chcete použiť, stiahnite súbor a importujte ho:
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

OpenClaw spúšťame vnútri WSL (odporúčané) a pripájame ho k Lemonade, ktoré beží natívne na Windows. Vďaka tomu získate pre OpenClaw prostredie shellu Linuxu, pričom si zachováte GPU akceleráciu Lemonade na strane Windows.

### Inštalácia WSL a Ubuntu

Otvorte PowerShell ako správca a nainštalujte jadro WSL:

```powershell
wsl --install --no-distribution
```

Následne nainštalujte Ubuntu:

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

Ukončite WSL a reštartujte ho:

```powershell
exit
wsl --shutdown
wsl
```

### Premostenie Lemonade z Windows do WSL

WSL2 beží vo virtuálnej sieti. Lemonade na Windows sa viaže na `127.0.0.1`, ktorú WSL nemôže priamo dosiahnuť. Proxy portu Windows presmeruje prevádzku z gateway IP adresy WSL na localhost systému Windows.

**Zistite gateway IP adresu WSL** (spustite vnútri WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Pridajte proxy portu** (spustite v PowerShell ako správca, pričom `<WSL-Gateway-IP>` nahraďte vašou gateway IP adresou WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Poznámka: Ak sa stretnete s chybou `netsh: command not found`, skúste namiesto toho použiť explicitný názov spustiteľného súboru – `netsh.exe`

**Pridajte pravidlo brány firewall** (v tom istom PowerShell so zvýšenými oprávneniami):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Overte z WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ak ste v predchádzajúcom kroku už načítali model Qwen3.6-35B-A3B-GGUF, mali by ste vidieť JSON výstup podobný tomuto:

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

#### Ako zabezpečiť, aby premostenie fungovalo aj po reštarte

Pravidlo `netsh portproxy` prežije reštart, ale IP adresa brány WSL sa môže po `wsl --shutdown` alebo reštarte zmeniť. Keď sa to stane, proxy stále smeruje na starú IP adresu a Lemonade sa z WSL stane nedostupným. Ak k tomu dôjde, použite jednu z nasledujúcich možností.

**Možnosť 1 (odporúčaná) — Automatická oprava premostenia.** Aby ste to nemuseli robiť ručne zakaždým, použite naplánovanú úlohu, ktorá pri každom spustení a prihlásení skontroluje premostenie a znova ho vytvorí iba vtedy, keď sa IP adresa brány zmenila. Pozrite si [príručku na automatickú opravu premostenia Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Možnosť 2 — Manuálna oprava premostenia.** Najprv zistite aktuálnu IP adresu brány WSL spustením tohto príkazu vnútri WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Skopírujte túto hodnotu; použijete ju namiesto `<new-WSL-Gateway-IP>` nižšie.

Potom v **PowerShelli so zvýšenými oprávneniami** (spustenom ako správca) vypíšte existujúce pravidlá, odstráňte iba zastarané pravidlo Lemonade a pridajte nové s aktuálnou IP adresou:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Vo výstupe príkazu `show all` je zastarané pravidlo Lemonade tá položka, ktorej pripájacia adresa (connect address) je `127.0.0.1` na porte `13305`; jej naslúchacia adresa (listen address) je vaša `<old-WSL-Gateway-IP>`. Odstránením podľa tejto adresy sa odstráni iba toto pravidlo a ostatné pravidlá port-proxy na vašom počítači zostanú nedotknuté.

Pravidlo brány firewall, ktoré ste pridali počas nastavovania, je viazané na port `13305` (nie na IP adresu), takže naďalej funguje a nie je potrebné ho znova vytvárať.

> **Odporúčanie:** Aby ste predišli problémom s bránou, dôrazne odporúčame nasledujúcu konfiguráciu shellu:
> - **Príkazy pre Windows** by sa mali spúšťať v **PowerShelli**
> - **Príkazy pre distribúciu WSL** by sa mali spúšťať v **príkazovom riadku** (spustenom ako **správca**)

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
> Príkazy v tejto časti spúšťajte vnútri **terminálu WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Príznak `--no-onboard` preskočí interaktívneho sprievodcu nastavením, model backend nakonfigurujete manuálne v nasledujúcom kroku, čo vám poskytuje presnú kontrolu nad tým, ktorý model a server sa použijú.

Otvorte nový terminál a potvrďte inštaláciu:

```bash
openclaw --version
```

> **Tip:** Ak sa po inštalácii zobrazí `command not found`, pridajte globálny bin adresár npm do vašej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby bola táto zmena trvalá, pridajte uvedený riadok do svojho súboru `~/.bashrc` alebo `~/.zshrc`.

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

Spustite neinteraktívne nastavenie (onboarding) OpenClaw.
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

> **Veľkosť kontextového okna OpenClaw:** Kompaktovanie v OpenClaw sa spustí, keď `contextTokens > contextWindow − reserveTokens`. Predvolená hodnota `reserveTokensFloor` je 20 000 tokenov, čo je spodná hranica, ktorá prepíše `reserveTokens`, keď je nižšia, takže akýkoľvek kontext modelu pod ~37k spustí nekonečnú slučku kompaktovania. Nastavte nízku rezervu a raz vo svojej konfigurácii vypnite spodnú hranicu a bude to platiť pre každý model, bez potreby ladenia pre jednotlivé modely:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodná hranica* (minimálna poistka), nie samotná rezerva, nastavenie iba spodnej hranice nemá žiaden účinok. `reserveTokensFloor: 0` vypne poistku, takže sa akceptuje nižšia hodnota `reserveTokens`.
>
> **Kedy toto použiť:** Použite túto konfiguráciu, ak je efektívne kontextové okno vášho modelu pod ~37k, buď preto, že model je malý (napr. 8k, 16k, 32k), alebo preto, že ste ho zámerne obmedzili na nižšiu hodnotu (napr. načítanie modelu so 128k, ale nastavenie kontextu na 16k v Lemonade). Bez toho OpenClaw pri spustení vstúpi do nekonečnej slučky kompaktovania.
>
> **Modely s veľkým kontextom pri plnom kontexte:** Toto môžete úplne preskočiť. Predvolené nastavenia fungujú dobre, kompaktovanie sa spustí ešte pred zaplnením okna a model má dostatok priestoru na generovanie dlhých odpovedí. Ak toto predsa len použijete, majte na pamäti, že `reserveTokens: 4096` obmedzuje dĺžku odpovede na približne 4k tokenov, čo môže spôsobiť skrátenie generovania dlhých súborov alebo podrobných plánov.
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
> Zvyšok vašej konfigurácie (gateway, channels, models atď.) zostáva nezmenený, treba pridať iba kľúč `compaction`.
### (Odporúčané) Povoľte Docker Sandboxing

OpenClaw dokáže presmerovať všetky operácie agenta so súbormi a kódom cez izolovaný Docker kontajner namiesto ich priameho spúšťania na vašom hostiteľovi. Tým sa obmedzí dosah akejkoľvek neúmyselnej akcie iba na sandbox, pričom súborový systém a sieť vášho hostiteľa zostanú nedotknuté.

Zostavte obraz sandboxu jedenkrát (Docker musí byť nainštalovaný):

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

Spustite toto, aby ste pridali kľúč `sandbox` vo vnútri existujúceho bloku `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Kontajnery sandboxu nemajú predvolene **žiadny prístup k sieti**. Pozrite si [referenčnú príručku k sandboxingu](https://docs.openclaw.ai/gateway/sandboxing) pre bind mounty a prepísania siete.

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
> Potom **reštartujte** svoj systém.
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

<!-- @os:linux -->
## (Odporúčané) Integrácia OpenClaw so službami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) poskytuje samostatne hostovanú službu na prehľadávanie webu a extrakciu obsahu, ktorá dokáže obísť tieto problémy a odomknúť plný potenciál automatizácie OpenClaw. 

V tomto nastavení beží OpenClaw ako súbor Docker kontajnerov spravovaných pomocou Podman. Aby sme zjednodušili správu životného cyklu a automatické spúšťanie, registrujeme Firecrawl ako používateľskú `systemd` službu, ktorá orchestrácie príslušný Podman Compose stack. Vďaka tomu môže OpenClaw spúšťať gateway, zastavovať ho a overovať službu Firecrawl pomocou štandardných príkazov `systemctl --user` namiesto priamej interakcie s kontajnermi. 

Aby sme veci zjednodušili, rozdelili sme celý proces do štyroch krokov:

---

### 1. Registrácia systémovej služby
Prejdite do adresára používateľskej konfigurácie systemd:
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
Ak je to úspešné, mali by ste vidieť nasledujúci výstup:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` obsahuje symbolické odkazy na služby nakonfigurované na automatické spúšťanie.

### 2. Konfigurácia Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je ideálny pre tých, ktorí potrebujú plnú kontrolu nad svojím prostredím na scraping a spracovanie dát, no má za následok dodatočné nároky na údržbu a konfiguráciu.

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
# FIRECRAWL_API_KEY="" # optional
```
### 3. Nasadenie OpenClaw pomocou Podman Compose

Predtým, ako budete pokračovať, uistite sa, že máte stiahnutý najnovší Docker obraz OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Keď je to hotové, stiahnite si súbor OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) a umiestnite ho do koreňového adresára `/firecrawl`:

> Táto konvencia je nevyhnutná na to, aby `systemd` mohol správne nájsť a spustiť službu, ako je uvedené v `WorkingDirectory=${HOME}/firecrawl`.

> Stack môžete kedykoľvek rozšíriť pridaním ďalších služieb Firecrawl podľa potreby. Úplný zoznam dostupných služieb nájdete v oficiálnom súbore [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Spustenie služby OpenClaw cez Firecrawl 

Predtým, ako odovzdáte kontrolu `systemd`, overte, že všetko funguje správne manuálnym spustením stacku:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ak je všetko správne nakonfigurované, mali by ste vidieť, ako sa kontajner OpenClaw spúšťa, a výstup príkazového riadka by mal vyzerať podobne ako toto:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Po overení stack pred pokračovaním znova zastavte:
```bash
podman compose -f openclaw-compose.yaml down
```
Pred spustením služby sa musíte uistiť, že sú nastavené správne vlastníctvo a oprávnenia pre adresár `firecrawl` a jeho súbor `.env`. 
Toto je nevyhnutné na to, aby služba mohla pri spustení zapísať vaše prihlasovacie údaje.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Teraz, keď je všetko overené, spustite službu cez `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Akcie OpenClaw](https://docs.openclaw.ai/) sú prístupné z interaktívneho kontajnera a webový dashboard je dostupný na rovnakom hostiteľovi a porte na adrese http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Získanie vášho `OPENCLAW_GATEWAY_TOKEN`

Keď je služba spustená a beží, všimnete si nový adresár `.openclaw` vytvorený vo vašom domovskom priečinku (~/.openclaw). Tento adresár je predvolene uzamknutý, takže ho budete musieť odomknúť, aby ste získali svoj gateway token.

1. Udeľte prístup k adresáru:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Prečítajte si svoj gateway token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Vyhľadajte hodnotu `OPENCLAW_GATEWAY_TOKEN` vo výstupe.

3. Otvorte dashboard gateway vo svojom prehliadači na adrese http://127.0.0.1:18789. Vložte svoj token, keď sa zobrazí výzva na autentifikáciu.

Ak chcete službu zastaviť, spustite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Spustenie OpenClaw Gateway

Gateway je proces OpenClaw, ktorý riadi slučku agenta a obsluhuje dashboard:

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

Ak chcete otvoriť dashboard, spustite toto v druhom termináli, zatiaľ čo gateway stále beží:

```bash
openclaw dashboard
```

Keďže gateway sa viaže na loopback, dashboard sa automaticky autentifikuje pri otvorení z rovnakého počítača, na lokálny prístup nie je potrebné zadávať token ani schvaľovať zariadenie. Mali by ste vidieť dashboard OpenClaw s vaším modelom Lemonade uvedeným ako aktívny backend.

> Ak ste povolili sandboxing, môžete si to overiť tak, že požiadate agenta, aby spustil `run hostname` z dashboardu. Ak namiesto názvu hostiteľa vášho počítača vidíte krátke ID kontajnera, sandbox funguje správne.

**Gratulujeme, vytvorili ste plne lokálny zásobník AI agenta od základov.**

> **Potrebujete token gateway?** Spustite `openclaw dashboard --no-open`, aby sa vypísala URL dashboardu so zabudovaným tokenom (tiež sa pokúsi skopírovať ho do schránky). Prípadne sa token nachádza v `gateway.auth.token` v súbore `~/.openclaw/openclaw.json`.

**Prístup k dashboardu z iného zariadenia (cez SSH tunel)**

Ak OpenClaw beží na vzdialenom počítači, môžete sa k jeho dashboardu dostať z vášho lokálneho počítača prostredníctvom SSH tunela. Tunel presmeruje port gateway (`18789`), aby váš lokálny prehliadač mohol komunikovať so vzdialeným gateway cez `127.0.0.1`.

1. Z vášho **lokálneho počítača** sa raz pripojte k vzdialenému počítaču a prijmite výzvu na odtlačok (fingerprint), aby sa hostiteľ pridal do vašich known hosts:

   ```bash
   ssh user@<host-ip>
   ```

2. Stále na vašom **lokálnom počítači** otvorte SSH tunel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Poznámka:** Po zadaní hesla terminál nezobrazí žiadny výstup a zdá sa, že zamrzol. To je očakávané: príznak `-N` hovorí SSH, aby nespúšťal žiadny vzdialený príkaz, takže jednoducho udržiava tunel otvorený. Nechajte tento terminál bežať.

3. Na vašom **lokálnom počítači** otvorte prehliadač a prejdite na `http://127.0.0.1:18789`.

4. Na **vzdialenom počítači** vypíšte token gateway a vložte ho do prehliadača na prihlásenie:

   ```bash
   openclaw dashboard --no-open
   ```

   Toto vypíše URL dashboardu so zabudovaným tokenom; skopírujte token na prihlásenie. (Token je tiež uložený v `gateway.auth.token` v súbore `~/.openclaw/openclaw.json`.)

> **Schvaľovanie vzdialeného zariadenia:** Keď otvoríte dashboard z iného počítača alebo telefónu, prehliadač môže zobraziť ID žiadosti. Na **vzdialenom počítači** vypíšte zoznam čakajúcich žiadostí:
> ```bash
> openclaw devices list
> ```
> Potom schváľte príslušnú žiadosť:
> ```bash
> openclaw devices approve <requestId>
> ```
> Toto je potrebné iba pre vzdialené alebo sekundárne zariadenia; prístup cez loopback z rovnakého počítača sa autentifikuje automaticky. Podrobnosti nájdete v dokumentácii [Vzdialený prístup](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Voliteľné: Pripojenie komunikačného kanála

Po spustení gateway sa k vášmu lokálnemu agentovi môžete pripojiť z akéhokoľvek zariadenia. Vyberte možnosť, ktorá vyhovuje vášmu nastaveniu. OpenClaw podporuje [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) a ďalšie kanály, kompletný zoznam nájdete na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnosť A: Discord

Discord vyžaduje server, na ktorom **máte administrátorský prístup** na pridanie bota. Ak zdieľate servery, ale žiadny nevlastníte, použite možnosť B (Telegram).

#### Vytvorenie účtu a servera Discord

Ak nemáte účet Discord, zaregistrujte sa na [discord.com](https://discord.com). Potrebujete tiež server, na ktorom ste administrátorom, vytvorte ho kliknutím na ikonu **+** na bočnom paneli Discord a výberom **Create My Own**. Súkromný server postačuje.

#### Vytvorenie aplikácie a bota Discord

1. Prejdite na [Discord Developer Portal](https://discord.com/developers/applications) a kliknite na **New Application**. Zadajte mu názov (napr. „openclaw-bot“).
2. Na bočnom paneli kliknite na **Bot**. Nastavte používateľské meno bota.
3. Stále na stránke Bot prejdite dolu na **Privileged Gateway Intents** a povoľte:
   - **Message Content Intent** (povinné)
   - **Server Members Intent** (odporúčané)
4. Prejdite späť nahor a kliknite na **Reset Token**, aby ste vygenerovali token bota. Skopírujte ho.

#### Pridanie bota na váš server

1. Na bočnom paneli kliknite na **OAuth2/ URL Generator**.
2. V časti **Scopes** povoľte `bot` a `applications.commands`.
3. V časti **Bot Permissions** povoľte: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Skopírujte vygenerovanú URL, vložte ju do prehliadača, vyberte váš server a potvrďte. Bot by sa teraz mal objaviť v zozname členov vášho servera.

#### Zistenie vašich ID

Povoľte Developer Mode v Discorde (**User Settings/ Advanced/ Developer Mode**), potom:
- Kliknite pravým tlačidlom na ikonu vášho servera: **Copy Server ID**
- Kliknite pravým tlačidlom na svoj avatar: **Copy User ID**

#### Povolenie DM od členov servera

Kliknite pravým tlačidlom na ikonu vášho servera/ **Privacy Settings**/ zapnite **Direct Messages**. Toto umožňuje botovi posielať vám DM, čo je potrebné pre krok párovania.

#### Konfigurácia OpenClaw pre Discord

Uložte token vášho bota ako premennú prostredia, potom vytvorte jeden patch súbor, ktorý povolí Discord, odkazuje na token a zaradí váš server do allowlistu. Nahraďte `<server_id>` a `<user_id>` ID, ktoré ste zhromaždili vyššie.

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

> **Nespoliehajte sa na to, že požiadate agenta, aby toto nakonfiguroval.** Keď je povolený sandboxing, agent nemôže zapisovať do `~/.openclaw/openclaw.json` zvnútra sandboxu, namiesto toho použite vyššie uvedené príkazy CLI na hostiteľovi.

Reštartujte gateway, aby sa načítala nová konfigurácia kanála:

```bash
openclaw gateway run --bind loopback --port 18789
```

V priebehu niekoľkých sekúnd by ste mali vo výstupe gateway vidieť `logged in to discord as <bot-name>`.
#### Spárujte si účet Discord

Napíšte botovi súkromnú správu (DM) na Discorde. Odpovie krátkym párovacím kódom.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Schváľte ho na stroji, na ktorom beží OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Platnosť párovacích kódov vyprší po hodine.

Teraz môžete komunikovať so svojím agentom priamo z Discordu a presúvať úlohy na svoj lokálny hardvér.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnosť B: Telegram

Telegram je pre väčšinu používateľov jednoduchší ako Discord, nevyžaduje server ani prístup správcu.

#### Vytvorenie bota v Telegrame

1. Otvorte Telegram a napíšte správu **@BotFather**.
2. Odošlite `/newbot` a postupujte podľa pokynov. Uložte si token bota, ktorý vám poskytne.

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

Reštartujte gateway a potom pošlite svojmu botovi ľubovoľnú správu v Telegrame. Schváľte párovanie:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Platnosť párovacích kódov vyprší po hodine. Teraz môžete komunikovať so svojím agentom cez súkromné správy v Telegrame.

---

## Ďalšie kroky

Teraz, keď váš agent dokáže prijímať príkazy z telefónu a vykonávať akcie na vašom lokálnom stroji, tu sú tri smery, ktoré stoja za preskúmanie:

1. **Súhrn akciového trhu**: Naplánujte OpenClaw tak, aby v pevných intervaloch získaval údaje z finančných API, sumarizoval denné pohyby pomocou vášho lokálneho modelu a každé ráno posielal súhrn do vášho telefónu cez zvolený kanál.

2. **Monitor doladenia (fine-tuning)**: Spustite tréningovú úlohu na diaľku cez Telegram alebo Discord a nechajte agenta sledovať tréningový log a pravidelne hlásiť hodnoty straty (loss), využitie GPU a stav disku späť do vášho telefónu. Ak sa beh zastaví alebo dôjde k nárastu VRAM, dozviete sa to okamžite bez toho, aby ste museli byť pri stroji.

3. **IOT s lokálnym VLM**: Nasmerujte kameru na svoje vchodové dvere, spustite vizuálny model na Lemonade a nechajte OpenClaw analyzovať snímky na požiadanie alebo pri spustení. Opýtajte sa z telefónu „prišli dnes nejaké balíky?“ a dostanete priamu odpoveď z vlastného hardvéru.

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