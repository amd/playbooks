<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# פיתוח מרחוק עם AMD Sync

## סקירה כללית

**AMD Sync** הופך את המחשב הנייד שלך לתא טייס מרוחק עבור AMD Ryzen™ AI Halo. דלג על הגדרת SSH, מפתחות וסביבת פיתוח ידנית — התקן את AMD Sync וקבל גישה בלחיצה אחת לטרמינל מרוחק, VS Code, JupyterLab ולוח מחוונים חי של GPU/CPU/זיכרון על ה-Ryzen AI Halo.

המחשב המקומי שלך נשאר מוכר; כל פקודה, מחברת ומודל רצים על ה-Ryzen AI Halo.

> **טיפ**: דף זה יכיל כל עדכון חדש ל-AMDSync.

## מה תלמד

- הפעלת SSH על ה-Ryzen AI Halo וחיבור אליו מ-AMD Sync
- הפעלת VS Code, Terminal, JupyterLab ומדדים חיים מול ה-Ryzen AI Halo בלחיצה אחת
- ארגון עבודה מרחוק באמצעות תיקיות פרויקט מנוהלות של AMD Sync

---

## מושגי יסוד

ל-AMD Sync שני צדדים: **לקוח** (המחשב הנייד שלך, שמריץ את אפליקציית AMD Sync) ו**שרת** (ה-Ryzen AI Halo, שמריץ שרת SSH שאליו AMD Sync מתחבר במנהרה). כל מה שאתה מפעיל מ-AMD Sync — VS Code, טרמינל, מחברת — נפתח מקומית אך מתבצע על ה-Ryzen AI Halo.

> **לקוחות נתמכים:** Windows 11 ו-Linux. macOS אינו נתמך.

---

## שלב 1 — הפעלת SSH על ה-Ryzen AI Halo


> **הערה:** ב-Windows, ה-Ryzen AI Halo מגיע עם שרת SSH *כבוי כברירת מחדל*. ב-Linux, הוא מגיע עם שרת SSH *פעיל כברירת מחדל*.

1. על ה-Ryzen AI Halo, פתח את **AMD Ryzen™ AI Developer Center**.
2. עבור ללשונית **Remote**.
3. הפעל את **SSH Server**.
4. שים לב ל**כתובת IP**, ל**פורט** ול**שם המשתמש** המוצגים תחת **Server Information** — תדביק אותם ב-AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **הערה:** זהו AMD Developer Center עבור Windows. זה של Linux עשוי להיות בעל ממשק שונה, אך פונקציונליות מרחוק דומה.

> **טיפ:** AMD Sync מבקש את **סיסמת הכניסה למערכת ההפעלה** של אותו משתמש, לא סיסמה מה-Developer Center.

---

## שלב 2 — התקנת AMD Sync על הלקוח שלך

AMD Sync פועל על Windows 11 ו-Linux. הורד את תוכנית ההתקנה עבור מערכת ההפעלה שלך, ולאחר מכן עקוב אחר השלבים הבאים. לאחר ההתקנה, לחץ על **Accept & Install** במסך **Get Started** — AMD Sync מופעל אוטומטית כשהוא מסיים.

### Windows

[הורד AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. לחץ פעמיים על `AMDSyncInstaller.exe`.
2. לחץ על **Accept & Install**.

> אם חומת האש של Windows מבקשת ממך אישור, אפשר ל-AMD Sync גישה לרשת כדי שיוכל להגיע ל-Ryzen AI Halo דרך SSH.

### Linux

לחץ על הקישור להורדת הפורמט המועדף עליך:

| פורמט | הורדה | פקודת התקנה |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **הערה:** מרכז האפליקציות של Ubuntu עשוי לסמן קובץ `.deb` שנפתח מקומית כ*"עלול להיות לא בטוח."* זוהי האזהרה הסטנדרטית לכל תוכנית התקנה מקומית של צד שלישי. אם לחיצה כפולה על קובץ ה-`.deb` נכשלת, השתמש בפקודת הטרמינל שלמעלה.

---

## שלב 3 — חיבור ל-Ryzen AI Halo שלך

בהפעלה הראשונה, AMD Sync מציג את טופס **Add a Remote Device**. מלא אותו באמצעות הערכים מלשונית **Remote** של Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| שדה | הערות |
|-------|-------|
| **Device Name** *(אופציונלי)* | תווית ידידותית כמו `Ryzen AI Halo`. ברירת המחדל היא `Device 1`, `Device 2`, … |
| **Hostname or IP** | מלשונית Remote |
| **SSH Port** | מלשונית Remote (מספרים בלבד) |
| **Username** | שם חשבון מערכת ההפעלה שלך על ה-Ryzen AI Halo |
| **Password** | סיסמת הכניסה למערכת ההפעלה שלך — מוסתרת בעת ההקלדה |

לחץ על **Add Device**. לאחר מסך טעינה קצר, תראה **"Connection Successful"** ותגיע לתצוגת הבית, שנמצאת במגש המערכת שלך. לחץ מחוץ לחלון כדי לסגור אותו; AMD Sync ממשיך לפעול ונגיש בלחיצה אחת.

> **אם החיבור נכשל,** AMD Sync חוזר לטופס עם הערכים שלך שמורים. הסיבות הנפוצות הן SSH מושבת על ה-Ryzen AI Halo, סיסמה שגויה, או שני המכשירים נמצאים ברשתות שונות.

---

## שלב 4 — הפעלת הכלי המרוחק הראשון שלך

תצוגת הבית מעניקה לך חמישה רכיבים בלחיצה אחת — כולם זמינים ללא קשר לאיזו מערכת הפעלה הלקוח וה-Ryzen AI Halo מריצים.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| רכיב | מה הוא עושה |
|-----------|--------------|
| **Directory** | בוחר את התיקייה על ה-Ryzen AI Halo שבה VS Code, Terminal ו-JupyterLab ייפתחו. ברירת המחדל היא סביבת עבודה מנוהלת `Documents/AMD_Sync`. |
| **VS Code** | פותח את VS Code מקומית עם מנהרת SSH לתיקייה הנבחרת. |
| **Terminal** | פותח טרמינל מקומי המחובר ב-SSH ל-Ryzen AI Halo, בתיקייה הנבחרת. |
| **JupyterLab** | מפעיל פרויקט מחברת המחובר ב-SSH ל-Ryzen AI Halo, בהיקף התיקייה הנבחרת. |
| **Live Metrics** | תצוגה בזמן אמת של ניצול GPU, זיכרון ו-CPU על ה-Ryzen AI Halo. |

### נסה את VS Code

להפעלה הראשונה שלך, נסה את **VS Code**.

1. השאר את **Directory** על ברירת המחדל `~/Documents/AMD_Sync`.
2. לחץ על **VS Code**.
3. AMD Sync יוצר את `Documents/AMD_Sync/Project_1` על ה-Ryzen AI Halo ופותח את VS Code מקומית, במנהרה אליו.

כעת אתה עורך קבצים שנמצאים על ה-Ryzen AI Halo עם הגדרת VS Code המקומית שלך. צור `helloworld.py`, הוסף `print("hello world")`, פתח את הטרמינל המשולב (`` Ctrl + ` ``), והרץ אותו:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

שורת הסטטוס מציגה **SSH: Linux** — הוכחה שהקוד שלך רץ על ה-Ryzen AI Halo, לא על המחשב הנייד שלך.

### נסה את הטרמינל

לחץ על **Terminal** כדי להיכנס לאותה תיקייה דרך SSH מבלי לעזוב את המקלדת.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

ב-Windows, הטרמינל ברירת המחדל הוא **PowerShell** — עבור ל-**Windows Command Prompt** מתפריט ההגדרות אם אתה מעדיף. ב-Linux, AMD Sync משתמש בטרמינל ברירת המחדל של המערכת שלך.

---

## כיצד Directory עובד

הרשימה הנפתחת **Directory** היא הפקד החשוב ביותר ב-AMD Sync — היא קובעת היכן כל כלי שאתה מפעיל נוחת על ה-Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (ברירת מחדל)** — הפעלת VS Code או JupyterLab מכאן יוצרת תיקיית פרויקט חדשה אוטומטית (`Project_1`, `Project_2`, … עבור VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … עבור JupyterLab).
- **תיקיות פרויקט קיימות** — כל ילד ישיר של `AMD_Sync` (כולל תיקיות שאתה יוצר ידנית על ה-Ryzen AI Halo) מופיע ברשימה הנפתחת. התיקייה האחרונה שהשתמשת בה הופכת לברירת המחדל בפעם הבאה.
- **נתיבים מותאמים אישית** — הקלד כל נתיב מוחלט כדי לפתוח תיקייה במקום אחר על ה-Ryzen AI Halo. AMD Sync רק *פותח* אותה — הוא לא יצור תיקיות מחוץ ל-`AMD_Sync`, ונתיבים מותאמים אישית אינם נשמרים בין הפעלות.

אם נתיב מותאם אישית אינו עובד, AMD Sync יודיע לך מדוע: תחביר לא חוקי, התיקייה אינה קיימת, או שהנתיב מצביע על קובץ.

---

## Live Metrics ו-JupyterLab

- **Live Metrics** — לוח מחוונים חי של ניצול GPU, זיכרון ו-CPU. הדרך המהירה ביותר לאשר שריצת אימון מרחוק אכן פוגעת בחומרה.
- **JupyterLab** — פרויקט מחברת מלא המחובר ב-SSH ל-Ryzen AI Halo, עם טרמינל משולב משלו לשילוב תאי מחברת ופקודות מעטפת מבלי לעזוב את הממשק.

---

## הגדרות ומכשירים מרובים

לתפריט **Settings** שלושה לשוניות:

| לשונית | מה היא מכסה |
|-----|----------------|
| **Devices** | מפרטת כל Ryzen AI Halo שהתחברת אליו בהצלחה. התחבר מחדש, ערוך אישורים, או הוסף מכשיר חדש. |
| **Information** | קישורים לתיעוד ותמיכה בפורום. |
| **Customize** | שנה את מיקום האפליקציה על שולחן העבודה שלך, החלף סוג טרמינל (Windows בלבד), ובדוק עדכוני AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **סוג טרמינל (Windows)** — בחר בין **PowerShell** (ברירת מחדל) ו-**Windows Command Prompt**.
- **סוג טרמינל (Linux)** — רק טרמינל ברירת המחדל של המערכת זמין.
- **עדכוני אפליקציה** — לשונית זו היא המקום הנכון לבדוק ולהתקין גרסאות חדשות של AMD Sync מתוך הממשק; אין צורך בכלי עדכון נפרד.

> מכשיר מופיע תחת **Devices** רק לאחר חיבור ראשון מוצלח, כך שניסיונות כושלים לא יעמיסו על הרשימה.

---

## פתרון בעיות

- **החיבור נכשל מיד** — אשר שה-SSH server מופעל בלשונית **Remote** של ה-Ryzen AI Halo ב-Developer Center.
- **שגיאת סיסמה שגויה** — השתמש ב**סיסמת הכניסה למערכת ההפעלה** שלך על ה-Ryzen AI Halo, לא בסיסמאות מה-Developer Center.
- **כפתור VS Code לא עושה כלום** — התקן את VS Code על מחשב הלקוח שלך מ-[code.visualstudio.com](https://code.visualstudio.com).
- **סמל מגש AMD Sync חסר (Linux/GNOME)** — התקן והפעל את תוסף AppIndicator.
- **`.deb` לא נפתח ממנהל הקבצים** — השתמש ב-`sudo apt install ./AMDSyncInstaller.deb` מטרמינל.

---