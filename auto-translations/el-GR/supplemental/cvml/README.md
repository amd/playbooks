<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Η [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) είναι ένα εργαλείο AMD C++ για όραση υπολογιστών και μηχανική μάθηση που παρέχει ισχυρές δυνατότητες αντίληψης στη συσκευή — συμπεριλαμβανομένων της εκτίμησης βάθους, της ανίχνευσης προσώπου και της παρακολούθησης πλέγματος προσώπου (face mesh). Χτισμένη πάνω στους οδηγούς Ryzen AI, η βιβλιοθήκη επιλέγει αυτόματα το καλύτερο διαθέσιμο υλικό (GPU ή NPU) για συμπερασμό, επιτρέποντάς σας να προσθέτετε δυνατότητες AI σε εφαρμογές C++ χωρίς να χρειάζεται να ανησυχείτε για την εκπαίδευση μοντέλων ή την ενσωμάτωση πλαισίων. Όλη η επεξεργασία γίνεται τοπικά στο σύστημά σας, καθιστώντας την ιδανική για εφαρμογές ευαίσθητες στην ιδιωτικότητα και χαμηλής καθυστέρησης.

Αυτό το playbook σας διδάσκει πώς να ρυθμίσετε τη Ryzen AI CVML Library, να δημιουργήσετε (build) τις περιλαμβανόμενες δείγμα εφαρμογές και να εκτελέσετε ανίχνευση προσώπου σε μια δείγμα εικόνα.

## Τι Θα Μάθετε

- Πώς να εγκαταστήσετε τις προϋποθέσεις και να ρυθμίσετε τη Ryzen AI CVML Library στο σύστημά σας
- Πώς λειτουργεί το CVML C++ API: contexts, feature objects και image buffers
- Πώς να δημιουργήσετε (build) και να εκτελέσετε τις περιλαμβανόμενες δείγμα εφαρμογές χρησιμοποιώντας CMake και OpenCV
- Πώς να εκτελέσετε ανίχνευση προσώπου σε μια εικόνα με πλαίσια οριοθέτησης (bounding boxes) και σημεία αναφοράς (landmarks)
- Πώς να ενσωματώσετε δυνατότητες CVML στις δικές σας εφαρμογές C++

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προϋποθέσεων Λογισμικού
<!-- @require:driver -->

## Πρόσθετες Εξαρτήσεις

Πριν ξεκινήσετε, βεβαιωθείτε ότι διαθέτετε τα εξής:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — κατεβάστε το `opencv-4.11.0-windows.exe`, εκτελέστε το και εξαγάγετε σε έναν τοπικό φάκελο (π.χ. `C:\opencv`)
- [CMake](https://cmake.org/download/) — κατεβάστε τον εγκαταστάτη Windows x86-64 MSI και κατά την εγκατάσταση επιλέξτε **"Add CMake to the system PATH for all users"**
- [Οδηγός Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — εγκαταστήστε την τελευταία διαθέσιμη έκδοση
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) με το φορτίο εργασίας "Desktop development with C++" (περιλαμβάνει τον μεταγλωττιστή MSVC, το Windows SDK και τα εργαλεία δημιουργίας C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — πρέπει να δημιουργηθεί (build) από τον πηγαίο κώδικα (τα πακέτα apt στο Ubuntu 22.04 και 24.04 δεν παρέχουν την έκδοση 4.11). Δείτε [Building OpenCV from Source](#building-opencv-from-source) παρακάτω.
- CMake — εγκαταστήστε μέσω apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 ή 24.04 (kernel >= 6.11.0-21-generic)
- [Οδηγός Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (εγκαταστάτης Linux — απαιτείται για συμπερασμό NPU)
- Vulkan SDK (εγκαθίσταται στην ενότητα [Vulkan SDK](#vulkan-sdk) παρακάτω)
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

## Ρύθμιση της CVML Library

Δημιουργήστε έναν λογαριασμό AMD στο [account.amd.com](https://account.amd.com) αν δεν έχετε ήδη, στη συνέχεια συνδεθείτε για να κατεβάσετε τη Ryzen AI CVML Library από τον σύνδεσμο της πύλης παρακάτω:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Μετά τη λήψη, εξαγάγετε το πακέτο σε έναν τοπικό κατάλογο (π.χ., `C:\RyzenAI-Library` στα Windows ή `~/RyzenAI-Library` στο Linux) και ορίστε τη μεταβλητή περιβάλλοντος `AMD_CVML_SDK_ROOT` στην τοποθεσία εξαγωγής:

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

Το πακέτο βιβλιοθήκης περιέχει την ακόλουθη δομή:

| Φάκελος | Περιεχόμενα |
|--------|----------|
| `cmake/` | Πληροφορίες πακεταρίσματος για τη συνάρτηση `find_package` του CMake |
| `include/` | Αρχεία κεφαλίδων C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, κ.λπ.) |
| `windows/` | Δυαδικά αρχεία για Windows (αρχεία `.LIB` χρόνου μεταγλώττισης και `.DLL`/`.GRAPHLIB`/`.AMODEL` χρόνου εκτέλεσης) |
| `linux/` | Δυαδικά αρχεία για Linux (αρχεία μεταγλώττισης και χρόνου εκτέλεσης `.SO`) |
| `samples/` | Μεμονωμένες δείγμα εφαρμογές με πηγαίο κώδικα |

<!-- @os:linux -->

### Ρύθμιση Ειδική για Linux

#### Δημιουργία (Build) του OpenCV από τον Πηγαίο Κώδικα

Εγκαταστήστε τις εξαρτήσεις δημιουργίας (build) του OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Κατεβάστε, διαμορφώστε και δημιουργήστε (build) το OpenCV 4.11.0 με τις ενότητες contrib (αναφορά: [OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Οι κοινόχρηστες βιβλιοθήκες εγκαθίστανται στο `<build>/install/lib/`. Χρησιμοποιήστε τον κατάλογο `install` ως `OPENCV_INSTALL_ROOT` στα επόμενα βήματα.

#### Vulkan SDK

Εγκαταστήστε το Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Αν εκτελείτε Ubuntu 22.04, ενημερώστε επίσης τους οδηγούς MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Πρόσθετες Εξαρτήσεις για Ubuntu 24.04

Αν εκτελείτε Ubuntu 24.04, εγκαταστήστε τα πρόσθετα απαιτούμενα πακέτα:

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

## Βασικές Έννοιες

Η CVML Library παρέχει ένα απλό C++ API όπου κάθε δυνατότητα αντίληψης (εκτίμηση βάθους, ανίχνευση προσώπου, face mesh) έχει το δικό της αρχείο κεφαλίδας και το δικό της feature object. Δεν εργάζεστε με ακατέργαστα μοντέλα — η βιβλιοθήκη διαχειρίζεται αυτόματα τη φόρτωση μοντέλων, την προεπεξεργασία και τον συμπερασμό.

### Διαθέσιμες Δυνατότητες

| Δυνατότητα | Αρχείο Κεφαλίδας | Περιγραφή |
|---------|------------|-------------|
| **Εκτίμηση Βάθους** | `cvml-depth-estimation.h` | Δημιουργεί χάρτες βάθους ανά pixel από εικόνες RGB |
| **Ανίχνευση Προσώπου** | `cvml-face-detector.h` | Ανιχνεύει πρόσωπα με πλαίσια οριοθέτησης (bounding boxes), σημεία αναφοράς (μάτια, μύτη, στόμα) και βαθμολογίες εμπιστοσύνης |
| **Face Mesh** | `cvml-face-mesh.h` | Παρακολουθεί λεπτομερή γεωμετρία προσώπου με πυκνά σημεία πλέγματος |

### Μοντέλο Προγραμματισμού

Κάθε εφαρμογή CVML ακολουθεί το ίδιο μοτίβο τεσσάρων βημάτων:

1. **Δημιουργία Context** — Το `amd::cvml::Context` διαχειρίζεται κοινόχρηστους πόρους όπως η καταγραφή (logging) και η επιλογή backend συμπερασμού.
2. **Δημιουργία Feature Object** — Δημιουργήστε στιγμιότυπο της συγκεκριμένης δυνατότητας (π.χ., `amd::cvml::DepthEstimation`) έναντι του context.
3. **Περιτύλιξη Δεδομένων Εισόδου** — Χρησιμοποιήστε το `amd::cvml::Image` για να ενσωματώσετε τον buffer εικόνας RGB χωρίς αντιγραφή δεδομένων.
4. **Εκτέλεση** — Καλέστε τη μέθοδο επεξεργασίας της δυνατότητας και διαβάστε τα αποτελέσματα.

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

### Backend Συμπερασμού (Inference)

Η βιβλιοθήκη επιλέγει αυτόματα το καλύτερο υλικό (GPU ή NPU) για κάθε λειτουργία. Μπορείτε επίσης να ορίσετε το backend ρητά:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```


> **Σημείωση:** Οι λειτουργίες που χρησιμοποιούν το backend ONNX για λειτουργίες NPU ενδέχεται να παρουσιάσουν μεγαλύτερη καθυστέρηση εκκίνησης κατά την πρώτη εκτέλεση. Οι επόμενες εκτελέσεις θα είναι ταχύτερες.

> **Σημείωση:** Εάν το πρόγραμμα οδήγησης NPU δεν είναι εγκατεστημένο στο σύστημα-στόχο, η βιβλιοθήκη Ryzen AI CVML θα επιστρέψει αυτόματα στο backend GPU για τις λειτουργίες συμπερασμού.

## Δημιουργία των Δειγματικών Εφαρμογών

Η βιβλιοθήκη CVML περιλαμβάνει έτοιμες προς μεταγλώττιση δειγματικές εφαρμογές για κάθε λειτουργία. Ας τις δημιουργήσουμε όλες μαζί.

1. Ορίστε τη μεταβλητή περιβάλλοντος `OPENCV_INSTALL_ROOT` ώστε να δείχνει στην εγκατάσταση OpenCV σας:

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

2. Δημιουργήστε τα δείγματα με το CMake:

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

   Μετά από μια επιτυχημένη δημιουργία, τα εκτελέσιμα βρίσκονται στη διαδρομή:

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

3. Πριν εκτελέσετε οποιοδήποτε δείγμα, βεβαιωθείτε ότι τα αρχεία χρόνου εκτέλεσης CVML είναι προσβάσιμα:

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

## Εκτέλεση Ανίχνευσης Προσώπου

Το δείγμα ανίχνευσης προσώπου εντοπίζει πρόσωπα σε μια εικόνα, βίντεο ή ζωντανή ροή κάμερας. Σχεδιάζει πλαίσια οριοθέτησης, βαθμολογίες εμπιστοσύνης, και πέντε σημεία αναφοράς προσώπου (δύο μάτια, μύτη, και δύο άκρα στόματος) σε κάθε ανιχνευμένο πρόσωπο.

Πρώτα, μεταβείτε στον φάκελο του εκτελέσιμου ανίχνευσης προσώπου:

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

Στη συνέχεια, κατεβάστε μια δειγματική εικόνα για χρήση ως είσοδο (φωτογραφία από [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), ελεύθερη προς χρήση μέσω του Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```


**Εκτελέστε την ανίχνευση προσώπου στη δειγματική εικόνα:**

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

Θα εμφανιστεί ένα παράθυρο που δείχνει την εικόνα με πλαίσια οριοθέτησης γύρω από τα ανιχνευμένα πρόσωπα, βαθμολογίες εμπιστοσύνης, και σημεία αναφοράς προσώπου (μάτια, μύτη, άκρα στόματος).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Αποθηκεύστε την σχολιασμένη έξοδο σε ένα αρχείο:**

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

**Χρησιμοποιήστε το ακριβές μοντέλο** για μεγαλύτερη ακρίβεια (με κόστος την ταχύτητα):

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

Η λειτουργία ανίχνευσης προσώπου προσφέρει δύο παραλλαγές μοντέλου:

| Μοντέλο | Ταχύτητα | Ακρίβεια | Καλύτερο Για |
|-------|-------|----------|----------|
| `fast` (προεπιλογή) | Υψηλότερα FPS | Καλή | Εφαρμογές κάμερας σε πραγματικό χρόνο |
| `precise` | Χαμηλότερα FPS | Άριστη | Ανάλυση φωτογραφιών, ανάγκες υψηλής ακρίβειας |


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

## Ενσωμάτωση του CVML στη Δική σας Εφαρμογή

Για να χρησιμοποιήσετε τη βιβλιοθήκη CVML στο δικό σας C++ έργο, προσθέστε την μέσω του `find_package` του CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Όπου το `AMD_CVML_SDK_ROOT` δείχνει στη ρίζα του φακέλου της βιβλιοθήκης Ryzen AI CVML. Στη συνέχεια, συμπεριλάβετε την κατάλληλη επικεφαλίδα για τη λειτουργία που θέλετε:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Επόμενα Βήματα

Για κάθε δείγμα παρακάτω, μεταβείτε πρώτα στον φάκελο εκτελέσιμων αρχείων του, ακολουθώντας το ίδιο μοτίβο με την ενότητα [Running Face Detection](#running-face-detection) παραπάνω (π.χ. `cd build\cvml-sample-depth-estimation\Release` σε Windows ή `cd build/cvml-sample-depth-estimation` σε Linux). Σε Windows, προσθέστε `.exe` σε κάθε εντολή (π.χ. `cvml-sample-depth-estimation.exe`).

- **Δοκιμάστε την Depth Estimation**: Εκτελέστε `cvml-sample-depth-estimation -i sample_face.jpg` για να δημιουργήσετε έναν έγχρωμο χάρτη βάθους — τα πιο κοντινά αντικείμενα εμφανίζονται με θερμά χρώματα, τα πιο μακρινά με ψυχρά χρώματα
- **Εξερευνήστε το Face Mesh**: Εκτελέστε `cvml-sample-face-mesh -i sample_face.jpg` για να δείτε πυκνή παρακολούθηση γεωμετρίας προσώπου με λεπτομερή σημεία πλέγματος
- **Επεξεργαστείτε αρχεία βίντεο**: Χρησιμοποιήστε τα flags `-i` και `-o` σε οποιοδήποτε δείγμα για να επεξεργαστείτε βίντεο (π.χ., `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Συγκρίνετε παραλλαγές μοντέλων**: Δοκιμάστε το `-m precise` σε σχέση με το προεπιλεγμένο `-m fast` στην ανίχνευση προσώπου για να δείτε από πρώτο χέρι την αντιστάθμιση ακρίβειας/ταχύτητας
- **Δημιουργήστε τη δική σας εφαρμογή**: Χρησιμοποιήστε την ενσωμάτωση CMake και το C++ API για να προσθέσετε λειτουργίες CVML στις δικές σας εφαρμογές C++
- **Συνδυάστε λειτουργίες**: Συνδέστε την ανίχνευση προσώπου με την εκτίμηση βάθους στην ίδια εφαρμογή για πλουσιότερη κατανόηση σκηνής
- **Περιηγηθείτε στον πηγαίο κώδικα**: Διαβάστε το [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) για τεκμηρίωση κεφαλίδων, επιπλέον δείγματα και λεπτομέρειες API