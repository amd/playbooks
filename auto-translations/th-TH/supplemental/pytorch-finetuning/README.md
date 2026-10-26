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

บทช่วยสอนนี้มีตัวอย่างแบบทีละขั้นตอนสำหรับการปรับแต่ง (fine-tuning) โมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm โดยครอบคลุมเทคนิคหลายรูปแบบ ตั้งแต่การปรับแต่งมาตรฐานไปจนถึงกลยุทธ์ Parameter-Efficient Fine-Tuning (PEFT) ที่ประหยัดหน่วยความจำ เพื่อให้คุณสามารถปรับโมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it  *(ดู [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากเป็นโมเดลแบบ gated)*  
**ฮาร์ดแวร์**: AMD Radeon™ GPU ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** 
> - การปรับแต่งแบบเต็มรูปแบบ (Full fine-tuning) ต้องใช้ **RAM ระบบอย่างน้อย 64 GB** โดยต้องมี **อย่างน้อย 32 GB ที่ใช้งานได้กับ GPU** (32 GB นี้เป็นส่วนหนึ่งของ 64 GB ไม่ใช่ส่วนเพิ่มเติม)
> - คุณยังสามารถลองใช้สถาปัตยกรรมโมเดลอื่น ๆ รวมถึง **GPT-OSS-20B** ได้ โดยแทนที่โมเดลในสคริปต์การฝึกอบรมที่ให้มา
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องใช้ **RAM ระบบอย่างน้อย 32 GB** โดยต้องมี **อย่างน้อย 16 GB ที่ใช้งานได้กับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่ส่วนเพิ่มเติม)
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องใช้ **RAM ระบบอย่างน้อย 32 GB** โดยต้องมี **อย่างน้อย 16 GB ที่ใช้งานได้กับ GPU** (16 GB นี้เป็นส่วนหนึ่งของ 32 GB ไม่ใช่ส่วนเพิ่มเติม)
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA และ QLoRA ต้องใช้การ์ดกราฟิกที่มี **หน่วยความจำ GPU เฉพาะอย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Linux การฝึกอบรมจะทำงานทั้งหมดในหน่วยความจำ VRAM เฉพาะของการ์ดกราฟิก
> - ระบบจะไม่ย้อนกลับไปใช้หน่วยความจำ GPU ที่ใช้ร่วมกัน (RAM ระบบ) เมื่อ VRAM หมด
> - การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB จะเกิดปัญหาหน่วยความจำไม่พอระหว่างการฝึกอบรมบน Linux แม้ว่าระบบจะมี RAM เหลือเฟือก็ตาม
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งแบบ LoRA ต้องใช้ **หน่วยความจำ GPU รวมอย่างน้อย 16 GB** และ **RAM ระบบ 32 GB**
> - บน Windows หน่วยความจำ GPU รวมจะประกอบด้วย VRAM เฉพาะของการ์ดกราฟิกรวมกับหน่วยความจำ GPU ที่ใช้ร่วมกัน (ยืมมาจาก RAM ระบบ)
> - ดังนั้น การ์ดที่มี VRAM เฉพาะน้อยกว่า 16 GB ก็ยังสามารถทำตามคู่มือนี้ได้ โดยใช้หน่วยความจำ GPU ที่ใช้ร่วมกันเพื่อชดเชยส่วนที่ขาด
<!-- @os:end -->
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีการปรับแต่ง LLM โดยใช้ LoRA, QLoRA และการปรับแต่งแบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีการบันทึกและปรับใช้โมเดลที่ปรับแต่งแล้วของคุณ
- วิธีการติดตามการฝึกอบรมและแก้ไขปัญหาที่พบบ่อย

<!-- @device:halo_box,halo,stx,krk -->
## การตั้งค่าหน่วยความจำ

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### การติดตั้งไลบรารีพื้นฐานที่จำเป็น
<!-- @require:pytorch -->

#### ไลบรารีเพิ่มเติมที่จำเป็น

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีการทดสอบและรองรับเฉพาะแพ็กเกจหลักเท่านั้นที่นี่ **bitsandbytes ไม่ได้รับการรองรับที่ดีบน Windows** ดังนั้นการติดตั้งบน Windows จะไม่รวม bitsandbytes ให้ใช้ LoRA หรือการปรับแต่งแบบเต็มรูปแบบบน Windows (QLoRA ต้องใช้ bitsandbytes และมีไว้สำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการยืนยันตัวตน HF (โมเดลแบบ gated หรือแบบกำหนดเอง / ที่ไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลแบบ **gated** คุณต้องยอมรับข้อตกลงของโมเดลบน Hugging Face ก่อน แล้วจึงยืนยันตัวตนเพื่อให้สคริปต์การฝึกอบรมสามารถดาวน์โหลดโมเดลได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) เข้าสู่ระบบ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อตกลงบนหน้าโมเดล (เช่น "Agree and access repository")
2. **ติดตั้งและเข้าสู่ระบบ:** ติดตั้ง Hugging Face CLI จากนั้นเรียกใช้การเข้าสู่ระบบมาตรฐาน:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## ทำความเข้าใจเทคนิคต่าง ๆ

### LoRA คืออะไร?

**LoRA (Low-Rank Adaptation)** จะคงโมเดลฐานไว้แบบไม่เปลี่ยนแปลง (frozen) และฝึกเฉพาะเมทริกซ์ "อะแดปเตอร์" ขนาดเล็กที่จะถูกเพิ่มเข้าไปในบางเลเยอร์ 

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์นับล้าน เราเรียนรู้การอัปเดตแบบ low-rank (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณของทั้งสองมีพารามิเตอร์น้อยกว่ามาก) วิธีนี้ช่วยลดพารามิเตอร์ที่ต้องฝึกและ VRAM ได้อย่างมาก ในขณะที่ยังคงคุณภาพของการปรับแต่งแบบเต็มรูปแบบไว้ได้เกือบทั้งหมด

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA คืออะไร?

**QLoRA** ผสมผสาน **การควอนไทซ์แบบ 4-bit** เข้ากับ **LoRA** โมเดลฐานจะถูกโหลดในรูปแบบ 4-bit (ประหยัดหน่วยความจำได้มาก) และมีเพียงอะแดปเตอร์ LoRA เท่านั้นที่ถูกฝึกด้วยความแม่นยำที่สูงกว่า ดังนั้นคุณจะได้ทั้งประสิทธิภาพด้านพารามิเตอร์ของ LoRA และ VRAM ที่ต่ำกว่ามาก โดยมีการแลกเปลี่ยนคุณภาพเล็กน้อยเมื่อเทียบกับ LoRA แบบความแม่นยำเต็ม โปรดทราบว่าการควอนไทซ์แบบ 4-bit อาจก่อให้เกิดความไม่เสถียรทางตัวเลข (loss พุ่งสูงหรือ NaN) ดังนั้นผู้ใช้อาจต้องการเลือกใช้ **LoRA** แทน หากมี VRAM เพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลฐานแบบ MXFP4 เช่น `openai/gpt-oss-20b` เราแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เนื่องจากเส้นทางการทำงานแบบ 4-bit ของ `bitsandbytes` ในสคริปต์ QLoRA มักจะทำการ dequantize น้ำหนัก MXFP4 เป็น BF16 ทำให้การรันทำงานเหมือนกับ LoRA มาตรฐาน MXFP4 แบบเนทีฟต้องใช้ `bitsandbytes` ที่คอมไพล์จากซอร์สโค้ด รวมถึงชุด Transformers/Triton/kernels ที่ตรงกัน ดูรายละเอียดเพิ่มเติมได้ที่ [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---
### 2. เลือกวิธีการของคุณ

| วิธีการ | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (เฉพาะ Linux) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |

### 3. เริ่มการฝึกอบรม (Training)

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์เหล่านี้จะเปลี่ยนชุดข้อมูลให้เป็นตัวอย่างการแชท ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่ user–assistant เช่น:

- **User:** “Give me a quote about: &lt;tag&gt;”
- **Assistant:** “&lt;quote&gt; – &lt;author&gt;”

การปรับแต่งละเอียด (Fine-tuning) จะสอนให้โมเดลตอบสนองต่อพรอมต์ที่ขอคำคมเกี่ยวกับหัวข้อหนึ่ง ๆ และส่งคืนในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และการปรับแต่งละเอียดแบบเต็มรูปแบบ (full fine-tuning) ใช้ **databricks/databricks-dolly-15k** (คู่คำสั่ง/การตอบสนองทั่วไป) ดังนั้นงานที่แท้จริงจะแตกต่างกันไปตามสคริปต์ แนวคิดยังคงเดิม - ปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปวิธีการฝึกอบรมที่มีให้ใช้งาน แต่ละวิธีจะเชื่อมโยงไปยังสคริปต์ของตนเองและมีคำอธิบายสั้น ๆ เพื่อช่วยเลือกแนวทางที่เหมาะสม

| สคริปต์                           | วิธีการ            | คำอธิบาย                                                                                                         | VRAM ทั่วไป | แนะนำสำหรับ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึกเมทริกซ์อะแดปเตอร์ขนาดเล็กในขณะที่หยุดการอัปเดตโมเดลฐาน เร็วกว่า 3–5 เท่า; คุณภาพประมาณ 95–98% ของแบบเต็ม                        | 24–32GB      | ผู้ใช้ขั้นสูง; อะแดปเตอร์หลายตัว; VRAM มากขึ้น    |
| [`train_qlora.py`](assets/train_qlora.py)  *(เฉพาะ Linux)*             | **QLoRA**       | การควอนไทซ์ 4-bit + อะแดปเตอร์ LoRA ใช้หน่วยความจำต่ำสุด เร็วที่สุด มีการแลกเปลี่ยนคุณภาพเพียงเล็กน้อย ต้องใช้ `bitsandbytes` (เฉพาะ Linux)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองที่รวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **การปรับแต่งละเอียดแบบเต็มรูปแบบ (Full Fine-tuning)** | อัปเดตพารามิเตอร์ทั้งหมดของโมเดล คุณภาพสูงสุด; ใช้หน่วยความจำและการประมวลผลสูงสุด                                    | 40GB+        | คุณภาพสูงสุด; งานวิจัย; VRAM จำนวนมาก           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การปรับแต่งละเอียดแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การปรับแต่งละเอียดแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่เกี่ยวข้อง และรันโดยใช้คำสั่งนี้ในขณะที่เปิดใช้งาน virtual environment ของคุณอยู่: 

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ปรับแต่งละเอียดแล้วของคุณ

### หลังจากการปรับแต่งละเอียดแบบเต็มรูปแบบ

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### หลังจากการฝึกอบรมด้วย LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### รวมอะแดปเตอร์ LoRA เข้ากับโมเดลฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีของโมเดล (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) ตรงกับโฟลเดอร์ผลลัพธ์จริงจากการฝึกอบรมของคุณ  
- หากคุณใช้ LoRA แทน QLoRA เพียงแค่แทนที่ path ให้ตรงกัน  
- โมเดล Gemma บางตัวต้องระบุ `trust_remote_code=True` ใน `from_pretrained` ให้เพิ่มหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device เป็นต้น) โปรดดูสคริปต์ที่คุณใช้ในการฝึกอบรม

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## คู่มือการปรับแต่ง

### ใช้ชุดข้อมูลของคุณเอง

สคริปต์ทั้งหมดใช้รูปแบบชุดข้อมูลเดียวกัน แทนที่ส่วนการโหลด:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**รูปแบบชุดข้อมูลสำหรับไฟล์ JSON/JSONL ในเครื่อง:**

เมื่อใช้วิธีนี้ โปรดตรวจสอบให้แน่ใจว่าไฟล์ JSON ของคุณมีโครงสร้างที่ถูกต้องเพื่อหลีกเลี่ยงข้อผิดพลาดในการแยกวิเคราะห์ 

ต้องปฏิบัติตามแนวทางต่อไปนี้:
* **การจัดรูปแบบไฟล์:** ไฟล์ JSON ควรได้รับการจัดรูปแบบภายใน Integrated Development Environment (IDE) เพื่อให้แน่ใจว่ามีโครงสร้างและไวยากรณ์ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้จำเป็นสำหรับให้วิธีการทำงานได้อย่างถูกต้อง
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**รูปแบบชุดข้อมูลสำหรับชุดข้อมูล Hugging Face Hub**

เมื่อใช้ชุดข้อมูลจาก Hugging Face โปรดตรวจสอบให้แน่ใจว่าชุดข้อมูลของคุณมีโครงสร้างที่ถูกต้องเพื่อให้สามารถบูรณาการได้อย่างราบรื่น 

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **คู่ Instruction-Response:** เน้นชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้จำเป็นสำหรับการทำงานที่ต้องการ
* **การปรับแต่งคีย์แบบกำหนดเอง:** หากชุดข้อมูลของคุณไม่สอดคล้องกับโครงสร้าง `instruction-response` คุณมีตัวเลือกในการปรับเปลี่ยนฟังก์ชัน `format_instruction()` ซึ่งจะช่วยให้คุณรองรับคีย์เฉพาะตามที่ต้องการ

ตัวอย่างการปรับเปลี่ยน: ในกรณีที่ผลลัพธ์ของชุดข้อมูลต้องได้รับการปรับเปลี่ยน คุณสามารถแก้ไขส่วนการตอบสนองภายในฟังก์ชัน format_instruction() เพื่อให้ตรงตามความต้องการของคุณ
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**รูปแบบชุดข้อมูลสำหรับไฟล์ CSV**

เพื่อให้สคริปต์รองรับรูปแบบไฟล์ CSV คุณต้องตรวจสอบให้แน่ใจว่าไฟล์ CSV มีคอลัมน์ชื่อ `instruction` และ `response` 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ปรับแต่งพารามิเตอร์การฝึกอบรม

แก้ไขสคริปต์การฝึกอบรมและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA คือ **rank** (`LORA_R`) หากต้องการให้รันได้เร็วขึ้น ให้ใช้ epoch น้อยลงและ learning rate (LR) สูงขึ้น หากต้องการคุณภาพที่ดีขึ้น ให้ใช้ epoch มากขึ้นและ LR ต่ำลง ลด batch size หรือความยาวของลำดับ (sequence length) หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (out-of-memory)
### เคล็ดลับการเพิ่มประสิทธิภาพหน่วยความจำ

หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (out-of-memory):

**1. ลดขนาด Batch:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาวของ Sequence:**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การควอนไทซ์ที่เข้มข้นขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (สำหรับการ fine-tuning แบบเต็มรูปแบบเท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและดีบัก

### ตรวจสอบหน่วยความจำ GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (ทางเลือกเสริม) ติดตามการทดลองด้วย Weights & Biases

หากต้องการบันทึกการรันและเมตริกไปยัง [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

ในสคริปต์การฝึก ให้ตั้งค่า `report_to="wandb"` และตั้งค่า `run_name="your-experiment-name"` เพิ่มเติมได้ตามต้องการในการตั้งค่า trainer หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้น หรือกำหนดเป็น `"none"`

### ปัญหาที่พบบ่อย

#### หน่วยความจำไม่เพียงพอ (OOM)

**วิธีแก้ไข:** ลดขนาด batch และ/หรือใช้ QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ค่า Loss ไม่ลดลง

**วิธีแก้ไข:** ปรับ learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### การฝึกช้า

**วิธีแก้ไข:** เพิ่มขนาด batch หากหน่วยความจำเพียงพอ
```python
BATCH_SIZE = 8
```
## ขั้นตอนถัดไป

หลังจากที่คุณ fine-tuning สำเร็จแล้ว ควรพิจารณาขั้นตอนถัดไปดังต่อไปนี้เพื่อดึงศักยภาพจากโมเดลของคุณให้ได้มากขึ้น:

1. **ประเมินผล** อย่างละเอียดบนชุดข้อมูลทดสอบที่แยกไว้ต่างหาก เพื่อวัดความสามารถในการนำไปใช้ทั่วไปและหลีกเลี่ยงการ overfitting
2. **ทดลอง** ใช้ค่าไฮเปอร์พารามิเตอร์ต่าง ๆ เพื่อให้ได้ความแม่นยำ ความเร็ว และการแลกเปลี่ยนด้านหน่วยความจำที่ดีขึ้น
3. **ติดตาม** การทดลองทั้งหมด (พร้อมเมตริกที่เกี่ยวข้อง) ของคุณด้วย Weights & Biases เพื่อให้งานวิจัยสามารถทำซ้ำได้
4. **ลองฝึก** ด้วยชุดข้อมูลที่กำหนดเองของคุณ เพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **นำไปใช้งาน** โมเดลที่ fine-tuning แล้วของคุณเพื่อการอนุมานที่รวดเร็ว โดยใช้แบ็กเอนด์ที่มีประสิทธิภาพ เช่น vLLM บนฮาร์ดแวร์ที่รองรับ
6. **สำรวจ** เทคนิคขั้นสูง เช่น prompt engineering, mixed precision และความยาว sequence ที่ยาวขึ้น
7. **ฝึก** LoRA adapter หลายตัวสำหรับงานหรือโดเมนที่แตกต่างกัน และสลับใช้งานตามความจำเป็น

---