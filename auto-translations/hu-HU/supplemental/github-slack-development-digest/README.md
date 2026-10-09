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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Áttekintés

A fejlesztők rengeteg időt töltenek apró, ismétlődő feladatkörökkel: címkézett pull requestek átnézésével, GitHub megjegyzésekre való válaszadással, új issue-k priorizálásával, Slack beszélgetési szálak napi állapotjelentéssé vagy incidens-utókövetéssé alakításával, illetve release- vagy kutatási jelzések nyomon követésével.
Minden ilyen feladatkör ismerős, mégis megítélést igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít fontosnak, és egyértelmű frissítést kell közzétenni ott, ahol a csapat már dolgozik.

Az [OpenHands automatizációk](https://docs.openhands.dev/openhands/usage/automations/overview) ezeket a feladatköröket ütemezett vagy eseményindítású ágensbeszélgetésekké alakítják: olyan futtatásokká, amelyekben egy AI szoftverágens kontextust olvashat, eszközöket hívhat meg, és frissítést készíthet.
Az OpenHands bővítménykatalógusban található megosztott automatizációs sablonok ezt a mintát követik GitHub pull request áttekintéshez, repository-megfigyeléshez, Linear issue priorizáláshoz, incidens-utóelemzésekhez, Slack napi állapot-összefoglalókhoz és kutatási összefoglalókhoz: egy automatizáció aktiválódik, konfigurált integrációkat (például GitHub-ot vagy Slacket) használ a kontextus lekéréséhez, egy nagy nyelvi modellel (LLM) következtet erre a kontextusra, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az a helyi vezérlőközpont, amely ezen automatizációk létrehozására és teszteléséhez szolgál.
Ebben az útmutatóban egy OpenHands Agent Servert futtat, amely az a háttérfolyamat, ami végrehajtja az ágensbeszélgetéseket, és összeköti az ágenst külső szolgáltatásokkal, például GitHub-bal és Slackkel.

Ahhoz, hogy a munkafolyamat az AMD rendszeren maradjon, az ágens egy helyi, Lemonade Server által kiszolgált modellel kommunikál.
A Lemonade ezt a modellt egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé, így az Agent Canvas úgy konfigurálhatja, mintha egy távoli, OpenAI-stílusú végpont lenne, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben az útmutatóban egy konkrét automatizációt fogsz felépíteni: egy ütemezett GitHub-ból Slackbe küldött fejlesztési összefoglalót.
Ez a GitHub-ot használja a legutóbbi repository-tevékenység vizsgálatához, a Slacket az összefoglaló közzétételéhez, az Agent Canvas API-hívásait az automatizáció konfigurálásához és teszteléséhez, valamint a Lemonade-et az LLM helyi futtatásához.

![Architektúra ábra, amely a GitHub MCP-t, az OpenHands automatizációt, a Lemonade Servert és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Amit tanulni fogsz

- Hogyan indítsd el a Lemonade Servert, és hogyan ellenőrizd, hogy egy helyi modell válaszol a csevegési kérésekre
- Hogyan indítsd el az Agent Canvast, és hogyan irányítsd az Agent Serverét egy helyi LLM-re
- Hogyan telepíts GitHub és Slack Model Context Protocol (MCP) szervereket az Agent Server API-n keresztül
- Hogyan hozz létre és indíts el egy ütemezett OpenHands automatizációt, amely fejlesztési összefoglalót tesz közzé Slackben
- Hogyan hárítsd el a leggyakoribb helyi modellel és automatizációval kapcsolatos hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe az útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | Futtatja az ágenst meghajtó modellt. |
| OpenHands Agent Server | Az a háttérfolyamat, amely végrehajtja az OpenHands ágensbeszélgetéseket. | Üzemelteti az ágenst, annak LLM-profilját és MCP szervereit. |
| Agent Canvas | Az OpenHands helyi vezérlőközpontja, amely futtatja az Agent Servert és egy felhasználói felületet az ágensfuttatások vizsgálatához. | Elindítja a háttérrendszereket, és biztosítja a meghívott API-t. |
| MCP szerver | Egy Model Context Protocol szerver, amely eszközöket ad egy ágensnek egy külső szolgáltatáshoz, például GitHub-hoz vagy Slackhez. | Lehetővé teszi az ágens számára, hogy olvassa a GitHub-ot és írjon a Slackbe. |
| OpenHands automatizáció | Egy ütemezett vagy eseményindítású ágensbeszélgetés, amely kontextust kér le, következtet rá, és valahol eredményt ír ki. | Az itt felépített GitHub-ból Slackbe küldött összefoglaló. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló-ágens munkafolyamatok nagyobb modellből és kontextusablakból profitálnak.
> Használj legalább 32 GB rendszermemóriát, és a nagyobb GGUF modellekhez inkább 64 GB-ot vagy többet.
<!-- @device:end -->

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Szükséged lesz a következőkre:

- A Lemonade Server, telepítve a szabványos [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb, valamint `npm`, amelyekkel telepítheted a publikált Agent Canvas CLI-t, és az `npx` segítségével futtathatod az MCP szervereket.
- `uv`, az a Python csomagkezelő, amelyet az Agent Canvas az Agent Server környezetének felépítéséhez használ. Ha még nincs telepítve, telepítsd az [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján.
- Egy friss, publikált `@openhands/agent-canvas` csomag, amely séma-alapú ágensbeállításokat, `LLMSummarizingCondenserSettings.max_tokens`-t és LLM `custom_tokenizer` támogatást tartalmaz.
- A Python `transformers` csomagjának elérhetőnek kell lennie az Agent Server környezetében. Ez szükséges a csevegési sablon alapú tokenszámláláshoz, amikor a `custom_tokenizer` be van állítva.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), telepítve és futtatva. Windows alatt az Agent Canvas verem a publikált Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t, a `transformers`-t és az `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítened a hosztgépen.
<!-- @os:end -->

- Egy GitHub token, amely olvasási jogosultsággal rendelkezik az összefoglalandó repository-hoz.
- Egy Slack bot token (`xoxb-...`), `chat:write` és csatorna-olvasási jogosultsággal.
- Egy Slack csapat-azonosító (`T...`).
- Egy Slack csatorna-azonosító (`C...`), ahová az összefoglalót közzé kell tenni.

Hívd meg a Slack appot a célcsatornára, mielőtt tesztelnéd az automatizációt.
## A playbookban használt változók

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Ezt a két változót az alábbi ellenőrző parancsok használják.
A modellt, a tokenizert és a többi LLM-beállítást a későbbi lépésekben közvetlenül az Agent Canvas felhasználói felületén adjuk meg, ezért ezek konkrét értékei ott jelennek meg, ahol szükségesek.

A következő értékeket a későbbi lépésekben az Agent Canvas felhasználói felületén kell megadni.
Állítsd be őket itt, hogy később be tudd másolni:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Használj egyértelmű `owner/repo` értéket a `GITHUB_REPO_FILTER` paraméterhez.
A túl tág szervezeti helyettesítő karakterek túl sok MCP-kontextust adhatnak vissza a helyi modellek számára.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. A Lemonade szerver elindítása

Indítsd el a modellt a Lemonade parancssori felületéről:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Válassz olyan modellt, amely illeszkedik a hardveredhez.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) erős modell ehhez a munkafolyamathoz, de nagy memóriakeretet igényel.
> Ha az eszközödön kevesebb memória vagy GPU VRAM áll rendelkezésre, válassz egy kisebb GGUF modellt a Lemonade modellkönyvtárából, és ezt a modellazonosítót (valamint a hozzá illő tokenizert) használd a playbook során mindvégig.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs meg, ami a modell méretétől és az internetkapcsolatodtól függően eltarthat egy ideig.

A Lemonade OpenAI-kompatibilis API-t biztosít itt:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálási futtató nem ugyanazon a gépen fut, tedd elérhetővé a Lemonade végpontot egy biztonságos alagúton keresztül, és használd a HTTPS URL-t LLM alap URL-ként.
Az [ngrok](https://ngrok.com/) egy helyi portot tesz elérhetővé az interneten egy biztonságos HTTPS URL-en keresztül; ehhez ingyenes ngrok fiók szükséges, és a `YOUR_NGROK_DOMAIN.ngrok-free.dev` részt a saját, lefoglalt domainedre kell cserélned:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Győződj meg róla, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ezután küldj egy kis chat kérést:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Ezután küldj egy kis chat kérést:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Az Agent Canvas elindítása

<!-- @os:linux -->
Telepítsd a közzétett Agent Canvas csomagot, és indítsd el a teljes rendszert:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm telepítés jogosultsági hibával meghiúsul, lásd az alábbi npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul el.
Nyisd meg ezt az URL-t a böngésződben.
A port nem speciális – ha a 8000-es port már foglalt, adj meg egy szabad portot a `--port` (vagy `-p`) kapcsolóval.
Az alapértelmezett helyi háttérrendszernek a kezdőképernyőn egészségesként kell megjelennie.

> **Megjegyzés:** Az első indítás felépíti az Agent Server `uv`-vel kezelt Python-környezetét, így eltarthat néhány percig, mire a háttérrendszer egészségesnek jelzi magát.

Az `agent-canvas` parancs egyszerre indítja el az agent szervert, az automatizálási háttérrendszert és a webes felhasználói felületet.
Csak erre az egyetlen parancsra van szükséged az OpenHands helyi futtatásához.
A playbook további része az Agent Canvas felhasználói felületén keresztül, a böngésződben konfigurál mindent.
<!-- @os:end -->

<!-- @os:windows -->
Windows rendszeren a közzétett Agent Canvas konténerképet a Docker Desktop segítségével futtasd.
A kép tartalmazza az Agent Servert, az automatizálási háttérrendszert és a webes felhasználói felületet, így nem kell Node.js-t, `uv`-t vagy a parancssori felületet telepítened a gazdagépre.

Először hozd létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltsd le a közzétett képet (kb. 6 GB; nyilvános, így bejelentkezés nem szükséges):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Ezután indítsd el a rendszert:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Nyisd meg a `http://localhost:8000/canvas` címet a böngésződben.
Ha a 8000-es port már foglalt, rendelj hozzá egy másik gazdagépi portot, például `-p 8080:8000`, és ehelyett a `http://localhost:8080/canvas` címet nyisd meg.

> **Megjegyzés:** Az első indítás felépíti az Agent Server környezetét a konténeren belül, így eltarthat néhány percig, mire a háttérrendszer egészségesnek jelzi magát.

A `.openhands` csatolás megőrzi az LLM profilodat, az MCP szervereket és az automatizálásokat a konténer újraindításai között.
A playbook további része az Agent Canvas felhasználói felületén keresztül, a böngésződben a `http://localhost:8000/canvas` címen konfigurál mindent.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
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
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
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
## 4. A helyi LLM konfigurálása a felhasználói felületen

Első indításkor az Agent Canvas egy bevezető folyamatot nyit meg.
Ebben a folyamatban:

1. Hagyd kiválasztva az **OpenHands** ügynököt, majd kattints a **Next** gombra.
2. A **Set up your LLM** résznél válaszd az **Advanced** lehetőséget.
3. Hagyd az **Authentication** mezőt **API key** értéken.
4. Állítsd a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsd a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe írj be egy tetszőleges, nem üres helyőrzőt, például `lemonade-local` értéket. A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van valamilyen értékre a küldéshez.

<!-- @os:windows -->
> **Windows (Docker):** az Agent Server a konténeren belül fut, ezért a **Base URL** mezőt a `http://host.docker.internal:13305/api/v1` értékre állítsd a `http://127.0.0.1:13305/api/v1` helyett.
> A konténeren belülről a `127.0.0.1` magát a konténert jelenti; a `host.docker.internal` a Windows gazdagépen futó Lemonade-et éri el, és a Docker Desktop automatikusan biztosítja ezt a gazdagépnevet.
<!-- @os:end -->

A kapcsolati mezőknek az alábbiakhoz hasonlóan kell kinézniük.
Az API kulcs mezőt a felhasználói felület elrejti.

![Agent Canvas első használatkori LLM Advanced beállításai a Lemonade modellel és a helyi alap URL-lel](assets/01-llm-advanced-settings.png)

Ezután válaszd az **All** fület, és add meg a kiegészítő helyi modell mezőket:

1. Görgess a **Custom Tokenizer** mezőhöz, és állítsd be erre: `Qwen/Qwen3.6-35B-A3B`.
2. Görgess a **LiteLLM Extra Body** mezőhöz, és állítsd be erre: `{"enable_thinking": true}`.
3. Kattints a **Next** gombra.

![Agent Canvas első használatkori LLM All fül a Qwen egyéni tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas első használatkori LLM All fül a beállított LiteLLM extra body mezővel](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak az alábbiakat kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag jelzi a LiteLLM-nek, hogy OpenAI-kompatibilis kérésformázást használjon a Lemonade végponttal szemben.
Az egyéni tokenizáló a GGUF modell eredeti Hugging Face tokenizálója; ez lehetővé teszi, hogy az OpenHands ugyanazokat a chat-sablon tokeneket számolja, mint amelyeket a helyi modellkiszolgáló lát.
A jelenlegi első használatkori LLM űrlap nem mutat kondenzáló (condenser) beállításokat.
Ha az Agent Canvas build-ed később megjeleníti a kondenzáló beállításokat a **Settings > LLM** alatt, használd a `llm_summarizing` értéket, és állítsd a maximális tokenszámot a Lemonade kontextusablak alá, például `56000` értékre.

## 5. GitHub és Slack MCP kiszolgálók telepítése

Az Agent Canvas felhasználói felületen nyisd meg a **Customize** (vagy **Settings > MCP**) lehetőséget, hogy hozzáadd azokat az MCP kiszolgálókat, amelyek eszközöket biztosítanak az ügynöknek a GitHubhoz és a Slackhez.
A tokenértékek csak a helyi Agent Serverhez kerülnek elküldésre, és titkosított beállításként maradnak meg.

<!-- @os:windows -->
> **Windows (Docker):** az alábbi `npx` MCP kiszolgáló parancsok a konténeren belül futnak, amely már tartalmazza a Node.js-t, így a gazdagépen semmi extra nem kerül telepítésre.
> Mivel a `.openhands` csatolva van, az MCP kiszolgálók és tokenjeik megmaradnak a konténer újraindításai között is.
<!-- @os:end -->

### GitHub MCP kiszolgáló

Adj hozzá egy új MCP kiszolgálót az alábbi beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = a GitHub tokened |

Használj olyan GitHub tokent, amelynek olvasási hozzáférése van az összegezni kívánt repóhoz.

### Slack MCP kiszolgáló

Adj hozzá egy második MCP kiszolgálót az alábbi beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = a digest csatornád azonosítója |

Állítsd a `SLACK_CHANNEL_IDS` értékét a digest csatorna azonosítójára (ugyanarra az értékre, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne kelljen minden Slack csatornát végiglapoznia.

Miután hozzáadtad mindkét kiszolgálót, használd a **Test** gombot mindegyiken, hogy megerősítsd a kapcsolódásukat és az eszközeik hirdetését.
A GitHub kiszolgálónak GitHub eszközöket kell listáznia, a Slack kiszolgálónak pedig Slack eszközöket.

![Agent Canvas MCP oldal a telepített GitHub és Slack kiszolgálókkal](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. A digest automatizálás létrehozása

Az Agent Canvas felhasználói felületen nyisd meg az **Automations** oldalt, és hozz létre egy új automatizálást:

1. Válaszd a **Create automation** lehetőséget, majd a **Prompt preset** típust.
2. Állítsd a **Name** mezőt erre: `GitHub Development Digest to Slack`.
3. Állítsd a **Prompt** mezőt az alábbi szövegre, a repó és a csatorna helyőrzőit a saját értékeidre cserélve:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Állítsd a **Trigger** mezőt **Cron** értékre a `0 9 * * 1-5` ütemezéssel (hétköznaponként reggel 9 órakor), és állítsd be a **Timezone** mezőt a saját időzónádra, például `America/New_York` értékre.
5. Állítsd a **Timeout** mezőt `900` másodpercre.
6. Mentsd el az automatizálást.

Az automatizálás részletező oldala megjeleníti az új automatizálást a cron triggerrel és a generált prompt-preset belépési ponttal.

![Agent Canvas automatizálás részletező oldala a létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az Agent Canvas felület automatizálás-részletező oldaláról:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra, hogy az automatizálást azonnal, egyszer lefuttassa.
2. Figyelje a futáslistát ugyanazon az oldalon. A legutóbbi futásnak `COMPLETED` állapotba kell kerülnie.
3. Nyissa meg a cél Slack-csatornát. Tartalmaznia kell a generált digestet.

Nem szükséges megvárnia a cron ütemezés aktiválódását – a **Run now** gombbal igény szerint indítható futás, így előre ellenőrizheti, hogy a prompt, az MCP-kapcsolatok és a Slack-posztolás mind megfelelően működnek, mielőtt az ütemezésre hagyatkozna.

![Agent Canvas automatizálási futás sikeresen befejeződött](assets/06-automation-run-completed.png)

![Slack-csatorna, amely megjeleníti a generált OpenHands digestet](assets/07-slackbot-message.png)

## Hibaelhárítás

<!-- @os:windows -->
- **A Docker 8000-es portja már használatban van:** rendeljen hozzá egy másik host portot, például: `docker run ... -p 8080:8000 ...`, majd nyissa meg a `http://localhost:8080/canvas` címet.
- **A `docker pull` hitelesítési hibával meghiúsul** (például: "A specified logon session does not exist"): futtassa a pull műveletet interaktív Windows-munkamenetből, vagy húzza le előre a képet. A kép nyilvános, így nincs szükség `docker login` parancsra.
- **A felület betöltődik, de a backend nem egészséges:** az első indításkor a konténeren belül épül fel az Agent Server környezete. Várjon egy percet, majd frissítse az oldalt, ezután ellenőrizze a folyamatot a `docker logs <container>` paranccsal.
- **Az Agent Canvas nem éri el a Lemonade-ot a konténerből:** állítsa be az LLM **Base URL** mezőjét a `http://host.docker.internal:13305/api/v1` értékre (ne a `127.0.0.1` címet), és győződjön meg róla, hogy a Lemonade fut a Windows hoston.
<!-- @os:end -->

- **A Lemonade leállt:** indítsa újra az 1. lépésben szereplő `lemonade run "${LEMONADE_MODEL}"` paranccsal, majd futtassa újra az állapotellenőrzést.
- **Az `npm install -g` jogosultsági hibával meghiúsul:** Linuxon vagy WSL-en állítson be egy felhasználói tulajdonú globális npm könyvtárat, adja hozzá a shell indítófájljához, majd telepítse újra az Agent Canvast:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ha `zsh`-t használ, ugyanezt az `export PATH=...` sort a `~/.bashrc` helyett a `~/.zshrc` fájlhoz adja hozzá.
- **Az Agent Canvas elutasítja az LLM-beállításokat a `custom_tokenizer` megadása után:** telepítse a `transformers` csomagot az Agent Server Python-környezetébe, szükség esetén indítsa újra az Agent Canvast, majd próbálja meg újra menteni az LLM-beállításokat. Az OpenHandsnek szüksége van a Transformers csomagra a tokenizáló chat-sablonjának betöltéséhez, ha a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-ot:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancs kimenetét, és győződjön meg róla, hogy az első használatkor megjelenő LLM-űrlapon vagy a **Settings > LLM** menüben megadott alap URL megegyezik a futó helyi végponttal vagy HTTPS-alagúttal.
- **Az LLM-beállítások nem mentődtek el:** győződjön meg róla, hogy az értékek megadása után rákattintott a **Next** gombra. Nyissa meg újra a **Settings > LLM** menüt, hogy ellenőrizze, az értékek megmaradtak-e.
- **A GitHub MCP nem látja a privát tárolókat:** ellenőrizze, hogy a GitHub token rendelkezik-e olvasási jogosultsággal a cél tárolóhoz, valamint hogy a MCP **Test** gombja a **Customize** menüben megjeleníti-e a GitHub eszközöket.
- **A Slack tudja olvasni a csatornákat, de nem tud posztolni:** hívja meg a Slack alkalmazást a cél csatornába, és győződjön meg róla, hogy a bot rendelkezik `chat:write` jogosultsággal.
- **Az automatizálás túl sok Slack-csatornát listáz:** használjon Slack-csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálási futás meghiúsul vagy túllépi a kontextust:** győződjön meg róla, hogy a Lemonade `ctx_size=65536` beállítással indult el, hogy az OpenHands LLM-nél be van állítva a `custom_tokenizer`, és használjon egy explicit tárolót, a GitHub eredményhalmazokat pedig korlátozza 3-5 elemre. Ha az Agent Canvas build-je kínál condenser-beállításokat, állítsa a condenser maximális tokenszámát a Lemonade kontextusablaka alá.

## Következő lépések

- Adjon hozzá egy heti, csak kiadásokra vonatkozó digestet.
- Adjon hozzá egy GitHub eseményindítású automatizálást a gyorsabb PR- vagy push-riasztásokhoz.
- Irányítsa ugyanazt a digestet Notionba, Linearbe vagy egy másik MCP-alapú eszközbe.

## Erőforrások

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server dokumentáció](https://lemonade-server.ai/docs)
- [OpenHands bővítmények tárolója](https://github.com/OpenHands/extensions)
- [Model Context Protocol szerverek](https://github.com/modelcontextprotocol/servers)
- [Slack MCP csomag](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->