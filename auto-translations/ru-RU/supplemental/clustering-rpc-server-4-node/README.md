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

Ваш Ryzen™ AI Halo уже способен запускать большие языковые модели локально. Кластеризация выводит это на новый уровень, объединяя память GPU нескольких систем через локальную сеть, что даёт вам доступ к ещё более крупным моделям с более сильным рассуждением, лучшей генерацией кода и более глубоким пониманием многоязычного текста — и всё это полностью на вашем собственном оборудовании.

Этот playbook научит вас кластеризовать четыре системы Ryzen AI Halo с помощью RPC-движка llama.cpp и запускать Kimi K2.6, большую модель типа mixture-of-experts, на всех четырёх машинах с ускорением AMD ROCm™.

## Что вы узнаете

- Как расширить выделение VRAM на системах Ryzen AI Halo
- Установку llama.cpp с поддержкой ROCm и RPC
- Настройку RPC-воркеров и запуск распределённого инференса на четырёх узлах
- Запуск модели с 1 триллионом параметров на четырёх подключённых по сети системах Ryzen AI Halo

## Настройка конфигурации памяти

> **Примечание**: Выполните этот шаг на всех четырёх машинах (Машина 1 – Машина 4).

<!-- @os:windows -->
В Windows для запуска более крупных моделей, требующих больше памяти, необходимо использовать выделение AMD Variable Graphics Memory (iGPU VRAM).

Это можно сделать, открыв панель управления AMD Software: Adrenalin Edition и перейдя в: `Performance > Tuning > AMD Variable Graphics Memory`. Установите значение **96 GB**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
В Linux ROCm использует общий пул системной памяти, и по умолчанию этот пул настроен на половину объёма системной памяти.

Этот объём можно увеличить, изменив настройку страниц Translation Table Manager (TTM) ядра, следуя приведённым ниже инструкциям. AMD рекомендует установить минимальный выделенный объём VRAM в BIOS (0.5 GB).

* Установите утилиту pipx и добавьте путь к установленным через pipx пакетам в системный путь поиска.

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

* Переконфигурируйте настройки общей памяти на **120 GB**:
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

Для этого playbook требуется четыре устройства Ryzen AI Halo и один Ethernet-коммутатор, подключённые по топологии «звезда», где каждое устройство напрямую соединено с коммутатором.

| Компонент | Количество | Описание |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Вычислительные узлы, образующие кластер |
| Ethernet-коммутатор 10 Гбит/с | 1 | Центральный коммутатор для обеспечения связи между несколькими узлами Ryzen AI Halo (не менее 4 портов) |
| Ethernet-кабель | 4 | Соединяет каждое устройство Halo с коммутатором (рекомендуется Cat 7 или выше) |

> **Примечание**: Для подключения четырёх устройств Ryzen AI Halo требуется четыре порта Ethernet-коммутатора. Пятый порт требуется, если вы обращаетесь к модели с отдельной клиентской машины, а не с одного из устройств Halo.

### Программное обеспечение
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Установите:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) с рабочей нагрузкой **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Настройка физического оборудования

> **Примечание**: Выполните этот шаг на всех четырёх машинах (Машина 1 – Машина 4).

Подключите каждое устройство Ryzen AI Halo к Ethernet-коммутатору с помощью кабеля Cat 7 (или выше). Это устанавливает соединение на скорости 10 Гбит/с, используемое для высокоскоростной связи между узлами.
<!-- @os:linux -->
### 1. Определение сетевых интерфейсов

На каждой машине найдите имя её сетевого интерфейса и запишите его (далее оно будет упоминаться как `IFNAME`). Выполните:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Это напрямую выводит имя интерфейса, например:

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

> **Примечание**: Если скорость ниже `10000Mb/s` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и вручную установить скорость соединения; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Проверка скорости сетевого соединения

На каждой машине проверьте скорость соединения ваших сетевых интерфейсов:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш Ethernet-интерфейс должен иметь статус `Up` и работать на скорости `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примечание**: Если скорость ниже `10 Gbps` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и вручную установить скорость соединения; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

## Установка llama.cpp

> **Примечание**: Выполните этот шаг на всех четырёх машинах (Машина 1 – Машина 4).

Доступны два варианта установки:

- [Вариант 1: Lemonade SDK (рекомендуется)](#option-1-lemonade-sdk-recommended) — готовые бинарные файлы, самая быстрая настройка
- [Вариант 2: Ручная сборка из исходного кода](#option-2-manual-source-build) — сборка из исходного кода с полным контролем над флагами сборки

### Вариант 1: Lemonade SDK (рекомендуется)

Lemonade SDK предоставляет ночные сборки llama.cpp с ускорением AMD ROCm 7, ориентированные на GPU, такие как gfx1151 (Strix Halo / Ryzen AI Max+ 395) и другие современные архитектуры Radeon.

<!-- @os:windows -->
#### Шаг 1: Загрузка готовых бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Шаг 2: Распаковка бинарных файлов

Распакуйте загруженный архив:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Теперь этот каталог содержит сборки `llama-cli.exe`, `llama-server.exe` и `ggml-rpc-server.exe` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

#### Шаг 3: Проверка обнаружения GPU

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
#### Шаг 1: Загрузка готовых бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Шаг 2: Распаковка и подготовка бинарных файлов

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Теперь этот каталог содержит сборки `llama-cli`, `llama-server` и `rpc-server` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

#### Шаг 3: Проверка обнаружения GPU

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
#### Шаг 1: Сборка llama.cpp

Откройте **x64 Native Tools Command Prompt** (устанавливается вместе с Visual Studio Build Tools) и клонируйте репозиторий:

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
| `-DGGML_RPC=ON` | Включает RPC для распределённого инференса |
| `-DGPU_TARGETS=gfx1151` | Указывает целевой GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Использует систему сборки Ninja |

#### Шаг 2: Проверка обнаружения GPU

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

#### Шаг 3: Добавление HIP в пользовательский путь

Приведённый выше шаг сборки установил `%HIP_PATH%\bin` только для текущей сессии. Чтобы библиотеки HIP были доступны в любом терминале (а не только в x64 Native Tools Command Prompt), добавьте его в пользовательскую переменную `PATH` на постоянной основе:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

После подготовки llama.cpp на каждом узле переходите к разделу [Загрузка модели](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Шаг 1: Сборка llama.cpp

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
| `-DGGML_RPC=ON` | Включает RPC для распределённого инференса |
| `-DAMDGPU_TARGETS="gfx1151"` | Указывает целевой GPU Ryzen AI Halo (Radeon 8060s) |

Дополнительные параметры сборки см. в [документации по сборке llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Шаг 2: Проверка обнаружения GPU

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

В данном руководстве используется [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) в квантизации `UD-Q2_K_XL` от [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Эта квантизация помещается в суммарную видеопамять четырёх узлов Ryzen AI Halo.

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

> **Примечание**: загрузка модели должна выполняться на Машине 1 (контроллере). Рабочим узлам RPC (Машинам 2, 3 и 4) локальная копия файлов модели не требуется.

## Запуск модели в кластере

Механизм RPC (Remote Procedure Call) в llama.cpp позволяет одному экземпляру llama.cpp выгружать слои модели на удалённые рабочие узлы по сети. Одна машина выступает в роли **контроллера** (Машина 1), выполняя токенизацию, планирование и оркестрацию. Три остальные машины (Машины 2, 3 и 4) запускают лёгкий **RPC-сервер**, который предоставляет свою видеопамять и вычислительные ресурсы контроллеру.

В момент загрузки llama.cpp распределяет модель по всем четырём узлам. После загрузки инференс выполняется так, как будто он работает на одном ускорителе. RPC незаметно для пользователя обрабатывает передачу тензоров и синхронизацию.

### Шаг 1: Запуск RPC-серверов (Машины 2, 3 и 4)

На каждой из Машин 2, 3 и 4 запустите RPC-сервер, чтобы предоставить контроллеру доступ к её ресурсам GPU:
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
| `-c` | Включает локальный кэш для больших тензоров, что позволяет избежать повторных передач по сети при загрузке модели |
| `--host` | IP-адрес, к которому привязывается RPC-сервер (`0.0.0.0` для всех интерфейсов) |

Дополнительные параметры см. в [документации по RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Шаг 2: Запуск модели (Машина 1)

После запуска RPC-серверов на Машинах 2, 3 и 4 запустите инференс с Машины 1 с помощью `llama-cli` или `llama-server`.
#### llama-cli

`llama-cli` предоставляет терминальный интерфейс для прямого взаимодействия с моделью. Он идеально подходит для бенчмаркинга, отладки и низкоуровневого экспериментирования.

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

> **Определение `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
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

> **Определение `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.

<!-- @os:end -->

После запуска `llama-cli` отображает ход загрузки модели и переходит в интерактивный режим, в котором можно напрямую общаться с моделью:

![llama-cli, работающий с Kimi K2.6 на четырёх узлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` предоставляет тот же движок инференса через постоянный серверный процесс со встроенным веб-интерфейсом и HTTP API, совместимым с OpenAI. Это предпочтительный интерфейс для длительных развертываний, доступа нескольких пользователей и интеграции с внешними инструментами.

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

> **Определение `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
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

> **Определение `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на каждой из машин 2, 3 и 4 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

После запуска откройте `http://<HOST_IP>:8081` в браузере, чтобы получить доступ к встроенному веб-интерфейсу. Он предоставляет браузерный чат-интерфейс для взаимодействия с моделью:

![Веб-интерфейс llama-server, работающий с Kimi K2.6 на четырёх узлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Определение `<HOST_IP>`**: на машине 1 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Определение `<HOST_IP>`**: на машине 1 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

#### Справочник по параметрам

| Флаг | Назначение |
|------|---------|
| `-m` | Путь к файлу модели GGUF (используйте первый шард, `00001-of-00008`) |
| `-c` | Размер контекста в токенах. Большие значения используют больше памяти |
| `-fa on` | Включает rocWMMA Flash Attention для повышения производительности на GPU AMD |
| `-ngl 999` | Выгружает все слои модели на GPU |
| `-lm none` | Устанавливает режим загрузки модели `none`, отключая отображение в память (memory-mapping) для сокращения времени загрузки, если размер модели превышает объём системной ОЗУ, но помещается в VRAM |
| `-b` | Логический размер пакета в токенах. Установка значения 4096 обеспечивает баланс между пропускной способностью и использованием памяти на узлах |
| `-ub` | Физический (микро) размер пакета для обработки промпта. Совпадение с `-b` позволяет избежать лишних накладных расходов на разбиение |
| `--host` | IP-адрес для привязки `llama-server` (только для `llama-server`) |
| `--port` | Порт для предоставления HTTP API (только для `llama-server`) |
| `--rpc` | Список конечных точек RPC-воркеров через запятую (`IP:port`) |

Полное описание использования параметров см. в [документации llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) и [документации llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Дальнейшие шаги

- **Подключение сторонних приложений**: `llama-server` предоставляет API, совместимый с OpenAI. Направьте любое совместимое с OpenAI приложение (например, Open WebUI) на `http://<HOST_IP>:8081` с произвольным заполнительным API-ключом (например, `none`), чтобы подключиться к вашему кластеру
- **Изучение других моделей**: просмотрите квантованные GGUF-модели на [Hugging Face](https://huggingface.co/models?search=gguf), чтобы найти модели, которые помещаются в суммарную память GPU вашего кластера
- **Масштабирование за пределы четырёх узлов**: добавьте дополнительные системы Ryzen AI Halo в качестве дополнительных RPC-воркеров, чтобы получить доступ к моделям масштаба свыше 1 триллиона параметров. Передайте дополнительные конечные точки в `--rpc` в виде списка через запятую (например, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)