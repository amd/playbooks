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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Översikt

[OpenHands](https://github.com/All-Hands-AI/OpenHands) är en AI-programvaruagent
som kan skriva kod, köra kommandon, surfa på webben och redigera filer i en riktig
arbetsyta. Istället för att kopiera förslag från ett chattfönster riktar du
agenten mot en projektmapp och låter den göra arbetet: implementera en funktion,
åtgärda en bugg, skriva tester eller förklara en kodbas.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) är det rekommenderade
webbläsargränssnittet för att köra OpenHands. Ett enda `agent-canvas`-kommando
startar agentservern, automationsbackend och webbfrontend tillsammans, så att
du kan föra en konversation med agenten från din webbläsare.

För att hålla allt på ditt AMD-system kommunicerar agenten med en lokal modell
som serveras av Lemonade Server. Lemonade exponerar den modellen via ett
OpenAI-kompatibelt API, så Agent Canvas kan konfigurera den som vilken annan
OpenAI-liknande slutpunkt som helst, samtidigt som modellen, din kod och
konversationskontexten stannar på din dator.

I den här handboken startar du en lokal modell, startar Agent Canvas, riktar
den mot den modellen och kör din första kodningsuppgift mot en riktig
projektmapp.

## Vad du kommer att lära dig

- Hur du startar Lemonade Server och bekräftar att en lokal modell svarar på chattförfrågningar
- Hur du installerar och startar Agent Canvas från npm-paketet
- Hur du konfigurerar Agent Canvas att använda en lokal Lemonade-modell som LLM
- Hur du startar en OpenHands-konversation och ser agenten redigera filer och köra
  kommandon i en arbetsyta
- Hur du granskar vad agenten ändrade och styr den med uppföljningsmeddelanden

## Centrala begrepp

| Begrepp | Vad det är | Var det passar in i den här handboken |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform byggd för AMD-hårdvara som exponerar ett OpenAI-kompatibelt API. Din data lämnar aldrig din dator. | Kör modellen som driver agenten. |
| OpenHands | En AI-programvaruagent som läser och redigerar filer, kör skalkommandon och surfar på webben inom en arbetsyta. | Agenten du styr från chatten. |
| Agent Canvas | Webbläsargränssnittet och backend som kör OpenHands-konversationer och visar verktygsanrop och filändringar. | Startar stacken och är värd för din konversation. |
| Arbetsyta | Projektmappen som agenten tillåts läsa och ändra. | Målet för agentens redigeringar och kommandon. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Kodningsagent-arbetsflöden gynnas av en större modell och ett större kontextfönster. Använd
> minst 32 GB systemminne, och föredra 64 GB eller mer för större GGUF-modeller.
<!-- @device:end -->

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Förutsättningar


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Du behöver:

- Lemonade Server installerat och kunna serva modellen nedan.

<!-- @os:linux -->
- Node.js 22.12 eller senare och `npm` (används av `agent-canvas`-CLI:et).
- `uv`, pakethanteraren för Python som Agent Canvas använder för att hantera
  agentserverns miljö. Om ditt system inte redan har det installerat, installera
  det från [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/)
  innan du startar Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop för Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installerat och körande. På Windows körs Agent Canvas-stacken från den
  publicerade Docker-avbildningen, som paketerar Node.js, `uv` och paketet
  `@openhands/agent-canvas`, så du behöver inte installera dessa på värden.
<!-- @os:end -->

- En projektmapp att arbeta i. Detta kan vara vilket lokalt git-repository eller
  vilken kodkatalog som helst som du vill att agenten ska arbeta med.

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

## 1. Starta Lemonade Server

Starta modellen från Lemonade-CLI:et:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Välj en modell som passar din hårdvara.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) är en stark kodningsmodell men kräver en stor minnespool. Om din enhet har begränsat minne eller GPU-VRAM, välj istället en mindre GGUF-modell från Lemonade-modellbiblioteket och använd det modell-ID:t genom hela denna handbok.

> **Obs:** Den första `lemonade run` laddar ner modellen om den inte redan finns, vilket kan ta ett tag beroende på modellens storlek och din anslutning.

Lemonade exponerar ett OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verifiera den lokala modellen

Bekräfta att Lemonade kan serva den valda modellen:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Skicka sedan en liten chattförfrågan:

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
## 3. Installera och starta Agent Canvas

<!-- @os:linux -->
Installera det publicerade Agent Canvas-paketet globalt:

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

Starta sedan hela stacken från en terminal:

```bash
agent-canvas
```

Som standard startar Agent Canvas på `http://localhost:8000`. Öppna den URL:en i
din webbläsare. Porten är inte speciell — om 8000 redan används, ange en ledig
port med `--port` (eller `-p`) när du startar Agent Canvas:

```bash
agent-canvas --port 3000
```

Öppna sedan `http://localhost:3000` istället. Standardbackend lokalt bör visas
som frisk (healthy) på startskärmen.

Kommandot `agent-canvas` startar agentservern, automationsbackenden och
webbgränssnittet tillsammans. Du behöver bara detta enda kommando för att köra
OpenHands lokalt.

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
På Windows kör du den publicerade Agent Canvas-containerbilden med Docker
Desktop. Bilden innehåller agentservern, automationsbackenden och
webbgränssnittet, så du behöver inte installera Node.js, `uv` eller CLI:t på
värden.

Skapa först de konfigurations- och arbetsytemappar som containern monterar:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Hämta den publicerade bilden (den är publik, så ingen inloggning krävs):

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

Öppna `http://localhost:8000/canvas` i din webbläsare. Om port 8000 redan
används, mappa en annan värdport, till exempel `-p 8080:8000`, och öppna
`http://localhost:8080/canvas` istället.

> **Obs:** Vid första starten initialiseras agentservern inuti containern,
> så det kan ta en minut eller två innan backenden rapporterar sig frisk.

Monteringen `.openhands` sparar din LLM-profil och dina inställningar mellan
omstarter av containern. Resten av denna guide konfigurerar allt genom
Agent Canvas-gränssnittet i din webbläsare.

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

## 4. Konfigurera den lokala LLM:en

Vid den första starten öppnar Agent Canvas ett introduktionsflöde. I det flödet:

1. Behåll **OpenHands** vald som agent och klicka på **Next**.
2. Under **Set up your LLM**, välj **Advanced**.
3. Behåll **Authentication** inställd på **API key**.
4. Ställ in **Custom Model** till `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ställ in **Base URL** till `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > På Windows körs stacken i en container, som inte kan nå värden på
   > `127.0.0.1`. Använd `http://host.docker.internal:13305/api/v1` istället
   > så att den containeriserade agenten kan nå Lemonade som körs på
   > Windows-värden.
   <!-- @os:end -->
6. För **API Key**, ange valfri icke-tom platshållare, till exempel
   `lemonade-local`. Lemonade kräver ingen riktig nyckel, men OpenHands-klienten
   behöver ett värde att skicka.
7. Klicka på **Next**.

De slutförda Advanced-inställningarna bör se ut så här. API-nyckelfältet
maskeras av gränssnittet.

![Agent Canvas första användningens LLM Advanced-inställningar med Lemonade-modellen och lokal bas-URL](assets/01-llm-advanced-settings.png)

Agent Canvas sparar dessa värden som en LLM-profil. Om din version ber dig
namnge den profilen, använd ett namn utan mellanslag, till exempel
`lemonade-local`. Om du byter modell senare, öppna **Settings > LLM** och
uppdatera samma Advanced-fält. Du kan växla mellan sparade profiler från
chattinmatningen med kommandot `/model`.

## 5. Öppna en arbetsyta

Agenten kan bara läsa och ändra filer inom en arbetsyta du väljer. Innan du
startar en uppgift, peka Agent Canvas mot din projektmapp:

1. Från startskärmen, välj **Open Workspace**.
2. Välj mappen som innehåller ditt projekt (till exempel ett git-arkiv som du
   vill att agenten ska arbeta på).
3. Starta en ny konversation i den arbetsytan.

Allt agenten gör—läser filer, kör kommandon, redigerar kod—är begränsat till
den arbetsytan.

![Agent Canvas startsida efter introduktionen](assets/02-agent-canvas-home.png)

## 6. Kör din första kodningsuppgift

Med arbetsytan öppen och den lokala LLM:en vald, skriv in en konkret uppgift i
chatten. En bra första uppgift är liten och verifierbar, till exempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observera konversationens tidslinje. OpenHands kommer att:

- Läsa arbetsytan för att förstå layouten.
- Skapa `hello.py` med den begärda funktionen och testblocket.
- Eventuellt köra `python3 hello.py` för att verifiera resultatet.
- Rapportera vad den gjorde och eventuell kommandoutdata i chatten.

Du bör se den nya filen dyka upp i arbetsytan, och agentens slutmeddelande bör
beskriva ändringen den gjorde. Detta är den avgörande stunden: agenten skrev
och körde riktig kod i din projektmapp.

## 7. Granska och styr agenten

När agenten har slutfört ett steg, granska dess arbete innan du godkänner
nästa steg:

- **Filändringar**: använd arbetsytans filbläddrare eller agentens diff-vy för
  att se exakt vad som lades till, ändrades eller togs bort.
- **Kommandoutdata**: expandera valfritt kommando som agenten körde för att se
  stdout, stderr och avslutningskoden.
- **Uppföljningar**: om resultatet inte blev som du ville, svara i samma
  konversation med en korrigering. Agenten behåller den tidigare kontexten och
  itererar på samma filer.

Om testet till exempel inte skrev ut den förväntade hälsningen, svara:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten läser filen igen, kör kommandot, diagnostiserar problemet och
redigerar filen på nytt—allt i samma konversation.
## Felsökning

<!-- @os:linux -->
- **`agent-canvas` finns inte i PATH:** installera om med
  `npm install -g @openhands/agent-canvas` och kontrollera att npms globala
  binärkatalog finns i din PATH innan `agent-canvas` kan startas från en ny
  terminal.
- **`npm install -g` misslyckas med ett behörighetsfel:** konfigurera en
  användarägd global npm-katalog, öppna sedan terminalen igen och installera
  Agent Canvas på nytt.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` saknas:** installera det från
  [installationsguiden för uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas använder `uv` för att hantera agentserverns Python-miljö.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` eller `docker run` misslyckas med att ansluta:** se till att
  Docker Desktop körs (dess valikon finns i systemfältet) och att motorn har
  startat klart. `docker version` bör visa både en Client- och en
  Server-sektion.
- **Containern startar men backenden blir aldrig hälsosam (healthy):** den
  första starten initierar Agent Server inuti containern; ge det en minut
  eller två och kontrollera sedan `docker logs <container>` för fel.
- **Containern kan inte nå Lemonade:** containern når värden via
  `host.docker.internal`. Kontrollera att Lemonade körs på Windows-värden med
  `lemonade status`, och använd `http://host.docker.internal:13305/api/v1` som
  Base URL när du konfigurerar LLM:en.
<!-- @os:end -->

- **Användargränssnittet laddas men backenden visas som osund:** vänta en
  minut eller två tills agentservern har startat klart och uppdatera sedan
  sidan. Om det förblir osunt, starta om stacken och kontrollera loggarna för
  fel.
- **Lemonade-chattförfrågningar misslyckas med ett anslutningsfel:**
  kontrollera att `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lyckas
  och att Lemonade fortfarande serverar modellen med `lemonade status`.
- **Agenten ger ett fel om kontextlängd eller tokengräns:** starta en ny
  konversation så att agenten inte bär med sig en alltför stor historik. Om
  det fortsätter att inträffa, starta om Lemonade med ett större `ctx_size` än
  standardvärdet 65536 (till exempel `ctx_size=131072`), om minnet tillåter.
- **Agenten producerar redigeringar av låg kvalitet eller ofullständiga
  redigeringar:** byt till en större modell i Lemonade, eller ge agenten en
  mindre, mer konkret uppgift och låt den bli klar innan du ber om nästa
  ändring.

## Nästa steg

- Prova en större uppgift i samma arbetsyta, till exempel att lägga till en
  enhetstestfil eller åtgärda en känd bugg, och granska agentens diff innan du
  behåller ändringen.
- Anslut en MCP-server som GitHub eller Slack under **Customize** så att
  agenten kan läsa ärenden eller publicera uppdateringar medan den arbetar.
- Spara flera LLM-profiler (en snabb liten modell och en kraftfullare stor
  modell) och växla mellan dem med `/model` mitt i en konversation.
- Gå vidare till [OpenHands-automatiseringar](https://docs.openhands.dev/openhands/usage/automations/overview) för att
  omvandla återkommande utvecklingsloopar till schemalagda eller
  händelseutlösta agentkörningar.

## Resurser

- [OpenHands-dokumentation](https://docs.openhands.dev/)
- [Översikt över Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Konfiguration av Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler och modellkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentation för Lemonade Server](https://lemonade-server.ai/docs)

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