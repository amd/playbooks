<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
ניתן להתקין את LM Studio דרך **AMD Ryzen™ AI Developer Center**. עברו ללשונית **Updates** והתקינו את LM Studio אם הוא עדיין לא מותקן.

אם במערכת שלכם מותקנים מודלים מראש, נווטו אל Settings > General > Models Directory. לאחר מכן שנו את הנתיב ל-`C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. הורידו את תוכנת ההתקנה מכאן: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. התקינו.
<!-- @device:end -->

> **מודלים:** אם המערכת שלכם הגיעה עם המודל של ספר המשחק הזה מותקן מראש, הפנו את LM Studio לתיקיית המודלים המותקנים מראש שלמעלה כדי להשתמש בו. אחרת, הורידו את המודל מלשונית **Discover** של LM Studio (סמל החיפוש) לפני שתמשיכו.

> טיפ: לאחר ההתקנה, הפעילו את LM Studio פעם אחת כדי לאתחל את ה-CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> הערה: תוכלו לבחור להתקין את קובץ ה-.deb או את ה-AppImage.
1. הורידו את ה-appimage מכאן: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. הריצו `sudo apt install libfuse2`  
3. הריצו `cd ~/Downloads`  
4. הריצו `chmod +x LM-Studio-*.AppImage`  
5. הריצו `./LM-Studio-*.AppImage`  
> טיפ: לאחר ההתקנה, הפעילו את LM Studio פעם אחת כדי לאתחל את ה-CLI (`lms`).

<!-- @device:halo_box -->
אם במערכת שלכם מותקנים מודלים מראש, נווטו אל Settings > General > Models Directory. לאחר מכן שנו את הנתיב ל-`/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **מודלים:** אם המערכת שלכם הגיעה עם המודל של ספר המשחק הזה מותקן מראש, הפנו את LM Studio לתיקיית המודלים המותקנים מראש שלמעלה כדי להשתמש בו. אחרת, הורידו את המודל מלשונית **Discover** של LM Studio (סמל החיפוש) לפני שתמשיכו.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->