<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversikt

Utviklere bruker mye tid på små, tilbakevendende sløyfer: gjennomgå merkede pull requests, svare på GitHub-kommentarer, prioritere nye issues, gjøre om Slack-tråder til standup-notater eller hendelsesoppfølginger, og følge med på utgivelses- eller forskningssignaler.
Hver sløyfe er kjent, men den krever likevel skjønn: samle inn riktig kontekst, avgjøre hva som betyr noe, og legge ut en tydelig oppdatering der teamet allerede jobber.

[OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) gjør disse sløyfene om til planlagte eller hendelsesutløste agentsamtaler: kjøringer der en AI-programvareagent kan lese kontekst, kalle verktøy, og produsere en oppdatering.
De delte automatiseringsmalene i OpenHands-utvidelseskatalogen følger dette mønsteret for GitHub pull request-gjennomgang, overvåking av repositorier, Linear issue-prioritering, hendelsesgjennomganger, Slack-digester for standup, og forskningsoppsummeringer: en automatisering våkner, bruker konfigurerte integrasjoner som GitHub eller Slack til å hente kontekst, resonnerer over den konteksten med en stor språkmodell (LLM), og skriver tilbake et resultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det lokale kontrollplanet for å bygge og teste disse automatiseringene.
I denne oppskriften kjører den en OpenHands Agent Server, backend-prosessen som utfører agentsamtaler, og kobler agenten til eksterne tjenester som GitHub og Slack.

For å holde arbeidsflyten på ditt AMD-system, snakker agenten med en lokal modell servert av Lemonade Server.
Lemonade eksponerer den modellen gjennom et OpenAI-kompatibelt API, slik at Agent Canvas kan konfigurere det som et eksternt OpenAI-lignende endepunkt mens modellen, prompten og arbeidsflytkonteksten forblir lokal.

I denne oppskriften bygger du én konkret automatisering: en planlagt GitHub-til-Slack-utviklingsdigest.
Den bruker GitHub til å inspisere nylig repositorium-aktivitet, Slack til å legge ut digesten, Agent Canvas API-kall for å konfigurere og teste automatiseringen, og Lemonade til å kjøre LLM-en lokalt.

![Arkitekturdiagram som viser GitHub MCP, OpenHands-automatisering, Lemonade Server, og Slack MCP](assets/00-architecture-overview.png)

## Hva du vil lære

- Hvordan starte Lemonade Server og verifisere at en lokal modell svarer på chatforespørsler
- Hvordan starte Agent Canvas og peke Agent Server-en mot en lokal LLM
- Hvordan installere GitHub- og Slack Model Context Protocol (MCP)-servere gjennom Agent Server-API-et
- Hvordan opprette og sende ut en planlagt OpenHands-automatisering som legger ut en utviklingsdigest til Slack
- Hvordan feilsøke de vanligste feilene knyttet til lokal modell og automatisering

## Kjernekonsepter

| Konsept | Hva det er | Hvor det passer inn i denne oppskriften |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform bygget for AMD-maskinvare som eksponerer et OpenAI-kompatibelt API. Dataene dine forlater aldri maskinen din. | Kjører modellen som driver agenten. |
| OpenHands Agent Server | Backend-prosessen som utfører OpenHands-agentsamtaler. | Er vert for agenten, dens LLM-profil, og dens MCP-servere. |
| Agent Canvas | Det lokale kontrollplanet for OpenHands som kjører Agent Server og et grensesnitt for å inspisere agentkjøringer. | Starter backendene og gir API-et du kaller. |
| MCP-server | En Model Context Protocol-server som gir en agent verktøy for en ekstern tjeneste som GitHub eller Slack. | Lar agenten lese GitHub og skrive til Slack. |
| OpenHands-automatisering | En planlagt eller hendelsesutløst agentsamtale som henter kontekst, resonnerer over den, og skriver et resultat et sted. | GitHub-til-Slack-digesten du bygger her. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Kodingsagent-arbeidsflyter har nytte av en større modell og kontekstvindu.
> Bruk minst 32 GB systemminne, og foretrekk 64 GB eller mer for større GGUF-modeller.
<!-- @device:end -->

## Sette minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk for programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Forutsetninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Du trenger:

- Lemonade Server installert ved å følge den standard [Lemonade-installasjonsveiledningen](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 eller nyere og `npm`, brukt til å installere den publiserte Agent Canvas CLI-en og kjøre MCP-servere med `npx`.
- `uv`, Python-pakkebehandleren Agent Canvas bruker til å bygge Agent Server-miljøet. Hvis det ikke allerede er installert, installer det fra [uv-installasjonsveiledningen](https://docs.astral.sh/uv/getting-started/installation/).
- En nylig publisert `@openhands/agent-canvas`-pakke med skjemadrevne agentinnstillinger, `LLMSummarizingCondenserSettings.max_tokens`, og LLM `custom_tokenizer`-støtte.
- Python-pakken `transformers` tilgjengelig i Agent Server-miljøet. Den kreves for chat-mal-token-telling når `custom_tokenizer` er satt.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installert og kjørende. På Windows kjører Agent Canvas-stakken fra det publiserte Docker-bildet, som pakker med seg Node.js, `uv`, `transformers`, og `@openhands/agent-canvas`-pakken, slik at du ikke installerer disse på verten.
<!-- @os:end -->

- En GitHub-token med lesetilgang til repositoriet du vil ha oppsummert.
- En Slack-bot-token (`xoxb-...`) med `chat:write` og kanal-lesetilgang.
- En Slack-team-ID (`T...`).
- En Slack-kanal-ID (`C...`) der digesten skal legges ut.

Inviter Slack-appen til målkanalen før du tester automatiseringen.
## Variabler brukt i denne oppskriften

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

Disse to variablene brukes av verifiseringskommandoene nedenfor.
Modellen, tokenizeren og andre LLM-innstillinger legges inn direkte i Agent Canvas-brukergrensesnittet i senere trinn, så de bokstavelige verdiene deres vises direkte der du trenger dem.

Følgende verdier legges inn i Agent Canvas-brukergrensesnittet i senere trinn.
Sett dem her slik at du kan kopiere dem inn:

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

Bruk en eksplisitt `owner/repo`-verdi for `GITHUB_REPO_FILTER`.
Brede organisasjons-jokertegn kan gi for mye MCP-kontekst for lokale modeller.

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

> **Velg en modell som passer maskinvaren din.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) er en sterk modell for denne arbeidsflyten, men krever et stort minnebasseng.
> Hvis enheten din har begrenset minne eller GPU-VRAM, velg en mindre GGUF-modell fra Lemonade-modellbiblioteket og bruk den modell-ID-en (og tilhørende tokenizer) gjennom hele denne oppskriften.

> **Merk:** Den første `lemonade run` laster ned modellen hvis den ikke allerede finnes, noe som kan ta en stund avhengig av modellstørrelsen og tilkoblingen din.

Lemonade eksponerer et OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

Valgfritt: hvis Agent Canvas eller automasjonskjøreren ikke er på samme maskin, publiser Lemonade-endepunktet gjennom en sikker tunnel og bruk HTTPS-URL-en som LLM-basis-URL.
[ngrok](https://ngrok.com/) eksponerer en lokal port til internett over en sikker HTTPS-URL; det krever en gratis ngrok-konto, og du erstatter `YOUR_NGROK_DOMAIN.ngrok-free.dev` med ditt eget reserverte domene:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifiser den lokale modellen

Bekreft at Lemonade kan betjene den valgte modellen:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Send deretter en liten chat-forespørsel:

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

Send deretter en liten chat-forespørsel:

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

Hvis dette returnerer et `choices`-array, er Lemonade klar for Agent Canvas.

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
Installer den publiserte Agent Canvas-pakken og start hele stacken:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Hvis den globale npm-installasjonen mislykkes med en tillatelsesfeil, se feilsøkingsoppføringen for npm-tillatelser nedenfor.

Som standard starter Agent Canvas på `http://localhost:8000`.
Åpne den URL-en i nettleseren din.
Porten er ikke spesiell—hvis 8000 allerede er i bruk, angi en hvilken som helst ledig port med `--port` (eller `-p`).
Standard lokal backend bør vises som frisk på hjemskjermen.

> **Merk:** Den første oppstarten bygger Agent Server sitt `uv`-styrte Python-miljø, så det kan ta noen minutter før backenden rapporterer at den er frisk.

Kommandoen `agent-canvas` starter agentserveren, automasjonsbackenden og webfronten sammen.
Du trenger bare denne ene kommandoen for å kjøre OpenHands lokalt.
Resten av denne oppskriften konfigurerer alt gjennom Agent Canvas-brukergrensesnittet i nettleseren din.
<!-- @os:end -->

<!-- @os:windows -->
På Windows, kjør det publiserte Agent Canvas-containerbildet med Docker Desktop.
Bildet inkluderer Agent Server, automasjonsbackend og webfront, så du trenger ikke installere Node.js, `uv`, eller CLI-en på verten.

Opprett først config- og workspace-mappene som containeren monterer:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hent det publiserte bildet (ca. 6 GB; det er offentlig, så ingen innlogging kreves):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Start deretter stacken:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Åpne `http://localhost:8000/canvas` i nettleseren din.
Hvis port 8000 allerede er i bruk, kartlegg en annen vertsport, for eksempel `-p 8080:8000`, og åpne `http://localhost:8080/canvas` i stedet.

> **Merk:** Den første oppstarten bygger Agent Server-miljøet inne i containeren, så det kan ta noen minutter før backenden rapporterer at den er frisk.

`.openhands`-monteringen bevarer LLM-profilen din, MCP-serverne og automasjonene på tvers av containeromstarter.
Resten av denne oppskriften konfigurerer alt gjennom Agent Canvas-brukergrensesnittet i nettleseren din på `http://localhost:8000/canvas`.
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
## 4. Konfigurer den lokale LLM-en i brukergrensesnittet

Ved første oppstart åpner Agent Canvas en veiledningsflyt.
I den flyten:

1. Behold **OpenHands** valgt som agent, og klikk **Next**.
2. Under **Set up your LLM**, velg **Advanced**.
3. La **Authentication** stå som **API key**.
4. Sett **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sett **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, angi en hvilken som helst ikke-tom plassholder, for eksempel `lemonade-local`. Lemonade krever ikke en ekte nøkkel, men OpenHands-klienten trenger en verdi å sende.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server kjører inne i containeren, så sett **Base URL** til `http://host.docker.internal:13305/api/v1` i stedet for `http://127.0.0.1:13305/api/v1`.
> Sett innenfra containeren er `127.0.0.1` containeren selv; `host.docker.internal` når frem til Lemonade som kjører på Windows-verten, og Docker Desktop tilbyr dette vertsnavnet automatisk.
<!-- @os:end -->

Tilkoblingsfeltene skal se slik ut.
API-nøkkelfeltet er maskert av brukergrensesnittet.

![Agent Canvas første gangs LLM Advanced-innstillinger med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Velg deretter **All** og sett de ekstra feltene for lokal modell:

1. Bla til **Custom Tokenizer** og sett den til `Qwen/Qwen3.6-35B-A3B`.
2. Bla til **LiteLLM Extra Body** og sett den til `{"enable_thinking": true}`.
3. Klikk **Next**.

![Agent Canvas første gangs LLM All-fane med Qwen egendefinert tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas første gangs LLM All-fane med LiteLLM extra body konfigurert](assets/03-llm-all-extra-body-settings.png)

LLM-innstillingene skal vise:

| Felt | Verdi |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/`-prefikset forteller LiteLLM å bruke OpenAI-kompatibel forespørselsformatering mot Lemonade-endepunktet.
Den egendefinerte tokenizeren er den opprinnelige Hugging Face-tokenizeren for GGUF-modellen; den lar OpenHands telle de samme chat-mal-tokenene som den lokale modellserveren ser.
Det nåværende skjemaet for LLM ved første bruk viser ikke condenser-innstillinger.
Hvis din Agent Canvas-build eksponerer condenser-innstillinger senere under **Settings > LLM**, bruk `llm_summarizing` og sett maks tokens under Lemonade-kontekstvinduet, for eksempel `56000`.

## 5. Installer GitHub- og Slack-MCP-servere

I Agent Canvas-brukergrensesnittet, åpne **Customize** (eller **Settings > MCP**) for å legge til MCP-serverne som gir agenten verktøy for GitHub og Slack.
Tokenverdier sendes kun til din lokale Agent Server og lagres som krypterte innstillinger.

<!-- @os:windows -->
> **Windows (Docker):** `npx`-MCP-serverkommandoene nedenfor kjører inne i containeren, som allerede inkluderer Node.js, så ingenting ekstra installeres på verten.
> Fordi `.openhands` er montert, bevares MCP-serverne og tokenene deres på tvers av containeromstarter.
<!-- @os:end -->

### GitHub-MCP-server

Legg til en ny MCP-server med disse innstillingene:

| Felt | Verdi |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = din GitHub-token |

Bruk en GitHub-token med lesetilgang til depotet du vil oppsummere.

### Slack-MCP-server

Legg til en ny MCP-server med disse innstillingene:

| Felt | Verdi |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = din sammendrags-kanal-ID |

Sett `SLACK_CHANNEL_IDS` til sammendrags-kanal-ID-en (samme verdi som `SLACK_DIGEST_CHANNEL`) slik at agenten ikke trenger å bla gjennom hver eneste Slack-kanal.

Etter at begge serverne er lagt til, bruk **Test**-knappen på hver av dem for å bekrefte at den kobler til og annonserer verktøy.
GitHub-serveren skal liste GitHub-verktøy, og Slack-serveren skal liste Slack-verktøy.

![Agent Canvas MCP-side med GitHub- og Slack-servere installert](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Opprett sammendragsautomatiseringen

I Agent Canvas-brukergrensesnittet, åpne **Automations**-siden og opprett en ny automatisering:

1. Velg **Create automation** og velg typen **Prompt preset**.
2. Sett **Name** til `GitHub Development Digest to Slack`.
3. Sett **Prompt** til følgende tekst, og erstatt plassholderne for depot og kanal med dine egne verdier:

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

4. Sett **Trigger** til **Cron** med planen `0 9 * * 1-5` (kl. 9 på hverdager), og sett **Timezone** til din tidssone, for eksempel `America/New_York`.
5. Sett **Timeout** til `900` sekunder.
6. Lagre automatiseringen.

Detaljsiden for automatiseringen viser den nye automatiseringen med cron-utløseren og den genererte prompt-preset-inngangen.

![Agent Canvas automatiseringsdetaljer etter opprettelse](assets/05-automation-created.png)
## 7. Test automatiseringen

Fra automatiseringens detaljside i Agent Canvas UI:

1. Klikk på **Run now** (eller **Dispatch**) for å kjøre automatiseringen én gang umiddelbart.
2. Følg med på kjørelisten på samme side. Den siste kjøringen skal gå over til `COMPLETED`.
3. Åpne målkanalen din i Slack. Den skal inneholde den genererte oppsummeringen.

Du trenger ikke å vente på at cron-planen skal utløses – **Run now** utløser en kjøring på forespørsel, slik at du kan bekrefte at prompten, MCP-tilkoblingene og Slack-publiseringen fungerer før du stoler på tidsplanen.

![Agent Canvas-automatiseringskjøring fullført](assets/06-automation-run-completed.png)

![Slack-kanal som viser den genererte OpenHands-oppsummeringen](assets/07-slackbot-message.png)

## Feilsøking

<!-- @os:windows -->
- **Docker-port 8000 er allerede i bruk:** map en annen vertsport, for eksempel `docker run ... -p 8080:8000 ...`, og åpne `http://localhost:8080/canvas`.
- **`docker pull` mislykkes med en legitimasjonsfeil** (for eksempel «A specified logon session does not exist»): kjør pull-kommandoen fra en interaktiv Windows-økt, eller forhåndshent bildet på forhånd. Bildet er offentlig, så ingen `docker login` er nødvendig.
- **UI-et lastes, men backend er utilstrekkelig:** ved første oppstart bygges Agent Server-miljøet inne i containeren. Vent et minutt og oppdater siden, sjekk deretter `docker logs <container>` for fremdrift.
- **Agent Canvas kan ikke nå Lemonade fra containeren:** angi LLM-**Base URL** til `http://host.docker.internal:13305/api/v1` (ikke `127.0.0.1`), og bekreft at Lemonade kjører på Windows-verten.
<!-- @os:end -->

- **Lemonade er nede:** start den på nytt med kommandoen `lemonade run "${LEMONADE_MODEL}"` fra trinn 1, og kjør deretter helsesjekken på nytt.
- **`npm install -g` mislykkes med en tillatelsesfeil:** på Linux eller WSL, konfigurer en brukereid global npm-mappe, legg den til i oppstartsfilen for skallet ditt, og installer deretter Agent Canvas på nytt:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Hvis du bruker `zsh`, legg til samme `export PATH=...`-linje i `~/.zshrc` i stedet for `~/.bashrc`.
- **Agent Canvas avviser LLM-innstillingene etter at `custom_tokenizer` er angitt:** installer `transformers` i Agent Server sitt Python-miljø, start Agent Canvas på nytt om nødvendig, og prøv å lagre LLM-innstillingene igjen. OpenHands krever Transformers for å laste tokenizer-chatmalen når `custom_tokenizer` er angitt.
- **Agent Canvas kan ikke nå Lemonade:** bekreft `curl -fsS "${LEMONADE_BASE_URL}/health"` og sjekk at base-URL-en som er angitt i LLM-skjemaet ved første bruk eller under **Settings > LLM** samsvarer med det kjørende lokale endepunktet eller HTTPS-tunnelen.
- **LLM-innstillingene ble ikke lagret:** kontroller at du klikket **Next** etter at du fylte inn verdiene. Åpne **Settings > LLM** på nytt for å bekrefte at verdiene ble beholdt.
- **GitHub MCP kan ikke se private repositorier:** bekreft at GitHub-tokenet har lesetilgang til målrepositoriet, og at **Test**-knappen for MCP under **Customize** viser GitHub-verktøy.
- **Slack kan lese kanaler, men kan ikke publisere:** inviter Slack-appen til målkanalen og bekreft at boten har `chat:write`.
- **Automatiseringen viser for mange Slack-kanaler:** bruk en Slack-kanal-ID og angi `SLACK_CHANNEL_IDS` på Slack MCP-serveren under **Customize**.
- **Automatiseringskjøringen mislykkes eller overskrider konteksten:** bekreft at Lemonade ble startet med `ctx_size=65536`, bekreft at OpenHands-LLM-en har `custom_tokenizer` angitt, og bruk et eksplisitt repositorium med GitHub-resultatsett begrenset til 3–5 elementer. Hvis Agent Canvas-bygget ditt eksponerer condenser-innstillinger, sett maks antall condenser-tokens under Lemonade-kontekstvinduet.

## Neste steg

- Legg til en ukentlig oppsummering kun for utgivelser.
- Legg til en GitHub-hendelsesutløst automatisering for raskere PR- eller push-varsler.
- Rut den samme oppsummeringen til Notion, Linear eller et annet MCP-basert verktøy.

## Ressurser

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentasjon](https://lemonade-server.ai/docs)
- [OpenHands-utvidelsesrepositorium](https://github.com/OpenHands/extensions)
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