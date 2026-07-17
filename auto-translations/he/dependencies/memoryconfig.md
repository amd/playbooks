<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

עבור Ryzen AI Halo, זיכרון ה-GPU הייעודי מוגדר כברירת מחדל ל-64GB, שזה מספיק לרוב עומסי העבודה. עבור מודלים גדולים יותר או הקשרים ארוכים יותר, הגדלה ל-96GB עשויה לסייע. לכוונון, פתח את **AMD Software: Adrenalin Edition™** ונווט אל **Performance → Tuning → AMD Variable Graphics Memory**. הפעל מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

כדי לשנות את ערך זיכרון ה-GPU הייעודי, פתח את **AMD Software: Adrenalin Edition™** ונווט אל **Performance → Tuning → AMD Variable Graphics Memory**. הפעל מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

ב-Linux, כדי להריץ מודלים גדולים יותר, הגדל את מאגר **הזיכרון המשותף** הזמין ל-GPU. פעולה זו עשויה לכלול הגדרת זיכרון ה-GPU הייעודי ב-BIOS לערך המינימלי, כך שניתן יהיה למקסם את מאגר הזיכרון המשותף.

<!-- @device:halo_box -->

עבור AMD Ryzen™ AI Halo, ברירת המחדל היא 96GB משותף. כדי לשנות זאת, פתח את **AMD Ryzen™ AI Developer Center** ועבור ללשונית **Settings**. תחת **Graphics Performance Settings**, הגדל את המחוון **Shared Video Memory**, לאחר מכן לחץ על **Apply Changes** והפעל מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

הגדל את מאגר הזיכרון המשותף על ידי שינוי הגדרת דף Translation Table Manager (TTM) של הקרנל. AMD ממליצה להגדיר את ה-VRAM הייעודי המינימלי ב-BIOS (0.5 GB) כך שהכמות המרבית תהיה זמינה כזיכרון משותף.

1. התקן את כלי השירות `pipx` והוסף את הנתיב עבור גלגלים המותקנים על ידי pipx לנתיב החיפוש של המערכת:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. התקן את גלגל `amd-debug-tools` מ-PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. שאל את הגדרות הזיכרון המשותף הנוכחיות:

   ```bash
   amd-ttm
   ```

4. הגדל את הקצאת הזיכרון המשותף (יחידות ב-GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. הפעל מחדש את המחשב כדי שהשינויים ייכנסו לתוקף.

<!-- @device:end -->

<!-- @os:end -->