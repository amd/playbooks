<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio kan worden geïnstalleerd vanuit het **AMD Ryzen™ AI Developer Center**. Ga naar het tabblad **Updates** en installeer LM Studio als dit nog niet aanwezig is.

Als op uw systeem al modellen vooraf zijn geïnstalleerd, navigeer dan naar Settings > General > Models Directory. Wijzig vervolgens het pad naar `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Download het installatieprogramma hier: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installeer. 
<!-- @device:end -->

> **Modellen:** Als op uw systeem het model van deze playbook al vooraf is geïnstalleerd, wijs LM Studio dan naar de hierboven vermelde map met vooraf geïnstalleerde modellen om het te gebruiken. Download anders het model via het tabblad **Discover** van LM Studio (zoekicoon) voordat u verdergaat.

> Tip: Start LM Studio na installatie één keer op om de CLI (`lms`) te initialiseren.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Opmerking: U kunt ervoor kiezen om ofwel de .deb ofwel de AppImage te installeren. 
1. Download de appimage hier: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. voer `sudo apt install libfuse2` uit  
3. voer `cd ~/Downloads` uit  
4. voer `chmod +x LM-Studio-*.AppImage` uit  
5. voer `./LM-Studio-*.AppImage` uit  
> Tip: Start LM Studio na installatie één keer op om de CLI (`lms`) te initialiseren.

<!-- @device:halo_box -->
Als op uw systeem al modellen vooraf zijn geïnstalleerd, navigeer dan naar Settings > General > Models Directory. Wijzig vervolgens het pad naar `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modellen:** Als op uw systeem het model van deze playbook al vooraf is geïnstalleerd, wijs LM Studio dan naar de hierboven vermelde map met vooraf geïnstalleerde modellen om het te gebruiken. Download anders het model via het tabblad **Discover** van LM Studio (zoekicoon) voordat u verdergaat.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->