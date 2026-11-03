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

# פיתוח מרוחק עם AMD Sync

## סקירה כללית

**AMD Sync** הופך את המחשב הנייד שלכם לתחנת שליטה מרוחקת עבור ה-AMD Ryzen™ AI Halo. דלגו על ההגדרה הידנית של SSH, מפתחות וסביבת פיתוח — התקינו את AMD Sync וקבלו גישה בלחיצה אחת למסוף מרוחק, VS Code, JupyterLab, ולוח מחוונים חי של GPU/CPU/זיכרון על ה-Ryzen AI Halo.

המחשב המקומי שלכם נשאר מוכר; כל פקודה, מחברת (notebook) ומודל פועלים על ה-Ryzen AI Halo.

> **טיפ**: עמוד זה יכיל עדכונים חדשים כלשהם ל-AMDSync.

## מה תלמדו

- להפעיל SSH על ה-Ryzen AI Halo ולהתחבר אליו מ-AMD Sync
- להפעיל VS Code, מסוף, JupyterLab ומדדים חיים (Live Metrics) מול ה-Ryzen AI Halo בלחיצה אחת
- לארגן עבודה מרוחקת באמצעות תיקיות הפרויקטים המנוהלות של AMD Sync

---

## מושגי יסוד

ל-AMD Sync שני צדדים: **לקוח** (client, המחשב הנייד שלכם, שמריץ את אפליקציית AMD Sync) ו-**שרת** (server, ה-Ryzen AI Halo, שמריץ שרת SSH ש-AMD Sync מבצע דרכו מנהור (tunneling)). כל דבר שאתם מפעילים מ-AMD Sync — VS Code, מסוף, מחברת (notebook) — נפתח מקומית אך פועל על ה-Ryzen AI Halo.

> **לקוחות נתמכים:** Windows 11 ו-Linux. macOS אינה נתמכת.

---

## שלב 1 — הפעלת SSH על ה-Ryzen AI Halo


> **הערה:** ב-Windows, ה-Ryzen AI Halo מגיע עם שרת ה-SSH *כבוי כברירת מחדל*. ב-Linux, הוא מגיע עם שרת ה-SSH *דלוק כברירת מחדל*.

1. על ה-Ryzen AI Halo, פתחו את **AMD Ryzen™ AI Developer Center**.
2. עברו ללשונית **Remote**.
3. הפעילו את **SSH Server**.
4. שימו לב ל-**כתובת ה-IP**, **הפורט** ו-**שם המשתמש** המוצגים תחת **Server Information** — תצטרכו להדביק אותם ב-AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **הערה:** זהו AMD Developer Center עבור Windows. הגרסה עבור Linux עשויה להיראות שונה בממשק, אך מציעה פונקציונליות מרוחקת דומה.

> **טיפ:** AMD Sync מבקש את **סיסמת ההתחברות של מערכת ההפעלה** של אותו משתמש, לא סיסמה מה-Developer Center.

---

## שלב 2 — התקנת AMD Sync במחשב הלקוח שלכם

AMD Sync פועל על Windows 11 ו-Linux. הורידו את קובץ ההתקנה עבור מערכת ההפעלה שלכם, ולאחר מכן בצעו את השלבים הבאים. לאחר ההתקנה, לחצו על **Accept & Install** במסך **Get Started** — AMD Sync יופעל אוטומטית עם סיום התהליך.

### Windows

[הורדת AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. לחצו לחיצה כפולה על `AMDSyncInstaller.exe`.
2. לחצו על **Accept & Install**.

> אם חומת האש של Windows מבקשת אישור, אפשרו ל-AMD Sync גישת רשת כדי שיוכל להגיע ל-Ryzen AI Halo דרך SSH.

### Linux

לחצו על הקישור כדי להוריד את הפורמט המועדף עליכם:

| פורמט | הורדה | פקודת התקנה |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **הערה:** מרכז האפליקציות (App Center) של Ubuntu עשוי לסמן קובץ `.deb` שנפתח מקומית כ-*"Potentially unsafe"* ("עלול להיות לא בטוח"). זוהי אזהרה סטנדרטית עבור כל תוכנת התקנה מקומית של צד שלישי. אם לחיצה כפולה על ה-`.deb` נכשלת, השתמשו בפקודת המסוף שלמעלה.

---

## שלב 3 — התחברות ל-Ryzen AI Halo שלכם

בהפעלה הראשונה, AMD Sync מציג את הטופס **Add a Remote Device**. מלאו אותו באמצעות הערכים מלשונית ה-**Remote** של ה-Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| שדה | הערות |
|-------|-------|
| **Device Name** *(אופציונלי)* | תווית ידידותית כמו `Ryzen AI Halo`. ברירת המחדל היא `Device 1`, `Device 2`, … |
| **Hostname or IP** | מלשונית ה-Remote |
| **SSH Port** | מלשונית ה-Remote (מספרים בלבד) |
| **Username** | שם חשבון מערכת ההפעלה שלכם ב-Ryzen AI Halo |
| **Password** | סיסמת ההתחברות למערכת ההפעלה שלכם — מוסתרת בעת ההקלדה |

לחצו על **Add Device**. לאחר מסך טעינה קצר, יופיע **"Connection Successful"** ותגיעו לתצוגת הבית, השוכנת במגש המערכת (system tray) שלכם. לחצו מחוץ לחלון כדי לסגור אותו; AMD Sync ימשיך לפעול ויהיה נגיש בלחיצה אחת.

> **אם החיבור נכשל,** AMD Sync יחזור לטופס עם הערכים שהזנתם שמורים. הסיבות הנפוצות הן שה-SSH מושבת ב-Ryzen AI Halo, סיסמה שגויה, או שני המכשירים נמצאים ברשתות שונות.

---

## שלב 4 — הפעלת הכלי המרוחק הראשון שלכם

תצוגת הבית מספקת חמישה רכיבים הפועלים בלחיצה אחת — כולם זמינים ללא קשר לאיזו מערכת הפעלה הלקוח וה-Ryzen AI Halo פועלים.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| רכיב | מה הוא עושה |
|-----------|--------------|
| **Directory** | בוחר את התיקייה ב-Ryzen AI Halo שבה ייפתחו VS Code, המסוף ו-JupyterLab. ברירת המחדל היא סביבת עבודה מנוהלת בשם `Documents/AMD_Sync`. |
| **VS Code** | פותח VS Code מקומית עם מנהור SSH (SSH tunnel) לתוך התיקייה שנבחרה. |
| **Terminal** | פותח מסוף מקומי המחובר דרך SSH ל-Ryzen AI Halo, בתיקייה שנבחרה. |
| **JupyterLab** | מפעיל פרויקט מחברת (notebook) המחובר דרך SSH ל-Ryzen AI Halo, מוגבל לתיקייה שנבחרה. |
| **Live Metrics** | תצוגה בזמן אמת של ניצול ה-GPU, הזיכרון וה-CPU על ה-Ryzen AI Halo. |

### נסו את VS Code

בהפעלה הראשונה שלכם, נסו את **VS Code**.

1. השאירו את **Directory** בברירת המחדל `~/Documents/AMD_Sync`.
2. לחצו על **VS Code**.
3. AMD Sync יוצר את `Documents/AMD_Sync/Project_1` על ה-Ryzen AI Halo ופותח VS Code מקומית, כשהוא ממונהר (tunneled) לתוכה.

כעת אתם עורכים קבצים השוכנים ב-Ryzen AI Halo באמצעות סביבת ה-VS Code המקומית שלכם. צרו קובץ `helloworld.py`, הוסיפו `print("hello world")`, פתחו את המסוף המשולב (`` Ctrl + ` ``), והריצו אותו:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

שורת המצב מציגה **SSH: Linux** — הוכחה לכך שהקוד שלכם רץ על ה-Ryzen AI Halo, לא על המחשב הנייד שלכם.
### נסה את הטרמינל

לחץ על **Terminal** כדי לעבור לאותה תיקייה דרך SSH מבלי לעזוב את המקלדת.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

ב-Windows, הטרמינל שמוגדר כברירת מחדל הוא **PowerShell** — עברו ל-**Windows Command Prompt** מתפריט ההגדרות אם אתם מעדיפים זאת. ב-Linux, AMD Sync משתמש בטרמינל המוגדר כברירת מחדל במערכת שלכם.

---

## כיצד פועלת התיקייה (Directory)

התפריט הנפתח **Directory** הוא הפקד החשוב ביותר ב-AMD Sync — הוא קובע היכן כל כלי שתפעילו יתמקם על ה-Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (ברירת מחדל)** — הפעלת VS Code או JupyterLab מכאן יוצרת אוטומטית תיקיית פרויקט חדשה (`Project_1`, `Project_2`, … עבור VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … עבור JupyterLab).
- **תיקיות פרויקט קיימות** — כל תיקייה שהיא ילד ישיר של `AMD_Sync` (כולל תיקיות שיצרתם ידנית ב-Ryzen AI Halo) מופיעה בתפריט הנפתח. התיקייה האחרונה בה השתמשתם הופכת לברירת המחדל בפעם הבאה.
- **נתיבים מותאמים אישית** — הקלידו כל נתיב מוחלט כדי לפתוח תיקייה במקום אחר ב-Ryzen AI Halo. AMD Sync רק *פותח* אותה — הוא לא ייצור תיקיות מחוץ ל-`AMD_Sync`, ונתיבים מותאמים אישית אינם נשמרים בין הפעלות.

אם נתיב מותאם אישית לא עובד, AMD Sync מודיע מדוע: תחביר לא תקין, התיקייה אינה קיימת, או שהנתיב מצביע על קובץ.

---

## מדדים חיים ו-JupyterLab

- **Live Metrics** — לוח מחוונים חי של ניצול GPU, זיכרון ו-CPU. הדרך המהירה ביותר לוודא שריצת אימון מרוחקת אכן פוגעת בחומרה.
- **JupyterLab** — פרויקט מחברת מלא, מחובר דרך SSH ל-Ryzen AI Halo, עם טרמינל משולב משלו לשילוב תאי מחברת ופקודות מעטפת מבלי לעזוב את הממשק.

---

## הגדרות ומספר מכשירים

בתפריט **Settings** ישנן שלוש לשוניות:

| לשונית | מה היא כוללת |
|-----|----------------|
| **Devices** | מציגה רשימה של כל מכשיר Ryzen AI Halo שהתחברתם אליו בהצלחה. התחברו מחדש, ערכו פרטי התחברות, או הוסיפו מכשיר חדש. |
| **Information** | קישורים לתיעוד ולתמיכה בפורום. |
| **Customize** | מיקום מחדש של האפליקציה על שולחן העבודה, החלפת סוג הטרמינל (Windows בלבד), ובדיקה של עדכונים ל-AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **סוג טרמינל (Windows)** — בחרו בין **PowerShell** (ברירת מחדל) ל-**Windows Command Prompt**.
- **סוג טרמינל (Linux)** — זמין רק הטרמינל המוגדר כברירת מחדל במערכת.
- **עדכוני אפליקציה** — לשונית זו היא המקום הנכון לבדוק ולהתקין גרסאות חדשות של AMD Sync מתוך הממשק; אין צורך במעדכן נפרד.

> מכשיר יופיע תחת **Devices** רק לאחר חיבור ראשון מוצלח, כך שניסיונות כושלים לא יעמיסו על הרשימה.

---

## פתרון בעיות

- **החיבור נכשל מיד** — ודאו ששרת ה-SSH מופעל בלשונית **Remote** של Ryzen AI Halo ב-Developer Center.
- **שגיאת סיסמה שגויה** — השתמשו ב**סיסמת ההתחברות למערכת ההפעלה** של Ryzen AI Halo, לא בסיסמאות שנלקחו מ-Developer Center.
- **כפתור VS Code לא עושה דבר** — התקינו את VS Code במחשב הלקוח שלכם מתוך [code.visualstudio.com](https://code.visualstudio.com).
- **סמל המגש של AMD Sync חסר (Linux/GNOME)** — התקינו והפעילו את הרחבת AppIndicator.
- **קובץ `.deb` לא נפתח ממנהל הקבצים** — השתמשו ב-`sudo apt install ./AMDSyncInstaller.deb` מתוך טרמינל.
- **מסך ההגדרה מופיע מחדש בכל הפעלה (Linux)**: שחררו את מחזיק המפתחות (keyring) של ההתחברות שלכם, או הפעילו עם `--password-store=gnome-libsecret`, ולאחר מכן בצעו את ההגדרה מחדש פעם אחת.

---