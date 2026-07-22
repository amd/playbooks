<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# تشغيل OpenClaw باستخدام Lemonade Server كخلفية

## نظرة عامة

[**OpenClaw**](https://openclaw.ai/) هو عميل ذكاء اصطناعي مستقل يمكنه كتابة الكود وتشغيله، وإدارة الملفات، وإنجاز مهام متعددة الخطوات ومعقدة نيابةً عنك. على عكس مساعد المحادثة الذي يكتفي بالإجابة على الأسئلة، يقوم OpenClaw باتخاذ إجراءات فعلية على نظامك، مما يعني أنه يحتاج إلى خلفية ذكاء اصطناعي سريعة وقادرة تستطيع مواكبة حلقة عمل العميل المتطلبة.

[**Lemonade Server**](https://lemonade-server.ai/) هو تلك الخلفية. إنه خادم استدلال محلي مفتوح المصدر يقوم بتشغيل نماذج GenAI مباشرةً على جهازك ويعرضها من خلال واجهة برمجة تطبيقات OpenAI القياسية في هذا المجال.

معًا، يشكّلان مجموعة عمل كاملة لعميل ذكاء اصطناعي محلي بالكامل: يتولى Lemonade عملية استدلال النموذج، بينما يوفّر OpenClaw حلقة عمل العميل التي تُحوّل مخرجات النموذج إلى إجراءات فعلية.

> **قبل المتابعة:** OpenClaw هو عميل ذكاء اصطناعي عالي الاستقلالية. منح أي عميل ذكاء اصطناعي صلاحية الوصول إلى نظامك قد يؤدي إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه قيام برنامج مستقل بالتصرف نيابةً عنك.

---

## ما ستتعلمه

بنهاية هذا الدليل ستكون قادرًا على:

- التعرف على **Lemonade Server**
- **تثبيت OpenClaw** و**توجيهه إلى Lemonade Server** كخلفية ذكاء اصطناعي له.
- **تشغيل بوابة OpenClaw** والتأكد من جاهزية عميلك للعمل.
- **ربط قناة تواصل** (Discord أو Telegram) حتى تتمكن من التحدث مع عميلك من أي جهاز.

---

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة لينكس مبنية على Debian ومتوافقة وتدعم `apt-get`
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (اختياري، لعزل OpenClaw)

- **حوالي 10-30 جيجابايت من مساحة القرص الفارغة** لأوزان النموذج
<!-- @os:end -->
<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **حوالي 10-30 جيجابايت من مساحة القرص الفارغة** لأوزان النموذج
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (اختياري، لعزل OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب وتحميل النموذج الموصى به

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تصل إلى 263 ألف رمز مميز، وهو مناسب جدًا لأعباء عمل العملاء. يستخدم هذا النموذج ضغط UD-Q4_K_XL. قم بسحبه الآن:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

ثم قم بتحميله بنافذة سياق كبيرة واحفظ هذا الإعداد للتشغيلات المستقبلية:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزًا مميزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، فكّر في تقليل نافذة السياق. ومع ذلك، نظرًا لأن Qwen3.6 يستفيد من السياق الموسّع للمهام المعقدة، ننصح بالحفاظ على طول سياق لا يقل عن 128 ألف رمز مميز للحفاظ على قدرات التفكير.

> **نصيحة: عطّل التفكير للحصول على استجابات أسرع من العميل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، مما يضيف زمن انتقال قبل كل استجابة. بالنسبة لحلقات عمل العملاء، يتراكم هذا العبء بسرعة. يوفّر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تهيئة جاهزة تعطّل التفكير. لاستخدامها، قم بتنزيل الملف واستيراده:
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

نقوم بتشغيل OpenClaw داخل WSL (موصى به) وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة سطر أوامر لينكس لـ OpenClaw مع الحفاظ على تسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL و Ubuntu

افتح PowerShell كمسؤول (Administrator) وقم بتثبيت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم قم بتثبيت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

قم بتشغيل هذا داخل طرفية Ubuntu:

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

يعمل WSL2 ضمن شبكة افتراضية. يرتبط Lemonade على Windows بالعنوان `127.0.0.1`، والذي لا يستطيع WSL الوصول إليه مباشرةً. يقوم وكيل منفذ Windows (Windows port proxy) بإعادة توجيه حركة المرور من عنوان بوابة WSL إلى المضيف المحلي (localhost) على Windows.

**اعثر على عنوان بوابة WSL الخاص بك** (قم بالتشغيل داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (قم بالتشغيل في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان بوابة WSL الخاص بك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**أضف قاعدة جدار حماية** (في نفس نافذة PowerShell المرتفعة الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من ذلك من داخل WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد قمت بالفعل بتحميل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فيجب أن ترى مخرجات JSON مثل هذه:

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

> تبقى قاعدة `netsh portproxy` فعّالة بعد إعادة التشغيل، لكن عنوان بوابة WSL قد يتغيّر بعد تنفيذ `wsl --shutdown`. إذا أصبح Lemonade غير قابل للوصول من WSL بعد إعادة التشغيل، احصل على عنوان البوابة المحدّث وقم بتحديث الوكيل بهذا العنوان الجديد.

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

## تثبيت وضبط OpenClaw

### تثبيت OpenClaw
<!-- @os:windows -->
> قم بتنفيذ الأوامر في هذا القسم داخل **طرفية WSL** الخاصة بك.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

تُتيح لك العلامة `--no-onboard` تخطي معالج الإعداد التفاعلي، حيث ستقوم بضبط خلفية النموذج يدويًا في الخطوة التالية، مما يمنحك تحكمًا دقيقًا في النموذج والخادم المستخدمَين.

افتح طرفية جديدة وتحقق من التثبيت:

```bash
openclaw --version
```

> **نصيحة:** إذا ظهرت لك رسالة `command not found` بعد التثبيت، أضف مجلد npm العام (global bin) إلى متغير PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> لجعل هذا التغيير دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

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

قم بتشغيل عملية الإعداد غير التفاعلية الخاصة بـ OpenClaw.
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

يقوم هذا الأمر بكتابة تهيئة OpenClaw إلى `~/.openclaw/openclaw.json`.

> **تحديد حجم نافذة السياق في OpenClaw:** يتم تفعيل عملية الضغط (compaction) في OpenClaw عندما تكون `contextTokens > contextWindow − reserveTokens`. القيمة الافتراضية لـ `reserveTokensFloor` هي 20,000 رمز (token)، وهي حد أدنى يتجاوز `reserveTokens` عندما تكون قيمته أقل، لذا فإن أي نافذة سياق للنموذج أقل من حوالي 37 ألف رمز ستؤدي إلى حلقة ضغط لا نهائية. اضبط قيمة احتياطي منخفضة وعطّل الحد الأدنى مرة واحدة في تهيئتك، وسيُطبَّق ذلك على كل نموذج، دون الحاجة لضبط منفصل لكل نموذج:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` هو *حد أدنى* (ضمانة دنيا)، وليس الاحتياطي نفسه، لذا فإن ضبط الحد الأدنى فقط لن يكون له أي تأثير. تعطيل `reserveTokensFloor: 0` يُلغي هذه الضمانة بحيث يتم قبول قيمة `reserveTokens` الأقل.

>
> **متى يتم تطبيق ذلك:** استخدم هذه التهيئة إذا كانت نافذة السياق الفعلية لنموذجك أقل من حوالي 37 ألف رمز، سواء لأن النموذج صغير (مثل 8 آلاف أو 16 ألف أو 32 ألف رمز) أو لأنك قمت عمداً بتحديدها بقيمة أقل (مثل تحميل نموذج بسعة 128 ألف رمز مع ضبط السياق على 16 ألف رمز في Lemonade). بدون ذلك، سيدخل OpenClaw في حلقة ضغط لا نهائية عند بدء التشغيل.
>
> **النماذج ذات السياق الكبير عند السعة الكاملة:** يمكنك تخطي هذا الأمر بالكامل. الإعدادات الافتراضية تعمل بشكل جيد، حيث ستبدأ عملية الضغط قبل امتلاء النافذة بوقت كافٍ، وسيتوفر للنموذج مساحة كافية لتوليد استجابات طويلة. إذا قمت بتطبيق ذلك، فاعلم أن `reserveTokens: 4096` يحد من طول الاستجابة إلى حوالي 4 آلاف رمز، مما قد يؤدي إلى قطع عملية توليد الملفات الطويلة أو الخطط التفصيلية.
>
> **أين يتم إضافة ذلك:** ضع كتلة `compaction` داخل `agents.defaults` في ملف `openclaw.json` الخاص بك (عادةً في `~/.openclaw/openclaw.json`):
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
> باقي إعداداتك (البوابة، القنوات، النماذج، إلخ) تبقى دون تغيير، ولا يلزم إضافة سوى مفتاح `compaction`.

### (موصى به) تفعيل العزل بواسطة Docker

يمكن لـ OpenClaw توجيه جميع عمليات الملفات والتعليمات البرمجية الخاصة بالعميل عبر حاوية Docker معزولة بدلاً من تشغيلها مباشرة على جهازك المضيف. يحد هذا من نطاق تأثير أي إجراء غير مقصود ليقتصر على بيئة العزل، مع ترك نظام ملفات جهازك المضيف وشبكته دون أي تأثير.

قم ببناء صورة العزل (sandbox) مرة واحدة (يجب أن يكون Docker مثبتاً):

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

قم بتشغيل هذا الأمر لإضافة المفتاح `sandbox` داخل كتلة `agents.defaults` الموجودة في `~/.openclaw/openclaw.json`:

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

لا تتوفر لحاويات العزل (sandbox) أي إمكانية وصول للشبكة **network access** افتراضياً. راجع [مرجع العزل](https://docs.openclaw.ai/gateway/sandboxing) للاطلاع على نقاط الربط (bind mounts) وتجاوزات الشبكة.

> #### استكشاف الأخطاء وإصلاحها: رفض الإذن في Docker
> 
> إذا حصلت على رسالة "permission denied" عند تشغيل أوامر Docker:
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
> **الخطوة 2: إذا استمر الخطأ، طبّق الحل الدائم**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> ثم قم **بإعادة تشغيل** نظامك.
> 
> **حل مؤقت سريع** (يُعاد ضبطه بعد إعادة التشغيل):
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

<!-- @os:linux -->
## (موصى به) تكامل OpenClaw مع خدمات Firecrawl

يوفر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة استضافة ذاتية لزحف الويب واستخراج المحتوى يمكنها تجاوز هذه التحديات وإطلاق العنان للإمكانات الكاملة لأتمتة OpenClaw.

في هذا الإعداد، يعمل OpenClaw كمجموعة من حاويات Docker يتم إدارتها بواسطة Podman. لتبسيط إدارة دورة الحياة والبدء التلقائي، نقوم بتسجيل Firecrawl كخدمة `systemd` على مستوى المستخدم تقوم بتنسيق مجموعة Podman Compose الأساسية. يتيح هذا لـ OpenClaw بدء تشغيل البوابة وإيقافها والتحقق من خدمة Firecrawl باستخدام أوامر `systemctl --user` القياسية بدلاً من التفاعل مع الحاويات مباشرة.

للحفاظ على البساطة، قمنا بتقسيم العملية بأكملها إلى أربع خطوات:

---

### 1. تسجيل خدمة النظام
انتقل إلى دليل تهيئة مستخدم systemd:
```bash
cd ~/.config/systemd/user
```
أنشئ وافتح ملفاً جديداً باسم `firecrawl.service`.
```bash
nano firecrawl.service
```
انسخ والصق التهيئة التالية:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
في هذه المرحلة، تم تعريف الخدمة ولكن لم يتم تسجيلها بعد لدى `systemd`.
تأكد من أن اسم الملف يطابق تماماً ما قمت بإنشائه أعلاه، ثم قم بتشغيل:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
إذا نجحت العملية، يجب أن تظهر لك المخرجات التالية:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

يحتوي `default.target.wants/` على روابط رمزية للخدمات التي تم تهيئتها لبدء التشغيل تلقائياً.
### 2. تهيئة Firecrawl

يُعد [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) خيارًا مثاليًا لمن يحتاجون إلى التحكم الكامل في بيئات الاستخلاص ومعالجة البيانات الخاصة بهم، لكنه يأتي مقابل مجهود إضافي في الصيانة والتهيئة.

ابدأ باستنساخ المستودع:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
أنشئ ملف `.env` في المجلد الجذري `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. نشر OpenClaw باستخدام Podman Compose

قبل المتابعة، تأكد من أنك قمت بسحب أحدث صورة OpenClaw Docker:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
بعد الانتهاء من ذلك، قم بتنزيل ملف OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) وضعه في المجلد الجذري `/firecrawl`:

> هذا الاتفاق مطلوب حتى يتمكن `systemd` من تحديد الخدمة وبدء تشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع المكدس بإضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة OpenClaw عبر Firecrawl 

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح عن طريق تشغيل المكدس يدويًا:
```bash
podman compose -f openclaw-compose.yaml up -d
```
إذا تمت التهيئة بشكل صحيح، فيجب أن ترى حاوية OpenClaw تعمل، وينبغي أن يبدو مخرج سطر الأوامر لديك مشابهًا لهذا:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

بعد التحقق، أوقف المكدس قبل المتابعة:
```bash
podman compose -f openclaw-compose.yaml down
```
قبل بدء تشغيل الخدمة، يجب عليك التأكد من ضبط الملكية والأذونات الصحيحة على مجلد `firecrawl` وملف `.env` الخاص به. 
هذا أمر ضروري لتتمكن الخدمة من كتابة بيانات الاعتماد الخاصة بك عند بدء التشغيل.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
الآن بعد التحقق من كل شيء، ابدأ تشغيل الخدمة عبر `systemd`:
```bash
systemctl --user start firecrawl.service
```
يمكن الوصول إلى [إجراءات OpenClaw](https://docs.openclaw.ai/) من داخل الحاوية التفاعلية، ولوحة التحكم الويب متاحة على نفس المضيف والمنفذ على http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### الحصول على `OPENCLAW_GATEWAY_TOKEN` الخاص بك

بمجرد تشغيل الخدمة، ستلاحظ إنشاء مجلد جديد باسم `.openclaw` في مجلدك الرئيسي (~/.openclaw). هذا المجلد مقفل افتراضيًا، لذا ستحتاج إلى فتحه لاسترجاع رمز البوابة الخاص بك.

1. امنح الوصول إلى المجلد:
```bash
sudo chmod 777 ~/.openclaw/
```
2. اقرأ رمز البوابة الخاص بك:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
حدد قيمة `OPENCLAW_GATEWAY_TOKEN` في المخرجات.

3. افتح لوحة تحكم البوابة في متصفحك على http://127.0.0.1:18789. الصق رمزك عند مطالبتك بالمصادقة.

لإيقاف الخدمة، شغّل:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## بدء تشغيل بوابة OpenClaw

البوابة هي عملية OpenClaw التي تدير حلقة الوكيل وتقدّم لوحة التحكم:

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

لفتح لوحة التحكم، شغّل هذا في طرفية ثانية بينما لا تزال البوابة قيد التشغيل:

```bash
openclaw dashboard
```

لأن البوابة ترتبط بـ loopback، فإن لوحة التحكم تصادق تلقائيًا عند فتحها من نفس الجهاز، ولا حاجة لإدخال رمز أو الموافقة على الجهاز للوصول المحلي. يجب أن ترى لوحة تحكم OpenClaw مع إدراج نموذج Lemonade الخاص بك كخلفية نشطة.

> إذا قمت بتفعيل العزل (sandboxing)، يمكنك التحقق منه بسؤال الوكيل تشغيل `run hostname` من لوحة التحكم. إذا رأيت معرّف حاوية قصير بدلاً من اسم مضيف جهازك، فهذا يعني أن العزل يعمل.

**تهانينا، لقد بنيت مكدس وكيل ذكاء اصطناعي محلي بالكامل من الصفر.**

> **هل تحتاج إلى رمز البوابة؟** شغّل `openclaw dashboard --no-open` لطباعة رابط لوحة التحكم مع تضمين الرمز فيه (كما يحاول أيضًا نسخه إلى الحافظة الخاصة بك). بدلاً من ذلك، يمكن العثور على الرمز في `gateway.auth.token` داخل `~/.openclaw/openclaw.json`.
>
> **الموافقة على جهاز عن بُعد:** عند فتح لوحة التحكم من جهاز ثانٍ أو هاتف، يعرض المتصفح معرّف طلب. عد إلى الجهاز الذي يشغّل البوابة، وشغّل:
> ```bash
> openclaw devices approve <requestId>
> ```
> هذا مطلوب فقط للأجهزة البعيدة أو الثانوية، أما الوصول عبر loopback من نفس الجهاز فيصادق تلقائيًا.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## اختياري: ربط قناة تواصل

بمجرد تشغيل البوابة، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. اختر الخيار الذي يناسب إعدادك. يدعم OpenClaw [Discord](https://docs.openclaw.ai/channels/discord)، و[Telegram](https://docs.openclaw.ai/channels/telegram)، وقنوات أخرى، راجع القائمة الكاملة على [docs.openclaw.ai](https://docs.openclaw.ai).

---

### الخيار أ: Discord

يتطلب Discord خادمًا **لديك فيه صلاحية المسؤول (administrator)** لإضافة بوت. إذا كنت تشارك خوادم لكنك لا تملك واحدًا، استخدم الخيار ب (Telegram) بدلاً من ذلك.

#### إنشاء حساب وخادم Discord

إذا لم يكن لديك حساب Discord، سجّل في [discord.com](https://discord.com). تحتاج أيضًا إلى خادم تكون فيه مسؤولًا، أنشئ واحدًا بالنقر على أيقونة **+** في الشريط الجانبي لـ Discord واختيار **Create My Own**. الخادم الخاص كافٍ.

#### إنشاء تطبيق وبوت Discord

1. اذهب إلى [Discord Developer Portal](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسمًا (مثل "openclaw-bot").
2. في الشريط الجانبي، انقر على **Bot**. عيّن اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرّر إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (يُنصح به)
4. مرّر للأعلى وانقر على **Reset Token** لإنشاء رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر على **OAuth2/ URL Generator**.
2. تحت **Scopes**، فعّل `bot` و`applications.commands`.
3. تحت **Bot Permissions**، فعّل: View Channels، Send Messages، Read Message History، Embed Links، Attach Files.
4. انسخ الرابط الذي تم إنشاؤه، الصقه في متصفحك، اختر خادمك، وأكّد. يجب أن يظهر البوت الآن في قائمة أعضاء خادمك.
#### اجمع معرّفاتك (IDs)

فعّل وضع المطوّر في Discord (**User Settings/ Advanced/ Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة السيرفر الخاص بك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية الخاصة: **Copy User ID**

#### السماح بالرسائل المباشرة من أعضاء السيرفر

انقر بزر الفأرة الأيمن على أيقونة السيرفر الخاص بك/ **Privacy Settings**/ فعّل خيار **Direct Messages**. هذا يسمح للبوت بإرسال رسالة مباشرة لك، وهو أمر مطلوب لخطوة الاقتران.

#### إعداد OpenClaw لـ Discord

خزّن رمز البوت (bot token) الخاص بك كمتغير بيئة، ثم أنشئ ملف تصحيح (patch) واحد يفعّل Discord، ويشير إلى الرمز، ويسمح بالوصول لسيرفرك فقط. استبدل `<server_id>` و`<user_id>` بالمعرّفات التي جمعتها أعلاه.

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

> **لا تعتمد على طلب إعداد هذا من الوكيل.** عند تفعيل العزل (sandboxing)، لا يستطيع الوكيل الكتابة إلى `~/.openclaw/openclaw.json` من داخل بيئة العزل، استخدم أوامر CLI أعلاه على الجهاز المضيف بدلاً من ذلك.

أعد تشغيل البوابة (gateway) لتلتقط إعدادات القناة الجديدة:

```bash
openclaw gateway run --bind loopback --port 18789
```

يجب أن ترى `logged in to discord as <bot-name>` في مخرجات البوابة خلال ثوانٍ قليلة.

#### قرن حسابك على Discord

أرسل رسالة مباشرة إلى البوت في Discord. سيرد برمز اقتران قصير.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

وافق عليه على الجهاز الذي يشغّل OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> تنتهي صلاحية رموز الاقتران بعد ساعة واحدة.

يمكنك الآن الدردشة مع وكيلك مباشرة من Discord وتفريغ المهام إلى جهازك المحلي.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### الخيار ب: Telegram

يعد Telegram أبسط من Discord لمعظم المستخدمين، فهو لا يتطلب سيرفراً ولا صلاحيات إدارية.

#### أنشئ بوت Telegram

1. افتح Telegram وراسل **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يعطيك إياه.

#### إعداد OpenClaw لـ Telegram

خزّن الرمز كمتغير بيئة:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

أضف إعدادات القناة إلى `~/.openclaw/openclaw.json` (أو صحّحها عبر لوحة التحكم):

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

أعد تشغيل البوابة، ثم أرسل أي رسالة إلى بوتك في Telegram. وافق على الاقتران:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

تنتهي صلاحية رموز الاقتران بعد ساعة واحدة. يمكنك الآن الدردشة مع وكيلك عبر رسائل Telegram المباشرة.

---

## الخطوات التالية

الآن بعد أن أصبح بإمكان وكيلك استقبال الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخّص سوق الأسهم**: جدول OpenClaw لجلب البيانات من واجهات برمجة التطبيقات (APIs) المالية على فترة زمنية ثابتة، وتلخيص حركة اليوم باستخدام نموذجك المحلي، ودفع ملخص إلى هاتفك كل صباح عبر القناة التي تختارها.

2. **مراقب الضبط الدقيق (Fine-tuning)**: ابدأ مهمة تدريب عن بُعد عبر Telegram أو Discord، ثم اجعل الوكيل يتابع سجل التدريب ويبلغ بشكل دوري عن قيم الخسارة، ونسبة استخدام GPU، ومساحة القرص إلى هاتفك. إذا توقف التشغيل أو ارتفع استخدام VRAM فجأة، ستعرف ذلك فوراً دون الحاجة إلى التواجد بجانب الجهاز.

3. **إنترنت الأشياء (IOT) مع نموذج VLM محلي**: وجّه كاميرا نحو باب منزلك، وشغّل نموذج رؤية على Lemonade، واجعل OpenClaw يحلل الإطارات عند الطلب أو عند حدوث محفّز. اسأل "هل وصلت أي طرود اليوم؟" من هاتفك واحصل على إجابة مباشرة من عتادك الخاص.

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