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

# Кластеризация двух Ryzen™ AI Halo с помощью RPC

## Обзор

Ваш Ryzen™ AI Halo уже способен локально запускать большие языковые модели. Кластеризация выводит это на новый уровень, объединяя объём памяти GPU нескольких систем по локальной сети, что даёт доступ к ещё более крупным моделям с более сильным логическим мышлением, лучшей генерацией кода и более глубоким пониманием многоязычных текстов — и всё это полностью на вашем собственном оборудовании.

Это руководство научит вас кластеризовать две системы Ryzen AI Halo с помощью RPC-движка llama.cpp и запустить GLM 4.7, модель с 358 млрд параметров, на обеих машинах с ускорением AMD ROCm™.

## Чему вы научитесь

- Расширению выделения VRAM на системах Ryzen AI Halo
- Установке llama.cpp с поддержкой ROCm и RPC
- Настройке RPC-воркера и запуску распределённого инференса на двух узлах
- Запуску модели с 358 млрд параметров на двух объединённых в сеть системах Ryzen AI Halo

## Настройка конфигурации памяти

> **Примечание**: выполните этот шаг как на Машине 1, так и на Машине 2.

<!-- @os:windows -->
В Windows для запуска более крупных моделей, требующих больше памяти, необходимо использовать выделение AMD Variable Graphics Memory (VRAM iGPU).

Это можно сделать, открыв панель управления AMD Software: Adrenalin Edition и перейдя в: `Performance > Tuning > AMD Variable Graphics Memory`. Установите значение **96 ГБ**. Перезагрузите систему, чтобы изменения вступили в силу.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
В Linux ROCm использует общий пул системной памяти, и по умолчанию этот пул настроен на половину объёма системной памяти.

Этот объём можно увеличить, изменив настройку страниц Translation Table Manager (TTM) в ядре, следуя приведённым ниже инструкциям. AMD рекомендует установить минимальный выделенный объём VRAM в BIOS (0,5 ГБ).

* Установите утилиту pipx и добавьте путь к установленным через pipx wheel-пакетам в системный путь поиска.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Установите wheel-пакет amd-debug-tools из PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустите утилиту amd-ttm, чтобы узнать текущие настройки общей памяти.
  ```bash
  amd-ttm
  ```

* Переконфигурируйте настройки общей памяти на **120 ГБ**:
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

### Аппаратное обеспечение

Для этого руководства требуются два блока Ryzen AI Halo и один Ethernet-коммутатор, соединённые по топологии «звезда» с подключением каждого блока напрямую к коммутатору.

| Компонент | Количество | Описание |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Вычислительные узлы, образующие кластер |
| 10-гигабитный Ethernet-коммутатор | 1 | Центральный коммутатор, обеспечивающий связь между узлами Ryzen AI Halo (не менее 2 портов) |
| Ethernet-кабель | 2 | Соединяет каждый блок Halo с коммутатором (рекомендуется Cat 7 или выше) |

> **Примечание**: для подключения двух блоков Ryzen AI Halo требуются два порта Ethernet-коммутатора. Третий порт нужен, если вы обращаетесь к модели с отдельной клиентской машины, а не с одного из блоков Halo.

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

## Физическая настройка оборудования

> **Примечание**: выполните этот шаг как на Машине 1, так и на Машине 2.

Подключите каждый блок Ryzen AI Halo к Ethernet-коммутатору с помощью кабеля Cat 7 (или выше). Это устанавливает 10-гигабитное соединение, используемое для высокоскоростной связи между узлами.
<!-- @os:linux -->
### 1. Определение сетевых интерфейсов

На каждой машине определите имя её сетевого интерфейса и запишите его (далее оно будет упоминаться как `IFNAME`). Выполните:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Это выводит имя интерфейса напрямую, например:

```bash
enp191s0
```

### 2. Проверка скорости сетевого соединения

Убедитесь, что соединение активно и работает на полной скорости, проверив скорость вашего интерфейса:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примечание**: замените `<IFNAME>` на имя выходного интерфейса из раздела [1. Определение сетевых интерфейсов](#1-определение-сетевых-интерфейсов)

Вы должны увидеть скорость `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примечание**: если скорость ниже `10000Mb/s` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и вручную задать скорость соединения; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Проверка скорости сетевого соединения

На каждой машине проверьте скорость соединения ваших сетевых интерфейсов:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш Ethernet-интерфейс должен быть в состоянии `Up` и работать на скорости `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примечание**: если скорость ниже `10 Gbps` или соединение не устанавливается, проверьте подключение кабеля и убедитесь, что порт коммутатора настроен на 10 Гбит/с. Некоторым коммутаторам требуется отключить автосогласование и вручную задать скорость соединения; обратитесь к документации вашего коммутатора.

<!-- @os:end -->

## Установка llama.cpp

> **Примечание**: выполните этот шаг как на Машине 1, так и на Машине 2.

Доступны два варианта установки:

- [Вариант 1: Lemonade SDK (рекомендуется)](#option-1-lemonade-sdk-recommended) — готовые бинарные файлы, самая быстрая настройка
- [Вариант 2: Ручная сборка из исходников](#option-2-manual-source-build) — сборка из исходного кода с полным контролем над флагами сборки

### Вариант 1: Lemonade SDK (рекомендуется)

Lemonade SDK предоставляет ночные сборки llama.cpp с ускорением AMD ROCm 7, нацеленные на такие GPU, как gfx1151 (Strix Halo / Ryzen AI Max+ 395) и другие современные архитектуры Radeon.

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

Теперь эта директория содержит сборки `llama-cli.exe`, `llama-server.exe` и `rpc-server.exe` с поддержкой ROCm, скомпилированные для вашей системы Ryzen AI Halo.

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

Теперь эта директория содержит сборки `llama-cli`, `llama-server` и `rpc-server` с поддержкой ROCm, скомпилированные для вашей системы Ryzen AI Halo.

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

### Вариант 2: Ручная сборка из исходного кода

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
| `-DGPU_TARGETS=gfx1151` | Целевой GPU — Ryzen AI Halo (Radeon 8060s) |
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

Приведённый выше шаг сборки установил `%HIP_PATH%\bin` только для текущей сессии. Чтобы сделать библиотеки HIP доступными в любом терминале (а не только в x64 Native Tools Command Prompt), добавьте его в пользовательский `PATH` на постоянной основе:

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
| `-DAMDGPU_TARGETS="gfx1151"` | Целевой GPU — Ryzen AI Halo (Radeon 8060s) |

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

В этом руководстве используется [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) — модель с 358 миллиардами параметров в квантовании `Q4_K_XL` от [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). При таком квантовании модели требуется примерно 205 ГБ хранилища, и она умещается в объединённой памяти GPU двух узлов Ryzen AI Halo.

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

> **Примечание**: загрузка модели должна быть выполнена на Машине 1 (контроллере). Узлам-обработчикам RPC не требуется локальная копия файлов модели.

## Запуск модели в кластере

Движок RPC (Remote Procedure Call) llama.cpp позволяет одному экземпляру llama.cpp выгружать слои модели на удалённые обработчики по сети. Одна машина выступает в роли **контроллера** (Машина 1), выполняя токенизацию, планирование и оркестрацию. Другая машина запускает лёгкий **RPC-сервер** (Машина 2), который предоставляет контроллеру доступ к своей памяти GPU и вычислительным ресурсам.

Во время загрузки llama.cpp разбивает модель между обоими узлами. После загрузки инференс выполняется так, как если бы он работал на одном ускорителе. RPC незаметно для пользователя обрабатывает передачу тензоров и синхронизацию.

### Шаг 1: Запуск RPC-сервера (Машина 2)

На Машине 2 запустите RPC-сервер, чтобы предоставить контроллеру доступ к её ресурсам GPU:
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
| `-p` | Порт, через который транслируется RPC-сервер |
| `-c` | Включает локальный кэш для больших тензоров, избегая повторных сетевых передач во время загрузки модели |
| `--host` | IP-адрес для привязки RPC-сервера (`0.0.0.0` для всех интерфейсов) |

Дополнительные параметры см. в [документации по RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Шаг 2: Запуск модели (Машина 1)

После того как RPC-сервер запущен на Машине 2, запустите инференс с Машины 1, используя `llama-cli` или `llama-server`.

#### llama-cli

`llama-cli` предоставляет терминальный интерфейс для прямого взаимодействия с моделью. Он идеально подходит для бенчмаркинга, отладки и низкоуровневых экспериментов.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **Поиск `<RPC_WORKER_IP>`**: на Машине 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: выполните эту команду в терминале (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Поиск `<RPC_WORKER_IP>`**: на Машине 2 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.

<!-- @os:end -->

После запуска `llama-cli` отображает прогресс загрузки модели и переходит в интерактивный режим, где вы можете напрямую общаться с моделью:

![llama-cli, запускающий GLM 4.7 на двух узлах](assets/llama-cli-example.png)
#### llama-server

`llama-server` предоставляет тот же движок вывода через постоянный серверный процесс со встроенным веб-интерфейсом и HTTP API, совместимым с OpenAI. Это предпочтительный интерфейс для долгосрочных развёртываний, многопользовательского доступа и интеграции с внешними инструментами.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: на Машине 2 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: выполните эту команду в терминале (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Определение `<RPC_WORKER_IP>`**: на Машине 2 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

После запуска откройте `http://<HOST_IP>:8081` в браузере, чтобы получить доступ к встроенному веб-интерфейсу. Он предоставляет браузерный интерфейс чата для взаимодействия с моделью:

![Веб-интерфейс llama-server с моделью GLM 4.7, запущенной на двух узлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Определение `<HOST_IP>`**: на Машине 1 выполните `hostname -I | awk '{print $1}'`, чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

<!-- @os:windows -->
> **Определение `<HOST_IP>`**: на Машине 1 выполните `ipconfig | findstr /C:"IPv4"` в терминале (Powershell), чтобы узнать её локальный IP-адрес.
<!-- @os:end -->

#### Справочник параметров

| Флаг | Назначение |
|------|---------|
| `-m` | Путь к файлу модели GGUF (используйте первый шард, `00001-of-00005`) |
| `-c` | Размер контекста в токенах. Большие значения используют больше памяти |
| `-fa on` | Включает rocWMMA Flash Attention для повышения производительности на GPU AMD |
| `-ngl 999` | Выгружает все слои модели на GPU |
| `-lm none` | Устанавливает режим загрузки модели `none`, отключая отображение в память (memory-mapping) для сокращения времени загрузки, когда размер модели превышает объём системной ОЗУ, но помещается в VRAM |
| `--host` | IP-адрес, к которому привязывается `llama-server` (только для `llama-server`) |
| `--port` | Порт для обслуживания HTTP API (только для `llama-server`) |
| `--rpc` | Список конечных точек RPC-воркеров через запятую (`IP:port`) |

Полное описание параметров см. в [документации llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) и [документации llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Дальнейшие шаги

- **Подключение сторонних приложений**: `llama-server` предоставляет API, совместимый с OpenAI. Укажите в любом приложении, совместимом с OpenAI (например, Open WebUI), адрес `http://<HOST_IP>:8081` и любой произвольный API-ключ (например, `none`), чтобы подключиться к вашему кластеру
- **Изучение других моделей**: просмотрите квантованные модели GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), чтобы найти модели, помещающиеся в общий объём памяти GPU вашего кластера
- **Масштабирование до четырёх узлов**: добавьте ещё две системы Ryzen AI Halo в качестве дополнительных RPC-воркеров, чтобы получить доступ к моделям масштаба 1 триллиона параметров. Передайте дополнительные конечные точки в `--rpc` в виде списка через запятую (например, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)