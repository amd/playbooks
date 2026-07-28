<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio può essere installato dall'**AMD Ryzen™ AI Developer Center**. Vai alla scheda **Updates** e installa LM Studio se non è già presente.

Per consentire a LM Studio di vedere i modelli preinstallati, vai su Settings > General > Models Directory. Quindi modifica il percorso in `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Scarica il programma di installazione da qui: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installa. 
<!-- @device:end -->

> Suggerimento: dopo l'installazione, avvia LM Studio una volta per inizializzare la CLI (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Nota: puoi scegliere di installare il .deb oppure l'AppImage. 
1. Scarica l'appimage da qui: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. esegui `sudo apt install libfuse2`  
3. esegui `cd ~/Downloads`  
4. esegui `chmod +x LM-Studio-*.AppImage`  
5. esegui `./LM-Studio-*.AppImage`  
> Suggerimento: dopo l'installazione, avvia LM Studio una volta per inizializzare la CLI (`lms`).

<!-- @device:halo_box -->
Per consentire a LM Studio di vedere i modelli preinstallati, vai su Settings > General > Models Directory. Quindi modifica il percorso in `/var/cache/models`.

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