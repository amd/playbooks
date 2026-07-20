<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Mevcut kullanıcıyı render ve video gruplarına ekleyin.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Ayarları uygulamak için sisteminizi yeniden başlatın.**
```bash
sudo reboot
```

**ROCm'i oluşturulan sanal ortama kurun.**
> **Not**: Devam etmeden önce sanal ortamın etkin olduğundan emin olun.

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

Kurulumla ilgili daha fazla yardım için lütfen bu [bağlantıya](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html) bakın.