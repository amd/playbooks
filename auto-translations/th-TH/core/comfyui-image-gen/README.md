<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

ComfyUI คืออินเทอร์เฟซแบบโหนดที่ทรงพลังสำหรับ Stable Diffusion และโมเดล diffusion อื่นๆ ต่างจากอินเทอร์เฟซแบบข้อความเป็นภาพทั่วไปที่มีเพียงช่องป้อน prompt ComfyUI เปิดเผยกระบวนการสร้างภาพทั้งหมดในรูปแบบกราฟภาพ ให้คุณควบคุมทุกขั้นตอนอย่างละเอียด ตั้งแต่การเข้ารหัสข้อความไปจนถึงการจัดการ latent space และการถอดรหัสขั้นสุดท้าย

บทช่วยสอนนี้จะสอนวิธีใช้ ComfyUI กับโมเดล Z Image Turbo บน GPU ของคุณเพื่อสร้างภาพ AI คุณภาพสูง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเปิด ComfyUI และโหลดเทมเพลต Z-Image Turbo
- ทำความเข้าใจส่วนประกอบของ diffusion pipeline
- การสร้างภาพและปรับแต่งพารามิเตอร์การสร้าง
- การบันทึกและแชร์ workflow

## การตั้งค่าการกำหนดค่าหน่วยความจำ

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### สร้าง Virtual Environment
บน Linux ให้เปิด terminal ในไดเรกทอรีที่คุณต้องการ แล้วรันคำสั่งต่อไปนี้เพื่อสร้าง venv:

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


## การเปิด ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
หากต้องการเปิด ComfyUI บน Windows ให้คลิก ComfyUI Desktop Launcher ที่อยู่บน Desktop ของคุณ ทำตามขั้นตอนเพื่อติดตั้งเวอร์ชันในเครื่องกับ AMD

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

จากนั้นคลิกปุ่ม ComfyUI ที่ด้านบนตรงกลางของแอป ซึ่งจะเปิดแท็บการตั้งค่า เปิดแท็บ Storage และตรวจสอบให้แน่ใจว่าเส้นทางถูกตั้งค่าดังต่อไปนี้เพื่อเข้าถึงโมเดลที่ติดตั้งไว้ล่วงหน้า

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
หากต้องการเปิด ComfyUI บน Linux ให้คลิกทางลัด ComfyUI ในแถบงาน ซึ่งจะเปิดในหน้าต่างเบราว์เซอร์โดยอัตโนมัติ
>**เคล็ดลับ**: ComfyUI และโมเดลต่างๆ จะถูกเก็บไว้ที่ `~/.local/share/ComfyUI/models` นี่คือที่ที่คุณสามารถเพิ่ม workflow หรือโมเดลใหม่ด้วยตนเองได้


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
หากต้องการเปิด ComfyUI บน Windows เพียงคลิกทางลัด ComfyUI บน Desktop ของคุณ
<!-- @os:end -->

<!-- @os:linux -->

หากต้องการเปิด ComfyUI:

1. ตรวจสอบให้แน่ใจว่าคุณอยู่ในไดเรกทอรี ComfyUI 
2. รัน `python3 main.py --use-pytorch-cross-attention`

ComfyUI จะเริ่มต้นเว็บเซิร์ฟเวอร์ในเครื่อง เปิดเบราว์เซอร์ไปที่ `http://127.0.0.1:8188` เพื่อเข้าถึงอินเทอร์เฟซ

> **เคล็ดลับ**: เปิดหน้าต่าง terminal ไว้ขณะใช้งาน ComfyUI การปิดหน้าต่างจะหยุดเซิร์ฟเวอร์
<!-- @os:end -->
<!-- @device:end -->


## การค้นหาเทมเพลต Z-Image Turbo

ก่อนสร้างภาพ คุณต้องโหลดเทมเพลต Z-Image Turbo ก่อน วิธีค้นหามีดังนี้:

1. **มองที่ขอบซ้ายสุดของหน้าจอ**—มีแถบเครื่องมือแนวตั้งที่ทอดยาวจากบนลงล่างทางด้านซ้ายสุดของแอป

2. **ค้นหาไอคอนโฟลเดอร์**—ในแถบเครื่องมือด้านซ้ายนั้น ให้มองหาไอคอนที่มีลักษณะเหมือนโฟลเดอร์ เมื่อคุณวางเมาส์เหนือมัน จะมีป้ายกำกับว่า "Templates"

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **คลิกไอคอนโฟลเดอร์**—ซึ่งจะเปิดแผง Templates

4. **ค้นหา "Z-Image Turbo"**—ใช้แถบค้นหาหรือเลื่อนดูเทมเพลตที่มีอยู่เพื่อค้นหา workflow Z-Image Turbo Text To Image จากนั้นคลิกเพื่อโหลด

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## การดาวน์โหลดโมเดล

<!-- @require:comfyui-models -->

## ทำความเข้าใจอินเทอร์เฟซ

เมื่อเทมเพลต Z-Image Turbo โหลดขึ้นมา คุณจะเห็น canvas ที่มีโหนดหลัก 2 โหนด โหนดแรกชื่อว่า 'Text to Image (Z-Image-Turbo)' และโหนดที่สองใช้สำหรับดูภาพ

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


บนโหนด Z-Image ให้คลิกปุ่มด้านบนขวาเพื่อขยายโหนดและดู subgraph

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### ส่วนประกอบของ Pipeline

workflow Z-Image Turbo ใช้ส่วนประกอบโมเดลหลักสี่อย่างที่ทำงานร่วมกัน:

| ส่วนประกอบ | บทบาท |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | แปลง text prompt ของคุณเป็น embedding ที่โมเดล diffusion เข้าใจ |
| **Diffusion Model** (Z-Image Turbo) | เครือข่ายประสาทเทียมหลักที่ทำการ denoise การแสดงแทน latent ซ้ำๆ เพื่อสร้างภาพ |
| **VAE** (Variational Autoencoder) | เข้ารหัสภาพไปยัง/จาก latent space (ถอดรหัส latent สุดท้ายเป็นพิกเซล) |
| **LoRA** (ไม่บังคับ) | อะแดปเตอร์น้ำหนักเบาที่ปรับเปลี่ยนสไตล์หรือหัวข้อโดยไม่ต้องฝึกโมเดลพื้นฐานใหม่ |

แต่ละโหนดใน workflow สอดคล้องกับส่วนประกอบเหล่านี้ ข้อมูลไหลจากซ้ายไปขวา: ข้อความ → embedding → guided denoising → latents → ภาพสุดท้าย

## การสร้างภาพแรกของคุณ

โมเดล Z-Image Turbo โหลดพร้อมใช้งานแล้ว หากต้องการสร้างภาพ:

1. **ป้อน prompt ของคุณ** ในโหนด Z-Image หลัก ควรอธิบายอย่างละเอียด นี่คือตัวอย่าง:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(ไม่บังคับ)**: ยืนยันหรือปรับแต่งการตั้งค่าเฉพาะอื่นๆ ภายใน subgraph
3. **คลิก "Run Workflow" สีน้ำเงิน** ที่มุมขวา (หรือกด `Ctrl+Enter`)
4. ดูโหนดที่ไฮไลต์ขณะที่แต่ละขั้นตอนทำงาน

การดำเนินการ workflow ทั้งหมดควรเสร็จสิ้นภายในเวลาไม่ถึง 30 วินาที ภาพที่สร้างขึ้นจะปรากฏในโหนด **Save Image** และถูกบันทึกไปยังโฟลเดอร์ `output/`

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


## การปรับพารามิเตอร์การสร้าง

### การตั้งค่า KSampler

โหนด KSampler ควบคุมกระบวนการ diffusion หลัก:

| พารามิเตอร์ | สิ่งที่ควบคุม | แนะนำสำหรับ Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | จำนวนรอบการ denoise | 4–10 (โมเดล turbo ถูก distill สำหรับขั้นตอนที่น้อยกว่า) |
| **cfg** | ค่า classifier-free guidance scale—ความใกล้เคียงกับ prompt มากแค่ไหน | 1.0–2.0 (โมเดล turbo ใช้ guidance ต่ำมาก) |
| **sampler_name** | อัลกอริทึมการ denoise | `euler` และ `res_multistep` ทำงานได้ดีกับโมเดล turbo |
| **scheduler** | เส้นโค้งตารางเวลาของ noise | `normal` หรือ `simple` |
| **seed** | seed แบบสุ่มสำหรับความสามารถในการทำซ้ำ | ตั้งค่าคงที่เพื่อทำซ้ำบน composition |

### ขนาดภาพ

หากต้องการปรับขนาดผลลัพธ์ ให้ค้นหาโหนด **Empty Latent Image** และแก้ไข **width** และ **height** รักษาขนาดไม่เกิน 1024 พิกเซลในด้านที่ยาวที่สุดเพื่อคุณภาพที่ดีที่สุด

### ModelSamplingAuraFlow

โหนด **ModelSamplingAuraFlow** คือตัวปรับแต่งการ sampling เฉพาะทางที่ปรับวิธีที่กระบวนการ diffusion จัดการกับการกำหนดตารางเวลา noise คุณจะเห็นโหนดนี้เชื่อมต่อกับเอาต์พุตของโมเดลใน workflow Z-Image Turbo

| พารามิเตอร์ | สิ่งที่ควบคุม | ค่าที่แนะนำ |
|-----------|------------------|-------------------|
| **shift** | ปรับเวลาของตารางเวลา noise—ค่าที่สูงกว่าจะผลักการปรับแต่งรายละเอียดไปยังขั้นตอนหลัง | 1.0–4.0 (ค่าเริ่มต้นคือ 3.0) |

เมื่อใดควรปรับ **shift**:

- **ค่าต่ำ (1.0–2.0)**: การบรรจบกันเร็วขึ้น เหมาะสำหรับ composition ที่เรียบง่าย
- **ค่าสูง (3.0–4.0)**: การปรับแต่งที่ค่อยเป็นค่อยไปมากขึ้น สามารถปรับปรุงรายละเอียดในฉากที่ซับซ้อน

วิธีการ sampling แบบ AuraFlow ได้รับการออกแบบมาเฉพาะสำหรับโมเดล flow-matching อย่าง Z-Image Turbo เพื่อให้มั่นใจว่ามีการกระจาย noise ที่เหมาะสมตลอดกระบวนการสร้าง

## การทำงานกับ Workflow

### การบันทึก Workflow

คลิกปุ่ม **Save** ในเมนูเพื่อส่งออก workflow ของคุณเป็นไฟล์ JSON ซึ่งจะบันทึก:

- โหนดทั้งหมดและพารามิเตอร์ของโหนด
- การเชื่อมต่อทั้งหมดระหว่างโหนด
- ข้อความ prompt ปัจจุบัน

### การโหลด Workflow

ลากไฟล์ JSON ของ workflow ไปวางบน canvas หรือใช้ **Load** จากเมนู workflow Z-Image Turbo ที่คุณเห็นตามค่าเริ่มต้นจะถูกโหลดจากไฟล์ workflow ที่บันทึกไว้

### การแชร์ Workflow

Workflow เป็นแบบ self-contained—แชร์ไฟล์ JSON กับเพื่อนร่วมงาน และพวกเขาสามารถทำซ้ำการตั้งค่าของคุณได้อย่างแม่นยำ ทำให้ ComfyUI เหมาะสำหรับการทดลองร่วมกัน

## ขั้นตอนถัดไป

- **สำรวจโหนด LoRA**: ใช้อะแดปเตอร์สไตล์หรือหัวข้อโดยไม่ต้องฝึกใหม่
- **เพิ่ม negative prompt**: เชื่อมต่อโหนด CLIP Text Encode ที่สองกับอินพุต **negative** conditioning ของ KSampler เพื่อนำทางโมเดลให้หลีกเลี่ยงคุณลักษณะที่ไม่ต้องการ เช่น ความเบลอ สิ่งแปลกปลอม หรือลายน้ำ
- **สร้าง workflow แบบกำหนดเอง**: เชื่อมต่อการสร้างหลายรายการ เพิ่มการ upscaling หรือสร้างภาพแบบต่างๆ
- **เรียกดู workflow ของชุมชน**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) มี workflow พร้อมใช้งานมากมาย

จุดแข็งของ ComfyUI คือการทดลอง: เชื่อมต่อโหนดในรูปแบบต่างๆ ปรับพารามิเตอร์ และสังเกตว่าการเปลี่ยนแปลงแต่ละอย่างส่งผลต่อผลลัพธ์อย่างไร การสำรวจแบบลงมือปฏิบัตินี้จะสร้างความเข้าใจเชิงลึกเกี่ยวกับวิธีการทำงานของโมเดล diffusion

สำหรับข้อมูลเพิ่มเติม โปรดดูที่ [ComfyUI Documentation](https://docs.comfy.org/)