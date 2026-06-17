<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

For the Ryzen AI Halo, the dedicated GPU memory defaults to 64GB, which is sufficient for most workloads. For larger models or longer contexts, increasing this to 96GB may help. To adjust, open **AMD Software: Adrenalin Edition™** and navigate to **Performance → Tuning → AMD Variable Graphics Memory**. Reboot for the changes to take effect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

To change the dedicated GPU memory value, open **AMD Software: Adrenalin Edition™** and navigate to **Performance → Tuning → AMD Variable Graphics Memory**. Reboot for the changes to take effect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

On Linux, to run larger models, increase the **shared memory** pool available to the GPU. This might involve setting the BIOS dedicated GPU memory to the minimum, so that the shared memory pool can be maximized.

<!-- @device:halo_box -->

For the AMD Ryzen™ AI Halo, the default is 96GB shared. To modify this, open the **AMD Ryzen™ AI Developer Center** and go to the **Settings** tab. Under **Graphics Performance Settings**, increase the **Shared Video Memory** slider, then click **Apply Changes** and reboot for the changes to take effect.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Increase the shared memory pool by changing the kernel's Translation Table Manager (TTM) page setting. AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5 GB) so the maximum amount is available as shared memory.

1. Install the `pipx` utility and add the path for pipx-installed wheels to the system search path:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. Install the `amd-debug-tools` wheel from PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. Query the current shared memory settings:

   ```bash
   amd-ttm
   ```

4. Increase the shared memory allocation (units in GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Reboot for the changes to take effect.

For `amd-ttm` usage examples, see the [ROCm documentation](https://rocm.docs.amd.com/projects/radeon-ryzen/en/docs-7.0.2/docs/install/installryz/native_linux/install-ryzen.html#amd-ttm-usage-examples).

<!-- @device:end -->

<!-- @os:end -->
