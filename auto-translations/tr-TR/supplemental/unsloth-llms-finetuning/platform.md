# Platform Konfigürasyonu

Bu belge, bu playbook'un çalıştırılması için beklenen platform konfigürasyonlarını açıklar.

## Ön Koşullar

ROCm desteğine sahip PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiş olarak gelir. Diğer tüm cihazlarda kullanıcıların ROCm desteğine sahip PyTorch'u manuel olarak yüklemesi gerekir. Lütfen işletim sisteminize uygun bölüme bakın:


### Windows

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklüdür; diğer tüm cihazlarda manuel olarak yüklenmelidir |


### Linux

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklüdür; diğer tüm cihazlarda manuel olarak yüklenmelidir |


## Gerekli Modeller

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parametreler | Boyut | İndirme Konumu |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | HF'den indirin

Modeller otomatik olarak Hugging Face önbellek dizinine indirilecektir: `~/.cache/huggingface/hub/`

Model depolama için en az **20GB boş alan** olduğundan emin olun.

## Ağ Gereksinimleri

İlk kurulum, modelleri Hugging Face'ten indirmek için internet erişimi gerektirir. İndirme işleminden sonra playbook çevrimdışı olarak çalışabilir.

- İlk model indirmeleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve tekrar indirilmesi gerekmez