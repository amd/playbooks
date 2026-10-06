<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prezentare generală

Dezvoltatorii petrec mult timp pe bucle mici și recurente: revizuirea pull request-urilor etichetate, răspunsul la comentariile de pe GitHub, triajul problemelor noi și transformarea firelor de discuții din Slack în notițe de standup sau urmăriri de incidente, precum și monitorizarea semnalelor de lansare sau de cercetare.
Fiecare buclă este familiară, dar necesită totuși discernământ: adunarea contextului potrivit, decizia asupra a ceea ce contează și postarea unei actualizări clare acolo unde echipa lucrează deja.

[Automatizările OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transformă aceste bucle în conversații programate sau declanșate de evenimente ale agentului: rulări în care un agent software de tip AI poate citi contextul, apela instrumente și produce o actualizare.
Șabloanele de automatizare comune din catalogul de extensii OpenHands urmează acest tipar pentru revizuirea pull request-urilor pe GitHub, monitorizarea depozitelor, triajul problemelor Linear, retrospectivele incidentelor, rezumatele de standup pe Slack și rapoartele de cercetare: o automatizare se activează, folosește integrări configurate precum GitHub sau Slack pentru a prelua contextul, raționează asupra acelui context cu un model de limbaj de mari dimensiuni (LLM) și scrie înapoi un rezultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) este planul de control local pentru construirea și testarea acestor automatizări.
În acest ghid, rulează un OpenHands Agent Server, procesul backend care execută conversațiile agentului, și conectează agentul la servicii externe precum GitHub și Slack.

Pentru a păstra fluxul de lucru pe sistemul tău AMD, agentul comunică cu un model local servit de Lemonade Server.
Lemonade expune acel model printr-un API compatibil cu OpenAI, astfel încât Agent Canvas îl poate configura precum un punct final la distanță de tip OpenAI, în timp ce modelul, promptul și contextul fluxului de lucru rămân locale.

În acest ghid, vei construi o automatizare concretă: un rezumat programat de dezvoltare de la GitHub la Slack.
Acesta folosește GitHub pentru a inspecta activitatea recentă a depozitului, Slack pentru a posta rezumatul, apeluri API Agent Canvas pentru a configura și testa automatizarea, și Lemonade pentru a rula LLM-ul local.

![Diagramă de arhitectură care arată GitHub MCP, automatizarea OpenHands, Lemonade Server și Slack MCP](assets/00-architecture-overview.png)

## Ce vei învăța

- Cum să pornești Lemonade Server și să verifici că un model local răspunde la cereri de chat
- Cum să lansezi Agent Canvas și să îndrepți Agent Server-ul acestuia către un LLM local
- Cum să instalezi servere GitHub și Slack Model Context Protocol (MCP) prin API-ul Agent Server
- Cum să creezi și să lansezi o automatizare OpenHands programată care postează un rezumat de dezvoltare pe Slack
- Cum să depanezi cele mai comune eșecuri legate de modelul local și de automatizare

## Concepte de bază

| Concept | Ce este | Unde se încadrează în acest ghid |
| --- | --- | --- |
| Lemonade Server | O platformă locală de servire LLM construită pentru hardware AMD, care expune un API compatibil cu OpenAI. Datele tale nu părăsesc niciodată mașina ta. | Rulează modelul care alimentează agentul. |
| OpenHands Agent Server | Procesul backend care execută conversațiile agentului OpenHands. | Găzduiește agentul, profilul său LLM și serverele sale MCP. |
| Agent Canvas | Planul de control local pentru OpenHands care rulează Agent Server și o interfață pentru inspectarea rulărilor agentului. | Lansează backend-urile și oferă API-ul pe care îl apelezi. |
| Server MCP | Un server Model Context Protocol care oferă unui agent instrumente pentru un serviciu extern precum GitHub sau Slack. | Permite agentului să citească GitHub și să scrie pe Slack. |
| Automatizare OpenHands | O conversație a agentului programată sau declanșată de evenimente, care preia context, raționează asupra acestuia și scrie undeva un rezultat. | Rezumatul GitHub-la-Slack pe care îl construiești aici. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Fluxurile de lucru ale agenților de programare beneficiază de un model și o fereastră de context mai mari.
> Folosește cel puțin 32 GB de memorie de sistem și preferă 64 GB sau mai mult pentru modele GGUF mai mari.
<!-- @device:end -->

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifică actualizările de software

<!-- @require:software-update -->
<!-- @device:end -->

## Cerințe preliminare

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

Ai nevoie de:

- Lemonade Server instalat urmând [ghidul standard de instalare Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 sau o versiune ulterioară și `npm`, folosite pentru a instala CLI-ul publicat Agent Canvas și pentru a rula servere MCP cu `npx`.
- `uv`, managerul de pachete Python pe care Agent Canvas îl folosește pentru a construi mediul Agent Server. Dacă nu este deja instalat, instalează-l din [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/).
- Un pachet `@openhands/agent-canvas` publicat recent, cu setări de agent bazate pe schemă, `LLMSummarizingCondenserSettings.max_tokens` și suport LLM `custom_tokenizer`.
- Pachetul Python `transformers` disponibil în mediul Agent Server. Este necesar pentru numărarea tokenurilor pe baza șablonului de chat atunci când este setat `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instalat și în funcțiune. Pe Windows, stiva Agent Canvas rulează din imaginea Docker publicată, care include Node.js, `uv`, `transformers` și pachetul `@openhands/agent-canvas`, astfel încât nu este nevoie să le instalezi pe gazdă.
<!-- @os:end -->

- Un token GitHub cu acces de citire la depozitul pe care dorești să îl rezumi.
- Un token de bot Slack (`xoxb-...`) cu acces `chat:write` și de citire a canalelor.
- Un ID de echipă Slack (`T...`).
- Un ID de canal Slack (`C...`) unde ar trebui postat rezumatul.

Invită aplicația Slack în canalul țintă înainte de a testa automatizarea.
## Variabile utilizate în acest playbook

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

Aceste două variabile sunt folosite de comenzile de verificare de mai jos.
Modelul, tokenizerul și celelalte setări LLM sunt introduse direct în UI-ul Agent Canvas în pașii următori, așa că valorile lor literale sunt afișate inline unde este nevoie de ele.

Următoarele valori sunt introduse în UI-ul Agent Canvas în pașii următori.
Setați-le aici pentru a le putea copia:

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

Folosiți o valoare explicită `owner/repo` pentru `GITHUB_REPO_FILTER`.
Caracterele wildcard largi pentru organizații pot returna prea mult context MCP pentru modelele locale.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Porniți Lemonade Server

Porniți modelul din Lemonade CLI:

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

> **Alegeți un model potrivit pentru hardware-ul dvs.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) este un model puternic pentru acest flux de lucru, dar necesită un pool mare de memorie.
> Dacă dispozitivul dvs. are memorie sau VRAM GPU limitate, alegeți un model GGUF mai mic din biblioteca de modele Lemonade și folosiți acel ID de model (și tokenizerul corespunzător) pe parcursul acestui playbook.

> **Notă:** Prima comandă `lemonade run` descarcă modelul dacă acesta nu este deja prezent, ceea ce poate dura un timp, în funcție de dimensiunea modelului și de conexiunea dvs.

Lemonade expune un API compatibil OpenAI la:

```text
http://127.0.0.1:13305/api/v1
```

Opțional: dacă Agent Canvas sau automation runner nu se află pe aceeași mașină, publicați endpoint-ul Lemonade printr-un tunel securizat și folosiți URL-ul HTTPS ca URL de bază LLM.
[ngrok](https://ngrok.com/) expune un port local pe internet printr-un URL HTTPS securizat; necesită un cont ngrok gratuit, iar dvs. înlocuiți `YOUR_NGROK_DOMAIN.ngrok-free.dev` cu propriul domeniu rezervat:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificați modelul local

Confirmați că Lemonade poate servi modelul selectat:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Apoi trimiteți o cerere mică de chat:

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

Apoi trimiteți o cerere mică de chat:

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

## 3. Porniți Agent Canvas

<!-- @os:linux -->
Instalați pachetul Agent Canvas publicat și porniți întregul stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Dacă instalarea globală npm eșuează cu o eroare de permisiuni, consultați secțiunea de depanare a permisiunilor npm de mai jos.

În mod implicit, Agent Canvas pornește la `http://localhost:8000`.
Deschideți acel URL în browser.
Portul nu este special—dacă 8000 este deja utilizat, transmiteți orice port liber cu `--port` (sau `-p`).
Backend-ul local implicit ar trebui să apară ca fiind sănătos pe ecranul principal.

> **Notă:** Prima lansare construiește mediul Python gestionat de `uv` al Agent Server, așa că poate dura câteva minute înainte ca backend-ul să raporteze starea sănătoasă.

Comanda `agent-canvas` pornește împreună agent server-ul, backend-ul de automatizare și frontend-ul web.
Aveți nevoie doar de această singură comandă pentru a rula OpenHands local.
Restul acestui playbook configurează totul prin UI-ul Agent Canvas din browser.
<!-- @os:end -->

<!-- @os:windows -->
Pe Windows, rulați imaginea de container Agent Canvas publicată cu Docker Desktop.
Imaginea include Agent Server, backend-ul de automatizare și frontend-ul web, astfel încât nu este nevoie să instalați Node.js, `uv` sau CLI-ul pe gazdă.

Mai întâi, creați folderele de configurare și de workspace pe care containerul le montează:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Descărcați imaginea publicată (aproximativ 6 GB; este publică, deci nu este necesară autentificarea):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Apoi porniți stack-ul:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Deschideți `http://localhost:8000/canvas` în browser.
Dacă portul 8000 este deja utilizat, mapați un port de gazdă diferit, de exemplu `-p 8080:8000`, și deschideți în schimb `http://localhost:8080/canvas`.

> **Notă:** Prima lansare construiește mediul Agent Server în interiorul containerului, așa că poate dura câteva minute înainte ca backend-ul să raporteze starea sănătoasă.

Montarea `.openhands` păstrează profilul LLM, serverele MCP și automatizările dvs. între reporniri ale containerului.
Restul acestui playbook configurează totul prin UI-ul Agent Canvas din browser, la `http://localhost:8000/canvas`.
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
## 4. Configurați LLM-ul local în interfață

La prima lansare, Agent Canvas deschide un flux de onboarding.
În acel flux:

1. Păstrați **OpenHands** selectat ca agent și faceți clic pe **Next**.
2. La **Set up your LLM**, selectați **Advanced**.
3. Păstrați **Authentication** setat la **API key**.
4. Setați **Custom Model** la `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setați **Base URL** la `http://127.0.0.1:13305/api/v1`.
6. Pentru **API Key**, introduceți orice valoare de rezervă non-goală, precum `lemonade-local`. Lemonade nu necesită o cheie reală, dar clientul OpenHands trebuie să trimită o valoare.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server rulează în interiorul containerului, așa că setați **Base URL** la `http://host.docker.internal:13305/api/v1` în loc de `http://127.0.0.1:13305/api/v1`.
> Din interiorul containerului, `127.0.0.1` reprezintă containerul însuși; `host.docker.internal` ajunge la Lemonade care rulează pe gazda Windows, iar Docker Desktop furnizează automat acest nume de gazdă.
<!-- @os:end -->

Câmpurile de conexiune ar trebui să arate astfel.
Câmpul pentru cheia API este mascat de interfață.

![Setările avansate pentru LLM la prima utilizare în Agent Canvas, cu modelul Lemonade și URL-ul de bază local](assets/01-llm-advanced-settings.png)

Apoi selectați **All** și setați câmpurile suplimentare pentru modelul local:

1. Derulați până la **Custom Tokenizer** și setați-l la `Qwen/Qwen3.6-35B-A3B`.
2. Derulați până la **LiteLLM Extra Body** și setați-l la `{"enable_thinking": true}`.
3. Faceți clic pe **Next**.

![Fila All pentru LLM la prima utilizare în Agent Canvas, cu tokenizer-ul personalizat Qwen](assets/02-llm-all-tokenizer-settings.png)

![Fila All pentru LLM la prima utilizare în Agent Canvas, cu corpul suplimentar LiteLLM configurat](assets/03-llm-all-extra-body-settings.png)

Setările LLM ar trebui să arate astfel:

| Câmp | Valoare |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefixul `openai/` indică LiteLLM să folosească formatarea cererilor compatibilă cu OpenAI pentru endpoint-ul Lemonade.
Tokenizer-ul personalizat este tokenizer-ul original Hugging Face pentru modelul GGUF; acesta îi permite lui OpenHands să numere aceleași token-uri din șablonul de chat pe care le vede serverul local al modelului.
Formularul actual pentru LLM la prima utilizare nu afișează setările de condenser.
Dacă versiunea dumneavoastră de Agent Canvas expune ulterior setările de condenser sub **Settings > LLM**, folosiți `llm_summarizing` și setați numărul maxim de token-uri sub fereastra de context Lemonade, de exemplu `56000`.

## 5. Instalarea serverelor MCP pentru GitHub și Slack

În interfața Agent Canvas, deschideți **Customize** (sau **Settings > MCP**) pentru a adăuga serverele MCP care oferă agentului instrumente pentru GitHub și Slack.
Valorile token-urilor sunt trimise doar către Agent Server-ul local și sunt persistate ca setări criptate.

<!-- @os:windows -->
> **Windows (Docker):** comenzile serverului MCP `npx` de mai jos rulează în interiorul containerului, care include deja Node.js, astfel încât nu se instalează nimic suplimentar pe gazdă.
> Deoarece `.openhands` este montat, serverele MCP și token-urile acestora persistă între repornirile containerului.
<!-- @os:end -->

### Serverul MCP pentru GitHub

Adăugați un nou server MCP cu aceste setări:

| Câmp | Valoare |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = token-ul dumneavoastră GitHub |

Folosiți un token GitHub cu acces de citire la depozitul pe care doriți să îl rezumați.

### Serverul MCP pentru Slack

Adăugați un al doilea server MCP cu aceste setări:

| Câmp | Valoare |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID-ul canalului dumneavoastră de rezumat |

Setați `SLACK_CHANNEL_IDS` la ID-ul canalului de rezumat (aceeași valoare ca `SLACK_DIGEST_CHANNEL`) astfel încât agentul să nu fie nevoit să parcurgă fiecare canal Slack.

După adăugarea ambelor servere, folosiți butonul **Test** pe fiecare dintre ele pentru a confirma că se conectează și anunță instrumentele.
Serverul GitHub ar trebui să listeze instrumente GitHub, iar serverul Slack ar trebui să listeze instrumente Slack.

![Pagina MCP din Agent Canvas cu serverele GitHub și Slack instalate](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Crearea automatizării pentru rezumat

În interfața Agent Canvas, deschideți pagina **Automations** și creați o nouă automatizare:

1. Alegeți **Create automation** și selectați tipul **Prompt preset**.
2. Setați **Name** la `GitHub Development Digest to Slack`.
3. Setați **Prompt** la următorul text, înlocuind valorile de rezervă pentru depozit și canal cu valorile dumneavoastră:

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

4. Setați **Trigger** la **Cron** cu programul `0 9 * * 1-5` (ora 9:00 în zilele lucrătoare) și setați **Timezone** la fusul dumneavoastră orar, de exemplu `America/New_York`.
5. Setați **Timeout** la `900` secunde.
6. Salvați automatizarea.

Pagina de detalii a automatizării afișează noua automatizare împreună cu declanșatorul cron și punctul de intrare generat pentru prompt preset.

![Pagina de detalii a automatizării din Agent Canvas după creare](assets/05-automation-created.png)
## 7. Testați automatizarea

Din pagina de detalii a automatizării din interfața Agent Canvas:

1. Faceți clic pe **Run now** (sau **Dispatch**) pentru a rula automatizarea o dată, imediat.
2. Urmăriți lista de execuții de pe aceeași pagină. Cea mai recentă execuție ar trebui să treacă în starea `COMPLETED`.
3. Deschideți canalul Slack țintă. Acesta ar trebui să conțină digest-ul generat.

Nu este necesar să așteptați declanșarea programării cron—**Run now** declanșează o execuție la cerere, astfel încât să puteți confirma că prompt-ul, conexiunile MCP și postarea pe Slack funcționează toate înainte de a vă baza pe programare.

![Execuția automatizării Agent Canvas finalizată cu succes](assets/06-automation-run-completed.png)

![Canal Slack care afișează digest-ul OpenHands generat](assets/07-slackbot-message.png)

## Depanare

<!-- @os:windows -->
- **Portul Docker 8000 este deja utilizat:** mapați un alt port gazdă, de exemplu `docker run ... -p 8080:8000 ...`, și deschideți `http://localhost:8080/canvas`.
- **`docker pull` eșuează cu o eroare de autentificare** (de exemplu, „A specified logon session does not exist"): rulați pull-ul dintr-o sesiune Windows interactivă, sau pre-descărcați imaginea. Imaginea este publică, deci nu este necesar `docker login`.
- **Interfața se încarcă, dar backend-ul nu este sănătos:** prima lansare construiește mediul Agent Server în interiorul containerului. Așteptați un minut și reîmprospătați, apoi verificați `docker logs <container>` pentru progres.
- **Agent Canvas nu poate ajunge la Lemonade din container:** setați **Base URL** pentru LLM la `http://host.docker.internal:13305/api/v1` (nu `127.0.0.1`), și confirmați că Lemonade rulează pe gazda Windows.
<!-- @os:end -->

- **Lemonade este oprit:** reporniți-l cu comanda `lemonade run "${LEMONADE_MODEL}"` din pasul 1, apoi re-rulați verificarea de sănătate.
- **`npm install -g` eșuează cu o eroare de permisiuni:** pe Linux sau WSL, configurați un director global npm deținut de utilizator, adăugați-l în fișierul de pornire al shell-ului, apoi instalați din nou Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Dacă utilizați `zsh`, adăugați aceeași linie `export PATH=...` în `~/.zshrc` în loc de `~/.bashrc`.
- **Agent Canvas respinge setările LLM după setarea `custom_tokenizer`:** instalați `transformers` în mediul Python al Agent Server, reporniți Agent Canvas dacă este necesar, și încercați din nou să salvați setările LLM. OpenHands necesită Transformers pentru a încărca șablonul de chat al tokenizer-ului atunci când `custom_tokenizer` este setat.
- **Agent Canvas nu poate ajunge la Lemonade:** verificați `curl -fsS "${LEMONADE_BASE_URL}/health"` și confirmați că URL-ul de bază introdus în formularul LLM la prima utilizare sau în **Settings > LLM** corespunde endpoint-ului local activ sau tunelului HTTPS.
- **Setările LLM nu s-au salvat:** asigurați-vă că ați făcut clic pe **Next** după introducerea valorilor. Redeschideți **Settings > LLM** pentru a confirma că valorile au fost păstrate.
- **GitHub MCP nu poate vedea depozitele private:** confirmați că token-ul GitHub are acces de citire la depozitul țintă și că butonul **Test** MCP din **Customize** afișează uneltele GitHub.
- **Slack poate citi canale, dar nu poate posta:** invitați aplicația Slack în canalul țintă și confirmați că bot-ul are `chat:write`.
- **Automatizarea listează prea multe canale Slack:** utilizați un ID de canal Slack și setați `SLACK_CHANNEL_IDS` pe serverul Slack MCP din **Customize**.
- **Execuția automatizării eșuează sau depășește contextul:** confirmați că Lemonade a fost pornit cu `ctx_size=65536`, confirmați că LLM-ul OpenHands are setat `custom_tokenizer`, și utilizați un depozit explicit cu seturile de rezultate GitHub limitate la 3-5 elemente. Dacă versiunea dvs. de Agent Canvas expune setări de condensare, setați numărul maxim de token-uri pentru condensare sub fereastra de context a Lemonade.

## Pași următori

- Adăugați un digest săptămânal doar pentru lansări.
- Adăugați o automatizare declanșată de evenimente GitHub pentru alerte mai rapide de PR sau push.
- Direcționați același digest către Notion, Linear sau un alt instrument susținut de MCP.

## Resurse

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentația Lemonade Server](https://lemonade-server.ai/docs)
- [Depozitul de extensii OpenHands](https://github.com/OpenHands/extensions)
- [Servere Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pachetul Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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