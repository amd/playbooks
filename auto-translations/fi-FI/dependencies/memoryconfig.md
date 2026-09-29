<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo -laitteissa GPU:lle varattu näytönohjaimen muisti on oletusarvoisesti 64 Gt, mikä riittää useimpiin työkuormiin. Suurempien mallien tai pidempien kontekstien käsittelyssä tämän arvon kasvattamisesta voi olla hyötyä. Muuta asetusta avaamalla **AMD Software: Adrenalin Edition™** ja siirtymällä kohtaan **Performance → Tuning → AMD Variable Graphics Memory**. Käynnistä tietokone uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Voit muuttaa GPU:lle varatun näytönohjaimen muistin arvoa avaamalla **AMD Software: Adrenalin Edition™** ja siirtymällä kohtaan **Performance → Tuning → AMD Variable Graphics Memory**. Käynnistä tietokone uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linux-käyttöjärjestelmässä suurempien mallien suorittamiseksi kasvata GPU:n käytettävissä olevaa **jaetun muistin** poolia. Tämä saattaa edellyttää GPU:lle BIOS:ssa varatun näytönohjaimen muistin asettamista minimiin, jotta jaetun muistin poolin koko voidaan maksimoida.

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo -laitteissa voit muokata oletusasetusta avaamalla **AMD Ryzen™ AI Developer Center** -sovelluksen ja siirtymällä **Settings**-välilehteen. Kasvata kohdassa **Graphics Performance Settings** olevaa **Shared Video Memory** -liukusäädintä, napsauta sitten **Apply Changes** ja käynnistä tietokone uudelleen, jotta muutokset tulevat voimaan.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Kasvata jaetun muistin poolia muuttamalla kernelin Translation Table Manager (TTM) -sivuasetusta. AMD suosittelee asettamaan BIOS:ssa minimimäärän varattua VRAM-muistia (0,5 Gt), jotta mahdollisimman suuri määrä on käytettävissä jaettuna muistina.

1. Asenna `pipx`-työkalu ja lisää pipx:llä asennettujen wheel-pakettien polku järjestelmän hakupolkuun:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Asenna `amd-debug-tools`-wheel PyPI:stä:

   ```bash
   pipx install amd-debug-tools
   ```

3. Tarkista nykyiset jaetun muistin asetukset:

   ```bash
   amd-ttm
   ```

4. Kasvata jaetun muistin varausta (yksikkönä Gt):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Käynnistä tietokone uudelleen, jotta muutokset tulevat voimaan.

<!-- @device:end -->

<!-- @os:end -->