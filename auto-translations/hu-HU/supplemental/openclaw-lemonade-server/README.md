<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Az OpenClaw futtatása Lemonade Server háttérrendszerrel

## Áttekintés

Az [**OpenClaw**](https://openclaw.ai/) egy autonóm AI ügynök, amely képes kódot írni és futtatni, fájlokat kezelni, valamint összetett, többlépéses feladatokat elvégezni az Ön nevében. Ellentétben egy csevegőasszisztenssel, amely csupán kérdésekre válaszol, az OpenClaw valódi műveleteket hajt végre a rendszeren – ehhez gyors, képes AI háttérrendszerre van szüksége, amely lépést tud tartani az igényes ügynöki ciklussal.

A [**Lemonade Server**](https://lemonade-server.ai/) pontosan ez a háttérrendszer. Egy nyílt forráskódú helyi következtetési szerver, amely közvetlenül a hardveren futtatja a GenAI modelleket, és az iparági szabványos OpenAI API-n keresztül teszi elérhetővé azokat.

Együtt egy teljesen helyi AI ügynök-veremot alkotnak: a Lemonade kezeli a modell következtetést, az OpenClaw pedig biztosítja azt az ügynöki ciklust, amely a modell kimeneteit valódi műveletekké alakítja.

> **Mielőtt folytatná:** Az OpenClaw egy rendkívül autonóm AI ügynök. Bármely AI ügynök rendszerhez való hozzáférésének megadása kiszámíthatatlan vagy nem szándékolt következményekkel járhat. Csak akkor folytassa, ha tisztában van a kockázatokkal, és elfogadja, hogy autonóm szoftver jár el az Ön nevében.

---

## Mit fog megtanulni

Az útmutató végére képes lesz:

- Megismerni a **Lemonade Server**t
- **Telepíteni az OpenClaw**-t és **a Lemonade Serverre irányítani** AI háttérrendszerként.
- **Elindítani az OpenClaw átjárót** és megerősíteni, hogy az ügynök készen áll a munkára.
- **Kommunikációs csatornát csatlakoztatni** (Discord vagy Telegram), hogy bármely eszközről cseveghet az ügynökkel.

---

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

<!-- @os:linux -->
- **Ubuntu 24.04+** vagy kompatibilis Debian-alapú Linux disztribúciót futtató PC `apt-get` csomagkezelővel
- Legalább **12 GB RAM** (64 GB+ ajánlott nagyobb modellekhez)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcionális, az OpenClaw homokozóba zárásához)

- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11** operációs rendszert futtató PC
- Legalább **12 GB RAM** (64 GB+ ajánlott nagyobb modellekhez)
- **~10–30 GB szabad lemezterület** a modellsúlyokhoz
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcionális, az OpenClaw homokozóba zárásához)
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

Az útmutatóhoz ajánlott modell az Unsloth **Qwen3.6-35B-A3B-GGUF** modellje, egy erős MoE modell 263k tokenes kontextusablakkal, amely kiválóan alkalmas ügynöki feladatokhoz. Ez a modell UD-Q4_K_XL kvantálást használ. Töltse le most:

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

A modell alapértelmezett kontextushossza 262 144 token. Ha memóriahiány (OOM) hibákba ütközik, fontolja meg a kontextusablak csökkentését. Mivel azonban a Qwen3.6 a kiterjesztett kontextust összetett feladatokhoz használja, javasoljuk legalább 128K tokenes kontextushossz fenntartását a gondolkodási képességek megőrzése érdekében.

> **Tipp: A gondolkodás letiltása a gyorsabb ügynöki válaszokért:** A Qwen3.6-35B-A3B alapértelmezés szerint gondolkodási módban fut, ami minden válasz előtt késleltetést okoz. Az ügynöki ciklusokban ez a többletterhelés gyorsan összeadódik. A [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tároló tartalmaz egy kész konfigurációt, amely letiltja a gondolkodást. A használatához töltse le a fájlt és importálja:
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

Az OpenClaw-t WSL-en belül futtatjuk (ajánlott), és a Windows-on natívan futó Lemonade-hez csatlakoztatjuk. Ez Linux shell környezetet biztosít az OpenClaw számára, miközben a Lemonade GPU-gyorsítása a Windows oldalon marad.

### A WSL és az Ubuntu telepítése

Nyissa meg a PowerShellt rendszergazdaként, és telepítse a WSL kernelt:

```powershell
wsl --install --no-distribution
```

Ezután telepítse az Ubuntut:

```powershell
wsl --install -d Ubuntu-24.04
```

### A systemd engedélyezése WSL-ben

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

### A Lemonade áthidalása Windows-ból WSL-be

A WSL2 virtuális hálózaton fut. A Windows-on futó Lemonade a `127.0.0.1`-hez kötődik, amelyet a WSL nem tud közvetlenül elérni. Egy Windows portproxy továbbítja a forgalmat a WSL átjáró IP-jéről a Windows localhosthoz.

**Keresse meg a WSL átjáró IP-jét** (futtassa WSL-en belül):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adja hozzá a portproxyt** (futtassa PowerShellben rendszergazdaként, a `<WSL-Gateway-IP>` helyére írja be a WSL átjáró IP-jét):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adjon hozzá tűzfalszabályt** (ugyanabban az emelt jogosultságú PowerShellben):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Ellenőrzés WSL-ből**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ha az előző lépésben már betöltötte a Qwen3.6-35B-A3B-GGUF modellt, az alábbihoz hasonló JSON kimenetet kell látnia:

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

> A `netsh portproxy` szabály túléli az újraindításokat, de a WSL átjáró IP-je megváltozhat a `wsl --shutdown` után. Ha a Lemonade újraindítás után elérhetetlenné válik WSL-ből, kérje le a frissített átjáró IP-t, és frissítse a proxyt ezzel az új IP-vel.

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

A `--no-onboard` jelző kihagyja az interaktív beállítási varázslót – a modell háttérrendszert manuálisan konfigurálja a következő lépésben, ami pontos irányítást biztosít a használt modell és szerver felett.

Nyisson meg egy új terminált, és erősítse meg a telepítést:

```bash
openclaw --version
```

> **Tipp:** Ha a telepítés után `command not found` üzenetet lát, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> A tartós beállításhoz adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájlhoz.

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

Futtassa az OpenClaw nem interaktív bevezetőjét.
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

> **Az OpenClaw kontextusablak méretezése:** Az OpenClaw tömörítése akkor aktiválódik, ha `contextTokens > contextWindow − reserveTokens`. Az alapértelmezett `reserveTokensFloor` értéke 20 000 token – ez egy alsó korlát, amely felülírja a `reserveTokens` értékét, ha az alacsonyabb, így minden ~37k alatti modellkontextus végtelen tömörítési ciklust indít el. Állítson be alacsony tartalékot, és tiltsa le az alsó korlátot egyszer a konfigurációban, és ez minden modellre érvényes lesz, modellenként nem szükséges hangolás:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> A `reserveTokensFloor` egy *alsó korlát* (minimális védelem), nem maga a tartalék – csak az alsó korlát beállítása nem hat. A `reserveTokensFloor: 0` letiltja a védelmet, így az alacsonyabb `reserveTokens` elfogadásra kerül.
>
> **Mikor alkalmazza ezt:** Használja ezt a konfigurációt, ha a modell tényleges kontextusablaka ~37k alatt van – akár azért, mert a modell kis méretű (pl. 8k, 16k, 32k), akár azért, mert szándékosan alacsonyabb értékre korlátozta (pl. egy 128k modellt tölt be, de a kontextust 16k-ra állítja a Lemonade-ben). Enélkül az OpenClaw végtelen tömörítési ciklusba kerül indításkor.
>
> **Nagy kontextusú modellek teljes kontextussal:** Ezt teljesen kihagyhatja. Az alapértelmezett értékek jól működnek – a tömörítés jóval az ablak megtelése előtt aktiválódik, és a modellnek bőven van helye hosszú válaszok generálásához. Ha mégis alkalmazza, vegye figyelembe, hogy a `reserveTokens: 4096` a válasz hosszát ~4k tokenre korlátozza, ami megszakíthat hosszú fájlgenerálást vagy részletes terveket.
>
> **Hova adja hozzá:** Helyezze a `compaction` blokkot az `agents.defaults` blokkba az `openclaw.json` fájlban (általában `~/.openclaw/openclaw.json`):
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
> A konfiguráció többi része (átjáró, csatornák, modellek stb.) változatlan marad – csak a `compaction` kulcsot kell hozzáadni.

### (Ajánlott) Docker homokozó engedélyezése

Az OpenClaw az összes ügynöki fájl- és kódműveletet egy izolált Docker konténeren keresztül irányíthatja, ahelyett, hogy közvetlenül a gazdagépen futtatná azokat. Ez korlátozza a nem szándékolt műveletek hatókörét a homokozóra, érintetlenül hagyva a gazdagép fájlrendszerét és hálózatát.

Egyszer hozza létre a homokozó képet (a Docker-nek telepítve kell lennie):

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

Futtassa ezt a `sandbox` kulcs hozzáadásához a meglévő `agents.defaults` blokkba a `~/.openclaw/openclaw.json` fájlban:

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

A homokozó konténerek alapértelmezés szerint **nem rendelkeznek hálózati hozzáféréssel**. A kötési csatolásokkal és hálózati felülbírálásokkal kapcsolatban tekintse meg a [homokozó referenciát](https://docs.openclaw.ai/gateway/sandboxing).

> #### Hibaelhárítás: Docker hozzáférés megtagadva
> 
> Ha „permission denied" hibaüzenetet kap Docker parancsok futtatásakor:
> 
> **1. lépés: Adja hozzá felhasználóját a docker csoporthoz**
> 
> ```bash
> sudo groupadd docker                    # Csoport létrehozása, ha szükséges
> sudo usermod -aG docker $USER           # Saját maga hozzáadása a csoporthoz
> newgrp docker                           # A változtatás aktiválása
> docker run hello-world                  # Tesztelés
> ```
> 
> **2. lépés: Ha a hiba továbbra is fennáll, alkalmazza a tartós javítást**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Ezután **indítsa újra** a rendszert.
> 
> **Gyors ideiglenes javítás** (újraindítás után visszaáll):
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

### Az OpenClaw átjáró elindítása

Az átjáró az az OpenClaw folyamat, amely kezeli az ügynöki ciklust és kiszolgálja az irányítópultot:

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

Az irányítópult megnyitásához futtassa ezt egy második terminálon, miközben az átjáró még fut:

```bash
openclaw dashboard
```

Mivel az átjáró a loopback interfészhez kötődik, az irányítópult automatikusan hitelesíti magát, ha ugyanarról a gépről nyitják meg – nincs szükség token megadására vagy eszköz jóváhagyására a helyi hozzáféréshez. Látnia kell az OpenClaw irányítópultját, amelyen a Lemonade modellje aktív háttérrendszerként szerepel.

> Ha engedélyezte a homokozót, ellenőrizheti azt azzal, hogy megkéri az ügynököt, hogy `run hostname` parancsot futtasson az irányítópultról. Ha a gép nevének neve helyett egy rövid konténerazonosítót lát, a homokozó működik.

**Gratulálunk, teljesen helyi AI ügynök-veremot épített fel a semmiből.**

> **Szüksége van az átjáró tokenre?** Futtassa az `openclaw dashboard --no-open` parancsot az irányítópult URL-jének kinyomtatásához a beágyazott tokennel (megpróbálja azt a vágólapra is másolni). Alternatívaként a token a `gateway.auth.token` alatt található a `~/.openclaw/openclaw.json` fájlban.
>
> **Távoli eszköz jóváhagyása:** Amikor egy második gépről vagy telefonról nyitja meg az irányítópultot, a böngésző megjelenít egy kérésazonosítót. Az átjárót futtató gépen futtassa:
> ```bash
> openclaw devices approve <requestId>
> ```
> Ez csak távoli vagy másodlagos eszközöknél szükséges – az ugyanarról a gépről érkező loopback hozzáférés automatikusan hitelesítődik.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionális: Kommunikációs csatorna csatlakoztatása

Amint az átjáró fut, bármely eszközről elérheti a helyi ügynököt. Válassza a beállításához illő lehetőséget. Az OpenClaw támogatja a [Discord](https://docs.openclaw.ai/channels/discord), a [Telegram](https://docs.openclaw.ai/channels/telegram) és más csatornákat – a teljes listát a [docs.openclaw.ai](https://docs.openclaw.ai) oldalon találja.

---

### A lehetőség: Discord

A Discord olyan szervert igényel, amelyen **rendszergazdai hozzáféréssel rendelkezik** a bot hozzáadásához. Ha megosztott szervereken van, de nem rendelkezik saját szerverrel, használja a B lehetőséget (Telegram).

#### Discord fiók és szerver létrehozása

Ha nincs Discord fiókja, regisztráljon a [discord.com](https://discord.com) oldalon. Szüksége van egy szerverre is, amelyen Ön a rendszergazda – hozzon létre egyet a Discord oldalsávjában lévő **+** ikonra kattintva, majd válassza a **Create My Own** lehetőséget. Egy privát szerver is megfelelő.

#### Discord alkalmazás és bot létrehozása

1. Lépjen a [Discord Developer Portal](https://discord.com/developers/applications) oldalra, és kattintson a **New Application** gombra. Adjon nevet (pl. „openclaw-bot").
2. Az oldalsávban kattintson a **Bot** elemre. Állítson be felhasználónevet a botnak.
3. Még a Bot oldalon görgessen le a **Privileged Gateway Intents** részhez, és engedélyezze:
   - **Message Content Intent** (kötelező)
   - **Server Members Intent** (ajánlott)
4. Görgessen vissza felfelé, és kattintson a **Reset Token** gombra a bot token generálásához. Másolja ki.

#### A bot hozzáadása a szerverhez

1. Az oldalsávban kattintson az **OAuth2/ URL Generator** elemre.
2. A **Scopes** alatt engedélyezze a `bot` és `applications.commands` lehetőségeket.
3. A **Bot Permissions** alatt engedélyezze: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Másolja ki a generált URL-t, illessze be a böngészőbe, válassza ki a szerverét, és erősítse meg. A botnak most meg kell jelennie a szerver taglistájában.

#### Az azonosítók összegyűjtése

Engedélyezze a fejlesztői módot a Discordban (**User Settings/ Advanced/ Developer Mode**), majd:
- Kattintson jobb gombbal a szerver ikonjára: **Copy Server ID**
- Kattintson jobb gombbal a saját avatárjára: **Copy User ID**

#### Közvetlen üzenetek engedélyezése szerver tagoktól

Kattintson jobb gombbal a szerver ikonjára/ **Privacy Settings**/ kapcsolja be a **Direct Messages** lehetőséget. Ez lehetővé teszi, hogy a bot közvetlen üzenetet küldjön Önnek, ami szükséges a párosítási lépéshez.

#### Az OpenClaw konfigurálása Discordhoz

Tárolja a bot tokent környezeti változóként, majd hozzon létre egy egyetlen javítófájlt, amely engedélyezi a Discordot, hivatkozik a tokenre, és engedélyezi a szerverét. Cserélje ki a `<server_id>` és `<user_id>` értékeket a fent összegyűjtött azonosítókra.

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

> **Ne hagyatkozzon arra, hogy az ügynököt kéri meg ennek konfigurálására.** Ha a homokozó engedélyezve van, az ügynök nem tud írni a `~/.openclaw/openclaw.json` fájlba a homokozón belülről – használja a fenti CLI parancsokat a gazdagépen.

Indítsa újra az átjárót, hogy felvegye az új csatornakonfigurációt:

```bash
openclaw gateway run --bind loopback --port 18789
```

Néhány másodpercen belül a `logged in to discord as <bot-name>` üzenetet kell látnia az átjáró kimenetében.

#### A Discord fiók párosítása

Küldjön közvetlen üzenetet a botnak a Discordban. Egy rövid párosítási kóddal fog válaszolni.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hagyja jóvá az OpenClaw-t futtató gépen:
```bash
openclaw pairing approve discord <CODE>
```

> A párosítási kódok egy óra után lejárnak.

Mostantól közvetlenül a Discordból cseveghet az ügynökkel, és feladatokat delegálhat a helyi hardverére.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### B lehetőség: Telegram

A Telegram a legtöbb felhasználó számára egyszerűbb a Discordnál – nem igényel szervert és rendszergazdai hozzáférést.

#### Telegram bot létrehozása

1. Nyissa meg a Telegramot, és üzenjen a **@BotFather**-nek.
2. Küldje el a `/newbot` parancsot, és kövesse az utasításokat. Mentse el a kapott bot tokent.

#### Az OpenClaw konfigurálása Telegramhoz

Tárolja a tokent környezeti változóként:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adja hozzá a csatornakonfigurációt a `~/.openclaw/openclaw.json` fájlhoz (vagy javítsa az irányítópulton keresztül):

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

Indítsa újra az átjárót, majd küldjön bármilyen üzenetet a botnak a Telegramban. Hagyja jóvá a párosítást:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

A párosítási kódok egy óra után lejárnak. Mostantól cseveghet az ügynökkel Telegram közvetlen üzeneten keresztül.

---

## Következő lépések

Most, hogy az ügynök fogadhat parancsokat a telefonjáról és cselekedhet a helyi gépen, íme három érdemes irány a felfedezésre:

1. **Tőzsdei összefoglaló**: Ütemezze az OpenClaw-t, hogy rögzített időközönként kérjen le adatokat pénzügyi API-kból, foglalja össze a nap mozgásait a helyi modellel, és minden reggel küldjön egy összefoglalót a telefonjára a választott csatornán keresztül.

2. **Finomhangolás-figyelő**: Indítson el egy tanítási feladatot távolról Telegramon vagy Discordon keresztül, majd kérje meg az ügynököt, hogy kövesse a tanítási naplót, és rendszeres időközönként jelentse a veszteségértékeket, GPU-kihasználtságot és lemezhasználatot a telefonjára. Ha a futtatás megakad vagy a VRAM megugrik, azonnal értesül róla anélkül, hogy a gépnél kellene lennie.

3. **IoT helyi VLM-mel**: Irányítson egy kamerát a bejárati ajtóra, futtasson egy látásmodellt a Lemonade-en, és kérje meg az OpenClaw-t, hogy igény szerint vagy esemény hatására elemezze a képkockákat. Kérdezze meg a telefonjáról: „Érkezett ma csomag?" – és kapjon egyenes választ a saját hardverétől.