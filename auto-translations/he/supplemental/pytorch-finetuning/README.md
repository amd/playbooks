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

מדריך זה מספק דוגמאות שלב-אחר-שלב לכוונון עדין (fine-tuning) של מודל שפה גדול (LLM) באמצעות PyTorch ו-ROCm. הוא מכסה מספר טכניקות, מכוונון עדין רגיל ועד לאסטרטגיות כוונון עדין יעיל בזיכרון (Parameter-Efficient Fine-Tuning - PEFT), כך שתוכלו להתאים מודלים בקלות לצרכים שלכם.

**המודל בו נעשה שימוש**: google/gemma-3-4b-it  *(ראו [הפעלת אימות HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) אם המודל נעול)*  
**חומרה**: מעבד גרפי (GPU) של ‎AMD Radeon™‎ עם תמיכת ROCm  
**מסגרת עבודה**: PyTorch ‎+‎ Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **הערה:** 
> - כוונון עדין מלא (Full fine-tuning) דורש לפחות **64 GB של זיכרון RAM במערכת**, כאשר לפחות **32 GB מתוכם זמינים ל-GPU** (32 ה-GB הם חלק מ-64 ה-GB, ולא בנוסף להם).
> - ניתן גם לנסות ארכיטקטורות מודלים אחרות, כולל **GPT-OSS-20B**, על ידי החלפת המודל בסקריפטים המסופקים לאימון.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **הערה:** כוונון עדין באמצעות LoRA ו-QLoRA דורש לפחות **32 GB של זיכרון RAM במערכת**, כאשר לפחות **16 GB מתוכם זמינים ל-GPU** (16 ה-GB הם חלק מ-32 ה-GB, ולא בנוסף להם).
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין באמצעות LoRA דורש לפחות **32 GB של זיכרון RAM במערכת**, כאשר לפחות **16 GB מתוכם זמינים ל-GPU** (16 ה-GB הם חלק מ-32 ה-GB, ולא בנוסף להם).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **הערה:** כוונון עדין באמצעות LoRA ו-QLoRA דורש כרטיס מסך עם לפחות **16 GB של זיכרון GPU ייעודי** ו-**32 GB של זיכרון RAM במערכת**.
> - בלינוקס, האימון פועל כולו בזיכרון ה-VRAM הייעודי של כרטיס המסך.
> - הוא אינו עובר לזיכרון GPU משותף (RAM של המערכת) כאשר ה-VRAM נגמר.
> - כרטיסים עם פחות מ-16 GB של VRAM ייעודי ייגמר להם הזיכרון במהלך האימון בלינוקס, גם אם למערכת יש הרבה RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין באמצעות LoRA דורש לפחות **16 GB של זיכרון GPU כולל** ו-**32 GB של זיכרון RAM במערכת**.
> - בחלונות, זיכרון ה-GPU הכולל משלב את ה-VRAM הייעודי של כרטיס המסך עם זיכרון GPU משותף (שנשאל מזיכרון ה-RAM של המערכת).
> - לכן, כרטיסים עם פחות מ-16 GB של VRAM ייעודי עדיין יכולים להריץ את המדריך הזה באמצעות שימוש בזיכרון GPU משותף כדי להשלים את ההפרש.
<!-- @os:end -->
<!-- @device:end -->

## מה תלמדו

- כיצד לבצע כוונון עדין למודל שפה גדול באמצעות LoRA, QLoRA וכוונון עדין מלא (full fine-tuning) עם PyTorch ו-ROCm
- כיצד לשמור ולפרוס את המודל המכוונן שלכם
- כיצד לנטר את האימון ולבצע איתור באגים לבעיות נפוצות

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

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
**חלונות:** רק חבילות הליבה נבדקו ונתמכות כאן. **bitsandbytes אינו נתמך היטב בחלונות**, לכן ההתקנה עבור חלונות משמיטה אותה; השתמשו ב-LoRA או בכוונון עדין מלא בחלונות (QLoRA דורש bitsandbytes ומיועד ללינוקס).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### הפעלת אימות HF (מודלים נעולים או מותאמים אישית / שאינם מותקנים מראש)

בדוגמה זו אנו משתמשים ב-**google/gemma-3-4b-it**, שהוא מודל **נעול**. עליכם לאשר את התנאים של המודל ב-Hugging Face ולאחר מכן לבצע אימות כך שסקריפטי האימון יוכלו להוריד אותו.

1. **קבלת הרישיון:** פתחו את [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), התחברו (או צרו חשבון), וקבלו את הרישיון/התנאים בדף המודל (למשל, "Agree and access repository").
2. **התקנה והתחברות:** התקינו את ה-Hugging Face CLI, ולאחר מכן הריצו את ההתחברות הרגילה:

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

**LoRA ‏(Low-Rank Adaptation)** משאיר את המודל הבסיסי קפוא ומאמן רק מטריצות "מתאם" (adapter) קטנות שמתווספות לשכבות מסוימות. 

- **הרעיון המרכזי**: במקום לעדכן מטריצת משקלים ענקית עם מיליוני פרמטרים, אנו לומדים עדכון בדרגה נמוכה (rank נמוך) - שתי מטריצות קטנות שהמכפלה שלהן מכילה הרבה פחות פרמטרים. כך מתקבלת הפחתה גדולה במספר הפרמטרים הניתנים לאימון ובזיכרון ה-VRAM, תוך שמירה על רוב האיכות של כוונון עדין מלא.

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

**QLoRA** משלב **קוונטיזציה ל-4 סיביות** עם **LoRA**. המודל הבסיסי נטען ב-4 סיביות (חיסכון גדול בזיכרון), ורק מתאמי ה-LoRA מאומנים בדיוק גבוה יותר. כך מתקבלת יעילות הפרמטרים של LoRA בתוספת VRAM נמוך בהרבה, עם פשרה קטנה באיכות בהשוואה ל-LoRA בדיוק מלא. שימו לב שקוונטיזציה ל-4 סיביות עלולה לגרום לחוסר יציבות מספרית (קפיצות בפונקציית האובדן או ערכי NaN), ולכן משתמשים לרוב עשויים להעדיף **LoRA** אם יש מספיק VRAM זמין.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **הערה**: עבור מודלים בסיסיים מסוג MXFP4 כגון `openai/gpt-oss-20b`, אנו ממליצים להשתמש ב-**LoRA** (`train_lora.py`) במקום ב-QLoRA. הנתיב ל-4 סיביות של `bitsandbytes` בסקריפט ה-QLoRA בדרך כלל מבצע דה-קוונטיזציה (dequantize) למשקלי MXFP4 חזרה ל-BF16, כך שההרצה מתנהגת כמו LoRA רגיל. MXFP4 מקורי (native) דורש `bitsandbytes` שנבנה מקוד המקור בתוספת ערימת Transformers/Triton/kernels תואמת. ראו [תיעוד MXFP4 של Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. בחר את השיטה שלך

| שיטה | זיכרון | מהירות | איכות | הכי מתאים עבור |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux בלבד) | 12-16GB | הכי מהיר | 90-95% | שימוש נמוך בזיכרון |
| **LoRA** | 24-32GB | מהיר | 95-98% | גישה מאוזנת |
| **Full** | 80GB+ | הכי איטי | 100% | איכות מקסימלית |

### 3. הרצת אימון

**מערך הנתונים ומה המודל לומד**  
הסקריפטים הופכים את מערך הנתונים לדוגמאות שיחה. לדוגמה, סקריפט ה-QLoRA משתמש ב-**Abirate/english_quotes**: כל דוגמה הופכת לזוג משתמש-עוזר כמו:

- **משתמש:** "תן לי ציטוט על: &lt;תג&gt;"
- **עוזר:** "&lt;ציטוט&gt; – &lt;מחבר&gt;"

כוונון עדין מלמד את המודל להגיב לבקשות המבקשות ציטוטים על נושא מסוים ולהחזיר אותם בפורמט `<quote text> - <author>`. סקריפטי ה-LoRA וכוונון עדין מלא משתמשים ב-**databricks/databricks-dolly-15k** (זוגות הוראה/תגובה כלליים), כך שהמשימה המדויקת משתנה לפי הסקריפט; הרעיון זהה - להתאים את המודל למערך הנתונים ולפורמט שבחרת.

להלן סיכום של שיטות האימון הזמינות. כל שיטה מקושרת לסקריפט שלה ומספקת תיאור קצר לבחירת הגישה הנכונה.

| סקריפט                           | שיטה            | תיאור                                                                                                         | VRAM טיפוסי | מומלץ עבור                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | מאמן מטריצות מתאם קטנות תוך הקפאת המודל הבסיסי. מהיר פי 3–5; ~95–98% מהאיכות המלאה.                         | 24–32GB      | משתמשים מתקדמים; מתאמים מרובים; יותר VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux בלבד)*             | **QLoRA**       | קוונטיזציה ב-4 ביט + מתאמי LoRA. שימוש נמוך ביותר בזיכרון, הכי מהיר, פשרה קטנה באיכות. דורש `bitsandbytes` (Linux בלבד).                            | 12–16GB      | רוב המשתמשים; ניסויים מהירים; VRAM מוגבל      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **כוונון עדין מלא** | מעדכן את כל פרמטרי המודל. איכות מקסימלית; השימוש הגבוה ביותר בזיכרון ובחישוב.                                    | 40GB+        | איכות מקסימלית; מחקר; VRAM גדול           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **הערה:** כוונון עדין מלא (`train_full_finetuning.py`) עשוי לדרוש יותר מ-64GB של זיכרון מערכת (RAM) וייתכן שלא יהיה ישים במכשיר זה. שקול להשתמש ב-LoRA או QLoRA במקום זאת.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין מלא (`train_full_finetuning.py`) עשוי לדרוש יותר מ-64GB של זיכרון מערכת (RAM) וייתכן שלא יהיה ישים במכשיר זה. שקול להשתמש ב-LoRA במקום זאת.
<!-- @os:end -->
<!-- @device:end -->

פשוט בחר את `Training method` המועדפת עליך, הורד את הסקריפט המתאים והרץ אותו באמצעות הפקודה תוך שמירה על סביבה וירטואלית פעילה: 

```python
python3 train_<method_name>.py.
```

## שימוש במודל המכוונן שלך

### לאחר כוונון עדין מלא

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
- ודא ששם ספריית המודל (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) תואם לתיקיית הפלט בפועל מהאימון שלך.  
- אם השתמשת ב-LoRA במקום QLoRA, פשוט החלף את הנתיב בהתאם.  
- חלק ממודלי Gemma דורשים ציון `trust_remote_code=True` ב-`from_pretrained`; הוסף אם אתה רואה אזהרה קשורה.

לקבלת הגדרות מותאמות אישית נוספות (אסימוני ריפוד, מכשיר וכו'), עיין בסקריפט שבו השתמשת לאימון.

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

### שימוש במערך הנתונים שלך

כל הסקריפטים משתמשים באותו פורמט מערך נתונים. החלף את חלק הטעינה:

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

**פורמט מערך נתונים עבור קובץ JSON/JSONL מקומי:**

בעת שימוש בשיטה זו, ודא שקבצי ה-JSON שלך מובנים כראוי כדי למנוע שגיאות ניתוח (parsing).

יש להקפיד על ההנחיות הבאות:
* **עיצוב קובץ:** קבצי JSON צריכים להיות מעוצבים בתוך סביבת פיתוח משולבת (IDE) כדי להבטיח מבנה ותחביר תקינים.
* **מפתחות נדרשים:** קובץ ה-JSON המותאם אישית חייב להכיל את המפתחות `instruction` ו-`response`. מפתחות אלה חיוניים לתפקוד תקין של השיטה.
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
**פורמט מערך נתונים עבור מערך נתונים מ-Hugging Face Hub**

בעת שימוש במערכי נתונים מ-Hugging Face, ודא שמערכי הנתונים שלך מובנים כראוי כדי לאפשר שילוב חלק.

יש לפעול לפי ההנחיות הבאות:
* **זוג הוראה-תגובה:** התמקד במערכי נתונים הכוללים זוג `instruction-response`. מבנה זה חיוני לתפקוד המיועד.
* **שינוי מפתח מותאם אישית:** אם מערך הנתונים שלך אינו תואם למבנה `instruction-response`, יש לך אפשרות לשנות את הפונקציה `format_instruction()`. הדבר מאפשר לך להתאים למפתחות ספציפיים לפי הצורך.

דוגמה להתאמה: במקרים שבהם יש להתאים את הפלט של מערך הנתונים, ניתן לשנות את חלק התגובה בתוך הפונקציה format_instruction() כדי להתאים לדרישות שלך.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**פורמט מערך נתונים עבור קובץ CSV**

כדי להתאים את הסקריפט לשימוש בפורמט קובץ CSV, עליך לוודא שקובץ ה-CSV מכיל עמודות בשם `instruction` ו-`response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### התאמת פרמטרי אימון

ערוך את סקריפט האימון ושנה את המשתנים כך שיתאימו למטרות שלך: **קצב למידה** (`LR`), **אפוקים** (`EPOCHS`), **גודל אצווה** (`BATCH_SIZE`), **צבירת גרדיאנטים** (`GRAD_ACCUM_STEPS`), ועבור LoRA/QLoRA **דרגה** (`LORA_R`). להרצות מהירות יותר, השתמש בפחות אפוקים וקצב למידה (LR) גבוה יותר; לאיכות טובה יותר, השתמש ביותר אפוקים ו-LR נמוך יותר. הקטן את גודל האצווה או אורך הרצף אם אתה נתקל בשגיאות זיכרון חסר (out-of-memory).
### טיפים לאופטימיזציית זיכרון

אם אתם נתקלים בשגיאות של חוסר זיכרון:

**1. הקטינו את גודל האצווה (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. הקטינו את אורך הרצף (Sequence Length):**
```python
max_seq_length=256  # Instead of 512
```

**3. השתמשו בקוונטיזציה אגרסיבית יותר:**
```
Full → LoRA → QLoRA
```

**4. הפעילו Gradient Checkpointing (רק לכוונון מלא - Full fine-tuning):**
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

כדי לרשום ריצות ומדדים אל [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

בסקריפט האימון, הגדירו `report_to="wandb"` ובאופן אופציונלי `run_name="your-experiment-name"` בתצורת ה-trainer. אם אתם מעדיפים לא להשתמש ב-Wandb, השאירו את `report_to` בערך ברירת המחדל שלו או הגדירו אותו כ-`"none"`.

### בעיות נפוצות

#### חוסר בזיכרון (OOM)

**פתרון:** הקטינו את גודל האצווה ו/או השתמשו ב-QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### ההפסד (Loss) לא יורד

**פתרון:** התאימו את קצב הלמידה (Learning Rate)
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### אימון איטי

**פתרון:** הגדילו את גודל האצווה אם הזיכרון מאפשר זאת
```python
BATCH_SIZE = 8
```
## הצעדים הבאים

לאחר שהשלמתם בהצלחה את תהליך הכוונון העדין, שקלו את הצעדים הבאים כדי להפיק את המרב מהמודל שלכם:

1. **הערכה** יסודית על נתוני בדיקה מוחזקים (held-out) כדי למדוד הכללה ולהימנע מהתאמת יתר (overfitting).
2. **ניסוי** בערכים שונים של היפרפרמטרים כדי לקבל פשרות טובות יותר בין דיוק, מהירות וזיכרון.
3. **מעקב** אחר כל הניסויים שלכם (והמדדים המתאימים) עם Weights & Biases למחקר בר-שחזור.
4. **ניסיון** אימון על מערכי נתונים מותאמים אישית משלכם כדי להתאים את המודל במיוחד למקרה השימוש שלכם.
5. **פריסה** של המודל המכוונן שלכם להסקה מהירה באמצעות backends יעילים כמו vLLM על חומרה תואמת.
6. **חקירה** של טכניקות מתקדמות כולל הנדסת פרומפטים, דיוק מעורב (mixed precision), ואורכי רצפים ארוכים יותר.
7. **אימון** מספר מתאמי LoRA עבור משימות או תחומים שונים והחלפתם לפי הצורך.

---