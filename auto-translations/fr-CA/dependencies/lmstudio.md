<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio peut être installé à partir de l'**AMD Ryzen™ AI Developer Center**. Accédez à l'onglet **Updates** et installez LM Studio s'il n'est pas déjà présent.

Pour permettre à LM Studio de voir les modèles préinstallés, accédez à Settings > General > Models Directory. Modifiez ensuite le chemin d'accès pour `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Téléchargez le programme d'installation ici : [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installez-le. 
<!-- @device:end -->

> Astuce : Après l'installation, lancez LM Studio une fois pour initialiser l'interface en ligne de commande (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Remarque : Vous pouvez choisir d'installer le fichier .deb ou l'AppImage. 
1. Téléchargez l'AppImage ici : [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. exécutez `sudo apt install libfuse2`  
3. exécutez `cd ~/Downloads`  
4. exécutez `chmod +x LM-Studio-*.AppImage`  
5. exécutez `./LM-Studio-*.AppImage`  
> Astuce : Après l'installation, lancez LM Studio une fois pour initialiser l'interface en ligne de commande (`lms`).

<!-- @device:halo_box -->
Pour permettre à LM Studio de voir les modèles préinstallés, accédez à Settings > General > Models Directory. Modifiez ensuite le chemin d'accès pour `/var/cache/models`.

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