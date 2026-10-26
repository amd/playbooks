<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo の場合、専用GPUメモリはデフォルトで64GBに設定されており、ほとんどのワークロードには十分です。より大きなモデルやより長いコンテキストを扱う場合は、この値を増やすことが有効な場合があります。設定を変更するには、**AMD Software: Adrenalin Edition™** を開き、**Performance → Tuning → AMD Variable Graphics Memory** に移動してください。変更を反映するには再起動が必要です。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

専用GPUメモリの値を変更するには、**AMD Software: Adrenalin Edition™** を開き、**Performance → Tuning → AMD Variable Graphics Memory** に移動してください。変更を反映するには再起動が必要です。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linuxでより大きなモデルを実行するには、GPUが利用できる**共有メモリ**プールを増やしてください。これには、共有メモリプールを最大化するために、BIOSの専用GPUメモリを最小値に設定する必要がある場合があります。

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo の場合、デフォルト設定を変更するには、**AMD Ryzen™ AI Developer Center** を開き、**Settings** タブに移動してください。**Graphics Performance Settings** の下にある **Shared Video Memory** スライダーを増やし、**Apply Changes** をクリックしてから、変更を反映するために再起動してください。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

カーネルのTranslation Table Manager (TTM) ページ設定を変更することで、共有メモリプールを増やしてください。AMDは、共有メモリとして最大量を利用できるように、BIOSで専用VRAMを最小値（0.5 GB）に設定することを推奨しています。

1. `pipx` ユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します。

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. PyPIから `amd-debug-tools` wheelをインストールします。

   ```bash
   pipx install amd-debug-tools
   ```

3. 現在の共有メモリ設定を確認します。

   ```bash
   amd-ttm
   ```

4. 共有メモリの割り当てを増やします（単位はGB）。

   ```bash
   amd-ttm --set <NUM>
   ```

5. 変更を反映するために再起動してください。

<!-- @device:end -->

<!-- @os:end -->