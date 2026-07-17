<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## סקירה כללית

vLLM הוא מנוע הסקה בעל ביצועים גבוהים המיועד למודלי שפה גדולים (LLMs). הוא מספק שירות מותאם עם אצווה רציפה לתפוקה גבוהה וממשק API תואם OpenAI לאינטגרציה חלקה עם יישומים. זה הופך את vLLM למצוין לפריסות ייצור שבהן מהירות ויעילות משאבים הן קריטיות.

מדריך זה מלמד אותך כיצד להגיש LLMs באמצעות vLLM בקונטיינר על ה-GPU המשולב ולתקשר עם מודלים דרך ממשק ה-Python API של OpenAI.

## מה תלמד

- כיצד להגדיר ולהפעיל שרת vLLM עם תמיכה ב-AMD ROCm™
- כיצד לתקשר עם מודלים דרך נקודות קצה של API תואם OpenAI
- כיצד לשלוח פרומפטים לשרת המקומי עם `vllm-prompt`

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו עם AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

מדריך זה משתמש בתמונת קונטיינר מוכנה מראש הכוללת את vLLM, תמיכה ב-ROCm ואת סקריפטי העזר הדרושים להפעלת השרת. אין צורך להתקין את PyTorch, vLLM או סקריפטי מדריך מקומיים באופן ידני.

אין שלב התקנת vLLM בצד המארח. הפעל את vLLM עם:

```bash
vllm-launch
```

המפעיל מאתחל את הקונטיינר, מכוון ל-GPU המשולב וחושף שרת vLLM מקומי תואם OpenAI. לחלופין, לחץ על סמל vLLM בשורת המשימות.

## התחלה מהירה

### 1. אמת שהשרת vLLM פועל

ל-`vllm-launch` עשויות לקחת כמה דקות לאתחל הכל. לאחר שהוא מתחיל, השרת זמין בכתובת `http://localhost:8001`. השאר את טרמינל ההפעלה פתוח מכיוון שהשרת פועל בחזית, ולאחר מכן פתח טרמינל נפרד לשלבים הנותרים. הדוגמאות שלהלן משתמשות ב-`Qwen/Qwen3-1.7B`; אם המפעיל שלך מוגדר למודל אחר, החלף את מזהה המודל הזה בבקשות.

### 2. שלח פרומפט

השתמש בסקריפט `vllm-prompt` המסופק כדי לשלוח בקשה לשרת vLLM המקומי התואם OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. שוחח עם המודל באמצעות ממשק ה-Python API של OpenAI

מכיוון ש-vLLM חושף API תואם OpenAI, ניתן להשתמש בחבילת ה-Python של `openai` כדי לתקשר איתו.

ראשית, צור סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

התקן את חבילת OpenAI
```bash
pip install openai
```

צור לקוח `OpenAI` המכוון לשרת vLLM המקומי במקום לשרתי OpenAI. ה-`api_key` נדרש על ידי הלקוח אך vLLM אינו מאמת אותו, כך שכל מחרוזת תעבוד:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

לאחר מכן, שלח בקשת השלמת צ'אט. זה משתמש באותו פורמט הודעות כמו ממשק ה-API של OpenAI — רשימת הודעות עם תפקידים כמו `"user"` ו-`"assistant"`. הגדרת `stream=True` פירושה שהתגובה תגיע בצורה מצטברת ולא כולה בבת אחת:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

לבסוף, עבור על פני הנתחים המוזרמים והדפס כל חלק של טקסט כשהוא מגיע:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

הסקריפט [chat_with_model.py](assets/chat_with_model.py) הכלול מכיל את הדוגמה המלאה וניתן להוריד אותו.


## פתרון בעיות

### חיבור נדחה

ודא שהשרת פועל:
```bash
curl http://localhost:8001/health
```

## סיכום

במדריך זה, למדת כיצד:

- להפעיל vLLM בקונטיינר עם תמיכה ב-ROCm על ה-GPU המשולב
- להפעיל שרת vLLM עם נקודות קצה של API תואם OpenAI על פורט 8001
- לשלוח פרומפטים עם `vllm-prompt`
- לבצע קריאות API לשרת vLLM באמצעות בקשות מוזרמות ולא מוזרמות כאחד
- לפתור בעיות נפוצות עם הפעלת שרת, זיכרון וחיבורי לקוח

כעת יש לך פריסת vLLM בקונטיינר להגשת מודלי שפה גדולים עם ביצועים מותאמים על ה-GPU המשולב.

## השלבים הבאים

- **נסה מודלים שונים** — החלף את המודל בתצורת `vllm-launch` כדי להתנסות עם LLMs שונים ולהשוות ביצועים.
- **בנה יישום** — השתמש ב-API התואם OpenAI כדי לשלב את vLLM ביישום Python, צ'אטבוט או זרימת עבודה אוטומטית.
- **כוונן עדין והגש** — כוונן עדין מודל באמצעות LoRA או QLoRA, ולאחר מכן פרוס אותו עם vLLM להסקה מותאמת.

## משאבים נוספים

- **[תיעוד רשמי של vLLM](https://docs.vllm.ai/)** — מדריכים מקיפים ועיון ב-API
- **[מאגר vLLM ב-GitHub](https://github.com/vllm-project/vllm)** — קוד מקור, בעיות ודיוני קהילה