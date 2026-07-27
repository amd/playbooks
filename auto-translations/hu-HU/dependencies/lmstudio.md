<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
A LM Studio telepíthető az **AMD Ryzen™ AI Developer Center**-ből. Lépjen az **Updates** fülre, és telepítse a LM Studio-t, ha még nincs telepítve.

Ahhoz, hogy a LM Studio láthassa az előre telepített modelleket, navigáljon a Settings > General > Models Directory menüpontra. Ezután módosítsa az elérési utat erre: `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Töltse le a telepítőt innen: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Telepítse.
<!-- @device:end -->

> Tipp: A telepítés után indítsa el egyszer a LM Studio-t a CLI (`lms`) inicializálásához.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Megjegyzés: Választhat, hogy a .deb vagy az AppImage csomagot telepíti.
1. Töltse le az appimage fájlt innen: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. futtassa: `sudo apt install libfuse2`  
3. futtassa: `cd ~/Downloads`  
4. futtassa: `chmod +x LM-Studio-*.AppImage`  
5. futtassa: `./LM-Studio-*.AppImage`  
> Tipp: A telepítés után indítsa el egyszer a LM Studio-t a CLI (`lms`) inicializálásához.

<!-- @device:halo_box -->
Ahhoz, hogy a LM Studio láthassa az előre telepített modelleket, navigáljon a Settings > General > Models Directory menüpontra. Ezután módosítsa az elérési utat erre: `/var/cache/models`.

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