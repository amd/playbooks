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

ComfyUI هي واجهة قوية قائمة على العُقد لنماذج Stable Diffusion ونماذج الانتشار الأخرى. على عكس واجهات تحويل النص إلى صورة التقليدية ذات مربعات الإدخال البسيطة، تعرض ComfyUI خط أنابيب توليد الصور بالكامل كرسم بياني مرئي، مما يمنحك تحكمًا دقيقًا في كل خطوة، من ترميز النص إلى معالجة الفضاء الكامن وصولًا إلى فك التشفير النهائي.

يعلّمك هذا البرنامج التعليمي كيفية استخدام ComfyUI مع نموذج Z Image Turbo على وحدة معالجة الرسومات (GPU) الخاصة بك لتوليد صور ذكاء اصطناعي عالية الجودة.

## ما الذي ستتعلمه

- كيفية تشغيل ComfyUI وتحميل قالب Z-Image Turbo
- فهم مكوّنات خط أنابيب الانتشار
- توليد الصور وضبط معاملات التوليد
- حفظ سير العمل ومشاركته

<!-- @device:halo_box,halo,stx,krk -->
## تعيين إعداد الذاكرة

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرمجيات

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرمجيات

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك إمكانية الوصول إلى أجهزة GPU** (يجب تسجيل الخروج ثم الدخول مرة أخرى لتفعيل ذلك):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### إنشاء بيئة افتراضية
على Linux، افتح طرفية (terminal) في المجلد الذي تختاره ونفّذ الأمر التالي لإنشاء بيئة venv:

<!-- @test:id=create-venv-linux timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv comfyui-env
source comfyui-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source comfyui-env/bin/activate" -->
<!-- @device:end -->

<!-- @require:driver,pytorch,comfyui -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-desktop-workspace-present-windows timeout=60 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) installs into %LOCALAPPDATA%\Comfy-Desktop\
# Layout: ComfyUI-Installs\<name>\ComfyUI\ holds main.py + .venv
#         ComfyUI-Shared\ holds the shared model library
$instBase  = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI"
$comfyRoot = Join-Path $instBase "ComfyUI"
$py        = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy    = Join-Path $comfyRoot "main.py"
$sharedModels = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"

if (-not (Test-Path $instBase))     { throw "Comfy Desktop instance not found at: $instBase" }
if (-not (Test-Path $comfyRoot))    { throw "ComfyUI source not found at: $comfyRoot" }
if (-not (Test-Path $py))           { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $mainPy))       { throw "ComfyUI main.py not found: $mainPy" }
if (-not (Test-Path $sharedModels)) { throw "Comfy Desktop shared models dir not found: $sharedModels" }

Write-Host "OK: instance root: $instBase"
Write-Host "OK: ComfyUI source: $comfyRoot"
Write-Host "OK: Python: $py"
Write-Host "OK: main.py: $mainPy"
Write-Host "OK: shared models: $sharedModels"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-clone-linux timeout=300 hidden=True -->
```bash
set -euo pipefail
if [ -d "ComfyUI/.git" ]; then
 (cd ComfyUI && git fetch --all && git reset --hard origin/master)
else
 git clone https://github.com/Comfy-Org/ComfyUI.git
fi
cd ComfyUI
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-requirements-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r ./ComfyUI/requirements.txt
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=comfyui-sync-requirements-windows timeout=600 hidden=True -->
```powershell
$comfyRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py  = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$req = Join-Path $comfyRoot "requirements.txt"

if (-not (Test-Path $py))  { throw "ComfyUI venv python not found: $py" }
if (-not (Test-Path $req)) { throw "ComfyUI requirements.txt not found: $req" }

& $py -m pip install --upgrade --force-reinstall --no-cache-dir comfyui-frontend-package
if ($LASTEXITCODE -ne 0) { throw "Failed to install comfyui-frontend-package into workspace venv." }

& $py -c "import importlib.metadata as m; print(m.version('comfyui-frontend-package'))"
if ($LASTEXITCODE -ne 0) { throw "comfyui-frontend-package metadata still missing after install." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows --> 
<!-- @test:id=comfyui-backend-usable-windows timeout=120 hidden=True -->
```powershell
$py = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Missing ComfyUI venv python: $py" }

& $py -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
if ($LASTEXITCODE -ne 0) { throw "Torch import/check failed in ComfyUI venv." }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-install-rocm-torch-linux timeout=900 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

python - <<'PY'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"ROCm/HIP version: {getattr(torch.version, 'hip', None)}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-verify-torch-linux timeout=120 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('hip', getattr(torch.version,'hip',None));"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows --> 
<!-- @test:id=comfyui-populate-models-from-cache-windows timeout=600 hidden=True -->
```powershell
# The new Comfy Desktop (since June 2026) uses a shared model library separate from the ComfyUI source.
# Models are served from %LOCALAPPDATA%\Comfy-Desktop\ComfyUI-Shared\models\
# as configured in shared_model_paths.yaml.
$modelsRoot = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Shared\models"
if (-not (Test-Path $modelsRoot)) { throw "Comfy Desktop shared models dir not found: $modelsRoot" }

$cacheDiff = "C:\ModelCache\ComfyUI\models\diffusion_models\z_image_turbo_bf16.safetensors"
$cacheTE   = "C:\ModelCache\ComfyUI\models\text_encoders\qwen_3_4b.safetensors"
$cacheVAE  = "C:\ModelCache\ComfyUI\models\vae\ae.safetensors"

if (-not (Test-Path $cacheDiff)) { throw "models missing on runner: $cacheDiff" }
if (-not (Test-Path $cacheTE))   { throw "models missing on runner: $cacheTE" }
if (-not (Test-Path $cacheVAE))  { throw "models missing on runner: $cacheVAE" }

New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "diffusion_models")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "text_encoders")
New-Item -ItemType Directory -Force -Path (Join-Path $modelsRoot "vae")

Copy-Item -Force $cacheDiff (Join-Path $modelsRoot "diffusion_models\z_image_turbo_bf16.safetensors")
Copy-Item -Force $cacheTE   (Join-Path $modelsRoot "text_encoders\qwen_3_4b.safetensors")
Copy-Item -Force $cacheVAE  (Join-Path $modelsRoot "vae\ae.safetensors")

Write-Host "OK: models copied into $modelsRoot"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=comfyui-populate-models-from-cache-linux timeout=600 hidden=True -->
```bash
cd ComfyUI
cache_diff="/opt/model_cache/ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors"
cache_te="/opt/model_cache/ComfyUI/models/text_encoders/qwen_3_4b.safetensors"
cache_vae="/opt/model_cache/ComfyUI/models/vae/ae.safetensors"
test -f "$cache_diff" || (echo "models missing on runner: $cache_diff" && exit 1)
test -f "$cache_te" || (echo "models missing on runner: $cache_te" && exit 1)
test -f "$cache_vae" || (echo "models missing on runner: $cache_vae" && exit 1)
mkdir -p models/diffusion_models models/text_encoders models/vae
cp -f "$cache_diff" models/diffusion_models/z_image_turbo_bf16.safetensors
cp -f "$cache_te" models/text_encoders/qwen_3_4b.safetensors
cp -f "$cache_vae" models/vae/ae.safetensors
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=comfyui-server-up-windows timeout=300 hidden=True -->
```powershell
$comfyRoot   = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py          = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy      = Join-Path $comfyRoot "main.py"
$sharedPaths = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not reachable at http://127.0.0.1:8188/" }
 Write-Host "OK: ComfyUI server is reachable!"
} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-server-up-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not reachable at http://127.0.0.1:8188/"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

echo "OK: ComfyUI server is reachable!"
```
<!-- @test:end --> 
<!-- @os:end -->


## تشغيل ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
لتشغيل ComfyUI على Windows، انقر على مُشغّل ComfyUI Desktop الموجود على سطح المكتب. اتبع الخطوات لتثبيت النسخة المحلية مع AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

بعد ذلك، انقر على زر ComfyUI في أعلى منتصف التطبيق. سيؤدي ذلك إلى فتح علامة تبويب الإعدادات. افتح علامة التبويب Storage وتأكد من أن المسارات مضبوطة كما يلي للوصول إلى النماذج المثبتة مسبقًا.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
على AMD Ryzen™ AI Halo، يعمل ComfyUI داخل حاوية مُعدّة مسبقًا لا تتطلب أي إعداد إضافي لـ Python.

لتشغيل ComfyUI على Linux، انقر على اختصار ComfyUI في شريط المهام. يجب أن يفتح من تلقاء نفسه في نافذة متصفح.
>**نصيحة**: يتم تخزين ComfyUI ونماذجه في `~/.local/share/ComfyUI/models`. هنا يمكنك إضافة سير العمل أو النماذج الجديدة يدويًا.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
لتشغيل ComfyUI على Windows، ما عليك سوى النقر على اختصار ComfyUI على سطح المكتب.
<!-- @os:end -->

<!-- @os:linux -->

لتشغيل ComfyUI:

1. تأكد من أنك داخل مجلد ComfyUI.
2. نفّذ الأمر `python3 main.py --use-pytorch-cross-attention`

يبدأ ComfyUI خادم ويب محليًا. افتح متصفحك على العنوان `http://127.0.0.1:8188` للوصول إلى الواجهة.

> **نصيحة**: أبقِ نافذة الطرفية مفتوحة أثناء استخدام ComfyUI. إغلاقها سيوقف الخادم.
<!-- @os:end -->
<!-- @device:end -->


## العثور على قالب Z-Image Turbo

قبل توليد الصور، تحتاج إلى تحميل قالب Z-Image Turbo. إليك كيفية العثور عليه:

1. **انظر إلى الحافة اليسرى القصوى للشاشة**—يوجد شريط أدوات عمودي يمتد من الأعلى إلى الأسفل في أقصى يسار التطبيق.

2. **ابحث عن أيقونة المجلد**—في ذلك الشريط الأيسر، ابحث عن أيقونة تشبه المجلد. عند تمرير المؤشر فوقها، ستظهر بعنوان "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **انقر على أيقونة المجلد**—سيؤدي ذلك إلى فتح لوحة Templates.

4. **ابحث عن "Z-Image Turbo"**—استخدم شريط البحث أو مرّر عبر القوالب المتاحة للعثور على سير عمل Z-Image Turbo Text To Image، ثم انقر لتحميله.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## تنزيل النماذج

<!-- @require:comfyui-models -->

## فهم الواجهة

عند تحميل قالب Z-Image Turbo، سترى لوحة عمل تحتوي على عُقدتين رئيسيتين. تُسمّى العقدة الأولى 'Text to Image (Z-Image-Turbo)'، والثانية مخصصة لعرض الصورة.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


على عقدة Z-Image، انقر على الزر في أعلى اليمين لتوسيع العقدة ومشاهدة الرسم البياني الفرعي (subgraph).

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### مكوّنات خط الأنابيب

يستخدم سير عمل Z-Image Turbo أربعة مكوّنات أساسية للنموذج تعمل معًا:

| المكوّن | الدور |
|-----------|------|
| **مُرمّز النص** (Qwen 3 4B) | يحوّل موجّهك النصي إلى تضمينات (embeddings) يفهمها نموذج الانتشار |
| **نموذج الانتشار** (Z-Image Turbo) | الشبكة العصبية الأساسية التي تزيل الضوضاء بشكل تكراري من التمثيلات الكامنة لتحويلها إلى صور |
| **VAE** (المُشفّر التلقائي التبايني) | يقوم بترميز الصور من وإلى الفضاء الكامن (يفك تشفير التمثيلات الكامنة النهائية إلى وحدات بكسل) |
| **LoRA** (اختياري) | محوّلات خفيفة الوزن تعدّل الأسلوب أو الموضوع دون إعادة تدريب النموذج الأساسي |

تقابل كل عقدة في سير العمل أحد هذه المكوّنات. تتدفق البيانات من اليسار إلى اليمين: النص ← التضمينات ← إزالة الضوضاء الموجّهة ← التمثيلات الكامنة ← الصورة النهائية.

## توليد صورتك الأولى

نموذج Z-Image Turbo محمّل بالفعل. لتوليد صورة:

1. **أدخل موجّهك (prompt)** في عقدة Z-Image الرئيسية. كن وصفيًا. إليك مثال:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(اختياري)**: تأكد من أي إعدادات محدّدة أخرى داخل الرسم البياني الفرعي أو عدّلها.
3. **انقر على زر "Run Workflow" الأزرق** في الزاوية اليمنى (أو اضغط `Ctrl+Enter`)
4. راقب تمييز العُقد أثناء تنفيذ كل خطوة

يجب أن يكتمل تنفيذ سير العمل بالكامل في أقل من 30 ثانية. تظهر الصورة المولّدة في عقدة **Save Image** ويتم حفظها في مجلد `output/`.

<!-- @os:windows -->
<!-- @test:id=comfyui-generate-zimage-windows timeout=1200 hidden=True -->
```powershell
$comfyRoot      = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI"
$py             = Join-Path $comfyRoot ".venv\Scripts\python.exe"
$mainPy         = Join-Path $comfyRoot "main.py"
$sharedPaths    = Join-Path $env:APPDATA "Comfy Desktop\shared_model_paths.yaml"

$proc = Start-Process -FilePath $py `
 -ArgumentList "`"$mainPy`" --listen 127.0.0.1 --port 8188 --extra-model-paths-config `"$sharedPaths`"" `
 -WorkingDirectory $comfyRoot `
 -NoNewWindow -PassThru

try {
 $ok = $false
 for ($i=0; $i -lt 60; $i++) {
   $resp = curl.exe -s --max-time 2 http://127.0.0.1:8188/
   if ($LASTEXITCODE -eq 0 -and $resp) { $ok = $true; break }
   Start-Sleep -Seconds 1
 }
 if (-not $ok) { throw "ComfyUI server not ready on http://127.0.0.1:8188/" }

 # run submit script from assets working dir (where image_z_image_turbo.json should exist)
 @'
import json, time, urllib.request, urllib.error, sys, os
wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")
with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)
data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)
try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)
except Exception as e:
  print("Request failed:", repr(e))
  sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
sys.exit(1)
'@ | & $py -
 if ($LASTEXITCODE -ne 0) { throw "Workflow submit/generation failed" }

} finally {
 Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:linux --> 
<!-- @test:id=comfyui-generate-zimage-linux timeout=1200 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}
# start server
python ./ComfyUI/main.py --listen 127.0.0.1 --port 8188 >/tmp/comfyui.log 2>&1 &
PID=$!

cleanup() {
 kill -9 "$PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# wait ready
ok=0
for i in $(seq 1 60); do
 resp="$(curl -s --max-time 2 http://127.0.0.1:8188/ || true)"
 if [ -n "$resp" ]; then ok=1; break; fi
 sleep 1
done

if [ "$ok" -ne 1 ]; then
 echo "ComfyUI server not ready"
 tail -n 200 /tmp/comfyui.log || true
 exit 1
fi

# submit workflow json from assets folder (one level up from ComfyUI)
python - <<'PY'
import json, time, urllib.request, urllib.error, sys, os

wf_path = "image_z_image_turbo.json"
if not os.path.exists(wf_path):
 raise SystemExit(f"Missing workflow json in working dir: {os.getcwd()} -> {wf_path}")

with open(wf_path, "r", encoding="utf-8") as f:
 workflow = json.load(f)

data = json.dumps({"prompt": workflow}).encode("utf-8")
req = urllib.request.Request(
 "http://127.0.0.1:8188/prompt",
 data=data,
 headers={"Content-Type":"application/json"},
 method="POST",
)

try:
 with urllib.request.urlopen(req, timeout=60) as r:
   prompt_id = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
 body = e.read().decode("utf-8", "replace")
 print("HTTPError", e.code, e.reason)
 print(body)
 sys.exit(1)

for _ in range(600):
 with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}", timeout=60) as r:
   hist = json.load(r)
 entry = hist.get(prompt_id, {})
 if entry.get("outputs"):
   print("OK, output image generated!")
   sys.exit(0)
 time.sleep(1)

print("No outputs after waiting.")
print("history status:", json.dumps(entry.get("status", {})))  # surfaces the ComfyUI node/execution error
sys.exit(1)
PY
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows -->
<!-- @test:id=comfyui-output-exists-windows timeout=60 hidden=True -->
```powershell
$outDir = Join-Path $env:LOCALAPPDATA "Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\output"

# ComfyUI saves into date-stamped subdirectories, so recurse to find PNGs
$files = Get-ChildItem -Path $outDir -Filter *.png -File -Recurse -ErrorAction SilentlyContinue
if (-not $files) {
 throw "No PNG files found under: $outDir"
}
$files | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { $_.FullName }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=comfyui-output-exists-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
ls -1 ComfyUI/output/*.png >/dev/null 2>&1 || (echo "No PNG files found in ComfyUI/output" && exit 1)
ls -1t ComfyUI/output/*.png | head -n 5
```
<!-- @test:end --> 
<!-- @os:end -->


## ضبط معاملات التوليد
### إعدادات KSampler

تتحكم عقدة KSampler في عملية الانتشار (diffusion) الأساسية:

| المعامل | ما الذي يتحكم فيه | الموصى به لـ Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | عدد تكرارات إزالة التشويش | 4–10 (النماذج المُقطّرة turbo مصممة لعدد أقل من الخطوات) |
| **cfg** | مقياس التوجيه الخالي من المصنّف (classifier-free guidance)—مدى الالتزام بالموجّه (prompt) | 1.0–2.0 (نماذج turbo تستخدم توجيهًا منخفضًا جدًا) |
| **sampler_name** | خوارزمية إزالة التشويش | `euler` و`res_multistep` يعملان بشكل جيد مع نماذج turbo |
| **scheduler** | منحنى جدولة التشويش | `normal` أو `simple` |
| **seed** | البذرة العشوائية لضمان قابلية إعادة الإنتاج | حدّد قيمًا ثابتة للتكرار على تركيبة معينة |

### حجم الصورة

لضبط أبعاد المخرجات، ابحث عن عقدة **Empty Latent Image** وعدّل **width** و**height**. حافظ على الأبعاد عند 1024 بكسل أو أقل على الجانب الأطول للحصول على أفضل جودة.

### ModelSamplingAuraFlow

عقدة **ModelSamplingAuraFlow** هي معدّل أخذ عينات متخصص يضبط كيفية تعامل عملية الانتشار مع جدولة التشويش. سترى هذه العقدة متصلة بمخرج النموذج في سير عمل Z-Image Turbo.

| المعامل | ما الذي يتحكم فيه | القيم الموصى بها |
|-----------|------------------|-------------------|
| **shift** | يضبط توقيت جدولة التشويش—القيم الأعلى تدفع مزيدًا من تحسين التفاصيل إلى الخطوات اللاحقة | 1.0–4.0 (القيمة الافتراضية هي 3.0) |

متى تضبط **shift**:

- **قيم أقل (1.0–2.0)**: تقارب أسرع، جيد للتركيبات البسيطة
- **قيم أعلى (3.0–4.0)**: تحسين أكثر تدرجًا، يمكن أن يحسّن التفاصيل الدقيقة في المشاهد المعقدة

طريقة أخذ العينات AuraFlow مصممة خصيصًا لنماذج مطابقة التدفق (flow-matching) مثل Z-Image Turbo، مما يضمن توزيعًا صحيحًا للتشويش طوال عملية التوليد.

## العمل مع سير العمل

### حفظ سير العمل

انقر على زر **Save** في القائمة لتصدير سير العمل الخاص بك كملف JSON. يشمل هذا:

- جميع العقد ومعاملاتها
- جميع الاتصالات بين العقد
- نص الموجّه الحالي

### تحميل سير العمل

اسحب ملف JSON لسير العمل إلى مساحة العمل (canvas)، أو استخدم **Load** من القائمة. يتم تحميل سير عمل Z-Image Turbo الذي تراه افتراضيًا من ملف سير عمل محفوظ.

### مشاركة سير العمل

سير العمل مستقل بذاته—شارك ملف JSON مع زملائك، وسيتمكنون من إعادة إنتاج إعدادك بالضبط. هذا يجعل ComfyUI ممتازًا للتجارب التعاونية.

## الخطوات التالية

- **استكشف عقد LoRA**: طبّق محوّلات الأسلوب أو الموضوع دون الحاجة لإعادة التدريب
- **أضف موجّهات سلبية**: اربط عقدة CLIP Text Encode ثانية بمدخل التكييف **negative** في KSampler لتوجيه النموذج بعيدًا عن السمات غير المرغوبة مثل الضبابية أو التشوهات أو العلامات المائية
- **ابنِ سير عمل مخصصًا**: سلسل عدة عمليات توليد، أضف تحسين الدقة (upscaling)، أو أنشئ اختلافات للصور
- **تصفّح سير العمل المجتمعي**: يحتوي [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) على العديد من سير العمل الجاهزة للاستخدام

تكمن قوة ComfyUI في التجريب: اربط العقد بطرق مختلفة، واضبط المعاملات، ولاحظ كيف يؤثر كل تغيير على المخرجات. هذا الاستكشاف العملي يبني الحدس حول كيفية عمل نماذج الانتشار.

لمزيد من المعلومات، راجع [ComfyUI Documentation](https://docs.comfy.org/).