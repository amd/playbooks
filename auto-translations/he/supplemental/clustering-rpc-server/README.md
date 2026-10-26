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

# אשכול (Clustering) של שני Ryzen™ AI Halo עם RPC

## סקירה כללית

מערכת Ryzen™ AI Halo שברשותכם כבר מסוגלת להריץ מודלים גדולים של שפה (LLM) באופן מקומי. יצירת אשכול (clustering) לוקחת זאת צעד נוסף קדימה, על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניקה לכם גישה למודלים גדולים אף יותר, עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר והבנה רב-לשונית מעמיקה יותר - הכל לגמרי על החומרה שלכם.

מדריך זה מלמד אתכם כיצד לאשכל (cluster) שתי מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את GLM 4.7, מודל עם 358 מיליארד פרמטרים, על פני שתי המכונות עם האצת AMD ROCm™.

## מה תלמדו

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכה ב-ROCm וב-RPC
- הגדרת worker של RPC והפעלת הסקה מבוזרת על פני שני צמתים
- הרצת מודל עם 358 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: השלימו שלב זה הן על מכונה 1 והן על מכונה 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **הרצת מודלים קרוב ל-128GB ומעלה:** במערכות AMD Ryzen™ AI Max 400 Series‏ (Gorgon Halo) המריצות Windows, מודלים המתקרבים ל-128GB זיכרון או חורגים ממנו דורשים תצורה נוספת כדי לפעול ללא שגיאות. עקבו אחר [הנחיות מערכת ההפעלה Windows עבור AMD Ryzen AI Max PRO 400 Series](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) לפני טעינת המודל.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
ב-Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון גבוה יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory‏ (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדירו את הערך ל-**96GB**. אתחלו מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת העמודים של Translation Table Manager‏ (TTM) של הקרנל (kernel), לפי ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5GB).

* התקינו את כלי השירות pipx והוסיפו את הנתיב עבור wheels המותקנים על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את הכלי amd-ttm כדי לשאול על ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדירו מחדש את הגדרות הזיכרון המשותף ל-**120GB**:
  ```bash
  amd-ttm --set 120
  ```

* אתחלו מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.


<!-- @os:end -->
<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מקדימות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב (star) כאשר כל יחידה מחווטת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet בנפח 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין מספר צמתי Ryzen AI Halo (לפחות 2 פתחים) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשים שני פתחי מתג Ethernet כדי לחבר את שתי יחידות Ryzen AI Halo. נדרש פתח שלישי אם אתם ניגשים למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
יש להתקין:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) עם חבילת העבודה **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: השלימו שלב זה הן על מכונה 1 והן על מכונה 2.

חברו כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (ומעלה). פעולה זו מבססת את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. קביעת ממשקי הרשת

בכל מכונה, מצאו את שם ממשק הרשת שלה ורשמו אותו (אליו נתייחס להלן בשם `IFNAME`). הריצו:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

זה מדפיס את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודאו שהקישור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלכם:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החליפו את `<IFNAME>` בשם ממשק הפלט מתוך [1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אמורה להופיע מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שפתח המתג מוגדר ל-10Gbps. חלק מהמתגים דורשים השבתה של משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור ידנית; עיינו בתיעוד של המתג שלכם.

<!-- @os:end -->

<!-- @os:windows -->
### אימות מהירות קישור הרשת

בכל מכונה, בדקו את מהירות הקישור של ממשקי הרשת שלכם:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

ממשק ה-Ethernet שלכם אמור להיות `Up` ופועל במהירות `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שפתח המתג מוגדר ל-10Gbps. חלק מהמתגים דורשים השבתה של משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור ידנית; עיינו בתיעוד של המתג שלכם.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: השלימו שלב זה הן על מכונה 1 והן על מכונה 2.

קיימות שתי אפשרויות התקנה:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, ההתקנה המהירה ביותר
- [אפשרות 2: בנייה ידנית מהקוד המקור](#option-2-manual-source-build) - בנייה מהקוד המקור עם שליטה מלאה על דגלי הבנייה (build flags)
### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק בילדים לילי (nightly builds) של llama.cpp עם האצת AMD ROCm 7, המיועדים ל-GPU כמו gfx1151‏ (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות נוספות.

<!-- @os:windows -->
#### שלב 1: הורדת הבינארים המובנים מראש

נווטו לעמוד ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה ולמטרת ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבילד).

#### שלב 2: חילוץ הבינארים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת בילדים התומכים ב-ROCm של `llama-cli.exe`,‏ `llama-server.exe` ו-`rpc-server.exe`, מהודרים מראש עבור מערכת ה-Ryzen AI Halo שלכם.

#### שלב 3: אימות זיהוי ה-GPU

```bash
.\llama-cli.exe --list-devices
```

פלט צפוי:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### שלב 1: הורדת הבינארים המובנים מראש

נווטו לעמוד ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה ולמטרת ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבילד).

#### שלב 2: חילוץ והכנת הבינארים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת בילדים התומכים ב-ROCm של `llama-cli`,‏ `llama-server` ו-`rpc-server`, מהודרים מראש עבור מערכת ה-Ryzen AI Halo שלכם.

#### שלב 3: אימות זיהוי ה-GPU

```bash
./llama-cli --list-devices
```

פלט צפוי:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
לאחר הכנת llama.cpp בכל צומת, המשיכו אל [הורדת המודל](#downloading-the-model).

### אפשרות 2: בנייה ידנית מהקוד המקור

<!-- @os:windows -->
#### שלב 1: בניית llama.cpp

פתחו את **x64 Native Tools Command Prompt** (המותקן יחד עם Visual Studio Build Tools) ושכפלו (clone) את המאגר:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

הוסיפו את HIP לנתיב (path) ובנו עם תמיכה ב-ROCm וב-RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm/HIP |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת (distributed inference) |
| `-DGPU_TARGETS=gfx1151` | מכוון ל-GPU של Ryzen AI Halo‏ (Radeon 8060s) |
| `-G Ninja` | משתמש במערכת הבנייה Ninja |

#### שלב 2: אימות זיהוי ה-GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

פלט צפוי:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### שלב 3: הוספת HIP לנתיב המשתמש שלכם

שלב הבנייה שלעיל הגדיר את `%HIP_PATH%\bin` עבור ההפעלה הנוכחית בלבד. כדי להפוך את ספריות HIP לזמינות בכל מסוף (terminal), ולא רק ב-x64 Native Tools Command Prompt, הוסיפו אותו באופן קבוע ל-`PATH` של המשתמש שלכם:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

לאחר הכנת llama.cpp בכל צומת, המשיכו אל [הורדת המודל](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### שלב 1: בניית llama.cpp

שכפלו (clone) את המאגר:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

בנו עם תמיכה ב-ROCm וב-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת (distributed inference) |
| `-DAMDGPU_TARGETS="gfx1151"` | מכוון ל-GPU של Ryzen AI Halo‏ (Radeon 8060s) |

לאפשרויות בנייה נוספות, עיינו ב[תיעוד הבנייה של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### שלב 2: אימות זיהוי ה-GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

פלט צפוי:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

לאחר הכנת llama.cpp בכל צומת, המשיכו אל [הורדת המודל](#downloading-the-model).
<!-- @os:end -->

## הורדת המודל

מדריך זה משתמש ב-[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), מודל בן 358 מיליארד פרמטרים בכימות (quantization) מסוג `Q4_K_XL` מבית [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). בכימות זה המודל דורש כ-205GB אחסון ומתאים לזיכרון ה-GPU המשולב של שני צמתי Ryzen AI Halo.

הורידו את קבצי ה-GGUF באמצעות ה-CLI של Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **הערה**: הורדת המודל חייבת להתבצע במחשב 1 (הבקר - controller). צמתי ה-RPC Worker אינם זקוקים לעותק מקומי של קובצי המודל.

## הפעלת המודל על האשכול (Cluster)

מנוע ה-RPC‏ (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות מודל (offload) לעובדים מרוחקים דרך הרשת. מחשב אחד פועל בתור **הבקר (controller)** (מחשב 1), ומטפל בטוקניזציה, בתזמון ובתיאום. המחשב השני מריץ **שרת RPC** קל משקל (מחשב 2) שחושף את זיכרון ה-GPU שלו ואת כוח העיבוד שלו לבקר.

בזמן הטעינה, llama.cpp מחלק את המודל בין שני הצמתים (sharding). לאחר הטעינה, ההסקה (inference) ממשיכה כאילו היא רצה על מאיץ יחיד. RPC מטפל בהעברות הטנסורים (tensor) ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרת ה-RPC (מחשב 2)

במחשב 2, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלו לבקר:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| דגל | מטרה |
|------|---------|
| `-p` | הפורט שבו ישודר שרת ה-RPC |
| `-c` | מפעיל מטמון (cache) מקומי לטנסורים גדולים, ומונע העברות רשת חוזרות במהלך טעינת המודל |
| `--host` | כתובת ה-IP שאליה יתחבר שרת ה-RPC (`0.0.0.0` עבור כל הממשקים) |

לאפשרויות נוספות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מחשב 1)

כאשר שרת ה-RPC פועל במחשב 2, הפעילו את ההסקה (inference) ממחשב 1 באמצעות `llama-cli` או `llama-server`.
#### llama-cli

`llama-cli` מספק ממשק מבוסס מסוף לאינטראקציה ישירה עם המודל. זהו ממשק אידיאלי להשוואת ביצועים (benchmarking), ניפוי שגיאות וניסויים ברמה נמוכה.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **איתור `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו ב-Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **איתור `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס לשורת פקודה אינטראקטיבית שבה ניתן לשוחח ישירות עם המודל:

![llama-cli מריץ GLM 4.7 על פני שני צמתים](assets/llama-cli-example.png)

#### llama-server

`llama-server` חושף את אותו מנוע היסק דרך תהליך שרת מתמשך עם ממשק משתמש אינטרנטי משולב וממשק API מבוסס HTTP התואם ל-OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה מרובת-משתמשים, ושילוב עם כלים חיצוניים.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **איתור `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו ב-Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **איתור `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

לאחר ההפעלה, פתחו את `http://<HOST_IP>:8081` בדפדפן שלכם כדי לגשת לממשק המשתמש האינטרנטי המובנה. זהו ממשק צ'אט מבוסס דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server מריץ GLM 4.7 על פני שני צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **איתור `<HOST_IP>`**: על מכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **איתור `<HOST_IP>`**: על מכונה 1, הריצו `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ המודל מסוג GGUF (יש להשתמש במקטע הראשון, `00001-of-00005`) |
| `-c` | גודל ההקשר (context) בטוקנים. ערכים גדולים יותר משתמשים בזיכרון רב יותר |
| `-fa on` | מאפשר rocWMMA Flash Attention לשיפור ביצועים ב-GPU של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל ל-GPU |
| `-lm none` | מגדיר את מצב טעינת המודל ל-`none`, ומשבית מיפוי זיכרון כדי לקצר זמני טעינה כאשר גודל המודל עולה על זיכרון ה-RAM של המערכת אך מתאים לזיכרון ה-VRAM |
| `--host` | כתובת ה-IP שאליה יקושר `llama-server` (עבור `llama-server` בלבד) |
| `--port` | הפורט שבו יוגש ה-API של HTTP (עבור `llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה (endpoints) של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## שלבים הבאים

- **חיבור יישומי צד שלישי**: `llama-server` חושף API התואם ל-OpenAI. כוונו כל יישום התואם ל-OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם מפתח API כלשהו כתחליף-מקום (לדוגמה, `none`) כדי להתחבר לאשכול שלכם
- **חקרו מודלים נוספים**: עיינו במודלי GGUF מכומתים (quantized) ב-[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים שמתאימים לסך זיכרון ה-GPU המשולב של האשכול שלכם
- **הרחיבו לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים בסדר גודל של טריליון פרמטרים. העבירו נקודות קצה נוספות אל `--rpc` כרשימה מופרדת בפסיקים (לדוגמה, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)