<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Napišite jedro GPU od začetka, ga prevedite, zaženite na GPU-ju AMD in opazujte, kako izraba naraste. Ta priročnik prikazuje, kako pravzaprav deluje računanje na GPU-ju: napišete kodo jedra in jo izvedete vzporedno na tisočih niti.

> **Opomba**: To je precej zapleten priročnik, ki lahko zahteva dodatno odpravljanje napak in prilagoditve.

## Kaj se boste naučili

<!-- @os:windows -->
- Kako delujejo jedra GPU: mreže, bloki, niti in model indeksiranja, ki jih preslika na podatke
- Kako sklad AMD ROCm/HIP omogoča pisanje kode v slogu CUDA, ki se izvaja na GPU-jih AMD brez sprememb
- Kako prevesti jedro med izvajanjem z uporabo `torch.cuda._compile_kernel`
- Kako izdelati nativno razširitev jedra v C++ z uporabo `CUDAExtension` + pybind11, ki jo je mogoče uvoziti iz Pythona
<!-- @os:end -->
<!-- @os:linux -->
- Kako delujejo jedra GPU: mreže, bloki, niti in model indeksiranja, ki jih preslika na podatke
- Kako sklad AMD ROCm/HIP omogoča pisanje kode v slogu CUDA, ki se izvaja na GPU-jih AMD brez sprememb
- Kako prevesti jedro med izvajanjem z uporabo `torch.cuda._compile_kernel`
- Kako izdelati nativno razširitev jedra v C++ z uporabo `CUDAExtension` + pybind11, ki jo je mogoče uvoziti iz Pythona
- Kako izmeriti čas izvajanja jedra in spremljati izrabo GPU-ja v živo z `amd-smi`
<!-- @os:end -->

---

Ta priročnik zajema dva pristopa za razvoj jeder:

<!-- @os:windows -->
| Pristop | Vstopna točka |
|---|---|
| **Prevajanje JIT** | `torch.cuda._compile_kernel`, napišite jedro kot niz Python brez koraka gradnje |
| **Razširitev C++** | `CUDAExtension` + pybind11: prevedite datoteko `.cu` v nativno datoteko `.pyd` in jo uvozite |
<!-- @os:end -->
<!-- @os:linux -->
| Pristop | Vstopna točka |
|---|---|
| **Prevajanje JIT** | `torch.cuda._compile_kernel`, napišite jedro kot niz Python brez koraka gradnje |
| **Razširitev C++** | `CUDAExtension` + pybind11: prevedite datoteko `.cu` v nativno datoteko `.so` in jo uvozite |
<!-- @os:end -->

Oba pristopa delujeta na GPU-jih AMD. To je mogoče, ker gradnja PyTorch za ROCm preslika celotno površino API-ja CUDA na HIP. To pomeni, da `torch.cuda`, `CUDAExtension` in sintaksa jeder CUDA vsi delujejo na strojni opremi AMD pregledno.

---

## Ozadje

### Kaj je jedro GPU?

Jedro GPU je funkcija, ki se izvaja vzporedno na tisočih niti GPU-ja hkrati. Za razliko od funkcije CPE-ja, ki se izvede enkrat na klic, se jedro zažene z **mrežo** **blokov**, od katerih vsak vsebuje veliko **niti**, ki vse izvajajo isto kodo na različnih podatkih.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indeksiranja niti

Pri zagonu jedra določite dve dimenziji:

| Spremenljivka | Pomen |
|---|---|
| `gridDim` | Število blokov v mreži |
| `blockDim` | Število niti na blok |

Vsaka nit ima dostop do treh vgrajenih spremenljivk samo za branje:

| Spremenljivka | Pomen |
|---|---|
| `blockIdx.x` | Kateremu bloku pripada ta nit |
| `blockDim.x` | Število niti v enem bloku |
| `threadIdx.x` | Indeks niti znotraj njenega bloka |

### Globalni ID niti

Te spremenljivke se združijo za izračun globalno enoličnega indeksa niti:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Skupno število niti = `gridDim.x * blockDim.x`. Vsaka nit neodvisno obdela en element. To je temelj **podatkovne vzporednosti**. Ista operacija se izvaja na veliko elementih hkrati, brez medsebojne odvisnosti niti.

---

### Model izvajanja GPU: valovne fronte (wavefronts)

GPU-ji AMD izvajajo niti v skupinah po **32**, imenovanih **valovne fronte (wavefronts)**. Vse niti v valovni fronti izvajajo isti ukaz hkrati. To vpliva na izbiro optimalne velikosti bloka (256 niti = 8 valovnih front = dobra učinkovitost razporejanja).

### Programiranje GPU-ja AMD: HIP + ROCm

**ROCm** je odprtokodni sklad za računanje na GPU-ju podjetja AMD (gonilniki, prevajalniki, knjižnice, izvajalno okolje). **HIP** deluje na vrhu tega sklada in je zasnovan tako, da je sintaktično enak CUDA. Gradnja PyTorch za ROCm pregledno preslika `torch.cuda.*` na HIP, tako da ista koda deluje na GPU-jih AMD.

---

### PyTorch + AMD/HIP

PyTorch ponuja gradnjo za ROCm, kjer je površina API-ja CUDA (`torch.cuda.*`) pregledno podprta s HIP. To pomeni:

- `torch.cuda.is_available()` deluje na GPU-jih AMD z ROCm
- `tensor.to("cuda")` dodeli pomnilnik na GPU-ju AMD
- `torch.version.hip` razkrije različico HIP

PyTorch prav tako ponuja `torch.cuda._compile_kernel()`, hitrejšo bližnjico za prevajanje JIT surovega niza jedra in pridobitev klicljivega objekta, brez potrebe po ločenem koraku gradnje.

---

<!-- @device:halo_box -->
## Preverite posodobitve programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Predpogoji - Windows
- Namestite najnovejšo različico: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Ustvarite virtualno okolje

<!-- @os:linux -->
<!-- @device:halo_box -->
V Linuxu odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv) z že nameščenima ROCm+Pytorch.
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
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se morate odjaviti in ponovno prijaviti):

```bash
sudo usermod -aG render,video $LOGNAME
```

V Linuxu odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
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
V sistemu Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti pravilnik izvajanja PowerShell (Execution Policy) (npr.
> nastaviti ga na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze PowerShell.

<!-- @os:end -->
### Namestitev osnovnih odvisnosti
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
> **Opomba:** Za ta priročnik je treba ROCm in PyTorch namestiti v virtualno okolje tudi na Ryzen AI Halo, saj kompilacija prilagojenih jeder zahteva popolne razvojne glave (headers).

Namestite ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Namestite PyTorch:
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

### Namestitev dodatnih odvisnosti

<!-- @os:linux -->
Namestite Linux C/C++ orodno verigo za gradnjo. To je odvisnost na sistemski ravni in je potrebna za vodiče po razširitvah C++, ker `CUDAExtension` zgradi izvorne module `.so` iz datotek `.cu`.

To zaženite enkrat na Linux računalniku, izven ustvarjenega virtualnega okolja Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktivaciji virtualnega okolja `kernel-env` namestite odvisnosti za gradnjo Python:
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
Prosimo, poskrbite, da je nameščen [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ali [novejši](https://visualstudio.microsoft.com/vs/community/) z delovnim obremenitvijo **Desktop development with C++**.

> **Opomba**: Ta nastavitev okolja Visual Studio C++ je potrebna samo za pristop **C++ Extension**. Za pristop JIT Compilation ni potrebna.

Odprite terminal PowerShell in pred gradnjo razširitve C++ zaženite naslednje ukaze.

**Korak 1: Poiščite nameščeno okolje Visual Studio C++**

**(A) Poiščite `vswhere.exe`, ki se namesti z Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Poiščite `vcvars64.bat` iz Visual Studio 2022 ali novejšega z orodji za gradnjo C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Izpišite okolje Visual Studio C++, ki se uporablja**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Korak 2: Aktivirajte okolje za gradnjo Visual Studio C++**

**(A) Zaženite `vcvars64.bat` in zajemite okolje, ki ga nastavi**

To omogoči dostop do `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` in poti Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Uvozite spremenljivke okolja Visual Studio v to sejo PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Korak 3: Preverite, ali je prevajalnik Microsoft C++ na voljo**

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

#### Nastavite spremenljivke okolja
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
Preverite, ali je AMD GPU viden z ukazom:
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

## Prenos zahtevanih datotek

Ustvarite naslednjo strukturo map tako, da ustvarite **2 novi mapi** in prenesete ustrezne datoteke:

| Mapa | Datoteke za prenos | Opis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Datoteke JIT in C++ extension za jedro seštevanja vektorjev |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Datoteke JIT in C++ extension za jedro množenja matrik |


## Vodiči po korakih

### Vodič po korakih 1: Seštevanje vektorjev

#### Pristop A: JIT Compilation

JIT (Just-In-Time) kompilacija pomeni, da je jedro napisano kot surov niz C++ znotraj Python in prevedeno med izvajanjem, brez potrebe po dodatnih korakih gradnje.

Za uporabo [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) se prepričajte, da je prenesen, in zaženite:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Ključni izsečki kode**
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
> **Nasvet**: Skripta prav tako sproži ozadnjo nit, ki vsakih 100 ms poizveduje `amd-smi`, da beleži najvišjo in povprečno izkoriščenost GPU med izvajanjem jedra.
<!-- @os:end -->

> **Opomba**: **Zakaj je velikost bloka 256?** <br>
> - Jedro uporablja **256 niti na blok**, ker se dobro ujema z **modelom izvajanja wavefront na AMD GPU-jih**.
> - Ne pozabite, da strojna oprema AMD izvaja niti v skupinah po 32 niti, kar rezultira v 8 wavefrontih na blok. (8 wavefrontov x 32 niti = 1 blok)


**Kaj naredi delovna obremenitev:**

Jedro umetno doda dodatno delo za prikaz izkoriščenosti GPU:

- **100.000.000 elementov** v tenzorju
- **Notranja zanka se izvede 1.000-krat** na element ob vsakem zagonu jedra
- Skupno **200 zagonov jedra**

**Matematika:**  
- Vsak element: se poveča za 1 × 1.000 iteracij × 200 zagonov = 200.000  
- Končni rezultat: 1,0 (začetna vrednost) + 200.000 (seštevanja) = 200001,0

**Zakaj notranja zanka?**  
- Brez zanke `for (int i = 0; i < 1000; i++)` bi se 200 zagonov zaključilo takoj, orodja za spremljanje pa ne bi zajela smiselne izkoriščenosti GPU. Umetno delo poskrbi, da vsak zagon jedra traja dovolj dolgo, da lahko orodja za spremljanje izmerijo zmogljivost.

<!-- @os:linux -->
**Pričakovan izpis:**[Vrednosti zmogljivosti se bodo razlikovale]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: V sistemu Windows `amd-smi` ni podprt. Za spremljanje izkoriščenosti GPU lahko uporabite Upravitelja opravil, kjer bi morali ob zagonu programa videti kratek skok izkoriščenosti.

**Pričakovan izpis:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Odlično opravljeno! Pravkar ste zagnali svoje prvo jedro GPU.**

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
#### Pristop B: razširitev C++

Drugi pristop je bolj ročen: jedro in Python-vezavo zapišete v eno samo datoteko `.cu`, jo prevedete izvorno z uporabo PyTorch-ovega sistema za gradnjo in jo uvozite v Python.

<!-- @os:windows -->
> **Opomba**: pristop z razširitvijo C++ zahteva razvojno okolje Visual Studio C++, ker PyTorch prevede izvorno datoteko `.cu` v izvorni razširitveni modul `.pyd`. Gradnja tega izvornega razširitvenega modula je odvisna od Microsoftove verige orodij C++ (prevajalnik, povezovalnik in orodja za gradnjo), ki jih zagotavlja Visual Studio. Pred gradnjo razširitve zaženite ukaze za aktivacijo Visual Studia iz razdelka o nastavitvi.
<!-- @os:end -->

Prenesite naslednje datoteke, če jih še niste:
<!-- @os:windows -->
| Datoteka | Vloga |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Jedro + zaganjalnik + vezava pybind11, vse v eni datoteki |
| [setup.py](assets/Vector_Addition/setup.py) | Skripta za gradnjo, uporablja `CUDAExtension` za prevajanje datoteke `.cu` v `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skripta, ki zažene zgrajene artefakte |
<!-- @os:end -->

<!-- @os:linux -->
| Datoteka | Vloga |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Jedro + zaganjalnik + vezava pybind11, vse v eni datoteki |
| [setup.py](assets/Vector_Addition/setup.py) | Skripta za gradnjo, uporablja `CUDAExtension` za prevajanje datoteke `.cu` v `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python skripta, ki zažene zgrajene artefakte |
<!-- @os:end -->

#### **Korak 1: Jedro, zaganjalnik in vezava** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Nasvet**: zakaj uporabiti `hipDeviceSynchronize()`? <br>
> - Zagoni jeder GPE so asinhroni. Ko CPE zažene `add_one<<<grid_size, block_size>>>(data, n);`, bi takoj izvedel naslednji ukaz, ne da bi počakal na GPE. `hipDeviceSynchronize()` prisili CPE, da počaka, dokler se jedro GPE ne dokonča.

#### **Korak 2: Gradnja**
```bash
pip install --no-build-isolation -v .
```
>**Opomba**: ta ukaz išče `setup.py` v trenutnem imeniku, da bi zgradil ustvarjeno datoteko .cu.


`CUDAExtension` je pomočnik za gradnjo CUDA iz `torch.utils.cpp_extension`. Pri ROCm PyTorch **preusmeri `CUDAExtension`, da uporablja `hipcc`** namesto `nvcc`. ROCm prestreže pot gradnje in jo usmeri skozi prevajalnik HIP, s čimer prenese kodo CUDA na AMD.

To ustvari naslednje datoteke:
<!-- @os:windows -->
- `build/`: imenik z datotekami `.pyd`
- `add_one_kernel.hip`: izvorna koda HIP, ustvarjena s hipifikacijo datoteke `.cu`; to je tisto, kar je `hipcc` dejansko prevedel
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: imenik z datotekami `.so`
- `add_one_kernel.hip`: izvorna koda HIP, ustvarjena s hipifikacijo datoteke `.cu`; to je tisto, kar je `hipcc` dejansko prevedel
<!-- @os:end -->

#### **Korak 3: Uporaba iz Pythona** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Izvedite to skripto, da vidite jedro v akciji:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Pričakovani izpis:**
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

### Vodič 2: Množenje matrik

Množenje matrik izračuna **C = A × B**, kjer:
- **A** je M×N (vrstice × stolpci)
- **B** je N×K  
- **C** je M×K (rezultat)

Vsak izhodni element je definiran kot:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Vsak element matrike C se izračuna neodvisno, zaradi česar je to idealno za paralelizem GPE.

#### Kako se to preslika na niti GPE

Za razliko od seštevanja vektorjev (1D), množenje matrik ustvari **2D izhod**, zato uporabimo **2D mrežo niti**:

| | Seštevanje vektorjev | Množenje matrik |
|---|---|---|
| **Oblika izhoda** | 1D polje | 2D matrika (M×K) |
| **Preslikava niti** | 1 nit → 1 element | 1 nit → 1 izhodni element |
| **Vzorec zagona** | 1D mreža: `(grid_x, 1, 1)` | 2D mreža: `(grid_x, grid_y, 1)` |
| **Velikost bloka** | `(256, 1, 1)` | `(16, 16, 1)` = 256 niti |

Vsaka nit izračuna en element izhodne matrike C. Nit na položaju `(row, col)` izračuna `C[row][col]` z množenjem ustrezne vrstice A z ustreznim stolpcem B.

**Postavitev pomnilnika**: pomnilnik GPE je ravninski (1D), vendar so matrike shranjene vrstico za vrstico. Za dostop do `A[row][col]` jedro uporabi `A[row * N + col]`.


#### Pristop A: pravočasno prevajanje (JIT):

Tako kot pri vodiču 1 je jedro zapisano kot surov niz C++ znotraj Pythona in prevedeno ob izvajanju prek vgrajenega JIT-a PyTorch.


Za uporabo datoteke [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) se prepričajte, da je prenesena, in zaženite:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Ključni odlomki kode**
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

Skripta preveri rezultat glede na `torch.mm` z majhno toleranco. Aritmetika s plavajočo vejico na GPE lahko povzroči majhne numerične razlike v primerjavi z izvedbami na CPE zaradi vrstnega reda paralelne redukcije.

<!-- @os:linux -->
**Pričakovani izpis:** [Zmogljivostne številke se bodo razlikovale]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: v operacijskem sistemu Windows `amd-smi` ni podprt. Za spremljanje izkoriščenosti GPE lahko uporabite Upravitelja opravil, kjer bi morali ob zagonu programa videti kratek skok izkoriščenosti.

**Pričakovani izpis:**
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
#### Pristop B: Razširitev C++

Drugi pristop je bolj ročen: kodo jedra in Python vezavo zapišete v eno samo datoteko `.cu`, jo prevedete izvorno z uporabo PyTorchevega gradbenega sistema in jo uvozite v Python.

<!-- @os:windows -->
> **Opomba**: Pristop z razširitvijo C++ zahteva gradbeno okolje Visual Studio C++, ker PyTorch prevede izvorno datoteko `.cu` v izvorni razširitveni modul `.pyd`. Gradnja tega izvornega modula je odvisna od orodne verige Microsoft C++ (prevajalnika, povezovalnika in gradbenih orodij), ki jih zagotavlja Visual Studio. Pred gradnjo razširitve zaženite ukaze za aktivacijo Visual Studia iz razdelka o namestitvi.
<!-- @os:end -->

Če tega še niste storili, prenesite naslednje datoteke:
<!-- @os:windows -->
| Datoteka | Vloga |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Jedro + zaganjalnik + pybind11 vezava |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Gradbeni skript, ki uporablja `CUDAExtension` za prevod `.cu` v `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, ki zažene zgrajene artefakte |
<!-- @os:end -->
<!-- @os:linux -->
| Datoteka | Vloga |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Jedro + zaganjalnik + pybind11 vezava |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Gradbeni skript, ki uporablja `CUDAExtension` za prevod `.cu` v `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python skript, ki zažene zgrajene artefakte |
<!-- @os:end -->

#### **Korak 1: Jedro, zaganjalnik in vezava** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

V primerjavi z `add_one_launcher` iz Vodiča po korakih 1 zaganjalnik tukaj:
- Sprejme dva vhodna tenzorja namesto enega
- Izpelje vse tri dimenzije (M, N, K) iz oblik tenzorjev, brez ročnega posredovanja velikosti iz Pythona
- Dodeli in vrne izhodni tenzor C, namesto da bi ga spreminjal na mestu
- Za mrežo in blok uporablja `dim3`, da izrazi 2D obliko zagona

#### **Korak 2: Gradnja**
```bash
pip install --no-build-isolation -v .
```
>**Opomba**: Ta ukaz za gradnjo ustvarjene datoteke `.cu` v trenutnem imeniku poišče `setup.py`.


To ustvari naslednje datoteke:
<!-- @os:windows -->
- `build/`:  imenik z datotekami `.pyd`
- `matmul_kernel.hip`:  izvorna koda HIP, ustvarjena s pretvorbo (hipify) datoteke `.cu`; to je tisto, kar je `hipcc` dejansko prevedel
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  imenik z datotekami `.so`
- `matmul_kernel.hip`:  izvorna koda HIP, ustvarjena s pretvorbo (hipify) datoteke `.cu`; to je tisto, kar je `hipcc` dejansko prevedel
<!-- @os:end -->

#### **Korak 3: Uporaba iz Pythona** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Zaženite ta skript, da vidite jedro v akciji:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Pričakovan izpis:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Odlično! Pravkar ste implementirali množenje matrik na GPU-ju.** To je pomemben mejnik, saj je množenje matrik hrbtenica sodobnih operacij strojnega učenja, kot so:
- Sloji nevronskih mrež
- Mehanizmi pozornosti
- Vdelave (embeddings)
- Transformerji

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

## Naslednji koraki

Naučili ste se pisati, prevajati in zaganjati jedra GPU z uporabo tako sprotnega (JIT) prevajanja kot razširitev C++ za osnovne vzporedne operacije.

**Optimizacije zmogljivosti:**
- **Tlakovanje s souporabljenim pomnilnikom (shared memory tiling)** - Predpomnenje blokov podatkov za zmanjšanje dostopa do globalnega pomnilnika
- **Zlivanje pomnilniških dostopov (memory coalescing)** - Optimizacija vzorcev dostopa do pomnilnika za pasovno širino

**Algoritmi iz resničnega sveta:**
- **2D konvolucija** - Majhen filter (jedro) drsi po sliki in izračuna vsak izhodni piksel kot uteženo vsoto sosednjih pikslov. To uvede stencil izračune in tlakovanje s souporabljenim pomnilnikom, kjer niti ponovno uporabljajo prekrivajoča se območja slike za zmanjšanje dostopa do globalnega pomnilnika.
- **Funkcija Softmax**: Softmax pretvori vektor števil v verjetnosti, ki se seštejejo v 1, kar se pogosto uporablja pri izhodih nevronskih mrež. Učinkovita implementacija na GPU-ju uvede vzporedne redukcije in tehnike numerične stabilnosti pri obdelavi velikih vektorjev.

**Preudarki za produkcijsko uporabo:**
- **Obravnava napak** - Preverjanje mej in upravljanje naprav
- **Integracija s PyTorch** - Operatorji po meri s podporo za avtomatski odvod (autograd)