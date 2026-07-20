<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Добавьте текущего пользователя в группы render и video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Перезагрузите систему, чтобы применить настройки.**
```bash
sudo reboot
```

**Установите ROCm в созданном виртуальном окружении.**
> **Примечание**: Перед выполнением этого шага убедитесь, что виртуальное окружение активно.

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

Дополнительную информацию по установке можно найти по этой [ссылке](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html).