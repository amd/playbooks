<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio voidaan asentaa **AMD Ryzen™ AI Developer Centeristä**. Siirry **Updates**-välilehdelle ja asenna LM Studio, jos sitä ei ole jo asennettu.

Jos järjestelmässäsi on valmiiksi asennettuja malleja, siirry kohtaan Settings > General > Models Directory. Vaihda sitten polku muotoon `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Lataa asennusohjelma täältä: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Asenna. 
<!-- @device:end -->

> **Mallit:** Jos järjestelmässäsi oli tämän ohjekirjan malli valmiiksi asennettuna, osoita LM Studio yllä olevaan valmiiksi asennettujen mallien hakemistoon käyttääksesi sitä. Muutoin lataa malli LM Studion **Discover**-välilehdeltä (hakukuvake) ennen jatkamista.

> Vihje: Käynnistä asennuksen jälkeen LM Studio kerran alustaaksesi CLI:n (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Huom: Voit halutessasi asentaa joko .deb-paketin tai AppImagen. 
1. Lataa appimage täältä: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. suorita `sudo apt install libfuse2`  
3. suorita `cd ~/Downloads`  
4. suorita `chmod +x LM-Studio-*.AppImage`  
5. suorita `./LM-Studio-*.AppImage`  
> Vihje: Käynnistä asennuksen jälkeen LM Studio kerran alustaaksesi CLI:n (`lms`).

<!-- @device:halo_box -->
Jos järjestelmässäsi on valmiiksi asennettuja malleja, siirry kohtaan Settings > General > Models Directory. Vaihda sitten polku muotoon `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Mallit:** Jos järjestelmässäsi oli tämän ohjekirjan malli valmiiksi asennettuna, osoita LM Studio yllä olevaan valmiiksi asennettujen mallien hakemistoon käyttääksesi sitä. Muutoin lataa malli LM Studion **Discover**-välilehdeltä (hakukuvake) ennen jatkamista.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->