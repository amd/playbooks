<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

يوفر هذا البرنامج التعليمي أمثلة خطوة بخطوة لضبط نموذج لغوي كبير (LLM) باستخدام PyTorch و ROCm. يغطي عدة تقنيات، من الضبط الدقيق القياسي إلى استراتيجيات الضبط الدقيق الفعّال للمعاملات (PEFT) الموفرة للذاكرة، حتى تتمكن من تكييف النماذج بسهولة وفق احتياجاتك.

**النموذج المستخدم**: google/gemma-3-4b-it  *(راجع [تفعيل مصادقة HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) إذا كان النموذج مقيّداً)*  
**الأجهزة**: AMD Radeon™ GPU مع دعم ROCm  
**الإطار**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **ملاحظة:** يمكنك أيضاً تجربة بنيات نماذج أخرى، بما في ذلك **GPT-OSS-20B**، عن طريق استبدال النموذج في سكريبتات التدريب المقدمة.
> يتطلب الضبط الدقيق الكامل ما لا يقل عن 32 جيجابايت من ذاكرة GPU و64 جيجابايت من ذاكرة الوصول العشوائي للنظام.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA و QLoRA ما لا يقل عن 16 جيجابايت من ذاكرة GPU و32 جيجابايت من ذاكرة الوصول العشوائي للنظام.
<!-- @device:end -->

## ما ستتعلمه

- كيفية ضبط نموذج LLM دقيقاً باستخدام LoRA و QLoRA والضبط الدقيق الكامل مع PyTorch و ROCm
- كيفية حفظ ونشر نموذجك المضبوط دقيقاً
- كيفية مراقبة التدريب وتصحيح المشكلات الشائعة

## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتاً، يمكنك تثبيته من خلال AMD Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

#### إنشاء بيئة افتراضية

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
**منح مستخدمك صلاحية الوصول إلى أجهزة GPU** (سجّل الخروج وأعد تسجيل الدخول لتفعيل هذا الإعداد):

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

#### تثبيت التبعيات الأساسية
<!-- @require:pytorch -->

#### تبعيات إضافية

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** يتم اختبار الحزم الأساسية فقط ودعمها هنا. **bitsandbytes غير مدعوم بشكل جيد على Windows**، لذا يستثني تثبيت Windows هذه الحزمة؛ استخدم LoRA أو الضبط الدقيق الكامل على Windows (يتطلب QLoRA حزمة bitsandbytes وهو مخصص لنظام Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### تفعيل مصادقة HF (النماذج المقيّدة أو المخصصة / غير المثبتة مسبقاً)

في هذا المثال نستخدم **google/gemma-3-4b-it**، وهو نموذج **مقيّد**. يجب عليك قبول شروط النموذج على Hugging Face ثم المصادقة حتى تتمكن سكريبتات التدريب من تنزيله.

1. **قبول الترخيص:** افتح [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)، سجّل الدخول (أو أنشئ حساباً)، واقبل الترخيص/الشروط في صفحة النموذج (مثل "Agree and access repository").
2. **التثبيت وتسجيل الدخول:** ثبّت واجهة سطر أوامر Hugging Face، ثم نفّذ تسجيل الدخول القياسي:

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

## فهم التقنيات

### ما هو LoRA؟

**LoRA (التكيّف منخفض الرتبة)** يُبقي النموذج الأساسي مجمّداً ويدرّب فقط مصفوفات "محوّل" صغيرة تُضاف إلى طبقات معينة.

- **الفكرة الأساسية**: بدلاً من تحديث مصفوفة أوزان ضخمة تحتوي على ملايين المعاملات، نتعلم تحديثاً منخفض الرتبة (مصفوفتان صغيرتان حاصل ضربهما يحتوي على معاملات أقل بكثير). يمنح ذلك تخفيضاً كبيراً في المعاملات القابلة للتدريب وذاكرة VRAM مع الحفاظ على معظم جودة الضبط الدقيق الكامل.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### ما هو QLoRA؟

**QLoRA** يجمع بين **التكميم رباعي البت** و**LoRA**. يُحمَّل النموذج الأساسي بتكميم 4 بت (توفير كبير في الذاكرة)، وتُدرَّب محوّلات LoRA فقط بدقة أعلى. وبذلك تحصل على كفاءة المعاملات من LoRA مع ذاكرة VRAM أقل بكثير، مع مقايضة طفيفة في الجودة مقارنةً بـ LoRA بدقة كاملة. لاحظ أن التكميم رباعي البت قد يسبب عدم استقرار عددي (ارتفاعات في الخسارة أو قيم NaN)، لذا قد يفضّل المستخدمون في الغالب **LoRA** إذا كانت ذاكرة VRAM كافية.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **ملاحظة**: بالنسبة للنماذج الأساسية MXFP4 مثل `openai/gpt-oss-20b`، نوصي باستخدام **LoRA** (`train_lora.py`) بدلاً من QLoRA. عادةً ما يُلغي مسار `bitsandbytes` رباعي البت في سكريبت QLoRA تكميم أوزان MXFP4 إلى BF16، لذا يتصرف التشغيل كـ LoRA قياسي. يتطلب MXFP4 الأصلي بناء `bitsandbytes` من المصدر مع مجموعة Transformers/Triton/kernels المتوافقة. راجع [وثائق Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. اختر طريقتك

| الطريقة | الذاكرة | السرعة | الجودة | الأنسب لـ |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux فقط) | 12-16 جيجابايت | الأسرع | 90-95% | استخدام ذاكرة منخفض |
| **LoRA** | 24-32 جيجابايت | سريع | 95-98% | نهج متوازن |
| **كامل** | 80 جيجابايت+ | الأبطأ | 100% | أقصى جودة |

### 3. تشغيل التدريب

**مجموعة البيانات وما يتعلمه النموذج**  
تحوّل السكريبتات مجموعة البيانات إلى أمثلة محادثة. على سبيل المثال، يستخدم سكريبت QLoRA **Abirate/english_quotes**: يصبح كل مثال زوجاً من المستخدم والمساعد كالتالي:

- **المستخدم:** "أعطني اقتباساً عن: &lt;tag&gt;"
- **المساعد:** "&lt;quote&gt; – &lt;author&gt;"

يعلّم الضبط الدقيق النموذجَ الاستجابةَ للمطالبات التي تطلب اقتباسات حول موضوع ما وإعادتها بالتنسيق `<quote text> - <author>`. تستخدم سكريبتا LoRA والضبط الدقيق الكامل **databricks/databricks-dolly-15k** (أزواج تعليمات/استجابات عامة)، لذا تتفاوت المهمة الدقيقة حسب السكريبت؛ الفكرة واحدة - تكييف النموذج مع مجموعة البيانات والتنسيق الذي اخترته.

فيما يلي ملخص لطرق التدريب المتاحة. كل طريقة مرتبطة بسكريبتها وتوفر وصفاً موجزاً لاختيار النهج المناسب.

| السكريبت | الطريقة | الوصف | ذاكرة VRAM النموذجية | موصى به لـ |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | يدرّب مصفوفات محوّل صغيرة مع تجميد النموذج الأساسي. أسرع بـ 3-5 مرات؛ جودة ~95-98% من الكاملة. | 24-32 جيجابايت | المستخدمون المتقدمون؛ محوّلات متعددة؛ ذاكرة VRAM أكبر |
| [`train_qlora.py`](assets/train_qlora.py) *(Linux فقط)* | **QLoRA** | تكميم 4 بت + محوّلات LoRA. أقل استخدام للذاكرة، الأسرع، مقايضة طفيفة في الجودة. يتطلب `bitsandbytes` (Linux فقط). | 12-16 جيجابايت | معظم المستخدمين؛ تجارب سريعة؛ ذاكرة VRAM محدودة |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **الضبط الدقيق الكامل** | يحدّث جميع معاملات النموذج. أقصى جودة؛ أعلى استخدام للذاكرة والحوسبة. | 40 جيجابايت+ | أقصى جودة؛ البحث؛ ذاكرة VRAM كبيرة |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64 جيجابايت من ذاكرة الوصول العشوائي للنظام وقد لا يكون ممكناً على هذا الجهاز. فكّر في استخدام LoRA أو QLoRA بدلاً من ذلك.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64 جيجابايت من ذاكرة الوصول العشوائي للنظام وقد لا يكون ممكناً على هذا الجهاز. فكّر في استخدام LoRA بدلاً من ذلك.
<!-- @os:end -->
<!-- @device:end -->

ببساطة اختر `طريقة التدريب` المفضلة لديك، نزّل السكريبت المقابل ونفّذه باستخدام الأمر مع إبقاء بيئتك الافتراضية مفعّلة:

```python
python3 train_<method_name>.py.
```

## استخدام نموذجك المضبوط دقيقاً

### بعد الضبط الدقيق الكامل

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

### بعد تدريب LoRA/QLoRA

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

### دمج محوّل LoRA في النموذج الأساسي

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**ملاحظة:**  
- تأكد من أن اسم مجلد النموذج (`output-gemma-3-4b-full`، `output-gemma-3-4b-qlora`) يطابق مجلد الإخراج الفعلي من التدريب.  
- إذا استخدمت LoRA بدلاً من QLoRA، فاستبدل المسار وفقاً لذلك.  
- تتطلب بعض نماذج Gemma تحديد `trust_remote_code=True` في `from_pretrained`؛ أضفها إذا رأيت تحذيراً ذا صلة.

لمزيد من الإعدادات المخصصة (رموز الحشو، الجهاز، إلخ)، راجع السكريبت الذي استخدمته للتدريب.

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

## دليل التخصيص

### استخدام مجموعة بياناتك الخاصة

تستخدم جميع السكريبتات نفس تنسيق مجموعة البيانات. استبدل قسم التحميل:

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

**تنسيق مجموعة البيانات لملف JSON/JSONL محلي:**

عند استخدام هذه الطريقة، يرجى التأكد من أن ملفات JSON منظمة بشكل صحيح لتجنب أخطاء التحليل.

يجب الالتزام بالإرشادات التالية:
* **تنسيق الملف:** يجب تنسيق ملفات JSON داخل بيئة تطوير متكاملة (IDE) لضمان البنية والصياغة الصحيحة.
* **المفاتيح المطلوبة:** يجب أن يحتوي ملف JSON المخصص على المفاتيح `instruction` و`response`. هذه المفاتيح ضرورية لعمل الطريقة بشكل صحيح.
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
**تنسيق مجموعة البيانات لمجموعة بيانات Hugging Face Hub**

عند استخدام مجموعات البيانات من Hugging Face، يرجى التأكد من أن مجموعات بياناتك منظمة بشكل صحيح لتسهيل التكامل السلس.

يجب اتباع الإرشادات التالية:
* **زوج التعليمات والاستجابة:** ركّز على مجموعات البيانات التي تتضمن زوج `instruction-response`. هذه البنية ضرورية للوظيفة المقصودة.
* **تعديل المفاتيح المخصصة:** إذا كانت مجموعة بياناتك لا تتوافق مع بنية `instruction-response`، يمكنك تعديل دالة `format_instruction()`. يتيح لك ذلك استيعاب مفاتيح محددة حسب الحاجة.

مثال على التعديل: في الحالات التي يحتاج فيها إخراج مجموعة البيانات إلى تعديل، يمكنك تعديل قسم الاستجابة داخل دالة format_instruction() لتناسب متطلباتك.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**تنسيق مجموعة البيانات لملف CSV**

لاستيعاب السكريبت باستخدام تنسيق ملف CSV، تحتاج إلى التأكد من أن ملف CSV يحتوي على أعمدة باسم `instruction` و`response`.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ضبط معاملات التدريب

عدّل سكريبت التدريب وغيّر المتغيرات لتتوافق مع أهدافك: **معدل التعلم** (`LR`)، **الحقب** (`EPOCHS`)، **حجم الدفعة** (`BATCH_SIZE`)، **تراكم التدرج** (`GRAD_ACCUM_STEPS`)، وبالنسبة لـ LoRA/QLoRA **الرتبة** (`LORA_R`). للحصول على تشغيلات أسرع استخدم حقباً أقل ومعدل تعلم أعلى (LR)؛ وللحصول على جودة أفضل استخدم حقباً أكثر ومعدل LR أقل. قلّل حجم الدفعة أو طول التسلسل إذا واجهت أخطاء نفاد الذاكرة.

### نصائح تحسين الذاكرة

إذا واجهت أخطاء نفاد الذاكرة:

**1. تقليل حجم الدفعة:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. تقليل طول التسلسل:**
```python
max_seq_length=256  # Instead of 512
```

**3. استخدام تكميم أكثر قوة:**
```
Full → LoRA → QLoRA
```

**4. تفعيل نقاط تفتيش التدرج (الضبط الدقيق الكامل فقط):**
```python
model.gradient_checkpointing_enable()
```

---

## المراقبة والتصحيح

### مراقبة ذاكرة GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (اختياري) تتبع التجارب مع Weights & Biases

لتسجيل التشغيلات والمقاييس في [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

في سكريبت التدريب، اضبط `report_to="wandb"` واختيارياً `run_name="your-experiment-name"` في تهيئة المدرّب. إذا كنت تفضّل عدم استخدام Wandb، اترك `report_to` عند قيمته الافتراضية أو اضبطه على `"none"`.

### المشكلات الشائعة

#### نفاد الذاكرة (OOM)

**الحل:** قلّل حجم الدفعة و/أو استخدم QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### الخسارة لا تتناقص

**الحل:** اضبط معدل التعلم
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### بطء التدريب

**الحل:** زد حجم الدفعة إذا سمحت الذاكرة بذلك
```python
BATCH_SIZE = 8
```
## الخطوات التالية

بعد إتمام الضبط الدقيق بنجاح، فكّر في الخطوات التالية للاستفادة أكثر من نموذجك:

1. **التقييم** بشكل شامل على بيانات اختبار محجوزة لقياس التعميم وتجنب الإفراط في التخصيص.
2. **التجريب** بتجربة قيم مختلفة للمعاملات الفائقة للحصول على توازن أفضل بين الدقة والسرعة والذاكرة.
3. **التتبع** لجميع تجاربك (والمقاييس المقابلة) باستخدام Weights & Biases للبحث القابل للاستنساخ.
4. **التجربة** بالتدريب على مجموعات بياناتك المخصصة لتكييف النموذج تحديداً لحالة استخدامك.
5. **النشر** لنموذجك المضبوط دقيقاً للاستدلال السريع باستخدام خلفيات فعّالة مثل vLLM على الأجهزة المتوافقة.
6. **استكشاف** التقنيات المتقدمة بما في ذلك هندسة المطالبات والدقة المختلطة وأطوال التسلسل الأطول.
7. **تدريب** محوّلات LoRA متعددة لمهام أو مجالات مختلفة والتبديل بينها حسب الحاجة.

---