<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın render edemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

## Genel Bakış

Bu playbook, AMD donanımında Unsloth kullanarak bir dil modelinin yerel olarak nasıl ince ayar yapılacağını göstermektedir.

`mlabonne/FineTome-100k` veri setinin bir alt kümesini kullanarak `unsloth/gemma-4-E4B-it` üzerinde LoRA adaptörleriyle kısa bir Denetimli İnce Ayar (SFT) örneği kullanır. Amaç, kurulum, eğitim, çıkarım ve ince ayarlı sonucun kaydedilmesini kapsayan basit bir uçtan uca iş akışı sunmaktır.

Örnek, pratik ve kolayca değiştirilebilir olacak şekilde tasarlanmıştır; böylece kendi veri setleriniz ve modelleriniz için bir başlangıç noktası olarak kullanabilirsiniz.

## Neler Öğreneceksiniz

- Unsloth ortamı nasıl kurulur
- Unsloth ile SFT kullanarak bir LLM nasıl ince ayar yapılır
- İnce ayarlı sonuç yerel depolamaya nasıl kaydedilir

<!-- @device:halo,stx,krk -->
> **Not:** Bu playbook'taki ince ayar teknikleri en az 24 GB GPU belleği ve 32 GB sistem RAM'i gerektirir.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Not:** Bu playbook'taki ince ayar teknikleri en az 24 GB GPU belleği ve 32 GB sistem RAM'i gerektirir.
<!-- @os:end -->

<!-- @os:linux -->
> **Not:** Bu playbook'taki ince ayar teknikleri en az 24 GB **ayrılmış** GPU belleği ve 32 GB sistem RAM'i gerektirir.
<!-- @os:end -->
<!-- @device:end -->

## Neden Unsloth?

Unsloth, bellek kullanımını azaltarak ve standart bir kuruluma kıyasla eğitimi hızlandırarak LLM ince ayarını yerel donanımda çalıştırmayı kolaylaştırır.

Bu playbook'ta Unsloth'u **LoRA tabanlı SFT** ile birlikte kullanıyoruz. Bu, temel modelin büyük ölçüde dondurulmuş kalırken çok daha küçük bir adaptör ağırlıkları kümesinin eğitildiği anlamına gelir. Bu, tam ince ayardan daha hafif ve üzerinde yineleme yapmak daha hızlı olduğundan yerel geliştirme için iyi bir seçimdir.

Unsloth ayrıca QLoRA ve pekiştirmeli öğrenme iş akışları dahil diğer eğitim yaklaşımlarını da destekler. Bu playbook önce en basit yola odaklanır: kullanıcıların çalıştırabileceği, anlayabileceği ve genişletebileceği küçük bir LoRA ince ayar örneği.

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
Bir terminal açın ve AMD ROCm™ yazılımı ile PyTorch önceden yüklenmiş bir venv oluşturun:
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
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun geçerli olması için oturumu kapatıp tekrar açın):

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
Bir PowerShell terminali açın ve sanal ortam oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Bir PowerShell terminali açın ve sanal ortam oluşturun:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Temel Bağımlılıkları Yükleme
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
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Not:** İçe aktarma sırasında Unsloth, isteğe bağlı `bitsandbytes` hızlandırma yollarını araştırabilir. Bazı ROCm sürümlerinde `bitsandbytes library load error: Configured ROCm binary not found` gibi bir mesaj görebilirsiniz. Bu playbook, `optim="adamw_torch"` ile standart LoRA ince ayarı kullanır; dolayısıyla `bitsandbytes` optimize edici veya 4-bit QLoRA'ya bağımlı değiliz. Bu mesaj güvenle yoksayılabilir.

<!-- @os:windows -->
> **Not:** Windows ROCm'da Unsloth, başlangıçta birkaç uyarı yazdıracaktır — aşağıdaki [Bilinen Uyarılar](#known-warnings) bölümüne bakın. Bunların tümü güvenle yoksayılabilir; eğitim doğru şekilde çalışır.
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

Her adımı manuel olarak yürütmek yerine, bu playbook burada temiz, uçtan uca bir betik sunmaktadır: [test_unsloth.py](assets/test_unsloth.py).

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

Playbook'un geri kalanı, betiğin her önemli adımını kavramsal olarak ele alacaktır.

## Nasıl Çalışır

test_unsloth.py betiği aşağıdaki adımları gerçekleştirir:
* **Model Yükleme**: FastModel kullanarak unsloth/gemma-4-E4B-it'i yükler.
* **Veri Hazırlama**: Veri setini (örn. FineTome-100k) standartlaştırır ve Gemma-4 sohbet şablonunu uygular.
* **LoRA Uygulama**: Verimli eğitim için dil, dikkat ve MLP modüllerine adaptörler ekler.
* **Eğitim**: Yalnızca yanıt kaybı maskeleme ile SFTTrainer kullanır.
* **Çıkarım**: Performansı doğrulamak için hızlı bir üretim testi çalıştırır.
* **Kaydetme**: LoRA adaptörlerini yerel olarak dışa aktarır.

## Temel Yapılandırma

Çalıştırmanızı özelleştirmek için aşağıdaki sabitleri değiştirebilirsiniz:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Model ağırlıkları yüklenirken Unsloth karşılama mesajı ve çıktı örneği:

![alt text](assets/welcome.png)

## Veri Setini Hazırlama

Şunun bir alt kümesini kullanıyoruz:
```text
mlabonne/FineTome-100k
```
Veri seti:
* Sohbet formatına dönüştürülür
* Gemma-4 sohbet şablonu kullanılarak işlenir
* Yinelenen BOS belirteçlerini kaldırmak için temizlenir

## Modeli Eğitme

Betik, aşağıdaki parametrelerle kısa bir eğitim demosu çalıştırır:
- ~50 adım
- Küçük toplu iş boyutu
- Gradyan birikimi

Eğitim sırasında şunun gibi günlükler göreceksiniz:

![alt text](assets/training.png)


## Kaydetme ve Dağıtım

### Yerel Kaydetme (LoRA)

Betik, LoRA adaptörlerini otomatik olarak OUTPUT_DIR'e kaydeder.
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
> **Not:** vLLM, Windows'u desteklememektedir. İnce ayarlı modelinizi Windows'ta dağıtmak için llama.cpp kullanın (aşağıdaki [GGUF Dışa Aktarma](#export-gguf-for-llamacpp) bölümüne bakın) veya birleştirilmiş modeli vLLM çalıştıran bir Linux makinesine aktarın.
<!-- @os:end -->

<!-- @os:linux -->
vLLM ile dağıtım için adaptörleri tam bir modelde birleştirin:
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

Yerel çıkarım için doğrudan GGUF'a dönüştürün:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Bilinen Uyarılar

Bu uyarılar, Windows ROCm'da Unsloth tarafından başlangıçta yazdırılır ve tümü güvenle yoksayılabilir:

| Uyarı | Neden | Güvenle yoksayılabilir mi? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes'ın Windows ROCm derlemesi yoktur | Evet — bu playbook `adamw_torch` kullanır, bnb değil |
| `No ROCm platform found for torch.distributed` | Windows üzerinde ROCm, dağıtık eğitimden yoksundur | Evet — tek GPU eğitimi etkilenmez |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth, Linux dışı derlemeleri işaretler | Evet — Windows ROCm, tek GPU SFT için çalışır |
| `triton is not available` | Triton'ın Windows derlemesi yoktur | Evet — Unsloth, PyTorch çekirdeklerine geri döner |

Bu uyarılara rağmen eğitim doğru şekilde ilerleyecektir.
<!-- @os:end -->

## Sonraki Adımlar
- Unsloth için sezgisel bir GUI olan [Unsloth Studio](https://unsloth.ai/docs/new/studio)'yu deneyin
- Kendi özel veri setlerinizde eğitin
- Farklı hiperparametrelerle ince ayar yapmayı deneyin
- vLLM veya llama.cpp ile dağıtın
- Daha düşük bellek kullanımı için QLoRA'yı deneyin

## Kaynaklar

Unsloth ve ince ayar hakkında daha fazla bilgi edinmek için bazı ek kaynaklar aşağıda verilmiştir:

* [Unsloth Belgeleri](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth İnce Ayar Kılavuzu](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)