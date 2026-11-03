<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

Цей плейбук показує, як локально дофайнтюнити мовну модель за допомогою Unsloth на апаратному забезпеченні AMD.

Він використовує короткий приклад Supervised Fine-Tuning (SFT) з адаптерами LoRA на `unsloth/gemma-4-E4B-it`, використовуючи підмножину датасету `mlabonne/FineTome-100k`. Мета — надати вам простий наскрізний робочий процес, який охоплює налаштування, тренування, інференс і збереження результату дофайнтюнінгу.

Приклад розроблено так, щоб бути практичним і легким для модифікації, тому ви можете використовувати його як відправну точку для власних датасетів і моделей.

## Що ви дізнаєтеся

- Як налаштувати середовище Unsloth
- Як дофайнтюнити LLM за допомогою SFT з Unsloth
- Як зберегти результат дофайнтюнінгу в локальному сховищі

<!-- @device:halo,stx,krk -->
> **Примітка:** Техніки дофайнтюнінгу в цьому плейбуку вимагають щонайменше **64 ГБ системної оперативної пам'яті**, з яких щонайменше **24 ГБ доступні GPU** (ці 24 ГБ є частиною 64 ГБ, а не додатковими).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примітка:** Техніки дофайнтюнінгу в цьому плейбуку вимагають щонайменше **24 ГБ загальної пам'яті GPU** та **32 ГБ системної оперативної пам'яті**.
> - У Windows загальна пам'ять GPU поєднує виділену VRAM відеокарти з спільною пам'яттю GPU (запозиченою з системної оперативної пам'яті).
> - Тому карти з менш ніж 24 ГБ виділеної VRAM все ще можуть запускати цей плейбук, використовуючи спільну пам'ять GPU для компенсації різниці.
<!-- @os:end -->

<!-- @os:linux -->
> **Примітка:** Техніки дофайнтюнінгу в цьому плейбуку вимагають відеокарту з щонайменше **24 ГБ виділеної пам'яті GPU** та **32 ГБ системної оперативної пам'яті**.
> - У Linux тренування виконується повністю у виділеній VRAM відеокарти.
> - Воно не переходить на спільну пам'ять GPU (системну оперативну пам'ять), коли VRAM вичерпується.
> - Картам з менш ніж 24 ГБ виділеної VRAM бракуватиме пам'яті під час тренування на Linux, навіть якщо в системі достатньо оперативної пам'яті.
<!-- @os:end -->
<!-- @device:end -->

## Чому Unsloth?

Unsloth полегшує запуск дофайнтюнінгу LLM на локальному апаратному забезпеченні, зменшуючи використання пам'яті та прискорюючи тренування порівняно зі стандартним налаштуванням.

У цьому плейбуку ми використовуємо Unsloth разом із **LoRA-based SFT**. Це означає, що базова модель залишається переважно замороженою, тоді як тренується значно менший набір ваг адаптера. Це добре підходить для локальної розробки, оскільки легше за повне дофайнтюнінгу і швидше для ітерацій.

Unsloth також підтримує інші підходи до тренування, включаючи QLoRA та робочі процеси навчання з підкріпленням. Цей плейбук зосереджується спочатку на найпростішому шляху: невеликому прикладі дофайнтюнінгу LoRA, який користувачі можуть запустити, зрозуміти та розширити.

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

### Створення віртуального середовища

<!-- @os:linux -->
<!-- @device:halo_box -->
Відкрийте термінал і створіть venv з уже встановленим програмним забезпеченням AMD ROCm™ та PyTorch:
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
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набрали чинності):

```bash
sudo usermod -aG render,video $LOGNAME
```

Відкрийте термінал і створіть venv:
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
<!-- @require:driver -->

> **Важливо:** Unsloth ще не підтримує збірку PyTorch 2.13, яка постачається з ROCm 10. Для цього плейбуку встановіть **ROCm 7.14 з PyTorch 2.12**, використовуючи наведені нижче команди. Не використовуйте пакети ROCm 10 / PyTorch 2.13.

**Встановіть PyTorch з підтримкою AMD ROCm™ software** у створеному віртуальному середовищі:

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

Для інших пристроїв, будь ласка, зверніться до [Документації ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) для повних інструкцій.

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Примітка:** Під час імпорту Unsloth може перевіряти опціональні шляхи прискорення `bitsandbytes`. У деяких версіях ROCm ви можете побачити повідомлення на кшталт `bitsandbytes library load error: Configured ROCm binary not found`. Цей плейбук використовує стандартне дофайнтюнінгу LoRA з `optim="adamw_torch"`, тому ми не покладаємося на оптимізатор `bitsandbytes` або 4-бітний QLoRA. Це повідомлення можна безпечно ігнорувати.

<!-- @os:windows -->
> **Примітка:** У Windows ROCm Unsloth виведе кілька попереджень під час запуску — див. [Відомі попередження](#known-warnings) нижче. Усі вони безпечні для ігнорування; тренування працює коректно.
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

## Завантажте скрипт дофайнтюнінгу Unsloth

Замість того, щоб вручну виконувати кожен крок, цей плейбук надає чіткий, наскрізний скрипт тут: [test_unsloth.py](assets/test_unsloth.py).

Виконайте наступний код для запуску скрипта:

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

Решта плейбука концептуально розгляне кожен основний крок скрипта.

## Як це працює

Скрипт test_unsloth.py виконує наступні кроки:
* **Завантаження моделі**: Завантажує unsloth/gemma-4-E4B-it за допомогою FastModel.
* **Підготовка даних**: Стандартизує датасет (наприклад, FineTome-100k) та застосовує чат-шаблон Gemma-4.
* **Застосування LoRA**: Додає адаптери до мовних, уваги (attention) та MLP модулів для ефективного тренування.
* **Тренування**: Використовує SFTTrainer з маскуванням втрат тільки для відповідей (response-only loss masking).
* **Інференс**: Запускає швидкий тест генерації для перевірки продуктивності.
* **Збереження**: Експортує адаптери LoRA локально.
## Ключове налаштування

Ви можете змінити наступні константи, щоб налаштувати запуск:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Приклад привітального повідомлення Unsloth та виводу під час завантаження вагів моделі:

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

Скрипт запускає коротку демонстрацію навчання з такими параметрами:
- ~50 кроків
- Малий розмір батчу
- Накопичення градієнтів

Під час навчання ви побачите такі журнали:

![alt text](assets/training.png)


## Збереження та розгортання

### Локальне збереження (LoRA)

Скрипт автоматично зберігає адаптери LoRA в OUTPUT_DIR.
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
> **Примітка:** vLLM не підтримує Windows. Щоб розгорнути вашу тонко налаштовану модель на Windows, використовуйте llama.cpp (див. [Експорт GGUF](#export-gguf-for-llamacpp) нижче) або перенесіть об'єднану модель на машину з Linux, на якій запущено vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Для розгортання з vLLM об'єднайте адаптери у повну модель:
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
| `No ROCm platform found for torch.distributed` | ROCm на Windows не підтримує розподілене навчання | Так — навчання з одним GPU не постраждає |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth позначає збірки не для Linux | Так — Windows ROCm працює для SFT з одним GPU |
| `triton is not available` | Triton не має збірки для Windows | Так — Unsloth переходить на ядра PyTorch |

Навчання пройде успішно, незважаючи на ці попередження.
<!-- @os:end -->

## Наступні кроки
- Спробуйте [Unsloth Studio](https://unsloth.ai/docs/new/studio), інтуїтивно зрозумілий графічний інтерфейс для Unsloth
- Навчайте на власних специфічних наборах даних
- Спробуйте тонке налаштування з різними гіперпараметрами
- Розгорніть за допомогою vLLM або llama.cpp
- Спробуйте QLoRA для налаштування з меншим використанням пам'яті

## Ресурси

Нижче наведено додаткові ресурси, щоб дізнатися більше про Unsloth та тонке налаштування:

* [Документація Unsloth](https://docs.unsloth.ai)

* [GitHub Unsloth](https://github.com/unslothai/unsloth)

* [Посібник з тонкого налаштування Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)