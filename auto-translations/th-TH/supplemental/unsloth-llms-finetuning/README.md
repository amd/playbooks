<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> เอกสารนี้ใช้แท็กพิเศษที่ GitHub ไม่สามารถแสดงผลได้ โปรดไปที่ [amd.com/playbooks](https://amd.com/playbooks) เพื่อดูตัวอย่างเนื้อหานี้อย่างถูกต้อง
<!-- @github-only:end -->

## ภาพรวม

เอกสารนี้แสดงวิธีการปรับแต่งโมเดลภาษาในเครื่องด้วย Unsloth บนฮาร์ดแวร์ AMD

โดยใช้ตัวอย่าง Supervised Fine-Tuning (SFT) แบบสั้นพร้อม LoRA adapters บน `unsloth/gemma-4-E4B-it` โดยใช้ชุดข้อมูลย่อยของ `mlabonne/FineTome-100k` เป้าหมายคือเพื่อให้คุณได้เวิร์กโฟลว์แบบ end-to-end ที่เรียบง่าย ครอบคลุมการตั้งค่า การฝึกโมเดล การอนุมาน และการบันทึกผลลัพธ์ที่ปรับแต่งแล้ว

ตัวอย่างนี้ถูกออกแบบมาให้ใช้งานได้จริงและปรับเปลี่ยนได้ง่าย เพื่อให้คุณสามารถใช้เป็นจุดเริ่มต้นสำหรับชุดข้อมูลและโมเดลของคุณเอง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีการตั้งค่าสภาพแวดล้อม Unsloth
- วิธีการปรับแต่ง LLM โดยใช้ SFT ร่วมกับ Unsloth
- วิธีการบันทึกผลลัพธ์ที่ปรับแต่งแล้วในที่จัดเก็บข้อมูลภายในเครื่อง

<!-- @device:halo,stx,krk -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการหน่วยความจำ GPU อย่างน้อย 24 GB และ RAM ของระบบอย่างน้อย 32 GB
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการหน่วยความจำ GPU อย่างน้อย 24 GB และ RAM ของระบบอย่างน้อย 32 GB
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการหน่วยความจำ GPU แบบ**เฉพาะ** อย่างน้อย 24 GB และ RAM ของระบบอย่างน้อย 32 GB
<!-- @os:end -->
<!-- @device:end -->

## ทำไมต้อง Unsloth?

Unsloth ช่วยให้การปรับแต่ง LLM รันบนฮาร์ดแวร์ในเครื่องได้ง่ายขึ้น โดยลดการใช้หน่วยความจำและเพิ่มความเร็วในการฝึกโมเดลเมื่อเทียบกับการตั้งค่าแบบมาตรฐาน

ในเอกสารนี้ เราใช้ Unsloth ร่วมกับ **LoRA-based SFT** ซึ่งหมายความว่าโมเดลฐานส่วนใหญ่จะถูกล็อกไว้ ในขณะที่ชุดน้ำหนักของ adapter ที่มีขนาดเล็กกว่ามากจะถูกฝึก วิธีนี้เหมาะสำหรับการพัฒนาในเครื่องเนื่องจากมีน้ำหนักเบากว่าการปรับแต่งแบบเต็มรูปแบบ และทำซ้ำได้เร็วกว่า

Unsloth ยังรองรับแนวทางการฝึกอื่น ๆ รวมถึง QLoRA และเวิร์กโฟลว์การเรียนรู้แบบเสริมกำลัง (reinforcement learning) เอกสารนี้เน้นที่เส้นทางที่ง่ายที่สุดก่อน คือตัวอย่างการปรับแต่งด้วย LoRA ขนาดเล็กที่ผู้ใช้สามารถรัน ทำความเข้าใจ และขยายผลได้

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
เปิดเทอร์มินัลและสร้าง venv ที่ติดตั้ง AMD ROCm™ software และ PyTorch ไว้แล้ว:
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
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

เปิดเทอร์มินัลและสร้าง venv:
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

### การติดตั้งดีเพนเดนซีพื้นฐาน
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

### ดีเพนเดนซีเพิ่มเติม

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

> **หมายเหตุ:** ระหว่างการ import Unsloth อาจตรวจสอบเส้นทางการเร่งความเร็วแบบเสริม `bitsandbytes` บน ROCm บางเวอร์ชัน คุณอาจเห็นข้อความเช่น `bitsandbytes library load error: Configured ROCm binary not found` เอกสารนี้ใช้การปรับแต่งแบบ LoRA มาตรฐานด้วย `optim="adamw_torch"` ดังนั้นเราจึงไม่ได้พึ่งพา optimizer ของ `bitsandbytes` หรือ 4-bit QLoRA ข้อความนี้สามารถละเลยได้อย่างปลอดภัย

<!-- @os:windows -->
> **หมายเหตุ:** บน Windows ROCm Unsloth จะแสดงคำเตือนหลายรายการเมื่อเริ่มทำงาน — ดู [คำเตือนที่ทราบอยู่แล้ว](#known-warnings) ด้านล่าง คำเตือนเหล่านี้สามารถละเลยได้อย่างปลอดภัยทั้งหมด การฝึกโมเดลยังคงทำงานได้อย่างถูกต้อง
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

แทนที่จะรันแต่ละขั้นตอนด้วยตนเอง เอกสารนี้มีสคริปต์แบบ end-to-end ที่พร้อมใช้งานให้ที่นี่: [test_unsloth.py](assets/test_unsloth.py)

รันโค้ดต่อไปนี้เพื่อรันสคริปต์:

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

ในส่วนที่เหลือของเอกสารนี้จะอธิบายในเชิงแนวคิดเกี่ยวกับแต่ละขั้นตอนหลักของสคริปต์

## วิธีการทำงาน

สคริปต์ test_unsloth.py ดำเนินการตามขั้นตอนต่อไปนี้:
* **โหลดโมเดล**: โหลด unsloth/gemma-4-E4B-it โดยใช้ FastModel
* **เตรียมข้อมูล**: จัดรูปแบบชุดข้อมูล (เช่น FineTome-100k) ให้เป็นมาตรฐาน และใช้เทมเพลตแชทของ Gemma-4
* **ใช้ LoRA**: เพิ่ม adapters เข้าไปในโมดูลภาษา, attention และ MLP เพื่อการฝึกที่มีประสิทธิภาพ
* **ฝึกโมเดล**: ใช้ SFTTrainer พร้อมการปิดบัง loss แบบ response-only
* **การอนุมาน**: รันการทดสอบสร้างข้อความอย่างรวดเร็วเพื่อตรวจสอบประสิทธิภาพ
* **บันทึก**: ส่งออก LoRA adapters ไว้ในเครื่อง

## การตั้งค่าหลัก

คุณสามารถปรับเปลี่ยนค่าคงที่ต่อไปนี้เพื่อปรับแต่งการรันของคุณ:

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
ชุดข้อมูลนี้จะถูก:
* แปลงเป็นรูปแบบแชท
* ประมวลผลโดยใช้เทมเพลตแชทของ Gemma-4
* ทำความสะอาดเพื่อลบโทเค็น BOS ที่ซ้ำกัน

## ฝึกโมเดล

สคริปต์นี้รันการสาธิตการฝึกแบบสั้น ด้วยพารามิเตอร์ต่อไปนี้:
- ประมาณ 50 ขั้นตอน
- ขนาดแบตช์เล็ก
- การสะสมเกรเดียนต์ (gradient accumulation)

ระหว่างการฝึก คุณจะเห็นบันทึก (logs) เช่น:

![alt text](assets/training.png)


## การบันทึกและการนำไปใช้งาน

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
> **หมายเหตุ:** vLLM ไม่รองรับ Windows หากต้องการนำโมเดลที่ปรับแต่งแล้วไปใช้งานบน Windows ให้ใช้ llama.cpp (ดู [ส่งออก GGUF](#export-gguf-for-llamacpp) ด้านล่าง) หรือย้ายโมเดลที่รวมแล้วไปยังเครื่อง Linux ที่รัน vLLM
<!-- @os:end -->

<!-- @os:linux -->
สำหรับการนำไปใช้งานกับ vLLM ให้รวม adapters เข้ากับโมเดลแบบเต็ม:
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

คำเตือนเหล่านี้จะถูกพิมพ์โดย Unsloth ตอนเริ่มทำงานบน Windows ROCm และปลอดภัยที่จะเพิกเฉยได้ทั้งหมด:

| คำเตือน | สาเหตุ | ปลอดภัยที่จะเพิกเฉยหรือไม่? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes ไม่มีบิลด์สำหรับ Windows ROCm | ใช่ — เพลย์บุ๊กนี้ใช้ `adamw_torch` ไม่ใช่ bnb |
| `No ROCm platform found for torch.distributed` | ROCm บน Windows ไม่รองรับการฝึกแบบกระจาย (distributed training) | ใช่ — การฝึกแบบ single-GPU ไม่ได้รับผลกระทบ |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth แจ้งเตือนสำหรับบิลด์ที่ไม่ใช่ Linux | ใช่ — Windows ROCm ใช้งานได้กับ single-GPU SFT |
| `triton is not available` | Triton ไม่มีบิลด์สำหรับ Windows | ใช่ — Unsloth จะกลับไปใช้ PyTorch kernels แทน |

การฝึกจะดำเนินไปได้อย่างถูกต้องแม้จะมีคำเตือนเหล่านี้
<!-- @os:end -->

## ขั้นตอนถัดไป
- ลองใช้ [Unsloth Studio](https://unsloth.ai/docs/new/studio) ซึ่งเป็น GUI ที่ใช้งานง่ายสำหรับ Unsloth
- ฝึกด้วยชุดข้อมูลเฉพาะของคุณเอง
- ลองปรับแต่งไฮเปอร์พารามิเตอร์ที่แตกต่างกัน
- ปรับใช้ (deploy) ด้วย vLLM หรือ llama.cpp
- ลองใช้ QLoRA สำหรับการตั้งค่าที่ใช้หน่วยความจำน้อยกว่า

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เกี่ยวกับ Unsloth และการไฟน์จูนมากขึ้น:

* [เอกสาร Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [คู่มือการไฟน์จูนของ Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)