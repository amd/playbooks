<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

Это руководство содержит пошаговые примеры тонкой настройки большой языковой модели (LLM) с помощью PyTorch и ROCm. В нём рассматриваются несколько техник — от стандартной тонкой настройки до памятеэффективных стратегий Parameter-Efficient Fine-Tuning (PEFT), — что позволяет легко адаптировать модели под ваши задачи.

**Используемая модель**: google/gemma-3-4b-it  *(см. [Включение аутентификации HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), если модель закрытая)*  
**Оборудование**: AMD Radeon™ GPU с поддержкой ROCm  
**Фреймворк**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Примечание:** Вы также можете попробовать другие архитектуры моделей, включая **GPT-OSS-20B**, подставив нужную модель в предоставленные скрипты обучения.
> Полная тонкая настройка требует не менее 32 ГБ видеопамяти GPU и 64 ГБ оперативной памяти.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Примечание:** Тонкая настройка LoRA и QLoRA требует не менее 16 ГБ видеопамяти GPU и 32 ГБ оперативной памяти.
<!-- @device:end -->

## Чему вы научитесь

- Как выполнять тонкую настройку LLM с использованием LoRA, QLoRA и полной тонкой настройки с помощью PyTorch и ROCm
- Как сохранять и развёртывать модель после тонкой настройки
- Как отслеживать процесс обучения и устранять распространённые проблемы

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения
> **Примечание**: Если VS Code не установлен, его можно установить через Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимых программных компонентов

#### Создание виртуальной среды

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
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления в силу необходимо выйти из системы и войти снова):

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

#### Установка базовых зависимостей
<!-- @require:pytorch -->

#### Дополнительные зависимости

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Здесь протестированы и поддерживаются только основные пакеты. **bitsandbytes плохо поддерживается в Windows**, поэтому установка для Windows его не включает; используйте LoRA или полную тонкую настройку в Windows (QLoRA требует bitsandbytes и предназначена для Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Включение аутентификации HF (закрытые или пользовательские / не предустановленные модели)

В этом примере используется **google/gemma-3-4b-it** — **закрытая** модель. Вы должны принять условия использования модели на Hugging Face, а затем пройти аутентификацию, чтобы скрипты обучения могли её загрузить.

1. **Примите лицензию:** Откройте [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), войдите в систему (или создайте аккаунт) и примите лицензию/условия на странице модели (например, «Agree and access repository»).
2. **Установите и войдите:** Установите Hugging Face CLI, затем выполните стандартный вход:

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

## Понимание техник

### Что такое LoRA?

**LoRA (Low-Rank Adaptation)** сохраняет базовую модель замороженной и обучает только небольшие «адаптерные» матрицы, добавляемые к определённым слоям.

- **Ключевая идея**: вместо обновления огромной матрицы весов с миллионами параметров мы обучаем низкоранговое обновление (две небольшие матрицы, произведение которых содержит значительно меньше параметров). Это даёт существенное сокращение обучаемых параметров и потребления видеопамяти при сохранении большей части качества полной тонкой настройки.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Что такое QLoRA?

**QLoRA** сочетает **4-битное квантование** с **LoRA**. Базовая модель загружается в 4-битном формате (значительная экономия памяти), а обучаются только адаптеры LoRA в более высокой точности. Таким образом достигается параметрическая эффективность LoRA при значительно меньшем потреблении видеопамяти, с небольшим компромиссом по качеству по сравнению с LoRA в полной точности. Обратите внимание, что 4-битное квантование может вызывать численную нестабильность (скачки потерь или NaN), поэтому пользователи нередко предпочитают **LoRA**, если видеопамяти достаточно.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Примечание**: Для базовых моделей MXFP4, таких как `openai/gpt-oss-20b`, рекомендуется использовать **LoRA** (`train_lora.py`) вместо QLoRA. Путь `bitsandbytes` с 4-битным квантованием в скрипте QLoRA обычно деквантует веса MXFP4 до BF16, поэтому запуск ведёт себя как стандартная LoRA. Нативный MXFP4 требует `bitsandbytes`, собранного из исходников, а также совместимого стека Transformers/Triton/ядер. См. [документацию Transformers по MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Выберите метод

| Метод | Память | Скорость | Качество | Лучше всего подходит для |
|--------|--------|-------|---------|----------|
| **QLoRA** (только Linux) | 12–16 ГБ | Самый быстрый | 90–95% | Минимальное использование памяти |
| **LoRA** | 24–32 ГБ | Быстрый | 95–98% | Сбалансированный подход |
| **Полная** | 80+ ГБ | Самый медленный | 100% | Максимальное качество |

### 3. Запустите обучение

**Датасет и чему учится модель**  
Скрипты преобразуют датасет в примеры диалогов. Например, скрипт QLoRA использует **Abirate/english_quotes**: каждый пример становится парой пользователь–ассистент вида:

- **Пользователь:** «Give me a quote about: &lt;tag&gt;»
- **Ассистент:** «&lt;quote&gt; – &lt;author&gt;»

Тонкая настройка учит модель отвечать на запросы о цитатах по теме и возвращать их в формате `<текст цитаты> - <автор>`. Скрипты LoRA и полной тонкой настройки используют **databricks/databricks-dolly-15k** (общие пары инструкция/ответ), поэтому конкретная задача варьируется в зависимости от скрипта; идея та же — адаптировать модель к выбранному датасету и формату.

Ниже приведена сводка доступных методов обучения. Каждый метод ссылается на соответствующий скрипт и содержит краткое описание для выбора подходящего подхода.

| Скрипт | Метод | Описание | Типичная видеопамять | Рекомендуется для |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | Обучает небольшие адаптерные матрицы при замороженной базовой модели. В 3–5 раз быстрее; ~95–98% полного качества. | 24–32 ГБ | Опытные пользователи; несколько адаптеров; больше видеопамяти |
| [`train_qlora.py`](assets/train_qlora.py) *(только Linux)* | **QLoRA** | 4-битное квантование + адаптеры LoRA. Минимальное потребление памяти, самый быстрый, небольшой компромисс по качеству. Требует `bitsandbytes` (только Linux). | 12–16 ГБ | Большинство пользователей; быстрые эксперименты; ограниченная видеопамять |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Полная тонкая настройка** | Обновляет все параметры модели. Максимальное качество; наибольшее потребление памяти и вычислительных ресурсов. | 40+ ГБ | Максимальное качество; исследования; большая видеопамять |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примечание:** Полная тонкая настройка (`train_full_finetuning.py`) может потребовать более 64 ГБ оперативной памяти и может оказаться невозможной на данном устройстве. Рассмотрите использование LoRA или QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание:** Полная тонкая настройка (`train_full_finetuning.py`) может потребовать более 64 ГБ оперативной памяти и может оказаться невозможной на данном устройстве. Рассмотрите использование LoRA.
<!-- @os:end -->
<!-- @device:end -->

Просто выберите предпочтительный `Метод обучения`, скачайте соответствующий скрипт и выполните его с помощью команды, сохраняя активированную виртуальную среду:

```python
python3 train_<method_name>.py.
```

## Использование модели после тонкой настройки

### После полной тонкой настройки

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

### После обучения LoRA/QLoRA

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

### Объединение адаптера LoRA с базовой моделью

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Примечание:**  
- Убедитесь, что имя директории модели (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) совпадает с фактической выходной папкой из обучения.  
- Если вы использовали LoRA вместо QLoRA, просто подставьте соответствующий путь.  
- Некоторые модели Gemma требуют указания `trust_remote_code=True` в `from_pretrained`; добавьте, если увидите соответствующее предупреждение.

Для более тонкой настройки (токены заполнения, устройство и т. д.) обратитесь к скрипту, который вы использовали для обучения.

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

## Руководство по настройке

### Использование собственного датасета

Все скрипты используют одинаковый формат датасета. Замените раздел загрузки:

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

**Формат датасета для локального файла JSON/JSONL:**

При использовании этого метода убедитесь, что ваши JSON-файлы имеют правильную структуру во избежание ошибок разбора.

Необходимо соблюдать следующие требования:
* **Форматирование файла:** JSON-файлы должны быть отформатированы в интегрированной среде разработки (IDE) для обеспечения правильной структуры и синтаксиса.
* **Обязательные ключи:** Пользовательский JSON-файл должен содержать ключи `instruction` и `response`. Эти ключи необходимы для корректной работы метода.
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
**Формат датасета для датасета из Hugging Face Hub**

При использовании датасетов из Hugging Face убедитесь, что они имеют правильную структуру для обеспечения бесшовной интеграции.

Следует придерживаться следующих рекомендаций:
* **Пара инструкция–ответ:** Ориентируйтесь на датасеты, содержащие пару `instruction-response`. Эта структура необходима для предполагаемой функциональности.
* **Изменение пользовательских ключей:** Если ваш датасет не соответствует структуре `instruction-response`, вы можете изменить функцию `format_instruction()`. Это позволяет использовать специфические ключи по мере необходимости.

Пример корректировки: в случаях, когда вывод датасета требует изменения, вы можете модифицировать раздел ответа внутри функции format_instruction() в соответствии с вашими требованиями.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Формат датасета для CSV-файла**

Для работы скрипта с CSV-файлом необходимо убедиться, что CSV-файл содержит столбцы с именами `instruction` и `response`.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Настройка параметров обучения

Отредактируйте скрипт обучения и измените переменные в соответствии с вашими целями: **скорость обучения** (`LR`), **количество эпох** (`EPOCHS`), **размер батча** (`BATCH_SIZE`), **накопление градиентов** (`GRAD_ACCUM_STEPS`), а для LoRA/QLoRA — **ранг** (`LORA_R`). Для более быстрого обучения используйте меньше эпох и более высокую скорость обучения (LR); для лучшего качества — больше эпох и меньшую LR. Уменьшите размер батча или длину последовательности при возникновении ошибок нехватки памяти.

### Советы по оптимизации памяти

Если вы сталкиваетесь с ошибками нехватки памяти:

**1. Уменьшите размер батча:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Уменьшите длину последовательности:**
```python
max_seq_length=256  # Instead of 512
```

**3. Используйте более агрессивное квантование:**
```
Full → LoRA → QLoRA
```

**4. Включите контрольные точки градиента (только для полной тонкой настройки):**
```python
model.gradient_checkpointing_enable()
```

---

## Мониторинг и отладка

### Наблюдение за видеопамятью GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Необязательно) Отслеживание экспериментов с Weights & Biases

Для записи запусков и метрик в [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

В скрипте обучения установите `report_to="wandb"` и при желании `run_name="your-experiment-name"` в конфигурации тренера. Если вы предпочитаете не использовать Wandb, оставьте `report_to` по умолчанию или установите значение `"none"`.

### Распространённые проблемы

#### Нехватка памяти (OOM)

**Решение:** Уменьшите размер батча и/или используйте QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Потери не уменьшаются

**Решение:** Скорректируйте скорость обучения
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Медленное обучение

**Решение:** Увеличьте размер батча, если позволяет память
```python
BATCH_SIZE = 8
```
## Следующие шаги

После успешного завершения тонкой настройки рассмотрите следующие шаги для получения максимальной отдачи от вашей модели:

1. **Оцените** результаты на отложенных тестовых данных для измерения обобщающей способности и предотвращения переобучения.
2. **Экспериментируйте**, пробуя различные значения гиперпараметров для достижения лучшего баланса точности, скорости и потребления памяти.
3. **Отслеживайте** все свои эксперименты (и соответствующие метрики) с помощью Weights & Biases для воспроизводимых исследований.
4. **Попробуйте** обучение на собственных пользовательских датасетах для адаптации модели под конкретный сценарий использования.
5. **Развёртывайте** вашу модель после тонкой настройки для быстрого инференса с использованием эффективных бэкендов, таких как vLLM, на совместимом оборудовании.
6. **Изучайте** продвинутые техники, включая инжиниринг промптов, смешанную точность и более длинные последовательности.
7. **Обучайте** несколько адаптеров LoRA для различных задач или доменов и переключайтесь между ними по мере необходимости.

---