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
ktorý dokáže písať kód, spúšťať príkazy, prehliadať web a upravovať súbory v
reálnom pracovnom priestore. Namiesto kopírovania návrhov z chatového okna
nasmerujete agenta na priečinok projektu a necháte ho vykonať prácu:
implementovať funkciu, opraviť chybu, napísať testy alebo vysvetliť kódovú
základňu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je odporúčané
webové rozhranie na spúšťanie OpenHands. Jediný príkaz `agent-canvas` spustí
server agenta, automatizačný backend a webový frontend spolu, takže konverzáciu
s agentom môžete viesť priamo z prehliadača.

Aby všetko zostalo na vašom AMD systéme, agent komunikuje s lokálnym modelom
poskytovaným serverom Lemonade Server. Lemonade sprístupňuje tento model cez
API kompatibilné s OpenAI, takže Agent Canvas ho môže nakonfigurovať ako
akýkoľvek iný koncový bod v štýle OpenAI, pričom model, váš kód aj kontext
konverzácie zostávajú na vašom počítači.

V tejto príručke spustíte lokálny model, spustíte Agent Canvas, nasmerujete ho
na daný model a vykonáte svoju prvú úlohu na skutočnom priečinku projektu.

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na chatové požiadavky
- Ako nainštalovať a spustiť Agent Canvas z npm balíka
- Ako nakonfigurovať Agent Canvas na použitie lokálneho modelu Lemonade ako LLM
- Ako spustiť konverzáciu v OpenHands a sledovať, ako agent upravuje súbory a spúšťa
  príkazy v pracovnom priestore
- Ako skontrolovať, čo agent zmenil, a usmerniť ho ďalšími správami

## Základné pojmy

| Pojem | Čo to je | Kde sa uplatňuje v tejto príručke |
| --- | --- | --- |
| Lemonade Server | Lokálna platforma na poskytovanie LLM postavená pre hardvér AMD, ktorá sprístupňuje API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands | AI softvérový agent, ktorý číta a upravuje súbory, spúšťa shellové príkazy a prehliada web v rámci pracovného priestoru. | Agent, ktorého ovládate z chatu. |
| Agent Canvas | Webové rozhranie a backend, ktorý spúšťa konverzácie OpenHands a zobrazuje volania nástrojov a zmeny súborov. | Spúšťa celý stack a hostí vašu konverzáciu. |
| Pracovný priestor | Priečinok projektu, ktorý má agent povolené čítať a upravovať. | Cieľ úprav a príkazov agenta. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Pracovné postupy kódovacích agentov profitujú z väčšieho modelu a väčšieho
> kontextového okna. Použite aspoň 32 GB systémovej pamäte a uprednostnite
> 64 GB alebo viac pre väčšie GGUF modely.
<!-- @device:end -->

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Predpoklady


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

Potrebujete:

- Nainštalovaný Lemonade Server schopný poskytovať nižšie uvedený model.

<!-- @os:linux -->
- Node.js 22.12 alebo novší a `npm` (používané CLI nástrojom `agent-canvas`).
- `uv`, správca Python balíkov, ktorý Agent Canvas používa na správu prostredia
  servera agenta. Ak ho váš systém ešte nemá, nainštalujte ho podľa
  [sprievodcu inštaláciou uv](https://docs.astral.sh/uv/getting-started/installation/)
  pred spustením Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  nainštalovaný a spustený. Na Windows beží stack Agent Canvas z publikovaného
  Docker image, ktorý v sebe zahŕňa Node.js, `uv` a balík
  `@openhands/agent-canvas`, takže tieto komponenty nemusíte inštalovať na
  hostiteľský systém.
<!-- @os:end -->

- Priečinok projektu, na ktorom sa bude pracovať. Môže to byť ľubovoľný lokálny
  git repozitár alebo adresár s kódom, na ktorom má agent pracovať.

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

## 1. Spustenie Lemonade Server

Spustite model z CLI nástroja Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Vyberte model, ktorý vyhovuje vášmu hardvéru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je silný model na kódovanie, ale vyžaduje veľký pamäťový fond. Ak má vaše zariadenie obmedzenú pamäť alebo GPU VRAM, vyberte si namiesto toho menší GGUF model z knižnice modelov Lemonade a toto ID modelu používajte v celej príručke.

> **Poznámka:** Prvý príkaz `lemonade run` stiahne model, ak ešte nie je prítomný, čo môže chvíľu trvať v závislosti od veľkosti modelu a vášho pripojenia.

Lemonade sprístupňuje API kompatibilné s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Overenie lokálneho modelu

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
Globálne nainštalujte publikovaný balík Agent Canvas:

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

Potom spustite celý zásobník z terminálu:

```bash
agent-canvas
```

Agent Canvas sa predvolene spúšťa na adrese `http://localhost:8000`. Otvorte
túto adresu vo svojom prehliadači. Port nie je nijako špeciálny — ak je port
8000 už obsadený, pri spúšťaní Agent Canvas zadajte ľubovoľný voľný port
pomocou `--port` (alebo `-p`):

```bash
agent-canvas --port 3000
```

Potom namiesto toho otvorte `http://localhost:3000`. Predvolený lokálny backend
by sa mal na domovskej obrazovke zobraziť ako funkčný (healthy).

Príkaz `agent-canvas` spúšťa agent server, automatizačný backend a webové
rozhranie spoločne. Na lokálne spustenie OpenHands potrebujete iba tento jeden
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
Vo Windows spustite publikovaný kontajnerový obraz Agent Canvas pomocou
Docker Desktop. Obraz obsahuje Agent Server, automatizačný backend a webové
rozhranie, takže na hostiteľský počítač nemusíte inštalovať Node.js, `uv` ani CLI.

Najskôr vytvorte priečinky pre konfiguráciu a pracovný priestor, ktoré kontajner pripojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stiahnite publikovaný obraz (je verejný, takže prihlásenie nie je potrebné):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Potom spustite zásobník:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otvorte `http://localhost:8000/canvas` vo svojom prehliadači. Ak je port 8000
už obsadený, namapujte iný port hostiteľa, napríklad `-p 8080:8000`, a namiesto
toho otvorte `http://localhost:8080/canvas`.

> **Poznámka:** Pri prvom spustení sa Agent Server inicializuje vo vnútri
> kontajnera, takže môže trvať minútu alebo dve, kým backend ohlási, že je funkčný.

Pripojenie `.openhands` uchováva váš profil LLM a nastavenia aj po reštarte
kontajnera. Zvyšok tejto príručky nakonfiguruje všetko prostredníctvom
používateľského rozhrania Agent Canvas vo vašom prehliadači.

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

Pri prvom spustení otvorí Agent Canvas uvádzací (onboarding) postup. V rámci neho:

1. Ponechajte **OpenHands** vybratý ako agent a kliknite na **Next**.
2. V časti **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavenú na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Vo Windows beží zásobník v kontajneri, ktorý nedokáže dosiahnuť hostiteľa na
   > adrese `127.0.0.1`. Namiesto toho použite
   > `http://host.docker.internal:13305/api/v1`, aby kontajnerizovaný agent mohol
   > dosiahnuť Lemonade bežiaci na hostiteľovi so systémom Windows.
   <!-- @os:end -->
6. Do poľa **API Key** zadajte ľubovoľný neprázdny zástupný text, napríklad
   `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands
   potrebuje nejakú hodnotu na odoslanie.
7. Kliknite na **Next**.

Dokončené pokročilé nastavenia by mali vyzerať takto. Pole API kľúča je v
rozhraní maskované.

![Pokročilé nastavenia LLM pri prvom spustení Agent Canvas s modelom Lemonade a lokálnou základnou adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tieto hodnoty ako profil LLM. Ak vás vaša verzia požiada o
pomenovanie tohto profilu, použite názov bez medzier, napríklad
`lemonade-local`. Ak neskôr zmeníte modely, otvorte **Settings > LLM** a
aktualizujte rovnaké pokročilé polia. Medzi uloženými profilmi môžete
prepínať z poľa chatu príkazom `/model`.

## 5. Otvorenie pracovného priestoru

Agent môže čítať a upravovať súbory iba v rámci pracovného priestoru, ktorý
zvolíte. Pred spustením úlohy nasmerujte Agent Canvas na priečinok svojho
projektu:

1. Na domovskej obrazovke vyberte **Open Workspace**.
2. Vyberte priečinok obsahujúci váš projekt (napríklad git repozitár, na
   ktorom chcete, aby agent pracoval).
3. Spustite v tomto pracovnom priestore novú konverzáciu.

Všetko, čo agent robí — čítanie súborov, spúšťanie príkazov, úprava kódu — je
obmedzené na tento pracovný priestor.

![Domovská obrazovka Agent Canvas po uvádzacom postupe](assets/02-agent-canvas-home.png)

## 6. Spustenie vašej prvej úlohy programovania

Keď je pracovný priestor otvorený a je vybratý lokálny LLM, zadajte do chatu
konkrétnu úlohu. Dobrou prvou úlohou je malá a overiteľná úloha, napríklad:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovú os konverzácie. OpenHands:

- Prečíta pracovný priestor, aby pochopil jeho štruktúru.
- Vytvorí `hello.py` s požadovanou funkciou a testovacím blokom.
- Voliteľne spustí `python3 hello.py`, aby overil výstup.
- Nahlási v chate, čo urobil, a výstup akéhokoľvek príkazu.

Mali by ste vidieť, ako sa v pracovnom priestore objaví nový súbor, a záverečná
správa agenta by mala opisovať zmenu, ktorú vykonal. Toto je chvíľa, na ktorú
sa to všetko oplatilo: agent napísal a spustil skutočný kód vo vašom
projektovom priečinku.

## 7. Kontrola a usmerňovanie agenta

Po dokončení kroku agentom skontrolujte jeho prácu pred prijatím ďalšieho kroku:

- **Zmeny súborov**: na zobrazenie presne toho, čo bolo pridané, zmenené alebo
  odstránené, použite prehliadač súborov pracovného priestoru alebo zobrazenie
  rozdielov (diff) agenta.
- **Výstup príkazov**: rozbaľte ľubovoľný príkaz, ktorý agent spustil, aby ste
  videli stdout, stderr a exit code.
- **Nadväzujúce kroky**: ak výsledok nie je taký, aký ste chceli, odpovedzte v
  tej istej konverzácii s opravou. Agent si zachová predchádzajúci kontext a
  pokračuje v práci na tých istých súboroch.

Ak napríklad test nevypísal očakávaný pozdrav, odpovedzte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent súbor znova prečíta, spustí príkaz, diagnostikuje problém a súbor znova
upraví — všetko v rámci tej istej konverzácie.
## Riešenie problémov

<!-- @os:linux -->
- **`agent-canvas` sa nenachádza v PATH:** preinštalujte pomocou
  `npm install -g @openhands/agent-canvas` a pred spustením `agent-canvas` z nového
  terminálu overte, že globálny adresár binárnych súborov npm je zahrnutý vo vašom PATH.
- **`npm install -g` zlyhá s chybou oprávnení:** nakonfigurujte globálny adresár npm
  vlastnený používateľom, potom znova otvorte terminál a znova nainštalujte Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Chýba `uv`:** nainštalujte ho z
  [návodu na inštaláciu uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používa `uv` na správu Python prostredia servera agenta.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` alebo `docker run` sa nedokáže pripojiť:** uistite sa, že Docker Desktop
  je spustený (jeho ikona veľryby je v systémovej lište) a že engine dokončil spúšťanie.
  `docker version` by mal vypísať sekciu Client aj Server.
- **Kontajner sa spustí, ale backend nikdy nie je v stave healthy:** prvé
  spustenie inicializuje Agent Server vnútri kontajnera; dajte mu minútu alebo
  dve, potom skontrolujte `docker logs <container>` kvôli chybám.
- **Kontajner sa nedokáže pripojiť k Lemonade:** kontajner sa pripája k hostiteľovi cez
  `host.docker.internal`. Overte, že Lemonade beží na Windows hostiteľovi pomocou
  `lemonade status`, a použite `http://host.docker.internal:13305/api/v1` ako
  základnú URL (Base URL) pri konfigurácii LLM.
<!-- @os:end -->

- **Rozhranie sa načíta, ale backend je nezdravý (unhealthy):** počkajte minútu alebo dve,
  kým sa dokončí spúšťanie servera agenta, a potom obnovte stránku. Ak zostáva nezdravý,
  reštartujte stack a skontrolujte logy kvôli chybám.
- **Požiadavky na chat Lemonade zlyhávajú s chybou pripojenia:** overte, že
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` je úspešné a že
  Lemonade stále obsluhuje model pomocou `lemonade status`.
- **Agent hlási chybu týkajúcu sa dĺžky kontextu alebo limitu tokenov:** začnite
  novú konverzáciu, aby agent nenosil so sebou nadmerne veľkú históriu. Ak sa to
  deje opakovane, reštartujte Lemonade s väčším `ctx_size`, ako je predvolených
  65536 (napríklad `ctx_size=131072`), ak to pamäť dovoľuje.
- **Agent produkuje nekvalitné alebo neúplné úpravy:** prepnite na väčší
  model v Lemonade, alebo zadajte agentovi menšiu, konkrétnejšiu úlohu a nechajte ju
  dokončiť pred požiadavkou na ďalšiu zmenu.

## Ďalšie kroky

- Vyskúšajte väčšiu úlohu v tom istom pracovnom priestore, napríklad pridanie súboru
  s jednotkovým testom alebo opravu známej chyby, a pred ponechaním zmeny skontrolujte
  rozdiel (diff) vytvorený agentom.
- Pripojte MCP server, napríklad GitHub alebo Slack, v sekcii **Customize**, aby
  agent mohol čítať issues alebo zverejňovať aktualizácie počas práce.
- Uložte si viacero LLM profilov (rýchly malý model a výkonnejší veľký model) a
  prepínajte medzi nimi pomocou `/model` priamo počas konverzácie.
- Prejdite na [OpenHands automatizácie](https://docs.openhands.dev/openhands/usage/automations/overview) a
  premeňte opakujúce sa vývojové cykly na naplánované alebo udalosťami spúšťané behy agenta.

## Zdroje

- [Dokumentácia OpenHands](https://docs.openhands.dev/)
- [Prehľad Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavenie Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profily a konfigurácia modelu](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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