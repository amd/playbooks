<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

Skriv en GPU-kerne fra bunden, kompilér den, start den på en AMD GPU, og se udnyttelsen stige. Denne playbook viser, hvordan GPU-beregning faktisk fungerer: skriv kernekoden, og udfør den parallelt på tværs af tusindvis af tråde.

> **Bemærk**: Dette er en ret kompleks playbook, som muligvis kræver lidt ekstra fejlfinding og ændringer.

## Hvad du vil lære

<!-- @os:windows -->
- Hvordan GPU-kerner fungerer: gitre, blokke, tråde og den indekseringsmodel, der knytter dem til data
- Hvordan AMD ROCm/HIP-stakken lader dig skrive CUDA-lignende kode, der kører på AMD GPU'er uden ændringer
- Hvordan man kompilerer en kerne ved kørselstid ved hjælp af `torch.cuda._compile_kernel`
- Hvordan man bygger en native C++-kerneudvidelse med `CUDAExtension` + pybind11, der kan importeres fra Python
<!-- @os:end -->
<!-- @os:linux -->
- Hvordan GPU-kerner fungerer: gitre, blokke, tråde og den indekseringsmodel, der knytter dem til data
- Hvordan AMD ROCm/HIP-stakken lader dig skrive CUDA-lignende kode, der kører på AMD GPU'er uden ændringer
- Hvordan man kompilerer en kerne ved kørselstid ved hjælp af `torch.cuda._compile_kernel`
- Hvordan man bygger en native C++-kerneudvidelse med `CUDAExtension` + pybind11, der kan importeres fra Python
- Hvordan man måler kerneudførelsestid og overvåger live GPU-udnyttelse med `amd-smi`
<!-- @os:end -->

---

Denne playbook dækker to tilgange til kerneudvikling:

<!-- @os:windows -->
| Tilgang | Indgangspunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kerne som en Python-streng, uden byggetrin |
| **C++-udvidelse** | `CUDAExtension` + pybind11: kompilér en `.cu`-fil til en native `.pyd` og importér den |
<!-- @os:end -->
<!-- @os:linux -->
| Tilgang | Indgangspunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kerne som en Python-streng, uden byggetrin |
| **C++-udvidelse** | `CUDAExtension` + pybind11: kompilér en `.cu`-fil til en native `.so` og importér den |
<!-- @os:end -->

Begge tilgange kører på AMD GPU'er. Dette er muligt, fordi PyTorch's ROCm-build afbilder hele CUDA API-overfladen til HIP. Det betyder, at `torch.cuda`, `CUDAExtension` og CUDA-kernesyntaks alle fungerer på AMD-hardware på en transparent måde.

---

## Baggrund

### Hvad er en GPU-kerne?

En GPU-kerne er en funktion, der kører parallelt på tværs af tusindvis af GPU-tråde samtidigt. I modsætning til en CPU-funktion, der udføres én gang pr. kald, startes en kerne med et **gitter** af **blokke**, der hver indeholder mange **tråde**, som alle udfører den samme kode på forskellige data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Trådindekseringsmodel

Når du starter en kerne, angiver du to dimensioner:

| Variabel | Betydning |
|---|---|
| `gridDim` | Antal blokke i gitteret |
| `blockDim` | Antal tråde pr. blok |

Hver tråd har adgang til tre indbyggede skrivebeskyttede variabler:

| Variabel | Betydning |
|---|---|
| `blockIdx.x` | Hvilken blok denne tråd tilhører |
| `blockDim.x` | Antal tråde i én blok |
| `threadIdx.x` | Trådindeks inden for dens blok |

### Globalt tråd-ID

Disse variabler kombineres for at beregne et globalt unikt trådindeks:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Samlet antal tråde = `gridDim.x * blockDim.x`. Hver tråd behandler ét element uafhængigt. Dette er grundlaget for **dataparallelisme**. Den samme operation kører på mange elementer på én gang, uden afhængighed mellem tråde.

---

### GPU-udførelsesmodel: Wavefronts

AMD GPU'er udfører tråde i grupper af **32** kaldet **wavefronts**. Alle tråde i en wavefront kører den samme instruktion samtidigt. Dette påvirker valget af optimal blokstørrelse (256 tråde = 8 wavefronts = god planlægningseffektivitet).

### AMD GPU-programmering: HIP + ROCm

**ROCm** er AMD's open source GPU-beregningsstak (drivere, compilere, biblioteker, kørselstid). **HIP** ligger ovenpå og er designet til at være syntaktisk identisk med CUDA. PyTorch's ROCm-build afbilder transparent `torch.cuda.*` til HIP, så den samme kode fungerer på AMD GPU'er.

---

### PyTorch + AMD/HIP

PyTorch leveres med et ROCm-build, hvor CUDA API-overfladen (`torch.cuda.*`) transparent understøttes af HIP. Det betyder:

- `torch.cuda.is_available()` fungerer på AMD GPU'er med ROCm
- `tensor.to("cuda")` allokerer på AMD GPU'en
- `torch.version.hip` eksponerer HIP-versionen

PyTorch eksponerer også `torch.cuda._compile_kernel()`, en høj-niveau genvej til JIT-kompilering af en rå kernestreng og returnering af et kaldbart objekt, uden behov for et separat byggetrin.

---

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Forudsætninger - Windows
- Installér den nyeste: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Opret et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux skal du åbne en terminal i den ønskede mappe og følge kommandoerne for at oprette et venv med ROCm+Pytorch allerede installeret.
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
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen for at dette træder i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux skal du åbne en terminal i den ønskede mappe og følge kommandoerne for at oprette et venv.
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
På Windows skal du åbne en terminal i den ønskede mappe og følge kommandoerne for at oprette et venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Windows-brugere skal muligvis ændre deres PowerShell-udførelsespolitik (f.eks.
> sætte den til RemoteSigned eller Unrestricted) inden de kører nogle PowerShell-kommandoer.

<!-- @os:end -->
### Installation af grundlæggende afhængigheder
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
> **Bemærk:** Til denne playbook skal ROCm og PyTorch installeres i det virtuelle miljø, selv på Ryzen AI Halo, da kompilering af brugerdefinerede kerner kræver de fulde udviklingsheadere.

Installer ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Installer PyTorch:
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

### Installation af yderligere afhængigheder

<!-- @os:linux -->
Installer Linux C/C++ byggeværktøjskæden. Dette er en afhængighed på systemniveau og er påkrævet til C++ udvidelsesgennemgangene, fordi `CUDAExtension` bygger native `.so`-moduler fra `.cu`-filer.

Kør dette én gang på Linux-maskinen, uden for det oprettede Python virtuelle miljø:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Efter aktivering af det virtuelle `kernel-env`-miljø skal du installere Python-byggeafhængighederne:
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
Sørg for, at [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) er installeret med arbejdsbyrden **Desktop development with C++**.

> **Bemærk**: Denne opsætning af Visual Studio C++-miljøet er kun påkrævet til **C++ Extension**-tilgangen. Det er ikke påkrævet til JIT-kompileringstilgangen.

Åbn en PowerShell-terminal og kør følgende kommandoer, inden du bygger C++-udvidelsen.

**Trin 1: Find det installerede Visual Studio C++-miljø**

**(A) Find `vswhere.exe`, som installeres med Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Find `vcvars64.bat` fra Visual Studio 2022 eller nyere med C++ byggeværktøjer**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Udskriv det Visual Studio C++-miljø, der bruges**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Trin 2: Aktiver Visual Studio C++ byggemiljøet**

**(A) Kør `vcvars64.bat` og registrer det miljø, det opsætter**

Dette gør `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` og Windows SDK-stier tilgængelige.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importér Visual Studio-miljøvariablerne til denne PowerShell-session**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Trin 3: Bekræft, at Microsoft C++-kompileren er tilgængelig**

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

#### Indstil miljøvariabler
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
Bekræft, at AMD GPU'en er synlig med:
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

## Download af påkrævede filer

Opret følgende mappestruktur ved at oprette de **2 nye mapper** og downloade de tilsvarende filer:

| Mappe | Filer der skal downloades | Beskrivelse |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- og C++-udviddelsesfiler til vektoradditionskerne |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- og C++-udviddelsesfiler til matrixmultiplikationskerne |


## Gennemgange

### Gennemgang 1: Vektoraddition

#### Tilgang A: JIT-kompilering

JIT (Just-In-Time)-kompilering betyder, at kernen er skrevet som en rå C++-streng inde i Python og kompileres ved kørselstid, uden at der er behov for ekstra byggetrin.

For at bruge [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) skal du sikre dig, at den er downloadet, og køre:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Vigtige kodeuddrag**
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
> **Tip**: Scriptet starter også en baggrundstråd, der poller `amd-smi` hvert 100 ms for at logge maksimal og gennemsnitlig GPU-udnyttelse under kernekørslen.
<!-- @os:end -->

> **Bemærk**: **Hvorfor er blokstørrelsen 256?** <br>
> - Kernen bruger **256 tråde pr. blok**, fordi det passer godt til **AMD GPU'ernes wavefront-eksekvéringsmodel**.
> - Husk, at AMD-hardware eksekverer tråde i grupper af 32 tråde, hvilket resulterer i 8 wavefronts pr. blok. (8 wavefronts x 32 tråde = 1 blok)


**Hvad arbejdsbyrden gør:**

Kernen tilføjer kunstigt ekstra arbejde for at demonstrere GPU-udnyttelse:

- **100.000.000 elementer** i tensoren
- **Indre løkke kører 1.000 gange** pr. element pr. kernekørsel  
- **200 kernekørsler** i alt

**Matematik:**  
- Hvert element: forøges med 1 × 1.000 iterationer × 200 kørsler = 200.000  
- Slutresultat: 1,0 (startværdi) + 200.000 (additioner) = 200.001,0

**Hvorfor den indre løkke?**  
- Uden `for (int i = 0; i < 1000; i++)`-løkken ville 200 kørsler afsluttes øjeblikkeligt, og overvågningsværktøjerne ville ikke registrere meningsfuld GPU-udnyttelse. Det kunstige arbejde gør, at hver kernekørsel varer længe nok til, at overvågningsværktøjer kan måle ydeevnen.

<!-- @os:linux -->
**Forventet output:** [Ydeevnetallene vil variere]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: På Windows understøttes `amd-smi` ikke. For at spore GPU-udnyttelse kan du bruge Jobliste, hvor du bør se en kort stigning i udnyttelsen, når du kører programmet.

**Forventet output:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Godt arbejde! Du har netop kørt din første GPU-kerne.**

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
#### Tilgang B: C++ Extension

Den anden tilgang er mere manuel: skriv kernen og Python-bindingen til en enkelt `.cu`-fil, kompilér den nativt ved hjælp af PyTorch's byggesystem, og importér den i Python.

<!-- @os:windows -->
> **Bemærk**: C++ Extension-tilgangen kræver Visual Studio C++ byggemiljøet, fordi PyTorch kompilerer `.cu`-kildefilen til et nativt `.pyd`-extensionsmodul. Bygning af det native extension afhænger af Microsofts C++ værktøjskæde (compiler, linker og byggeværktøjer) leveret af Visual Studio. Kør Visual Studio-aktiveringskommandoerne fra opsætningssektionen, inden du bygger extensionen.
<!-- @os:end -->

Download følgende filer, hvis du ikke allerede har gjort det:
<!-- @os:windows -->
| Fil | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kerne + launcher + pybind11-binding, alt i én fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggescript, bruger `CUDAExtension` til at kompilere `.cu` til en `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-script der kører de byggede artefakter |
<!-- @os:end -->

<!-- @os:linux -->
| Fil | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kerne + launcher + pybind11-binding, alt i én fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggescript, bruger `CUDAExtension` til at kompilere `.cu` til en `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-script der kører de byggede artefakter |
<!-- @os:end -->

#### **Trin 1: Kernen, launcheren og bindingen** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Hvorfor bruge `hipDeviceSynchronize()`? <br>
> - GPU-kernelstarter er asynkrone. Når CPU'en kører `add_one<<<grid_size, block_size>>>(data, n);`, ville den straks udføre den næste instruktion uden at vente på GPU'en. `hipDeviceSynchronize()` tvinger CPU'en til at vente, indtil GPU-kernen er færdig.

#### **Trin 2: Byg**
```bash
pip install --no-build-isolation -v .
```
>**Bemærk**: Denne kommando leder efter `setup.py` i den aktuelle mappe for at bygge den `.cu`-fil, vi har oprettet.


`CUDAExtension` er en CUDA-byggehjælper fra `torch.utils.cpp_extension`. Med ROCm **omdirigerer PyTorch `CUDAExtension` til at bruge `hipcc`** i stedet for `nvcc`. ROCm opfanger byggestien og ruter den gennem HIP-compileren, som porterer CUDA-kode til AMD.

Dette producerer følgende filer:
<!-- @os:windows -->
- `build/`: mappe med `.pyd`-filerne
- `add_one_kernel.hip`: HIP-kilden genereret ved at hipificere `.cu`-filen; dette er hvad `hipcc` faktisk kompilerede
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: mappe med `.so`-filerne
- `add_one_kernel.hip`: HIP-kilden genereret ved at hipificere `.cu`-filen; dette er hvad `hipcc` faktisk kompilerede
<!-- @os:end -->

#### **Trin 3: Brug fra Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Kør dette script for at se kernen i aktion:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Forventet output:**
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

### Gennemgang 2: Matrixmultiplikation

Matrixmultiplikation beregner **C = A × B**, hvor:
- **A** er M×N (rækker × kolonner)
- **B** er N×K  
- **C** er M×K (resultatet)

Hvert outputelement er defineret som:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Hvert element i C beregnes uafhængigt, hvilket gør dette perfekt til GPU-parallelisme.

#### Sådan mappes det til GPU-tråde

I modsætning til vektoraddition (1D) producerer matrixmultiplikation et **2D-output**, så vi bruger et **2D-gitter af tråde**:

| | Vektoraddition | Matrixmultiplikation |
|---|---|---|
| **Outputform** | 1D-array | 2D-matrix (M×K) |
| **Trådmapping** | 1 tråd → 1 element | 1 tråd → 1 outputelement |
| **Startmønster** | 1D-gitter: `(grid_x, 1, 1)` | 2D-gitter: `(grid_x, grid_y, 1)` |
| **Blokstørrelse** | `(256, 1, 1)` | `(16, 16, 1)` = 256 tråde |

Hver tråd beregner ét element i outputmatricen C. Tråden ved position `(row, col)` beregner `C[row][col]` ved at multiplicere den tilsvarende række i A med den tilsvarende kolonne i B.

**Hukommelseslayout**: GPU-hukommelse er flad (1D), men matricer gemmes række for række. For at tilgå `A[row][col]` bruger kernen `A[row * N + col]`.


#### Tilgang A: JIT-kompilering:

Ligesom i Gennemgang 1 skrives kernen som en rå C++-streng inde i Python og kompileres ved kørselstid via PyTorch's indbyggede JIT.


For at bruge [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) skal du sikre dig, at den er downloadet, og køre:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Vigtige kodeuddrag**
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

Scriptet verificerer resultatet mod `torch.mm` med en lille tolerance. Floating-point-aritmetik på GPU'er kan producere små numeriske forskelle sammenlignet med CPU-implementeringer på grund af parallel reduktionsrækkefølge.

<!-- @os:linux -->
**Forventet output:** [Ydelsestallene vil variere]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: På Windows understøttes `amd-smi` ikke. For at spore GPU-udnyttelse kan du bruge Jobliste, hvor du bør se en kort stigning i udnyttelsen, når du kører programmet.

**Forventet output:**
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
#### Tilgang B: C++ Extension

Den anden tilgang er mere manuel: skriv kernen og Python-bindingen til en enkelt `.cu`-fil, kompilér den nativt ved hjælp af PyTorchs byggesystem, og importér den i Python.

<!-- @os:windows -->
> **Bemærk**: C++ Extension-tilgangen kræver Visual Studio C++ byggemiljøet, fordi PyTorch kompilerer `.cu`-kildefilen til et nativt `.pyd`-extensionsmodul. Opbygning af det native extension afhænger af Microsofts C++ toolchain (compiler, linker og byggeværktøjer) leveret af Visual Studio. Kør Visual Studio-aktiveringskommandoerne fra opsætningssektionen, inden du bygger extensionen.
<!-- @os:end -->

Download følgende filer, hvis du ikke allerede har gjort det:
<!-- @os:windows -->
| Fil | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kerne + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggescript, bruger `CUDAExtension` til at kompilere `.cu` til en `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-script der kører de byggede artefakter |
<!-- @os:end -->
<!-- @os:linux -->
| Fil | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kerne + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggescript, bruger `CUDAExtension` til at kompilere `.cu` til en `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-script der kører de byggede artefakter |
<!-- @os:end -->

#### **Trin 1: Kernen, launcheren og bindingen** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Sammenlignet med `add_one_launcher` i Gennemgang 1 gør launcheren her følgende:
- Tager to inputtensorer i stedet for én
- Udleder alle tre dimensioner (M, N, K) fra tensorformerne – ingen manuel størrelsesoverføring fra Python
- Allokerer og returnerer outputtensoren C i stedet for at mutere på stedet
- Bruger `dim3` til både grid og blok for at udtrykke den 2D-startform

#### **Trin 2: Byg**
```bash
pip install --no-build-isolation -v .
```
>**Bemærk**: Denne kommando leder efter `setup.py` i den aktuelle mappe for at bygge den `.cu`-fil, vi har oprettet.


Dette producerer følgende filer:
<!-- @os:windows -->
- `build/`:  mappe med `.pyd`-filerne
- `matmul_kernel.hip`:  HIP-kilden genereret ved at hipificere `.cu`-filen; dette er hvad `hipcc` faktisk kompilerede
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  mappe med `.so`-filerne
- `matmul_kernel.hip`:  HIP-kilden genereret ved at hipificere `.cu`-filen; dette er hvad `hipcc` faktisk kompilerede
<!-- @os:end -->

#### **Trin 3: Brug fra Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Kør dette script for at se kernen i aktion:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Forventet output:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Fremragende! Du har netop implementeret matrixmultiplikation på GPU'en.** Dette er en vigtig milepæl, fordi matrixmultiplikation er rygraden i moderne maskinlæringsoperationer som:
- Neurale netværkslag
- Opmærksomhedsmekanismer
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

## Næste skridt

Du har lært at skrive, kompilere og starte GPU-kerner ved hjælp af både JIT-kompilering og C++ extensions til grundlæggende parallelle operationer.

**Ydeevneoptimeringer:**
- **Shared memory tiling** – Cach datablokke for at reducere adgang til global hukommelse
- **Memory coalescing** – Optimer hukommelsesadgangsmønstre for båndbredde

**Algoritmer fra den virkelige verden:**
- **2D Konvolution** – Et lille filter (kerne) glider hen over et billede og beregner hver outputpixel fra en vægtet sum af nabopixler. Dette introducerer stencil-beregninger og shared memory tiling, hvor tråde genbruger overlappende billedregioner for at reducere adgang til global hukommelse.
- **Softmax-funktion**: Softmax konverterer en vektor af tal til sandsynligheder, der summer til 1, og bruges almindeligvis i neurale netværks output. En effektiv implementering på GPU introducerer parallelle reduktioner og teknikker til numerisk stabilitet ved behandling af store vektorer.

**Produktionshensyn:**
- **Fejlhåndtering** – Grænsekontrol og enhedsstyring
- **PyTorch-integration** – Brugerdefinerede operatorer med autograd-understøttelse