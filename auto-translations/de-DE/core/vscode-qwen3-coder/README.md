<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Übersicht

Coding-Agenten sind leistungsstarke Werkzeuge, die Entwickler durch die Zusammenarbeit mit KI-Agenten unterstützen, die auf Large Language Models (LLMs) basieren. Sie können in die Entwicklungsumgebung eingebettet werden, beispielsweise in das Terminal oder VS Code, und ermöglichen so eine nahtlose Integration in den Arbeitsablauf eines Entwicklers.

Dieses Tutorial zeigt, wie man Cline, VS Code und LM Studio verwendet, um einen Coding-Agenten vollständig auf dem lokalen Rechner auszuführen.

## Was Sie lernen werden

* Wie man VS Code mit dem Cline-Coding-Agenten ausführt, um bei Software-Engineering-Aufgaben zu unterstützen.
* Wie man Cline so konfiguriert, dass es mit LM Studio für lokale Inferenz von Coding-Agenten kommuniziert.
* Wie man lokale Coding-Agenten einsetzt, um reale Software-Engineering-Aufgaben zu lösen.

## Speicherkonfiguration festlegen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Auf Software-Updates prüfen
> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es über das Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-Voraussetzungen installieren

<!-- @require:lmstudio,vscode -->

## LM Studio starten und konfigurieren

Wir verwenden LM Studio, um das LLM bereitzustellen, das den Coding-Agenten antreibt.

- Suchen Sie in der Suchleiste nach `LM Studio` und starten Sie die Anwendung. Sie werden von der folgenden Seite begrüßt.

![LM Studio Startbildschirm](assets/initial-lm-studio.png)

Als Nächstes müssen wir das LLM auf dem System laden. Wir werden das Modell `Qwen3-Coder-30B-A3B` mit einer großen Kontextlänge verwenden. (Verwenden Sie den Modell-Tab, um es zu installieren, falls Sie dies noch nicht getan haben).
- Klicken Sie auf die Suchleiste oben im LM Studio-Fenster oder drücken Sie `CTRL+L`. Klicken Sie auf den Schalter `Manually choose model load parameters` und dann auf das Modell Qwen3-Coder-30B-A3B.
- Ändern Sie die Kontextlänge von `4096` auf `32768` und stellen Sie sicher, dass `GPU Offload` auf dem Maximum ist. Klicken Sie dann auf `Load Model`.

![Modell auswählen](assets/model-list-zoomed.png)

Wir verwenden eine große Kontextlänge, damit der Agent große Codebasen verarbeiten und vorgenommene Änderungen im Gedächtnis behalten kann.

![Modell konfigurieren](assets/selecting-model-zoomed.png)

Als Nächstes müssen wir den LM Studio-Server aktivieren.
- Klicken Sie auf den Developer-Tab oder drücken Sie `CTRL+2` in LM Studio auf der linken Seite.
- Überprüfen Sie den Status-Schalter und stellen Sie sicher, dass er auf `Running` gesetzt ist.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Serverstatus](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code starten und konfigurieren

Wir werden die Cline-Erweiterung in VS Code installieren und sie mit dem soeben erstellten LM Studio-Server verbinden.
- Suchen Sie in der Suchleiste nach `VS Code` und starten Sie die Anwendung.
- Klicken Sie auf das Symbol `Extensions` in der linken Spalte von VS Code und suchen Sie nach `Cline`. Klicken Sie dann auf die Schaltfläche `Install`.

![Cline-Erweiterung installieren](assets/installing-cline-vscode-extension.png)

- In der linken Spalte sollte ein Cline-Symbol erscheinen. Klicken Sie darauf, um Cline zu öffnen. Es erscheint ein Fenster mit der Frage `How will you use Cline?` Da wir ein lokales LLM verwenden werden, das über LM Studio läuft, wählen Sie `Bring my own API Key` und klicken Sie auf `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Kontoerstellung](assets/cline-how-will-you-use-cline-zoomed.png)

Als Nächstes müssen wir Cline so konfigurieren, dass es mit dem von uns eingerichteten LM Studio-Server kommuniziert.
- Setzen Sie den API-Anbieter auf `LM Studio` und das Modell auf `Qwen3-Coder-30B-A3B-GGUF`.

>**Tipp**: Möglicherweise sind neuere Modelle verfügbar. Erwägen Sie, Qwen3.6-Modelle herunterzuladen und zu diesen zu wechseln, falls gewünscht.


![Modellkonfiguration](assets/cline-model-configuration-zoomed.png)

## Ihr erstes Projekt erstellen

Lassen Sie uns unseren lokalen Agenten verwenden, um eine Website zu erstellen! Öffnen Sie VSCode in einem Verzeichnis Ihrer Wahl, in dem Cline die Dateien erstellen wird.
- Gehen Sie dazu oben links in VS Code auf `File -> Open Folder` und wählen Sie einen Ordner wie `Documents`.

![VS Code leerer Ordner](assets/open-cline-test.png)

Jetzt sind wir bereit, den lokalen Coding-Agenten zu verwenden.
- Klicken Sie auf die Cline-Erweiterung in der linken Spalte und geben Sie eine Eingabeaufforderung ein, um den Agenten zu starten. Als Beispiel verwenden wir die folgende Eingabeaufforderung:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Der Agent beginnt dann, Dateien gemäß der Eingabeaufforderung zu erstellen. Als Benutzer können Sie beobachten, wie der Code in VS Code generiert wird, wie unten gezeigt. Möglicherweise müssen Sie jedes Mal auf `Save` klicken, wenn Cline eine Datei erstellen möchte.

![Cline-Codegenerierung](assets/cline-code-generation.png)

Nach der Generierung der Software ist der Agent fertig und Sie können die Anwendung ausführen. In diesem Fall hat der Agent drei Dateien geschrieben: `index.html`, `script.js` und `styles.css`. Durch einfaches Doppelklicken auf die HTML-Datei können wir die generierte Website laden und mit ihr interagieren.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Nächste Schritte

Nach der Generierung der Website können Sie weiterhin mit Cline zusammenarbeiten, um die Website zu verbessern. Zwei mögliche Verbesserungen sind:

- **Dokumentation**: Die Eingabeaufforderung `Add a README` an den Agenten ist alles, was benötigt wird, damit der Agent eine `README.md`-Datei generiert, die die Website dokumentiert.
- **Animation**: Geben Sie dem Modell die Eingabeaufforderung `Add an animation that visually represents a large language model running on a laptop.`, um eine Animation zur Website hinzuzufügen.

Wir ermutigen den Leser, andere Anwendungen mit diesem Setup zu generieren. Nachfolgend sind einige unterhaltsame Beispiele aufgeführt, die wir ausprobiert haben:

- **Retro-Arcade-Spiele**: Probieren Sie andere Eingabeaufforderungen aus. Es kann auch Spaß machen, den Agenten Retro-Spiele in Python mit dem `PyGame`-Paket erstellen zu lassen, mit der folgenden Eingabeaufforderung:

```code
Create a simple pong game using the PyGame python package.
```

- **Datenanalyse**: Ein Bereich, in dem Coding-Agenten besonders nützlich sind, ist das Scripting und die Datenanalyse. Dies ist eine Eingabeaufforderung, um die Fähigkeit des lokalen Modells zur Generierung von Datenanalysesoftware für die Visualisierung von Aktienkursen zu demonstrieren:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressourcen

Nachfolgend finden Sie einige zusätzliche Ressourcen, um mehr über Coding-Agenten, Cline und die Ausführung von Workloads zu erfahren.

* Weitere Informationen zur AMD LM Studio-Partnerschaft und -Integration: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-Blog zur Ausführung von Cline auf AMD Ryzen™ AI und Radeon™ Grafikkarten: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-Blog zur lokalen Ausführung von Coding-Agenten auf KI-PCs: https://cline.bot/blog/local-models-amd