<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

Этот playbook показывает, как выполнить тонкую настройку языковой модели локально с помощью Unsloth на оборудовании AMD.

В нём используется краткий пример обучения с учителем (SFT) с адаптерами LoRA на модели `unsloth/gemma-4-E4B-it` и подмножестве датасета `mlabonne/FineTome-100k`. Цель — предоставить простой сквозной рабочий процесс, охватывающий настройку, обучение, инференс и сохранение результата тонкой настройки.

Пример разработан так, чтобы быть практичным и легко модифицируемым, поэтому вы можете использовать его как отправную точку для собственных датасетов и моделей.

## Что вы узнаете

- Как настроить среду Unsloth
- Как выполнить тонкую настройку LLM с помощью SFT и Unsloth
- Как сохранить результат тонкой настройки в локальном хранилище

<!-- @device:halo,stx,krk -->
> **Примечание:** Методы тонкой настройки, описанные в этом playbook, требуют не менее 24 ГБ памяти GPU и 32 ГБ оперативной памяти.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примечание:** Методы тонкой настройки, описанные в этом playbook, требуют не менее 24 ГБ памяти GPU и 32 ГБ оперативной памяти.
<!-- @os:end -->

<!-- @os:linux -->
> **Примечание:** Методы тонкой настройки, описанные в этом playbook, требуют не менее 24 ГБ **выделенной** памяти GPU и 32 ГБ оперативной памяти.
<!-- @os:end -->
<!-- @device:end -->

## Почему Unsloth?

Unsloth упрощает тонкую настройку LLM на локальном оборудовании, снижая потребление памяти и ускоряя обучение по сравнению со стандартной конфигурацией.

В этом playbook мы используем Unsloth совместно с **SFT на основе LoRA**. Это означает, что базовая модель остаётся в основном замороженной, а обучается значительно меньший набор весов адаптера. Такой подход хорошо подходит для локальной разработки, поскольку он легче полной тонкой настройки и позволяет быстрее итерировать.

Unsloth также поддерживает другие подходы к обучению, включая QLoRA и рабочие процессы с обучением с подкреплением. Этот playbook сосредоточен на простейшем пути: небольшом примере тонкой настройки с LoRA, который пользователи могут запустить, понять и расширить.

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения
> **Примечание**: Если VS Code не установлен, его можно установить через Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимых программных компонентов

### Создание виртуальной среды

<!-- @os:linux -->
<!-- @device:halo_box -->
Откройте терминал и создайте venv с уже установленным программным обеспечением AMD ROCm™ и PyTorch:
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
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления в силу необходимо выйти из системы и войти снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

Откройте терминал и создайте venv:
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
> **Примечание:** Для Windows требуется Python 3.13.

<!-- @device:halo_box -->
Откройте терминал PowerShell и создайте виртуальную среду:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Откройте терминал PowerShell и создайте виртуальную среду:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Установка основных зависимостей
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

### Дополнительные зависимости

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

> **Примечание:** При импорте Unsloth может проверять дополнительные пути ускорения через `bitsandbytes`. На некоторых версиях ROCm вы можете увидеть сообщение вида `bitsandbytes library load error: Configured ROCm binary not found`. В этом playbook используется стандартная тонкая настройка LoRA с `optim="adamw_torch"`, поэтому мы не зависим от оптимизатора `bitsandbytes` или 4-битного QLoRA. Это сообщение можно безопасно игнорировать.

<!-- @os:windows -->
> **Примечание:** На Windows ROCm Unsloth выводит несколько предупреждений при запуске — см. раздел [Известные предупреждения](#known-warnings) ниже. Все они безопасны и могут быть проигнорированы; обучение работает корректно.
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

## Загрузка скрипта тонкой настройки Unsloth

Вместо ручного выполнения каждого шага этот playbook предоставляет готовый сквозной скрипт: [test_unsloth.py](assets/test_unsloth.py).

Выполните следующий код для запуска скрипта:

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

Далее в playbook концептуально рассматривается каждый основной шаг скрипта.

## Принцип работы

Скрипт test_unsloth.py выполняет следующие шаги:
* **Загрузка модели**: Загружает unsloth/gemma-4-E4B-it с помощью FastModel.
* **Подготовка данных**: Стандартизирует датасет (например, FineTome-100k) и применяет шаблон чата Gemma-4.
* **Применение LoRA**: Добавляет адаптеры к языковым, attention- и MLP-модулям для эффективного обучения.
* **Обучение**: Использует SFTTrainer с маскировкой потерь только на ответах.
* **Инференс**: Выполняет быстрый тест генерации для проверки производительности.
* **Сохранение**: Экспортирует адаптеры LoRA локально.

## Ключевая конфигурация

Вы можете изменить следующие константы для настройки запуска:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Пример приветственного сообщения Unsloth и вывода при загрузке весов модели:

![alt text](assets/welcome.png)

## Подготовка датасета

Мы используем подмножество:
```text
mlabonne/FineTome-100k
```
Датасет:
* Преобразован в формат чата
* Обработан с использованием шаблона чата Gemma-4
* Очищен от дублирующихся токенов BOS

## Обучение модели

Скрипт запускает краткую демонстрацию обучения со следующими параметрами:
- ~50 шагов
- Малый размер батча
- Накопление градиентов

В процессе обучения вы увидите логи следующего вида:

![alt text](assets/training.png)


## Сохранение и развёртывание

### Локальное сохранение (LoRA)

Скрипт автоматически сохраняет адаптеры LoRA в OUTPUT_DIR.
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

### Сохранение объединённой модели (для vLLM)

<!-- @os:windows -->
> **Примечание:** vLLM не поддерживает Windows. Для развёртывания тонко настроенной модели на Windows используйте llama.cpp (см. раздел [Экспорт GGUF](#export-gguf-for-llamacpp) ниже) или перенесите объединённую модель на машину с Linux, работающую под управлением vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Для развёртывания с vLLM объедините адаптеры с полной моделью:
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

### Экспорт GGUF (для llama.cpp)

Конвертируйте напрямую в GGUF для локального инференса:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Известные предупреждения

Эти предупреждения выводятся Unsloth при запуске на Windows ROCm и все безопасны для игнорирования:

| Предупреждение | Причина | Безопасно игнорировать? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes не имеет сборки для Windows ROCm | Да — в этом playbook используется `adamw_torch`, а не bnb |
| `No ROCm platform found for torch.distributed` | ROCm на Windows не поддерживает распределённое обучение | Да — обучение на одном GPU не затронуто |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth помечает сборки не на Linux | Да — Windows ROCm работает для SFT на одном GPU |
| `triton is not available` | Triton не имеет сборки для Windows | Да — Unsloth переключается на ядра PyTorch |

Обучение будет выполняться корректно, несмотря на эти предупреждения.
<!-- @os:end -->

## Следующие шаги
- Попробуйте [Unsloth Studio](https://unsloth.ai/docs/new/studio) — интуитивный графический интерфейс для Unsloth
- Обучайтесь на собственных специализированных датасетах
- Попробуйте тонкую настройку с различными гиперпараметрами
- Разверните с помощью vLLM или llama.cpp
- Попробуйте QLoRA для конфигурации с меньшим потреблением памяти

## Ресурсы

Ниже приведены дополнительные ресурсы для изучения Unsloth и тонкой настройки:

* [Документация Unsloth](https://docs.unsloth.ai)

* [Unsloth на GitHub](https://github.com/unslothai/unsloth)

* [Руководство по тонкой настройке Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)