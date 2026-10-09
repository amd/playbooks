<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

يقدم هذا الدليل التعليمي أمثلة تفصيلية خطوة بخطوة لضبط نموذج لغوي كبير (LLM) باستخدام PyTorch وROCm. ويغطي عدة تقنيات، بدءًا من الضبط الدقيق القياسي وصولًا إلى استراتيجيات الضبط الدقيق الفعّالة من حيث استخدام المعلمات (Parameter-Efficient Fine-Tuning - PEFT) الموفّرة للذاكرة، بحيث يمكنك تكييف النماذج بسهولة وفق احتياجاتك.

**النموذج المستخدم**: google/gemma-3-4b-it (سكربت QLoRA: openai/gpt-oss-20b)  *(راجع [تفعيل مصادقة HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) إن كان النموذج مقيدًا)*  
**العتاد**: وحدة معالجة رسومية AMD Radeon™ مدعومة بتقنية ROCm  
**إطار العمل**: PyTorch وHugging Face (Transformers وPEFT وTransformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **ملاحظة:** 
> - يتطلب الضبط الدقيق الكامل ما لا يقل عن **64 جيجابايت من ذاكرة الوصول العشوائي للنظام**، على أن يكون ما لا يقل عن **32 جيجابايت منها متاحًا لوحدة معالجة الرسومات** (هذه الـ32 جيجابايت جزء من الـ64 جيجابايت، وليست إضافة إليها).
> - يمكنك أيضًا تجربة بنى نماذج أخرى، بما في ذلك **GPT-OSS-20B**، باستبدال النموذج في سكربتات التدريب المقدَّمة.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA وQLoRA ما لا يقل عن **32 جيجابايت من ذاكرة الوصول العشوائي للنظام**، على أن يكون ما لا يقل عن **16 جيجابايت منها متاحًا لوحدة معالجة الرسومات** (هذه الـ16 جيجابايت جزء من الـ32 جيجابايت، وليست إضافة إليها).
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA ما لا يقل عن **32 جيجابايت من ذاكرة الوصول العشوائي للنظام**، على أن يكون ما لا يقل عن **16 جيجابايت منها متاحًا لوحدة معالجة الرسومات** (هذه الـ16 جيجابايت جزء من الـ32 جيجابايت، وليست إضافة إليها).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA وQLoRA بطاقة رسومات بسعة لا تقل عن **16 جيجابايت من ذاكرة GPU المخصصة** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - على أنظمة Linux، يتم التدريب بالكامل في ذاكرة VRAM المخصصة لبطاقة الرسومات.
> - لا يعود النظام إلى استخدام ذاكرة GPU المشتركة (ذاكرة الوصول العشوائي للنظام) عند نفاد VRAM.
> - ستنفد ذاكرة البطاقات التي تقل سعتها عن 16 جيجابايت من VRAM المخصصة أثناء التدريب على Linux، حتى لو توفرت كمية كبيرة من ذاكرة الوصول العشوائي في النظام.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA ما لا يقل عن **16 جيجابايت من إجمالي ذاكرة GPU** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - على أنظمة Windows، يجمع إجمالي ذاكرة GPU بين ذاكرة VRAM المخصصة لبطاقة الرسومات وذاكرة GPU المشتركة (المقتطعة من ذاكرة الوصول العشوائي للنظام).
> - لذلك، يمكن للبطاقات التي تقل سعتها عن 16 جيجابايت من VRAM المخصصة تشغيل هذا الدليل عبر استخدام ذاكرة GPU المشتركة لتعويض الفرق.
<!-- @os:end -->
<!-- @device:end -->

## ما الذي ستتعلمه

- كيفية ضبط نموذج لغوي كبير باستخدام LoRA وQLoRA والضبط الدقيق الكامل مع PyTorch وROCm
- كيفية حفظ ونشر النموذج المضبوط لديك
- كيفية مراقبة التدريب وتصحيح المشكلات الشائعة

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته عبر Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

#### إنشاء بيئة افتراضية

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
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (سجّل الخروج ثم الدخول مجددًا ليصبح هذا نافذ المفعول):

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

#### تثبيت التبعيات الأساسية
<!-- @require:pytorch -->

#### تبعيات إضافية

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** يتم اختبار الحزم الأساسية فقط ودعمها هنا. **مكتبة bitsandbytes غير مدعومة جيدًا على Windows**، لذا يتم استبعادها من التثبيت على Windows؛ استخدم LoRA أو الضبط الدقيق الكامل على Windows (يتطلب QLoRA مكتبة bitsandbytes وهو مخصص لنظام Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### تفعيل مصادقة HF (النماذج المقيدة أو المخصصة / غير المثبتة مسبقًا)

في هذا المثال نستخدم **google/gemma-3-4b-it**، وهو نموذج **مقيد**. يجب عليك قبول شروط النموذج على Hugging Face ثم المصادقة ليتمكن سكربت التدريب من تنزيله.

1. **قبول الترخيص:** افتح [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)، وسجّل الدخول (أو أنشئ حسابًا)، واقبل الترخيص/الشروط في صفحة النموذج (مثل خيار "Agree and access repository").
2. **التثبيت وتسجيل الدخول:** ثبّت واجهة سطر الأوامر الخاصة بـHugging Face، ثم نفّذ تسجيل الدخول القياسي:

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

تُبقي تقنية **LoRA (Low-Rank Adaptation)** النموذج الأساسي مجمدًا وتقوم فقط بتدريب مصفوفات "محوّل" صغيرة تُضاف إلى طبقات معينة. 

- **الفكرة الأساسية**: بدلًا من تحديث مصفوفة أوزان ضخمة بملايين المعلمات، نتعلم تحديثًا منخفض الرتبة (مصفوفتان صغيرتان يكون ناتج ضربهما أقل بكثير من حيث عدد المعلمات). وهذا يحقق انخفاضًا كبيرًا في عدد المعلمات القابلة للتدريب وفي استهلاك VRAM مع الحفاظ على معظم جودة الضبط الدقيق الكامل.

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

تجمع تقنية **QLoRA** بين **التكميم بـ4 بت** و**LoRA**. يتم تحميل النموذج الأساسي بتنسيق 4 بت (توفير كبير في الذاكرة)، ويتم تدريب محوّلات LoRA فقط بدقة أعلى. وبذلك تحصل على كفاءة معلمات LoRA إلى جانب استهلاك أقل بكثير لذاكرة VRAM، مع تنازل بسيط في الجودة مقارنة بـLoRA بدقة كاملة. يُلاحظ أن التكميم بـ4 بت قد يسبب عدم استقرار رقمي (ارتفاعات مفاجئة في قيمة الخسارة أو قيم NaN)، لذا قد يفضل المستخدمون غالبًا استخدام **LoRA** إذا توفرت ذاكرة VRAM كافية.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **ملاحظة**: بالنسبة للنماذج الأساسية من نوع MXFP4 مثل `openai/gpt-oss-20b`، نوصي باستخدام **LoRA** (`train_lora.py`) بدلًا من QLoRA. فمسار 4 بت الخاص بمكتبة `bitsandbytes` في سكربت QLoRA عادةً ما يقوم بإلغاء تكميم أوزان MXFP4 إلى BF16، مما يجعل التشغيل يتصرف كـLoRA قياسي. أما دعم MXFP4 الأصلي فيتطلب بناء `bitsandbytes` من المصدر مع حزمة متوافقة من Transformers/Triton/kernels. راجع [وثائق Transformers الخاصة بـMXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. اختر الطريقة

| الطريقة | الذاكرة | السرعة | الجودة | الأفضل لـ |
|--------|--------|-------|---------|----------|
| **QLoRA** (لينكس فقط) | 12-16GB | الأسرع | 90-95% | استخدام ذاكرة منخفض |
| **LoRA** | 24-32GB | سريع | 95-98% | نهج متوازن |
| **Full** | 80GB+ | الأبطأ | 100% | أقصى جودة |

### 3. تشغيل التدريب

**مجموعة البيانات وما يتعلمه النموذج**  
تحوّل السكربتات مجموعة البيانات إلى أمثلة محادثة. فعلى سبيل المثال، يستخدم سكربت QLoRA مجموعة **Abirate/english_quotes**: يصبح كل مثال زوجًا من نوع مستخدم-مساعد كما يلي:

- **المستخدم:** "أعطني اقتباسًا عن: &lt;tag&gt;"
- **المساعد:** "&lt;quote&gt; – &lt;author&gt;"

يُعلّم الضبط الدقيق النموذج الاستجابة للطلبات التي تطلب اقتباسات حول موضوع معين وإعادتها بالصيغة `<quote text> - <author>`. تستخدم سكربتات LoRA والضبط الدقيق الكامل مجموعة **databricks/databricks-dolly-15k** (أزواج تعليمات/استجابات عامة)، لذا تختلف المهمة الدقيقة حسب السكربت؛ لكن الفكرة واحدة - تكييف النموذج مع مجموعة البيانات والصيغة التي تختارها.

فيما يلي ملخص لطرق التدريب المتاحة. يرتبط كل طريقة بسكربتها ويقدم وصفًا موجزًا لاختيار النهج المناسب.

| السكربت                           | الطريقة            | الوصف                                                                                                         | VRAM النموذجي | يُوصى به لـ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | يدرّب مصفوفات محول صغيرة مع تجميد النموذج الأساسي. أسرع بمقدار 3-5 أضعاف؛ ~95-98% من الجودة الكاملة.                         | 24–32GB      | المستخدمون المتقدمون؛ محولات متعددة؛ المزيد من VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(لينكس فقط)*             | **QLoRA**       | التكميم بـ 4-بت + محولات LoRA. أقل استخدام للذاكرة، الأسرع، مقايضة طفيفة في الجودة. يتطلب `bitsandbytes` (لينكس فقط).                            | 12–16GB      | معظم المستخدمين؛ التجارب السريعة؛ VRAM محدود      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **الضبط الدقيق الكامل** | يحدّث جميع معاملات النموذج. أقصى جودة؛ أعلى استخدام للذاكرة والحوسبة.                                    | 40GB+        | أقصى جودة؛ البحث؛ VRAM كبير           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64GB من ذاكرة النظام (RAM) وقد لا يكون ممكنًا على هذا الجهاز. ضع في اعتبارك استخدام LoRA أو QLoRA بدلاً من ذلك.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64GB من ذاكرة النظام (RAM) وقد لا يكون ممكنًا على هذا الجهاز. ضع في اعتبارك استخدام LoRA بدلاً من ذلك.
<!-- @os:end -->
<!-- @device:end -->

ببساطة، اختر `Training method` المفضلة لديك، ونزّل السكربت المقابل ونفّذه باستخدام الأمر مع إبقاء بيئتك الافتراضية مفعّلة: 

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
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

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
- تأكد من أن اسم مجلد النموذج (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) يطابق مجلد الإخراج الفعلي من التدريب.  
- إذا استخدمت LoRA بدلاً من QLoRA، فقط استبدل المسار وفقًا لذلك.  
- تتطلب بعض نماذج Gemma تحديد `trust_remote_code=True` في `from_pretrained`؛ أضفها إذا رأيت تحذيرًا متعلقًا بذلك.

لمزيد من الإعدادات المخصصة (رموز الحشو، الجهاز، إلخ)، راجع السكربت الذي استخدمته للتدريب.

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

## دليل التخصيص

### استخدام مجموعة البيانات الخاصة بك

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

عند استخدام هذه الطريقة، يُرجى التأكد من أن ملفات JSON الخاصة بك مُهيكلة بشكل صحيح لتجنب أخطاء التحليل. 

يجب الالتزام بالإرشادات التالية:
* **تنسيق الملف:** يجب تنسيق ملفات JSON داخل بيئة تطوير متكاملة (IDE) لضمان البنية والصياغة الصحيحة.
* **المفاتيح المطلوبة:** يجب أن يحتوي ملف JSON المخصص على المفتاحين `instruction` و `response`. هذان المفتاحان أساسيان لعمل الطريقة بشكل صحيح.
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

عند استخدام مجموعات بيانات من Hugging Face، يُرجى التأكد من أن مجموعات البيانات الخاصة بك مُهيكلة بشكل صحيح لتسهيل التكامل السلس. 

يجب اتباع الإرشادات التالية:
* **زوج التعليمات-الاستجابة:** ركّز على مجموعات البيانات التي تتضمن زوج `instruction-response`. هذه البنية أساسية للوظيفة المقصودة.
* **تعديل المفتاح المخصص:** إذا كانت مجموعة البيانات الخاصة بك لا تتوافق مع بنية `instruction-response`، فلديك خيار تعديل الدالة `format_instruction()`. يتيح لك ذلك استيعاب مفاتيح محددة حسب الحاجة.

مثال على التعديل: في الحالات التي يحتاج فيها إخراج مجموعة البيانات إلى تعديل، يمكنك تعديل قسم الاستجابة داخل الدالة format_instruction() لتناسب متطلباتك.
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

لاستيعاب السكربت باستخدام تنسيق ملف CSV، تحتاج إلى التأكد من أن ملف CSV يحتوي على أعمدة باسم `instruction` و `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ضبط معاملات التدريب

حرّر سكربت التدريب وغيّر المتغيرات لتناسب أهدافك: **معدل التعلم** (`LR`)، **عدد الدورات** (`EPOCHS`)، **حجم الدفعة** (`BATCH_SIZE`)، **تراكم التدرج** (`GRAD_ACCUM_STEPS`)، وبالنسبة لـ LoRA/QLoRA **الرتبة** (`LORA_R`). لتشغيلات أسرع، استخدم عددًا أقل من الدورات ومعدل تعلم أعلى (LR)؛ وللحصول على جودة أفضل، استخدم عددًا أكبر من الدورات ومعدل تعلم أقل. قلّل حجم الدفعة أو طول التسلسل إذا واجهت أخطاء نفاد الذاكرة.
### نصائح لتحسين استخدام الذاكرة

إذا واجهت أخطاء نفاد الذاكرة:

**1. تقليل حجم الدُفعة (Batch Size):**
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

### (اختياري) تتبّع التجارب باستخدام Weights & Biases

لتسجيل عمليات التشغيل والمقاييس إلى [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

في نص برنامج التدريب، اضبط `report_to="wandb"` واختياريًا `run_name="your-experiment-name"` في إعدادات المدرِّب (trainer). إذا كنت تفضل عدم استخدام Wandb، فاترك `report_to` على قيمته الافتراضية أو اضبطها على `"none"`.

### المشكلات الشائعة

#### نفاد الذاكرة (OOM)

**الحل:** تقليل حجم الدُفعة و/أو استخدام QLoRA
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

**الحل:** زيادة حجم الدُفعة إذا سمحت الذاكرة بذلك
```python
BATCH_SIZE = 8
```
## الخطوات التالية

بعد أن تُتم عملية ضبط دقيق ناجحة، ضع في اعتبارك الخطوات التالية للحصول على أقصى استفادة من نموذجك:

1. **التقييم** بدقة على بيانات اختبار مُستبعدة لقياس قدرة التعميم وتجنب الإفراط في التخصيص (Overfitting).
2. **التجريب** من خلال تجربة قيم مختلفة للمعاملات الفائقة (Hyperparameters) لتحقيق توازن أفضل بين الدقة والسرعة واستهلاك الذاكرة.
3. **التتبّع** لجميع تجاربك (والمقاييس المرتبطة بها) باستخدام Weights & Biases لضمان إمكانية إعادة إنتاج الأبحاث.
4. **المحاولة** بالتدريب على مجموعات بيانات مخصصة خاصة بك لتكييف النموذج خصيصًا مع حالة استخدامك.
5. **النشر** لنموذجك بعد ضبطه الدقيق لتحقيق استدلال سريع باستخدام خلفيات فعّالة مثل vLLM على الأجهزة المتوافقة.
6. **الاستكشاف** للتقنيات المتقدمة، بما في ذلك هندسة المُوجّهات (Prompt Engineering)، والدقة المختلطة (Mixed Precision)، وأطوال التسلسل الأطول.
7. **التدريب** لعدة محولات LoRA لمهام أو مجالات مختلفة وتبديلها حسب الحاجة.

---