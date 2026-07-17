<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

Цей посібник містить покрокові приклади тонкого налаштування великої мовної моделі (LLM) за допомогою PyTorch та ROCm. Він охоплює кілька технік — від стандартного тонкого налаштування до ефективних за пам'яттю стратегій Parameter-Efficient Fine-Tuning (PEFT) — щоб ви могли легко адаптувати моделі під свої потреби.

**Використовувана модель**: google/gemma-3-4b-it  *(див. [Увімкнення автентифікації HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), якщо модель є закритою)*  
**Апаратне забезпечення**: AMD Radeon™ GPU з підтримкою ROCm  
**Фреймворк**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Примітка:** Ви також можете спробувати інші архітектури моделей, зокрема **GPT-OSS-20B**, замінивши модель у наданих скриптах навчання.
> Повне тонке налаштування потребує щонайменше 32 ГБ пам'яті GPU та 64 ГБ системної оперативної пам'яті.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Примітка:** Тонке налаштування LoRA та QLoRA потребує щонайменше 16 ГБ пам'яті GPU та 32 ГБ системної оперативної пам'яті.
<!-- @device:end -->

## Що ви дізнаєтесь

- Як виконати тонке налаштування LLM за допомогою LoRA, QLoRA та повного тонкого налаштування з PyTorch і ROCm
- Як зберегти та розгорнути вашу налаштовану модель
- Як відстежувати навчання та усувати типові проблеми

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідних програмних компонентів

#### Створення віртуального середовища

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
**Надайте вашому користувачу доступ до пристроїв GPU** (для набрання чинності необхідно вийти з системи та увійти знову):

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

#### Встановлення базових залежностей
<!-- @require:pytorch -->

#### Додаткові залежності

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Тут перевірено та підтримується лише основний набір пакетів. **bitsandbytes погано підтримується на Windows**, тому встановлення для Windows його не включає; використовуйте LoRA або повне тонке налаштування на Windows (QLoRA потребує bitsandbytes і призначений для Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Увімкнення автентифікації HF (закриті або власні / не попередньо встановлені моделі)

У цьому прикладі ми використовуємо **google/gemma-3-4b-it** — це **закрита** модель. Ви повинні прийняти умови використання моделі на Hugging Face, а потім пройти автентифікацію, щоб скрипти навчання могли її завантажити.

1. **Прийміть ліцензію:** Відкрийте [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), увійдіть в обліковий запис (або створіть його) та прийміть ліцензію/умови на сторінці моделі (наприклад, «Agree and access repository»).
2. **Встановіть та увійдіть:** Встановіть Hugging Face CLI, а потім виконайте стандартний вхід:

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

**LoRA (Low-Rank Adaptation)** зберігає базову модель замороженою та навчає лише невеликі «адаптерні» матриці, які додаються до певних шарів.

- **Ключова ідея**: замість оновлення величезної матриці ваг з мільйонами параметрів ми навчаємо низькорангове оновлення (дві невеликі матриці, добуток яких має значно менше параметрів). Це дає суттєве скорочення кількості параметрів, що навчаються, та обсягу VRAM, зберігаючи при цьому більшу частину якості повного тонкого налаштування.

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

**QLoRA** поєднує **4-бітне квантування** з **LoRA**. Базова модель завантажується у 4-бітному форматі (значна економія пам'яті), а навчаються лише адаптери LoRA у вищій точності. Таким чином ви отримуєте ефективність параметрів LoRA разом із значно меншим обсягом VRAM, з невеликим компромісом у якості порівняно з LoRA у повній точності. Зверніть увагу, що 4-бітне квантування може спричиняти числову нестабільність (стрибки втрат або NaN), тому користувачі часто можуть надавати перевагу **LoRA**, якщо доступно достатньо VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Примітка**: Для базових моделей MXFP4, таких як `openai/gpt-oss-20b`, ми рекомендуємо використовувати **LoRA** (`train_lora.py`) замість QLoRA. Шлях 4-бітного квантування `bitsandbytes` у скрипті QLoRA зазвичай деквантує ваги MXFP4 до BF16, тому виконання поводиться як стандартний LoRA. Нативний MXFP4 потребує `bitsandbytes`, зібраного з вихідного коду, а також відповідного стеку Transformers/Triton/ядер. Дивіться [документацію Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Оберіть свій метод

| Метод | Пам'ять | Швидкість | Якість | Найкраще підходить для |
|--------|--------|-------|---------|----------|
| **QLoRA** (лише Linux) | 12–16 ГБ | Найшвидший | 90–95% | Мінімальне використання пам'яті |
| **LoRA** | 24–32 ГБ | Швидкий | 95–98% | Збалансований підхід |
| **Повне** | 80+ ГБ | Найповільніший | 100% | Максимальна якість |

### 3. Запустіть навчання

**Набір даних і що модель вивчає**  
Скрипти перетворюють набір даних на приклади у форматі чату. Наприклад, скрипт QLoRA використовує **Abirate/english_quotes**: кожен приклад стає парою користувач–асистент:

- **Користувач:** «Give me a quote about: &lt;tag&gt;»
- **Асистент:** «&lt;quote&gt; – &lt;author&gt;»

Тонке налаштування навчає модель відповідати на запити щодо цитат на певну тему та повертати їх у форматі `<quote text> - <author>`. Скрипти LoRA та повного тонкого налаштування використовують **databricks/databricks-dolly-15k** (загальні пари інструкція/відповідь), тому конкретне завдання залежить від скрипту; ідея та сама — адаптувати модель до обраного набору даних і формату.

Нижче наведено зведення доступних методів навчання. Кожен метод посилається на відповідний скрипт і містить короткий опис для вибору правильного підходу.

| Скрипт | Метод | Опис | Типовий VRAM | Рекомендовано для |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | Навчає невеликі адаптерні матриці, заморожуючи базову модель. У 3–5 разів швидше; ~95–98% повної якості. | 24–32 ГБ | Досвідчені користувачі; кілька адаптерів; більше VRAM |
| [`train_qlora.py`](assets/train_qlora.py) *(лише Linux)* | **QLoRA** | 4-бітне квантування + адаптери LoRA. Найменше використання пам'яті, найшвидший, невеликий компроміс у якості. Потребує `bitsandbytes` (лише Linux). | 12–16 ГБ | Більшість користувачів; швидкі експерименти; обмежений VRAM |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Повне тонке налаштування** | Оновлює всі параметри моделі. Максимальна якість; найвище використання пам'яті та обчислень. | 40+ ГБ | Максимальна якість; дослідження; великий VRAM |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примітка:** Повне тонке налаштування (`train_full_finetuning.py`) може потребувати більше 64 ГБ системної оперативної пам'яті та може бути нездійсненним на цьому пристрої. Розгляньте використання LoRA або QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка:** Повне тонке налаштування (`train_full_finetuning.py`) може потребувати більше 64 ГБ системної оперативної пам'яті та може бути нездійсненним на цьому пристрої. Розгляньте використання LoRA.
<!-- @os:end -->
<!-- @device:end -->

Просто оберіть бажаний `Метод навчання`, завантажте відповідний скрипт і виконайте його за допомогою наведеної команди, зберігаючи активованим ваше віртуальне середовище:

```python
python3 train_<method_name>.py.
```

## Використання вашої налаштованої моделі

### Після повного тонкого налаштування

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

### Злиття адаптера LoRA з базовою моделлю

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Примітка:**  
- Переконайтеся, що назва директорії моделі (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) відповідає вашій фактичній вихідній папці після навчання.  
- Якщо ви використовували LoRA замість QLoRA, просто замініть шлях відповідним чином.  
- Деякі моделі Gemma потребують вказання `trust_remote_code=True` у `from_pretrained`; додайте це, якщо побачите відповідне попередження.

Для більш детального налаштування (токени заповнення, пристрій тощо) зверніться до скрипту, який ви використовували для навчання.

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

При використанні цього методу переконайтеся, що ваші файли JSON правильно структуровані, щоб уникнути помилок розбору.

Необхідно дотримуватися таких вимог:
* **Форматування файлу:** Файли JSON слід форматувати в інтегрованому середовищі розробки (IDE) для забезпечення правильної структури та синтаксису.
* **Обов'язкові ключі:** Власний файл JSON повинен містити ключі `instruction` та `response`. Ці ключі є обов'язковими для правильної роботи методу.
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

При використанні наборів даних з Hugging Face переконайтеся, що ваші набори даних правильно структуровані для забезпечення безперебійної інтеграції.

Слід дотримуватися таких рекомендацій:
* **Пара інструкція-відповідь:** Зосередьтеся на наборах даних, що містять пару `instruction-response`. Ця структура є обов'язковою для передбаченої функціональності.
* **Зміна власних ключів:** Якщо ваш набір даних не відповідає структурі `instruction-response`, ви можете змінити функцію `format_instruction()`. Це дозволяє враховувати специфічні ключі за потреби.

Приклад коригування: у випадках, коли вихідні дані набору потребують коригування, ви можете змінити розділ відповіді у функції format_instruction() відповідно до ваших вимог.
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

Щоб скрипт міг працювати з файлом у форматі CSV, необхідно переконатися, що файл CSV містить стовпці з назвами `instruction` та `response`.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Налаштування параметрів навчання

Відредагуйте скрипт навчання та змініть змінні відповідно до ваших цілей: **швидкість навчання** (`LR`), **кількість епох** (`EPOCHS`), **розмір пакету** (`BATCH_SIZE`), **накопичення градієнтів** (`GRAD_ACCUM_STEPS`), а для LoRA/QLoRA — **ранг** (`LORA_R`). Для швидших запусків використовуйте менше епох і вищу швидкість навчання (LR); для кращої якості — більше епох і нижчу LR. Зменшіть розмір пакету або довжину послідовності, якщо виникають помилки нестачі пам'яті.

### Поради щодо оптимізації пам'яті

Якщо ви стикаєтеся з помилками нестачі пам'яті:

**1. Зменшіть розмір пакету:**
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

**4. Увімкніть контрольні точки градієнтів (лише для повного тонкого налаштування):**
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

Щоб записувати запуски та метрики до [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

У скрипті навчання встановіть `report_to="wandb"` та за бажанням `run_name="your-experiment-name"` у конфігурації тренера. Якщо ви не хочете використовувати Wandb, залиште `report_to` за замовчуванням або встановіть значення `"none"`.

### Типові проблеми

#### Нестача пам'яті (OOM)

**Рішення:** Зменшіть розмір пакету та/або використовуйте QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Втрата не зменшується

**Рішення:** Налаштуйте швидкість навчання
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Повільне навчання

**Рішення:** Збільшіть розмір пакету, якщо дозволяє пам'ять
```python
BATCH_SIZE = 8
```
## Наступні кроки

Після успішного завершення тонкого налаштування розгляньте такі наступні кроки, щоб отримати більше від вашої моделі:

1. **Оцініть** ретельно на відкладених тестових даних для вимірювання узагальнення та уникнення перенавчання.
2. **Експериментуйте**, пробуючи різні значення гіперпараметрів для кращих компромісів між точністю, швидкістю та пам'яттю.
3. **Відстежуйте** всі свої експерименти (та відповідні метрики) за допомогою Weights & Biases для відтворюваних досліджень.
4. **Спробуйте** навчання на власних наборах даних, щоб адаптувати модель спеціально для вашого випадку використання.
5. **Розгорніть** вашу налаштовану модель для швидкого виведення за допомогою ефективних бекендів, таких як vLLM, на сумісному апаратному забезпеченні.
6. **Досліджуйте** передові техніки, зокрема проектування підказок, змішану точність і довші послідовності.
7. **Навчайте** кілька адаптерів LoRA для різних завдань або доменів і перемикайте їх за потреби.

---