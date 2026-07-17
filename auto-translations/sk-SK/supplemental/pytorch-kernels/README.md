<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

Napíšte GPU kernel od základu, skompilujte ho, spustite na AMD GPU a sledujte, ako stúpa využitie. Tento playbook ukazuje, ako GPU výpočty skutočne fungujú: napíšte kód kernelu a spustite ho paralelne naprieč tisíckami vlákien.

> **Poznámka**: Toto je pomerne zložitý playbook, ktorý môže vyžadovať dodatočné ladenie a úpravy.

## Čo sa naučíte

<!-- @os:windows -->
- Ako fungujú GPU kernely: mriežky, bloky, vlákna a indexovací model, ktorý ich mapuje na dáta
- Ako zásobník AMD ROCm/HIP umožňuje písať kód v štýle CUDA, ktorý beží na AMD GPU bez úprav
- Ako skompilovať kernel za behu pomocou `torch.cuda._compile_kernel`
- Ako zostaviť natívne rozšírenie C++ kernelu pomocou `CUDAExtension` + pybind11, importovateľné z Pythonu
<!-- @os:end -->
<!-- @os:linux -->
- Ako fungujú GPU kernely: mriežky, bloky, vlákna a indexovací model, ktorý ich mapuje na dáta
- Ako zásobník AMD ROCm/HIP umožňuje písať kód v štýle CUDA, ktorý beží na AMD GPU bez úprav
- Ako skompilovať kernel za behu pomocou `torch.cuda._compile_kernel`
- Ako zostaviť natívne rozšírenie C++ kernelu pomocou `CUDAExtension` + pybind11, importovateľné z Pythonu
- Ako merať čas vykonávania kernelu a sledovať živé využitie GPU pomocou `amd-smi`
<!-- @os:end -->

---

Tento playbook pokrýva dva prístupy k vývoju kernelov:

<!-- @os:windows -->
| Prístup | Vstupný bod |
|---|---|
| **JIT kompilácia** | `torch.cuda._compile_kernel`, napíšte kernel ako reťazec v Pythone, bez kroku zostavenia |
| **Rozšírenie C++** | `CUDAExtension` + pybind11: skompilujte súbor `.cu` do natívneho `.pyd` a importujte ho |
<!-- @os:end -->
<!-- @os:linux -->
| Prístup | Vstupný bod |
|---|---|
| **JIT kompilácia** | `torch.cuda._compile_kernel`, napíšte kernel ako reťazec v Pythone, bez kroku zostavenia |
| **Rozšírenie C++** | `CUDAExtension` + pybind11: skompilujte súbor `.cu` do natívneho `.so` a importujte ho |
<!-- @os:end -->

Oba prístupy fungujú na AMD GPU. Je to možné, pretože ROCm build PyTorch mapuje celý povrch CUDA API na HIP. To znamená, že `torch.cuda`, `CUDAExtension` a syntax CUDA kernelov fungujú na AMD hardvéri transparentne.

---

## Pozadie

### Čo je GPU kernel?

GPU kernel je funkcia, ktorá beží paralelne naprieč tisíckami GPU vlákien súčasne. Na rozdiel od funkcie CPU, ktorá sa vykoná raz za volanie, kernel sa spúšťa s **mriežkou** **blokov**, pričom každý obsahuje mnoho **vlákien**, ktoré všetky vykonávajú rovnaký kód na rôznych dátach.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indexovania vlákien

Pri spúšťaní kernelu zadávate dve dimenzie:

| Premenná | Význam |
|---|---|
| `gridDim` | Počet blokov v mriežke |
| `blockDim` | Počet vlákien na blok |

Každé vlákno má prístup k trom vstavaným premenným len na čítanie:

| Premenná | Význam |
|---|---|
| `blockIdx.x` | Ku ktorému bloku toto vlákno patrí |
| `blockDim.x` | Počet vlákien v jednom bloku |
| `threadIdx.x` | Index vlákna v rámci jeho bloku |

### Globálne ID vlákna

Tieto premenné sa kombinujú na výpočet globálne jedinečného indexu vlákna:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Celkový počet vlákien = `gridDim.x * blockDim.x`. Každé vlákno spracúva jeden prvok nezávisle. Toto je základ **dátového paralelizmu**. Rovnaká operácia beží na mnohých prvkoch naraz, bez závislosti medzi vláknami.

---

### Model vykonávania GPU: Wavefronty

AMD GPU vykonávajú vlákna v skupinách po **32**, nazývaných **wavefronty**. Všetky vlákna vo wavefrontе vykonávajú rovnakú inštrukciu súčasne. To ovplyvňuje optimálne voľby veľkosti bloku (256 vlákien = 8 wavefrontov = dobrá efektivita plánovania).

### Programovanie AMD GPU: HIP + ROCm

**ROCm** je open-source zásobník GPU výpočtov od AMD (ovládače, kompilátory, knižnice, runtime). **HIP** je postavený na vrchu, navrhnutý tak, aby bol syntakticky identický s CUDA. ROCm build PyTorch transparentne mapuje `torch.cuda.*` na HIP, takže rovnaký kód funguje na AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch dodáva ROCm build, kde je povrch CUDA API (`torch.cuda.*`) transparentne podporovaný HIP. To znamená:

- `torch.cuda.is_available()` funguje na AMD GPU s ROCm
- `tensor.to("cuda")` alokuje na AMD GPU
- `torch.version.hip` sprístupňuje verziu HIP

PyTorch tiež sprístupňuje `torch.cuda._compile_kernel()`, vysokoúrovňovú skratku na JIT-kompiláciu surového reťazca kernelu a získanie volateľného objektu späť, bez potreby samostatného kroku zostavenia.

---

<!-- @device:halo_box -->
## Skontrolujte aktualizácie softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Predpoklady – Windows
- Nainštalujte najnovší: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linuxe otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+PyTorch.
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linuxe otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
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
Na Windows otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Používatelia Windows môžu pred spustením niektorých príkazov PowerShell potrebovať upraviť politiku vykonávania PowerShell (napr.
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
> **Poznámka:** Pre tento návod je potrebné nainštalovať ROCm a PyTorch do virtuálneho prostredia aj na Ryzen AI Halo, pretože kompilácia vlastných jadier vyžaduje úplné vývojové hlavičky.

Inštalácia ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Inštalácia PyTorch:
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
Nainštalujte zostavovací reťazec Linux C/C++. Ide o závislosť na úrovni systému, ktorá je potrebná pre návody s rozšíreniami C++, pretože `CUDAExtension` zostavuje natívne moduly `.so` zo súborov `.cu`.

Spustite toto raz na linuxovom počítači, mimo vytvoreného virtuálneho prostredia Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktivácii virtuálneho prostredia `kernel-env` nainštalujte závislosti zostavenia pre Python:
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
Uistite sa, že je nainštalované [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) alebo [novšia verzia](https://visualstudio.microsoft.com/vs/community/) s pracovnou záťažou **Vývoj desktopových aplikácií v C++**.

> **Poznámka**: Toto nastavenie prostredia Visual Studio C++ je potrebné iba pre prístup **C++ Extension**. Pre prístup JIT Compilation nie je potrebné.

Otvorte terminál PowerShell a pred zostavením rozšírenia C++ spustite nasledujúce príkazy.

**Krok 1: Nájdite nainštalované prostredie Visual Studio C++**

**(A) Nájdite `vswhere.exe`, ktorý je nainštalovaný spolu s inštalátorom Visual Studio**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Nájdite `vcvars64.bat` z Visual Studio 2022 alebo novšieho s nástrojmi na zostavenie C++**

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

**Krok 2: Aktivujte zostavovacie prostredie Visual Studio C++**

**(A) Spustite `vcvars64.bat` a zachyťte prostredie, ktoré nastaví**

Tým sprístupníte `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` a cesty Windows SDK.

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

**Krok 3: Overte, že je dostupný kompilátor Microsoft C++**

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
Overte, že je AMD GPU viditeľná pomocou:
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

## Stiahnutie požadovaných súborov

Vytvorte nasledujúcu adresárovú štruktúru vytvorením **2 nových priečinkov** a stiahnutím zodpovedajúcich súborov:

| Adresár | Súbory na stiahnutie | Popis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Súbory JIT a rozšírenia C++ pre jadro vektorového sčítania |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Súbory JIT a rozšírenia C++ pre jadro násobenia matíc |


## Návody

### Návod 1: Vektorové sčítanie

#### Prístup A: JIT kompilácia

JIT (Just-In-Time) kompilácia znamená, že jadro je napísané ako surový reťazec C++ vo vnútri Pythonu a kompiluje sa za behu, bez potreby ďalších krokov zostavenia.

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
> **Tip**: Skript tiež spúšťa vlákno na pozadí, ktoré každých 100 ms dotazuje `amd-smi` a zaznamenáva maximálne a priemerné využitie GPU počas behu jadra.
<!-- @os:end -->

> **Poznámka**: **Prečo je veľkosť bloku 256?** <br>
> - Jadro používa **256 vlákien na blok**, pretože to dobre zodpovedá **modelu vlnovej fronty vykonávania AMD GPU**.
> - Pripomeňme, že AMD hardvér vykonáva vlákna v skupinách po 32 vlákien, čo vedie k 8 vlnovým frontám na blok. (8 vlnových front × 32 vlákien = 1 blok)


**Čo pracovná záťaž robí:**

Jadro umelo pridáva ďalšiu prácu, aby demonštrovalo využitie GPU:

- **100 000 000 prvkov** v tenzore
- **Vnútorná slučka beží 1 000-krát** na prvok na každé spustenie jadra
- **200 spustení jadra** celkovo

**Matematika:**  
- Každý prvok: je zvýšený o 1 × 1 000 iterácií × 200 spustení = 200 000  
- Konečný výsledok: 1,0 (počiatočná hodnota) + 200 000 (sčítaní) = 200 001,0

**Prečo vnútorná slučka?**  
- Bez slučky `for (int i = 0; i < 1000; i++)` by sa 200 spustení dokončilo okamžite a monitorovacie nástroje by nezachytili zmysluplné využitie GPU. Umelá práca spôsobuje, že každý beh jadra trvá dostatočne dlho na to, aby monitorovacie nástroje mohli merať výkon.

<!-- @os:linux -->
**Očakávaný výstup:** [Výsledky výkonu sa môžu líšiť]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: V systéme Windows nie je `amd-smi` podporovaný. Na sledovanie využitia GPU môžete použiť Správcu úloh, kde by ste mali vidieť krátky nárast využitia pri spustení programu.

**Očakávaný výstup:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Výborne! Práve ste spustili svoje prvé jadro GPU.**

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
#### Prístup B: Rozšírenie C++

Druhý prístup je manuálnejší: napíšte kernel a väzbu Pythonu do jedného súboru `.cu`, skompilujte ho natívne pomocou systému zostavenia PyTorch a importujte ho do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Prístup s rozšírením C++ vyžaduje prostredie zostavenia Visual Studio C++, pretože PyTorch kompiluje zdrojový súbor `.cu` do natívneho rozširujúceho modulu `.pyd`. Zostavenie tohto natívneho rozšírenia závisí od nástrojového reťazca Microsoft C++ (kompilátor, linker a nástroje zostavenia) poskytovaného Visual Studio. Pred zostavením rozšírenia spustite aktivačné príkazy Visual Studio z časti nastavenia.
<!-- @os:end -->

Ak ste tak ešte neurobili, stiahnite nasledujúce súbory:
<!-- @os:windows -->
| Súbor | Úloha |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + spúšťač + väzba pybind11, všetko v jednom súbore |
| [setup.py](assets/Vector_Addition/setup.py) | Skript zostavenia, používa `CUDAExtension` na kompiláciu `.cu` do `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Skript Pythonu, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

<!-- @os:linux -->
| Súbor | Úloha |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + spúšťač + väzba pybind11, všetko v jednom súbore |
| [setup.py](assets/Vector_Addition/setup.py) | Skript zostavenia, používa `CUDAExtension` na kompiláciu `.cu` do `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Skript Pythonu, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, spúšťač a väzba** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Prečo používať `hipDeviceSynchronize()`? <br>
> - Spustenia kernelu GPU sú asynchrónne. Keď CPU spustí `add_one<<<grid_size, block_size>>>(data, n);`, okamžite by vykonalo ďalšiu inštrukciu bez čakania na GPU. `hipDeviceSynchronize()` núti CPU čakať, kým kernel GPU nedokončí svoju prácu.

#### **Krok 2: Zostavenie**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento príkaz hľadá `setup.py` v aktuálnom adresári na zostavenie súboru .cu, ktorý sme vytvorili.


`CUDAExtension` je pomocník zostavenia CUDA z `torch.utils.cpp_extension`. S ROCm PyTorch **presmeruje `CUDAExtension` na použitie `hipcc`** namiesto `nvcc`. ROCm zachytí cestu zostavenia a presmeruje ju cez kompilátor HIP, čím portuje kód CUDA na AMD.

Výsledkom sú nasledujúce súbory:
<!-- @os:windows -->
- `build/`: adresár so súbormi `.pyd`
- `add_one_kernel.hip`: zdroj HIP vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo `hipcc` skutočne skompiloval
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: adresár so súbormi `.so`
- `add_one_kernel.hip`: zdroj HIP vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo `hipcc` skutočne skompiloval
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

Násobenie matíc vypočíta **C = A × B**, kde:
- **A** je M×N (riadky × stĺpce)
- **B** je N×K  
- **C** je M×K (výsledok)

Každý výstupný prvok je definovaný ako:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Každý prvok C sa vypočítava nezávisle, čo z toho robí ideálny prípad pre paralelizmus GPU.

#### Ako sa to mapuje na vlákna GPU

Na rozdiel od vektorového sčítania (1D) násobenie matíc produkuje **2D výstup**, preto používame **2D mriežku vlákien**:

| | Vektorové sčítanie | Násobenie matíc |
|---|---|---|
| **Tvar výstupu** | 1D pole | 2D matica (M×K) |
| **Mapovanie vlákien** | 1 vlákno → 1 prvok | 1 vlákno → 1 výstupný prvok |
| **Vzor spustenia** | 1D mriežka: `(grid_x, 1, 1)` | 2D mriežka: `(grid_x, grid_y, 1)` |
| **Veľkosť bloku** | `(256, 1, 1)` | `(16, 16, 1)` = 256 vlákien |

Každé vlákno vypočíta jeden prvok výstupnej matice C. Vlákno na pozícii `(row, col)` vypočíta `C[row][col]` vynásobením zodpovedajúceho riadku A so zodpovedajúcim stĺpcom B.

**Rozloženie pamäte**: Pamäť GPU je plochá (1D), ale matice sú uložené riadok po riadku. Na prístup k `A[row][col]` kernel používa `A[row * N + col]`.


#### Prístup A: JIT kompilácia:

Rovnako ako v návode 1, kernel je napísaný ako surový reťazec C++ vo vnútri Pythonu a kompilovaný za behu prostredníctvom vstavaného JIT PyTorch.


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

Skript overuje výsledok oproti `torch.mm` s malou toleranciou. Aritmetika s pohyblivou rádovou čiarkou na GPU môže produkovať malé číselné rozdiely v porovnaní s implementáciami CPU z dôvodu poradia paralelnej redukcie.

<!-- @os:linux -->
**Očakávaný výstup:** [Výkonnostné čísla sa budú líšiť]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: V systéme Windows nie je `amd-smi` podporovaný. Na sledovanie využitia GPU môžete použiť Správcu úloh, kde by ste mali vidieť krátky nárast využitia pri spustení programu.

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

Druhý prístup je manuálnejší: napíšte kernel a väzbu Pythonu do jedného súboru `.cu`, skompilujte ho natívne pomocou systému zostavenia PyTorch a importujte ho do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Prístup s rozšírením C++ vyžaduje prostredie zostavenia Visual Studio C++, pretože PyTorch kompiluje zdrojový súbor `.cu` do natívneho rozšírovacieho modulu `.pyd`. Zostavenie tohto natívneho rozšírenia závisí od nástrojového reťazca Microsoft C++ (kompilátor, linker a nástroje zostavenia) poskytovaného Visual Studio. Pred zostavením rozšírenia spustite aktivačné príkazy Visual Studio z časti nastavenia.
<!-- @os:end -->

Ak ste tak ešte neurobili, stiahnite si nasledujúce súbory:
<!-- @os:windows -->
| Súbor | Úloha |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + spúšťač + väzba pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Skript zostavenia, používa `CUDAExtension` na kompiláciu `.cu` do `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Skript Pythonu, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->
<!-- @os:linux -->
| Súbor | Úloha |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + spúšťač + väzba pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Skript zostavenia, používa `CUDAExtension` na kompiláciu `.cu` do `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Skript Pythonu, ktorý spúšťa zostavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, spúšťač a väzba** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

V porovnaní s `add_one_launcher` v Návode 1 spúšťač tu:
- Prijíma dva vstupné tenzory namiesto jedného
- Odvodzuje všetky tri rozmery (M, N, K) z tvarov tenzorov, bez manuálneho odovzdávania veľkosti z Pythonu
- Alokuje a vracia výstupný tenzor C namiesto mutácie na mieste
- Používa `dim3` pre sieť aj blok na vyjadrenie 2D tvaru spustenia

#### **Krok 2: Zostavenie**
```bash
pip install --no-build-isolation -v .
```
> **Poznámka**: Tento príkaz hľadá `setup.py` v aktuálnom adresári na zostavenie súboru .cu, ktorý sme vytvorili.


Výsledkom sú nasledujúce súbory:
<!-- @os:windows -->
- `build/`: adresár so súbormi `.pyd`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo `hipcc` skutočne skompiloval
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: adresár so súbormi `.so`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikáciou súboru `.cu`; toto je to, čo `hipcc` skutočne skompiloval
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

**Skvelé! Práve ste implementovali násobenie matíc na GPU.** Toto je dôležitý míľnik, pretože násobenie matíc je základom moderných operácií strojového učenia, ako sú:
- Vrstvy neurónových sietí
- Mechanizmy pozornosti
- Vkladania (Embeddings)
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
- **Dláždenie zdieľanou pamäťou** – Ukladanie blokov dát do vyrovnávacej pamäte na zníženie prístupu ku globálnej pamäti
- **Koalescencia pamäte** – Optimalizácia vzorcov prístupu k pamäti pre šírku pásma

**Algoritmy zo skutočného sveta:**
- **2D konvolúcia** – Malý filter (kernel) sa posúva po obrázku a vypočítava každý výstupný pixel z váženého súčtu susedných pixelov. Toto zavádza výpočty šablóny a dláždenie zdieľanou pamäťou, kde vlákna opätovne využívajú prekrývajúce sa oblasti obrázka na zníženie prístupu ku globálnej pamäti.
- **Funkcia Softmax**: Softmax konvertuje vektor čísel na pravdepodobnosti, ktorých súčet je 1, bežne používané vo výstupoch neurónových sietí. Jej efektívna implementácia na GPU zavádza paralelné redukcie a techniky numerickej stability pri spracovaní veľkých vektorov.

**Aspekty produkčného nasadenia:**
- **Spracovanie chýb** – Kontrola hraníc a správa zariadení
- **Integrácia PyTorch** – Vlastné operátory s podporou autograd