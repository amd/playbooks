<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Önkoşullar

ROCm desteğine sahip PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiştir. Diğer tüm cihazlar için kullanıcıların ROCm desteğine sahip PyTorch'u manuel olarak yüklemesi gerekir. Lütfen işletim sisteminize uygun bölüme bakın:


### Windows

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |


### Linux

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |


## Gerekli Modeller

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parametreler | Boyut | İndirme Konumu |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | HF'den indirin

Modeller otomatik olarak Hugging Face önbellek dizinine indirilecektir: `~/.cache/huggingface/hub/`

Model depolama için en az **20 GB boş alan** olduğundan emin olun.

## Ağ Gereksinimleri

İlk kurulum, Hugging Face'ten model indirmek için internet erişimi gerektirir. İndirme işleminden sonra, playbook çevrimdışı olarak çalıştırılabilir.

- İlk model indirmeleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve yeniden indirilmesi gerekmez