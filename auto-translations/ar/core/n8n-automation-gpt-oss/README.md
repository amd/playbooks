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
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!ملاحظة]
> يتطلب هذا الدليل الإرشادي حدًا أدنى قدره **32 جيجابايت** من ذاكرة النظام.
<!-- @device:end -->
n8n هي منصة أتمتة سير العمل تتيح لك ربط التطبيقات والخدمات باستخدام محرر مرئي قائم على العُقَد.

يعلّمك هذا الدليل كيفية إعداد أداة تلخيص إخبارية مالية مدعومة بالذكاء الاصطناعي، تقوم بسحب أحدث عناوين الأخبار التجارية من موجز RSS إخباري، وتستخدم نموذج لغة كبير محلي يعمل على نظامك لإنشاء ملخص موجّه للمستثمرين.

## ماذا ستتعلم

- كيفية تثبيت وتشغيل n8n
- استيراد وتهيئة سير عمل جاهز مسبقًا
- الاتصال بـ Lemonade باستخدام التكامل الأصلي في n8n
- فهم عُقَد سير العمل وتدفق البيانات

## ما هو Lemonade؟

[Lemonade](https://lemonade-server.ai) هي منصة لتشغيل نماذج اللغة الكبيرة محليًا، مصممة خصيصًا لأجهزة AMD. توفّر واجهة برمجة تطبيقات متوافقة مع OpenAI تعمل بالكامل على جهازك - فبياناتك لا تغادر جهازك أبدًا.

في هذا الدليل، نستخدم Lemonade لتشغيل نموذج لغة كبير محلي يتصل به n8n لتنفيذ مهام مدعومة بالذكاء الاصطناعي.

يتضمن n8n **عقدة Lemonade أصلية** (`Lemonade Chat Model`) توفّر تكاملًا من الدرجة الأولى - دون الحاجة إلى أي تهيئة يدوية. هذا يجعل ربط نموذج اللغة الكبير المحلي الخاص بك بسير عمل الأتمتة أمرًا بسيطًا ومباشرًا.
<!-- @device:halo_box,halo,stx,krk -->
## إعداد تهيئة الذاكرة
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرنامج
<!-- @require:software-update -->
<!-- @device:end -->
## تثبيت متطلبات البرامج الأساسية
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->
## تثبيت n8n
<!-- @os:windows -->
تثبيت n8n عالميًا باستخدام npm.

> **ملاحظة**: قد تظهر بعض تحذيرات npm. هذا أمر متوقع.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **نصيحة**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (Execution Policy) (على سبيل المثال
> بتعيينها إلى RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **مشكلة متغير PATH**: إذا ظهرت رسالة تفيد بأن الأمر `n8n --version` غير معروف (command not found)، فتأكد من أن مسار مجلد npm العام (global bin) مضاف إلى متغير `PATH` الخاص بالمستخدم. المسار المعتاد للتثبيت هو `C:\Users\<username>\AppData\Roaming\npm`.
> أضف هذا المسار إلى متغير PATH الخاص بالمستخدم (عبر الانتقال إلى Edit the system environment variables > Environment Variables > Edit User Path) ثم أعد تحميل الطرفية (terminal).
<!-- @os:end -->

<!-- @os:linux -->
سنقوم الآن باستخدام خدمة Podman لتثبيت n8n الخاص بنا داخل حاوية.

يرجى تنزيل الملف التالي إلى دليل من اختيارك: [compose.yml](assets/compose.yml)

في ذلك الدليل، قم بتشغيل الأمر التالي:
```bash
podman compose up -d
```

يجب أن يؤدي هذا إلى تثبيت n8n والكتابة إلى تخزين دائم.

قم بتشغيل n8n عن طريق كتابة `localhost:5678` في شريط عنوان متصفحك.
<!-- @os:end -->

<!-- @os:windows -->
## تشغيل n8n

ابدأ تشغيل n8n من الطرفية (Terminal):

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n يبدأ خادم ويب محلي. اضغط على `'o'` أو افتح متصفحك على `http://localhost:5678` للوصول إلى المحرر.
<!-- @os:end -->
> **تلميح**: حافظ على فتح نافذة الطرفية أثناء استخدام n8n. إغلاقها قد يوقف الخادم.

## تشغيل Lemonade

Lemonade هو الخادم المحلي الذي سيقوم بتشغيل نموذج والاتصال بـ n8n.
<!-- @os:linux -->
افتح واجهة Lemonade الرسومية (GUI) بالنقر على أيقونة Lemonade في شريط المهام. يمكنك من هنا تصفح النماذج والواجهات الخلفية (backends)، وتحميل النماذج المثبّتة مسبقًا.
<!-- @os:end -->

<!-- @os:windows -->
فتح واجهة Lemonade الرسومية بالنقر على أيقونة Lemonade. انقر بالزر الأيمن على أيقونة شريط المهام لفتح التطبيق. بعد ذلك، يمكنك إضافة النماذج والواجهات الخلفية (backends)، وتحميل النماذج المثبتة مسبقًا.
<!-- @os:end -->
>**ملاحظة**: بمجرد التشغيل، يمكن أيضًا الوصول إلى واجهة Lemonade الرسومية عبر http://localhost:13305

بدلاً من ذلك، يمكنك فتح طرفية (terminal) وتشغيل `lemonade list` لمعرفة النماذج المثبتة. بعد ذلك، شغّل:
<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->
## إعداد سير العمل

### الخطوة 1: التسجيل أو تسجيل الدخول إلى n8n

عند فتح n8n لأول مرة، سيُطلب منك إنشاء حساب أو تسجيل الدخول:

1. افتح `http://localhost:5678` في متصفحك
2. أنشئ حسابًا محليًا جديدًا باستخدام بريدك الإلكتروني، أو سجّل الدخول إذا كان لديك حساب بالفعل
3. بمجرد تسجيل الدخول، ستظهر لك لوحة تحكم n8n

> **ملاحظة**: إذا تم إغلاق حسابك ولم تتمكن من الدخول، جرّب `n8n user-management:reset`

### الخطوة 2: استيراد سير العمل

لقد قدّمنا سير عمل جاهزًا يمكنك استيراده مباشرةً:

1. قم بتنزيل ملف سير العمل التالي: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. انقر على **Start from Scratch** لفتح محرر سير العمل. بدلًا من ذلك، انقر على زر + في أعلى اليسار، ثم **Add workflow**.
3. انقر على قائمة **...** (النقاط الثلاث) في الشريط العلوي الأيمن واختر **Import from file**
4. حدد ملف `financial-news-workflow.json` الذي قمت بتنزيله
5. سيظهر سير العمل على لوحة العمل
### الخطوة 3: فهم سير العمل

يحتوي سير العمل المستورد على 8 عُقد متصلة:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| العقدة | الغرض |
|------|---------|
| **When clicking 'Execute workflow'** | مشغّل يدوي لبدء سير العمل |
| **Fetch Financial News Feed** | عقدة RSS Read تسحب أحدث العناوين الرئيسية التجارية من خلاصة RSS (تستخدم افتراضيًا خلاصة NYT Business، ولا تتطلب مفتاح API) |
| **Aggregate Headlines** | عقدة Aggregate تجمع عناوين وملخصات كل عنصر من الخلاصة في قائمة واحدة |
| **Clean Extracted News Data** | عقدة Set تدمج جميع العناوين في حقل نصي واحد |
| **AI Financial News Summarizer** | وكيل ذكاء اصطناعي يعالج الأخبار باستخدام موجّه نظام لمحلل مالي |
| **Lemonade Chat Model** | يتصل بخادم Lemonade المحلي الذي يشغّل نموذج اللغة |
| **Structured Output Parser** | ينسّق مخرجات الذكاء الاصطناعي بصيغة JSON منظمة |
| **Convert to File** | يحول الملخص إلى ملف قابل للتنزيل |

> **تلميح**: لاستخدام مصدر أخبار مختلف، انقر نقرًا مزدوجًا على عقدة **Fetch Financial News Feed** واستبدل الرابط بأي خلاصة RSS للأعمال أو الأسواق تفضّلها.

### الخطوة 4: تهيئة بيانات اعتماد Lemonade

قبل تشغيل سير العمل، تحتاج إلى ربطه بخادم Lemonade المحلي الخاص بك:

1. انقر نقرًا مزدوجًا على عقدة **Lemonade Chat Model** في n8n
2. من القائمة المنسدلة **Credential to connect with** اختر **Create New Credential**
3. أدخل القيم في الجدول أدناه ثم انقر على حفظ.
4. اختر النموذج المناسب الذي قمت بتحميله في Lemonade Server.

  | الحقل | القيمة |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **ملاحظة**: قبل الاختبار، شغّل الأمر `lemonade status` في الطرفية للتأكد من أن خادم Lemonade يعمل.
<!-- @device:halo_box -->
> يستخدم سير العمل هذا GPT-OSS-120B وهو مثبت مسبقًا في Lemonade. يمكنك تغيير ذلك إلى نماذج أخرى محمّلة في إعدادات عقدة Lemonade Chat Model.
<!-- @device:end -->

### الخطوة 5: اختبار سير العمل

1. تأكد من أن Lemonade يعمل مع نموذج محمّل
2. انقر على **Execute workflow** في أسفل منتصف لوحة العمل
3. راقب تنفيذ كل عقدة من اليسار إلى اليمين — تتحول إلى اللون الأخضر عند الانتهاء
4. انقر نقرًا مزدوجًا على عقدة **AI Financial News Summarizer** لرؤية الملخص الذي تم إنشاؤه في اللوحة السفلية.
5. انقر نقرًا مزدوجًا على عقدة **Convert to File** لتنزيل ملف النص المقابل من اللوحة السفلية.

## فهم وكيل الذكاء الاصطناعي

يستخدم AI Financial News Summarizer موجّه نظام مصمم للتحليل المالي:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

يستقبل الوكيل بيانات الأخبار المنظفة ويُخرج ملخصًا منظمًا مع معنويات السوق.

### حفظ سير العمل الخاص بك

انقر على اسم سير العمل في الأعلى وأعد تسميته إذا أردت. تُحفظ سير العمل تلقائيًا أثناء العمل.

## الخطوات التالية

- **جدولة التشغيل التلقائي**: استبدل Manual Trigger بـ **Schedule Trigger** للتشغيل يوميًا
- **إرسال الإشعارات**: أضف عقدة **Discord** أو **Slack** أو **Email** لاستلام الملخصات
- **جرّب نماذج مختلفة**: غيّر النموذج في عقدة Lemonade Chat Model لتجربة نماذج لغوية مختلفة
- **تغيير مصدر الأخبار**: وجّه عقدة **Fetch Financial News Feed** إلى خلاصة RSS مختلفة لمتابعة أقسام أو منشورات أخرى
- **جرّب خلفيات مختلفة**: يدعم n8n أيضًا [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)، وLM Studio، وخلفيات LLM محلية أخرى

### استكشاف قوالب n8n

يحتوي n8n على مئات قوالب سير العمل الجاهزة. تصفح مكتبة القوالب الرسمية على:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

ابحث عن "AI" أو "LLM" أو "automation" للعثور على سير عمل يمكنك استيراده وتخصيصه.

لمزيد من المعلومات، راجع [وثائق n8n](https://docs.n8n.io/).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->