<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Áttekintés

Az [OpenHands](https://github.com/All-Hands-AI/OpenHands) egy AI szoftverügynök,
amely képes kódot írni, parancsokat futtatni, böngészni az interneten, és fájlokat szerkeszteni egy valós
munkaterületen. Ahelyett, hogy javaslatokat másolnál ki egy csevegőablakból, az
ügynököt egy projektmappára irányítod, és hagyod, hogy elvégezze a munkát: megvalósítson egy funkciót, kijavítson
egy hibát, teszteket írjon, vagy elmagyarázza a kódbázist.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az ajánlott
böngészős felhasználói felület az OpenHands futtatásához. Egyetlen `agent-canvas`
parancs elindítja az ügynök szervert, az automatizálási háttérrendszert és a webes frontendet együtt, így
böngészőből folytathatsz beszélgetést az ügynökkel.

Annak érdekében, hogy minden a te AMD rendszereden maradjon, az ügynök egy, a Lemonade Server
által kiszolgált helyi modellel kommunikál. A Lemonade ezt a modellt egy OpenAI-kompatibilis
API-n keresztül teszi elérhetővé, így az Agent Canvas úgy konfigurálhatja, mint bármely más OpenAI-stílusú
végpontot, miközben a modell, a kódod és a beszélgetés kontextusa mind a te
gépeden marad.

Ebben az útmutatóban elindítasz egy helyi modellt, elindítod az Agent Canvast, ráirányítod
arra a modellre, és futtatod az első kódolási feladatodat egy valós projektmappán.

## Amit tanulni fogsz

- Hogyan indítsd el a Lemonade Servert, és hogyan győződj meg róla, hogy egy helyi modell válaszol a csevegési kérésekre
- Hogyan telepítsd és indítsd el az Agent Canvast az npm csomagból
- Hogyan konfiguráld az Agent Canvast úgy, hogy egy helyi Lemonade modellt használjon LLM-ként
- Hogyan indíts egy OpenHands beszélgetést, és hogyan figyeld meg, ahogy az ügynök fájlokat szerkeszt és
  parancsokat futtat egy munkaterületen
- Hogyan tekintsd át, mit változtatott az ügynök, és hogyan irányítsd azt további üzenetekkel

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe az útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely egy OpenAI-kompatibilis API-t tesz elérhetővé. Az adataid soha nem hagyják el a gépedet. | A modellt futtatja, amely az ügynököt hajtja. |
| OpenHands | Egy AI szoftverügynök, amely fájlokat olvas és szerkeszt, shell parancsokat futtat, és böngészik az interneten egy munkaterületen belül. | Az ügynök, amelyet a csevegésből irányítasz. |
| Agent Canvas | A böngészős felhasználói felület és háttérrendszer, amely az OpenHands beszélgetéseket futtatja, és megjeleníti az eszközhívásokat és fájlváltozásokat. | Elindítja a verem (stack) elemeit, és befogadja a beszélgetésedet. |
| Munkaterület | A projektmappa, amelyet az ügynök olvashat és módosíthat. | Az ügynök szerkesztéseinek és parancsainak célpontja. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló-ügynök munkafolyamatok nagyobb modellből és kontextusablakból profitálnak. Használj
> legalább 32 GB rendszermemóriát, és a nagyobb GGUF modellekhez inkább 64 GB-ot vagy többet részesíts előnyben.
<!-- @device:end -->

## A memória konfigurációjának beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Szükséged lesz:

- Telepített Lemonade Serverre, amely képes kiszolgálni az alábbi modellt.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb verzió és `npm` (az `agent-canvas` CLI használja).
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az ügynök szerver környezetének kezeléséhez használ. Ha a rendszereden még nincs telepítve, telepítsd az
  [uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/)
  az Agent Canvas elindítása előtt.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  telepítve és futtatva. Windows rendszeren az Agent Canvas verem a közzétett
  Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t és a
  `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítened a hoszton.
<!-- @os:end -->

- Egy projektmappa, amelyben dolgozni szeretnél. Ez lehet bármely helyi git tároló vagy kódkönyvtár,
  amelyen szeretnéd, hogy az ügynök dolgozzon.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. A Lemonade Server elindítása

Indítsd el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Válassz a hardveredhez illeszkedő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős kódoló modell, de nagy memóriakeretre van szüksége. Ha az eszközöd memóriája vagy GPU VRAM-ja korlátozott, válassz inkább egy kisebb GGUF modellt a Lemonade modellkönyvtárból, és ennek a modellazonosítóját használd az útmutató során.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs jelen, ami eltarthat egy ideig a modell méretétől és a kapcsolatodtól függően.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé itt:

```text
http://127.0.0.1:13305/api/v1
```

## 2. A helyi modell ellenőrzése

Erősítsd meg, hogy a Lemonade képes kiszolgálni a kiválasztott modellt:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Majd küldj egy kis csevegési kérést:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Ha ez egy `choices` tömböt ad vissza, a Lemonade készen áll az Agent Canvas használatára.

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
model_id = "${lemonade_model}"

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
PY

body='{
  "model": "${lemonade_model}",
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
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
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
## 3. Az Agent Canvas telepítése és indítása

<!-- @os:linux -->
Telepítse globálisan a kiadott Agent Canvas csomagot:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Ezután indítsa el a teljes stacket egy terminálból:

```bash
agent-canvas
```

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul. Nyissa meg ezt az URL-t
a böngészőjében. A port nem speciális — ha a 8000-es már foglalt, adjon meg egy
szabad portot a `--port` (vagy `-p`) kapcsolóval az Agent Canvas indításakor:

```bash
agent-canvas --port 3000
```

Ezután nyissa meg a `http://localhost:3000` címet helyette. Az alapértelmezett helyi backendnek
egészségesként kell megjelennie a kezdőképernyőn.

Az `agent-canvas` parancs együtt indítja az agent szervert, az automatizálási backendet és
a webes frontendet. Csak erre az egyetlen parancsra van szüksége az OpenHands
helyi futtatásához.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windows rendszeren a kiadott Agent Canvas konténerképet a Docker Desktop segítségével futtassa. 
A kép tartalmazza az Agent Servert, az automatizálási backendet és a webes frontendet, így
nem kell telepítenie a Node.js-t, a `uv`-t vagy a CLI-t a gazdagépre.

Először hozza létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltse le a kiadott képet (nyilvános, így bejelentkezés nem szükséges):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Ezután indítsa el a stacket:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Nyissa meg a `http://localhost:8000/canvas` címet a böngészőjében. Ha a 8000-es port már
foglalt, rendeljen hozzá egy másik gazdagép portot, például `-p 8080:8000`, és nyissa meg
helyette a `http://localhost:8080/canvas` címet.

> **Megjegyzés:** Az első indítás inicializálja az Agent Servert a konténeren belül,
> így eltarthat egy-két percig, mire a backend egészségesnek jelzi magát.

A `.openhands` csatolás megőrzi az LLM profilját és beállításait a konténer
újraindításai között. Ennek az útmutatónak a hátralévő része mindent az Agent
Canvas felhasználói felületén keresztül konfigurál a böngészőjében.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->

## 4. A helyi LLM konfigurálása

Az első indításkor az Agent Canvas egy bevezető folyamatot indít. Ebben a folyamatban:

1. Hagyja az **OpenHands**-t kiválasztva ügynökként, és kattintson a **Next** gombra.
2. A **Set up your LLM** képernyőn válassza az **Advanced** opciót.
3. Hagyja az **Authentication** beállítást **API key** értéken.
4. Állítsa be a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa be a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Windows rendszeren a stack egy konténerben fut, amely nem éri el a gazdagépet a
   > `127.0.0.1` címen. Ehelyett használja a `http://host.docker.internal:13305/api/v1`
   > címet, hogy a konténerizált ügynök elérje a Windows gazdagépen futó Lemonade-et.
   <!-- @os:end -->
6. Az **API Key** mezőbe írjon be bármilyen nem üres helyőrzőt, például `lemonade-local`.
   A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van
   egy értékre a küldéshez.
7. Kattintson a **Next** gombra.

A kész Advanced beállításoknak így kell kinézniük. Az API key mezőt a felhasználói
felület elrejti.

![Agent Canvas első használatkori LLM Advanced beállítások a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Az Agent Canvas LLM profilként menti ezeket az értékeket. Ha a verziója arra kéri, hogy
nevezze el ezt a profilt, használjon egy szóközök nélküli nevet, például `lemonade-local`. Ha
később modellt vált, nyissa meg a **Settings > LLM** menüt, és frissítse ugyanazokat az
Advanced mezőket. A mentett profilok között a chat beviteli mezőből válthat a `/model`
paranccsal.

## 5. Munkaterület megnyitása

Az ügynök csak a Ön által kiválasztott munkaterületen belüli fájlokat tudja olvasni és
módosítani. Mielőtt feladatot indít, irányítsa az Agent Canvast a projekt mappájára:

1. A kezdőképernyőről válassza az **Open Workspace** lehetőséget.
2. Válassza ki azt a mappát, amely tartalmazza a projektjét (például egy git
   repository-t, amelyen szeretné, hogy az ügynök dolgozzon).
3. Indítson egy új beszélgetést ebben a munkaterületben.

Minden, amit az ügynök tesz — fájlok olvasása, parancsok futtatása, kód szerkesztése —
arra a munkaterületre korlátozódik.

![Agent Canvas kezdőlap a bevezető folyamat után](assets/02-agent-canvas-home.png)

## 6. Az első kódolási feladat futtatása

A munkaterület megnyitásával és a helyi LLM kiválasztásával írjon be egy konkrét feladatot
a chatbe. Egy jó első feladat kicsi és ellenőrizhető, például:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Figyelje a beszélgetés idővonalát. Az OpenHands a következőket fogja tenni:

- Beolvassa a munkaterületet az elrendezés megértéséhez.
- Létrehozza a `hello.py` fájlt a kért függvénnyel és teszt blokkal.
- Opcionálisan futtatja a `python3 hello.py` parancsot a kimenet ellenőrzéséhez.
- Beszámol arról, hogy mit tett, és minden parancskimenetről a chatben.

Látnia kell az új fájl megjelenését a munkaterületen, és az ügynök végső üzenetének
le kell írnia az általa végzett módosítást. Ez a kifizetődés pillanata: az
ügynök valódi kódot írt és futtatott a projekt mappájában.

## 7. Az ügynök munkájának áttekintése és irányítása

Miután az ügynök befejezett egy lépést, tekintse át a munkáját, mielőtt elfogadná a
következőt:

- **Fájlváltozások**: használja a munkaterület fájlböngészőjét vagy az ügynök diff
  nézetét, hogy pontosan lássa, mi lett hozzáadva, módosítva vagy törölve.
- **Parancskimenet**: bontsa ki bármely parancsot, amelyet az ügynök futtatott, hogy
  lássa a stdout-ot, stderr-t és a kilépési kódot.
- **Visszajelzések**: ha az eredmény nem az, amit szeretett volna, válaszoljon ugyanabban
  a beszélgetésben egy javítással. Az ügynök megőrzi a korábbi kontextust, és
  tovább dolgozik ugyanazokon a fájlokon.

Ha például a teszt nem írta ki a várt köszöntést, válaszoljon ezzel:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Az ügynök újra beolvassa a fájlt, futtatja a parancsot, diagnosztizálja a problémát, és
újra szerkeszti a fájlt — mindezt ugyanabban a beszélgetésben.
## Hibaelhárítás

<!-- @os:linux -->
- **Az `agent-canvas` nincs a PATH-on:** telepítse újra a
  `npm install -g @openhands/agent-canvas` paranccsal, és győződjön meg róla, hogy
  az npm globális binárisainak könyvtára szerepel a PATH-ban, mielőtt az
  `agent-canvas` elindítható lenne egy új terminálból.
- **Az `npm install -g` jogosultsági hibával meghiúsul:** állítson be egy
  felhasználó tulajdonában lévő globális npm könyvtárat, majd nyissa meg újra a
  terminált, és telepítse ismét az Agent Canvast.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Az `uv` hiányzik:** telepítse
  [az uv telepítési útmutatója](https://docs.astral.sh/uv/getting-started/installation/) alapján.
  Az Agent Canvas az `uv` segítségével kezeli az agent szerver Python környezetét.
<!-- @os:end -->

<!-- @os:windows -->
- **A `docker pull` vagy `docker run` nem tud kapcsolódni:** győződjön meg róla,
  hogy a Docker Desktop fut (a bálna ikonja megjelenik a tálcán), és hogy a motor
  elindult. A `docker version` parancsnak mind egy Client, mind egy Server
  szakaszt ki kell írnia.
- **A konténer elindul, de a háttérrendszer sosem lesz egészséges állapotú:** az
  első indítás a konténeren belül inicializálja az Agent Servert; adjon neki egy-két
  percet, majd ellenőrizze a `docker logs <container>` parancs kimenetét a hibák
  miatt.
- **A konténer nem éri el a Lemonade-ot:** a konténer a `host.docker.internal`
  címen éri el a hosztot. Győződjön meg róla, hogy a Lemonade fut a Windows
  hoszton a `lemonade status` paranccsal, és használja a
  `http://host.docker.internal:13305/api/v1` címet alap URL-ként az LLM
  konfigurálásakor.
<!-- @os:end -->

- **A felhasználói felület betöltődik, de a háttérrendszer állapota nem egészséges:**
  várjon egy-két percet, amíg az agent szerver befejezi az indulást, majd
  frissítse az oldalt. Ha továbbra is nem egészséges, indítsa újra a verem
  szolgáltatásait, és ellenőrizze a naplókat a hibák miatt.
- **A Lemonade csevegési kérések kapcsolódási hibával meghiúsulnak:** győződjön meg
  róla, hogy a `curl -fsS "http://127.0.0.1:13305/api/v1/health"` parancs sikeres,
  és hogy a Lemonade még mindig kiszolgálja a modellt a `lemonade status`
  paranccsal ellenőrizve.
- **Az ügynök kontextushossz- vagy tokenkorlát-üzenettel hibázik:** kezdjen új
  beszélgetést, hogy az ügynök ne cipeljen magával túl nagy előzményt. Ha
  rendszeresen előfordul, indítsa újra a Lemonade-ot a 65536-os alapértelmezettnél
  nagyobb `ctx_size` értékkel (például `ctx_size=131072`), ha a memória engedi.
- **Az ügynök rossz minőségű vagy hiányos módosításokat készít:** váltson egy
  nagyobb modellre a Lemonade-ban, vagy adjon az ügynöknek kisebb, konkrétabb
  feladatot, és hagyja, hogy befejezze, mielőtt a következő módosítást kéri.

## Következő lépések

- Próbáljon ki egy nagyobb feladatot ugyanabban a munkaterületben, például adjon
  hozzá egy unit teszt fájlt, vagy javítson egy ismert hibát, és tekintse át az
  ügynök diffjét, mielőtt megtartaná a módosítást.
- Csatlakoztasson egy MCP szervert, például GitHubot vagy Slacket a
  **Customize** alatt, hogy az ügynök olvashasson hibajegyeket vagy
  közzétehessen frissítéseket munka közben.
- Mentsen el több LLM profilt (egy gyors, kis modellt és egy erősebb, nagy
  modellt), és váltson közöttük a `/model` paranccsal a beszélgetés közben.
- Térjen át az [OpenHands automatizálásokra](https://docs.openhands.dev/openhands/usage/automations/overview),
  hogy az ismétlődő fejlesztési ciklusokat ütemezett vagy eseményindítású
  ügynökfutásokká alakítsa.

## Erőforrások

- [OpenHands dokumentáció](https://docs.openhands.dev/)
- [Agent Canvas áttekintés](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas beállítása](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profilok és modellkonfiguráció](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server dokumentáció](https://lemonade-server.ai/docs)

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