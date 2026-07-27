<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Lägg till den aktuella användaren i grupperna render och video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Starta om systemet för att tillämpa inställningarna.**
```bash
sudo reboot
```

**Installera ROCm i den skapade virtuella miljön.**
> **Obs**: Se till att den virtuella miljön är aktiv innan du fortsätter.

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

För mer installationshjälp, se [ROCm 7.14-dokumentationen](https://rocm.docs.amd.com/en/latest/install/rocm.html).