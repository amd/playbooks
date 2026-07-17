<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio se može instalirati iz **AMD Ryzen™ AI Developer Center**. Idite na karticu **Updates** i instalirajte LM Studio ako već nije prisutan.

Da biste omogućili LM Studio-u da vidi unapred instalirane modele, idite na Settings > General > Models Directory. Zatim promenite putanju na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Preuzmite instalater odavde: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Instalirajte.
<!-- @device:end -->

> Savet: Nakon instalacije, pokrenite LM Studio jednom da biste inicijalizovali CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Napomena: Možete odabrati da instalirate .deb ili AppImage.
1. Preuzmite appimage odavde: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. pokrenite `sudo apt install libfuse2`
3. pokrenite `cd ~/Downloads`
4. pokrenite `chmod +x LM-Studio-*.AppImage`
5. pokrenite `./LM-Studio-*.AppImage`
> Savet: Nakon instalacije, pokrenite LM Studio jednom da biste inicijalizovali CLI (`lms`).

<!-- @device:halo_box -->
Da biste omogućili LM Studio-u da vidi unapred instalirane modele, idite na Settings > General > Models Directory. Zatim promenite putanju na `/var/cache/models`.

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