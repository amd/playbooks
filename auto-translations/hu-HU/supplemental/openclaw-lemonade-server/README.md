<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Futtassa az OpenClaw-t Lemonade Server backend használatával

## Áttekintés

[**OpenClaw**](https://openclaw.ai/) egy autonóm AI ügynök, amely képes kódot írni és futtatni, fájlokat kezelni, valamint összetett, több lépésből álló feladatokat elvégezni az Ön nevében. Egy egyszerű chat-asszisztenssel ellentétben, amely csak kérdésekre válaszol, az OpenClaw valós műveleteket hajt végre a rendszerén, ami azt jelenti, hogy egy gyors, nagy teljesítményű AI backendre van szüksége, amely lépést tud tartani egy igényes ügynöki munkafolyamattal.

A [**Lemonade Server**](https://lemonade-server.ai/) pontosan ez a backend. Ez egy nyílt forráskódú, helyi inferenciakiszolgáló, amely közvetlenül az Ön hardverén futtatja a GenAI modelleket, és az iparági szabványnak számító OpenAI API-n keresztül teszi azokat elérhetővé.

Együtt egy teljesen helyi AI ügynöki rendszert alkotnak: a Lemonade végzi a modell-inferenciát, az OpenClaw pedig biztosítja azt az ügynöki munkafolyamatot, amely a modell kimeneteit valós műveletekké alakítja.

> **Mielőtt folytatná:** Az OpenClaw egy kifejezetten autonóm AI ügynök. Bármely AI ügynöknek hozzáférést adni a rendszeréhez kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytassa, ha megérti a kockázatokat, és elfogadja, hogy autonóm szoftver cselekszik az Ön nevében.

---

## Mit fog megtanulni

Ennek az útmutatónak a végére képes lesz:

- Megismerni a **Lemonade Server**-t
- **Telepíteni az OpenClaw-t**, és **beállítani, hogy a Lemonade Server-t** használja AI backendként.
- **Elindítani az OpenClaw gateway-t**, és megerősíteni, hogy az ügynöke készen áll a munkára.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármely eszközről beszélgethessen az ügynökével.

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
- Egy **Ubuntu 24.04+** rendszert futtató PC, vagy egy kompatibilis, Debian-alapú Linux disztribúció `apt-get` parancskezelővel
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcionális, az OpenClaw homokozó-környezetbe (sandbox) helyezéséhez)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
<!-- @os:end -->

<!-- @os:windows -->
- Egy **Windows 10/11** rendszert futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcionális, az OpenClaw homokozó-környezetbe (sandbox) helyezéséhez)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Az ajánlott modell letöltése és betöltése

Ehhez az útmutatóhoz az ajánlott modell a **Qwen3.6-35B-A3B-GGUF** az Unsloth-tól, egy erős MoE modell 263k tokenes kontextusablakkal, amely kiválóan alkalmas ügynöki munkaterhelésekhez. Ez a modell UD-Q4_K_XL kvantálást használ. Töltse le most:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ezután töltse be nagy kontextusablakkal, és mentse el ezt a beállítást a jövőbeli futtatásokhoz:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriahiányra (OOM) vonatkozó hibákba ütközik, érdemes csökkenteni a kontextusablakot. Mivel azonban a Qwen3.6 kibővített kontextust használ az összetett feladatokhoz, azt javasoljuk, hogy tartson meg legalább 128K tokenes kontextushosszt a gondolkodási képességek megőrzése érdekében.

> **Tipp: A gondolkodás kikapcsolása a gyorsabb ügynöki válaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést ad hozzá. Ügynöki munkafolyamatoknál ez a többletterhelés gyorsan felhalmozódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tároló egy kész konfigurációt biztosít, amely kikapcsolja a gondolkodást. A használatához töltse le a fájlt, és importálja:
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

Az OpenClaw-t WSL-en belül futtatjuk (ajánlott), és a natívan Windows alatt futó Lemonade-hez csatlakoztatjuk. Ez egy Linux parancssori környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### A WSL és az Ubuntu telepítése

Nyissa meg a PowerShell-t rendszergazdaként, és telepítse a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítse az Ubuntu-t:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése WSL-ben

Futtassa ezt az Ubuntu terminálban:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Lépjen ki a WSL-ből, és indítsa újra:

```powershell
exit
wsl --shutdown
wsl
```

### A Lemonade áthidalása Windowsból WSL-be

A WSL2 egy virtuális hálózatban fut. A Windows alatti Lemonade a `127.0.0.1` címre kötődik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows port proxy a forgalmat a WSL átjáró IP-címéről a Windows localhost felé irányítja.

**Keresse meg a WSL átjáró IP-címét** (futtassa WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adja hozzá a port proxyt** (futtassa rendszergazdaként PowerShell-ben, a `<WSL-Gateway-IP>` helyére a WSL átjáró IP-címét behelyettesítve):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Megjegyzés: Ha a `netsh: command not found` hibával találkozik, próbálja meg helyette az `netsh.exe` explicit végrehajtható nevet használni

**Adjon hozzá egy tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShell-ben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrizze a WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötte a Qwen3.6-35B-A3B-GGUF modellt, akkor a következőhöz hasonló JSON kimenetet kell látnia:

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

A `netsh portproxy` szabály túléli az újraindításokat, de a WSL gateway IP-je megváltozhat a `wsl --shutdown` parancs futtatása vagy egy újraindítás után. Ha ez megtörténik, a proxy továbbra is a régi IP-címre mutat, és a Lemonade elérhetetlenné válik a WSL-ből. Ha ez történik, használd az alábbi lehetőségek egyikét.

**1. lehetőség (ajánlott) — A híd automatikus javítása.** Hogy ezt ne kelljen minden alkalommal kézzel elvégezned, használj egy ütemezett feladatot, amely minden indításkor és bejelentkezéskor ellenőrzi a hidat, és csak akkor építi újra, ha a gateway IP megváltozott. Lásd a [Lemonade WSL híd automatikus javítási útmutatóját](assets/RepairLemonadeWslBridge.md).


**2. lehetőség — A híd manuális javítása.** Először szerezd meg az aktuális WSL gateway IP-t az alábbi parancs WSL-en belüli futtatásával:

```bash
ip route show default | awk '{print $3}' | head -1
```

Másold ki ezt az értéket; ezt fogod használni a `<new-WSL-Gateway-IP>` helyén az alábbiakban.

Ezután egy **emelt jogosultságú PowerShellben** (futtatás rendszergazdaként) sorold fel a meglévő szabályokat, töröld csak az elavult Lemonade szabályt, és adj hozzá egy újat az aktuális IP-vel:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

A `show all` kimenetében az elavult Lemonade szabály az a bejegyzés, amelynek a connect address értéke `127.0.0.1`, a `13305`-ös porton; a listen address a te `<old-WSL-Gateway-IP>` címed. Ha ezen cím alapján törölsz, csak ezt az egy szabályt távolítod el, a gépeden lévő összes többi port-proxy szabály érintetlen marad.

A beállítás során hozzáadott tűzfalszabály a `13305`-ös porthoz van kötve (nem az IP-hez), így az továbbra is működik, és nem kell újra létrehozni.

> **Javaslat:** A gateway-problémák elkerülése érdekében az alábbi parancshéj-konfigurációt javasoljuk:
> - A **Windows parancsokat** **PowerShellben** kell futtatni
> - A **WSL disztribúció parancsait** egy **parancssorban** (**Rendszergazdaként futtatva**) kell futtatni

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
> Az ebben a szakaszban szereplő parancsokat a **WSL terminálodon belül** futtasd.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-onboard` jelző kihagyja az interaktív beállítási varázslót, a modell háttérrendszerét a következő lépésben manuálisan konfigurálod, ami pontos irányítást biztosít afelett, hogy melyik modellt és szervert használod.

Nyiss egy új terminált, és erősítsd meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha a telepítés után `command not found` hibát látsz, add hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Hogy ez tartós legyen, add hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájlodhoz.

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

Futtasd az OpenClaw nem interaktív bevezetési folyamatát.
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

> **OpenClaw kontextusablak méretezése:** Az OpenClaw tömörítése (compaction) akkor indul el, amikor `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` értéke 20 000 token, ami egy alsó korlát (floor), amely felülírja a `reserveTokens` értéket, ha az alacsonyabb, így bármely ~37k alatti modell-kontextus végtelen tömörítési ciklust indít el. Állíts be egy alacsony reserve értéket, és kapcsold ki a floor-t egyszer a konfigurációdban, és ez minden modellre érvényes lesz, modellenkénti hangolás nélkül:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimum védelem), nem maga a reserve, csak az alsó korlát beállítása nincs hatással semmire. A `reserveTokensFloor: 0` kikapcsolja ezt a védelmet, így az alacsonyabb `reserveTokens` érték érvényesül.
>
> **Mikor alkalmazd ezt:** Használd ezt a konfigurációt, ha a modelled effektív kontextusablaka ~37k alatt van, akár azért, mert a modell kicsi (pl. 8k, 16k, 32k), akár azért, mert szándékosan alacsonyabb értékre korlátoztad (pl. egy 128k-s modellt töltesz be, de a kontextust 16k-ra állítod a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatod. Az alapértelmezett beállítások jól működnek, a tömörítés jóval azelőtt elindul, hogy az ablak megtelne, és a modellnek bőven van helye hosszú válaszok generálására. Ha mégis alkalmazod, vedd figyelembe, hogy a `reserveTokens: 4096` ~4k tokenre korlátozza a válasz hosszát, ami megszakíthatja a hosszú fájlgenerálást vagy a részletes terveket.
>
> **Hova add hozzá ezt:** Helyezd el a `compaction` blokkot az `agents.defaults` szakaszban az `openclaw.json` fájlodban (jellemzően a `~/.openclaw/openclaw.json` helyen):
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
> A konfigurációd többi része (gateway, channels, models stb.) változatlan marad, csak a `compaction` kulcsot kell hozzáadni.
### (Ajánlott) Docker sandboxing engedélyezése

Az OpenClaw képes az ügynök (agent) összes fájl- és kódműveletét egy izolált Docker konténeren keresztül irányítani ahelyett, hogy közvetlenül a hoszton futtatná azokat. Ez a nem szándékolt műveletek hatókörét a sandboxra korlátozza, így a hoszt fájlrendszere és hálózata érintetlen marad.

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

Futtasd ezt, hogy hozzáadd a `sandbox` kulcsot a meglévő `agents.defaults` blokkon belül a `~/.openclaw/openclaw.json` fájlban:

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

A sandbox konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A kötések (bind mounts) és a hálózati felülírások tekintetében lásd a [sandboxing referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker hozzáférés megtagadva
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

A [Firecrawl](https://docs.firecrawl.dev/introduction) egy önállóan üzemeltethető (self-hosted) webes feltérképezési és tartalomkinyerési szolgáltatást biztosít, amely képes áthidalni ezeket a kihívásokat, és kibontakoztatni az OpenClaw automatizálásban rejlő teljes potenciált.

Ebben a felállásban az OpenClaw Docker konténerek halmazaként fut, amelyeket Podman kezel. Az életciklus-kezelés és az automatikus indítás egyszerűsítése érdekében a Firecrawl-t felhasználói szintű `systemd` szolgáltatásként regisztráljuk, amely az alapul szolgáló Podman Compose stacket orkesztrálja. Ez lehetővé teszi, hogy az OpenClaw elindítsa az átjárót (gateway), leállítsa, és ellenőrizze a Firecrawl szolgáltatást standard `systemctl --user` parancsokkal, ahelyett hogy közvetlenül a konténerekkel kellene kommunikálnia.

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
Siker esetén a következő kimenetet kell látnod:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 A `default.target.wants/` könyvtár szimbolikus linkeket tartalmaz azokhoz a szolgáltatásokhoz, amelyek automatikus indításra vannak konfigurálva.

### 2. Firecrawl konfigurálása

A [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) azoknak ideális, akik teljes kontrollt szeretnének a scraping és adatfeldolgozási környezetük felett, de ez a kényelem további karbantartási és konfigurációs ráfordítással jár.

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

Mielőtt folytatnád, győződj meg róla, hogy letöltötted a legújabb OpenClaw Docker image-et:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ha ez megtörtént, töltsd le az OpenClaw Compose fájlt [openclaw-compose.yaml](assets/openclaw-compose.yaml), és helyezd el a gyökér `/firecrawl` könyvtárban:

> Ez a konvenció szükséges ahhoz, hogy a `systemd` megtalálja és megfelelően elindítsa a szolgáltatást, ahogy azt a `WorkingDirectory=${HOME}/firecrawl` beállítás megadja.

> A stacket bármikor bővítheted további Firecrawl szolgáltatások hozzáadásával, ahogy szükséges. Az elérhető szolgáltatások teljes listája megtalálható a hivatalos [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fájlban.

### 4. Az OpenClaw szolgáltatás elindítása a Firecrawl-on keresztül

Mielőtt átadnád az irányítást a `systemd`-nek, ellenőrizd, hogy minden megfelelően működik-e, a stack manuális futtatásával:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ha minden megfelelően van konfigurálva, látnod kell, hogy az OpenClaw konténer elindul, és a parancssori kimenetednek hasonlónak kell lennie ehhez:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Az ellenőrzés után állítsd le a stacket, mielőtt továbblépnél:
```bash
podman compose -f openclaw-compose.yaml down
```
A szolgáltatás elindítása előtt győződj meg róla, hogy a megfelelő tulajdonjog és jogosultságok be vannak állítva a `firecrawl` könyvtáron és annak `.env` fájlján.
Ez elengedhetetlen ahhoz, hogy a szolgáltatás induláskor írni tudja a hitelesítő adataidat.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Most, hogy minden ellenőrizve van, indítsd el a szolgáltatást a `systemd`-n keresztül:
```bash
systemctl --user start firecrawl.service
```
[Az OpenClaw Actions](https://docs.openclaw.ai/) elérhető az interaktív konténeren belülről, és a Web Dashboard ugyanazon a hoszton és porton érhető el a http://127.0.0.1:18789 címen.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Az `OPENCLAW_GATEWAY_TOKEN` beszerzése

Miután a szolgáltatás elindult és fut, egy új `.openclaw` könyvtárat fogsz találni a saját mappádban létrehozva (~/.openclaw). Ez a könyvtár alapértelmezés szerint zárolva van, így fel kell oldanod a zárolást a gateway tokened lekéréséhez.

1. Add meg a hozzáférést a könyvtárhoz:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Olvasd ki a gateway tokened:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Keresd meg az `OPENCLAW_GATEWAY_TOKEN` értéket a kimenetben.

3. Nyisd meg a gateway irányítópultot a böngésződben a http://127.0.0.1:18789 címen. Illeszd be a tokened, amikor hitelesítésre kér.

A szolgáltatás leállításához futtasd:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Az OpenClaw Gateway indítása

A gateway az az OpenClaw folyamat, amely kezeli az ügynökhurkot (agent loop), és kiszolgálja az irányítópultot:

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

Mivel a gateway a loopback-re kötődik, az irányítópult automatikusan hitelesít, ha ugyanarról a gépről nyitják meg, nincs szükség token megadására vagy eszközjóváhagyásra a helyi hozzáféréshez. Az OpenClaw irányítópultot kell látnod, amelyen a Lemonade modelled aktív háttérrendszerként szerepel.

> Ha engedélyezted a sandboxolást, ezt úgy ellenőrizheted, hogy az irányítópultról megkéred az ügynököt a `run hostname` futtatására. Ha a géped gazdaneve helyett egy rövid konténer-azonosítót látsz, a sandbox megfelelően működik.

**Gratulálunk, teljesen helyi AI-ügynökstruktúrát építettél fel a nulláról.**

> **Szükséged van a gateway tokenre?** Futtasd a `openclaw dashboard --no-open` parancsot, hogy kiírja az irányítópult URL-jét a beágyazott tokennel (emellett megpróbálja azt a vágólapra is másolni). Alternatívaként a token a `gateway.auth.token` alatt található a `~/.openclaw/openclaw.json` fájlban.

**Az irányítópult elérése másik eszközről (SSH alagúton keresztül)**

Ha az OpenClaw egy távoli gépen fut, az irányítópultot a helyi géped SSH alagúton keresztül érheti el. Az alagút továbbítja a gateway portot (`18789`), így a helyi böngésződ a `127.0.0.1` címen keresztül kommunikálhat a távoli gateway-jel.

1. A **helyi gépedről** kapcsolódj egyszer a távoli géphez, és fogadd el az ujjlenyomat-kérést, hogy a host bekerüljön az ismert hostok közé:

   ```bash
   ssh user@<host-ip>
   ```

2. Még mindig a **helyi gépeden**, nyisd meg az SSH alagutat:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Megjegyzés:** A jelszó megadása után a terminál nem mutat semmilyen kimenetet, és úgy tűnik, lefagyott. Ez normális: a `-N` jelző utasítja az SSH-t, hogy ne futtasson semmilyen távoli parancsot, így egyszerűen nyitva tartja az alagutat. Hagyd futni ezt a terminált.

3. A **helyi gépeden** nyiss meg egy böngészőt, és navigálj a `http://127.0.0.1:18789` címre.

4. A **távoli gépen** írasd ki a gateway tokent, és illeszd be a böngészőbe a bejelentkezéshez:

   ```bash
   openclaw dashboard --no-open
   ```

   Ez kiírja az irányítópult URL-jét a beágyazott tokennel; másold ki a tokent a bejelentkezéshez. (A token a `gateway.auth.token` alatt is tárolva van a `~/.openclaw/openclaw.json` fájlban.)

> **Távoli eszköz jóváhagyása:** Amikor egy másik gépről vagy telefonról nyitod meg az irányítópultot, a böngésző megjeleníthet egy kéréskonódot. A **távoli gépen** listázd ki a függőben lévő kéréseket:
> ```bash
> openclaw devices list
> ```
> Majd hagyd jóvá a megfelelő kérést:
> ```bash
> openclaw devices approve <requestId>
> ```
> Erre csak távoli vagy másodlagos eszközök esetén van szükség; az ugyanarról a gépről történő loopback hozzáférés automatikusan hitelesít. A részletekért lásd a [Remote Access](https://docs.openclaw.ai/gateway/remote) dokumentációt.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Ha a gateway fut, bármely eszközről elérheted a helyi ügynöködet. Válaszd ki a beállításaidnak megfelelő lehetőséget. Az OpenClaw támogatja a [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) és egyéb csatornákat, a teljes listát lásd itt: [docs.openclaw.ai](https://docs.openclaw.ai).

---

### A opció: Discord

A Discordhoz szükséged van egy olyan szerverre, ahol **rendelkezel adminisztrátori hozzáféréssel**, hogy botot adhass hozzá. Ha szervereket osztasz meg másokkal, de nem te vagy a tulajdonos, használd inkább a B opciót (Telegram).

#### Discord fiók és szerver létrehozása

Ha nincs Discord fiókod, regisztrálj a [discord.com](https://discord.com) oldalon. Szükséged van egy szerverre is, ahol adminisztrátor vagy; hozz létre egyet a Discord oldalsávjában található **+** ikonra kattintva, majd válaszd a **Create My Own** lehetőséget. Egy privát szerver is megfelelő.

#### Discord alkalmazás és bot létrehozása

1. Menj a [Discord Developer Portal](https://discord.com/developers/applications) oldalra, és kattints a **New Application** gombra. Adj neki egy nevet (pl. „openclaw-bot”).
2. Az oldalsávban kattints a **Bot** elemre. Állíts be egy felhasználónevet a botnak.
3. Még mindig a Bot oldalon, görgess le a **Privileged Gateway Intents** részhez, és engedélyezd:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgess vissza felfelé, és kattints a **Reset Token** gombra a bot tokenjének generálásához. Másold ki.

#### A bot hozzáadása a szerveredhez

1. Az oldalsávban kattints az **OAuth2/ URL Generator** elemre.
2. A **Scopes** alatt engedélyezd a `bot` és `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezd: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másold ki a generált URL-t, illeszd be a böngésződbe, válaszd ki a szerveredet, és erősítsd meg. A botnak most már meg kell jelennie a szerver tagjainak listájában.

#### Azonosítók begyűjtése

Engedélyezd a Fejlesztői módot a Discordban (**User Settings/ Advanced/ Developer Mode**), majd:
- Kattints jobb gombbal a szerver ikonjára: **Copy Server ID**
- Kattints jobb gombbal a saját avatárodra: **Copy User ID**

#### Privát üzenetek engedélyezése a szerver tagjaitól

Kattints jobb gombbal a szerver ikonjára/ **Privacy Settings**/ kapcsold be a **Direct Messages** opciót. Ez lehetővé teszi, hogy a bot privát üzenetet küldjön neked, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárold a bot tokenjét környezeti változóként, majd hozz létre egyetlen patch fájlt, amely engedélyezi a Discordot, hivatkozik a tokenre, és engedélyezőlistára veszi a szervered. Cseréld ki a `<server_id>` és `<user_id>` értékeket a fent begyűjtött azonosítókra.

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

> **Ne hagyatkozz arra, hogy megkéred az ügynököt ennek beállítására.** Ha a sandboxolás engedélyezve van, az ügynök nem tud írni a `~/.openclaw/openclaw.json` fájlba a sandboxon belülről, ehelyett használd a fenti CLI parancsokat a hoszton.

Indítsd újra a gateway-t, hogy átvegye az új csatornakonfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül meg kell jelennie a `logged in to discord as <bot-name>` üzenetnek a gateway kimenetében.
#### Párosítsd a Discord fiókodat

Küldj DM-et a botnak Discordon. A bot válaszként küld egy rövid párosítási kódot.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyd jóvá azon a gépen, amelyiken az OpenClaw fut:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Mostantól közvetlenül Discordból is cseveghetsz az ügynököddel, és feladatokat delegálhatsz a helyi hardverednek.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb, mint a Discord, nincs szükség sem szerverre, sem admin hozzáférésre.

#### Hozz létre egy Telegram botot

1. Nyisd meg a Telegramot, és küldj üzenetet a **@BotFather**-nek.
2. Küldd el a `/newbot` parancsot, és kövesd az utasításokat. Mentsd el a kapott bot tokent.

#### Állítsd be az OpenClaw-t Telegramhoz

Tárold a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add hozzá a csatorna konfigurációját a `~/.openclaw/openclaw.json` fájlhoz (vagy frissítsd a dashboardon keresztül):

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

Indítsd újra a gatewayt, majd küldj a botodnak bármilyen üzenetet Telegramon. Hagyd jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Mostantól Telegram DM-en keresztül is cseveghetsz az ügynököddel.

---

## Következő lépések

Most, hogy az ügynököd képes parancsokat fogadni a telefonodról és ezeket végrehajtani a helyi gépeden, íme három érdemes irány, amelyet érdemes megfontolni:

1. **Tőzsdei összefoglaló**: Ütemezd be az OpenClaw-t, hogy rendszeres időközönként adatokat kérjen le pénzügyi API-kból, foglalja össze a nap mozgásait a helyi modelleddel, és küldjön egy kivonatot a telefonodra minden reggel a választott csatornán keresztül.

2. **Finomhangolás monitor**: Indíts el egy tanítási feladatot távolról Telegramon vagy Discordon, majd hagyd, hogy az ügynök kövesse a tanítási naplót, és rendszeresen jelentse a veszteségértékeket, a GPU-kihasználtságot és a lemezhasználatot a telefonodra. Ha a futás leáll, vagy a VRAM-használat megugrik, azonnal értesülsz róla, anélkül, hogy a gépnél kellene lenned.

3. **IOT helyi VLM-mel**: Irányíts egy kamerát a bejárati ajtódra, futtass egy látásmodellt Lemonade-en, és hagyd, hogy az OpenClaw igény szerint vagy egy kiváltó esemény alapján elemezze a képkockákat. Kérdezd meg a telefonodról, hogy „érkezett ma valamilyen csomag?”, és kapj egyenes választ a saját hardveredtől.

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