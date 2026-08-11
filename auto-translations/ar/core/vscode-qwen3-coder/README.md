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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> يتطلب هذا الدليل الإرشادي حد أدنى **32 جيجابايت** من ذاكرة النظام.
<!-- @device:end -->

## نظرة عامة

تُعد وكلاء البرمجة أدوات قوية تُمكّن المطورين من خلال التعاون مع وكلاء الذكاء الاصطناعي المدعومين بنماذج اللغة الكبيرة (LLMs). يمكن دمجها في بيئة التطوير، مثل الطرفية أو VS Code، مما يتيح تكاملاً سلساً مع سير عمل المطور.

يوضح هذا الدرس التعليمي كيفية استخدام Cline وVS Code وLM Studio لتشغيل وكيل برمجة بالكامل على جهازك المحلي.

## ما ستتعلمه

* كيفية تشغيل VS Code مع وكيل البرمجة Cline للمساعدة في مهام هندسة البرمجيات.
* كيفية تهيئة Cline للتواصل مع LM Studio لإجراء الاستدلال المحلي لوكلاء البرمجة.
* كيفية استخدام وكلاء البرمجة المحليين لحل مهام هندسة برمجيات واقعية.

## تعيين تهيئة الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتاً، يمكنك تثبيته باستخدام Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @require:lmstudio,vscode -->

## تشغيل وتهيئة LM Studio

سنستخدم LM Studio لتقديم خدمة نموذج اللغة الكبير الذي يشغّل وكيل البرمجة.

- في شريط البحث، ابحث عن `LM Studio` وشغّل التطبيق. ستظهر لك الصفحة التالية.

![الشاشة الأولية لـ LM Studio](assets/initial-lm-studio.png)

بعد ذلك، يجب علينا تحميل نموذج اللغة الكبير على النظام. سنستخدم نموذج `Qwen3-Coder-30B-A3B` بطول سياق كبير. (استخدم علامة تبويب Model لتثبيته إذا لم تكن قد فعلت ذلك بالفعل).
- انقر على شريط البحث في أعلى نافذة LM Studio أو اضغط على `CTRL+L`. انقر على المفتاح `Manually choose model load parameters` ثم انقر على نموذج Qwen3-Coder-30B-A3B.
- غيّر طول السياق من `4096` إلى `32768`، وتأكد من أن `GPU Offload` عند الحد الأقصى. ثم انقر على `Load Model`

![اختيار النموذج](assets/model-list-zoomed.png)

نستخدم طول سياق كبيراً حتى يتمكن الوكيل من معالجة قواعد أكواد كبيرة وتذكر التغييرات التي تم إجراؤها.

![تهيئة النموذج](assets/selecting-model-zoomed.png)

بعد ذلك، نحتاج إلى تفعيل خادم LM Studio.
- انقر على علامة تبويب Developer أو اضغط على `CTRL+2` في LM Studio على اليسار.
- تحقق من مفتاح الحالة وتأكد من أنه مضبوط على `Running`.

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

![حالة الخادم](assets/lm-studio-server-status.png)

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## تشغيل وتهيئة VS Code

سنقوم بتثبيت إضافة Cline في VS Code وربطها بخادم LM Studio الذي أنشأناه للتو.
- في شريط البحث، ابحث عن `VS Code` وشغّل التطبيق.
- انقر على أيقونة `Extensions` في العمود الأيسر من VS Code وابحث عن `Cline`. ثم انقر على زر `Install`.

![تثبيت إضافة Cline](assets/installing-cline-vscode-extension.png)

- ستظهر أيقونة Cline على اليسار. انقر عليها لفتح Cline. ستظهر نافذة تسأل `How will you use Cline?` نظراً لأننا سنستخدم نموذج لغة كبير محلي يعمل عبر LM Studio، اختر `Bring my own API Key` واضغط على `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![إنشاء حساب](assets/cline-how-will-you-use-cline-zoomed.png)

بعد ذلك، نحتاج إلى تهيئة Cline للتواصل مع خادم LM Studio الذي أعددناه.
- اضبط API Provider على `LM Studio` والنموذج على `Qwen3-Coder-30B-A3B-GGUF`.

>**نصيحة**: قد تتوفر نماذج أحدث. فكّر في تنزيل نماذج Qwen3.6 والتبديل إليها إذا رغبت في ذلك.


![تهيئة النموذج](assets/cline-model-configuration-zoomed.png)

## إنشاء مشروعك الأول

لنستخدم وكيلنا المحلي لإنشاء موقع ويب! افتح VSCode على مجلد من اختيارك حيث سينشئ Cline الملفات.
- للقيام بذلك، انتقل إلى `File -> Open Folder` في أعلى يسار VS Code واختر مجلداً مثل `Documents`.

![مجلد فارغ في VS Code](assets/open-cline-test.png)

الآن نحن مستعدون لمطالبة وكيل البرمجة المحلي.
- انقر على إضافة Cline في العمود الأيسر وأدخل مطالبة لبدء تشغيل الوكيل. كمثال، لنستخدم المطالبة التالية:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

سيبدأ الوكيل بعد ذلك في إنشاء الملفات وفقاً للمطالبة. كمستخدم، يمكنك مشاهدة إنشاء الكود في VS Code كما هو موضح أدناه. قد تحتاج إلى النقر على `Save` في كل مرة يرغب فيها Cline بإنشاء ملف.

![إنشاء الكود بواسطة Cline](assets/cline-code-generation.png)

بعد إنشاء البرنامج، يكتمل عمل الوكيل ويمكنك تشغيل التطبيق. في هذه الحالة، كتب الوكيل ثلاثة ملفات: `index.html` و`script.js` و`styles.css`. بمجرد النقر المزدوج على ملف HTML، يمكننا تحميل الموقع الذي تم إنشاؤه والتفاعل معه.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
## الخطوات التالية

بعد إنشاء الموقع الإلكتروني، يمكنك الاستمرار في العمل مع Cline لتحسين الموقع. إليك تحسينان محتملان:

- **التوثيق**: يكفي توجيه الوكيل بـ `Add a README` ليقوم بإنشاء ملف `README.md` يوثّق الموقع الإلكتروني.
- **الرسوم المتحركة**: وجّه النموذج بـ `Add an animation that visually represents a large language model running on a laptop.` لإنشاء رسوم متحركة تُضاف إلى الموقع.

نشجّع القارئ على تجربة إنشاء تطبيقات أخرى باستخدام هذا الإعداد. فيما يلي بعض الأمثلة الممتعة التي جرّبناها:

- **ألعاب الأركيد الكلاسيكية**: جرّب بعض التوجيهات (Prompts) الأخرى. يمكن أن يكون من الممتع أيضًا أن ينشئ الوكيل ألعابًا بأسلوب كلاسيكي باستخدام لغة Python وحزمة `PyGame` باستخدام التوجيه التالي:

```code
Create a simple pong game using the PyGame python package.
```

- **تحليل البيانات**: من المجالات التي تُعد فيها وكلاء البرمجة مفيدة بشكل خاص، مجال كتابة السكربتات وتحليل البيانات. هذا توجيه لعرض قدرة النموذج المحلي على إنشاء برمجيات تحليل بيانات لتصور أسعار الأسهم:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## الموارد

فيما يلي بعض الموارد الإضافية لمعرفة المزيد حول وكلاء البرمجة، وCline، وتشغيل أعباء العمل على 

* مزيد من المعلومات حول شراكة وتكامل AMD مع LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* مدونة AMD التي تستعرض تشغيل Cline على بطاقات AMD Ryzen™ AI وRadeon™ Graphics: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* مدونة Cline حول تشغيل وكلاء البرمجة محليًا على أجهزة الكمبيوتر الشخصي المزودة بالذكاء الاصطناعي (AI PCs): https://cline.bot/blog/local-models-amd