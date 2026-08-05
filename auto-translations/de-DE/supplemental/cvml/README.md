<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

Die [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) ist ein AMD C++-Toolkit für Computer Vision und Machine Learning, das leistungsstarke, geräteinterne Wahrnehmungsfunktionen bietet – darunter Tiefenschätzung, Gesichtserkennung und Face-Mesh-Tracking. Aufbauend auf den Ryzen AI-Treibern wählt die Bibliothek automatisch die beste verfügbare Hardware (GPU oder NPU) für die Inferenz aus, sodass Sie C++-Anwendungen um KI-Funktionen erweitern können, ohne sich um Modelltraining oder Framework-Integration kümmern zu müssen. Die gesamte Verarbeitung erfolgt lokal auf Ihrem System, was diese Lösung ideal für datenschutzsensible Anwendungen mit geringer Latenz macht.

Dieses Playbook zeigt Ihnen, wie Sie die Ryzen AI CVML Library einrichten, die enthaltenen Beispielanwendungen erstellen und Gesichtserkennung auf einem Beispielbild ausführen.

## Was Sie lernen werden

- Wie Sie Voraussetzungen installieren und die Ryzen AI CVML Library auf Ihrem System einrichten
- Wie die CVML C++-API funktioniert: Kontexte, Feature-Objekte und Bildpuffer
- Wie Sie die enthaltenen Beispielanwendungen mit CMake und OpenCV erstellen und ausführen
- Wie Sie Gesichtserkennung an einem Bild mit Begrenzungsrahmen und Orientierungspunkten durchführen
- Wie Sie CVML-Funktionen in Ihre eigenen C++-Anwendungen integrieren

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Installation der Software-Voraussetzungen
<!-- @require:driver -->

## Zusätzliche Abhängigkeiten

Stellen Sie vor dem Start sicher, dass Sie Folgendes haben:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — laden Sie `opencv-4.11.0-windows.exe` herunter, führen Sie es aus und extrahieren Sie es in einen lokalen Ordner (z. B. `C:\opencv`)
- [CMake](https://cmake.org/download/) — laden Sie den Windows x86-64 MSI-Installer herunter und wählen Sie während der Installation **„Add CMake to the system PATH for all users“**
- [Ryzen AI NPU-Treiber](https://ryzenai.docs.amd.com/en/latest/inst.html) — installieren Sie die neueste verfügbare Version
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) mit der Workload „Desktopentwicklung mit C++“ (enthält MSVC-Compiler, Windows SDK und C++-Build-Tools)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — muss aus dem Quellcode erstellt werden (die apt-Pakete unter Ubuntu 22.04 und 24.04 bieten keine Version 4.11). Siehe [Erstellen von OpenCV aus dem Quellcode](#building-opencv-from-source) unten.
- CMake — Installation über apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 oder 24.04 (Kernel >= 6.11.0-21-generic)
- [Ryzen AI NPU-Treiber](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (Linux-Installer — erforderlich für NPU-Inferenz)
- Vulkan SDK (installiert im Abschnitt [Vulkan SDK](#vulkan-sdk) weiter unten)
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

## Einrichten der CVML Library

Erstellen Sie ein AMD-Konto unter [account.amd.com](https://account.amd.com), falls Sie noch keines haben, und melden Sie sich dann an, um die Ryzen AI CVML Library über den unten stehenden Portal-Link herunterzuladen:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Extrahieren Sie nach dem Download das Paket in ein lokales Verzeichnis (z. B. `C:\RyzenAI-Library` unter Windows oder `~/RyzenAI-Library` unter Linux) und legen Sie die Umgebungsvariable `AMD_CVML_SDK_ROOT` auf den extrahierten Speicherort fest:

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

Das Bibliothekspaket enthält folgende Struktur:

| Ordner | Inhalte |
|--------|----------|
| `cmake/` | Packaging-Informationen für die `find_package`-Funktion von CMake |
| `include/` | C++-Header-Dateien (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` usw.) |
| `windows/` | Binärdateien für Windows (Compile-Time-`.LIB`- und Runtime-`.DLL`/`.GRAPHLIB`/`.AMODEL`-Dateien) |
| `linux/` | Binärdateien für Linux (Compile- und Runtime-`.SO`-Dateien) |
| `samples/` | Einzelne Beispielanwendungen mit Quellcode |

<!-- @os:linux -->

### Linux-spezifische Einrichtung

#### Erstellen von OpenCV aus dem Quellcode

Installieren Sie die Build-Abhängigkeiten von OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Laden Sie OpenCV 4.11.0 mit den Contrib-Modulen herunter, konfigurieren und erstellen Sie es (Referenz: [OpenCV Linux-Installationsanleitung](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Die freigegebenen Bibliotheken werden unter `<build>/install/lib/` installiert. Verwenden Sie das Verzeichnis `install` als `OPENCV_INSTALL_ROOT` in späteren Schritten.

#### Vulkan SDK

Installieren Sie das Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Falls Sie Ubuntu 22.04 verwenden, aktualisieren Sie außerdem die MESA-Vulkan-Treiber:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Zusätzliche Ubuntu 24.04-Abhängigkeiten

Falls Sie Ubuntu 24.04 verwenden, installieren Sie zusätzliche erforderliche Pakete:

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

## Grundlegende Konzepte

Die CVML Library bietet eine einfache C++-API, bei der jede Wahrnehmungsfunktion (Tiefenschätzung, Gesichtserkennung, Face Mesh) über eine eigene Header-Datei und ein eigenes Feature-Objekt verfügt. Sie arbeiten nicht mit rohen Modellen — die Bibliothek übernimmt automatisch das Laden von Modellen, die Vorverarbeitung und die Inferenz.

### Verfügbare Funktionen

| Funktion | Header-Datei | Beschreibung |
|---------|------------|-------------|
| **Tiefenschätzung** | `cvml-depth-estimation.h` | Erzeugt pixelgenaue Tiefenkarten aus RGB-Bildern |
| **Gesichtserkennung** | `cvml-face-detector.h` | Erkennt Gesichter mit Begrenzungsrahmen, Orientierungspunkten (Augen, Nase, Mund) und Konfidenzwerten |
| **Face Mesh** | `cvml-face-mesh.h` | Verfolgt detaillierte Gesichtsgeometrie mit dichten Mesh-Punkten |

### Programmiermodell

Jede CVML-Anwendung folgt demselben vierstufigen Muster:

1. **Kontext erstellen** — Der `amd::cvml::Context` verwaltet gemeinsam genutzte Ressourcen wie Protokollierung und die Auswahl des Inferenz-Backends.
2. **Feature-Objekt erstellen** — Instanziieren Sie die spezifische Funktion (z. B. `amd::cvml::DepthEstimation`) über den Kontext.
3. **Eingabedaten kapseln** — Verwenden Sie `amd::cvml::Image`, um Ihren RGB-Bildpuffer zu kapseln, ohne Daten zu kopieren.
4. **Ausführen** — Rufen Sie die Verarbeitungsmethode der Funktion auf und lesen Sie die Ergebnisse.

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

### Inferenz-Backend

Die Bibliothek wählt automatisch die beste Hardware (GPU oder NPU) für jeden Vorgang aus. Sie können das Backend auch explizit festlegen:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Hinweis:** Bei Funktionen, die das ONNX-Backend für NPU-Vorgänge verwenden, kann es beim ersten Ausführen zu einer längeren Startlatenz kommen. Nachfolgende Ausführungen sind schneller.

> **Hinweis:** Falls der NPU-Treiber auf dem Zielsystem nicht installiert ist, verwendet die Ryzen AI CVML Library für Inferenzvorgänge automatisch das GPU-Backend als Fallback.

## Erstellen der Beispielanwendungen

Die CVML Library enthält fertige Beispielanwendungen für jede Funktion, die Sie selbst kompilieren können. Lassen Sie uns alle auf einmal erstellen.

1. Legen Sie die Umgebungsvariable `OPENCV_INSTALL_ROOT` so fest, dass sie auf Ihre OpenCV-Installation verweist:

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

2. Erstellen Sie die Beispiele mit CMake:

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

   Nach einem erfolgreichen Build befinden sich die ausführbaren Dateien hier:

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

3. Bevor Sie ein Beispiel ausführen, stellen Sie sicher, dass die CVML-Laufzeitdateien zugänglich sind:

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

## Gesichtserkennung ausführen

Das Gesichtserkennungsbeispiel erkennt Gesichter in einem Bild, Video oder Live-Kamerabild. Es zeichnet Begrenzungsrahmen, Konfidenzwerte und fünf Gesichtsmerkmale (zwei Augen, Nase und zwei Mundwinkel) für jedes erkannte Gesicht ein.

Navigieren Sie zunächst zum Ordner mit der ausführbaren Datei der Gesichtserkennung:

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

Laden Sie anschließend ein Beispielbild als Eingabe herunter (Foto von [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), kostenlos nutzbar über Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Führen Sie die Gesichtserkennung mit dem Beispielbild aus:**

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

Ein Fenster wird angezeigt, das das Bild mit Begrenzungsrahmen um erkannte Gesichter, Konfidenzwerten und Gesichtsmerkmalspunkten (Augen, Nase, Mundwinkel) zeigt.

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Speichern Sie die kommentierte Ausgabe in einer Datei:**

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

**Verwenden Sie das präzise Modell** für höhere Genauigkeit (auf Kosten der Geschwindigkeit):

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

Die Gesichtserkennungsfunktion bietet zwei Modellvarianten:

| Modell | Geschwindigkeit | Genauigkeit | Am besten geeignet für |
|-------|-------|----------|----------|
| `fast` (Standard) | Höhere FPS | Gut | Echtzeit-Kameraanwendungen |
| `precise` | Niedrigere FPS | Beste | Fotoanalyse, hohe Genauigkeitsanforderungen |


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

## Integration von CVML in Ihre eigene Anwendung

Um die CVML Library in Ihrem eigenen C++-Projekt zu verwenden, fügen Sie sie über die `find_package`-Funktion von CMake hinzu:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Dabei verweist `AMD_CVML_SDK_ROOT` auf das Stammverzeichnis des Ordners der Ryzen AI CVML Library. Fügen Sie dann die passende Header-Datei für die gewünschte Funktion ein:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Nächste Schritte

Navigieren Sie für jedes Beispiel unten zunächst in den zugehörigen ausführbaren Ordner, nach demselben Muster wie im Abschnitt [Running Face Detection](#running-face-detection) oben (z. B. `cd build\cvml-sample-depth-estimation\Release` unter Windows oder `cd build/cvml-sample-depth-estimation` unter Linux). Hängen Sie unter Windows an jeden Befehl `.exe` an (z. B. `cvml-sample-depth-estimation.exe`).

- **Tiefenschätzung ausprobieren**: Führen Sie `cvml-sample-depth-estimation -i sample_face.jpg` aus, um eine farbcodierte Tiefenkarte zu erzeugen – nähere Objekte erscheinen in warmen Farben, entfernte in kühlen Farben
- **Face Mesh erkunden**: Führen Sie `cvml-sample-face-mesh -i sample_face.jpg` aus, um die dichte Verfolgung der Gesichtsgeometrie mit detaillierten Mesh-Punkten zu sehen
- **Videodateien verarbeiten**: Verwenden Sie die Flags `-i` und `-o` bei jedem Beispiel, um Videos zu verarbeiten (z. B. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Modellvarianten vergleichen**: Testen Sie `-m precise` im Vergleich zum Standard `-m fast` bei der Gesichtserkennung, um den Kompromiss zwischen Genauigkeit und Geschwindigkeit live zu erleben
- **Eigene App entwickeln**: Nutzen Sie die CMake-Integration und die C++-API, um CVML-Funktionen in Ihre eigenen C++-Anwendungen einzubinden
- **Funktionen kombinieren**: Verketten Sie die Gesichtserkennung mit der Tiefenschätzung in derselben Anwendung für ein umfassenderes Szenenverständnis
- **Quellcode durchsuchen**: Lesen Sie die [Ryzen AI CVML Library auf GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) für Header-Dokumentation, zusätzliche Beispiele und API-Details