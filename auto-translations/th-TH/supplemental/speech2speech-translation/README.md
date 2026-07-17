<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

ซอฟต์แวร์ AMD ROCm™ และสแตก PyTorch สร้างระบบนิเวศแบบรวมศูนย์สำหรับ AI บนอุปกรณ์ รองรับทั้ง Windows และ Linux พร้อมการสนับสนุนอย่างเป็นทางการสำหรับอุปกรณ์หลากหลายประเภท รวมถึง Ryzen™ AI APUs และ Radeon™ GPUs

Playbook นี้จะสอนวิธีรันการแปลเสียงพูดเป็นเสียงพูดแบบ latency ต่ำ มีความเป็นธรรมชาติ และเป็นส่วนตัวอย่างสมบูรณ์บนอุปกรณ์ edge

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่าสภาพแวดล้อมสำหรับ speech-to-speech
- วิธีเขียนโค้ด Python เพื่อโหลดและใช้งานโมเดล speech-to-speech
- วิธีรันและทดลองใช้งาน Gradio UI

## ทำไมต้องใช้การแปลเสียงพูดเป็นเสียงพูดแบบเรียลไทม์?

- ขจัดอุปสรรคระหว่างการแปลและกำแพงภาษา
- ถ่ายทอดน้ำเสียง อารมณ์ และความตั้งใจโดยไม่มีการหยุดชะงักที่น่าอึดอัด
- เปิดใช้งานการทำงานร่วมกันระดับโลกและการตัดสินใจที่รวดเร็วขึ้น

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ผ่าน Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

### สร้าง Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux ให้เปิด terminal และรันคำสั่งต่อไปนี้เพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้แล้ว:

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
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้การเปลี่ยนแปลงมีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux ให้เปิด terminal และรันคำสั่งต่อไปนี้เพื่อสร้าง venv:

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
บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้แล้ว:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
บน Windows ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @device:end -->
<!-- @os:end -->

### การติดตั้ง Dependencies พื้นฐาน

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Dependencies เพิ่มเติม

ติดตั้ง m4t dependencies โดยใช้ pip:
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


## ตั้งค่าการสาธิต speech-to-speech

#### เรียนรู้เกี่ยวกับ seamless-m4t-v2

ดูข้อมูลเพิ่มเติมได้ที่ [model card](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) บน Hugging Face
นี่คือสถาปัตยกรรมทางเทคนิคของโมเดล speech-to-speech:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### ดาวน์โหลดสคริปต์

Playbook นี้มีสคริปต์ที่พร้อมใช้งาน กรุณาดาวน์โหลดทั้งหมดไปยังไดเรกทอรีเดียวกับสภาพแวดล้อมที่คุณสร้างไว้

| สคริปต์ | คำอธิบาย | การใช้งาน |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | การสร้างข้อความ LLM พื้นฐาน | `python infer.py` |
| [input1.wav](assets/input1.wav) | ไฟล์เสียงตัวอย่าง | N/A |
| [lang_list.py](assets/lang_list.py) | ไฟล์รองรับภาษา | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | UI ที่ใช้งานง่ายสำหรับการแปลเสียงพูด | `python gradio_demo.py --no-share` |


### เริ่มต้นด้วย infer.py

เพื่อรันสคริปต์ ให้รัน 
```bash
python infer.py
```
> **หมายเหตุ**: คุณอาจเห็นคำเตือนบางอย่าง ซึ่งเป็นเรื่องปกติ
 
  
#### อธิบายโค้ด
**ส่วนที่ 1: นำเข้า dependencies ที่จำเป็น**

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

**ส่วนที่ 2: โหลดโมเดลจาก HuggingFace**

ฟังก์ชันนี้รับ model ID และดาวน์โหลดโมเดลหากยังไม่ได้ดาวน์โหลด จากนั้นส่งคืน processor และโมเดลให้ฟังก์ชันถัดไปใช้งาน
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

**ส่วนที่ 3: ไฟล์คลิปเสียง .wav และประมวลผลล่วงหน้า**

ฟังก์ชันนี้โหลดคลิปเสียงและ resample ให้ได้อัตราเป้าหมาย
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

**ส่วนที่ 4: รัน inference**

ฟังก์ชันนี้รัน inference ด้วยโมเดลและส่งคืนผลลัพธ์ที่สร้างขึ้น
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

**ส่วนที่ 5: บันทึกไฟล์ที่แปลแล้ว**

ฟังก์ชันนี้บันทึก audio array ลงในไฟล์ .WAV 
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

### การรัน Gradio UI demo:

เมื่อคุณได้รันตัวอย่างสคริปต์พื้นฐานแล้ว คำแนะนำต่อไปนี้จะให้ UI ที่เป็นประโยชน์ซึ่งต่อยอดจากโค้ดที่เราเขียนไว้และทำให้การแปลเสียงพูดเป็นเสียงพูดแบบสดง่ายขึ้น

#### รัน Gradio ในเครื่อง

```bash
python ./gradio_demo.py --no-share
```
จากนั้น เปิดเว็บเบราว์เซอร์ที่ `http://127.0.0.1:7860` เพื่อเข้าถึง UI


### ตัวอย่าง Gradio UI:

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


## ขั้นตอนถัดไป

- ผสมผสานระหว่างภาษาต่างๆ หลายสิบภาษาเพื่อการแปลที่รวดเร็ว
- แชร์การสาธิตของคุณกับผู้อื่น: เพิ่ม --share เพื่อสร้างลิงก์สาธารณะที่ทุกคนสามารถเข้าถึงได้จากระยะไกล หรือปรับใช้งานถาวรโดยใช้ Hugging Face Spaces

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เพิ่มเติมเกี่ยวกับการแปลเสียงพูดเป็นเสียงพูด:
* repo อยู่ที่นี่ https://huggingface.co/facebook/seamless-m4t-v2-large
* งานวิจัยทางวิชาการที่เกี่ยวข้องกับ "Seamless: Multilingual Expressive and Streaming Speech Translation"
* การแชร์และปรับใช้งาน Gradio: [คู่มือการแชร์แอปของคุณ](https://www.gradio.app/guides/sharing-your-app) และ [ปรับใช้งานบน Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)