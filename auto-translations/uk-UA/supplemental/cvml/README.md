<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

[Бібліотека Ryzen AI CVML](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) — це набір інструментів AMD на C++ для комп’ютерного зору та машинного навчання, який надає потужні можливості локального сприйняття, зокрема оцінку глибини, виявлення обличчя та відстеження сітки обличчя. Побудована на основі драйверів Ryzen AI, бібліотека автоматично обирає найкраще доступне апаратне забезпечення (GPU або NPU) для інференсу, дозволяючи додавати функції штучного інтелекту до застосунків на C++ без необхідності турбуватися про навчання моделей чи інтеграцію фреймворків. Уся обробка відбувається локально на вашій системі, що робить бібліотеку ідеальною для застосунків, чутливих до конфіденційності та затримок.

Цей посібник навчить вас налаштовувати бібліотеку Ryzen AI CVML, збирати включені зразки застосунків і виконувати виявлення обличчя на прикладі зображення.

## Що ви дізнаєтесь

- Як встановити необхідні передумови та налаштувати бібліотеку Ryzen AI CVML на вашій системі
- Як працює C++ API CVML: контексти, об’єкти функцій та буфери зображень
- Як зібрати та запустити включені зразки застосунків за допомогою CMake та OpenCV
- Як виконати виявлення обличчя на зображенні з обмежувальними рамками та ключовими точками
- Як інтегрувати функції CVML у власні застосунки на C++

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення
<!-- @require:driver -->

## Додаткові залежності

Перш ніж почати, переконайтеся, що у вас є наступне:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — завантажте `opencv-4.11.0-windows.exe`, запустіть його та розпакуйте в локальну папку (наприклад, `C:\opencv`)
- [CMake](https://cmake.org/download/) — завантажте інсталятор Windows x86-64 MSI та під час встановлення оберіть **"Add CMake to the system PATH for all users"**
- [Драйвер Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — встановіть найновішу доступну версію
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) з навантаженням "Desktop development with C++" (включає компілятор MSVC, Windows SDK та інструменти збирання C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — потрібно збирати з вихідного коду (пакети apt в Ubuntu 22.04 та 24.04 не надають версію 4.11). Див. розділ [Building OpenCV from Source](#building-opencv-from-source) нижче.
- CMake — встановіть через apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 або 24.04 (ядро >= 6.11.0-21-generic)
- [Драйвер Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (інсталятор для Linux — необхідний для інференсу на NPU)
- Vulkan SDK (встановлюється в розділі [Vulkan SDK](#vulkan-sdk) нижче)
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

## Налаштування бібліотеки CVML

Створіть обліковий запис AMD на сайті [account.amd.com](https://account.amd.com), якщо у вас його немає, потім увійдіть, щоб завантажити бібліотеку Ryzen AI CVML за посиланням на портал нижче:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Після завантаження розпакуйте пакет у локальний каталог (наприклад, `C:\RyzenAI-Library` у Windows або `~/RyzenAI-Library` у Linux) і встановіть змінну середовища `AMD_CVML_SDK_ROOT` у місце розташування розпакованих файлів:

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

Пакет бібліотеки містить наступну структуру:

| Папка | Вміст |
|--------|----------|
| `cmake/` | Інформація про пакування для функції `find_package` CMake |
| `include/` | Файли заголовків C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` тощо) |
| `windows/` | Бінарні файли для Windows (файли `.LIB` для компіляції та `.DLL`/`.GRAPHLIB`/`.AMODEL` для виконання) |
| `linux/` | Бінарні файли для Linux (файли `.SO` для компіляції та виконання) |
| `samples/` | Окремі зразки застосунків з вихідним кодом |

<!-- @os:linux -->

### Специфічне налаштування для Linux

#### Збирання OpenCV з вихідного коду

Встановіть залежності для збирання OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Завантажте, налаштуйте та зберіть OpenCV 4.11.0 з модулями contrib (посилання: [OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Спільні бібліотеки встановлюються в `<build>/install/lib/`. Використовуйте каталог `install` як `OPENCV_INSTALL_ROOT` у наступних кроках.

#### Vulkan SDK

Встановіть Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Якщо ви використовуєте Ubuntu 22.04, також оновіть драйвери MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Додаткові залежності для Ubuntu 24.04

Якщо ви використовуєте Ubuntu 24.04, встановіть додаткові необхідні пакети:

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

## Основні концепції

Бібліотека CVML надає простий C++ API, де кожна функція сприйняття (оцінка глибини, виявлення обличчя, сітка обличчя) має власний файл заголовка та об’єкт функції. Вам не потрібно працювати з необробленими моделями — бібліотека автоматично обробляє завантаження моделей, попередню обробку та інференс.

### Доступні функції

| Функція | Файл заголовка | Опис |
|---------|------------|-------------|
| **Оцінка глибини** | `cvml-depth-estimation.h` | Генерує попіксельні карти глибини з RGB-зображень |
| **Виявлення обличчя** | `cvml-face-detector.h` | Виявляє обличчя з обмежувальними рамками, ключовими точками (очі, ніс, рот) та показниками впевненості |
| **Сітка обличчя** | `cvml-face-mesh.h` | Відстежує детальну геометрію обличчя за допомогою щільних точок сітки |

### Модель програмування

Кожен застосунок CVML дотримується того самого чотирикрокового шаблону:

1. **Створення контексту** — `amd::cvml::Context` керує спільними ресурсами, такими як логування та вибір бекенда для інференсу.
2. **Створення об’єкта функції** — Створіть екземпляр конкретної функції (наприклад, `amd::cvml::DepthEstimation`) на основі контексту.
3. **Обгортання вхідних даних** — Використовуйте `amd::cvml::Image`, щоб інкапсулювати ваш буфер RGB-зображення без копіювання даних.
4. **Виконання** — Викличте метод обробки функції та отримайте результати.

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

### Бекенд для інференсу

Бібліотека автоматично вибирає найкраще апаратне забезпечення (GPU або NPU) для кожної операції. Ви також можете задати бекенд явно:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Примітка.** Функції, які використовують бекенд ONNX для операцій NPU, можуть мати довшу затримку запуску під час першого виконання. Наступні запуски будуть швидшими.

> **Примітка.** Якщо драйвер NPU не встановлено в цільовій системі, бібліотека Ryzen AI CVML автоматично переключиться на бекенд GPU для операцій інференсу.

## Збірка прикладних застосунків

Бібліотека CVML містить готові до збірки прикладні застосунки для кожної функції. Зберемо їх усі одразу.

1. Встановіть змінну середовища `OPENCV_INSTALL_ROOT`, щоб вона вказувала на вашу інсталяцію OpenCV:

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

2. Зберіть приклади за допомогою CMake:

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

   Після успішної збірки виконувані файли знаходяться тут:

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

3. Перед запуском будь-якого прикладу переконайтеся, що файли середовища виконання CVML доступні:

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

## Запуск виявлення облич

Приклад виявлення облич розпізнає обличчя на зображенні, відео або потоці з відеокамери в реальному часі. Він малює обмежувальні рамки, показники впевненості та п'ять контрольних точок обличчя (два ока, ніс і два краї рота) для кожного виявленого обличчя.

Спочатку перейдіть до папки з виконуваним файлом виявлення облич:

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

Потім завантажте приклад зображення для використання як вхідних даних (фото від [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), доступне для вільного використання через Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Запустіть виявлення облич на прикладі зображення:**

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

З'явиться вікно із зображенням, на якому показані обмежувальні рамки навколо виявлених облич, показники впевненості та точки контрольних ознак обличчя (очі, ніс, краї рота).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Збережіть анотований результат у файл:**

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

**Використайте точну модель** для вищої точності (ціною швидкості):

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

Функція виявлення облич пропонує два варіанти моделей:

| Модель | Швидкість | Точність | Найкраще підходить для |
|-------|-------|----------|----------|
| `fast` (за замовчуванням) | Вища частота кадрів | Добра | Застосунків з камерою в реальному часі |
| `precise` | Нижча частота кадрів | Найкраща | Аналізу фотографій, потреб у високій точності |


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

## Інтеграція CVML у власний застосунок

Щоб використовувати бібліотеку CVML у власному проєкті C++, додайте її за допомогою `find_package` з CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Де `AMD_CVML_SDK_ROOT` вказує на кореневу папку бібліотеки Ryzen AI CVML. Потім підключіть відповідний заголовковий файл для потрібної функції:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Наступні кроки

Для кожного прикладу нижче спершу перейдіть до відповідної виконуваної папки, дотримуючись того самого шаблону, що й у розділі [Running Face Detection](#running-face-detection) вище (наприклад, `cd build\cvml-sample-depth-estimation\Release` у Windows або `cd build/cvml-sample-depth-estimation` у Linux). У Windows додайте `.exe` до кожної команди (наприклад, `cvml-sample-depth-estimation.exe`).

- **Спробуйте оцінку глибини**: виконайте `cvml-sample-depth-estimation -i sample_face.jpg`, щоб згенерувати кольорову карту глибини — ближчі об’єкти відображаються теплими кольорами, а віддалені — холодними
- **Дослідіть Face Mesh**: виконайте `cvml-sample-face-mesh -i sample_face.jpg`, щоб побачити щільне відстеження геометрії обличчя з детальними точками сітки
- **Обробляйте відеофайли**: використовуйте прапорці `-i` та `-o` у будь-якому прикладі для обробки відео (наприклад, `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Порівняйте варіанти моделі**: спробуйте `-m precise` замість стандартного `-m fast` у виявленні облич, щоб на власні очі побачити компроміс між точністю та швидкістю
- **Створіть власний застосунок**: використовуйте інтеграцію CMake та C++ API, щоб додати можливості CVML до власних застосунків на C++
- **Поєднуйте функції**: об’єднайте виявлення облич з оцінкою глибини в одному застосунку для глибшого розуміння сцени
- **Перегляньте вихідний код**: ознайомтеся з [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library), щоб отримати документацію заголовкових файлів, додаткові приклади та деталі API