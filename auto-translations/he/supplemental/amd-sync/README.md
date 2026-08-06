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

**AMD Sync** הופך את המחשב הנייד שלך לעמדת בקרה מרוחקת עבור AMD Ryzen™ AI Halo. דלג על הגדרת SSH, מפתחות ו-IDE ידנית — התקן את AMD Sync וקבל גישה בלחיצה אחת למסוף מרוחק, VS Code,‏ JupyterLab, ולוח מחוונים חי של GPU/CPU/זיכרון על ה-Ryzen AI Halo.

המחשב המקומי שלך נשאר מוכר; כל פקודה, מחברת (notebook) ומודל פועלים על ה-Ryzen AI Halo.

> **טיפ**: עמוד זה יכיל כל עדכון חדש ל-AMDSync.

## מה תלמד

- הפעלת SSH על ה-Ryzen AI Halo והתחברות אליו מ-AMD Sync
- הפעלת VS Code, מסוף, JupyterLab ומדדים חיים (Live Metrics) מול ה-Ryzen AI Halo בלחיצה אחת
- ארגון עבודה מרוחקת באמצעות תיקיות הפרויקטים המנוהלות של AMD Sync

---

## מושגי יסוד

ל-AMD Sync שני צדדים: **לקוח** (המחשב הנייד שלך, שבו רץ אפליקציית AMD Sync) ו**שרת** (ה-Ryzen AI Halo, שבו רץ שרת SSH ש-AMD Sync יוצר אליו מנהרה (tunnel)). כל דבר שתפעיל מ-AMD Sync — VS Code, מסוף, מחברת — נפתח מקומית אך פועל על ה-Ryzen AI Halo.

> **לקוחות נתמכים:** Windows 11 ו-Linux. macOS אינה נתמכת.

---

## שלב 1 — הפעלת SSH על ה-Ryzen AI Halo


> **הערה:** ב-Windows, ה-Ryzen AI Halo מגיע עם שרת SSH *כבוי כברירת מחדל*. ב-Linux, הוא מגיע עם שרת SSH *מופעל כברירת מחדל*.

1. על ה-Ryzen AI Halo, פתח את **AMD Ryzen™ AI Developer Center**.
2. עבור לכרטיסייה **Remote**.
3. הפעל את **SSH Server**.
4. שים לב ל-**IP Address**,‏ **Port** ו-**Username** המוצגים תחת **Server Information** — תזדקק להם כדי להדביק אותם ב-AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **הערה:** זהו AMD Developer Center עבור Windows. גרסת ה-Linux עשויה להיות בעלת ממשק שונה, אך עם פונקציונליות מרוחקת דומה.

> **טיפ:** AMD Sync מבקש את **סיסמת הכניסה למערכת ההפעלה** של אותו משתמש, לא סיסמה מה-Developer Center.

---

## שלב 2 — התקנת AMD Sync על הלקוח שלך

AMD Sync פועל על Windows 11 ו-Linux. הורד את קובץ ההתקנה עבור מערכת ההפעלה שלך, ולאחר מכן פעל לפי השלבים למטה. לאחר ההתקנה, לחץ על **Accept & Install** במסך **Get Started** — AMD Sync ייפתח אוטומטית עם סיום ההתקנה.

### Windows

[הורדת AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. לחץ פעמיים על `AMDSyncInstaller.exe`.
2. לחץ על **Accept & Install**.

> אם חומת האש של Windows מציגה הודעה, אפשר ל-AMD Sync גישה לרשת כדי שיוכל להגיע אל ה-Ryzen AI Halo דרך SSH.

### Linux

לחץ על הקישור להורדת הפורמט המועדף עליך:

| פורמט | הורדה | פקודת התקנה |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **הערה:** מרכז האפליקציות של Ubuntu עשוי לסמן קובץ `.deb` שנפתח מקומית כ-*"עלול להיות לא בטוח."* זוהי אזהרה סטנדרטית עבור כל מתקין מקומי של צד שלישי. אם לחיצה כפולה על ה-`.deb` נכשלת, השתמש בפקודת המסוף שלמעלה.

---

## שלב 3 — התחברות אל ה-Ryzen AI Halo שלך

בהפעלה הראשונה, AMD Sync מציג את הטופס **Add a Remote Device**. מלא אותו לפי הערכים מכרטיסיית **Remote** ב-Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| שדה | הערות |
|-------|-------|
| **Device Name** *(אופציונלי)* | תווית ידידותית כמו `Ryzen AI Halo`. ברירת המחדל היא `Device 1`,‏ `Device 2`, וכן הלאה. |
| **Hostname or IP** | מהכרטיסייה Remote |
| **SSH Port** | מהכרטיסייה Remote (מספרים בלבד) |
| **Username** | שם חשבון מערכת ההפעלה שלך על ה-Ryzen AI Halo |
| **Password** | סיסמת הכניסה למערכת ההפעלה שלך — מוסתרת בעת ההקלדה |

לחץ על **Add Device**. לאחר מסך טעינה קצר, תראה **"Connection Successful"** ותגיע למסך הבית, השוכן במגש המערכת (system tray) שלך. לחץ מחוץ לחלון כדי לסגור אותו; AMD Sync ימשיך לפעול ויהיה זמין בלחיצה אחת.

> **אם החיבור נכשל,** AMD Sync חוזר לטופס עם הערכים שהזנת שמורים. הסיבות הנפוצות הן ש-SSH מושבת על ה-Ryzen AI Halo, סיסמה שגויה, או שני המכשירים נמצאים ברשתות שונות.

---

## שלב 4 — הפעלת הכלי המרוחק הראשון שלך

מסך הבית מציע חמישה רכיבים בלחיצה אחת — כולם זמינים ללא קשר למערכת ההפעלה שבה פועלים הלקוח וה-Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| רכיב | מה הוא עושה |
|-----------|--------------|
| **Directory** | בוחר את התיקייה על ה-Ryzen AI Halo שבה ייפתחו VS Code, Terminal ו-JupyterLab. ברירת המחדל היא סביבת עבודה מנוהלת בשם `Documents/AMD_Sync`. |
| **VS Code** | פותח VS Code מקומית עם מנהרת SSH אל התיקייה שנבחרה. |
| **Terminal** | פותח מסוף מקומי מחובר ב-SSH אל ה-Ryzen AI Halo, בתיקייה שנבחרה. |
| **JupyterLab** | מפעיל פרויקט מחברת מחובר ב-SSH אל ה-Ryzen AI Halo, מוגבל לתיקייה שנבחרה. |
| **Live Metrics** | תצוגה בזמן אמת של ניצול GPU, זיכרון ו-CPU על ה-Ryzen AI Halo. |

### נסה את VS Code

בהפעלה הראשונה שלך, נסה את **VS Code**.

1. השאר את **Directory** בברירת המחדל `~/Documents/AMD_Sync`.
2. לחץ על **VS Code**.
3. AMD Sync יוצר `Documents/AMD_Sync/Project_1` על ה-Ryzen AI Halo ופותח את VS Code מקומית, כשהוא מוצפן במנהרה אליו.

כעת אתה עורך קבצים ששוכנים על ה-Ryzen AI Halo באמצעות הגדרת VS Code המקומית שלך. צור `helloworld.py`, הוסף `print("hello world")`, פתח את המסוף המשולב (`` Ctrl + ` ``), והרץ אותו:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

שורת הסטטוס מציגה **SSH: Linux** — הוכחה לכך שהקוד שלך רץ על ה-Ryzen AI Halo, לא על המחשב הנייד שלך.
### נסה את הטרמינל

לחץ על **Terminal** כדי לעבור לאותה תיקייה דרך SSH מבלי להרים את הידיים מהמקלדת.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

ב-Windows, הטרמינל המוגדר כברירת מחדל הוא **PowerShell** — עבור אל **Windows Command Prompt** מתפריט ההגדרות אם אתה מעדיף. ב-Linux, AMD Sync משתמש בטרמינל המערכת המוגדר כברירת מחדל.

---

## כיצד פועלת הספרייה

התפריט הנפתח **Directory** הוא הבקרה החשובה ביותר ב-AMD Sync — היא קובעת היכן ייחת כל כלי שתפעיל על ה-Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (ברירת מחדל)** — הפעלת VS Code או JupyterLab מכאן יוצרת תיקיית פרויקט חדשה באופן אוטומטי (`Project_1`, `Project_2`, ... עבור VS Code; `Notebook_Project_1`, `Notebook_Project_2`, ... עבור JupyterLab).
- **תיקיות פרויקט קיימות** — כל תיקיית משנה ישירה של `AMD_Sync` (כולל תיקיות שיצרת ידנית על ה-Ryzen AI Halo) מופיעה בתפריט הנפתח. התיקייה האחרונה שבה השתמשת הופכת לברירת המחדל בפעם הבאה.
- **נתיבים מותאמים אישית** — הקלד כל נתיב מוחלט כדי לפתוח תיקייה במקום אחר על ה-Ryzen AI Halo. AMD Sync רק *פותח* אותה — הוא לא ייצור תיקיות מחוץ ל-`AMD_Sync`, ונתיבים מותאמים אישית לא נשמרים בין הפעלות.

אם נתיב מותאם אישית לא עובד, AMD Sync יודיע לך מדוע: תחביר לא תקין, התיקייה לא קיימת, או שהנתיב מצביע על קובץ.

---

## מדדים חיים ו-JupyterLab

- **Live Metrics** — לוח מחוונים חי של שימוש ב-GPU, זיכרון ו-CPU. הדרך המהירה ביותר לוודא שריצת אימון מרוחקת אכן פוגעת בחומרה.
- **JupyterLab** — פרויקט מחברת מלא המחובר ב-SSH ל-Ryzen AI Halo, עם טרמינל משולב משלו לשילוב תאי מחברת ופקודות מעטפת מבלי לצאת מהממשק.

---

## הגדרות ומכשירים מרובים

לתפריט **Settings** יש שלושה כרטיסיות:

| כרטיסייה | מה היא כוללת |
|-----|----------------|
| **Devices** | מציגה רשימה של כל Ryzen AI Halo שהתחברת אליו בהצלחה. התחבר מחדש, ערוך פרטי גישה, או הוסף מכשיר חדש. |
| **Information** | קישורים לתיעוד ותמיכת פורום. |
| **Customize** | הצב מחדש את האפליקציה בשולחן העבודה שלך, החלף את סוג הטרמינל (Windows בלבד), ובדוק עדכונים ל-AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **סוג טרמינל (Windows)** — בחר בין **PowerShell** (ברירת מחדל) ל-**Windows Command Prompt**.
- **סוג טרמינל (Linux)** — זמין רק טרמינל המערכת המוגדר כברירת מחדל.
- **עדכוני אפליקציה** — כרטיסייה זו היא המקום הנכון לבדוק ולהתקין גרסאות חדשות של AMD Sync מתוך הממשק; אין צורך בכלי עדכון נפרד.

> מכשיר יופיע תחת **Devices** רק לאחר חיבור ראשון מוצלח, כך שניסיונות כושלים לא יעמיסו על הרשימה.

---

## פתרון בעיות

- **החיבור נכשל מיידית** — ודא ששרת ה-SSH מופעל בכרטיסייה **Remote** ב-Developer Center של ה-Ryzen AI Halo.
- **שגיאת סיסמה שגויה** — השתמש ב**סיסמת ההתחברות למערכת ההפעלה** שלך ב-Ryzen AI Halo, לא בסיסמאות שנלקחו מ-Developer Center.
- **כפתור VS Code לא עושה כלום** — התקן את VS Code על מחשב הלקוח שלך מ-[code.visualstudio.com](https://code.visualstudio.com).
- **סמל המגש של AMD Sync חסר (Linux/GNOME)** — התקן והפעל את הרחבת AppIndicator.
- **קובץ ה-`.deb` לא נפתח ממנהל הקבצים** — השתמש בפקודה `sudo apt install ./AMDSyncInstaller.deb` מתוך טרמינל.

---