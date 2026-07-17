<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio voidaan asentaa **AMD Ryzen™ AI Developer Center** -palvelusta. Siirry **Updates**-välilehdelle ja asenna LM Studio, jos sitä ei ole vielä asennettu.

Jotta LM Studio näkee valmiiksi asennetut mallit, siirry kohtaan Settings > General > Models Directory. Muuta sitten poluksi `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Lataa asennusohjelma täältä: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Asenna.
<!-- @device:end -->

> Vinkki: Asennuksen jälkeen käynnistä LM Studio kerran CLI:n (`lms`) alustamiseksi.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Huomio: Voit valita asennettavaksi joko .deb-paketin tai AppImagen.
1. Lataa AppImage täältä: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. suorita `sudo apt install libfuse2`  
3. suorita `cd ~/Downloads`  
4. suorita `chmod +x LM-Studio-*.AppImage`  
5. suorita `./LM-Studio-*.AppImage`  
> Vinkki: Asennuksen jälkeen käynnistä LM Studio kerran CLI:n (`lms`) alustamiseksi.

<!-- @device:halo_box -->
Jotta LM Studio näkee valmiiksi asennetut mallit, siirry kohtaan Settings > General > Models Directory. Muuta sitten poluksi `/var/cache/models`.

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