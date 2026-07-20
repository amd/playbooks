# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Ön Koşullar

ROCm desteğine sahip PyTorch, AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiştir. Diğer tüm cihazlarda kullanıcıların ROCm desteğine sahip PyTorch'u manuel olarak yüklemesi gerekir. Lütfen işletim sisteminize uygun bölüme bakın:

### Windows

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

### Linux

| Bileşen     | Sürüm         | Notlar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 veya daha yeni    | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

## Gerekli Modeller

Aşağıdaki modeller platformunuz için test edilmiş ve optimize edilmiştir:

| Model | Parametreler | Boyut | İndirme Konumu |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | AMD Ryzen AI Halo Developer Platform üzerinde önceden yüklenmiştir; diğer tüm cihazlarda manuel olarak yüklenmelidir |

Modeller otomatik olarak Hugging Face önbellek dizinine indirilecektir:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Model depolama için en az **20 GB boş alan** ayırdığınızdan emin olun.

## Ağ Gereksinimleri

İlk kurulum, Hugging Face'ten model indirmek için internet erişimi gerektirir. İndirme işleminden sonra playbook çevrimdışı olarak çalışabilir.

- İlk model indirmeleri, model boyutuna ve bağlantı hızına bağlı olarak **5-10 dakika** sürebilir
- Modeller yerel olarak önbelleğe alınır ve tekrar indirilmesi gerekmez