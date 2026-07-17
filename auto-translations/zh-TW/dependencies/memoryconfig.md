<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

對於 Ryzen AI Halo，專用 GPU 記憶體預設為 64GB，對大多數工作負載已足夠。若需執行較大的模型或更長的上下文，將其增加至 96GB 可能有所幫助。如需調整，請開啟 **AMD Software: Adrenalin Edition™**，並導覽至 **Performance → Tuning → AMD Variable Graphics Memory**。重新開機後變更即可生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

如需變更專用 GPU 記憶體的數值，請開啟 **AMD Software: Adrenalin Edition™**，並導覽至 **Performance → Tuning → AMD Variable Graphics Memory**。重新開機後變更即可生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

在 Linux 上，若要執行較大的模型，請增加 GPU 可用的**共享記憶體**池。這可能需要將 BIOS 中的專用 GPU 記憶體設定為最小值，以便將共享記憶體池最大化。

<!-- @device:halo_box -->

對於 AMD Ryzen™ AI Halo，預設為 96GB 共享記憶體。如需修改，請開啟 **AMD Ryzen™ AI Developer Center**，並前往 **Settings** 標籤頁。在 **Graphics Performance Settings** 下，增加 **Shared Video Memory** 滑桿的數值，然後點擊 **Apply Changes** 並重新開機，使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

透過變更核心的 Translation Table Manager (TTM) 頁面設定來增加共享記憶體池。AMD 建議在 BIOS 中將專用 VRAM 設定為最小值（0.5 GB），以便將最大容量作為共享記憶體使用。

1. 安裝 `pipx` 工具，並將 pipx 安裝的套件路徑加入系統搜尋路徑：

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. 從 PyPI 安裝 `amd-debug-tools` 套件：

   ```bash
   pipx install amd-debug-tools
   ```

3. 查詢目前的共享記憶體設定：

   ```bash
   amd-ttm
   ```

4. 增加共享記憶體配置（單位為 GB）：

   ```bash
   amd-ttm --set <NUM>
   ```

5. 重新開機後變更即可生效。

<!-- @device:end -->

<!-- @os:end -->