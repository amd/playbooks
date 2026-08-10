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

Цей посібник показує, як локально донавчити мовну модель за допомогою Unsloth на обладнанні AMD.

Він використовує короткий приклад контрольованого донавчання (Supervised Fine-Tuning, SFT) з адаптерами LoRA на `unsloth/gemma-4-E4B-it`, використовуючи підмножину набору даних `mlabonne/FineTome-100k`. Мета — надати простий наскрізний робочий процес, що охоплює налаштування, навчання, інференс і збереження донавченого результату.

Цей приклад створено практичним і легким для модифікації, тож ви можете використовувати його як відправну точку для власних наборів даних і моделей.

## Що ви дізнаєтеся

- Як налаштувати середовище Unsloth
- Як донавчити LLM за допомогою SFT з Unsloth
- Як зберегти донавчений результат у локальному сховищі

<!-- @device:halo,stx,krk -->
> **Примітка:** Методи донавчання в цьому посібнику вимагають щонайменше **64 ГБ оперативної пам'яті системи**, з яких щонайменше **24 ГБ доступно для GPU** (ці 24 ГБ є частиною 64 ГБ, а не додатковими до них).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примітка:** Методи донавчання в цьому посібнику вимагають щонайменше **24 ГБ загальної пам'яті GPU** та **32 ГБ оперативної пам'яті системи**.
> - У Windows загальна пам'ять GPU поєднує виділену відеопам'ять (VRAM) відеокарти зі спільною пам'яттю GPU (запозиченою з оперативної пам'яті системи).
> - Тому відеокарти з менш ніж 24 ГБ виділеної VRAM все ще можуть виконувати цей посібник, використовуючи спільну пам'ять GPU для компенсації різниці.
<!-- @os:end -->

<!-- @os:linux -->
> **Примітка:** Методи донавчання в цьому посібнику вимагають відеокарту з щонайменше **24 ГБ виділеної пам'яті GPU** та **32 ГБ оперативної пам'яті системи**.
> - У Linux навчання виконується повністю у виділеній VRAM відеокарти.
> - Воно не переходить на спільну пам'ять GPU (оперативну пам'ять системи), коли VRAM вичерпується.
> - Відеокарти з менш ніж 24 ГБ виділеної VRAM вичерпають пам'ять під час навчання в Linux, навіть якщо в системі достатньо оперативної пам'яті.
<!-- @os:end -->
<!-- @device:end -->

## Чому Unsloth?

Unsloth спрощує виконання донавчання LLM на локальному обладнанні, зменшуючи використання пам'яті та прискорюючи навчання порівняно зі стандартним налаштуванням.

У цьому посібнику ми використовуємо Unsloth разом з **SFT на основі LoRA**. Це означає, що базова модель залишається переважно замороженою, тоді як навчається значно менший набір ваг адаптера. Це добре підходить для локальної розробки, оскільки є легшим за повне донавчання та швидшим для ітерацій.

Unsloth також підтримує інші підходи до навчання, включно з QLoRA та робочими процесами навчання з підкріпленням. Цей посібник спочатку зосереджується на найпростішому шляху: невеликому прикладі донавчання LoRA, який користувачі можуть запустити, зрозуміти та розширити.

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

### Створення віртуального середовища

<!-- @os:linux -->
<!-- @device:halo_box -->
Відкрийте термінал і створіть venv з уже встановленими AMD ROCm™ software та PyTorch:
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
**Надайте своєму користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

```bash
sudo usermod -aG render,video $LOGNAME
```

Відкрийте термінал і створіть venv:
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
> **Примітка:** Для Windows потрібен Python 3.13.

<!-- @device:halo_box -->
Відкрийте термінал PowerShell і створіть віртуальне середовище:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Відкрийте термінал PowerShell і створіть віртуальне середовище:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Встановлення базових залежностей
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

### Додаткові залежності

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Примітка:** Під час імпорту Unsloth може перевіряти додаткові шляхи прискорення `bitsandbytes`. У деяких версіях ROCm ви можете побачити повідомлення на кшталт `bitsandbytes library load error: Configured ROCm binary not found`. Цей посібник використовує стандартне донавчання LoRA з `optim="adamw_torch"`, тому ми не покладаємося на оптимізатор `bitsandbytes` чи 4-бітну QLoRA. Це повідомлення можна безпечно ігнорувати.

<!-- @os:windows -->
> **Примітка:** У Windows ROCm Unsloth виведе кілька попереджень під час запуску — див. [Відомі попередження](#known-warnings) нижче. Усі вони безпечні для ігнорування; навчання працює коректно.
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

## Завантаження скрипту донавчання Unsloth

Замість того щоб виконувати кожен крок вручну, цей посібник надає чистий, наскрізний скрипт тут: [test_unsloth.py](assets/test_unsloth.py).

Запустіть наступний код для виконання скрипту:

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

Решта посібника концептуально пройде через кожен основний крок скрипту.

## Як це працює

Скрипт test_unsloth.py виконує наступні кроки:
* **Завантаження моделі**: Завантажує unsloth/gemma-4-E4B-it за допомогою FastModel.
* **Підготовка даних**: Стандартизує набір даних (наприклад, FineTome-100k) і застосовує шаблон чату Gemma-4.
* **Застосування LoRA**: Додає адаптери до модулів мови, уваги та MLP для ефективного навчання.
* **Навчання**: Використовує SFTTrainer з маскуванням втрат лише для відповідей.
* **Інференс**: Виконує швидкий тест генерації для перевірки продуктивності.
* **Збереження**: Експортує адаптери LoRA локально.

## Ключова конфігурація

Ви можете змінити наступні константи, щоб налаштувати свій запуск:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Приклад вітального повідомлення Unsloth та виведення під час завантаження ваг моделі:

![alt text](assets/welcome.png)

## Підготовка набору даних

Ми використовуємо підмножину:
```text
mlabonne/FineTome-100k
```
Набір даних:
* Перетворено у формат чату
* Оброблено за допомогою шаблону чату Gemma-4
* Очищено від дублікатів токенів BOS

## Навчання моделі

Скрипт виконує коротку демонстрацію навчання з наступними параметрами:
- ~50 кроків
- Малий розмір пакета (batch size)
- Накопичення градієнта

Під час навчання ви побачите такі журнали:

![alt text](assets/training.png)


## Збереження та розгортання
### Локальне збереження (LoRA)

Скрипт автоматично зберігає адаптери LoRA до OUTPUT_DIR.
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

### Збереження об'єднаної моделі (для vLLM) 

<!-- @os:windows -->
> **Примітка:** vLLM не підтримує Windows. Щоб розгорнути вашу дообучену модель на Windows, використовуйте llama.cpp (див. [Експорт GGUF](#export-gguf-for-llamacpp) нижче) або перенесіть об'єднану модель на машину з Linux, на якій запущено vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Для розгортання з vLLM об'єднайте адаптери в повну модель:
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

### Експорт GGUF (для llama.cpp)

Конвертуйте безпосередньо у GGUF для локального інференсу:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Відомі попередження

Ці попередження виводяться Unsloth під час запуску на Windows ROCm, і всі вони безпечні для ігнорування:

| Попередження | Причина | Безпечно ігнорувати? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes не має збірки для Windows ROCm | Так — цей посібник використовує `adamw_torch`, а не bnb |
| `No ROCm platform found for torch.distributed` | ROCm на Windows не підтримує розподілене навчання | Так — навчання на одному GPU не постраждає |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth позначає збірки, відмінні від Linux | Так — Windows ROCm працює для SFT на одному GPU |
| `triton is not available` | Triton не має збірки для Windows | Так — Unsloth використовує резервні ядра PyTorch |

Навчання пройде коректно, незважаючи на ці попередження.
<!-- @os:end -->

## Наступні кроки
- Спробуйте [Unsloth Studio](https://unsloth.ai/docs/new/studio) — інтуїтивно зрозумілий графічний інтерфейс для Unsloth
- Навчайте на власних специфічних наборах даних
- Спробуйте дообучення з різними гіперпараметрами
- Розгортайте за допомогою vLLM або llama.cpp
- Спробуйте QLoRA для налаштування з меншим використанням пам'яті

## Ресурси

Нижче наведено додаткові ресурси для більш детального ознайомлення з Unsloth та дообученням:

* [Документація Unsloth](https://docs.unsloth.ai)

* [Unsloth на GitHub](https://github.com/unslothai/unsloth)

* [Посібник з дообучення Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)