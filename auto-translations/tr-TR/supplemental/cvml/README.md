<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış

[Ryzen AI CVML Kitaplığı](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library), derinlik tahmini, yüz algılama ve yüz ağı (mesh) izleme dahil olmak üzere güçlü, cihaz üzerinde algı yetenekleri sunan bir AMD C++ bilgisayarlı görü ve makine öğrenimi araç setidir. Ryzen AI sürücüleri üzerine inşa edilen kitaplık, çıkarım için mevcut en iyi donanımı (GPU veya NPU) otomatik olarak seçer ve model eğitimi veya çerçeve entegrasyonu ile uğraşmadan C++ uygulamalarınıza AI özellikleri eklemenize olanak tanır. Tüm işlemler sisteminizde yerel olarak gerçekleşir, bu da onu gizliliğe duyarlı, düşük gecikmeli uygulamalar için ideal hale getirir.

Bu kılavuz, Ryzen AI CVML Kitaplığı'nı nasıl kuracağınızı, birlikte gelen örnek uygulamaları nasıl derleyeceğinizi ve bir örnek görüntü üzerinde yüz algılamayı nasıl çalıştıracağınızı öğretir.

## Neler Öğreneceksiniz

- Sisteminizde ön koşulları nasıl kuracağınızı ve Ryzen AI CVML Kitaplığı'nı nasıl ayarlayacağınızı
- CVML C++ API'sinin nasıl çalıştığını: bağlamlar (context), özellik nesneleri ve görüntü arabellekleri
- CMake ve OpenCV kullanarak birlikte gelen örnek uygulamaları nasıl derleyip çalıştıracağınızı
- Sınırlayıcı kutular ve dönüm noktalarıyla bir görüntü üzerinde yüz algılamayı nasıl çalıştıracağınızı
- CVML özelliklerini kendi C++ uygulamalarınıza nasıl entegre edeceğinizi

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu
<!-- @require:driver -->

## Ek Bağımlılıklar

Başlamadan önce, aşağıdakilere sahip olduğunuzdan emin olun:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — `opencv-4.11.0-windows.exe` dosyasını indirin, çalıştırın ve yerel bir klasöre (örn. `C:\opencv`) çıkarın
- [CMake](https://cmake.org/download/) — Windows x86-64 MSI yükleyicisini indirin ve kurulum sırasında **"Add CMake to the system PATH for all users"** seçeneğini işaretleyin
- [Ryzen AI NPU sürücüsü](https://ryzenai.docs.amd.com/en/latest/inst.html) — mevcut en güncel sürümü yükleyin
- "Desktop development with C++" iş yükü (MSVC derleyicisi, Windows SDK ve C++ derleme araçlarını içerir) ile birlikte [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — kaynak koddan derlenmelidir (Ubuntu 22.04 ve 24.04'teki apt paketleri 4.11 sürümünü sağlamaz). Aşağıdaki [Building OpenCV from Source](#building-opencv-from-source) bölümüne bakın.
- CMake — apt aracılığıyla kurun:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 veya 24.04 (çekirdek >= 6.11.0-21-generic)
- [Ryzen AI NPU sürücüsü](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (Linux yükleyicisi — NPU çıkarımı için gereklidir)
- Vulkan SDK (aşağıdaki [Vulkan SDK](#vulkan-sdk) bölümünde kurulmaktadır)
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

## CVML Kitaplığının Kurulumu

Bir hesabınız yoksa [account.amd.com](https://account.amd.com) adresinden bir AMD hesabı oluşturun, ardından Ryzen AI CVML Kitaplığı'nı aşağıdaki portal bağlantısından indirmek için oturum açın:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

İndirdikten sonra, paketi yerel bir dizine (örn. Windows'ta `C:\RyzenAI-Library` veya Linux'ta `~/RyzenAI-Library`) çıkarın ve `AMD_CVML_SDK_ROOT` ortam değişkenini çıkarılan konuma ayarlayın:

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

Kitaplık paketi aşağıdaki yapıyı içerir:

| Klasör | İçerik |
|--------|----------|
| `cmake/` | CMake'in `find_package` işlevi için paketleme bilgisi |
| `include/` | C++ başlık dosyaları (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, vb.) |
| `windows/` | Windows için ikili dosyalar (derleme zamanı `.LIB` ve çalışma zamanı `.DLL`/`.GRAPHLIB`/`.AMODEL` dosyaları) |
| `linux/` | Linux için ikili dosyalar (derleme ve çalışma zamanı `.SO` dosyaları) |
| `samples/` | Kaynak kodlu bağımsız örnek uygulamalar |

<!-- @os:linux -->

### Linux'a Özgü Kurulum

#### OpenCV'yi Kaynak Koddan Derleme

OpenCV derleme bağımlılıklarını kurun:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

OpenCV 4.11.0'ı contrib modülleriyle birlikte indirin, yapılandırın ve derleyin (referans: [OpenCV Linux install tutorial](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

Paylaşılan kitaplıklar `<build>/install/lib/` altına kurulur. Sonraki adımlarda `install` dizinini `OPENCV_INSTALL_ROOT` olarak kullanın.

#### Vulkan SDK

Vulkan SDK'yı kurun:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

Ubuntu 22.04 çalıştırıyorsanız, MESA Vulkan sürücülerini de güncelleyin:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### Ek Ubuntu 24.04 Bağımlılıkları

Ubuntu 24.04 çalıştırıyorsanız, ek gerekli paketleri kurun:

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

## Temel Kavramlar

CVML Kitaplığı, her algı özelliğinin (derinlik tahmini, yüz algılama, yüz ağı) kendi başlık dosyasına ve özellik nesnesine sahip olduğu basit bir C++ API sunar. Ham modellerle çalışmazsınız — kitaplık model yüklemeyi, ön işlemeyi ve çıkarımı otomatik olarak yönetir.

### Mevcut Özellikler

| Özellik | Başlık Dosyası | Açıklama |
|---------|------------|-------------|
| **Derinlik Tahmini** | `cvml-depth-estimation.h` | RGB görüntülerden piksel başına derinlik haritaları oluşturur |
| **Yüz Algılama** | `cvml-face-detector.h` | Sınırlayıcı kutular, dönüm noktaları (gözler, burun, ağız) ve güven puanlarıyla yüzleri algılar |
| **Yüz Ağı (Face Mesh)** | `cvml-face-mesh.h` | Yoğun ağ noktalarıyla ayrıntılı yüz geometrisini izler |

### Programlama Modeli

Her CVML uygulaması aynı dört adımlı deseni izler:

1. **Bir Bağlam (Context) Oluşturun** — `amd::cvml::Context`, günlükleme ve çıkarım arka ucu seçimi gibi paylaşılan kaynakları yönetir.
2. **Bir Özellik Nesnesi Oluşturun** — Belirli özelliği (örn. `amd::cvml::DepthEstimation`) bağlama karşı örnekleyin.
3. **Girdi Verilerini Sarmalayın** — RGB görüntü arabelleğinizi veri kopyalamadan kapsüllemek için `amd::cvml::Image` kullanın.
4. **Çalıştırın** — Özelliğin işleme yöntemini çağırın ve sonuçları okuyun.

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

### Çıkarım Arka Ucu

Kitaplık, her işlem için en uygun donanımı (GPU veya NPU) otomatik olarak seçer. Arka ucu açıkça da ayarlayabilirsiniz:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Not:** NPU işlemleri için ONNX arka ucunu kullanan özellikler, ilk çalıştırmada daha uzun başlatma gecikmesi yaşayabilir. Sonraki çalıştırmalar daha hızlı olacaktır.

> **Not:** Hedef sistemde NPU sürücüsü kurulu değilse, Ryzen AI CVML kitaplığı çıkarım işlemleri için otomatik olarak GPU arka ucuna geri döner.

## Örnek Uygulamaları Derleme

CVML Kitaplığı, her özellik için derlemeye hazır örnek uygulamalar içerir. Hepsini bir kerede derleyelim.

1. OpenCV kurulumunuzu göstermesi için `OPENCV_INSTALL_ROOT` ortam değişkenini ayarlayın:

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

2. Örnekleri CMake ile derleyin:

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

   Başarılı bir derlemenin ardından, çalıştırılabilir dosyalar şurada bulunur:

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

3. Herhangi bir örneği çalıştırmadan önce, CVML çalışma zamanı dosyalarının erişilebilir olduğundan emin olun:

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

## Yüz Algılamayı Çalıştırma

Yüz algılama örneği, bir görüntüde, videoda veya canlı kamera akışında yüzleri algılar. Algılanan her yüz üzerine sınırlayıcı kutular, güven puanları ve beş yüz işareti noktası (iki göz, burun ve iki ağız kenarı) çizer.

Öncelikle, yüz algılama çalıştırılabilir dosya klasörüne gidin:

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

Ardından giriş olarak kullanılacak örnek bir görüntü indirin (fotoğraf [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/) tarafından, Pexels üzerinden ücretsiz kullanım için sunulmuştur):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**Yüz algılamayı örnek görüntü üzerinde çalıştırın:**

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

Algılanan yüzlerin etrafında sınırlayıcı kutuları, güven puanlarını ve yüz işareti noktalarını (gözler, burun, ağız kenarları) gösteren bir pencere açılacaktır.

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**Açıklamalı çıktıyı bir dosyaya kaydedin:**

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

Daha yüksek doğruluk için (hız pahasına) **hassas modeli kullanın**:

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

Yüz algılama özelliği iki model varyantı sunar:

| Model | Hız | Doğruluk | En Uygun Kullanım |
|-------|-------|----------|----------|
| `fast` (varsayılan) | Daha yüksek FPS | İyi | Gerçek zamanlı kamera uygulamaları |
| `precise` | Daha düşük FPS | En iyi | Fotoğraf analizi, yüksek doğruluk gerektiren durumlar |


<!-- @os:windows -->
<!-- @test:id=cvml-build-sample-applications-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$env:AMD_CVML_SDK_ROOT = "C:\RyzenAI-Library"
$env:OPENCV_INSTALL_ROOT = "C:\Users\user\opencv\build"

if (-not (Test-Path $env:AMD_CVML_SDK_ROOT)) {throw "AMD_CVML_SDK_ROOT does not exist: $env:AMD_CVML_SDK_ROOT"}
if (-not (Test-Path $env:OPENCV_INSTALL_ROOT)) {throw "OPENCV_INSTALL_ROOT does not exist: $env:OPENCV_INSTALL_ROOT"}

$work = Join-Path (Get-Location) "cvml-test"
if (Test-Path $work) {Remove-Item -Recurse -Force $work}
New-Item -ItemType Directory -Force -Path $work | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $env:AMD_CVML_SDK_ROOT "*") -Destination $work

$samplesDir = Join-Path $work "samples"
$buildDir = Join-Path $samplesDir "build"

Push-Location $samplesDir

try {
  New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
  foreach ($sample in @("cvml-sample-face-detection", "cvml-sample-depth-estimation", "cvml-sample-face-mesh")) {
    $mainFile = Join-Path $samplesDir "$sample\main.cpp"
    $source = Get-Content -Path $mainFile -Raw

    $createContextLine = "auto context = amd::cvml::CreateContext();"
    $setBackendLine = "  context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);"

    if ($source -notmatch "SetInferenceBackend") {
      if (-not $source.Contains($createContextLine)) {
        throw "Could not find CreateContext line in: $mainFile"
      }

      $source = $source.Replace($createContextLine, "$createContextLine`r`n$setBackendLine")
      Set-Content -Path $mainFile -Value $source -NoNewline
    }
  }

  cmake -S (Get-Location).Path -B $buildDir -DOPENCV_INSTALL_ROOT="$env:OPENCV_INSTALL_ROOT" -DCMAKE_PREFIX_PATH="$env:OPENCV_INSTALL_ROOT"
  cmake --build $buildDir --config Release --parallel

  $faceExe = Join-Path $buildDir "cvml-sample-face-detection\Release\cvml-sample-face-detection.exe"
  $depthExe = Join-Path $buildDir "cvml-sample-depth-estimation\Release\cvml-sample-depth-estimation.exe"
  $meshExe = Join-Path $buildDir "cvml-sample-face-mesh\Release\cvml-sample-face-mesh.exe"

  foreach ($exe in @($faceExe, $depthExe, $meshExe)) {
    if (-not (Test-Path $exe)) {throw "Expected executable was not found: $exe"}
  }

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
}
finally {
  Pop-Location -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
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

## CVML'i Kendi Uygulamanıza Entegre Etme

CVML Kitaplığını kendi C++ projenizde kullanmak için, CMake'in `find_package` işlevi aracılığıyla ekleyin:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Burada `AMD_CVML_SDK_ROOT`, Ryzen AI CVML Kitaplığı klasörünün köküne işaret eder. Ardından istediğiniz özellik için uygun başlık dosyasını ekleyin:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Sonraki Adımlar

Aşağıdaki her örnek için, önce yukarıdaki [Running Face Detection](#running-face-detection) bölümüyle aynı düzeni izleyerek çalıştırılabilir klasörüne gidin (ör. Windows'ta `cd build\cvml-sample-depth-estimation\Release` veya Linux'ta `cd build/cvml-sample-depth-estimation`). Windows'ta her komutun sonuna `.exe` ekleyin (ör. `cvml-sample-depth-estimation.exe`).

- **Derinlik Tahminini Deneyin**: Renklendirilmiş bir derinlik haritası oluşturmak için `cvml-sample-depth-estimation -i sample_face.jpg` komutunu çalıştırın — yakındaki nesneler sıcak renklerde, uzaktakiler soğuk renklerde görünür
- **Face Mesh'i Keşfedin**: Ayrıntılı mesh noktalarıyla yoğun yüz geometrisi izlemeyi görmek için `cvml-sample-face-mesh -i sample_face.jpg` komutunu çalıştırın
- **Video dosyalarını işleyin**: Videoları işlemek için herhangi bir örnekte `-i` ve `-o` bayraklarını kullanın (ör. `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Model varyantlarını karşılaştırın**: Doğruluk/hız dengesini birebir görmek için yüz algılamada varsayılan `-m fast` yerine `-m precise` seçeneğini deneyin
- **Kendi uygulamanızı oluşturun**: Kendi C++ uygulamalarınıza CVML özellikleri eklemek için CMake entegrasyonunu ve C++ API'sini kullanın
- **Özellikleri birleştirin**: Daha zengin bir sahne anlayışı için aynı uygulamada yüz algılamayı derinlik tahminiyle zincirleyin
- **Kaynak koduna göz atın**: Başlık belgeleri, ek örnekler ve API ayrıntıları için [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) sayfasını okuyun