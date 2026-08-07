<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## סקירה כללית

כתבו kernel של GPU מאפס, קמפלו אותו, הפעילו אותו על AMD GPU, וצפו בזינוק בניצולת. מדריך זה מציג כיצד חישוב GPU עובד בפועל: כתיבת קוד ה-kernel, והרצתו במקביל על פני אלפי threads.

> **הערה**: זהו מדריך מורכב למדי, שעשוי לדרוש דיבוג ושינויים נוספים.

## מה תלמדו

<!-- @os:windows -->
- כיצד kernels של GPU עובדים: grids, blocks, threads, ומודל האינדוקס שממפה אותם לנתונים
- כיצד ערימת AMD ROCm/HIP מאפשרת לכתוב קוד בסגנון CUDA שרץ על AMD GPUs ללא שינוי
- כיצד לקמפל kernel בזמן ריצה באמצעות `torch.cuda._compile_kernel`
- כיצד לבנות תוסף kernel מקורי ב-C++ עם `CUDAExtension` + pybind11, שניתן לייבא מ-Python
<!-- @os:end -->
<!-- @os:linux -->
- כיצד kernels של GPU עובדים: grids, blocks, threads, ומודל האינדוקס שממפה אותם לנתונים
- כיצד ערימת AMD ROCm/HIP מאפשרת לכתוב קוד בסגנון CUDA שרץ על AMD GPUs ללא שינוי
- כיצד לקמפל kernel בזמן ריצה באמצעות `torch.cuda._compile_kernel`
- כיצד לבנות תוסף kernel מקורי ב-C++ עם `CUDAExtension` + pybind11, שניתן לייבא מ-Python
- כיצד למדוד את זמן ביצוע ה-kernel ולנטר ניצולת GPU בזמן אמת עם `amd-smi`
<!-- @os:end -->

---

מדריך זה מכסה שתי גישות לפיתוח kernels:

<!-- @os:windows -->
| גישה | נקודת כניסה |
|---|---|
| **קימפול JIT** | `torch.cuda._compile_kernel`, כתיבת kernel כמחרוזת Python, ללא שלב build |
| **תוסף C++** | `CUDAExtension` + pybind11: קימפול קובץ `.cu` ל-`.pyd` מקורי וייבואו |
<!-- @os:end -->
<!-- @os:linux -->
| גישה | נקודת כניסה |
|---|---|
| **קימפול JIT** | `torch.cuda._compile_kernel`, כתיבת kernel כמחרוזת Python, ללא שלב build |
| **תוסף C++** | `CUDAExtension` + pybind11: קימפול קובץ `.cu` ל-`.so` מקורי וייבואו |
<!-- @os:end -->

שתי הגישות פועלות על AMD GPUs. הדבר אפשרי מכיוון שבניית ROCm של PyTorch ממפה את כל שטח ה-API של CUDA ל-HIP. משמעות הדבר היא ש-`torch.cuda`, `CUDAExtension`, ותחביר kernel של CUDA פועלים כולם על חומרת AMD בצורה שקופה.

---

## רקע

### מהו GPU Kernel?

GPU kernel הוא פונקציה הרצה במקביל על פני אלפי threads של GPU בו-זמנית. בניגוד לפונקציית CPU המבוצעת פעם אחת בכל קריאה, kernel מופעל עם **grid** של **blocks**, כל אחד מכיל threads רבים, כולם מבצעים את אותו הקוד על נתונים שונים.

<p align="center">
  <img src="assets/grid_threads.png" width="900"/>
</p>

### מודל אינדוקס Thread

בעת הפעלת kernel יש לציין שני ממדים:

| משתנה | משמעות |
|---|---|
| `gridDim` | מספר ה-blocks ב-grid |
| `blockDim` | מספר ה-threads ב-block |

לכל thread יש גישה לשלושה משתנים מובנים לקריאה בלבד:

| משתנה | משמעות |
|---|---|
| `blockIdx.x` | ל-block איזה thread זה שייך |
| `blockDim.x` | מספר ה-threads ב-block אחד |
| `threadIdx.x` | אינדקס ה-thread בתוך ה-block שלו |

### מזהה Thread גלובלי

משתנים אלה משולבים יחד כדי לחשב אינדקס thread ייחודי גלובלי:

```c
int idx = blockIdx.x * blockDim.x + threadIdx.x;
```

סך ה-threads = `gridDim.x * blockDim.x`. כל thread מעבד אלמנט אחד באופן עצמאי. זהו הבסיס ל**מקביליות נתונים** (data parallelism). אותה פעולה רצה על אלמנטים רבים בו-זמנית, ללא תלות בין threads.

---

### מודל ביצוע GPU: Wavefronts

AMD GPUs מבצעים threads בקבוצות של **32** הנקראות **wavefronts**. כל ה-threads ב-wavefront מריצים את אותה הוראה בו-זמנית. הדבר משפיע על בחירת גודל block אופטימלי (256 threads = 8 wavefronts = יעילות תזמון טובה).

### תכנות AMD GPU: HIP + ROCm

**ROCm** היא ערימת מחשוב GPU בקוד פתוח של AMD (drivers, קומפיילרים, ספריות, runtime). **HIP** יושב מעליה, ומתוכנן להיות זהה תחבירית ל-CUDA. בניית ROCm של PyTorch ממפה בצורה שקופה את `torch.cuda.*` ל-HIP, כך שאותו קוד פועל על AMD GPUs.

---

### PyTorch + AMD/HIP

PyTorch מספקת בנייה של ROCm שבה שטח ה-API של CUDA (`torch.cuda.*`) נתמך בצורה שקופה על ידי HIP. משמעות הדבר היא:

- `torch.cuda.is_available()` פועל על AMD GPUs עם ROCm
- `tensor.to("cuda")` מקצה זיכרון על AMD GPU
- `torch.version.hip` חושף את גרסת ה-HIP

PyTorch גם חושפת את `torch.cuda._compile_kernel()`, קיצור דרך ברמה גבוהה לקימפול JIT של מחרוזת kernel גולמית וקבלת callable, ללא צורך בשלב build נפרד.

---

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### דרישות מוקדמות - Windows
- התקינו את הגרסה העדכנית ביותר של: [AMD Adrenalin Software](https://www.amd.com/en/products/software/adrenalin.html)
<!-- @device:end -->
<!-- @os:end -->

### יצירת סביבה וירטואלית

<!-- @os:linux -->
<!-- @device:halo_box -->
ב-Linux, פתחו טרמינל בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv עם ROCm+Pytorch מותקנים מראש.
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
**הענקת גישה למשתמש שלכם להתקני GPU** (יש להתנתק ולהתחבר מחדש כדי שהשינוי ייכנס לתוקף):

```bash
sudo usermod -aG render,video $LOGNAME
```

ב-Linux, פתחו טרמינל בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv.
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
ב-Windows, פתחו טרמינל בתיקייה לבחירתכם ובצעו את הפקודות ליצירת venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv kernel-env
kernel-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="kernel-env\Scripts\activate" -->

> **טיפ**: ייתכן שמשתמשי Windows יצטרכו לשנות את מדיניות ההרשאות של PowerShell (Execution Policy) (למשל
> להגדיר אותה ל-RemoteSigned או Unrestricted) לפני הרצת חלק מפקודות ה-PowerShell.

<!-- @os:end -->
### התקנת תלויות בסיסיות
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
> **הערה:** עבור המדריך הזה, יש להתקין את ROCm ו-PyTorch לתוך הסביבה הווירטואלית גם ב-Ryzen AI Halo, מכיוון שהידור ליבות מותאמות אישית דורש את כותרות הפיתוח המלאות.

התקנת ROCm:
```powershell
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```

התקנת PyTorch:
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

### התקנת תלויות נוספות

<!-- @os:linux -->
התקן את שרשרת הכלים לבנייה של C/C++ עבור Linux. זוהי תלות ברמת המערכת והיא נדרשת עבור מדריכי ההרחבות ב-C++ מכיוון ש-`CUDAExtension` בונה מודולי `.so` מקוריים מקבצי `.cu`.

הרץ זאת פעם אחת על מכונת ה-Linux, מחוץ לסביבה הווירטואלית של Python שנוצרה:

```bash
sudo apt update
sudo apt install -y build-essential gcc g++
```
<!-- @os:end -->

לאחר הפעלת הסביבה הווירטואלית `kernel-env`, התקן את תלויות הבנייה של Python:
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
יש לוודא ש-[Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) או [חדש יותר](https://visualstudio.microsoft.com/vs/community/) מותקן עם עומס העבודה **Desktop development with C++**.

> **הערה**: הגדרת סביבת ה-C++ של Visual Studio נדרשת רק עבור גישת ה-**C++ Extension**. היא אינה נדרשת עבור גישת JIT Compilation.

פתח מסוף PowerShell והרץ את הפקודות הבאות לפני בניית הרחבת ה-C++.

**שלב 1: איתור סביבת ה-C++ של Visual Studio המותקנת**

**(א) איתור `vswhere.exe`, המותקן יחד עם Visual Studio Installer**
```powershell
$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $VsWhere)) {throw "vswhere.exe was not found. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(ב) איתור `vcvars64.bat` מ-Visual Studio 2022 או חדש יותר עם כלי בנייה של C++**

```powershell
$Vcvars = & $VsWhere `
  -latest `
  -products * `
  -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
  -find "VC\Auxiliary\Build\vcvars64.bat" |
  Select-Object -First 1

if (-not $Vcvars) {throw "Could not find vcvars64.bat. Install Visual Studio 2022 or newer with the Desktop development with C++ workload."}
```

**(ג) הדפסת סביבת ה-C++ של Visual Studio שבשימוש**

```powershell
Write-Host "Using Visual Studio C++ environment: $Vcvars"
```

**שלב 2: הפעלת סביבת הבנייה של Visual Studio C++**

**(א) הרץ את `vcvars64.bat` וקלוט את הסביבה שהוא מגדיר**

פעולה זו הופכת את `cl.exe`, `INCLUDE`, `LIB`, `LIBPATH`, ונתיבי Windows SDK לזמינים.

```powershell
$VsEnv = cmd /c "`"$Vcvars`" && where cl && set" 2>&1
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
  $VsEnv | Out-Host
  throw "Failed to activate the Visual Studio C++ environment. Exit code: $ExitCode"
}
```

**(ב) ייבא את משתני הסביבה של Visual Studio לתוך הסשן הזה של PowerShell**

```powershell
$VsEnv | ForEach-Object {
  if ($_ -match '^([^=]+)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
  }
}
```

**שלב 3: ודא שמהדר ה-C++ של Microsoft זמין**

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

#### הגדרת משתני סביבה
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
ודא שה-GPU של AMD גלוי באמצעות:
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

## הורדת הקבצים הנדרשים

צור את מבנה התיקיות הבא על ידי יצירת **2 תיקיות חדשות** והורדת הקבצים המתאימים:

| תיקייה | קבצים להורדה | תיאור |
|-----------|-------------------|-------------|
| **Vector_Addition/** | [add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py)<br>[add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)<br>[setup.py](assets/Vector_Addition/setup.py)<br>[run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)| קבצי JIT והרחבת C++ עבור ליבת חיבור וקטורים |
| **Matrix_Multiplication/** | [matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py)<br>[matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)<br>[setup.py](assets/Matrix_Multiplication/setup.py)<br>[run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | קבצי JIT והרחבת C++ עבור ליבת כפל מטריצות |


## מדריכים מודרכים

### מדריך 1: חיבור וקטורים

#### גישה א': הידור JIT

הידור JIT (Just-In-Time) פירושו שהליבה נכתבת כמחרוזת C++ גולמית בתוך Python ומהודרת בזמן ריצה, ללא צורך בשלבי בנייה נוספים.

כדי להשתמש ב-[add_one_kernel.py](assets/Vector_Addition/add_one_kernel.py), ודא שהוא הורד והרץ:
```bash
cd Vector_Addition # if not already inside the directory
python add_one_kernel.py
```

**קטעי קוד מרכזיים**
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
> **טיפ**: הסקריפט גם מפעיל תהליכון (thread) ברקע הסוקר את `amd-smi` כל 100 מילישניות כדי לתעד ניצולת GPU שיא וממוצעת במהלך ריצת הליבה.
<!-- @os:end -->

> **הערה**: **מדוע גודל הבלוק הוא 256?** <br>
> - הליבה משתמשת ב-**256 תהליכונים (threads) לבלוק** מכיוון שזה מתיישר היטב עם **מודל הביצוע ה-wavefront של GPUs מבית AMD**.
> - יש לזכור שחומרת AMD מבצעת תהליכונים בקבוצות של 32 תהליכונים, מה שמביא ל-8 wavefronts לכל בלוק. (8 wavefronts x 32 תהליכונים = בלוק אחד)


**מה עושה עומס העבודה:**

הליבה מוסיפה באופן מלאכותי עבודה נוספת כדי להדגים ניצולת GPU:

- **100,000,000 איברים** בטנזור
- **הלולאה הפנימית רצה 1,000 פעמים** לכל איבר בכל הפעלת ליבה  
- **200 הפעלות ליבה** בסך הכול

**חישוב:**  
- כל איבר: מוגדל ב-1 × 1,000 איטרציות × 200 הפעלות = 200,000  
- תוצאה סופית: 1.0 (ערך התחלתי) + 200,000 (תוספות) = 200,001.0

**מדוע הלולאה הפנימית?**  
- ללא הלולאה `for (int i = 0; i < 1000; i++)`, 200 הפעלות היו מסתיימות באופן מיידי וכלי הניטור לא היו לוכדים ניצולת GPU משמעותית. העבודה המלאכותית גורמת לכל הפעלת ליבה להימשך זמן ארוך מספיק כדי שכלי הניטור יוכלו למדוד ביצועים.

<!-- @os:linux -->
**פלט צפוי:**[מספרי הביצועים ישתנו]
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: ב-Windows, `amd-smi` אינו נתמך. כדי לעקוב אחר ניצולת ה-GPU, ניתן להשתמש במנהל המשימות (Task Manager), שם אמורה להיראות קפיצה קצרה בניצולת בעת הרצת התוכנית.

**פלט צפוי:**
```
First 5 elements: tensor([200001., 200001., 200001., 200001., 200001.])
Elapsed time: 2.753s
No GPU Usage captured.
```
<!-- @os:end -->
**עבודה נהדרת! הרגע הרצת את ליבת ה-GPU הראשונה שלך.**

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
#### גישה ב': הרחבת C++

הגישה השנייה ידנית יותר: כתיבת הקרנל וכריכת ה-Python לקובץ `.cu` יחיד, קומפילציה שלו באופן טבעי באמצעות מערכת הבנייה של PyTorch, וייבואו לתוך Python.

<!-- @os:windows -->
> **הערה**: גישת הרחבת ה-C++ דורשת את סביבת הבנייה של Visual Studio C++ מכיוון ש-PyTorch מקמפל את קובץ המקור `.cu` למודול הרחבה טבעי `.pyd`. בניית ההרחבה הטבעית הזו תלויה בשרשרת הכלים של Microsoft C++ (מהדר, מקשר וכלי בנייה) המסופקת על ידי Visual Studio. הריצו את פקודות ההפעלה של Visual Studio מסעיף ההגדרה לפני בניית ההרחבה.
<!-- @os:end -->

הורידו את הקבצים הבאים אם עדיין לא עשיתם זאת:
<!-- @os:windows -->
| קובץ | תפקיד |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | קרנל + מפעיל + כריכת pybind11, הכל בקובץ אחד |
| [setup.py](assets/Vector_Addition/setup.py) | סקריפט בנייה, משתמש ב-`CUDAExtension` כדי לקמפל את ה-`.cu` ל-`.pyd` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | סקריפט Python שמריץ את התוצרים שנבנו |
<!-- @os:end -->

<!-- @os:linux -->
| קובץ | תפקיד |
|---|---|
| [add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu) | קרנל + מפעיל + כריכת pybind11, הכל בקובץ אחד |
| [setup.py](assets/Vector_Addition/setup.py) | סקריפט בנייה, משתמש ב-`CUDAExtension` כדי לקמפל את ה-`.cu` ל-`.so` |
| [run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py) | סקריפט Python שמריץ את התוצרים שנבנו |
<!-- @os:end -->

#### **שלב 1: הקרנל, המפעיל והכריכה** ([add_one_kernel.cu](assets/Vector_Addition/add_one_kernel.cu)):
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

>**טיפ**: מדוע להשתמש ב-`hipDeviceSynchronize()`? <br>
> - הפעלות של קרנל GPU הן אסינכרוניות. כאשר ה-CPU מריץ את `add_one<<<grid_size, block_size>>>(data, n);` הוא יבצע מיד את ההוראה הבאה מבלי להמתין ל-GPU. `hipDeviceSynchronize()` מכריח את ה-CPU להמתין עד שהקרנל של ה-GPU יסתיים.

#### **שלב 2: בנייה**
```bash
pip install --no-build-isolation -v .
```
>**הערה**: פקודה זו מחפשת את `setup.py` בתיקייה הנוכחית כדי לבנות את קובץ ה-.cu שיצרנו.


`CUDAExtension` הוא כלי עזר לבניית CUDA מתוך `torch.utils.cpp_extension`. עם ROCm, PyTorch **ממפה מחדש את `CUDAExtension` כך שישתמש ב-`hipcc`** במקום ב-`nvcc`. ROCm מיירט את נתיב הבנייה ומנתב אותו דרך מהדר ה-HIP, ומעביר קוד CUDA לפלטפורמת AMD.

פעולה זו מייצרת את הקבצים הבאים:
<!-- @os:windows -->
- `build/`: תיקייה עם קובצי `.pyd`
- `add_one_kernel.hip`: מקור ה-HIP שנוצר מ"היפוף" (hipify) של קובץ ה-`.cu`; זה מה ש-`hipcc` בפועל קימפל
<!-- @os:end -->

<!-- @os:linux -->
- `build/`: תיקייה עם קובצי `.so`
- `add_one_kernel.hip`: מקור ה-HIP שנוצר מ"היפוף" (hipify) של קובץ ה-`.cu`; זה מה ש-`hipcc` בפועל קימפל
<!-- @os:end -->

#### **שלב 3: שימוש מ-Python** ([run_compiled_addition.py](assets/Vector_Addition/run_compiled_addition.py)):
הריצו סקריפט זה כדי לראות את הקרנל בפעולה:
```bash
cd Vector_Addition # if not already in directory
python run_compiled_addition.py
```

**פלט צפוי:**
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

### הדרכה 2: כפל מטריצות

כפל מטריצות מחשב **C = A × B** כאשר:
- **A** היא M×N (שורות × עמודות)
- **B** היא N×K  
- **C** היא M×K (התוצאה)

כל אלמנט בפלט מוגדר כך:
$$C[row, col] = \sum_{n=0}^{N-1} A[row, n] \cdot B[n, col]$$

כל אלמנט של C מחושב באופן עצמאי, מה שהופך זאת למושלם לביצוע מקבילי ב-GPU.

#### כיצד זה ממופה לתהליכונים (threads) של ה-GPU

בשונה מחיבור וקטורים (חד-ממדי), כפל מטריצות מייצר **פלט דו-ממדי**, ולכן אנו משתמשים ב**רשת דו-ממדית של תהליכונים**:

| | חיבור וקטורים | כפל מטריצות |
|---|---|---|
| **צורת הפלט** | מערך חד-ממדי | מטריצה דו-ממדית (M×K) |
| **מיפוי תהליכונים** | תהליכון אחד → אלמנט אחד | תהליכון אחד → אלמנט פלט אחד |
| **דפוס הפעלה** | רשת חד-ממדית: `(grid_x, 1, 1)` | רשת דו-ממדית: `(grid_x, grid_y, 1)` |
| **גודל בלוק** | `(256, 1, 1)` | `(16, 16, 1)` = 256 תהליכונים |

כל תהליכון מחשב אלמנט אחד של מטריצת הפלט C. תהליכון במיקום `(row, col)` מחשב את `C[row][col]` על ידי הכפלת השורה המתאימה של A בעמודה המתאימה של B.

**פריסת זיכרון**: זיכרון ה-GPU שטוח (חד-ממדי), אך המטריצות מאוחסנות שורה אחר שורה. כדי לגשת אל `A[row][col]`, הקרנל משתמש ב-`A[row * N + col]`.


#### גישה א': קומפילציית JIT:

כמו בהדרכה 1, הקרנל נכתב כמחרוזת C++ גולמית בתוך Python ומקומפל בזמן ריצה באמצעות מנגנון ה-JIT המובנה של PyTorch.


כדי להשתמש ב-[matmul_kernel.py](assets/Matrix_Multiplication/matmul_kernel.py), ודאו שהוא הורד והריצו:
```bash
cd Matrix_Multiplication # if not already inside the directory
python matmul_kernel.py
```

**קטעי קוד מרכזיים**
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

הסקריפט מאמת את התוצאה מול `torch.mm` בסבילות קטנה. חשבון נקודה צפה ב-GPU עשוי לייצר הבדלים מספריים קטנים בהשוואה למימושי CPU עקב סדר הצטברות (reduction) מקבילי.

<!-- @os:linux -->
**פלט צפוי:**[מספרי הביצועים ישתנו]
```
Elapsed time: 2.753s
Max error vs torch.mm: 0.000160
Peak GPU Utilization: 93%
Average GPU Utilization: 65.94%
```
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: ב-Windows, `amd-smi` אינו נתמך. כדי לעקוב אחר ניצול ה-GPU, ניתן להשתמש במנהל המשימות, שם אמורה להופיע קפיצה קצרה בניצול כאשר תריצו את התוכנית.

**פלט צפוי:**
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
#### גישה B: הרחבת ++C

הגישה השנייה ידנית יותר: כתיבת הקרנל וקישור Python (Python binding) לקובץ `.cu` יחיד, קומפילציה שלו באופן טבעי (native) באמצעות מערכת הבנייה (build system) של PyTorch, וייבוא שלו ל-Python.

<!-- @os:windows -->
> **הערה**: גישת הרחבת ++C דורשת את סביבת הבנייה של Visual Studio C++ מכיוון ש-PyTorch מקמפל את קובץ המקור `.cu` למודול הרחבה `.pyd` טבעי (native). בניית ההרחבה הטבעית הזו תלויה בשרשרת הכלים (toolchain) של Microsoft ++C (מהדר, מקשר וכלי בנייה) המסופקת על ידי Visual Studio. הריצו את פקודות ההפעלה של Visual Studio מחלק ההגדרה לפני בניית ההרחבה.
<!-- @os:end -->

הורידו את הקבצים הבאים אם עדיין לא עשיתם זאת:
<!-- @os:windows -->
| קובץ | תפקיד |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | קרנל + launcher + קישור pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | סקריפט בנייה, משתמש ב-`CUDAExtension` כדי לקמפל את ה-`.cu` ל-`.pyd` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | סקריפט Python שמריץ את הארטיפקטים שנבנו |
<!-- @os:end -->
<!-- @os:linux -->
| קובץ | תפקיד |
|---|---|
| [matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu) | קרנל + launcher + קישור pybind11 |
| [setup.py](assets/Matrix_Multiplication/setup.py) | סקריפט בנייה, משתמש ב-`CUDAExtension` כדי לקמפל את ה-`.cu` ל-`.so` |
| [run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py) | סקריפט Python שמריץ את הארטיפקטים שנבנו |
<!-- @os:end -->

#### **שלב 1: הקרנל, ה-launcher והקישור** ([matmul_kernel.cu](assets/Matrix_Multiplication/matmul_kernel.cu)):
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

בהשוואה ל-`add_one_launcher` בהדרכה 1, ה-launcher כאן:
- לוקח שני טנזורי קלט במקום אחד
- גוזר את כל שלושת הממדים (M, N, K) מצורות הטנזורים, ללא העברת גודל ידנית מ-Python
- מקצה ומחזיר את טנזור הפלט C, במקום לשנות במקום (in-place)
- משתמש ב-`dim3` הן עבור הרשת (grid) והן עבור הבלוק (block) כדי לבטא את צורת ההשקה הדו-ממדית

#### **שלב 2: בנייה**
```bash
pip install --no-build-isolation -v .
```
>**הערה**: פקודה זו מחפשת את `setup.py` בתיקייה הנוכחית כדי לבנות את קובץ ה-.cu שיצרנו.


פעולה זו מייצרת את הקבצים הבאים:
<!-- @os:windows -->
- `build/`: תיקייה עם קבצי ה-`.pyd`
- `matmul_kernel.hip`: קוד המקור HIP שנוצר מהמרת (hipifying) קובץ ה-`.cu`; זהו למעשה מה ש-`hipcc` קימפל
<!-- @os:end -->
<!-- @os:linux -->
- `build/`: תיקייה עם קבצי ה-`.so`
- `matmul_kernel.hip`: קוד המקור HIP שנוצר מהמרת (hipifying) קובץ ה-`.cu`; זהו למעשה מה ש-`hipcc` קימפל
<!-- @os:end -->

#### **שלב 3: שימוש מ-Python** ([run_compiled_multiply.py](assets/Matrix_Multiplication/run_compiled_multiply.py)):
הריצו את הסקריפט הזה כדי לראות את הקרנל בפעולה:
```bash
cd Matrix_Multiplication # if not already in directory
python run_compiled_multiply.py
```

**פלט צפוי:**
```
Result: tensor([[19., 22.],
        [43., 50.]])
```

**מעולה! הרגע יישמתם כפל מטריצות על ה-GPU.** זהו אבן דרך משמעותית מכיוון שכפל מטריצות הוא עמוד השדרה של פעולות למידת מכונה מודרניות כמו:
- שכבות רשת עצבית
- מנגנוני קשב (attention)
- הטמעות (embeddings)
- טרנספורמרים

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

## הצעדים הבאים

למדתם לכתוב, לקמפל ולהשיק קרנלי GPU באמצעות קומפילציית JIT והרחבות ++C עבור פעולות מקבילות בסיסיות.

**אופטימיזציות ביצועים:**
- **ריצוף זיכרון משותף (shared memory tiling)** - שמירה במטמון של בלוקי נתונים כדי להפחית גישה לזיכרון גלובלי
- **מיזוג זיכרון (memory coalescing)** - אופטימיזציה של דפוסי גישה לזיכרון עבור רוחב פס

**אלגוריתמים מהעולם האמיתי:**
- **קונבולוציה דו-ממדית (2D Convolution)** - מסנן (קרנל) קטן נע על פני תמונה, ומחשב כל פיקסל פלט מסכום משוקלל של פיקסלים שכנים. זה מציג חישובי stencil וריצוף זיכרון משותף, שבהם threads עושים שימוש חוזר באזורי תמונה חופפים כדי להפחית גישה לזיכרון גלובלי.
- **פונקציית Softmax**: Softmax ממירה וקטור של מספרים להסתברויות שסכומן 1, נפוץ בשימוש בפלטי רשתות עצביות. יישום יעיל שלה על GPU מציג רדוקציות מקבילות וטכניקות יציבות מספרית תוך עיבוד וקטורים גדולים.

**שיקולי ייצור:**
- **טיפול בשגיאות** - בדיקת גבולות וניהול מכשירים
- **אינטגרציה עם PyTorch** - אופרטורים מותאמים אישית עם תמיכת autograd