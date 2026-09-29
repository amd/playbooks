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

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) は、AMD が提供する C++ 製のコンピュータービジョン・機械学習ツールキットであり、深度推定、顔検出、顔メッシュトラッキングなど、強力なオンデバイス知覚機能を提供します。Ryzen AI ドライバーの上に構築されており、このライブラリは推論に最適な利用可能ハードウェア（GPU または NPU）を自動的に選択するため、モデルのトレーニングやフレームワーク統合を気にすることなく、C++ アプリケーションに AI 機能を追加できます。すべての処理はシステム上でローカルに実行されるため、プライバシーに配慮した低レイテンシーなアプリケーションに最適です。

このプレイブックでは、Ryzen AI CVML Library のセットアップ方法、付属のサンプルアプリケーションのビルド方法、サンプル画像での顔検出の実行方法を説明します。

## 学べること

- 前提条件のインストール方法とシステムでの Ryzen AI CVML Library のセットアップ方法
- CVML C++ API の仕組み：コンテキスト、フィーチャーオブジェクト、画像バッファ
- CMake と OpenCV を使用した付属サンプルアプリケーションのビルドおよび実行方法
- バウンディングボックスとランドマークを用いた画像上での顔検出の実行方法
- CVML 機能を独自の C++ アプリケーションに統合する方法

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール
<!-- @require:driver -->

## 追加の依存関係

始める前に、以下が揃っていることを確認してください：

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — `opencv-4.11.0-windows.exe` をダウンロードして実行し、ローカルフォルダー（例：`C:\opencv`）に展開します
- [CMake](https://cmake.org/download/) — Windows x86-64 MSI インストーラーをダウンロードし、インストール時に **"Add CMake to the system PATH for all users"** を選択します
- [Ryzen AI NPU driver](https://ryzenai.docs.amd.com/en/latest/inst.html) — 利用可能な最新バージョンをインストールします
- 「C++ によるデスクトップ開発」ワークロード付きの [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe)（MSVC コンパイラー、Windows SDK、C++ ビルドツールを含みます）
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — ソースからビルドする必要があります（Ubuntu 22.04 および 24.04 の apt パッケージではバージョン 4.11 は提供されていません）。以下の [Building OpenCV from Source](#building-opencv-from-source) を参照してください。
- CMake — apt 経由でインストールします：
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 または 24.04（カーネル >= 6.11.0-21-generic）
- [Ryzen AI NPU driver](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers)（Linux インストーラー — NPU 推論に必要です）
- Vulkan SDK（以下の [Vulkan SDK](#vulkan-sdk) セクションでインストールします）
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=cvml-prereqs-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
$env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"

cmake --version

if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
foreach ($dir in @("cmake", "include", "windows", "samples")) {
  $path = Join-Path $env:AMD_CVML_SDK_ROOT $dir
  if (-not (Test-Path $path)) {throw "Expected CVML folder was not found: $path"}
}

if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}
$opencvConfig = Join-Path $env:OPENCV_INSTALL_ROOT "OpenCVConfig.cmake"
if (-not (Test-Path $opencvConfig)) {throw "OpenCVConfig.cmake was not found: $opencvConfig"}

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $vswhere)) {throw "vswhere.exe not found. Install Visual Studio 2022 with Desktop development with C++ workload."}

$vsInstall = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Workload.NativeDesktop -property installationPath
if (-not $vsInstall) {throw "Visual Studio 2022 Desktop development with C++ workload was not found."}

$clPath = Get-ChildItem "$vsInstall\VC\Tools\MSVC" -Recurse -Filter cl.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $clPath) {throw "MSVC cl.exe was not found under Visual Studio installation."}

Write-Host "Checking Ryzen AI NPU driver presence..."
$npuDevices = Get-PnpDevice -Class ComputeAccelerator -ErrorAction SilentlyContinue | Where-Object {$_.FriendlyName -match "NPU|Neural|Ryzen AI|XDNA"}
if ($npuDevices) {
    Write-Host "NPU driver/device found:"
    $npuDevices | Format-Table Status, Class, Name, InstanceId -AutoSize
} else {
    Write-Host "Ryzen AI NPU driver was not detected. The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cvml-prereqs-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export AMD_CVML_SDK_ROOT="${AMD_CVML_SDK_ROOT:-/home/user/RyzenAI-Library}"
export OPENCV_INSTALL_ROOT="${OPENCV_INSTALL_ROOT:-/home/user/build/install}"

cmake --version

. /etc/os-release
if [ "${VERSION_ID}" != "24.04" ]; then
  echo "This CI runner is expected to be Ubuntu 24.04. Found: ${PRETTY_NAME}"
  exit 1
fi

if [ ! -d "$AMD_CVML_SDK_ROOT" ]; then
  echo "AMD_CVML_SDK_ROOT does not exist: $AMD_CVML_SDK_ROOT"
  exit 1
fi
for dir in cmake include linux samples; do
  if [ ! -d "$AMD_CVML_SDK_ROOT/$dir" ]; then
    echo "Expected CVML folder was not found: $AMD_CVML_SDK_ROOT/$dir"
    exit 1
  fi
done

if [ ! -d "$OPENCV_INSTALL_ROOT" ]; then
  echo "OPENCV_INSTALL_ROOT does not exist: $OPENCV_INSTALL_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT/lib" ]; then
  echo "OpenCV lib directory was not found: $OPENCV_INSTALL_ROOT/lib"
  exit 1
fi
if [ ! -f "$OPENCV_INSTALL_ROOT/lib/cmake/opencv4/OpenCVConfig.cmake" ]; then
  echo "OpenCVConfig.cmake was not found under: $OPENCV_INSTALL_ROOT/lib/cmake/opencv4"
  exit 1
fi

if ! command -v glslc >/dev/null 2>&1 && ! command -v vulkaninfo >/dev/null 2>&1; then
  echo "Vulkan SDK tools were not found. Install the Vulkan SDK before running this test."
  exit 1
fi

if [ -d /opt/xilinx/xrt/lib ]; then
  echo "Ryzen AI NPU driver/XRT runtime appears to be present."
else
  echo "Ryzen AI NPU driver/XRT runtime was not found at /opt/xilinx/xrt/lib."
  echo "The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
fi
```
<!-- @test:end --> 
<!-- @os:end -->

## CVML Library のセットアップ

まだアカウントをお持ちでない場合は [account.amd.com](https://account.amd.com) で AMD アカウントを作成し、以下のポータルリンクからサインインして Ryzen AI CVML Library をダウンロードします：

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

ダウンロード後、パッケージをローカルディレクトリ（例：Windows では `C:\RyzenAI-Library`、Linux では `~/RyzenAI-Library`）に展開し、`AMD_CVML_SDK_ROOT` 環境変数を展開先の場所に設定します：

<!-- @os:windows -->
```cmd
set AMD_CVML_SDK_ROOT=C:\RyzenAI-Library
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
export AMD_CVML_SDK_ROOT=~/RyzenAI-Library
```
<!-- @os:end -->

ライブラリパッケージには以下の構造が含まれています：

| フォルダー | 内容 |
|--------|----------|
| `cmake/` | CMake の `find_package` 関数用のパッケージ情報 |
| `include/` | C++ ヘッダーファイル（`cvml-depth-estimation.h`、`cvml-face-detector.h`、`cvml-face-mesh.h` など） |
| `windows/` | Windows 用バイナリファイル（コンパイル時の `.LIB` および実行時の `.DLL`/`.GRAPHLIB`/`.AMODEL` ファイル） |
| `linux/` | Linux 用バイナリファイル（コンパイル時および実行時の `.SO` ファイル） |
| `samples/` | ソースコード付きの個別サンプルアプリケーション |

<!-- @os:linux -->

### Linux 固有のセットアップ

#### OpenCV をソースからビルドする

OpenCV のビルド依存関係をインストールします：

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

contrib モジュールを含む OpenCV 4.11.0 をダウンロード、構成、ビルドします（参照：[OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)）：

```bash
wget -O opencv-4.11.0.zip https://github.com/opencv/opencv/archive/4.11.0.zip
wget -O opencv_contrib-4.11.0.zip https://github.com/opencv/opencv_contrib/archive/4.11.0.zip
unzip opencv-4.11.0.zip
unzip opencv_contrib-4.11.0.zip
mkdir -p build && cd build

cmake -DBUILD_opencv_world=ON \
  -DBUILD_SHARED_LIBS=ON \
  -DCMAKE_INSTALL_PREFIX=install \
  -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.11.0/modules ../opencv-4.11.0 \
  -DWITH_GSTREAMER=ON \
  -DHIGHGUI_ENABLE_PLUGINS=ON

cmake --build . --target install
```

共有ライブラリは `<build>/install/lib/` 配下にインストールされます。以降の手順では `install` ディレクトリを `OPENCV_INSTALL_ROOT` として使用してください。

#### Vulkan SDK

Vulkan SDK をインストールします：

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Ubuntu 22.04 を使用している場合は、MESA Vulkan ドライバーも更新してください：

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Ubuntu 24.04 の追加依存関係

Ubuntu 24.04 を使用している場合は、追加で必要なパッケージをインストールしてください：

```bash
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libnsl2 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly -y

DEP_PKG_LIST="https://launchpad.net/ubuntu/+archive/primary/+files/libmpdec3_2.5.1-2build2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10-minimal_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10-stdlib_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libprotobuf23_3.12.4-1ubuntu7_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libgoogle-glog0v5_0.5.0+really0.4.0-2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libtiff5_4.3.0-6_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libilmbase25_2.5.7-2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libopenexr25_2.5.7-1_amd64.deb"

for pkg in $DEP_PKG_LIST
do
    echo $pkg
    wget $pkg
    sudo dpkg -i *.deb
    rm *.deb
done
```

<!-- @os:end -->

## 基本概念

CVML Library は、各知覚機能（深度推定、顔検出、顔メッシュ）が独自のヘッダーファイルとフィーチャーオブジェクトを持つ、シンプルな C++ API を提供します。生のモデルを直接扱う必要はなく、ライブラリがモデルの読み込み、前処理、推論を自動的に処理します。

### 利用可能な機能

| 機能 | ヘッダーファイル | 説明 |
|---------|------------|-------------|
| **深度推定** | `cvml-depth-estimation.h` | RGB 画像からピクセル単位の深度マップを生成します |
| **顔検出** | `cvml-face-detector.h` | バウンディングボックス、ランドマーク（目、鼻、口）、信頼度スコアを用いて顔を検出します |
| **顔メッシュ** | `cvml-face-mesh.h` | 高密度なメッシュポイントで詳細な顔のジオメトリを追跡します |

### プログラミングモデル

すべての CVML アプリケーションは、同じ 4 ステップのパターンに従います：

1. **コンテキストの作成** — `amd::cvml::Context` はログ記録や推論バックエンドの選択などの共有リソースを管理します。
2. **フィーチャーオブジェクトの作成** — コンテキストに対して特定の機能（例：`amd::cvml::DepthEstimation`）をインスタンス化します。
3. **入力データのラップ** — `amd::cvml::Image` を使用して、データをコピーせずに RGB 画像バッファをカプセル化します。
4. **実行** — フィーチャーの処理メソッドを呼び出し、結果を読み取ります。

```cpp
// Step 1: Create context
auto context = amd::cvml::CreateContext();

// Step 2: Create feature object
amd::cvml::DepthEstimation depth_estimation(context);

// Step 3: Wrap input image (RGB, uint8, no copy)
amd::cvml::Image input(amd::cvml::Image::Format::kRGB,
                       amd::cvml::Image::DataType::kUint8,
                       width, height, data_pointer);

// Step 4: Execute
amd::cvml::Image output(amd::cvml::Image::Format::kGrayScale,
                        amd::cvml::Image::DataType::kFloat32,
                        width, height, nullptr);
depth_estimation.GenerateDepthMap(input, &output);

// Cleanup
context->Release();
```

### 推論バックエンド

このライブラリは、各操作に最適なハードウェア (GPU または NPU) を自動的に選択します。バックエンドを明示的に設定することもできます。

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **注:** NPU 操作に ONNX バックエンドを使用する機能は、初回実行時の起動レイテンシが長くなる場合があります。以降の実行では高速になります。

> **注:** 対象システムに NPU ドライバーがインストールされていない場合、Ryzen AI CVML ライブラリは推論操作を自動的に GPU バックエンドにフォールバックします。

## サンプルアプリケーションのビルド

CVML ライブラリには、各機能に対応したビルド可能なサンプルアプリケーションが含まれています。これらを一度にすべてビルドしてみましょう。

1. `OPENCV_INSTALL_ROOT` 環境変数を設定し、OpenCV のインストール先を指すようにします。

   <!-- @os:windows -->
   ```cmd
   rem Set the OpenCV path (Windows)
   rem Point to the build subfolder inside your OpenCV installation
   rem (e.g. if you extracted OpenCV to C:\opencv, use C:\opencv\build)
   rem CMake's find_package needs this folder to locate OpenCVConfig.cmake
   set OPENCV_INSTALL_ROOT=C:\opencv\build
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Set the OpenCV path (Linux)
   export OPENCV_INSTALL_ROOT=/path/to/opencv
   ```
   <!-- @os:end -->

2. CMake でサンプルをビルドします。

   <!-- @os:windows -->
   ```cmd
   rem Build the samples (Windows)
   cd samples
   mkdir build
   cmake -S %CD% -B %CD%\build -DOPENCV_INSTALL_ROOT=%OPENCV_INSTALL_ROOT% -DCMAKE_PREFIX_PATH=%OPENCV_INSTALL_ROOT%
   cmake --build %CD%\build --config Release
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Build the samples (Linux)
   cd samples
   mkdir build
   cmake -S $PWD -B $PWD/build -DOPENCV_INSTALL_ROOT="$OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$OPENCV_INSTALL_ROOT"
   cmake --build $PWD/build --config Release
   ```
   <!-- @os:end -->

   ビルドが成功すると、実行ファイルは以下の場所に生成されます。

   <!-- @os:windows -->
   ```
   samples\build\cvml-sample-face-detection\Release\cvml-sample-face-detection.exe
   samples\build\cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe
   samples\build\cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```
   samples/build/cvml-sample-face-detection/cvml-sample-face-detection
   samples/build/cvml-sample-depth-estimation/cvml-sample-depth-estimation
   samples/build/cvml-sample-face-mesh/cvml-sample-face-mesh
   ```
   <!-- @os:end -->

3. サンプルを実行する前に、CVML ランタイムファイルにアクセスできることを確認してください。

   <!-- @os:windows -->
   ```cmd
   rem Add the CVML runtime folder to PATH (Windows)
   set PATH=%CD%\..\windows;%PATH%
   rem Add OpenCV runtime libraries to PATH
   set PATH=%OPENCV_INSTALL_ROOT%\x64\vc16\bin;%PATH%
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Add the CVML runtime folder to LD_LIBRARY_PATH (Linux)
   export LD_LIBRARY_PATH=$PWD/../linux:$LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=/opt/xilinx/xrt/lib:$LD_LIBRARY_PATH
   # Add OpenCV runtime libraries to LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=$OPENCV_INSTALL_ROOT/lib:$LD_LIBRARY_PATH
   ```
   <!-- @os:end -->

## 顔検出の実行

顔検出サンプルは、画像、動画、またはライブカメラ映像から顔を検出します。検出した各顔に対して、バウンディングボックス、信頼度スコア、5 つの顔ランドマーク (両目、鼻、口の両端) を描画します。

まず、顔検出の実行ファイルがあるフォルダーに移動します。

<!-- @os:windows -->
```cmd
cd build\cvml-sample-face-detection\Release
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
cd build/cvml-sample-face-detection
```
<!-- @os:end -->

次に、入力として使用するサンプル画像をダウンロードします (写真提供: [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/)、Pexels を通じて無料で利用可能):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**サンプル画像に対して顔検出を実行します:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg
```
<!-- @os:end -->

ウィンドウが表示され、検出された顔の周囲のバウンディングボックス、信頼度スコア、顔ランドマークのポイント (目、鼻、口の両端) が付いた画像が表示されます。

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**注釈付き出力をファイルに保存します:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

**precise モデルを使用**すると、速度を犠牲にしてより高い精度が得られます:

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -m precise
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -m precise
```
<!-- @os:end -->

顔検出機能には 2 つのモデルバリアントがあります。

| モデル | 速度 | 精度 | 最適な用途 |
|-------|-------|----------|----------|
| `fast` (デフォルト) | 高い FPS | 良好 | リアルタイムカメラアプリケーション |
| `precise` | 低い FPS | 最高 | 写真解析、高精度が必要な用途 |


<!-- @os:windows -->
<!-- @test:id=cvml-build-sample-applications-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Build and run the samples inside a passwordless S4U scheduled task.

$ci = Join-Path $env:USERPROFILE "cvml-ci"
if (Test-Path $ci) {Remove-Item -Recurse -Force $ci}
New-Item -ItemType Directory -Force -Path $ci | Out-Null
$innerPs = Join-Path $ci "run_cvml.ps1"
$log = Join-Path $ci "cvml.log"

# Inner script (single-quoted here-string: not expanded here). It builds the
# samples and runs them (face detection twice, depth, and mesh), exiting
# non-zero on any failure. Its combined stdout+stderr is redirected to cvml.log
# by the task action below.
$inner = @'
$ErrorActionPreference = "Stop"
$ci = $PSScriptRoot
$code = 0
try {
  $env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
  $env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"
  if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
  if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}
  $work = Join-Path $ci "work"
  if (Test-Path $work) {Remove-Item -Recurse -Force $work}
  New-Item -ItemType Directory -Force -Path $work | Out-Null
  Copy-Item -Recurse -Force -Path (Join-Path $env:AMD_CVML_SDK_ROOT "*") -Destination $work
  $samplesDir = Join-Path $work "samples"
  $buildDir = Join-Path $samplesDir "build"
  Push-Location $samplesDir
  New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
  foreach ($sample in @("cvml-sample-face-detection", "cvml-sample-depth-estimation", "cvml-sample-face-mesh")) {
    $mainFile = Join-Path $samplesDir "$sample\main.cpp"
    $source = Get-Content -Path $mainFile -Raw
    $createContextLine = "auto context = amd::cvml::CreateContext();"
    $setBackendLine = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"
    if ($source -notmatch "SetInferenceBackend") {
      if (-not $source.Contains($createContextLine)) {throw "Could not find CreateContext line in: $mainFile"}
      $source = $source.Replace($createContextLine, "$createContextLine`r`n$setBackendLine")
      Set-Content -Path $mainFile -Value $source -NoNewline
    }
  }
  cmake -S (Get-Location).Path -B $buildDir -DOPENCV_INSTALL_ROOT="$env:OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$env:OPENCV_INSTALL_ROOT"
  cmake --build $buildDir --config Release --parallel
  $faceExe = Join-Path $buildDir "cvml-sample-face-detection\Release\cvml-sample-face-detection.exe"
  $depthExe = Join-Path $buildDir "cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe"
  $meshExe = Join-Path $buildDir "cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe"
  foreach ($exe in @($faceExe, $depthExe, $meshExe)) {if (-not (Test-Path $exe)) {throw "Expected executable was not found: $exe"}}
  $env:PATH = "$(Join-Path $samplesDir "..\windows");$env:PATH"
  $opencvRuntime = Join-Path $env:OPENCV_INSTALL_ROOT "x64\vc16\bin"
  if (-not (Test-Path $opencvRuntime)) {throw "OpenCV runtime DLL folder was not found: $opencvRuntime"}
  $env:PATH = "$opencvRuntime;$env:PATH"
  $inputImage = Join-Path $samplesDir "sample_face.jpg"
  curl.exe -L -o $inputImage "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
  $outputFaceFast = Join-Path $samplesDir "output_face_fast.jpg"
  $outputFacePrecise = Join-Path $samplesDir "output_face_precise.jpg"
  $outputDepth = Join-Path $samplesDir "output_depth.jpg"
  $outputMesh = Join-Path $samplesDir "output_mesh.jpg"
  Push-Location (Split-Path $faceExe)
  & $faceExe -i $inputImage -o $outputFaceFast
  if ($LASTEXITCODE -ne 0) {throw "Face detection default model failed with exit code $LASTEXITCODE."}
  & $faceExe -i $inputImage -o $outputFacePrecise -m precise
  if ($LASTEXITCODE -ne 0) {throw "Face detection precise model failed with exit code $LASTEXITCODE."}
  Pop-Location
  Push-Location (Split-Path $depthExe)
  & $depthExe -i $inputImage -o $outputDepth
  if ($LASTEXITCODE -ne 0) {throw "Depth estimation failed with exit code $LASTEXITCODE."}
  Pop-Location
  Push-Location (Split-Path $meshExe)
  & $meshExe -i $inputImage -o $outputMesh
  if ($LASTEXITCODE -ne 0) {throw "Face mesh failed with exit code $LASTEXITCODE."}
  Pop-Location
  foreach ($output in @($outputFaceFast, $outputFacePrecise, $outputDepth, $outputMesh)) {
    if (-not (Test-Path $output)) {throw "Expected output image was not created: $output"}
    if ((Get-Item $output).Length -le 0) {throw "Output image is empty: $output"}
  }
  Write-Output "CVML_ALL_SAMPLES_PASSED"
} catch {
  Write-Output ("CVML_ERROR: " + $_.Exception.Message)
  $code = 1
} finally {
  Pop-Location -ErrorAction SilentlyContinue
  if ($work -and (Test-Path $work)) {Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue}
}
exit $code
'@
Set-Content -Path $innerPs -Value $inner -Encoding UTF8

# Run via cmd so the inner script's full stdout+stderr (cmake, curl, and every
# sample executable, including any error text) is captured to cvml.log.
$taskName = "cvml_ci_run"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$innerPs`" > `"$log`" 2>&1"
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Force | Out-Null

try {
  Start-ScheduledTask -TaskName $taskName
  $deadline = (Get-Date).AddSeconds(1500)
  do {
    Start-Sleep -Seconds 5
    $state = (Get-ScheduledTask -TaskName $taskName).State
  } while ($state -eq "Running" -and (Get-Date) -lt $deadline)

  if (Test-Path $log) {Get-Content $log}

  if ($state -eq "Running") {throw "cvml S4U task did not finish within the time limit"}
  $result = (Get-ScheduledTaskInfo -TaskName $taskName).LastTaskResult
  if ($result -ne 0) {throw "cvml samples failed under S4U task (exit code $result)"}
}
finally {
  Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $ci -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cvml-build-sample-applications-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

export AMD_CVML_SDK_ROOT="${AMD_CVML_SDK_ROOT:-/home/user/RyzenAI-Library}"
export OPENCV_INSTALL_ROOT="${OPENCV_INSTALL_ROOT:-/home/user/build/install}"

if [ ! -d "$AMD_CVML_SDK_ROOT" ]; then
  echo "AMD_CVML_SDK_ROOT does not exist: $AMD_CVML_SDK_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT" ]; then
  echo "OPENCV_INSTALL_ROOT does not exist: $OPENCV_INSTALL_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT/lib" ]; then
  echo "OpenCV lib directory was not found: $OPENCV_INSTALL_ROOT/lib"
  exit 1
fi
if [ ! -f "$OPENCV_INSTALL_ROOT/lib/cmake/opencv4/OpenCVConfig.cmake" ]; then
  echo "OpenCVConfig.cmake was not found under: $OPENCV_INSTALL_ROOT/lib/cmake/opencv4"
  exit 1
fi

work="$PWD/cvml-test"
rm -rf "$work"
mkdir -p "$work"

cp -a "$AMD_CVML_SDK_ROOT"/. "$work"/

cleanup() {
  rm -rf "$work"
}
trap cleanup EXIT

samples_dir="$work/samples"
build_dir="$samples_dir/build"

cd "$samples_dir"
mkdir build

python3 - <<'PY'
from pathlib import Path

samples = [
    Path("cvml-sample-face-detection/main.cpp"),
    Path("cvml-sample-depth-estimation/main.cpp"),
    Path("cvml-sample-face-mesh/main.cpp"),
]

create_context_line = "auto context = amd::cvml::CreateContext();"
set_backend_line = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"

for path in samples:
    source = path.read_text()

    if "SetInferenceBackend" in source:
        continue

    if create_context_line not in source:
        raise SystemExit(f"Could not find CreateContext line in: {path}")

    source = source.replace(
        create_context_line,
        create_context_line + "\n" + set_backend_line,
        1,
    )

    path.write_text(source)
PY

cmake_config_log="$build_dir/cmake-configure.log"

cmake -S "$PWD" -B "$PWD/build" \
  -DOPENCV_INSTALL_ROOT="$OPENCV_INSTALL_ROOT" \
  -DCMAKE_PREFIX_PATH="$OPENCV_INSTALL_ROOT" 2>&1 | tee "$cmake_config_log"

if ! grep -q 'found version "4.11.0"' "$cmake_config_log"; then
  echo "CMake did not report OpenCV version 4.11.0."
  cat "$cmake_config_log"
  exit 1
fi

cmake --build "$PWD/build" --config Release --parallel "$(nproc)"

face_exe="$build_dir/cvml-sample-face-detection/cvml-sample-face-detection"
depth_exe="$build_dir/cvml-sample-depth-estimation/cvml-sample-depth-estimation"
mesh_exe="$build_dir/cvml-sample-face-mesh/cvml-sample-face-mesh"

for exe in "$face_exe" "$depth_exe" "$mesh_exe"; do
  if [ ! -x "$exe" ]; then
    echo "Expected executable was not found or is not executable: $exe"
    exit 1
  fi
done

export LD_LIBRARY_PATH="$PWD/../linux:${LD_LIBRARY_PATH:-}"

if [ -d /opt/xilinx/xrt/lib ]; then
  export LD_LIBRARY_PATH="/opt/xilinx/xrt/lib:$LD_LIBRARY_PATH"
  echo "Ryzen AI NPU driver/XRT runtime path found. Added /opt/xilinx/xrt/lib to LD_LIBRARY_PATH."
else
  echo "Ryzen AI NPU driver/XRT runtime was not found."
  echo "The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
fi

export LD_LIBRARY_PATH="$OPENCV_INSTALL_ROOT/lib:$LD_LIBRARY_PATH"

curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"

input_image="$samples_dir/sample_face.jpg"
output_face_fast="$samples_dir/output_face_fast.jpg"
output_face_precise="$samples_dir/output_face_precise.jpg"
output_depth="$samples_dir/output_depth.jpg"
output_mesh="$samples_dir/output_mesh.jpg"

cd "$(dirname "$face_exe")"
./cvml-sample-face-detection -i "$input_image" -o "$output_face_fast"
./cvml-sample-face-detection -i "$input_image" -o "$output_face_precise" -m precise

cd "$(dirname "$depth_exe")"
./cvml-sample-depth-estimation -i "$input_image" -o "$output_depth"

cd "$(dirname "$mesh_exe")"
./cvml-sample-face-mesh -i "$input_image" -o "$output_mesh"

for output in "$output_face_fast" "$output_face_precise" "$output_depth" "$output_mesh"; do
  if [ ! -s "$output" ]; then
    echo "Expected output image was not created or is empty: $output"
    exit 1
  fi
done
```
<!-- @test:end --> 
<!-- @os:end -->

## CVML を独自のアプリケーションに統合する

自身の C++ プロジェクトで CVML ライブラリを使用するには、CMake の `find_package` を使用して追加します。

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

ここで、`AMD_CVML_SDK_ROOT` は Ryzen AI CVML ライブラリフォルダーのルートを指します。次に、使用したい機能に対応する適切なヘッダーをインクルードします。

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## 次のステップ

以下の各サンプルについて、上記の[顔検出の実行](#running-face-detection)セクションと同じ手順に従い、まずそれぞれの実行可能フォルダに移動してください（例: Windowsでは`cd build\cvml-sample-depth-estimation\Release`、Linuxでは`cd build/cvml-sample-depth-estimation`）。Windowsでは、各コマンドの末尾に`.exe`を付加してください（例: `cvml-sample-depth-estimation.exe`）。

- **深度推定を試す**: `cvml-sample-depth-estimation -i sample_face.jpg`を実行して、色分けされた深度マップを生成します。近くの物体は暖色、遠くの物体は寒色で表示されます
- **フェイスメッシュを試す**: `cvml-sample-face-mesh -i sample_face.jpg`を実行して、詳細なメッシュポイントによる高密度な顔ジオメトリトラッキングを確認します
- **動画ファイルを処理する**: 任意のサンプルで`-i`および`-o`フラグを使用して動画を処理します（例: `cvml-sample-face-detection -i video.mp4 -o output.mp4`）
- **モデルバリアントを比較する**: 顔検出でデフォルトの`-m fast`に対して`-m precise`を試し、精度と速度のトレードオフを実際に確認します
- **独自のアプリを構築する**: CMake統合とC++ APIを使用して、独自のC++アプリケーションにCVML機能を追加します
- **機能を組み合わせる**: 同じアプリケーション内で顔検出と深度推定を連携させ、より豊かなシーン理解を実現します
- **ソースコードを閲覧する**: [GitHub上のRyzen AI CVML Library](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library)でヘッダードキュメント、追加サンプル、APIの詳細を確認します