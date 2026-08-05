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

Sıfırdan bir GPU çekirdeği yazın, derleyin, bir AMD GPU üzerinde başlatın ve kullanımın yükseldiğini görün. Bu kılavuz, GPU hesaplamasının gerçekte nasıl çalıştığını gösterir: çekirdek kodunu yazın ve binlerce iş parçacığı üzerinde paralel olarak çalıştırın.

> **Not**: Bu, ek hata ayıklama ve değişiklikler gerektirebilecek oldukça karmaşık bir kılavuzdur.

## Neler Öğreneceksiniz

<!-- @os:windows -->
- GPU çekirdeklerinin nasıl çalıştığı: gridler, bloklar, iş parçacıkları ve bunları veriye eşleyen indeksleme modeli
- AMD ROCm/HIP yığınının, CUDA tarzı kodun değiştirilmeden AMD GPU'larda çalışmasına nasıl olanak sağladığı
- `torch.cuda._compile_kernel` kullanarak bir çekirdeğin çalışma zamanında (runtime) nasıl derleneceği
- Python'dan içe aktarılabilen, `CUDAExtension` + pybind11 ile bir yerel C++ çekirdek uzantısının nasıl oluşturulacağı
<!-- @os:end -->
<!-- @os:linux -->
- GPU çekirdeklerinin nasıl çalıştığı: gridler, bloklar, iş parçacıkları ve bunları veriye eşleyen indeksleme modeli
- AMD ROCm/HIP yığınının, CUDA tarzı kodun değiştirilmeden AMD GPU'larda çalışmasına nasıl olanak sağladığı
- `torch.cuda._compile_kernel` kullanarak bir çekirdeğin çalışma zamanında (runtime) nasıl derleneceği
- Python'dan içe aktarılabilen, `CUDAExtension` + pybind11 ile bir yerel C++ çekirdek uzantısının nasıl oluşturulacağı
- Çekirdek yürütme süresinin nasıl ölçüleceği ve `amd-smi` ile canlı GPU kullanımının nasıl izleneceği
<!-- @os:end -->

---

Bu kılavuz, çekirdek geliştirme için iki yaklaşımı ele almaktadır:

<!-- @os:windows -->
| Yaklaşım | Giriş noktası |
|---|---|
| **JIT Derleme** | `torch.cuda._compile_kernel`, çekirdeği bir Python dizesi olarak yazın, herhangi bir derleme adımı olmadan |
| **C++ Uzantısı** | `CUDAExtension` + pybind11: bir `.cu` dosyasını yerel bir `.pyd` dosyasına derleyin ve içe aktarın |
<!-- @os:end -->
<!-- @os:linux -->
| Yaklaşım | Giriş noktası |
|---|---|
| **JIT Derleme** | `torch.cuda._compile_kernel`, çekirdeği bir Python dizesi olarak yazın, herhangi bir derleme adımı olmadan |
| **C++ Uzantısı** | `CUDAExtension` + pybind11: bir `.cu` dosyasını yerel bir `.so` dosyasına derleyin ve içe aktarın |
<!-- @os:end -->

Her iki yaklaşım da AMD GPU'lar üzerinde çalışır. Bu, PyTorch'un ROCm derlemesinin tüm CUDA API yüzeyini HIP'e eşlemesi sayesinde mümkündür. Bu, `torch.cuda`, `CUDAExtension` ve CUDA çekirdek sözdiziminin AMD donanımında şeffaf bir şekilde çalışması anlamına gelir.

---

## Arka Plan

### GPU Çekirdeği Nedir?

GPU çekirdeği, binlerce GPU iş parçacığı üzerinde aynı anda paralel olarak çalışan bir fonksiyondur. Her çağrıda bir kez çalışan bir CPU fonksiyonunun aksine, bir çekirdek, her biri çok sayıda **iş parçacığı (thread)** içeren bir **blok (block)** **gridi** ile başlatılır ve hepsi farklı veriler üzerinde aynı kodu çalıştırır.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### İş Parçacığı İndeksleme Modeli

Bir çekirdeği başlatırken iki boyut belirtirsiniz:

| Değişken | Anlamı |
|---|---|
| `gridDim` | Griddeki blok sayısı |
| `blockDim` | Blok başına iş parçacığı sayısı |

Her iş parçacığının erişebildiği üç yerleşik salt okunur değişken vardır:

| Değişken | Anlamı |
|---|---|
| `blockIdx.x` | Bu iş parçacığının ait olduğu blok |
| `blockDim.x` | Bir bloktaki iş parçacığı sayısı |
| `threadIdx.x` | İş parçacığının kendi bloğu içindeki indeksi |

### Global İş Parçacığı Kimliği

Bu değişkenler birleştirilerek küresel olarak benzersiz bir iş parçacığı indeksi hesaplanır:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Toplam iş parçacığı sayısı = `gridDim.x * blockDim.x`. Her iş parçacığı bir öğeyi bağımsız olarak işler. Bu, **veri paralelliğinin (data parallelism)** temelidir. Aynı işlem, iş parçacıkları arasında herhangi bir bağımlılık olmadan birçok öğe üzerinde aynı anda çalışır.

---

### GPU Yürütme Modeli: Dalga Cepheleri (Wavefronts)

AMD GPU'lar, iş parçacıklarını **wavefront** adı verilen **32**'lik gruplar halinde yürütür. Bir wavefront'taki tüm iş parçacıkları aynı komutu aynı anda çalıştırır. Bu durum, en uygun blok boyutu seçimlerini etkiler (256 iş parçacığı = 8 wavefront = iyi zamanlama verimliliği).

### AMD GPU Programlama: HIP + ROCm

**ROCm**, AMD'nin açık kaynaklı GPU hesaplama yığınıdır (sürücüler, derleyiciler, kütüphaneler, çalışma zamanı). **HIP** bunun üzerinde yer alır ve sözdizimsel olarak CUDA ile aynı olacak şekilde tasarlanmıştır. PyTorch'un ROCm derlemesi, `torch.cuda.*`'ı şeffaf bir şekilde HIP'e eşler, böylece aynı kod AMD GPU'larda çalışır.

---

### PyTorch + AMD/HIP

PyTorch, CUDA API yüzeyinin (`torch.cuda.*`) şeffaf bir şekilde HIP tarafından desteklendiği bir ROCm derlemesi sunar. Bu şu anlama gelir:

- `torch.cuda.is_available()`, ROCm ile AMD GPU'larda çalışır
- `tensor.to("cuda")`, AMD GPU üzerinde ayırma yapar
- `torch.version.hip`, HIP sürümünü gösterir

PyTorch ayrıca, ayrı bir derleme adımına gerek kalmadan ham bir çekirdek dizesini JIT olarak derleyip çağrılabilir bir nesne elde etmek için üst düzey bir kısayol olan `torch.cuda._compile_kernel()` fonksiyonunu sunar.

---

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Ön Koşullar - Windows
- En son sürümü yükleyin: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux'ta, seçtiğiniz dizinde bir terminal açın ve ROCm+Pytorch'un önceden kurulu olduğu bir venv oluşturmak için aşağıdaki komutları izleyin.
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
**Kullanıcınıza GPU cihazlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp tekrar açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
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
Windows'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **İpucu**: Windows kullanıcılarının bazı PowerShell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini (Execution Policy) değiştirmesi gerekebilir (örneğin,
> RemoteSigned veya Unrestricted olarak ayarlamak).

<!-- @os:end -->
### Temel Bağımlılıkların Kurulumu
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
> **Not:** Bu playbook için, özel çekirdek derlemesi tam geliştirme başlıklarını gerektirdiğinden, ROCm ve PyTorch'un Ryzen AI Halo üzerinde bile sanal ortama kurulması gerekir.

ROCm'yi kurun:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorch'u kurun:
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

### Ek Bağımlılıkların Kurulumu

<!-- @os:linux -->
Linux C/C++ derleme araç zincirini kurun. Bu, sistem düzeyinde bir bağımlılıktır ve `CUDAExtension`, `.cu` dosyalarından yerel `.so` modülleri oluşturduğu için C++ eklenti (extension) örnekleri için gereklidir.

Bunu Linux makinesinde, oluşturulan Python sanal ortamının dışında, bir kez çalıştırın:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

`kernel-env` sanal ortamını etkinleştirdikten sonra, Python derleme bağımlılıklarını kurun:
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
Lütfen [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) veya [daha yeni bir sürümün](https://visualstudio.microsoft.com/vs/community/) **Desktop development with C++** iş yüküyle birlikte kurulu olduğundan emin olun.

> **Not**: Bu Visual Studio C++ ortam kurulumu yalnızca **C++ Extension** yaklaşımı için gereklidir. JIT Compilation yaklaşımı için gerekli değildir.

Bir PowerShell terminali açın ve C++ eklentisini oluşturmadan önce aşağıdaki komutları çalıştırın.

**Adım 1: Kurulu Visual Studio C++ ortamını bulma**

**(A) Visual Studio Installer ile birlikte kurulan `vswhere.exe` dosyasını bulun**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) C++ derleme araçlarına sahip Visual Studio 2022 veya daha yeni bir sürümden `vcvars64.bat` dosyasını bulun**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) Kullanılan Visual Studio C++ Ortamını yazdırın**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**Adım 2: Visual Studio C++ derleme ortamını etkinleştirme**

**(A) `vcvars64.bat` dosyasını çalıştırın ve ayarladığı ortamı yakalayın**

Bu, `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` ve Windows SDK yollarının kullanılabilir olmasını sağlar.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) Visual Studio ortam değişkenlerini bu PowerShell oturumuna aktarın**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**Adım 3: Microsoft C++ derleyicisinin kullanılabilir olduğunu doğrulayın**

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

#### Ortam Değişkenlerini Ayarlama
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
AMD GPU'nun görünür olduğunu şu şekilde doğrulayın:
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

## Gerekli Dosyaları İndirin

Aşağıdaki dizin yapısını oluşturmak için **2 yeni klasör** oluşturun ve ilgili dosyaları indirin:

| Dizin | İndirilecek Dosyalar | Açıklama |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Vektör toplama çekirdeği için JIT ve C++ eklenti dosyaları |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Matris çarpımı çekirdeği için JIT ve C++ eklenti dosyaları |


## Uygulamalı Örnekler

### Uygulamalı Örnek 1: Vektör Toplama

#### Yaklaşım A: JIT Derleme

JIT (Just-In-Time) derleme, çekirdeğin Python içinde ham bir C++ dizesi olarak yazılması ve ekstra derleme adımlarına gerek kalmadan çalışma zamanında derlenmesi anlamına gelir.

[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) dosyasını kullanmak için, dosyanın indirildiğinden emin olun ve şunu çalıştırın:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Önemli Kod Parçaları**
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
> **İpucu**: Betik ayrıca, çekirdek çalışması sırasında tepe ve ortalama GPU kullanımını kaydetmek için her 100ms'de bir `amd-smi`'yi sorgulayan bir arka plan iş parçacığı (thread) da başlatır.
<!-- @os:end -->

> **Not**: **Blok Boyutu Neden 256?** <br>
> - Çekirdek, **blok başına 256 iş parçacığı** kullanır çünkü bu, **AMD GPU'ların wavefront yürütme modeliyle** iyi uyum sağlar.
> - AMD donanımının iş parçacıklarını 32'lik gruplar halinde yürüttüğünü ve bunun sonucunda blok başına 8 wavefront oluştuğunu hatırlayın. (8 wavefront x 32 iş parçacığı = 1 blok)


**İş yükünün yaptığı şey:**

Çekirdek, GPU kullanımını göstermek için yapay olarak ekstra iş ekler:

- Tensörde **100.000.000 eleman**
- Her çekirdek çalıştırmasında eleman başına **iç döngü 1.000 kez** çalışır  
- Toplam **200 çekirdek çalıştırması**

**Matematik:**  
- Her eleman: 1 × 1.000 iterasyon × 200 çalıştırma = 200.000 kadar artırılır  
- Nihai sonuç: 1.0 (başlangıç değeri) + 200.000 (eklemeler) = 200.001,0

**İç döngü neden var?**  
- `for (int i = 0; i < 1000; i++)` döngüsü olmadan, 200 çalıştırma anında tamamlanır ve izleme araçları anlamlı bir GPU kullanımı yakalayamaz. Yapay iş, her çekirdek çalıştırmasının izleme araçlarının performansı ölçebilmesi için yeterince uzun sürmesini sağlar.

<!-- @os:linux -->
**Beklenen çıktı:**[Performans sayıları değişiklik gösterebilir]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Windows üzerinde `amd-smi` desteklenmemektedir. GPU kullanımını izlemek için, programı çalıştırdığınızda kısa bir kullanım artışı görmeniz gereken Görev Yöneticisi'ni kullanabilirsiniz.

**Beklenen çıktı:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Aferin! İlk GPU çekirdeğinizi az önce çalıştırdınız.**

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
#### Yaklaşım B: C++ Uzantısı

İkinci yaklaşım daha manueldir: çekirdeği ve Python bağlamasını tek bir `.cu` dosyasına yazın, PyTorch'un derleme sistemini kullanarak yerel olarak derleyin ve Python'a aktarın.

<!-- @os:windows -->
> **Not**: C++ Uzantısı yaklaşımı, PyTorch `.cu` kaynak dosyasını yerel bir `.pyd` uzantı modülüne derlediğinden Visual Studio C++ derleme ortamını gerektirir. Bu yerel uzantının derlenmesi, Visual Studio tarafından sağlanan Microsoft C++ araç zincirine (derleyici, bağlayıcı ve derleme araçları) bağlıdır. Uzantıyı derlemeden önce kurulum bölümündeki Visual Studio etkinleştirme komutlarını çalıştırın.
<!-- @os:end -->

Henüz indirmediyseniz aşağıdaki dosyaları indirin:
<!-- @os:windows -->
| Dosya | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Çekirdek + başlatıcı + pybind11 bağlaması, hepsi tek bir dosyada |
| [setup.py](assets/Vector_Addition/setup.py) | `.cu` dosyasını bir `.pyd` dosyasına derlemek için `CUDAExtension` kullanan derleme betiği |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Derlenmiş yapıları çalıştıran Python betiği |
<!-- @os:end -->

<!-- @os:linux -->
| Dosya | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Çekirdek + başlatıcı + pybind11 bağlaması, hepsi tek bir dosyada |
| [setup.py](assets/Vector_Addition/setup.py) | `.cu` dosyasını bir `.so` dosyasına derlemek için `CUDAExtension` kullanan derleme betiği |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Derlenmiş yapıları çalıştıran Python betiği |
<!-- @os:end -->

#### **Adım 1: Çekirdek, başlatıcı ve bağlama** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**İpucu**: Neden `hipDeviceSynchronize()` kullanılır? <br>
> - GPU çekirdek başlatmaları asenkrondur. CPU `add_one<<<grid_size, block_size>>>(data, n);` çalıştırdığında, GPU'nun beklemesini beklemeden bir sonraki komutu hemen yürütür. `hipDeviceSynchronize()`, CPU'yu GPU çekirdeği tamamlanana kadar beklemeye zorlar.

#### **Adım 2: Derleme**
```bash
pip install --no-build-isolation -v .
```
>**Not**: Bu komut, oluşturduğumuz .cu dosyasını derlemek için geçerli dizinde `setup.py` dosyasını arar.


`CUDAExtension`, `torch.utils.cpp_extension` içinden bir CUDA derleme yardımcısıdır. ROCm ile PyTorch, **`CUDAExtension`'ı `nvcc` yerine `hipcc` kullanacak şekilde yeniden yönlendirir**. ROCm, derleme yolunu ele geçirir ve HIP derleyicisi üzerinden yönlendirerek CUDA kodunu AMD'ye taşır.

Bu işlem aşağıdaki dosyaları üretir:
<!-- @os:windows -->
- `build/`: `.pyd` dosyalarını içeren dizin
- `add_one_kernel.hip`: `.cu` dosyasının hipify edilmesiyle oluşturulan HIP kaynağı; `hipcc`'nin fiilen derlediği şey budur
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: `.so` dosyalarını içeren dizin
- `add_one_kernel.hip`: `.cu` dosyasının hipify edilmesiyle oluşturulan HIP kaynağı; `hipcc`'nin fiilen derlediği şey budur
<!-- @os:end -->

#### **Adım 3: Python'dan kullanma** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Çekirdeği çalışırken görmek için bu betiği çalıştırın:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**Beklenen çıktı:**
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

### İnceleme 2: Matris Çarpımı

Matris çarpımı **C = A × B** işlemini hesaplar; burada:
- **A** M×N boyutlarındadır (satır × sütun)
- **B** N×K boyutlarındadır
- **C** M×K boyutlarındadır (sonuç)

Her çıktı elemanı şu şekilde tanımlanır:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C'nin her bir elemanı bağımsız olarak hesaplanır, bu da işlemi GPU paralelliği için mükemmel hale getirir.

#### GPU İş Parçacıklarına Nasıl Eşlenir

Vektör toplamanın (1D) aksine, matris çarpımı **2D bir çıktı** üretir, bu nedenle **2D bir iş parçacığı ızgarası** kullanırız:

| | Vektör Toplama | Matris Çarpımı |
|---|---|---|
| **Çıktı şekli** | 1D dizi | 2D matris (M×K) |
| **İş parçacığı eşlemesi** | 1 iş parçacığı → 1 eleman | 1 iş parçacığı → 1 çıktı elemanı |
| **Başlatma deseni** | 1D ızgara: `(grid_x, 1, 1)` | 2D ızgara: `(grid_x, grid_y, 1)` |
| **Blok boyutu** | `(256, 1, 1)` | `(16, 16, 1)` = 256 iş parçacığı |

Her iş parçacığı, çıktı matrisi C'nin bir elemanını hesaplar. `(row, col)` konumundaki iş parçacığı, A'nın karşılık gelen satırını B'nin karşılık gelen sütunuyla çarparak `C[row][col]`'u hesaplar.

**Bellek Düzeni**: GPU belleği düz (1D) yapıdadır, ancak matrisler satır satır saklanır. `A[row][col]`'a erişmek için çekirdek `A[row * N + col]` kullanır.


#### Yaklaşım A: JIT Derlemesi:

İnceleme 1'de olduğu gibi, çekirdek Python içinde ham bir C++ dizesi olarak yazılır ve PyTorch'un yerleşik JIT'i aracılığıyla çalışma zamanında derlenir.


[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) dosyasını kullanmak için, indirildiğinden emin olun ve çalıştırın:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Anahtar Kod Parçacıkları**
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

Betik, sonucu küçük bir tolerans ile `torch.mm` ile karşılaştırarak doğrular. GPU'lardaki kayan nokta aritmetiği, paralel indirgeme sırası nedeniyle CPU uygulamalarına kıyasla küçük sayısal farklılıklar üretebilir.

<!-- @os:linux -->
**Beklenen çıktı:**[Performans rakamları değişebilir]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Windows'ta `amd-smi` desteklenmez. GPU kullanımını izlemek için, programı çalıştırdığınızda kısa bir kullanım artışı görmeniz gereken Görev Yöneticisi'ni kullanabilirsiniz.

**Beklenen çıktı:**
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
#### Yaklaşım B: C++ Uzantısı

İkinci yaklaşım daha manueldir: kernel ve Python bağlamasını tek bir `.cu` dosyasına yazın, bunu PyTorch'un derleme sistemini kullanarak yerel olarak derleyin ve Python'a aktarın.

<!-- @os:windows -->
> **Not**: C++ Uzantısı yaklaşımı, PyTorch'un `.cu` kaynak dosyasını yerel bir `.pyd` uzantı modülüne derlemesi nedeniyle Visual Studio C++ derleme ortamını gerektirir. Bu yerel uzantının derlenmesi, Visual Studio tarafından sağlanan Microsoft C++ araç zincirine (derleyici, bağlayıcı ve derleme araçları) bağlıdır. Uzantıyı derlemeden önce kurulum bölümündeki Visual Studio etkinleştirme komutlarını çalıştırın.
<!-- @os:end -->

Henüz indirmediyseniz aşağıdaki dosyaları indirin:
<!-- @os:windows -->
| Dosya | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması |
| [setup.py](assets/Matrix_Multiplication/setup.py) | `.cu` dosyasını bir `.pyd` dosyasına derlemek için `CUDAExtension` kullanan derleme betiği |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Oluşturulan yapıtları çalıştıran Python betiği |
<!-- @os:end -->
<!-- @os:linux -->
| Dosya | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması |
| [setup.py](assets/Matrix_Multiplication/setup.py) | `.cu` dosyasını bir `.so` dosyasına derlemek için `CUDAExtension` kullanan derleme betiği |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Oluşturulan yapıtları çalıştıran Python betiği |
<!-- @os:end -->

#### **Adım 1: Kernel, başlatıcı ve bağlama** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

Yürüyüş 1'deki `add_one_launcher` ile karşılaştırıldığında, buradaki başlatıcı:
- Bir yerine iki girdi tensörü alır
- Python'dan manuel boyut aktarımı olmadan üç boyutun tümünü (M, N, K) tensör şekillerinden türetir
- Yerinde değiştirmek yerine çıktı tensörü C'yi tahsis eder ve döndürür
- 2D başlatma şeklini ifade etmek için hem grid hem de blok için `dim3` kullanır

#### **Adım 2: Derleme**
```bash
pip install --no-build-isolation -v .
```
>**Not**: Bu komut, oluşturduğumuz .cu dosyasını derlemek için mevcut dizinde `setup.py` dosyasını arar.


Bu, aşağıdaki dosyaları üretir:
<!-- @os:windows -->
- `build/`: `.pyd` dosyalarını içeren dizin
- `matmul_kernel.hip`: `.cu` dosyasının hipify edilmesiyle oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği şey budur
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` dosyalarını içeren dizin
- `matmul_kernel.hip`: `.cu` dosyasının hipify edilmesiyle oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği şey budur
<!-- @os:end -->

#### **Adım 3: Python'dan kullanma** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Kernel'i çalışırken görmek için bu betiği çalıştırın:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Beklenen çıktı:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Harika! Az önce GPU üzerinde matris çarpımı gerçekleştirdiniz.** Bu önemli bir kilometre taşıdır çünkü matris çarpımı, aşağıdakiler gibi modern makine öğrenimi işlemlerinin temelini oluşturur:
- Sinir ağı katmanları
- Dikkat (attention) mekanizmaları
- Gömme (embedding) katmanları
- Transformer'lar

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

## Sonraki Adımlar

Temel paralel işlemler için hem JIT derlemesi hem de C++ uzantılarını kullanarak GPU kernellerini yazmayı, derlemeyi ve başlatmayı öğrendiniz.

**Performans optimizasyonları:**
- **Paylaşımlı bellek döşemesi (tiling)** - Global bellek erişimini azaltmak için veri bloklarını önbelleğe alma
- **Bellek birleştirme (coalescing)** - Bant genişliği için bellek erişim kalıplarını optimize etme

**Gerçek dünya algoritmaları:**
- **2D Evrişim (Convolution)** - Küçük bir filtre (kernel) bir görüntü üzerinde kaydırılarak her çıktı pikselini komşu piksellerin ağırlıklı toplamından hesaplar. Bu, threadlerin global bellek erişimini azaltmak için örtüşen görüntü bölgelerini yeniden kullandığı stencil hesaplamalarını ve paylaşımlı bellek döşemesini tanıtır.
- **Softmax Fonksiyonu**: Softmax, bir sayı vektörünü toplamı 1 olan olasılıklara dönüştürür ve genellikle sinir ağı çıktılarında kullanılır. Bunu GPU üzerinde verimli bir şekilde uygulamak, büyük vektörleri işlerken paralel indirgemeleri (reduction) ve sayısal kararlılık tekniklerini tanıtır.

**Üretim değerlendirmeleri:**
- **Hata işleme** - Sınır kontrolü ve cihaz yönetimi
- **PyTorch entegrasyonu** - Autograd desteğine sahip özel operatörler