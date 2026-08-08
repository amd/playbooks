<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklar.

## Windows

### LM Studio Kurulumu

LM Studio önceden kurulmuş olmalıdır:

| Bileşen | Sürüm | Konum |
|-----------|---------|----------|
| **LM Studio (Modeller + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Önbellek)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model İndirme

Aşağıdaki modeller LM Studio modeller dizininde (`C:\Users\...\.lmstudio\models`) zaten bulunuyor olmalıdır:

| Cihaz | Model Türü | Nicemleme | Boyut (GB) | Konum |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio Kurulumu

Daha fazla bilgi için bkz. [lmstudio.md](../../dependencies/lmstudio.md).

### Model İndirme

Windows'takiyle aynıdır.