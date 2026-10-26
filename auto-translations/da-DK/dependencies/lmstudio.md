<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan installeres fra **AMD Ryzen™ AI Developer Center**. Gå til fanen **Updates**, og installer LM Studio, hvis det ikke allerede er til stede.

Hvis dit system har forudinstallerede modeller, skal du navigere til Settings > General > Models Directory. Skift derefter stien til `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Download installationsprogrammet herfra: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installer. 
<!-- @device:end -->

> **Modeller:** Hvis dit system blev leveret med denne playbooks model forudinstalleret, skal du pege LM Studio på den forudinstallerede modelmappe ovenfor for at bruge den. Ellers skal du downloade modellen fra LM Studios fane **Discover** (søgeikonet), før du fortsætter.

> Tip: Efter installationen skal du starte LM Studio én gang for at initialisere CLI'en (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Bemærk: Du kan vælge at installere enten .deb-filen eller AppImage. 
1. Download appimage'n herfra: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. kør `sudo apt install libfuse2`  
3. kør `cd ~/Downloads`  
4. kør `chmod +x LM-Studio-*.AppImage`  
5. kør `./LM-Studio-*.AppImage`  
> Tip: Efter installationen skal du starte LM Studio én gang for at initialisere CLI'en (`lms`).

<!-- @device:halo_box -->
Hvis dit system har forudinstallerede modeller, skal du navigere til Settings > General > Models Directory. Skift derefter stien til `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modeller:** Hvis dit system blev leveret med denne playbooks model forudinstalleret, skal du pege LM Studio på den forudinstallerede modelmappe ovenfor for at bruge den. Ellers skal du downloade modellen fra LM Studios fane **Discover** (søgeikonet), før du fortsætter.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->