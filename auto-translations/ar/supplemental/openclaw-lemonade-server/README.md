<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تشغيل OpenClaw باستخدام Lemonade Server كخلفية

## نظرة عامة

[**OpenClaw**](https://openclaw.ai/) هو وكيل ذكاء اصطناعي مستقل يمكنه كتابة الشيفرة البرمجية وتشغيلها، وإدارة الملفات، وإنجاز مهام معقدة متعددة الخطوات نيابة عنك. على عكس مساعد الدردشة الذي يكتفي بالإجابة عن الأسئلة، يقوم OpenClaw باتخاذ إجراءات فعلية على نظامك، مما يعني أنه يحتاج إلى خلفية ذكاء اصطناعي سريعة وقادرة تواكب حلقة عمل الوكيل المتطلبة.

[**Lemonade Server**](https://lemonade-server.ai/) هو تلك الخلفية. إنه خادم استدلال محلي مفتوح المصدر يقوم بتشغيل نماذج GenAI مباشرة على عتادك ويعرضها عبر واجهة برمجة التطبيقات OpenAI API المعيارية في هذا المجال.

معًا، يشكّلان حزمة وكيل ذكاء اصطناعي محلية بالكامل: يتولى Lemonade استدلال النموذج، بينما يوفر OpenClaw حلقة عمل الوكيل التي تحوّل مخرجات النموذج إلى إجراءات فعلية.

> **قبل أن تتابع:** OpenClaw هو وكيل ذكاء اصطناعي ذو استقلالية عالية. قد يؤدي منح أي وكيل ذكاء اصطناعي وصولًا إلى نظامك إلى نتائج غير متوقعة أو غير مقصودة. تابع فقط إذا كنت تفهم المخاطر وتشعر بالارتياح تجاه قيام برنامج مستقل بالتصرف نيابةً عنك.

---

## ما الذي ستتعلمه

بنهاية هذا الدليل الإرشادي ستكون قادرًا على:

- التعرف على **Lemonade Server**
- **تثبيت OpenClaw** و**توجيهه نحو Lemonade Server** كخلفية ذكاء اصطناعي له.
- **بدء تشغيل بوابة OpenClaw** والتأكد من أن وكيلك جاهز للعمل.
- **ربط قناة اتصال** (Discord أو Telegram) حتى تتمكن من الدردشة مع وكيلك من أي جهاز.

---

<!-- @device:halo_box,halo,stx,krk -->
## ضبط إعداد الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @os:linux -->
- جهاز كمبيوتر يعمل بنظام **Ubuntu 24.04+** أو توزيعة لينكس متوافقة مبنية على Debian مع `apt-get`
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (اختياري، لعزل OpenClaw في بيئة معزولة)
- **مساحة قرص خالية تتراوح بين 10 و30 جيجابايت تقريبًا** لأوزان النموذج
<!-- @os:end -->

<!-- @os:windows -->
- جهاز كمبيوتر يعمل بنظام **Windows 10/11**
- ما لا يقل عن **12 جيجابايت من ذاكرة الوصول العشوائي (RAM)** (يُنصح بـ 64 جيجابايت أو أكثر للنماذج الأكبر)
- **مساحة قرص خالية تتراوح بين 10 و30 جيجابايت تقريبًا** لأوزان النموذج
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (اختياري، لعزل OpenClaw في بيئة معزولة)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## سحب وتحميل النموذج الموصى به

النموذج الموصى به لهذا الدليل الإرشادي هو **Qwen3.6-35B-A3B-GGUF** من Unsloth، وهو نموذج MoE قوي يتميز بنافذة سياق تبلغ 263 ألف رمز وملائم جدًا لأعباء عمل الوكلاء. يستخدم هذا النموذج ضغط UD-Q4_K_XL. اسحبه الآن:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

بعد ذلك قم بتحميله بنافذة سياق كبيرة واحفظ هذا الإعداد للتشغيلات المستقبلية:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

يبلغ طول السياق الافتراضي للنموذج 262,144 رمزًا. إذا واجهت أخطاء نفاد الذاكرة (OOM)، ففكر في تقليل نافذة السياق. ومع ذلك، نظرًا لأن Qwen3.6 يستفيد من السياق الممتد للمهام المعقدة، ننصح بالحفاظ على طول سياق لا يقل عن 128 ألف رمز للحفاظ على قدرات التفكير.

> **نصيحة: تعطيل التفكير لاستجابات أسرع للوكيل:** يعمل Qwen3.6-35B-A3B في وضع التفكير افتراضيًا، مما يضيف زمن انتقال قبل كل استجابة. وبالنسبة لحلقات عمل الوكلاء، يتراكم هذا العبء بسرعة. يوفر مستودع [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) إعدادًا جاهزًا يعطل التفكير. لاستخدامه، قم بتنزيل الملف واستيراده:
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

نقوم بتشغيل OpenClaw داخل WSL (موصى به) وربطه بـ Lemonade الذي يعمل بشكل أصلي على Windows. يمنحك هذا بيئة شل لينكس لـ OpenClaw مع الاحتفاظ بتسريع GPU الخاص بـ Lemonade على جانب Windows.

### تثبيت WSL و Ubuntu

افتح PowerShell كمسؤول وقم بتثبيت نواة WSL:

```powershell
wsl --install --no-distribution
```

ثم قم بتثبيت Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### تفعيل systemd في WSL

شغّل هذا داخل طرفية Ubuntu:

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

يعمل WSL2 ضمن شبكة افتراضية. يرتبط Lemonade على Windows بـ `127.0.0.1`، والذي لا يستطيع WSL الوصول إليه مباشرة. يقوم وكيل منفذ Windows بتوجيه حركة المرور من عنوان IP الخاص ببوابة WSL إلى المضيف المحلي (localhost) الخاص بـ Windows.

**اعثر على عنوان IP الخاص ببوابة WSL** (شغّل هذا داخل WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**أضف وكيل المنفذ** (شغّل هذا في PowerShell كمسؤول، مع استبدال `<WSL-Gateway-IP>` بعنوان IP الخاص ببوابة WSL لديك):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> ملاحظة: إذا واجهت خطأ `netsh: command not found`، فحاول استخدام اسم الملف التنفيذي الصريح بدلًا من ذلك - `netsh.exe`

**أضف قاعدة جدار حماية** (في نفس نافذة PowerShell التي تم رفع صلاحياتها):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**تحقق من WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

إذا كنت قد قمت بالفعل بتحميل نموذج Qwen3.6-35B-A3B-GGUF في الخطوة السابقة، فيجب أن ترى مخرجات JSON على هذا النحو:

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

تبقى قاعدة `netsh portproxy` فعّالة بعد إعادة التشغيل، لكن عنوان IP الخاص ببوابة WSL قد يتغيّر بعد تنفيذ `wsl --shutdown` أو إعادة تشغيل الجهاز. وعند حدوث ذلك، يظل الوكيل يشير إلى العنوان القديم، ويصبح Lemonade غير قابل للوصول من WSL. إذا حدث ذلك، استخدم أحد الخيارين أدناه.

**الخيار 1 (موصى به) — إصلاح الجسر تلقائيًا.** لتجنّب القيام بذلك يدويًا في كل مرة، استخدم مهمة مجدولة تتحقق من حالة الجسر عند كل بدء تشغيل وتسجيل دخول، وتعيد بناءه فقط عند تغيّر عنوان IP الخاص بالبوابة. راجع [دليل الإصلاح التلقائي لجسر Lemonade على WSL](assets/RepairLemonadeWslBridge.md).


**الخيار 2 — إصلاح الجسر يدويًا.** أولًا، احصل على عنوان IP الحالي لبوابة WSL بتشغيل الأمر التالي داخل WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

انسخ هذه القيمة؛ ستستخدمها بدلًا من `<new-WSL-Gateway-IP>` أدناه.

بعد ذلك، في **PowerShell بصلاحيات مرتفعة** (شغّله كمسؤول)، اعرض القواعد الحالية، واحذف فقط قاعدة Lemonade القديمة، وأضف قاعدة جديدة بعنوان IP الحالي:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

في مخرجات `show all`، قاعدة Lemonade القديمة هي الإدخال الذي يكون عنوان الاتصال الخاص به `127.0.0.1` على المنفذ `13305`؛ وعنوان الاستماع الخاص به هو `<old-WSL-Gateway-IP>` الخاص بك. حذف القاعدة بناءً على هذا العنوان يزيل هذه القاعدة فقط، ويترك أي قواعد port-proxy أخرى على جهازك دون تغيير.

قاعدة جدار الحماية التي أضفتها أثناء الإعداد مرتبطة بالمنفذ `13305` (وليس بعنوان IP)، لذا تستمر في العمل ولا حاجة لإعادة إنشائها.

> **توصية:** لتجنّب مشاكل البوابة، ننصح بشدة باتّباع إعداد الأوامر التالي:
> - يجب تنفيذ **أوامر Windows** في **PowerShell**
> - يجب تنفيذ **أوامر توزيعة WSL** في **موجه الأوامر (Command Prompt)** (شغّله كـ **مسؤول**)

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
> نفّذ الأوامر الواردة في هذا القسم داخل **طرفية WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

يؤدي العلم `--no-onboard` إلى تخطي معالج الإعداد التفاعلي، وستقوم بتهيئة الخلفية الخاصة بالنموذج يدويًا في الخطوة التالية، مما يمنحك تحكمًا دقيقًا في النموذج والخادم المستخدمين.

افتح طرفية جديدة وتأكد من اكتمال التثبيت:

```bash
openclaw --version
```

> **نصيحة:** إذا ظهرت لك رسالة `command not found` بعد التثبيت، أضف دليل npm العام للثنائيات (bin) إلى متغير PATH:
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

نفّذ عملية الإعداد غير التفاعلية الخاصة بـ OpenClaw.
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

يكتب هذا الأمر تهيئة OpenClaw إلى الملف `~/.openclaw/openclaw.json`.

> **تحديد حجم نافذة السياق في OpenClaw:** يتم تفعيل عملية الضغط (compaction) في OpenClaw عندما تكون `contextTokens > contextWindow − reserveTokens`. القيمة الافتراضية لـ `reserveTokensFloor` هي 20,000 رمز (token)، وهي حد أدنى يتجاوز قيمة `reserveTokens` عندما تكون أقل منها، لذا فإن أي نافذة سياق للنموذج أقل من حوالي 37 ألف رمز ستؤدي إلى حلقة ضغط لا نهائية. اضبط قيمة احتياط منخفضة وعطّل الحد الأدنى مرة واحدة في إعدادك، وسيُطبَّق ذلك على كل نموذج، دون الحاجة لضبط منفصل لكل نموذج:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> تمثّل `reserveTokensFloor` *حدًا أدنى* (ضمانًا)، وليست قيمة الاحتياط نفسها، لذا فإن ضبط الحد الأدنى فقط لن يكون له أي أثر. تعطّل القيمة `reserveTokensFloor: 0` هذا الضمان بحيث تُقبَل قيمة `reserveTokens` الأقل.
>
> **متى تطبّق هذا الإعداد:** استخدم هذه التهيئة إذا كانت نافذة السياق الفعلية لنموذجك أقل من حوالي 37 ألف رمز، سواء كان ذلك لأن النموذج صغير (مثل 8 آلاف أو 16 ألف أو 32 ألف رمز)، أو لأنك قمت عمدًا بتحديد قيمة أقل (مثل تحميل نموذج بسعة 128 ألف رمز ولكن ضبط السياق على 16 ألف رمز في Lemonade). بدون ذلك، سيدخل OpenClaw في حلقة ضغط لا نهائية عند بدء التشغيل.
>
> **النماذج ذات نافذة السياق الكبيرة بالسعة الكاملة:** يمكنك تخطي هذا الأمر بالكامل. الإعدادات الافتراضية تعمل بشكل جيد، إذ ستبدأ عملية الضغط قبل امتلاء النافذة بوقت كافٍ، وسيبقى للنموذج مساحة كافية لتوليد استجابات طويلة. إذا قمت بتطبيق هذا الإعداد رغم ذلك، فانتبه إلى أن `reserveTokens: 4096` يحدّ طول الاستجابة بحوالي 4 آلاف رمز، مما قد يقطع عمليات توليد الملفات الطويلة أو الخطط التفصيلية.
>
> **أين تضيف هذا الإعداد:** ضع كتلة `compaction` داخل `agents.defaults` في ملف `openclaw.json` الخاص بك (عادةً في `~/.openclaw/openclaw.json`):
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
> تبقى بقية إعداداتك (البوابة، القنوات، النماذج، إلخ) دون تغيير، إذ لا حاجة لإضافة سوى مفتاح `compaction`.
### (موصى به) تفعيل العزل باستخدام Docker

يمكن لـ OpenClaw توجيه جميع عمليات الملفات والتعليمات البرمجية الخاصة بالوكيل عبر حاوية Docker معزولة بدلاً من تشغيلها مباشرة على جهازك المضيف. وهذا يحد من نطاق تأثير أي إجراء غير مقصود ليقتصر على البيئة المعزولة (sandbox)، مع ترك نظام الملفات والشبكة الخاصين بجهازك المضيف دون تأثير.

قم ببناء صورة البيئة المعزولة مرة واحدة (يجب أن يكون Docker مثبتًا):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

قم بتشغيل هذا لإضافة المفتاح `sandbox` داخل الكتلة الحالية `agents.defaults` في `~/.openclaw/openclaw.json`:

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

لا تملك حاويات البيئة المعزولة **أي وصول إلى الشبكة** افتراضيًا. راجع [مرجع العزل](https://docs.openclaw.ai/gateway/sandboxing) للاطلاع على عمليات ربط المسارات (bind mounts) وتجاوزات الشبكة.

> #### استكشاف الأخطاء وإصلاحها: رفض الإذن في Docker
> 
> إذا ظهرت لك رسالة "permission denied" عند تشغيل أوامر Docker:
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

توفر [Firecrawl](https://docs.firecrawl.dev/introduction) خدمة استضافة ذاتية لزحف الويب واستخراج المحتوى يمكنها تجاوز هذه التحديات وإطلاق العِنان للإمكانات الكاملة لأتمتة OpenClaw. 

في هذا الإعداد، يعمل OpenClaw كمجموعة من حاويات Docker تتم إدارتها عبر Podman. ولتبسيط إدارة دورة الحياة والتشغيل التلقائي، نقوم بتسجيل Firecrawl كخدمة `systemd` على مستوى المستخدم تنسّق حزمة Podman Compose الأساسية. يتيح هذا لـ OpenClaw بدء البوابة (gateway) وإيقافها والتحقق من خدمة Firecrawl باستخدام أوامر `systemctl --user` القياسية بدلاً من التعامل مباشرة مع الحاويات. 

ولتبسيط الأمور، قسّمنا العملية بأكملها إلى أربع خطوات:

---

### 1. تسجيل خدمة النظام
انتقل إلى دليل إعدادات systemd الخاص بالمستخدم:
```bash
cd ~/.config/systemd/user
```
أنشئ وافتح ملفًا جديدًا باسم `firecrawl.service`.
```bash
nano firecrawl.service
```
انسخ والصق التكوين التالي:
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
عند هذه النقطة، تم تعريف الخدمة لكنها لم تُسجّل بعد لدى `systemd`. 
تأكد من أن اسم الملف يطابق تمامًا ما أنشأته أعلاه، ثم قم بتشغيل:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
إذا نجحت العملية، يجب أن ترى الناتج التالي:

> **تم إنشاء الرابط الرمزي '\~/.config/systemd/user/default.target.wants/firecrawl.service' ← '\~/.config/systemd/user/firecrawl.service'.**

 يحتوي `default.target.wants/` على روابط رمزية للخدمات المُهيأة لتبدأ تلقائيًا.

### 2. إعداد Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) مثالي لمن يحتاج إلى تحكم كامل في بيئات الزحف ومعالجة البيانات الخاصة به، لكنه يأتي مقابل جهد إضافي في الصيانة والتهيئة.

ابدأ باستنساخ المستودع:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
أنشئ ملف `.env` داخل دليل `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. نشر OpenClaw باستخدام Podman Compose

قبل المتابعة، تأكد من أنك قمت بسحب أحدث صورة Docker الخاصة بـ OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
بمجرد الانتهاء من ذلك، قم بتنزيل ملف OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) وضعه في الدليل الجذري `/firecrawl`:

> هذا الاصطلاح مطلوب لكي يتمكن `systemd` من تحديد موقع الخدمة وبدء تشغيلها بشكل صحيح كما هو محدد في `WorkingDirectory=${HOME}/firecrawl`.

> يمكنك دائمًا توسيع المجموعة بإضافة خدمات Firecrawl إضافية حسب الحاجة. يمكن العثور على القائمة الكاملة للخدمات المتاحة في ملف [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) الرسمي.

### 4. تشغيل خدمة OpenClaw عبر Firecrawl 

قبل تسليم التحكم إلى `systemd`، تحقق من أن كل شيء يعمل بشكل صحيح من خلال تشغيل المجموعة يدويًا:
```bash
podman compose -f openclaw-compose.yaml up -d
```
إذا كان كل شيء مُهيأً بشكل صحيح، يجب أن ترى حاوية OpenClaw تعمل، ويجب أن يبدو ناتج سطر الأوامر لديك مشابهًا لهذا:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

بمجرد التحقق، أوقف المجموعة قبل المتابعة:
```bash
podman compose -f openclaw-compose.yaml down
```
قبل بدء تشغيل الخدمة، يجب عليك التأكد من ضبط الملكية والأذونات الصحيحة على دليل `firecrawl` وملف `.env` الخاص به. 
هذا ضروري لكي تتمكن الخدمة من كتابة بيانات الاعتماد الخاصة بك عند بدء التشغيل.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
الآن وقد تم التحقق من كل شيء، ابدأ تشغيل الخدمة عبر `systemd`:
```bash
systemctl --user start firecrawl.service
```
يمكن الوصول إلى [إجراءات OpenClaw](https://docs.openclaw.ai/) من داخل الحاوية التفاعلية، كما تتوفر لوحة التحكم عبر الويب على نفس المضيف والمنفذ عبر http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### الحصول على `OPENCLAW_GATEWAY_TOKEN` الخاص بك

بمجرد تشغيل الخدمة، ستلاحظ إنشاء دليل جديد باسم `.openclaw` في مجلدك الرئيسي (~/.openclaw). هذا الدليل مقفل افتراضيًا، لذا ستحتاج إلى فتحه لاسترداد رمز البوابة (gateway token) الخاص بك.

1. امنح الوصول إلى الدليل:
```bash
sudo chmod 777 ~/.openclaw/
```
2. اقرأ رمز البوابة الخاص بك:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
حدد موقع قيمة `OPENCLAW_GATEWAY_TOKEN` في الناتج.

3. افتح لوحة تحكم البوابة في متصفحك عبر http://127.0.0.1:18789. الصق رمزك عند مطالبتك بالمصادقة.

لإيقاف الخدمة، قم بتشغيل:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## بدء تشغيل OpenClaw Gateway

الـ gateway هي عملية OpenClaw التي تدير حلقة الوكيل (agent loop) وتقدّم لوحة التحكم:

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

لفتح لوحة التحكم، شغّل هذا الأمر في نافذة طرفية ثانية بينما تظل الـ gateway قيد التشغيل:

```bash
openclaw dashboard
```

نظرًا لأن الـ gateway ترتبط بـ loopback، تقوم لوحة التحكم بالمصادقة التلقائية عند فتحها من نفس الجهاز، فلا حاجة لإدخال رمز أو الموافقة على الجهاز للوصول المحلي. يجب أن ترى لوحة تحكم OpenClaw مع ظهور نموذج Lemonade الخاص بك كخلفية نشطة.

> إذا قمت بتفعيل العزل (sandboxing)، يمكنك التحقق من ذلك بطلب تنفيذ `run hostname` من الوكيل عبر لوحة التحكم. إذا رأيت معرّف حاوية (container ID) قصيرًا بدلاً من اسم مضيف جهازك، فهذا يعني أن العزل يعمل بشكل صحيح.

**تهانينا، لقد بنيت حزمة وكيل ذكاء اصطناعي محلية بالكامل من الصفر.**

> **هل تحتاج إلى رمز الـ gateway؟** شغّل `openclaw dashboard --no-open` لطباعة رابط لوحة التحكم مع الرمز المضمّن فيه (كما يحاول نسخه إلى الحافظة لديك). بدلاً من ذلك، يوجد الرمز في `gateway.auth.token` ضمن `~/.openclaw/openclaw.json`.

**الوصول إلى لوحة التحكم من جهاز آخر (عبر نفق SSH)**

إذا كانت OpenClaw تعمل على جهاز بعيد، يمكنك الوصول إلى لوحة تحكمها من جهازك المحلي عبر نفق SSH. ينقل النفق منفذ الـ gateway (`18789`) بحيث يمكن لمتصفحك المحلي التواصل مع الـ gateway البعيدة عبر `127.0.0.1`.

1. من **جهازك المحلي**، اتصل بالجهاز البعيد مرة واحدة وتقبّل طلب البصمة (fingerprint) ليتم إضافة المضيف إلى قائمة المضيفين المعروفين لديك:

   ```bash
   ssh user@<host-ip>
   ```

2. لا يزال على **جهازك المحلي**، افتح نفق SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **ملاحظة:** بعد إدخال كلمة المرور، لن تظهر النافذة الطرفية أي مُخرَجات ويبدو أنها معلّقة. هذا متوقع: فعلامة `-N` تخبر SSH بعدم تشغيل أي أمر بعيد، لذا فهي تُبقي النفق مفتوحًا فقط. اترك هذه النافذة الطرفية قيد التشغيل.

3. على **جهازك المحلي**، افتح متصفحًا وانتقل إلى `http://127.0.0.1:18789`.

4. على **الجهاز البعيد**، اطبع رمز الـ gateway والصقه في المتصفح لتسجيل الدخول:

   ```bash
   openclaw dashboard --no-open
   ```

   يؤدي هذا إلى طباعة رابط لوحة التحكم مع الرمز المضمّن فيه؛ انسخ الرمز لتسجيل الدخول. (يتم تخزين الرمز أيضًا في `gateway.auth.token` ضمن `~/.openclaw/openclaw.json`.)

> **الموافقة على جهاز بعيد:** عندما تفتح لوحة التحكم من جهاز آخر أو هاتف، قد يعرض المتصفح معرّف طلب (request ID). على **الجهاز البعيد**، اعرض الطلبات المعلّقة:
> ```bash
> openclaw devices list
> ```
> ثم وافق على الطلب المطابق:
> ```bash
> openclaw devices approve <requestId>
> ```
> هذا مطلوب فقط للأجهزة البعيدة أو الثانوية؛ أما الوصول عبر loopback من نفس الجهاز فيتم مصادقته تلقائيًا. راجع وثائق [الوصول عن بُعد](https://docs.openclaw.ai/gateway/remote) لمزيد من التفاصيل.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## اختياري: ربط قناة تواصل

بمجرد تشغيل الـ gateway، يمكنك الوصول إلى وكيلك المحلي من أي جهاز. اختر الخيار المناسب لإعدادك. تدعم OpenClaw [Discord](https://docs.openclaw.ai/channels/discord) و[Telegram](https://docs.openclaw.ai/channels/telegram) وقنوات أخرى، راجع القائمة الكاملة على [docs.openclaw.ai](https://docs.openclaw.ai).

---

### الخيار أ: Discord

يتطلب Discord خادمًا تملك فيه **صلاحيات إدارية (administrator access)** لإضافة بوت. إذا كنت تشارك خوادم ولكن لا تملك واحدًا، استخدم الخيار ب (Telegram) بدلاً من ذلك.

#### إنشاء حساب وخادم على Discord

إذا لم يكن لديك حساب على Discord، سجّل في [discord.com](https://discord.com). تحتاج أيضًا إلى خادم تكون فيه مسؤولًا إداريًا، أنشئ واحدًا بالنقر على أيقونة **+** في الشريط الجانبي لـ Discord واختيار **Create My Own**. خادم خاص يكفي.

#### إنشاء تطبيق وبوت على Discord

1. اذهب إلى [بوابة مطوري Discord](https://discord.com/developers/applications) وانقر **New Application**. أعطِه اسمًا (مثلاً "openclaw-bot").
2. في الشريط الجانبي، انقر **Bot**. عيّن اسم مستخدم للبوت.
3. لا تزال في صفحة Bot، مرّر للأسفل إلى **Privileged Gateway Intents** وفعّل:
   - **Message Content Intent** (مطلوب)
   - **Server Members Intent** (موصى به)
4. مرّر للأعلى وانقر **Reset Token** لإنشاء رمز البوت الخاص بك. انسخه.

#### إضافة البوت إلى خادمك

1. في الشريط الجانبي، انقر **OAuth2/ URL Generator**.
2. ضمن **Scopes**، فعّل `bot` و`applications.commands`.
3. ضمن **Bot Permissions**، فعّل: View Channels وSend Messages وRead Message History وEmbed Links وAttach Files.
4. انسخ الرابط الذي تم إنشاؤه، والصقه في متصفحك، واختر خادمك، وأكّد. يجب أن يظهر البوت الآن في قائمة أعضاء خادمك.

#### جمع معرّفاتك (IDs)

فعّل وضع المطور (Developer Mode) في Discord (**User Settings/ Advanced/ Developer Mode**)، ثم:
- انقر بزر الفأرة الأيمن على أيقونة خادمك: **Copy Server ID**
- انقر بزر الفأرة الأيمن على صورتك الرمزية: **Copy User ID**

#### السماح بالرسائل المباشرة من أعضاء الخادم

انقر بزر الفأرة الأيمن على أيقونة خادمك/ **Privacy Settings**/ فعّل خيار **Direct Messages**. يتيح هذا للبوت إرسال رسائل مباشرة لك، وهو مطلوب لخطوة الاقتران (pairing).

#### تهيئة OpenClaw لـ Discord

خزّن رمز البوت كمتغير بيئة، ثم أنشئ ملف تصحيح (patch file) واحد يفعّل Discord، ويشير إلى الرمز، ويضيف خادمك إلى القائمة المسموح بها. استبدل `<server_id>` و`<user_id>` بالمعرّفات التي جمعتها أعلاه.

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

> **لا تعتمد على طلب تهيئة ذلك من الوكيل.** عند تفعيل العزل (sandboxing)، لا يمكن للوكيل الكتابة إلى `~/.openclaw/openclaw.json` من داخل العزل، استخدم بدلاً من ذلك أوامر CLI أعلاه على المضيف.

أعد تشغيل الـ gateway حتى تأخذ إعدادات القناة الجديدة بعين الاعتبار:

```bash
openclaw gateway run --bind loopback --port 18789
```

يجب أن ترى `logged in to discord as <bot-name>` في مخرجات الـ gateway خلال ثوانٍ قليلة.
#### قم بربط حساب Discord الخاص بك

أرسل رسالة خاصة للبوت على Discord. سيرد عليك برمز إقران قصير.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

وافق عليه على الجهاز الذي يشغّل OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> تنتهي صلاحية رموز الإقران بعد ساعة واحدة.

يمكنك الآن التحدث مع وكيلك مباشرة من Discord وتفويض المهام إلى عتادك المحلي.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### الخيار ب: Telegram

يُعد Telegram أبسط من Discord بالنسبة لمعظم المستخدمين، فهو لا يتطلب خادمًا ولا صلاحيات إدارية.

#### إنشاء بوت Telegram

1. افتح Telegram وأرسل رسالة إلى **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات. احفظ رمز البوت الذي يمنحك إياه.

#### تهيئة OpenClaw لـ Telegram

خزّن الرمز كمتغير بيئة:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

أضف تهيئة القناة إلى `~/.openclaw/openclaw.json` (أو عدّلها عبر لوحة التحكم):

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

أعد تشغيل البوابة، ثم أرسل أي رسالة إلى بوتك على Telegram. وافق على الإقران:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

تنتهي صلاحية رموز الإقران بعد ساعة واحدة. يمكنك الآن التحدث مع وكيلك عبر رسائل Telegram الخاصة.

---

## الخطوات التالية

الآن بعد أن أصبح بإمكان وكيلك تلقي الأوامر من هاتفك والتصرف على جهازك المحلي، إليك ثلاثة اتجاهات تستحق الاستكشاف:

1. **ملخّص سوق الأسهم**: اجعل OpenClaw يجلب البيانات من واجهات برمجة التطبيقات المالية على فترات زمنية ثابتة، ويلخّص حركة اليوم باستخدام نموذجك المحلي، ويرسل ملخصًا إلى هاتفك كل صباح عبر القناة التي اخترتها.

2. **مراقبة الضبط الدقيق**: ابدأ مهمة تدريب عن بُعد عبر Telegram أو Discord، ثم اجعل الوكيل يتابع سجل التدريب ويرسل قيم الخسارة الدورية، واستخدام GPU، واستخدام القرص إلى هاتفك. وإذا توقفت العملية أو ارتفع استخدام VRAM فجأة، ستعلم بذلك فورًا دون الحاجة للتواجد أمام الجهاز.

3. **إنترنت الأشياء باستخدام نموذج VLM محلي**: وجّه كاميرا نحو بابك الأمامي، وشغّل نموذج رؤية على Lemonade، واجعل OpenClaw يحلل الإطارات عند الطلب أو عند حدوث مشغّل. اسأل "هل وصلت أي طرود اليوم؟" من هاتفك واحصل على إجابة مباشرة من عتادك الخاص.

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