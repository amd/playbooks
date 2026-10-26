<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pour le Ryzen AI Halo, la mémoire GPU dédiée est par défaut de 64 Go, ce qui est suffisant pour la plupart des charges de travail. Pour des modèles plus volumineux ou des contextes plus longs, il peut être utile d'augmenter cette valeur. Pour ajuster ce paramètre, ouvrez **AMD Software: Adrenalin Edition™** et accédez à **Performance → Tuning → AMD Variable Graphics Memory**. Redémarrez pour que les modifications prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Pour modifier la valeur de la mémoire GPU dédiée, ouvrez **AMD Software: Adrenalin Edition™** et accédez à **Performance → Tuning → AMD Variable Graphics Memory**. Redémarrez pour que les modifications prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Sous Linux, pour exécuter des modèles plus volumineux, augmentez le pool de **mémoire partagée** disponible pour le GPU. Cela peut impliquer de définir la mémoire GPU dédiée du BIOS au minimum, afin que le pool de mémoire partagée puisse être maximisé.

<!-- @device:halo_box -->

Pour l'AMD Ryzen™ AI Halo, afin de modifier le paramètre par défaut, ouvrez l'**AMD Ryzen™ AI Developer Center** et accédez à l'onglet **Settings**. Sous **Graphics Performance Settings**, augmentez le curseur **Shared Video Memory**, puis cliquez sur **Apply Changes** et redémarrez pour que les modifications prennent effet.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Augmentez le pool de mémoire partagée en modifiant le paramètre de pages du Translation Table Manager (TTM) du noyau. AMD recommande de définir la VRAM dédiée minimale dans le BIOS (0,5 Go) afin que la quantité maximale soit disponible en tant que mémoire partagée.

1. Installez l'utilitaire `pipx` et ajoutez le chemin des wheels installés par pipx au chemin de recherche du système :

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installez le wheel `amd-debug-tools` depuis PyPI :

   ```bash
   pipx install amd-debug-tools
   ```

3. Interrogez les paramètres actuels de mémoire partagée :

   ```bash
   amd-ttm
   ```

4. Augmentez l'allocation de mémoire partagée (unités en Go) :

   ```bash
   amd-ttm --set <NUM>
   ```

5. Redémarrez pour que les modifications prennent effet.

<!-- @device:end -->

<!-- @os:end -->