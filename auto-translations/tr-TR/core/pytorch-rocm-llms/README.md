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


Güçlü yapay zeka dil modellerini kendi donanımınızda çalıştırmak mı istiyorsunuz? Bu kılavuz bunu nasıl yapacağınızı gösterir.
Bu eğitim, belgeleri özetleyebilen, soruları yanıtlayabilen, metin üretebilen ve daha fazlasını yapabilen modelleri tamamen yerel olarak çalıştırmak için AMD ROCm™ yazılımı tarafından desteklenen PyTorch'u kullanır.

## Neler Öğreneceksiniz

- PyTorch ve ROCm kullanarak gpt-oss-20b ve qwen3.5-4B gibi LLM'leri yerel olarak çalıştırın
- LLM'leri kullanarak bir belge özetleme aracı oluşturun

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Edin
> **Not**: VS Code yüklü değilse, Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux üzerinde, tercih ettiğiniz dizinde bir terminal açın ve ROCm+Pytorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU cihazlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp tekrar açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux üzerinde, tercih ettiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
Windows üzerinde, tercih ettiğiniz dizinde bir terminal açın ve ROCm+Pytorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows üzerinde, tercih ettiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **İpucu**: Windows kullanıcılarının bazı Powershell komutlarını çalıştırmadan önce PowerShell Execution Policy ayarlarını değiştirmeleri gerekebilir (örneğin,
> RemoteSigned veya Unrestricted olarak ayarlamak).

<!-- @os:end -->

### Temel Bağımlılıkları Yükleme
<!-- @require:driver,pytorch -->

### Ek Bağımlılıkları Yükleme

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Not:** Model yüklenemezse veya bellek yetersizliği oluşursa, modeli optimize edilmiş nicemleme ile yüklemek için `kernels` paketini yüklemeyi deneyin.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Örnek Betiklerle Hızlı Başlangıç

Bu kılavuz, kullanıma hazır betikler içerir. Bunları önizlemek ve oluşturduğunuz ortamla aynı dizine indirmek için üzerlerine tıklayın.

| Betik | Açıklama | Kullanım |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Temel LLM metin üretimi | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Harmony destekli belge özetleyici | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Her iki betik de şunları destekler:
- `--model` bayrağı aracılığıyla model seçimi
- Uygun model istemi için sohbet şablonu biçimlendirmesi, özellikle belge özetleme için faydalıdır

## İlk LLM'inizi Yükleme ve Çalıştırma

Dahil edilen [run_llm.py](assets/run_llm.py) betiği, PyTorch ve AMD ROCm kullanarak LLM'lerle metin üretmenin nasıl yapılacağını gösterir.

> **Not:** Bir model yüklediğinizde, Hugging Face Transformers önce yerel önbelleğini kontrol eder (Linux'ta `~/.cache/huggingface/hub`, Windows'ta `C:\Users\<user>\.cache\huggingface\hub`). Model önbellekte yoksa, huggingface.co'dan otomatik olarak indirilir. İlk çalıştırma, model boyutuna ve ağ hızına bağlı olarak birkaç dakika sürebilir.

Aşağıdaki kod parçacığı, modelin nasıl kullanılacağını ve sorulan soruların nasıl özelleştirileceğini göstermektedir.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

İndirilen betiği deneyin:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Bir Belge Özetleyici Oluşturma

Yerel LLM çıktısı ürettiğinize göre, pratik bir belge özetleyicisi oluşturarak bunun üzerine inşa edebilirsiniz. Bu bölümde, bir .txt dosyası besleyip GPU'nuzda tamamen yerel olarak çalışarak otomatik olarak özlü bir özet üretmek için [summarizer.py](assets/summarizer.py) betiğini kullanacaksınız.

Betik, kutudan çıktığı gibi çalışacak şekilde tasarlanmıştır. Kodu keşfetmek, istemleri özelleştirmek ve uzunluk ile sıcaklık gibi parametreleri ayarlamak için betiği bir düzenleyicide açın.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Kullanım Örnekleri

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Üretim Parametreleri Hakkında Bilgi Edinin

| Parametre | Neyi Kontrol Eder | Tipik Değerler |
|-----------|------------------|----------------|
| `max_new_tokens` | LLM'in çıktısının maksimum uzunluğu | Özetler için 50–500 token kullanın. (1 token yaklaşık 0,75 İngilizce kelimeye denk gelir) |
| `temperature` | Yaratıcılık. Düşük değerler odaklı yapar, yüksek değerler ise daha fazla öngörülemezlik getirir | - **0.1–0.3**: Odaklı, deterministik (özetler için iyi) <br> **0.5–0.7**: Dengeli (genel kullanım) <br> **0.8–1.0**: Yaratıcı, çeşitli (beyin fırtınası) |
| `top_p` | Nucleus Sampling - Düşük değerler modeli daha dar çıktılarla sınırlar | **0.1-0.5**: Katı, öngörülebilir <br> **0.9-0.95**: (standart, doğal, sohbet tarzı) |


## Gerçek Dünya Uygulamaları

- **Araştırma Makalesi Analizi**: Hızlı inceleme için karmaşık yayınlardan önemli bulguları çıkarın
- **Haber Toplama**: Haber makalelerini kısa günlük özetlere veya öne çıkanlara dönüştürün
- **Toplantı Notları**: Transkriptleri eyleme geçirilebilir maddelere ve özlü özetlere dönüştürün
- **Hukuki Belge İncelemesi**: Uzun hukuki metinlerden ilgili maddeleri veya yükümlülükleri hızlıca çıkarın
- **Kod Dokümantasyonu**: Özlü depo genel bakışları ve fonksiyon açıklamaları oluşturun
## Sonraki Adımlar

- **İnce Ayar (Fine-tuning)**: Modelleri kendi alanınıza veya jargonunuza uyarlayarak daha iyi doğruluk elde edin (bkz. Fine-tuning Playbooks)
- **RAG Sistemleri**: Bağlama duyarlı yanıtlar ve arama için LLM'leri belge alma (retrieval) ile birleştirin
- **Model Keşfi**: Daha iyi sonuçlar için Llama 3, Phi-3 veya Qwen gibi yeni modelleri deneyin
- **Üretim Ortamına Dağıtım**: Kuruluşlarda ölçeklenebilir LLM sunumu için vLLM gibi araçları kullanın

Sisteminiz, gelişmiş dil modellerini yerel olarak çalıştırma gücünü size sunar. Uygulamalarınız için en iyi sonucu verecek yöntemi keşfetmek üzere farklı modelleri, komut istemlerini ve parametreleri deneyin.