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

# Кластеризация четырёх Ryzen™ AI Halo с помощью RPC

## Обзор

Ваш Ryzen™ AI Halo уже способен локально запускать большие языковые модели. Кластеризация выводит это на новый уровень, объединяя память GPU нескольких систем по локальной сети, что открывает доступ к ещё более крупным моделям с более сильным логическим мышлением, лучшей генерацией кода и более глубоким пониманием многоязычного текста — и всё это полностью на вашем собственном оборудовании.

Этот практикум научит вас кластеризовать четыре системы Ryzen AI Halo с помощью RPC-движка llama.cpp и запускать Kimi K2.6, большую модель mixture-of-experts, на всех четырёх машинах с ускорением AMD ROCm™.

## Что вы узнаете

- Как расширить выделение VRAM на системах Ryzen AI Halo
- Установку llama.cpp с поддержкой ROCm и RPC
- Настройку RPC-воркеров и запуск распределённого вывода на четырёх узлах
- Запуск модели с 1 трлн параметров на четырёх объединённых в сеть системах Ryzen AI Halo

## Настройка конфигурации памяти

> **Примечание**: Выполните этот шаг на всех четырёх машинах (с Машины 1 по Машину 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Запуск моделей, занимающих около 128 ГБ или более:** В системах AMD Ryzen™ AI Max 400 Series (Gorgon Halo) под управлением Windows модели, объём которых приближается к 128 ГБ памяти или превышает его, требуют дополнительной настройки для корректной работы без ошибок. Перед загрузкой модели выполните инструкции из [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
В Windows для запуска более крупных моделей, требующих большего объёма памяти, необходимо использовать выделение памяти AMD Variable Graphics Memory (iGPU VRAM).

Это можно сделать, открыв панель управления AMD Software: Adrenalin Edition и перейдя в раздел: `Performance > Tuning > AMD Variable Graphics Memory`. Установите значение **96 ГБ**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
В Linux ROCm использует общий пул системной памяти, и по умолчанию этот пул настроен на половину объёма системной памяти.

Этот объём можно увеличить, изменив настройку страниц Translation Table Manager (TTM) ядра, следуя приведённым ниже инструкциям. AMD рекомендует установить минимальный объём выделенной VRAM в BIOS (0,5 ГБ).

* Установите утилиту pipx и добавьте путь к установленным через pipx пакетам в системный путь поиска.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Установите пакет amd-debug-tools из PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустите утилиту amd-ttm, чтобы узнать текущие настройки общей памяти.
  ```bash
  amd-ttm
  ```

* Измените настройки общей памяти на **120 ГБ**:
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

Для этого практикума требуются четыре устройства Ryzen AI Halo и один коммутатор Ethernet, подключённые по топологии «звезда», при этом каждое устройство напрямую соединено с коммутатором.

| Компонент | Количество | Описание |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Вычислительные узлы, образующие кластер |
| Коммутатор Ethernet 10 Гбит/с | 1 | Центральный коммутатор для обеспечения связи между несколькими узлами Ryzen AI Halo (не менее 4 портов) |
| Кабель Ethernet | 4 | Соединяет каждое устройство Halo с коммутатором (рекомендуется кабель Cat 7 или выше) |

> **Примечание**: Для подключения четырёх устройств Ryzen AI Halo требуется четыре порта коммутатора Ethernet. Пятый порт необходим, если вы обращаетесь к модели с отдельной клиентской машины, а не с одного из устройств Halo.

### Программное обеспечение
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Установите:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) с компонентом **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Физическая настройка оборудования

> **Примечание**: Выполните этот шаг на всех четырёх машинах (с Машины 1 по Машину 4).

Подключите каждое устройство Ryzen AI Halo к коммутатору Ethernet с помощью кабеля Cat 7 (или выше). Это обеспечивает соединение на 10 Гбит/с, используемое для высокоскоростной связи между узлами.
<!-- @os:linux -->
### 1. Определение сетевых интерфейсов

На каждой машине найдите имя её сетевого интерфейса и запишите его (далее оно будет называться `IFNAME`). Выполните:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Эта команда напрямую выводит имя интерфейса, например:

```bash
enp191s0
```

### 2. Проверка скорости сетевого соединения

Убедитесь, что соединение активно и работает на полной скорости, проверив скорость вашего интерфейса:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примечание**: Замените `<IFNAME>` на имя выходного интерфейса из раздела [1. Определение сетевых интерфейсов](#1-определение-сетевых-интерфейсов)

Вы должны увидеть скорость `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примечание**: Если скорость ниже `10000Mb/s` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и задать скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Проверка скорости сетевого соединения

На каждой машине проверьте скорость соединения сетевых интерфейсов:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш интерфейс Ethernet должен находиться в состоянии `Up` и работать на скорости `10 Гбит/с`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примечание**: Если скорость ниже `10 Гбит/с` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и задать скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

## Установка llama.cpp

> **Примечание**: Выполните этот шаг на всех четырёх машинах (с Машины 1 по Машину 4).

Доступны два варианта установки:

- [Вариант 1: Lemonade SDK (рекомендуется)](#option-1-lemonade-sdk-recommended) — готовые бинарные файлы, самая быстрая установка
- [Вариант 2: сборка из исходного кода вручную](#option-2-manual-source-build) — сборка из исходного кода с полным контролем над флагами сборки
### Вариант 1: Lemonade SDK (рекомендуется)

Lemonade SDK предоставляет ежедневные сборки llama.cpp с ускорением AMD ROCm 7, предназначенные для таких GPU, как gfx1151 (Strix Halo / Ryzen AI Max+ 395), и других современных архитектур Radeon.

<!-- @os:windows -->
#### Шаг 1. Загрузка предварительно собранных бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Шаг 2. Распаковка бинарных файлов

Распакуйте загруженный архив:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Теперь этот каталог содержит сборки `llama-cli.exe`, `llama-server.exe` и `ggml-rpc-server.exe` с поддержкой ROCm, скомпилированные для вашей системы Ryzen AI Halo.

#### Шаг 3. Проверка обнаружения GPU

```bash
.\llama-cli.exe --list-devices
```

Ожидаемый вывод:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Шаг 1. Загрузка предварительно собранных бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Шаг 2. Распаковка и подготовка бинарных файлов

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Теперь этот каталог содержит сборки `llama-cli`, `llama-server` и `rpc-server` с поддержкой ROCm, скомпилированные для вашей системы Ryzen AI Halo.

#### Шаг 3. Проверка обнаружения GPU

```bash
./llama-cli --list-devices
```

Ожидаемый вывод:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).

### Вариант 2: Сборка из исходного кода вручную

<!-- @os:windows -->
#### Шаг 1. Сборка llama.cpp

Откройте **x64 Native Tools Command Prompt** (устанавливается вместе с Visual Studio Build Tools) и клонируйте репозиторий:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Добавьте HIP в переменную PATH и выполните сборку с поддержкой ROCm и RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm/HIP |
| `-DGGML_RPC=ON` | Включает RPC для распределённого вывода |
| `-DGPU_TARGETS=gfx1151` | Нацеливает сборку на GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Использует систему сборки Ninja |

#### Шаг 2. Проверка обнаружения GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Ожидаемый вывод:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Шаг 3. Добавление HIP в пользовательский PATH

Шаг сборки выше устанавливал `%HIP_PATH%\bin` только для текущей сессии. Чтобы сделать библиотеки HIP доступными в любом терминале (а не только в x64 Native Tools Command Prompt), добавьте этот путь в пользовательскую переменную `PATH` на постоянной основе:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Шаг 1. Сборка llama.cpp

Клонируйте репозиторий:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Выполните сборку с поддержкой ROCm и RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm |
| `-DGGML_RPC=ON` | Включает RPC для распределённого вывода |
| `-DAMDGPU_TARGETS="gfx1151"` | Нацеливает сборку на GPU Ryzen AI Halo (Radeon 8060s) |

Дополнительные параметры сборки см. в [документации по сборке llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Шаг 2. Проверка обнаружения GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Ожидаемый вывод:

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

В этом руководстве используется модель [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) в квантизации `UD-Q2_K_XL` от [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Эта квантизация помещается в суммарную память GPU четырёх узлов Ryzen AI Halo.

Загрузите файлы GGUF с помощью Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Примечание**: загрузка модели должна выполняться на машине 1 (контроллере). Рабочим узлам RPC (машины 2, 3 и 4) локальная копия файлов модели не требуется.

## Запуск модели на кластере

Движок llama.cpp RPC (Remote Procedure Call) позволяет одному экземпляру llama.cpp передавать слои модели удалённым рабочим узлам по сети. Одна машина выступает в роли **контроллера** (машина 1), выполняя токенизацию, планирование и оркестрацию. На каждой из остальных трёх машин (машины 2, 3 и 4) запускается лёгкий **RPC-сервер**, предоставляющий контроллеру доступ к памяти и вычислительным ресурсам своего GPU.

Во время загрузки llama.cpp распределяет модель по всем четырём узлам. После загрузки вывод выполняется так, как если бы он выполнялся на одном ускорителе. RPC незаметно для пользователя обеспечивает передачу тензоров и синхронизацию.

### Шаг 1. Запуск RPC-серверов (машины 2, 3 и 4)

На каждой из машин 2, 3 и 4 запустите RPC-сервер, чтобы предоставить контроллеру доступ к ресурсам GPU:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Флаг | Назначение |
|------|---------|
| `-p` | Порт, на котором транслируется RPC-сервер |
| `-c` | Включает локальный кэш для больших тензоров, избегая повторной передачи данных по сети при загрузке модели |
| `--host` | IP-адрес, на который привязывается RPC-сервер (`0.0.0.0` для всех интерфейсов) |

Дополнительные параметры см. в [документации по RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Шаг 2. Запуск модели (машина 1)

После запуска RPC-серверов на машинах 2, 3 и 4 запустите вывод с машины 1, используя либо `llama-cli`, либо `llama-server`.
#### llama-cli

`llama-cli` предоставляет терминальный интерфейс для прямого взаимодействия с моделью. Он идеально подходит для бенчмаркинга, отладки и низкоуровневых экспериментов.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Поиск `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: выполните эту команду в терминале (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Поиск `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.

<!-- @os:end -->

После запуска `llama-cli` отображает процесс загрузки модели и открывает интерактивное приглашение, в котором можно напрямую общаться с моделью:

![llama-cli, работающий с Kimi K2.6 на четырёх узлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` предоставляет тот же механизм инференса через постоянно работающий серверный процесс со встроенным веб-интерфейсом и HTTP API, совместимым с OpenAI. Это предпочтительный интерфейс для долгоживущих развёртываний, многопользовательского доступа и интеграции с внешними инструментами.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Поиск `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: выполните эту команду в терминале (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Поиск `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

После запуска откройте `http://<HOST_IP>:8081` в браузере, чтобы получить доступ к встроенному веб-интерфейсу. Он предоставляет браузерный интерфейс чата для взаимодействия с моделью:

![Веб-интерфейс llama-server, работающий с Kimi K2.6 на четырёх узлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Поиск `<HOST_IP>`**: на машине 1 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Поиск `<HOST_IP>`**: на машине 1 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

#### Справочник параметров

| Флаг | Назначение |
|------|---------|
| `-m` | Путь к файлу модели GGUF (используйте первый шард, `00001-of-00008`) |
| `-c` | Размер контекста в токенах. Большие значения используют больше памяти |
| `-fa on` | Включает rocWMMA Flash Attention для повышения производительности на AMD GPU |
| `-ngl 999` | Выгружает все слои модели на GPU |
| `-lm none` | Устанавливает режим загрузки модели `none`, отключая отображение памяти (memory-mapping) для сокращения времени загрузки, когда размер модели превышает объём системной RAM, но помещается в VRAM |
| `-b` | Логический размер пакета (batch) в токенах. Значение 4096 обеспечивает баланс между пропускной способностью и использованием памяти на узлах |
| `-ub` | Физический (микро) размер пакета для обработки запроса. Совпадение с `-b` позволяет избежать лишних накладных расходов на разбиение на части |
| `--host` | IP-адрес, к которому привязывается `llama-server` (только для `llama-server`) |
| `--port` | Порт для предоставления HTTP API (только для `llama-server`) |
| `--rpc` | Список конечных точек RPC-воркеров, разделённых запятыми (`IP:port`) |

Полное описание параметров см. в [документации llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) и [документации llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Дальнейшие шаги

- **Подключение сторонних приложений**: `llama-server` предоставляет API, совместимый с OpenAI. Укажите в любом совместимом с OpenAI приложении (например, Open WebUI) адрес `http://<HOST_IP>:8081` с любым произвольным API-ключом (например, `none`), чтобы подключиться к вашему кластеру
- **Изучение других моделей**: просмотрите квантованные GGUF-модели на [Hugging Face](https://huggingface.co/models?search=gguf), чтобы найти модели, которые помещаются в суммарный объём памяти GPU вашего кластера
- **Масштабирование за пределы четырёх узлов**: добавьте дополнительные системы Ryzen AI Halo в качестве дополнительных RPC-воркеров, чтобы получить доступ к моделям с числом параметров свыше 1 триллиона. Передайте дополнительные конечные точки в `--rpc` в виде списка, разделённого запятыми (например, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)