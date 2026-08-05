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

ComfyUI هي واجهة قوية قائمة على العُقد لنماذج Stable Diffusion ونماذج الانتشار الأخرى. على عكس واجهات النص إلى صورة التقليدية ذات مربعات المطالبة البسيطة، تعرض ComfyUI خط أنابيب توليد الصور بالكامل كرسم بياني مرئي، مما يمنحك تحكمًا دقيقًا في كل خطوة، من ترميز النص إلى معالجة الفضاء الكامن وصولًا إلى فك الترميز النهائي.

يعلّمك هذا البرنامج التعليمي كيفية استخدام ComfyUI مع نموذج Z Image Turbo على وحدة معالجة GPU لديك لتوليد صور عالية الجودة بالذكاء الاصطناعي.

## ماذا ستتعلم

- كيفية تشغيل ComfyUI وتحميل قالب Z-Image Turbo
- فهم مكوّنات خط أنابيب الانتشار
- توليد الصور وضبط معلمات التوليد
- حفظ ومشاركة سير العمل

## ضبط إعدادات الذاكرة

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات البرمجية الأساسية

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**امنح مستخدمك حق الوصول إلى أجهزة GPU** (يجب تسجيل الخروج والدخول مرة أخرى لتفعيل ذلك):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### إنشاء بيئة افتراضية
على نظام Linux، افتح طرفية في الدليل الذي تختاره وقم بتشغيل الأمر التالي لإنشاء venv:

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
لتشغيل ComfyUI على Windows، انقر على مشغّل ComfyUI Desktop الموجود على سطح المكتب لديك. اتبع الخطوات لتثبيت الإصدار المحلي مع AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

بعد ذلك، انقر على زر ComfyUI في أعلى منتصف التطبيق. سيؤدي ذلك إلى فتح علامة تبويب الإعدادات. افتح علامة تبويب Storage وتأكد من ضبط المسارات على النحو التالي للوصول إلى النماذج المثبَّتة مسبقًا.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
على AMD Ryzen™ AI Halo، تعمل ComfyUI داخل حاوية جاهزة مسبقًا لا تتطلب أي إعداد إضافي لـ Python.

لتشغيل ComfyUI على Linux، انقر على اختصار ComfyUI في شريط المهام. يجب أن يفتح من تلقاء نفسه في نافذة متصفح.
>**نصيحة**: يتم تخزين ComfyUI ونماذجه في `~/.local/share/ComfyUI/models`. هنا يمكنك إضافة سير العمل أو النماذج الجديدة يدويًا.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
لتشغيل ComfyUI على Windows، ما عليك سوى النقر على اختصار ComfyUI الموجود على سطح المكتب لديك.
<!-- @os:end -->

<!-- @os:linux -->

لتشغيل ComfyUI:

1. تأكد من أنك داخل دليل ComfyUI. 
2. قم بتشغيل `python3 main.py --use-pytorch-cross-attention`

يبدأ ComfyUI خادم ويب محليًا. افتح متصفحك على `http://127.0.0.1:8188` للوصول إلى الواجهة.

> **نصيحة**: أبقِ نافذة الطرفية مفتوحة أثناء استخدام ComfyUI. إغلاقها سيوقف الخادم.
<!-- @os:end -->
<!-- @device:end -->


## العثور على قالب Z-Image Turbo

قبل توليد الصور، تحتاج إلى تحميل قالب Z-Image Turbo. إليك كيفية العثور عليه:

1. **انظر إلى الحافة اليسرى القصوى للشاشة**—توجد شريط أدوات عمودي يمتد من الأعلى إلى الأسفل على الجانب الأيسر الأقصى للتطبيق.

2. **ابحث عن أيقونة المجلد**—في شريط الأدوات الأيسر ذاك، ابحث عن أيقونة تشبه المجلد. عند تمرير المؤشر فوقها، ستظهر موسومة بـ "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **انقر على أيقونة المجلد**—سيؤدي ذلك إلى فتح لوحة Templates.

4. **ابحث عن "Z-Image Turbo"**—استخدم شريط البحث أو تصفّح القوالب المتاحة للعثور على سير عمل Z-Image Turbo Text To Image، ثم انقر لتحميله.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## تنزيل النماذج

<!-- @require:comfyui-models -->

## فهم الواجهة

عند تحميل قالب Z-Image Turbo، سترى لوحة عمل تحتوي على عقدتين رئيسيتين. تُسمى العقدة الأولى 'Text to Image (Z-Image-Turbo)'، والعقدة الثانية مخصصة لعرض الصورة.

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


على عقدة Z-Image، انقر على الزر العلوي الأيمن لتوسيع العقدة ورؤية الرسم البياني الفرعي.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### مكوّنات خط الأنابيب

يستخدم سير عمل Z-Image Turbo أربعة مكوّنات نموذجية رئيسية تعمل معًا:

| المكوّن | الدور |
|-----------|------|
| **مُرمِّز النص** (Qwen 3 4B) | يحوّل مطالبتك النصية إلى تضمينات (embeddings) يفهمها نموذج الانتشار |
| **نموذج الانتشار** (Z-Image Turbo) | الشبكة العصبية الأساسية التي تزيل الضوضاء تكراريًا من التمثيلات الكامنة لتحويلها إلى صور |
| **VAE** (المُرمِّز التلقائي التبايني) | يقوم بترميز الصور من/إلى الفضاء الكامن (ويفك ترميز التمثيلات الكامنة النهائية إلى وحدات بكسل) |
| **LoRA** (اختياري) | محوّلات خفيفة الوزن تعدّل الأسلوب أو الموضوع دون إعادة تدريب النموذج الأساسي |

تقابل كل عقدة في سير العمل أحد هذه المكوّنات. يتدفق البيانات من اليسار إلى اليمين: النص ← التضمينات ← إزالة الضوضاء الموجَّهة ← التمثيلات الكامنة ← الصورة النهائية.
## توليد أول صورة لك

نموذج Z-Image Turbo محمّل بالفعل. لتوليد صورة:

1. **أدخل موجّهك (prompt)** في عقدة Z-Image الرئيسية. كن وصفيًا. إليك مثال:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(اختياري)**: تأكد من أي إعدادات محددة أخرى داخل الرسم الفرعي (subgraph) أو عدّلها.
3. **انقر على زر "Run Workflow" الأزرق** في الزاوية اليمنى (أو اضغط `Ctrl+Enter`)
4. راقب تمييز العقد أثناء تنفيذ كل خطوة

من المفترض أن يكتمل تنفيذ سير العمل بأكمله في أقل من 30 ثانية. تظهر الصورة التي تم توليدها في عقدة **Save Image** ويتم حفظها في مجلد `output/`.

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


## ضبط معلمات التوليد

### إعدادات KSampler

تتحكم عقدة KSampler في عملية الانتشار (diffusion) الأساسية:

| المعلمة | ما الذي تتحكم فيه | القيم الموصى بها لـ Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | عدد تكرارات إزالة الضوضاء | 4–10 (النماذج السريعة "turbo" مقطّرة لعدد أقل من الخطوات) |
| **cfg** | مقياس التوجيه الخالي من المصنّف—مدى الالتزام بالموجّه (prompt) | 1.0–2.0 (نماذج turbo تستخدم توجيهًا منخفضًا جدًا) |
| **sampler_name** | خوارزمية إزالة الضوضاء | `euler` و`res_multistep` يعملان بشكل جيد مع نماذج turbo |
| **scheduler** | منحنى جدول الضوضاء | `normal` أو `simple` |
| **seed** | البذرة العشوائية لإمكانية إعادة الإنتاج | حدّد قيمًا ثابتة للتكرار على تركيبة معينة |

### حجم الصورة

لضبط أبعاد الإخراج، ابحث عن عقدة **Empty Latent Image** وعدّل **width** و**height**. حافظ على الأبعاد عند 1024 بكسل أو أقل على الجانب الأطول للحصول على جودة مثالية.

### ModelSamplingAuraFlow

عقدة **ModelSamplingAuraFlow** هي معدّل أخذ عينات متخصص يضبط كيفية تعامل عملية الانتشار مع جدولة الضوضاء. ستجد هذه العقدة متصلة بمخرج النموذج في سير عمل Z-Image Turbo.

| المعلمة | ما الذي تتحكم فيه | القيم الموصى بها |
|-----------|------------------|-------------------|
| **shift** | يضبط توقيت جدول الضوضاء—القيم الأعلى تدفع بمزيد من صقل التفاصيل إلى خطوات لاحقة | 1.0–4.0 (القيمة الافتراضية هي 3.0) |

متى تضبط **shift**:

- **قيم أقل (1.0–2.0)**: تقارب أسرع، مناسب للتركيبات البسيطة
- **قيم أعلى (3.0–4.0)**: صقل أكثر تدرجًا، يمكن أن يحسّن التفاصيل الدقيقة في المشاهد المعقدة

طريقة أخذ العينات AuraFlow مصممة خصيصًا لنماذج مطابقة التدفق (flow-matching) مثل Z-Image Turbo، مما يضمن توزيعًا صحيحًا للضوضاء طوال عملية التوليد.

## العمل مع سير العمل (Workflows)

### حفظ سير العمل

انقر على زر **Save** في القائمة لتصدير سير عملك كملف JSON. يلتقط هذا:

- جميع العقد ومعلماتها
- جميع الاتصالات بين العقد
- نص الموجّه الحالي

### تحميل سير العمل

اسحب ملف سير عمل JSON إلى اللوحة، أو استخدم **Load** من القائمة. سير عمل Z-Image Turbo الذي تراه افتراضيًا محمّل من ملف سير عمل محفوظ.

### مشاركة سير العمل

سير العمل مستقل بذاته—شارك ملف JSON مع زملائك، وسيتمكنون من إعادة إنتاج إعدادك بالضبط. هذا يجعل ComfyUI ممتازًا للتجريب التعاوني.

## الخطوات التالية

- **استكشف عقد LoRA**: طبّق محوّلات الأسلوب أو الموضوع دون إعادة التدريب
- **أضف موجّهات سلبية**: صِل عقدة CLIP Text Encode ثانية بمدخل التكييف **negative** في KSampler لتوجيه النموذج بعيدًا عن الميزات غير المرغوبة مثل الضبابية أو الأخطاء الفنية أو العلامات المائية
- **ابنِ سير عمل مخصص**: اربط عدة عمليات توليد معًا، أضف تحسين الدقة (upscaling)، أو أنشئ تنويعات للصور
- **تصفح سير عمل المجتمع**: [أمثلة ComfyUI](https://github.com/comfyanonymous/ComfyUI_examples) تحتوي على العديد من سير العمل الجاهزة للاستخدام

تكمن قوة ComfyUI في التجريب: صِل العقد بطرق مختلفة، اضبط المعلمات، ولاحظ كيف يؤثر كل تغيير على الناتج. هذا الاستكشاف العملي يبني الحدس حول كيفية عمل نماذج الانتشار.

لمزيد من المعلومات، اطّلع على [توثيق ComfyUI](https://docs.comfy.org/).