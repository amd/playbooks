<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Za Ryzen AI Halo, namenjena GPU memorija podrazumevano iznosi 64GB, što je dovoljno za većinu radnih opterećenja. Za veće modele ili duže kontekste, povećanje na 96GB može pomoći. Da biste to podesili, otvorite **AMD Software: Adrenalin Edition™** i idite na **Performance → Tuning → AMD Variable Graphics Memory**. Ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Da biste promenili vrednost namenjene GPU memorije, otvorite **AMD Software: Adrenalin Edition™** i idite na **Performance → Tuning → AMD Variable Graphics Memory**. Ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Na Linux-u, da biste pokretali veće modele, povećajte skup **deljene memorije** dostupan GPU-u. To može podrazumevati postavljanje namenjene GPU memorije u BIOS-u na minimum, kako bi skup deljene memorije mogao biti maksimizovan.

<!-- @device:halo_box -->

Za AMD Ryzen™ AI Halo, podrazumevano je 96GB deljene memorije. Da biste to izmenili, otvorite **AMD Ryzen™ AI Developer Center** i idite na karticu **Settings**. Pod **Graphics Performance Settings**, povećajte klizač **Shared Video Memory**, zatim kliknite na **Apply Changes** i ponovo pokrenite sistem da bi promene stupile na snagu.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Povećajte skup deljene memorije promenom podešavanja stranice Translation Table Manager (TTM) kernela. AMD preporučuje postavljanje minimalne namenjene VRAM memorije u BIOS-u (0.5 GB) kako bi maksimalna količina bila dostupna kao deljena memorija.

1. Instalirajte `pipx` alatku i dodajte putanju za pipx-instalirane pakete u sistemsku putanju pretrage:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instalirajte `amd-debug-tools` paket sa PyPI:

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