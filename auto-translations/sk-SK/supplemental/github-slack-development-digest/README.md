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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prehľad

Vývojári trávia veľa času opakujúcimi sa malými slučkami: kontrolou označených pull requestov, odpovedaním na komentáre na GitHub, triedením nových issues, premieňaním vlákien v Slacku na poznámky zo standupu alebo následné kroky po incidente a sledovaním signálov o vydaniach alebo výskume.
Každá takáto slučka je síce dôverne známa, no stále si vyžaduje úsudok: zhromaždiť správny kontext, rozhodnúť, čo je dôležité, a zverejniť jasný update tam, kde tím už pracuje.

[OpenHands automatizácie](https://docs.openhands.dev/openhands/usage/automations/overview) premieňajú tieto slučky na naplánované alebo udalosťami vyvolané konverzácie agenta: behy, počas ktorých môže AI softvérový agent čítať kontext, volať nástroje a vytvárať update.
Zdieľané šablóny automatizácií v katalógu rozšírení OpenHands nasledujú tento vzor pri revízii pull requestov na GitHub, monitorovaní repozitárov, triedení issues v Linear, retrospektívach incidentov, denných súhrnoch v Slacku a výskumných prehľadoch: automatizácia sa „prebudí“, pomocou nakonfigurovaných integrácií, ako je GitHub alebo Slack, získa kontext, nad týmto kontextom uvažuje pomocou veľkého jazykového modelu (LLM) a zapíše výsledok späť.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokálna riadiaca rovina na vytváranie a testovanie týchto automatizácií.
V tomto návode spúšťa OpenHands Agent Server, backendový proces, ktorý vykonáva konverzácie agenta, a prepája agenta s externými službami, ako sú GitHub a Slack.

Aby pracovný postup zostal na vašom systéme AMD, agent komunikuje s lokálnym modelom, ktorý poskytuje Lemonade Server.
Lemonade sprístupňuje tento model prostredníctvom rozhrania API kompatibilného s OpenAI, takže Agent Canvas ho môže nakonfigurovať podobne ako vzdialený endpoint v štýle OpenAI, pričom model, prompt aj kontext pracovného postupu zostávajú lokálne.

V tomto návode vytvoríte jednu konkrétnu automatizáciu: naplánovaný denný prehľad vývoja z GitHub do Slacku.
Automatizácia používa GitHub na kontrolu nedávnej aktivity v repozitári, Slack na zverejnenie prehľadu, API volania Agent Canvas na konfiguráciu a testovanie automatizácie a Lemonade na lokálne spúšťanie LLM.

![Diagram architektúry zobrazujúci GitHub MCP, OpenHands automatizáciu, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na chatové požiadavky
- Ako spustiť Agent Canvas a nasmerovať jeho Agent Server na lokálny LLM
- Ako nainštalovať MCP servery (Model Context Protocol) pre GitHub a Slack prostredníctvom API rozhrania Agent Server
- Ako vytvoriť a spustiť naplánovanú OpenHands automatizáciu, ktorá zverejňuje denný prehľad vývoja do Slacku
- Ako riešiť najčastejšie zlyhania súvisiace s lokálnym modelom a automatizáciou

## Základné pojmy

| Pojem | Čo to je | Kde zapadá do tohto návodu |
| --- | --- | --- |
| Lemonade Server | Lokálna platforma na poskytovanie LLM navrhnutá pre hardvér AMD, ktorá sprístupňuje rozhranie API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands Agent Server | Backendový proces, ktorý vykonáva konverzácie agenta OpenHands. | Hostí agenta, jeho LLM profil a jeho MCP servery. |
| Agent Canvas | Lokálna riadiaca rovina pre OpenHands, ktorá spúšťa Agent Server a používateľské rozhranie na kontrolu behov agenta. | Spúšťa backendy a poskytuje API, ktoré voláte. |
| MCP server | Server Model Context Protocol, ktorý agentovi poskytuje nástroje pre externú službu, ako je GitHub alebo Slack. | Umožňuje agentovi čítať z GitHub a zapisovať do Slacku. |
| OpenHands automatizácia | Naplánovaná alebo udalosťami vyvolaná konverzácia agenta, ktorá získa kontext, uvažuje nad ním a niekam zapíše výsledok. | Prehľad z GitHub do Slacku, ktorý tu vytvárate. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Pracovné postupy s kódovacím agentom profitujú z väčšieho modelu a väčšieho kontextového okna.
> Použite minimálne 32 GB systémovej pamäte, pričom pri väčších GGUF modeloch sa odporúča 64 GB alebo viac.
<!-- @device:end -->

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Predpoklady

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Potrebujete:

- Lemonade Server nainštalovaný podľa štandardného [sprievodcu inštaláciou Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 alebo novší a `npm`, ktoré slúžia na inštaláciu publikovaného CLI nástroja Agent Canvas a na spúšťanie MCP serverov pomocou `npx`.
- `uv`, správcu balíkov pre Python, ktorý Agent Canvas používa na zostavenie prostredia Agent Server. Ak ešte nie je nainštalovaný, nainštalujte ho podľa [sprievodcu inštaláciou uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedávno publikovaný balík `@openhands/agent-canvas` so schémou riadeným nastavením agenta, `LLMSummarizingCondenserSettings.max_tokens` a podporou LLM `custom_tokenizer`.
- Balík Pythonu `transformers` dostupný v prostredí Agent Server. Je potrebný na počítanie tokenov podľa chatovej šablóny, keď je nastavené `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nainštalovaný a spustený. V systéme Windows beží stack Agent Canvas z publikovaného Docker obrazu, ktorý obsahuje Node.js, `uv`, `transformers` a balík `@openhands/agent-canvas`, takže ich netreba inštalovať na hostiteľský systém.
<!-- @os:end -->

- Token GitHub s právom čítania repozitára, ktorý chcete zhrnúť.
- Slack bot token (`xoxb-...`) s oprávneniami `chat:write` a prístupom na čítanie kanálov.
- ID tímu Slack (`T...`).
- ID kanála Slack (`C...`), kam sa má prehľad zverejniť.

Pred testovaním automatizácie pozvite aplikáciu Slack do cieľového kanála.
## Premenné použité v tejto príručke

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

Tieto dve premenné sa používajú v overovacích príkazoch nižšie.
Model, tokenizér a ostatné nastavenia LLM sa zadávajú priamo v používateľskom rozhraní Agent Canvas v neskorších krokoch, takže ich doslovné hodnoty sú uvedené priamo tam, kde ich potrebujete.

Nasledujúce hodnoty sa zadávajú do používateľského rozhrania Agent Canvas v neskorších krokoch.
Nastavte si ich tu, aby ste ich mohli skopírovať:

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

Použite explicitnú hodnotu `owner/repo` pre `GITHUB_REPO_FILTER`.
Všeobecné zástupné znaky pre celú organizáciu môžu vrátiť príliš veľa kontextu MCP pre lokálne modely.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Spustenie servera Lemonade

Spustite model z CLI nástroja Lemonade:

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

> **Vyberte model, ktorý vyhovuje vášmu hardvéru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je silný model pre tento pracovný postup, no vyžaduje veľký pamäťový fond.
> Ak má vaše zariadenie obmedzenú pamäť alebo GPU VRAM, vyberte menší model GGUF z knižnice modelov Lemonade a použite jeho ID modelu (a zodpovedajúci tokenizér) v celej tejto príručke.

> **Poznámka:** Prvý príkaz `lemonade run` stiahne model, ak ešte nie je prítomný, čo môže chvíľu trvať v závislosti od veľkosti modelu a vášho pripojenia.

Lemonade sprístupňuje rozhranie API kompatibilné s OpenAI na:

```text
http://127.0.0.1:13305/api/v1
```

Voliteľné: ak Agent Canvas alebo spúšťač automatizácie nie je na tom istom zariadení, publikujte koncový bod Lemonade cez zabezpečený tunel a použite HTTPS URL ako základnú URL adresu LLM.
[ngrok](https://ngrok.com/) sprístupňuje lokálny port internetu cez zabezpečenú HTTPS URL adresu; vyžaduje bezplatný účet ngrok a nahradíte `YOUR_NGROK_DOMAIN.ngrok-free.dev` vlastnou rezervovanou doménou:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Overenie lokálneho modelu

Potvrďte, že Lemonade dokáže obsluhovať vybraný model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Potom odošlite malú chat požiadavku:

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

Potom odošlite malú chat požiadavku:

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

Ak toto vráti pole `choices`, Lemonade je pripravený pre Agent Canvas.

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

## 3. Spustenie Agent Canvas

<!-- @os:linux -->
Nainštalujte publikovaný balík Agent Canvas a spustite celý zásobník:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ak globálna inštalácia npm zlyhá s chybou oprávnení, pozrite si nižšie uvedenú položku o riešení problémov s oprávneniami npm.

Predvolene sa Agent Canvas spúšťa na `http://localhost:8000`.
Otvorte túto URL adresu vo svojom prehliadači.
Port nie je nijako špecifický – ak je port 8000 už obsadený, zadajte ľubovoľný voľný port pomocou `--port` (alebo `-p`).
Predvolený lokálny backend by mal byť na domovskej obrazovke zobrazený ako funkčný (healthy).

> **Poznámka:** Prvé spustenie vytvorí Python prostredie servera Agent Server spravované nástrojom `uv`, takže môže chvíľu trvať, kým backend nahlási stav funkčný (healthy).

Príkaz `agent-canvas` spúšťa server agenta, backend automatizácie a webový frontend spoločne.
Na lokálne spustenie OpenHands potrebujete iba tento jeden príkaz.
Zvyšok tejto príručky konfiguruje všetko prostredníctvom používateľského rozhrania Agent Canvas vo vašom prehliadači.
<!-- @os:end -->

<!-- @os:windows -->
V systéme Windows spustite publikovaný obraz kontajnera Agent Canvas pomocou Docker Desktop.
Obraz obsahuje Agent Server, backend automatizácie a webový frontend, takže na hostiteľovi nemusíte inštalovať Node.js, `uv` ani CLI.

Najskôr vytvorte priečinky pre konfiguráciu a pracovný priestor, ktoré kontajner pripojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stiahnite publikovaný obraz (asi 6 GB; je verejný, takže nie je potrebné prihlásenie):

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

Otvorte `http://localhost:8000/canvas` vo svojom prehliadači.
Ak je port 8000 už obsadený, namapujte iný hostiteľský port, napríklad `-p 8080:8000`, a namiesto toho otvorte `http://localhost:8080/canvas`.

> **Poznámka:** Prvé spustenie vytvorí prostredie Agent Server vnútri kontajnera, takže môže chvíľu trvať, kým backend nahlási stav funkčný (healthy).

Pripojenie `.openhands` uchováva váš profil LLM, servery MCP a automatizácie aj po reštartoch kontajnera.
Zvyšok tejto príručky konfiguruje všetko prostredníctvom používateľského rozhrania Agent Canvas vo vašom prehliadači na adrese `http://localhost:8000/canvas`.
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
## 4. Konfigurácia lokálneho LLM v používateľskom rozhraní

Pri prvom spustení Agent Canvas otvorí sprievodcu nastavením.
V tomto sprievodcovi:

1. Ponechajte **OpenHands** vybraté ako agenta a kliknite na **Next**.
2. Na obrazovke **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do poľa **API Key** zadajte ľubovoľný neprázdny zástupný text, napríklad `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands potrebuje nejakú hodnotu na odoslanie.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server beží vo vnútri kontajnera, preto nastavte **Base URL** na `http://host.docker.internal:13305/api/v1` namiesto `http://127.0.0.1:13305/api/v1`.
> Z vnútra kontajnera je `127.0.0.1` samotný kontajner; `host.docker.internal` sa pripája k Lemonade bežiacemu na hostiteľskom systéme Windows a Docker Desktop tento názov hostiteľa poskytuje automaticky.
<!-- @os:end -->

Polia pripojenia by mali vyzerať takto.
Pole API kľúča je v používateľskom rozhraní maskované.

![Prvotné rozšírené nastavenia LLM v Agent Canvas s modelom Lemonade a lokálnou základnou URL adresou](assets/01-llm-advanced-settings.png)

Potom vyberte **All** a nastavte ďalšie polia pre lokálny model:

1. Prejdite na **Custom Tokenizer** a nastavte ho na `Qwen/Qwen3.6-35B-A3B`.
2. Prejdite na **LiteLLM Extra Body** a nastavte ho na `{"enable_thinking": true}`.
3. Kliknite na **Next**.

![Karta All pri prvotnom nastavení LLM v Agent Canvas s vlastným tokenizátorom Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta All pri prvotnom nastavení LLM v Agent Canvas s nakonfigurovaným LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavenia LLM by mali zobrazovať:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` hovorí LiteLLM, aby voči koncovému bodu Lemonade použil formátovanie požiadaviek kompatibilné s OpenAI.
Vlastný tokenizátor je pôvodný tokenizátor Hugging Face pre model GGUF; umožňuje nástroju OpenHands počítať tokeny podľa rovnakej chatovej šablóny, akú vidí lokálny model server.
Súčasný formulár prvotného nastavenia LLM nezobrazuje nastavenia kondenzátora.
Ak vaša zostava Agent Canvas neskôr sprístupní nastavenia kondenzátora v časti **Settings > LLM**, použite `llm_summarizing` a nastavte maximálny počet tokenov pod úrovňou kontextového okna Lemonade, napríklad `56000`.

## 5. Inštalácia MCP serverov pre GitHub a Slack

V používateľskom rozhraní Agent Canvas otvorte **Customize** (alebo **Settings > MCP**) a pridajte MCP servery, ktoré agentovi poskytnú nástroje pre GitHub a Slack.
Hodnoty tokenov sa odosielajú iba na váš lokálny Agent Server a ukladajú sa ako šifrované nastavenia.

<!-- @os:windows -->
> **Windows (Docker):** príkazy MCP servera `npx` uvedené nižšie bežia vo vnútri kontajnera, ktorý už obsahuje Node.js, takže na hostiteľskom systéme sa nič ďalšie neinštaluje.
> Keďže `.openhands` je pripojený, MCP servery a ich tokeny zostávajú zachované aj po reštartovaní kontajnera.
<!-- @os:end -->

### MCP server pre GitHub

Pridajte nový MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš token GitHub |

Použite token GitHub s právom na čítanie repozitára, ktorý chcete zhrnúť.

### MCP server pre Slack

Pridajte druhý MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vášho kanála pre súhrn |

Nastavte `SLACK_CHANNEL_IDS` na ID kanála pre súhrn (rovnaká hodnota ako `SLACK_DIGEST_CHANNEL`), aby agent nemusel prechádzať každým kanálom Slack.

Po pridaní oboch serverov použite tlačidlo **Test** na každom z nich, aby ste potvrdili, že sa pripájajú a ponúkajú nástroje.
Server pre GitHub by mal zobraziť zoznam nástrojov pre GitHub a server pre Slack by mal zobraziť zoznam nástrojov pre Slack.

![Stránka MCP v Agent Canvas s nainštalovanými servermi pre GitHub a Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Vytvorenie automatizácie súhrnu

V používateľskom rozhraní Agent Canvas otvorte stránku **Automations** a vytvorte novú automatizáciu:

1. Zvoľte **Create automation** a vyberte typ **Prompt preset**.
2. Nastavte **Name** na `GitHub Development Digest to Slack`.
3. Nastavte **Prompt** na nasledujúci text, pričom nahraďte zástupné symboly repozitára a kanála svojimi hodnotami:

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

4. Nastavte **Trigger** na **Cron** s rozvrhom `0 9 * * 1-5` (9:00 v pracovných dňoch) a nastavte **Timezone** na vaše časové pásmo, napríklad `America/New_York`.
5. Nastavte **Timeout** na `900` sekúnd.
6. Uložte automatizáciu.

Stránka s podrobnosťami automatizácie zobrazí novú automatizáciu spolu s jej cron spúšťačom a vygenerovaným vstupným bodom prompt presetu.

![Podrobnosti automatizácie v Agent Canvas po vytvorení](assets/05-automation-created.png)
## 7. Otestujte automatizáciu

Na stránke s podrobnosťami automatizácie v rozhraní Agent Canvas UI:

1. Kliknite na **Run now** (alebo **Dispatch**) na okamžité jednorazové spustenie automatizácie.
2. Sledujte zoznam spustení na tej istej stránke. Najnovšie spustenie by malo prejsť do stavu `COMPLETED`.
3. Otvorte svoj cieľový Slack kanál. Mal by obsahovať vygenerovaný súhrn.

Nemusíte čakať na spustenie cron plánu—**Run now** spustí beh na požiadanie, takže si môžete overiť, že prompt, pripojenia MCP a odosielanie na Slack fungujú ešte predtým, než sa spoľahnete na plán.

![Automatizačné spustenie v Agent Canvas úspešne dokončené](assets/06-automation-run-completed.png)

![Slack kanál zobrazujúci vygenerovaný súhrn OpenHands](assets/07-slackbot-message.png)

## Riešenie problémov

<!-- @os:windows -->
- **Port 8000 v Docker je už používaný:** namapujte iný hostiteľský port, napríklad `docker run ... -p 8080:8000 ...`, a otvorte `http://localhost:8080/canvas`.
- **`docker pull` zlyhá s chybou prihlasovacích údajov** (napríklad „A specified logon session does not exist“): spustite pull z interaktívnej relácie Windows alebo si obraz vopred stiahnite (pre-pull). Obraz je verejný, takže `docker login` nie je potrebný.
- **Rozhranie sa načíta, ale backend je nefunkčný:** pri prvom spustení sa vnútri kontajnera zostavuje prostredie Agent Server. Počkajte minútu a obnovte stránku, potom skontrolujte priebeh pomocou `docker logs <container>`.
- **Agent Canvas sa nedokáže pripojiť k Lemonade z kontajnera:** nastavte **Base URL** pre LLM na `http://host.docker.internal:13305/api/v1` (nie `127.0.0.1`) a overte, že Lemonade beží na hostiteľskom systéme Windows.
<!-- @os:end -->

- **Lemonade nebeží:** reštartujte ho príkazom `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a následne znova spustite kontrolu stavu.
- **`npm install -g` zlyhá s chybou oprávnení:** na Linuxe alebo WSL nakonfigurujte globálny npm adresár vlastnený používateľom, pridajte ho do štartovacieho súboru shellu a potom znova nainštalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ak používate `zsh`, pridajte rovnaký riadok `export PATH=...` namiesto do `~/.bashrc` do `~/.zshrc`.
- **Agent Canvas odmietne nastavenia LLM po nastavení `custom_tokenizer`:** nainštalujte `transformers` do Python prostredia Agent Server, v prípade potreby reštartujte Agent Canvas a skúste znova uložiť nastavenia LLM. OpenHands vyžaduje Transformers na načítanie šablóny tokenizéra pre chat, keď je nastavené `custom_tokenizer`.
- **Agent Canvas sa nedokáže pripojiť k Lemonade:** overte `curl -fsS "${LEMONADE_BASE_URL}/health"` a potvrďte, že základná URL adresa zadaná vo formulári LLM pri prvom použití alebo v **Settings > LLM** zodpovedá bežiacemu lokálnemu koncovému bodu alebo HTTPS tunelu.
- **Nastavenia LLM sa neuložili:** uistite sa, že ste po zadaní hodnôt klikli na **Next**. Znova otvorte **Settings > LLM** a overte, že sa hodnoty zachovali.
- **GitHub MCP nevidí súkromné repozitáre:** potvrďte, že token GitHub má prístup na čítanie k cieľovému repozitáru a že tlačidlo **Test** v časti **Customize** pre MCP zobrazuje nástroje GitHub.
- **Slack dokáže čítať kanály, ale nedokáže na ne odosielať:** pozvite aplikáciu Slack do cieľového kanála a potvrďte, že bot má `chat:write`.
- **Automatizácia zobrazuje príliš veľa Slack kanálov:** použite identifikátor Slack kanála a nastavte `SLACK_CHANNEL_IDS` na serveri Slack MCP v časti **Customize**.
- **Spustenie automatizácie zlyhá alebo presiahne kontext:** potvrďte, že Lemonade bol spustený s `ctx_size=65536`, potvrďte, že LLM v OpenHands má nastavené `custom_tokenizer`, a použite explicitný repozitár s výsledkovými sadami GitHub obmedzenými na 3 až 5 položiek. Ak vaša verzia Agent Canvas obsahuje nastavenia kondenzéra, nastavte maximálny počet tokenov kondenzéra pod úroveň kontextového okna Lemonade.

## Ďalšie kroky

- Pridajte týždenný súhrn len pre vydania (release-only digest).
- Pridajte automatizáciu spúšťanú udalosťami GitHub pre rýchlejšie upozornenia na PR alebo push.
- Smerujte rovnaký súhrn do Notion, Linear alebo iného nástroja podporovaného cez MCP.

## Zdroje

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentácia Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitár rozšírení OpenHands](https://github.com/OpenHands/extensions)
- [Servery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Balík Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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