<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan installeres fra **AMD Ryzen™ AI Developer Center**. Gå til fanen **Updates**, og installer LM Studio hvis den ikke allerede finnes.

For at LM Studio skal kunne se de forhåndsinstallerte modellene, naviger til Settings > General > Models Directory. Endre deretter stien til `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Last ned installasjonsprogrammet herfra: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installer. 
<!-- @device:end -->

> Tips: Etter installasjonen, start LM Studio én gang for å initialisere CLI-en (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Merk: Du kan velge å installere enten .deb-filen eller AppImage-filen. 
1. Last ned appimage-filen herfra: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. kjør `sudo apt install libfuse2`  
3. kjør `cd ~/Downloads`  
4. kjør `chmod +x LM-Studio-*.AppImage`  
5. kjør `./LM-Studio-*.AppImage`  
> Tips: Etter installasjonen, start LM Studio én gang for å initialisere CLI-en (`lms`).

<!-- @device:halo_box -->
For at LM Studio skal kunne se de forhåndsinstallerte modellene, naviger til Settings > General > Models Directory. Endre deretter stien til `/var/cache/models`.

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