<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão geral

A [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) é um kit de ferramentas AMD de visão computacional e machine learning em C++ que fornece capacidades poderosas de perceção no dispositivo — incluindo estimativa de profundidade, deteção de rostos e rastreio de malha facial. Construída sobre os controladores Ryzen AI, a biblioteca seleciona automaticamente o melhor hardware disponível (GPU ou NPU) para inferência, permitindo adicionar funcionalidades de IA a aplicações C++ sem se preocupar com o treino de modelos ou a integração de frameworks. Todo o processamento ocorre localmente no seu sistema, tornando-a ideal para aplicações sensíveis à privacidade e de baixa latência.

Este manual ensina-o a configurar a Ryzen AI CVML Library, a compilar as aplicações de exemplo incluídas e a executar deteção de rostos numa imagem de amostra.

## O que vai aprender

- Como instalar os pré-requisitos e configurar a Ryzen AI CVML Library no seu sistema
- Como funciona a API C++ do CVML: contextos, objetos de funcionalidades e buffers de imagem
- Como compilar e executar as aplicações de exemplo incluídas usando CMake e OpenCV
- Como executar deteção de rostos numa imagem com caixas delimitadoras e pontos de referência
- Como integrar funcionalidades do CVML nas suas próprias aplicações C++

<!-- @device:halo_box -->
## Verificar atualizações de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalação dos pré-requisitos de software
<!-- @require:driver -->

## Dependências adicionais

Antes de começar, certifique-se de que tem o seguinte:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — transfira `opencv-4.11.0-windows.exe`, execute-o e extraia para uma pasta local (por exemplo, `C:\opencv`)
- [CMake](https://cmake.org/download/) — transfira o instalador MSI para Windows x86-64 e, durante a instalação, selecione **"Add CMake to the system PATH for all users"**
- [Controlador NPU Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html) — instale a versão mais recente disponível
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) com a carga de trabalho "Desktop development with C++" (inclui o compilador MSVC, o Windows SDK e as ferramentas de compilação C++)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — tem de ser compilado a partir do código-fonte (os pacotes apt no Ubuntu 22.04 e 24.04 não fornecem a versão 4.11). Consulte [Compilar o OpenCV a partir do código-fonte](#building-opencv-from-source) abaixo.
- CMake — instale através do apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 ou 24.04 (kernel >= 6.11.0-21-generic)
- [Controlador NPU Ryzen AI](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (instalador Linux — necessário para inferência na NPU)
- Vulkan SDK (instalado na secção [Vulkan SDK](#vulkan-sdk) abaixo)
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=cvml-prereqs-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
$env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"

cmake --version

if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
foreach ($dir in @("cmake", "include", "windows", "samples")) {
  $path = Join-Path $env:AMD_CVML_SDK_ROOT $dir
  if (-not (Test-Path $path)) {throw "Expected CVML folder was not found: $path"}
}

if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}
$opencvConfig = Join-Path $env:OPENCV_INSTALL_ROOT "OpenCVConfig.cmake"
if (-not (Test-Path $opencvConfig)) {throw "OpenCVConfig.cmake was not found: $opencvConfig"}

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $vswhere)) {throw "vswhere.exe not found. Install Visual Studio 2022 with Desktop development with C++ workload."}

$vsInstall = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Workload.NativeDesktop -property installationPath
if (-not $vsInstall) {throw "Visual Studio 2022 Desktop development with C++ workload was not found."}

$clPath = Get-ChildItem "$vsInstall\VC\Tools\MSVC" -Recurse -Filter cl.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $clPath) {throw "MSVC cl.exe was not found under Visual Studio installation."}

Write-Host "Checking Ryzen AI NPU driver presence..."
$npuDevices = Get-PnpDevice -Class ComputeAccelerator -ErrorAction SilentlyContinue | Where-Object {$_.FriendlyName -match "NPU|Neural|Ryzen AI|XDNA"}
if ($npuDevices) {
    Write-Host "NPU driver/device found:"
    $npuDevices | Format-Table Status, Class, Name, InstanceId -AutoSize
} else {
    Write-Host "Ryzen AI NPU driver was not detected. The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cvml-prereqs-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export AMD_CVML_SDK_ROOT="${AMD_CVML_SDK_ROOT:-/home/user/RyzenAI-Library}"
export OPENCV_INSTALL_ROOT="${OPENCV_INSTALL_ROOT:-/home/user/build/install}"

cmake --version

. /etc/os-release
if [ "${VERSION_ID}" != "24.04" ]; then
  echo "This CI runner is expected to be Ubuntu 24.04. Found: ${PRETTY_NAME}"
  exit 1
fi

if [ ! -d "$AMD_CVML_SDK_ROOT" ]; then
  echo "AMD_CVML_SDK_ROOT does not exist: $AMD_CVML_SDK_ROOT"
  exit 1
fi
for dir in cmake include linux samples; do
  if [ ! -d "$AMD_CVML_SDK_ROOT/$dir" ]; then
    echo "Expected CVML folder was not found: $AMD_CVML_SDK_ROOT/$dir"
    exit 1
  fi
done

if [ ! -d "$OPENCV_INSTALL_ROOT" ]; then
  echo "OPENCV_INSTALL_ROOT does not exist: $OPENCV_INSTALL_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT/lib" ]; then
  echo "OpenCV lib directory was not found: $OPENCV_INSTALL_ROOT/lib"
  exit 1
fi
if [ ! -f "$OPENCV_INSTALL_ROOT/lib/cmake/opencv4/OpenCVConfig.cmake" ]; then
  echo "OpenCVConfig.cmake was not found under: $OPENCV_INSTALL_ROOT/lib/cmake/opencv4"
  exit 1
fi

if ! command -v glslc >/dev/null 2>&1 && ! command -v vulkaninfo >/dev/null 2>&1; then
  echo "Vulkan SDK tools were not found. Install the Vulkan SDK before running this test."
  exit 1
fi

if [ -d /opt/xilinx/xrt/lib ]; then
  echo "Ryzen AI NPU driver/XRT runtime appears to be present."
else
  echo "Ryzen AI NPU driver/XRT runtime was not found at /opt/xilinx/xrt/lib."
  echo "The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
fi
```
<!-- @test:end --> 
<!-- @os:end -->

## Configurar a CVML Library

Crie uma conta AMD em [account.amd.com](https://account.amd.com) caso ainda não tenha uma e, em seguida, inicie sessão para transferir a Ryzen AI CVML Library a partir da ligação do portal abaixo:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

Após a transferência, extraia o pacote para um diretório local (por exemplo, `C:\RyzenAI-Library` no Windows ou `~/RyzenAI-Library` no Linux) e defina a variável de ambiente `AMD_CVML_SDK_ROOT` para a localização extraída:

<!-- @os:windows -->
```cmd
set AMD_CVML_SDK_ROOT=C:\RyzenAI-Library
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
export AMD_CVML_SDK_ROOT=~/RyzenAI-Library
```
<!-- @os:end -->

O pacote da biblioteca contém a seguinte estrutura:

| Pasta | Conteúdo |
|--------|----------|
| `cmake/` | Informações de empacotamento para a função `find_package` do CMake |
| `include/` | Ficheiros de cabeçalho C++ (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, etc.) |
| `windows/` | Ficheiros binários para Windows (ficheiros `.LIB` em tempo de compilação e `.DLL`/`.GRAPHLIB`/`.AMODEL` em tempo de execução) |
| `linux/` | Ficheiros binários para Linux (ficheiros `.SO` de compilação e de execução) |
| `samples/` | Aplicações de exemplo individuais com código-fonte |

<!-- @os:linux -->

### Configuração específica para Linux

#### Compilar o OpenCV a partir do código-fonte

Instale as dependências de compilação do OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

Transfira, configure e compile o OpenCV 4.11.0 com os módulos contrib (referência: [tutorial de instalação do OpenCV no Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

```bash
wget -O opencv-4.11.0.zip https://github.com/opencv/opencv/archive/4.11.0.zip
wget -O opencv_contrib-4.11.0.zip https://github.com/opencv/opencv_contrib/archive/4.11.0.zip
unzip opencv-4.11.0.zip
unzip opencv_contrib-4.11.0.zip
mkdir -p build && cd build

cmake -DBUILD_opencv_world=ON \
  -DBUILD_SHARED_LIBS=ON \
  -DCMAKE_INSTALL_PREFIX=install \
  -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.11.0/modules ../opencv-4.11.0 \
  -DWITH_GSTREAMER=ON \
  -DHIGHGUI_ENABLE_PLUGINS=ON

cmake --build . --target install
```

As bibliotecas partilhadas são instaladas em `<build>/install/lib/`. Utilize o diretório `install` como `OPENCV_INSTALL_ROOT` nos passos seguintes.

#### Vulkan SDK

Instale o Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Se estiver a utilizar o Ubuntu 22.04, atualize também os controladores MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Dependências adicionais para Ubuntu 24.04

Se estiver a utilizar o Ubuntu 24.04, instale os pacotes adicionais necessários:

```bash
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libnsl2 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly -y

DEP_PKG_LIST="https://launchpad.net/ubuntu/+archive/primary/+files/libmpdec3_2.5.1-2build2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10-minimal_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10-stdlib_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libpython3.10_3.10.4-3_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libprotobuf23_3.12.4-1ubuntu7_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libgoogle-glog0v5_0.5.0+really0.4.0-2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libtiff5_4.3.0-6_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libilmbase25_2.5.7-2_amd64.deb \
    https://launchpad.net/ubuntu/+archive/primary/+files/libopenexr25_2.5.7-1_amd64.deb"

for pkg in $DEP_PKG_LIST
do
    echo $pkg
    wget $pkg
    sudo dpkg -i *.deb
    rm *.deb
done
```

<!-- @os:end -->

## Conceitos fundamentais

A CVML Library fornece uma API C++ simples em que cada funcionalidade de perceção (estimativa de profundidade, deteção de rostos, malha facial) tem o seu próprio ficheiro de cabeçalho e objeto de funcionalidade. Não trabalha diretamente com modelos brutos — a biblioteca trata automaticamente do carregamento de modelos, pré-processamento e inferência.

### Funcionalidades disponíveis

| Funcionalidade | Ficheiro de cabeçalho | Descrição |
|---------|------------|-------------|
| **Estimativa de profundidade** | `cvml-depth-estimation.h` | Gera mapas de profundidade por pixel a partir de imagens RGB |
| **Deteção de rostos** | `cvml-face-detector.h` | Deteta rostos com caixas delimitadoras, pontos de referência (olhos, nariz, boca) e pontuações de confiança |
| **Malha facial** | `cvml-face-mesh.h` | Rastreia geometria facial detalhada com pontos de malha densa |

### Modelo de programação

Todas as aplicações CVML seguem o mesmo padrão de quatro passos:

1. **Criar um contexto** — O `amd::cvml::Context` gere recursos partilhados, como o registo de logs e a seleção do backend de inferência.
2. **Criar um objeto de funcionalidade** — Instancie a funcionalidade específica (por exemplo, `amd::cvml::DepthEstimation`) associada ao contexto.
3. **Envolver os dados de entrada** — Utilize `amd::cvml::Image` para encapsular o seu buffer de imagem RGB sem copiar dados.
4. **Executar** — Chame o método de processamento da funcionalidade e leia os resultados.

```cpp
// Step 1: Create context
auto context = amd::cvml::CreateContext();

// Step 2: Create feature object
amd::cvml::DepthEstimation depth_estimation(context);

// Step 3: Wrap input image (RGB, uint8, no copy)
amd::cvml::Image input(amd::cvml::Image::Format::kRGB,
                       amd::cvml::Image::DataType::kUint8,
                       width, height, data_pointer);

// Step 4: Execute
amd::cvml::Image output(amd::cvml::Image::Format::kGrayScale,
                        amd::cvml::Image::DataType::kFloat32,
                        width, height, nullptr);
depth_estimation.GenerateDepthMap(input, &output);

// Cleanup
context->Release();
```

### Backend de Inferência

A biblioteca seleciona automaticamente o melhor hardware (GPU ou NPU) para cada operação. Também é possível definir o backend explicitamente:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Nota:** As funcionalidades que utilizam o backend ONNX para operações de NPU podem apresentar uma latência de arranque mais longa na primeira execução. As execuções seguintes serão mais rápidas.

> **Nota:** Se o controlador da NPU não estiver instalado no sistema de destino, a biblioteca Ryzen AI CVML recorrerá automaticamente ao backend de GPU para as operações de inferência.

## Compilar as Aplicações de Exemplo

A CVML Library inclui aplicações de exemplo prontas a compilar para cada funcionalidade. Vamos compilá-las todas de uma vez.

1. Defina a variável de ambiente `OPENCV_INSTALL_ROOT` para apontar para a sua instalação do OpenCV:

   <!-- @os:windows -->
   ```cmd
   rem Set the OpenCV path (Windows)
   rem Point to the build subfolder inside your OpenCV installation
   rem (e.g. if you extracted OpenCV to C:\opencv, use C:\opencv\build)
   rem CMake's find_package needs this folder to locate OpenCVConfig.cmake
   set OPENCV_INSTALL_ROOT=C:\opencv\build
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Set the OpenCV path (Linux)
   export OPENCV_INSTALL_ROOT=/path/to/opencv
   ```
   <!-- @os:end -->

2. Compile os exemplos com o CMake:

   <!-- @os:windows -->
   ```cmd
   rem Build the samples (Windows)
   cd samples
   mkdir build
   cmake -S %CD% -B %CD%\build -DOPENCV_INSTALL_ROOT=%OPENCV_INSTALL_ROOT% -DCMAKE_PREFIX_PATH=%OPENCV_INSTALL_ROOT%
   cmake --build %CD%\build --config Release
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Build the samples (Linux)
   cd samples
   mkdir build
   cmake -S $PWD -B $PWD/build -DOPENCV_INSTALL_ROOT="$OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$OPENCV_INSTALL_ROOT"
   cmake --build $PWD/build --config Release
   ```
   <!-- @os:end -->

   Após uma compilação bem-sucedida, os executáveis encontram-se em:

   <!-- @os:windows -->
   ```
   samples\build\cvml-sample-face-detection\Release\cvml-sample-face-detection.exe
   samples\build\cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe
   samples\build\cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```
   samples/build/cvml-sample-face-detection/cvml-sample-face-detection
   samples/build/cvml-sample-depth-estimation/cvml-sample-depth-estimation
   samples/build/cvml-sample-face-mesh/cvml-sample-face-mesh
   ```
   <!-- @os:end -->

3. Antes de executar qualquer exemplo, certifique-se de que os ficheiros de runtime da CVML estão acessíveis:

   <!-- @os:windows -->
   ```cmd
   rem Add the CVML runtime folder to PATH (Windows)
   set PATH=%CD%\..\windows;%PATH%
   rem Add OpenCV runtime libraries to PATH
   set PATH=%OPENCV_INSTALL_ROOT%\x64\vc16\bin;%PATH%
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   # Add the CVML runtime folder to LD_LIBRARY_PATH (Linux)
   export LD_LIBRARY_PATH=$PWD/../linux:$LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=/opt/xilinx/xrt/lib:$LD_LIBRARY_PATH
   # Add OpenCV runtime libraries to LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=$OPENCV_INSTALL_ROOT/lib:$LD_LIBRARY_PATH
   ```
   <!-- @os:end -->

## Executar a Deteção de Rostos

O exemplo de deteção de rostos deteta rostos numa imagem, vídeo ou transmissão de câmara ao vivo. Desenha caixas delimitadoras, pontuações de confiança e cinco pontos de referência faciais (dois olhos, nariz e dois cantos da boca) em cada rosto detetado.

Primeiro, navegue até à pasta do executável de deteção de rostos:

<!-- @os:windows -->
```cmd
cd build\cvml-sample-face-detection\Release
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
cd build/cvml-sample-face-detection
```
<!-- @os:end -->

Em seguida, descarregue uma imagem de exemplo para usar como entrada (fotografia de [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), de utilização gratuita via Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Execute a deteção de rostos na imagem de exemplo:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg
```
<!-- @os:end -->

Será apresentada uma janela com a imagem, mostrando caixas delimitadoras à volta dos rostos detetados, pontuações de confiança e pontos de referência faciais (olhos, nariz, cantos da boca).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Guarde a saída anotada num ficheiro:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

**Utilize o modelo preciso** para maior precisão (à custa da velocidade):

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -m precise
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -m precise
```
<!-- @os:end -->

A funcionalidade de deteção de rostos oferece duas variantes de modelo:

| Modelo | Velocidade | Precisão | Ideal para |
|-------|-------|----------|----------|
| `fast` (predefinição) | FPS mais elevado | Boa | Aplicações de câmara em tempo real |
| `precise` | FPS mais baixo | Máxima | Análise de fotografias, necessidades de alta precisão |


<!-- @os:windows -->
<!-- @test:id=cvml-build-sample-applications-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Build and run the samples inside a passwordless S4U scheduled task.

$ci = Join-Path $env:USERPROFILE "cvml-ci"
if (Test-Path $ci) {Remove-Item -Recurse -Force $ci}
New-Item -ItemType Directory -Force -Path $ci | Out-Null
$innerPs = Join-Path $ci "run_cvml.ps1"
$log = Join-Path $ci "cvml.log"

# Inner script (single-quoted here-string: not expanded here). It builds the
# samples and runs them (face detection twice, depth, and mesh), exiting
# non-zero on any failure. Its combined stdout+stderr is redirected to cvml.log
# by the task action below.
$inner = @'
$ErrorActionPreference = "Stop"
$ci = $PSScriptRoot
$code = 0
try {
  $env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
  $env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"
  if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
  if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}
  $work = Join-Path $ci "work"
  if (Test-Path $work) {Remove-Item -Recurse -Force $work}
  New-Item -ItemType Directory -Force -Path $work | Out-Null
  Copy-Item -Recurse -Force -Path (Join-Path $env:AMD_CVML_SDK_ROOT "*") -Destination $work
  $samplesDir = Join-Path $work "samples"
  $buildDir = Join-Path $samplesDir "build"
  Push-Location $samplesDir
  New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
  foreach ($sample in @("cvml-sample-face-detection", "cvml-sample-depth-estimation", "cvml-sample-face-mesh")) {
    $mainFile = Join-Path $samplesDir "$sample\main.cpp"
    $source = Get-Content -Path $mainFile -Raw
    $createContextLine = "auto context = amd::cvml::CreateContext();"
    $setBackendLine = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"
    if ($source -notmatch "SetInferenceBackend") {
      if (-not $source.Contains($createContextLine)) {throw "Could not find CreateContext line in: $mainFile"}
      $source = $source.Replace($createContextLine, "$createContextLine`r`n$setBackendLine")
      Set-Content -Path $mainFile -Value $source -NoNewline
    }
  }
  cmake -S (Get-Location).Path -B $buildDir -DOPENCV_INSTALL_ROOT="$env:OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$env:OPENCV_INSTALL_ROOT"
  cmake --build $buildDir --config Release --parallel
  $faceExe = Join-Path $buildDir "cvml-sample-face-detection\Release\cvml-sample-face-detection.exe"
  $depthExe = Join-Path $buildDir "cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe"
  $meshExe = Join-Path $buildDir "cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe"
  foreach ($exe in @($faceExe, $depthExe, $meshExe)) {if (-not (Test-Path $exe)) {throw "Expected executable was not found: $exe"}}
  $env:PATH = "$(Join-Path $samplesDir "..\windows");$env:PATH"
  $opencvRuntime = Join-Path $env:OPENCV_INSTALL_ROOT "x64\vc16\bin"
  if (-not (Test-Path $opencvRuntime)) {throw "OpenCV runtime DLL folder was not found: $opencvRuntime"}
  $env:PATH = "$opencvRuntime;$env:PATH"
  $inputImage = Join-Path $samplesDir "sample_face.jpg"
  curl.exe -L -o $inputImage "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
  $outputFaceFast = Join-Path $samplesDir "output_face_fast.jpg"
  $outputFacePrecise = Join-Path $samplesDir "output_face_precise.jpg"
  $outputDepth = Join-Path $samplesDir "output_depth.jpg"
  $outputMesh = Join-Path $samplesDir "output_mesh.jpg"
  Push-Location (Split-Path $faceExe)
  & $faceExe -i $inputImage -o $outputFaceFast
  if ($LASTEXITCODE -ne 0) {throw "Face detection default model failed with exit code $LASTEXITCODE."}
  & $faceExe -i $inputImage -o $outputFacePrecise -m precise
  if ($LASTEXITCODE -ne 0) {throw "Face detection precise model failed with exit code $LASTEXITCODE."}
  Pop-Location
  Push-Location (Split-Path $depthExe)
  & $depthExe -i $inputImage -o $outputDepth
  if ($LASTEXITCODE -ne 0) {throw "Depth estimation failed with exit code $LASTEXITCODE."}
  Pop-Location
  Push-Location (Split-Path $meshExe)
  & $meshExe -i $inputImage -o $outputMesh
  if ($LASTEXITCODE -ne 0) {throw "Face mesh failed with exit code $LASTEXITCODE."}
  Pop-Location
  foreach ($output in @($outputFaceFast, $outputFacePrecise, $outputDepth, $outputMesh)) {
    if (-not (Test-Path $output)) {throw "Expected output image was not created: $output"}
    if ((Get-Item $output).Length -le 0) {throw "Output image is empty: $output"}
  }
  Write-Output "CVML_ALL_SAMPLES_PASSED"
} catch {
  Write-Output ("CVML_ERROR: " + $_.Exception.Message)
  $code = 1
} finally {
  Pop-Location -ErrorAction SilentlyContinue
  if ($work -and (Test-Path $work)) {Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue}
}
exit $code
'@
Set-Content -Path $innerPs -Value $inner -Encoding UTF8

# Run via cmd so the inner script's full stdout+stderr (cmake, curl, and every
# sample executable, including any error text) is captured to cvml.log.
$taskName = "cvml_ci_run"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$innerPs`" > `"$log`" 2>&1"
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Force | Out-Null

try {
  Start-ScheduledTask -TaskName $taskName
  $deadline = (Get-Date).AddSeconds(1500)
  do {
    Start-Sleep -Seconds 5
    $state = (Get-ScheduledTask -TaskName $taskName).State
  } while ($state -eq "Running" -and (Get-Date) -lt $deadline)

  if (Test-Path $log) {Get-Content $log}

  if ($state -eq "Running") {throw "cvml S4U task did not finish within the time limit"}
  $result = (Get-ScheduledTaskInfo -TaskName $taskName).LastTaskResult
  if ($result -ne 0) {throw "cvml samples failed under S4U task (exit code $result)"}
}
finally {
  Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $ci -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cvml-build-sample-applications-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

export AMD_CVML_SDK_ROOT="${AMD_CVML_SDK_ROOT:-/home/user/RyzenAI-Library}"
export OPENCV_INSTALL_ROOT="${OPENCV_INSTALL_ROOT:-/home/user/build/install}"

if [ ! -d "$AMD_CVML_SDK_ROOT" ]; then
  echo "AMD_CVML_SDK_ROOT does not exist: $AMD_CVML_SDK_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT" ]; then
  echo "OPENCV_INSTALL_ROOT does not exist: $OPENCV_INSTALL_ROOT"
  exit 1
fi
if [ ! -d "$OPENCV_INSTALL_ROOT/lib" ]; then
  echo "OpenCV lib directory was not found: $OPENCV_INSTALL_ROOT/lib"
  exit 1
fi
if [ ! -f "$OPENCV_INSTALL_ROOT/lib/cmake/opencv4/OpenCVConfig.cmake" ]; then
  echo "OpenCVConfig.cmake was not found under: $OPENCV_INSTALL_ROOT/lib/cmake/opencv4"
  exit 1
fi

work="$PWD/cvml-test"
rm -rf "$work"
mkdir -p "$work"

cp -a "$AMD_CVML_SDK_ROOT"/. "$work"/

cleanup() {
  rm -rf "$work"
}
trap cleanup EXIT

samples_dir="$work/samples"
build_dir="$samples_dir/build"

cd "$samples_dir"
mkdir build

python3 - <<'PY'
from pathlib import Path

samples = [
    Path("cvml-sample-face-detection/main.cpp"),
    Path("cvml-sample-depth-estimation/main.cpp"),
    Path("cvml-sample-face-mesh/main.cpp"),
]

create_context_line = "auto context = amd::cvml::CreateContext();"
set_backend_line = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"

for path in samples:
    source = path.read_text()

    if "SetInferenceBackend" in source:
        continue

    if create_context_line not in source:
        raise SystemExit(f"Could not find CreateContext line in: {path}")

    source = source.replace(
        create_context_line,
        create_context_line + "\n" + set_backend_line,
        1,
    )

    path.write_text(source)
PY

cmake_config_log="$build_dir/cmake-configure.log"

cmake -S "$PWD" -B "$PWD/build" \
  -DOPENCV_INSTALL_ROOT="$OPENCV_INSTALL_ROOT" \
  -DCMAKE_PREFIX_PATH="$OPENCV_INSTALL_ROOT" 2>&1 | tee "$cmake_config_log"

if ! grep -q 'found version "4.11.0"' "$cmake_config_log"; then
  echo "CMake did not report OpenCV version 4.11.0."
  cat "$cmake_config_log"
  exit 1
fi

cmake --build "$PWD/build" --config Release --parallel "$(nproc)"

face_exe="$build_dir/cvml-sample-face-detection/cvml-sample-face-detection"
depth_exe="$build_dir/cvml-sample-depth-estimation/cvml-sample-depth-estimation"
mesh_exe="$build_dir/cvml-sample-face-mesh/cvml-sample-face-mesh"

for exe in "$face_exe" "$depth_exe" "$mesh_exe"; do
  if [ ! -x "$exe" ]; then
    echo "Expected executable was not found or is not executable: $exe"
    exit 1
  fi
done

export LD_LIBRARY_PATH="$PWD/../linux:${LD_LIBRARY_PATH:-}"

if [ -d /opt/xilinx/xrt/lib ]; then
  export LD_LIBRARY_PATH="/opt/xilinx/xrt/lib:$LD_LIBRARY_PATH"
  echo "Ryzen AI NPU driver/XRT runtime path found. Added /opt/xilinx/xrt/lib to LD_LIBRARY_PATH."
else
  echo "Ryzen AI NPU driver/XRT runtime was not found."
  echo "The samples explicitly set InferenceBackend::AUTO, so GPU fallback should be used if supported by the runtime."
fi

export LD_LIBRARY_PATH="$OPENCV_INSTALL_ROOT/lib:$LD_LIBRARY_PATH"

curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"

input_image="$samples_dir/sample_face.jpg"
output_face_fast="$samples_dir/output_face_fast.jpg"
output_face_precise="$samples_dir/output_face_precise.jpg"
output_depth="$samples_dir/output_depth.jpg"
output_mesh="$samples_dir/output_mesh.jpg"

cd "$(dirname "$face_exe")"
./cvml-sample-face-detection -i "$input_image" -o "$output_face_fast"
./cvml-sample-face-detection -i "$input_image" -o "$output_face_precise" -m precise

cd "$(dirname "$depth_exe")"
./cvml-sample-depth-estimation -i "$input_image" -o "$output_depth"

cd "$(dirname "$mesh_exe")"
./cvml-sample-face-mesh -i "$input_image" -o "$output_mesh"

for output in "$output_face_fast" "$output_face_precise" "$output_depth" "$output_mesh"; do
  if [ ! -s "$output" ]; then
    echo "Expected output image was not created or is empty: $output"
    exit 1
  fi
done
```
<!-- @test:end --> 
<!-- @os:end -->

## Integrar a CVML na Sua Própria Aplicação

Para utilizar a CVML Library no seu próprio projeto C++, adicione-a através do `find_package` do CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Onde `AMD_CVML_SDK_ROOT` aponta para a raiz da pasta da Ryzen AI CVML Library. Em seguida, inclua o cabeçalho apropriado para a funcionalidade pretendida:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Próximos Passos

Para cada exemplo abaixo, navegue primeiro até à respetiva pasta executável, seguindo o mesmo padrão da secção [Running Face Detection](#running-face-detection) acima (por exemplo, `cd build\cvml-sample-depth-estimation\Release` no Windows ou `cd build/cvml-sample-depth-estimation` no Linux). No Windows, adicione `.exe` a cada comando (por exemplo, `cvml-sample-depth-estimation.exe`).

- **Experimente a Estimativa de Profundidade**: Execute `cvml-sample-depth-estimation -i sample_face.jpg` para gerar um mapa de profundidade colorizado — os objetos mais próximos aparecem em cores quentes, os mais distantes em cores frias
- **Explore a Malha Facial**: Execute `cvml-sample-face-mesh -i sample_face.jpg` para ver o rastreio denso da geometria facial com pontos de malha detalhados
- **Processe ficheiros de vídeo**: Use as flags `-i` e `-o` em qualquer exemplo para processar vídeos (por exemplo, `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Compare variantes de modelo**: Experimente `-m precise` em vez do valor predefinido `-m fast` na deteção facial para constatar em primeira mão o compromisso entre precisão e velocidade
- **Crie a sua própria aplicação**: Use a integração com o CMake e a API de C++ para adicionar funcionalidades CVML às suas próprias aplicações C++
- **Combine funcionalidades**: Encadeie a deteção facial com a estimativa de profundidade na mesma aplicação para uma compreensão de cena mais rica
- **Explore o código-fonte**: Leia a [Ryzen AI CVML Library no GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) para documentação de cabeçalhos, exemplos adicionais e detalhes da API