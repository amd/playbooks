<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Dieses Playbook verwendet spezielle Tags, die GitHub nicht darstellen kann. Bitte besuchen Sie [amd.com/playbooks](https://amd.com/playbooks), um diesen Inhalt korrekt anzuzeigen.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Dieses Playbook erfordert mindestens **32 GB** Systemspeicher.
<!-- @device:end -->

## Übersicht

Coding-Agenten sind leistungsstarke Werkzeuge, die Entwickler durch die Zusammenarbeit mit KI-Agenten befähigen, die auf Large Language Models (LLMs) basieren. Sie können in die Entwicklungsumgebung eingebettet werden, etwa in das Terminal oder VS Code, wodurch sie sich nahtlos in den Workflow eines Entwicklers integrieren lassen.

Dieses Tutorial zeigt, wie Sie Cline, VS Code und LM Studio verwenden, um einen Coding-Agenten vollständig auf Ihrem lokalen Rechner auszuführen.

## Was Sie lernen werden

* Wie man VS Code mit dem Cline-Coding-Agenten ausführt, um Software-Engineering-Aufgaben zu unterstützen.
* Wie man Cline so konfiguriert, dass es mit LM Studio für die lokale Inferenz von Coding-Agenten kommuniziert.
* Wie man lokale Coding-Agenten zur Lösung realer Software-Engineering-Aufgaben einsetzt.

## Einstellen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen
> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es mit dem Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

<!-- @require:lmstudio,vscode -->

## LM Studio starten und konfigurieren

Wir verwenden LM Studio, um das LLM bereitzustellen, das den Coding-Agenten antreibt.

- Suchen Sie in der Suchleiste nach `LM Studio` und starten Sie die Anwendung. Sie werden mit der folgenden Seite begrüßt.

![LM Studio Startbildschirm](assets/initial-lm-studio.png)

Als Nächstes müssen wir das LLM auf dem System laden. Wir verwenden das Modell `Qwen3-Coder-30B-A3B` mit einer großen Kontextlänge. (Verwenden Sie den Tab "Model", um es zu installieren, falls noch nicht geschehen).
- Klicken Sie oben im LM-Studio-Fenster auf die Suchleiste oder drücken Sie `CTRL+L`. Klicken Sie auf den Schalter `Manually choose model load parameters` und anschließend auf das Modell Qwen3-Coder-30B-A3B.
- Ändern Sie die Kontextlänge von `4096` auf `32768` und stellen Sie sicher, dass `GPU Offload` auf das Maximum gesetzt ist. Klicken Sie anschließend auf `Load Model`

![Modellauswahl](assets/model-list-zoomed.png)

Wir verwenden eine große Kontextlänge, damit der Agent umfangreiche Codebasen verarbeiten und vorgenommene Änderungen im Gedächtnis behalten kann.

![Modellkonfiguration](assets/selecting-model-zoomed.png)

Als Nächstes müssen wir den LM Studio Server aktivieren.
- Klicken Sie in LM Studio links auf den Tab "Developer" oder drücken Sie `CTRL+2`.
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

Wir installieren die Cline-Erweiterung in VS Code und verbinden sie mit dem gerade eingerichteten LM Studio Server.
- Suchen Sie in der Suchleiste nach `VS Code` und starten Sie die Anwendung.
- Klicken Sie links in VS Code auf das Symbol `Extensions` und suchen Sie nach `Cline`. Klicken Sie dann auf die Schaltfläche `Install`.

![Installation der Cline-Erweiterung](assets/installing-cline-vscode-extension.png)

- Links sollte ein Cline-Symbol erscheinen. Klicken Sie darauf, um Cline zu öffnen. Es erscheint ein Fenster mit der Frage `How will you use Cline?`. Da wir ein lokales LLM verwenden, das über LM Studio läuft, wählen Sie `Bring my own API Key` und klicken Sie auf `Continue`.

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

Als Nächstes müssen wir Cline so konfigurieren, dass es mit dem eingerichteten LM Studio Server kommuniziert.
- Setzen Sie den API Provider auf `LM Studio` und das Modell auf `Qwen3-Coder-30B-A3B-GGUF`.

>**Tipp**: Möglicherweise sind neuere Modelle verfügbar. Erwägen Sie, bei Bedarf Qwen3.6-Modelle herunterzuladen und zu diesen zu wechseln.


![Modellkonfiguration](assets/cline-model-configuration-zoomed.png)

## Erstellen Ihres ersten Projekts

Verwenden wir unseren lokalen Agenten, um eine Website zu erstellen! Öffnen Sie VS Code in einem Verzeichnis Ihrer Wahl, in dem Cline die Dateien erstellen soll.
- Gehen Sie dazu oben links in VS Code auf `File -> Open Folder` und wählen Sie einen Ordner wie `Documents`.

![VS Code leerer Ordner](assets/open-cline-test.png)

Nun sind wir bereit, den lokalen Coding-Agenten zu prompten.
- Klicken Sie links auf die Cline-Erweiterung und geben Sie einen Prompt ein, um den Agenten zu starten. Verwenden wir als Beispiel den folgenden Prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Der Agent beginnt daraufhin, Dateien entsprechend dem Prompt zu erstellen. Als Benutzer können Sie beobachten, wie der Code in VS Code generiert wird, wie unten dargestellt. Möglicherweise müssen Sie jedes Mal auf `Save` klicken, wenn Cline eine Datei erstellen möchte.

![Cline Codegenerierung](assets/cline-code-generation.png)

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

Nachdem Sie die Website generiert haben, können Sie weiterhin mit Cline arbeiten, um die Website zu verbessern. Zwei mögliche Verbesserungen sind:

- **Dokumentation**: Es reicht aus, den Agenten mit `Add a README` zu prompten, damit dieser eine `README.md`-Datei erstellt, die die Website dokumentiert.
- **Animation**: Prompten Sie das Modell mit `Add an animation that visually represents a large language model running on a laptop.`, um eine Animation für die Website zu generieren.

Wir ermutigen die Leserschaft, weitere Anwendungen mit diesem Setup zu generieren. Nachfolgend finden Sie einige spannende Beispiele, die wir ausprobiert haben:

- **Retro-Arcade-Spiele**: Probieren Sie weitere Prompts aus. Es kann für den Agenten auch spannend sein, mit dem Paket `PyGame` Retro-Spiele in Python zu erstellen, mit folgendem Prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Datenanalyse**: Ein Bereich, in dem Coding-Agenten besonders nützlich sind, ist das Scripting und die Datenanalyse. Dies ist ein Prompt, der die Fähigkeit des lokalen Modells zeigt, Datenanalyse-Software zur Visualisierung von Aktienkursen zu generieren:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ressourcen

Nachfolgend finden Sie einige weitere Ressourcen, um mehr über Coding-Agenten, Cline und das Ausführen von Workloads auf 

* Weitere Informationen zur Partnerschaft und Integration zwischen AMD und LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD-Blogbeitrag zur Ausführung von Cline auf AMD Ryzen™ AI und Radeon™ Grafikkarten: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline-Blogbeitrag zur lokalen Ausführung von Coding-Agenten auf AI-PCs: https://cline.bot/blog/local-models-amd