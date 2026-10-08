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

Az [OpenHands](https://github.com/All-Hands-AI/OpenHands) egy olyan AI szoftverügynök,
amely kódot ír, parancsokat futtat, böngészi a webet, és fájlokat szerkeszt egy valódi
munkaterületen. Ahelyett, hogy egy chatablakból másolna ki javaslatokat, az ügynököt
egy projektmappára irányítja, és hagyja, hogy elvégezze a munkát: megvalósítson egy
funkciót, kijavítson egy hibát, teszteket írjon, vagy elmagyarázzon egy kódbázist.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az ajánlott
böngészőalapú felhasználói felület az OpenHands futtatásához. Egyetlen `agent-canvas`
parancs indítja el egyszerre az ügynökkiszolgálót, az automatizálási háttérrendszert
és a webes frontendet, így a böngészőjéből irányíthatja a beszélgetést az ügynökkel.

Annak érdekében, hogy minden az AMD rendszerén maradjon, az ügynök egy, a Lemonade Server
által kiszolgált helyi modellel kommunikál. A Lemonade ezt a modellt egy OpenAI-kompatibilis
API-n keresztül teszi elérhetővé, így az Agent Canvas ugyanúgy konfigurálhatja, mint bármely
más OpenAI stílusú végpontot, miközben a modell, a kódja és a beszélgetés kontextusa mind
a saját gépén marad.

Ebben az útmutatóban elindít egy helyi modellt, elindítja az Agent Canvast, ráirányítja
arra a modellre, és futtatja az első kódolási feladatát egy valódi projektmappán.

## Amit meg fog tanulni

- Hogyan indítsa el a Lemonade Servert, és hogyan erősítse meg, hogy egy helyi modell
  válaszol a chatkérésekre
- Hogyan telepítse és indítsa el az Agent Canvast az npm csomagból
- Hogyan konfigurálja az Agent Canvast úgy, hogy egy helyi Lemonade modellt használjon LLM-ként
- Hogyan indítson el egy OpenHands beszélgetést, és figyelje meg, ahogy az ügynök fájlokat
  szerkeszt és parancsokat futtat egy munkaterületen
- Hogyan tekintse át, mit változtatott az ügynök, és hogyan irányítsa további üzenetekkel

## Alapfogalmak

| Fogalom | Mi ez | Hol helyezkedik el ebben az útmutatóban |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely egy OpenAI-kompatibilis API-t tesz elérhetővé. Az adatai soha nem hagyják el a gépét. | A modellt futtatja, amely az ügynököt működteti. |
| OpenHands | Egy AI szoftverügynök, amely fájlokat olvas és szerkeszt, parancssori utasításokat futtat, és böngészi a webet egy munkaterületen belül. | Az ügynök, amelyet a chaten keresztül irányít. |
| Agent Canvas | A böngészőalapú felhasználói felület és háttérrendszer, amely az OpenHands beszélgetéseket futtatja, és megjeleníti az eszközhívásokat és a fájlváltozásokat. | Elindítja a teljes rendszert, és otthont ad a beszélgetésének. |
| Munkaterület | A projektmappa, amelyet az ügynök olvashat és módosíthat. | Az ügynök szerkesztéseinek és parancsainak célpontja. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló-ügynök munkafolyamatok nagyobb modellből és kontextusablakból profitálnak.
> Használjon legalább 32 GB rendszermemóriát, és a nagyobb GGUF modellekhez részesítse
> előnyben a 64 GB-os vagy nagyobb memóriát.
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Szüksége lesz a következőkre:

- Telepített Lemonade Server, amely képes kiszolgálni az alábbi modellt.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb verzió, valamint `npm` (az `agent-canvas` CLI használja).
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az ügynökkiszolgáló
  környezetének kezelésére használ. Ha a rendszerén még nincs telepítve, telepítse
  az [uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/)
  az Agent Canvas elindítása előtt.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop Windowshoz](https://docs.docker.com/desktop/setup/install/windows-install/)
  telepítve és futtatva. Windows rendszeren az Agent Canvas rendszer a közzétett
  Docker-képből fut, amely tartalmazza a Node.js-t, az `uv`-t és az
  `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítenie a hoszton.
<!-- @os:end -->

- Egy projektmappa, amelyben dolgozni szeretne. Ez lehet bármilyen helyi git
  tárolómappa vagy kódkönyvtár, amelyen szeretné, hogy az ügynök dolgozzon.

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

Indítsa el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Válasszon a hardveréhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős kódoló modell, de nagy memóriakeretet igényel. Ha az eszköze korlátozott memóriával vagy GPU VRAM-mal rendelkezik, inkább válasszon egy kisebb GGUF modellt a Lemonade modellkönyvtárából, és ezt a modellazonosítót használja az útmutató további részében.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs jelen, ami a modell méretétől és az internetkapcsolatától függően eltarthat egy ideig.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé a következő címen:

```text
http://127.0.0.1:13305/api/v1
```

## 2. A helyi modell ellenőrzése

Erősítse meg, hogy a Lemonade képes kiszolgálni a kiválasztott modellt:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Ezután küldjön egy kis chatkérést:

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
a böngészőjében. A port nem speciális — ha a 8000-es már foglalt, adjon meg egy
szabad portot a `--port` (vagy `-p`) kapcsolóval az Agent Canvas indításakor:

```bash
agent-canvas --port 3000
```

Ezután nyissa meg a `http://localhost:3000` címet helyette. Az alapértelmezett helyi backendnek
egészségesként kell megjelennie a kezdőképernyőn.

Az `agent-canvas` parancs egyszerre indítja el az agent szervert, az automatizálási
backendet és a webes frontendet. Csak erre az egy parancsra van szüksége az OpenHands
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
Windows rendszeren a közzétett Agent Canvas konténerképet a Docker Desktop segítségével futtassa.
A kép tartalmazza az Agent Servert, az automatizálási backendet és a webes frontendet, így
nem kell telepítenie a Node.js-t, az `uv`-t, sem a CLI-t a gazdagépre.

Először hozza létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltse le a közzétett image-et (nyilvános, így nincs szükség bejelentkezésre):

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
foglalt, rendeljen hozzá egy másik gazdagép-portot, például `-p 8080:8000`, és nyissa meg helyette a
`http://localhost:8080/canvas` címet.

> **Megjegyzés:** Az első indításkor az Agent Server inicializálódik a konténeren belül,
> így eltarthat egy-két percig, mire a backend egészségesnek jelenti magát.

A `.openhands` csatolás megőrzi az LLM-profilt és a beállításokat a konténer
újraindításai között. A jelen útmutató további részében mindent az Agent
Canvas felhasználói felületén konfigurálunk a böngészőben.

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

1. Hagyja kijelölve az **OpenHands** agentet, majd kattintson a **Next** gombra.
2. A **Set up your LLM** résznél válassza az **Advanced** opciót.
3. Hagyja az **Authentication** beállítást **API key** értéken.
4. Állítsa be a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa be a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Windows rendszeren a stack egy konténerben fut, amely nem éri el a gazdagépet a
   > `127.0.0.1` címen. Használja helyette a `http://host.docker.internal:13305/api/v1` címet, hogy
   > a konténerizált agent elérhesse a Windows gazdagépen futó Lemonade-et.
   <!-- @os:end -->
6. Az **API Key** mezőbe adjon meg bármilyen nem üres helyőrző értéket, például `lemonade-local`.
   A Lemonade-nek nincs szüksége valódi kulcsra, de az OpenHands kliensnek szüksége van egy
   küldendő értékre.
7. Kattintson a **Next** gombra.

A kész Advanced beállításoknak így kell kinézniük. Az API key mezőt az
UI elrejti.

![Agent Canvas első használatkori LLM Advanced beállításai a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Az Agent Canvas ezeket az értékeket LLM-profilként menti. Ha a verziója a profil
elnevezését kéri, használjon szóköz nélküli nevet, például `lemonade-local`. Ha később
modellt vált, nyissa meg a **Settings > LLM** menüt, és frissítse ugyanazokat az Advanced
mezőket. A mentett profilok között a chat beviteli mezőből válthat a `/model` paranccsal.

## 5. Munkaterület megnyitása

Az agent csak azokat a fájlokat tudja olvasni és módosítani, amelyek a Ön által
kiválasztott munkaterületen belül vannak. Mielőtt elindítana egy feladatot, irányítsa
az Agent Canvast a projekt mappájára:

1. A kezdőképernyőről válassza az **Open Workspace** opciót.
2. Válassza ki a projektjét tartalmazó mappát (például egy git repozitóriumot,
   amelyen szeretné, hogy az agent dolgozzon).
3. Indítson új beszélgetést ebben a munkaterületben.

Minden, amit az agent végez — fájlok olvasása, parancsok futtatása, kód szerkesztése —
erre a munkaterületre korlátozódik.

![Agent Canvas kezdőlap a bevezető folyamat után](assets/02-agent-canvas-home.png)

## 6. Az első kódolási feladat futtatása

A munkaterület megnyitásával és a helyi LLM kiválasztásával írjon be egy konkrét
feladatot a chatbe. Egy jó első feladat kicsi és ellenőrizhető, például:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Figyelje a beszélgetés idővonalát. Az OpenHands:

- Beolvassa a munkaterületet, hogy megértse az elrendezést.
- Létrehozza a `hello.py` fájlt a kért függvénnyel és teszt-blokkal.
- Opcionálisan lefuttatja a `python3 hello.py` parancsot a kimenet ellenőrzéséhez.
- Beszámol a chatben arról, hogy mit tett, és minden parancskimenetről.

Látnia kell, ahogy az új fájl megjelenik a munkaterületen, és az agent utolsó
üzenetének le kell írnia az elvégzett módosítást. Ez a jutalom pillanata: az
agent valódi kódot írt és futtatott a projekt mappájában.

## 7. Az agent munkájának átnézése és irányítása

Miután az agent befejez egy lépést, nézze át a munkáját, mielőtt elfogadná a
következőt:

- **Fájlváltozások**: használja a munkaterület fájlböngészőjét vagy az agent
  diff-nézetét, hogy pontosan lássa, mi lett hozzáadva, módosítva vagy törölve.
- **Parancskimenet**: bontsa ki bármelyik futtatott parancsot, hogy lássa a
  stdoutot, a stderrt és a kilépési kódot.
- **Visszajelzések**: ha az eredmény nem a kívánt, válaszoljon ugyanabban a
  beszélgetésben egy korrekcióval. Az agent megtartja a korábbi kontextust,
  és ugyanazokon a fájlokon folytatja az iterálást.

Például, ha a teszt nem a várt üdvözlést írta ki, válaszoljon ezzel:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Az agent újra beolvassa a fájlt, futtatja a parancsot, diagnosztizálja a
problémát, és ismét szerkeszti a fájlt — mindezt ugyanabban a beszélgetésben.
## Hibaelhárítás

<!-- @os:linux -->
- **A `agent-canvas` nincs rajta a PATH-on:** telepítsd újra a
  `npm install -g @openhands/agent-canvas` paranccsal, és győződj meg róla, hogy
  az npm globális bináris könyvtára szerepel a PATH-ban, mielőtt az
  `agent-canvas`-t új terminálból el tudnád indítani.
- **Az `npm install -g` jogosultsági hibával hiúsul meg:** állíts be egy
  felhasználói tulajdonú globális npm könyvtárat, majd nyisd meg újra a
  terminált, és telepítsd újra az Agent Canvas-t.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Hiányzik az `uv`:** telepítsd
  [a uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/).
  Az Agent Canvas a `uv` eszközzel kezeli az agent szerver Python környezetét.
<!-- @os:end -->

<!-- @os:windows -->
- **A `docker pull` vagy `docker run` nem tud kapcsolódni:** győződj meg róla,
  hogy a Docker Desktop fut (a bálna ikon megjelenik a tálcán), és hogy a motor
  elindítása befejeződött. A `docker version` parancsnak egyaránt ki kell írnia
  egy Client és egy Server szakaszt.
- **A konténer elindul, de a backend soha nem válik egészségessé:** az első
  indítás inicializálja az Agent Servert a konténeren belül; adj neki egy-két
  percet, majd ellenőrizd a `docker logs <container>` kimenetét hibák
  szempontjából.
- **A konténer nem éri el a Lemonade-et:** a konténer a `host.docker.internal`
  címen éri el a hostot. Győződj meg róla, hogy a Lemonade fut a Windows
  hoston a `lemonade status` paranccsal, és a LLM konfigurálásakor
  `http://host.docker.internal:13305/api/v1` címet add meg Base URL-ként.
<!-- @os:end -->

- **A felület betöltődik, de a backend nem egészséges állapotot mutat:** várj
  egy-két percet, amíg az agent szerver befejezi az indulást, majd frissítsd az
  oldalt. Ha továbbra is nem egészséges, indítsd újra a stacket, és nézd meg a
  naplókat hibák után kutatva.
- **A Lemonade chat kérések kapcsolódási hibával hiúsulnak meg:** ellenőrizd,
  hogy a `curl -fsS "http://127.0.0.1:13305/api/v1/health"` sikeres-e, és hogy
  a Lemonade még mindig kiszolgálja-e a modellt a `lemonade status` paranccsal.
- **Az agent kontextushossz- vagy token-limit üzenettel hibázik:** kezdj új
  beszélgetést, hogy az agent ne cipeljen magával túl nagy előzményt. Ha ez
  rendszeresen előfordul, indítsd újra a Lemonade-et az alapértelmezett 65536
  helyett nagyobb `ctx_size` értékkel (például `ctx_size=131072`), ha a memória
  engedi.
- **Az agent gyenge minőségű vagy hiányos szerkesztéseket készít:** válts
  nagyobb modellre a Lemonade-ben, vagy adj az agentnek kisebb, konkrétabb
  feladatot, és hagyd, hogy befejezze, mielőtt a következő változtatást kéred.

## Következő lépések

- Próbálj ki egy nagyobb feladatot ugyanabban a munkaterületben, például adj
  hozzá egy unit teszt fájlt vagy javíts egy ismert hibát, és nézd át az agent
  diffjét, mielőtt megtartanád a változtatást.
- Csatlakoztass egy MCP szervert, például GitHubot vagy Slacket a
  **Customize** alatt, hogy az agent munka közben olvashasson issue-kat vagy
  tehessen közzé frissítéseket.
- Mentsd el több LLM profilt (egy gyors, kis modellt és egy erősebb, nagy
  modellt), és válts közöttük a `/model` paranccsal beszélgetés közben.
- Lépj tovább az [OpenHands automatizálásokhoz](https://docs.openhands.dev/openhands/usage/automations/overview), hogy az
  ismétlődő fejlesztési folyamatokat ütemezett vagy eseményalapú agent futtatásokká alakítsd.

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