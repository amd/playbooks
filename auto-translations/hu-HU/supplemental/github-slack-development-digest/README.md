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

A fejlesztők rengeteg időt töltenek apró, ismétlődő ciklusokkal: címkézett pull requestek átnézésével, GitHub-kommentekre válaszolással, új issue-k triázsolásával, Slack-szálak standup jegyzetekké vagy incidens-utókövetéssé alakításával, valamint kiadási vagy kutatási jelzések nyomon követésével.
Minden ciklus ismerős, mégis megítélést igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít, és világos frissítést kell közzétenni ott, ahol a csapat már dolgozik.

Az [OpenHands automatizálások](https://docs.openhands.dev/openhands/usage/automations/overview) ezeket a ciklusokat ütemezett vagy eseményalapú ágens-beszélgetésekké alakítják: olyan futtatásokká, amelyekben egy AI szoftverágens kontextust olvashat, eszközöket hívhat meg, és frissítést állíthat elő.
Az OpenHands bővítménykatalógusban található megosztott automatizálási sablonok ezt a mintát követik GitHub pull request áttekintés, repository monitorozás, Linear issue triázs, incidens utóelemzés, Slack standup összefoglalók és kutatási beszámolók esetén: egy automatizálás felébred, konfigurált integrációkat, például GitHub-ot vagy Slack-et használ a kontextus lekéréséhez, egy nagy nyelvi modellel (LLM) végiggondolja azt a kontextust, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az a helyi vezérlőréteg, amellyel ezeket az automatizálásokat felépítheted és tesztelheted.
Ebben az útmutatóban egy OpenHands Agent Server-t futtat, azt a háttérfolyamatot, amely az ágens-beszélgetéseket végrehajtja, és összeköti az ágenst külső szolgáltatásokkal, például GitHub-bal és Slack-kel.

Ahhoz, hogy a munkafolyamat a te AMD rendszereden maradjon, az ágens egy, a Lemonade Server által kiszolgált helyi modellel kommunikál.
A Lemonade ezt a modellt egy OpenAI-kompatibilis API-n keresztül teszi elérhetővé, így az Agent Canvas úgy tudja konfigurálni, mint egy távoli, OpenAI-stílusú végpontot, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben az útmutatóban egy konkrét automatizálást fogsz felépíteni: egy ütemezett GitHub-ról Slack-be küldött fejlesztési összefoglalót.
Ez a GitHub-ot használja a legutóbbi repository-tevékenység megvizsgálására, a Slack-et az összefoglaló közzétételére, az Agent Canvas API-hívásokat az automatizálás konfigurálására és tesztelésére, valamint a Lemonade-et az LLM helyi futtatására.

![Architektúradiagram, amely a GitHub MCP-t, az OpenHands automatizálást, a Lemonade Server-t és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Amit tanulni fogsz

- Hogyan indítsd el a Lemonade Server-t, és ellenőrizd, hogy egy helyi modell válaszol-e a chat-kérésekre
- Hogyan indítsd el az Agent Canvas-t, és irányítsd az Agent Server-ét egy helyi LLM-re
- Hogyan telepíts GitHub és Slack Model Context Protocol (MCP) szervereket az Agent Server API-n keresztül
- Hogyan hozz létre és indíts el egy ütemezett OpenHands automatizálást, amely egy fejlesztési összefoglalót tesz közzé a Slack-en
- Hogyan hárítsd el a leggyakoribb helyi modell- és automatizálási hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe az útmutatóba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | Futtatja a modellt, amely az ágenst hajtja. |
| OpenHands Agent Server | A háttérfolyamat, amely az OpenHands ágens-beszélgetéseket végrehajtja. | Az ágenst, annak LLM-profilját és MCP szervereit tárolja. |
| Agent Canvas | Az OpenHands helyi vezérlőrétege, amely futtatja az Agent Server-t, valamint egy felhasználói felületet az ágensfuttatások megvizsgálásához. | Elindítja a háttérszolgáltatásokat, és biztosítja a meghívandó API-t. |
| MCP szerver | Egy Model Context Protocol szerver, amely eszközöket biztosít az ágensnek egy külső szolgáltatáshoz, például GitHub-hoz vagy Slack-hez. | Lehetővé teszi az ágens számára, hogy olvasson a GitHub-ból és írjon a Slack-be. |
| OpenHands automatizálás | Egy ütemezett vagy eseményalapú ágens-beszélgetés, amely kontextust kér le, végiggondolja azt, és valahová eredményt ír. | Az itt felépített GitHub-ról Slack-be küldött összefoglaló. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> A kódoló ágens munkafolyamatok egy nagyobb modellből és kontextusablakból profitálnak.
> Használj legalább 32 GB rendszermemóriát, és a nagyobb GGUF modellekhez érdemesebb 64 GB-ot vagy annál is többet választani.
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

Szükséged lesz a következőkre:

- A Lemonade Server telepítve legyen a szokásos [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján.

<!-- @os:linux -->
- Node.js 22.12 vagy újabb verzió, valamint `npm`, amelyet a közzétett Agent Canvas CLI telepítéséhez és az MCP szerverek `npx`-szel történő futtatásához használunk.
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az Agent Server környezetének felépítéséhez használ. Ha még nincs telepítve, telepítsd az [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján.
- Egy friss, közzétett `@openhands/agent-canvas` csomag, amely séma alapú ágensbeállításokat, `LLMSummarizingCondenserSettings.max_tokens`-t és LLM `custom_tokenizer` támogatást tartalmaz.
- A Python `transformers` csomag legyen elérhető az Agent Server környezetében. Ez szükséges a chat-sablon alapú tokenszámláláshoz, amikor a `custom_tokenizer` be van állítva.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), telepítve és futtatva. Windows rendszeren az Agent Canvas verem a közzétett Docker image-ből fut, amely tartalmazza a Node.js-t, az `uv`-t, a `transformers`-t és az `@openhands/agent-canvas` csomagot, így ezeket nem kell külön telepítened a gazdagépen.
<!-- @os:end -->

- Egy GitHub token, amely olvasási hozzáféréssel rendelkezik ahhoz a repository-hoz, amelyet össze szeretnél foglaltatni.
- Egy Slack bot token (`xoxb-...`), `chat:write` és csatorna-olvasási hozzáféréssel.
- Egy Slack csapatazonosító (`T...`).
- Egy Slack csatornaazonosító (`C...`), ahová az összefoglalót közzé kell tenni.

Hívd meg a Slack alkalmazást a célcsatornába, mielőtt tesztelnéd az automatizálást.
## A visszajátszásban használt változók

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
A modell, a tokenizáló és az egyéb LLM-beállítások a későbbi lépésekben közvetlenül az Agent Canvas felhasználói felületén kerülnek megadásra, ezért ezeknek a konkrét értékei ott, ahol szükséges, közvetlenül a szövegben szerepelnek.

A következő értékeket a későbbi lépésekben az Agent Canvas felhasználói felületén kell megadni:
Állítsd be itt ezeket, hogy később be tudd másolni:

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

Használj explicit `owner/repo` értéket a `GITHUB_REPO_FILTER` számára.
A túl tág szervezeti helyettesítő karakterek túl sok MCP kontextust adhatnak vissza a helyi modellek számára.

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

> **Válassz a hardveredhez illő modellt.** A `Qwen3.6-35B-A3B-GGUF` (~20 GB) egy erős modell ehhez a munkafolyamathoz, de nagy memóriakészletet igényel.
> Ha az eszközöd memóriája vagy GPU VRAM-ja korlátozott, válassz egy kisebb GGUF modellt a Lemonade modellkönyvtárból, és használd azt a modellazonosítót (és a hozzá tartozó tokenizálót) ebben a visszajátszásban végig.

> **Megjegyzés:** Az első `lemonade run` letölti a modellt, ha még nincs jelen, ami a modell méretétől és az internetkapcsolattól függően eltarthat egy ideig.

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé itt:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálási futtató nem ugyanazon a gépen fut, tedd elérhetővé a Lemonade végpontot egy biztonságos alagúton keresztül, és használd a HTTPS URL-t az LLM alap URL-jeként.
Az [ngrok](https://ngrok.com/) egy helyi portot tesz elérhetővé az interneten egy biztonságos HTTPS URL-en keresztül; ehhez egy ingyenes ngrok fiók szükséges, és a `YOUR_NGROK_DOMAIN.ngrok-free.dev` helyére a saját fenntartott domainedet kell írnod:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Erősítsd meg, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

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

## 3. Az Agent Canvas indítása

<!-- @os:linux -->
Telepítsd a publikált Agent Canvas csomagot, és indítsd el a teljes rendszert:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm telepítés jogosultsági hibával meghiúsul, nézd meg az alábbi npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyisd meg ezt az URL-t a böngésződben.
A portnak nincs különösebb jelentősége—ha a 8000-es port már foglalt, adj meg egy szabad portot a `--port` (vagy `-p`) kapcsolóval.
Az alapértelmezett helyi háttérrendszernek egészségesként kell megjelennie a kezdőképernyőn.

> **Megjegyzés:** Az első indításkor felépül az Agent Server `uv`-vel kezelt Python környezete, így eltarthat néhány percig, amíg a háttérrendszer egészségesnek jelenti magát.

Az `agent-canvas` parancs egyszerre indítja el az ágensszervert, az automatizálási háttérrendszert és a webes felhasználói felületet.
Csak erre az egyetlen parancsra van szükséged az OpenHands helyi futtatásához.
Ennek a visszajátszásnak a hátralévő része mindent az Agent Canvas felhasználói felületén keresztül konfigurál a böngésződben.
<!-- @os:end -->

<!-- @os:windows -->
Windows rendszeren futtasd a publikált Agent Canvas konténerképét a Docker Desktop segítségével.
A kép tartalmazza az Agent Servert, az automatizálási háttérrendszert és a webes felhasználói felületet, így nem kell a hoszton Node.js-t, `uv`-t vagy a CLI-t telepítened.

Először hozd létre a konfigurációs és munkaterület mappákat, amelyeket a konténer csatol:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Töltsd le a publikált képet (kb. 6 GB; nyilvános, így bejelentkezés nem szükséges):

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
Ha a 8000-es port már foglalt, rendelj hozzá egy másik hosztportot, például `-p 8080:8000`, és ehelyett a `http://localhost:8080/canvas` címet nyisd meg.

> **Megjegyzés:** Az első indításkor felépül az Agent Server környezete a konténeren belül, így eltarthat néhány percig, amíg a háttérrendszer egészségesnek jelenti magát.

A `.openhands` csatolás megőrzi az LLM profilodat, az MCP szervereket és az automatizálásokat a konténer újraindításai között.
Ennek a visszajátszásnak a hátralévő része mindent az Agent Canvas felhasználói felületén keresztül konfigurál a böngésződben a `http://localhost:8000/canvas` címen.
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

Az első indításkor az Agent Canvas egy bevezető folyamatot indít.
Ebben a folyamatban:

1. Hagyd az **OpenHands** kiválasztva ügynökként, majd kattints a **Next** gombra.
2. A **Set up your LLM** résznél válaszd az **Advanced** lehetőséget.
3. Hagyd az **Authentication** beállítást **API key** értéken.
4. Állítsd be a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsd be a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe adj meg bármilyen nem üres helykitöltőt, például `lemonade-local` értéket. A Lemonade nem igényel valódi kulcsot, de az OpenHands kliensnek szüksége van egy értékre a küldéshez.

<!-- @os:windows -->
> **Windows (Docker):** az Agent Server a konténeren belül fut, ezért a **Base URL** mezőt állítsd `http://host.docker.internal:13305/api/v1` értékre a `http://127.0.0.1:13305/api/v1` helyett.
> A konténeren belülről nézve a `127.0.0.1` maga a konténer; a `host.docker.internal` a Windows hoszton futó Lemonade-hez vezet, és ezt a hosztnevet a Docker Desktop automatikusan biztosítja.
<!-- @os:end -->

A kapcsolati mezőknek így kell kinézniük.
Az API key mezőt a felhasználói felület elrejti.

![Agent Canvas első használatkori LLM Advanced beállítások a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Ezután válaszd az **All** lehetőséget, és állítsd be a további helyi modellel kapcsolatos mezőket:

1. Görgess a **Custom Tokenizer** mezőhöz, és állítsd be erre: `Qwen/Qwen3.6-35B-A3B`.
2. Görgess a **LiteLLM Extra Body** mezőhöz, és állítsd be erre: `{"enable_thinking": true}`.
3. Kattints a **Next** gombra.

![Agent Canvas első használatkori LLM All fül a Qwen egyedi tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas első használatkori LLM All fül a beállított LiteLLM extra body-val](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak az alábbiakat kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag jelzi a LiteLLM számára, hogy OpenAI-kompatibilis kérésformázást használjon a Lemonade végponttal szemben.
Az egyedi tokenizáló a GGUF modell eredeti Hugging Face tokenizálója; ez teszi lehetővé, hogy az OpenHands ugyanazokat a chat-sablon tokeneket számolja, mint amelyeket a helyi modellkiszolgáló lát.
A jelenlegi első használatkori LLM űrlap nem jeleníti meg a condenser beállításokat.
Ha az Agent Canvas buildje később megjeleníti a condenser beállításokat a **Settings > LLM** alatt, használd az `llm_summarizing` beállítást, és állítsd a maximális tokenszámot a Lemonade kontextusablaka alá, például `56000` értékre.

## 5. GitHub és Slack MCP szerverek telepítése

Az Agent Canvas felhasználói felületén nyisd meg a **Customize** (vagy **Settings > MCP**) menüpontot azoknak az MCP szervereknek a hozzáadásához, amelyek eszközöket biztosítanak az ügynöknek a GitHubhoz és a Slackhez.
A tokenértékek csak a helyi Agent Serverhez kerülnek elküldésre, és titkosított beállításokként tárolódnak.

<!-- @os:windows -->
> **Windows (Docker):** az alábbi `npx` MCP szerver parancsok a konténeren belül futnak, amely már tartalmazza a Node.js-t, így semmi extra nem kerül telepítésre a hosztgépen.
> Mivel a `.openhands` mappa csatolva van, az MCP szerverek és tokenjeik megmaradnak a konténer újraindításai között.
<!-- @os:end -->

### GitHub MCP szerver

Adj hozzá egy új MCP szervert az alábbi beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = a GitHub tokened |

Használj olyan GitHub tokent, amely olvasási hozzáféréssel rendelkezik az összefoglalni kívánt repóhoz.

### Slack MCP szerver

Adj hozzá egy második MCP szervert az alábbi beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = a digest csatornád azonosítója |

Állítsd be a `SLACK_CHANNEL_IDS` értékét a digest csatorna azonosítójára (ugyanaz az érték, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne kelljen minden Slack csatornát végignéznie.

Mindkét szerver hozzáadása után használd a **Test** gombot mindegyiken, hogy megbizonyosodj a kapcsolat sikerességéről és az eszközök hirdetéséről.
A GitHub szervernek GitHub eszközöket, a Slack szervernek pedig Slack eszközöket kell listáznia.

![Agent Canvas MCP oldal telepített GitHub és Slack szerverekkel](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. A digest automatizálás létrehozása

Az Agent Canvas felhasználói felületén nyisd meg az **Automations** oldalt, és hozz létre egy új automatizálást:

1. Válaszd a **Create automation** lehetőséget, majd a **Prompt preset** típust.
2. Állítsd a **Name** mezőt erre: `GitHub Development Digest to Slack`.
3. Állítsd a **Prompt** mezőt az alábbi szövegre, a repó és a csatorna helykitöltőit a saját értékeidre cserélve:

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

4. Állítsd a **Trigger** mezőt **Cron** értékre a `0 9 * * 1-5` ütemezéssel (hétköznap reggel 9-kor), és állítsd be a **Timezone** mezőt a saját időzónádra, például `America/New_York` értékre.
5. Állítsd a **Timeout** mezőt `900` másodpercre.
6. Mentsd el az automatizálást.

Az automatizálás részletoldala megjeleníti az új automatizálást a cron triggerével és a generált prompt-preset belépési ponttal.

![Agent Canvas automatizálás részletoldala a létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az Agent Canvas UI automatizálás-részletező oldaláról:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra, hogy azonnal, egyszer lefuttassa az automatizálást.
2. Figyelje a futtatási listát ugyanazon az oldalon. A legutóbbi futtatásnak `COMPLETED` állapotba kell kerülnie.
3. Nyissa meg a cél Slack-csatornát. Tartalmaznia kell a generált digestet.

Nem kell megvárnia a cron ütemezés lefutását – a **Run now** azonnali futtatást indít, így megerősítheti, hogy a prompt, az MCP-kapcsolatok és a Slack-küldés is működik, mielőtt az ütemezésre hagyatkozna.

![Az Agent Canvas automatizálás futtatása sikeresen befejeződött](assets/06-automation-run-completed.png)

![A Slack-csatorna a generált OpenHands digestet mutatja](assets/07-slackbot-message.png)

## Hibaelhárítás

<!-- @os:windows -->
- **A Docker 8000-es portja már foglalt:** rendeljen hozzá egy másik hoszt portot, például `docker run ... -p 8080:8000 ...`, majd nyissa meg a `http://localhost:8080/canvas` címet.
- **A `docker pull` hitelesítési hibával leáll** (például: „A specified logon session does not exist"): futtassa a pull-t interaktív Windows-munkamenetből, vagy húzza le előre a képet. A kép nyilvános, így nincs szükség `docker login` parancsra.
- **A UI betölt, de a háttérrendszer nem egészséges:** az első indításkor az Agent Server környezet felépítése a konténeren belül történik. Várjon egy percet, és frissítse az oldalt, majd ellenőrizze a `docker logs <container>` kimenetét a folyamat állapotáért.
- **Az Agent Canvas nem éri el a Lemonade-et a konténerből:** állítsa be az LLM **Base URL** mezőjét a `http://host.docker.internal:13305/api/v1` értékre (ne `127.0.0.1`-re), és győződjön meg róla, hogy a Lemonade fut a Windows hoszton.
<!-- @os:end -->

- **A Lemonade nem fut:** indítsa újra az 1. lépésben szereplő `lemonade run "${LEMONADE_MODEL}"` paranccsal, majd futtassa újra az állapotellenőrzést.
- **Az `npm install -g` jogosultsági hibával leáll:** Linuxon vagy WSL-en állítson be egy felhasználó tulajdonában lévő globális npm könyvtárat, adja hozzá a shell indítófájljához, majd telepítse újra az Agent Canvast:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ha `zsh`-t használ, ugyanazt az `export PATH=...` sort a `~/.bashrc` helyett a `~/.zshrc` fájlhoz adja hozzá.
- **Az Agent Canvas elutasítja az LLM-beállításokat a `custom_tokenizer` beállítása után:** telepítse a `transformers` csomagot az Agent Server Python-környezetében, szükség esetén indítsa újra az Agent Canvast, majd próbálja meg újra menteni az LLM-beállításokat. Az OpenHandsnek szüksége van a Transformersre a tokenizáló chat sablonjának betöltéséhez, ha a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-et:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancsot, és győződjön meg róla, hogy az első használatkor megjelenő LLM-űrlapon vagy a **Settings > LLM** menüben megadott base URL megegyezik a futó helyi végponttal vagy a HTTPS-alagúttal.
- **Az LLM-beállítások nem mentődtek:** győződjön meg róla, hogy az értékek megadása után az **Next** gombra kattintott. Nyissa meg újra a **Settings > LLM** menüt az értékek megőrzésének ellenőrzéséhez.
- **A GitHub MCP nem látja a privát repókat:** ellenőrizze, hogy a GitHub tokennek van-e olvasási jogosultsága a cél repóhoz, és hogy a **Customize** menüben az MCP **Test** gombja jelzi-e a GitHub eszközöket.
- **A Slack tudja olvasni a csatornákat, de nem tud posztolni:** hívja meg a Slack alkalmazást a cél csatornába, és győződjön meg róla, hogy a bot rendelkezik `chat:write` jogosultsággal.
- **Az automatizálás túl sok Slack-csatornát listáz:** használjon Slack csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálás futtatása sikertelen, vagy túllépi a kontextust:** ellenőrizze, hogy a Lemonade `ctx_size=65536` beállítással indult-e, hogy az OpenHands LLM-nél be van-e állítva a `custom_tokenizer`, és használjon explicit repót, a GitHub eredményhalmazokat 3–5 elemre korlátozva. Ha az Agent Canvas kiépítése tartalmaz kondenzáló beállításokat, állítsa be a kondenzáló maximum token értékét a Lemonade kontextusablaka alá.

## Következő lépések

- Adjon hozzá egy heti, csak kiadásokra vonatkozó digestet.
- Adjon hozzá egy GitHub eseményalapú automatizálást a gyorsabb PR- vagy push-riasztásokért.
- Irányítsa ugyanazt a digestet Notionba, Linearbe, vagy egy másik MCP-alapú eszközbe.

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