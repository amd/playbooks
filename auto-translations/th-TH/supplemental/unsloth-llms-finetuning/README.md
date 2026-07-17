<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

Playbook นี้แสดงวิธีการ fine-tune โมเดลภาษาในเครื่องด้วย Unsloth บนฮาร์ดแวร์ AMD

ใช้ตัวอย่าง Supervised Fine-Tuning (SFT) แบบสั้นพร้อม LoRA adapters บน `unsloth/gemma-4-E4B-it` โดยใช้ชุดข้อมูลย่อยของ `mlabonne/FineTome-100k` เป้าหมายคือให้คุณมีเวิร์กโฟลว์แบบ end-to-end ที่เรียบง่าย ครอบคลุมการตั้งค่า การฝึก การอนุมาน และการบันทึกผลลัพธ์ที่ผ่านการ fine-tune แล้ว

ตัวอย่างนี้ออกแบบมาให้ใช้งานได้จริงและปรับแต่งได้ง่าย คุณจึงสามารถใช้เป็นจุดเริ่มต้นสำหรับชุดข้อมูลและโมเดลของคุณเองได้

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่าสภาพแวดล้อม Unsloth
- วิธี fine-tune LLM โดยใช้ SFT กับ Unsloth
- วิธีบันทึกผลลัพธ์ที่ผ่านการ fine-tune แล้วลงในที่จัดเก็บในเครื่อง

<!-- @device:halo,stx,krk -->
> **หมายเหตุ:** เทคนิคการ fine-tune ใน playbook นี้ต้องการหน่วยความจำ GPU อย่างน้อย 24 GB และ RAM ของระบบ 32 GB
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิคการ fine-tune ใน playbook นี้ต้องการหน่วยความจำ GPU อย่างน้อย 24 GB และ RAM ของระบบ 32 GB
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิคการ fine-tune ใน playbook นี้ต้องการหน่วยความจำ GPU **แบบ dedicated** อย่างน้อย 24 GB และ RAM ของระบบ 32 GB
<!-- @os:end -->
<!-- @device:end -->

## ทำไมต้องใช้ Unsloth?

Unsloth ทำให้การ fine-tune LLM บนฮาร์ดแวร์ในเครื่องทำได้ง่ายขึ้น โดยลดการใช้หน่วยความจำและเพิ่มความเร็วในการฝึกเมื่อเทียบกับการตั้งค่าแบบมาตรฐาน

ใน playbook นี้ เราใช้ Unsloth ร่วมกับ **SFT แบบ LoRA** ซึ่งหมายความว่าโมเดลฐานจะถูกแช่แข็งเป็นส่วนใหญ่ ในขณะที่ชุดน้ำหนัก adapter ที่มีขนาดเล็กกว่ามากจะถูกฝึก วิธีนี้เหมาะสำหรับการพัฒนาในเครื่องเพราะเบากว่าการ fine-tune แบบเต็มรูปแบบและทำซ้ำได้เร็วกว่า

Unsloth ยังรองรับแนวทางการฝึกอื่น ๆ รวมถึง QLoRA และเวิร์กโฟลว์ reinforcement learning playbook นี้มุ่งเน้นที่เส้นทางที่ง่ายที่สุดก่อน: ตัวอย่างการ fine-tune LoRA ขนาดเล็กที่ผู้ใช้สามารถรัน ทำความเข้าใจ และขยายต่อได้

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
เปิด terminal และสร้าง venv พร้อม AMD ROCm™ software และ PyTorch ที่ติดตั้งไว้แล้ว:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

เปิด terminal และสร้าง venv:
<!-- @test:id=create-venv timeout=120 -->
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
> **หมายเหตุ:** ต้องใช้ Python 3.13 สำหรับ Windows

<!-- @device:halo_box -->
เปิด PowerShell terminal และสร้าง virtual environment:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
เปิด PowerShell terminal และสร้าง virtual environment:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### การติดตั้ง Dependencies พื้นฐาน
<!-- @require:pytorch,driver -->

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

### Dependencies เพิ่มเติม

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **หมายเหตุ:** ระหว่างการ import Unsloth อาจตรวจสอบเส้นทางการเร่งความเร็ว `bitsandbytes` แบบ optional บน ROCm บางเวอร์ชัน คุณอาจเห็นข้อความเช่น `bitsandbytes library load error: Configured ROCm binary not found` playbook นี้ใช้การ fine-tune LoRA แบบมาตรฐานด้วย `optim="adamw_torch"` ดังนั้นเราจึงไม่พึ่งพา optimizer `bitsandbytes` หรือ 4-bit QLoRA ข้อความนี้สามารถละเว้นได้อย่างปลอดภัย

<!-- @os:windows -->
> **หมายเหตุ:** บน Windows ROCm Unsloth จะแสดงคำเตือนหลายรายการเมื่อเริ่มต้น — ดู [คำเตือนที่ทราบ](#known-warnings) ด้านล่าง คำเตือนเหล่านี้ทั้งหมดสามารถละเว้นได้อย่างปลอดภัย การฝึกทำงานได้อย่างถูกต้อง
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

## ดาวน์โหลดสคริปต์ Fine-Tuning ของ Unsloth

แทนที่จะดำเนินการแต่ละขั้นตอนด้วยตนเอง playbook นี้มีสคริปต์แบบ end-to-end ที่สะอาดตรงนี้: [test_unsloth.py](assets/test_unsloth.py)

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

ส่วนที่เหลือของ playbook จะอธิบายแนวคิดของแต่ละขั้นตอนหลักของสคริปต์

## วิธีการทำงาน

สคริปต์ test_unsloth.py ดำเนินการตามขั้นตอนต่อไปนี้:
* **โหลดโมเดล**: โหลด unsloth/gemma-4-E4B-it โดยใช้ FastModel
* **เตรียมข้อมูล**: ทำให้ชุดข้อมูล (เช่น FineTome-100k) เป็นมาตรฐานและใช้ Gemma-4 chat template
* **ใช้ LoRA**: เพิ่ม adapters ให้กับโมดูล language, attention และ MLP เพื่อการฝึกที่มีประสิทธิภาพ
* **ฝึก**: ใช้ SFTTrainer พร้อม response-only loss masking
* **อนุมาน**: รันการทดสอบการสร้างข้อความอย่างรวดเร็วเพื่อตรวจสอบประสิทธิภาพ
* **บันทึก**: ส่งออก LoRA adapters ไปยังเครื่อง

## การกำหนดค่าหลัก

คุณสามารถแก้ไขค่าคงที่ต่อไปนี้เพื่อปรับแต่งการรันของคุณ:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

ตัวอย่างข้อความต้อนรับของ Unsloth และผลลัพธ์เมื่อโหลดน้ำหนักโมเดล:

![alt text](assets/welcome.png)

## เตรียมชุดข้อมูล

เราใช้ชุดข้อมูลย่อยของ:
```text
mlabonne/FineTome-100k
```
ชุดข้อมูลนี้:
* แปลงเป็นรูปแบบ chat
* ประมวลผลโดยใช้ Gemma-4 chat template
* ทำความสะอาดเพื่อลบ BOS tokens ที่ซ้ำกัน

## ฝึกโมเดล

สคริปต์รันการสาธิตการฝึกแบบสั้น โดยมีพารามิเตอร์ดังต่อไปนี้:
- ประมาณ 50 steps
- Batch size ขนาดเล็ก
- Gradient accumulation

ระหว่างการฝึก คุณจะเห็น log เช่น:

![alt text](assets/training.png)


## การบันทึกและการ Deploy

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

### บันทึกโมเดลที่รวมแล้ว (สำหรับ vLLM)

<!-- @os:windows -->
> **หมายเหตุ:** vLLM ไม่รองรับ Windows หากต้องการ deploy โมเดลที่ผ่านการ fine-tune บน Windows ให้ใช้ llama.cpp (ดู [ส่งออก GGUF](#export-gguf-for-llamacpp) ด้านล่าง) หรือโอนโมเดลที่รวมแล้วไปยังเครื่อง Linux ที่รัน vLLM
<!-- @os:end -->

<!-- @os:linux -->
สำหรับการ deploy กับ vLLM ให้รวม adapters เข้ากับโมเดลเต็มรูปแบบ:
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
## คำเตือนที่ทราบ

คำเตือนเหล่านี้ถูกแสดงโดย Unsloth เมื่อเริ่มต้นบน Windows ROCm และทั้งหมดสามารถละเว้นได้อย่างปลอดภัย:

| คำเตือน | สาเหตุ | ละเว้นได้อย่างปลอดภัย? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes ไม่มี build สำหรับ Windows ROCm | ใช่ — playbook นี้ใช้ `adamw_torch` ไม่ใช่ bnb |
| `No ROCm platform found for torch.distributed` | ROCm บน Windows ขาดการฝึกแบบ distributed | ใช่ — การฝึกแบบ single-GPU ไม่ได้รับผลกระทบ |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth ตั้งค่าสถานะ build ที่ไม่ใช่ Linux | ใช่ — Windows ROCm ทำงานได้สำหรับ single-GPU SFT |
| `triton is not available` | Triton ไม่มี build สำหรับ Windows | ใช่ — Unsloth ใช้ PyTorch kernels แทน |

การฝึกจะดำเนินการได้อย่างถูกต้องแม้จะมีคำเตือนเหล่านี้
<!-- @os:end -->

## ขั้นตอนถัดไป
- ลอง [Unsloth Studio](https://unsloth.ai/docs/new/studio) ซึ่งเป็น GUI ที่ใช้งานง่ายสำหรับ Unsloth
- ฝึกบนชุดข้อมูลเฉพาะของคุณเอง
- ลอง fine-tune ด้วย hyperparameters ที่แตกต่างกัน
- Deploy ด้วย vLLM หรือ llama.cpp
- ลอง QLoRA สำหรับการตั้งค่าที่ใช้หน่วยความจำน้อยลง

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เพิ่มเติมเกี่ยวกับ Unsloth และการ fine-tune:

* [เอกสาร Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [คู่มือการ Fine-tuning ของ Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)