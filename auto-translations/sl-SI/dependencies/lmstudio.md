<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio je mogoče namestiti iz **AMD Ryzen™ AI Developer Center**. Pojdite na zavihek **Updates** in namestite LM Studio, če še ni prisoten.

Da bi LM Studio lahko videl vnaprej nameščene modele, se pomaknite na Settings > General > Models Directory. Nato spremenite pot na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Prenesite namestitveni program od tukaj: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Namestite.
<!-- @device:end -->

> Nasvet: Po namestitvi enkrat zaženite LM Studio, da inicializirate CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Opomba: Izberete lahko namestitev .deb ali AppImage.
1. Prenesite appimage od tukaj: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. Zaženite `sudo apt install libfuse2`
3. Zaženite `cd ~/Downloads`
4. Zaženite `chmod +x LM-Studio-*.AppImage`
5. Zaženite `./LM-Studio-*.AppImage`
> Nasvet: Po namestitvi enkrat zaženite LM Studio, da inicializirate CLI (`lms`).

<!-- @device:halo_box -->
Da bi LM Studio lahko videl vnaprej nameščene modele, se pomaknite na Settings > General > Models Directory. Nato spremenite pot na `/var/cache/models`.

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