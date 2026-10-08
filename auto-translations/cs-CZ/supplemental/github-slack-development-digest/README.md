<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Přehled

Vývojáři tráví spoustu času malými opakujícími se smyčkami: kontrolou označených pull requestů, odpovídáním na komentáře na GitHub, tříděním nových issues, přeměnou Slack vláken na poznámky ze standupu nebo následné kroky po incidentu a sledováním signálů z vydání nebo výzkumu.
Každá z těchto smyček je důvěrně známá, přesto vyžaduje úsudek: shromáždit správný kontext, rozhodnout, co je důležité, a zveřejnit jasnou aktualizaci tam, kde tým již pracuje.

[OpenHands automatizace](https://docs.openhands.dev/openhands/usage/automations/overview) mění tyto smyčky v naplánované nebo událostmi spouštěné konverzace agenta: běhy, ve kterých může AI softwarový agent číst kontext, volat nástroje a vytvářet aktualizaci.
Sdílené šablony automatizací v katalogu rozšíření OpenHands se řídí tímto vzorem pro kontrolu pull requestů na GitHub, monitorování repozitářů, třídění issues v Linear, retrospektivy incidentů, Slack standup souhrny a výzkumné přehledy: automatizace se probudí, použije nakonfigurované integrace, jako je GitHub nebo Slack, k získání kontextu, uvažuje nad tímto kontextem pomocí velkého jazykového modelu (LLM) a zapíše výsledek zpět.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokální řídicí rovina pro vytváření a testování těchto automatizací.
V tomto playbooku spouští OpenHands Agent Server, backendový proces, který vykonává konverzace agenta, a propojuje agenta s externími službami, jako jsou GitHub a Slack.

Aby pracovní postup zůstal na vašem systému AMD, agent komunikuje s lokálním modelem obsluhovaným pomocí Lemonade Server.
Lemonade zpřístupňuje tento model prostřednictvím API kompatibilního s OpenAI, takže Agent Canvas jej může nakonfigurovat jako vzdálený endpoint ve stylu OpenAI, zatímco model, prompt i kontext pracovního postupu zůstávají lokálně.

V tomto playbooku vytvoříte jednu konkrétní automatizaci: naplánovaný vývojářský přehled z GitHub do Slack.
Používá GitHub ke kontrole nedávné aktivity v repozitáři, Slack ke zveřejnění přehledu, API volání Agent Canvas ke konfiguraci a testování automatizace a Lemonade ke spuštění LLM lokálně.

![Diagram architektury zobrazující GitHub MCP, OpenHands automatizaci, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové požadavky
- Jak spustit Agent Canvas a nasměrovat jeho Agent Server na lokální LLM
- Jak nainstalovat servery GitHub a Slack Model Context Protocol (MCP) prostřednictvím API Agent Server
- Jak vytvořit a spustit naplánovanou OpenHands automatizaci, která zveřejní vývojářský přehled na Slack
- Jak řešit nejčastější problémy s lokálním modelem a automatizací

## Základní koncepty

| Koncept | Co to je | Kde zapadá do tohoto playbooku |
| --- | --- | --- |
| Lemonade Server | Lokální platforma pro obsluhu LLM postavená pro hardware AMD, která zpřístupňuje API kompatibilní s OpenAI. Vaše data nikdy neopustí váš počítač. | Spouští model, který pohání agenta. |
| OpenHands Agent Server | Backendový proces, který vykonává konverzace agenta OpenHands. | Hostuje agenta, jeho profil LLM a jeho MCP servery. |
| Agent Canvas | Lokální řídicí rovina pro OpenHands, která spouští Agent Server a uživatelské rozhraní pro kontrolu běhů agenta. | Spouští backendy a poskytuje API, které voláte. |
| MCP server | Server Model Context Protocol, který agentovi poskytuje nástroje pro externí službu, jako je GitHub nebo Slack. | Umožňuje agentovi číst z GitHub a zapisovat do Slack. |
| OpenHands automatizace | Naplánovaná nebo událostmi spouštěná konverzace agenta, která získá kontext, uvažuje nad ním a někam zapíše výsledek. | Přehled z GitHub do Slack, který zde vytváříte. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Workflowy s kódovacím agentem těží z většího modelu a většího kontextového okna.
> Použijte alespoň 32 GB systémové paměti a pro větší modely GGUF upřednostněte 64 GB nebo více.
<!-- @device:end -->

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Předpoklady

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Potřebujete:

- Nainstalovaný Lemonade Server podle standardního [návodu k instalaci Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 nebo novější a `npm`, používané k instalaci publikovaného CLI Agent Canvas a ke spouštění MCP serverů pomocí `npx`.
- `uv`, správce balíčků Pythonu, který Agent Canvas používá k sestavení prostředí Agent Server. Pokud ještě není nainstalován, nainstalujte jej podle [návodu k instalaci uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedávno publikovaný balíček `@openhands/agent-canvas` se schématem řízeným nastavením agenta, `LLMSummarizingCondenserSettings.max_tokens` a podporou `custom_tokenizer` pro LLM.
- Balíček Pythonu `transformers` dostupný v prostředí Agent Server. Je vyžadován pro počítání tokenů podle šablony chatu, pokud je nastaveno `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop pro Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nainstalovaný a spuštěný. Na Windows běží stack Agent Canvas z publikovaného Docker obrazu, který obsahuje Node.js, `uv`, `transformers` a balíček `@openhands/agent-canvas`, takže je nemusíte instalovat na hostitelský systém.
<!-- @os:end -->

- Token GitHub s právem čtení k repozitáři, který chcete shrnout.
- Bot token Slack (`xoxb-...`) s oprávněním `chat:write` a právem čtení kanálu.
- ID týmu Slack (`T...`).
- ID kanálu Slack (`C...`), kam má být přehled zveřejněn.

Před testováním automatizace pozvěte aplikaci Slack do cílového kanálu.
## Proměnné použité v tomto playbooku

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

Tyto dvě proměnné se používají v ověřovacích příkazech níže.
Model, tokenizer a další nastavení LLM se v dalších krocích zadávají přímo do uživatelského rozhraní Agent Canvas, takže jejich konkrétní hodnoty jsou uvedeny přímo v textu tam, kde jsou potřeba.

Následující hodnoty se v dalších krocích zadávají do uživatelského rozhraní Agent Canvas.
Nastavte si je zde, abyste si je mohli zkopírovat:

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

Pro `GITHUB_REPO_FILTER` použijte explicitní hodnotu `owner/repo`.
Široké zástupné znaky pro celou organizaci mohou vrátit příliš mnoho MCP kontextu pro lokální modely.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Spuštění serveru Lemonade

Spusťte model z rozhraní příkazové řádky Lemonade CLI:

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

> **Vyberte model, který odpovídá vašemu hardwaru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je pro tento pracovní postup silný model, ale potřebuje velkou paměťovou kapacitu.
> Pokud má vaše zařízení omezenou paměť nebo VRAM GPU, vyberte si menší GGUF model z knihovny modelů Lemonade a použijte toto ID modelu (a odpovídající tokenizer) v celém tomto playbooku.

> **Poznámka:** První spuštění `lemonade run` model stáhne, pokud ještě není k dispozici, což může chvíli trvat v závislosti na velikosti modelu a rychlosti vašeho připojení.

Lemonade zpřístupňuje API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

Volitelné: pokud Agent Canvas nebo automatizační runner neběží na stejném počítači, zveřejněte koncový bod Lemonade přes zabezpečený tunel a použijte HTTPS URL jako základní URL pro LLM.
[ngrok](https://ngrok.com/) zpřístupní lokální port na internetu přes zabezpečenou HTTPS URL; vyžaduje bezplatný účet ngrok a `YOUR_NGROK_DOMAIN.ngrok-free.dev` nahradíte svou vlastní rezervovanou doménou:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Ověření lokálního modelu

Potvrďte, že Lemonade dokáže obsluhovat vybraný model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Poté odešlete malý chatovací požadavek:

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

Poté odešlete malý chatovací požadavek:

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

Pokud se vrátí pole `choices`, je Lemonade připraven pro Agent Canvas.

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

## 3. Spuštění Agent Canvas

<!-- @os:linux -->
Nainstalujte publikovaný balíček Agent Canvas a spusťte celý stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Pokud se globální instalace npm nezdaří s chybou oprávnění, přečtěte si níže položku týkající se řešení problémů s oprávněními npm.

Agent Canvas se ve výchozím nastavení spouští na `http://localhost:8000`.
Otevřete tuto adresu URL ve svém prohlížeči.
Port není nijak zvláštní – pokud je 8000 již obsazen, zadejte libovolný volný port pomocí `--port` (nebo `-p`).
Výchozí lokální backend by měl na domovské obrazovce zobrazovat stav „healthy“.

> **Poznámka:** První spuštění sestavuje Python prostředí Agent Serveru spravované nástrojem `uv`, takže může trvat několik minut, než backend ohlásí stav „healthy“.

Příkaz `agent-canvas` spustí agent server, automatizační backend a webové frontend dohromady.
K lokálnímu spuštění OpenHands potřebujete pouze tento jeden příkaz.
Zbytek tohoto playbooku nastavuje vše přes uživatelské rozhraní Agent Canvas ve vašem prohlížeči.
<!-- @os:end -->

<!-- @os:windows -->
Na Windows spusťte publikovaný obraz kontejneru Agent Canvas pomocí Docker Desktop.
Obraz obsahuje agent server, automatizační backend a webové frontend, takže na hostitele nemusíte instalovat Node.js, `uv` ani CLI.

Nejprve vytvořte složky pro konfiguraci a pracovní prostor, které kontejner připojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stáhněte publikovaný obraz (přibližně 6 GB; je veřejný, takže není vyžadováno přihlášení):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Poté spusťte stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Otevřete `http://localhost:8000/canvas` ve svém prohlížeči.
Pokud je port 8000 již obsazen, namapujte jiný port hostitele, například `-p 8080:8000`, a místo toho otevřete `http://localhost:8080/canvas`.

> **Poznámka:** První spuštění sestavuje prostředí Agent Serveru uvnitř kontejneru, takže může trvat několik minut, než backend ohlásí stav „healthy“.

Připojení `.openhands` uchovává váš LLM profil, MCP servery a automatizace i po restartu kontejneru.
Zbytek tohoto playbooku nastavuje vše přes uživatelské rozhraní Agent Canvas ve vašem prohlížeči na adrese `http://localhost:8000/canvas`.
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
## 4. Nakonfigurujte lokální LLM v uživatelském rozhraní

Při prvním spuštění se otevře úvodní proces nastavení Agent Canvas.
V tomto procesu:

1. Ponechte vybraného agenta **OpenHands** a klikněte na **Next**.
2. V kroku **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavenou na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do pole **API Key** zadejte libovolnou neprázdnou zástupnou hodnotu, například `lemonade-local`. Lemonade nevyžaduje skutečný klíč, ale klient OpenHands potřebuje nějakou hodnotu k odeslání.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server běží uvnitř kontejneru, takže místo `http://127.0.0.1:13305/api/v1` nastavte **Base URL** na `http://host.docker.internal:13305/api/v1`.
> Z pohledu uvnitř kontejneru je `127.0.0.1` samotný kontejner; `host.docker.internal` se dostane k Lemonade běžícímu na hostitelském systému Windows a Docker Desktop tento hostitelský název poskytuje automaticky.
<!-- @os:end -->

Pole pro připojení by měla vypadat takto.
Pole API key je v uživatelském rozhraní maskováno.

![Pokročilá nastavení LLM při prvním použití Agent Canvas s modelem Lemonade a lokální základní URL adresou](assets/01-llm-advanced-settings.png)

Poté vyberte **All** a nastavte doplňková pole lokálního modelu:

1. Přejděte na **Custom Tokenizer** a nastavte ho na `Qwen/Qwen3.6-35B-A3B`.
2. Přejděte na **LiteLLM Extra Body** a nastavte ho na `{"enable_thinking": true}`.
3. Klikněte na **Next**.

![Karta All pro LLM při prvním použití Agent Canvas s vlastním tokenizérem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta All pro LLM při prvním použití Agent Canvas s nakonfigurovaným LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavení LLM by mělo zobrazovat:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Předpona `openai/` říká LiteLLM, aby vůči koncovému bodu Lemonade používal formátování požadavků kompatibilní s OpenAI.
Vlastní tokenizér je původní tokenizér Hugging Face pro model GGUF; umožňuje OpenHands počítat stejné tokeny šablony chatu, jaké vidí lokální server modelu.
Aktuální formulář pro první použití LLM nezobrazuje nastavení condenseru.
Pokud vaše sestavení Agent Canvas později zpřístupní nastavení condenseru v **Settings > LLM**, použijte `llm_summarizing` a nastavte maximální počet tokenů pod velikost kontextového okna Lemonade, například `56000`.

## 5. Nainstalujte MCP servery pro GitHub a Slack

V uživatelském rozhraní Agent Canvas otevřete **Customize** (nebo **Settings > MCP**) a přidejte MCP servery, které agentovi poskytnou nástroje pro GitHub a Slack.
Hodnoty tokenů se odesílají pouze na váš lokální Agent Server a ukládají se jako šifrovaná nastavení.

<!-- @os:windows -->
> **Windows (Docker):** níže uvedené příkazy MCP serveru `npx` běží uvnitř kontejneru, který již obsahuje Node.js, takže na hostitelský systém se nic dalšího neinstaluje.
> Protože je `.openhands` připojen jako svazek, MCP servery a jejich tokeny přetrvávají i po restartování kontejneru.
<!-- @os:end -->

### MCP server pro GitHub

Přidejte nový MCP server s těmito nastaveními:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš GitHub token |

Použijte GitHub token s právem čtení k repozitáři, který chcete shrnovat.

### MCP server pro Slack

Přidejte druhý MCP server s těmito nastaveními:

| Pole | Hodnota |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašeho kanálu pro souhrn |

Nastavte `SLACK_CHANNEL_IDS` na ID kanálu pro souhrn (stejná hodnota jako `SLACK_DIGEST_CHANNEL`), aby agent nemusel procházet všechny kanály Slacku.

Po přidání obou serverů použijte u každého z nich tlačítko **Test** a ověřte, že se připojí a nabízí nástroje.
Server pro GitHub by měl zobrazit seznam nástrojů pro GitHub a server pro Slack by měl zobrazit seznam nástrojů pro Slack.

![Stránka MCP v Agent Canvas s nainstalovanými servery pro GitHub a Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Vytvořte automatizaci souhrnu

V uživatelském rozhraní Agent Canvas otevřete stránku **Automations** a vytvořte novou automatizaci:

1. Zvolte **Create automation** a vyberte typ **Prompt preset**.
2. Nastavte **Name** na `GitHub Development Digest to Slack`.
3. Nastavte **Prompt** na následující text, přičemž zástupné hodnoty repozitáře a kanálu nahraďte svými hodnotami:

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

4. Nastavte **Trigger** na **Cron** s plánem `0 9 * * 1-5` (9:00 v pracovní dny) a nastavte **Timezone** na své časové pásmo, například `America/New_York`.
5. Nastavte **Timeout** na `900` sekund.
6. Uložte automatizaci.

Stránka s podrobnostmi automatizace zobrazuje novou automatizaci s jejím cron triggerem a vygenerovaným vstupním bodem předvolby promptu.

![Podrobnosti automatizace v Agent Canvas po vytvoření](assets/05-automation-created.png)
## 7. Otestujte automatizaci

Na stránce podrobností automatizace v Agent Canvas UI:

1. Klikněte na **Run now** (nebo **Dispatch**) pro okamžité jednorázové spuštění automatizace.
2. Sledujte seznam spuštění na stejné stránce. Nejnovější spuštění by mělo přejít do stavu `COMPLETED`.
3. Otevřete cílový Slack kanál. Měl by obsahovat vygenerovaný souhrn.

Nemusíte čekat, až se spustí plán podle cronu—**Run now** spustí běh na vyžádání, takže si můžete ověřit, že prompt, MCP připojení i publikování na Slack fungují, ještě než se spolehnete na plánovač.

![Automatizace v Agent Canvas byla úspěšně spuštěna](assets/06-automation-run-completed.png)

![Slack kanál zobrazující vygenerovaný souhrn OpenHands](assets/07-slackbot-message.png)

## Řešení potíží

<!-- @os:windows -->
- **Docker port 8000 je již používán:** namapujte jiný hostitelský port, například `docker run ... -p 8080:8000 ...`, a otevřete `http://localhost:8080/canvas`.
- **`docker pull` selže s chybou přihlašovacích údajů** (například „A specified logon session does not exist“): spusťte pull z interaktivní relace Windows nebo si image stáhněte předem. Image je veřejný, takže `docker login` není potřeba.
- **Rozhraní se načte, ale backend je nefunkční:** při prvním spuštění se v kontejneru sestavuje prostředí Agent Server. Počkejte minutu a obnovte stránku, poté zkontrolujte průběh pomocí `docker logs <container>`.
- **Agent Canvas se z kontejneru nemůže připojit k Lemonade:** nastavte **Base URL** pro LLM na `http://host.docker.internal:13305/api/v1` (ne `127.0.0.1`) a ověřte, že Lemonade běží na hostitelském systému Windows.
<!-- @os:end -->

- **Lemonade neběží:** restartujte ji příkazem `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a poté znovu spusťte kontrolu stavu.
- **`npm install -g` selže s chybou oprávnění:** na Linuxu nebo WSL nastavte globální npm adresář vlastněný uživatelem, přidejte ho do souboru spouštěného při startu shellu a poté znovu nainstalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Pokud používáte `zsh`, přidejte stejný řádek `export PATH=...` místo do `~/.bashrc` do souboru `~/.zshrc`.
- **Agent Canvas odmítne nastavení LLM po nastavení `custom_tokenizer`:** nainstalujte `transformers` do Python prostředí Agent Server, v případě potřeby restartujte Agent Canvas a zkuste nastavení LLM uložit znovu. OpenHands vyžaduje Transformers k načtení chat šablony tokenizéru, pokud je nastaveno `custom_tokenizer`.
- **Agent Canvas se nemůže připojit k Lemonade:** ověřte `curl -fsS "${LEMONADE_BASE_URL}/health"` a potvrďte, že základní URL zadaná ve formuláři LLM při prvním použití nebo v **Settings > LLM** odpovídá běžícímu lokálnímu endpointu nebo HTTPS tunelu.
- **Nastavení LLM se neuložilo:** ujistěte se, že jste po zadání hodnot klikli na **Next**. Znovu otevřete **Settings > LLM** a ověřte, že hodnoty zůstaly zachovány.
- **GitHub MCP nevidí privátní repozitáře:** ověřte, že GitHub token má oprávnění ke čtení cílového repozitáře a že tlačítko **Test** u MCP v sekci **Customize** hlásí dostupné GitHub nástroje.
- **Slack dokáže číst kanály, ale nemůže do nich publikovat:** pozvěte Slack aplikaci do cílového kanálu a potvrďte, že bot má oprávnění `chat:write`.
- **Automatizace zobrazuje příliš mnoho Slack kanálů:** použijte ID Slack kanálu a nastavte `SLACK_CHANNEL_IDS` na Slack MCP serveru v sekci **Customize**.
- **Spuštění automatizace selže nebo překročí kontext:** ověřte, že byla Lemonade spuštěna s `ctx_size=65536`, že má LLM v OpenHands nastaveno `custom_tokenizer`, a použijte konkrétní repozitář s výsledky z GitHubu omezenými na 3 až 5 položek. Pokud vaše sestavení Agent Canvas obsahuje nastavení condenseru, nastavte maximální počet tokenů condenseru pod velikost kontextového okna Lemonade.

## Další kroky

- Přidejte týdenní souhrn pouze pro vydání (release).
- Přidejte automatizaci spouštěnou událostmi GitHubu pro rychlejší upozornění na PR nebo push.
- Směrujte stejný souhrn do Notion, Linear nebo jiného nástroje podporovaného MCP.

## Zdroje

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentace Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitář rozšíření OpenHands](https://github.com/OpenHands/extensions)
- [Servery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Balíček Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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