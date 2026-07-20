<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Az OpenClaw futtatása Lemonade Serverrel háttérrendszerként

## Áttekintés

Az [**OpenClaw**](https://openclaw.ai/) egy autonóm AI-ügynök, amely kódot tud írni és futtatni, fájlokat tud kezelni, és komplex, több lépésből álló feladatokat tud elvégezni Ön helyett. Egy chatalkalmazással ellentétben, amely csak kérdésekre válaszol, az OpenClaw valós műveleteket hajt végre a rendszerén, ami azt jelenti, hogy gyors, képes AI háttérrendszerre van szüksége, amely lépést tud tartani egy igényes ügynöki ciklussal.

A [**Lemonade Server**](https://lemonade-server.ai/) éppen egy ilyen háttérrendszer. Ez egy nyílt forráskódú, helyi következtetési kiszolgáló, amely közvetlenül az Ön hardverén futtatja a GenAI modelleket, és iparági szabványnak számító OpenAI API-n keresztül teszi elérhetővé őket.

Együtt egy teljesen helyi AI-ügynöki csomagot alkotnak: a Lemonade végzi a modell-következtetést, az OpenClaw pedig biztosítja azt az ügynöki ciklust, amely a modell kimeneteit valós műveletekké alakítja.

> **Mielőtt folytatná:** Az OpenClaw egy rendkívül autonóm AI-ügynök. Ha bármely AI-ügynöknek hozzáférést biztosít a rendszeréhez, az kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytassa, ha megérti a kockázatokat, és elfogadja, hogy autonóm szoftver cselekszik Ön helyett.

---

## Amit meg fog tanulni

E útmutató végére képes lesz:

- Megismerkedni a **Lemonade Server**-rel
- **Telepíteni az OpenClaw-t**, és **beállítani, hogy a Lemonade Servert** használja AI háttérrendszerként.
- **Elindítani az OpenClaw gateway-t**, és megerősíteni, hogy az ügynöke készen áll a munkára.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármely eszközről cseveghessen az ügynökével.

---

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## A szoftveres előfeltételek telepítése

<!-- @os:linux -->
- Egy **Ubuntu 24.04+**-t vagy egy kompatibilis, Debian alapú, `apt-get`-et használó Linux disztribúciót futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcionális, az OpenClaw sandboxolásához)

- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
<!-- @os:end -->
<!-- @os:windows -->
- Egy **Windows 10/11**-et futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opcionális, az OpenClaw sandboxolásához)
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

Az ehhez az útmutatóhoz ajánlott modell a **Qwen3.6-35B-A3B-GGUF**, amelyet az Unsloth készített; ez egy erős MoE modell 263k tokenes kontextusablakkal, amely jól illeszkedik az ügynöki feladatokhoz. Ez a modell UD-Q4_K_XL kvantálást használ. Töltse le most:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ezután töltse be nagy kontextusablakkal, és mentse el ezt a beállítást a jövőbeli futtatásokhoz:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriahiányból (OOM) adódó hibákat tapasztal, fontolja meg a kontextusablak csökkentését. Mivel azonban a Qwen3.6 a bővített kontextust használja a komplex feladatokhoz, azt javasoljuk, hogy tartson meg legalább 128K tokenes kontextushosszt a gondolkodási képességek megőrzése érdekében.

> **Tipp: A gondolkodás kikapcsolása a gyorsabb ügynöki válaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést okoz. Ügynöki ciklusok esetén ez a többletidő gyorsan felhalmozódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tárolóban található egy előre elkészített konfiguráció, amely kikapcsolja a gondolkodást. A használatához töltse le a fájlt, és importálja:
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

Az OpenClaw-t a WSL-en belül (ajánlott) futtatjuk, és a natívan Windowson futó Lemonade-hez csatlakoztatjuk. Ez egy Linux shell környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### A WSL és az Ubuntu telepítése

Nyissa meg a PowerShellt rendszergazdaként, és telepítse a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítse az Ubuntu-t:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése a WSL-ben

Futtassa ezt az Ubuntu terminálon belül:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Indítsa újra a WSL-t:

```powershell
wsl --shutdown
wsl
```

### A Lemonade áthidalása a Windowsból a WSL-be

A WSL2 egy virtuális hálózatban fut. A Windowson futó Lemonade a `127.0.0.1`-hez kötődik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows port proxy továbbítja a forgalmat a WSL átjáró IP-címéről a Windows localhostjára.

**Keresse meg a WSL átjáró IP-címét** (futtassa a WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adja hozzá a port proxyt** (futtassa PowerShellben rendszergazdaként, cserélje ki a `<WSL-Gateway-IP>`-t a saját WSL átjáró IP-címére):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adjon hozzá egy tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShellben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrizze a WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötte a Qwen3.6-35B-A3B-GGUF modellt, akkor ehhez hasonló JSON-kimenetet kell látnia:

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

> A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-címe megváltozhat a `wsl --shutdown` után. Ha a Lemonade újraindítás után elérhetetlenné válik a WSL-ből, kérje le a frissített átjáró IP-címet, és frissítse vele a proxyt.

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

## Az OpenClaw telepítése és beállítása

### Az OpenClaw telepítése
<!-- @os:windows -->
> A parancsokat ebben a szakaszban a **WSL terminálján** belül futtassa.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-onboard` jelölő kihagyja az interaktív beállítási varázslót; a modell háttérrendszert manuálisan fogja beállítani a következő lépésben, ami pontos irányítást biztosít afölött, hogy melyik modell és melyik szerver kerüljön felhasználásra.

Nyisson meg egy új terminált, és erősítse meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha a telepítés után `command not found` üzenetet lát, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ahhoz, hogy ez véglegessé váljon, adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájljához.

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

Futtassa le az OpenClaw nem interaktív bevezető beállítását.
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

> **OpenClaw kontextusablak méretezése:** Az OpenClaw tömörítése (compaction) akkor indul el, amikor `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` érték 20 000 token, ez egy alsó korlát, amely felülírja a `reserveTokens` értéket, ha az alacsonyabb, így minden ~37k alatti modellkontextus végtelen tömörítési ciklust indít el. Állítson be egy alacsony tartalékot (reserve), és tiltsa le az alsó korlátot egyszer a konfigurációban, és ez minden modellre érvényes lesz, nincs szükség modellenkénti beállításra:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimum védelem), nem maga a tartalék, ha csak az alsó korlátot állítja be, annak nincs hatása. A `reserveTokensFloor: 0` letiltja a védelmet, így az alacsonyabb `reserveTokens` érték érvényesül.
>
> **Mikor alkalmazza ezt:** Használja ezt a konfigurációt, ha a modell tényleges kontextusablaka ~37k alatt van, akár azért, mert a modell kicsi (pl. 8k, 16k, 32k), akár azért, mert szándékosan alacsonyabb értékre korlátozta (pl. egy 128k-s modell betöltése, de a kontextus 16k-ra állítása a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatja. Az alapértelmezett beállítások jól működnek, a tömörítés jóval azelőtt beindul, hogy az ablak megtelne, és a modellnek bőven van hely hosszú válaszok generálásához. Ha mégis alkalmazza, vegye figyelembe, hogy a `reserveTokens: 4096` a válasz hosszát ~4k tokenre korlátozza, ami megszakíthatja a hosszú fájlgenerálást vagy a részletes terveket.
>
> **Hova adja hozzá:** Helyezze el a `compaction` blokkot az `agents.defaults` szakaszon belül az `openclaw.json` fájlban (általában a `~/.openclaw/openclaw.json` alatt):
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

### (Ajánlott) A Docker homokozó (sandboxing) engedélyezése

Az OpenClaw képes az ügynök összes fájl- és kódműveletét egy elkülönített Docker konténeren keresztül irányítani, ahelyett hogy közvetlenül a gépen futtatná őket. Ez a nem kívánt műveletek hatókörét a homokozóra korlátozza, így a gép fájlrendszere és hálózata érintetlen marad.

Építse meg egyszer a homokozó image-et (a Docker telepítve kell legyen):

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

Futtassa ezt a `sandbox` kulcs hozzáadásához a meglévő `agents.defaults` blokkon belül a `~/.openclaw/openclaw.json` fájlban:

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

A homokozó konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A bind mountokért és hálózati felülbírálásokért lásd a [sandboxing referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker hozzáférés megtagadva
> 
> Ha „permission denied” hibát kap Docker parancsok futtatásakor:
> 
> **1. lépés: Adja hozzá felhasználóját a docker csoporthoz**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **2. lépés: Ha a hiba továbbra is fennáll, alkalmazza a végleges javítást**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Ezután **indítsa újra** a rendszert.
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

### Az OpenClaw gateway indítása

A gateway az az OpenClaw folyamat, amely kezeli az ügynök hurkot (agent loop) és kiszolgálja az irányítópultot:

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

Az irányítópult megnyitásához futtassa ezt egy második terminálban, amíg a gateway továbbra is fut:

```bash
openclaw dashboard
```

Mivel a gateway a loopback címre kapcsolódik, az irányítópult automatikusan hitelesít, amikor ugyanarról a gépről nyitja meg, nincs szükség tokenbeírásra vagy eszközjóváhagyásra a helyi hozzáféréshez. Az OpenClaw irányítópultot kell látnia, amelyen a Lemonade modell szerepel aktív háttérrendszerként.

> Ha engedélyezte a homokozót, ellenőrizheti azt úgy, hogy megkéri az ügynököt a `run hostname` parancs futtatására az irányítópultról. Ha rövid konténerazonosítót lát a gép hosztneve helyett, a homokozó működik.

**Gratulálunk, egy teljesen helyi AI-ügynök architektúrát épített fel a semmiből.**

> **Szüksége van a gateway tokenre?** Futtassa a `openclaw dashboard --no-open` parancsot, hogy kiírja az irányítópult URL-jét a beágyazott tokennel (emellett megpróbálja vágólapra másolni). Alternatívaként a token a `gateway.auth.token` alatt található a `~/.openclaw/openclaw.json` fájlban.
>
> **Távoli eszköz jóváhagyása:** Amikor egy második gépről vagy telefonról nyitja meg az irányítópultot, a böngésző megjelenít egy kérésazonosítót. A gateway-t futtató gépen futtassa:
> ```bash
> openclaw devices approve <requestId>
> ```
> Erre csak távoli vagy másodlagos eszközök esetén van szükség, a loopback hozzáférés ugyanarról a gépről automatikusan hitelesít.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Amint a gateway fut, bármilyen eszközről elérheti a helyi ügynökét. Válassza ki a beállításának megfelelő lehetőséget. Az OpenClaw támogatja a [Discord](https://docs.openclaw.ai/channels/discord), a [Telegram](https://docs.openclaw.ai/channels/telegram) és más csatornákat, a teljes listát a [docs.openclaw.ai](https://docs.openclaw.ai) oldalon találja.

---

### A lehetőség: Discord

A Discordhoz olyan szerver szükséges, ahol **rendszergazdai hozzáféréssel** rendelkezik a bot hozzáadásához. Ha megosztott szervereken van jelen, de nincs sajátja, használja inkább a B lehetőséget (Telegram).
#### Hozz létre egy Discord-fiókot és -szervert

Ha nincs Discord-fiókod, regisztrálj a [discord.com](https://discord.com) oldalon. Szükséged lesz egy szerverre is, amelyen adminisztrátor vagy, hozz létre egyet a **+** ikonra kattintva a Discord oldalsávjában, majd válaszd a **Create My Own** lehetőséget. Egy privát szerver is megfelel.

#### Hozz létre egy Discord alkalmazást és botot

1. Menj a [Discord Developer Portal](https://discord.com/developers/applications) oldalra, és kattints a **New Application** gombra. Adj neki egy nevet (pl. „openclaw-bot").
2. Az oldalsávban kattints a **Bot** menüpontra. Állíts be egy felhasználónevet a botnak.
3. Még a Bot oldalon görgess le a **Privileged Gateway Intents** részhez, és engedélyezd:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgess vissza felfelé, és kattints a **Reset Token** gombra a bot tokenjének generálásához. Másold ki.

#### Add hozzá a botot a szerveredhez

1. Az oldalsávban kattints az **OAuth2/ URL Generator** menüpontra.
2. A **Scopes** alatt engedélyezd a `bot` és az `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezd: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másold ki a generált URL-t, illeszd be a böngésződbe, válaszd ki a szervered, és erősítsd meg. A botnak ezután meg kell jelennie a szerver tagjai listájában.

#### Gyűjtsd össze az azonosítóidat

Kapcsold be a Fejlesztői módot a Discordban (**User Settings/ Advanced/ Developer Mode**), majd:
- Kattints jobb gombbal a szerver ikonjára: **Copy Server ID**
- Kattints jobb gombbal a saját avatarodra: **Copy User ID**

#### Engedélyezd a DM-eket a szerver tagjaitól

Kattints jobb gombbal a szerver ikonjára/ **Privacy Settings**/ kapcsold be a **Direct Messages** opciót. Ez lehetővé teszi, hogy a bot DM-et küldjön neked, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárold a bot tokenedet környezeti változóként, majd hozz létre egyetlen patch fájlt, amely bekapcsolja a Discordot, hivatkozik a tokenre, és engedélyezőlistára veszi a szerveredet. Cseréld le a `<server_id>` és `<user_id>` értékeket a fent összegyűjtött azonosítókra.

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

> **Ne bízd ennek konfigurálását az ügynökre.** Ha a sandboxolás engedélyezve van, az ügynök nem tud írni a `~/.openclaw/openclaw.json` fájlba a sandboxon belülről, ehelyett használd a fenti CLI parancsokat a hoszton.

Indítsd újra a gateway-t, hogy felvegye az új csatorna konfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül meg kell jelennie a `logged in to discord as <bot-name>` üzenetnek a gateway kimenetében.

#### Párosítsd a Discord-fiókodat

Küldj DM-et a botnak a Discordban. Válaszul egy rövid párosítási kódot fog küldeni.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyd jóvá azon a gépen, amelyen az OpenClaw fut:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Mostantól közvetlenül a Discordból tudsz csevegni az ügynököddel, és feladatokat tudsz áthelyezni a helyi hardveredre.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb, mint a Discord, nem igényel szervert és admin jogosultságot sem.

#### Hozz létre egy Telegram botot

1. Nyisd meg a Telegramot, és küldj üzenetet a **@BotFather**-nek.
2. Küldd el a `/newbot` parancsot, és kövesd az utasításokat. Mentsd el a kapott bot tokent.

#### Az OpenClaw konfigurálása Telegramhoz

Tárold a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add hozzá a csatorna konfigurációját a `~/.openclaw/openclaw.json` fájlhoz (vagy javítsd a dashboardon keresztül):

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

Indítsd újra a gateway-t, majd küldj bármilyen üzenetet a botodnak Telegramon. Hagyd jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Mostantól csevegni tudsz az ügynököddel a Telegram DM-en keresztül.

---

## Következő lépések

Most, hogy az ügynököd parancsokat tud fogadni a telefonodról, és cselekedni tud a helyi gépeden, íme három irány, amelyet érdemes felfedezni:

1. **Tőzsdei összefoglaló**: Ütemezd be az OpenClaw-t, hogy fix időközönként adatokat kérjen le pénzügyi API-któl, foglalja össze a nap mozgásait a helyi modelleddel, és küldjön egy összefoglalót a telefonodra minden reggel a választott csatornán keresztül.

2. **Finomhangolás-monitor**: Indíts el egy tanítási feladatot távolról Telegramon vagy Discordon keresztül, majd az ügynök kövesse a tanítási naplót, és jelentse vissza időszakosan a veszteségértékeket, a GPU-kihasználtságot és a lemezhasználatot a telefonodra. Ha a futás leáll vagy a VRAM megugrik, azonnal értesülsz róla anélkül, hogy a gépnél kellene lenned.

3. **IOT helyi VLM-mel**: Irányíts egy kamerát a bejárati ajtódra, futtass egy vizuális modellt a Lemonade-en, és hagyd, hogy az OpenClaw kérésre vagy triggerre elemezze a képkockákat. Kérdezd meg „érkezett ma bármilyen csomag?" a telefonodról, és kapj egyértelmű választ a saját hardveredről.