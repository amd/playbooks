<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

Escreva um kernel de GPU do zero, compile-o, execute-o em uma GPU AMD e observe o pico de utilização. Este playbook mostra como a computação em GPU realmente funciona: escreva o código do kernel e execute-o em paralelo em milhares de threads.

> **Observação**: Este é um playbook razoavelmente complexo, que pode exigir alguma depuração e modificações extras.

## O que Você Vai Aprender

<!-- @os:windows -->
- Como funcionam os kernels de GPU: grids, blocks, threads e o modelo de indexação que os mapeia para os dados
- Como a pilha AMD ROCm/HIP permite escrever código no estilo CUDA que roda em GPUs AMD sem modificações
- Como compilar um kernel em tempo de execução usando `torch.cuda._compile_kernel`
- Como criar uma extensão de kernel C++ nativa com `CUDAExtension` + pybind11, importável a partir do Python
<!-- @os:end -->
<!-- @os:linux -->
- Como funcionam os kernels de GPU: grids, blocks, threads e o modelo de indexação que os mapeia para os dados
- Como a pilha AMD ROCm/HIP permite escrever código no estilo CUDA que roda em GPUs AMD sem modificações
- Como compilar um kernel em tempo de execução usando `torch.cuda._compile_kernel`
- Como criar uma extensão de kernel C++ nativa com `CUDAExtension` + pybind11, importável a partir do Python
- Como medir o tempo de execução de um kernel e monitorar a utilização da GPU em tempo real com `amd-smi`
<!-- @os:end -->

---

Este playbook aborda duas abordagens para desenvolvimento de kernels:

<!-- @os:windows -->
| Abordagem | Ponto de entrada |
|---|---|
| **Compilação JIT** | `torch.cuda._compile_kernel`, escreva um kernel como uma string Python, sem etapa de build |
| **Extensão C++** | `CUDAExtension` + pybind11: compile um arquivo `.cu` em um `.pyd` nativo e importe-o |
<!-- @os:end -->
<!-- @os:linux -->
| Abordagem | Ponto de entrada |
|---|---|
| **Compilação JIT** | `torch.cuda._compile_kernel`, escreva um kernel como uma string Python, sem etapa de build |
| **Extensão C++** | `CUDAExtension` + pybind11: compile um arquivo `.cu` em um `.so` nativo e importe-o |
<!-- @os:end -->

Ambas as abordagens funcionam em GPUs AMD. Isso é possível porque o build ROCm do PyTorch mapeia toda a superfície da API CUDA para HIP. Isso significa que `torch.cuda`, `CUDAExtension` e a sintaxe de kernel CUDA funcionam de forma transparente no hardware AMD.

---

## Contexto

### O que é um Kernel de GPU?

Um kernel de GPU é uma função que roda em paralelo em milhares de threads da GPU simultaneamente. Diferente de uma função de CPU que executa uma vez por chamada, um kernel é lançado com um **grid** de **blocks**, cada um contendo muitas **threads**, todas executando o mesmo código em dados diferentes.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### Modelo de Indexação de Threads

Ao lançar um kernel você especifica duas dimensões:

| Variável | Significado |
|---|---|
| `gridDim` | Número de blocks no grid |
| `blockDim` | Número de threads por block |

Cada thread tem acesso a três variáveis integradas somente leitura:

| Variável | Significado |
|---|---|
| `blockIdx.x` | A qual block esta thread pertence |
| `blockDim.x` | Número de threads em um block |
| `threadIdx.x` | Índice da thread dentro do seu block |

### ID Global da Thread

Essas variáveis são combinadas para calcular um índice de thread globalmente único:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Total de threads = `gridDim.x * blockDim.x`. Cada thread processa um elemento de forma independente. Esta é a base do **paralelismo de dados**. A mesma operação roda em muitos elementos ao mesmo tempo, sem dependência entre threads.

---

### Modelo de Execução da GPU: Wavefronts

As GPUs AMD executam threads em grupos de **32** chamados **wavefronts**. Todas as threads em uma wavefront executam a mesma instrução simultaneamente. Isso afeta as escolhas ideais de tamanho de block (256 threads = 8 wavefronts = boa eficiência de agendamento).

### Programação em GPU AMD: HIP + ROCm

**ROCm** é a pilha de computação em GPU de código aberto da AMD (drivers, compiladores, bibliotecas, runtime). **HIP** fica em cima, projetado para ser sintaticamente idêntico ao CUDA. O build ROCm do PyTorch mapeia de forma transparente `torch.cuda.*` para HIP, então o mesmo código funciona em GPUs AMD.

---

### PyTorch + AMD/HIP

O PyTorch disponibiliza um build ROCm no qual a superfície da API CUDA (`torch.cuda.*`) é suportada de forma transparente pelo HIP. Isso significa que:

- `torch.cuda.is_available()` funciona em GPUs AMD com ROCm
- `tensor.to("cuda")` aloca na GPU AMD
- `torch.version.hip` expõe a versão do HIP

O PyTorch também disponibiliza `torch.cuda._compile_kernel()`, um atalho de alto nível para compilar via JIT uma string de kernel bruta e obter de volta um callable, sem precisar de uma etapa de build separada.

---

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Pré-requisitos - Windows
- Instale a versão mais recente: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
No Linux, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv com ROCm+Pytorch já instalados.
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
**Conceda ao seu usuário acesso aos dispositivos de GPU** (saia e entre novamente para que isso tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

No Linux, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
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
No Windows, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **Dica**: Usuários do Windows podem precisar modificar sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @os:end -->
### Instalando Dependências Básicas
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
> **Nota:** Para este playbook, o ROCm e o PyTorch precisam ser instalados no ambiente virtual mesmo no Ryzen AI Halo, já que a compilação de kernels personalizados requer os cabeçalhos de desenvolvimento completos.

Instale o ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

Instale o PyTorch:
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

### Instalando Dependências Adicionais

<!-- @os:linux -->
Instale o toolchain de compilação C/C++ do Linux. Essa é uma dependência de nível de sistema e é necessária para os walkthroughs de extensão C++ porque o `CUDAExtension` compila módulos `.so` nativos a partir de arquivos `.cu`.

Execute isso uma vez na máquina Linux, fora do ambiente virtual Python criado:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

Depois de ativar o ambiente virtual `kernel-env`, instale as dependências de compilação Python:
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
Certifique-se de que o [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou [uma versão mais recente](https://visualstudio.microsoft.com/vs/community/) esteja instalado com a carga de trabalho **Desktop development with C++**.

> **Nota**: Essa configuração do ambiente Visual Studio C++ é necessária somente para a abordagem de **Extensão C++**. Ela não é necessária para a abordagem de Compilação JIT.

Abra um terminal do PowerShell e execute os comandos a seguir antes de compilar a extensão C++.

**Etapa 1: Encontre o ambiente Visual Studio C++ instalado**

**(A) Localize o `vswhere.exe`, que é instalado com o Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) Encontre o `vcvars64.bat` do Visual Studio 2022 ou de uma versão mais recente com as ferramentas de compilação C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Imprima o ambiente Visual Studio C++ sendo usado**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Etapa 2: Ative o ambiente de compilação Visual Studio C++**

**(A) Execute o `vcvars64.bat` e capture o ambiente que ele configura**

Isso torna disponíveis o `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` e os caminhos do Windows SDK.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Importe as variáveis de ambiente do Visual Studio para esta sessão do PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Etapa 3: Verifique se o compilador C++ da Microsoft está disponível**

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

#### Defina as Variáveis de Ambiente
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
Verifique se a GPU AMD está visível com:
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

## Baixar Arquivos Necessários

Crie a seguinte estrutura de diretórios criando as **2 novas pastas** e baixando os arquivos correspondentes:

| Diretório | Arquivos para Baixar | Descrição |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Arquivos JIT e de extensão C++ para o kernel de adição de vetores |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Arquivos JIT e de extensão C++ para o kernel de multiplicação de matrizes |


## Walkthroughs

### Walkthrough 1: Adição de Vetores

#### Abordagem A: Compilação JIT

A compilação JIT (Just-In-Time) significa que o kernel é escrito como uma string C++ bruta dentro do Python e compilado em tempo de execução, sem a necessidade de etapas extras de build.

Para usar o [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), certifique-se de que ele foi baixado e execute:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Trechos de Código Principais**
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
> **Dica**: O script também gera uma thread em segundo plano que consulta o `amd-smi` a cada 100ms para registrar o pico e a média de utilização da GPU durante a execução do kernel.
<!-- @os:end -->

> **Nota**: **Por que o Tamanho do Bloco é 256?** <br>
> - O kernel usa **256 threads por bloco** porque isso se alinha bem com o **modelo de execução de wavefront das GPUs AMD**.
> - Lembre-se de que o hardware AMD executa threads em grupos de 32 threads, resultando em 8 wavefronts por bloco. (8 wavefronts x 32 threads = 1 bloco)


**O que a carga de trabalho faz:**

O kernel adiciona trabalho extra artificialmente para demonstrar a utilização da GPU:

- **100.000.000 de elementos** no tensor
- **O loop interno executa 1.000 vezes** por elemento a cada execução do kernel  
- **200 execuções** de kernel no total

**Matemática:**  
- Cada elemento: é incrementado em 1 × 1.000 iterações × 200 execuções = 200.000  
- Resultado final: 1,0 (valor inicial) + 200.000 (adições) = 200.001,0

**Por que o loop interno?**  
- Sem o loop `for (int i = 0; i < 1000; i++)`, as 200 execuções terminariam instantaneamente e as ferramentas de monitoramento não capturariam uma utilização de GPU significativa. O trabalho artificial faz com que cada execução do kernel dure tempo suficiente para que as ferramentas de monitoramento possam medir o desempenho.

<!-- @os:linux -->
**Saída esperada:**[Os números de desempenho podem variar]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: No Windows, o `amd-smi` não é suportado. Para acompanhar a utilização da GPU, você pode usar o Gerenciador de Tarefas, onde deverá ver um breve pico de utilização ao executar o programa.

**Saída esperada:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Muito bem! Você acabou de executar seu primeiro kernel de GPU.**

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
#### Approach B: Extensão C++

A segunda abordagem é mais manual: escreva o kernel e a associação Python em um único arquivo `.cu`, compile-o nativamente usando o sistema de build do PyTorch e importe-o para o Python.

<!-- @os:windows -->
> **Observação**: A abordagem de Extensão C++ requer o ambiente de build C++ do Visual Studio, pois o PyTorch compila o arquivo de origem `.cu` em um módulo de extensão `.pyd` nativo. A construção dessa extensão nativa depende do toolchain C++ da Microsoft (compilador, linker e ferramentas de build) fornecido pelo Visual Studio. Execute os comandos de ativação do Visual Studio da seção de configuração antes de construir a extensão.
<!-- @os:end -->

Baixe os seguintes arquivos, caso ainda não tenha feito isso:
<!-- @os:windows -->
| Arquivo | Função |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + associação pybind11, tudo em um único arquivo |
| [setup.py](assets/Vector_Addition/setup.py) | Script de build, usa `CUDAExtension` para compilar o `.cu` em um `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python que executa os artefatos construídos |
<!-- @os:end -->

<!-- @os:linux -->
| Arquivo | Função |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + associação pybind11, tudo em um único arquivo |
| [setup.py](assets/Vector_Addition/setup.py) | Script de build, usa `CUDAExtension` para compilar o `.cu` em um `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Script Python que executa os artefatos construídos |
<!-- @os:end -->

#### **Etapa 1: O kernel, launcher e associação** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**Dica**: Por que usar `hipDeviceSynchronize()`? <br>
> - As execuções de kernel na GPU são assíncronas. Quando a CPU executa `add_one<<<grid_size, block_size>>>(data, n);`, ela executaria imediatamente a próxima instrução sem esperar pela GPU. O `hipDeviceSynchronize()` força a CPU a esperar até que o kernel da GPU seja concluído.

#### **Etapa 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Observação**: Este comando procura por `setup.py` no diretório atual para construir o arquivo .cu que criamos.


`CUDAExtension` é um auxiliar de build CUDA de `torch.utils.cpp_extension`. Com o ROCm, o PyTorch **remapeia o `CUDAExtension` para usar o `hipcc`** em vez do `nvcc`. O ROCm intercepta o caminho de build e o encaminha pelo compilador HIP, portando o código CUDA para AMD.

Isso produz os seguintes arquivos:
<!-- @os:windows -->
- `build/`: diretório com os arquivos `.pyd`
- `add_one_kernel.hip`: o código-fonte HIP gerado ao hipificar o arquivo `.cu`; isso é o que o `hipcc` realmente compilou
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: diretório com os arquivos `.so`
- `add_one_kernel.hip`: o código-fonte HIP gerado ao hipificar o arquivo `.cu`; isso é o que o `hipcc` realmente compilou
<!-- @os:end -->

#### **Etapa 3: Usar a partir do Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Execute este script para ver o kernel em ação:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Saída esperada:**
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

### Passo a passo 2: Multiplicação de Matrizes

A multiplicação de matrizes calcula **C = A × B**, onde:
- **A** é M×N (linhas × colunas)
- **B** é N×K  
- **C** é M×K (o resultado)

Cada elemento de saída é definido como:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

Cada elemento de C é calculado independentemente, o que torna essa operação perfeita para o paralelismo de GPU.

#### Como Isso Se Mapeia para Threads da GPU

Diferentemente da adição de vetores (1D), a multiplicação de matrizes produz uma **saída 2D**, então usamos uma **grade 2D de threads**:

| | Adição de Vetores | Multiplicação de Matrizes |
|---|---|---|
| **Formato da saída** | Array 1D | Matriz 2D (M×K) |
| **Mapeamento de threads** | 1 thread → 1 elemento | 1 thread → 1 elemento de saída |
| **Padrão de lançamento** | Grade 1D: `(grid_x, 1, 1)` | Grade 2D: `(grid_x, grid_y, 1)` |
| **Tamanho do bloco** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

Cada thread calcula um elemento da matriz de saída C. A thread na posição `(row, col)` calcula `C[row][col]` multiplicando a linha correspondente de A pela coluna correspondente de B.

**Layout de Memória**: A memória da GPU é plana (1D), mas as matrizes são armazenadas linha por linha. Para acessar `A[row][col]`, o kernel usa `A[row * N + col]`.


#### Approach A: Compilação JIT:

Assim como no Passo a passo 1, o kernel é escrito como uma string C++ bruta dentro do Python e compilado em tempo de execução via JIT integrado do PyTorch.


Para usar [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), certifique-se de que foi baixado e execute:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Trechos de Código Principais**
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

O script verifica o resultado em comparação com `torch.mm` com uma pequena tolerância. Operações de ponto flutuante em GPUs podem produzir pequenas diferenças numéricas em comparação com implementações em CPU devido à ordem de redução paralela.

<!-- @os:linux -->
**Saída esperada:**[Os números de desempenho variam]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: No Windows, o `amd-smi` não é compatível. Para acompanhar a utilização da GPU, você pode usar o Gerenciador de Tarefas, onde deverá ver um breve pico de utilização ao executar o programa.

**Saída esperada:**
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
#### Abordagem B: Extensão C++

A segunda abordagem é mais manual: escrever o kernel e o binding Python em um único arquivo `.cu`, compilá-lo nativamente usando o sistema de build do PyTorch e importá-lo no Python.

<!-- @os:windows -->
> **Observação**: A abordagem de Extensão C++ requer o ambiente de build do Visual Studio C++, pois o PyTorch compila o arquivo de origem `.cu` em um módulo de extensão `.pyd` nativo. A construção dessa extensão nativa depende do toolchain C++ da Microsoft (compilador, linker e ferramentas de build) fornecido pelo Visual Studio. Execute os comandos de ativação do Visual Studio da seção de configuração antes de construir a extensão.
<!-- @os:end -->

Baixe os seguintes arquivos, caso ainda não tenha feito isso:
<!-- @os:windows -->
| Arquivo | Função |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de build, usa `CUDAExtension` para compilar o `.cu` em um `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python que executa os artefatos construídos |
<!-- @os:end -->
<!-- @os:linux -->
| Arquivo | Função |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + binding pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Script de build, usa `CUDAExtension` para compilar o `.cu` em um `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Script Python que executa os artefatos construídos |
<!-- @os:end -->

#### **Etapa 1: O kernel, launcher e binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Comparado ao `add_one_launcher` no Passo a passo 1, o launcher aqui:
- Recebe dois tensores de entrada em vez de um
- Deriva todas as três dimensões (M, N, K) a partir das formas dos tensores, sem passagem manual de tamanho a partir do Python
- Aloca e retorna o tensor de saída C, em vez de mutá-lo no local
- Usa `dim3` tanto para grid quanto para block para expressar a forma de lançamento 2D

#### **Etapa 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**Observação**: Este comando procura o `setup.py` no diretório atual para construir o arquivo .cu que criamos.


Isso produz os seguintes arquivos:
<!-- @os:windows -->
- `build/`: diretório com os arquivos `.pyd`
- `matmul_kernel.hip`: o código-fonte HIP gerado ao hipificar o arquivo `.cu`; isso é o que o `hipcc` realmente compilou
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: diretório com os arquivos `.so`
- `matmul_kernel.hip`: o código-fonte HIP gerado ao hipificar o arquivo `.cu`; isso é o que o `hipcc` realmente compilou
<!-- @os:end -->

#### **Etapa 3: Usar a partir do Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Execute este script para ver o kernel em ação:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Saída esperada:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Excelente! Você acabou de implementar multiplicação de matrizes na GPU.** Este é um marco importante, pois a multiplicação de matrizes é a espinha dorsal de operações modernas de aprendizado de máquina, como:
- Camadas de redes neurais
- Mecanismos de atenção
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

## Próximos passos

Você aprendeu a escrever, compilar e lançar kernels de GPU usando tanto compilação JIT quanto extensões C++ para operações paralelas básicas.

**Otimizações de desempenho:**
- **Tiling de memória compartilhada** - Armazenar em cache blocos de dados para reduzir o acesso à memória global
- **Coalescência de memória** - Otimizar padrões de acesso à memória para melhorar a largura de banda

**Algoritmos do mundo real:**
- **Convolução 2D** - Um pequeno filtro (kernel) desliza por uma imagem, calculando cada pixel de saída a partir de uma soma ponderada dos pixels vizinhos. Isso introduz computações do tipo stencil e tiling de memória compartilhada, em que os threads reutilizam regiões sobrepostas da imagem para reduzir o acesso à memória global.
- **Função Softmax**: A Softmax converte um vetor de números em probabilidades que somam 1, comumente usada em saídas de redes neurais. Implementá-la de forma eficiente na GPU introduz reduções paralelas e técnicas de estabilidade numérica ao processar vetores grandes.

**Considerações de produção:**
- **Tratamento de erros** - Verificação de limites e gerenciamento de dispositivos
- **Integração com PyTorch** - Operadores personalizados com suporte a autograd