<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo için ayrılmış GPU belleği varsayılan olarak 64 GB'tır; bu, çoğu iş yükü için yeterlidir. Daha büyük modeller veya daha uzun bağlamlar için bunu 96 GB'a çıkarmak yardımcı olabilir. Ayarlamak için **AMD Software: Adrenalin Edition™** uygulamasını açın ve **Performance → Tuning → AMD Variable Graphics Memory** yolunu izleyin. Değişikliklerin geçerli olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Ayrılmış GPU belleği değerini değiştirmek için **AMD Software: Adrenalin Edition™** uygulamasını açın ve **Performance → Tuning → AMD Variable Graphics Memory** yolunu izleyin. Değişikliklerin geçerli olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linux'ta daha büyük modeller çalıştırmak için GPU'ya sunulan **paylaşılan bellek** havuzunu artırın. Bu, paylaşılan bellek havuzunun en üst düzeye çıkarılabilmesi için BIOS'taki ayrılmış GPU belleğinin minimum değere ayarlanmasını gerektirebilir.

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo için varsayılan değer 96 GB paylaşılan bellektir. Bunu değiştirmek için **AMD Ryzen™ AI Developer Center** uygulamasını açın ve **Settings** sekmesine gidin. **Graphics Performance Settings** altında **Shared Video Memory** kaydırıcısını artırın, ardından **Apply Changes** düğmesine tıklayın ve değişikliklerin geçerli olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Çekirdeğin Translation Table Manager (TTM) sayfa ayarını değiştirerek paylaşılan bellek havuzunu artırın. AMD, maksimum miktarın paylaşılan bellek olarak kullanılabilmesi için BIOS'ta minimum ayrılmış VRAM (0,5 GB) ayarlanmasını önerir.

1. `pipx` yardımcı programını yükleyin ve pipx ile yüklenen wheel'lerin yolunu sistem arama yoluna ekleyin:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. `amd-debug-tools` wheel'ini PyPI'dan yükleyin:

   ```bash
   pipx install amd-debug-tools
   ```

3. Mevcut paylaşılan bellek ayarlarını sorgulayın:

   ```bash
   amd-ttm
   ```

4. Paylaşılan bellek tahsisini artırın (birim GB cinsinden):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Değişikliklerin geçerli olması için yeniden başlatın.

<!-- @device:end -->

<!-- @os:end -->