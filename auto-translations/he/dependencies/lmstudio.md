<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
ניתן להתקין את LM Studio מ**מרכז המפתחים של AMD Ryzen™ AI**. עבור ללשונית **Updates** והתקן את LM Studio אם הוא אינו מותקן כבר.

כדי לאפשר ל-LM Studio לראות את המודלים המותקנים מראש, נווט אל Settings > General > Models Directory. לאחר מכן שנה את הנתיב ל-`C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. הורד את תוכנית ההתקנה מכאן: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. התקן.
<!-- @device:end -->

> טיפ: לאחר ההתקנה, הפעל את LM Studio פעם אחת כדי לאתחל את ה-CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> הערה: ניתן לבחור להתקין את קובץ ה-.deb או את ה-AppImage.
1. הורד את ה-appimage מכאן: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. הרץ `sudo apt install libfuse2`
3. הרץ `cd ~/Downloads`
4. הרץ `chmod +x LM-Studio-*.AppImage`
5. הרץ `./LM-Studio-*.AppImage`
> טיפ: לאחר ההתקנה, הפעל את LM Studio פעם אחת כדי לאתחל את ה-CLI (`lms`).

<!-- @device:halo_box -->
כדי לאפשר ל-LM Studio לראות את המודלים המותקנים מראש, נווט אל Settings > General > Models Directory. לאחר מכן שנה את הנתיב ל-`/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end -->
<!-- @os:end -->