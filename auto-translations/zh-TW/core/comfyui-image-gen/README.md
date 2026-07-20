<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> 此手冊使用 GitHub 無法呈現的特殊標籤。請造訪 [amd.com/playbooks](https://amd.com/playbooks) 以正確預覽此內容。
<!-- @github-only:end -->

## 概觀

ComfyUI 是一個功能強大、以節點為基礎的介面,適用於 Stable Diffusion 及其他擴散模型。與傳統只有簡單提示框的文字轉圖片介面不同,ComfyUI 將整個影像生成流程以視覺化圖形呈現,讓你能夠對從文字編碼、潛在空間操作到最終解碼的每個步驟進行精細控制。

本教學將教你如何在 GPU 上使用 ComfyUI 搭配 Z Image Turbo 模型,以產生高品質的 AI 影像。

## 你將學到什麼

- 如何啟動 ComfyUI 並載入 Z-Image Turbo 範本
- 了解擴散管線的各個組成部分
- 產生影像並調整生成參數
- 儲存與分享工作流程

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予你的使用者存取 GPU 裝置的權限**(需登出並重新登入才能生效):

```bash
sudo usermod -aG render,video $LOGNAME
```

#### 建立虛擬環境
在 Linux 上,於你選擇的目錄中開啟終端機,並執行以下指令來建立 venv:

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


## 啟動 ComfyUI

<!-- @device:halo_box -->
<!-- @os:windows -->
要在 Windows 上啟動 ComfyUI,請點選桌面上的 ComfyUI Desktop Launcher。依照步驟安裝支援 AMD 的本機版本。

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

接著,點選應用程式頂部中間的 ComfyUI 按鈕。這會開啟一個設定分頁。開啟 Storage 分頁,並確認路徑設定如下,以存取預先安裝的模型。

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
要在 Linux 上啟動 ComfyUI,請點選工作列中的 ComfyUI 捷徑。它應該會自動在瀏覽器視窗中開啟。
>**提示**:ComfyUI 及其模型儲存在 `~/.local/share/ComfyUI/models`。你可以在此處手動新增工作流程或新模型。


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
要在 Windows 上啟動 ComfyUI,只需點選桌面上的 ComfyUI 捷徑。
<!-- @os:end -->

<!-- @os:linux -->

要啟動 ComfyUI:

1. 確認你目前位於 ComfyUI 目錄中。
2. 執行 `python3 main.py --use-pytorch-cross-attention`

ComfyUI 會啟動本機網頁伺服器。開啟瀏覽器並前往 `http://127.0.0.1:8188` 以存取介面。

> **提示**:使用 ComfyUI 時請保持終端機視窗開啟。關閉它將停止伺服器。
<!-- @os:end -->
<!-- @device:end -->


## 尋找 Z-Image Turbo 範本

在生成影像之前,你需要先載入 Z-Image Turbo 範本。以下是尋找方式:

1. **查看畫面最左側邊緣**——應用程式最左側有一條由上到下延伸的垂直工具列。

2. **找到資料夾圖示**——在左側工具列中,尋找看起來像資料夾的圖示。將滑鼠懸停於其上時,會顯示「Templates」標籤。

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **點選資料夾圖示**——這會開啟 Templates 面板。

4. **搜尋「Z-Image Turbo」**——使用搜尋列或捲動瀏覽可用範本,找到 Z-Image Turbo Text To Image 工作流程,然後點選以載入。

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## 下載模型

<!-- @require:comfyui-models -->

## 了解介面

當 Z-Image Turbo 範本載入後,你會看到畫布上有 2 個主要節點。第一個節點稱為「Text to Image (Z-Image-Turbo)」,第二個節點用於檢視影像。

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


在 Z-Image 節點上,點選右上角的按鈕以展開節點並查看子圖。

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### 管線組成

Z-Image Turbo 工作流程使用四個關鍵模型元件協同運作:

| 元件 | 角色 |
|-----------|------|
| **文字編碼器**(Qwen 3 4B) | 將你的文字提示轉換為擴散模型能理解的嵌入向量 |
| **擴散模型**(Z-Image Turbo) | 核心神經網路,透過反覆去噪將潛在表示轉換為影像 |
| **VAE**(變分自動編碼器) | 在潛在空間與影像之間進行編碼/解碼(將最終潛在向量解碼為像素) |
| **LoRA**(選用) | 輕量級轉接器,可在不重新訓練基礎模型的情況下修改風格或主體 |

工作流程中的每個節點都對應其中一個元件。資料由左至右流動:文字 → 嵌入向量 → 引導式去噪 → 潛在向量 → 最終影像。

## 生成你的第一張影像

Z-Image Turbo 模型已經載入完成。要生成影像:

1. **在主要 Z-Image 節點中輸入你的提示**。請盡量描述詳細。以下是一個範例:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(選用)**:確認或微調子圖中的其他特定設定。
3. **點選右上角的藍色「Run Workflow」**(或按下 `Ctrl+Enter`)
4. 觀察每個步驟執行時節點的高亮顯示

整個工作流程的執行應該會在 30 秒內完成。生成的影像會顯示在 **Save Image** 節點中,並儲存至 `output/` 資料夾。

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


## 調整生成參數
### KSampler 設定

KSampler 節點控制核心擴散流程：

| 參數 | 控制內容 | Z-Image Turbo 建議值 |
|-----------|------------------|-------------------------------|
| **steps** | 去噪迭代次數 | 4–10（turbo 模型經過蒸餾，適合較少步數） |
| **cfg** | 無分類器引導比例——依循提示詞的緊密程度 | 1.0–2.0（turbo 模型使用非常低的引導值） |
| **sampler_name** | 去噪演算法 | `euler` 與 `res_multistep` 對 turbo 模型效果良好 |
| **scheduler** | 噪聲排程曲線 | `normal` 或 `simple` |
| **seed** | 用於可重現性的隨機種子 | 設定固定值以反覆調整構圖 |

### 圖像尺寸

若要調整輸出尺寸，請找到 **Empty Latent Image** 節點並修改 **width** 與 **height**。請將最長邊維持在 1024 像素以內以取得最佳品質。

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow** 節點是一個專門的取樣修飾器，用於調整擴散流程處理噪聲排程的方式。在 Z-Image Turbo 工作流程中，您會看到此節點連接到模型輸出。

| 參數 | 控制內容 | 建議值 |
|-----------|------------------|-------------------|
| **shift** | 調整噪聲排程時機——數值越高，會將更多細節精修推移到後段步驟 | 1.0–4.0（預設為 3.0） |

何時調整 **shift**：

- **較低值（1.0–2.0）**：收斂較快，適合簡單構圖
- **較高值（3.0–4.0）**：漸進式精修更平滑，可改善複雜場景中的細節

AuraFlow 取樣方法專為 Z-Image Turbo 等流匹配（flow-matching）模型設計，可確保整個生成過程中噪聲分佈得當。

## 使用工作流程

### 儲存工作流程

點選選單中的 **Save** 按鈕，將您的工作流程匯出為 JSON 檔案。這會保存：

- 所有節點及其參數
- 節點之間的所有連接
- 目前的提示詞文字

### 載入工作流程

將工作流程 JSON 檔案拖曳到畫布上，或從選單中使用 **Load**。您預設看到的 Z-Image Turbo 工作流程即是從已儲存的工作流程檔案載入的。

### 分享工作流程

工作流程是自成一體的——與同事分享 JSON 檔案，他們便能重現您完全相同的設定。這使得 ComfyUI 非常適合協作實驗。

## 後續步驟

- **探索 LoRA 節點**：無需重新訓練即可套用風格或主題適配器
- **加入負面提示詞**：將第二個 CLIP Text Encode 節點連接到 KSampler 的 **negative** 條件輸入，引導模型避開模糊、瑕疵或浮水印等不想要的特徵
- **建立自訂工作流程**：串連多次生成、加入放大處理，或建立圖像變化版本
- **瀏覽社群工作流程**：[ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) 提供許多現成可用的工作流程

ComfyUI 的強項在於實驗：以不同方式連接節點、調整參數，並觀察每項變更如何影響輸出結果。這種親手實作的探索方式能培養對擴散模型運作原理的直覺理解。

如需更多資訊，請參閱 [ComfyUI Documentation](https://docs.comfy.org/)。