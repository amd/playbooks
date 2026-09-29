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

# חיבור בענן (Clustering) של ארבעה מחשבי Ryzen™ AI Halo עם RPC

## סקירה כללית

מחשב ה-Ryzen™ AI Halo שברשותכם כבר מסוגל להריץ מודלים גדולים של שפה (LLM) באופן מקומי. חיבור בענן (clustering) לוקח זאת צעד קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לכם גישה למודלים גדולים אף יותר, עם יכולות היגיון חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית עמוקה יותר - הכול על החומרה שלכם בלבד.

מדריך זה מלמד אתכם כיצד לחבר בענן ארבע מערכות Ryzen AI Halo באמצעות מנוע ה-RPC של llama.cpp ולהריץ את Kimi K2.6, מודל גדול מסוג mixture-of-experts, על פני כל ארבעת המכונות עם האצת AMD ROCm™.

## מה תלמדו

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- התקנת llama.cpp עם תמיכה ב-ROCm וב-RPC
- הגדרת עובדי RPC (RPC workers) והפעלת הסקה מבוזרת (distributed inference) על פני ארבעה צמתים
- הרצת מודל בעל טריליון פרמטרים על פני ארבע מערכות Ryzen AI Halo מחוברות ברשת

## הגדרת תצורת הזיכרון

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

<!-- @os:windows -->
במערכת Windows, כדי להריץ מודלים גדולים יותר הדורשים זיכרון רב יותר, עלינו להשתמש בהקצאת AMD Variable Graphics Memory (iGPU VRAM).

ניתן לעשות זאת על ידי פתיחת לוח הבקרה AMD Software: Adrenalin Edition וניווט אל: `Performance > Tuning > AMD Variable Graphics Memory`. הגדירו את הערך ל-**96 GB**. אנא הפעילו מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
במערכת Linux, ROCm משתמש במאגר זיכרון משותף למערכת, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת עמודי ה-Translation Table Manager (TTM) של הליבה (kernel), בעזרת ההוראות הבאות. AMD ממליצה להגדיר את ה-VRAM הייעודי המינימלי ב-BIOS (0.5 GB).

* התקינו את כלי pipx והוסיפו את הנתיב לחבילות wheel שהותקנו באמצעות pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את חבילת ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את הכלי amd-ttm כדי לבדוק את ההגדרות הנוכחיות של הזיכרון המשותף.
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
## בדקו אם קיימים עדכוני תוכנה

<!-- @require:software-update -->
<!-- @device:end -->
## דרישות מקדימות

### חומרה

מדריך זה דורש ארבע יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | צמתי חישוב המרכיבים את האשכול (cluster) |
| מתג Ethernet בקצב 10Gbps | 1 | מתג מרכזי המאפשר תקשורת רב-צמתית בין יחידות Ryzen AI Halo (לפחות 4 יציאות) |
| כבל Ethernet | 4 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות ארבע יציאות במתג ה-Ethernet לחיבור ארבע יחידות Ryzen AI Halo. נדרשת יציאה חמישית אם אתם ניגשים למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

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

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

חברו כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (ומעלה). פעולה זו מקימה את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.
<!-- @os:linux -->
### 1. קביעת ממשקי הרשת

בכל מכונה, מצאו את שם ממשק הרשת שלה ורשמו אותו (הוא יכונה בהמשך `IFNAME`). הריצו:

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

> **הערה**: החליפו את `<IFNAME>` בשם ממשק הפלט מתוך [1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אתם אמורים לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול של auto-negotiation והגדרה ידנית של מהירות הקישור; עיינו בתיעוד המתג שלכם.

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

> **הערה**: אם המהירות נמוכה מ-`10 Gbps` או שהקישור אינו עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול של auto-negotiation והגדרה ידנית של מהירות הקישור; עיינו בתיעוד המתג שלכם.

<!-- @os:end -->

## התקנת llama.cpp

> **הערה**: השלימו שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

קיימות שתי אפשרויות התקנה:

- [אפשרות 1: Lemonade SDK (מומלץ)](#option-1-lemonade-sdk-recommended) - קבצים בינאריים בנויים מראש, ההתקנה המהירה ביותר
- [אפשרות 2: בנייה ידנית מקוד המקור](#option-2-manual-source-build) - בנייה מקוד המקור עם שליטה מלאה בדגלי הבנייה

### אפשרות 1: Lemonade SDK (מומלץ)

ה-Lemonade SDK מספק בניות לילה (nightly builds) של llama.cpp עם האצת AMD ROCm 7, המיועדות ל-GPU כגון gfx1151‏ (Strix Halo / Ryzen AI Max+ 395) וארכיטקטורות Radeon עדכניות נוספות.

<!-- @os:windows -->
#### שלב 1: הורדת הקבצים הבינאריים המוכנים מראש

נווטו לדף ההוצאה (release) העדכני ביותר והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר ה-build).

#### שלב 2: חילוץ הקבצים הבינאריים

חלצו את הארכיון שהורדתם:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

תיקייה זו מכילה כעת בנייה (build) עם תמיכת ROCm של `llama-cli.exe`, `llama-server.exe` ו-`ggml-rpc-server.exe`, שהודרו מראש עבור מערכת Ryzen AI Halo שברשותכם.

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

נווטו לדף ההוצאה (release) העדכני ביותר והורידו את הארכיון המתאים לפלטפורמה וליעד ה-GPU שלכם:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

הורידו את הקובץ בשם `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (כאשר `xxxx` הוא מספר ה-build).

#### שלב 2: חילוץ והכנת הקבצים הבינאריים

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

תיקייה זו מכילה כעת בנייה (build) עם תמיכת ROCm של `llama-cli`, `llama-server` ו-`rpc-server`, שהודרו מראש עבור מערכת Ryzen AI Halo שברשותכם.

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

הוסיפו את HIP לנתיב שלכם ובנו עם תמיכת ROCm ו-RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm/HIP |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת (distributed inference) |
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

שלב הבנייה שלמעלה הגדיר את `%HIP_PATH%\bin` עבור ההפעלה הנוכחית בלבד. כדי להנגיש את ספריות HIP בכל מסוף (ולא רק ב-x64 Native Tools Command Prompt), הוסיפו אותו לקבוע `PATH` של המשתמש שלכם:

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

בנו עם תמיכת ROCm ו-RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| דגל בנייה | מטרה |
|-----------|---------|
| `-DGGML_HIP=ON` | מפעיל את מחסנית התוכנה ROCm |
| `-DGGML_RPC=ON` | מפעיל RPC להסקה מבוזרת (distributed inference) |
| `-DAMDGPU_TARGETS="gfx1151"` | מכוון ל-GPU של Ryzen AI Halo (Radeon 8060s) |

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

מדריך זה משתמש ב-[Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) ברמת הקוונטיזציה `UD-Q2_K_XL` מבית [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). קוונטיזציה זו משתלבת בתוך זיכרון ה-GPU המשולב של ארבעה צמתי Ryzen AI Halo.

הורידו את קבצי ה-GGUF באמצעות ה-CLI של Hugging Face:
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

> **הערה**: הורדת המודל חייבת להתבצע במחשב 1 (הבקר). צמתי ה-worker של RPC (מחשבים 2, 3, ו-4) אינם זקוקים לעותק מקומי של קבצי המודל.

## הפעלת המודל באשכול (Cluster)

מנוע ה-RPC (Remote Procedure Call) של llama.cpp מאפשר למופע יחיד של llama.cpp להעביר שכבות מודל ל-workers מרוחקים דרך הרשת. מחשב אחד משמש כ**בקר** (Machine 1), ומטפל בטוקניזציה, תזמון, ותיאום. שלושת המחשבים האחרים מריצים כל אחד **שרת RPC** קליל (מחשבים 2, 3, ו-4) שחושף את זיכרון ה-GPU ואת כוח החישוב שלו לבקר.

בזמן הטעינה, llama.cpp מפצל את המודל בין כל ארבעת הצמתים. לאחר הטעינה, ההסקה (inference) ממשיכה כאילו רצה על מאיץ יחיד. ה-RPC מטפל בהעברת הטנסורים ובסנכרון מאחורי הקלעים.

### שלב 1: הפעלת שרתי ה-RPC (מחשבים 2, 3, ו-4)

בכל אחד ממחשבים 2, 3, ו-4, הפעילו את שרת ה-RPC כדי לחשוף את משאבי ה-GPU שלו לבקר:
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
| `-p` | הפורט שדרכו משודר שרת ה-RPC |
| `-c` | מפעיל מטמון מקומי לטנסורים גדולים, ומונע העברות רשת חוזרות במהלך טעינת המודל |
| `--host` | כתובת ה-IP שאליה יאוגד שרת ה-RPC (`0.0.0.0` עבור כל הממשקים) |

למידע נוסף על אפשרויות, עיינו ב[תיעוד ה-RPC של llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### שלב 2: הפעלת המודל (מחשב 1)

לאחר שהריצו את שרתי ה-RPC על מחשבים 2, 3, ו-4, הפעילו את ההסקה ממחשב 1 באמצעות `llama-cli` או `llama-server`.
#### llama-cli

`llama-cli` מספק ממשק מבוסס טרמינל לאינטראקציה ישירה עם המודל. הוא אידיאלי לבנצ'מרקינג, דיבאג וניסויים ברמה נמוכה.

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

> **מציאת `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3, ו-4, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הרץ פקודה זו ב-Terminal (Powershell).

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

> **מציאת `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3, ו-4, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.

<!-- @os:end -->

לאחר ההרצה, `llama-cli` מציג את התקדמות טעינת המודל ונכנס לפרומפט אינטראקטיבי שבו ניתן לשוחח ישירות עם המודל:

![llama-cli פועל עם Kimi K2.6 על פני ארבעה צמתים](assets/llama-cli-example.png)

#### llama-server

`llama-server` חושף את אותו מנוע היסק דרך תהליך שרת מתמיד עם ממשק משתמש אינטרנטי מובנה ו-API מסוג HTTP תואם OpenAI. זהו הממשק המועדף לפריסות ארוכות טווח, גישה של משתמשים מרובים, ואינטגרציה עם כלים חיצוניים.

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

> **מציאת `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3, ו-4, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **הערה**: הרץ פקודה זו ב-Terminal (Powershell).

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

> **מציאת `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: בכל אחת מהמכונות 2, 3, ו-4, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

לאחר ההפעלה, פתח את `http://<HOST_IP>:8081` בדפדפן שלך כדי לגשת לממשק המשתמש האינטרנטי המובנה. זה מספק ממשק צ'אט מבוסס דפדפן לאינטראקציה עם המודל:

![ממשק המשתמש האינטרנטי של llama-server פועל עם Kimi K2.6 על פני ארבעה צמתים](assets/llama-server-example.png)

<!-- @os:linux -->
> **מציאת `<HOST_IP>`**: על מכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

<!-- @os:windows -->
> **מציאת `<HOST_IP>`**: על מכונה 1, הרץ `ipconfig | findstr /C:"IPv4"` ב-Terminal (Powershell) כדי למצוא את כתובת ה-IP המקומית שלה.
<!-- @os:end -->

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `-m` | נתיב לקובץ מודל ה-GGUF (השתמש בשבר הראשון, `00001-of-00008`) |
| `-c` | גודל ההקשר בטוקנים. ערכים גדולים יותר צורכים יותר זיכרון |
| `-fa on` | מפעיל rocWMMA Flash Attention לביצועים משופרים על GPU-ים של AMD |
| `-ngl 999` | מעביר את כל שכבות המודל אל ה-GPU |
| `-lm none` | מגדיר את מצב טעינת המודל ל-`none`, ומבטל מיפוי זיכרון (memory-mapping) כדי לקצר את זמני הטעינה כאשר גודל המודל עולה על זיכרון ה-RAM של המערכת אך מתאים לזיכרון ה-VRAM |
| `-b` | גודל אצווה לוגי (batch) בטוקנים. הגדרה של 4096 מאזנת בין תפוקה לשימוש בזיכרון בין הצמתים |
| `-ub` | גודל אצווה פיזי (מיקרו) לעיבוד פרומפט. התאמה ל-`-b` מונעת עלויות פיצול מיותרות |
| `--host` | כתובת ה-IP שאליה יש לקשור את `llama-server` (`llama-server` בלבד) |
| `--port` | הפורט שדרכו יוגש ה-API של HTTP (`llama-server` בלבד) |
| `--rpc` | רשימה מופרדת בפסיקים של נקודות קצה של עובדי RPC (`IP:port`) |

לשימוש מלא בפרמטרים, עיין ב[תיעוד llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) וב[תיעוד llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## הצעדים הבאים

- **חיבור אפליקציות צד שלישי**: `llama-server` חושף API תואם OpenAI. הפנה כל אפליקציה תואמת OpenAI (כגון Open WebUI) אל `http://<HOST_IP>:8081` עם מפתח API כלשהו כמציין מקום (לדוגמה, `none`) כדי להתחבר לאשכול שלך
- **חקירת מודלים נוספים**: עיין ב-GGUF-ים מכומתים (quantized) ב-[Hugging Face](https://huggingface.co/models?search=gguf) כדי למצוא מודלים המתאימים לזיכרון ה-GPU המשולב של האשכול שלך
- **הרחבה מעבר לארבעה צמתים**: הוסף מערכות Ryzen AI Halo נוספות כעובדי RPC נוספים כדי לגשת למודלים מעבר לסקאלה של טריליון פרמטרים. העבר נקודות קצה נוספות אל `--rpc` כרשימה מופרדת בפסיקים (לדוגמה, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)