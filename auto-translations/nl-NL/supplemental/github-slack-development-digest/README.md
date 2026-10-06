<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Overzicht

Ontwikkelaars besteden veel tijd aan kleine terugkerende cycli: het beoordelen van gelabelde pull requests, het beantwoorden van GitHub-opmerkingen, het triëren van nieuwe issues, het omzetten van Slack-threads in standup-notities of incidentopvolgingen, en het bijhouden van release- of onderzoekssignalen.
Elke cyclus is bekend, maar vereist nog steeds inzicht: het verzamelen van de juiste context, bepalen wat belangrijk is, en een duidelijke update plaatsen waar het team al werkt.

[OpenHands-automatiseringen](https://docs.openhands.dev/openhands/usage/automations/overview) veranderen die cycli in geplande of gebeurtenisgestuurde agentgesprekken: runs waarin een AI-softwareagent context kan lezen, tools kan aanroepen en een update kan produceren.
De gedeelde automatiseringssjablonen in de OpenHands-extensiecatalogus volgen dit patroon voor GitHub pull request-beoordeling, repositorymonitoring, Linear issue-triage, incidentretrospectieven, Slack-standupoverzichten en onderzoeksbriefings: een automatisering ontwaakt, gebruikt geconfigureerde integraties zoals GitHub of Slack om context op te halen, redeneert over die context met een groot taalmodel (LLM), en schrijft een resultaat terug.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is het lokale controlecentrum voor het bouwen en testen van die automatiseringen.
In deze playbook draait het een OpenHands Agent Server, het backendproces dat agentgesprekken uitvoert, en verbindt het de agent met externe diensten zoals GitHub en Slack.

Om de workflow op uw AMD-systeem te houden, communiceert de agent met een lokaal model dat wordt aangeboden door Lemonade Server.
Lemonade stelt dat model beschikbaar via een OpenAI-compatibele API, zodat Agent Canvas het kan configureren als een extern OpenAI-achtig eindpunt, terwijl het model, de prompt en de workflowcontext lokaal blijven.

In deze playbook bouwt u één concrete automatisering: een geplande GitHub-naar-Slack-ontwikkelingsoverzicht.
Het gebruikt GitHub om recente repositoryactiviteit te inspecteren, Slack om het overzicht te plaatsen, Agent Canvas API-aanroepen om de automatisering te configureren en te testen, en Lemonade om de LLM lokaal uit te voeren.

![Architectuurdiagram met GitHub MCP, OpenHands-automatisering, Lemonade Server en Slack MCP](assets/00-architecture-overview.png)

## Wat u gaat leren

- Hoe u Lemonade Server start en controleert of een lokaal model chatverzoeken beantwoordt
- Hoe u Agent Canvas start en de Agent Server ervan naar een lokale LLM wijst
- Hoe u GitHub- en Slack Model Context Protocol (MCP)-servers installeert via de Agent Server API
- Hoe u een geplande OpenHands-automatisering maakt en verzendt die een ontwikkelingsoverzicht naar Slack plaatst
- Hoe u de meest voorkomende storingen in lokale modellen en automatiseringen oplost

## Kernconcepten

| Concept | Wat het is | Waar het past in deze playbook |
| --- | --- | --- |
| Lemonade Server | Een lokaal LLM-serveerplatform gebouwd voor AMD-hardware dat een OpenAI-compatibele API beschikbaar stelt. Uw gegevens verlaten nooit uw machine. | Voert het model uit dat de agent aandrijft. |
| OpenHands Agent Server | Het backendproces dat OpenHands-agentgesprekken uitvoert. | Host de agent, diens LLM-profiel en diens MCP-servers. |
| Agent Canvas | Het lokale controlecentrum voor OpenHands dat Agent Server en een UI voor het inspecteren van agentruns uitvoert. | Start de backends en biedt de API die u aanroept. |
| MCP-server | Een Model Context Protocol-server die een agent tools geeft voor een externe dienst zoals GitHub of Slack. | Laat de agent GitHub lezen en naar Slack schrijven. |
| OpenHands-automatisering | Een geplande of gebeurtenisgestuurde agentgesprek dat context ophaalt, erover redeneert en ergens een resultaat schrijft. | Het GitHub-naar-Slack-overzicht dat u hier bouwt. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Workflows met codeerende agents profiteren van een groter model en contextvenster.
> Gebruik ten minste 32 GB systeemgeheugen, en geef de voorkeur aan 64 GB of meer voor grotere GGUF-modellen.
<!-- @device:end -->

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Vereisten

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

U hebt het volgende nodig:

- Lemonade Server geïnstalleerd volgens de standaard [Lemonade-installatiehandleiding](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 of nieuwer en `npm`, gebruikt om de gepubliceerde Agent Canvas CLI te installeren en MCP-servers uit te voeren met `npx`.
- `uv`, de Python-pakketbeheerder die Agent Canvas gebruikt om de Agent Server-omgeving te bouwen. Als dit nog niet is geïnstalleerd, installeer het dan via de [uv-installatiehandleiding](https://docs.astral.sh/uv/getting-started/installation/).
- Een recent gepubliceerd `@openhands/agent-canvas`-pakket met schemagestuurde agentinstellingen, `LLMSummarizingCondenserSettings.max_tokens`, en ondersteuning voor `custom_tokenizer` van de LLM.
- Het Python-pakket `transformers` beschikbaar in de Agent Server-omgeving. Dit is vereist voor het tellen van chat-sjabloon-tokens wanneer `custom_tokenizer` is ingesteld.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop voor Windows](https://docs.docker.com/desktop/setup/install/windows-install/), geïnstalleerd en actief. Op Windows draait de Agent Canvas-stack vanuit de gepubliceerde Docker-image, die Node.js, `uv`, `transformers` en het `@openhands/agent-canvas`-pakket bundelt, zodat u deze niet op de host hoeft te installeren.
<!-- @os:end -->

- Een GitHub-token met leestoegang tot de repository die u wilt samenvatten.
- Een Slack-bottoken (`xoxb-...`) met `chat:write` en kanaalleestoegang.
- Een Slack-team-ID (`T...`).
- Een Slack-kanaal-ID (`C...`) waar het overzicht moet worden geplaatst.

Nodig de Slack-app uit voor het doelkanaal voordat u de automatisering test.
## Variabelen die in dit playbook worden gebruikt

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

Deze twee variabelen worden gebruikt door de verificatieopdrachten hieronder.
Het model, de tokenizer en andere LLM-instellingen worden in latere stappen rechtstreeks ingevoerd in de Agent Canvas UI, dus de letterlijke waarden ervan worden inline weergegeven waar je ze nodig hebt.

De volgende waarden worden in latere stappen ingevoerd in de Agent Canvas UI.
Stel ze hier in zodat je ze kunt overnemen:

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

Gebruik een expliciete `owner/repo`-waarde voor `GITHUB_REPO_FILTER`.
Brede wildcards voor organisaties kunnen te veel MCP-context opleveren voor lokale modellen.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Start Lemonade Server

Start het model vanuit de Lemonade CLI:

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

> **Kies een model dat bij je hardware past.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) is een sterk model voor deze workflow, maar vereist een grote geheugenpool.
> Als je apparaat beperkt geheugen of GPU-VRAM heeft, kies dan een kleiner GGUF-model uit de Lemonade modelbibliotheek en gebruik die model-ID (en de bijbehorende tokenizer) doorheen dit playbook.

> **Opmerking:** De eerste `lemonade run` downloadt het model als het nog niet aanwezig is, wat afhankelijk van de modelgrootte en je verbinding even kan duren.

Lemonade biedt een OpenAI-compatibele API aan op:

```text
http://127.0.0.1:13305/api/v1
```

Optioneel: als Agent Canvas of de automatiseringsrunner niet op dezelfde machine draait, publiceer dan het Lemonade-eindpunt via een beveiligde tunnel en gebruik de HTTPS-URL als de LLM-basis-URL.
[ngrok](https://ngrok.com/) stelt een lokale poort via een beveiligde HTTPS-URL beschikbaar op internet; dit vereist een gratis ngrok-account, en je vervangt `YOUR_NGROK_DOMAIN.ngrok-free.dev` door je eigen gereserveerde domein:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifieer het lokale model

Bevestig dat Lemonade het geselecteerde model kan serveren:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Stuur vervolgens een klein chatverzoek:

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

Stuur vervolgens een klein chatverzoek:

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

Als dit een `choices`-array retourneert, is Lemonade klaar voor Agent Canvas.

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

## 3. Start Agent Canvas

<!-- @os:linux -->
Installeer het gepubliceerde Agent Canvas-pakket en start de volledige stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Als de globale npm-installatie mislukt met een machtigingsfout, raadpleeg dan het probleemoplossingsonderdeel over npm-machtigingen hieronder.

Standaard start Agent Canvas op `http://localhost:8000`.
Open die URL in je browser.
De poort is niet bijzonder—als 8000 al in gebruik is, geef dan een vrije poort op met `--port` (of `-p`).
De standaard lokale backend zou op het startscherm als gezond moeten verschijnen.

> **Opmerking:** De eerste start bouwt de door `uv` beheerde Python-omgeving van de Agent Server op, dus het kan een paar minuten duren voordat de backend als gezond wordt gerapporteerd.

Het commando `agent-canvas` start de agent server, de automatiseringsbackend en de webfrontend samen.
Je hebt slechts dit ene commando nodig om OpenHands lokaal uit te voeren.
De rest van dit playbook configureert alles via de Agent Canvas UI in je browser.
<!-- @os:end -->

<!-- @os:windows -->
Voer op Windows de gepubliceerde Agent Canvas-container-image uit met Docker Desktop.
De image bundelt de Agent Server, automatiseringsbackend en webfrontend, dus je hoeft Node.js, `uv` of de CLI niet op de host te installeren.

Maak eerst de config- en workspace-mappen aan die de container mount:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Haal de gepubliceerde image op (ongeveer 6 GB; deze is openbaar, dus er is geen login vereist):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Start vervolgens de stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Open `http://localhost:8000/canvas` in je browser.
Als poort 8000 al in gebruik is, wijs dan een andere hostpoort toe, bijvoorbeeld `-p 8080:8000`, en open in plaats daarvan `http://localhost:8080/canvas`.

> **Opmerking:** De eerste start bouwt de Agent Server-omgeving binnen de container op, dus het kan een paar minuten duren voordat de backend als gezond wordt gerapporteerd.

De `.openhands`-mount behoudt je LLM-profiel, MCP-servers en automatiseringen bij het opnieuw opstarten van de container.
De rest van dit playbook configureert alles via de Agent Canvas UI in je browser op `http://localhost:8000/canvas`.
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
## 4. Configureer de Lokale LLM in de UI

Bij de eerste start opent Agent Canvas een onboardingflow.
In die flow:

1. Houd **OpenHands** geselecteerd als de agent en klik op **Next**.
2. Selecteer op **Set up your LLM** de optie **Advanced**.
3. Houd **Authentication** ingesteld op **API key**.
4. Stel **Custom Model** in op `openai/Qwen3.6-35B-A3B-GGUF`.
5. Stel **Base URL** in op `http://127.0.0.1:13305/api/v1`.
6. Voer bij **API Key** een willekeurige, niet-lege placeholder in, zoals `lemonade-local`. Lemonade vereist geen echte sleutel, maar de OpenHands-client moet wel een waarde meesturen.

<!-- @os:windows -->
> **Windows (Docker):** de Agent Server draait binnen de container, dus stel **Base URL** in op `http://host.docker.internal:13305/api/v1` in plaats van `http://127.0.0.1:13305/api/v1`.
> Vanuit de container gezien is `127.0.0.1` de container zelf; `host.docker.internal` bereikt Lemonade dat op de Windows-host draait, en Docker Desktop biedt die hostnaam automatisch aan.
<!-- @os:end -->

De verbindingsvelden zouden er zo uit moeten zien.
Het API-sleutelveld wordt door de UI gemaskeerd weergegeven.

![Agent Canvas-instellingen voor LLM Advanced bij eerste gebruik met het Lemonade-model en lokale base-URL](assets/01-llm-advanced-settings.png)

Selecteer vervolgens **All** en stel de extra velden voor het lokale model in:

1. Scroll naar **Custom Tokenizer** en stel deze in op `Qwen/Qwen3.6-35B-A3B`.
2. Scroll naar **LiteLLM Extra Body** en stel deze in op `{"enable_thinking": true}`.
3. Klik op **Next**.

![Agent Canvas-tabblad LLM All bij eerste gebruik met de aangepaste Qwen-tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas-tabblad LLM All bij eerste gebruik met geconfigureerde LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

De LLM-instellingen moeten het volgende tonen:

| Veld | Waarde |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Het `openai/`-voorvoegsel vertelt LiteLLM om OpenAI-compatibele requestopmaak te gebruiken tegen het Lemonade-endpoint.
De aangepaste tokenizer is de originele Hugging Face-tokenizer voor het GGUF-model; hiermee kan OpenHands dezelfde chat-template-tokens tellen die de lokale modelserver ziet.
Het huidige LLM-formulier voor eerste gebruik toont geen condenser-instellingen.
Als uw Agent Canvas-build later condenser-instellingen aanbiedt onder **Settings > LLM**, gebruik dan `llm_summarizing` en stel het maximum aantal tokens in onder het Lemonade-contextvenster, bijvoorbeeld `56000`.

## 5. Installeer GitHub- en Slack-MCP-servers

Open in de Agent Canvas-UI **Customize** (of **Settings > MCP**) om de MCP-servers toe te voegen die de agent tools geven voor GitHub en Slack.
Tokenwaarden worden alleen naar uw lokale Agent Server verzonden en worden opgeslagen als versleutelde instellingen.

<!-- @os:windows -->
> **Windows (Docker):** de onderstaande `npx` MCP-servercommando's draaien binnen de container, die al Node.js bevat, dus er wordt niets extra's op de host geïnstalleerd.
> Omdat `.openhands` is gekoppeld, blijven de MCP-servers en hun tokens behouden bij het opnieuw opstarten van de container.
<!-- @os:end -->

### GitHub MCP-server

Voeg een nieuwe MCP-server toe met deze instellingen:

| Veld | Waarde |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = uw GitHub-token |

Gebruik een GitHub-token met leestoegang tot de repository die u wilt samenvatten.

### Slack MCP-server

Voeg een tweede MCP-server toe met deze instellingen:

| Veld | Waarde |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = uw digest-kanaal-ID |

Stel `SLACK_CHANNEL_IDS` in op het digest-kanaal-ID (dezelfde waarde als `SLACK_DIGEST_CHANNEL`), zodat de agent niet door elk Slack-kanaal hoeft te bladeren.

Gebruik na het toevoegen van beide servers de knop **Test** op elke server om te bevestigen dat deze verbinding maakt en tools aanbiedt.
De GitHub-server moet GitHub-tools tonen, en de Slack-server moet Slack-tools tonen.

![Agent Canvas MCP-pagina met geïnstalleerde GitHub- en Slack-servers](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Maak de Digest-automatisering

Open in de Agent Canvas-UI de pagina **Automations** en maak een nieuwe automatisering:

1. Kies **Create automation** en selecteer het type **Prompt preset**.
2. Stel de **Name** in op `GitHub Development Digest to Slack`.
3. Stel de **Prompt** in op de volgende tekst en vervang de placeholders voor repository en kanaal door uw eigen waarden:

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

4. Stel de **Trigger** in op **Cron** met het schema `0 9 * * 1-5` (9 uur 's ochtends op weekdagen) en stel de **Timezone** in op uw tijdzone, bijvoorbeeld `America/New_York`.
5. Stel de **Timeout** in op `900` seconden.
6. Sla de automatisering op.

De detailpagina van de automatisering toont de nieuwe automatisering met de cron-trigger en het gegenereerde prompt-preset-entrypoint.

![Agent Canvas-automatiseringsdetail na aanmaak](assets/05-automation-created.png)
## 7. Test de automatisering

Vanaf de detailpagina van de automatisering in de Agent Canvas UI:

1. Klik op **Run now** (of **Dispatch**) om de automatisering direct één keer uit te voeren.
2. Bekijk de lijst met runs op dezelfde pagina. De meest recente run moet overgaan naar `COMPLETED`.
3. Open je doel-Slackkanaal. Het zou de gegenereerde digest moeten bevatten.

Je hoeft niet te wachten tot het cron-schema wordt geactiveerd—**Run now** activeert een run op aanvraag, zodat je kunt bevestigen dat de prompt, de MCP-verbindingen en het plaatsen in Slack allemaal werken voordat je op het schema vertrouwt.

![Agent Canvas-automatiseringsrun succesvol voltooid](assets/06-automation-run-completed.png)

![Slackkanaal met de gegenereerde OpenHands-digest](assets/07-slackbot-message.png)

## Probleemoplossing

<!-- @os:windows -->
- **Docker-poort 8000 is al in gebruik:** koppel een andere hostpoort, bijvoorbeeld `docker run ... -p 8080:8000 ...`, en open `http://localhost:8080/canvas`.
- **`docker pull` mislukt met een inloggegevensfout** (bijvoorbeeld: "A specified logon session does not exist"): voer de pull uit vanuit een interactieve Windows-sessie, of haal de image vooraf op. De image is openbaar, dus er is geen `docker login` vereist.
- **De UI laadt, maar de backend is ongezond:** bij de eerste start wordt de Agent Server-omgeving binnen de container opgebouwd. Wacht een minuutje en vernieuw de pagina, controleer daarna `docker logs <container>` voor voortgang.
- **Agent Canvas kan Lemonade niet bereiken vanuit de container:** stel de LLM **Base URL** in op `http://host.docker.internal:13305/api/v1` (niet `127.0.0.1`), en bevestig dat Lemonade draait op de Windows-host.
<!-- @os:end -->

- **Lemonade is offline:** start het opnieuw met het `lemonade run "${LEMONADE_MODEL}"`-commando uit stap 1, en voer daarna de gezondheidscontrole opnieuw uit.
- **`npm install -g` mislukt met een rechtenfout:** configureer op Linux of WSL een map voor globale npm-installaties die eigendom is van de gebruiker, voeg deze toe aan je shell-opstartbestand en installeer Agent Canvas opnieuw:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Als je `zsh` gebruikt, voeg dan dezelfde `export PATH=...`-regel toe aan `~/.zshrc` in plaats van `~/.bashrc`.
- **Agent Canvas weigert de LLM-instellingen na het instellen van `custom_tokenizer`:** installeer `transformers` in de Python-omgeving van de Agent Server, start Agent Canvas opnieuw indien nodig, en probeer de LLM-instellingen opnieuw op te slaan. OpenHands vereist Transformers om de tokenizer-chattemplate te laden wanneer `custom_tokenizer` is ingesteld.
- **Agent Canvas kan Lemonade niet bereiken:** controleer `curl -fsS "${LEMONADE_BASE_URL}/health"` en bevestig dat de base URL die is ingevoerd in het LLM-formulier bij eerste gebruik of bij **Settings > LLM** overeenkomt met het actieve lokale eindpunt of de HTTPS-tunnel.
- **De LLM-instellingen zijn niet opgeslagen:** zorg ervoor dat je op **Next** hebt geklikt na het invoeren van de waarden. Open **Settings > LLM** opnieuw om te bevestigen dat de waarden behouden zijn gebleven.
- **GitHub MCP kan geen privérepositories zien:** controleer of het GitHub-token leesrechten heeft voor de doelrepository en of de MCP **Test**-knop in **Customize** GitHub-tools aankondigt.
- **Slack kan kanalen lezen, maar kan niet posten:** nodig de Slack-app uit voor het doelkanaal en bevestig dat de bot `chat:write`-rechten heeft.
- **De automatisering toont te veel Slackkanalen:** gebruik een Slack-kanaal-ID en stel `SLACK_CHANNEL_IDS` in op de Slack MCP-server in **Customize**.
- **De run van de automatisering mislukt of overschrijdt de context:** bevestig dat Lemonade is gestart met `ctx_size=65536`, bevestig dat de OpenHands LLM `custom_tokenizer` heeft ingesteld, en gebruik een expliciete repository met GitHub-resultaten die beperkt zijn tot 3 tot 5 items. Als jouw Agent Canvas-build condenser-instellingen biedt, stel dan het maximale aantal condenser-tokens in onder het Lemonade-contextvenster.

## Volgende stappen

- Voeg een wekelijkse digest toe die alleen releases bevat.
- Voeg een door GitHub-events geactiveerde automatisering toe voor snellere PR- of push-meldingen.
- Stuur dezelfde digest door naar Notion, Linear of een andere MCP-ondersteunde tool.

## Bronnen

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-documentatie](https://lemonade-server.ai/docs)
- [OpenHands-extensies repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servers](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-pakket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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