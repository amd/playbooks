<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**Ajoutez l'utilisateur actuel aux groupes render et video.** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**Redémarrez votre système pour appliquer les paramètres.**
```bash
sudo reboot
```

**Installez ROCm dans l'environnement virtuel créé.**
> **Remarque** : assurez-vous que l'environnement virtuel est actif avant de continuer.

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

Pour obtenir plus d'aide sur l'installation, veuillez consulter la [documentation ROCm 10.0.0](https://rocm.docs.amd.com/en/latest/install/rocm.html).