<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**أضف المستخدم الحالي إلى مجموعتي render و video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**أعد تشغيل النظام لتطبيق الإعدادات.**
```bash
sudo reboot
```

**ثبّت ROCm في البيئة الافتراضية التي تم إنشاؤها.**
> **ملاحظة**: تأكد من أن البيئة الافتراضية نشطة قبل المتابعة.

<!-- @device:halo_box,halo -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1151]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1150]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1152]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1100]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "rocm[libraries,devel,device-gfx1201]==7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

للحصول على مزيد من المساعدة في التثبيت، يُرجى مراجعة [وثائق ROCm 7.14](https://rocm.docs.amd.com/en/latest/install/rocm.html).