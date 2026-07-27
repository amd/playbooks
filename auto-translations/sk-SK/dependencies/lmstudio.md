<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio je možné nainštalovať z **AMD Ryzen™ AI Developer Center**. Prejdite na kartu **Updates** a nainštalujte LM Studio, ak ešte nie je nainštalované.

Aby LM Studio videlo predinštalované modely, prejdite na Settings > General > Models Directory. Potom zmeňte cestu na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Stiahnite si inštalátor odtiaľto: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Nainštalujte. 
<!-- @device:end -->

> Tip: Po inštalácii spustite LM Studio raz, aby sa inicializovalo CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Poznámka: Môžete si vybrať, či nainštalujete .deb, alebo AppImage. 
1. Stiahnite si appimage odtiaľto: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. spustite `sudo apt install libfuse2`  
3. spustite `cd ~/Downloads`  
4. spustite `chmod +x LM-Studio-*.AppImage`  
5. spustite `./LM-Studio-*.AppImage`  
> Tip: Po inštalácii spustite LM Studio raz, aby sa inicializovalo CLI (`lms`).

<!-- @device:halo_box -->
Aby LM Studio videlo predinštalované modely, prejdite na Settings > General > Models Directory. Potom zmeňte cestu na `/var/cache/models`.

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