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

Az [OpenHands](https://github.com/All-Hands-AI/OpenHands) egy olyan AI szoftverügynök, amely kódot ír, parancsokat futtat, böngészi a webet, és fájlokat szerkeszt egy valós munkaterületen. Ahelyett, hogy a javaslatokat egy chatablakból másolnád ki, az ügynököt egy projektmappára irányítod, és hagyod, hogy elvégezze a munkát: implementáljon egy funkciót, javítson egy hibát, írjon teszteket, vagy magyarázza el a kódbázist.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az ajánlott böngésző felhasználói felület az OpenHands futtatásához. Egyetlen `agent-canvas` parancs elindítja az ügynökszervert, az automatizálási háttérrendszert és a webes frontendet együtt, így a böngésződből tudsz beszélgetést folytatni az ügynökkel.

Ahhoz, hogy minden a te AMD rendszereden maradjon, az ügynök egy helyi modellel kommunikál, amelyet a Lemonade Server szolgáltat. A Lemonade egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé ezt a modellt, így az Agent Canvas ugyanúgy tudja konfigurálni, mint bármely más OpenAI-stílusú végpontot, miközben a modell, a kódod és a beszélgetés kontextusa mind a te gépeden marad.

Ebben az útmutatóban elindítasz egy helyi modellt, elindítod az Agent Canvast, ráirányítod arra a modellre, és lefuttatod az első kódolási feladatodat egy valós projektmappán.

## Mit fogsz megtanulni

- Hogyan indítsd el a Lemonade Servert, és győződj meg róla, hogy egy helyi modell válaszol a chatkérésekre
- Hogyan telepítsd és indítsd el az Agent Canvast az npm csomagból
- Hogyan konfiguráld az Agent Canvast, hogy egy helyi Lemonade modellt használjon LLM-ként
- Hogyan indíts egy OpenHands beszélgetést, és figyeld meg, ahogy az ügynök fájlokat szerkeszt és parancsokat futtat egy munkaterületen
- Hogyan tekintsd át, mit változtatott az ügynök, és hogyan irányítsd további üzenetekkel

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe az útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | A modellt futtatja, amely az ügynököt hajtja. |
| OpenHands | Egy AI szoftverügynök, amely fájlokat olvas és szerkeszt, shell parancsokat futtat, és böngészi a webet egy munkaterületen belül. | Az ügynök, amelyet a chatből irányítasz. |
| Agent Canvas | A böngésző felhasználói felület és háttérrendszer, amely az OpenHands beszélgetéseket futtatja, és megjeleníti az eszközhívásokat és fájlváltoztatásokat. | Elindítja a rendszert, és otthont ad a beszélgetésednek. |
| Munkaterület | A projektmappa, amelyet az ügynök olvashat és módosíthat. | Az ügynök szerkesztéseinek és parancsainak célpontja. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló ügynök munkafolyamatok nagyobb modellből és kontextusablakból profitálnak. Használj legalább 32 GB rendszermemóriát, és részesítsd előnyben a 64 GB-ot vagy annál többet a nagyobb GGUF modellekhez.
<!-- @device:end -->

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Ellenőrizd a szoftverfrissítéseket

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Szükséged van a következőkre:

- Telepített Lemonade Server, amely képes kiszolgálni az alábbi modellt.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb, és `npm` (az `agent-canvas` CLI-hez szükséges).
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az ügynökszerver környezetének kezelésére használ. Ha a rendszereden még nincs telepítve, telepítsd az
  [uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/)
  az Agent Canvas elindítása előtt.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop Windows-hoz](https://docs.docker.com/desktop/setup/install/windows-install/),
  telepítve és futtatva. Windows rendszeren az Agent Canvas rendszer a
  közzétett Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t és a
  `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítened a hoszton.
<!-- @os:end -->

- Egy projektmappa, amelyben dolgozni fogsz. Ez lehet bármely helyi git repository vagy kódmappa, amelyen az ügynöknek dolgoznia kell.

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

## 1. Indítsd el a Lemonade Servert

Indítsd el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Válassz a hardveredhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős kódolási modell, de nagy memóriaterületet igényel. Ha az eszközöd korlátozott memóriával vagy GPU VRAM-mal rendelkezik, válassz helyette egy kisebb GGUF modellt a Lemonade modellkönyvtárból, és használd azt a modellazonosítót az útmutató további részében.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha még nincs jelen, ami eltarthat egy ideig a modell méretétől és a kapcsolatodtól függően.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé a következő címen:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Ellenőrizd a helyi modellt

Győződj meg róla, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Ezután küldj egy rövid chatkérést:

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
## 3. Az Agent Canvas telepítése és indítása

<!-- @os:linux -->
Telepítse globálisan a közzétett Agent Canvas csomagot:

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
a böngészőjében. A port nem különleges — ha a 8000-es port már foglalt, adjon meg egy
szabad portot a `--port` (vagy `-p`) kapcsolóval az Agent Canvas indításakor:

```bash
agent-canvas --port 3000
```

Ezután nyissa meg helyette a `http://localhost:3000` címet. Az alapértelmezett helyi backendnek egészségesként kell megjelennie a kezdőképernyőn.

Az `agent-canvas` parancs egyszerre indítja el az ágensservert, az automatizálási backendet és
a webes frontendet. Csak erre az egy parancsra van szükség az OpenHands helyi
futtatásához.

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
Windows rendszeren futtassa a közzétett Agent Canvas konténerképet Docker Desktop segítségével. A kép tartalmazza az Agent Servert, az automatizálási backendet és
a webes frontendet, így nem kell a Node.js-t, az `uv`-t vagy a CLI-t telepítenie a hoszton.

Először hozza létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltse le a közzétett képet (nyilvános, így nincs szükség bejelentkezésre):

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
foglalt, rendeljen hozzá egy másik hoszt portot, például `-p 8080:8000`, és nyissa meg helyette a
`http://localhost:8080/canvas` címet.

> **Megjegyzés:** Az első indítás inicializálja az Agent Servert a konténeren belül,
> így eltarthat egy-két percig, mire a backend egészségesként jelentkezik.

A `.openhands` csatolás megőrzi az LLM-profilt és a beállításokat a konténer
újraindításai között. Ennek az útmutatónak a további része mindent az Agent
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

Első indításkor az Agent Canvas egy bevezető folyamatot indít. Ebben a folyamatban:

1. Hagyja kiválasztva az **OpenHands** ágenst, majd kattintson a **Next** gombra.
2. A **Set up your LLM** részen válassza az **Advanced** lehetőséget.
3. Hagyja az **Authentication** beállítást **API key** értéken.
4. Állítsa a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Windows rendszeren a stack egy konténerben fut, amely nem éri el a hosztot a
   > `127.0.0.1` címen. Ehelyett használja a `http://host.docker.internal:13305/api/v1` címet, hogy a
   > konteneres ágens elérje a Windows hoszton futó Lemonade-et.
   <!-- @os:end -->
6. Az **API Key** mezőbe írjon be egy tetszőleges nem üres helyőrzőt, például `lemonade-local`.
   A Lemonade-nek nincs szüksége valós kulcsra, de az OpenHands kliensnek kell egy érték
   a küldéshez.
7. Kattintson a **Next** gombra.

A kitöltött Advanced beállításoknak így kell kinézniük. Az API kulcs mezőt
a felhasználói felület elrejti.

![Agent Canvas első használatakor megjelenő LLM Advanced beállítások a Lemonade modellel és a helyi bázis URL-lel](assets/01-llm-advanced-settings.png)

Az Agent Canvas ezeket az értékeket LLM-profilként menti el. Ha az adott verzió elnevezést kér ehhez a
profilhoz, használjon szóköz nélküli nevet, például `lemonade-local`. Ha később
modellt vált, nyissa meg a **Settings > LLM** menüt, és frissítse ugyanazokat az Advanced mezőket. A mentett profilok között a chat beviteli mezőből a `/model` paranccsal
válthat.

## 5. Munkaterület megnyitása

Az ágens csak azon a munkaterületen belüli fájlokat tudja olvasni és módosítani, amelyet Ön kiválaszt. Mielőtt
elindít egy feladatot, irányítsa az Agent Canvast a projektmappájára:

1. A kezdőképernyőn válassza az **Open Workspace** lehetőséget.
2. Válassza ki azt a mappát, amely a projektjét tartalmazza (például egy git repository-t,
   amelyen szeretné, hogy az ágens dolgozzon).
3. Indítson egy új beszélgetést abban a munkaterületben.

Minden, amit az ágens tesz — fájlok olvasása, parancsok futtatása, kód szerkesztése —, arra a munkaterületre korlátozódik.

![Agent Canvas kezdőképernyője a bevezető folyamat után](assets/02-agent-canvas-home.png)

## 6. Az első kódolási feladat futtatása

A munkaterület megnyitása és a helyi LLM kiválasztása után írjon be egy konkrét feladatot a
chatbe. Egy jó első feladat kicsi és ellenőrizhető, például:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Figyelje a beszélgetés idővonalát. Az OpenHands a következőket fogja tenni:

- Beolvassa a munkaterületet, hogy megértse az elrendezést.
- Létrehozza a `hello.py` fájlt a kért függvénnyel és teszt blokkal.
- Opcionálisan futtatja a `python3 hello.py` parancsot az eredmény ellenőrzésére.
- Beszámol a chatben arról, hogy mit tett, és bármilyen parancs kimenetéről.

Az új fájlnak meg kell jelennie a munkaterületen, és az ágens záró üzenetének
le kell írnia az elvégzett módosítást. Ez a kifizetődő pillanat: az
ágens valódi kódot írt és futtatott a projektmappájában.

## 7. Az ágens felülvizsgálata és irányítása

Miután az ágens befejezett egy lépést, mielőtt elfogadná a következő lépést, tekintse át a munkáját:

- **Fájlmódosítások**: használja a munkaterület fájlböngészőjét vagy az ágens diff nézetét, hogy
  pontosan lássa, mi lett hozzáadva, módosítva vagy törölve.
- **Parancs kimenete**: bontson ki bármelyik parancsot, amelyet az ágens futtatott, hogy lássa a stdout-ot, a stderr-t
  és a kilépési kódot.
- **Utókövetés**: ha az eredmény nem az, amit szeretett volna, válaszoljon ugyanabban a
  beszélgetésben egy korrekcióval. Az ágens megtartja a korábbi kontextust, és
  tovább dolgozik ugyanazokon a fájlokon.

Ha például a teszt nem a várt üdvözlést írta ki, válaszoljon így:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Az ágens újra beolvassa a fájlt, futtatja a parancsot, diagnosztizálja a problémát, majd
ismét szerkeszti a fájlt — mindezt ugyanabban a beszélgetésben.
## Hibaelhárítás

<!-- @os:linux -->
- **Az `agent-canvas` nincs rajta a PATH-on:** telepítse újra a
  `npm install -g @openhands/agent-canvas` paranccsal, és győződjön meg róla, hogy az npm globális bináris
  könyvtára szerepel a PATH-on, mielőtt az `agent-canvas` elindítható lenne egy új
  terminálból.
- **Az `npm install -g` engedélyezési hibával meghiúsul:** állítson be egy felhasználó tulajdonában lévő
  globális npm könyvtárat, majd nyissa meg újra a terminált, és telepítse újra az Agent Canvas-t.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Az `uv` hiányzik:** telepítse
  [az uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/).
  Az Agent Canvas a `uv`-t használja az ügynökkiszolgáló Python-környezetének kezelésére.
<!-- @os:end -->

<!-- @os:windows -->
- **A `docker pull` vagy `docker run` nem tud kapcsolódni:** győződjön meg róla, hogy a Docker Desktop
  fut (a bálna ikonja a tálcán látható), és hogy a motor elindult. A
  `docker version` parancsnak egy Client és egy Server szakaszt is ki kell írnia.
- **A konténer elindul, de a háttérszolgáltatás sosem lesz egészséges:** az első
  indítás inicializálja az Agent Server-t a konténeren belül; adjon neki egy-két
  percet, majd nézze meg a `docker logs <container>` kimenetét hibák után kutatva.
- **A konténer nem éri el a Lemonade-et:** a konténer a hoszthoz a
  `host.docker.internal` címen keresztül fér hozzá. Ellenőrizze, hogy a Lemonade fut-e
  a Windows hoszton a `lemonade status` paranccsal, és az LLM konfigurálásakor
  a `http://host.docker.internal:13305/api/v1` címet használja Base URL-ként.
<!-- @os:end -->

- **A felhasználói felület betöltődik, de a háttérszolgáltatás nem egészséges:** várjon egy-két
  percet, amíg az ügynökkiszolgáló elindul, majd frissítse az oldalt. Ha továbbra sem
  egészséges, indítsa újra a stacket, és nézze meg a naplókat hibák után kutatva.
- **A Lemonade csevegési kérések kapcsolódási hibával meghiúsulnak:** ellenőrizze, hogy
  a `curl -fsS "http://127.0.0.1:13305/api/v1/health"` sikeres-e, és hogy
  a Lemonade még mindig kiszolgálja-e a modellt a `lemonade status` paranccsal.
- **Az ügynök kontextushossz- vagy tokenkorlát-üzenettel hibázik:** kezdjen új
  beszélgetést, hogy az ügynök ne cipeljen túlméretezett előzményeket. Ha ez
  továbbra is előfordul, indítsa újra a Lemonade-et a `ctx_size` alapértelmezett
  65536 értékénél nagyobb beállítással (például `ctx_size=131072`), memóriakapacitás függvényében.
- **Az ügynök alacsony minőségű vagy hiányos szerkesztéseket készít:** váltson egy nagyobb
  modellre a Lemonade-ben, vagy adjon az ügynöknek egy kisebb, konkrétabb feladatot, és hagyja
  befejezni, mielőtt a következő módosítást kérné.

## Következő lépések

- Próbáljon ki egy nagyobb feladatot ugyanabban a munkaterületben, például adjon hozzá egy
  unit teszt fájlt vagy javítson egy ismert hibát, és tekintse át az ügynök diffjét, mielőtt megtartaná a módosítást.
- Kapcsoljon egy MCP-kiszolgálót, például GitHub-ot vagy Slack-et a **Customize** alatt, hogy
  az ügynök olvashassa a hibajegyeket vagy közzétehessen frissítéseket munka közben.
- Mentsen több LLM-profilt (egy gyors kis modellt és egy erősebb nagy modellt), és
  váltson közöttük a `/model` paranccsal beszélgetés közben.
- Lépjen tovább az [OpenHands automatizálásokhoz](https://docs.openhands.dev/openhands/usage/automations/overview), hogy
  ismétlődő fejlesztési ciklusokat ütemezett vagy eseményvezérelt ügynökfuttatásokká alakítson.

## Erőforrások

- [OpenHands dokumentáció](https://docs.openhands.dev/)
- [Agent Canvas áttekintés](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas beállítás](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profilok és modellkonfiguráció](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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