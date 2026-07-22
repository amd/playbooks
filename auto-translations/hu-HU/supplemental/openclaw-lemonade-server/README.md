<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# OpenClaw futtatása a Lemonade Server backendjével

## Áttekintés

A [**OpenClaw**](https://openclaw.ai/) egy autonóm AI ügynök, amely kódot tud írni és futtatni, fájlokat tud kezelni, és összetett, több lépésből álló feladatokat tud elvégezni Ön helyett. A puszta kérdés-válasz chat asszisztensekkel ellentétben az OpenClaw valódi műveleteket hajt végre a rendszeren, ami azt jelenti, hogy gyors, képes AI backendre van szüksége, amely lépést tud tartani egy igényes ügynöki (agent) hurokkal.

A [**Lemonade Server**](https://lemonade-server.ai/) ez a backend. Nyílt forráskódú, helyi következtetési (inference) szerver, amely GenAI modelleket futtat közvetlenül az Ön hardverén, és az iparági szabványnak számító OpenAI API-n keresztül teszi őket elérhetővé.

Együtt egy teljesen helyi AI ügynök-stacket alkotnak: a Lemonade végzi a modell-következtetést, az OpenClaw pedig biztosítja azt az ügynöki hurkot, amely a modell kimeneteit valódi műveletekké alakítja.

> **Mielőtt folytatná:** Az OpenClaw egy erősen autonóm AI ügynök. Bármely AI ügynöknek a rendszerhez való hozzáférés biztosítása kiszámíthatatlan vagy nem szándékolt eredményekhez vezethet. Csak akkor folytassa, ha megérti a kockázatokat, és elfogadja, hogy autonóm szoftver cselekszik az Ön nevében.

---

## Amit meg fog tanulni

Ennek a segédletnek a végére Ön képes lesz:

- Megismerni a **Lemonade Server**-t
- **Telepíteni az OpenClaw-ot**, és **beállítani, hogy a Lemonade Server-t** használja AI backendként.
- **Elindítani az OpenClaw gateway-t**, és megerősíteni, hogy az ügynöke készen áll a munkára.
- **Csatlakoztatni egy kommunikációs csatornát** (Discord vagy Telegram), hogy bármely eszközről cseveghessen az ügynökével.

---

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftverelőfeltételek telepítése

<!-- @os:linux -->
- Egy **Ubuntu 24.04+** rendszert futtató PC, vagy egy kompatibilis, Debian-alapú Linux disztribúció `apt-get` paranccsal
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opcionális, az OpenClaw sandboxolásához)

- **~10–30 GB szabad lemezterület** a modellsúlyok számára
<!-- @os:end -->
<!-- @os:windows -->
- Egy **Windows 10/11** rendszert futtató PC
- Legalább **12 GB RAM** (nagyobb modellekhez 64 GB+ ajánlott)
- **~10–30 GB szabad lemezterület** a modellsúlyok számára
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

## Ajánlott modell letöltése és betöltése

Ehhez a segédlethez az ajánlott modell a **Qwen3.6-35B-A3B-GGUF** az Unsloth-tól, egy erős MoE modell 263k tokenes kontextusablakkal, amely jól illeszkedik az ügynöki munkaterhelésekhez. Ez a modell UD-Q4_K_XL kvantálást használ. Töltse le most:

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

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriakifogyási (OOM) hibákkal találkozik, fontolja meg a kontextusablak csökkentését. Mivel azonban a Qwen3.6 kiterjesztett kontextust használ az összetett feladatokhoz, azt javasoljuk, hogy tartson meg legalább 128K tokenes kontextushosszt a gondolkodási képességek megőrzése érdekében.

> **Tipp: A gondolkodás kikapcsolása gyorsabb ügynökválaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést okoz. Ügynöki hurkoknál ez a többletidő gyorsan összeadódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) repó egy kész konfigurációt biztosít, amely kikapcsolja a gondolkodást. A használatához töltse le a fájlt, és importálja:
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

Az OpenClaw-ot WSL-en belül futtatjuk (ajánlott), és a Windows-on natívan futó Lemonade-hez csatlakoztatjuk. Ez egy Linux shell környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### WSL és Ubuntu telepítése

Nyisson meg egy PowerShell ablakot rendszergazdaként, és telepítse a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítse az Ubuntu-t:

```powershell
wsl --install -d Ubuntu-24.04
```

### systemd engedélyezése WSL-ben

Futtassa ezt az Ubuntu terminálban:

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

### A Lemonade áthidalása Windowsból WSL-be

A WSL2 egy virtuális hálózatban fut. A Windows-on futó Lemonade a `127.0.0.1` címhez kötődik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows-os port-proxy továbbítja a forgalmat a WSL átjáró IP-címéről a Windows localhost-ra.

**Keresse meg a WSL átjáró IP-címét** (futtassa a WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adja hozzá a port-proxy-t** (futtassa PowerShell-ben rendszergazdaként, cserélje ki a `<WSL-Gateway-IP>` helyét a saját WSL átjáró IP-címére):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adjon hozzá egy tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShell-ben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrizze WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötte a Qwen3.6-35B-A3B-GGUF modellt, akkor egy ehhez hasonló JSON kimenetet kell látnia:

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

> A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-címe megváltozhat a `wsl --shutdown` után. Ha a Lemonade nem érhető el a WSL-ből egy újraindítás után, kérje le a frissített átjáró IP-címet, és frissítse a proxy-t ezzel az új IP-vel.

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
> Az ebben a szakaszban szereplő parancsokat a **WSL terminálon** belül futtassa.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-onboard` jelző kihagyja az interaktív telepítővarázslót; a modell backendet a következő lépésben manuálisan fogja beállítani, ami pontos irányítást biztosít afölött, hogy melyik modell és szerver kerül felhasználásra.

Nyisson meg egy új terminált, és erősítse meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha telepítés után a `command not found` üzenetet látja, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ennek tartóssá tételéhez adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájljához.

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

Futtassa le az OpenClaw nem interaktív bevezető (onboarding) folyamatát.
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

Ez a parancs az OpenClaw konfigurációját a `~/.openclaw/openclaw.json` fájlba írja.

> **Az OpenClaw kontextusablak méretezése:** Az OpenClaw tömörítése (compaction) akkor indul el, amikor `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` érték 20 000 token, ami egy alsó korlát, és felülírja a `reserveTokens` értékét, ha annál kisebb, így minden olyan modell, amelynek kontextusa ~37k alatt van, végtelen tömörítési ciklusba kerül. Állítson be egy alacsony tartalékértéket, és kapcsolja ki az alsó korlátot egyszer a konfigurációban, és ez minden modellre érvényes lesz, modellenkénti hangolásra nincs szükség:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimum védőérték), nem maga a tartalék, ha csak ezt az értéket állítja be, annak nincs hatása. A `reserveTokensFloor: 0` kikapcsolja a védelmet, így az alacsonyabb `reserveTokens` érték érvényesül.
>
> **Mikor alkalmazza ezt:** Használja ezt a konfigurációt, ha a modell tényleges kontextusablaka ~37k alatt van, akár azért, mert a modell kicsi (pl. 8k, 16k, 32k), akár mert szándékosan alacsonyabb értékre korlátozta (pl. egy 128k modellt tölt be, de a kontextust 16k-ra állítja a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatja. Az alapértelmezett beállítások megfelelően működnek, a tömörítés jóval azelőtt beindul, hogy az ablak megtelne, és a modellnek bőven van hely hosszú válaszok generálására. Ha mégis alkalmazza, vegye figyelembe, hogy a `reserveTokens: 4096` a válasz hosszát ~4k tokenre korlátozza, ami megszakíthatja a hosszú fájlgenerálást vagy a részletes terveket.
>
> **Hova adja hozzá:** Helyezze a `compaction` blokkot az `agents.defaults` szakaszon belülre az `openclaw.json` fájlban (általában a `~/.openclaw/openclaw.json` helyen):
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

Az OpenClaw képes az ágens összes fájl- és kódműveletét egy elkülönített Docker konténeren keresztül irányítani, ahelyett hogy közvetlenül a gazdagépen futtatná azokat. Ez a nem kívánt műveletek hatókörét a sandboxra korlátozza, a gazdagép fájlrendszerét és hálózatát pedig érintetlenül hagyja.

Építse fel egyszer a sandbox image-et (a Dockernek telepítve kell lennie):

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

A sandbox konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A bind mount-okkal és hálózati felülírásokkal kapcsolatban lásd a [sandboxing referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker jogosultság megtagadva
> 
> Ha "permission denied" hibaüzenetet kap Docker parancsok futtatásakor:
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
> **Gyors, ideiglenes megoldás** (újraindítás után visszaáll):
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

A [Firecrawl](https://docs.firecrawl.dev/introduction) egy önállóan üzemeltetett webes tartalomkinyerő és -bejáró szolgáltatást biztosít, amely képes megkerülni ezeket a problémákat, és kihasználni az OpenClaw automatizálásban rejlő teljes potenciált.

Ebben a konfigurációban az OpenClaw Docker konténerek egy csoportjaként fut, amelyeket Podman kezel. Az életciklus-kezelés és az automatikus indítás egyszerűsítése érdekében a Firecrawl-t felhasználói szintű `systemd` szolgáltatásként regisztráljuk, amely vezérli az alatta lévő Podman Compose stacket. Ez lehetővé teszi, hogy az OpenClaw a szabványos `systemctl --user` parancsokkal indítsa el a gateway-t, állítsa le és ellenőrizze a Firecrawl szolgáltatást, ahelyett hogy közvetlenül a konténerekkel kellene interakcióba lépnie.

Az egyszerűség kedvéért a teljes folyamatot négy lépésre bontottuk:

---

### 1. A rendszerszolgáltatás regisztrálása
Navigáljon a systemd felhasználói konfigurációs könyvtárba:
```bash
cd ~/.config/systemd/user
```
Hozzon létre és nyisson meg egy új fájlt `firecrawl.service` néven.
```bash
nano firecrawl.service
```
Másolja be és illessze be a következő konfigurációt:
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
Győződjön meg róla, hogy a fájlnév pontosan megegyezik a fent létrehozottal, majd futtassa a következőt:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ha sikeres volt, a következő kimenetet kell látnia:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 A `default.target.wants/` szimbolikus linkeket tartalmaz azokra a szolgáltatásokra, amelyek automatikus indításra vannak konfigurálva.
### 2. A Firecrawl konfigurálása

A [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) azoknak ideális, akiknek teljes kontrollra van szükségük a scraping és adatfeldolgozási környezeteik felett, cserébe azonban ez további karbantartási és konfigurációs feladatokkal jár.

Kezdje a repository klónozásával:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Hozzon létre egy `.env` fájlt a gyökér `/firecrawl` könyvtárban: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Az OpenClaw telepítése Podman Compose segítségével

Mielőtt tovább lép, győződjön meg róla, hogy letöltötte a legújabb OpenClaw Docker image-et:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ezután töltse le az OpenClaw Compose fájlt: [openclaw-compose.yaml](assets/openclaw-compose.yaml), és helyezze el a gyökér `/firecrawl` könyvtárban:

> Erre a konvencióra azért van szükség, hogy a `systemd` megfelelően megtalálja és el tudja indítani a szolgáltatást, a `WorkingDirectory=${HOME}/firecrawl` beállításnak megfelelően.

> A stack-et bármikor bővítheti további Firecrawl szolgáltatások hozzáadásával, igény szerint. Az elérhető szolgáltatások teljes listája megtalálható a hivatalos [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fájlban.

### 4. Az OpenClaw szolgáltatás elindítása a Firecrawl-on keresztül 

Mielőtt átadná az irányítást a `systemd`-nek, ellenőrizze, hogy minden megfelelően működik, a stack manuális futtatásával:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ha minden megfelelően van konfigurálva, akkor az OpenClaw konténernek el kell indulnia, és a parancssori kimenetnek nagyjából így kell kinéznie:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Az ellenőrzés után állítsa le a stack-et, mielőtt továbblépne:
```bash
podman compose -f openclaw-compose.yaml down
```
A szolgáltatás elindítása előtt gondoskodnia kell arról, hogy a `firecrawl` könyvtár és a benne lévő `.env` fájl megfelelő tulajdonossal és jogosultságokkal rendelkezzen. 
Ez elengedhetetlen ahhoz, hogy a szolgáltatás induláskor ki tudja írni a hitelesítő adatait.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Most, hogy mindent ellenőrzött, indítsa el a szolgáltatást a `systemd` segítségével:
```bash
systemctl --user start firecrawl.service
```
[Az OpenClaw Actions](https://docs.openclaw.ai/) elérhetők az interaktív konténeren belülről, a Web Dashboard pedig ugyanazon a hoszton és porton érhető el, itt: http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Az `OPENCLAW_GATEWAY_TOKEN` beszerzése

Miután a szolgáltatás elindult és fut, egy új `.openclaw` könyvtárat vesz észre a saját mappájában (~/.openclaw). Ez a könyvtár alapértelmezés szerint zárolva van, ezért fel kell oldania a zárolást, hogy hozzáférjen a gateway tokenjéhez.

1. Adjon hozzáférést a könyvtárhoz:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Olvassa ki a gateway tokent:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Keresse meg az `OPENCLAW_GATEWAY_TOKEN` értéket a kimenetben.

3. Nyissa meg a gateway irányítópultot a böngészőjében: http://127.0.0.1:18789. Illessze be a tokenjét, amikor a rendszer hitelesítést kér.

A szolgáltatás leállításához futtassa:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Az OpenClaw Gateway elindítása

A gateway az az OpenClaw folyamat, amely kezeli az ágens ciklust és kiszolgálja az irányítópultot:

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

Az irányítópult megnyitásához futtassa ezt egy második terminálban, miközben a gateway még fut:

```bash
openclaw dashboard
```

Mivel a gateway a loopback interfészhez kötődik, az irányítópult automatikusan hitelesít, amikor ugyanarról a gépről nyitja meg, így helyi hozzáféréshez nincs szükség token megadására vagy eszközjóváhagyásra. Az OpenClaw irányítópultot kell látnia, amelyben a Lemonade modell szerepel aktív háttérrendszerként.

> Ha bekapcsolta a sandboxingot, ellenőrizheti azt úgy, hogy az irányítópultról megkéri az ágenst a `run hostname` futtatására. Ha a gép hosztneve helyett egy rövid konténer-azonosítót lát, a sandbox megfelelően működik.

**Gratulálunk, sikeresen felépített egy teljesen helyi AI ágens stack-et a semmiből.**

> **Szüksége van a gateway tokenre?** Futtassa az `openclaw dashboard --no-open` parancsot, hogy kiírja az irányítópult URL-jét a beágyazott tokennel (ez a vágólapra másolást is megkísérli). Alternatívaként a token megtalálható a `gateway.auth.token` alatt a `~/.openclaw/openclaw.json` fájlban.
>
> **Távoli eszköz jóváhagyása:** Ha az irányítópultot egy második gépről vagy telefonról nyitja meg, a böngésző megjelenít egy kérésazonosítót. A gateway-t futtató gépen futtassa:
> ```bash
> openclaw devices approve <requestId>
> ```
> Erre csak távoli vagy másodlagos eszközök esetén van szükség, ugyanarról a gépről történő loopback hozzáférés automatikusan hitelesít.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Miután a gateway elindult, bármely eszközről elérheti a helyi ágensét. Válassza ki az Önnek megfelelő beállítást. Az OpenClaw támogatja a [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) és más csatornákat, a teljes listát itt találja: [docs.openclaw.ai](https://docs.openclaw.ai).

---

### A opció: Discord

A Discordhoz olyan szerverre van szükség, amelyen **rendszergazdai hozzáféréssel** rendelkezik a bot hozzáadásához. Ha csak megosztott szerverei vannak, de nincs sajátja, használja inkább a B opciót (Telegram).

#### Discord fiók és szerver létrehozása

Ha még nincs Discord fiókja, regisztráljon a [discord.com](https://discord.com) oldalon. Emellett szüksége van egy szerverre, amelyen rendszergazda, hozzon létre egyet a Discord oldalsávjában található **+** ikonra kattintva, majd válassza a **Create My Own** opciót. Egy privát szerver is megfelel.

#### Discord alkalmazás és bot létrehozása

1. Nyissa meg a [Discord Developer Portal](https://discord.com/developers/applications) oldalt, és kattintson a **New Application** gombra. Adjon neki nevet (pl. "openclaw-bot").
2. Az oldalsávban kattintson a **Bot** menüpontra. Állítson be egy felhasználónevet a botnak.
3. Még mindig a Bot oldalon, görgessen le a **Privileged Gateway Intents** részhez, és engedélyezze a következőket:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgessen vissza felfelé, és kattintson a **Reset Token** gombra a bot tokenjének generálásához. Másolja ki.

#### A bot hozzáadása a szerveréhez

1. Az oldalsávban kattintson az **OAuth2/ URL Generator** menüpontra.
2. A **Scopes** alatt engedélyezze a `bot` és `applications.commands` opciókat.
3. A **Bot Permissions** alatt engedélyezze a következőket: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másolja ki a generált URL-t, illessze be a böngészőjébe, válassza ki a szerverét, majd erősítse meg. A botnak ezután meg kell jelennie a szerver tagjai között.
#### Az azonosítók begyűjtése

Engedélyezd a Fejlesztői módot a Discordban (**Felhasználói beállítások / Speciális / Fejlesztői mód**), majd:
- Kattints jobb gombbal a szervered ikonjára: **Szerverazonosító másolása**
- Kattints jobb gombbal a saját avatárodra: **Felhasználói azonosító másolása**

#### Privát üzenetek engedélyezése a szerver tagjaitól

Kattints jobb gombbal a szervered ikonjára / **Adatvédelmi beállítások** / kapcsold be a **Direkt üzenetek** opciót. Ez lehetővé teszi, hogy a bot privát üzenetet küldjön neked, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárold a bot tokenjét környezeti változóként, majd hozz létre egy egyetlen patch fájlt, amely engedélyezi a Discordot, hivatkozik a tokenre, és engedélyezőlistára veszi a szerveredet. Cseréld le a `<server_id>` és `<user_id>` értékeket a fent begyűjtött azonosítókra.

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

> **Ne bízd rá az agentre ennek a konfigurálását.** Ha a sandboxolás engedélyezve van, az agent nem tud írni a `~/.openclaw/openclaw.json` fájlba a sandboxon belülről, ehelyett a fent látható CLI parancsokat a hoszton kell használnod.

Indítsd újra a gateway-t, hogy felvegye az új csatornakonfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül a `logged in to discord as <bot-name>` üzenetet kell látnod a gateway kimenetében.

#### A Discord fiókod párosítása

Küldj privát üzenetet a botnak Discordban. Válaszul egy rövid párosítási kódot fog küldeni.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyd jóvá azon a gépen, amelyen az OpenClaw fut:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Mostantól közvetlenül a Discordból cseveghetsz az agenteddel, és feladatokat delegálhatsz a helyi hardveredre.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb, mint a Discord, nem igényel sem szervert, sem admin hozzáférést.

#### Telegram bot létrehozása

1. Nyisd meg a Telegramot, és küldj üzenetet a **@BotFather**-nek.
2. Küldd el a `/newbot` parancsot, és kövesd az utasításokat. Mentsd el a bot tokent, amit kapsz.

#### Az OpenClaw konfigurálása Telegramhoz

Tárold a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add hozzá a csatornakonfigurációt a `~/.openclaw/openclaw.json` fájlhoz (vagy patcheld a dashboardon keresztül):

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

Indítsd újra a gateway-t, majd küldj egy üzenetet a botodnak Telegramon. Hagyd jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Mostantól cseveghetsz az agenteddel Telegram privát üzeneten keresztül.

---

## Következő lépések

Most, hogy az agented parancsokat tud fogadni a telefonodról, és tud cselekedni a helyi gépeden, íme három érdemes irány, amit érdemes felfedezni:

1. **Tőzsdei összefoglaló**: Ütemezd be az OpenClaw-t, hogy fix időközönként lekérje az adatokat pénzügyi API-kból, foglalja össze a napi mozgásokat a helyi modelleddel, és küldjön egy összefoglalót a telefonodra minden reggel a választott csatornán keresztül.

2. **Finomhangolás-monitor**: Indíts el egy tanítási feladatot távolról Telegramon vagy Discordon keresztül, majd kérd meg az agentet, hogy kövesse figyelemmel a tanítási naplót, és jelentse vissza rendszeresen a loss értékeket, a GPU-kihasználtságot és a lemezhasználatot a telefonodra. Ha a futás megakad vagy a VRAM-használat megugrik, azonnal értesülsz róla anélkül, hogy a gépnél kellene lenned.

3. **IOT egy helyi VLM-mel**: Irányíts egy kamerát a bejárati ajtódra, futtass egy vision modellt a Lemonade-en, és kérd meg az OpenClaw-t, hogy elemezze a képkockákat igény szerint vagy egy trigger hatására. Kérdezd meg „érkezett ma valamilyen csomag?” a telefonodról, és kapj egyértelmű választ a saját hardveredtől.

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