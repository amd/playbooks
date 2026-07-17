<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> يستخدم هذا الدليل علامات خاصة لا يستطيع GitHub عرضها. يرجى زيارة [amd.com/playbooks](https://amd.com/playbooks) لمعاينة هذا المحتوى بشكل صحيح.
<!-- @github-only:end -->

## نظرة عامة

اكتب نواة GPU من الصفر، وقم بتجميعها، وشغّلها على AMD GPU، وراقب ارتفاع معدل الاستخدام. يوضح هذا الدليل كيفية عمل الحوسبة على GPU فعلياً: اكتب كود النواة، ونفّذه بالتوازي عبر آلاف الخيوط.

> **ملاحظة**: هذا دليل معقد نسبياً، وقد يتطلب بعض التصحيح والتعديلات الإضافية.

## ما ستتعلمه

<!-- @os:windows -->
- كيفية عمل نوى GPU: الشبكات، والكتل، والخيوط، ونموذج الفهرسة الذي يربطها بالبيانات
- كيف يتيح لك مكدس AMD ROCm/HIP كتابة كود بأسلوب CUDA يعمل على AMD GPUs دون تعديل
- كيفية تجميع نواة في وقت التشغيل باستخدام `torch.cuda._compile_kernel`
- كيفية بناء امتداد C++ أصلي للنواة باستخدام `CUDAExtension` + pybind11، قابل للاستيراد من Python
<!-- @os:end -->
<!-- @os:linux -->
- كيفية عمل نوى GPU: الشبكات، والكتل، والخيوط، ونموذج الفهرسة الذي يربطها بالبيانات
- كيف يتيح لك مكدس AMD ROCm/HIP كتابة كود بأسلوب CUDA يعمل على AMD GPUs دون تعديل
- كيفية تجميع نواة في وقت التشغيل باستخدام `torch.cuda._compile_kernel`
- كيفية بناء امتداد C++ أصلي للنواة باستخدام `CUDAExtension` + pybind11، قابل للاستيراد من Python
- كيفية قياس وقت تنفيذ النواة ومراقبة استخدام GPU المباشر باستخدام `amd-smi`
<!-- @os:end -->

---

يغطي هذا الدليل نهجين لتطوير النوى:

<!-- @os:windows -->
| النهج | نقطة الدخول |
|---|---|
| **التجميع الفوري (JIT)** | `torch.cuda._compile_kernel`، اكتب نواة كسلسلة نصية Python، دون خطوة بناء |
| **امتداد C++** | `CUDAExtension` + pybind11: جمّع ملف `.cu` إلى ملف `.pyd` أصلي واستورده |
<!-- @os:end -->
<!-- @os:linux -->
| النهج | نقطة الدخول |
|---|---|
| **التجميع الفوري (JIT)** | `torch.cuda._compile_kernel`، اكتب نواة كسلسلة نصية Python، دون خطوة بناء |
| **امتداد C++** | `CUDAExtension` + pybind11: جمّع ملف `.cu` إلى ملف `.so` أصلي واستورده |
<!-- @os:end -->

كلا النهجين يعملان على AMD GPUs. هذا ممكن لأن بناء ROCm في PyTorch يربط سطح واجهة برمجة تطبيقات CUDA بالكامل بـ HIP. وهذا يعني أن `torch.cuda` و`CUDAExtension` وصياغة نواة CUDA تعمل جميعها على أجهزة AMD بشكل شفاف.

---

## الخلفية النظرية

### ما هي نواة GPU؟

نواة GPU هي دالة تعمل بالتوازي عبر آلاف خيوط GPU في آنٍ واحد. على عكس دالة CPU التي تُنفَّذ مرة واحدة لكل استدعاء، تُطلَق النواة بـ**شبكة** من **الكتل**، تحتوي كل منها على عدد كبير من **الخيوط**، وتنفّذ جميعها نفس الكود على بيانات مختلفة.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### نموذج فهرسة الخيوط

عند إطلاق نواة، تحدد بُعدين:

| المتغير | المعنى |
|---|---|
| `gridDim` | عدد الكتل في الشبكة |
| `blockDim` | عدد الخيوط لكل كتلة |

يمتلك كل خيط وصولاً إلى ثلاثة متغيرات مدمجة للقراءة فقط:

| المتغير | المعنى |
|---|---|
| `blockIdx.x` | الكتلة التي ينتمي إليها هذا الخيط |
| `blockDim.x` | عدد الخيوط في كتلة واحدة |
| `threadIdx.x` | فهرس الخيط داخل كتلته |

### معرّف الخيط العالمي

تُجمع هذه المتغيرات لحساب فهرس خيط فريد عالمياً:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

إجمالي الخيوط = `gridDim.x * blockDim.x`. يعالج كل خيط عنصراً واحداً بشكل مستقل. هذا هو أساس **التوازي في البيانات**. تعمل نفس العملية على عناصر كثيرة في آنٍ واحد، دون أي تبعية بين الخيوط.

---

### نموذج تنفيذ GPU: موجات الواجهة (Wavefronts)

تُنفّذ AMD GPUs الخيوط في مجموعات من **32** تُسمى **wavefronts**. تُنفّذ جميع الخيوط في wavefront نفس التعليمة في آنٍ واحد. يؤثر هذا على اختيارات حجم الكتلة الأمثل (256 خيطاً = 8 wavefronts = كفاءة جدولة جيدة).

### برمجة AMD GPU: HIP + ROCm

**ROCm** هو مكدس حوسبة GPU مفتوح المصدر من AMD (برامج تشغيل، ومجمّعات، ومكتبات، وبيئة تشغيل). يقع **HIP** فوقه، مصمم ليكون متطابقاً من الناحية النحوية مع CUDA. يربط بناء ROCm في PyTorch بشكل شفاف `torch.cuda.*` بـ HIP، لذا يعمل نفس الكود على AMD GPUs.

---

### PyTorch + AMD/HIP

يوفر PyTorch بناء ROCm حيث يكون سطح واجهة برمجة تطبيقات CUDA (`torch.cuda.*`) مدعوماً بشكل شفاف بواسطة HIP. وهذا يعني:

- `torch.cuda.is_available()` يعمل على AMD GPUs مع ROCm
- `tensor.to("cuda")` يخصص الذاكرة على AMD GPU
- `torch.version.hip` يكشف عن إصدار HIP

يكشف PyTorch أيضاً عن `torch.cuda._compile_kernel()`، وهو اختصار عالي المستوى لتجميع سلسلة نواة خام فورياً والحصول على كائن قابل للاستدعاء، دون الحاجة إلى خطوة بناء منفصلة.

---

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت المتطلبات الأساسية للبرامج
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### المتطلبات الأساسية - Windows
- تثبيت أحدث إصدار: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
على Linux، افتح طرفية في الدليل الذي تختاره واتبع الأوامر لإنشاء بيئة venv مع تثبيت ROCm+PyTorch مسبقاً.
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
**امنح مستخدمك حق الوصول إلى أجهزة GPU** (سجّل الخروج وأعد الدخول لتفعيل هذا الإعداد):

```bash
sudo usermod -aG render,video $LOGNAME
```

على Linux، افتح طرفية في الدليل الذي تختاره واتبع الأوامر لإنشاء بيئة venv.
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
على Windows، افتح طرفية في الدليل الذي تختاره واتبع الأوامر لإنشاء بيئة venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **تلميح**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell (مثلاً
> ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر PowerShell.

<!-- @os:end -->
### تثبيت التبعيات الأساسية
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
> **ملاحظة:** لهذا الدليل التطبيقي، يجب تثبيت ROCm و PyTorch داخل البيئة الافتراضية حتى على Ryzen AI Halo، إذ يتطلب تجميع النواة المخصصة توفر ترويسات التطوير الكاملة.

تثبيت ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

تثبيت PyTorch:
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

### تثبيت التبعيات الإضافية

<!-- @os:linux -->
قم بتثبيت سلسلة أدوات البناء C/C++ لنظام Linux. هذه تبعية على مستوى النظام وهي مطلوبة لعروض امتداد C++ التفصيلية لأن `CUDAExtension` يبني وحدات `.so` أصلية من ملفات `.cu`.

شغّل هذا الأمر مرة واحدة على جهاز Linux، خارج البيئة الافتراضية Python التي تم إنشاؤها:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

بعد تفعيل البيئة الافتراضية `kernel-env`، قم بتثبيت تبعيات بناء Python:
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
يرجى التأكد من تثبيت [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) أو [إصدار أحدث](https://visualstudio.microsoft.com/vs/community/) مع حمل العمل **Desktop development with C++**.

> **ملاحظة**: إعداد بيئة C++ في Visual Studio مطلوب فقط لأسلوب **امتداد C++**. وهو غير مطلوب لأسلوب التجميع في وقت التشغيل JIT.

افتح طرفية PowerShell وشغّل الأوامر التالية قبل بناء امتداد C++.

**الخطوة 1: البحث عن بيئة C++ المثبتة في Visual Studio**

**(أ) تحديد موقع `vswhere.exe`، الذي يُثبَّت مع Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(ب) البحث عن `vcvars64.bat` من Visual Studio 2022 أو أحدث مع أدوات بناء C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(ج) طباعة بيئة C++ الخاصة بـ Visual Studio المستخدمة**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**الخطوة 2: تفعيل بيئة بناء C++ في Visual Studio**

**(أ) تشغيل `vcvars64.bat` والتقاط البيئة التي يضبطها**

هذا يجعل `cl.exe` و`INCLUDE` و`LIB` و`LIBPATH` ومسارات Windows SDK متاحة.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(ب) استيراد متغيرات بيئة Visual Studio إلى جلسة PowerShell الحالية**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**الخطوة 3: التحقق من توفر مترجم Microsoft C++**

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

#### ضبط متغيرات البيئة
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
تحقق من أن AMD GPU مرئي باستخدام:
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

## تنزيل الملفات المطلوبة

أنشئ هيكل الدليل التالي بإنشاء **مجلدين جديدين** وتنزيل الملفات المقابلة:

| الدليل | الملفات المطلوب تنزيلها | الوصف |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ملفات JIT وامتداد C++ لنواة جمع المتجهات |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ملفات JIT وامتداد C++ لنواة ضرب المصفوفات |


## العروض التفصيلية

### العرض التفصيلي 1: جمع المتجهات

#### الأسلوب أ: التجميع في وقت التشغيل JIT

يعني التجميع في وقت التشغيل JIT (Just-In-Time) أن النواة تُكتب كسلسلة نصية خام بلغة C++ داخل Python وتُجمَّع أثناء التشغيل، دون الحاجة إلى خطوات بناء إضافية.

لاستخدام [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)، تأكد من تنزيله ثم شغّل:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**مقتطفات الكود الرئيسية**
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
> **تلميح**: يُشغّل السكريبت أيضاً خيطاً في الخلفية يستطلع `amd-smi` كل 100 مللي ثانية لتسجيل ذروة استخدام GPU ومتوسطه خلال تشغيل النواة.
<!-- @os:end -->

> **ملاحظة**: **لماذا حجم الكتلة 256؟** <br>
> - تستخدم النواة **256 خيطاً لكل كتلة** لأن ذلك يتوافق جيداً مع **نموذج تنفيذ الموجة الأمامية في AMD GPUs**.
> - تذكر أن أجهزة AMD تنفّذ الخيوط في مجموعات من 32 خيطاً، مما ينتج عنه 8 موجات أمامية لكل كتلة. (8 موجات أمامية × 32 خيطاً = كتلة واحدة)


**ما يقوم به حمل العمل:**

تضيف النواة عملاً إضافياً اصطناعياً لإظهار استخدام GPU:

- **100,000,000 عنصر** في الموتر
- **الحلقة الداخلية تعمل 1,000 مرة** لكل عنصر لكل إطلاق للنواة  
- **200 إطلاق للنواة** إجمالاً

**الحسابات:**  
- كل عنصر: يُزاد بمقدار 1 × 1,000 تكرار × 200 إطلاق = 200,000  
- النتيجة النهائية: 1.0 (القيمة الابتدائية) + 200,000 (عمليات الجمع) = 200,001.0

**لماذا الحلقة الداخلية؟**  
- بدون حلقة `for (int i = 0; i < 1000; i++)`، ستنتهي 200 عملية إطلاق فوراً ولن تتمكن أدوات المراقبة من التقاط استخدام GPU بشكل ذي معنى. يجعل العمل الاصطناعي كل تشغيل للنواة طويلاً بما يكفي لأدوات المراقبة لقياس الأداء.

<!-- @os:linux -->
**المخرجات المتوقعة:** [ستتفاوت أرقام الأداء]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: على Windows، لا يُدعم `amd-smi`. لتتبع استخدام GPU، يمكنك استخدام إدارة المهام، حيث يجب أن ترى ارتفاعاً مؤقتاً في الاستخدام عند تشغيل البرنامج.

**المخرجات المتوقعة:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**أحسنت! لقد شغّلت للتو أول نواة GPU خاصة بك.**

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
#### النهج B: امتداد C++

النهج الثاني أكثر يدوية: اكتب النواة وربط Python في ملف `.cu` واحد، وقم بتجميعه بشكل أصلي باستخدام نظام بناء PyTorch، ثم استورده إلى Python.

<!-- @os:windows -->
> **ملاحظة**: يتطلب نهج امتداد C++ بيئة بناء Visual Studio C++ لأن PyTorch يجمّع ملف `.cu` المصدر إلى وحدة امتداد `.pyd` أصلية. يعتمد بناء هذا الامتداد الأصلي على سلسلة أدوات Microsoft C++ (المترجم، والرابط، وأدوات البناء) التي يوفرها Visual Studio. قم بتشغيل أوامر تفعيل Visual Studio من قسم الإعداد قبل بناء الامتداد.
<!-- @os:end -->

قم بتنزيل الملفات التالية إذا لم تكن قد فعلت ذلك بالفعل:
<!-- @os:windows -->
| الملف | الدور |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | النواة + المشغّل + ربط pybind11، كل شيء في ملف واحد |
| [setup.py](assets/Vector_Addition/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لتجميع `.cu` إلى `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | سكريبت Python الذي يشغّل المخرجات المبنية |
<!-- @os:end -->

<!-- @os:linux -->
| الملف | الدور |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | النواة + المشغّل + ربط pybind11، كل شيء في ملف واحد |
| [setup.py](assets/Vector_Addition/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لتجميع `.cu` إلى `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | سكريبت Python الذي يشغّل المخرجات المبنية |
<!-- @os:end -->

#### **الخطوة 1: النواة والمشغّل والربط** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**تلميح**: لماذا نستخدم `hipDeviceSynchronize()`؟ <br>
> - إطلاق نوى GPU غير متزامن. عندما يشغّل CPU الأمر `add_one<<<grid_size, block_size>>>(data, n);` فإنه سينفّذ التعليمة التالية فوراً دون انتظار GPU. يجبر `hipDeviceSynchronize()` CPU على الانتظار حتى تكتمل نواة GPU.

#### **الخطوة 2: البناء**
```bash
pip install --no-build-isolation -v .
```
>**ملاحظة**: يبحث هذا الأمر عن `setup.py` في الدليل الحالي لبناء ملف .cu الذي أنشأناه.


`CUDAExtension` هو مساعد بناء CUDA من `torch.utils.cpp_extension`. مع ROCm، يُعيد PyTorch **تعيين `CUDAExtension` لاستخدام `hipcc`** بدلاً من `nvcc`. يعترض ROCm مسار البناء ويوجّهه عبر مترجم HIP، مما يُنقل كود CUDA إلى AMD.

ينتج عن ذلك الملفات التالية:
<!-- @os:windows -->
- `build/`: دليل يحتوي على ملفات `.pyd`
- `add_one_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu` إلى HIP؛ وهذا ما قام `hipcc` بتجميعه فعلياً
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: دليل يحتوي على ملفات `.so`
- `add_one_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu` إلى HIP؛ وهذا ما قام `hipcc` بتجميعه فعلياً
<!-- @os:end -->

#### **الخطوة 3: الاستخدام من Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
نفّذ هذا السكريبت لرؤية النواة في العمل:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**المخرجات المتوقعة:**
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

### العرض التفصيلي 2: ضرب المصفوفات

يحسب ضرب المصفوفات **C = A × B** حيث:
- **A** هي M×N (صفوف × أعمدة)
- **B** هي N×K  
- **C** هي M×K (النتيجة)

يُعرَّف كل عنصر في المخرجات على النحو التالي:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

يُحسب كل عنصر من C بشكل مستقل، مما يجعل هذه العملية مثالية للتوازي على GPU.

#### كيفية تعيينها على خيوط GPU

على عكس جمع المتجهات (أحادي البعد)، ينتج ضرب المصفوفات **مخرجات ثنائية الأبعاد**، لذا نستخدم **شبكة خيوط ثنائية الأبعاد**:

| | جمع المتجهات | ضرب المصفوفات |
|---|---|---|
| **شكل المخرجات** | مصفوفة أحادية البعد | مصفوفة ثنائية الأبعاد (M×K) |
| **تعيين الخيوط** | خيط واحد ← عنصر واحد | خيط واحد ← عنصر مخرجات واحد |
| **نمط الإطلاق** | شبكة أحادية البعد: `(grid_x, 1, 1)` | شبكة ثنائية الأبعاد: `(grid_x, grid_y, 1)` |
| **حجم الكتلة** | `(256, 1, 1)` | `(16, 16, 1)` = 256 خيطاً |

يحسب كل خيط عنصراً واحداً من مصفوفة المخرجات C. الخيط في الموضع `(row, col)` يحسب `C[row][col]` بضرب الصف المقابل من A في العمود المقابل من B.

**تخطيط الذاكرة**: ذاكرة GPU مسطّحة (أحادية البعد)، لكن المصفوفات مخزّنة صفاً تلو الآخر. للوصول إلى `A[row][col]`، تستخدم النواة `A[row * N + col]`.


#### النهج A: التجميع في وقت التشغيل (JIT):

كما في العرض التفصيلي 1، تُكتب النواة كسلسلة نصية خام بلغة C++ داخل Python وتُجمَّع في وقت التشغيل عبر JIT المدمج في PyTorch.


لاستخدام [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)، تأكد من تنزيله ثم شغّله:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**مقتطفات الكود الرئيسية**
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

يتحقق السكريبت من النتيجة مقارنةً بـ `torch.mm` بتسامح صغير. قد تُنتج العمليات الحسابية للفاصلة العائمة على GPU اختلافات عددية صغيرة مقارنةً بتطبيقات CPU بسبب ترتيب التقليص المتوازي.

<!-- @os:linux -->
**المخرجات المتوقعة:** [ستتفاوت أرقام الأداء]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: على Windows، لا يُدعم `amd-smi`. لتتبع استخدام GPU، يمكنك استخدام إدارة المهام، حيث يجب أن ترى ارتفاعاً مؤقتاً في الاستخدام عند تشغيل البرنامج.

**المخرجات المتوقعة:**
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
#### النهج B: امتداد C++

النهج الثاني أكثر يدوية: اكتب النواة وربط Python في ملف `.cu` واحد، وقم بتجميعه بشكل أصلي باستخدام نظام بناء PyTorch، ثم استورده إلى Python.

<!-- @os:windows -->
> **ملاحظة**: يتطلب نهج امتداد C++ بيئة بناء Visual Studio C++ لأن PyTorch يقوم بتجميع ملف المصدر `.cu` إلى وحدة امتداد `.pyd` أصلية. يعتمد بناء هذا الامتداد الأصلي على سلسلة أدوات Microsoft C++ (المترجم، والرابط، وأدوات البناء) التي توفرها Visual Studio. قم بتشغيل أوامر تفعيل Visual Studio من قسم الإعداد قبل بناء الامتداد.
<!-- @os:end -->

قم بتنزيل الملفات التالية إذا لم تكن قد فعلت ذلك بالفعل:
<!-- @os:windows -->
| الملف | الدور |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | النواة + المشغّل + ربط pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لتجميع `.cu` إلى `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | سكريبت Python الذي يشغّل المخرجات المبنية |
<!-- @os:end -->
<!-- @os:linux -->
| الملف | الدور |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | النواة + المشغّل + ربط pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لتجميع `.cu` إلى `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | سكريبت Python الذي يشغّل المخرجات المبنية |
<!-- @os:end -->

#### **الخطوة 1: النواة والمشغّل والربط** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

بالمقارنة مع `add_one_launcher` في العرض التفصيلي 1، يقوم المشغّل هنا بما يلي:
- يأخذ موترَين كمدخلات بدلاً من واحد
- يستخلص جميع الأبعاد الثلاثة (M، N، K) من أشكال الموترات، دون الحاجة إلى تمرير الحجم يدوياً من Python
- يخصص موتر الإخراج C ويعيده، بدلاً من التعديل في المكان
- يستخدم `dim3` لكل من الشبكة والكتلة للتعبير عن شكل الإطلاق ثنائي الأبعاد

#### **الخطوة 2: البناء**
```bash
pip install --no-build-isolation -v .
```
> **ملاحظة**: يبحث هذا الأمر عن `setup.py` في الدليل الحالي لبناء ملف .cu الذي أنشأناه.


ينتج عن ذلك الملفات التالية:
<!-- @os:windows -->
- `build/`: دليل يحتوي على ملفات `.pyd`
- `matmul_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu` إلى HIP؛ وهذا ما قام `hipcc` بتجميعه فعلياً
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: دليل يحتوي على ملفات `.so`
- `matmul_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu` إلى HIP؛ وهذا ما قام `hipcc` بتجميعه فعلياً
<!-- @os:end -->

#### **الخطوة 3: الاستخدام من Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
نفّذ هذا السكريبت لرؤية النواة في العمل:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**المخرجات المتوقعة:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**رائع! لقد نفّذت للتو ضرب المصفوفات على GPU.** هذه نقطة تحول كبرى لأن ضرب المصفوفات هو العمود الفقري لعمليات التعلم الآلي الحديثة مثل:
- طبقات الشبكات العصبية
- آليات الانتباه
- التضمينات
- المحوّلات

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

## الخطوات التالية

لقد تعلمت كتابة نوى GPU وتجميعها وإطلاقها باستخدام كل من التجميع الفوري (JIT) وامتدادات C++ للعمليات التوازية الأساسية.

**تحسينات الأداء:**
- **تقسيم الذاكرة المشتركة إلى بلاطات** - تخزين كتل البيانات مؤقتاً لتقليل الوصول إلى الذاكرة العامة
- **تنسيق الذاكرة** - تحسين أنماط الوصول إلى الذاكرة لزيادة عرض النطاق الترددي

**الخوارزميات الواقعية:**
- **الالتفاف ثنائي الأبعاد** - يتحرك مرشح صغير (نواة) عبر صورة، محسوباً كل بكسل في المخرجات من مجموع موزون للبكسلات المجاورة. يُقدّم هذا حسابات القالب وتقسيم الذاكرة المشتركة إلى بلاطات، حيث تُعيد الخيوط استخدام مناطق الصورة المتداخلة لتقليل الوصول إلى الذاكرة العامة.
- **دالة Softmax**: تحوّل Softmax متجهاً من الأرقام إلى احتمالات مجموعها 1، وتُستخدم بشكل شائع في مخرجات الشبكات العصبية. يُقدّم تنفيذها بكفاءة على GPU تقليلات متوازية وتقنيات الاستقرار العددي أثناء معالجة المتجهات الكبيرة.

**اعتبارات الإنتاج:**
- **معالجة الأخطاء** - التحقق من الحدود وإدارة الأجهزة
- **تكامل PyTorch** - عوامل تشغيل مخصصة مع دعم autograd