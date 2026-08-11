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

Bu kılavuz, AMD donanımında Unsloth kullanarak bir dil modelini yerel olarak nasıl ince ayar (fine-tune) yapacağınızı gösterir.

`mlabonne/FineTome-100k` veri kümesinin bir alt kümesi kullanılarak `unsloth/gemma-4-E4B-it` üzerinde LoRA bağdaştırıcılarıyla kısa bir Denetimli İnce Ayar (SFT) örneği kullanır. Amaç, kurulum, eğitim, çıkarım ve ince ayarlanmış sonucun kaydedilmesini kapsayan uçtan uca basit bir iş akışı sunmaktır.

Örnek, pratik ve kolayca değiştirilebilir olacak şekilde tasarlanmıştır; böylece kendi veri kümeleriniz ve modelleriniz için bir başlangıç noktası olarak kullanabilirsiniz.

## Neler Öğreneceksiniz

- Unsloth ortamının nasıl kurulacağı
- Unsloth ile SFT kullanarak bir LLM'nin nasıl ince ayar yapılacağı
- İnce ayarlanmış sonucun yerel depolamaya nasıl kaydedileceği

<!-- @device:halo,stx,krk -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **64 GB sistem RAM'i** gerektirir ve bunun en az **24 GB'ının GPU için kullanılabilir olması** gerekir (bu 24 GB, 64 GB'a ek değil, onun bir parçasıdır).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **24 GB toplam GPU belleği** ve **32 GB sistem RAM'i** gerektirir.
> - Windows'ta toplam GPU belleği, ekran kartının ayrılmış VRAM'i ile paylaşımlı GPU belleğini (sistem RAM'inden ödünç alınan) birleştirir.
> - Bu nedenle, ayrılmış VRAM'i 24 GB'ın altında olan kartlar, aradaki farkı kapatmak için paylaşımlı GPU belleğini kullanarak bu kılavuzu yine de çalıştırabilir.
<!-- @os:end -->

<!-- @os:linux -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **24 GB ayrılmış GPU belleğine** ve **32 GB sistem RAM'ine** sahip bir ekran kartı gerektirir.
> - Linux'ta eğitim tamamen ekran kartının ayrılmış VRAM'i içinde çalışır.
> - VRAM tükendiğinde paylaşımlı GPU belleğine (sistem RAM'i) geri düşmez.
> - Ayrılmış VRAM'i 24 GB'ın altında olan kartlar, sistemde bol miktarda RAM olsa bile Linux'ta eğitim sırasında bellek yetersizliği yaşayacaktır.
<!-- @os:end -->
<!-- @device:end -->

## Neden Unsloth?

Unsloth, standart bir kuruluma kıyasla bellek kullanımını azaltıp eğitimi hızlandırarak LLM ince ayarının yerel donanımda çalıştırılmasını kolaylaştırır.

Bu kılavuzda Unsloth'u **LoRA tabanlı SFT** ile birlikte kullanıyoruz. Bu, temel modelin büyük ölçüde dondurulmuş kalması, bunun yerine çok daha küçük bir bağdaştırıcı ağırlıkları kümesinin eğitilmesi anlamına gelir. Bu yaklaşım, tam ince ayara göre daha hafif ve üzerinde yineleme yapmak için daha hızlı olduğundan yerel geliştirme için iyi bir uyuma sahiptir.

Unsloth ayrıca QLoRA ve pekiştirmeli öğrenme iş akışları dahil olmak üzere başka eğitim yaklaşımlarını da destekler. Bu kılavuz, önce en basit yolu ele alır: kullanıcıların çalıştırabileceği, anlayabileceği ve genişletebileceği küçük bir LoRA ince ayar örneği.

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code kurulu değilse, Ryzen AI Developer Center ile kurabilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Önkoşullarını Kurma

### Sanal Bir Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
Bir terminal açın ve AMD ROCm™ yazılımı ile PyTorch'un önceden kurulu olduğu bir venv oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Bir terminal açın ve bir venv oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Not:** Windows için Python 3.13 gereklidir.

<!-- @device:halo_box -->
Bir PowerShell terminali açın ve bir sanal ortam oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Bir PowerShell terminali açın ve bir sanal ortam oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Temel Bağımlılıkları Kurma
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Ek Bağımlılıklar

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Not:** İçe aktarma sırasında Unsloth, isteğe bağlı `bitsandbytes` hızlandırma yollarını araştırabilir. Bazı ROCm sürümlerinde `bitsandbytes library load error: Configured ROCm binary not found` gibi bir mesaj görebilirsiniz. Bu kılavuz `optim="adamw_torch"` ile standart LoRA ince ayarını kullandığından `bitsandbytes` optimize edicisine veya 4-bit QLoRA'ya güvenmiyoruz. Bu mesaj güvenle göz ardı edilebilir.

<!-- @os:windows -->
> **Not:** Windows ROCm üzerinde Unsloth, başlangıçta çeşitli uyarılar yazdıracaktır — aşağıdaki [Bilinen Uyarılar](#known-warnings) bölümüne bakın. Bunların tümü güvenle göz ardı edilebilir; eğitim düzgün şekilde çalışır.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Unsloth İnce Ayar Betiğini İndirme

Her adımı manuel olarak çalıştırmak yerine, bu kılavuz burada eksiksiz, uçtan uca bir betik sağlar: [test_unsloth.py](assets/test_unsloth.py).

Betiği çalıştırmak için aşağıdaki kodu çalıştırın:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Kılavuzun geri kalanı, betiğin her bir ana adımını kavramsal olarak ele alacaktır. 

## Nasıl Çalışır

test_unsloth.py betiği aşağıdaki adımları gerçekleştirir:
* **Modeli Yükle**: FastModel kullanarak unsloth/gemma-4-E4B-it'i yükler.
* **Veriyi Hazırla**: Veri kümesini (ör. FineTome-100k) standartlaştırır ve Gemma-4 sohbet şablonunu uygular.
* **LoRA Uygula**: Verimli eğitim için dil, dikkat (attention) ve MLP modüllerine bağdaştırıcılar ekler.
* **Eğit**: Yalnızca yanıta özgü kayıp maskeleme ile SFTTrainer kullanır.
* **Çıkarım**: Performansı doğrulamak için hızlı bir üretim testi çalıştırır.
* **Kaydet**: LoRA bağdaştırıcılarını yerel olarak dışa aktarır.

## Anahtar Yapılandırma

Çalıştırmanızı özelleştirmek için aşağıdaki sabitleri değiştirebilirsiniz:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Model ağırlıkları yüklenirken Unsloth karşılama mesajı ve çıktısına örnek:

![alt text](assets/welcome.png)

## Veri Kümesini Hazırlama

Şunun bir alt kümesini kullanıyoruz:
```text
mlabonne/FineTome-100k
```
Veri kümesi:
* Sohbet formatına dönüştürülür
* Gemma-4 sohbet şablonu kullanılarak işlenir
* Yinelenen BOS belirteçlerini kaldırmak için temizlenir

## Modeli Eğitme

Betik, aşağıdaki parametrelerle kısa bir eğitim gösterimi çalıştırır:
- ~50 adım
- Küçük yığın (batch) boyutu
- Gradyan biriktirme

Eğitim sırasında şu şekilde günlükler göreceksiniz:

![alt text](assets/training.png)


## Kaydetme ve Dağıtım
### Yerel Kaydetme (LoRA)

Betik, LoRA bağdaştırıcılarını otomatik olarak OUTPUT_DIR içine kaydeder.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Birleştirilmiş modeli kaydetme (vLLM için) 

<!-- @os:windows -->
> **Not:** vLLM, Windows'u desteklemez. İnce ayarlanmış modelinizi Windows üzerinde dağıtmak için llama.cpp kullanın (aşağıdaki [GGUF Dışa Aktarma](#export-gguf-for-llamacpp) bölümüne bakın) veya birleştirilmiş modeli vLLM çalıştıran bir Linux makinesine aktarın.
<!-- @os:end -->

<!-- @os:linux -->
vLLM ile dağıtım için, bağdaştırıcıları tam bir modelde birleştirin:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### GGUF Dışa Aktarma (llama.cpp için)

Yerel çıkarım için doğrudan GGUF formatına dönüştürün:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Bilinen Uyarılar

Bu uyarılar, Windows ROCm üzerinde başlangıçta Unsloth tarafından yazdırılır ve tamamı göz ardı edilmesi güvenlidir:

| Uyarı | Neden | Göz ardı edilmesi güvenli mi? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes'ın Windows ROCm derlemesi yoktur | Evet — bu oyun kitabı bnb yerine `adamw_torch` kullanır |
| `No ROCm platform found for torch.distributed` | Windows üzerindeki ROCm, dağıtık eğitimden yoksundur | Evet — tek GPU eğitimi bundan etkilenmez |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth, Linux olmayan derlemeleri işaretler | Evet — Windows ROCm, tek GPU SFT için çalışır |
| `triton is not available` | Triton'un Windows derlemesi yoktur | Evet — Unsloth, PyTorch çekirdeklerine geri döner |

Bu uyarılara rağmen eğitim doğru şekilde devam edecektir.
<!-- @os:end -->

## Sonraki Adımlar
- Unsloth için sezgisel bir GUI olan [Unsloth Studio](https://unsloth.ai/docs/new/studio)'yu deneyin
- Kendi özel veri kümelerinizle eğitin
- Farklı hiper parametrelerle ince ayar yapmayı deneyin
- vLLM veya llama.cpp ile dağıtın
- Daha düşük bellek kullanımına sahip bir kurulum için QLoRA'yı deneyin

## Kaynaklar

Unsloth ve ince ayar hakkında daha fazla bilgi edinmek için aşağıda bazı ek kaynaklar bulunmaktadır:

* [Unsloth Dokümanları](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth İnce Ayar Kılavuzu](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)