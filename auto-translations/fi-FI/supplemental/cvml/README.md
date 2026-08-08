<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

[Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) on AMD:n C++-pohjainen konenäön ja koneoppimisen työkalupakki, joka tarjoaa tehokkaita, laitteessa suoritettavia havainnointiominaisuuksia — mukaan lukien syvyysarviointi, kasvojentunnistus ja kasvoverkon seuranta. Kirjasto on rakennettu Ryzen AI -ohjainten päälle, ja se valitsee automaattisesti parhaan käytettävissä olevan laitteiston (GPU tai NPU) päättelyä varten, jolloin voit lisätä tekoälyominaisuuksia C++-sovelluksiin ilman huolta mallien koulutuksesta tai kehysten integroinnista. Kaikki käsittely tapahtuu paikallisesti järjestelmässäsi, mikä tekee siitä ihanteellisen yksityisyyttä vaativiin, matalan viiveen sovelluksiin.

Tämä ohjekirja opettaa sinulle, miten asennat Ryzen AI CVML Library -kirjaston, rakennat mukana tulevat esimerkkisovellukset ja suoritat kasvojentunnistuksen esimerkkikuvalle.

## Mitä opit

- Miten asennat esivaatimukset ja määrität Ryzen AI CVML Library -kirjaston järjestelmääsi
- Miten CVML:n C++-rajapinta toimii: kontekstit, ominaisuusobjektit ja kuvapuskurit
- Miten rakennat ja suoritat mukana tulevat esimerkkisovellukset käyttäen CMakea ja OpenCV:tä
- Miten suoritat kasvojentunnistuksen kuvalle rajaavine laatikoineen ja tunnuspisteineen
- Miten integroit CVML-ominaisuudet omiin C++-sovelluksiisi

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen
<!-- @require:driver -->

## Muut riippuvuudet

Ennen aloittamista varmista, että sinulla on seuraavat:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — lataa `opencv-4.11.0-windows.exe`, suorita se ja pura tiedostot paikalliseen kansioon (esim. `C:\opencv`)
- [CMake](https://cmake.org/download/) — lataa Windows x86-64 MSI -asennusohjelma ja valitse asennuksen aikana **"Add CMake to the system PATH for all users"**
- [Ryzen AI NPU -ohjain](https://ryzenai.docs.amd.com/en/latest/inst.html) — asenna uusin saatavilla oleva versio
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) "Desktop development with C++" -työkuormalla (sisältää MSVC-kääntäjän, Windows SDK:n ja C++-rakennustyökalut)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — täytyy rakentaa lähdekoodista (Ubuntu 22.04:n ja 24.04:n apt-paketit eivät tarjoa versiota 4.11). Katso alta [OpenCV:n rakentaminen lähdekoodista](#building-opencv-from-source).
- CMake — asenna apt:n kautta:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 tai 24.04 (kernel >= 6.11.0-21-generic)
- [Ryzen AI NPU -ohjain](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (Linux-asennusohjelma — vaaditaan NPU-päättelyyn)
- Vulkan SDK (asennetaan alla olevassa [Vulkan SDK](#vulkan-sdk) -osiossa)
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

## CVML-kirjaston määrittäminen

Luo AMD-tili osoitteessa [account.amd.com](https://account.amd.com), jos sinulla ei vielä ole tiliä, ja kirjaudu sitten sisään ladataksesi Ryzen AI CVML Library -kirjaston alla olevasta portaalilinkistä:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Latauksen jälkeen pura paketti paikalliseen hakemistoon (esim. `C:\RyzenAI-Library` Windowsissa tai `~/RyzenAI-Library` Linuxissa) ja aseta `AMD_CVML_SDK_ROOT`-ympäristömuuttuja osoittamaan puretun sijaintiin:

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

Kirjastopaketti sisältää seuraavan rakenteen:

| Kansio | Sisältö |
|--------|----------|
| `cmake/` | Pakkaustiedot CMaken `find_package`-funktiota varten |
| `include/` | C++-otsikkotiedostot (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h` jne.) |
| `windows/` | Binääritiedostot Windowsille (käännösaikaiset `.LIB`- ja ajonaikaiset `.DLL`/`.GRAPHLIB`/`.AMODEL`-tiedostot) |
| `linux/` | Binääritiedostot Linuxille (käännös- ja ajonaikaiset `.SO`-tiedostot) |
| `samples/` | Yksittäiset esimerkkisovellukset lähdekoodeineen |

<!-- @os:linux -->

### Linux-kohtaiset asetukset

#### OpenCV:n rakentaminen lähdekoodista

Asenna OpenCV:n rakennusriippuvuudet:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Lataa, määritä ja rakenna OpenCV 4.11.0 contrib-moduulien kanssa (viite: [OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Jaetut kirjastot asennetaan hakemistoon `<build>/install/lib/`. Käytä `install`-hakemistoa `OPENCV_INSTALL_ROOT`-arvona myöhemmissä vaiheissa.

#### Vulkan SDK

Asenna Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Jos käytät Ubuntu 22.04:ää, päivitä myös MESA Vulkan -ohjaimet:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Lisäriippuvuudet Ubuntu 24.04:lle

Jos käytät Ubuntu 24.04:ää, asenna lisävaadittavat paketit:

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

## Peruskäsitteet

CVML Library tarjoaa yksinkertaisen C++-rajapinnan, jossa jokaisella havainnointiominaisuudella (syvyysarviointi, kasvojentunnistus, kasvoverkko) on oma otsikkotiedostonsa ja ominaisuusobjektinsa. Sinun ei tarvitse työskennellä raakojen mallien kanssa — kirjasto hoitaa mallin lataamisen, esikäsittelyn ja päättelyn automaattisesti.

### Käytettävissä olevat ominaisuudet

| Ominaisuus | Otsikkotiedosto | Kuvaus |
|---------|------------|-------------|
| **Syvyysarviointi** | `cvml-depth-estimation.h` | Tuottaa pikselikohtaisia syvyyskarttoja RGB-kuvista |
| **Kasvojentunnistus** | `cvml-face-detector.h` | Havaitsee kasvot rajaavine laatikoineen, tunnuspisteineen (silmät, nenä, suu) ja luottamuspisteineen |
| **Kasvoverkko** | `cvml-face-mesh.h` | Seuraa yksityiskohtaista kasvojen geometriaa tiheillä verkkopisteillä |

### Ohjelmointimalli

Jokainen CVML-sovellus noudattaa samaa neljän vaiheen mallia:

1. **Luo konteksti** — `amd::cvml::Context` hallinnoi jaettuja resursseja, kuten lokitusta ja päättelytaustajärjestelmän valintaa.
2. **Luo ominaisuusobjekti** — Instansioi haluttu ominaisuus (esim. `amd::cvml::DepthEstimation`) kontekstia vasten.
3. **Kääri syöttödata** — Käytä `amd::cvml::Image`-luokkaa RGB-kuvapuskurisi kapseloimiseen ilman datan kopiointia.
4. **Suorita** — Kutsu ominaisuuden käsittelymetodia ja lue tulokset.

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

### Päättelytausta (Inference Backend)

Kirjasto valitsee automaattisesti kullekin toiminnolle parhaan laitteiston (GPU tai NPU). Voit myös asettaa taustajärjestelmän eksplisiittisesti:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Huomautus:** Ominaisuudet, jotka käyttävät ONNX-taustajärjestelmää NPU-toiminnoissa, saattavat kokea pidemmän käynnistysviiveen ensimmäisellä ajokerralla. Seuraavat ajot ovat nopeampia.

> **Huomautus:** Jos NPU-ajuria ei ole asennettu kohdejärjestelmään, Ryzen AI CVML -kirjasto siirtyy automaattisesti käyttämään GPU-taustajärjestelmää päättelytoiminnoissa.

## Esimerkkisovellusten kääntäminen

CVML-kirjasto sisältää valmiiksi käännettävät esimerkkisovellukset jokaista ominaisuutta varten. Käännetään ne kaikki kerralla.

1. Aseta `OPENCV_INSTALL_ROOT`-ympäristömuuttuja osoittamaan OpenCV-asennukseesi:

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

2. Käännä esimerkit CMakella:

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

   Onnistuneen käännöksen jälkeen suoritettavat tiedostot sijaitsevat seuraavasti:

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

3. Ennen minkään esimerkin ajamista varmista, että CVML-ajonaikaiset tiedostot ovat saatavilla:

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

## Kasvojentunnistuksen suorittaminen

Kasvojentunnistuksen esimerkki tunnistaa kasvoja kuvasta, videosta tai suorasta kamerasyötteestä. Se piirtää rajauslaatikot, luottamuspisteet ja viisi kasvonpiirrettä (kaksi silmää, nenä ja kaksi suunkulmaa) jokaiselle havaitulle kasvolle.

Siirry ensin kasvojentunnistuksen suoritettavan tiedoston kansioon:

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

Lataa sitten esimerkkikuva käytettäväksi syötteenä (kuva: [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), vapaasti käytettävissä Pexelsin kautta):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Suorita kasvojentunnistus esimerkkikuvalle:**

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

Näyttöön avautuu ikkuna, jossa näkyy kuva havaittujen kasvojen ympärillä olevine rajauslaatikoineen, luottamuspisteineen ja kasvonpiirrepisteineen (silmät, nenä, suunkulmat).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Tallenna merkitty tuloste tiedostoon:**

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

**Käytä tarkkaa mallia** paremman tarkkuuden saavuttamiseksi (nopeuden kustannuksella):

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

Kasvojentunnistusominaisuus tarjoaa kaksi mallivaihtoehtoa:

| Malli | Nopeus | Tarkkuus | Sopii parhaiten |
|-------|-------|----------|----------|
| `fast` (oletus) | Korkeampi FPS | Hyvä | Reaaliaikaiset kamerasovellukset |
| `precise` | Alhaisempi FPS | Paras | Valokuva-analyysi, korkean tarkkuuden tarpeet |


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

## CVML:n integrointi omaan sovellukseesi

Käyttääksesi CVML-kirjastoa omassa C++-projektissasi lisää se CMaken `find_package`-komennolla:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Missä `AMD_CVML_SDK_ROOT` osoittaa Ryzen AI CVML -kirjastokansion juureen. Sisällytä sitten sopiva otsikkotiedosto haluamaasi ominaisuutta varten:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Seuraavat vaiheet

Siirry kunkin alla olevan esimerkin kohdalla ensin sen suoritettavaan kansioon noudattaen samaa kaavaa kuin edellä olevassa [Kasvojentunnistuksen suorittaminen](#running-face-detection) -osiossa (esim. `cd build\cvml-sample-depth-estimation\Release` Windowsissa tai `cd build/cvml-sample-depth-estimation` Linuxissa). Windowsissa lisää `.exe` jokaisen komennon perään (esim. `cvml-sample-depth-estimation.exe`).

- **Kokeile syvyysarviointia**: Suorita `cvml-sample-depth-estimation -i sample_face.jpg` luodaksesi väritetyn syvyyskartan — lähempänä olevat kohteet näkyvät lämpiminä väreinä, kauempana olevat viileinä väreinä
- **Tutustu kasvoverkkoon**: Suorita `cvml-sample-face-mesh -i sample_face.jpg` nähdäksesi tiheän kasvojen geometrian seurannan yksityiskohtaisilla verkkopisteillä
- **Käsittele videotiedostoja**: Käytä `-i`- ja `-o`-lippuja missä tahansa esimerkissä käsitelläksesi videoita (esim. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Vertaile mallivariantteja**: Kokeile `-m precise` -asetusta oletuksena olevan `-m fast` -asetuksen sijaan kasvojentunnistuksessa nähdäksesi tarkkuuden ja nopeuden välisen kompromissin käytännössä
- **Rakenna oma sovelluksesi**: Käytä CMake-integraatiota ja C++-API:a lisätäksesi CVML-ominaisuuksia omiin C++-sovelluksiisi
- **Yhdistä ominaisuuksia**: Ketjuta kasvojentunnistus syvyysarvioinnin kanssa samassa sovelluksessa laajemman kohtausymmärryksen saavuttamiseksi
- **Selaa lähdekoodia**: Lue [Ryzen AI CVML Library GitHubissa](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) saadaksesi otsikkotiedoston dokumentaation, lisää esimerkkejä ja API-tietoja