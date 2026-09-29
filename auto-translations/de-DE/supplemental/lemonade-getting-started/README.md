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

## Übersicht

🍋 **Lemonade** ist ein Open-Source-Server für lokale KI, mit dem Sie große Sprachmodelle (LLMs), Bildgeneratoren und Audiomodelle direkt auf Ihrer eigenen Hardware ausführen können. Er stellt die Modelle über die branchenübliche **OpenAI-API** bereit, sodass jede App, die mit OpenAI funktioniert, sofort auch mit Lemonade funktioniert. Am Ende dieses Playbooks werden Sie Lemonade verwenden, um Modelle lokal auf Ihrem Rechner auszuführen.

## Was Sie lernen werden

Am Ende dieses Playbooks können Sie:

* **Lemonade Server installieren** und überprüfen, dass er läuft.
* **Ein LLM herunterladen und damit chatten** mit nur einem Befehl.
* **Die Web-UI erkunden** und verschiedene Modalitäten wie Bilderkennung (Vision), Sprache-zu-Text und Bildgenerierung ausprobieren.
* **GPU-Backends wechseln** zwischen Vulkan und AMD ROCm™-Software.
* **Eine Python-App erstellen**, die von einem lokalen LLM über die OpenAI-kompatible API angetrieben wird.
<!-- @device:halo_box,halo,stx,krk -->
* **Modelle auf der AMD Neural Processing Unit (NPU) ausführen** mithilfe der Ausführungsmodi Hybrid und FLM auf AMD Ryzen™ AI-Hardware.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie Folgendes haben:

- Einen PC mit **Windows 11** oder einer unterstützten **Linux**-Distribution (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** werden für das in Schritt 1–7 verwendete Laufzeitmodell empfohlen (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** werden empfohlen, wenn Sie das größere Modell zur Codegenerierung aus Schritt 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB) verwenden möchten.
- **~4–30 GB freien Festplattenspeicher**, je nachdem, welche Modelle Sie herunterladen. Das größte Modell in diesem Leitfaden ist etwa 20 GB groß.
- **Python 3.10–3.13** (verwendet im Abschnitt zur Python-App)
- Eine Internetverbindung (kabelgebunden oder kabellos)
<!-- @device:halo_box,halo,stx,krk -->
- [Optional] Eine AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300-Serie oder Z2 Extreme) mit dem neuesten installierten Treiber aus den [Installationsanweisungen für Ryzen AI Software](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), wenn Sie ein Modell auf der NPU ausführen möchten.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Grundlegende Konzepte — Wie lokale KI-Server funktionieren

Bevor wir ein Modell ausführen, lohnt es sich zu verstehen, *warum* die Dinge so eingerichtet sind. Lemonade ist ein **lokaler Modellserver**, ein Prozess, der KI-Modelle in den Arbeitsspeicher lädt und sie Anwendungen über HTTP bereitstellt, genau wie es ein Cloud-KI-Dienst tun würde.

### Warum ein Server?

| Vorteil | Was das für Sie bedeutet |
|---------|----------------------|
| **Vereinfachte Integration** | Apps kommunizieren mit einer einzigen HTTP-API, anstatt sich mit hardwarespezifischen C++- oder Python-Bibliotheken auseinanderzusetzen. |
| **Gemeinsam genutzte Modelle** | Ein einzelnes geladenes Modell kann mehrere Apps gleichzeitig bedienen, ohne dass doppelte Kopien Ihren RAM belegen. |
| **Portabilität von Cloud zu lokal** | Code, der für die Cloud-API von OpenAI geschrieben wurde, funktioniert mit Lemonade, indem Sie nur eine URL ändern. |
| **Trennung der Zuständigkeiten** | Modellverwaltung, Streaming und Fehlertoleranz werden vom Server übernommen, sodass sich Entwickler auf ihre App konzentrieren können. |

### Der OpenAI-API-Standard

Lemonade implementiert die **OpenAI-API**, dieselbe Schnittstelle, die von ChatGPT, Azure OpenAI und Dutzenden anderer Dienste verwendet wird. Das Konversationsmodell ist einfach:

| Rolle | Wer spricht |
|------|---------------|
| **system** | Anweisungen an das Modell (Persona, Einschränkungen, verfügbare Tools) |
| **user** | Nachrichten des Menschen (oder der Anwendung) an das Modell |
| **assistant** | Vom Modell generierte Antworten |

Das bedeutet, dass jede Bibliothek oder App, die OpenAI unterstützt, mit Lemonade kommunizieren kann, indem sie auf `http://localhost:13305/api/v1` verweist, während der Lemonade Server läuft.

## Hauptaktivität — Ihr erster lokaler KI-Chat

Laden wir ein LLM herunter und führen ein Gespräch damit, wobei die KI vollständig auf Ihrem eigenen Rechner läuft.

### Schritt 1: Ein Modell herunterladen und ausführen

Lemonade wird mit einer kuratierten Modellbibliothek ausgeliefert. Beginnen wir mit **Gemma-4-E2B-it**, einem leistungsfähigen und kompakten Modell mit Unterstützung für Bilderkennung (Vision). Öffnen Sie ein Terminal und führen Sie Folgendes aus:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Dieser einzelne Befehl erledigt drei Dinge:

1. **Lädt** das Modell (~3 GB) von Hugging Face herunter, sofern es noch nicht heruntergeladen wurde. (Kann einige Zeit dauern)
2. **Startet** den Lemonade-Server-Prozess auf Port 13305.
3. **Öffnet die Lemonade App**, sodass Sie sofort mit dem Modell chatten können.


<!-- @os:windows -->
Unter Windows startet die Lemonade App automatisch, und Sie können sofort mit dem Chatten beginnen. Wenn Sie das Paket `minimal.msi` installiert haben, ist die App nicht enthalten. Um zu chatten, öffnen Sie Ihren Webbrowser und rufen Sie `http://localhost:13305` auf.
<!-- @os:end -->

<!-- @os:linux -->
Öffnen Sie unter Linux Ihren Browser und navigieren Sie zu `http://localhost:13305`, um auf die Web-App zuzugreifen.
<!-- @os:end -->

Versuchen Sie, eine Frage einzugeben:

```
What are three fun facts about lemons?
```

Das Modell antwortet direkt im Chatfenster. **Herzlichen Glückwunsch! Sie führen ein großes Sprachmodell lokal aus.**

![Lemonade App mit angezeigten Logs](../../dependencies/assets/ChatwithLogs.png)

Im Bereich „Server Logs“ der Lemonade App finden Sie nach jeder Antwort Telemetriedaten zur Leistung des Modells. Zum Beispiel:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Schritt 2: Erkunden Sie die Web-Oberfläche und verschiedene Modalitäten

Lemonade enthält eine integrierte Web-Oberfläche, mit der Sie:

- **Interagieren** können mit dem geladenen Modell in einem vertrauten Chat-Fenster
- **Modelle durchsuchen** können im Model Manager-Tab
- **Neue Modelle herunterladen** können mit einem Klick

Probieren Sie den Wechsel zwischen verschiedenen Modalitäten mithilfe des Tabs **Model Manager** in der Web-Oberfläche aus, wo Sie Modelle nach Recipe oder nach Kategorie durchsuchen können:

1. **Vision:** Das bereits geladene Modell `Gemma-4-E2B-it-GGUF` unterstützt Vision. Fügen Sie ein Bild in das Chat-Feld ein und bitten Sie das Modell, es zu beschreiben.
2. **Bildgenerierung:** Laden Sie in der Kategorie Image ein Bildmodell wie `SDXL-Turbo` aus dem Model Manager herunter und verwenden Sie dann den Lemonade Image Generator, um eine Eingabeaufforderung einzugeben und lokal ein Bild zu erzeugen.
3. **Audio:** Laden Sie in der Kategorie Audio ein Audiomodell wie `Whisper-Tiny` herunter, das Sprache in Text umwandeln kann. Stellen Sie eine Audioaufnahme bereit, um sie lokal zu transkribieren. Für Text-zu-Sprache probieren Sie eines der Modelle in der Kategorie Speech, wie z. B. `kokoro-v1`.

![Multi-Modalität mit Lemonade](../../dependencies/assets/multi_modality.png)

### Schritt 3: Probieren Sie ein Modell mit einem anderen Backend aus

Wenn Sie in der Lemonade-App mit der Maus über ein Modell fahren, sehen Sie ein Zahnradsymbol. Wenn Sie darauf klicken, können Sie Optionen für das Modell auswählen, einschließlich der Auswahl des gewünschten Backends.

Standardmäßig verwendet Lemonade Vulkan für die GPU-Beschleunigung. Wenn Sie über eine unterstützte AMD-Diskrete-GPU verfügen, können Sie zu ROCm wechseln.

![Lemonade Backend auswählen](../../dependencies/assets/lemonademodeloptions.png)

Um Ihre installierten Backends zu verwalten, klicken Sie auf die Backend-Schaltfläche in der äußersten linken Spalte.

Alternativ können Sie das Backend mit dem folgenden Befehl angeben:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Sie können Ihr Standard-Backend auch über die Umgebungsvariable `LEMONADE_LLAMACPP` mit den Werten `vulkan`, `rocm` oder `cpu` festlegen.

---

## Tiefer einsteigen — Erstellen Sie eine KI-gestützte App mit Python

Die eigentliche Stärke eines lokalen KI-Servers besteht darin, dass sich jede Anwendung mit nur wenigen Zeilen Code damit verbinden kann. Um das zu beweisen, erstellen wir einen kleinen, aber funktionalen **Lernkartei-Generator**, bei dem Sie ein Thema angeben, er Lernkarten generiert und Sie sich selbst interaktiv abfragen können.

### Schritt 4: Starten Sie den Server

Überprüfen Sie, ob der Lemonade-Server läuft. In der Regel startet er nach der Installation automatisch im Hintergrund. Zur Überprüfung führen Sie Folgendes aus:

```
lemonade status
```

Sie sollten eine Meldung wie die folgende sehen: `Server is running on port 13305`.

Falls der Server nicht läuft, starten Sie ihn, indem Sie die Lemonade-App öffnen. Verwenden Sie den Standardport **13305** (Sie können ihn über das Tray-Symbol bestätigen oder auswählen).

### Schritt 5: Installieren Sie den OpenAI Python Client

Erstellen Sie in einem Terminal ein venv und installieren Sie den OpenAI Python Client mit den folgenden Befehlen:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Schritt 6: Erstellen Sie die Lernkarten-App

Laden wir ein anderes Modell herunter, um Code zu generieren: `Qwen3.5-35B-A3B-GGUF`. Dies ist ein großes (~20 GB) und leistungsstarkes Modell, das am besten für Systeme mit 32 GB+ RAM geeignet ist. Wenn Sie über weniger RAM verfügen, probieren Sie stattdessen `Qwen3.5-9B-GGUF` (~6 GB).

Sie können es über die Benutzeroberfläche herunterladen oder Folgendes ausführen:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Geben Sie die folgende Eingabeaufforderung in die Lemonade Chat-Oberfläche ein, um Code für eine einfache Flashcard-App zu generieren.

Wir verwenden Qwen3.5-35B-A3B-GGUF (ein größeres Modell, das besser im Schreiben von Code ist), um unsere Python-App zu generieren, und die App selbst ruft zur Laufzeit Gemma-4-E2B-it-GGUF (das kleinere, bereits heruntergeladene Modell) auf. Der Code kann dann in eine Datei Ihrer Wahl kopiert werden, um in Python ausgeführt zu werden.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Tipp**: Wir haben bewährte Engineering-Praktiken befolgt, indem wir gründliche Prompt-Erstellung und ein Zwei-Modell-System verwendet haben, um Ressourcen und Geschwindigkeit zu optimieren.

Der Einfachheit halber haben wir eine Beispielausgabe in [`flashcards.py`](assets/flashcards.py) bereitgestellt. Sie können sie gerne in Ihr Verzeichnis herunterladen. So oder so sollten Sie nun über eine Python-Datei verfügen, die ausgeführt werden kann.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Schritt 7: Führen Sie den generierten Code aus

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**So sollte es aussehen:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

In etwa 150 Zeilen Code haben Sie ein voll funktionsfähiges Lernwerkzeug erstellt, das von einem lokalen LLM angetrieben wird. Es gibt keinen API-Schlüssel zu verwalten, keine Nutzungskosten, und keine Daten verlassen jemals Ihren Rechner.

> **Wichtige Erkenntnis:** Beachten Sie, dass die Zeile `client = OpenAI(base_url=...) ` das *einzige* Element ist, das diese App mit Lemonade anstatt mit der Cloud von OpenAI verbindet. Der Rest des Codes ist identisch mit dem, den Sie für jeden OpenAI-kompatiblen Dienst schreiben würden. Wenn Sie schon einmal die OpenAI Python-Bibliothek verwendet haben, wissen Sie bereits, wie man Apps mit Lemonade erstellt.

### Was dies zeigt

Diese kleine App demonstriert mehrere reale Integrationsmuster:

| Muster | Wo es vorkommt |
|---------|-----------------|
| **System-Prompts** | Die `"system"`-Nachricht weist das LLM an, strukturiertes JSON auszugeben |
| **Strukturierte Ausgabe** | Die App analysiert die Antwort des LLM als JSON, um Lernkarten zu erstellen |
| **Zustandslose Anfragen** | Jeder Aufruf von `generate_flashcards()` ist unabhängig |
| **Fehlerbehandlung** | Der `try/except`-Block behandelt elegant Fälle, in denen die Ausgabe des LLM kein gültiges JSON ist |

Diese gleichen Muster lassen sich auf jede Anwendung skalieren, wie z. B. Chatbots, Code-Assistenten, Content-Generatoren, Automatisierungstools.

#### Bonus-Herausforderung

* Für eine zusätzliche Herausforderung versuchen Sie, die App so zu aktualisieren, dass die Lernkarten dem Benutzer vorgelesen werden, indem Sie sich an dem Beispiel [hier](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py) orientieren.

---

<!-- @device:halo_box,halo,stx,krk -->
## Modelle auf der NPU ausführen (optional)

Wenn Sie eine Ryzen AI 300/400/Max 300 Serie oder Z2 Extreme besitzen, verfügt Ihr Gerät über eine integrierte **Neural Processing Unit (NPU)**, einen dedizierten Chip, der speziell für KI-Workloads entwickelt wurde. Die Ausführung von Modellen auf der NPU ist energieeffizienter als die Nutzung der GPU, was sie ideal für Hintergrund-KI-Aufgaben, längere Sitzungen und den batteriebetriebenen Einsatz macht.

Lemonade unterstützt drei NPU-Ausführungsmodi, die alle transparent über dieselbe OpenAI API bereitgestellt werden:

| Modus | Funktionsweise | Rezept | Beispielmodelle |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU verarbeitet den Prompt, iGPU generiert Token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Nur NPU** | Gesamte Inferenz läuft auf der NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Verwendet die FastFlowLM-Engine auf der NPU, optimiert für AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Voraussetzungen

- **AMD Ryzen AI 300/400 Serie oder Z2 Serie** Prozessor
- Für **FLM**-Modelle: Die FLM-Runtime kann innerhalb der Lemonade App installiert werden, oder Lemonade installiert die FLM-Runtime automatisch, wenn ein FLM-Modell ausgeführt wird. Weitere Informationen zu FastFlowLM finden Sie [hier](https://fastflowlm.com/docs/).


### Schritt 8: Ein Hybrid-Modell ausführen

Hybrid-Modelle teilen die Arbeit zwischen NPU und iGPU auf, um eine gute Balance zwischen Geschwindigkeit und Effizienz zu erreichen. Wählen Sie in der Lemonade App ein Modell aus der Liste `Ryzen AI LLM`, zum Beispiel `Qwen3-4B-Hybrid`, oder führen Sie es mit folgendem Befehl aus:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade erkennt Ihre NPU automatisch und installiert das **Ryzen AI LLM**-Backend.

> **Was passiert im Hintergrund?** Wenn Sie eine Nachricht senden, verarbeitet die NPU Ihren gesamten Prompt parallel (dies wird als „Prefill“ bezeichnet). Anschließend übernimmt die iGPU und generiert die Antwort Token für Token (dies wird als „Decode“ bezeichnet). Dieser hybride Ansatz nutzt die jeweiligen Stärken beider Chips.

### Schritt 9: Ein FLM-Modell ausführen

FastFlowLM (FLM) Modelle sind speziell für die AMD XDNA2 NPU-Architektur optimiert und können für ihre Größe sehr schnell sein. Wählen Sie beispielsweise `qwen3.5-4b-FLM` aus der Liste `FastFlowLM NPU` oder verwenden Sie folgenden Befehl:

<!-- @os:windows -->
So aktivieren Sie `FastFlowLM` unter Windows:

* Öffnen Sie das Menü `Backends Manager`.
* Suchen Sie die Backend-Kategorie `FastFlowLM NPU`.
* Klicken Sie auf Install NPU.
* Nach Abschluss der Installation stehen etwa 36 Standardmodelle im FFLM-Dropdown-Menü zur Verfügung.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Wenn die `Lemonade` App zum ersten Mal gestartet wird, ist das `FastFlowNPU`-Backend standardmäßig nicht aktiviert.
Die lokale App öffnet die Installationsseite, um Sie durch die Einrichtung zu führen.

So aktivieren Sie `FastFlowLM` unter Linux:

* Öffnen Sie die `Lemonade` App.
* Besuchen Sie die [offizielle FLM](https://lemonade-server.ai/flm_npu_linux.html) Dokumentation und folgen Sie den Installationsschritten für FLM, indem Sie Ihre Linux-Distribution auswählen.
* Aktivieren Sie Backports wie auf der Installationsseite beschrieben.
* Laden Sie das neueste `v0.9.x`-Release von der [Tags-Seite](https://github.com/FastFlowLM/FastFlowLM/tags) herunter.'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Wählen Sie für die AMD Halo Developer Platform unbedingt Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Installieren Sie das heruntergeladene `.deb`-Paket.
* Empfohlen: Beenden Sie die `Lemonade App` und öffnen Sie sie erneut, damit die Änderungen erkannt werden.
* Empfohlen: Öffnen Sie den `Backends Manager` und klicken Sie auf Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Nach einer erfolgreichen Installation sollten Sie sehen, dass `flm:npu` im **Download Manager** innerhalb der **Lemonade Desktop App** abgeschlossen ist.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Sie können dann eines der verfügbaren FFLM-Modelle auswählen und mit der Nutzung des NPU-Backends beginnen.

Für ein bestimmtes Modell laden Sie das gewünschte Modell von der [Modellseite](https://fastflowlm.com/docs/models/qwen/) herunter und validieren es mit dem in der Dokumentation angegebenen Shell-Befehl.
```
flm run qwen3.5-4b-FLM
```
oder über 
```
lemonade run qwen3.5-4b-FLM
```

FLM-Modelle umfassen einige der beliebtesten Architekturen (Gemma 3, Qwen 3, Llama 3 und DeepSeek R1) und reichen von unter 1 GB bis über 13 GB.
Lemonade erkennt Ihre NPU automatisch und installiert das **FastFlowLM NPU**-Backend.

<!-- @os:windows -->
> **Tipp:** Für die beste NPU-Leistung aktivieren Sie den Turbo-Modus:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Modelle wechseln

Die Karteikarten-App aus Schritt 6 funktioniert auch mit NPU-Modellen, ändern Sie einfach den Modellnamen:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Nächste Schritte

Sie haben nun einen lokalen KI-Server auf Ihrer eigenen Hardware laufen – hier erfahren Sie, wie es weitergeht:

1. **Verbinden Sie Ihre bevorzugten Apps**: Lemonade funktioniert sofort mit [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) und [vielen weiteren](https://lemonade-server.ai/marketplace).

2. **Weitere Modelle durchsuchen**: Entdecken Sie die vollständige [Modellbibliothek](https://lemonade-server.ai/docs/server/server_models/), um Modelle zu finden, die für Coding, Reasoning, Vision und mehr optimiert sind. Nutzen Sie die Lemonade App oder `lemonade list`, um zu sehen, was verfügbar ist.

3. **ROCm GPU-Beschleunigung freischalten**: Wenn Sie über eine unterstützte AMD GPU verfügen, wechseln Sie zum ROCm-Backend: `lemonade config set llamacpp.backend=rocm`. Siehe [unterstützte AMD GPUs](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Die vollständige API-Spezifikation lesen**: Lemonade unterstützt Chat Completions, Embeddings, Audiotranskription, Bildgenerierung, Text-to-Speech und mehr. Siehe die [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) für jeden Endpunkt.

5. **Mitwirken**: Lemonade ist Open Source. Schauen Sie sich den [Contribution Guide](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) an und suchen Sie nach [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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