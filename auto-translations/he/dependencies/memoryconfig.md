<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

עבור Ryzen AI Halo, זיכרון ה-GPU הייעודי מוגדר כברירת מחדל ל-64GB, שמספיק לרוב העומסים. עבור מודלים גדולים יותר או הקשרים ארוכים יותר, הגדלת הערך ל-96GB עשויה לעזור. כדי לבצע התאמה, פתחו את **AMD Software: Adrenalin Edition™** ונווטו אל **Performance → Tuning → AMD Variable Graphics Memory**. הפעילו מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

כדי לשנות את ערך זיכרון ה-GPU הייעודי, פתחו את **AMD Software: Adrenalin Edition™** ונווטו אל **Performance → Tuning → AMD Variable Graphics Memory**. הפעילו מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

ב-Linux, כדי להריץ מודלים גדולים יותר, הגדילו את מאגר **הזיכרון המשותף** הזמין ל-GPU. פעולה זו עשויה לדרוש הגדרת זיכרון ה-GPU הייעודי ב-BIOS למינימום, כדי שניתן יהיה למקסם את מאגר הזיכרון המשותף.

<!-- @device:halo_box -->

עבור AMD Ryzen™ AI Halo, ברירת המחדל היא 96GB משותפים. כדי לשנות זאת, פתחו את **AMD Ryzen™ AI Developer Center** ועברו ללשונית **Settings**. תחת **Graphics Performance Settings**, הגדילו את המחוון **Shared Video Memory**, לאחר מכן לחצו על **Apply Changes** והפעילו מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

הגדילו את מאגר הזיכרון המשותף על ידי שינוי הגדרת ה-page של Translation Table Manager (TTM) של הקרנל. AMD ממליצה להגדיר את ה-VRAM הייעודי המינימלי ב-BIOS (0.5 GB) כדי שהכמות המקסימלית תהיה זמינה כזיכרון משותף.

1. התקינו את הכלי `pipx` והוסיפו את הנתיב עבור ה-wheels המותקנים באמצעות pipx לנתיב החיפוש של המערכת:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. התקינו את ה-wheel של `amd-debug-tools` מ-PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. בצעו שאילתה על הגדרות הזיכרון המשותף הנוכחיות:

   ```bash
   amd-ttm
   ```

4. הגדילו את הקצאת הזיכרון המשותף (יחידות ב-GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. הפעילו מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<!-- @device:end -->

<!-- @os:end -->