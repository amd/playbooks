<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Voor de Ryzen AI Halo staat het toegewezen GPU-geheugen standaard op 64GB, wat voldoende is voor de meeste workloads. Voor grotere modellen of langere contexten kan het verhogen hiervan helpen. Om dit aan te passen, open **AMD Software: Adrenalin Edition™** en navigeer naar **Performance → Tuning → AMD Variable Graphics Memory**. Start opnieuw op om de wijzigingen door te voeren.

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

Op Linux, om grotere modellen te draaien, verhoog de pool aan **gedeeld geheugen** die beschikbaar is voor de GPU. Dit kan inhouden dat het toegewezen GPU-geheugen in de BIOS op het minimum wordt ingesteld, zodat de gedeelde geheugenpool gemaximaliseerd kan worden.

<!-- @device:halo_box -->

Voor de AMD Ryzen™ AI Halo, om de standaardinstelling te wijzigen, open het **AMD Ryzen™ AI Developer Center** en ga naar het tabblad **Settings**. Onder **Graphics Performance Settings**, verhoog de schuifregelaar **Shared Video Memory**, klik vervolgens op **Apply Changes** en start opnieuw op om de wijzigingen door te voeren.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Verhoog de pool aan gedeeld geheugen door de instelling van de Translation Table Manager (TTM) pagina van de kernel te wijzigen. AMD raadt aan om het minimale toegewezen VRAM in te stellen in de BIOS (0,5 GB) zodat de maximale hoeveelheid beschikbaar is als gedeeld geheugen.

1. Installeer de `pipx`-hulpprogramma en voeg het pad voor via pipx geïnstalleerde wheels toe aan het zoekpad van het systeem:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Installeer de `amd-debug-tools`-wheel vanuit PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Vraag de huidige instellingen voor gedeeld geheugen op:

   ```bash
   amd-ttm
   ```

4. Verhoog de toewijzing van gedeeld geheugen (eenheden in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Start opnieuw op om de wijzigingen door te voeren.

<!-- @device:end -->

<!-- @os:end -->