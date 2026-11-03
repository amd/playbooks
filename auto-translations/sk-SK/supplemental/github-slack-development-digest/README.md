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

Vývojári trávia veľa času malými opakujúcimi sa slučkami: kontrolou označených pull requestov, odpovedaním na komentáre na GitHub, triedením nových issues, premenou vlákien v Slacku na poznámky zo standupov alebo následné kroky po incidentoch a sledovaním signálov o vydaniach alebo výskume.
Každá slučka je známa, no napriek tomu vyžaduje úsudok: zhromaždiť správny kontext, rozhodnúť, čo je dôležité, a zverejniť jasnú aktualizáciu tam, kde tím už pracuje.

[Automatizácie OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) menia tieto slučky na naplánované alebo udalosťami spúšťané konverzácie agenta: behy, počas ktorých AI softvérový agent môže čítať kontext, volať nástroje a vytvárať aktualizáciu.
Zdieľané šablóny automatizácií v katalógu rozšírení OpenHands nasledujú tento vzor pre kontrolu pull requestov na GitHub, monitorovanie repozitárov, triedenie issues v Linear, retrospektívy incidentov, digesty standupov v Slacku a výskumné súhrny: automatizácia sa prebudí, použije nakonfigurované integrácie ako GitHub alebo Slack na získanie kontextu, uvažuje nad týmto kontextom pomocou veľkého jazykového modelu (LLM) a zapíše späť výsledok.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokálna riadiaca rovina na vytváranie a testovanie týchto automatizácií.
V tomto sprievodcovi spúšťa OpenHands Agent Server, backendový proces, ktorý vykonáva konverzácie agenta, a prepája agenta s externými službami, ako sú GitHub a Slack.

Aby pracovný postup zostal na vašom systéme AMD, agent komunikuje s lokálnym modelom obsluhovaným cez Lemonade Server.
Lemonade sprístupňuje tento model prostredníctvom API kompatibilného s OpenAI, takže Agent Canvas ho môže nakonfigurovať ako vzdialený koncový bod v štýle OpenAI, pričom model, prompt a kontext pracovného postupu zostávajú lokálne.

V tomto sprievodcovi vytvoríte jednu konkrétnu automatizáciu: naplánovaný vývojový digest z GitHub do Slacku.
Používa GitHub na kontrolu nedávnej aktivity v repozitári, Slack na zverejnenie digestu, volania API Agent Canvas na konfiguráciu a testovanie automatizácie a Lemonade na lokálne spúšťanie LLM.

![Diagram architektúry zobrazujúci GitHub MCP, automatizáciu OpenHands, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na chatové požiadavky
- Ako spustiť Agent Canvas a nasmerovať jeho Agent Server na lokálny LLM
- Ako nainštalovať servery GitHub a Slack Model Context Protocol (MCP) prostredníctvom API Agent Servera
- Ako vytvoriť a spustiť naplánovanú automatizáciu OpenHands, ktorá zverejní vývojový digest na Slacku
- Ako riešiť najčastejšie zlyhania lokálneho modelu a automatizácie

## Základné pojmy

| Pojem | Čo to je | Kde sa hodí v tomto sprievodcovi |
| --- | --- | --- |
| Lemonade Server | Platforma na lokálne obsluhovanie LLM postavená pre hardvér AMD, ktorá sprístupňuje API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands Agent Server | Backendový proces, ktorý vykonáva konverzácie agenta OpenHands. | Hostí agenta, jeho profil LLM a jeho servery MCP. |
| Agent Canvas | Lokálna riadiaca rovina pre OpenHands, ktorá spúšťa Agent Server a rozhranie na kontrolu behov agenta. | Spúšťa backendy a poskytuje API, ktoré voláte. |
| MCP server | Server Model Context Protocol, ktorý dáva agentovi nástroje pre externú službu, ako je GitHub alebo Slack. | Umožňuje agentovi čítať z GitHub a zapisovať do Slacku. |
| Automatizácia OpenHands | Naplánovaná alebo udalosťami spúšťaná konverzácia agenta, ktorá získa kontext, uvažuje nad ním a niekam zapíše výsledok. | Digest z GitHub do Slacku, ktorý tu vytvoríte. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Pracovné postupy s kódovacím agentom profitujú z väčšieho modelu a väčšieho kontextového okna.
> Použite minimálne 32 GB systémovej pamäte, pričom pre väčšie modely GGUF uprednostnite 64 GB alebo viac.
<!-- @device:end -->

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola softvérových aktualizácií

<!-- @require:software-update -->
<!-- @device:end -->

## Predpoklady

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Budete potrebovať:

- Lemonade Server nainštalovaný podľa štandardného [sprievodcu inštaláciou Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 alebo novší a `npm`, používané na inštaláciu publikovaného CLI Agent Canvas a spúšťanie MCP serverov pomocou `npx`.
- `uv`, správca balíkov Python, ktorý Agent Canvas používa na zostavenie prostredia Agent Servera. Ak ešte nie je nainštalovaný, nainštalujte ho podľa [sprievodcu inštaláciou uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedávno publikovaný balík `@openhands/agent-canvas` so schémou riadenými nastaveniami agenta, `LLMSummarizingCondenserSettings.max_tokens` a podporou `custom_tokenizer` pre LLM.
- Balík Pythonu `transformers` dostupný v prostredí Agent Servera. Je vyžadovaný na počítanie tokenov chatovej šablóny, keď je nastavené `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nainštalovaný a spustený. V systéme Windows beží celý stack Agent Canvas z publikovaného obrazu Docker, ktorý obsahuje Node.js, `uv`, `transformers` a balík `@openhands/agent-canvas`, takže ich nemusíte inštalovať na hostiteľský systém.
<!-- @os:end -->

- Token GitHub s právom čítania do repozitára, ktorý chcete zhrnúť.
- Token bota Slack (`xoxb-...`) s právami `chat:write` a čítania kanálov.
- ID tímu Slack (`T...`).
- ID kanálu Slack (`C...`), kam sa má digest zverejniť.

Pred testovaním automatizácie pozvite aplikáciu Slack do cieľového kanála.
## Variables Used v tomto scenári

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
Model, tokenizér a ďalšie nastavenia LLM sa v neskorších krokoch zadávajú priamo v používateľskom rozhraní Agent Canvas, takže ich konkrétne hodnoty sú uvedené priamo tam, kde ich potrebujete.

Nasledujúce hodnoty sa v neskorších krokoch zadávajú do používateľského rozhrania Agent Canvas.
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
Širokie zástupné znaky pre organizáciu môžu vrátiť príliš veľa kontextu MCP pre lokálne modely.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Spustenie servera Lemonade

Spustite model z rozhrania Lemonade CLI:

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

> **Vyberte model, ktorý zodpovedá vášmu hardvéru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je pre tento pracovný postup silný model, no vyžaduje veľký pamäťový priestor.
> Ak má vaše zariadenie obmedzenú pamäť alebo GPU VRAM, vyberte si menší model GGUF z knižnice modelov Lemonade a použite jeho ID modelu (a zodpovedajúci tokenizér) v celom tomto scenári.

> **Poznámka:** Prvý príkaz `lemonade run` model stiahne, ak ešte nie je stiahnutý, čo môže chvíľu trvať v závislosti od veľkosti modelu a rýchlosti vášho pripojenia.

Lemonade sprístupňuje rozhranie API kompatibilné s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

Voliteľné: ak Agent Canvas alebo automatizačný runner nie sú na tom istom počítači, publikujte koncový bod Lemonade prostredníctvom zabezpečeného tunela a ako základnú adresu URL LLM použite HTTPS adresu URL.
[ngrok](https://ngrok.com/) sprístupňuje lokálny port na internete prostredníctvom zabezpečenej HTTPS adresy URL; vyžaduje bezplatný účet ngrok a `YOUR_NGROK_DOMAIN.ngrok-free.dev` nahradíte vlastnou rezervovanou doménou:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Overenie lokálneho modelu

Potvrďte, že Lemonade dokáže obslúžiť vybraný model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Následne odošlite malú požiadavku chatu:

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

Následne odošlite malú požiadavku chatu:

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

Ak sa vráti pole `choices`, Lemonade je pripravený pre Agent Canvas.

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

Ak globálna inštalácia npm zlyhá s chybou oprávnení, pozrite si nižšie uvedenú položku riešenia problémov s oprávneniami npm.

Predvolene sa Agent Canvas spúšťa na adrese `http://localhost:8000`.
Otvorte túto adresu URL vo svojom prehliadači.
Port nie je nijako špeciálny – ak je 8000 už používaný, zadajte akýkoľvek voľný port pomocou `--port` (alebo `-p`).
Predvolený lokálny backend by sa mal na domovskej obrazovke zobraziť ako funkčný (healthy).

> **Poznámka:** Pri prvom spustení sa vytvára prostredie Python spravované nástrojom `uv` pre Agent Server, takže môže chvíľu trvať, kým backend nahlási stav funkčný.

Príkaz `agent-canvas` spúšťa agent server, automatizačný backend a webový frontend spoločne.
Na lokálne spustenie OpenHands potrebujete iba tento jeden príkaz.
Zvyšná časť tohto scenára konfiguruje všetko prostredníctvom používateľského rozhrania Agent Canvas vo vašom prehliadači.
<!-- @os:end -->

<!-- @os:windows -->
V systéme Windows spustite publikovaný obraz kontajnera Agent Canvas pomocou Docker Desktop.
Obraz obsahuje Agent Server, automatizačný backend a webový frontend, takže na hostiteľovi nemusíte inštalovať Node.js, `uv` ani CLI.

Najprv vytvorte priečinky pre konfiguráciu a pracovný priestor, ktoré kontajner pripojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stiahnite publikovaný obraz (približne 6 GB; je verejný, takže prihlásenie nie je potrebné):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Následne spustite zásobník:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otvorte `http://localhost:8000/canvas` vo svojom prehliadači.
Ak je port 8000 už používaný, namapujte iný port hostiteľa, napríklad `-p 8080:8000`, a namiesto toho otvorte `http://localhost:8080/canvas`.

> **Poznámka:** Pri prvom spustení sa v rámci kontajnera vytvára prostredie Agent Server, takže môže chvíľu trvať, kým backend nahlási stav funkčný.

Pripojenie `.openhands` uchováva váš profil LLM, servery MCP a automatizácie aj po reštartovaní kontajnera.
Zvyšná časť tohto scenára konfiguruje všetko prostredníctvom používateľského rozhrania Agent Canvas vo vašom prehliadači na adrese `http://localhost:8000/canvas`.
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

Pri prvom spustení sa v Agent Canvas otvorí sprievodca nastavením (onboarding flow).
V tomto sprievodcovi:

1. Ponechajte **OpenHands** vybraný ako agenta a kliknite na **Next**.
2. V časti **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do poľa **API Key** zadajte ľubovoľný neprázdny zástupný text, napríklad `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands potrebuje nejakú hodnotu na odoslanie.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server beží vnútri kontajnera, takže nastavte **Base URL** na `http://host.docker.internal:13305/api/v1` namiesto `http://127.0.0.1:13305/api/v1`.
> Zvnútra kontajnera je `127.0.0.1` samotný kontajner; `host.docker.internal` smeruje k Lemonade bežiacemu na hostiteľovi Windows a Docker Desktop poskytuje tento hostname automaticky.
<!-- @os:end -->

Polia pripojenia by mali vyzerať takto.
Pole API key je v používateľskom rozhraní maskované.

![Prvotné nastavenia Agent Canvas LLM Advanced s modelom Lemonade a lokálnou base URL](assets/01-llm-advanced-settings.png)

Potom vyberte **All** a nastavte ďalšie polia pre lokálny model:

1. Prejdite na **Custom Tokenizer** a nastavte ho na `Qwen/Qwen3.6-35B-A3B`.
2. Prejdite na **LiteLLM Extra Body** a nastavte ho na `{"enable_thinking": true}`.
3. Kliknite na **Next**.

![Karta Agent Canvas prvotné LLM All s vlastným tokenizátorom Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta Agent Canvas prvotné LLM All s nakonfigurovaným LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavenia LLM by mali zobrazovať:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` hovorí LiteLLM, aby použil formátovanie požiadaviek kompatibilné s OpenAI voči koncovému bodu Lemonade.
Vlastný tokenizátor je pôvodný tokenizátor Hugging Face pre model GGUF; umožňuje OpenHands počítať rovnaké tokeny chat-template, aké vidí lokálny server modelu.
Súčasný formulár prvotného LLM nezobrazuje nastavenia condenser.
Ak vaše zostavenie Agent Canvas neskôr sprístupní nastavenia condenser v časti **Settings > LLM**, použite `llm_summarizing` a nastavte maximálny počet tokenov pod kontextovým oknom Lemonade, napríklad `56000`.

## 5. Inštalácia MCP serverov pre GitHub a Slack

V používateľskom rozhraní Agent Canvas otvorte **Customize** (alebo **Settings > MCP**) a pridajte MCP servery, ktoré agentovi poskytnú nástroje pre GitHub a Slack.
Hodnoty tokenov sa odosielajú iba vášmu lokálnemu Agent Server a uchovávajú sa ako zašifrované nastavenia.

<!-- @os:windows -->
> **Windows (Docker):** nižšie uvedené príkazy MCP servera `npx` bežia vnútri kontajnera, ktorý už obsahuje Node.js, takže na hostiteľa sa nič naviac neinštaluje.
> Keďže `.openhands` je pripojený, MCP servery a ich tokeny zostávajú zachované aj po reštarte kontajnera.
<!-- @os:end -->

### MCP server pre GitHub

Pridajte nový MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš GitHub token |

Použite GitHub token s právom čítania pre repozitár, ktorý chcete zhrnúť.

### MCP server pre Slack

Pridajte druhý MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vášho digest kanála |

Nastavte `SLACK_CHANNEL_IDS` na ID digest kanála (rovnaká hodnota ako `SLACK_DIGEST_CHANNEL`), aby agent nemusel prechádzať každý kanál Slack.

Po pridaní oboch serverov použite tlačidlo **Test** na každom z nich, aby ste potvrdili, že sa pripája a inzeruje nástroje.
Server GitHub by mal zobraziť zoznam nástrojov GitHub a server Slack by mal zobraziť zoznam nástrojov Slack.

![Stránka MCP v Agent Canvas s nainštalovanými servermi GitHub a Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Vytvorenie automatizácie digestu

V používateľskom rozhraní Agent Canvas otvorte stránku **Automations** a vytvorte novú automatizáciu:

1. Zvoľte **Create automation** a vyberte typ **Prompt preset**.
2. Nastavte **Name** na `GitHub Development Digest to Slack`.
3. Nastavte **Prompt** na nasledujúci text, pričom nahraďte zástupné hodnoty repozitára a kanála vlastnými hodnotami:

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

4. Nastavte **Trigger** na **Cron** s plánom `0 9 * * 1-5` (9:00 v pracovných dňoch) a nastavte **Timezone** na vaše časové pásmo, napríklad `America/New_York`.
5. Nastavte **Timeout** na `900` sekúnd.
6. Uložte automatizáciu.

Stránka s podrobnosťami automatizácie zobrazuje novú automatizáciu s jej cron triggerom a vygenerovaným entrypointom prompt-preset.

![Podrobnosti automatizácie v Agent Canvas po vytvorení](assets/05-automation-created.png)
## 7. Otestujte automatizáciu

Na stránke s podrobnosťami automatizácie v Agent Canvas UI:

1. Kliknite na **Run now** (alebo **Dispatch**) na okamžité jednorazové spustenie automatizácie.
2. Sledujte zoznam spustení na tej istej stránke. Najnovšie spustenie by malo prejsť do stavu `COMPLETED`.
3. Otvorte váš cieľový kanál Slack. Mal by obsahovať vygenerovaný súhrn.

Nemusíte čakať na spustenie podľa cron plánu—**Run now** spustí beh na požiadanie, takže si môžete overiť, že prompt, MCP pripojenia a odosielanie do Slacku fungujú ešte predtým, ako sa spoľahnete na plánované spúšťanie.

![Automatizácia Agent Canvas úspešne dokončená](assets/06-automation-run-completed.png)

![Kanál Slack zobrazujúci vygenerovaný súhrn OpenHands](assets/07-slackbot-message.png)

## Riešenie problémov

<!-- @os:windows -->
- **Port 8000 Dockeru je už používaný:** namapujte iný port hostiteľa, napríklad `docker run ... -p 8080:8000 ...`, a otvorte `http://localhost:8080/canvas`.
- **`docker pull` zlyhá s chybou prihlasovacích údajov** (napríklad „A specified logon session does not exist“): spustite pull z interaktívnej relácie Windows alebo si obraz vopred stiahnite. Obraz je verejný, takže `docker login` nie je potrebný.
- **Rozhranie sa načíta, ale backend je nefunkčný:** pri prvom spustení sa v kontajneri buduje prostredie Agent Server. Počkajte minútu a obnovte stránku, potom skontrolujte `docker logs <container>` kvôli priebehu.
- **Agent Canvas sa nemôže z kontajnera pripojiť k Lemonade:** nastavte **Base URL** LLM na `http://host.docker.internal:13305/api/v1` (nie `127.0.0.1`) a overte, že Lemonade beží na hostiteľskom systéme Windows.
<!-- @os:end -->

- **Lemonade nefunguje:** reštartujte ho príkazom `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a potom znova spustite kontrolu funkčnosti.
- **`npm install -g` zlyhá s chybou oprávnení:** na Linuxe alebo WSL nastavte globálny adresár npm vo vlastníctve používateľa, pridajte ho do súboru na spustenie shellu a potom znova nainštalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Ak používate `zsh`, pridajte rovnaký riadok `export PATH=...` namiesto do `~/.bashrc` do `~/.zshrc`.
- **Agent Canvas odmieta nastavenia LLM po nastavení `custom_tokenizer`:** nainštalujte `transformers` do prostredia Python servera Agent Server, v prípade potreby reštartujte Agent Canvas a skúste znova uložiť nastavenia LLM. OpenHands vyžaduje Transformers na načítanie šablóny chatu tokenizátora, keď je nastavený `custom_tokenizer`.
- **Agent Canvas sa nemôže pripojiť k Lemonade:** overte `curl -fsS "${LEMONADE_BASE_URL}/health"` a potvrďte, že základná URL adresa zadaná vo formulári LLM pri prvom použití alebo v **Settings > LLM** zodpovedá bežiacemu lokálnemu koncovému bodu alebo HTTPS tunelu.
- **Nastavenia LLM sa neuložili:** uistite sa, že ste po zadaní hodnôt klikli na **Next**. Znova otvorte **Settings > LLM** a overte, či sa hodnoty uložili.
- **GitHub MCP nevidí súkromné repozitáre:** overte, že token GitHub má prístup na čítanie k cieľovému repozitáru a že tlačidlo **Test** MCP v **Customize** hlási dostupné nástroje GitHub.
- **Slack dokáže čítať kanály, ale nedokáže do nich odosielať príspevky:** pozvite aplikáciu Slack do cieľového kanála a overte, že bot má oprávnenie `chat:write`.
- **Automatizácia zobrazuje príliš veľa kanálov Slack:** použite ID kanála Slack a nastavte `SLACK_CHANNEL_IDS` na serveri Slack MCP v **Customize**.
- **Spustenie automatizácie zlyhá alebo prekročí kontext:** overte, že Lemonade bol spustený s `ctx_size=65536`, potvrďte, že LLM OpenHands má nastavené `custom_tokenizer`, a použite explicitný repozitár s výsledkami GitHub obmedzenými na 3 až 5 položiek. Ak vaša zostava Agent Canvas obsahuje nastavenia kondenzátora (condenser), nastavte maximálny počet tokenov kondenzátora pod hodnotu kontextového okna Lemonade.

## Ďalšie kroky

- Pridajte týždenný súhrn iba pre vydania (release-only digest).
- Pridajte automatizáciu spúšťanú udalosťou GitHub pre rýchlejšie upozornenia na PR alebo push.
- Presmerujte rovnaký súhrn do Notion, Linear alebo iného nástroja podporovaného MCP.

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