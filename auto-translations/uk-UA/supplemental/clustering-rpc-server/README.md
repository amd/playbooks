<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а деякі кроки, команди, завантаження або доступність продуктів можуть відрізнятися у вашій мові чи регіоні. Якщо щось виглядає неправильно, вважайте оригінальний англомовний playbook джерелом достовірної інформації.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> Цей посібник використовує спеціальні теги, які GitHub не може відобразити. Будь ласка, відвідайте [amd.com/playbooks](https://amd.com/playbooks), щоб коректно переглянути цей вміст.
<!-- @github-only:end -->

# Кластеризація двох Ryzen™ AI Halo за допомогою RPC

## Огляд

Ваш Ryzen™ AI Halo вже здатний локально запускати великі мовні моделі. Кластеризація виводить це на новий рівень, об'єднуючи пам'ять GPU кількох систем через локальну мережу, надаючи доступ до ще більших моделей із потужнішим міркуванням, кращою генерацією коду та глибшим розумінням багатьох мов — і все це повністю на власному обладнанні.

Цей посібник навчить вас кластеризувати дві системи Ryzen AI Halo за допомогою RPC-рушія llama.cpp та запускати GLM 4.7, модель із 358 мільярдами параметрів, на обох машинах з прискоренням AMD ROCm™.

## Що ви дізнаєтеся

- Як розширити виділення VRAM на системах Ryzen AI Halo
- Встановлення llama.cpp з підтримкою ROCm та RPC
- Налаштування RPC-воркера та запуск розподіленого інференсу на двох вузлах
- Запуск моделі з 358 мільярдами параметрів на двох мережевих системах Ryzen AI Halo

## Налаштування конфігурації пам'яті

> **Примітка**: Виконайте цей крок на обох машинах: Машина 1 і Машина 2.

<!-- @os:windows -->
У Windows, щоб запускати більші моделі, які потребують більшого обсягу пам'яті, нам потрібно використовувати виділення AMD Variable Graphics Memory (iGPU VRAM).

Це можна зробити, відкривши панель керування AMD Software: Adrenalin Edition і перейшовши до: `Performance > Tuning > AMD Variable Graphics Memory`. Встановіть значення **96 GB**. Будь ласка, перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
У Linux ROCm використовує спільний пул системної пам'яті, і цей пул за замовчуванням налаштовано на половину обсягу системної пам'яті.

Цей обсяг можна збільшити, змінивши налаштування сторінок Translation Table Manager (TTM) ядра, дотримуючись наведених нижче інструкцій. AMD рекомендує встановити мінімальний виділений обсяг VRAM у BIOS (0.5 GB).

* Встановіть утиліту pipx та додайте шлях до встановлених за допомогою pipx wheel-пакетів до системного шляху пошуку.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Встановіть wheel-пакет amd-debug-tools з PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустіть інструмент amd-ttm, щоб дізнатися поточні налаштування спільної пам'яті.
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

### Апаратне забезпечення

Для цього посібника потрібні два пристрої Ryzen AI Halo та один комутатор Ethernet, з'єднані за топологією "зірка", де кожен пристрій підключений безпосередньо до комутатора.

| Компонент | Кількість | Опис |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Обчислювальні вузли, що утворюють кластер |
| Комутатор Ethernet 10 Гбіт/с | 1 | Центральний комутатор для забезпечення зв'язку між кількома вузлами Ryzen AI Halo (щонайменше 2 порти) |
| Кабель Ethernet | 2 | З'єднує кожен пристрій Halo з комутатором (рекомендується Cat 7 або вище) |

> **Примітка**: Для підключення двох пристроїв Ryzen AI Halo потрібні два порти комутатора Ethernet. Третій порт потрібен, якщо ви звертаєтеся до моделі з окремої клієнтської машини, а не з одного з пристроїв Halo.

### Програмне забезпечення
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Будь ласка, встановіть:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) з робочим навантаженням **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Фізичне налаштування обладнання

> **Примітка**: Виконайте цей крок на обох машинах: Машина 1 і Машина 2.

Підключіть кожен пристрій Ryzen AI Halo до комутатора Ethernet за допомогою кабелю Cat 7 (або вище). Це встановить 10-гігабітне з'єднання, яке використовується для високошвидкісного зв'язку між вузлами.
<!-- @os:linux -->
### 1. Визначення мережевих інтерфейсів

На кожній машині визначте назву її мережевого інтерфейсу та запишіть її (далі вона позначатиметься як `IFNAME`). Виконайте:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Це виведе назву інтерфейсу безпосередньо, наприклад:

```bash
enp191s0
```

### 2. Перевірка швидкості мережевого з'єднання

Переконайтеся, що з'єднання активне та працює на повній швидкості, перевіривши швидкість вашого інтерфейсу:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примітка**: Замініть `<IFNAME>` на назву вихідного інтерфейсу з розділу [1. Визначення мережевих інтерфейсів](#1-determine-network-interfaces)

Ви маєте побачити швидкість `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примітка**: Якщо швидкість нижча за `10000Mb/s` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштовано на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації свого комутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Перевірка швидкості мережевого з'єднання

На кожній машині перевірте швидкість з'єднання ваших мережевих інтерфейсів:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш інтерфейс Ethernet має бути `Up` і працювати на швидкості `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примітка**: Якщо швидкість нижча за `10 Gbps` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштовано на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації свого комутатора.

<!-- @os:end -->

## Встановлення llama.cpp

> **Примітка**: Виконайте цей крок на обох машинах: Машина 1 і Машина 2.

Доступні два варіанти встановлення:

- [Варіант 1: Lemonade SDK (рекомендовано)](#option-1-lemonade-sdk-recommended) — попередньо зібрані бінарні файли, найшвидше налаштування
- [Варіант 2: Ручна збірка з вихідного коду](#option-2-manual-source-build) — збірка з вихідного коду з повним контролем над прапорцями збірки

### Варіант 1: Lemonade SDK (рекомендовано)

Lemonade SDK надає нічні збірки llama.cpp з прискоренням AMD ROCm 7, орієнтовані на GPU, такі як gfx1151 (Strix Halo / Ryzen AI Max+ 395) та інші новіші архітектури Radeon.

<!-- @os:windows -->
#### Крок 1: Завантаження попередньо зібраних бінарних файлів

Перейдіть на сторінку останнього релізу та завантажте архів, що відповідає вашій платформі та цільовому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Завантажте файл з назвою `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування бінарних файлів

Розпакуйте завантажений архів:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Тепер цей каталог містить збірки `llama-cli.exe`, `llama-server.exe` та `rpc-server.exe` з підтримкою ROCm, скомпільовані для вашої системи Ryzen AI Halo.

#### Крок 3: Перевірка виявлення GPU

```bash
.\llama-cli.exe --list-devices
```

Очікуваний результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Завантаження попередньо зібраних бінарних файлів

Перейдіть на сторінку останнього релізу та завантажте архів, що відповідає вашій платформі та цільовому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Завантажте файл з назвою `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування та підготовка бінарних файлів

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Тепер цей каталог містить збірки `llama-cli`, `llama-server` та `rpc-server` з підтримкою ROCm, скомпільовані для вашої системи Ryzen AI Halo.

#### Крок 3: Перевірка виявлення GPU

```bash
./llama-cli --list-devices
```

Очікуваний результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Підготувавши llama.cpp на кожному вузлі, переходьте до розділу [Завантаження моделі](#downloading-the-model).

### Варіант 2: Ручна збірка з вихідного коду

<!-- @os:windows -->
#### Крок 1: Збірка llama.cpp

Відкрийте **x64 Native Tools Command Prompt** (встановлюється разом із Visual Studio Build Tools) і клонуйте репозиторій:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Додайте HIP до шляху та зберіть із підтримкою ROCm та RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm/HIP |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGPU_TARGETS=gfx1151` | Націлено на GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Використовує систему збірки Ninja |

#### Крок 2: Перевірка виявлення GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Очікуваний результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Крок 3: Додавання HIP до вашого користувацького шляху

Наведений вище крок збірки встановив `%HIP_PATH%\bin` лише для поточного сеансу. Щоб зробити бібліотеки HIP доступними в будь-якому терміналі (не лише в x64 Native Tools Command Prompt), додайте його до вашого користувацького `PATH` на постійній основі:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Підготувавши llama.cpp на кожному вузлі, переходьте до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Збірка llama.cpp

Клонуйте репозиторій:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Зберіть із підтримкою ROCm та RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Вмикає rocWMMA для покращеної Flash Attention на GPU AMD |
| `-DAMDGPU_TARGETS="gfx1151"` | Націлено на GPU Ryzen AI Halo (Radeon 8060s) |

Щоб дізнатися більше про параметри збірки, зверніться до [документації зі збірки llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Крок 2: Перевірка виявлення GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Очікуваний результат:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Підготувавши llama.cpp на кожному вузлі, переходьте до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

## Завантаження моделі

У цьому посібнику використовується [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), модель зі 358 мільярдами параметрів у квантизації `Q4_K_XL` від [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). За такої квантизації модель потребує приблизно 205 ГБ пам'яті для зберігання та вміщується в сукупну пам'ять GPU двох вузлів Ryzen AI Halo.

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

> **Примітка**: Завантаження моделі має бути виконане на Machine 1 (контролер). Робочим вузлам RPC не потрібна локальна копія файлів моделі.

## Запуск моделі в кластері

Механізм RPC (Remote Procedure Call) у llama.cpp дозволяє одному екземпляру llama.cpp вивантажувати шари моделі на віддалені робочі вузли через мережу. Одна машина виконує роль **контролера** (Machine 1), відповідаючи за токенізацію, планування та оркестрацію. Інша машина запускає легкий **RPC-сервер** (Machine 2), який надає контролеру доступ до своєї пам'яті GPU та обчислювальних ресурсів.

Під час завантаження llama.cpp розподіляє модель між обома вузлами. Після завантаження інференс відбувається так, ніби він виконується на єдиному прискорювачі. RPC непомітно для користувача керує передачею тензорів і синхронізацією.

### Крок 1: Запуск RPC-сервера (Machine 2)

На Machine 2 запустіть RPC-сервер, щоб надати контролеру доступ до ресурсів GPU:
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

| Прапорець | Призначення |
|------|---------|
| `-p` | Порт, на якому транслюється RPC-сервер |
| `-c` | Вмикає локальний кеш для великих тензорів, уникаючи повторних передач мережею під час завантаження моделі |
| `--host` | IP-адреса, до якої прив'язується RPC-сервер (`0.0.0.0` для всіх інтерфейсів) |

Щоб дізнатися більше про параметри, зверніться до [документації RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Крок 2: Запуск моделі (Machine 1)

Коли RPC-сервер запущено на Machine 2, запустіть інференс з Machine 1, використовуючи `llama-cli` або `llama-server`.

#### llama-cli

`llama-cli` надає інтерфейс на основі терміналу для прямої взаємодії з моделлю. Він ідеально підходить для бенчмаркінгу, налагодження та експериментів низького рівня.

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
> **Примітка**: Виконайте цю команду в терміналі (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.

<!-- @os:end -->

Після запуску `llama-cli` відображає хід завантаження моделі та переходить в інтерактивний режим підказки, де ви можете спілкуватися безпосередньо з моделлю:

![llama-cli, що запускає GLM 4.7 на двох вузлах](assets/llama-cli-example.png)
#### llama-server

`llama-server` надає доступ до того самого механізму інференсу через постійний серверний процес з інтегрованим веб-інтерфейсом і HTTP API, сумісним з OpenAI. Це кращий варіант для тривалих розгортань, доступу кількох користувачів та інтеграції із зовнішніми інструментами.

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

> **Пошук `<RPC_WORKER_IP>`**: На Машині 2 виконайте `hostname -I | awk '{print $1}'`, щоб дізнатися її локальну IP-адресу.
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

> **Пошук `<RPC_WORKER_IP>`**: На Машині 2 виконайте `ipconfig | findstr /C:"IPv4"` у Terminal (Powershell), щоб дізнатися її локальну IP-адресу.
<!-- @os:end -->

Після запуску відкрийте `http://<HOST_IP>:8081` у своєму браузері, щоб отримати доступ до вбудованого веб-інтерфейсу. Це надає інтерфейс чату на основі браузера для взаємодії з моделлю:

![Веб-інтерфейс llama-server, у якому запущено GLM 4.7 на двох вузлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Пошук `<HOST_IP>`**: На Машині 1 виконайте `hostname -I | awk '{print $1}'`, щоб дізнатися її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Пошук `<HOST_IP>`**: На Машині 1 виконайте `ipconfig | findstr /C:"IPv4"` у Terminal (Powershell), щоб дізнатися її локальну IP-адресу.
<!-- @os:end -->

#### Довідник параметрів

| Прапорець | Призначення |
|------|---------|
| `-m` | Шлях до файлу моделі GGUF (використовуйте перший фрагмент, `00001-of-00005`) |
| `-c` | Розмір контексту в токенах. Більші значення використовують більше пам'яті |
| `-fa on` | Вмикає rocWMMA Flash Attention для покращеної продуктивності на GPU AMD |
| `-ngl 999` | Вивантажує всі шари моделі на GPU |
| `--no-mmap` | Вимикає відображення пам'яті (memory-mapping), скорочуючи час завантаження, коли розмір моделі перевищує обсяг системної RAM, але вміщується у VRAM |
| `--host` | IP-адреса, на якій буде запущено `llama-server` (лише для `llama-server`) |
| `--port` | Порт для обслуговування HTTP API (лише для `llama-server`) |
| `--rpc` | Список кінцевих точок RPC-воркерів через кому (`IP:port`) |

Щоб дізнатися про повне використання параметрів, зверніться до [документації llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) та [документації llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Наступні кроки

- **Підключення сторонніх застосунків**: `llama-server` надає API, сумісний з OpenAI. Направте будь-який сумісний з OpenAI застосунок (наприклад, Open WebUI) на `http://<HOST_IP>:8081` із будь-яким заповнювачем API-ключа (наприклад, `none`), щоб підключитися до вашого кластера
- **Дослідження інших моделей**: Перегляньте квантовані GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), щоб знайти моделі, які поміщаються в сукупну пам'ять GPU вашого кластера
- **Масштабування до чотирьох вузлів**: Додайте ще дві системи Ryzen AI Halo як додаткові RPC-воркери, щоб отримати доступ до моделей масштабу 1 трильйона параметрів. Передайте додаткові кінцеві точки в `--rpc` у вигляді списку через кому (наприклад, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)