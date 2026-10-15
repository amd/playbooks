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

מדריך זה מראה כיצד לבצע כוונון עדין (fine-tuning) של מודל שפה באופן מקומי באמצעות Unsloth על חומרת AMD.

הוא משתמש בדוגמת כוונון עדין מפוקח (Supervised Fine-Tuning - SFT) קצרה עם מתאמי LoRA על `unsloth/gemma-4-E4B-it`, תוך שימוש בתת-קבוצה של מערך הנתונים `mlabonne/FineTome-100k`. המטרה היא לספק לך תהליך עבודה פשוט מקצה לקצה שמכסה הגדרה, אימון, היסק ושמירה של התוצאה המכוונת.

הדוגמה תוכננה להיות מעשית וקלה לשינוי, כך שתוכל להשתמש בה כנקודת התחלה עבור מערכי הנתונים והמודלים שלך.

## מה תלמד

- כיצד להגדיר את סביבת Unsloth
- כיצד לבצע כוונון עדין ל-LLM באמצעות SFT עם Unsloth
- כיצד לשמור את התוצאה המכוונת באחסון מקומי

<!-- @device:halo,stx,krk -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **64 GB של זיכרון RAM של המערכת**, כאשר לפחות **24 GB מתוכם זמינים ל-GPU** (24 GB אלה הם חלק מ-64 GB, לא בנוסף להם).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **24 GB של זיכרון GPU כולל** ו-**32 GB של זיכרון RAM של המערכת**.
> - ב-Windows, זיכרון ה-GPU הכולל משלב את ה-VRAM הייעודי של כרטיס הגרפיקה עם זיכרון GPU משותף (מושאל מזיכרון ה-RAM של המערכת).
> - לכן, כרטיסים עם פחות מ-24 GB של VRAM ייעודי עדיין יכולים להריץ מדריך זה באמצעות שימוש בזיכרון GPU משותף כדי להשלים את ההפרש.
<!-- @os:end -->

<!-- @os:linux -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות כרטיס גרפי עם לפחות **24 GB של זיכרון GPU ייעודי** ו-**32 GB של זיכרון RAM של המערכת**.
> - ב-Linux, האימון פועל כולו בזיכרון ה-VRAM הייעודי של כרטיס הגרפיקה.
> - הוא אינו חוזר לזיכרון GPU משותף (זיכרון RAM של המערכת) כאשר ה-VRAM אוזל.
> - כרטיסים עם פחות מ-24 GB של VRAM ייעודי ייגמר להם הזיכרון במהלך האימון ב-Linux, גם אם למערכת יש הרבה זיכרון RAM.
<!-- @os:end -->
<!-- @device:end -->

## מדוע Unsloth?

Unsloth הופך את הכוונון העדין של LLM לקל יותר להרצה על חומרה מקומית על ידי הפחתת השימוש בזיכרון והאצת האימון בהשוואה להגדרה סטנדרטית.

במדריך זה, אנו משתמשים ב-Unsloth יחד עם **SFT מבוסס LoRA**. משמעות הדבר היא שהמודל הבסיסי נשאר קפוא ברובו, בעוד שקבוצה קטנה בהרבה של משקלי מתאמים מאומנת. זוהי התאמה טובה לפיתוח מקומי מכיוון שהיא קלה יותר מכוונון עדין מלא ומהירה יותר לביצוע איטרציות.

Unsloth תומכת גם בגישות אימון נוספות, כולל QLoRA ותהליכי עבודה של למידת חיזוק. מדריך זה מתמקד תחילה בנתיב הפשוט ביותר: דוגמת כוונון עדין קטנה של LoRA שמשתמשים יכולים להריץ, להבין ולהרחיב.

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

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
פתח מסוף וצור venv עם תוכנת AMD ROCm™ ו-PyTorch כבר מותקנים:
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
**הענק לחשבון המשתמש שלך גישה להתקני GPU** (התנתק והתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

פתח מסוף וצור venv:
<!-- @test:id=create-venv timeout=300 -->
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
> **הערה:** נדרש Python 3.13 עבור Windows.

<!-- @device:halo_box -->
פתח מסוף PowerShell וצור סביבה וירטואלית:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
פתח מסוף PowerShell וצור סביבה וירטואלית:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### התקנת תלויות בסיסיות
<!-- @require:driver -->

> **חשוב:** Unsloth עדיין אינה תומכת בגרסת PyTorch 2.13 שמגיעה עם ROCm 10. עבור מדריך זה, התקן **ROCm 7.14 עם PyTorch 2.12** באמצעות הפקודות שלהלן. אל תשתמש בחבילות ROCm 10 / PyTorch 2.13.

**התקן את PyTorch עם תמיכת תוכנת AMD ROCm™** בסביבה הווירטואלית שנוצרה:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

עבור התקנים אחרים, נא עיין ב-[תיעוד ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) לקבלת הוראות מלאות.

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

### תלויות נוספות

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **הערה:** במהלך הייבוא, Unsloth עשויה לבדוק נתיבי האצה אופציונליים של `bitsandbytes`. בגרסאות ROCm מסוימות, ייתכן שתראה הודעה כגון `bitsandbytes library load error: Configured ROCm binary not found`. מדריך זה משתמש בכוונון עדין סטנדרטי של LoRA עם `optim="adamw_torch"`, כך שאיננו מסתמכים על האופטימייזר של `bitsandbytes` או על QLoRA בן 4 סיביות. ניתן להתעלם בבטחה מהודעה זו.

<!-- @os:windows -->
> **הערה:** ב-Windows ROCm, Unsloth תדפיס מספר אזהרות בעת ההפעלה — ראה [אזהרות ידועות](#known-warnings) למטה. ניתן להתעלם מכולן בבטחה; האימון פועל כראוי.
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

## הורדת סקריפט הכוונון העדין של Unsloth

במקום לבצע כל שלב באופן ידני, מדריך זה מספק סקריפט נקי מקצה לקצה כאן: [test_unsloth.py](assets/test_unsloth.py).

הרץ את הקוד הבא כדי להריץ את הסקריפט:

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

יתר המדריך יעבור באופן מושגי על כל שלב מרכזי בסקריפט.

## כיצד זה עובד

הסקריפט test_unsloth.py מבצע את השלבים הבאים:
* **טעינת מודל**: טוען את unsloth/gemma-4-E4B-it באמצעות FastModel.
* **הכנת נתונים**: מתקנן את מערך הנתונים (למשל, FineTome-100k) ומחיל את תבנית הצ'אט של Gemma-4.
* **החלת LoRA**: מוסיף מתאמים למודולי שפה, תשומת לב (attention) ו-MLP לצורך אימון יעיל.
* **אימון**: משתמש ב-SFTTrainer עם מיסוך הפסד (loss masking) של תגובה בלבד.
* **היסק**: מריץ בדיקת ייצור מהירה כדי לאמת ביצועים.
* **שמירה**: מייצא מתאמי LoRA באופן מקומי.
## הגדרות תצורה עיקריות

ניתן לשנות את הקבועים הבאים כדי להתאים אישית את הריצה:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

דוגמה להודעת הפתיחה של Unsloth ולפלט בעת טעינת משקלי המודל:

![alt text](assets/welcome.png)

## הכנת מערך הנתונים

אנו משתמשים בתת-קבוצה של:
```text
mlabonne/FineTome-100k
```
מערך הנתונים:
* מומר לפורמט צ'אט
* מעובד באמצעות תבנית הצ'אט Gemma-4
* מנוקה כדי להסיר אסימוני BOS כפולים

## אימון המודל

הסקריפט מריץ הדגמת אימון קצרה, עם הפרמטרים הבאים:
- כ-50 שלבים
- גודל אצווה קטן
- צבירת גרדיאנטים

במהלך האימון, יופיעו יומני רישום כגון:

![alt text](assets/training.png)


## שמירה ופריסה

### שמירה מקומית (LoRA)

הסקריפט שומר אוטומטית את מתאמי LoRA לתוך OUTPUT_DIR.
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

### שמירת מודל ממוזג (עבור vLLM)

<!-- @os:windows -->
> **הערה:** vLLM אינו תומך ב-Windows. כדי לפרוס את המודל המכוונן על Windows, השתמשו ב-llama.cpp (ראו [ייצוא GGUF](#export-gguf-for-llamacpp) בהמשך) או העבירו את המודל הממוזג למחשב Linux המריץ vLLM.
<!-- @os:end -->

<!-- @os:linux -->
לפריסה עם vLLM, מזגו את המתאמים למודל מלא:
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

### ייצוא GGUF (עבור llama.cpp)

המרה ישירה ל-GGUF להסקה מקומית:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## אזהרות ידועות

אזהרות אלו מודפסות על ידי Unsloth בעת ההפעלה ב-Windows ROCm וניתן להתעלם מכולן בבטחה:

| אזהרה | סיבה | בטוח להתעלם? |
|---|---|---|
| `bitsandbytes library load error` | ל-bitsandbytes אין בנייה עבור Windows ROCm | כן — מדריך זה משתמש ב-`adamw_torch`, לא ב-bnb |
| `No ROCm platform found for torch.distributed` | ל-ROCm על Windows חסרה תמיכה באימון מבוזר | כן — אימון על GPU בודד אינו מושפע |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth מסמן בניות שאינן Linux | כן — Windows ROCm עובד עבור SFT על GPU בודד |
| `triton is not available` | ל-Triton אין בנייה עבור Windows | כן — Unsloth חוזר לשימוש בקרנלים של PyTorch |

האימון יתבצע כראוי למרות אזהרות אלו.
<!-- @os:end -->

## הצעדים הבאים
- נסו את [Unsloth Studio](https://unsloth.ai/docs/new/studio), ממשק גרפי אינטואיטיבי עבור Unsloth
- אמנו על מערכי נתונים ספציפיים משלכם
- נסו כוונון עדין עם היפרפרמטרים שונים
- פרסו עם vLLM או llama.cpp
- נסו QLoRA להגדרה בעלת צריכת זיכרון נמוכה יותר

## משאבים

להלן כמה משאבים נוספים ללמידה נוספת על Unsloth וכוונון עדין:

* [תיעוד Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [מדריך הכוונון העדין של Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)