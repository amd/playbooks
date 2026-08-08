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

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) เป็นชุดเครื่องมือคอมพิวเตอร์วิทัศน์และแมชชีนเลิร์นนิงแบบ C++ ของ AMD ที่มอบความสามารถในการรับรู้บนอุปกรณ์ (on-device perception) ที่ทรงพลัง — รวมถึงการประมาณค่าความลึก (depth estimation) การตรวจจับใบหน้า และการติดตามตาข่ายใบหน้า (face mesh tracking) โดยสร้างขึ้นบนไดรเวอร์ Ryzen AI ไลบรารีนี้จะเลือกฮาร์ดแวร์ที่ดีที่สุดที่มีอยู่ (GPU หรือ NPU) สำหรับการอนุมานโดยอัตโนมัติ ทำให้คุณสามารถเพิ่มฟีเจอร์ AI ให้กับแอปพลิเคชัน C++ ได้โดยไม่ต้องกังวลเรื่องการฝึกโมเดลหรือการผสานรวมเฟรมเวิร์ก การประมวลผลทั้งหมดเกิดขึ้นในเครื่องของคุณเอง ทำให้เหมาะอย่างยิ่งสำหรับแอปพลิเคชันที่คำนึงถึงความเป็นส่วนตัวและต้องการเวลาแฝงต่ำ

คู่มือนี้จะสอนวิธีตั้งค่า Ryzen AI CVML Library สร้างแอปพลิเคชันตัวอย่างที่มีให้ และรันการตรวจจับใบหน้าบนภาพตัวอย่าง

## สิ่งที่คุณจะได้เรียนรู้

- วิธีติดตั้งข้อกำหนดเบื้องต้นและตั้งค่า Ryzen AI CVML Library บนระบบของคุณ
- วิธีการทำงานของ CVML C++ API: contexts, feature objects และ image buffers
- วิธีสร้างและรันแอปพลิเคชันตัวอย่างที่มีให้โดยใช้ CMake และ OpenCV
- วิธีรันการตรวจจับใบหน้าบนภาพพร้อมกรอบขอบเขต (bounding boxes) และจุดสังเกต (landmarks)
- วิธีผสานรวมฟีเจอร์ CVML เข้ากับแอปพลิเคชัน C++ ของคุณเอง

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งข้อกำหนดเบื้องต้นของซอฟต์แวร์
<!-- @require:driver -->

## ความต้องการเพิ่มเติม

ก่อนเริ่มต้น ตรวจสอบให้แน่ใจว่าคุณมีสิ่งต่อไปนี้:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — ดาวน์โหลด `opencv-4.11.0-windows.exe` เรียกใช้งาน แล้วแตกไฟล์ไปยังโฟลเดอร์ในเครื่อง (เช่น `C:\opencv`)
- [CMake](https://cmake.org/download/) — ดาวน์โหลดตัวติดตั้ง Windows x86-64 MSI และระหว่างการติดตั้งให้เลือก **"Add CMake to the system PATH for all users"**
- [ไดรเวอร์ Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — ติดตั้งเวอร์ชันล่าสุดที่มีให้
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) พร้อมชุดงาน "Desktop development with C++" (รวมถึงคอมไพเลอร์ MSVC, Windows SDK และเครื่องมือสร้าง C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — ต้องสร้างขึ้นจากซอร์สโค้ด (แพ็กเกจ apt บน Ubuntu 22.04 และ 24.04 ไม่มีเวอร์ชัน 4.11) ดู [การสร้าง OpenCV จากซอร์สโค้ด](#building-opencv-from-source) ด้านล่าง
- CMake — ติดตั้งผ่าน apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 หรือ 24.04 (kernel >= 6.11.0-21-generic)
- [ไดรเวอร์ Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (ตัวติดตั้ง Linux — จำเป็นสำหรับการอนุมานบน NPU)
- Vulkan SDK (ติดตั้งในหัวข้อ [Vulkan SDK](#vulkan-sdk) ด้านล่าง)
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

## การตั้งค่า CVML Library

สร้างบัญชี AMD ที่ [account.amd.com](https://account.amd.com) หากคุณยังไม่มี จากนั้นลงชื่อเข้าใช้เพื่อดาวน์โหลด Ryzen AI CVML Library จากลิงก์พอร์ทัลด้านล่าง:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

หลังจากดาวน์โหลดแล้ว ให้แตกไฟล์แพ็กเกจไปยังไดเรกทอรีในเครื่อง (เช่น `C:\RyzenAI-Library` บน Windows หรือ `~/RyzenAI-Library` บน Linux) และตั้งค่าตัวแปรสภาพแวดล้อม `AMD_CVML_SDK_ROOT` ให้ชี้ไปยังตำแหน่งที่แตกไฟล์:

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

แพ็กเกจไลบรารีมีโครงสร้างดังนี้:

| โฟลเดอร์ | เนื้อหา |
|--------|----------|
| `cmake/` | ข้อมูลการแพ็กเกจสำหรับฟังก์ชัน `find_package` ของ CMake |
| `include/` | ไฟล์ส่วนหัว C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` เป็นต้น) |
| `windows/` | ไฟล์ไบนารีสำหรับ Windows (ไฟล์ `.LIB` สำหรับคอมไพล์ และไฟล์ `.DLL`/`.GRAPHLIB`/`.AMODEL` สำหรับรันไทม์) |
| `linux/` | ไฟล์ไบนารีสำหรับ Linux (ไฟล์ `.SO` สำหรับคอมไพล์และรันไทม์) |
| `samples/` | แอปพลิเคชันตัวอย่างแต่ละรายการพร้อมซอร์สโค้ด |

<!-- @os:linux -->

### การตั้งค่าเฉพาะ Linux

#### การสร้าง OpenCV จากซอร์สโค้ด

ติดตั้งไลบรารีที่จำเป็นสำหรับการสร้าง OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

ดาวน์โหลด กำหนดค่า และสร้าง OpenCV 4.11.0 พร้อมโมดูล contrib (อ้างอิง: [OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

ไลบรารีที่ใช้ร่วมกัน (shared libraries) จะถูกติดตั้งไว้ใต้ `<build>/install/lib/` ใช้ไดเรกทอรี `install` เป็น `OPENCV_INSTALL_ROOT` ในขั้นตอนถัดไป

#### Vulkan SDK

ติดตั้ง Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

หากคุณใช้งาน Ubuntu 22.04 ให้อัปเดตไดรเวอร์ MESA Vulkan ด้วย:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### ข้อกำหนดเพิ่มเติมสำหรับ Ubuntu 24.04

หากคุณใช้งาน Ubuntu 24.04 ให้ติดตั้งแพ็กเกจที่จำเป็นเพิ่มเติม:

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

## แนวคิดหลัก

CVML Library มอบ C++ API ที่เรียบง่าย โดยแต่ละฟีเจอร์การรับรู้ (การประมาณค่าความลึก การตรวจจับใบหน้า face mesh) มีไฟล์ส่วนหัวและออบเจ็กต์ฟีเจอร์เป็นของตัวเอง คุณไม่ต้องทำงานกับโมเดลดิบ — ไลบรารีจัดการการโหลดโมเดล การประมวลผลล่วงหน้า และการอนุมานให้โดยอัตโนมัติ

### ฟีเจอร์ที่มีให้ใช้งาน

| ฟีเจอร์ | ไฟล์ส่วนหัว | คำอธิบาย |
|---------|------------|-------------|
| **การประมาณค่าความลึก** | `cvml-depth-estimation.h` | สร้างแผนที่ความลึกระดับพิกเซล (per-pixel depth maps) จากภาพ RGB |
| **การตรวจจับใบหน้า** | `cvml-face-detector.h` | ตรวจจับใบหน้าพร้อมกรอบขอบเขต จุดสังเกต (ตา จมูก ปาก) และคะแนนความเชื่อมั่น |
| **Face Mesh** | `cvml-face-mesh.h` | ติดตามรายละเอียดโครงสร้างใบหน้าด้วยจุดตาข่ายความละเอียดสูง |

### รูปแบบการเขียนโปรแกรม

ทุกแอปพลิเคชัน CVML ทำตามรูปแบบสี่ขั้นตอนเดียวกัน:

1. **สร้าง Context** — `amd::cvml::Context` จัดการทรัพยากรที่ใช้ร่วมกัน เช่น การบันทึกล็อกและการเลือกแบ็กเอนด์การอนุมาน
2. **สร้าง Feature Object** — สร้างอินสแตนซ์ของฟีเจอร์เฉพาะ (เช่น `amd::cvml::DepthEstimation`) โดยอ้างอิงกับ context
3. **ห่อหุ้มข้อมูลนำเข้า** — ใช้ `amd::cvml::Image` เพื่อห่อหุ้มบัฟเฟอร์ภาพ RGB ของคุณโดยไม่ต้องคัดลอกข้อมูล
4. **ประมวลผล** — เรียกใช้เมธอดการประมวลผลของฟีเจอร์และอ่านผลลัพธ์

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

### แบ็กเอนด์การอนุมาน (Inference Backend)

ไลบรารีจะเลือกฮาร์ดแวร์ที่ดีที่สุด (GPU หรือ NPU) โดยอัตโนมัติสำหรับการทำงานแต่ละอย่าง คุณยังสามารถกำหนดแบ็กเอนด์ได้อย่างชัดเจน:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **หมายเหตุ:** ฟีเจอร์ที่ใช้แบ็กเอนด์ ONNX สำหรับการทำงานบน NPU อาจมีเวลาแฝงในการเริ่มต้นที่นานขึ้นในการรันครั้งแรก การรันครั้งถัดไปจะเร็วขึ้น

> **หมายเหตุ:** หากไม่ได้ติดตั้งไดรเวอร์ NPU บนระบบเป้าหมาย ไลบรารี Ryzen AI CVML จะสลับกลับไปใช้แบ็กเอนด์ GPU สำหรับการทำงานอนุมานโดยอัตโนมัติ

## การสร้างแอปพลิเคชันตัวอย่าง

CVML Library มาพร้อมกับแอปพลิเคชันตัวอย่างที่พร้อมสร้างสำหรับแต่ละฟีเจอร์ มาสร้างทั้งหมดพร้อมกันเลย

1. ตั้งค่าตัวแปรสภาพแวดล้อม `OPENCV_INSTALL_ROOT` ให้ชี้ไปยังตำแหน่งที่ติดตั้ง OpenCV ของคุณ:

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

2. สร้างตัวอย่างด้วย CMake:

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

   หลังจากสร้างสำเร็จแล้ว ไฟล์ปฏิบัติการจะอยู่ที่:

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

3. ก่อนรันตัวอย่างใด ๆ โปรดตรวจสอบให้แน่ใจว่าสามารถเข้าถึงไฟล์รันไทม์ของ CVML ได้:

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

## การรันการตรวจจับใบหน้า

ตัวอย่างการตรวจจับใบหน้าจะตรวจจับใบหน้าในภาพ วิดีโอ หรือฟีดกล้องแบบสด โดยจะวาดกรอบสี่เหลี่ยม คะแนนความเชื่อมั่น และจุดสังเกตใบหน้าห้าจุด (ดวงตาสองข้าง จมูก และมุมปากสองข้าง) บนใบหน้าที่ตรวจพบแต่ละใบหน้า

ก่อนอื่น ให้ไปยังโฟลเดอร์ไฟล์ปฏิบัติการของการตรวจจับใบหน้า:

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

จากนั้นดาวน์โหลดภาพตัวอย่างเพื่อใช้เป็นอินพุต (ภาพถ่ายโดย [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/) ใช้งานได้ฟรีผ่าน Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**รันการตรวจจับใบหน้าบนภาพตัวอย่าง:**

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

หน้าต่างจะปรากฏขึ้นแสดงภาพพร้อมกรอบสี่เหลี่ยมรอบใบหน้าที่ตรวจพบ คะแนนความเชื่อมั่น และจุดสังเกตใบหน้า (ดวงตา จมูก มุมปาก)

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**บันทึกผลลัพธ์ที่มีคำอธิบายประกอบลงไฟล์:**

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

**ใช้โมเดล precise** เพื่อความแม่นยำที่สูงขึ้น (แลกกับความเร็ว):

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

ฟีเจอร์การตรวจจับใบหน้ามีโมเดลให้เลือกสองแบบ:

| โมเดล | ความเร็ว | ความแม่นยำ | เหมาะสำหรับ |
|-------|-------|----------|----------|
| `fast` (ค่าเริ่มต้น) | FPS สูงกว่า | ดี | แอปพลิเคชันกล้องแบบเรียลไทม์ |
| `precise` | FPS ต่ำกว่า | ดีที่สุด | การวิเคราะห์ภาพถ่าย งานที่ต้องการความแม่นยำสูง |


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

## การผสานรวม CVML เข้ากับแอปพลิเคชันของคุณเอง

หากต้องการใช้ CVML Library ในโปรเจกต์ C++ ของคุณเอง ให้เพิ่มผ่าน `find_package` ของ CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

โดยที่ `AMD_CVML_SDK_ROOT` ชี้ไปยังรากของโฟลเดอร์ Ryzen AI CVML Library จากนั้นให้รวมเฮดเดอร์ที่เหมาะสมสำหรับฟีเจอร์ที่คุณต้องการ:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## ขั้นตอนถัดไป

สำหรับตัวอย่างแต่ละตัวด้านล่างนี้ ให้ไปที่โฟลเดอร์ที่เก็บไฟล์ปฏิบัติการก่อน โดยทำตามรูปแบบเดียวกับที่แสดงในส่วน [Running Face Detection](#running-face-detection) ด้านบน (เช่น `cd build\cvml-sample-depth-estimation\Release` บน Windows หรือ `cd build/cvml-sample-depth-estimation` บน Linux) บน Windows ให้เติม `.exe` ต่อท้ายแต่ละคำสั่ง (เช่น `cvml-sample-depth-estimation.exe`)

- **ลองใช้ Depth Estimation**: รันคำสั่ง `cvml-sample-depth-estimation -i sample_face.jpg` เพื่อสร้างแผนที่ความลึกแบบมีสี — วัตถุที่อยู่ใกล้จะแสดงเป็นสีโทนอุ่น ส่วนวัตถุที่อยู่ไกลจะแสดงเป็นสีโทนเย็น
- **สำรวจ Face Mesh**: รันคำสั่ง `cvml-sample-face-mesh -i sample_face.jpg` เพื่อดูการติดตามโครงสร้างใบหน้าแบบละเอียด พร้อมจุดเมชที่ชัดเจน
- **ประมวลผลไฟล์วิดีโอ**: ใช้แฟล็ก `-i` และ `-o` กับตัวอย่างใดก็ได้เพื่อประมวลผลวิดีโอ (เช่น `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **เปรียบเทียบรุ่นของโมเดล**: ลองใช้ `-m precise` เทียบกับค่าเริ่มต้น `-m fast` ในฟีเจอร์ตรวจจับใบหน้า เพื่อดูความแตกต่างระหว่างความแม่นยำและความเร็วด้วยตัวเอง
- **สร้างแอปพลิเคชันของคุณเอง**: ใช้การผสานรวม CMake และ C++ API เพื่อเพิ่มฟีเจอร์ของ CVML เข้าไปในแอปพลิเคชัน C++ ของคุณ
- **รวมฟีเจอร์เข้าด้วยกัน**: เชื่อมต่อการตรวจจับใบหน้าเข้ากับ Depth Estimation ในแอปพลิเคชันเดียวกันเพื่อความเข้าใจฉากที่สมบูรณ์ยิ่งขึ้น
- **ดูซอร์สโค้ด**: อ่าน [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) สำหรับเอกสารส่วนหัว ตัวอย่างเพิ่มเติม และรายละเอียด API