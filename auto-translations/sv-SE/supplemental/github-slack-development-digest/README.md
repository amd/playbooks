<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Översikt

Utvecklare lägger ner mycket tid på små återkommande slingor: granska märkta pull requests, svara på GitHub-kommentarer, triagera nya ärenden, omvandla Slack-trådar till standup-anteckningar eller incidentuppföljningar, och följa upp release- eller forskningssignaler.
Varje slinga är bekant, men den kräver fortfarande omdöme: samla rätt kontext, avgöra vad som är viktigt och publicera en tydlig uppdatering där teamet redan arbetar.

[OpenHands-automationer](https://docs.openhands.dev/openhands/usage/automations/overview) förvandlar dessa slingor till schemalagda eller händelseutlösta agentkonversationer: körningar där en AI-mjukvaruagent kan läsa kontext, anropa verktyg och producera en uppdatering.
De delade automationsmallarna i OpenHands-tilläggskatalogen följer detta mönster för GitHub pull request-granskning, repository-övervakning, Linear-ärendetriage, incidentretrospektiv, Slack-standupsammanfattningar och forskningssammanfattningar: en automation vaknar, använder konfigurerade integrationer såsom GitHub eller Slack för att hämta kontext, resonerar kring den kontexten med en stor språkmodell (LLM) och skriver tillbaka ett resultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) är den lokala kontrollplattformen för att bygga och testa dessa automationer.
I den här handboken kör den en OpenHands Agent Server, bakgrundsprocessen som exekverar agentkonversationer, och kopplar agenten till externa tjänster såsom GitHub och Slack.

För att hålla arbetsflödet på ditt AMD-system pratar agenten med en lokal modell som serveras av Lemonade Server.
Lemonade exponerar den modellen genom ett OpenAI-kompatibelt API, så Agent Canvas kan konfigurera den som en fjärransluten OpenAI-liknande slutpunkt medan modellen, prompten och arbetsflödeskontexten förblir lokala.

I den här handboken bygger du en konkret automation: en schemalagd GitHub-till-Slack-utvecklingssammanfattning.
Den använder GitHub för att inspektera senaste repository-aktivitet, Slack för att publicera sammanfattningen, Agent Canvas API-anrop för att konfigurera och testa automationen, och Lemonade för att köra LLM:en lokalt.

![Arkitekturdiagram som visar GitHub MCP, OpenHands-automation, Lemonade Server och Slack MCP](assets/00-architecture-overview.png)

## Vad du kommer att lära dig

- Hur man startar Lemonade Server och verifierar att en lokal modell svarar på chattförfrågningar
- Hur man startar Agent Canvas och pekar dess Agent Server mot en lokal LLM
- Hur man installerar GitHub- och Slack-servrar för Model Context Protocol (MCP) genom Agent Server-API:et
- Hur man skapar och skickar iväg en schemalagd OpenHands-automation som publicerar en utvecklingssammanfattning till Slack
- Hur man felsöker de vanligaste felen med lokal modell och automation

## Grundläggande koncept

| Koncept | Vad det är | Var det passar in i den här handboken |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform byggd för AMD-hårdvara som exponerar ett OpenAI-kompatibelt API. Dina data lämnar aldrig din maskin. | Kör modellen som driver agenten. |
| OpenHands Agent Server | Bakgrundsprocessen som exekverar OpenHands-agentkonversationer. | Hostar agenten, dess LLM-profil och dess MCP-servrar. |
| Agent Canvas | Den lokala kontrollplattformen för OpenHands som kör Agent Server och ett gränssnitt för att inspektera agentkörningar. | Startar bakgrundstjänsterna och tillhandahåller API:et du anropar. |
| MCP-server | En Model Context Protocol-server som ger en agent verktyg för en extern tjänst såsom GitHub eller Slack. | Låter agenten läsa GitHub och skriva till Slack. |
| OpenHands-automation | En schemalagd eller händelseutlöst agentkonversation som hämtar kontext, resonerar kring den och skriver ett resultat någonstans. | GitHub-till-Slack-sammanfattningen du bygger här. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Arbetsflöden med kodningsagenter gynnas av en större modell och ett större kontextfönster.
> Använd minst 32 GB systemminne, och föredra 64 GB eller mer för större GGUF-modeller.
<!-- @device:end -->

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Förutsättningar

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

Du behöver:

- Lemonade Server installerad genom att följa den vanliga [installationsguiden för Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 eller senare samt `npm`, som används för att installera det publicerade Agent Canvas CLI-verktyget och köra MCP-servrar med `npx`.
- `uv`, Python-pakethanteraren som Agent Canvas använder för att bygga Agent Server-miljön. Om den inte redan är installerad, installera den från [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/).
- Ett nyligen publicerat `@openhands/agent-canvas`-paket med schemastyrda agentinställningar, `LLMSummarizingCondenserSettings.max_tokens`, och stöd för LLM `custom_tokenizer`.
- Python-paketet `transformers` tillgängligt i Agent Server-miljön. Det krävs för tokenräkning av chattmallar när `custom_tokenizer` är inställt.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop för Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installerad och igång. På Windows körs Agent Canvas-stacken från den publicerade Docker-avbildningen, som paketerar Node.js, `uv`, `transformers` och paketet `@openhands/agent-canvas`, så du behöver inte installera dessa på värden.
<!-- @os:end -->

- En GitHub-token med läsbehörighet till det repository du vill sammanfatta.
- En Slack-bottoken (`xoxb-...`) med `chat:write` och läsbehörighet till kanaler.
- Ett Slack-team-ID (`T...`).
- Ett Slack-kanal-ID (`C...`) där sammanfattningen ska publiceras.

Bjud in Slack-appen till målkanalen innan du testar automationen.
## Variabler som används i denna playbook

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

Dessa två variabler används av verifieringskommandona nedan.
Modellen, tokeniseraren och andra LLM-inställningar anges direkt i Agent Canvas UI i senare steg, så deras bokstavliga värden visas infogade där du behöver dem.

Följande värden anges i Agent Canvas UI i senare steg.
Ange dem här så att du kan kopiera in dem:

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

Använd ett explicit `owner/repo`-värde för `GITHUB_REPO_FILTER`.
Breda jokertecken för organisationer kan returnera för mycket MCP-kontext för lokala modeller.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Starta Lemonade Server

Starta modellen från Lemonade CLI:

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

> **Välj en modell som passar din hårdvara.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) är en stark modell för detta arbetsflöde men behöver en stor minnespool.
> Om din enhet har begränsat minne eller GPU-VRAM, välj en mindre GGUF-modell från Lemonade-modellbiblioteket och använd det modell-ID:et (och dess matchande tokeniserare) genomgående i denna playbook.

> **Obs:** Det första `lemonade run` laddar ner modellen om den inte redan finns, vilket kan ta ett tag beroende på modellens storlek och din anslutning.

Lemonade exponerar ett OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

Valfritt: om Agent Canvas eller automatiseringskörningsmiljön inte finns på samma maskin, publicera Lemonade-slutpunkten genom en säker tunnel och använd HTTPS-URL:en som LLM-basadress.
[ngrok](https://ngrok.com/) exponerar en lokal port mot internet via en säker HTTPS-URL; det kräver ett gratis ngrok-konto, och du ersätter `YOUR_NGROK_DOMAIN.ngrok-free.dev` med din egen reserverade domän:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifiera den lokala modellen

Bekräfta att Lemonade kan servera den valda modellen:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Skicka sedan en liten chattförfrågan:

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

Skicka sedan en liten chattförfrågan:

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

Om detta returnerar en `choices`-array är Lemonade redo för Agent Canvas.

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

## 3. Starta Agent Canvas

<!-- @os:linux -->
Installera det publicerade Agent Canvas-paketet och starta hela stacken:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Om den globala npm-installationen misslyckas med ett behörighetsfel, se felsökningsposten för npm-behörigheter nedan.

Som standard startar Agent Canvas på `http://localhost:8000`.
Öppna den URL:en i din webbläsare.
Porten är inte speciell—om 8000 redan används, ange en ledig port med `--port` (eller `-p`).
Standardbackenden lokalt bör visas som frisk (healthy) på startskärmen.

> **Obs:** Den första starten bygger Agent Server-tjänstens `uv`-hanterade Python-miljö, så det kan ta några minuter innan backenden rapporterar att den är frisk.

Kommandot `agent-canvas` startar agentservern, automatiseringsbackenden och webbfrontend tillsammans.
Du behöver bara detta enda kommando för att köra OpenHands lokalt.
Resten av denna playbook konfigurerar allt genom Agent Canvas UI i din webbläsare.
<!-- @os:end -->

<!-- @os:windows -->
På Windows, kör den publicerade Agent Canvas-containeravbildningen med Docker Desktop.
Avbildningen levereras med Agent Server, automatiseringsbackend och webbfrontend, så du behöver inte installera Node.js, `uv` eller CLI:n på värden.

Skapa först konfigurations- och arbetsytemapparna som containern monterar:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hämta den publicerade avbildningen (cirka 6 GB; den är publik, så ingen inloggning krävs):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Starta sedan stacken:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Öppna `http://localhost:8000/canvas` i din webbläsare.
Om port 8000 redan används, mappa en annan värdport, till exempel `-p 8080:8000`, och öppna `http://localhost:8080/canvas` istället.

> **Obs:** Den första starten bygger Agent Server-miljön inuti containern, så det kan ta några minuter innan backenden rapporterar att den är frisk.

Monteringen `.openhands` bevarar din LLM-profil, MCP-servrar och automatiseringar mellan containeromstarter.
Resten av denna playbook konfigurerar allt genom Agent Canvas UI i din webbläsare på `http://localhost:8000/canvas`.
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
## 4. Konfigurera den lokala LLM:n i användargränssnittet

Vid första start öppnas ett onboardingflöde i Agent Canvas.
I det flödet:

1. Behåll **OpenHands** som agent och klicka på **Next**.
2. Under **Set up your LLM**, välj **Advanced**.
3. Behåll **Authentication** inställt på **API key**.
4. Ange **Custom Model** till `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ange **Base URL** till `http://127.0.0.1:13305/api/v1`.
6. För **API Key**, ange valfri icke-tom platshållare, till exempel `lemonade-local`. Lemonade kräver inte en riktig nyckel, men OpenHands-klienten behöver ett värde att skicka.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server körs inuti containern, så ange **Base URL** till `http://host.docker.internal:13305/api/v1` istället för `http://127.0.0.1:13305/api/v1`.
> Från containerns insida är `127.0.0.1` containern själv; `host.docker.internal` når Lemonade som körs på Windows-värden, och Docker Desktop tillhandahåller det värdnamnet automatiskt.
<!-- @os:end -->

Anslutningsfälten ska se ut så här.
API-nyckelfältet är maskerat av användargränssnittet.

![Agent Canvas första användningens LLM Advanced-inställningar med Lemonade-modellen och lokal bas-URL](assets/01-llm-advanced-settings.png)

Välj sedan **All** och ange de extra fälten för lokal modell:

1. Scrolla till **Custom Tokenizer** och ange det till `Qwen/Qwen3.6-35B-A3B`.
2. Scrolla till **LiteLLM Extra Body** och ange det till `{"enable_thinking": true}`.
3. Klicka på **Next**.

![Agent Canvas första användningens LLM All-flik med Qwen custom tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas första användningens LLM All-flik med konfigurerad LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM-inställningarna ska visa:

| Fält | Värde |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefixet `openai/` talar om för LiteLLM att använda OpenAI-kompatibel förfrågningsformatering mot Lemonade-slutpunkten.
Den anpassade tokeniseraren är den ursprungliga Hugging Face-tokeniseraren för GGUF-modellen; den gör att OpenHands kan räkna samma chat-template-tokens som den lokala modellservern ser.
Det nuvarande formuläret för första användningens LLM visar inte condenser-inställningar.
Om din Agent Canvas-build senare exponerar condenser-inställningar under **Settings > LLM**, använd `llm_summarizing` och ange max tokens under Lemonades kontextfönster, till exempel `56000`.

## 5. Installera GitHub- och Slack MCP-servrar

I Agent Canvas-användargränssnittet, öppna **Customize** (eller **Settings > MCP**) för att lägga till de MCP-servrar som ger agenten verktyg för GitHub och Slack.
Token-värden skickas endast till din lokala Agent Server och sparas som krypterade inställningar.

<!-- @os:windows -->
> **Windows (Docker):** `npx` MCP-serverkommandona nedan körs inuti containern, som redan inkluderar Node.js, så inget extra installeras på värden.
> Eftersom `.openhands` är monterad, bevaras MCP-servrarna och deras tokens mellan containeromstarter.
<!-- @os:end -->

### GitHub MCP-server

Lägg till en ny MCP-server med följande inställningar:

| Fält | Värde |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = din GitHub-token |

Använd en GitHub-token med läsbehörighet till det repository du vill sammanfatta.

### Slack MCP-server

Lägg till en andra MCP-server med följande inställningar:

| Fält | Värde |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ditt digest-kanal-ID |

Ange `SLACK_CHANNEL_IDS` till digest-kanalens ID (samma värde som `SLACK_DIGEST_CHANNEL`) så att agenten inte behöver bläddra igenom varenda Slack-kanal.

Efter att du har lagt till båda servrarna, använd knappen **Test** på var och en för att bekräfta att den ansluter och annonserar verktyg.
GitHub-servern bör lista GitHub-verktyg, och Slack-servern bör lista Slack-verktyg.

![Agent Canvas MCP-sida med installerade GitHub- och Slack-servrar](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Skapa digest-automatiseringen

Öppna sidan **Automations** i Agent Canvas-användargränssnittet och skapa en ny automatisering:

1. Välj **Create automation** och välj typen **Prompt preset**.
2. Ange **Name** till `GitHub Development Digest to Slack`.
3. Ange **Prompt** till följande text, och ersätt platshållarna för repository och kanal med dina egna värden:

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

4. Ange **Trigger** till **Cron** med schemat `0 9 * * 1-5` (kl. 9 på vardagar) och ange **Timezone** till din tidszon, till exempel `America/New_York`.
5. Ange **Timeout** till `900` sekunder.
6. Spara automatiseringen.

Automatiseringens detaljsida visar den nya automatiseringen med dess cron-trigger och den genererade prompt-preset-ingångspunkten.

![Agent Canvas automatiseringsdetaljer efter skapande](assets/05-automation-created.png)
## 7. Testa automatiseringen

Från detaljsidan för automatiseringen i Agent Canvas-användargränssnittet:

1. Klicka på **Run now** (eller **Dispatch**) för att köra automatiseringen en gång omedelbart.
2. Håll ett öga på körlistan på samma sida. Den senaste körningen bör övergå till `COMPLETED`.
3. Öppna din målkanal i Slack. Den bör innehålla det genererade sammandraget.

Du behöver inte vänta på att cron-schemat ska utlösas – **Run now** utlöser en körning på begäran så att du kan bekräfta att prompten, MCP-anslutningarna och Slack-publiceringen alla fungerar innan du förlitar dig på schemat.

![Agent Canvas-automatisering slutförd](assets/06-automation-run-completed.png)

![Slack-kanal som visar det genererade OpenHands-sammandraget](assets/07-slackbot-message.png)

## Felsökning

<!-- @os:windows -->
- **Docker-port 8000 används redan:** mappa en annan värdport, till exempel `docker run ... -p 8080:8000 ...`, och öppna `http://localhost:8080/canvas`.
- **`docker pull` misslyckas med ett autentiseringsfel** (till exempel "A specified logon session does not exist"): kör pull-kommandot från en interaktiv Windows-session, eller hämta avbildningen i förväg. Avbildningen är offentlig, så ingen `docker login` krävs.
- **Användargränssnittet laddas men serverdelen är i ett ohälsosamt tillstånd:** den första starten bygger Agent Server-miljön inuti containern. Vänta en minut och uppdatera, kontrollera sedan `docker logs <container>` för att se förloppet.
- **Agent Canvas kan inte nå Lemonade från containern:** ställ in LLM:ets **Base URL** till `http://host.docker.internal:13305/api/v1` (inte `127.0.0.1`), och bekräfta att Lemonade körs på Windows-värden.
<!-- @os:end -->

- **Lemonade är nere:** starta om det med kommandot `lemonade run "${LEMONADE_MODEL}"` i steg 1, kör sedan hälsokontrollen igen.
- **`npm install -g` misslyckas med ett behörighetsfel:** på Linux eller WSL, konfigurera en användarägd global npm-katalog, lägg till den i din skalstartfil och installera sedan Agent Canvas igen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Om du använder `zsh`, lägg till samma `export PATH=...`-rad i `~/.zshrc` istället för `~/.bashrc`.
- **Agent Canvas avvisar LLM-inställningarna efter att `custom_tokenizer` ställts in:** installera `transformers` i Agent Server-miljön för Python, starta om Agent Canvas vid behov och försök sedan spara LLM-inställningarna igen. OpenHands kräver Transformers för att ladda tokeniserarens chattmall när `custom_tokenizer` är inställt.
- **Agent Canvas kan inte nå Lemonade:** kontrollera `curl -fsS "${LEMONADE_BASE_URL}/health"` och bekräfta att bas-URL:en som angetts i formuläret för första användning av LLM eller i **Settings > LLM** matchar den körande lokala slutpunkten eller HTTPS-tunneln.
- **LLM-inställningarna sparades inte:** se till att du klickade på **Next** efter att ha angett värdena. Öppna **Settings > LLM** igen för att bekräfta att värdena sparades.
- **GitHub MCP kan inte se privata repositories:** bekräfta att GitHub-token har läsbehörighet till målrepositoryt och att MCP-knappen **Test** i **Customize** annonserar GitHub-verktyg.
- **Slack kan läsa kanaler men kan inte publicera:** bjud in Slack-appen till målkanalen och bekräfta att boten har `chat:write`.
- **Automatiseringen listar för många Slack-kanaler:** använd ett Slack-kanal-ID och ställ in `SLACK_CHANNEL_IDS` på Slack MCP-servern i **Customize**.
- **Automatiseringskörningen misslyckas eller överskrider kontexten:** bekräfta att Lemonade startades med `ctx_size=65536`, bekräfta att OpenHands LLM har `custom_tokenizer` inställt, och använd ett explicit repository med GitHub-resultatuppsättningar begränsade till 3 till 5 objekt. Om din Agent Canvas-version exponerar inställningar för kondenserare, ställ in maximalt antal tokens för kondenseraren under Lemonades kontextfönster.

## Nästa steg

- Lägg till ett veckovis sammandrag enbart för utgåvor.
- Lägg till en GitHub-händelseutlöst automatisering för snabbare PR- eller push-aviseringar.
- Dirigera samma sammandrag till Notion, Linear eller ett annat MCP-stött verktyg.

## Resurser

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)
- [OpenHands tilläggsrepository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servrar](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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