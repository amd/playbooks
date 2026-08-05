<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 개요

ComfyUI는 Stable Diffusion 및 기타 diffusion 모델을 위한 강력한 노드 기반 인터페이스입니다. 간단한 프롬프트 상자가 있는 기존의 텍스트-이미지 인터페이스와 달리, ComfyUI는 전체 이미지 생성 파이프라인을 시각적 그래프로 노출하여 텍스트 인코딩부터 잠재 공간 조작, 최종 디코딩에 이르기까지 모든 단계를 세밀하게 제어할 수 있게 해줍니다.

이 튜토리얼에서는 GPU에서 Z Image Turbo 모델과 함께 ComfyUI를 사용하여 고품질 AI 이미지를 생성하는 방법을 배웁니다.

## 배우게 될 내용

- ComfyUI를 실행하고 Z-Image Turbo 템플릿을 로드하는 방법
- Diffusion 파이프라인 구성 요소 이해하기
- 이미지 생성 및 생성 매개변수 조정하기
- 워크플로 저장 및 공유하기

## 메모리 구성 설정하기

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인하기

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치하기

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**사용자에게 GPU 장치 액세스 권한을 부여합니다** (적용되려면 로그아웃 후 다시 로그인해야 합니다):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### 가상 환경 생성하기
Linux에서는 원하는 디렉터리에서 터미널을 열고 다음 명령을 실행하여 venv를 생성합니다:

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


## ComfyUI 실행하기

<!-- @device:halo_box -->
<!-- @os:windows -->
Windows에서 ComfyUI를 실행하려면 바탕화면에 있는 ComfyUI Desktop Launcher를 클릭하세요. 단계에 따라 AMD용 로컬 버전을 설치하세요.

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

그런 다음 앱 상단 중앙에 있는 ComfyUI 버튼을 클릭합니다. 설정 탭이 열립니다. Storage 탭을 열고 사전 설치된 모델에 액세스할 수 있도록 경로가 다음과 같이 설정되어 있는지 확인하세요.

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
AMD Ryzen™ AI Halo에서는 ComfyUI가 추가적인 Python 설정이 필요 없는 사전 빌드된 컨테이너에서 실행됩니다.

Linux에서 ComfyUI를 실행하려면 작업 표시줄에 있는 ComfyUI 바로 가기를 클릭하세요. 브라우저 창에서 자동으로 열립니다.
>**팁**: ComfyUI와 모델은 `~/.local/share/ComfyUI/models`에 저장됩니다. 여기서 워크플로나 새 모델을 수동으로 추가할 수 있습니다.


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Windows에서 ComfyUI를 실행하려면 바탕화면에 있는 ComfyUI 바로 가기를 클릭하기만 하면 됩니다.
<!-- @os:end -->

<!-- @os:linux -->

ComfyUI를 실행하려면:

1. ComfyUI 디렉터리 내에 있는지 확인합니다. 
2. `python3 main.py --use-pytorch-cross-attention`을 실행합니다

ComfyUI는 로컬 웹 서버를 시작합니다. 인터페이스에 접속하려면 브라우저에서 `http://127.0.0.1:8188`을 여세요.

> **팁**: ComfyUI를 사용하는 동안 터미널 창을 열어 두세요. 창을 닫으면 서버가 중지됩니다.
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turbo 템플릿 찾기

이미지를 생성하기 전에 Z-Image Turbo 템플릿을 로드해야 합니다. 찾는 방법은 다음과 같습니다:

1. **화면 맨 왼쪽 가장자리를 확인하세요**—앱의 가장 왼쪽에 위에서 아래로 이어지는 세로 도구 모음이 있습니다.

2. **폴더 아이콘을 찾으세요**—해당 왼쪽 도구 모음에서 폴더처럼 생긴 아이콘을 찾습니다. 마우스를 올리면 "Templates"라는 레이블이 표시됩니다.

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **폴더 아이콘을 클릭하세요**—Templates 패널이 열립니다.

4. **"Z-Image Turbo"를 검색하세요**—검색창을 사용하거나 사용 가능한 템플릿을 스크롤하여 Z-Image Turbo Text To Image 워크플로를 찾은 다음 클릭하여 로드합니다.

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## 모델 다운로드하기

<!-- @require:comfyui-models -->

## 인터페이스 이해하기

Z-Image Turbo 템플릿이 로드되면 2개의 주요 노드가 있는 캔버스가 표시됩니다. 첫 번째 노드는 'Text to Image (Z-Image-Turbo)'이며, 두 번째 노드는 이미지를 확인하기 위한 것입니다. 

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Z-Image 노드에서 오른쪽 상단 버튼을 클릭하여 노드를 확장하고 서브그래프를 확인하세요.

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### 파이프라인 구성 요소

Z-Image Turbo 워크플로는 함께 작동하는 4가지 핵심 모델 구성 요소를 사용합니다:

| 구성 요소 | 역할 |
|-----------|------|
| **텍스트 인코더** (Qwen 3 4B) | 텍스트 프롬프트를 diffusion 모델이 이해하는 임베딩으로 변환합니다 |
| **Diffusion 모델** (Z-Image Turbo) | 잠재 표현을 반복적으로 노이즈 제거하여 이미지로 만드는 핵심 신경망입니다 |
| **VAE** (Variational Autoencoder) | 이미지를 잠재 공간과의 사이에서 인코딩/디코딩합니다 (최종 잠재값을 픽셀로 디코딩) |
| **LoRA** (선택 사항) | 기본 모델을 재학습하지 않고도 스타일이나 대상을 수정하는 경량 어댑터입니다 |

워크플로의 각 노드는 이러한 구성 요소 중 하나에 해당합니다. 데이터는 왼쪽에서 오른쪽으로 흐릅니다: 텍스트 → 임베딩 → 가이드 노이즈 제거 → 잠재값 → 최종 이미지.
## 첫 이미지 생성하기

Z-Image Turbo 모델이 이미 로드되어 있습니다. 이미지를 생성하려면:

1. 메인 Z-Image 노드에 **프롬프트를 입력**하세요. 최대한 구체적으로 작성하세요. 예시는 다음과 같습니다:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(선택 사항)**: 서브그래프 내의 다른 특정 설정을 확인하거나 조정하세요.
3. 오른쪽 상단의 파란색 **"Run Workflow"**를 클릭합니다(또는 `Ctrl+Enter`를 누릅니다).
4. 각 단계가 실행되면서 노드가 강조 표시되는 것을 확인하세요

전체 워크플로우 실행은 30초 이내에 완료됩니다. 생성된 이미지는 **Save Image** 노드에 표시되며 `output/` 폴더에 저장됩니다.

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


## 생성 매개변수 조정하기

### KSampler 설정

KSampler 노드는 핵심 확산(diffusion) 프로세스를 제어합니다:

| 매개변수 | 제어 대상 | Z-Image Turbo 권장값 |
|-----------|------------------|-------------------------------|
| **steps** | 노이즈 제거 반복 횟수 | 4–10 (turbo 모델은 더 적은 단계를 위해 증류됨) |
| **cfg** | 분류기 없는 가이던스 스케일—프롬프트를 얼마나 밀접하게 따를지 | 1.0–2.0 (turbo 모델은 매우 낮은 가이던스를 사용) |
| **sampler_name** | 노이즈 제거 알고리즘 | `euler`와 `res_multistep`이 turbo 모델에 적합함 |
| **scheduler** | 노이즈 스케줄 곡선 | `normal` 또는 `simple` |
| **seed** | 재현성을 위한 랜덤 시드 | 구성을 반복 작업하려면 고정값을 설정 |

### 이미지 크기

출력 크기를 조정하려면 **Empty Latent Image** 노드를 찾아 **width**와 **height**를 수정하세요. 최적의 품질을 위해 가장 긴 변의 크기를 1024픽셀 이하로 유지하세요.

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow** 노드는 확산 프로세스가 노이즈 스케줄링을 처리하는 방식을 조정하는 전용 샘플링 수정자입니다. Z-Image Turbo 워크플로우에서 이 노드가 모델 출력에 연결되어 있는 것을 확인할 수 있습니다.

| 매개변수 | 제어 대상 | 권장값 |
|-----------|------------------|-------------------|
| **shift** | 노이즈 스케줄 타이밍을 조정—값이 높을수록 더 많은 디테일 정제 작업이 후반 단계로 밀림 | 1.0–4.0 (기본값은 3.0) |

**shift**를 조정해야 할 때:

- **낮은 값(1.0–2.0)**: 더 빠른 수렴, 단순한 구성에 적합
- **높은 값(3.0–4.0)**: 더 점진적인 정제, 복잡한 장면에서 세부 디테일을 개선할 수 있음

AuraFlow 샘플링 방식은 Z-Image Turbo와 같은 흐름 매칭(flow-matching) 모델을 위해 특별히 설계되어, 생성 프로세스 전반에 걸쳐 적절한 노이즈 분포를 보장합니다.

## 워크플로우 다루기

### 워크플로우 저장하기

메뉴의 **Save** 버튼을 클릭하여 워크플로우를 JSON 파일로 내보냅니다. 여기에는 다음이 포함됩니다:

- 모든 노드와 해당 매개변수
- 노드 간의 모든 연결
- 현재 프롬프트 텍스트

### 워크플로우 불러오기

워크플로우 JSON 파일을 캔버스로 드래그하거나 메뉴의 **Load**를 사용하세요. 기본적으로 표시되는 Z-Image Turbo 워크플로우는 저장된 워크플로우 파일에서 로드된 것입니다.

### 워크플로우 공유하기

워크플로우는 자체적으로 완결되어 있습니다—JSON 파일을 동료와 공유하면 정확히 동일한 설정을 재현할 수 있습니다. 이 때문에 ComfyUI는 협업 실험에 매우 적합합니다.

## 다음 단계

- **LoRA 노드 살펴보기**: 재학습 없이 스타일 또는 대상 어댑터를 적용해보세요
- **네거티브 프롬프트 추가하기**: 두 번째 CLIP Text Encode 노드를 KSampler의 **negative** 컨디셔닝 입력에 연결하여 흐림, 아티팩트, 워터마크 등 원치 않는 요소를 피하도록 모델을 유도하세요
- **커스텀 워크플로우 구축하기**: 여러 생성 작업을 연결하거나, 업스케일링을 추가하거나, 이미지 변형을 만들어보세요
- **커뮤니티 워크플로우 둘러보기**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples)에는 바로 사용할 수 있는 다양한 워크플로우가 있습니다

ComfyUI의 강점은 실험입니다: 노드를 다르게 연결하고, 매개변수를 조정하고, 각 변경 사항이 결과물에 어떤 영향을 미치는지 관찰해보세요. 이러한 직접적인 탐구 과정을 통해 확산 모델의 작동 방식에 대한 직관을 기를 수 있습니다.

자세한 내용은 [ComfyUI Documentation](https://docs.comfy.org/)을 확인하세요.