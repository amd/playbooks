<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
A LM Studio telepíthető az **AMD Ryzen™ AI Developer Center**-ből. Lépj az **Updates** fülre, és telepítsd a LM Studio-t, ha még nincs telepítve.

Ha a rendszereden előre telepített modellek vannak, navigálj a Settings > General > Models Directory menüpontra. Ezután módosítsd az elérési utat erre: `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Töltsd le a telepítőt innen: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Telepítsd. 
<!-- @device:end -->

> **Modellek:** Ha a rendszered ezzel a playbookkal előre telepített modellt tartalmazott, irányítsd a LM Studio-t a fent megadott előre telepített modellkönyvtárra a használatához. Egyébként töltsd le a modellt a LM Studio **Discover** füléről (keresés ikon) a folytatás előtt.

> Tipp: Telepítés után indítsd el egyszer a LM Studio-t a CLI (`lms`) inicializálásához.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Megjegyzés: Választhatsz, hogy a .deb vagy az AppImage csomagot telepíted. 
1. Töltsd le az appimage-t innen: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. futtasd: `sudo apt install libfuse2`  
3. futtasd: `cd ~/Downloads`  
4. futtasd: `chmod +x LM-Studio-*.AppImage`  
5. futtasd: `./LM-Studio-*.AppImage`  
> Tipp: Telepítés után indítsd el egyszer a LM Studio-t a CLI (`lms`) inicializálásához.

<!-- @device:halo_box -->
Ha a rendszereden előre telepített modellek vannak, navigálj a Settings > General > Models Directory menüpontra. Ezután módosítsd az elérési utat erre: `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modellek:** Ha a rendszered ezzel a playbookkal előre telepített modellt tartalmazott, irányítsd a LM Studio-t a fent megadott előre telepített modellkönyvtárra a használatához. Egyébként töltsd le a modellt a LM Studio **Discover** füléről (keresés ikon) a folytatás előtt.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->