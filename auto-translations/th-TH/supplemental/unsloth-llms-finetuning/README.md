<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

## <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

คู่มือการใช้งานนี้แสดงวิธีการปรับแต่ง (fine-tune) โมเดลภาษาในเครื่องด้วย Unsloth บนฮาร์ดแวร์ของ AMD

โดยใช้ตัวอย่าง Supervised Fine-Tuning (SFT) แบบสั้น ๆ พร้อมกับ LoRA adapters บน `unsloth/gemma-4-E4B-it` โดยใช้ชุดข้อมูลส่วนหนึ่งจาก `mlabonne/FineTome-100k` เป้าหมายคือการมอบเวิร์กโฟลว์แบบครบวงจรที่เรียบง่ายซึ่งครอบคลุมการตั้งค่า การฝึกฝน การอนุมาน และการบันทึกผลลัพธ์ที่ปรับแต่งแล้ว

ตัวอย่างนี้ได้รับการออกแบบมาให้ใช้งานได้จริงและปรับเปลี่ยนได้ง่าย ดังนั้นคุณสามารถใช้มันเป็นจุดเริ่มต้นสำหรับชุดข้อมูลและโมเดลของคุณเองได้

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่าสภาพแวดล้อม Unsloth
- วิธีปรับแต่ง LLM โดยใช้ SFT ร่วมกับ Unsloth
- วิธีบันทึกผลลัพธ์ที่ปรับแต่งแล้วในพื้นที่จัดเก็บข้อมูลภายในเครื่อง

<!-- @device:halo,stx,krk -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือการใช้งานนี้ต้องการ **แรม (RAM) ของระบบอย่างน้อย 64 GB** โดยต้องมีอย่างน้อย **24 GB ที่สามารถใช้งานได้กับ GPU** (24 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่เพิ่มเติมจากนั้น)
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือการใช้งานนี้ต้องการ **หน่วยความจำ GPU ทั้งหมดอย่างน้อย 24 GB** และ **แรมของระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU ทั้งหมดจะรวม VRAM เฉพาะของการ์ดจอกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ที่ยืมมาจากแรมของระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 24 GB ก็ยังสามารถใช้งานคู่มือการใช้งานนี้ได้โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนต่าง
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในคู่มือการใช้งานนี้ต้องการการ์ดจอที่มี **หน่วยความจำ GPU เฉพาะอย่างน้อย 24 GB** และ **แรมของระบบ 32 GB**
> - บน Linux การฝึกฝนจะทำงานทั้งหมดใน VRAM เฉพาะของการ์ดจอ
> - จะไม่ตกกลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (แรมของระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 24 GB จะหน่วยความจำหมดระหว่างการฝึกฝนบน Linux แม้ว่าระบบจะมีแรมเหลือเฟือก็ตาม
<!-- @os:end -->
<!-- @device:end -->

## ทำไมต้อง Unsloth?

Unsloth ทำให้การปรับแต่ง LLM สามารถทำงานบนฮาร์ดแวร์ในเครื่องได้ง่ายขึ้นโดยการลดการใช้หน่วยความจำและเพิ่มความเร็วในการฝึกฝนเมื่อเทียบกับการตั้งค่ามาตรฐาน

ในคู่มือการใช้งานนี้ เราใช้ Unsloth ร่วมกับ **SFT แบบใช้ LoRA** ซึ่งหมายความว่าโมเดลพื้นฐานส่วนใหญ่จะถูกตรึงไว้ (frozen) ในขณะที่ชุดน้ำหนักของ adapter ที่เล็กกว่ามากจะถูกฝึกฝน วิธีนี้เหมาะสมกับการพัฒนาในเครื่องเนื่องจากมีน้ำหนักเบากว่าการปรับแต่งแบบเต็มรูปแบบและทำซ้ำได้เร็วกว่า

Unsloth ยังรองรับแนวทางการฝึกฝนอื่น ๆ รวมถึง QLoRA และเวิร์กโฟลว์การเรียนรู้แบบเสริมแรง (reinforcement learning) คู่มือการใช้งานนี้มุ่งเน้นไปที่เส้นทางที่ง่ายที่สุดก่อน นั่นคือตัวอย่างการปรับแต่ง LoRA ขนาดเล็กที่ผู้ใช้สามารถรัน ทำความเข้าใจ และขยายต่อได้

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
เปิดเทอร์มินัลและสร้าง venv ที่มีซอฟต์แวร์ AMD ROCm™ และ PyTorch ติดตั้งไว้เรียบร้อยแล้ว:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบแล้วเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

เปิดเทอร์มินัลและสร้าง venv:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** Python 3.13 จำเป็นสำหรับ Windows

<!-- @device:halo_box -->
เปิดเทอร์มินัล PowerShell และสร้างสภาพแวดล้อมเสมือน:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
เปิดเทอร์มินัล PowerShell และสร้างสภาพแวดล้อมเสมือน:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### การติดตั้งการพึ่งพาพื้นฐาน
<!-- @require:driver -->

> **สำคัญ:** Unsloth ยังไม่รองรับบิลด์ PyTorch 2.13 ที่มาพร้อมกับ ROCm 10 สำหรับคู่มือการใช้งานนี้ ให้ติดตั้ง **ROCm 7.14 พร้อม PyTorch 2.12** โดยใช้คำสั่งด้านล่าง อย่าใช้แพ็กเกจ ROCm 10 / PyTorch 2.13

**ติดตั้ง PyTorch พร้อมการรองรับซอฟต์แวร์ AMD ROCm™** ในสภาพแวดล้อมเสมือนที่สร้างขึ้น:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

สำหรับอุปกรณ์อื่น ๆ โปรดดู [ROCm 7.14 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) สำหรับคำแนะนำฉบับเต็ม

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### การพึ่งพาเพิ่มเติม

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **หมายเหตุ:** ระหว่างการนำเข้า (import) Unsloth อาจตรวจสอบเส้นทางการเร่งความเร็วแบบเสริมของ `bitsandbytes` บน ROCm บางเวอร์ชัน คุณอาจเห็นข้อความเช่น `bitsandbytes library load error: Configured ROCm binary not found` คู่มือการใช้งานนี้ใช้การปรับแต่ง LoRA แบบมาตรฐานด้วย `optim="adamw_torch"` ดังนั้นเราจึงไม่ได้พึ่งพาตัวปรับค่า (optimizer) ของ `bitsandbytes` หรือ QLoRA แบบ 4-bit ข้อความนี้สามารถเพิกเฉยได้อย่างปลอดภัย

<!-- @os:windows -->
> **หมายเหตุ:** บน Windows ROCm, Unsloth จะพิมพ์คำเตือนหลายรายการเมื่อเริ่มทำงาน — ดู [Known Warnings](#known-warnings) ด้านล่าง คำเตือนเหล่านี้สามารถเพิกเฉยได้อย่างปลอดภัยทั้งหมด การฝึกฝนจะทำงานได้อย่างถูกต้อง
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## ดาวน์โหลดสคริปต์การปรับแต่ง Unsloth

แทนที่จะดำเนินการแต่ละขั้นตอนด้วยตนเอง คู่มือการใช้งานนี้มีสคริปต์แบบครบวงจรที่สะอาดเรียบร้อยไว้ที่นี่: [test_unsloth.py](assets/test_unsloth.py)

รันโค้ดต่อไปนี้เพื่อดำเนินการสคริปต์:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

ส่วนที่เหลือของคู่มือการใช้งานนี้จะอธิบายแนวคิดของแต่ละขั้นตอนหลักของสคริปต์

## วิธีการทำงาน

สคริปต์ test_unsloth.py ดำเนินการตามขั้นตอนต่อไปนี้:
* **โหลดโมเดล**: โหลด unsloth/gemma-4-E4B-it โดยใช้ FastModel
* **เตรียมข้อมูล**: ปรับมาตรฐานชุดข้อมูล (เช่น FineTome-100k) และนำเทมเพลตการสนทนา Gemma-4 มาใช้
* **นำ LoRA ไปใช้**: เพิ่ม adapters เข้าไปในโมดูลภาษา, attention และ MLP เพื่อการฝึกฝนที่มีประสิทธิภาพ
* **ฝึกฝน**: ใช้ SFTTrainer พร้อมการปิดบังการสูญเสีย (loss masking) แบบเฉพาะคำตอบ
* **การอนุมาน**: รันการทดสอบการสร้างข้อความอย่างรวดเร็วเพื่อตรวจสอบประสิทธิภาพ
* **บันทึก**: ส่งออก LoRA adapters ไปยังพื้นที่จัดเก็บข้อมูลภายในเครื่อง
## การกำหนดค่าหลัก

คุณสามารถแก้ไขค่าคงที่ต่อไปนี้เพื่อปรับแต่งการรันของคุณ:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

ตัวอย่างข้อความต้อนรับของ Unsloth และผลลัพธ์เมื่อโหลดน้ำหนักของโมเดล:

![alt text](assets/welcome.png)

## เตรียมชุดข้อมูล

เราใช้ชุดย่อยของ:
```text
mlabonne/FineTome-100k
```
ชุดข้อมูลนี้ถูก
* แปลงให้อยู่ในรูปแบบแชท
* ประมวลผลโดยใช้เทมเพลตแชทของ Gemma-4
* ทำความสะอาดเพื่อลบโทเคน BOS ที่ซ้ำกัน

## ฝึกโมเดล

สคริปต์นี้รันการสาธิตการฝึกแบบสั้น ๆ ด้วยพารามิเตอร์ดังต่อไปนี้:
- ประมาณ 50 ขั้นตอน
- ขนาดแบตช์เล็ก
- การสะสมเกรเดียนต์ (Gradient accumulation)

ระหว่างการฝึก คุณจะเห็นบันทึกดังนี้:

![alt text](assets/training.png)


## การบันทึกและการปรับใช้งาน

### การบันทึกในเครื่อง (LoRA)

สคริปต์จะบันทึก LoRA adapters ไปยัง OUTPUT_DIR โดยอัตโนมัติ
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### บันทึกโมเดลที่ผสานรวมแล้ว (สำหรับ vLLM)

<!-- @os:windows -->
> **หมายเหตุ:** vLLM ไม่รองรับ Windows หากต้องการปรับใช้โมเดลที่ปรับแต่งแล้วของคุณบน Windows ให้ใช้ llama.cpp (ดู [ส่งออก GGUF](#export-gguf-for-llamacpp) ด้านล่าง) หรือถ่ายโอนโมเดลที่ผสานรวมแล้วไปยังเครื่อง Linux ที่รัน vLLM
<!-- @os:end -->

<!-- @os:linux -->
สำหรับการปรับใช้งานด้วย vLLM ให้ผสานรวม adapters เข้ากับโมเดลแบบเต็ม:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### ส่งออก GGUF (สำหรับ llama.cpp)

แปลงเป็น GGUF โดยตรงสำหรับการอนุมานในเครื่อง:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## คำเตือนที่ทราบอยู่แล้ว

คำเตือนเหล่านี้ถูกพิมพ์โดย Unsloth เมื่อเริ่มทำงานบน Windows ROCm และปลอดภัยที่จะละเลยทั้งหมด:

| คำเตือน | เหตุผล | ปลอดภัยที่จะละเลยหรือไม่ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes ไม่มีการสร้างสำหรับ Windows ROCm | ใช่ — playbook นี้ใช้ `adamw_torch` ไม่ใช่ bnb |
| `No ROCm platform found for torch.distributed` | ROCm บน Windows ไม่รองรับการฝึกแบบกระจาย | ใช่ — การฝึกด้วย GPU เดียวไม่ได้รับผลกระทบ |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth แจ้งเตือนการสร้างที่ไม่ใช่ Linux | ใช่ — Windows ROCm ใช้งานได้สำหรับ SFT แบบ GPU เดียว |
| `triton is not available` | Triton ไม่มีการสร้างสำหรับ Windows | ใช่ — Unsloth จะใช้เคอร์เนล PyTorch แทน |

การฝึกจะดำเนินต่อไปได้อย่างถูกต้องแม้จะมีคำเตือนเหล่านี้
<!-- @os:end -->

## ขั้นตอนถัดไป
- ลองใช้ [Unsloth Studio](https://unsloth.ai/docs/new/studio) ซึ่งเป็น GUI ที่ใช้งานง่ายสำหรับ Unsloth
- ฝึกด้วยชุดข้อมูลเฉพาะของคุณเอง
- ลองปรับแต่งโมเดลด้วยไฮเปอร์พารามิเตอร์ที่แตกต่างกัน
- ปรับใช้งานด้วย vLLM หรือ llama.cpp
- ลองใช้ QLoRA สำหรับการตั้งค่าที่ใช้หน่วยความจำน้อยลง

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมบางส่วนเพื่อเรียนรู้เพิ่มเติมเกี่ยวกับ Unsloth และการปรับแต่งโมเดล:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [คู่มือการปรับแต่งโมเดลของ Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)