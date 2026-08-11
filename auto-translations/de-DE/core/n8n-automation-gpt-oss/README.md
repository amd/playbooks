<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Übersetzung

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Überblick

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Dieses Playbook erfordert mindestens **32 GB** Systemspeicher.
<!-- @device:end -->

n8n ist eine Workflow-Automatisierungsplattform, mit der Sie Apps und Dienste über einen visuellen, knotenbasierten Editor verbinden können.

Dieses Playbook zeigt Ihnen, wie Sie einen KI-gestützten Finanznachrichten-Zusammenfasser einrichten, der den Business-Bereich von AP News durchsucht, wichtige Schlagzeilen extrahiert und ein lokales LLM auf Ihrem System verwendet, um eine investorenorientierte Zusammenfassung zu erstellen.

## Was Sie lernen werden

- Wie Sie n8n installieren und starten
- Importieren und Konfigurieren eines vorgefertigten Workflows
- Verbindung zu Lemonade über die native n8n-Integration
- Verständnis der Workflow-Knoten und des Datenflusses

## Was ist Lemonade?

[Lemonade](https://lemonade-server.ai) ist eine lokale LLM-Serving-Plattform, die für AMD-Hardware entwickelt wurde. Sie bietet eine OpenAI-kompatible API, die vollständig auf Ihrem Rechner läuft – Ihre Daten verlassen niemals Ihr Gerät.

In diesem Playbook verwenden wir Lemonade, um ein lokales LLM bereitzustellen, mit dem sich n8n für KI-gestützte Aufgaben verbindet.

n8n enthält einen **nativen Lemonade-Knoten** (`Lemonade Chat Model`), der eine erstklassige Integration bietet – keine manuelle Konfiguration erforderlich. Dies macht das Verbinden Ihres lokalen LLM mit Automatisierungs-Workflows unkompliziert.

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Software-Voraussetzungen
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


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
  "max_tokens": 32
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Installieren von n8n
<!-- @os:windows -->
Installieren Sie n8n global mit npm.

> **Hinweis**: Möglicherweise sehen Sie einige npm-Warnungen. Dies ist zu erwarten.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie anpassen (z. B.
> auf RemoteSigned oder Unrestricted setzen), bevor sie einige PowerShell-Befehle ausführen.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH-Problem**: Wenn `n8n --version` mit „Befehl nicht gefunden“ antwortet, stellen Sie sicher, dass sich Ihr npm-Global-Bin-Verzeichnis im `PATH` des Benutzers befindet. Der übliche Installationspfad ist `C:\Users\<username>\AppData\Roaming\npm`.
> Fügen Sie dies dem Benutzerpfad hinzu (Systemumgebungsvariablen bearbeiten > Umgebungsvariablen > Benutzerpfad bearbeiten) und starten Sie das Terminal neu.

<!-- @os:end -->

<!-- @os:linux -->
Wir verwenden nun den Podman-Dienst, um unsere n8n-Installation zu containerisieren.

Bitte laden Sie Folgendes in ein Verzeichnis Ihrer Wahl herunter: [compose.yml](assets/compose.yml)

Führen Sie in diesem Verzeichnis den folgenden Befehl aus:
```bash
podman compose up -d
```

Dies sollte n8n installieren und in einen persistenten Speicher schreiben.

Starten Sie n8n, indem Sie `localhost:5678` in Ihre Browser-Adresszeile eingeben.
<!-- @os:end -->

<!-- @os:windows -->
## Starten von n8n

Starten Sie n8n über das Terminal:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n startet einen lokalen Webserver. Drücken Sie `'o'` oder öffnen Sie Ihren Browser unter `http://localhost:5678`, um auf den Editor zuzugreifen.
<!-- @os:end -->


> **Tipp**: Lassen Sie das Terminal-Fenster geöffnet, während Sie n8n verwenden. Das Schließen könnte den Server stoppen.

## Starten von Lemonade

Lemonade ist der lokale Server, der ein Modell ausführt und sich mit n8n verbindet.

<!-- @os:linux -->
Öffnen Sie die Lemonade-GUI, indem Sie auf das Lemonade-Symbol in der Taskleiste klicken. Von hier aus können Sie Modelle und Backends durchsuchen und die vorinstallierten Modelle laden.
<!-- @os:end -->

<!-- @os:windows -->
Öffnen Sie die Lemonade-GUI, indem Sie auf das Lemonade-Symbol klicken. Klicken Sie mit der rechten Maustaste auf das Tray-Symbol, um die App zu öffnen. Anschließend können Sie Modelle und Backends hinzufügen und die vorinstallierten Modelle laden.
<!-- @os:end -->

>**Tipp**: Sobald sie läuft, ist die Lemonade-GUI auch unter http://localhost:13305 erreichbar

Alternativ können Sie ein Terminal öffnen und `lemonade list` ausführen, um zu sehen, welche Modelle installiert sind. Führen Sie dann Folgendes aus:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Einrichten des Workflows

### Schritt 1: Bei n8n registrieren oder anmelden

Wenn Sie n8n zum ersten Mal öffnen, werden Sie aufgefordert, ein Konto zu erstellen oder sich anzumelden:

1. Öffnen Sie `http://localhost:5678` in Ihrem Browser
2. Erstellen Sie ein neues lokales Konto mit Ihrer E-Mail-Adresse, oder melden Sie sich an, falls Sie bereits eines haben
3. Nach der Anmeldung sehen Sie das n8n-Dashboard

> **Tipp**: Wenn Sie von Ihrem Konto ausgesperrt sind, versuchen Sie `n8n user-management:reset`

### Schritt 2: Den Workflow importieren

Wir haben einen vorgefertigten Workflow bereitgestellt, den Sie direkt importieren können:

1. Laden Sie die folgende Workflow-Datei herunter: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Klicken Sie auf **Start from Scratch**, um den Workflow-Editor zu öffnen. Alternativ klicken Sie oben links auf die Schaltfläche +, und dann auf **Add workflow**.
3. Klicken Sie oben rechts auf das Menü **...** (drei Punkte) und wählen Sie **Import from file**
4. Wählen Sie die heruntergeladene Datei `financial-news-workflow.json` aus
5. Der Workflow erscheint auf der Arbeitsfläche
### Schritt 3: Den Workflow verstehen

Der importierte Workflow enthält 9 verbundene Nodes:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Zweck |
|------|-------|
| **When clicking 'Execute workflow'** | Manueller Trigger zum Starten des Workflows |
| **Fetch Financial News Webpage** | HTTP-GET-Anfrage an `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait-Node, um sicherzustellen, dass der Seiteninhalt vollständig geladen ist |
| **Extract News Headlines & Text** | HTML-Node, der Schlagzeilen, redaktionelle Empfehlungen, Top-Nachrichten und regionale Nachrichten mithilfe von CSS-Selektoren extrahiert |
| **Clean Extracted News Data** | Set-Node, der alle extrahierten Daten in einem einzigen Textfeld zusammenführt |
| **AI Financial News Summarizer** | KI-Agent, der die Nachrichten mit einem Systemprompt für Finanzanalysten verarbeitet |
| **Lemonade Chat Model** | Verbindet sich mit Ihrem lokalen Lemonade-Server, auf dem das LLM läuft |
| **Structured Output Parser** | Formatiert die KI-Ausgabe als strukturiertes JSON |
| **Convert to File** | Konvertiert die Zusammenfassung in eine herunterladbare Datei |

### Schritt 4: Lemonade-Anmeldedaten konfigurieren

Bevor Sie den Workflow ausführen, müssen Sie ihn mit Ihrem lokalen Lemonade-Server verbinden:

1. Doppelklicken Sie in n8n auf den Node **Lemonade Chat Model**
2. Wählen Sie im Dropdown-Menü **Credential to connect with** die Option **Create New Credential**
3. Geben Sie die Werte aus der folgenden Tabelle ein und klicken Sie auf Speichern.
4. Wählen Sie das entsprechende Modell aus, das Sie in Lemonade Server geladen haben.

  | Feld | Wert |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Hinweis**: Führen Sie vor dem Testen `lemonade status` in einem Terminal aus, um zu bestätigen, dass der Lemonade-Server läuft.
<!-- @device:halo_box -->
> Dieser Workflow verwendet GPT-OSS-120B, das bereits in Lemonade vorinstalliert ist. Sie können dies in den Einstellungen des Lemonade Chat Model-Nodes auf andere geladene Modelle ändern.
<!-- @device:end -->

### Schritt 5: Den Workflow testen

1. Stellen Sie sicher, dass Lemonade läuft und ein Modell geladen ist
2. Klicken Sie unten in der Mitte der Arbeitsfläche auf **Execute workflow**
3. Beobachten Sie, wie jeder Node von links nach rechts ausgeführt wird – sie werden grün, sobald sie abgeschlossen sind
4. Doppelklicken Sie auf den Node **AI Financial News Summarizer**, um die generierte Zusammenfassung im unteren Bereich anzuzeigen.
5. Doppelklicken Sie auf den Node **Convert to File**, um die entsprechende Textdatei im unteren Bereich herunterzuladen.

## Den KI-Agenten verstehen

Der AI Financial News Summarizer verwendet einen Systemprompt, der für Finanzanalysen konzipiert ist:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Der Agent erhält die bereinigten Nachrichtendaten und gibt eine strukturierte Zusammenfassung mit Marktstimmung aus.

### Ihren Workflow speichern

Klicken Sie oben auf den Workflow-Namen und benennen Sie ihn bei Bedarf um. Workflows werden während der Arbeit automatisch gespeichert.

## Nächste Schritte

- **Automatisierung planen**: Ersetzen Sie den Manual Trigger durch einen **Schedule Trigger**, um den Workflow täglich auszuführen
- **Benachrichtigungen senden**: Fügen Sie einen **Discord**-, **Slack**- oder **Email**-Node hinzu, um Zusammenfassungen zu erhalten
- **Verschiedene Modelle ausprobieren**: Ändern Sie das Modell im Lemonade Chat Model-Node, um mit unterschiedlichen LLMs zu experimentieren
- **Extraktion anpassen**: Ändern Sie die CSS-Selektoren des HTML-Extract-Nodes, um andere Nachrichtenbereiche anzusteuern
- **Verschiedene Backends ausprobieren**: n8n unterstützt außerdem [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio und andere lokale LLM-Backends

### n8n-Vorlagen erkunden

n8n bietet Hunderte vorgefertigter Workflow-Vorlagen. Durchsuchen Sie die offizielle Vorlagenbibliothek unter:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Suchen Sie nach „AI“, „LLM“ oder „automation“, um Workflows zu finden, die Sie importieren und anpassen können.

Weitere Informationen finden Sie in der [n8n-Dokumentation](https://docs.n8n.io/).

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