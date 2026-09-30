<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Para el Ryzen AI Halo, la memoria de GPU dedicada tiene un valor predeterminado de 64GB, lo cual es suficiente para la mayoría de las cargas de trabajo. Para modelos más grandes o contextos más largos, aumentar este valor puede ayudar. Para ajustarlo, abra **AMD Software: Adrenalin Edition™** y navegue a **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie el equipo para que los cambios surtan efecto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Para cambiar el valor de la memoria de GPU dedicada, abra **AMD Software: Adrenalin Edition™** y navegue a **Performance → Tuning → AMD Variable Graphics Memory**. Reinicie el equipo para que los cambios surtan efecto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

En Linux, para ejecutar modelos más grandes, aumente el **grupo de memoria compartida** disponible para la GPU. Esto podría implicar configurar la memoria de GPU dedicada del BIOS al mínimo, de modo que el grupo de memoria compartida pueda maximizarse.

<!-- @device:halo_box -->

Para el AMD Ryzen™ AI Halo, para modificar la configuración predeterminada, abra el **AMD Ryzen™ AI Developer Center** y vaya a la pestaña **Settings**. En **Graphics Performance Settings**, aumente el control deslizante **Shared Video Memory**, luego haga clic en **Apply Changes** y reinicie el equipo para que los cambios surtan efecto.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Aumente el grupo de memoria compartida cambiando la configuración de páginas del Translation Table Manager (TTM) del kernel. AMD recomienda establecer la VRAM dedicada mínima en el BIOS (0.5 GB) para que la cantidad máxima esté disponible como memoria compartida.

1. Instale la utilidad `pipx` y agregue la ruta de las wheels instaladas por pipx a la ruta de búsqueda del sistema:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Instale la wheel `amd-debug-tools` desde PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Consulte la configuración actual de memoria compartida:

   ```bash
   amd-ttm
   ```

4. Aumente la asignación de memoria compartida (unidades en GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reinicie el equipo para que los cambios surtan efecto.

<!-- @device:end -->

<!-- @os:end -->