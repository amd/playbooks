<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Übersicht

Schreiben Sie einen GPU-Kernel von Grund auf, kompilieren Sie ihn, starten Sie ihn auf einer AMD GPU und beobachten Sie, wie die Auslastung ansteigt. Dieses Playbook zeigt, wie GPU-Berechnungen tatsächlich funktionieren: Schreiben Sie den Kernel-Code und führen Sie ihn parallel über Tausende von Threads aus.

> **Hinweis**: Dies ist ein recht komplexes Playbook, das möglicherweise zusätzliches Debugging und Anpassungen erfordert.

## Was Sie lernen werden

<!-- @os:windows -->
- Wie GPU-Kernel funktionieren: Grids, Blöcke, Threads und das Indexierungsmodell, das sie Daten zuordnet
- Wie der AMD ROCm/HIP-Stack es Ihnen ermöglicht, CUDA-ähnlichen Code zu schreiben, der ohne Änderungen auf AMD GPUs läuft
- Wie man einen Kernel zur Laufzeit mit `torch.cuda._compile_kernel` kompiliert
- Wie man eine native C++-Kernel-Erweiterung mit `CUDAExtension` + pybind11 erstellt, die aus Python importiert werden kann
<!-- @os:end -->
<!-- @os:linux -->
- Wie GPU-Kernel funktionieren: Grids, Blöcke, Threads und das Indexierungsmodell, das sie Daten zuordnet
- Wie der AMD ROCm/HIP-Stack es Ihnen ermöglicht, CUDA-ähnlichen Code zu schreiben, der ohne Änderungen auf AMD GPUs läuft
- Wie man einen Kernel zur Laufzeit mit `torch.cuda._compile_kernel` kompiliert
- Wie man eine native C++-Kernel-Erweiterung mit `CUDAExtension` + pybind11 erstellt, die aus Python importiert werden kann
- Wie man die Kernel-Ausführungszeit misst und die Live-GPU-Auslastung mit `amd-smi` überwacht
<!-- @os:end -->

---

Dieses Playbook behandelt zwei Ansätze für die Kernel-Entwicklung:

<!-- @os:windows -->
| Ansatz | Einstiegspunkt |
|---|---|
| **JIT-Kompilierung** | `torch.cuda._compile_kernel`, einen Kernel als Python-String schreiben, ohne Build-Schritt |
| **C++-Erweiterung** | `CUDAExtension` + pybind11: eine `.cu`-Datei in eine native `.pyd` kompilieren und importieren |
<!-- @os:end -->
<!-- @os:linux -->
| Ansatz | Einstiegspunkt |
|---|---|
| **JIT-Kompilierung** | `torch.cuda._compile_kernel`, einen Kernel als Python-String schreiben, ohne Build-Schritt |
| **C++-Erweiterung** | `CUDAExtension` + pybind11: eine `.cu`-Datei in eine native `.so` kompilieren und importieren |
<!-- @os:end -->

Beide Ansätze laufen auf AMD GPUs. Dies ist möglich, weil PyTorchs ROCm-Build die gesamte CUDA-API-Oberfläche auf HIP abbildet. Das bedeutet, dass `torch.cuda`, `CUDAExtension` und die CUDA-Kernel-Syntax alle transparent auf AMD-Hardware funktionieren.

---

## Hintergrund

### Was ist ein GPU-Kernel?

Ein GPU-Kernel ist eine Funktion, die parallel über Tausende von GPU-Threads gleichzeitig ausgeführt wird. Im Gegensatz zu einer CPU-Funktion, die pro Aufruf einmal ausgeführt wird, wird ein Kernel mit einem **Grid** aus **Blöcken** gestartet, die jeweils viele **Threads** enthalten, die alle denselben Code auf unterschiedlichen Daten ausführen.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Thread-Indexierungsmodell

Beim Starten eines Kernels geben Sie zwei Dimensionen an:

| Variable | Bedeutung |
|---|---|
| `gridDim` | Anzahl der Blöcke im Grid |
| `blockDim` | Anzahl der Threads pro Block |

Jeder Thread hat Zugriff auf drei eingebaute schreibgeschützte Variablen:

| Variable | Bedeutung |
|---|---|
| `blockIdx.x` | Zu welchem Block dieser Thread gehört |
| `blockDim.x` | Anzahl der Threads in einem Block |
| `threadIdx.x` | Thread-Index innerhalb seines Blocks |

### Globale Thread-ID

Diese Variablen werden kombiniert, um einen global eindeutigen Thread-Index zu berechnen:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Gesamtanzahl der Threads = `gridDim.x * blockDim.x`. Jeder Thread verarbeitet ein Element unabhängig. Dies ist die Grundlage der **Datenparallelität**. Dieselbe Operation wird auf vielen Elementen gleichzeitig ausgeführt, ohne Abhängigkeiten zwischen Threads.

---

### GPU-Ausführungsmodell: Wavefronts

AMD GPUs führen Threads in Gruppen von **32** aus, die **Wavefronts** genannt werden. Alle Threads in einer Wavefront führen dieselbe Anweisung gleichzeitig aus. Dies beeinflusst die optimale Wahl der Blockgröße (256 Threads = 8 Wavefronts = gute Scheduling-Effizienz).

### AMD GPU-Programmierung: HIP + ROCm

**ROCm** ist AMDs Open-Source-GPU-Compute-Stack (Treiber, Compiler, Bibliotheken, Laufzeit). **HIP** baut darauf auf und ist syntaktisch identisch mit CUDA. PyTorchs ROCm-Build bildet `torch.cuda.*` transparent auf HIP ab, sodass derselbe Code auf AMD GPUs funktioniert.

---

### PyTorch + AMD/HIP

PyTorch liefert einen ROCm-Build, bei dem die CUDA-API-Oberfläche (`torch.cuda.*`) transparent durch HIP unterstützt wird. Das bedeutet:

- `torch.cuda.is_available()` funktioniert auf AMD GPUs mit ROCm
- `tensor.to("cuda")` allokiert auf der AMD GPU
- `torch.version.hip` gibt die HIP-Version aus

PyTorch stellt auch `torch.cuda._compile_kernel()` bereit, eine High-Level-Abkürzung zum JIT-Kompilieren eines rohen Kernel-Strings und zum Zurückgeben eines aufrufbaren Objekts, ohne einen separaten Build-Schritt zu benötigen.

---

<!-- @device:halo_box -->
## Auf Software-Updates prüfen

<!-- @require:software-update -->
<!-- @device:end -->

## Software-Voraussetzungen installieren
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Voraussetzungen - Windows
- Neueste Version installieren: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Eine virtuelle Umgebung erstellen

<!-- @os:linux -->
<!-- @device:halo_box -->
Öffnen Sie unter Linux ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv mit bereits installiertem ROCm+PyTorch zu erstellen.
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
**Gewähren Sie Ihrem Benutzer Zugriff auf GPU-Geräte** (melden Sie sich ab und wieder an, damit dies wirksam wird):

```bash
sudo usermod -aG render,video $LOGNAME
```

Öffnen Sie unter Linux ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
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
Öffnen Sie unter Windows ein Terminal im Verzeichnis Ihrer Wahl und folgen Sie den Befehlen, um eine venv zu erstellen.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Tipp**: Windows-Benutzer müssen möglicherweise ihre PowerShell-Ausführungsrichtlinie anpassen (z. B.
> auf RemoteSigned oder Unrestricted setzen), bevor sie einige PowerShell-Befehle ausführen.

<!-- @os:end -->
### Installieren grundlegender Abhängigkeiten
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
> **Hinweis:** Für dieses Playbook müssen ROCm und PyTorch auch auf dem Ryzen AI Halo in die virtuelle Umgebung installiert werden, da die Kompilierung benutzerdefinierter Kernel die vollständigen Entwicklungs-Header erfordert.

ROCm installieren:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorch installieren:
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

### Installieren zusätzlicher Abhängigkeiten

<!-- @os:linux -->
Installieren Sie die Linux-C/C++-Build-Toolchain. Dies ist eine Abhängigkeit auf Systemebene und wird für die C++-Erweiterungs-Walkthroughs benötigt, da `CUDAExtension` native `.so`-Module aus `.cu`-Dateien erstellt.

Führen Sie dies einmalig auf dem Linux-Rechner aus, außerhalb der erstellten virtuellen Python-Umgebung:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Nach dem Aktivieren der virtuellen Umgebung `kernel-env` installieren Sie die Python-Build-Abhängigkeiten:
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
Bitte stellen Sie sicher, dass [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) oder [neuer](https://visualstudio.microsoft.com/vs/community/) mit der Workload **Desktopentwicklung mit C++** installiert ist.

> **Hinweis**: Diese Einrichtung der Visual Studio-C++-Umgebung ist nur für den **C++-Erweiterungs**-Ansatz erforderlich. Für den JIT-Kompilierungsansatz ist sie nicht erforderlich.

Öffnen Sie ein PowerShell-Terminal und führen Sie die folgenden Befehle aus, bevor Sie die C++-Erweiterung erstellen.

**Schritt 1: Die installierte Visual Studio-C++-Umgebung finden**

**(A) `vswhere.exe` suchen, das mit dem Visual Studio Installer installiert wird**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) `vcvars64.bat` aus Visual Studio 2022 oder neuer mit C++-Build-Tools finden**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Die verwendete Visual Studio-C++-Umgebung ausgeben**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Schritt 2: Die Visual Studio-C++-Build-Umgebung aktivieren**

**(A) `vcvars64.bat` ausführen und die gesetzten Umgebungsvariablen erfassen**

Dadurch werden `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` und Windows-SDK-Pfade verfügbar gemacht.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Die Visual Studio-Umgebungsvariablen in diese PowerShell-Sitzung importieren**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Schritt 3: Überprüfen, ob der Microsoft-C++-Compiler verfügbar ist**

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

#### Umgebungsvariablen festlegen
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
Überprüfen Sie, ob die AMD GPU sichtbar ist, mit:
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

## Erforderliche Dateien herunterladen

Erstellen Sie die folgende Verzeichnisstruktur, indem Sie die **2 neuen Ordner** anlegen und die entsprechenden Dateien herunterladen:

| Verzeichnis | Herunterzuladende Dateien | Beschreibung |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| JIT- und C++-Erweiterungsdateien für den Vektoradditions-Kernel |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | JIT- und C++-Erweiterungsdateien für den Matrixmultiplikations-Kernel |


## Walkthroughs

### Walkthrough 1: Vektoraddition

#### Ansatz A: JIT-Kompilierung

JIT-Kompilierung (Just-In-Time) bedeutet, dass der Kernel als roher C++-String innerhalb von Python geschrieben und zur Laufzeit kompiliert wird, ohne dass zusätzliche Build-Schritte erforderlich sind.

Um [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) zu verwenden, stellen Sie sicher, dass die Datei heruntergeladen wurde, und führen Sie aus:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Wichtige Code-Ausschnitte**
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
> **Tipp**: Das Skript startet außerdem einen Hintergrund-Thread, der alle 100 ms `amd-smi` abfragt, um die maximale und durchschnittliche GPU-Auslastung während des Kernel-Laufs zu protokollieren.
<!-- @os:end -->

> **Hinweis**: **Warum ist die Blockgröße 256?** <br>
> - Der Kernel verwendet **256 Threads pro Block**, da dies gut mit dem **Wavefront-Ausführungsmodell von AMD GPUs** übereinstimmt.
> - Zur Erinnerung: AMD-Hardware führt Threads in Gruppen von 32 Threads aus, was zu 8 Wavefronts pro Block führt. (8 Wavefronts × 32 Threads = 1 Block)


**Was die Workload tut:**

Der Kernel fügt künstlich zusätzliche Arbeit hinzu, um die GPU-Auslastung zu demonstrieren:

- **100.000.000 Elemente** im Tensor
- **Innere Schleife läuft 1.000 Mal** pro Element pro Kernel-Start  
- **200 Kernel-Starts** insgesamt

**Mathematik:**  
- Jedes Element: wird um 1 × 1.000 Iterationen × 200 Starts = 200.000 erhöht  
- Endergebnis: 1,0 (Startwert) + 200.000 (Additionen) = 200.001,0

**Warum die innere Schleife?**  
- Ohne die `for (int i = 0; i < 1000; i++)`-Schleife würden 200 Starts sofort abgeschlossen sein und die Überwachungstools würden keine aussagekräftige GPU-Auslastung erfassen. Die künstliche Arbeit lässt jeden Kernel-Lauf lang genug dauern, damit Überwachungstools die Leistung messen können.

<!-- @os:linux -->
**Erwartete Ausgabe:** [Die Leistungswerte können variieren]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Unter Windows wird `amd-smi` nicht unterstützt. Um die GPU-Auslastung zu verfolgen, können Sie den Task-Manager verwenden, in dem Sie beim Ausführen des Programms einen kurzen Auslastungsspike sehen sollten.

**Erwartete Ausgabe:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Gut gemacht! Sie haben soeben Ihren ersten GPU-Kernel ausgeführt.**

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
#### Ansatz B: C++ Extension

Der zweite Ansatz ist manueller: Schreiben Sie den Kernel und die Python-Bindung in eine einzige `.cu`-Datei, kompilieren Sie diese nativ mit PyTorchs Build-System und importieren Sie sie in Python.

<!-- @os:windows -->
> **Hinweis**: Der C++ Extension-Ansatz erfordert die Visual Studio C++ Build-Umgebung, da PyTorch die `.cu`-Quelldatei in ein natives `.pyd`-Erweiterungsmodul kompiliert. Das Erstellen dieser nativen Erweiterung hängt von der Microsoft C++ Toolchain (Compiler, Linker und Build-Tools) ab, die von Visual Studio bereitgestellt wird. Führen Sie die Visual Studio-Aktivierungsbefehle aus dem Setup-Abschnitt aus, bevor Sie die Erweiterung erstellen.
<!-- @os:end -->

Laden Sie die folgenden Dateien herunter, falls noch nicht geschehen:
<!-- @os:windows -->
| Datei | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + Launcher + pybind11-Bindung, alles in einer Datei |
| [setup.py](assets/Vector_Addition/setup.py) | Build-Skript, verwendet `CUDAExtension` zum Kompilieren der `.cu` in eine `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-Skript, das die erstellten Artefakte ausführt |
<!-- @os:end -->

<!-- @os:linux -->
| Datei | Rolle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + Launcher + pybind11-Bindung, alles in einer Datei |
| [setup.py](assets/Vector_Addition/setup.py) | Build-Skript, verwendet `CUDAExtension` zum Kompilieren der `.cu` in eine `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python-Skript, das die erstellten Artefakte ausführt |
<!-- @os:end -->

#### **Schritt 1: Der Kernel, Launcher und die Bindung** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Tipp**: Warum `hipDeviceSynchronize()` verwenden? <br>
> - GPU-Kernel-Starts sind asynchron. Wenn die CPU `add_one<<<grid_size, block_size>>>(data, n);` ausführt, würde sie sofort die nächste Anweisung ausführen, ohne auf die GPU zu warten. `hipDeviceSynchronize()` zwingt die CPU zu warten, bis der GPU-Kernel abgeschlossen ist.

#### **Schritt 2: Erstellen**
```bash
pip install --no-build-isolation -v .
```
>**Hinweis**: Dieser Befehl sucht nach `setup.py` im aktuellen Verzeichnis, um die von uns erstellte .cu-Datei zu kompilieren.


`CUDAExtension` ist ein CUDA-Build-Hilfsprogramm aus `torch.utils.cpp_extension`. Mit ROCm **ordnet PyTorch `CUDAExtension` so um, dass `hipcc`** anstelle von `nvcc` verwendet wird. ROCm fängt den Build-Pfad ab und leitet ihn durch den HIP-Compiler, wodurch CUDA-Code auf AMD portiert wird.

Dies erzeugt die folgenden Dateien:
<!-- @os:windows -->
- `build/`: Verzeichnis mit den `.pyd`-Dateien
- `add_one_kernel.hip`: die durch Hipifizierung der `.cu`-Datei generierte HIP-Quelle; dies ist das, was `hipcc` tatsächlich kompiliert hat
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: Verzeichnis mit den `.so`-Dateien
- `add_one_kernel.hip`: die durch Hipifizierung der `.cu`-Datei generierte HIP-Quelle; dies ist das, was `hipcc` tatsächlich kompiliert hat
<!-- @os:end -->

#### **Schritt 3: Verwendung aus Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Führen Sie dieses Skript aus, um den Kernel in Aktion zu sehen:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Erwartete Ausgabe:**
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

### Durchgang 2: Matrizenmultiplikation

Die Matrizenmultiplikation berechnet **C = A × B**, wobei:
- **A** M×N ist (Zeilen × Spalten)
- **B** N×K ist  
- **C** M×K ist (das Ergebnis)

Jedes Ausgabeelement ist definiert als:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Jedes Element von C wird unabhängig berechnet, was dies ideal für GPU-Parallelismus macht.

#### Zuordnung zu GPU-Threads

Im Gegensatz zur Vektoraddition (1D) erzeugt die Matrizenmultiplikation eine **2D-Ausgabe**, daher verwenden wir ein **2D-Gitter von Threads**:

| | Vektoraddition | Matrizenmultiplikation |
|---|---|---|
| **Ausgabeform** | 1D-Array | 2D-Matrix (M×K) |
| **Thread-Zuordnung** | 1 Thread → 1 Element | 1 Thread → 1 Ausgabeelement |
| **Startmuster** | 1D-Gitter: `(grid_x, 1, 1)` | 2D-Gitter: `(grid_x, grid_y, 1)` |
| **Blockgröße** | `(256, 1, 1)` | `(16, 16, 1)` = 256 Threads |

Jeder Thread berechnet ein Element der Ausgabematrix C. Der Thread an Position `(row, col)` berechnet `C[row][col]`, indem er die entsprechende Zeile von A mit der entsprechenden Spalte von B multipliziert.

**Speicherlayout**: GPU-Speicher ist flach (1D), aber Matrizen werden zeilenweise gespeichert. Um auf `A[row][col]` zuzugreifen, verwendet der Kernel `A[row * N + col]`.


#### Ansatz A: JIT-Kompilierung:

Wie in Durchgang 1 wird der Kernel als roher C++-String innerhalb von Python geschrieben und zur Laufzeit über PyTorchs integrierten JIT kompiliert.


Um [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) zu verwenden, stellen Sie sicher, dass es heruntergeladen ist, und führen Sie aus:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Wichtige Code-Ausschnitte**
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

Das Skript überprüft das Ergebnis gegen `torch.mm` mit einer kleinen Toleranz. Gleitkomma-Arithmetik auf GPUs kann im Vergleich zu CPU-Implementierungen kleine numerische Unterschiede erzeugen, bedingt durch die Reihenfolge der parallelen Reduktion.

<!-- @os:linux -->
**Erwartete Ausgabe:** [Die Leistungszahlen können variieren]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Unter Windows wird `amd-smi` nicht unterstützt. Um die GPU-Auslastung zu verfolgen, können Sie den Task-Manager verwenden, in dem Sie beim Ausführen des Programms einen kurzen Auslastungsspike sehen sollten.

**Erwartete Ausgabe:**
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
#### Ansatz B: C++-Erweiterung

Der zweite Ansatz ist manueller: Schreiben Sie den Kernel und die Python-Bindung in eine einzige `.cu`-Datei, kompilieren Sie diese nativ mit PyTorchs Build-System und importieren Sie sie in Python.

<!-- @os:windows -->
> **Hinweis**: Der C++-Erweiterungsansatz erfordert die Visual Studio C++-Build-Umgebung, da PyTorch die `.cu`-Quelldatei in ein natives `.pyd`-Erweiterungsmodul kompiliert. Das Erstellen dieser nativen Erweiterung hängt von der Microsoft C++-Toolchain (Compiler, Linker und Build-Tools) ab, die von Visual Studio bereitgestellt wird. Führen Sie die Visual Studio-Aktivierungsbefehle aus dem Setup-Abschnitt aus, bevor Sie die Erweiterung erstellen.
<!-- @os:end -->

Laden Sie die folgenden Dateien herunter, falls Sie dies noch nicht getan haben:
<!-- @os:windows -->
| Datei | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + Launcher + pybind11-Bindung |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build-Skript, verwendet `CUDAExtension` zum Kompilieren der `.cu` in eine `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-Skript, das die erstellten Artefakte ausführt |
<!-- @os:end -->
<!-- @os:linux -->
| Datei | Rolle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + Launcher + pybind11-Bindung |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build-Skript, verwendet `CUDAExtension` zum Kompilieren der `.cu` in eine `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python-Skript, das die erstellten Artefakte ausführt |
<!-- @os:end -->

#### **Schritt 1: Der Kernel, Launcher und die Bindung** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Im Vergleich zu `add_one_launcher` in Walkthrough 1 führt der Launcher hier Folgendes aus:
- Nimmt zwei Eingabe-Tensoren statt einem entgegen
- Leitet alle drei Dimensionen (M, N, K) aus den Tensor-Formen ab, ohne manuelles Übergeben der Größe aus Python
- Allokiert und gibt den Ausgabe-Tensor C zurück, anstatt ihn direkt zu verändern
- Verwendet `dim3` sowohl für Grid als auch Block, um die 2D-Launch-Form auszudrücken

#### **Schritt 2: Erstellen**
```bash
pip install --no-build-isolation -v .
```
>**Hinweis**: Dieser Befehl sucht nach `setup.py` im aktuellen Verzeichnis, um die von uns erstellte .cu-Datei zu kompilieren.


Dies erzeugt die folgenden Dateien:
<!-- @os:windows -->
- `build/`:  Verzeichnis mit den `.pyd`-Dateien
- `matmul_kernel.hip`:  die durch Hipifizierung der `.cu`-Datei generierte HIP-Quelle; dies ist das, was `hipcc` tatsächlich kompiliert hat
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  Verzeichnis mit den `.so`-Dateien
- `matmul_kernel.hip`:  die durch Hipifizierung der `.cu`-Datei generierte HIP-Quelle; dies ist das, was `hipcc` tatsächlich kompiliert hat
<!-- @os:end -->

#### **Schritt 3: Verwendung aus Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Führen Sie dieses Skript aus, um den Kernel in Aktion zu sehen:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Erwartete Ausgabe:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Großartig! Sie haben soeben Matrizenmultiplikation auf der GPU implementiert.** Dies ist ein wichtiger Meilenstein, da Matrizenmultiplikation das Fundament moderner Machine-Learning-Operationen wie der folgenden bildet:
- Neuronale Netzwerkschichten
- Aufmerksamkeitsmechanismen
- Einbettungen
- Transformer

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

## Nächste Schritte

Sie haben gelernt, GPU-Kernel mithilfe von JIT-Kompilierung und C++-Erweiterungen für grundlegende Paralleloperationen zu schreiben, zu kompilieren und zu starten.

**Leistungsoptimierungen:**
- **Shared-Memory-Tiling** – Datenblocke zwischenspeichern, um den Zugriff auf den globalen Speicher zu reduzieren
- **Memory Coalescing** – Speicherzugriffsmuster für Bandbreite optimieren

**Reale Algorithmen:**
- **2D-Faltung** – Ein kleiner Filter (Kernel) gleitet über ein Bild und berechnet jeden Ausgabepixel aus einer gewichteten Summe benachbarter Pixel. Dies führt Stencil-Berechnungen und Shared-Memory-Tiling ein, bei denen Threads überlappende Bildbereiche wiederverwenden, um den globalen Speicherzugriff zu reduzieren.
- **Softmax-Funktion**: Softmax wandelt einen Vektor von Zahlen in Wahrscheinlichkeiten um, die sich zu 1 summieren, und wird häufig in neuronalen Netzwerkausgaben verwendet. Eine effiziente Implementierung auf der GPU führt parallele Reduktionen und Techniken zur numerischen Stabilität ein, während große Vektoren verarbeitet werden.

**Produktionsüberlegungen:**
- **Fehlerbehandlung** – Bereichsprüfung und Geräteverwaltung
- **PyTorch-Integration** – Benutzerdefinierte Operatoren mit Autograd-Unterstützung