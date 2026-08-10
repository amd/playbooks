<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

[Biblioteka Ryzen AI CVML](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) to zestaw narzędzi AMD w języku C++ do wizji komputerowej i uczenia maszynowego, który zapewnia zaawansowane możliwości percepcji realizowane bezpośrednio na urządzeniu — w tym estymację głębi, wykrywanie twarzy oraz śledzenie siatki twarzy. Biblioteka, zbudowana na sterownikach Ryzen AI, automatycznie wybiera najlepszy dostępny sprzęt (GPU lub NPU) do wnioskowania, umożliwiając dodawanie funkcji AI do aplikacji C++ bez konieczności martwienia się o trenowanie modeli czy integrację z frameworkami. Całe przetwarzanie odbywa się lokalnie na Twoim systemie, co czyni tę bibliotekę idealną do zastosowań wymagających prywatności i niskich opóźnień.

Ten podręcznik nauczy Cię, jak skonfigurować bibliotekę Ryzen AI CVML, zbudować dołączone przykładowe aplikacje oraz uruchomić wykrywanie twarzy na przykładowym obrazie.

## Czego się nauczysz

- Jak zainstalować wymagania wstępne i skonfigurować bibliotekę Ryzen AI CVML w systemie
- Jak działa interfejs API C++ CVML: konteksty, obiekty funkcji i bufory obrazów
- Jak zbudować i uruchomić dołączone przykładowe aplikacje przy użyciu CMake i OpenCV
- Jak uruchomić wykrywanie twarzy na obrazie z ramkami ograniczającymi i punktami charakterystycznymi
- Jak zintegrować funkcje CVML z własnymi aplikacjami C++

<!-- @device:halo_box -->
## Sprawdź dostępność aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymagań wstępnych dotyczących oprogramowania
<!-- @require:driver -->

## Dodatkowe zależności

Przed rozpoczęciem upewnij się, że masz następujące elementy:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — pobierz plik `opencv-4.11.0-windows.exe`, uruchom go i rozpakuj do lokalnego folderu (np. `C:\opencv`)
- [CMake](https://cmake.org/download/) — pobierz instalator MSI dla systemu Windows x86-64 i podczas instalacji zaznacz opcję **„Add CMake to the system PATH for all users”**
- [Sterownik Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — zainstaluj najnowszą dostępną wersję
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) z obciążeniem roboczym „Desktop development with C++” (obejmuje kompilator MSVC, Windows SDK oraz narzędzia do budowania C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — musi zostać zbudowane ze źródeł (pakiety apt w Ubuntu 22.04 i 24.04 nie udostępniają wersji 4.11). Zobacz sekcję [Building OpenCV from Source](#building-opencv-from-source) poniżej.
- CMake — zainstaluj za pomocą apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 lub 24.04 (kernel >= 6.11.0-21-generic)
- [Sterownik Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (instalator dla systemu Linux — wymagany do wnioskowania na NPU)
- Vulkan SDK (instalowany w sekcji [Vulkan SDK](#vulkan-sdk) poniżej)
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

## Konfiguracja biblioteki CVML

Jeśli nie masz jeszcze konta AMD, utwórz je na stronie [account.amd.com](https://account.amd.com), a następnie zaloguj się, aby pobrać bibliotekę Ryzen AI CVML za pomocą poniższego linku do portalu:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Po pobraniu rozpakuj pakiet do lokalnego katalogu (np. `C:\RyzenAI-Library` w systemie Windows lub `~/RyzenAI-Library` w systemie Linux) i ustaw zmienną środowiskową `AMD_CVML_SDK_ROOT`, wskazując na rozpakowaną lokalizację:

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

Pakiet biblioteki zawiera następującą strukturę:

| Folder | Zawartość |
|--------|----------|
| `cmake/` | Informacje pakietowe dla funkcji `find_package` w CMake |
| `include/` | Pliki nagłówkowe C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` itd.) |
| `windows/` | Pliki binarne dla systemu Windows (pliki `.LIB` kompilowane oraz pliki wykonawcze `.DLL`/`.GRAPHLIB`/`.AMODEL`) |
| `linux/` | Pliki binarne dla systemu Linux (pliki kompilowane i wykonawcze `.SO`) |
| `samples/` | Poszczególne przykładowe aplikacje wraz z kodem źródłowym |

<!-- @os:linux -->

### Konfiguracja specyficzna dla systemu Linux

#### Budowanie OpenCV ze źródeł

Zainstaluj zależności potrzebne do zbudowania OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Pobierz, skonfiguruj i zbuduj OpenCV 4.11.0 wraz z modułami contrib (odwołanie: [samouczek instalacji OpenCV dla systemu Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Biblioteki współdzielone są instalowane w katalogu `<build>/install/lib/`. Użyj katalogu `install` jako `OPENCV_INSTALL_ROOT` w kolejnych krokach.

#### Vulkan SDK

Zainstaluj Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Jeśli używasz systemu Ubuntu 22.04, zaktualizuj również sterowniki MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Dodatkowe zależności dla Ubuntu 24.04

Jeśli używasz systemu Ubuntu 24.04, zainstaluj dodatkowe wymagane pakiety:

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

## Podstawowe koncepcje

Biblioteka CVML udostępnia prosty interfejs API w języku C++, w którym każda funkcja percepcyjna (estymacja głębi, wykrywanie twarzy, siatka twarzy) posiada własny plik nagłówkowy i obiekt funkcji. Nie pracujesz bezpośrednio z surowymi modelami — biblioteka automatycznie zajmuje się ładowaniem modeli, przetwarzaniem wstępnym oraz wnioskowaniem.

### Dostępne funkcje

| Funkcja | Plik nagłówkowy | Opis |
|---------|------------|-------------|
| **Estymacja głębi** | `cvml-depth-estimation.h` | Generuje mapy głębi dla poszczególnych pikseli na podstawie obrazów RGB |
| **Wykrywanie twarzy** | `cvml-face-detector.h` | Wykrywa twarze wraz z ramkami ograniczającymi, punktami charakterystycznymi (oczy, nos, usta) oraz wskaźnikami pewności |
| **Siatka twarzy** | `cvml-face-mesh.h` | Śledzi szczegółową geometrię twarzy przy użyciu gęstych punktów siatki |

### Model programowania

Każda aplikacja CVML działa według tego samego czteroetapowego wzorca:

1. **Utwórz kontekst** — `amd::cvml::Context` zarządza zasobami współdzielonymi, takimi jak logowanie i wybór backendu wnioskowania.
2. **Utwórz obiekt funkcji** — utwórz instancję konkretnej funkcji (np. `amd::cvml::DepthEstimation`) w kontekście.
3. **Opakuj dane wejściowe** — użyj `amd::cvml::Image`, aby opakować bufor obrazu RGB bez kopiowania danych.
4. **Wykonaj przetwarzanie** — wywołaj metodę przetwarzania funkcji i odczytaj wyniki.

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

### Backend wnioskowania

Biblioteka automatycznie wybiera najlepszy sprzęt (GPU lub NPU) dla każdej operacji. Można też ustawić backend jawnie:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Uwaga:** Funkcje korzystające z backendu ONNX do operacji na NPU mogą charakteryzować się dłuższym opóźnieniem uruchamiania przy pierwszym uruchomieniu. Kolejne uruchomienia będą szybsze.

> **Uwaga:** Jeśli sterownik NPU nie jest zainstalowany w systemie docelowym, biblioteka Ryzen AI CVML automatycznie przełączy się na backend GPU do operacji wnioskowania.

## Kompilowanie przykładowych aplikacji

Biblioteka CVML zawiera gotowe do skompilowania przykładowe aplikacje dla każdej funkcji. Skompilujmy je wszystkie naraz.

1. Ustaw zmienną środowiskową `OPENCV_INSTALL_ROOT`, aby wskazywała na instalację OpenCV:

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

2. Skompiluj przykłady za pomocą CMake:

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

   Po pomyślnym skompilowaniu pliki wykonywalne znajdują się w:

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

3. Przed uruchomieniem dowolnego przykładu upewnij się, że pliki środowiska uruchomieniowego CVML są dostępne:

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

## Uruchamianie wykrywania twarzy

Przykład wykrywania twarzy wykrywa twarze na obrazie, w filmie lub na żywym obrazie z kamery. Rysuje ramki ograniczające, wyniki pewności oraz pięć punktów charakterystycznych twarzy (dwoje oczu, nos i dwa kąciki ust) na każdej wykrytej twarzy.

Najpierw przejdź do folderu z plikiem wykonywalnym wykrywania twarzy:

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

Następnie pobierz przykładowy obraz do użycia jako dane wejściowe (zdjęcie autorstwa [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), dostępne do bezpłatnego użytku dzięki Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Uruchom wykrywanie twarzy na przykładowym obrazie:**

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

Pojawi się okno przedstawiające obraz z ramkami ograniczającymi wokół wykrytych twarzy, wynikami pewności oraz punktami charakterystycznymi twarzy (oczy, nos, kąciki ust).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Zapisz opisany wynik do pliku:**

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

**Użyj precyzyjnego modelu** dla wyższej dokładności (kosztem szybkości):

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

Funkcja wykrywania twarzy oferuje dwa warianty modelu:

| Model | Szybkość | Dokładność | Najlepiej sprawdza się w |
|-------|-------|----------|----------|
| `fast` (domyślny) | Wyższa liczba FPS | Dobra | Aplikacjach z kamerą działających w czasie rzeczywistym |
| `precise` | Niższa liczba FPS | Najlepsza | Analizie zdjęć, zastosowaniach wymagających wysokiej dokładności |


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

## Integracja CVML z własną aplikacją

Aby użyć biblioteki CVML we własnym projekcie C++, dodaj ją za pomocą `find_package` w CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Gdzie `AMD_CVML_SDK_ROOT` wskazuje na katalog główny folderu biblioteki Ryzen AI CVML. Następnie dołącz odpowiedni nagłówek dla funkcji, której chcesz użyć:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Kolejne kroki

Dla każdej z poniższych próbek najpierw przejdź do jej folderu wykonywalnego, postępując zgodnie z tym samym schematem, co w sekcji [Running Face Detection](#running-face-detection) powyżej (np. `cd build\cvml-sample-depth-estimation\Release` w systemie Windows lub `cd build/cvml-sample-depth-estimation` w systemie Linux). W systemie Windows dodaj `.exe` do każdego polecenia (np. `cvml-sample-face-detection.exe`).

- **Wypróbuj estymację głębi**: Uruchom `cvml-sample-depth-estimation -i sample_face.jpg`, aby wygenerować kolorową mapę głębi — bliższe obiekty pojawiają się w ciepłych kolorach, a dalsze w chłodnych
- **Poznaj Face Mesh**: Uruchom `cvml-sample-face-mesh -i sample_face.jpg`, aby zobaczyć śledzenie gęstej geometrii twarzy z dokładnymi punktami siatki
- **Przetwarzaj pliki wideo**: Użyj flag `-i` oraz `-o` w dowolnej próbce, aby przetwarzać pliki wideo (np. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Porównaj warianty modelu**: Wypróbuj `-m precise` w porównaniu z domyślnym `-m fast` w wykrywaniu twarzy, aby na własne oczy zobaczyć kompromis między dokładnością a szybkością
- **Zbuduj własną aplikację**: Skorzystaj z integracji CMake oraz interfejsu C++ API, aby dodać funkcje CVML do własnych aplikacji w języku C++
- **Łącz funkcje**: Połącz wykrywanie twarzy z estymacją głębi w tej samej aplikacji, aby uzyskać bogatsze rozumienie sceny
- **Przeglądaj kod źródłowy**: Zapoznaj się z [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library), aby uzyskać dokumentację nagłówków, dodatkowe przykłady i szczegóły API