<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
يمكن تثبيت LM Studio من **AMD Ryzen™ AI Developer Center**. انتقل إلى علامة التبويب **Updates** وقم بتثبيت LM Studio إذا لم يكن موجودًا بالفعل.

إذا كان نظامك يحتوي على نماذج مثبتة مسبقًا، انتقل إلى Settings > General > Models Directory. ثم غيّر المسار إلى `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. قم بتنزيل برنامج التثبيت من هنا: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. قم بالتثبيت. 
<!-- @device:end -->

> **النماذج:** إذا كان نظامك قد جاء مع نموذج هذا الدليل التشغيلي مثبتًا مسبقًا، وجّه LM Studio إلى دليل النماذج المثبتة مسبقًا أعلاه لاستخدامه. وإلا، قم بتنزيل النموذج من علامة التبويب **Discover** في LM Studio (أيقونة البحث) قبل المتابعة.

> ملاحظة: بعد التثبيت، قم بتشغيل LM Studio مرة واحدة لتهيئة واجهة سطر الأوامر (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> ملاحظة: يمكنك اختيار تثبيت إما .deb أو AppImage. 
1. قم بتنزيل الـ appimage من هنا: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. نفّذ `sudo apt install libfuse2`  
3. نفّذ `cd ~/Downloads`  
4. نفّذ `chmod +x LM-Studio-*.AppImage`  
5. نفّذ `./LM-Studio-*.AppImage`  
> ملاحظة: بعد التثبيت، قم بتشغيل LM Studio مرة واحدة لتهيئة واجهة سطر الأوامر (`lms`).

<!-- @device:halo_box -->
إذا كان نظامك يحتوي على نماذج مثبتة مسبقًا، انتقل إلى Settings > General > Models Directory. ثم غيّر المسار إلى `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **النماذج:** إذا كان نظامك قد جاء مع نموذج هذا الدليل التشغيلي مثبتًا مسبقًا، وجّه LM Studio إلى دليل النماذج المثبتة مسبقًا أعلاه لاستخدامه. وإلا، قم بتنزيل النموذج من علامة التبويب **Discover** في LM Studio (أيقونة البحث) قبل المتابعة.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->