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

A fejlesztők sok időt töltenek kis, ismétlődő ciklusokkal: címkézett pull requestek átnézésével, GitHub-kommentekre való válaszadással, új hibajegyek priorizálásával, Slack-szálak standup jegyzetekké vagy incidens-utókövetésekké alakításával, valamint kiadási vagy kutatási jelzések nyomon követésével.
Minden ciklus ismerős, mégis megítélést igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít, és világos frissítést kell közzétenni ott, ahol a csapat már amúgy is dolgozik.

Az [OpenHands automatizálások](https://docs.openhands.dev/openhands/usage/automations/overview) ezeket a ciklusokat ütemezett vagy eseményvezérelt agent-beszélgetésekké alakítják: olyan futtatásokká, amelyek során egy AI szoftveragent kontextust olvashat, eszközöket hívhat, és frissítést állíthat elő.
Az OpenHands bővítménykatalógusában található megosztott automatizálási sablonok ezt a mintát követik GitHub pull request review, repository monitorozás, Linear issue triage, incidens utólagos elemzés, Slack standup összefoglalók és kutatási beszámolók esetén: egy automatizálás felébred, konfigurált integrációkat, például GitHubot vagy Slacket használ a kontextus lekéréséhez, ezen a kontextuson egy nagy nyelvi modellel (LLM) gondolkodik, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) a helyi vezérlőpult ezen automatizálások felépítéséhez és teszteléséhez.
Ebben a útmutatóban egy OpenHands Agent Server-t futtat, amely az agent-beszélgetéseket végrehajtó háttérfolyamat, és összekapcsolja az agentet külső szolgáltatásokkal, például GitHubbal és Slackkel.

Ahhoz, hogy a munkafolyamat az AMD rendszeren maradjon, az agent egy helyileg futó, a Lemonade Server által kiszolgált modellel kommunikál.
A Lemonade OpenAI-kompatibilis API-n keresztül teszi elérhetővé ezt a modellt, így az Agent Canvas úgy konfigurálhatja, mintha egy távoli OpenAI-stílusú végpont lenne, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben a útmutatóban egy konkrét automatizálást fog felépíteni: egy ütemezett GitHub-Slack fejlesztési összefoglalót.
Ez a GitHubot használja a legutóbbi repository-tevékenység vizsgálatára, a Slacket az összefoglaló közzétételére, az Agent Canvas API-hívásokat az automatizálás konfigurálására és tesztelésére, valamint a Lemonade-et az LLM helyi futtatására.

![Architektúra diagram, amely a GitHub MCP-t, az OpenHands automatizálást, a Lemonade Server-t és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Amit meg fog tanulni

- Hogyan indítsa el a Lemonade Server-t, és hogyan ellenőrizze, hogy a helyi modell válaszol-e a chatkérésekre
- Hogyan indítsa el az Agent Canvas-t, és hogyan irányítsa az Agent Server-ét egy helyi LLM-re
- Hogyan telepítsen GitHub és Slack Model Context Protocol (MCP) szervereket az Agent Server API-n keresztül
- Hogyan hozzon létre és indítson el egy ütemezett OpenHands automatizálást, amely fejlesztési összefoglalót tesz közzé a Slacken
- Hogyan hárítsa el a leggyakoribb helyi modellel és automatizálással kapcsolatos hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe a útmutatóba |
| --- | --- | --- |
| Lemonade Server | Az AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az Ön adatai soha nem hagyják el a gépét. | Futtatja azt a modellt, amely az agentet hajtja. |
| OpenHands Agent Server | Az OpenHands agent-beszélgetéseket végrehajtó háttérfolyamat. | Az agentet, annak LLM-profilját és MCP-szervereit tartalmazza. |
| Agent Canvas | Az OpenHands helyi vezérlőpultja, amely futtatja az Agent Server-t és egy felhasználói felületet az agentfuttatások vizsgálatához. | Elindítja a háttérrendszereket, és biztosítja az API-t, amelyet meghív. |
| MCP server | Egy Model Context Protocol szerver, amely eszközöket biztosít egy agent számára egy külső szolgáltatáshoz, például GitHubhoz vagy Slackhez. | Lehetővé teszi az agent számára a GitHub olvasását és a Slackre való írást. |
| OpenHands automatizálás | Egy ütemezett vagy eseményvezérelt agent-beszélgetés, amely kontextust kér le, azon gondolkodik, és valahol eredményt ír. | Az itt felépített GitHub-Slack összefoglaló. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló agent munkafolyamatok nagyobb modellből és kontextusablakból profitálnak.
> Használjon legalább 32 GB rendszermemóriát, és a nagyobb GGUF modellekhez inkább 64 GB-ot vagy többet.
<!-- @device:end -->

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Előfeltételek

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Szüksége lesz a következőkre:

- A Lemonade Server telepítve a szokásos [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb verzió és `npm`, amelyekkel telepítheti a publikált Agent Canvas CLI-t, és `npx` segítségével futtathatja az MCP-szervereket.
- `uv`, az a Python csomagkezelő, amelyet az Agent Canvas az Agent Server környezetének felépítéséhez használ. Ha még nincs telepítve, telepítse az [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján.
- Egy friss, publikált `@openhands/agent-canvas` csomag, amely sémavezérelt agentbeállításokat, `LLMSummarizingCondenserSettings.max_tokens`-t és LLM `custom_tokenizer` támogatást tartalmaz.
- A Python `transformers` csomag elérhető az Agent Server környezetében. Ez szükséges a chat-sablon alapú tokenszámláláshoz, ha a `custom_tokenizer` be van állítva.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), telepítve és futtatva. Windows rendszeren az Agent Canvas verem a publikált Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t, a `transformers`-t és az `@openhands/agent-canvas` csomagot, így ezeket nem kell telepítenie a hoszton.
<!-- @os:end -->

- Egy GitHub token, amely olvasási hozzáféréssel rendelkezik az összefoglalandó repositoryhoz.
- Egy Slack bot token (`xoxb-...`), amely rendelkezik `chat:write` és csatorna-olvasási hozzáféréssel.
- Egy Slack csapatazonosító (`T...`).
- Egy Slack csatornaazonosító (`C...`), ahová az összefoglalót közzé kell tenni.

Hívja meg a Slack alkalmazást a célcsatornába, mielőtt tesztelné az automatizálást.
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

Ezt a két változót a lenti ellenőrző parancsok használják.
A modellt, a tokenizert és az egyéb LLM-beállításokat a későbbi lépésekben közvetlenül az Agent Canvas felhasználói felületén adja meg, ezért ezek konkrét értékei ott, ahol szükség van rájuk, közvetlenül a szövegben szerepelnek.

A következő értékeket a későbbi lépésekben az Agent Canvas felhasználói felületén kell megadni:
Állítsa be itt őket, hogy onnan bemásolhassa:

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

A `GITHUB_REPO_FILTER` esetében használjon explicit `owner/repo` értéket.
A tág szervezeti helyettesítő karakterek túl sok MCP-kontextust adhatnak vissza a helyi modellek számára.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. A Lemonade szerver elindítása

Indítsa el a modellt a Lemonade parancssori felületéről:

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

> **Válasszon a hardveréhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) erős modell ehhez a munkafolyamathoz, de nagy memóriakeretet igényel.
> Ha az eszközén korlátozott a memória vagy a GPU VRAM, válasszon egy kisebb GGUF modellt a Lemonade modellkönyvtárából, és ezt a modellazonosítót (valamint a hozzá tartozó tokenizert) használja végig ebben a playbookban.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha az még nincs meg, ami a modell méretétől és a kapcsolat sebességétől függően eltarthat egy ideig.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé itt:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálást futtató komponens nem ugyanazon a gépen fut, tegye elérhetővé a Lemonade végpontot egy biztonságos alagúton keresztül, és a HTTPS URL-t használja LLM base URL-ként.
Az [ngrok](https://ngrok.com/) egy helyi portot tesz elérhetővé az interneten egy biztonságos HTTPS URL-en keresztül; ehhez ingyenes ngrok fiók szükséges, és a `YOUR_NGROK_DOMAIN.ngrok-free.dev` helyére a saját fenntartott domainjét kell behelyettesítenie:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Győződjön meg róla, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ezután küldjön egy kis chat-kérést:

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

Ezután küldjön egy kis chat-kérést:

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
Telepítse a közzétett Agent Canvas csomagot, és indítsa el a teljes rendszert:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm telepítés jogosultsági hibával meghiúsul, tekintse meg az alábbi npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyissa meg ezt az URL-t a böngészőjében.
A port nem különleges – ha a 8000-es már foglalt, adjon meg egy szabad portot a `--port` (vagy `-p`) kapcsolóval.
Az alapértelmezett helyi háttérrendszernek egészségesként kell megjelennie a kezdőképernyőn.

> **Megjegyzés:** Az első indítás felépíti az Agent Server `uv`-vel kezelt Python-környezetét, így eltarthat néhány percig, mire a háttérrendszer egészségesnek jelentkezik.

Az `agent-canvas` parancs együtt indítja el az agent szervert, az automatizálási háttérrendszert és a webes frontendet.
Csak erre az egyetlen parancsra van szüksége az OpenHands helyi futtatásához.
A playbook további része mindent az Agent Canvas felhasználói felületén keresztül konfigurál a böngészőjében.
<!-- @os:end -->

<!-- @os:windows -->
Windows rendszeren futtassa a közzétett Agent Canvas konténerképet Docker Desktop segítségével.
A kép tartalmazza az Agent Servert, az automatizálási háttérrendszert és a webes frontendet, így nem kell telepítenie a Node.js-t, az `uv`-t vagy a parancssori felületet a gazdagépre.

Először hozza létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltse le a közzétett képet (kb. 6 GB; nyilvános, így bejelentkezés nem szükséges):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Ezután indítsa el a rendszert:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Nyissa meg a `http://localhost:8000/canvas` címet a böngészőjében.
Ha a 8000-es port már foglalt, rendeljen hozzá egy másik gazdaportot, például `-p 8080:8000`, és ehelyett a `http://localhost:8080/canvas` címet nyissa meg.

> **Megjegyzés:** Az első indítás felépíti az Agent Server környezetét a konténeren belül, így eltarthat néhány percig, mire a háttérrendszer egészségesnek jelentkezik.

A `.openhands` csatolás megőrzi az LLM-profilját, az MCP-szervereket és az automatizálásokat a konténer újraindításai között.
A playbook további része mindent az Agent Canvas felhasználói felületén keresztül konfigurál a böngészőjében a `http://localhost:8000/canvas` címen.
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

Első indításkor az Agent Canvas egy bevezető (onboarding) folyamatot indít.
Ebben a folyamatban:

1. Hagyja kiválasztva az **OpenHands** ügynököt, majd kattintson a **Next** gombra.
2. A **Set up your LLM** részen válassza az **Advanced** opciót.
3. Hagyja az **Authentication** beállítást **API key** értéken.
4. Állítsa a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe írjon be egy tetszőleges, nem üres helyőrző értéket, például `lemonade-local`. A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van egy értékre a küldéshez.

<!-- @os:windows -->
> **Windows (Docker):** az Agent Server a konténeren belül fut, ezért a **Base URL** mezőt állítsa `http://host.docker.internal:13305/api/v1` értékre a `http://127.0.0.1:13305/api/v1` helyett.
> A konténeren belülről nézve a `127.0.0.1` maga a konténer; a `host.docker.internal` a Windows hoszton futó Lemonade-ot éri el, és ezt a hosztnevet a Docker Desktop automatikusan biztosítja.
<!-- @os:end -->

A kapcsolódási mezőknek így kell kinézniük.
Az API kulcs mezőt a felhasználói felület elrejti (maszkolja).

![Az Agent Canvas első használatkori LLM Advanced beállításai a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Ezután válassza az **All** lehetőséget, és állítsa be a további, helyi modellhez tartozó mezőket:

1. Görgessen a **Custom Tokenizer** mezőhöz, és állítsa erre: `Qwen/Qwen3.6-35B-A3B`.
2. Görgessen a **LiteLLM Extra Body** mezőhöz, és állítsa erre: `{"enable_thinking": true}`.
3. Kattintson a **Next** gombra.

![Az Agent Canvas első használatkori LLM All lapja a Qwen egyéni tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Az Agent Canvas első használatkori LLM All lapja a beállított LiteLLM extra body értékkel](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak a következőket kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag arra utasítja a LiteLLM-et, hogy OpenAI-kompatibilis kérésformázást használjon a Lemonade végponttal szemben.
Az egyéni tokenizáló a GGUF modellhez tartozó eredeti Hugging Face tokenizáló; ez lehetővé teszi, hogy az OpenHands ugyanazokat a chat-sablon tokeneket számolja, amelyeket a helyi modellkiszolgáló lát.
A jelenlegi első használatkori LLM űrlap nem jeleníti meg a condenser beállításokat.
Ha az Ön Agent Canvas buildje később megjeleníti a condenser beállításokat a **Settings > LLM** alatt, használja az `llm_summarizing` értéket, és a maximális tokenszámot állítsa a Lemonade kontextusablaka alá, például `56000` értékre.

## 5. GitHub és Slack MCP szerverek telepítése

Az Agent Canvas felhasználói felületén nyissa meg a **Customize** (vagy **Settings > MCP**) menüpontot, hogy hozzáadja azokat az MCP szervereket, amelyek a GitHubhoz és a Slackhez biztosítanak eszközöket az ügynök számára.
A token értékek csak a helyi Agent Serverre kerülnek elküldésre, és titkosított beállításokként kerülnek tárolásra.

<!-- @os:windows -->
> **Windows (Docker):** az alábbi `npx` MCP szerverparancsok a konténeren belül futnak, amely már tartalmazza a Node.js-t, így a hoszton semmi extra nem kerül telepítésre.
> Mivel a `.openhands` mappa csatolva van, az MCP szerverek és tokenjeik megmaradnak a konténer újraindításai között.
<!-- @os:end -->

### GitHub MCP szerver

Adjon hozzá egy új MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = az Ön GitHub tokenje |

Használjon olyan GitHub tokent, amely olvasási jogosultsággal rendelkezik az összegzendő repóhoz.

### Slack MCP szerver

Adjon hozzá egy második MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = az Ön digest csatornájának azonosítója |

Állítsa a `SLACK_CHANNEL_IDS` értékét a digest csatorna azonosítójára (ugyanaz az érték, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne kelljen minden Slack csatornát végignéznie.

Miután mindkét szervert hozzáadta, használja a **Test** gombot mindegyiken, hogy megerősítse a kapcsolódásukat és az eszközeik meghirdetését.
A GitHub szervernek GitHub eszközöket kell listáznia, a Slack szervernek pedig Slack eszközöket.

![Az Agent Canvas MCP oldala a telepített GitHub és Slack szerverekkel](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. A digest automatizálás létrehozása

Az Agent Canvas felhasználói felületén nyissa meg az **Automations** oldalt, és hozzon létre egy új automatizálást:

1. Válassza a **Create automation** lehetőséget, majd a **Prompt preset** típust.
2. Állítsa a **Name** mezőt erre: `GitHub Development Digest to Slack`.
3. Állítsa a **Prompt** mezőt a következő szövegre, a repó- és csatorna-helyőrzőket a saját értékeire cserélve:

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

4. Állítsa a **Trigger** mezőt **Cron** értékre, a `0 9 * * 1-5` ütemezéssel (hétköznaponként 9 órakor), és állítsa be a **Timezone** mezőt az Ön időzónájára, például erre: `America/New_York`.
5. Állítsa a **Timeout** értéket `900` másodpercre.
6. Mentse el az automatizálást.

Az automatizálás részletező oldala megjeleníti az új automatizálást a cron triggerével és a generált prompt-preset belépési ponttal.

![Az Agent Canvas automatizálás részletező oldala létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az Agent Canvas UI automatizálás részletek oldaláról:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra az automatizálás azonnali, egyszeri futtatásához.
2. Figyelje a futáslistát ugyanazon az oldalon. A legutóbbi futásnak `COMPLETED` állapotba kell váltania.
3. Nyissa meg a célzott Slack csatornát. Tartalmaznia kell a generált digest üzenetet.

Nem kell megvárnia a cron ütemezés elindulását – a **Run now** azonnali futtatást indít, így igazolhatja, hogy a prompt, az MCP kapcsolatok és a Slack posztolás mind működik, mielőtt az ütemezésre hagyatkozna.

![Az Agent Canvas automatizálás futása sikeresen befejeződött](assets/06-automation-run-completed.png)

![Slack csatorna, amely a generált OpenHands digestet mutatja](assets/07-slackbot-message.png)

## Hibaelhárítás

<!-- @os:windows -->
- **A Docker 8000-es portja már foglalt:** rendeljen hozzá másik host portot, például `docker run ... -p 8080:8000 ...`, majd nyissa meg a `http://localhost:8080/canvas` címet.
- **A `docker pull` hitelesítési hibával leáll** (például: „A specified logon session does not exist”): futtassa a pull-t interaktív Windows munkamenetből, vagy húzza le előre a lemezképet. A lemezkép nyilvános, így nincs szükség `docker login` bejelentkezésre.
- **Az UI betöltődik, de a backend nem egészséges:** az első indításkor a konténer belsejében épül fel az Agent Server környezete. Várjon egy percet, frissítse az oldalt, majd ellenőrizze a `docker logs <container>` kimenetét a folyamat állapotáért.
- **Az Agent Canvas nem éri el a Lemonade-et a konténerből:** állítsa be az LLM **Base URL** mezőjét a `http://host.docker.internal:13305/api/v1` értékre (ne a `127.0.0.1`-et használja), és győződjön meg róla, hogy a Lemonade fut a Windows host gépen.
<!-- @os:end -->

- **A Lemonade nem fut:** indítsa újra az 1. lépésben szereplő `lemonade run "${LEMONADE_MODEL}"` paranccsal, majd futtassa újra az állapotellenőrzést.
- **Az `npm install -g` jogosultsági hibával leáll:** Linuxon vagy WSL-ben állítson be egy felhasználói tulajdonú globális npm könyvtárat, adja hozzá a shell indítófájljához, majd telepítse újra az Agent Canvast:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ha `zsh`-t használ, ugyanezt az `export PATH=...` sort a `~/.bashrc` helyett a `~/.zshrc` fájlhoz adja hozzá.
- **Az Agent Canvas elutasítja az LLM beállításokat a `custom_tokenizer` megadása után:** telepítse a `transformers` csomagot az Agent Server Python környezetében, szükség esetén indítsa újra az Agent Canvast, majd próbálja meg újra menteni az LLM beállításokat. Az OpenHandsnek szüksége van a Transformers csomagra a tokenizer chat sablon betöltéséhez, ha a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-et:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancs kimenetét, és győződjön meg róla, hogy az első használatkor megjelenő LLM űrlapon vagy a **Settings > LLM** menüben megadott alap URL egyezik a futó helyi végponttal vagy a HTTPS alagúttal.
- **Az LLM beállítások nem mentődtek el:** győződjön meg róla, hogy az értékek megadása után rákattintott a **Next** gombra. Nyissa meg újra a **Settings > LLM** menüt, hogy ellenőrizze, megmaradtak-e az értékek.
- **A GitHub MCP nem látja a privát tárolókat:** ellenőrizze, hogy a GitHub token rendelkezik-e olvasási jogosultsággal a célzott tárolóhoz, és hogy az MCP **Test** gombja a **Customize** menüben megjeleníti-e a GitHub eszközöket.
- **A Slack képes olvasni a csatornákat, de nem tud posztolni:** hívja meg a Slack alkalmazást a célzott csatornába, és győződjön meg róla, hogy a bot rendelkezik `chat:write` jogosultsággal.
- **Az automatizálás túl sok Slack csatornát sorol fel:** használjon Slack csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálás futása sikertelen, vagy túllépi a kontextust:** győződjön meg róla, hogy a Lemonade `ctx_size=65536` beállítással indult, hogy az OpenHands LLM-nél be van állítva a `custom_tokenizer`, és használjon explicit tárolót, a GitHub eredményhalmazokat pedig korlátozza 3–5 elemre. Ha az Agent Canvas verziója tartalmaz condenser beállításokat, állítsa a condenser maximális tokenszámát a Lemonade kontextusablaka alá.

## Következő lépések

- Adjon hozzá egy heti, csak kiadásokra vonatkozó digestet.
- Adjon hozzá egy GitHub eseményindítású automatizálást a gyorsabb PR vagy push riasztásokért.
- Irányítsa ugyanazt a digestet Notionba, Linearbe, vagy más MCP-alapú eszközbe.

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