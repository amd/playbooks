<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

LM Studio הוא עטיפה גרפית (GUI) עוצמתית עבור [llama.cpp](https://github.com/ggml-org/llama.cpp) ומספק גם [נקודת קצה תואמת OpenAI](https://lmstudio.ai/docs/developer/openai-compat) לשירות מודלים מקומי. LM Studio מציע ממשק פשוט אך עוצמתי להורדה ופריסה קלה של מודלים. LM Studio מציע גם backends של Vulkan וגם של AMD ROCm™ (הנקראים runtimes) עבור משתמשי AMD.


## מה תלמד
- כיצד להגדיר ולהשתמש ב-LM Studio כדי למנף את החומרה המקומית שלך
- לבדוק ולנהל מודלי LLM בסביבה לא מקוונת לחלוטין
- לשרת מודלים דרך API תואם OpenAI כדי להניע תהליכי עבודה ואפליקציות מותאמות אישית


## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @os:linux -->
> **הערה**: ניתן להתקין את VS Code דרך AMD Ryzen™ AI Developer Center. עבור LM Studio, יש לפעול לפי הוראות ההתקנה שלהלן.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: אם VS Code או LM Studio אינם מותקנים, ניתן להתקין אותם מ-AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## הורדת מודלים

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## שיחה עם LLM
למד כיצד להתחיל לשוחח עם LLM ברמת ChatGPT באופן מקומי לחלוטין.

1. פתח את LMStudio.
2. לחץ על `Ctrl + L` כדי לפתוח את טוען המודלים (Model Loader), בחר `Manually choose model load parameters`, ולחץ על `${model_name}`
3. ודא שהאפשרות "show advanced settings" מסומנת.
4. שנה את `Context Length` לפי הצורך. אורך הקשר גבוה יותר פירושו יותר זיכרון מודל, אך שימוש רב יותר בזיכרון המערכת. המומלץ עבור playbook זה הוא 4096.
5. ודא ש-`GPU Offload` מוגדר למקסימום ו-`Flash Attention` מופעל (Cache Quantizations יכול להישאר כבוי)
6. סמן את `Remember settings` ולחץ על `Load Model`.
7. אם אינך בחלון הצ'אט, לחץ על `Ctrl + 1` או לחץ על כפתור 👾 בפינה השמאלית העליונה של המסך.
8. שלח הודעה והתחל לתקשר עם המודל!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **טיפ**: אורך הקשר מתייחס לזיכרון המודל. Flash attention משפר את מהירות העיבוד תוך הפחתת השימוש בזיכרון. GPU Offload מעביר את החישוב לכרטיס המסך לקבלת תגובות מהירות יותר.

## שירות מודלי LLM דרך נקודת קצה תואמת OpenAI

LM Studio מציע גם נקודת קצה תואמת OpenAI בצורת LM Studio Server. זה כבר הודגם בתהליך עבודה של קידוד אג'נטי עם Cline [כאן](../playbooks/vscode-qwen3-coder). שימוש נפוץ נוסף הוא חיבור LM Studio Server לכל אפליקציית ווב (React, Node.js, Python) על ידי שליחת בקשות HTTP סטנדרטיות לנקודת הקצה של ה-inference.

כדי להגדיר את LM Studio Server, השתמש בהוראות הבאות:

1. בצד שמאל, לחץ על הכרטיסייה `Developer` (סמל שורת פקודה) או `Ctrl + 2` ולאחר מכן לחץ על `Server Settings`.
2. (אופציונלי): אם ברצונך לשרת את המודל ברשת ה-LAN שלך, סמן את `Serve on Local Network`. אם ברצונך להשתמש עם אתר אינטרנט או קריאות נרחבות בתוך VS Code, סמן את `Enable CORS`.
3. בפינה השמאלית העליונה, ודא שהשרת פועל על ידי לחיצה על כפתור ההחלפה מול `Status`.
4. נקודת קצה תואמת OpenAI תפעל כעת. הכתובת נמצאת בדרך כלל ב-http://127.0.0.1:1234
5. אם מודל אינו טעון כבר, ניתן לטעון אותו על ידי לחיצה על `Load Model` ופעולה לפי השלבים שהוזכרו קודם.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->


מודל זה יהיה נגיש כעת דרך נקודת הקצה של LM Studio Server ויתמוך בנקודות קצה של OpenAI כולל:

| נקודת קצה | שיטה | תיעוד |
|------------|----------|----------|
| /v1/models | GET | [מודלים](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [תגובות](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [השלמות צ'אט](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [הטמעות](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [השלמות](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### דוגמה: בדיקת נקודת הקצה שלך
לאחר יצירת נקודת הקצה התואמת OpenAI, בואו נבחן כיצד לשלב זאת בסביבת פיתוח Python (כגון VSCode) ולהשתמש במערכת שלך כספק API מקומי.

1. צור סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    על Linux, פתח טרמינל בתיקייה לבחירתך ופעל לפי הפקודות ליצירת venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**הענק למשתמש שלך גישה למכשירי GPU** (התנתק והתחבר מחדש כדי שזה ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

    על Linux, פתח טרמינל בתיקייה לבחירתך ופעל לפי הפקודות ליצירת venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    על Windows, פתח טרמינל בתיקייה לבחירתך ופעל לפי הפקודות ליצירת venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **טיפ**: משתמשי Windows עשויים להזדקק לשינוי מדיניות הביצוע של PowerShell (לדוגמה,
    > הגדרתה ל-RemoteSigned או Unrestricted) לפני הפעלת חלק מפקודות Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    על Windows, פתח טרמינל בתיקייה לבחירתך ופעל לפי הפקודות ליצירת venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **טיפ**: משתמשי Windows עשויים להזדקק לשינוי מדיניות הביצוע של PowerShell (לדוגמה,
    > הגדרתה ל-RemoteSigned או Unrestricted) לפני הפעלת חלק מפקודות Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. התקן את חבילת OpenAI
    ```bash
    pip install openai
    ```

3. הפעל את הסקריפט הבא כדי לבדוק את נקודת הקצה שיצרנו זה עתה.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

#### (אופציונלי): מעבר בין Runtimes

1. לחץ על `Ctrl + Shift + R` במקלדת. לחלופין, לחץ על הכרטיסייה `Discover` (זכוכית מגדלת) בצד שמאל ולאחר מכן לחץ על `Runtime` בחלון הקופץ.
2. לאחר מכן אמור להופיע `Runtime Selections`, שבו ניתן להשתמש בתפריט הנפתח כדי לשנות את ה-runtime.


## השלבים הבאים

- **שילוב אפליקציות מותאמות אישית**: שלב סקריפטים או אפליקציות Python משלך באמצעות ה-API המקומי התואם OpenAI.
- **ממשקים מתקדמים**: חבר ממשקים עוצמתיים כמו Open WebUI לשרת שלך לניהול היסטוריית צ'אט ופרסונות.

לתיעוד נוסף, בקר בכתובת: https://lmstudio.ai/docs/developer