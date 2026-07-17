<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Napište GPU kernel od základu, zkompilujte ho, spusťte ho na AMD GPU a sledujte, jak stoupá využití. Tento playbook ukazuje, jak GPU výpočty skutečně fungují: napište kód kernelu a spusťte ho paralelně napříč tisíci vláken.

> **Poznámka**: Jedná se o poměrně složitý playbook, který může vyžadovat dodatečné ladění a úpravy.

## Co se naučíte

<!-- @os:windows -->
- Jak fungují GPU kernely: mřížky, bloky, vlákna a indexovací model, který je mapuje na data
- Jak AMD ROCm/HIP stack umožňuje psát kód ve stylu CUDA, který běží na AMD GPU bez úprav
- Jak zkompilovat kernel za běhu pomocí `torch.cuda._compile_kernel`
- Jak sestavit nativní C++ rozšíření kernelu pomocí `CUDAExtension` + pybind11, importovatelné z Pythonu
<!-- @os:end -->
<!-- @os:linux -->
- Jak fungují GPU kernely: mřížky, bloky, vlákna a indexovací model, který je mapuje na data
- Jak AMD ROCm/HIP stack umožňuje psát kód ve stylu CUDA, který běží na AMD GPU bez úprav
- Jak zkompilovat kernel za běhu pomocí `torch.cuda._compile_kernel`
- Jak sestavit nativní C++ rozšíření kernelu pomocí `CUDAExtension` + pybind11, importovatelné z Pythonu
- Jak měřit dobu provádění kernelu a sledovat živé využití GPU pomocí `amd-smi`
<!-- @os:end -->

---

Tento playbook pokrývá dva přístupy k vývoji kernelů:

<!-- @os:windows -->
| Přístup | Vstupní bod |
|---|---|
| **JIT kompilace** | `torch.cuda._compile_kernel`, napište kernel jako řetězec v Pythonu, bez kroku sestavení |
| **C++ rozšíření** | `CUDAExtension` + pybind11: zkompilujte soubor `.cu` do nativního `.pyd` a importujte ho |
<!-- @os:end -->
<!-- @os:linux -->
| Přístup | Vstupní bod |
|---|---|
| **JIT kompilace** | `torch.cuda._compile_kernel`, napište kernel jako řetězec v Pythonu, bez kroku sestavení |
| **C++ rozšíření** | `CUDAExtension` + pybind11: zkompilujte soubor `.cu` do nativního `.so` a importujte ho |
<!-- @os:end -->

Oba přístupy fungují na AMD GPU. Je to možné, protože ROCm sestavení PyTorch mapuje celý povrch CUDA API na HIP. To znamená, že `torch.cuda`, `CUDAExtension` a syntaxe CUDA kernelů fungují na AMD hardwaru transparentně.

---

## Pozadí

### Co je GPU kernel?

GPU kernel je funkce, která běží paralelně napříč tisíci GPU vlákny současně. Na rozdíl od CPU funkce, která se provede jednou za volání, je kernel spuštěn s **mřížkou** **bloků**, z nichž každý obsahuje mnoho **vláken**, přičemž všechna provádějí stejný kód na různých datech.

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

Tyto proměnné se kombinují pro výpočet globálně jedinečného indexu vlákna:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Celkový počet vláken = `gridDim.x * blockDim.x`. Každé vlákno zpracovává jeden prvek nezávisle. Toto je základ **datového paralelismu**. Stejná operace běží na mnoha prvcích najednou, bez závislosti mezi vlákny.

---

### Model provádění GPU: Wavefronty

AMD GPU provádějí vlákna ve skupinách po **32**, nazývaných **wavefronty**. Všechna vlákna ve wavefrontu provádějí stejnou instrukci současně. To ovlivňuje volbu optimální velikosti bloku (256 vláken = 8 wavefrontů = dobrá efektivita plánování).

### Programování AMD GPU: HIP + ROCm

**ROCm** je open-source stack pro GPU výpočty od AMD (ovladače, kompilátory, knihovny, runtime). **HIP** leží nad ním a je navržen tak, aby byl syntakticky identický s CUDA. ROCm sestavení PyTorch transparentně mapuje `torch.cuda.*` na HIP, takže stejný kód funguje na AMD GPU.

---

### PyTorch + AMD/HIP

PyTorch dodává ROCm sestavení, kde je povrch CUDA API (`torch.cuda.*`) transparentně podpořen HIPem. To znamená:

- `torch.cuda.is_available()` funguje na AMD GPU s ROCm
- `tensor.to("cuda")` alokuje na AMD GPU
- `torch.version.hip` zpřístupňuje verzi HIP

PyTorch také zpřístupňuje `torch.cuda._compile_kernel()`, vysokoúrovňovou zkratku pro JIT kompilaci surového řetězce kernelu a získání volatelného objektu zpět, bez nutnosti samostatného kroku sestavení.

---

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Předpoklady – Windows
- Nainstalujte nejnovější verzi: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv s již nainstalovaným ROCm+PyTorch.
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
**Udělte svému uživateli přístup k GPU zařízením** (pro aktivaci se odhlaste a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
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
Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Uživatelé Windows mohou před spuštěním některých příkazů PowerShell potřebovat upravit zásady spouštění PowerShellu (např.
> nastavit je na RemoteSigned nebo Unrestricted).

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
> **Poznámka:** Pro tento návod musí být ROCm a PyTorch nainstalovány do virtuálního prostředí i na Ryzen AI Halo, protože kompilace vlastních jader vyžaduje úplné vývojové hlavičky.

Instalace ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Instalace PyTorch:
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
Nainstalujte linuxový sestavovací řetězec C/C++. Jedná se o závislost na úrovni systému, která je vyžadována pro návody s rozšířeními C++, protože `CUDAExtension` sestavuje nativní moduly `.so` ze souborů `.cu`.

Spusťte tento příkaz jednou na linuxovém počítači, mimo vytvořené virtuální prostředí Pythonu:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktivaci virtuálního prostředí `kernel-env` nainstalujte závislosti pro sestavení Pythonu:
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
Ujistěte se, že je nainstalováno [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) nebo [novější verze](https://visualstudio.microsoft.com/vs/community/) s úlohou **Vývoj desktopových aplikací v C++**.

> **Poznámka**: Nastavení prostředí Visual Studio C++ je vyžadováno pouze pro přístup **Rozšíření C++**. Pro přístup JIT Compilation není vyžadováno.

Otevřete terminál PowerShell a před sestavením rozšíření C++ spusťte následující příkazy.

**Krok 1: Nalezení nainstalovaného prostředí Visual Studio C++**

**(A) Vyhledejte `vswhere.exe`, který je nainstalován spolu s instalačním programem Visual Studio**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Vyhledejte `vcvars64.bat` z Visual Studio 2022 nebo novějšího s nástroji pro sestavení C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Zobrazte používané prostředí Visual Studio C++**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Krok 2: Aktivace sestavovacího prostředí Visual Studio C++**

**(A) Spusťte `vcvars64.bat` a zachyťte prostředí, které nastaví**

Tím zpřístupníte `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` a cesty k Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importujte proměnné prostředí Visual Studio do této relace PowerShell**

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
Ověřte, že je AMD GPU viditelná, pomocí:
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

## Stažení požadovaných souborů

Vytvořte následující adresářovou strukturu vytvořením **2 nových složek** a stažením příslušných souborů:

| Adresář | Soubory ke stažení | Popis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Soubory JIT a rozšíření C++ pro jádro vektorového sčítání |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Soubory JIT a rozšíření C++ pro jádro maticového násobení |


## Návody

### Návod 1: Vektorové sčítání

#### Přístup A: JIT Compilation

JIT (Just-In-Time) kompilace znamená, že jádro je zapsáno jako řetězec surového C++ uvnitř Pythonu a zkompilováno za běhu, bez nutnosti dalších kroků sestavení.

Chcete-li použít [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), ujistěte se, že je stažen, a spusťte:
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
> **Tip**: Skript také spouští vlákno na pozadí, které každých 100 ms dotazuje `amd-smi` a zaznamenává špičkové a průměrné využití GPU během běhu jádra.
<!-- @os:end -->

> **Poznámka**: **Proč je velikost bloku 256?** <br>
> - Jádro používá **256 vláken na blok**, protože to dobře odpovídá **modelu vlnového provádění AMD GPU**.
> - Připomeňme, že hardware AMD provádí vlákna ve skupinách po 32 vláknech, což vede k 8 wavefrontům na blok. (8 wavefrontů × 32 vláken = 1 blok)


**Co úloha dělá:**

Jádro uměle přidává extra práci, aby demonstrovalo využití GPU:

- **100 000 000 prvků** v tensoru
- **Vnitřní smyčka běží 1 000krát** na prvek na spuštění jádra  
- **200 spuštění jádra** celkem

**Matematika:**  
- Každý prvek: je inkrementován o 1 × 1 000 iterací × 200 spuštění = 200 000  
- Výsledek: 1,0 (počáteční hodnota) + 200 000 (sčítání) = 200 001,0

**Proč vnitřní smyčka?**  
- Bez smyčky `for (int i = 0; i < 1000; i++)` by 200 spuštění skončilo okamžitě a monitorovací nástroje by nezachytily smysluplné využití GPU. Umělá práce zajišťuje, že každé spuštění jádra trvá dostatečně dlouho, aby monitorovací nástroje mohly měřit výkon.

<!-- @os:linux -->
**Očekávaný výstup:** [Výsledky výkonu se mohou lišit]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Ve Windows není `amd-smi` podporováno. Pro sledování využití GPU můžete použít Správce úloh, kde byste při spuštění programu měli vidět krátký nárůst využití.

**Očekávaný výstup:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Výborně! Právě jste spustili své první jádro GPU.**

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
#### Přístup B: Rozšíření C++

Druhý přístup je více manuální: napište kernel a Python binding do jednoho souboru `.cu`, zkompilujte jej nativně pomocí sestavovacího systému PyTorch a importujte do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Přístup s rozšířením C++ vyžaduje sestavovací prostředí Visual Studio C++, protože PyTorch kompiluje zdrojový soubor `.cu` do nativního rozšiřujícího modulu `.pyd`. Sestavení tohoto nativního rozšíření závisí na nástrojovém řetězci Microsoft C++ (kompilátor, linker a sestavovací nástroje) poskytovaném Visual Studiem. Před sestavením rozšíření spusťte aktivační příkazy Visual Studia z části nastavení.
<!-- @os:end -->

Pokud jste tak ještě neučinili, stáhněte si následující soubory:
<!-- @os:windows -->
| Soubor | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, vše v jednom souboru |
| [setup.py](assets/Vector_Addition/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci `.cu` do `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

<!-- @os:linux -->
| Soubor | Role |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding, vše v jednom souboru |
| [setup.py](assets/Vector_Addition/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci `.cu` do `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, launcher a binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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
> - Spouštění GPU kernelů je asynchronní. Když CPU spustí `add_one<<<grid_size, block_size>>>(data, n);`, okamžitě by provedlo další instrukci bez čekání na GPU. `hipDeviceSynchronize()` nutí CPU čekat, dokud GPU kernel nedokončí svou práci.

#### **Krok 2: Sestavení**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento příkaz hledá `setup.py` v aktuálním adresáři pro sestavení souboru .cu, který jsme vytvořili.


`CUDAExtension` je pomocník pro sestavení CUDA z `torch.utils.cpp_extension`. S ROCm PyTorch **přemapuje `CUDAExtension` na použití `hipcc`** místo `nvcc`. ROCm zachytí cestu sestavení a přesměruje ji přes kompilátor HIP, čímž portuje kód CUDA na AMD.

Výsledkem jsou následující soubory:
<!-- @os:windows -->
- `build/`: adresář se soubory `.pyd`
- `add_one_kernel.hip`: zdrojový soubor HIP vygenerovaný hipifikací souboru `.cu`; to je to, co `hipcc` skutečně zkompiloval
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: adresář se soubory `.so`
- `add_one_kernel.hip`: zdrojový soubor HIP vygenerovaný hipifikací souboru `.cu`; to je to, co `hipcc` skutečně zkompiloval
<!-- @os:end -->

#### **Krok 3: Použití z Pythonu** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Spusťte tento skript, abyste viděli kernel v akci:
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

### Průvodce 2: Maticové násobení

Maticové násobení vypočítá **C = A × B**, kde:
- **A** je M×N (řádky × sloupce)
- **B** je N×K  
- **C** je M×K (výsledek)

Každý výstupní prvek je definován jako:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Každý prvek C je vypočítán nezávisle, což z toho dělá ideální úlohu pro paralelismus GPU.

#### Jak se to mapuje na vlákna GPU

Na rozdíl od vektorového sčítání (1D) produkuje maticové násobení **2D výstup**, proto používáme **2D mřížku vláken**:

| | Vektorové sčítání | Maticové násobení |
|---|---|---|
| **Tvar výstupu** | 1D pole | 2D matice (M×K) |
| **Mapování vláken** | 1 vlákno → 1 prvek | 1 vlákno → 1 výstupní prvek |
| **Vzor spuštění** | 1D mřížka: `(grid_x, 1, 1)` | 2D mřížka: `(grid_x, grid_y, 1)` |
| **Velikost bloku** | `(256, 1, 1)` | `(16, 16, 1)` = 256 vláken |

Každé vlákno vypočítá jeden prvek výstupní matice C. Vlákno na pozici `(row, col)` vypočítá `C[row][col]` vynásobením odpovídajícího řádku A s odpovídajícím sloupcem B.

**Rozložení paměti**: Paměť GPU je plochá (1D), ale matice jsou uloženy řádek po řádku. Pro přístup k `A[row][col]` kernel používá `A[row * N + col]`.


#### Přístup A: JIT kompilace:

Stejně jako v Průvodci 1 je kernel napsán jako řetězec surového C++ uvnitř Pythonu a kompilován za běhu prostřednictvím vestavěného JIT PyTorch.


Chcete-li použít [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), ujistěte se, že je stažen, a spusťte:
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

Skript ověřuje výsledek oproti `torch.mm` s malou tolerancí. Aritmetika s plovoucí desetinnou čárkou na GPU může produkovat malé numerické rozdíly ve srovnání s implementacemi na CPU kvůli pořadí paralelní redukce.

<!-- @os:linux -->
**Očekávaný výstup:** [Výkonnostní čísla se budou lišit]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: V systému Windows není `amd-smi` podporováno. Pro sledování využití GPU můžete použít Správce úloh, kde byste měli vidět krátký nárůst využití při spuštění programu.

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
#### Přístup B: Rozšíření C++

Druhý přístup je více manuální: napište kernel a Python binding do jednoho souboru `.cu`, zkompilujte ho nativně pomocí sestavovacího systému PyTorch a importujte ho do Pythonu.

<!-- @os:windows -->
> **Poznámka**: Přístup s rozšířením C++ vyžaduje sestavovací prostředí Visual Studio C++, protože PyTorch kompiluje zdrojový soubor `.cu` do nativního rozšiřujícího modulu `.pyd`. Sestavení tohoto nativního rozšíření závisí na nástrojovém řetězci Microsoft C++ (kompilátor, linker a sestavovací nástroje) poskytovaném sadou Visual Studio. Před sestavením rozšíření spusťte aktivační příkazy Visual Studio z části nastavení.
<!-- @os:end -->

Pokud jste tak ještě neučinili, stáhněte si následující soubory:
<!-- @os:windows -->
| Soubor | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci `.cu` do `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->
<!-- @os:linux -->
| Soubor | Role |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Sestavovací skript, používá `CUDAExtension` ke kompilaci `.cu` do `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, který spouští sestavené artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, launcher a binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Ve srovnání s `add_one_launcher` z průvodce 1 launcher zde:
- Přijímá dva vstupní tensory místo jednoho
- Odvozuje všechny tři dimenze (M, N, K) z tvarů tensorů, bez ručního předávání velikosti z Pythonu
- Alokuje a vrací výstupní tensor C, místo aby prováděl úpravy na místě
- Používá `dim3` pro grid i blok k vyjádření 2D tvaru spuštění

#### **Krok 2: Sestavení**
```bash
pip install --no-build-isolation -v .
```
>**Poznámka**: Tento příkaz hledá `setup.py` v aktuálním adresáři pro sestavení souboru .cu, který jsme vytvořili.


Výsledkem jsou následující soubory:
<!-- @os:windows -->
- `build/`: adresář se soubory `.pyd`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikací souboru `.cu`; to je to, co `hipcc` skutečně zkompiloval
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: adresář se soubory `.so`
- `matmul_kernel.hip`: zdrojový kód HIP vygenerovaný hipifikací souboru `.cu`; to je to, co `hipcc` skutečně zkompiloval
<!-- @os:end -->

#### **Krok 3: Použití z Pythonu** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Spusťte tento skript, abyste viděli kernel v akci:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Očekávaný výstup:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Skvěle! Právě jste implementovali násobení matic na GPU.** Toto je důležitý milník, protože násobení matic je základem moderních operací strojového učení, jako jsou:
- Vrstvy neuronových sítí
- Mechanismy pozornosti (attention)
- Embeddingy
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

Naučili jste se psát, kompilovat a spouštět GPU kernely pomocí JIT kompilace i rozšíření C++ pro základní paralelní operace.

**Optimalizace výkonu:**
- **Tiling sdílené paměti** – Ukládání bloků dat do mezipaměti pro snížení přístupu ke globální paměti
- **Koalescence paměti** – Optimalizace vzorů přístupu k paměti pro šířku pásma

**Algoritmy z reálného světa:**
- **2D konvoluce** – Malý filtr (kernel) se posouvá přes obrázek a pro každý výstupní pixel vypočítá vážený součet sousedních pixelů. Tím se zavádějí výpočty stencil a tiling sdílené paměti, kde vlákna znovu využívají překrývající se oblasti obrázku ke snížení přístupu ke globální paměti.
- **Funkce Softmax**: Softmax převádí vektor čísel na pravděpodobnosti, jejichž součet je 1, a běžně se používá na výstupech neuronových sítí. Efektivní implementace na GPU zavádí paralelní redukce a techniky numerické stability při zpracování velkých vektorů.

**Aspekty produkčního nasazení:**
- **Ošetření chyb** – Kontrola hranic a správa zařízení
- **Integrace s PyTorch** – Vlastní operátory s podporou autograd