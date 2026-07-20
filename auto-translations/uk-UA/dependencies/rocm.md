<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Додайте поточного користувача до груп render і video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Перезавантажте систему, щоб застосувати налаштування.**
```bash
sudo reboot
```

**Встановіть ROCm у створеному віртуальному середовищі.**
> **Примітка**: перш ніж продовжити, переконайтеся, що віртуальне середовище активне.

<!-- @device:halo,halo_box -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx110X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

Для отримання додаткової допомоги зі встановлення перегляньте це [посилання](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).