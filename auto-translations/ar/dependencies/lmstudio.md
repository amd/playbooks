<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
يمكن تثبيت LM Studio من **AMD Ryzen™ AI Developer Center**. انتقل إلى علامة التبويب **Updates** وقم بتثبيت LM Studio إذا لم يكن موجودًا بالفعل.

للسماح لـ LM Studio برؤية النماذج المثبتة مسبقًا، انتقل إلى Settings > General > Models Directory. ثم قم بتغيير المسار إلى `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. قم بتنزيل المثبت من هنا: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. قم بالتثبيت. 
<!-- @device:end -->

> ملاحظة: بعد التثبيت، قم بتشغيل LM Studio مرة واحدة لتهيئة واجهة سطر الأوامر (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> ملاحظة: يمكنك اختيار تثبيت إما .deb أو AppImage. 
1. قم بتنزيل ملف appimage من هنا: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. نفّذ الأمر `sudo apt install libfuse2`  
3. نفّذ الأمر `cd ~/Downloads`  
4. نفّذ الأمر `chmod +x LM-Studio-*.AppImage`  
5. نفّذ الأمر `./LM-Studio-*.AppImage`  
> ملاحظة: بعد التثبيت، قم بتشغيل LM Studio مرة واحدة لتهيئة واجهة سطر الأوامر (`lms`).

<!-- @device:halo_box -->
للسماح لـ LM Studio برؤية النماذج المثبتة مسبقًا، انتقل إلى Settings > General > Models Directory. ثم قم بتغيير المسار إلى `/var/cache/models`.

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