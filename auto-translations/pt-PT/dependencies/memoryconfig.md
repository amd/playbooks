<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Para o Ryzen AI Halo, a memória de GPU dedicada assume por predefinição 64GB, o que é suficiente para a maioria das cargas de trabalho. Para modelos maiores ou contextos mais longos, aumentar este valor pode ajudar. Para o ajustar, abra o **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Para alterar o valor de memória de GPU dedicada, abra o **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

No Linux, para executar modelos maiores, aumente o **conjunto de memória partilhada** disponível para a GPU. Isto pode implicar definir a memória de GPU dedicada na BIOS para o mínimo, de modo a que o conjunto de memória partilhada possa ser maximizado.

<!-- @device:halo_box -->

Para o AMD Ryzen™ AI Halo, para modificar a definição predefinida, abra o **AMD Ryzen™ AI Developer Center** e vá ao separador **Settings**. Em **Graphics Performance Settings**, aumente o cursor **Shared Video Memory**, depois clique em **Apply Changes** e reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aumente o conjunto de memória partilhada alterando a definição de páginas do Translation Table Manager (TTM) do kernel. A AMD recomenda definir o mínimo de VRAM dedicada na BIOS (0.5 GB) para que a quantidade máxima esteja disponível como memória partilhada.

1. Instale o utilitário `pipx` e adicione o caminho para os wheels instalados pelo pipx ao caminho de pesquisa do sistema:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instale o wheel `amd-debug-tools` a partir do PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Consulte as definições atuais de memória partilhada:

   ```bash
   amd-ttm
   ```

4. Aumente a alocação de memória partilhada (unidades em GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reinicie para que as alterações tenham efeito.

<!-- @device:end -->

<!-- @os:end -->