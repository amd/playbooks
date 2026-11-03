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

LM Studio ist ein leistungsstarker GUI-basierter Wrapper für [llama.cpp](https://github.com/ggml-org/llama.cpp) und bietet zudem einen [OpenAI-kompatiblen Endpunkt](https://lmstudio.ai/docs/developer/openai-compat) zur lokalen Modellbereitstellung. LM Studio bietet eine einfache, aber leistungsstarke Oberfläche, um Modelle problemlos herunterzuladen und bereitzustellen. LM Studio bietet für AMD-Nutzer sowohl Vulkan- als auch AMD ROCm™ Software-Backends (sogenannte Runtimes).


## Was Sie lernen werden
- Wie Sie LM Studio konfigurieren und nutzen, um Ihre lokale Hardware optimal zu verwenden
- Testen und Verwalten von LLMs in einer vollständig offline arbeitenden Umgebung
- Bereitstellung von Modellen über eine OpenAI-kompatible API, um benutzerdefinierte Workflows und Anwendungen zu unterstützen


<!-- @device:halo_box,halo,stx,krk -->
## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @os:linux -->
> **Hinweis**: Sie können VS Code über das AMD Ryzen™ AI Developer Center installieren. Für LM Studio folgen Sie den nachstehenden Installationsanweisungen.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Wenn VS Code oder LM Studio nicht installiert ist, können Sie diese über das AMD Ryzen™ AI Developer Center installieren. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Herunterladen von Modellen

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

## Mit einem LLM chatten
Erfahren Sie, wie Sie mit einem LLM auf ChatGPT-Niveau vollständig lokal chatten können.  

1. Öffnen Sie LMStudio. 
2. Drücken Sie `Ctrl + L`, um den Model Loader zu öffnen, wählen Sie `Manually choose model load parameters` und klicken Sie auf `${model_name}`
3. Stellen Sie sicher, dass „show advanced settings“ aktiviert ist.  
4. Ändern Sie `Context Length` nach Wunsch. Eine höhere Kontextlänge bedeutet mehr Modellspeicher, aber auch mehr genutzten Systemspeicher. Für dieses Playbook wird 4096 empfohlen.
5. Stellen Sie sicher, dass `GPU Offload` auf Maximum gesetzt ist und `Flash Attention` aktiviert ist (Cache Quantizations können deaktiviert bleiben)
6. Aktivieren Sie `Remember settings` und klicken Sie auf `Load Model`.
7. Wenn Sie sich nicht im Chatfenster befinden, drücken Sie `Ctrl + 1` oder klicken Sie auf die Schaltfläche 👾 oben links auf dem Bildschirm.
8. Senden Sie eine Nachricht und beginnen Sie mit der Interaktion mit dem Modell!

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

LM Studio bietet außerdem einen OpenAI-kompatiblen Endpunkt in Form des LM Studio Servers. Dies wurde bereits in einem agentischen Coding-Workflow mit Cline [hier](../playbooks/vscode-qwen3-coder) demonstriert. Ein weiterer gängiger Anwendungsfall besteht darin, den LM Studio Server mit einer beliebigen Webanwendung (React, Node.js, Python) zu verbinden, indem Standard-HTTP-Anfragen an den Inferenz-Endpunkt gesendet werden.

Um den LM Studio Server einzurichten, befolgen Sie diese Anweisungen:

1. Klicken Sie auf der linken Seite auf den Tab `Developer` (Befehlszeilensymbol) oder drücken Sie `Ctrl + 2` und klicken Sie dann auf `Server Settings`.  
2. (Optional): Wenn Sie das Modell in Ihrem LAN bereitstellen möchten, aktivieren Sie `Serve on Local Network`. Wenn Sie es mit einer Website oder umfangreichen Aufrufen innerhalb von VS Code verwenden möchten, aktivieren Sie `Enable CORS`. 
3. Stellen Sie oben links sicher, dass der Server läuft, indem Sie auf den Umschaltknopf vor `Status` klicken.
4. Ein OpenAI-kompatibler Endpunkt läuft nun. Die Adresse lautet typischerweise http://127.0.0.1:1234  
5. Falls noch kein Modell geladen ist, können Sie es laden, indem Sie auf `Load Model` klicken und die zuvor genannten Schritte befolgen. 

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


Dieses Modell ist nun über den LM Studio Server-Endpunkt zugänglich und unterstützt OpenAI-Endpunkte, darunter:

| Endpunkt | Methode | Dokumentation |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Beispiel: Ihren Endpoint anpingen
Nachdem wir gerade den OpenAI Compatible Endpoint erstellt haben, schauen wir uns an, wie man diesen in eine Python-Entwicklungsumgebung (wie VSCode) integriert und Ihr System als lokalen API-Provider verwendet.

1. Erstellen Sie eine Python-virtuelle Umgebung:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Öffnen Sie unter Linux ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
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

    Öffnen Sie unter Linux ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
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
    Öffnen Sie unter Windows ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Windows-Nutzer müssen möglicherweise ihre PowerShell Execution Policy anpassen (z. B.
    > auf RemoteSigned oder Unrestricted setzen), bevor sie bestimmte Powershell-Befehle ausführen können.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Öffnen Sie unter Windows ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Windows-Nutzer müssen möglicherweise ihre PowerShell Execution Policy anpassen (z. B.
    > auf RemoteSigned oder Unrestricted setzen), bevor sie bestimmte Powershell-Befehle ausführen können.

<!-- @device:end -->
<!-- @os:end -->

2. Installieren Sie das OpenAI-Paket
    ```bash
    pip install openai
    ```

3. Führen Sie das folgende Skript aus, um den gerade erstellten Endpoint anzupingen.
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

#### (Optional): Wechseln zwischen Runtimes

1. Drücken Sie `Ctrl + Shift + R` auf Ihrer Tastatur. Alternativ klicken Sie auf den Tab `Discover` (Lupe) auf der linken Seite und dann im Popup auf `Runtime`.
2. Sie sollten dann `Runtime Selections` sehen, wo das Dropdown-Menü verwendet werden kann, um die Runtime zu ändern.


## Nächste Schritte

- **Individuelle App-Integration**: Integrieren Sie Ihre eigenen Python-Skripte oder Anwendungen über die lokale OpenAI-kompatible API.
- **Erweiterte Frontends**: Verbinden Sie leistungsstarke Oberflächen wie Open WebUI mit Ihrem Server für Chatverlauf und Personaverwaltung.

Weitere Dokumentation finden Sie unter: https://lmstudio.ai/docs/developer