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

LM Studio הוא עוטף (wrapper) עוצמתי מבוסס ממשק גרפי עבור [llama.cpp](https://github.com/ggml-org/llama.cpp) ומספק גם [נקודת קצה תואמת OpenAI](https://lmstudio.ai/docs/developer/openai-compat) להגשת מודלים מקומית. LM Studio מספק ממשק פשוט אך עוצמתי להורדה ולפריסה קלה של מודלים. LM Studio מציע גם backend של Vulkan וגם של AMD ROCm™ (הנקראים runtimes) עבור משתמשי AMD.


## מה תלמדו
- כיצד להגדיר ולהשתמש ב-LM Studio כדי לנצל את החומרה המקומית שלכם
- לבדוק ולנהל LLMs בסביבה שהיא לחלוטין ללא חיבור לרשת
- להגיש מודלים דרך API תואם OpenAI כדי להפעיל זרימות עבודה ואפליקציות מותאמות אישית


<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @os:linux -->
> **הערה**: ניתן להתקין את VS Code דרך AMD Ryzen™ AI Developer Center. עבור LM Studio, יש לפעול לפי הוראות ההתקנה שלהלן.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: אם VS Code או LM Studio אינם מותקנים, ניתן להתקין אותם מתוך AMD Ryzen™ AI Developer Center. 
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
למדו כיצד להתחיל לשוחח עם LLM ברמת ChatGPT באופן מקומי לחלוטין.  

1. פתחו את LMStudio. 
2. לחצו על `Ctrl + L` כדי לפתוח את Model Loader, בחרו `Manually choose model load parameters`, ולחצו על `${model_name}`
3. ודאו שהאפשרות "show advanced settings" מסומנת.  
4. שנו את `Context Length` כרצונכם. אורך הקשר (context length) גבוה יותר משמעו יותר זיכרון מודל, אך יותר זיכרון מערכת בשימוש. המומלץ עבור מדריך זה הוא 4096.
5. ודאו ש-`GPU Offload` מוגדר למקסימום ושהאפשרות `Flash Attention` פעילה (Cache Quantizations יכולות להישאר כבויות)
6. סמנו `Remember settings` ולחצו על `Load Model`.
7. אם אינכם נמצאים בחלון הצ'אט, לחצו `Ctrl + 1` או לחצו על הכפתור 👾 בפינה השמאלית העליונה של המסך.
8. שלחו הודעה והתחילו לתקשר עם המודל!

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

> **טיפ**: אורך ההקשר (context length) מתייחס לזיכרון של המודל. Flash attention משפר את מהירות העיבוד תוך הפחתת השימוש בזיכרון. GPU Offload מעביר עומסי חישוב לכרטיס הגרפי לצורך תגובות מהירות יותר.

## הגשת LLMs דרך נקודת קצה תואמת OpenAI

LM Studio מציע גם נקודת קצה תואמת OpenAI בצורת LM Studio Server. הדבר כבר הודגם בזרימת עבודה agentic לתכנות עם Cline [כאן](../playbooks/vscode-qwen3-coder). מקרה שימוש נפוץ נוסף הוא חיבור LM Studio Server לכל אפליקציית אינטרנט (React, Node.js, Python) על ידי שליחת בקשות HTTP סטנדרטיות לנקודת הקצה של ההסקה (inference).

כדי להגדיר את LM Studio Server, פעלו לפי ההוראות הבאות:

1. בצד שמאל, לחצו על הכרטיסייה `Developer` (סמל שורת הפקודה) או `Ctrl + 2` ולאחר מכן לחצו על `Server Settings`.  
2. (אופציונלי): אם ברצונכם להגיש את המודל דרך רשת ה-LAN שלכם, סמנו `Serve on Local Network`. אם ברצונכם להשתמש באתר אינטרנט או בקריאות נרחבות בתוך VS Code, סמנו `Enable CORS`. 
3. בפינה השמאלית העליונה, ודאו שהשרת פועל על ידי לחיצה על כפתור המתג מול `Status`.
4. כעת תפעל נקודת קצה תואמת OpenAI. הכתובת היא בדרך כלל http://127.0.0.1:1234  
5. אם מודל אינו טעון עדיין, ניתן לטעון אותו על ידי לחיצה על `Load Model` ופעולה לפי השלבים שהוזכרו קודם לכן. 

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


מודל זה יהיה כעת נגיש דרך נקודת הקצה של LM Studio Server ויתמוך בנקודות קצה של OpenAI, כולל:

| נקודת קצה | שיטה | תיעוד |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### דוגמה: פינג לנקודת הקצה (Endpoint) שלכם
לאחר שיצרנו זה עתה נקודת קצה תואמת OpenAI, בואו נבחן כיצד לשלב זאת בסביבת פיתוח Python (כגון VSCode) ולהשתמש במערכת שלכם כספק API מקומי.

1. צרו סביבה וירטואלית של Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    ב-Linux, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

    ב-Linux, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
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
    ב-Windows, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרצה (Execution Policy) של PowerShell (למשל
    > להגדיר אותה כ-RemoteSigned או Unrestricted) לפני הרצת חלק מפקודות Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    ב-Windows, פתחו טרמינל בתיקייה לבחירתכם ופעלו לפי הפקודות ליצירת venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרצה (Execution Policy) של PowerShell (למשל
    > להגדיר אותה כ-RemoteSigned או Unrestricted) לפני הרצת חלק מפקודות Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. התקינו את חבילת OpenAI
    ```bash
    pip install openai
    ```

3. הריצו את הסקריפט הבא כדי לבצע פינג לנקודת הקצה שיצרנו זה עתה.
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

#### (אופציונלי): החלפה בין זמני ריצה (Runtimes)

1. הקישו `Ctrl + Shift + R` במקלדת. לחלופין, לחצו על לשונית `Discover` (זכוכית מגדלת) בצד שמאל ולאחר מכן לחצו על `Runtime` בחלון שנפתח.
2. כעת אמורים להופיע `Runtime Selections`, שם ניתן להשתמש בתפריט הנפתח כדי לשנות את זמן הריצה.


## הצעדים הבאים

- **שילוב אפליקציה מותאמת אישית**: שלבו את הסקריפטים או האפליקציות שלכם ב-Python באמצעות ה-API המקומי התואם ל-OpenAI.
- **ממשקי משתמש מתקדמים**: חברו ממשקים עוצמתיים כמו Open WebUI לשרת שלכם לצורך היסטוריית צ'אט וניהול פרסונות.

לתיעוד נוסף, בקרו בכתובת: https://lmstudio.ai/docs/developer