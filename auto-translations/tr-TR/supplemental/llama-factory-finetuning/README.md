<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

## Genel Bakış

Büyük dil modellerini (LLM'ler) alt görevlere uyarlamak için verimli ince ayar (fine-tuning) hayati önem taşır. LLaMA Factory, büyük dil modellerinin ve çok modlu modellerin eğitimini ve ince ayarını kolaylaştıran açık kaynaklı ve kullanıcı dostu bir platformdur. Kullanıcıların minimum kodlamayla yüzlerce önceden eğitilmiş modeli yerel olarak özelleştirmesine olanak tanır.

Bu kılavuz, yerel AMD donanımınızda LLaMA Factory kullanarak LLM'lere nasıl ince ayar yapılacağını öğretir.

<!-- @device:stx,krk -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **32 GB sistem RAM'i** ve bunun en az **16 GB'ının GPU için kullanılabilir** olmasını gerektirir (bu 16 GB, 32 GB'a ek değil, onun bir parçasıdır).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **16 GB toplam GPU belleği** ve **32 GB sistem RAM'i** gerektirir.
> - Windows'ta toplam GPU belleği, grafik kartının özel VRAM'i ile paylaşılan GPU belleğini (sistem RAM'inden ödünç alınan) birleştirir.
> - Bu nedenle, 16 GB'dan daha az özel VRAM'e sahip kartlar, farkı kapatmak için paylaşılan GPU belleğini kullanarak bu kılavuzu yine de çalıştırabilir.
<!-- @os:end -->

<!-- @os:linux -->
> **Not:** Bu kılavuzdaki ince ayar teknikleri en az **16 GB özel GPU belleğine** ve **32 GB sistem RAM'ine** sahip bir grafik kartı gerektirir.
> - Linux'ta eğitim tamamen grafik kartının özel VRAM'inde çalışır.
> - VRAM tükendiğinde paylaşılan GPU belleğine (sistem RAM'i) geri dönüş yapılmaz.
> - 16 GB'dan daha az özel VRAM'e sahip kartlar, sistemde bolca RAM olsa bile Linux üzerinde eğitim sırasında bellek yetersizliği yaşayacaktır.
<!-- @os:end -->
<!-- @device:end -->

## Bu Kılavuzda Öğrenecekleriniz

- AMD ROCm™ yazılımıyla LLaMA Factory'nin nasıl kurulacağı
- LLM ince ayar parametrelerinin nasıl yapılandırılacağı (örnek olarak Qwen/Qwen3-4B-Instruct-2507 kullanılarak)
- LLaMA Factory ince ayarının nasıl çalıştırılacağı
- İnce ayarlı modelle çıkarımın (inference) nasıl yapılacağı
- İnce ayarlı modelin nasıl dışa aktarılacağı 

## Tahmini Süre

- Süre: Bu kılavuzu çalıştırmak yaklaşık 60 dakika sürecektir (model/veri seti boyutunuza ve ağ hızınıza bağlı olarak).
- Daha fazla bilgi için [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) sayfasını ziyaret edin.

## Bellek Yapılandırmasının Ayarlanması

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerinin Kontrol Edilmesi

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Kurulumu

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU cihazlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp tekrar açmanız gerekir):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### Temel Bağımlılıkların Kurulumu

<!-- @require:pytorch,driver -->
 
### Ek Bağımlılıkların Kurulumu

> **Not**: Python sürümünün 3.11, 3.12 veya 3.13 olduğundan emin olun

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### LLaMA Factory Kurulumu

LLaMA Factory, PyTorch'a bağımlıdır. Yukarıdaki gereksinimlere göre bunu zaten kurmuş olmalısınız.

Kaynak kodunu [LLaMA Factory resmi GitHub deposundan](https://github.com/hiyouga/LlamaFactory) indirin ve bağımlılıklarını kurun.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

`llamafactory-cli`'nin çalıştırılabilir olup olmadığını doğrulayın.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Örnek çıktı:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

LLaMA Factory'yi başarıyla kurduğunuza göre, şimdi üzerinde ince ayarı çalıştıralım.

## İnce Ayar için LLaMA Factory CLI'nin Kullanılması 

Bu bölümde, ince ayar veri setlerinin nasıl hazırlanacağı, LoRA/QLoRA parametrelerinin nasıl yapılandırılacağı ve LoRA ince ayarının nasıl çalıştırılacağı ele alınacaktır.

### Veri Seti Hazırlığı

LLaMA Factory, Alpaca formatında ve ShareGPT formatında ince ayar veri setlerini destekler. Kullanılabilir tüm veri setleri [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) dosyasında tanımlanmıştır. Özel bir veri seti kullanıyorsanız, lütfen `dataset_info.json` dosyasına bir veri seti açıklaması eklediğinizden ve eğitimden önce veri seti adını belirttiğinizden emin olun. Ayrıntıları [buradaki](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html) belgelerinde bulabilirsiniz.

Bu kılavuzda örnek olarak identity ve alpaca_en_demo veri setlerini kullanacağız ve veri seti bilgilerini bir sonraki adımda yapılandıracağız.
### İnce ayar parametre yapılandırması

LLaMA Factory birden fazla ince ayar (fine-tuning) şemasını destekler.

| İnce Ayar şemaları | LLaMA Factory Örnekleri |
|-----------|------|
| Tüm Parametreler (Full-Parameter)    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA ince ayarı  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA ince ayarı | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Bu örnek yapılandırma dosyaları, model parametrelerini, ince ayar yöntemi parametrelerini, veri kümesi parametrelerini, değerlendirme parametrelerini ve daha fazlasını belirtmiştir. Bunları kendi ihtiyaçlarınıza göre yapılandırabilirsiniz. Bu kılavuzda [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml) dosyasını kullanacağız.

**Açıklanan temel parametreler:**
- `model_name_or_path` - Hugging Face model adı veya yerel model dosyası yolu.
- `stage` - Eğitim aşaması. Seçenekler: rm (ödül modelleme), pt (ön eğitim), sft (Denetimli İnce Ayar), PPO, DPO, KTO, ORPO.
- `do_train` - Eğitim için true, değerlendirme için false
- `finetuning_type` - İnce ayar yöntemi. Seçenekler: freeze, lora, full
- `lora_rank` - LoRA'da kullanılan düşük dereceli matrisin boyutu, tipik değerler: 4, 6, 8, 16 (daha küçük değerler = daha az parametre = daha hızlı ince ayar; daha büyük değerler = daha iyi görev uyumu ancak daha yüksek kaynak kullanımı).
- `lora_target` - LoRA yöntemi için hedef modüller. Varsayılan: all.
- `dataset` - Kullanılacak veri kümesi(leri). Birden fazla veri kümesini ayırmak için "," kullanın
- `output_dir` - İnce ayar çıktı yolu
- `logging_steps` - Adım cinsinden günlükleme aralığı
- `save_steps` - Model kontrol noktası kaydetme aralığı.
- `overwrite_output_dir` - Çıktı dizininin üzerine yazmaya izin verilip verilmeyeceği.
- `per_device_train_batch_size` - Cihaz başına eğitim yığın (batch) boyutu.
- `gradient_accumulation_steps` - Gradyan biriktirme adımlarının sayısı.
- `learning_rate` - Öğrenme oranı
- `num_train_epochs` - Eğitim epoch sayısı
- `lr_scheduler_type` - Öğrenme oranı zamanlaması. Seçenekler: linear, cosine, polynomial, constant, vb.
- `warmup_ratio` - Öğrenme oranı ısınma (warmup) oranı

<!-- @os:linux -->
AMD Ryzen™ ve AMD Radeon™ GPU'larda ince ayarı çalıştırmak için `lora_rank` varsayılan değerini değiştireceğiz.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
AMD Ryzen™ ve AMD Radeon™ GPU'larla daha iyi uyumluluk için varsayılan LoRA ince ayarı yapılandırmasını güncelleyeceğiz:
- İnce ayar sırasında bellek kullanımını azaltmak için `lora_rank` değerini `8`'den `6`'ya ayarlayın.
- Daha geniş AMD GPU uyumluluğu ve daha düşük bellek kullanımı için `bf16` yerine `fp16` kullanın.
- Windows'ta çoklu işlemli veri yüklemenin neden olduğu `"Can't pickle local object<>"` hatalarından kaçınmak için `dataloader_num_workers` değerini `0` olarak ayarlayın.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### LLaMA Factory İnce Ayarını Çalıştırma 

**llamafactory-cli**, karmaşık kod yazmadan uçtan uca LLM iş akışlarını (veri hazırlama → ince ayar → değerlendirme → dağıtım) basitleştirmek için geliştirilen LLaMA Factory'nin resmi komut satırı arayüzü (CLI) aracıdır.

Eğitim/ince ayar için **llamafactory-cli train**, LLaMA Factory CLI'nin temel alt komutudur. İnce ayar iş akışlarını (veri ön işleme, hiperparametre ayarlama, donanım optimizasyonu) tek bir CLI komutunda soyutlar, birden fazla ince ayar paradigmasını (LoRA/QLoRA/Tam İnce Ayar) destekler ve düşük kaynaklı GPU'lar için optimize edilmiştir (örneğin, 16GB VRAM üzerinde QLoRA).

Qwen3 LoRA ince ayarının değiştirilmiş yapılandırma dosyasına dayanan aşağıdaki komutu kullanarak LLaMA Factory ince ayarını çalıştırabilirsiniz.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

LLM ince ayarını çalıştırdıktan sonra, oluşturulan tüm çıktılar model kontrol noktası dosyaları, yapılandırma dosyaları ve eğitim ölçümleri dahil olmak üzere "output_dir" içinde saklanır.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### İnce ayarlı modeli test etme 

**llamafactory-cli chat**, LLM'lerle (hem temel modeller hem de LoRA ile ince ayarlanmış modeller) etkileşimli sohbet/çıkarım için tasarlanmıştır. LLaMA Factory, ince ayarlı modellerin çıkarımını çalıştırmak için [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) içinde örnek bir yapılandırma sağlar. Çıkarım arka ucu gibi ayarları değiştirmek için bu örnek yapılandırmayı da değiştirebilirsiniz.

Qwen3 ince ayarlı modelini test etmek için aşağıdaki komutu kullanın:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
İnce ayarlı model kullanılarak yapılan bir örnek sohbet aşağıda gösterilmiştir:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### İnce ayarlı modeli dışa aktarma

Üretim kullanım durumları için, ön eğitilmiş model ve LoRA bağdaştırıcısının (adapter) birleştirilip tek bir model olarak dışa aktarılması gerekir. Bu birleştirilmiş model, normal bir Hugging Face model dosyası olarak kullanılabilir. LLaMA Factory, [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora) içinde örnek yapılandırmalar sağlar.

Qwen3 ince ayarlı modelini dışa aktarmak için aşağıdaki komutu kullanın:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
İnce ayarlı modeli dışa aktarma sonucu aşağıda gösterilmiştir.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
## LLaMA Factory GUI Kullanımı

`LLaMA-Factory`, tarayıcıdaki bir web arayüzü aracılığıyla LLM'lerin kod yazmadan ince ayarını yapmayı da destekler.

Açmak için aşağıdaki komutu kullanın:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI`, eğitim, değerlendirme, tahmin, sohbet etme ve modelleri dışa aktarma dahil olmak üzere makine öğrenimi iş akışlarını yönetmek için sadeleştirilmiş bir arayüz sunar. İşte her sekmeye kısa bir giriş:

* **Train**: Bu sekme, bir model ve veri kümesi seçmenize, eğitim parametrelerini yapılandırmanıza ve eğitim sürecini başlatmanıza olanak tanır. Eğitim kurulumunu optimize etmek için zorunlu ve isteğe bağlı parametreleri anlamak önemlidir.
* **Evaluate & Predict**: Eğitimden sonra, bu sekmeyi kullanarak modelin performansını değerlendirebilir ve tahminler yapabilirsiniz. Modelin yeni veriler üzerindeki doğruluğu ve etkinliği hakkında bilgi sağlar.
* **Chat**: Eğitim tamamlandıktan sonra, modeli Chat sekmesinde yükleyerek onunla etkileşim kurabilir ve çalışmanızın sonuçlarını görebilirsiniz. Bu özellik, eğitilmiş modelle gerçek zamanlı iletişim kurulmasını sağlar.
* **Export**: Bu sekme, eğitilmiş modellerin dağıtım veya daha ileri kullanım için dışa aktarılmasını kolaylaştırır. Modellerinizi farklı uygulamalara uygun çeşitli formatlarda kaydedebilirsiniz.

Ayrıntılı rehberlik için, [LlamaFactory GitHub deposundaki](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) resmi belgelere ve [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) sayfasına başvurmanızı öneririz. Ayrıca, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) sayfası arayüz ve işlevleri hakkında değerli bilgiler sunar.

## Sonraki Adımlar
- `gpt-oss` gibi farklı modelleri ve diğer son teknoloji modelleri deneyin.
- İnce ayarı yapılmış model üzerinde farklı arka uçları deneyin

Daha fazla belge için lütfen şu adresi ziyaret edin: https://llamafactory.readthedocs.io/en/latest/