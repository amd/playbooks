<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

對於 Ryzen AI Halo，專用 GPU 記憶體預設為 64GB，這對大多數工作負載來說已經足夠。對於較大的模型或較長的上下文，增加此數值可能會有所幫助。若要調整，請開啟 **AMD Software: Adrenalin Edition™** 並前往 **Performance → Tuning → AMD Variable Graphics Memory**。重新啟動以使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

若要變更專用 GPU 記憶體數值，請開啟 **AMD Software: Adrenalin Edition™** 並前往 **Performance → Tuning → AMD Variable Graphics Memory**。重新啟動以使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

在 Linux 上，若要執行較大的模型，請增加 GPU 可用的**共用記憶體**池。這可能需要將 BIOS 的專用 GPU 記憶體設定為最小值，以便最大化共用記憶體池。

<!-- @device:halo_box -->

對於 AMD Ryzen™ AI Halo，若要修改預設設定，請開啟 **AMD Ryzen™ AI Developer Center** 並前往 **Settings** 分頁。在 **Graphics Performance Settings** 下，增加 **Shared Video Memory** 滑桿，然後點選 **Apply Changes** 並重新啟動以使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

透過變更核心的 Translation Table Manager (TTM) 頁面設定來增加共用記憶體池。AMD 建議在 BIOS 中將專用 VRAM 設為最小值（0.5 GB），以便最大量的記憶體可作為共用記憶體使用。

1. 安裝 `pipx` 工具，並將 pipx 安裝的 wheel 路徑加入系統搜尋路徑：

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. 從 PyPI 安裝 `amd-debug-tools` wheel：

   ```bash
   pipx install amd-debug-tools
   ```

3. 查詢目前的共用記憶體設定：

   ```bash
   amd-ttm
   ```

4. 增加共用記憶體配置（單位為 GB）：

   ```bash
   amd-ttm --set <NUM>
   ```

5. 重新啟動以使變更生效。

<!-- @device:end -->

<!-- @os:end -->