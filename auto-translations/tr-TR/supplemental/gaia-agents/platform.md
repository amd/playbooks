<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Gerekli Uygulamalar/Çerçeveler

### Windows/Linux

GAIA, [GAIA Kurulum Kılavuzu](../../dependencies/gaia.md) içinde sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

Lemonade Server, [Lemonade Kurulum Kılavuzu](../../dependencies/lemonade.md) içinde sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

## Gerekli Modeller

### Windows/Linux

Donanım Danışmanı Ajanı, ajan akıl yürütmesi için **Qwen3-Coder-30B** kullanır. Bu model, `gaia init` sırasında otomatik olarak indirilir. Manuel model indirmesi gerekmez.