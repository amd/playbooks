<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmasını açıklar.

## Gerekli Uygulamalar/Çerçeveler

### Windows/Linux
Lemonade [buradan](https://lemonade-server.ai/install_options.html) önceden kurulmuş olmalıdır.

- **Open WebUI** (önyüz web uygulaması)
- **Lemonade Server** (arka uç model sunucusu)

> Bu playbook, **Lemonade**'i (Lemonade server/app) **yerel olarak** çalıştırır. **Open WebUI**, Linux'ta bir **konteyner** olarak (Podman üzerinden) ve Windows'ta bir **Python paketi** olarak çalışır. `open-webui` PyPI paketi yalnızca Python ≤ 3.12 sürümünü desteklediğinden, Linux konteyneri eski Python sürümlerini yönetme zorunluluğunu ortadan kaldırır.

## Modeller (Lemonade içinde)

Modeller, **Lemonade uygulaması** içinde (yerleşik Model Manager kullanılarak) veya Lemonade'in model yönetim komutları (`lemonade pull <model_name>`) aracılığıyla indirilmelidir. Bu playbook, aşağıda önerilen modellerin indirildiğini ve models list endpoint'inde göründüğünü varsayar.

Model kullanılabilirliğini kontrol edin:
- Açın: `http://localhost:13305/api/v1/models`
- İndirilen modeller `"data"` altında listelenecektir.

### Önerilen modeller

| Yetenek | Model ID | Notlar |
|---|----|-----|
| LLM (Metin girişi → Metin çıkışı) | `Qwen3-4B-Hybrid` (veya benzeri) | Sohbet, metin tamamlama, kodlama veya akıl yürütme için herhangi bir Lemonade LLM modeli |
| VLM (Görüntü → Metin) | `Qwen3.5-4B-GGUF` (veya **Vision** kategorisindeki herhangi bir model) | Görüntüleri girdilerinin bir parçası olarak alabilen herhangi bir çok modlu/görsel yetenekli model |
| Görüntü Üretimi (Metin → Görüntü) | `SDXL-Turbo` (veya **Image** kategorisindeki herhangi bir model) | Bir metin isteminden görüntü üreten herhangi bir Stable Diffusion modeli |
| Ses (Konuşma → Metin) | `Whisper-Large-v3` (veya **Audio** kategorisindeki herhangi bir model) | Sesi metne dönüştüren herhangi bir ASR modeli |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Kullanılan portlar

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Bu portlar sisteminizde zaten kullanılıyorsa, sunucu(lar)ı başlatırken bunları değiştirin.