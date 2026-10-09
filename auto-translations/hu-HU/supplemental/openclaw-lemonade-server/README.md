<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# OpenClaw futtatása Lemonade Server háttérszolgáltatással

## Áttekintés

A [**OpenClaw**](https://openclaw.ai/) egy autonóm AI-ügynök, amely képes kódot írni és futtatni, fájlokat kezelni, valamint összetett, több lépésből álló feladatokat elvégezni a nevedben. Egy csevegőasszisztenssel ellentétben, amely csak kérdésekre válaszol, az OpenClaw valódi műveleteket hajt végre a rendszereden, ami azt jelenti, hogy egy gyors, nagy teljesítményű AI háttérszolgáltatásra van szüksége, amely lépést tud tartani egy igényes ügynöki ciklussal.

A [**Lemonade Server**](https://lemonade-server.ai/) ez a háttérszolgáltatás. Ez egy nyílt forráskódú, helyi következtetési szerver, amely közvetlenül a hardvereden futtatja a GenAI modelleket, és az iparági szabványnak számító OpenAI API-n keresztül teszi elérhetővé azokat.

Együtt egy teljesen helyi AI-ügynöki rendszert alkotnak: a Lemonade végzi a modellek következtetését, az OpenClaw pedig biztosítja azt az ügynöki ciklust, amely a modell kimeneteit valódi műveletekké alakítja.

> **Mielőtt folytatnád:** Az OpenClaw egy rendkívül autonóm AI-ügynök. Ha bármely AI-ügynöknek hozzáférést adsz a rendszeredhez, az kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytasd, ha megérted a kockázatokat, és elfogadod, hogy autonóm szoftver cselekszik a nevedben.

---

## Mit fogsz megtanulni

Ennek az útmutatónak a végére képes leszel:

- Megismerni a **Lemonade Server**-t
- **Telepíteni az OpenClaw-ot**, és **beállítani, hogy a Lemonade Server-t** használja AI háttérszolgáltatásként.
- **Elindítani az OpenClaw gateway-t**, és megerősíteni, hogy az ügynököd készen áll a munkára.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármely eszközről csevegni tudj az ügynököddel.

---

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## A szükséges szoftverek telepítése

<!-- @os:linux -->
- Egy **Ubuntu 24.04+** vagy egy kompatibilis, `apt-get`-et használó, Debian-alapú Linux disztribúciót futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcionális, az OpenClaw sandboxoláshoz)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
<!-- @os:end -->

<!-- @os:windows -->
- Egy **Windows 10/11** rendszert futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcionális, az OpenClaw sandboxoláshoz)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @os:linux -->
<!-- @prereq:nodejs -->
<!-- @os:end -->
<!-- On Windows OpenClaw runs in WSL, so its Node.js is covered by the openclaw prereq. -->
<!-- @prereq:docker,openclaw,lemonade-models-qwen3-6-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Az ajánlott modell letöltése és betöltése

Ehhez az útmutatóhoz az ajánlott modell a **Qwen3.6-35B-A3B-GGUF**, az Unsloth kínálatából, egy erős MoE modell 263k tokenes kontextusablakkal, amely kiválóan alkalmas ügynöki munkaterhelésekhez. Ez a modell UD-Q4_K_XL kvantálást használ. Töltsd le most:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ezután töltsd be egy nagy kontextusablakkal, és mentsd el ezt a beállítást a jövőbeli futtatásokhoz:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriahiány (OOM) hibákba ütközöl, fontold meg a kontextusablak csökkentését. Mivel azonban a Qwen3.6 kibővített kontextust használ az összetett feladatokhoz, azt javasoljuk, hogy legalább 128K tokenes kontextushosszt tarts meg a gondolkodási képességek megőrzése érdekében.

> **Tipp: Kapcsold ki a gondolkodást a gyorsabb ügynöki válaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést ad hozzá. Ügynöki ciklusok esetén ez a többletterhelés gyorsan felhalmozódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tárolóban található egy kész konfiguráció, amely kikapcsolja a gondolkodást. A használatához töltsd le a fájlt, és importáld:
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

## A WSL beállítása

Az OpenClaw-ot WSL-en belül futtatjuk (ajánlott), és a natívan Windows alatt futó Lemonade-hez csatlakoztatjuk. Ez egy Linux parancssori környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása Windows oldalon marad.

### A WSL és az Ubuntu telepítése

Nyisd meg a PowerShell-t rendszergazdaként, és telepítsd a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítsd az Ubuntut:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése WSL-ben

Futtasd ezt az Ubuntu terminálon belül:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Lépj ki a WSL-ből, majd indítsd újra:

```powershell
exit
wsl --shutdown
wsl
```

### A Lemonade áthidalása Windows-ról WSL-be

A WSL2 egy virtuális hálózatban fut. A Windows alatt futó Lemonade a `127.0.0.1` címhez kapcsolódik, amelyet a WSL nem tud közvetlenül elérni. A Windows portproxy továbbítja a forgalmat a WSL átjáró IP-címéről a Windows localhost felé.

**Keresd meg a WSL átjáró IP-címét** (futtasd a WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Add hozzá a portproxyt** (futtasd rendszergazdaként a PowerShell-ben, a `<WSL-Gateway-IP>` helyére írd be a saját WSL átjáró IP-címedet):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Megjegyzés: Ha `netsh: command not found` hibát tapasztalsz, próbáld meg helyette az explicit végrehajtható fájlnevet használni - `netsh.exe`

**Adj hozzá egy tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShell-ben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrizd a WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötted a Qwen3.6-35B-A3B-GGUF modellt, akkor ehhez hasonló JSON kimenetet kell látnod:

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

#### A híd működésének fenntartása újraindítás után

A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-címe megváltozhat a `wsl --shutdown` parancs vagy egy újraindítás után. Ha ez történik, a proxy még mindig a régi IP-címre mutat, és a Lemonade elérhetetlenné válik a WSL-ből. Ha ez bekövetkezik, használja az alábbi lehetőségek egyikét.

**1. lehetőség (ajánlott) — A híd automatikus javítása.** Hogy ne kelljen ezt minden alkalommal kézzel elvégeznie, használjon egy ütemezett feladatot, amely minden indításkor és bejelentkezéskor ellenőrzi a hidat, és csak akkor építi újra, ha az átjáró IP-címe megváltozott. Lásd a [Lemonade WSL híd automatikus javítási útmutatóját](assets/RepairLemonadeWslBridge.md).


**2. lehetőség — A híd kézi javítása.** Először szerezze meg az aktuális WSL átjáró IP-címét az alábbi parancs futtatásával a WSL-en belül:

```bash
ip route show default | awk '{print $3}' | head -1
```

Másolja ki ezt az értéket; ezt fogja használni a `<new-WSL-Gateway-IP>` helyett lentebb.

Ezután egy **emelt jogosultságú PowerShellben** (rendszergazdaként futtatva) listázza ki a meglévő szabályokat, törölje csak az elavult Lemonade szabályt, és adjon hozzá egy újat az aktuális IP-címmel:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

A `show all` kimenetében az elavult Lemonade szabály az a bejegyzés, amelynek kapcsolódási címe `127.0.0.1` a `13305` porton; a figyelési címe a `<old-WSL-Gateway-IP>`. Ha ezen cím alapján törli, csak ez az egy szabály szűnik meg, a gépen lévő többi port-proxy szabály érintetlen marad.

A beállítás során hozzáadott tűzfalszabály a `13305` porthoz van kötve (nem az IP-címhez), így az továbbra is működik, és nem kell újra létrehozni.

> **Javaslat:** Az átjáróval kapcsolatos problémák elkerülése érdekében a következő shell-konfigurációt javasoljuk:
> - A **Windows-parancsokat** **PowerShell**-ben kell futtatni
> - A **WSL disztribúció parancsait** egy **parancssorban** (Command Prompt) kell futtatni (**rendszergazdaként** futtatva)

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

## Az OpenClaw telepítése és konfigurálása

### Az OpenClaw telepítése
<!-- @os:windows -->
> A szakaszban szereplő parancsokat a **WSL terminálban** futtassa.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-onboard` jelző kihagyja az interaktív beállítási varázslót, a modell háttérrendszerét a következő lépésben manuálisan fogja beállítani, ami pontos ellenőrzést biztosít afölött, hogy melyik modellt és szervert használja.

Nyisson egy új terminált, és erősítse meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha a telepítés után a `command not found` üzenetet látja, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ahhoz, hogy ez maradandó legyen, adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájlhoz.

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


### Az OpenClaw konfigurálása a Lemonade használatára

Futtassa az OpenClaw nem interaktív onboarding folyamatát.
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

Ez a parancs megírja az OpenClaw konfigurációját a `~/.openclaw/openclaw.json` fájlba.

> **OpenClaw kontextusablak-méretezés:** Az OpenClaw tömörítése akkor indul el, amikor `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` érték 20 000 token, egy alsó korlát, amely felülírja a `reserveTokens` értéket, ha az alacsonyabb, így minden olyan modell-kontextus, amely ~37k alatt van, végtelen tömörítési ciklust indít el. Állítson be egy alacsony tartalékot, és tiltsa le az alsó korlátot egyszer a konfigurációjában, és ez minden modellre vonatkozni fog, modellenkénti finomhangolásra nincs szükség:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimum védelem), nem maga a tartalék; ha csak az alsó korlátot állítja be, annak nincs hatása. A `reserveTokensFloor: 0` letiltja a védelmet, így az alacsonyabb `reserveTokens` érték érvénybe lép.
>
> **Mikor alkalmazza ezt:** Használja ezt a konfigurációt, ha a modell tényleges kontextusablaka ~37k alatt van, akár azért, mert a modell kicsi (pl. 8k, 16k, 32k), akár azért, mert szándékosan alacsonyabb értékre korlátozta (pl. egy 128k-s modellt tölt be, de a kontextust 16k-ra állítja a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatja. Az alapértelmezett beállítások jól működnek, a tömörítés jóval azelőtt elindul, hogy az ablak megtelne, és a modellnek bőven van helye hosszú válaszok generálására. Ha mégis alkalmazza, vegye figyelembe, hogy a `reserveTokens: 4096` a válasz hosszát ~4k tokenre korlátozza, ami megszakíthatja a hosszú fájlgenerálást vagy a részletes terveket.
>
> **Hová adja hozzá:** Helyezze el a `compaction` blokkot az `agents.defaults` részen belül az `openclaw.json` fájlban (általában a `~/.openclaw/openclaw.json` útvonalon):
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
> A konfiguráció többi része (gateway, csatornák, modellek stb.) változatlan marad, csak a `compaction` kulcsot kell hozzáadni.
### (Ajánlott) Docker sandboxing engedélyezése

Az OpenClaw képes az összes ügynöki fájl- és kódműveletet egy izolált Docker konténeren keresztül irányítani ahelyett, hogy közvetlenül a hoszton futtatná azokat. Ez a nem szándékolt műveletek hatókörét a sandboxra korlátozza, így a hoszt fájlrendszere és hálózata érintetlen marad.

Építsd fel egyszer a sandbox image-et (a Dockernek telepítve kell lennie):

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

Futtasd ezt a `sandbox` kulcs hozzáadásához a meglévő `agents.defaults` blokkon belül a `~/.openclaw/openclaw.json` fájlban:

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

A sandbox konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A bind mountokkal és a hálózati felülírásokkal kapcsolatban lásd a [sandboxing referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker engedély megtagadva
> 
> Ha „permission denied” hibát kapsz Docker parancsok futtatásakor:
> 
> **1. lépés: Add hozzá a felhasználódat a docker csoporthoz**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **2. lépés: Ha a hiba továbbra is fennáll, alkalmazd a végleges javítást**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Ezután **indítsd újra** a rendszered.
> 
> **Gyors, ideiglenes javítás** (újraindítás után visszaáll):
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
## (Ajánlott) OpenClaw integráció Firecrawl szolgáltatásokkal

A [Firecrawl](https://docs.firecrawl.dev/introduction) egy önállóan üzemeltetett webes bejárási és tartalomkinyerési szolgáltatást biztosít, amely képes megkerülni ezeket a kihívásokat, és kiaknázni az OpenClaw automatizálás teljes potenciálját.

Ebben a konfigurációban az OpenClaw Docker konténerek halmazaként fut, amelyeket Podman kezel. Az életciklus-kezelés és az automatikus indítás egyszerűsítése érdekében a Firecrawl-t felhasználói szintű `systemd` szolgáltatásként regisztráljuk, amely az alapul szolgáló Podman Compose stacket vezérli. Ez lehetővé teszi, hogy az OpenClaw a gateway-t standard `systemctl --user` parancsokkal indítsa, állítsa le és ellenőrizze a Firecrawl szolgáltatást, ahelyett hogy közvetlenül a konténerekkel kellene interakcióba lépni.

Az egyszerűség kedvéért a teljes folyamatot négy lépésre bontottuk:

---

### 1. A rendszerszolgáltatás regisztrálása
Navigálj a systemd felhasználói konfigurációs könyvtárba:
```bash
cd ~/.config/systemd/user
```
Hozz létre és nyiss meg egy új fájlt `firecrawl.service` néven.
```bash
nano firecrawl.service
```
Másold be a következő konfigurációt:
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
Ezen a ponton a szolgáltatás definiálva van, de még nincs regisztrálva a `systemd`-nél.
Győződj meg róla, hogy a fájlnév pontosan megegyezik a fent létrehozottal, majd futtasd:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Sikeres végrehajtás esetén a következő kimenetet kell látnod:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

A `default.target.wants/` szimbolikus linkeket tartalmaz azokra a szolgáltatásokra, amelyek automatikus indításra vannak konfigurálva.

### 2. A Firecrawl konfigurálása

A [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) ideális azok számára, akiknek teljes körű irányításra van szükségük a scraping és adatfeldolgozási környezetük felett, de ez további karbantartási és konfigurációs ráfordítással jár.

Kezdd a repository klónozásával:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Hozz létre egy `.env` fájlt a `/firecrawl` könyvtárban: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Az OpenClaw telepítése Podman Compose segítségével

Mielőtt továbblépnél, győződj meg róla, hogy letöltötted a legújabb OpenClaw Docker image-et:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ha ez megtörtént, töltsd le az OpenClaw Compose fájlt [openclaw-compose.yaml](assets/openclaw-compose.yaml) és helyezd el a `/firecrawl` gyökérkönyvtárban:

> Erre a konvencióra azért van szükség, hogy a `systemd` a `WorkingDirectory=${HOME}/firecrawl` beállításnak megfelelően megtalálja és el tudja indítani a szolgáltatást.

> A stacket bármikor bővítheted további Firecrawl szolgáltatások hozzáadásával, igény szerint. Az elérhető szolgáltatások teljes listája a hivatalos [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fájlban található.

### 4. Az OpenClaw szolgáltatás elindítása a Firecrawl-on keresztül

Mielőtt átadnád az irányítást a `systemd`-nek, ellenőrizd, hogy minden megfelelően működik, a stack manuális futtatásával:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ha minden helyesen van konfigurálva, látnod kell, hogy az OpenClaw konténer elindul, és a parancssori kimenetednek valahogy így kell kinéznie:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Ellenőrzés után a továbblépés előtt állítsd le újra a stacket:
```bash
podman compose -f openclaw-compose.yaml down
```
A szolgáltatás elindítása előtt győződj meg róla, hogy a `firecrawl` könyvtáron és a `.env` fájlon a megfelelő tulajdonjog és jogosultságok vannak beállítva.
Ez elengedhetetlen ahhoz, hogy a szolgáltatás indításkor ki tudja írni a hitelesítő adataidat.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Most, hogy minden ellenőrizve van, indítsd el a szolgáltatást a `systemd`-en keresztül:
```bash
systemctl --user start firecrawl.service
```
[Az OpenClaw Actions](https://docs.openclaw.ai/) elérhető az interaktív konténeren belülről, és a Web Dashboard ugyanazon a hoszton és porton érhető el: http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Az `OPENCLAW_GATEWAY_TOKEN` beszerzése

Miután a szolgáltatás elindult és fut, egy új `.openclaw` könyvtárat fogsz találni a saját mappádban (~/.openclaw). Ez a könyvtár alapértelmezés szerint zárolva van, ezért a gateway token lekéréséhez fel kell oldanod a zárolást.

1. Add meg a hozzáférést a könyvtárhoz:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Olvasd ki a gateway tokenedet:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Keresd meg az `OPENCLAW_GATEWAY_TOKEN` értékét a kimenetben.

3. Nyisd meg a gateway irányítópultot a böngésződben a http://127.0.0.1:18789 címen. Illeszd be a tokenedet, amikor a hitelesítéshez kéri.

A szolgáltatás leállításához futtasd:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Indítsd el az OpenClaw Gateway-t

A gateway az az OpenClaw folyamat, amely kezeli az ügynök hurkot (agent loop), és kiszolgálja a műszerfalat (dashboard):

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

A műszerfal megnyitásához futtasd ezt egy második terminálban, miközben a gateway továbbra is fut:

```bash
openclaw dashboard
```

Mivel a gateway a loopback-re csatlakozik, a műszerfal automatikusan hitelesít, amikor ugyanarról a gépről nyitod meg, nincs szükség token megadására vagy eszközjóváhagyásra helyi hozzáférés esetén. A megjelenő OpenClaw műszerfalon a Lemonade modelled aktív háttérrendszerként (backend) kell, hogy szerepeljen.

> Ha engedélyezted a sandboxolást, ezt úgy ellenőrizheted, hogy megkéred az ügynököt a `run hostname` futtatására a műszerfalról. Ha egy rövid konténer-azonosítót látsz a géped hosztneve helyett, a sandbox megfelelően működik.

**Gratulálunk, egy teljesen helyi AI ügynök-stacket építettél fel a semmiből.**

> **Szükséged van a gateway tokenjére?** Futtasd az `openclaw dashboard --no-open` parancsot, hogy kiírja a műszerfal URL-jét a beágyazott tokennel együtt (emellett megpróbálja a vágólapra is másolni). Alternatívaként a token megtalálható a `gateway.auth.token` alatt a `~/.openclaw/openclaw.json` fájlban.

**A műszerfal elérése egy másik eszközről (SSH alagúton keresztül)**

Ha az OpenClaw egy távoli gépen fut, elérheted a műszerfalát a helyi gépedről egy SSH alagúton keresztül. Az alagút továbbítja a gateway portot (`18789`), így a helyi böngésződ a `127.0.0.1` címen keresztül tud kommunikálni a távoli gateway-vel.

1. A **helyi gépeden** csatlakozz egyszer a távoli géphez, és fogadd el az ujjlenyomat (fingerprint) felszólítást, hogy a hoszt bekerüljön az ismert hosztok közé:

   ```bash
   ssh user@<host-ip>
   ```

2. Még mindig a **helyi gépeden**, nyisd meg az SSH alagutat:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Megjegyzés:** A jelszó megadása után a terminál nem mutat semmilyen kimenetet, és úgy tűnik, lefagyott. Ez normális: a `-N` jelző utasítja az SSH-t, hogy ne futtasson semmilyen távoli parancsot, így egyszerűen nyitva tartja az alagutat. Hagyd futni ezt a terminált.

3. A **helyi gépeden** nyiss meg egy böngészőt, és menj a `http://127.0.0.1:18789` címre.

4. A **távoli gépen** írasd ki a gateway tokent, és illeszd be a böngészőbe a bejelentkezéshez:

   ```bash
   openclaw dashboard --no-open
   ```

   Ez kiírja a műszerfal URL-jét a beágyazott tokennel; másold ki a tokent a bejelentkezéshez. (A token a `gateway.auth.token` alatt is tárolva van a `~/.openclaw/openclaw.json` fájlban.)

> **Egy távoli eszköz jóváhagyása:** Amikor egy másik gépről vagy telefonról nyitod meg a műszerfalat, a böngésző megjeleníthet egy kérés-azonosítót (request ID). A **távoli gépen** listázd a függőben lévő kéréseket:
> ```bash
> openclaw devices list
> ```
> Majd hagyd jóvá a megfelelő kérést:
> ```bash
> openclaw devices approve <requestId>
> ```
> Erre csak távoli vagy másodlagos eszközök esetén van szükség; a loopback hozzáférés ugyanarról a gépről automatikusan hitelesít. Bővebben lásd a [Remote Access](https://docs.openclaw.ai/gateway/remote) dokumentációt.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Amint a gateway fut, bármelyik eszközödről elérheted a helyi ügynöködet. Válaszd ki a beállításodnak megfelelő opciót. Az OpenClaw támogatja a [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) és más csatornákat, lásd a teljes listát a [docs.openclaw.ai](https://docs.openclaw.ai) oldalon.

---

### A opció: Discord

A Discordhoz szükség van egy szerverre, ahol **adminisztrátori hozzáféréssel rendelkezel** egy bot hozzáadásához. Ha osztozol szervereken, de nincs saját szervered, használd a B opciót (Telegram) helyette.

#### Discord fiók és szerver létrehozása

Ha nincs Discord fiókod, regisztrálj a [discord.com](https://discord.com) oldalon. Szükséged van egy szerverre is, ahol adminisztrátor vagy; hozz létre egyet a **+** ikonra kattintva a Discord oldalsávjában, majd válaszd a **Create My Own** lehetőséget. Egy privát szerver megfelelő.

#### Discord alkalmazás és bot létrehozása

1. Menj a [Discord Developer Portal](https://discord.com/developers/applications) oldalra, és kattints a **New Application** gombra. Adj neki egy nevet (pl. „openclaw-bot”).
2. Az oldalsávban kattints a **Bot** fülre. Állíts be egy felhasználónevet a botnak.
3. Még mindig a Bot oldalon, görgess le a **Privileged Gateway Intents** részhez, és engedélyezd:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgess vissza és kattints a **Reset Token** gombra a bot tokened generálásához. Másold ki.

#### A bot hozzáadása a szerveredhez

1. Az oldalsávban kattints az **OAuth2/ URL Generator** fülre.
2. A **Scopes** alatt engedélyezd a `bot` és `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezd: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másold ki a generált URL-t, illeszd be a böngésződbe, válaszd ki a szervered, és erősítsd meg. A botnak most meg kell jelennie a szervered tagjainak listájában.

#### Az azonosítóid összegyűjtése

Engedélyezd a Fejlesztői módot (Developer Mode) a Discordban (**User Settings/ Advanced/ Developer Mode**), majd:
- Kattints jobb gombbal a szervered ikonjára: **Copy Server ID**
- Kattints jobb gombbal a saját avatárodra: **Copy User ID**

#### Közvetlen üzenetek engedélyezése a szerver tagjaitól

Kattints jobb gombbal a szervered ikonjára/ **Privacy Settings**/ kapcsold be a **Direct Messages** opciót. Ez lehetővé teszi, hogy a bot privát üzenetet küldjön neked, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárold a bot tokenedet környezeti változóként, majd hozz létre egyetlen patch fájlt, amely engedélyezi a Discordot, hivatkozik a tokenre, és engedélyezőlistára (allowlist) teszi a szervered. Cseréld ki a `<server_id>` és `<user_id>` értékeket a fent összegyűjtött azonosítókra.

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

> **Ne hagyatkozz arra, hogy megkéred az ügynököt ennek konfigurálására.** Ha a sandboxolás engedélyezve van, az ügynök nem tud írni a `~/.openclaw/openclaw.json` fájlba a sandboxon belülről, ehelyett használd a fenti CLI parancsokat a hoszton.

Indítsd újra a gateway-t, hogy felvegye az új csatorna konfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül meg kell jelennie a `logged in to discord as <bot-name>` üzenetnek a gateway kimenetében.
#### Discord-fiók párosítása

Küldj DM-et a botnak Discordon. Egy rövid párosítási kóddal fog válaszolni.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyd jóvá azon a gépen, amelyen az OpenClaw fut:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Most már közvetlenül Discordról cseveghetsz az ügynököddel, és a feladatokat áthelyezheted a helyi hardveredre.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb, mint a Discord, nincs szükség sem szerverre, sem rendszergazdai hozzáférésre.

#### Telegram bot létrehozása

1. Nyisd meg a Telegramot, és küldj üzenetet a **@BotFather**-nek.
2. Küldd el a `/newbot` parancsot, és kövesd az utasításokat. Mentsd el a kapott bot tokent.

#### Az OpenClaw konfigurálása Telegramhoz

Tárold a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add hozzá a csatorna konfigurációját a `~/.openclaw/openclaw.json` fájlhoz (vagy javítsd a panelen keresztül):

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

Indítsd újra a gatewayt, majd küldj a botodnak egy üzenetet Telegramon. Hagyd jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Most már cseveghetsz az ügynököddel a Telegram DM-en keresztül.

---

## Következő lépések

Most, hogy az ügynököd parancsokat tud fogadni a telefonodról, és végrehajtja azokat a helyi gépeden, íme három irány, amelyet érdemes felfedezni:

1. **Tőzsdei összefoglaló**: Ütemezd be az OpenClaw-t, hogy fix időközönként adatokat kérjen le pénzügyi API-kból, foglalja össze a nap mozgásait a helyi modellel, és minden reggel küldjön egy kivonatot a telefonodra a választott csatornán keresztül.

2. **Finomhangolás-figyelő**: Indíts el egy tanítási feladatot távolról Telegramon vagy Discordon keresztül, majd az ügynök kövesse nyomon a tanítási naplót, és jelentse vissza a telefonodra az időszakos veszteségértékeket, a GPU-kihasználtságot és a lemezhasználatot. Ha a futás megakad vagy a VRAM-használat megugrik, azonnal értesülsz róla anélkül, hogy a gépnél kellene lenned.

3. **IOT helyi VLM-mel**: Irányíts egy kamerát a bejárati ajtódra, futtass egy látásmodellt a Lemonade-en, és az OpenClaw igény szerint vagy egy kiváltó esemény alapján elemezze a képkockákat. Kérdezd meg a telefonodról, hogy „érkezett-e ma csomag?”, és egyenes választ kapsz a saját hardveredtől.

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