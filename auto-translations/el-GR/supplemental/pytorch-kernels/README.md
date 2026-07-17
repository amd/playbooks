<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Επισκόπηση

Γράψτε έναν πυρήνα GPU από το μηδέν, μεταγλωττίστε τον, εκκινήστε τον σε μια AMD GPU και παρακολουθήστε την αξιοποίηση να εκτοξεύεται. Αυτό το playbook δείχνει πώς λειτουργεί πραγματικά ο υπολογισμός GPU: γράψτε τον κώδικα του πυρήνα και εκτελέστε τον παράλληλα σε χιλιάδες νήματα.

> **Σημείωση**: Πρόκειται για ένα αρκετά σύνθετο playbook, το οποίο ενδέχεται να απαιτεί κάποια επιπλέον αποσφαλμάτωση και τροποποιήσεις.

## Τι θα Μάθετε

<!-- @os:windows -->
- Πώς λειτουργούν οι πυρήνες GPU: grids, blocks, threads και το μοντέλο ευρετηρίασης που τα αντιστοιχεί σε δεδομένα
- Πώς η στοίβα AMD ROCm/HIP σάς επιτρέπει να γράφετε κώδικα τύπου CUDA που εκτελείται σε AMD GPU χωρίς τροποποίηση
- Πώς να μεταγλωττίσετε έναν πυρήνα κατά την εκτέλεση χρησιμοποιώντας `torch.cuda._compile_kernel`
- Πώς να δημιουργήσετε μια εγγενή επέκταση C++ πυρήνα με `CUDAExtension` + pybind11, εισαγώγιμη από Python
<!-- @os:end -->
<!-- @os:linux -->
- Πώς λειτουργούν οι πυρήνες GPU: grids, blocks, threads και το μοντέλο ευρετηρίασης που τα αντιστοιχεί σε δεδομένα
- Πώς η στοίβα AMD ROCm/HIP σάς επιτρέπει να γράφετε κώδικα τύπου CUDA που εκτελείται σε AMD GPU χωρίς τροποποίηση
- Πώς να μεταγλωττίσετε έναν πυρήνα κατά την εκτέλεση χρησιμοποιώντας `torch.cuda._compile_kernel`
- Πώς να δημιουργήσετε μια εγγενή επέκταση C++ πυρήνα με `CUDAExtension` + pybind11, εισαγώγιμη από Python
- Πώς να μετράτε τον χρόνο εκτέλεσης πυρήνα και να παρακολουθείτε ζωντανά την αξιοποίηση GPU με `amd-smi`
<!-- @os:end -->

---

Αυτό το playbook καλύπτει δύο προσεγγίσεις για την ανάπτυξη πυρήνων:

<!-- @os:windows -->
| Προσέγγιση | Σημείο εισόδου |
|---|---|
| **JIT Μεταγλώττιση** | `torch.cuda._compile_kernel`, γράψτε έναν πυρήνα ως συμβολοσειρά Python, χωρίς βήμα δημιουργίας |
| **Επέκταση C++** | `CUDAExtension` + pybind11: μεταγλωττίστε ένα αρχείο `.cu` σε εγγενές `.pyd` και εισαγάγετέ το |
<!-- @os:end -->
<!-- @os:linux -->
| Προσέγγιση | Σημείο εισόδου |
|---|---|
| **JIT Μεταγλώττιση** | `torch.cuda._compile_kernel`, γράψτε έναν πυρήνα ως συμβολοσειρά Python, χωρίς βήμα δημιουργίας |
| **Επέκταση C++** | `CUDAExtension` + pybind11: μεταγλωττίστε ένα αρχείο `.cu` σε εγγενές `.so` και εισαγάγετέ το |
<!-- @os:end -->

Και οι δύο προσεγγίσεις εκτελούνται σε AMD GPU. Αυτό είναι εφικτό επειδή η έκδοση ROCm του PyTorch αντιστοιχεί ολόκληρη την επιφάνεια CUDA API στο HIP. Αυτό σημαίνει ότι το `torch.cuda`, το `CUDAExtension` και η σύνταξη πυρήνων CUDA λειτουργούν διαφανώς σε AMD υλικό.

---

## Υπόβαθρο

### Τι είναι ένας Πυρήνας GPU;

Ένας πυρήνας GPU είναι μια συνάρτηση που εκτελείται παράλληλα σε χιλιάδες νήματα GPU ταυτόχρονα. Σε αντίθεση με μια συνάρτηση CPU που εκτελείται μία φορά ανά κλήση, ένας πυρήνας εκκινείται με ένα **grid** από **blocks**, καθένα από τα οποία περιέχει πολλά **threads**, που εκτελούν όλα τον ίδιο κώδικα σε διαφορετικά δεδομένα.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Μοντέλο Ευρετηρίασης Νημάτων

Κατά την εκκίνηση ενός πυρήνα ορίζετε δύο διαστάσεις:

| Μεταβλητή | Σημασία |
|---|---|
| `gridDim` | Αριθμός blocks στο grid |
| `blockDim` | Αριθμός νημάτων ανά block |

Κάθε νήμα έχει πρόσβαση σε τρεις ενσωματωμένες μεταβλητές μόνο για ανάγνωση:

| Μεταβλητή | Σημασία |
|---|---|
| `blockIdx.x` | Σε ποιο block ανήκει αυτό το νήμα |
| `blockDim.x` | Αριθμός νημάτων σε ένα block |
| `threadIdx.x` | Δείκτης νήματος εντός του block του |

### Καθολικό Αναγνωριστικό Νήματος

Αυτές οι μεταβλητές συνδυάζονται για τον υπολογισμό ενός παγκοσμίως μοναδικού δείκτη νήματος:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Συνολικά νήματα = `gridDim.x * blockDim.x`. Κάθε νήμα επεξεργάζεται ένα στοιχείο ανεξάρτητα. Αυτή είναι η βάση του **παραλληλισμού δεδομένων**. Η ίδια λειτουργία εκτελείται σε πολλά στοιχεία ταυτόχρονα, χωρίς εξάρτηση μεταξύ νημάτων.

---

### Μοντέλο Εκτέλεσης GPU: Wavefronts

Οι AMD GPU εκτελούν νήματα σε ομάδες των **32** που ονομάζονται **wavefronts**. Όλα τα νήματα σε ένα wavefront εκτελούν την ίδια εντολή ταυτόχρονα. Αυτό επηρεάζει τις βέλτιστες επιλογές μεγέθους block (256 νήματα = 8 wavefronts = καλή αποδοτικότητα χρονοπρογραμματισμού).

### Προγραμματισμός AMD GPU: HIP + ROCm

Το **ROCm** είναι η ανοιχτού κώδικα στοίβα υπολογισμού GPU της AMD (οδηγοί, μεταγλωττιστές, βιβλιοθήκες, χρόνος εκτέλεσης). Το **HIP** βρίσκεται από πάνω, σχεδιασμένο να είναι συντακτικά πανομοιότυπο με το CUDA. Η έκδοση ROCm του PyTorch αντιστοιχεί διαφανώς το `torch.cuda.*` στο HIP, οπότε ο ίδιος κώδικας λειτουργεί σε AMD GPU.

---

### PyTorch + AMD/HIP

Το PyTorch διαθέτει έκδοση ROCm όπου η επιφάνεια CUDA API (`torch.cuda.*`) υποστηρίζεται διαφανώς από το HIP. Αυτό σημαίνει:

- Το `torch.cuda.is_available()` λειτουργεί σε AMD GPU με ROCm
- Το `tensor.to("cuda")` δεσμεύει μνήμη στην AMD GPU
- Το `torch.version.hip` εκθέτει την έκδοση HIP

Το PyTorch εκθέτει επίσης το `torch.cuda._compile_kernel()`, μια υψηλού επιπέδου συντόμευση για JIT-μεταγλώττιση μιας ακατέργαστης συμβολοσειράς πυρήνα και επιστροφή ενός καλέσιμου αντικειμένου, χωρίς να απαιτείται ξεχωριστό βήμα δημιουργίας.

---

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Προαπαιτούμενων Λογισμικού
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Προαπαιτούμενα - Windows
- Εγκαταστήστε την πιο πρόσφατη έκδοση: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv με ROCm+Pytorch ήδη εγκατεστημένο.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env --system-site-packages
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Παραχωρήστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και επανασυνδεθείτε για να τεθεί σε ισχύ):

```bash
sudo usermod -aG render,video $LOGNAME
```

Στο Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv kernel-env
source kernel-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source kernel-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
Στα Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (π.χ.
> ορίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.

<!-- @os:end -->
### Εγκατάσταση Βασικών Εξαρτήσεων
<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:rocm,pytorch -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,rocm,pytorch -->
<!-- @device:end -->

<!-- @device:halo_box -->
> **Σημείωση:** Για αυτό το playbook, το ROCm και το PyTorch πρέπει να εγκατασταθούν στο εικονικό περιβάλλον ακόμα και στο Ryzen AI Halo, καθώς η μεταγλώττιση προσαρμοσμένου πυρήνα απαιτεί τις πλήρεις κεφαλίδες ανάπτυξης.

Εγκατάσταση ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Εγκατάσταση PyTorch:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "torch==2.11.0+rocm7.13.0" "torchvision==0.26.0+rocm7.13.0" "torchaudio==2.11.0+rocm7.13.0"
```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```bash
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-installed-package-versions timeout=60 hidden=True setup=activate-venv -->
```powershell
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"
```
<!-- @test:end -->
<!-- @os:end -->
---

### Εγκατάσταση Πρόσθετων Εξαρτήσεων

<!-- @os:linux -->
Εγκαταστήστε την αλυσίδα εργαλείων κατασκευής Linux C/C++. Αυτή είναι μια εξάρτηση σε επίπεδο συστήματος και απαιτείται για τις αναλυτικές παρουσιάσεις επέκτασης C++ επειδή το `CUDAExtension` κατασκευάζει εγγενή modules `.so` από αρχεία `.cu`.

Εκτελέστε αυτό μία φορά στο μηχάνημα Linux, εκτός του δημιουργημένου εικονικού περιβάλλοντος Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Αφού ενεργοποιήσετε το εικονικό περιβάλλον `kernel-env`, εγκαταστήστε τις εξαρτήσεις κατασκευής Python:
<!-- @test:id=install-deps timeout=60 setup=activate-venv -->
```bash
python -m pip install "setuptools<82" wheel ninja
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-linux-build-tools timeout=60 hidden=True -->
```bash
set -euo pipefail

command -v gcc
command -v g++
gcc --version
g++ --version

echo "OK: Linux C/C++ build toolchain is available."
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Βεβαιωθείτε ότι είναι εγκατεστημένο το [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ή [νεότερη έκδοση](https://visualstudio.microsoft.com/vs/community/) με τον φόρτο εργασίας **Ανάπτυξη επιφάνειας εργασίας με C++**.

> **Σημείωση**: Αυτή η ρύθμιση περιβάλλοντος C++ του Visual Studio απαιτείται μόνο για την προσέγγιση **Επέκτασης C++**. Δεν απαιτείται για την προσέγγιση JIT Compilation.

Ανοίξτε ένα τερματικό PowerShell και εκτελέστε τις παρακάτω εντολές πριν από την κατασκευή της επέκτασης C++.

**Βήμα 1: Εντοπισμός του εγκατεστημένου περιβάλλοντος C++ του Visual Studio**

**(Α) Εντοπισμός του `vswhere.exe`, το οποίο εγκαθίσταται με το Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(Β) Εύρεση του `vcvars64.bat` από το Visual Studio 2022 ή νεότερο με εργαλεία κατασκευής C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(Γ) Εκτύπωση του χρησιμοποιούμενου περιβάλλοντος C++ του Visual Studio**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Βήμα 2: Ενεργοποίηση του περιβάλλοντος κατασκευής C++ του Visual Studio**

**(Α) Εκτέλεση του `vcvars64.bat` και καταγραφή του περιβάλλοντος που ορίζει**

Αυτό καθιστά διαθέσιμα τα `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` και τις διαδρομές Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(Β) Εισαγωγή των μεταβλητών περιβάλλοντος του Visual Studio σε αυτή τη συνεδρία PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Βήμα 3: Επαλήθευση ότι ο μεταγλωττιστής Microsoft C++ είναι διαθέσιμος**

```powershell
where.exe cl
```

<!-- @test:id=verify-visual-studio-community timeout=60 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Detected Visual Studio installations:"
& $VsWhere -all -products * -format table | Out-Host

$VcvarsList = & $VsWhere `
  -all `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat"
if (-not $VcvarsList) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
$Vcvars = $VcvarsList | Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using vcvars64.bat from Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}

$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}

where.exe cl

Write-Host "OK: Visual Studio C++ build environment is available."
```
<!-- @test:end -->
<!-- @os:end -->

#### Ορισμός Μεταβλητών Περιβάλλοντος
<!-- @os:linux -->
<!-- @test:id=set-env-variables-linux timeout=300 setup=activate-venv -->
```bash
rocm-sdk init # Initialize the devel libraries

# Get the active Python version (e.g. "3.13") so the path works with any Python release
PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:$LD_LIBRARY_PATH"
export PATH="$ROCM_HOME/bin:$PATH"

# Set compiler and build settings
export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=set-env-variables-windows timeout=300 setup=activate-venv -->
```powershell
rocm-sdk init # Initialize the devel libraries

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

# Set compiler and build settings
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
Επαληθεύστε ότι η AMD GPU είναι ορατή με:
<!-- @test:id=amd-smi-linux timeout=60 setup=activate-venv -->
```bash
amd-smi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-setup-rocm-pytorch-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

echo "Installed ROCm/PyTorch packages:"
python -m pip list | grep -E '^(rocm|rocm-sdk|torch|torchvision|torchaudio)' || true

test -d "$ROCM_HOME"
test -d "$ROCM_HOME/bin"
test -d "$ROCM_HOME/lib"

test -f "$ROCM_HOME/lib/libhiprtc.so" || ls "$ROCM_HOME/lib"/libhiprtc.so*
test -f "$ROCM_HOME/lib/libroctx64.so" || ls "$ROCM_HOME/lib"/libroctx64.so*

hipcc --version >/dev/null
rocminfo >/dev/null

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=env-setup-rocm-pytorch-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }
$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"
$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Write-Host "ROCM_ROOT=$ROCM_ROOT"
Write-Host "ROCM_BIN=$ROCM_BIN"

Write-Host "Installed ROCm/PyTorch packages:"
python -m pip list | Select-String "rocm|torch|torchvision|torchaudio"

Get-ChildItem -Path $ROCM_ROOT -Recurse -Filter "hiprtc*.dll" | Select-Object -First 10 FullName | Out-Host

hipcc --version | Out-Host
hipinfo | Out-Host

$code = @'
import os
import sys
import torch

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

print("torch:", torch.__version__)
print("HIP:", torch.version.hip)
print("CUDA available via HIP:", torch.cuda.is_available())

if torch.version.hip is None:
    raise SystemExit("PyTorch is not a ROCm/HIP build.")

if not torch.cuda.is_available():
    raise SystemExit("torch.cuda.is_available() is False. AMD GPU is not available through HIP.")

print("Device:", torch.cuda.get_device_name(0))
print("OK: ROCm PyTorch environment is ready")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Λήψη Απαιτούμενων Αρχείων

Δημιουργήστε την παρακάτω δομή καταλόγου δημιουργώντας τους **2 νέους φακέλους** και κατεβάζοντας τα αντίστοιχα αρχεία:

| Κατάλογος | Αρχεία προς Λήψη | Περιγραφή |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Αρχεία JIT και επέκτασης C++ για τον πυρήνα πρόσθεσης διανυσμάτων |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Αρχεία JIT και επέκτασης C++ για τον πυρήνα πολλαπλασιασμού πινάκων |


## Αναλυτικές Παρουσιάσεις

### Αναλυτική Παρουσίαση 1: Πρόσθεση Διανυσμάτων

#### Προσέγγιση Α: JIT Compilation

Το JIT (Just-In-Time) compilation σημαίνει ότι ο πυρήνας γράφεται ως ακατέργαστη συμβολοσειρά C++ μέσα στην Python και μεταγλωττίζεται κατά την εκτέλεση, χωρίς να απαιτούνται επιπλέον βήματα κατασκευής.

Για να χρησιμοποιήσετε το [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), βεβαιωθείτε ότι έχει ληφθεί και εκτελέστε:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Βασικά Αποσπάσματα Κώδικα**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        for (int i = 0; i < 1000; i++)
            data[idx] += 1.0f;
    }
}
"""


# Snippet 2: Compile the kernel string. PyTorch calls hipcc under the hood with ROCm
add_one_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "add_one")

x = torch.ones(100_000_000, dtype=torch.float32, device="cuda")
n = x.numel()
block_size = 256
grid_size = (n + block_size - 1) // block_size


# Snippet 3: Launch: specify the grid/block dimensions and pass tensor arguments directly
for _ in range(200):
    add_one_kernel(
        grid=(grid_size, 1, 1),
        block=(block_size, 1, 1),
        args=[x, n],
    )


# Snippet 4: Test the output
print("First 5 elements:", x[:5].cpu()) 
#Expected output: tensor([200001., 200001., 200001., 200001., 200001.])
```
<!-- @os:linux -->
> **Συμβουλή**: Το script δημιουργεί επίσης ένα νήμα παρασκηνίου που ελέγχει το `amd-smi` κάθε 100ms για να καταγράφει την μέγιστη και μέση χρήση GPU κατά τη διάρκεια εκτέλεσης του πυρήνα.
<!-- @os:end -->

> **Σημείωση**: **Γιατί το Block Size είναι 256;** <br>
> - Ο πυρήνας χρησιμοποιεί **256 νήματα ανά block** επειδή ευθυγραμμίζεται καλά με το **μοντέλο εκτέλεσης wavefront των AMD GPU**.
> - Υπενθυμίζεται ότι το AMD hardware εκτελεί νήματα σε ομάδες των 32 νημάτων, με αποτέλεσμα 8 wavefronts ανά block. (8 wavefronts x 32 νήματα = 1 block)


**Τι κάνει ο φόρτος εργασίας:**

Ο πυρήνας προσθέτει τεχνητά επιπλέον εργασία για να επιδείξει τη χρήση GPU:

- **100.000.000 στοιχεία** στον tensor
- **Ο εσωτερικός βρόχος εκτελείται 1.000 φορές** ανά στοιχείο ανά εκκίνηση πυρήνα  
- **200 εκκινήσεις πυρήνα** συνολικά

**Μαθηματικά:**  
- Κάθε στοιχείο: αυξάνεται κατά 1 × 1.000 επαναλήψεις × 200 εκκινήσεις = 200.000  
- Τελικό αποτέλεσμα: 1,0 (αρχική τιμή) + 200.000 (προσθέσεις) = 200.001,0

**Γιατί ο εσωτερικός βρόχος;**  
- Χωρίς τον βρόχο `for (int i = 0; i < 1000; i++)`, οι 200 εκκινήσεις θα ολοκληρώνονταν άμεσα και τα εργαλεία παρακολούθησης δεν θα κατέγραφαν ουσιαστική χρήση GPU. Η τεχνητή εργασία κάνει κάθε εκτέλεση πυρήνα αρκετά μεγάλη ώστε τα εργαλεία παρακολούθησης να μετρούν την απόδοση.

<!-- @os:linux -->
**Αναμενόμενη έξοδος:** [Οι αριθμοί απόδοσης θα ποικίλλουν]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Στα Windows, το `amd-smi` δεν υποστηρίζεται. Για να παρακολουθείτε τη χρήση GPU, μπορείτε να χρησιμοποιήσετε τη Διαχείριση Εργασιών, όπου θα πρέπει να δείτε μια σύντομη αύξηση χρήσης όταν εκτελείτε το πρόγραμμα.

**Αναμενόμενη έξοδος:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Μπράβο! Μόλις εκτελέσατε τον πρώτο σας πυρήνα GPU.**

<!-- @os:linux -->
<!-- @test:id=vector-addition-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
'''

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
PY
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-addition-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] += 1.0f;
    }
}
"""

kernel = torch.cuda._compile_kernel(kernel_source, "add_one")

x = torch.ones(1024, dtype=torch.float32, device="cuda")
n = x.numel()
block = 256
grid = (n + block - 1) // block

kernel(
    grid=(grid, 1, 1),
    block=(block, 1, 1),
    args=[x, n],
)

torch.cuda.synchronize()

if not torch.allclose(x, torch.full_like(x, 2.0)):
    raise SystemExit(f"Vector JIT output mismatch. First values: {x[:5].cpu()}")

print("OK: vector addition JIT kernel compiled and ran correctly")
'@

$code | python -
```
<!-- @test:end -->
<!-- @os:end -->

---
#### Προσέγγιση Β: Επέκταση C++

Η δεύτερη προσέγγιση είναι πιο χειροκίνητη: γράψτε τον πυρήνα και τη σύνδεση Python σε ένα μόνο αρχείο `.cu`, μεταγλωττίστε το εγγενώς χρησιμοποιώντας το σύστημα κατασκευής του PyTorch, και εισαγάγετέ το στην Python.

<!-- @os:windows -->
> **Σημείωση**: Η προσέγγιση Επέκτασης C++ απαιτεί το περιβάλλον κατασκευής C++ του Visual Studio, επειδή το PyTorch μεταγλωττίζει το αρχείο πηγαίου κώδικα `.cu` σε ένα εγγενές module επέκτασης `.pyd`. Η κατασκευή αυτής της εγγενούς επέκτασης εξαρτάται από την αλυσίδα εργαλείων Microsoft C++ (μεταγλωττιστής, σύνδεσμος και εργαλεία κατασκευής) που παρέχεται από το Visual Studio. Εκτελέστε τις εντολές ενεργοποίησης του Visual Studio από την ενότητα ρύθμισης πριν από την κατασκευή της επέκτασης.
<!-- @os:end -->

Κατεβάστε τα παρακάτω αρχεία εάν δεν το έχετε κάνει ήδη:
<!-- @os:windows -->
| Αρχείο | Ρόλος |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11, όλα σε ένα αρχείο |
| [setup.py](assets/Vector_Addition/setup.py) | Σενάριο κατασκευής, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Σενάριο Python που εκτελεί τα κατασκευασμένα αντικείμενα |
<!-- @os:end -->

<!-- @os:linux -->
| Αρχείο | Ρόλος |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11, όλα σε ένα αρχείο |
| [setup.py](assets/Vector_Addition/setup.py) | Σενάριο κατασκευής, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Σενάριο Python που εκτελεί τα κατασκευασμένα αντικείμενα |
<!-- @os:end -->

#### **Βήμα 1: Ο πυρήνας, ο εκκινητής και η σύνδεση** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
// GPU kernel, one thread per element
__global__ void add_one(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) data[idx] += 1.0f;
}

// Launcher, bridges torch::Tensor to raw pointer, sets grid/block, runs kernel
void add_one_launcher(torch::Tensor tensor) {
    int n = tensor.numel();
    float* data = tensor.data_ptr<float>();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    add_one<<<grid_size, block_size>>>(data, n);
    hipDeviceSynchronize();
}

// Python binding, exposes add_one_launcher as add_one_ext.add_one
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("add_one", &add_one_launcher, "Add one kernel (HIP)");
}
```

>**Συμβουλή**: Γιατί να χρησιμοποιήσετε `hipDeviceSynchronize()`; <br>
> - Οι εκκινήσεις πυρήνα GPU είναι ασύγχρονες. Όταν η CPU εκτελεί `add_one<<<grid_size, block_size>>>(data, n);` θα εκτελούσε αμέσως την επόμενη εντολή χωρίς να περιμένει το GPU. Το `hipDeviceSynchronize()` αναγκάζει την CPU να περιμένει μέχρι να ολοκληρωθεί ο πυρήνας GPU.

#### **Βήμα 2: Κατασκευή**
```bash
pip install --no-build-isolation -v .
```
>**Σημείωση**: Αυτή η εντολή αναζητά το `setup.py` στον τρέχοντα κατάλογο για να κατασκευάσει το αρχείο .cu που έχουμε δημιουργήσει.


Το `CUDAExtension` είναι ένα βοηθητικό εργαλείο κατασκευής CUDA από το `torch.utils.cpp_extension`. Με το ROCm, το PyTorch **αντιστοιχίζει εκ νέου το `CUDAExtension` ώστε να χρησιμοποιεί `hipcc`** αντί για `nvcc`. Το ROCm παρεμβαίνει στη διαδρομή κατασκευής και την δρομολογεί μέσω του μεταγλωττιστή HIP, μεταφέροντας τον κώδικα CUDA στην AMD.

Αυτό παράγει τα παρακάτω αρχεία:
<!-- @os:windows -->
- `build/`:  κατάλογος με τα αρχεία `.pyd`
- `add_one_kernel.hip`:  η πηγή HIP που δημιουργήθηκε από την μετατροπή του αρχείου `.cu` σε HIP· αυτό είναι που μεταγλώττισε πραγματικά το `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  κατάλογος με τα αρχεία `.so`
- `add_one_kernel.hip`:  η πηγή HIP που δημιουργήθηκε από την μετατροπή του αρχείου `.cu` σε HIP· αυτό είναι που μεταγλώττισε πραγματικά το `hipcc`
<!-- @os:end -->

#### **Βήμα 3: Χρήση από Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Εκτελέστε αυτό το σενάριο για να δείτε τον πυρήνα σε δράση:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Αναμενόμενη έξοδος:**
```
Before: tensor([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], device='cuda:0')
After: tensor([2., 2., 2., 2., 2., 2., 2., 2., 2., 2.], device='cuda:0')
```

<!-- @os:linux -->
<!-- @test:id=vector-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Vector_Addition

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=vector-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Vector_Addition"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import add_one_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

x = torch.ones(16, dtype=torch.float32, device="cuda")
add_one_ext.add_one(x)
torch.cuda.synchronize()

expected = torch.full_like(x, 2.0)
if not torch.allclose(x, expected):
    raise SystemExit(f"Vector extension output mismatch. Got: {x.cpu()}")

print("OK: vector addition C++ extension built, imported, and ran correctly")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

### Παράδειγμα 2: Πολλαπλασιασμός Πινάκων

Ο πολλαπλασιασμός πινάκων υπολογίζει το **C = A × B** όπου:
- **A** είναι M×N (γραμμές × στήλες)
- **B** είναι N×K  
- **C** είναι M×K (το αποτέλεσμα)

Κάθε στοιχείο εξόδου ορίζεται ως:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Κάθε στοιχείο του C υπολογίζεται ανεξάρτητα, καθιστώντας αυτό ιδανικό για παραλληλισμό GPU.

#### Πώς Αντιστοιχίζεται σε Νήματα GPU

Σε αντίθεση με την πρόσθεση διανυσμάτων (1D), ο πολλαπλασιασμός πινάκων παράγει μια **έξοδο 2D**, οπότε χρησιμοποιούμε ένα **πλέγμα νημάτων 2D**:

| | Πρόσθεση Διανυσμάτων | Πολλαπλασιασμός Πινάκων |
|---|---|---|
| **Σχήμα εξόδου** | Πίνακας 1D | Πίνακας 2D (M×K) |
| **Αντιστοίχιση νημάτων** | 1 νήμα → 1 στοιχείο | 1 νήμα → 1 στοιχείο εξόδου |
| **Μοτίβο εκκίνησης** | Πλέγμα 1D: `(grid_x, 1, 1)` | Πλέγμα 2D: `(grid_x, grid_y, 1)` |
| **Μέγεθος μπλοκ** | `(256, 1, 1)` | `(16, 16, 1)` = 256 νήματα |

Κάθε νήμα υπολογίζει ένα στοιχείο του πίνακα εξόδου C. Το νήμα στη θέση `(row, col)` υπολογίζει το `C[row][col]` πολλαπλασιάζοντας την αντίστοιχη γραμμή του A με την αντίστοιχη στήλη του B.

**Διάταξη Μνήμης**: Η μνήμη GPU είναι επίπεδη (1D), αλλά οι πίνακες αποθηκεύονται γραμμή-γραμμή. Για πρόσβαση στο `A[row][col]`, ο πυρήνας χρησιμοποιεί `A[row * N + col]`.


#### Προσέγγιση Α: Μεταγλώττιση JIT:

Όπως στο Παράδειγμα 1, ο πυρήνας γράφεται ως ακατέργαστη συμβολοσειρά C++ μέσα στην Python και μεταγλωττίζεται κατά την εκτέλεση μέσω του ενσωματωμένου JIT του PyTorch.


Για να χρησιμοποιήσετε το [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), βεβαιωθείτε ότι έχει ληφθεί και εκτελέστε:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Βασικά Αποσπάσματα Κώδικα**
```python
import torch

# Snippet 1: Kernel source as a string
KERNEL_SOURCE = """
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

# Snippet 2: Creating the Matrix - 2D indexing to map threads onto the M×K output matrix
# Inputs: A is M x N, B is N x K, C is M x K
M, N, K = 1024, 512, 768

A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK


# Snippet 3: Compile the kernel string
matmul_kernel = torch.cuda._compile_kernel(KERNEL_SOURCE, "matmul")


# Snippet 4:. Launch with a 2D grid, grid_x covers columns (K), grid_y covers rows (M)
BLOCK = 16
matmul_kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()
print(f"Max error vs torch.mm: {max_err:.6f}")
```

Το σενάριο επαληθεύει το αποτέλεσμα έναντι του `torch.mm` με μικρή ανοχή. Η αριθμητική κινητής υποδιαστολής σε GPU μπορεί να παράγει μικρές αριθμητικές διαφορές σε σύγκριση με υλοποιήσεις CPU λόγω της σειράς παράλληλης αναγωγής.

<!-- @os:linux -->
**Αναμενόμενη έξοδος:** [Οι αριθμοί απόδοσης θα ποικίλλουν]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Στα Windows, το `amd-smi` δεν υποστηρίζεται. Για να παρακολουθήσετε τη χρήση GPU, μπορείτε να χρησιμοποιήσετε τη Διαχείριση Εργασιών, όπου θα πρέπει να δείτε μια σύντομη αύξηση χρήσης όταν εκτελείτε το πρόγραμμα.

**Αναμενόμενη έξοδος:**
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
No GPU Usage captured.
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=matmul-jit-linux timeout=300 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

export CC=clang
export CXX=clang
export DISTUTILS_USE_SDK=1

python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r'''
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
'''

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-jit-windows timeout=300 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

kernel_source = r"""
extern "C"
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}
"""

M, N, K = 32, 16, 24
A = torch.randn(M, N, dtype=torch.float32, device="cuda")
B = torch.randn(N, K, dtype=torch.float32, device="cuda")
C = torch.zeros(M, K, dtype=torch.float32, device="cuda")

kernel = torch.cuda._compile_kernel(kernel_source, "matmul")

BLOCK = 16
grid_x = (K + BLOCK - 1) // BLOCK
grid_y = (M + BLOCK - 1) // BLOCK

kernel(
    grid=(grid_x, grid_y, 1),
    block=(BLOCK, BLOCK, 1),
    args=[A, B, C, M, N, K],
)

torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul JIT max error too high: {max_err}")

print(f"OK: matmul JIT kernel compiled and ran correctly; max_err={max_err:.6f}")
'@

$code | python -
```
<!-- @test:end --> 
<!-- @os:end -->
#### Προσέγγιση Β: Επέκταση C++

Η δεύτερη προσέγγιση είναι πιο χειροκίνητη: γράψτε τον πυρήνα και τη σύνδεση Python σε ένα μόνο αρχείο `.cu`, μεταγλωττίστε το εγγενώς χρησιμοποιώντας το σύστημα κατασκευής του PyTorch, και εισαγάγετέ το στην Python.

<!-- @os:windows -->
> **Σημείωση**: Η προσέγγιση Επέκτασης C++ απαιτεί το περιβάλλον κατασκευής Visual Studio C++ επειδή το PyTorch μεταγλωττίζει το αρχείο πηγαίου κώδικα `.cu` σε ένα εγγενές module επέκτασης `.pyd`. Η κατασκευή αυτής της εγγενούς επέκτασης εξαρτάται από την αλυσίδα εργαλείων Microsoft C++ (μεταγλωττιστής, σύνδεσμος και εργαλεία κατασκευής) που παρέχεται από το Visual Studio. Εκτελέστε τις εντολές ενεργοποίησης του Visual Studio από την ενότητα ρύθμισης πριν από την κατασκευή της επέκτασης.
<!-- @os:end -->

Κατεβάστε τα παρακάτω αρχεία εάν δεν το έχετε κάνει ήδη:
<!-- @os:windows -->
| Αρχείο | Ρόλος |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Σενάριο κατασκευής, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Σενάριο Python που εκτελεί τα κατασκευασμένα αντικείμενα |
<!-- @os:end -->
<!-- @os:linux -->
| Αρχείο | Ρόλος |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Σενάριο κατασκευής, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Σενάριο Python που εκτελεί τα κατασκευασμένα αντικείμενα |
<!-- @os:end -->

#### **Βήμα 1: Ο πυρήνας, ο εκκινητής και η σύνδεση** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
```cpp
#include <torch/extension.h>
#include <hip/hip_runtime.h>
#define BLOCK 16

// GPU kernel, one thread per output element of C
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < M && col < K) {
        float sum = 0.0f;
        for (int n = 0; n < N; n++) {
            sum += A[row * N + n] * B[n * K + col];
        }
        C[row * K + col] = sum;
    }
}

// Launcher, extracts dims from torch::Tensor, allocates C, sets 2D grid/block
torch::Tensor matmul_launcher(torch::Tensor A, torch::Tensor B) {
    int M = A.size(0), N = A.size(1), K = B.size(1);
    auto C = torch::zeros({M, K}, A.options());

    dim3 block(BLOCK, BLOCK);
    dim3 grid((K + BLOCK - 1) / BLOCK, (M + BLOCK - 1) / BLOCK);

    matmul<<<grid, block>>>(A.data_ptr<float>(), B.data_ptr<float>(),
                            C.data_ptr<float>(), M, N, K);
    hipDeviceSynchronize();
    return C;
}

// Python binding, exposes matmul_launcher as matmul_ext.matmul
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("matmul", &matmul_launcher, "Naive matmul kernel (HIP): A(M,N) @ B(N,K) -> C(M,K)");
}
```

Σε σύγκριση με το `add_one_launcher` στην Αναλυτική Παρουσίαση 1, ο εκκινητής εδώ:
- Δέχεται δύο tensors εισόδου αντί για ένα
- Εξάγει και τις τρεις διαστάσεις (M, N, K) από τα σχήματα των tensors, χωρίς χειροκίνητη μεταβίβαση μεγέθους από την Python
- Δεσμεύει και επιστρέφει το tensor εξόδου C, αντί να τροποποιεί επί τόπου
- Χρησιμοποιεί `dim3` τόσο για το πλέγμα όσο και για το μπλοκ για να εκφράσει το 2D σχήμα εκκίνησης

#### **Βήμα 2: Κατασκευή**
```bash
pip install --no-build-isolation -v .
```
>**Σημείωση**: Αυτή η εντολή αναζητά το `setup.py` στον τρέχοντα κατάλογο για να κατασκευάσει το αρχείο .cu που έχουμε δημιουργήσει.


Αυτό παράγει τα παρακάτω αρχεία:
<!-- @os:windows -->
- `build/`:  κατάλογος με τα αρχεία `.pyd`
- `matmul_kernel.hip`:  η πηγή HIP που δημιουργήθηκε από την μετατροπή του αρχείου `.cu` σε HIP· αυτό είναι που μεταγλωττίστηκε πραγματικά από το `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  κατάλογος με τα αρχεία `.so`
- `matmul_kernel.hip`:  η πηγή HIP που δημιουργήθηκε από την μετατροπή του αρχείου `.cu` σε HIP· αυτό είναι που μεταγλωττίστηκε πραγματικά από το `hipcc`
<!-- @os:end -->

#### **Βήμα 3: Χρήση από Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Εκτελέστε αυτό το σενάριο για να δείτε τον πυρήνα σε δράση:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Αναμενόμενη έξοδος:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Εξαιρετικό! Μόλις υλοποιήσατε πολλαπλασιασμό πινάκων στο GPU.** Αυτό είναι ένα σημαντικό ορόσημο επειδή ο πολλαπλασιασμός πινάκων αποτελεί τη ραχοκοκαλιά των σύγχρονων λειτουργιών μηχανικής μάθησης όπως:
- Στρώματα νευρωνικών δικτύων
- Μηχανισμοί προσοχής
- Ενσωματώσεις
- Transformers

<!-- @os:linux -->
<!-- @test:id=matmul-extension-linux timeout=600 hidden=True setup=activate-venv -->
```bash
set -euo pipefail

rocm-sdk init

PY_MM="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
export ROCM_HOME="$VIRTUAL_ENV/lib/python${PY_MM}/site-packages/_rocm_sdk_devel"
export LD_LIBRARY_PATH="$ROCM_HOME/lib:${LD_LIBRARY_PATH:-}"
export PATH="$ROCM_HOME/bin:$PATH"

cd Matrix_Multiplication

python -m pip install --no-build-isolation -v .

python - <<'PY'
import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
PY
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=matmul-extension-windows timeout=600 hidden=True setup=activate-venv -->
```powershell
$ErrorActionPreference = "Stop"

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}

$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1
if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
Write-Host "Using Visual Studio C++ environment: $Vcvars"

$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
$VsEnv | Select-String "Developer Command Prompt|Environment initialized|cl.exe" | Out-Host
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {[System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')}
}
where.exe cl

rocm-sdk init

$ROCM_ROOT = (rocm-sdk path --root).Trim()
$ROCM_BIN = (rocm-sdk path --bin).Trim()

$RocmPathEntries = @(
  $ROCM_BIN,
  "$ROCM_ROOT\bin",
  "$ROCM_ROOT\lib",
  "$ROCM_ROOT\lib\llvm\bin"
) | Where-Object { $_ -and (Test-Path $_) }

$env:PATH = (($RocmPathEntries + @($env:PATH)) -join ";")

$env:ROCM_HOME = $ROCM_ROOT
$env:HIP_PATH = $ROCM_ROOT
$env:ROCM_BIN = $ROCM_BIN
$env:HIP_PLATFORM = "amd"

$env:CC = "clang-cl"
$env:CXX = "clang-cl"
$env:DISTUTILS_USE_SDK = "1"

Push-Location "Matrix_Multiplication"
try {
  python -m pip install --no-build-isolation -v .

  $code = @'
import os
import sys

if sys.platform == "win32":
    for key in ("ROCM_HOME", "HIP_PATH"):
        root = os.environ.get(key)
        if root:
            for subdir in ("bin", "lib", r"lib\llvm\bin"):
                path = os.path.join(root, subdir)
                if os.path.isdir(path):
                    os.add_dll_directory(path)

    rocm_bin = os.environ.get("ROCM_BIN")
    if rocm_bin and os.path.isdir(rocm_bin):
        os.add_dll_directory(rocm_bin)

import torch
import matmul_ext

if not torch.cuda.is_available():
    raise SystemExit("HIP GPU is not available.")

A = torch.randn(32, 16, dtype=torch.float32, device="cuda")
B = torch.randn(16, 24, dtype=torch.float32, device="cuda")

C = matmul_ext.matmul(A, B)
torch.cuda.synchronize()

C_ref = torch.mm(A, B)
max_err = (C - C_ref).abs().max().item()

if max_err > 1e-3:
    raise SystemExit(f"Matmul extension max error too high: {max_err}")

print(f"OK: matmul C++ extension built, imported, and ran correctly; max_err={max_err:.6f}")
'@

  $code | python -
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 
<!-- @os:end -->

---

## Επόμενα Βήματα

Μάθατε να γράφετε, να μεταγλωττίζετε και να εκκινείτε πυρήνες GPU χρησιμοποιώντας τόσο τη μεταγλώττιση JIT όσο και τις επεκτάσεις C++ για βασικές παράλληλες λειτουργίες.

**Βελτιστοποιήσεις απόδοσης:**
- **Κεραμοποίηση κοινής μνήμης** - Αποθήκευση προσωρινά μπλοκ δεδομένων για μείωση της πρόσβασης στη γενική μνήμη
- **Συνένωση μνήμης** - Βελτιστοποίηση μοτίβων πρόσβασης μνήμης για εύρος ζώνης

**Αλγόριθμοι πραγματικού κόσμου:**
- **2D Συνέλιξη** - Ένα μικρό φίλτρο (πυρήνας) ολισθαίνει πάνω από μια εικόνα, υπολογίζοντας κάθε pixel εξόδου από ένα σταθμισμένο άθροισμα γειτονικών pixels. Αυτό εισάγει υπολογισμούς stencil και κεραμοποίηση κοινής μνήμης, όπου τα νήματα επαναχρησιμοποιούν επικαλυπτόμενες περιοχές εικόνας για μείωση της πρόσβασης στη γενική μνήμη.
- **Συνάρτηση Softmax**: Το Softmax μετατρέπει ένα διάνυσμα αριθμών σε πιθανότητες που αθροίζουν στο 1, χρησιμοποιείται συνήθως στις εξόδους νευρωνικών δικτύων. Η αποδοτική υλοποίησή του στο GPU εισάγει παράλληλες αναγωγές και τεχνικές αριθμητικής σταθερότητας κατά την επεξεργασία μεγάλων διανυσμάτων.

**Ζητήματα παραγωγής:**
- **Διαχείριση σφαλμάτων** - Έλεγχος ορίων και διαχείριση συσκευής
- **Ενσωμάτωση PyTorch** - Προσαρμοσμένοι τελεστές με υποστήριξη autograd