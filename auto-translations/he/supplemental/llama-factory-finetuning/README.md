<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

## סקירה כללית

כוונון עדין (fine-tuning) יעיל הוא חיוני להתאמת מודלי שפה גדולים (LLMs) למשימות ייעודיות. LLaMA Factory היא פלטפורמה בקוד פתוח וידידותית למשתמש, המייעלת את תהליך האימון והכוונון העדין של מודלי שפה גדולים ומודלים מולטימודליים. היא מאפשרת למשתמשים להתאים אישית מאות מודלים מאומנים מראש באופן מקומי עם כתיבת קוד מינימלית.

מדריך זה מלמד אתכם כיצד לכוונן עדין מודלי LLM באמצעות LLaMA Factory על חומרת AMD המקומית שלכם.

<!-- @device:stx,krk -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **32 GB זיכרון RAM של המערכת**, מתוכם לפחות **16 GB זמינים ל-GPU** (16 ה-GB הללו הם חלק מ-32 ה-GB, ולא בנוסף להם).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות לפחות **16 GB של סך זיכרון GPU** ו-**32 GB זיכרון RAM של המערכת**.
> - במערכת Windows, סך זיכרון ה-GPU משלב את ה-VRAM הייעודי של כרטיס הגרפיקה עם זיכרון GPU משותף (מושאל מזיכרון ה-RAM של המערכת).
> - לכן, כרטיסים עם פחות מ-16 GB VRAM ייעודי עדיין יכולים להריץ מדריך זה באמצעות שימוש בזיכרון GPU משותף כדי להשלים את ההפרש.
<!-- @os:end -->

<!-- @os:linux -->
> **הערה:** טכניקות הכוונון העדין במדריך זה דורשות כרטיס גרפיקה עם לפחות **16 GB זיכרון GPU ייעודי** ו-**32 GB זיכרון RAM של המערכת**.
> - במערכת Linux, האימון פועל כולו בתוך ה-VRAM הייעודי של כרטיס הגרפיקה.
> - הוא אינו חוזר לזיכרון GPU משותף (זיכרון RAM של המערכת) כאשר ה-VRAM אוזל.
> - כרטיסים עם פחות מ-16 GB VRAM ייעודי ייגמר להם הזיכרון במהלך האימון על Linux, גם אם למערכת יש הרבה RAM פנוי.
<!-- @os:end -->
<!-- @device:end -->

## מה תלמדו

- כיצד להגדיר את LLaMA Factory עם תוכנת AMD ROCm™
- כיצד להגדיר פרמטרי כוונון עדין למודלי LLM (באמצעות Qwen/Qwen3-4B-Instruct-2507 כדוגמה)
- כיצד להריץ כוונון עדין באמצעות LLaMA Factory
- כיצד להריץ הסקה (inference) עם המודל שכוונן
- כיצד לייצא את המודל שכוונן 

## זמן משוער

- משך זמן: יידרשו כ-60 דקות להרצת מדריך זה (בהתאם לגודל המודל/מערך הנתונים שלכם ומהירות הרשת).
- ראו [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) למידע נוסף.

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
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
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### התקנת תלויות בסיסיות

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

### התקנת תלויות נוספות

> **הערה**: ודאו שגרסת Python היא 3.11, 3.12, או 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### התקנת LLaMA Factory

LLaMA Factory תלויה ב-PyTorch. אמור להיות לכם כבר מותקן בהתאם לדרישות שלעיל.

הורידו את קוד המקור מ[מאגר ה-GitHub הרשמי של LLaMA Factory](https://github.com/hiyouga/LlamaFactory), והתקינו את התלויות שלו.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

ודאו שהקובץ `llamafactory-cli` ניתן להרצה.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

דוגמה לפלט:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

לאחר שהתקנתם בהצלחה את LLaMA Factory, בואו נריץ כוונון עדין עליה.

## שימוש בממשק שורת הפקודה של LLaMA Factory לכוונון עדין 

חלק זה יסקור כיצד להכין מערכי נתונים לכוונון עדין, להגדיר פרמטרי LoRA/QLoRA, ולהריץ כוונון עדין בשיטת LoRA.

### הכנת מערך הנתונים

LLaMA Factory תומכת במערכי נתונים לכוונון עדין בפורמט Alpaca ובפורמט ShareGPT. כל מערכי הנתונים הזמינים הוגדרו בקובץ [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). אם אתם משתמשים במערך נתונים מותאם אישית, ודאו להוסיף תיאור מערך נתונים בקובץ `dataset_info.json` ולציין את שם מערך הנתונים לפני האימון. ניתן למצוא פרטים נוספים בתיעוד שלהם [כאן](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

במדריך זה, נשתמש במערכי הנתונים identity ו-alpaca_en_demo כדוגמה, ונגדיר את מידע מערך הנתונים בשלב הבא.
### הגדרת פרמטרים לכוונון עדין (Fine-tuning)

LLaMA Factory תומכת במספר סכימות כוונון עדין.

| סכימות כוונון עדין | דוגמאות LLaMA Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| כוונון עדין LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| כוונון עדין QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

קובצי תצורה לדוגמה אלה מגדירים פרמטרים של המודל, פרמטרים של שיטת הכוונון העדין, פרמטרים של מערך הנתונים, פרמטרים של הערכה ועוד. ניתן להתאים אותם בהתאם לצרכים שלכם. במדריך זה נשתמש בקובץ [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**הסבר על הפרמטרים העיקריים:**
- `model_name_or_path` - שם המודל ב-Hugging Face או נתיב לקובץ מודל מקומי.
- `stage` - שלב האימון. אפשרויות: rm (מידול תגמול), pt (אימון מקדים), sft (כוונון עדין מונחה), PPO, DPO, KTO, ORPO.
- `do_train` - true עבור אימון, false עבור הערכה
- `finetuning_type` - שיטת הכוונון העדין. אפשרויות: freeze, lora, full
- `lora_rank` - המימד של מטריצת הדרגה הנמוכה (low-rank) הנעשה בה שימוש בשיטת LoRA, ערכים אופייניים: 4, 6, 8, 16 (ערכים קטנים יותר = פחות פרמטרים = כוונון עדין מהיר יותר; ערכים גדולים יותר = התאמה טובה יותר למשימה אך שימוש גבוה יותר במשאבים).
- `lora_target` - מודולי היעד עבור שיטת LoRA. ברירת מחדל: all.
- `dataset` - מערך(י) הנתונים לשימוש. יש להשתמש ב-"," להפרדה בין מספר מערכי נתונים
- `output_dir` - נתיב הפלט של הכוונון העדין
- `logging_steps` - מרווח רישום הלוגים בצעדים
- `save_steps` - מרווח שמירת נקודות ביקורת (checkpoint) של המודל.
- `overwrite_output_dir` - האם לאפשר דריסה של תיקיית הפלט.
- `per_device_train_batch_size` - גודל אצווית האימון (batch) עבור כל התקן.
- `gradient_accumulation_steps` - מספר צעדי צבירת הגרדיאנטים.
- `learning_rate` - קצב הלמידה
- `num_train_epochs` - מספר תקופות האימון (epochs)
- `lr_scheduler_type` - לוח זמנים של קצב הלמידה. אפשרויות: linear, cosine, polynomial, constant וכו'.
- `warmup_ratio` - יחס ההתחממות (warmup) של קצב הלמידה

<!-- @os:linux -->
נשנה את ערך ברירת המחדל של `lora_rank` כדי להריץ כוונון עדין על GPU‏‏ מסוג AMD Ryzen™ ו-AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
נעדכן את תצורת ברירת המחדל של כוונון עדין LoRA לשם תאימות טובה יותר עם GPU‏‏ מסוג AMD Ryzen™ ו-AMD Radeon™:
- נשנה את `lora_rank` מ-`8` ל-`6` כדי להפחית את השימוש בזיכרון במהלך הכוונון העדין.
- נשתמש ב-`fp16` במקום ב-`bf16` לתאימות רחבה יותר עם GPU‏‏ מסוג AMD ולשימוש נמוך יותר בזיכרון.
- נגדיר את `dataloader_num_workers` לערך `0` במערכת Windows כדי למנוע שגיאות מסוג `"Can't pickle local object<>"` הנגרמות עקב טעינת נתונים מרובת תהליכים (multiprocessing).

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### הרצת כוונון עדין עם LLaMA Factory 

**llamafactory-cli** הוא כלי שורת הפקודה (CLI) הרשמי עבור LLaMA Factory, שפותח כדי לפשט תהליכי עבודה מקצה לקצה עם מודלי שפה גדולים (הכנת נתונים ← כוונון עדין ← הערכה ← פריסה) ללא צורך בכתיבת קוד מורכב.

עבור אימון/כוונון עדין, **llamafactory-cli train** היא תת-הפקודה המרכזית של ה-CLI של LLaMA Factory. היא מכלילה תהליכי כוונון עדין (עיבוד מקדים של נתונים, כוונון היפר-פרמטרים, אופטימיזציית חומרה) בפקודת CLI אחת, תומכת במספר פרדיגמות כוונון עדין (LoRA/QLoRA/Full Fine-Tuning) ומותאמת עבור GPU‏‏ עם משאבים מוגבלים (לדוגמה, QLoRA עם 16GB VRAM).

ניתן להריץ כוונון עדין עם LLaMA Factory באמצעות הפקודה הבאה, המבוססת על קובץ התצורה המעודכן של כוונון עדין LoRA עבור Qwen3.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

לאחר הרצת הכוונון העדין של מודל השפה הגדול, כל הפלטים שנוצרו נשמרים בתוך "output_dir", כולל קובצי נקודות ביקורת (checkpoint) של המודל, קובצי תצורה ומדדי אימון.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### בדיקת המודל המכוון עדין

**llamafactory-cli chat** מיועדת לצ'אט/הסקה אינטראקטיביים עם מודלי שפה גדולים (הן מודלי בסיס והן מודלים מכווני עדין בשיטת LoRA). LLaMA Factory מספקת תצורה לדוגמה להרצת הסקה של מודלים מכווני עדין תחת [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). ניתן גם לשנות תצורה זו כדי לשנות הגדרות, כגון מנוע ההסקה.

השתמשו בפקודה הבאה כדי לבדוק את המודל המכוון עדין של Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
דוגמה לצ'אט באמצעות המודל המכוון עדין מוצגת להלן:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### ייצוא המודל המכוון עדין

עבור מקרי שימוש בייצור, יש למזג את המודל המאומן מראש עם מתאם ה-LoRA ולייצא אותם כמודל יחיד. ניתן להשתמש במודל הממוזג הזה כקובץ מודל רגיל של Hugging Face. LLaMA Factory מספקת תצורות לדוגמה תחת [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

השתמשו בפקודה הבאה כדי לייצא את המודל המכוון עדין של Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
התוצאה של ייצוא המודל המכוון עדין מוצגת להלן.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end -->
## שימוש בממשק הגרפי (GUI) של LLaMA Factory

`LLaMA-Factory` תומך גם בכוונון עדין (fine-tuning) של מודלי שפה גדולים ללא כתיבת קוד, באמצעות ממשק משתמש מבוסס דפדפן (web UI).

יש להשתמש בפקודה הבאה כדי לפתוח אותו:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` מציע ממשק פשוט ונוח לניהול תהליכי עבודה של למידת מכונה, כולל אימון, הערכה, חיזוי, שיחה וייצוא מודלים. להלן הסבר קצר על כל לשונית:

* **Train**: לשונית זו מאפשרת לבחור מודל ומערך נתונים, להגדיר את פרמטרי האימון ולהתחיל בתהליך האימון. חשוב להכיר את הפרמטרים החובה והאופציונליים כדי לייעל את הגדרות האימון.
* **Evaluate & Predict**: לאחר האימון, ניתן להעריך את ביצועי המודל ולבצע חיזויים באמצעות לשונית זו. היא מספקת תובנות לגבי הדיוק והיעילות של המודל על נתונים חדשים.
* **Chat**: לאחר סיום האימון, ניתן לטעון את המודל בלשונית Chat כדי ליצור איתו אינטראקציה ולראות את תוצאות העבודה. תכונה זו מאפשרת תקשורת בזמן אמת עם המודל המאומן.
* **Export**: לשונית זו מאפשרת לייצא מודלים מאומנים לפריסה (deployment) או לשימוש נוסף. ניתן לשמור את המודלים בפורמטים שונים המתאימים ליישומים שונים.

לקבלת הנחיות מפורטות, מומלץ לעיין בתיעוד הרשמי במאגר [LlamaFactory ב-GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) ובאתר [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). בנוסף, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) מספק תובנות שימושיות לגבי הממשק ופונקציונליות שלו.

## השלבים הבאים
- נסו מודלים שונים כגון `gpt-oss` ומודלים מתקדמים נוספים.
- התנסו עם backends שונים על המודל שעבר כוונון עדין

למידע נוסף, ניתן לבקר בכתובת: https://llamafactory.readthedocs.io/en/latest/