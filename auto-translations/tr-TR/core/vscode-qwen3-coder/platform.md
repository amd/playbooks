<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Yapılandırması

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

Aşağıdaki modeller LM Studio modeller dizininde (`C:\Users\...\.lmstudio\models`) zaten mevcut olmalıdır:

| Model Türü | Nicemleme | Boyut | Konum |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio Kurulumu

Daha fazla ayrıntı için lmstudio.md (dependencies klasörü içinde) dosyasına bakın.

### Model İndirme

Windows ile aynıdır.