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

**AMD Sync** הופך את המחשב הנייד שלך לתא טייס מרוחק עבור ה-AMD Ryzen™ AI Halo. דלגו על הגדרת SSH, מפתחות ו-IDE הידנית — התקינו את AMD Sync וקבלו גישה בלחיצה אחת למסוף מרוחק, VS Code, JupyterLab, ולוח מחוונים חי של GPU/CPU/זיכרון על ה-Ryzen AI Halo.

המחשב המקומי שלכם נשאר מוכר; כל פקודה, מחברת, ומודל פועלים על ה-Ryzen AI Halo.

> **טיפ**: עמוד זה יכיל כל עדכון חדש ל-AMDSync.

## מה תלמדו

- הפעלת SSH על ה-Ryzen AI Halo והתחברות אליו מ-AMD Sync
- הפעלת VS Code, מסוף, JupyterLab, ומדדים חיים מול ה-Ryzen AI Halo בלחיצה אחת
- ארגון עבודה מרוחקת באמצעות תיקיות הפרויקטים המנוהלות של AMD Sync

---

## מושגי יסוד

ל-AMD Sync שני צדדים: **לקוח** (המחשב הנייד שלכם, שמריץ את אפליקציית AMD Sync) ו-**שרת** (ה-Ryzen AI Halo, שמריץ שרת SSH ש-AMD Sync חופר לתוכו מנהרה). כל דבר שאתם מפעילים מ-AMD Sync — VS Code, מסוף, מחברת — נפתח מקומית אך פועל על ה-Ryzen AI Halo.

> **לקוחות נתמכים:** Windows 11 ו-Linux. macOS אינו נתמך.

---

## שלב 1 — הפעלת SSH על ה-Ryzen AI Halo

> **הערה:** ב-Windows, ה-Ryzen AI Halo מגיע עם שרת SSH *כבוי כברירת מחדל*. ב-Linux, הוא מגיע עם שרת SSH *מופעל כברירת מחדל*.

1. על ה-Ryzen AI Halo, פתחו את **AMD Ryzen™ AI Developer Center**.
2. עברו ללשונית **Remote**.
3. הפעילו את **SSH Server**.
4. שימו לב ל-**IP Address**, **Port**, ו-**Username** המוצגים תחת **Server Information** — תזדקקו להדביק אותם ל-AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **הערה:** זהו AMD Developer Center עבור Windows. גרסת Linux עשויה להיראות אחרת ב-UI, אך בעלת פונקציונליות מרוחקת דומה.

> **טיפ:** AMD Sync מבקש את **סיסמת ההתחברות של מערכת ההפעלה** של אותו משתמש, לא סיסמה מ-Developer Center.

---

## שלב 2 — התקנת AMD Sync על הלקוח שלכם

AMD Sync פועל על Windows 11 ו-Linux. הורידו את המתקין עבור מערכת ההפעלה שלכם, ולאחר מכן פעלו לפי השלבים שלהלן. לאחר ההתקנה, לחצו על **Accept & Install** במסך **Get Started** — AMD Sync ייפתח אוטומטית בסיום.

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

> **הערה:** מרכז האפליקציות של Ubuntu עשוי לסמן קובץ `.deb` שנפתח מקומית כ-*"פוטנציאלית לא בטוח."* זוהי האזהרה הרגילה עבור כל מתקין צד-שלישי מקומי. אם לחיצה כפולה על ה-`.deb` נכשלת, השתמשו בפקודת המסוף שלעיל.

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
| **Password** | סיסמת ההתחברות של מערכת ההפעלה שלכם — מוסתרת בעת ההקלדה |

לחצו על **Add Device**. לאחר מסך טעינה קצר, תראו **"Connection Successful"** ותגיעו לתצוגת הבית, שנמצאת במגש המערכת שלכם. לחצו מחוץ לחלון כדי לסגור אותו; AMD Sync ממשיך לפעול ונמצא במרחק לחיצה אחת.

> **אם ההתחברות נכשלת,** AMD Sync חוזר לטופס עם הערכים שלכם שמורים. הסיבות הנפוצות הן ש-SSH מבוטל על ה-Ryzen AI Halo, סיסמה שגויה, או ששני המכשירים נמצאים ברשתות שונות.

---

## שלב 4 — הפעלת הכלי המרוחק הראשון שלכם

תצוגת הבית מספקת חמישה רכיבים בלחיצה אחת — כולם זמינים ללא קשר לאיזו מערכת הפעלה הלקוח וה-Ryzen AI Halo פועלים עליה.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| רכיב | מה הוא עושה |
|-----------|--------------|
| **Directory** | בוחר את התיקייה על ה-Ryzen AI Halo שבה VS Code, מסוף, ו-JupyterLab ייפתחו. ברירת המחדל היא סביבת עבודה מנוהלת `Documents/AMD_Sync`. |
| **VS Code** | פותח את VS Code מקומית עם מנהרת SSH לתוך התיקייה שנבחרה. |
| **Terminal** | פותח מסוף מקומי המחובר ב-SSH ל-Ryzen AI Halo, בתיקייה שנבחרה. |
| **JupyterLab** | מפעיל פרויקט מחברת מחובר ב-SSH ל-Ryzen AI Halo, מוגבל לתיקייה שנבחרה. |
| **Live Metrics** | תצוגה בזמן אמת של ניצול GPU, זיכרון, ו-CPU על ה-Ryzen AI Halo. |

### נסו את VS Code

בהפעלה הראשונה שלכם, נסו את **VS Code**.

1. השאירו את **Directory** על ברירת המחדל `~/Documents/AMD_Sync`.
2. לחצו על **VS Code**.
3. AMD Sync יוצר את `Documents/AMD_Sync/Project_1` על ה-Ryzen AI Halo ופותח את VS Code מקומית, במנהרה לתוכו.

כעת אתם עורכים קבצים שנמצאים על ה-Ryzen AI Halo עם הגדרת VS Code המקומית שלכם. צרו את `helloworld.py`, הוסיפו `print("hello world")`, פתחו את המסוף המשולב (`` Ctrl + ` ``), והריצו אותו:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

שורת הסטטוס מציגה **SSH: Linux** — הוכחה שהקוד שלכם פועל על ה-Ryzen AI Halo, לא על המחשב הנייד שלכם.
### נסו את הטרמינל

לחצו על **Terminal** כדי לגשת לאותה תיקייה דרך SSH מבלי להרים את הידיים מהמקלדת.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

ב-Windows, הטרמינל שברירת המחדל שלו הוא **PowerShell** — עברו ל-**Windows Command Prompt** מתפריט ההגדרות אם תעדיפו זאת. ב-Linux, AMD Sync משתמש בטרמינל המערכת שברירת המחדל שלכם.

---

## איך התיקייה עובדת

תפריט הנפתח **Directory** הוא הפקד החשוב ביותר ב-AMD Sync — הוא קובע היכן ינחת כל כלי שתפעילו ב-Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (ברירת מחדל)** — הפעלת VS Code או JupyterLab מכאן יוצרת אוטומטית תיקיית פרויקט חדשה (`Project_1`, `Project_2`, … עבור VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … עבור JupyterLab).
- **תיקיות פרויקט קיימות** — כל תת-תיקייה ישירה של `AMD_Sync` (כולל תיקיות שיצרתם ידנית ב-Ryzen AI Halo) מופיעה בתפריט הנפתח. התיקייה האחרונה שבה השתמשתם הופכת לברירת המחדל בפעם הבאה.
- **נתיבים מותאמים אישית** — הקלידו כל נתיב מוחלט כדי לפתוח תיקייה במקום אחר ב-Ryzen AI Halo. AMD Sync רק *פותח* אותה — הוא לא ייצור תיקיות מחוץ ל-`AMD_Sync`, ונתיבים מותאמים אישית אינם נשמרים בין הפעלות.

אם נתיב מותאם אישית לא עובד, AMD Sync יודיע לכם מדוע: תחביר לא תקין, התיקייה לא קיימת, או שהנתיב מצביע לקובץ.

---

## מדדים חיים ו-JupyterLab

- **Live Metrics** — לוח מחוונים חי של שימוש ב-GPU, זיכרון ו-CPU. הדרך המהירה ביותר לוודא שהרצת אימון מרוחקת אכן פוגעת בחומרה.
- **JupyterLab** — פרויקט מחברת מלא המחובר דרך SSH ל-Ryzen AI Halo, עם טרמינל משולב משלו לשילוב תאי מחברת ופקודות מעטפת מבלי לצאת מהממשק.

---

## הגדרות והתקנים מרובים

לתפריט **Settings** יש שלושה כרטיסיות:

| כרטיסייה | מה היא כוללת |
|-----|----------------|
| **Devices** | מציג רשימה של כל התקן Ryzen AI Halo שהתחברתם אליו בהצלחה. התחברו מחדש, ערכו פרטי גישה, או הוסיפו התקן חדש. |
| **Information** | קישורים לתיעוד ולתמיכת פורום. |
| **Customize** | מיקום מחדש של האפליקציה על שולחן העבודה, החלפת סוג הטרמינל (Windows בלבד), ובדיקת עדכונים עבור AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **סוג טרמינל (Windows)** — בחרו בין **PowerShell** (ברירת מחדל) ל-**Windows Command Prompt**.
- **סוג טרמינל (Linux)** — זמין רק טרמינל המערכת שברירת המחדל.
- **עדכוני אפליקציה** — כרטיסייה זו היא המקום הנכון לבדוק ולהתקין גרסאות חדשות של AMD Sync מתוך הממשק; אין צורך במעדכן נפרד.

> התקן יופיע תחת **Devices** רק לאחר חיבור ראשון מוצלח, כך שניסיונות כושלים לא יעמיסו על הרשימה.

---

## פתרון בעיות

- **החיבור נכשל מיד** — ודאו ששרת ה-SSH מופעל בכרטיסייה **Remote** במרכז המפתחים (Developer Center) של Ryzen AI Halo.
- **שגיאת סיסמה שגויה** — השתמשו ב**סיסמת ההתחברות למערכת ההפעלה** שלכם ב-Ryzen AI Halo, ולא בסיסמאות שנלקחו ממרכז המפתחים.
- **לחצן VS Code לא עושה כלום** — התקינו את VS Code במחשב הלקוח שלכם מתוך [code.visualstudio.com](https://code.visualstudio.com).
- **סמל המגש של AMD Sync חסר (Linux/GNOME)** — התקינו והפעילו את הרחבת AppIndicator.
- **קובץ `.deb` לא נפתח ממנהל הקבצים** — השתמשו בפקודה `sudo apt install ./AMDSyncInstaller.deb` מטרמינל.
- **תהליך ההגדרה מופיע מחדש בכל הפעלה (Linux)**: פתחו את מחזיק המפתחות (keyring) של ההתחברות שלכם, או הפעילו עם `--password-store=gnome-libsecret`, ולאחר מכן בצעו את ההגדרה מחדש פעם אחת.