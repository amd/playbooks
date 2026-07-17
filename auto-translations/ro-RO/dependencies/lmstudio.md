<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio poate fi instalat din **AMD Ryzen™ AI Developer Center**. Accesați fila **Updates** și instalați LM Studio dacă nu este deja prezent.

Pentru a permite LM Studio să vadă modelele preinstalate, navigați la Settings > General > Models Directory. Apoi schimbați calea la `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Descărcați programul de instalare de aici: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Instalați.
<!-- @device:end -->

> Sfat: După instalare, lansați LM Studio o dată pentru a inițializa CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Notă: Puteți alege să instalați fie .deb, fie AppImage.
1. Descărcați appimage-ul de aici: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. rulați `sudo apt install libfuse2`
3. rulați `cd ~/Downloads`
4. rulați `chmod +x LM-Studio-*.AppImage`
5. rulați `./LM-Studio-*.AppImage`
> Sfat: După instalare, lansați LM Studio o dată pentru a inițializa CLI (`lms`).

<!-- @device:halo_box -->
Pentru a permite LM Studio să vadă modelele preinstalate, navigați la Settings > General > Models Directory. Apoi schimbați calea la `/var/cache/models`.

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