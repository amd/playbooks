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

# אשכול (Clustering) של ארבעה Ryzen™ AI Halo עם RPC

## סקירה כללית

ה-Ryzen™ AI Halo שברשותכם כבר מסוגל להריץ מודלי שפה גדולים באופן מקומי. אשכול (clustering) לוקח זאת צעד קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, מה שמעניק לכם גישה למודלים גדולים אף יותר עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר והבנה רב-לשונית עמוקה יותר, הכל לחלוטין על החומרה שלכם.

מדריך זה מלמד אתכם כיצד לאשכל ארבע מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את Kimi K2.6, מודל mixture-of-experts גדול, על פני כל ארבע המכונות עם האצת AMD ROCm™.

## מה תלמדו

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכה ב-ROCm וב-RPC
- הגדרת עובדי RPC (RPC workers) והפעלת הסקה מבוזרת בארבעה צמתים
- הרצת מודל עם 1T פרמטרים על פני ארבע מערכות Ryzen AI Halo מחוברות לרשת

## הגדרת תצורת הזיכרון

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **הרצת מודלים בסביבות 128GB ומעלה:** במערכות AMD Ryzen™ AI Max 400 Series (Gorgon Halo) המריצות Windows, מודלים המתקרבים ל-128GB זיכרון או חורגים ממנו דורשים תצורה נוספת כדי לפעול ללא שגיאות. עקבו אחר [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) לפני טעינת המודל.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
ב-Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון רב יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדירו את הערך ל-**96 GB**. יש להפעיל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת ה-Translation Table Manager (TTM) page של הליבה (kernel), לפי ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5 GB).

* התקינו את כלי השירות pipx והוסיפו את הנתיב עבור גלגלים (wheels) שהותקנו דרך pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את גלגל amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את כלי amd-ttm כדי לבדוק את ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדירו מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעילו מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.


<!-- @os:end -->
<!-- @device:halo_box -->
## בדיקת עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מוקדמות

### חומרה

מדריך זה דורש ארבע יחידות Ryzen AI Halo ומתג (switch) Ethernet אחד, מחוברים בטופולוגיית כוכב (star topology) כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet בנפח 10Gbps | 1 | מתג מרכזי המאפשר תקשורת Ryzen AI Halo מרובת צמתים (לפחות 4 יציאות) |
| כבל Ethernet | 4 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות ארבע יציאות מתג Ethernet כדי לחבר את ארבע יחידות Ryzen AI Halo. נדרשת יציאה חמישית אם אתם ניגשים למודל ממחשב לקוח נפרד במקום מאחת מיחידות ה-Halo.

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

## התקנת חומרה פיזית

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

חברו כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו מקימה את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. זיהוי ממשקי הרשת

בכל מכונה, מצאו את שם ממשק הרשת שלה ורשמו אותו (אליו נתייחס בהמשך בתור `IFNAME`). הריצו:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודאו שהקישור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלכם:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החליפו את `<IFNAME>` בשם ממשק הפלט מתוך [1. זיהוי ממשקי הרשת](#1-determine-network-interfaces)

אתם אמורים לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתה של auto-negotiation והגדרה ידנית של מהירות הקישור; עיינו בתיעוד המתג שברשותכם.

<!-- @os:end -->

<!-- @os:windows -->
### אימות מהירות קישור הרשת

בכל מכונה, בדקו את מהירות הקישור של ממשקי הרשת שלכם:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

ממשק ה-Ethernet שלכם אמור להיות `Up` ולפעול ב-`10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתה של auto-negotiation והגדרה ידנית של מהירות הקישור; עיינו בתיעוד המתג שברשותכם.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

שתי אפשרויות התקנה זמינות:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, הגדרה מהירה ביותר
- [אפשרות 2: בנייה ידנית מקוד המקור](#option-2-manual-source-build) - בנייה מקוד המקור עם שליטה מלאה בדגלי הבנייה
### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק בניות לילה (nightly builds) של llama.cpp עם תאוצת AMD ROCm 7, המיועדות ל-GPU כגון gfx1151‏ (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות נוספות.

<!-- @os:windows -->
#### שלב 1: הורדת הקבצים הבינאריים המוכנים מראש

נווטו לדף ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ הקבצים הבינאריים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת בניות מופעלות ROCm של `llama-cli.exe`,‏ `llama-server.exe`, ו-`ggml-rpc-server.exe`, שהודרו מראש עבור מערכת Ryzen AI Halo שלכם.

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

נווטו לדף ההוצאה (release) האחרונה והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר הבנייה).

#### שלב 2: חילוץ והכנת הקבצים הבינאריים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת בניות מופעלות ROCm של `llama-cli`,‏ `llama-server`, ו-`rpc-server`, שהודרו מראש עבור מערכת Ryzen AI Halo שלכם.

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

פתחו את **x64 Native Tools Command Prompt** (מותקן עם Visual Studio Build Tools) ושכפלו (clone) את המאגר:

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

שלב הבנייה שלעיל הגדיר את `%HIP_PATH%\bin` עבור ההפעלה הנוכחית בלבד. כדי להפוך את ספריות HIP לזמינות בכל מסוף (לא רק ב-x64 Native Tools Command Prompt), הוסיפו אותו ל-`PATH` של המשתמש שלכם באופן קבוע:

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
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת |
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

מדריך זה משתמש ב-[Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) בקוונטיזציית `UD-Q2_K_XL` מ-[Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). קוונטיזציה זו נכנסת בתוך הזיכרון המשולב של ה-GPU של ארבעה צמתי Ryzen AI Halo.

הורידו את קובצי ה-GGUF באמצעות ה-CLI של Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **הערה**: הורדת המודל חייבת להתבצע במכונה 1 (הבקר). צמתי ה-RPC Worker (מכונות 2, 3 ו-4) אינם זקוקים לעותק מקומי של קובצי המודל.

## הפעלת המודל במקבץ (Cluster)

מנוע ה-RPC‏ (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות מודל ל-Worker-ים מרוחקים דרך הרשת. מכונה אחת פועלת בתור ה**בקר** (מכונה 1), ומטפלת בטוקניזציה, בתזמון ובתיאום. שלוש המכונות האחרות כל אחת מריצה **שרת RPC** קל משקל (מכונות 2, 3 ו-4) החושף את זיכרון ה-GPU ואת יכולת העיבוד שלהן לבקר.

בזמן הטעינה, llama.cpp מפצל את המודל על פני כל ארבעת הצמתים. לאחר הטעינה, ההסקה ממשיכה כאילו היא פועלת על מאיץ יחיד. RPC מטפל בהעברות הטנסורים ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרתי ה-RPC (מכונות 2, 3 ו-4)

בכל אחת ממכונות 2, 3 ו-4, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלה לבקר:
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
| `-c` | מפעיל מטמון מקומי עבור טנסורים גדולים, ומונע העברות רשת חוזרות במהלך טעינת המודל |
| `--host` | כתובת ה-IP שאליה יקושר שרת ה-RPC (`0.0.0.0` עבור כל הממשקים) |

לאפשרויות נוספות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מכונה 1)

עם שרתי ה-RPC פועלים במכונות 2, 3 ו-4, הפעילו את ההסקה ממכונה 1 באמצעות `llama-cli` או `llama-server`.
#### llama-cli

`llama-cli` מספק ממשק מבוסס-מסוף לאינטראקציה ישירה עם המודל. הוא אידיאלי לבנצ'מארקינג, דיבוג וניסויים ברמה נמוכה.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **איתור `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3 ו-4, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו בטרמינל (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **איתור `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3 ו-4, הריצו `ipconfig | findstr /C:"IPv4"` בטרמינל (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההפעלה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס להנחיה אינטראקטיבית שבה ניתן לשוחח ישירות עם המודל:

![llama-cli פועל עם Kimi K2.6 על פני ארבעה צמתים](assets/llama-cli-example.png)

#### llama-server

`llama-server` חושף את אותו מנוע היסק דרך תהליך שרת מתמשך עם ממשק משתמש אינטרנטי משולב ו-API מבוסס HTTP תואם OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה מרובת-משתמשים ואינטגרציה עם כלים חיצוניים.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **איתור `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3 ו-4, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הריצו פקודה זו בטרמינל (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **איתור `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3 ו-4, הריצו `ipconfig | findstr /C:"IPv4"` בטרמינל (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

לאחר ההפעלה, פתחו את `http://<HOST_IP>:8081` בדפדפן שלכם כדי לגשת לממשק המשתמש האינטרנטי המובנה. זה מספק ממשק צ'אט מבוסס-דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server פועל עם Kimi K2.6 על פני ארבעה צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **איתור `<HOST_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **איתור `<HOST_IP>`**: במכונה 1, הריצו `ipconfig | findstr /C:"IPv4"` בטרמינל (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ מודל ה-GGUF (השתמשו בחלק הראשון, `00001-of-00008`) |
| `-c` | גודל ההקשר באסימונים (tokens). ערכים גדולים יותר משתמשים ביותר זיכרון |
| `-fa on` | מאפשר rocWMMA Flash Attention לביצועים משופרים ב-GPU של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל ל-GPU |
| `-lm none` | מגדיר את מצב הטעינה של המודל ל-`none`, ומבטל מיפוי זיכרון (memory-mapping) כדי לקצר זמני טעינה כאשר גודל המודל חורג מזיכרון המערכת (RAM) אך מתאים ל-VRAM |
| `-b` | גודל אצווה לוגי (batch size) באסימונים. הגדרה ל-4096 מאזנת בין תפוקה לשימוש בזיכרון בין הצמתים |
| `-ub` | גודל אצווה פיזי (מיקרו) לעיבוד הנחיות (prompt processing). התאמה ל-`-b` נמנעת מתקורת פיצול (chunking) מיותרת |
| `--host` | כתובת IP לקישור `llama-server` אליה (`llama-server` בלבד) |
| `--port` | היציאה (port) שבה מוגש ה-API של HTTP (`llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## השלבים הבאים

- **חיבור יישומי צד שלישי**: `llama-server` חושף API תואם OpenAI. הפנו כל יישום תואם OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם מפתח API זמני כלשהו (לדוגמה, `none`) כדי להתחבר לאשכול (cluster) שלכם
- **חקרו מודלים נוספים**: עיינו ב-GGUF-ים מכומתים (quantized) ב[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחבה מעבר לארבעה צמתים**: הוסיפו מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים מעבר לקנה מידה של טריליון פרמטרים. העבירו נקודות קצה נוספות ל-`--rpc` כרשימה מופרדת בפסיקים (לדוגמה, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)