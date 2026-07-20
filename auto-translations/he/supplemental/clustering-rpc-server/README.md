<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> מדריך זה משתמש בתגים מיוחדים ש-GitHub אינו יכול להציג. יש לבקר בכתובת [amd.com/playbooks](https://amd.com/playbooks) כדי לצפות בתוכן זה כראוי.
<!-- @github-only:end -->

# צביר שני מכשירי Ryzen™ AI Halo באמצעות RPC

## סקירה כללית

מכשיר ה-Ryzen™ AI Halo שברשותך כבר מסוגל להריץ מודלי שפה גדולים באופן מקומי. צביר (Clustering) לוקח זאת צעד קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לך גישה למודלים גדולים אף יותר עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית עמוקה יותר - הכול באופן מלא על החומרה שלך.

מדריך זה ילמד אותך כיצד לצבר שתי מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את GLM 4.7, מודל בעל 358 מיליארד פרמטרים, על פני שתי המכונות עם האצת AMD ROCm™.

## מה תלמדו

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכת ROCm ו-RPC
- הגדרת עובד RPC (RPC worker) והפעלת הסקה מבוזרת בין שני צמתים
- הרצת מודל בעל 358 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: יש להשלים שלב זה הן במכונה 1 והן במכונה 2.

<!-- @os:windows -->
במערכת Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון רב יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (‏iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. יש להגדיר את הערך ל-**96GB**. יש להפעיל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
במערכת Linux, ROCm משתמש במאגר זיכרון משותף של המערכת, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת עמוד ה-Translation Table Manager (TTM) של הליבה, בהתאם להוראות הבאות. AMD ממליצה להגדיר את הכמות המינימלית של VRAM ייעודי ב-BIOS (‏0.5GB).

* התקינו את הכלי pipx והוסיפו את הנתיב עבור חבילות (wheels) המותקנות באמצעות pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את חבילת amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את הכלי amd-ttm כדי לשאול את ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* קבעו מחדש את הגדרות הזיכרון המשותף ל-**120GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעילו מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.


<!-- @os:end -->
<!-- @device:halo_box -->
## בדקו אם קיימים עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מקדימות

### חומרה

מדריך זה דורש שני יחידות Ryzen AI Halo ומתג Ethernet אחד, המחוברים בטופולוגיית כוכב (star topology) כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את הצביר |
| מתג Ethernet 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין מספר צמתי Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שתי יחידות ה-Ryzen AI Halo. יציאה שלישית נדרשת אם ניגשים למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
יש להתקין:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) עם עומס העבודה **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## הגדרת החומרה הפיזית

> **הערה**: יש להשלים שלב זה הן במכונה 1 והן במכונה 2.

חברו כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (ומעלה). פעולה זו יוצרת את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. קביעת ממשקי הרשת

בכל מכונה, אתרו את שם ממשק הרשת שלה ורשמו אותו (אליו נתייחס להלן בתור `IFNAME`). הריצו:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודאו שהקישור פעיל ורץ במהירות מלאה על ידי בדיקת מהירות הממשק שלכם:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: יש להחליף את `<IFNAME>` בשם ממשק הפלט מהשלב [1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אתם אמורים לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים כיבוי של auto-negotiation וקביעת מהירות הקישור ידנית; עיינו בתיעוד המתג שלכם.

<!-- @os:end -->

<!-- @os:windows -->
### אימות מהירות קישור הרשת

בכל מכונה, בדקו את מהירות הקישור של ממשקי הרשת שלכם:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

ממשק ה-Ethernet שלכם אמור להיות `Up` ולרוץ במהירות `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים כיבוי של auto-negotiation וקביעת מהירות הקישור ידנית; עיינו בתיעוד המתג שלכם.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: יש להשלים שלב זה הן במכונה 1 והן במכונה 2.

קיימות שתי אפשרויות התקנה:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, ההתקנה המהירה ביותר
- [אפשרות 2: בנייה ידנית מקוד המקור](#option-2-manual-source-build) - בנייה מקוד המקור עם שליטה מלאה על דגלי הבנייה

### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק בנייה לילית (nightly build) של llama.cpp עם האצת AMD ROCm 7, המיועדת ל-GPU-ים כגון gfx1151 (‏Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות נוספות.

<!-- @os:windows -->
#### שלב 1: הורדת הקבצים הבינאריים המובנים מראש

עברו לדף ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר ה-build).

#### שלב 2: חילוץ הקבצים הבינאריים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת גרסאות build מבוססות ROCm של `llama-cli.exe`,‏ `llama-server.exe` ו-`rpc-server.exe`, שהודרו מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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
#### שלב 1: הורדת הקבצים הבינאריים המובנים מראש

עברו לדף ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר ה-build).

#### שלב 2: חילוץ והכנת הקבצים הבינאריים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת גרסאות build מבוססות ROCm של `llama-cli`,‏ `llama-server` ו-`rpc-server`, שהודרו מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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

### אפשרות 2: בנייה ידנית מקוד המקור

<!-- @os:windows -->
#### שלב 1: בניית llama.cpp

פתחו את **x64 Native Tools Command Prompt** (מותקן יחד עם Visual Studio Build Tools) ושכפלו (clone) את המאגר:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

הוסיפו את HIP לנתיב שלכם ובצעו בנייה עם תמיכה ב-ROCm וב-RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm/HIP |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
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

שלב הבנייה שלעיל הגדיר את `%HIP_PATH%\bin` עבור הפעלה (session) הנוכחית בלבד. כדי להפוך את ספריות HIP לזמינות בכל מסוף (לא רק ב-x64 Native Tools Command Prompt), הוסיפו אותו לנתיב `PATH` של המשתמש שלכם באופן קבוע:

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

בצעו בנייה עם תמיכה ב-ROCm וב-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | מפעיל rocWMMA לשיפור ביצועי Flash Attention במעבדי GPU של AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | מכוון ל-GPU של Ryzen AI Halo‏ (Radeon 8060s) |

למידע נוסף על אפשרויות בנייה, עיינו ב[תיעוד הבנייה של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

מדריך זה משתמש ב-[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), מודל עם 358 מיליארד פרמטרים בקוונטיזציית `Q4_K_XL` מבית [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). בקוונטיזציה זו, המודל דורש כ-205GB של אחסון ומתאים לזיכרון ה-GPU המשולב של שני צמתי Ryzen AI Halo.

הורידו את קובצי ה-GGUF באמצעות ה-CLI של Hugging Face:
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

> **הערה**: הורדת המודל חייבת להתבצע במחשב 1 (הבקר). צמתי ה-RPC worker אינם זקוקים לעותק מקומי של קובצי המודל.

## הפעלת המודל באשכול (Cluster)

מנוע ה-RPC (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות מודל ל-workers מרוחקים דרך הרשת. מחשב אחד משמש כ**בקר** (מחשב 1), ומטפל בטוקניזציה, בתזמון ובתיאום. המחשב השני מריץ **שרת RPC** קליל (מחשב 2) שחושף את זיכרון ה-GPU ואת כוח החישוב שלו לבקר.

בזמן הטעינה, llama.cpp מפצל (shards) את המודל בין שני הצמתים. לאחר הטעינה, ההסקה ממשיכה כאילו היא רצה על מאיץ יחיד. RPC מטפל בהעברות הטנזורים ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרת ה-RPC (מחשב 2)

במחשב 2, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלו לבקר:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| דגל | מטרה |
|------|---------|
| `-p` | הפורט שדרכו משדר שרת ה-RPC |
| `-c` | מפעיל מטמון (cache) מקומי עבור טנזורים גדולים, כדי להימנע מהעברות רשת חוזרות במהלך טעינת המודל |
| `--host` | כתובת ה-IP שאליה נקשר שרת ה-RPC (`0.0.0.0` עבור כל הממשקים) |

למידע נוסף על אפשרויות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מחשב 1)

לאחר שהפעלתם את שרת ה-RPC במחשב 2, הפעילו את ההסקה ממחשב 1 באמצעות `llama-cli` או `llama-server`.

#### llama-cli

`llama-cli` מספק ממשק מבוסס-מסוף לאינטראקציה ישירה עם המודל. הוא אידיאלי לבנצ'מרקינג, לניפוי באגים ולניסויים ברמה נמוכה.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במחשב 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו במסוף (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במחשב 2, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס לפרומפט אינטראקטיבי שבו תוכלו לשוחח ישירות עם המודל:

![llama-cli מריץ את GLM 4.7 על פני שני צמתים](assets/llama-cli-example.png)
#### llama-server

`llama-server` חושף את אותו מנוע היסק דרך תהליך שרת מתמשך עם ממשק משתמש אינטרנטי משולב ו-API מסוג HTTP תואם OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה מרובת משתמשים, ואינטגרציה עם כלים חיצוניים.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במחשב 2, הריצו את `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו ב-Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במחשב 2, הריצו את `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

לאחר ההפעלה, פתחו את `http://<HOST_IP>:8081` בדפדפן שלכם כדי לגשת לממשק המשתמש האינטרנטי המובנה. זה מספק ממשק צ'אט מבוסס-דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server המריץ GLM 4.7 על פני שני צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **מציאת `<HOST_IP>`**: במחשב 1, הריצו את `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **מציאת `<HOST_IP>`**: במחשב 1, הריצו את `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ מודל ה-GGUF (השתמשו במקטע הראשון, `00001-of-00005`) |
| `-c` | גודל ההקשר בטוקנים. ערכים גדולים יותר משתמשים בזיכרון רב יותר |
| `-fa on` | מפעיל rocWMMA Flash Attention לביצועים משופרים במעבדי גרפיקה של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל למעבד הגרפי |
| `--no-mmap` | מבטל מיפוי זיכרון, מה שמקצר את זמני הטעינה כאשר גודל המודל חורג מזיכרון ה-RAM של המערכת אך מתאים ל-VRAM |
| `--host` | כתובת ה-IP לקשירת `llama-server` (`llama-server` בלבד) |
| `--port` | הפורט להגשת ה-API מסוג HTTP (`llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## הצעדים הבאים

- **חיבור יישומי צד שלישי**: `llama-server` חושף API תואם OpenAI. הפנו כל יישום תואם OpenAI (כגון Open WebUI) לכתובת `http://<HOST_IP>:8081` עם מפתח API כלשהו לצורך שמירת מקום (למשל, `none`) כדי להתחבר לאשכול שלכם
- **חקירת מודלים נוספים**: עיינו בקבצי GGUF מכומתים ב[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחבה לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים בסדר גודל של טריליון פרמטרים. העבירו נקודות קצה נוספות ל-`--rpc` כרשימה מופרדת בפסיקים (למשל, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)