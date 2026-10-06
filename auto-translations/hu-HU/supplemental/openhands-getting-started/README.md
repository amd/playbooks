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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) egy olyan AI szoftverügynök, amely képes kódot írni, parancsokat futtatni, böngészni az interneten, és fájlokat szerkeszteni egy valós munkaterületen. Ahelyett, hogy a javaslatokat kimásolnád egy csevegőablakból, az ügynököt egy projektmappára irányítod, és hagyod, hogy elvégezze a munkát: implementáljon egy funkciót, javítson egy hibát, írjon teszteket, vagy magyarázzon el egy kódbázist.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) az ajánlott böngészős felhasználói felület az OpenHands futtatásához. Egyetlen `agent-canvas` parancs egyszerre indítja el az ügynökkiszolgálót, az automatizálási háttérrendszert és a webes frontendet, így a böngészőből irányíthatod a beszélgetést az ügynökkel.

Annak érdekében, hogy minden az AMD rendszereden maradjon, az ügynök egy helyi modellel kommunikál, amelyet a Lemonade Server szolgál ki. A Lemonade egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé ezt a modellt, így az Agent Canvas ugyanúgy konfigurálhatja, mint bármely más OpenAI-stílusú végpontot, miközben a modell, a kódod és a beszélgetés kontextusa is a gépeden marad.

Ebben az útmutatóban elindítasz egy helyi modellt, elindítod az Agent Canvast, ráirányítod erre a modellre, majd futtatod az első kódolási feladatodat egy valódi projektmappán.

## Amit meg fogsz tanulni

- Hogyan indítsd el a Lemonade Servert, és győződj meg róla, hogy a helyi modell válaszol a csevegési kérésekre
- Hogyan telepítsd és indítsd el az Agent Canvast az npm csomagból
- Hogyan konfiguráld az Agent Canvast, hogy egy helyi Lemonade modellt használjon LLM-ként
- Hogyan indíts el egy OpenHands beszélgetést, és figyeld meg, ahogy az ügynök fájlokat szerkeszt és parancsokat futtat a munkaterületen
- Hogyan tekintsd át az ügynök által végzett módosításokat, és hogyan irányítsd azt további üzenetekkel

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe az útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely egy OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | Futtatja az ügynököt meghajtó modellt. |
| OpenHands | Egy AI szoftverügynök, amely fájlokat olvas és szerkeszt, shell parancsokat futtat, és böngészik az interneten egy munkaterületen belül. | Az ügynök, amelyet a csevegésből irányítasz. |
| Agent Canvas | A böngészős felhasználói felület és háttérrendszer, amely futtatja az OpenHands beszélgetéseket, és megjeleníti az eszközhívásokat és fájlmódosításokat. | Elindítja a teljes rendszert, és otthont ad a beszélgetésednek. |
| Munkaterület | A projektmappa, amelyet az ügynök olvashat és módosíthat. | Az ügynök szerkesztéseinek és parancsainak célpontja. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló ügynök munkafolyamatok nagyobb modellből és kontextusablakból profitálnak. Használj legalább 32 GB rendszermemóriát, és lehetőleg 64 GB-ot vagy többet a nagyobb GGUF modellekhez.
<!-- @device:end -->

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Szükséged lesz a következőkre:

- Telepített Lemonade Server, amely képes kiszolgálni az alábbi modellt.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb, valamint `npm` (az `agent-canvas` CLI használja).
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az ügynökkiszolgáló környezetének kezelésére használ. Ha a rendszereden még nincs telepítve, telepítsd a [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján, mielőtt elindítanád az Agent Canvast.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop Windows rendszerhez](https://docs.docker.com/desktop/setup/install/windows-install/),
  telepítve és futva. Windows rendszeren az Agent Canvas rendszer a közzétett
  Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t és a
  `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítened a hoszton.
<!-- @os:end -->

- Egy projektmappa, amelyben dolgozni fogsz. Ez lehet bármilyen helyi git
  tárolója vagy kódkönyvtár, amelyen szeretnéd, hogy az ügynök dolgozzon.

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

## 1. Lemonade Server indítása

Indítsd el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Válassz a hardveredhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős kódoló modell, de nagy memóriakeretet igényel. Ha az eszközöd korlátozott memóriával vagy GPU VRAM-mal rendelkezik, válassz inkább egy kisebb GGUF modellt a Lemonade modellkönyvtárból, és ezt a modellazonosítót használd az útmutató során.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs jelen, ami a modell méretétől és a kapcsolatodtól függően eltarthat egy ideig.

A Lemonade egy OpenAI-kompatibilis API-t biztosít itt:

```text
http://127.0.0.1:13305/api/v1
```

## 2. A helyi modell ellenőrzése

Győződj meg róla, hogy a Lemonade képes kiszolgálni a kiválasztott modellt:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Ezután küldj egy kis csevegési kérést:

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

Ha ez egy `choices` tömböt ad vissza, a Lemonade készen áll az Agent Canvas számára.

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
## 3. Agent Canvas telepítése és indítása

<!-- @os:linux -->
Telepítse globálisan a publikált Agent Canvas csomagot:

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
a böngészőjében. A port nem speciális — ha a 8000-es port már foglalt, adjon meg bármilyen
szabad portot a `--port` (vagy `-p`) kapcsolóval az Agent Canvas indításakor:

```bash
agent-canvas --port 3000
```

Ezután nyissa meg a `http://localhost:3000` címet. Az alapértelmezett helyi backendnek egészségesként kell megjelennie
a kezdőképernyőn.

Az `agent-canvas` parancs együtt indítja el az agent szervert, az automatizálási backendet és
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
Windows rendszeren futtassa a publikált Agent Canvas konténerképet Docker Desktop segítségével.
A kép tartalmazza az Agent Servert, az automatizálási backendet és a webes frontendet, így
nem kell Node.js-t, `uv`-t vagy a CLI-t telepítenie a hoszton.

Először hozza létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltse le a publikált képet (nyilvános, így bejelentkezésre nincs szükség):

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

Nyissa meg a `http://localhost:8000/canvas` címet a böngészőjében. Ha a 8000-es port már foglalt,
rendeljen hozzá egy másik host portot, például `-p 8080:8000`, és helyette nyissa meg
a `http://localhost:8080/canvas` címet.

> **Megjegyzés:** Az első indításkor a konténeren belül inicializálódik az Agent Server,
> így eltarthat egy-két percig, mire a backend egészségesnek jelzi magát.

A `.openhands` csatolás megőrzi az LLM-profilját és beállításait a konténer
újraindításai között. A playbook hátralévő része teljes egészében az Agent
Canvas felhasználói felületén keresztül konfigurál mindent a böngészőjében.

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

Az első indításkor az Agent Canvas megnyit egy bevezető (onboarding) folyamatot. Ebben a folyamatban:

1. Hagyja az **OpenHands**-et kiválasztva agensként, és kattintson a **Next** gombra.
2. A **Set up your LLM** képernyőn válassza az **Advanced** opciót.
3. Hagyja az **Authentication** beállítást **API key**-en.
4. Állítsa be a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa be a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Windows rendszeren a stack konténerben fut, amely nem éri el a hosztot a
   > `127.0.0.1` címen. Ehelyett használja a `http://host.docker.internal:13305/api/v1` címet, így
   > a konténerizált agens elérheti a Windows hoszton futó Lemonade-ot.
   <!-- @os:end -->
6. Az **API Key** mezőbe írjon be bármilyen nem üres helyőrzőt, például `lemonade-local`.
   A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van egy értékre
   a küldéshez.
7. Kattintson a **Next** gombra.

A kitöltött Advanced beállításoknak így kell kinézniük. Az API key mezőt
elfedi a felhasználói felület.

![Agent Canvas első használatkori LLM Advanced beállítások a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Az Agent Canvas ezeket az értékeket LLM-profilként menti el. Ha az Ön verziója arra kéri, hogy
nevezze el ezt a profilt, használjon szóköz nélküli nevet, például `lemonade-local`. Ha később
modellt vált, nyissa meg a **Settings > LLM** menüt, és frissítse ugyanazokat az Advanced mezőket. A
mentett profilok között a chat beviteli mezőből a `/model` paranccsal válthat.

## 5. Munkaterület megnyitása

Az agens csak az Ön által kiválasztott munkaterületen belüli fájlokat tudja olvasni és módosítani. Egy
feladat megkezdése előtt irányítsa az Agent Canvast a projektmappájára:

1. A kezdőképernyőről válassza az **Open Workspace** lehetőséget.
2. Válassza ki a projektjét tartalmazó mappát (például egy git repository-t,
   amelyen szeretné, hogy az agens dolgozzon).
3. Indítson egy új beszélgetést abban a munkaterületben.

Minden, amit az agens tesz — fájlok olvasása, parancsok futtatása, kód szerkesztése —, arra a munkaterületre
korlátozódik.

![Agent Canvas kezdőképernyő az onboarding után](assets/02-agent-canvas-home.png)

## 6. Első kódolási feladat futtatása

A munkaterület megnyitásával és a helyi LLM kiválasztásával írjon be egy konkrét feladatot a
chatbe. Egy jó első feladat kicsi és ellenőrizhető, például:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Figyelje a beszélgetés idővonalát. Az OpenHands a következőket fogja tenni:

- Beolvassa a munkaterületet, hogy megértse a struktúráját.
- Létrehozza a `hello.py` fájlt a kért függvénnyel és teszt blokkal.
- Opcionálisan lefuttatja a `python3 hello.py` parancsot a kimenet ellenőrzéséhez.
- Beszámol a chatben arról, mit tett, és bármilyen parancs kimenetéről.

Látnia kell, hogy az új fájl megjelenik a munkaterületen, és az agens végső
üzenetének le kell írnia az elvégzett módosítást. Ez a kifizetődő pillanat: az
agens valódi kódot írt és futtatott a projektmappájában.

## 7. Az agens felülvizsgálata és irányítása

Miután az agens befejez egy lépést, vizsgálja felül a munkáját, mielőtt elfogadná a következőt:

- **Fájlváltozások**: használja a munkaterület fájlböngészőjét vagy az agens diff nézetét, hogy
  pontosan lássa, mi lett hozzáadva, megváltoztatva vagy törölve.
- **Parancskimenet**: bontsa ki bármelyik futtatott parancsot, hogy lássa a stdout, stderr,
  és a kilépési kódot (exit code).
- **Utánkövetés**: ha az eredmény nem az, amit szeretett volna, válaszoljon ugyanabban a
  beszélgetésben egy javítással. Az agens megőrzi az előző kontextust, és
  tovább dolgozik ugyanazokon a fájlokon.

Például, ha a teszt nem a várt üdvözlést írta ki, válaszoljon:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Az agens újraolvassa a fájlt, lefuttatja a parancsot, diagnosztizálja a problémát, és újra szerkeszti
a fájlt — mindezt ugyanabban a beszélgetésben.
## Hibaelhárítás

<!-- @os:linux -->
- **Az `agent-canvas` nincs rajta a PATH-on:** telepítsd újra a
  `npm install -g @openhands/agent-canvas` paranccsal, és győződj meg róla, hogy
  az npm globális bináris könyvtára szerepel a PATH-ban, mielőtt az
  `agent-canvas` elindítható lenne egy új terminálból.
- **Az `npm install -g` jogosultsági hibával hiúsul meg:** állíts be egy
  felhasználó tulajdonában lévő globális npm könyvtárat, majd nyisd meg újra a
  terminált, és telepítsd újra az Agent Canvas-t.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Az `uv` hiányzik:** telepítsd
  [az uv telepítési útmutatója](https://docs.astral.sh/uv/getting-started/installation/) alapján.
  Az Agent Canvas az `uv`-t használja az agent szerver Python-környezetének kezelésére.
<!-- @os:end -->

<!-- @os:windows -->
- **A `docker pull` vagy a `docker run` nem tud kapcsolódni:** győződj meg róla,
  hogy a Docker Desktop fut (a bálna ikonja ott van a tálcán), és hogy a motor
  elindult. A `docker version` parancsnak mind a Client, mind a Server
  szakaszt ki kell írnia.
- **A konténer elindul, de a backend soha nem válik egészségessé:** az első
  indítás a konténeren belül inicializálja az Agent Servert; adj neki egy-két
  percet, majd ellenőrizd a `docker logs <container>` parancs kimenetét hibák
  után kutatva.
- **A konténer nem éri el a Lemonade-ot:** a konténer a hosztot a
  `host.docker.internal` címen éri el. Ellenőrizd, hogy a Lemonade fut-e a
  Windows hoszton a `lemonade status` paranccsal, és a
  `http://host.docker.internal:13305/api/v1` címet add meg Base URL-ként az
  LLM beállításakor.
<!-- @os:end -->

- **A felhasználói felület betöltődik, de a backend nem egészséges állapotot
  mutat:** várj egy-két percet, amíg az agent szerver befejezi az indulást,
  majd frissítsd az oldalt. Ha továbbra is nem egészséges, indítsd újra a
  stacket, és nézd át a naplókat hibák után kutatva.
- **A Lemonade chat kérések kapcsolódási hibával hiúsulnak meg:** ellenőrizd,
  hogy a `curl -fsS "http://127.0.0.1:13305/api/v1/health"` sikeres-e, és hogy
  a Lemonade még mindig szolgáltatja-e a modellt a `lemonade status`
  paranccsal.
- **Az agent kontextushossz- vagy tokenkorlát-üzenettel hibázik:** indíts egy
  friss beszélgetést, hogy az agent ne cipeljen túlméretezett előzményeket. Ha
  ez továbbra is előfordul, indítsd újra a Lemonade-ot egy nagyobb `ctx_size`
  értékkel az alapértelmezett 65536-nál (például `ctx_size=131072`), ha a
  memória engedi.
- **Az agent gyenge minőségű vagy hiányos szerkesztéseket készít:** válts egy
  nagyobb modellre a Lemonade-ban, vagy adj az agentnek kisebb, konkrétabb
  feladatot, és hagyd, hogy befejezze, mielőtt a következő módosítást kéred.

## Következő lépések

- Próbálj ki egy nagyobb feladatot ugyanabban a munkaterületben, például adj
  hozzá egy unit teszt fájlt, vagy javíts ki egy ismert hibát, és tekintsd át
  az agent diffjét, mielőtt megtartod a módosítást.
- Csatlakoztass egy MCP szervert, például GitHub-ot vagy Slacket a
  **Customize** alatt, hogy az agent olvashassa az issue-kat vagy közzétehessen
  frissítéseket munka közben.
- Mentsél el több LLM profilt (egy gyors kis modellt és egy erősebb nagy
  modellt), és válts közöttük a `/model` paranccsal beszélgetés közben.
- Lépj tovább az [OpenHands automatizációk](https://docs.openhands.dev/openhands/usage/automations/overview)
  témakörre, hogy az ismétlődő fejlesztési ciklusokat ütemezett vagy
  eseményalapú agent futtatásokká alakítsd.

## Erőforrások

- [OpenHands dokumentáció](https://docs.openhands.dev/)
- [Agent Canvas áttekintés](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas beállítás](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
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