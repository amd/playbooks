<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

ComfyUI היא ממשק עוצמתי, מבוסס-צמתים (node-based) עבור Stable Diffusion ומודלי דיפוזיה אחרים. בניגוד לממשקי טקסט-לתמונה מסורתיים עם תיבות פרומפט פשוטות, ComfyUI חושפת את כל צינור יצירת התמונות כגרף חזותי, ומעניקה לך שליטה מדויקת בכל שלב, מקידוד טקסט ועד מניפולציה במרחב הלטנטי ופענוח סופי.

מדריך זה מלמד אותך כיצד להשתמש ב-ComfyUI עם מודל Z Image Turbo על ה-GPU שלך כדי ליצור תמונות AI באיכות גבוהה.

## מה תלמדו

- כיצד להפעיל את ComfyUI ולטעון את תבנית Z-Image Turbo
- הבנת רכיבי צינור הדיפוזיה
- יצירת תמונות וכוונון פרמטרי היצירה
- שמירה ושיתוף של זרימות עבודה (workflows)

<!-- @device:halo_box,halo,stx,krk -->
## הגדרת תצורת הזיכרון

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מקדימות

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**הענק למשתמש שלך גישה להתקני GPU** (התנתק והתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### יצירת סביבה וירטואלית
ב-Linux, פתח מסוף בתיקייה שבחרת והרץ את הפקודה הבאה כדי ליצור venv:

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


## הפעלת ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
כדי להפעיל את ComfyUI ב-Windows, לחץ על מפעיל שולחן העבודה של ComfyUI (ComfyUI Desktop Launcher) שנמצא על שולחן העבודה שלך. עקוב אחר השלבים כדי להתקין את הגרסה המקומית עם AMD.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

לאחר מכן, לחץ על כפתור ComfyUI בחלק העליון-אמצעי של האפליקציה. פעולה זו תפתח כרטיסיית הגדרות. פתח את כרטיסיית האחסון (Storage) וודא שהנתיבים מוגדרים כך שניתן יהיה לגשת למודלים המותקנים מראש.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
ב-AMD Ryzen™ AI Halo, ComfyUI פועלת בתוך קונטיינר בנוי-מראש שאינו דורש הגדרת Python נוספת.

כדי להפעיל את ComfyUI ב-Linux, לחץ על קיצור הדרך של ComfyUI בשורת המשימות. הוא אמור להיפתח מעצמו בחלון דפדפן.
>**טיפ**: ComfyUI והמודלים שלה מאוחסנים ב-`~/.local/share/ComfyUI/models`. כאן ניתן להוסיף באופן ידני זרימות עבודה או מודלים חדשים.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
כדי להפעיל את ComfyUI ב-Windows, פשוט לחץ על קיצור הדרך של ComfyUI על שולחן העבודה שלך.
<!-- @os:end -->

<!-- @os:linux -->

כדי להפעיל את ComfyUI:

1. ודא שאתה נמצא בתוך תיקיית ComfyUI. 
2. הרץ `python3 main.py --use-pytorch-cross-attention`

ComfyUI מפעילה שרת אינטרנט מקומי. פתח את הדפדפן שלך בכתובת `http://127.0.0.1:8188` כדי לגשת לממשק.

> **טיפ**: השאר את חלון המסוף פתוח בזמן השימוש ב-ComfyUI. סגירתו תעצור את השרת.
<!-- @os:end -->
<!-- @device:end -->


## איתור תבנית Z-Image Turbo

לפני יצירת תמונות, עליך לטעון את תבנית Z-Image Turbo. הנה כיצד למצוא אותה:

1. **הבט בקצה השמאלי הרחוק ביותר של המסך** — יש שם סרגל כלים אנכי שרץ מלמעלה למטה בצד השמאלי ביותר של האפליקציה.

2. **מצא את סמל התיקייה** — בסרגל הכלים השמאלי הזה, חפש סמל שנראה כמו תיקייה. כאשר תרחף מעליו, הוא מסומן בתווית "Templates".

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **לחץ על סמל התיקייה** — פעולה זו פותחת את חלונית התבניות (Templates).

4. **חפש את "Z-Image Turbo"** — השתמש בשורת החיפוש או גלול בין התבניות הזמינות כדי למצוא את זרימת העבודה Z-Image Turbo Text To Image, ולאחר מכן לחץ כדי לטעון אותה.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## הורדת מודלים

<!-- @require:comfyui-models -->

## הבנת הממשק

כאשר תבנית Z-Image Turbo נטענת, תראה קנבס עם 2 צמתים ראשיים. הצומת הראשון נקרא 'Text to Image (Z-Image-Turbo)', והצומת השני מיועד לצפייה בתמונה. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


בצומת Z-Image, לחץ על הכפתור בפינה השמאלית העליונה כדי להרחיב את הצומת ולראות את תת-הגרף (subgraph).

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### רכיבי צינור העבודה

זרימת העבודה של Z-Image Turbo משתמשת בארבעה רכיבי מודל מרכזיים הפועלים יחד:

| רכיב | תפקיד |
|-----------|------|
| **מקודד טקסט (Text Encoder)** (Qwen 3 4B) | ממיר את פרומפט הטקסט שלך ל-embeddings שמודל הדיפוזיה מבין |
| **מודל הדיפוזיה (Diffusion Model)** (Z-Image Turbo) | הרשת הנוירונית המרכזית שמסירה רעש (denoise) באופן איטרטיבי מייצוגים לטנטיים לכדי תמונות |
| **VAE** (Variational Autoencoder) | מקודד תמונות אל/מתוך מרחב לטנטי (מפענח את הלטנטים הסופיים לפיקסלים) |
| **LoRA** (אופציונלי) | מתאמים קלים (adapters) המשנים סגנון או נושא ללא צורך באימון מחדש של מודל הבסיס |

כל צומת בזרימת העבודה מתאים לאחד מהרכיבים הללו. הנתונים זורמים משמאל לימין: טקסט ← embeddings ← הסרת רעש מונחית (guided denoising) ← לטנטים ← תמונה סופית.

## יצירת התמונה הראשונה שלך

מודל Z-Image Turbo כבר טעון. כדי ליצור תמונה:

1. **הזן את הפרומפט שלך** בצומת Z-Image הראשי. היה תיאורי. הנה דוגמה:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(אופציונלי)**: אשר או כוונן הגדרות ספציפיות נוספות בתוך תת-הגרף.
3. **לחץ על "Run Workflow" הכחול** בפינה הימנית (או הקש `Ctrl+Enter`)
4. צפה כיצד הצמתים מודגשים בעת ביצוע כל שלב

ביצוע כל זרימת העבודה אמור להסתיים תוך פחות מ-30 שניות. התמונה שנוצרה מופיעה בצומת **Save Image** ונשמרת בתיקיית `output/`.

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


## כוונון פרמטרי היצירה
### הגדרות KSampler

צומת ה-KSampler שולט בתהליך הליבה של הדיפוזיה:

| פרמטר | מה הוא שולט בו | מומלץ עבור Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | מספר איטרציות הסרת הרעש (denoising) | 4–10 (מודלים מסוג turbo עברו זיקוק לפחות שלבים) |
| **cfg** | קנה מידה של הכוונה נטולת מסווג (classifier-free guidance)—עד כמה לעקוב בקפדנות אחר הפרומפט | 1.0–2.0 (מודלים מסוג turbo משתמשים בהכוונה נמוכה מאוד) |
| **sampler_name** | אלגוריתם הסרת הרעש | `euler` ו-`res_multistep` עובדים היטב עבור מודלים מסוג turbo |
| **scheduler** | עקומת לוח הזמנים של הרעש | `normal` או `simple` |
| **seed** | זרע אקראי (seed) לצורך שחזוריות | הגדירו ערכים קבועים כדי לחדד קומפוזיציה |

### גודל התמונה

כדי לשנות את מידות הפלט, אתרו את צומת **Empty Latent Image** ושנו את **width** ו-**height**. שמרו על מידות שוות או קטנות מ-1024 פיקסלים בצלע הארוכה ביותר לקבלת איכות מיטבית.

### ModelSamplingAuraFlow

צומת **ModelSamplingAuraFlow** הוא מתאם דגימה ייעודי שמשנה את האופן שבו תהליך הדיפוזיה מטפל בלוח הזמנים של הרעש. תוכלו לראות את הצומת הזה מחובר לפלט המודל בתהליך העבודה של Z-Image Turbo.

| פרמטר | מה הוא שולט בו | ערכים מומלצים |
|-----------|------------------|-------------------|
| **shift** | מכוון את התזמון של לוח הזמנים של הרעש—ערכים גבוהים יותר דוחפים יותר עידון פרטים לשלבים מאוחרים יותר | 1.0–4.0 (ברירת המחדל היא 3.0) |

מתי לכוונן את **shift**:

- **ערכים נמוכים (1.0–2.0)**: התכנסות מהירה יותר, טוב לקומפוזיציות פשוטות
- **ערכים גבוהים (3.0–4.0)**: עידון הדרגתי יותר, יכול לשפר פרטים דקים בסצנות מורכבות

שיטת הדגימה AuraFlow תוכננה במיוחד עבור מודלים מסוג flow-matching כמו Z-Image Turbo, ומבטיחה פיזור נכון של הרעש לאורך כל תהליך היצירה.

## עבודה עם תהליכי עבודה

### שמירת תהליכי עבודה

לחצו על כפתור **Save** בתפריט כדי לייצא את תהליך העבודה שלכם כקובץ JSON. פעולה זו שומרת:

- את כל הצמתים והפרמטרים שלהם
- את כל החיבורים בין הצמתים
- את טקסט הפרומפט הנוכחי

### טעינת תהליכי עבודה

גררו קובץ JSON של תהליך עבודה אל הקנבס, או השתמשו באפשרות **Load** מהתפריט. תהליך העבודה של Z-Image Turbo שאתם רואים כברירת מחדל נטען מקובץ תהליך עבודה שמור.

### שיתוף תהליכי עבודה

תהליכי עבודה הם עצמאיים—שתפו את קובץ ה-JSON עם עמיתים, והם יוכלו לשחזר את ההגדרות המדויקות שלכם. הדבר הופך את ComfyUI לכלי מצוין לניסויים משותפים.

## הצעדים הבאים

- **חקרו צמתי LoRA**: החילו מתאמי סגנון או נושא ללא צורך באימון מחדש
- **הוסיפו פרומפטים שליליים**: חברו צומת שני מסוג CLIP Text Encode לקלט הקונדישינינג **negative** של ה-KSampler כדי להנחות את המודל להימנע ממאפיינים לא רצויים כמו טשטוש, ארטיפקטים או סימני מים
- **בנו תהליכי עבודה מותאמים אישית**: שרשרו יצירות מרובות, הוסיפו הגדלת רזולוציה (upscaling), או צרו וריאציות של תמונות
- **עיינו בתהליכי עבודה של הקהילה**: [דוגמאות ComfyUI](https://github.com/comfyanonymous/ComfyUI_examples) מכיל תהליכי עבודה מוכנים לשימוש רבים

החוזק של ComfyUI טמון בניסוי: חברו צמתים בדרכים שונות, כווננו פרמטרים, וצפו כיצד כל שינוי משפיע על הפלט. חקירה מעשית זו בונה אינטואיציה לגבי אופן פעולתם של מודלי דיפוזיה.

למידע נוסף, עיינו ב-[תיעוד ComfyUI](https://docs.comfy.org/).