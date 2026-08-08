<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Napišite GPU kernel od nule, kompajlirajte ga, pokrenite na AMD GPU-u i posmatrajte kako iskorišćenost naglo raste. Ovaj priručnik pokazuje kako GPU računanje zapravo funkcioniše: napišite kôd kernela i izvršite ga paralelno kroz hiljade niti (threads).

> **Napomena**: Ovo je prilično kompleksan priručnik, koji može zahtevati dodatno otklanjanje grešaka i izmene.

## Šta ćete naučiti

<!-- @os:windows -->
- Kako funkcionišu GPU kerneli: mreže (grids), blokovi, niti i model indeksiranja koji ih mapira na podatke
- Kako AMD ROCm/HIP stek omogućava da pišete kôd u CUDA stilu koji se izvršava na AMD GPU-ovima bez izmena
- Kako da kompajlirate kernel u vreme izvršavanja koristeći `torch.cuda._compile_kernel`
- Kako da izgradite native C++ kernel ekstenziju koristeći `CUDAExtension` + pybind11, uvozivu iz Python-a
<!-- @os:end -->
<!-- @os:linux -->
- Kako funkcionišu GPU kerneli: mreže (grids), blokovi, niti i model indeksiranja koji ih mapira na podatke
- Kako AMD ROCm/HIP stek omogućava da pišete kôd u CUDA stilu koji se izvršava na AMD GPU-ovima bez izmena
- Kako da kompajlirate kernel u vreme izvršavanja koristeći `torch.cuda._compile_kernel`
- Kako da izgradite native C++ kernel ekstenziju koristeći `CUDAExtension` + pybind11, uvozivu iz Python-a
- Kako da izmerite vreme izvršavanja kernela i pratite iskorišćenost GPU-a uživo pomoću `amd-smi`
<!-- @os:end -->

---

Ovaj priručnik obuhvata dva pristupa razvoju kernela:

<!-- @os:windows -->
| Pristup | Ulazna tačka |
|---|---|
| **JIT kompilacija** | `torch.cuda._compile_kernel`, pišete kernel kao Python string, bez koraka izgradnje |
| **C++ ekstenzija** | `CUDAExtension` + pybind11: kompajlirajte `.cu` fajl u native `.pyd` i uvezite ga |
<!-- @os:end -->
<!-- @os:linux -->
| Pristup | Ulazna tačka |
|---|---|
| **JIT kompilacija** | `torch.cuda._compile_kernel`, pišete kernel kao Python string, bez koraka izgradnje |
| **C++ ekstenzija** | `CUDAExtension` + pybind11: kompajlirajte `.cu` fajl u native `.so` i uvezite ga |
<!-- @os:end -->

Oba pristupa rade na AMD GPU-ovima. To je moguće jer PyTorch-ov ROCm build mapira celokupan CUDA API na HIP. To znači da `torch.cuda`, `CUDAExtension` i CUDA sintaksa kernela transparentno rade na AMD hardveru.

---

## Pozadina

### Šta je GPU kernel?

GPU kernel je funkcija koja se izvršava paralelno kroz hiljade GPU niti istovremeno. Za razliku od CPU funkcije koja se izvršava jednom po pozivu, kernel se pokreće sa **mrežom** (grid) **blokova**, od kojih svaki sadrži mnogo **niti** (threads), a sve izvršavaju isti kôd nad različitim podacima.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indeksiranja niti

Prilikom pokretanja kernela navode se dve dimenzije:

| Promenljiva | Značenje |
|---|---|
| `gridDim` | Broj blokova u mreži |
| `blockDim` | Broj niti po bloku |

Svaka nit ima pristup trima ugrađenim promenljivama samo za čitanje:

| Promenljiva | Značenje |
|---|---|
| `blockIdx.x` | Kom bloku ova nit pripada |
| `blockDim.x` | Broj niti u jednom bloku |
| `threadIdx.x` | Indeks niti unutar svog bloka |

### Globalni identifikator niti

Ove promenljive se kombinuju da bi se izračunao globalno jedinstven indeks niti:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Ukupan broj niti = `gridDim.x * blockDim.x`. Svaka nit obrađuje jedan element nezavisno. Ovo je osnova **paralelizma podataka** (data parallelism). Ista operacija se izvršava nad mnogo elemenata odjednom, bez zavisnosti između niti.

---

### Model izvršavanja GPU-a: Wavefront-ovi

AMD GPU-ovi izvršavaju niti u grupama od **32**, koje se nazivaju **wavefront-ovi**. Sve niti u wavefront-u izvršavaju istu instrukciju istovremeno. Ovo utiče na izbor optimalne veličine bloka (256 niti = 8 wavefront-ova = dobra efikasnost raspoređivanja).

### AMD GPU programiranje: HIP + ROCm

**ROCm** je AMD-ov open-source GPU compute stek (drajveri, kompajleri, biblioteke, runtime). **HIP** se nalazi na vrhu, i dizajniran je da bude sintaksno identičan CUDA-i. PyTorch-ov ROCm build transparentno mapira `torch.cuda.*` na HIP, tako da isti kôd radi na AMD GPU-ovima.

---

### PyTorch + AMD/HIP

PyTorch isporučuje ROCm build u kojem je CUDA API (`torch.cuda.*`) transparentno podržan pomoću HIP-a. To znači:

- `torch.cuda.is_available()` radi na AMD GPU-ovima sa ROCm
- `tensor.to("cuda")` alocira na AMD GPU-u
- `torch.version.hip` prikazuje verziju HIP-a

PyTorch takođe izlaže `torch.cuda._compile_kernel()`, prečicu visokog nivoa za JIT kompilaciju sirovog stringa kernela i dobijanje pozivne funkcije (callable), bez potrebe za posebnim korakom izgradnje.

---

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija potrebnog softvera
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Preduslovi - Windows
- Instalirajte najnoviju verziju: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Kreiranje virtuelnog okruženja

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linux-u, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv sa već instaliranim ROCm+Pytorch.
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
**Dajte svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linux-u, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv.
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
Na Windows-u, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Savet**: Korisnicima Windows-a možda će biti potrebno da izmene svoju PowerShell Execution Policy (npr.
> da je podese na RemoteSigned ili Unrestricted) pre pokretanja nekih PowerShell komandi.

<!-- @os:end -->
### Instaliranje osnovnih zavisnosti

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
> **Napomena:** Za ovaj vodič, ROCm i PyTorch moraju biti instalirani u virtuelno okruženje čak i na Ryzen AI Halo, pošto kompajliranje prilagođenih kernela zahteva kompletna razvojna zaglavlja (development headers).

Instalirajte ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Instalirajte PyTorch:
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

### Instaliranje dodatnih zavisnosti

<!-- @os:linux -->
Instalirajte Linux C/C++ build toolchain. Ovo je zavisnost na nivou sistema i neophodna je za vodiče o C++ ekstenzijama jer `CUDAExtension` gradi native `.so` module iz `.cu` fajlova.

Ovo pokrenite jednom na Linux mašini, van kreiranog Python virtuelnog okruženja:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Nakon aktiviranja virtuelnog okruženja `kernel-env`, instalirajte Python build zavisnosti:
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
Obezbedite da je instaliran [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ili [noviji](https://visualstudio.microsoft.com/vs/community/), sa radnim opterećenjem (workload) **Desktop development with C++**.

> **Napomena**: Ovo podešavanje Visual Studio C++ okruženja je neophodno samo za pristup **C++ ekstenzijom**. Nije potrebno za pristup JIT kompajliranjem.

Otvorite PowerShell terminal i pokrenite sledeće komande pre nego što izgradite C++ ekstenziju.

**Korak 1: Pronađite instalirano Visual Studio C++ okruženje**

**(A) Pronađite `vswhere.exe`, koji se instalira zajedno sa Visual Studio Installer-om**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Pronađite `vcvars64.bat` iz Visual Studio 2022 ili novijeg, sa C++ build alatima**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Ispišite Visual Studio C++ okruženje koje se koristi**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Korak 2: Aktivirajte Visual Studio C++ build okruženje**

**(A) Pokrenite `vcvars64.bat` i preuzmite okruženje koje ono podešava**

Ovo omogućava dostupnost `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` i putanja Windows SDK-a.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Uvezite Visual Studio promenljive okruženja u ovu PowerShell sesiju**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Korak 3: Proverite da li je Microsoft C++ kompajler dostupan**

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

#### Podešavanje promenljivih okruženja
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
Proverite da li je AMD GPU vidljiv pomoću:
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

## Preuzimanje potrebnih fajlova

Kreirajte sledeću strukturu direktorijuma tako što ćete napraviti **2 nova foldera** i preuzeti odgovarajuće fajlove:

| Direktorijum | Fajlovi za preuzimanje | Opis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT i C++ ekstenzija fajlovi za kernel sabiranja vektora |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT i C++ ekstenzija fajlovi za kernel množenja matrica |


## Vodiči kroz vežbe

### Vežba 1: Sabiranje vektora

#### Pristup A: JIT kompajliranje

JIT (Just-In-Time) kompajliranje znači da je kernel napisan kao sirovi C++ string unutar Python-a i kompajlira se u vreme izvršavanja, bez potrebe za dodatnim koracima izgradnje.

Da biste koristili [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), proverite da li je preuzet i pokrenite:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Ključni isečci koda**
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
> **Savet**: Skripta takođe pokreće pozadinsku nit koja ispituje `amd-smi` na svakih 100ms kako bi beležila maksimalno i prosečno iskorišćenje GPU-a tokom izvršavanja kernela.
<!-- @os:end -->

> **Napomena**: **Zašto je veličina bloka 256?** <br>
> - Kernel koristi **256 niti po bloku** jer se to dobro poklapa sa **modelom izvršavanja talasnih frontova (wavefront) AMD GPU-a**.
> - Podsetimo se da AMD hardver izvršava niti u grupama od 32 niti, što rezultira sa 8 wavefront-ova po bloku. (8 wavefront-ova x 32 niti = 1 blok)


**Šta radi ovo radno opterećenje:**

Kernel veštački dodaje dodatan posao kako bi demonstrirao iskorišćenje GPU-a:

- **100.000.000 elemenata** u tenzoru
- **Unutrašnja petlja se izvršava 1.000 puta** po elementu, po pokretanju kernela  
- Ukupno **200 pokretanja kernela**

**Matematika:**  
- Svaki element: povećava se za 1 × 1.000 iteracija × 200 pokretanja = 200.000  
- Konačan rezultat: 1.0 (početna vrednost) + 200.000 (sabiranja) = 200001.0

**Zašto unutrašnja petlja?**  
- Bez petlje `for (int i = 0; i < 1000; i++)`, 200 pokretanja bi se završilo trenutno, a alati za monitoring ne bi uspeli da zabeleže smisleno iskorišćenje GPU-a. Veštački posao čini da svako izvršavanje kernela traje dovoljno dugo da alati za monitoring mogu da izmere performanse.

<!-- @os:linux -->
**Očekivani izlaz:**[Brojevi performansi će varirati]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Na Windows-u, `amd-smi` nije podržan. Za praćenje iskorišćenja GPU-a, možete koristiti Task Manager, gde biste trebalo da vidite kratak skok iskorišćenja kada pokrenete program.

**Očekivani izlaz:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Odličan posao! Upravo ste pokrenuli svoj prvi GPU kernel.**

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
#### Pristup B: C++ ekstenzija

Drugi pristup je ručniji: napišite kernel i Python vezivanje u jednu `.cu` datoteku, kompajlirajte je nativno koristeći PyTorch-ov sistem za izgradnju, i uvezite je u Python.

<!-- @os:windows -->
> **Napomena**: Pristup C++ ekstenzije zahteva Visual Studio C++ okruženje za izgradnju jer PyTorch kompajlira `.cu` izvorni fajl u nativni `.pyd` ekstenzioni modul. Izgradnja te nativne ekstenzije zavisi od Microsoft C++ toolchain-a (kompajler, linker i alati za izgradnju) koje obezbeđuje Visual Studio. Pokrenite komande za aktivaciju Visual Studio-a iz sekcije za podešavanje pre izgradnje ekstenzije.
<!-- @os:end -->

Preuzmite sledeće datoteke ako to već niste učinili:
<!-- @os:windows -->
| Datoteka | Uloga |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 vezivanje, sve u jednoj datoteci |
| [setup.py](assets/Vector_Addition/setup.py) | Skripta za izgradnju, koristi `CUDAExtension` za kompajliranje `.cu` u `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skripta koja pokreće izgrađene artefakte |
<!-- @os:end -->

<!-- @os:linux -->
| Datoteka | Uloga |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 vezivanje, sve u jednoj datoteci |
| [setup.py](assets/Vector_Addition/setup.py) | Skripta za izgradnju, koristi `CUDAExtension` za kompajliranje `.cu` u `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skripta koja pokreće izgrađene artefakte |
<!-- @os:end -->

#### **Korak 1: Kernel, launcher i vezivanje** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Savet**: Zašto koristiti `hipDeviceSynchronize()`? <br>
> - Pokretanja GPU kernela su asinhrona. Kada CPU izvrši `add_one<<<grid_size, block_size>>>(data, n);`, on bi odmah izvršio sledeću instrukciju bez čekanja na GPU. `hipDeviceSynchronize()` primorava CPU da čeka dok se GPU kernel ne završi.

#### **Korak 2: Izgradnja**
```bash
pip install --no-build-isolation -v .
```
>**Napomena**: Ova komanda traži `setup.py` u trenutnom direktorijumu kako bi izgradila `.cu` datoteku koju smo napravili.


`CUDAExtension` je pomoćni alat za CUDA izgradnju iz `torch.utils.cpp_extension`. Sa ROCm-om, PyTorch **preusmerava `CUDAExtension` da koristi `hipcc`** umesto `nvcc`. ROCm presreće put izgradnje i usmerava ga kroz HIP kompajler, portujući CUDA kod na AMD.

Ovo proizvodi sledeće datoteke:
<!-- @os:windows -->
- `build/`: direktorijum sa `.pyd` datotekama
- `add_one_kernel.hip`: HIP izvorni kod generisan hipifikacijom `.cu` datoteke; ovo je ono što je `hipcc` zapravo kompajlirao
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: direktorijum sa `.so` datotekama
- `add_one_kernel.hip`: HIP izvorni kod generisan hipifikacijom `.cu` datoteke; ovo je ono što je `hipcc` zapravo kompajlirao
<!-- @os:end -->

#### **Korak 3: Korišćenje iz Python-a** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Izvršite ovu skriptu da vidite kernel u akciji:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Očekivani izlaz:**
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

### Vodič 2: Množenje matrica

Množenje matrica izračunava **C = A × B** gde su:
- **A** M×N (redovi × kolone)
- **B** N×K  
- **C** M×K (rezultat)

Svaki izlazni element je definisan kao:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Svaki element matrice C se izračunava nezavisno, što ovo čini idealnim za GPU paralelizam.

#### Kako se to preslikava na GPU niti

Za razliku od sabiranja vektora (1D), množenje matrica proizvodi **2D izlaz**, pa koristimo **2D mrežu niti**:

| | Sabiranje vektora | Množenje matrica |
|---|---|---|
| **Oblik izlaza** | 1D niz | 2D matrica (M×K) |
| **Mapiranje niti** | 1 nit → 1 element | 1 nit → 1 izlazni element |
| **Šablon pokretanja** | 1D mreža: `(grid_x, 1, 1)` | 2D mreža: `(grid_x, grid_y, 1)` |
| **Veličina bloka** | `(256, 1, 1)` | `(16, 16, 1)` = 256 niti |

Svaka nit izračunava jedan element izlazne matrice C. Nit na poziciji `(row, col)` izračunava `C[row][col]` množenjem odgovarajućeg reda matrice A sa odgovarajućom kolonom matrice B.

**Raspored memorije**: GPU memorija je ravna (1D), ali matrice se čuvaju red po red. Za pristup `A[row][col]`, kernel koristi `A[row * N + col]`.


#### Pristup A: JIT kompilacija:

Kao i u Vodiču 1, kernel je napisan kao sirovi C++ string unutar Python-a i kompajlira se tokom izvršavanja putem PyTorch-ove ugrađene JIT kompilacije.


Da biste koristili [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), proverite da li je preuzet i pokrenite:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Ključni isečci koda**
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

Skripta proverava rezultat u odnosu na `torch.mm` sa malom tolerancijom. Aritmetika sa pokretnim zarezom na GPU-ima može proizvesti male numeričke razlike u poređenju sa implementacijama na CPU-u zbog redosleda paralelne redukcije.

<!-- @os:linux -->
**Očekivani izlaz:** [Brojevi performansi će varirati]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Na Windows-u, `amd-smi` nije podržan. Da biste pratili iskorišćenost GPU-a, možete koristiti Task Manager, gde biste trebalo da vidite kratak skok iskorišćenosti kada pokrenete program.

**Očekivani izlaz:**
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
#### Pristup B: C++ ekstenzija

Drugi pristup je manuelniji: napišite kernel i Python binding u jednu `.cu` datoteku, kompajlirajte je nativno koristeći PyTorch-ov build sistem i uvezite je u Python.

<!-- @os:windows -->
> **Napomena**: Pristup C++ ekstenzije zahteva Visual Studio C++ build okruženje jer PyTorch kompajlira `.cu` izvorni fajl u nativni `.pyd` extension modul. Izgradnja te nativne ekstenzije zavisi od Microsoft C++ toolchain-a (kompajler, linker i build alati) koji obezbeđuje Visual Studio. Pokrenite komande za aktivaciju Visual Studio-a iz sekcije za podešavanje pre nego što izgradite ekstenziju.
<!-- @os:end -->

Preuzmite sledeće fajlove ukoliko to već niste uradili:
<!-- @os:windows -->
| Fajl | Uloga |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build skripta, koristi `CUDAExtension` za kompajliranje `.cu` fajla u `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skripta koja pokreće izgrađene artefakte |
<!-- @os:end -->
<!-- @os:linux -->
| Fajl | Uloga |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build skripta, koristi `CUDAExtension` za kompajliranje `.cu` fajla u `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skripta koja pokreće izgrađene artefakte |
<!-- @os:end -->

#### **Korak 1: Kernel, launcher i binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

U poređenju sa `add_one_launcher` iz Vodiča 1, launcher ovde:
- Uzima dva ulazna tenzora umesto jednog
- Izvodi sve tri dimenzije (M, N, K) iz oblika tenzora, bez ručnog prosleđivanja veličina iz Python-a
- Alocira i vraća izlazni tenzor C, umesto da vrši mutaciju in-place
- Koristi `dim3` i za grid i za block da bi izrazio 2D oblik pokretanja

#### **Korak 2: Izgradnja**
```bash
pip install --no-build-isolation -v .
```
>**Napomena**: Ova komanda traži `setup.py` u trenutnom direktorijumu da bi izgradila `.cu` fajl koji smo napravili.


Ovo proizvodi sledeće fajlove:
<!-- @os:windows -->
- `build/`: direktorijum sa `.pyd` fajlovima
- `matmul_kernel.hip`: HIP izvorni kod generisan hipifikovanjem `.cu` fajla; ovo je ono što je `hipcc` zapravo kompajlirao
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: direktorijum sa `.so` fajlovima
- `matmul_kernel.hip`: HIP izvorni kod generisan hipifikovanjem `.cu` fajla; ovo je ono što je `hipcc` zapravo kompajlirao
<!-- @os:end -->

#### **Korak 3: Korišćenje iz Python-a** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Izvršite ovu skriptu da vidite kernel u akciji:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Očekivani izlaz:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Odlično! Upravo ste implementirali množenje matrica na GPU-u.** Ovo je značajna prekretnica jer je množenje matrica okosnica modernih operacija mašinskog učenja poput:
- Slojeva neuronskih mreža
- Mehanizama pažnje (attention)
- Ugrađivanja (embeddings)
- Transformera

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

## Sledeći koraci

Naučili ste da pišete, kompajlirate i pokrećete GPU kernele koristeći i JIT kompilaciju i C++ ekstenzije za osnovne paralelne operacije.

**Optimizacije performansi:**
- **Tajling deljene memorije (Shared memory tiling)** - Keširanje blokova podataka radi smanjenja pristupa globalnoj memoriji
- **Koaliscirano pristupanje memoriji (Memory coalescing)** - Optimizacija obrazaca pristupa memoriji radi propusnog opsega

**Algoritmi iz stvarnog sveta:**
- **2D konvolucija** - Mali filter (kernel) klizi preko slike, izračunavajući svaki izlazni piksel na osnovu ponderisanog zbira susednih piksela. Ovo uvodi stencil izračunavanja i tajling deljene memorije, gde niti ponovo koriste preklapajuće regione slike kako bi se smanjio pristup globalnoj memoriji.
- **Softmax funkcija**: Softmax konvertuje vektor brojeva u verovatnoće koje daju zbir 1, što se često koristi u izlazima neuronskih mreža. Efikasna implementacija na GPU-u uvodi paralelne redukcije i tehnike numeričke stabilnosti prilikom obrade velikih vektora.

**Razmatranja za produkciju:**
- **Rukovanje greškama** - Provera granica i upravljanje uređajem
- **PyTorch integracija** - Prilagođeni operatori sa podrškom za autograd