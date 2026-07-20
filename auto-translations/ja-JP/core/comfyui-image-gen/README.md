<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> このプレイブックは、GitHubではレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) にアクセスしてください。
<!-- @github-only:end -->

## 概要

ComfyUIは、Stable Diffusionやその他の拡散モデルのための強力なノードベースのインターフェースです。シンプルなプロンプトボックスを備えた従来のテキストから画像への変換インターフェースとは異なり、ComfyUIは画像生成パイプライン全体をビジュアルグラフとして公開し、テキストエンコーディングから潜在空間の操作、最終的なデコードまで、各ステップをきめ細かく制御できます。

このチュートリアルでは、GPU上でZ Image Turboモデルを使用してComfyUIを利用し、高品質なAI画像を生成する方法を学びます。

## 学習内容

- ComfyUIを起動し、Z-Image Turboテンプレートを読み込む方法
- 拡散パイプラインのコンポーネントを理解する
- 画像を生成し、生成パラメータを調整する
- ワークフローを保存・共有する

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ユーザーにGPUデバイスへのアクセス権限を付与します**（有効にするには、一度ログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

#### 仮想環境の作成
Linuxでは、任意のディレクトリでターミナルを開き、以下のプロンプトを実行してvenvを作成します：

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


## ComfyUIの起動

<!-- @device:halo_box -->
<!-- @os:windows -->
Windows上でComfyUIを起動するには、デスクトップにあるComfyUI Desktop Launcherをクリックします。手順に従って、AMD向けのローカルバージョンをインストールしてください。

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

次に、アプリ上部中央にあるComfyUIボタンをクリックします。これにより設定タブが開きます。Storageタブを開き、事前インストール済みのモデルにアクセスできるように、パスが以下のように設定されていることを確認してください。

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
Linux上でComfyUIを起動するには、タスクバーにあるComfyUIのショートカットをクリックします。ブラウザウィンドウで自動的に開くはずです。
>**ヒント**：ComfyUIとそのモデルは `~/.local/share/ComfyUI/models` に保存されています。ここから手動でワークフローや新しいモデルを追加できます。


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Windows上でComfyUIを起動するには、デスクトップにあるComfyUIのショートカットをクリックするだけです。
<!-- @os:end -->

<!-- @os:linux -->

ComfyUIを起動するには：

1. ComfyUIディレクトリ内にいることを確認します。
2. `python3 main.py --use-pytorch-cross-attention` を実行します

ComfyUIはローカルWebサーバーを起動します。ブラウザで `http://127.0.0.1:8188` を開いてインターフェースにアクセスしてください。

> **ヒント**：ComfyUIを使用している間は、ターミナルウィンドウを開いたままにしてください。閉じるとサーバーが停止します。
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turboテンプレートの検索

画像を生成する前に、Z-Image Turboテンプレートを読み込む必要があります。見つけ方は次のとおりです：

1. **画面の一番左端を見ます**—アプリの一番左側に、上から下まで伸びる縦型のツールバーがあります。

2. **フォルダアイコンを見つけます**—その左側のツールバー内で、フォルダのように見えるアイコンを探します。マウスをホバーすると「Templates」というラベルが表示されます。

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **フォルダアイコンをクリックします**—これによりTemplatesパネルが開きます。

4. **「Z-Image Turbo」を検索します**—検索バーを使用するか、利用可能なテンプレートをスクロールしてZ-Image Turbo Text To Imageワークフローを見つけ、クリックして読み込みます。

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## モデルのダウンロード

<!-- @require:comfyui-models -->

## インターフェースの理解

Z-Image Turboテンプレートが読み込まれると、キャンバス上に2つの主要なノードが表示されます。最初のノードは「Text to Image (Z-Image-Turbo)」と呼ばれ、2番目のノードは画像を表示するためのものです。

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Z-Imageノードで、右上のボタンをクリックしてノードを展開し、サブグラフを表示します。

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### パイプラインのコンポーネント

Z-Image Turboワークフローは、連携して動作する4つの主要なモデルコンポーネントを使用します：

| コンポーネント | 役割 |
|-----------|------|
| **Text Encoder**（Qwen 3 4B） | テキストプロンプトを拡散モデルが理解できる埋め込みに変換します |
| **Diffusion Model**（Z-Image Turbo） | 潜在表現を反復的にノイズ除去して画像へと変換する中核となるニューラルネットワークです |
| **VAE**（変分オートエンコーダー） | 画像を潜在空間との間でエンコード／デコードします（最終的な潜在表現をピクセルにデコードします） |
| **LoRA**（任意） | ベースモデルを再学習することなく、スタイルや被写体を変更する軽量なアダプターです |

ワークフロー内の各ノードは、これらのコンポーネントのいずれかに対応しています。データは左から右へ流れます：テキスト → 埋め込み → ガイド付きノイズ除去 → 潜在表現 → 最終画像。

## 最初の画像を生成する

Z-Image Turboモデルはすでに読み込まれています。画像を生成するには：

1. メインのZ-Imageノードに**プロンプトを入力**します。具体的に記述してください。例を以下に示します：
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **（任意）**：サブグラフ内の他の特定の設定を確認または調整します。
3. 右上隅にある**青い「Run Workflow」ボタンをクリック**します（または `Ctrl+Enter` を押します）
4. 各ステップが実行されるにつれて、ノードがハイライトされる様子を確認します

ワークフロー全体の実行は30秒未満で完了するはずです。生成された画像は**Save Image**ノードに表示され、`output/` フォルダに保存されます。

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


## 生成パラメータの調整
### KSamplerの設定

KSamplerノードは、コアとなる拡散プロセスを制御します。

| パラメータ | 制御する内容 | Z-Image Turboでの推奨値 |
|-----------|------------------|-------------------------------|
| **steps** | ノイズ除去反復の回数 | 4〜10(ターボモデルはステップ数を減らすように蒸留されています) |
| **cfg** | クラシファイアフリーガイダンススケール—プロンプトにどれだけ忠実に従うか | 1.0〜2.0(ターボモデルは非常に低いガイダンスを使用します) |
| **sampler_name** | ノイズ除去アルゴリズム | ターボモデルには`euler`および`res_multistep`が適しています |
| **scheduler** | ノイズスケジュールカーブ | `normal`または`simple` |
| **seed** | 再現性のためのランダムシード | 構図を反復する場合は固定値を設定してください |

### 画像サイズ

出力寸法を調整するには、**Empty Latent Image**ノードを見つけて、**width**と**height**を変更してください。最適な品質を得るには、最長辺を1024ピクセル以下に保ってください。

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow**ノードは、拡散プロセスがノイズスケジューリングをどのように処理するかを調整する特殊なサンプリング修飾子です。Z-Image Turboワークフローでは、このノードがモデル出力に接続されているのが見られます。

| パラメータ | 制御する内容 | 推奨値 |
|-----------|------------------|-------------------|
| **shift** | ノイズスケジュールのタイミングを調整—値が高いほど、より多くのディテール改善が後のステップに送られます | 1.0〜4.0(デフォルトは3.0) |

**shift**を調整するタイミング:

- **低い値(1.0〜2.0)**: より速い収束、シンプルな構図に適しています
- **高い値(3.0〜4.0)**: より緩やかな改善、複雑なシーンで細部を改善できる場合があります

AuraFlowサンプリング方式は、Z-Image Turboのようなフローマッチングモデル専用に設計されており、生成プロセス全体を通じて適切なノイズ分布を保証します。

## ワークフローを扱う

### ワークフローの保存

メニューの**Save**ボタンをクリックして、ワークフローをJSONファイルとしてエクスポートします。これには以下が含まれます。

- すべてのノードとそのパラメータ
- ノード間のすべての接続
- 現在のプロンプトテキスト

### ワークフローの読み込み

ワークフローのJSONファイルをキャンバスにドラッグするか、メニューから**Load**を使用してください。デフォルトで表示されるZ-Image Turboワークフローは、保存されたワークフローファイルから読み込まれています。

### ワークフローの共有

ワークフローは自己完結型です—JSONファイルを同僚と共有すれば、あなたの正確な設定を再現できます。これにより、ComfyUIは共同での実験に非常に適したものとなっています。

## 次のステップ

- **LoRAノードを試す**: 再トレーニングなしでスタイルまたは被写体のアダプターを適用する
- **ネガティブプロンプトを追加する**: 2つ目のCLIP Text EncodeノードをKSamplerの**negative**コンディショニング入力に接続し、ぼやけ、アーティファクト、透かしなどの望ましくない特徴からモデルを遠ざけるように誘導する
- **カスタムワークフローを構築する**: 複数の生成を連結したり、アップスケーリングを追加したり、画像のバリエーションを作成したりする
- **コミュニティのワークフローを閲覧する**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples)には、すぐに使えるワークフローが多数用意されています

ComfyUIの強みは実験にあります。ノードを異なる方法で接続し、パラメータを調整し、それぞれの変更が出力にどのように影響するかを観察してください。この実践的な探求により、拡散モデルがどのように機能するかについての直感が養われます。

詳細については、[ComfyUI Documentation](https://docs.comfy.org/)をご覧ください。