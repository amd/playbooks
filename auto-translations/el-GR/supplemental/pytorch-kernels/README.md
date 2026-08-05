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

Γράψτε έναν πυρήνα GPU (GPU kernel) από την αρχή, μεταγλωττίστε τον, εκτελέστε τον σε μια GPU AMD, και παρακολουθήστε την αξιοποίηση να εκτοξεύεται. Αυτό το playbook δείχνει πώς λειτουργεί στην πραγματικότητα ο υπολογισμός GPU: γράψτε τον κώδικα του πυρήνα και εκτελέστε τον παράλληλα σε χιλιάδες νήματα.

> **Σημείωση**: Αυτό είναι ένα αρκετά περίπλοκο playbook, το οποίο ενδέχεται να απαιτεί επιπλέον αποσφαλμάτωση και τροποποιήσεις.

## Τι Θα Μάθετε

<!-- @os:windows -->
- Πώς λειτουργούν οι πυρήνες GPU: πλέγματα (grids), μπλοκ (blocks), νήματα (threads), και το μοντέλο ευρετηρίασης που τα αντιστοιχίζει σε δεδομένα
- Πώς το στοίβαγμα AMD ROCm/HIP σας επιτρέπει να γράφετε κώδικα τύπου CUDA που εκτελείται σε GPU της AMD χωρίς τροποποίηση
- Πώς να μεταγλωττίσετε έναν πυρήνα κατά τον χρόνο εκτέλεσης χρησιμοποιώντας το `torch.cuda._compile_kernel`
- Πώς να δημιουργήσετε μια εγγενή επέκταση πυρήνα C++ με `CUDAExtension` + pybind11, εισαγώγιμη από την Python
<!-- @os:end -->
<!-- @os:linux -->
- Πώς λειτουργούν οι πυρήνες GPU: πλέγματα (grids), μπλοκ (blocks), νήματα (threads), και το μοντέλο ευρετηρίασης που τα αντιστοιχίζει σε δεδομένα
- Πώς το στοίβαγμα AMD ROCm/HIP σας επιτρέπει να γράφετε κώδικα τύπου CUDA που εκτελείται σε GPU της AMD χωρίς τροποποίηση
- Πώς να μεταγλωττίσετε έναν πυρήνα κατά τον χρόνο εκτέλεσης χρησιμοποιώντας το `torch.cuda._compile_kernel`
- Πώς να δημιουργήσετε μια εγγενή επέκταση πυρήνα C++ με `CUDAExtension` + pybind11, εισαγώγιμη από την Python
- Πώς να μετρήσετε τον χρόνο εκτέλεσης πυρήνα και να παρακολουθείτε ζωντανά την αξιοποίηση GPU με το `amd-smi`
<!-- @os:end -->

---

Αυτό το playbook καλύπτει δύο προσεγγίσεις για την ανάπτυξη πυρήνων:

<!-- @os:windows -->
| Προσέγγιση | Σημείο εισόδου |
|---|---|
| **Μεταγλώττιση JIT** | `torch.cuda._compile_kernel`, γράψτε έναν πυρήνα ως συμβολοσειρά Python, χωρίς βήμα κατασκευής |
| **Επέκταση C++** | `CUDAExtension` + pybind11: μεταγλωττίστε ένα αρχείο `.cu` σε ένα εγγενές `.pyd` και εισαγάγετέ το |
<!-- @os:end -->
<!-- @os:linux -->
| Προσέγγιση | Σημείο εισόδου |
|---|---|
| **Μεταγλώττιση JIT** | `torch.cuda._compile_kernel`, γράψτε έναν πυρήνα ως συμβολοσειρά Python, χωρίς βήμα κατασκευής |
| **Επέκταση C++** | `CUDAExtension` + pybind11: μεταγλωττίστε ένα αρχείο `.cu` σε ένα εγγενές `.so` και εισαγάγετέ το |
<!-- @os:end -->

Και οι δύο προσεγγίσεις εκτελούνται σε GPU της AMD. Αυτό είναι εφικτό επειδή η έκδοση ROCm του PyTorch αντιστοιχίζει ολόκληρη την επιφάνεια του API CUDA σε HIP. Αυτό σημαίνει ότι τα `torch.cuda`, `CUDAExtension`, και η σύνταξη πυρήνα CUDA λειτουργούν όλα διαφανώς σε υλικό AMD.

---

## Ιστορικό

### Τι Είναι ένας Πυρήνας GPU;

Ένας πυρήνας GPU είναι μια συνάρτηση που εκτελείται παράλληλα σε χιλιάδες νήματα GPU ταυτόχρονα. Σε αντίθεση με μια συνάρτηση CPU που εκτελείται μία φορά ανά κλήση, ένας πυρήνας εκκινείται με ένα **πλέγμα (grid)** από **μπλοκ (blocks)**, καθένα από τα οποία περιέχει πολλά **νήματα (threads)**, όλα εκτελώντας τον ίδιο κώδικα σε διαφορετικά δεδομένα.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Μοντέλο Ευρετηρίασης Νημάτων

Κατά την εκκίνηση ενός πυρήνα καθορίζετε δύο διαστάσεις:

| Μεταβλητή | Σημασία |
|---|---|
| `gridDim` | Αριθμός μπλοκ στο πλέγμα |
| `blockDim` | Αριθμός νημάτων ανά μπλοκ |

Κάθε νήμα έχει πρόσβαση σε τρεις ενσωματωμένες μεταβλητές μόνο για ανάγνωση:

| Μεταβλητή | Σημασία |
|---|---|
| `blockIdx.x` | Σε ποιο μπλοκ ανήκει αυτό το νήμα |
| `blockDim.x` | Αριθμός νημάτων σε ένα μπλοκ |
| `threadIdx.x` | Δείκτης νήματος εντός του μπλοκ του |

### Καθολικό Αναγνωριστικό Νήματος

Αυτές οι μεταβλητές συνδυάζονται για να υπολογίσουν έναν καθολικά μοναδικό δείκτη νήματος:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Σύνολο νημάτων = `gridDim.x * blockDim.x`. Κάθε νήμα επεξεργάζεται ένα στοιχείο ανεξάρτητα. Αυτό αποτελεί τη βάση του **παραλληλισμού δεδομένων (data parallelism)**. Η ίδια λειτουργία εκτελείται σε πολλά στοιχεία ταυτόχρονα, χωρίς εξάρτηση μεταξύ νημάτων.

---

### Μοντέλο Εκτέλεσης GPU: Wavefronts

Οι GPU της AMD εκτελούν νήματα σε ομάδες των **32** που ονομάζονται **wavefronts**. Όλα τα νήματα σε ένα wavefront εκτελούν την ίδια εντολή ταυτόχρονα. Αυτό επηρεάζει τις βέλτιστες επιλογές μεγέθους μπλοκ (256 νήματα = 8 wavefronts = καλή αποδοτικότητα προγραμματισμού).

### Προγραμματισμός GPU AMD: HIP + ROCm

Το **ROCm** είναι το ανοιχτού κώδικα στοίβαγμα υπολογισμών GPU της AMD (προγράμματα οδήγησης, μεταγλωττιστές, βιβλιοθήκες, χρόνος εκτέλεσης). Το **HIP** βρίσκεται από πάνω, σχεδιασμένο να είναι συντακτικά πανομοιότυπο με το CUDA. Η έκδοση ROCm του PyTorch αντιστοιχίζει διαφανώς το `torch.cuda.*` σε HIP, οπότε ο ίδιος κώδικας λειτουργεί σε GPU της AMD.

---

### PyTorch + AMD/HIP

Το PyTorch διαθέτει μια έκδοση ROCm όπου η επιφάνεια του API CUDA (`torch.cuda.*`) υποστηρίζεται διαφανώς από το HIP. Αυτό σημαίνει ότι:

- Το `torch.cuda.is_available()` λειτουργεί σε GPU της AMD με ROCm
- Το `tensor.to("cuda")` δεσμεύει μνήμη στην GPU της AMD
- Το `torch.version.hip` εκθέτει την έκδοση HIP

Το PyTorch εκθέτει επίσης το `torch.cuda._compile_kernel()`, μια συντόμευση υψηλού επιπέδου για τη μεταγλώττιση JIT μιας συμβολοσειράς ακατέργαστου πυρήνα και την επιστροφή μιας καλέσιμης συνάρτησης, χωρίς να χρειάζεται ξεχωριστό βήμα κατασκευής.

---

<!-- @device:halo_box -->
## Έλεγχος για Ενημερώσεις Λογισμικού

<!-- @require:software-update -->
<!-- @device:end -->

## Εγκατάσταση Απαιτούμενου Λογισμικού
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Προαπαιτούμενα - Windows
- Εγκαταστήστε την πιο πρόσφατη έκδοση: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Δημιουργία Εικονικού Περιβάλλοντος

<!-- @os:linux -->
<!-- @device:halo_box -->
Σε Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv με το ROCm+Pytorch ήδη εγκατεστημένα.
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
**Δώστε στον χρήστη σας πρόσβαση στις συσκευές GPU** (αποσυνδεθείτε και συνδεθείτε ξανά για να ισχύσει αυτό):

```bash
sudo usermod -aG render,video $LOGNAME
```

Σε Linux, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
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
Σε Windows, ανοίξτε ένα τερματικό στον κατάλογο της επιλογής σας και ακολουθήστε τις εντολές για να δημιουργήσετε ένα venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Συμβουλή**: Οι χρήστες Windows ενδέχεται να χρειαστεί να τροποποιήσουν την Πολιτική Εκτέλεσης PowerShell (π.χ.
> ρυθμίζοντάς την σε RemoteSigned ή Unrestricted) πριν εκτελέσουν ορισμένες εντολές Powershell.

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
> **Σημείωση:** Για αυτό το playbook, τα ROCm και PyTorch πρέπει να εγκατασταθούν στο εικονικό περιβάλλον ακόμα και στο Ryzen AI Halo, καθώς η μεταγλώττιση προσαρμοσμένων kernel απαιτεί τις πλήρεις κεφαλίδες ανάπτυξης.

Εγκαταστήστε το ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Εγκαταστήστε το PyTorch:
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
Εγκαταστήστε την αλυσίδα εργαλείων μεταγλώττισης C/C++ για Linux. Πρόκειται για εξάρτηση σε επίπεδο συστήματος και απαιτείται για τα οδηγήματα επεκτάσεων C++, καθώς το `CUDAExtension` δημιουργεί εγγενείς ενότητες `.so` από αρχεία `.cu`.

Εκτελέστε αυτό μία φορά στο μηχάνημα Linux, εκτός του δημιουργημένου εικονικού περιβάλλοντος Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Αφού ενεργοποιήσετε το εικονικό περιβάλλον `kernel-env`, εγκαταστήστε τις εξαρτήσεις μεταγλώττισης Python:
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
Βεβαιωθείτε ότι έχει εγκατασταθεί το [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ή [νεότερη έκδοση](https://visualstudio.microsoft.com/vs/community/) με το φόρτο εργασίας **Desktop development with C++**.

> **Σημείωση**: Αυτή η ρύθμιση περιβάλλοντος Visual Studio C++ απαιτείται μόνο για την προσέγγιση **C++ Extension**. Δεν απαιτείται για την προσέγγιση JIT Compilation.

Ανοίξτε ένα τερματικό PowerShell και εκτελέστε τις παρακάτω εντολές πριν από τη δημιουργία της επέκτασης C++.

**Βήμα 1: Εντοπίστε το εγκατεστημένο περιβάλλον Visual Studio C++**

**(A) Εντοπίστε το `vswhere.exe`, το οποίο εγκαθίσταται με το Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Βρείτε το `vcvars64.bat` από το Visual Studio 2022 ή νεότερη έκδοση με εργαλεία δημιουργίας C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Εκτυπώστε το περιβάλλον Visual Studio C++ που χρησιμοποιείται**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Βήμα 2: Ενεργοποιήστε το περιβάλλον δημιουργίας Visual Studio C++**

**(A) Εκτελέστε το `vcvars64.bat` και καταγράψτε το περιβάλλον που ορίζει**

Αυτό καθιστά διαθέσιμα τα `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH`, και τις διαδρομές Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Εισαγάγετε τις μεταβλητές περιβάλλοντος Visual Studio σε αυτήν τη συνεδρία PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Βήμα 3: Επαληθεύστε ότι ο μεταγλωττιστής Microsoft C++ είναι διαθέσιμος**

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
Επαληθεύστε ότι η κάρτα γραφικών AMD είναι ορατή με:
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

Δημιουργήστε την παρακάτω δομή καταλόγου φτιάχνοντας τους **2 νέους φακέλους** και κατεβάζοντας τα αντίστοιχα αρχεία:

| Κατάλογος | Αρχεία προς Λήψη | Περιγραφή |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Αρχεία JIT και επέκτασης C++ για το kernel πρόσθεσης διανυσμάτων |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Αρχεία JIT και επέκτασης C++ για το kernel πολλαπλασιασμού πινάκων |


## Οδηγήματα

### Οδήγημα 1: Πρόσθεση Διανυσμάτων

#### Προσέγγιση A: JIT Compilation

Η μεταγλώττιση JIT (Just-In-Time) σημαίνει ότι το kernel γράφεται ως ακατέργαστη συμβολοσειρά C++ μέσα στην Python και μεταγλωττίζεται κατά την εκτέλεση, χωρίς να απαιτούνται επιπλέον βήματα δημιουργίας.

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
> **Συμβουλή**: Το script δημιουργεί επίσης ένα νήμα παρασκηνίου που ελέγχει το `amd-smi` κάθε 100ms για να καταγράφει τη μέγιστη και μέση χρήση της κάρτας γραφικών κατά την εκτέλεση του kernel.
<!-- @os:end -->

> **Σημείωση**: **Γιατί το Μέγεθος Block είναι 256;** <br>
> - Το kernel χρησιμοποιεί **256 νήματα ανά block** επειδή ευθυγραμμίζεται καλά με το **μοντέλο εκτέλεσης wavefront των καρτών γραφικών AMD**.
> - Θυμηθείτε ότι το υλικό AMD εκτελεί νήματα σε ομάδες των 32 νημάτων, με αποτέλεσμα 8 wavefronts ανά block. (8 wavefronts x 32 νήματα = 1 block)


**Τι κάνει ο φόρτος εργασίας:**

Το kernel προσθέτει τεχνητά επιπλέον εργασία για να επιδείξει τη χρήση της κάρτας γραφικών:

- **100.000.000 στοιχεία** στο tensor
- **Ο εσωτερικός βρόχος εκτελείται 1.000 φορές** ανά στοιχείο ανά εκκίνηση kernel  
- **200 εκκινήσεις kernel** συνολικά

**Μαθηματικά:**  
- Κάθε στοιχείο: αυξάνεται κατά 1 × 1.000 επαναλήψεις × 200 εκκινήσεις = 200.000  
- Τελικό αποτέλεσμα: 1.0 (αρχική τιμή) + 200.000 (προσθέσεις) = 200001.0

**Γιατί ο εσωτερικός βρόχος;**  
- Χωρίς τον βρόχο `for (int i = 0; i < 1000; i++)`, οι 200 εκκινήσεις θα ολοκληρώνονταν ακαριαία και τα εργαλεία παρακολούθησης δεν θα κατέγραφαν ουσιαστική χρήση της κάρτας γραφικών. Η τεχνητή εργασία κάνει κάθε εκτέλεση kernel αρκετά μεγάλη ώστε τα εργαλεία παρακολούθησης να μπορούν να μετρήσουν την απόδοση.

<!-- @os:linux -->
**Αναμενόμενη έξοδος:**[Οι αριθμοί απόδοσης θα ποικίλλουν]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Στα Windows, το `amd-smi` δεν υποστηρίζεται. Για να παρακολουθήσετε τη χρήση της κάρτας γραφικών, μπορείτε να χρησιμοποιήσετε τη Διαχείριση Εργασιών, όπου θα πρέπει να δείτε μια σύντομη αιχμή χρήσης όταν εκτελείτε το πρόγραμμα.

**Αναμενόμενη έξοδος:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Μπράβο! Μόλις εκτελέσατε το πρώτο σας kernel GPU.**

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

Η δεύτερη προσέγγιση είναι πιο χειροκίνητη: γράψτε τον kernel και το Python binding σε ένα ενιαίο αρχείο `.cu`, μεταγλωττίστε το εγγενώς χρησιμοποιώντας το σύστημα build του PyTorch, και εισαγάγετέ το στην Python.

<!-- @os:windows -->
> **Σημείωση**: Η προσέγγιση της Επέκτασης C++ απαιτεί το περιβάλλον build της Visual Studio C++, επειδή το PyTorch μεταγλωττίζει το αρχείο πηγής `.cu` σε μια εγγενή μονάδα επέκτασης `.pyd`. Η δημιουργία αυτής της εγγενούς επέκτασης εξαρτάται από την αλυσίδα εργαλείων C++ της Microsoft (compiler, linker, και εργαλεία build) που παρέχεται από τη Visual Studio. Εκτελέστε τις εντολές ενεργοποίησης της Visual Studio από την ενότητα ρύθμισης πριν από τη δημιουργία της επέκτασης.
<!-- @os:end -->

Κατεβάστε τα παρακάτω αρχεία αν δεν το έχετε ήδη κάνει:
<!-- @os:windows -->
| Αρχείο | Ρόλος |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, όλα σε ένα αρχείο |
| [setup.py](assets/Vector_Addition/setup.py) | Σενάριο build, χρησιμοποιεί το `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Σενάριο Python που εκτελεί τα δημιουργημένα artifacts |
<!-- @os:end -->

<!-- @os:linux -->
| Αρχείο | Ρόλος |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, όλα σε ένα αρχείο |
| [setup.py](assets/Vector_Addition/setup.py) | Σενάριο build, χρησιμοποιεί το `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Σενάριο Python που εκτελεί τα δημιουργημένα artifacts |
<!-- @os:end -->

#### **Βήμα 1: Ο kernel, ο launcher, και το binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Συμβουλή**: Γιατί να χρησιμοποιήσετε το `hipDeviceSynchronize()`; <br>
> - Οι εκκινήσεις kernel της GPU είναι ασύγχρονες. Όταν η CPU εκτελεί την `add_one<<<grid_size, block_size>>>(data, n);` θα εκτελέσει αμέσως την επόμενη εντολή χωρίς να περιμένει την GPU. Το `hipDeviceSynchronize()` αναγκάζει την CPU να περιμένει μέχρι να ολοκληρωθεί ο kernel της GPU.

#### **Βήμα 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Σημείωση**: Αυτή η εντολή αναζητά το `setup.py` στον τρέχοντα κατάλογο για να δημιουργήσει το αρχείο .cu που έχουμε δημιουργήσει.


Το `CUDAExtension` είναι ένας βοηθός δημιουργίας CUDA από το `torch.utils.cpp_extension`. Με το ROCm, το PyTorch **ανακατευθύνει το `CUDAExtension` ώστε να χρησιμοποιεί το `hipcc`** αντί του `nvcc`. Το ROCm παρεμβάλλεται στη διαδρομή build και το δρομολογεί μέσω του compiler HIP, μεταφέροντας τον κώδικα CUDA σε AMD.

Αυτό παράγει τα παρακάτω αρχεία:
<!-- @os:windows -->
- `build/`:  κατάλογος με τα αρχεία `.pyd`
- `add_one_kernel.hip`:  ο κώδικας πηγής HIP που δημιουργήθηκε από το hipify-ing του αρχείου `.cu`· αυτό είναι που όντως μεταγλωττίστηκε από το `hipcc`
<!-- @os:end -->

<!-- @os:linux -->
- `build/`:  κατάλογος με τα αρχεία `.so`
- `add_one_kernel.hip`:  ο κώδικας πηγής HIP που δημιουργήθηκε από το hipify-ing του αρχείου `.cu`· αυτό είναι που όντως μεταγλωττίστηκε από το `hipcc`
<!-- @os:end -->

#### **Βήμα 3: Χρήση από την Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Εκτελέστε αυτό το σενάριο για να δείτε τον kernel σε δράση:
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

### Πλήρης οδηγός 2: Πολλαπλασιασμός Πινάκων

Ο πολλαπλασιασμός πινάκων υπολογίζει **C = A × B** όπου:
- **A** είναι M×N (γραμμές × στήλες)
- **B** είναι N×K  
- **C** είναι M×K (το αποτέλεσμα)

Κάθε στοιχείο εξόδου ορίζεται ως:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Κάθε στοιχείο του C υπολογίζεται ανεξάρτητα, καθιστώντας το ιδανικό για παραλληλισμό GPU.

#### Πώς Αντιστοιχίζεται στα Threads της GPU

Σε αντίθεση με την πρόσθεση διανυσμάτων (1D), ο πολλαπλασιασμός πινάκων παράγει μια **2D έξοδο**, οπότε χρησιμοποιούμε ένα **2D πλέγμα threads**:

| | Πρόσθεση Διανυσμάτων | Πολλαπλασιασμός Πινάκων |
|---|---|---|
| **Σχήμα εξόδου** | Πίνακας 1D | Πίνακας 2D (M×K) |
| **Αντιστοίχιση threads** | 1 thread → 1 στοιχείο | 1 thread → 1 στοιχείο εξόδου |
| **Μοτίβο εκκίνησης** | Πλέγμα 1D: `(grid_x, 1, 1)` | Πλέγμα 2D: `(grid_x, grid_y, 1)` |
| **Μέγεθος block** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

Κάθε thread υπολογίζει ένα στοιχείο του πίνακα εξόδου C. Το thread στη θέση `(row, col)` υπολογίζει το `C[row][col]` πολλαπλασιάζοντας την αντίστοιχη γραμμή του A με την αντίστοιχη στήλη του B.

**Διάταξη Μνήμης**: Η μνήμη της GPU είναι επίπεδη (1D), αλλά οι πίνακες αποθηκεύονται γραμμή προς γραμμή. Για την πρόσβαση στο `A[row][col]`, ο kernel χρησιμοποιεί το `A[row * N + col]`.


#### Προσέγγιση Α: Μεταγλώττιση JIT:

Όπως και στον Πλήρη οδηγό 1, ο kernel γράφεται ως ένα ακατέργαστο string C++ μέσα στην Python και μεταγλωττίζεται κατά την εκτέλεση μέσω του ενσωματωμένου JIT του PyTorch.


Για να χρησιμοποιήσετε το [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), βεβαιωθείτε ότι έχει κατέβει και εκτελέστε:
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

Το σενάριο επαληθεύει το αποτέλεσμα σε σχέση με το `torch.mm` με μια μικρή ανοχή. Η αριθμητική κινητής υποδιαστολής στις GPU μπορεί να παράγει μικρές αριθμητικές διαφορές σε σύγκριση με υλοποιήσεις CPU λόγω της σειράς παράλληλης αναγωγής.

<!-- @os:linux -->
**Αναμενόμενη έξοδος:**[Οι αριθμοί απόδοσης θα ποικίλλουν]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Σημείωση**: Στα Windows, το `amd-smi` δεν υποστηρίζεται. Για να παρακολουθήσετε τη χρήση της GPU, μπορείτε να χρησιμοποιήσετε τη Διαχείριση Εργασιών, όπου θα πρέπει να δείτε μια σύντομη αιχμή χρήσης όταν εκτελείτε το πρόγραμμα.

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

---
#### Προσέγγιση B: Επέκταση C++

Η δεύτερη προσέγγιση είναι πιο χειροκίνητη: γράψτε τον πυρήνα και τη σύνδεση Python σε ένα ενιαίο αρχείο `.cu`, μεταγλωττίστε το εγγενώς χρησιμοποιώντας το σύστημα δόμησης του PyTorch, και εισαγάγετέ το στην Python.

<!-- @os:windows -->
> **Σημείωση**: Η προσέγγιση της Επέκτασης C++ απαιτεί το περιβάλλον δόμησης Visual Studio C++, καθώς το PyTorch μεταγλωττίζει το αρχείο προέλευσης `.cu` σε μια εγγενή μονάδα επέκτασης `.pyd`. Η δόμηση αυτής της εγγενούς επέκτασης εξαρτάται από την αλυσίδα εργαλείων C++ της Microsoft (μεταγλωττιστής, συνδέτης και εργαλεία δόμησης) που παρέχεται από το Visual Studio. Εκτελέστε τις εντολές ενεργοποίησης του Visual Studio από την ενότητα εγκατάστασης πριν από τη δόμηση της επέκτασης.
<!-- @os:end -->

Κατεβάστε τα ακόλουθα αρχεία εάν δεν το έχετε κάνει ήδη:
<!-- @os:windows -->
| Αρχείο | Ρόλος |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Σενάριο δόμησης, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Σενάριο Python που εκτελεί τα δομημένα τεχνουργήματα |
<!-- @os:end -->
<!-- @os:linux -->
| Αρχείο | Ρόλος |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Πυρήνας + εκκινητής + σύνδεση pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Σενάριο δόμησης, χρησιμοποιεί `CUDAExtension` για τη μεταγλώττιση του `.cu` σε `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Σενάριο Python που εκτελεί τα δομημένα τεχνουργήματα |
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

Σε σύγκριση με το `add_one_launcher` στην Πρακτική Άσκηση 1, ο εκκινητής εδώ:
- Λαμβάνει δύο εισερχόμενα τανυστές αντί για έναν
- Παράγει και τις τρεις διαστάσεις (M, N, K) από τα σχήματα των τανυστών, χωρίς χειροκίνητη μεταβίβαση μεγέθους από την Python
- Δεσμεύει και επιστρέφει τον τανυστή εξόδου C, αντί να τον τροποποιεί επί τόπου
- Χρησιμοποιεί `dim3` τόσο για το πλέγμα όσο και για το μπλοκ για να εκφράσει το σχήμα εκκίνησης 2D

#### **Βήμα 2: Δόμηση**
```bash
pip install --no-build-isolation -v .
```
>**Σημείωση**: Αυτή η εντολή αναζητά το `setup.py` στον τρέχοντα κατάλογο για να δομήσει το αρχείο .cu που έχουμε δημιουργήσει.


Αυτό παράγει τα ακόλουθα αρχεία:
<!-- @os:windows -->
- `build/`:  κατάλογος με τα αρχεία `.pyd`
- `matmul_kernel.hip`:  ο πηγαίος κώδικας HIP που δημιουργήθηκε από το hipifying του αρχείου `.cu`· αυτό είναι που πραγματικά μεταγλωττίστηκε από το `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  κατάλογος με τα αρχεία `.so`
- `matmul_kernel.hip`:  ο πηγαίος κώδικας HIP που δημιουργήθηκε από το hipifying του αρχείου `.cu`· αυτό είναι που πραγματικά μεταγλωττίστηκε από το `hipcc`
<!-- @os:end -->

#### **Βήμα 3: Χρήση από την Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
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

**Καταπληκτικά! Μόλις υλοποιήσατε πολλαπλασιασμό πινάκων στη GPU.** Αυτό αποτελεί σημαντικό ορόσημο επειδή ο πολλαπλασιασμός πινάκων είναι η ραχοκοκαλιά των σύγχρονων λειτουργιών μηχανικής μάθησης όπως:
- Επίπεδα νευρωνικών δικτύων
- Μηχανισμοί προσοχής
- Ενσωματώσεις (embeddings)
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

Μάθατε να γράφετε, να μεταγλωττίζετε και να εκκινείτε πυρήνες GPU χρησιμοποιώντας τόσο μεταγλώττιση JIT όσο και επεκτάσεις C++ για βασικές παράλληλες λειτουργίες.

**Βελτιστοποιήσεις απόδοσης:**
- **Κατακερματισμός κοινόχρηστης μνήμης (Shared memory tiling)** - Αποθήκευση προσωρινών δεδομένων σε μπλοκ για μείωση της πρόσβασης στην καθολική μνήμη
- **Συνένωση μνήμης (Memory coalescing)** - Βελτιστοποίηση μοτίβων πρόσβασης μνήμης για το εύρος ζώνης

**Αλγόριθμοι πραγματικού κόσμου:**
- **2D Συνέλιξη (Convolution)** - Ένα μικρό φίλτρο (πυρήνας) ολισθαίνει κατά μήκος μιας εικόνας, υπολογίζοντας κάθε εικονοστοιχείο εξόδου από ένα σταθμισμένο άθροισμα γειτονικών εικονοστοιχείων. Αυτό εισάγει υπολογισμούς stencil και κατακερματισμό κοινόχρηστης μνήμης, όπου τα νήματα επαναχρησιμοποιούν επικαλυπτόμενες περιοχές εικόνας για να μειώσουν την πρόσβαση στην καθολική μνήμη.
- **Συνάρτηση Softmax**: Η Softmax μετατρέπει ένα διάνυσμα αριθμών σε πιθανότητες που αθροίζονται στο 1, χρησιμοποιούμενη συνήθως σε εξόδους νευρωνικών δικτύων. Η αποδοτική υλοποίησή της στη GPU εισάγει παράλληλες αναγωγές (reductions) και τεχνικές αριθμητικής σταθερότητας κατά την επεξεργασία μεγάλων διανυσμάτων.

**Παράγοντες παραγωγής:**
- **Χειρισμός σφαλμάτων** - Έλεγχος ορίων και διαχείριση συσκευής
- **Ενσωμάτωση PyTorch** - Προσαρμοσμένοι τελεστές με υποστήριξη autograd