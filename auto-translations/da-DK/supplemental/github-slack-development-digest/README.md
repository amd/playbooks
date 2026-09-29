<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversigt

Udviklere bruger meget tid på små, tilbagevendende opgaver: gennemgang af mærkede pull requests, besvarelse af GitHub-kommentarer, triagering af nye issues, omdannelse af Slack-tråde til standup-noter eller opfølgning på hændelser og overvågning af release- eller forskningssignaler.
Hver opgave er velkendt, men kræver stadig vurdering: at indhente den rette kontekst, afgøre hvad der er vigtigt, og lægge en klar opdatering, hvor teamet allerede arbejder.

[OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) omdanner disse opgaver til planlagte eller hændelsesudløste agentsamtaler: kørsler hvor en AI-softwareagent kan læse kontekst, kalde værktøjer og producere en opdatering.
De delte automatiseringsskabeloner i OpenHands-udvidelseskataloget følger dette mønster for GitHub pull request-gennemgang, overvågning af repositories, triagering af Linear-issues, hændelsesopfølgning, Slack standup-digests og forskningsresuméer: en automatisering vågner, bruger konfigurerede integrationer såsom GitHub eller Slack til at hente kontekst, ræsonnerer over den kontekst med en stor sprogmodel (LLM) og skriver et resultat tilbage.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det lokale kontrolplan til at bygge og teste disse automatiseringer.
I denne playbook kører det en OpenHands Agent Server, den backend-proces der udfører agentsamtaler, og forbinder agenten til eksterne tjenester såsom GitHub og Slack.

For at holde arbejdsgangen på dit AMD-system taler agenten med en lokal model, der serveres af Lemonade Server.
Lemonade eksponerer den model via et OpenAI-kompatibelt API, så Agent Canvas kan konfigurere det som et eksternt OpenAI-lignende endpoint, mens modellen, prompten og arbejdsgangskonteksten forbliver lokal.

I denne playbook bygger du én konkret automatisering: en planlagt GitHub-til-Slack-udviklingsdigest.
Den bruger GitHub til at inspicere nylig repository-aktivitet, Slack til at poste digesten, Agent Canvas API-kald til at konfigurere og teste automatiseringen, og Lemonade til at køre LLM'en lokalt.

![Arkitekturdiagram der viser GitHub MCP, OpenHands-automatisering, Lemonade Server og Slack MCP](assets/00-architecture-overview.png)

## Hvad du vil lære

- Hvordan man starter Lemonade Server og verificerer, at en lokal model besvarer chatanmodninger
- Hvordan man starter Agent Canvas og peger dens Agent Server mod en lokal LLM
- Hvordan man installerer GitHub- og Slack Model Context Protocol (MCP)-servere via Agent Server API'et
- Hvordan man opretter og udsender en planlagt OpenHands-automatisering, der poster en udviklingsdigest til Slack
- Hvordan man fejlfinder de mest almindelige fejl med lokale modeller og automatiseringer

## Grundlæggende begreber

| Begreb | Hvad det er | Hvor det passer ind i denne playbook |
| --- | --- | --- |
| Lemonade Server | En platform til lokal LLM-servering bygget til AMD-hardware, der eksponerer et OpenAI-kompatibelt API. Dine data forlader aldrig din maskine. | Kører modellen, der driver agenten. |
| OpenHands Agent Server | Den backend-proces, der udfører OpenHands-agentsamtaler. | Hoster agenten, dens LLM-profil og dens MCP-servere. |
| Agent Canvas | Det lokale kontrolplan for OpenHands, der kører Agent Server og en UI til at inspicere agentkørsler. | Starter backends og stiller API'et til rådighed, som du kalder. |
| MCP-server | En Model Context Protocol-server, der giver en agent værktøjer til en ekstern tjeneste såsom GitHub eller Slack. | Lader agenten læse GitHub og skrive til Slack. |
| OpenHands-automatisering | En planlagt eller hændelsesudløst agentsamtale, der henter kontekst, ræsonnerer over den og skriver et resultat et sted. | GitHub-til-Slack-digesten, du bygger her. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Coding-agent-arbejdsgange har gavn af en større model og et større kontekstvindue.
> Brug mindst 32 GB systemhukommelse, og foretræk 64 GB eller mere til større GGUF-modeller.
<!-- @device:end -->

## Angivelse af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Forudsætninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Du skal bruge:

- Lemonade Server installeret ved at følge den standard [Lemonade-installationsguide](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 eller nyere og `npm`, som bruges til at installere den udgivne Agent Canvas CLI og køre MCP-servere med `npx`.
- `uv`, den Python-pakkemanager Agent Canvas bruger til at bygge Agent Server-miljøet. Hvis det ikke allerede er installeret, kan det installeres fra [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/).
- En nylig udgivet `@openhands/agent-canvas`-pakke med skemastyrede agentindstillinger, `LLMSummarizingCondenserSettings.max_tokens`, og understøttelse af LLM `custom_tokenizer`.
- Python-pakken `transformers` tilgængelig i Agent Server-miljøet. Den er nødvendig til optælling af chat-template-tokens, når `custom_tokenizer` er angivet.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installeret og kørende. På Windows kører Agent Canvas-stakken fra det udgivne Docker-image, som bundler Node.js, `uv`, `transformers` og `@openhands/agent-canvas`-pakken, så du behøver ikke installere disse på værten.
<!-- @os:end -->

- Et GitHub-token med læseadgang til det repository, du ønsker opsummeret.
- Et Slack-bot-token (`xoxb-...`) med `chat:write` og adgang til at læse kanaler.
- Et Slack-team-ID (`T...`).
- Et Slack-kanal-ID (`C...`), hvor digesten skal postes.

Inviter Slack-appen til målkanalen, før du tester automatiseringen.
## Variables, der bruges i denne playbook

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

Disse to variabler bruges af verifikationskommandoerne nedenfor.
Modellen, tokenizeren og andre LLM-indstillinger indtastes direkte i Agent Canvas UI i senere trin, så deres bogstavelige værdier vises inline, hvor du har brug for dem.

Følgende værdier indtastes i Agent Canvas UI i senere trin.
Angiv dem her, så du kan kopiere dem ind:

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

Brug en eksplicit `owner/repo`-værdi for `GITHUB_REPO_FILTER`.
Brede organisations-wildcards kan returnere for meget MCP-kontekst til lokale modeller.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Start Lemonade Server

Start modellen fra Lemonade CLI:

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

> **Vælg en model, der passer til din hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) er en stærk model til dette workflow, men kræver en stor hukommelsespulje.
> Hvis din enhed har begrænset hukommelse eller GPU VRAM, så vælg en mindre GGUF-model fra Lemonade-modelbiblioteket, og brug det pågældende model-ID (og dets tilhørende tokenizer) gennem hele denne playbook.

> **Bemærk:** Den første `lemonade run` downloader modellen, hvis den ikke allerede findes, hvilket kan tage et stykke tid afhængigt af modellens størrelse og din forbindelse.

Lemonade eksponerer en OpenAI-kompatibel API på:

```text
http://127.0.0.1:13305/api/v1
```

Valgfrit: hvis Agent Canvas eller automatiseringskøreren ikke er på samme maskine, kan du publicere Lemonade-endepunktet via en sikker tunnel og bruge HTTPS-URL'en som LLM-basis-URL.
[ngrok](https://ngrok.com/) eksponerer en lokal port til internettet via en sikker HTTPS-URL; det kræver en gratis ngrok-konto, og du erstatter `YOUR_NGROK_DOMAIN.ngrok-free.dev` med dit eget reserverede domæne:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificer den lokale model

Bekræft, at Lemonade kan servere den valgte model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Send derefter en lille chatanmodning:

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

Send derefter en lille chatanmodning:

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

Hvis dette returnerer et `choices`-array, er Lemonade klar til Agent Canvas.

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
Installer den udgivne Agent Canvas-pakke, og start hele stakken:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Hvis den globale npm-installation fejler med en tilladelsesfejl, se afsnittet om fejlfinding af npm-tilladelser nedenfor.

Som standard starter Agent Canvas på `http://localhost:8000`.
Åbn den URL i din browser.
Porten er ikke speciel—hvis 8000 allerede er i brug, kan du angive en ledig port med `--port` (eller `-p`).
Den standardmæssige lokale backend bør vises som sund på startskærmen.

> **Bemærk:** Den første opstart bygger Agent Serverens `uv`-styrede Python-miljø, så det kan tage et par minutter, før backenden rapporterer sund.

Kommandoen `agent-canvas` starter agentserveren, automatiseringsbackenden og webfrontenden sammen.
Du behøver kun denne ene kommando for at køre OpenHands lokalt.
Resten af denne playbook konfigurerer alt gennem Agent Canvas UI i din browser.
<!-- @os:end -->

<!-- @os:windows -->
På Windows skal du køre det udgivne Agent Canvas-containerimage med Docker Desktop.
Imaget indeholder Agent Serveren, automatiseringsbackenden og webfrontenden, så du behøver ikke at installere Node.js, `uv` eller CLI'en på værtsmaskinen.

Opret først de konfigurations- og arbejdsområdemapper, som containeren monterer:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hent det udgivne image (ca. 6 GB; det er offentligt, så der kræves ikke login):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Start derefter stakken:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Åbn `http://localhost:8000/canvas` i din browser.
Hvis port 8000 allerede er i brug, kan du mappe en anden værtsport, for eksempel `-p 8080:8000`, og åbne `http://localhost:8080/canvas` i stedet.

> **Bemærk:** Den første opstart bygger Agent Server-miljøet inde i containeren, så det kan tage et par minutter, før backenden rapporterer sund.

`.openhands`-monteringen bevarer din LLM-profil, MCP-servere og automatiseringer på tværs af containerens genstarter.
Resten af denne playbook konfigurerer alt gennem Agent Canvas UI i din browser på `http://localhost:8000/canvas`.
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
## 4. Konfigurer den lokale LLM i UI'en

Ved første start åbner Agent Canvas et onboarding-forløb.
I dette forløb:

1. Behold **OpenHands** valgt som agent, og klik på **Next**.
2. På **Set up your LLM** skal du vælge **Advanced**.
3. Behold **Authentication** sat til **API key**.
4. Sæt **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sæt **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key** skal du indtaste en vilkårlig ikke-tom pladsholder, f.eks. `lemonade-local`. Lemonade kræver ikke en rigtig nøgle, men OpenHands-klienten skal bruge en værdi at sende.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server kører inde i containeren, så sæt **Base URL** til `http://host.docker.internal:13305/api/v1` i stedet for `http://127.0.0.1:13305/api/v1`.
> Set indefra containeren er `127.0.0.1` containeren selv; `host.docker.internal` når frem til Lemonade, som kører på Windows-værten, og Docker Desktop leverer automatisk dette hostnavn.
<!-- @os:end -->

Forbindelsesfelterne bør se sådan ud.
API-nøgle-feltet er maskeret af UI'en.

![Agent Canvas første-brugs LLM Advanced-indstillinger med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Vælg derefter **All**, og angiv de ekstra felter for lokal model:

1. Rul til **Custom Tokenizer**, og sæt den til `Qwen/Qwen3.6-35B-A3B`.
2. Rul til **LiteLLM Extra Body**, og sæt den til `{"enable_thinking": true}`.
3. Klik på **Next**.

![Agent Canvas første-brugs LLM All-fane med den brugerdefinerede Qwen-tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas første-brugs LLM All-fane med konfigureret LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM-indstillingerne bør vise:

| Felt | Værdi |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/`-præfikset fortæller LiteLLM at bruge OpenAI-kompatibel anmodningsformatering mod Lemonade-endpointet.
Den brugerdefinerede tokenizer er den originale Hugging Face-tokenizer til GGUF-modellen; den gør det muligt for OpenHands at tælle de samme chat-template-tokens, som den lokale modelserver ser.
Den nuværende første-brugs-LLM-formular viser ikke condenser-indstillinger.
Hvis din Agent Canvas-build senere eksponerer condenser-indstillinger under **Settings > LLM**, skal du bruge `llm_summarizing` og sætte maks. antal tokens under Lemonade-kontekstvinduet, f.eks. `56000`.

## 5. Installer GitHub- og Slack-MCP-servere

I Agent Canvas-UI'en skal du åbne **Customize** (eller **Settings > MCP**) for at tilføje de MCP-servere, der giver agenten værktøjer til GitHub og Slack.
Token-værdier sendes kun til din lokale Agent Server og gemmes som krypterede indstillinger.

<!-- @os:windows -->
> **Windows (Docker):** de `npx`-MCP-server-kommandoer nedenfor kører inde i containeren, som allerede indeholder Node.js, så der installeres intet ekstra på værten.
> Fordi `.openhands` er monteret, bevares MCP-serverne og deres tokens på tværs af genstart af containeren.
<!-- @os:end -->

### GitHub-MCP-server

Tilføj en ny MCP-server med følgende indstillinger:

| Felt | Værdi |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = dit GitHub-token |

Brug et GitHub-token med læseadgang til det repository, du vil have opsummeret.

### Slack-MCP-server

Tilføj en anden MCP-server med følgende indstillinger:

| Felt | Værdi |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = dit digest-kanal-ID |

Sæt `SLACK_CHANNEL_IDS` til digest-kanal-ID'et (samme værdi som `SLACK_DIGEST_CHANNEL`), så agenten ikke skal bladre gennem alle Slack-kanaler.

Efter du har tilføjet begge servere, skal du bruge **Test**-knappen på hver af dem for at bekræfte, at den forbinder og annoncerer værktøjer.
GitHub-serveren bør vise GitHub-værktøjer, og Slack-serveren bør vise Slack-værktøjer.

![Agent Canvas MCP-side med installerede GitHub- og Slack-servere](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Opret digest-automatiseringen

I Agent Canvas-UI'en skal du åbne siden **Automations** og oprette en ny automatisering:

1. Vælg **Create automation**, og vælg typen **Prompt preset**.
2. Sæt **Name** til `GitHub Development Digest to Slack`.
3. Sæt **Prompt** til følgende tekst, og erstat pladsholderne for repository og kanal med dine egne værdier:

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

4. Sæt **Trigger** til **Cron** med tidsplanen `0 9 * * 1-5` (kl. 9 på hverdage), og sæt **Timezone** til din tidszone, f.eks. `America/New_York`.
5. Sæt **Timeout** til `900` sekunder.
6. Gem automatiseringen.

Automatiseringens detaljeside viser den nye automatisering med dens cron-trigger og det genererede prompt-preset-entrypoint.

![Agent Canvas automatiseringsdetalje efter oprettelse](assets/05-automation-created.png)
## 7. Test automatiseringen

Fra automatiseringens detaljeside i Agent Canvas UI:

1. Klik på **Run now** (eller **Dispatch**) for at køre automatiseringen én gang med det samme.
2. Følg med i kørselslisten på samme side. Den seneste kørsel skulle skifte til `COMPLETED`.
3. Åbn din valgte Slack-kanal. Den skulle nu indeholde det genererede digest.

Du behøver ikke vente på, at cron-planen udløses—**Run now** udløser en kørsel på forlangende, så du kan bekræfte, at prompten, MCP-forbindelserne og Slack-postingen alle fungerer, før du er afhængig af tidsplanen.

![Agent Canvas-automatiseringskørsel gennemført med succes](assets/06-automation-run-completed.png)

![Slack-kanal der viser det genererede OpenHands-digest](assets/07-slackbot-message.png)

## Fejlfinding

<!-- @os:windows -->
- **Docker-port 8000 er allerede i brug:** map en anden vært-port, for eksempel `docker run ... -p 8080:8000 ...`, og åbn `http://localhost:8080/canvas`.
- **`docker pull` fejler med en legitimationsfejl** (for eksempel "A specified logon session does not exist"): kør pull'et fra en interaktiv Windows-session, eller hent forudgående (pre-pull) image'et. Image'et er offentligt, så ingen `docker login` er nødvendig.
- **UI'et indlæses, men backend er usund:** den første opstart bygger Agent Server-miljøet inde i containeren. Vent et minut og opdater, og tjek derefter `docker logs <container>` for fremdrift.
- **Agent Canvas kan ikke nå Lemonade fra containeren:** sæt LLM'ens **Base URL** til `http://host.docker.internal:13305/api/v1` (ikke `127.0.0.1`), og bekræft, at Lemonade kører på Windows-værten.
<!-- @os:end -->

- **Lemonade er nede:** genstart det med kommandoen `lemonade run "${LEMONADE_MODEL}"` i trin 1, og kør derefter helbredstjekket igen.
- **`npm install -g` fejler med en tilladelsesfejl:** på Linux eller WSL, konfigurer en brugerejet global npm-mappe, tilføj den til din shell-startupfil, og installer derefter Agent Canvas igen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Hvis du bruger `zsh`, skal du tilføje den samme `export PATH=...`-linje til `~/.zshrc` i stedet for `~/.bashrc`.
- **Agent Canvas afviser LLM-indstillingerne efter angivelse af `custom_tokenizer`:** installer `transformers` i Agent Server Python-miljøet, genstart Agent Canvas om nødvendigt, og prøv igen at gemme LLM-indstillingerne. OpenHands kræver Transformers for at indlæse tokenizer chat-skabelonen, når `custom_tokenizer` er sat.
- **Agent Canvas kan ikke nå Lemonade:** kontroller `curl -fsS "${LEMONADE_BASE_URL}/health"`, og bekræft at base-URL'en indtastet i førstegangs-LLM-formularen eller **Settings > LLM** matcher det kørende lokale endpoint eller HTTPS-tunnel.
- **LLM-indstillingerne blev ikke gemt:** sørg for, at du klikkede på **Next** efter at have indtastet værdierne. Genåbn **Settings > LLM** for at bekræfte, at værdierne blev bevaret.
- **GitHub MCP kan ikke se private repositories:** bekræft, at GitHub-token'en har læseadgang til mål-repositoriet, og at MCP'ens **Test**-knap i **Customize** viser GitHub-værktøjer.
- **Slack kan læse kanaler, men kan ikke poste:** inviter Slack-appen til mål-kanalen, og bekræft, at bot'en har `chat:write`.
- **Automatiseringen viser for mange Slack-kanaler:** brug et Slack-kanal-ID og sæt `SLACK_CHANNEL_IDS` på Slack MCP-serveren i **Customize**.
- **Automatiseringskørslen fejler eller overskrider konteksten:** bekræft, at Lemonade blev startet med `ctx_size=65536`, bekræft at OpenHands LLM'en har `custom_tokenizer` sat, og brug et eksplicit repository med GitHub-resultatsæt begrænset til 3 til 5 elementer. Hvis din Agent Canvas-build eksponerer condenser-indstillinger, skal du sætte condenser max tokens under Lemonade-kontekstvinduet.

## Næste skridt

- Tilføj et ugentligt digest, der kun indeholder releases.
- Tilføj en GitHub-hændelsesudløst automatisering for hurtigere PR- eller push-advarsler.
- Send det samme digest videre til Notion, Linear eller et andet MCP-baseret værktøj.

## Ressourcer

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)
- [OpenHands extensions-repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servere](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-pakke](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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