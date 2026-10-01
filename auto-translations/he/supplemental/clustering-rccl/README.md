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

# צירוף שני מכשירי Ryzen™ AI Halo לאשכול באמצעות RCCL

## סקירה כללית

מכשיר ה-Ryzen™ AI Halo שברשותך כבר מסוגל להריץ מודלי שפה גדולים באופן מקומי. צירוף לאשכול (Clustering) לוקח זאת צעד קדימה, על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומאפשר לך גישה למודלים גדולים אף יותר, עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית מעמיקה יותר - הכול לחלוטין על החומרה שלך.

מדריך זה מלמד אותך כיצד לצרף לאשכול שתי מערכות Ryzen AI Halo באמצעות RCCL‏ (ROCm Communication Collectives Library) עם vLLM, ולהריץ את Qwen3.5-397B, מודל בעל 397 מיליארד פרמטרים, על פני שתי המכונות עם האצת ROCm.

## מה תלמד/י

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- הפעלת vLLM עם תמיכת ROCm
- הגדרת RCCL להסקה מקבילית-טנזורית (tensor-parallel) מרובת-צמתים על פני שתי מערכות Ryzen AI Halo
- הרצת מודל בעל 397 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo מקושרות ברשת

## דרישות מקדימות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב (star topology) כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet‏ 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין מספר צמתי Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שתי יחידות ה-Ryzen AI Halo. יציאה שלישית נדרשת אם ניגשים למודל ממחשב לקוח נפרד במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: יש להשלים שלב זה גם במכונה 1 וגם במכונה 2.

חברו כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו מקימה את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.

### 1. קביעת ממשקי הרשת

בכל מכונה, מצאו את שם ממשק הרשת שלה ורשמו אותו (הוא יכונה בהמשך ההוראות `IFNAME`). הריצו:

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

> **הערה**: יש להחליף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אמורה להופיע מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהקישור לא עולה, בדקו את חיבור הכבל וודאו שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים כיבוי משא ומתן אוטומטי (auto-negotiation) והגדרת מהירות הקישור באופן ידני; עיינו בתיעוד המתג שלכם.

## הרחבת הקצאת VRAM

> **הערה**: יש להשלים שלב זה גם במכונה 1 וגם במכונה 2.

### הגדרת זיכרון להרצת מודלים גדולים

ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת דפי ה-Translation Table Manager (TTM) של הליבה (kernel), לפי ההוראות הבאות. AMD ממליצה להגדיר בביוס (BIOS) מינימום VRAM ייעודי (0.5GB).

* התקינו את כלי ה-pipx והוסיפו את הנתיב עבור wheels המותקנים על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקינו את ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הריצו את הכלי amd-ttm כדי לשאול לגבי ההגדרות הנוכחיות של זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדירו מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* אתחלו את המערכת מחדש כדי שהשינויים ייכנסו לתוקף.

## אתחול קונטיינר vLLM

> **הערה**: יש להשלים שלב זה גם במכונה 1 וגם במכונה 2.

מכשיר ה-Ryzen AI Halo שברשותך מגיע עם vLLM ארוז בתוך תמונת קונטיינר (container image) בנויה מראש, אותה מריצים באמצעות Podman, כלי קונטיינרים חופשי וקוד פתוח.

### 1. יצירת תיקיית הורדת המודל

כאשר תגישו (serve) את מודל Qwen3.5-397B במדריך זה, vLLM יוריד באופן אוטומטי את משקלי המודל למערכת שלכם. כדי לוודא שמשקלים אלה נגישים מתוך הקונטיינר, יש ליצור תחילה תיקיית models שהקונטיינר יוכל לחבר (mount):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. הפעלת קונטיינר ה-vLLM

הפקודה שלהלן מפעילה את הקונטיינר ומכניסה אתכם למעטפת (shell) אינטראקטיבית. היא מחברת (mount) את תיקיית ה-models שיצרתם זה עתה, ומעבירה את ה-`IFNAME` שלכם ל-`NCCL_SOCKET_IFNAME` ול-`GLOO_SOCKET_IFNAME`, ומודיעה ל-RCCL (הספרייה בה vLLM משתמש כדי לתאם GPUs על פני האשכול) איזה ממשק להשתמש בו.

הפעילו את הקונטיינר עם:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **הערה**: יש להחליף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

## הרצת המודל על האשכול

vLLM משתמש ב-Ray כדי לתזמר (orchestrate) את האשכול וב-RCCL כדי לטפל בתקשורת GPU-ל-GPU בין הצמתים. מכונה אחת פועלת כ**צומת ראשי** (head node) (מכונה 1), ומתאמת את ההסקה. המכונה השנייה מצטרפת כ**צומת עובד** (worker node) (מכונה 2), ותורמת את זיכרון ה-GPU וכוח החישוב שלה.

> **הערה**: Ray היא תלות אופציונלית עבור vLLM וזמינה רק מתוך קונטיינר ה-Podman המוגדר מראש.

בעת ההפעלה, vLLM מפצל (shards) את המודל על פני שני הצמתים באמצעות מקביליות טנזורית (tensor parallelism). לאחר הטעינה, ההסקה ממשיכה כאילו רצה על מאיץ יחיד.

#### מניעת שגיאות OOM ב-Ray

כברירת מחדל, Ray עוקב אחר זיכרון המארח (host memory) בכל צומת וממית את התהליך הגדול ביותר כאשר השימוש בזיכרון חוצה 95%. במכשיר ה-Ryzen™ AI Halo שלכם, ה-GPU והמארח חולקים מאגר זיכרון אחד, כך שטעינת מודל עלולה להפעיל `ray.exceptions.OutOfMemoryError` ולהמית את תהליך העובד (worker).

כדי למנוע זאת, נייצא (export) את `RAY_memory_monitor_refresh_ms=0` בכל מכונה לפני התחלת ההצטרפות לאשכול.
### שלב 1: הפעלת צומת הראש של Ray (מכונה 1)

במכונה 1, הפעל את צומת הראש של Ray כדי לאתחל את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 2: הצטרפות לאשכול (מכונה 2)

במכונה 2, התחבר לצומת הראש כדי ליצור את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **איתור `<MACHINE_2_IP>`**: במכונה 2, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 3: הגשת המודל (מכונה 1)

במכונה 1, הפעל את שרת vLLM. פעולה זו תוריד באופן אוטומטי את המודל ותתחיל להגיש אותו בשני הצמתים:

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
| `--port` | הפורט להגשת ה-API של HTTP |
| `--host` | כתובת ה-IP שאליה ישויך השרת (`0.0.0.0` עבור כל הממשקים) |
| `--max-model-len` | אורך ההקשר המרבי באסימונים |
| `--gpu-memory-utilization` | החלק מזיכרון ה-GPU שיוקצה (0.0–1.0) |
| `--dtype` | סוג הנתונים עבור משקלי המודל |
| `--tensor-parallel-size` | מספר ה-GPU-ים שעליהם יפוצל המודל (יש להגדיר לפי סך ה-GPU-ים באשכול) |
| `--distributed-executor-backend` | ה-Backend להרצה מבוזרת בין צמתים (`ray` עבור פריסות אשכול) |
| `--enforce-eager` | משבית קומפילציה של CUDA graph לצורך תאימות |
| `--language-model-only` | מדלג על טעינת רכיבי מודל נלווים (למשל, מקודד חזותי) |
| `--reasoning-parser` | מאפשר ניתוח מובנה של פלט חשיבה עבור המודל |

לשימוש מלא בפרמטרים, עיין ב[תיעוד vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## גישה למודל

vLLM חושף API תואם OpenAI, כך שתוכל לחבר כל לקוח או ממשק תואם לאשכול שלך. אפשרות פופולרית אחת היא [Open WebUI](https://github.com/open-webui/open-webui), המספקת ממשק צ'אט מבוסס דפדפן.

כדי לחבר את Open WebUI לנקודת הקצה של vLLM שלך:

1. פתח את **Settings** > **Admin Panel** > **Connections**
2. לחץ על **+** ליד **Manage OpenAI API Connections**
3. הגדר את **Connection Type** ל-**External**
4. הגדר את **URL** ל-`http://<MACHINE_1_IP>:7000/v1`
5. תחת **Auth**, בחר **None** מהתפריט הנפתח
6. השאר את **Model IDs** ריק כדי לגלות אוטומטית את כל המודלים מנקודת הקצה

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה. אם ניגשים ל-Open WebUI ממכונה 1 עצמה, ניתן להשתמש ב-`http://localhost:7000/v1`.

![הגדרות חיבור Open WebUI עבור נקודת הקצה של vLLM](assets/openwebui-connection.png)

לאחר החיבור, בחר את המודל מהתפריט הנפתח של המודלים ב-Open WebUI והתחל לשוחח. המודל פועל כעת בשני צמתי Ryzen AI Halo שלך:

![שיחה עם Qwen3.5-397B ב-Open WebUI](assets/openwebui-chat.png)

## הצעדים הבאים

- **גלה מודלים נוספים**: גלה מודלים חדשים ב-[Hugging Face](https://huggingface.co/models?&sort=trending) המתאימים לזיכרון ה-GPU המשולב של האשכול שלך
- **הרחבה לארבעה צמתים**: הוסף שתי מערכות Ryzen AI Halo נוספות כעובדי Ray נוספים כדי לפצל מודלים בין עוד יותר GPU-ים. פעולה זו דורשת מתג Ethernet עם לפחות ארבעה פורטים, אחד לכל צומת. עקוב אחר [שלב 2: הצטרפות לאשכול](#step-2-join-the-cluster-machine-2) בכל עובד נוסף והגדל את `--tensor-parallel-size` בהתאם
- **נסה אסטרטגיות מקבילות נוספות**: vLLM תומך ב-[מקביליות מומחים](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) עבור מודלים מסוג mixture-of-experts וב-[מקביליות נתונים](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) עבור תפוקה גבוהה יותר. נסה את `--enable-expert-parallel` ו-`--data-parallel-size` כדי למצוא את התצורה הטובה ביותר לעומס העבודה שלך