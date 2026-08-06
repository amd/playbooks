<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

Skriv en GPU-kärna från grunden, kompilera den, kör den på en AMD-GPU och se hur användningen skjuter i höjden. Denna handbok visar hur GPU-beräkningar faktiskt fungerar: skriv kärnkoden och kör den parallellt över tusentals trådar.

> **Obs**: Detta är en ganska komplex handbok, som kan kräva viss extra felsökning och modifiering.

## Vad du kommer att lära dig

<!-- @os:windows -->
- Hur GPU-kärnor fungerar: rutnät, block, trådar och indexeringsmodellen som mappar dem till data
- Hur AMD:s ROCm/HIP-stack låter dig skriva CUDA-liknande kod som körs på AMD-GPU:er utan modifiering
- Hur du kompilerar en kärna vid körning med `torch.cuda._compile_kernel`
- Hur du bygger ett inbyggt C++-kärnstillägg med `CUDAExtension` + pybind11, som kan importeras från Python
<!-- @os:end -->
<!-- @os:linux -->
- Hur GPU-kärnor fungerar: rutnät, block, trådar och indexeringsmodellen som mappar dem till data
- Hur AMD:s ROCm/HIP-stack låter dig skriva CUDA-liknande kod som körs på AMD-GPU:er utan modifiering
- Hur du kompilerar en kärna vid körning med `torch.cuda._compile_kernel`
- Hur du bygger ett inbyggt C++-kärnstillägg med `CUDAExtension` + pybind11, som kan importeras från Python
- Hur du mäter kärnans exekveringstid och övervakar GPU-användning i realtid med `amd-smi`
<!-- @os:end -->

---

Denna handbok täcker två metoder för kärnutveckling:

<!-- @os:windows -->
| Metod | Startpunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kärna som en Python-sträng, utan byggsteg |
| **C++-tillägg** | `CUDAExtension` + pybind11: kompilera en `.cu`-fil till en inbyggd `.pyd` och importera den |
<!-- @os:end -->
<!-- @os:linux -->
| Metod | Startpunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kärna som en Python-sträng, utan byggsteg |
| **C++-tillägg** | `CUDAExtension` + pybind11: kompilera en `.cu`-fil till en inbyggd `.so` och importera den |
<!-- @os:end -->

Båda metoderna körs på AMD-GPU:er. Detta är möjligt eftersom PyTorchs ROCm-bygge mappar hela CUDA API-ytan till HIP. Det innebär att `torch.cuda`, `CUDAExtension` och CUDA-kärnsyntax alla fungerar transparent på AMD-hårdvara.

---

## Bakgrund

### Vad är en GPU-kärna?

En GPU-kärna är en funktion som körs parallellt över tusentals GPU-trådar samtidigt. Till skillnad från en CPU-funktion som exekveras en gång per anrop, startas en kärna med ett **rutnät** (grid) av **block**, där varje block innehåller många **trådar**, som alla kör samma kod på olika data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Trådindexeringsmodell

När du startar en kärna anger du två dimensioner:

| Variabel | Betydelse |
|---|---|
| `gridDim` | Antal block i rutnätet |
| `blockDim` | Antal trådar per block |

Varje tråd har tillgång till tre inbyggda skrivskyddade variabler:

| Variabel | Betydelse |
|---|---|
| `blockIdx.x` | Vilket block denna tråd tillhör |
| `blockDim.x` | Antal trådar i ett block |
| `threadIdx.x` | Trådindex inom sitt block |

### Globalt tråd-ID

Dessa variabler kombineras för att beräkna ett globalt unikt trådindex:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Totalt antal trådar = `gridDim.x * blockDim.x`. Varje tråd bearbetar ett element oberoende av de andra. Detta är grunden för **dataparallellism**. Samma operation körs på många element samtidigt, utan beroenden mellan trådarna.

---

### GPU-exekveringsmodell: Wavefronts

AMD-GPU:er exekverar trådar i grupper om **32** som kallas **wavefronts**. Alla trådar i en wavefront kör samma instruktion samtidigt. Detta påverkar det optimala valet av blockstorlek (256 trådar = 8 wavefronts = god schemaläggningseffektivitet).

### AMD-GPU-programmering: HIP + ROCm

**ROCm** är AMD:s öppen källkods-GPU-beräkningsstack (drivrutiner, kompilatorer, bibliotek, körtidsmiljö). **HIP** ligger ovanpå den, designad för att vara syntaktiskt identisk med CUDA. PyTorchs ROCm-bygge mappar transparent `torch.cuda.*` till HIP, så samma kod fungerar på AMD-GPU:er.

---

### PyTorch + AMD/HIP

PyTorch levererar ett ROCm-bygge där CUDA API-ytan (`torch.cuda.*`) transparent backas av HIP. Detta innebär att:

- `torch.cuda.is_available()` fungerar på AMD-GPU:er med ROCm
- `tensor.to("cuda")` allokerar på AMD-GPU:n
- `torch.version.hip` exponerar HIP-versionen

PyTorch exponerar också `torch.cuda._compile_kernel()`, en högnivågenväg för att JIT-kompilera en rå kärnsträng och få tillbaka en anropsbar funktion, utan att behöva ett separat byggsteg.

---

<!-- @device:halo_box -->
## Kontrollera efter programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvaruförutsättningar
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Förutsättningar - Windows
- Installera senaste: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Skapa en virtuell miljö

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux öppnar du en terminal i katalogen du väljer och följer kommandona för att skapa en venv med ROCm+PyTorch redan installerat.
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
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux öppnar du en terminal i katalogen du väljer och följer kommandona för att skapa en venv.
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
På Windows öppnar du en terminal i katalogen du väljer och följer kommandona för att skapa en venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tips**: Windows-användare kan behöva ändra sin PowerShell Execution Policy (t.ex.
> ställa in den till RemoteSigned eller Unrestricted) innan de kör vissa PowerShell-kommandon.

<!-- @os:end -->
### Installing Basic Dependencies
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
> **Obs:** För denna spelbok måste ROCm och PyTorch installeras i den virtuella miljön även på Ryzen AI Halo, eftersom kompilering av anpassade kernels kräver de fullständiga utvecklingshuvudfilerna.

Installera ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Installera PyTorch:
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

### Installera ytterligare beroenden

<!-- @os:linux -->
Installera Linux C/C++-byggkedjan. Detta är ett systemberoende och krävs för genomgångarna med C++-tillägg eftersom `CUDAExtension` bygger native `.so`-moduler från `.cu`-filer.

Kör detta en gång på Linux-maskinen, utanför den skapade virtuella Python-miljön:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Efter att ha aktiverat den virtuella miljön `kernel-env`, installera Python-byggberoendena:
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
Se till att [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyare](https://visualstudio.microsoft.com/vs/community/) är installerat med arbetsbelastningen **Desktop development with C++**.

> **Obs**: Denna installation av Visual Studio C++-miljön krävs endast för metoden **C++ Extension**. Den krävs inte för JIT-kompileringsmetoden.

Öppna en PowerShell-terminal och kör följande kommandon innan du bygger C++-tillägget.

**Steg 1: Hitta den installerade Visual Studio C++-miljön**

**(A) Leta upp `vswhere.exe`, som installeras med Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Hitta `vcvars64.bat` från Visual Studio 2022 eller nyare med C++-byggverktyg**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Skriv ut den Visual Studio C++-miljö som används**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Steg 2: Aktivera Visual Studio C++-byggmiljön**

**(A) Kör `vcvars64.bat` och fånga upp miljön den ställer in**

Detta gör `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` och Windows SDK-sökvägar tillgängliga.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importera Visual Studio-miljövariablerna till denna PowerShell-session**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Steg 3: Verifiera att Microsoft C++-kompilatorn är tillgänglig**

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

#### Ange miljövariabler
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
Verifiera att AMD-GPU:n är synlig med:
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

## Ladda ner nödvändiga filer

Skapa följande katalogstruktur genom att skapa **2 nya mappar** och ladda ner motsvarande filer:

| Katalog | Filer att ladda ner | Beskrivning |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- och C++-tilläggsfiler för vektoradditionskernel |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- och C++-tilläggsfiler för matrismultiplikationskernel |


## Genomgångar

### Genomgång 1: Vektoraddition

#### Metod A: JIT-kompilering

JIT-kompilering (Just-In-Time) innebär att kerneln skrivs som en rå C++-sträng inuti Python och kompileras vid körning, utan att behöva extra byggsteg.

För att använda [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), se till att den är nedladdad och kör:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Viktiga kodavsnitt**
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
> **Tips**: Skriptet startar även en bakgrundstråd som pollar `amd-smi` var 100:e ms för att logga topp- och genomsnittlig GPU-användning under kernelkörningen.
<!-- @os:end -->

> **Obs**: **Varför är blockstorleken 256?** <br>
> - Kerneln använder **256 trådar per block** eftersom det stämmer väl överens med **wavefront-exekveringsmodellen för AMD-GPU:er**.
> - Kom ihåg att AMD-hårdvara exekverar trådar i grupper om 32 trådar, vilket resulterar i 8 wavefronts per block. (8 wavefronts x 32 trådar = 1 block)


**Vad arbetsbelastningen gör:**

Kerneln lägger på konstgjort extra arbete för att demonstrera GPU-användning:

- **100 000 000 element** i tensorn
- **Inre loop körs 1 000 gånger** per element och kernelanrop  
- **200 kernelanrop** totalt

**Matematik:**  
- Varje element: ökas med 1 × 1 000 iterationer × 200 anrop = 200 000  
- Slutresultat: 1,0 (startvärde) + 200 000 (additioner) = 200 001,0

**Varför den inre loopen?**  
- Utan loopen `for (int i = 0; i < 1000; i++)` skulle 200 anrop slutföras direkt och övervakningsverktygen skulle inte fånga upp meningsfull GPU-användning. Det konstgjorda arbetet gör att varje kernelkörning tar tillräckligt lång tid för att övervakningsverktyg ska kunna mäta prestanda.

<!-- @os:linux -->
**Förväntad utdata:**[Prestandasiffrorna kommer att variera]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Obs**: På Windows stöds inte `amd-smi`. För att spåra GPU-användning kan du använda Aktivitetshanteraren, där du bör se en kort topp i användningen när du kör programmet.

**Förväntad utdata:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Bra jobbat! Du har precis kört din första GPU-kernel.**

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
#### Metod B: C++-tillägg

Det andra tillvägagångssättet är mer manuellt: skriv kärnan och Python-bindningen till en enda `.cu`-fil, kompilera den nativt med hjälp av PyTorchs byggsystem och importera den till Python.

<!-- @os:windows -->
> **Obs!**: Metoden med C++-tillägg kräver Visual Studios C++-byggmiljö eftersom PyTorch kompilerar `.cu`-källfilen till en native `.pyd`-tilläggsmodul. Byggandet av det nativa tillägget är beroende av Microsofts C++-verktygskedja (kompilator, länkare och byggverktyg) som tillhandahålls av Visual Studio. Kör aktiveringskommandona för Visual Studio från installationsavsnittet innan du bygger tillägget.
<!-- @os:end -->

Ladda ner följande filer om du inte redan har gjort det:
<!-- @os:windows -->
| Fil | Roll |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kärna + startprogram + pybind11-bindning, allt i en fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggskript, använder `CUDAExtension` för att kompilera `.cu`-filen till en `.pyd`-fil |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skript som kör de byggda artefakterna |
<!-- @os:end -->

<!-- @os:linux -->
| Fil | Roll |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kärna + startprogram + pybind11-bindning, allt i en fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggskript, använder `CUDAExtension` för att kompilera `.cu`-filen till en `.so`-fil |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skript som kör de byggda artefakterna |
<!-- @os:end -->

#### **Steg 1: Kärnan, startprogrammet och bindningen** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tips**: Varför använda `hipDeviceSynchronize()`? <br>
> - GPU-kärnstarter är asynkrona. När CPU:n kör `add_one<<<grid_size, block_size>>>(data, n);` skulle den omedelbart köra nästa instruktion utan att vänta på GPU:n. `hipDeviceSynchronize()` tvingar CPU:n att vänta tills GPU-kärnan är klar.

#### **Steg 2: Bygg**
```bash
pip install --no-build-isolation -v .
```
>**Obs!**: Det här kommandot letar efter `setup.py` i den aktuella katalogen för att bygga .cu-filen vi har skapat.


`CUDAExtension` är en CUDA-byggmedhjälpare från `torch.utils.cpp_extension`. Med ROCm **omdirigerar PyTorch `CUDAExtension` till att använda `hipcc`** istället för `nvcc`. ROCm fångar upp byggvägen och dirigerar den genom HIP-kompilatorn, som porterar CUDA-kod till AMD.

Detta producerar följande filer:
<!-- @os:windows -->
- `build/`: katalog med `.pyd`-filerna
- `add_one_kernel.hip`: HIP-källkoden som genereras genom att hipifiera `.cu`-filen; detta är vad `hipcc` faktiskt kompilerade
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: katalog med `.so`-filerna
- `add_one_kernel.hip`: HIP-källkoden som genereras genom att hipifiera `.cu`-filen; detta är vad `hipcc` faktiskt kompilerade
<!-- @os:end -->

#### **Steg 3: Använd från Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Kör detta skript för att se kärnan i aktion:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Förväntad utdata:**
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

### Genomgång 2: Matrismultiplikation

Matrismultiplikation beräknar **C = A × B** där:
- **A** är M×N (rader × kolumner)
- **B** är N×K  
- **C** är M×K (resultatet)

Varje utdataelement definieras som:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Varje element i C beräknas oberoende av de andra, vilket gör detta perfekt för GPU-parallellism.

#### Hur det mappas till GPU-trådar

Till skillnad från vektoraddition (1D) producerar matrismultiplikation ett **2D-utdata**, så vi använder ett **2D-rutnät av trådar**:

| | Vektoraddition | Matrismultiplikation |
|---|---|---|
| **Utdataform** | 1D-array | 2D-matris (M×K) |
| **Trådmappning** | 1 tråd → 1 element | 1 tråd → 1 utdataelement |
| **Startmönster** | 1D-rutnät: `(grid_x, 1, 1)` | 2D-rutnät: `(grid_x, grid_y, 1)` |
| **Blockstorlek** | `(256, 1, 1)` | `(16, 16, 1)` = 256 trådar |

Varje tråd beräknar ett element i utdatamatrisen C. Tråden vid position `(row, col)` beräknar `C[row][col]` genom att multiplicera motsvarande rad i A med motsvarande kolumn i B.

**Minneslayout**: GPU-minnet är platt (1D), men matriser lagras rad för rad. För att komma åt `A[row][col]` använder kärnan `A[row * N + col]`.


#### Metod A: JIT-kompilering:

Precis som i genomgång 1 skrivs kärnan som en rå C++-sträng inuti Python och kompileras vid körning via PyTorchs inbyggda JIT.


För att använda [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), se till att den är nedladdad och kör:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Viktiga kodutdrag**
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

Skriptet verifierar resultatet mot `torch.mm` med en liten tolerans. Flyttalsaritmetik på GPU:er kan ge små numeriska skillnader jämfört med CPU-implementeringar på grund av ordningen på den parallella reduktionen.

<!-- @os:linux -->
**Förväntad utdata:**[Prestandasiffrorna kommer att variera]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Obs!**: På Windows stöds inte `amd-smi`. För att övervaka GPU-användning kan du använda Aktivitetshanteraren, där du bör se en kort topp i användningen när du kör programmet.

**Förväntad utdata:**
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
#### Ansats B: C++-tillägg

Den andra ansatsen är mer manuell: skriv kärnan och Python-bindningen till en enda `.cu`-fil, kompilera den nativt med hjälp av PyTorchs byggsystem och importera den till Python.

<!-- @os:windows -->
> **Obs**: C++-tilläggsansatsen kräver Visual Studios C++-byggmiljö eftersom PyTorch kompilerar `.cu`-källfilen till en native `.pyd`-tilläggsmodul. Att bygga det nativa tillägget beror på Microsofts C++-verktygskedja (kompilator, länkare och byggverktyg) som tillhandahålls av Visual Studio. Kör aktiveringskommandona för Visual Studio från installationsavsnittet innan du bygger tillägget.
<!-- @os:end -->

Ladda ner följande filer om du inte redan har gjort det:
<!-- @os:windows -->
| Fil | Roll |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kärna + startare + pybind11-bindning |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggskript, använder `CUDAExtension` för att kompilera `.cu`-filen till en `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skript som kör de byggda artefakterna |
<!-- @os:end -->
<!-- @os:linux -->
| Fil | Roll |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kärna + startare + pybind11-bindning |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggskript, använder `CUDAExtension` för att kompilera `.cu`-filen till en `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skript som kör de byggda artefakterna |
<!-- @os:end -->

#### **Steg 1: Kärnan, startaren och bindningen** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Jämfört med `add_one_launcher` i genomgång 1 gör startaren här följande:
- Tar två indata-tensorer istället för en
- Härleder alla tre dimensionerna (M, N, K) från tensorformerna, ingen manuell storleksöverföring från Python
- Allokerar och returnerar utdatatensorn C, i stället för att mutera på plats
- Använder `dim3` för både rutnät och block för att uttrycka den 2D-formade starten

#### **Steg 2: Bygg**
```bash
pip install --no-build-isolation -v .
```
>**Obs**: Detta kommando letar efter `setup.py` i den aktuella katalogen för att bygga den `.cu`-fil vi har skapat.


Detta genererar följande filer:
<!-- @os:windows -->
- `build/`: katalog med `.pyd`-filerna
- `matmul_kernel.hip`: HIP-källkoden som genererats genom att hipifiera `.cu`-filen; detta är vad `hipcc` faktiskt kompilerade
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: katalog med `.so`-filerna
- `matmul_kernel.hip`: HIP-källkoden som genererats genom att hipifiera `.cu`-filen; detta är vad `hipcc` faktiskt kompilerade
<!-- @os:end -->

#### **Steg 3: Använd från Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Kör detta skript för att se kärnan i aktion:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Förväntad utdata:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Grymt! Du har just implementerat matrismultiplikation på GPU:n.** Detta är en viktig milstolpe eftersom matrismultiplikation är ryggraden i moderna maskininlärningsoperationer som:
- Neurala nätverkslager
- Uppmärksamhetsmekanismer (attention)
- Inbäddningar (embeddings)
- Transformatorer (transformers)

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

## Nästa steg

Du har lärt dig att skriva, kompilera och starta GPU-kärnor med både JIT-kompilering och C++-tillägg för grundläggande parallella operationer.

**Prestandaoptimeringar:**
- **Kakling med delat minne (shared memory tiling)** - Cacha datablock för att minska åtkomsten till globalt minne
- **Minnessammanslagning (memory coalescing)** - Optimera minnesåtkomstmönster för bandbredd

**Verkliga algoritmer:**
- **2D-faltning (convolution)** - Ett litet filter (kärna) glider över en bild och beräknar varje utdatapixel utifrån en viktad summa av grannpixlar. Detta introducerar stencilberäkningar och kakling med delat minne, där trådar återanvänder överlappande bildregioner för att minska åtkomsten till globalt minne.
- **Softmax-funktionen**: Softmax omvandlar en vektor med tal till sannolikheter som summerar till 1, vanligt förekommande i utdata från neurala nätverk. Att implementera den effektivt på GPU introducerar parallella reduktioner och tekniker för numerisk stabilitet vid bearbetning av stora vektorer.

**Produktionsöverväganden:**
- **Felhantering** - Gränskontroll och enhetshantering
- **PyTorch-integration** - Anpassade operatorer med stöd för autograd