<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# פיתוח מרחוק עם AMD Sync

## סקירה כללית

**AMD Sync** הופך את המחשב הנייד שלכם לעמדת בקרה מרחוק עבור ה-AMD Ryzen™ AI Halo. דלגו על ההגדרה הידנית של SSH, מפתחות וה-IDE — התקינו את AMD Sync וקבלו גישה בלחיצה אחת למסוף מרוחק, VS Code, JupyterLab ולוח מחוונים חי של GPU/CPU/זיכרון על ה-Ryzen AI Halo.

המחשב המקומי שלכם נשאר מוכר; כל פקודה, מחברת ומודל רצים על ה-Ryzen AI Halo.

> **טיפ**: עמוד זה יכיל כל עדכון חדש ל-AMDSync.

## מה תלמדו

- להפעיל SSH על ה-Ryzen AI Halo ולהתחבר אליו מתוך AMD Sync
- להפעיל VS Code, Terminal, JupyterLab ו-Live Metrics מול ה-Ryzen AI Halo בלחיצה אחת
- לארגן עבודה מרחוק באמצעות תיקיות הפרויקט המנוהלות של AMD Sync

---

## מושגי יסוד

ל-AMD Sync יש שני צדדים: **לקוח** (המחשב הנייד שלכם, שמריץ את אפליקציית AMD Sync) ו**שרת** (ה-Ryzen AI Halo, שמריץ שרת SSH ש-AMD Sync יוצר אליו מנהרה). כל דבר שתפעילו מתוך AMD Sync — VS Code, מסוף, מחברת — נפתח מקומית אך פועל על ה-Ryzen AI Halo.

> **לקוחות נתמכים:** Windows 11 ו-Linux. macOS אינו נתמך.

---

## שלב 1 — הפעלת SSH על ה-Ryzen AI Halo


> **הערה:** ב-Windows, ה-Ryzen AI Halo מגיע עם שרת SSH *כבוי כברירת מחדל*. ב-Linux, הוא מגיע עם שרת SSH *פועל כברירת מחדל*.

1. על ה-Ryzen AI Halo, פתחו את **AMD Ryzen™ AI Developer Center**.
2. עברו ללשונית **Remote**.
3. הפעילו את **SSH Server**.
4. שימו לב ל-**IP Address**, **Port** ו-**Username** המוצגים תחת **Server Information** — תזדקקו להדביק אותם ב-AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **הערה:** זהו AMD Developer Center עבור Windows. גרסת Linux עשויה להיראות אחרת בממשק, אך בעלת פונקציונליות מרוחקת דומה.

> **טיפ:** AMD Sync מבקש את **סיסמת הכניסה למערכת ההפעלה** של אותו משתמש, לא סיסמה מתוך ה-Developer Center.

---

## שלב 2 — התקנת AMD Sync במכשיר הלקוח שלכם

AMD Sync פועל על Windows 11 ו-Linux. הורידו את מתקין ההתקנה עבור מערכת ההפעלה שלכם, ולאחר מכן בצעו את השלבים הבאים. לאחר ההתקנה, לחצו על **Accept & Install** במסך **Get Started** — AMD Sync יופעל אוטומטית בסיום.

### Windows

[הורדת AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. לחצו לחיצה כפולה על `AMDSyncInstaller.exe`.
2. לחצו על **Accept & Install**.

> אם Windows Firewall שואל אתכם, אשרו ל-AMD Sync גישת רשת כדי שיוכל להגיע ל-Ryzen AI Halo דרך SSH.

### Linux

לחצו על הקישור כדי להוריד את הפורמט המועדף עליכם:

| פורמט | הורדה | פקודת התקנה |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **הערה:** Ubuntu App Center עשוי לסמן קובץ `.deb` שנפתח מקומית כ-*"Potentially unsafe."* זוהי האזהרה הסטנדרטית עבור כל מתקין מקומי של צד שלישי. אם לחיצה כפולה על ה-`.deb` נכשלת, השתמשו בפקודת הטרמינל שלמעלה.

---

## שלב 3 — התחברות ל-Ryzen AI Halo שלכם

בהפעלה הראשונה, AMD Sync מציג את הטופס **Add a Remote Device**. מלאו אותו באמצעות הערכים מלשונית **Remote** ב-Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| שדה | הערות |
|-------|-------|
| **Device Name** *(אופציונלי)* | תווית ידידותית כמו `Ryzen AI Halo`. ברירת המחדל היא `Device 1`, `Device 2`, … |
| **Hostname or IP** | מלשונית Remote |
| **SSH Port** | מלשונית Remote (מספרים בלבד) |
| **Username** | שם חשבון מערכת ההפעלה שלכם על ה-Ryzen AI Halo |
| **Password** | סיסמת הכניסה למערכת ההפעלה שלכם — מוסתרת בזמן ההקלדה |

לחצו על **Add Device**. לאחר מסך טעינה קצר, תראו **"Connection Successful"** ותגיעו למסך הבית, שנמצא במגש המערכת (system tray) שלכם. לחצו מחוץ לחלון כדי לסגור אותו; AMD Sync ממשיך לפעול ונמצא במרחק לחיצה אחת.

> **אם ההתחברות נכשלת,** AMD Sync חוזר לטופס עם הערכים שהזנתם שמורים. הסיבות הנפוצות הן ש-SSH מושבת ב-Ryzen AI Halo, סיסמה שגויה, או ששני המכשירים נמצאים ברשתות שונות.

---

## שלב 4 — הפעלת הכלי המרוחק הראשון שלכם

מסך הבית מעניק לכם חמישה רכיבים בלחיצה אחת — כולם זמינים ללא תלות במערכת ההפעלה שעליה פועלים הלקוח וה-Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| רכיב | מה הוא עושה |
|-----------|--------------|
| **Directory** | בוחר את התיקייה על ה-Ryzen AI Halo שבה ייפתחו VS Code, Terminal ו-JupyterLab. ברירת המחדל היא סביבת עבודה מנוהלת `Documents/AMD_Sync`. |
| **VS Code** | פותח את VS Code מקומית עם מנהרת SSH אל התיקייה שנבחרה. |
| **Terminal** | פותח מסוף מקומי המחובר ב-SSH ל-Ryzen AI Halo, בתיקייה שנבחרה. |
| **JupyterLab** | מפעיל פרויקט מחברת המחובר ב-SSH ל-Ryzen AI Halo, בגבולות התיקייה שנבחרה. |
| **Live Metrics** | תצוגה בזמן אמת של ניצול GPU, זיכרון ו-CPU על ה-Ryzen AI Halo. |

### נסו את VS Code

להפעלה הראשונה שלכם, נסו את **VS Code**. ההוראות הבאות הן עבור Linux, אך חוויית Windows דומה.

1. השאירו את **Directory** בברירת המחדל `~/Documents/AMD_Sync`.
2. לחצו על **VS Code**.
3. AMD Sync יוצר `Documents/AMD_Sync/Project_1` על ה-Ryzen AI Halo ופותח את VS Code מקומית, עם מנהרה אליו.

כעת אתם עורכים קבצים שנמצאים על ה-Ryzen AI Halo באמצעות הגדרת VS Code המקומית שלכם. צרו `helloworld.py`, הוסיפו `print("hello world")`, פתחו את המסוף המשולב (`` Ctrl + ` ``), והריצו אותו:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

שורת הסטטוס מציגה **SSH: Linux** — הוכחה שהקוד שלכם פועל על ה-Ryzen AI Halo, לא על המחשב הנייד שלכם.
### נסה את הטרמינל

לחץ על **Terminal** כדי לעבור לאותה תיקייה דרך SSH מבלי לעזוב את המקלדת.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

ב-Windows, הטרמינל המוגדר כברירת מחדל הוא **PowerShell** — עבור ל-**Windows Command Prompt** מתפריט ההגדרות אם אתה מעדיף. ב-Linux, AMD Sync משתמש בטרמינל ברירת המחדל של המערכת שלך.

---

## כך פועל הספרייה

התפריט הנפתח **Directory** הוא הבקרה החשובה ביותר ב-AMD Sync — הוא קובע היכן כל כלי שתפעיל ינחת על ה-Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (ברירת מחדל)** — הפעלת VS Code או JupyterLab מכאן יוצרת אוטומטית תיקיית פרויקט חדשה (`Project_1`, `Project_2`, … עבור VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … עבור JupyterLab).
- **תיקיות פרויקט קיימות** — כל תיקייה שהיא צאצא ישיר של `AMD_Sync` (כולל תיקיות שיצרת ידנית על ה-Ryzen AI Halo) מופיעה בתפריט הנפתח. התיקייה האחרונה שבה השתמשת הופכת לברירת המחדל בפעם הבאה.
- **נתיבים מותאמים אישית** — הקלד כל נתיב מוחלט כדי לפתוח תיקייה במקום אחר על ה-Ryzen AI Halo. AMD Sync רק *פותח* אותה — הוא לא ייצור תיקיות מחוץ ל-`AMD_Sync`, ונתיבים מותאמים אישית לא נשמרים בין הפעלות.

אם נתיב מותאם אישית לא עובד, AMD Sync יגיד לך למה: תחביר לא תקין, התיקייה לא קיימת, או שהנתיב מצביע על קובץ.

---

## מדדים חיים ו-JupyterLab

- **Live Metrics** — לוח מחוונים חי המציג שימוש ב-GPU, זיכרון ו-CPU. הדרך המהירה ביותר לוודא שריצת אימון מרוחקת אכן פוגעת בחומרה.
- **JupyterLab** — פרויקט מחברת מלא המחובר ב-SSH אל ה-Ryzen AI Halo, עם טרמינל משולב משלו לשילוב תאי מחברת ופקודות מעטפת מבלי לעזוב את הממשק.

---

## הגדרות ומכשירים מרובים

לתפריט **Settings** שלושה לשוניות:

| לשונית | מה היא מכסה |
|-----|----------------|
| **Devices** | מציג רשימה של כל Ryzen AI Halo שאליו התחברת בהצלחה. התחבר מחדש, ערוך פרטי התחברות, או הוסף מכשיר חדש. |
| **Information** | קישורים לתיעוד ולתמיכה בפורום. |
| **Customize** | שנה את מיקום האפליקציה על שולחן העבודה שלך, החלף את סוג הטרמינל (Windows בלבד), ובדוק עדכונים ל-AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **סוג טרמינל (Windows)** — בחר בין **PowerShell** (ברירת מחדל) לבין **Windows Command Prompt**.
- **סוג טרמינל (Linux)** — זמין רק טרמינל ברירת המחדל של המערכת.
- **עדכוני אפליקציה** — זהו המקום הנכון לבדוק ולהתקין גרסאות חדשות של AMD Sync מתוך הממשק; אין צורך בכלי עדכון נפרד.

> מכשיר מופיע תחת **Devices** רק לאחר חיבור ראשון מוצלח, כך שניסיונות כושלים לא יעמיסו על הרשימה.

---

## פתרון בעיות

- **החיבור נכשל מיידית** — ודא ששרת ה-SSH מופעל בלשונית ה-**Remote** של ה-Ryzen AI Halo במרכז המפתחים.
- **שגיאת סיסמה שגויה** — השתמש בסיסמת ההתחברות של מערכת ההפעלה שלך (**OS login password**) על ה-Ryzen AI Halo, לא בסיסמאות שנלקחו ממרכז המפתחים.
- **לחצן VS Code לא עושה כלום** — התקן את VS Code במחשב הלקוח שלך מתוך [code.visualstudio.com](https://code.visualstudio.com).
- **סמל AMD Sync חסר במגש המערכת (Linux/GNOME)** — התקן והפעל את תוסף AppIndicator.
- **קובץ `.deb` לא נפתח מתוך מנהל הקבצים** — השתמש ב-`sudo apt install ./AMDSyncInstaller.deb` מתוך טרמינל.
- **מסך ההתקנה חוזר בכל הפעלה (Linux)**: בטל את נעילת טבעת המפתחות (keyring) של ההתחברות שלך, או הפעל עם `--password-store=gnome-libsecret`, ולאחר מכן בצע את ההתקנה מחדש פעם אחת.

---