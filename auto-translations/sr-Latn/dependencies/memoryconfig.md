<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Za Ryzen AI Halo, namenska memorija GPU-a podrazumevano iznosi 64GB, što je dovoljno za većinu radnih opterećenja. Za veće modele ili duže kontekste, povećanje na 96GB može pomoći. Da biste to podesili, otvorite **AMD Software: Adrenalin Edition™** i idite na **Performance → Tuning → AMD Variable Graphics Memory**. Ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Da biste promenili vrednost namenske memorije GPU-a, otvorite **AMD Software: Adrenalin Edition™** i idite na **Performance → Tuning → AMD Variable Graphics Memory**. Ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Na Linux-u, da biste pokretali veće modele, povećajte **deljeni memorijski** prostor dostupan GPU-u. Ovo može zahtevati podešavanje namenske memorije GPU-a u BIOS-u na minimum, kako bi se deljeni memorijski prostor mogao maksimalno povećati.

<!-- @device:halo_box -->

Za AMD Ryzen™ AI Halo, podrazumevana vrednost je 96GB deljeno. Da biste ovo izmenili, otvorite **AMD Ryzen™ AI Developer Center** i idite na karticu **Settings**. U okviru **Graphics Performance Settings**, povećajte klizač **Shared Video Memory**, zatim kliknite na **Apply Changes** i ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Povećajte deljeni memorijski prostor promenom podešavanja stranica Translation Table Manager-a (TTM) u kernelu. AMD preporučuje da se u BIOS-u podesi minimalna namenska VRAM memorija (0.5 GB) kako bi maksimalna količina bila dostupna kao deljena memorija.

1. Instalirajte alat `pipx` i dodajte putanju za pakete instalirane putem pipx-a u sistemsku putanju za pretragu:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instalirajte paket `amd-debug-tools` sa PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Proverite trenutna podešavanja deljene memorije:

   ```bash
   amd-ttm
   ```

4. Povećajte alokaciju deljene memorije (jedinice su u GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Ponovo pokrenite sistem da bi promene stupile na snagu.

<!-- @device:end -->

<!-- @os:end -->