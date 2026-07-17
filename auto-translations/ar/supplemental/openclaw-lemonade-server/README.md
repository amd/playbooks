<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# تشغيل OpenClaw مع Lemonade Server كخلفية

## نظرة عامة

[**OpenClaw**](https://openclaw.ai/) هو وكيل ذكاء اصطناعي مستقل يمكنه كتابة التعليمات البرمجية وتشغيلها، وإدارة الملفات، والعمل على مهام معقدة متعددة الخطوات نيابةً عنك. على عكس مساعد الدردشة الذي يجيب على الأسئلة فحسب، يتخذ OpenClaw إجراءات حقيقية على نظامك، مما يعني أنه يحتاج إلى خلفية ذكاء اصطناعي سريعة وقادرة تواكب حلقة الوكيل المتطلبة.

[**Lemonade Server**](https://lemonade-server.ai/) هو تلك الخلفية. إنه خادم استدلال محلي مفتوح المصدر يشغّل نماذج الذكاء الاصطناعي التوليدي مباشرةً على أجهزتك ويعرضها من خلال واجهة برمجة التطبيقات OpenAI القياسية في الصناعة.

معاً، يشكّلان مجموعة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade الاستدلال على النماذج، ويوفر OpenClaw حلقة الوكيل التي تحوّل مخرجات النموذج إلى إجراءات حقيقية.

> **قبل المتابعة:** OpenClaw هو وكيل ذكاء اصطناعي عالي الاستقلالية. قد يؤدي منح أي وكيل ذكاء اصطناعي وصولاً إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه البرامج المستقلة التي تتصرف نيابةً عنك.

---

## ما ستتعلمه

بنهاية هذا الدليل ستكون قادراً على:

- التعرف على **Lemonade Server**
- **تثبيت OpenClaw** و**توجيهه نحو Lemonade Server** كخلفية للذكاء الاصطناعي.
- **تشغيل بوابة OpenClaw** والتأكد من جاهزية وكيلك للعمل.
- **ربط قناة تواصل** (Discord أو Telegram) حتى تتمكن من الدردشة مع وكيلك من أي جهاز.

---

## ضبط إعداد الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة Linux مبنية على Debian متوافقة مع `apt-get`
- ذاكرة وصول عشوائي لا تقل عن **12 جيجابايت** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (اختياري، لعزل OpenClaw في بيئة محمية)

- **~10–30 جيجابايت من مساحة القرص الحرة** لأوزان النموذج
<!-- @os:end -->
<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- ذاكرة وصول عشوائي لا تقل عن **12 جيجابايت** (يُوصى بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **~10–30 جيجابايت من مساحة القرص الحرة** لأوزان النموذج
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (اختياري، لعزل OpenClaw في بيئة محمية)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب النموذج الموصى به وتحميله

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تبلغ 263 ألف رمز مناسب جداً لأعباء عمل الوكيل. يستخدم هذا النموذج تكميماً من نوع UD-Q4_K_XL. اسحبه الآن:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

ثم حمّله بنافذة سياق كبيرة واحفظ هذا الإعداد للتشغيلات المستقبلية:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزاً. إذا واجهت أخطاء نفاد الذاكرة (OOM)، فكّر في تقليل نافذة السياق. ومع ذلك، نظراً لأن Qwen3.6 يستفيد من السياق الموسّع للمهام المعقدة، نوصي بالحفاظ على طول سياق لا يقل عن 128 ألف رمز للحفاظ على قدرات التفكير.

> **نصيحة: تعطيل التفكير للحصول على استجابات وكيل أسرع:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضياً، مما يضيف تأخيراً قبل كل استجابة. في حلقات الوكيل، يتراكم هذا التأخير بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) إعداداً جاهزاً يعطّل التفكير. لاستخدامه، نزّل الملف واستورده:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
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
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## إعداد WSL

نشغّل OpenClaw داخل WSL (موصى به) ونربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة shell لنظام Linux لـ OpenClaw مع الحفاظ على تسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL وUbuntu

افتح PowerShell بصلاحيات المسؤول وثبّت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم ثبّت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

شغّل هذا الأمر داخل طرفية Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

أعد تشغيل WSL:

```powershell
wsl --shutdown
wsl
```

### ربط Lemonade من Windows إلى WSL

يعمل WSL2 في شبكة افتراضية. يرتبط Lemonade على Windows بـ `127.0.0.1`، وهو عنوان لا يمكن لـ WSL الوصول إليه مباشرةً. يقوم وكيل منفذ Windows بإعادة توجيه حركة المرور من عنوان IP بوابة WSL إلى المضيف المحلي لـ Windows.

**ابحث عن عنوان IP لبوابة WSL** (شغّل داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (شغّل في PowerShell بصلاحيات المسؤول، مستبدلاً `<WSL-Gateway-IP>` بعنوان IP لبوابة WSL الخاصة بك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار الحماية** (في نفس PowerShell المرفوع الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد حمّلت نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، يجب أن ترى مخرجات JSON كالتالي:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> تبقى قاعدة `netsh portproxy` بعد إعادة التشغيل، لكن عنوان IP لبوابة WSL قد يتغير بعد `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، احصل على عنوان IP المحدّث للبوابة وحدّث الوكيل بهذا العنوان الجديد.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## تثبيت OpenClaw وتهيئته

### تثبيت OpenClaw
<!-- @os:windows -->
> شغّل الأوامر في هذا القسم داخل **طرفية WSL** الخاصة بك.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

تتخطى علامة `--no-onboard` معالج الإعداد التفاعلي، وستقوم بتهيئة خلفية النموذج يدوياً في الخطوة التالية، مما يمنحك تحكماً دقيقاً في النموذج والخادم المستخدمَين.

افتح طرفية جديدة وتأكد من التثبيت:

```bash
openclaw --version
```

> **نصيحة:** إذا رأيت `command not found` بعد التثبيت، أضف دليل bin العام لـ npm إلى PATH الخاص بك:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> لجعل هذا دائماً، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### تهيئة OpenClaw لاستخدام Lemonade

قم بتشغيل الإعداد التلقائي غير التفاعلي لـ OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

يكتب هذا الأمر تهيئة OpenClaw إلى `~/.openclaw/openclaw.json`.

> **تحديد حجم نافذة السياق في OpenClaw:** يُشغَّل ضغط OpenClaw عندما يكون `contextTokens > contextWindow − reserveTokens`. القيمة الافتراضية لـ `reserveTokensFloor` هي 20,000 رمز، وهي حد أدنى يتجاوز `reserveTokens` عند انخفاضه، لذا فإن أي سياق نموذج أقل من ~37k سيؤدي إلى حلقة ضغط لا نهائية. اضبط احتياطيًا منخفضًا وعطّل الحد الأدنى مرة واحدة في تهيئتك وسيُطبَّق على كل نموذج، دون الحاجة إلى ضبط لكل نموذج على حدة:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` هو *حد أدنى* (حارس الحد الأدنى)، وليس الاحتياطي نفسه، فضبط الحد الأدنى فقط لا يُحدث أي تأثير. `reserveTokensFloor: 0` يعطّل الحارس بحيث يُقبل `reserveTokens` الأدنى.
>
> **متى تُطبّق هذا:** استخدم هذه التهيئة إذا كانت نافذة السياق الفعّالة لنموذجك أقل من ~37k، إما لأن النموذج صغير (مثل 8k أو 16k أو 32k) أو لأنك قيّدتها عمدًا إلى قيمة أدنى (مثل تحميل نموذج 128k لكن ضبط السياق على 16k في Lemonade). بدونها، يدخل OpenClaw في حلقة ضغط لا نهائية عند بدء التشغيل.
>
> **نماذج السياق الكبير بسياق كامل:** يمكنك تخطي هذا تمامًا. تعمل الإعدادات الافتراضية بشكل جيد، إذ سيبدأ الضغط قبل امتلاء النافذة وللنموذج مساحة كافية لتوليد ردود طويلة. إذا طبّقته، فاعلم أن `reserveTokens: 4096` يحدّ من طول الرد إلى ~4k رمز، مما قد يقطع توليد الملفات الطويلة أو الخطط التفصيلية.
>
> **أين تُضيف هذا:** ضع كتلة `compaction` داخل `agents.defaults` في ملف `openclaw.json` (عادةً في `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> يبقى باقي تهيئتك (البوابة والقنوات والنماذج وغيرها) دون تغيير، ولا يحتاج إلا مفتاح `compaction` إلى الإضافة.

### (موصى به) تفعيل عزل Docker

يمكن لـ OpenClaw توجيه جميع عمليات الملفات والكود الخاصة بالوكيل عبر حاوية Docker معزولة بدلًا من تشغيلها مباشرةً على مضيفك. يحدّ هذا من نطاق أي إجراء غير مقصود داخل بيئة العزل، مع إبقاء نظام ملفات المضيف والشبكة بمنأى عن أي تأثير.

أنشئ صورة بيئة العزل مرة واحدة (يجب أن يكون Docker مثبتًا):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

شغّل هذا لإضافة مفتاح `sandbox` داخل كتلة `agents.defaults` الموجودة في `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

لا تملك حاويات بيئة العزل **أي وصول إلى الشبكة** بشكل افتراضي. راجع [مرجع العزل](https://docs.openclaw.ai/gateway/sandboxing) للاطلاع على ربط التحميل وتجاوزات الشبكة.

> #### استكشاف الأخطاء وإصلاحها: رفض إذن Docker
> 
> إذا حصلت على خطأ "permission denied" عند تشغيل أوامر Docker:
> 
> **الخطوة 1: أضف مستخدمك إلى مجموعة docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **الخطوة 2: إذا استمر الخطأ، طبّق الإصلاح الدائم**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> ثم **أعد تشغيل** نظامك.
> 
> **إصلاح مؤقت سريع** (يُعاد ضبطه بعد إعادة التشغيل):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### تشغيل بوابة OpenClaw

البوابة هي عملية OpenClaw التي تدير حلقة الوكيل وتخدم لوحة التحكم:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

لفتح لوحة التحكم، شغّل هذا في طرفية ثانية بينما لا تزال البوابة تعمل:

```bash
openclaw dashboard
```

نظرًا لأن البوابة ترتبط بـ loopback، تُجري لوحة التحكم المصادقة تلقائيًا عند فتحها من الجهاز نفسه، دون الحاجة إلى إدخال رمز أو الموافقة على الجهاز للوصول المحلي. يجب أن ترى لوحة تحكم OpenClaw مع نموذج Lemonade الخاص بك مدرجًا كخلفية نشطة.

> إذا كنت قد فعّلت العزل، يمكنك التحقق منه بطلب من الوكيل `run hostname` من لوحة التحكم. إذا رأيت معرّف حاوية قصيرًا بدلًا من اسم مضيف جهازك، فإن بيئة العزل تعمل.

**تهانينا، لقد بنيت مكدسًا كاملًا من الوكيل الذكاء الاصطناعي المحلي من الصفر.**

> **هل تحتاج إلى رمز البوابة؟** شغّل `openclaw dashboard --no-open` لطباعة عنوان URL للوحة التحكم مع الرمز مضمّنًا (كما يحاول نسخه إلى الحافظة). بدلًا من ذلك، يوجد الرمز في `gateway.auth.token` داخل `~/.openclaw/openclaw.json`.
>
> **الموافقة على جهاز بعيد:** عند فتح لوحة التحكم من جهاز ثانٍ أو هاتف، يعرض المتصفح معرّف طلب. على الجهاز الذي يشغّل البوابة، شغّل:
> ```bash
> openclaw devices approve <requestId>
> ```
> هذا مطلوب فقط للأجهزة البعيدة أو الثانوية، إذ يُجري وصول loopback من الجهاز نفسه المصادقة تلقائيًا.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## اختياري: توصيل قناة اتصال

بمجرد تشغيل البوابة، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. اختر الخيار الذي يناسب إعدادك. يدعم OpenClaw [Discord](https://docs.openclaw.ai/channels/discord) و[Telegram](https://docs.openclaw.ai/channels/telegram) وقنوات أخرى، راجع القائمة الكاملة على [docs.openclaw.ai](https://docs.openclaw.ai).

---

### الخيار أ: Discord

يتطلب Discord خادمًا تمتلك فيه **صلاحيات المسؤول** لإضافة بوت. إذا كنت تشارك في خوادم لكنك لا تملك أيًا منها، استخدم الخيار ب (Telegram) بدلًا من ذلك.
#### إنشاء حساب وخادم على Discord

إذا لم يكن لديك حساب على Discord، سجّل في [discord.com](https://discord.com). تحتاج أيضاً إلى خادم تكون فيه مسؤولاً، أنشئ واحداً بالنقر على أيقونة **+** في الشريط الجانبي لـ Discord واختيار **Create My Own**. الخادم الخاص مناسب تماماً.

#### إنشاء تطبيق وبوت على Discord

1. انتقل إلى [Discord Developer Portal](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسماً (مثلاً "openclaw-bot").
2. في الشريط الجانبي، انقر على **Bot**. حدد اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرر للأسفل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرر للأعلى مجدداً وانقر على **Reset Token** لإنشاء رمز البوت. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر على **OAuth2/ URL Generator**.
2. تحت **Scopes**، فعّل `bot` و`applications.commands`.
3. تحت **Bot Permissions**، فعّل: View Channels، Send Messages، Read Message History، Embed Links، Attach Files.
4. انسخ الرابط المُنشأ، الصقه في متصفحك، اختر خادمك، وأكّد. يجب أن يظهر البوت الآن في قائمة أعضاء خادمك.

#### جمع معرّفاتك

فعّل وضع المطوّر في Discord (**User Settings/ Advanced/ Developer Mode**)، ثم:
- انقر بزر الماوس الأيمن على أيقونة خادمك: **Copy Server ID**
- انقر بزر الماوس الأيمن على صورتك الرمزية: **Copy User ID**

#### السماح بالرسائل المباشرة من أعضاء الخادم

انقر بزر الماوس الأيمن على أيقونة خادمك/ **Privacy Settings**/ فعّل **Direct Messages**. يتيح هذا للبوت إرسال رسائل مباشرة إليك، وهو مطلوب لخطوة الإقران.

#### تهيئة OpenClaw لـ Discord

خزّن رمز البوت كمتغير بيئة، ثم أنشئ ملف تصحيح واحد يُفعّل Discord، ويشير إلى الرمز، ويضع خادمك في القائمة البيضاء. استبدل `<server_id>` و`<user_id>` بالمعرّفات التي جمعتها أعلاه.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **لا تعتمد على طلب تهيئة هذا من الوكيل.** عند تفعيل وضع الحماية، لا يستطيع الوكيل الكتابة إلى `~/.openclaw/openclaw.json` من داخل بيئة الحماية، استخدم أوامر CLI أعلاه على المضيف بدلاً من ذلك.

أعد تشغيل البوابة لتلتقط تهيئة القناة الجديدة:

```bash
openclaw gateway run --bind loopback --port 18789
```

يجب أن ترى `logged in to discord as <bot-name>` في مخرجات البوابة خلال ثوانٍ قليلة.

#### إقران حساب Discord الخاص بك

أرسل رسالة مباشرة للبوت في Discord. سيرد بكود إقران قصير.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

وافق عليه على الجهاز الذي يشغّل OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> تنتهي صلاحية أكواد الإقران بعد ساعة واحدة.

يمكنك الآن الدردشة مع وكيلك مباشرةً من Discord وإسناد المهام إلى أجهزتك المحلية.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### الخيار B: Telegram

Telegram أبسط من Discord لمعظم المستخدمين، إذ لا يتطلب خادماً ولا صلاحيات مسؤول.

#### إنشاء بوت على Telegram

1. افتح Telegram وراسل **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يمنحك إياه.

#### تهيئة OpenClaw لـ Telegram

خزّن الرمز كمتغير بيئة:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

أضف تهيئة القناة إلى `~/.openclaw/openclaw.json` (أو طبّقها عبر لوحة التحكم):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

أعد تشغيل البوابة، ثم أرسل أي رسالة لبوتك في Telegram. وافق على الإقران:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

تنتهي صلاحية أكواد الإقران بعد ساعة واحدة. يمكنك الآن الدردشة مع وكيلك عبر رسائل Telegram المباشرة.

---

## الخطوات التالية

الآن بعد أن أصبح وكيلك قادراً على تلقّي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخّص سوق الأسهم**: جدوِل OpenClaw لجلب البيانات من واجهات برمجة التطبيقات المالية على فترات منتظمة، ولخّص تحركات اليوم باستخدام نموذجك المحلي، وأرسل ملخصاً إلى هاتفك كل صباح عبر القناة التي تختارها.

2. **مراقب الضبط الدقيق**: ابدأ مهمة تدريب عن بُعد عبر Telegram أو Discord، ثم اجعل الوكيل يتابع سجل التدريب ويُرسل إلى هاتفك قيم الخسارة الدورية واستخدام GPU والمساحة على القرص. إذا توقف التشغيل أو ارتفع استخدام VRAM، ستعلم بذلك فوراً دون الحاجة إلى التواجد أمام الجهاز.

3. **إنترنت الأشياء مع نموذج رؤية محلي**: وجّه كاميرا نحو بابك الأمامي، وشغّل نموذج رؤية على Lemonade، واجعل OpenClaw يحلل الإطارات عند الطلب أو عند تفعيل مشغّل معين. اسأل "هل وصلت أي طرود اليوم؟" من هاتفك واحصل على إجابة مباشرة من أجهزتك الخاصة.