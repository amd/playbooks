<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

LM Studio هو غلاف قوي يعتمد على واجهة رسومية لـ [llama.cpp](https://github.com/ggml-org/llama.cpp) ويوفر أيضًا [نقطة نهاية متوافقة مع OpenAI](https://lmstudio.ai/docs/developer/openai-compat) لخدمة النماذج محليًا. يوفر LM Studio واجهة بسيطة لكنها قوية لتنزيل النماذج ونشرها بسهولة. يقدم LM Studio كلًا من خلفيتي Vulkan وAMD ROCm™ (تُسمى بيئات التشغيل) لمستخدمي AMD.


## ما ستتعلمه
- كيفية تهيئة LM Studio واستخدامه للاستفادة من الأجهزة المحلية لديك
- اختبار وإدارة نماذج اللغة الكبيرة (LLMs) في بيئة غير متصلة بالإنترنت بالكامل
- تقديم النماذج عبر واجهة برمجة تطبيقات متوافقة مع OpenAI لتشغيل سير عمل وتطبيقات مخصصة


## ضبط تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @os:linux -->
> **ملاحظة**: يمكنك تثبيت VS Code من خلال مركز مطوري AMD Ryzen™ AI. أما بالنسبة لـ LM Studio، فاتبع تعليمات التثبيت أدناه.
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: إذا لم يكن VS Code أو LM Studio مثبتًا، يمكنك تثبيتهما من مركز مطوري AMD Ryzen™ AI.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

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
تعرّف على كيفية بدء الدردشة مع نموذج لغوي كبير بجودة ChatGPT بشكل محلي بالكامل.

1. افتح LMStudio.
2. اضغط `Ctrl + L` لفتح محمّل النماذج، ثم اختر `Manually choose model load parameters`، وانقر على `${model_name}`
3. تأكد من تفعيل خيار "show advanced settings".
4. غيّر `Context Length` حسب الرغبة. طول السياق الأعلى يعني ذاكرة نموذج أكبر، ولكن استخدامًا أكبر لذاكرة النظام. الموصى به لهذا الدليل هو 4096.
5. تأكد من ضبط `GPU Offload` على الحد الأقصى وأن `Flash Attention` مفعّل (يمكن ترك Cache Quantizations معطّلًا)
6. حدد `Remember settings` وانقر على `Load Model`.
7. إذا لم تكن في نافذة الدردشة، اضغط `Ctrl + 1` أو انقر على زر 👾 في أعلى يسار الشاشة.
8. أرسل رسالة وابدأ التفاعل مع النموذج!

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

> **نصيحة**: يشير طول السياق إلى ذاكرة النموذج. يعمل Flash Attention على تحسين سرعة المعالجة مع تقليل استهلاك الذاكرة. يقوم GPU Offload بنقل عملية الحوسبة إلى بطاقة الرسوميات للحصول على استجابات أسرع.

## تقديم نماذج اللغة الكبيرة عبر نقطة نهاية متوافقة مع OpenAI

يوفر LM Studio أيضًا نقطة نهاية متوافقة مع OpenAI على شكل LM Studio Server. وقد تم عرض ذلك بالفعل في سير عمل برمجي وكيلي (agentic) باستخدام Cline [هنا](../playbooks/vscode-qwen3-coder). حالة استخدام شائعة أخرى هي ربط LM Studio Server بأي تطبيق ويب (React، Node.js، Python) عن طريق إرسال طلبات HTTP قياسية إلى نقطة نهاية الاستدلال.

لإعداد LM Studio Server، استخدم التعليمات التالية:

1. من الجانب الأيسر، انقر على علامة التبويب `Developer` (أيقونة سطر الأوامر) أو اضغط `Ctrl + 2` ثم انقر على `Server Settings`.
2. (اختياري): إذا كنت تريد تقديم النموذج عبر شبكتك المحلية (LAN)، فحدد `Serve on Local Network`. وإذا كنت تريد استخدامه مع موقع ويب أو استدعاءات مكثفة داخل VS Code، فحدد `Enable CORS`.
3. في الزاوية العلوية اليسرى، تأكد من أن الخادم قيد التشغيل عن طريق النقر على زر التبديل أمام `Status`.
4. ستعمل الآن نقطة نهاية متوافقة مع OpenAI. عادةً ما يكون العنوان هو http://127.0.0.1:1234
5. إذا لم يكن هناك نموذج محمّل بالفعل، يمكنك تحميله بالنقر على `Load Model` واتباع الخطوات المذكورة سابقًا.

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


سيكون هذا النموذج الآن متاحًا عبر نقطة نهاية LM Studio Server وسيدعم نقاط نهاية OpenAI بما في ذلك:

| نقطة النهاية | الطريقة | الوثائق |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### مثال: اختبار الاتصال بنقطة النهاية (Endpoint) الخاصة بك
بعد أن أنشأنا للتو نقطة النهاية المتوافقة مع OpenAI، دعنا نلقي نظرة على كيفية دمج ذلك في بيئة تطوير Python (مثل VSCode) واستخدام نظامك كمزود API محلي.

1. أنشئ بيئة Python افتراضية:

<!-- @os:linux -->
<!-- @device:halo_box -->
    على نظام Linux، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك صلاحية الوصول إلى أجهزة GPU** (يجب تسجيل الخروج ثم تسجيل الدخول مرة أخرى ليصبح هذا نافذ المفعول):

```bash
sudo usermod -aG render,video $LOGNAME
```

    على نظام Linux، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء venv.
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
    على نظام Windows، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (على سبيل المثال
    > بضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    على نظام Windows، افتح طرفية (terminal) في الدليل الذي تختاره واتبع الأوامر التالية لإنشاء venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (على سبيل المثال
    > بضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. ثبّت حزمة OpenAI
    ```bash
    pip install openai
    ```

3. شغّل النص البرمجي التالي لاختبار الاتصال بنقطة النهاية التي أنشأناها للتو.
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

#### (اختياري): التبديل بين بيئات التشغيل (Runtimes)

1. اضغط على `Ctrl + Shift + R` على لوحة المفاتيح. أو بدلاً من ذلك، انقر على تبويب `Discover` (أيقونة العدسة المكبرة) الموجود على الجانب الأيسر، ثم انقر على `Runtime` في النافذة المنبثقة.
2. ستظهر لك عندها `Runtime Selections`، حيث يمكن استخدام القائمة المنسدلة لتغيير بيئة التشغيل.


## الخطوات التالية

- **دمج تطبيق مخصص**: قم بدمج نصوصك البرمجية أو تطبيقاتك الخاصة بلغة Python باستخدام واجهة API المحلية المتوافقة مع OpenAI.
- **واجهات أمامية متقدمة**: اربط واجهات قوية مثل Open WebUI بخادمك لإدارة سجل المحادثات والشخصيات (persona management).

لمزيد من التوثيق، يُرجى زيارة: https://lmstudio.ai/docs/developer