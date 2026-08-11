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

vLLM, büyük dil modelleri (LLM'ler) için tasarlanmış yüksek performanslı bir çıkarım motorudur. Yüksek verim için sürekli gruplama (continuous batching) ile optimize edilmiş sunum sağlar ve sorunsuz uygulama entegrasyonu için OpenAI uyumlu bir API sunar. Bu özellikler, hızın ve kaynak verimliliğinin kritik olduğu üretim dağıtımları için vLLM'yi mükemmel bir seçim haline getirir.

Bu kılavuz, entegre GPU üzerinde konteynerleştirilmiş vLLM kullanarak LLM'leri nasıl sunacağınızı ve OpenAI Python API'si aracılığıyla modellerle nasıl etkileşime geçeceğinizi öğretir.

## Öğrenecekleriniz

- AMD ROCm™ desteğiyle bir vLLM sunucusunu nasıl kuracağınızı ve başlatacağınızı
- OpenAI uyumlu API uç noktaları aracılığıyla modellerle nasıl etkileşime geçeceğinizi
- `vllm-prompt` ile yerel sunucuya nasıl istem gönderileceğini

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

> **Not**: VS Code yüklü değilse, AMD Ryzen™ AI Geliştirici Merkezi ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

vLLM, ROCm ve bağımlılıklarının önceden eşleştirildiği önceden oluşturulmuş bir konteynerde çalışır. Ek bir kurulum gerekmez.

Ana makine tarafında bir vLLM kurulum adımı yoktur. vLLM'yi şununla başlatın:

```bash
vllm-launch
```

Başlatıcı, konteyneri başlatır, entegre GPU'yu hedefler ve yerel bir OpenAI uyumlu vLLM sunucusu sunar. Alternatif olarak, görev çubuğundaki vLLM simgesine tıklayın.

## Hızlı Başlangıç

### 1. vLLM Sunucusunun Çalıştığını Doğrulayın

`vllm-launch`'ın her şeyi başlatması birkaç dakika sürebilir. Başladığında, sunucu `http://localhost:8001` adresinde kullanılabilir olur. Sunucu ön planda çalıştığından başlatma terminalini açık tutun, ardından kalan adımlar için ayrı bir terminal açın. Aşağıdaki örnekler `Qwen/Qwen3-1.7B` kullanır; başlatıcınız farklı bir model için yapılandırılmışsa, isteklerde o model kimliğini kullanın.

### 2. Bir İstem Gönderin

Yerel vLLM OpenAI uyumlu sunucusuna bir istek göndermek için sağlanan `vllm-prompt` betiğini kullanın:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API'sini Kullanarak Modelle Sohbet Edin

vLLM, OpenAI uyumlu bir API sunduğundan, onunla etkileşime geçmek için `openai` Python paketini kullanabilirsiniz.

Öncelikle, bir Python sanal ortamı oluşturun:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

OpenAI paketini yükleyin
```bash
pip install openai
```

OpenAI'nin sunucuları yerine yerel vLLM sunucusuna yönlendirilmiş bir `OpenAI` istemcisi oluşturun. `api_key`, istemci tarafından gereklidir ancak vLLM bunu doğrulamaz, bu nedenle herhangi bir dize işe yarar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ardından, bir sohbet tamamlama isteği gönderin. Bu, OpenAI API'siyle aynı mesaj biçimini kullanır — `"user"` ve `"assistant"` gibi rollere sahip mesajlardan oluşan bir liste. `stream=True` ayarı, yanıtın tamamının bir kerede değil, kademeli olarak geleceği anlamına gelir:

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

Son olarak, akış halinde gelen parçalar üzerinde döngü kurun ve her metin parçasını geldiğinde yazdırın:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Dahil edilen [chat_with_model.py](assets/chat_with_model.py) betiği, tüm örneği içerir ve indirilebilir.


## Bir Model Seçme ve Yapılandırma

Varsayılan olarak, `vllm-launch`, `8001` portunda test modeli olarak `Qwen/Qwen3-1.7B`'yi sunar. Konteyneri yeniden oluşturmadan veya düzenlemeden modeli, portu ve vLLM sunum parametrelerini değiştirebilirsiniz.

### AMD tarafından test edilen modeller

Aşağıdaki modeller AMD tarafından önceden yapılandırılmış ve doğrulanmıştır:

| Model | Notlar |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Varsayılan model. Hafif ve hızlı yüklenir. |
| `openai/gpt-oss-20b` | Daha yüksek kaliteli yanıtlar için daha büyük model. |

### Farklı bir model başlatma

Model kimliğini `--model` (veya `-m`) ile geçirin:

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Portu değiştirme

1024'ün üzerinde bir portu `--port` (veya `-p`) ile geçirin; varsayılan `8001`'dir:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Portu değiştirirseniz, istemcinizin `base_url` değerini aynı porta yönlendirin (örneğin `http://localhost:8080/v1`).

### Ek vLLM parametreleri geçirme

Ek argümanların tümü doğrudan vLLM'ye iletilir, böylece bağlam uzunluğu veya veri türü gibi sunum davranışını ayarlayabilirsiniz. Bunları sağlamanın iki yolu vardır.

Başlatıcı seçeneklerinden sonra, **satır içi** olarak:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

`~/.local/share/vLLM/vllm-launch.conf` konumundaki bir yapılandırma dosyasında **kalıcı olarak**. Bu dosya varsayılan olarak mevcut değildir — oluşturun ve argümanlarınızı bir Bash dizisi olarak ekleyin:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Varsayılan argümanların yerine geçmek yerine onlara eklemek için `+=` kullanın:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Herhangi bir zamanda tüm başlatıcı seçeneklerini görmek için şunu çalıştırın:

```bash
vllm-launch --help
```

### Modellerin depolandığı yer

`vllm-launch`, modelleri iki konumda arar:

| Konum | Yol |
|----------|------|
| Sistem modelleri | `/var/cache/models` |
| Kullanıcı modelleri | `~/.local/share/vLLM/models` |

İndirilen bir modeli bu dizinlerden birine yerleştirebilir ve yolunu veya kimliğini `--model` ile geçirerek başlatabilirsiniz:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Not**: Kendi indirdiğiniz modeli bu şekilde çalıştırmanın, model yukarıdaki dizinlerden birine yerleştirildikten sonra çalışması beklenir, ancak bu iş akışı AMD tarafından henüz resmi olarak doğrulanmamıştır.

## Sorun Giderme

### Bağlantı reddedildi

Sunucunun çalıştığından emin olun:
```bash
curl http://localhost:8001/health
```

## Özet

Bu kılavuzda şunları öğrendiniz:

- Entegre GPU üzerinde ROCm desteğiyle konteynerleştirilmiş vLLM'yi başlatma
- Port 8001'de OpenAI uyumlu API uç noktalarıyla bir vLLM sunucusu başlatma
- `vllm-prompt` ile istem gönderme
- Hem akış hem de akış olmayan istekler kullanarak vLLM sunucusuna API çağrıları yapma
- Sunucu başlatma, bellek ve istemci bağlantılarıyla ilgili yaygın sorunları giderme

Artık entegre GPU üzerinde optimize edilmiş performansla büyük dil modellerini sunmak için konteynerleştirilmiş bir vLLM dağıtımına sahipsiniz.

## Sonraki Adımlar

- **Farklı modeller deneyin** — Farklı LLM'leri denemek ve performansı karşılaştırmak için `vllm-launch --model <model>` kullanın (bkz. [Bir Model Seçme ve Yapılandırma](#choosing-and-configuring-a-model)).
- **Bir uygulama oluşturun** — vLLM'yi bir Python uygulamasına, sohbet botuna veya otomasyon iş akışına entegre etmek için OpenAI uyumlu API'yi kullanın.
- **İnce ayar yapın ve sunun** — LoRA veya QLoRA kullanarak bir modele ince ayar yapın, ardından optimize edilmiş çıkarım için vLLM ile dağıtın.
## Ek Kaynaklar

- **[vLLM Resmi Dokümantasyonu](https://docs.vllm.ai/)** — Kapsamlı kılavuzlar ve API referansları
- **[vLLM GitHub Deposu](https://github.com/vllm-project/vllm)** — Kaynak kod, sorunlar ve topluluk tartışmaları