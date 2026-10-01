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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Übersicht

[OpenHands](https://github.com/All-Hands-AI/OpenHands) ist ein KI-Softwareagent,
der Code schreiben, Befehle ausführen, im Web browsen und Dateien in einem
echten Workspace bearbeiten kann. Anstatt Vorschläge aus einem Chatfenster
abzuschreiben, richten Sie den Agenten auf einen Projektordner aus und lassen
ihn die Arbeit erledigen: eine Funktion implementieren, einen Fehler beheben,
Tests schreiben oder eine Codebasis erklären.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) ist die empfohlene
Browser-UI zum Ausführen von OpenHands. Ein einziger Befehl `agent-canvas`
startet den Agent-Server, das Automatisierungs-Backend und das Web-Frontend
zusammen, sodass Sie eine Konversation mit dem Agenten aus Ihrem Browser heraus
steuern können.

Damit alles auf Ihrem AMD-System bleibt, spricht der Agent mit einem lokalen
Modell, das von Lemonade Server bereitgestellt wird. Lemonade stellt dieses
Modell über eine OpenAI-kompatible API bereit, sodass Agent Canvas es wie
jeden anderen OpenAI-artigen Endpunkt konfigurieren kann, während das Modell,
Ihr Code und der Konversationskontext auf Ihrem Rechner verbleiben.

In diesem Playbook starten Sie ein lokales Modell, starten Agent Canvas,
richten es auf dieses Modell aus und führen Ihre erste Coding-Aufgabe mit
einem echten Projektordner aus.

## Was Sie lernen werden

- Wie Sie Lemonade Server starten und bestätigen, dass ein lokales Modell auf
  Chat-Anfragen antwortet
- Wie Sie Agent Canvas aus dem npm-Paket installieren und starten
- Wie Sie Agent Canvas so konfigurieren, dass es ein lokales Lemonade-Modell
  als LLM verwendet
- Wie Sie eine OpenHands-Konversation starten und beobachten, wie der Agent
  Dateien bearbeitet und Befehle in einem Workspace ausführt
- Wie Sie überprüfen, was der Agent geändert hat, und ihn mit
  Folgenachrichten steuern

## Kernkonzepte

| Konzept | Was es ist | Wo es in diesem Playbook einzuordnen ist |
| --- | --- | --- |
| Lemonade Server | Eine lokale LLM-Bereitstellungsplattform für AMD-Hardware, die eine OpenAI-kompatible API bereitstellt. Ihre Daten verlassen niemals Ihren Rechner. | Führt das Modell aus, das den Agenten antreibt. |
| OpenHands | Ein KI-Softwareagent, der Dateien liest und bearbeitet, Shell-Befehle ausführt und innerhalb eines Workspace im Web browst. | Der Agent, den Sie über den Chat steuern. |
| Agent Canvas | Die Browser-UI und das Backend, das OpenHands-Konversationen ausführt und Tool-Aufrufe sowie Dateiänderungen anzeigt. | Startet den Stack und beherbergt Ihre Konversation. |
| Workspace | Der Projektordner, den der Agent lesen und ändern darf. | Das Ziel der Bearbeitungen und Befehle des Agenten. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Coding-Agent-Workflows profitieren von einem größeren Modell und Kontextfenster. Verwenden Sie
> mindestens 32 GB Arbeitsspeicher und bevorzugen Sie 64 GB oder mehr für größere GGUF-Modelle.
<!-- @device:end -->

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Voraussetzungen


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Sie benötigen:

- Lemonade Server installiert und in der Lage, das unten genannte Modell bereitzustellen.

<!-- @os:linux -->
- Node.js 22.12 oder höher und `npm` (wird von der `agent-canvas`-CLI verwendet).
- `uv`, den Python-Paketmanager, den Agent Canvas zur Verwaltung der
  Agent-Server-Umgebung verwendet. Falls Ihr System dies noch nicht besitzt,
  installieren Sie es aus dem
  [uv-Installationsleitfaden](https://docs.astral.sh/uv/getting-started/installation/),
  bevor Sie Agent Canvas starten.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop für Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installiert und ausgeführt. Unter Windows läuft der Agent-Canvas-Stack aus
  dem veröffentlichten Docker-Image, das Node.js, `uv` und das Paket
  `@openhands/agent-canvas` enthält, sodass Sie diese nicht auf dem Host
  installieren müssen.
<!-- @os:end -->

- Einen Projektordner, in dem gearbeitet werden soll. Dies kann ein beliebiges
  lokales Git-Repository oder Codeverzeichnis sein, an dem der Agent arbeiten
  soll.

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

## 1. Lemonade Server starten

Starten Sie das Modell über die Lemonade-CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Wählen Sie ein Modell, das zu Ihrer Hardware passt.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) ist ein starkes Coding-Modell, benötigt jedoch einen großen Speicherpool. Wenn Ihr Gerät über begrenzten Arbeitsspeicher oder GPU-VRAM verfügt, wählen Sie stattdessen ein kleineres GGUF-Modell aus der Lemonade-Modellbibliothek und verwenden Sie diese Modell-ID durchgängig in diesem Playbook.

> **Hinweis:** Der erste `lemonade run` lädt das Modell herunter, falls es noch nicht vorhanden ist, was je nach Modellgröße und Ihrer Verbindung eine Weile dauern kann.

Lemonade stellt eine OpenAI-kompatible API bereit unter:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Das lokale Modell überprüfen

Bestätigen Sie, dass Lemonade das ausgewählte Modell bereitstellen kann:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Senden Sie dann eine kleine Chat-Anfrage:

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
## 3. Agent Canvas installieren und starten

<!-- @os:linux -->
Installieren Sie das veröffentlichte Agent-Canvas-Paket global:

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

Starten Sie dann den vollständigen Stack aus einem Terminal:

```bash
agent-canvas
```

Standardmäßig startet Agent Canvas unter `http://localhost:8000`. Öffnen Sie diese
URL in Ihrem Browser. Der Port ist nicht fest vorgegeben — falls 8000 bereits
belegt ist, geben Sie beim Starten von Agent Canvas mit `--port` (oder `-p`)
einen freien Port an:

```bash
agent-canvas --port 3000
```

Öffnen Sie dann stattdessen `http://localhost:3000`. Das lokale Standard-Backend
sollte auf dem Startbildschirm als „healthy“ angezeigt werden.

Der Befehl `agent-canvas` startet den Agent-Server, das Automatisierungs-Backend
und das Web-Frontend gemeinsam. Sie benötigen nur diesen einen Befehl, um
OpenHands lokal auszuführen.

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
Führen Sie unter Windows das veröffentlichte Agent-Canvas-Container-Image mit
Docker Desktop aus. Das Image enthält den Agent-Server, das
Automatisierungs-Backend und das Web-Frontend, sodass Sie Node.js, `uv` oder
die CLI nicht auf dem Host installieren müssen.

Erstellen Sie zunächst die Konfigurations- und Arbeitsbereichsordner, die der
Container einbindet:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Laden Sie das veröffentlichte Image herunter (es ist öffentlich, daher ist
keine Anmeldung erforderlich):

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

Öffnen Sie `http://localhost:8000/canvas` in Ihrem Browser. Falls Port 8000
bereits belegt ist, ordnen Sie einen anderen Host-Port zu, zum Beispiel
`-p 8080:8000`, und öffnen Sie stattdessen `http://localhost:8080/canvas`.

> **Hinweis:** Beim ersten Start wird der Agent-Server innerhalb des Containers
> initialisiert, sodass es eine bis zwei Minuten dauern kann, bis das Backend
> als „healthy“ gemeldet wird.

Die Einbindung von `.openhands` sorgt dafür, dass Ihr LLM-Profil und Ihre
Einstellungen über Container-Neustarts hinweg erhalten bleiben. Der Rest dieses
Leitfadens konfiguriert alles über die Agent-Canvas-Benutzeroberfläche in
Ihrem Browser.

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

## 4. Das lokale LLM konfigurieren

Beim ersten Start öffnet Agent Canvas einen Onboarding-Ablauf. In diesem Ablauf:

1. Belassen Sie **OpenHands** als ausgewählten Agenten und klicken Sie auf **Next**.
2. Wählen Sie unter **Set up your LLM** die Option **Advanced**.
3. Belassen Sie **Authentication** auf **API key**.
4. Setzen Sie **Custom Model** auf `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setzen Sie **Base URL** auf `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > Unter Windows läuft der Stack in einem Container, der den Host unter
   > `127.0.0.1` nicht erreichen kann. Verwenden Sie stattdessen
   > `http://host.docker.internal:13305/api/v1`, damit der containerisierte
   > Agent Lemonade erreichen kann, das auf dem Windows-Host läuft.
   <!-- @os:end -->
6. Geben Sie bei **API Key** einen beliebigen, nicht leeren Platzhalter ein,
   zum Beispiel `lemonade-local`. Lemonade benötigt keinen echten Schlüssel,
   aber der OpenHands-Client benötigt einen Wert zum Senden.
7. Klicken Sie auf **Next**.

Die abgeschlossenen Advanced-Einstellungen sollten wie folgt aussehen. Das
API-Key-Feld wird von der Benutzeroberfläche maskiert.

![Agent Canvas Erststart-LLM-Advanced-Einstellungen mit dem Lemonade-Modell und der lokalen Basis-URL](assets/01-llm-advanced-settings.png)

Agent Canvas speichert diese Werte als LLM-Profil. Wenn Ihre Version Sie
auffordert, dieses Profil zu benennen, verwenden Sie einen Namen ohne
Leerzeichen, zum Beispiel `lemonade-local`. Wenn Sie später das Modell ändern,
öffnen Sie **Settings > LLM** und aktualisieren Sie dieselben Advanced-Felder.
Sie können gespeicherte Profile über die Chat-Eingabe mit dem Befehl `/model`
wechseln.

## 5. Einen Arbeitsbereich öffnen

Der Agent kann nur Dateien innerhalb eines von Ihnen gewählten Arbeitsbereichs
lesen und ändern. Richten Sie Agent Canvas vor dem Start einer Aufgabe auf
Ihren Projektordner aus:

1. Wählen Sie auf dem Startbildschirm **Open Workspace**.
2. Wählen Sie den Ordner, der Ihr Projekt enthält (zum Beispiel ein
   Git-Repository, an dem der Agent arbeiten soll).
3. Starten Sie eine neue Unterhaltung in diesem Arbeitsbereich.

Alles, was der Agent tut — Dateien lesen, Befehle ausführen, Code bearbeiten —
ist auf diesen Arbeitsbereich beschränkt.

![Agent Canvas Startbildschirm nach dem Onboarding](assets/02-agent-canvas-home.png)

## 6. Ihre erste Programmieraufgabe ausführen

Geben Sie bei geöffnetem Arbeitsbereich und ausgewähltem lokalem LLM eine
konkrete Aufgabe in den Chat ein. Eine gute erste Aufgabe ist klein und
überprüfbar, zum Beispiel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Beobachten Sie den Unterhaltungsverlauf. OpenHands wird:

- den Arbeitsbereich lesen, um die Struktur zu verstehen.
- `hello.py` mit der angeforderten Funktion und dem Testblock erstellen.
- optional `python3 hello.py` ausführen, um die Ausgabe zu überprüfen.
- im Chat berichten, was es getan hat, sowie jegliche Befehlsausgabe.

Sie sollten sehen, wie die neue Datei im Arbeitsbereich erscheint, und die
abschließende Nachricht des Agenten sollte die vorgenommene Änderung
beschreiben. Dies ist der entscheidende Moment: Der Agent hat echten Code in
Ihrem Projektordner geschrieben und ausgeführt.

## 7. Den Agenten überprüfen und steuern

Nachdem der Agent einen Schritt abgeschlossen hat, überprüfen Sie seine Arbeit,
bevor Sie den nächsten Schritt akzeptieren:

- **Dateiänderungen**: Verwenden Sie den Dateibrowser des Arbeitsbereichs oder
  die Diff-Ansicht des Agenten, um genau zu sehen, was hinzugefügt, geändert
  oder gelöscht wurde.
- **Befehlsausgabe**: Erweitern Sie einen vom Agenten ausgeführten Befehl, um
  stdout, stderr und den Exit-Code zu sehen.
- **Nachfragen**: Wenn das Ergebnis nicht Ihren Erwartungen entspricht,
  antworten Sie in derselben Unterhaltung mit einer Korrektur. Der Agent
  behält den vorherigen Kontext bei und arbeitet an denselben Dateien weiter.

Wenn der Test beispielsweise nicht die erwartete Begrüßung ausgibt, antworten
Sie:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Der Agent liest die Datei erneut, führt den Befehl aus, diagnostiziert das
Problem und bearbeitet die Datei erneut — alles innerhalb derselben
Unterhaltung.
## Fehlerbehebung

<!-- @os:linux -->
- **`agent-canvas` befindet sich nicht im PATH:** Führen Sie eine erneute Installation mit
  `npm install -g @openhands/agent-canvas` durch und stellen Sie sicher, dass sich das globale npm-Binärverzeichnis
  im PATH befindet, bevor `agent-canvas` aus einem neuen
  Terminal gestartet werden kann.
- **`npm install -g` schlägt mit einem Berechtigungsfehler fehl:** Konfigurieren Sie ein benutzereigenes
  globales npm-Verzeichnis, öffnen Sie dann das Terminal erneut und installieren Sie Agent Canvas noch einmal.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` fehlt:** Installieren Sie es über
  [den uv-Installationsleitfaden](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas verwendet `uv` zur Verwaltung der Python-Umgebung des Agent-Servers.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` oder `docker run` kann keine Verbindung herstellen:** Stellen Sie sicher, dass Docker Desktop
  ausgeführt wird (das Wal-Symbol befindet sich in der Taskleiste) und dass die Engine
  vollständig gestartet ist. `docker version` sollte sowohl einen Client- als auch einen Server-Abschnitt
  ausgeben.
- **Der Container startet, aber das Backend wird nie fehlerfrei:** Beim ersten
  Start wird der Agent Server im Container initialisiert; geben Sie ihm ein bis
  zwei Minuten Zeit und prüfen Sie anschließend `docker logs <container>` auf Fehler.
- **Der Container kann Lemonade nicht erreichen:** Der Container erreicht den Host über
  `host.docker.internal`. Stellen Sie mit
  `lemonade status` sicher, dass Lemonade auf dem Windows-Host bereitgestellt wird, und verwenden Sie
  `http://host.docker.internal:13305/api/v1` als Basis-URL bei der Konfiguration des LLM.
<!-- @os:end -->

- **Die Benutzeroberfläche wird geladen, aber das Backend zeigt „nicht fehlerfrei“ an:** Warten Sie ein bis zwei Minuten, bis der
  Agent Server den Start abgeschlossen hat, und aktualisieren Sie dann die Seite. Bleibt der Zustand „nicht fehlerfrei“ bestehen, starten Sie
  den Stack neu und prüfen Sie die Protokolle auf Fehler.
- **Lemonade-Chatanfragen schlagen mit einem Verbindungsfehler fehl:** Stellen Sie sicher, dass
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` erfolgreich ist und dass
  Lemonade das Modell weiterhin bereitstellt, was Sie mit `lemonade status` prüfen können.
- **Der Agent gibt einen Fehler mit einer Meldung zur Kontextlänge oder zum Token-Limit aus:** Beginnen Sie eine
  neue Unterhaltung, damit der Agent keinen übermäßig großen Verlauf mitführt. Tritt der Fehler weiterhin
  auf, starten Sie Lemonade mit einer größeren `ctx_size` als dem Standardwert
  65536 neu (zum Beispiel `ctx_size=131072`), sofern der Arbeitsspeicher dies zulässt.
- **Der Agent liefert minderwertige oder unvollständige Bearbeitungen:** Wechseln Sie zu einem größeren
  Modell in Lemonade, oder geben Sie dem Agenten eine kleinere, konkretere Aufgabe und lassen Sie ihn diese
  abschließen, bevor Sie die nächste Änderung anfordern.

## Nächste Schritte

- Probieren Sie eine größere Aufgabe im gleichen Arbeitsbereich aus, wie zum Beispiel das Hinzufügen einer Unit-Test-Datei oder
  das Beheben eines bekannten Fehlers, und überprüfen Sie den Diff des Agenten, bevor Sie die Änderung übernehmen.
- Verbinden Sie unter **Customize** einen MCP-Server wie GitHub oder Slack, damit
  der Agent Issues lesen oder Updates posten kann, während er arbeitet.
- Speichern Sie mehrere LLM-Profile (ein schnelles kleines Modell und ein leistungsstärkeres großes Modell) und
  wechseln Sie während einer Unterhaltung mit `/model` zwischen ihnen.
- Fahren Sie mit [OpenHands-Automatisierungen](https://docs.openhands.dev/openhands/usage/automations/overview) fort, um
  wiederkehrende Entwicklungsabläufe in geplante oder ereignisgesteuerte Agentenläufe umzuwandeln.

## Ressourcen

- [OpenHands-Dokumentation](https://docs.openhands.dev/)
- [Agent Canvas Übersicht](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas Einrichtung](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-Profile und Modellkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server Dokumentation](https://lemonade-server.ai/docs)

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