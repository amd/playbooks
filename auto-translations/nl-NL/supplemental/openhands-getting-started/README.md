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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Overzicht

[OpenHands](https://github.com/All-Hands-AI/OpenHands) is een AI-softwareagent
die code kan schrijven, opdrachten kan uitvoeren, kan browsen op het web en
bestanden kan bewerken in een echte werkruimte. In plaats van suggesties uit
een chatvenster te kopiëren, wijs je de agent naar een projectmap en laat je
hem het werk doen: een functie implementeren, een bug oplossen, tests
schrijven of een codebase uitleggen.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is de aanbevolen
browser-UI voor het uitvoeren van OpenHands. Één `agent-canvas`-opdracht start
de agentserver, de automatiseringsback-end en de webfrontend samen, zodat je
een gesprek met de agent kunt voeren vanuit je browser.

Om alles op je AMD-systeem te houden, praat de agent met een lokaal model dat
wordt aangeboden door Lemonade Server. Lemonade stelt dat model beschikbaar
via een OpenAI-compatibele API, zodat Agent Canvas het kan configureren als
elk ander OpenAI-achtig eindpunt, terwijl het model, je code en de
gespreksinhoud allemaal op je machine blijven.

In deze playbook start je een lokaal model, start je Agent Canvas, wijs je het
naar dat model en voer je je eerste codeertaak uit op een echte projectmap.

## Wat je leert

- Hoe je Lemonade Server start en bevestigt dat een lokaal model chatverzoeken
  beantwoordt
- Hoe je Agent Canvas installeert en start vanuit het npm-pakket
- Hoe je Agent Canvas configureert om een lokaal Lemonade-model als LLM te
  gebruiken
- Hoe je een OpenHands-gesprek start en kijkt hoe de agent bestanden bewerkt en
  opdrachten uitvoert in een werkruimte
- Hoe je beoordeelt wat de agent heeft gewijzigd en hem stuurt met
  vervolgberichten

## Kernconcepten

| Concept | Wat het is | Waar het past in deze playbook |
| --- | --- | --- |
| Lemonade Server | Een lokaal LLM-platform gebouwd voor AMD-hardware dat een OpenAI-compatibele API beschikbaar stelt. Je gegevens verlaten je machine nooit. | Voert het model uit dat de agent aandrijft. |
| OpenHands | Een AI-softwareagent die bestanden leest en bewerkt, shellopdrachten uitvoert en op het web browst binnen een werkruimte. | De agent die je aanstuurt vanuit de chat. |
| Agent Canvas | De browser-UI en back-end die OpenHands-gesprekken uitvoert en tool-aanroepen en bestandswijzigingen toont. | Start de stack en host je gesprek. |
| Werkruimte | De projectmap die de agent mag lezen en wijzigen. | Het doel van de bewerkingen en opdrachten van de agent. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Coderingsagent-workflows profiteren van een groter model en contextvenster.
> Gebruik minstens 32 GB systeemgeheugen en geef de voorkeur aan 64 GB of meer
> voor grotere GGUF-modellen.
<!-- @device:end -->

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Vereisten


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Je hebt nodig:

- Lemonade Server geïnstalleerd en in staat om het onderstaande model te
  serveren.

<!-- @os:linux -->
- Node.js 22.12 of later en `npm` (gebruikt door de `agent-canvas`-CLI).
- `uv`, de Python-pakketbeheerder die Agent Canvas gebruikt om de omgeving van
  de agentserver te beheren. Als je systeem dit nog niet heeft, installeer het
  dan vanuit de
  [uv-installatiehandleiding](https://docs.astral.sh/uv/getting-started/installation/)
  voordat je Agent Canvas start.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop voor Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  geïnstalleerd en actief. Op Windows draait de Agent Canvas-stack vanuit de
  gepubliceerde Docker-image, die Node.js, `uv` en het
  `@openhands/agent-canvas`-pakket bundelt, zodat je die niet op de host hoeft
  te installeren.
<!-- @os:end -->

- Een projectmap om in te werken. Dit kan elke lokale git-repository of
  codemap zijn waaraan je de agent wilt laten werken.

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

## 1. Lemonade Server starten

Start het model vanuit de Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Kies een model dat past bij je hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) is een sterk codeermodel maar heeft een grote geheugenpool nodig. Als je apparaat beperkt geheugen of GPU-VRAM heeft, kies dan in plaats daarvan een kleiner GGUF-model uit de Lemonade-modelbibliotheek en gebruik die model-ID doorheen deze playbook.

> **Opmerking:** De eerste `lemonade run` downloadt het model als het nog niet aanwezig is, wat een tijdje kan duren afhankelijk van de modelgrootte en je verbinding.

Lemonade stelt een OpenAI-compatibele API beschikbaar op:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Het lokale model verifiëren

Bevestig dat Lemonade het geselecteerde model kan serveren:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Stuur vervolgens een klein chatverzoek:

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
## 3. Agent Canvas installeren en starten

<!-- @os:linux -->
Installeer het gepubliceerde Agent Canvas-pakket globaal:

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

Start vervolgens de volledige stack vanuit een terminal:

```bash
agent-canvas
```

Standaard start Agent Canvas op `http://localhost:8000`. Open die URL in
uw browser. De poort is niet bijzonder — als 8000 al in gebruik is, geeft u
elke vrije poort op met `--port` (of `-p`) wanneer u Agent Canvas start:

```bash
agent-canvas --port 3000
```

Open daarna `http://localhost:3000` in plaats daarvan. De standaard lokale backend zou
als gezond moeten worden weergegeven op het startscherm.

Het `agent-canvas`-commando start de agentserver, de automatiseringsbackend en
de webfrontend samen. U hebt alleen dit ene commando nodig om OpenHands
lokaal uit te voeren.

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
Voer op Windows de gepubliceerde Agent Canvas-containerimage uit met Docker Desktop.
De image bundelt de Agent Server, de automatiseringsbackend en de webfrontend, dus u
hoeft Node.js, `uv` of de CLI niet op de host te installeren.

Maak eerst de config- en werkruimtemappen aan die de container koppelt:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Haal de gepubliceerde image op (deze is openbaar, dus er is geen aanmelding vereist):

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

Open `http://localhost:8000/canvas` in uw browser. Als poort 8000 al in
gebruik is, koppel dan een andere hostpoort, bijvoorbeeld `-p 8080:8000`, en open
`http://localhost:8080/canvas` in plaats daarvan.

> **Opmerking:** Bij de eerste keer starten wordt de Agent Server binnen de container geïnitialiseerd,
> dus het kan een minuut of twee duren voordat de backend als gezond wordt gerapporteerd.

De `.openhands`-koppeling behoudt uw LLM-profiel en instellingen tussen herstarts van de container.
De rest van dit playbook configureert alles via de Agent
Canvas-UI in uw browser.

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

## 4. Het lokale LLM configureren

Bij de eerste keer starten opent Agent Canvas een onboardingflow. In die flow:

1. Houd **OpenHands** geselecteerd als de agent en klik op **Next**.
2. Selecteer bij **Set up your LLM** de optie **Advanced**.
3. Houd **Authentication** ingesteld op **API key**.
4. Stel **Custom Model** in op `openai/Qwen3.6-35B-A3B-GGUF`.
5. Stel **Base URL** in op `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Op Windows draait de stack in een container, die de host niet kan bereiken op
   > `127.0.0.1`. Gebruik in plaats daarvan `http://host.docker.internal:13305/api/v1` zodat de
   > gecontaineriseerde agent Lemonade kan bereiken die op de Windows-host draait.
   <!-- @os:end -->
6. Voer bij **API Key** een niet-lege plaatshouder in, zoals `lemonade-local`.
   Lemonade vereist geen echte sleutel, maar de OpenHands-client heeft wel een waarde nodig
   om te verzenden.
7. Klik op **Next**.

De voltooide Advanced-instellingen zouden er als volgt uit moeten zien. Het veld voor de API-sleutel is
gemaskeerd door de UI.

![Agent Canvas eerste-gebruik LLM Advanced-instellingen met het Lemonade-model en de lokale basis-URL](assets/01-llm-advanced-settings.png)

Agent Canvas slaat deze waarden op als een LLM-profiel. Als uw versie vraagt om dat profiel
te benoemen, gebruik dan een naam zonder spaties, zoals `lemonade-local`. Als u later van
model wisselt, open dan **Settings > LLM** en werk dezelfde Advanced-velden bij. U
kunt opgeslagen profielen wisselen vanuit het chatinvoerveld met het `/model`-commando.

## 5. Een werkruimte openen

De agent kan alleen bestanden lezen en wijzigen binnen een werkruimte die u kiest. Voordat u
een taak start, wijst u Agent Canvas naar uw projectmap:

1. Kies **Open Workspace** vanaf het startscherm.
2. Selecteer de map die uw project bevat (bijvoorbeeld een git-repository
   waaraan u de agent wilt laten werken).
3. Start een nieuwe conversatie in die werkruimte.

Alles wat de agent doet—bestanden lezen, commando's uitvoeren, code bewerken—is
beperkt tot die werkruimte.

![Agent Canvas-startscherm na onboarding](assets/02-agent-canvas-home.png)

## 6. Uw eerste codeertaak uitvoeren

Met de werkruimte geopend en het lokale LLM geselecteerd, typt u een concrete taak in
de chat. Een goede eerste taak is klein en verifieerbaar, bijvoorbeeld:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Bekijk de tijdlijn van de conversatie. OpenHands zal:

- De werkruimte lezen om de indeling te begrijpen.
- `hello.py` aanmaken met de gevraagde functie en testblok.
- Optioneel `python3 hello.py` uitvoeren om de uitvoer te verifiëren.
- Rapporteren wat het heeft gedaan en eventuele commando-uitvoer in de chat.

U zou het nieuwe bestand in de werkruimte moeten zien verschijnen, en het laatste bericht van de agent
zou de wijziging die het heeft aangebracht moeten beschrijven. Dit is het beloningsmoment: de
agent heeft echte code geschreven en uitgevoerd in uw projectmap.

## 7. De agent beoordelen en bijsturen

Nadat de agent een stap heeft voltooid, beoordeelt u het werk voordat u de volgende stap accepteert:

- **Bestandswijzigingen**: gebruik de bestandsverkenner van de werkruimte of de diff-weergave van de agent om
  precies te zien wat er is toegevoegd, gewijzigd of verwijderd.
- **Commando-uitvoer**: vouw een commando dat de agent heeft uitgevoerd uit om stdout, stderr,
  en de exitcode te zien.
- **Vervolgstappen**: als het resultaat niet is wat u wilde, reageert u in dezelfde
  conversatie met een correctie. De agent behoudt de eerdere context en
  itereert verder op dezelfde bestanden.

Als de test bijvoorbeeld niet de verwachte begroeting afdrukte, antwoordt u:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

De agent zal het bestand opnieuw lezen, het commando uitvoeren, het probleem diagnosticeren en
het bestand opnieuw bewerken—allemaal in dezelfde conversatie.
## Probleemoplossing

<!-- @os:linux -->
- **`agent-canvas` staat niet in PATH:** installeer opnieuw met
  `npm install -g @openhands/agent-canvas` en controleer of de globale npm-binaire
  map zich in uw PATH bevindt voordat `agent-canvas` vanuit een nieuwe
  terminal kan worden gestart.
- **`npm install -g` mislukt met een machtigingsfout:** configureer een globale
  npm-map die eigendom is van de gebruiker, open daarna de terminal opnieuw en installeer Agent Canvas nogmaals.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` ontbreekt:** installeer het via
  [de uv-installatiehandleiding](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas gebruikt `uv` om de Python-omgeving van de agent-server te beheren.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` of `docker run` kan geen verbinding maken:** zorg ervoor dat Docker Desktop
  actief is (het walvispictogram staat in het systeemvak) en dat de engine
  klaar is met opstarten. `docker version` moet zowel een Client- als een Server-
  sectie weergeven.
- **De container start, maar de backend wordt nooit gezond:** bij de eerste
  start wordt de Agent Server binnen de container geïnitialiseerd; geef dit een minuut of
  twee de tijd en controleer vervolgens `docker logs <container>` op fouten.
- **De container kan Lemonade niet bereiken:** de container bereikt de host via
  `host.docker.internal`. Controleer of Lemonade actief is op de Windows-host met
  `lemonade status`, en gebruik `http://host.docker.internal:13305/api/v1` als de
  Base URL bij het configureren van de LLM.
<!-- @os:end -->

- **De UI laadt, maar de backend geeft aan ongezond te zijn:** wacht een minuut of twee tot
  de agent-server klaar is met opstarten en ververs dan de pagina. Als het ongezond blijft, herstart
  de stack en controleer de logs op fouten.
- **Lemonade-chatverzoeken mislukken met een verbindingsfout:** controleer of
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` slaagt en dat
  Lemonade het model nog steeds aanbiedt met `lemonade status`.
- **De agent geeft een foutmelding over contextlengte of tokenlimiet:** start een
  nieuw gesprek zodat de agent geen te grote geschiedenis meesleept. Als dit
  blijft gebeuren, herstart Lemonade met een grotere `ctx_size` dan de standaard
  65536 (bijvoorbeeld `ctx_size=131072`), als het geheugen dit toelaat.
- **De agent produceert bewerkingen van lage kwaliteit of onvolledige bewerkingen:** schakel over naar een groter
  model in Lemonade, of geef de agent een kleinere, concretere taak en laat deze
  afronden voordat u om de volgende wijziging vraagt.

## Volgende stappen

- Probeer een grotere taak in dezelfde werkruimte, zoals het toevoegen van een unit-testbestand of
  het oplossen van een bekende bug, en bekijk de diff van de agent voordat u de wijziging behoudt.
- Verbind een MCP-server zoals GitHub of Slack onder **Aanpassen** zodat de
  agent issues kan lezen of updates kan plaatsen terwijl deze werkt.
- Sla meerdere LLM-profielen op (een snel klein model en een sterker groot model) en
  wissel ertussen met `/model` tijdens een gesprek.
- Ga verder met [OpenHands-automatiseringen](https://docs.openhands.dev/openhands/usage/automations/overview) om
  terugkerende ontwikkellussen om te zetten in geplande of gebeurtenisgestuurde agent-runs.

## Bronnen

- [OpenHands-documentatie](https://docs.openhands.dev/)
- [Overzicht van Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Instellen van Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profielen en modelconfiguratie](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentatie van Lemonade Server](https://lemonade-server.ai/docs)

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