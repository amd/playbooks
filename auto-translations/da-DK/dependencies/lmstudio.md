<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan installeres fra **AMD Ryzen™ AI Developer Center**. Gå til fanen **Updates** og installer LM Studio, hvis det ikke allerede er til stede.

For at give LM Studio adgang til de forudinstallerede modeller skal du navigere til Settings > General > Models Directory. Skift derefter stien til `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Download installationsprogrammet herfra: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installer.
<!-- @device:end -->

> Tip: Efter installation skal du starte LM Studio én gang for at initialisere CLI'en (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Bemærk: Du kan vælge at installere enten .deb eller AppImage.
1. Download appimage herfra: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. kør `sudo apt install libfuse2`
3. kør `cd ~/Downloads`
4. kør `chmod +x LM-Studio-*.AppImage`
5. kør `./LM-Studio-*.AppImage`
> Tip: Efter installation skal du starte LM Studio én gang for at initialisere CLI'en (`lms`).

<!-- @device:halo_box -->
For at give LM Studio adgang til de forudinstallerede modeller skal du navigere til Settings > General > Models Directory. Skift derefter stien til `/var/cache/models`.

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