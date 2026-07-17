<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Кластеризация двух Ryzen™ AI Halo с помощью RPC

## Обзор

Ваш Ryzen™ AI Halo уже способен запускать большие языковые модели локально. Кластеризация расширяет эти возможности, объединяя GPU-память нескольких систем через локальную сеть и открывая доступ к ещё более крупным моделям с улучшенными возможностями рассуждения, генерации кода и многоязычного понимания — и всё это исключительно на вашем собственном оборудовании.

Этот сборник инструкций научит вас, как объединить в кластер две системы Ryzen AI Halo с помощью RPC-движка llama.cpp и запустить GLM 4.7 — модель с 358 миллиардами параметров — на обеих машинах с ускорением AMD ROCm™.

## Что вы узнаете

- Как расширить выделение VRAM на системах Ryzen AI Halo
- Установка llama.cpp с поддержкой ROCm и RPC
- Настройка RPC-воркера и запуск распределённого инференса на двух узлах
- Запуск модели с 358 миллиардами параметров на двух объединённых в сеть системах Ryzen AI Halo

## Настройка конфигурации памяти

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

<!-- @os:windows -->
В Windows для запуска более крупных моделей, требующих большего объёма памяти, необходимо использовать выделение AMD Variable Graphics Memory (iGPU VRAM).

Это можно сделать, открыв панель управления AMD Software: Adrenalin Edition и перейдя по пути: `Performance > Tuning > AMD Variable Graphics Memory`. Установите значение **96 ГБ**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
В Linux ROCm использует общий пул системной памяти, который по умолчанию настроен на половину объёма системной памяти.

Этот объём можно увеличить, изменив настройку страниц Translation Table Manager (TTM) ядра, следуя приведённым ниже инструкциям. AMD рекомендует установить минимальный выделенный VRAM в BIOS (0,5 ГБ).

* Установите утилиту pipx и добавьте путь для колёс, установленных pipx, в системный путь поиска.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Установите колесо amd-debug-tools из PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустите инструмент amd-ttm для просмотра текущих настроек общей памяти.
  ```bash
  amd-ttm
  ```

* Перенастройте параметры общей памяти на **120 ГБ**:
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

Для этого сборника инструкций требуются два устройства Ryzen AI Halo и один коммутатор Ethernet, соединённые в топологии «звезда», где каждое устройство подключено напрямую к коммутатору.

| Компонент | Количество | Описание |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Вычислительные узлы, образующие кластер |
| Коммутатор Ethernet 10 Гбит/с | 1 | Центральный коммутатор для обеспечения связи между узлами Ryzen AI Halo (не менее 2 портов) |
| Кабель Ethernet | 2 | Подключает каждое устройство Halo к коммутатору (рекомендуется Cat 7 или выше) |

> **Примечание**: Для подключения двух устройств Ryzen AI Halo требуются два порта коммутатора Ethernet. Третий порт необходим, если вы обращаетесь к модели с отдельной клиентской машины, а не с одного из устройств Halo.

### Программное обеспечение
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Пожалуйста, установите:
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

## Физическая настройка оборудования

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

Подключите каждое устройство Ryzen AI Halo к коммутатору Ethernet с помощью кабеля Cat 7 (или выше). Это обеспечивает канал 10 Гбит/с для высокоскоростной связи между узлами.
<!-- @os:linux -->
### 1. Определение сетевых интерфейсов

На каждой машине найдите имя её сетевого интерфейса и запишите его (ниже оно будет обозначаться как `IFNAME`). Выполните:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Команда выводит имя интерфейса напрямую, например:

```bash
enp191s0
```

### 2. Проверка скоростей сетевого соединения

Убедитесь, что соединение активно и работает на полной скорости, проверив скорость вашего интерфейса:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примечание**: Замените `<IFNAME>` именем интерфейса, полученным в разделе [1. Определение сетевых интерфейсов](#1-determine-network-interfaces)

Вы должны увидеть скорость `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примечание**: Если скорость ниже `10000Mb/s` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. На некоторых коммутаторах может потребоваться отключить автосогласование и задать скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Проверка скорости сетевого соединения

На каждой машине проверьте скорость соединения ваших сетевых интерфейсов:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш интерфейс Ethernet должен быть в состоянии `Up` и работать на скорости `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примечание**: Если скорость ниже `10 Gbps` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. На некоторых коммутаторах может потребоваться отключить автосогласование и задать скорость соединения вручную; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

## Установка llama.cpp

> **Примечание**: Выполните этот шаг на обеих машинах — Machine 1 и Machine 2.

Доступны два варианта установки:

- [Вариант 1: Lemonade SDK (рекомендуется)](#option-1-lemonade-sdk-recommended) — готовые бинарные файлы, быстрейшая настройка
- [Вариант 2: Сборка из исходного кода вручную](#option-2-manual-source-build) — сборка из исходников с полным контролем над флагами сборки

### Вариант 1: Lemonade SDK (рекомендуется)

Lemonade SDK предоставляет ночные сборки llama.cpp с ускорением AMD ROCm 7, ориентированные на GPU такие как gfx1151 (Strix Halo / Ryzen AI Max+ 395) и другие современные архитектуры Radeon.

<!-- @os:windows -->
#### Шаг 1: Загрузка готовых бинарных файлов

Перейдите на страницу последнего релиза и загрузите архив, соответствующий вашей платформе и целевому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Загрузите файл с именем `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (где `xxxx` — номер сборки).

#### Шаг 2: Извлечение бинарных файлов

Распакуйте загруженный архив:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Этот каталог теперь содержит сборки `llama-cli.exe`, `llama-server.exe` и `rpc-server.exe` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

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

#### Шаг 2: Извлечение и подготовка бинарных файлов

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Этот каталог теперь содержит сборки `llama-cli`, `llama-server` и `rpc-server` с поддержкой ROCm, предварительно скомпилированные для вашей системы Ryzen AI Halo.

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
После подготовки llama.cpp на каждом узле перейдите к разделу [Загрузка модели](#downloading-the-model).

### Вариант 2: Сборка из исходного кода вручную

<!-- @os:windows -->
#### Шаг 1: Сборка llama.cpp

Откройте **x64 Native Tools Command Prompt** (устанавливается вместе с Visual Studio Build Tools) и клонируйте репозиторий:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Добавьте HIP в ваш путь и выполните сборку с поддержкой ROCm и RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm/HIP |
| `-DGGML_RPC=ON` | Включает RPC для распределённого инференса |
| `-DGPU_TARGETS=gfx1151` | Нацелен на GPU Ryzen AI Halo (Radeon 8060s) |
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

#### Шаг 3: Добавление HIP в пользовательский PATH

Шаг сборки выше установил `%HIP_PATH%\bin` только для текущего сеанса. Чтобы библиотеки HIP были доступны в любом терминале (а не только в x64 Native Tools Command Prompt), добавьте их в пользовательский `PATH` постоянно:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

После подготовки llama.cpp на каждом узле перейдите к разделу [Загрузка модели](#downloading-the-model).
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
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Флаг сборки | Назначение |
|-----------|---------|
| `-DGGML_HIP=ON` | Включает программный стек ROCm |
| `-DGGML_RPC=ON` | Включает RPC для распределённого инференса |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Включает rocWMMA для улучшенного Flash Attention на GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Нацелен на GPU Ryzen AI Halo (Radeon 8060s) |

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

После подготовки llama.cpp на каждом узле перейдите к разделу [Загрузка модели](#downloading-the-model).
<!-- @os:end -->

## Загрузка модели

В этом сборнике инструкций используется [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) — модель с 358 миллиардами параметров в квантизации `Q4_K_XL` от [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). При данной квантизации модель требует около 205 ГБ дискового пространства и помещается в объединённую GPU-память двух узлов Ryzen AI Halo.

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

> **Примечание**: Загрузка модели должна быть выполнена на Machine 1 (контроллере). Узлам RPC-воркеров локальная копия файлов модели не нужна.

## Запуск модели на кластере

RPC-движок llama.cpp (Remote Procedure Call) позволяет одному экземпляру llama.cpp выгружать слои модели на удалённые воркеры по сети. Одна машина выступает в роли **контроллера** (Machine 1), обрабатывая токенизацию, планирование и оркестрацию. Другая машина запускает лёгкий **RPC-сервер** (Machine 2), предоставляющий контроллеру свою GPU-память и вычислительные ресурсы.

При загрузке llama.cpp разбивает модель на части между обоими узлами. После загрузки инференс выполняется так, как если бы он работал на одном ускорителе. RPC обрабатывает передачу тензоров и синхронизацию в фоновом режиме.

### Шаг 1: Запуск RPC-сервера (Machine 2)

На Machine 2 запустите RPC-сервер, чтобы предоставить контроллеру доступ к GPU-ресурсам:
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
| `-p` | Порт для трансляции RPC-сервера |
| `-c` | Включает локальный кэш для больших тензоров, избегая повторных сетевых передач при загрузке модели |
| `--host` | IP-адрес для привязки RPC-сервера (`0.0.0.0` для всех интерфейсов) |

Дополнительные параметры см. в [документации по RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Шаг 2: Запуск модели (Machine 1)

После запуска RPC-сервера на Machine 2 запустите инференс с Machine 1, используя `llama-cli` или `llama-server`.

#### llama-cli

`llama-cli` предоставляет терминальный интерфейс для непосредственного взаимодействия с моделью. Он идеально подходит для бенчмаркинга, отладки и низкоуровневых экспериментов.

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

> **Как найти `<RPC_WORKER_IP>`**: На Machine 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: Выполните эту команду в Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Как найти `<RPC_WORKER_IP>`**: На Machine 2 выполните `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), чтобы узнать её локальный IP-адрес.

<!-- @os:end -->

После запуска `llama-cli` отображает прогресс загрузки модели и переходит в интерактивный режим, где вы можете напрямую общаться с моделью:

![llama-cli, запускающий GLM 4.7 на двух узлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` предоставляет тот же движок инференса через постоянный серверный процесс со встроенным веб-интерфейсом и HTTP API, совместимым с OpenAI. Это предпочтительный интерфейс для длительных развёртываний, многопользовательского доступа и интеграции с внешними инструментами.

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

> **Как найти `<RPC_WORKER_IP>`**: На Machine 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: Выполните эту команду в Terminal (Powershell).

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

> **Как найти `<RPC_WORKER_IP>`**: На Machine 2 выполните `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

После запуска откройте `http://<HOST_IP>:8081` в браузере для доступа к встроенному веб-интерфейсу. Он предоставляет браузерный чат-интерфейс для взаимодействия с моделью:

![Веб-интерфейс llama-server, запускающий GLM 4.7 на двух узлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Как найти `<HOST_IP>`**: На Machine 1 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Как найти `<HOST_IP>`**: На Machine 1 выполните `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

#### Справочник по параметрам

| Флаг | Назначение |
|------|---------|
| `-m` | Путь к файлу модели GGUF (используйте первый фрагмент, `00001-of-00005`) |
| `-c` | Размер контекста в токенах. Большие значения требуют больше памяти |
| `-fa on` | Включает rocWMMA Flash Attention для повышения производительности на GPU AMD |
| `-ngl 999` | Выгружает все слои модели на GPU |
| `--no-mmap` | Отключает отображение памяти, сокращая время загрузки, когда размер модели превышает системную RAM, но помещается в VRAM |
| `--host` | IP для привязки `llama-server` (только для `llama-server`) |
| `--port` | Порт для обслуживания HTTP API (только для `llama-server`) |
| `--rpc` | Разделённый запятыми список конечных точек RPC-воркеров (`IP:порт`) |

Полное описание параметров см. в [документации llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) и [документации llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Следующие шаги

- **Подключение сторонних приложений**: `llama-server` предоставляет API, совместимый с OpenAI. Направьте любое совместимое с OpenAI приложение (например, Open WebUI) на `http://<HOST_IP>:8081` с любым API-ключом-заглушкой (например, `none`) для подключения к вашему кластеру
- **Изучение других моделей**: Просматривайте квантизованные GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), чтобы найти модели, помещающиеся в объединённую GPU-память вашего кластера
- **Масштабирование до четырёх узлов**: Добавьте ещё две системы Ryzen AI Halo в качестве дополнительных RPC-воркеров для доступа к моделям масштаба 1 триллиона параметров. Передайте дополнительные конечные точки в `--rpc` в виде списка, разделённого запятыми (например, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)