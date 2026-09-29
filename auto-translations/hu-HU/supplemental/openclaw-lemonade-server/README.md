<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# OpenClaw futtatása Lemonade Server háttérrendszerrel

## Áttekintés

A [**OpenClaw**](https://openclaw.ai/) egy autonóm AI ágens, amely képes kódot írni és futtatni, fájlokat kezelni, és összetett, több lépésből álló feladatokat végrehajtani a nevedben. Ellentétben egy csevegőasszisztenssel, amely csupán válaszol a kérdésekre, az OpenClaw valós műveleteket hajt végre a rendszereden, ami azt jelenti, hogy egy gyors, képes AI háttérrendszerre van szüksége, amely lépést tud tartani egy igényes ágenshurokkal.

A [**Lemonade Server**](https://lemonade-server.ai/) ez a háttérrendszer. Egy nyílt forráskódú, helyi következtetési szerver, amely közvetlenül a hardvereden futtatja a GenAI modelleket, és az iparági szabvány OpenAI API-n keresztül teszi őket elérhetővé.

Együtt egy teljesen helyi AI ágens stacket alkotnak: a Lemonade végzi a modell-következtetést, az OpenClaw pedig biztosítja azt az ágenshurkot, amely a modell kimeneteit valós műveletekké alakítja.

> **Mielőtt folytatnád:** Az OpenClaw egy erősen autonóm AI ágens. Ha bármely AI ágensnek hozzáférést adsz a rendszeredhez, az kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytasd, ha megérted a kockázatokat, és elfogadod, hogy autonóm szoftver cselekszik a nevedben.

---

## Amit meg fogsz tanulni

Ennek a playbooknak a végére képes leszel:

- Megismerni a **Lemonade Server**-t
- **Telepíteni az OpenClaw-t**, és **beállítani, hogy a Lemonade Server-t** használja AI háttérrendszerként.
- **Elindítani az OpenClaw gateway-t**, és megerősíteni, hogy az ágensed készen áll a munkára.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármely eszközről cseveghess az ágenseddel.

---

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

<!-- @os:linux -->
- Egy **Ubuntu 24.04+**-t futtató PC, vagy egy kompatibilis, Debian alapú Linux disztribúció `apt-get` paranccsal
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcionális, az OpenClaw homokozózásához)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
<!-- @os:end -->

<!-- @os:windows -->
- Egy **Windows 10/11**-et futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcionális, az OpenClaw homokozózásához)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Az ajánlott modell letöltése és betöltése

Ehhez a playbookhoz az ajánlott modell a **Qwen3.6-35B-A3B-GGUF** az Unsloth-tól, egy erős MoE modell 263k tokenes kontextusablakkal, amely kiválóan alkalmas ágensfeladatokhoz. Ez a modell UD-Q4_K_XL kvantálást használ. Töltsd le most:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ezután töltsd be nagy kontextusablakkal, és mentsd el ezt a beállítást a jövőbeli futtatásokhoz:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriahiány (OOM) hibákba ütközöl, fontold meg a kontextusablak csökkentését. Mivel azonban a Qwen3.6 kibővített kontextust használ az összetett feladatokhoz, javasoljuk, hogy legalább 128K tokenes kontextushosszt tarts fenn a gondolkodási képességek megőrzése érdekében.

> **Tipp: Kapcsold ki a gondolkodást a gyorsabb ágensválaszokért:** A Qwen3.6-35B-A3B alapértelmezetten gondolkodási módban fut, ami minden válasz előtt késleltetést ad hozzá. Ágenshurkok esetén ez a többletidő gyorsan felhalmozódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tároló egy kész konfigurációt biztosít, amely kikapcsolja a gondolkodást. A használatához töltsd le a fájlt, és importáld:
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

## WSL beállítása

Az OpenClaw-t a WSL-en belül futtatjuk (ajánlott), és a natívan Windowson futó Lemonade-hez csatlakoztatjuk. Ez egy Linux shell környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### WSL és Ubuntu telepítése

Nyisd meg a PowerShellt rendszergazdaként, és telepítsd a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítsd az Ubuntu-t:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése a WSL-ben

Futtasd ezt az Ubuntu terminálban:

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

### A Lemonade áthidalása Windowsról a WSL-be

A WSL2 egy virtuális hálózatban fut. A Windowson futó Lemonade a `127.0.0.1` címhez kötődik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows portproxy továbbítja a forgalmat a WSL átjáró IP-címéről a Windows localhost felé.

**A WSL átjáró IP-cím megkeresése** (futtasd a WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**A portproxy hozzáadása** (futtasd PowerShellben rendszergazdaként, a `<WSL-Gateway-IP>` helyére a saját WSL átjáró IP-címedet írva):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Megjegyzés: Ha a `netsh: command not found` hibaüzenetet kapod, próbáld meg helyette az explicit végrehajtható fájlnevet használni - `netsh.exe`

**Tűzfalszabály hozzáadása** (ugyanabban az emelt jogosultságú PowerShellben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrzés a WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötted a Qwen3.6-35B-A3B-GGUF modellt, ehhez hasonló JSON kimenetet kell látnod:

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

A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-je megváltozhat egy `wsl --shutdown` vagy egy újraindítás után. Ha ez megtörténik, a proxy még mindig a régi IP-re mutat, és a Lemonade elérhetetlenné válik a WSL-ből. Ha ez történik, használja az alábbi lehetőségek egyikét.

**1. lehetőség (ajánlott) — A híd automatikus javítása.** Hogy ne kelljen ezt kézzel elvégezni minden alkalommal, használjon egy ütemezett feladatot, amely minden indításkor és bejelentkezéskor ellenőrzi a hidat, és csak akkor építi újra, ha az átjáró IP-je megváltozott. Lásd a [Lemonade WSL híd automatikus javítási útmutatóját](assets/RepairLemonadeWslBridge.md).


**2. lehetőség — A híd kézi javítása.** Először szerezze meg az aktuális WSL átjáró IP-t az alábbi parancs WSL-en belüli futtatásával:

```bash
ip route show default | awk '{print $3}' | head -1
```

Másolja ki ezt az értéket; a következőkben `<new-WSL-Gateway-IP>` helyett fogja használni.

Ezután egy **emelt jogosultságú PowerShell**-ben (Futtatás rendszergazdaként) sorolja fel a meglévő szabályokat, törölje csak az elavult Lemonade szabályt, és adjon hozzá egy újat az aktuális IP-vel:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

A `show all` kimenetében az elavult Lemonade szabály az a bejegyzés, amelynek csatlakozási címe `127.0.0.1` a `13305` porton; figyelő címe a régi `<old-WSL-Gateway-IP>`. Ha az adott cím alapján törli, csak ez az egy szabály törlődik, a gépén lévő többi port-proxy szabályt nem érinti.

A beállítás során hozzáadott tűzfalszabály a `13305` porthoz van kötve (nem az IP-hez), így tovább is működik, és nem kell újra létrehozni.

> **Javaslat:** Az átjáró problémáinak elkerülése érdekében erősen javasoljuk az alábbi shell-konfigurációt:
> - A **Windows-parancsokat** **PowerShell**-ben kell futtatni
> - A **WSL disztribúció parancsait** egy **Parancssorban** (rendszergazdaként futtatva) kell futtatni

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
> Az ebben a szakaszban szereplő parancsokat a **WSL terminálban** futtassa.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-onboard` jelző kihagyja az interaktív beállítási varázslót, a modell backendet a következő lépésben manuálisan fogja konfigurálni, ami pontos kontrollt biztosít afölött, hogy melyik modellt és szervert használja.

Nyisson egy új terminált, és erősítse meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha a telepítés után `command not found` üzenetet lát, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ahhoz, hogy ez tartós legyen, adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájljához.

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


### Az OpenClaw konfigurálása a Lemonade használatához

Futtassa az OpenClaw nem interaktív beüzemelését.
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

Ez a parancs kiírja az OpenClaw konfigurációját a `~/.openclaw/openclaw.json` fájlba.

> **OpenClaw kontextusablak méretezése:** Az OpenClaw tömörítése akkor indul el, amikor `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` érték 20 000 token, egy olyan alsó korlát, amely felülírja a `reserveTokens` értéket, ha az alacsonyabb, így minden kb. 37k alatti modellkontextus végtelen tömörítési ciklust indít el. Állítson be egy alacsony tartalékot, és egyszer tiltsa le az alsó korlátot a konfigurációjában, ez minden modellre érvényes lesz, modellenkénti hangolás nélkül:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimum védőérték), nem maga a tartalék, ha csak az alsó korlátot állítja be, annak nincs hatása. A `reserveTokensFloor: 0` letiltja a védőértéket, így az alacsonyabb `reserveTokens` érték érvényesül.
>
> **Mikor alkalmazza ezt:** Használja ezt a konfigurációt, ha a modell tényleges kontextusablaka kb. 37k alatt van, akár azért, mert a modell kicsi (pl. 8k, 16k, 32k), akár azért, mert szándékosan alacsonyabb értékre korlátozta (pl. egy 128k-s modellt tölt be, de a kontextust 16k-ra állítja a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatja. Az alapértelmezett beállítások megfelelően működnek, a tömörítés jóval azelőtt bekapcsol, hogy az ablak megtelne, és a modellnek bőven van tere hosszú válaszok generálására. Ha mégis alkalmazza, vegye figyelembe, hogy a `reserveTokens: 4096` a válasz hosszát kb. 4k tokenre korlátozza, ami levághatja a hosszú fájlgenerálást vagy a részletes terveket.
>
> **Hova adja hozzá:** Helyezze el a `compaction` blokkot az `agents.defaults` szakaszban az `openclaw.json` fájlban (általában a `~/.openclaw/openclaw.json` helyen):
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
### (Ajánlott) Docker sandboxolás engedélyezése

Az OpenClaw képes az ügynök összes fájl- és kódműveletét egy izolált Docker konténeren keresztül irányítani, ahelyett, hogy közvetlenül a gazdagépen futtatná őket. Ez a nem szándékos műveletek hatókörét a sandboxra korlátozza, így a gazdagép fájlrendszere és hálózata érintetlen marad.

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

Futtasd le ezt, hogy hozzáadd a `sandbox` kulcsot a meglévő `agents.defaults` blokkhoz a `~/.openclaw/openclaw.json` fájlban:

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

A sandbox konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A bind mountokért és a hálózati beállítások felülbírálásáért lásd a [sandboxolási referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker jogosultság megtagadva
> 
> Ha "permission denied" hibát kapsz Docker parancsok futtatásakor:
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
> Ezután **indítsd újra** a rendszeredet.
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

A [Firecrawl](https://docs.firecrawl.dev/introduction) egy önállóan üzemeltethető webes lekérdezési és tartalomkinyerési szolgáltatást biztosít, amely képes megkerülni ezeket a kihívásokat, és kiaknázni az OpenClaw automatizálásban rejlő teljes potenciált.

Ebben a beállításban az OpenClaw egy Podmannel kezelt Docker konténerkészletként fut. Az életciklus-kezelés és az automatikus indítás egyszerűsítése érdekében a Firecrawl-t egy felhasználói szintű `systemd` szolgáltatásként regisztráljuk, amely a mögöttes Podman Compose stacket vezérli. Ez lehetővé teszi, hogy az OpenClaw elindítsa az átjárót, leállítsa és ellenőrizze a Firecrawl szolgáltatást a standard `systemctl --user` parancsokkal, ahelyett, hogy közvetlenül a konténerekkel kellene interakcióba lépni.

Az egyszerűség kedvéért a teljes folyamatot négy lépésre bontottuk:

---

### 1. Rendszerszolgáltatás regisztrálása
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
Sikeres futtatás esetén a következő kimenetet kell látnod:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

A `default.target.wants/` szimbolikus linkeket tartalmaz azokhoz a szolgáltatásokhoz, amelyek automatikusan indulnak.

### 2. Firecrawl konfigurálása

A [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) ideális azok számára, akiknek teljes kontrollra van szükségük a lekérdezési és adatfeldolgozási környezetük felett, de ez cserébe további karbantartási és konfigurációs feladatokkal jár.

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
### 3. OpenClaw telepítése Podman Compose-zal

Mielőtt továbblépnél, győződj meg róla, hogy letöltötted a legújabb OpenClaw Docker image-et:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ezután töltsd le az OpenClaw Compose fájlt [openclaw-compose.yaml](assets/openclaw-compose.yaml), és helyezd el a gyökér `/firecrawl` könyvtárban:

> Ez a konvenció szükséges ahhoz, hogy a `systemd` megfelelően megtalálja és elindítsa a szolgáltatást a `WorkingDirectory=${HOME}/firecrawl` beállításnak megfelelően.

> A stacket bármikor bővítheted további Firecrawl szolgáltatásokkal, amennyiben szükséges. A rendelkezésre álló szolgáltatások teljes listája a hivatalos [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fájlban található meg.

### 4. OpenClaw szolgáltatás indítása a Firecrawl-on keresztül

Mielőtt átadnád az irányítást a `systemd`-nek, ellenőrizd, hogy minden megfelelően működik-e a stack manuális futtatásával:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ha minden megfelelően van beállítva, látnod kell, hogy az OpenClaw konténer elindul, és a parancssori kimenetnek hasonlónak kell lennie ehhez:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Az ellenőrzés után a folytatás előtt állítsd le a stacket:
```bash
podman compose -f openclaw-compose.yaml down
```
A szolgáltatás elindítása előtt biztosítanod kell, hogy a `firecrawl` könyvtár és annak `.env` fájlja megfelelő tulajdonjoggal és jogosultságokkal rendelkezzen.
Ez elengedhetetlen ahhoz, hogy a szolgáltatás induláskor ki tudja írni a hitelesítő adataidat.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Most, hogy minden ellenőrizve lett, indítsd el a szolgáltatást a `systemd`-en keresztül:
```bash
systemctl --user start firecrawl.service
```
[Az OpenClaw Actions](https://docs.openclaw.ai/) elérhető az interaktív konténeren belülről, a Web Dashboard pedig ugyanazon a hoston és porton érhető el: http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Az `OPENCLAW_GATEWAY_TOKEN` beszerzése

Miután a szolgáltatás elindult és fut, észreveheted, hogy egy új `.openclaw` könyvtár jött létre a saját mappádban (~/.openclaw). Ez a könyvtár alapértelmezés szerint zárolva van, ezért fel kell oldanod a zárolást a gateway tokened lekéréséhez.

1. Adj hozzáférést a könyvtárhoz:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Olvasd ki a gateway tokened:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Keresd meg az `OPENCLAW_GATEWAY_TOKEN` értéket a kimenetben.

3. Nyisd meg a gateway dashboardot a böngésződben: http://127.0.0.1:18789. Az illesztéskor illeszd be a tokenedet a hitelesítéshez.

A szolgáltatás leállításához futtasd:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Az OpenClaw Gateway indítása

A gateway az az OpenClaw folyamat, amely az ügynök hurkot kezeli és kiszolgálja az irányítópultot:

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

Az irányítópult megnyitásához futtasd ezt egy második terminálban, miközben a gateway még fut:

```bash
openclaw dashboard
```

Mivel a gateway a loopback interfészhez kötődik, az irányítópult automatikusan hitelesít, ha ugyanarról a gépről nyitod meg, így a helyi hozzáféréshez nincs szükség token megadására vagy eszközjóváhagyásra. Az OpenClaw irányítópultnak meg kell jelennie, aktív háttérrendszerként a Lemonade modelleddel.

> Ha bekapcsoltad a sandboxolást, ellenőrizheted úgy, hogy megkéred az ügynököt a `run hostname` futtatására az irányítópultról. Ha egy rövid konténerazonosítót látsz a géped hosztneve helyett, a sandbox működik.

**Gratulálunk, egy teljesen helyi AI ügynök stacket építettél fel a semmiből.**

> **Szükséged van a gateway tokenre?** Futtasd az `openclaw dashboard --no-open` parancsot, hogy kiírassa az irányítópult URL-jét a beágyazott tokennel (a rendszer megpróbálja a vágólapra is másolni). Alternatívaként a token a `gateway.auth.token` mezőben található a `~/.openclaw/openclaw.json` fájlban.

**Az irányítópult elérése másik eszközről (SSH alagúton keresztül)**

Ha az OpenClaw egy távoli gépen fut, elérheted az irányítópultját a helyi gépedről egy SSH alagúton keresztül. Az alagút továbbítja a gateway portot (`18789`), így a helyi böngésződ a `127.0.0.1` címen keresztül kommunikálhat a távoli gateway-jel.

1. A **helyi gépeden** csatlakozz egyszer a távoli géphez, és fogadd el az ujjlenyomat-kérést, hogy a host bekerüljön az ismert hosztok közé:

   ```bash
   ssh user@<host-ip>
   ```

2. Még mindig a **helyi gépeden**, nyisd meg az SSH alagutat:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Megjegyzés:** A jelszó megadása után a terminál nem mutat kimenetet, és úgy tűnik, mintha lefagyott volna. Ez normális: a `-N` kapcsoló megmondja az SSH-nak, hogy ne futtasson semmilyen távoli parancsot, így egyszerűen nyitva tartja az alagutat. Hagyd futni ezt a terminált.

3. A **helyi gépeden** nyiss meg egy böngészőt, és menj a `http://127.0.0.1:18789` címre.

4. A **távoli gépen** írasd ki a gateway tokent, és illeszd be a böngészőbe a bejelentkezéshez:

   ```bash
   openclaw dashboard --no-open
   ```

   Ez kiírja az irányítópult URL-jét a beágyazott tokennel; másold ki a tokent a bejelentkezéshez. (A token a `gateway.auth.token` mezőben is megtalálható a `~/.openclaw/openclaw.json` fájlban.)

> **Távoli eszköz jóváhagyása:** Amikor egy másik gépről vagy telefonról nyitod meg az irányítópultot, a böngésző megjeleníthet egy kérésazonosítót. A **távoli gépen** listázd ki a függőben lévő kéréseket:
> ```bash
> openclaw devices list
> ```
> Majd hagyd jóvá a megfelelő kérést:
> ```bash
> openclaw devices approve <requestId>
> ```
> Erre csak távoli vagy másodlagos eszközök esetén van szükség; az ugyanarról a gépről érkező loopback hozzáférés automatikusan hitelesít. Részletekért lásd a [Távoli hozzáférés](https://docs.openclaw.ai/gateway/remote) dokumentációt.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Miután a gateway fut, bármilyen eszközről elérheted a helyi ügynöködet. Válaszd ki a beállításodhoz illő lehetőséget. Az OpenClaw támogatja a [Discordot](https://docs.openclaw.ai/channels/discord), a [Telegramot](https://docs.openclaw.ai/channels/telegram), és más csatornákat is, a teljes listát itt találod: [docs.openclaw.ai](https://docs.openclaw.ai).

---

### A opció: Discord

A Discordhoz szükséged van egy szerverre, ahol **rendelkezel adminisztrátori hozzáféréssel** egy bot hozzáadásához. Ha van közös szervered, de nem te vagy a tulajdonosa, használd inkább a B opciót (Telegram).

#### Discord fiók és szerver létrehozása

Ha nincs Discord fiókod, regisztrálj a [discord.com](https://discord.com) oldalon. Szükséged van egy szerverre is, ahol adminisztrátor vagy; hozz létre egyet a **+** ikonra kattintva a Discord oldalsávjában, majd válaszd a **Create My Own** opciót. Egy privát szerver is megfelelő.

#### Discord alkalmazás és bot létrehozása

1. Menj a [Discord Fejlesztői Portálra](https://discord.com/developers/applications), és kattints a **New Application** gombra. Adj neki egy nevet (pl. „openclaw-bot”).
2. Az oldalsávban kattints a **Bot** menüpontra. Állíts be egy felhasználónevet a botnak.
3. Még mindig a Bot oldalon, görgess le a **Privileged Gateway Intents** részhez, és engedélyezd:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgess vissza, és kattints a **Reset Token** gombra a bot tokened generálásához. Másold ki.

#### A bot hozzáadása a szerveredhez

1. Az oldalsávban kattints az **OAuth2/ URL Generator** menüpontra.
2. A **Scopes** alatt engedélyezd a `bot` és `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezd: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másold ki a generált URL-t, illeszd be a böngésződbe, válaszd ki a szervered, és erősítsd meg. A botnak most már meg kell jelennie a szervered tagjai között.

#### Az azonosítóid összegyűjtése

Kapcsold be a Fejlesztői módot a Discordban (**User Settings/ Advanced/ Developer Mode**), majd:
- Kattints jobb gombbal a szerver ikonjára: **Copy Server ID**
- Kattints jobb gombbal a saját avatárodra: **Copy User ID**

#### DM-ek engedélyezése a szerver tagjaitól

Kattints jobb gombbal a szerver ikonjára/ **Privacy Settings**/ kapcsold be a **Direct Messages** opciót. Ez lehetővé teszi, hogy a bot privát üzenetet küldjön neked, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárold a bot tokened környezeti változóként, majd hozz létre egyetlen patch fájlt, amely engedélyezi a Discordot, hivatkozik a tokenre, és engedélyezőlistára veszi a szerveredet. Cseréld le a `<server_id>` és `<user_id>` értékeket a fent összegyűjtött azonosítókra.

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

> **Ne bízd az ügynökre ennek beállítását.** Amikor a sandboxolás engedélyezve van, az ügynök nem tud írni a `~/.openclaw/openclaw.json` fájlba a sandboxon belülről, ehelyett használd a fenti CLI parancsokat a hoszton.

Indítsd újra a gateway-t, hogy felvegye az új csatorna konfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül a `logged in to discord as <bot-name>` üzenetet kell látnod a gateway kimenetében.
#### Párosítsd a Discord fiókodat

Küldj privát üzenetet a botnak Discordon. Válaszul egy rövid párosítási kódot fog küldeni.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyd jóvá azon a gépen, amelyiken az OpenClaw fut:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Mostantól közvetlenül a Discordból beszélgethetsz az ügynököddel, és feladatokat delegálhatsz a helyi hardveredre.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb, mint a Discord, mivel nincs szükség sem szerverre, sem admin hozzáférésre.

#### Hozz létre egy Telegram botot

1. Nyisd meg a Telegramot, és küldj üzenetet a **@BotFather**-nek.
2. Küldd el a `/newbot` parancsot, és kövesd az utasításokat. Mentsd el a kapott bot tokent.

#### Konfiguráld az OpenClaw-t Telegramhoz

Tárold a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add hozzá a csatorna konfigurációját a `~/.openclaw/openclaw.json` fájlhoz (vagy módosítsd a dashboardon keresztül):

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

Indítsd újra a gatewayt, majd küldj egy tetszőleges üzenetet a botodnak Telegramon. Hagyd jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Mostantól csevegehetsz az ügynököddel Telegram privát üzeneteken keresztül.

---

## Következő lépések

Most, hogy az ügynököd tud parancsokat fogadni a telefonodról, és tud is cselekedni a helyi gépeden, íme három érdemes irány, amit érdemes megvizsgálni:

1. **Tőzsdei összefoglaló**: Ütemezd be, hogy az OpenClaw rendszeres időközönként lekérje az adatokat pénzügyi API-kból, foglalja össze a napi mozgásokat a helyi modelleddel, és küldjön egy összegzést a telefonodra minden reggel a választott csatornán keresztül.

2. **Finomhangolás-figyelő**: Indíts el egy tanítási feladatot távolról Telegramon vagy Discordon keresztül, majd az ügynök kövesse nyomon a tanítási naplót, és jelentse vissza a telefonodra időszakosan a loss értékeket, a GPU-kihasználtságot és a lemezhasználatot. Ha a futás megakad, vagy megugrik a VRAM-használat, azonnal értesülsz róla anélkül, hogy a gépnél kellene lenned.

3. **IOT egy helyi VLM-mel**: Irányíts egy kamerát a bejárati ajtódra, futtass egy vizuális modellt a Lemonade-en, és kérd meg az OpenClaw-t, hogy elemezze a képkockákat igény szerint vagy egy trigger hatására. Kérdezd meg a telefonodról, hogy „érkezett-e csomag ma?”, és kapj egyértelmű választ a saját hardveredről.

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