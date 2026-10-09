<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

Это руководство показывает, как выполнить тонкую настройку (fine-tuning) языковой модели локально с помощью Unsloth на оборудовании AMD.

В нем используется короткий пример контролируемой тонкой настройки (Supervised Fine-Tuning, SFT) с адаптерами LoRA на `unsloth/gemma-4-E4B-it`, с использованием подмножества набора данных `mlabonne/FineTome-100k`. Цель — показать простой сквозной рабочий процесс, охватывающий настройку, обучение, вывод и сохранение результата тонкой настройки.

Пример разработан так, чтобы быть практичным и легко модифицируемым, поэтому вы можете использовать его как отправную точку для собственных наборов данных и моделей.

## Чему вы научитесь

- Как настроить окружение Unsloth
- Как выполнить тонкую настройку LLM с помощью SFT и Unsloth
- Как сохранить результат тонкой настройки локально

<!-- @device:halo,stx,krk -->
> **Примечание:** Техники тонкой настройки, описанные в этом руководстве, требуют как минимум **64 ГБ системной оперативной памяти**, при этом как минимум **24 ГБ из них должны быть доступны GPU** (эти 24 ГБ являются частью 64 ГБ, а не дополнением к ним).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примечание:** Техники тонкой настройки, описанные в этом руководстве, требуют как минимум **24 ГБ общей памяти GPU** и **32 ГБ системной оперативной памяти**.
> - В Windows общая память GPU объединяет выделенную видеопамять (VRAM) видеокарты с разделяемой памятью GPU (заимствованной из системной оперативной памяти).
> - Поэтому видеокарты с менее чем 24 ГБ выделенной VRAM все равно могут выполнять это руководство, используя разделяемую память GPU для восполнения разницы.
<!-- @os:end -->

<!-- @os:linux -->
> **Примечание:** Техники тонкой настройки, описанные в этом руководстве, требуют видеокарту как минимум с **24 ГБ выделенной памяти GPU** и **32 ГБ системной оперативной памяти**.
> - В Linux обучение полностью выполняется в выделенной VRAM видеокарты.
> - Оно не переключается на разделяемую память GPU (системную оперативную память), когда VRAM заканчивается.
> - Видеокарты с менее чем 24 ГБ выделенной VRAM столкнутся с нехваткой памяти во время обучения в Linux, даже если в системе достаточно оперативной памяти.
<!-- @os:end -->
<!-- @device:end -->

## Почему Unsloth?

Unsloth упрощает запуск тонкой настройки LLM на локальном оборудовании, снижая потребление памяти и ускоряя обучение по сравнению со стандартной настройкой.

В этом руководстве мы используем Unsloth вместе с **SFT на основе LoRA**. Это означает, что базовая модель остается в основном замороженной, в то время как обучается гораздо меньший набор весов адаптеров. Это хорошо подходит для локальной разработки, поскольку этот подход легче, чем полная тонкая настройка, и позволяет быстрее итерировать.

Unsloth также поддерживает другие подходы к обучению, включая QLoRA и рабочие процессы обучения с подкреплением. Это руководство в первую очередь сосредоточено на самом простом пути: небольшом примере тонкой настройки LoRA, который пользователи могут запустить, понять и расширить.

<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения
> **Примечание**: Если VS Code не установлен, вы можете установить его с помощью Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Создание виртуального окружения

<!-- @os:linux -->
<!-- @device:halo_box -->
Откройте терминал и создайте venv с уже установленными AMD ROCm™ software и PyTorch:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Предоставьте вашему пользователю доступ к устройствам GPU** (чтобы изменения вступили в силу, выйдите из системы и войдите снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

Откройте терминал и создайте venv:
<!-- @test:id=create-venv timeout=300 -->
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
Откройте терминал PowerShell и создайте виртуальное окружение:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Откройте терминал PowerShell и создайте виртуальное окружение:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Установка базовых зависимостей
<!-- @require:driver -->

> **Важно:** Unsloth пока не поддерживает сборку PyTorch 2.13, которая поставляется с ROCm 10. Для этого руководства установите **ROCm 7.14 с PyTorch 2.12**, используя приведенные ниже команды. Не используйте пакеты ROCm 10 / PyTorch 2.13.

**Установите PyTorch с поддержкой AMD ROCm™ software** в созданном виртуальном окружении:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Для других устройств, пожалуйста, обратитесь к [документации ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) для получения полных инструкций.

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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Примечание:** Во время импорта Unsloth может проверять опциональные пути ускорения `bitsandbytes`. На некоторых версиях ROCm вы можете увидеть сообщение вида `bitsandbytes library load error: Configured ROCm binary not found`. В этом руководстве используется стандартная тонкая настройка LoRA с `optim="adamw_torch"`, поэтому мы не полагаемся на оптимизатор `bitsandbytes` или 4-битный QLoRA. Это сообщение можно безопасно игнорировать.

<!-- @os:windows -->
> **Примечание:** В Windows ROCm при запуске Unsloth выведет несколько предупреждений — см. [Known Warnings](#known-warnings) ниже. Все их можно безопасно игнорировать; обучение работает корректно.
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

## Скачивание скрипта тонкой настройки Unsloth

Вместо того чтобы выполнять каждый шаг вручную, в этом руководстве предоставляется чистый сквозной скрипт здесь: [test_unsloth.py](assets/test_unsloth.py).

Выполните следующий код, чтобы запустить скрипт:

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

Остальная часть руководства концептуально пройдет через каждый основной шаг скрипта.

## Как это работает

Скрипт test_unsloth.py выполняет следующие шаги:
* **Загрузка модели**: загружает unsloth/gemma-4-E4B-it с помощью FastModel.
* **Подготовка данных**: приводит набор данных (например, FineTome-100k) к стандартному виду и применяет шаблон чата Gemma-4.
* **Применение LoRA**: добавляет адаптеры к языковым, attention- и MLP-модулям для эффективного обучения.
* **Обучение**: использует SFTTrainer с маскированием потерь только для ответов (response-only loss masking).
* **Вывод**: запускает быстрый тест генерации для проверки производительности.
* **Сохранение**: экспортирует адаптеры LoRA локально.
## Key Configuration

Вы можете изменить следующие константы для настройки вашего запуска:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Пример приветственного сообщения Unsloth и вывода при загрузке весов модели:

![alt text](assets/welcome.png)

## Подготовка набора данных

Мы используем подмножество:
```text
mlabonne/FineTome-100k
```
Набор данных:
* Преобразован в формат чата
* Обработан с использованием шаблона чата Gemma-4
* Очищен от дублирующихся токенов BOS

## Обучение модели

Скрипт запускает короткую демонстрацию обучения со следующими параметрами:
- ~50 шагов
- Небольшой размер батча
- Накопление градиента

Во время обучения вы увидите логи, такие как:

![alt text](assets/training.png)


## Сохранение и развертывание

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
> **Примечание:** vLLM не поддерживает Windows. Чтобы развернуть вашу дообученную модель в Windows, используйте llama.cpp (см. раздел [Экспорт GGUF](#export-gguf-for-llamacpp) ниже) или перенесите объединённую модель на машину с Linux, на которой работает vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Для развертывания с помощью vLLM объедините адаптеры в полную модель:
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

Преобразуйте напрямую в GGUF для локального вывода:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Известные предупреждения

Эти предупреждения выводятся Unsloth при запуске в Windows ROCm, и все они безопасны и их можно игнорировать:

| Предупреждение | Причина | Можно игнорировать? |
|---|---|---|
| `bitsandbytes library load error` | у bitsandbytes нет сборки для Windows ROCm | Да — в этом руководстве используется `adamw_torch`, а не bnb |
| `No ROCm platform found for torch.distributed` | в ROCm для Windows отсутствует распределённое обучение | Да — это не влияет на обучение с одним GPU |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth помечает сборки, отличные от Linux | Да — Windows ROCm работает для SFT с одним GPU |
| `triton is not available` | у Triton нет сборки для Windows | Да — Unsloth переключается на ядра PyTorch |

Обучение будет проходить корректно, несмотря на эти предупреждения.
<!-- @os:end -->

## Дальнейшие шаги
- Попробуйте [Unsloth Studio](https://unsloth.ai/docs/new/studio) — интуитивно понятный графический интерфейс для Unsloth
- Обучите модель на собственных специфических наборах данных
- Попробуйте дообучение с другими гиперпараметрами
- Разверните модель с помощью vLLM или llama.cpp
- Попробуйте QLoRA для настройки с меньшим потреблением памяти

## Ресурсы

Ниже приведены дополнительные ресурсы, чтобы узнать больше об Unsloth и дообучении:

* [Документация Unsloth](https://docs.unsloth.ai)

* [Unsloth на GitHub](https://github.com/unslothai/unsloth)

* [Руководство по дообучению Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)