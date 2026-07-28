<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan worden geïnstalleerd vanuit het **AMD Ryzen™ AI Developer Center**. Ga naar het tabblad **Updates** en installeer LM Studio als het nog niet aanwezig is.

Om LM Studio de vooraf geïnstalleerde modellen te laten zien, navigeer je naar Settings > General > Models Directory. Wijzig vervolgens het pad naar `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Download het installatieprogramma hier vandaan: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installeer. 
<!-- @device:end -->

> Tip: Start na installatie LM Studio één keer om de CLI (`lms`) te initialiseren.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Opmerking: U kunt ervoor kiezen om ofwel de .deb ofwel de AppImage te installeren. 
1. Download de appimage hier vandaan: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. voer uit `sudo apt install libfuse2`  
3. voer uit `cd ~/Downloads`  
4. voer uit `chmod +x LM-Studio-*.AppImage`  
5. voer uit `./LM-Studio-*.AppImage`  
> Tip: Start na installatie LM Studio één keer om de CLI (`lms`) te initialiseren.

<!-- @device:halo_box -->
Om LM Studio de vooraf geïnstalleerde modellen te laten zien, navigeer je naar Settings > General > Models Directory. Wijzig vervolgens het pad naar `/var/cache/models`.

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