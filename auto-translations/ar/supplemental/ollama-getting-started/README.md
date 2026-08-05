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

Ollama هي أداة خفيفة الوزن وشائعة الاستخدام لتشغيل نماذج اللغة الكبيرة محليًا. تتولى تنزيل النماذج، وتحويلها إلى صيغة الكم (quantization)، وتقديمها من خلال واجهة سطر أوامر بسيطة وتطبيق سطح مكتب، بحيث يمكنك الانتقال من الصفر إلى الدردشة مع نموذج لغوي كبير في دقائق معدودة.

يرشدك هذا الدليل التعليمي خلال عملية تثبيت Ollama، وسحب نموذج GPT-OSS 20B، وإجراء محادثة معه، سواء عبر الطرفية أو تطبيق سطح المكتب.

## ما ستتعلمه

- كيفية تثبيت وتشغيل Ollama على نظامك
- سحب وتشغيل نموذج GPT-OSS 20B محليًا
- الدردشة مع النماذج باستخدام واجهة سطر الأوامر (CLI)
- الاستعلام من النماذج برمجيًا عبر واجهة REST API

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج
> **ملاحظة**: إذا لم يكن VS Code مثبتًا، يمكنك تثبيته باستخدام Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية

<!-- @require:driver -->

### تثبيت Ollama

<!-- @os:windows -->

1. قم بتنزيل برنامج التثبيت من [ollama.com/download](https://ollama.com/download).
2. شغّل برنامج التثبيت `.exe` واتبع التعليمات.
3. بمجرد التثبيت، يعمل Ollama كخدمة في الخلفية ويمكن الوصول إليه من الطرفية وتطبيق سطح المكتب وعلبة النظام.

تحقق من التثبيت بفتح طرفية وتشغيل:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

يجب أن ترى رقم الإصدار المثبت مطبوعًا في وحدة التحكم.
<!-- @os:end -->

<!-- @os:linux -->

شغّل نص التثبيت الرسمي:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

تحقق من التثبيت:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

يجب أن ترى رقم الإصدار المثبت مطبوعًا في وحدة التحكم.
<!-- @os:end -->

## سحب أول نموذج لك

يدير Ollama النماذج من خلال سجل مشابه لصور الحاويات. لتنزيل GPT-OSS 20B:

```bash
ollama pull gpt-oss:20b
```

يقوم هذا بتنزيل أوزان النموذج إلى جهازك المحلي (حوالي 12 جيجابايت). يحدث التنزيل مرة واحدة فقط، وتُحمَّل عمليات التشغيل اللاحقة النموذج من القرص.

يمكنك التأكد من توفر النموذج باستخدام:

```bash
ollama list
```

يجب أن ترى `gpt-oss:20b` في الناتج مع حجمه وتاريخ آخر تعديل له.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### تسمية النماذج

تتبع أسماء نماذج Ollama التنسيق `name:tag`. تشير الوسمة (tag) عادةً إلى عدد المعلمات أو نوع التحويل إلى صيغة الكم. فيما يلي بعض الأوامر المفيدة لإدارة النماذج:

| الأمر | الوصف |
|---------|-------------|
| `ollama list` | عرض جميع النماذج التي تم تنزيلها |
| `ollama pull <model>` | تنزيل نموذج دون تشغيله |
| `ollama rm <model>` | إزالة نموذج لتحرير مساحة القرص |
| `ollama show <model>` | عرض بيانات النموذج الوصفية ومعلماته |

## الدردشة من الطرفية

ابدأ جلسة دردشة تفاعلية مباشرة من سطر الأوامر:

```bash
ollama run gpt-oss:20b
```

يقوم Ollama بتحميل النموذج في الذاكرة وينقلك إلى موجّه الأوامر. جرّب سؤاله عن شيء ما:

```
>>> What is the capital of France and why is it historically significant?
```

يقوم النموذج ببث استجابته رمزًا تلو الآخر (token-by-token) مباشرة في الطرفية. اكتب `/bye` أو اضغط `Ctrl+D` للخروج من الجلسة.

> **نصيحة**: يستغرق التشغيل الأول بضع ثوانٍ لتحميل النموذج في الذاكرة. تستجيب المطالبات اللاحقة ضمن الجلسة نفسها بشكل أسرع بكثير لأن النموذج يظل محمّلًا.

<!-- @os:windows -->
## الدردشة من تطبيق سطح المكتب

يأتي Ollama أيضًا مزودًا بتطبيق سطح مكتب يوفر واجهة دردشة نظيفة للتفاعل مع نماذجك.

افتح **Ollama** من قائمة ابدأ أو انقر على أيقونة Ollama في علبة النظام واختر **Open Ollama**.

بمجرد فتح التطبيق:

1. انقر على **New Chat** في الشريط الجانبي.
2. اختر **gpt-oss:20b** من القائمة المنسدلة للنماذج في الزاوية السفلية اليمنى من منطقة إدخال الدردشة.
3. اكتب رسالة واضغط Enter لبدء الدردشة.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

يحتفظ تطبيق سطح المكتب بسجل محادثاتك في الشريط الجانبي، مما يسهّل الرجوع إلى المحادثات السابقة.
<!-- @os:end -->

## استخدام واجهة REST API

بعد التثبيت، يعمل Ollama كخدمة في الخلفية ويعرض واجهة REST API على العنوان `http://localhost:11434` يمكنك استخدامها لدمج النماذج في تطبيقاتك ونصوصك البرمجية الخاصة.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### توليد استجابة في الطرفية

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

الاستجابة عبارة عن كائن JSON يحتوي على ناتج النموذج في الحقل `response`.


### مثال بلغة Python
الآن بعد أن أصبح بإمكاننا استدعاء واجهة Ollama API برمجيًا، لنستدعيها من Python.

#### إنشاء بيئة افتراضية في الطرفية

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### إنشاء ملف Python
في نفس الدليل، استخدم VS Code أو محررًا آخر لإنشاء ملف .py وانسخ الكود التالي فيه. بعد ذلك، شغّل الملف في بيئتك المفعّلة باستخدام `python your_file_name.py`

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### نقاط نهاية API الرئيسية

| نقطة النهاية | الطريقة | الغرض |
|----------|--------|---------|
| `/api/generate` | POST | توليد نص بدورة واحدة |
| `/api/chat` | POST | محادثة متعددة الأدوار مع سجل الرسائل |
| `/api/tags` | GET | عرض قائمة النماذج المتاحة |
| `/api/show` | POST | عرض تفاصيل النموذج |
| `/api/pull` | POST | سحب نموذج من السجل |

للاطلاع على مرجع API الكامل، راجع [وثائق Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md).
## الخطوات التالية

- **جرّب نماذج مختلفة**: تصفح [مكتبة نماذج Ollama](https://ollama.com/library) لاستكشاف مئات النماذج المتاحة، من مساعدي البرمجة الصغيرة إلى نماذج الاستدلال الكبيرة.
- **أنشئ نماذج مخصصة**: استخدم [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) لضبط موجّهات النظام المخصصة، ودرجة الحرارة، وغيرها من المعلمات للحصول على تجربة مخصصة.
- **ابنِ باستخدام الواجهة البرمجية (API)**: استخدم مكتبات العميل [Python](https://github.com/ollama/ollama-python) أو [JavaScript](https://github.com/ollama/ollama-js) لدمج Ollama في تطبيقاتك.
- **اتصل بالواجهات الأمامية**: اقرن Ollama مع أدوات مثل [Open WebUI](https://github.com/open-webui/open-webui) للحصول على واجهة محادثة غنية بالميزات تتضمن البحث والشخصيات ورفع المستندات.

لمزيد من المعلومات، اطّلع على [توثيق Ollama](https://github.com/ollama/ollama/blob/main/README.md).