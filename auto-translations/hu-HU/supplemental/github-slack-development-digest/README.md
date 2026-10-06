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

A fejlesztők rengeteg időt töltenek kis, ismétlődő feladatokkal: címkézett pull requestek áttekintésével, GitHub-megjegyzésekre válaszolással, új hibajegyek triázsolásával, Slack-beszélgetések állapotjelentésekké vagy incidens-utánkövetésekké alakításával, valamint kiadási vagy kutatási jelzések nyomon követésével.
Minden ilyen feladat ismerős, mégis döntéshozatalt igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít, és világos frissítést kell közzétenni ott, ahol a csapat már amúgy is dolgozik.

Az [OpenHands automatizálások](https://docs.openhands.dev/openhands/usage/automations/overview) ezeket a feladatokat ütemezett vagy eseményindította ügynöki beszélgetésekké alakítják: olyan futásokká, amelyekben egy mesterséges intelligencia-alapú szoftverügynök kontextust olvas, eszközöket hív meg, és frissítést készít.
Az OpenHands bővítménykatalógusában található megosztott automatizálási sablonok ezt a mintát követik a GitHub pull request felülvizsgálathoz, a tárolók megfigyeléséhez, a Linear hibajegy-triázshoz, az incidens utólagos elemzésekhez, a Slack állapotjelentés-összefoglalókhoz és a kutatási összefoglalókhoz: egy automatizálás elindul, konfigurált integrációkat, például GitHubot vagy Slacket használ a kontextus lekéréséhez, ezt a kontextust egy nagy nyelvi modellel (LLM) elemzi, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az ilyen automatizálások helyi felépítésére és teszteléséhez szolgáló helyi vezérlősík.
Ebben a gyakorlati útmutatóban egy OpenHands Agent Servert futtat, amely az ügynöki beszélgetéseket végrehajtó háttérfolyamat, és összekapcsolja az ügynököt külső szolgáltatásokkal, például a GitHubbal és a Slackkel.

Ahhoz, hogy a munkafolyamat az AMD rendszeren maradjon, az ügynök egy, a Lemonade Server által kiszolgált helyi modellel kommunikál.
A Lemonade egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé ezt a modellt, így az Agent Canvas úgy konfigurálhatja, mintha egy távoli OpenAI-stílusú végpont lenne, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben a gyakorlati útmutatóban egy konkrét automatizálást fogsz felépíteni: egy ütemezett GitHub-ból Slack-be küldött fejlesztési összefoglalót (digest).
Ez a GitHub-ot használja a legutóbbi tárolótevékenység megvizsgálásához, a Slacket az összefoglaló közzétételéhez, az Agent Canvas API-hívásokat az automatizálás konfigurálásához és teszteléséhez, valamint a Lemonade-ot az LLM helyi futtatásához.

![Architektúra-diagram, amely a GitHub MCP-t, az OpenHands automatizálást, a Lemonade Servert és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Mit fogsz megtanulni

- Hogyan indítsd el a Lemonade Servert, és hogyan ellenőrizd, hogy egy helyi modell válaszol-e csevegési kérésekre
- Hogyan indítsd el az Agent Canvas-t, és hogyan irányítsd az Agent Serverét egy helyi LLM-re
- Hogyan telepíts GitHub és Slack Model Context Protocol (MCP) szervereket az Agent Server API-n keresztül
- Hogyan hozz létre és indíts el egy ütemezett OpenHands automatizálást, amely fejlesztési összefoglalót tesz közzé a Slacken
- Hogyan hárítsd el a leggyakoribb helyi modell- és automatizálási hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe a gyakorlati útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | Futtatja az ügynököt meghajtó modellt. |
| OpenHands Agent Server | Az OpenHands ügynöki beszélgetéseket végrehajtó háttérfolyamat. | Ez tárolja az ügynököt, annak LLM-profilját és MCP szervereit. |
| Agent Canvas | Az OpenHands helyi vezérlősíkja, amely futtatja az Agent Servert és egy felhasználói felületet az ügynöki futások vizsgálatához. | Elindítja a háttérrendszereket, és biztosítja az általad meghívott API-t. |
| MCP szerver | Egy Model Context Protocol szerver, amely eszközöket biztosít az ügynöknek egy külső szolgáltatáshoz, például a GitHubhoz vagy a Slackhez. | Lehetővé teszi az ügynöknek a GitHub olvasását és a Slackre írást. |
| OpenHands automatizálás | Egy ütemezett vagy eseményindította ügynöki beszélgetés, amely kontextust kér le, azt elemzi, majd valahová eredményt ír. | Az itt felépített GitHub-ból Slack-be küldött összefoglaló. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló ügynöki munkafolyamatok nagyobb modellből és kontextusablakból profitálnak.
> Használj legalább 32 GB rendszermemóriát, és nagyobb GGUF modellekhez inkább 64 GB-ot vagy többet részesíts előnyben.
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Szükséged lesz:

- Telepített Lemonade Serverre, a szokásos [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb verzióra és `npm`-re, amelyekkel a közzétett Agent Canvas CLI telepíthető, és az MCP szerverek `npx` segítségével futtathatók.
- `uv`-re, a Python csomagkezelőre, amelyet az Agent Canvas az Agent Server környezet felépítéséhez használ. Ha még nincs telepítve, telepítsd az [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján.
- Egy friss, közzétett `@openhands/agent-canvas` csomagra, amely séma-vezérelt ügynökbeállításokat, `LLMSummarizingCondenserSettings.max_tokens`-t és LLM `custom_tokenizer` támogatást tartalmaz.
- A Python `transformers` csomagra, amelynek elérhetőnek kell lennie az Agent Server környezetében. Erre a csevegősablon-alapú tokenszámláláshoz van szükség, ha a `custom_tokenizer` be van állítva.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)-ra, telepítve és futtatva. Windows rendszeren az Agent Canvas verem a közzétett Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t, a `transformers`-t és az `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítened a hoszton.
<!-- @os:end -->

- Egy GitHub tokenre, amely olvasási hozzáféréssel rendelkezik az összefoglalni kívánt tárolóhoz.
- Egy Slack bot tokenre (`xoxb-...`), amely `chat:write` és csatornaolvasási jogosultsággal rendelkezik.
- Egy Slack csapatazonosítóra (`T...`).
- Egy Slack csatornaazonosítóra (`C...`), ahová az összefoglalót közzé kell tenni.

Az automatizálás tesztelése előtt hívd meg a Slack alkalmazást a célcsatornába.
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
A modellt, a tokenizert és a többi LLM-beállítást a későbbi lépésekben közvetlenül az Agent Canvas felületén adjuk meg, ezért ezek konkrét értékei ott, a helyszínükön, beágyazva jelennek meg, ahol szükséged van rájuk.

A következő értékeket a későbbi lépésekben az Agent Canvas felületén kell megadni.
Állítsd be őket itt, hogy később be tudd másolni azokat:

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

A `GITHUB_REPO_FILTER` esetében egy explicit `owner/repo` értéket használj.
A túl általános szervezeti helyettesítő karakterek (wildcard) túl sok MCP kontextust adhatnak vissza a helyi modellek számára.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. A Lemonade Server elindítása

Indítsd el a modellt a Lemonade parancssori felületéről (CLI):

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

> **Válassz a hardveredhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős modell ehhez a munkafolyamathoz, de nagy memóriakeszletet igényel.
> Ha az eszközöd memóriája vagy GPU VRAM-ja korlátozott, válassz egy kisebb GGUF modellt a Lemonade modellkönyvtárából, és azt a modellazonosítót (és a hozzá illő tokenizert) használd a playbook során mindvégig.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs jelen, ami a modell méretétől és az internetkapcsolattól függően eltarthat egy ideig.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé a következő címen:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálási futtató nincs ugyanazon a gépen, tedd elérhetővé a Lemonade végpontot egy biztonságos alagúton (tunnel) keresztül, és a HTTPS URL-t használd LLM alap URL-ként.
Az [ngrok](https://ngrok.com/) egy helyi portot tesz elérhetővé az interneten egy biztonságos HTTPS URL-en keresztül; ehhez egy ingyenes ngrok fiók szükséges, és a `YOUR_NGROK_DOMAIN.ngrok-free.dev` részt a saját fenntartott domainedre kell cserélned:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Erősítsd meg, hogy a Lemonade képes kiszolgálni a kiválasztott modellt:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Majd küldj egy kisebb chat kérést:

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

Majd küldj egy kisebb chat kérést:

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
Telepítsd a publikált Agent Canvas csomagot, és indítsd el a teljes rendszert (stack):

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm telepítés jogosultsági hibával hiusul meg, nézd meg az alábbi npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyisd meg ezt az URL-t a böngésződben.
A port nem speciális – ha a 8000 már foglalt, adj meg bármilyen szabad portot a `--port` (vagy `-p`) kapcsolóval.
Az alapértelmezett helyi háttérrendszernek (backend) egészségesként kell megjelennie a kezdőképernyőn.

> **Megjegyzés:** Az első indítás felépíti az Agent Server `uv`-vel kezelt Python környezetét, így eltarthat néhány percig, mire a háttérrendszer egészségesként jelentkezik.

Az `agent-canvas` parancs egyszerre indítja el az agent servert, az automatizálási háttérrendszert és a webes felhasználói felületet.
Csak erre az egy parancsra van szükséged az OpenHands helyi futtatásához.
A playbook további része mindent az Agent Canvas felhasználói felületén keresztül állít be a böngésződben.
<!-- @os:end -->

<!-- @os:windows -->
Windows alatt a publikált Agent Canvas konténerképet Docker Desktoppal futtasd.
A kép tartalmazza az Agent Servert, az automatizálási háttérrendszert és a webes felhasználói felületet, így nem kell Node.js-t, `uv`-t vagy a CLI-t telepítened a gépre.

Először hozd létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Húzd le a publikált képet (kb. 6 GB; nyilvános, így nincs szükség bejelentkezésre):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Majd indítsd el a rendszert (stack):

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Nyisd meg a `http://localhost:8000/canvas` címet a böngésződben.
Ha a 8000-es port már foglalt, rendelj hozzá egy másik host portot, például `-p 8080:8000`, és helyette a `http://localhost:8080/canvas` címet nyisd meg.

> **Megjegyzés:** Az első indítás felépíti az Agent Server környezetet a konténeren belül, így eltarthat néhány percig, mire a háttérrendszer egészségesként jelentkezik.

A `.openhands` csatolás megőrzi az LLM profilodat, az MCP szervereket és az automatizálásokat a konténer újraindításai között.
A playbook további része mindent az Agent Canvas felhasználói felületén keresztül állít be a böngésződben, a `http://localhost:8000/canvas` címen.
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

Az első indításkor az Agent Canvas megnyit egy bevezető folyamatot.
Ebben a folyamatban:

1. Hagyd meg az **OpenHands** beállítást ügynökként, majd kattints a **Next** gombra.
2. A **Set up your LLM** résznél válaszd a **Advanced** lehetőséget.
3. Hagyd az **Authentication** beállítást **API key** értéken.
4. Állítsd a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsd a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe írj be bármilyen nem üres helyőrzőt, például `lemonade-local`. A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van egy értékre a küldéshez.

<!-- @os:windows -->
> **Windows (Docker):** az Agent Server a konténeren belül fut, ezért a **Base URL** mezőt `http://host.docker.internal:13305/api/v1` értékre állítsd a `http://127.0.0.1:13305/api/v1` helyett.
> A konténeren belülről nézve a `127.0.0.1` maga a konténer; a `host.docker.internal` eléri a Windows hoszton futó Lemonade-et, és ezt a hosztnevet a Docker Desktop automatikusan biztosítja.
<!-- @os:end -->

A kapcsolat mezőinek így kell kinézniük.
Az API kulcs mezőt a felhasználói felület elrejti.

![Agent Canvas első használatkor megjelenő LLM Advanced beállításai a Lemonade modellel és a helyi alap URL-lel](assets/01-llm-advanced-settings.png)

Ezután válaszd az **All** lehetőséget, és állítsd be a további helyi modellhez tartozó mezőket:

1. Görgess a **Custom Tokenizer** mezőhöz, és állítsd be erre: `Qwen/Qwen3.6-35B-A3B`.
2. Görgess a **LiteLLM Extra Body** mezőhöz, és állítsd be erre: `{"enable_thinking": true}`.
3. Kattints a **Next** gombra.

![Agent Canvas első használatkor megjelenő LLM All fül a Qwen egyéni tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas első használatkor megjelenő LLM All fül a konfigurált LiteLLM extra body mezővel](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak a következőket kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag jelzi a LiteLLM számára, hogy OpenAI-kompatibilis kérésformázást használjon a Lemonade végponttal szemben.
Az egyéni tokenizáló a GGUF modell eredeti Hugging Face tokenizálója; ez lehetővé teszi, hogy az OpenHands ugyanazokat a csevegősablon-tokeneket számolja, amelyeket a helyi modellkiszolgáló lát.
A jelenlegi első használatkori LLM űrlap nem mutatja a condenser beállításokat.
Ha az Agent Canvas buildje később megjeleníti a condenser beállításokat a **Settings > LLM** alatt, használd a `llm_summarizing` értéket, és állítsd a maximum token mennyiséget a Lemonade kontextusablak alá, például `56000` értékre.

## 5. GitHub és Slack MCP kiszolgálók telepítése

Az Agent Canvas felhasználói felületen nyisd meg a **Customize** (vagy **Settings > MCP**) menüpontot, hogy hozzáadhasd azokat az MCP kiszolgálókat, amelyek eszközöket biztosítanak az ügynök számára a GitHubhoz és a Slackhez.
A token értékek csak a helyi Agent Serverhez kerülnek elküldésre, és titkosított beállításokként kerülnek tárolásra.

<!-- @os:windows -->
> **Windows (Docker):** az alábbi `npx` MCP kiszolgáló parancsok a konténeren belül futnak, amely már tartalmazza a Node.js-t, így a hoszton semmi extrát nem kell telepíteni.
> Mivel a `.openhands` csatolva van, az MCP kiszolgálók és tokenjeik megmaradnak a konténer újraindításai között is.
<!-- @os:end -->

### GitHub MCP kiszolgáló

Adj hozzá egy új MCP kiszolgálót a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = a GitHub tokened |

Használj olyan GitHub tokent, amely olvasási hozzáféréssel rendelkezik ahhoz a repóhoz, amelyet összegezni szeretnél.

### Slack MCP kiszolgáló

Adj hozzá egy második MCP kiszolgálót a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = a digest csatornád azonosítója |

Állítsd a `SLACK_CHANNEL_IDS` értékét a digest csatorna azonosítójára (ugyanarra az értékre, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne kelljen végiglapoznia minden Slack csatornát.

Miután mindkét kiszolgálót hozzáadtad, használd a **Test** gombot mindegyiken, hogy megerősítsd a kapcsolódásukat és az eszközök meghirdetését.
A GitHub kiszolgálónak GitHub eszközöket, a Slack kiszolgálónak pedig Slack eszközöket kell listáznia.

![Agent Canvas MCP oldal telepített GitHub és Slack kiszolgálókkal](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. A Digest automatizálás létrehozása

Az Agent Canvas felhasználói felületen nyisd meg az **Automations** oldalt, és hozz létre egy új automatizálást:

1. Válaszd a **Create automation** lehetőséget, és válaszd a **Prompt preset** típust.
2. Állítsd a **Name** mezőt erre: `GitHub Development Digest to Slack`.
3. Állítsd a **Prompt** mezőt a következő szövegre, a repó és csatorna helyőrzőket a saját értékeidre cserélve:

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

4. Állítsd a **Trigger** mezőt **Cron** típusra, a `0 9 * * 1-5` ütemezéssel (hétköznaponként reggel 9 órakor), és állítsd be a **Timezone** mezőt a saját időzónádra, például `America/New_York` értékre.
5. Állítsd a **Timeout** mezőt `900` másodpercre.
6. Mentsd el az automatizálást.

Az automatizálás részletező oldala megmutatja az új automatizálást a cron triggerrel és a generált prompt-preset belépési ponttal.

![Agent Canvas automatizálás részletező oldala a létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az automatizálás részletező oldaláról az Agent Canvas felhasználói felületen:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra az automatizálás azonnali, egyszeri futtatásához.
2. Figyelje a futtatási listát ugyanazon az oldalon. A legutóbbi futtatásnak `COMPLETED` állapotba kell átváltania.
3. Nyissa meg a célként megadott Slack csatornát. Tartalmaznia kell a generált digestet.

Nem kell megvárnia, amíg a cron ütemezés aktiválódik — a **Run now** igény szerint indít egy futtatást, így még az ütemezésre való hagyatkozás előtt megerősítheti, hogy a prompt, az MCP-kapcsolatok és a Slackre történő közzététel mind megfelelően működnek.

![Sikeresen befejeződött Agent Canvas automatizálási futtatás](assets/06-automation-run-completed.png)

![Slack csatorna, amely a generált OpenHands digestet mutatja](assets/07-slackbot-message.png)

## Hibaelhárítás

<!-- @os:windows -->
- **A Docker 8000-es portja már foglalt:** rendeljen hozzá egy másik gazdagép portot, például `docker run ... -p 8080:8000 ...`, és nyissa meg a `http://localhost:8080/canvas` oldalt.
- **A `docker pull` hitelesítési hibával meghiúsul** (például: „A specified logon session does not exist"): futtassa a pull-t interaktív Windows-munkamenetből, vagy húzza le előre a képet. A képfájl nyilvános, így nincs szükség `docker login` parancsra.
- **A felhasználói felület betöltődik, de a háttérrendszer nem egészséges:** az első indításkor a konténeren belül épül fel az Agent Server környezete. Várjon egy percet, és frissítse az oldalt, majd ellenőrizze a `docker logs <container>` kimenetét a folyamat állapotáról.
- **Az Agent Canvas nem éri el a Lemonade-ot a konténerből:** állítsa be az LLM **Base URL** mezőjét erre: `http://host.docker.internal:13305/api/v1` (ne `127.0.0.1`-re), és győződjön meg róla, hogy a Lemonade fut a Windows gazdagépen.
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

Ha `zsh`-t használ, adja hozzá ugyanazt az `export PATH=...` sort a `~/.bashrc` helyett a `~/.zshrc` fájlhoz.
- **Az Agent Canvas elutasítja az LLM-beállításokat a `custom_tokenizer` megadása után:** telepítse a `transformers` csomagot az Agent Server Python környezetébe, szükség esetén indítsa újra az Agent Canvast, és próbálja meg újra menteni az LLM-beállításokat. Az OpenHandsnek szüksége van a Transformersre a tokenizáló chat sablonjának betöltéséhez, amikor a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-ot:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancsot, és győződjön meg róla, hogy az első használatkor megjelenő LLM-űrlapban vagy a **Settings > LLM** menüben megadott base URL megegyezik a futó helyi végponttal vagy a HTTPS alagúttal.
- **Az LLM-beállítások nem mentődtek:** győződjön meg róla, hogy az értékek megadása után a **Next** gombra kattintott. Nyissa meg újra a **Settings > LLM** menüt, hogy megerősítse az értékek megmaradását.
- **A GitHub MCP nem látja a privát tárolókat:** győződjön meg róla, hogy a GitHub token olvasási hozzáféréssel rendelkezik a célként megadott tárolóhoz, és hogy az MCP **Test** gombja a **Customize** menüben GitHub eszközöket hirdet.
- **A Slack tudja olvasni a csatornákat, de nem tud közzétenni:** hívja meg a Slack alkalmazást a célként megadott csatornába, és győződjön meg róla, hogy a bot rendelkezik `chat:write` jogosultsággal.
- **Az automatizálás túl sok Slack csatornát sorol fel:** használjon Slack csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálás futtatása meghiúsul, vagy túllépi a kontextust:** győződjön meg róla, hogy a Lemonade `ctx_size=65536` beállítással indult, hogy az OpenHands LLM-nél be van állítva a `custom_tokenizer`, és használjon kifejezett tárolót, a GitHub eredményhalmazokat pedig korlátozza 3-5 elemre. Ha az Agent Canvas build kondenzáló (condenser) beállításokat tesz elérhetővé, állítsa a kondenzáló maximális tokenszámát a Lemonade kontextusablaka alá.

## Következő lépések

- Heti, csak kiadásokra vonatkozó digest hozzáadása.
- GitHub eseményindította automatizálás hozzáadása a gyorsabb PR- vagy push-értesítésekhez.
- Ugyanazon digest irányítása Notionba, Linearbe vagy egy másik MCP-alapú eszközbe.

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