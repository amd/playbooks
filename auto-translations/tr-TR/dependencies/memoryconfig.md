<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo için, ayrılmış GPU belleği varsayılan olarak 64GB'dır ve bu, çoğu iş yükü için yeterlidir. Daha büyük modeller veya daha uzun bağlamlar için bu değeri 96GB'a yükseltmek yardımcı olabilir. Ayarlamak için **AMD Software: Adrenalin Edition™**'ı açın ve **Performance → Tuning → AMD Variable Graphics Memory** yolunu izleyin. Değişikliklerin etkili olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Ayrılmış GPU belleği değerini değiştirmek için **AMD Software: Adrenalin Edition™**'ı açın ve **Performance → Tuning → AMD Variable Graphics Memory** yolunu izleyin. Değişikliklerin etkili olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linux'ta daha büyük modelleri çalıştırmak için, GPU'ya ayrılan **paylaşımlı bellek** havuzunu artırın. Bu, paylaşımlı bellek havuzunun en üst düzeye çıkarılabilmesi için BIOS'taki ayrılmış GPU belleğini minimuma ayarlamayı gerektirebilir.

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo için varsayılan değer 96GB paylaşımlıdır. Bunu değiştirmek için **AMD Ryzen™ AI Developer Center**'ı açın ve **Settings** sekmesine gidin. **Graphics Performance Settings** altında, **Shared Video Memory** kaydırıcısını artırın, ardından **Apply Changes**'e tıklayın ve değişikliklerin etkili olması için yeniden başlatın.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

Çekirdeğin Translation Table Manager (TTM) sayfa ayarını değiştirerek paylaşımlı bellek havuzunu artırın. AMD, maksimum miktarın paylaşımlı bellek olarak kullanılabilir olması için BIOS'ta minimum ayrılmış VRAM'in (0.5 GB) ayarlanmasını önerir.

1. `pipx` aracını yükleyin ve pipx ile yüklenen wheel'lerin yolunu sistem arama yoluna ekleyin:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. `amd-debug-tools` wheel'ini PyPI'den yükleyin:

   ```bash
   pipx install amd-debug-tools
   ```

3. Mevcut paylaşımlı bellek ayarlarını sorgulayın:

   ```bash
   amd-ttm
   ```

4. Paylaşımlı bellek ayrımını artırın (birimler GB cinsindendir):

   ```bash
   amd-ttm --set <NUM>
   ```

5. Değişikliklerin etkili olması için yeniden başlatın.

<!-- @device:end -->

<!-- @os:end -->