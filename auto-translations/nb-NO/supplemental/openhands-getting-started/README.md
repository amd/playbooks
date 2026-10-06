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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversikt

[OpenHands](https://github.com/All-Hands-AI/OpenHands) er en AI-programvareagent
som kan skrive kode, kjøre kommandoer, surfe på nettet og redigere filer i et
reelt arbeidsområde. I stedet for å kopiere forslag ut fra et chattevindu,
peker du agenten mot en prosjektmappe og lar den gjøre arbeidet: implementere
en funksjon, fikse en feil, skrive tester eller forklare en kodebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det anbefalte
nettleserbrukergrensesnittet for å kjøre OpenHands. En enkelt `agent-canvas`-kommando
starter agentserveren, automatiseringsbakenden og nettleserfronten sammen, slik
at du kan drive en samtale med agenten fra nettleseren din.

For å holde alt på AMD-systemet ditt, snakker agenten med en lokal modell som
serveres av Lemonade Server. Lemonade eksponerer den modellen gjennom et
OpenAI-kompatibelt API, slik at Agent Canvas kan konfigurere det som ethvert
annet OpenAI-stil-endepunkt, mens modellen, koden din og samtalekonteksten
forblir på maskinen din.

I denne oppskriften starter du en lokal modell, lanserer Agent Canvas, peker
den mot den modellen, og kjører din første kodeoppgave mot en reell
prosjektmappe.

## Hva du vil lære

- Hvordan starte Lemonade Server og bekrefte at en lokal modell svarer på
  chatteforespørsler
- Hvordan installere og starte Agent Canvas fra npm-pakken
- Hvordan konfigurere Agent Canvas til å bruke en lokal Lemonade-modell som LLM
- Hvordan starte en OpenHands-samtale og se agenten redigere filer og kjøre
  kommandoer i et arbeidsområde
- Hvordan gjennomgå hva agenten endret og styre den med oppfølgingsmeldinger

## Kjernebegreper

| Begrep | Hva det er | Hvor det passer inn i denne oppskriften |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform bygget for AMD-maskinvare som eksponerer et OpenAI-kompatibelt API. Dataene dine forlater aldri maskinen din. | Kjører modellen som driver agenten. |
| OpenHands | En AI-programvareagent som leser og redigerer filer, kjører skallkommandoer og surfer på nettet i et arbeidsområde. | Agenten du styrer fra chatten. |
| Agent Canvas | Nettleserbrukergrensesnittet og bakenden som kjører OpenHands-samtaler og viser verktøykall og filendringer. | Starter stacken og er vert for samtalen din. |
| Arbeidsområde | Prosjektmappen agenten har tillatelse til å lese og endre. | Målet for agentens redigeringer og kommandoer. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Kodeagent-arbeidsflyter drar nytte av en større modell og et større
> kontekstvindu. Bruk minst 32 GB systemminne, og foretrekk 64 GB eller mer for
> større GGUF-modeller.
<!-- @device:end -->

## Angi minnekonfigurasjon

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Forutsetninger


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Du trenger:

- Lemonade Server installert og i stand til å servere modellen nedenfor.

<!-- @os:linux -->
- Node.js 22.12 eller nyere og `npm` (brukes av `agent-canvas`-CLI-en).
- `uv`, Python-pakkebehandleren som Agent Canvas bruker til å administrere
  agentserverens miljø. Hvis systemet ditt ikke allerede har det, installer det
  fra [uv-installasjonsveiledningen](https://docs.astral.sh/uv/getting-started/installation/)
  før du starter Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installert og kjørende. På Windows kjører Agent Canvas-stacken fra det
  publiserte Docker-bildet, som pakker med Node.js, `uv` og
  `@openhands/agent-canvas`-pakken, slik at du ikke trenger å installere disse
  på verten.
<!-- @os:end -->

- En prosjektmappe å jobbe i. Dette kan være ethvert lokalt git-repositorium
  eller kodekatalog du vil at agenten skal jobbe på.

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

## 1. Start Lemonade Server

Start modellen fra Lemonade-CLI-en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Velg en modell som passer maskinvaren din.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) er en sterk kodemodell, men trenger en stor minnepool. Hvis enheten din har begrenset minne eller GPU-VRAM, velg i stedet en mindre GGUF-modell fra Lemonade-modellbiblioteket og bruk den modell-ID-en gjennom hele denne oppskriften.

> **Merk:** Den første `lemonade run` laster ned modellen hvis den ikke allerede finnes, noe som kan ta en stund avhengig av modellstørrelsen og tilkoblingen din.

Lemonade eksponerer et OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Bekreft den lokale modellen

Bekreft at Lemonade kan servere den valgte modellen:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Send deretter en liten chatteforespørsel:

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

Hvis dette returnerer en `choices`-array, er Lemonade klar for Agent Canvas.

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
## 3. Installer og start Agent Canvas

<!-- @os:linux -->
Installer den publiserte Agent Canvas-pakken globalt:

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

Start deretter hele stacken fra en terminal:

```bash
agent-canvas
```

Som standard starter Agent Canvas på `http://localhost:8000`. Åpne denne URL-en i
nettleseren din. Porten er ikke spesiell — hvis 8000 allerede er i bruk, kan du
angi en ledig port med `--port` (eller `-p`) når du starter Agent Canvas:

```bash
agent-canvas --port 3000
```

Åpne deretter `http://localhost:3000` i stedet. Standard lokal backend bør vises
som sunn (healthy) på startskjermen.

Kommandoen `agent-canvas` starter agentserveren, automasjonsbackenden og
webfrontenden sammen. Du trenger bare denne ene kommandoen for å kjøre OpenHands
lokalt.

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
På Windows kjører du det publiserte Agent Canvas-containerbildet med Docker Desktop.
Bildet inneholder agentserveren, automasjonsbackenden og webfrontenden, så du
trenger ikke installere Node.js, `uv` eller CLI-en på verten.

Opprett først konfigurasjons- og arbeidsområdemappene som containeren monterer:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Last ned det publiserte bildet (det er offentlig, så ingen innlogging kreves):

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

Åpne `http://localhost:8000/canvas` i nettleseren din. Hvis port 8000 allerede er i
bruk, kan du mappe en annen vertsport, for eksempel `-p 8080:8000`, og åpne
`http://localhost:8080/canvas` i stedet.

> **Merk:** Den første oppstarten initialiserer agentserveren inne i containeren,
> så det kan ta et minutt eller to før backenden rapporteres som sunn.

Monteringen `.openhands` lagrer LLM-profilen og innstillingene dine på tvers av
containeromstarter. Resten av denne veiledningen konfigurerer alt gjennom Agent
Canvas-brukergrensesnittet i nettleseren din.

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

## 4. Konfigurer den lokale LLM-en

Ved første oppstart åpner Agent Canvas en onboarding-flyt. I den flyten:

1. Behold **OpenHands** valgt som agent, og klikk **Next**.
2. På **Set up your LLM**, velg **Advanced**.
3. Behold **Authentication** satt til **API key**.
4. Sett **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sett **Base URL** til `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > På Windows kjører stacken i en container, som ikke kan nå verten på
   > `127.0.0.1`. Bruk `http://host.docker.internal:13305/api/v1` i stedet, slik at
   > den containeriserte agenten kan nå Lemonade som kjører på Windows-verten.
   <!-- @os:end -->
6. For **API Key**, skriv inn en hvilken som helst ikke-tom plassholder, for
   eksempel `lemonade-local`. Lemonade krever ikke en ekte nøkkel, men
   OpenHands-klienten trenger en verdi å sende.
7. Klikk **Next**.

De fullførte Advanced-innstillingene skal se slik ut. API-nøkkelfeltet er
maskert av brukergrensesnittet.

![Agent Canvas førstegangs LLM Advanced-innstillinger med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Agent Canvas lagrer disse verdiene som en LLM-profil. Hvis versjonen din ber deg
navngi denne profilen, bruk et navn uten mellomrom, for eksempel `lemonade-local`.
Hvis du bytter modeller senere, åpne **Settings > LLM** og oppdater de samme
Advanced-feltene. Du kan bytte mellom lagrede profiler fra chat-innfeltet med
kommandoen `/model`.

## 5. Åpne et arbeidsområde

Agenten kan bare lese og endre filer inne i et arbeidsområde du velger. Før du
starter en oppgave, pek Agent Canvas mot prosjektmappen din:

1. Fra startskjermen, velg **Open Workspace**.
2. Velg mappen som inneholder prosjektet ditt (for eksempel et git-repository
   du vil at agenten skal jobbe med).
3. Start en ny samtale i det arbeidsområdet.

Alt agenten gjør — lese filer, kjøre kommandoer, redigere kode — er
avgrenset til det arbeidsområdet.

![Agent Canvas-hjemmeskjerm etter onboarding](assets/02-agent-canvas-home.png)

## 6. Kjør din første kodeoppgave

Med arbeidsområdet åpent og den lokale LLM-en valgt, skriv en konkret oppgave inn
i chatten. En god første oppgave er liten og verifiserbar, for eksempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Følg med på samtaletidslinjen. OpenHands vil:

- Lese arbeidsområdet for å forstå oppsettet.
- Opprette `hello.py` med den forespurte funksjonen og testblokken.
- Eventuelt kjøre `python3 hello.py` for å verifisere resultatet.
- Rapportere hva den gjorde og eventuell kommandoutdata i chatten.

Du bør se den nye filen dukke opp i arbeidsområdet, og agentens avsluttende
melding bør beskrive endringen den gjorde. Dette er gjennombruddsøyeblikket:
agenten skrev og kjørte ekte kode i prosjektmappen din.

## 7. Gjennomgå og styr agenten

Etter at agenten har fullført et steg, gjennomgå arbeidet før du godkjenner neste:

- **Filendringer**: bruk filleseren i arbeidsområdet eller agentens diff-visning
  for å se nøyaktig hva som ble lagt til, endret eller slettet.
- **Kommandoutdata**: utvid en hvilken som helst kommando agenten kjørte for å se
  stdout, stderr og avslutningskoden.
- **Oppfølginger**: hvis resultatet ikke var det du ønsket, svar i samme
  samtale med en korrigering. Agenten beholder den tidligere konteksten og
  itererer på de samme filene.

For eksempel, hvis testen ikke skrev ut den forventede hilsenen, svar:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten vil lese filen på nytt, kjøre kommandoen, diagnostisere problemet og
redigere filen igjen — alt i samme samtale.
## Feilsøking

<!-- @os:linux -->
- **`agent-canvas` finnes ikke på PATH:** installer på nytt med
  `npm install -g @openhands/agent-canvas` og bekreft at npm sin globale
  binærkatalog er på PATH-en din før `agent-canvas` kan startes fra en ny
  terminal.
- **`npm install -g` mislykkes med en tillatelsesfeil:** konfigurer en
  brukereid global npm-katalog, åpne deretter terminalen på nytt og installer
  Agent Canvas igjen.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` mangler:** installer det fra
  [installasjonsveiledningen for uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas bruker `uv` til å administrere Python-miljøet for agentserveren.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` eller `docker run` klarer ikke å koble til:** sørg for at
  Docker Desktop kjører (hvalikonet vises i systemstatusfeltet) og at motoren
  har fullført oppstarten. `docker version` bør skrive ut både en Client- og
  en Server-del.
- **Beholderen starter, men backend blir aldri frisk (healthy):** den første
  oppstarten initialiserer Agent Server inne i beholderen; gi det et minutt
  eller to, og sjekk deretter `docker logs <container>` for feil.
- **Beholderen kan ikke nå Lemonade:** beholderen når verten via
  `host.docker.internal`. Bekreft at Lemonade betjener forespørsler på
  Windows-verten med `lemonade status`, og bruk
  `http://host.docker.internal:13305/api/v1` som Base URL når du konfigurerer
  LLM-en.
<!-- @os:end -->

- **UI-en lastes, men backend viser usunn tilstand:** vent et minutt eller to
  til agentserveren er ferdig med å starte, og oppdater deretter siden. Hvis
  den fortsatt er usunn, start stacken på nytt og sjekk loggene for feil.
- **Lemonade-chatforespørsler mislykkes med en tilkoblingsfeil:** bekreft at
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lykkes, og at Lemonade
  fortsatt betjener modellen med `lemonade status`.
- **Agenten feiler med en melding om kontekstlengde eller tokengrense:** start
  en ny samtale slik at agenten ikke bærer med seg en altfor stor historikk.
  Hvis det fortsetter å skje, start Lemonade på nytt med en større `ctx_size`
  enn standardverdien 65536 (for eksempel `ctx_size=131072`), så sant minnet
  tillater det.
- **Agenten produserer lavkvalitets- eller ufullstendige endringer:** bytt til
  en større modell i Lemonade, eller gi agenten en mindre, mer konkret oppgave
  og la den fullføre før du ber om neste endring.

## Neste steg

- Prøv en større oppgave i samme arbeidsområde, for eksempel å legge til en
  enhetstestfil eller fikse en kjent feil, og gjennomgå agentens diff før du
  beholder endringen.
- Koble til en MCP-server som GitHub eller Slack under **Customize** slik at
  agenten kan lese saker eller legge ut oppdateringer mens den jobber.
- Lagre flere LLM-profiler (en rask liten modell og en sterkere stor modell)
  og bytt mellom dem med `/model` midt i en samtale.
- Gå videre til [OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) for
  å gjøre tilbakevendende utviklingsløkker om til planlagte eller
  hendelsesutløste agentkjøringer.

## Ressurser

- [OpenHands-dokumentasjon](https://docs.openhands.dev/)
- [Oversikt over Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Oppsett av Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler og modellkonfigurasjon](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentasjon for Lemonade Server](https://lemonade-server.ai/docs)

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