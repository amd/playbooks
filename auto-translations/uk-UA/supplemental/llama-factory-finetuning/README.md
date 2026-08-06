<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

## Огляд

Ефективне тонке налаштування є важливим для адаптації великих мовних моделей (LLM) до прикладних завдань. LLaMA Factory — це платформа з відкритим кодом, зручна у використанні, яка спрощує навчання та тонке налаштування великих мовних моделей і мультимодальних моделей. Вона дозволяє користувачам налаштовувати сотні попередньо навчених моделей локально з мінімальним обсягом кодування.

Цей посібник навчить вас тонко налаштовувати LLM за допомогою LLaMA Factory на вашому локальному апаратному забезпеченні AMD.

<!-- @device:stx,krk -->
> **Примітка.** Методи тонкого налаштування, описані в цьому посібнику, вимагають щонайменше **32 ГБ системної оперативної пам'яті**, з яких щонайменше **16 ГБ має бути доступно для GPU** (ці 16 ГБ є частиною 32 ГБ, а не додатковим обсягом).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примітка.** Методи тонкого налаштування, описані в цьому посібнику, вимагають щонайменше **16 ГБ загальної пам'яті GPU** та **32 ГБ системної оперативної пам'яті**.
> - У Windows загальна пам'ять GPU об'єднує виділену відеопам'ять (VRAM) відеокарти зі спільною пам'яттю GPU (запозиченою із системної оперативної пам'яті).
> - Тому відеокарти з менше ніж 16 ГБ виділеної VRAM все ще можуть використовуватися для роботи з цим посібником, використовуючи спільну пам'ять GPU для компенсації різниці.
<!-- @os:end -->

<!-- @os:linux -->
> **Примітка.** Методи тонкого налаштування, описані в цьому посібнику, вимагають відеокарти з щонайменше **16 ГБ виділеної пам'яті GPU** та **32 ГБ системної оперативної пам'яті**.
> - У Linux навчання виконується повністю у виділеній VRAM відеокарти.
> - Воно не переходить на спільну пам'ять GPU (системну оперативну пам'ять), коли VRAM вичерпується.
> - Відеокарти з менше ніж 16 ГБ виділеної VRAM вичерпають пам'ять під час навчання в Linux, навіть якщо в системі достатньо оперативної пам'яті.
<!-- @os:end -->
<!-- @device:end -->

## Що ви вивчите

- Як налаштувати LLaMA Factory з програмним забезпеченням AMD ROCm™
- Як налаштувати параметри тонкого налаштування LLM (на прикладі Qwen/Qwen3-4B-Instruct-2507)
- Як запустити тонке налаштування LLaMA Factory
- Як виконати інференс з тонко налаштованою моделлю
- Як експортувати тонко налаштовану модель 

## Орієнтовний час

- Тривалість: виконання цього посібника займе приблизно 60 хвилин (залежно від розміру вашої моделі/набору даних та швидкості мережі).
- Перегляньте [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) для отримання додаткової інформації.

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

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

#### Створення віртуального середовища

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
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

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

### Встановлення основних залежностей

<!-- @require:pytorch,driver -->
 
### Встановлення додаткових залежностей

> **Примітка**: Переконайтеся, що версія Python — 3.11, 3.12 або 3.13

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

### Встановлення LLaMA Factory

LLaMA Factory залежить від PyTorch. Він уже має бути встановлений відповідно до наведених вище вимог.

Завантажте вихідний код з [офіційного репозиторію LLaMA Factory на GitHub](https://github.com/hiyouga/LlamaFactory) та встановіть його залежності.

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

Перевірте, чи виконується `llamafactory-cli`.

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

Приклад виводу:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Успішно встановивши LLaMA Factory, перейдемо до запуску тонкого налаштування.

## Використання LLaMA Factory CLI для тонкого налаштування 

У цьому розділі описано, як підготувати набори даних для тонкого налаштування, налаштувати параметри LoRA/QLoRA та запустити тонке налаштування LoRA.

### Підготовка набору даних

LLaMA Factory підтримує набори даних для тонкого налаштування у форматах Alpaca та ShareGPT. Усі доступні набори даних визначені у файлі [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Якщо ви використовуєте власний набір даних, обов'язково додайте опис набору даних у `dataset_info.json` та вкажіть назву набору даних перед навчанням. Детальнішу інформацію можна знайти в їхній документації [тут](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

У цьому посібнику як приклад ми використаємо набори даних identity та alpaca_en_demo, а конфігурацію інформації про набір даних налаштуємо на наступному кроці.
### Налаштування параметрів донавчання

LLaMA Factory підтримує кілька схем донавчання.

| Схема донавчання | Приклади LLaMA Factory |
|-----------|------|
| Повнопараметричне    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Донавчання LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Донавчання QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

У цих прикладах файлів конфігурації вказано параметри моделі, параметри методу донавчання, параметри набору даних, параметри оцінювання та інше. Ви можете налаштувати їх відповідно до власних потреб. У цьому посібнику ми використаємо [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Пояснення ключових параметрів:**
- `model_name_or_path` - назва моделі Hugging Face або шлях до локального файлу моделі.
- `stage` - етап навчання. Варіанти: rm (моделювання винагороди), pt (попереднє навчання), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true для навчання, false для оцінювання
- `finetuning_type` - метод донавчання. Варіанти: freeze, lora, full
- `lora_rank` - розмірність матриці низького рангу, яка використовується в LoRA, типові значення: 4, 6, 8, 16 (менші значення = менше параметрів = швидше донавчання; більші значення = краща адаптація до задачі, але вищі вимоги до ресурсів).
- `lora_target` - цільові модулі для методу LoRA. За замовчуванням: all.
- `dataset` - набір(и) даних для використання. Використовуйте «,» для розділення кількох наборів даних
- `output_dir` - шлях для виведення результатів донавчання
- `logging_steps` - інтервал логування у кроках
- `save_steps` - інтервал збереження контрольної точки моделі.
- `overwrite_output_dir` - чи дозволяти перезапис вихідного каталогу.
- `per_device_train_batch_size` - розмір навчального пакету (batch) на пристрій.
- `gradient_accumulation_steps` - кількість кроків накопичення градієнта.
- `learning_rate` - швидкість навчання
- `num_train_epochs` - кількість епох навчання
- `lr_scheduler_type` - розклад швидкості навчання. Варіанти: linear, cosine, polynomial, constant тощо.
- `warmup_ratio` - коефіцієнт розігріву швидкості навчання

<!-- @os:linux -->
Ми змінимо значення `lora_rank` за замовчуванням, щоб запустити донавчання на AMD Ryzen™ та AMD Radeon™ GPU.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Ми оновимо конфігурацію донавчання LoRA за замовчуванням для кращої сумісності з AMD Ryzen™ та AMD Radeon™ GPU:
- Змінимо `lora_rank` з `8` на `6`, щоб зменшити використання пам'яті під час донавчання.
- Використовуватимемо `fp16` замість `bf16` для ширшої сумісності з AMD GPU та меншого використання пам'яті.
- Встановимо `dataloader_num_workers` на `0` у Windows, щоб уникнути помилок `"Can't pickle local object<>"`, спричинених багатопроцесним завантаженням даних.

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

### Запуск донавчання LLaMA Factory 

**llamafactory-cli** — це офіційний інструмент інтерфейсу командного рядка (CLI) для LLaMA Factory, розроблений для спрощення наскрізних робочих процесів LLM (підготовка даних → донавчання → оцінювання → розгортання) без написання складного коду.

Для навчання/донавчання **llamafactory-cli train** є основною підкомандою CLI LLaMA Factory. Вона абстрагує робочі процеси донавчання (попередня обробка даних, налаштування гіперпараметрів, оптимізація апаратного забезпечення) в єдину команду CLI, підтримуючи кілька парадигм донавчання (LoRA/QLoRA/повнопараметричне донавчання) та оптимізована для GPU з обмеженими ресурсами (наприклад, QLoRA на 16 ГБ VRAM).

Ви можете запустити донавчання LLaMA Factory за допомогою наведеної нижче команди, яка базується на зміненому файлі конфігурації для донавчання Qwen3 LoRA.

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

Після запуску донавчання LLM усі згенеровані результати зберігаються у каталозі "output_dir", включно з файлами контрольних точок моделі, файлами конфігурації та метриками навчання.

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

### Тестування донавченої моделі 

**llamafactory-cli chat** призначено для інтерактивного чату/інференсу з LLM (як з базовими моделями, так і з моделями, донавченими за допомогою LoRA). LLaMA Factory надає приклад конфігурації для запуску інференсу донавчених моделей у [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Ви також можете змінити цю приклад-конфігурацію, щоб змінити налаштування, наприклад бекенд інференсу.

Скористайтеся наведеною нижче командою для тестування донавченої моделі Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Нижче наведено приклад чату з використанням донавченої моделі:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Експорт донавченої моделі

Для промислового використання попередньо навчену модель та адаптер LoRA потрібно об'єднати та експортувати в одну модель. Цю об'єднану модель можна використовувати як звичайний файл моделі Hugging Face. LLaMA Factory надає приклади конфігурацій у [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Скористайтеся наведеною нижче командою для експорту донавченої моделі Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Результат експорту донавченої моделі показано нижче.

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
## Використання графічного інтерфейсу LLaMA Factory

`LLaMA-Factory` також підтримує безкодове донавчання LLM за допомогою веб-інтерфейсу в браузері.

Використайте наступну команду, щоб відкрити його:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` пропонує зручний інтерфейс для керування робочими процесами машинного навчання, включно з навчанням, оцінюванням, прогнозуванням, чатом та експортом моделей. Ось короткий опис кожної вкладки:

* **Train**: ця вкладка дозволяє вибрати модель і набір даних, налаштувати параметри навчання та розпочати процес навчання. Важливо розуміти обов'язкові та необов'язкові параметри, щоб оптимізувати налаштування навчання.
* **Evaluate & Predict**: після навчання ви можете оцінити продуктивність моделі та зробити прогнози за допомогою цієї вкладки. Вона надає інформацію про точність та ефективність моделі на нових даних.
* **Chat**: після завершення навчання завантажте модель у вкладці Chat, щоб взаємодіяти з нею та побачити результати вашої роботи. Ця функція дозволяє спілкуватися з навченою моделлю в реальному часі.
* **Export**: ця вкладка полегшує експорт навчених моделей для розгортання або подальшого використання. Ви можете зберегти свої моделі у різних форматах, придатних для різних застосунків.

Для детальнішої інформації радимо звернутися до офіційної документації в [репозиторії LlamaFactory на GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) та [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Крім того, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) надає цінну інформацію про інтерфейс та його функціональність.

## Наступні кроки
- Спробуйте різні моделі, такі як `gpt-oss` та інші сучасні моделі.
- Поекспериментуйте з різними бекендами на донавченій моделі
 
Для отримання додаткової документації відвідайте: https://llamafactory.readthedocs.io/en/latest/