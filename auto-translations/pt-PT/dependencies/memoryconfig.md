<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Para o Ryzen AI Halo, a memória dedicada da GPU tem por predefinição 64 GB, o que é suficiente para a maioria das cargas de trabalho. Para modelos maiores ou contextos mais longos, aumentar este valor pode ajudar. Para ajustar, abra **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Para alterar o valor de memória dedicada da GPU, abra **AMD Software: Adrenalin Edition™** e navegue até **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

No Linux, para executar modelos maiores, aumente o conjunto de **memória partilhada** disponível para a GPU. Isto pode implicar definir a memória dedicada da GPU na BIOS para o mínimo, de modo a que o conjunto de memória partilhada possa ser maximizado.

<!-- @device:halo_box -->

Para o AMD Ryzen™ AI Halo, para modificar a definição predefinida, abra o **AMD Ryzen™ AI Developer Center** e vá para o separador **Settings**. Em **Graphics Performance Settings**, aumente o cursor de **Shared Video Memory**, depois clique em **Apply Changes** e reinicie para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aumente o conjunto de memória partilhada alterando a definição da página do Translation Table Manager (TTM) do kernel. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB) para que a quantidade máxima esteja disponível como memória partilhada.

1. Instale o utilitário `pipx` e adicione o caminho dos wheels instalados pelo pipx ao caminho de pesquisa do sistema:

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

4. Aumente a atribuição de memória partilhada (unidades em GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reinicie para que as alterações tenham efeito.

<!-- @device:end -->

<!-- @os:end -->