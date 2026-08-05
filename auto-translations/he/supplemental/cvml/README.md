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

[ספריית Ryzen AI CVML](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) היא ערכת כלים של AMD ב-++C לראייה ממוחשבת ולמידת מכונה, המספקת יכולות תפיסה עוצמתיות במכשיר עצמו — כולל הערכת עומק, זיהוי פנים, ומעקב אחר רשת פנים (face mesh). הספרייה בנויה מעל מנהלי ההתקן של Ryzen AI, ובוחרת אוטומטית בחומרה הטובה ביותר הזמינה (GPU או NPU) להסקה (inference), ומאפשרת לכם להוסיף יכולות בינה מלאכותית לאפליקציות ++C מבלי לדאוג לאימון מודלים או לשילוב עם מסגרות עבודה (frameworks). כל העיבוד מתבצע באופן מקומי על המערכת שלכם, מה שהופך אותה לאידיאלית עבור אפליקציות רגישות לפרטיות ובעלות זמן השהיה נמוך.

מדריך זה ילמד אתכם כיצד להגדיר את ספריית Ryzen AI CVML, לבנות את אפליקציות הדוגמה הכלולות בה, ולהריץ זיהוי פנים על תמונת דוגמה.

## מה תלמדו

- כיצד להתקין דרישות קדם ולהגדיר את ספריית Ryzen AI CVML על המערכת שלכם
- כיצד עובד ה-API של CVML ב-++C: הקשרים (contexts), אובייקטי תכונה (feature objects), ומאגרי תמונות (image buffers)
- כיצד לבנות ולהריץ את אפליקציות הדוגמה הכלולות באמצעות CMake ו-OpenCV
- כיצד להריץ זיהוי פנים על תמונה עם תיבות תוחמות (bounding boxes) וציוני דרך (landmarks)
- כיצד לשלב תכונות CVML באפליקציות ++C משלכם

<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->

## התקנת דרישות תוכנה מוקדמות
<!-- @require:driver -->

## תלויות נוספות

לפני שתתחילו, ודאו שיש לכם את הדברים הבאים:

<!-- @os:windows -->
- [OpenCV 4.11](https://github.com/opencv/opencv/releases/tag/4.11.0) — הורידו את `opencv-4.11.0-windows.exe`, הריצו אותו, וחלצו לתיקייה מקומית (למשל `C:\opencv`)
- [CMake](https://cmake.org/download/) — הורידו את מתקין ה-MSI עבור Windows x86-64, ובמהלך ההתקנה בחרו ב-**"Add CMake to the system PATH for all users"**
- [מנהל התקן Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/inst.html) — התקינו את הגרסה העדכנית ביותר הזמינה
- [Visual Studio 2022 Community](https://aka.ms/vs/17/release/vs_community.exe) עם עומס העבודה "Desktop development with C++" (כולל מהדר MSVC, Windows SDK, וכלי בנייה ל-++C)
<!-- @os:end -->

<!-- @os:linux -->
- OpenCV 4.11 — יש לבנות מהמקור (חבילות apt ב-Ubuntu 22.04 ו-24.04 אינן מספקות גרסה 4.11). ראו [בניית OpenCV מהמקור](#building-opencv-from-source) בהמשך.
- CMake — התקינו באמצעות apt:
  ```bash
  sudo apt install cmake
  ```
- Ubuntu 22.04 או 24.04 (kernel >= 6.11.0-21-generic)
- [מנהל התקן Ryzen AI NPU](https://ryzenai.docs.amd.com/en/latest/linux.html#install-npu-drivers) (מתקין עבור Linux — נדרש להסקת NPU)
- Vulkan SDK (מותקן בקטע [Vulkan SDK](#vulkan-sdk) בהמשך)
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

## הגדרת ספריית CVML

צרו חשבון AMD בכתובת [account.amd.com](https://account.amd.com) אם אין לכם עדיין, ולאחר מכן היכנסו כדי להוריד את ספריית Ryzen AI CVML מקישור הפורטל שלהלן:

```
https://account.amd.com/en/forms/downloads/xef.html?filename=72293_Ryzen_AI_Library_26.05.20.zip
```

לאחר ההורדה, חלצו את החבילה לתיקייה מקומית (למשל, `C:\RyzenAI-Library` ב-Windows או `~/RyzenAI-Library` ב-Linux) והגדירו את משתנה הסביבה `AMD_CVML_SDK_ROOT` למיקום שאליו חילצתם:

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

חבילת הספרייה מכילה את המבנה הבא:

| תיקייה | תוכן |
|--------|----------|
| `cmake/` | מידע אריזה עבור פונקציית `find_package` של CMake |
| `include/` | קובצי כותרת (header files) ב-++C (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, וכו') |
| `windows/` | קבצים בינאריים עבור Windows (קבצי `.LIB` בזמן קומפילציה ו-`.DLL`/`.GRAPHLIB`/`.AMODEL` בזמן ריצה) |
| `linux/` | קבצים בינאריים עבור Linux (קבצי `.SO` לקומפילציה ולזמן ריצה) |
| `samples/` | אפליקציות דוגמה נפרדות עם קוד מקור |

<!-- @os:linux -->

### הגדרה ייעודית ל-Linux

#### בניית OpenCV מהמקור

התקינו את תלויות הבנייה של OpenCV:

```bash
sudo apt install unzip wget ubuntu-restricted-extras libunwind-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libgtk-3-dev pkg-config ffmpeg
```

הורידו, הגדירו ובנו את OpenCV 4.11.0 עם מודולי contrib (מקור: [מדריך התקנת OpenCV עבור Linux](https://docs.opencv.org/4.11.0/d7/d9f/tutorial_linux_install.html#tutorial_linux_install_quick_build_contrib)):

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

ספריות משותפות (shared libraries) מותקנות תחת `<build>/install/lib/`. השתמשו בתיקיית `install` בתור `OPENCV_INSTALL_ROOT` בשלבים הבאים.

#### Vulkan SDK

התקינו את Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

אם אתם מריצים Ubuntu 22.04, עדכנו גם את מנהלי ההתקן MESA Vulkan:

```bash
sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update
sudo apt upgrade
```

#### תלויות נוספות עבור Ubuntu 24.04

אם אתם מריצים Ubuntu 24.04, התקינו חבילות נוספות נדרשות:

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

## מושגי יסוד

ספריית CVML מספקת API פשוט ב-++C שבו לכל תכונת תפיסה (הערכת עומק, זיהוי פנים, רשת פנים) יש קובץ כותרת ואובייקט תכונה משלה. אין צורך לעבוד עם מודלים גולמיים — הספרייה מטפלת בטעינת מודלים, בעיבוד מקדים, ובהסקה באופן אוטומטי.

### תכונות זמינות

| תכונה | קובץ כותרת | תיאור |
|---------|------------|-------------|
| **הערכת עומק** | `cvml-depth-estimation.h` | יוצר מפות עומק לכל פיקסל מתמונות RGB |
| **זיהוי פנים** | `cvml-face-detector.h` | מזהה פנים עם תיבות תוחמות, ציוני דרך (עיניים, אף, פה), וציוני ביטחון |
| **רשת פנים** | `cvml-face-mesh.h` | עוקב אחר גיאומטריית פנים מפורטת עם נקודות רשת צפופות |

### מודל תכנות

כל אפליקציית CVML פועלת לפי אותו תבנית בת ארבעה שלבים:

1. **יצירת הקשר (Context)** — ה-`amd::cvml::Context` מנהל משאבים משותפים כמו רישום (logging) ובחירת מנוע הסקה (inference backend).
2. **יצירת אובייקט תכונה** — יצירת מופע של התכונה הספציפית (למשל, `amd::cvml::DepthEstimation`) כנגד ההקשר.
3. **עטיפת נתוני קלט** — השתמשו ב-`amd::cvml::Image` כדי לעטוף את מאגר תמונת ה-RGB שלכם ללא העתקת נתונים.
4. **ביצוע** — קראו לשיטת העיבוד של התכונה וקראו את התוצאות.

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

### Backend היסק

הספרייה בוחרת אוטומטית את החומרה הטובה ביותר (GPU או NPU) עבור כל פעולה. ניתן גם להגדיר את ה-backend באופן מפורש:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **הערה:** תכונות המשתמשות ב-backend של ONNX עבור פעולות NPU עשויות לחוות זמן אחזור (latency) ארוך יותר בעת ההפעלה הראשונה. הפעלות עוקבות יהיו מהירות יותר.

> **הערה:** אם מנהל ההתקן (driver) של ה-NPU אינו מותקן על המערכת היעד, ספריית Ryzen AI CVML תחזור אוטומטית לשימוש ב-backend של ה-GPU עבור פעולות ההיסק.

## בניית אפליקציות הדוגמה

ספריית CVML כוללת אפליקציות דוגמה מוכנות לבנייה עבור כל תכונה. בואו נבנה את כולן בבת אחת.

1. הגדירו את משתנה הסביבה `OPENCV_INSTALL_ROOT` כך שיצביע על התקנת OpenCV שלכם:

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

2. בנו את הדוגמאות באמצעות CMake:

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

   לאחר בנייה מוצלחת, קובצי ההרצה (executables) ממוקמים ב:

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

3. לפני הרצת כל דוגמה, ודאו שקבצי זמן הריצה (runtime) של CVML נגישים:

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

## הרצת זיהוי פנים

דוגמת זיהוי הפנים מזהה פנים בתמונה, בווידאו, או בהזנת מצלמה חיה (live camera feed). היא מציירת תיבות תוחמות (bounding boxes), ציוני ביטחון (confidence scores), וחמישה ציוני דרך (landmarks) של הפנים (שתי עיניים, אף, ושני קצוות פה) על כל פנים שזוהו.

תחילה, נווטו לתיקיית קובץ ההרצה של זיהוי הפנים:

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

לאחר מכן הורידו תמונת דוגמה לשימוש כקלט (צילום מאת [Jopwell](https://www.pexels.com/photo/man-in-gray-crew-neck-shirt-smiling-on-focus-photo-895863/), חופשי לשימוש דרך Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/895863/pexels-photo-895863.jpeg?cs=srgb&dl=pexels-jopwell-895863.jpg&fm=jpg"
```

**הריצו זיהוי פנים על תמונת הדוגמה:**

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

יופיע חלון שמציג את התמונה עם תיבות תוחמות סביב הפנים שזוהו, ציוני ביטחון, ונקודות ציון פנים (עיניים, אף, קצוות פה).

<p align="center">
  <img src="assets/human_face_output.png" alt="Face detection output showing bounding box, confidence score, and facial landmarks" width="600"/>
</p>

**שמרו את הפלט המסומן (annotated) לקובץ:**

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

**השתמשו במודל המדויק (precise)** לדיוק גבוה יותר (על חשבון המהירות):

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

תכונת זיהוי הפנים מציעה שני וריאנטים של מודל:

| מודל | מהירות | דיוק | מתאים ביותר עבור |
|-------|-------|----------|----------|
| `fast` (ברירת מחדל) | FPS גבוה יותר | טוב | אפליקציות מצלמה בזמן אמת |
| `precise` | FPS נמוך יותר | הטוב ביותר | ניתוח תמונות, צרכי דיוק גבוה |


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

## שילוב CVML באפליקציה שלכם

כדי להשתמש בספריית CVML בפרויקט C++ שלכם, הוסיפו אותה באמצעות `find_package` של CMake:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

כאשר `AMD_CVML_SDK_ROOT` מצביע על השורש של תיקיית ספריית Ryzen AI CVML. לאחר מכן כללו את הכותרת המתאימה עבור התכונה שברצונכם להשתמש בה:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## הצעדים הבאים

עבור כל דוגמה למטה, נווטו תחילה לתיקיית ההרצה שלה, לפי אותו דפוס שהוצג בסעיף [Running Face Detection](#running-face-detection) למעלה (למשל `cd build\cvml-sample-depth-estimation\Release` ב-Windows או `cd build/cvml-sample-depth-estimation` ב-Linux). ב-Windows, הוסיפו `.exe` לכל פקודה (למשל `cvml-sample-depth-estimation.exe`).

- **נסו הערכת עומק (Depth Estimation)**: הריצו `cvml-sample-depth-estimation -i sample_face.jpg` כדי ליצור מפת עומק צבעונית — עצמים קרובים יותר יופיעו בצבעים חמים, ורחוקים יותר בצבעים קרים
- **גלו רשת פנים (Face Mesh)**: הריצו `cvml-sample-face-mesh -i sample_face.jpg` כדי לראות מעקב גיאומטרי צפוף אחר הפנים עם נקודות רשת מפורטות
- **עבדו על קובצי וידאו**: השתמשו בדגלים `-i` ו-`-o` בכל דוגמה כדי לעבד קובצי וידאו (למשל, `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **השוו בין וריאנטים של מודלים**: נסו `-m precise` לעומת ברירת המחדל `-m fast` בזיהוי פנים כדי לראות במו עיניכם את הפשרה בין דיוק למהירות
- **בנו אפליקציה משלכם**: השתמשו באינטגרציית CMake וב-API של C++ כדי להוסיף יכולות CVML לאפליקציות C++ משלכם
- **שלבו יכולות**: חברו זיהוי פנים עם הערכת עומק באותה אפליקציה להבנת סצנה עשירה יותר
- **עיינו בקוד המקור**: קראו את [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) לתיעוד הכותרות, דוגמאות נוספות ופרטי API