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

# צירוף בענן (Clustering) של שני מחשבי Ryzen™ AI Halo באמצעות RCCL

## סקירה כללית

מחשב ה-Ryzen™ AI Halo שברשותך כבר מסוגל להריץ מודלי שפה גדולים באופן מקומי. צירוף בענן (Clustering) לוקח זאת צעד קדימה, על ידי שילוב זיכרון ה-GPU של מספר מערכות דרך רשת מקומית, ומעניק לך גישה למודלים גדולים אף יותר, בעלי יכולות היסק חזקות יותר, יצירת קוד טובה יותר, והבנה רב-לשונית עמוקה יותר — הכול על גבי החומרה שלך בלבד.

מדריך זה מלמד אותך כיצד לצרף שני מחשבי Ryzen AI Halo בענן (cluster) באמצעות RCCL‏ (ROCm Communication Collectives Library) עם vLLM, ולהריץ את Qwen3.5-397B, מודל בעל 397 מיליארד פרמטרים, על פני שתי המכונות עם האצת ROCm.

## מה תלמד

- כיצד להרחיב את הקצאת ה-VRAM במערכות Ryzen AI Halo
- הפעלת vLLM עם תמיכת ROCm
- הגדרת RCCL עבור היסק מקבילי-טנזור (tensor-parallel) מרובה צמתים בין שתי מערכות Ryzen AI Halo
- הרצת מודל בעל 397 מיליארד פרמטרים על פני שתי מערכות Ryzen AI Halo המחוברות ברשת

## דרישות מוקדמות

### חומרה

מדריך זה דורש שתי יחידות Ryzen AI Halo ומתג Ethernet אחד, המחוברים בטופולוגיית כוכב (star topology), כאשר כל יחידה מחוברת ישירות למתג.

| רכיב | כמות | תיאור |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | צמתי חישוב היוצרים את האשכול (cluster) |
| מתג Ethernet בקצב 10Gbps | 1 | מתג מרכזי המאפשר תקשורת בין מספר צמתי Ryzen AI Halo (לפחות 2 יציאות) |
| כבל Ethernet | 2 | מחבר כל יחידת Halo למתג (מומלץ Cat 7 ומעלה) |

> **הערה**: נדרשות שתי יציאות מתג Ethernet כדי לחבר את שתי יחידות ה-Ryzen AI Halo. נדרשת יציאה שלישית אם ניגשים למודל ממחשב לקוח נפרד במקום מאחת מיחידות ה-Halo.

### תוכנה
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## הגדרת החומרה הפיזית

> **הערה**: יש לבצע שלב זה הן במכונה 1 והן במכונה 2.

חבר כל יחידת Ryzen AI Halo למתג ה-Ethernet באמצעות כבל Cat 7 (או גבוה יותר). פעולה זו יוצרת את קישור ה-10Gbps המשמש לתקשורת מהירה בין הצמתים.

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

ודא שהקישור פעיל ופועל במהירות המלאה על ידי בדיקת מהירות הממשק שלך:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מתוך [1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

אמור להופיע קצב של `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **הערה**: אם הקצב נמוך מ-`10000Mb/s` או שהקישור אינו פעיל, בדוק את חיבור הכבל וודא שיציאת המתג מוגדרת ל-10Gbps. חלק מהמתגים דורשים ביטול משא ומתן אוטומטי (auto-negotiation) והגדרה ידנית של מהירות הקישור; עיין בתיעוד המתג שלך.

## הרחבת הקצאת ה-VRAM

> **הערה**: יש לבצע שלב זה הן במכונה 1 והן במכונה 2.

### תצורת זיכרון להרצת מודלים גדולים

ב-Linux, ROCm משתמש במאגר זיכרון מערכת משותף, ומאגר זה מוגדר כברירת מחדל למחצית מזיכרון המערכת.

ניתן להגדיל כמות זו על ידי שינוי הגדרת דפי מנהל טבלת התרגום (Translation Table Manager - TTM) של הליבה, בעזרת ההוראות הבאות. AMD ממליצה להגדיר את מינימום ה-VRAM הייעודי ב-BIOS (0.5 GB).

* התקן את כלי השירות pipx והוסף את הנתיב עבור חבילות wheel שהותקנו על ידי pipx לנתיב החיפוש של המערכת.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* התקן את חבילת ה-wheel של amd-debug-tools מ-PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* הרץ את הכלי amd-ttm כדי לבצע שאילתה על ההגדרות הנוכחיות של הזיכרון המשותף.
  ```bash
  amd-ttm
  ```

* הגדר מחדש את הגדרות הזיכרון המשותף ל-**120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* הפעל מחדש את המערכת כדי שהשינויים ייכנסו לתוקף.

## אתחול מיכל vLLM

> **הערה**: יש לבצע שלב זה הן במכונה 1 והן במכונה 2.

מחשב ה-Ryzen AI Halo שברשותך מגיע עם vLLM ארוז בתוך תמונת מיכל (container image) בנויה מראש, אותה אתה מריץ באמצעות Podman, כלי מיכלים חינמי בקוד פתוח.

### 1. יצירת תיקיית הורדת המודל

כאשר תגיש (serve) את מודל Qwen3.5-397B במדריך זה, vLLM יוריד אוטומטית את משקלי המודל למערכת שלך. כדי לוודא שמשקלים אלה נגישים מתוך המיכל, צור תחילה תיקיית models שהמיכל יוכל לצרף (mount):

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. הפעלת מיכל ה-vLLM

הפקודה שלמטה מפעילה את המיכל ומעבירה אותך לשורת פקודה אינטראקטיבית. היא מצרפת (mount) את תיקיית ה-models שיצרת זה עתה, ומעבירה את ה-`IFNAME` שלך אל `NCCL_SOCKET_IFNAME` ו-`GLOO_SOCKET_IFNAME`, ומודיעה ל-RCCL (הספרייה בה vLLM משתמש לתיאום GPUs על פני האשכול) איזה ממשק להשתמש בו.

הפעל את המיכל עם:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **הערה**: החלף את `<IFNAME>` בשם ממשק הפלט מתוך [1. קביעת ממשקי הרשת](#1-determine-network-interfaces)

## הרצת המודל על האשכול

vLLM משתמש ב-Ray לתזמור (orchestrate) האשכול וב-RCCL לטיפול בתקשורת GPU-to-GPU בין הצמתים. מכונה אחת פועלת בתור **צומת הראש** (Machine 1), ומתאמת את ההיסק. המכונה האחרת מצטרפת כ**צומת עובד** (Machine 2), ותורמת את זיכרון ה-GPU והכוח החישובי שלה.

> **הערה**: Ray היא תלות אופציונלית עבור vLLM וזמינה רק מתוך מיכל ה-Podman המוגדר מראש.

בעת ההפעלה, vLLM מפצל את המודל בין שני הצמתים באמצעות מקביליות טנזור (tensor parallelism). לאחר הטעינה, ההיסק ממשיך כאילו הוא רץ על מאיץ יחיד.

### שלב 1: הפעלת צומת הראש של Ray (מכונה 1)

במכונה 1, הפעל את צומת הראש של Ray כדי לאתחל את האשכול:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הרץ `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.
### שלב 2: הצטרפות לאשכול (מכונה 2)

במכונה 2, התחברו לצומת הראשי (head node) כדי ליצור את האשכול:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **איתור `<MACHINE_2_IP>`**: במכונה 2, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה.

### שלב 3: הגשת המודל (מכונה 1)

במכונה 1, הפעילו את שרת vLLM. פעולה זו תוריד את המודל באופן אוטומטי ותתחיל להגיש אותו על פני שני הצמתים:

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
| `--host` | כתובת ה-IP שאליה השרת ייקשר (`0.0.0.0` עבור כל הממשקים) |
| `--max-model-len` | אורך ההקשר המרבי בטוקנים |
| `--gpu-memory-utilization` | חלק זיכרון ה-GPU להקצאה (0.0–1.0) |
| `--dtype` | סוג הנתונים עבור משקלי המודל |
| `--tensor-parallel-size` | מספר ה-GPU-ים שעליהם יחולק המודל (הגדירו לסך כל ה-GPU-ים באשכול) |
| `--distributed-executor-backend` | מנוע אחורי (backend) עבור ביצוע רב-צמתי (`ray` עבור פריסות אשכול) |
| `--enforce-eager` | משבית קומפילציית CUDA graph לצורך תאימות |
| `--language-model-only` | מדלג על טעינת רכיבי מודל עזר (למשל, מקודד ראייה) |
| `--reasoning-parser` | מפעיל פענוח פלט חשיבה מובנה עבור המודל |

לשימוש מלא בפרמטרים, עיינו ב[תיעוד vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## גישה למודל

vLLM חושף API תואם-OpenAI, כך שניתן לחבר כל לקוח או ממשק תואם לאשכול שלכם. אפשרות פופולרית אחת היא [Open WebUI](https://github.com/open-webui/open-webui), המספקת ממשק צ'אט מבוסס דפדפן.

כדי לחבר את Open WebUI לנקודת הקצה של vLLM שלכם:

1. פתחו **Settings** > **Admin Panel** > **Connections**
2. לחצו על ה-**+** ליד **Manage OpenAI API Connections**
3. הגדירו את **Connection Type** ל-**External**
4. הגדירו את **URL** ל-`http://<MACHINE_1_IP>:7000/v1`
5. תחת **Auth**, בחרו **None** מהתפריט הנפתח
6. השאירו את **Model IDs** ריק כדי לגלות אוטומטית את כל המודלים מנקודת הקצה

> **איתור `<MACHINE_1_IP>`**: במכונה 1, הריצו `hostname -I | awk '{print $1}'` כדי למצוא את כתובת ה-IP המקומית שלה. אם ניגשים ל-Open WebUI ממכונה 1 עצמה, ניתן להשתמש ב-`http://localhost:7000/v1`.

![הגדרות חיבור Open WebUI עבור נקודת הקצה של vLLM](assets/openwebui-connection.png)

לאחר החיבור, בחרו את המודל מתפריט המודלים הנפתח ב-Open WebUI והתחילו לשוחח. המודל פועל כעת על פני שני צמתי ה-Ryzen AI Halo שלכם:

![שיחה עם Qwen3.5-397B ב-Open WebUI](assets/openwebui-chat.png)

## הצעדים הבאים

- **גלו מודלים נוספים**: גלו מודלים חדשים ב-[Hugging Face](https://huggingface.co/models?&sort=trending) שמתאימים לזיכרון ה-GPU המשולב של האשכול שלכם
- **הרחיבו לארבעה צמתים**: הוסיפו שתי מערכות Ryzen AI Halo נוספות כעובדי Ray נוספים כדי לחלק מודלים על פני GPU-ים רבים אף יותר. פעולה זו דורשת מתג Ethernet עם לפחות ארבעה יציאות, אחת עבור כל צומת. בצעו את [שלב 2: הצטרפות לאשכול](#step-2-join-the-cluster-machine-2) בכל עובד נוסף והגדילו את `--tensor-parallel-size` בהתאם
- **נסו אסטרטגיות מקבילות אחרות**: vLLM תומכת ב[מקביליות מומחים](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) עבור מודלים מסוג mixture-of-experts וב[מקביליות נתונים](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) עבור תפוקה גבוהה יותר. נסו את `--enable-expert-parallel` ואת `--data-parallel-size` כדי למצוא את התצורה הטובה ביותר עבור העומס שלכם