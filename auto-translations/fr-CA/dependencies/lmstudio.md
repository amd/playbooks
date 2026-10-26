<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio peut être installé depuis le **AMD Ryzen™ AI Developer Center**. Accédez à l'onglet **Updates** et installez LM Studio s'il n'est pas déjà présent.

Si votre système dispose de modèles préinstallés, accédez à Settings > General > Models Directory. Changez ensuite le chemin pour `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Téléchargez l'installateur ici : [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Installez. 
<!-- @device:end -->

> **Modèles :** Si votre système est livré avec le modèle de ce playbook préinstallé, pointez LM Studio vers le répertoire des modèles préinstallés ci-dessus pour l'utiliser. Sinon, téléchargez le modèle depuis l'onglet **Discover** de LM Studio (icône de recherche) avant de continuer.

> Astuce : Après l'installation, lancez LM Studio une fois pour initialiser l'interface en ligne de commande (`lms`).

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Remarque : Vous pouvez choisir d'installer soit le .deb, soit l'AppImage. 
1. Téléchargez l'appimage ici : [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. exécutez `sudo apt install libfuse2`  
3. exécutez `cd ~/Downloads`  
4. exécutez `chmod +x LM-Studio-*.AppImage`  
5. exécutez `./LM-Studio-*.AppImage`  
> Astuce : Après l'installation, lancez LM Studio une fois pour initialiser l'interface en ligne de commande (`lms`).

<!-- @device:halo_box -->
Si votre système dispose de modèles préinstallés, accédez à Settings > General > Models Directory. Changez ensuite le chemin pour `/var/cache/models`.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Modèles :** Si votre système est livré avec le modèle de ce playbook préinstallé, pointez LM Studio vers le répertoire des modèles préinstallés ci-dessus pour l'utiliser. Sinon, téléchargez le modèle depuis l'onglet **Discover** de LM Studio (icône de recherche) avant de continuer.

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->