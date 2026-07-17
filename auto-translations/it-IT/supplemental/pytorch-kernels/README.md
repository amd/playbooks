<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

Scrivi un kernel GPU da zero, compilalo, avvialo su una GPU AMD e osserva l'utilizzo aumentare. Questo playbook mostra come funziona effettivamente il calcolo GPU: scrivi il codice del kernel ed eseguilo in parallelo su migliaia di thread.

> **Nota**: Questo è un playbook piuttosto complesso, che potrebbe richiedere debug aggiuntivo e modifiche.

## Cosa Imparerai

<!-- @os:windows -->
- Come funzionano i kernel GPU: griglie, blocchi, thread e il modello di indicizzazione che li mappa ai dati
- Come lo stack AMD ROCm/HIP ti permette di scrivere codice in stile CUDA che gira su GPU AMD senza modifiche
- Come compilare un kernel a runtime usando `torch.cuda._compile_kernel`
- Come costruire un'estensione kernel C++ nativa con `CUDAExtension` + pybind11, importabile da Python
<!-- @os:end -->
<!-- @os:linux -->
- Come funzionano i kernel GPU: griglie, blocchi, thread e il modello di indicizzazione che li mappa ai dati
- Come lo stack AMD ROCm/HIP ti permette di scrivere codice in stile CUDA che gira su GPU AMD senza modifiche
- Come compilare un kernel a runtime usando `torch.cuda._compile_kernel`
- Come costruire un'estensione kernel C++ nativa con `CUDAExtension` + pybind11, importabile da Python
- Come misurare il tempo di esecuzione del kernel e monitorare l'utilizzo live della GPU con `amd-smi`
<!-- @os:end -->

---

Questo playbook copre due approcci per lo sviluppo di kernel:

<!-- @os:windows -->
| Approccio | Punto di ingresso |
|---|---|
| **Compilazione JIT** | `torch.cuda._compile_kernel`, scrivi un kernel come stringa Python, senza passaggi di build |
| **Estensione C++** | `CUDAExtension` + pybind11: compila un file `.cu` in un `.pyd` nativo e importalo |
<!-- @os:end -->
<!-- @os:linux -->
| Approccio | Punto di ingresso |
|---|---|
| **Compilazione JIT** | `torch.cuda._compile_kernel`, scrivi un kernel come stringa Python, senza passaggi di build |
| **Estensione C++** | `CUDAExtension` + pybind11: compila un file `.cu` in un `.so` nativo e importalo |
<!-- @os:end -->

Entrambi gli approcci funzionano su GPU AMD. Ciò è possibile perché la build ROCm di PyTorch mappa l'intera superficie API CUDA su HIP. Questo significa che `torch.cuda`, `CUDAExtension` e la sintassi dei kernel CUDA funzionano tutti su hardware AMD in modo trasparente.

---

## Contesto

### Cos'è un Kernel GPU?

Un kernel GPU è una funzione che viene eseguita in parallelo su migliaia di thread GPU simultaneamente. A differenza di una funzione CPU che viene eseguita una volta per chiamata, un kernel viene avviato con una **griglia** di **blocchi**, ciascuno contenente molti **thread**, tutti che eseguono lo stesso codice su dati diversi.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Modello di Indicizzazione dei Thread

Quando si avvia un kernel si specificano due dimensioni:

| Variabile | Significato |
|---|---|
| `gridDim` | Numero di blocchi nella griglia |
| `blockDim` | Numero di thread per blocco |

Ogni thread ha accesso a tre variabili built-in di sola lettura:

| Variabile | Significato |
|---|---|
| `blockIdx.x` | A quale blocco appartiene questo thread |
| `blockDim.x` | Numero di thread in un blocco |
| `threadIdx.x` | Indice del thread all'interno del suo blocco |

### ID Thread Globale

Queste variabili vengono combinate per calcolare un indice thread univoco a livello globale:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Il totale dei thread è `gridDim.x * blockDim.x`. Ogni thread elabora un elemento in modo indipendente. Questa è la base del **parallelismo dei dati**. La stessa operazione viene eseguita su molti elementi contemporaneamente, senza dipendenze tra thread.

---

### Modello di Esecuzione GPU: Wavefront

Le GPU AMD eseguono i thread in gruppi di **32** chiamati **wavefront**. Tutti i thread in un wavefront eseguono la stessa istruzione simultaneamente. Questo influisce sulle scelte ottimali della dimensione del blocco (256 thread = 8 wavefront = buona efficienza di scheduling).

### Programmazione GPU AMD: HIP + ROCm

**ROCm** è lo stack di calcolo GPU open-source di AMD (driver, compilatori, librerie, runtime). **HIP** si trova sopra, progettato per essere sintatticamente identico a CUDA. La build ROCm di PyTorch mappa in modo trasparente `torch.cuda.*` su HIP, quindi lo stesso codice funziona su GPU AMD.

---

### PyTorch + AMD/HIP

PyTorch include una build ROCm in cui la superficie API CUDA (`torch.cuda.*`) è supportata in modo trasparente da HIP. Questo significa:

- `torch.cuda.is_available()` funziona su GPU AMD con ROCm
- `tensor.to("cuda")` alloca sulla GPU AMD
- `torch.version.hip` espone la versione HIP

PyTorch espone anche `torch.cuda._compile_kernel()`, una scorciatoia di alto livello per compilare JIT una stringa di kernel grezza e ottenere un callable, senza necessità di un passaggio di build separato.

---

<!-- @device:halo_box -->
## Verifica Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Prerequisiti - Windows
- Installa l'ultima versione: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Crea un Ambiente Virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv con ROCm+Pytorch già installato.
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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra per rendere effettiva la modifica):

```bash
sudo usermod -aG render,video $LOGNAME
```

Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
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
Su Windows, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Suggerimento**: Gli utenti Windows potrebbero dover modificare la PowerShell Execution Policy (ad es.
> impostandola su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi PowerShell.

<!-- @os:end -->


### Installazione delle Dipendenze di Base
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
> **Nota:** Per questo playbook, ROCm e PyTorch devono essere installati nell'ambiente virtuale anche su Ryzen AI Halo, poiché la compilazione di kernel personalizzati richiede gli header di sviluppo completi.

Installa ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Installa PyTorch:
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

### Installazione delle Dipendenze Aggiuntive

<!-- @os:linux -->
Installa la toolchain di build C/C++ per Linux. Questa è una dipendenza a livello di sistema ed è richiesta per le procedure guidate dell'estensione C++ perché `CUDAExtension` costruisce moduli `.so` nativi da file `.cu`.

Esegui questo comando una volta sulla macchina Linux, al di fuori dell'ambiente virtuale Python creato:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Dopo aver attivato l'ambiente virtuale `kernel-env`, installa le dipendenze Python di build:
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
Assicurati che [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [versione più recente](https://visualstudio.microsoft.com/vs/community/) sia installato con il carico di lavoro **Sviluppo desktop con C++**.

> **Nota**: Questa configurazione dell'ambiente C++ di Visual Studio è richiesta solo per l'approccio **Estensione C++**. Non è richiesta per l'approccio Compilazione JIT.

Apri un terminale PowerShell ed esegui i seguenti comandi prima di costruire l'estensione C++.

**Passaggio 1: Trova l'ambiente C++ di Visual Studio installato**

**(A) Individua `vswhere.exe`, che viene installato con il Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Trova `vcvars64.bat` da Visual Studio 2022 o versione più recente con gli strumenti di build C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Stampa l'ambiente C++ di Visual Studio in uso**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Passaggio 2: Attiva l'ambiente di build C++ di Visual Studio**

**(A) Esegui `vcvars64.bat` e cattura l'ambiente che imposta**

Questo rende disponibili `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` e i percorsi Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importa le variabili d'ambiente di Visual Studio in questa sessione PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Passaggio 3: Verifica che il compilatore Microsoft C++ sia disponibile**

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

#### Imposta le Variabili d'Ambiente
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
Verifica che la GPU AMD sia visibile con:
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

## Scarica i File Necessari

Crea la seguente struttura di directory creando le **2 nuove cartelle** e scaricando i file corrispondenti:

| Directory | File da Scaricare | Descrizione |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| File JIT e di estensione C++ per il kernel di addizione vettoriale |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | File JIT e di estensione C++ per il kernel di moltiplicazione matriciale |


## Procedure Guidate

### Procedura Guidata 1: Addizione Vettoriale

#### Approccio A: Compilazione JIT

La compilazione JIT (Just-In-Time) significa che il kernel è scritto come stringa C++ grezza all'interno di Python e compilato a runtime, senza necessità di passaggi di build aggiuntivi.

Per usare [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), assicurati che sia scaricato ed esegui:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Frammenti di Codice Chiave**
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
> **Suggerimento**: Lo script avvia anche un thread in background che interroga `amd-smi` ogni 100ms per registrare l'utilizzo massimo e medio della GPU durante l'esecuzione del kernel.
<!-- @os:end -->

> **Nota**: **Perché la dimensione del blocco è 256?** <br>
> - Il kernel usa **256 thread per blocco** perché si allinea bene con il **modello di esecuzione wavefront delle GPU AMD**.
> - Ricorda che l'hardware AMD esegue i thread in gruppi di 32 thread, risultando in 8 wavefront per blocco. (8 wavefront x 32 thread = 1 blocco)


**Cosa fa il carico di lavoro:**

Il kernel aggiunge artificialmente lavoro extra per dimostrare l'utilizzo della GPU:

- **100.000.000 di elementi** nel tensore
- **Il ciclo interno viene eseguito 1.000 volte** per elemento per ogni avvio del kernel
- **200 avvii del kernel** in totale

**Matematica:**  
- Ogni elemento: viene incrementato di 1 × 1.000 iterazioni × 200 avvii = 200.000  
- Risultato finale: 1,0 (valore iniziale) + 200.000 (addizioni) = 200.001,0

**Perché il ciclo interno?**  
- Senza il ciclo `for (int i = 0; i < 1000; i++)`, 200 avvii terminerebbero istantaneamente e gli strumenti di monitoraggio non catturerebbero un utilizzo significativo della GPU. Il lavoro artificiale rende ogni esecuzione del kernel abbastanza lunga da consentire agli strumenti di monitoraggio di misurare le prestazioni.

<!-- @os:linux -->
**Output atteso:**[I numeri di prestazione varieranno]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Su Windows, `amd-smi` non è supportato. Per monitorare l'utilizzo della GPU, puoi usare Task Manager, dove dovresti vedere un breve picco di utilizzo quando esegui il programma.

**Output atteso:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Ottimo lavoro! Hai appena eseguito il tuo primo kernel GPU.**

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

#### Approccio B: Estensione C++

Il secondo approccio è più manuale: scrivi il kernel e il binding Python in un singolo file `.cu`, compilalo nativamente usando il sistema di build di PyTorch e importalo in Python.

<!-- @os:windows -->
> **Nota**: L'approccio Estensione C++ richiede l'ambiente di build C++ di Visual Studio perché PyTorch compila il file sorgente `.cu` in un modulo di estensione nativo `.pyd`. La costruzione di tale estensione nativa dipende dalla toolchain Microsoft C++ (compilatore, linker e strumenti di build) fornita da Visual Studio. Esegui i comandi di attivazione di Visual Studio dalla sezione di configurazione prima di costruire l'estensione.
<!-- @os:end -->

Scarica i seguenti file se non lo hai già fatto:
<!-- @os:windows -->
| File | Ruolo |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + binding pybind11, tutto in un unico file |
| [setup.py](assets/Vector_Addition/setup.py) | Script di build, usa `CUDAExtension` per compilare il `.cu` in un `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python che esegue gli artefatti costruiti |
<!-- @os:end -->

<!-- @os:linux -->
| File | Ruolo |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + binding pybind11, tutto in un unico file |
| [setup.py](assets/Vector_Addition/setup.py) | Script di build, usa `CUDAExtension` per compilare il `.cu` in un `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python che esegue gli artefatti costruiti |
<!-- @os:end -->

#### **Passaggio 1: Il kernel, il launcher e il binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Suggerimento**: Perché usare `hipDeviceSynchronize()`? <br>
> - Gli avvii del kernel GPU sono asincroni. Quando la CPU esegue `add_one<<<grid_size, block_size>>>(data, n);` eseguirebbe immediatamente l'istruzione successiva senza attendere la GPU. `hipDeviceSynchronize()` forza la CPU ad attendere fino al completamento del kernel GPU.

#### **Passaggio 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Nota**: Questo comando cerca `setup.py` nella directory corrente per costruire il file .cu che abbiamo creato.


`CUDAExtension` è un helper di build CUDA da `torch.utils.cpp_extension`. Con ROCm, PyTorch **rimappa `CUDAExtension` per usare `hipcc`** invece di `nvcc`. ROCm intercetta il percorso di build e lo instrada attraverso il compilatore HIP, portando il codice CUDA su AMD.

Questo produce i seguenti file:
<!-- @os:windows -->
- `build/`:  directory con i file `.pyd`
- `add_one_kernel.hip`:  il sorgente HIP generato dall'hipificazione del file `.cu`; questo è ciò che `hipcc` ha effettivamente compilato
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory con i file `.so`
- `add_one_kernel.hip`:  il sorgente HIP generato dall'hipificazione del file `.cu`; questo è ciò che `hipcc` ha effettivamente compilato
<!-- @os:end -->

#### **Passaggio 3: Usa da Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Esegui questo script per vedere il kernel in azione:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Output atteso:**
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

### Procedura Guidata 2: Moltiplicazione Matriciale

La moltiplicazione matriciale calcola **C = A × B** dove:
- **A** è M×N (righe × colonne)
- **B** è N×K  
- **C** è M×K (il risultato)

Ogni elemento di output è definito come:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Ogni elemento di C viene calcolato in modo indipendente, rendendo questo perfetto per il parallelismo GPU.

#### Come Si Mappa ai Thread GPU

A differenza dell'addizione vettoriale (1D), la moltiplicazione matriciale produce un **output 2D**, quindi usiamo una **griglia 2D di thread**:

| | Addizione Vettoriale | Moltiplicazione Matriciale |
|---|---|---|
| **Forma dell'output** | Array 1D | Matrice 2D (M×K) |
| **Mappatura thread** | 1 thread → 1 elemento | 1 thread → 1 elemento di output |
| **Schema di avvio** | Griglia 1D: `(grid_x, 1, 1)` | Griglia 2D: `(grid_x, grid_y, 1)` |
| **Dimensione blocco** | `(256, 1, 1)` | `(16, 16, 1)` = 256 thread |

Ogni thread calcola un elemento della matrice di output C. Il thread in posizione `(row, col)` calcola `C[row][col]` moltiplicando la riga corrispondente di A con la colonna corrispondente di B.

**Layout di Memoria**: La memoria GPU è piatta (1D), ma le matrici sono memorizzate riga per riga. Per accedere a `A[row][col]`, il kernel usa `A[row * N + col]`.


#### Approccio A: Compilazione JIT:

Come nella Procedura Guidata 1, il kernel è scritto come stringa C++ grezza all'interno di Python e compilato a runtime tramite il JIT integrato di PyTorch.


Per usare [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), assicurati che sia scaricato ed esegui:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Frammenti di Codice Chiave**
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

Lo script verifica il risultato rispetto a `torch.mm` con una piccola tolleranza. L'aritmetica in virgola mobile sulle GPU può produrre piccole differenze numeriche rispetto alle implementazioni CPU a causa dell'ordine di riduzione parallela.

<!-- @os:linux -->
**Output atteso:**[I numeri di prestazione varieranno]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Su Windows, `amd-smi` non è supportato. Per monitorare l'utilizzo della GPU, puoi usare Task Manager, dove dovresti vedere un breve picco di utilizzo quando esegui il programma.

**Output atteso:**
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

#### Approccio B: Estensione C++

Il secondo approccio è più manuale: scrivi il kernel e il binding Python in un singolo file `.cu`, compilalo nativamente usando il sistema di build di PyTorch e importalo in Python.

<!-- @os:windows -->
> **Nota**: L'approccio Estensione C++ richiede l'ambiente di build C++ di Visual Studio perché PyTorch compila il file sorgente `.cu` in un modulo di estensione nativo `.pyd`. La costruzione di tale estensione nativa dipende dalla toolchain Microsoft C++ (compilatore, linker e strumenti di build) fornita da Visual Studio. Esegui i comandi di attivazione di Visual Studio dalla sezione di configurazione prima di costruire l'estensione.
<!-- @os:end -->

Scarica i seguenti file se non lo hai già fatto:
<!-- @os:windows -->
| File | Ruolo |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script di build, usa `CUDAExtension` per compilare il `.cu` in un `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python che esegue gli artefatti costruiti |
<!-- @os:end -->
<!-- @os:linux -->
| File | Ruolo |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script di build, usa `CUDAExtension` per compilare il `.cu` in un `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python che esegue gli artefatti costruiti |
<!-- @os:end -->

#### **Passaggio 1: Il kernel, il launcher e il binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Rispetto a `add_one_launcher` nella Procedura Guidata 1, il launcher qui:
- Accetta due tensori di input invece di uno
- Deriva tutte e tre le dimensioni (M, N, K) dalle forme dei tensori, senza passaggio manuale delle dimensioni da Python
- Alloca e restituisce il tensore di output C, invece di modificarlo in-place
- Usa `dim3` sia per la griglia che per il blocco per esprimere la forma di avvio 2D

#### **Passaggio 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Nota**: Questo comando cerca `setup.py` nella directory corrente per costruire il file .cu che abbiamo creato.


Questo produce i seguenti file:
<!-- @os:windows -->
- `build/`:  directory con i file `.pyd`
- `matmul_kernel.hip`:  il sorgente HIP generato dall'hipificazione del file `.cu`; questo è ciò che `hipcc` ha effettivamente compilato
<!-- @os:end -->
<!-- @os:linux -->
- `build/`:  directory con i file `.so`
- `matmul_kernel.hip`:  il sorgente HIP generato dall'hipificazione del file `.cu`; questo è ciò che `hipcc` ha effettivamente compilato
<!-- @os:end -->

#### **Passaggio 3: Usa da Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Esegui questo script per vedere il kernel in azione:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Output atteso:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Ottimo! Hai appena implementato la moltiplicazione matriciale sulla GPU.** Questo è un traguardo importante perché la moltiplicazione matriciale è la spina dorsale delle moderne operazioni di machine learning come:
- Layer di reti neurali
- Meccanismi di attenzione
- Embedding
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

## Prossimi Passi

Hai imparato a scrivere, compilare e avviare kernel GPU usando sia la compilazione JIT che le estensioni C++ per operazioni parallele di base.

**Ottimizzazioni delle prestazioni:**
- **Tiling con memoria condivisa** - Memorizza nella cache blocchi di dati per ridurre l'accesso alla memoria globale
- **Coalescenza della memoria** - Ottimizza i pattern di accesso alla memoria per la larghezza di banda

**Algoritmi del mondo reale:**
- **Convoluzione 2D** - Un piccolo filtro (kernel) scorre su un'immagine, calcolando ogni pixel di output da una somma pesata dei pixel vicini. Questo introduce calcoli stencil e tiling con memoria condivisa, dove i thread riutilizzano regioni di immagine sovrapposte per ridurre l'accesso alla memoria globale.
- **Funzione Softmax