# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Ön Koşullar

ROCm destekli PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerine önceden yüklenmiş olarak gelir. Diğer tüm cihazlar için kullanıcıların ROCm destekli PyTorch'u manuel olarak yüklemesi gerekmektedir. Lütfen işletim sisteminize uygun bölüme başvurun:

### Windows

| Bileşen       | Sürüm           | Notlar                            |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerine önceden yüklenmiş olarak gelir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

### Linux

| Bileşen       | Sürüm           | Notlar                            |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerine önceden yüklenmiş olarak gelir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

## Gerekli Modeller

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parametreler | Boyut | İndirme Konumu |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | AMD Ryzen AI Halo Developer Platform üzerine önceden yüklenmiş olarak gelir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

Modeller otomatik olarak Hugging Face önbellek dizinine indirilecektir:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Model depolama alanı için en az **20 GB boş alan** bulundurun.

## Ağ Gereksinimleri

İlk kurulum, Hugging Face'ten model indirmek için internet erişimi gerektirir. İndirme işleminin ardından playbook çevrimdışı olarak çalıştırılabilir.

- İlk kez model indirme işlemleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve yeniden indirilmesi gerekmez