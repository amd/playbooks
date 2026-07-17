<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

เขียน GPU kernel ตั้งแต่ต้น คอมไพล์ เปิดใช้งานบน AMD GPU และดูการใช้งานพุ่งสูงขึ้น Playbook นี้แสดงให้เห็นว่าการประมวลผล GPU ทำงานอย่างไรในความเป็นจริง: เขียนโค้ด kernel และรันแบบขนานบนหลายพันเธรดพร้อมกัน

> **หมายเหตุ**: นี่เป็น playbook ที่ค่อนข้างซับซ้อน ซึ่งอาจต้องการการดีบักและการปรับแต่งเพิ่มเติม

## สิ่งที่คุณจะได้เรียนรู้

<!-- @os:windows -->
- วิธีที่ GPU kernel ทำงาน: grids, blocks, threads และโมเดลการจัดทำดัชนีที่แมปไปยังข้อมูล
- วิธีที่ AMD ROCm/HIP stack ให้คุณเขียนโค้ดแบบ CUDA ที่รันบน AMD GPU ได้โดยไม่ต้องแก้ไข
- วิธีคอมไพล์ kernel ขณะรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้าง native C++ kernel extension ด้วย `CUDAExtension` + pybind11 ที่สามารถ import จาก Python ได้
<!-- @os:end -->
<!-- @os:linux -->
- วิธีที่ GPU kernel ทำงาน: grids, blocks, threads และโมเดลการจัดทำดัชนีที่แมปไปยังข้อมูล
- วิธีที่ AMD ROCm/HIP stack ให้คุณเขียนโค้ดแบบ CUDA ที่รันบน AMD GPU ได้โดยไม่ต้องแก้ไข
- วิธีคอมไพล์ kernel ขณะรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้าง native C++ kernel extension ด้วย `CUDAExtension` + pybind11 ที่สามารถ import จาก Python ได้
- วิธีวัดเวลาการรัน kernel และตรวจสอบการใช้งาน GPU แบบเรียลไทม์ด้วย `amd-smi`
<!-- @os:end -->

---

Playbook นี้ครอบคลุมสองแนวทางสำหรับการพัฒนา kernel:

<!-- @os:windows -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel` เขียน kernel เป็น Python string โดยไม่มีขั้นตอน build |
| **C++ Extension** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` เป็น native `.pyd` และ import ได้ |
<!-- @os:end -->
<!-- @os:linux -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **JIT Compilation** | `torch.cuda._compile_kernel` เขียน kernel เป็น Python string โดยไม่มีขั้นตอน build |
| **C++ Extension** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` เป็น native `.so` และ import ได้ |
<!-- @os:end -->

ทั้งสองแนวทางรันบน AMD GPU ได้ เป็นไปได้เพราะ ROCm build ของ PyTorch แมป CUDA API surface ทั้งหมดไปยัง HIP ซึ่งหมายความว่า `torch.cuda`, `CUDAExtension` และ syntax ของ CUDA kernel ทำงานบนฮาร์ดแวร์ AMD ได้อย่างโปร่งใส

---

## พื้นฐาน

### GPU Kernel คืออะไร?

GPU kernel คือฟังก์ชันที่รันแบบขนานบนเธรด GPU หลายพันเธรดพร้อมกัน ต่างจากฟังก์ชัน CPU ที่รันครั้งเดียวต่อการเรียก kernel จะถูกเปิดใช้งานด้วย **grid** ของ **blocks** โดยแต่ละ block มีหลาย **threads** ทั้งหมดรันโค้ดเดียวกันบนข้อมูลที่แตกต่างกัน

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### โมเดลการจัดทำดัชนีเธรด

เมื่อเปิดใช้งาน kernel คุณระบุสองมิติ:

| ตัวแปร | ความหมาย |
|---|---|
| `gridDim` | จำนวน blocks ใน grid |
| `blockDim` | จำนวนเธรดต่อ block |

แต่ละเธรดมีสิทธิ์เข้าถึงตัวแปร built-in แบบอ่านอย่างเดียวสามตัว:

| ตัวแปร | ความหมาย |
|---|---|
| `blockIdx.x` | block ที่เธรดนี้อยู่ |
| `blockDim.x` | จำนวนเธรดใน block หนึ่ง |
| `threadIdx.x` | ดัชนีเธรดภายใน block ของตัวเอง |

### Global Thread ID

ตัวแปรเหล่านี้ถูกรวมกันเพื่อคำนวณดัชนีเธรดที่ไม่ซ้ำกันทั่วโลก:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

จำนวนเธรดทั้งหมด = `gridDim.x * blockDim.x` แต่ละเธรดประมวลผลหนึ่งองค์ประกอบอย่างอิสระ นี่คือรากฐานของ **data parallelism** การดำเนินการเดียวกันรันบนหลายองค์ประกอบพร้อมกัน โดยไม่มีการพึ่งพาระหว่างเธรด

---

### โมเดลการรัน GPU: Wavefronts

AMD GPU รันเธรดเป็นกลุ่มละ **32** เรียกว่า **wavefronts** เธรดทั้งหมดใน wavefront รันคำสั่งเดียวกันพร้อมกัน สิ่งนี้ส่งผลต่อการเลือกขนาด block ที่เหมาะสม (256 เธรด = 8 wavefronts = ประสิทธิภาพการจัดตารางที่ดี)

### การเขียนโปรแกรม AMD GPU: HIP + ROCm

**ROCm** คือ open-source GPU compute stack ของ AMD (ไดรเวอร์, คอมไพเลอร์, ไลบรารี, runtime) **HIP** อยู่ด้านบน ออกแบบมาให้มี syntax เหมือนกับ CUDA ROCm build ของ PyTorch แมป `torch.cuda.*` ไปยัง HIP อย่างโปร่งใส ดังนั้นโค้ดเดียวกันจึงทำงานบน AMD GPU ได้

---

### PyTorch + AMD/HIP

PyTorch มาพร้อม ROCm build ที่ CUDA API surface (`torch.cuda.*`) ถูกสนับสนุนโดย HIP อย่างโปร่งใส ซึ่งหมายความว่า:

- `torch.cuda.is_available()` ทำงานบน AMD GPU ที่มี ROCm
- `tensor.to("cuda")` จัดสรรบน AMD GPU
- `torch.version.hip` แสดงเวอร์ชัน HIP

PyTorch ยังเปิดเผย `torch.cuda._compile_kernel()` ซึ่งเป็น shortcut ระดับสูงสำหรับ JIT-compile kernel string แบบ raw และได้รับ callable กลับมา โดยไม่ต้องมีขั้นตอน build แยกต่างหาก

---

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### ข้อกำหนดเบื้องต้น - Windows
- ติดตั้งเวอร์ชันล่าสุด: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### สร้าง Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv ที่ติดตั้ง ROCm+Pytorch ไว้แล้ว
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
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
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
บน Windows เปิด terminal ในไดเรกทอรีที่คุณต้องการและทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องแก้ไข PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนรันคำสั่ง Powershell บางคำสั่ง

<!-- @os:end -->
### การติดตั้ง Dependencies พื้นฐาน
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
> **หมายเหตุ:** สำหรับ playbook นี้ ROCm และ PyTorch จำเป็นต้องติดตั้งลงใน virtual environment แม้บน Ryzen AI Halo เนื่องจากการคอมไพล์ kernel แบบกำหนดเองต้องใช้ development headers แบบเต็มรูปแบบ

ติดตั้ง ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

ติดตั้ง PyTorch:
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

### การติดตั้ง Dependencies เพิ่มเติม

<!-- @os:linux -->
ติดตั้ง Linux C/C++ build toolchain นี่คือ dependency ระดับระบบและจำเป็นสำหรับการทำตาม C++ extension walkthroughs เนื่องจาก `CUDAExtension` สร้าง native `.so` modules จากไฟล์ `.cu`

รันคำสั่งนี้ครั้งเดียวบนเครื่อง Linux ภายนอก Python virtual environment ที่สร้างขึ้น:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

หลังจาก activate `kernel-env` virtual environment แล้ว ให้ติดตั้ง Python build dependencies:
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
โปรดตรวจสอบให้แน่ใจว่าได้ติดตั้ง [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) หรือ [เวอร์ชันใหม่กว่า](https://visualstudio.microsoft.com/vs/community/) พร้อมกับ workload **Desktop development with C++**

> **หมายเหตุ**: การตั้งค่า Visual Studio C++ environment นี้จำเป็นเฉพาะสำหรับแนวทาง **C++ Extension** เท่านั้น ไม่จำเป็นสำหรับแนวทาง JIT Compilation

เปิด PowerShell terminal และรันคำสั่งต่อไปนี้ก่อนสร้าง C++ extension

**ขั้นตอนที่ 1: ค้นหา Visual Studio C++ environment ที่ติดตั้งไว้**

**(A) ค้นหา `vswhere.exe` ซึ่งติดตั้งมาพร้อมกับ Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) ค้นหา `vcvars64.bat` จาก Visual Studio 2022 หรือเวอร์ชันใหม่กว่าที่มี C++ build tools**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) แสดง Visual Studio C++ Environment ที่กำลังใช้งาน**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**ขั้นตอนที่ 2: Activate Visual Studio C++ build environment**

**(A) รัน `vcvars64.bat` และจับ environment ที่มันตั้งค่าไว้**

ขั้นตอนนี้ทำให้ `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` และ Windows SDK paths พร้อมใช้งาน

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) นำเข้า Visual Studio environment variables เข้าสู่ PowerShell session นี้**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**ขั้นตอนที่ 3: ตรวจสอบว่า Microsoft C++ compiler พร้อมใช้งาน**

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

#### ตั้งค่า Environment Variables
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
ตรวจสอบว่า AMD GPU มองเห็นได้ด้วย:
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

## ดาวน์โหลดไฟล์ที่จำเป็น

สร้างโครงสร้างไดเรกทอรีต่อไปนี้โดยสร้าง **2 โฟลเดอร์ใหม่** และดาวน์โหลดไฟล์ที่เกี่ยวข้อง:

| ไดเรกทอรี | ไฟล์ที่ต้องดาวน์โหลด | คำอธิบาย |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ไฟล์ JIT และ C++ extension สำหรับ vector addition kernel |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ไฟล์ JIT และ C++ extension สำหรับ matrix multiplication kernel |


## Walkthroughs

### Walkthrough 1: Vector Addition

#### แนวทาง A: JIT Compilation

JIT (Just-In-Time) compilation หมายความว่า kernel ถูกเขียนเป็น raw C++ string ภายใน Python และคอมไพล์ขณะ runtime โดยไม่ต้องมีขั้นตอน build เพิ่มเติม

หากต้องการใช้ [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) ให้ตรวจสอบว่าดาวน์โหลดแล้วและรัน:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**ส่วนของโค้ดสำคัญ**
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
> **เคล็ดลับ**: สคริปต์ยังสร้าง background thread ที่ poll `amd-smi` ทุก 100ms เพื่อบันทึกการใช้งาน GPU สูงสุดและเฉลี่ยระหว่างการรัน kernel
<!-- @os:end -->

> **หมายเหตุ**: **ทำไมถึงใช้ Block Size 256?** <br>
> - kernel ใช้ **256 threads ต่อ block** เนื่องจากสอดคล้องกับ **wavefront execution model ของ AMD GPU**
> - โปรดทราบว่า AMD hardware รัน threads เป็นกลุ่มละ 32 threads ส่งผลให้มี 8 wavefronts ต่อ block (8 wavefronts x 32 threads = 1 block)


**สิ่งที่ workload ทำ:**

kernel เพิ่มงานพิเศษเทียมเพื่อแสดงการใช้งาน GPU:

- **100,000,000 elements** ใน tensor
- **Inner loop รัน 1,000 ครั้ง** ต่อ element ต่อการ launch kernel หนึ่งครั้ง
- **200 kernel launches** ทั้งหมด

**การคำนวณ:**  
- แต่ละ element: ถูกเพิ่มค่าทีละ 1 × 1,000 iterations × 200 launches = 200,000  
- ผลลัพธ์สุดท้าย: 1.0 (ค่าเริ่มต้น) + 200,000 (การบวก) = 200,001.0

**ทำไมถึงต้องมี inner loop?**  
- หากไม่มี `for (int i = 0; i < 1000; i++)` loop การ launch 200 ครั้งจะเสร็จสิ้นทันทีและเครื่องมือตรวจสอบจะไม่สามารถจับการใช้งาน GPU ที่มีความหมายได้ งานเทียมนี้ทำให้การรัน kernel แต่ละครั้งใช้เวลานานพอที่เครื่องมือตรวจสอบจะวัดประสิทธิภาพได้

<!-- @os:linux -->
**ผลลัพธ์ที่คาดหวัง:** [ตัวเลขประสิทธิภาพอาจแตกต่างกัน]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows ไม่รองรับ `amd-smi` หากต้องการติดตามการใช้งาน GPU สามารถใช้ Task Manager ซึ่งคุณควรเห็นการใช้งานพุ่งขึ้นชั่วคราวเมื่อรันโปรแกรม

**ผลลัพธ์ที่คาดหวัง:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**ยอดเยี่ยม! คุณเพิ่งรัน GPU kernel ตัวแรกของคุณแล้ว**

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
#### แนวทาง B: C++ Extension

แนวทางที่สองเป็นแบบ manual มากกว่า: เขียน kernel และ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์โดยตรงโดยใช้ระบบ build ของ PyTorch และ import เข้า Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension ต้องใช้สภาพแวดล้อม Visual Studio C++ build เนื่องจาก PyTorch คอมไพล์ไฟล์ `.cu` ให้เป็น native `.pyd` extension module การ build native extension นั้นขึ้นอยู่กับ Microsoft C++ toolchain (compiler, linker และ build tools) ที่ Visual Studio จัดเตรียมไว้ให้ รัน Visual Studio activation commands จากส่วน setup ก่อนที่จะ build extension
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding ทุกอย่างอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | Build script ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python script ที่รัน built artifacts |
<!-- @os:end -->

<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | Kernel + launcher + pybind11 binding ทุกอย่างอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | Build script ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | Python script ที่รัน built artifacts |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: kernel, launcher และ binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**เคล็ดลับ**: ทำไมต้องใช้ `hipDeviceSynchronize()`? <br>
> - การ launch GPU kernel เป็นแบบ asynchronous เมื่อ CPU รัน `add_one<<<grid_size, block_size>>>(data, n);` มันจะดำเนินการคำสั่งถัดไปทันทีโดยไม่รอ GPU `hipDeviceSynchronize()` บังคับให้ CPU รอจนกว่า GPU kernel จะทำงานเสร็จสมบูรณ์

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราสร้างขึ้น


`CUDAExtension` คือ CUDA build helper จาก `torch.utils.cpp_extension` เมื่อใช้กับ ROCm PyTorch จะ**remap `CUDAExtension` ให้ใช้ `hipcc`** แทน `nvcc` ROCm จะ intercept build path และส่งต่อผ่าน HIP compiler เพื่อ port โค้ด CUDA ไปยัง AMD

สิ่งนี้จะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `add_one_kernel.hip`: HIP source ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu` นี่คือสิ่งที่ `hipcc` คอมไพล์จริงๆ
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `add_one_kernel.hip`: HIP source ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu` นี่คือสิ่งที่ `hipcc` คอมไพล์จริงๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
รัน script นี้เพื่อดู kernel ในการทำงาน:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**ผลลัพธ์ที่คาดหวัง:**
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

### Walkthrough 2: การคูณเมทริกซ์

การคูณเมทริกซ์คำนวณ **C = A × B** โดยที่:
- **A** มีขนาด M×N (แถว × คอลัมน์)
- **B** มีขนาด N×K  
- **C** มีขนาด M×K (ผลลัพธ์)

แต่ละ element ของผลลัพธ์ถูกนิยามดังนี้:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

แต่ละ element ของ C ถูกคำนวณอย่างอิสระ ทำให้เหมาะสมอย่างยิ่งสำหรับการประมวลผลแบบขนานบน GPU

#### วิธีที่ Mapping ไปยัง GPU Threads

ต่างจาก vector addition (1D) การคูณเมทริกซ์ให้ผลลัพธ์เป็น **2D** ดังนั้นเราจึงใช้ **2D grid ของ threads**:

| | Vector Addition | Matrix Multiplication |
|---|---|---|
| **รูปร่างของผลลัพธ์** | อาร์เรย์ 1D | เมทริกซ์ 2D (M×K) |
| **การ mapping ของ thread** | 1 thread → 1 element | 1 thread → 1 output element |
| **รูปแบบการ launch** | 1D grid: `(grid_x, 1, 1)` | 2D grid: `(grid_x, grid_y, 1)` |
| **ขนาด block** | `(256, 1, 1)` | `(16, 16, 1)` = 256 threads |

แต่ละ thread คำนวณ element หนึ่งของเมทริกซ์ผลลัพธ์ C Thread ที่ตำแหน่ง `(row, col)` คำนวณ `C[row][col]` โดยการคูณแถวที่สอดคล้องกันของ A กับคอลัมน์ที่สอดคล้องกันของ B

**Memory Layout**: หน่วยความจำ GPU เป็นแบบ flat (1D) แต่เมทริกซ์ถูกเก็บทีละแถว ในการเข้าถึง `A[row][col]` kernel จะใช้ `A[row * N + col]`


#### แนวทาง A: JIT Compilation:

เช่นเดียวกับ Walkthrough 1 kernel ถูกเขียนเป็น raw C++ string ภายใน Python และคอมไพล์ขณะ runtime ผ่าน JIT ที่ built-in ของ PyTorch


หากต้องการใช้ [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) ตรวจสอบให้แน่ใจว่าดาวน์โหลดแล้วและรัน:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**ส่วนของโค้ดสำคัญ**
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

Script จะตรวจสอบผลลัพธ์เทียบกับ `torch.mm` ด้วย tolerance ขนาดเล็ก การคำนวณทางคณิตศาสตร์แบบ floating-point บน GPU อาจให้ผลต่างเชิงตัวเลขเล็กน้อยเมื่อเทียบกับการ implement บน CPU เนื่องจากลำดับการ reduction แบบขนาน

<!-- @os:linux -->
**ผลลัพธ์ที่คาดหวัง:** [ตัวเลขประสิทธิภาพจะแตกต่างกันไป]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows ไม่รองรับ `amd-smi` หากต้องการติดตามการใช้งาน GPU สามารถใช้ Task Manager ซึ่งคุณควรเห็นการใช้งานพุ่งขึ้นชั่วครู่เมื่อรันโปรแกรม

**ผลลัพธ์ที่คาดหวัง:**
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
#### แนวทาง B: C++ Extension

แนวทางที่สองเป็นแบบ manual มากกว่า: เขียน kernel และ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์โดยตรงโดยใช้ระบบ build ของ PyTorch แล้วนำเข้าใช้งานใน Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension จำเป็นต้องใช้สภาพแวดล้อม Visual Studio C++ build เนื่องจาก PyTorch คอมไพล์ไฟล์ต้นฉบับ `.cu` ให้เป็น native `.pyd` extension module การสร้าง native extension ดังกล่าวขึ้นอยู่กับ Microsoft C++ toolchain (compiler, linker และ build tools) ที่ Visual Studio จัดเตรียมไว้ให้ รันคำสั่ง Visual Studio activation จากส่วน setup ก่อนที่จะ build extension
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python script ที่รัน built artifacts |
<!-- @os:end -->
<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | Kernel + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | Build script ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | Python script ที่รัน built artifacts |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: kernel, launcher และ binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

เมื่อเปรียบเทียบกับ `add_one_launcher` ใน Walkthrough 1 launcher ในที่นี้:
- รับ input tensor สองตัวแทนที่จะเป็นหนึ่งตัว
- ดึงค่าทั้งสามมิติ (M, N, K) จาก tensor shapes โดยไม่ต้องส่งขนาดด้วยตนเองจาก Python
- จัดสรรและคืนค่า output tensor C แทนที่จะแก้ไขข้อมูลใน-place
- ใช้ `dim3` สำหรับทั้ง grid และ block เพื่อแสดง 2D launch shape

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราสร้างขึ้น


ซึ่งจะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `matmul_kernel.hip`: HIP source ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu` นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `matmul_kernel.hip`: HIP source ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu` นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
รัน script นี้เพื่อดู kernel ในการทำงาน:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**ยอดเยี่ยม! คุณเพิ่งนำ matrix multiplication ไปใช้งานบน GPU แล้ว** นี่เป็นก้าวสำคัญเพราะ matrix multiplication คือแกนหลักของการดำเนินการ machine learning สมัยใหม่ เช่น:
- Neural network layers
- Attention mechanisms
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

## ขั้นตอนถัดไป

คุณได้เรียนรู้วิธีเขียน คอมไพล์ และ launch GPU kernels โดยใช้ทั้ง JIT compilation และ C++ extensions สำหรับการดำเนินการแบบ parallel พื้นฐานแล้ว

**การปรับปรุงประสิทธิภาพ:**
- **Shared memory tiling** - แคชบล็อกข้อมูลเพื่อลดการเข้าถึง global memory
- **Memory coalescing** - ปรับรูปแบบการเข้าถึง memory ให้เหมาะสมเพื่อ bandwidth

**อัลกอริทึมในโลกจริง:**
- **2D Convolution** - filter ขนาดเล็ก (kernel) เลื่อนผ่านภาพ โดยคำนวณ output pixel แต่ละจุดจากผลรวมถ่วงน้ำหนักของ pixel ที่อยู่ใกล้เคียง ซึ่งแนะนำการคำนวณแบบ stencil และ shared memory tiling ที่ thread นำข้อมูลบริเวณภาพที่ทับซ้อนกันมาใช้ซ้ำเพื่อลดการเข้าถึง global memory
- **Softmax Function**: Softmax แปลงเวกเตอร์ของตัวเลขให้เป็นความน่าจะเป็นที่รวมกันได้ 1 ซึ่งใช้กันทั่วไปใน output ของ neural network การนำไปใช้งานอย่างมีประสิทธิภาพบน GPU แนะนำ parallel reductions และเทคนิคความเสถียรเชิงตัวเลขในขณะที่ประมวลผลเวกเตอร์ขนาดใหญ่

**ข้อพิจารณาสำหรับ production:**
- **Error handling** - การตรวจสอบขอบเขตและการจัดการ device
- **PyTorch integration** - Custom operators พร้อม autograd support