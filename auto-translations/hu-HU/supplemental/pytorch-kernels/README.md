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

Írjon egy GPU kernelt a semmiből, fordítsa le, indítsa el egy AMD GPU-n, és figyelje meg, ahogy a kihasználtság megugrik. Ez a playbook bemutatja, hogyan működik valójában a GPU-alapú számítás: megírja a kernelkódot, majd párhuzamosan végrehajtja azt több ezer szálon.

> **Megjegyzés**: Ez egy meglehetősen összetett playbook, amely némi extra hibakeresést és módosítást igényelhet.

## Amit tanulni fog

<!-- @os:windows -->
- Hogyan működnek a GPU kernelek: rácsok (grids), blokkok, szálak, és az indexelési modell, amely ezeket az adatokhoz rendeli
- Hogyan teszi lehetővé az AMD ROCm/HIP stack, hogy CUDA-stílusú kódot írjon, amely módosítás nélkül fut AMD GPU-kon
- Hogyan fordítson le egy kernelt futásidőben a `torch.cuda._compile_kernel` segítségével
- Hogyan építsen natív C++ kernel kiterjesztést a `CUDAExtension` + pybind11 segítségével, amely Pythonból importálható
<!-- @os:end -->
<!-- @os:linux -->
- Hogyan működnek a GPU kernelek: rácsok (grids), blokkok, szálak, és az indexelési modell, amely ezeket az adatokhoz rendeli
- Hogyan teszi lehetővé az AMD ROCm/HIP stack, hogy CUDA-stílusú kódot írjon, amely módosítás nélkül fut AMD GPU-kon
- Hogyan fordítson le egy kernelt futásidőben a `torch.cuda._compile_kernel` segítségével
- Hogyan építsen natív C++ kernel kiterjesztést a `CUDAExtension` + pybind11 segítségével, amely Pythonból importálható
- Hogyan mérje a kernel végrehajtási idejét, és hogyan figyelje élőben a GPU kihasználtságát az `amd-smi` segítségével
<!-- @os:end -->

---

Ez a playbook a kernelfejlesztés két megközelítését mutatja be:

<!-- @os:windows -->
| Megközelítés | Belépési pont |
|---|---|
| **JIT fordítás** | `torch.cuda._compile_kernel`, a kernel megírása Python stringként, build lépés nélkül |
| **C++ kiterjesztés** | `CUDAExtension` + pybind11: egy `.cu` fájl lefordítása natív `.pyd` fájllá, majd importálás |
<!-- @os:end -->
<!-- @os:linux -->
| Megközelítés | Belépési pont |
|---|---|
| **JIT fordítás** | `torch.cuda._compile_kernel`, a kernel megírása Python stringként, build lépés nélkül |
| **C++ kiterjesztés** | `CUDAExtension` + pybind11: egy `.cu` fájl lefordítása natív `.so` fájllá, majd importálás |
<!-- @os:end -->

Mindkét megközelítés fut AMD GPU-kon. Ez azért lehetséges, mert a PyTorch ROCm build-je a teljes CUDA API felületet HIP-re képezi le. Ez azt jelenti, hogy a `torch.cuda`, a `CUDAExtension` és a CUDA kernel szintaxis mind átlátszó módon működik AMD hardveren.

---

## Háttér

### Mi az a GPU Kernel?

A GPU kernel egy olyan függvény, amely egyidejűleg több ezer GPU szálon fut párhuzamosan. Egy CPU-függvénnyel ellentétben, amely híváskor egyszer fut le, a kernel egy **blokkokból** álló **rács** (grid) segítségével kerül elindításra, ahol minden blokk sok **szálat** (thread) tartalmaz, és mindegyik ugyanazt a kódot hajtja végre eltérő adatokon.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Szálindexelési modell

Egy kernel indításakor két dimenziót kell megadnia:

| Változó | Jelentés |
|---|---|
| `gridDim` | A rácsban lévő blokkok száma |
| `blockDim` | Blokkonkénti szálak száma |

Minden szál három beépített, csak olvasható változóhoz fér hozzá:

| Változó | Jelentés |
|---|---|
| `blockIdx.x` | Melyik blokkhoz tartozik az adott szál |
| `blockDim.x` | Egy blokkban lévő szálak száma |
| `threadIdx.x` | A szál indexe a blokkján belül |

### Globális szálazonosító

Ezeket a változókat kombinálva kiszámítható egy globálisan egyedi szálindex:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Az összes szál száma = `gridDim.x * blockDim.x`. Minden szál egy elemet dolgoz fel önállóan. Ez a **data parallelism** (adatpárhuzamosság) alapja. Ugyanaz a művelet fut le sok elemen egyszerre, szálak közötti függőség nélkül.

---

### GPU végrehajtási modell: Wavefrontok

Az AMD GPU-k **32**-es csoportokban hajtják végre a szálakat, amelyeket **wavefrontnak** neveznek. Egy wavefront összes szála ugyanazt az utasítást hajtja végre egyidejűleg. Ez befolyásolja az optimális blokkméret-választást (256 szál = 8 wavefront = jó ütemezési hatékonyság).

### AMD GPU programozás: HIP + ROCm

A **ROCm** az AMD nyílt forráskódú GPU számítási stack-je (illesztőprogramok, fordítók, könyvtárak, futtatókörnyezet). A **HIP** ezen a rétegen fut, és úgy tervezték, hogy szintaktikailag azonos legyen a CUDA-val. A PyTorch ROCm build-je átlátszó módon képezi le a `torch.cuda.*`-ot HIP-re, így ugyanaz a kód működik AMD GPU-kon is.

---

### PyTorch + AMD/HIP

A PyTorch egy olyan ROCm build-et kínál, ahol a CUDA API felületet (`torch.cuda.*`) átlátszó módon a HIP biztosítja. Ez azt jelenti, hogy:

- a `torch.cuda.is_available()` működik AMD GPU-kon ROCm-mal
- a `tensor.to("cuda")` az AMD GPU-n foglal memóriát
- a `torch.version.hip` felfedi a HIP verzióját

A PyTorch emellett elérhetővé teszi a `torch.cuda._compile_kernel()`-t is, amely egy magas szintű parancsikon egy nyers kernel string JIT lefordításához, és egy hívható objektum visszaadásához, külön build lépés nélkül.

---

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver előfeltételek telepítése
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Előfeltételek - Windows
- Telepítse a legújabb verziót: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux alatt nyisson meg egy terminált a választott könyvtárban, majd kövesse a parancsokat egy olyan venv létrehozásához, amelyben már telepítve van a ROCm+PyTorch.
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
**Adjon hozzáférést a felhasználójának a GPU eszközökhöz** (a hatásba lépéshez jelentkezzen ki, majd vissza):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux alatt nyisson meg egy terminált a választott könyvtárban, majd kövesse a parancsokat egy venv létrehozásához.
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
Windows alatt nyisson meg egy terminált a választott könyvtárban, majd kövesse a parancsokat egy venv létrehozásához.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tipp**: Előfordulhat, hogy a Windows felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
> RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell parancs futtatása előtt.

<!-- @os:end -->
### Alapvető függőségek telepítése
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
> **Megjegyzés:** Ehhez a playbookhoz a ROCm-ot és a PyTorch-ot a virtuális környezetbe kell telepíteni, még a Ryzen AI Halo esetén is, mivel az egyedi kernelfordításhoz a teljes fejlesztői fejlécekre van szükség.

Telepítse a ROCm-ot:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Telepítse a PyTorch-ot:
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

### További függőségek telepítése

<!-- @os:linux -->
Telepítse a Linux C/C++ build eszközláncot. Ez egy rendszerszintű függőség, és szükséges a C++ kiterjesztés bemutatókhoz, mivel a `CUDAExtension` natív `.so` modulokat épít `.cu` fájlokból.

Ezt egyszer futtassa a Linux gépen, a létrehozott Python virtuális környezeten kívül:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

A `kernel-env` virtuális környezet aktiválása után telepítse a Python build függőségeket:
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
Kérjük, győződjön meg róla, hogy a [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) vagy [újabb](https://visualstudio.microsoft.com/vs/community/) telepítve van a **Desktop development with C++** munkaterheléssel.

> **Megjegyzés**: Ez a Visual Studio C++ környezet beállítás csak a **C++ Extension** megközelítéshez szükséges. A JIT Compilation megközelítéshez nem szükséges.

Nyisson meg egy PowerShell terminált, és futtassa az alábbi parancsokat a C++ kiterjesztés elkészítése előtt.

**1. lépés: Keresse meg a telepített Visual Studio C++ környezetet**

**(A) Keresse meg a `vswhere.exe`-t, amely a Visual Studio Installerrel települ**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Keresse meg a `vcvars64.bat`-ot a Visual Studio 2022-ből vagy újabb verzióból, C++ build eszközökkel**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Írassa ki a használt Visual Studio C++ környezetet**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**2. lépés: A Visual Studio C++ build környezet aktiválása**

**(A) Futtassa a `vcvars64.bat`-ot, és rögzítse a beállított környezetet**

Ez elérhetővé teszi a `cl.exe`-t, az `INCLUDE`, `LIB`, `LIBPATH` változókat és a Windows SDK elérési útjait.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importálja a Visual Studio környezeti változóit ebbe a PowerShell munkamenetbe**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**3. lépés: Ellenőrizze, hogy a Microsoft C++ fordító elérhető-e**

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

#### Környezeti változók beállítása
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
Ellenőrizze, hogy az AMD GPU látható-e a következővel:
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

## Szükséges fájlok letöltése

Hozza létre a következő könyvtárstruktúrát a **2 új mappa** létrehozásával és a megfelelő fájlok letöltésével:

| Könyvtár | Letöltendő fájlok | Leírás |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT és C++ kiterjesztés fájlok a vektorösszeadás kernelhez |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT és C++ kiterjesztés fájlok a mátrixszorzás kernelhez |


## Bemutatók

### 1. bemutató: Vektorösszeadás

#### A megközelítés: JIT fordítás

A JIT (Just-In-Time) fordítás azt jelenti, hogy a kernel egy nyers C++ string formájában van megírva a Pythonban, és futásidőben kerül lefordításra, extra build lépések nélkül.

Az [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) használatához győződjön meg róla, hogy le van töltve, majd futtassa:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Kulcs kódrészletek**
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
> **Tipp**: A szkript emellett indít egy háttérszálat is, amely 100 ms-onként lekérdezi az `amd-smi`-t, hogy naplózza a csúcs- és átlagos GPU-kihasználtságot a kernel futása közben.
<!-- @os:end -->

> **Megjegyzés**: **Miért 256 a blokkméret?** <br>
> - A kernel **256 szálat blokkonként** használ, mert ez jól illeszkedik az **AMD GPU-k wavefront végrehajtási modelljéhez**.
> - Emlékeztetőül: az AMD hardver 32 szálas csoportokban hajtja végre a szálakat, ami blokkonként 8 wavefrontot eredményez. (8 wavefront x 32 szál = 1 blokk)


**Mit végez a munkaterhelés:**

A kernel mesterségesen extra munkát ad hozzá, hogy szemléltesse a GPU-kihasználtságot:

- **100 000 000 elem** a tenzorban
- A **belső ciklus 1000-szer fut** elemenként, kernelindításonként  
- **200 kernelindítás** összesen

**Matematika:**  
- Minden elem: 1-gyel nő × 1000 iteráció × 200 indítás = 200 000  
- Végeredmény: 1,0 (kezdőérték) + 200 000 (növelések) = 200 001,0

**Miért a belső ciklus?**  
- A `for (int i = 0; i < 1000; i++)` ciklus nélkül a 200 indítás azonnal befejeződne, és a monitorozó eszközök nem tudnának érdemi GPU-kihasználtságot rögzíteni. A mesterséges munka elég hosszúra nyújtja az egyes kernelfutásokat ahhoz, hogy a monitorozó eszközök mérni tudják a teljesítményt.

<!-- @os:linux -->
**Elvárt kimenet:**[A teljesítményértékek eltérőek lehetnek]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Windows rendszeren az `amd-smi` nem támogatott. A GPU-kihasználtság nyomon követéséhez használhatja a Feladatkezelőt, ahol a program futtatásakor egy rövid kihasználtsági csúcsot kell látnia.

**Elvárt kimenet:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Szép munka! Éppen most futtatta le az első GPU-kernelét.**

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
#### B megközelítés: C++ kiterjesztés

A második megközelítés kézi jellegű: a kernel és a Python-kötés egyetlen `.cu` fájlba kerül, natívan lefordítva a PyTorch build rendszerével, majd importálva Pythonba.

<!-- @os:windows -->
> **Megjegyzés**: A C++ kiterjesztés megközelítés a Visual Studio C++ build környezetet igényli, mivel a PyTorch a `.cu` forrásfájlt natív `.pyd` kiterjesztésmodullá fordítja. Ennek a natív kiterjesztésnek az elkészítése a Visual Studio által biztosított Microsoft C++ eszközlánctól (fordító, linker és build eszközök) függ. Futtassa a Visual Studio aktiváló parancsait a beállítási szakaszból, mielőtt lefordítaná a kiterjesztést.
<!-- @os:end -->

Töltse le a következő fájlokat, ha még nem tette meg:
<!-- @os:windows -->
| Fájl | Szerep |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + indító + pybind11 kötés, minden egy fájlban |
| [setup.py](assets/Vector_Addition/setup.py) | Build szkript, `CUDAExtension`-t használ a `.cu` fájl `.pyd`-vé fordításához |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python szkript, amely lefuttatja a lefordított artefaktumokat |
<!-- @os:end -->

<!-- @os:linux -->
| Fájl | Szerep |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + indító + pybind11 kötés, minden egy fájlban |
| [setup.py](assets/Vector_Addition/setup.py) | Build szkript, `CUDAExtension`-t használ a `.cu` fájl `.so`-vá fordításához |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python szkript, amely lefuttatja a lefordított artefaktumokat |
<!-- @os:end -->

#### **1. lépés: A kernel, az indító és a kötés** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tipp**: Miért használjuk a `hipDeviceSynchronize()`-t? <br>
> - A GPU kernel indítások aszinkronok. Amikor a CPU futtatja az `add_one<<<grid_size, block_size>>>(data, n);` sort, azonnal végrehajtja a következő utasítást anélkül, hogy megvárná a GPU-t. A `hipDeviceSynchronize()` arra kényszeríti a CPU-t, hogy megvárja a GPU kernel befejezését.

#### **2. lépés: Build**
```bash
pip install --no-build-isolation -v .
```
>**Megjegyzés**: Ez a parancs a `setup.py` fájlt keresi az aktuális könyvtárban a létrehozott .cu fájl lefordításához.


A `CUDAExtension` a `torch.utils.cpp_extension` egy CUDA build segédeszköze. ROCm esetén a PyTorch **átirányítja a `CUDAExtension`-t, hogy `hipcc`-t használjon** az `nvcc` helyett. A ROCm elfogja a build útvonalat, és a HIP fordítón keresztül irányítja, átültetve a CUDA kódot AMD-re.

Ez a következő fájlokat hozza létre:
<!-- @os:windows -->
- `build/`: könyvtár a `.pyd` fájlokkal
- `add_one_kernel.hip`: a `.cu` fájl hipify-olásával létrejött HIP forrás; ezt fordította valójában a `hipcc`
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: könyvtár a `.so` fájlokkal
- `add_one_kernel.hip`: a `.cu` fájl hipify-olásával létrejött HIP forrás; ezt fordította valójában a `hipcc`
<!-- @os:end -->

#### **3. lépés: Használat Pythonból** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Futtassa ezt a szkriptet, hogy lássa a kernelt működés közben:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Várt kimenet:**
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

### 2. bemutató: Mátrixszorzás

A mátrixszorzás kiszámítja a **C = A × B** eredményt, ahol:
- **A** M×N méretű (sorok × oszlopok)
- **B** N×K méretű  
- **C** M×K méretű (az eredmény)

Minden kimeneti elem a következőképpen definiált:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

A C minden eleme egymástól függetlenül számítható ki, ami tökéletessé teszi ezt a GPU-s párhuzamosításhoz.

#### Hogyan képeződik le a GPU szálakra

A vektoros összeadástól (1D) eltérően a mátrixszorzás **2D kimenetet** eredményez, ezért **2D szálrácsot** használunk:

| | Vektoros összeadás | Mátrixszorzás |
|---|---|---|
| **Kimeneti alak** | 1D tömb | 2D mátrix (M×K) |
| **Szálleképezés** | 1 szál → 1 elem | 1 szál → 1 kimeneti elem |
| **Indítási minta** | 1D rács: `(grid_x, 1, 1)` | 2D rács: `(grid_x, grid_y, 1)` |
| **Blokkméret** | `(256, 1, 1)` | `(16, 16, 1)` = 256 szál |

Minden szál a C kimeneti mátrix egy elemét számítja ki. A `(row, col)` pozícióban lévő szál a `C[row][col]`-t számítja ki az A megfelelő sorának és B megfelelő oszlopának szorzásával.

**Memóriaelrendezés**: A GPU memória lapos (1D), de a mátrixok soronként tárolódnak. Az `A[row][col]` eléréséhez a kernel az `A[row * N + col]`-t használja.


#### A megközelítés: JIT fordítás:

Az 1. bemutatóhoz hasonlóan a kernel nyers C++ karakterláncként van megírva a Pythonon belül, és futásidőben lesz lefordítva a PyTorch beépített JIT-jén keresztül.


A [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) használatához győződjön meg róla, hogy le van töltve, majd futtassa:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Kulcsfontosságú kódrészletek**
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

A szkript kis tűréssel ellenőrzi az eredményt a `torch.mm`-mel szemben. A lebegőpontos aritmetika GPU-kon kis numerikus eltéréseket eredményezhet a CPU implementációkhoz képest a párhuzamos redukció sorrendje miatt.

<!-- @os:linux -->
**Várt kimenet:**[A teljesítményértékek eltérhetnek]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Windows rendszeren az `amd-smi` nem támogatott. A GPU kihasználtságának nyomon követéséhez használhatja a Feladatkezelőt, ahol egy rövid kihasználtsági csúcsot kell látnia, amikor futtatja a programot.

**Várt kimenet:**
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
#### B megközelítés: C++ kiterjesztés

A második megközelítés kézi jellegű: a kernelt és a Python-kötést egyetlen `.cu` fájlba írjuk, natívan lefordítjuk a PyTorch build rendszerével, majd importáljuk Pythonba.

<!-- @os:windows -->
> **Megjegyzés**: A C++ kiterjesztés megközelítés a Visual Studio C++ build környezetet igényli, mivel a PyTorch a `.cu` forrásfájlt natív `.pyd` kiterjesztésmodullá fordítja. Ennek a natív kiterjesztésnek a felépítése a Visual Studio által biztosított Microsoft C++ eszközlánctól (fordító, linker és build eszközök) függ. Futtassa a Visual Studio aktiválási parancsait a beállítási szakaszból, mielőtt felépítené a kiterjesztést.
<!-- @os:end -->

Töltse le a következő fájlokat, ha még nem tette meg:
<!-- @os:windows -->
| Fájl | Szerep |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + indító + pybind11 kötés |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build szkript, `CUDAExtension`-t használ a `.cu` fájl `.pyd`-vé fordításához |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python szkript, amely futtatja a felépített artefaktumokat |
<!-- @os:end -->
<!-- @os:linux -->
| Fájl | Szerep |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + indító + pybind11 kötés |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build szkript, `CUDAExtension`-t használ a `.cu` fájl `.so`-vá fordításához |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python szkript, amely futtatja a felépített artefaktumokat |
<!-- @os:end -->

#### **1. lépés: A kernel, az indító és a kötés** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Az 1. bemutatóban szereplő `add_one_launcher`-hez képest az itteni indító:
- Egy helyett két bemeneti tenzort fogad
- Mindhárom dimenziót (M, N, K) a tenzorok alakjából származtatja, nincs szükség manuális méretátadásra Pythonból
- Lefoglalja és visszaadja a C kimeneti tenzort, ahelyett hogy helyben módosítaná
- `dim3`-at használ a griden és a blokkon egyaránt, hogy kifejezze a 2D indítási alakot

#### **2. lépés: Fordítás**
```bash
pip install --no-build-isolation -v .
```
>**Megjegyzés**: Ez a parancs a `setup.py` fájlt keresi az aktuális könyvtárban, hogy felépítse az általunk létrehozott .cu fájlt.


Ez a következő fájlokat hozza létre:
<!-- @os:windows -->
- `build/`: könyvtár a `.pyd` fájlokkal
- `matmul_kernel.hip`: a HIP forrás, amely a `.cu` fájl hipify-olásával jött létre; ezt fordította le ténylegesen a `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: könyvtár a `.so` fájlokkal
- `matmul_kernel.hip`: a HIP forrás, amely a `.cu` fájl hipify-olásával jött létre; ezt fordította le ténylegesen a `hipcc`
<!-- @os:end -->

#### **3. lépés: Használat Pythonból** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Futtassa ezt a szkriptet, hogy lássa a kernelt működés közben:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Várt kimenet:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Kiváló! Éppen most valósította meg a mátrixszorzást a GPU-n.** Ez jelentős mérföldkő, mivel a mátrixszorzás a modern gépi tanulási műveletek gerince, mint például:
- Neurális hálózati rétegek
- Figyelem (attention) mechanizmusok
- Beágyazások
- Transzformerek

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

## Következő lépések

Megtanulta, hogyan írjon, fordítson és indítson el GPU kernelt JIT fordítás és C++ kiterjesztések használatával alapvető párhuzamos műveletekhez.

**Teljesítményoptimalizálások:**
- **Megosztott memória csempézés (tiling)** - Adatblokkok gyorsítótárazása a globális memóriaelérés csökkentése érdekében
- **Memóriaegyesítés (coalescing)** - A memóriaelérési minták optimalizálása a sávszélesség érdekében

**Valós algoritmusok:**
- **2D konvolúció** - Egy kis szűrő (kernel) végigcsúszik egy képen, minden kimeneti pixelt a szomszédos pixelek súlyozott összegéből számítva. Ez bevezeti a stencil számításokat és a megosztott memória csempézését, ahol a szálak újrahasznosítják az átfedő képrégiókat a globális memóriaelérés csökkentése érdekében.
- **Softmax függvény**: A softmax egy számvektort valószínűségekké alakít, amelyek összege 1, gyakran használt neurális hálózati kimenetekben. Hatékony GPU-s megvalósítása bevezeti a párhuzamos redukciókat és a numerikus stabilitási technikákat nagy vektorok feldolgozása közben.

**Éles környezeti megfontolások:**
- **Hibakezelés** - Határellenőrzés és eszközkezelés
- **PyTorch integráció** - Egyéni operátorok autograd támogatással