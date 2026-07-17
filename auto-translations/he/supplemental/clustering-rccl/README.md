<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# אשכול שני מערכות Ryzen™ AI Halo עם RCCL

## סקירה כללית

ה-Ryzen™ AI Halo שלך כבר מסוגל להריץ מודלים של שפה גדולים באופן מקומי. אשכול מרחיב יכולת זו על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לך גישה למודלים גדולים עוד יותר עם יכולת הסקה חזקה יותר, יצירת קוד טובה יותר והבנה רב-לשונית עמוקה יותר — הכל על החומרה שלך בלבד.

מדריך זה מלמד אותך כיצד לאשכל שתי מערכות Ryzen AI Halo באמצעות RCCL (ROCm Communication Collectives Library) עם vLLM ולהריץ את Qwen3.5-397B, מודל בעל 397 מיליארד פרמטרים, על פני שתי המכונות עם האצת ROCm.

## מה תלמד

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- הפעלת vLLM עם תמיכה ב-ROCm
- הגדרת RCCL להסקה מקבילה-טנסורית מרובת-צמתים על פני שתי מערכות Ryzen AI Halo
- הרצת מודל בעל 397 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## דרישות מוקדמות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet בעל 10Gbps | 1 | מתג מרכזי לאפשר תקשורת מרובת-צמתים בין מערכות Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet לחיבור שתי יחידות Ryzen AI Halo. יציאה שלישית נדרשת אם אתה ניגש למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

חבר כל יחידת Ryzen AI Halo למתג Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו מבססת את קישור ה-10Gbps המשמש לתקשורת במהירות גבוהה בין הצמתים.

### 1. זיהוי ממשקי הרשת

על כל מכונה, מצא את שם ממשק הרשת שלה ורשום אותו (הוא יכונה בהמשך ההוראות `IFNAME`). הרץ:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

אשר שהקישור פעיל ורץ במהירות מלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף את `<IFNAME>` בשם הממשק שהתקבל מ-[1. זיהוי ממשקי הרשת](#1-determine-network-interfaces)

אמור לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדוק את חיבור הכבל ואשר שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתת ניהול-אוטומטי והגדרה ידנית של מהירות הקישור; עיין בתיעוד המתג שלך.

## הרחבת הקצאת VRAM

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

### הגדרת זיכרון להרצת מודלים גדולים

ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית זיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת דף Translation Table Manager (TTM) של הקרנל, בהתאם להוראות הבאות. AMD ממליצה להגדיר את ה-VRAM הייעודי המינימלי ב-BIOS (0.5 GB).

* התקן את כלי השירות pipx והוסף את הנתיב לגלגלים המותקנים על ידי pipx לנתיב החיפוש של המערכת.

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

* אתחל את המערכת כדי שהשינויים ייכנסו לתוקף.

## אתחול מיכל vLLM

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

ה-Ryzen AI Halo שלך מגיע עם vLLM ארוז בתוך תמונת מיכל מוכנה מראש, אותה אתה מריץ באמצעות Podman, כלי מיכלים חינמי וקוד פתוח.

### 1. יצירת ספריית הורדת המודל

כאשר תגיש את מודל Qwen3.5-397B במדריך זה, vLLM יוריד אוטומטית את משקלי המודל למערכת שלך. כדי לוודא שמשקלים אלה נגישים מתוך המיכל, צור תחילה ספריית מודלים שהמיכל יכול לעגן:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. הפעלת מיכל vLLM

הפקודה שלהלן מפעילה את המיכל ומוציאה אותך לממשק פקודות אינטראקטיבי. היא עוגנת את ספריית המודלים שיצרת זה עתה ומעבירה את `IFNAME` שלך אל `NCCL_SOCKET_IFNAME` ו-`GLOO_SOCKET_IFNAME`, ומודיעה ל-RCCL (הספרייה שבה vLLM משתמש לתיאום GPU-ים ברחבי האשכול) איזה ממשק להשתמש בו.

הפעל את המיכל עם:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **הערה**: החלף את `<IFNAME>` בשם הממשק שהתקבל מ-[1. זיהוי ממשקי הרשת](#1-determine-network-interfaces)

## הרצת המודל על האשכול

vLLM משתמש ב-Ray לתזמור האשכול וב-RCCL לטיפול בתקשורת GPU-ל-GPU בין הצמתים. מכונה אחת משמשת כ**צומת ראש** (מכונה 1), המתאמת את ההסקה. השנייה מצטרפת כ**צומת עובד** (מכונה 2), התורמת את זיכרון ה-GPU ואת כוח החישוב שלה.

> **הערה**: Ray הוא תלות אופציונלית עבור vLLM וזמין רק מתוך מיכל Podman המוגדר מראש.

בעת ההפעלה, vLLM מפצל את המודל על פני שני הצמתים באמצעות מקביליות טנסורית. לאחר הטעינה, ההסקה מתבצעת כאילו רצה על מאיץ יחיד.

### שלב 1: הפעלת צומת הראש של Ray (מכונה 1)

על מכונה 1, הפעל את צומת הראש של Ray לאתחול האשכול:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **איתור `<MACHINE_1_IP>`**: על מכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 2: הצטרפות לאשכול (מכונה 2)

על מכונה 2, התחבר לצומת הראש ליצירת האשכול:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **איתור `<MACHINE_2_IP>`**: על מכונה 2, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 3: הגשת המודל (מכונה 1)

על מכונה 1, הפעל את שרת vLLM. פעולה זו תוריד אוטומטית את המודל ותתחיל להגיש אותו על פני שני הצמתים:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### עזר לפרמטרים

| דגל | מטרה |
|------|---------|
| `--port` | יציאה להגשת ה-API של HTTP עליה |
| `--host` | כתובת IP לקשירת השרת אליה (`0.0.0.0` לכל הממשקים) |
| `--max-model-len` | אורך הקשר מקסימלי בטוקנים |
| `--gpu-memory-utilization` | שבר זיכרון ה-GPU להקצאה (0.0–1.0) |
| `--dtype` | סוג נתונים למשקלי המודל |
| `--tensor-parallel-size` | מספר GPU-ים לפיצול המודל עליהם (הגדר לסך ה-GPU-ים באשכול) |
| `--distributed-executor-backend` | ממשק עורפי לביצוע מרובת-צמתים (`ray` לפריסות אשכול) |
| `--enforce-eager` | משבית קומפילציית גרף CUDA לצורך תאימות |
| `--language-model-only` | מדלג על טעינת רכיבי מודל עזר (למשל, מקודד חזותי) |
| `--reasoning-parser` | מאפשר ניתוח פלט הסקה מובנה עבור המודל |

לשימוש מלא בפרמטרים, עיין ב-[תיעוד vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## גישה למודל

vLLM חושף API תואם-OpenAI, כך שתוכל לחבר כל לקוח או ממשק תואם לאשכול שלך. אפשרות פופולרית אחת היא [Open WebUI](https://github.com/open-webui/open-webui), המספקת ממשק צ'אט מבוסס-דפדפן.

לחיבור Open WebUI לנקודת הקצה של vLLM:

1. פתח **Settings** > **Admin Panel** > **Connections**
2. לחץ על **+** ב-**Manage OpenAI API Connections**
3. הגדר את **Connection Type** ל-**External**
4. הגדר את **URL** ל-`http://<MACHINE_1_IP>:7000/v1`
5. תחת **Auth**, בחר **None** מהתפריט הנפתח
6. השאר את **Model IDs** ריק לגילוי אוטומטי של כל המודלים מנקודת הקצה

> **איתור `<MACHINE_1_IP>`**: על מכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה. אם אתה ניגש ל-Open WebUI ממכונה 1 עצמה, תוכל להשתמש ב-`http://localhost:7000/v1`.

![הגדרות חיבור Open WebUI לנקודת הקצה של vLLM](assets/openwebui-connection.png)

לאחר החיבור, בחר את המודל מתפריט המודלים ב-Open WebUI והתחל לשוחח. המודל רץ כעת על פני שני צמתי Ryzen AI Halo שלך:

![שיחה עם Qwen3.5-397B ב-Open WebUI](assets/openwebui-chat.png)

## השלבים הבאים

- **חקור מודלים נוספים**: גלה מודלים חדשים ב-[Hugging Face](https://huggingface.co/models?&sort=trending) המתאימים לזיכרון ה-GPU המשולב של האשכול שלך
- **הרחב לארבעה צמתים**: הוסף שתי מערכות Ryzen AI Halo נוספות כעובדי Ray נוספים לפיצול מודלים על פני עוד GPU-ים. פעולה זו דורשת מתג Ethernet עם לפחות ארבע יציאות, אחת לכל צומת. עקוב אחר [שלב 2: הצטרפות לאשכול](#step-2-join-the-cluster-machine-2) על כל עובד נוסף והגדל את `--tensor-parallel-size` בהתאם
- **נסה אסטרטגיות מקביליות אחרות**: vLLM תומך ב-[מקביליות מומחים](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) עבור מודלים של תערובת-מומחים וב-[מקביליות נתונים](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) לתפוקה גבוהה יותר. נסה עם `--enable-expert-parallel` ו-`--data-parallel-size` כדי למצוא את התצורה הטובה ביותר לעומס העבודה שלך