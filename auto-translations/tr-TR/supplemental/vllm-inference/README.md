<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Genel Bakış

vLLM, büyük dil modelleri (LLM) için tasarlanmış yüksek performanslı bir çıkarım motorudur. Yüksek verim için sürekli gruplama (continuous batching) özelliğiyle optimize edilmiş sunum ve sorunsuz uygulama entegrasyonu için OpenAI uyumlu bir API sağlar. Bu özellikler, vLLM'i hız ve kaynak verimliliğinin kritik önem taşıdığı üretim dağıtımları için mükemmel bir seçim haline getirir.

Bu kılavuz, entegre GPU üzerinde container'laştırılmış vLLM kullanarak LLM'leri nasıl sunacağınızı ve modellerle OpenAI Python API aracılığıyla nasıl etkileşim kuracağınızı öğretir.

## Öğrenecekleriniz

- AMD ROCm™ desteğiyle bir vLLM sunucusunun nasıl kurulup başlatılacağı
- OpenAI uyumlu API uç noktaları üzerinden modellerle nasıl etkileşim kurulacağı
- `vllm-prompt` ile yerel sunucuya nasıl komut gönderileceği

## Bellek Yapılandırmasının Ayarlanması
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin

> **Not**: VS Code yüklü değilse, AMD Ryzen™ AI Developer Center ile yükleyebilirsiniz.
<!-- @require:software-update -->
<!-- @device:end -->
## Yazılım Ön Koşullarının Yüklenmesi

vLLM, ROCm ve bağımlılıklarının önceden eşleştirildiği önceden oluşturulmuş bir konteyner içinde çalışır. Ek bir yükleme gerekmez.

Ana makine tarafında vLLM yükleme adımı yoktur. vLLM'i şununla başlatın:

```bash
vllm-launch
```

Başlatıcı, konteyneri çalıştırır, entegre GPU'yu hedefler ve OpenAI uyumlu yerel bir vLLM sunucusu sunar. Alternatif olarak, görev çubuğundaki vLLM simgesine tıklayın.

## Hızlı Başlangıç

### 1. vLLM Sunucusunun Çalıştığını Doğrulayın

`vllm-launch`, her şeyi başlatmak için birkaç dakika sürebilir. Başladıktan sonra sunucu `http://localhost:8001` adresinde kullanılabilir olur. Sunucu ön planda çalıştığı için başlatma terminalini açık tutun, ardından kalan adımlar için ayrı bir terminal açın. Aşağıdaki örneklerde `Qwen/Qwen3-1.7B` kullanılmaktadır; başlatıcınız farklı bir model için yapılandırılmışsa isteklerde o model kimliğini kullanın.

### 2. Bir İstem (Prompt) Gönderin

Yerel vLLM OpenAI uyumlu sunucusuna bir istek göndermek için sağlanan `vllm-prompt` betiğini kullanın:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API kullanarak modelle sohbet edin

vLLM, OpenAI uyumlu bir API sunduğundan, onunla etkileşim kurmak için `openai` Python paketini kullanabilirsiniz.

Öncelikle bir Python sanal ortamı oluşturun:
<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->
OpenAI paketini yükleyin
```bash
pip install openai
```

OpenAI'nin sunucuları yerine yerel vLLM sunucusuna yönlendirilmiş bir `OpenAI` istemcisi oluşturun. İstemci için `api_key` gereklidir, ancak vLLM bunu doğrulamaz, bu yüzden herhangi bir dize işe yarar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ardından, bir sohbet tamamlama (chat completion) isteği gönderin. Bu, OpenAI API ile aynı mesaj biçimini kullanır — `"user"` ve `"assistant"` gibi rollere sahip bir mesaj listesi. `stream=True` ayarlanması, yanıtın tek seferde değil, aşamalı olarak gelmesini sağlar:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

İşte son adım: akışla gelen (streamed) parçalar üzerinde döngü kurun ve her bir metin parçasını geldiği anda yazdırın:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

İndirilebilir [chat_with_model.py](assets/chat_with_model.py) betiği, örneğin tamamını içerir.

## Model Seçme ve Yapılandırma

Varsayılan olarak, `vllm-launch`, test modeli olarak `Qwen/Qwen3-1.7B`'yi `8001` portunda sunar. Modeli, portu ve vLLM sunum parametrelerini konteyneri yeniden oluşturmadan veya düzenlemeden değiştirebilirsiniz.

### AMD tarafından test edilen modeller

Aşağıdaki modeller AMD tarafından önceden yapılandırılmış ve doğrulanmıştır:

| Model | Notlar |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Varsayılan model. Hafif ve hızlı yüklenir. |
| `openai/gpt-oss-20b` | Daha yüksek kaliteli yanıtlar için daha büyük model. |

### Farklı bir model başlatma

Model kimliğini `--model` (veya `-m`) ile iletin:

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Portu değiştirme

`--port` (veya `-p`) ile 1024'ün üzerinde bir port belirtin; varsayılan değer `8001`'dir:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Bağlantı noktasını değiştirirseniz, istemcinizin `base_url` değerini aynı bağlantı noktasına yönlendirin (örneğin `http://localhost:8080/v1`).

### Ek vLLM parametrelerinin geçirilmesi

Eklenen tüm ek bağımsız değişkenler doğrudan vLLM'e iletilir, böylece bağlam uzunluğu veya veri türü gibi sunum davranışlarını ayarlayabilirsiniz. Bunları sağlamanın iki yolu vardır.

**Satır içi**, başlatıcı seçeneklerinden sonra:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Kalıcı olarak**, `~/.local/share/vLLM/vllm-launch.conf` konumundaki bir yapılandırma dosyasında. Bu dosya varsayılan olarak mevcut değildir — oluşturun ve argümanlarınızı bir Bash dizisi olarak ekleyin:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

`+=` kullanarak varsayılan argümanlara, onların yerine geçmek yerine ekleme yapın:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Herhangi bir zamanda tüm başlatıcı seçeneklerini görmek için şunu çalıştırın:

```bash
vllm-launch --help
```

### Modellerin saklandığı konum

`vllm-launch`, modelleri iki konumda arar:

| Konum | Yol |
|----------|------|
| Sistem modelleri | `/var/cache/models` |
| Kullanıcı modelleri | `~/.local/share/vLLM/models` |

İndirilen bir modeli bu dizinlerden birine yerleştirip yolunu veya kimliğini `--model` parametresine vererek başlatabilirsiniz:

```bash
vllm-launch --model /var/cache/models/my-model
```

**Not**: Kendi indirdiğiniz modeli bu şekilde çalıştırmanın, model yukarıdaki dizinlerden birine yerleştirildiğinde çalışması beklenir, ancak bu iş akışı henüz AMD tarafından resmi olarak doğrulanmamıştır.

## Sorun Giderme

### Bağlantı reddedildi

Sunucunun çalıştığından emin olun:
```bash
curl http://localhost:8001/health
```

## Özet

Bu kılavuzda şunları öğrendiniz:

- Entegre GPU üzerinde ROCm destekli konteynerleştirilmiş vLLM'yi başlatma
- 8001 portunda OpenAI uyumlu API uç noktalarına sahip bir vLLM sunucusu başlatma
- `vllm-prompt` ile prompt gönderme
- Hem akışlı hem de akışsız istekler kullanarak vLLM sunucusuna API çağrıları yapma
- Sunucu başlatma, bellek ve istemci bağlantılarıyla ilgili yaygın sorunları giderme

Artık entegre GPU üzerinde optimize edilmiş performansla büyük dil modellerini sunmak için konteynerleştirilmiş bir vLLM dağıtımına sahipsiniz.

## Sonraki Adımlar

- **Farklı modeller deneyin** — Farklı LLM'leri denemek ve performansı karşılaştırmak için `vllm-launch --model <model>` komutunu kullanın (bkz. [Model Seçme ve Yapılandırma](#choosing-and-configuring-a-model)).
- **Bir uygulama oluşturun** — vLLM'yi bir Python uygulamasına, sohbet botuna veya otomasyon iş akışına entegre etmek için OpenAI uyumlu API'yi kullanın.
- **İnce ayar yapın ve sunun** — LoRA veya QLoRA kullanarak bir modele ince ayar yapın, ardından optimize edilmiş çıkarım için vLLM ile dağıtın.
## Ek Kaynaklar

- **[vLLM Resmi Dokümantasyonu](https://docs.vllm.ai/)** — Kapsamlı kılavuzlar ve API referansları
- **[vLLM GitHub Deposu](https://github.com/vllm-project/vllm)** — Kaynak kodu, sorunlar ve topluluk tartışmaları