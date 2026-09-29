<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

Scrieți un kernel GPU de la zero, compilați-l, lansați-l pe un GPU AMD și urmăriți cum crește utilizarea. Acest playbook arată cum funcționează efectiv calculul GPU: scrieți codul kernelului și executați-l în paralel pe mii de fire de execuție.

> **Notă**: Acesta este un playbook destul de complex, care poate necesita depanare și modificări suplimentare.

## Ce veți învăța

<!-- @os:windows -->
- Cum funcționează kernelurile GPU: grile, blocuri, fire de execuție și modelul de indexare care le mapează la date
- Cum stiva AMD ROCm/HIP vă permite să scrieți cod în stil CUDA care rulează pe GPU-uri AMD fără modificări
- Cum să compilați un kernel la momentul execuției folosind `torch.cuda._compile_kernel`
- Cum să construiți o extensie nativă de kernel în C++ cu `CUDAExtension` + pybind11, importabilă din Python
<!-- @os:end -->
<!-- @os:linux -->
- Cum funcționează kernelurile GPU: grile, blocuri, fire de execuție și modelul de indexare care le mapează la date
- Cum stiva AMD ROCm/HIP vă permite să scrieți cod în stil CUDA care rulează pe GPU-uri AMD fără modificări
- Cum să compilați un kernel la momentul execuției folosind `torch.cuda._compile_kernel`
- Cum să construiți o extensie nativă de kernel în C++ cu `CUDAExtension` + pybind11, importabilă din Python
- Cum să măsurați timpul de execuție al kernelului și să monitorizați utilizarea GPU în timp real cu `amd-smi`
<!-- @os:end -->

---

Acest playbook acoperă două abordări pentru dezvoltarea kernelurilor:

<!-- @os:windows -->
| Abordare | Punct de intrare |
|---|---|
| **Compilare JIT** | `torch.cuda._compile_kernel`, scrieți un kernel ca șir de caractere Python, fără pas de compilare |
| **Extensie C++** | `CUDAExtension` + pybind11: compilați un fișier `.cu` într-un `.pyd` nativ și importați-l |
<!-- @os:end -->
<!-- @os:linux -->
| Abordare | Punct de intrare |
|---|---|
| **Compilare JIT** | `torch.cuda._compile_kernel`, scrieți un kernel ca șir de caractere Python, fără pas de compilare |
| **Extensie C++** | `CUDAExtension` + pybind11: compilați un fișier `.cu` într-un `.so` nativ și importați-l |
<!-- @os:end -->

Ambele abordări rulează pe GPU-uri AMD. Acest lucru este posibil deoarece build-ul ROCm al PyTorch mapează întreaga suprafață a API-ului CUDA la HIP. Aceasta înseamnă că `torch.cuda`, `CUDAExtension` și sintaxa kernelului CUDA funcționează toate în mod transparent pe hardware-ul AMD.

---

## Context

### Ce este un kernel GPU?

Un kernel GPU este o funcție care rulează în paralel pe mii de fire de execuție GPU simultan. Spre deosebire de o funcție CPU care se execută o singură dată per apel, un kernel este lansat cu o **grilă** de **blocuri**, fiecare conținând mai multe **fire de execuție**, toate executând același cod pe date diferite.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Modelul de indexare a firelor de execuție

Când lansați un kernel, specificați două dimensiuni:

| Variabilă | Semnificație |
|---|---|
| `gridDim` | Numărul de blocuri din grilă |
| `blockDim` | Numărul de fire de execuție per bloc |

Fiecare fir de execuție are acces la trei variabile predefinite, doar pentru citire:

| Variabilă | Semnificație |
|---|---|
| `blockIdx.x` | Blocul căruia îi aparține acest fir de execuție |
| `blockDim.x` | Numărul de fire de execuție dintr-un bloc |
| `threadIdx.x` | Indexul firului de execuție în cadrul blocului său |

### ID-ul global al firului de execuție

Aceste variabile sunt combinate pentru a calcula un index global unic al firului de execuție:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Totalul firelor de execuție = `gridDim.x * blockDim.x`. Fiecare fir de execuție procesează un element în mod independent. Aceasta este baza **paralelismului de date**. Aceeași operație rulează pe mai multe elemente simultan, fără nicio dependență între fire de execuție.

---

### Modelul de execuție GPU: Wavefronts

GPU-urile AMD execută firele de execuție în grupuri de **32**, numite **wavefronts**. Toate firele de execuție dintr-un wavefront rulează aceeași instrucțiune simultan. Acest lucru influențează alegerea dimensiunii optime a blocului (256 de fire de execuție = 8 wavefronts = eficiență bună de planificare).

### Programarea GPU-urilor AMD: HIP + ROCm

**ROCm** este stiva de calcul GPU open-source a AMD (drivere, compilatoare, biblioteci, runtime). **HIP** se află deasupra, fiind conceput să fie sintactic identic cu CUDA. Build-ul ROCm al PyTorch mapează în mod transparent `torch.cuda.*` la HIP, astfel încât același cod funcționează pe GPU-uri AMD.

---

### PyTorch + AMD/HIP

PyTorch livrează un build ROCm în care suprafața API-ului CUDA (`torch.cuda.*`) este susținută în mod transparent de HIP. Aceasta înseamnă că:

- `torch.cuda.is_available()` funcționează pe GPU-uri AMD cu ROCm
- `tensor.to("cuda")` alocă pe GPU-ul AMD
- `torch.version.hip` expune versiunea HIP

PyTorch expune de asemenea `torch.cuda._compile_kernel()`, o comandă rapidă de nivel înalt pentru a compila JIT un șir de caractere brut de kernel și a obține înapoi un obiect apelabil, fără a fi nevoie de un pas de build separat.

---

<!-- @device:halo_box -->
## Verificați actualizările software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Cerințe preliminare - Windows
- Instalați cea mai recentă versiune: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Crearea unui mediu virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Pe Linux, deschideți un terminal în directorul ales de dvs. și urmați comenzile pentru a crea un venv cu ROCm+PyTorch deja instalate.
<!-- @test:id=create-venv timeout=300 -->
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
**Acordați utilizatorului dvs. acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca aceasta să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

Pe Linux, deschideți un terminal în directorul ales de dvs. și urmați comenzile pentru a crea un venv.
<!-- @test:id=create-venv timeout=300 -->
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
Pe Windows, deschideți un terminal în directorul ales de dvs. și urmați comenzile pentru a crea un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Sfat**: Este posibil ca utilizatorii Windows să trebuiască să modifice Politica de Executare PowerShell (de exemplu,
> setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi PowerShell.

<!-- @os:end -->


### Instalarea dependențelor de bază
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
> **Notă:** Pentru acest playbook, ROCm și PyTorch trebuie instalate în mediul virtual chiar și pe Ryzen AI Halo, deoarece compilarea kernelurilor personalizate necesită headerele complete de dezvoltare.

Instalați ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Instalați PyTorch:
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
### Instalarea dependențelor suplimentare

<!-- @os:linux -->
Instalați lanțul de compilare Linux C/C++. Aceasta este o dependență la nivel de sistem și este necesară pentru tutorialele de extensii C++, deoarece `CUDAExtension` compilează module native `.so` din fișiere `.cu`.

Rulați aceasta o singură dată pe mașina Linux, în afara mediului virtual Python creat:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

După activarea mediului virtual `kernel-env`, instalați dependențele de compilare Python:
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
Asigurați-vă că [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) sau [o versiune mai nouă](https://visualstudio.microsoft.com/vs/community/) este instalată cu sarcina de lucru **Desktop development with C++**.

> **Notă**: Această configurare a mediului Visual Studio C++ este necesară doar pentru abordarea de tip **C++ Extension**. Nu este necesară pentru abordarea de tip JIT Compilation.

Deschideți un terminal PowerShell și rulați următoarele comenzi înainte de a compila extensia C++.

**Pasul 1: Găsiți mediul Visual Studio C++ instalat**

**(A) Localizați `vswhere.exe`, care este instalat împreună cu Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Găsiți `vcvars64.bat` din Visual Studio 2022 sau o versiune mai nouă cu instrumente de compilare C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Afișați mediul Visual Studio C++ utilizat**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Pasul 2: Activați mediul de compilare Visual Studio C++**

**(A) Rulați `vcvars64.bat` și capturați mediul pe care îl setează**

Acest lucru face disponibile `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` și căile SDK Windows.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importați variabilele de mediu Visual Studio în această sesiune PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Pasul 3: Verificați dacă compilatorul Microsoft C++ este disponibil**

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

#### Setați variabilele de mediu
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
Verificați dacă GPU-ul AMD este vizibil cu:
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

## Descărcarea fișierelor necesare

Creați următoarea structură de directoare, creând **2 foldere noi** și descărcând fișierele corespunzătoare:

| Director | Fișiere de descărcat | Descriere |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Fișiere JIT și de extensie C++ pentru kernelul de adunare a vectorilor |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Fișiere JIT și de extensie C++ pentru kernelul de înmulțire a matricelor |


## Tutorial 1: Adunarea vectorilor

#### Abordarea A: Compilare JIT

Compilarea JIT (Just-In-Time) înseamnă că kernelul este scris ca un șir de caractere C++ brut în interiorul Python și este compilat în timpul execuției, fără a fi nevoie de pași suplimentari de compilare.

Pentru a utiliza [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), asigurați-vă că este descărcat și rulați:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Fragmente de cod cheie**
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
> **Sfat**: Scriptul lansează, de asemenea, un fir de execuție în fundal care interoghează `amd-smi` la fiecare 100ms pentru a înregistra utilizarea maximă și medie a GPU-ului pe durata rulării kernelului.
<!-- @os:end -->

> **Notă**: **De ce dimensiunea blocului este 256?** <br>
> - Kernelul folosește **256 de fire de execuție per bloc**, deoarece se aliniază bine cu **modelul de execuție wavefront al GPU-urilor AMD**.
> - Amintiți-vă că hardware-ul AMD execută firele de execuție în grupuri de 32 de fire, rezultând 8 wavefronturi per bloc. (8 wavefronturi x 32 de fire = 1 bloc)


**Ce face sarcina de lucru:**

Kernelul adaugă în mod artificial muncă suplimentară pentru a demonstra utilizarea GPU-ului:

- **100.000.000 de elemente** în tensor
- **Bucla interioară rulează de 1.000 de ori** per element, per lansare a kernelului  
- **200 de lansări** ale kernelului în total

**Calcul:**  
- Fiecare element: este incrementat cu 1 × 1.000 iterații × 200 lansări = 200.000  
- Rezultatul final: 1.0 (valoarea de pornire) + 200.000 (adunări) = 200.001,0

**De ce bucla interioară?**  
- Fără bucla `for (int i = 0; i < 1000; i++)`, cele 200 de lansări s-ar finaliza instantaneu, iar instrumentele de monitorizare nu ar putea captura o utilizare relevantă a GPU-ului. Munca artificială face ca fiecare rulare a kernelului să dureze suficient de mult pentru ca instrumentele de monitorizare să poată măsura performanța.

<!-- @os:linux -->
**Rezultat așteptat:** [Valorile de performanță vor varia]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Pe Windows, `amd-smi` nu este acceptat. Pentru a urmări utilizarea GPU-ului, puteți folosi Task Manager, unde ar trebui să vedeți un scurt vârf de utilizare atunci când rulați programul.

**Rezultat așteptat:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Bravo! Tocmai ați rulat primul vostru kernel GPU.**

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
#### Abordarea B: extensie C++

A doua abordare este mai manuală: se scrie kernelul și binding-ul Python într-un singur fișier `.cu`, se compilează nativ folosind sistemul de build al PyTorch și se importă în Python.

<!-- @os:windows -->
> **Notă**: Abordarea cu extensie C++ necesită mediul de build Visual Studio C++, deoarece PyTorch compilează fișierul sursă `.cu` într-un modul de extensie nativ `.pyd`. Construirea acelei extensii native depinde de lanțul de instrumente C++ Microsoft (compilator, linker și instrumente de build) oferit de Visual Studio. Rulați comenzile de activare Visual Studio din secțiunea de configurare înainte de a construi extensia.
<!-- @os:end -->

Descărcați următoarele fișiere dacă nu ați făcut-o deja:
<!-- @os:windows -->
| Fișier | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + binding pybind11, toate într-un singur fișier |
| [setup.py](assets/Vector_Addition/setup.py) | Script de build, folosește `CUDAExtension` pentru a compila `.cu` într-un `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python care rulează artefactele construite |
<!-- @os:end -->

<!-- @os:linux -->
| Fișier | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + binding pybind11, toate într-un singur fișier |
| [setup.py](assets/Vector_Addition/setup.py) | Script de build, folosește `CUDAExtension` pentru a compila `.cu` într-un `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python care rulează artefactele construite |
<!-- @os:end -->

#### **Pasul 1: kernelul, launcher-ul și binding-ul** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Sugestie**: De ce se folosește `hipDeviceSynchronize()`? <br>
> - Lansările de kernel GPU sunt asincrone. Când CPU-ul rulează `add_one<<<grid_size, block_size>>>(data, n);`, acesta ar executa imediat următoarea instrucțiune fără a aștepta GPU-ul. `hipDeviceSynchronize()` forțează CPU-ul să aștepte până când kernelul GPU se finalizează.

#### **Pasul 2: build**
```bash
pip install --no-build-isolation -v .
```
>**Notă**: Această comandă caută fișierul `setup.py` în directorul curent pentru a construi fișierul .cu pe care l-am creat.


`CUDAExtension` este un helper de build CUDA din `torch.utils.cpp_extension`. Cu ROCm, PyTorch **remapează `CUDAExtension` pentru a folosi `hipcc`** în locul `nvcc`. ROCm interceptează calea de build și o direcționează prin compilatorul HIP, portând codul CUDA pe AMD.

Aceasta produce următoarele fișiere:
<!-- @os:windows -->
- `build/`: director cu fișierele `.pyd`
- `add_one_kernel.hip`: sursa HIP generată prin hipificarea fișierului `.cu`; aceasta este ceea ce a compilat de fapt `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: director cu fișierele `.so`
- `add_one_kernel.hip`: sursa HIP generată prin hipificarea fișierului `.cu`; aceasta este ceea ce a compilat de fapt `hipcc`
<!-- @os:end -->

#### **Pasul 3: utilizare din Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Executați acest script pentru a vedea kernelul în acțiune:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Rezultat așteptat:**
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

## Parcurgere 2: înmulțirea matricelor

Înmulțirea matricelor calculează **C = A × B**, unde:
- **A** este M×N (rânduri × coloane)
- **B** este N×K  
- **C** este M×K (rezultatul)

Fiecare element de ieșire este definit ca:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Fiecare element al C este calculat independent, ceea ce face ca acest lucru să fie perfect pentru paralelismul GPU.

#### Cum se mapează la firele de execuție GPU

Spre deosebire de adunarea vectorilor (1D), înmulțirea matricelor produce o **ieșire 2D**, așa că folosim o **grilă 2D de fire de execuție**:

| | Adunarea vectorilor | Înmulțirea matricelor |
|---|---|---|
| **Forma ieșirii** | tablou 1D | matrice 2D (M×K) |
| **Maparea firelor** | 1 fir → 1 element | 1 fir → 1 element de ieșire |
| **Model de lansare** | grilă 1D: `(grid_x, 1, 1)` | grilă 2D: `(grid_x, grid_y, 1)` |
| **Dimensiunea blocului** | `(256, 1, 1)` | `(16, 16, 1)` = 256 fire |

Fiecare fir de execuție calculează un element al matricei de ieșire C. Firul aflat la poziția `(row, col)` calculează `C[row][col]` prin înmulțirea rândului corespunzător din A cu coloana corespunzătoare din B.

**Structura memoriei**: memoria GPU este plată (1D), dar matricele sunt stocate rând cu rând. Pentru a accesa `A[row][col]`, kernelul folosește `A[row * N + col]`.


#### Abordarea A: compilare JIT:

Ca și la Parcurgerea 1, kernelul este scris ca un șir C++ brut în interiorul Python și compilat la momentul execuției prin JIT-ul integrat al PyTorch.


Pentru a folosi [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), asigurați-vă că este descărcat și rulați:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Fragmente de cod cheie**
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

Scriptul verifică rezultatul comparativ cu `torch.mm` cu o toleranță mică. Aritmetica în virgulă mobilă pe GPU-uri poate produce diferențe numerice mici comparativ cu implementările pe CPU, din cauza ordinii de reducere paralelă.

<!-- @os:linux -->
**Rezultat așteptat:**[Numerele de performanță vor varia]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Pe Windows, `amd-smi` nu este suportat. Pentru a urmări utilizarea GPU, puteți folosi Task Manager, unde ar trebui să vedeți un scurt vârf de utilizare atunci când rulați programul.

**Rezultat așteptat:**
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
#### Abordarea B: Extensie C++

A doua abordare este mai manuală: se scrie kernel-ul și legătura Python într-un singur fișier `.cu`, se compilează nativ folosind sistemul de build al PyTorch, și se importă în Python.

<!-- @os:windows -->
> **Notă**: Abordarea prin Extensie C++ necesită mediul de build Visual Studio C++ deoarece PyTorch compilează fișierul sursă `.cu` într-un modul de extensie nativ `.pyd`. Construirea acelei extensii native depinde de toolchain-ul C++ Microsoft (compilator, linker și instrumente de build) furnizat de Visual Studio. Rulați comenzile de activare Visual Studio din secțiunea de configurare înainte de a construi extensia.
<!-- @os:end -->

Descărcați următoarele fișiere dacă nu ați făcut-o deja:
<!-- @os:windows -->
| Fișier | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + legătură pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de build, folosește `CUDAExtension` pentru a compila `.cu`-ul într-un `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python care rulează artefactele construite |
<!-- @os:end -->
<!-- @os:linux -->
| Fișier | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + legătură pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de build, folosește `CUDAExtension` pentru a compila `.cu`-ul într-un `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python care rulează artefactele construite |
<!-- @os:end -->

#### **Pasul 1: Kernel-ul, launcher-ul și legătura** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

În comparație cu `add_one_launcher` din Prezentarea generală 1, launcher-ul de aici:
- Preia doi tensori de intrare în loc de unul
- Derivă toate cele trei dimensiuni (M, N, K) din formele tensorilor, fără transmiterea manuală a dimensiunilor din Python
- Alocă și returnează tensorul de ieșire C, în loc să modifice în loc
- Folosește `dim3` atât pentru grid, cât și pentru block, pentru a exprima forma de lansare 2D

#### **Pasul 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Notă**: Această comandă caută `setup.py` în directorul curent pentru a construi fișierul .cu pe care l-am creat.


Aceasta produce următoarele fișiere:
<!-- @os:windows -->
- `build/`: director cu fișierele `.pyd`
- `matmul_kernel.hip`: sursa HIP generată prin hipificarea fișierului `.cu`; aceasta este ceea ce a compilat de fapt `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: director cu fișierele `.so`
- `matmul_kernel.hip`: sursa HIP generată prin hipificarea fișierului `.cu`; aceasta este ceea ce a compilat de fapt `hipcc`
<!-- @os:end -->

#### **Pasul 3: Utilizare din Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Executați acest script pentru a vedea kernel-ul în acțiune:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Rezultat așteptat:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Excelent! Tocmai ați implementat înmulțirea matricelor pe GPU.** Aceasta este o etapă majoră deoarece înmulțirea matricelor este coloana vertebrală a operațiilor moderne de machine learning precum:
- Straturi de rețele neuronale
- Mecanisme de atenție
- Embeddings
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

## Pașii următori

Ați învățat să scrieți, compilați și lansați kernel-uri GPU folosind atât compilarea JIT, cât și extensii C++ pentru operații paralele de bază.

**Optimizări de performanță:**
- **Shared memory tiling** - Stochează în cache blocuri de date pentru a reduce accesul la memoria globală
- **Memory coalescing** - Optimizează tiparele de acces la memorie pentru lățimea de bandă

**Algoritmi din lumea reală:**
- **Convoluție 2D** - Un filtru mic (kernel) glisează pe o imagine, calculând fiecare pixel de ieșire dintr-o sumă ponderată a pixelilor vecini. Aceasta introduce calcule de tip stencil și shared memory tiling, unde thread-urile reutilizează regiuni de imagine suprapuse pentru a reduce accesul la memoria globală.
- **Funcția Softmax**: Softmax convertește un vector de numere în probabilități care însumează 1, folosit în mod obișnuit în ieșirile rețelelor neuronale. Implementarea sa eficientă pe GPU introduce reduceri paralele și tehnici de stabilitate numerică în timpul procesării vectorilor mari.

**Considerații de producție:**
- **Gestionarea erorilor** - Verificarea limitelor și gestionarea dispozitivului
- **Integrare PyTorch** - Operatori personalizați cu suport pentru autograd