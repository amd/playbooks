<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Para o Ryzen AI Halo, a memória GPU dedicada tem como padrão 64GB, o que é suficiente para a maioria das cargas de trabalho. Para modelos maiores ou contextos mais longos, aumentar para 96GB pode ajudar. Para ajustar, abra o **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações entrem em vigor.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Para alterar o valor da memória GPU dedicada, abra o **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações entrem em vigor.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

No Linux, para executar modelos maiores, aumente o pool de **memória compartilhada** disponível para o GPU. Isso pode envolver definir a memória GPU dedicada no BIOS para o valor mínimo, de modo que o pool de memória compartilhada possa ser maximizado.

<!-- @device:halo_box -->

Para o AMD Ryzen™ AI Halo, o padrão é 96GB compartilhados. Para modificar isso, abra o **AMD Ryzen™ AI Developer Center** e vá até a aba **Settings**. Em **Graphics Performance Settings**, aumente o controle deslizante de **Shared Video Memory**, clique em **Apply Changes** e reinicie para que as alterações entrem em vigor.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aumente o pool de memória compartilhada alterando a configuração de página do Translation Table Manager (TTM) do kernel. A AMD recomenda definir a VRAM dedicada mínima no BIOS (0,5 GB) para que a quantidade máxima esteja disponível como memória compartilhada.

1. Instale o utilitário `pipx` e adicione o caminho para os wheels instalados pelo pipx ao caminho de busca do sistema:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instale o wheel `amd-debug-tools` do PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Consulte as configurações atuais de memória compartilhada:

   ```bash
   amd-ttm
   ```

4. Aumente a alocação de memória compartilhada (unidades em GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reinicie para que as alterações entrem em vigor.

<!-- @device:end -->

<!-- @os:end -->