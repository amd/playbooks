<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

对于 Ryzen AI Halo，专用 GPU 内存默认为 64GB，这对于大多数工作负载已经足够。对于更大的模型或更长的上下文，将其增加到 96GB 可能会有所帮助。要进行调整，请打开 **AMD Software: Adrenalin Edition™**，然后导航至 **Performance → Tuning → AMD Variable Graphics Memory**。重启后更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

要更改专用 GPU 内存值，请打开 **AMD Software: Adrenalin Edition™**，然后导航至 **Performance → Tuning → AMD Variable Graphics Memory**。重启后更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

在 Linux 上，若要运行更大的模型，请增加 GPU 可用的**共享内存**池。这可能需要将 BIOS 中的专用 GPU 内存设置为最小值，以便最大化共享内存池。

<!-- @device:halo_box -->

对于 AMD Ryzen™ AI Halo，默认共享内存为 96GB。要修改此设置，请打开 **AMD Ryzen™ AI Developer Center**，然后转到 **Settings** 选项卡。在 **Graphics Performance Settings** 下，增大 **Shared Video Memory** 滑块，然后单击 **Apply Changes** 并重启以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

通过更改内核的转换表管理器（TTM）页面设置来增加共享内存池。AMD 建议在 BIOS 中将专用 VRAM 设置为最小值（0.5 GB），以便最大数量的内存可作为共享内存使用。

1. 安装 `pipx` 工具，并将 pipx 安装的 wheel 路径添加到系统搜索路径：

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. 从 PyPI 安装 `amd-debug-tools` wheel：

   ```bash
   pipx install amd-debug-tools
   ```

3. 查询当前共享内存设置：

   ```bash
   amd-ttm
   ```

4. 增加共享内存分配（单位为 GB）：

   ```bash
   amd-ttm --set <NUM>
   ```

5. 重启后更改生效。

<!-- @device:end -->

<!-- @os:end -->