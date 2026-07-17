<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд


Хочете запускати потужні мовні моделі ШІ на власному обладнанні? Цей посібник покаже вам, як це зробити.
У цьому підручнику використовується PyTorch на основі програмного забезпечення AMD ROCm™ для запуску моделей, які можуть підсумовувати документи, відповідати на запитання, генерувати текст тощо — все це працює локально.

## Що ви дізнаєтесь

- Запускати LLM, такі як gpt-oss-20b та qwen3.5-4B, локально за допомогою PyTorch та ROCm
- Створювати інструмент для підсумовування документів за допомогою LLM

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідних програмних компонентів

### Створення віртуального середовища

<!-- @os:linux -->
<!-- @device:halo_box -->
На Linux відкрийте термінал у вибраному каталозі та виконайте команди для створення venv із вже встановленими ROCm+Pytorch.
<!-- @test:id=create-venv timeout=120 -->
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
**Надайте вашому користувачу доступ до пристроїв GPU** (для набрання чинності необхідно вийти з системи та увійти знову):

```bash
sudo usermod -aG render,video $LOGNAME
```

На Linux відкрийте термінал у вибраному каталозі та виконайте команди для створення venv.
<!-- @test:id=create-venv timeout=120 -->
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
На Windows відкрийте термінал у вибраному каталозі та виконайте команди для створення venv із вже встановленими ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
На Windows відкрийте термінал у вибраному каталозі та виконайте команди для створення venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Порада**: Користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
> встановити значення RemoteSigned або Unrestricted) перед виконанням деяких команд Powershell.

<!-- @os:end -->

### Встановлення основних залежностей
<!-- @require:driver,pytorch -->

### Встановлення додаткових залежностей

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Швидкий старт із прикладами скриптів

Цей посібник містить готові до використання скрипти. Натисніть на них, щоб переглянути та завантажити їх до того самого каталогу, де ви створили середовище.

| Скрипт | Опис | Використання |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Базова генерація тексту за допомогою LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Інструмент підсумовування документів із підтримкою Harmony | `python summarizer.py --file document.txt` |

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
- Форматування шаблону чату для правильного формулювання запитів до моделі, що особливо корисно для підсумовування документів

## Завантаження та запуск вашої першої LLM

Доданий скрипт [run_llm.py](assets/run_llm.py) показує, як генерувати текст за допомогою LLM із використанням PyTorch та AMD ROCm.

> **Примітка:** Під час завантаження моделі Hugging Face Transformers спочатку перевіряє локальний кеш (`~/.cache/huggingface/hub` на Linux, `C:\Users\<user>\.cache\huggingface\hub` на Windows). Якщо модель не кешована, вона автоматично завантажується з huggingface.co. Перший запуск може зайняти кілька хвилин залежно від розміру моделі та швидкості мережі.

Наведений нижче фрагмент показує, як використовувати модель і налаштовувати запитання.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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


## Створення інструменту підсумовування документів

Тепер, коли ви отримали локальний вивід LLM, ви можете розвинути це, створивши практичний інструмент підсумовування документів. У цьому розділі ви використаєте скрипт [summarizer.py](assets/summarizer.py), щоб передати файл .txt і автоматично згенерувати стислий підсумок — все це працює локально на вашому GPU.

Скрипт розроблено так, щоб він працював одразу після завантаження. Відкрийте скрипт у редакторі, щоб вивчити код, налаштувати підказки та змінити такі параметри, як довжина та температура.

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

| Параметр | Що він контролює | Типові значення |
|-----------|------------------|----------------|
| `max_new_tokens` | Максимальна довжина виводу LLM | Використовуйте 50–500 токенів для підсумків. (1 токен — приблизно 0,75 слова англійською) |
| `temperature` | Креативність. Низькі значення роблять вивід більш зосередженим, тоді як високі значення додають непередбачуваності | - **0.1–0.3**: Зосереджений, детермінований (добре для підсумків) <br> **0.5–0.7**: Збалансований (загальне використання) <br> **0.8–1.0**: Творчий, різноманітний (мозковий штурм) |
| `top_p` | Ядерна вибірка — низькі значення обмежують модель більш вузькими виводами | **0.1-0.5**: Суворий, передбачуваний <br> **0.9-0.95**: (стандартний, природний, розмовний) |


## Практичне застосування

- **Аналіз наукових статей**: Витягуйте ключові висновки зі складних публікацій для швидкого ознайомлення
- **Агрегація новин**: Підсумовуйте новинні статті у стислі щоденні дайджести або огляди
- **Нотатки нарад**: Стискайте стенограми до переліку дій та стислих підсумків
- **Перегляд юридичних документів**: Швидко витягуйте відповідні пункти або зобов'язання з довгих юридичних текстів
- **Документація коду**: Генеруйте стислі огляди репозиторіїв та пояснення функцій

## Наступні кроки

- **Тонке налаштування**: Адаптуйте моделі до вашої конкретної галузі або термінології для кращої точності (див. посібники з тонкого налаштування)
- **RAG-системи**: Поєднуйте LLM із пошуком документів для контекстно-залежних відповідей і пошуку
- **Дослідження моделей**: Експериментуйте з новими моделями, такими як Llama 3, Phi-3 або Qwen, для кращих результатів
- **Розгортання у виробництві**: Використовуйте такі інструменти, як vLLM, для масштабованого обслуговування LLM в організаціях

Ваша система дає вам можливість запускати складні мовні моделі локально. Експериментуйте з різними моделями, підказками та параметрами, щоб знайти те, що найкраще підходить для ваших застосунків.