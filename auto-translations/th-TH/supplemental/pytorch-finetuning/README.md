<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> เพลย์บุ๊กนี้ใช้แท็กพิเศษที่ GitHub ไม่สามารถแสดงผลได้ กรุณาเข้าชม [amd.com/playbooks](https://amd.com/playbooks) เพื่อดูตัวอย่างเนื้อหานี้อย่างถูกต้อง
<!-- @github-only:end -->

## ภาพรวม

บทช่วยสอนนี้มีตัวอย่างทีละขั้นตอนสำหรับการปรับแต่งโมเดลภาษาขนาดใหญ่ (LLM) ด้วย PyTorch และ ROCm ครอบคลุมเทคนิคหลายรูปแบบ ตั้งแต่การปรับแต่งแบบมาตรฐานไปจนถึงกลยุทธ์ Parameter-Efficient Fine-Tuning (PEFT) ที่ประหยัดหน่วยความจำ เพื่อให้คุณสามารถปรับใช้โมเดลให้เหมาะกับความต้องการของคุณได้อย่างง่ายดาย

**โมเดลที่ใช้**: google/gemma-3-4b-it  *(ดู [เปิดใช้งานการรับรองตัวตนของ HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) หากเป็นโมเดลแบบ gated)*  
**ฮาร์ดแวร์**: AMD Radeon™ GPU ที่รองรับ ROCm  
**เฟรมเวิร์ก**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **หมายเหตุ:** คุณยังสามารถลองสถาปัตยกรรมโมเดลอื่นๆ ได้ รวมถึง **GPT-OSS-20B** โดยการแทนที่โมเดลในสคริปต์การฝึกที่ให้มา
> การปรับแต่งแบบเต็มรูปแบบ (Full fine-tuning) ต้องการหน่วยความจำ GPU อย่างน้อย 32 GB และ RAM ของระบบ 64 GB
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **หมายเหตุ:** การปรับแต่งด้วย LoRA และ QLoRA ต้องการหน่วยความจำ GPU อย่างน้อย 16 GB และ RAM ของระบบ 32 GB
<!-- @device:end -->

## สิ่งที่คุณจะได้เรียนรู้

- วิธีปรับแต่ง LLM โดยใช้ LoRA, QLoRA และการปรับแต่งแบบเต็มรูปแบบด้วย PyTorch และ ROCm
- วิธีบันทึกและนำโมเดลที่ปรับแต่งแล้วไปใช้งาน
- วิธีตรวจสอบการฝึกและแก้ไขปัญหาที่พบบ่อย

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์
> **หมายเหตุ**: หากยังไม่ได้ติดตั้ง VS Code คุณสามารถติดตั้งได้ด้วย Ryzen AI Developer Center

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
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
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** มีเพียงแพ็กเกจหลักเท่านั้นที่ได้รับการทดสอบและรองรับในที่นี้ **bitsandbytes ไม่ได้รับการรองรับที่ดีบน Windows** ดังนั้นการติดตั้งบน Windows จึงไม่รวม bitsandbytes ให้ใช้ LoRA หรือการปรับแต่งแบบเต็มรูปแบบบน Windows (QLoRA ต้องใช้ bitsandbytes และมีไว้สำหรับ Linux)
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### เปิดใช้งานการรับรองตัวตนของ HF (โมเดลแบบ gated หรือแบบกำหนดเอง / ที่ไม่ได้ติดตั้งไว้ล่วงหน้า)

ในตัวอย่างนี้เราใช้ **google/gemma-3-4b-it** ซึ่งเป็นโมเดลแบบ **gated** คุณต้องยอมรับข้อกำหนดของโมเดลบน Hugging Face ก่อน จากนั้นจึงยืนยันตัวตนเพื่อให้สคริปต์การฝึกสามารถดาวน์โหลดได้

1. **ยอมรับใบอนุญาต:** เปิด [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) เข้าสู่ระบบ (หรือสร้างบัญชี) และยอมรับใบอนุญาต/ข้อกำหนดบนหน้าโมเดล (เช่น “Agree and access repository”)
2. **ติดตั้งและเข้าสู่ระบบ:** ติดตั้ง Hugging Face CLI จากนั้นรันคำสั่งเข้าสู่ระบบมาตรฐาน:

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

## ทำความเข้าใจเทคนิคต่างๆ

### LoRA คืออะไร?

**LoRA (Low-Rank Adaptation)** จะคงโมเดลฐานไว้แบบไม่เปลี่ยนแปลง (frozen) และฝึกเฉพาะเมทริกซ์ "adapter" ขนาดเล็กที่ถูกเพิ่มเข้าไปในบางเลเยอร์เท่านั้น

- **แนวคิดหลัก**: แทนที่จะอัปเดตเมทริกซ์น้ำหนักขนาดใหญ่ที่มีพารามิเตอร์หลายล้านตัว เราเรียนรู้การอัปเดตแบบ low-rank (เมทริกซ์ขนาดเล็กสองตัวที่ผลคูณมีพารามิเตอร์น้อยกว่ามาก) ซึ่งช่วยลดจำนวนพารามิเตอร์ที่ต้องฝึกและ VRAM ได้อย่างมาก ในขณะที่ยังคงคุณภาพส่วนใหญ่ของการปรับแต่งแบบเต็มรูปแบบไว้

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

**QLoRA** รวม **การควอนไทซ์แบบ 4-บิต** เข้ากับ **LoRA** โมเดลฐานจะถูกโหลดในรูปแบบ 4-บิต (ประหยัดหน่วยความจำได้มาก) และมีเพียง LoRA adapters เท่านั้นที่ถูกฝึกด้วยความแม่นยำที่สูงกว่า ดังนั้นคุณจะได้ทั้งประสิทธิภาพด้านพารามิเตอร์ของ LoRA และ VRAM ที่ต่ำลงมาก โดยแลกกับคุณภาพที่ลดลงเล็กน้อยเมื่อเทียบกับ LoRA แบบความแม่นยำเต็ม โปรดทราบว่าการควอนไทซ์แบบ 4-บิตอาจทำให้เกิดความไม่เสถียรทางตัวเลข (loss พุ่งขึ้นหรือค่า NaN) ดังนั้นผู้ใช้อาจต้องการเลือกใช้ **LoRA** แทน หากมี VRAM เพียงพอ

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **หมายเหตุ**: สำหรับโมเดลฐานแบบ MXFP4 เช่น `openai/gpt-oss-20b` เราแนะนำให้ใช้ **LoRA** (`train_lora.py`) แทน QLoRA เนื่องจากพาธ 4-บิตของ `bitsandbytes` ในสคริปต์ QLoRA มักจะแปลงน้ำหนัก MXFP4 กลับเป็น BF16 (dequantize) ทำให้การรันมีพฤติกรรมเหมือน LoRA มาตรฐาน MXFP4 แบบเนทีฟจำเป็นต้องใช้ `bitsandbytes` ที่คอมไพล์จากซอร์สโค้ด พร้อมกับชุด Transformers/Triton/kernels ที่รองรับกัน ดูรายละเอียดเพิ่มเติมได้ที่ [เอกสาร Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)

---

### 2. เลือกวิธีของคุณ

| วิธี | หน่วยความจำ | ความเร็ว | คุณภาพ | เหมาะที่สุดสำหรับ |
|--------|--------|-------|---------|----------|
| **QLoRA** (เฉพาะ Linux) | 12-16GB | เร็วที่สุด | 90-95% | การใช้หน่วยความจำต่ำ |
| **LoRA** | 24-32GB | เร็ว | 95-98% | แนวทางที่สมดุล |
| **Full** | 80GB+ | ช้าที่สุด | 100% | คุณภาพสูงสุด |
### 3. เริ่มการฝึกโมเดล (Run Training)

**ชุดข้อมูลและสิ่งที่โมเดลเรียนรู้**  
สคริปต์เหล่านี้จะแปลงชุดข้อมูลให้เป็นตัวอย่างการสนทนา ตัวอย่างเช่น สคริปต์ QLoRA ใช้ **Abirate/english_quotes**: แต่ละตัวอย่างจะกลายเป็นคู่ user–assistant ดังนี้:

- **User:** “Give me a quote about: &lt;tag&gt;”
- **Assistant:** “&lt;quote&gt; – &lt;author&gt;”

การไฟน์จูนจะสอนให้โมเดลตอบสนองต่อพรอมป์ที่ขอคำคมเกี่ยวกับหัวข้อหนึ่ง ๆ และให้ตอบกลับในรูปแบบ `<quote text> - <author>` สคริปต์ LoRA และการไฟน์จูนแบบเต็มรูปแบบ (full fine-tuning) จะใช้ **databricks/databricks-dolly-15k** (คู่คำสั่ง/คำตอบทั่วไป) ดังนั้นงานที่แท้จริงจะแตกต่างกันไปตามแต่ละสคริปต์ แต่แนวคิดพื้นฐานเหมือนกัน คือการปรับโมเดลให้เข้ากับชุดข้อมูลและรูปแบบที่คุณเลือก

ด้านล่างนี้คือสรุปวิธีการฝึกที่มีให้ใช้งาน แต่ละวิธีจะลิงก์ไปยังสคริปต์ของตนเองพร้อมคำอธิบายสั้น ๆ เพื่อช่วยในการเลือกแนวทางที่เหมาะสม

| Script                           | Method            | Description                                                                                                         | Typical VRAM | Recommended For                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | ฝึกเมทริกซ์ adapter ขนาดเล็กโดยล็อกโมเดลฐานไว้ เร็วกว่า 3–5 เท่า; คุณภาพประมาณ 95–98% ของการฝึกแบบเต็มรูปแบบ                         | 24–32GB      | ผู้ใช้ขั้นสูง; ใช้ adapter หลายตัว; มี VRAM มากกว่า    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux only)*             | **QLoRA**       | การควอนไทซ์ 4 บิต + adapter แบบ LoRA ใช้หน่วยความจำน้อยที่สุด เร็วที่สุด แลกกับคุณภาพที่ลดลงเล็กน้อย ต้องใช้ `bitsandbytes` (เฉพาะ Linux เท่านั้น)                            | 12–16GB      | ผู้ใช้ส่วนใหญ่; การทดลองที่รวดเร็ว; VRAM จำกัด      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | ปรับพารามิเตอร์ของโมเดลทั้งหมด ให้คุณภาพสูงสุด ใช้หน่วยความจำและการประมวลผลมากที่สุด                                    | 40GB+        | คุณภาพสูงสุด; งานวิจัย; มี VRAM มาก           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **หมายเหตุ:** การไฟน์จูนแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA หรือ QLoRA แทน
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ:** การไฟน์จูนแบบเต็มรูปแบบ (`train_full_finetuning.py`) อาจต้องใช้ RAM ของระบบมากกว่า 64GB และอาจไม่สามารถทำได้บนอุปกรณ์นี้ ควรพิจารณาใช้ LoRA แทน
<!-- @os:end -->
<!-- @device:end -->

เพียงเลือก `Training method` ที่คุณต้องการ ดาวน์โหลดสคริปต์ที่เกี่ยวข้อง และรันโดยใช้คำสั่งต่อไปนี้ พร้อมเปิดใช้งานสภาพแวดล้อมเสมือน (virtual environment) ของคุณไว้: 

```python
python3 train_<method_name>.py.
```

## การใช้งานโมเดลที่ผ่านการไฟน์จูนของคุณ

### หลังจากการไฟน์จูนแบบเต็มรูปแบบ (Full Fine-Tuning)

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

### หลังจากการฝึกด้วย LoRA/QLoRA

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

### รวม LoRA Adapter เข้ากับโมเดลฐาน

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**หมายเหตุ:**  
- ตรวจสอบให้แน่ใจว่าชื่อไดเรกทอรีของโมเดล (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) ตรงกับโฟลเดอร์ผลลัพธ์จริงจากการฝึกของคุณ  
- หากคุณใช้ LoRA แทน QLoRA ให้แทนที่พาธให้เหมาะสม  
- โมเดล Gemma บางรุ่นต้องระบุ `trust_remote_code=True` ใน `from_pretrained` ให้เพิ่มเข้าไปหากคุณเห็นคำเตือนที่เกี่ยวข้อง

สำหรับการตั้งค่าที่กำหนดเองเพิ่มเติม (padding tokens, device เป็นต้น) โปรดดูสคริปต์ที่คุณใช้ในการฝึก

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## คู่มือการปรับแต่ง (Customization Guide)

### ใช้ชุดข้อมูลของคุณเอง

สคริปต์ทั้งหมดใช้รูปแบบชุดข้อมูลเดียวกัน ให้แทนที่ส่วนการโหลดข้อมูล:

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

เมื่อใช้วิธีนี้ โปรดตรวจสอบให้แน่ใจว่าไฟล์ JSON ของคุณมีโครงสร้างที่ถูกต้อง เพื่อหลีกเลี่ยงข้อผิดพลาดในการแยกวิเคราะห์ 

ต้องปฏิบัติตามแนวทางต่อไปนี้:
* **การจัดรูปแบบไฟล์:** ไฟล์ JSON ควรจัดรูปแบบภายในสภาพแวดล้อมการพัฒนาแบบรวม (IDE) เพื่อให้มั่นใจว่ามีโครงสร้างและไวยากรณ์ที่ถูกต้อง
* **คีย์ที่จำเป็น:** ไฟล์ JSON ที่กำหนดเองต้องมีคีย์ `instruction` และ `response` คีย์เหล่านี้มีความสำคัญต่อการทำงานของวิธีนี้ให้ถูกต้อง
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
**รูปแบบชุดข้อมูลสำหรับชุดข้อมูลจาก Hugging Face Hub**

เมื่อใช้ชุดข้อมูลจาก Hugging Face โปรดตรวจสอบให้แน่ใจว่าชุดข้อมูลของคุณมีโครงสร้างที่ถูกต้องเพื่อให้การรวมเข้าด้วยกันเป็นไปอย่างราบรื่น 

ควรปฏิบัติตามแนวทางต่อไปนี้:
* **คู่คำสั่ง-คำตอบ (Instruction-Response Pair):** เน้นชุดข้อมูลที่มีคู่ `instruction-response` โครงสร้างนี้มีความสำคัญต่อการทำงานที่ตั้งใจไว้
* **การปรับเปลี่ยนคีย์แบบกำหนดเอง:** หากชุดข้อมูลของคุณไม่สอดคล้องกับโครงสร้าง `instruction-response` คุณสามารถปรับเปลี่ยนฟังก์ชัน `format_instruction()` ได้ ซึ่งช่วยให้คุณรองรับคีย์เฉพาะตามที่ต้องการ

ตัวอย่างการปรับเปลี่ยน: ในกรณีที่ผลลัพธ์ของชุดข้อมูลจำเป็นต้องปรับเปลี่ยน คุณสามารถแก้ไขส่วนคำตอบภายในฟังก์ชัน format_instruction() ให้เหมาะกับความต้องการของคุณได้
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

### ปรับพารามิเตอร์การฝึก

แก้ไขสคริปต์การฝึกและเปลี่ยนตัวแปรให้ตรงกับเป้าหมายของคุณ: **อัตราการเรียนรู้** (`LR`), **จำนวนรอบการฝึก** (`EPOCHS`), **ขนาดแบทช์** (`BATCH_SIZE`), **การสะสมเกรเดียนต์** (`GRAD_ACCUM_STEPS`) และสำหรับ LoRA/QLoRA คือ **rank** (`LORA_R`) หากต้องการรันที่รวดเร็วขึ้นให้ใช้จำนวนรอบการฝึกน้อยลงและอัตราการเรียนรู้ (LR) ที่สูงขึ้น หากต้องการคุณภาพที่ดีขึ้นให้ใช้จำนวนรอบการฝึกมากขึ้นและ LR ที่ต่ำลง ลดขนาดแบทช์หรือความยาวของลำดับ (sequence length) หากพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (out-of-memory)

### เคล็ดลับการปรับแต่งหน่วยความจำ

หากคุณพบข้อผิดพลาดหน่วยความจำไม่เพียงพอ (out-of-memory):

**1. ลดขนาดแบทช์ (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. ลดความยาวของลำดับ (Sequence Length):**
```python
max_seq_length=256  # Instead of 512
```

**3. ใช้การควอนไทซ์ที่เข้มข้นขึ้น:**
```
Full → LoRA → QLoRA
```

**4. เปิดใช้งาน Gradient Checkpointing (เฉพาะการไฟน์จูนแบบเต็มรูปแบบเท่านั้น):**
```python
model.gradient_checkpointing_enable()
```

---

## การตรวจสอบและแก้ไขปัญหา (Monitoring & Debugging)

### ตรวจสอบหน่วยความจำ GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (ตัวเลือกเพิ่มเติม) ติดตามการทดลองด้วย Weights & Biases

หากต้องการบันทึกการรันและเมตริกไปยัง [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

ในสคริปต์การฝึก ให้ตั้งค่า `report_to="wandb"` และ `run_name="your-experiment-name"` (ตัวเลือกเพิ่มเติม) ในการตั้งค่า trainer หากคุณไม่ต้องการใช้ Wandb ให้ปล่อย `report_to` ไว้ที่ค่าเริ่มต้นหรือตั้งค่าเป็น `"none"`

### ปัญหาที่พบบ่อย

#### หน่วยความจำไม่เพียงพอ (Out of Memory - OOM)

**วิธีแก้ไข:** ลดขนาด batch และ/หรือใช้ QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ค่า Loss ไม่ลดลง

**วิธีแก้ไข:** ปรับอัตราการเรียนรู้ (learning rate)
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

หลังจากที่คุณทำการปรับแต่งโมเดล (fine-tuning) สำเร็จแล้ว ให้พิจารณาขั้นตอนถัดไปต่อไปนี้เพื่อให้ได้ประโยชน์สูงสุดจากโมเดลของคุณ:

1. **ประเมินผล** อย่างละเอียดบนชุดข้อมูลทดสอบที่แยกไว้ต่างหาก (held-out test data) เพื่อวัดความสามารถในการทำงานกับข้อมูลใหม่และหลีกเลี่ยงการโอเวอร์ฟิต (overfitting)
2. **ทดลอง** โดยลองใช้ค่าไฮเปอร์พารามิเตอร์ (hyperparameter) ที่แตกต่างกันเพื่อให้ได้ความสมดุลที่ดีขึ้นระหว่างความแม่นยำ ความเร็ว และการใช้หน่วยความจำ
3. **ติดตาม** การทดลองทั้งหมดของคุณ (พร้อมเมตริกที่เกี่ยวข้อง) ด้วย Weights & Biases เพื่อให้สามารถทำวิจัยที่ทำซ้ำได้
4. **ลอง** ฝึกด้วยชุดข้อมูลที่กำหนดเองของคุณเพื่อปรับโมเดลให้เหมาะกับกรณีการใช้งานของคุณโดยเฉพาะ
5. **ปรับใช้** โมเดลที่ปรับแต่งแล้วของคุณเพื่อการอนุมาน (inference) ที่รวดเร็วโดยใช้แบ็กเอนด์ที่มีประสิทธิภาพ เช่น vLLM บนฮาร์ดแวร์ที่รองรับ
6. **สำรวจ** เทคนิคขั้นสูง รวมถึงวิศวกรรมพรอมต์ (prompt engineering) การใช้ความแม่นยำแบบผสม (mixed precision) และความยาวลำดับที่มากขึ้น
7. **ฝึก** ตัวปรับแต่ง LoRA หลายตัวสำหรับงานหรือโดเมนที่แตกต่างกัน และสลับใช้งานตามความจำเป็น

---