<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Software AMD ROCm™ a PyTorch stack vytvářejí jednotný ekosystém pro AI přímo na zařízení. Funguje jak ve Windows, tak v Linuxu s oficiální podporou širokého spektra zařízení, včetně Ryzen™ AI APU a Radeon™ GPU.

Tento průvodce vás naučí, jak spouštět nízkolatenční, expresivní a soukromý překlad řeč-do-řeči zcela na okraji sítě (on-device).

## Co se naučíte

- Jak nastavit prostředí pro překlad řeč-do-řeči
- Jak napsat Python kód pro načtení a použití modelů řeč-do-řeči
- Jak spustit a experimentovat s uživatelským rozhraním Gradio

## Proč používat překlad řeč-do-řeči v reálném čase?

- Odstraňuje tření mezi překladem a jazykovými bariérami
- Přenáší tón, emoce a záměr bez trapných pauz
- Umožňuje globální spolupráci a rychlejší rozhodování

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalován, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
V Linuxu otevřete terminál a spusťte následující příkaz pro vytvoření venv s již nainstalovaným ROCm+Pytorch:

<!-- @test:id=create-venv timeout=300 -->
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
**Udělte svému uživateli přístup k zařízením GPU** (odhlaste se a znovu přihlaste, aby se změna projevila):

```bash
sudo usermod -aG render,video $LOGNAME
```

V Linuxu otevřete terminál a spusťte následující příkaz pro vytvoření venv:

<!-- @test:id=create-venv timeout=300 -->
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
Ve Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv s již nainstalovaným ROCm+Pytorch:

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tip**: Uživatelé Windows mohou potřebovat upravit svou zásadu spouštění PowerShellu (Execution Policy) (např.
> nastavit ji na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Ve Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv:

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Tip**: Uživatelé Windows mohou potřebovat upravit svou zásadu spouštění PowerShellu (Execution Policy) (např.
> nastavit ji na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @device:end -->
<!-- @os:end -->

### Instalace základních závislostí

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Další závislosti

Nainstalujte závislosti m4t pomocí pip:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
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


## Nastavení dema pro překlad řeč-do-řeči

#### Seznamte se s modelem seamless-m4t-v2

Podívejte se na [model card](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) na Hugging Face pro více informací.
Toto je technická architektura modelů řeč-řeč:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Stažení skriptů

Tento průvodce obsahuje připravené skripty. Stáhněte je prosím všechny do stejného adresáře jako prostředí, které jste vytvořili.

| Skript | Popis | Použití |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Základní generování textu LLM | `python infer.py` |
| [input1.wav](assets/input1.wav) | Ukázkový zvukový soubor | N/A |
| [lang_list.py](assets/lang_list.py) | Soubor podpory jazyků | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Intuitivní UI pro překlad řeči | `python gradio_demo.py --no-share` |


### Začínáme se souborem infer.py

Skript spustíte příkazem 
```bash
python infer.py
```
> **Poznámka**: Můžete vidět některá varování. To je očekávané.
 
  
#### Vysvětlení kódu
**Úryvek 1: Import potřebných závislostí**

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

**Úryvek 2: Načtení modelů z HuggingFace**

Tato funkce přijímá ID modelu a stáhne model, pokud ještě není stažený. Poté vrátí processor a model pro použití v další funkci.
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

**Úryvek 3: Vstupní zvukový klip .wav a jeho předzpracování**

Tato funkce načte zvukový klip a přesampluje jej na cílovou vzorkovací frekvenci.
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

**Úryvek 4: Spuštění inference**

Tato funkce spouští inferenci s modelem a vrací vygenerovaný výstup.
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

**Úryvek 5: Uložení přeloženého souboru**

Tato funkce uloží zvukové pole do souboru .WAV. 
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

### Spuštění dema uživatelského rozhraní Gradio:

Nyní, když jste spustili základní příklad skriptu, následující pokyny poskytují užitečné uživatelské rozhraní, které staví na napsaném kódu a usnadňuje živý překlad řeč-do-řeči.

#### Spuštění Gradio lokálně

```bash
python ./gradio_demo.py --no-share
```
Poté otevřete webový prohlížeč na adrese `http://127.0.0.1:7860` pro přístup k uživatelskému rozhraní.


### Příklad uživatelského rozhraní Gradio:

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


## Další kroky

- Kombinujte a experimentujte s desítkami jazyků pro rychlý překlad. 
- Sdílejte své demo s ostatními: Přidejte --share pro vytvoření veřejného odkazu, ke kterému může kdokoliv přistupovat vzdáleně, nebo nasaďte trvale pomocí Hugging Face Spaces

## Zdroje

Níže naleznete několik dalších zdrojů pro hlubší pochopení překladu řeč-do-řeči:  
* Repozitář najdete zde https://huggingface.co/facebook/seamless-m4t-v2-large 
* Akademický výzkum týkající se tématu "Seamless: Multilingual Expressive and Streaming Speech Translation"
* Sdílení a nasazení Gradio: [Sharing Your App Guide](https://www.gradio.app/guides/sharing-your-app) a [Deploy to Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)