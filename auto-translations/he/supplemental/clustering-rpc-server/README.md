<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# אשכול שני מערכות Ryzen™ AI Halo עם RPC

## סקירה כללית

ה-Ryzen™ AI Halo שלך כבר מסוגל להריץ מודלים של שפה גדולים באופן מקומי. אשכול מרחיב יכולת זו על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לך גישה למודלים גדולים עוד יותר עם יכולת הסקה חזקה יותר, יצירת קוד משופרת והבנה רב-לשונית עמוקה יותר — הכל על החומרה שלך בלבד.

מדריך זה מלמד אותך כיצד לאשכל שתי מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את GLM 4.7, מודל עם 358 מיליארד פרמטרים, על פני שתי המכונות עם האצת AMD ROCm™.

## מה תלמד

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכה ב-ROCm וב-RPC
- הגדרת עובד RPC והפעלת הסקה מבוזרת על פני שני צמתים
- הרצת מודל עם 358 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: השלם שלב זה הן במכונה 1 והן במכונה 2.

<!-- @os:windows -->
ב-Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון גבוה יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה של AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדר את הערך ל-**96 GB**. אנא הפעל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת דף Translation Table Manager (TTM) של הקרנל, בהתאם להוראות הבאות. AMD ממליצה להגדיר את ה-VRAM הייעודי המינימלי ב-BIOS (0.5 GB).

* התקן את כלי השירות pipx והוסף את הנתיב עבור גלגלי pipx המותקנים לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקן את גלגל amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הרץ את כלי amd-ttm לשאילתת ההגדרות הנוכחיות של הזיכרון המשותף.
  ```bash
  amd-ttm
  ```

* הגדר מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.


<!-- @os:end -->
<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מוקדמות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet בעל 10Gbps | 1 | מתג מרכזי לאפשר תקשורת בין צמתי Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet לחיבור שתי יחידות Ryzen AI Halo. יציאה שלישית נדרשת אם אתה ניגש למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
אנא התקן:
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

> **הערה**: השלם שלב זה הן במכונה 1 והן במכונה 2.

חבר כל יחידת Ryzen AI Halo למתג Ethernet באמצעות כבל Cat 7 (ומעלה). פעולה זו מבססת את קישור ה-10Gbps המשמש לתקשורת במהירות גבוהה בין הצמתים.
<!-- @os:linux -->
### 1. זיהוי ממשקי הרשת

בכל מכונה, מצא את שם ממשק הרשת שלה ורשום אותו (הוא יכונה להלן `IFNAME`). הרץ:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

אשר שהקישור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף את `<IFNAME>` בשם הממשק שהתקבל מ-[1. זיהוי ממשקי הרשת](#1-determine-network-interfaces)

אמור לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדוק את חיבור הכבל ואשר שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתת ניהול אוטומטי והגדרה ידנית של מהירות הקישור; עיין בתיעוד המתג שלך.

<!-- @os:end -->

<!-- @os:windows -->
### אימות מהירות קישור הרשת

בכל מכונה, בדוק את מהירות הקישור של ממשקי הרשת שלך:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

ממשק ה-Ethernet שלך אמור להיות `Up` ולפעול במהירות `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדוק את חיבור הכבל ואשר שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתת ניהול אוטומטי והגדרה ידנית של מהירות הקישור; עיין בתיעוד המתג שלך.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: השלם שלב זה הן במכונה 1 והן במכונה 2.

שתי אפשרויות התקנה זמינות:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים מוכנים מראש, הגדרה מהירה ביותר
- [אפשרות 2: בנייה ידנית מקוד מקור](#option-2-manual-source-build) - בנייה מקוד מקור עם שליטה מלאה על דגלי הבנייה

### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק גרסאות לילה של llama.cpp עם האצת AMD ROCm 7, המכוונות ל-GPU כגון gfx1151 (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות אחרות.

<!-- @os:windows -->
#### שלב 1: הורדת הקבצים הבינאריים המוכנים מראש

נווט לדף הגרסה האחרונה והורד את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלך:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורד את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ הקבצים הבינאריים

פתח את הארכיון שהורדת:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

ספרייה זו מכילה כעת גרסאות מוכנות ל-ROCm של `llama-cli.exe`, `llama-server.exe` ו-`rpc-server.exe`, מקומפלות מראש עבור מערכת Ryzen AI Halo שלך.

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
#### שלב 1: הורדת הקבצים הבינאריים המוכנים מראש

נווט לדף הגרסה האחרונה והורד את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלך:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורד את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ והכנת הקבצים הבינאריים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

ספרייה זו מכילה כעת גרסאות מוכנות ל-ROCm של `llama-cli`, `llama-server` ו-`rpc-server`, מקומפלות מראש עבור מערכת Ryzen AI Halo שלך.

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
לאחר הכנת llama.cpp בכל צומת, המשך אל [הורדת המודל](#downloading-the-model).

### אפשרות 2: בנייה ידנית מקוד מקור

<!-- @os:windows -->
#### שלב 1: בנייה של llama.cpp

פתח את **x64 Native Tools Command Prompt** (המותקן עם Visual Studio Build Tools) ושכפל את המאגר:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

הוסף את HIP לנתיב שלך ובנה עם תמיכה ב-ROCm וב-RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm/HIP |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DGPU_TARGETS=gfx1151` | מכוון ל-GPU של Ryzen AI Halo (Radeon 8060s) |
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

#### שלב 3: הוספת HIP לנתיב המשתמש שלך

שלב הבנייה לעיל הגדיר את `%HIP_PATH%\bin` לסשן הנוכחי בלבד. כדי להפוך את ספריות HIP לזמינות בכל טרמינל (לא רק ב-x64 Native Tools Command Prompt), הוסף אותן ל-`PATH` של המשתמש שלך באופן קבוע:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

לאחר הכנת llama.cpp בכל צומת, המשך אל [הורדת המודל](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### שלב 1: בנייה של llama.cpp

שכפל את המאגר:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

בנה עם תמיכה ב-ROCm וב-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | מפעיל rocWMMA לשיפור Flash Attention על GPU של AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | מכוון ל-GPU של Ryzen AI Halo (Radeon 8060s) |

לאפשרויות בנייה נוספות, עיין ב-[תיעוד הבנייה של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

לאחר הכנת llama.cpp בכל צומת, המשך אל [הורדת המודל](#downloading-the-model).
<!-- @os:end -->

## הורדת המודל

מדריך זה משתמש ב-[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), מודל עם 358 מיליארד פרמטרים בכימות `Q4_K_XL` מ-[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). בכימות זה המודל דורש כ-205GB אחסון ומתאים לזיכרון ה-GPU המשולב של שני צמתי Ryzen AI Halo.

הורד את קבצי ה-GGUF באמצעות Hugging Face CLI:
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

> **הערה**: הורדת המודל חייבת להתבצע במכונה 1 (הבקר). צמתי עובד ה-RPC אינם זקוקים לעותק מקומי של קבצי המודל.

## הפעלת המודל על האשכול

מנוע ה-RPC (Remote Procedure Call) של llama.cpp מאפשר למופע llama.cpp יחיד להעביר שכבות מודל לעובדים מרוחקים דרך הרשת. מכונה אחת משמשת כ**בקר** (מכונה 1), המטפלת בטוקניזציה, תזמון ותיאום. המכונה האחרת מריצה **שרת RPC** קל משקל (מכונה 2) שחושף את זיכרון ה-GPU ויכולת החישוב שלה לבקר.

בזמן הטעינה, llama.cpp מפצל את המודל על פני שני הצמתים. לאחר הטעינה, ההסקה מתבצעת כאילו היא רצה על מאיץ יחיד. RPC מטפל בהעברות הטנסורים ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרת ה-RPC (מכונה 2)

במכונה 2, הפעל את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלה לבקר:
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
| `-p` | יציאה לשידור שרת ה-RPC עליה |
| `-c` | מפעיל מטמון מקומי לטנסורים גדולים, ומונע העברות רשת חוזרות בזמן טעינת המודל |
| `--host` | כתובת IP לקשירת שרת ה-RPC אליה (`0.0.0.0` לכל הממשקים) |

לאפשרויות נוספות, עיין ב-[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מכונה 1)

כאשר שרת ה-RPC פועל במכונה 2, הפעל הסקה ממכונה 1 באמצעות `llama-cli` או `llama-server`.

#### llama-cli

`llama-cli` מספק ממשק מבוסס טרמינל לאינטראקציה ישירה עם המודל. הוא אידיאלי לבנצ'מרקינג, ניפוי שגיאות וניסויים ברמה נמוכה.

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

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הרץ פקודה זו ב-Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס לפרומפט אינטראקטיבי שבו ניתן לשוחח ישירות עם המודל:

![llama-cli מריץ GLM 4.7 על פני שני צמתים](assets/llama-cli-example.png)

#### llama-server

`llama-server` חושף את אותו מנוע הסקה דרך תהליך שרת מתמשך עם ממשק משתמש אינטגרטיבי מבוסס אינטרנט ו-API HTTP תואם OpenAI. זהו הממשק המועדף לפריסות ממושכות, גישה מרובת משתמשים ואינטגרציה עם כלים חיצוניים.

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

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הרץ פקודה זו ב-Terminal (Powershell).

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

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

לאחר ההפעלה, פתח את `http://<HOST_IP>:8081` בדפדפן שלך כדי לגשת לממשק המשתמש המובנה מבוסס האינטרנט. ממשק זה מספק ממשק צ'אט מבוסס דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server מריץ GLM 4.7 על פני שני צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **מציאת `<HOST_IP>`**: במכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **מציאת `<HOST_IP>`**: במכונה 1, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

#### עזר לפרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ מודל ה-GGUF (השתמש בשבר הראשון, `00001-of-00005`) |
| `-c` | גודל הקשר בטוקנים. ערכים גדולים יותר משתמשים ביותר זיכרון |
| `-fa on` | מפעיל rocWMMA Flash Attention לשיפור ביצועים על GPU של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל ל-GPU |
| `--no-mmap` | משבית מיפוי זיכרון, מקצר זמני טעינה כאשר גודל המודל עולה על ה-RAM של המערכת אך מתאים ל-VRAM |
| `--host` | IP לקשירת `llama-server` אליו (ל-`llama-server` בלבד) |
| `--port` | יציאה להגשת ה-API HTTP עליה (ל-`llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובד RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיין ב-[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב-[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## השלבים הבאים

- **חיבור יישומים של צד שלישי**: `llama-server` חושף API תואם OpenAI. הפנה כל יישום תואם OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם כל מפתח API כ-placeholder (למשל, `none`) כדי להתחבר לאשכול שלך
- **חקור מודלים אחרים**: עיין ב-GGUF מכומתים ב-[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים המתאימים לזיכרון ה-GPU המשולב של האשכול שלך
- **הרחב לארבעה צמתים**: הוסף שתי מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים בסדר גודל של טריליון פרמטרים. העבר נקודות קצה נוספות ל-`--rpc` כרשימה מופרדת בפסיקים (למשל, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)