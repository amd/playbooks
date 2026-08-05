<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Az AMD ROCm™ szoftver és a PyTorch stack egységes ökoszisztémát hoz létre az eszközön futó mesterséges intelligencia számára. Windows és Linux rendszeren egyaránt működik, hivatalos támogatással számos eszközhöz, beleértve a Ryzen™ AI APU-kat és a Radeon™ GPU-kat is.

Ez az útmutató megtanítja, hogyan futtathat alacsony késleltetésű, kifejező és privát beszéd-beszéd fordítást teljes egészében az edge-en.

## Amit tanulni fog

- Hogyan állítsa be a beszéd-beszéd környezetet
- Hogyan írjon Python kódot beszéd-beszéd modellek betöltéséhez és használatához
- Hogyan futtassa és kísérletezzen a Gradio UI-vel

## Miért érdemes valós idejű beszéd-beszéd fordítást használni?

- Megszünteti a súrlódást a fordítás és a nyelvi akadályok között
- Közvetíti a hangnemet, az érzelmeket és a szándékot kínos szünetek nélkül
- Lehetővé teszi a globális együttműködést és a gyorsabb döntéshozatalt

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## A szoftveres előfeltételek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux rendszeren nyisson meg egy terminált, és futtassa az alábbi parancsot egy olyan venv létrehozásához, amelyben már telepítve van a ROCm+Pytorch:

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
**Adjon hozzáférést a felhasználójának a GPU eszközökhöz** (jelentkezzen ki és be újra, hogy ez érvénybe lépjen):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux rendszeren nyisson meg egy terminált, és futtassa az alábbi parancsot egy venv létrehozásához:

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
Windows rendszeren nyisson meg egy terminált a választott könyvtárban, és kövesse a parancsokat egy olyan venv létrehozásához, amelyben már telepítve van a ROCm+Pytorch:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tipp**: Előfordulhat, hogy Windows felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
> RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell parancs futtatása előtt.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows rendszeren nyisson meg egy terminált a választott könyvtárban, és kövesse a parancsokat egy venv létrehozásához:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tipp**: Előfordulhat, hogy Windows felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
> RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell parancs futtatása előtt.

<!-- @device:end -->
<!-- @os:end -->

### Alapvető függőségek telepítése

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### További függőségek

Telepítse az m4t függőségeket pip segítségével:
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


## A beszéd-beszéd demó beállítása

#### Ismerje meg a seamless-m4t-v2-t

Nézze meg a [modell kártyát](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) a Hugging Face-en további információkért.
Ez a beszéd-beszéd modellek technikai architektúrája:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Szkriptek letöltése

Ez az útmutató használatra kész szkripteket tartalmaz. Kérjük, töltse le mindegyiket ugyanabba a könyvtárba, ahol a létrehozott környezet található.

| Szkript | Leírás | Használat |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Alapvető LLM szöveggenerálás | `python infer.py` |
| [input1.wav](assets/input1.wav) | Példa hangfájl | N/A |
| [lang_list.py](assets/lang_list.py) | Nyelvi támogatási fájl | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Intuitív UI a beszédfordításhoz | `python gradio_demo.py --no-share` |


### Kezdés az infer.py-vel

A szkript végrehajtásához futtassa a 
```bash
python infer.py
```
> **Megjegyzés**: Előfordulhat, hogy néhány figyelmeztetést lát. Ez várható.
 
  
#### A kód magyarázata
**1. részlet: A szükséges függőségek importálása**

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

**2. részlet: A modellek betöltése a HuggingFace-ről**

Ez a funkció egy modell azonosítót vesz be, és letölti a modellt, ha még nincs letöltve. Ezután visszaadja a processzort és a modellt a következő funkció számára.
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

**3. részlet: Bemeneti hangklip .wav fájl betöltése és előfeldolgozása**

Ez a funkció betölti a hangklipet, és újramintavételezi a célsebességre.
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

**4. részlet: Következtetés futtatása**

Ez a funkció futtatja a következtetést a modellel, és visszaadja a generált kimenetet.
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

**5. részlet: A lefordított fájl mentése**

Ez a funkció elmenti a hangtömböt egy .WAV fájlba. 
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

### A Gradio UI demó futtatása:

Most, hogy futtatott egy alapvető szkript példát, a következő útmutatás egy hasznos felületet biztosít, amely az eddig megírt kódra épül, és megkönnyíti az élő beszéd-beszéd fordítást.

#### Gradio helyi futtatása

```bash
python ./gradio_demo.py --no-share
```
Ezután nyissa meg a webböngészőjét a `http://127.0.0.1:7860` címen az UI eléréséhez.


### Gradio UI példa:

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


## Következő lépések

- Válogasson tucatnyi nyelv közül a gyors fordításhoz. 
- Ossza meg demóját másokkal: Adja hozzá a --share opciót egy nyilvános link létrehozásához, amelyet bárki elérhet távolról, vagy telepítse tartósan a Hugging Face Spaces segítségével

## Erőforrások

Az alábbiakban további erőforrásokat talál a beszéd-beszéd fordításról:  
* A repó itt található https://huggingface.co/facebook/seamless-m4t-v2-large 
* Tudományos kutatás a "Seamless: Multilingual Expressive and Streaming Speech Translation" témában
* Gradio megosztás és telepítés: [Az alkalmazás megosztása útmutató](https://www.gradio.app/guides/sharing-your-app) és [Telepítés Hugging Face Spaces-re](https://shafiqulai.github.io/blogs/blog_5.html)