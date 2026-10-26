<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio lahko namestite iz **AMD Ryzen™ AI Developer Center**. Pojdite na zavihek **Updates** in namestite LM Studio, če še ni prisoten.

Če ima vaš sistem vnaprej nameščene modele, pojdite na Settings > General > Models Directory. Nato spremenite pot na `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Prenesite namestitveni program od tukaj: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Namestite. 
<!-- @device:end -->

> **Modeli:** Če je imel vaš sistem vnaprej nameščen model iz tega vodnika, usmerite LM Studio na zgornjo mapo z vnaprej nameščenimi modeli, da ga uporabite. V nasprotnem primeru pred nadaljevanjem prenesite model iz zavihka **Discover** v LM Studio (ikona iskanja).

> Nasvet: Po namestitvi enkrat zaženite LM Studio, da inicializirate CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Opomba: Izbirate lahko med namestitvijo .deb ali AppImage. 
1. Prenesite appimage od tukaj: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. zaženite `sudo apt install libfuse2`  
3. zaženite `cd ~/Downloads`  
4. zaženite `chmod +x LM-Studio-*.AppImage`  
5. zaženite `./LM-Studio-*.AppImage`  
> Nasvet: Po namestitvi enkrat zaženite LM Studio, da inicializirate CLI (`lms`).

<!-- @device:halo_box -->
Če ima vaš sistem vnaprej nameščene modele, pojdite na Settings > General > Models Directory. Nato spremenite pot na `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modeli:** Če je imel vaš sistem vnaprej nameščen model iz tega vodnika, usmerite LM Studio na zgornjo mapo z vnaprej nameščenimi modeli, da ga uporabite. V nasprotnem primeru pred nadaljevanjem prenesite model iz zavihka **Discover** v LM Studio (ikona iskanja).

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->