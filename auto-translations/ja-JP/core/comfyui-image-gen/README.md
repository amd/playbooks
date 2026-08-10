<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

ComfyUI は、Stable Diffusion やその他の拡散モデル向けの強力なノードベースのインターフェースです。シンプルなプロンプトボックスを持つ従来のテキストから画像への変換インターフェースとは異なり、ComfyUI は画像生成パイプライン全体をビジュアルグラフとして公開し、テキストエンコーディングから潜在空間の操作、最終デコードに至るまで、あらゆるステップをきめ細かく制御できます。

このチュートリアルでは、GPU 上で ComfyUI と Z Image Turbo モデルを使用して、高品質な AI 画像を生成する方法を学びます。

## このチュートリアルで学ぶこと

- ComfyUI を起動し、Z-Image Turbo テンプレートを読み込む方法
- 拡散パイプラインのコンポーネントの理解
- 画像の生成と生成パラメータの調整
- ワークフローの保存と共有

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @os:windows -->
<!-- @require:driver,comfyui -->
<!-- @os:end -->

<!-- @os:linux -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ユーザーに GPU デバイスへのアクセス権を付与します**（有効にするには一度ログアウトして再度ログインしてください）:

```bash
sudo usermod -aG render,video $LOGNAME
```

#### 仮想環境の作成
Linux では、任意のディレクトリでターミナルを開き、以下のコマンドを実行して venv を作成します:

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


## ComfyUI の起動

<!-- @device:halo_box -->
<!-- @os:windows -->
Windows で ComfyUI を起動するには、デスクトップにある ComfyUI Desktop Launcher をクリックします。手順に従って、AMD 向けのローカルバージョンをインストールしてください。

<p align="center">
  <img src="assets/new_installer.png" alt="ComfyUI Desktop Launcher and Installer" width="600"/>
</p>

次に、アプリの上部中央にある ComfyUI ボタンをクリックします。これにより設定タブが開きます。Storage タブを開き、事前インストール済みのモデルにアクセスできるようにパスが以下のように設定されていることを確認してください。

<p align="center">
  <img src="assets/models_storage.png" alt="ComfyUI Desktop Menu Storage Tab" width="600"/>
</p>


<!-- @os:end -->

<!-- @os:linux -->
AMD Ryzen™ AI Halo では、ComfyUI は事前構築済みのコンテナ内で動作するため、追加の Python セットアップは不要です。

Linux で ComfyUI を起動するには、タスクバーの ComfyUI ショートカットをクリックします。ブラウザウィンドウが自動的に開きます。
>**ヒント**: ComfyUI とそのモデルは `~/.local/share/ComfyUI/models` に保存されています。ここで手動でワークフローや新しいモデルを追加できます。


<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
Windows で ComfyUI を起動するには、デスクトップの ComfyUI ショートカットをクリックするだけです。
<!-- @os:end -->

<!-- @os:linux -->

ComfyUI を起動するには:

1. ComfyUI ディレクトリ内にいることを確認します。
2. `python3 main.py --use-pytorch-cross-attention` を実行します

ComfyUI はローカル Web サーバーを起動します。ブラウザで `http://127.0.0.1:8188` を開いてインターフェースにアクセスしてください。

> **ヒント**: ComfyUI を使用している間は、ターミナルウィンドウを開いたままにしてください。閉じるとサーバーが停止します。
<!-- @os:end -->
<!-- @device:end -->


## Z-Image Turbo テンプレートを探す

画像を生成する前に、Z-Image Turbo テンプレートを読み込む必要があります。以下の手順で見つけてください:

1. **画面の左端を確認する**—アプリの最も左側に、上から下まで縦に並んだツールバーがあります。

2. **フォルダアイコンを探す**—その左側のツールバーの中に、フォルダのように見えるアイコンを探します。マウスを重ねると「Templates」というラベルが表示されます。

<p align="center">
  <img src="assets/templates.png" alt="Templates button in the left toolbar" width="600"/>
</p>

3. **フォルダアイコンをクリックする**—これにより Templates パネルが開きます。

4. **「Z-Image Turbo」を検索する**—検索バーを使用するか、利用可能なテンプレートをスクロールして Z-Image Turbo Text To Image ワークフローを見つけ、クリックして読み込みます。

<p align="center">
  <img src="assets/select-template.png" alt="Selecting the Z-Image Turbo template" width="600"/>
</p>

## モデルのダウンロード

<!-- @require:comfyui-models -->

## インターフェースを理解する

Z-Image Turbo テンプレートが読み込まれると、2 つの主要なノードを含むキャンバスが表示されます。1 つ目のノードは「Text to Image (Z-Image-Turbo)」と呼ばれ、2 つ目のノードは画像を表示するためのものです。

<p align="center">
  <img src="assets/zimagenode.png" alt="ComfyUI Main Node" width="600"/>
</p>


Z-Image ノードで、右上のボタンをクリックしてノードを展開し、サブグラフを確認します。

<p align="center">
  <img src="assets/subgraph_good.png" alt="ComfyUI Node Subgraph" width="600"/>
</p>

### パイプラインのコンポーネント

Z-Image Turbo ワークフローは、連携して動作する 4 つの主要なモデルコンポーネントを使用します:

| コンポーネント | 役割 |
|-----------|------|
| **テキストエンコーダー**（Qwen 3 4B） | テキストプロンプトを、拡散モデルが理解できる埋め込みに変換します |
| **拡散モデル**（Z-Image Turbo） | 潜在表現を反復的にノイズ除去して画像に変換する中核となるニューラルネットワークです |
| **VAE**（変分オートエンコーダー） | 画像と潜在空間の相互変換を行います（最終的な潜在表現をピクセルにデコードします） |
| **LoRA**（オプション） | ベースモデルを再学習することなく、スタイルや被写体を変更できる軽量なアダプターです |

ワークフロー内の各ノードは、これらのコンポーネントのいずれかに対応しています。データは左から右へ流れます: テキスト → 埋め込み → ガイド付きノイズ除去 → 潜在表現 → 最終画像。
## 初めての画像を生成する

Z-Image Turbo モデルはすでにロードされています。画像を生成するには:

1. メインの Z-Image ノードに**プロンプトを入力**します。できるだけ具体的に記述してください。以下は一例です:
   ```
   A photorealistic red fox sitting in a snowy forest clearing, 
   morning light filtering through pine trees, 
   detailed fur texture, bokeh background
   ```
2. **(任意)**: サブグラフ内の他の特定の設定を確認または調整します。
3. 右上隅の青い「**Run Workflow**」をクリックします(または `Ctrl+Enter` を押します)
4. 各ステップが実行される際にノードがハイライトされる様子を確認します

ワークフロー全体の実行は30秒未満で完了するはずです。生成された画像は **Save Image** ノードに表示され、`output/` フォルダに保存されます。

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

### KSampler の設定

KSampler ノードはコアとなる拡散処理を制御します:

| パラメータ | 制御内容 | Z-Image Turbo での推奨値 |
|-----------|------------------|-------------------------------|
| **steps** | ノイズ除去の反復回数 | 4〜10(turbo モデルは少ないステップ数向けに蒸留されています) |
| **cfg** | クラシファイアフリーガイダンススケール—プロンプトにどれだけ忠実に従うか | 1.0〜2.0(turbo モデルは非常に低いガイダンスを使用します) |
| **sampler_name** | ノイズ除去アルゴリズム | `euler` と `res_multistep` は turbo モデルに適しています |
| **scheduler** | ノイズスケジュールの曲線 | `normal` または `simple` |
| **seed** | 再現性のためのランダムシード | 構図を反復調整する場合は固定値を設定してください |

### 画像サイズ

出力の寸法を調整するには、**Empty Latent Image** ノードを見つけて **width** と **height** を変更します。最適な品質を得るため、最長辺は1024ピクセル以下に保ってください。

### ModelSamplingAuraFlow

**ModelSamplingAuraFlow** ノードは、拡散処理がノイズスケジューリングをどのように扱うかを調整する専用のサンプリング修飾子です。Z-Image Turbo ワークフローでは、このノードがモデル出力に接続されているのが確認できます。

| パラメータ | 制御内容 | 推奨値 |
|-----------|------------------|-------------------|
| **shift** | ノイズスケジュールのタイミングを調整します—値が高いほど、より多くの詳細の精緻化を後のステップに委ねます | 1.0〜4.0(デフォルトは3.0) |

**shift** を調整するタイミング:

- **低い値(1.0〜2.0)**: 収束が速く、シンプルな構図に適しています
- **高い値(3.0〜4.0)**: より段階的な精緻化が行われ、複雑なシーンの細部を改善できます

AuraFlow サンプリング手法は、Z-Image Turbo のようなフローマッチングモデル専用に設計されており、生成プロセス全体を通じて適切なノイズ分布を保証します。

## ワークフローを扱う

### ワークフローの保存

メニューの**保存**ボタンをクリックすると、ワークフローを JSON ファイルとしてエクスポートできます。これには以下が含まれます:

- すべてのノードとそのパラメータ
- ノード間のすべての接続
- 現在のプロンプトテキスト

### ワークフローの読み込み

ワークフロー JSON ファイルをキャンバス上にドラッグするか、メニューから**読み込み**を使用します。デフォルトで表示される Z-Image Turbo ワークフローは、保存済みのワークフローファイルから読み込まれたものです。

### ワークフローの共有

ワークフローは自己完結型です—JSON ファイルを同僚と共有すれば、彼らはあなたと全く同じセットアップを再現できます。これにより、ComfyUI は共同での実験に非常に適したツールとなります。

## 次のステップ

- **LoRA ノードを試す**: 再学習せずにスタイルや被写体のアダプターを適用できます
- **ネガティブプロンプトを追加する**: 2つ目の CLIP Text Encode ノードを KSampler の **negative** コンディショニング入力に接続し、ぼやけ、アーティファクト、透かしなどの望ましくない特徴をモデルが避けるように誘導します
- **カスタムワークフローを構築する**: 複数の生成をチェーンさせたり、アップスケーリングを追加したり、画像バリエーションを作成したりできます
- **コミュニティのワークフローを閲覧する**: [ComfyUI Examples](https://github.com/comfyanonymous/ComfyUI_examples) にはすぐに使えるワークフローが多数用意されています

ComfyUI の強みは実験にあります: ノードを異なる方法で接続し、パラメータを調整して、それぞれの変更が出力にどう影響するかを観察してください。この実践的な探求が、拡散モデルの仕組みに対する直感を養います。

詳細については、[ComfyUI ドキュメント](https://docs.comfy.org/) をご覧ください。