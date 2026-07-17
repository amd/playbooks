<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış


Güçlü yapay zeka dil modellerini kendi donanımınızda çalıştırmak ister misiniz? Bu kılavuz size nasıl yapacağınızı gösteriyor.
Bu eğitim, belgeleri özetleyebilen, soruları yanıtlayabilen, metin üretebilen ve daha fazlasını yapabilen modelleri yerel olarak çalıştırmak için AMD ROCm™ yazılımıyla desteklenen PyTorch kullanır.

## Ne Öğreneceksiniz

- PyTorch ve ROCm kullanarak gpt-oss-20b ve qwen3.5-4B gibi LLM'leri yerel olarak çalıştırma
- LLM'leri kullanarak bir belge özetleme aracı oluşturma

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code yüklü değilse, Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux'ta, seçtiğiniz dizinde bir terminal açın ve ROCm+Pytorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=120 -->
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
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun geçerli olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=120 -->
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
Windows'ta, seçtiğiniz dizinde bir terminal açın ve ROCm+Pytorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **İpucu**: Windows kullanıcılarının bazı PowerShell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmeleri gerekebilir (örneğin
> RemoteSigned veya Unrestricted olarak ayarlama).

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
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Örnek Betiklerle Hızlı Başlangıç

Bu playbook kullanıma hazır betikler içermektedir. Önizlemek ve oluşturduğunuz ortamla aynı dizine indirmek için üzerlerine tıklayın.

| Betik | Açıklama | Kullanım |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Temel LLM metin üretimi | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Harmony desteğiyle belge özetleyici | `python summarizer.py --file document.txt` |

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
- Özellikle belge özetleme için kullanışlı olan, doğru model yönlendirmesi amacıyla sohbet şablonu biçimlendirmesi

## İlk LLM'inizi Yükleme ve Çalıştırma

Dahil edilen [run_llm.py](assets/run_llm.py) betiği, PyTorch ve AMD ROCm kullanarak LLM'lerle nasıl metin üretileceğini göstermektedir.

> **Not:** Bir model yüklediğinizde, Hugging Face Transformers önce yerel önbelleğini kontrol eder (Linux'ta `~/.cache/huggingface/hub`, Windows'ta `C:\Users\<user>\.cache\huggingface\hub`). Model önbellekte yoksa huggingface.co'dan otomatik olarak indirilir. Model boyutuna ve ağ hızına bağlı olarak ilk çalıştırma birkaç dakika sürebilir.

Aşağıdaki kod parçacığı, modelin nasıl kullanılacağını ve soruların nasıl özelleştirileceğini göstermektedir.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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


## Belge Özetleyici Oluşturma

Yerel LLM çıktısı ürettikten sonra, pratik bir belge özetleyici yaparak bunu daha da ileri götürebilirsiniz. Bu bölümde, bir .txt dosyası beslemek ve GPU'nuzda tamamen yerel olarak çalışan kısa bir özet otomatik olarak oluşturmak için [summarizer.py](assets/summarizer.py) betiğini kullanacaksınız.

Betik, kutudan çıktığı gibi çalışacak şekilde tasarlanmıştır. Kodu incelemek, yönlendirmeleri özelleştirmek ve uzunluk ile sıcaklık gibi parametreleri ayarlamak için betiği bir düzenleyicide açın.

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
| `max_new_tokens` | LLM çıktısının maksimum uzunluğu | Özetler için 50–500 token kullanın. (1 token yaklaşık 0,75 İngilizce kelimedir) |
| `temperature` | Yaratıcılık. Düşük değerler odaklanmayı sağlarken, yüksek değerler daha fazla öngörülemezlik getirir | - **0.1–0.3**: Odaklı, deterministik (özetler için iyi) <br> **0.5–0.7**: Dengeli (genel kullanım) <br> **0.8–1.0**: Yaratıcı, çeşitli (beyin fırtınası) |
| `top_p` | Çekirdek Örnekleme - Düşük değerler modeli daha dar çıktılarla sınırlar | **0.1-0.5**: Katı, öngörülebilir <br> **0.9-0.95**: (standart, doğal, konuşma dili) |


## Gerçek Dünya Uygulamaları

- **Araştırma Makalesi Analizi**: Hızlı inceleme için karmaşık yayınlardan temel bulguları çıkarma
- **Haber Toplama**: Haber makalelerini kısa günlük özetlere veya öne çıkanlara dönüştürme
- **Toplantı Notları**: Transkriptleri eyleme geçirilebilir maddelere ve kısa özetlere dönüştürme
- **Hukuki Belge İncelemesi**: Uzun hukuki metinlerden ilgili maddeleri veya yükümlülükleri hızla çıkarma
- **Kod Belgelendirmesi**: Kısa depo genel bakışları ve işlev açıklamaları oluşturma

## Sonraki Adımlar

- **İnce Ayar**: Daha iyi doğruluk için modelleri belirli alanınıza veya jargonunuza uyarlama (İnce Ayar Playbook'larına bakın)
- **RAG Sistemleri**: Bağlama duyarlı yanıtlar ve arama için LLM'leri belge alımıyla birleştirme
- **Model Keşfi**: Daha iyi sonuçlar için Llama 3, Phi-3 veya Qwen gibi yeni modellerle denemeler yapma
- **Üretim Dağıtımı**: Kuruluşlarda ölçeklenebilir LLM sunumu için vLLM gibi araçları kullanma

Sisteminiz, gelişmiş dil modellerini yerel olarak çalıştırma gücü sağlar. Uygulamalarınız için en iyi neyin işe yaradığını keşfetmek amacıyla farklı modeller, yönlendirmeler ve parametrelerle denemeler yapın.