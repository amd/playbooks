<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не проверялась человеком. Она может содержать ошибки, а некоторые шаги, команды, ссылки для скачивания или доступность продукта могут отличаться в вашем языке или регионе. Если что-то выглядит некорректно, ориентируйтесь на оригинальный playbook на английском языке как на достоверный источник.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> В этом руководстве используются специальные теги, которые GitHub не может отобразить. Пожалуйста, посетите [amd.com/playbooks](https://amd.com/playbooks) для корректного просмотра этого содержимого.
<!-- @github-only:end -->

# Кластеризация двух Ryzen™ AI Halo с помощью RPC

## Обзор

Ваш Ryzen™ AI Halo уже способен запускать большие языковые модели локально. Кластеризация выводит это на новый уровень, объединяя память GPU нескольких систем через локальную сеть, что дает вам доступ к еще более крупным моделям с более сильным reasoning, лучшей генерацией кода и более глубоким многоязычным пониманием — и все это полностью на вашем собственном оборудовании.

Это руководство научит вас кластеризовать две системы Ryzen AI Halo с использованием RPC-движка llama.cpp и запускать GLM 4.7, модель с 358 миллиардами параметров, на обеих машинах с ускорением AMD ROCm™.

## Чему вы научитесь

- Как расширить выделение VRAM на системах Ryzen AI Halo
- Установка llama.cpp с поддержкой ROCm и RPC
- Настройка RPC-воркера и запуск распределенного вывода на двух узлах
- Запуск модели с 358 миллиардами параметров на двух объединенных в сеть системах Ryzen AI Halo

## Настройка конфигурации памяти

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

<!-- @os:windows -->
В Windows для запуска более крупных моделей, требующих больше памяти, необходимо использовать выделение AMD Variable Graphics Memory (iGPU VRAM).

Это можно сделать, открыв панель управления AMD Software: Adrenalin Edition и перейдя в: `Performance > Tuning > AMD Variable Graphics Memory`. Установите значение **96 GB**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
В Linux ROCm использует общий пул системной памяти, и по умолчанию этот пул настроен на половину системной памяти.

Этот объем можно увеличить, изменив настройку страниц Translation Table Manager (TTM) ядра, следуя приведенным ниже инструкциям. AMD рекомендует установить минимальный выделенный объем VRAM в BIOS (0,5 GB).

* Установите утилиту pipx и добавьте путь для установленных через pipx пакетов в системный путь поиска.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Установите пакет amd-debug-tools из PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустите инструмент amd-ttm, чтобы узнать текущие настройки общей памяти.
  ```bash
  amd-ttm
  ```

* Измените настройки общей памяти на **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Перезагрузите систему, чтобы изменения вступили в силу.


<!-- @os:end -->
<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->
## Предварительные требования

### Оборудование

Для этого руководства требуются два устройства Ryzen AI Halo и один сетевой коммутатор Ethernet, соединенные по топологии «звезда», при этом каждое устройство подключено напрямую к коммутатору.

| Компонент | Количество | Описание |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Вычислительные узлы, образующие кластер |
| Сетевой коммутатор Ethernet 10 Гбит/с | 1 | Центральный коммутатор для обеспечения связи между несколькими узлами Ryzen AI Halo (не менее 2 портов) |
| Кабель Ethernet | 2 | Соединяет каждое устройство Halo с коммутатором (рекомендуется Cat 7 или выше) |

> **Примечание**: Для подключения двух устройств Ryzen AI Halo требуется два порта сетевого коммутатора Ethernet. Третий порт требуется, если вы обращаетесь к модели с отдельной клиентской машины, а не с одного из устройств Halo.

### Программное обеспечение
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Установите:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) с рабочей нагрузкой **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Настройка физического оборудования

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

Подключите каждое устройство Ryzen AI Halo к сетевому коммутатору Ethernet с помощью кабеля Cat 7 (или выше). Это устанавливает соединение со скоростью 10 Гбит/с, используемое для высокоскоростной связи между узлами.
<!-- @os:linux -->
### 1. Определение сетевых интерфейсов

На каждой машине найдите имя ее сетевого интерфейса и запишите его (далее оно будет упоминаться как `IFNAME`). Выполните:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Это выводит имя интерфейса напрямую, например:

```bash
enp191s0
```

### 2. Проверка скорости сетевого соединения

Убедитесь, что соединение активно и работает на полной скорости, проверив скорость своего интерфейса:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примечание**: Замените `<IFNAME>` на имя выходного интерфейса из раздела [1. Определение сетевых интерфейсов](#1-определение-сетевых-интерфейсов)

Вы должны увидеть скорость `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примечание**: Если скорость ниже `10000Mb/s` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и установить скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Проверка скорости сетевого соединения

На каждой машине проверьте скорость соединения своих сетевых интерфейсов:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш интерфейс Ethernet должен быть в состоянии `Up` и работать на скорости `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примечание**: Если скорость ниже `10 Gbps` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и установить скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

## Установка llama.cpp

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

Доступны два варианта установки:

- [Вариант 1: Lemonade SDK (рекомендуется)](#option-1-lemonade-sdk-recommended) — готовые сборки, самая быстрая настройка
- [Вариант 2: Ручная сборка из исходного кода](#option-2-manual-source-build) — сборка из исходного кода с полным контролем над флагами сборки

### Вариант 1: Lemonade SDK (рекомендуется)

Lemonade SDK предоставляет ночные сборки llama.cpp с ускорением AMD ROCm 7, ориентированные на GPU, такие как gfx1151 (Strix Halo / Ryzen AI Max+ 395), и другие современные архитектуры Radeon.

<!-- @os:windows -->
#### Step 1: Загрузка предварительно скомпилированных бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Step 2: Извлечение бинарных файлов

Распакуйте загруженный архив:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Теперь этот каталог содержит сборки `llama-cli.exe`, `llama-server.exe` и `rpc-server.exe` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

#### Step 3: Проверка обнаружения GPU

```bash
.\llama-cli.exe --list-devices
```

Ожидаемый результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Загрузка предварительно скомпилированных бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Step 2: Извлечение и подготовка бинарных файлов

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Теперь этот каталог содержит сборки `llama-cli`, `llama-server` и `rpc-server` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

#### Step 3: Проверка обнаружения GPU

```bash
./llama-cli --list-devices
```

Ожидаемый результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).

### Вариант 2: Ручная сборка из исходного кода

<!-- @os:windows -->
#### Step 1: Сборка llama.cpp

Откройте **x64 Native Tools Command Prompt** (устанавливается вместе с Visual Studio Build Tools) и склонируйте репозиторий:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Добавьте HIP в путь и выполните сборку с поддержкой ROCm и RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm/HIP |
| `-DGGML_RPC=ON` | Включает RPC для распределённого вывода |
| `-DGPU_TARGETS=gfx1151` | Целевой GPU — Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Использует систему сборки Ninja |

#### Step 2: Проверка обнаружения GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Ожидаемый результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Step 3: Добавление HIP в пользовательский путь

Шаг сборки выше устанавливает `%HIP_PATH%\bin` только для текущей сессии. Чтобы сделать библиотеки HIP доступными в любом терминале (а не только в x64 Native Tools Command Prompt), добавьте его в пользовательскую переменную `PATH` на постоянной основе:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Сборка llama.cpp

Склонируйте репозиторий:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Выполните сборку с поддержкой ROCm и RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm |
| `-DGGML_RPC=ON` | Включает RPC для распределённого вывода |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Включает rocWMMA для улучшенного Flash Attention на GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Целевой GPU — Ryzen AI Halo (Radeon 8060s) |

Дополнительные параметры сборки см. в [документации по сборке llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Проверка обнаружения GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Ожидаемый результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).
<!-- @os:end -->

## Загрузка модели

В этом руководстве используется [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) — модель с 358 млрд параметров в квантовании `Q4_K_XL` от [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). В этом квантовании модель требует примерно 205 ГБ хранилища и помещается в суммарную память GPU двух узлов Ryzen AI Halo.

Загрузите файлы GGUF с помощью Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Примечание**: загрузка модели должна быть выполнена на Machine 1 (контроллере). Узлам RPC-воркеров локальная копия файлов модели не требуется.

## Запуск модели на кластере

Движок RPC (Remote Procedure Call) llama.cpp позволяет одному экземпляру llama.cpp выгружать слои модели на удалённые воркеры по сети. Одна машина выступает в роли **контроллера** (Machine 1), выполняя токенизацию, планирование и оркестрацию. Другая машина запускает лёгкий **RPC-сервер** (Machine 2), предоставляющий контроллеру доступ к своей памяти GPU и вычислительным ресурсам.

Во время загрузки llama.cpp распределяет модель между обоими узлами. После загрузки вывод выполняется так, как будто он работает на едином ускорителе. RPC обрабатывает передачу тензоров и синхронизацию «за кулисами».

### Step 1: Запуск RPC-сервера (Machine 2)

На Machine 2 запустите RPC-сервер, чтобы предоставить контроллеру доступ к своим ресурсам GPU:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Флаг | Назначение |
|------|---------|
| `-p` | Порт, на котором транслируется RPC-сервер |
| `-c` | Включает локальный кэш для больших тензоров, избегая повторной передачи данных по сети при загрузке модели |
| `--host` | IP-адрес для привязки RPC-сервера (`0.0.0.0` для всех интерфейсов) |

Дополнительные параметры см. в [документации RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Запуск модели (Machine 1)

После запуска RPC-сервера на Machine 2 запустите вывод с Machine 1, используя `llama-cli` или `llama-server`.

#### llama-cli

`llama-cli` предоставляет терминальный интерфейс для прямого взаимодействия с моделью. Он идеально подходит для бенчмаркинга, отладки и низкоуровневых экспериментов.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: на Machine 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: выполните эту команду в терминале (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: на Machine 2 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.

<!-- @os:end -->

После запуска `llama-cli` отображает прогресс загрузки модели и переходит в интерактивный режим, где вы можете напрямую общаться с моделью:

![llama-cli выполняет GLM 4.7 на двух узлах](assets/llama-cli-example.png)
#### llama-server

`llama-server` предоставляет тот же движок вывода через постоянный серверный процесс со встроенным веб-интерфейсом и HTTP API, совместимым с OpenAI. Это предпочтительный интерфейс для долговременных развертываний, многопользовательского доступа и интеграции с внешними инструментами.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: На Машине 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: Выполните эту команду в терминале (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: На Машине 2 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

После запуска откройте `http://<HOST_IP>:8081` в браузере, чтобы получить доступ к встроенному веб-интерфейсу. Он предоставляет чат-интерфейс на основе браузера для взаимодействия с моделью:

![Веб-интерфейс llama-server с запущенной GLM 4.7 на двух узлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Определение `<HOST_IP>`**: На Машине 1 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Определение `<HOST_IP>`**: На Машине 1 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

#### Справочник параметров

| Флаг | Назначение |
|------|---------|
| `-m` | Путь к файлу модели GGUF (используйте первый фрагмент, `00001-of-00005`) |
| `-c` | Размер контекста в токенах. Большие значения используют больше памяти |
| `-fa on` | Включает rocWMMA Flash Attention для повышения производительности на GPU AMD |
| `-ngl 999` | Выгружает все слои модели на GPU |
| `--no-mmap` | Отключает отображение памяти (memory-mapping), сокращая время загрузки, когда размер модели превышает объём системной RAM, но помещается в VRAM |
| `--host` | IP-адрес для привязки `llama-server` (только для `llama-server`) |
| `--port` | Порт для обслуживания HTTP API (только для `llama-server`) |
| `--rpc` | Список конечных точек RPC-воркеров через запятую (`IP:port`) |

Полное описание использования параметров см. в [документации llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) и [документации llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Дальнейшие шаги

- **Подключение сторонних приложений**: `llama-server` предоставляет API, совместимый с OpenAI. Направьте любое приложение, совместимое с OpenAI (например, Open WebUI), на `http://<HOST_IP>:8081` с любым фиктивным API-ключом (например, `none`), чтобы подключиться к вашему кластеру
- **Изучение других моделей**: Просмотрите квантованные GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), чтобы найти модели, помещающиеся в общий объём памяти GPU вашего кластера
- **Масштабирование до четырёх узлов**: Добавьте ещё две системы Ryzen AI Halo в качестве дополнительных RPC-воркеров, чтобы получить доступ к моделям масштаба 1 триллиона параметров. Передайте дополнительные конечные точки в `--rpc` в виде списка через запятую (например, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)