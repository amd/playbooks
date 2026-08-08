<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

ComfyUI เป็นอินเทอร์เฟซแบบโหนดที่ทรงพลังสำหรับ Stable Diffusion และโมเดล diffusion อื่น ๆ ต่างจากอินเทอร์เฟซแบบ text-to-image ทั่วไปที่มีเพียงกล่องข้อความสำหรับป้อนพรอมต์ ComfyUI เปิดเผยไปป์ไลน์การสร้างภาพทั้งหมดในรูปแบบกราฟภาพ ทำให้คุณสามารถควบคุมทุกขั้นตอนได้อย่างละเอียด ตั้งแต่การเข้ารหัสข้อความ ไปจนถึงการจัดการ latent space และการถอดรหัสเป็นภาพสุดท้าย

บทเรียนนี้จะสอนวิธีการใช้งาน ComfyUI ร่วมกับโมเดล Z Image Turbo บน GPU ของคุณ เพื่อสร้างภาพ AI คุณภาพสูง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีเปิดใช้งาน ComfyUI และโหลดเทมเพลต Z-Image Turbo
- ทำความเข้าใจส่วนประกอบของไปป์ไลน์ diffusion
- การสร้างภาพและการปรับแต่งพารามิเตอร์การสร้างภาพ
- การบันทึกและแชร์เวิร์กโฟลว์

## การตั้งค่าหน่วยความจำ

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
**ให้สิทธิ์ผู้ใช้ของคุณในการเข้าถึงอุปกรณ์ GPU** (ต้องออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)
บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วรันคำสั่งต่อไปนี้เพื่อสร้าง venv:

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


## การเปิดใช้งาน ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
ในการเปิดใช้งาน ComfyUI บน Windows ให้คลิกที่ ComfyUI Desktop Launcher ซึ่งอยู่บนเดสก์ท็อปของคุณ จากนั้นทำตามขั้นตอนเพื่อติดตั้งเวอร์ชันภายในเครื่องร่วมกับ AMD

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

จากนั้น คลิกปุ่ม ComfyUI ที่อยู่ตรงกลางด้านบนของแอป ซึ่งจะเปิดแท็บการตั้งค่าขึ้นมา เปิดแท็บ Storage และตรวจสอบให้แน่ใจว่าเส้นทาง (paths) ถูกตั้งค่าไว้ดังนี้เพื่อเข้าถึงโมเดลที่ติดตั้งไว้ล่วงหน้า

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
บน AMD Ryzen™ AI Halo ComfyUI จะทำงานในคอนเทนเนอร์ที่สร้างไว้ล่วงหน้า ซึ่งไม่จำเป็นต้องตั้งค่า Python เพิ่มเติมแต่อย่างใด

ในการเปิดใช้งาน ComfyUI บน Linux ให้คลิกที่ทางลัด ComfyUI ในทาสก์บาร์ โปรแกรมจะเปิดขึ้นเองในหน้าต่างเบราว์เซอร์
>**เคล็ดลับ**: ComfyUI และโมเดลของมันถูกจัดเก็บไว้ที่ `~/.local/share/ComfyUI/models` นี่คือตำแหน่งที่คุณสามารถเพิ่มเวิร์กโฟลว์หรือโมเดลใหม่ด้วยตนเองได้


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
ในการเปิดใช้งาน ComfyUI บน Windows เพียงคลิกที่ทางลัด ComfyUI บนเดสก์ท็อปของคุณ
<!-- @os:end -->

<!-- @os:linux -->

ในการเปิดใช้งาน ComfyUI:

1. ตรวจสอบให้แน่ใจว่าคุณอยู่ในไดเรกทอรี ComfyUI 
2. รันคำสั่ง `python3 main.py --use-pytorch-cross-attention`

ComfyUI จะเริ่มเซิร์ฟเวอร์เว็บภายในเครื่อง เปิดเบราว์เซอร์ของคุณไปที่ `http://127.0.0.1:8188` เพื่อเข้าถึงอินเทอร์เฟซ

> **เคล็ดลับ**: เปิดหน้าต่างเทอร์มินัลค้างไว้ในขณะที่ใช้งาน ComfyUI หากปิดหน้าต่างนี้ เซิร์ฟเวอร์จะหยุดทำงาน
<!-- @os:end -->
<!-- @device:end -->


## การค้นหาเทมเพลต Z-Image Turbo

ก่อนที่จะสร้างภาพ คุณจำเป็นต้องโหลดเทมเพลต Z-Image Turbo ก่อน วิธีค้นหามีดังนี้:

1. **มองไปที่ขอบซ้ายสุดของหน้าจอ**—จะมีแถบเครื่องมือแนวตั้งพาดจากด้านบนลงล่างอยู่ที่ด้านซ้ายสุดของแอป

2. **หาไอคอนรูปโฟลเดอร์**—ในแถบเครื่องมือด้านซ้ายนั้น ให้มองหาไอคอนที่มีลักษณะคล้ายโฟลเดอร์ เมื่อคุณเลื่อนเมาส์ไปวางไว้ จะปรากฏข้อความว่า "Templates"

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **คลิกที่ไอคอนโฟลเดอร์**—จะเปิดแผงเทมเพลตขึ้นมา

4. **ค้นหา "Z-Image Turbo"**—ใช้แถบค้นหาหรือเลื่อนดูรายการเทมเพลตที่มีอยู่ เพื่อหาเวิร์กโฟลว์ Z-Image Turbo Text To Image จากนั้นคลิกเพื่อโหลด

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## การดาวน์โหลดโมเดล

<!-- @require:comfyui-models -->

## ทำความเข้าใจอินเทอร์เฟซ

เมื่อเทมเพลต Z-Image Turbo โหลดขึ้นมา คุณจะเห็นแคนวาสที่มีโหนดหลัก 2 โหนด โหนดแรกชื่อว่า 'Text to Image (Z-Image-Turbo)' และโหนดที่สองใช้สำหรับดูภาพ 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


บนโหนด Z-Image ให้คลิกปุ่มด้านขวาบนเพื่อขยายโหนดและดูซับกราฟ (subgraph)

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### ส่วนประกอบของไปป์ไลน์

เวิร์กโฟลว์ Z-Image Turbo ใช้ส่วนประกอบของโมเดลหลักสี่ส่วนที่ทำงานร่วมกัน:

| ส่วนประกอบ | บทบาท |
|-----------|------|
| **Text Encoder** (Qwen 3 4B) | แปลงพรอมต์ข้อความของคุณให้เป็น embeddings ที่โมเดล diffusion เข้าใจ |
| **Diffusion Model** (Z-Image Turbo) | โครงข่ายประสาทหลักที่ทำการลด noise แบบวนซ้ำ (iteratively denoise) จากการแทนค่า latent ให้กลายเป็นภาพ |
| **VAE** (Variational Autoencoder) | เข้ารหัสภาพเข้าและออกจาก latent space (ถอดรหัส latent สุดท้ายให้กลายเป็นพิกเซล) |
| **LoRA** (ตัวเลือกเสริม) | อะแดปเตอร์น้ำหนักเบาที่ปรับเปลี่ยนสไตล์หรือหัวข้อโดยไม่ต้องฝึกโมเดลพื้นฐานใหม่ |

แต่ละโหนดในเวิร์กโฟลว์สอดคล้องกับส่วนประกอบเหล่านี้อย่างใดอย่างหนึ่ง ข้อมูลจะไหลจากซ้ายไปขวา: ข้อความ → embeddings → การลด noise แบบมีทิศทาง → latents → ภาพสุดท้าย
## การสร้างภาพแรกของคุณ

โมเดล Z-Image Turbo ถูกโหลดไว้เรียบร้อยแล้ว หากต้องการสร้างภาพ:

1. **ป้อนพรอมต์ของคุณ** ใน Z-Image Node หลัก ควรอธิบายให้ละเอียด ตัวอย่างเช่น:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(ไม่บังคับ)**: ยืนยันหรือปรับแต่งการตั้งค่าเฉพาะอื่น ๆ ภายใน subgraph
3. **คลิกปุ่มสีน้ำเงิน "Run Workflow"** ที่มุมขวา (หรือกด `Ctrl+Enter`)
4. สังเกตโหนดที่ไฮไลต์ขึ้นขณะที่แต่ละขั้นตอนทำงาน

การทำงานของ workflow ทั้งหมดควรเสร็จสิ้นภายในเวลาไม่ถึง 30 วินาที ภาพที่สร้างขึ้นของคุณจะปรากฏใน node **Save Image** และถูกบันทึกไว้ในโฟลเดอร์ `output/`

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


## การปรับพารามิเตอร์การสร้างภาพ

### การตั้งค่า KSampler

โหนด KSampler ควบคุมกระบวนการ diffusion หลัก:

| พารามิเตอร์ | สิ่งที่ควบคุม | ค่าที่แนะนำสำหรับ Z-Image Turbo |
|-----------|------------------|-------------------------------|
| **steps** | จำนวนรอบการทำ denoising | 4–10 (โมเดล turbo ถูก distill มาให้ใช้ step น้อยลง) |
| **cfg** | Classifier-free guidance scale—ความใกล้เคียงในการทำตามพรอมต์ | 1.0–2.0 (โมเดล turbo ใช้ guidance ที่ต่ำมาก) |
| **sampler_name** | อัลกอริทึม denoising | `euler` และ `res_multistep` ทำงานได้ดีกับโมเดล turbo |
| **scheduler** | เส้นโค้งของ noise schedule | `normal` หรือ `simple` |
| **seed** | ค่า seed แบบสุ่มสำหรับความสามารถในการทำซ้ำ | ตั้งค่าคงที่เพื่อทำการปรับแต่งองค์ประกอบของภาพซ้ำ ๆ |

### ขนาดภาพ

หากต้องการปรับขนาดของผลลัพธ์ ให้ไปที่โหนด **Empty Latent Image** แล้วแก้ไข **width** และ **height** ควรกำหนดขนาดให้อยู่ที่หรือต่ำกว่า 1024 พิกเซลในด้านที่ยาวที่สุด เพื่อคุณภาพที่ดีที่สุด

### ModelSamplingAuraFlow

โหนด **ModelSamplingAuraFlow** เป็นตัวปรับแต่งการสุ่มตัวอย่างเฉพาะทาง ที่ปรับวิธีที่กระบวนการ diffusion จัดการกับ noise scheduling คุณจะเห็นโหนดนี้เชื่อมต่อกับเอาต์พุตของโมเดลใน workflow ของ Z-Image Turbo

| พารามิเตอร์ | สิ่งที่ควบคุม | ค่าที่แนะนำ |
|-----------|------------------|-------------------|
| **shift** | ปรับจังหวะเวลาของ noise schedule—ค่าที่สูงขึ้นจะผลักการปรับแต่งรายละเอียดไปยัง step หลัง ๆ มากขึ้น | 1.0–4.0 (ค่าเริ่มต้นคือ 3.0) |

เมื่อใดควรปรับ **shift**:

- **ค่าต่ำ (1.0–2.0)**: บรรจบเร็วขึ้น เหมาะสำหรับองค์ประกอบภาพที่เรียบง่าย
- **ค่าสูง (3.0–4.0)**: การปรับแต่งที่ค่อยเป็นค่อยไปมากขึ้น สามารถปรับปรุงรายละเอียดปลีกย่อยในฉากที่ซับซ้อนได้

วิธีการสุ่มตัวอย่างแบบ AuraFlow ถูกออกแบบมาโดยเฉพาะสำหรับโมเดลประเภท flow-matching อย่าง Z-Image Turbo เพื่อให้มั่นใจได้ถึงการกระจายตัวของ noise ที่เหมาะสมตลอดกระบวนการสร้างภาพ

## การทำงานกับ Workflows

### การบันทึก Workflows

คลิกปุ่ม **Save** ในเมนูเพื่อส่งออก workflow ของคุณเป็นไฟล์ JSON ซึ่งจะบันทึกข้อมูลต่อไปนี้ไว้:

- โหนดทั้งหมดและพารามิเตอร์ของโหนดเหล่านั้น
- การเชื่อมต่อทั้งหมดระหว่างโหนด
- ข้อความพรอมต์ปัจจุบัน

### การโหลด Workflows

ลากไฟล์ workflow JSON มาวางบนแคนวาส หรือใช้ **Load** จากเมนู workflow ของ Z-Image Turbo ที่คุณเห็นเป็นค่าเริ่มต้นนั้นถูกโหลดมาจากไฟล์ workflow ที่บันทึกไว้

### การแชร์ Workflows

Workflows เป็นไฟล์แบบครบในตัวเอง—สามารถแชร์ไฟล์ JSON กับเพื่อนร่วมงาน และพวกเขาก็สามารถสร้างผลลัพธ์ตามการตั้งค่าเดียวกับคุณได้อย่างแม่นยำ ทำให้ ComfyUI เหมาะอย่างยิ่งสำหรับการทดลองร่วมกัน

## ขั้นตอนถัดไป

- **สำรวจโหนด LoRA**: นำ adapter ด้านสไตล์หรือหัวเรื่องมาใช้โดยไม่ต้องฝึกโมเดลใหม่
- **เพิ่ม negative prompt**: เชื่อมต่อโหนด CLIP Text Encode ตัวที่สองเข้ากับอินพุตแบบ conditioning **negative** ของ KSampler เพื่อชี้นำให้โมเดลหลีกเลี่ยงคุณลักษณะที่ไม่ต้องการ เช่น ความเบลอ สิ่งแปลกปลอม (artifacts) หรือลายน้ำ
- **สร้าง workflow ที่กำหนดเอง**: ต่อเชื่อมการสร้างภาพหลายรอบเข้าด้วยกัน เพิ่มการ upscale หรือสร้างภาพในรูปแบบต่าง ๆ
- **สำรวจ workflow จากคอมมูนิตี้**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) มี workflow พร้อมใช้งานมากมาย

จุดแข็งของ ComfyUI คือการทดลอง: ลองเชื่อมต่อโหนดในรูปแบบต่าง ๆ ปรับพารามิเตอร์ และสังเกตว่าการเปลี่ยนแปลงแต่ละอย่างส่งผลต่อผลลัพธ์อย่างไร การลงมือสำรวจด้วยตนเองแบบนี้จะช่วยสร้างความเข้าใจเชิงลึกเกี่ยวกับการทำงานของโมเดล diffusion

หากต้องการข้อมูลเพิ่มเติม โปรดดูที่ [เอกสาร ComfyUI](https://docs.comfy.org/)