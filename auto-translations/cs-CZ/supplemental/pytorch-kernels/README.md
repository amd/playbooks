<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Napište GPU kernel od začátku, zkompilujte ho, spusťte na AMD GPU a sledujte, jak vzroste vytížení. Tento playbook ukazuje, jak GPU výpočty skutečně fungují: napíšete kód kernelu a spustíte ho paralelně napříč tisíci vlákny.

> **Poznámka**: Jedná se o poměrně komplexní playbook, který si může vyžádat další ladění a úpravy.

## Co se naučíte

<!-- @os:windows -->
- Jak fungují GPU kernely: grids, blocks, threads a model indexování, který je mapuje na data
- Jak vám zásobník AMD ROCm/HIP umožňuje psát kód ve stylu CUDA, který běží na AMD GPU bez úprav
- Jak zkompilovat kernel za běhu pomocí `torch.cuda._compile_kernel`
- Jak sestavit nativní rozšíření kernelu v C++ pomocí `CUDAExtension` + pybind11, importovatelné z Pythonu
<!-- @os:end -->
<!-- @os:linux -->
- Jak fungují GPU kernely: grids, blocks, threads a model indexování, který je mapuje na data
- Jak vám zásobník AMD ROCm/HIP umožňuje psát kód ve stylu CUDA, který běží na AMD GPU bez úprav
- Jak zkompilovat kernel za běhu pomocí `torch.cuda._compile_kernel`
- Jak sestavit nativní rozšíření kernelu v C++ pomocí `CUDAExtension` + pybind11, importovatelné z Pythonu
- Jak měřit dobu provádění kernelu a sledovat živé vytížení GPU pomocí `amd-smi`
<!-- @os:end -->

---

Tento playbook popisuje dva přístupy k vývoji kernelů:

<!-- @os:windows -->
| Přístup | Vstupní bod |
|---|---|
| **JIT kompilace** | `torch.cuda._compile_kernel`, napište kernel jako řetězec v Pythonu, bez sestavovacího kroku |
| **Rozšíření v C++** | `CUDAExtension` + pybind11: zkompilujte soubor `.cu` do nativního `.pyd` a importujte ho |
<!-- @os:end -->
<!-- @os:linux -->
| Přístup | Vstupní bod |
|---|---|
| **JIT kompilace** | `torch.cuda._compile_kernel`, napište kernel jako řetězec v Pythonu, bez sestavovacího kroku |
| **Rozšíření v C++** | `CUDAExtension` + pybind11: zkompilujte soubor `.cu` do nativního `.so` a importujte ho |
<!-- @os:end -->

Oba přístupy fungují na AMD GPU. Je to možné díky tomu, že ROCm sestavení PyTorch mapuje celé rozhraní CUDA API na HIP. To znamená, že `torch.cuda`, `CUDAExtension` a syntaxe CUDA kernelů fungují na hardwaru AMD transparentně.

---

## Souvislosti

### Co je GPU kernel?

GPU kernel je funkce, která běží paralelně napříč tisíci vlákny GPU současně. Na rozdíl od funkce CPU, která se při volání provede jednou, je kernel spouštěn s **grid** (mřížkou) **blocks** (bloků), z nichž každý obsahuje mnoho **threads** (vláken), přičemž všechna provádějí stejný kód nad různými daty.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indexování vláken

Při spouštění kernelu zadáváte dvě dimenze:

| Proměnná | Význam |
|---|---|
| `gridDim` | Počet bloků v mřížce |
| `blockDim` | Počet vláken na blok |

Každé vlákno má přístup ke třem vestavěným proměnným pouze pro čtení:

| Proměnná | Význam |
|---|---|
| `blockIdx.x` | Do kterého bloku toto vlákno patří |
| `blockDim.x` | Počet vláken v jednom bloku |
| `threadIdx.x` | Index vlákna v rámci jeho bloku |

### Globální ID vlákna

Tyto proměnné se kombinují a vypočítá se z nich globálně jedinečný index vlákna:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Celkový počet vláken = `gridDim.x * blockDim.x`. Každé vlákno zpracovává jeden prvek nezávisle. To je základ **datového paralelismu**. Stejná operace probíhá nad mnoha prvky současně, bez závislosti mezi vlákny.

---

### Model provádění GPU: Wavefronty

GPU AMD provádějí vlákna ve skupinách po **32**, nazývaných **wavefronty**. Všechna vlákna ve wavefrontu provádějí stejnou instrukci současně. To ovlivňuje optimální volbu velikosti bloku (256 vláken = 8 wavefrontů = dobrá efektivita plánování).

### Programování GPU AMD: HIP + ROCm

**ROCm** je open-source výpočetní zásobník AMD pro GPU (ovladače, kompilátory, knihovny, runtime). **HIP** na něm staví a je navržen tak, aby byl syntakticky totožný s CUDA. ROCm sestavení PyTorch transparentně mapuje `torch.cuda.*` na HIP, takže stejný kód funguje na AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch dodává ROCm sestavení, ve kterém je rozhraní CUDA API (`torch.cuda.*`) transparentně podporováno pomocí HIP. To znamená:

- `torch.cuda.is_available()` funguje na AMD GPU s ROCm
- `tensor.to("cuda")` alokuje na AMD GPU
- `torch.version.hip` zpřístupňuje verzi HIP

PyTorch také poskytuje `torch.cuda._compile_kernel()`, vysokoúrovňovou zkratku pro JIT kompilaci řetězce se surovým kernelem a získání volatelného objektu zpět, bez nutnosti samostatného kroku sestavení.

---

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Předpoklady – Windows
- Nainstalujte nejnovější: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
V systému Linux otevřete terminál v adresáři dle vlastního výběru a pomocí následujících příkazů vytvořte venv s již nainstalovaným ROCm+Pytorch.
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
**Udělte svému uživateli přístup k zařízením GPU** (aby se změna projevila, odhlaste se a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

V systému Linux otevřete terminál v adresáři dle vlastního výběru a pomocí následujících příkazů vytvořte venv.
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
V systému Windows otevřete terminál v adresáři dle vlastního výběru a pomocí následujících příkazů vytvořte venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Uživatelé Windows mohou potřebovat upravit zásady spouštění (Execution Policy) v PowerShellu (např.
> nastavit ji na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @os:end -->
### Instalace základních závislostí
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
> **Poznámka:** Pro tuto příručku je nutné nainstalovat ROCm a PyTorch do virtuálního prostředí i na Ryzen AI Halo, protože kompilace vlastních kernelů vyžaduje kompletní vývojové hlavičkové soubory.

Nainstalujte ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Nainstalujte PyTorch:
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

### Instalace dalších závislostí

<!-- @os:linux -->
Nainstalujte sadu nástrojů pro sestavování jazyka C/C++ pro Linux. Jedná se o systémovou závislost, která je nutná pro ukázky rozšíření v C++, protože `CUDAExtension` sestavuje nativní moduly `.so` ze souborů `.cu`.

Spusťte toto jednou na linuxovém počítači, mimo vytvořené virtuální prostředí Pythonu:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktivaci virtuálního prostředí `kernel-env` nainstalujte závislosti pro sestavování v Pythonu:
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
Zajistěte, aby byl nainstalován [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) nebo [novější](https://visualstudio.microsoft.com/vs/community/) s pracovní zátěží **Desktop development with C++**.

> **Poznámka**: Toto nastavení prostředí Visual Studio C++ je nutné pouze pro přístup **C++ Extension**. Pro přístup JIT Compilation není potřeba.

Otevřete terminál PowerShell a před sestavením rozšíření v C++ spusťte následující příkazy.

**Krok 1: Vyhledejte nainstalované prostředí Visual Studio C++**

**(A) Vyhledejte `vswhere.exe`, který se instaluje s Visual Studio Installerem**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Vyhledejte `vcvars64.bat` z Visual Studio 2022 nebo novějšího s nástroji pro sestavování C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Vypište používané prostředí Visual Studio C++**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Krok 2: Aktivujte sestavovací prostředí Visual Studio C++**

**(A) Spusťte `vcvars64.bat` a zachyťte prostředí, které nastavuje**

Tím se zpřístupní `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` a cesty k Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importujte proměnné prostředí Visual Studia do této relace PowerShellu**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Krok 3: Ověřte, že je k dispozici kompilátor Microsoft C++**

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

#### Nastavení proměnných prostředí
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
Ověřte, že je GPU AMD viditelné pomocí:
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

## Stažení potřebných souborů

Vytvořte následující strukturu adresářů vytvořením **2 nových složek** a stažením odpovídajících souborů:

| Adresář | Soubory ke stažení | Popis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Soubory pro JIT a rozšíření v C++ pro kernel sčítání vektorů |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Soubory pro JIT a rozšíření v C++ pro kernel násobení matic |


## Ukázky postupu

### Ukázka postupu 1: Sčítání vektorů

#### Přístup A: JIT Compilation

JIT (Just-In-Time) kompilace znamená, že kernel je napsán jako řetězec v jazyce C++ přímo v Pythonu a je zkompilován za běhu, bez nutnosti dalších kroků sestavování.

Chcete-li použít [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), ujistěte se, že je stažený, a spusťte:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Klíčové úryvky kódu**
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
> **Tip**: Skript také spustí vlákno na pozadí, které každých 100 ms dotazuje `amd-smi`, aby zaznamenávalo špičkové a průměrné využití GPU během běhu kernelu.
<!-- @os:end -->

> **Poznámka**: **Proč je velikost bloku 256?** <br>
> - Kernel používá **256 vláken na blok**, protože to dobře odpovídá **modelu provádění wavefrontů u GPU AMD**.
> - Připomeňme, že hardware AMD provádí vlákna ve skupinách po 32 vláknech, což vede k 8 wavefrontům na blok. (8 wavefrontů x 32 vláken = 1 blok)


**Co pracovní zátěž dělá:**

Kernel uměle přidává další práci, aby demonstroval využití GPU:

- **100 000 000 prvků** v tenzoru
- **Vnitřní smyčka běží 1 000krát** na prvek při každém spuštění kernelu  
- **200 spuštění kernelu** celkem

**Matematika:**  
- Každý prvek: je zvýšen o 1 × 1 000 iterací × 200 spuštění = 200 000  
- Konečný výsledek: 1,0 (počáteční hodnota) + 200 000 (přičtení) = 200 001,0

**Proč vnitřní smyčka?**  
- Bez smyčky `for (int i = 0; i < 1000; i++)` by 200 spuštění skončilo okamžitě a monitorovací nástroje by nezachytily smysluplné využití GPU. Umělá práce zajistí, že každé spuštění kernelu trvá dostatečně dlouho na to, aby monitorovací nástroje mohly měřit výkon.

<!-- @os:linux -->
**Očekávaný výstup:**[Hodnoty výkonu se budou lišit]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Na Windows není `amd-smi` podporován. Pro sledování využití GPU můžete použít Správce úloh, kde by se mělo při spuštění programu zobrazit krátké zvýšení využití.

**Očekávaný výstup:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Skvělá práce! Právě jste spustili svůj první kernel GPU.**

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
#### Přístup B: Rozšíření v C++

Druhý přístup je více manuální: napište jádro a vazbu Python do jediného souboru `.cu`, zkompilujte jej nativně pomocí sestavovacího systému PyTorch a importujte jej do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Přístup pomocí rozšíření v C++ vyžaduje sestavovací prostředí Visual Studio C++, protože PyTorch kompiluje zdrojový soubor `.cu` do nativního modulu rozšíření `.pyd`. Sestavení tohoto nativního rozšíření závisí na sadě nástrojů Microsoft C++ (kompilátor, linker a sestavovací nástroje) poskytované Visual Studiem. Před sestavením rozšíření spusťte příkazy pro aktivaci Visual Studia z části o instalaci.
<!-- @os:end -->

Pokud jste to ještě neudělali, stáhněte si následující soubory:
<!-- @os:windows -->
| Soubor | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Jádro + spouštěč + vazba pybind11, vše v jednom souboru |
| [setup.py](assets/Vector_Addition/setup.py) | Sestavovací skript, využívá `CUDAExtension` ke kompilaci souboru `.cu` do `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

<!-- @os:linux -->
| Soubor | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Jádro + spouštěč + vazba pybind11, vše v jednom souboru |
| [setup.py](assets/Vector_Addition/setup.py) | Sestavovací skript, využívá `CUDAExtension` ke kompilaci souboru `.cu` do `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

#### **Krok 1: Jádro, spouštěč a vazba** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Proč používat `hipDeviceSynchronize()`? <br>
> - Spouštění jader GPU je asynchronní. Když CPU spustí `add_one<<<grid_size, block_size>>>(data, n);`, ihned pokračuje dalším příkazem, aniž by čekal na GPU. `hipDeviceSynchronize()` donutí CPU počkat, dokud jádro na GPU nedokončí svou práci.

#### **Krok 2: Sestavení**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento příkaz hledá soubor `setup.py` v aktuálním adresáři, aby sestavil vytvořený soubor .cu.


`CUDAExtension` je pomocník pro sestavování CUDA z modulu `torch.utils.cpp_extension`. S ROCm PyTorch **přesměruje `CUDAExtension` na použití `hipcc`** místo `nvcc`. ROCm zachytí cestu sestavení a přesměruje ji přes kompilátor HIP, čímž portuje kód CUDA na hardware AMD.

Výsledkem jsou následující soubory:
<!-- @os:windows -->
- `build/`: adresář se soubory `.pyd`
- `add_one_kernel.hip`: zdrojový kód HIP vygenerovaný „hipifikací“ souboru `.cu`; toto je to, co skutečně zkompiloval `hipcc`
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: adresář se soubory `.so`
- `add_one_kernel.hip`: zdrojový kód HIP vygenerovaný „hipifikací“ souboru `.cu`; toto je to, co skutečně zkompiloval `hipcc`
<!-- @os:end -->

#### **Krok 3: Použití z Pythonu** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Spusťte tento skript, abyste viděli jádro v akci:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Očekávaný výstup:**
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

### Návod 2: Násobení matic

Násobení matic počítá **C = A × B**, kde:
- **A** je M×N (řádky × sloupce)
- **B** je N×K  
- **C** je M×K (výsledek)

Každý prvek výstupu je definován jako:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Každý prvek matice C se počítá nezávisle, což je ideální pro paralelismus na GPU.

#### Jak se to mapuje na vlákna GPU

Na rozdíl od sčítání vektorů (1D) produkuje násobení matic **2D výstup**, proto použijeme **2D mřížku vláken**:

| | Sčítání vektorů | Násobení matic |
|---|---|---|
| **Tvar výstupu** | 1D pole | 2D matice (M×K) |
| **Mapování vláken** | 1 vlákno → 1 prvek | 1 vlákno → 1 výstupní prvek |
| **Vzor spouštění** | 1D mřížka: `(grid_x, 1, 1)` | 2D mřížka: `(grid_x, grid_y, 1)` |
| **Velikost bloku** | `(256, 1, 1)` | `(16, 16, 1)` = 256 vláken |

Každé vlákno počítá jeden prvek výstupní matice C. Vlákno na pozici `(row, col)` počítá `C[row][col]` vynásobením odpovídajícího řádku matice A s odpovídajícím sloupcem matice B.

**Rozvržení paměti**: Paměť GPU je plochá (1D), ale matice jsou uloženy řádek po řádku. Pro přístup k `A[row][col]` používá jádro výraz `A[row * N + col]`.


#### Přístup A: Kompilace JIT:

Stejně jako v návodu 1 je jádro napsáno jako řetězec v jazyce C++ přímo v Pythonu a kompilováno za běhu pomocí vestavěného JIT nástroje PyTorch.


Chcete-li použít soubor [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), ujistěte se, že je stažený, a spusťte:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Klíčové úryvky kódu**
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

Skript ověřuje výsledek oproti `torch.mm` s malou tolerancí. Aritmetika s plovoucí desetinnou čárkou na GPU může produkovat mírné číselné rozdíly oproti implementacím na CPU kvůli pořadí paralelní redukce.

<!-- @os:linux -->
**Očekávaný výstup:** [Hodnoty výkonu se budou lišit]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Na Windows není `amd-smi` podporován. Pro sledování využití GPU můžete použít Správce úloh, kde byste měli vidět krátký nárůst využití při spuštění programu.

**Očekávaný výstup:**
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
#### Přístup B: Rozšíření v jazyce C++

Druhý přístup je manuálnější: zapište jádro a Python binding do jednoho souboru `.cu`, zkompilujte jej nativně pomocí sestavovacího systému PyTorch a importujte jej do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Přístup s rozšířením v jazyce C++ vyžaduje sestavovací prostředí Visual Studio C++, protože PyTorch kompiluje zdrojový soubor `.cu` do nativního modulu rozšíření `.pyd`. Sestavení tohoto nativního rozšíření závisí na řetězci nástrojů Microsoft C++ (kompilátor, linker a sestavovací nástroje) poskytovaných Visual Studio. Před sestavením rozšíření spusťte příkazy pro aktivaci Visual Studio z části o nastavení.
<!-- @os:end -->

Stáhněte si následující soubory, pokud jste to ještě neudělali:
<!-- @os:windows -->
| Soubor | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Jádro + spouštěč + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci souboru `.cu` do `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->
<!-- @os:linux -->
| Soubor | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Jádro + spouštěč + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci souboru `.cu` do `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

#### **Krok 1: Jádro, spouštěč a binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Ve srovnání s `add_one_launcher` v ukázce 1 tento spouštěč:
- Přijímá dva vstupní tenzory místo jednoho
- Odvozuje všechny tři rozměry (M, N, K) z tvarů tenzorů, bez ručního předávání velikostí z Pythonu
- Alokuje a vrací výstupní tenzor C, místo aby jej upravoval na místě
- Používá `dim3` pro mřížku i blok, aby vyjádřil 2D tvar spuštění

#### **Krok 2: Sestavení**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento příkaz hledá soubor `setup.py` v aktuálním adresáři, aby sestavil vytvořený soubor .cu.


Tím se vytvoří následující soubory:
<!-- @os:windows -->
- `build/`: adresář se soubory `.pyd`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikací souboru `.cu`; toto je to, co ve skutečnosti zkompiloval `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: adresář se soubory `.so`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikací souboru `.cu`; toto je to, co ve skutečnosti zkompiloval `hipcc`
<!-- @os:end -->

#### **Krok 3: Použití z Pythonu** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Spusťte tento skript, abyste viděli jádro v akci:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Očekávaný výstup:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Skvělé! Právě jste implementovali násobení matic na GPU.** Toto je významný milník, protože násobení matic je páteří moderních operací strojového učení, jako jsou:
- Vrstvy neuronových sítí
- Mechanismy pozornosti (attention)
- Vkládání (embeddings)
- Transformery

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

## Další kroky

Naučili jste se psát, kompilovat a spouštět jádra GPU pomocí JIT kompilace i rozšíření v jazyce C++ pro základní paralelní operace.

**Optimalizace výkonu:**
- **Tiling sdílené paměti** - Ukládání bloků dat do mezipaměti za účelem snížení přístupů do globální paměti
- **Slučování paměti (memory coalescing)** - Optimalizace vzorců přístupu do paměti pro šířku pásma

**Algoritmy z reálného světa:**
- **2D konvoluce** - Malý filtr (jádro) posouvá se přes obrázek a počítá každý výstupní pixel jako vážený součet sousedních pixelů. Tím se zavádí stencil computations (výpočty se šablonou) a tiling sdílené paměti, kde vlákna znovu využívají překrývající se oblasti obrázku, aby se snížil přístup do globální paměti.
- **Funkce Softmax**: Softmax převádí vektor čísel na pravděpodobnosti, jejichž součet je 1, což se běžně používá ve výstupech neuronových sítí. Efektivní implementace na GPU zavádí paralelní redukce a techniky numerické stability při zpracování velkých vektorů.

**Aspekty pro produkční nasazení:**
- **Zpracování chyb** - Kontrola mezí a správa zařízení
- **Integrace s PyTorch** - Vlastní operátory s podporou autogradu