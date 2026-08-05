<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

يقدم هذا البرنامج التعليمي أمثلة خطوة بخطوة لضبط نموذج لغوي كبير (LLM) باستخدام PyTorch و ROCm. ويغطي عدة تقنيات، من الضبط الدقيق القياسي إلى استراتيجيات الضبط الدقيق الفعّالة من حيث الذاكرة والمعاملات (PEFT)، حتى تتمكن من تكييف النماذج بسهولة وفقًا لاحتياجاتك.

**النموذج المستخدم**: google/gemma-3-4b-it  *(راجع [تفعيل مصادقة HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) إذا كان النموذج مقيّدًا)*  
**العتاد**: بطاقة رسومات AMD Radeon™ مع دعم ROCm  
**إطار العمل**: PyTorch + Hugging Face (Transformers، PEFT، Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **ملاحظة:** 
> - يتطلب الضبط الدقيق الكامل ما لا يقل عن **64 جيجابايت من ذاكرة النظام (RAM)**، مع توفر ما لا يقل عن **32 جيجابايت منها لبطاقة الرسومات** (الـ 32 جيجابايت جزء من الـ 64 جيجابايت، وليست إضافة عليها).
> - يمكنك أيضًا تجربة معماريات نماذج أخرى، بما في ذلك **GPT-OSS-20B**، عن طريق استبدال النموذج في نصوص التدريب البرمجية المتوفرة.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA و QLoRA ما لا يقل عن **32 جيجابايت من ذاكرة النظام (RAM)**، مع توفر ما لا يقل عن **16 جيجابايت منها لبطاقة الرسومات** (الـ 16 جيجابايت جزء من الـ 32 جيجابايت، وليست إضافة عليها).
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA ما لا يقل عن **32 جيجابايت من ذاكرة النظام (RAM)**، مع توفر ما لا يقل عن **16 جيجابايت منها لبطاقة الرسومات** (الـ 16 جيجابايت جزء من الـ 32 جيجابايت، وليست إضافة عليها).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA و QLoRA بطاقة رسومات بها ما لا يقل عن **16 جيجابايت من ذاكرة GPU المخصصة** و **32 جيجابايت من ذاكرة النظام (RAM)**.
> - على Linux، يتم تشغيل التدريب بالكامل ضمن ذاكرة VRAM المخصصة لبطاقة الرسومات.
> - ولا يتم اللجوء إلى ذاكرة GPU المشتركة (ذاكرة النظام) عند نفاد VRAM.
> - البطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة ستنفد ذاكرتها أثناء التدريب على Linux، حتى لو كان النظام يحتوي على كمية وفيرة من ذاكرة RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA ما لا يقل عن **16 جيجابايت من إجمالي ذاكرة GPU** و **32 جيجابايت من ذاكرة النظام (RAM)**.
> - على Windows، تجمع ذاكرة GPU الإجمالية بين VRAM المخصصة لبطاقة الرسومات وذاكرة GPU المشتركة (المستعارة من ذاكرة النظام).
> - لذلك، يمكن للبطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة أن تشغّل هذا الدليل الإرشادي مع ذلك باستخدام ذاكرة GPU المشتركة لتعويض الفرق.
<!-- @os:end -->
<!-- @device:end -->

## ما ستتعلمه

- كيفية ضبط نموذج لغوي كبير (LLM) باستخدام LoRA و QLoRA والضبط الدقيق الكامل مع PyTorch و ROCm
- كيفية حفظ النموذج المضبوط ونشره
- كيفية مراقبة التدريب واستكشاف المشكلات الشائعة وإصلاحها

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته من Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرمجيات الأساسية

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
**امنح المستخدم الخاص بك صلاحية الوصول إلى أجهزة GPU** (سجّل الخروج ثم الدخول مجددًا حتى يسري هذا التغيير):

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
**Windows:** يتم اختبار الحزم الأساسية فقط ودعمها هنا. **bitsandbytes غير مدعوم جيدًا على Windows**، لذا يستبعده تثبيت Windows؛ استخدم LoRA أو الضبط الدقيق الكامل على Windows (يتطلب QLoRA حزمة bitsandbytes وهو مخصص لنظام Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### تفعيل مصادقة HF (النماذج المقيّدة أو المخصصة / غير المثبّتة مسبقًا)

في هذا المثال نستخدم **google/gemma-3-4b-it**، وهو نموذج **مقيّد**. يجب عليك قبول شروط النموذج على Hugging Face ثم المصادقة حتى تتمكن نصوص التدريب البرمجية من تنزيله.

1. **قبول الترخيص:** افتح [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)، وسجّل الدخول (أو أنشئ حسابًا)، ثم اقبل الترخيص/الشروط في صفحة النموذج (على سبيل المثال "Agree and access repository").
2. **التثبيت وتسجيل الدخول:** ثبّت واجهة سطر الأوامر الخاصة بـ Hugging Face، ثم شغّل تسجيل الدخول المعتاد:

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

**LoRA (Low-Rank Adaptation)** يبقي النموذج الأساسي مجمّدًا ويقوم فقط بتدريب مصفوفات "مهايئة" (adapter) صغيرة تُضاف إلى طبقات معينة. 

- **الفكرة الأساسية**: بدلاً من تحديث مصفوفة أوزان ضخمة تحتوي على ملايين المعاملات، نتعلم تحديثًا منخفض الرتبة (مصفوفتان صغيرتان يكون حاصل ضربهما أقل بكثير من حيث عدد المعاملات). وهذا يمنح انخفاضًا كبيرًا في عدد المعاملات القابلة للتدريب وفي استهلاك VRAM، مع الحفاظ على معظم جودة الضبط الدقيق الكامل.

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

يجمع **QLoRA** بين **التكميم رباعي البت (4-bit quantization)** و **LoRA**. يتم تحميل النموذج الأساسي بدقة 4 بت (توفير كبير في الذاكرة)، ولا يتم تدريب سوى مهايئات LoRA بدقة أعلى. وبذلك تحصل على كفاءة معاملات LoRA بالإضافة إلى استهلاك أقل بكثير لذاكرة VRAM، مع مقايضة طفيفة في الجودة مقارنة بـ LoRA بالدقة الكاملة. لاحظ أن التكميم رباعي البت قد يسبب عدم استقرار عددي (ارتفاعات مفاجئة في الخسارة أو قيم NaN)، لذا قد يفضل المستخدمون غالبًا استخدام **LoRA** إذا كانت ذاكرة VRAM المتاحة كافية.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **ملاحظة**: بالنسبة للنماذج الأساسية من نوع MXFP4 مثل `openai/gpt-oss-20b`، نوصي باستخدام **LoRA** (`train_lora.py`) بدلاً من QLoRA. عادةً ما يقوم مسار 4-بت الخاص بـ `bitsandbytes` في نص QLoRA البرمجي بإلغاء تكميم أوزان MXFP4 إلى BF16، بحيث تتصرف عملية التشغيل مثل LoRA القياسي. يتطلب MXFP4 الأصلي بناء `bitsandbytes` من المصدر بالإضافة إلى حزمة متوافقة من Transformers/Triton/kernels. راجع [وثائق MXFP4 الخاصة بـ Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. اختر الطريقة

| الطريقة | الذاكرة | السرعة | الجودة | الأنسب لـ |
|--------|--------|-------|---------|----------|
| **QLoRA** (لينكس فقط) | 12-16GB | الأسرع | 90-95% | استخدام ذاكرة منخفض |
| **LoRA** | 24-32GB | سريع | 95-98% | نهج متوازن |
| **Full** | 80GB+ | الأبطأ | 100% | أقصى جودة |

### 3. تشغيل التدريب

**مجموعة البيانات وما يتعلمه النموذج**  
تحوّل السكربتات مجموعة البيانات إلى أمثلة محادثة. على سبيل المثال، يستخدم سكربت QLoRA مجموعة **Abirate/english_quotes**: يصبح كل مثال زوجًا من المستخدم والمساعد على النحو التالي:

- **المستخدم:** "أعطني اقتباسًا عن: &lt;tag&gt;"
- **المساعد:** "&lt;quote&gt; – &lt;author&gt;"

يعلّم الضبط الدقيق النموذج الاستجابة للطلبات التي تطلب اقتباسات حول موضوع ما وإرجاعها بالتنسيق `<quote text> - <author>`. تستخدم سكربتات LoRA والضبط الدقيق الكامل مجموعة **databricks/databricks-dolly-15k** (أزواج تعليمات/استجابات عامة)، لذا تختلف المهمة الدقيقة حسب السكربت؛ لكن الفكرة واحدة - تكييف النموذج مع مجموعة البيانات والتنسيق الذي تختاره.

فيما يلي ملخص لطرق التدريب المتاحة. كل طريقة ترتبط بسكربتها وتوفر وصفًا موجزًا لاختيار النهج الصحيح.

| السكربت                           | الطريقة            | الوصف                                                                                                         | ذاكرة الفيديو النموذجية | موصى به لـ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | يدرّب مصفوفات محول صغيرة مع تجميد النموذج الأساسي. أسرع بـ 3-5 أضعاف؛ ~95-98% من الجودة الكاملة.                         | 24–32GB      | المستخدمون المتقدمون؛ محولات متعددة؛ ذاكرة فيديو أكبر    |
| [`train_qlora.py`](assets/train_qlora.py)  *(لينكس فقط)*             | **QLoRA**       | تكميم 4-بت + محولات LoRA. أقل استخدام للذاكرة، الأسرع، مقايضة بسيطة في الجودة. يتطلب `bitsandbytes` (لينكس فقط).                            | 12–16GB      | معظم المستخدمين؛ تجارب سريعة؛ ذاكرة فيديو محدودة      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **الضبط الدقيق الكامل** | يحدّث جميع معلمات النموذج. أقصى جودة؛ أعلى استخدام للذاكرة والحوسبة.                                    | 40GB+        | أقصى جودة؛ البحث؛ ذاكرة فيديو كبيرة           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64GB من ذاكرة النظام (RAM) وقد لا يكون ممكنًا على هذا الجهاز. فكّر في استخدام LoRA أو QLoRA بدلاً من ذلك.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64GB من ذاكرة النظام (RAM) وقد لا يكون ممكنًا على هذا الجهاز. فكّر في استخدام LoRA بدلاً من ذلك.
<!-- @os:end -->
<!-- @device:end -->

ببساطة، اختر `Training method` الذي تفضّله، وقم بتنزيل السكربت المطابق ونفّذه باستخدام الأمر مع إبقاء بيئتك الافتراضية مفعّلة: 

```python
python3 train_<method_name>.py.
```

## استخدام نموذجك المضبوط دقيقًا

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

### دمج محول LoRA في النموذج الأساسي

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**ملاحظة:**  
- تأكد من أن اسم دليل النموذج (`output-gemma-3-4b-full`، `output-gemma-3-4b-qlora`) يطابق مجلد الإخراج الفعلي من التدريب.  
- إذا استخدمت LoRA بدلاً من QLoRA، فقط استبدل المسار وفقًا لذلك.  
- تتطلب بعض نماذج Gemma تحديد `trust_remote_code=True` في `from_pretrained`؛ أضفه إذا رأيت تحذيرًا متعلقًا بذلك.

للحصول على المزيد من الإعدادات المخصصة (رموز الحشو، الجهاز، إلخ)، راجع السكربت الذي استخدمته للتدريب.

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

تستخدم جميع السكربتات نفس تنسيق مجموعة البيانات. استبدل قسم التحميل:

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

عند استخدام هذه الطريقة، يرجى التأكد من أن ملفات JSON الخاصة بك مُنظّمة بشكل صحيح لتجنب أخطاء التحليل. 

يجب الالتزام بالإرشادات التالية:
* **تنسيق الملف:** يجب تنسيق ملفات JSON داخل بيئة تطوير متكاملة (IDE) لضمان البنية والصياغة الصحيحة.
* **المفاتيح المطلوبة:** يجب أن يحتوي ملف JSON المخصص على المفتاحين `instruction` و`response`. هذان المفتاحان أساسيان لعمل الطريقة بشكل صحيح.
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
**تنسيق مجموعة البيانات لمجموعة بيانات من Hugging Face Hub**

عند استخدام مجموعات بيانات من Hugging Face، يرجى التأكد من أن مجموعات بياناتك منظمة بشكل صحيح لتسهيل التكامل السلس. 

يجب اتباع الإرشادات التالية:
* **زوج التعليمات-الاستجابة:** ركّز على مجموعات البيانات التي تتضمن زوج `instruction-response`. هذه البنية أساسية للوظيفة المقصودة.
* **تعديل المفتاح المخصص:** إذا كانت مجموعة بياناتك لا تتوافق مع بنية `instruction-response`، فلديك خيار تعديل الدالة `format_instruction()`. يتيح لك هذا استيعاب مفاتيح محددة حسب الحاجة.

مثال على التعديل: في الحالات التي يحتاج فيها ناتج مجموعة البيانات إلى تعديل، يمكنك تعديل قسم الاستجابة داخل الدالة format_instruction() ليتناسب مع متطلباتك.
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

لاستيعاب السكربت باستخدام تنسيق ملف CSV، تحتاج إلى التأكد من أن ملف CSV يحتوي على أعمدة باسم `instruction` و`response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ضبط معلمات التدريب

عدّل سكربت التدريب وغيّر المتغيرات لتتناسب مع أهدافك: **معدل التعلم** (`LR`)، و**عدد الحقب** (`EPOCHS`)، و**حجم الدفعة** (`BATCH_SIZE`)، و**تراكم التدرج** (`GRAD_ACCUM_STEPS`)، وبالنسبة لـ LoRA/QLoRA **الرتبة** (`LORA_R`). للحصول على تشغيلات أسرع، استخدم عددًا أقل من الحقب ومعدل تعلم أعلى (LR)؛ وللحصول على جودة أفضل، استخدم المزيد من الحقب ومعدل تعلم أقل. قلّل حجم الدفعة أو طول التسلسل إذا واجهت أخطاء نفاد الذاكرة.
### نصائح لتحسين استخدام الذاكرة

إذا واجهت أخطاء نفاد الذاكرة:

**1. تقليل حجم الدفعة (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. تقليل طول التسلسل:**
```python
max_seq_length=256  # Instead of 512
```

**3. استخدام تكميم (Quantization) أكثر صرامة:**
```
Full → LoRA → QLoRA
```

**4. تفعيل نقاط التحقق التدرجية (Gradient Checkpointing) (للضبط الدقيق الكامل فقط):**
```python
model.gradient_checkpointing_enable()
```

---

## المراقبة واستكشاف الأخطاء وإصلاحها

### مراقبة ذاكرة GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (اختياري) تتبع التجارب باستخدام Weights & Biases

لتسجيل عمليات التشغيل والمقاييس على [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

في نص التدريب البرمجي، اضبط `report_to="wandb"` واختياريًا `run_name="your-experiment-name"` في إعدادات المدرّب (trainer). إذا كنت تفضل عدم استخدام Wandb، اترك `report_to` على قيمته الافتراضية أو اضبطها على `"none"`.

### المشكلات الشائعة

#### نفاد الذاكرة (OOM)

**الحل:** تقليل حجم الدفعة (Batch Size) و/أو استخدام QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### عدم انخفاض الخسارة (Loss)

**الحل:** ضبط معدل التعلم (Learning Rate)
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### بطء التدريب

**الحل:** زيادة حجم الدفعة (Batch Size) إذا سمحت الذاكرة بذلك
```python
BATCH_SIZE = 8
```
## الخطوات التالية

بعد إتمام الضبط الدقيق بنجاح، ضع في اعتبارك الخطوات التالية للاستفادة أكثر من نموذجك:

1. **قيّم** النموذج بدقة على بيانات اختبار محجوزة لقياس التعميم وتجنب الإفراط في التخصيص (Overfitting).
2. **جرّب** قيمًا مختلفة للمعاملات الفائقة (Hyperparameters) للحصول على توازن أفضل بين الدقة والسرعة واستخدام الذاكرة.
3. **تتبّع** جميع تجاربك (والمقاييس المرتبطة بها) باستخدام Weights & Biases من أجل بحث قابل لإعادة الإنتاج.
4. **جرّب** التدريب على مجموعات بيانات مخصصة خاصة بك لتكييف النموذج تحديدًا مع حالة استخدامك.
5. **انشر** نموذجك المضبوط دقيقًا للحصول على استدلال سريع باستخدام محركات فعّالة مثل vLLM على الأجهزة المتوافقة.
6. **استكشف** التقنيات المتقدمة بما في ذلك هندسة المطالبات (Prompt Engineering)، والدقة المختلطة (Mixed Precision)، وأطوال التسلسل الأطول.
7. **درّب** محولات LoRA متعددة لمهام أو مجالات مختلفة وقم بتبديلها حسب الحاجة.

---