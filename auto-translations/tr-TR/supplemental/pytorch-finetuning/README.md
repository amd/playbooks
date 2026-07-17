<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış

Bu eğitim, PyTorch ve ROCm kullanarak büyük bir dil modelini (LLM) ince ayar yapmak için adım adım örnekler sunmaktadır. Standart ince ayardan bellek açısından verimli Parametre Verimli İnce Ayar (PEFT) stratejilerine kadar çeşitli teknikleri kapsamakta olup modelleri ihtiyaçlarınıza göre kolayca uyarlamanızı sağlar.

**Kullanılan Model**: google/gemma-3-4b-it  *(kısıtlıysa [HF kimlik doğrulamasını etkinleştir](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) bölümüne bakın)*  
**Donanım**: ROCm destekli AMD Radeon™ GPU  
**Çerçeve**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Pekiştirmeli Öğrenme (TRL))

<!-- @device:halo,halo_box -->
> **Not:** **GPT-OSS-20B** dahil diğer model mimarilerini de deneyebilirsiniz; bunun için sağlanan eğitim betiklerindeki modeli değiştirmeniz yeterlidir.
> Tam ince ayar için en az 32 GB GPU belleği ve 64 GB sistem RAM'i gerekmektedir.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Not:** LoRA ve QLoRA ince ayarı için en az 16 GB GPU belleği ve 32 GB sistem RAM'i gerekmektedir.
<!-- @device:end -->

## Neler Öğreneceksiniz

- PyTorch ve ROCm ile LoRA, QLoRA ve tam ince ayar kullanarak bir LLM'nin nasıl ince ayar yapılacağı
- İnce ayarlı modelinizin nasıl kaydedileceği ve dağıtılacağı
- Eğitimin nasıl izleneceği ve yaygın sorunların nasıl giderileceği

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code yüklü değilse Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

#### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun geçerli olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Temel Bağımlılıkları Yükleme
<!-- @require:pytorch -->

#### Ek Bağımlılıklar

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Burada yalnızca temel paketler test edilmekte ve desteklenmektedir. **bitsandbytes, Windows'ta iyi desteklenmemektedir**; bu nedenle Windows kurulumu bunu atlar. Windows'ta LoRA veya tam ince ayar kullanın (QLoRA, bitsandbytes gerektirir ve Linux için tasarlanmıştır).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF kimlik doğrulamasını etkinleştirme (kısıtlı veya özel / önceden yüklenmemiş modeller)

Bu örnekte **kısıtlı** bir model olan **google/gemma-3-4b-it** kullanıyoruz. Modelin koşullarını Hugging Face üzerinde kabul etmeniz ve ardından eğitim betiklerinin modeli indirebilmesi için kimlik doğrulaması yapmanız gerekmektedir.

1. **Lisansı kabul edin:** [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) adresini açın, oturum açın (veya bir hesap oluşturun) ve model sayfasındaki lisans/koşulları kabul edin (örn. "Kabul et ve depoya eriş").
2. **Yükleyin ve oturum açın:** Hugging Face CLI'yi yükleyin, ardından standart oturum açma işlemini çalıştırın:

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

**LoRA (Düşük Sıralı Uyarlama)**, temel modeli dondurarak yalnızca belirli katmanlara eklenen küçük "adaptör" matrislerini eğitir.

- **Temel fikir**: Milyonlarca parametreye sahip büyük bir ağırlık matrisini güncellemek yerine, düşük sıralı bir güncelleme öğrenilir (çarpımı çok daha az parametreye sahip iki küçük matris). Bu, eğitilebilir parametre sayısını ve VRAM kullanımını büyük ölçüde azaltırken tam ince ayar kalitesinin büyük bölümünü korur.

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

**QLoRA**, **4-bit niceleme** ile **LoRA**'yı birleştirir. Temel model 4-bit olarak yüklenir (büyük bellek tasarrufu sağlar) ve yalnızca LoRA adaptörleri daha yüksek hassasiyetle eğitilir. Böylece LoRA'nın parametre verimliliğini ve çok daha düşük VRAM kullanımını elde edersiniz; tam hassasiyetli LoRA ile karşılaştırıldığında küçük bir kalite ödünü söz konusudur. 4-bit nicelemenin sayısal kararsızlıklara (kayıp artışları veya NaN'lar) yol açabileceğini unutmayın; bu nedenle yeterli VRAM mevcutsa kullanıcılar genellikle **LoRA**'yı tercih edebilir.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Not**: `openai/gpt-oss-20b` gibi MXFP4 temel modeller için QLoRA yerine **LoRA** (`train_lora.py`) kullanmanızı öneririz. QLoRA betiğinin `bitsandbytes` 4-bit yolu genellikle MXFP4 ağırlıklarını BF16'ya dönüştürür; bu nedenle çalışma standart LoRA gibi davranır. Yerel MXFP4, kaynaktan derlenen `bitsandbytes` ve eşleşen bir Transformers/Triton/çekirdek yığını gerektirir. [Transformers MXFP4 belgelerine](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4) bakın.

---

### 2. Yönteminizi Seçin

| Yöntem | Bellek | Hız | Kalite | En İyi Kullanım |
|--------|--------|-----|--------|-----------------|
| **QLoRA** (yalnızca Linux) | 12-16GB | En Hızlı | %90-95 | Düşük Bellek Kullanımı |
| **LoRA** | 24-32GB | Hızlı | %95-98 | Dengeli yaklaşım |
| **Tam** | 80GB+ | En Yavaş | %100 | Maksimum kalite |

### 3. Eğitimi Çalıştırın

**Veri kümesi ve modelin öğrendikleri**  
Betikler, veri kümesini sohbet örneklerine dönüştürür. Örneğin, QLoRA betiği **Abirate/english_quotes** kullanır: her örnek şu şekilde bir kullanıcı–asistan çiftine dönüşür:

- **Kullanıcı:** "Bana şu konuda bir alıntı ver: &lt;etiket&gt;"
- **Asistan:** "&lt;alıntı&gt; – &lt;yazar&gt;"

İnce ayar, modele bir konu hakkında alıntı isteyen komutlara yanıt vermeyi ve bunları `<alıntı metni> - <yazar>` biçiminde döndürmeyi öğretir. LoRA ve tam ince ayar betikleri **databricks/databricks-dolly-15k** kullanır (genel talimat/yanıt çiftleri); bu nedenle tam görev betiğe göre değişir; temel fikir aynıdır: modeli seçtiğiniz veri kümesine ve biçime uyarlayın.

Aşağıda mevcut eğitim yöntemlerinin bir özeti yer almaktadır. Her yöntem kendi betiğine bağlantı verir ve doğru yaklaşımı seçmenize yardımcı olacak kısa bir açıklama sunar.

| Betik | Yöntem | Açıklama | Tipik VRAM | Önerilen Kullanım |
|-------|--------|----------|------------|-------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | Temel modeli dondururken küçük adaptör matrislerini eğitir. 3–5 kat daha hızlı; ~%95–98 tam kalite. | 24–32GB | İleri düzey kullanıcılar; birden fazla adaptör; daha fazla VRAM |
| [`train_qlora.py`](assets/train_qlora.py) *(yalnızca Linux)* | **QLoRA** | 4-bit niceleme + LoRA adaptörleri. En düşük bellek kullanımı, en hızlı, küçük kalite ödünü. `bitsandbytes` gerektirir (yalnızca Linux). | 12–16GB | Çoğu kullanıcı; hızlı denemeler; sınırlı VRAM |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Tam İnce Ayar** | Tüm model parametrelerini günceller. Maksimum kalite; en yüksek bellek ve hesaplama kullanımı. | 40GB+ | Maksimum kalite; araştırma; büyük VRAM |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Not:** Tam ince ayar (`train_full_finetuning.py`) 64 GB'tan fazla sistem RAM'i gerektirebilir ve bu cihazda uygulanabilir olmayabilir. Bunun yerine LoRA veya QLoRA kullanmayı düşünün.
<!-- @os:end -->

<!-- @os:windows -->
> **Not:** Tam ince ayar (`train_full_finetuning.py`) 64 GB'tan fazla sistem RAM'i gerektirebilir ve bu cihazda uygulanabilir olmayabilir. Bunun yerine LoRA kullanmayı düşünün.
<!-- @os:end -->
<!-- @device:end -->

Tercih ettiğiniz `Eğitim yöntemini` seçin, ilgili betiği indirin ve sanal ortamınızı etkin tutarak aşağıdaki komutu kullanarak çalıştırın:

```python
python3 train_<method_name>.py.
```

## İnce Ayarlı Modelinizi Kullanma

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

### LoRA Adaptörünü Temel Modelle Birleştirme

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Not:**  
- Model dizin adının (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) eğitimden elde ettiğiniz gerçek çıktı klasörüyle eşleştiğinden emin olun.  
- QLoRA yerine LoRA kullandıysanız yolu buna göre değiştirin.  
- Bazı Gemma modelleri `from_pretrained` içinde `trust_remote_code=True` belirtilmesini gerektirebilir; ilgili bir uyarı görürseniz ekleyin.

Daha fazla özel ayar (dolgu belirteçleri, aygıt vb.) için eğitimde kullandığınız betiğe başvurun.

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Özelleştirme Kılavuzu

### Kendi Veri Kümenizi Kullanma

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

**Yerel JSON/JSONL dosyası için Veri Kümesi Biçimi:**

Bu yöntemi kullanırken JSON dosyalarınızın ayrıştırma hatalarını önlemek için doğru yapılandırıldığından emin olun.

Aşağıdaki yönergelere uyulması gerekmektedir:
* **Dosya Biçimlendirme:** JSON dosyaları, uygun yapı ve sözdizimini sağlamak için bir Tümleşik Geliştirme Ortamı'nda (IDE) biçimlendirilmelidir.
* **Gerekli Anahtarlar:** Özel JSON dosyası `instruction` ve `response` anahtarlarını içermelidir. Bu anahtarlar yöntemin doğru çalışması için zorunludur.
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
**Hugging Face Hub veri kümesi için Veri Kümesi Biçimi**

Hugging Face'ten veri kümeleri kullanırken sorunsuz entegrasyonu kolaylaştırmak için veri kümelerinizin doğru yapılandırıldığından emin olun.

Aşağıdaki yönergelere uyulmalıdır:
* **Talimat-Yanıt Çifti:** `instruction-response` çifti içeren veri kümelerine odaklanın. Bu yapı, amaçlanan işlevsellik için zorunludur.
* **Özel Anahtar Değişikliği:** Veri kümeniz `instruction-response` yapısına uymuyorsa `format_instruction()` işlevini değiştirme seçeneğiniz vardır. Bu, gerektiğinde belirli anahtarları barındırmanıza olanak tanır.

Örnek Ayarlama: Veri kümesinin çıktısının ayarlanması gereken durumlarda, gereksinimlerinize uyacak şekilde format_instruction() işlevi içindeki yanıt bölümünü değiştirebilirsiniz.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV dosyası için Veri Kümesi Biçimi**

Betiği CSV dosya biçimiyle kullanmak için CSV dosyasının `instruction` ve `response` adlı sütunlar içerdiğinden emin olmanız gerekmektedir.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Eğitim Parametrelerini Ayarlama

Eğitim betiğini düzenleyin ve değişkenleri hedeflerinize göre değiştirin: **öğrenme hızı** (`LR`), **dönem sayısı** (`EPOCHS`), **toplu iş boyutu** (`BATCH_SIZE`), **gradyan birikimi** (`GRAD_ACCUM_STEPS`) ve LoRA/QLoRA için **sıra** (`LORA_R`). Daha hızlı çalışmalar için daha az dönem ve daha yüksek öğrenme hızı (LR) kullanın; daha iyi kalite için daha fazla dönem ve daha düşük LR kullanın. Bellek yetersizliği hatalarıyla karşılaşırsanız toplu iş boyutunu veya dizi uzunluğunu azaltın.

### Bellek Optimizasyon İpuçları

Bellek yetersizliği hatalarıyla karşılaşırsanız:

**1. Toplu İş Boyutunu Azaltın:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Dizi Uzunluğunu Azaltın:**
```python
max_seq_length=256  # Instead of 512
```

**3. Daha Agresif Niceleme Kullanın:**
```
Full → LoRA → QLoRA
```

**4. Gradyan Kontrol Noktasını Etkinleştirin (yalnızca tam ince ayar):**
```python
model.gradient_checkpointing_enable()
```

---

## İzleme ve Hata Ayıklama

### GPU Belleğini İzleme

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (İsteğe Bağlı) Weights & Biases ile Deneyleri Takip Etme

Çalışmaları ve metrikleri [Weights & Biases](https://wandb.ai) üzerine kaydetmek için:

```bash
pip install wandb
wandb login
```

Eğitim betiğinde, eğitici yapılandırmasında `report_to="wandb"` ve isteğe bağlı olarak `run_name="your-experiment-name"` ayarlayın. Wandb kullanmayı tercih etmiyorsanız `report_to` değerini varsayılanda bırakın veya `"none"` olarak ayarlayın.

### Yaygın Sorunlar

#### Bellek Yetersizliği (OOM)

**Çözüm:** Toplu iş boyutunu azaltın ve/veya QLoRA kullanın
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Kayıp Azalmıyor

**Çözüm:** Öğrenme hızını ayarlayın
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Yavaş Eğitim

**Çözüm:** Bellek izin veriyorsa toplu iş boyutunu artırın
```python
BATCH_SIZE = 8
```
## Sonraki Adımlar

Başarılı bir ince ayar tamamladıktan sonra modelinizden daha fazla yararlanmak için aşağıdaki adımları göz önünde bulundurun:

1. **Değerlendirin**: Genellemeyi ölçmek ve aşırı öğrenmeyi önlemek için ayrılmış test verileri üzerinde kapsamlı değerlendirme yapın.
2. **Deneyin**: Daha iyi doğruluk, hız ve bellek dengesi için farklı hiper parametre değerlerini deneyin.
3. **Takip Edin**: Tekrarlanabilir araştırma için tüm denemelerinizi (ve ilgili metrikleri) Weights & Biases ile kaydedin.
4. **Deneyin**: Modeli özel kullanım durumunuza göre uyarlamak için kendi özel veri kümelerinizde eğitin.
5. **Dağıtın**: İnce ayarlı modelinizi uyumlu donanımda vLLM gibi verimli arka uçları kullanarak hızlı çıkarım için dağıtın.
6. **Keşfedin**: İstem mühendisliği, karma hassasiyet ve daha uzun dizi uzunlukları dahil gelişmiş teknikleri inceleyin.
7. **Eğitin**: Farklı görevler veya alanlar için birden fazla LoRA adaptörü eğitin ve gerektiğinde bunları değiştirin.

---