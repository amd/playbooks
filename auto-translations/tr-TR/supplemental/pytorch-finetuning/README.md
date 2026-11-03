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

Bu eğitim, PyTorch ve ROCm ile büyük bir dil modelini (LLM) ince ayar yapmak için adım adım örnekler sunar. Standart ince ayardan bellek verimli Parametre-Etkin İnce Ayar (PEFT) stratejilerine kadar çeşitli teknikleri kapsar, böylece modelleri ihtiyaçlarınıza kolayca uyarlayabilirsiniz.

**Kullanılan Model**: google/gemma-3-4b-it  *(kısıtlıysa [HF kimlik doğrulamasını etkinleştirme](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) bölümüne bakın)*  
**Donanım**: ROCm destekli AMD Radeon™ GPU  
**Çerçeve**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Not:** 
> - Tam ince ayar için en az **64 GB sistem RAM**'i gerekir; bunun en az **32 GB'ı GPU için kullanılabilir olmalıdır** (32 GB, 64 GB'ın bir parçasıdır, ona ek değildir).
> - Sağlanan eğitim betiklerinde modeli değiştirerek **GPT-OSS-20B** dahil diğer model mimarilerini de deneyebilirsiniz.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Not:** LoRA ve QLoRA ince ayarı için en az **32 GB sistem RAM**'i gerekir; bunun en az **16 GB'ı GPU için kullanılabilir olmalıdır** (16 GB, 32 GB'ın bir parçasıdır, ona ek değildir).
<!-- @os:end -->

<!-- @os:windows -->
> **Not:** LoRA ince ayarı için en az **32 GB sistem RAM**'i gerekir; bunun en az **16 GB'ı GPU için kullanılabilir olmalıdır** (16 GB, 32 GB'ın bir parçasıdır, ona ek değildir).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Not:** LoRA ve QLoRA ince ayarı, en az **16 GB özel GPU belleğine** ve **32 GB sistem RAM**'ine sahip bir ekran kartı gerektirir.
> - Linux'ta eğitim tamamen ekran kartının özel VRAM'inde çalışır.
> - VRAM tükendiğinde paylaşımlı GPU belleğine (sistem RAM'i) geri dönmez.
> - 16 GB'dan az özel VRAM'e sahip kartlar, sistemde bol miktarda RAM olsa bile Linux'ta eğitim sırasında bellek yetersizliği yaşar.
<!-- @os:end -->

<!-- @os:windows -->
> **Not:** LoRA ince ayarı, en az **16 GB toplam GPU belleği** ve **32 GB sistem RAM**'i gerektirir.
> - Windows'ta toplam GPU belleği, ekran kartının özel VRAM'ini paylaşımlı GPU belleğiyle (sistem RAM'inden ödünç alınan) birleştirir.
> - Bu nedenle, 16 GB'dan az özel VRAM'e sahip kartlar, farkı kapatmak için paylaşımlı GPU belleğini kullanarak yine de bu kılavuzu çalıştırabilir.
<!-- @os:end -->
<!-- @device:end -->

## Öğrenecekleriniz

- PyTorch ve ROCm ile LoRA, QLoRA ve tam ince ayar kullanarak bir LLM'in nasıl ince ayarlanacağı
- İnce ayarlanmış modelinizin nasıl kaydedileceği ve dağıtılacağı
- Eğitimin nasıl izleneceği ve yaygın sorunların nasıl giderileceği

<!-- @device:halo_box,halo,stx,krk -->
## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code kurulu değilse, Ryzen AI Developer Center ile kurabilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

#### Sanal Bir Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp tekrar açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Temel Bağımlılıkların Kurulumu
<!-- @require:pytorch -->

#### Ek Bağımlılıklar

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Burada yalnızca çekirdek paketler test edilmiş ve desteklenmektedir. **bitsandbytes, Windows'ta iyi desteklenmez**, bu nedenle Windows kurulumu bunu içermez; Windows'ta LoRA veya tam ince ayar kullanın (QLoRA, bitsandbytes gerektirir ve Linux için tasarlanmıştır).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF kimlik doğrulamasını etkinleştirme (kısıtlı veya özel / önceden kurulmamış modeller)

Bu örnekte **kısıtlı** bir model olan **google/gemma-3-4b-it** kullanıyoruz. Eğitim betiklerinin modeli indirebilmesi için Hugging Face üzerinde modelin şartlarını kabul etmeniz ve ardından kimlik doğrulaması yapmanız gerekir.

1. **Lisansı kabul edin:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) adresini açın, oturum açın (veya bir hesap oluşturun) ve model sayfasında lisans/şartları kabul edin (örneğin "Agree and access repository").
2. **Kurun ve oturum açın:** Hugging Face CLI'yi kurun, ardından standart girişi çalıştırın:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Teknikleri Anlama

### LoRA Nedir?

**LoRA (Düşük Sıralı Adaptasyon)**, temel modeli dondurulmuş halde tutar ve yalnızca belirli katmanlara eklenen küçük "adaptör" matrislerini eğitir. 

- **Ana fikir**: milyonlarca parametreye sahip devasa bir ağırlık matrisini güncellemek yerine, düşük sıralı bir güncelleme öğreniriz (çarpımı çok daha az parametreye sahip iki küçük matris). Bu, tam ince ayarın kalitesinin çoğunu korurken eğitilebilir parametre sayısında ve VRAM'de büyük bir azalma sağlar.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### QLoRA Nedir?

**QLoRA**, **4-bit nicemlemeyi** **LoRA** ile birleştirir. Temel model 4-bit olarak yüklenir (büyük bellek tasarrufu) ve yalnızca LoRA adaptörleri daha yüksek hassasiyette eğitilir. Böylece LoRA'nın parametre verimliliğini, çok daha düşük VRAM ile birlikte, tam hassasiyetli LoRA'ya kıyasla küçük bir kalite ödünü karşılığında elde edersiniz. 4-bit nicemlemenin sayısal kararsızlıklara (kayıp sıçramaları veya NaN'lar) neden olabileceğini unutmayın, bu nedenle kullanıcılar yeterli VRAM mevcutsa çoğunlukla **LoRA**'yı tercih edebilir.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Not**: `openai/gpt-oss-20b` gibi MXFP4 temel modelleri için, QLoRA yerine **LoRA** (`train_lora.py`) kullanmanızı öneririz. QLoRA betiğinin `bitsandbytes` 4-bit yolu genellikle MXFP4 ağırlıklarını BF16'ya dequantize eder, bu nedenle çalıştırma standart LoRA gibi davranır. Yerel MXFP4, kaynaktan derlenmiş `bitsandbytes` ile birlikte uyumlu bir Transformers/Triton/kernels yığını gerektirir. [Transformers MXFP4 belgelerine](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) bakın.

---
### 2. Yönteminizi Seçin

| Yöntem | Bellek | Hız | Kalite | En Uygun Kullanım |
|--------|--------|-------|---------|----------|
| **QLoRA** (yalnızca Linux) | 12-16GB | En Hızlı | %90-95 | Düşük Bellek Kullanımı |
| **LoRA** | 24-32GB | Hızlı | %95-98 | Dengeli yaklaşım |
| **Full** | 80GB+ | En Yavaş | %100 | Maksimum kalite |

### 3. Eğitimi Çalıştırın

**Veri kümesi ve modelin öğrendikleri**  
Betikler, veri kümesini sohbet örneklerine dönüştürür. Örneğin QLoRA betiği **Abirate/english_quotes** veri kümesini kullanır: her örnek şu şekilde bir kullanıcı-asistan çifti haline gelir:

- **Kullanıcı:** “Bana şu konuyla ilgili bir alıntı ver: &lt;etiket&gt;”
- **Asistan:** “&lt;alıntı&gt; – &lt;yazar&gt;”

İnce ayar, modele bir konuyla ilgili alıntı isteyen istemlere yanıt vermeyi ve bunları `<alıntı metni> - <yazar>` biçiminde döndürmeyi öğretir. LoRA ve tam ince ayar betikleri **databricks/databricks-dolly-15k** (genel talimat/yanıt çiftleri) veri kümesini kullanır, dolayısıyla kesin görev betiğe göre değişir; fikir aynıdır - modeli seçtiğiniz veri kümesine ve biçime uyarlamak.

Aşağıda mevcut eğitim yöntemlerinin bir özeti bulunmaktadır. Her yöntem, kendi betiğine bağlantı verir ve doğru yaklaşımı seçmeniz için kısa bir açıklama sunar.

| Betik                           | Yöntem            | Açıklama                                                                                                         | Tipik VRAM | Önerilen Kullanım                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Temel modeli dondururken küçük adaptör matrislerini eğitir. 3-5 kat daha hızlı; ~%95-98 tam kalite.                         | 24-32GB      | İleri düzey kullanıcılar; birden fazla adaptör; daha fazla VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(yalnızca Linux)*             | **QLoRA**       | 4-bit nicemleme + LoRA adaptörleri. En düşük bellek kullanımı, en hızlı, küçük bir kalite ödünleşimi. `bitsandbytes` gerektirir (yalnızca Linux).                            | 12-16GB      | Çoğu kullanıcı; hızlı denemeler; sınırlı VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Tam İnce Ayar** | Tüm model parametrelerini günceller. Maksimum kalite; en yüksek bellek ve işlem kullanımı.                                    | 40GB+        | Maksimum kalite; araştırma; büyük VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Not:** Tam ince ayar (`train_full_finetuning.py`) 64GB'den fazla sistem RAM'i gerektirebilir ve bu cihazda uygulanabilir olmayabilir. Bunun yerine LoRA veya QLoRA kullanmayı düşünün.
<!-- @os:end -->

<!-- @os:windows -->
> **Not:** Tam ince ayar (`train_full_finetuning.py`) 64GB'den fazla sistem RAM'i gerektirebilir ve bu cihazda uygulanabilir olmayabilir. Bunun yerine LoRA kullanmayı düşünün.
<!-- @os:end -->
<!-- @device:end -->

Tercih ettiğiniz `Training method`'u seçmeniz, ilgili betiği indirmeniz ve sanal ortamınızı etkin tutarak aşağıdaki komutla çalıştırmanız yeterlidir: 

```python
python3 train_<method_name>.py.
```

## İnce Ayarlanmış Modelinizi Kullanma

### Tam İnce Ayardan Sonra

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA/QLoRA Eğitiminden Sonra

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA Adaptörünü Temel Modele Birleştirme

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Not:**  
- Model dizini adının (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) eğitimden elde ettiğiniz gerçek çıktı klasörüyle eşleştiğinden emin olun.  
- QLoRA yerine LoRA kullandıysanız yolu buna göre değiştirmeniz yeterlidir.  
- Bazı Gemma modelleri, `from_pretrained` içinde `trust_remote_code=True` belirtilmesini gerektirir; ilgili bir uyarı görürseniz bunu ekleyin.

Daha fazla özel ayar için (dolgu belirteçleri, cihaz vb.), eğitim için kullandığınız betiğe başvurun.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Özelleştirme Kılavuzu

### Kendi Veri Kümenizi Kullanın

Tüm betikler aynı veri kümesi biçimini kullanır. Yükleme bölümünü değiştirin:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Yerel JSON/JSONL Dosyası için Veri Kümesi Biçimi:**

Bu yöntemi kullanırken, ayrıştırma hatalarını önlemek için JSON dosyalarınızın doğru şekilde yapılandırıldığından emin olun. 

Aşağıdaki yönergelere uyulmalıdır:
* **Dosya Biçimlendirmesi:** JSON dosyaları, doğru yapı ve söz dizimini sağlamak amacıyla Entegre Geliştirme Ortamı (IDE) içinde biçimlendirilmelidir.
* **Gerekli Anahtarlar:** Özel JSON dosyası, `instruction` ve `response` anahtarlarını içermelidir. Bu anahtarlar, yöntemin doğru şekilde çalışması için gereklidir.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Hugging Face Hub Veri Kümesi için Veri Kümesi Biçimi**

Hugging Face'ten veri kümeleri kullanırken, sorunsuz bir entegrasyon sağlamak için veri kümelerinizin doğru şekilde yapılandırıldığından emin olun. 

Aşağıdaki yönergeler izlenmelidir:
* **Talimat-Yanıt Çifti:** `instruction-response` çifti içeren veri kümelerine odaklanın. Bu yapı, amaçlanan işlevsellik için gereklidir.
* **Özel Anahtar Değişikliği:** Veri kümeniz `instruction-response` yapısına uymuyorsa, `format_instruction()` işlevini değiştirme seçeneğiniz vardır. Bu, gerektiğinde belirli anahtarları uyarlamanıza olanak tanır.

Örnek Ayarlama: Veri kümesinin çıktısının ayarlanması gereken durumlarda, gereksinimlerinize uyması için format_instruction() işlevi içindeki yanıt bölümünü değiştirebilirsiniz.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV Dosyası için Veri Kümesi Biçimi**

Betiği bir CSV dosya biçimi kullanarak çalıştırabilmek için, CSV dosyasının `instruction` ve `response` adlı sütunlar içerdiğinden emin olmanız gerekir. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Eğitim Parametrelerini Ayarlama

Eğitim betiğini düzenleyin ve değişkenleri hedeflerinize uyacak şekilde değiştirin: **öğrenme oranı** (`LR`), **epoklar** (`EPOCHS`), **grup boyutu** (`BATCH_SIZE`), **gradyan birikimi** (`GRAD_ACCUM_STEPS`) ve LoRA/QLoRA için **sıra** (`LORA_R`). Daha hızlı çalıştırmalar için daha az epok ve daha yüksek bir öğrenme oranı (LR) kullanın; daha iyi kalite için daha fazla epok ve daha düşük bir LR kullanın. Bellek yetersizliği hatalarıyla karşılaşırsanız grup boyutunu veya dizi uzunluğunu azaltın.
### Bellek Optimizasyonu İpuçları

Bellek yetersizliği (out-of-memory) hatalarıyla karşılaşırsanız:

**1. Batch Boyutunu Azaltın:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Dizi Uzunluğunu Azaltın:**
```python
max_seq_length=256  # Instead of 512
```

**3. Daha Agresif Nicemleme (Quantization) Kullanın:**
```
Full → LoRA → QLoRA
```

**4. Gradient Checkpointing'i Etkinleştirin (Yalnızca tam ince ayar için):**
```python
model.gradient_checkpointing_enable()
```

---

## İzleme ve Hata Ayıklama

### GPU Belleğini İzleyin

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (İsteğe Bağlı) Deneyleri Weights & Biases ile Takip Edin

Çalıştırmaları ve metrikleri [Weights & Biases](https://wandb.ai) adresine kaydetmek için:

```bash
pip install wandb
wandb login
```

Eğitim betiğinde, trainer yapılandırmasında `report_to="wandb"` ve isteğe bağlı olarak `run_name="your-experiment-name"` ayarını yapın. Wandb kullanmak istemiyorsanız, `report_to` değerini varsayılanında bırakın veya `"none"` olarak ayarlayın.

### Yaygın Sorunlar

#### Bellek Yetersizliği (OOM)

**Çözüm:** Batch boyutunu azaltın ve/veya QLoRA kullanın
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Kayıp (Loss) Azalmıyor

**Çözüm:** Öğrenme oranını ayarlayın
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Yavaş Eğitim

**Çözüm:** Bellek izin veriyorsa batch boyutunu artırın
```python
BATCH_SIZE = 8
```
## Sonraki Adımlar

Başarılı bir ince ayar işlemini tamamladıktan sonra, modelinizden daha fazla yararlanmak için aşağıdaki sonraki adımları değerlendirin:

1. **Değerlendirin:** Genelleme yeteneğini ölçmek ve aşırı uyumdan (overfitting) kaçınmak için ayrılmış test verileri üzerinde kapsamlı bir şekilde değerlendirin.
2. **Deneyin:** Daha iyi doğruluk, hız ve bellek dengeleri için farklı hiperparametre değerlerini deneyerek keşfedin.
3. **Takip Edin:** Tekrarlanabilir araştırmalar için tüm deneylerinizi (ve ilgili metriklerinizi) Weights & Biases ile izleyin.
4. **Deneyin:** Modeli özel kullanım durumunuza uyarlamak için kendi özel veri setlerinizle eğitim yapmayı deneyin.
5. **Dağıtın:** Uyumlu donanımlarda vLLM gibi verimli arka uçları kullanarak ince ayarlı modelinizi hızlı çıkarım (inference) için dağıtın.
6. **Keşfedin:** Prompt mühendisliği, karma hassasiyet (mixed precision) ve daha uzun dizi uzunlukları gibi gelişmiş teknikleri keşfedin.
7. **Eğitin:** Farklı görevler veya alanlar için birden fazla LoRA adaptörü eğitin ve gerektiğinde bunları değiştirin.

---