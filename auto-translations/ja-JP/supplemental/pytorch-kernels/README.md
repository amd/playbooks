<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックはGitHubがレンダリングできない特殊なタグを使用しています。正しくコンテンツをプレビューするには [amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

GPU カーネルをゼロから記述し、コンパイルして AMD GPU 上で起動し、使用率が急上昇するのを確認しましょう。このプレイブックでは、GPU 計算が実際にどのように機能するかを示します。カーネルコードを記述し、数千のスレッドにわたって並列実行します。

> **注意**: これはかなり複雑なプレイブックであり、追加のデバッグや修正が必要になる場合があります。

## 学習内容

<!-- @os:windows -->
- GPU カーネルの仕組み: グリッド、ブロック、スレッド、およびそれらをデータにマッピングするインデックスモデル
- AMD ROCm/HIP スタックにより、CUDA スタイルのコードを変更なしで AMD GPU 上で実行できる方法
- `torch.cuda._compile_kernel` を使用してランタイムにカーネルをコンパイルする方法
- `CUDAExtension` + pybind11 を使用してネイティブ C++ カーネル拡張をビルドし、Python からインポートできるようにする方法
<!-- @os:end -->
<!-- @os:linux -->
- GPU カーネルの仕組み: グリッド、ブロック、スレッド、およびそれらをデータにマッピングするインデックスモデル
- AMD ROCm/HIP スタックにより、CUDA スタイルのコードを変更なしで AMD GPU 上で実行できる方法
- `torch.cuda._compile_kernel` を使用してランタイムにカーネルをコンパイルする方法
- `CUDAExtension` + pybind11 を使用してネイティブ C++ カーネル拡張をビルドし、Python からインポートできるようにする方法
- `amd-smi` を使用してカーネル実行時間を計測し、GPU 使用率をライブで監視する方法
<!-- @os:end -->

---

このプレイブックでは、カーネル開発のための 2 つのアプローチを取り上げます。

<!-- @os:windows -->
| アプローチ | エントリーポイント |
|---|---|
| **JIT コンパイル** | `torch.cuda._compile_kernel`、ビルドステップなしで Python 文字列としてカーネルを記述 |
| **C++ 拡張** | `CUDAExtension` + pybind11: `.cu` ファイルをネイティブ `.pyd` にコンパイルしてインポート |
<!-- @os:end -->
<!-- @os:linux -->
| アプローチ | エントリーポイント |
|---|---|
| **JIT コンパイル** | `torch.cuda._compile_kernel`、ビルドステップなしで Python 文字列としてカーネルを記述 |
| **C++ 拡張** | `CUDAExtension` + pybind11: `.cu` ファイルをネイティブ `.so` にコンパイルしてインポート |
<!-- @os:end -->

どちらのアプローチも AMD GPU 上で動作します。これが可能なのは、PyTorch の ROCm ビルドが CUDA API サーフェス全体を HIP にマッピングしているためです。つまり、`torch.cuda`、`CUDAExtension`、および CUDA カーネル構文はすべて AMD ハードウェア上で透過的に動作します。

---

## 背景

### GPU カーネルとは？

GPU カーネルは、数千の GPU スレッドにわたって同時に並列実行される関数です。呼び出しごとに 1 回実行される CPU 関数とは異なり、カーネルは**ブロック**の**グリッド**で起動され、各ブロックには多数の**スレッド**が含まれ、すべてが異なるデータに対して同じコードを実行します。

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### スレッドインデックスモデル

カーネルを起動する際に、2 つの次元を指定します。

| 変数 | 意味 |
|---|---|
| `gridDim` | グリッド内のブロック数 |
| `blockDim` | ブロックあたりのスレッド数 |

各スレッドは 3 つの組み込み読み取り専用変数にアクセスできます。

| 変数 | 意味 |
|---|---|
| `blockIdx.x` | このスレッドが属するブロック |
| `blockDim.x` | 1 つのブロック内のスレッド数 |
| `threadIdx.x` | ブロック内のスレッドインデックス |

### グローバルスレッド ID

これらの変数を組み合わせて、グローバルに一意なスレッドインデックスを計算します。

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

総スレッド数 = `gridDim.x * blockDim.x`。各スレッドは 1 つの要素を独立して処理します。これが**データ並列性**の基盤です。同じ操作が多くの要素に対して同時に実行され、スレッド間の依存関係はありません。

---

### GPU 実行モデル: ウェーブフロント

AMD GPU はスレッドを**ウェーブフロント**と呼ばれる **32** 個のグループで実行します。ウェーブフロント内のすべてのスレッドは同じ命令を同時に実行します。これは最適なブロックサイズの選択に影響します（256 スレッド = 8 ウェーブフロント = 良好なスケジューリング効率）。

### AMD GPU プログラミング: HIP + ROCm

**ROCm** は AMD のオープンソース GPU コンピュートスタック（ドライバー、コンパイラー、ライブラリ、ランタイム）です。**HIP** はその上に位置し、CUDA と構文的に同一になるよう設計されています。PyTorch の ROCm ビルドは `torch.cuda.*` を HIP に透過的にマッピングするため、同じコードが AMD GPU 上で動作します。

---

### PyTorch + AMD/HIP

PyTorch は ROCm ビルドを提供しており、CUDA API サーフェス（`torch.cuda.*`）が HIP によって透過的にバックアップされています。つまり:

- `torch.cuda.is_available()` は ROCm を搭載した AMD GPU 上で動作します
- `tensor.to("cuda")` は AMD GPU 上にメモリを割り当てます
- `torch.version.hip` は HIP バージョンを公開します

PyTorch は `torch.cuda._compile_kernel()` も公開しており、これは生のカーネル文字列を JIT コンパイルして呼び出し可能なオブジェクトを返す高レベルのショートカットで、別のビルドステップは不要です。

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
Linux では、任意のディレクトリでターミナルを開き、ROCm+PyTorch がすでにインストールされた venv を作成するためのコマンドに従ってください。
<!-- @test:id=create-venv timeout=60 -->
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
**GPU デバイスへのユーザーアクセスを許可します**（有効にするにはログアウトして再度ログインしてください）:

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux では、任意のディレクトリでターミナルを開き、venv を作成するためのコマンドに従ってください。
<!-- @test:id=create-venv timeout=60 -->
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
Windows では、任意のディレクトリでターミナルを開き、venv を作成するためのコマンドに従ってください。
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に PowerShell 実行ポリシーを変更する必要がある場合があります（例:
> RemoteSigned または Unrestricted に設定する）。

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
> **注意:** このプレイブックでは、カスタムカーネルのコンパイルに完全な開発ヘッダーが必要なため、Ryzen AI Halo 上でも ROCm と PyTorch を仮想環境にインストールする必要があります。

ROCm をインストールします:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorch をインストールします:
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
Linux の C/C++ ビルドツールチェーンをインストールします。これはシステムレベルの依存関係であり、`CUDAExtension` が `.cu` ファイルからネイティブの `.so` モジュールをビルドするため、C++ 拡張機能のウォークスルーに必要です。

作成した Python 仮想環境の外で、Linux マシン上で一度実行します:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

`kernel-env` 仮想環境をアクティブにした後、Python ビルドの依存関係をインストールします:
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
**Desktop development with C++** ワークロードを含む [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 以降 ([新しいバージョン](https://visualstudio.microsoft.com/vs/community/)) がインストールされていることを確認してください。

> **注意**: この Visual Studio C++ 環境のセットアップは、**C++ 拡張機能**アプローチにのみ必要です。JIT コンパイルアプローチには必要ありません。

PowerShell ターミナルを開き、C++ 拡張機能をビルドする前に以下のコマンドを実行します。

**ステップ 1: インストール済みの Visual Studio C++ 環境を見つける**

**(A) Visual Studio インストーラーと共にインストールされる `vswhere.exe` を見つける**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) C++ ビルドツールを含む Visual Studio 2022 以降から `vcvars64.bat` を見つける**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) 使用している Visual Studio C++ 環境を表示する**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**ステップ 2: Visual Studio C++ ビルド環境をアクティブにする**

**(A) `vcvars64.bat` を実行し、設定される環境をキャプチャする**

これにより、`cl.exe`、`INCLUDE`、`LIB`、`LIBPATH`、および Windows SDK のパスが利用可能になります。

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Visual Studio の環境変数をこの PowerShell セッションにインポートする**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**ステップ 3: Microsoft C++ コンパイラが利用可能であることを確認する**

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
AMD GPU が認識されていることを以下のコマンドで確認します:
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

以下のディレクトリ構造を作成するために、**2 つの新しいフォルダー**を作成し、対応するファイルをダウンロードします:

| ディレクトリ | ダウンロードするファイル | 説明 |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ベクター加算カーネル用の JIT および C++ 拡張機能ファイル |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | 行列乗算カーネル用の JIT および C++ 拡張機能ファイル |


## ウォークスルー

### ウォークスルー 1: ベクター加算

#### アプローチ A: JIT コンパイル

JIT（Just-In-Time）コンパイルとは、カーネルを Python 内の生の C++ 文字列として記述し、追加のビルドステップを必要とせずに実行時にコンパイルすることを意味します。

[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) を使用するには、ダウンロード済みであることを確認してから実行します:
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
> **ヒント**: このスクリプトは、カーネル実行中の GPU 使用率のピーク値と平均値をログに記録するために、100ms ごとに `amd-smi` をポーリングするバックグラウンドスレッドも起動します。
<!-- @os:end -->

> **注意**: **ブロックサイズが 256 である理由** <br>
> - このカーネルは、AMD GPU の**ウェーブフロント実行モデル**に適合するため、**ブロックあたり 256 スレッド**を使用します。
> - AMD ハードウェアはスレッドを 32 スレッドのグループで実行するため、ブロックあたり 8 ウェーブフロントになります。（8 ウェーブフロント × 32 スレッド = 1 ブロック）


**ワークロードの内容:**

このカーネルは GPU 使用率を示すために意図的に余分な処理を追加しています:

- テンソル内の要素数: **100,000,000**
- **内部ループはカーネル起動ごとに要素あたり 1,000 回**実行されます
- **カーネル起動の合計回数**: 200 回

**計算:**  
- 各要素: 1 × 1,000 イテレーション × 200 回起動 = 200,000 ずつインクリメントされます
- 最終結果: 1.0（初期値）+ 200,000（加算）= 200,001.0

**内部ループが必要な理由:**  
- `for (int i = 0; i < 1000; i++)` ループがなければ、200 回の起動は瞬時に完了し、監視ツールが意味のある GPU 使用率を取得できません。この意図的な処理により、各カーネルの実行時間が十分に長くなり、監視ツールでパフォーマンスを計測できるようになります。

<!-- @os:linux -->
**期待される出力:** [パフォーマンスの数値は異なる場合があります]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**: Windows では `amd-smi` はサポートされていません。GPU 使用率を追跡するには、タスクマネージャーを使用してください。プログラムを実行すると、使用率が一時的にスパイクするのを確認できます。

**期待される出力:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**よくできました！初めての GPU カーネルを実行しました。**

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
#### アプローチ B: C++ Extension

2つ目のアプローチはより手動的です。カーネルとPythonバインディングを単一の `.cu` ファイルに記述し、PyTorchのビルドシステムを使ってネイティブにコンパイルし、Pythonにインポートします。

<!-- @os:windows -->
> **注意**: C++ Extensionアプローチでは、PyTorchが `.cu` ソースファイルをネイティブの `.pyd` 拡張モジュールにコンパイルするため、Visual Studio C++ビルド環境が必要です。そのネイティブ拡張のビルドは、Visual Studioが提供するMicrosoft C++ツールチェーン（コンパイラ、リンカ、ビルドツール）に依存します。拡張をビルドする前に、セットアップセクションのVisual Studio有効化コマンドを実行してください。
<!-- @os:end -->

まだダウンロードしていない場合は、以下のファイルをダウンロードしてください：
<!-- @os:windows -->
| ファイル | 役割 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | カーネル + ランチャー + pybind11バインディング、すべて1つのファイルに収録 |
| [setup.py](assets/Vector_Addition/setup.py) | ビルドスクリプト。`CUDAExtension` を使って `.cu` を `.pyd` にコンパイル |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | ビルド成果物を実行するPythonスクリプト |
<!-- @os:end -->

<!-- @os:linux -->
| ファイル | 役割 |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | カーネル + ランチャー + pybind11バインディング、すべて1つのファイルに収録 |
| [setup.py](assets/Vector_Addition/setup.py) | ビルドスクリプト。`CUDAExtension` を使って `.cu` を `.so` にコンパイル |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | ビルド成果物を実行するPythonスクリプト |
<!-- @os:end -->

#### **ステップ 1: カーネル、ランチャー、バインディング** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**ヒント**: なぜ `hipDeviceSynchronize()` を使うのか？ <br>
> - GPU カーネルの起動は非同期です。CPU が `add_one<<<grid_size, block_size>>>(data, n);` を実行すると、GPU を待たずに即座に次の命令を実行します。`hipDeviceSynchronize()` は、GPU カーネルが完了するまで CPU を強制的に待機させます。

#### **ステップ 2: ビルド**
```bash
pip install --no-build-isolation -v .
```
>**注意**: このコマンドは、作成した .cu ファイルをビルドするために、カレントディレクトリの `setup.py` を参照します。


`CUDAExtension` は `torch.utils.cpp_extension` が提供する CUDA ビルドヘルパーです。ROCm では、PyTorch が **`CUDAExtension` を `nvcc` の代わりに `hipcc` を使用するようにリマップ**します。ROCm はビルドパスをインターセプトし、HIP コンパイラを通じてルーティングすることで、CUDA コードを AMD 向けに移植します。

これにより以下のファイルが生成されます：
<!-- @os:windows -->
- `build/`: `.pyd` ファイルが格納されるディレクトリ
- `add_one_kernel.hip`: `.cu` ファイルをHIP化して生成されたHIPソース。`hipcc` が実際にコンパイルするファイル
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` ファイルが格納されるディレクトリ
- `add_one_kernel.hip`: `.cu` ファイルをHIP化して生成されたHIPソース。`hipcc` が実際にコンパイルするファイル
<!-- @os:end -->

#### **ステップ 3: Python から使用する** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
このスクリプトを実行してカーネルの動作を確認してください：
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**期待される出力：**
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

### ウォークスルー 2: 行列乗算

行列乗算は **C = A × B** を計算します。ここで：
- **A** は M×N（行 × 列）
- **B** は N×K  
- **C** は M×K（結果）

各出力要素は次のように定義されます：
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C の各要素は独立して計算されるため、GPU の並列処理に最適です。

#### GPU スレッドへのマッピング方法

ベクトル加算（1D）とは異なり、行列乗算は **2D の出力**を生成するため、**2D グリッドのスレッド**を使用します：

| | ベクトル加算 | 行列乗算 |
|---|---|---|
| **出力の形状** | 1D 配列 | 2D 行列 (M×K) |
| **スレッドのマッピング** | 1スレッド → 1要素 | 1スレッド → 1出力要素 |
| **起動パターン** | 1D グリッド: `(grid_x, 1, 1)` | 2D グリッド: `(grid_x, grid_y, 1)` |
| **ブロックサイズ** | `(256, 1, 1)` | `(16, 16, 1)` = 256スレッド |

各スレッドは出力行列 C の1要素を計算します。位置 `(row, col)` のスレッドは、A の対応する行と B の対応する列を掛け合わせることで `C[row][col]` を計算します。

**メモリレイアウト**: GPU メモリはフラット（1D）ですが、行列は行ごとに格納されます。`A[row][col]` にアクセスするために、カーネルは `A[row * N + col]` を使用します。


#### アプローチ A: JIT コンパイル:

ウォークスルー 1 と同様に、カーネルは Python 内の生の C++ 文字列として記述され、PyTorch の組み込み JIT を通じて実行時にコンパイルされます。


[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) を使用するには、ダウンロード済みであることを確認して実行してください：
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

このスクリプトは、小さな許容誤差を設けて `torch.mm` と結果を照合します。GPU での浮動小数点演算は、並列リダクションの順序の違いにより、CPU 実装と比べてわずかな数値差が生じる場合があります。

<!-- @os:linux -->
**期待される出力：**[パフォーマンスの数値は異なる場合があります]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **注意**: Windows では `amd-smi` はサポートされていません。GPU 使用率を追跡するには、タスクマネージャーを使用してください。プログラムを実行すると、使用率が一時的に急上昇するのを確認できます。

**期待される出力：**
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
#### アプローチ B: C++ Extension

2つ目のアプローチはより手動的です。カーネルとPythonバインディングを単一の `.cu` ファイルに記述し、PyTorchのビルドシステムを使用してネイティブにコンパイルし、Pythonにインポートします。

<!-- @os:windows -->
> **Note**: C++ Extensionアプローチでは、PyTorchが `.cu` ソースファイルをネイティブの `.pyd` 拡張モジュールにコンパイルするため、Visual Studio C++ビルド環境が必要です。そのネイティブ拡張のビルドは、Visual Studioが提供するMicrosoft C++ツールチェーン（コンパイラ、リンカ、ビルドツール）に依存します。拡張をビルドする前に、セットアップセクションのVisual Studioアクティベーションコマンドを実行してください。
<!-- @os:end -->

まだダウンロードしていない場合は、以下のファイルをダウンロードしてください：
<!-- @os:windows -->
| ファイル | 役割 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | カーネル + ランチャー + pybind11バインディング |
| [setup.py](assets/Matrix_Multiplication/setup.py) | ビルドスクリプト。`CUDAExtension` を使用して `.cu` を `.pyd` にコンパイル |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ビルド成果物を実行するPythonスクリプト |
<!-- @os:end -->
<!-- @os:linux -->
| ファイル | 役割 |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | カーネル + ランチャー + pybind11バインディング |
| [setup.py](assets/Matrix_Multiplication/setup.py) | ビルドスクリプト。`CUDAExtension` を使用して `.cu` を `.so` にコンパイル |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ビルド成果物を実行するPythonスクリプト |
<!-- @os:end -->

#### **ステップ 1: カーネル、ランチャー、バインディング** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

ウォークスルー1の `add_one_launcher` と比較して、ここでのランチャーは以下の点が異なります：
- 入力テンソルが1つではなく2つ
- Pythonからサイズを手動で渡すのではなく、テンソルの形状から3つの次元（M、N、K）をすべて導出
- インプレースで変更するのではなく、出力テンソルCを割り当てて返す
- グリッドとブロックの両方に `dim3` を使用して2Dの起動形状を表現

#### **ステップ 2: ビルド**
```bash
pip install --no-build-isolation -v .
```
>**Note**: このコマンドは、作成した .cu ファイルをビルドするために、カレントディレクトリの `setup.py` を参照します。


以下のファイルが生成されます：
<!-- @os:windows -->
- `build/`:  `.pyd` ファイルを含むディレクトリ
- `matmul_kernel.hip`:  `.cu` ファイルをhipifyして生成されたHIPソース。`hipcc` が実際にコンパイルするファイル
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  `.so` ファイルを含むディレクトリ
- `matmul_kernel.hip`:  `.cu` ファイルをhipifyして生成されたHIPソース。`hipcc` が実際にコンパイルするファイル
<!-- @os:end -->

#### **ステップ 3: Pythonから使用する** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
このスクリプトを実行してカーネルの動作を確認してください：
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**期待される出力：**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**素晴らしい！GPU上で行列乗算を実装しました。** これは重要なマイルストーンです。行列乗算は以下のような現代の機械学習演算の根幹をなすものだからです：
- ニューラルネットワーク層
- アテンションメカニズム
- 埋め込み
- Transformers

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

JITコンパイルとC++ Extensionの両方を使用して、基本的な並列演算のGPUカーネルを記述、コンパイル、起動する方法を学びました。

**パフォーマンスの最適化：**
- **共有メモリタイリング** - データブロックをキャッシュしてグローバルメモリアクセスを削減
- **メモリコアレッシング** - 帯域幅のためにメモリアクセスパターンを最適化

**実世界のアルゴリズム：**
- **2次元畳み込み** - 小さなフィルター（カーネル）が画像上をスライドし、隣接ピクセルの重み付き和から各出力ピクセルを計算します。これにより、ステンシル計算と共有メモリタイリングが導入され、スレッドが重複する画像領域を再利用してグローバルメモリアクセスを削減します。
- **Softmax関数**: Softmaxは数値のベクトルを合計が1になる確率に変換するもので、ニューラルネットワークの出力で一般的に使用されます。GPU上で効率的に実装することで、大きなベクトルを処理しながら並列リダクションと数値安定性の手法が導入されます。

**本番環境での考慮事項：**
- **エラーハンドリング** - 境界チェックとデバイス管理
- **PyTorch統合** - autogradサポートを持つカスタムオペレーター