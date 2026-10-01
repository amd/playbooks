<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

GPUカーネルをゼロから作成し、コンパイルして、AMD GPU上で起動し、使用率が跳ね上がる様子を観察します。このプレイブックでは、GPU計算が実際にどのように動作するかを示します。カーネルコードを記述し、それを数千のスレッドにわたって並列実行します。

> **注**: これはかなり複雑なプレイブックであり、追加のデバッグや修正が必要になる場合があります。

## 学習内容

<!-- @os:windows -->
- GPUカーネルの仕組み: グリッド、ブロック、スレッド、そしてそれらをデータにマッピングするインデックスモデル
- AMD ROCm/HIPスタックが、変更なしでAMD GPU上で動作するCUDAスタイルのコードをどのように実現するか
- `torch.cuda._compile_kernel` を使用してランタイムにカーネルをコンパイルする方法
- `CUDAExtension` + pybind11を使用して、Pythonからインポート可能なネイティブC++カーネル拡張をビルドする方法
<!-- @os:end -->
<!-- @os:linux -->
- GPUカーネルの仕組み: グリッド、ブロック、スレッド、そしてそれらをデータにマッピングするインデックスモデル
- AMD ROCm/HIPスタックが、変更なしでAMD GPU上で動作するCUDAスタイルのコードをどのように実現するか
- `torch.cuda._compile_kernel` を使用してランタイムにカーネルをコンパイルする方法
- `CUDAExtension` + pybind11を使用して、Pythonからインポート可能なネイティブC++カーネル拡張をビルドする方法
- カーネルの実行時間を測定し、`amd-smi` でリアルタイムのGPU使用率を監視する方法
<!-- @os:end -->

---

このプレイブックでは、カーネル開発の2つのアプローチを扱います。

<!-- @os:windows -->
| アプローチ | エントリポイント |
|---|---|
| **JITコンパイル** | `torch.cuda._compile_kernel`。カーネルをPython文字列として記述し、ビルドステップなし |
| **C++拡張** | `CUDAExtension` + pybind11: `.cu`ファイルをネイティブな`.pyd`にコンパイルし、インポートする |
<!-- @os:end -->
<!-- @os:linux -->
| アプローチ | エントリポイント |
|---|---|
| **JITコンパイル** | `torch.cuda._compile_kernel`。カーネルをPython文字列として記述し、ビルドステップなし |
| **C++拡張** | `CUDAExtension` + pybind11: `.cu`ファイルをネイティブな`.so`にコンパイルし、インポートする |
<!-- @os:end -->

どちらのアプローチもAMD GPU上で動作します。これは、PyTorchのROCmビルドがCUDA APIサーフェス全体をHIPにマッピングしているために可能となっています。つまり、`torch.cuda`、`CUDAExtension`、そしてCUDAカーネル構文はすべて、AMDハードウェア上で透過的に動作するということです。

---

## 背景

### GPUカーネルとは？

GPUカーネルとは、数千のGPUスレッドにわたって同時に並列実行される関数です。CPU関数が呼び出しごとに1回実行されるのとは異なり、カーネルは**ブロック**の**グリッド**とともに起動され、各ブロックには多数の**スレッド**が含まれ、すべてが異なるデータに対して同じコードを実行します。

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### スレッドインデックスモデル

カーネルを起動する際には、2つの次元を指定します。

| 変数 | 意味 |
|---|---|
| `gridDim` | グリッド内のブロック数 |
| `blockDim` | ブロックごとのスレッド数 |

各スレッドは、3つの組み込み読み取り専用変数にアクセスできます。

| 変数 | 意味 |
|---|---|
| `blockIdx.x` | このスレッドが属するブロック |
| `blockDim.x` | 1ブロック内のスレッド数 |
| `threadIdx.x` | ブロック内でのスレッドインデックス |

### グローバルスレッドID

これらの変数を組み合わせて、グローバルに一意なスレッドインデックスを計算します。

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

合計スレッド数 = `gridDim.x * blockDim.x`。各スレッドは1つの要素を独立して処理します。これが**データ並列性**の基礎です。同じ演算が、スレッド間の依存関係なしに、多数の要素に対して一度に実行されます。

---

### GPU実行モデル: ウェーブフロント

AMD GPUは、**ウェーブフロント**と呼ばれる**32**個のスレッドのグループでスレッドを実行します。ウェーブフロント内のすべてのスレッドは、同じ命令を同時に実行します。これは最適なブロックサイズの選択に影響します（256スレッド = 8ウェーブフロント = 良好なスケジューリング効率）。

### AMD GPUプログラミング: HIP + ROCm

**ROCm**は、AMDのオープンソースGPUコンピュートスタック（ドライバー、コンパイラー、ライブラリ、ランタイム）です。**HIP**はその上に位置し、構文的にCUDAと同一になるよう設計されています。PyTorchのROCmビルドは、`torch.cuda.*`を透過的にHIPにマッピングするため、同じコードがAMD GPU上でも動作します。

---

### PyTorch + AMD/HIP

PyTorchはROCmビルドを提供しており、CUDA APIサーフェス（`torch.cuda.*`）が透過的にHIPによってバックエンドされています。これは以下を意味します。

- `torch.cuda.is_available()` はROCmを搭載したAMD GPU上で動作する
- `tensor.to("cuda")` はAMD GPU上にメモリを割り当てる
- `torch.version.hip` がHIPバージョンを公開する

PyTorchはまた、`torch.cuda._compile_kernel()`を公開しており、これは生のカーネル文字列をJITコンパイルして呼び出し可能なオブジェクトを取得するための高レベルなショートカットで、別個のビルドステップを必要としません。

---

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 前提条件 - Windows
- 最新版をインストール: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
Linuxでは、任意のディレクトリでターミナルを開き、以下のコマンドに従って、ROCm+PyTorchがすでにインストールされた状態のvenvを作成します。
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env --system-site-packages
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPUデバイスへのアクセス権をユーザーに付与します**（これを有効にするには一度ログアウトして再度ログインする必要があります）。

```bash
sudo usermod -aG render,video $LOGNAME
```

Linuxでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windowsでは、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **ヒント**: 一部のPowerShellコマンドを実行する前に、Windowsユーザーはご自身のPowerShell実行ポリシーを変更する必要がある場合があります（例:
> RemoteSignedまたはUnrestrictedに設定する）。

<!-- @os:end -->


### 基本的な依存関係のインストール
<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:rocm,pytorch -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->

<!-- @device:halo_box -->
> **注:** このプレイブックでは、Ryzen AI Haloであっても、カスタムカーネルのコンパイルには完全な開発用ヘッダーが必要となるため、ROCmとPyTorchを仮想環境にインストールする必要があります。

ROCmをインストールします:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorchをインストールします:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```bash
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```powershell
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"
```
<!-- @test:end -->
<!-- @os:end -->
---
### 追加の依存関係のインストール

<!-- @os:linux -->
Linux C/C++ ビルドツールチェーンをインストールします。これはシステムレベルの依存関係であり、`CUDAExtension` が `.cu` ファイルからネイティブな `.so` モジュールをビルドするため、C++ 拡張機能のウォークスルーに必要です。

これを Linux マシン上で一度、作成した Python 仮想環境の外で実行します:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

`kernel-env` 仮想環境をアクティブ化した後、Python ビルドの依存関係をインストールします:
<!-- @test:id=install-deps timeout=60 setup=activate-venv -->
```bash
python -m pip install "setuptools<82" wheel ninja
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-linux-build-tools timeout=60 hidden=True -->
```bash
set -euo pipefail

command -v gcc
command -v g++
gcc --version
g++ --version

echo "OK: Linux C/C++ build toolchain is available."
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
[Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) または[それ以降のバージョン](https://visualstudio.microsoft.com/vs/community/)が **Desktop development with C++** ワークロード付きでインストールされていることを確認してください。

> **注**: この Visual Studio C++ 環境のセットアップは、**C++ 拡張機能**アプローチにのみ必要です。JIT コンパイルアプローチでは不要です。

PowerShell ターミナルを開き、C++ 拡張機能をビルドする前に次のコマンドを実行してください。

**手順1: インストール済みの Visual Studio C++ 環境を見つける**

**(A) Visual Studio Installer と共にインストールされる `vswhere.exe` を見つける**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) C++ ビルドツールを備えた Visual Studio 2022 以降から `vcvars64.bat` を見つける**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) 使用されている Visual Studio C++ 環境を表示する**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**手順2: Visual Studio C++ ビルド環境をアクティブ化する**

**(A) `vcvars64.bat` を実行し、設定される環境を取得する**

これにより、`cl.exe`、`INCLUDE`、`LIB`、`LIBPATH`、Windows SDK のパスが利用可能になります。

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Visual Studio の環境変数をこの PowerShell セッションに取り込む**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**手順3: Microsoft C++ コンパイラが利用可能であることを確認する**

```powershell
where.exe cl
```

<!-- @test:id=verify-visual-studio-community timeout=60 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Detected Visual Studio installations:"
& $VsWhere -all -products * -format table | Out-Host

$VcvarsList = & $VsWhere `
  -all `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat"
if (-not $VcvarsList) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
$Vcvars = $VcvarsList | Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using vcvars64.bat from Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}

$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

where.exe cl

Write-Host "OK: Visual Studio C++ build environment is available."
```
<!-- @test:end -->
<!-- @os:end -->

#### 環境変数の設定
<!-- @os:linux -->
<!-- @test:id=set-env-variables-linux timeout=300 setup=activate-venv -->
```bash
rocm-sdk init # Initialize the devel libraries

# Get the active Python version (e.g. "3.13") so the path works with any Python release
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"

# Set compiler and build settings
export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=set-env-variables-windows timeout=300 setup=activate-venv -->
```powershell
rocm-sdk init # Initialize the devel libraries

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
以下で AMD GPU が認識されていることを確認します:
<!-- @test:id=amd-smi-linux timeout=60 setup=activate-venv -->
```bash
amd-smi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-setup-rocm-pytorch-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

echo "Installed ROCm/PyTorch packages:"
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true

test -d "$ROCM_HOME"
test -d "$ROCM_HOME/bin"
test -d "$ROCM_HOME/lib"

test -f "$ROCM_HOME/lib/libhiprtc.so" || ls "$ROCM_HOME/lib"/libhiprtc.so*
test -f "$ROCM_HOME/lib/libroctx64.so" || ls "$ROCM_HOME/lib"/libroctx64.so*

hipcc --version >/dev/null
rocminfo >/dev/null

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=env-setup-rocm-pytorch-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }
$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Write-Host "ROCM_ROOT=$ROCM_ROOT"
Write-Host "ROCM_BIN=$ROCM_BIN"

Write-Host "Installed ROCm/PyTorch packages:"
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"

Get-ChildItem -Path $ROCM_ROOT -Recurse -Filter "hiprtc*.dll" | Select-Object -First 10 FullName | Out-Host

hipcc --version | Out-Host
hipinfo | Out-Host

$code = @'
import os
import sys
import torch

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

## 必要なファイルのダウンロード

**2つの新しいフォルダ**を作成し、対応するファイルをダウンロードして、以下のディレクトリ構造を作成してください:

| ディレクトリ | ダウンロードするファイル | 説明 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ベクトル加算カーネル用の JIT および C++ 拡張機能ファイル |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 行列乗算カーネル用の JIT および C++ 拡張機能ファイル |


## ウォークスルー1: ベクトル加算

#### アプローチA: JIT コンパイル

JIT（Just-In-Time）コンパイルとは、カーネルを Python 内の生の C++ 文字列として記述し、追加のビルド手順を必要とせずに実行時にコンパイルすることを意味します。

[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) を使用するには、ダウンロード済みであることを確認して次を実行します:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**主要なコードスニペット**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        for (int i = 0; i < 1000; i++)
            data[idx] += 1.0f;
    }
}
"""


# Snippet 2: Compile the kernel string. PyTorch calls hipcc under the hood with ROCm
add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()
block_size = 256
grid_size = (n + block_size - 1) // block_size


# Snippet 3: Launch: specify the grid/block dimensions and pass tensor arguments directly
for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )


# Snippet 4: Test the output
print("First 5 elements:", x[:5].cpu()) 
#Expected output: tensor([200001., 200001., 200001., 200001., 200001.])
```
<!-- @os:linux -->
> **ヒント**: このスクリプトは、カーネル実行中に `amd-smi` を100ミリ秒ごとにポーリングして、GPU 使用率のピーク値と平均値を記録するバックグラウンドスレッドも起動します。
<!-- @os:end -->

> **注**: **なぜブロックサイズが256なのか？** <br>
> - このカーネルは、**AMD GPU のウェーブフロント実行モデル**とうまく整合するため、**ブロックあたり256スレッド**を使用しています。
> - AMD ハードウェアは32スレッドのグループでスレッドを実行することを思い出してください。これにより、1ブロックあたり8ウェーブフロントとなります。（8ウェーブフロント × 32スレッド = 1ブロック）


**このワークロードの内容:**

このカーネルは、GPU 使用率を実証するために意図的に余分な処理を追加しています:

- テンソル内の**要素数は100,000,000個**
- カーネル起動ごとに、各要素につき**内部ループが1,000回実行**される
- 合計**200回のカーネル起動**

**計算式:**  
- 各要素: 1 × 1,000回の反復 × 200回の起動 だけ増加 = 200,000
- 最終結果: 1.0（初期値） + 200,000（加算分） = 200,001.0

**なぜ内部ループが必要か？**  
- `for (int i = 0; i < 1000; i++)` ループがなければ、200回の起動は瞬時に終了してしまい、監視ツールが意味のある GPU 使用率を捉えることができません。この意図的な処理により、各カーネル実行が十分に長くなり、監視ツールがパフォーマンスを測定できるようになります。

<!-- @os:linux -->
**期待される出力:**[パフォーマンス数値は変動します]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注**: Windows では、`amd-smi` はサポートされていません。GPU 使用率を追跡するには、タスクマネージャーを使用できます。プログラムを実行すると、使用率の短いスパイクが表示されるはずです。

**期待される出力:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**よくできました！これで最初の GPU カーネルを実行しました。**

<!-- @os:linux -->
<!-- @test:id=vector-addition-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
'''

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-addition-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
"""

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
'@

$code | python -
```
<!-- @test:end -->
<!-- @os:end -->

---
#### アプローチB: C++ 拡張機能

2つ目のアプローチはより手動的なもので、カーネルと Python バインディングを1つの `.cu` ファイルに記述し、PyTorch のビルドシステムを使ってネイティブにコンパイルし、それを Python にインポートします。

<!-- @os:windows -->
> **注**: C++ 拡張機能のアプローチでは、PyTorch が `.cu` ソースファイルをネイティブの `.pyd` 拡張モジュールにコンパイルするため、Visual Studio C++ ビルド環境が必要です。このネイティブ拡張機能のビルドは、Visual Studio が提供する Microsoft C++ ツールチェーン（コンパイラ、リンカ、ビルドツール）に依存しています。拡張機能をビルドする前に、セットアップセクションにある Visual Studio のアクティベーションコマンドを実行してください。
<!-- @os:end -->

まだダウンロードしていない場合は、次のファイルをダウンロードしてください。
<!-- @os:windows -->
| ファイル | 役割 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | カーネル + ランチャー + pybind11 バインディング、すべてが1つのファイルに |
| [setup.py](assets/Vector_Addition/setup.py) | ビルドスクリプト。`CUDAExtension` を使って `.cu` を `.pyd` にコンパイル |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | ビルドされた成果物を実行する Python スクリプト |
<!-- @os:end -->

<!-- @os:linux -->
| ファイル | 役割 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | カーネル + ランチャー + pybind11 バインディング、すべてが1つのファイルに |
| [setup.py](assets/Vector_Addition/setup.py) | ビルドスクリプト。`CUDAExtension` を使って `.cu` を `.so` にコンパイル |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | ビルドされた成果物を実行する Python スクリプト |
<!-- @os:end -->

#### **ステップ1: カーネル、ランチャー、バインディング** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
// GPU kernel, one thread per element
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] += 1.0f;
}

// Launcher, bridges torch::Tensor to raw pointer, sets grid/block, runs kernel
void add_one_launcher(torch::Tensor tensor) {
    int n = tensor.numel();
    float* data = tensor.data_ptr<float>();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    add_one<<<grid_size, block_size>>>(data, n);
    hipDeviceSynchronize();
}

// Python binding, exposes add_one_launcher as add_one_ext.add_one
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("add_one", &add_one_launcher, "Add one kernel (HIP)");
}
```

>**ヒント**: なぜ `hipDeviceSynchronize()` を使うのでしょうか？<br>
> - GPU カーネルの起動は非同期です。CPU が `add_one<<<grid_size, block_size>>>(data, n);` を実行すると、GPU の完了を待たずに直ちに次の命令を実行してしまいます。`hipDeviceSynchronize()` は、GPU カーネルが完了するまで CPU を待機させます。

#### **ステップ2: ビルド**
```bash
pip install --no-build-isolation -v .
```
>**注**: このコマンドは、作成した .cu ファイルをビルドするために、カレントディレクトリ内の `setup.py` を探します。


`CUDAExtension` は `torch.utils.cpp_extension` にある CUDA ビルドヘルパーです。ROCm を使用すると、PyTorch は **`CUDAExtension` を再マッピングして `nvcc` の代わりに `hipcc` を使用**するようにします。ROCm がビルドパスを横取りし、HIP コンパイラを経由させることで、CUDA コードを AMD 用に移植します。

これにより、以下のファイルが生成されます。
<!-- @os:windows -->
- `build/`: `.pyd` ファイルが含まれるディレクトリ
- `add_one_kernel.hip`: `.cu` ファイルを hipify して生成された HIP ソース。実際に `hipcc` がコンパイルしたのはこちら
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` ファイルが含まれるディレクトリ
- `add_one_kernel.hip`: `.cu` ファイルを hipify して生成された HIP ソース。実際に `hipcc` がコンパイルしたのはこちら
<!-- @os:end -->

#### **ステップ3: Python から使用する** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
このスクリプトを実行して、カーネルの動作を確認します。
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**期待される出力:**
```
Before: tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
After: tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

<!-- @os:linux -->
<!-- @test:id=vector-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Vector_Addition

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Vector_Addition"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## ウォークスルー2: 行列積

行列積は **C = A × B** を計算します。ここで、
- **A** は M×N（行×列）
- **B** は N×K
- **C** は M×K（結果）

各出力要素は次のように定義されます。
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C の各要素は独立して計算されるため、これは GPU の並列処理に最適です。

#### GPU スレッドへのマッピング方法

ベクトル加算（1次元）とは異なり、行列積は**2次元の出力**を生成するため、**2次元のスレッドグリッド**を使用します。

| | ベクトル加算 | 行列積 |
|---|---|---|
| **出力形状** | 1次元配列 | 2次元行列（M×K） |
| **スレッドマッピング** | 1スレッド → 1要素 | 1スレッド → 1出力要素 |
| **起動パターン** | 1次元グリッド: `(grid_x, 1, 1)` | 2次元グリッド: `(grid_x, grid_y, 1)` |
| **ブロックサイズ** | `(256, 1, 1)` | `(16, 16, 1)` = 256スレッド |

各スレッドは出力行列 C の1要素を計算します。位置 `(row, col)` にあるスレッドは、A の対応する行と B の対応する列を乗算することで `C[row][col]` を計算します。

**メモリレイアウト**: GPU メモリはフラット（1次元）ですが、行列は行ごとに格納されます。`A[row][col]` にアクセスするために、カーネルは `A[row * N + col]` を使用します。


#### アプローチA: JIT コンパイル:

ウォークスルー1と同様に、カーネルは Python 内で生の C++ 文字列として記述され、PyTorch の組み込み JIT によって実行時にコンパイルされます。


[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) を使用するには、ダウンロード済みであることを確認してから、次を実行してください。
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**主要なコードスニペット**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

# Snippet 2: Creating the Matrix - 2D indexing to map threads onto the M×K output matrix
# Inputs: A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK


# Snippet 3: Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")


# Snippet 4:. Launch with a 2D grid, grid_x covers columns (K), grid_y covers rows (M)
BLOCK = 16
matmul_kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()
print(f"Max error vs torch.mm: {max_err:.6f}")
```

このスクリプトは、結果を小さな許容誤差で `torch.mm` と照合して検証します。GPU 上の浮動小数点演算は、並列リダクションの順序の違いにより、CPU 実装と比較してわずかな数値的差異が生じることがあります。

<!-- @os:linux -->
**期待される出力:**[パフォーマンス値は変動します]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注**: Windows では `amd-smi` はサポートされていません。GPU の使用率を確認するには、タスクマネージャーを使用できます。プログラムを実行すると、使用率が短時間スパイクするのが確認できるはずです。

**期待される出力:**
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
No GPU Usage captured.
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=matmul-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
'''

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---
#### アプローチB：C++拡張機能

2つ目のアプローチはより手動的なもので、カーネルとPythonバインディングを1つの`.cu`ファイルに記述し、PyTorchのビルドシステムを使ってネイティブにコンパイルし、Pythonにインポートします。

<!-- @os:windows -->
> **注**：C++拡張機能のアプローチでは、PyTorchが`.cu`ソースファイルをネイティブの`.pyd`拡張モジュールにコンパイルするため、Visual Studio C++ビルド環境が必要です。このネイティブ拡張機能のビルドは、Visual Studioが提供するMicrosoft C++ツールチェーン（コンパイラ、リンカ、ビルドツール）に依存します。拡張機能をビルドする前に、セットアップセクションのVisual Studioアクティベーションコマンドを実行してください。
<!-- @os:end -->

まだダウンロードしていない場合は、以下のファイルをダウンロードしてください：
<!-- @os:windows -->
| ファイル | 役割 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | カーネル＋ランチャー＋pybind11バインディング |
| [setup.py](assets/Matrix_Multiplication/setup.py) | ビルドスクリプト。`CUDAExtension`を使用して`.cu`を`.pyd`にコンパイル |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ビルドされた成果物を実行するPythonスクリプト |
<!-- @os:end -->
<!-- @os:linux -->
| ファイル | 役割 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | カーネル＋ランチャー＋pybind11バインディング |
| [setup.py](assets/Matrix_Multiplication/setup.py) | ビルドスクリプト。`CUDAExtension`を使用して`.cu`を`.so`にコンパイル |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ビルドされた成果物を実行するPythonスクリプト |
<!-- @os:end -->

#### **ステップ1：カーネル、ランチャー、バインディング** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
#define BLOCK 16

// GPU kernel, one thread per output element of C
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}

// Launcher, extracts dims from torch::Tensor, allocates C, sets 2D grid/block
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0), N = A.size(1), K = B.size(1);
    auto C = torch::zeros({M, K}, A.options());

    dim3 block(BLOCK, BLOCK);
    dim3 grid((K + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(A.data_ptr<float>(), B.data_ptr<float>(),
                            C.data_ptr<float>(), M, N, K);
    hipDeviceSynchronize();
    return C;
}

// Python binding, exposes matmul_launcher as matmul_ext.matmul
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,K) -> C(M,K)");
}
```

ウォークスルー1の`add_one_launcher`と比較すると、ここでのランチャーは以下の点が異なります：
- 1つではなく2つの入力テンソルを受け取る
- 3つの次元（M、N、K）すべてをテンソルの形状から導出し、Pythonから手動でサイズを渡す必要がない
- 出力テンソルCをインプレースで変更するのではなく、確保して返す
- 2Dのローンチ形状を表現するために、グリッドとブロックの両方に`dim3`を使用する

#### **ステップ2：ビルド**
```bash
pip install --no-build-isolation -v .
```
>**注**：このコマンドは、現在のディレクトリ内の`setup.py`を探して、作成した.cuファイルをビルドします。


これにより、以下のファイルが生成されます：
<!-- @os:windows -->
- `build/`：`.pyd`ファイルを含むディレクトリ
- `matmul_kernel.hip`：`.cu`ファイルをhipify（HIP変換）することで生成されたHIPソース。これが実際に`hipcc`によってコンパイルされたものです
<!-- @os:end -->
<!-- @os:linux -->
- `build/`：`.so`ファイルを含むディレクトリ
- `matmul_kernel.hip`：`.cu`ファイルをhipify（HIP変換）することで生成されたHIPソース。これが実際に`hipcc`によってコンパイルされたものです
<!-- @os:end -->

#### **ステップ3：Pythonから使用する** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
このスクリプトを実行して、カーネルの動作を確認してください：
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**期待される出力：**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**素晴らしい！これでGPU上での行列乗算を実装できました。** これは大きなマイルストーンです。なぜなら、行列乗算は以下のような現代の機械学習演算の基盤だからです：
- ニューラルネットワーク層
- アテンション機構
- 埋め込み
- Transformer

<!-- @os:linux -->
<!-- @test:id=matmul-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Matrix_Multiplication

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Matrix_Multiplication"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## 次のステップ

JITコンパイルとC++拡張機能の両方を使用して、基本的な並列演算のためのGPUカーネルの記述、コンパイル、起動を学びました。

**パフォーマンス最適化：**
- **共有メモリタイリング** - データブロックをキャッシュしてグローバルメモリへのアクセスを削減
- **メモリコアレッシング** - 帯域幅のためにメモリアクセスパターンを最適化

**実世界のアルゴリズム：**
- **2D畳み込み** - 小さなフィルター（カーネル）が画像上をスライドし、近傍ピクセルの加重和から各出力ピクセルを計算します。これにより、ステンシル計算と共有メモリタイリングが導入され、スレッドが重複する画像領域を再利用してグローバルメモリへのアクセスを削減します。
- **Softmax関数**：Softmaxは、数値のベクトルを合計が1になる確率に変換するもので、ニューラルネットワークの出力に一般的に使用されます。これをGPU上で効率的に実装するには、大規模なベクトルを処理しながら並列リダクションと数値安定性の技術を導入します。

**本番環境での考慮事項：**
- **エラーハンドリング** - 境界チェックとデバイス管理
- **PyTorch統合** - autogradサポート付きのカスタム演算子