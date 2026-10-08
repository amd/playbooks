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

A fejlesztők sok időt töltenek kisebb, ismétlődő feladatkörökkel: címkézett pull request-ek átnézésével, GitHub-megjegyzésekre való válaszolással, új issue-k triázsolásával, Slack-szálak standup-jegyzetekké vagy incidensnyomon-követéssé alakításával, valamint a kiadási vagy kutatási jelzések nyomon követésével.
Minden egyes feladatkör ismerős, mégis döntéshozatalt igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít fontosnak, és egy világos frissítést kell közzétenni ott, ahol a csapat már dolgozik.

Az [OpenHands automatizálások](https://docs.openhands.dev/openhands/usage/automations/overview) ezeket a feladatköröket ütemezett vagy eseményvezérelt ágens-beszélgetésekké alakítják: olyan futtatásokká, amelyek során egy mesterséges intelligenciát használó szoftverügynök (AI software agent) kontextust olvashat, eszközöket hívhat meg, és frissítést állíthat elő.
Az OpenHands bővítménykatalógusában található megosztott automatizálási sablonok ezt a mintát követik GitHub pull request áttekintéshez, tárolók (repository) megfigyeléséhez, Linear issue triázsoláshoz, incidens-utólagos elemzésekhez (retrospective), Slack standup-összefoglalókhoz és kutatási jelentésekhez: egy automatizálás elindul, konfigurált integrációkat – például GitHub-ot vagy Slack-et – használ a kontextus lekéréséhez, egy nagy nyelvi modellel (LLM) következtetéseket von le ebből a kontextusból, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) a helyi vezérlő sík (control plane) ezeknek az automatizálásoknak a felépítéséhez és teszteléséhez.
Ebben a gyakorlati útmutatóban egy OpenHands Agent Servert futtat – ez az a háttérfolyamat, amely végrehajtja az ágens-beszélgetéseket –, és összeköti az ágenst külső szolgáltatásokkal, például a GitHub-bal és a Slack-kel.

Annak érdekében, hogy a munkafolyamat az AMD rendszerén maradjon, az ágens egy, a Lemonade Server által kiszolgált helyi modellel kommunikál.
A Lemonade ezt a modellt egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé, így az Agent Canvas úgy tudja konfigurálni, mintha egy távoli, OpenAI-stílusú végpont lenne, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben a gyakorlati útmutatóban egy konkrét automatizálást fogsz felépíteni: egy ütemezett GitHub-ból Slack-be küldött fejlesztési összefoglalót (digest).
Ez a GitHub-ot használja a tároló legutóbbi tevékenységének vizsgálatához, a Slack-et az összefoglaló közzétételéhez, az Agent Canvas API-hívásait az automatizálás konfigurálásához és teszteléséhez, valamint a Lemonade-ot az LLM helyi futtatásához.

![Architektúra ábra, amely a GitHub MCP-t, az OpenHands automatizálást, a Lemonade Server-t és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Amit meg fogsz tanulni

- Hogyan indítsd el a Lemonade Server-t, és ellenőrizd, hogy egy helyi modell válaszol-e a chat-kérésekre
- Hogyan indítsd el az Agent Canvas-t, és hogyan irányítsd az Agent Server-ét egy helyi LLM-re
- Hogyan telepíts GitHub és Slack Model Context Protocol (MCP) szervereket az Agent Server API-n keresztül
- Hogyan hozz létre és indíts el egy ütemezett OpenHands automatizálást, amely egy fejlesztési összefoglalót (digest) tesz közzé a Slack-en
- Hogyan hárítsd el a leggyakoribb helyi modellel és automatizálással kapcsolatos hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe a gyakorlati útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített, helyi LLM-kiszolgáló platform, amely egy OpenAI-kompatibilis API-t tesz elérhetővé. Az adataid soha nem hagyják el a gépedet. | Futtatja a modellt, amely az ágenst működteti. |
| OpenHands Agent Server | A háttérfolyamat, amely végrehajtja az OpenHands ágens-beszélgetéseket. | Ez hostolja az ágenst, annak LLM-profilját és MCP szervereit. |
| Agent Canvas | Az OpenHands helyi vezérlő síkja (control plane), amely futtatja az Agent Server-t és egy felhasználói felületet az ágens-futtatások megtekintéséhez. | Elindítja a háttérrendszereket, és biztosítja az API-t, amelyet meghívsz. |
| MCP szerver | Egy Model Context Protocol szerver, amely eszközöket ad egy ágensnek egy külső szolgáltatáshoz, például GitHub-hoz vagy Slack-hez. | Lehetővé teszi az ágens számára, hogy olvasson a GitHub-ból, és írjon a Slack-be. |
| OpenHands automatizálás | Egy ütemezett vagy eseményvezérelt ágens-beszélgetés, amely kontextust kér le, következtet rá, és valahol eredményt ír ki. | A GitHub-ból Slack-be küldött összefoglaló, amelyet itt felépítesz. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Az ágens-kódolási (coding-agent) munkafolyamatok nagyobb modellből és kontextusablakból profitálnak.
> Használj legalább 32 GB rendszermemóriát, nagyobb GGUF modellekhez pedig lehetőleg 64 GB-ot vagy többet.
<!-- @device:end -->

## A memória-konfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Szükséged lesz a következőkre:

- Telepített Lemonade Server, a szokásos [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb, valamint `npm`, amely a kiadott Agent Canvas CLI telepítéséhez és az MCP szerverek `npx`-szel történő futtatásához szükséges.
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az Agent Server környezetének felépítéséhez használ. Ha még nincs telepítve, telepítsd az [uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/).
- Egy friss, kiadott `@openhands/agent-canvas` csomag séma-vezérelt ágens-beállításokkal, `LLMSummarizingCondenserSettings.max_tokens` támogatással és LLM `custom_tokenizer` támogatással.
- A Python `transformers` csomag elérhető az Agent Server környezetében. Ez szükséges a chat-sablon alapú token-számláláshoz, ha a `custom_tokenizer` be van állítva.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), telepítve és futtatva. Windows rendszeren az Agent Canvas-verem a kiadott Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t, a `transformers`-t és a `@openhands/agent-canvas` csomagot, így ezeket nem kell a hoszton telepítened.
<!-- @os:end -->

- Egy GitHub token, amely olvasási hozzáféréssel rendelkezik az összegzendő tárolóhoz.
- Egy Slack bot token (`xoxb-...`), amely rendelkezik `chat:write` és csatorna-olvasási hozzáféréssel.
- Egy Slack csapat-azonosító (team ID) (`T...`).
- Egy Slack csatorna-azonosító (channel ID) (`C...`), ahol az összefoglalót közzé kell tenni.

Hívd meg a Slack alkalmazást a célcsatornába, mielőtt tesztelnéd az automatizálást.
## A playbookhoz használt változók

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

Ezt a két változót a lenti ellenőrző parancsok használják.
A modell, a tokenizáló és az egyéb LLM-beállítások közvetlenül az Agent Canvas felhasználói felületén kerülnek megadásra a későbbi lépésekben, így a konkrét értékeiket ott, soron belül tüntetjük fel, ahol szükséges.

A következő értékeket a későbbi lépésekben kell megadni az Agent Canvas felhasználói felületén:
Állítsd be itt, hogy később be tudd másolni őket:

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
A túl tág szervezeti helyettesítő karakterek (wildcard) túl sok MCP kontextust adhatnak vissza a helyi modellek számára.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. A Lemonade Server indítása

Indítsd el a modellt a Lemonade CLI-ből:

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

> **Válassz olyan modellt, amely illeszkedik a hardveredhez.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős modell ehhez a munkafolyamathoz, de nagy memóriakeretet igényel.
> Ha az eszközödön korlátozott a memória vagy a GPU VRAM mennyisége, válassz egy kisebb GGUF modellt a Lemonade modellkönyvtárából, és használd azt a modellazonosítót (valamint a hozzá tartozó tokenizálót) a playbook teljes egészében.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs jelen, ami a modell méretétől és a kapcsolat sebességétől függően hosszabb ideig is eltarthat.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé a következő címen:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálási futtató nem ugyanazon a gépen fut, tedd elérhetővé a Lemonade végpontot egy biztonságos alagúton (tunnel) keresztül, és a HTTPS URL-t add meg LLM alap URL-ként.
Az [ngrok](https://ngrok.com/) egy helyi portot tesz elérhetővé az interneten egy biztonságos HTTPS URL-en keresztül; ehhez egy ingyenes ngrok fiók szükséges, és a `YOUR_NGROK_DOMAIN.ngrok-free.dev` helyére a saját lefoglalt domainedet kell behelyettesítened:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Győződj meg róla, hogy a Lemonade képes kiszolgálni a kiválasztott modellt:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ezután küldj egy kis chat-kérést:

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

Ezután küldj egy kis chat-kérést:

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

## 3. Az Agent Canvas indítása

<!-- @os:linux -->
Telepítsd a publikált Agent Canvas csomagot, és indítsd el a teljes stacket:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm telepítés jogosultsági hibával hiúsul meg, lásd a lenti npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyisd meg ezt az URL-t a böngésződben.
A port nem egyedi jelentőségű – ha a 8000-es port már foglalt, bármilyen szabad portot megadhatsz a `--port` (vagy `-p`) kapcsolóval.
Az alapértelmezett helyi backendnek egészségesként (healthy) kell megjelennie a kezdőképernyőn.

> **Megjegyzés:** Az első indításkor felépül az Agent Server `uv`-vel kezelt Python környezete, ezért eltarthat néhány percig, mire a backend egészségesnek jelzi magát.

Az `agent-canvas` parancs elindítja az agent servert, az automatizálási backendet és a webes frontendet együtt.
Csak erre az egyetlen parancsra van szükséged az OpenHands helyi futtatásához.
A playbook további része a böngésződben megjelenő Agent Canvas felhasználói felületén keresztül konfigurál mindent.
<!-- @os:end -->

<!-- @os:windows -->
Windows rendszeren futtasd a publikált Agent Canvas konténerképet Docker Desktoppal.
A kép tartalmazza az Agent Servert, az automatizálási backendet és a webes frontendet, így nem kell Node.js-t, `uv`-t vagy a CLI-t telepítened a hoszt gépre.

Először hozd létre a konfigurációs és workspace mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltsd le a publikált image-et (kb. 6 GB; nyilvános, így bejelentkezés nem szükséges):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Ezután indítsd el a stacket:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Nyisd meg a `http://localhost:8000/canvas` címet a böngésződben.
Ha a 8000-es port már foglalt, rendelj hozzá egy másik hoszt portot, például `-p 8080:8000`, és helyette a `http://localhost:8080/canvas` címet nyisd meg.

> **Megjegyzés:** Az első indításkor felépül az Agent Server környezete a konténeren belül, ezért eltarthat néhány percig, mire a backend egészségesnek jelzi magát.

A `.openhands` csatolás megőrzi az LLM profilodat, az MCP szervereket és az automatizálásokat a konténer újraindításai között is.
A playbook további része a böngésződben, a `http://localhost:8000/canvas` címen elérhető Agent Canvas felhasználói felületén keresztül konfigurál mindent.
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
## 4. Helyi LLM konfigurálása a felhasználói felületen

Első indításkor az Agent Canvas egy bevezető (onboarding) folyamatot indít.
Ebben a folyamatban:

1. Hagyd kiválasztva az **OpenHands** ügynököt, és kattints a **Next** gombra.
2. A **Set up your LLM** résznél válaszd az **Advanced** lehetőséget.
3. Hagyd az **Authentication** beállítást **API key** értéken.
4. Állítsd a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsd a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe írj be bármilyen nem üres helyőrzőt, például `lemonade-local`. A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van egy értékre, amit elküldhet.

<!-- @os:windows -->
> **Windows (Docker):** az Agent Server a konténeren belül fut, ezért a **Base URL** mezőt állítsd `http://host.docker.internal:13305/api/v1` értékre a `http://127.0.0.1:13305/api/v1` helyett.
> A konténeren belülről nézve a `127.0.0.1` maga a konténer; a `host.docker.internal` a Windows hoszton futó Lemonade-et éri el, és a Docker Desktop automatikusan biztosítja ezt a hosztnevet.
<!-- @os:end -->

A kapcsolat mezőinek így kell kinézniük.
Az API key mezőt a felhasználói felület elrejti (maszkolja).

![Agent Canvas első használatkori LLM Advanced beállítások a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Ezután válaszd ki az **All** fület, és állítsd be a további helyi modell mezőket:

1. Görgess a **Custom Tokenizer** mezőhöz, és állítsd be erre: `Qwen/Qwen3.6-35B-A3B`.
2. Görgess a **LiteLLM Extra Body** mezőhöz, és állítsd be erre: `{"enable_thinking": true}`.
3. Kattints a **Next** gombra.

![Agent Canvas első használatkori LLM All fül a Qwen egyéni tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas első használatkori LLM All fül a beállított LiteLLM extra body mezővel](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak a következőket kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag utasítja a LiteLLM-et, hogy OpenAI-kompatibilis kérésformázást használjon a Lemonade végponttal szemben.
Az egyéni tokenizáló a GGUF modell eredeti Hugging Face tokenizálója; ez lehetővé teszi, hogy az OpenHands ugyanazokat a chat-sablon tokeneket számolja, amelyeket a helyi modellkiszolgáló lát.
A jelenlegi első használatkori LLM űrlap nem jeleníti meg a condenser beállításokat.
Ha az Agent Canvas buildje később megjeleníti a condenser beállításokat a **Settings > LLM** alatt, használd a `llm_summarizing` értéket, és állítsd a max tokens értéket a Lemonade kontextusablak alá, például `56000` értékre.

## 5. GitHub és Slack MCP szerverek telepítése

Az Agent Canvas felhasználói felületén nyisd meg a **Customize** (vagy **Settings > MCP**) menüt, hogy hozzáadd azokat az MCP szervereket, amelyek eszközöket biztosítanak az ügynöknek a GitHubhoz és a Slackhez.
A tokenértékek csak a helyi Agent Serverhez kerülnek elküldésre, és titkosított beállításokként kerülnek mentésre.

<!-- @os:windows -->
> **Windows (Docker):** az alábbi `npx` MCP szerverparancsok a konténeren belül futnak, amely már tartalmazza a Node.js-t, így a hoszton semmit sem kell külön telepíteni.
> Mivel a `.openhands` csatolva van, az MCP szerverek és tokenjeik a konténer újraindítása után is megmaradnak.
<!-- @os:end -->

### GitHub MCP szerver

Adj hozzá egy új MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = a te GitHub tokened |

Használj egy olyan GitHub tokent, amely olvasási hozzáféréssel rendelkezik ahhoz a repositoryhoz, amelyet össze szeretnél foglaltatni.

### Slack MCP szerver

Adj hozzá egy második MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = a digest csatornád azonosítója |

Állítsd a `SLACK_CHANNEL_IDS` értéket a digest csatorna azonosítójára (ugyanarra az értékre, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne kelljen végiglapoznia az összes Slack csatornát.

Miután mindkét szervert hozzáadtad, használd a **Test** gombot mindegyiknél, hogy megerősítsd a kapcsolódásukat és az eszközeik meghirdetését.
A GitHub szervernek GitHub eszközöket kell listáznia, a Slack szervernek pedig Slack eszközöket.

![Agent Canvas MCP oldal a telepített GitHub és Slack szerverekkel](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. A Digest automatizálás létrehozása

Az Agent Canvas felhasználói felületén nyisd meg az **Automations** oldalt, és hozz létre egy új automatizálást:

1. Válaszd a **Create automation** lehetőséget, majd a **Prompt preset** típust.
2. Állítsd be a **Name** mezőt erre: `GitHub Development Digest to Slack`.
3. Állítsd be a **Prompt** mezőt a következő szövegre, a repository és csatorna helyőrzőket a saját értékeidre cserélve:

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

4. Állítsd be a **Trigger** mezőt **Cron** típusra, az ütemezést `0 9 * * 1-5` értékre (hétköznaponként 9 órakor), és a **Timezone** mezőt a saját időzónádra, például `America/New_York` értékre.
5. Állítsd a **Timeout** mezőt `900` másodpercre.
6. Mentsd el az automatizálást.

Az automatizálás részletező oldala megjeleníti az új automatizálást a cron triggerrel és a generált prompt-preset belépési ponttal.

![Agent Canvas automatizálás részletei a létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az Agent Canvas UI automatizálás részletező oldaláról:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra, hogy az automatizálást azonnal, egyszer lefuttassa.
2. Figyelje meg a futtatási listát ugyanazon az oldalon. A legutóbbi futtatásnak `COMPLETED` állapotba kell kerülnie.
3. Nyissa meg a céloz Slack csatornát. Tartalmaznia kell a generált összefoglalót.

Nem kell megvárnia, hogy a cron ütemezés aktiválódjon — a **Run now** igény szerinti futtatást indít, így megerősítheti, hogy a prompt, az MCP-kapcsolatok és a Slack-posztolás mind működnek, mielőtt az ütemezésre hagyatkozna.

![Sikeresen befejeződött Agent Canvas automatizálási futtatás](assets/06-automation-run-completed.png)

![Slack csatorna, amely a generált OpenHands összefoglalót mutatja](assets/07-slackbot-message.png)

## Hibaelhárítás

<!-- @os:windows -->
- **A 8000-es Docker port már foglalt:** rendeljen hozzá egy másik gazdagép portot, például `docker run ... -p 8080:8000 ...`, és nyissa meg a `http://localhost:8080/canvas` címet.
- **A `docker pull` hitelesítési hibával meghiúsul** (például: "A specified logon session does not exist"): futtassa a pull-t interaktív Windows munkamenetből, vagy húzza le előre a képet (pre-pull). A kép publikus, így nincs szükség `docker login` parancsra.
- **Az UI betöltődik, de a háttérrendszer nem egészséges:** az első indításkor a konténeren belül épül fel az Agent Server környezet. Várjon egy percet, és frissítse az oldalt, majd ellenőrizze a `docker logs <container>` kimenetét a folyamat állapotáról.
- **Az Agent Canvas nem éri el a Lemonade-ot a konténerből:** állítsa be az LLM **Base URL** mezőjét a `http://host.docker.internal:13305/api/v1` értékre (ne `127.0.0.1`-re), és győződjön meg róla, hogy a Lemonade fut a Windows gazdagépen.
<!-- @os:end -->

- **A Lemonade leállt:** indítsa újra a `lemonade run "${LEMONADE_MODEL}"` paranccsal az 1. lépésben, majd futtassa újra az állapotellenőrzést.
- **Az `npm install -g` jogosultsági hibával meghiúsul:** Linuxon vagy WSL-en állítson be egy felhasználói tulajdonú globális npm könyvtárat, adja hozzá a shell indítófájljához, majd telepítse újra az Agent Canvas-t:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ha `zsh`-t használ, adja hozzá ugyanazt az `export PATH=...` sort a `~/.zshrc` fájlhoz a `~/.bashrc` helyett.
- **Az Agent Canvas elutasítja az LLM-beállításokat a `custom_tokenizer` beállítása után:** telepítse a `transformers` csomagot az Agent Server Python környezetébe, szükség esetén indítsa újra az Agent Canvas-t, majd próbálja meg ismét menteni az LLM-beállításokat. Az OpenHands-nek szüksége van a Transformers csomagra, hogy betöltse a tokenizáló csevegősablonját, amikor a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-ot:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancsot, és győződjön meg róla, hogy az első használatkor megjelenő LLM-űrlapon vagy a **Settings > LLM** menüben megadott alap URL megegyezik a futó helyi végponttal vagy a HTTPS-alagúttal.
- **Az LLM-beállítások nem mentődtek el:** győződjön meg róla, hogy az értékek megadása után a **Next** gombra kattintott. Nyissa meg újra a **Settings > LLM** menüt, hogy ellenőrizze, az értékek megmaradtak-e.
- **A GitHub MCP nem látja a privát tárolókat:** győződjön meg róla, hogy a GitHub-token olvasási jogosultsággal rendelkezik a céltárolóhoz, és hogy az MCP **Test** gombja a **Customize** menüben GitHub-eszközöket hirdet.
- **A Slack tudja olvasni a csatornákat, de nem tud posztolni:** hívja meg a Slack-alkalmazást a céloz csatornára, és győződjön meg róla, hogy a bot rendelkezik `chat:write` jogosultsággal.
- **Az automatizálás túl sok Slack-csatornát listáz:** használjon Slack-csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálás futtatása meghiúsul vagy túllépi a kontextust:** győződjön meg róla, hogy a Lemonade `ctx_size=65536` paraméterrel indult, hogy az OpenHands LLM-nél be van állítva a `custom_tokenizer`, és használjon kifejezett tárolót, a GitHub eredményhalmazokat pedig korlátozza 3-5 elemre. Ha az Agent Canvas build-je tartalmaz kondenzáló (condenser) beállításokat, állítsa a kondenzáló maximális tokenszámát a Lemonade kontextusablaka alá.

## Következő lépések

- Adjon hozzá egy heti, csak kiadásokra vonatkozó összefoglalót.
- Adjon hozzá egy GitHub-eseményen alapuló automatizálást a gyorsabb PR- vagy push-riasztásokhoz.
- Irányítsa ugyanazt az összefoglalót a Notionba, a Linearbe, vagy egy másik MCP-alapú eszközbe.

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