<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Übersicht

Entwickler verbringen viel Zeit mit kleinen, wiederkehrenden Aufgaben: das Überprüfen von gekennzeichneten Pull Requests, das Beantworten von GitHub-Kommentaren, das Triagieren neuer Issues, das Umwandeln von Slack-Threads in Standup-Notizen oder Incident-Follow-ups sowie das Verfolgen von Release- oder Research-Signalen.
Jede dieser Aufgaben ist vertraut, erfordert aber dennoch Urteilsvermögen: den richtigen Kontext sammeln, entscheiden, was wichtig ist, und ein klares Update dort posten, wo das Team bereits arbeitet.

[OpenHands-Automatisierungen](https://docs.openhands.dev/openhands/usage/automations/overview) verwandeln diese Aufgaben in geplante oder ereignisgesteuerte Agent-Konversationen: Durchläufe, bei denen ein KI-Softwareagent Kontext lesen, Tools aufrufen und ein Update erstellen kann.
Die gemeinsam genutzten Automatisierungsvorlagen im OpenHands-Erweiterungskatalog folgen diesem Muster für die Überprüfung von GitHub-Pull-Requests, die Überwachung von Repositories, die Linear-Issue-Triage, Incident-Retrospektiven, Slack-Standup-Digests und Research-Briefings: Eine Automatisierung wird aktiviert, verwendet konfigurierte Integrationen wie GitHub oder Slack, um Kontext abzurufen, verarbeitet diesen Kontext mit einem Large Language Model (LLM) und schreibt ein Ergebnis zurück.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) ist die lokale Steuerungsebene zum Erstellen und Testen dieser Automatisierungen.
In diesem Playbook führt es einen OpenHands Agent Server aus, den Backend-Prozess, der Agent-Konversationen ausführt, und verbindet den Agenten mit externen Diensten wie GitHub und Slack.

Damit der Workflow auf Ihrem AMD-System bleibt, kommuniziert der Agent mit einem lokalen Modell, das von Lemonade Server bereitgestellt wird.
Lemonade stellt dieses Modell über eine OpenAI-kompatible API bereit, sodass Agent Canvas es wie einen entfernten OpenAI-ähnlichen Endpunkt konfigurieren kann, während Modell, Prompt und Workflow-Kontext lokal bleiben.

In diesem Playbook erstellen Sie eine konkrete Automatisierung: einen geplanten GitHub-zu-Slack-Entwicklungs-Digest.
Dabei wird GitHub verwendet, um aktuelle Repository-Aktivitäten zu untersuchen, Slack, um den Digest zu posten, Agent-Canvas-API-Aufrufe, um die Automatisierung zu konfigurieren und zu testen, sowie Lemonade, um das LLM lokal auszuführen.

![Architekturdiagramm, das GitHub MCP, OpenHands-Automatisierung, Lemonade Server und Slack MCP zeigt](assets/00-architecture-overview.png)

## Was Sie lernen werden

- Wie Sie Lemonade Server starten und überprüfen, ob ein lokales Modell auf Chat-Anfragen antwortet
- Wie Sie Agent Canvas starten und dessen Agent Server auf ein lokales LLM ausrichten
- Wie Sie GitHub- und Slack-Model-Context-Protocol-Server (MCP) über die Agent-Server-API installieren
- Wie Sie eine geplante OpenHands-Automatisierung erstellen und auslösen, die einen Entwicklungs-Digest in Slack postet
- Wie Sie die häufigsten Fehler bei lokalen Modellen und Automatisierungen beheben

## Kernkonzepte

| Konzept | Was es ist | Wo es in diesem Playbook eingesetzt wird |
| --- | --- | --- |
| Lemonade Server | Eine lokale LLM-Serving-Plattform für AMD-Hardware, die eine OpenAI-kompatible API bereitstellt. Ihre Daten verlassen niemals Ihren Rechner. | Betreibt das Modell, das den Agenten antreibt. |
| OpenHands Agent Server | Der Backend-Prozess, der OpenHands-Agent-Konversationen ausführt. | Hostet den Agenten, sein LLM-Profil und seine MCP-Server. |
| Agent Canvas | Die lokale Steuerungsebene für OpenHands, die Agent Server sowie eine Benutzeroberfläche zur Überprüfung von Agent-Durchläufen ausführt. | Startet die Backends und stellt die API bereit, die Sie aufrufen. |
| MCP-Server | Ein Model-Context-Protocol-Server, der einem Agenten Tools für einen externen Dienst wie GitHub oder Slack bereitstellt. | Ermöglicht dem Agenten, GitHub zu lesen und in Slack zu schreiben. |
| OpenHands-Automatisierung | Eine geplante oder ereignisgesteuerte Agent-Konversation, die Kontext abruft, darüber nachdenkt und ein Ergebnis irgendwo schreibt. | Der GitHub-zu-Slack-Digest, den Sie hier erstellen. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Coding-Agent-Workflows profitieren von einem größeren Modell und Kontextfenster.
> Verwenden Sie mindestens 32 GB Systemspeicher, und bevorzugen Sie 64 GB oder mehr für größere GGUF-Modelle.
<!-- @device:end -->

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Voraussetzungen

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

Sie benötigen:

- Lemonade Server, installiert gemäß der standardmäßigen [Lemonade-Installationsanleitung](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 oder höher und `npm`, verwendet, um die veröffentlichte Agent-Canvas-CLI zu installieren und MCP-Server mit `npx` auszuführen.
- `uv`, den Python-Paketmanager, den Agent Canvas zum Erstellen der Agent-Server-Umgebung verwendet. Falls noch nicht installiert, installieren Sie es über die [uv-Installationsanleitung](https://docs.astral.sh/uv/getting-started/installation/).
- Ein aktuell veröffentlichtes `@openhands/agent-canvas`-Paket mit schemabasierten Agent-Einstellungen, `LLMSummarizingCondenserSettings.max_tokens` und LLM-`custom_tokenizer`-Unterstützung.
- Das Python-Paket `transformers`, verfügbar in der Agent-Server-Umgebung. Es wird für die Token-Zählung anhand von Chat-Vorlagen benötigt, wenn `custom_tokenizer` festgelegt ist.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop für Windows](https://docs.docker.com/desktop/setup/install/windows-install/), installiert und ausgeführt. Unter Windows läuft der Agent-Canvas-Stack über das veröffentlichte Docker-Image, das Node.js, `uv`, `transformers` und das `@openhands/agent-canvas`-Paket enthält, sodass Sie diese nicht auf dem Host installieren müssen.
<!-- @os:end -->

- Ein GitHub-Token mit Lesezugriff auf das Repository, das zusammengefasst werden soll.
- Ein Slack-Bot-Token (`xoxb-...`) mit `chat:write`- und Kanal-Lesezugriff.
- Eine Slack-Team-ID (`T...`).
- Eine Slack-Kanal-ID (`C...`), in der der Digest gepostet werden soll.

Laden Sie die Slack-App in den Zielkanal ein, bevor Sie die Automatisierung testen.
# In diesem Playbook verwendete Variablen

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

Diese beiden Variablen werden von den unten stehenden Verifizierungsbefehlen verwendet.
Das Modell, der Tokenizer und andere LLM-Einstellungen werden in späteren Schritten direkt in der Agent-Canvas-UI eingegeben, daher werden ihre literalen Werte dort inline angezeigt, wo Sie sie benötigen.

Die folgenden Werte werden in späteren Schritten in die Agent-Canvas-UI eingegeben.
Legen Sie sie hier fest, damit Sie sie übernehmen können:

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

Verwenden Sie für `GITHUB_REPO_FILTER` einen expliziten Wert im Format `owner/repo`.
Breite Organisations-Wildcards können zu viel MCP-Kontext für lokale Modelle zurückliefern.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Lemonade-Server starten

Starten Sie das Modell über die Lemonade-CLI:

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

> **Wählen Sie ein Modell, das zu Ihrer Hardware passt.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) ist ein leistungsstarkes Modell für diesen Workflow, benötigt jedoch einen großen Speicherpool.
> Wenn Ihr Gerät über begrenzten Speicher oder GPU-VRAM verfügt, wählen Sie ein kleineres GGUF-Modell aus der Lemonade-Modellbibliothek und verwenden Sie diese Modell-ID (und den passenden Tokenizer) im gesamten Playbook.

> **Hinweis:** Der erste `lemonade run`-Befehl lädt das Modell herunter, falls es noch nicht vorhanden ist, was je nach Modellgröße und Verbindung eine Weile dauern kann.

Lemonade stellt eine OpenAI-kompatible API bereit unter:

```text
http://127.0.0.1:13305/api/v1
```

Optional: Wenn sich Agent Canvas oder der Automatisierungs-Runner nicht auf demselben Rechner befinden, veröffentlichen Sie den Lemonade-Endpunkt über einen sicheren Tunnel und verwenden Sie die HTTPS-URL als LLM-Basis-URL.
[ngrok](https://ngrok.com/) stellt einen lokalen Port über eine sichere HTTPS-URL im Internet bereit; es erfordert ein kostenloses ngrok-Konto, und Sie ersetzen `YOUR_NGROK_DOMAIN.ngrok-free.dev` durch Ihre eigene reservierte Domain:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Das lokale Modell überprüfen

Bestätigen Sie, dass Lemonade das ausgewählte Modell bereitstellen kann:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Senden Sie dann eine kleine Chat-Anfrage:

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

Senden Sie dann eine kleine Chat-Anfrage:

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

Wenn dies ein `choices`-Array zurückgibt, ist Lemonade bereit für Agent Canvas.

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

## 3. Agent Canvas starten

<!-- @os:linux -->
Installieren Sie das veröffentlichte Agent-Canvas-Paket und starten Sie den vollständigen Stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Wenn die globale npm-Installation mit einem Berechtigungsfehler fehlschlägt, finden Sie weiter unten den Eintrag zur Fehlerbehebung bei npm-Berechtigungen.

Standardmäßig startet Agent Canvas unter `http://localhost:8000`.
Öffnen Sie diese URL in Ihrem Browser.
Der Port ist nicht besonders festgelegt – falls 8000 bereits belegt ist, übergeben Sie mit `--port` (oder `-p`) einen beliebigen freien Port.
Das standardmäßige lokale Backend sollte auf dem Startbildschirm als funktionsfähig angezeigt werden.

> **Hinweis:** Beim ersten Start wird die von `uv` verwaltete Python-Umgebung des Agent Servers erstellt, sodass es einige Minuten dauern kann, bis das Backend als funktionsfähig gemeldet wird.

Der Befehl `agent-canvas` startet den Agent Server, das Automatisierungs-Backend und das Web-Frontend gemeinsam.
Sie benötigen nur diesen einen Befehl, um OpenHands lokal auszuführen.
Der Rest dieses Playbooks konfiguriert alles über die Agent-Canvas-UI in Ihrem Browser.
<!-- @os:end -->

<!-- @os:windows -->
Führen Sie unter Windows das veröffentlichte Agent-Canvas-Container-Image mit Docker Desktop aus.
Das Image bündelt den Agent Server, das Automatisierungs-Backend und das Web-Frontend, sodass Sie Node.js, `uv` oder die CLI nicht auf dem Host installieren müssen.

Erstellen Sie zunächst die Konfigurations- und Workspace-Ordner, die der Container mountet:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Laden Sie das veröffentlichte Image herunter (ca. 6 GB; es ist öffentlich, daher ist kein Login erforderlich):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Starten Sie dann den Stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Öffnen Sie `http://localhost:8000/canvas` in Ihrem Browser.
Falls Port 8000 bereits belegt ist, mappen Sie einen anderen Host-Port, zum Beispiel `-p 8080:8000`, und öffnen Sie stattdessen `http://localhost:8080/canvas`.

> **Hinweis:** Beim ersten Start wird die Agent-Server-Umgebung innerhalb des Containers erstellt, sodass es einige Minuten dauern kann, bis das Backend als funktionsfähig gemeldet wird.

Der `.openhands`-Mount speichert dauerhaft Ihr LLM-Profil, MCP-Server und Automatisierungen über Container-Neustarts hinweg.
Der Rest dieses Playbooks konfiguriert alles über die Agent-Canvas-UI in Ihrem Browser unter `http://localhost:8000/canvas`.
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
## 4. Konfigurieren Sie das lokale LLM in der Benutzeroberfläche

Beim ersten Start öffnet Agent Canvas einen Onboarding-Ablauf.
In diesem Ablauf:

1. Lassen Sie **OpenHands** als Agent ausgewählt und klicken Sie auf **Next**.
2. Wählen Sie unter **Set up your LLM** die Option **Advanced**.
3. Belassen Sie **Authentication** auf **API key**.
4. Setzen Sie **Custom Model** auf `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setzen Sie **Base URL** auf `http://127.0.0.1:13305/api/v1`.
6. Geben Sie bei **API Key** einen beliebigen nicht leeren Platzhalter wie `lemonade-local` ein. Lemonade benötigt keinen echten Schlüssel, aber der OpenHands-Client muss einen Wert senden.

<!-- @os:windows -->
> **Windows (Docker):** Der Agent Server läuft im Container, setzen Sie daher **Base URL** auf `http://host.docker.internal:13305/api/v1` anstelle von `http://127.0.0.1:13305/api/v1`.
> Von innerhalb des Containers aus ist `127.0.0.1` der Container selbst; `host.docker.internal` erreicht Lemonade, das auf dem Windows-Host läuft, und Docker Desktop stellt diesen Hostnamen automatisch bereit.
<!-- @os:end -->

Die Verbindungsfelder sollten wie folgt aussehen.
Das Feld für den API-Schlüssel wird von der Benutzeroberfläche maskiert dargestellt.

![Agent-Canvas-Erststart-LLM-Advanced-Einstellungen mit dem Lemonade-Modell und der lokalen Basis-URL](assets/01-llm-advanced-settings.png)

Wählen Sie dann **All** aus und legen Sie die zusätzlichen Felder für das lokale Modell fest:

1. Scrollen Sie zu **Custom Tokenizer** und setzen Sie es auf `Qwen/Qwen3.6-35B-A3B`.
2. Scrollen Sie zu **LiteLLM Extra Body** und setzen Sie es auf `{"enable_thinking": true}`.
3. Klicken Sie auf **Next**.

![Agent-Canvas-Erststart-LLM-Tab „All“ mit dem benutzerdefinierten Qwen-Tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent-Canvas-Erststart-LLM-Tab „All“ mit konfiguriertem LiteLLM Extra Body](assets/03-llm-all-extra-body-settings.png)

Die LLM-Einstellungen sollten Folgendes anzeigen:

| Feld | Wert |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Das Präfix `openai/` teilt LiteLLM mit, dass OpenAI-kompatible Anforderungsformatierung gegenüber dem Lemonade-Endpunkt verwendet werden soll.
Der benutzerdefinierte Tokenizer ist der ursprüngliche Hugging-Face-Tokenizer für das GGUF-Modell; er ermöglicht es OpenHands, dieselben Chat-Template-Tokens zu zählen, die der lokale Modellserver sieht.
Das aktuelle Erststart-LLM-Formular zeigt keine Condenser-Einstellungen an.
Wenn Ihr Agent-Canvas-Build später Condenser-Einstellungen unter **Settings > LLM** anzeigt, verwenden Sie `llm_summarizing` und setzen Sie die maximale Tokenanzahl unterhalb des Lemonade-Kontextfensters, zum Beispiel `56000`.

## 5. GitHub- und Slack-MCP-Server installieren

Öffnen Sie in der Agent-Canvas-Benutzeroberfläche **Customize** (oder **Settings > MCP**), um die MCP-Server hinzuzufügen, die dem Agenten Tools für GitHub und Slack bereitstellen.
Token-Werte werden nur an Ihren lokalen Agent Server gesendet und als verschlüsselte Einstellungen gespeichert.

<!-- @os:windows -->
> **Windows (Docker):** Die unten genannten `npx`-MCP-Server-Befehle laufen im Container, der bereits Node.js enthält, sodass auf dem Host nichts Zusätzliches installiert wird.
> Da `.openhands` eingebunden ist, bleiben die MCP-Server und ihre Tokens über Container-Neustarts hinweg erhalten.
<!-- @os:end -->

### GitHub-MCP-Server

Fügen Sie einen neuen MCP-Server mit diesen Einstellungen hinzu:

| Feld | Wert |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = Ihr GitHub-Token |

Verwenden Sie ein GitHub-Token mit Lesezugriff auf das Repository, das zusammengefasst werden soll.

### Slack-MCP-Server

Fügen Sie einen zweiten MCP-Server mit diesen Einstellungen hinzu:

| Feld | Wert |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = Ihre Digest-Kanal-ID |

Setzen Sie `SLACK_CHANNEL_IDS` auf die Digest-Kanal-ID (denselben Wert wie `SLACK_DIGEST_CHANNEL`), damit der Agent nicht jeden Slack-Kanal durchblättern muss.

Nachdem Sie beide Server hinzugefügt haben, verwenden Sie die Schaltfläche **Test** bei jedem, um zu bestätigen, dass die Verbindung funktioniert und Tools angekündigt werden.
Der GitHub-Server sollte GitHub-Tools auflisten, und der Slack-Server sollte Slack-Tools auflisten.

![Agent-Canvas-MCP-Seite mit installierten GitHub- und Slack-Servern](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Erstellen Sie die Digest-Automatisierung

Öffnen Sie in der Agent-Canvas-Benutzeroberfläche die Seite **Automations** und erstellen Sie eine neue Automatisierung:

1. Wählen Sie **Create automation** und wählen Sie den Typ **Prompt preset**.
2. Setzen Sie **Name** auf `GitHub Development Digest to Slack`.
3. Setzen Sie **Prompt** auf den folgenden Text und ersetzen Sie die Platzhalter für Repository und Kanal durch Ihre Werte:

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

4. Setzen Sie **Trigger** auf **Cron** mit dem Zeitplan `0 9 * * 1-5` (9 Uhr an Wochentagen) und setzen Sie **Timezone** auf Ihre Zeitzone, zum Beispiel `America/New_York`.
5. Setzen Sie **Timeout** auf `900` Sekunden.
6. Speichern Sie die Automatisierung.

Die Detailseite der Automatisierung zeigt die neue Automatisierung mit ihrem Cron-Trigger und dem generierten Prompt-Preset-Einstiegspunkt.

![Agent-Canvas-Automatisierungsdetails nach der Erstellung](assets/05-automation-created.png)
## 7. Testen Sie die Automatisierung

Klicken Sie auf der Detailseite der Automatisierung in der Agent Canvas UI:

1. Klicken Sie auf **Run now** (oder **Dispatch**), um die Automatisierung sofort einmal auszuführen.
2. Beobachten Sie die Liste der Ausführungen auf derselben Seite. Der neueste Lauf sollte in den Status `COMPLETED` wechseln.
3. Öffnen Sie Ihren Ziel-Slack-Kanal. Er sollte den generierten Digest enthalten.

Sie müssen nicht auf den Cron-Zeitplan warten—**Run now** löst eine Ausführung auf Anfrage aus, sodass Sie den Prompt, die MCP-Verbindungen und das Posten in Slack überprüfen können, bevor Sie sich auf den Zeitplan verlassen.

![Agent Canvas-Automatisierungslauf erfolgreich abgeschlossen](assets/06-automation-run-completed.png)

![Slack-Kanal zeigt den generierten OpenHands-Digest](assets/07-slackbot-message.png)

## Fehlerbehebung

<!-- @os:windows -->
- **Docker-Port 8000 wird bereits verwendet:** Mappen Sie einen anderen Host-Port, zum Beispiel `docker run ... -p 8080:8000 ...`, und öffnen Sie `http://localhost:8080/canvas`.
- **`docker pull` schlägt mit einem Anmeldeinformationsfehler fehl** (zum Beispiel „A specified logon session does not exist"): Führen Sie den Pull aus einer interaktiven Windows-Sitzung aus, oder laden Sie das Image vorab herunter. Das Image ist öffentlich, sodass kein `docker login` erforderlich ist.
- **Die UI lädt, aber das Backend ist fehlerhaft:** Beim ersten Start wird die Agent-Server-Umgebung innerhalb des Containers erstellt. Warten Sie eine Minute und aktualisieren Sie die Seite, dann prüfen Sie `docker logs <container>` auf den Fortschritt.
- **Agent Canvas kann Lemonade nicht vom Container aus erreichen:** Setzen Sie die LLM-**Base URL** auf `http://host.docker.internal:13305/api/v1` (nicht `127.0.0.1`), und stellen Sie sicher, dass Lemonade auf dem Windows-Host läuft.
<!-- @os:end -->

- **Lemonade ist nicht aktiv:** Starten Sie es mit dem Befehl `lemonade run "${LEMONADE_MODEL}"` aus Schritt 1 neu und führen Sie dann den Health-Check erneut aus.
- **`npm install -g` schlägt mit einem Berechtigungsfehler fehl:** Konfigurieren Sie unter Linux oder WSL ein benutzereigenes globales npm-Verzeichnis, fügen Sie es Ihrer Shell-Startdatei hinzu und installieren Sie Agent Canvas erneut:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Wenn Sie `zsh` verwenden, fügen Sie dieselbe `export PATH=...`-Zeile stattdessen zu `~/.zshrc` hinzu.
- **Agent Canvas lehnt die LLM-Einstellungen nach dem Setzen von `custom_tokenizer` ab:** Installieren Sie `transformers` in der Python-Umgebung des Agent Servers, starten Sie Agent Canvas bei Bedarf neu, und versuchen Sie erneut, die LLM-Einstellungen zu speichern. OpenHands benötigt Transformers, um die Tokenizer-Chat-Vorlage zu laden, wenn `custom_tokenizer` gesetzt ist.
- **Agent Canvas kann Lemonade nicht erreichen:** Überprüfen Sie `curl -fsS "${LEMONADE_BASE_URL}/health"` und stellen Sie sicher, dass die im LLM-Formular bei der Erstbenutzung oder unter **Settings > LLM** eingegebene Base-URL mit dem laufenden lokalen Endpunkt oder HTTPS-Tunnel übereinstimmt.
- **Die LLM-Einstellungen wurden nicht gespeichert:** Stellen Sie sicher, dass Sie nach der Eingabe der Werte auf **Next** geklickt haben. Öffnen Sie **Settings > LLM** erneut, um zu überprüfen, ob die Werte übernommen wurden.
- **GitHub MCP kann private Repositories nicht sehen:** Stellen Sie sicher, dass das GitHub-Token Lesezugriff auf das Ziel-Repository hat und dass die MCP-**Test**-Schaltfläche in **Customize** GitHub-Tools anzeigt.
- **Slack kann Kanäle lesen, aber nicht posten:** Laden Sie die Slack-App in den Ziel-Kanal ein und stellen Sie sicher, dass der Bot `chat:write` besitzt.
- **Die Automatisierung listet zu viele Slack-Kanäle auf:** Verwenden Sie eine Slack-Kanal-ID und setzen Sie `SLACK_CHANNEL_IDS` auf dem Slack-MCP-Server in **Customize**.
- **Der Automatisierungslauf schlägt fehl oder überschreitet den Kontext:** Stellen Sie sicher, dass Lemonade mit `ctx_size=65536` gestartet wurde, dass bei der OpenHands-LLM `custom_tokenizer` gesetzt ist, und verwenden Sie ein explizites Repository mit GitHub-Ergebnismengen, die auf 3 bis 5 Elemente begrenzt sind. Wenn Ihre Agent-Canvas-Version Condenser-Einstellungen bietet, setzen Sie die maximale Token-Anzahl des Condensers unter das Lemonade-Kontextfenster.

## Nächste Schritte

- Fügen Sie einen wöchentlichen, nur release-bezogenen Digest hinzu.
- Fügen Sie eine durch GitHub-Ereignisse ausgelöste Automatisierung für schnellere PR- oder Push-Benachrichtigungen hinzu.
- Leiten Sie denselben Digest in Notion, Linear oder ein anderes MCP-gestütztes Tool.

## Ressourcen

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-Dokumentation](https://lemonade-server.ai/docs)
- [OpenHands Extensions Repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-Server](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-Paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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