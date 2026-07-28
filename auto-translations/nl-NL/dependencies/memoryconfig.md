<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Voor de Ryzen AI Halo staat het toegewezen GPU-geheugen standaard ingesteld op 64GB, wat voor de meeste workloads voldoende is. Voor grotere modellen of langere contexten kan het verhogen naar 96GB helpen. Om dit aan te passen, open **AMD Software: Adrenalin Edition™** en navigeer naar **Performance → Tuning → AMD Variable Graphics Memory**. Start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Om de waarde van het toegewezen GPU-geheugen te wijzigen, open **AMD Software: Adrenalin Edition™** en navigeer naar **Performance → Tuning → AMD Variable Graphics Memory**. Start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Op Linux moet u, om grotere modellen te draaien, de **shared memory**-pool die beschikbaar is voor de GPU vergroten. Dit kan inhouden dat u het toegewezen GPU-geheugen in de BIOS op het minimum instelt, zodat de shared memory-pool gemaximaliseerd kan worden.

<!-- @device:halo_box -->

Voor de AMD Ryzen™ AI Halo is de standaardinstelling 96GB shared. Om dit te wijzigen, open het **AMD Ryzen™ AI Developer Center** en ga naar het tabblad **Settings**. Verhoog onder **Graphics Performance Settings** de schuifregelaar **Shared Video Memory**, klik vervolgens op **Apply Changes** en start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Vergroot de shared memory-pool door de paginainstelling van de Translation Table Manager (TTM) van de kernel te wijzigen. AMD raadt aan om de minimale toegewezen VRAM in de BIOS (0.5 GB) in te stellen, zodat de maximale hoeveelheid beschikbaar is als shared memory.

1. Installeer het hulpprogramma `pipx` en voeg het pad voor via pipx geïnstalleerde wheels toe aan het zoekpad van het systeem:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installeer de `amd-debug-tools`-wheel vanaf PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Vraag de huidige shared memory-instellingen op:

   ```bash
   amd-ttm
   ```

4. Verhoog de shared memory-toewijzing (eenheden in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Start opnieuw op om de wijzigingen door te voeren.

<!-- @device:end -->

<!-- @os:end -->