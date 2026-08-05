<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

A [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) egy AMD C++ számítógépes látás és gépi tanulási eszközkészlet, amely nagy teljesítményű, eszközön futó észlelési képességeket biztosít — beleértve a mélységbecslést, arcfelismerést és archáló-követést. A Ryzen AI illesztőprogramokra épülve a könyvtár automatikusan kiválasztja a következtetéshez rendelkezésre álló legjobb hardvert (GPU vagy NPU), így AI-funkciókat adhatsz C++ alkalmazásaidhoz anélkül, hogy modellbetanítással vagy keretrendszer-integrációval kellene foglalkoznod. Minden feldolgozás helyben, a rendszereden történik, így ideális választás adatvédelem szempontjából érzékeny, alacsony késleltetést igénylő alkalmazásokhoz.

Ez a playbook megtanítja, hogyan állítsd be a Ryzen AI CVML Library-t, hogyan fordítsd le a mellékelt mintaalkalmazásokat, és hogyan futtass arcfelismerést egy mintaképen.

## Amit tanulni fogsz

- Hogyan telepítsd az előfeltételeket, és hogyan állítsd be a Ryzen AI CVML Library-t a rendszereden
- Hogyan működik a CVML C++ API: kontextusok, funkcióobjektumok és képpufferek
- Hogyan fordítsd le és futtasd a mellékelt mintaalkalmazásokat CMake és OpenCV segítségével
- Hogyan futtass arcfelismerést egy képen, körülhatároló dobozokkal és jellemzőpontokkal
- Hogyan integráld a CVML funkciókat saját C++ alkalmazásaidba

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése
<!-- @require:driver -->

## További függőségek

Mielőtt elkezdenéd, győződj meg róla, hogy rendelkezésedre áll a következő:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — töltsd le az `opencv-4.11.0-windows.exe` fájlt, futtasd, és csomagold ki egy helyi mappába (pl. `C:\opencv`)
- [CMake](https://cmake.org/download/) — töltsd le a Windows x86-64 MSI telepítőt, és a telepítés során válaszd az **"Add CMake to the system PATH for all users"** opciót
- [Ryzen AI NPU illesztőprogram](https://ryzenai.docs.amd.com/en/latest/inst.html) — telepítsd a legújabb elérhető verziót
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) a "Desktop development with C++" munkaterhelés-csomaggal (tartalmazza az MSVC fordítót, a Windows SDK-t és a C++ build eszközöket)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — forrásból kell lefordítani (az Ubuntu 22.04 és 24.04 apt csomagjai nem tartalmazzák a 4.11-es verziót). Lásd az alábbi [OpenCV fordítása forrásból](#building-opencv-from-source) szakaszt.
- CMake — telepítsd apt segítségével:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 vagy 24.04 (kernel >= 6.11.0-21-generic)
- [Ryzen AI NPU illesztőprogram](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (Linux telepítő — szükséges az NPU-alapú következtetéshez)
- Vulkan SDK (az alábbi [Vulkan SDK](#vulkan-sdk) szakaszban telepítve)
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

## A CVML Library beállítása

Hozz létre egy AMD fiókot az [account.amd.com](https://account.amd.com) oldalon, ha még nincs, majd jelentkezz be, hogy letöltsd a Ryzen AI CVML Library-t az alábbi portál linkről:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

A letöltés után csomagold ki a csomagot egy helyi könyvtárba (pl. `C:\RyzenAI-Library` Windows alatt vagy `~/RyzenAI-Library` Linux alatt), és állítsd be az `AMD_CVML_SDK_ROOT` környezeti változót a kicsomagolt helyre:

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

A könyvtárcsomag a következő struktúrát tartalmazza:

| Mappa | Tartalom |
|--------|----------|
| `cmake/` | Csomagolási információk a CMake `find_package` függvényéhez |
| `include/` | C++ fejlécfájlok (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` stb.) |
| `windows/` | Windows bináris fájlok (fordítási idejű `.LIB` és futásidejű `.DLL`/`.GRAPHLIB`/`.AMODEL` fájlok) |
| `linux/` | Linux bináris fájlok (fordítási és futásidejű `.SO` fájlok) |
| `samples/` | Egyedi mintaalkalmazások forráskóddal |

<!-- @os:linux -->

### Linux-specifikus beállítás

#### OpenCV fordítása forrásból

Telepítsd az OpenCV build-függőségeit:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Töltsd le, konfiguráld és fordítsd le az OpenCV 4.11.0-t a contrib modulokkal együtt (hivatkozás: [OpenCV Linux telepítési útmutató](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

A megosztott könyvtárak a `<build>/install/lib/` alatt kerülnek telepítésre. Használd az `install` könyvtárat `OPENCV_INSTALL_ROOT`-ként a további lépésekben.

#### Vulkan SDK

Telepítsd a Vulkan SDK-t:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Ha Ubuntu 22.04-et használsz, frissítsd a MESA Vulkan illesztőprogramokat is:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### További Ubuntu 24.04 függőségek

Ha Ubuntu 24.04-et használsz, telepítsd a további szükséges csomagokat:

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

## Alapfogalmak

A CVML Library egy egyszerű C++ API-t biztosít, amelyben minden észlelési funkciónak (mélységbecslés, arcfelismerés, archáló) saját fejlécfájlja és funkcióobjektuma van. Nem nyers modellekkel dolgozol — a könyvtár automatikusan kezeli a modellbetöltést, előfeldolgozást és következtetést.

### Elérhető funkciók

| Funkció | Fejlécfájl | Leírás |
|---------|------------|-------------|
| **Mélységbecslés** | `cvml-depth-estimation.h` | Pixelenkénti mélységtérképeket generál RGB képekből |
| **Arcfelismerés** | `cvml-face-detector.h` | Arcokat detektál körülhatároló dobozokkal, jellemzőpontokkal (szemek, orr, száj) és megbízhatósági pontszámokkal |
| **Archáló** | `cvml-face-mesh.h` | Részletes arcgeometriát követ sűrű hálópontokkal |

### Programozási modell

Minden CVML alkalmazás ugyanazt a négylépéses mintát követi:

1. **Kontextus létrehozása** — Az `amd::cvml::Context` kezeli a megosztott erőforrásokat, például a naplózást és a következtetési háttérrendszer kiválasztását.
2. **Funkcióobjektum létrehozása** — Példányosítsd a kívánt funkciót (pl. `amd::cvml::DepthEstimation`) a kontextushoz kapcsolva.
3. **Bemeneti adatok becsomagolása** — Használd az `amd::cvml::Image`-et az RGB képpuffer becsomagolásához, adatmásolás nélkül.
4. **Végrehajtás** — Hívd meg a funkció feldolgozó metódusát, és olvasd ki az eredményeket.

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

### Következtetési háttérrendszer

A könyvtár automatikusan kiválasztja az egyes műveletekhez a legjobb hardvert (GPU vagy NPU). A háttérrendszert explicit módon is beállíthatja:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Megjegyzés:** Előfordulhat, hogy az NPU-műveletekhez ONNX háttérrendszert használó funkciók az első futtatáskor hosszabb indítási késleltetést tapasztalnak. A további futtatások gyorsabbak lesznek.

> **Megjegyzés:** Ha az NPU-illesztőprogram nincs telepítve a célrendszeren, a Ryzen AI CVML könyvtár automatikusan visszavált a GPU háttérrendszerre a következtetési műveletekhez.

## A mintaalkalmazások összeállítása

A CVML Library minden funkcióhoz tartalmaz azonnal összeállítható mintaalkalmazásokat. Állítsuk össze ezeket egyszerre.

1. Állítsa be az `OPENCV_INSTALL_ROOT` környezeti változót úgy, hogy az OpenCV-telepítésére mutasson:

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

2. Állítsa össze a mintákat a CMake segítségével:

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

   A sikeres összeállítás után a futtatható fájlok itt találhatók:

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

3. Bármely minta futtatása előtt győződjön meg arról, hogy a CVML futásidejű fájlok elérhetők:

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

## Arcfelismerés futtatása

Az arcfelismerési minta arcokat érzékel egy képen, videóban vagy élő kamerás forrásban. Minden érzékelt archoz kirajzol egy határolókeretet, egy megbízhatósági pontszámot, valamint öt arc-jellemzőpontot (két szem, orr és a száj két sarka).

Először navigáljon az arcfelismerés futtatható fájljának mappájába:

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

Ezután töltsön le egy mintaképet bemenetként (fotó: [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), szabadon felhasználható a Pexels-en keresztül):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Arcfelismerés futtatása a mintaképen:**

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

Megjelenik egy ablak, amely a képet mutatja az érzékelt arcok körüli határolókeretekkel, megbízhatósági pontszámokkal és arc-jellemzőpontokkal (szemek, orr, száj sarkai).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Az annotált kimenet mentése fájlba:**

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

**A precíz modell használata** nagyobb pontosság érdekében (a sebesség rovására):

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

Az arcfelismerési funkció két modellváltozatot kínál:

| Modell | Sebesség | Pontosság | Legalkalmasabb |
|-------|-------|----------|----------|
| `fast` (alapértelmezett) | Magasabb képkockasebesség | Jó | Valós idejű kamerás alkalmazások |
| `precise` | Alacsonyabb képkockasebesség | Legjobb | Fényképelemzés, nagy pontosságot igénylő igények |


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

## A CVML integrálása saját alkalmazásába

Ahhoz, hogy a CVML Library-t saját C++ projektjében használja, adja hozzá a CMake `find_package` parancsával:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Ahol az `AMD_CVML_SDK_ROOT` a Ryzen AI CVML Library mappa gyökerére mutat. Ezután illessze be a megfelelő fejlécfájlt a kívánt funkcióhoz:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Következő lépések

Az alábbi mintapéldák mindegyikéhez először navigálj a hozzá tartozó futtatható mappába, a fent található [Arcfelismerés futtatása](#running-face-detection) szakaszban bemutatott mintát követve (pl. `cd build\cvml-sample-depth-estimation\Release` Windows rendszeren, vagy `cd build/cvml-sample-depth-estimation` Linux rendszeren). Windows esetén minden parancshoz fűzd hozzá a `.exe` kiterjesztést (pl. `cvml-sample-depth-estimation.exe`).

- **Próbáld ki a mélységbecslést**: Futtasd a `cvml-sample-depth-estimation -i sample_face.jpg` parancsot egy színezett mélységtérkép előállításához — a közelebbi objektumok meleg színekkel, a távolabbiak hideg színekkel jelennek meg
- **Fedezd fel az Archáló funkciót**: Futtasd a `cvml-sample-face-mesh -i sample_face.jpg` parancsot, hogy sűrű arcgeometriai követést láss részletes hálópontokkal
- **Videófájlok feldolgozása**: Használd a `-i` és `-o` kapcsolókat bármelyik mintán videók feldolgozásához (pl. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Modellváltozatok összehasonlítása**: Próbáld ki a `-m precise` kapcsolót az alapértelmezett `-m fast` helyett az arcfelismerésnél, hogy saját tapasztalatból lásd a pontosság és sebesség közti kompromisszumot
- **Építs saját alkalmazást**: Használd a CMake integrációt és a C++ API-t, hogy CVML funkciókat adj hozzá saját C++ alkalmazásaidhoz
- **Kombináld a funkciókat**: Kapcsold össze az arcfelismerést a mélységbecsléssel ugyanabban az alkalmazásban a gazdagabb jelenetértelmezés érdekében
- **Böngészd a forráskódot**: Olvasd el a [Ryzen AI CVML Library a GitHubon](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) oldalt a fejlécdokumentációért, további mintákért és API-részletekért