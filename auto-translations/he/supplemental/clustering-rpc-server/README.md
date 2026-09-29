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

# אשכול (Clustering) של שני מכשירי Ryzen™ AI Halo באמצעות RPC

## סקירה כללית

מכשיר ה-Ryzen™ AI Halo שברשותכם כבר מסוגל להריץ מודלים גדולים של שפה (LLM) באופן מקומי. אשכול (Clustering) לוקח את זה צעד קדימה, על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לכם גישה למודלים גדולים אף יותר, עם יכולות הנמקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית מעמיקה יותר - הכול לחלוטין על החומרה שלכם.

מדריך זה מלמד אתכם כיצד לבצע אשכול (clustering) של שתי מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp, ולהריץ את GLM 4.7, מודל בעל 358 מיליארד פרמטרים, על פני שתי המכונות עם האצת AMD ROCm™.

## מה תלמדו

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכת ROCm ו-RPC
- הגדרת עובד RPC (RPC worker) והפעלת הסקה מבוזרת (distributed inference) על פני שני צמתים
- הרצת מודל בעל 358 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: השלימו שלב זה הן במכונה 1 והן במכונה 2.

<!-- @os:windows -->
במערכת Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון רב יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת פאנל הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדירו את הערך ל-**96 GB**. יש לאתחל את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
במערכת Linux, ROCm משתמש במאגר זיכרון משותף של המערכת, ומאגר זה מוגדר כברירת מחדל לחצי מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת דפי ה-Translation Table Manager (TTM) של הליבה (kernel), בהתאם להוראות הבאות. AMD ממליצה להגדיר את ה-VRAM המוקדש המינימלי ב-BIOS (0.5 GB).

* התקינו את כלי השירות pipx והוסיפו את הנתיב עבור wheels המותקנים על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את הכלי amd-ttm כדי לשלוח שאילתה לגבי ההגדרות הנוכחיות של הזיכרון המשותף.
  ```bash
  amd-ttm
  ```

* קבעו מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* אתחלו את המערכת כדי שהשינויים ייכנסו לתוקף.


<!-- @os:end -->
<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מקדימות

### חומרה

מדריך זה דורש שני מכשירי Ryzen AI Halo ומתג Ethernet אחד, המחוברים בטופולוגיית כוכב (star topology) כאשר כל מכשיר מחובר ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet במהירות 10Gbps | 1 | מתג מרכזי המאפשר תקשורת Ryzen AI Halo מרובת צמתים (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל מכשיר Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שני מכשירי Ryzen AI Halo. נדרשת יציאה שלישית אם אתם ניגשים למודל ממכונת לקוח נפרדת במקום מאחד ממכשירי ה-Halo.

### תוכנה
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
אנא התקינו:
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

## הגדרת החומרה הפיזית

> **הערה**: השלימו שלב זה הן במכונה 1 והן במכונה 2.

חברו כל מכשיר Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו יוצרת את הקישור בקצב 10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. קביעת ממשקי הרשת

בכל מכונה, מצאו את שם ממשק הרשת שלה ורשמו אותו (הוא ייקרא להלן `IFNAME`). הריצו:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מציגה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודאו שהקישור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלכם:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החליפו את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אתם אמורים לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול של auto-negotiation והגדרת מהירות הקישור באופן ידני; עיינו בתיעוד המתג שלכם.

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

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול של auto-negotiation והגדרת מהירות הקישור באופן ידני; עיינו בתיעוד המתג שלכם.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: השלימו שלב זה הן במכונה 1 והן במכונה 2.

זמינות שתי אפשרויות התקנה:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, ההתקנה המהירה ביותר
- [אפשרות 2: בנייה ידנית מהמקור](#option-2-manual-source-build) - בנייה מהמקור עם שליטה מלאה על דגלי הבנייה

### אפשרות 1: Lemonade SDK (מומלץ)

Lemonade SDK מספק גרסאות בנייה לילית (nightly builds) של llama.cpp עם האצת AMD ROCm 7, המיועדות ל-GPU כגון gfx1151 (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות אחרות.

<!-- @os:windows -->
#### שלב 1: הורדת הבינארים המוכנים מראש

נווטו לדף הגרסה האחרונה והורידו את הארכיון התואם לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ הבינארים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת בניות תומכות-ROCm של `llama-cli.exe`, `llama-server.exe`, ו-`rpc-server.exe`, מהודרות מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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
#### שלב 1: הורדת הבינארים המוכנים מראש

נווטו לדף הגרסה האחרונה והורידו את הארכיון התואם לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ והכנת הבינארים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת בניות תומכות-ROCm של `llama-cli`, `llama-server`, ו-`rpc-server`, מהודרות מראש עבור מערכת ה-Ryzen AI Halo שלכם.

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

פתחו את **x64 Native Tools Command Prompt** (מותקן יחד עם Visual Studio Build Tools) ושכפלו את המאגר:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

הוסיפו את HIP לנתיב שלכם ובנו עם תמיכה ב-ROCm וב-RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm/HIP |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DGPU_TARGETS=gfx1151` | מיועד ל-GPU של Ryzen AI Halo‏ (Radeon 8060s) |
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

שלב הבנייה שלעיל הגדיר את `%HIP_PATH%\bin` עבור ההפעלה הנוכחית בלבד. כדי להפוך את ספריות HIP לזמינות בכל מסוף (לא רק ב-x64 Native Tools Command Prompt), הוסיפו אותו לנתיב `PATH` של המשתמש שלכם באופן קבוע:

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

בנו עם תמיכה ב-ROCm וב-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
| `-DAMDGPU_TARGETS="gfx1151"` | מיועד ל-GPU של Ryzen AI Halo‏ (Radeon 8060s) |

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

מדריך זה משתמש ב[GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), מודל בעל 358 מיליארד פרמטרים בקוונטיזציית `Q4_K_XL` מבית [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). בקוונטיזציה זו המודל דורש כ-205GB של אחסון ומתאים לזיכרון ה-GPU המשולב של שני צמתי Ryzen AI Halo.

הורידו את קבצי ה-GGUF באמצעות ה-Hugging Face CLI:
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

> **הערה**: הורדת המודל חייבת להתבצע על מכונה 1 (הבקר). צמתי עובד ה-RPC אינם זקוקים לעותק מקומי של קבצי המודל.

## הפעלת המודל על גבי האשכול

מנוע ה-RPC (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות של המודל לעובדים מרוחקים דרך הרשת. מכונה אחת פועלת בתור **הבקר** (מכונה 1), ומטפלת בטוקניזציה, בתזמון ובתיאום. המכונה השנייה מריצה **שרת RPC** קליל (מכונה 2) שחושף את זיכרון ה-GPU ואת כוח החישוב שלה לבקר.

בזמן הטעינה, llama.cpp מפצל את המודל בין שני הצמתים. לאחר הטעינה, ההסקה ממשיכה כאילו היא רצה על מאיץ יחיד. RPC מטפל בהעברות הטנסורים ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרת ה-RPC (מכונה 2)

על מכונה 2, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלה לבקר:
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
| `-p` | הפורט לשידור שרת ה-RPC |
| `-c` | מאפשר מטמון מקומי עבור טנסורים גדולים, תוך הימנעות מהעברות רשת חוזרות במהלך טעינת המודל |
| `--host` | כתובת ה-IP לקישור שרת ה-RPC אליה (`0.0.0.0` עבור כל הממשקים) |

לאפשרויות נוספות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מכונה 1)

כאשר שרת ה-RPC פועל על מכונה 2, הפעילו את ההסקה ממכונה 1 באמצעות `llama-cli` או `llama-server`.

#### llama-cli

`llama-cli` מספק ממשק מבוסס-מסוף לאינטראקציה ישירה עם המודל. הוא אידיאלי לבנצ'מרקינג, לניפוי שגיאות ולניסויים ברמה נמוכה.

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

> **מציאת `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
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

> **מציאת `<RPC_WORKER_IP>`**: על מכונה 2, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס לשורת פקודה אינטראקטיבית שבה תוכלו לשוחח ישירות עם המודל:

![llama-cli מריץ את GLM 4.7 בפריסה על שני צמתים](assets/llama-cli-example.png)
#### llama-server

`llama-server` חושף את אותו מנוע הסקה דרך תהליך שרת מתמשך עם ממשק משתמש רשתי משולב וממשק API מבוסס HTTP תואם-OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה של משתמשים מרובים, ואינטגרציה עם כלים חיצוניים.

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

לאחר ההפעלה, פתחו את `http://<HOST_IP>:8081` בדפדפן כדי לגשת לממשק המשתמש הרשתי המובנה. הוא מספק ממשק צ'אט מבוסס דפדפן לאינטראקציה עם המודל:

![ממשק משתמש רשתי של llama-server מריץ GLM 4.7 על פני שני צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **איתור `<HOST_IP>`**: במחשב 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

<!-- @os:windows -->
> **איתור `<HOST_IP>`**: במחשב 1, הריצו `ipconfig | findstr /C:"IPv4"` במסוף (Powershell) כדי למצוא את כתובת ה-IP המקומית שלו.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ מודל ה-GGUF (השתמשו במקטע הראשון, `00001-of-00005`) |
| `-c` | גודל ההקשר בטוקנים. ערכים גדולים יותר משתמשים בזיכרון רב יותר |
| `-fa on` | מפעיל את rocWMMA Flash Attention לביצועים משופרים ב-GPU-ים של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל ל-GPU |
| `-lm none` | מגדיר את מצב טעינת המודל ל-`none`, ומבטל מיפוי זיכרון כדי לצמצם זמני טעינה כאשר גודל המודל חורג מזיכרון ה-RAM של המערכת אך מתאים ל-VRAM |
| `--host` | כתובת ה-IP שאליה יש לקשר את `llama-server` (רק ב-`llama-server`) |
| `--port` | הפורט שדרכו יסופק ממשק ה-API של HTTP (רק ב-`llama-server`) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## הצעדים הבאים

- **חיבור אפליקציות צד שלישי**: `llama-server` חושף API תואם-OpenAI. הפנו כל אפליקציה תואמת-OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם מפתח API כלשהו כמציין מקום (למשל, `none`) כדי להתחבר לאשכול שלכם
- **חקירת מודלים נוספים**: עיינו ב-GGUF-ים מכומתים ב-[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים המתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **התרחבות לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים בקנה מידה של טריליון פרמטרים. העבירו נקודות קצה נוספות ל-`--rpc` כרשימה מופרדת בפסיקים (למשל, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)