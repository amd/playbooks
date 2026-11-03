<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

La [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) è un toolkit C++ AMD per la visione artificiale e il machine learning che offre potenti funzionalità di percezione on-device, tra cui stima della profondità, rilevamento del volto e tracciamento della mesh facciale. Costruita sopra i driver Ryzen AI, la libreria seleziona automaticamente l'hardware disponibile migliore (GPU o NPU) per l'inferenza, permettendoti di aggiungere funzionalità di AI alle applicazioni C++ senza doverti preoccupare dell'addestramento dei modelli o dell'integrazione del framework. L'intera elaborazione avviene localmente sul tuo sistema, rendendola ideale per applicazioni sensibili alla privacy e a bassa latenza.

Questa guida ti insegna come impostare la Ryzen AI CVML Library, compilare le applicazioni di esempio incluse ed eseguire il rilevamento del volto su un'immagine di esempio.

## Cosa imparerai

- Come installare i prerequisiti e configurare la Ryzen AI CVML Library sul tuo sistema
- Come funziona l'API C++ di CVML: contesti, oggetti feature e buffer immagine
- Come compilare ed eseguire le applicazioni di esempio incluse usando CMake e OpenCV
- Come eseguire il rilevamento del volto su un'immagine con riquadri di delimitazione e punti di riferimento
- Come integrare le funzionalità di CVML nelle tue applicazioni C++

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software
<!-- @require:driver -->

## Dipendenze aggiuntive

Prima di iniziare, assicurati di avere quanto segue:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — scarica `opencv-4.11.0-windows.exe`, eseguilo ed estrai in una cartella locale (ad es. `C:\opencv`)
- [CMake](https://cmake.org/download/) — scarica l'installer MSI per Windows x86-64 e durante l'installazione seleziona **"Add CMake to the system PATH for all users"**
- [Driver NPU Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html) — installa l'ultima versione disponibile
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) con il carico di lavoro "Desktop development with C++" (include il compilatore MSVC, Windows SDK e gli strumenti di build C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — deve essere compilato dal codice sorgente (i pacchetti apt su Ubuntu 22.04 e 24.04 non forniscono la versione 4.11). Vedi [Compilazione di OpenCV dal codice sorgente](#building-opencv-from-source) di seguito.
- CMake — installa tramite apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 o 24.04 (kernel >= 6.11.0-21-generic)
- [Driver NPU Ryzen AI](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (installer Linux — richiesto per l'inferenza su NPU)
- Vulkan SDK (installato nella sezione [Vulkan SDK](#vulkan-sdk) di seguito)
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

## Configurazione della CVML Library

Crea un account AMD su [account.amd.com](https://account.amd.com) se non ne hai uno, quindi accedi per scaricare la Ryzen AI CVML Library dal link del portale qui sotto:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Dopo il download, estrai il pacchetto in una directory locale (ad es. `C:\RyzenAI-Library` su Windows o `~/RyzenAI-Library` su Linux) e imposta la variabile d'ambiente `AMD_CVML_SDK_ROOT` sulla posizione estratta:

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

Il pacchetto della libreria contiene la seguente struttura:

| Cartella | Contenuti |
|--------|----------|
| `cmake/` | Informazioni di packaging per la funzione `find_package` di CMake |
| `include/` | File header C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, ecc.) |
| `windows/` | File binari per Windows (file `.LIB` di compilazione e `.DLL`/`.GRAPHLIB`/`.AMODEL` di runtime) |
| `linux/` | File binari per Linux (file `.SO` di compilazione e runtime) |
| `samples/` | Applicazioni di esempio individuali con codice sorgente |

<!-- @os:linux -->

### Configurazione specifica per Linux

#### Compilazione di OpenCV dal codice sorgente

Installa le dipendenze di compilazione di OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Scarica, configura e compila OpenCV 4.11.0 con i moduli contrib (riferimento: [tutorial di installazione OpenCV su Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Le librerie condivise vengono installate in `<build>/install/lib/`. Usa la directory `install` come `OPENCV_INSTALL_ROOT` nei passaggi successivi.

#### Vulkan SDK

Installa il Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Se stai eseguendo Ubuntu 22.04, aggiorna anche i driver MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Dipendenze aggiuntive per Ubuntu 24.04

Se stai eseguendo Ubuntu 24.04, installa i pacchetti aggiuntivi richiesti:

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

## Concetti fondamentali

La CVML Library fornisce una semplice API C++ in cui ogni funzionalità di percezione (stima della profondità, rilevamento del volto, mesh facciale) ha il proprio file header e oggetto feature. Non lavori direttamente con i modelli grezzi: la libreria gestisce automaticamente il caricamento del modello, il pre-processing e l'inferenza.

### Funzionalità disponibili

| Funzionalità | File header | Descrizione |
|---------|------------|-------------|
| **Stima della profondità** | `cvml-depth-estimation.h` | Genera mappe di profondità per pixel a partire da immagini RGB |
| **Rilevamento del volto** | `cvml-face-detector.h` | Rileva volti con riquadri di delimitazione, punti di riferimento (occhi, naso, bocca) e punteggi di confidenza |
| **Mesh facciale** | `cvml-face-mesh.h` | Traccia la geometria facciale dettagliata con punti mesh densi |

### Modello di programmazione

Ogni applicazione CVML segue lo stesso schema a quattro fasi:

1. **Crea un contesto** — Il `amd::cvml::Context` gestisce risorse condivise come il logging e la selezione del backend di inferenza.
2. **Crea un oggetto feature** — Crea un'istanza della funzionalità specifica (ad es. `amd::cvml::DepthEstimation`) associata al contesto.
3. **Incapsula i dati di input** — Usa `amd::cvml::Image` per incapsulare il tuo buffer immagine RGB senza copiare i dati.
4. **Esegui** — Chiama il metodo di elaborazione della funzionalità e leggi i risultati.

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

### Backend di inferenza

La libreria seleziona automaticamente l'hardware migliore (GPU o NPU) per ogni operazione. È inoltre possibile impostare esplicitamente il backend:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Nota:** le funzionalità che utilizzano il backend ONNX per le operazioni su NPU potrebbero presentare una latenza di avvio più lunga alla prima esecuzione. Le esecuzioni successive saranno più veloci.

> **Nota:** se il driver NPU non è installato sul sistema di destinazione, la libreria Ryzen AI CVML utilizzerà automaticamente il backend GPU per le operazioni di inferenza.

## Compilazione delle applicazioni di esempio

La libreria CVML include applicazioni di esempio pronte per la compilazione per ciascuna funzionalità. Compiliamole tutte insieme.

1. Impostare la variabile d'ambiente `OPENCV_INSTALL_ROOT` in modo che punti alla propria installazione di OpenCV:

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

2. Compilare i sample con CMake:

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

   Al termine della compilazione, gli eseguibili si trovano in:

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

3. Prima di eseguire qualsiasi sample, assicurarsi che i file runtime di CVML siano accessibili:

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

## Esecuzione del rilevamento del volto

Il sample di rilevamento del volto rileva i volti in un'immagine, un video o un flusso video dal vivo di una fotocamera. Disegna riquadri di delimitazione, punteggi di affidabilità e cinque punti di riferimento facciali (due occhi, naso e due angoli della bocca) su ogni volto rilevato.

Per prima cosa, spostarsi nella cartella dell'eseguibile di rilevamento del volto:

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

Quindi scaricare un'immagine di esempio da utilizzare come input (foto di [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), utilizzabile gratuitamente tramite Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Eseguire il rilevamento del volto sull'immagine di esempio:**

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

Verrà visualizzata una finestra che mostra l'immagine con i riquadri di delimitazione attorno ai volti rilevati, i punteggi di affidabilità e i punti di riferimento facciali (occhi, naso, angoli della bocca).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Salvare l'output annotato in un file:**

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

**Utilizzare il modello preciso** per una maggiore accuratezza (a scapito della velocità):

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

La funzionalità di rilevamento del volto offre due varianti di modello:

| Modello | Velocità | Accuratezza | Ideale per |
|-------|-------|----------|----------|
| `fast` (predefinito) | FPS più elevati | Buona | Applicazioni con fotocamera in tempo reale |
| `precise` | FPS più bassi | Ottima | Analisi fotografiche, esigenze di elevata accuratezza |


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

## Integrazione di CVML nella propria applicazione

Per utilizzare la libreria CVML nel proprio progetto C++, aggiungerla tramite `find_package` di CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Dove `AMD_CVML_SDK_ROOT` punta alla radice della cartella della libreria Ryzen AI CVML. Quindi includere l'header appropriato per la funzionalità desiderata:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Prossimi Passi

Per ciascun esempio riportato di seguito, spostati prima nella relativa cartella eseguibile, seguendo lo stesso schema della sezione [Running Face Detection](#running-face-detection) sopra (ad es. `cd build\cvml-sample-depth-estimation\Release` su Windows o `cd build/cvml-sample-depth-estimation` su Linux). Su Windows, aggiungi `.exe` a ciascun comando (ad es. `cvml-sample-depth-estimation.exe`).

- **Prova la Depth Estimation**: Esegui `cvml-sample-depth-estimation -i sample_face.jpg` per generare una mappa di profondità colorata — gli oggetti più vicini appaiono in colori caldi, quelli più distanti in colori freddi
- **Esplora Face Mesh**: Esegui `cvml-sample-face-mesh -i sample_face.jpg` per vedere il tracciamento denso della geometria facciale con punti mesh dettagliati
- **Elabora file video**: Usa i flag `-i` e `-o` su qualsiasi esempio per elaborare video (ad es., `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Confronta le varianti dei modelli**: Prova `-m precise` rispetto al valore predefinito `-m fast` sulla rilevazione dei volti per verificare di persona il compromesso tra accuratezza e velocità
- **Crea la tua app**: Usa l'integrazione CMake e l'API C++ per aggiungere funzionalità CVML alle tue applicazioni C++
- **Combina le funzionalità**: Concatena la rilevazione dei volti con la depth estimation nella stessa applicazione per una comprensione della scena più ricca
- **Esplora il codice sorgente**: Leggi [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) per la documentazione degli header, esempi aggiuntivi e dettagli sull'API