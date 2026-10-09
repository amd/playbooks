<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prehľad

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je AI softvérový agent,
ktorý dokáže písať kód, spúšťať príkazy, prehliadať web a upravovať súbory v reálnom
pracovnom priestore. Namiesto kopírovania návrhov z okna chatu nasmerujete
agenta na priečinok projektu a necháte ho pracovať: implementovať funkciu, opraviť
chybu, napísať testy alebo vysvetliť kódovú základňu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je odporúčané
webové rozhranie na spúšťanie OpenHands. Jediný príkaz `agent-canvas` spustí
server agenta, automatizačný backend a webový frontend naraz, takže môžete
viesť konverzáciu s agentom z prehliadača.

Aby všetko zostalo na vašom systéme AMD, agent komunikuje s lokálnym modelom poskytovaným
serverom Lemonade Server. Lemonade sprístupňuje tento model prostredníctvom API kompatibilného
s OpenAI, takže Agent Canvas ho môže nakonfigurovať ako akýkoľvek iný koncový bod v štýle OpenAI,
pričom model, váš kód a kontext konverzácie zostávajú na vašom
počítači.

V tejto príručke spustíte lokálny model, spustíte Agent Canvas, nasmerujete ho
na tento model a spustíte svoju prvú programátorskú úlohu na skutočnom priečinku projektu.

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na chatové požiadavky
- Ako nainštalovať a spustiť Agent Canvas z npm balíka
- Ako nakonfigurovať Agent Canvas tak, aby používal lokálny model Lemonade ako LLM
- Ako spustiť konverzáciu OpenHands a sledovať, ako agent upravuje súbory a spúšťa
  príkazy v pracovnom priestore
- Ako skontrolovať, čo agent zmenil, a usmerniť ho ďalšími správami

## Základné koncepty

| Koncept | Čo to je | Kde to zapadá do tejto príručky |
| --- | --- | --- |
| Lemonade Server | Lokálna platforma na poskytovanie LLM postavená pre hardvér AMD, ktorá sprístupňuje API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands | AI softvérový agent, ktorý číta a upravuje súbory, spúšťa príkazy shellu a prehliada web v rámci pracovného priestoru. | Agent, ktorého ovládate z chatu. |
| Agent Canvas | Webové rozhranie a backend, ktorý spúšťa konverzácie OpenHands a zobrazuje volania nástrojov a zmeny súborov. | Spúšťa celý stack a hostí vašu konverzáciu. |
| Pracovný priestor | Priečinok projektu, ktorý má agent povolené čítať a upravovať. | Cieľ úprav a príkazov agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Workflow kódovacích agentov profituje z väčšieho modelu a väčšieho kontextového okna. Použite
> aspoň 32 GB systémovej pamäte a uprednostnite 64 GB alebo viac pri väčších GGUF modeloch.
<!-- @device:end -->

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola softvérových aktualizácií

<!-- @require:software-update -->
<!-- @device:end -->

## Predpoklady


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Potrebujete:

- Nainštalovaný Lemonade Server schopný poskytovať nižšie uvedený model.

<!-- @os:linux -->
- Node.js 22.12 alebo novší a `npm` (používané CLI nástrojom `agent-canvas`).
- `uv`, správca balíkov Python, ktorý Agent Canvas používa na správu prostredia
  servera agenta. Ak ho vo vašom systéme ešte nemáte, nainštalujte si ho podľa
  [sprievodcu inštaláciou uv](https://docs.astral.sh/uv/getting-started/installation/)
  pred spustením Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  nainštalovaný a spustený. V systéme Windows beží stack Agent Canvas z
  publikovaného Docker obrazu, ktorý obsahuje Node.js, `uv` a balík
  `@openhands/agent-canvas`, takže ich na hostiteľskom systéme nemusíte inštalovať.
<!-- @os:end -->

- Priečinok projektu, v ktorom budete pracovať. Môže to byť akýkoľvek lokálny git repozitár alebo
  adresár s kódom, na ktorom má agent pracovať.

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

## 1. Spustite Lemonade Server

Spustite model z Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Vyberte model, ktorý vyhovuje vášmu hardvéru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je silný kódovací model, ale vyžaduje veľký pamäťový pool. Ak má vaše zariadenie obmedzenú pamäť alebo VRAM grafickej karty, namiesto toho vyberte menší GGUF model z knižnice modelov Lemonade a toto ID modelu používajte v celej tejto príručke.

> **Poznámka:** Prvé spustenie `lemonade run` model stiahne, ak ešte nie je prítomný, čo môže trvať chvíľu v závislosti od veľkosti modelu a vášho pripojenia.

Lemonade sprístupňuje API kompatibilné s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Overte lokálny model

Overte, že Lemonade dokáže poskytovať vybraný model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Následne odošlite malú chatovú požiadavku:

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

Ak táto požiadavka vráti pole `choices`, Lemonade je pripravený pre Agent Canvas.

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
## 3. Inštalácia a spustenie Agent Canvas

<!-- @os:linux -->
Nainštalujte publikovaný balík Agent Canvas globálne:

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

Potom spustite celý stack z terminálu:

```bash
agent-canvas
```

Štandardne sa Agent Canvas spustí na adrese `http://localhost:8000`. Otvorte túto
adresu URL vo svojom prehliadači. Port nie je ničím výnimočný — ak je 8000 už
používaný, pri spúšťaní Agent Canvas zadajte ľubovoľný voľný port pomocou
`--port` (alebo `-p`):

```bash
agent-canvas --port 3000
```

Potom namiesto toho otvorte `http://localhost:3000`. Predvolený lokálny backend
by sa mal na domovskej obrazovke zobraziť ako funkčný (healthy).

Príkaz `agent-canvas` spustí agent server, automatizačný backend a webový
frontend spoločne. Na lokálne spustenie OpenHands potrebujete iba tento jeden
príkaz.

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
V systéme Windows spustite publikovaný kontajnerový obraz Agent Canvas pomocou
Docker Desktop. Obraz obsahuje Agent Server, automatizačný backend a webový
frontend, takže na hostiteľský systém nemusíte inštalovať Node.js, `uv` ani CLI.

Najprv vytvorte priečinky pre konfiguráciu a pracovný priestor, ktoré kontajner pripojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stiahnite publikovaný obraz (je verejný, takže nie je potrebné prihlásenie):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Potom spustite stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otvorte `http://localhost:8000/canvas` vo svojom prehliadači. Ak je port 8000
už používaný, namapujte iný hostiteľský port, napríklad `-p 8080:8000`, a
namiesto toho otvorte `http://localhost:8080/canvas`.

> **Poznámka:** Prvé spustenie inicializuje Agent Server vnútri kontajnera,
> takže môže trvať minútu alebo dve, kým backend nahlási, že je funkčný.

Pripojenie `.openhands` zachováva váš LLM profil a nastavenia medzi
reštartmi kontajnera. Zvyšok tohto návodu konfiguruje všetko prostredníctvom
rozhrania Agent Canvas vo vašom prehliadači.

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

## 4. Konfigurácia lokálneho LLM

Pri prvom spustení otvorí Agent Canvas úvodný (onboarding) proces. V tomto procese:

1. Ponechajte **OpenHands** vybraný ako agent a kliknite na **Next**.
2. Na obrazovke **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > V systéme Windows beží stack v kontajneri, ktorý sa nedokáže pripojiť k
   > hostiteľovi na adrese `127.0.0.1`. Namiesto toho použite
   > `http://host.docker.internal:13305/api/v1`, aby sa kontajnerizovaný agent
   > mohol pripojiť k Lemonade bežiacemu na hostiteľskom systéme Windows.
   <!-- @os:end -->
6. Do poľa **API Key** zadajte akýkoľvek neprázdny zástupný text, napríklad
   `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands
   potrebuje nejakú hodnotu na odoslanie.
7. Kliknite na **Next**.

Dokončené nastavenia Advanced by mali vyzerať takto. Pole s API kľúčom je
v používateľskom rozhraní skryté.

![Rozšírené nastavenia LLM v Agent Canvas pri prvom použití s modelom Lemonade a lokálnou základnou adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tieto hodnoty ako LLM profil. Ak vás vaša verzia požiada o
pomenovanie tohto profilu, použite názov bez medzier, napríklad `lemonade-local`.
Ak neskôr zmeníte modely, otvorte **Settings > LLM** a aktualizujte tie isté
rozšírené polia. Medzi uloženými profilmi môžete prepínať priamo z poľa na
zadávanie chatu pomocou príkazu `/model`.

## 5. Otvorenie pracovného priestoru

Agent môže čítať a upravovať súbory iba v rámci pracovného priestoru, ktorý
vyberiete. Pred spustením úlohy nasmerujte Agent Canvas na priečinok vášho
projektu:

1. Na domovskej obrazovke zvoľte **Open Workspace**.
2. Vyberte priečinok, ktorý obsahuje váš projekt (napríklad git repozitár,
   na ktorom má agent pracovať).
3. Spustite novú konverzáciu v tomto pracovnom priestore.

Všetko, čo agent robí — čítanie súborov, spúšťanie príkazov, úprava kódu — je
obmedzené na tento pracovný priestor.

![Domovská obrazovka Agent Canvas po úvodnom procese](assets/02-agent-canvas-home.png)

## 6. Spustenie prvej programátorskej úlohy

Keď je pracovný priestor otvorený a je vybraný lokálny LLM, zadajte do chatu
konkrétnu úlohu. Dobrá prvá úloha je malá a overiteľná, napríklad:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovú os konverzácie. OpenHands:

- Prečíta pracovný priestor, aby pochopil jeho štruktúru.
- Vytvorí `hello.py` s požadovanou funkciou a testovacím blokom.
- Voliteľne spustí `python3 hello.py` na overenie výstupu.
- Oznámi v chate, čo urobil, a prípadný výstup príkazov.

Mali by ste vidieť, že sa v pracovnom priestore objaví nový súbor, a konečná
správa agenta by mala popisovať vykonanú zmenu. Toto je okamih odmeny: agent
napísal a spustil skutočný kód vo vašom projektovom priečinku.

## 7. Kontrola a usmerňovanie agenta

Po dokončení kroku agentom skontrolujte jeho prácu predtým, ako prijmete
ďalší krok:

- **Zmeny súborov**: na zobrazenie presne toho, čo bolo pridané, zmenené alebo
  odstránené, použite prehliadač súborov pracovného priestoru alebo zobrazenie
  rozdielov (diff) agenta.
- **Výstup príkazov**: rozbaľte ktorýkoľvek príkaz, ktorý agent spustil, aby
  ste videli stdout, stderr a návratový kód.
- **Následné kroky**: ak výsledok nie je taký, aký ste chceli, odpovedzte v
  tej istej konverzácii s opravou. Agent si zachová predchádzajúci kontext a
  pokračuje v práci na tých istých súboroch.

Ak sa napríklad v teste nevypísal očakávaný pozdrav, odpovedzte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent znova prečíta súbor, spustí príkaz, diagnostikuje problém a súbor
opäť upraví — všetko v tej istej konverzácii.
## Riešenie problémov

<!-- @os:linux -->
- **`agent-canvas` sa nenachádza v PATH:** preinštalujte pomocou
  `npm install -g @openhands/agent-canvas` a overte, že adresár globálnych binárnych súborov npm
  je zahrnutý v PATH predtým, než bude možné spustiť `agent-canvas` z nového
  terminálu.
- **Príkaz `npm install -g` zlyhá s chybou oprávnení:** nastavte globálny adresár npm vo vlastníctve
  používateľa, potom znova otvorte terminál a znova nainštalujte Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Chýba `uv`:** nainštalujte ho podľa
  [sprievodcu inštaláciou uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používa `uv` na správu Python prostredia agent servera.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` alebo `docker run` sa nedokáže pripojiť:** uistite sa, že Docker Desktop
  beží (jeho ikona veľryby je v systémovej lište) a že engine dokončil spúšťanie.
  Príkaz `docker version` by mal zobraziť sekciu Client aj Server.
- **Kontajner sa spustí, ale backend nikdy nenadobudne stav healthy:** prvé
  spustenie inicializuje Agent Server vnútri kontajnera; dajte mu minútu alebo
  dve a potom skontrolujte `docker logs <container>` kvôli chybám.
- **Kontajner sa nedokáže pripojiť k Lemonade:** kontajner sa pripája k hostiteľovi cez
  `host.docker.internal`. Overte, že Lemonade beží na Windows hostiteľovi pomocou
  `lemonade status`, a pri konfigurácii LLM použite ako základnú URL adresu
  `http://host.docker.internal:13305/api/v1`.
<!-- @os:end -->

- **UI sa načíta, ale backend zobrazuje stav unhealthy:** počkajte minútu alebo dve, kým
  agent server dokončí spúšťanie, a potom obnovte stránku. Ak zostane unhealthy, reštartujte
  stack a skontrolujte logy kvôli chybám.
- **Chatové požiadavky v Lemonade zlyhávajú s chybou pripojenia:** overte, že
  príkaz `curl -fsS "http://127.0.0.1:13305/api/v1/health"` je úspešný a že
  Lemonade stále obsluhuje model pomocou `lemonade status`.
- **Agent hlási chybu týkajúcu sa dĺžky kontextu alebo limitu tokenov:** začnite
  novú konverzáciu, aby agent neniesol so sebou nadmerne veľkú históriu. Ak sa to
  opakuje, reštartujte Lemonade s väčším `ctx_size`, než je predvolená hodnota
  65536 (napríklad `ctx_size=131072`), ak to pamäť dovoľuje.
- **Agent produkuje nekvalitné alebo neúplné úpravy:** prepnite sa na väčší
  model v Lemonade, alebo dajte agentovi menšiu, konkrétnejšiu úlohu a nechajte ho
  dokončiť ju skôr, než požiadate o ďalšiu zmenu.

## Ďalšie kroky

- Vyskúšajte väčšiu úlohu v rovnakom pracovnom priestore, napríklad pridanie súboru s jednotkovými testami alebo
  opravu známej chyby, a pred ponechaním zmeny skontrolujte diff vytvorený agentom.
- Pripojte server MCP, napríklad GitHub alebo Slack, v časti **Customize**, aby
  agent mohol počas práce čítať problémy (issues) alebo zverejňovať aktualizácie.
- Uložte si viacero profilov LLM (rýchly malý model a výkonnejší veľký model) a
  prepínajte medzi nimi pomocou `/model` priamo počas konverzácie.
- Pokračujte na [automatizácie OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), kde
  môžete opakujúce sa vývojové cykly premeniť na naplánované alebo udalosťami spúšťané behy agenta.

## Zdroje

- [Dokumentácia OpenHands](https://docs.openhands.dev/)
- [Prehľad Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavenie Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profily LLM a konfigurácia modelu](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentácia Lemonade Server](https://lemonade-server.ai/docs)

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