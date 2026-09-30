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

# אשכול (Clustering) של שני Ryzen™ AI Halo באמצעות RPC

## סקירה כללית

מערכת ה-Ryzen™ AI Halo שברשותך כבר מסוגלת להריץ מודלי שפה גדולים באופן מקומי. יצירת אשכול (clustering) לוקחת זאת צעד קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, מה שמעניק לך גישה למודלים גדולים עוד יותר עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית מעמיקה יותר, הכול על החומרה שלך בלבד.

מדריך זה מלמד אותך כיצד ליצור אשכול של שתי מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את GLM 4.7, מודל עם 358 מיליארד פרמטרים, על פני שתי המכונות עם האצת AMD ROCm™.

## מה תלמד/י

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכה ב-ROCm וב-RPC
- הגדרת worker של RPC והפעלת הסקה מבוזרת על פני שני צמתים
- הרצת מודל עם 358 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: יש לבצע שלב זה גם במכונה 1 וגם במכונה 2.

<!-- @os:windows -->
ב-Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון גבוה יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדר/י את הערך ל-**96 GB**. יש להפעיל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, ROCm משתמשת במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת עמוד ה-Translation Table Manager (TTM) של הקרנל, בעזרת ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5 GB).

* התקן/י את הכלי pipx והוסף/י את הנתיב עבור wheels המותקנים על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקן/י את ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הרץ/הריצי את הכלי amd-ttm כדי לשאול את ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדר/י מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעל/הפעילי מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.


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
| מתג Ethernet בקצב 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין מספר צמתי Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שתי יחידות ה-Ryzen AI Halo. נדרשת יציאה שלישית אם ניגשים למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
יש להתקין:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) עם עומס העבודה **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: יש לבצע שלב זה גם במכונה 1 וגם במכונה 2.

חבר/י כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו מקימה את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. זיהוי ממשקי הרשת

בכל מכונה, מצא/י את שם ממשק הרשת שלה ורשום/רשמי אותו (הוא ייקרא להלן `IFNAME`). הרץ/הריצי:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פעולה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודא/ודאי שהקישור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף/החליפי את `<IFNAME>` בשם ממשק הפלט מתוך [1. זיהוי ממשקי הרשת](#1-determine-network-interfaces)

אמור/אמורה להופיע מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדוק/י את חיבור הכבל וודא/י שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים כיבוי משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור באופן ידני; עיין/י בתיעוד המתג שלך.

<!-- @os:end -->

<!-- @os:windows -->
### אימות מהירות קישור הרשת

בכל מכונה, בדוק/י את מהירות הקישור של ממשקי הרשת שלך:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

ממשק ה-Ethernet שלך אמור להיות `Up` ולפעול במהירות `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדוק/י את חיבור הכבל וודא/י שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים כיבוי משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור באופן ידני; עיין/י בתיעוד המתג שלך.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: יש לבצע שלב זה גם במכונה 1 וגם במכונה 2.

קיימות שתי אפשרויות התקנה:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, ההתקנה המהירה ביותר
- [אפשרות 2: בנייה ידנית מקוד המקור](#option-2-manual-source-build) - בנייה מקוד המקור עם שליטה מלאה על דגלי הבנייה

### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק בנייות לילה (nightly builds) של llama.cpp עם האצת AMD ROCm 7, המיועדות ל-GPU כגון gfx1151‏ (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות נוספות.

<!-- @os:windows -->
#### שלב 1: הורדת הקבצים הבינאריים המוכנים מראש

עברו לדף המהדורה האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ הקבצים הבינאריים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת גרסאות בנייה תומכות ROCm של `llama-cli.exe`, `llama-server.exe`, ו-`rpc-server.exe`, מהודרות מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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

עברו לדף המהדורה האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ והכנת הקבצים הבינאריים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת גרסאות בנייה תומכות ROCm של `llama-cli`, `llama-server`, ו-`rpc-server`, מהודרות מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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

### אפשרות 2: בנייה ידנית מהמקור

<!-- @os:windows -->
#### שלב 1: בניית llama.cpp

פתחו את **x64 Native Tools Command Prompt** (מותקן יחד עם Visual Studio Build Tools) ושכפלו את המאגר:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

הוסיפו את HIP לנתיב שלכם ובנו עם תמיכת ROCm ו-RPC:

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

#### שלב 3: הוספת HIP לנתיב המשתמש שלכם

שלב הבנייה שלמעלה הגדיר את `%HIP_PATH%\bin` עבור הסשן הנוכחי בלבד. כדי להפוך את ספריות ה-HIP לזמינות בכל מסוף (לא רק ב-x64 Native Tools Command Prompt), הוסיפו אותו לנתיב `PATH` של המשתמש שלכם באופן קבוע:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

לאחר הכנת llama.cpp בכל צומת, המשיכו אל [הורדת המודל](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### שלב 1: בניית llama.cpp

שכפלו את המאגר:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

בנו עם תמיכת ROCm ו-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DAMDGPU_TARGETS="gfx1151"` | מכוון ל-GPU של Ryzen AI Halo (Radeon 8060s) |

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

מדריך זה משתמש ב-[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), מודל בעל 358 מיליארד פרמטרים בכימות `Q4_K_XL` מ-[Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). בכימות זה, המודל דורש כ-205GB של אחסון ומתאים לזיכרון ה-GPU המשולב של שני צמתי Ryzen AI Halo.

הורידו את קובצי ה-GGUF באמצעות ה-Hugging Face CLI:
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

> **הערה**: הורדת המודל חייבת להתבצע במכונה 1 (הבקר). צמתי ה-RPC Worker אינם זקוקים לעותק מקומי של קובצי המודל.

## הפעלת המודל באשכול

מנוע ה-RPC (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות מודל לעובדים מרוחקים דרך הרשת. מכונה אחת פועלת כ**בקר** (מכונה 1), ומטפלת בטוקניזציה, בתזמון ובתיאום. המכונה השנייה מריצה **שרת RPC** קליל (מכונה 2) שחושף את זיכרון ה-GPU וכוח העיבוד שלה לבקר.

בזמן הטעינה, llama.cpp מפצל את המודל בין שני הצמתים. לאחר הטעינה, ההסקה מתבצעת כאילו היא רצה על מאיץ יחיד. ה-RPC מטפל בהעברות ה-tensor ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרת ה-RPC (מכונה 2)

במכונה 2, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלה לבקר:
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
| `-p` | הפורט שדרכו משדרים את שרת ה-RPC |
| `-c` | מפעיל מטמון מקומי עבור tensor-ים גדולים, למניעת העברות רשת חוזרות בזמן טעינת המודל |
| `--host` | כתובת ה-IP שאליה מקושר שרת ה-RPC (`0.0.0.0` עבור כל הממשקים) |

לאפשרויות נוספות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מכונה 1)

כאשר שרת ה-RPC פועל במכונה 2, הפעילו את ההסקה ממכונה 1 באמצעות `llama-cli` או `llama-server`.

#### llama-cli

`llama-cli` מספק ממשק מבוסס מסוף לאינטראקציה ישירה עם המודל. הוא אידיאלי לבדיקות ביצועים, לניפוי באגים ולניסויים ברמה נמוכה.

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

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו במסוף (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **מציאת `<RPC_WORKER_IP>`**: במכונה 2, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס למצב פרומפט אינטראקטיבי שבו תוכלו לשוחח ישירות עם המודל:

![llama-cli מריץ את GLM 4.7 בשני צמתים](assets/llama-cli-example.png)
#### llama-server

`llama-server` חושף את אותו מנוע היסק דרך תהליך שרת מתמשך עם ממשק משתמש אינטרנטי משולב ו-API מסוג HTTP תואם OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה של משתמשים מרובים, ואינטגרציה עם כלים חיצוניים.

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

> **איתור `<RPC_WORKER_IP>`**: במחשב 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו במסוף (Powershell).

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

> **איתור `<RPC_WORKER_IP>`**: במחשב 2, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

לאחר ההפעלה, פתחו את `http://<HOST_IP>:8081` בדפדפן כדי לגשת לממשק המשתמש האינטרנטי המובנה. ממשק זה מספק ממשק צ'אט מבוסס דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server מריץ את GLM 4.7 על פני שני צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **איתור `<HOST_IP>`**: במחשב 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **איתור `<HOST_IP>`**: במחשב 1, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ המודל מסוג GGUF (השתמשו בפרגמנט הראשון, `00001-of-00005`) |
| `-c` | גודל ההקשר (context) בטוקנים. ערכים גדולים יותר משתמשים ביותר זיכרון |
| `-fa on` | מפעיל rocWMMA Flash Attention לביצועים משופרים במעבדי GPU של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל ל-GPU |
| `-lm none` | קובע את מצב טעינת המודל ל-`none`, מבטל את מיפוי הזיכרון (memory-mapping) כדי לקצר את זמני הטעינה כאשר גודל המודל עולה על זיכרון ה-RAM של המערכת אך מתאים ל-VRAM |
| `--host` | כתובת ה-IP שאליה יש לקשר את `llama-server` (`llama-server` בלבד) |
| `--port` | הפורט שדרכו יסופק ה-API מסוג HTTP (`llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## השלבים הבאים

- **חיבור אפליקציות צד שלישי**: `llama-server` חושף API תואם OpenAI. הפנו כל אפליקציה תואמת OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם מפתח API כלשהו כתחליף (למשל, `none`) כדי להתחבר לאשכול (cluster) שלכם
- **חקרו מודלים נוספים**: עיינו בקבצי GGUF מקוונטטים ב-[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחבה לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים בסדר גודל של טריליון פרמטרים. העבירו נקודות קצה נוספות ל-`--rpc` כרשימה מופרדת בפסיקים (למשל, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)