<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Haloの場合、専用GPUメモリのデフォルトは64GBで、ほとんどのワークロードには十分です。より大きなモデルやより長いコンテキストの場合、これを96GBに増やすと役立つことがあります。調整するには、**AMD Software: Adrenalin Edition™**を開き、**Performance → Tuning → AMD Variable Graphics Memory**に移動します。変更を反映させるには再起動が必要です。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

専用GPUメモリの値を変更するには、**AMD Software: Adrenalin Edition™**を開き、**Performance → Tuning → AMD Variable Graphics Memory**に移動します。変更を反映させるには再起動が必要です。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linuxでは、より大きなモデルを実行するには、GPUで利用可能な**共有メモリ**プールを増やします。これには、共有メモリプールを最大化できるよう、BIOSの専用GPUメモリを最小値に設定することが必要な場合があります。

<!-- @device:halo_box -->

AMD Ryzen™ AI Haloの場合、デフォルトは96GB共有です。これを変更するには、**AMD Ryzen™ AI Developer Center**を開き、**Settings**タブに移動します。**Graphics Performance Settings**の下で、**Shared Video Memory**スライダーを増やし、**Apply Changes**をクリックして、変更を反映させるために再起動します。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

カーネルのTranslation Table Manager (TTM) ページ設定を変更することで、共有メモリプールを増やします。AMDは、最大量を共有メモリとして利用できるよう、BIOSで専用VRAMを最小値（0.5 GB）に設定することを推奨しています。

1. `pipx`ユーティリティをインストールし、pipxでインストールされたwheelのパスをシステムの検索パスに追加します：

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. PyPIから`amd-debug-tools`のwheelをインストールします：

   ```bash
   pipx install amd-debug-tools
   ```

3. 現在の共有メモリ設定を確認します：

   ```bash
   amd-ttm
   ```

4. 共有メモリの割り当てを増やします（単位はGB）：

   ```bash
   amd-ttm --set <NUM>
   ```

5. 変更を反映させるには再起動が必要です。

<!-- @device:end -->

<!-- @os:end -->