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

เขียนเคอร์เนล GPU ตั้งแต่ต้น คอมไพล์ ประมวลผลบน AMD GPU และดูค่าการใช้งานพุ่งสูงขึ้น เพลย์บุ๊กนี้แสดงให้เห็นว่าการประมวลผลบน GPU ทำงานอย่างไรจริง ๆ นั่นคือ เขียนโค้ดเคอร์เนล แล้วประมวลผลแบบขนานผ่านเธรดนับพัน

> **หมายเหตุ**: นี่เป็นเพลย์บุ๊กที่ค่อนข้างซับซ้อน ซึ่งอาจต้องมีการดีบักและปรับแก้เพิ่มเติมบ้าง

## สิ่งที่คุณจะได้เรียนรู้

<!-- @os:windows -->
- เคอร์เนล GPU ทำงานอย่างไร: กริด บล็อก เธรด และรูปแบบการจัดทำดัชนีที่เชื่อมโยงสิ่งเหล่านี้เข้ากับข้อมูล
- สแตก AMD ROCm/HIP ช่วยให้คุณเขียนโค้ดสไตล์ CUDA ที่รันบน AMD GPU ได้โดยไม่ต้องแก้ไขอย่างไร
- วิธีคอมไพล์เคอร์เนลขณะรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้างส่วนขยายเคอร์เนล C++ แบบเนทีฟด้วย `CUDAExtension` + pybind11 ที่สามารถนำเข้าใช้จาก Python ได้
<!-- @os:end -->
<!-- @os:linux -->
- เคอร์เนล GPU ทำงานอย่างไร: กริด บล็อก เธรด และรูปแบบการจัดทำดัชนีที่เชื่อมโยงสิ่งเหล่านี้เข้ากับข้อมูล
- สแตก AMD ROCm/HIP ช่วยให้คุณเขียนโค้ดสไตล์ CUDA ที่รันบน AMD GPU ได้โดยไม่ต้องแก้ไขอย่างไร
- วิธีคอมไพล์เคอร์เนลขณะรันไทม์โดยใช้ `torch.cuda._compile_kernel`
- วิธีสร้างส่วนขยายเคอร์เนล C++ แบบเนทีฟด้วย `CUDAExtension` + pybind11 ที่สามารถนำเข้าใช้จาก Python ได้
- วิธีวัดเวลาการประมวลผลเคอร์เนลและตรวจสอบการใช้งาน GPU แบบเรียลไทม์ด้วย `amd-smi`
<!-- @os:end -->

---

เพลย์บุ๊กนี้ครอบคลุมสองแนวทางสำหรับการพัฒนาเคอร์เนล:

<!-- @os:windows -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **การคอมไพล์แบบ JIT** | `torch.cuda._compile_kernel` เขียนเคอร์เนลเป็นสตริง Python โดยไม่ต้องมีขั้นตอนการ build |
| **ส่วนขยาย C++** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` ให้เป็น `.pyd` แบบเนทีฟและนำเข้าใช้งาน |
<!-- @os:end -->
<!-- @os:linux -->
| แนวทาง | จุดเริ่มต้น |
|---|---|
| **การคอมไพล์แบบ JIT** | `torch.cuda._compile_kernel` เขียนเคอร์เนลเป็นสตริง Python โดยไม่ต้องมีขั้นตอนการ build |
| **ส่วนขยาย C++** | `CUDAExtension` + pybind11: คอมไพล์ไฟล์ `.cu` ให้เป็น `.so` แบบเนทีฟและนำเข้าใช้งาน |
<!-- @os:end -->

ทั้งสองแนวทางสามารถรันบน AMD GPU ได้ เพราะ PyTorch เวอร์ชัน ROCm มีการแมปพื้นผิว API ของ CUDA ทั้งหมดไปยัง HIP ซึ่งหมายความว่า `torch.cuda`, `CUDAExtension` และไวยากรณ์เคอร์เนล CUDA ทั้งหมดทำงานได้บนฮาร์ดแวร์ AMD อย่างโปร่งใส

---

## พื้นฐาน

### เคอร์เนล GPU คืออะไร?

เคอร์เนล GPU คือฟังก์ชันที่ทำงานแบบขนานบนเธรด GPU นับพันพร้อมกัน ต่างจากฟังก์ชันบน CPU ที่ทำงานเพียงครั้งเดียวต่อการเรียก เคอร์เนลจะถูกเรียกใช้งานพร้อมกับ **กริด (grid)** ของ **บล็อก (block)** โดยแต่ละบล็อกมี **เธรด (thread)** จำนวนมาก ซึ่งทั้งหมดจะประมวลผลโค้ดเดียวกันแต่กับข้อมูลที่ต่างกัน

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### รูปแบบการจัดทำดัชนีเธรด

เมื่อเรียกใช้งานเคอร์เนล คุณจะต้องระบุมิติสองมิติ:

| ตัวแปร | ความหมาย |
|---|---|
| `gridDim` | จำนวนบล็อกในกริด |
| `blockDim` | จำนวนเธรดต่อบล็อก |

แต่ละเธรดสามารถเข้าถึงตัวแปรที่มีอยู่ในตัวและอ่านได้อย่างเดียวสามตัว:

| ตัวแปร | ความหมาย |
|---|---|
| `blockIdx.x` | เธรดนี้เป็นของบล็อกใด |
| `blockDim.x` | จำนวนเธรดในหนึ่งบล็อก |
| `threadIdx.x` | ดัชนีเธรดภายในบล็อกของมัน |

### รหัสเธรดสากล (Global Thread ID)

ตัวแปรเหล่านี้จะถูกนำมารวมกันเพื่อคำนวณดัชนีเธรดที่ไม่ซ้ำกันในระดับสากล:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

จำนวนเธรดทั้งหมด = `gridDim.x * blockDim.x` แต่ละเธรดประมวลผลข้อมูลหนึ่งชิ้นอย่างอิสระ นี่คือรากฐานของ **การประมวลผลแบบขนานข้อมูล (data parallelism)** ซึ่งการดำเนินการเดียวกันจะทำงานกับข้อมูลจำนวนมากพร้อมกัน โดยไม่มีการพึ่งพาระหว่างเธรด

---

### รูปแบบการประมวลผลของ GPU: Wavefront

AMD GPU ประมวลผลเธรดเป็นกลุ่มละ **32** เธรด เรียกว่า **wavefront** เธรดทั้งหมดใน wavefront จะรันคำสั่งเดียวกันพร้อมกัน สิ่งนี้ส่งผลต่อการเลือกขนาดบล็อกที่เหมาะสม (256 เธรด = 8 wavefront = ประสิทธิภาพการจัดตารางที่ดี)

### การเขียนโปรแกรม AMD GPU: HIP + ROCm

**ROCm** คือสแตกการประมวลผลบน GPU แบบโอเพนซอร์สของ AMD (ไดรเวอร์ คอมไพเลอร์ ไลบรารี รันไทม์) **HIP** ทำงานอยู่บนชั้นบนสุด ออกแบบมาให้มีไวยากรณ์เหมือนกับ CUDA ทุกประการ PyTorch เวอร์ชัน ROCm จะแมป `torch.cuda.*` ไปยัง HIP อย่างโปร่งใส ทำให้โค้ดเดียวกันสามารถทำงานบน AMD GPU ได้

---

### PyTorch + AMD/HIP

PyTorch มีเวอร์ชัน ROCm ที่พื้นผิว API ของ CUDA (`torch.cuda.*`) ถูกรองรับด้วย HIP อย่างโปร่งใส ซึ่งหมายความว่า:

- `torch.cuda.is_available()` ทำงานได้บน AMD GPU ที่มี ROCm
- `tensor.to("cuda")` จัดสรรหน่วยความจำบน AMD GPU
- `torch.version.hip` แสดงเวอร์ชันของ HIP

PyTorch ยังมี `torch.cuda._compile_kernel()` ซึ่งเป็นทางลัดระดับสูงสำหรับคอมไพล์สตริงเคอร์เนลดิบแบบ JIT และได้ตัวเรียกใช้งาน (callable) กลับมา โดยไม่ต้องมีขั้นตอนการ build แยกต่างหาก

---

<!-- @device:halo_box -->
## ตรวจสอบการอัปเดตซอฟต์แวร์

<!-- @require:software-update -->
<!-- @device:end -->

## การติดตั้งซอฟต์แวร์ที่จำเป็น
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### ข้อกำหนดเบื้องต้น - Windows
- ติดตั้งเวอร์ชันล่าสุดของ: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### สร้างสภาพแวดล้อมเสมือน (Virtual Environment)

<!-- @os:linux -->
<!-- @device:halo_box -->
บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv ที่มี ROCm+Pytorch ติดตั้งไว้แล้ว
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
**อนุญาตให้ผู้ใช้ของคุณเข้าถึงอุปกรณ์ GPU** (ออกจากระบบและเข้าสู่ระบบใหม่เพื่อให้มีผล):

```bash
sudo usermod -aG render,video $LOGNAME
```

บน Linux ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
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
บน Windows ให้เปิดเทอร์มินัลในไดเรกทอรีที่คุณเลือก แล้วทำตามคำสั่งเพื่อสร้าง venv
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **เคล็ดลับ**: ผู้ใช้ Windows อาจต้องปรับเปลี่ยน PowerShell Execution Policy (เช่น
> ตั้งค่าเป็น RemoteSigned หรือ Unrestricted) ก่อนที่จะรันคำสั่ง Powershell บางคำสั่ง

<!-- @os:end -->
### การติดตั้งข้อกำหนดเบื้องต้นพื้นฐาน
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
> **หมายเหตุ:** สำหรับ playbook นี้ จำเป็นต้องติดตั้ง ROCm และ PyTorch ลงใน virtual environment แม้จะอยู่บน Ryzen AI Halo ก็ตาม เนื่องจากการคอมไพล์ custom kernel จำเป็นต้องใช้ development headers แบบเต็มรูปแบบ

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

### การติดตั้งข้อกำหนดเพิ่มเติม

<!-- @os:linux -->
ติดตั้ง Linux C/C++ build toolchain ซึ่งเป็นข้อกำหนดระดับระบบและจำเป็นสำหรับ walkthrough ของ C++ extension เนื่องจาก `CUDAExtension` จะสร้างโมดูล `.so` แบบ native จากไฟล์ `.cu`

รันคำสั่งนี้เพียงครั้งเดียวบนเครื่อง Linux โดยอยู่นอก Python virtual environment ที่สร้างไว้:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

หลังจากเปิดใช้งาน virtual environment `kernel-env` แล้ว ให้ติดตั้งข้อกำหนดในการ build ของ Python:
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

**(A) รัน `vcvars64.bat` และเก็บค่าสภาพแวดล้อมที่ตั้งไว้**

ขั้นตอนนี้จะทำให้ `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH` และเส้นทาง Windows SDK พร้อมใช้งาน

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

สร้างโครงสร้างไดเรกทอรีต่อไปนี้โดยสร้าง **โฟลเดอร์ใหม่ 2 โฟลเดอร์** และดาวน์โหลดไฟล์ที่เกี่ยวข้อง:

| ไดเรกทอรี | ไฟล์ที่ต้องดาวน์โหลด | คำอธิบาย |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ไฟล์ JIT และ C++ extension สำหรับ kernel การบวกเวกเตอร์ |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ไฟล์ JIT และ C++ extension สำหรับ kernel การคูณเมทริกซ์ |


## Walkthrough

### Walkthrough 1: การบวกเวกเตอร์ (Vector Addition)

#### แนวทาง A: JIT Compilation

JIT (Just-In-Time) compilation หมายถึงการที่ kernel ถูกเขียนเป็น C++ string ดิบภายใน Python และคอมไพล์ในขณะรัน โดยไม่จำเป็นต้องมีขั้นตอนการ build เพิ่มเติม

ในการใช้ [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py) ให้แน่ใจว่าได้ดาวน์โหลดไฟล์แล้ว จากนั้นรัน:
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
> **เคล็ดลับ**: สคริปต์นี้ยังสร้างเธรดเบื้องหลังที่ทำการ poll `amd-smi` ทุก 100ms เพื่อบันทึกค่าการใช้งาน GPU สูงสุดและค่าเฉลี่ยระหว่างการรัน kernel
<!-- @os:end -->

> **หมายเหตุ**: **ทำไม Block Size ถึงเป็น 256?** <br>
> - kernel นี้ใช้ **256 เธรดต่อบล็อก** เนื่องจากสอดคล้องกับ **โมเดลการทำงานแบบ wavefront ของ AMD GPU** ได้เป็นอย่างดี
> - โปรดจำไว้ว่าฮาร์ดแวร์ของ AMD จะรันเธรดเป็นกลุ่มกลุ่มละ 32 เธรด ส่งผลให้มี 8 wavefronts ต่อบล็อก (8 wavefronts x 32 เธรด = 1 บล็อก)


**สิ่งที่ workload นี้ทำ:**

kernel นี้เพิ่มงานเทียมเข้าไปเพื่อสาธิตการใช้งาน GPU:

- **100,000,000 elements** ในเทนเซอร์
- **inner loop รันซ้ำ 1,000 ครั้ง** ต่อ element ในแต่ละครั้งที่รัน kernel  
- **รัน kernel ทั้งหมด 200 ครั้ง**

**การคำนวณ:**  
- แต่ละ element: ถูกเพิ่มค่าครั้งละ 1 × 1,000 รอบ × 200 ครั้งที่รัน = 200,000  
- ผลลัพธ์สุดท้าย: 1.0 (ค่าเริ่มต้น) + 200,000 (การบวก) = 200,001.0

**ทำไมต้องมี inner loop?**  
- หากไม่มี loop `for (int i = 0; i < 1000; i++)` การรัน 200 ครั้งจะเสร็จสิ้นในทันที และเครื่องมือตรวจสอบจะไม่สามารถจับข้อมูลการใช้งาน GPU ที่มีความหมายได้ งานเทียมนี้ทำให้แต่ละการรัน kernel ใช้เวลานานพอที่เครื่องมือตรวจสอบจะวัดประสิทธิภาพได้

<!-- @os:linux -->
**ผลลัพธ์ที่คาดหวัง:**[ตัวเลขประสิทธิภาพจะแตกต่างกันไป]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows ไม่รองรับ `amd-smi` หากต้องการติดตามการใช้งาน GPU คุณสามารถใช้ Task Manager ซึ่งคุณควรเห็นการใช้งานพุ่งขึ้นชั่วขณะเมื่อรันโปรแกรม

**ผลลัพธ์ที่คาดหวัง:**
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

แนวทางที่สองต้องทำด้วยตนเองมากกว่า โดยเขียนเคอร์เนลและ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์แบบเนทีฟโดยใช้ระบบ build ของ PyTorch แล้วนำเข้าสู่ Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension ต้องใช้สภาพแวดล้อม build ของ Visual Studio C++ เนื่องจาก PyTorch จะคอมไพล์ไฟล์ต้นฉบับ `.cu` ให้เป็นโมดูล extension แบบเนทีฟ `.pyd` การ build extension แบบเนทีฟนี้ต้องอาศัยชุดเครื่องมือ Microsoft C++ (คอมไพเลอร์ ลิงเกอร์ และเครื่องมือ build) ที่มาพร้อมกับ Visual Studio ให้รันคำสั่งเปิดใช้งาน Visual Studio จากส่วนการตั้งค่าก่อนที่จะ build extension
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | เคอร์เนล + ตัวเรียกใช้ + pybind11 binding รวมอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | สคริปต์สำหรับ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | สคริปต์ Python ที่รันสิ่งที่ build เสร็จแล้ว |
<!-- @os:end -->

<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | เคอร์เนล + ตัวเรียกใช้ + pybind11 binding รวมอยู่ในไฟล์เดียว |
| [setup.py](assets/Vector_Addition/setup.py) | สคริปต์สำหรับ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | สคริปต์ Python ที่รันสิ่งที่ build เสร็จแล้ว |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: เคอร์เนล ตัวเรียกใช้ และ binding** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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
> - การเรียกใช้เคอร์เนลบน GPU เป็นแบบ asynchronous เมื่อ CPU รัน `add_one<<<grid_size, block_size>>>(data, n);` มันจะดำเนินการคำสั่งถัดไปทันทีโดยไม่รอให้ GPU ทำงานเสร็จ `hipDeviceSynchronize()` จะบังคับให้ CPU รอจนกว่าเคอร์เนลบน GPU จะทำงานเสร็จสมบูรณ์

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราสร้างขึ้น


`CUDAExtension` เป็นตัวช่วย build CUDA จาก `torch.utils.cpp_extension` เมื่อใช้ ROCm PyTorch จะ **remap `CUDAExtension` ให้ใช้ `hipcc`** แทน `nvcc` ROCm จะสกัดกั้นเส้นทางการ build และส่งผ่านไปยังคอมไพเลอร์ HIP เพื่อพอร์ตโค้ด CUDA ไปยัง AMD

ขั้นตอนนี้จะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `add_one_kernel.hip`: ซอร์ส HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `add_one_kernel.hip`: ซอร์ส HIP ที่สร้างขึ้นจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
รันสคริปต์นี้เพื่อดูเคอร์เนลทำงาน:
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
- **A** คือ M×N (แถว × คอลัมน์)
- **B** คือ N×K  
- **C** คือ M×K (ผลลัพธ์)

แต่ละสมาชิกในผลลัพธ์ถูกกำหนดเป็น:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

สมาชิกแต่ละตัวของ C ถูกคำนวณอย่างอิสระจากกัน ทำให้เหมาะอย่างยิ่งสำหรับการประมวลผลแบบขนานบน GPU

#### วิธีการแม็ปไปยัง GPU Thread

ต่างจากการบวกเวกเตอร์ (1D) การคูณเมทริกซ์ให้ผลลัพธ์เป็น **2D output** ดังนั้นเราจึงใช้ **grid ของ thread แบบ 2D**:

| | การบวกเวกเตอร์ | การคูณเมทริกซ์ |
|---|---|---|
| **รูปแบบผลลัพธ์** | อาร์เรย์ 1D | เมทริกซ์ 2D (M×K) |
| **การแม็ป thread** | 1 thread → 1 สมาชิก | 1 thread → 1 สมาชิกในผลลัพธ์ |
| **รูปแบบการ launch** | grid 1D: `(grid_x, 1, 1)` | grid 2D: `(grid_x, grid_y, 1)` |
| **ขนาด block** | `(256, 1, 1)` | `(16, 16, 1)` = 256 thread |

แต่ละ thread คำนวณสมาชิกหนึ่งตัวของเมทริกซ์ผลลัพธ์ C thread ที่ตำแหน่ง `(row, col)` จะคำนวณ `C[row][col]` โดยการคูณแถวที่สอดคล้องกันของ A กับคอลัมน์ที่สอดคล้องกันของ B

**การจัดวางหน่วยความจำ**: หน่วยความจำ GPU เป็นแบบแฟลต (1D) แต่เมทริกซ์ถูกเก็บทีละแถว การเข้าถึง `A[row][col]` เคอร์เนลจะใช้ `A[row * N + col]`


#### แนวทางที่ A: การคอมไพล์แบบ JIT:

เช่นเดียวกับ Walkthrough 1 เคอร์เนลถูกเขียนเป็นสตริง C++ ดิบภายใน Python และคอมไพล์ขณะรันไทม์ผ่าน JIT ในตัวของ PyTorch


ในการใช้ [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py) ตรวจสอบให้แน่ใจว่าดาวน์โหลดแล้ว จากนั้นรัน:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**ตัวอย่างโค้ดที่สำคัญ**
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

สคริปต์นี้จะตรวจสอบผลลัพธ์เทียบกับ `torch.mm` โดยยอมให้มีความคลาดเคลื่อนเล็กน้อย เลขคณิตแบบทศนิยม (floating-point) บน GPU อาจให้ผลลัพธ์ที่แตกต่างเล็กน้อยเมื่อเทียบกับการทำงานบน CPU เนื่องจากลำดับการลดค่า (reduction) แบบขนาน

<!-- @os:linux -->
**ผลลัพธ์ที่คาดหวัง:**[ตัวเลขประสิทธิภาพอาจแตกต่างกันไป]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **หมายเหตุ**: บน Windows ไม่รองรับ `amd-smi` หากต้องการติดตามการใช้งาน GPU คุณสามารถใช้ Task Manager ซึ่งคุณควรจะเห็นการใช้งานพุ่งขึ้นในช่วงสั้น ๆ เมื่อรันโปรแกรม

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
#### แนวทางที่ B: C++ Extension

แนวทางที่สองเป็นแบบแมนวลมากกว่า คือเขียนเคอร์เนลและ Python binding ลงในไฟล์ `.cu` ไฟล์เดียว คอมไพล์แบบเนทีฟโดยใช้ระบบ build ของ PyTorch แล้วนำเข้าสู่ Python

<!-- @os:windows -->
> **หมายเหตุ**: แนวทาง C++ Extension ต้องใช้สภาพแวดล้อม build ของ Visual Studio C++ เนื่องจาก PyTorch จะคอมไพล์ไฟล์ต้นฉบับ `.cu` ให้เป็นโมดูล extension แบบเนทีฟ `.pyd` การ build extension แบบเนทีฟนี้ต้องอาศัย Microsoft C++ toolchain (compiler, linker และ build tools) ที่มาพร้อมกับ Visual Studio ให้รันคำสั่งเปิดใช้งาน Visual Studio จากส่วนการตั้งค่าก่อนที่จะทำการ build extension
<!-- @os:end -->

ดาวน์โหลดไฟล์ต่อไปนี้หากคุณยังไม่ได้ดาวน์โหลด:
<!-- @os:windows -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | เคอร์เนล + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | สคริปต์ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | สคริปต์ Python ที่รัน artifacts ที่ build แล้ว |
<!-- @os:end -->
<!-- @os:linux -->
| ไฟล์ | บทบาท |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | เคอร์เนล + launcher + pybind11 binding |
| [setup.py](assets/Matrix_Multiplication/setup.py) | สคริปต์ build ใช้ `CUDAExtension` เพื่อคอมไพล์ `.cu` ให้เป็น `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | สคริปต์ Python ที่รัน artifacts ที่ build แล้ว |
<!-- @os:end -->

#### **ขั้นตอนที่ 1: เคอร์เนล, launcher และ binding** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

เมื่อเทียบกับ `add_one_launcher` ใน Walkthrough 1 launcher ที่นี่:
- รับเทนเซอร์อินพุตสองตัวแทนที่จะเป็นตัวเดียว
- คำนวณมิติทั้งสาม (M, N, K) จากรูปร่างของเทนเซอร์ โดยไม่ต้องส่งขนาดด้วยตนเองจาก Python
- จัดสรรและคืนค่าเทนเซอร์เอาต์พุต C แทนที่จะแก้ไขในตำแหน่งเดิม (mutate in-place)
- ใช้ `dim3` ทั้งสำหรับ grid และ block เพื่อแสดงรูปแบบการ launch แบบ 2 มิติ

#### **ขั้นตอนที่ 2: Build**
```bash
pip install --no-build-isolation -v .
```
>**หมายเหตุ**: คำสั่งนี้จะค้นหา `setup.py` ในไดเรกทอรีปัจจุบันเพื่อ build ไฟล์ .cu ที่เราได้สร้างขึ้น


การดำเนินการนี้จะสร้างไฟล์ต่อไปนี้:
<!-- @os:windows -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.pyd`
- `matmul_kernel.hip`: ซอร์ส HIP ที่สร้างจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: ไดเรกทอรีที่มีไฟล์ `.so`
- `matmul_kernel.hip`: ซอร์ส HIP ที่สร้างจากการ hipify ไฟล์ `.cu`; นี่คือสิ่งที่ `hipcc` คอมไพล์จริง ๆ
<!-- @os:end -->

#### **ขั้นตอนที่ 3: ใช้งานจาก Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
รันสคริปต์นี้เพื่อดูเคอร์เนลทำงาน:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**เยี่ยมมาก! คุณเพิ่งทำการคูณเมทริกซ์บน GPU สำเร็จแล้ว** นี่ถือเป็นเหตุการณ์สำคัญ เพราะการคูณเมทริกซ์เป็นแกนหลักของการดำเนินการแมชชีนเลิร์นนิงสมัยใหม่ เช่น:
- เลเยอร์ของนิวรัลเน็ตเวิร์ก
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

คุณได้เรียนรู้การเขียน คอมไพล์ และเรียกใช้เคอร์เนล GPU โดยใช้ทั้งการคอมไพล์แบบ JIT และ C++ extensions สำหรับการดำเนินการแบบขนานพื้นฐาน

**การปรับแต่งประสิทธิภาพ:**
- **Shared memory tiling** - แคชบล็อกข้อมูลเพื่อลดการเข้าถึงหน่วยความจำ global
- **Memory coalescing** - ปรับรูปแบบการเข้าถึงหน่วยความจำให้เหมาะสมกับแบนด์วิดท์

**อัลกอริทึมในโลกจริง:**
- **2D Convolution** - ฟิลเตอร์ขนาดเล็ก (kernel) เลื่อนผ่านภาพ โดยคำนวณพิกเซลเอาต์พุตแต่ละตัวจากผลรวมถ่วงน้ำหนักของพิกเซลข้างเคียง สิ่งนี้แนะนำการคำนวณแบบ stencil และ shared memory tiling โดยที่เธรดจะนำภูมิภาคของภาพที่ซ้อนทับกันมาใช้ซ้ำเพื่อลดการเข้าถึงหน่วยความจำ global
- **Softmax Function**: Softmax แปลงเวกเตอร์ของตัวเลขให้เป็นความน่าจะเป็นที่รวมกันได้ 1 ซึ่งมักใช้ในเอาต์พุตของนิวรัลเน็ตเวิร์ก การนำไปใช้อย่างมีประสิทธิภาพบน GPU จะแนะนำการรีดักชันแบบขนานและเทคนิคความเสถียรทางตัวเลขในขณะที่ประมวลผลเวกเตอร์ขนาดใหญ่

**ข้อพิจารณาสำหรับการใช้งานจริง:**
- **การจัดการข้อผิดพลาด** - การตรวจสอบขอบเขตและการจัดการอุปกรณ์
- **การผสานรวมกับ PyTorch** - Custom operators ที่รองรับ autograd