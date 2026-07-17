<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration — Lemonade Local AI

Bu belge, bu playbook tarafından varsayılan olarak kullanılan önceden yüklenmiş yazılımları, model yollarını ve platforma özgü ön koşulları açıklamaktadır.

## Önceden Yüklenmiş Yazılımlar

| Yazılım | Sürüm | Amaç |
|----------|---------|---------|
| Lemonade Server | En son sürüm | OpenAI uyumlu API ile yerel LLM sunucusu |
| Python | 3.10–3.13 | OpenAI Python istemci örneği için gereklidir |

## Varsayılan Model Depolama Alanı

Lemonade aracılığıyla indirilen modeller, Hugging Face Hub belirtimine göre depolanır:

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
- Modeller indirildikten sonra internet bağlantısı gerekmez