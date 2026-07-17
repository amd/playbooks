<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmasını açıklamaktadır.

## Gerekli Uygulamalar/Çerçeveler

### Windows/Linux
Lemonade, [buradan](https://lemonade-server.ai/install_options.html) önceden yüklenmiş olmalıdır.

- **Open WebUI** (ön uç web uygulaması)
- **Lemonade Server** (arka uç model sunucusu)

> Bu playbook, **Lemonade**'i (Lemonade sunucu/uygulama) **yerel olarak** çalıştırır. **Open WebUI**, Linux'ta (Podman aracılığıyla) bir **konteyner** olarak ve Windows'ta bir **Python paketi** olarak çalışır. `open-webui` PyPI paketi yalnızca Python ≤ 3.12'yi desteklediğinden, Linux konteyneri eski Python sürümlerini yönetme zorunluluğunu ortadan kaldırır.

## Modeller (Lemonade'de)

Modeller, **Lemonade uygulaması** içinde (yerleşik Model Yöneticisi kullanılarak) veya Lemonade'in model yönetim komutları (`lemonade pull <model_name>`) aracılığıyla indirilmelidir. Bu playbook, aşağıda önerilen modellerin indirilmiş olduğunu ve modeller listesi uç noktasında göründüğünü varsayar.

Model kullanılabilirliğini kontrol edin:
- Açın: `http://localhost:13305/api/v1/models`
- İndirilen modeller `"data"` altında listelenecektir.

### Önerilen modeller

| Yetenek | Model ID | Notlar |
|---|----|-----|
| LLM (Metin girişi → Metin çıkışı) | `Qwen3-4B-Hybrid` (veya benzeri) | Sohbet, metin tamamlama, kodlama veya akıl yürütme için herhangi bir Lemonade LLM modeli |
| VLM (Görüntü → Metin) | `Qwen3.5-4B-GGUF` (veya **Vision** kategorisindeki herhangi bir model) | Girişlerinin bir parçası olarak görüntü alabilen herhangi bir çok modlu/görme yetenekli model |
| Görüntü Oluşturma (Metin → Görüntü) | `SDXL-Turbo` (veya **Image** kategorisindeki herhangi bir model) | Bir metin istemi için görüntü oluşturan herhangi bir Stable Diffusion modeli |
| Ses (Konuşma → Metin) | `Whisper-Large-v3` (veya **Audio** kategorisindeki herhangi bir model) | Sesi metne dönüştüren herhangi bir ASR modeli |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Kullanılan Portlar

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Bu portlar sisteminizde zaten kullanılıyorsa, sunucu(ları) başlatırken bunları değiştirin.