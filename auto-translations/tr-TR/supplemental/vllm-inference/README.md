<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu kılavuz, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->


## Genel Bakış

vLLM, büyük dil modelleri (LLM'ler) için tasarlanmış yüksek performanslı bir çıkarım motorudur. Yüksek verimlilik için sürekli toplu işleme (continuous batching) özellikli optimize edilmiş sunum ve sorunsuz uygulama entegrasyonu için OpenAI uyumlu bir API sağlar. Bu özellikler, vLLM'yi hız ve kaynak verimliliğinin kritik olduğu üretim dağıtımları için harika bir seçenek haline getirir.

Bu kılavuz, konteynerleştirilmiş vLLM kullanarak entegre GPU üzerinde LLM'lerin nasıl sunulacağını ve modellerle OpenAI Python API üzerinden nasıl etkileşim kurulacağını öğretir.

## Neler Öğreneceksiniz

- AMD ROCm™ desteğiyle bir vLLM sunucusunun nasıl kurulacağı ve başlatılacağı
- OpenAI uyumlu API uç noktaları aracılığıyla modellerle nasıl etkileşim kurulacağı
- `vllm-prompt` ile yerel sunucuya nasıl istem gönderileceği

## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

> **Not**: VS Code yüklü değilse, AMD Ryzen™ AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Yüklenmesi

Bu kılavuz, vLLM, ROCm desteği ve sunucuyu başlatmak için gereken yardımcı betikleri içeren önceden oluşturulmuş bir konteyner görüntüsü kullanır. PyTorch, vLLM veya yerel kılavuz betiklerini manuel olarak yüklemenize gerek yoktur.

Ana makine tarafında bir vLLM kurulum adımı yoktur. vLLM'yi şu şekilde başlatın:

```bash
vllm-launch
```

Başlatıcı konteyneri başlatır, entegre GPU'yu hedefler ve yerel bir OpenAI uyumlu vLLM sunucusu sunar. Alternatif olarak, görev çubuğundaki vLLM simgesine tıklayabilirsiniz.

## Hızlı Başlangıç

### 1. vLLM Sunucusunun Çalıştığını Doğrulayın

`vllm-launch`ın her şeyi başlatması birkaç dakika sürebilir. Başladığında, sunucu `http://localhost:8001` adresinde kullanılabilir olur. Sunucu ön planda çalıştığı için başlatma terminalini açık tutun, ardından kalan adımlar için ayrı bir terminal açın. Aşağıdaki örnekler `Qwen/Qwen3-1.7B` kullanmaktadır; başlatıcınız farklı bir model için yapılandırılmışsa, isteklerde o model kimliğini kullanın.

### 2. Bir İstem Gönderin

Yerel vLLM OpenAI uyumlu sunucusuna bir istek göndermek için sağlanan `vllm-prompt` betiğini kullanın:

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API'sini Kullanarak Modelle Sohbet Edin

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

OpenAI paketini yükleyin
```bash
pip install openai
```

OpenAI'nin sunucuları yerine yerel vLLM sunucusunu hedefleyen bir `OpenAI` istemcisi oluşturun. `api_key` istemci tarafından gerekli olsa da vLLM bunu doğrulamaz, bu nedenle herhangi bir dize işe yarar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ardından, bir sohbet tamamlama isteği gönderin. Bu, OpenAI API'siyle aynı mesaj biçimini kullanır — `"user"` ve `"assistant"` gibi rollere sahip bir mesaj listesi. `stream=True` ayarlanması, yanıtın tek seferde değil, aşamalı olarak geleceği anlamına gelir:

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

Son olarak, akış halindeki parçalar üzerinde döngü kurun ve her metin parçasını geldiği anda yazdırın:

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

Bu kılavuzda şunları öğrendiniz:

- Entegre GPU üzerinde ROCm desteğiyle konteynerleştirilmiş vLLM'yi başlatma
- Port 8001'de OpenAI uyumlu API uç noktalarına sahip bir vLLM sunucusu başlatma
- `vllm-prompt` ile istem gönderme
- Hem akış hem de akış dışı istekler kullanarak vLLM sunucusuna API çağrıları yapma
- Sunucu başlatma, bellek ve istemci bağlantılarıyla ilgili yaygın sorunları giderme

Artık entegre GPU üzerinde optimize edilmiş performansla büyük dil modellerini sunmak için konteynerleştirilmiş bir vLLM dağıtımına sahipsiniz.

## Sonraki Adımlar

- **Farklı modeller deneyin** — Farklı LLM'leri denemek ve performansı karşılaştırmak için `vllm-launch` yapılandırmasındaki modeli değiştirin.
- **Bir uygulama oluşturun** — vLLM'yi bir Python uygulamasına, sohbet botuna veya otomasyon iş akışına entegre etmek için OpenAI uyumlu API'yi kullanın.
- **İnce ayar yapın ve sunun** — LoRA veya QLoRA kullanarak bir modele ince ayar yapın, ardından optimize edilmiş çıkarım için vLLM ile dağıtın.

## Ek Kaynaklar

- **[vLLM Resmi Belgeleri](https://docs.vllm.ai/)** — Kapsamlı kılavuzlar ve API referansları
- **[vLLM GitHub Deposu](https://github.com/vllm-project/vllm)** — Kaynak kod, sorunlar ve topluluk tartışmaları