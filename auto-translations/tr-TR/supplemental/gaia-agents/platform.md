<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Yapılandırması

Bu belge, bu senaryoyu (playbook) çalıştırmak için beklenen platform yapılandırmalarını açıklar.

## Gerekli Uygulamalar/Çerçeveler

### Windows/Linux

GAIA, [GAIA Installation Guide](../../dependencies/gaia.md) belgesinde sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

Lemonade Server, [Lemonade Installation Guide](../../dependencies/lemonade.md) belgesinde sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

## Gerekli Modeller

### Windows/Linux

Hardware Advisor Agent, aracı (agent) muhakemesi için **Qwen3-Coder-30B** kullanır. Bu model, `gaia init` sırasında otomatik olarak indirilir. Manuel model indirmesi gerekmez.