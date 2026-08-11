<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

В этом руководстве представлены пошаговые примеры тонкой настройки большой языковой модели (LLM) с использованием PyTorch и ROCm. Оно охватывает несколько методов — от стандартной тонкой настройки до экономичных по памяти стратегий Parameter-Efficient Fine-Tuning (PEFT), — позволяя легко адаптировать модели под ваши задачи.

**Используемая модель**: google/gemma-3-4b-it  *(см. раздел [Включение аутентификации HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), если модель закрытая)*  
**Оборудование**: AMD Radeon™ GPU с поддержкой ROCm  
**Фреймворк**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Примечание:** 
> - Полная тонкая настройка требует не менее **64 ГБ системной оперативной памяти**, из которых не менее **32 ГБ должно быть доступно GPU** (эти 32 ГБ являются частью 64 ГБ, а не дополнением к ним).
> - Вы также можете попробовать другие архитектуры моделей, включая **GPT-OSS-20B**, заменив модель в предоставленных скриптах обучения.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Примечание:** Тонкая настройка LoRA и QLoRA требует не менее **32 ГБ системной оперативной памяти**, из которых не менее **16 ГБ должно быть доступно GPU** (эти 16 ГБ являются частью 32 ГБ, а не дополнением к ним).
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание:** Тонкая настройка LoRA требует не менее **32 ГБ системной оперативной памяти**, из которых не менее **16 ГБ должно быть доступно GPU** (эти 16 ГБ являются частью 32 ГБ, а не дополнением к ним).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примечание:** Тонкая настройка LoRA и QLoRA требует видеокарты с не менее чем **16 ГБ выделенной памяти GPU** и **32 ГБ системной оперативной памяти**.
> - В Linux обучение полностью выполняется в выделенной видеопамяти (VRAM) видеокарты.
> - При исчерпании VRAM переключение на общую память GPU (системную оперативную память) не происходит.
> - На видеокартах с менее чем 16 ГБ выделенной VRAM во время обучения в Linux память будет исчерпана, даже если в системе достаточно оперативной памяти.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание:** Тонкая настройка LoRA требует не менее **16 ГБ общей памяти GPU** и **32 ГБ системной оперативной памяти**.
> - В Windows общая память GPU объединяет выделенную VRAM видеокарты с общей памятью GPU (заимствованной из системной оперативной памяти).
> - Поэтому видеокарты с менее чем 16 ГБ выделенной VRAM всё же могут использоваться для этого сборника инструкций за счёт использования общей памяти GPU для компенсации разницы.
<!-- @os:end -->
<!-- @device:end -->

## Что вы узнаете

- Как выполнить тонкую настройку LLM с использованием LoRA, QLoRA и полной тонкой настройки с PyTorch и ROCm
- Как сохранить и развернуть настроенную модель
- Как отслеживать процесс обучения и устранять типичные проблемы

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения
> **Примечание**: Если VS Code не установлен, вы можете установить его через Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

#### Создание виртуального окружения

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
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления изменений в силу выйдите из системы и войдите снова):

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
**Windows:** Здесь тестируются и поддерживаются только основные пакеты. **bitsandbytes не имеет хорошей поддержки в Windows**, поэтому установка для Windows не включает его; используйте LoRA или полную тонкую настройку в Windows (QLoRA требует bitsandbytes и предназначена для Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Включение аутентификации HF (закрытые или пользовательские / предустановленные модели)

В этом примере мы используем **google/gemma-3-4b-it**, которая является **закрытой** моделью. Вам необходимо принять условия использования модели на Hugging Face, а затем пройти аутентификацию, чтобы скрипты обучения могли её загрузить.

1. **Примите лицензию:** Откройте [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), войдите в систему (или создайте учётную запись) и примите лицензию/условия использования на странице модели (например, «Agree and access repository»).
2. **Установите CLI и войдите в систему:** Установите Hugging Face CLI, затем выполните стандартный вход:

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

## Понимание методов

### Что такое LoRA?

**LoRA (Low-Rank Adaptation)** оставляет базовую модель замороженной и обучает только небольшие матрицы «адаптеров», которые добавляются к определённым слоям.

- **Ключевая идея**: вместо обновления огромной весовой матрицы с миллионами параметров мы обучаем обновление низкого ранга (две небольшие матрицы, произведение которых имеет значительно меньше параметров). Это даёт значительное сокращение количества обучаемых параметров и объёма VRAM при сохранении большей части качества полной тонкой настройки.

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

**QLoRA** объединяет **4-битное квантование** с **LoRA**. Базовая модель загружается в 4-битном формате (значительная экономия памяти), а обучаются только адаптеры LoRA — с более высокой точностью. Таким образом, вы получаете эффективность по параметрам LoRA плюс значительно меньший расход VRAM, с небольшим компромиссом по качеству по сравнению с LoRA с полной точностью. Обратите внимание, что 4-битное квантование может приводить к численной нестабильности (скачки функции потерь или NaN), поэтому пользователи часто предпочитают **LoRA**, если доступно достаточно VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Примечание**: Для базовых моделей MXFP4, таких как `openai/gpt-oss-20b`, мы рекомендуем использовать **LoRA** (`train_lora.py`) вместо QLoRA. 4-битный путь `bitsandbytes` в скрипте QLoRA обычно деквантует веса MXFP4 в BF16, поэтому запуск ведёт себя как обычная LoRA. Для нативной поддержки MXFP4 требуется `bitsandbytes`, собранная из исходников, а также соответствующий стек Transformers/Triton/kernels. См. [документацию Transformers по MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Выберите метод

| Метод | Память | Скорость | Качество | Лучше всего подходит для |
|--------|--------|-------|---------|----------|
| **QLoRA** (только для Linux) | 12-16GB | Самая высокая | 90-95% | Низкого потребления памяти |
| **LoRA** | 24-32GB | Высокая | 95-98% | Сбалансированного подхода |
| **Full** | 80GB+ | Самая низкая | 100% | Максимального качества |

### 3. Запуск обучения

**Набор данных и что изучает модель**  
Скрипты преобразуют набор данных в примеры чата. Например, скрипт QLoRA использует **Abirate/english_quotes**: каждый пример превращается в пару «пользователь-ассистент», например:

- **Пользователь:** «Give me a quote about: &lt;tag&gt;»
- **Ассистент:** «&lt;quote&gt; – &lt;author&gt;»

Дообучение учит модель отвечать на запросы с просьбой привести цитату на определённую тему и возвращать их в формате `<quote text> - <author>`. Скрипты LoRA и полного дообучения используют **databricks/databricks-dolly-15k** (общие пары инструкция/ответ), поэтому точная задача варьируется в зависимости от скрипта; идея одна и та же — адаптировать модель под выбранный вами набор данных и формат.

Ниже приведена сводка доступных методов обучения. Каждый метод содержит ссылку на свой скрипт и краткое описание для выбора правильного подхода.

| Скрипт                           | Метод            | Описание                                                                                                         | Типичный объём VRAM | Рекомендуется для                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Обучает небольшие матрицы адаптеров, замораживая базовую модель. В 3–5 раз быстрее; ~95–98% полного качества.                         | 24–32GB      | Продвинутых пользователей; несколько адаптеров; больше VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(только для Linux)*             | **QLoRA**       | 4-битное квантование + адаптеры LoRA. Наименьшее потребление памяти, самая высокая скорость, небольшой компромисс по качеству. Требует `bitsandbytes` (только для Linux).                            | 12–16GB      | Большинства пользователей; быстрых экспериментов; ограниченного VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Полное дообучение** | Обновляет все параметры модели. Максимальное качество; наибольшее потребление памяти и вычислительных ресурсов.                                    | 40GB+        | Максимального качества; исследований; большого объёма VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Примечание:** Полное дообучение (`train_full_finetuning.py`) может потребовать более 64 ГБ системной ОЗУ и может быть неосуществимо на данном устройстве. Рассмотрите возможность использования LoRA или QLoRA вместо него.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание:** Полное дообучение (`train_full_finetuning.py`) может потребовать более 64 ГБ системной ОЗУ и может быть неосуществимо на данном устройстве. Рассмотрите возможность использования LoRA вместо него.
<!-- @os:end -->
<!-- @device:end -->

Просто выберите предпочитаемый `Training method`, скачайте соответствующий скрипт и выполните его с помощью команды, сохраняя активированным виртуальное окружение: 

```python
python3 train_<method_name>.py.
```

## Использование вашей дообученной модели

### После полного дообучения

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
- Убедитесь, что имя каталога модели (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) совпадает с фактическим выходным каталогом, полученным при обучении.  
- Если вы использовали LoRA вместо QLoRA, просто замените путь соответствующим образом.  
- Некоторые модели Gemma требуют указания `trust_remote_code=True` в `from_pretrained`; добавьте это, если увидите соответствующее предупреждение.

Для дополнительных пользовательских настроек (токены дополнения, устройство и т.д.) обратитесь к скрипту, который вы использовали для обучения.

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

### Используйте собственный набор данных

Все скрипты используют один и тот же формат набора данных. Замените раздел загрузки:

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

**Формат набора данных для локального файла JSON/JSONL:**

При использовании этого метода убедитесь, что ваши файлы JSON правильно структурированы во избежание ошибок разбора. 

Необходимо соблюдать следующие рекомендации:
* **Форматирование файла:** файлы JSON должны быть отформатированы в интегрированной среде разработки (IDE) для обеспечения правильной структуры и синтаксиса.
* **Обязательные ключи:** пользовательский файл JSON должен содержать ключи `instruction` и `response`. Эти ключи необходимы для корректной работы метода.
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
**Формат набора данных для набора данных Hugging Face Hub**

При использовании наборов данных из Hugging Face убедитесь, что ваши наборы данных структурированы правильно для беспрепятственной интеграции. 

Следует придерживаться следующих рекомендаций:
* **Пара инструкция-ответ:** сосредоточьтесь на наборах данных, которые содержат пару `instruction-response`. Эта структура необходима для правильной работы функциональности.
* **Изменение пользовательских ключей:** если ваш набор данных не соответствует структуре `instruction-response`, у вас есть возможность изменить функцию `format_instruction()`. Это позволяет вам учитывать нужные ключи по мере необходимости.

Пример корректировки: в случаях, когда выходные данные набора данных необходимо скорректировать, вы можете изменить раздел ответа в функции format_instruction(), чтобы он соответствовал вашим требованиям.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Формат набора данных для файла CSV**

Чтобы адаптировать скрипт для использования формата файла CSV, необходимо убедиться, что файл CSV содержит столбцы с именами `instruction` и `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Настройка параметров обучения

Отредактируйте скрипт обучения и измените переменные в соответствии с вашими целями: **скорость обучения** (`LR`), **количество эпох** (`EPOCHS`), **размер батча** (`BATCH_SIZE`), **накопление градиента** (`GRAD_ACCUM_STEPS`), а для LoRA/QLoRA — **ранг** (`LORA_R`). Для более быстрого выполнения используйте меньше эпох и более высокую скорость обучения (LR); для лучшего качества используйте больше эпох и более низкую LR. Уменьшите размер батча или длину последовательности, если возникают ошибки нехватки памяти.
### Советы по оптимизации памяти

Если вы столкнулись с ошибками нехватки памяти:

**1. Уменьшите размер батча:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Уменьшите длину последовательности:**
```python
max_seq_length=256  # Instead of 512
```

**3. Используйте более агрессивную квантизацию:**
```
Full → LoRA → QLoRA
```

**4. Включите Gradient Checkpointing (только для полного дообучения):**
```python
model.gradient_checkpointing_enable()
```

---

## Мониторинг и отладка

### Отслеживание использования памяти GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Необязательно) Отслеживание экспериментов с помощью Weights & Biases

Чтобы логировать запуски и метрики в [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

В скрипте обучения установите `report_to="wandb"` и, при желании, `run_name="your-experiment-name"` в конфигурации trainer. Если вы предпочитаете не использовать Wandb, оставьте `report_to` со значением по умолчанию или установите `"none"`.

### Распространённые проблемы

#### Нехватка памяти (OOM)

**Решение:** уменьшите размер батча и/или используйте QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Функция потерь не уменьшается

**Решение:** скорректируйте скорость обучения
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Медленное обучение

**Решение:** увеличьте размер батча, если позволяет память
```python
BATCH_SIZE = 8
```
## Дальнейшие шаги

После успешного завершения дообучения рассмотрите следующие шаги, чтобы получить больше от вашей модели:

1. **Оцените** её тщательно на отложенных тестовых данных, чтобы измерить обобщающую способность и избежать переобучения.
2. **Экспериментируйте**, пробуя разные значения гиперпараметров для лучшего баланса точности, скорости и памяти.
3. **Отслеживайте** все свои эксперименты (и соответствующие метрики) с помощью Weights & Biases для воспроизводимости исследований.
4. **Попробуйте** обучение на собственных наборах данных, чтобы адаптировать модель именно под ваш сценарий использования.
5. **Разверните** дообученную модель для быстрого инференса с помощью эффективных бэкендов, таких как vLLM, на совместимом оборудовании.
6. **Изучите** продвинутые техники, включая prompt engineering, смешанную точность и увеличенную длину последовательности.
7. **Обучите** несколько LoRA-адаптеров для разных задач или доменов и переключайтесь между ними по мере необходимости.

---