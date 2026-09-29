<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Per Ryzen AI Halo, la memoria GPU dedicata predefinita è 64GB, sufficiente per la maggior parte dei carichi di lavoro. Per modelli più grandi o contesti più lunghi, aumentarla può essere utile. Per modificarla, aprire **AMD Software: Adrenalin Edition™** e accedere a **Performance → Tuning → AMD Variable Graphics Memory**. Riavviare affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Per modificare il valore della memoria GPU dedicata, aprire **AMD Software: Adrenalin Edition™** e accedere a **Performance → Tuning → AMD Variable Graphics Memory**. Riavviare affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Su Linux, per eseguire modelli più grandi, aumentare il pool di **memoria condivisa** disponibile per la GPU. Ciò potrebbe richiedere di impostare la memoria GPU dedicata nel BIOS al minimo, in modo da poter massimizzare il pool di memoria condivisa.

<!-- @device:halo_box -->

Per AMD Ryzen™ AI Halo, per modificare l'impostazione predefinita, aprire **AMD Ryzen™ AI Developer Center** e accedere alla scheda **Settings**. In **Graphics Performance Settings**, aumentare il cursore **Shared Video Memory**, quindi fare clic su **Apply Changes** e riavviare affinché le modifiche abbiano effetto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aumentare il pool di memoria condivisa modificando l'impostazione delle pagine del Translation Table Manager (TTM) del kernel. AMD consiglia di impostare nel BIOS la VRAM dedicata al minimo (0,5 GB) in modo che la quantità massima sia disponibile come memoria condivisa.

1. Installare l'utility `pipx` e aggiungere il percorso per i wheel installati tramite pipx al percorso di ricerca di sistema:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installare il wheel `amd-debug-tools` da PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Interrogare le impostazioni attuali della memoria condivisa:

   ```bash
   amd-ttm
   ```

4. Aumentare l'allocazione della memoria condivisa (unità in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Riavviare affinché le modifiche abbiano effetto.

<!-- @device:end -->

<!-- @os:end -->