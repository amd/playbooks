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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversigt

[OpenHands](https://github.com/All-Hands-AI/OpenHands) er en AI-softwareagent,
der kan skrive kode, køre kommandoer, browse på nettet og redigere filer i et
rigtigt arbejdsområde. I stedet for at kopiere forslag fra et chatvindue
peger du agenten mod en projektmappe og lader den udføre arbejdet: implementere
en funktion, rette en fejl, skrive tests eller forklare en kodebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er den anbefalede
browser-UI til at køre OpenHands. En enkelt `agent-canvas`-kommando starter
agentserveren, automatiseringsbackenden og webfrontenden sammen, så du kan
føre en samtale med agenten fra din browser.

For at holde alt på dit AMD-system taler agenten med en lokal model, der
serveres af Lemonade Server. Lemonade eksponerer denne model via en
OpenAI-kompatibel API, så Agent Canvas kan konfigurere den som alle andre
OpenAI-lignende endpoints, mens modellen, din kode og samtalekonteksten alle
forbliver på din maskine.

I denne playbook starter du en lokal model, lancerer Agent Canvas, peger den
mod denne model og kører din første kodningsopgave mod en rigtig
projektmappe.

## Hvad du vil lære

- Hvordan du starter Lemonade Server og bekræfter, at en lokal model svarer på
  chatforespørgsler
- Hvordan du installerer og starter Agent Canvas fra npm-pakken
- Hvordan du konfigurerer Agent Canvas til at bruge en lokal Lemonade-model som
  LLM
- Hvordan du starter en OpenHands-samtale og følger med i, mens agenten
  redigerer filer og kører kommandoer i et arbejdsområde
- Hvordan du gennemgår, hvad agenten har ændret, og styrer den med
  opfølgende beskeder

## Centrale begreber

| Begreb | Hvad det er | Hvor det passer ind i denne playbook |
| --- | --- | --- |
| Lemonade Server | En platform til lokal LLM-servering bygget til AMD-hardware, der eksponerer en OpenAI-kompatibel API. Dine data forlader aldrig din maskine. | Kører den model, der driver agenten. |
| OpenHands | En AI-softwareagent, der læser og redigerer filer, kører shell-kommandoer og browser på nettet inde i et arbejdsområde. | Agenten, du styrer fra chatten. |
| Agent Canvas | Browser-UI'et og backenden, der kører OpenHands-samtaler og viser værktøjskald og filændringer. | Starter stakken og er vært for din samtale. |
| Arbejdsområde | Projektmappen, som agenten har tilladelse til at læse og ændre. | Målet for agentens redigeringer og kommandoer. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Workflows med kodningsagenter har gavn af en større model og et større
> kontekstvindue. Brug mindst 32 GB systemhukommelse, og foretræk 64 GB eller
> mere til større GGUF-modeller.
<!-- @device:end -->

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Forudsætninger


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

Du skal bruge:

- Lemonade Server installeret og i stand til at servere modellen nedenfor.

<!-- @os:linux -->
- Node.js 22.12 eller nyere og `npm` (bruges af `agent-canvas`-CLI'en).
- `uv`, Python-pakkehåndteringen, som Agent Canvas bruger til at administrere
  agentserverens miljø. Hvis dit system ikke allerede har det, så installer
  det fra [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/)
  før du starter Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop til Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installeret og kørende. På Windows kører Agent Canvas-stakken fra det
  udgivne Docker-image, som indeholder Node.js, `uv` og
  `@openhands/agent-canvas`-pakken, så du behøver ikke installere disse på
  værtsmaskinen.
<!-- @os:end -->

- En projektmappe at arbejde i. Dette kan være et hvilket som helst lokalt
  git-repository eller kodemappe, du vil have agenten til at arbejde på.

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

Start modellen fra Lemonade CLI'en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Vælg en model, der passer til din hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) er en stærk kodningsmodel, men kræver en stor hukommelsespulje. Hvis din enhed har begrænset hukommelse eller GPU-VRAM, så vælg i stedet en mindre GGUF-model fra Lemonade-modelbiblioteket, og brug det model-ID i hele denne playbook.

> **Bemærk:** Den første `lemonade run` downloader modellen, hvis den ikke allerede findes, hvilket kan tage et stykke tid afhængigt af modelstørrelsen og din forbindelse.

Lemonade eksponerer en OpenAI-kompatibel API på:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Bekræft den lokale model

Bekræft, at Lemonade kan servere den valgte model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Send derefter en lille chatforespørgsel:

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
Installer den udgivne Agent Canvas-pakke globalt:

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

Start derefter hele stakken fra en terminal:

```bash
agent-canvas
```

Som standard starter Agent Canvas på `http://localhost:8000`. Åbn denne URL i
din browser. Porten er ikke speciel — hvis 8000 allerede er i brug, kan du angive
en ledig port med `--port` (eller `-p`), når du starter Agent Canvas:

```bash
agent-canvas --port 3000
```

Åbn derefter `http://localhost:3000` i stedet. Den lokale standardbackend bør
vises som sund på startskærmen.

Kommandoen `agent-canvas` starter agentserveren, automationsbackenden og
webfrontenden sammen. Du behøver kun denne ene kommando for at køre OpenHands
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
På Windows skal du køre det udgivne Agent Canvas-containerbillede med Docker Desktop.
Billedet indeholder Agent Server, automationsbackend og webfrontend, så du
behøver ikke at installere Node.js, `uv` eller CLI'en på værten.

Opret først de konfigurations- og arbejdsområdemapper, som containeren monterer:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hent det udgivne billede (det er offentligt, så der kræves ikke login):

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

Åbn `http://localhost:8000/canvas` i din browser. Hvis port 8000 allerede er i
brug, så mapper du en anden værtsport, for eksempel `-p 8080:8000`, og åbner
`http://localhost:8080/canvas` i stedet.

> **Bemærk:** Den første opstart initialiserer Agent Server inde i containeren,
> så det kan tage et minut eller to, før backenden rapporteres som sund.

`.openhands`-monteringen gemmer din LLM-profil og indstillinger på tværs af
genstarter af containeren. Resten af denne guide konfigurerer alt gennem Agent
Canvas-brugergrænsefladen i din browser.

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

## 4. Konfigurer den lokale LLM

Ved første opstart åbner Agent Canvas et onboarding-forløb. I dette forløb:

1. Behold **OpenHands** valgt som agent, og klik på **Next**.
2. Under **Set up your LLM**, vælg **Advanced**.
3. Behold **Authentication** sat til **API key**.
4. Sæt **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sæt **Base URL** til `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > På Windows kører stakken i en container, som ikke kan nå værten på
   > `127.0.0.1`. Brug i stedet `http://host.docker.internal:13305/api/v1`, så
   > den containeriserede agent kan nå Lemonade, der kører på Windows-værten.
   <!-- @os:end -->
6. For **API Key** skal du indtaste en vilkårlig ikke-tom pladsholder, f.eks.
   `lemonade-local`. Lemonade kræver ikke en rigtig nøgle, men OpenHands-klienten
   skal bruge en værdi at sende.
7. Klik på **Next**.

De udfyldte Advanced-indstillinger bør se sådan ud. API-nøglefeltet er
maskeret af brugergrænsefladen.

![Agent Canvas førstegangsindstillinger for LLM Advanced med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Agent Canvas gemmer disse værdier som en LLM-profil. Hvis din version beder dig
navngive denne profil, så brug et navn uden mellemrum, f.eks. `lemonade-local`.
Hvis du senere skifter model, skal du åbne **Settings > LLM** og opdatere de
samme Advanced-felter. Du kan skifte mellem gemte profiler fra chatinputtet med
kommandoen `/model`.

## 5. Åbn et arbejdsområde

Agenten kan kun læse og ændre filer inde i et arbejdsområde, du vælger. Før du
starter en opgave, skal du pege Agent Canvas mod din projektmappe:

1. Vælg **Open Workspace** fra startskærmen.
2. Vælg den mappe, der indeholder dit projekt (for eksempel et git-repository,
   du vil have agenten til at arbejde på).
3. Start en ny samtale i dette arbejdsområde.

Alt, hvad agenten gør — læse filer, køre kommandoer, redigere kode — er
afgrænset til dette arbejdsområde.

![Agent Canvas-startskærm efter onboarding](assets/02-agent-canvas-home.png)

## 6. Kør din første kodeopgave

Med arbejdsområdet åbent og den lokale LLM valgt, skal du skrive en konkret
opgave i chatten. En god første opgave er lille og verificerbar, for eksempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Følg samtaletidslinjen. OpenHands vil:

- Læse arbejdsområdet for at forstå opbygningen.
- Oprette `hello.py` med den ønskede funktion og testblok.
- Eventuelt køre `python3 hello.py` for at verificere output.
- Rapportere hvad den gjorde, og eventuelt kommandooutput i chatten.

Du bør se den nye fil dukke op i arbejdsområdet, og agentens afsluttende
besked bør beskrive den ændring, den har lavet. Dette er det afgørende
øjeblik: agenten skrev og kørte rigtig kode i din projektmappe.

## 7. Gennemgå og styr agenten

Når agenten har afsluttet et trin, skal du gennemgå dens arbejde, før du
accepterer det næste:

- **Filændringer**: brug arbejdsområdets filbrowser eller agentens diff-visning
  til at se præcis, hvad der blev tilføjet, ændret eller slettet.
- **Kommandooutput**: udvid enhver kommando, agenten har kørt, for at se
  stdout, stderr og afslutningskoden.
- **Opfølgning**: hvis resultatet ikke er det, du ønskede, så svar i samme
  samtale med en rettelse. Agenten bevarer den tidligere kontekst og
  gentager processen på de samme filer.

Hvis testen for eksempel ikke udskrev den forventede hilsen, så svar:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten vil genlæse filen, køre kommandoen, diagnosticere problemet og
redigere filen igen — alt sammen i den samme samtale.
## Fejlfinding

<!-- @os:linux -->
- **`agent-canvas` er ikke på PATH:** geninstaller med
  `npm install -g @openhands/agent-canvas` og bekræft, at npm's globale binær-mappe
  er på din PATH, før `agent-canvas` kan startes fra en ny
  terminal.
- **`npm install -g` fejler med en tilladelsesfejl:** konfigurer en brugerejet
  global npm-mappe, og genåbn derefter terminalen og installer Agent Canvas igen.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` mangler:** installer det fra
  [installationsvejledningen til uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas bruger `uv` til at administrere agent-serverens Python-miljø.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` eller `docker run` kan ikke oprette forbindelse:** sørg for, at Docker Desktop
  kører (dets hvalikon findes i systembakken), og at motoren er
  færdig med at starte. `docker version` bør udskrive både en Client- og en Server-
  sektion.
- **Containeren starter, men backenden bliver aldrig sund (healthy):** den første
  opstart initialiserer Agent Server inde i containeren; giv den et minut eller
  to, og tjek derefter `docker logs <container>` for fejl.
- **Containeren kan ikke nå Lemonade:** containeren når værten via
  `host.docker.internal`. Bekræft, at Lemonade betjener på Windows-værten med
  `lemonade status`, og brug `http://host.docker.internal:13305/api/v1` som
  Base URL, når LLM'en konfigureres.
<!-- @os:end -->

- **UI'en indlæses, men backenden viser usund (unhealthy):** vent et minut eller to, mens
  agent-serveren bliver færdig med at starte, og opdater derefter. Hvis den forbliver usund,
  genstart stakken, og tjek logfilerne for fejl.
- **Lemonade-chatanmodninger fejler med en forbindelsesfejl:** bekræft, at
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lykkes, og at
  Lemonade stadig betjener modellen med `lemonade status`.
- **Agenten fejler med en besked om kontekstlængde eller tokengrænse:** start en
  ny samtale, så agenten ikke medbringer en for stor historik. Hvis det
  fortsætter med at ske, genstart Lemonade med en større `ctx_size` end standarden på
  65536 (for eksempel `ctx_size=131072`), hvis hukommelsen tillader det.
- **Agenten producerer redigeringer af lav kvalitet eller ufuldstændige redigeringer:** skift til en større
  model i Lemonade, eller giv agenten en mindre, mere konkret opgave, og lad den
  blive færdig, før du beder om den næste ændring.

## Næste trin

- Prøv en større opgave i det samme workspace, såsom at tilføje en unit test-fil eller
  rette en kendt fejl, og gennemgå agentens diff, før du beholder ændringen.
- Forbind en MCP-server som GitHub eller Slack under **Customize**, så
  agenten kan læse issues eller poste opdateringer, mens den arbejder.
- Gem flere LLM-profiler (en hurtig lille model og en stærkere stor model), og
  skift mellem dem med `/model` midt i en samtale.
- Fortsæt til [OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) for at
  omdanne tilbagevendende udviklingsløkker til planlagte eller hændelsesudløste agentkørsler.

## Ressourcer

- [OpenHands-dokumentation](https://docs.openhands.dev/)
- [Oversigt over Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Opsætning af Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler og modelkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)

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