<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pentru Ryzen AI Halo, memoria GPU dedicată este setată implicit la 64GB, ceea ce este suficient pentru majoritatea sarcinilor de lucru. Pentru modele mai mari sau contexte mai lungi, creșterea acestei valori poate ajuta. Pentru a o ajusta, deschideți **AMD Software: Adrenalin Edition™** și navigați la **Performance → Tuning → AMD Variable Graphics Memory**. Reporniți pentru ca modificările să aibă efect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Pentru a modifica valoarea memoriei GPU dedicate, deschideți **AMD Software: Adrenalin Edition™** și navigați la **Performance → Tuning → AMD Variable Graphics Memory**. Reporniți pentru ca modificările să aibă efect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Pe Linux, pentru a rula modele mai mari, creșteți grupul de **memorie partajată** disponibil pentru GPU. Acest lucru poate implica setarea memoriei GPU dedicate din BIOS la minim, astfel încât grupul de memorie partajată să poată fi maximizat.

<!-- @device:halo_box -->

Pentru AMD Ryzen™ AI Halo, pentru a modifica setarea implicită, deschideți **AMD Ryzen™ AI Developer Center** și accesați fila **Settings**. Sub **Graphics Performance Settings**, creșteți glisorul **Shared Video Memory**, apoi faceți clic pe **Apply Changes** și reporniți pentru ca modificările să aibă efect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Creșteți grupul de memorie partajată modificând setarea de pagini a Translation Table Manager (TTM) din kernel. AMD recomandă setarea VRAM-ului dedicat minim în BIOS (0,5 GB), astfel încât cantitatea maximă să fie disponibilă ca memorie partajată.

1. Instalați utilitarul `pipx` și adăugați calea pentru pachetele wheel instalate prin pipx la calea de căutare a sistemului:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instalați pachetul wheel `amd-debug-tools` din PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Interogați setările curente de memorie partajată:

   ```bash
   amd-ttm
   ```

4. Creșteți alocarea memoriei partajate (unități în GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reporniți pentru ca modificările să aibă efect.

<!-- @device:end -->

<!-- @os:end -->