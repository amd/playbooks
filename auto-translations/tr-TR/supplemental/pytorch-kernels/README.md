<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın render edemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

## Genel Bakış

Sıfırdan bir GPU kernel'i yazın, derleyin, AMD GPU üzerinde başlatın ve kullanım oranının nasıl yükseldiğini izleyin. Bu playbook, GPU hesaplamasının gerçekte nasıl çalıştığını gösterir: kernel kodunu yazın ve binlerce iş parçacığı genelinde paralel olarak çalıştırın.

> **Not**: Bu oldukça karmaşık bir playbook'tur ve bazı ek hata ayıklama ile değişiklikler gerektirebilir.

## Neler Öğreneceksiniz

<!-- @os:windows -->
- GPU kernel'lerinin nasıl çalıştığı: grid'ler, bloklar, iş parçacıkları ve bunları veriye eşleyen indeksleme modeli
- AMD ROCm/HIP yığınının, CUDA tarzı kodunuzu değişiklik yapmadan AMD GPU'larda çalıştırmanıza nasıl olanak tanıdığı
- `torch.cuda._compile_kernel` kullanarak çalışma zamanında bir kernel'in nasıl derleneceği
- `CUDAExtension` + pybind11 ile Python'dan içe aktarılabilir yerel bir C++ kernel uzantısının nasıl oluşturulacağı
<!-- @os:end -->
<!-- @os:linux -->
- GPU kernel'lerinin nasıl çalıştığı: grid'ler, bloklar, iş parçacıkları ve bunları veriye eşleyen indeksleme modeli
- AMD ROCm/HIP yığınının, CUDA tarzı kodunuzu değişiklik yapmadan AMD GPU'larda çalıştırmanıza nasıl olanak tanıdığı
- `torch.cuda._compile_kernel` kullanarak çalışma zamanında bir kernel'in nasıl derleneceği
- `CUDAExtension` + pybind11 ile Python'dan içe aktarılabilir yerel bir C++ kernel uzantısının nasıl oluşturulacağı
- `amd-smi` ile kernel yürütme süresinin nasıl ölçüleceği ve canlı GPU kullanımının nasıl izleneceği
<!-- @os:end -->

---

Bu playbook, kernel geliştirme için iki yaklaşımı kapsar:

<!-- @os:windows -->
| Yaklaşım | Giriş noktası |
|---|---|
| **JIT Derleme** | `torch.cuda._compile_kernel`, bir kernel'i Python dizesi olarak yazın, derleme adımı gerekmez |
| **C++ Uzantısı** | `CUDAExtension` + pybind11: bir `.cu` dosyasını yerel bir `.pyd` olarak derleyin ve içe aktarın |
<!-- @os:end -->
<!-- @os:linux -->
| Yaklaşım | Giriş noktası |
|---|---|
| **JIT Derleme** | `torch.cuda._compile_kernel`, bir kernel'i Python dizesi olarak yazın, derleme adımı gerekmez |
| **C++ Uzantısı** | `CUDAExtension` + pybind11: bir `.cu` dosyasını yerel bir `.so` olarak derleyin ve içe aktarın |
<!-- @os:end -->

Her iki yaklaşım da AMD GPU'larda çalışır. Bu, PyTorch'un ROCm derlemesinin tüm CUDA API yüzeyini HIP'e eşlemesi sayesinde mümkündür. Bu, `torch.cuda`, `CUDAExtension` ve CUDA kernel sözdiziminin AMD donanımında şeffaf biçimde çalıştığı anlamına gelir.

---

## Arka Plan

### GPU Kernel'i Nedir?

GPU kernel'i, binlerce GPU iş parçacığında eş zamanlı olarak paralel çalışan bir fonksiyondur. Her çağrıda bir kez çalışan CPU fonksiyonunun aksine, bir kernel **blok** içeren bir **grid** ile başlatılır; her blok birçok **iş parçacığı** içerir ve tümü farklı veriler üzerinde aynı kodu çalıştırır.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### İş Parçacığı İndeksleme Modeli

Bir kernel başlatırken iki boyut belirtirsiniz:

| Değişken | Anlam |
|---|---|
| `gridDim` | Grid içindeki blok sayısı |
| `blockDim` | Blok başına iş parçacığı sayısı |

Her iş parçacığının üç yerleşik salt okunur değişkene erişimi vardır:

| Değişken | Anlam |
|---|---|
| `blockIdx.x` | Bu iş parçacığının ait olduğu blok |
| `blockDim.x` | Bir bloktaki iş parçacığı sayısı |
| `threadIdx.x` | Bloğu içindeki iş parçacığı indeksi |

### Küresel İş Parçacığı Kimliği

Bu değişkenler, küresel olarak benzersiz bir iş parçacığı indeksi hesaplamak için birleştirilir:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

Toplam iş parçacığı sayısı = `gridDim.x * blockDim.x`. Her iş parçacığı bir öğeyi bağımsız olarak işler. Bu, **veri paralelliğinin** temelidir. Aynı işlem, iş parçacıkları arası bağımlılık olmaksızın birçok öğe üzerinde aynı anda çalışır.

---

### GPU Yürütme Modeli: Wavefront'lar

AMD GPU'lar, iş parçacıklarını **wavefront** adı verilen **32**'lik gruplar halinde çalıştırır. Bir wavefront içindeki tüm iş parçacıkları aynı talimatı eş zamanlı olarak çalıştırır. Bu durum, optimal blok boyutu seçimlerini etkiler (256 iş parçacığı = 8 wavefront = iyi zamanlama verimliliği).

### AMD GPU Programlama: HIP + ROCm

**ROCm**, AMD'nin açık kaynaklı GPU hesaplama yığınıdır (sürücüler, derleyiciler, kütüphaneler, çalışma zamanı). **HIP** bunun üzerinde yer alır ve sözdizimsel olarak CUDA ile özdeş olacak şekilde tasarlanmıştır. PyTorch'un ROCm derlemesi, `torch.cuda.*` fonksiyonlarını şeffaf biçimde HIP'e eşler; böylece aynı kod AMD GPU'larda da çalışır.

---

### PyTorch + AMD/HIP

PyTorch, CUDA API yüzeyinin (`torch.cuda.*`) şeffaf biçimde HIP tarafından desteklendiği bir ROCm derlemesiyle birlikte gelir. Bu şu anlama gelir:

- `torch.cuda.is_available()`, ROCm ile AMD GPU'larda çalışır
- `tensor.to("cuda")`, AMD GPU üzerinde bellek ayırır
- `torch.version.hip`, HIP sürümünü gösterir

PyTorch ayrıca `torch.cuda._compile_kernel()` fonksiyonunu sunar; bu, ayrı bir derleme adımına gerek kalmadan ham bir kernel dizesini JIT derleyip çağrılabilir bir nesne döndüren üst düzey bir kısayoldur.

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
Linux'ta, tercih ettiğiniz dizinde bir terminal açın ve ROCm+PyTorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin.
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
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun geçerli olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux'ta, tercih ettiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
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
Windows'ta, tercih ettiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **İpucu**: Windows kullanıcılarının bazı PowerShell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmeleri gerekebilir (örneğin,
> RemoteSigned veya Unrestricted olarak ayarlama).

<!-- @os:end -->
### Temel Bağımlılıkları Yükleme
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
> **Not:** Bu kılavuz için, özel çekirdek derlemesi tam geliştirme başlıklarını gerektirdiğinden, ROCm ve PyTorch'un Ryzen AI Halo üzerinde bile sanal ortama yüklenmesi gerekmektedir.

ROCm'u yükleyin:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

PyTorch'u yükleyin:
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

### Ek Bağımlılıkları Yükleme

<!-- @os:linux -->
Linux C/C++ derleme araç zincirini yükleyin. Bu, sistem düzeyinde bir bağımlılıktır ve C++ uzantısı adım adım anlatımları için gereklidir; çünkü `CUDAExtension`, `.cu` dosyalarından yerel `.so` modülleri derler.

Bunu Linux makinesinde, oluşturulan Python sanal ortamının dışında bir kez çalıştırın:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

`kernel-env` sanal ortamını etkinleştirdikten sonra Python derleme bağımlılıklarını yükleyin:
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
**Desktop development with C++** iş yüküyle birlikte [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) veya [daha yeni bir sürümünün](https://visualstudio.microsoft.com/vs/community/) yüklü olduğundan emin olun.

> **Not**: Bu Visual Studio C++ ortam kurulumu yalnızca **C++ Uzantısı** yaklaşımı için gereklidir. JIT Derleme yaklaşımı için gerekli değildir.

Bir PowerShell terminali açın ve C++ uzantısını derlemeden önce aşağıdaki komutları çalıştırın.

**Adım 1: Yüklü Visual Studio C++ ortamını bulun**

**(A) Visual Studio Yükleyicisi ile birlikte yüklenen `vswhere.exe`'yi bulun**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) C++ derleme araçlarıyla Visual Studio 2022 veya daha yenisinden `vcvars64.bat`'ı bulun**

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

**Adım 2: Visual Studio C++ derleme ortamını etkinleştirin**

**(A) `vcvars64.bat`'ı çalıştırın ve ayarladığı ortamı yakalayın**

Bu işlem, `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` ve Windows SDK yollarını kullanılabilir hale getirir.

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
AMD GPU'nun görünür olduğunu şu komutla doğrulayın:
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

**2 yeni klasör** oluşturarak ve ilgili dosyaları indirerek aşağıdaki dizin yapısını oluşturun:

| Dizin | İndirilecek Dosyalar | Açıklama |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| Vektör toplama çekirdeği için JIT ve C++ uzantısı dosyaları |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Matris çarpımı çekirdeği için JIT ve C++ uzantısı dosyaları |


## Adım Adım Anlatımlar

### Adım Adım Anlatım 1: Vektör Toplama

#### Yaklaşım A: JIT Derleme

JIT (Tam Zamanında) derleme, çekirdeğin Python içinde ham bir C++ dizesi olarak yazıldığı ve ek derleme adımlarına gerek kalmadan çalışma zamanında derlendiği anlamına gelir.

[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) dosyasını kullanmak için, dosyanın indirildiğinden emin olun ve çalıştırın:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**Temel Kod Parçacıkları**
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
> **İpucu**: Betik ayrıca, çekirdek çalışması sırasında tepe ve ortalama GPU kullanımını kaydetmek için her 100ms'de bir `amd-smi`'yi sorgulayan bir arka plan iş parçacığı başlatır.
<!-- @os:end -->

> **Not**: **Blok Boyutu Neden 256?** <br>
> - Çekirdek, **AMD GPU'ların dalgacık yürütme modeliyle** iyi uyum sağladığı için **blok başına 256 iş parçacığı** kullanır.
> - AMD donanımının iş parçacıklarını 32'lik gruplar halinde yürüttüğünü, bunun da blok başına 8 dalgacıkla sonuçlandığını hatırlayın. (8 dalgacık x 32 iş parçacığı = 1 blok)


**İş yükünün yaptığı işlem:**

Çekirdek, GPU kullanımını göstermek için yapay olarak fazladan iş ekler:

- Tensörde **100.000.000 eleman**
- **İç döngü, her çekirdek başlatımında** eleman başına **1.000 kez** çalışır
- Toplam **200 çekirdek başlatımı**

**Matematik:**  
- Her eleman: 1 × 1.000 yineleme × 200 başlatım = 200.000 artırılır  
- Nihai sonuç: 1,0 (başlangıç değeri) + 200.000 (toplama) = 200.001,0

**İç döngü neden var?**  
- `for (int i = 0; i < 1000; i++)` döngüsü olmadan, 200 başlatım anında tamamlanır ve izleme araçları anlamlı GPU kullanımını yakalayamaz. Yapay iş, her çekirdek çalışmasının izleme araçlarının performansı ölçebilmesi için yeterince uzun sürmesini sağlar.

<!-- @os:linux -->
**Beklenen çıktı:** [Performans rakamları değişiklik gösterecektir]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Windows'ta `amd-smi` desteklenmemektedir. GPU kullanımını izlemek için Görev Yöneticisi'ni kullanabilirsiniz; programı çalıştırdığınızda kısa süreli bir kullanım artışı görmelisiniz.

**Beklenen çıktı:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**Harika iş! İlk GPU çekirdeğinizi çalıştırdınız.**

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

İkinci yaklaşım daha manueldir: kernel ve Python bağlamasını tek bir `.cu` dosyasına yazın, PyTorch'un derleme sistemi kullanarak yerel olarak derleyin ve Python'a aktarın.

<!-- @os:windows -->
> **Not**: C++ Uzantısı yaklaşımı, PyTorch `.cu` kaynak dosyasını yerel bir `.pyd` uzantı modülüne derlediğinden Visual Studio C++ derleme ortamını gerektirir. Bu yerel uzantının derlenmesi, Visual Studio tarafından sağlanan Microsoft C++ araç zincirine (derleyici, bağlayıcı ve derleme araçları) bağlıdır. Uzantıyı derlemeden önce kurulum bölümündeki Visual Studio etkinleştirme komutlarını çalıştırın.
<!-- @os:end -->

Henüz indirmediyseniz aşağıdaki dosyaları indirin:
<!-- @os:windows -->
| Dosya | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması, her şey tek dosyada |
| [setup.py](assets/Vector_Addition/setup.py) | Derleme betiği, `.cu` dosyasını `.pyd` olarak derlemek için `CUDAExtension` kullanır |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Derlenen yapıtları çalıştıran Python betiği |
<!-- @os:end -->

<!-- @os:linux -->
| Dosya | Rol |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması, her şey tek dosyada |
| [setup.py](assets/Vector_Addition/setup.py) | Derleme betiği, `.cu` dosyasını `.so` olarak derlemek için `CUDAExtension` kullanır |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Derlenen yapıtları çalıştıran Python betiği |
<!-- @os:end -->

#### **Adım 1: Kernel, başlatıcı ve bağlama** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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
> - GPU kernel başlatmaları asenkrondur. CPU `add_one<<<grid_size, block_size>>>(data, n);` komutunu çalıştırdığında, GPU'nun bitmesini beklemeden hemen bir sonraki talimatı yürütür. `hipDeviceSynchronize()`, CPU'yu GPU kernel tamamlanana kadar beklemeye zorlar.

#### **Adım 2: Derleme**
```bash
pip install --no-build-isolation -v .
```
>**Not**: Bu komut, oluşturduğumuz .cu dosyasını derlemek için geçerli dizinde `setup.py` arar.


`CUDAExtension`, `torch.utils.cpp_extension` içindeki bir CUDA derleme yardımcısıdır. ROCm ile PyTorch, **`CUDAExtension`'ı `nvcc` yerine `hipcc` kullanacak şekilde yeniden eşler**. ROCm derleme yolunu keser ve HIP derleyicisi üzerinden yönlendirerek CUDA kodunu AMD'ye taşır.

Bu işlem aşağıdaki dosyaları üretir:
<!-- @os:windows -->
- `build/`: `.pyd` dosyalarını içeren dizin
- `add_one_kernel.hip`: `.cu` dosyası hipify edilerek oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği dosya budur
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` dosyalarını içeren dizin
- `add_one_kernel.hip`: `.cu` dosyası hipify edilerek oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği dosya budur
<!-- @os:end -->

#### **Adım 3: Python'dan kullanım** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
Kernel'i çalışırken görmek için bu betiği çalıştırın:
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

### İzlenecek Yol 2: Matris Çarpımı

Matris çarpımı **C = A × B** hesaplar; burada:
- **A**, M×N boyutundadır (satır × sütun)
- **B**, N×K boyutundadır
- **C**, M×K boyutundadır (sonuç)

Her çıktı elemanı şu şekilde tanımlanır:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

C'nin her elemanı bağımsız olarak hesaplanır; bu da GPU paralelliği için mükemmel bir yapı oluşturur.

#### GPU İş Parçacıklarına Nasıl Eşlenir

Vektör toplamadan (1D) farklı olarak, matris çarpımı **2D bir çıktı** üretir; bu nedenle **2D bir iş parçacığı ızgarası** kullanırız:

| | Vektör Toplama | Matris Çarpımı |
|---|---|---|
| **Çıktı şekli** | 1D dizi | 2D matris (M×K) |
| **İş parçacığı eşlemesi** | 1 iş parçacığı → 1 eleman | 1 iş parçacığı → 1 çıktı elemanı |
| **Başlatma düzeni** | 1D ızgara: `(grid_x, 1, 1)` | 2D ızgara: `(grid_x, grid_y, 1)` |
| **Blok boyutu** | `(256, 1, 1)` | `(16, 16, 1)` = 256 iş parçacığı |

Her iş parçacığı, çıktı matrisinin C'nin bir elemanını hesaplar. `(row, col)` konumundaki iş parçacığı, A'nın ilgili satırını B'nin ilgili sütunuyla çarparak `C[row][col]`'u hesaplar.

**Bellek Düzeni**: GPU belleği düzdür (1D), ancak matrisler satır satır depolanır. `A[row][col]`'a erişmek için kernel `A[row * N + col]` ifadesini kullanır.


#### Yaklaşım A: JIT Derlemesi:

İzlenecek Yol 1'de olduğu gibi, kernel Python içinde ham bir C++ dizesi olarak yazılır ve PyTorch'un yerleşik JIT'i aracılığıyla çalışma zamanında derlenir.


[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) dosyasını kullanmak için indirildiğinden emin olun ve çalıştırın:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**Temel Kod Parçacıkları**
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

Betik, sonucu küçük bir toleransla `torch.mm` ile doğrular. GPU'larda kayan nokta aritmetiği, paralel indirgeme sırası nedeniyle CPU uygulamalarına kıyasla küçük sayısal farklılıklar üretebilir.

<!-- @os:linux -->
**Beklenen çıktı:** [Performans rakamları değişiklik gösterecektir]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: Windows'ta `amd-smi` desteklenmez. GPU kullanımını izlemek için Görev Yöneticisi'ni kullanabilirsiniz; programı çalıştırdığınızda kısa süreli bir kullanım artışı görmelisiniz.

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

İkinci yaklaşım daha manueldir: kernel ve Python bağlamasını tek bir `.cu` dosyasına yazın, PyTorch'un derleme sistemi kullanarak yerel olarak derleyin ve Python'a aktarın.

<!-- @os:windows -->
> **Not**: C++ Uzantısı yaklaşımı, PyTorch `.cu` kaynak dosyasını yerel bir `.pyd` uzantı modülüne derlediğinden Visual Studio C++ derleme ortamını gerektirir. Bu yerel uzantının derlenmesi, Visual Studio tarafından sağlanan Microsoft C++ araç zincirine (derleyici, bağlayıcı ve derleme araçları) bağlıdır. Uzantıyı derlemeden önce kurulum bölümündeki Visual Studio etkinleştirme komutlarını çalıştırın.
<!-- @os:end -->

Henüz indirmediyseniz aşağıdaki dosyaları indirin:
<!-- @os:windows -->
| Dosya | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Derleme betiği, `.cu` dosyasını `.pyd` dosyasına derlemek için `CUDAExtension` kullanır |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Derlenen yapıtları çalıştıran Python betiği |
<!-- @os:end -->
<!-- @os:linux -->
| Dosya | Rol |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + başlatıcı + pybind11 bağlaması |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Derleme betiği, `.cu` dosyasını `.so` dosyasına derlemek için `CUDAExtension` kullanır |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Derlenen yapıtları çalıştıran Python betiği |
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

1. İzlenecek Yol'daki `add_one_launcher` ile karşılaştırıldığında, buradaki başlatıcı:
- Bir yerine iki giriş tensörü alır
- Üç boyutun tamamını (M, N, K) tensör şekillerinden türetir; Python'dan manuel boyut aktarımı gerekmez
- Yerinde değiştirme yapmak yerine C çıkış tensörünü tahsis eder ve döndürür
- 2B başlatma şeklini ifade etmek için hem ızgara hem de blok için `dim3` kullanır

#### **Adım 2: Derleme**
```bash
pip install --no-build-isolation -v .
```
> **Not**: Bu komut, oluşturduğumuz .cu dosyasını derlemek için geçerli dizinde `setup.py` dosyasını arar.


Bu işlem aşağıdaki dosyaları üretir:
<!-- @os:windows -->
- `build/`: `.pyd` dosyalarını içeren dizin
- `matmul_kernel.hip`: `.cu` dosyası hipify edilerek oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği dosya budur
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: `.so` dosyalarını içeren dizin
- `matmul_kernel.hip`: `.cu` dosyası hipify edilerek oluşturulan HIP kaynağı; `hipcc`'nin gerçekte derlediği dosya budur
<!-- @os:end -->

#### **Adım 3: Python'dan kullanım** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
Kerneli çalışırken görmek için bu betiği çalıştırın:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**Beklenen çıktı:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**Harika! GPU üzerinde matris çarpımını başarıyla uyguladınız.** Bu önemli bir kilometre taşıdır; çünkü matris çarpımı, aşağıdaki gibi modern makine öğrenmesi işlemlerinin temelini oluşturur:
- Sinir ağı katmanları
- Dikkat mekanizmaları
- Gömme vektörleri
- Transformatörler

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

Temel paralel işlemler için hem JIT derlemesi hem de C++ uzantıları kullanarak GPU kernellerini yazmayı, derlemeyi ve başlatmayı öğrendiniz.

**Performans optimizasyonları:**
- **Paylaşımlı bellek döşemesi** - Global bellek erişimini azaltmak için veri bloklarını önbelleğe alın
- **Bellek birleştirme** - Bant genişliği için bellek erişim düzenlerini optimize edin

**Gerçek dünya algoritmaları:**
- **2B Evrişim** - Küçük bir filtre (kernel), her çıkış pikselini komşu piksellerin ağırlıklı toplamından hesaplayarak bir görüntü üzerinde kayar. Bu, şablon hesaplamalarını ve paylaşımlı bellek döşemesini tanıtır; burada iş parçacıkları global bellek erişimini azaltmak için örtüşen görüntü bölgelerini yeniden kullanır.
- **Softmax Fonksiyonu**: Softmax, bir sayı vektörünü toplamı 1 olan olasılıklara dönüştürür ve sinir ağı çıktılarında yaygın olarak kullanılır. GPU üzerinde verimli biçimde uygulamak, büyük vektörleri işlerken paralel indirgeme ve sayısal kararlılık tekniklerini gündeme getirir.

**Üretim ortamı değerlendirmeleri:**
- **Hata yönetimi** - Sınır denetimi ve cihaz yönetimi
- **PyTorch entegrasyonu** - Autograd desteğiyle özel operatörler