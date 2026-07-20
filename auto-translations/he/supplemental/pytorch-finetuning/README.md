<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> ספר משחקים זה משתמש בתגיות מיוחדות ש-GitHub אינו יכול לעבד. יש לבקר בכתובת [amd.com/playbooks](https://amd.com/playbooks) כדי להציג כראוי תוכן זה.
<!-- @github-only:end -->

## סקירה כללית

מדריך זה מספק דוגמאות שלב-אחר-שלב לכוונון עדין (fine-tuning) של מודל שפה גדול (LLM) עם PyTorch ו-ROCm. הוא מכסה מספר טכניקות, החל מכוונון עדין סטנדרטי ועד אסטרטגיות כוונון עדין יעילות בזיכרון (Parameter-Efficient Fine-Tuning - PEFT), כך שתוכלו להתאים בקלות מודלים לצרכיכם.

**המודל בו נעשה שימוש**: google/gemma-3-4b-it  *(ראו [הפעלת אימות HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) אם המודל נעול)*  
**חומרה**: מעבד גרפי AMD Radeon™ עם תמיכת ROCm  
**מסגרת עבודה**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **הערה:** ניתן גם לנסות ארכיטקטורות מודל אחרות, כולל **GPT-OSS-20B**, על ידי החלפת המודל בסקריפטים המסופקים לאימון.
> כוונון עדין מלא דורש לפחות 32GB של זיכרון GPU ו-64GB של זיכרון מערכת (RAM).
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **הערה:** כוונון עדין מסוג LoRA ו-QLoRA דורש לפחות 16GB של זיכרון GPU ו-32GB של זיכרון מערכת.
<!-- @device:end -->

## מה תלמדו

- כיצד לבצע כוונון עדין ל-LLM באמצעות LoRA, QLoRA וכוונון עדין מלא עם PyTorch ו-ROCm
- כיצד לשמור ולפרוס את המודל שעבר כוונון עדין
- כיצד לנטר את האימון ולנפות בעיות נפוצות

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

#### יצירת סביבה וירטואלית

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
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

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

#### התקנת תלויות בסיסיות
<!-- @require:pytorch -->

#### תלויות נוספות

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** רק חבילות ליבה נבדקות ונתמכות כאן. **bitsandbytes אינה נתמכת היטב ב-Windows**, לכן ההתקנה עבור Windows משמיטה אותה; יש להשתמש ב-LoRA או בכוונון עדין מלא ב-Windows (QLoRA דורשת bitsandbytes ומיועדת ל-Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### הפעלת אימות HF (מודלים נעולים או מותאמים אישית / שאינם מותקנים מראש)

בדוגמה זו אנו משתמשים ב-**google/gemma-3-4b-it**, שהוא מודל **נעול**. עליכם לקבל את תנאי המודל ב-Hugging Face ולאחר מכן לבצע אימות כדי שסקריפטי האימון יוכלו להוריד אותו.

1. **קבלת הרישיון:** פתחו את [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), התחברו (או צרו חשבון), וקבלו את הרישיון/תנאים בעמוד המודל (למשל "Agree and access repository").
2. **התקנה והתחברות:** התקינו את ה-CLI של Hugging Face, ולאחר מכן הריצו את ההתחברות הסטנדרטית:

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

### מהי LoRA?

**LoRA (Low-Rank Adaptation)** משמרת את המודל הבסיסי קפוא ומאמנת רק מטריצות "מתאם" קטנות שמתווספות לשכבות מסוימות.

- **הרעיון המרכזי**: במקום לעדכן מטריצת משקלים ענקית עם מיליוני פרמטרים, אנו לומדים עדכון בדרגה נמוכה (rank נמוך) (שתי מטריצות קטנות שמכפלתן כוללת הרבה פחות פרמטרים). זה נותן הפחתה גדולה בפרמטרים הניתנים לאימון ובזיכרון VRAM תוך שמירה על רוב איכות הכוונון העדין המלא.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### מהי QLoRA?

**QLoRA** משלבת **קוונטיזציה של 4 סיביות** עם **LoRA**. המודל הבסיסי נטען ב-4 סיביות (חיסכון גדול בזיכרון), ורק מתאמי ה-LoRA מאומנים בדיוק גבוה יותר. כך מתקבלת היעילות הפרמטרית של LoRA בתוספת שימוש נמוך משמעותית ב-VRAM, עם פשרה קטנה באיכות בהשוואה ל-LoRA בדיוק מלא. שימו לב שקוונטיזציה של 4 סיביות עלולה לגרום לחוסר יציבות נומרית (קפיצות אובדן (loss) או NaN), ולכן משתמשים לרוב מעדיפים **LoRA** כאשר יש מספיק VRAM זמין.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **הערה**: עבור מודלי בסיס MXFP4 כמו `openai/gpt-oss-20b`, אנו ממליצים להשתמש ב-**LoRA** (`train_lora.py`) במקום QLoRA. נתיב ה-4 סיביות של `bitsandbytes` בסקריפט ה-QLoRA בדרך כלל מבצע דה-קוונטיזציה של משקלי MXFP4 ל-BF16, כך שהריצה מתנהגת כמו LoRA סטנדרטית. MXFP4 מקורי דורש `bitsandbytes` שנבנתה מקוד המקור בתוספת מחסנית Transformers/Triton/kernels תואמת. ראו את [תיעוד MXFP4 של Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. בחירת השיטה שלכם

| שיטה | זיכרון | מהירות | איכות | מתאימה במיוחד עבור |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux בלבד) | 12-16GB | המהירה ביותר | 90-95% | שימוש נמוך בזיכרון |
| **LoRA** | 24-32GB | מהירה | 95-98% | גישה מאוזנת |
| **מלא (Full)** | 80GB+ | האיטית ביותר | 100% | איכות מרבית |
### 3. הרצת אימון

**מערך הנתונים ומה המודל לומד**  
הסקריפטים הופכים את מערך הנתונים לדוגמאות שיחה. לדוגמה, סקריפט ה-QLoRA משתמש ב-**Abirate/english_quotes**: כל דוגמה הופכת לזוג משתמש-עוזר כמו:

- **משתמש:** "תן לי ציטוט על: &lt;tag&gt;"
- **עוזר:** "&lt;quote&gt; – &lt;author&gt;"

כוונון עדין מלמד את המודל להגיב להנחיות המבקשות ציטוטים על נושא ולהחזיר אותם בפורמט `<quote text> - <author>`. סקריפטי ה-LoRA וכוונון עדין מלא משתמשים ב-**databricks/databricks-dolly-15k** (זוגות הוראה/תגובה כלליים), כך שהמשימה המדויקת משתנה בהתאם לסקריפט; הרעיון זהה - להתאים את המודל למערך הנתונים ולפורמט שבחרתם.

להלן סיכום של שיטות האימון הזמינות. כל שיטה מקושרת לסקריפט שלה ומספקת תיאור קצר לבחירת הגישה הנכונה.

| סקריפט                           | שיטה            | תיאור                                                                                                         | VRAM טיפוסי | מומלץ עבור                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | מאמן מטריצות מתאם קטנות תוך הקפאת המודל הבסיסי. מהיר פי 3–5; איכות של כ-95–98% מהמלאה.                         | 24–32GB      | משתמשים מתקדמים; מספר מתאמים; יותר VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux בלבד)*             | **QLoRA**       | קוונטיזציה ל-4 סיביות + מתאמי LoRA. שימוש הזיכרון הנמוך ביותר, המהיר ביותר, פשרת איכות קטנה. דורש `bitsandbytes` (Linux בלבד).                            | 12–16GB      | רוב המשתמשים; ניסויים מהירים; VRAM מוגבל      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **כוונון עדין מלא** | מעדכן את כל פרמטרי המודל. איכות מקסימלית; השימוש הגבוה ביותר בזיכרון וחישוב.                                    | 40GB+        | איכות מקסימלית; מחקר; VRAM גדול           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **הערה:** כוונון עדין מלא (`train_full_finetuning.py`) עשוי לדרוש יותר מ-64GB של זיכרון מערכת (RAM) וייתכן שלא יהיה ישים במכשיר זה. שקלו להשתמש במקום זאת ב-LoRA או QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה:** כוונון עדין מלא (`train_full_finetuning.py`) עשוי לדרוש יותר מ-64GB של זיכרון מערכת (RAM) וייתכן שלא יהיה ישים במכשיר זה. שקלו להשתמש במקום זאת ב-LoRA.
<!-- @os:end -->
<!-- @device:end -->

פשוט בחרו את `Training method` המועדפת עליכם, הורידו את הסקריפט המתאים והריצו אותו באמצעות הפקודה תוך שמירה על הסביבה הווירטואלית פעילה: 

```python
python3 train_<method_name>.py.
```

## שימוש במודל המכוונן שלכם

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

### מיזוג מתאם LoRA למודל הבסיסי

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**הערה:**  
- ודאו ששם ספריית המודל (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) תואם לתיקיית הפלט בפועל שלכם מהאימון.  
- אם השתמשתם ב-LoRA במקום QLoRA, פשוט החליפו את הנתיב בהתאם.  
- חלק ממודלי Gemma דורשים ציון `trust_remote_code=True` ב-`from_pretrained`; הוסיפו אם אתם רואים אזהרה רלוונטית.

להגדרות מותאמות אישית נוספות (טוקני ריפוד, מכשיר וכו'), עיינו בסקריפט בו השתמשתם לאימון.

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

**פורמט מערך נתונים לקובץ JSON/JSONL מקומי:**

בעת שימוש בשיטה זו, ודאו שקובצי ה-JSON שלכם בנויים כראוי כדי למנוע שגיאות ניתוח (parsing).

יש לפעול לפי ההנחיות הבאות:
* **עיצוב הקובץ:** יש לעצב קובצי JSON בתוך סביבת פיתוח משולבת (IDE) כדי להבטיח מבנה ותחביר תקינים.
* **מפתחות נדרשים:** קובץ ה-JSON המותאם אישית חייב להכיל את המפתחות `instruction` ו-`response`. מפתחות אלה חיוניים לפעולה תקינה של השיטה.
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
**פורמט מערך נתונים למערך נתונים מ-Hugging Face Hub**

בעת שימוש במערכי נתונים מ-Hugging Face, ודאו שמערכי הנתונים שלכם בנויים כראוי כדי לאפשר שילוב חלק.

יש לפעול לפי ההנחיות הבאות:
* **זוג הוראה-תגובה:** התמקדו במערכי נתונים הכוללים זוג `instruction-response`. מבנה זה חיוני לפעולה המיועדת.
* **שינוי מפתח מותאם אישית:** אם מערך הנתונים שלכם אינו תואם למבנה `instruction-response`, יש לכם אפשרות לשנות את הפונקציה `format_instruction()`. זה מאפשר לכם להתאים מפתחות ספציפיים לפי הצורך.

דוגמה להתאמה: במקרים בהם יש צורך להתאים את פלט מערך הנתונים, תוכלו לשנות את קטע התגובה בתוך הפונקציה format_instruction() כך שיתאים לדרישותיכם.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**פורמט מערך נתונים לקובץ CSV**

כדי להתאים את הסקריפט לשימוש בפורמט קובץ CSV, עליכם לוודא שקובץ ה-CSV מכיל עמודות בשם `instruction` ו-`response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### התאמת פרמטרי אימון

ערכו את סקריפט האימון ושנו את המשתנים בהתאם למטרותיכם: **קצב למידה** (`LR`), **אפוקים** (`EPOCHS`), **גודל אצווה** (`BATCH_SIZE`), **צבירת גרדיאנטים** (`GRAD_ACCUM_STEPS`), ועבור LoRA/QLoRA **דרגה** (`LORA_R`). להרצות מהירות יותר השתמשו בפחות אפוקים וקצב למידה (LR) גבוה יותר; לאיכות טובה יותר השתמשו ביותר אפוקים ו-LR נמוך יותר. הקטינו את גודל האצווה או אורך הרצף אם אתם נתקלים בשגיאות חוסר זיכרון.

### טיפים לאופטימיזציית זיכרון

אם אתם נתקלים בשגיאות חוסר זיכרון:

**1. הקטנת גודל האצווה:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. הקטנת אורך הרצף:**
```python
max_seq_length=256  # Instead of 512
```

**3. שימוש בקוונטיזציה אגרסיבית יותר:**
```
Full → LoRA → QLoRA
```

**4. הפעלת בדיקת גרדיאנטים (Gradient Checkpointing) (כוונון עדין מלא בלבד):**
```python
model.gradient_checkpointing_enable()
```

---

## ניטור וניפוי באגים

### מעקב אחר זיכרון GPU

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

בסקריפט האימון, הגדירו `report_to="wandb"` ובאופן אופציונלי `run_name="your-experiment-name"` בתצורת ה-trainer. אם אינכם מעוניינים להשתמש ב-Wandb, השאירו את `report_to` בערך ברירת המחדל שלו או הגדירו אותו כ-`"none"`.

### בעיות נפוצות

#### חוסר בזיכרון (OOM)

**פתרון:** הקטינו את גודל האצווה ו/או השתמשו ב-QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### הפסד שאינו יורד

**פתרון:** כווננו את קצב הלמידה
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

לאחר שהשלמתם בהצלחה את תהליך הכוונון העדין, שקלו את הצעדים הבאים כדי להפיק יותר מהמודל שלכם:

1. **הערכה** מקיפה על נתוני בדיקה מוחזקים כדי למדוד הכללה ולהימנע מהתאמת יתר.
2. **ניסוי** בערכי היפרפרמטרים שונים לקבלת פשרות טובות יותר בין דיוק, מהירות וזיכרון.
3. **מעקב** אחר כל הניסויים שלכם (והמדדים המתאימים) עם Weights & Biases למחקר בר-שחזור.
4. **ניסיון** אימון על מערכי נתונים מותאמים אישית משלכם כדי להתאים את המודל במיוחד למקרה השימוש שלכם.
5. **פריסה** של המודל המכוונן שלכם להסקה מהירה באמצעות backends יעילים כמו vLLM על חומרה תואמת.
6. **חקירה** של טכניקות מתקדמות כולל הנדסת פרומפטים, דיוק מעורב (mixed precision), ואורכי רצף ארוכים יותר.
7. **אימון** מספר מתאמי LoRA למשימות או תחומים שונים והחלפה ביניהם לפי הצורך.

---