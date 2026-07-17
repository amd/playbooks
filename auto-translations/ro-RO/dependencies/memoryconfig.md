<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Pentru Ryzen AI Halo, memoria GPU dedicată este implicit de 64GB, ceea ce este suficient pentru majoritatea sarcinilor de lucru. Pentru modele mai mari sau contexte mai lungi, creșterea acesteia la 96GB poate fi de ajutor. Pentru a ajusta, deschideți **AMD Software: Adrenalin Edition™** și navigați la **Performance → Tuning → AMD Variable Graphics Memory**. Reporniți pentru ca modificările să intre în vigoare.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Pentru a modifica valoarea memoriei GPU dedicate, deschideți **AMD Software: Adrenalin Edition™** și navigați la **Performance → Tuning → AMD Variable Graphics Memory**. Reporniți pentru ca modificările să intre în vigoare.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Pe Linux, pentru a rula modele mai mari, creșteți grupul de **memorie partajată** disponibil pentru GPU. Aceasta poate implica setarea memoriei GPU dedicate din BIOS la valoarea minimă, astfel încât grupul de memorie partajată să poată fi maximizat.

<!-- @device:halo_box -->

Pentru AMD Ryzen™ AI Halo, valoarea implicită este de 96GB partajat. Pentru a modifica aceasta, deschideți **AMD Ryzen™ AI Developer Center** și accesați fila **Settings**. Sub **Graphics Performance Settings**, măriți cursorul **Shared Video Memory**, apoi faceți clic pe **Apply Changes** și reporniți pentru ca modificările să intre în vigoare.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Creșteți grupul de memorie partajată modificând setarea paginii Translation Table Manager (TTM) a kernelului. AMD recomandă setarea VRAM dedicat minim în BIOS (0,5 GB) astfel încât cantitatea maximă să fie disponibilă ca memorie partajată.

1. Instalați utilitarul `pipx` și adăugați calea pentru pachetele instalate prin pipx la calea de căutare a sistemului:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instalați pachetul `amd-debug-tools` din PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Interogați setările curente ale memoriei partajate:

   ```bash
   amd-ttm
   ```

4. Creșteți alocarea memoriei partajate (unități în GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reporniți pentru ca modificările să intre în vigoare.

<!-- @device:end -->

<!-- @os:end -->