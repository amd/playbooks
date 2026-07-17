<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo -laitteessa omistettu GPU-muisti on oletuksena 64 Gt, mikä riittää useimpiin työkuormiin. Suuremmille malleille tai pidemmille konteksteille sen kasvattaminen 96 Gt:iin voi auttaa. Säätääksesi tätä, avaa **AMD Software: Adrenalin Edition™** ja siirry kohtaan **Performance → Tuning → AMD Variable Graphics Memory**. Käynnistä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Muuttaaksesi omistetun GPU-muistin arvoa, avaa **AMD Software: Adrenalin Edition™** ja siirry kohtaan **Performance → Tuning → AMD Variable Graphics Memory**. Käynnistä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linuxissa suurempien mallien ajamiseksi kasvata GPU:lle käytettävissä olevaa **jaetun muistin** allokointia. Tämä saattaa edellyttää BIOS:ssa omistetun GPU-muistin asettamista minimiin, jotta jaetun muistin allas voidaan maksimoida.

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo -laitteessa oletus on 96 Gt jaettua muistia. Muokataksesi tätä, avaa **AMD Ryzen™ AI Developer Center** ja siirry **Settings**-välilehdelle. Kohdassa **Graphics Performance Settings** kasvata **Shared Video Memory** -liukusäädintä, napsauta sitten **Apply Changes** ja käynnistä uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Kasvata jaetun muistin allokointia muuttamalla ytimen Translation Table Manager (TTM) -sivuasetusta. AMD suosittelee asettamaan BIOS:ssa omistetun VRAM:n minimiin (0,5 Gt), jotta maksimaalinen määrä on käytettävissä jaettuna muistina.

1. Asenna `pipx`-apuohjelma ja lisää pipx:llä asennettujen pakettien polku järjestelmän hakupolkuun:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Asenna `amd-debug-tools`-paketti PyPI:stä:

   ```bash
   pipx install amd-debug-tools
   ```

3. Kysy nykyiset jaetun muistin asetukset:

   ```bash
   amd-ttm
   ```

4. Kasvata jaetun muistin allokointia (yksikkönä Gt):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Käynnistä uudelleen, jotta muutokset tulevat voimaan.

<!-- @device:end -->

<!-- @os:end -->