<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Dieses Playbook verwendet spezielle Tags, die GitHub nicht rendern kann. Bitte besuchen Sie [amd.com/playbooks](https://amd.com/playbooks), um diesen Inhalt korrekt anzuzeigen.
<!-- @github-only:end -->

## Überblick

LM Studio ist ein leistungsstarker, GUI-basierter Wrapper für [llama.cpp](https://github.com/ggml-org/llama.cpp) und bietet außerdem einen [OpenAI-kompatiblen Endpunkt](https://lmstudio.ai/docs/developer/openai-compat) für die lokale Bereitstellung von Modellen. LM Studio bietet eine einfache, aber leistungsstarke Oberfläche, um Modelle einfach herunterzuladen und bereitzustellen. LM Studio bietet für AMD-Nutzer sowohl Vulkan- als auch AMD ROCm™-Software-Backends (sogenannte Runtimes).


## Was Sie lernen werden
- Wie Sie LM Studio konfigurieren und nutzen, um Ihre lokale Hardware optimal einzusetzen
- LLMs in einer vollständig offline arbeitenden Umgebung testen und verwalten
- Modelle über eine OpenAI-kompatible API bereitstellen, um benutzerdefinierte Workflows und Anwendungen zu unterstützen


## Konfigurieren des Arbeitsspeichers

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @os:linux -->
> **Hinweis**: Sie können VS Code über das AMD Ryzen™ AI Developer Center installieren. Für LM Studio folgen Sie bitte den nachstehenden Installationsanweisungen.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Falls VS Code oder LM Studio nicht installiert sind, können Sie diese über das AMD Ryzen™ AI Developer Center installieren. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Modelle herunterladen

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Chatten mit einem LLM
Erfahren Sie, wie Sie mit einem LLM auf ChatGPT-Niveau vollständig lokal zu chatten beginnen.  

1. Öffnen Sie LMStudio. 
2. Drücken Sie `Ctrl + L`, um den Model Loader zu öffnen, wählen Sie `Manually choose model load parameters` und klicken Sie auf `${model_name}`
3. Stellen Sie sicher, dass „show advanced settings“ aktiviert ist.  
4. Ändern Sie `Context Length` nach Bedarf. Eine höhere Kontextlänge bedeutet mehr Modellspeicher, aber auch mehr genutzten Systemspeicher. Für dieses Playbook wird 4096 empfohlen.
5. Stellen Sie sicher, dass `GPU Offload` auf das Maximum eingestellt ist und `Flash Attention` aktiviert ist (Cache-Quantisierungen können deaktiviert bleiben).
6. Aktivieren Sie `Remember settings` und klicken Sie auf `Load Model`.
7. Falls Sie sich nicht im Chat-Fenster befinden, drücken Sie `Ctrl + 1` oder klicken Sie oben links im Bildschirm auf die Schaltfläche 👾.
8. Senden Sie eine Nachricht und beginnen Sie mit der Interaktion mit dem Modell!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Tipp**: Die Kontextlänge bezieht sich auf das Gedächtnis des Modells. Flash Attention verbessert die Verarbeitungsgeschwindigkeit und reduziert gleichzeitig den Speicherverbrauch. GPU Offload verlagert die Berechnung auf die Grafikkarte, um schnellere Antworten zu ermöglichen.

## LLMs über einen OpenAI-kompatiblen Endpunkt bereitstellen

LM Studio bietet außerdem einen OpenAI-kompatiblen Endpunkt in Form des LM Studio Servers. Dies wurde bereits in einem agentischen Coding-Workflow mit Cline [hier](../playbooks/vscode-qwen3-coder) demonstriert. Ein weiterer gängiger Anwendungsfall ist die Verbindung des LM Studio Servers mit einer beliebigen Webanwendung (React, Node.js, Python), indem standardmäßige HTTP-Anfragen an den Inferenz-Endpunkt gesendet werden.

Um den LM Studio Server einzurichten, folgen Sie diesen Anweisungen:

1. Klicken Sie auf der linken Seite auf die Registerkarte `Developer` (Befehlszeilensymbol) oder drücken Sie `Ctrl + 2` und klicken Sie dann auf `Server Settings`.  
2. (Optional): Wenn Sie das Modell über Ihr LAN bereitstellen möchten, aktivieren Sie `Serve on Local Network`. Wenn Sie es mit einer Website oder umfangreichen Aufrufen innerhalb von VS Code verwenden möchten, aktivieren Sie `Enable CORS`. 
3. Stellen Sie oben links sicher, dass der Server läuft, indem Sie auf den Schalter vor `Status` klicken.
4. Nun läuft ein OpenAI-kompatibler Endpunkt. Die Adresse lautet üblicherweise http://127.0.0.1:1234  
5. Falls noch kein Modell geladen ist, können Sie es laden, indem Sie auf `Load Model` klicken und die zuvor beschriebenen Schritte befolgen. 

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


Dieses Modell ist nun über den LM Studio Server-Endpunkt erreichbar und unterstützt OpenAI-Endpunkte, darunter:

| Endpunkt | Methode | Dokumentation |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Beispiel: Ping an Ihren Endpunkt senden
Nachdem Sie soeben den OpenAI-kompatiblen Endpunkt erstellt haben, sehen wir uns an, wie Sie diesen in eine Python-Entwicklungsumgebung (wie VSCode) integrieren und Ihr System als lokalen API-Anbieter nutzen können.

1. Erstellen Sie eine Python-virtuelle Umgebung:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Öffnen Sie unter Linux ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Öffnen Sie unter Linux ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    Öffnen Sie unter Windows ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie ändern (z. B.
    > auf RemoteSigned oder Unrestricted festlegen), bevor sie einige PowerShell-Befehle ausführen können.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Öffnen Sie unter Windows ein Terminal in einem Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie ändern (z. B.
    > auf RemoteSigned oder Unrestricted festlegen), bevor sie einige PowerShell-Befehle ausführen können.

<!-- @device:end -->
<!-- @os:end -->

2. Installieren Sie das OpenAI-Paket
    ```bash
    pip install openai
    ```

3. Führen Sie das folgende Skript aus, um den soeben erstellten Endpunkt anzupingen.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
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
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
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

#### (Optional): Zwischen Laufzeitumgebungen wechseln

1. Drücken Sie `Ctrl + Shift + R` auf Ihrer Tastatur. Alternativ klicken Sie auf die Registerkarte `Discover` (Lupe) auf der linken Seite und dann im Popup-Fenster auf `Runtime`.
2. Daraufhin sollten Sie `Runtime Selections` sehen, wo Sie über das Dropdown-Menü die Laufzeitumgebung ändern können.


## Nächste Schritte

- **Integration eigener Anwendungen**: Integrieren Sie Ihre eigenen Python-Skripte oder Anwendungen über die lokale OpenAI-kompatible API.
- **Erweiterte Frontends**: Verbinden Sie leistungsstarke Oberflächen wie Open WebUI mit Ihrem Server für Chatverlauf und Persona-Verwaltung.

Weitere Dokumentation finden Sie unter: https://lmstudio.ai/docs/developer