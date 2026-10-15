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


Хочете запускати потужні мовні моделі штучного інтелекту на власному обладнанні? Цей посібник покаже вам, як це зробити.
У цьому навчальному посібнику використовується PyTorch на основі програмного забезпечення AMD ROCm™ для запуску моделей, які можуть узагальнювати документи, відповідати на запитання, генерувати текст та багато іншого — і все це локально.

## Чого ви навчитеся

- Запускати LLM, такі як gpt-oss-20b і qwen3.5-4B, локально за допомогою PyTorch та ROCm
- Створити інструмент узагальнення документів за допомогою LLM

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

### Створення віртуального середовища

<!-- @os:linux -->
<!-- @device:halo_box -->
У Linux відкрийте термінал у потрібному каталозі та виконайте наведені команди, щоб створити venv з уже встановленими ROCm+Pytorch.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Надайте вашому користувачу доступ до пристроїв GPU** (для набуття чинності потрібно вийти з системи та увійти знову):

```bash
sudo usermod -aG render,video $LOGNAME
```

У Linux відкрийте термінал у потрібному каталозі та виконайте наведені команди, щоб створити venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
У Windows відкрийте термінал у потрібному каталозі та виконайте наведені команди, щоб створити venv з уже встановленими ROCm+Pytorch.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
У Windows відкрийте термінал у потрібному каталозі та виконайте наведені команди, щоб створити venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Порада**: користувачам Windows може знадобитися змінити політику виконання PowerShell (Execution Policy) (наприклад,
> встановивши значення RemoteSigned або Unrestricted) перед запуском деяких команд Powershell.

<!-- @os:end -->

### Встановлення базових залежностей
<!-- @require:driver,pytorch -->

### Встановлення додаткових залежностей

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Примітка:** якщо модель не завантажується або призводить до нестачі пам'яті, спробуйте встановити пакет `kernels` для завантаження моделі з оптимізованим квантуванням.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Швидкий старт із прикладами скриптів

Цей посібник містить готові до використання скрипти. Натисніть на них, щоб переглянути та завантажити їх у той самий каталог, що й створене вами середовище.

| Скрипт | Опис | Використання |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Базова генерація тексту LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Узагальнювач документів із підтримкою Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Обидва скрипти підтримують:
- Вибір моделі за допомогою прапорця `--model`
- Форматування шаблону чату для належного формування промптів моделі, що особливо корисно для узагальнення документів

## Завантаження та запуск вашого першого LLM

Включений скрипт [run_llm.py](assets/run_llm.py) показує, як генерувати текст за допомогою LLM, використовуючи PyTorch та AMD ROCm.

> **Примітка:** коли ви завантажуєте модель, Hugging Face Transformers спочатку перевіряє свій локальний кеш (`~/.cache/huggingface/hub` у Linux, `C:\Users\<user>\.cache\huggingface\hub` у Windows). Якщо модель не закешована, вона автоматично завантажується з huggingface.co. Перший запуск може зайняти кілька хвилин залежно від розміру моделі та швидкості мережі.

Наведений нижче фрагмент показує, як використовувати модель і налаштовувати поставлені запитання.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Спробуйте завантажений скрипт:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Створення узагальнювача документів

Тепер, коли ви згенерували локальний вивід LLM, ви можете продовжити, створивши практичний узагальнювач документів. У цьому розділі ви використаєте скрипт [summarizer.py](assets/summarizer.py), щоб подати на вхід файл .txt та автоматично згенерувати стисле резюме — і все це локально на вашому GPU.

Скрипт розроблено так, щоб він працював одразу без додаткових налаштувань. Відкрийте скрипт у редакторі, щоб дослідити код, налаштувати промпти та відрегулювати такі параметри, як довжина та температура.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Приклади використання

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Дізнайтеся про параметри генерації

| Параметр | Що контролює | Типові значення |
|-----------|------------------|----------------|
| `max_new_tokens` | Максимальна довжина виведення LLM | Для резюме використовуйте 50–500 токенів. (1 токен становить приблизно 0,75 англійського слова) |
| `temperature` | Творчість. Низькі значення роблять результат зосередженим, а високі — більш непередбачуваним | - **0.1–0.3**: зосереджено, детерміновано (добре для резюме) <br> **0.5–0.7**: збалансовано (для загального використання) <br> **0.8–1.0**: творчо, різноманітно (для мозкового штурму) |
| `top_p` | Nucleus Sampling — низькі значення обмежують модель вужчим набором виводів | **0.1-0.5**: строго, передбачувано <br> **0.9-0.95**: (стандартно, природно, розмовно) |


## Практичне застосування

- **Аналіз наукових статей**: Виокремлення ключових результатів зі складних публікацій для швидкого перегляду
- **Агрегація новин**: Узагальнення новинних статей у короткі щоденні дайджести або основні моменти
- **Нотатки нарад**: Стиснення транскриптів у конкретні пункти дій та стислі резюме
- **Перевірка юридичних документів**: Швидке виокремлення відповідних положень або зобов'язань з довгих юридичних текстів
- **Документація коду**: Створення стислих оглядів репозиторіїв та пояснень функцій
## Наступні кроки

- **Донавчання**: адаптуйте моделі до вашої специфічної галузі або термінології для кращої точності (див. Fine-tuning Playbooks)
- **RAG-системи**: поєднуйте LLM з пошуком документів для контекстно-залежних відповідей і пошуку
- **Дослідження моделей**: експериментуйте з новими моделями, такими як Llama 3, Phi-3 або Qwen, для отримання кращих результатів
- **Розгортання у продакшн**: використовуйте такі інструменти, як vLLM, для масштабованого обслуговування LLM в організаціях

Ваша система дає вам можливість запускати складні мовні моделі локально. Експериментуйте з різними моделями, промптами та параметрами, щоб визначити, що найкраще підходить для ваших застосунків.