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


רוצים להריץ מודלי שפה עוצמתיים של AI על החומרה שלכם? המדריך הזה מראה לכם איך.
מדריך זה משתמש ב-PyTorch, המופעל על ידי תוכנת AMD ROCm™, כדי להריץ מודלים שיכולים לסכם מסמכים, לענות על שאלות, לייצר טקסט ועוד, הכול ריצה מקומית.

## מה תלמדו

- הרצת מודלי LLM כמו gpt-oss-20b ו-qwen3.5-4B באופן מקומי באמצעות PyTorch ו-ROCm
- יצירת כלי לסיכום מסמכים באמצעות מודלי LLM

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה
> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
במערכת Linux, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv עם ROCm+Pytorch כבר מותקנים.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

במערכת Linux, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
במערכת Windows, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv עם ROCm+Pytorch כבר מותקנים.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
במערכת Windows, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרצה (Execution Policy) של PowerShell שלהם (למשל,
> להגדיר אותה ל-RemoteSigned או Unrestricted) לפני הרצת חלק מפקודות ה-Powershell.

<!-- @os:end -->

### התקנת תלויות בסיסיות
<!-- @require:driver,pytorch -->

### התקנת תלויות נוספות

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **הערה:** אם טעינת המודל נכשלת או אוזל הזיכרון, נסו להתקין את חבילת ה-`kernels` כדי לטעון את המודל עם קוונטיזציה מותאמת.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## התחלה מהירה עם סקריפטים לדוגמה

מדריך זה כולל סקריפטים מוכנים לשימוש. לחצו עליהם כדי לצפות ולהוריד אותם לאותה תיקייה כמו הסביבה שיצרתם.

| סקריפט | תיאור | שימוש |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | יצירת טקסט בסיסית באמצעות LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | מסכם מסמכים עם תמיכת Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

שני הסקריפטים תומכים ב:
- בחירת מודל באמצעות הדגל `--model`
- עיצוב תבנית שיחה (chat template) לניסוח הנחיות מדויק למודל, שימושי במיוחד לסיכום מסמכים

## טעינה והרצה של ה-LLM הראשון שלכם

הסקריפט המצורף [run_llm.py](assets/run_llm.py) מדגים כיצד ליצור טקסט עם מודלי LLM באמצעות PyTorch ו-AMD ROCm.

> **הערה:** כאשר אתם טוענים מודל, Hugging Face Transformers בודקת תחילה את המטמון המקומי שלה (`~/.cache/huggingface/hub` במערכת Linux, `C:\Users\<user>\.cache\huggingface\hub` במערכת Windows). אם המודל אינו נמצא במטמון, הוא מורד באופן אוטומטי מ-huggingface.co. הריצה הראשונה עשויה לקחת מספר דקות, בהתאם לגודל המודל ומהירות הרשת.

הקטע שלהלן מראה כיצד להשתמש במודל ולהתאים אישית את השאלות הנשאלות.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

נסו את הסקריפט שהורדתם:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## בניית מסכם מסמכים

עכשיו כשכבר יצרתם פלט LLM מקומי, תוכלו להמשיך משם על ידי בניית מסכם מסמכים מעשי. בסעיף זה תשתמשו בסקריפט [summarizer.py](assets/summarizer.py) כדי להזין קובץ txt. ולייצר באופן אוטומטי סיכום תמציתי, הכול ריצה מקומית על ה-GPU שלכם.

הסקריפט מיועד לעבוד מיד לאחר ההתקנה. פתחו את הסקריפט בעורך כדי לחקור את הקוד, להתאים אישית את ההנחיות (prompts), ולכוונן פרמטרים כמו אורך וטמפרטורה.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### דוגמאות שימוש

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## מידע על פרמטרי יצירה

| פרמטר | מה הוא שולט | ערכים אופייניים |
|-----------|------------------|----------------|
| `max_new_tokens` | האורך המקסימלי של פלט ה-LLM | השתמשו ב-50–500 טוקנים לסיכומים. (טוקן אחד שווה בערך ל-0.75 מילים באנגלית) |
| `temperature` | יצירתיות. ערכים נמוכים הופכים אותו למרוכז, בעוד ערכים גבוהים מביאים ליותר חוסר צפיות | - **0.1–0.3**: ממוקד, דטרמיניסטי (טוב לסיכומים) <br> **0.5–0.7**: מאוזן (שימוש כללי) <br> **0.8–1.0**: יצירתי, מגוון (סיעור מוחות) |
| `top_p` | דגימת גרעין (Nucleus Sampling) - ערכים נמוכים מגבילים את המודל לפלטים צרים יותר | **0.1-0.5**: מחמיר, צפוי <br> **0.9-0.95**: (סטנדרטי, טבעי, שיחתי) |


## יישומים בעולם האמיתי

- **ניתוח מאמרים אקדמיים**: חילוץ ממצאים מרכזיים מפרסומים מורכבים לסקירה מהירה
- **ריכוז חדשות**: סיכום כתבות חדשותיות לתקצירים או הדגשות יומיות קצרות
- **הערות פגישות**: תמצות תמלולים לפעולות נדרשות וסיכומים תמציתיים
- **סקירת מסמכים משפטיים**: חילוץ סעיפים או התחייבויות רלוונטיים מטקסטים משפטיים ארוכים במהירות
- **תיעוד קוד**: יצירת סקירות מאגר תמציתיות והסברי פונקציות
## הצעדים הבאים

- **Fine-tuning**: התאמת מודלים לתחום או לז'רגון הספציפי שלכם לצורך דיוק טוב יותר (ראו Fine-tuning Playbooks)
- **מערכות RAG**: שילוב LLMs עם אחזור מסמכים לקבלת תשובות וחיפוש מודעי-הקשר
- **חקר מודלים**: התנסות במודלים חדשים כמו Llama 3, Phi-3 או Qwen לתוצאות טובות יותר
- **פריסה בסביבת ייצור**: שימוש בכלים כמו vLLM לשירות LLM ניתן להרחבה בארגונים

המערכת שלכם מעניקה לכם את היכולת להריץ מודלי שפה מתוחכמים באופן מקומי. התנסו במודלים, פרומפטים ופרמטרים שונים כדי לגלות מה עובד הכי טוב עבור היישומים שלכם.