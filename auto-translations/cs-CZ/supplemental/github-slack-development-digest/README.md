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

Vývojáři tráví hodně času malými opakujícími se úkoly: kontrolou označených pull requestů, odpovídáním na komentáře na GitHub, tříděním nových issues, přeměnou vláken ve Slacku na standup poznámky nebo následné kroky po incidentech a sledováním signálů o vydáních nebo výzkumu.
Každý z těchto cyklů je známý, přesto vyžaduje úsudek: shromáždit správný kontext, rozhodnout, co je důležité, a zveřejnit jasnou aktualizaci tam, kde tým už pracuje.

[Automatizace OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) mění tyto opakující se úkoly na naplánované nebo událostmi spouštěné konverzace agenta: běhy, kdy AI softwarový agent může číst kontext, volat nástroje a vytvářet aktualizaci.
Sdílené šablony automatizací v katalogu rozšíření OpenHands sledují tento vzor pro kontrolu pull requestů na GitHub, monitorování repozitářů, třídění issues v Linear, retrospektivy incidentů, standup souhrny ve Slacku a výzkumné přehledy: automatizace se probudí, pomocí nakonfigurovaných integrací, jako je GitHub nebo Slack, načte kontext, uvažuje nad tímto kontextem pomocí velkého jazykového modelu (LLM) a zapíše výsledek zpět.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokální řídicí rovina pro vytváření a testování těchto automatizací.
V této příručce spouští OpenHands Agent Server, backendový proces, který provádí konverzace agenta, a propojuje agenta s externími službami, jako je GitHub a Slack.

Aby pracovní postup zůstal na vašem systému AMD, agent komunikuje s lokálním modelem obsluhovaným serverem Lemonade Server.
Lemonade zpřístupňuje tento model prostřednictvím API kompatibilního s OpenAI, takže jej Agent Canvas může konfigurovat jako vzdálený endpoint ve stylu OpenAI, zatímco model, prompt a kontext pracovního postupu zůstávají lokální.

V této příručce vytvoříte jednu konkrétní automatizaci: naplánovaný souhrn vývoje z GitHub do Slacku.
Používá GitHub ke kontrole nedávné aktivity v repozitáři, Slack ke zveřejnění souhrnu, volání API Agent Canvas ke konfiguraci a testování automatizace a Lemonade ke spouštění LLM lokálně.

![Diagram architektury zobrazující GitHub MCP, automatizaci OpenHands, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové požadavky
- Jak spustit Agent Canvas a nasměrovat jeho Agent Server na lokální LLM
- Jak nainstalovat servery GitHub a Slack Model Context Protocol (MCP) prostřednictvím API Agent Server
- Jak vytvořit a spustit naplánovanou automatizaci OpenHands, která zveřejní souhrn vývoje ve Slacku
- Jak řešit nejčastější selhání lokálního modelu a automatizace

## Základní pojmy

| Pojem | Co to je | Kde v této příručce zapadá |
| --- | --- | --- |
| Lemonade Server | Platforma pro lokální obsluhu LLM postavená pro hardware AMD, která zpřístupňuje API kompatibilní s OpenAI. Vaše data neopustí váš počítač. | Spouští model, který pohání agenta. |
| OpenHands Agent Server | Backendový proces, který provádí konverzace agenta OpenHands. | Hostí agenta, jeho profil LLM a jeho servery MCP. |
| Agent Canvas | Lokální řídicí rovina pro OpenHands, která spouští Agent Server a uživatelské rozhraní pro kontrolu běhů agenta. | Spouští backendy a poskytuje API, které voláte. |
| Server MCP | Server Model Context Protocol, který poskytuje agentovi nástroje pro externí službu, jako je GitHub nebo Slack. | Umožňuje agentovi číst z GitHub a zapisovat do Slacku. |
| Automatizace OpenHands | Naplánovaná nebo událostmi spouštěná konverzace agenta, která načte kontext, uvažuje nad ním a někam zapíše výsledek. | Souhrn z GitHub do Slacku, který zde vytváříte. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Pracovní postupy s kódovacím agentem těží z většího modelu a kontextového okna.
> Použijte alespoň 32 GB systémové paměti a pro větší modely GGUF upřednostněte 64 GB nebo více.
<!-- @device:end -->

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Předpoklady

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Budete potřebovat:

- Server Lemonade Server nainstalovaný podle standardního [instalačního průvodce Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 nebo novější a `npm`, používané k instalaci publikovaného CLI Agent Canvas a ke spouštění serverů MCP pomocí `npx`.
- `uv`, správce balíčků Pythonu, který Agent Canvas používá k sestavení prostředí Agent Server. Pokud ještě není nainstalovaný, nainstalujte jej podle [instalačního průvodce uv](https://docs.astral.sh/uv/getting-started/installation/).
- Nedávný publikovaný balíček `@openhands/agent-canvas` se schématem řízeným nastavením agenta, `LLMSummarizingCondenserSettings.max_tokens` a podporou `custom_tokenizer` pro LLM.
- Balíček Pythonu `transformers` dostupný v prostředí Agent Server. Je vyžadován pro počítání tokenů podle chatové šablony, pokud je nastaven `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), nainstalovaný a spuštěný. Ve Windows běží stack Agent Canvas z publikovaného obrazu Docker, který zahrnuje Node.js, `uv`, `transformers` a balíček `@openhands/agent-canvas`, takže je není nutné instalovat na hostitele.
<!-- @os:end -->

- Token GitHub s právem čtení pro repozitář, který chcete shrnout.
- Bot token Slack (`xoxb-...`) s právem `chat:write` a čtení kanálu.
- ID týmu Slack (`T...`).
- ID kanálu Slack (`C...`), kam se má souhrn zveřejnit.

Než automatizaci otestujete, pozvěte aplikaci Slack do cílového kanálu.
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
Model, tokenizer a další nastavení LLM se v pozdějších krocích zadávají přímo v uživatelském rozhraní Agent Canvas, takže jejich doslovné hodnoty jsou uvedeny přímo tam, kde je potřebujete.

Následující hodnoty se v pozdějších krocích zadávají do uživatelského rozhraní Agent Canvas.
Nastavte je zde, abyste je mohli zkopírovat:

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
Široké zástupné znaky pro celou organizaci mohou vracet příliš mnoho kontextu MCP pro lokální modely.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Spusťte Lemonade Server

Spusťte model z rozhraní Lemonade CLI:

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

> **Zvolte model, který odpovídá vašemu hardwaru.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) je pro tento pracovní postup silný model, ale vyžaduje velkou paměťovou kapacitu.
> Pokud má vaše zařízení omezenou paměť nebo VRAM GPU, vyberte menší model GGUF z knihovny modelů Lemonade a použijte toto ID modelu (a odpovídající tokenizer) v celém tomto playbooku.

> **Poznámka:** První `lemonade run` model stáhne, pokud ještě není přítomen, což může chvíli trvat v závislosti na velikosti modelu a rychlosti vašeho připojení.

Lemonade zpřístupňuje rozhraní API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

Volitelně: pokud Agent Canvas nebo automatizační runner neběží na stejném počítači, zpřístupněte koncový bod Lemonade prostřednictvím zabezpečeného tunelu a jako základní URL adresu LLM použijte adresu HTTPS.
[ngrok](https://ngrok.com/) zpřístupňuje lokální port na internetu prostřednictvím zabezpečené adresy URL HTTPS; vyžaduje bezplatný účet ngrok a `YOUR_NGROK_DOMAIN.ngrok-free.dev` nahradíte vlastní rezervovanou doménou:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Ověření lokálního modelu

Ověřte, že Lemonade dokáže obsluhovat vybraný model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Poté odešlete malý chatový požadavek:

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

Poté odešlete malý chatový požadavek:

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

## 3. Spusťte Agent Canvas

<!-- @os:linux -->
Nainstalujte publikovaný balíček Agent Canvas a spusťte celý stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Pokud globální instalace npm selže s chybou oprávnění, podívejte se na položku o řešení problémů s oprávněními npm níže.

Ve výchozím nastavení se Agent Canvas spustí na adrese `http://localhost:8000`.
Otevřete tuto adresu URL ve svém prohlížeči.
Port není nijak zvláštní – pokud je port 8000 již používán, zadejte jakýkoli volný port pomocí `--port` (nebo `-p`).
Výchozí lokální backend by se měl na domovské obrazovce zobrazovat jako funkční (healthy).

> **Poznámka:** První spuštění sestavuje Python prostředí Agent Serveru spravované nástrojem `uv`, takže může trvat několik minut, než backend nahlásí stav healthy.

Příkaz `agent-canvas` spouští agent server, automatizační backend a webový frontend společně.
K lokálnímu spuštění OpenHands potřebujete pouze tento jediný příkaz.
Zbytek tohoto playbooku vše nastavuje prostřednictvím uživatelského rozhraní Agent Canvas ve vašem prohlížeči.
<!-- @os:end -->

<!-- @os:windows -->
Na Windows spusťte publikovaný obraz kontejneru Agent Canvas pomocí Docker Desktop.
Obraz obsahuje Agent Server, automatizační backend a webový frontend, takže na hostitelský systém nemusíte instalovat Node.js, `uv` ani CLI.

Nejprve vytvořte konfigurační a pracovní složky, které kontejner připojí:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Stáhněte publikovaný obraz (přibližně 6 GB; je veřejný, takže není potřeba žádné přihlášení):

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
Pokud je port 8000 již používán, namapujte jiný hostitelský port, například `-p 8080:8000`, a místo toho otevřete `http://localhost:8080/canvas`.

> **Poznámka:** První spuštění sestavuje prostředí Agent Serveru uvnitř kontejneru, takže může trvat několik minut, než backend nahlásí stav healthy.

Připojení `.openhands` uchovává váš profil LLM, servery MCP a automatizace i po restartu kontejneru.
Zbytek tohoto playbooku vše nastavuje prostřednictvím uživatelského rozhraní Agent Canvas ve vašem prohlížeči na adrese `http://localhost:8000/canvas`.
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
## 4. Konfigurace lokálního LLM v uživatelském rozhraní

Při prvním spuštění se v Agent Canvas otevře průvodce úvodním nastavením.
V tomto průvodci proveďte následující:

1. Ponechte **OpenHands** vybraný jako agent a klikněte na **Next**.
2. V části **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. U pole **API Key** zadejte libovolnou neprázdnou zástupnou hodnotu, například `lemonade-local`. Lemonade nevyžaduje skutečný klíč, ale klient OpenHands potřebuje nějakou hodnotu k odeslání.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server běží uvnitř kontejneru, takže pole **Base URL** nastavte na `http://host.docker.internal:13305/api/v1` místo `http://127.0.0.1:13305/api/v1`.
> Zevnitř kontejneru je `127.0.0.1` samotný kontejner; `host.docker.internal` se dostane k Lemonade běžícímu na hostitelském systému Windows a Docker Desktop tento hostname poskytuje automaticky.
<!-- @os:end -->

Pole pro připojení by měla vypadat takto.
Pole s API klíčem je v uživatelském rozhraní maskováno.

![Nastavení Agent Canvas first-use LLM Advanced s modelem Lemonade a lokální základní URL](assets/01-llm-advanced-settings.png)

Poté vyberte **All** a nastavte doplňující pole pro lokální model:

1. Přejděte na **Custom Tokenizer** a nastavte jej na `Qwen/Qwen3.6-35B-A3B`.
2. Přejděte na **LiteLLM Extra Body** a nastavte jej na `{"enable_thinking": true}`.
3. Klikněte na **Next**.

![Karta Agent Canvas first-use LLM All s vlastním tokenizérem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta Agent Canvas first-use LLM All s nakonfigurovaným LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavení LLM by mělo zobrazovat:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Předpona `openai/` říká LiteLLM, aby vůči koncovému bodu Lemonade používal formátování požadavků kompatibilní s OpenAI.
Vlastní tokenizér je původní tokenizér Hugging Face pro model GGUF; umožňuje OpenHands počítat tokeny stejné šablony chatu, jaké vidí server lokálního modelu.
Aktuální první formulář pro nastavení LLM nezobrazuje nastavení condenseru.
Pokud vaše sestavení Agent Canvas později zpřístupní nastavení condenseru v **Settings > LLM**, použijte `llm_summarizing` a nastavte maximální počet tokenů pod velikost kontextového okna Lemonade, například `56000`.

## 5. Instalace MCP serverů pro GitHub a Slack

V uživatelském rozhraní Agent Canvas otevřete **Customize** (nebo **Settings > MCP**) a přidejte MCP servery, které agentovi poskytnou nástroje pro GitHub a Slack.
Hodnoty tokenů se odesílají pouze na váš lokální Agent Server a jsou ukládány jako šifrovaná nastavení.

<!-- @os:windows -->
> **Windows (Docker):** níže uvedené příkazy MCP serveru `npx` běží uvnitř kontejneru, který již obsahuje Node.js, takže se na hostitelský systém nic navíc neinstaluje.
> Protože je `.openhands` připojen jako svazek, MCP servery a jejich tokeny přetrvávají i po restartu kontejneru.
<!-- @os:end -->

### MCP server pro GitHub

Přidejte nový MCP server s těmito nastaveními:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš token GitHub |

Použijte token GitHub s přístupem pro čtení k repozitáři, který chcete shrnout.

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

Nastavte `SLACK_CHANNEL_IDS` na ID kanálu pro souhrn (stejná hodnota jako `SLACK_DIGEST_CHANNEL`), aby agent nemusel procházet všechny kanály Slack.

Po přidání obou serverů použijte u každého z nich tlačítko **Test** a ověřte, že se připojí a nabízí nástroje.
Server GitHub by měl vypsat nástroje GitHub a server Slack by měl vypsat nástroje Slack.

![Stránka MCP v Agent Canvas s nainstalovanými servery GitHub a Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Vytvoření automatizace souhrnu

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

4. Nastavte **Trigger** na **Cron** s plánem `0 9 * * 1-5` (9:00 v pracovní dny) a nastavte **Timezone** na vaše časové pásmo, například `America/New_York`.
5. Nastavte **Timeout** na `900` sekund.
6. Uložte automatizaci.

Na stránce s detailem automatizace se zobrazí nová automatizace se svým cron triggerem a vygenerovaným vstupním bodem typu prompt preset.

![Detail automatizace v Agent Canvas po vytvoření](assets/05-automation-created.png)
## 7. Otestujte automatizaci

Na stránce podrobností automatizace v uživatelském rozhraní Agent Canvas:

1. Klikněte na tlačítko **Run now** (nebo **Dispatch**) a okamžitě jednorázově spusťte automatizaci.
2. Sledujte seznam běhů na stejné stránce. Nejnovější běh by měl přejít do stavu `COMPLETED`.
3. Otevřete cílový kanál Slack. Měl by obsahovat vygenerovaný souhrn.

Není nutné čekat, až se spustí naplánovaný cron úkol – tlačítko **Run now** spustí běh na vyžádání, takže si můžete ověřit, že prompt, připojení MCP i publikování na Slack fungují ještě předtím, než se spolehnete na plán.

![Automatizace v Agent Canvas byla úspěšně dokončena](assets/06-automation-run-completed.png)

![Kanál Slack zobrazující vygenerovaný souhrn OpenHands](assets/07-slackbot-message.png)

## Řešení problémů

<!-- @os:windows -->
- **Port 8000 v Dockeru je již používán:** namapujte jiný port hostitele, například `docker run ... -p 8080:8000 ...`, a otevřete `http://localhost:8080/canvas`.
- **Příkaz `docker pull` selže s chybou přihlašovacích údajů** (například „A specified logon session does not exist“): spusťte pull z interaktivní relace Windows nebo image předem stáhněte. Image je veřejný, takže `docker login` není potřeba.
- **Uživatelské rozhraní se načte, ale backend je nefunkční:** při prvním spuštění se uvnitř kontejneru sestavuje prostředí Agent Server. Počkejte minutu, obnovte stránku a poté zkontrolujte průběh pomocí `docker logs <container>`.
- **Agent Canvas se z kontejneru nemůže připojit k Lemonade:** nastavte **Base URL** pro LLM na `http://host.docker.internal:13305/api/v1` (nikoli `127.0.0.1`) a ověřte, že Lemonade běží na hostitelském systému Windows.
<!-- @os:end -->

- **Lemonade neběží:** restartujte jej příkazem `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a poté znovu spusťte kontrolu stavu.
- **Příkaz `npm install -g` selže s chybou oprávnění:** v Linuxu nebo WSL nastavte globální adresář npm vlastněný uživatelem, přidejte jej do spouštěcího souboru shellu a poté znovu nainstalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Pokud používáte `zsh`, přidejte stejný řádek `export PATH=...` do `~/.zshrc` místo `~/.bashrc`.
- **Agent Canvas odmítne nastavení LLM po zadání `custom_tokenizer`:** nainstalujte `transformers` do Python prostředí Agent Server, v případě potřeby restartujte Agent Canvas a zkuste nastavení LLM uložit znovu. OpenHands vyžaduje Transformers k načtení šablony chatu tokenizeru, pokud je nastaveno `custom_tokenizer`.
- **Agent Canvas se nemůže připojit k Lemonade:** ověřte pomocí `curl -fsS "${LEMONADE_BASE_URL}/health"` a potvrďte, že základní URL zadaná ve formuláři LLM při prvním použití nebo v **Settings > LLM** odpovídá běžícímu lokálnímu koncovému bodu nebo tunelu HTTPS.
- **Nastavení LLM se neuložilo:** ujistěte se, že jste po zadání hodnot klikli na **Next**. Znovu otevřete **Settings > LLM** a ověřte, že se hodnoty uložily.
- **GitHub MCP nevidí soukromé repozitáře:** ověřte, že GitHub token má oprávnění ke čtení cílového repozitáře a že tlačítko **Test** u MCP v sekci **Customize** hlásí dostupné nástroje GitHub.
- **Slack umí číst kanály, ale nemůže do nich publikovat:** pozvěte aplikaci Slack do cílového kanálu a ověřte, že bot má oprávnění `chat:write`.
- **Automatizace zobrazuje příliš mnoho kanálů Slack:** použijte ID kanálu Slack a nastavte `SLACK_CHANNEL_IDS` na serveru Slack MCP v sekci **Customize**.
- **Běh automatizace selže nebo překročí kontext:** ověřte, že Lemonade byl spuštěn s `ctx_size=65536`, že LLM OpenHands má nastaveno `custom_tokenizer`, a použijte konkrétní repozitář s výsledky GitHubu omezenými na 3 až 5 položek. Pokud vaše sestavení Agent Canvas obsahuje nastavení condenseru, nastavte maximální počet tokenů condenseru pod hodnotu kontextového okna Lemonade.

## Další kroky

- Přidejte týdenní souhrn zaměřený pouze na vydání (release).
- Přidejte automatizaci spouštěnou událostmi GitHubu pro rychlejší upozornění na PR nebo push.
- Přesměrujte stejný souhrn do Notion, Linear nebo jiného nástroje podporovaného přes MCP.

## Zdroje

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentace serveru Lemonade](https://lemonade-server.ai/docs)
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