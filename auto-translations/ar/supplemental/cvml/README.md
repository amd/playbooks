<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

تُعد [مكتبة Ryzen AI CVML](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) مجموعة أدوات AMD للرؤية الحاسوبية والتعلم الآلي بلغة C++، توفر قدرات إدراك قوية تعمل مباشرة على الجهاز — بما في ذلك تقدير العمق، والكشف عن الوجوه، وتتبع شبكة الوجه. مبنية فوق برامج تشغيل Ryzen AI، تقوم المكتبة تلقائيًا باختيار أفضل عتاد متاح (GPU أو NPU) لعملية الاستدلال، مما يتيح لك إضافة ميزات الذكاء الاصطناعي إلى تطبيقات C++ دون القلق بشأن تدريب النماذج أو التكامل مع أطر العمل. تتم كل عمليات المعالجة محليًا على نظامك، مما يجعلها مثالية للتطبيقات الحساسة للخصوصية ذات زمن الاستجابة المنخفض.

يعلّمك هذا الدليل كيفية إعداد مكتبة Ryzen AI CVML، وبناء تطبيقات العينة المرفقة، وتشغيل الكشف عن الوجوه على صورة نموذجية.

## ما ستتعلمه

- كيفية تثبيت المتطلبات الأساسية وإعداد مكتبة Ryzen AI CVML على نظامك
- كيفية عمل واجهة برمجة تطبيقات CVML بلغة C++: السياقات (contexts)، وكائنات الميزات (feature objects)، ومخازن الصور (image buffers)
- كيفية بناء وتشغيل تطبيقات العينة المرفقة باستخدام CMake وOpenCV
- كيفية تشغيل الكشف عن الوجوه على صورة مع مربعات الإحاطة والمعالم
- كيفية دمج ميزات CVML في تطبيقات C++ الخاصة بك

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج
<!-- @require:driver -->

## المتطلبات الإضافية

قبل البدء، تأكد من توفر ما يلي:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — قم بتنزيل `opencv-4.11.0-windows.exe`، وشغّله، واستخرجه إلى مجلد محلي (مثل `C:\opencv`)
- [CMake](https://cmake.org/download/) — قم بتنزيل مثبّت MSI لنظام Windows x86-64 وأثناء التثبيت اختر **"Add CMake to the system PATH for all users"**
- [برنامج تشغيل Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — قم بتثبيت أحدث إصدار متاح
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) مع حزمة عمل "Desktop development with C++" (تتضمن مترجم MSVC، وWindows SDK، وأدوات بناء C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — يجب بناؤه من المصدر (حزم apt على Ubuntu 22.04 و24.04 لا توفر الإصدار 4.11). راجع [بناء OpenCV من المصدر](#building-opencv-from-source) أدناه.
- CMake — قم بتثبيته عبر apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 أو 24.04 (النواة >= 6.11.0-21-generic)
- [برنامج تشغيل Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (مثبّت Linux — مطلوب لاستدلال NPU)
- Vulkan SDK (يُثبَّت في قسم [Vulkan SDK](#vulkan-sdk) أدناه)
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

## إعداد مكتبة CVML

أنشئ حساب AMD على [account.amd.com](https://account.amd.com) إذا لم يكن لديك حساب، ثم سجّل الدخول لتنزيل مكتبة Ryzen AI CVML من رابط البوابة أدناه:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

بعد التنزيل، استخرج الحزمة إلى دليل محلي (مثل `C:\RyzenAI-Library` على Windows أو `~/RyzenAI-Library` على Linux) وقم بتعيين متغير البيئة `AMD_CVML_SDK_ROOT` إلى الموقع المستخرج إليه:

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

تحتوي حزمة المكتبة على البنية التالية:

| المجلد | المحتويات |
|--------|----------|
| `cmake/` | معلومات التعبئة لدالة `find_package` الخاصة بـ CMake |
| `include/` | ملفات رأس C++ (`cvml-depth-estimation.h`، `cvml-face-detector.h`، `cvml-face-mesh.h`، إلخ) |
| `windows/` | ملفات ثنائية لنظام Windows (ملفات `.LIB` وقت الترجمة و`.DLL`/`.GRAPHLIB`/`.AMODEL` وقت التشغيل) |
| `linux/` | ملفات ثنائية لنظام Linux (ملفات `.SO` وقت الترجمة والتشغيل) |
| `samples/` | تطبيقات عينة فردية مع الشيفرة المصدرية |

<!-- @os:linux -->

### الإعداد الخاص بنظام Linux

#### بناء OpenCV من المصدر

قم بتثبيت متطلبات بناء OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

قم بتنزيل وإعداد وبناء OpenCV 4.11.0 مع وحدات contrib (مرجع: [درس تثبيت OpenCV على Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

يتم تثبيت المكتبات المشتركة تحت `<build>/install/lib/`. استخدم دليل `install` كـ `OPENCV_INSTALL_ROOT` في الخطوات اللاحقة.

#### Vulkan SDK

قم بتثبيت Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

إذا كنت تستخدم Ubuntu 22.04، قم أيضًا بتحديث برامج تشغيل MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### متطلبات إضافية لنظام Ubuntu 24.04

إذا كنت تستخدم Ubuntu 24.04، قم بتثبيت الحزم الإضافية المطلوبة:

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

## المفاهيم الأساسية

توفر مكتبة CVML واجهة برمجة تطبيقات بسيطة بلغة C++ حيث تمتلك كل ميزة إدراك (تقدير العمق، الكشف عن الوجوه، شبكة الوجه) ملف رأس خاصًا بها وكائن ميزة خاصًا بها. لا تتعامل مع النماذج الخام مباشرة — تتولى المكتبة تحميل النموذج والمعالجة المسبقة والاستدلال تلقائيًا.

### الميزات المتاحة

| الميزة | ملف الرأس | الوصف |
|---------|------------|-------------|
| **تقدير العمق** | `cvml-depth-estimation.h` | يولّد خرائط عمق لكل بكسل من الصور RGB |
| **الكشف عن الوجوه** | `cvml-face-detector.h` | يكتشف الوجوه مع مربعات الإحاطة، والمعالم (العينان، الأنف، الفم)، ودرجات الثقة |
| **شبكة الوجه** | `cvml-face-mesh.h` | يتتبع هندسة الوجه التفصيلية بنقاط شبكة كثيفة |

### نموذج البرمجة

يتبع كل تطبيق CVML نفس النمط المكوّن من أربع خطوات:

1. **إنشاء سياق (Context)** — يدير `amd::cvml::Context` الموارد المشتركة مثل التسجيل (logging) واختيار خلفية الاستدلال.
2. **إنشاء كائن ميزة (Feature Object)** — قم بإنشاء نسخة من الميزة المحددة (مثل `amd::cvml::DepthEstimation`) مرتبطة بالسياق.
3. **تغليف بيانات الإدخال** — استخدم `amd::cvml::Image` لتغليف مخزن صورة RGB الخاص بك دون نسخ البيانات.
4. **التنفيذ** — استدعِ طريقة معالجة الميزة واقرأ النتائج.

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

### الواجهة الخلفية للاستدلال

تختار المكتبة تلقائيًا أفضل عتاد (GPU أو NPU) لكل عملية. يمكنك أيضًا تحديد الواجهة الخلفية بشكل صريح:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```


> **ملاحظة:** قد تعاني الميزات التي تستخدم الواجهة الخلفية ONNX لعمليات NPU من زمن استجابة أطول عند بدء التشغيل في أول تشغيل. أما عمليات التشغيل اللاحقة فستكون أسرع.

> **ملاحظة:** إذا لم يكن مُشغّل NPU مثبتًا على النظام المستهدف، فستعود مكتبة Ryzen AI CVML تلقائيًا إلى استخدام الواجهة الخلفية GPU لعمليات الاستدلال.

## بناء التطبيقات النموذجية

تتضمن مكتبة CVML تطبيقات نموذجية جاهزة للبناء لكل ميزة. لنقم ببنائها جميعًا مرة واحدة.

1. عيّن متغيّر البيئة `OPENCV_INSTALL_ROOT` بحيث يشير إلى تثبيت OpenCV الخاص بك:

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

2. ابنِ التطبيقات النموذجية باستخدام CMake:

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

   بعد نجاح عملية البناء، ستجد الملفات التنفيذية في المسارات التالية:

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

3. قبل تشغيل أي تطبيق نموذجي، تأكد من أن ملفات وقت التشغيل الخاصة بـ CVML متاحة:

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

## تشغيل ميزة اكتشاف الوجه

يقوم التطبيق النموذجي لاكتشاف الوجه باكتشاف الوجوه في صورة أو فيديو أو بث كاميرا مباشر. وهو يرسم مربعات إحاطة ودرجات ثقة وخمس معالم للوجه (عينان وأنف وحافتا الفم) على كل وجه تم اكتشافه.

أولًا، انتقل إلى مجلد الملف التنفيذي لاكتشاف الوجه:

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

بعد ذلك، قم بتنزيل صورة نموذجية لاستخدامها كمُدخل (صورة بواسطة [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/)، متاحة للاستخدام المجاني عبر Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**تشغيل اكتشاف الوجه على الصورة النموذجية:**

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

ستظهر نافذة تعرض الصورة مع مربعات إحاطة حول الوجوه المكتشفة، ودرجات الثقة، ونقاط معالم الوجه (العينان والأنف وحافتا الفم).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**حفظ المُخرَج المُشروح في ملف:**

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

**استخدام النموذج الدقيق** لتحقيق دقة أعلى (على حساب السرعة):

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

توفر ميزة اكتشاف الوجه نسختين من النموذج:

| النموذج | السرعة | الدقة | الأنسب لـ |
|-------|-------|----------|----------|
| `fast` (افتراضي) | معدل إطارات أعلى | جيدة | تطبيقات الكاميرا في الوقت الفعلي |
| `precise` | معدل إطارات أقل | الأفضل | تحليل الصور، الاحتياجات ذات الدقة العالية |


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

## دمج CVML في تطبيقك الخاص

لاستخدام مكتبة CVML في مشروع C++ الخاص بك، أضفها عبر `find_package` الخاص بـ CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

حيث تشير `AMD_CVML_SDK_ROOT` إلى الجذر الخاص بمجلد مكتبة Ryzen AI CVML. ثم قم بتضمين الترويسة (header) المناسبة للميزة التي تريد استخدامها:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## الخطوات التالية

لكل عينة أدناه، انتقل أولاً إلى مجلدها التنفيذي، باتباع نفس النمط الموضح في قسم [Running Face Detection](#running-face-detection) أعلاه (على سبيل المثال `cd build\cvml-sample-depth-estimation\Release` على Windows أو `cd build/cvml-sample-depth-estimation` على Linux). على Windows، أضف `.exe` إلى كل أمر (على سبيل المثال `cvml-sample-depth-estimation.exe`).

- **جرّب تقدير العمق**: شغّل `cvml-sample-depth-estimation -i sample_face.jpg` لإنشاء خريطة عمق ملوّنة — تظهر الأجسام الأقرب بألوان دافئة، والأجسام البعيدة بألوان باردة
- **استكشف Face Mesh**: شغّل `cvml-sample-face-mesh -i sample_face.jpg` لرؤية تتبع هندسة الوجه الكثيفة مع نقاط شبكية مفصّلة
- **معالجة ملفات الفيديو**: استخدم العلامتين `-i` و `-o` مع أي عينة لمعالجة الفيديوهات (على سبيل المثال، `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **قارن بين متغيرات النموذج**: جرّب `-m precise` مقابل الافتراضي `-m fast` في كشف الوجه لترى الفرق بين الدقة والسرعة بنفسك
- **ابنِ تطبيقك الخاص**: استخدم تكامل CMake وواجهة C++ لإضافة ميزات CVML إلى تطبيقات C++ الخاصة بك
- **ادمج الميزات**: اربط كشف الوجه مع تقدير العمق في نفس التطبيق لفهم أغنى للمشهد
- **تصفّح الكود المصدري**: اقرأ [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) للاطلاع على توثيق الترويسات (headers)، وعينات إضافية، وتفاصيل واجهة البرمجة API