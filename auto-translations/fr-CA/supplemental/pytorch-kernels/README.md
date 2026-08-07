<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement de l'anglais et n'a pas été révisée par un humain. Elle peut contenir des erreurs, et certaines instructions, commandes, options de téléchargement, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incompatibilité ou de divergence, la version originale anglaise du playbook fait foi.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Aperçu

Écrivez un kernel GPU à partir de zéro, compilez-le, lancez-le sur un GPU AMD et observez l'utilisation grimper en flèche. Ce guide pratique montre comment fonctionne réellement le calcul GPU : écrire le code du kernel et l'exécuter en parallèle sur des milliers de threads.

> **Remarque** : Il s'agit d'un guide pratique assez complexe, qui peut nécessiter du débogage et des modifications supplémentaires.

## Ce que vous apprendrez

<!-- @os:windows -->
- Comment fonctionnent les kernels GPU : grilles, blocs, threads et le modèle d'indexation qui les associe aux données
- Comment la pile AMD ROCm/HIP permet d'écrire du code de style CUDA qui s'exécute sur les GPU AMD sans modification
- Comment compiler un kernel à l'exécution à l'aide de `torch.cuda._compile_kernel`
- Comment construire une extension de kernel C++ native avec `CUDAExtension` + pybind11, importable depuis Python
<!-- @os:end -->
<!-- @os:linux -->
- Comment fonctionnent les kernels GPU : grilles, blocs, threads et le modèle d'indexation qui les associe aux données
- Comment la pile AMD ROCm/HIP permet d'écrire du code de style CUDA qui s'exécute sur les GPU AMD sans modification
- Comment compiler un kernel à l'exécution à l'aide de `torch.cuda._compile_kernel`
- Comment construire une extension de kernel C++ native avec `CUDAExtension` + pybind11, importable depuis Python
- Comment mesurer le temps d'exécution d'un kernel et surveiller l'utilisation du GPU en direct avec `amd-smi`
<!-- @os:end -->

---

Ce guide pratique couvre deux approches pour le développement de kernels :

<!-- @os:windows -->
| Approche | Point d'entrée |
|---|---|
| **Compilation JIT** | `torch.cuda._compile_kernel`, écrivez un kernel sous forme de chaîne Python, sans étape de compilation |
| **Extension C++** | `CUDAExtension` + pybind11 : compilez un fichier `.cu` en un `.pyd` natif et importez-le |
<!-- @os:end -->
<!-- @os:linux -->
| Approche | Point d'entrée |
|---|---|
| **Compilation JIT** | `torch.cuda._compile_kernel`, écrivez un kernel sous forme de chaîne Python, sans étape de compilation |
| **Extension C++** | `CUDAExtension` + pybind11 : compilez un fichier `.cu` en un `.so` natif et importez-le |
<!-- @os:end -->

Les deux approches fonctionnent sur les GPU AMD. Cela est possible parce que la version ROCm de PyTorch fait correspondre toute la surface de l'API CUDA à HIP. Cela signifie que `torch.cuda`, `CUDAExtension` et la syntaxe des kernels CUDA fonctionnent tous de manière transparente sur le matériel AMD.

---

## Contexte

### Qu'est-ce qu'un kernel GPU?

Un kernel GPU est une fonction qui s'exécute en parallèle sur des milliers de threads GPU simultanément. Contrairement à une fonction CPU qui s'exécute une seule fois par appel, un kernel est lancé avec une **grille** de **blocs**, chacun contenant de nombreux **threads**, exécutant tous le même code sur des données différentes.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Modèle d'indexation des threads

Lors du lancement d'un kernel, vous spécifiez deux dimensions :

| Variable | Signification |
|---|---|
| `gridDim` | Nombre de blocs dans la grille |
| `blockDim` | Nombre de threads par bloc |

Chaque thread a accès à trois variables intégrées en lecture seule :

| Variable | Signification |
|---|---|
| `blockIdx.x` | Le bloc auquel ce thread appartient |
| `blockDim.x` | Nombre de threads dans un bloc |
| `threadIdx.x` | Index du thread au sein de son bloc |

### ID de thread global

Ces variables sont combinées pour calculer un index de thread global unique :

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Threads totaux = `gridDim.x * blockDim.x`. Chaque thread traite un élément de manière indépendante. C'est le fondement du **parallélisme de données**. La même opération s'exécute sur de nombreux éléments à la fois, sans dépendance entre les threads.

---

### Modèle d'exécution GPU : wavefronts

Les GPU AMD exécutent les threads par groupes de **32** appelés **wavefronts**. Tous les threads d'un wavefront exécutent la même instruction simultanément. Cela influence le choix optimal de la taille des blocs (256 threads = 8 wavefronts = bonne efficacité d'ordonnancement).

### Programmation GPU AMD : HIP + ROCm

**ROCm** est la pile de calcul GPU ouverte d'AMD (pilotes, compilateurs, bibliothèques, runtime). **HIP** se situe au-dessus, conçu pour être syntaxiquement identique à CUDA. La version ROCm de PyTorch fait correspondre de manière transparente `torch.cuda.*` à HIP, de sorte que le même code fonctionne sur les GPU AMD.

---

### PyTorch + AMD/HIP

PyTorch propose une version ROCm où la surface de l'API CUDA (`torch.cuda.*`) est prise en charge de manière transparente par HIP. Cela signifie que :

- `torch.cuda.is_available()` fonctionne sur les GPU AMD avec ROCm
- `tensor.to("cuda")` alloue sur le GPU AMD
- `torch.version.hip` expose la version HIP

PyTorch expose également `torch.cuda._compile_kernel()`, un raccourci de haut niveau pour compiler à la volée (JIT) une chaîne de kernel brute et obtenir en retour un appelable, sans avoir besoin d'une étape de compilation distincte.

---

<!-- @device:halo_box -->
## Vérifier les mises à jour logicielles

<!-- @require:software-update -->
<!-- @device:end -->

## Installation des prérequis logiciels
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Prérequis - Windows
- Installer la dernière version : [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Créer un environnement virtuel

<!-- @os:linux -->
<!-- @device:halo_box -->
Sous Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv avec ROCm+PyTorch déjà installé.
<!-- @test:id=create-venv timeout=300 -->
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
**Accordez à votre utilisateur l'accès aux périphériques GPU** (déconnectez-vous et reconnectez-vous pour que cela prenne effet) :

```bash
sudo usermod -aG render,video $LOGNAME
```

Sous Linux, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
<!-- @test:id=create-venv timeout=300 -->
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
Sous Windows, ouvrez un terminal dans le répertoire de votre choix et suivez les commandes pour créer un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Astuce** : Les utilisateurs de Windows devront peut-être modifier leur politique d'exécution PowerShell (par exemple,
> en la définissant sur RemoteSigned ou Unrestricted) avant d'exécuter certaines commandes PowerShell.

<!-- @os:end -->


### Installation des dépendances de base
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
> **Remarque :** Pour ce guide pratique, ROCm et PyTorch doivent être installés dans l'environnement virtuel même sur le Ryzen AI Halo, car la compilation de kernels personnalisés nécessite les en-têtes de développement complets.

Installer ROCm :
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Installer PyTorch :
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
### Installation de dépendances supplémentaires

<!-- @os:linux -->
Installez la chaîne d'outils de compilation C/C++ pour Linux. Il s'agit d'une dépendance au niveau du système, requise pour les tutoriels d'extension C++, car `CUDAExtension` compile des modules natifs `.so` à partir de fichiers `.cu`.

Exécutez cette commande une seule fois sur la machine Linux, à l'extérieur de l'environnement virtuel Python créé :

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Après avoir activé l'environnement virtuel `kernel-env`, installez les dépendances Python de compilation :
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
Veuillez vous assurer que [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou une [version plus récente](https://visualstudio.microsoft.com/vs/community/) est installée avec la charge de travail **Développement Desktop en C++**.

> **Remarque** : cette configuration de l'environnement Visual Studio C++ n'est requise que pour l'approche **d'extension C++**. Elle n'est pas nécessaire pour l'approche de compilation JIT.

Ouvrez un terminal PowerShell et exécutez les commandes suivantes avant de compiler l'extension C++.

**Étape 1 : Trouver l'environnement Visual Studio C++ installé**

**(A) Localiser `vswhere.exe`, qui est installé avec l'installateur de Visual Studio**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Trouver `vcvars64.bat` à partir de Visual Studio 2022 ou d'une version plus récente avec les outils de compilation C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Afficher l'environnement Visual Studio C++ utilisé**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Étape 2 : Activer l'environnement de compilation Visual Studio C++**

**(A) Exécuter `vcvars64.bat` et capturer l'environnement qu'il configure**

Cela rend disponibles `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` ainsi que les chemins du kit SDK Windows.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importer les variables d'environnement de Visual Studio dans cette session PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Étape 3 : Vérifier que le compilateur C++ de Microsoft est disponible**

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

#### Définir les variables d'environnement
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
Vérifiez que le GPU AMD est bien détecté à l'aide de la commande suivante :
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

## Téléchargement des fichiers requis

Créez la structure de répertoires suivante en créant les **2 nouveaux dossiers** et en téléchargeant les fichiers correspondants :

| Répertoire | Fichiers à télécharger | Description |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Fichiers JIT et d'extension C++ pour le kernel d'addition de vecteurs |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Fichiers JIT et d'extension C++ pour le kernel de multiplication matricielle |


## Tutoriel 1 : Addition de vecteurs

#### Approche A : Compilation JIT

La compilation JIT (Just-In-Time, à la volée) signifie que le kernel est écrit sous forme de chaîne C++ brute dans Python et compilé au moment de l'exécution, sans nécessiter d'étapes de compilation supplémentaires.

Pour utiliser [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), assurez-vous qu'il est téléchargé, puis exécutez :
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Extraits de code clés**
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
> **Astuce** : le script démarre également un fil d'exécution en arrière-plan qui interroge `amd-smi` toutes les 100 ms afin de consigner l'utilisation maximale et moyenne du GPU pendant l'exécution du kernel.
<!-- @os:end -->

> **Remarque** : **Pourquoi une taille de bloc de 256?** <br>
> - Le kernel utilise **256 threads par bloc**, car cela s'aligne bien avec le **modèle d'exécution par wavefront des GPU AMD**.
> - Rappelons que le matériel AMD exécute les threads par groupes de 32, ce qui donne 8 wavefronts par bloc (8 wavefronts x 32 threads = 1 bloc).


**Ce que fait la charge de travail :**

Le kernel ajoute artificiellement du travail supplémentaire pour démontrer l'utilisation du GPU :

- **100 000 000 éléments** dans le tenseur
- La **boucle interne s'exécute 1 000 fois** par élément à chaque lancement de kernel  
- **200 lancements** de kernel au total

**Calcul :**  
- Chaque élément est incrémenté de 1 × 1 000 itérations × 200 lancements = 200 000  
- Résultat final : 1,0 (valeur de départ) + 200 000 (additions) = 200 001,0

**Pourquoi la boucle interne?**  
- Sans la boucle `for (int i = 0; i < 1000; i++)`, les 200 lancements se termineraient instantanément et les outils de surveillance ne pourraient pas capturer une utilisation significative du GPU. Ce travail artificiel permet à chaque exécution du kernel de durer suffisamment longtemps pour que les outils de surveillance puissent mesurer la performance.

<!-- @os:linux -->
**Sortie attendue :** [Les valeurs de performance peuvent varier]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : sous Windows, `amd-smi` n'est pas pris en charge. Pour suivre l'utilisation du GPU, vous pouvez utiliser le Gestionnaire des tâches, où vous devriez observer un bref pic d'utilisation lors de l'exécution du programme.

**Sortie attendue :**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Bon travail! Vous venez d'exécuter votre premier kernel GPU.**

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
#### Approche B : Extension C++

La deuxième approche est plus manuelle : écrire le noyau et la liaison Python dans un seul fichier `.cu`, le compiler nativement à l'aide du système de compilation de PyTorch, puis l'importer dans Python.

<!-- @os:windows -->
> **Remarque** : L'approche par extension C++ nécessite l'environnement de compilation Visual Studio C++, car PyTorch compile le fichier source `.cu` en un module d'extension natif `.pyd`. La compilation de cette extension native dépend de la chaîne d'outils C++ Microsoft (compilateur, éditeur de liens et outils de compilation) fournie par Visual Studio. Exécutez les commandes d'activation de Visual Studio de la section de configuration avant de compiler l'extension.
<!-- @os:end -->

Téléchargez les fichiers suivants si ce n'est pas déjà fait :
<!-- @os:windows -->
| Fichier | Rôle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Noyau + lanceur + liaison pybind11, tout dans un seul fichier |
| [setup.py](assets/Vector_Addition/setup.py) | Script de compilation, utilise `CUDAExtension` pour compiler le `.cu` en `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python qui exécute les artefacts compilés |
<!-- @os:end -->

<!-- @os:linux -->
| Fichier | Rôle |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Noyau + lanceur + liaison pybind11, tout dans un seul fichier |
| [setup.py](assets/Vector_Addition/setup.py) | Script de compilation, utilise `CUDAExtension` pour compiler le `.cu` en `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python qui exécute les artefacts compilés |
<!-- @os:end -->

#### **Étape 1 : Le noyau, le lanceur et la liaison** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)) :
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

>**Astuce** : Pourquoi utiliser `hipDeviceSynchronize()`? <br>
> - Les lancements de noyaux GPU sont asynchrones. Lorsque le CPU exécute `add_one<<<grid_size, block_size>>>(data, n);`, il exécuterait immédiatement l'instruction suivante sans attendre le GPU. `hipDeviceSynchronize()` force le CPU à attendre que le noyau GPU se termine.

#### **Étape 2 : Compilation**
```bash
pip install --no-build-isolation -v .
```
>**Remarque** : Cette commande recherche `setup.py` dans le répertoire actuel pour compiler le fichier .cu que nous avons créé.


`CUDAExtension` est un utilitaire de compilation CUDA provenant de `torch.utils.cpp_extension`. Avec ROCm, PyTorch **redirige `CUDAExtension` pour utiliser `hipcc`** au lieu de `nvcc`. ROCm intercepte le chemin de compilation et le redirige vers le compilateur HIP, portant le code CUDA vers AMD.

Cela produit les fichiers suivants :
<!-- @os:windows -->
- `build/` : répertoire contenant les fichiers `.pyd`
- `add_one_kernel.hip` : la source HIP générée par le hipification du fichier `.cu`; c'est ce que `hipcc` a réellement compilé
<!-- @os:end -->
<!-- @os:linux -->
- `build/` : répertoire contenant les fichiers `.so`
- `add_one_kernel.hip` : la source HIP générée par le hipification du fichier `.cu`; c'est ce que `hipcc` a réellement compilé
<!-- @os:end -->

#### **Étape 3 : Utilisation depuis Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)) :
Exécutez ce script pour voir le noyau en action :
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Résultat attendu :**
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

## Présentation 2 : Multiplication de matrices

La multiplication de matrices calcule **C = A × B**, où :
- **A** est de dimension M×N (lignes × colonnes)
- **B** est de dimension N×K  
- **C** est de dimension M×K (le résultat)

Chaque élément de sortie est défini comme suit :
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Chaque élément de C est calculé indépendamment, ce qui rend cette opération parfaitement adaptée au parallélisme du GPU.

#### Comment cela correspond aux threads du GPU

Contrairement à l'addition vectorielle (1D), la multiplication de matrices produit une **sortie 2D**, nous utilisons donc une **grille de threads 2D** :

| | Addition vectorielle | Multiplication de matrices |
|---|---|---|
| **Forme de la sortie** | Tableau 1D | Matrice 2D (M×K) |
| **Correspondance des threads** | 1 thread → 1 élément | 1 thread → 1 élément de sortie |
| **Modèle de lancement** | Grille 1D : `(grid_x, 1, 1)` | Grille 2D : `(grid_x, grid_y, 1)` |
| **Taille du bloc** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

Chaque thread calcule un élément de la matrice de sortie C. Le thread à la position `(row, col)` calcule `C[row][col]` en multipliant la ligne correspondante de A avec la colonne correspondante de B.

**Disposition de la mémoire** : La mémoire du GPU est plate (1D), mais les matrices sont stockées ligne par ligne. Pour accéder à `A[row][col]`, le noyau utilise `A[row * N + col]`.


#### Approche A : Compilation JIT :

Comme dans la présentation 1, le noyau est écrit sous forme de chaîne C++ brute dans Python et compilé au moment de l'exécution via le JIT intégré de PyTorch.


Pour utiliser [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), assurez-vous qu'il est téléchargé, puis exécutez :
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Extraits de code clés**
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

Le script vérifie le résultat par rapport à `torch.mm` avec une tolérance faible. L'arithmétique à virgule flottante sur les GPU peut produire de petites différences numériques par rapport aux implémentations CPU en raison de l'ordre de réduction parallèle.

<!-- @os:linux -->
**Résultat attendu :**[Les chiffres de performance varieront]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Remarque** : Sous Windows, `amd-smi` n'est pas pris en charge. Pour suivre l'utilisation du GPU, vous pouvez utiliser le Gestionnaire des tâches, où vous devriez voir un bref pic d'utilisation lorsque vous exécutez le programme.

**Résultat attendu :**
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
#### Approche B : extension C++

La deuxième approche est plus manuelle : écrire le noyau et la liaison Python dans un seul fichier `.cu`, le compiler nativement à l'aide du système de compilation de PyTorch, puis l'importer dans Python.

<!-- @os:windows -->
> **Remarque** : l'approche par extension C++ nécessite l'environnement de compilation C++ Visual Studio, car PyTorch compile le fichier source `.cu` en un module d'extension natif `.pyd`. La compilation de cette extension native dépend de la chaîne d'outils C++ de Microsoft (compilateur, éditeur de liens et outils de compilation) fournie par Visual Studio. Exécutez les commandes d'activation de Visual Studio de la section de configuration avant de compiler l'extension.
<!-- @os:end -->

Téléchargez les fichiers suivants si ce n'est pas déjà fait :
<!-- @os:windows -->
| Fichier | Rôle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Noyau + programme de lancement + liaison pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de compilation, utilise `CUDAExtension` pour compiler le `.cu` en un `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python qui exécute les artefacts compilés |
<!-- @os:end -->
<!-- @os:linux -->
| Fichier | Rôle |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Noyau + programme de lancement + liaison pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de compilation, utilise `CUDAExtension` pour compiler le `.cu` en un `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python qui exécute les artefacts compilés |
<!-- @os:end -->

#### **Étape 1 : le noyau, le programme de lancement et la liaison** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)) :
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

Par rapport à `add_one_launcher` dans le tutoriel 1, le programme de lancement ici :
- Prend deux tenseurs d'entrée au lieu d'un seul
- Dérive les trois dimensions (M, N, K) à partir des formes des tenseurs, sans passage manuel des tailles depuis Python
- Alloue et retourne le tenseur de sortie C, plutôt que de le modifier sur place
- Utilise `dim3` à la fois pour la grille et le bloc afin d'exprimer la forme de lancement 2D

#### **Étape 2 : compilation**
```bash
pip install --no-build-isolation -v .
```
>**Remarque** : cette commande recherche `setup.py` dans le répertoire courant pour compiler le fichier .cu que nous avons créé.


Cela produit les fichiers suivants :
<!-- @os:windows -->
- `build/` : répertoire contenant les fichiers `.pyd`
- `matmul_kernel.hip` : la source HIP générée par la « hipification » du fichier `.cu`; c'est ce que `hipcc` a réellement compilé
<!-- @os:end -->
<!-- @os:linux -->
- `build/` : répertoire contenant les fichiers `.so`
- `matmul_kernel.hip` : la source HIP générée par la « hipification » du fichier `.cu`; c'est ce que `hipcc` a réellement compilé
<!-- @os:end -->

#### **Étape 3 : utilisation depuis Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)) :
Exécutez ce script pour voir le noyau en action :
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Résultat attendu :**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Excellent! Vous venez d'implémenter la multiplication matricielle sur le GPU.** Il s'agit d'une étape importante, car la multiplication matricielle est le pilier des opérations modernes d'apprentissage automatique, comme :
- Les couches de réseaux de neurones
- Les mécanismes d'attention
- Les plongements (embeddings)
- Les transformateurs

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

## Prochaines étapes

Vous avez appris à écrire, compiler et lancer des noyaux GPU en utilisant à la fois la compilation JIT et les extensions C++ pour des opérations parallèles de base.

**Optimisations de performance :**
- **Tuilage en mémoire partagée (shared memory tiling)** - Mise en cache de blocs de données pour réduire les accès à la mémoire globale
- **Coalescence de mémoire (memory coalescing)** - Optimisation des modèles d'accès mémoire pour la bande passante

**Algorithmes du monde réel :**
- **Convolution 2D** - Un petit filtre (noyau) glisse sur une image, calculant chaque pixel de sortie à partir d'une somme pondérée des pixels voisins. Cela introduit les calculs de type stencil et le tuilage en mémoire partagée, où les threads réutilisent des régions d'image qui se chevauchent afin de réduire les accès à la mémoire globale.
- **Fonction Softmax** : Softmax convertit un vecteur de nombres en probabilités dont la somme est égale à 1, une opération couramment utilisée dans les sorties des réseaux de neurones. Son implémentation efficace sur GPU introduit des réductions parallèles et des techniques de stabilité numérique pour le traitement de grands vecteurs.

**Considérations relatives à la production :**
- **Gestion des erreurs** - Vérification des limites et gestion des périphériques
- **Intégration à PyTorch** - Opérateurs personnalisés avec prise en charge de l'autograd