<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор


Хотите запускать мощные языковые модели ИИ на собственном оборудовании? Это руководство покажет вам, как это сделать.
В данном руководстве используется PyTorch на базе программного обеспечения AMD ROCm™ для запуска моделей, способных суммировать документы, отвечать на вопросы, генерировать текст и многое другое — всё это работает локально.

## Что вы узнаете

- Запускать LLM, такие как gpt-oss-20b и qwen3.5-4B, локально с использованием PyTorch и ROCm
- Создавать инструмент суммаризации документов с помощью LLM

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения
> **Примечание**: Если VS Code не установлен, вы можете установить его с помощью Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимых программных компонентов

### Создание виртуальной среды

<!-- @os:linux -->
<!-- @device:halo_box -->
В Linux откройте терминал в выбранном каталоге и выполните команды для создания venv с уже установленными ROCm+Pytorch.
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
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления в силу необходимо выйти из системы и войти снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

В Linux откройте терминал в выбранном каталоге и выполните команды для создания venv.
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
В Windows откройте терминал в выбранном каталоге и выполните команды для создания venv с уже установленными ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
В Windows откройте терминал в выбранном каталоге и выполните команды для создания venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Совет**: Пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
> установить значение RemoteSigned или Unrestricted) перед выполнением некоторых команд Powershell.

<!-- @os:end -->

### Установка основных зависимостей
<!-- @require:driver,pytorch -->

### Установка дополнительных зависимостей

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

## Быстрый старт с примерами скриптов

Этот playbook включает готовые к использованию скрипты. Нажмите на них для предварительного просмотра и загрузите в тот же каталог, где была создана среда.

| Скрипт | Описание | Использование |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Базовая генерация текста с помощью LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Суммаризатор документов с поддержкой Harmony | `python summarizer.py --file document.txt` |

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

Оба скрипта поддерживают:
- Выбор модели с помощью флага `--model`
- Форматирование с использованием шаблона чата для корректного формирования запросов к модели, что особенно полезно при суммаризации документов

## Загрузка и запуск первой LLM

Включённый скрипт [run_llm.py](assets/run_llm.py) демонстрирует, как генерировать текст с помощью LLM, используя PyTorch и AMD ROCm.

> **Примечание:** При загрузке модели Hugging Face Transformers сначала проверяет локальный кэш (`~/.cache/huggingface/hub` в Linux, `C:\Users\<user>\.cache\huggingface\hub` в Windows). Если модель не кэширована, она автоматически загружается с huggingface.co. Первый запуск может занять несколько минут в зависимости от размера модели и скорости сети.

Фрагмент ниже показывает, как использовать модель и настраивать задаваемые вопросы.

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

Попробуйте загруженный скрипт:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Создание суммаризатора документов

Теперь, когда вы получили локальный вывод LLM, вы можете развить это, создав практичный суммаризатор документов. В этом разделе вы будете использовать скрипт [summarizer.py](assets/summarizer.py), чтобы передать файл .txt и автоматически сгенерировать краткое резюме — всё это работает локально на вашем GPU.

Скрипт разработан для работы «из коробки». Откройте скрипт в редакторе, чтобы изучить код, настроить запросы и изменить такие параметры, как длина и температура.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Примеры использования

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

## Узнайте о параметрах генерации

| Параметр | Что контролирует | Типичные значения |
|-----------|------------------|----------------|
| `max_new_tokens` | Максимальная длина вывода LLM | Используйте 50–500 токенов для резюме. (1 токен — примерно 0,75 слова на английском языке) |
| `temperature` | Креативность. Низкие значения делают вывод сфокусированным, высокие — менее предсказуемым | - **0.1–0.3**: Сфокусированный, детерминированный (хорошо для резюме) <br> **0.5–0.7**: Сбалансированный (общее использование) <br> **0.8–1.0**: Творческий, разнообразный (мозговой штурм) |
| `top_p` | Nucleus Sampling — низкие значения ограничивают модель более узкими выводами | **0.1-0.5**: Строгий, предсказуемый <br> **0.9-0.95**: (стандартный, естественный, разговорный) |


## Реальные сценарии применения

- **Анализ научных статей**: Извлечение ключевых выводов из сложных публикаций для быстрого ознакомления
- **Агрегация новостей**: Суммаризация новостных статей в краткие ежедневные дайджесты или обзоры
- **Заметки с совещаний**: Сжатие стенограмм в список действий и краткие резюме
- **Проверка юридических документов**: Быстрое извлечение соответствующих пунктов или обязательств из объёмных юридических текстов
- **Документация кода**: Создание кратких обзоров репозиториев и пояснений к функциям

## Следующие шаги

- **Тонкая настройка**: Адаптация моделей к вашей конкретной области или терминологии для повышения точности (см. playbook по тонкой настройке)
- **RAG-системы**: Объединение LLM с поиском по документам для контекстно-зависимых ответов и поиска
- **Исследование моделей**: Экспериментируйте с новыми моделями, такими как Llama 3, Phi-3 или Qwen, для получения лучших результатов
- **Производственное развёртывание**: Используйте такие инструменты, как vLLM, для масштабируемого обслуживания LLM в организациях

Ваша система даёт вам возможность запускать сложные языковые модели локально. Экспериментируйте с различными моделями, запросами и параметрами, чтобы найти то, что лучше всего подходит для ваших задач.