<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Kirjoita GPU-kerneli tyhjästä, käännä se, käynnistä se AMD-GPU:lla ja katso, kuinka käyttöaste nousee. Tämä ohjeisto näyttää, miten GPU-laskenta oikeasti toimii: kirjoita kernelikoodi ja suorita se rinnakkain tuhansissa säikeissä.

> **Huomio**: Tämä on melko monimutkainen ohjeisto, joka saattaa vaatia hieman ylimääräistä virheenkorjausta ja muokkauksia.

## Mitä opit

<!-- @os:windows -->
- Miten GPU-kernelit toimivat: gridit, lohkot, säikeet ja indeksointimalli, joka yhdistää ne dataan
- Miten AMD:n ROCm/HIP-pino mahdollistaa CUDA-tyylisen koodin kirjoittamisen, joka toimii AMD-GPU:illa ilman muutoksia
- Miten kerneli käännetään ajonaikaisesti käyttäen komentoa `torch.cuda._compile_kernel`
- Miten rakennetaan natiivi C++-kernelilaajennus käyttäen `CUDAExtension`- ja pybind11-työkaluja, joka on tuotavissa Pythonista
<!-- @os:end -->
<!-- @os:linux -->
- Miten GPU-kernelit toimivat: gridit, lohkot, säikeet ja indeksointimalli, joka yhdistää ne dataan
- Miten AMD:n ROCm/HIP-pino mahdollistaa CUDA-tyylisen koodin kirjoittamisen, joka toimii AMD-GPU:illa ilman muutoksia
- Miten kerneli käännetään ajonaikaisesti käyttäen komentoa `torch.cuda._compile_kernel`
- Miten rakennetaan natiivi C++-kernelilaajennus käyttäen `CUDAExtension`- ja pybind11-työkaluja, joka on tuotavissa Pythonista
- Miten mitataan kernelin suoritusaikaa ja seurataan GPU:n käyttöastetta reaaliajassa `amd-smi`-työkalulla
<!-- @os:end -->

---

Tämä ohjeisto kattaa kaksi lähestymistapaa kernelien kehittämiseen:

<!-- @os:windows -->
| Lähestymistapa | Aloituspiste |
|---|---|
| **JIT-kääntäminen** | `torch.cuda._compile_kernel`, kirjoita kerneli Python-merkkijonona, ilman erillistä koontivaihetta |
| **C++-laajennus** | `CUDAExtension` + pybind11: käännä `.cu`-tiedosto natiiviksi `.pyd`-tiedostoksi ja tuo se |
<!-- @os:end -->
<!-- @os:linux -->
| Lähestymistapa | Aloituspiste |
|---|---|
| **JIT-kääntäminen** | `torch.cuda._compile_kernel`, kirjoita kerneli Python-merkkijonona, ilman erillistä koontivaihetta |
| **C++-laajennus** | `CUDAExtension` + pybind11: käännä `.cu`-tiedosto natiiviksi `.so`-tiedostoksi ja tuo se |
<!-- @os:end -->

Molemmat lähestymistavat toimivat AMD-GPU:illa. Tämä on mahdollista, koska PyTorchin ROCm-versio kuvaa koko CUDA-rajapinnan HIP:iin. Tämä tarkoittaa, että `torch.cuda`, `CUDAExtension` ja CUDA-kernelisyntaksi toimivat kaikki AMD-laitteistolla läpinäkyvästi.

---

## Tausta

### Mikä on GPU-kerneli?

GPU-kerneli on funktio, joka suoritetaan rinnakkain tuhansissa GPU-säikeissä samanaikaisesti. Toisin kuin CPU-funktio, joka suoritetaan kerran per kutsu, kerneli käynnistetään **gridinä**, joka koostuu **lohkoista**, joista jokainen sisältää monta **säiettä**, jotka kaikki suorittavat samaa koodia eri datalla.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Säikeiden indeksointimalli

Kerneliä käynnistettäessä määritetään kaksi ulottuvuutta:

| Muuttuja | Merkitys |
|---|---|
| `gridDim` | Lohkojen määrä gridissä |
| `blockDim` | Säikeiden määrä lohkoa kohti |

Jokaisella säikeellä on pääsy kolmeen sisäänrakennettuun, vain luku -muuttujaan:

| Muuttuja | Merkitys |
|---|---|
| `blockIdx.x` | Mihin lohkoon tämä säie kuuluu |
| `blockDim.x` | Säikeiden määrä yhdessä lohkossa |
| `threadIdx.x` | Säikeen indeksi lohkonsa sisällä |

### Globaali säie-tunniste

Näitä muuttujia yhdistetään globaalisti yksilöllisen säie-indeksin laskemiseksi:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Säikeitä yhteensä = `gridDim.x * blockDim.x`. Jokainen säie käsittelee yhtä elementtiä itsenäisesti. Tämä on **datarinnakkaisuuden** perusta. Sama operaatio suoritetaan monelle elementille kerralla ilman säikeiden välisiä riippuvuuksia.

---

### GPU:n suoritusmalli: Wavefrontit

AMD-GPU:t suorittavat säikeitä **32**:n ryhmissä, joita kutsutaan **wavefronteiksi**. Kaikki wavefrontin säikeet suorittavat samaa käskyä samanaikaisesti. Tämä vaikuttaa optimaalisen lohkokoon valintaan (256 säiettä = 8 wavefronttia = hyvä ajoituustehokkuus).

### AMD-GPU-ohjelmointi: HIP + ROCm

**ROCm** on AMD:n avoimen lähdekoodin GPU-laskentapino (ajurit, kääntäjät, kirjastot, ajonaikainen ympäristö). **HIP** toimii sen päällä ja on suunniteltu syntaktisesti identtiseksi CUDA:n kanssa. PyTorchin ROCm-versio kuvaa `torch.cuda.*`-rajapinnan läpinäkyvästi HIP:iin, joten sama koodi toimii AMD-GPU:illa.

---

### PyTorch + AMD/HIP

PyTorch toimittaa ROCm-version, jossa CUDA-rajapinta (`torch.cuda.*`) on läpinäkyvästi toteutettu HIP:in avulla. Tämä tarkoittaa, että:

- `torch.cuda.is_available()` toimii AMD-GPU:illa ROCm:n kanssa
- `tensor.to("cuda")` varaa muistia AMD-GPU:lta
- `torch.version.hip` paljastaa HIP-version

PyTorch tarjoaa myös funktion `torch.cuda._compile_kernel()`, joka on ylätason oikotie raa'an kernelimerkkijonon JIT-kääntämiseen ja kutsuttavan funktion saamiseen ilman erillistä koontivaihetta.

---

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Esivaatimukset - Windows
- Asenna uusin: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Virtuaaliympäristön luominen

<!-- @os:linux -->
<!-- @device:halo_box -->
Linuxissa avaa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv, jossa ROCm+PyTorch on jo asennettu.
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta tämä astuu voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linuxissa avaa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv.
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
Windowsissa avaa pääte haluamassasi hakemistossa ja seuraa komentoja luodaksesi venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Vihje**: Windows-käyttäjien on ehkä muokattava PowerShellin suorituskäytäntöä (esim.
> asettamalla se arvoon RemoteSigned tai Unrestricted) ennen joidenkin PowerShell-komentojen suorittamista.

<!-- @os:end -->
### Perusriippuvuuksien asentaminen
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
> **Huom:** Tätä ohjekirjaa varten ROCm ja PyTorch on asennettava virtuaaliympäristöön jopa Ryzen AI Halo -laitteessa, sillä mukautettujen kernelien kääntäminen edellyttää täydellisiä kehitysotsikkotiedostoja.

Asenna ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Asenna PyTorch:
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

### Lisäriippuvuuksien asentaminen

<!-- @os:linux -->
Asenna Linuxin C/C++-käännöstyökaluketju. Tämä on järjestelmätason riippuvuus, ja se vaaditaan C++-laajennusesittelyjä varten, koska `CUDAExtension` kääntää natiiveja `.so`-moduuleja `.cu`-tiedostoista.

Suorita tämä kerran Linux-koneella, luodun Python-virtuaaliympäristön ulkopuolella:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Kun olet aktivoinut `kernel-env`-virtuaaliympäristön, asenna Python-käännösriippuvuudet:
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
Varmista, että [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) tai [uudempi](https://visualstudio.microsoft.com/vs/community/) on asennettu **Desktop development with C++** -työtaakalla.

> **Huom**: Tämä Visual Studio C++ -ympäristön asennus vaaditaan vain **C++-laajennus**-lähestymistapaa varten. Sitä ei tarvita JIT-kääntämisen lähestymistavassa.

Avaa PowerShell-pääte ja suorita seuraavat komennot ennen C++-laajennuksen kääntämistä.

**Vaihe 1: Etsi asennettu Visual Studio C++ -ympäristö**

**(A) Paikanna `vswhere.exe`, joka asennetaan Visual Studio Installerin mukana**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Etsi `vcvars64.bat` Visual Studio 2022:sta tai uudemmasta, jossa on C++-käännöstyökalut**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Tulosta käytettävä Visual Studio C++ -ympäristö**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Vaihe 2: Aktivoi Visual Studio C++ -käännösympäristö**

**(A) Suorita `vcvars64.bat` ja tallenna sen asettama ympäristö**

Tämä tekee `cl.exe`-tiedoston, `INCLUDE`-, `LIB`-, `LIBPATH`- ja Windows SDK -polut saataville.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Tuo Visual Studion ympäristömuuttujat tähän PowerShell-istuntoon**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Vaihe 3: Varmista, että Microsoft C++ -kääntäjä on saatavilla**

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

#### Aseta ympäristömuuttujat
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
Varmista, että AMD-GPU on näkyvissä:
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

## Lataa tarvittavat tiedostot

Luo seuraava hakemistorakenne tekemällä **2 uutta kansiota** ja lataamalla vastaavat tiedostot:

| Hakemisto | Ladattavat tiedostot | Kuvaus |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- ja C++-laajennustiedostot vektorien yhteenlaskukernelille |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- ja C++-laajennustiedostot matriisikertolaskukernelille |


## Ohjekirjat

### Ohjekirja 1: Vektorien yhteenlasku

#### Lähestymistapa A: JIT-kääntäminen

JIT (Just-In-Time) -kääntäminen tarkoittaa, että kerneli kirjoitetaan raakana C++-merkkijonona Pythonin sisällä ja käännetään ajon aikana ilman ylimääräisiä käännösvaiheita.

Käyttääksesi tiedostoa [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), varmista, että se on ladattu, ja suorita:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Keskeiset koodinpätkät**
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
> **Vinkki**: Skripti käynnistää myös taustasäikeen, joka kyselee `amd-smi`-komentoa 100 ms:n välein rekisteröidäkseen GPU:n huippu- ja keskimääräisen käytön kernelin ajon aikana.
<!-- @os:end -->

> **Huom**: **Miksi lohkokoko on 256?** <br>
> - Kerneli käyttää **256 säiettä lohkoa kohden**, koska se sopii hyvin yhteen **AMD-GPU:iden wavefront-suoritusmallin** kanssa.
> - Muista, että AMD-laitteisto suorittaa säikeitä 32 säikeen ryhmissä, mikä tuottaa 8 wavefrontia lohkoa kohden. (8 wavefrontia x 32 säiettä = 1 lohko)


**Mitä työkuorma tekee:**

Kerneli lisää keinotekoisesti ylimääräistä työtä osoittaakseen GPU:n käyttöastetta:

- **100 000 000 elementtiä** tensorissa
- **Sisempi silmukka toistuu 1000 kertaa** elementtiä kohden kernelin käynnistystä kohden  
- **200 kernelin käynnistystä** yhteensä

**Matematiikka:**  
- Jokainen elementti: kasvaa arvolla 1 × 1000 iteraatiota × 200 käynnistystä = 200 000  
- Lopputulos: 1,0 (alkuarvo) + 200 000 (lisäykset) = 200 001,0

**Miksi sisempi silmukka?**  
- Ilman `for (int i = 0; i < 1000; i++)` -silmukkaa 200 käynnistystä valmistuisi hetkessä, eivätkä seurantatyökalut ehtisi rekisteröidä merkityksellistä GPU:n käyttöastetta. Keinotekoinen työ saa jokaisen kernelin ajon kestämään riittävän kauan, jotta seurantatyökalut voivat mitata suorituskykyä.

<!-- @os:linux -->
**Odotettu tuloste:**[Suorituskykyluvut vaihtelevat]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Huom**: Windowsissa `amd-smi` ei ole tuettu. GPU:n käyttöastetta voi seurata Tehtävienhallinnasta, jossa pitäisi näkyä lyhyt käyttöasteen piikki ohjelman ajon aikana.

**Odotettu tuloste:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Hienoa työtä! Juuri ajoit ensimmäisen GPU-kernelisi.**

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
#### Lähestymistapa B: C++-laajennos

Toinen lähestymistapa on manuaalisempi: kirjoita ydin (kernel) ja Python-sidos yhteen `.cu`-tiedostoon, käännä se natiivisti PyTorchin build-järjestelmällä ja tuo se Pythoniin.

<!-- @os:windows -->
> **Huom**: C++-laajennos-lähestymistapa vaatii Visual Studio C++ -käännösympäristön, koska PyTorch kääntää `.cu`-lähdetiedoston natiiviksi `.pyd`-laajennosmoduuliksi. Tämän natiivin laajennoksen rakentaminen edellyttää Visual Studion tarjoamaa Microsoft C++ -työkaluketjua (kääntäjä, linkkeri ja build-työkalut). Suorita Visual Studion aktivointikomennot asennusosiosta ennen laajennoksen rakentamista.
<!-- @os:end -->

Lataa seuraavat tiedostot, jos et ole vielä ladannut niitä:
<!-- @os:windows -->
| Tiedosto | Rooli |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ydin + käynnistin + pybind11-sidos, kaikki yhdessä tiedostossa |
| [setup.py](assets/Vector_Addition/setup.py) | Build-skripti, käyttää `CUDAExtension`-luokkaa `.cu`-tiedoston kääntämiseen `.pyd`-muotoon |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skripti, joka suorittaa rakennetut artefaktit |
<!-- @os:end -->

<!-- @os:linux -->
| Tiedosto | Rooli |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Ydin + käynnistin + pybind11-sidos, kaikki yhdessä tiedostossa |
| [setup.py](assets/Vector_Addition/setup.py) | Build-skripti, käyttää `CUDAExtension`-luokkaa `.cu`-tiedoston kääntämiseen `.so`-muotoon |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-skripti, joka suorittaa rakennetut artefaktit |
<!-- @os:end -->

#### **Vaihe 1: Ydin, käynnistin ja sidos** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Vinkki**: Miksi käyttää `hipDeviceSynchronize()`-funktiota? <br>
> - GPU-ytimien käynnistykset ovat asynkronisia. Kun CPU suorittaa rivin `add_one<<<grid_size, block_size>>>(data, n);`, se suorittaisi välittömästi seuraavan käskyn odottamatta GPU:ta. `hipDeviceSynchronize()` pakottaa CPU:n odottamaan, kunnes GPU-ydin on suoritettu loppuun.

#### **Vaihe 2: Käännä**
```bash
pip install --no-build-isolation -v .
```
>**Huom**: Tämä komento etsii `setup.py`-tiedostoa nykyisestä hakemistosta kääntääkseen luomamme .cu-tiedoston.


`CUDAExtension` on `torch.utils.cpp_extension`-moduulin CUDA-käännösapuri. ROCm:n kanssa PyTorch **uudelleenohjaa `CUDAExtension`-luokan käyttämään `hipcc`-kääntäjää** `nvcc`:n sijaan. ROCm sieppaa käännöspolun ja ohjaa sen HIP-kääntäjän kautta, siirtäen CUDA-koodin AMD-laitteille.

Tämä tuottaa seuraavat tiedostot:
<!-- @os:windows -->
- `build/`: hakemisto, jossa `.pyd`-tiedostot sijaitsevat
- `add_one_kernel.hip`: HIP-lähdekoodi, joka on syntynyt `.cu`-tiedoston hipify-muunnoksesta; tämän `hipcc` todellisuudessa kääntää
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: hakemisto, jossa `.so`-tiedostot sijaitsevat
- `add_one_kernel.hip`: HIP-lähdekoodi, joka on syntynyt `.cu`-tiedoston hipify-muunnoksesta; tämän `hipcc` todellisuudessa kääntää
<!-- @os:end -->

#### **Vaihe 3: Käyttö Pythonista** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Suorita tämä skripti nähdäksesi ytimen toiminnassa:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Odotettu tuloste:**
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

### Läpikäynti 2: Matriisikertolasku

Matriisikertolasku laskee **C = A × B**, jossa:
- **A** on M×N (rivejä × sarakkeita)
- **B** on N×K  
- **C** on M×K (tulos)

Jokainen tuloselementti määritellään seuraavasti:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Jokainen C:n elementti lasketaan itsenäisesti, mikä tekee tästä täydellisen GPU-rinnakkaistamiseen.

#### Kuinka se kartoittuu GPU-säikeisiin

Toisin kuin vektorien yhteenlasku (1D), matriisikertolasku tuottaa **2D-tulosteen**, joten käytämme **2D-säiehilaa**:

| | Vektorien yhteenlasku | Matriisikertolasku |
|---|---|---|
| **Tulosteen muoto** | 1D-taulukko | 2D-matriisi (M×K) |
| **Säikeiden kartoitus** | 1 säie → 1 elementti | 1 säie → 1 tuloselementti |
| **Käynnistysmalli** | 1D-hila: `(grid_x, 1, 1)` | 2D-hila: `(grid_x, grid_y, 1)` |
| **Lohkokoko** | `(256, 1, 1)` | `(16, 16, 1)` = 256 säiettä |

Jokainen säie laskee yhden C-tulosmatriisin elementin. Säie sijainnissa `(row, col)` laskee arvon `C[row][col]` kertomalla A:n vastaavan rivin B:n vastaavalla sarakkeella.

**Muistin asettelu**: GPU-muisti on litteä (1D), mutta matriisit tallennetaan rivi kerrallaan. Elementtiin `A[row][col]` päästäksesi ydin käyttää muotoa `A[row * N + col]`.


#### Lähestymistapa A: JIT-käännös:

Kuten Läpikäynnissä 1, ydin kirjoitetaan raakana C++-merkkijonona Pythonin sisällä ja käännetään ajon aikana PyTorchin sisäänrakennetulla JIT-kääntäjällä.


Käyttääksesi tiedostoa [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), varmista että se on ladattu ja suorita:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Keskeiset koodinpätkät**
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

Skripti varmistaa tuloksen vertaamalla sitä funktioon `torch.mm` pienellä toleranssilla. Liukulukuaritmetiikka GPU:illa saattaa tuottaa pieniä numeerisia eroja verrattuna CPU-toteutuksiin rinnakkaisen reduktiojärjestyksen vuoksi.

<!-- @os:linux -->
**Odotettu tuloste:**[Suorituskykyluvut voivat vaihdella]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Huom**: Windowsissa `amd-smi` ei ole tuettu. GPU:n käyttöasteen seuraamiseen voit käyttää Tehtävienhallintaa, jossa pitäisi näkyä lyhyt käyttöasteen piikki, kun suoritat ohjelman.

**Odotettu tuloste:**
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
#### Menetelmä B: C++-laajennus

Toinen menetelmä on manuaalisempi: kirjoita ydin ja Python-sidonta yhteen `.cu`-tiedostoon, käännä se natiivisti PyTorchin käännösjärjestelmällä ja tuo se Pythoniin.

<!-- @os:windows -->
> **Huomautus**: C++-laajennusmenetelmä vaatii Visual Studio C++ -käännösympäristön, koska PyTorch kääntää `.cu`-lähdetiedoston natiiviksi `.pyd`-laajennusmoduuliksi. Tämän natiivin laajennuksen kääntäminen edellyttää Visual Studion tarjoamaa Microsoft C++ -työkaluketjua (kääntäjä, linkittäjä ja käännöstyökalut). Suorita Visual Studion aktivointikomennot asennusosiosta ennen laajennuksen kääntämistä.
<!-- @os:end -->

Lataa seuraavat tiedostot, jos et ole vielä tehnyt niin:
<!-- @os:windows -->
| Tiedosto | Rooli |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ydin + käynnistin + pybind11-sidonta |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Käännösskripti, käyttää `CUDAExtension`-luokkaa `.cu`-tiedoston kääntämiseen `.pyd`-tiedostoksi |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skripti, joka suorittaa käännetyt artefaktit |
<!-- @os:end -->
<!-- @os:linux -->
| Tiedosto | Rooli |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Ydin + käynnistin + pybind11-sidonta |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Käännösskripti, käyttää `CUDAExtension`-luokkaa `.cu`-tiedoston kääntämiseen `.so`-tiedostoksi |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-skripti, joka suorittaa käännetyt artefaktit |
<!-- @os:end -->

#### **Vaihe 1: Ydin, käynnistin ja sidonta** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Verrattuna `add_one_launcher`-toteutukseen läpikäynnissä 1, tämän käynnistimen erot ovat:
- Ottaa kaksi syötetensoria yhden sijaan
- Johtaa kaikki kolme ulottuvuutta (M, N, K) tensorien muodoista, ilman manuaalista koon välittämistä Pythonista
- Allokoi ja palauttaa tulostensorin C sen sijaan, että muokkaisi paikan päällä
- Käyttää `dim3`-tyyppiä sekä ruudukolle että lohkolle ilmaisemaan 2D-käynnistysmuodon

#### **Vaihe 2: Käännä**
```bash
pip install --no-build-isolation -v .
```
>**Huomautus**: Tämä komento etsii `setup.py`-tiedoston nykyisestä hakemistosta kääntääkseen luomamme .cu-tiedoston.


Tämä tuottaa seuraavat tiedostot:
<!-- @os:windows -->
- `build/`: hakemisto, jossa on `.pyd`-tiedostot
- `matmul_kernel.hip`: HIP-lähdekoodi, joka on luotu hipifioimalla `.cu`-tiedosto; tämän `hipcc` todellisuudessa käänsi
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: hakemisto, jossa on `.so`-tiedostot
- `matmul_kernel.hip`: HIP-lähdekoodi, joka on luotu hipifioimalla `.cu`-tiedosto; tämän `hipcc` todellisuudessa käänsi
<!-- @os:end -->

#### **Vaihe 3: Käyttö Pythonista** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Suorita tämä skripti nähdäksesi ytimen toiminnassa:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Odotettu tuloste:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Loistavaa! Juuri toteutit matriisikertolaskun GPU:lla.** Tämä on merkittävä virstanpylväs, sillä matriisikertolasku on modernien koneoppimisoperaatioiden selkäranka, kuten:
- Neuroverkkojen kerrokset
- Attentiomekanismit
- Upotukset (embeddings)
- Transformerit

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

## Seuraavat vaiheet

Olet oppinut kirjoittamaan, kääntämään ja käynnistämään GPU-ytimiä sekä JIT-kääntämisen että C++-laajennusten avulla perustason rinnakkaisoperaatioihin.

**Suorituskykyoptimoinnit:**
- **Jaetun muistin tiilitys (tiling)** - Välimuistita datalohkoja vähentääksesi globaalin muistin käyttöä
- **Muistin yhdistäminen (coalescing)** - Optimoi muistinkäyttömallit kaistanleveyden hyödyntämiseksi

**Todellisen maailman algoritmit:**
- **2D-konvoluutio** - Pieni suodatin (ydin) liukuu kuvan yli ja laskee kunkin tulospikselin naapuripikselien painotettuna summana. Tämä esittelee sabluunalaskennan (stencil computation) ja jaetun muistin tiilityksen, joissa säikeet käyttävät uudelleen päällekkäisiä kuva-alueita globaalin muistin käytön vähentämiseksi.
- **Softmax-funktio**: Softmax muuntaa lukuvektorin todennäköisyyksiksi, joiden summa on 1; sitä käytetään yleisesti neuroverkkojen tulosteissa. Sen tehokas toteuttaminen GPU:lla esittelee rinnakkaiset redusoinnit ja numeerisen vakauden tekniikat suurten vektorien käsittelyssä.

**Tuotantoon liittyvät näkökohdat:**
- **Virheenkäsittely** - Rajatarkistukset ja laitehallinta
- **PyTorch-integraatio** - Mukautetut operaattorit autograd-tuella