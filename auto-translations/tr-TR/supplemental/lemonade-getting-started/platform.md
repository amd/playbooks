<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration — Lemonade Local AI

Bu belge, bu kılavuzun varsaydığı önceden yüklenmiş yazılımları, model yollarını ve platforma özgü ön koşulları açıklar.

## Önceden Yüklenmiş Yazılım

| Yazılım | Sürüm | Amaç |
|----------|---------|---------|
| Lemonade Server | En son sürüm | OpenAI uyumlu API'ye sahip yerel LLM sunucusu |
| Python | 3.10–3.13 | OpenAI Python istemcisi örneği için gereklidir |

## Varsayılan Model Depolama

Lemonade aracılığıyla indirilen modeller, Hugging Face Hub spesifikasyonu kullanılarak depolanır:

| Platform | Varsayılan Yol |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Depolama konumunu değiştirmek için `HF_HOME` ortam değişkenini ayarlayın.

## Donanım Gereksinimleri

| Donanım Hedefi | Gereksinimler |
|----------------|-------------|
| **CPU** | Herhangi bir modern x86-64 işlemci (AMD veya Intel) |
| **GPU (Vulkan)** | Vulkan sürücü desteğine sahip herhangi bir GPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 serisi veya Radeon PRO W7000 serisi; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 serisi işlemci, Windows 11 |

## Ağ Gereksinimleri

- İlk model indirmesi için internet bağlantısı gereklidir (modele bağlı olarak 1–25 GB)
- Modeller indirildikten sonra internete gerek yoktur