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

يقدم هذا الدليل التعليمي أمثلة تفصيلية خطوة بخطوة لضبط نموذج لغوي كبير (LLM) باستخدام PyTorch وROCm. يغطي عدة تقنيات، من الضبط القياسي إلى استراتيجيات الضبط الدقيق كفؤ المعاملات (PEFT) الموفرة للذاكرة، لتتمكن من تكييف النماذج بسهولة وفق احتياجاتك.

**النموذج المستخدم**: google/gemma-3-4b-it (سكربت QLoRA: openai/gpt-oss-20b)  *(راجع [تفعيل مصادقة HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) إذا كان النموذج مقيّدًا)*  
**العتاد**: بطاقة AMD Radeon™ مع دعم ROCm  
**الإطار البرمجي**: PyTorch + Hugging Face (Transformers، PEFT، Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **ملاحظة:** 
> - يتطلب الضبط الدقيق الكامل على الأقل **64 جيجابايت من ذاكرة النظام RAM**، على أن يكون **32 جيجابايت منها متاحًا لبطاقة الرسوميات** (الـ32 جيجابايت جزء من الـ64 جيجابايت، وليست إضافة لها).
> - يمكنك أيضًا تجربة معماريات نماذج أخرى، بما في ذلك **GPT-OSS-20B**، عن طريق استبدال النموذج في سكربتات التدريب المقدمة.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA وQLoRA على الأقل **32 جيجابايت من ذاكرة النظام RAM**، على أن يكون **16 جيجابايت منها متاحًا لبطاقة الرسوميات** (الـ16 جيجابايت جزء من الـ32 جيجابايت، وليست إضافة لها).
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA على الأقل **32 جيجابايت من ذاكرة النظام RAM**، على أن يكون **16 جيجابايت منها متاحًا لبطاقة الرسوميات** (الـ16 جيجابايت جزء من الـ32 جيجابايت، وليست إضافة لها).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA وQLoRA بطاقة رسوميات تحتوي على الأقل **16 جيجابايت من ذاكرة GPU المخصصة** و**32 جيجابايت من ذاكرة النظام RAM**.
> - على نظام Linux، يعمل التدريب بالكامل ضمن ذاكرة VRAM المخصصة لبطاقة الرسوميات.
> - لا يتم الرجوع إلى ذاكرة GPU المشتركة (ذاكرة النظام RAM) عند نفاد VRAM.
> - البطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة ستنفد ذاكرتها أثناء التدريب على Linux، حتى لو كان النظام يحتوي على كمية وفيرة من RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** يتطلب الضبط الدقيق باستخدام LoRA على الأقل **16 جيجابايت من إجمالي ذاكرة GPU** و**32 جيجابايت من ذاكرة النظام RAM**.
> - على نظام Windows، يجمع إجمالي ذاكرة GPU بين ذاكرة VRAM المخصصة لبطاقة الرسوميات وذاكرة GPU المشتركة (المقترضة من ذاكرة النظام RAM).
> - لذلك، يمكن للبطاقات التي تحتوي على أقل من 16 جيجابايت من VRAM المخصصة تشغيل هذا الدليل بالاستعانة بذاكرة GPU المشتركة لتعويض الفرق.
<!-- @os:end -->
<!-- @device:end -->

## ما ستتعلمه

- كيفية ضبط نموذج لغوي كبير (LLM) باستخدام LoRA وQLoRA والضبط الدقيق الكامل مع PyTorch وROCm
- كيفية حفظ ونشر النموذج المضبوط
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

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

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
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (سجّل الخروج ثم الدخول مجددًا ليصبح هذا ساري المفعول):

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
**Windows:** يتم اختبار الحزم الأساسية فقط ودعمها هنا. **bitsandbytes غير مدعوم بشكل جيد على Windows**، لذا يتم استبعاده من التثبيت على Windows؛ استخدم LoRA أو الضبط الدقيق الكامل على Windows (تتطلب QLoRA وجود bitsandbytes وهي مخصصة لنظام Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.4.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### تفعيل مصادقة HF (النماذج المقيّدة أو المخصصة / غير المثبتة مسبقًا)

في هذا المثال نستخدم **google/gemma-3-4b-it**، وهو نموذج **مقيّد (gated)**. يجب عليك قبول شروط النموذج على Hugging Face ثم المصادقة ليتمكن سكربت التدريب من تنزيله.

1. **قبول الترخيص:** افتح [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)، وسجّل الدخول (أو أنشئ حسابًا)، واقبل الترخيص/الشروط في صفحة النموذج (مثل "Agree and access repository").
2. **التثبيت وتسجيل الدخول:** ثبّت واجهة سطر الأوامر الخاصة بـ Hugging Face، ثم قم بتسجيل الدخول القياسي:

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

تُبقي تقنية **LoRA (Low-Rank Adaptation)** النموذج الأساسي مجمدًا وتقوم فقط بتدريب مصفوفات "محول" (adapter) صغيرة تُضاف إلى طبقات معينة. 

- **الفكرة الأساسية**: بدلاً من تحديث مصفوفة أوزان ضخمة تحتوي على ملايين المعاملات، نتعلم تحديثًا منخفض الرتبة (مصفوفتان صغيرتان ناتج ضربهما يحتوي على معاملات أقل بكثير). هذا يمنح تخفيضًا كبيرًا في المعاملات القابلة للتدريب وذاكرة VRAM مع الحفاظ على معظم جودة الضبط الدقيق الكامل.

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

تجمع تقنية **QLoRA** بين **التكميم بـ4-بت (4-bit quantization)** و**LoRA**. يتم تحميل النموذج الأساسي بدقة 4-بت (توفير كبير في الذاكرة)، بينما تُدرَّب محولات LoRA فقط بدقة أعلى. بهذا تحصل على كفاءة معاملات LoRA مع ذاكرة VRAM أقل بكثير، مع تنازل بسيط في الجودة مقارنة بـLoRA كامل الدقة. يُلاحظ أن التكميم بـ4-بت قد يسبب عدم استقرار عددي (قفزات في الخسارة أو قيم NaN)، لذا قد يفضل المستخدمون غالبًا استخدام **LoRA** إذا كانت ذاكرة VRAM الكافية متوفرة.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **ملاحظة**: بالنسبة للنماذج الأساسية من نوع MXFP4 مثل `openai/gpt-oss-20b`، نوصي باستخدام **LoRA** (`train_lora.py`) بدلاً من QLoRA. يقوم مسار 4-بت الخاص بـ`bitsandbytes` في سكربت QLoRA عادةً بإلغاء تكميم أوزان MXFP4 إلى BF16، لذا يتصرف التشغيل كأنه LoRA قياسي. يتطلب دعم MXFP4 الأصلي بناء `bitsandbytes` من المصدر بالإضافة إلى حزمة متوافقة من Transformers/Triton/kernels. راجع [وثائق Transformers الخاصة بـMXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. اختر الطريقة المناسبة لك

| الطريقة | الذاكرة | السرعة | الجودة | الأفضل لـ |
|--------|--------|-------|---------|----------|
| **QLoRA** (لنظام Linux فقط) | 12-16 جيجابايت | الأسرع | 90-95% | استخدام ذاكرة منخفض |
| **LoRA** | 24-32 جيجابايت | سريع | 95-98% | نهج متوازن |
| **Full** | 80 جيجابايت+ | الأبطأ | 100% | أقصى جودة |

### 3. تشغيل التدريب

**مجموعة البيانات وما يتعلمه النموذج**  
تحوّل البرامج النصية مجموعة البيانات إلى أمثلة محادثة. على سبيل المثال، يستخدم برنامج QLoRA النصي مجموعة **Abirate/english_quotes**: يصبح كل مثال زوجًا من المستخدم والمساعد على النحو التالي:

- **المستخدم:** "أعطني اقتباسًا عن: &lt;tag&gt;"
- **المساعد:** "&lt;quote&gt; – &lt;author&gt;"

يُعلّم الضبط الدقيق النموذج كيفية الاستجابة للطلبات التي تطلب اقتباسات حول موضوع ما وإرجاعها بالتنسيق `<quote text> - <author>`. تستخدم برامج LoRA والضبط الدقيق الكامل النصية مجموعة **databricks/databricks-dolly-15k** (أزواج تعليمات/استجابات عامة)، لذا تختلف المهمة الدقيقة حسب البرنامج النصي؛ لكن الفكرة واحدة - تكييف النموذج مع مجموعة البيانات والتنسيق الذي تختاره.

فيما يلي ملخص لطرق التدريب المتاحة. يرتبط كل طريقة ببرنامجها النصي ويقدم وصفًا موجزًا لاختيار النهج المناسب.

| البرنامج النصي                           | الطريقة            | الوصف                                                                                                         | ذاكرة الفيديو العشوائية (VRAM) النموذجية | موصى به لـ                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | يدرّب مصفوفات محولات صغيرة مع تجميد النموذج الأساسي. أسرع بمقدار 3-5 مرات؛ جودة تبلغ حوالي 95-98% من الجودة الكاملة.                         | 24–32 جيجابايت      | المستخدمون المتقدمون؛ محولات متعددة؛ ذاكرة فيديو عشوائية أكبر    |
| [`train_qlora.py`](assets/train_qlora.py)  *(لنظام Linux فقط)*             | **QLoRA**       | تكميم 4-بت + محولات LoRA. أقل استخدام للذاكرة، الأسرع، مع تنازل بسيط في الجودة. يتطلب `bitsandbytes` (لنظام Linux فقط).                            | 12–16 جيجابايت      | معظم المستخدمين؛ تجارب سريعة؛ ذاكرة فيديو عشوائية محدودة      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **الضبط الدقيق الكامل** | يحدّث جميع معاملات النموذج. أقصى جودة؛ أعلى استخدام للذاكرة والحوسبة.                                    | 40 جيجابايت+      | أقصى جودة؛ البحث العلمي؛ ذاكرة فيديو عشوائية كبيرة           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64 جيجابايت من ذاكرة الوصول العشوائي للنظام وقد لا يكون ممكنًا على هذا الجهاز. ضع في اعتبارك استخدام LoRA أو QLoRA بدلًا من ذلك.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة:** قد يتطلب الضبط الدقيق الكامل (`train_full_finetuning.py`) أكثر من 64 جيجابايت من ذاكرة الوصول العشوائي للنظام وقد لا يكون ممكنًا على هذا الجهاز. ضع في اعتبارك استخدام LoRA بدلًا من ذلك.
<!-- @os:end -->
<!-- @device:end -->

ببساطة، اختر `طريقة التدريب` المفضلة لديك، وقم بتنزيل البرنامج النصي المطابق ونفّذه باستخدام الأمر مع إبقاء بيئتك الافتراضية مُفعّلة: 

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
- تأكد من أن اسم دليل النموذج (`output-gemma-3-4b-it-full`، `output-gpt-oss-20b-qlora`) يطابق مجلد الإخراج الفعلي لديك من التدريب.  
- إذا استخدمت LoRA بدلًا من QLoRA، فما عليك سوى استبدال المسار وفقًا لذلك.  
- تتطلب بعض نماذج Gemma تحديد `trust_remote_code=True` في `from_pretrained`؛ أضفها إذا رأيت تحذيرًا متعلقًا بذلك.

للحصول على إعدادات مخصصة أكثر (رموز الحشو، الجهاز، إلخ)، راجع البرنامج النصي الذي استخدمته للتدريب.

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

### استخدام مجموعة بياناتك الخاصة

تستخدم جميع البرامج النصية نفس تنسيق مجموعة البيانات. استبدل قسم التحميل:

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

عند استخدام هذه الطريقة، يرجى التأكد من أن ملفات JSON الخاصة بك مُهيكلة بشكل صحيح لتجنب أخطاء التحليل. 

يجب الالتزام بالإرشادات التالية:
* **تنسيق الملف:** يجب تنسيق ملفات JSON ضمن بيئة تطوير متكاملة (IDE) لضمان البنية وبناء الجملة الصحيحين.
* **المفاتيح المطلوبة:** يجب أن يحتوي ملف JSON المخصص على المفتاحين `instruction` و`response`. هذان المفتاحان ضروريان لعمل الطريقة بشكل صحيح.
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

عند استخدام مجموعات بيانات من Hugging Face، يرجى التأكد من أن مجموعات البيانات الخاصة بك مُهيكلة بشكل صحيح لتسهيل التكامل السلس. 

يجب اتباع الإرشادات التالية:
* **زوج التعليمة-الاستجابة:** ركّز على مجموعات البيانات التي تحتوي على زوج `instruction-response`. هذه البنية ضرورية للوظيفة المقصودة.
* **تعديل المفتاح المخصص:** إذا لم تتوافق مجموعة بياناتك مع بنية `instruction-response`، فلديك خيار تعديل الدالة `format_instruction()`. يتيح لك ذلك استيعاب مفاتيح محددة حسب الحاجة.

مثال على التعديل: في الحالات التي تحتاج فيها مخرجات مجموعة البيانات إلى تعديل، يمكنك تعديل قسم الاستجابة ضمن الدالة format_instruction() لتناسب متطلباتك.
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

لتهيئة البرنامج النصي لاستخدام تنسيق ملف CSV، تحتاج إلى التأكد من أن ملف CSV يحتوي على أعمدة باسم `instruction` و`response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### ضبط معاملات التدريب

حرّر البرنامج النصي للتدريب وغيّر المتغيرات لتتناسب مع أهدافك: **معدل التعلم** (`LR`)، و**عدد العصور** (`EPOCHS`)، و**حجم الدفعة** (`BATCH_SIZE`)، و**تراكم التدرجات** (`GRAD_ACCUM_STEPS`)، وبالنسبة لـ LoRA/QLoRA **الرتبة** (`LORA_R`). للحصول على تشغيل أسرع، استخدم عددًا أقل من العصور ومعدل تعلم أعلى (LR)؛ وللحصول على جودة أفضل، استخدم عددًا أكبر من العصور ومعدل تعلم أقل. قلّل حجم الدفعة أو طول التسلسل إذا واجهت أخطاء نفاد الذاكرة.
### نصائح تحسين الذاكرة

إذا واجهت أخطاء نفاد الذاكرة:

**1. تقليل حجم الدفعة (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. تقليل طول التسلسل (Sequence Length):**
```python
max_seq_length=256  # Instead of 512
```

**3. استخدام تكميم أكثر صرامة:**
```
Full → LoRA → QLoRA
```

**4. تفعيل Gradient Checkpointing (للضبط الدقيق الكامل فقط):**
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

لتسجيل عمليات التشغيل والمقاييس في [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

في نص البرمجة الخاص بالتدريب، اضبط `report_to="wandb"` واختياريًا `run_name="your-experiment-name"` في إعدادات المدرِّب. إذا كنت تفضل عدم استخدام Wandb، اترك `report_to` على قيمته الافتراضية أو اضبطه على `"none"`.

### المشكلات الشائعة

#### نفاد الذاكرة (OOM)

**الحل:** تقليل حجم الدفعة و/أو استخدام QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### الخسارة (Loss) لا تنخفض

**الحل:** ضبط معدل التعلّم
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### بطء التدريب

**الحل:** زيادة حجم الدفعة إذا سمحت الذاكرة بذلك
```python
BATCH_SIZE = 8
```
## الخطوات التالية

بعد إتمام عملية الضبط الدقيق بنجاح، ضع في اعتبارك الخطوات التالية للحصول على أقصى استفادة من نموذجك:

1. **قيّم** النموذج بدقة على بيانات اختبار منفصلة لقياس التعميم وتجنّب الإفراط في التخصيص (overfitting).
2. **جرّب** قيمًا مختلفة للمعاملات الفائقة (hyperparameters) للحصول على توازن أفضل بين الدقة والسرعة واستهلاك الذاكرة.
3. **تتبّع** جميع تجاربك (والمقاييس المرتبطة بها) باستخدام Weights & Biases لضمان أبحاث قابلة لإعادة الإنتاج.
4. **جرّب** التدريب على مجموعات بيانات خاصة بك لتكييف النموذج مع حالة استخدامك تحديدًا.
5. **انشر** نموذجك بعد الضبط الدقيق لتحقيق استدلال سريع باستخدام خلفيات فعّالة مثل vLLM على الأجهزة المتوافقة.
6. **استكشف** تقنيات متقدمة تشمل هندسة التلقين (prompt engineering)، والدقة المختلطة (mixed precision)، وأطوال تسلسل أطول.
7. **درّب** عدة محولات LoRA لمهام أو مجالات مختلفة وقم بتبديلها حسب الحاجة.

---