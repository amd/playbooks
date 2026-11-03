<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## نظرة عامة

اكتب نواة (kernel) لوحدة معالجة رسومية من الصفر، وقم بترجمتها، وشغّلها على وحدة معالجة رسومية من AMD، وشاهد ارتفاع نسبة الاستخدام. يوضح هذا الدليل كيف يعمل الحساب على وحدة معالجة الرسومات فعليًا: كتابة كود النواة، وتنفيذه بشكل متوازٍ عبر آلاف الخيوط (threads).

> **ملاحظة**: هذا دليل معقّد إلى حد ما، وقد يتطلب بعض التصحيح والتعديلات الإضافية.

## ما ستتعلمه

<!-- @os:windows -->
- كيف تعمل نوى وحدة معالجة الرسومات: الشبكات (grids)، والكتل (blocks)، والخيوط (threads)، ونموذج الفهرسة الذي يربطها بالبيانات
- كيف تتيح حزمة AMD ROCm/HIP كتابة كود بأسلوب CUDA يعمل على وحدات معالجة الرسومات من AMD دون أي تعديل
- كيفية ترجمة نواة أثناء وقت التشغيل باستخدام `torch.cuda._compile_kernel`
- كيفية بناء امتداد نواة أصلي بلغة C++ باستخدام `CUDAExtension` + pybind11، قابل للاستيراد من Python
<!-- @os:end -->
<!-- @os:linux -->
- كيف تعمل نوى وحدة معالجة الرسومات: الشبكات (grids)، والكتل (blocks)، والخيوط (threads)، ونموذج الفهرسة الذي يربطها بالبيانات
- كيف تتيح حزمة AMD ROCm/HIP كتابة كود بأسلوب CUDA يعمل على وحدات معالجة الرسومات من AMD دون أي تعديل
- كيفية ترجمة نواة أثناء وقت التشغيل باستخدام `torch.cuda._compile_kernel`
- كيفية بناء امتداد نواة أصلي بلغة C++ باستخدام `CUDAExtension` + pybind11، قابل للاستيراد من Python
- كيفية قياس زمن تنفيذ النواة ومراقبة استخدام وحدة معالجة الرسومات مباشرة باستخدام `amd-smi`
<!-- @os:end -->

---

يغطي هذا الدليل منهجين لتطوير النوى:

<!-- @os:windows -->
| المنهج | نقطة الدخول |
|---|---|
| **الترجمة الفورية (JIT Compilation)** | `torch.cuda._compile_kernel`، اكتب النواة كسلسلة نصية بلغة Python، دون أي خطوة بناء |
| **امتداد C++** | `CUDAExtension` + pybind11: ترجمة ملف `.cu` إلى ملف `.pyd` أصلي واستيراده |
<!-- @os:end -->
<!-- @os:linux -->
| المنهج | نقطة الدخول |
|---|---|
| **الترجمة الفورية (JIT Compilation)** | `torch.cuda._compile_kernel`، اكتب النواة كسلسلة نصية بلغة Python، دون أي خطوة بناء |
| **امتداد C++** | `CUDAExtension` + pybind11: ترجمة ملف `.cu` إلى ملف `.so` أصلي واستيراده |
<!-- @os:end -->

يعمل كلا المنهجين على وحدات معالجة الرسومات من AMD. وهذا ممكن لأن إصدار ROCm من PyTorch يربط سطح واجهة برمجة التطبيقات (API) الكامل لـ CUDA بـ HIP. وهذا يعني أن `torch.cuda`، و`CUDAExtension`، وصياغة نوى CUDA تعمل جميعها على أجهزة AMD بشكل شفاف.

---

## الخلفية

### ما هي نواة وحدة معالجة الرسومات (GPU Kernel)؟

نواة وحدة معالجة الرسومات هي دالة تعمل بشكل متوازٍ عبر آلاف الخيوط في وحدة معالجة الرسومات في آن واحد. على عكس دالة وحدة المعالجة المركزية (CPU) التي تُنفَّذ مرة واحدة لكل استدعاء، يتم إطلاق النواة مع **شبكة (grid)** من **الكتل (blocks)**، تحتوي كل منها على العديد من **الخيوط (threads)**، جميعها تنفّذ نفس الكود على بيانات مختلفة.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### نموذج فهرسة الخيوط

عند إطلاق نواة، تحدد بُعدين اثنين:

| المتغير | المعنى |
|---|---|
| `gridDim` | عدد الكتل في الشبكة |
| `blockDim` | عدد الخيوط لكل كتلة |

يتوفر لكل خيط ثلاثة متغيرات مدمجة للقراءة فقط:

| المتغير | المعنى |
|---|---|
| `blockIdx.x` | الكتلة التي ينتمي إليها هذا الخيط |
| `blockDim.x` | عدد الخيوط في كتلة واحدة |
| `threadIdx.x` | فهرس الخيط ضمن كتلته |

### معرّف الخيط العام

تُجمَع هذه المتغيرات لحساب فهرس خيط فريد عالميًا:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

إجمالي عدد الخيوط = `gridDim.x * blockDim.x`. يعالج كل خيط عنصرًا واحدًا بشكل مستقل. وهذا هو أساس **التوازي في البيانات (data parallelism)**. حيث تُنفَّذ نفس العملية على عناصر عديدة في آنٍ واحد، دون أي اعتماد بين الخيوط.

---

### نموذج تنفيذ وحدة معالجة الرسومات: الموجات (Wavefronts)

تُنفِّذ وحدات معالجة الرسومات من AMD الخيوط في مجموعات من **32** تسمى **الموجات (wavefronts)**. تُنفِّذ جميع الخيوط في الموجة نفس التعليمة في آنٍ واحد. وهذا يؤثر على اختيار حجم الكتلة الأمثل (256 خيطًا = 8 موجات = كفاءة جدولة جيدة).

### برمجة وحدات معالجة الرسومات من AMD: HIP + ROCm

**ROCm** هي حزمة حوسبة وحدة معالجة الرسومات مفتوحة المصدر من AMD (تعريفات، ومترجمات، ومكتبات، وبيئة تشغيل). وتقع **HIP** فوقها، وهي مصممة لتكون مطابقة نحويًا لـ CUDA. يربط إصدار ROCm من PyTorch بشكل شفاف `torch.cuda.*` بـ HIP، لذا يعمل نفس الكود على وحدات معالجة الرسومات من AMD.

---

### PyTorch + AMD/HIP

تُصدر PyTorch إصدارًا من ROCm حيث يكون سطح واجهة برمجة التطبيقات لـ CUDA (`torch.cuda.*`) مدعومًا بشكل شفاف بواسطة HIP. وهذا يعني:

- تعمل `torch.cuda.is_available()` على وحدات معالجة الرسومات من AMD مع ROCm
- تخصص `tensor.to("cuda")` الذاكرة على وحدة معالجة الرسومات من AMD
- يعرض `torch.version.hip` إصدار HIP

كما تعرض PyTorch الدالة `torch.cuda._compile_kernel()`، وهي اختصار عالي المستوى لترجمة سلسلة نواة خام أثناء وقت التشغيل (JIT) والحصول على كائن قابل للاستدعاء، دون الحاجة إلى خطوة بناء منفصلة.

---

<!-- @device:halo_box -->
## التحقق من تحديثات البرامج

<!-- @require:software-update -->
<!-- @device:end -->

## تثبيت متطلبات البرامج الأساسية
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### المتطلبات الأساسية - Windows
- ثبّت أحدث إصدار من: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### إنشاء بيئة افتراضية

<!-- @os:linux -->
<!-- @device:halo_box -->
على Linux، افتح طرفية (terminal) في الدليل الذي تختاره، واتبع الأوامر لإنشاء بيئة افتراضية (venv) مع تثبيت ROCm+Pytorch مسبقًا.
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
**امنح مستخدمك إمكانية الوصول إلى أجهزة وحدة معالجة الرسومات** (سجّل الخروج ثم الدخول مرة أخرى ليصبح هذا نافذًا):

```bash
sudo usermod -aG render,video $LOGNAME
```

على Linux، افتح طرفية (terminal) في الدليل الذي تختاره، واتبع الأوامر لإنشاء بيئة افتراضية (venv).
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
على Windows، افتح طرفية (terminal) في الدليل الذي تختاره، واتبع الأوامر لإنشاء بيئة افتراضية (venv).
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **نصيحة**: قد يحتاج مستخدمو Windows إلى تعديل سياسة تنفيذ PowerShell الخاصة بهم (مثل
> ضبطها على RemoteSigned أو Unrestricted) قبل تشغيل بعض أوامر Powershell.

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
> **ملاحظة:** بالنسبة لهذا الدليل، يجب تثبيت ROCm وPyTorch في البيئة الافتراضية حتى على Ryzen AI Halo، لأن ترجمة النواة المخصصة تتطلب رؤوس التطوير الكاملة.

ثبّت ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

ثبّت PyTorch:
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
قم بتثبيت أدوات بناء C/C++ الخاصة بنظام Linux. هذه تبعية على مستوى النظام وهي مطلوبة لدروس ملحق C++ لأن `CUDAExtension` يقوم ببناء وحدات `.so` أصلية من ملفات `.cu`.

قم بتشغيل هذا مرة واحدة على جهاز Linux، خارج بيئة Python الافتراضية التي تم إنشاؤها:

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
يرجى التأكد من تثبيت [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) أو [إصدار أحدث](https://visualstudio.microsoft.com/vs/community/) مع حزمة عمل **Desktop development with C++**.

> **ملاحظة**: إعداد بيئة Visual Studio C++ هذه مطلوب فقط لطريقة **ملحق C++**. وهو غير مطلوب لطريقة تجميع JIT.

افتح موجه أوامر PowerShell وقم بتشغيل الأوامر التالية قبل بناء ملحق C++.

**الخطوة 1: العثور على بيئة Visual Studio C++ المثبتة**

**(A) حدد موقع `vswhere.exe`، الذي يتم تثبيته مع مثبت Visual Studio (Visual Studio Installer)**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(B) ابحث عن `vcvars64.bat` من Visual Studio 2022 أو إصدار أحدث مع أدوات بناء C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(C) اطبع بيئة Visual Studio C++ المستخدمة**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**الخطوة 2: تفعيل بيئة بناء Visual Studio C++**

**(A) قم بتشغيل `vcvars64.bat` والتقط البيئة التي يقوم بإعدادها**

هذا يجعل `cl.exe`، و`INCLUDE`، و`LIB`، و`LIBPATH`، ومسارات Windows SDK متاحة.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(B) استورد متغيرات بيئة Visual Studio إلى جلسة PowerShell هذه**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**الخطوة 3: تحقق من أن مترجم Microsoft C++ متاح**

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

#### تعيين متغيرات البيئة
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
تحقق من أن معالج الرسومات AMD مرئي باستخدام:
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

قم بإنشاء بنية الدليل التالية عن طريق إنشاء **مجلدين جديدين** وتنزيل الملفات المقابلة:

| الدليل | الملفات المراد تنزيلها | الوصف |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| ملفات JIT وملحق C++ لكرنل جمع المتجهات |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | ملفات JIT وملحق C++ لكرنل ضرب المصفوفات |


## الدرس التطبيقي 1: جمع المتجهات

#### الطريقة A: تجميع JIT

يعني تجميع JIT (Just-In-Time) أن الكرنل مكتوب كسلسلة نصية خام بلغة C++ داخل Python ويتم تجميعه في وقت التشغيل، دون الحاجة إلى خطوات بناء إضافية.

لاستخدام [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)، تأكد من تنزيله وقم بتشغيل:
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
> **نصيحة**: يقوم البرنامج النصي أيضًا بإنشاء خيط في الخلفية يستطلع `amd-smi` كل 100 مللي ثانية لتسجيل ذروة ومتوسط استخدام معالج الرسومات (GPU) أثناء تشغيل الكرنل.
<!-- @os:end -->

> **ملاحظة**: **لماذا حجم الكتلة (Block Size) هو 256؟** <br>
> - يستخدم الكرنل **256 خيطًا لكل كتلة (block)** لأنه يتماشى بشكل جيد مع **نموذج تنفيذ موجات (wavefront) معالجات AMD**.
> - تذكر أن أجهزة AMD تنفذ الخيوط في مجموعات من 32 خيطًا، مما ينتج عنه 8 موجات لكل كتلة. (8 موجات × 32 خيطًا = كتلة واحدة)


**ما الذي يقوم به عبء العمل:**

يضيف الكرنل عمل إضافي بشكل مصطنع لإظهار استخدام معالج الرسومات (GPU):

- **100,000,000 عنصر** في المصفوفة (tensor)
- **الحلقة الداخلية تعمل 1,000 مرة** لكل عنصر في كل عملية تشغيل للكرنل  
- **200 عملية تشغيل** للكرنل إجمالاً

**الحساب:**  
- كل عنصر: يتم زيادته بمقدار 1 × 1,000 تكرار × 200 عملية تشغيل = 200,000  
- النتيجة النهائية: 1.0 (القيمة الابتدائية) + 200,000 (الإضافات) = 200,001.0

**لماذا الحلقة الداخلية؟**  
- بدون حلقة `for (int i = 0; i < 1000; i++)`، ستنتهي 200 عملية تشغيل على الفور ولن تتمكن أدوات المراقبة من التقاط استخدام ذي معنى لمعالج الرسومات (GPU). العمل المصطنع يجعل كل تشغيل للكرنل يستغرق وقتًا كافيًا لتتمكن أدوات المراقبة من قياس الأداء.

<!-- @os:linux -->
**النتيجة المتوقعة:**[أرقام الأداء ستختلف]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: على نظام Windows، لا يدعم `amd-smi`. لتتبع استخدام معالج الرسومات (GPU)، يمكنك استخدام مدير المهام (Task Manager)، حيث يجب أن ترى ارتفاعًا مؤقتًا في الاستخدام عند تشغيل البرنامج.

**النتيجة المتوقعة:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**عمل رائع! لقد قمت للتو بتشغيل أول كرنل GPU الخاص بك.**

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
#### الأسلوب B: امتداد ++C

الأسلوب الثاني أكثر يدوية: اكتب النواة (kernel) وربط Python في ملف `.cu` واحد، ثم قم بتجميعه محليًا باستخدام نظام البناء الخاص بـ PyTorch، واستورده إلى Python.

<!-- @os:windows -->
> **ملاحظة**: يتطلب أسلوب امتداد ++C بيئة بناء Visual Studio C++ لأن PyTorch يقوم بتجميع ملف مصدر `.cu` إلى وحدة امتداد أصلية `.pyd`. يعتمد بناء هذا الامتداد الأصلي على سلسلة أدوات ++Microsoft C (المترجم، والرابط، وأدوات البناء) التي يوفرها Visual Studio. قم بتشغيل أوامر تفعيل Visual Studio من قسم الإعداد قبل بناء الامتداد.
<!-- @os:end -->

قم بتنزيل الملفات التالية إذا لم تكن قد قمت بذلك بالفعل:
<!-- @os:windows -->
| الملف | الدور |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | النواة + المُشغّل + ربط pybind11، كل ذلك في ملف واحد |
| [setup.py](assets/Vector_Addition/setup.py) | نص البناء البرمجي، يستخدم `CUDAExtension` لتجميع ملف `.cu` إلى `.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | نص برمجي بلغة Python يقوم بتشغيل المخرجات المبنية |
<!-- @os:end -->

<!-- @os:linux -->
| الملف | الدور |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | النواة + المُشغّل + ربط pybind11، كل ذلك في ملف واحد |
| [setup.py](assets/Vector_Addition/setup.py) | نص البناء البرمجي، يستخدم `CUDAExtension` لتجميع ملف `.cu` إلى `.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | نص برمجي بلغة Python يقوم بتشغيل المخرجات المبنية |
<!-- @os:end -->

#### **الخطوة 1: النواة والمُشغّل والربط** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**نصيحة**: لماذا نستخدم `hipDeviceSynchronize()`؟ <br>
> - عمليات تشغيل نواة الـ GPU غير متزامنة. عندما تشغّل وحدة المعالجة المركزية (CPU) الأمر `add_one<<<grid_size, block_size>>>(data, n);` فإنها ستنفذ التعليمة التالية فورًا دون انتظار الـ GPU. يُجبر `hipDeviceSynchronize()` وحدة المعالجة المركزية على الانتظار حتى تكتمل نواة الـ GPU.

#### **الخطوة 2: البناء**
```bash
pip install --no-build-isolation -v .
```
>**ملاحظة**: يبحث هذا الأمر عن `setup.py` في الدليل الحالي لبناء ملف .cu الذي أنشأناه.


`CUDAExtension` هي أداة مساعدة لبناء CUDA من `torch.utils.cpp_extension`. مع ROCm، يقوم PyTorch **بإعادة توجيه `CUDAExtension` لاستخدام `hipcc`** بدلًا من `nvcc`. تعترض ROCm مسار البناء وتوجّهه عبر مترجم HIP، لتحويل كود CUDA إلى AMD.

ينتج عن ذلك الملفات التالية:
<!-- @os:windows -->
- `build/`: دليل يحتوي على ملفات `.pyd`
- `add_one_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu`؛ وهذا ما قام `hipcc` بتجميعه فعليًا
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: دليل يحتوي على ملفات `.so`
- `add_one_kernel.hip`: مصدر HIP الناتج عن تحويل ملف `.cu`؛ وهذا ما قام `hipcc` بتجميعه فعليًا
<!-- @os:end -->

#### **الخطوة 3: الاستخدام من Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
قم بتنفيذ هذا النص البرمجي لرؤية النواة أثناء العمل:
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

## الشرح التفصيلي 2: ضرب المصفوفات

يحسب ضرب المصفوفات **C = A × B** حيث:
- **A** بحجم M×N (صفوف × أعمدة)
- **B** بحجم N×K  
- **C** بحجم M×K (النتيجة)

يُعرَّف كل عنصر ناتج كالتالي:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

يُحسب كل عنصر من عناصر C بشكل مستقل، مما يجعل هذا مثاليًا للتوازي على الـ GPU.

#### كيفية ربط ذلك بخيوط الـ GPU

على عكس جمع المتجهات (أحادي البعد)، ينتج ضرب المصفوفات **مخرجات ثنائية الأبعاد**، لذا نستخدم **شبكة خيوط ثنائية الأبعاد**:

| | جمع المتجهات | ضرب المصفوفات |
|---|---|---|
| **شكل المخرجات** | مصفوفة أحادية البعد | مصفوفة ثنائية الأبعاد (M×K) |
| **تخطيط الخيوط** | خيط واحد ← عنصر واحد | خيط واحد ← عنصر ناتج واحد |
| **نمط التشغيل** | شبكة أحادية البعد: `(grid_x, 1, 1)` | شبكة ثنائية الأبعاد: `(grid_x, grid_y, 1)` |
| **حجم الكتلة** | `(256, 1, 1)` | `(16, 16, 1)` = 256 خيطًا |

يحسب كل خيط عنصرًا واحدًا من مصفوفة الناتج C. يحسب الخيط عند الموضع `(row, col)` القيمة `C[row][col]` بضرب الصف المقابل من A في العمود المقابل من B.

**تنظيم الذاكرة**: ذاكرة الـ GPU مسطحة (أحادية البعد)، لكن المصفوفات تُخزَّن صفًا تلو الآخر. للوصول إلى `A[row][col]`، تستخدم النواة `A[row * N + col]`.


#### الأسلوب A: التجميع الفوري (JIT):

كما في الشرح التفصيلي 1، تُكتب النواة كسلسلة نصية خام بلغة ++C داخل Python وتُجمَّع في وقت التشغيل عبر أداة JIT المدمجة في PyTorch.


لاستخدام [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)، تأكد من تنزيله وشغّل:
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

يتحقق النص البرمجي من النتيجة مقارنةً بـ `torch.mm` بهامش تسامح صغير. قد ينتج عن الحساب العشري على الـ GPU اختلافات عددية طفيفة مقارنةً بتنفيذات وحدة المعالجة المركزية بسبب ترتيب الاختزال المتوازي.

<!-- @os:linux -->
**المخرجات المتوقعة:**[ستختلف أرقام الأداء]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **ملاحظة**: على نظام Windows، لا يُدعم `amd-smi`. لتتبع استخدام الـ GPU، يمكنك استخدام مدير المهام، حيث يجب أن تلاحظ ارتفاعًا موجزًا في الاستخدام عند تشغيل البرنامج.

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
#### النهج ب: امتداد ++C

النهج الثاني أكثر يدوية: اكتب النواة (kernel) وربط Python في ملف `.cu` واحد، وقم بترجمته بشكل أصلي باستخدام نظام البناء الخاص بـ PyTorch، ثم استورده إلى Python.

<!-- @os:windows -->
> **ملاحظة**: يتطلب نهج امتداد ++C بيئة بناء ++Visual Studio C لأن PyTorch يُترجم ملف المصدر `.cu` إلى وحدة امتداد أصلية `.pyd`. يعتمد بناء هذا الامتداد الأصلي على سلسلة أدوات ++Microsoft C (المُترجم، والرابط، وأدوات البناء) التي يوفرها Visual Studio. قم بتشغيل أوامر تفعيل Visual Studio من قسم الإعداد قبل بناء الامتداد.
<!-- @os:end -->

قم بتنزيل الملفات التالية إذا لم تكن قد فعلت ذلك بالفعل:
<!-- @os:windows -->
| الملف | الدور |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | النواة + المُطلق + ربط pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لترجمة ملف `.cu` إلى `.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | سكريبت Python يقوم بتشغيل النتائج المبنية |
<!-- @os:end -->
<!-- @os:linux -->
| الملف | الدور |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | النواة + المُطلق + ربط pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | سكريبت البناء، يستخدم `CUDAExtension` لترجمة ملف `.cu` إلى `.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | سكريبت Python يقوم بتشغيل النتائج المبنية |
<!-- @os:end -->

#### **الخطوة 1: النواة والمُطلق والربط** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

مقارنة بـ `add_one_launcher` في الدرس التوضيحي 1، فإن المُطلق هنا:
- يأخذ مصفوفتين إدخال بدلاً من واحدة
- يشتق الأبعاد الثلاثة (M وN وK) من أشكال المصفوفات، بدون تمرير حجم يدوي من Python
- يخصص ويعيد مصفوفة الإخراج C، بدلاً من التعديل في المكان
- يستخدم `dim3` لكل من الشبكة والكتلة للتعبير عن شكل الإطلاق ثنائي الأبعاد

#### **الخطوة 2: البناء**
```bash
pip install --no-build-isolation -v .
```
>**ملاحظة**: يبحث هذا الأمر عن `setup.py` في الدليل الحالي لبناء ملف .cu الذي أنشأناه.


هذا ينتج الملفات التالية:
<!-- @os:windows -->
- `build/`: دليل يحتوي على ملفات `.pyd`
- `matmul_kernel.hip`: مصدر HIP الذي تم إنشاؤه من تحويل ملف `.cu` إلى صيغة HIP؛ وهذا ما قام `hipcc` بترجمته فعليًا
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: دليل يحتوي على ملفات `.so`
- `matmul_kernel.hip`: مصدر HIP الذي تم إنشاؤه من تحويل ملف `.cu` إلى صيغة HIP؛ وهذا ما قام `hipcc` بترجمته فعليًا
<!-- @os:end -->

#### **الخطوة 3: الاستخدام من Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
نفّذ هذا السكريبت لرؤية النواة في العمل:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**الناتج المتوقع:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**رائع! لقد قمت للتو بتنفيذ ضرب المصفوفات على وحدة معالجة الرسومات (GPU).** هذا إنجاز مهم لأن ضرب المصفوفات هو العمود الفقري لعمليات التعلم الآلي الحديثة مثل:
- طبقات الشبكات العصبية
- آليات الانتباه
- التضمينات
- المحولات (Transformers)

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

لقد تعلمت كتابة وترجمة وإطلاق نوى GPU باستخدام كل من الترجمة الفورية (JIT) وامتدادات ++C للعمليات المتوازية الأساسية.

**تحسينات الأداء:**
- **تجزئة الذاكرة المشتركة (Shared memory tiling)** - تخزين كتل البيانات مؤقتًا لتقليل الوصول إلى الذاكرة العامة
- **دمج الذاكرة (Memory coalescing)** - تحسين أنماط الوصول إلى الذاكرة من أجل النطاق الترددي

**خوارزميات واقعية:**
- **الالتفاف ثنائي الأبعاد (2D Convolution)** - مرشح صغير (نواة) ينزلق عبر صورة، ويحسب كل بكسل إخراج من مجموع موزون للبكسلات المجاورة. يقدم هذا حسابات ستنسل (stencil) وتجزئة الذاكرة المشتركة، حيث تعيد الخيوط استخدام مناطق الصورة المتداخلة لتقليل الوصول إلى الذاكرة العامة.
- **دالة Softmax**: تحول Softmax متجهًا من الأرقام إلى احتمالات يبلغ مجموعها 1، وتُستخدم عادة في مخرجات الشبكات العصبية. يقدم تنفيذها بكفاءة على GPU عمليات اختزال متوازية وتقنيات استقرار عددي أثناء معالجة متجهات كبيرة.

**اعتبارات الإنتاج:**
- **معالجة الأخطاء** - التحقق من الحدود وإدارة الأجهزة
- **تكامل PyTorch** - عوامل تشغيل مخصصة مع دعم autograd