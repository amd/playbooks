<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio lze nainstalovat z **AMD Ryzen™ AI Developer Center**. Přejděte na kartu **Updates** a nainstalujte LM Studio, pokud ještě není přítomno.

Aby LM Studio vidělo předinstalované modely, přejděte do Settings > General > Models Directory. Poté změňte cestu na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Stáhněte instalátor odsud: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Nainstalujte.
<!-- @device:end -->

> Tip: Po instalaci spusťte LM Studio jednou, aby se inicializovalo CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Poznámka: Můžete si vybrat, zda nainstalujete .deb nebo AppImage.
1. Stáhněte appimage odsud: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. spusťte `sudo apt install libfuse2`
3. spusťte `cd ~/Downloads`
4. spusťte `chmod +x LM-Studio-*.AppImage`
5. spusťte `./LM-Studio-*.AppImage`
> Tip: Po instalaci spusťte LM Studio jednou, aby se inicializovalo CLI (`lms`).

<!-- @device:halo_box -->
Aby LM Studio vidělo předinstalované modely, přejděte do Settings > General > Models Directory. Poté změňte cestu na `/var/cache/models`.

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