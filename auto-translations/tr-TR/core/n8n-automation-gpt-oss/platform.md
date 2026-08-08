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

## Ön Koşullar

### Windows

| Bileşen | Sürüm | Notlar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiş ve PATH içinde kullanılabilir durumdadır; diğer tüm cihazlarda manuel olarak yüklenmelidir |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1` üzerinde çalışıyor |

### Linux

| Bileşen | Sürüm | Notlar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform üzerinde önceden yüklenmiş ve PATH içinde kullanılabilir durumdadır; diğer tüm cihazlarda manuel olarak yüklenmelidir |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1` üzerinde çalışıyor |


## Lemonade LLM

Lemonade sunucusu, cihaza uygun model yüklenmiş şekilde çalışıyor olmalıdır (cihazınız için `lemonade run` komutuna ilişkin README dosyasına bakın):

| Cihaz | Uç Nokta | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |