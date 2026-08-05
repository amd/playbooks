<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) — это набор инструментов AMD на C++ для компьютерного зрения и машинного обучения, предоставляющий мощные возможности обработки данных на устройстве, включая оценку глубины, обнаружение лиц и отслеживание сетки лица. Библиотека построена поверх драйверов Ryzen AI и автоматически выбирает наилучшее доступное оборудование (GPU или NPU) для инференса, позволяя добавлять функции ИИ в приложения на C++ без необходимости заниматься обучением моделей или интеграцией с фреймворками. Вся обработка выполняется локально на вашей системе, что делает её идеальным решением для приложений с высокими требованиями к конфиденциальности и низкой задержке.

Этот плейбук научит вас настраивать Ryzen AI CVML Library, собирать входящие в комплект примеры приложений и выполнять обнаружение лиц на тестовом изображении.

## Чему вы научитесь

- Как установить необходимые компоненты и настроить Ryzen AI CVML Library в своей системе
- Как работает C++ API CVML: контексты, объекты функций и буферы изображений
- Как собирать и запускать входящие в комплект примеры приложений с помощью CMake и OpenCV
- Как выполнять обнаружение лиц на изображении с отображением ограничивающих рамок и ключевых точек
- Как интегрировать функции CVML в собственные приложения на C++

<!-- @device:halo_box -->
## Проверка наличия обновлений ПО

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого ПО
<!-- @require:driver -->

## Дополнительные зависимости

Перед началом убедитесь, что у вас есть следующее:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — скачайте `opencv-4.11.0-windows.exe`, запустите его и распакуйте в локальную папку (например, `C:\opencv`)
- [CMake](https://cmake.org/download/) — скачайте установщик Windows x86-64 MSI и во время установки выберите **«Add CMake to the system PATH for all users»**
- [Драйвер Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — установите последнюю доступную версию
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) с рабочей нагрузкой «Desktop development with C++» (включает компилятор MSVC, Windows SDK и инструменты сборки C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — необходимо собрать из исходного кода (пакеты apt в Ubuntu 22.04 и 24.04 не предоставляют версию 4.11). См. раздел [Сборка OpenCV из исходного кода](#building-opencv-from-source) ниже.
- CMake — установите через apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 или 24.04 (ядро >= 6.11.0-21-generic)
- [Драйвер Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (установщик для Linux — требуется для инференса на NPU)
- Vulkan SDK (устанавливается в разделе [Vulkan SDK](#vulkan-sdk) ниже)
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

## Настройка CVML Library

Создайте учётную запись AMD на [account.amd.com](https://account.amd.com), если у вас её ещё нет, затем войдите в систему, чтобы скачать Ryzen AI CVML Library по ссылке на портал ниже:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

После скачивания распакуйте пакет в локальный каталог (например, `C:\RyzenAI-Library` в Windows или `~/RyzenAI-Library` в Linux) и задайте переменную окружения `AMD_CVML_SDK_ROOT`, указав путь к распакованному каталогу:

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

Пакет библиотеки содержит следующую структуру:

| Папка | Содержимое |
|--------|----------|
| `cmake/` | Информация для упаковки, используемая функцией `find_package` в CMake |
| `include/` | Файлы заголовков C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` и т. д.) |
| `windows/` | Бинарные файлы для Windows (файлы `.LIB` для компиляции и `.DLL`/`.GRAPHLIB`/`.AMODEL` для выполнения) |
| `linux/` | Бинарные файлы для Linux (файлы `.SO` для компиляции и выполнения) |
| `samples/` | Отдельные примеры приложений с исходным кодом |

<!-- @os:linux -->

### Настройка, специфичная для Linux

#### Сборка OpenCV из исходного кода

Установите зависимости, необходимые для сборки OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Скачайте, настройте и соберите OpenCV 4.11.0 с модулями contrib (справка: [руководство по установке OpenCV в Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Общие библиотеки устанавливаются в каталог `<build>/install/lib/`. Используйте каталог `install` в качестве `OPENCV_INSTALL_ROOT` на следующих этапах.

#### Vulkan SDK

Установите Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Если вы используете Ubuntu 22.04, также обновите драйверы MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Дополнительные зависимости для Ubuntu 24.04

Если вы используете Ubuntu 24.04, установите дополнительные необходимые пакеты:

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

## Основные концепции

CVML Library предоставляет простой C++ API, в котором каждая функция обработки восприятия (оценка глубины, обнаружение лиц, сетка лица) имеет собственный файл заголовка и объект функции. Вам не нужно работать с исходными моделями — библиотека автоматически берёт на себя загрузку моделей, предварительную обработку и инференс.

### Доступные функции

| Функция | Файл заголовка | Описание |
|---------|------------|-------------|
| **Оценка глубины** | `cvml-depth-estimation.h` | Формирует попиксельные карты глубины на основе RGB-изображений |
| **Обнаружение лиц** | `cvml-face-detector.h` | Обнаруживает лица с ограничивающими рамками, ключевыми точками (глаза, нос, рот) и оценками достоверности |
| **Сетка лица** | `cvml-face-mesh.h` | Отслеживает детализированную геометрию лица с помощью плотных точек сетки |

### Модель программирования

Каждое приложение CVML следует одному и тому же шаблону из четырёх шагов:

1. **Создание контекста** — `amd::cvml::Context` управляет общими ресурсами, такими как логирование и выбор бэкенда инференса.
2. **Создание объекта функции** — создайте экземпляр конкретной функции (например, `amd::cvml::DepthEstimation`) на основе контекста.
3. **Обёртка входных данных** — используйте `amd::cvml::Image`, чтобы инкапсулировать буфер RGB-изображения без копирования данных.
4. **Выполнение** — вызовите метод обработки функции и прочитайте результаты.

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

### Бэкенд для инференса

Библиотека автоматически выбирает наилучшее оборудование (GPU или NPU) для каждой операции. Вы также можете задать бэкенд явно:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Примечание.** Функции, использующие бэкенд ONNX для операций NPU, могут демонстрировать более длительную задержку запуска при первом выполнении. Последующие запуски будут выполняться быстрее.

> **Примечание.** Если драйвер NPU не установлен в целевой системе, библиотека Ryzen AI CVML автоматически переключится на бэкенд GPU для операций инференса.

## Сборка примеров приложений

Библиотека CVML включает готовые к сборке примеры приложений для каждой функции. Соберём их все сразу.

1. Установите переменную окружения `OPENCV_INSTALL_ROOT`, указывающую на вашу установку OpenCV:

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

2. Соберите примеры с помощью CMake:

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

   После успешной сборки исполняемые файлы будут находиться здесь:

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

3. Перед запуском любого примера убедитесь, что файлы среды выполнения CVML доступны:

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

## Запуск определения лиц

Пример определения лиц обнаруживает лица на изображении, видео или в потоке с камеры в реальном времени. Он рисует ограничивающие рамки, оценки уверенности и пять лицевых ориентиров (два глаза, нос и два края рта) для каждого обнаруженного лица.

Сначала перейдите в папку с исполняемым файлом определения лиц:

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

Затем скачайте пример изображения для использования в качестве входных данных (фото от [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), свободно для использования через Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Запустите определение лиц на примере изображения:**

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

Появится окно с изображением, на котором показаны ограничивающие рамки вокруг обнаруженных лиц, оценки уверенности и точки лицевых ориентиров (глаза, нос, края рта).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Сохраните аннотированный результат в файл:**

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

**Используйте точную модель** для более высокой точности (ценой скорости):

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

Функция определения лиц предлагает два варианта модели:

| Модель | Скорость | Точность | Лучше всего подходит для |
|-------|-------|----------|----------|
| `fast` (по умолчанию) | Более высокий FPS | Хорошая | Приложений с камерой в реальном времени |
| `precise` | Более низкий FPS | Наилучшая | Анализа фотографий, задач с высокими требованиями к точности |


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

## Интеграция CVML в собственное приложение

Чтобы использовать библиотеку CVML в вашем собственном проекте на C++, подключите её через `find_package` в CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Где `AMD_CVML_SDK_ROOT` указывает на корень папки библиотеки Ryzen AI CVML. Затем подключите соответствующий заголовочный файл для нужной вам функции:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Дальнейшие шаги

Для каждого примера ниже сначала перейдите в его исполняемую папку, следуя той же схеме, что и в разделе [Running Face Detection](#running-face-detection) выше (например, `cd build\cvml-sample-depth-estimation\Release` в Windows или `cd build/cvml-sample-depth-estimation` в Linux). В Windows добавьте `.exe` к каждой команде (например, `cvml-sample-depth-estimation.exe`).

- **Попробуйте оценку глубины**: Запустите `cvml-sample-depth-estimation -i sample_face.jpg`, чтобы сгенерировать цветную карту глубины — более близкие объекты отображаются тёплыми цветами, более удалённые — холодными
- **Изучите сетку лица**: Запустите `cvml-sample-face-mesh -i sample_face.jpg`, чтобы увидеть плотное отслеживание геометрии лица с детализированными точками сетки
- **Обрабатывайте видеофайлы**: Используйте флаги `-i` и `-o` для любого примера, чтобы обрабатывать видео (например, `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Сравните варианты моделей**: Попробуйте `-m precise` вместо `-m fast` по умолчанию при обнаружении лиц, чтобы на практике увидеть компромисс между точностью и скоростью
- **Создайте собственное приложение**: Используйте интеграцию с CMake и C++ API, чтобы добавить функции CVML в собственные приложения на C++
- **Комбинируйте функции**: Объедините обнаружение лиц с оценкой глубины в одном приложении для более полного понимания сцены
- **Изучите исходный код**: Ознакомьтесь с [Ryzen AI CVML Library на GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library), где представлена документация по заголовочным файлам, дополнительные примеры и подробности API