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

Der AMD ROCm™-Software- und PyTorch-Stack bilden ein einheitliches Ökosystem für KI auf dem Gerät. Er funktioniert sowohl unter Windows als auch unter Linux mit offizieller Unterstützung für eine Vielzahl von Geräten, einschließlich Ryzen™ AI APUs und Radeon™ GPUs.

Dieses Playbook zeigt Ihnen, wie Sie eine latenzarme, ausdrucksstarke und private Sprache-zu-Sprache-Übersetzung vollständig lokal auf dem Gerät ausführen.

## Was Sie lernen werden

- Wie Sie eine Sprache-zu-Sprache-Umgebung einrichten
- Wie Sie Python-Code schreiben, um Sprache-zu-Sprache-Modelle zu laden und zu verwenden
- Wie Sie die Gradio-UI ausführen und damit experimentieren

## Warum Echtzeit-Sprache-zu-Sprache-Übersetzung verwenden?

- Beseitigt Reibungspunkte zwischen Übersetzungs- und Sprachbarrieren
- Vermittelt Tonfall, Emotion und Absicht ohne unangenehme Pausen
- Ermöglicht globale Zusammenarbeit und schnellere Entscheidungsfindung

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen
> **Hinweis**: Wenn VS Code nicht installiert ist, können Sie es über das Ryzen AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen

### Eine virtuelle Umgebung erstellen

<!-- @os:linux -->
<!-- @device:halo_box -->
Öffnen Sie unter Linux ein Terminal und führen Sie den folgenden Befehl aus, um eine venv mit bereits installiertem ROCm+PyTorch zu erstellen:

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

Öffnen Sie unter Linux ein Terminal und führen Sie den folgenden Befehl aus, um eine venv zu erstellen:

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
Öffnen Sie unter Windows ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv mit bereits installiertem ROCm+PyTorch zu erstellen:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie ändern (z. B.
> auf RemoteSigned oder Unrestricted setzen), bevor sie einige PowerShell-Befehle ausführen können.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Öffnen Sie unter Windows ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie ändern (z. B.
> auf RemoteSigned oder Unrestricted setzen), bevor sie einige PowerShell-Befehle ausführen können.

<!-- @device:end -->
<!-- @os:end -->

### Installation der grundlegenden Abhängigkeiten

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Zusätzliche Abhängigkeiten

Installieren Sie die m4t-Abhängigkeiten mit pip:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=300 setup=activate-venv hidden=True -->
```python
import importlib
import os
import sys

# Ensure local assets directory is importable
sys.path.insert(0, os.getcwd())

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
import lang_list
from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: imported local module lang_list")
print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->


## Einrichten der Sprache-zu-Sprache-Demo

#### Mehr über seamless-m4t-v2 erfahren

Weitere Informationen finden Sie in der [Modellkarte](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) auf Hugging Face.
Dies ist die technische Architektur der Sprache-zu-Sprache-Modelle:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Skripte herunterladen

Dieses Playbook enthält einsatzbereite Skripte. Bitte laden Sie alle in dasselbe Verzeichnis wie die von Ihnen erstellte Umgebung herunter.

| Skript | Beschreibung | Verwendung |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Grundlegende LLM-Textgenerierung | `python infer.py` |
| [input1.wav](assets/input1.wav) | Beispiel-Audiodatei | N/A |
| [lang_list.py](assets/lang_list.py) | Sprachunterstützungsdatei | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Intuitive UI für Sprachübersetzung | `python gradio_demo.py --no-share` |


### Erste Schritte mit infer.py

Um das Skript auszuführen, führen Sie 
```bash
python infer.py
```
> **Hinweis**: Es können einige Warnungen angezeigt werden. Dies ist zu erwarten.
 
  
#### Erläuterung des Codes
**Snippet 1: Import der erforderlichen Abhängigkeiten**

```python 
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio

from transformers import AutoProcessor, SeamlessM4Tv2Model

# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"

INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"

# Automatically downloads + caches via Hugging Face
MODEL_ID = "facebook/seamless-m4t-v2-large"

TARGET_SAMPLE_RATE = 16_000
```

**Snippet 2: Laden der Modelle von HuggingFace**

Diese Funktion nimmt eine Modell-ID entgegen und lädt das Modell herunter, falls es noch nicht heruntergeladen wurde. Anschließend gibt sie den Processor und das Modell für die nächste Funktion zurück.
```python
def load_model(model_id: str, device: torch.device):
    start = time.time()

    print("Loading model (downloads automatically on first run)...")

    processor = AutoProcessor.from_pretrained(model_id)

    dtype = torch.float16 if device.type == "cuda" else torch.float32

    model = SeamlessM4Tv2Model.from_pretrained(model_id, torch_dtype=dtype).to(device)

    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")

    return processor, model
```

**Snippet 3: Audiodatei (.wav) einlesen und vorverarbeiten**

Diese Funktion lädt den Audioclip und resampled ihn auf die Zielrate.
```python
def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:

    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)

    # Convert to tensor [channels, samples]
    audio = torch.from_numpy(audio_np.T)

    # Resample if needed
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    # Convert stereo -> mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio
```

**Snippet 4: Inferenz ausführen**

Diese Funktion führt die Inferenz mit dem Modell aus und gibt die generierte Ausgabe zurück.
```python
def run_inference(model, processor, audio: torch.Tensor, device: torch.device, target_lang: str = DEFAULT_TARGET_LANGUAGE):

    start = time.time()

    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    audio_inputs = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in audio_inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]

    audio_array = output.float().cpu().numpy().squeeze()

    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed
```

**Snippet 5: Die übersetzte Datei speichern**

Diese Funktion speichert das Audio-Array als .WAV-Datei. 
```python
def save_audio(audio_array: np.ndarray, output_path: str, sample_rate: int):
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0

        if max_abs > 1.0:
            audio_array = audio_array / max_abs

        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)

    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

    print(f"Output saved to: {output_path}")
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

if (-not (Test-Path .\input1.wav)) { throw "FAIL: input1.wav not found in current directory" }

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }

if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }
$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

if [ ! -f ./input1.wav ]; then
  echo "FAIL: input1.wav not found in current directory"
  exit 1
fi

python ./infer.py

if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi
if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### Ausführen der Gradio-UI-Demo:

Nachdem Sie nun ein grundlegendes Beispielskript ausgeführt haben, bieten die folgenden Anweisungen eine hilfreiche UI, die auf dem geschriebenen Code aufbaut und Live-Sprache-zu-Sprache-Übersetzung einfach macht.

#### Gradio lokal ausführen

```bash
python ./gradio_demo.py --no-share
```
Öffnen Sie anschließend Ihren Webbrowser unter `http://127.0.0.1:7860`, um auf die UI zuzugreifen.


### Beispiel für die Gradio-UI:

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>

<!-- @os:windows -->
<!-- @test:id=gradio-ui-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
'@

$tempPy = Join-Path $env:TEMP "gradio_ui_smoke_ci.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy

if ($LASTEXITCODE -ne 0) {
  Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
  throw "gradio UI smoke test failed"
}

Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=gradio-ui-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail

python - <<'PY'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
PY
```
<!-- @test:end --> 
<!-- @os:end -->


## Nächste Schritte

- Kombinieren Sie Dutzende von Sprachen für schnelle Übersetzungen. 
- Teilen Sie Ihre Demo mit anderen: Fügen Sie --share hinzu, um einen öffentlichen Link zu erstellen, auf den jeder remote zugreifen kann, oder stellen Sie sie dauerhaft über Hugging Face Spaces bereit

## Ressourcen

Nachfolgend finden Sie einige zusätzliche Ressourcen, um mehr über Sprache-zu-Sprache-Übersetzung zu erfahren:  
* Das Repository finden Sie hier https://huggingface.co/facebook/seamless-m4t-v2-large 
* Wissenschaftliche Forschung zu „Seamless: Multilingual Expressive and Streaming Speech Translation“
* Gradio-Sharing und -Deployment: [Leitfaden zum Teilen Ihrer App](https://www.gradio.app/guides/sharing-your-app) und [Deployment auf Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)