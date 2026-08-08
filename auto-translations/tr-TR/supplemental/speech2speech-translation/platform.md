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

## Prerequisites

ROCm desteğine sahip PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiştir. Diğer tüm cihazlarda kullanıcıların ROCm destekli PyTorch'u manuel olarak yüklemesi gerekir. Lütfen işletim sisteminize uygun bölüme bakın:

### Windows

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 or newer    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklüdür; diğer tüm cihazlarda manuel olarak yüklenmelidir |

### Linux

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 or newer    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklüdür; diğer tüm cihazlarda manuel olarak yüklenmelidir |

## Required Models

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parameters | Size | Download Location |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklüdür; diğer tüm cihazlarda manuel olarak yüklenmelidir |

Modeller, Hugging Face önbellek dizinine otomatik olarak indirilecektir:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Model depolama için en az **20GB boş alan** olduğundan emin olun.

## Network Requirements

İlk kurulum, Hugging Face'ten model indirmek için internet erişimi gerektirir. İndirme işleminden sonra playbook çevrimdışı olarak çalıştırılabilir.

- İlk model indirmeleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve tekrar indirilmesi gerekmez