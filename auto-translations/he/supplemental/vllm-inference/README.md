<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> מדריך זה משתמש בתגיות מיוחדות ש-GitHub אינו יכול לעבד. יש לבקר בכתובת [amd.com/playbooks](https://amd.com/playbooks) כדי לצפות בתוכן זה כראוי.
<!-- @github-only:end -->


## סקירה כללית

vLLM הוא מנוע היסק בעל ביצועים גבוהים המיועד למודלי שפה גדולים (LLMs). הוא מספק הגשה מותאמת עם קיבוץ רציף (continuous batching) לתפוקה גבוהה וממשק API תואם OpenAI לשילוב חלק עם אפליקציות. בזכות זה, vLLM מתאים במיוחד לפריסות ייצור שבהן מהירות ויעילות במשאבים הם קריטיים.

מדריך זה מלמד אתכם כיצד להגיש מודלי שפה גדולים באמצעות vLLM בקונטיינר על ה-GPU המשולב, וכיצד לתקשר עם המודלים דרך ה-OpenAI Python API.

## מה תלמדו

- כיצד להגדיר ולהפעיל שרת vLLM עם תמיכת AMD ROCm™
- כיצד לתקשר עם מודלים דרך נקודות קצה של API תואמות OpenAI
- כיצד לשלוח בקשות (prompts) לשרת המקומי באמצעות `vllm-prompt`

## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

> **הערה**: אם VS Code אינו מותקן, ניתן להתקין אותו באמצעות AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

מדריך זה משתמש בתמונת קונטיינר בנויה מראש הכוללת את vLLM, תמיכת ROCm, וסקריפטי העזר הדרושים להפעלת השרת. אין צורך להתקין את PyTorch, vLLM, או סקריפטים מקומיים של המדריך באופן ידני.

אין שלב התקנה של vLLM בצד המארח. הפעילו את vLLM באמצעות:

```bash
vllm-launch
```

המשגר מפעיל את הקונטיינר, מכוון ל-GPU המשולב, וחושף שרת vLLM מקומי תואם OpenAI. לחלופין, ניתן ללחוץ על סמל vLLM בשורת המשימות.

## התחלה מהירה

### 1. ודאו ששרת vLLM פועל

הרצת `vllm-launch` עשויה לקחת מספר דקות לאתחל את הכול. לאחר שהוא מתחיל לפעול, השרת זמין בכתובת `http://localhost:8001`. השאירו את מסוף ההפעלה פתוח מכיוון שהשרת פועל בחזית (foreground), ולאחר מכן פתחו מסוף נפרד עבור השלבים הנותרים. הדוגמאות למטה משתמשות ב-`Qwen/Qwen3-1.7B`; אם המשגר שלכם מוגדר עבור מודל אחר, החליפו את מזהה המודל הזה בבקשות.

### 2. שלחו בקשה (Prompt)

השתמשו בסקריפט `vllm-prompt` שסופק כדי לשלוח בקשה לשרת ה-vLLM המקומי התואם OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. שוחחו עם המודל באמצעות OpenAI Python API

מכיוון ש-vLLM חושף API תואם OpenAI, ניתן להשתמש בחבילת ה-Python בשם `openai` כדי לתקשר איתו.

תחילה, צרו סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

התקינו את חבילת ה-OpenAI
```bash
pip install openai
```

צרו לקוח `OpenAI` המצביע לשרת ה-vLLM המקומי במקום לשרתי OpenAI. המפתח `api_key` נדרש על ידי הלקוח אך vLLM אינו מאמת אותו, כך שכל מחרוזת תעבוד:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

לאחר מכן, שלחו בקשת השלמת שיחה (chat completion). זו משתמשת באותו פורמט הודעות כמו ה-API של OpenAI — רשימת הודעות עם תפקידים כגון `"user"` ו-`"assistant"`. הגדרת `stream=True` משמעה שהתשובה תגיע בהדרגה ולא בבת אחת:

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

לבסוף, עברו על מקטעי הזרם (streamed chunks) והדפיסו כל חלק טקסט ברגע שהוא מגיע:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

הסקריפט המצורף [chat_with_model.py](assets/chat_with_model.py) מכיל את הדוגמה המלאה וניתן להורדה.


## פתרון בעיות

### החיבור נדחה (Connection refused)

ודאו שהשרת פועל:
```bash
curl http://localhost:8001/health
```

## סיכום

במדריך זה למדתם כיצד:

- להפעיל את vLLM בקונטיינר עם תמיכת ROCm על ה-GPU המשולב
- להפעיל שרת vLLM עם נקודות קצה API תואמות OpenAI בפורט 8001
- לשלוח בקשות (prompts) באמצעות `vllm-prompt`
- לבצע קריאות API לשרת vLLM באמצעות בקשות עם וללא זרימה (streaming)
- לפתור בעיות נפוצות בהפעלת השרת, בזיכרון, ובחיבורי לקוח

כעת יש לכם פריסת vLLM בקונטיינר להגשת מודלי שפה גדולים עם ביצועים מותאמים על ה-GPU המשולב.

## השלבים הבאים

- **נסו מודלים שונים** — החליפו את המודל בתצורת `vllm-launch` כדי להתנסות במודלי שפה גדולים שונים ולהשוות ביצועים.
- **בנו אפליקציה** — השתמשו ב-API התואם OpenAI כדי לשלב את vLLM באפליקציית Python, בוט צ'אט, או תהליך עבודה אוטומטי.
- **כווננו והגישו** — כווננו מודל (fine-tune) באמצעות LoRA או QLoRA, ולאחר מכן פרסו אותו עם vLLM להיסק מותאם.

## משאבים נוספים

- **[תיעוד רשמי של vLLM](https://docs.vllm.ai/)** — מדריכים מקיפים והפניות ל-API
- **[מאגר GitHub של vLLM](https://github.com/vllm-project/vllm)** — קוד מקור, בעיות, ודיונים קהילתיים