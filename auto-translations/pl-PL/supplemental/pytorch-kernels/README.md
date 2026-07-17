<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

Napisz kernel GPU od podstaw, skompiluj go, uruchom na GPU AMD i obserwuj wzrost wykorzystania. Ten playbook pokazuje, jak faktycznie działa obliczanie na GPU: napisz kod kernela i wykonaj go równolegle na tysiącach wątków.

> **Uwaga**: To jest dość złożony playbook, który może wymagać dodatkowego debugowania i modyfikacji.

## Czego się nauczysz

<!-- @os:windows -->
- Jak działają kernele GPU: siatki, bloki, wątki i model indeksowania, który mapuje je na dane
- Jak stos AMD ROCm/HIP pozwala pisać kod w stylu CUDA, który działa na GPU AMD bez modyfikacji
- Jak kompilować kernel w czasie wykonywania przy użyciu `torch.cuda._compile_kernel`
- Jak budować natywne rozszerzenie C++ z `CUDAExtension` + pybind11, importowalne z Pythona
<!-- @os:end -->
<!-- @os:linux -->
- Jak działają kernele GPU: siatki, bloki, wątki i model indeksowania, który mapuje je na dane
- Jak stos AMD ROCm/HIP pozwala pisać kod w stylu CUDA, który działa na GPU AMD bez modyfikacji
- Jak kompilować kernel w czasie wykonywania przy użyciu `torch.cuda._compile_kernel`
- Jak budować natywne rozszerzenie C++ z `CUDAExtension` + pybind11, importowalne z Pythona
- Jak mierzyć czas wykonania kernela i monitorować na żywo wykorzystanie GPU za pomocą `amd-smi`
<!-- @os:end -->

---

Ten playbook obejmuje dwa podejścia do tworzenia kerneli:

<!-- @os:windows -->
| Podejście | Punkt wejścia |
|---|---|
| **Kompilacja JIT** | `torch.cuda._compile_kernel`, napisz kernel jako ciąg znaków w Pythonie, bez kroku budowania |
| **Rozszerzenie C++** | `CUDAExtension` + pybind11: skompiluj plik `.cu` do natywnego `.pyd` i zaimportuj go |
<!-- @os:end -->
<!-- @os:linux -->
| Podejście | Punkt wejścia |
|---|---|
| **Kompilacja JIT** | `torch.cuda._compile_kernel`, napisz kernel jako ciąg znaków w Pythonie, bez kroku budowania |
| **Rozszerzenie C++** | `CUDAExtension` + pybind11: skompiluj plik `.cu` do natywnego `.so` i zaimportuj go |
<!-- @os:end -->

Oba podejścia działają na GPU AMD. Jest to możliwe, ponieważ kompilacja ROCm PyTorch mapuje całą powierzchnię API CUDA na HIP. Oznacza to, że `torch.cuda`, `CUDAExtension` i składnia kerneli CUDA działają na sprzęcie AMD w sposób przezroczysty.

---

## Tło

### Czym jest kernel GPU?

Kernel GPU to funkcja, która działa równolegle na tysiącach wątków GPU jednocześnie. W przeciwieństwie do funkcji CPU, która wykonuje się raz na wywołanie, kernel jest uruchamiany z **siatką** **bloków**, z których każdy zawiera wiele **wątków** — wszystkie wykonują ten sam kod na różnych danych.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Model indeksowania wątków

Podczas uruchamiania kernela określasz dwa wymiary:

| Zmienna | Znaczenie |
|---|---|
| `gridDim` | Liczba bloków w siatce |
| `blockDim` | Liczba wątków na blok |

Każdy wątek ma dostęp do trzech wbudowanych zmiennych tylko do odczytu:

| Zmienna | Znaczenie |
|---|---|
| `blockIdx.x` | Do którego bloku należy ten wątek |
| `blockDim.x` | Liczba wątków w jednym bloku |
| `threadIdx.x` | Indeks wątku w jego bloku |

### Globalny identyfikator wątku

Te zmienne są łączone w celu obliczenia globalnie unikalnego indeksu wątku:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Łączna liczba wątków = `gridDim.x * blockDim.x`. Każdy wątek przetwarza jeden element niezależnie. To jest podstawa **równoległości danych**. Ta sama operacja działa na wielu elementach jednocześnie, bez zależności między wątkami.

---

### Model wykonania GPU: Wavefronty

GPU AMD wykonują wątki w grupach po **32**, zwanych **wavefrontami**. Wszystkie wątki w wavefroncie wykonują tę samą instrukcję jednocześnie. Wpływa to na optymalne wybory rozmiaru bloku (256 wątków = 8 wavefrontów = dobra wydajność harmonogramowania).

### Programowanie GPU AMD: HIP + ROCm

**ROCm** to otwartoźródłowy stos obliczeniowy GPU AMD (sterowniki, kompilatory, biblioteki, środowisko uruchomieniowe). **HIP** znajduje się na wierzchu, zaprojektowany tak, aby być składniowo identyczny z CUDA. Kompilacja ROCm PyTorch w sposób przezroczysty mapuje `torch.cuda.*` na HIP, dzięki czemu ten sam kod działa na GPU AMD.

---

### PyTorch + AMD/HIP

PyTorch dostarcza kompilację ROCm, w której powierzchnia API CUDA (`torch.cuda.*`) jest w sposób przezroczysty obsługiwana przez HIP. Oznacza to:

- `torch.cuda.is_available()` działa na GPU AMD z ROCm
- `tensor.to("cuda")` alokuje na GPU AMD
- `torch.version.hip` udostępnia wersję HIP

PyTorch udostępnia również `torch.cuda._compile_kernel()`, wysokopoziomowy skrót do kompilacji JIT surowego ciągu kernela i uzyskania wywoływalnego obiektu, bez potrzeby oddzielnego kroku budowania.

---

<!-- @device:halo_box -->
## Sprawdź dostępność aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymagań wstępnych oprogramowania
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Wymagania wstępne — Windows
- Zainstaluj najnowszą wersję: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Utwórz środowisko wirtualne

<!-- @os:linux -->
<!-- @device:halo_box -->
W systemie Linux otwórz terminal w wybranym katalogu i postępuj zgodnie z poleceniami, aby utworzyć venv z już zainstalowanym ROCm+PyTorch.
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
**Przyznaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiany weszły w życie):

```bash
sudo usermod -aG render,video $LOGNAME
```

W systemie Linux otwórz terminal w wybranym katalogu i postępuj zgodnie z poleceniami, aby utworzyć venv.
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
W systemie Windows otwórz terminal w wybranym katalogu i postępuj zgodnie z poleceniami, aby utworzyć venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania PowerShell (np.
> ustawić je na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.

<!-- @os:end -->
### Instalowanie podstawowych zależności
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
> **Uwaga:** W przypadku tego poradnika ROCm i PyTorch muszą być zainstalowane w środowisku wirtualnym nawet na Ryzen AI Halo, ponieważ kompilacja niestandardowych jąder wymaga pełnych nagłówków deweloperskich.

Zainstaluj ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Zainstaluj PyTorch:
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

### Instalowanie dodatkowych zależności

<!-- @os:linux -->
Zainstaluj łańcuch narzędzi do budowania C/C++ dla systemu Linux. Jest to zależność systemowa wymagana w przewodnikach dotyczących rozszerzeń C++, ponieważ `CUDAExtension` buduje natywne moduły `.so` z plików `.cu`.

Uruchom to jednorazowo na maszynie z systemem Linux, poza utworzonym wirtualnym środowiskiem Python:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Po aktywowaniu wirtualnego środowiska `kernel-env` zainstaluj zależności Python potrzebne do budowania:
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
Upewnij się, że zainstalowany jest [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) lub [nowszy](https://visualstudio.microsoft.com/vs/community/) z obciążeniem **Programowanie aplikacji klasycznych w języku C++**.

> **Uwaga**: Konfiguracja środowiska C++ dla Visual Studio jest wymagana tylko w przypadku podejścia **Rozszerzenie C++**. Nie jest wymagana w przypadku podejścia z kompilacją JIT.

Otwórz terminal PowerShell i uruchom poniższe polecenia przed zbudowaniem rozszerzenia C++.

**Krok 1: Znajdź zainstalowane środowisko C++ dla Visual Studio**

**(A) Zlokalizuj `vswhere.exe`, który jest instalowany razem z instalatorem Visual Studio**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Znajdź `vcvars64.bat` z Visual Studio 2022 lub nowszego z narzędziami do budowania C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Wyświetl używane środowisko C++ dla Visual Studio**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Krok 2: Aktywuj środowisko budowania C++ dla Visual Studio**

**(A) Uruchom `vcvars64.bat` i przechwyć ustawiane przez niego środowisko**

Dzięki temu dostępne będą `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` oraz ścieżki Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Zaimportuj zmienne środowiskowe Visual Studio do bieżącej sesji PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Krok 3: Sprawdź, czy kompilator Microsoft C++ jest dostępny**

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

#### Ustawianie zmiennych środowiskowych
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
Sprawdź, czy GPU AMD jest widoczny, używając:
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

## Pobieranie wymaganych plików

Utwórz następującą strukturę katalogów, tworząc **2 nowe foldery** i pobierając odpowiednie pliki:

| Katalog | Pliki do pobrania | Opis |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Pliki JIT i rozszerzenia C++ dla jądra dodawania wektorów |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Pliki JIT i rozszerzenia C++ dla jądra mnożenia macierzy |


## Przewodniki

### Przewodnik 1: Dodawanie wektorów

#### Podejście A: Kompilacja JIT

Kompilacja JIT (Just-In-Time) oznacza, że jądro jest zapisane jako surowy ciąg znaków C++ wewnątrz Pythona i kompilowane w czasie wykonywania, bez potrzeby wykonywania dodatkowych kroków budowania.

Aby użyć [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), upewnij się, że plik jest pobrany, i uruchom:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Kluczowe fragmenty kodu**
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
> **Wskazówka**: Skrypt uruchamia również wątek w tle, który co 100 ms odpytuje `amd-smi`, aby rejestrować szczytowe i średnie wykorzystanie GPU podczas działania jądra.
<!-- @os:end -->

> **Uwaga**: **Dlaczego rozmiar bloku wynosi 256?** <br>
> - Jądro używa **256 wątków na blok**, ponieważ dobrze to współgra z **modelem wykonywania wavefront GPU AMD**.
> - Przypomnijmy, że sprzęt AMD wykonuje wątki w grupach po 32 wątki, co daje 8 wavefrontów na blok. (8 wavefrontów × 32 wątki = 1 blok)


**Co robi to obciążenie:**

Jądro sztucznie dodaje dodatkową pracę, aby zademonstrować wykorzystanie GPU:

- **100 000 000 elementów** w tensorze
- **Pętla wewnętrzna wykonuje się 1 000 razy** na element na każde uruchomienie jądra
- **200 uruchomień jądra** łącznie

**Matematyka:**  
- Każdy element: jest zwiększany o 1 × 1 000 iteracji × 200 uruchomień = 200 000  
- Wynik końcowy: 1,0 (wartość początkowa) + 200 000 (dodawania) = 200 001,0

**Po co pętla wewnętrzna?**  
- Bez pętli `for (int i = 0; i < 1000; i++)` 200 uruchomień zakończyłoby się natychmiast, a narzędzia monitorujące nie zarejestrowałyby znaczącego wykorzystania GPU. Sztuczna praca sprawia, że każde uruchomienie jądra trwa wystarczająco długo, aby narzędzia monitorujące mogły zmierzyć wydajność.

<!-- @os:linux -->
**Oczekiwane wyjście:** [Wyniki wydajności mogą się różnić]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: W systemie Windows `amd-smi` nie jest obsługiwany. Aby śledzić wykorzystanie GPU, możesz użyć Menedżera zadań, w którym powinien być widoczny krótki skok wykorzystania podczas uruchamiania programu.

**Oczekiwane wyjście:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Świetna robota! Właśnie uruchomiłeś swoje pierwsze jądro GPU.**

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
#### Podejście B: Rozszerzenie C++

Drugie podejście jest bardziej manualne: napisz kernel i powiązanie Pythona do jednego pliku `.cu`, skompiluj go natywnie przy użyciu systemu budowania PyTorch i zaimportuj do Pythona.

<!-- @os:windows -->
> **Uwaga**: Podejście z rozszerzeniem C++ wymaga środowiska budowania Visual Studio C++, ponieważ PyTorch kompiluje plik źródłowy `.cu` do natywnego modułu rozszerzenia `.pyd`. Budowanie tego natywnego rozszerzenia zależy od łańcucha narzędzi Microsoft C++ (kompilator, linker i narzędzia budowania) dostarczanego przez Visual Studio. Przed budowaniem rozszerzenia uruchom polecenia aktywacji Visual Studio z sekcji konfiguracji.
<!-- @os:end -->

Pobierz następujące pliki, jeśli jeszcze tego nie zrobiłeś:
<!-- @os:windows -->
| Plik | Rola |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + powiązanie pybind11, wszystko w jednym pliku |
| [setup.py](assets/Vector_Addition/setup.py) | Skrypt budowania, używa `CUDAExtension` do kompilacji `.cu` do `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Skrypt Pythona uruchamiający zbudowane artefakty |
<!-- @os:end -->

<!-- @os:linux -->
| Plik | Rola |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + powiązanie pybind11, wszystko w jednym pliku |
| [setup.py](assets/Vector_Addition/setup.py) | Skrypt budowania, używa `CUDAExtension` do kompilacji `.cu` do `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Skrypt Pythona uruchamiający zbudowane artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, launcher i powiązanie** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Wskazówka**: Dlaczego używać `hipDeviceSynchronize()`? <br>
> - Uruchomienia kerneli GPU są asynchroniczne. Gdy CPU wykonuje `add_one<<<grid_size, block_size>>>(data, n);`, natychmiast przechodzi do następnej instrukcji bez oczekiwania na GPU. `hipDeviceSynchronize()` wymusza na CPU oczekiwanie do momentu zakończenia kernela GPU.

#### **Krok 2: Budowanie**
```bash
pip install --no-build-isolation -v .
```
>**Uwaga**: To polecenie szuka `setup.py` w bieżącym katalogu, aby zbudować utworzony przez nas plik .cu.


`CUDAExtension` to pomocnik budowania CUDA z `torch.utils.cpp_extension`. W przypadku ROCm, PyTorch **przekierowuje `CUDAExtension` do używania `hipcc`** zamiast `nvcc`. ROCm przechwytuje ścieżkę budowania i kieruje ją przez kompilator HIP, portując kod CUDA na AMD.

Powoduje to powstanie następujących plików:
<!-- @os:windows -->
- `build/`: katalog z plikami `.pyd`
- `add_one_kernel.hip`: źródło HIP wygenerowane przez hipifikację pliku `.cu`; to właśnie kompiluje `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: katalog z plikami `.so`
- `add_one_kernel.hip`: źródło HIP wygenerowane przez hipifikację pliku `.cu`; to właśnie kompiluje `hipcc`
<!-- @os:end -->

#### **Krok 3: Użycie z Pythona** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Wykonaj ten skrypt, aby zobaczyć kernel w działaniu:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Oczekiwane wyjście:**
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

### Przewodnik 2: Mnożenie macierzy

Mnożenie macierzy oblicza **C = A × B**, gdzie:
- **A** ma wymiary M×N (wiersze × kolumny)
- **B** ma wymiary N×K  
- **C** ma wymiary M×K (wynik)

Każdy element wyjściowy jest zdefiniowany jako:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Każdy element C jest obliczany niezależnie, co czyni to zadanie idealnym dla równoległości GPU.

#### Jak mapuje się na wątki GPU

W przeciwieństwie do dodawania wektorów (1D), mnożenie macierzy produkuje **wyjście 2D**, dlatego używamy **siatki wątków 2D**:

| | Dodawanie wektorów | Mnożenie macierzy |
|---|---|---|
| **Kształt wyjścia** | Tablica 1D | Macierz 2D (M×K) |
| **Mapowanie wątków** | 1 wątek → 1 element | 1 wątek → 1 element wyjściowy |
| **Wzorzec uruchomienia** | Siatka 1D: `(grid_x, 1, 1)` | Siatka 2D: `(grid_x, grid_y, 1)` |
| **Rozmiar bloku** | `(256, 1, 1)` | `(16, 16, 1)` = 256 wątków |

Każdy wątek oblicza jeden element macierzy wyjściowej C. Wątek na pozycji `(row, col)` oblicza `C[row][col]` mnożąc odpowiedni wiersz A przez odpowiednią kolumnę B.

**Układ pamięci**: Pamięć GPU jest płaska (1D), ale macierze są przechowywane wiersz po wierszu. Aby uzyskać dostęp do `A[row][col]`, kernel używa `A[row * N + col]`.


#### Podejście A: Kompilacja JIT:

Podobnie jak w Przewodniku 1, kernel jest zapisany jako surowy ciąg C++ wewnątrz Pythona i kompilowany w czasie wykonania za pomocą wbudowanego JIT PyTorch.


Aby użyć [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), upewnij się, że jest pobrany i uruchom:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Kluczowe fragmenty kodu**
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

Skrypt weryfikuje wynik w porównaniu z `torch.mm` z małą tolerancją. Arytmetyka zmiennoprzecinkowa na GPU może dawać małe różnice numeryczne w porównaniu z implementacjami CPU ze względu na kolejność redukcji równoległej.

<!-- @os:linux -->
**Oczekiwane wyjście:** [Liczby wydajności będą się różnić]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: W systemie Windows `amd-smi` nie jest obsługiwany. Aby śledzić wykorzystanie GPU, możesz użyć Menedżera zadań, gdzie powinieneś zobaczyć krótki skok wykorzystania podczas uruchamiania programu.

**Oczekiwane wyjście:**
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
#### Podejście B: Rozszerzenie C++

Drugie podejście jest bardziej manualne: napisz kernel i powiązanie Pythona do jednego pliku `.cu`, skompiluj go natywnie przy użyciu systemu budowania PyTorch i zaimportuj do Pythona.

<!-- @os:windows -->
> **Uwaga**: Podejście z rozszerzeniem C++ wymaga środowiska budowania Visual Studio C++, ponieważ PyTorch kompiluje plik źródłowy `.cu` do natywnego modułu rozszerzenia `.pyd`. Budowanie tego natywnego rozszerzenia zależy od łańcucha narzędzi Microsoft C++ (kompilator, linker i narzędzia budowania) dostarczanego przez Visual Studio. Przed budowaniem rozszerzenia uruchom polecenia aktywacji Visual Studio z sekcji konfiguracji.
<!-- @os:end -->

Pobierz następujące pliki, jeśli jeszcze tego nie zrobiłeś:
<!-- @os:windows -->
| Plik | Rola |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + powiązanie pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Skrypt budowania, używa `CUDAExtension` do kompilacji `.cu` do `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Skrypt Pythona uruchamiający zbudowane artefakty |
<!-- @os:end -->
<!-- @os:linux -->
| Plik | Rola |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + powiązanie pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Skrypt budowania, używa `CUDAExtension` do kompilacji `.cu` do `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Skrypt Pythona uruchamiający zbudowane artefakty |
<!-- @os:end -->

#### **Krok 1: Kernel, launcher i powiązanie** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

W porównaniu do `add_one_launcher` z Przewodnika 1, launcher tutaj:
- Przyjmuje dwa tensory wejściowe zamiast jednego
- Wyprowadza wszystkie trzy wymiary (M, N, K) z kształtów tensorów, bez ręcznego przekazywania rozmiaru z Pythona
- Alokuje i zwraca wyjściowy tensor C, zamiast modyfikować go w miejscu
- Używa `dim3` zarówno dla siatki, jak i bloku, aby wyrazić dwuwymiarowy kształt uruchomienia

#### **Krok 2: Budowanie**
```bash
pip install --no-build-isolation -v .
```
>**Uwaga**: To polecenie szuka `setup.py` w bieżącym katalogu, aby zbudować utworzony przez nas plik .cu.


Powoduje to powstanie następujących plików:
<!-- @os:windows -->
- `build/`:  katalog z plikami `.pyd`
- `matmul_kernel.hip`:  źródło HIP wygenerowane przez hipifikację pliku `.cu`; to właśnie kompiluje `hipcc`
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  katalog z plikami `.so`
- `matmul_kernel.hip`:  źródło HIP wygenerowane przez hipifikację pliku `.cu`; to właśnie kompiluje `hipcc`
<!-- @os:end -->

#### **Krok 3: Użycie z Pythona** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Wykonaj ten skrypt, aby zobaczyć kernel w działaniu:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Oczekiwane wyjście:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Świetnie! Właśnie zaimplementowałeś mnożenie macierzy na GPU.** To ważny kamień milowy, ponieważ mnożenie macierzy jest podstawą nowoczesnych operacji uczenia maszynowego, takich jak:
- Warstwy sieci neuronowych
- Mechanizmy uwagi
- Osadzenia
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

## Następne kroki

Nauczyłeś się pisać, kompilować i uruchamiać kernele GPU przy użyciu zarówno kompilacji JIT, jak i rozszerzeń C++ dla podstawowych operacji równoległych.

**Optymalizacje wydajności:**
- **Kafelkowanie pamięci współdzielonej** - Buforowanie bloków danych w celu zmniejszenia dostępu do pamięci globalnej
- **Koalescencja pamięci** - Optymalizacja wzorców dostępu do pamięci pod kątem przepustowości

**Algorytmy rzeczywiste:**
- **Splot 2D** - Mały filtr (kernel) przesuwa się po obrazie, obliczając każdy piksel wyjściowy z ważonej sumy sąsiednich pikseli. Wprowadza to obliczenia stencilowe i kafelkowanie pamięci współdzielonej, gdzie wątki ponownie wykorzystują nakładające się obszary obrazu w celu zmniejszenia dostępu do pamięci globalnej.
- **Funkcja Softmax**: Softmax przekształca wektor liczb w prawdopodobieństwa sumujące się do 1, powszechnie stosowane na wyjściach sieci neuronowych. Efektywna implementacja na GPU wprowadza równoległe redukcje i techniki stabilności numerycznej podczas przetwarzania dużych wektorów.

**Zagadnienia produkcyjne:**
- **Obsługa błędów** - Sprawdzanie granic i zarządzanie urządzeniami
- **Integracja z PyTorch** - Niestandardowe operatory z obsługą autograd