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

# צבירת (Clustering) שני Ryzen™ AI Halo באמצעות RCCL

## סקירה כללית

מערכת ה-Ryzen™ AI Halo שברשותך כבר מסוגלת להריץ מודלי שפה גדולים באופן מקומי. צבירה (clustering) לוקחת זאת צעד נוסף קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניקה לך גישה למודלים גדולים אף יותר עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית עמוקה יותר, הכל לגמרי על החומרה שלך.

מדריך זה מלמד אותך כיצד לצבור (cluster) שתי מערכות Ryzen AI Halo באמצעות RCCL (ROCm Communication Collectives Library) עם vLLM ולהריץ את Qwen3.5-397B, מודל בעל 397 מיליארד פרמטרים, על פני שתי המכונות עם האצת ROCm.

## מה תלמד

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- הפעלת vLLM עם תמיכת ROCm
- הגדרת RCCL להסקה מקבילית-טנזורית (tensor-parallel) מרובת-צמתים בין שתי מערכות Ryzen AI Halo
- הרצת מודל בעל 397 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מחוברות ברשת

## דרישות מוקדמות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול (cluster) |
| מתג Ethernet בקצב 10Gbps | 1 | מתג מרכזי לאפשור תקשורת רב-צמתית בין יחידות Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שתי יחידות ה-Ryzen AI Halo. נדרשת יציאה שלישית אם אתה ניגש למודל ממכונת לקוח (client) נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

חבר כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו יוצרת את הקישור בקצב 10Gbps המשמש לתקשורת מהירה בין הצמתים.

### 1. קביעת ממשקי הרשת

בכל מכונה, מצא את שם ממשק הרשת שלה ורשום אותו (הוא ייקרא בהמשך ההוראות `IFNAME`). הרץ:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות קישור הרשת

ודא שהקישור פעיל ורץ במהירות מלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

עליך לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור אינו עולה, בדוק את חיבור הכבל וודא שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור ידנית; עיין בתיעוד המתג שברשותך.

## הרחבת הקצאת VRAM

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

### תצורת זיכרון להרצת מודלים גדולים

בלינוקס, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת עמוד ה-Translation Table Manager (TTM) של הליבה, על פי ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5 GB).

* התקן את כלי pipx והוסף את הנתיב לחבילות (wheels) המותקנות על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקן את חבילת amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הרץ את כלי amd-ttm כדי לשאול את ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדר מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

## אתחול מכולת (container) vLLM

> **הערה**: השלם שלב זה הן על מכונה 1 והן על מכונה 2.

מערכת ה-Ryzen AI Halo שברשותך מגיעה עם vLLM ארוז בתוך תמונת מכולה (container image) בנויה מראש, שאותה אתה מריץ באמצעות Podman, כלי מכולות (container) חופשי וקוד פתוח.

### 1. יצירת ספריית הורדת המודל

כאשר אתה מגיש (serve) את מודל Qwen3.5-397B במדריך זה, vLLM יוריד באופן אוטומטי את משקלי המודל למערכת שלך. כדי לוודא שמשקלים אלה נגישים מתוך המכולה, צור תחילה ספריית models שהמכולה יכולה להעמיס (mount):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. הפעלת מכולת vLLM

הפקודה שלהלן מפעילה את המכולה ומכניסה אותך למעטפת (shell) אינטראקטיבית. היא מעמיסה (mounts) את ספריית ה-models שיצרת זה עתה ומעבירה את ה-`IFNAME` שלך אל `NCCL_SOCKET_IFNAME` ו-`GLOO_SOCKET_IFNAME`, ומודיעה ל-RCCL (הספרייה ש-vLLM משתמש בה כדי לתאם GPUs על פני האשכול) איזה ממשק להשתמש.

הפעל את המכולה עם:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

## הרצת המודל על האשכול (cluster)

vLLM משתמש ב-Ray כדי לתאם את האשכול וב-RCCL כדי לטפל בתקשורת בין GPUs לבין GPUs על פני צמתים. מכונה אחת פועלת כ**צומת הראש** (head node) (מכונה 1), ומתאמת את ההסקה. המכונה השנייה מצטרפת כ**צומת עובד** (worker node) (מכונה 2), ותורמת את זיכרון ה-GPU וכוח החישוב שלה.

> **הערה**: Ray היא תלות אופציונלית עבור vLLM וזמינה רק מתוך מכולת ה-Podman המוגדרת מראש.

בעת ההפעלה, vLLM מפצל (shards) את המודל על פני שני הצמתים באמצעות מקביליות טנזורית (tensor parallelism). לאחר הטעינה, ההסקה ממשיכה כאילו רצה על מאיץ בודד.

#### מניעת שגיאות OOM של Ray

כברירת מחדל, Ray מנטר את זיכרון המארח בכל צומת וממית את התהליך הגדול ביותר כאשר השימוש בזיכרון חוצה את סף ה-95%. במערכת ה-Ryzen™ AI Halo שברשותך, ה-GPU והמארח חולקים מאגר זיכרון אחד, כך שטעינת מודל עלולה לגרום ל-`ray.exceptions.OutOfMemoryError` ולהמית את תהליך העובד.

כדי למנוע זאת, נייצא (export) את `RAY_memory_monitor_refresh_ms=0` בכל מכונה לפני ההפעלה וההצטרפות לאשכול.
### שלב 1: הפעלת צומת הראש של Ray (מכונה 1)

במכונה 1, הפעילו את צומת הראש של Ray כדי לאתחל את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 2: הצטרפות לאשכול (מכונה 2)

במכונה 2, התחברו לצומת הראש כדי ליצור את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **איתור `<MACHINE_2_IP>`**: במכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 3: הגשת המודל (מכונה 1)

במכונה 1, הפעילו את שרת vLLM. פעולה זו תוריד באופן אוטומטי את המודל ותתחיל להגיש אותו בשני הצמתים:

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

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `--port` | הפורט שדרכו מוגש ה-API של HTTP |
| `--host` | כתובת ה-IP שאליה השרת מקושר (`0.0.0.0` עבור כל הממשקים) |
| `--max-model-len` | אורך ההקשר המקסימלי בטוקנים |
| `--gpu-memory-utilization` | החלק היחסי של זיכרון ה-GPU להקצאה (0.0–1.0) |
| `--dtype` | סוג הנתונים למשקלי המודל |
| `--tensor-parallel-size` | מספר ה-GPU-ים לחלוקת המודל ביניהם (יש להגדיר לפי סך ה-GPU-ים באשכול) |
| `--distributed-executor-backend` | הבאקנד להרצה מרובת-צמתים (`ray` עבור פריסות אשכול) |
| `--enforce-eager` | משבית קומפילציה של CUDA graph לצורך תאימות |
| `--language-model-only` | מדלג על טעינת רכיבי מודל עזר (למשל, מקודד ראייה) |
| `--reasoning-parser` | מפעיל ניתוח פלט חשיבה מובנה עבור המודל |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## גישה למודל

vLLM חושף API תואם OpenAI, כך שניתן לחבר כל לקוח או ממשק תואם לאשכול שלכם. אפשרות פופולרית אחת היא [Open WebUI](https://github.com/open-webui/open-webui), המספקת ממשק צ'אט מבוסס דפדפן.

כדי לחבר את Open WebUI לנקודת הקצה של vLLM שלכם:

1. פתחו **Settings** > **Admin Panel** > **Connections**
2. לחצו על ה-**+** ליד **Manage OpenAI API Connections**
3. הגדירו את **Connection Type** ל-**External**
4. הגדירו את **URL** ל-`http://<MACHINE_1_IP>:7000/v1`
5. תחת **Auth**, בחרו **None** מהתפריט הנפתח
6. השאירו את **Model IDs** ריק כדי לגלות אוטומטית את כל המודלים מנקודת הקצה

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה. אם ניגשים ל-Open WebUI ממכונה 1 עצמה, ניתן להשתמש ב-`http://localhost:7000/v1`.

![הגדרות חיבור Open WebUI עבור נקודת הקצה של vLLM](assets/openwebui-connection.png)

לאחר ההתחברות, בחרו את המודל מתפריט המודלים הנפתח ב-Open WebUI והתחילו לשוחח. המודל פועל כעת בשני צמתי Ryzen AI Halo שלכם:

![שיחה עם Qwen3.5-397B ב-Open WebUI](assets/openwebui-chat.png)

## הצעדים הבאים

- **חקרו מודלים נוספים**: גלו מודלים חדשים ב-[Hugging Face](https://huggingface.co/models?&sort=trending) שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחיבו לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי Ray נוספים כדי לחלק מודלים בין עוד יותר GPU-ים. פעולה זו דורשת מתג Ethernet עם לפחות ארבעה יציאות, אחת לכל צומת. בצעו את [שלב 2: הצטרפות לאשכול](#step-2-join-the-cluster-machine-2) בכל עובד נוסף והגדילו את `--tensor-parallel-size` בהתאם
- **נסו אסטרטגיות מקביליות נוספות**: vLLM תומך ב[מקביליות מומחים](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) עבור מודלים מסוג mixture-of-experts וב[מקביליות נתונים](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) לתפוקה גבוהה יותר. נסו את `--enable-expert-parallel` ו-`--data-parallel-size` כדי למצוא את התצורה הטובה ביותר לעומס העבודה שלכם