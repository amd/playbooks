<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

เอกสารนี้แสดงวิธีการปรับแต่งโมเดลภาษาในเครื่องด้วย Unsloth บนฮาร์ดแวร์ AMD

โดยใช้ตัวอย่าง Supervised Fine-Tuning (SFT) แบบสั้นด้วย LoRA adapters บน `unsloth/gemma-4-E4B-it` โดยใช้ชุดข้อมูลย่อยของ `mlabonne/FineTome-100k` เป้าหมายคือให้เวิร์กโฟลว์แบบครบวงจรที่เรียบง่าย ครอบคลุมการตั้งค่า การฝึกโมเดล การอนุมาน และการบันทึกผลลัพธ์ที่ปรับแต่งแล้ว

ตัวอย่างนี้ถูกออกแบบให้ใช้งานได้จริงและปรับเปลี่ยนได้ง่าย ดังนั้นคุณสามารถใช้เป็นจุดเริ่มต้นสำหรับชุดข้อมูลและโมเดลของคุณเองได้

## สิ่งที่คุณจะได้เรียนรู้

- วิธีตั้งค่าสภาพแวดล้อม Unsloth
- วิธีปรับแต่ง LLM โดยใช้ SFT ร่วมกับ Unsloth
- วิธีบันทึกผลลัพธ์ที่ปรับแต่งแล้วในที่จัดเก็บข้อมูลภายในเครื่อง

<!-- @device:halo,stx,krk -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการ **RAM ระบบอย่างน้อย 64 GB** โดยต้องมีอย่างน้อย **24 GB ที่ใช้ได้กับ GPU** (24 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่เพิ่มเติมจาก 64 GB)
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการ **หน่วยความจำ GPU รวมอย่างน้อย 24 GB** และ **RAM ระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมประกอบด้วย VRAM เฉพาะของการ์ดจอรวมกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ยืมมาจาก RAM ระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 24 GB ก็ยังสามารถใช้งานเอกสารนี้ได้โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนต่าง
<!-- @os:end -->

<!-- @os:linux -->
> **หมายเหตุ:** เทคนิคการปรับแต่งในเอกสารนี้ต้องการการ์ดจอที่มี **หน่วยความจำ GPU เฉพาะอย่างน้อย 24 GB** และ **RAM ระบบ 32 GB**
> - บน Linux การฝึกโมเดลจะทำงานทั้งหมดใน VRAM เฉพาะของการ์ดจอ
> - ระบบจะไม่ใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (RAM ระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 24 GB จะเกิดปัญหาหน่วยความจำไม่พอระหว่างการฝึกบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->
<!-- @device:end -->

## ทำไมต้อง Unsloth?

Unsloth ช่วยให้การปรับแต่ง LLM ทำงานบนฮาร์ดแวร์ในเครื่องได้ง่ายขึ้น โดยลดการใช้หน่วยความจำและเพิ่มความเร็วในการฝึกโมเดลเมื่อเทียบกับการตั้งค่ามาตรฐาน

ในเอกสารนี้ เราใช้ Unsloth ร่วมกับ **SFT แบบใช้ LoRA** ซึ่งหมายความว่าโมเดลฐานจะยังคงถูกล็อกไว้เป็นส่วนใหญ่ ในขณะที่มีการฝึกชุดน้ำหนัก adapter ที่มีขนาดเล็กกว่ามาก วิธีนี้เหมาะสำหรับการพัฒนาในเครื่องเนื่องจากใช้ทรัพยากรน้อยกว่าการปรับแต่งแบบเต็มรูปแบบ และทำการทดลองซ้ำได้เร็วกว่า

Unsloth ยังรองรับแนวทางการฝึกอื่นๆ ด้วย รวมถึง QLoRA และเวิร์กโฟลว์การเรียนรู้แบบเสริมกำลัง (reinforcement learning) เอกสารนี้เน้นที่แนวทางที่ง่ายที่สุดก่อน นั่นคือตัวอย่างการปรับแต่งด้วย LoRA ขนาดเล็กที่ผู้ใช้สามารถรัน ทำความเข้าใจ และต่อยอดได้

## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

### สร้างสภาพแวดล้อมเสมือน

<!-- @os:linux -->
<!-- @device:halo_box -->
เปิดเทอร์มินัลและสร้าง venv ที่มี AMD ROCm™ software และ PyTorch ติดตั้งไว้แล้ว:
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
> **หมายเหตุ:** จำเป็นต้องใช้ Python 3.13 สำหรับ Windows

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

### ติดตั้ง Dependency พื้นฐาน
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

### Dependency เพิ่มเติม

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **หมายเหตุ:** ระหว่างการ import Unsloth อาจตรวจสอบเส้นทางการเร่งความเร็วแบบเสริมของ `bitsandbytes` บน ROCm บางเวอร์ชัน คุณอาจเห็นข้อความเช่น `bitsandbytes library load error: Configured ROCm binary not found` เอกสารนี้ใช้การปรับแต่งแบบ LoRA มาตรฐานด้วย `optim="adamw_torch"` ดังนั้นเราจึงไม่ต้องพึ่งพา optimizer ของ `bitsandbytes` หรือ QLoRA แบบ 4-bit ข้อความนี้สามารถละเว้นได้อย่างปลอดภัย

<!-- @os:windows -->
> **หมายเหตุ:** บน Windows ROCm Unsloth จะแสดงคำเตือนหลายรายการเมื่อเริ่มทำงาน — ดู [Known Warnings](#known-warnings) ด้านล่าง คำเตือนเหล่านี้สามารถละเว้นได้อย่างปลอดภัยทั้งหมด การฝึกโมเดลยังคงทำงานได้อย่างถูกต้อง
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

แทนที่จะรันแต่ละขั้นตอนด้วยตนเอง เอกสารนี้มีสคริปต์แบบครบวงจรที่ชัดเจนให้ที่นี่: [test_unsloth.py](assets/test_unsloth.py)

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

ส่วนที่เหลือของเอกสารนี้จะอธิบายแนวคิดของแต่ละขั้นตอนหลักในสคริปต์

## หลักการทำงาน

สคริปต์ test_unsloth.py ดำเนินการตามขั้นตอนต่อไปนี้:
* **โหลดโมเดล**: โหลด unsloth/gemma-4-E4B-it โดยใช้ FastModel
* **เตรียมข้อมูล**: ทำให้ชุดข้อมูล (เช่น FineTome-100k) เป็นมาตรฐาน และใช้เทมเพลตแชทของ Gemma-4
* **ใช้ LoRA**: เพิ่ม adapter ให้กับโมดูลภาษา, attention และ MLP เพื่อการฝึกที่มีประสิทธิภาพ
* **ฝึกโมเดล**: ใช้ SFTTrainer พร้อมการปิดบัง loss เฉพาะส่วนคำตอบ (response-only loss masking)
* **อนุมาน**: รันการทดสอบสร้างข้อความอย่างรวดเร็วเพื่อตรวจสอบประสิทธิภาพ
* **บันทึก**: ส่งออก LoRA adapter ในเครื่อง

## การตั้งค่าที่สำคัญ

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
ชุดข้อมูลนี้ถูก:
* แปลงเป็นรูปแบบแชท
* ประมวลผลโดยใช้เทมเพลตแชทของ Gemma-4
* ทำความสะอาดเพื่อลบโทเคน BOS ที่ซ้ำกัน

## ฝึกโมเดล

สคริปต์จะรันการสาธิตการฝึกแบบสั้น ด้วยพารามิเตอร์ต่อไปนี้:
- ประมาณ 50 ขั้นตอน
- ขนาด batch เล็ก
- การสะสม gradient (gradient accumulation)

ระหว่างการฝึก คุณจะเห็นบันทึก log เช่น:

![alt text](assets/training.png)


## การบันทึกและการปรับใช้งาน
### บันทึกในเครื่อง (LoRA)

สคริปต์จะบันทึกอะแดปเตอร์ LoRA ไปยัง OUTPUT_DIR โดยอัตโนมัติ
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
> **หมายเหตุ:** vLLM ไม่รองรับ Windows หากต้องการนำโมเดลที่ปรับแต่งเพิ่มเติมมาใช้งานบน Windows ให้ใช้ llama.cpp (ดู [ส่งออก GGUF](#export-gguf-for-llamacpp) ด้านล่าง) หรือย้ายโมเดลที่ผสานรวมแล้วไปยังเครื่อง Linux ที่รัน vLLM
<!-- @os:end -->

<!-- @os:linux -->
สำหรับการนำไปใช้งานกับ vLLM ให้ผสานอะแดปเตอร์เข้ากับโมเดลเต็มรูปแบบ:
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

คำเตือนเหล่านี้จะถูกแสดงโดย Unsloth เมื่อเริ่มทำงานบน Windows ROCm และสามารถเพิกเฉยได้อย่างปลอดภัยทั้งหมด:

| คำเตือน | สาเหตุ | สามารถเพิกเฉยได้หรือไม่ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes ไม่มีบิลด์สำหรับ Windows ROCm | ได้ — คู่มือนี้ใช้ `adamw_torch` ไม่ใช่ bnb |
| `No ROCm platform found for torch.distributed` | ROCm บน Windows ไม่รองรับการฝึกแบบกระจาย | ได้ — ไม่มีผลต่อการฝึกแบบ GPU เดียว |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth แจ้งเตือนบิลด์ที่ไม่ใช่ Linux | ได้ — Windows ROCm ใช้งานได้กับ SFT แบบ GPU เดียว |
| `triton is not available` | Triton ไม่มีบิลด์สำหรับ Windows | ได้ — Unsloth จะใช้ PyTorch kernel แทน |

การฝึกจะดำเนินต่อไปได้อย่างถูกต้องแม้จะมีคำเตือนเหล่านี้
<!-- @os:end -->

## ขั้นตอนถัดไป
- ลองใช้ [Unsloth Studio](https://unsloth.ai/docs/new/studio) ซึ่งเป็น GUI ที่ใช้งานง่ายสำหรับ Unsloth
- ฝึกด้วยชุดข้อมูลเฉพาะของคุณเอง
- ลองปรับแต่งด้วยไฮเปอร์พารามิเตอร์ที่แตกต่างกัน
- นำไปใช้งานด้วย vLLM หรือ llama.cpp
- ลองใช้ QLoRA สำหรับการตั้งค่าที่ใช้หน่วยความจำน้อยลง

## แหล่งข้อมูล

ด้านล่างนี้คือแหล่งข้อมูลเพิ่มเติมเพื่อเรียนรู้เกี่ยวกับ Unsloth และการปรับแต่งเพิ่มเติมมากขึ้น:

* [เอกสาร Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [คู่มือการปรับแต่งเพิ่มเติมของ Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)