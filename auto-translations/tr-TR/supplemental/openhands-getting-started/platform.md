<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizceden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Hatalar içerebilir ve bazı adımlar, komutlar, indirmeler veya ürün kullanılabilirliği dilinize veya bölgenize göre farklılık gösterebilir. Yanlış görünen bir şey varsa, orijinal İngilizce playbook'u kaynak olarak kabul edin.
<!-- auto-translated-disclaimer:end -->

# Platform Yapılandırması

Bu belge, bu senaryonun (playbook) çalıştırılması için beklenen platform yapılandırmalarını açıklamaktadır.

## Gerekli Uygulamalar/Framework'ler

### Windows/Linux

- **Lemonade Server**, [Lemonade kurulum kılavuzu](https://lemonade-server.ai/docs/guide/install/) izlenerek kurulmalıdır.
- `agent-canvas` CLI tarafından kullanılan **Node.js 22.12 veya üzeri** ve `npm`.
- Agent Canvas'ın agent sunucu ortamını yönetmek için kullandığı Python paket yöneticisi **uv**. [uv kurulum kılavuzundan](https://docs.astral.sh/uv/getting-started/installation/) kurabilirsiniz.

## Gerekli Modeller

### Windows/Linux

Senaryoya (playbook) başlamadan önce aşağıdaki modelin Lemonade Server için hazır olması gerekir.

| Model Türü | Model ID | Notlar |
| --- | --- | --- |
| GGUF sohbet modeli | `Qwen3.6-35B-A3B-GGUF` | `http://127.0.0.1:13305/api/v1` üzerinden Lemonade Server tarafından sunulur. 32 GB'den az belleğe sahip cihazlarda daha küçük bir GGUF modeli kullanın. |

Modeli aşağıdakiyle başlatın:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
