<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تشغيل OpenClaw باستخدام Lemonade Server كواجهة خلفية

## نظرة عامة

[**OpenClaw**](https://openclaw.ai/) هو وكيل ذكاء اصطناعي مستقل يمكنه كتابة الكود وتشغيله، وإدارة الملفات، وإنجاز مهام معقدة متعددة الخطوات نيابة عنك. على عكس مساعد الدردشة الذي يكتفي بالإجابة عن الأسئلة، ينفّذ OpenClaw إجراءات حقيقية على نظامك، ما يعني أنه بحاجة إلى واجهة خلفية سريعة وقادرة لمواكبة دورة عمل الوكيل المتطلبة.

[**Lemonade Server**](https://lemonade-server.ai/) هو تلك الواجهة الخلفية. إنه خادم استدلال محلي مفتوح المصدر يقوم بتشغيل نماذج GenAI مباشرة على أجهزتك ويعرضها من خلال واجهة برمجة تطبيقات OpenAI القياسية في هذا المجال.

معًا، يشكّلان مجموعة وكيل ذكاء اصطناعي محلية بالكامل: يتعامل Lemonade مع استدلال النموذج، بينما يوفر OpenClaw دورة الوكيل التي تحوّل مخرجات النموذج إلى إجراءات حقيقية.

> **قبل أن تتابع:** OpenClaw وكيل ذكاء اصطناعي يتمتع بدرجة عالية من الاستقلالية. منح أي وكيل ذكاء اصطناعي حق الوصول إلى نظامك قد يؤدي إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه برمجيات مستقلة تتصرف نيابة عنك.

---

## ما ستتعلمه

بحلول نهاية هذا الدليل ستكون قادرًا على:

- التعرف على **Lemonade Server**
- **تثبيت OpenClaw** و**توجيهه نحو Lemonade Server** كواجهته الخلفية للذكاء الاصطناعي.
- **بدء تشغيل بوابة OpenClaw** والتأكد من جاهزية وكيلك للعمل.
- **ربط قناة تواصل** (Discord أو Telegram) لتتمكن من الدردشة مع وكيلك من أي جهاز.

---

## ضبط إعداد الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة لينكس متوافقة قائمة على Debian مع `apt-get`
- **12 جيجابايت** على الأقل من الذاكرة العشوائية (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (اختياري، لعزل OpenClaw في بيئة معزولة)
- **حوالي 10 إلى 30 جيجابايت** من مساحة القرص الفارغة لأوزان النموذج
<!-- @os:end -->

<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- **12 جيجابايت** على الأقل من الذاكرة العشوائية (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **حوالي 10 إلى 30 جيجابايت** من مساحة القرص الفارغة لأوزان النموذج
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (اختياري، لعزل OpenClaw في بيئة معزولة)
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

النموذج الموصى به لهذا الدليل هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي بنافذة سياق تبلغ 263 ألف رمز، وهو مناسب جدًا لأحمال عمل الوكلاء. يستخدم هذا النموذج التكميم UD-Q4_K_XL. اسحبه الآن:

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

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، فكّر في تقليل نافذة السياق. ومع ذلك، نظرًا لأن Qwen3.6 يستفيد من السياق الموسّع لأداء المهام المعقدة، ننصح بالحفاظ على طول سياق لا يقل عن 128 ألف رمز للحفاظ على قدرات التفكير.

> **نصيحة: تعطيل وضع التفكير للحصول على استجابات أسرع من الوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، ما يضيف زمن انتظار قبل كل استجابة. بالنسبة لدورات الوكلاء، يتراكم هذا العبء الإضافي بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) تهيئة جاهزة تعطّل وضع التفكير. لاستخدامها، قم بتنزيل الملف واستيراده:
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

نقوم بتشغيل OpenClaw داخل WSL (موصى به) وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة سطر أوامر Linux لـ OpenClaw مع الاحتفاظ بتسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL وUbuntu

افتح PowerShell كمسؤول (Administrator) وقم بتثبيت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم قم بتثبيت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

نفّذ هذا داخل طرفية Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

اخرج من WSL وأعد تشغيله:

```powershell
exit
wsl --shutdown
wsl
```

### ربط Lemonade من Windows إلى WSL

يعمل WSL2 في شبكة افتراضية. يرتبط Lemonade على Windows بـ `127.0.0.1`، والذي لا يمكن لـ WSL الوصول إليه مباشرة. يقوم وكيل منفذ (port proxy) في Windows بإعادة توجيه حركة المرور من عنوان IP لبوابة WSL إلى المضيف المحلي (localhost) في Windows.

**ابحث عن عنوان IP لبوابة WSL** (نفّذ داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (نفّذ في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP لبوابة WSL الخاصة بك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> ملاحظة: إذا واجهت خطأ `netsh: command not found`، جرّب استخدام اسم الملف التنفيذي الصريح بدلاً من ذلك - `netsh.exe`

**أضف قاعدة جدار حماية** (نفس نافذة PowerShell المرتفعة الصلاحيات):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من WSL**:

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

#### الحفاظ على عمل الجسر بعد إعادة التشغيل

تبقى قاعدة `netsh portproxy` فعّالة بعد إعادة التشغيل، لكن عنوان IP الخاص ببوابة WSL قد يتغيّر بعد تنفيذ `wsl --shutdown` أو إعادة تشغيل الجهاز. عندما يحدث ذلك، يظل الوكيل (proxy) يشير إلى العنوان القديم ويصبح Lemonade غير قابل للوصول من WSL. إذا حدث ذلك، استخدم أحد الخيارين أدناه.

**الخيار 1 (موصى به) — إصلاح الجسر تلقائيًا.** لتجنب القيام بذلك يدويًا في كل مرة، استخدم مهمة مجدولة تتحقق من الجسر عند كل بدء تشغيل وتسجيل دخول، وتعيد بناءه فقط عند تغيّر عنوان IP الخاص بالبوابة. راجع [دليل الإصلاح التلقائي لجسر Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**الخيار 2 — إصلاح الجسر يدويًا.** أولًا، احصل على عنوان IP الحالي لبوابة WSL بتشغيل الأمر التالي داخل WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

انسخ هذه القيمة؛ ستستخدمها بدلًا من `<new-WSL-Gateway-IP>` أدناه.

بعد ذلك، في نافذة **PowerShell مرفوعة الصلاحيات** (تشغيل كمسؤول)، اعرض القواعد الحالية، واحذف قاعدة Lemonade القديمة فقط، ثم أضف قاعدة جديدة بالعنوان الحالي:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

في نتيجة الأمر `show all`، تكون قاعدة Lemonade القديمة هي الإدخال الذي يكون عنوان الاتصال الخاص به `127.0.0.1` على المنفذ `13305`؛ وعنوان الاستماع الخاص بها هو `<old-WSL-Gateway-IP>` الخاص بك. حذف القاعدة عبر هذا العنوان يزيل هذه القاعدة فقط ويترك أي قواعد port-proxy أخرى على جهازك دون تغيير.

قاعدة جدار الحماية التي أضفتها أثناء الإعداد مرتبطة بالمنفذ `13305` (وليس بعنوان IP)، لذا تستمر في العمل ولا تحتاج إلى إعادة إنشائها.

> **توصية:** لتجنب مشاكل البوابة، نوصي بشدة باتباع إعدادات الصدفة التالية:
> - يجب تنفيذ **أوامر Windows** في **PowerShell**
> - يجب تنفيذ **أوامر توزيعة WSL** في **موجّه الأوامر (Command Prompt)** (يُشغَّل كـ**مسؤول**)

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

## تثبيت وتهيئة OpenClaw

### تثبيت OpenClaw
<!-- @os:windows -->
> نفّذ الأوامر في هذا القسم داخل **طرفية WSL** الخاصة بك.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

تتخطى العلامة `--no-onboard` معالج الإعداد التفاعلي، وستقوم بتهيئة الواجهة الخلفية للنموذج (model backend) يدويًا في الخطوة التالية، مما يمنحك تحكمًا دقيقًا في النموذج والخادم المستخدمَين.

افتح طرفية جديدة وتأكد من التثبيت:

```bash
openclaw --version
```

> **تلميح:** إذا ظهرت لك رسالة `command not found` بعد التثبيت، أضف دليل npm العام لملفات bin إلى PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> لجعل هذا دائمًا، أضف السطر أعلاه إلى ملف `~/.bashrc` أو `~/.zshrc` الخاص بك.

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

> **حجم نافذة السياق في OpenClaw:** يتم تفعيل الضغط (compaction) في OpenClaw عندما تكون `contextTokens > contextWindow − reserveTokens`. القيمة الافتراضية لـ `reserveTokensFloor` هي 20,000 رمز (token)، وهي حد أدنى يتجاوز `reserveTokens` عندما تكون قيمته أقل، لذا فإن أي نافذة سياق للنموذج أقل من حوالي 37 ألف رمز ستؤدي إلى حلقة ضغط لا نهائية. اضبط قيمة احتياطية منخفضة وعطّل الحد الأدنى مرة واحدة في تهيئتك ليُطبَّق ذلك على كل نموذج، دون الحاجة لضبط لكل نموذج على حدة:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` هو *حد أدنى* (ضمان أدنى)، وليس الاحتياطي نفسه، لذا فإن ضبط الحد الأدنى فقط ليس له أي تأثير. تعطّل القيمة `reserveTokensFloor: 0` هذا الضمان بحيث تُقبل قيمة `reserveTokens` الأقل.
>
> **متى تُطبَّق هذه الإعدادات:** استخدم هذه التهيئة إذا كانت نافذة السياق الفعّالة لنموذجك أقل من حوالي 37 ألف رمز، سواء كان ذلك لأن النموذج صغير (مثل 8k أو 16k أو 32k) أو لأنك قمت عمدًا بتحديد قيمة أقل (مثل تحميل نموذج بسعة 128k مع ضبط السياق على 16k في Lemonade). بدون ذلك، يدخل OpenClaw في حلقة ضغط لا نهائية عند بدء التشغيل.
>
> **نماذج السياق الكبير عند السياق الكامل:** يمكنك تخطي هذا الأمر بالكامل. الإعدادات الافتراضية تعمل بشكل جيد، إذ يبدأ الضغط قبل امتلاء النافذة بوقت كافٍ، ويكون لدى النموذج مساحة كافية لتوليد ردود طويلة. إذا طبّقت هذا الإعداد رغم ذلك، فانتبه إلى أن `reserveTokens: 4096` يحدّ طول الاستجابة إلى نحو 4 آلاف رمز، مما قد يقطع توليد الملفات الطويلة أو الخطط التفصيلية.
>
> **أين تُضاف هذه الإعدادات:** ضع كتلة `compaction` داخل `agents.defaults` في ملف `openclaw.json` الخاص بك (عادةً في `~/.openclaw/openclaw.json`):
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
> تبقى بقية إعداداتك (البوابة، القنوات، النماذج، إلخ) دون تغيير، ولا يلزم سوى إضافة مفتاح `compaction`.
### (موصى به) تفعيل عزل Docker Sandboxing

يمكن لـ OpenClaw توجيه جميع عمليات الملفات والتعليمات البرمجية الخاصة بالوكيل عبر حاوية Docker معزولة بدلاً من تشغيلها مباشرةً على جهازك المضيف. يحد هذا من نطاق تأثير أي إجراء غير مقصود ليقتصر على الصندوق المعزول (sandbox)، تاركًا نظام الملفات والشبكة الخاصين بجهازك المضيف دون مساس.

قم ببناء صورة الصندوق المعزول مرة واحدة (يجب تثبيت Docker):

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

نفّذ هذا الأمر لإضافة مفتاح `sandbox` داخل كتلة `agents.defaults` الموجودة في `~/.openclaw/openclaw.json`:

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

لا تملك حاويات الصندوق المعزول **أي وصول إلى الشبكة** افتراضيًا. راجع [مرجع الصندوق المعزول](https://docs.openclaw.ai/gateway/sandboxing) للاطلاع على عمليات ربط المسارات (bind mounts) وتجاوزات الشبكة.

> #### استكشاف الأخطاء وإصلاحها: رفض إذن Docker
> 
> إذا واجهت رسالة "permission denied" عند تشغيل أوامر Docker:
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
> ثم أعد **تشغيل** النظام.
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

توفر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة زحف واستخراج محتوى ويب مستضافة ذاتيًا يمكنها تجاوز هذه التحديات وإطلاق الإمكانات الكاملة لأتمتة OpenClaw.

في هذا الإعداد، يعمل OpenClaw كمجموعة من حاويات Docker يديرها Podman. لتبسيط إدارة دورة الحياة والتشغيل التلقائي، نقوم بتسجيل Firecrawl كخدمة `systemd` على مستوى المستخدم تنسّق حزمة Podman Compose الأساسية. يتيح هذا لـ OpenClaw بدء تشغيل البوابة (gateway) وإيقافها والتحقق من خدمة Firecrawl باستخدام أوامر `systemctl --user` القياسية بدلاً من التفاعل مع الحاويات مباشرةً.

للحفاظ على البساطة، قسّمنا العملية بأكملها إلى أربع خطوات:

---

### 1. تسجيل خدمة النظام
انتقل إلى دليل إعدادات مستخدم systemd:
```bash
cd ~/.config/systemd/user
```
أنشئ ملفًا جديدًا وافتحه باسم `firecrawl.service`.
```bash
nano firecrawl.service
```
انسخ الإعدادات التالية والصقها:
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
في هذه المرحلة، تكون الخدمة قد عُرّفت لكنها لم تُسجَّل بعد لدى `systemd`. 
تأكد من أن اسم الملف يطابق تمامًا ما أنشأته أعلاه، ثم نفّذ:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
إذا نجحت العملية، يجب أن ترى المخرجات التالية:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

يحتوي `default.target.wants/` على روابط رمزية إلى الخدمات المُعدَّة لتبدأ تلقائيًا.

### 2. إعداد Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) مثالي لمن يحتاج إلى تحكم كامل في بيئات الزحف ومعالجة البيانات الخاصة به، لكنه يأتي مع مقايضة تتمثل في جهود إضافية للصيانة والإعداد.

ابدأ باستنساخ المستودع:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
أنشئ ملف `.env` في الدليل الجذر `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. نشر OpenClaw باستخدام Podman Compose

قبل المتابعة، تأكد من أنك قد سحبت أحدث صورة Docker الخاصة بـ OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
بمجرد الانتهاء من ذلك، حمّل ملف OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) وضعه في الدليل الجذر `/firecrawl`:

> هذا الاصطلاح مطلوب لكي يتمكن `systemd` من تحديد موقع الخدمة وبدء تشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع الحزمة بإضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة OpenClaw عبر Firecrawl 

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح بتشغيل الحزمة يدويًا:
```bash
podman compose -f openclaw-compose.yaml up -d
```
إذا كانت الإعدادات صحيحة، يجب أن ترى حاوية OpenClaw تعمل، وأن تبدو مخرجات سطر الأوامر لديك مشابهة لهذا:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

بعد التحقق، أوقف تشغيل الحزمة قبل المتابعة:
```bash
podman compose -f openclaw-compose.yaml down
```
قبل بدء تشغيل الخدمة، يجب التأكد من ضبط الملكية والأذونات الصحيحة على دليل `firecrawl` وملف `.env` الخاص به. 
هذا أمر ضروري لكي تتمكن الخدمة من كتابة بيانات الاعتماد الخاصة بك عند بدء التشغيل.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
الآن بعد أن تم التحقق من كل شيء، ابدأ تشغيل الخدمة عبر `systemd`:
```bash
systemctl --user start firecrawl.service
```
يمكن الوصول إلى [إجراءات OpenClaw](https://docs.openclaw.ai/) من داخل الحاوية التفاعلية، ولوحة تحكم الويب متاحة على نفس المضيف والمنفذ عبر http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### الحصول على `OPENCLAW_GATEWAY_TOKEN` الخاص بك

بمجرد تشغيل الخدمة، ستلاحظ إنشاء دليل جديد باسم `.openclaw` في مجلدك الرئيسي (~/.openclaw). هذا الدليل مقفل افتراضيًا، لذا ستحتاج إلى فتحه لاسترجاع رمز البوابة الخاص بك.

1. امنح صلاحية الوصول إلى الدليل:
```bash
sudo chmod 777 ~/.openclaw/
```
2. اقرأ رمز البوابة الخاص بك:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
حدد موقع قيمة `OPENCLAW_GATEWAY_TOKEN` في المخرجات.

3. افتح لوحة تحكم البوابة في متصفحك عبر http://127.0.0.1:18789. الصق رمزك عند مطالبتك بالمصادقة.

لإيقاف الخدمة، نفّذ:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## بدء تشغيل OpenClaw Gateway

الـ gateway هو عملية OpenClaw التي تدير حلقة الوكيل (agent loop) وتقدّم لوحة التحكم (dashboard):

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

لفتح لوحة التحكم، شغّل هذا الأمر في محطة طرفية ثانية بينما لا يزال الـ gateway قيد التشغيل:

```bash
openclaw dashboard
```

نظرًا لأن الـ gateway يرتبط بـ loopback، تقوم لوحة التحكم بالمصادقة التلقائية عند فتحها من نفس الجهاز، فلا حاجة لإدخال رمز مميز (token) أو موافقة الجهاز للوصول المحلي. يجب أن تشاهد لوحة تحكم OpenClaw مع إدراج نموذج Lemonade الخاص بك كخلفية نشطة (active backend).

> إذا قمت بتمكين العزل (sandboxing)، يمكنك التحقق من ذلك عبر مطالبة الوكيل بتنفيذ `run hostname` من لوحة التحكم. إذا شاهدت معرّف حاوية (container ID) قصير بدلًا من اسم مضيف جهازك، فإن العزل يعمل بشكل صحيح.

**تهانينا، لقد بنيت مجموعة وكيل ذكاء اصطناعي محلية بالكامل من الصفر.**

> **هل تحتاج رمز الـ gateway المميز (token)؟** شغّل `openclaw dashboard --no-open` لطباعة رابط لوحة التحكم مع تضمين الرمز المميز (كما يحاول نسخه إلى الحافظة). بدلًا من ذلك، يوجد الرمز المميز في `gateway.auth.token` ضمن `~/.openclaw/openclaw.json`.

**الوصول إلى لوحة التحكم من جهاز آخر (عبر نفق SSH)**

إذا كان OpenClaw يعمل على جهاز بعيد، يمكنك الوصول إلى لوحة تحكمه من جهازك المحلي عبر نفق SSH. ينقل النفق منفذ الـ gateway (`18789`) بحيث يمكن لمتصفحك المحلي التواصل مع الـ gateway البعيد عبر `127.0.0.1`.

1. من **جهازك المحلي**، اتصل بالجهاز البعيد مرة واحدة واقبل مطالبة البصمة (fingerprint) بحيث يُضاف المضيف إلى قائمة المضيفين المعروفين لديك:

   ```bash
   ssh user@<host-ip>
   ```

2. لا تزال على **جهازك المحلي**، افتح نفق SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **ملاحظة:** بعد إدخال كلمة المرور، لن تظهر المحطة الطرفية أي ناتج وتبدو وكأنها متوقفة. هذا أمر متوقع: العلم `-N` يخبر SSH بعدم تشغيل أي أمر بعيد، لذا فهو يبقي النفق مفتوحًا فقط. اترك هذه المحطة الطرفية قيد التشغيل.

3. على **جهازك المحلي**، افتح متصفحًا واذهب إلى `http://127.0.0.1:18789`.

4. على **الجهاز البعيد**، اطبع رمز الـ gateway المميز والصقه في المتصفح لتسجيل الدخول:

   ```bash
   openclaw dashboard --no-open
   ```

   يطبع هذا رابط لوحة التحكم مع تضمين الرمز المميز؛ انسخ الرمز المميز لتسجيل الدخول. (يُخزَّن الرمز المميز أيضًا في `gateway.auth.token` ضمن `~/.openclaw/openclaw.json`.)

> **الموافقة على جهاز بعيد:** عندما تفتح لوحة التحكم من جهاز آخر أو هاتف، قد يعرض المتصفح معرّف طلب (request ID). على **الجهاز البعيد**، اسرد الطلبات المعلّقة:
> ```bash
> openclaw devices list
> ```
> ثم وافق على الطلب المطابق:
> ```bash
> openclaw devices approve <requestId>
> ```
> هذا مطلوب فقط للأجهزة البعيدة أو الثانوية؛ يتم مصادقة الوصول من نفس الجهاز عبر loopback تلقائيًا. راجع وثائق [الوصول عن بُعد](https://docs.openclaw.ai/gateway/remote) لمزيد من التفاصيل.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## اختياري: توصيل قناة تواصل

بمجرد تشغيل الـ gateway، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. اختر الخيار الذي يناسب إعدادك. يدعم OpenClaw [Discord](https://docs.openclaw.ai/channels/discord) و[Telegram](https://docs.openclaw.ai/channels/telegram) وقنوات أخرى، راجع القائمة الكاملة على [docs.openclaw.ai](https://docs.openclaw.ai).

---

### الخيار أ: Discord

يتطلب Discord سيرفرًا تملك فيه **صلاحيات المسؤول (administrator)** لإضافة بوت. إذا كنت تشارك سيرفرات لكنك لا تملك واحدًا، استخدم الخيار ب (Telegram) بدلًا من ذلك.

#### إنشاء حساب وسيرفر Discord

إذا لم يكن لديك حساب Discord، سجّل على [discord.com](https://discord.com). تحتاج أيضًا إلى سيرفر تكون فيه مسؤولًا، أنشئ واحدًا بالنقر على أيقونة **+** في الشريط الجانبي لـ Discord واختيار **Create My Own**. سيرفر خاص كافٍ.

#### إنشاء تطبيق وبوت Discord

1. اذهب إلى [بوابة مطوّري Discord](https://discord.com/developers/applications) وانقر على **New Application**. أعطه اسمًا (مثل "openclaw-bot").
2. في الشريط الجانبي، انقر على **Bot**. عيّن اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرر لأسفل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرر لأعلى وانقر على **Reset Token** لتوليد رمز البوت المميز (bot token). انسخه.

#### إضافة البوت إلى سيرفرك

1. في الشريط الجانبي، انقر على **OAuth2/ URL Generator**.
2. ضمن **Scopes**، فعّل `bot` و`applications.commands`.
3. ضمن **Bot Permissions**، فعّل: View Channels وSend Messages وRead Message History وEmbed Links وAttach Files.
4. انسخ الرابط المُولَّد، الصقه في متصفحك، اختر سيرفرك، وأكّد. يجب أن يظهر البوت الآن في قائمة أعضاء سيرفرك.

#### جمع معرّفاتك (IDs)

فعّل وضع المطوّر (Developer Mode) في Discord (**User Settings/ Advanced/ Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة سيرفرك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية: **Copy User ID**

#### السماح بالرسائل المباشرة من أعضاء السيرفر

انقر بزر الفأرة الأيمن على أيقونة سيرفرك/ **Privacy Settings**/ فعّل **Direct Messages**. هذا يسمح للبوت بمراسلتك مباشرة، وهو مطلوب لخطوة الاقتران (pairing).

#### تهيئة OpenClaw لـ Discord

خزّن رمز البوت المميز كمتغيّر بيئة، ثم أنشئ ملف تصحيح (patch file) واحد يفعّل Discord، ويشير إلى الرمز المميز، ويضيف سيرفرك إلى القائمة المسموحة. استبدل `<server_id>` و`<user_id>` بالمعرّفات التي جمعتها أعلاه.

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

> **لا تعتمد على مطالبة الوكيل بتهيئة هذا.** عند تفعيل العزل (sandboxing)، لا يمكن للوكيل الكتابة إلى `~/.openclaw/openclaw.json` من داخل العزل، استخدم أوامر CLI أعلاه على المضيف بدلًا من ذلك.

أعد تشغيل الـ gateway ليتعرّف على إعدادات القناة الجديدة:

```bash
openclaw gateway run --bind loopback --port 18789
```

يجب أن تشاهد `logged in to discord as <bot-name>` في ناتج الـ gateway خلال ثوانٍ قليلة.
#### اربط حساب Discord الخاص بك

أرسل رسالة مباشرة إلى البوت في Discord. سيرد عليك برمز اقتران قصير.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

وافق عليه على الجهاز الذي يشغّل OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> تنتهي صلاحية رموز الاقتران بعد ساعة واحدة.

يمكنك الآن الدردشة مع وكيلك مباشرة من Discord وتفويض المهام إلى جهازك المحلي.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### الخيار ب: Telegram

يُعد Telegram أبسط من Discord بالنسبة لمعظم المستخدمين، إذ لا يتطلب خادمًا ولا صلاحيات إدارية.

#### إنشاء بوت Telegram

1. افتح Telegram وأرسل رسالة إلى **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يُعطيك إياه.

#### إعداد OpenClaw لـ Telegram

خزّن الرمز كمتغير بيئة:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

أضف إعدادات القناة إلى `~/.openclaw/openclaw.json` (أو عدّلها عبر لوحة التحكم):

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

الآن بعد أن أصبح وكيلك قادرًا على تلقي الأوامر من هاتفك والتصرف بناءً عليها على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخّص سوق الأسهم**: جدولة OpenClaw لجلب البيانات من واجهات برمجة التطبيقات المالية على فترات ثابتة، وتلخيص تحركات اليوم باستخدام نموذجك المحلي، ودفع ملخص إلى هاتفك كل صباح عبر القناة التي تختارها.

2. **مراقب الضبط الدقيق**: ابدأ مهمة تدريب عن بُعد عبر Telegram أو Discord، ثم اجعل الوكيل يتابع سجل التدريب ويُبلغ بشكل دوري عن قيم الخسارة، واستخدام GPU، ومساحة القرص إلى هاتفك. إذا توقفت العملية أو ارتفع استخدام VRAM بشكل مفاجئ، ستعرف ذلك فورًا دون الحاجة إلى التواجد عند الجهاز.

3. **إنترنت الأشياء بنموذج VLM محلي**: وجّه كاميرا نحو باب منزلك الأمامي، شغّل نموذج رؤية على Lemonade، واجعل OpenClaw يحلل الإطارات عند الطلب أو عند حدوث محفّز. اسأل "هل وصلت أي طرود اليوم؟" من هاتفك واحصل على إجابة مباشرة من جهازك الخاص.

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