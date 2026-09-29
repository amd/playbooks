<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

מדריך זה מספק דוגמאות שלב אחר שלב לכוונון עדין (fine-tuning) של מודל שפה גדול (LLM) עם PyTorch ו-ROCm. הוא מכסה מספר טכניקות, החל מכוונון עדין סטנדרטי ועד לאסטרטגיות כוונון עדין יעילות בזיכרון (Parameter-Efficient Fine-Tuning, PEFT), כך שתוכלו להתאים מודלים בקלות לצרכים שלכם.

**המודל בו נעשה שימוש**: google/gemma-3-4b-it  *(ראו [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) אם המודל מוגבל גישה)*  
**חומרה**: כרטיס מסך AMD Radeon™ עם תמיכת ROCm  
**מסגרת עבודה**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **הערה:** 
> - כוונון עדין מלא דורש לפחות **64GB של זיכרון RAM במערכת**, כאשר לפחות **32GB מתוכם זמינים ל-GPU** (ה-32GB מהווים חלק מה-64GB, ולא נוספים עליהם).
> - ניתן גם לנסות ארכיטקטורות מודלים אחרות, כולל **GPT-OSS-20B**, על ידי החלפת המודל בסקריפטים לאימון שסופקו.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **הערה:** כוונון עדין מסוג LoRA ו-QLoRA דורש לפחות **32GB של זיכרון RAM במערכת**, כאשר לפחות **16GB מתוכם זמינים ל-GPU** (ה-16GB מהווים חלק מה-32GB, ולא נוספים עליהם).
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין מסוג LoRA דורש לפחות **32GB של זיכרון RAM במערכת**, כאשר לפחות **16GB מתוכם זמינים ל-GPU** (ה-16GB מהווים חלק מה-32GB, ולא נוספים עליהם).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **הערה:** כוונון עדין מסוג LoRA ו-QLoRA דורש כרטיס מסך עם לפחות **16GB של זיכרון GPU ייעודי** ו-**32GB של זיכרון RAM במערכת**.
> - ב-Linux, האימון פועל כולו בזיכרון ה-VRAM הייעודי של כרטיס המסך.
> - הוא אינו עובר לזיכרון GPU משותף (RAM של המערכת) כאשר ה-VRAM אוזל.
> - כרטיסים עם פחות מ-16GB של VRAM ייעודי ייגמר להם הזיכרון במהלך האימון ב-Linux, גם אם למערכת יש הרבה RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין מסוג LoRA דורש לפחות **16GB של זיכרון GPU כולל** ו-**32GB של זיכרון RAM במערכת**.
> - ב-Windows, זיכרון ה-GPU הכולל משלב את ה-VRAM הייעודי של כרטיס המסך יחד עם זיכרון GPU משותף (מושאל מ-RAM של המערכת).
> - לכן, כרטיסים עם פחות מ-16GB של VRAM ייעודי עדיין יכולים להריץ את המדריך הזה על ידי שימוש בזיכרון GPU משותף כדי להשלים את ההפרש.
<!-- @os:end -->
<!-- @device:end -->

## מה תלמדו

- כיצד לבצע כוונון עדין ל-LLM באמצעות LoRA, QLoRA וכוונון עדין מלא עם PyTorch ו-ROCm
- כיצד לשמור ולפרוס את המודל המכוונן שלכם
- כיצד לנטר את האימון ולפתור בעיות נפוצות

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו עם Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

#### יצירת סביבה וירטואלית

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
**הענקת גישה למשתמש שלכם להתקני GPU** (התנתקו והתחברו מחדש כדי שהשינוי ייכנס לתוקף):

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

#### התקנת תלויות בסיסיות
<!-- @require:pytorch -->

#### תלויות נוספות

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** רק חבילות הליבה נבדקו ונתמכות כאן. **bitsandbytes אינה נתמכת היטב ב-Windows**, ולכן ההתקנה עבור Windows משמיטה אותה; השתמשו ב-LoRA או בכוונון עדין מלא ב-Windows (QLoRA דורשת bitsandbytes ומיועדת ל-Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### הפעלת אימות HF (מודלים מוגבלי גישה או מותאמים אישית / שאינם מותקנים מראש)

בדוגמה זו אנו משתמשים ב-**google/gemma-3-4b-it**, שהוא מודל **מוגבל גישה**. עליכם לאשר את תנאי המודל ב-Hugging Face ולאחר מכן להתאמת כדי שסקריפטי האימון יוכלו להוריד אותו.

1. **אישור הרישיון:** פתחו את [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), התחברו (או צרו חשבון), ואשרו את הרישיון/תנאים בעמוד המודל (למשל "Agree and access repository").
2. **התקנה והתחברות:** התקינו את ה-Hugging Face CLI, ולאחר מכן הריצו את ההתחברות הסטנדרטית:

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

## הבנת הטכניקות

### מהו LoRA?

**LoRA (Low-Rank Adaptation)** משאיר את המודל הבסיסי קפוא ומאמן רק מטריצות "מתאם" קטנות שמתווספות לשכבות מסוימות. 

- **הרעיון המרכזי**: במקום לעדכן מטריצת משקלים ענקית עם מיליוני פרמטרים, אנו לומדים עדכון בדרגה נמוכה (שתי מטריצות קטנות שהמכפלה שלהן כוללת הרבה פחות פרמטרים). זה נותן הפחתה גדולה בפרמטרים הניתנים לאימון ובזיכרון ה-VRAM, תוך שמירה על רוב איכות הכוונון העדין המלא.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### מהו QLoRA?

**QLoRA** משלב **קוונטיזציה של 4 ביט** עם **LoRA**. המודל הבסיסי נטען ב-4 ביט (חיסכון זיכרון גדול), ורק המתאמי (adapters) LoRA מאומנים בדיוק גבוה יותר. כך מקבלים את יעילות הפרמטרים של LoRA בתוספת VRAM נמוך בהרבה, עם פשרה קטנה באיכות בהשוואה ל-LoRA בדיוק מלא. שימו לב שקוונטיזציה של 4 ביט עלולה לגרום לחוסר יציבות נומרי (קפיצות loss או NaN), ולכן משתמשים עשויים לרוב להעדיף **LoRA** אם יש מספיק VRAM זמין.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **הערה**: עבור מודלים בסיסיים מסוג MXFP4 כמו `openai/gpt-oss-20b`, אנו ממליצים להשתמש ב-**LoRA** (`train_lora.py`) במקום QLoRA. נתיב ה-4 ביט של `bitsandbytes` בסקריפט QLoRA בדרך כלל מבצע דה-קוונטיזציה למשקלי MXFP4 ל-BF16, כך שהריצה מתנהגת כמו LoRA סטנדרטי. MXFP4 מקורי דורש `bitsandbytes` שנבנה מהמקור בתוספת ערימת Transformers/Triton/kernels תואמת. ראו את [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. בחירת השיטה

| שיטה | זיכרון | מהירות | איכות | מתאים ביותר עבור |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux בלבד) | 12-16GB | הכי מהיר | 90-95% | שימוש מועט בזיכרון |
| **LoRA** | 24-32GB | מהיר | 95-98% | גישה מאוזנת |
| **Full** | 80GB+ | הכי איטי | 100% | איכות מקסימלית |

### 3. הרצת האימון

**מערך הנתונים ומה המודל לומד**  
הסקריפטים הופכים את מערך הנתונים לדוגמאות צ'אט. לדוגמה, סקריפט ה-QLoRA משתמש ב-**Abirate/english_quotes**: כל דוגמה הופכת לזוג משתמש-עוזר כמו:

- **משתמש:** "תן לי ציטוט על: &lt;תגית&gt;"
- **עוזר:** "&lt;ציטוט&gt; – &lt;מחבר&gt;"

כוונון עדין מלמד את המודל להגיב להנחיות שמבקשות ציטוט בנושא מסוים ולהחזיר אותם בפורמט `<טקסט הציטוט> - <מחבר>`. סקריפטי ה-LoRA ואימון ה-full fine-tuning משתמשים ב-**databricks/databricks-dolly-15k** (זוגות הוראה/תגובה כלליים), כך שהמשימה המדויקת משתנה בהתאם לסקריפט; הרעיון זהה - התאמת המודל למערך הנתונים ולפורמט שבחרתם.

להלן סיכום של שיטות האימון הזמינות. כל שיטה מקושרת לסקריפט שלה ומספקת תיאור קצר לבחירת הגישה הנכונה.

| סקריפט                           | שיטה            | תיאור                                                                                                         | VRAM אופייני | מומלץ עבור                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | מאמן מטריצות מתאם קטנות תוך הקפאת מודל הבסיס. מהיר פי 3-5; כ-95-98% מהאיכות המלאה.                         | 24–32GB      | משתמשים מתקדמים; מספר מתאמים; יותר VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux בלבד)*             | **QLoRA**       | קוונטיזציה ל-4 סיביות + מתאמי LoRA. שימוש מינימלי בזיכרון, הכי מהיר, פשרה קטנה באיכות. דורש `bitsandbytes` (Linux בלבד).                            | 12–16GB      | רוב המשתמשים; ניסויים מהירים; VRAM מוגבל      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | מעדכן את כל פרמטרי המודל. איכות מקסימלית; השימוש הגבוה ביותר בזיכרון ובחישוב.                                    | 40GB+        | איכות מקסימלית; מחקר; VRAM גדול           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **הערה:** ייתכן ש-Full fine-tuning (`train_full_finetuning.py`) ידרוש יותר מ-64GB של זיכרון RAM במערכת וייתכן שלא יהיה ישים במכשיר זה. שקלו להשתמש ב-LoRA או ב-QLoRA במקום זאת.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** ייתכן ש-Full fine-tuning (`train_full_finetuning.py`) ידרוש יותר מ-64GB של זיכרון RAM במערכת וייתכן שלא יהיה ישים במכשיר זה. שקלו להשתמש ב-LoRA במקום זאת.
<!-- @os:end -->
<!-- @device:end -->

פשוט בחרו את `Training method` המועדפת עליכם, הורידו את הסקריפט המתאים והריצו אותו באמצעות הפקודה תוך שמירה על סביבה וירטואלית פעילה: 

```python
python3 train_<method_name>.py.
```

## שימוש במודל שעבר כוונון עדין

### לאחר Full Fine-Tuning

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

### לאחר אימון LoRA/QLoRA

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

### מיזוג מתאם LoRA למודל הבסיס

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**הערה:**  
- ודאו ששם תיקיית המודל (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) תואם לתיקיית הפלט בפועל שלכם מהאימון.  
- אם השתמשתם ב-LoRA במקום QLoRA, פשוט החליפו את הנתיב בהתאם.  
- חלק ממודלי Gemma דורשים ציון `trust_remote_code=True` בתוך `from_pretrained`; הוסיפו אם אתם רואים אזהרה קשורה.

להגדרות מותאמות אישית נוספות (טוקני padding, מכשיר וכו'), עיינו בסקריפט שבו השתמשתם לאימון.

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

## מדריך התאמה אישית

### שימוש במערך הנתונים שלכם

כל הסקריפטים משתמשים באותו פורמט מערך נתונים. החליפו את קטע הטעינה:

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

**פורמט מערך הנתונים עבור קובץ JSON/JSONL מקומי:**

בעת שימוש בשיטה זו, ודאו שקבצי ה-JSON שלכם מובנים כראוי כדי להימנע משגיאות ניתוח (parsing).

יש להקפיד על ההנחיות הבאות:
* **פורמט הקובץ:** יש לעצב קבצי JSON בתוך סביבת פיתוח משולבת (IDE) כדי להבטיח מבנה ותחביר תקינים.
* **מפתחות נדרשים:** קובץ ה-JSON המותאם אישית חייב להכיל את המפתחות `instruction` ו-`response`. מפתחות אלו חיוניים לתפקוד תקין של השיטה.
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
**פורמט מערך הנתונים עבור מערך נתונים מ-Hugging Face Hub**

בעת שימוש במערכי נתונים מ-Hugging Face, ודאו שמערכי הנתונים שלכם מובנים כראוי כדי לאפשר שילוב חלק.

יש לפעול לפי ההנחיות הבאות:
* **זוג הוראה-תגובה:** התמקדו במערכי נתונים הכוללים זוג `instruction-response`. מבנה זה חיוני לתפקוד המיועד.
* **שינוי מפתח מותאם אישית:** אם מערך הנתונים שלכם אינו תואם למבנה `instruction-response`, יש לכם אפשרות לשנות את הפונקציה `format_instruction()`. הדבר מאפשר לכם להתאים למפתחות ספציפיים לפי הצורך.

דוגמה להתאמה: במקרים שבהם פלט מערך הנתונים דורש התאמה, ניתן לשנות את קטע התגובה בתוך הפונקציה format_instruction() כדי להתאים לדרישותיכם.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**פורמט מערך הנתונים עבור קובץ CSV**

כדי להתאים את הסקריפט לשימוש בפורמט קובץ CSV, עליכם לוודא שקובץ ה-CSV מכיל עמודות בשם `instruction` ו-`response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### התאמת פרמטרי האימון

ערכו את סקריפט האימון ושנו את המשתנים כך שיתאימו למטרותיכם: **קצב למידה** (`LR`), **אפוקים** (`EPOCHS`), **גודל אצווה** (`BATCH_SIZE`), **צבירת גרדיאנטים** (`GRAD_ACCUM_STEPS`), ועבור LoRA/QLoRA **דרגה** (`LORA_R`). להרצות מהירות יותר השתמשו בפחות אפוקים ובקצב למידה גבוה יותר (LR); לאיכות טובה יותר השתמשו ביותר אפוקים ובקצב למידה נמוך יותר. הקטינו את גודל האצווה או אורך הרצף אם אתם נתקלים בשגיאות של חוסר זיכרון.
### טיפים לאופטימיזציית זיכרון

אם אתם נתקלים בשגיאות של חוסר זיכרון:

**1. הקטינו את גודל האצווה (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. קצרו את אורך הרצף:**
```python
max_seq_length=256  # Instead of 512
```

**3. השתמשו בקוונטיזציה אגרסיבית יותר:**
```
Full → LoRA → QLoRA
```

**4. הפעילו Gradient Checkpointing (עבור כוונון עדין מלא בלבד):**
```python
model.gradient_checkpointing_enable()
```

---

## ניטור ואיתור באגים

### מעקב אחר זיכרון ה-GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (אופציונלי) מעקב אחר ניסויים עם Weights & Biases

כדי לרשום הרצות ומדדים ל-[Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

בסקריפט האימון, הגדירו `report_to="wandb"` ובאופן אופציונלי `run_name="your-experiment-name"` בתצורת ה-trainer. אם אתם מעדיפים לא להשתמש ב-Wandb, השאירו את `report_to` בברירת המחדל שלו או הגדירו אותו ל-`"none"`.

### בעיות נפוצות

#### חוסר זיכרון (OOM)

**פתרון:** הקטינו את גודל האצווה ו/או השתמשו ב-QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ה-Loss אינו יורד

**פתרון:** התאימו את קצב הלמידה
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### אימון איטי

**פתרון:** הגדילו את גודל האצווה אם הזיכרון מאפשר
```python
BATCH_SIZE = 8
```
## הצעדים הבאים

לאחר שהשלמתם בהצלחה את הכוונון העדין, שקלו את הצעדים הבאים כדי להפיק את המרב מהמודל שלכם:

1. **הערכה** יסודית על נתוני בדיקה מוחזקים כדי למדוד את יכולת ההכללה ולהימנע מהתאמת יתר.
2. **ניסוי** בערכי היפרפרמטרים שונים לצורך שיפור הדיוק, המהירות ופשרות הזיכרון.
3. **מעקב** אחר כל הניסויים שלכם (והמדדים המתאימים) עם Weights & Biases לצורך מחקר בר-שחזור.
4. **ניסיון** אימון על מערכי נתונים מותאמים אישית משלכם כדי להתאים את המודל במיוחד למקרה השימוש שלכם.
5. **פריסה** של המודל שלכם לאחר הכוונון העדין לצורך היסק מהיר תוך שימוש ב-backends יעילים כגון vLLM על חומרה תואמת.
6. **חקר** טכניקות מתקדמות כולל הנדסת פרומפטים, דיוק מעורב (mixed precision), ואורכי רצף ארוכים יותר.
7. **אימון** מספר מתאמי LoRA עבור משימות או תחומים שונים והחלפה ביניהם לפי הצורך.

---