<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## ภาพรวม

เขียนเคอร์เนล GPU ตั้งแต่ต้น คอมไพล์มัน รันมันบน GPU ของ AMD และดูอัตราการใช้งานพุ่งขึ้น เพลย์บุ๊กนี้แสดงให้เห็นว่าการประมวลผลด้วย GPU ทำงานอย่างไรจริง ๆ นั่นคือการเขียนโค้ดเคอร์เนล แล้วรันมันแบบขนานผ่านเธรดนับพัน

> **หมายเหตุ**: นี่เป็นเพลย์บุ๊กที่ค่อนข้างซับซ้อน ซึ่งอาจต้องใช้การดีบักและการปรับแก้เพิ่มเติมบ้าง

## สิ่งที่คุณจะได้เรียนรู้

<!-- @os:windows -->
- การทำงานของเคอร์เนล GPU: กริด บล็อก เธรด และโมเดลการทำดัชนีที่แม็ปสิ่งเหล่านี้เข้ากับข้อมูล
- วิธีที่สแตก AMD ROCm/HIP ช่วยให้คุณเขียนโค้ดสไตล์ CUDA ที่รันบน GPU ของ AMD ได้โดยไม่ต้องแก้ไข
- วิธีคอมไพล์เคอร์เนลระหว่างรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้างส่วนขยายเคอร์เนล C++ แบบเนทีฟด้วย `CUDAExtension` + pybind11 ที่สามารถอิมพอร์ตจาก Python ได้
<!-- @os:end -->
<!-- @os:linux -->
- การทำงานของเคอร์เนล GPU: กริด บล็อก เธรด และโมเดลการทำดัชนีที่แม็ปสิ่งเหล่านี้เข้ากับข้อมูล
- วิธีที่สแตก AMD ROCm/HIP ช่วยให้คุณเขียนโค้ดสไตล์ CUDA ที่รันบน GPU ของ AMD ได้โดยไม่ต้องแก้ไข
- วิธีคอมไพล์เคอร์เนลระหว่างรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้างส่วนขยายเคอร์เนล C++ แบบเนทีฟด้วย `CUDAExtension` + pybind11 ที่สามารถอิมพอร์ตจาก Python ได้
- วิธีวัดเวลาการทำงานของเคอร์เนลและมอนิเตอร์อัตราการใช้งาน GPU แบบเรียลไทม์ด้วย `amd-smi`
<!-- @os:end -->

---

เพลย์บุ๊กนี้ครอบคลุมสองแนวทางในการพัฒนาเคอร์เนล:

<!-- @os:windows -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **การคอมไพล์แบบ JIT** | `torch.cuda._compile_kernel` เขียนเคอร์เนลเป็นสตริง Python โดยไม่ต้องมีขั้นตอนการ build |
| **ส่วนขยาย C++** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` เป็น `.pyd` แบบเนทีฟและอิมพอร์ตมันเข้ามา |
<!-- @os:end -->
<!-- @os:linux -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **การคอมไพล์แบบ JIT** | `torch.cuda._compile_kernel` เขียนเคอร์เนลเป็นสตริง Python โดยไม่ต้องมีขั้นตอนการ build |
| **ส่วนขยาย C++** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` เป็น `.so` แบบเนทีฟและอิมพอร์ตมันเข้ามา |
<!-- @os:end -->

ทั้งสองแนวทางรันบน GPU ของ AMD ได้ ซึ่งเป็นไปได้เพราะบิลด์ ROCm ของ PyTorch แม็ป CUDA API ทั้งหมดไปยัง HIP นั่นหมายความว่า `torch.cuda`, `CUDAExtension` และไวยากรณ์เคอร์เนล CUDA ทั้งหมดทำงานบนฮาร์ดแวร์ AMD ได้อย่างโปร่งใส

---

## ภูมิหลัง

### เคอร์เนล GPU คืออะไร?

เคอร์เนล GPU คือฟังก์ชันที่รันแบบขนานผ่านเธรด GPU นับพันพร้อมกัน ต่างจากฟังก์ชัน CPU ที่รันครั้งเดียวต่อการเรียกใช้หนึ่งครั้ง เคอร์เนลจะถูกเรียกใช้พร้อมกับ **กริด (grid)** ของ **บล็อก (block)** โดยแต่ละบล็อกมี **เธรด (thread)** จำนวนมาก ซึ่งทั้งหมดรันโค้ดเดียวกันบนข้อมูลที่แตกต่างกัน

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### โมเดลการทำดัชนีของเธรด

เมื่อเรียกใช้เคอร์เนล คุณต้องระบุมิติสองมิติ:

| ตัวแปร | ความหมาย |
|---|---|
| `gridDim` | จำนวนบล็อกในกริด |
| `blockDim` | จำนวนเธรดต่อบล็อก |

แต่ละเธรดสามารถเข้าถึงตัวแปรในตัวแบบอ่านอย่างเดียวสามตัว:

| ตัวแปร | ความหมาย |
|---|---|
| `blockIdx.x` | เธรดนี้เป็นของบล็อกใด |
| `blockDim.x` | จำนวนเธรดในหนึ่งบล็อก |
| `threadIdx.x` | ดัชนีเธรดภายในบล็อกของมัน |

### รหัสเธรดแบบ Global

ตัวแปรเหล่านี้ถูกรวมกันเพื่อคำนวณดัชนีเธรดที่ไม่ซ้ำกันในระดับ global:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

เธรดทั้งหมด = `gridDim.x * blockDim.x` แต่ละเธรดประมวลผลข้อมูลหนึ่งชิ้นอย่างอิสระ นี่คือรากฐานของ **data parallelism** การดำเนินการเดียวกันจะรันบนข้อมูลหลายชิ้นพร้อมกัน โดยไม่มีการพึ่งพากันระหว่างเธรด

---

### โมเดลการทำงานของ GPU: Wavefronts

GPU ของ AMD ประมวลผลเธรดเป็นกลุ่มละ **32** เธรด เรียกว่า **wavefronts** เธรดทั้งหมดใน wavefront รันคำสั่งเดียวกันพร้อมกัน สิ่งนี้ส่งผลต่อการเลือกขนาดบล็อกที่เหมาะสม (256 เธรด = 8 wavefronts = ประสิทธิภาพการจัดตารางที่ดี)

### การเขียนโปรแกรม GPU ของ AMD: HIP + ROCm

**ROCm** คือสแตกการประมวลผลด้วย GPU แบบโอเพนซอร์สของ AMD (ไดรเวอร์ คอมไพเลอร์ ไลบรารี รันไทม์) **HIP** ทำงานอยู่บนชั้นบนสุด ถูกออกแบบมาให้มีไวยากรณ์เหมือนกับ CUDA ทุกประการ บิลด์ ROCm ของ PyTorch แม็ป `torch.cuda.*` ไปยัง HIP อย่างโปร่งใส ดังนั้นโค้ดเดียวกันจึงทำงานบน GPU ของ AMD ได้

---

### PyTorch + AMD/HIP

PyTorch มีบิลด์ ROCm ที่ CUDA API (`torch.cuda.*`) ถูกรองรับโดย HIP อย่างโปร่งใส ซึ่งหมายความว่า:

- `torch.cuda.is_available()` ทำงานบน GPU ของ AMD ที่ใช้ ROCm
- `tensor.to("cuda")` จัดสรรหน่วยความจำบน GPU ของ AMD
- `torch.version.hip` แสดงเวอร์ชันของ HIP

PyTorch ยังมี `torch.cuda._compile_kernel()` ซึ่งเป็นทางลัดระดับสูงสำหรับคอมไพล์สตริงเคอร์เนลดิบแบบ JIT แล้วได้ callable กลับมา โดยไม่ต้องมีขั้นตอนการ build แยกต่างหาก

---

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### สิ่งที่ต้องมีก่อน - Windows
- ติดตั้งเวอร์ชันล่าสุด: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv ที่มี ROCm+Pytorch ติดตั้งไว้แล้ว
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
**ให้สิทธิ์ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและกลับเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
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
บน Windows ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องปรับ Execution Policy ของ PowerShell (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนที่จะรันคำสั่ง PowerShell บางคำสั่ง

<!-- @os:end -->


### การติดตั้งการพึ่งพาพื้นฐาน (Basic Dependencies)
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
> **หมายเหตุ:** สำหรับเพลย์บุ๊กนี้ จำเป็นต้องติดตั้ง ROCm และ PyTorch ลงในสภาพแวดล้อมเสมือนแม้กระทั่งบน Ryzen AI Halo เนื่องจากการคอมไพล์เคอร์เนลแบบกำหนดเองต้องใช้เฮดเดอร์การพัฒนาแบบเต็มรูปแบบ

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
### การติดตั้งการพึ่งพาเพิ่มเติม

<!-- @os:linux -->
ติดตั้ง Linux C/C++ build toolchain การพึ่งพานี้เป็นการพึ่งพาระดับระบบและจำเป็นสำหรับบทแนะนำการใช้งาน C++ extension เนื่องจาก `CUDAExtension` จะสร้างโมดูล `.so` แบบเนทีฟจากไฟล์ `.cu`

รันคำสั่งนี้เพียงครั้งเดียวบนเครื่อง Linux โดยอยู่นอก Python virtual environment ที่สร้างขึ้น:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

หลังจากเปิดใช้งาน virtual environment `kernel-env` แล้ว ให้ติดตั้งการพึ่งพาสำหรับการ build ของ Python:
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
โปรดตรวจสอบให้แน่ใจว่าได้ติดตั้ง [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) หรือ[เวอร์ชันที่ใหม่กว่า](https://visualstudio.microsoft.com/vs/community/) พร้อมกับ workload **Desktop development with C++**

> **หมายเหตุ**: การตั้งค่าสภาพแวดล้อม Visual Studio C++ นี้จำเป็นเฉพาะสำหรับแนวทาง **C++ Extension** เท่านั้น ไม่จำเป็นสำหรับแนวทาง JIT Compilation

เปิด PowerShell terminal และรันคำสั่งต่อไปนี้ก่อนทำการ build C++ extension

**ขั้นตอนที่ 1: ค้นหาสภาพแวดล้อม Visual Studio C++ ที่ติดตั้งไว้**

**(A) ค้นหา `vswhere.exe` ซึ่งติดตั้งมาพร้อมกับ Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) ค้นหา `vcvars64.bat` จาก Visual Studio 2022 หรือใหม่กว่าที่มี C++ build tools**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) แสดงสภาพแวดล้อม Visual Studio C++ ที่กำลังใช้งาน**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**ขั้นตอนที่ 2: เปิดใช้งานสภาพแวดล้อมการ build ของ Visual Studio C++**

**(A) รัน `vcvars64.bat` และบันทึกสภาพแวดล้อมที่ถูกตั้งค่า**

ซึ่งจะทำให้ `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` และเส้นทาง Windows SDK พร้อมใช้งาน

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) นำเข้าตัวแปรสภาพแวดล้อมของ Visual Studio เข้าสู่เซสชัน PowerShell นี้**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**ขั้นตอนที่ 3: ตรวจสอบว่าคอมไพเลอร์ Microsoft C++ พร้อมใช้งาน**

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

#### ตั้งค่าตัวแปรสภาพแวดล้อม
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
ตรวจสอบว่า AMD GPU สามารถมองเห็นได้ด้วย:
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

สร้างโครงสร้างไดเรกทอรีต่อไปนี้โดยการสร้าง **โฟลเดอร์ใหม่ 2 โฟลเดอร์** และดาวน์โหลดไฟล์ที่เกี่ยวข้อง:

| ไดเรกทอรี | ไฟล์ที่ต้องดาวน์โหลด | คำอธิบาย |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ไฟล์ JIT และ C++ extension สำหรับ kernel การบวกเวกเตอร์ |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ไฟล์ JIT และ C++ extension สำหรับ kernel การคูณเมทริกซ์ |


## บทแนะนำที่ 1: การบวกเวกเตอร์

#### แนวทาง A: JIT Compilation

JIT (Just-In-Time) compilation หมายถึงการที่ kernel ถูกเขียนเป็น raw C++ string ภายใน Python และถูกคอมไพล์ในขณะรัน โดยไม่จำเป็นต้องมีขั้นตอนการ build เพิ่มเติม

หากต้องการใช้ [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) ตรวจสอบให้แน่ใจว่าได้ดาวน์โหลดไฟล์แล้วและรัน:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**ตัวอย่างโค้ดสำคัญ**
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
> **เคล็ดลับ**: สคริปต์นี้ยังสร้าง background thread ที่ตรวจสอบ `amd-smi` ทุก 100ms เพื่อบันทึกการใช้งาน GPU สูงสุดและค่าเฉลี่ยระหว่างการรัน kernel
<!-- @os:end -->

> **หมายเหตุ**: **เหตุใด Block Size จึงเป็น 256?** <br>
> - kernel ใช้ **256 threads ต่อ block** เนื่องจากสอดคล้องกับ **โมเดลการทำงานแบบ wavefront ของ AMD GPU** ได้เป็นอย่างดี
> - โปรดจำไว้ว่าฮาร์ดแวร์ของ AMD ประมวลผล threads เป็นกลุ่มละ 32 threads ส่งผลให้มี 8 wavefronts ต่อ block (8 wavefronts x 32 threads = 1 block)


**สิ่งที่ workload ทำ:**

kernel นี้เพิ่มงานเสริมขึ้นมาโดยเจตนาเพื่อแสดงให้เห็นการใช้งาน GPU:

- **100,000,000 elements** ใน tensor
- **inner loop ทำงาน 1,000 ครั้ง** ต่อ element ในแต่ละครั้งที่ kernel ถูกเรียกใช้งาน
- **การเรียกใช้งาน kernel ทั้งหมด 200 ครั้ง**

**การคำนวณ:**  
- แต่ละ element: ถูกเพิ่มค่าทีละ 1 คูณด้วย 1,000 รอบ คูณด้วย 200 ครั้งของการเรียกใช้งาน = 200,000  
- ผลลัพธ์สุดท้าย: 1.0 (ค่าเริ่มต้น) + 200,000 (การบวก) = 200,001.0

**เหตุใดจึงต้องมี inner loop?**  
- หากไม่มี loop `for (int i = 0; i < 1000; i++)` การเรียกใช้งาน 200 ครั้งจะเสร็จสิ้นในทันที และเครื่องมือตรวจสอบจะไม่สามารถจับข้อมูลการใช้งาน GPU ที่มีความหมายได้ งานเสริมนี้ทำให้แต่ละการรัน kernel ใช้เวลานานพอที่เครื่องมือตรวจสอบจะสามารถวัดประสิทธิภาพได้

<!-- @os:linux -->
**ผลลัพธ์ที่คาดว่าจะได้รับ:**[ตัวเลขประสิทธิภาพอาจแตกต่างกันไป]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows, `amd-smi` ไม่รองรับ ในการติดตามการใช้งาน GPU คุณสามารถใช้ Task Manager ซึ่งคุณควรจะเห็นการใช้งานพุ่งขึ้นในช่วงสั้นๆ เมื่อคุณรันโปรแกรม

**ผลลัพธ์ที่คาดว่าจะได้รับ:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**เยี่ยมมาก! คุณเพิ่งรัน GPU kernel ตัวแรกของคุณสำเร็จแล้ว**

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
#### แนวทางที่ B: C++ Extension

แนวทางที่สองต้องใช้แรงมากกว่า คือการเขียนเคอร์เนลและ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์แบบเนทีฟโดยใช้ระบบ build ของ PyTorch แล้วนำเข้ามาใช้งานใน Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension ต้องใช้สภาพแวดล้อม build ของ Visual Studio C++ เนื่องจาก PyTorch จะคอมไพล์ไฟล์ต้นฉบับ `.cu` เป็นโมดูลส่วนขยายเนทีฟ `.pyd` การ build ส่วนขยายเนทีฟนั้นขึ้นอยู่กับชุดเครื่องมือ Microsoft C++ (คอมไพเลอร์ ลิงเกอร์ และ build tools) ที่มาพร้อมกับ Visual Studio รันคำสั่งเปิดใช้งาน Visual Studio จากส่วนการตั้งค่าก่อนที่จะ build ส่วนขยายนี้
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากคุณยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | เคอร์เนล + ตัวเรียกใช้งาน + pybind11 binding ทุกอย่างอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | สคริปต์สำหรับ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | สคริปต์ Python ที่รันไฟล์ผลลัพธ์ที่ build แล้ว |
<!-- @os:end -->

<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | เคอร์เนล + ตัวเรียกใช้งาน + pybind11 binding ทุกอย่างอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | สคริปต์สำหรับ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | สคริปต์ Python ที่รันไฟล์ผลลัพธ์ที่ build แล้ว |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: เคอร์เนล ตัวเรียกใช้งาน และ binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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
> - การเรียกใช้เคอร์เนลของ GPU เป็นแบบอะซิงโครนัส เมื่อ CPU รัน `add_one<<<grid_size, block_size>>>(data, n);` มันจะรันคำสั่งถัดไปทันทีโดยไม่รอ GPU `hipDeviceSynchronize()` จะบังคับให้ CPU รอจนกว่าเคอร์เนลของ GPU จะทำงานเสร็จสิ้น

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราสร้างขึ้น


`CUDAExtension` เป็นตัวช่วย build CUDA จาก `torch.utils.cpp_extension` เมื่อใช้ ROCm PyTorch จะ **แมป `CUDAExtension` ใหม่ให้ใช้ `hipcc`** แทน `nvcc` ROCm จะสกัดกั้นเส้นทางการ build และส่งผ่านตัวคอมไพเลอร์ HIP เพื่อพอร์ตโค้ด CUDA ไปยัง AMD

การดำเนินการนี้จะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `add_one_kernel.hip`: ซอร์ส HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `add_one_kernel.hip`: ซอร์ส HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
รันสคริปต์นี้เพื่อดูเคอร์เนลทำงานจริง:
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

## แนวทางที่ 2: การคูณเมทริกซ์

การคูณเมทริกซ์คำนวณ **C = A × B** โดยที่:
- **A** มีขนาด M×N (แถว × คอลัมน์)
- **B** มีขนาด N×K  
- **C** มีขนาด M×K (ผลลัพธ์)

แต่ละองค์ประกอบของผลลัพธ์ถูกกำหนดเป็น:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

แต่ละองค์ประกอบของ C ถูกคำนวณอย่างอิสระจากกัน ทำให้เหมาะสมอย่างยิ่งสำหรับการประมวลผลแบบขนานบน GPU

#### สิ่งนี้แมปเข้ากับเธรดของ GPU อย่างไร

ต่างจากการบวกเวกเตอร์ (1D) การคูณเมทริกซ์ให้ **ผลลัพธ์แบบ 2D** ดังนั้นเราจึงใช้ **กริดเธรดแบบ 2D**:

| | การบวกเวกเตอร์ | การคูณเมทริกซ์ |
|---|---|---|
| **รูปร่างผลลัพธ์** | อาร์เรย์ 1D | เมทริกซ์ 2D (M×K) |
| **การแมปเธรด** | 1 เธรด → 1 องค์ประกอบ | 1 เธรด → 1 องค์ประกอบผลลัพธ์ |
| **รูปแบบการเรียกใช้งาน** | กริด 1D: `(grid_x, 1, 1)` | กริด 2D: `(grid_x, grid_y, 1)` |
| **ขนาดบล็อก** | `(256, 1, 1)` | `(16, 16, 1)` = 256 เธรด |

แต่ละเธรดคำนวณหนึ่งองค์ประกอบของเมทริกซ์ผลลัพธ์ C เธรดที่ตำแหน่ง `(row, col)` จะคำนวณ `C[row][col]` โดยการคูณแถวที่สอดคล้องกันของ A กับคอลัมน์ที่สอดคล้องกันของ B

**การจัดวางในหน่วยความจำ**: หน่วยความจำของ GPU เป็นแบบแบน (1D) แต่เมทริกซ์ถูกจัดเก็บทีละแถว เพื่อเข้าถึง `A[row][col]` เคอร์เนลจะใช้ `A[row * N + col]`


#### แนวทางที่ A: การคอมไพล์แบบ JIT:

เช่นเดียวกับตัวอย่างที่ 1 เคอร์เนลถูกเขียนเป็น C++ string ดิบภายใน Python และคอมไพล์ขณะรันไทม์ผ่าน JIT ในตัวของ PyTorch


หากต้องการใช้ [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) ตรวจสอบให้แน่ใจว่าดาวน์โหลดแล้ว จากนั้นรัน:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**ตัวอย่างโค้ดสำคัญ**
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

สคริปต์จะตรวจสอบผลลัพธ์เทียบกับ `torch.mm` โดยมีค่าความคลาดเคลื่อนเล็กน้อย เลขคณิตแบบจุดทศนิยมบน GPU อาจให้ผลลัพธ์ที่แตกต่างเล็กน้อยจากการคำนวณเชิงตัวเลขเมื่อเทียบกับการทำงานบน CPU เนื่องจากลำดับการลดรูป (reduction) แบบขนาน

<!-- @os:linux -->
**ผลลัพธ์ที่คาดหวัง:**[ตัวเลขประสิทธิภาพจะแตกต่างกันไป]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows `amd-smi` ไม่รองรับ หากต้องการติดตามการใช้งาน GPU คุณสามารถใช้ Task Manager ซึ่งคุณควรเห็นการพุ่งขึ้นของการใช้งานในช่วงสั้น ๆ เมื่อคุณรันโปรแกรม

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

แนวทางที่สองต้องทำด้วยตนเองมากขึ้น คือการเขียนเคอร์เนลและ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์ด้วยระบบ build ของ PyTorch โดยตรง แล้วนำเข้าสู่ Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension ต้องใช้สภาพแวดล้อมการ build ของ Visual Studio C++ เนื่องจาก PyTorch จะคอมไพล์ไฟล์ต้นฉบับ `.cu` ให้เป็นโมดูล native `.pyd` extension การ build extension แบบ native นี้ขึ้นอยู่กับชุดเครื่องมือ Microsoft C++ (คอมไพเลอร์, ลิงก์เกอร์ และเครื่องมือ build) ที่มาจาก Visual Studio รันคำสั่งเปิดใช้งาน Visual Studio จากส่วนการตั้งค่าก่อนทำการ build extension
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากคุณยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | เคอร์เนล + ตัวเรียกใช้งาน + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | สคริปต์ build ใช้ `CUDAExtension` ในการคอมไพล์ไฟล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | สคริปต์ Python ที่รันไฟล์ที่ build แล้ว |
<!-- @os:end -->
<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | เคอร์เนล + ตัวเรียกใช้งาน + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | สคริปต์ build ใช้ `CUDAExtension` ในการคอมไพล์ไฟล์ `.cu` ให้เป็น `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | สคริปต์ Python ที่รันไฟล์ที่ build แล้ว |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: เคอร์เนล ตัวเรียกใช้งาน และ binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

เมื่อเทียบกับ `add_one_launcher` ใน Walkthrough 1 ตัวเรียกใช้งานที่นี่:
- รับ tensor อินพุตสองตัวแทนที่จะเป็นหนึ่งตัว
- ดึงมิติทั้งสาม (M, N, K) มาจากรูปร่างของ tensor โดยไม่ต้องส่งขนาดด้วยตนเองจาก Python
- จัดสรรและคืนค่า output tensor C แทนที่จะแก้ไขแบบ in-place
- ใช้ `dim3` สำหรับทั้ง grid และ block เพื่อแสดงรูปแบบการ launch แบบ 2D

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราสร้างขึ้น


การดำเนินการนี้จะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `matmul_kernel.hip`: ซอร์สโค้ด HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `matmul_kernel.hip`: ซอร์สโค้ด HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
รันสคริปต์นี้เพื่อดูเคอร์เนลทำงานจริง:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**ยอดเยี่ยม! คุณเพิ่งใช้งานการคูณเมทริกซ์บน GPU สำเร็จแล้ว** นี่ถือเป็นก้าวสำคัญ เพราะการคูณเมทริกซ์เป็นแกนหลักของการดำเนินการ machine learning สมัยใหม่ เช่น:
- เลเยอร์ของ neural network
- กลไก attention
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

คุณได้เรียนรู้การเขียน คอมไพล์ และเรียกใช้งานเคอร์เนล GPU โดยใช้ทั้งการคอมไพล์แบบ JIT และ C++ extension สำหรับการดำเนินการแบบขนานพื้นฐาน

**การปรับปรุงประสิทธิภาพ:**
- **Shared memory tiling** - แคชบล็อกข้อมูลเพื่อลดการเข้าถึง global memory
- **Memory coalescing** - ปรับรูปแบบการเข้าถึงหน่วยความจำให้เหมาะสมกับแบนด์วิดท์

**อัลกอริทึมที่ใช้งานจริง:**
- **2D Convolution** - ฟิลเตอร์ขนาดเล็ก (เคอร์เนล) เลื่อนผ่านภาพ โดยคำนวณพิกเซลผลลัพธ์แต่ละพิกเซลจากผลรวมถ่วงน้ำหนักของพิกเซลข้างเคียง สิ่งนี้แนะนำการคำนวณแบบ stencil และ shared memory tiling ซึ่งเธรดต่าง ๆ จะนำพื้นที่ภาพที่ซ้อนทับกันมาใช้ซ้ำเพื่อลดการเข้าถึง global memory
- **Softmax Function**: Softmax แปลงเวกเตอร์ของตัวเลขให้กลายเป็นความน่าจะเป็นที่รวมกันได้ 1 ซึ่งมักใช้ในผลลัพธ์ของ neural network การนำไปใช้อย่างมีประสิทธิภาพบน GPU จะแนะนำการลดค่าแบบขนาน (parallel reductions) และเทคนิคความเสถียรเชิงตัวเลข ในขณะที่ประมวลผลเวกเตอร์ขนาดใหญ่

**ข้อพิจารณาสำหรับการใช้งานจริง:**
- **การจัดการข้อผิดพลาด** - การตรวจสอบขอบเขตและการจัดการอุปกรณ์
- **การผสานรวมกับ PyTorch** - Custom operators ที่รองรับ autograd