<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan installeras från **AMD Ryzen™ AI Developer Center**. Gå till fliken **Updates** och installera LM Studio om det inte redan finns installerat.

För att LM Studio ska kunna se de förinstallerade modellerna, navigera till Settings > General > Models Directory. Ändra sedan sökvägen till `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Ladda ner installationsprogrammet härifrån: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installera. 
<!-- @device:end -->

> Tips: Starta LM Studio en gång efter installationen för att initiera CLI:t (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Obs: Du kan välja att installera antingen .deb-filen eller AppImage-filen. 
1. Ladda ner appimage-filen härifrån: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. kör `sudo apt install libfuse2`  
3. kör `cd ~/Downloads`  
4. kör `chmod +x LM-Studio-*.AppImage`  
5. kör `./LM-Studio-*.AppImage`  
> Tips: Starta LM Studio en gång efter installationen för att initiera CLI:t (`lms`).

<!-- @device:halo_box -->
För att LM Studio ska kunna se de förinstallerade modellerna, navigera till Settings > General > Models Directory. Ändra sedan sökvägen till `/var/cache/models`.

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