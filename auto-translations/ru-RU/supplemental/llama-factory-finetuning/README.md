<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

## Обзор

Эффективная тонкая настройка играет важную роль в адаптации больших языковых моделей (LLM) под конкретные задачи. LLaMA Factory — это платформа с открытым исходным кодом, удобная в использовании и упрощающая обучение и тонкую настройку больших языковых моделей и мультимодальных моделей. Она позволяет пользователям настраивать сотни предобученных моделей локально с минимальным объёмом программирования.

Этот плейбук научит вас выполнять тонкую настройку LLM с помощью LLaMA Factory на вашем локальном оборудовании AMD.

<!-- @device:stx,krk -->
> **Примечание.** Методы тонкой настройки, описанные в этом плейбуке, требуют не менее **32 ГБ оперативной памяти системы**, из которых не менее **16 ГБ должно быть доступно GPU** (эти 16 ГБ являются частью 32 ГБ, а не дополнением к ним).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Примечание.** Методы тонкой настройки, описанные в этом плейбуке, требуют не менее **16 ГБ общей памяти GPU** и **32 ГБ оперативной памяти системы**.
> - В Windows общая память GPU складывается из выделенной видеопамяти (VRAM) видеокарты и совместно используемой памяти GPU (заимствуемой из оперативной памяти системы).
> - Таким образом, видеокарты с менее чем 16 ГБ выделенной VRAM всё же могут использоваться для этого плейбука за счёт использования совместно используемой памяти GPU для восполнения разницы.
<!-- @os:end -->

<!-- @os:linux -->
> **Примечание.** Методы тонкой настройки, описанные в этом плейбуке, требуют видеокарту как минимум с **16 ГБ выделенной памяти GPU** и **32 ГБ оперативной памяти системы**.
> - В Linux обучение выполняется полностью в выделенной видеопамяти (VRAM) видеокарты.
> - При исчерпании VRAM переход на совместно используемую память GPU (оперативную память системы) не происходит.
> - Видеокарты с менее чем 16 ГБ выделенной VRAM исчерпают память во время обучения в Linux, даже если в системе достаточно оперативной памяти.
<!-- @os:end -->
<!-- @device:end -->

## Чему вы научитесь

- Как настроить LLaMA Factory с программным обеспечением AMD ROCm™
- Как настроить параметры тонкой настройки LLM (на примере Qwen/Qwen3-4B-Instruct-2507)
- Как запустить тонкую настройку в LLaMA Factory
- Как выполнить вывод с помощью дообученной модели
- Как экспортировать дообученную модель 

## Приблизительное время

- Продолжительность: выполнение этого плейбука займёт около 60 минут (в зависимости от размера вашей модели/набора данных и скорости сети).
- Дополнительную информацию см. на странице [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

<!-- @prereq:hf-models-qwen3-4b-instruct-2507 -->

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Создание виртуальной среды

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления изменений в силу выйдите из системы и войдите снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
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

### Установка дополнительных зависимостей

> **Примечание**: убедитесь, что используется версия Python 3.11, 3.12 или 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Установка LLaMA Factory

LLaMA Factory зависит от PyTorch. Он уже должен быть установлен в соответствии с указанными выше требованиями.

Скачайте исходный код из [официального репозитория LLaMA Factory на GitHub](https://github.com/hiyouga/LlamaFactory) и установите его зависимости.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Проверьте, что `llamafactory-cli` является исполняемым.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Пример вывода:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

После успешной установки LLaMA Factory давайте запустим на ней тонкую настройку.

## Использование LLaMA Factory CLI для тонкой настройки 

В этом разделе рассматривается подготовка наборов данных для тонкой настройки, настройка параметров LoRA/QLoRA и запуск тонкой настройки LoRA.

### Подготовка набора данных

LLaMA Factory поддерживает наборы данных для тонкой настройки в форматах Alpaca и ShareGPT. Все доступные наборы данных описаны в файле [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Если вы используете собственный набор данных, убедитесь, что добавили его описание в `dataset_info.json` и указали имя набора данных перед обучением. Подробности можно найти в их документации [здесь](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

В этом плейбуке в качестве примера мы будем использовать наборы данных identity и alpaca_en_demo, а настройку информации о наборе данных выполним на следующем шаге.
### Настройка параметров тонкой настройки

LLaMA Factory поддерживает несколько схем тонкой настройки.

| Схема тонкой настройки | Примеры LLaMA Factory |
|-----------|------|
| Полная тонкая настройка параметров    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Тонкая настройка LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Тонкая настройка QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

В этих примерах конфигурационных файлов уже указаны параметры модели, параметры метода тонкой настройки, параметры набора данных, параметры оценки и другие. Вы можете настроить их в соответствии со своими потребностями. В этом руководстве мы будем использовать [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Описание ключевых параметров:**
- `model_name_or_path` — название модели Hugging Face или путь к локальному файлу модели.
- `stage` — этап обучения. Варианты: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` — true для обучения, false для оценки
- `finetuning_type` — метод тонкой настройки. Варианты: freeze, lora, full
- `lora_rank` — размерность матрицы низкого ранга, используемой в методе LoRA, типичные значения: 4, 6, 8, 16 (меньшие значения — меньше параметров — быстрее тонкая настройка; большие значения — лучшая адаптация к задаче, но выше потребление ресурсов).
- `lora_target` — целевые модули для метода LoRA. По умолчанию: all.
- `dataset` — используемый набор(ы) данных. Используйте «,» для разделения нескольких наборов данных
- `output_dir` — путь для вывода результатов тонкой настройки
- `logging_steps` — интервал логирования в шагах
- `save_steps` — интервал сохранения контрольных точек модели.
- `overwrite_output_dir` — разрешить ли перезапись выходного каталога.
- `per_device_train_batch_size` — размер обучающего батча на устройство.
- `gradient_accumulation_steps` — количество шагов накопления градиента.
- `learning_rate` — скорость обучения
- `num_train_epochs` — количество эпох обучения
- `lr_scheduler_type` — расписание скорости обучения. Варианты: linear, cosine, polynomial, constant и т. д.
- `warmup_ratio` — коэффициент разогрева скорости обучения

<!-- @os:linux -->
Мы изменим значение по умолчанию параметра `lora_rank` для запуска тонкой настройки на AMD Ryzen™ и AMD Radeon™ GPU.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Мы обновим конфигурацию тонкой настройки LoRA по умолчанию для лучшей совместимости с AMD Ryzen™ и AMD Radeon™ GPU:
- Изменим `lora_rank` с `8` на `6`, чтобы снизить потребление памяти во время тонкой настройки.
- Используем `fp16` вместо `bf16` для более широкой совместимости с AMD GPU и снижения потребления памяти.
- Установим `dataloader_num_workers` в `0` в Windows, чтобы избежать ошибок `"Can't pickle local object<>"`, вызванных многопроцессной загрузкой данных.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### Запуск тонкой настройки с помощью LLaMA Factory

**llamafactory-cli** — это официальный инструмент командной строки (CLI) для LLaMA Factory, разработанный для упрощения сквозных рабочих процессов LLM (подготовка данных → тонкая настройка → оценка → развертывание) без написания сложного кода.

Для обучения/тонкой настройки **llamafactory-cli train** является основной подкомандой LLaMA Factory CLI. Она объединяет рабочие процессы тонкой настройки (предобработка данных, настройка гиперпараметров, оптимизация под оборудование) в одну команду CLI, поддерживает несколько парадигм тонкой настройки (LoRA/QLoRA/полная тонкая настройка) и оптимизирована для GPU с ограниченными ресурсами (например, QLoRA на видеопамяти 16 ГБ).

Вы можете запустить тонкую настройку LLaMA Factory с помощью следующей команды, основанной на изменённом конфигурационном файле тонкой настройки Qwen3 LoRA.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

После запуска тонкой настройки LLM все сгенерированные выходные данные сохраняются в «output_dir», включая файлы контрольных точек модели, конфигурационные файлы и метрики обучения.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### Тестирование дообученной модели 

**llamafactory-cli chat** предназначен для интерактивного общения/вывода с LLM (как с базовыми моделями, так и с моделями, дообученными с помощью LoRA). LLaMA Factory предоставляет пример конфигурации для запуска вывода дообученных моделей в [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Вы также можете изменить эту примерную конфигурацию, чтобы изменить настройки, например, бэкенд вывода.

Используйте следующую команду для тестирования дообученной модели Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Пример общения с использованием дообученной модели показан ниже:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Экспорт дообученной модели

Для использования в production необходимо объединить предобученную модель и адаптер LoRA и экспортировать их в единую модель. Эта объединённая модель может использоваться как обычный файл модели Hugging Face. LLaMA Factory предоставляет примеры конфигураций в [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Используйте следующую команду для экспорта дообученной модели Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Результат экспорта дообученной модели показан ниже.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
## Использование графического интерфейса LLaMA Factory

`LLaMA-Factory` также поддерживает дообучение LLM без написания кода через веб-интерфейс в браузере.

Используйте следующую команду, чтобы открыть его:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` предоставляет удобный интерфейс для управления рабочими процессами машинного обучения, включая обучение, оценку, предсказание, общение в чате и экспорт моделей. Вот краткое описание каждой вкладки:

* **Train**: эта вкладка позволяет выбрать модель и набор данных, настроить параметры обучения и запустить процесс обучения. Важно понимать обязательные и опциональные параметры, чтобы оптимизировать настройку обучения.
* **Evaluate & Predict**: после обучения вы можете оценить производительность модели и выполнить предсказания с помощью этой вкладки. Она предоставляет сведения о точности и эффективности модели на новых данных.
* **Chat**: после завершения обучения загрузите модель во вкладке Chat, чтобы взаимодействовать с ней и увидеть результаты вашей работы. Эта функция позволяет общаться с обученной моделью в реальном времени.
* **Export**: эта вкладка упрощает экспорт обученных моделей для развёртывания или дальнейшего использования. Вы можете сохранять модели в различных форматах, подходящих для разных приложений.

Для получения подробных инструкций рекомендуем ознакомиться с официальной документацией в [репозитории LlamaFactory на GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) и на [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Кроме того, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) содержит ценную информацию об интерфейсе и его возможностях.

## Дальнейшие шаги
- Попробуйте различные модели, такие как `gpt-oss` и другие современные модели.
- Поэкспериментируйте с разными бэкендами на дообученной модели
 
Дополнительную документацию см. по адресу: https://llamafactory.readthedocs.io/en/latest/ 