<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

LM Studio هو غلاف قائم على واجهة رسومية قوي لـ [llama.cpp](https://github.com/ggml-org/llama.cpp) ويوفر أيضًا [نقطة نهاية متوافقة مع OpenAI](https://lmstudio.ai/docs/developer/openai-compat) لخدمة النماذج محليًا. يوفر LM Studio واجهة بسيطة لكنها قوية لتنزيل النماذج ونشرها بسهولة. يقدم LM Studio لمستخدمي AMD كلًا من خلفيتَي Vulkan وAMD ROCm™ (المعروفتين بالبيئات التشغيلية).


## ما ستتعلمه
- كيفية تهيئة LM Studio واستخدامه للاستفادة من أجهزتك المحلية
- اختبار النماذج اللغوية الكبيرة وإدارتها في بيئة غير متصلة بالإنترنت بالكامل
- خدمة النماذج عبر واجهة برمجة تطبيقات متوافقة مع OpenAI لتشغيل سير العمل والتطبيقات المخصصة


## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @os:linux -->
> **ملاحظة**: يمكنك تثبيت VS Code من خلال AMD Ryzen™ AI Developer Center. أما LM Studio، فاتبع تعليمات التثبيت أدناه.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: إذا لم يكن VS Code أو LM Studio مثبتًا، يمكنك تثبيتهما من AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## تنزيل النماذج

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

## الدردشة مع نموذج لغوي كبير
تعلّم كيفية بدء الدردشة مع نموذج لغوي كبير بمستوى ChatGPT بشكل محلي تمامًا.

1. افتح LMStudio.
2. اضغط `Ctrl + L` لفتح محمّل النماذج، واختر `Manually choose model load parameters`، ثم انقر على `${model_name}`
3. تأكد من تفعيل خيار "show advanced settings".
4. غيّر `Context Length` حسب الرغبة. كلما زاد طول السياق، زادت ذاكرة النموذج، لكن يزداد استهلاك ذاكرة النظام أيضًا. الموصى به لهذا الدليل هو 4096.
5. تأكد من ضبط `GPU Offload` على الحد الأقصى وتفعيل `Flash Attention` (يمكن إبقاء Cache Quantizations معطلة).
6. فعّل `Remember settings` وانقر على `Load Model`.
7. إذا لم تكن في نافذة الدردشة، اضغط `Ctrl + 1` أو انقر على زر 👾 في أعلى يسار الشاشة.
8. أرسل رسالة وابدأ التفاعل مع النموذج!

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

> **تلميح**: يشير طول السياق إلى ذاكرة النموذج. تُحسّن الانتباه الفوري (Flash Attention) سرعة المعالجة مع تقليل استهلاك الذاكرة. يُحوّل تفريغ GPU الحسابات إلى بطاقة الرسومات للحصول على استجابات أسرع.

## خدمة النماذج اللغوية الكبيرة عبر نقطة نهاية متوافقة مع OpenAI

يوفر LM Studio أيضًا نقطة نهاية متوافقة مع OpenAI في شكل LM Studio Server. وقد تم توضيح ذلك بالفعل في سير عمل برمجي وكيلي مع Cline [هنا](../playbooks/vscode-qwen3-coder). من حالات الاستخدام الشائعة الأخرى ربط LM Studio Server بأي تطبيق ويب (React أو Node.js أو Python) عن طريق إرسال طلبات HTTP قياسية إلى نقطة نهاية الاستدلال.

لإعداد LM Studio Server، اتبع التعليمات التالية:

1. على الجانب الأيسر، انقر على تبويب `Developer` (أيقونة سطر الأوامر) أو اضغط `Ctrl + 2`، ثم انقر على `Server Settings`.
2. (اختياري): إذا أردت خدمة النموذج عبر شبكتك المحلية، فعّل `Serve on Local Network`. وإذا أردت استخدامه مع موقع ويب أو استدعاءات مكثفة داخل VS Code، فعّل `Enable CORS`.
3. في الزاوية العلوية اليسرى، تأكد من تشغيل الخادم بالنقر على زر التبديل أمام `Status`.
4. ستعمل الآن نقطة نهاية متوافقة مع OpenAI. العنوان عادةً هو http://127.0.0.1:1234
5. إذا لم يكن النموذج محملًا بالفعل، يمكنك تحميله بالنقر على `Load Model` واتباع الخطوات المذكورة سابقًا.

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


سيصبح هذا النموذج الآن متاحًا عبر نقطة نهاية LM Studio Server وسيدعم نقاط نهاية OpenAI التالية:

| نقطة النهاية | الطريقة | التوثيق |
|------------|----------|----------|
| /v1/models | GET | [النماذج](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [الاستجابات](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [إكمالات الدردشة](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [التضمينات](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [الإكمالات](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### مثال: اختبار الاتصال بنقطة النهاية
بعد إنشاء نقطة النهاية المتوافقة مع OpenAI، دعنا نرى كيفية دمجها في بيئة تطوير Python (مثل VSCode) واستخدام نظامك كمزود API محلي.

1. أنشئ بيئة Python افتراضية:

<!-- @os:linux -->
<!-- @device:halo_box -->
    على Linux، افتح طرفية في المجلد الذي تختاره واتبع الأوامر التالية لإنشاء بيئة venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (سجّل الخروج وأعد الدخول لتفعيل هذا الإعداد):

```bash
sudo usermod -aG render,video $LOGNAME
```

    على Linux، افتح طرفية في المجلد الذي تختاره واتبع الأوامر التالية لإنشاء بيئة venv.
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
    على Windows، افتح طرفية في المجلد الذي تختاره واتبع الأوامر التالية لإنشاء بيئة venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell (مثلًا
    > ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    على Windows، افتح طرفية في المجلد الذي تختاره واتبع الأوامر التالية لإنشاء بيئة venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell (مثلًا
    > ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. ثبّت حزمة OpenAI
    ```bash
    pip install openai
    ```

3. شغّل السكريبت التالي لاختبار الاتصال بنقطة النهاية التي أنشأناها للتو.
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

#### (اختياري): التبديل بين البيئات التشغيلية

1. اضغط `Ctrl + Shift + R` على لوحة المفاتيح. أو انقر على تبويب `Discover` (أيقونة العدسة المكبّرة) على الجانب الأيسر، ثم انقر على `Runtime` في النافذة المنبثقة.
2. ستظهر لك `Runtime Selections`، حيث يمكن استخدام القائمة المنسدلة لتغيير البيئة التشغيلية.


## الخطوات التالية

- **دمج التطبيقات المخصصة**: ادمج سكريبتات Python الخاصة بك أو تطبيقاتك باستخدام واجهة برمجة التطبيقات المحلية المتوافقة مع OpenAI.
- **واجهات أمامية متقدمة**: اربط واجهات قوية مثل Open WebUI بخادمك لإدارة سجل الدردشة والشخصيات.

لمزيد من التوثيق، يرجى زيارة: https://lmstudio.ai/docs/developer