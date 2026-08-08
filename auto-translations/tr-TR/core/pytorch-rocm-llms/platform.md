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

## Ön Koşullar

ROCm desteğine sahip PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiş olarak gelir. Diğer tüm cihazlar için kullanıcıların ROCm destekli PyTorch'u manuel olarak yüklemesi gerekir. Lütfen işletim sisteminize uygun bölüme bakın:

### Windows

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

### Linux

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

## Gerekli Modeller

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parametreler | Boyut | İndirme Konumu |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

Modeller otomatik olarak Hugging Face önbellek dizinine indirilecektir:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Model depolama için en az **50GB boş alan** bulunduğundan emin olun.

## Ağ Gereksinimleri

İlk kurulum, modelleri Hugging Face'ten indirmek için internet erişimi gerektirir. İndirme işleminden sonra playbook çevrimdışı çalışabilir.

- İlk kez model indirmeleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve yeniden indirilmesine gerek yoktur