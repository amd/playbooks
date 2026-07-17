<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Кластеризація двох Ryzen™ AI Halo за допомогою RPC

## Огляд

Ваш Ryzen™ AI Halo вже здатний запускати великі мовні моделі локально. Кластеризація розширює ці можливості, об'єднуючи GPU пам'ять кількох систем через локальну мережу, надаючи вам доступ до ще більших моделей із потужнішим міркуванням, кращою генерацією коду та глибшим багатомовним розумінням — і все це виключно на вашому власному обладнанні.

Цей посібник навчить вас, як об'єднати дві системи Ryzen AI Halo у кластер за допомогою RPC-рушія llama.cpp та запустити GLM 4.7 — модель із 358 мільярдами параметрів — на обох машинах із прискоренням AMD ROCm™.

## Що ви дізнаєтесь

- Як розширити виділення VRAM на системах Ryzen AI Halo
- Встановлення llama.cpp із підтримкою ROCm та RPC
- Налаштування RPC-воркера та запуск розподіленого інференсу на двох вузлах
- Запуск моделі з 358 мільярдами параметрів на двох об'єднаних у мережу системах Ryzen AI Halo

## Налаштування конфігурації пам'яті

> **Примітка**: Виконайте цей крок на обох машинах — Machine 1 і Machine 2.

<!-- @os:windows -->
У Windows для запуску більших моделей, що потребують більшого обсягу пам'яті, необхідно використовувати виділення AMD Variable Graphics Memory (iGPU VRAM).

Це можна зробити, відкривши панель керування AMD Software: Adrenalin Edition і перейшовши до: `Performance > Tuning > AMD Variable Graphics Memory`. Встановіть значення **96 GB**. Будь ласка, перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
У Linux ROCm використовує спільний пул системної пам'яті, який за замовчуванням налаштований на половину системної пам'яті.

Цей обсяг можна збільшити, змінивши налаштування сторінки Translation Table Manager (TTM) ядра, дотримуючись наведених нижче інструкцій. AMD рекомендує встановити мінімальний виділений VRAM у BIOS (0.5 GB).

* Встановіть утиліту pipx і додайте шлях для встановлених pipx пакетів до системного шляху пошуку.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Встановіть пакет amd-debug-tools з PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустіть інструмент amd-ttm для перегляду поточних налаштувань спільної пам'яті.
  ```bash
  amd-ttm
  ```

* Перенастройте параметри спільної пам'яті на **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Перезавантажте систему, щоб зміни набули чинності.


<!-- @os:end -->
<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->
## Передумови

### Обладнання

Для цього посібника потрібні два пристрої Ryzen AI Halo та один комутатор Ethernet, з'єднані у топології «зірка», де кожен пристрій підключений безпосередньо до комутатора.

| Компонент | Кількість | Опис |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Обчислювальні вузли, що утворюють кластер |
| Комутатор Ethernet 10 Гбіт/с | 1 | Центральний комутатор для забезпечення зв'язку між вузлами Ryzen AI Halo (щонайменше 2 порти) |
| Кабель Ethernet | 2 | З'єднує кожен пристрій Halo з комутатором (рекомендується Cat 7 або вище) |

> **Примітка**: Для підключення двох пристроїв Ryzen AI Halo потрібні два порти комутатора Ethernet. Третій порт потрібен, якщо ви звертаєтесь до моделі з окремої клієнтської машини, а не з одного з пристроїв Halo.

### Програмне забезпечення
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Будь ласка, встановіть:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) із робочим навантаженням **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Фізичне налаштування обладнання

> **Примітка**: Виконайте цей крок на обох машинах — Machine 1 і Machine 2.

Підключіть кожен пристрій Ryzen AI Halo до комутатора Ethernet за допомогою кабелю Cat 7 (або вище). Це встановлює з'єднання 10 Гбіт/с, яке використовується для високошвидкісного зв'язку між вузлами.
<!-- @os:linux -->
### 1. Визначення мережевих інтерфейсів

На кожній машині знайдіть назву її мережевого інтерфейсу та запишіть її (нижче вона буде позначатися як `IFNAME`). Виконайте:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Це виводить назву інтерфейсу безпосередньо, наприклад:

```bash
enp191s0
```

### 2. Перевірка швидкості мережевого з'єднання

Переконайтеся, що з'єднання активне та працює на повній швидкості, перевіривши швидкість вашого інтерфейсу:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примітка**: Замініть `<IFNAME>` на назву інтерфейсу, отриману в розділі [1. Визначення мережевих інтерфейсів](#1-determine-network-interfaces)

Ви повинні побачити швидкість `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примітка**: Якщо швидкість нижча за `10000Mb/s` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштований на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Перевірка швидкості мережевого з'єднання

На кожній машині перевірте швидкість з'єднання ваших мережевих інтерфейсів:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш інтерфейс Ethernet повинен бути у стані `Up` і працювати на швидкості `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примітка**: Якщо швидкість нижча за `10 Gbps` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштований на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

## Встановлення llama.cpp

> **Примітка**: Виконайте цей крок на обох машинах — Machine 1 і Machine 2.

Доступні два варіанти встановлення:

- [Варіант 1: Lemonade SDK (Рекомендовано)](#option-1-lemonade-sdk-recommended) — готові бінарні файли, найшвидше налаштування
- [Варіант 2: Ручне збирання з вихідного коду](#option-2-manual-source-build) — збирання з вихідного коду з повним контролем над прапорами збирання

### Варіант 1: Lemonade SDK (Рекомендовано)

Lemonade SDK надає нічні збірки llama.cpp із прискоренням AMD ROCm 7, орієнтовані на GPU такі як gfx1151 (Strix Halo / Ryzen AI Max+ 395) та інші нові архітектури Radeon.

<!-- @os:windows -->
#### Крок 1: Завантаження готових бінарних файлів

Перейдіть на сторінку останнього релізу та завантажте архів, що відповідає вашій платформі та цільовому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Завантажте файл з назвою `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування бінарних файлів

Розпакуйте завантажений архів:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Цей каталог тепер містить збірки `llama-cli.exe`, `llama-server.exe` та `rpc-server.exe` з підтримкою ROCm, попередньо скомпільовані для вашої системи Ryzen AI Halo.

#### Крок 3: Перевірка виявлення GPU

```bash
.\llama-cli.exe --list-devices
```

Очікуваний вивід:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Завантаження готових бінарних файлів

Перейдіть на сторінку останнього релізу та завантажте архів, що відповідає вашій платформі та цільовому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Завантажте файл з назвою `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування та підготовка бінарних файлів

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Цей каталог тепер містить збірки `llama-cli`, `llama-server` та `rpc-server` з підтримкою ROCm, попередньо скомпільовані для вашої системи Ryzen AI Halo.

#### Крок 3: Перевірка виявлення GPU

```bash
./llama-cli --list-devices
```

Очікуваний вивід:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).

### Варіант 2: Ручне збирання з вихідного коду

<!-- @os:windows -->
#### Крок 1: Збирання llama.cpp

Відкрийте **x64 Native Tools Command Prompt** (встановлений разом із Visual Studio Build Tools) і клонуйте репозиторій:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Додайте HIP до вашого шляху та виконайте збирання з підтримкою ROCm та RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Прапор збирання | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm/HIP |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGPU_TARGETS=gfx1151` | Орієнтується на GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Використовує систему збирання Ninja |

#### Крок 2: Перевірка виявлення GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Очікуваний вивід:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Крок 3: Додавання HIP до шляху користувача

Крок збирання вище встановив `%HIP_PATH%\bin` лише для поточного сеансу. Щоб бібліотеки HIP були доступні в будь-якому терміналі (не лише в x64 Native Tools Command Prompt), додайте їх до `PATH` користувача постійно:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Збирання llama.cpp

Клонуйте репозиторій:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Виконайте збирання з підтримкою ROCm та RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Прапор збирання | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Вмикає rocWMMA для покращеного Flash Attention на GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Орієнтується на GPU Ryzen AI Halo (Radeon 8060s) |

Для отримання додаткових параметрів збирання зверніться до [документації зі збирання llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Крок 2: Перевірка виявлення GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Очікуваний вивід:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

## Завантаження моделі

У цьому посібнику використовується [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) — модель із 358 мільярдами параметрів у квантизації `Q4_K_XL` від [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). При такій квантизації модель потребує приблизно 205 ГБ сховища та вміщується в об'єднаній GPU пам'яті двох вузлів Ryzen AI Halo.

Завантажте файли GGUF за допомогою Hugging Face CLI:
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

> **Примітка**: Завантаження моделі необхідно виконати на Machine 1 (контролері). Вузлам RPC-воркерів локальна копія файлів моделі не потрібна.

## Запуск моделі на кластері

RPC-рушій (Remote Procedure Call) llama.cpp дозволяє одному екземпляру llama.cpp розвантажувати шари моделі на віддалені воркери через мережу. Одна машина виступає **контролером** (Machine 1), обробляючи токенізацію, планування та оркестрацію. Інша машина запускає легкий **RPC-сервер** (Machine 2), який надає свою GPU пам'ять і обчислювальні ресурси контролеру.

Під час завантаження llama.cpp розподіляє модель між обома вузлами. Після завантаження інференс відбувається так, ніби він виконується на одному прискорювачі. RPC обробляє передачу тензорів і синхронізацію у фоновому режимі.

### Крок 1: Запуск RPC-сервера (Machine 2)

На Machine 2 запустіть RPC-сервер, щоб надати його GPU-ресурси контролеру:
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

| Прапор | Призначення |
|------|---------|
| `-p` | Порт для трансляції RPC-сервера |
| `-c` | Вмикає локальний кеш для великих тензорів, уникаючи повторних мережевих передач під час завантаження моделі |
| `--host` | IP-адреса для прив'язки RPC-сервера (`0.0.0.0` для всіх інтерфейсів) |

Для отримання додаткових параметрів зверніться до [документації llama.cpp RPC](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Крок 2: Запуск моделі (Machine 1)

Після запуску RPC-сервера на Machine 2 запустіть інференс з Machine 1 за допомогою `llama-cli` або `llama-server`.

#### llama-cli

`llama-cli` надає термінальний інтерфейс для безпосередньої взаємодії з моделлю. Він ідеально підходить для бенчмаркінгу, налагодження та низькорівневих експериментів.

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

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Виконайте цю команду в Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.

<!-- @os:end -->

Після запуску `llama-cli` відображає прогрес завантаження моделі та переходить до інтерактивного запиту, де ви можете безпосередньо спілкуватися з моделлю:

![llama-cli, що запускає GLM 4.7 на двох вузлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` надає той самий рушій інференсу через постійний серверний процес із вбудованим веб-інтерфейсом та HTTP API, сумісним з OpenAI. Це кращий інтерфейс для тривалих розгортань, багатокористувацького доступу та інтеграції із зовнішніми інструментами.

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

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Виконайте цю команду в Terminal (Powershell).

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

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

Після запуску відкрийте `http://<HOST_IP>:8081` у браузері для доступу до вбудованого веб-інтерфейсу. Він надає браузерний інтерфейс чату для взаємодії з моделлю:

![Веб-інтерфейс llama-server, що запускає GLM 4.7 на двох вузлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Пошук `<HOST_IP>`**: На Machine 1 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Пошук `<HOST_IP>`**: На Machine 1 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

#### Довідник параметрів

| Прапор | Призначення |
|------|---------|
| `-m` | Шлях до файлу моделі GGUF (використовуйте перший фрагмент, `00001-of-00005`) |
| `-c` | Розмір контексту в токенах. Більші значення використовують більше пам'яті |
| `-fa on` | Вмикає rocWMMA Flash Attention для покращення продуктивності на GPU AMD |
| `-ngl 999` | Розвантажує всі шари моделі на GPU |
| `--no-mmap` | Вимикає відображення пам'яті, скорочуючи час завантаження, коли розмір моделі перевищує системну RAM, але вміщується у VRAM |
| `--host` | IP для прив'язки `llama-server` (лише для `llama-server`) |
| `--port` | Порт для обслуговування HTTP API (лише для `llama-server`) |
| `--rpc` | Розділений комами список кінцевих точок RPC-воркерів (`IP:port`) |

Для повного опису використання параметрів зверніться до [документації llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) та [документації llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Наступні кроки

- **Підключення сторонніх застосунків**: `llama-server` надає API, сумісний з OpenAI. Направте будь-який застосунок, сумісний з OpenAI (наприклад, Open WebUI), на `http://<HOST_IP>:8081` з будь-яким API-ключем-заповнювачем (наприклад, `none`) для підключення до вашого кластера
- **Дослідження інших моделей**: Перегляньте квантизовані GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), щоб знайти моделі, що вміщуються в об'єднаній GPU пам'яті вашого кластера
- **Масштабування до чотирьох вузлів**: Додайте ще дві системи Ryzen AI Halo як додаткові RPC-воркери для доступу до моделей масштабу 1 трильйона параметрів. Передайте додаткові кінцеві точки до `--rpc` у вигляді розділеного комами списку (наприклад, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)