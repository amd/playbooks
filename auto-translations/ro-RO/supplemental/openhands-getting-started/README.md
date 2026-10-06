<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prezentare generală

[OpenHands](https://github.com/All-Hands-AI/OpenHands) este un agent software bazat pe AI
care poate scrie cod, rula comenzi, naviga pe web și edita fișiere într-un
spațiu de lucru real. În loc să copiați sugestii dintr-o fereastră de chat,
îndreptați agentul către un folder de proiect și îl lăsați să facă munca:
implementați o funcționalitate, remediați o eroare, scrieți teste sau explicați
o bază de cod.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) este interfața de
browser recomandată pentru rularea OpenHands. O singură comandă `agent-canvas`
pornește serverul agentului, backend-ul de automatizare și frontend-ul web
împreună, astfel încât puteți purta o conversație cu agentul din browser.

Pentru a păstra totul pe sistemul dvs. AMD, agentul comunică cu un model local
servit de Lemonade Server. Lemonade expune acel model printr-un API compatibil
cu OpenAI, astfel încât Agent Canvas îl poate configura ca pe orice alt
endpoint de tip OpenAI, în timp ce modelul, codul dvs. și contextul
conversației rămân toate pe mașina dvs.

În acest ghid, veți porni un model local, veți lansa Agent Canvas, îl veți
îndrepta către acel model și veți rula prima sarcină de programare asupra unui
folder de proiect real.

## Ce veți învăța

- Cum să porniți Lemonade Server și să confirmați că un model local răspunde la
  cereri de chat
- Cum să instalați și să lansați Agent Canvas din pachetul npm
- Cum să configurați Agent Canvas pentru a utiliza un model Lemonade local ca
  LLM
- Cum să porniți o conversație OpenHands și să urmăriți agentul editând
  fișiere și rulând comenzi într-un spațiu de lucru
- Cum să revizuiți ce a modificat agentul și să îl ghidați cu mesaje
  ulterioare

## Concepte de bază

| Concept | Ce este | Unde se încadrează în acest ghid |
| --- | --- | --- |
| Lemonade Server | O platformă locală de servire LLM construită pentru hardware AMD, care expune un API compatibil cu OpenAI. Datele dvs. nu părăsesc niciodată mașina dvs. | Rulează modelul care alimentează agentul. |
| OpenHands | Un agent software bazat pe AI care citește și editează fișiere, rulează comenzi shell și navighează pe web în interiorul unui spațiu de lucru. | Agentul pe care îl conduceți din chat. |
| Agent Canvas | Interfața de browser și backend-ul care rulează conversațiile OpenHands și afișează apelurile de instrumente și modificările de fișiere. | Lansează stiva și găzduiește conversația dvs. |
| Spațiu de lucru | Folderul de proiect pe care agentul este autorizat să îl citească și să îl modifice. | Ținta editărilor și comenzilor agentului. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Fluxurile de lucru ale agenților de programare beneficiază de un model mai
> mare și de o fereastră de context mai mare. Utilizați cel puțin 32 GB de
> memorie de sistem și preferați 64 GB sau mai mult pentru modele GGUF mai
> mari.
<!-- @device:end -->

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările de software

<!-- @require:software-update -->
<!-- @device:end -->

## Cerințe preliminare


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

Aveți nevoie de:

- Lemonade Server instalat și capabil să servească modelul de mai jos.

<!-- @os:linux -->
- Node.js 22.12 sau o versiune ulterioară și `npm` (utilizate de CLI-ul
  `agent-canvas`).
- `uv`, managerul de pachete Python pe care Agent Canvas îl utilizează pentru a
  gestiona mediul serverului agentului. Dacă sistemul dvs. nu îl are deja,
  instalați-l din
  [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/)
  înainte de a lansa Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instalat și în execuție. Pe Windows, stiva Agent Canvas rulează din imaginea
  Docker publicată, care include Node.js, `uv` și pachetul
  `@openhands/agent-canvas`, astfel încât nu este necesar să le instalați pe
  gazdă.
<!-- @os:end -->

- Un folder de proiect în care să lucrați. Acesta poate fi orice depozit git
  local sau director de cod pe care doriți ca agentul să lucreze.

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

## 1. Porniți Lemonade Server

Porniți modelul din CLI-ul Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Alegeți un model potrivit pentru hardware-ul dvs.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) este un model de programare puternic, dar necesită un pool mare de memorie. Dacă dispozitivul dvs. are memorie sau VRAM GPU limitată, alegeți în schimb un model GGUF mai mic din biblioteca de modele Lemonade și utilizați acel ID de model pe tot parcursul acestui ghid.

> **Notă:** Prima rulare `lemonade run` descarcă modelul dacă nu este deja prezent, ceea ce poate dura o perioadă în funcție de dimensiunea modelului și de conexiunea dvs.

Lemonade expune un API compatibil cu OpenAI la:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verificați modelul local

Confirmați că Lemonade poate servi modelul selectat:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Apoi trimiteți o cerere mică de chat:

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

Dacă aceasta returnează un array `choices`, Lemonade este pregătit pentru Agent Canvas.

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
## 3. Instalați și lansați Agent Canvas

<!-- @os:linux -->
Instalați global pachetul publicat Agent Canvas:

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

Apoi porniți întreaga stivă dintr-un terminal:

```bash
agent-canvas
```

În mod implicit, Agent Canvas pornește pe `http://localhost:8000`. Deschideți acest URL în
browserul dvs. Portul nu are nimic special — dacă 8000 este deja în uz, specificați orice
port liber cu `--port` (sau `-p`) atunci când lansați Agent Canvas:

```bash
agent-canvas --port 3000
```

Apoi deschideți `http://localhost:3000` în loc. Backend-ul local implicit ar trebui să apară
ca fiind sănătos pe ecranul de start.

Comanda `agent-canvas` pornește împreună serverul de agent, backend-ul de automatizare și
frontend-ul web. Aveți nevoie doar de această singură comandă pentru a rula OpenHands
local.

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
Pe Windows, rulați imaginea de container Agent Canvas publicată cu Docker Desktop.
Imaginea include serverul Agent Server, backend-ul de automatizare și frontend-ul web, astfel
nu trebuie să instalați Node.js, `uv` sau CLI-ul pe gazdă.

Mai întâi, creați folderele de configurare și de spațiu de lucru pe care le montează containerul:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Descărcați imaginea publicată (este publică, deci nu este necesară autentificare):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Apoi porniți stiva:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Deschideți `http://localhost:8000/canvas` în browserul dvs. Dacă portul 8000 este deja
în uz, mapați un alt port pe gazdă, de exemplu `-p 8080:8000`, și deschideți
`http://localhost:8080/canvas` în loc.

> **Notă:** Prima lansare inițializează Agent Server-ul în interiorul containerului,
> astfel poate dura un minut sau două înainte ca backend-ul să raporteze starea de sănătate.

Montarea `.openhands` persistă profilul LLM și setările dvs. între reporniri de container
restarturi. Restul acestui ghid configurează totul prin interfața Agent
Canvas în browserul dvs.

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

## 4. Configurați LLM-ul local

La prima lansare, Agent Canvas deschide un flux de integrare inițială. În acest flux:

1. Păstrați **OpenHands** selectat ca agent și faceți clic pe **Next**.
2. La **Set up your LLM**, selectați **Advanced**.
3. Păstrați **Authentication** setat la **API key**.
4. Setați **Custom Model** la `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setați **Base URL** la `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Pe Windows stiva rulează într-un container, care nu poate accesa gazda la
   > `127.0.0.1`. Folosiți în schimb `http://host.docker.internal:13305/api/v1` pentru ca
   > agentul containerizat să poată accesa Lemonade care rulează pe gazda Windows.
   <!-- @os:end -->
6. Pentru **API Key**, introduceți orice valoare de rezervare ne-goală, cum ar fi `lemonade-local`.
   Lemonade nu necesită o cheie reală, dar clientul OpenHands are nevoie de o valoare
   de trimis.
7. Faceți clic pe **Next**.

Setările Advanced completate ar trebui să arate astfel. Câmpul pentru cheia API este
mascat de interfață.

![Setări Agent Canvas Advanced LLM la prima utilizare cu modelul Lemonade și URL-ul de bază local](assets/01-llm-advanced-settings.png)

Agent Canvas salvează aceste valori ca profil LLM. Dacă versiunea dvs. vă cere să
denumiți acel profil, folosiți un nume fără spații, cum ar fi `lemonade-local`. Dacă schimbați
modelele mai târziu, deschideți **Settings > LLM** și actualizați aceleași câmpuri Advanced. Puteți
comuta între profilurile salvate din câmpul de chat cu comanda `/model`.

## 5. Deschideți un spațiu de lucru

Agentul poate citi și modifica doar fișiere din interiorul unui spațiu de lucru pe care îl alegeți. Înainte
de a începe o sarcină, direcționați Agent Canvas către folderul proiectului dvs.:

1. Din ecranul de start, alegeți **Open Workspace**.
2. Selectați folderul care conține proiectul dvs. (de exemplu, un depozit git
   pe care doriți ca agentul să lucreze).
3. Începeți o nouă conversație în acel spațiu de lucru.

Tot ce face agentul—citirea fișierelor, rularea comenzilor, editarea codului—este
limitat la acel spațiu de lucru.

![Pagina de start Agent Canvas după integrarea inițială](assets/02-agent-canvas-home.png)

## 6. Rulați prima dvs. sarcină de programare

Cu spațiul de lucru deschis și LLM-ul local selectat, introduceți o sarcină concretă în
chat. O primă sarcină bună este mică și verificabilă, de exemplu:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Urmăriți cronologia conversației. OpenHands va:

- Citi spațiul de lucru pentru a înțelege structura.
- Crea `hello.py` cu funcția solicitată și blocul de test.
- Opțional, rula `python3 hello.py` pentru a verifica rezultatul.
- Raporta ce a făcut și orice rezultat de comandă în chat.

Ar trebui să vedeți noul fișier apărând în spațiul de lucru, iar mesajul final al agentului
ar trebui să descrie schimbarea pe care a făcut-o. Acesta este momentul de reușită: agentul
a scris și a rulat cod real în folderul proiectului dvs.

## 7. Revizuiți și direcționați agentul

După ce agentul termină un pas, revizuiți munca sa înainte de a accepta pasul următor:

- **Modificări de fișiere**: folosiți browserul de fișiere al spațiului de lucru sau vizualizarea diff a agentului pentru
  a vedea exact ce a fost adăugat, modificat sau șters.
- **Rezultat comandă**: extindeți orice comandă rulată de agent pentru a vedea stdout, stderr
  și codul de ieșire.
- **Continuări**: dacă rezultatul nu este cel dorit, răspundeți în aceeași
  conversație cu o corecție. Agentul păstrează contextul anterior și
  iterează pe aceleași fișiere.

De exemplu, dacă testul nu a afișat salutul așteptat, răspundeți:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agentul va reciti fișierul, va rula comanda, va diagnostica problema și va edita
din nou fișierul—toate în aceeași conversație.
## Depanare

<!-- @os:linux -->
- **`agent-canvas` nu se află în PATH:** reinstalați cu
  `npm install -g @openhands/agent-canvas` și confirmați că directorul binar
  global npm se află în PATH înainte ca `agent-canvas` să poată fi lansat dintr-un
  terminal nou.
- **`npm install -g` eșuează cu o eroare de permisiuni:** configurați un director
  global npm deținut de utilizator, apoi redeschideți terminalul și instalați din nou
  Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` lipsește:** instalați-l din
  [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas folosește `uv` pentru a gestiona mediul Python al serverului de agenți.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` sau `docker run` nu reușește să se conecteze:** asigurați-vă că
  Docker Desktop rulează (pictograma sa cu balenă se află în bara de sistem) și că
  motorul a terminat de pornit. `docker version` ar trebui să afișeze atât o secțiune
  Client, cât și una Server.
- **Containerul pornește, dar backend-ul nu devine niciodată sănătos:** prima
  lansare inițializează Agent Server în interiorul containerului; acordați-i un minut
  sau două, apoi verificați `docker logs <container>` pentru erori.
- **Containerul nu poate ajunge la Lemonade:** containerul ajunge la gazdă prin
  `host.docker.internal`. Confirmați că Lemonade rulează pe gazda Windows cu
  `lemonade status` și folosiți `http://host.docker.internal:13305/api/v1` ca
  Base URL la configurarea LLM-ului.
<!-- @os:end -->

- **Interfața se încarcă, dar backend-ul arată ca nesănătos:** așteptați un minut
  sau două pentru ca serverul de agenți să termine pornirea, apoi reîmprospătați.
  Dacă rămâne nesănătos, reporniți stiva și verificați jurnalele pentru erori.
- **Cererile de chat Lemonade eșuează cu o eroare de conexiune:** confirmați că
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` reușește și că Lemonade încă
  servește modelul cu `lemonade status`.
- **Agentul generează o eroare legată de lungimea contextului sau limita de
  token-uri:** porniți o conversație nouă, astfel încât agentul să nu care un
  istoric supradimensionat. Dacă se întâmplă în continuare, reporniți Lemonade cu
  un `ctx_size` mai mare decât valoarea implicită de 65536 (de exemplu
  `ctx_size=131072`), dacă memoria permite.
- **Agentul produce modificări de calitate scăzută sau incomplete:** treceți la
  un model mai mare în Lemonade sau oferiți agentului o sarcină mai mică și mai
  concretă, și lăsați-l să o finalizeze înainte de a solicita următoarea modificare.

## Pașii următori

- Încercați o sarcină mai amplă în același spațiu de lucru, cum ar fi adăugarea
  unui fișier de test unitar sau remedierea unei erori cunoscute, și revizuiți
  diferențele (diff) agentului înainte de a păstra modificarea.
- Conectați un server MCP precum GitHub sau Slack în secțiunea **Customize**,
  astfel încât agentul să poată citi probleme sau posta actualizări în timp ce
  lucrează.
- Salvați mai multe profiluri LLM (un model mic și rapid și un model mare și mai
  puternic) și comutați între ele cu `/model` în mijlocul conversației.
- Treceți la [automatizările OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  pentru a transforma buclele recurente de dezvoltare în rulări de agenți programate
  sau declanșate de evenimente.

## Resurse

- [Documentația OpenHands](https://docs.openhands.dev/)
- [Prezentare generală Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configurare Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profiluri LLM și configurarea modelului](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentația Lemonade Server](https://lemonade-server.ai/docs)

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