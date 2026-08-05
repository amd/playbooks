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

يوضح هذا الدليل الإرشادي كيفية ضبط نموذج لغوي محليًا باستخدام Unsloth على أجهزة AMD.

يستخدم مثالًا قصيرًا للضبط الدقيق الخاضع للإشراف (SFT) مع محولات LoRA على `unsloth/gemma-4-E4B-it`، باستخدام مجموعة فرعية من مجموعة بيانات `mlabonne/FineTome-100k`. الهدف هو تزويدك بسير عمل بسيط شامل يغطي الإعداد والتدريب والاستدلال وحفظ النتيجة المضبوطة.

صُمم هذا المثال ليكون عمليًا وسهل التعديل، بحيث يمكنك استخدامه كنقطة انطلاق لمجموعات البيانات والنماذج الخاصة بك.

## ما ستتعلمه

- كيفية إعداد بيئة Unsloth
- كيفية ضبط نموذج لغوي كبير باستخدام SFT مع Unsloth
- كيفية حفظ النتيجة المضبوطة دقيقًا في التخزين المحلي

<!-- @device:halo,stx,krk -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل الإرشادي ما لا يقل عن **64 جيجابايت من ذاكرة الوصول العشوائي للنظام**، مع توفر ما لا يقل عن **24 جيجابايت منها لوحدة معالجة الرسومات** (24 جيجابايت جزء من الـ 64 جيجابايت، وليست إضافة عليها).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل الإرشادي ما لا يقل عن **24 جيجابايت من إجمالي ذاكرة وحدة معالجة الرسومات** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - في نظام Windows، يجمع إجمالي ذاكرة وحدة معالجة الرسومات بين ذاكرة VRAM المخصصة لبطاقة الرسومات وذاكرة وحدة معالجة الرسومات المشتركة (المُستعارة من ذاكرة الوصول العشوائي للنظام).
> - لذلك، يمكن للبطاقات ذات الذاكرة المخصصة VRAM الأقل من 24 جيجابايت تشغيل هذا الدليل الإرشادي باستخدام ذاكرة وحدة معالجة الرسومات المشتركة لتعويض الفرق.
<!-- @os:end -->

<!-- @os:linux -->
> **ملاحظة:** تتطلب تقنيات الضبط الدقيق في هذا الدليل الإرشادي بطاقة رسومات بها ما لا يقل عن **24 جيجابايت من ذاكرة وحدة معالجة الرسومات المخصصة** و**32 جيجابايت من ذاكرة الوصول العشوائي للنظام**.
> - في نظام Linux، يعمل التدريب بالكامل ضمن ذاكرة VRAM المخصصة لبطاقة الرسومات.
> - لا يعود التدريب إلى ذاكرة وحدة معالجة الرسومات المشتركة (ذاكرة الوصول العشوائي للنظام) عند نفاد VRAM.
> - ستنفد ذاكرة البطاقات ذات الذاكرة المخصصة VRAM الأقل من 24 جيجابايت أثناء التدريب على Linux، حتى لو كان لدى النظام ذاكرة وصول عشوائي وفيرة.
<!-- @os:end -->
<!-- @device:end -->

## لماذا Unsloth؟

تُسهّل Unsloth تشغيل الضبط الدقيق لنماذج اللغة الكبيرة على الأجهزة المحلية من خلال تقليل استخدام الذاكرة وتسريع التدريب مقارنةً بالإعداد القياسي.

في هذا الدليل الإرشادي، نستخدم Unsloth مع **الضبط الدقيق الخاضع للإشراف القائم على LoRA**. هذا يعني أن النموذج الأساسي يبقى مجمدًا في الغالب، بينما يتم تدريب مجموعة أصغر بكثير من أوزان المحولات. هذا مناسب جدًا للتطوير المحلي لأنه أخف من الضبط الدقيق الكامل وأسرع في التكرار عليه.

تدعم Unsloth أيضًا أساليب تدريب أخرى، بما في ذلك QLoRA وسير عمل التعلم المعزز. يركز هذا الدليل الإرشادي على أبسط مسار أولاً: مثال صغير للضبط الدقيق باستخدام LoRA يمكن للمستخدمين تشغيله وفهمه وتوسيعه.

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته باستخدام Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
افتح طرفية (terminal) وأنشئ بيئة venv مع تثبيت برنامج AMD ROCm™ وPyTorch مسبقًا:
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
**امنح مستخدمك حق الوصول إلى أجهزة وحدة معالجة الرسومات** (يجب تسجيل الخروج وإعادة تسجيل الدخول ليدخل هذا حيز التنفيذ):

```bash
sudo usermod -aG render,video $LOGNAME
```

افتح طرفية (terminal) وأنشئ بيئة venv:
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
> **ملاحظة:** يُطلب Python 3.13 لنظام Windows.

<!-- @device:halo_box -->
افتح طرفية PowerShell وأنشئ بيئة افتراضية:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
افتح طرفية PowerShell وأنشئ بيئة افتراضية:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### تثبيت التبعيات الأساسية
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

### تبعيات إضافية

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

> **ملاحظة:** أثناء الاستيراد، قد تختبر Unsloth مسارات تسريع اختيارية لمكتبة `bitsandbytes`. في بعض إصدارات ROCm، قد تظهر رسالة مثل `bitsandbytes library load error: Configured ROCm binary not found`. يستخدم هذا الدليل الإرشادي الضبط الدقيق القياسي باستخدام LoRA مع `optim="adamw_torch"`، لذا فنحن لا نعتمد على محسّن `bitsandbytes` أو QLoRA بدقة 4-بت. يمكن تجاهل هذه الرسالة بأمان.

<!-- @os:windows -->
> **ملاحظة:** على نظام Windows ROCm، ستطبع Unsloth عدة تحذيرات عند بدء التشغيل — راجع [التحذيرات المعروفة](#known-warnings) أدناه. جميعها آمنة ويمكن تجاهلها؛ يعمل التدريب بشكل صحيح.
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

## تنزيل نص برمجي للضبط الدقيق باستخدام Unsloth

بدلًا من تنفيذ كل خطوة يدويًا، يوفر هذا الدليل الإرشادي نصًا برمجيًا نظيفًا وشاملًا هنا: [test_unsloth.py](assets/test_unsloth.py).

قم بتشغيل الكود التالي لتنفيذ النص البرمجي:

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

سيتناول باقي هذا الدليل الإرشادي من الناحية المفاهيمية كل خطوة رئيسية من خطوات النص البرمجي.

## كيف يعمل

يقوم النص البرمجي test_unsloth.py بتنفيذ الخطوات التالية:
* **تحميل النموذج**: يقوم بتحميل unsloth/gemma-4-E4B-it باستخدام FastModel.
* **تحضير البيانات**: يوحّد مجموعة البيانات (مثل FineTome-100k) ويطبّق قالب محادثة Gemma-4.
* **تطبيق LoRA**: يضيف محولات إلى وحدات اللغة والانتباه وMLP للتدريب الفعّال.
* **التدريب**: يستخدم SFTTrainer مع إخفاء الخسارة المقتصر على الاستجابة فقط.
* **الاستدلال**: يشغّل اختبار توليد سريع للتحقق من الأداء.
* **الحفظ**: يصدّر محولات LoRA محليًا.

## الإعدادات الرئيسية

يمكنك تعديل الثوابت التالية لتخصيص عملية التشغيل الخاصة بك:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

مثال على رسالة الترحيب من Unsloth والمخرجات عند تحميل أوزان النموذج:

![alt text](assets/welcome.png)

## تحضير مجموعة البيانات

نستخدم مجموعة فرعية من:
```text
mlabonne/FineTome-100k
```
تخضع مجموعة البيانات لما يلي: 
* تحويلها إلى تنسيق محادثة
* معالجتها باستخدام قالب محادثة Gemma-4
* تنظيفها لإزالة رموز BOS المكررة

## تدريب النموذج

يشغّل النص البرمجي عرضًا توضيحيًا قصيرًا للتدريب، بالمعاملات التالية:
- حوالي 50 خطوة
- حجم دفعة صغير
- تراكم التدرجات

أثناء التدريب، سترى سجلات مثل:

![alt text](assets/training.png)


## الحفظ والنشر
### الحفظ المحلي (LoRA)

يقوم البرنامج النصي تلقائيًا بحفظ محولات LoRA في OUTPUT_DIR.
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

### حفظ النموذج المدمج (لـ vLLM)

<!-- @os:windows -->
> **ملاحظة:** لا يدعم vLLM نظام Windows. لنشر النموذج الذي تم ضبطه دقيقًا على Windows، استخدم llama.cpp (راجع [تصدير GGUF](#export-gguf-for-llamacpp) أدناه) أو انقل النموذج المدمج إلى جهاز Linux يشغّل vLLM.
<!-- @os:end -->

<!-- @os:linux -->
للنشر باستخدام vLLM، ادمج المحولات في نموذج كامل:
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

### تصدير GGUF (لـ llama.cpp)

قم بالتحويل مباشرة إلى GGUF للاستدلال المحلي:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## تحذيرات معروفة

يتم طباعة هذه التحذيرات بواسطة Unsloth عند بدء التشغيل على Windows ROCm ويمكن تجاهلها جميعًا بأمان:

| التحذير | السبب | آمن للتجاهل؟ |
|---|---|---|
| `bitsandbytes library load error` | لا يوجد إصدار Windows ROCm لمكتبة bitsandbytes | نعم — يستخدم هذا الدليل `adamw_torch`، وليس bnb |
| `No ROCm platform found for torch.distributed` | لا يدعم ROCm على Windows التدريب الموزع | نعم — التدريب بوحدة معالجة رسومية واحدة غير متأثر |
| `Unsloth: WARNING! You are using an unsupported platform` | يشير Unsloth إلى الإصدارات غير الخاصة بـ Linux | نعم — يعمل Windows ROCm مع SFT بوحدة معالجة رسومية واحدة |
| `triton is not available` | لا يوجد إصدار Windows لـ Triton | نعم — يعود Unsloth إلى نواة PyTorch |

سيستمر التدريب بشكل صحيح رغم هذه التحذيرات.
<!-- @os:end -->

## الخطوات التالية
- جرّب [Unsloth Studio](https://unsloth.ai/docs/new/studio)، وهي واجهة رسومية بديهية لـ Unsloth
- درّب النموذج على مجموعات بياناتك الخاصة
- جرّب الضبط الدقيق باستخدام معاملات فائقة مختلفة
- انشر باستخدام vLLM أو llama.cpp
- جرّب QLoRA للحصول على إعداد بذاكرة أقل

## الموارد

فيما يلي بعض الموارد الإضافية لمعرفة المزيد حول Unsloth والضبط الدقيق:

* [مستندات Unsloth](https://docs.unsloth.ai)

* [مستودع Unsloth على GitHub](https://github.com/unslothai/unsloth)

* [دليل الضبط الدقيق من Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)