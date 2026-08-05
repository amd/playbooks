<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

Schrijf een GPU-kernel vanaf nul, compileer deze, start hem op een AMD GPU en zie het gebruik pieken. Deze playbook laat zien hoe GPU-berekeningen echt werken: schrijf de kernelcode en voer deze parallel uit over duizenden threads.

> **Opmerking**: Dit is een vrij complexe playbook, die extra debuggen en aanpassingen kan vereisen.

## Wat je leert

<!-- @os:windows -->
- Hoe GPU-kernels werken: grids, blocks, threads, en het indexeringsmodel dat deze koppelt aan data
- Hoe de AMD ROCm/HIP-stack het mogelijk maakt om code in CUDA-stijl te schrijven die zonder aanpassingen op AMD GPU's draait
- Hoe je een kernel tijdens runtime compileert met `torch.cuda._compile_kernel`
- Hoe je een native C++ kernelextensie bouwt met `CUDAExtension` + pybind11, importeerbaar vanuit Python
<!-- @os:end -->
<!-- @os:linux -->
- Hoe GPU-kernels werken: grids, blocks, threads, en het indexeringsmodel dat deze koppelt aan data
- Hoe de AMD ROCm/HIP-stack het mogelijk maakt om code in CUDA-stijl te schrijven die zonder aanpassingen op AMD GPU's draait
- Hoe je een kernel tijdens runtime compileert met `torch.cuda._compile_kernel`
- Hoe je een native C++ kernelextensie bouwt met `CUDAExtension` + pybind11, importeerbaar vanuit Python
- Hoe je de uitvoeringstijd van een kernel meet en het live GPU-gebruik monitort met `amd-smi`
<!-- @os:end -->

---

Deze playbook behandelt twee benaderingen voor kernelontwikkeling:

<!-- @os:windows -->
| Benadering | Startpunt |
|---|---|
| **JIT-compilatie** | `torch.cuda._compile_kernel`, schrijf een kernel als een Python-string, zonder buildstap |
| **C++-extensie** | `CUDAExtension` + pybind11: compileer een `.cu`-bestand naar een native `.pyd` en importeer het |
<!-- @os:end -->
<!-- @os:linux -->
| Benadering | Startpunt |
|---|---|
| **JIT-compilatie** | `torch.cuda._compile_kernel`, schrijf een kernel als een Python-string, zonder buildstap |
| **C++-extensie** | `CUDAExtension` + pybind11: compileer een `.cu`-bestand naar een native `.so` en importeer het |
<!-- @os:end -->

Beide benaderingen draaien op AMD GPU's. Dit is mogelijk omdat PyTorch's ROCm-build het volledige CUDA API-oppervlak naar HIP mapt. Dit betekent dat `torch.cuda`, `CUDAExtension`, en CUDA-kernelsyntax allemaal transparant werken op AMD-hardware.

---

## Achtergrond

### Wat is een GPU-kernel?

Een GPU-kernel is een functie die gelijktijdig parallel wordt uitgevoerd op duizenden GPU-threads. In tegenstelling tot een CPU-functie die eenmaal per aanroep wordt uitgevoerd, wordt een kernel gestart met een **grid** van **blocks**, elk met veel **threads**, die allemaal dezelfde code uitvoeren op verschillende data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Threadindexeringsmodel

Bij het starten van een kernel geef je twee dimensies op:

| Variabele | Betekenis |
|---|---|
| `gridDim` | Aantal blocks in het grid |
| `blockDim` | Aantal threads per block |

Elke thread heeft toegang tot drie ingebouwde alleen-lezen variabelen:

| Variabele | Betekenis |
|---|---|
| `blockIdx.x` | Tot welk block deze thread behoort |
| `blockDim.x` | Aantal threads in één block |
| `threadIdx.x` | Threadindex binnen zijn block |

### Globale thread-ID

Deze variabelen worden gecombineerd om een globaal uniek thread-index te berekenen:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Totaal aantal threads = `gridDim.x * blockDim.x`. Elke thread verwerkt onafhankelijk één element. Dit is de basis van **dataparallellisme**. Dezelfde bewerking wordt tegelijk uitgevoerd op veel elementen, zonder onderlinge afhankelijkheid tussen threads.

---

### GPU-uitvoeringsmodel: Wavefronts

AMD GPU's voeren threads uit in groepen van **32**, genaamd **wavefronts**. Alle threads in een wavefront voeren tegelijk dezelfde instructie uit. Dit beïnvloedt de optimale keuze van blockgrootte (256 threads = 8 wavefronts = goede scheduling-efficiëntie).

### AMD GPU-programmering: HIP + ROCm

**ROCm** is AMD's open-source GPU-compute-stack (drivers, compilers, bibliotheken, runtime). **HIP** zit hierboven op en is ontworpen om syntactisch identiek te zijn aan CUDA. PyTorch's ROCm-build mapt `torch.cuda.*` transparant naar HIP, zodat dezelfde code werkt op AMD GPU's.

---

### PyTorch + AMD/HIP

PyTorch levert een ROCm-build waarbij het CUDA API-oppervlak (`torch.cuda.*`) transparant wordt ondersteund door HIP. Dit betekent:

- `torch.cuda.is_available()` werkt op AMD GPU's met ROCm
- `tensor.to("cuda")` alloceert op de AMD GPU
- `torch.version.hip` toont de HIP-versie

PyTorch biedt ook `torch.cuda._compile_kernel()`, een handige shortcut om een ruwe kernel-string JIT te compileren en een aanroepbaar object terug te krijgen, zonder dat er een aparte buildstap nodig is.

---

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Vereisten - Windows
- Installeer de nieuwste versie van: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Een virtuele omgeving maken

<!-- @os:linux -->
<!-- @device:halo_box -->
Open op Linux een terminal in de map naar keuze en volg de commando's om een venv te maken met ROCm+PyTorch al geïnstalleerd.
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
**Geef je gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

Open op Linux een terminal in de map naar keuze en volg de commando's om een venv te maken.
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
Open op Windows een terminal in de map naar keuze en volg de commando's om een venv te maken.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
> instellen op RemoteSigned of Unrestricted) voordat ze bepaalde PowerShell-commando's uitvoeren.

<!-- @os:end -->
### Basisafhankelijkheden installeren
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
> **Opmerking:** Voor deze playbook moeten ROCm en PyTorch in de virtuele omgeving worden geïnstalleerd, zelfs op de Ryzen AI Halo, omdat het compileren van aangepaste kernels de volledige ontwikkelheaders vereist.

Installeer ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Installeer PyTorch:
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

### Aanvullende afhankelijkheden installeren

<!-- @os:linux -->
Installeer de Linux C/C++-buildtoolchain. Dit is een systeemniveau-afhankelijkheid en is vereist voor de C++-extensiehandleidingen, omdat `CUDAExtension` native `.so`-modules bouwt vanuit `.cu`-bestanden.

Voer dit eenmalig uit op de Linux-machine, buiten de aangemaakte virtuele Python-omgeving:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Na het activeren van de virtuele omgeving `kernel-env`, installeer je de Python-buildafhankelijkheden:
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
Zorg ervoor dat [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) of [nieuwer](https://visualstudio.microsoft.com/vs/community/) is geïnstalleerd met de werkbelasting **Desktop development with C++**.

> **Opmerking**: Deze installatie van de Visual Studio C++-omgeving is alleen vereist voor de aanpak **C++ Extension**. Dit is niet nodig voor de aanpak JIT Compilation.

Open een PowerShell-terminal en voer de volgende opdrachten uit voordat je de C++-extensie bouwt.

**Stap 1: Zoek de geïnstalleerde Visual Studio C++-omgeving**

**(A) Zoek `vswhere.exe`, dat wordt geïnstalleerd met de Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Zoek `vcvars64.bat` van Visual Studio 2022 of nieuwer met C++-buildtools**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Print de Visual Studio C++-omgeving die wordt gebruikt**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Stap 2: Activeer de Visual Studio C++-buildomgeving**

**(A) Voer `vcvars64.bat` uit en leg de omgeving vast die deze instelt**

Hierdoor worden `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` en de paden van de Windows SDK beschikbaar gemaakt.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importeer de Visual Studio-omgevingsvariabelen in deze PowerShell-sessie**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Stap 3: Controleer of de Microsoft C++-compiler beschikbaar is**

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

#### Omgevingsvariabelen instellen
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
Controleer of de AMD GPU zichtbaar is met:
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

## Vereiste bestanden downloaden

Maak de volgende mapstructuur aan door de **2 nieuwe mappen** aan te maken en de bijbehorende bestanden te downloaden:

| Map | Te downloaden bestanden | Beschrijving |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- en C++-extensiebestanden voor de vectoroptelkernel |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- en C++-extensiebestanden voor de matrixvermenigvuldigingskernel |


## Handleidingen

### Handleiding 1: Vectoroptelling

#### Aanpak A: JIT Compilation

JIT (Just-In-Time) compilatie betekent dat de kernel wordt geschreven als een onbewerkte C++-string binnen Python en tijdens runtime wordt gecompileerd, zonder dat er extra buildstappen nodig zijn.

Om [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) te gebruiken, zorg ervoor dat het is gedownload en voer uit:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Belangrijke codefragmenten**
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
> **Tip**: Het script start ook een achtergrondthread die elke 100ms `amd-smi` opvraagt om de piek- en gemiddelde GPU-benutting tijdens het uitvoeren van de kernel vast te leggen.
<!-- @os:end -->

> **Opmerking**: **Waarom is de blokgrootte 256?** <br>
> - De kernel gebruikt **256 threads per blok** omdat dit goed aansluit bij het **wavefront-uitvoeringsmodel van AMD-GPU's**.
> - Herinner je dat AMD-hardware threads uitvoert in groepen van 32 threads, wat resulteert in 8 wavefronts per blok. (8 wavefronts x 32 threads = 1 blok)


**Wat de workload doet:**

De kernel voegt kunstmatig extra werk toe om GPU-benutting te demonstreren:

- **100.000.000 elementen** in de tensor
- **Interne lus wordt 1.000 keer uitgevoerd** per element per kernel-aanroep  
- **200 kernel-aanroepen** in totaal

**Wiskunde:**  
- Elk element: wordt verhoogd met 1 × 1.000 iteraties × 200 aanroepen = 200.000  
- Eindresultaat: 1.0 (startwaarde) + 200.000 (optellingen) = 200.001,0

**Waarom de interne lus?**  
- Zonder de `for (int i = 0; i < 1000; i++)`-lus zouden 200 aanroepen direct klaar zijn en zouden de monitoringtools geen zinvolle GPU-benutting kunnen vastleggen. Het kunstmatige werk zorgt ervoor dat elke kernel-run lang genoeg duurt zodat monitoringtools de prestaties kunnen meten.

<!-- @os:linux -->
**Verwachte uitvoer:**[De prestatiecijfers zullen variëren]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Op Windows wordt `amd-smi` niet ondersteund. Om de GPU-benutting te volgen, kun je Taakbeheer gebruiken, waar je een korte piek in de benutting zou moeten zien wanneer je het programma uitvoert.

**Verwachte uitvoer:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Goed gedaan! Je hebt zojuist je eerste GPU-kernel uitgevoerd.**

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
#### Aanpak B: C++-extensie

De tweede aanpak is handmatiger: schrijf de kernel en Python-binding naar één enkel `.cu`-bestand, compileer dit native met het buildsysteem van PyTorch en importeer het in Python.

<!-- @os:windows -->
> **Opmerking**: De C++-extensie-aanpak vereist de Visual Studio C++-buildomgeving, omdat PyTorch het `.cu`-bronbestand compileert tot een native `.pyd`-extensiemodule. Het bouwen van die native extensie is afhankelijk van de Microsoft C++-toolchain (compiler, linker en buildtools) die door Visual Studio wordt geleverd. Voer de Visual Studio-activeringscommando's uit de installatiesectie uit voordat u de extensie bouwt.
<!-- @os:end -->

Download de volgende bestanden als u dat nog niet heeft gedaan:
<!-- @os:windows -->
| Bestand | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11-binding, alles in één bestand |
| [setup.py](assets/Vector_Addition/setup.py) | Buildscript, gebruikt `CUDAExtension` om de `.cu` te compileren naar een `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-script dat de gebouwde artefacten uitvoert |
<!-- @os:end -->

<!-- @os:linux -->
| Bestand | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11-binding, alles in één bestand |
| [setup.py](assets/Vector_Addition/setup.py) | Buildscript, gebruikt `CUDAExtension` om de `.cu` te compileren naar een `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-script dat de gebouwde artefacten uitvoert |
<!-- @os:end -->

#### **Stap 1: De kernel, launcher en binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tip**: Waarom `hipDeviceSynchronize()` gebruiken? <br>
> - GPU-kernellanceringen zijn asynchroon. Wanneer de CPU `add_one<<<grid_size, block_size>>>(data, n);` uitvoert, zou deze onmiddellijk de volgende instructie uitvoeren zonder te wachten op de GPU. `hipDeviceSynchronize()` dwingt de CPU om te wachten totdat de GPU-kernel is voltooid.

#### **Stap 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Opmerking**: Dit commando zoekt naar `setup.py` in de huidige map om het door ons gemaakte .cu-bestand te bouwen.


`CUDAExtension` is een CUDA-buildhelper uit `torch.utils.cpp_extension`. Met ROCm **mapt PyTorch `CUDAExtension` om `hipcc`** te gebruiken in plaats van `nvcc`. ROCm onderschept het buildpad en leidt dit via de HIP-compiler, waardoor CUDA-code wordt geport naar AMD.

Dit produceert de volgende bestanden:
<!-- @os:windows -->
- `build/`: map met de `.pyd`-bestanden
- `add_one_kernel.hip`: de HIP-broncode gegenereerd door het hipifyen van het `.cu`-bestand; dit is wat `hipcc` daadwerkelijk heeft gecompileerd
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: map met de `.so`-bestanden
- `add_one_kernel.hip`: de HIP-broncode gegenereerd door het hipifyen van het `.cu`-bestand; dit is wat `hipcc` daadwerkelijk heeft gecompileerd
<!-- @os:end -->

#### **Stap 3: Gebruik vanuit Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Voer dit script uit om de kernel in actie te zien:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Verwachte uitvoer:**
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

### Doorloop 2: Matrixvermenigvuldiging

Matrixvermenigvuldiging berekent **C = A × B** waarbij:
- **A** M×N is (rijen × kolommen)
- **B** N×K is
- **C** M×K is (het resultaat)

Elk uitvoerelement is gedefinieerd als:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Elk element van C wordt onafhankelijk berekend, wat dit perfect maakt voor GPU-parallellisme.

#### Hoe dit wordt afgebeeld op GPU-threads

In tegenstelling tot vectoroptelling (1D) produceert matrixvermenigvuldiging een **2D-uitvoer**, dus gebruiken we een **2D-raster van threads**:

| | Vectoroptelling | Matrixvermenigvuldiging |
|---|---|---|
| **Uitvoervorm** | 1D-array | 2D-matrix (M×K) |
| **Threadtoewijzing** | 1 thread → 1 element | 1 thread → 1 uitvoerelement |
| **Lanceerpatroon** | 1D-raster: `(grid_x, 1, 1)` | 2D-raster: `(grid_x, grid_y, 1)` |
| **Blokgrootte** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

Elke thread berekent één element van de uitvoermatrix C. De thread op positie `(row, col)` berekent `C[row][col]` door de bijbehorende rij van A te vermenigvuldigen met de bijbehorende kolom van B.

**Geheugenindeling**: GPU-geheugen is plat (1D), maar matrices worden rij-voor-rij opgeslagen. Om `A[row][col]` te benaderen, gebruikt de kernel `A[row * N + col]`.


#### Aanpak A: JIT-compilatie:

Net als in Doorloop 1 wordt de kernel geschreven als een ruwe C++-string in Python en tijdens runtime gecompileerd via de ingebouwde JIT van PyTorch.


Om [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) te gebruiken, zorg ervoor dat het is gedownload en voer uit:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Belangrijke codefragmenten**
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

Het script verifieert het resultaat tegen `torch.mm` met een kleine tolerantie. Drijvendekommarekenkunde op GPU's kan kleine numerieke verschillen opleveren in vergelijking met CPU-implementaties vanwege de volgorde van parallelle reductie.

<!-- @os:linux -->
**Verwachte uitvoer:**[De prestatiegetallen zullen variëren]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Op Windows wordt `amd-smi` niet ondersteund. Om het GPU-gebruik te volgen, kunt u Taakbeheer gebruiken, waar u een korte piek in gebruik zou moeten zien wanneer u het programma uitvoert.

**Verwachte uitvoer:**
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
#### Aanpak B: C++ Extensie

De tweede aanpak is meer handmatig: schrijf de kernel en Python-binding naar één `.cu`-bestand, compileer het native met het buildsysteem van PyTorch en importeer het in Python.

<!-- @os:windows -->
> **Opmerking**: Voor de C++ Extensie-aanpak is de Visual Studio C++ buildomgeving vereist, omdat PyTorch het `.cu`-bronbestand compileert naar een native `.pyd`-extensiemodule. Het bouwen van die native extensie is afhankelijk van de Microsoft C++-toolchain (compiler, linker en buildtools) die door Visual Studio wordt geleverd. Voer de Visual Studio-activeringscommando's uit de instellingensectie uit voordat je de extensie bouwt.
<!-- @os:end -->

Download de volgende bestanden als je dat nog niet hebt gedaan:
<!-- @os:windows -->
| Bestand | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Buildscript, gebruikt `CUDAExtension` om de `.cu` te compileren naar een `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-script dat de gebouwde artefacten uitvoert |
<!-- @os:end -->
<!-- @os:linux -->
| Bestand | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Buildscript, gebruikt `CUDAExtension` om de `.cu` te compileren naar een `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-script dat de gebouwde artefacten uitvoert |
<!-- @os:end -->

#### **Stap 1: De kernel, launcher en binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Vergeleken met `add_one_launcher` in Walkthrough 1 doet de launcher hier het volgende:
- Neemt twee invoertensors in plaats van één
- Leidt alle drie de dimensies (M, N, K) af van de tensorvormen, zonder handmatig groottes vanuit Python door te geven
- Wijst de uitvoertensor C toe en retourneert deze, in plaats van deze inline te muteren
- Gebruikt `dim3` voor zowel grid als block om de 2D-launchvorm uit te drukken

#### **Stap 2: Bouwen**
```bash
pip install --no-build-isolation -v .
```
>**Opmerking**: Dit commando zoekt naar `setup.py` in de huidige map om het door ons gemaakte .cu-bestand te bouwen.


Dit levert de volgende bestanden op:
<!-- @os:windows -->
- `build/`: map met de `.pyd`-bestanden
- `matmul_kernel.hip`: de HIP-broncode die is gegenereerd door het hipifyen van het `.cu`-bestand; dit is wat `hipcc` daadwerkelijk heeft gecompileerd
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: map met de `.so`-bestanden
- `matmul_kernel.hip`: de HIP-broncode die is gegenereerd door het hipifyen van het `.cu`-bestand; dit is wat `hipcc` daadwerkelijk heeft gecompileerd
<!-- @os:end -->

#### **Stap 3: Gebruiken vanuit Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Voer dit script uit om de kernel in actie te zien:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Verwachte uitvoer:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Geweldig! Je hebt zojuist matrixvermenigvuldiging op de GPU geïmplementeerd.** Dit is een belangrijke mijlpaal, omdat matrixvermenigvuldiging de ruggengraat is van moderne machine learning-bewerkingen zoals:
- Neurale netwerklagen
- Attention-mechanismen
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

## Volgende stappen

Je hebt geleerd hoe je GPU-kernels schrijft, compileert en start met zowel JIT-compilatie als C++-extensies voor basale parallelle bewerkingen.

**Prestatie-optimalisaties:**
- **Shared memory tiling** - Cache datablokken om toegang tot globaal geheugen te verminderen
- **Geheugencoalescentie** - Optimaliseer geheugentoegangspatronen voor bandbreedte

**Algoritmen uit de praktijk:**
- **2D-convolutie** - Een klein filter (kernel) schuift over een afbeelding en berekent elke uitvoerpixel op basis van een gewogen som van naburige pixels. Dit introduceert stencilberekeningen en shared memory tiling, waarbij threads overlappende afbeeldingsgebieden hergebruiken om toegang tot globaal geheugen te verminderen.
- **Softmax-functie**: Softmax zet een vector van getallen om in kansen die optellen tot 1, vaak gebruikt in de uitvoer van neurale netwerken. Het efficiënt implementeren hiervan op de GPU introduceert parallelle reducties en technieken voor numerieke stabiliteit tijdens de verwerking van grote vectoren.

**Overwegingen voor productie:**
- **Foutafhandeling** - Grenscontrole en apparaatbeheer
- **PyTorch-integratie** - Aangepaste operators met ondersteuning voor autograd