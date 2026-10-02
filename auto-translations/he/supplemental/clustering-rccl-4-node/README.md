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

# אשכול של ארבעה Ryzen™ AI Halo עם RCCL

## סקירה כללית

מערכת ה-Ryzen™ AI Halo שלך כבר מסוגלת להריץ מודלי שפה גדולים באופן מקומי. אשכול (clustering) לוקח את זה צעד נוסף קדימה על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, מה שמעניק לך גישה למודלים גדולים אף יותר עם יכולות הסקה חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית עמוקה יותר, הכול לחלוטין על החומרה שלך.

מדריך זה מלמד אותך כיצד ליצור אשכול של ארבע מערכות Ryzen AI Halo באמצעות RCCL (ROCm Communication Collectives Library) עם vLLM, ולהריץ את Qwen3.5-397B, מודל בעל 397 מיליארד פרמטרים, על פני ארבע המכונות עם האצת ROCm.

## מה תלמד

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- הפעלת vLLM עם תמיכת ROCm
- הגדרת RCCL להסקה מקבילית-טנזורית (tensor-parallel) מרובת-צמתים על פני ארבע מערכות Ryzen AI Halo
- הרצת מודל בעל 397 מיליארד פרמטרים על פני ארבע מערכות Ryzen AI Halo מחוברות לרשת

## דרישות מוקדמות

### חומרה

מדריך זה דורש ארבע יחידות Ryzen AI Halo ומתג Ethernet אחד, מחוברים בטופולוגיית כוכב (star topology) כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | צמתי חישוב המרכיבים את האשכול |
| מתג Ethernet בעל 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין יחידות Ryzen AI Halo מרובות (לפחות 4 יציאות) |
| כבל Ethernet | 4 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות ארבע יציאות מתג Ethernet כדי לחבר את ארבע יחידות ה-Ryzen AI Halo. יציאה חמישית נדרשת אם אתה ניגש למודל ממכונת לקוח נפרדת במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## הגדרת חומרה פיזית

> **הערה**: השלם שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

חבר כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). זה מקים את חיבור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.

### 1. קביעת ממשקי הרשת

בכל מכונה, מצא את שם ממשק הרשת שלה ורשום אותו (הוא יכונה בהמשך ההוראות בשם `IFNAME`). הרץ:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

פקודה זו מדפיסה את שם הממשק ישירות, לדוגמה:

```bash
enp191s0
```

### 2. אימות מהירויות חיבור הרשת

ודא שהחיבור פעיל ופועל במהירות מלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אתה אמור לראות מהירות של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם המהירות נמוכה מ-`10000Mb/s` או שהחיבור אינו עולה, בדוק את חיבור הכבל וודא שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים השבתה של משא ומתן אוטומטי (auto-negotiation) והגדרה ידנית של מהירות החיבור; עיין בתיעוד של המתג שלך.

## הרחבת הקצאת ה-VRAM

> **הערה**: השלם שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

### תצורת זיכרון להרצת מודלים גדולים

ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת העמוד של Translation Table Manager (TTM) של הקרנל, לפי ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5 GB).

* התקן את כלי השירות pipx והוסף את הנתיב עבור חבילות wheel המותקנות על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקן את חבילת ה-wheel amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הרץ את הכלי amd-ttm כדי לשאול את ההגדרות הנוכחיות עבור זיכרון משותף.
  ```bash
  amd-ttm
  ```

* הגדר מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

## אתחול מכולת vLLM

> **הערה**: השלם שלב זה בכל ארבע המכונות (מכונה 1 עד מכונה 4).

מערכת ה-Ryzen AI Halo שלך מגיעה עם vLLM ארוז בתוך תמונת מכולה (container image) בנויה מראש, שאותה אתה מריץ באמצעות Podman, כלי מכולות חינמי בקוד פתוח.

### 1. יצירת תיקיית הורדת המודל

כאשר אתה משרת את המודל Qwen3.5-397B במדריך זה, vLLM יוריד באופן אוטומטי את משקלי המודל למערכת שלך. כדי לוודא שמשקלים אלו נגישים מתוך המכולה, צור תחילה תיקיית models שהמכולה יכולה לעגן (mount):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. הפעלת מכולת ה-vLLM

הפקודה שלהלן מפעילה את המכולה ומכניסה אותך למעטפת (shell) אינטראקטיבית. היא מעגנת את תיקיית ה-models שיצרת זה עתה ומעבירה את ה-`IFNAME` שלך ל-`NCCL_SOCKET_IFNAME` ול-`GLOO_SOCKET_IFNAME`, ובכך מודיעה ל-RCCL (הספרייה ש-vLLM משתמשת בה לתיאום GPU-ים על פני האשכול) באיזה ממשק להשתמש.

הפעל את המכולה עם:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מ-[1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

## הרצת המודל על האשכול

vLLM משתמש ב-Ray לתזמור האשכול וב-RCCL לטיפול בתקשורת GPU-ל-GPU בין צמתים. מכונה אחת משמשת כצומת הראשי (head node) (מכונה 1), ומתאמת את ההסקה. שלוש האחרות מצטרפות כצמתי עובד (worker nodes) (מכונות 2, 3, ו-4), ותורמות את זיכרון ה-GPU והעיבוד שלהן.

> **הערה**: Ray היא תלות אופציונלית עבור vLLM וזמינה רק מתוך מכולת ה-Podman המוגדרת מראש.

בעת ההפעלה, vLLM מפצל (shards) את המודל על פני כל ארבעת הצמתים באמצעות מקביליות טנזורית (tensor parallelism). לאחר הטעינה, ההסקה ממשיכה כאילו היא פועלת על מאיץ יחיד.

#### מניעת שגיאות OOM של Ray

כברירת מחדל, Ray מנטר את זיכרון המארח (host memory) בכל צומת וממיתה את התהליך הגדול ביותר כאשר השימוש בזיכרון חוצה 95%. במערכת ה-Ryzen™ AI Halo שלך, ה-GPU והמארח חולקים מאגר זיכרון אחד, כך שטעינת מודל עלולה לגרום ל-`ray.exceptions.OutOfMemoryError` ולהמית את תהליך העובד (worker).

כדי למנוע זאת, נייצא את `RAY_memory_monitor_refresh_ms=0` בכל מכונה לפני תחילת ההפעלה וההצטרפות לאשכול.
### שלב 1: הפעלת צומת הראש של Ray (מכונה 1)

במכונה 1, הפעילו את צומת הראש של Ray כדי לאתחל את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 2: הצטרפות לאשכול (מכונות 2, 3 ו-4)

בכל אחת ממכונות 2, 3 ו-4, התחברו לצומת הראש כדי ליצור את האשכול:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **איתור `<MACHINE_N_IP>`**: בכל מכונת עובד, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 3: הגשת המודל (מכונה 1)

במכונה 1, הפעילו את שרת vLLM. פעולה זו תוריד אוטומטית את המודל ותתחיל להגיש אותו על פני כל ארבעת הצמתים:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### מדריך פרמטרים

| דגל | מטרה |
|------|---------|
| `--port` | הפורט לשירות ה-API של ה-HTTP |
| `--host` | כתובת ה-IP שאליה יקושר השרת (`0.0.0.0` עבור כל הממשקים) |
| `--max-model-len` | אורך ההקשר המרבי בטוקנים |
| `--gpu-memory-utilization` | החלק של זיכרון ה-GPU להקצאה (0.0–1.0) |
| `--dtype` | סוג הנתונים עבור משקלי המודל |
| `--tensor-parallel-size` | מספר כרטיסי ה-GPU שעליהם יפוצל המודל (יש להגדיר לסך כל כרטיסי ה-GPU באשכול) |
| `--distributed-executor-backend` | ה-backend להרצה מרובת-צמתים (`ray` עבור פריסות אשכול) |
| `--enforce-eager` | משבית קומפילציה של CUDA graph לצורך תאימות |
| `--language-model-only` | מדלג על טעינת רכיבי מודל עזר (למשל, מקודד חזותי) |
| `--reasoning-parser` | מאפשר ניתוח פלט חשיבה מובנה עבור המודל |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## גישה למודל

vLLM חושף API תואם-OpenAI, כך שניתן לחבר כל לקוח או ממשק תואם לאשכול שלכם. אפשרות פופולרית אחת היא [Open WebUI](https://github.com/open-webui/open-webui), המספקת ממשק צ'אט מבוסס-דפדפן.

כדי לחבר את Open WebUI לנקודת הקצה של vLLM:

1. פתחו **Settings** > **Admin Panel** > **Connections**
2. לחצו על **+** ליד **Manage OpenAI API Connections**
3. הגדירו את **Connection Type** ל-**External**
4. הגדירו את **URL** ל-`http://<MACHINE_1_IP>:7000/v1`
5. תחת **Auth**, בחרו **None** מהתפריט הנפתח
6. השאירו את **Model IDs** ריק כדי לגלות אוטומטית את כל המודלים מנקודת הקצה

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה. אם ניגשים ל-Open WebUI ממכונה 1 עצמה, ניתן להשתמש ב-`http://localhost:7000/v1`.

![הגדרות חיבור Open WebUI עבור נקודת הקצה של vLLM](assets/openwebui-connection.png)

לאחר ההתחברות, בחרו את המודל מהתפריט הנפתח של המודלים ב-Open WebUI והתחילו לשוחח. המודל כעת פועל על פני כל ארבעת צמתי ה-Ryzen AI Halo שלכם:

![שיחה עם Qwen3.5-397B ב-Open WebUI](assets/openwebui-chat.png)

## הצעדים הבאים

- **גלו מודלים נוספים**: גלו מודלים חדשים ב-[Hugging Face](https://huggingface.co/models?&sort=trending) שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחיבו מעבר לארבעה צמתים**: הוסיפו מערכות Ryzen AI Halo נוספות כעובדי Ray נוספים כדי לפצל מודלים על פני עוד יותר כרטיסי GPU. בצעו את [שלב 2: הצטרפות לאשכול](#step-2-join-the-cluster-machines-2-3-and-4) בכל עובד נוסף והגדילו את `--tensor-parallel-size` בהתאם
- **נסו אסטרטגיות הקבלה נוספות**: vLLM תומך ב-[expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) עבור מודלי mixture-of-experts וב-[data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) עבור תפוקה גבוהה יותר. נסו את `--enable-expert-parallel` ו-`--data-parallel-size` כדי למצוא את התצורה הטובה ביותר עבור עומס העבודה שלכם