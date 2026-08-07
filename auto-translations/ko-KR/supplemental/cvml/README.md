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

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library)는 심도 추정, 얼굴 감지, 얼굴 메시 추적을 포함하여 강력한 온디바이스 인식 기능을 제공하는 AMD의 C++ 컴퓨터 비전 및 머신러닝 툴킷입니다. Ryzen AI 드라이버를 기반으로 구축된 이 라이브러리는 추론에 가장 적합한 하드웨어(GPU 또는 NPU)를 자동으로 선택하므로 모델 학습이나 프레임워크 통합을 걱정하지 않고도 C++ 애플리케이션에 AI 기능을 추가할 수 있습니다. 모든 처리는 시스템에서 로컬로 이루어지므로 개인정보 보호가 중요하고 지연 시간이 짧아야 하는 애플리케이션에 이상적입니다.

이 플레이북에서는 Ryzen AI CVML Library를 설정하고, 포함된 샘플 애플리케이션을 빌드하며, 샘플 이미지에서 얼굴 감지를 실행하는 방법을 배웁니다.

## 학습 내용

- 시스템에 사전 요구 사항을 설치하고 Ryzen AI CVML Library를 설정하는 방법
- CVML C++ API가 작동하는 방식: 컨텍스트, 기능 객체, 이미지 버퍼
- CMake와 OpenCV를 사용하여 포함된 샘플 애플리케이션을 빌드하고 실행하는 방법
- 경계 상자와 랜드마크를 사용하여 이미지에서 얼굴 감지를 실행하는 방법
- CVML 기능을 자체 C++ 애플리케이션에 통합하는 방법

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치
<!-- @require:driver -->

## 추가 종속성

시작하기 전에 다음이 준비되어 있는지 확인하세요:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — `opencv-4.11.0-windows.exe`를 다운로드하여 실행하고 로컬 폴더(예: `C:\opencv`)에 압축을 풉니다
- [CMake](https://cmake.org/download/) — Windows x86-64 MSI 설치 프로그램을 다운로드하고 설치 중 **"Add CMake to the system PATH for all users"**를 선택합니다
- [Ryzen AI NPU 드라이버](https://ryzenai.docs.amd.com/en/latest/inst.html) — 최신 버전을 설치합니다
- "Desktop development with C++" 워크로드가 포함된 [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe)(MSVC 컴파일러, Windows SDK, C++ 빌드 도구 포함)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — 소스에서 빌드해야 합니다(Ubuntu 22.04 및 24.04의 apt 패키지는 4.11 버전을 제공하지 않습니다). 아래 [소스에서 OpenCV 빌드하기](#building-opencv-from-source)를 참조하세요.
- CMake — apt를 통해 설치합니다:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 또는 24.04(커널 >= 6.11.0-21-generic)
- [Ryzen AI NPU 드라이버](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers)(Linux 설치 프로그램 — NPU 추론에 필요)
- Vulkan SDK(아래 [Vulkan SDK](#vulkan-sdk) 섹션에서 설치)
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

## CVML Library 설정

[account.amd.com](https://account.amd.com)에서 AMD 계정이 없는 경우 계정을 생성한 다음, 로그인하여 아래 포털 링크에서 Ryzen AI CVML Library를 다운로드하세요:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

다운로드 후 패키지를 로컬 디렉터리(예: Windows에서는 `C:\RyzenAI-Library`, Linux에서는 `~/RyzenAI-Library`)에 압축 해제하고 `AMD_CVML_SDK_ROOT` 환경 변수를 압축 해제한 위치로 설정하세요:

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

라이브러리 패키지에는 다음과 같은 구조가 포함되어 있습니다:

| 폴더 | 내용 |
|--------|----------|
| `cmake/` | CMake의 `find_package` 함수를 위한 패키징 정보 |
| `include/` | C++ 헤더 파일(`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` 등) |
| `windows/` | Windows용 바이너리 파일(컴파일 타임 `.LIB` 및 런타임 `.DLL`/`.GRAPHLIB`/`.AMODEL` 파일) |
| `linux/` | Linux용 바이너리 파일(컴파일 및 런타임 `.SO` 파일) |
| `samples/` | 소스 코드가 포함된 개별 샘플 애플리케이션 |

<!-- @os:linux -->

### Linux 관련 설정

#### 소스에서 OpenCV 빌드하기

OpenCV 빌드 종속성을 설치합니다:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

contrib 모듈과 함께 OpenCV 4.11.0을 다운로드, 구성 및 빌드합니다(참고: [OpenCV Linux 설치 튜토리얼](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

공유 라이브러리는 `<build>/install/lib/` 아래에 설치됩니다. 이후 단계에서는 `install` 디렉터리를 `OPENCV_INSTALL_ROOT`로 사용하세요.

#### Vulkan SDK

Vulkan SDK를 설치합니다:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Ubuntu 22.04를 사용 중이라면 MESA Vulkan 드라이버도 업데이트하세요:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### 추가 Ubuntu 24.04 종속성

Ubuntu 24.04를 사용 중이라면 추가로 필요한 패키지를 설치하세요:

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

## 핵심 개념

CVML Library는 각 인식 기능(심도 추정, 얼굴 감지, 얼굴 메시)이 고유한 헤더 파일과 기능 객체를 갖는 간단한 C++ API를 제공합니다. 원시 모델을 직접 다루지 않아도 되며, 라이브러리가 모델 로딩, 전처리, 추론을 자동으로 처리합니다.

### 사용 가능한 기능

| 기능 | 헤더 파일 | 설명 |
|---------|------------|-------------|
| **심도 추정** | `cvml-depth-estimation.h` | RGB 이미지에서 픽셀 단위 심도 맵을 생성합니다 |
| **얼굴 감지** | `cvml-face-detector.h` | 경계 상자, 랜드마크(눈, 코, 입), 신뢰도 점수와 함께 얼굴을 감지합니다 |
| **얼굴 메시** | `cvml-face-mesh.h` | 조밀한 메시 포인트로 세부적인 얼굴 기하 구조를 추적합니다 |

### 프로그래밍 모델

모든 CVML 애플리케이션은 동일한 4단계 패턴을 따릅니다:

1. **컨텍스트 생성** — `amd::cvml::Context`는 로깅 및 추론 백엔드 선택과 같은 공유 리소스를 관리합니다.
2. **기능 객체 생성** — 컨텍스트에 대해 특정 기능(예: `amd::cvml::DepthEstimation`)을 인스턴스화합니다.
3. **입력 데이터 래핑** — `amd::cvml::Image`를 사용하여 데이터를 복사하지 않고 RGB 이미지 버퍼를 캡슐화합니다.
4. **실행** — 기능의 처리 메서드를 호출하고 결과를 읽습니다.

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

### 추론 백엔드

라이브러리는 각 작업에 가장 적합한 하드웨어(GPU 또는 NPU)를 자동으로 선택합니다. 백엔드를 명시적으로 설정할 수도 있습니다:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **참고:** NPU 작업에 ONNX 백엔드를 사용하는 기능은 처음 실행 시 시작 지연 시간이 더 길어질 수 있습니다. 이후 실행에서는 더 빨라집니다.

> **참고:** 대상 시스템에 NPU 드라이버가 설치되어 있지 않으면 Ryzen AI CVML 라이브러리는 추론 작업을 위해 자동으로 GPU 백엔드로 대체됩니다.

## 샘플 애플리케이션 빌드하기

CVML 라이브러리에는 각 기능에 대해 바로 빌드할 수 있는 샘플 애플리케이션이 포함되어 있습니다. 한 번에 모두 빌드해 보겠습니다.

1. `OPENCV_INSTALL_ROOT` 환경 변수를 설정하여 OpenCV 설치 위치를 가리키도록 합니다:

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

2. CMake로 샘플을 빌드합니다:

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

   빌드에 성공하면 실행 파일은 다음 위치에 생성됩니다:

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

3. 샘플을 실행하기 전에 CVML 런타임 파일에 접근할 수 있는지 확인합니다:

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

## 얼굴 인식 실행하기

얼굴 인식 샘플은 이미지, 동영상 또는 실시간 카메라 피드에서 얼굴을 감지합니다. 감지된 각 얼굴에 대해 경계 상자, 신뢰도 점수, 그리고 다섯 개의 얼굴 랜드마크(두 눈, 코, 입 양쪽 끝)를 그려서 표시합니다.

먼저 얼굴 인식 실행 파일 폴더로 이동합니다:

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

그런 다음 입력으로 사용할 샘플 이미지를 다운로드합니다(사진 제공: [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), Pexels를 통해 무료로 사용 가능):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**샘플 이미지에서 얼굴 인식 실행하기:**

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

감지된 얼굴 주변의 경계 상자, 신뢰도 점수, 얼굴 랜드마크 포인트(눈, 코, 입 가장자리)가 표시된 이미지 창이 나타납니다.

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**주석이 표시된 출력을 파일로 저장하기:**

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

더 높은 정확도를 위해 **정밀 모델을 사용하기**(속도를 희생함):

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

얼굴 인식 기능은 두 가지 모델 변형을 제공합니다:

| 모델 | 속도 | 정확도 | 최적 사용처 |
|-------|-------|----------|----------|
| `fast` (기본값) | 더 높은 FPS | 양호 | 실시간 카메라 애플리케이션 |
| `precise` | 더 낮은 FPS | 최고 | 사진 분석, 높은 정확도가 필요한 경우 |


<!-- @os:windows -->
<!-- @test:id=cvml-build-sample-applications-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
$env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"

if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}

$work = Join-Path (Get-Location) "cvml-test"
if (Test-Path $work) {Remove-Item -Recurse -Force $work}
New-Item -ItemType Directory -Force -Path $work | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $env:AMD_CVML_SDK_ROOT "*") -Destination $work

$samplesDir = Join-Path $work "samples"
$buildDir = Join-Path $samplesDir "build"

Push-Location $samplesDir

try {
  New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
  foreach ($sample in @("cvml-sample-face-detection", "cvml-sample-depth-estimation", "cvml-sample-face-mesh")) {
    $mainFile = Join-Path $samplesDir "$sample\main.cpp"
    $source = Get-Content -Path $mainFile -Raw

    $createContextLine = "auto context = amd::cvml::CreateContext();"
    $setBackendLine = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"

    if ($source -notmatch "SetInferenceBackend") {
      if (-not $source.Contains($createContextLine)) {
        throw "Could not find CreateContext line in: $mainFile"
      }

      $source = $source.Replace($createContextLine, "$createContextLine`r`n$setBackendLine")
      Set-Content -Path $mainFile -Value $source -NoNewline
    }
  }

  cmake -S (Get-Location).Path -B $buildDir -DOPENCV_INSTALL_ROOT="$env:OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$env:OPENCV_INSTALL_ROOT"
  cmake --build $buildDir --config Release --parallel

  $faceExe = Join-Path $buildDir "cvml-sample-face-detection\Release\cvml-sample-face-detection.exe"
  $depthExe = Join-Path $buildDir "cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe"
  $meshExe = Join-Path $buildDir "cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe"

  foreach ($exe in @($faceExe, $depthExe, $meshExe)) {
    if (-not (Test-Path $exe)) {throw "Expected executable was not found: $exe"}
  }

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
}
finally {
  Pop-Location -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
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

## 자체 애플리케이션에 CVML 통합하기

자체 C++ 프로젝트에서 CVML 라이브러리를 사용하려면 CMake의 `find_package`를 통해 추가합니다:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

여기서 `AMD_CVML_SDK_ROOT`는 Ryzen AI CVML 라이브러리 폴더의 루트를 가리킵니다. 그런 다음 사용하려는 기능에 맞는 헤더를 포함합니다:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## 다음 단계

아래 각 샘플에 대해, 위의 [얼굴 감지 실행하기](#running-face-detection) 섹션과 동일한 방식으로 먼저 실행 파일 폴더로 이동하십시오 (예: Windows에서는 `cd build\cvml-sample-depth-estimation\Release`, Linux에서는 `cd build/cvml-sample-depth-estimation`). Windows에서는 각 명령어 끝에 `.exe`를 붙이십시오 (예: `cvml-sample-depth-estimation.exe`).

- **깊이 추정 사용해보기**: `cvml-sample-depth-estimation -i sample_face.jpg`를 실행하여 색상화된 깊이 맵을 생성합니다 — 가까운 물체는 따뜻한 색상으로, 먼 물체는 차가운 색상으로 표시됩니다
- **얼굴 메쉬 살펴보기**: `cvml-sample-face-mesh -i sample_face.jpg`를 실행하여 상세한 메쉬 포인트로 조밀한 얼굴 기하학 추적을 확인합니다
- **비디오 파일 처리하기**: 모든 샘플에서 `-i` 및 `-o` 플래그를 사용하여 비디오를 처리할 수 있습니다 (예: `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **모델 변형 비교하기**: 얼굴 감지에서 기본값인 `-m fast` 대신 `-m precise`를 사용해보고 정확도와 속도 간의 트레이드오프를 직접 확인합니다
- **나만의 앱 빌드하기**: CMake 통합 및 C++ API를 사용하여 여러분의 C++ 애플리케이션에 CVML 기능을 추가합니다
- **기능 결합하기**: 동일한 애플리케이션 내에서 얼굴 감지와 깊이 추정을 연결하여 더욱 풍부한 장면 이해를 구현합니다
- **소스 코드 살펴보기**: 헤더 문서, 추가 샘플 및 API 세부 정보는 [GitHub의 Ryzen AI CVML Library](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library)를 참고하십시오