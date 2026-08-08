<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

Skriv en GPU-kjerne fra bunnen av, kompiler den, kjør den på en AMD GPU, og se utnyttelsen skyte i været. Denne oppskriften viser hvordan GPU-beregninger faktisk fungerer: skriv kjernekoden, og utfør den parallelt på tusenvis av tråder.

> **Merk**: Dette er en ganske kompleks oppskrift, som kan kreve litt ekstra feilsøking og modifikasjoner.

## Hva du vil lære

<!-- @os:windows -->
- Hvordan GPU-kjerner fungerer: grid, blokker, tråder, og indekseringsmodellen som knytter dem til data
- Hvordan AMD ROCm/HIP-stakken lar deg skrive CUDA-lignende kode som kjører på AMD GPU-er uten endringer
- Hvordan du kompilerer en kjerne under kjøring ved hjelp av `torch.cuda._compile_kernel`
- Hvordan du bygger en nativ C++-kjerneutvidelse med `CUDAExtension` + pybind11, som kan importeres fra Python
<!-- @os:end -->
<!-- @os:linux -->
- Hvordan GPU-kjerner fungerer: grid, blokker, tråder, og indekseringsmodellen som knytter dem til data
- Hvordan AMD ROCm/HIP-stakken lar deg skrive CUDA-lignende kode som kjører på AMD GPU-er uten endringer
- Hvordan du kompilerer en kjerne under kjøring ved hjelp av `torch.cuda._compile_kernel`
- Hvordan du bygger en nativ C++-kjerneutvidelse med `CUDAExtension` + pybind11, som kan importeres fra Python
- Hvordan du måler kjernens kjøretid og overvåker GPU-utnyttelse i sanntid med `amd-smi`
<!-- @os:end -->

---

Denne oppskriften dekker to tilnærminger for kjerneutvikling:

<!-- @os:windows -->
| Tilnærming | Inngangspunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kjerne som en Python-streng, uten byggetrinn |
| **C++-utvidelse** | `CUDAExtension` + pybind11: kompiler en `.cu`-fil til en nativ `.pyd` og importer den |
<!-- @os:end -->
<!-- @os:linux -->
| Tilnærming | Inngangspunkt |
|---|---|
| **JIT-kompilering** | `torch.cuda._compile_kernel`, skriv en kjerne som en Python-streng, uten byggetrinn |
| **C++-utvidelse** | `CUDAExtension` + pybind11: kompiler en `.cu`-fil til en nativ `.so` og importer den |
<!-- @os:end -->

Begge tilnærmingene kjører på AMD GPU-er. Dette er mulig fordi PyTorchs ROCm-bygg kartlegger hele CUDA API-overflaten til HIP. Dette betyr at `torch.cuda`, `CUDAExtension`, og CUDA-kjernesyntaks alle fungerer transparent på AMD-maskinvare.

---

## Bakgrunn

### Hva er en GPU-kjerne?

En GPU-kjerne er en funksjon som kjører parallelt på tusenvis av GPU-tråder samtidig. I motsetning til en CPU-funksjon som utføres én gang per kall, lanseres en kjerne med et **grid** av **blokker**, hver med mange **tråder**, som alle utfører samme kode på forskjellige data.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Trådindekseringsmodell

Når du starter en kjerne, spesifiserer du to dimensjoner:

| Variabel | Betydning |
|---|---|
| `gridDim` | Antall blokker i gridet |
| `blockDim` | Antall tråder per blokk |

Hver tråd har tilgang til tre innebygde, skrivebeskyttede variabler:

| Variabel | Betydning |
|---|---|
| `blockIdx.x` | Hvilken blokk denne tråden tilhører |
| `blockDim.x` | Antall tråder i én blokk |
| `threadIdx.x` | Trådens indeks innenfor sin blokk |

### Global tråd-ID

Disse variablene kombineres for å beregne en globalt unik trådindeks:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Totalt antall tråder = `gridDim.x * blockDim.x`. Hver tråd behandler ett element uavhengig av de andre. Dette er grunnlaget for **dataparallellisme**. Samme operasjon kjøres på mange elementer samtidig, uten avhengighet mellom trådene.

---

### GPU-kjøremodell: Wavefronts

AMD GPU-er utfører tråder i grupper på **32** kalt **wavefronts**. Alle tråder i en wavefront kjører samme instruksjon samtidig. Dette påvirker valg av optimal blokkstørrelse (256 tråder = 8 wavefronts = god planleggingseffektivitet).

### AMD GPU-programmering: HIP + ROCm

**ROCm** er AMDs åpne kildekode-stack for GPU-beregninger (drivere, kompilatorer, biblioteker, kjøretid). **HIP** ligger på toppen, og er designet for å være syntaktisk identisk med CUDA. PyTorchs ROCm-bygg kartlegger transparent `torch.cuda.*` til HIP, slik at samme kode fungerer på AMD GPU-er.

---

### PyTorch + AMD/HIP

PyTorch leverer et ROCm-bygg der CUDA API-overflaten (`torch.cuda.*`) er transparent støttet av HIP. Dette betyr:

- `torch.cuda.is_available()` fungerer på AMD GPU-er med ROCm
- `tensor.to("cuda")` allokerer på AMD GPU-en
- `torch.version.hip` eksponerer HIP-versjonen

PyTorch eksponerer også `torch.cuda._compile_kernel()`, en snarvei på høyt nivå for å JIT-kompilere en rå kjernestreng og få tilbake et kallbart objekt, uten behov for et separat byggetrinn.

---

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Forutsetninger - Windows
- Installer nyeste: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Opprett et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux, åpne en terminal i mappen du ønsker og følg kommandoene for å opprette et venv med ROCm+Pytorch allerede installert.
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
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux, åpne en terminal i mappen du ønsker og følg kommandoene for å opprette et venv.
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
På Windows, åpne en terminal i mappen du ønsker og følg kommandoene for å opprette et venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tips**: Windows-brukere kan trenge å endre PowerShell Execution Policy (f.eks.
> sette den til RemoteSigned eller Unrestricted) før de kjører enkelte PowerShell-kommandoer.

<!-- @os:end -->
### Installere grunnleggende avhengigheter
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
> **Merk:** For denne oppskriften må ROCm og PyTorch installeres i det virtuelle miljøet selv på Ryzen AI Halo, siden kompilering av tilpassede kjerner krever de fullstendige utviklingsheaderne.

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

### Installere ytterligere avhengigheter

<!-- @os:linux -->
Installer verktøykjeden for Linux C/C++-bygging. Dette er en systemnivå-avhengighet og er nødvendig for gjennomgangene av C++-utvidelser fordi `CUDAExtension` bygger native `.so`-moduler fra `.cu`-filer.

Kjør dette én gang på Linux-maskinen, utenfor det opprettede virtuelle Python-miljøet:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Etter at du har aktivert det virtuelle miljøet `kernel-env`, installer Python-byggeavhengighetene:
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
Sørg for at [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) er installert med arbeidsbelastningen **Desktop development with C++**.

> **Merk**: Dette oppsettet av Visual Studio C++-miljøet er kun nødvendig for **C++-utvidelses**-tilnærmingen. Det er ikke nødvendig for JIT-kompileringstilnærmingen.

Åpne en PowerShell-terminal og kjør følgende kommandoer før du bygger C++-utvidelsen.

**Trinn 1: Finn det installerte Visual Studio C++-miljøet**

**(A) Finn `vswhere.exe`, som installeres sammen med Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Finn `vcvars64.bat` fra Visual Studio 2022 eller nyere med C++-byggeverktøy**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Skriv ut Visual Studio C++-miljøet som brukes**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Trinn 2: Aktiver Visual Studio C++-byggemiljøet**

**(A) Kjør `vcvars64.bat` og fang opp miljøet det setter**

Dette gjør `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` og Windows SDK-stier tilgjengelige.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importer Visual Studio-miljøvariablene inn i denne PowerShell-økten**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Trinn 3: Bekreft at Microsoft C++-kompilatoren er tilgjengelig**

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

#### Sett miljøvariabler
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
Bekreft at AMD GPU-en er synlig med:
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

## Last ned nødvendige filer

Opprett følgende mappestruktur ved å lage de **2 nye mappene** og laste ned de tilhørende filene:

| Mappe | Filer å laste ned | Beskrivelse |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- og C++-utvidelsesfiler for vektoraddisjonskjerne |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- og C++-utvidelsesfiler for matrisemultipliseringskjerne |


## Gjennomganger

### Gjennomgang 1: Vektoraddisjon

#### Tilnærming A: JIT-kompilering

JIT-kompilering (Just-In-Time) betyr at kjernen skrives som en rå C++-streng inne i Python og kompileres ved kjøretid, uten behov for ekstra byggetrinn.

For å bruke [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), sørg for at den er lastet ned og kjør:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Viktige kodesnutter**
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
> **Tips**: Skriptet starter også en bakgrunnstråd som spør `amd-smi` hvert 100. millisekund for å logge topp- og gjennomsnittlig GPU-utnyttelse under kjøring av kjernen.
<!-- @os:end -->

> **Merk**: **Hvorfor er blokkstørrelsen 256?** <br>
> - Kjernen bruker **256 tråder per blokk** fordi det passer godt med **wavefront-utførelsesmodellen til AMD GPU-er**.
> - Husk at AMD-maskinvare kjører tråder i grupper på 32 tråder, noe som gir 8 wavefronts per blokk. (8 wavefronts x 32 tråder = 1 blokk)


**Hva arbeidsbelastningen gjør:**

Kjernen legger kunstig til ekstra arbeid for å demonstrere GPU-utnyttelse:

- **100 000 000 elementer** i tensoren
- **Indre løkke kjører 1000 ganger** per element per kjernestart
- **200 kjernestarter** totalt

**Matematikk:**  
- Hvert element: økes med 1 × 1000 iterasjoner × 200 starter = 200 000  
- Sluttresultat: 1,0 (startverdi) + 200 000 (addisjoner) = 200 001,0

**Hvorfor den indre løkken?**  
- Uten løkken `for (int i = 0; i < 1000; i++)` ville 200 starter blitt fullført umiddelbart, og overvåkingsverktøyene ville ikke fanget opp meningsfull GPU-utnyttelse. Det kunstige arbeidet gjør at hver kjernekjøring varer lenge nok til at overvåkingsverktøy kan måle ytelsen.

<!-- @os:linux -->
**Forventet utdata:**[Ytelsestallene vil variere]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Merk**: På Windows støttes ikke `amd-smi`. For å spore GPU-utnyttelse kan du bruke Oppgavebehandling, hvor du bør se en kort topp i utnyttelse når du kjører programmet.

**Forventet utdata:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Godt jobbet! Du har nettopp kjørt din første GPU-kjerne.**

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
#### Metode B: C++-utvidelse

Den andre metoden er mer manuell: skriv kjernen og Python-bindingen til én enkelt `.cu`-fil, kompiler den nativt ved hjelp av PyTorchs byggesystem, og importer den til Python.

<!-- @os:windows -->
> **Merk**: C++-utvidelsesmetoden krever Visual Studio C++-byggemiljøet fordi PyTorch kompilerer `.cu`-kildefilen til en nativ `.pyd`-utvidelsesmodul. Bygging av den native utvidelsen avhenger av Microsoft C++-verktøykjeden (kompilator, lenker og byggeverktøy) levert av Visual Studio. Kjør Visual Studio-aktiveringskommandoene fra oppsettdelen før du bygger utvidelsen.
<!-- @os:end -->

Last ned følgende filer hvis du ikke allerede har gjort det:
<!-- @os:windows -->
| Fil | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kjerne + oppstarter + pybind11-binding, alt i én fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggeskript, bruker `CUDAExtension` for å kompilere `.cu`-filen til en `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skript som kjører de bygde artefaktene |
<!-- @os:end -->

<!-- @os:linux -->
| Fil | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kjerne + oppstarter + pybind11-binding, alt i én fil |
| [setup.py](assets/Vector_Addition/setup.py) | Byggeskript, bruker `CUDAExtension` for å kompilere `.cu`-filen til en `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skript som kjører de bygde artefaktene |
<!-- @os:end -->

#### **Trinn 1: Kjernen, oppstarteren og bindingen** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tips**: Hvorfor bruke `hipDeviceSynchronize()`? <br>
> - GPU-kjernestarter er asynkrone. Når CPU-en kjører `add_one<<<grid_size, block_size>>>(data, n);`, vil den umiddelbart utføre neste instruksjon uten å vente på GPU-en. `hipDeviceSynchronize()` tvinger CPU-en til å vente til GPU-kjernen er ferdig.

#### **Trinn 2: Bygg**
```bash
pip install --no-build-isolation -v .
```
>**Merk**: Denne kommandoen ser etter `setup.py` i gjeldende katalog for å bygge `.cu`-filen vi har opprettet.


`CUDAExtension` er en CUDA-byggehjelper fra `torch.utils.cpp_extension`. Med ROCm **omdirigerer PyTorch `CUDAExtension` til å bruke `hipcc`** i stedet for `nvcc`. ROCm fanger opp byggeprosessen og ruter den gjennom HIP-kompilatoren, og porterer CUDA-koden til AMD.

Dette gir følgende filer:
<!-- @os:windows -->
- `build/`: katalog med `.pyd`-filene
- `add_one_kernel.hip`: HIP-kildekoden generert ved å hipifisere `.cu`-filen; dette er hva `hipcc` faktisk kompilerte
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: katalog med `.so`-filene
- `add_one_kernel.hip`: HIP-kildekoden generert ved å hipifisere `.cu`-filen; dette er hva `hipcc` faktisk kompilerte
<!-- @os:end -->

#### **Trinn 3: Bruk fra Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Kjør dette skriptet for å se kjernen i aksjon:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Forventet utdata:**
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

### Gjennomgang 2: Matrisemultiplikasjon

Matrisemultiplikasjon beregner **C = A × B** der:
- **A** er M×N (rader × kolonner)
- **B** er N×K  
- **C** er M×K (resultatet)

Hvert utdataelement er definert som:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Hvert element i C beregnes uavhengig, noe som gjør dette perfekt for GPU-parallellisme.

#### Hvordan det tilordnes til GPU-tråder

I motsetning til vektoraddisjon (1D), produserer matrisemultiplikasjon **2D-utdata**, så vi bruker et **2D-rutenett av tråder**:

| | Vektoraddisjon | Matrisemultiplikasjon |
|---|---|---|
| **Utdataform** | 1D-matrise | 2D-matrise (M×K) |
| **Trådtilordning** | 1 tråd → 1 element | 1 tråd → 1 utdataelement |
| **Oppstartsmønster** | 1D-rutenett: `(grid_x, 1, 1)` | 2D-rutenett: `(grid_x, grid_y, 1)` |
| **Blokkstørrelse** | `(256, 1, 1)` | `(16, 16, 1)` = 256 tråder |

Hver tråd beregner ett element av utdatamatrisen C. Tråden på posisjon `(row, col)` beregner `C[row][col]` ved å multiplisere den tilsvarende raden i A med den tilsvarende kolonnen i B.

**Minneoppsett**: GPU-minne er flatt (1D), men matriser lagres rad for rad. For å få tilgang til `A[row][col]` bruker kjernen `A[row * N + col]`.


#### Metode A: JIT-kompilering:

Som i gjennomgang 1, er kjernen skrevet som en rå C++-streng inne i Python og kompileres ved kjøretid via PyTorchs innebygde JIT.


For å bruke [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), sørg for at den er lastet ned og kjør:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Viktige kodeutdrag**
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

Skriptet verifiserer resultatet mot `torch.mm` med en liten toleranse. Flyttallsaritmetikk på GPU-er kan produsere små numeriske forskjeller sammenlignet med CPU-implementasjoner på grunn av parallell reduksjonsrekkefølge.

<!-- @os:linux -->
**Forventet utdata:**[Ytelsestallene vil variere]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Merk**: På Windows støttes ikke `amd-smi`. For å spore GPU-utnyttelse kan du bruke Oppgavebehandling, hvor du bør se et kort utslag av utnyttelse når du kjører programmet.

**Forventet utdata:**
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
#### Tilnærming B: C++-utvidelse

Den andre tilnærmingen er mer manuell: skriv kjernen og Python-bindingen til én enkelt `.cu`-fil, kompiler den nativt ved hjelp av PyTorchs byggesystem, og importer den til Python.

<!-- @os:windows -->
> **Merk**: Tilnærmingen med C++-utvidelse krever Visual Studio C++-byggemiljøet fordi PyTorch kompilerer `.cu`-kildefilen til en native `.pyd`-utvidelsesmodul. Bygging av den native utvidelsen avhenger av Microsoft C++-verktøykjeden (kompilator, lenker og byggeverktøy) som følger med Visual Studio. Kjør Visual Studio-aktiveringskommandoene fra oppsettdelen før du bygger utvidelsen.
<!-- @os:end -->

Last ned følgende filer hvis du ikke allerede har gjort det:
<!-- @os:windows -->
| Fil | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kjerne + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggeskript, bruker `CUDAExtension` til å kompilere `.cu`-filen til en `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skript som kjører de bygde artefaktene |
<!-- @os:end -->
<!-- @os:linux -->
| Fil | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kjerne + launcher + pybind11-binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Byggeskript, bruker `CUDAExtension` til å kompilere `.cu`-filen til en `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skript som kjører de bygde artefaktene |
<!-- @os:end -->

#### **Steg 1: Kjernen, launcheren og bindingen** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Sammenlignet med `add_one_launcher` i Gjennomgang 1, gjør launcheren her følgende:
- Tar to inputtensorer i stedet for én
- Utleder alle tre dimensjonene (M, N, K) fra tensorformene, ingen manuell størrelsesoverføring fra Python
- Allokerer og returnerer utdatatensoren C, i stedet for å mutere på plass
- Bruker `dim3` for både grid og block for å uttrykke den 2D-formede oppstarten

#### **Steg 2: Bygg**
```bash
pip install --no-build-isolation -v .
```
>**Merk**: Denne kommandoen ser etter `setup.py` i gjeldende mappe for å bygge `.cu`-filen vi har opprettet.


Dette produserer følgende filer:
<!-- @os:windows -->
- `build/`: mappe med `.pyd`-filene
- `matmul_kernel.hip`: HIP-kildekoden generert ved å hipify-e `.cu`-filen; dette er hva `hipcc` faktisk kompilerte
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: mappe med `.so`-filene
- `matmul_kernel.hip`: HIP-kildekoden generert ved å hipify-e `.cu`-filen; dette er hva `hipcc` faktisk kompilerte
<!-- @os:end -->

#### **Steg 3: Bruk fra Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Kjør dette skriptet for å se kjernen i aksjon:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Forventet utdata:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Bra jobbet! Du har nettopp implementert matrisemultiplikasjon på GPU-en.** Dette er en viktig milepæl fordi matrisemultiplikasjon er ryggraden i moderne maskinlæringsoperasjoner som:
- Nevrale nettverkslag
- Oppmerksomhetsmekanismer (attention)
- Embeddinger
- Transformere

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

## Neste steg

Du har lært å skrive, kompilere og starte GPU-kjerner ved hjelp av både JIT-kompilering og C++-utvidelser for grunnleggende parallelle operasjoner.

**Ytelsesoptimaliseringer:**
- **Shared memory tiling** - Cacher databllokker for å redusere tilgang til globalt minne
- **Minnesammenslåing (memory coalescing)** - Optimaliserer minnetilgangsmønstre for båndbredde

**Virkelige algoritmer:**
- **2D-konvolusjon** - Et lite filter (kjerne) glir over et bilde og beregner hver utdatapiksel fra en vektet sum av nabopiksler. Dette introduserer stencil-beregninger og shared memory tiling, der tråder gjenbruker overlappende bildeområder for å redusere tilgang til globalt minne.
- **Softmax-funksjonen**: Softmax konverterer en vektor med tall til sannsynligheter som summerer til 1, ofte brukt i nevrale nettverksutdata. Å implementere den effektivt på GPU introduserer parallelle reduksjoner og teknikker for numerisk stabilitet ved behandling av store vektorer.

**Produksjonshensyn:**
- **Feilhåndtering** - Grensekontroll og enhetshåndtering
- **PyTorch-integrasjon** - Egendefinerte operatorer med autograd-støtte