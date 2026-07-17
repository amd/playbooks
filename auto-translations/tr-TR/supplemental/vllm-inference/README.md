<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->


## Genel Bakış

vLLM, büyük dil modelleri (LLM'ler) için tasarlanmış yüksek performanslı bir çıkarım motorudur. Yüksek verim için sürekli toplu işleme ile optimize edilmiş sunma ve sorunsuz uygulama entegrasyonu için OpenAI uyumlu bir API sağlar. Bu, vLLM'yi hız ve kaynak verimliliğinin kritik olduğu üretim dağıtımları için mükemmel kılar.

Bu playbook, entegre GPU üzerinde kapsayıcılı vLLM kullanarak LLM'leri nasıl sunacağınızı ve OpenAI Python API'si aracılığıyla modellerle nasıl etkileşim kuracağınızı öğretir.

## Neler Öğreneceksiniz

- AMD ROCm™ desteğiyle bir vLLM sunucusunu nasıl kurar ve başlatırsınız
- OpenAI uyumlu API uç noktaları aracılığıyla modellerle nasıl etkileşim kurarsınız
- `vllm-prompt` ile yerel sunucuya nasıl istem gönderirsiniz

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

> **Not**: VS Code yüklü değilse, AMD Ryzen™ AI Geliştirici Merkezi ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

Bu playbook, vLLM, ROCm desteği ve sunucuyu başlatmak için gereken yardımcı betikleri içeren önceden oluşturulmuş bir kapsayıcı görüntüsü kullanır. PyTorch, vLLM veya yerel playbook betiklerini manuel olarak yüklemeniz gerekmez.

Ana bilgisayar tarafında vLLM yükleme adımı yoktur. vLLM'yi şu komutla başlatın:

```bash
vllm-launch
```

Başlatıcı, kapsayıcıyı başlatır, entegre GPU'yu hedefler ve yerel bir OpenAI uyumlu vLLM sunucusunu açığa çıkarır. Alternatif olarak, görev çubuğundaki vLLM simgesine tıklayabilirsiniz.

## Hızlı Başlangıç

### 1. vLLM Sunucusunun Çalıştığını Doğrulayın

`vllm-launch` her şeyi başlatmak için birkaç dakika sürebilir. Başladıktan sonra sunucu `http://localhost:8001` adresinde kullanılabilir. Sunucu ön planda çalıştığından başlatma terminalini açık tutun, ardından kalan adımlar için ayrı bir terminal açın. Aşağıdaki örnekler `Qwen/Qwen3-1.7B` kullanmaktadır; başlatıcınız farklı bir model için yapılandırılmışsa, isteklerde o model kimliğini kullanın.

### 2. İstem Gönderin

Yerel vLLM OpenAI uyumlu sunucusuna istek göndermek için sağlanan `vllm-prompt` betiğini kullanın:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API'sini Kullanarak Modelle Sohbet Edin

vLLM, OpenAI uyumlu bir API sunduğundan, onunla etkileşim kurmak için `openai` Python paketini kullanabilirsiniz.

Önce bir Python sanal ortamı oluşturun:

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

OpenAI'nin sunucuları yerine yerel vLLM sunucusuna yönlendirilmiş bir `OpenAI` istemcisi oluşturun. `api_key` istemci tarafından gereklidir ancak vLLM bunu doğrulamaz, dolayısıyla herhangi bir dize işe yarar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ardından bir sohbet tamamlama isteği gönderin. Bu, OpenAI API'siyle aynı mesaj biçimini kullanır — `"user"` ve `"assistant"` gibi rollerle mesajların bir listesi. `stream=True` ayarı, yanıtın hepsinin aynı anda değil, aşamalı olarak geleceği anlamına gelir:

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

Son olarak, akışlı parçalar üzerinde yineleyin ve her metin parçasını geldiğinde yazdırın:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Dahil edilen [chat_with_model.py](assets/chat_with_model.py) betiği tüm örneği içerir ve indirilebilir.


## Sorun Giderme

### Bağlantı reddedildi

Sunucunun çalıştığından emin olun:
```bash
curl http://localhost:8001/health
```

## Özet

Bu playbook'ta şunları öğrendiniz:

- Entegre GPU üzerinde ROCm desteğiyle kapsayıcılı vLLM'yi başlatma
- 8001 numaralı bağlantı noktasında OpenAI uyumlu API uç noktalarıyla bir vLLM sunucusu başlatma
- `vllm-prompt` ile istem gönderme
- Hem akışlı hem de akışsız istekler kullanarak vLLM sunucusuna API çağrıları yapma
- Sunucu başlatma, bellek ve istemci bağlantılarıyla ilgili yaygın sorunları giderme

Artık entegre GPU üzerinde optimize edilmiş performansla büyük dil modellerini sunmak için kapsayıcılı bir vLLM dağıtımına sahipsiniz.

## Sonraki Adımlar

- **Farklı modeller deneyin** — Farklı LLM'lerle denemeler yapmak ve performansı karşılaştırmak için `vllm-launch` yapılandırmasındaki modeli değiştirin.
- **Bir uygulama oluşturun** — vLLM'yi bir Python uygulamasına, sohbet botuna veya otomasyon iş akışına entegre etmek için OpenAI uyumlu API'yi kullanın.
- **İnce ayar yapın ve sunun** — LoRA veya QLoRA kullanarak bir modeli ince ayarlayın, ardından optimize edilmiş çıkarım için vLLM ile dağıtın.

## Ek Kaynaklar

- **[vLLM Resmi Belgeleri](https://docs.vllm.ai/)** — Kapsamlı kılavuzlar ve API referansları
- **[vLLM GitHub Deposu](https://github.com/vllm-project/vllm)** — Kaynak kodu, sorunlar ve topluluk tartışmaları