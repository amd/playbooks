<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklar.

## Gerekli Uygulamalar/Çerçeveler

### Windows/Linux

- **Lemonade Server**,
  [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/) izlenerek kurulmalıdır.
- `agent-canvas` CLI ve `npx` ile başlatılan MCP
  sunucuları tarafından kullanılan **Node.js 22.12 veya üzeri** ve `npm`.
- Agent Canvas'ın aracı
  sunucu ortamını yönetmek için kullandığı Python paket yöneticisi **uv**. Şu adresten kurun:
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Gerekli Modeller

### Windows/Linux

Playbook'a başlamadan önce aşağıdaki modelin Lemonade Server'da
kullanılabilir olması gerekir.

| Model Türü | Model Kimliği | Notlar |
| --- | --- | --- |
| GGUF chat modeli | `Qwen3.6-35B-A3B-GGUF` | Lemonade Server tarafından `http://127.0.0.1:13305/api/v1` üzerinden sunulur. 32 GB'den az belleğe sahip cihazlarda daha küçük bir GGUF modeli kullanın. |

Modeli şu şekilde başlatın:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Harici Kimlik Bilgileri

Bu playbook şunları gerektirir:

- Özetlenen depoya okuma erişimine sahip bir GitHub token'ı.
- `chat:write` ve kanal okuma erişimine sahip bir Slack bot token'ı.
- Bir Slack takım kimliği ve hedef Slack kanal kimliği.