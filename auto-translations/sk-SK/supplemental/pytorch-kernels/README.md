<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

Napíšte jadro GPU (kernel) od základu, skompilujte ho, spustite na AMD GPU a sledujte, ako stúpa vyťaženie. Táto príručka ukazuje, ako výpočty na GPU skutočne fungujú: napíšete kód jadra a spustíte ho paralelne naprieč tisíckami vlákien.

> **Poznámka**: Toto je pomerne zložitá príručka, ktorá si môže vyžadovať ďalšie ladenie a úpravy.

## Čo sa naučíte

<!-- @os:windows -->
- Ako fungujú jadrá GPU: mriežky, bloky, vlákna a model indexovania, ktorý ich mapuje na dáta
- Ako softvérový balík AMD ROCm/HIP umožňuje písať kód v štýle CUDA, ktorý beží na AMD GPU bez úprav
- Ako skompilovať jadro za behu pomocou `torch.cuda._compile_kernel`
- Ako vytvoriť natívne rozšírenie jadra v C++ pomocou `CUDAExtension` + pybind11, ktoré je možné importovať z Pythonu
<!-- @os:end -->
<!-- @os:linux -->
- Ako fungujú jadrá GPU: mriežky, bloky, vlákna a model indexovania, ktorý ich mapuje na dáta
- Ako softvérový balík AMD ROCm/HIP umožňuje písať kód v štýle CUDA, ktorý beží na AMD GPU bez úprav
- Ako skompilovať jadro za behu pomocou `torch.cuda._compile_kernel`
- Ako vytvoriť natívne rozšírenie jadra v C++ pomocou `CUDAExtension` + pybind11, ktoré je možné importovať z Pythonu
- Ako merať čas vykonávania jadra a sledovať vyťaženie GPU v reálnom čase pomocou `amd-smi`
<!-- @os:end -->

---

Táto príručka zahŕňa dva prístupy k vývoju jadier:

<!-- @os:windows -->
| Prístup | Vstupný bod |
|---|---|
| **JIT kompilácia** | `torch.cuda._compile_kernel`, napíšte jadro ako reťazec Python, bez kroku zostavovania |
| **Rozšírenie C++** | `CUDAExtension` + pybind11: skompilujte súbor `.cu` do natívneho `.pyd` a importujte ho |
<!-- @os:end -->
<!-- @os:linux -->
| Prístup | Vstupný bod |
|---|---|
| **JIT kompilácia** | `torch.cuda._compile_kernel`, napíšte jadro ako reťazec Python, bez kroku zostavovania |
| **Rozšírenie C++** | `CUDAExtension` + pybind11: skompilujte súbor `.cu` do natívneho `.so` a importujte ho |
<!-- @os:end -->

Oba prístupy fungujú na AMD GPU. Je to možné vďaka tomu, že zostava PyTorch pre ROCm mapuje celý povrch API CUDA na HIP. To znamená, že `torch.cuda`, `CUDAExtension` a syntax jadier CUDA fungujú na hardvéri AMD transparentne.

---

## Pozadie

### Čo je jadro GPU (GPU Kernel)?

Jadro GPU je funkcia, ktorá beží paralelne naprieč tisíckami vlákien GPU súčasne. Na rozdiel od funkcie CPU, ktorá sa vykoná raz pri každom volaní, jadro sa spúšťa s **mriežkou** (grid) **blokov** (blocks), z ktorých každý obsahuje mnoho **vlákien** (threads), pričom všetky vykonávajú rovnaký kód na rôznych dátach.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indexovania vlákien

Pri spúšťaní jadra zadávate dve rozmery:

| Premenná | Význam |
|---|---|
| `gridDim` | Počet blokov v mriežke |
| `blockDim` | Počet vlákien na blok |

Každé vlákno má prístup k trom zabudovaným premenným určeným len na čítanie:

| Premenná | Význam |
|---|---|
| `blockIdx.x` | Do ktorého bloku toto vlákno patrí |
| `blockDim.x` | Počet vlákien v jednom bloku |
| `threadIdx.x` | Index vlákna v rámci jeho bloku |

### Globálne ID vlákna

Tieto premenné sa kombinujú na výpočet globálne jedinečného indexu vlákna:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Celkový počet vlákien = `gridDim.x * blockDim.x`. Každé vlákno spracúva jeden prvok nezávisle. Toto je základ **dátovej paralelnosti**. Rovnaká operácia sa vykonáva na mnohých prvkoch naraz, bez závislosti medzi vláknami.

---

### Model vykonávania GPU: Wavefronty

GPU AMD vykonávajú vlákna v skupinách po **32** nazývaných **wavefronty**. Všetky vlákna vo wavefronte vykonávajú rovnakú inštrukciu súčasne. Toto ovplyvňuje optimálnu voľbu veľkosti bloku (256 vlákien = 8 wavefrontov = dobrá efektivita plánovania).

### Programovanie GPU AMD: HIP + ROCm

**ROCm** je open-source softvérový balík AMD pre výpočty na GPU (ovládače, kompilátory, knižnice, runtime). **HIP** stojí nad ním a je navrhnutý tak, aby bol syntakticky identický s CUDA. Zostava PyTorch pre ROCm transparentne mapuje `torch.cuda.*` na HIP, takže rovnaký kód funguje na AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch poskytuje zostavu pre ROCm, v ktorej je povrch API CUDA (`torch.cuda.*`) transparentne podporovaný cez HIP. To znamená:

- `torch.cuda.is_available()` funguje na AMD GPU s ROCm
- `tensor.to("cuda")` alokuje pamäť na AMD GPU
- `torch.version.hip` zobrazuje verziu HIP

PyTorch tiež poskytuje `torch.cuda._compile_kernel()`, praktickú skratku na JIT kompiláciu reťazca surového jadra a získanie volateľného objektu bez potreby samostatného kroku zostavovania.

---

<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových požiadaviek
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Požiadavky – Windows
- Nainštalujte najnovšiu verziu: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+PyTorch.
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (odhláste sa a znova prihláste, aby sa táto zmena prejavila):

```bash
sudo usermod -aG render,video $LOGNAME
```

V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
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
V systéme Windows otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Používatelia systému Windows možno budú musieť pred spustením niektorých príkazov PowerShell upraviť svoju politiku spúšťania PowerShell (napr.
> nastaviť ju na RemoteSigned alebo Unrestricted).

<!-- @os:end -->
### Inštalácia základných závislostí
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
> **Poznámka:** Pre tento playbook je potrebné nainštalovať ROCm a PyTorch do virtuálneho prostredia aj na Ryzen AI Halo, keďže kompilácia vlastných jadier (kernelov) vyžaduje kompletné vývojové hlavičky.

Nainštalujte ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Nainštalujte PyTorch:
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

### Inštalácia ďalších závislostí

<!-- @os:linux -->
Nainštalujte reťazec nástrojov na zostavovanie C/C++ pre Linux. Ide o systémovú závislosť, ktorá je potrebná pre postupy s rozšíreniami v C++, pretože `CUDAExtension` zostavuje natívne moduly `.so` zo súborov `.cu`.

Spustite toto raz na počítači s Linuxom, mimo vytvoreného virtuálneho prostredia Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktivácii virtuálneho prostredia `kernel-env` nainštalujte závislosti na zostavovanie Python:
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
Uistite sa, že máte nainštalované [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) alebo [novšie](https://visualstudio.microsoft.com/vs/community/) s pracovným zaťažením **Desktop development with C++**.

> **Poznámka**: Toto nastavenie prostredia Visual Studio C++ je potrebné iba pre prístup s **C++ rozšírením**. Pre prístup s JIT kompiláciou nie je potrebné.

Otvorte terminál PowerShell a pred zostavením C++ rozšírenia spustite nasledujúce príkazy.

**Krok 1: Nájdite nainštalované prostredie Visual Studio C++**

**(A) Nájdite `vswhere.exe`, ktorý sa inštaluje spolu s inštalátorom Visual Studio**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Nájdite `vcvars64.bat` z Visual Studio 2022 alebo novšieho s nástrojmi na zostavovanie v C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Vypíšte používané prostredie Visual Studio C++**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Krok 2: Aktivujte prostredie na zostavovanie Visual Studio C++**

**(A) Spustite `vcvars64.bat` a zachyťte prostredie, ktoré nastaví**

Tým sa sprístupnia `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` a cesty k sadám Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importujte premenné prostredia Visual Studio do tejto relácie PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Krok 3: Overte, že je k dispozícii kompilátor Microsoft C++**

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

#### Nastavenie premenných prostredia
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
Overte, že je GPU od AMD viditeľné pomocou:
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

## Stiahnutie potrebných súborov

Vytvorte nasledujúcu adresárovú štruktúru vytvorením **2 nových priečinkov** a stiahnutím príslušných súborov:

| Adresár | Súbory na stiahnutie | Popis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Súbory pre JIT a C++ rozšírenie pre jadro sčítania vektorov |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Súbory pre JIT a C++ rozšírenie pre jadro násobenia matíc |


## Postupy

### Postup 1: Sčítanie vektorov

#### Prístup A: JIT kompilácia

JIT (Just-In-Time) kompilácia znamená, že jadro je napísané ako reťazec surového kódu C++ vnútri Pythonu a kompiluje sa za behu, bez potreby ďalších krokov zostavovania.

Ak chcete použiť [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), uistite sa, že je stiahnutý, a spustite:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Kľúčové úryvky kódu**
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
> **Tip**: Skript tiež spustí vlákno na pozadí, ktoré každých 100 ms dopytuje `amd-smi`, aby zaznamenávalo maximálne a priemerné využitie GPU počas behu jadra.
<!-- @os:end -->

> **Poznámka**: **Prečo je veľkosť bloku 256?** <br>
> - Jadro používa **256 vlákien na blok**, pretože to dobre zodpovedá **modelu vykonávania vo wavefrontoch na GPU od AMD**.
> - Pripomeňme, že hardvér AMD vykonáva vlákna v skupinách po 32 vláknach, čo vedie k 8 wavefrontom na blok. (8 wavefrontov x 32 vlákien = 1 blok)


**Čo daná záťaž robí:**

Jadro umelo pridáva ďalšiu prácu, aby demonštrovalo využitie GPU:

- **100 000 000 prvkov** v tenzore
- **Vnútorný cyklus sa vykoná 1 000-krát** na prvok pri každom spustení jadra  
- **200 spustení jadra** celkovo

**Výpočet:**  
- Každý prvok: sa zvýši o 1 × 1 000 iterácií × 200 spustení = 200 000  
- Konečný výsledok: 1,0 (počiatočná hodnota) + 200 000 (sčítania) = 200 001,0

**Prečo vnútorný cyklus?**  
- Bez cyklu `for (int i = 0; i < 1000; i++)` by sa 200 spustení dokončilo okamžite a nástroje na monitorovanie by nezachytili zmysluplné využitie GPU. Umelá práca zabezpečí, že každé spustenie jadra trvá dostatočne dlho na to, aby ho nástroje na monitorovanie dokázali odmerať.

<!-- @os:linux -->
**Očakávaný výstup:**[Výkonnostné čísla sa budú líšiť]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Vo Windows nie je `amd-smi` podporované. Na sledovanie využitia GPU môžete použiť Správcu úloh, kde by ste mali vidieť krátky nárast využitia pri spustení programu.

**Očakávaný výstup:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Skvelá práca! Práve ste spustili svoje prvé jadro na GPU.**

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
#### Prístup B: Rozšírenie v C++

Druhý prístup je viac manuálny: napíšete kernel a Python binding do jedného súboru `.cu`, natívne ho skompilujete pomocou build systému PyTorch a importujete ho do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Prístup s rozšírením v C++ vyžaduje build prostredie Visual Studio C++, pretože PyTorch kompiluje zdrojový súbor `.cu` do natívneho rozšírujúceho modulu `.pyd`. Zostavenie tohto natívneho rozšírenia závisí od nástrojového reťazca Microsoft C++ (kompilátor, linker a build nástroje) poskytovaného Visual Studio. Pred zostavením rozšírenia spustite aktivačné príkazy pre Visual Studio zo sekcie nastavenia.
<!-- @os:end -->

Ak ste to ešte neurobili, stiahnite si nasledujúce súbory:
<!-- @os:windows -->
| Súbor | Úloha |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + spúšťač + pybind11 binding, všetko v jednom súbore |
| [setup.py](assets/Vector_Addition/setup.py) | Build skript, používa `CUDAExtension` na skompilovanie `.cu` do `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

<!-- @os:linux -->
| Súbor | Úloha |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + spúšťač + pybind11 binding, všetko v jednom súbore |
| [setup.py](assets/Vector_Addition/setup.py) | Build skript, používa `CUDAExtension` na skompilovanie `.cu` do `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, spúšťač a binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Prečo použiť `hipDeviceSynchronize()`? <br>
> - Spúšťanie kernelov na GPU je asynchrónne. Keď CPU spustí `add_one<<<grid_size, block_size>>>(data, n);`, okamžite pokračuje ďalšou inštrukciou bez čakania na GPU. `hipDeviceSynchronize()` prinúti CPU čakať, kým sa kernel na GPU nedokončí.

#### **Krok 2: Zostavenie**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento príkaz hľadá `setup.py` v aktuálnom adresári, aby zostavil vytvorený súbor .cu.


`CUDAExtension` je pomocník na zostavovanie CUDA z `torch.utils.cpp_extension`. S ROCm PyTorch **premapuje `CUDAExtension` tak, aby používal `hipcc`** namiesto `nvcc`. ROCm zachytí proces zostavovania a presmeruje ho cez HIP kompilátor, čím prenesie kód CUDA na AMD.

Toto vytvorí nasledujúce súbory:
<!-- @os:windows -->
- `build/`:  adresár so súbormi `.pyd`
- `add_one_kernel.hip`:  HIP zdrojový kód vygenerovaný „hipifikáciou“ súboru `.cu`; toto je to, čo skutočne skompiloval `hipcc`
<!-- @os:end -->

<!-- @os:linux -->
- `build/`:  adresár so súbormi `.so`
- `add_one_kernel.hip`:  HIP zdrojový kód vygenerovaný „hipifikáciou“ súboru `.cu`; toto je to, čo skutočne skompiloval `hipcc`
<!-- @os:end -->

#### **Krok 3: Použitie z Pythonu** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Spustite tento skript, aby ste videli kernel v akcii:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Očakávaný výstup:**
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

### Návod 2: Násobenie matíc

Násobenie matíc počíta **C = A × B**, kde:
- **A** má rozmer M×N (riadky × stĺpce)
- **B** má rozmer N×K  
- **C** má rozmer M×K (výsledok)

Každý výstupný prvok je definovaný ako:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Každý prvok matice C sa počíta nezávisle, čo je ideálne pre paralelizmus na GPU.

#### Ako sa to mapuje na vlákna GPU

Na rozdiel od sčítania vektorov (1D) produkuje násobenie matíc **2D výstup**, takže používame **2D mriežku vlákien**:

| | Sčítanie vektorov | Násobenie matíc |
|---|---|---|
| **Tvar výstupu** | 1D pole | 2D matica (M×K) |
| **Mapovanie vlákien** | 1 vlákno → 1 prvok | 1 vlákno → 1 výstupný prvok |
| **Vzor spustenia** | 1D mriežka: `(grid_x, 1, 1)` | 2D mriežka: `(grid_x, grid_y, 1)` |
| **Veľkosť bloku** | `(256, 1, 1)` | `(16, 16, 1)` = 256 vlákien |

Každé vlákno počíta jeden prvok výstupnej matice C. Vlákno na pozícii `(row, col)` počíta `C[row][col]` vynásobením zodpovedajúceho riadku A so zodpovedajúcim stĺpcom B.

**Rozloženie pamäte**: Pamäť GPU je plochá (1D), ale matice sú uložené po riadkoch. Na prístup k `A[row][col]` kernel používa `A[row * N + col]`.


#### Prístup A: JIT kompilácia:

Podobne ako v Návode 1, kernel je napísaný ako reťazec v surovom C++ vnútri Pythonu a skompilovaný za behu pomocou zabudovaného JIT v PyTorch.


Ak chcete použiť [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), uistite sa, že je stiahnutý, a spustite:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Kľúčové úryvky kódu**
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

Skript overuje výsledok voči `torch.mm` s malou toleranciou. Aritmetika s pohyblivou rádovou čiarkou na GPU môže produkovať malé číselné rozdiely v porovnaní s implementáciami na CPU kvôli poradiu paralelnej redukcie.

<!-- @os:linux -->
**Očakávaný výstup:**[Hodnoty výkonu sa budú líšiť]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Vo Windows nie je `amd-smi` podporovaný. Na sledovanie využitia GPU môžete použiť Správcu úloh, kde by ste mali vidieť krátky nárast využitia počas behu programu.

**Očakávaný výstup:**
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
#### Prístup B: Rozšírenie C++

Druhý prístup je manuálnejší: napíšte kernel a Python binding do jedného súboru `.cu`, skompilujte ho natívne pomocou build systému PyTorch a importujte ho do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Prístup C++ Extension vyžaduje build prostredie Visual Studio C++, pretože PyTorch kompiluje zdrojový súbor `.cu` do natívneho rozširujúceho modulu `.pyd`. Zostavenie tohto natívneho rozšírenia závisí od reťazca nástrojov Microsoft C++ (kompilátor, linker a build nástroje) poskytovaného Visual Studiom. Pred zostavením rozšírenia spustite aktivačné príkazy Visual Studio zo sekcie nastavenia.
<!-- @os:end -->

Stiahnite si nasledujúce súbory, ak ste tak ešte neurobili:
<!-- @os:windows -->
| Súbor | Úloha |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + spúšťač + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build skript, používa `CUDAExtension` na kompiláciu `.cu` do `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->
<!-- @os:linux -->
| Súbor | Úloha |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + spúšťač + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build skript, používa `CUDAExtension` na kompiláciu `.cu` do `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, spúšťač a binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

V porovnaní s `add_one_launcher` z Postupu 1 tento spúšťač:
- Prijíma dva vstupné tenzory namiesto jedného
- Odvodzuje všetky tri rozmery (M, N, K) z tvarov tenzorov, bez manuálneho odovzdávania veľkostí z Pythonu
- Alokuje a vracia výstupný tenzor C, namiesto úpravy na mieste
- Používa `dim3` pre grid aj block na vyjadrenie 2D tvaru spustenia

#### **Krok 2: Zostavenie**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento príkaz hľadá `setup.py` v aktuálnom adresári, aby zostavil súbor .cu, ktorý sme vytvorili.


Toto vytvorí nasledujúce súbory:
<!-- @os:windows -->
- `build/`:  adresár so súbormi `.pyd`
- `matmul_kernel.hip`:  HIP zdrojový kód vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo skutočne skompiloval `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  adresár so súbormi `.so`
- `matmul_kernel.hip`:  HIP zdrojový kód vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo skutočne skompiloval `hipcc`
<!-- @os:end -->

#### **Krok 3: Použitie z Pythonu** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Spustite tento skript, aby ste videli kernel v akcii:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Očakávaný výstup:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Skvelé! Práve ste implementovali násobenie matíc na GPU.** Toto je významný míľnik, pretože násobenie matíc je základom moderných operácií strojového učenia, ako sú:
- Vrstvy neurónových sietí
- Mechanizmy attention
- Embeddings
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

## Ďalšie kroky

Naučili ste sa písať, kompilovať a spúšťať GPU kernely pomocou JIT kompilácie aj rozšírení C++ pre základné paralelné operácie.

**Optimalizácie výkonu:**
- **Dláždenie so zdieľanou pamäťou (shared memory tiling)** - Ukladanie blokov dát do vyrovnávacej pamäte na zníženie prístupu ku globálnej pamäti
- **Zlučovanie prístupov do pamäte (memory coalescing)** - Optimalizácia vzorov prístupu do pamäte pre priepustnosť

**Reálne algoritmy:**
- **2D konvolúcia** - Malý filter (kernel) sa posúva cez obrázok a počíta každý výstupný pixel ako vážený súčet susedných pixelov. Toto zavádza stencil výpočty a dláždenie so zdieľanou pamäťou, kde vlákna opätovne využívajú prekrývajúce sa oblasti obrázka na zníženie prístupu ku globálnej pamäti.
- **Funkcia Softmax**: Softmax konvertuje vektor čísel na pravdepodobnosti, ktoré sa sčítajú na 1, bežne používané vo výstupoch neurónových sietí. Efektívna implementácia na GPU zavádza paralelné redukcie a techniky numerickej stability pri spracovaní veľkých vektorov.

**Úvahy pre produkčné nasadenie:**
- **Spracovanie chýb** - Kontrola hraníc a správa zariadení
- **Integrácia s PyTorch** - Vlastné operátory s podporou autograd