<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) je súprava nástrojov AMD pre počítačové videnie a strojové učenie v jazyku C++, ktorá poskytuje výkonné funkcie vnímania priamo na zariadení — vrátane odhadu hĺbky, detekcie tváre a sledovania siete bodov tváre. Knižnica je postavená na ovládačoch Ryzen AI a automaticky vyberá najvhodnejší dostupný hardvér (GPU alebo NPU) na vykonávanie inferencie, čo vám umožňuje pridávať funkcie AI do aplikácií v C++ bez nutnosti riešiť trénovanie modelov alebo integráciu s frameworkmi. Celé spracovanie prebieha lokálne vo vašom systéme, vďaka čomu je táto knižnica ideálna pre aplikácie citlivé na súkromie a s nízkou latenciou.

Táto príručka vás naučí, ako nastaviť knižnicu Ryzen AI CVML Library, zostaviť priložené ukážkové aplikácie a spustiť detekciu tváre na ukážkovom obrázku.

## Čo sa naučíte

- Ako nainštalovať predpoklady a nastaviť knižnicu Ryzen AI CVML Library vo vašom systéme
- Ako funguje CVML C++ API: kontexty, objekty funkcií a vyrovnávacie pamäte obrázkov
- Ako zostaviť a spustiť priložené ukážkové aplikácie pomocou CMake a OpenCV
- Ako spustiť detekciu tváre na obrázku s ohraničujúcimi rámčekmi a orientačnými bodmi
- Ako integrovať funkcie CVML do vlastných aplikácií v C++

<!-- @device:halo_box -->

## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov
<!-- @require:driver -->

## Ďalšie závislosti

Pred začatím sa uistite, že máte k dispozícii nasledujúce:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — stiahnite si `opencv-4.11.0-windows.exe`, spustite ho a rozbaľte do lokálneho priečinka (napr. `C:\opencv`)
- [CMake](https://cmake.org/download/) — stiahnite si inštalátor Windows x86-64 MSI a počas inštalácie vyberte možnosť **„Add CMake to the system PATH for all users“**
- [Ovládač Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — nainštalujte najnovšiu dostupnú verziu
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) so záťažou „Desktop development with C++“ (zahŕňa kompilátor MSVC, Windows SDK a nástroje na zostavovanie C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — musí byť zostavené zo zdrojového kódu (balíky apt v Ubuntu 22.04 a 24.04 neposkytujú verziu 4.11). Pozrite si časť [Zostavenie OpenCV zo zdrojového kódu](#building-opencv-from-source) nižšie.
- CMake — nainštalujte pomocou apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 alebo 24.04 (jadro >= 6.11.0-21-generic)
- [Ovládač Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (inštalátor pre Linux — vyžadovaný pre inferenciu na NPU)
- Vulkan SDK (nainštalovaný v časti [Vulkan SDK](#vulkan-sdk) nižšie)
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

## Nastavenie knižnice CVML

Ak ešte nemáte účet AMD, vytvorte si ho na stránke [account.amd.com](https://account.amd.com), potom sa prihláste a stiahnite si knižnicu Ryzen AI CVML Library pomocou odkazu na portál nižšie:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Po stiahnutí rozbaľte balík do lokálneho adresára (napr. `C:\RyzenAI-Library` v systéme Windows alebo `~/RyzenAI-Library` v systéme Linux) a nastavte premennú prostredia `AMD_CVML_SDK_ROOT` na umiestnenie rozbaleného balíka:

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

Balík knižnice obsahuje nasledujúcu štruktúru:

| Priečinok | Obsah |
|--------|----------|
| `cmake/` | Informácie o balení pre funkciu `find_package` nástroja CMake |
| `include/` | Hlavičkové súbory C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` atď.) |
| `windows/` | Binárne súbory pre Windows (súbory `.LIB` na kompiláciu a `.DLL`/`.GRAPHLIB`/`.AMODEL` na behu) |
| `linux/` | Binárne súbory pre Linux (súbory `.SO` na kompiláciu a beh) |
| `samples/` | Jednotlivé ukážkové aplikácie so zdrojovým kódom |

<!-- @os:linux -->

### Nastavenie špecifické pre Linux

#### Zostavenie OpenCV zo zdrojového kódu

Nainštalujte závislosti potrebné na zostavenie OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Stiahnite si, nakonfigurujte a zostavte OpenCV 4.11.0 spolu s modulmi contrib (referencia: [návod na inštaláciu OpenCV pre Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Zdieľané knižnice sa nainštalujú do `<build>/install/lib/`. Adresár `install` použite v ďalších krokoch ako `OPENCV_INSTALL_ROOT`.

#### Vulkan SDK

Nainštalujte Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Ak používate Ubuntu 22.04, aktualizujte aj ovládače MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Ďalšie závislosti pre Ubuntu 24.04

Ak používate Ubuntu 24.04, nainštalujte ďalšie potrebné balíky:

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

## Základné koncepty

Knižnica CVML poskytuje jednoduché C++ API, v ktorom má každá funkcia vnímania (odhad hĺbky, detekcia tváre, sieť bodov tváre) vlastný hlavičkový súbor a objekt funkcie. Nepracujete priamo so surovými modelmi — knižnica automaticky rieši načítanie modelu, predspracovanie aj inferenciu.

### Dostupné funkcie

| Funkcia | Hlavičkový súbor | Popis |
|---------|------------|-------------|
| **Odhad hĺbky** | `cvml-depth-estimation.h` | Generuje mapy hĺbky na úrovni jednotlivých pixelov z RGB obrázkov |
| **Detekcia tváre** | `cvml-face-detector.h` | Deteguje tváre s ohraničujúcimi rámčekmi, orientačnými bodmi (oči, nos, ústa) a mierou spoľahlivosti |
| **Sieť bodov tváre** | `cvml-face-mesh.h` | Sleduje podrobnú geometriu tváre pomocou hustej siete bodov |

### Programovací model

Každá aplikácia CVML sa riadi rovnakým postupom v štyroch krokoch:

1. **Vytvorenie kontextu** — `amd::cvml::Context` spravuje zdieľané zdroje, ako je logovanie a výber back-endu na inferenciu.
2. **Vytvorenie objektu funkcie** — vytvorte inštanciu konkrétnej funkcie (napr. `amd::cvml::DepthEstimation`) v rámci daného kontextu.
3. **Zabalenie vstupných dát** — pomocou `amd::cvml::Image` zapuzdrite svoju vyrovnávaciu pamäť RGB obrázka bez kopírovania dát.
4. **Spustenie** — zavolajte metódu spracovania danej funkcie a prečítajte si výsledky.


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

### Inferenčný backend

Knižnica automaticky vyberie najlepší hardvér (GPU alebo NPU) pre každú operáciu. Backend môžete nastaviť aj explicitne:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Poznámka:** Funkcie, ktoré na operácie NPU používajú backend ONNX, môžu mať pri prvom spustení dlhšiu úvodnú latenciu. Nasledujúce spustenia budú rýchlejšie.

> **Poznámka:** Ak nie je na cieľovom systéme nainštalovaný ovládač NPU, knižnica Ryzen AI CVML automaticky prejde na backend GPU pre inferenčné operácie.

## Zostavenie ukážkových aplikácií

Knižnica CVML obsahuje pripravené ukážkové aplikácie na zostavenie pre každú funkciu. Zostavme ich všetky naraz.

1. Nastavte premennú prostredia `OPENCV_INSTALL_ROOT` tak, aby ukazovala na vašu inštaláciu OpenCV:

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

2. Zostavte ukážky pomocou CMake:

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

   Po úspešnom zostavení sa spustiteľné súbory nachádzajú v:

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

3. Pred spustením akejkoľvek ukážky sa uistite, že sú dostupné súbory za behu (runtime) knižnice CVML:

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

## Spustenie detekcie tvárí

Ukážka detekcie tvárí deteguje tváre na obrázku, videu alebo zo živého kamerového vstupu. Na každej detegovanej tvári vykreslí ohraničujúce rámčeky, hodnoty spoľahlivosti a päť tvárových orientačných bodov (dve oči, nos a dva kútiky úst).

Najprv prejdite do priečinka so spustiteľným súborom detekcie tvárí:

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

Potom si stiahnite ukážkový obrázok, ktorý použijete ako vstup (fotografia od [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), voľne dostupná na použitie cez Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Spustite detekciu tvárí na ukážkovom obrázku:**

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

Zobrazí sa okno s obrázkom, na ktorom sú okolo detegovaných tvárí ohraničujúce rámčeky, hodnoty spoľahlivosti a body tvárových orientačných bodov (oči, nos, kútiky úst).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Uložte anotovaný výstup do súboru:**

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

**Použite presný model** pre vyššiu presnosť (na úkor rýchlosti):

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

Funkcia detekcie tvárí ponúka dva varianty modelu:

| Model | Rýchlosť | Presnosť | Najvhodnejšie pre |
|-------|-------|----------|----------|
| `fast` (predvolený) | Vyšší počet FPS | Dobrá | Aplikácie s kamerou v reálnom čase |
| `precise` | Nižší počet FPS | Najlepšia | Analýza fotografií, požiadavky na vysokú presnosť |


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

## Integrácia CVML do vlastnej aplikácie

Ak chcete použiť knižnicu CVML vo vlastnom projekte v C++, pridajte ju pomocou `find_package` v CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Kde `AMD_CVML_SDK_ROOT` ukazuje na koreňový priečinok knižnice Ryzen AI CVML. Potom zahrňte príslušnú hlavičku pre funkciu, ktorú chcete použiť:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Ďalšie kroky

Pre každú vzorku nižšie najprv prejdite do jej spustiteľného priečinka podľa rovnakého postupu ako v časti [Spustenie detekcie tváre](#running-face-detection) vyššie (napr. `cd build\cvml-sample-depth-estimation\Release` v systéme Windows alebo `cd build/cvml-sample-depth-estimation` v systéme Linux). V systéme Windows pridajte na koniec každého príkazu príponu `.exe` (napr. `cvml-sample-depth-estimation.exe`).

- **Vyskúšajte odhad hĺbky**: Spustite `cvml-sample-depth-estimation -i sample_face.jpg` na vygenerovanie farebnej mapy hĺbky — bližšie objekty sa zobrazujú v teplých farbách, vzdialenejšie v studených farbách
- **Preskúmajte sieť bodov tváre**: Spustite `cvml-sample-face-mesh -i sample_face.jpg`, aby ste videli hustotné sledovanie geometrie tváre s podrobnými bodmi siete
- **Spracovanie video súborov**: Použite prepínače `-i` a `-o` v ľubovoľnej vzorke na spracovanie videí (napr. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Porovnajte varianty modelu**: Vyskúšajte `-m precise` oproti predvolenému `-m fast` pri detekcii tváre a na vlastnej koži spoznajte kompromis medzi presnosťou a rýchlosťou
- **Vytvorte si vlastnú aplikáciu**: Použite integráciu CMake a C++ API na pridanie funkcií CVML do vašich vlastných C++ aplikácií
- **Kombinujte funkcie**: Reťazte detekciu tváre s odhadom hĺbky v rámci tej istej aplikácie pre bohatšie pochopenie scény
- **Prezrite si zdrojový kód**: Prečítajte si [Ryzen AI CVML Library na GitHube](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library), kde nájdete dokumentáciu hlavičkových súborov, ďalšie vzorky a podrobnosti o API