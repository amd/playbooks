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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Überblick

Ollama ist ein beliebtes, leichtgewichtiges Tool zum lokalen Ausführen großer Sprachmodelle. Es übernimmt das Herunterladen von Modellen, die Quantisierung und die Bereitstellung hinter einer einfachen Befehlszeilenschnittstelle und Desktop-App, sodass Sie innerhalb weniger Minuten mit einem LLM chatten können.

Dieses Playbook führt Sie durch die Installation von Ollama, das Herunterladen des GPT-OSS 20B-Modells und eine Unterhaltung damit, sowohl über das Terminal als auch über die Desktop-App.

## Was Sie lernen werden

- Wie Sie Ollama auf Ihrem System installieren und starten
- Das GPT-OSS 20B-Modell lokal herunterladen und ausführen
- Mit Modellen über die CLI chatten
- Modelle programmatisch über die REST-API abfragen

## Einstellen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen
> **Hinweis**: Wenn VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

<!-- @require:driver -->

### Ollama installieren

<!-- @os:windows -->

1. Laden Sie das Installationsprogramm von [ollama.com/download](https://ollama.com/download) herunter.
2. Führen Sie das `.exe`-Installationsprogramm aus und folgen Sie den Anweisungen.
3. Nach der Installation läuft Ollama als Hintergrunddienst und ist über das Terminal, die Desktop-App und das System-Tray zugänglich.

Überprüfen Sie die Installation, indem Sie ein Terminal öffnen und Folgendes ausführen:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

Sie sollten die installierte Versionsnummer in der Konsole ausgegeben sehen.
<!-- @os:end -->

<!-- @os:linux -->

Führen Sie das offizielle Installationsskript aus:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Überprüfen Sie die Installation:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

Sie sollten die installierte Versionsnummer in der Konsole ausgegeben sehen.
<!-- @os:end -->

## Ihr erstes Modell herunterladen

Ollama verwaltet Modelle über eine Registry, ähnlich wie bei Container-Images. Um GPT-OSS 20B herunterzuladen:

```bash
ollama pull gpt-oss:20b
```

Dies lädt die Modellgewichte auf Ihren lokalen Rechner herunter (ca. 12 GB). Der Download erfolgt nur einmal, nachfolgende Ausführungen laden das Modell von der Festplatte.

Sie können bestätigen, dass das Modell verfügbar ist, mit:

```bash
ollama list
```

Sie sollten `gpt-oss:20b` in der Ausgabe zusammen mit Größe und letztem Änderungsdatum sehen.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### Modellbenennung

Ollama-Modellnamen folgen dem Format `name:tag`. Der Tag gibt üblicherweise die Parameteranzahl oder die Quantisierungsvariante an. Einige nützliche Befehle zur Modellverwaltung:

| Befehl | Beschreibung |
|---------|-------------|
| `ollama list` | Alle heruntergeladenen Modelle anzeigen |
| `ollama pull <model>` | Ein Modell herunterladen, ohne es auszuführen |
| `ollama rm <model>` | Ein Modell entfernen, um Speicherplatz freizugeben |
| `ollama show <model>` | Modell-Metadaten und -Parameter anzeigen |

## Chatten über das Terminal

Starten Sie eine interaktive Chat-Sitzung direkt über die Befehlszeile:

```bash
ollama run gpt-oss:20b
```

Ollama lädt das Modell in den Speicher und öffnet eine Eingabeaufforderung. Versuchen Sie, etwas zu fragen:

```
>>> What is the capital of France and why is it historically significant?
```

Das Modell streamt seine Antwort Token für Token direkt im Terminal. Geben Sie `/bye` ein oder drücken Sie `Ctrl+D`, um die Sitzung zu beenden.

> **Tipp**: Der erste Durchlauf dauert einige Sekunden, um das Modell in den Speicher zu laden. Nachfolgende Prompts innerhalb derselben Sitzung reagieren viel schneller, da das Modell geladen bleibt.

<!-- @os:windows -->
## Chatten über die Desktop-App

Ollama wird auch mit einer Desktop-Anwendung ausgeliefert, die eine übersichtliche Chat-Oberfläche für die Interaktion mit Ihren Modellen bietet.

Öffnen Sie **Ollama** über das Startmenü oder klicken Sie auf das Ollama-Symbol im System-Tray und wählen Sie **Open Ollama**.

Sobald die App geöffnet ist:

1. Klicken Sie in der Seitenleiste auf **New Chat**.
2. Wählen Sie **gpt-oss:20b** aus dem Modell-Dropdown-Menü in der unteren rechten Ecke des Chat-Eingabebereichs.
3. Geben Sie eine Nachricht ein und drücken Sie die Eingabetaste, um den Chat zu starten.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

Die Desktop-App speichert einen Verlauf Ihrer Unterhaltungen in der Seitenleiste, sodass Sie frühere Chats leicht wiederfinden können.
<!-- @os:end -->

## Verwendung der REST-API

Nach der Installation läuft Ollama als Hintergrunddienst und stellt eine REST-API unter `http://localhost:11434` bereit, die Sie nutzen können, um Modelle in Ihre eigenen Anwendungen und Skripte zu integrieren.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### Eine Antwort im Terminal generieren

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

Die Antwort ist ein JSON-Objekt, das die Ausgabe des Modells im Feld `response` enthält.


### Python-Beispiel
Nachdem wir die Ollama-API nun programmatisch ansprechen können, rufen wir sie von Python aus auf.

#### Eine virtuelle Umgebung im Terminal erstellen

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### Eine Python-Datei erstellen
Verwenden Sie im selben Verzeichnis VS Code oder einen anderen Editor, um eine .py-Datei zu erstellen, und kopieren Sie den folgenden Code hinein. Führen Sie die Datei dann in Ihrer aktivierten Umgebung mit `python your_file_name.py` aus.

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### Wichtige API-Endpunkte

| Endpunkt | Methode | Zweck |
|----------|--------|---------|
| `/api/generate` | POST | Einzelne Textgenerierung |
| `/api/chat` | POST | Mehrteilige Unterhaltung mit Nachrichtenverlauf |
| `/api/tags` | GET | Verfügbare Modelle auflisten |
| `/api/show` | POST | Modelldetails anzeigen |
| `/api/pull` | POST | Ein Modell aus der Registry herunterladen |

Die vollständige API-Referenz finden Sie in der [Ollama API-Dokumentation](https://github.com/ollama/ollama/blob/main/docs/api.md).
## Nächste Schritte

- **Verschiedene Modelle ausprobieren**: Durchsuchen Sie die [Ollama-Modellbibliothek](https://ollama.com/library), um Hunderte verfügbarer Modelle zu entdecken, von kleinen Coding-Assistenten bis hin zu großen Reasoning-Modellen.
- **Benutzerdefinierte Modelle erstellen**: Verwenden Sie eine [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md), um benutzerdefinierte Systemprompts, die Temperatur und andere Parameter für ein maßgeschneidertes Erlebnis festzulegen.
- **Mit der API entwickeln**: Nutzen Sie die [Python](https://github.com/ollama/ollama-python)- oder [JavaScript](https://github.com/ollama/ollama-js)-Clientbibliotheken, um Ollama in Ihre Anwendungen zu integrieren.
- **Mit Frontends verbinden**: Kombinieren Sie Ollama mit Tools wie [Open WebUI](https://github.com/open-webui/open-webui) für eine funktionsreiche Chat-Oberfläche mit Suche, Personas und Dokumenten-Upload.

Weitere Informationen finden Sie in der [Ollama-Dokumentation](https://github.com/ollama/ollama/blob/main/README.md).