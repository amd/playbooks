<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Dodajte trenutnog korisnika u grupe render i video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Restartujte sistem da biste primenili podešavanja.**
```bash
sudo reboot
```

**Instalirajte ROCm u kreirano virtuelno okruženje.**
> **Napomena**: Uverite se da je virtuelno okruženje aktivno pre nego što nastavite.

<!-- @device:halo_box,halo -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1151]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1150]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1152]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1100]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1201]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

Za dodatnu pomoć oko instalacije, pogledajte [ROCm 10.0.0 dokumentaciju](https://rocm.docs.amd.com/en/latest/install/rocm.html).