<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# <!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل التعليمي علامات خاصة لا يمكن لموقع GitHub عرضها. يرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

## نظرة عامة

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> يتطلب هذا الدليل التعليمي حدًا أدنى من ذاكرة النظام قدره **32 جيجابايت**.
<!-- @device:end -->

n8n هي منصة أتمتة سير العمل التي تتيح لك ربط التطبيقات والخدمات باستخدام محرر مرئي قائم على العُقد.

يعلمك هذا الدليل التعليمي كيفية إعداد أداة تلخيص للأخبار المالية مدعومة بالذكاء الاصطناعي، تقوم باستخراج البيانات من قسم الأعمال في AP News، واستخراج العناوين الرئيسية، واستخدام نموذج لغوي كبير محلي يعمل على نظامك لإنشاء ملخص موجه للمستثمرين.

## ما ستتعلمه

- كيفية تثبيت وتشغيل n8n
- استيراد وتهيئة سير عمل مُعد مسبقًا
- الاتصال بـ Lemonade باستخدام التكامل الأصلي في n8n
- فهم عُقد سير العمل وتدفق البيانات

## ما هو Lemonade؟

[Lemonade](https://lemonade-server.ai) هي منصة تقديم نماذج لغوية كبيرة محلية مصممة خصيصًا لعتاد AMD. توفر واجهة برمجة تطبيقات متوافقة مع OpenAI تعمل بالكامل على جهازك - بياناتك لا تغادر جهازك أبدًا.

في هذا الدليل التعليمي، نستخدم Lemonade لتقديم نموذج لغوي كبير محلي تتصل به n8n لأداء مهام مدعومة بالذكاء الاصطناعي.

تتضمن n8n **عقدة Lemonade أصلية** (`Lemonade Chat Model`) توفر تكاملاً من الدرجة الأولى - دون الحاجة إلى تهيئة يدوية. هذا يجعل ربط نموذجك اللغوي الكبير المحلي بسير عمل الأتمتة أمرًا بسيطًا ومباشرًا.

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## تثبيت n8n
<!-- @os:windows -->
قم بتثبيت n8n عالميًا باستخدام npm.

> **ملاحظة**: قد تلاحظ ظهور بعض تحذيرات npm. هذا أمر متوقع.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (على سبيل المثال،
> بتعيينها إلى RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **مشكلة PATH**: إذا أظهر الأمر `n8n --version` رسالة تفيد بأن الأمر غير موجود، فتأكد من أن دليل npm العالمي (global bin) موجود ضمن متغير `PATH` الخاص بالمستخدم. مسار التثبيت المعتاد هو `C:\Users\<username>\AppData\Roaming\npm`.
> أضف هذا المسار إلى مسار المستخدم (Edit the system environment variables > Environment Variables > Edit User Path) ثم أعد تحميل الطرفية.

<!-- @os:end -->

<!-- @os:linux -->
سنستخدم الآن خدمة Podman لتحويل تثبيت n8n الخاص بنا إلى حاوية.

يرجى تنزيل الملف التالي إلى دليل من اختيارك: [compose.yml](assets/compose.yml)

في ذلك الدليل، قم بتشغيل الأمر التالي:
```bash
podman compose up -d
```

يجب أن يقوم هذا بتثبيت n8n والكتابة إلى تخزين دائم.

قم بتشغيل n8n عن طريق كتابة `localhost:5678` في شريط عنوان المتصفح.
<!-- @os:end -->

<!-- @os:windows -->
## تشغيل n8n

ابدأ تشغيل n8n من الطرفية:

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

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

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
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
يقوم n8n بتشغيل خادم ويب محلي. اضغط على `'o'` أو افتح متصفحك على العنوان `http://localhost:5678` للوصول إلى المحرر.
<!-- @os:end -->


> **تلميح**: أبقِ نافذة الطرفية مفتوحة أثناء استخدام n8n. إغلاقها قد يوقف الخادم.

## تشغيل Lemonade

Lemonade هو الخادم المحلي الذي سيشغل نموذجًا ويتصل بـ n8n.

<!-- @os:linux -->
افتح واجهة Lemonade الرسومية بالنقر على أيقونة Lemonade في شريط المهام. يمكنك من هنا تصفح النماذج والخلفيات (backends) وتحميل النماذج المثبتة مسبقًا.
<!-- @os:end -->

<!-- @os:windows -->
افتح واجهة Lemonade الرسومية بالنقر على أيقونة Lemonade. انقر بزر الماوس الأيمن على أيقونة شريط النظام لفتح التطبيق. بعد ذلك، يمكنك إضافة النماذج والخلفيات (backends) وتحميل النماذج المثبتة مسبقًا.
<!-- @os:end -->

>**تلميح**: بمجرد التشغيل، يمكن أيضًا الوصول إلى واجهة Lemonade الرسومية عبر الرابط http://localhost:13305

بدلاً من ذلك، يمكنك فتح طرفية وتشغيل `lemonade list` لمعرفة النماذج المثبتة. ثم قم بتشغيل:

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

> **تلميح**: إذا تعذر عليك الوصول إلى حسابك، جرّب `n8n user-management:reset`

### الخطوة 2: استيراد سير العمل

لقد وفّرنا لك سير عمل مُعدًا مسبقًا يمكنك استيراده مباشرة:

1. قم بتنزيل ملف سير العمل التالي: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. انقر على **Start from Scratch** لفتح محرر سير العمل. بدلاً من ذلك، انقر على زر + في أعلى اليسار، ثم **Add workflow**.
3. انقر على قائمة **...** (النقاط الثلاث) في الشريط العلوي الأيمن واختر **Import from file**
4. اختر ملف `financial-news-workflow.json` الذي قمت بتنزيله
5. سيظهر سير العمل على لوحة العمل
### الخطوة 3: فهم سير العمل

يحتوي سير العمل المستورد على 9 عقد متصلة:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| العقدة | الغرض |
|------|---------|
| **When clicking 'Execute workflow'** | مشغّل يدوي لبدء سير العمل |
| **Fetch Financial News Webpage** | طلب HTTP GET إلى `https://apnews.com/business` |
| **Delay to Ensure Page Load** | عقدة انتظار للتأكد من تحميل محتوى الصفحة بالكامل |
| **Extract News Headlines & Text** | عقدة HTML تستخرج العناوين الرئيسية، ومختارات المحرر، والأخبار الرئيسية، والأخبار الإقليمية باستخدام محددات CSS |
| **Clean Extracted News Data** | عقدة Set تدمج جميع البيانات المستخرجة في حقل نصي واحد |
| **AI Financial News Summarizer** | وكيل ذكاء اصطناعي يعالج الأخبار باستخدام موجه نظام خاص بمحلل مالي |
| **Lemonade Chat Model** | يتصل بخادم Lemonade المحلي الذي يشغّل نموذج اللغة الكبير |
| **Structured Output Parser** | ينسّق مخرجات الذكاء الاصطناعي كـ JSON منظم |
| **Convert to File** | يحوّل الملخص إلى ملف قابل للتنزيل |

### الخطوة 4: تهيئة بيانات اعتماد Lemonade

قبل تشغيل سير العمل، تحتاج إلى ربطه بخادم Lemonade المحلي:

1. انقر نقرًا مزدوجًا على عقدة **Lemonade Chat Model** في n8n
2. من القائمة المنسدلة **Credential to connect with** اختر **Create New Credential**
3. أدخل القيم في الجدول أدناه ثم انقر على الحفظ.
4. اختر النموذج المناسب الذي قمت بتحميله في Lemonade Server.

  | الحقل | القيمة |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **ملاحظة**: قبل الاختبار، شغّل `lemonade status` في الطرفية للتأكد من أن خادم Lemonade يعمل.
<!-- @device:halo_box -->
> يستخدم سير العمل هذا نموذج GPT-OSS-120B، وهو مثبت مسبقًا في Lemonade. يمكنك تغيير ذلك إلى نماذج أخرى محمّلة في إعدادات عقدة Lemonade Chat Model.
<!-- @device:end -->

### الخطوة 5: اختبار سير العمل

1. تأكد من أن Lemonade يعمل مع نموذج محمّل
2. انقر على **Execute workflow** في أسفل منتصف اللوحة
3. راقب تنفيذ كل عقدة من اليسار إلى اليمين — تتحول إلى اللون الأخضر عند الانتهاء
4. انقر نقرًا مزدوجًا على عقدة **AI Financial News Summarizer** لرؤية الملخص المُنشأ في اللوحة السفلية.
5. انقر نقرًا مزدوجًا على عقدة **Convert to File** لتنزيل ملف النص المقابل من اللوحة السفلية.

## فهم وكيل الذكاء الاصطناعي

يستخدم AI Financial News Summarizer موجه نظام مصمم للتحليل المالي:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

يستقبل الوكيل بيانات الأخبار المنظّفة ويُخرج ملخصًا منظمًا مع معنويات السوق.

### حفظ سير العمل الخاص بك

انقر على اسم سير العمل في الأعلى وأعد تسميته إذا رغبت. تُحفظ سير العمل تلقائيًا أثناء العمل.

## الخطوات التالية

- **جدولة الأتمتة**: استبدل Manual Trigger بـ **Schedule Trigger** لتشغيله يوميًا
- **إرسال الإشعارات**: أضف عقدة **Discord** أو **Slack** أو **Email** لتلقي الملخصات
- **جرّب نماذج مختلفة**: غيّر النموذج في عقدة Lemonade Chat Model لتجربة نماذج لغة كبيرة مختلفة
- **تخصيص الاستخراج**: عدّل محددات CSS في عقدة HTML Extract لاستهداف أقسام أخبار مختلفة
- **جرّب خلفيات مختلفة**: يدعم n8n أيضًا [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)، و LM Studio، وخلفيات نماذج لغة محلية أخرى

### استكشاف قوالب n8n

يحتوي n8n على مئات القوالب الجاهزة لسير العمل. تصفّح مكتبة القوالب الرسمية على:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

ابحث عن "AI" أو "LLM" أو "automation" للعثور على سير عمل يمكنك استيراده وتخصيصه.

لمزيد من المعلومات، راجع [توثيق n8n](https://docs.n8n.io/).