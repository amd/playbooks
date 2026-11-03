<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

Цей посібник містить покрокові приклади донавчання великої мовної моделі (LLM) за допомогою PyTorch і ROCm. У ньому розглянуто кілька технік — від стандартного донавчання до економних щодо пам'яті стратегій Parameter-Efficient Fine-Tuning (PEFT), що дозволяє легко адаптувати моделі під ваші потреби.

**Використана модель**: google/gemma-3-4b-it  *(див. [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), якщо модель захищена)*  
**Обладнання**: AMD Radeon™ GPU з підтримкою ROCm  
**Фреймворк**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Примітка:** 
> - Для повного донавчання потрібно щонайменше **64 ГБ оперативної пам'яті системи**, з яких щонайменше **32 ГБ мають бути доступні GPU** (ці 32 ГБ входять до складу 64 ГБ, а не додаються до них).
> - Ви також можете спробувати інші архітектури моделей, зокрема **GPT-OSS-20B**, замінивши модель у наданих скриптах навчання.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Примітка:** Для донавчання LoRA та QLoRA потрібно щонайменше **32 ГБ оперативної пам'яті системи**, з яких щонайменше **16 ГБ мають бути доступні GPU** (ці 16 ГБ входять до складу 32 ГБ, а не додаються до них).
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка:** Для донавчання LoRA потрібно щонайменше **32 ГБ оперативної пам'яті системи**, з яких щонайменше **16 ГБ мають бути доступні GPU** (ці 16 ГБ входять до складу 32 ГБ, а не додаються до них).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примітка:** Для донавчання LoRA та QLoRA потрібна відеокарта з щонайменше **16 ГБ виділеної пам'яті GPU** та **32 ГБ оперативної пам'яті системи**.
> - У Linux навчання повністю виконується у виділеній пам'яті VRAM відеокарти.
> - Воно не переходить на спільну пам'ять GPU (оперативну пам'ять системи), коли VRAM вичерпується.
> - Відеокарти з менш ніж 16 ГБ виділеної VRAM вичерпають пам'ять під час навчання в Linux, навіть якщо система має багато оперативної пам'яті.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка:** Для донавчання LoRA потрібно щонайменше **16 ГБ загальної пам'яті GPU** та **32 ГБ оперативної пам'яті системи**.
> - У Windows загальна пам'ять GPU поєднує виділену VRAM відеокарти зі спільною пам'яттю GPU (запозиченою з оперативної пам'яті системи).
> - Тому відеокарти з менш ніж 16 ГБ виділеної VRAM все одно можуть використовуватися за цим посібником, використовуючи спільну пам'ять GPU для компенсації різниці.
<!-- @os:end -->
<!-- @device:end -->

## Що ви дізнаєтеся

- Як донавчати LLM за допомогою LoRA, QLoRA та повного донавчання з PyTorch і ROCm
- Як зберегти та розгорнути вашу донавчену модель
- Як відстежувати навчання та усувати типові проблеми

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

#### Створення віртуального середовища

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
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

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

#### Встановлення базових залежностей
<!-- @require:pytorch -->

#### Додаткові залежності

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Тут протестовано та підтримується лише базові пакети. **bitsandbytes погано підтримується у Windows**, тому встановлення для Windows не включає його; використовуйте LoRA або повне донавчання у Windows (QLoRA потребує bitsandbytes і призначена для Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Увімкнення автентифікації HF (захищені або власні / попередньо невстановлені моделі)

У цьому прикладі ми використовуємо **google/gemma-3-4b-it**, яка є **захищеною (gated)** моделлю. Вам потрібно прийняти умови моделі на Hugging Face, а потім автентифікуватися, щоб скрипти навчання могли її завантажити.

1. **Прийміть ліцензію:** Відкрийте [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), увійдіть (або створіть обліковий запис) і прийміть ліцензію/умови на сторінці моделі (наприклад, «Agree and access repository»).
2. **Встановіть і увійдіть:** Встановіть Hugging Face CLI, а потім виконайте стандартний вхід:

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

## Розуміння технік

### Що таке LoRA?

**LoRA (Low-Rank Adaptation)** залишає базову модель замороженою і навчає лише невеликі "адаптерні" матриці, які додаються до певних шарів. 

- **Ключова ідея**: замість оновлення величезної матриці ваг із мільйонами параметрів ми навчаємо низькорангове оновлення (дві невеликі матриці, добуток яких має набагато менше параметрів). Це дає значне скорочення кількості параметрів для навчання та VRAM, зберігаючи при цьому більшу частину якості повного донавчання.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Що таке QLoRA?

**QLoRA** поєднує **4-бітне квантування** з **LoRA**. Базова модель завантажується у 4-бітному форматі (значна економія пам'яті), а навчаються з підвищеною точністю лише адаптери LoRA. Таким чином ви отримуєте ефективність параметрів LoRA плюс значно нижче використання VRAM, з невеликим компромісом якості порівняно з повноточним LoRA. Зауважте, що 4-бітне квантування може спричиняти числову нестабільність (сплески втрат або NaN), тому користувачі часто можуть віддавати перевагу **LoRA**, якщо доступно достатньо VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Примітка**: Для базових моделей MXFP4, таких як `openai/gpt-oss-20b`, ми рекомендуємо використовувати **LoRA** (`train_lora.py`) замість QLoRA. 4-бітний шлях `bitsandbytes` у скрипті QLoRA зазвичай деквантує ваги MXFP4 до BF16, тому запуск поводиться як стандартна LoRA. Нативний MXFP4 потребує `bitsandbytes`, зібраного з вихідного коду, а також відповідного стеку Transformers/Triton/kernels. Див. [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Оберіть свій метод

| Метод | Пам'ять | Швидкість | Якість | Найкраще підходить для |
|--------|--------|-------|---------|----------|
| **QLoRA** (лише Linux) | 12-16GB | Найшвидший | 90-95% | Низького використання пам'яті |
| **LoRA** | 24-32GB | Швидкий | 95-98% | Збалансованого підходу |
| **Full** | 80GB+ | Найповільніший | 100% | Максимальної якості |

### 3. Запустіть навчання

**Набір даних і те, чого навчається модель**  
Скрипти перетворюють набір даних на приклади чату. Наприклад, скрипт QLoRA використовує **Abirate/english_quotes**: кожен приклад стає парою user–assistant, наприклад:

- **User:** «Give me a quote about: &lt;tag&gt;»
- **Assistant:** «&lt;quote&gt; – &lt;author&gt;»

Донавчання вчить модель реагувати на запити з проханням про цитату на певну тему та повертати їх у форматі `<quote text> - <author>`. Скрипти LoRA та повного донавчання використовують **databricks/databricks-dolly-15k** (загальні пари інструкція/відповідь), тому конкретне завдання відрізняється залежно від скрипта; ідея та сама - адаптувати модель до обраного вами набору даних і формату.

Нижче наведено підсумок доступних методів навчання. Кожен метод посилається на свій скрипт і містить короткий опис для вибору правильного підходу.

| Скрипт                           | Метод            | Опис                                                                                                         | Типовий VRAM | Рекомендовано для                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Навчає невеликі матриці адаптерів, заморожуючи базову модель. У 3–5 разів швидше; ~95–98% повної якості.                         | 24–32GB      | Досвідчені користувачі; кілька адаптерів; більше VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(лише Linux)*             | **QLoRA**       | 4-бітне квантування + адаптери LoRA. Найменше використання пам'яті, найшвидший, невеликий компроміс якості. Потребує `bitsandbytes` (лише Linux).                            | 12–16GB      | Більшість користувачів; швидкі експерименти; обмежений VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Повне донавчання** | Оновлює всі параметри моделі. Максимальна якість; найвище використання пам'яті та обчислень.                                    | 40GB+        | Максимальна якість; дослідження; великий VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примітка:** Повне донавчання (`train_full_finetuning.py`) може потребувати понад 64GB системної пам'яті RAM і може бути нездійсненним на цьому пристрої. Розгляньте можливість використання LoRA або QLoRA замість цього.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка:** Повне донавчання (`train_full_finetuning.py`) може потребувати понад 64GB системної пам'яті RAM і може бути нездійсненним на цьому пристрої. Розгляньте можливість використання LoRA замість цього.
<!-- @os:end -->
<!-- @device:end -->

Просто оберіть свій бажаний `Training method`, завантажте відповідний скрипт і виконайте його за допомогою команди, зберігаючи ваше віртуальне середовище активованим: 

```python
python3 train_<method_name>.py.
```

## Використання вашої донавченої моделі

### Після повного донавчання

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

### Після навчання LoRA/QLoRA

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

### Об'єднання адаптера LoRA з базовою моделлю

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Примітка:**  
- Переконайтеся, що назва каталогу моделі (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) відповідає вашій фактичній вихідній папці з навчання.  
- Якщо ви використовували LoRA замість QLoRA, просто замініть шлях відповідно.  
- Деякі моделі Gemma потребують вказання `trust_remote_code=True` у `from_pretrained`; додайте це, якщо ви бачите відповідне попередження.

Для більш індивідуальних налаштувань (токени доповнення, пристрій тощо) зверніться до скрипту, який ви використовували для навчання.

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

## Посібник з налаштування

### Використання власного набору даних

Усі скрипти використовують однаковий формат набору даних. Замініть розділ завантаження:

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

**Формат набору даних для локального файлу JSON/JSONL:**

Використовуючи цей метод, будь ласка, переконайтеся, що ваші файли JSON правильно структуровані, щоб уникнути помилок аналізу. 

Необхідно дотримуватися наступних рекомендацій:
* **Форматування файлу:** Файли JSON слід форматувати в інтегрованому середовищі розробки (IDE), щоб забезпечити належну структуру та синтаксис.
* **Обов'язкові ключі:** Користувацький файл JSON повинен містити ключі `instruction` та `response`. Ці ключі є важливими для правильного функціонування методу.
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
**Формат набору даних для набору даних Hugging Face Hub**

Використовуючи набори даних з Hugging Face, будь ласка, переконайтеся, що ваші набори даних структуровані правильно для забезпечення безперешкодної інтеграції. 

Слід дотримуватися наступних рекомендацій:
* **Пара інструкція-відповідь:** Зосередьтеся на наборах даних, що містять пару `instruction-response`. Ця структура є важливою для передбачуваної функціональності.
* **Модифікація користувацького ключа:** Якщо ваш набір даних не відповідає структурі `instruction-response`, у вас є можливість змінити функцію `format_instruction()`. Це дозволяє врахувати конкретні ключі за потреби.

Приклад коригування: У випадках, коли вихідні дані набору даних потребують коригування, ви можете змінити розділ відповіді у функції format_instruction(), щоб відповідати вашим вимогам.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Формат набору даних для файлу CSV**

Щоб пристосувати скрипт до використання формату файлу CSV, вам потрібно переконатися, що файл CSV містить стовпці з назвами `instruction` та `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Налаштування параметрів навчання

Відредагуйте скрипт навчання та змініть змінні відповідно до ваших цілей: **швидкість навчання** (`LR`), **епохи** (`EPOCHS`), **розмір пакету** (`BATCH_SIZE`), **накопичення градієнта** (`GRAD_ACCUM_STEPS`), а для LoRA/QLoRA — **ранг** (`LORA_R`). Для швидшого запуску використовуйте менше епох і вищу швидкість навчання (LR); для кращої якості використовуйте більше епох і нижчу LR. Зменшіть розмір пакету або довжину послідовності, якщо ви стикаєтеся з помилками нестачі пам'яті.
### Поради з оптимізації пам'яті

Якщо ви стикаєтеся з помилками нестачі пам'яті:

**1. Зменшіть розмір батчу:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Зменшіть довжину послідовності:**
```python
max_seq_length=256  # Instead of 512
```

**3. Використовуйте більш агресивне квантування:**
```
Full → LoRA → QLoRA
```

**4. Увімкніть Gradient Checkpointing (лише для повного тонкого налаштування):**
```python
model.gradient_checkpointing_enable()
```

---

## Моніторинг і налагодження

### Спостереження за пам'яттю GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Необов'язково) Відстеження експериментів за допомогою Weights & Biases

Щоб реєструвати запуски та метрики у [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

У скрипті навчання встановіть `report_to="wandb"` та за бажанням `run_name="your-experiment-name"` у конфігурації trainer. Якщо ви не бажаєте використовувати Wandb, залиште `report_to` зі значенням за замовчуванням або встановіть `"none"`.

### Поширені проблеми

#### Нестача пам'яті (OOM)

**Рішення:** Зменшіть розмір батчу та/або використовуйте QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Втрати не зменшуються

**Рішення:** Скоригуйте швидкість навчання
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Повільне навчання

**Рішення:** Збільшіть розмір батчу, якщо дозволяє пам'ять
```python
BATCH_SIZE = 8
```
## Наступні кроки

Після успішного завершення тонкого налаштування розгляньте наступні кроки, щоб отримати більше від вашої моделі:

1. **Оцініть** модель ретельно на відкладених тестових даних, щоб виміряти узагальнення та уникнути перенавчання.
2. **Експериментуйте**, пробуючи різні значення гіперпараметрів для кращого балансу точності, швидкості та використання пам'яті.
3. **Відстежуйте** всі свої експерименти (та відповідні метрики) за допомогою Weights & Biases для відтворюваних досліджень.
4. **Спробуйте** навчання на власних користувацьких наборах даних, щоб адаптувати модель спеціально під ваш випадок використання.
5. **Розгорніть** вашу тонко налаштовану модель для швидкого інференсу за допомогою ефективних бекендів, таких як vLLM, на сумісному обладнанні.
6. **Досліджуйте** просунуті техніки, включаючи проєктування промптів, змішану точність та довші послідовності.
7. **Навчайте** кілька LoRA-адаптерів для різних завдань чи доменів і замінюйте їх за потреби.

---