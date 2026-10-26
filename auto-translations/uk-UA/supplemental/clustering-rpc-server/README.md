<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Кластеризація двох Ryzen™ AI Halo за допомогою RPC

## Огляд

Ваш Ryzen™ AI Halo вже здатний запускати великі мовні моделі локально. Кластеризація розширює ці можливості, об'єднуючи пам'ять GPU кількох систем через локальну мережу, надаючи доступ до ще більших моделей із потужнішими міркуваннями, кращою генерацією коду та глибшим розумінням багатьох мов — і все це повністю на вашому власному обладнанні.

Цей посібник навчить вас кластеризувати дві системи Ryzen AI Halo за допомогою RPC-двигуна llama.cpp та запускати GLM 4.7, модель із 358 мільярдами параметрів, на обох машинах одночасно з прискоренням AMD ROCm™.

## Що ви вивчите

- Як розширити виділення VRAM на системах Ryzen AI Halo
- Встановлення llama.cpp з підтримкою ROCm та RPC
- Налаштування RPC-воркера та запуск розподіленого інференсу на двох вузлах
- Запуск моделі з 358 мільярдами параметрів на двох з'єднаних у мережу системах Ryzen AI Halo

## Налаштування конфігурації пам'яті

> **Примітка**: Виконайте цей крок як на Machine 1, так і на Machine 2.

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Запуск моделей обсягом близько 128 ГБ або більше:** На системах AMD Ryzen™ AI Max 400 Series (Gorgon Halo) під керуванням Windows моделі, що наближаються до 128 ГБ пам'яті або перевищують цей обсяг, потребують додаткового налаштування для роботи без помилок. Перед завантаженням моделі дотримуйтесь [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
У Windows, щоб запускати більші моделі, які потребують більшого обсягу пам'яті, нам потрібно використовувати виділення AMD Variable Graphics Memory (iGPU VRAM).

Це можна зробити, відкривши панель керування AMD Software: Adrenalin Edition та перейшовши до: `Performance > Tuning > AMD Variable Graphics Memory`. Встановіть значення **96 GB**. Перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
У Linux ROCm використовує спільний пул системної пам'яті, і цей пул за замовчуванням налаштований на половину обсягу системної пам'яті.

Цей обсяг можна збільшити, змінивши налаштування сторінок Translation Table Manager (TTM) ядра, скориставшись наведеними нижче інструкціями. AMD рекомендує встановити мінімальний обсяг виділеної VRAM у BIOS (0.5 GB).

* Встановіть утиліту pipx та додайте шлях до встановлених через pipx пакетів у системний шлях пошуку.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Встановіть пакет amd-debug-tools з PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Запустіть інструмент amd-ttm, щоб дізнатися поточні налаштування спільної пам'яті.
  ```bash
  amd-ttm
  ```

* Перенастройте параметри спільної пам'яті на **120 ГБ**:
  ```bash
  amd-ttm --set 120
  ```

* Перезавантажте систему, щоб зміни набули чинності.


<!-- @os:end -->
<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->
## Попередні вимоги

### Обладнання

Для цього посібника потрібні два блоки Ryzen AI Halo та один Ethernet-комутатор, з'єднані за топологією "зірка", де кожен блок підключено безпосередньо до комутатора.

| Компонент | Кількість | Опис |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Обчислювальні вузли, що формують кластер |
| Ethernet-комутатор 10 Гбіт/с | 1 | Центральний комутатор для забезпечення зв'язку між кількома вузлами Ryzen AI Halo (щонайменше 2 порти) |
| Ethernet-кабель | 2 | З'єднує кожен блок Halo з комутатором (рекомендовано Cat 7 або вищий) |

> **Примітка**: Для підключення двох блоків Ryzen AI Halo потрібні два порти Ethernet-комутатора. Третій порт потрібен, якщо ви звертаєтесь до моделі з окремої клієнтської машини, а не з одного з блоків Halo.

### Програмне забезпечення
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Встановіть:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) з робочим навантаженням **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Фізичне налаштування обладнання

> **Примітка**: Виконайте цей крок як на Machine 1, так і на Machine 2.

Підключіть кожен блок Ryzen AI Halo до Ethernet-комутатора за допомогою кабелю Cat 7 (або вищого). Це встановить з'єднання 10 Гбіт/с, що використовується для високошвидкісного зв'язку між вузлами.
<!-- @os:linux -->
### 1. Визначення мережевих інтерфейсів

На кожній машині знайдіть назву її мережевого інтерфейсу та запишіть її (далі вона буде позначатися як `IFNAME`). Виконайте:

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

> **Примітка**: Якщо швидкість нижча за `10000Mb/s` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштований на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Перевірка швидкості мережевого з'єднання

На кожній машині перевірте швидкість з'єднання ваших мережевих інтерфейсів:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш Ethernet-інтерфейс має бути у стані `Up` та працювати на швидкості `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примітка**: Якщо швидкість нижча за `10 Gbps` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштований на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

## Встановлення llama.cpp

> **Примітка**: Виконайте цей крок як на Machine 1, так і на Machine 2.

Доступні два варіанти встановлення:

- [Варіант 1: Lemonade SDK (рекомендовано)](#option-1-lemonade-sdk-recommended) — попередньо зібрані бінарні файли, найшвидше налаштування
- [Варіант 2: Ручна збірка з вихідного коду](#option-2-manual-source-build) — збірка з вихідного коду з повним контролем над прапорцями збірки
### Варіант 1: Lemonade SDK (рекомендовано)

Lemonade SDK надає нічні збірки llama.cpp з прискоренням AMD ROCm 7, орієнтовані на такі GPU, як gfx1151 (Strix Halo / Ryzen AI Max+ 395), та інші новітні архітектури Radeon.

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
Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).

### Варіант 2: Збірка з вихідного коду вручну

<!-- @os:windows -->
#### Крок 1: Збірка llama.cpp

Відкрийте **x64 Native Tools Command Prompt** (встановлений разом із Visual Studio Build Tools) та клонуйте репозиторій:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Додайте HIP до шляху та зберіть проєкт з підтримкою ROCm та RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm/HIP |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGPU_TARGETS=gfx1151` | Орієнтується на GPU Ryzen AI Halo (Radeon 8060s) |
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

Наведений вище крок збірки встановив `%HIP_PATH%\bin` лише для поточного сеансу. Щоб зробити бібліотеки HIP доступними в будь-якому терміналі (а не лише в x64 Native Tools Command Prompt), додайте його до вашого користувацького `PATH` на постійній основі:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Збірка llama.cpp

Клонуйте репозиторій:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Зберіть проєкт з підтримкою ROCm та RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DAMDGPU_TARGETS="gfx1151"` | Орієнтується на GPU Ryzen AI Halo (Radeon 8060s) |

Щоб дізнатися про інші параметри збірки, див. [документацію зі збірки llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Після підготовки llama.cpp на кожному вузлі перейдіть до розділу [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

## Завантаження моделі

Цей посібник використовує [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7) — модель з 358 млрд параметрів у квантизації `Q4_K_XL` від [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). За такої квантизації модель потребує приблизно 205 ГБ сховища та вміщується в сукупну пам'ять GPU двох вузлів Ryzen AI Halo.

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

> **Примітка**: Завантаження моделі має бути завершене на Machine 1 (контролері). Вузли-воркери RPC не потребують локальної копії файлів моделі.

## Запуск моделі на кластері

Механізм RPC (Remote Procedure Call) у llama.cpp дозволяє одному екземпляру llama.cpp передавати шари моделі на віддалені воркери через мережу. Одна машина виконує роль **контролера** (Machine 1), відповідаючи за токенізацію, планування та оркестрацію. Інша машина запускає легкий **RPC-сервер** (Machine 2), який надає свою пам'ять GPU та обчислювальні ресурси контролеру.

Під час завантаження llama.cpp розподіляє модель між обома вузлами. Після завантаження інференс виконується так, ніби працює на одному прискорювачі. RPC непомітно для користувача обробляє передачу тензорів і синхронізацію.

### Крок 1: Запуск RPC-сервера (Machine 2)

На Machine 2 запустіть RPC-сервер, щоб надати свої ресурси GPU контролеру:
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

| Прапорець | Призначення |
|------|---------|
| `-p` | Порт для трансляції RPC-сервера |
| `-c` | Вмикає локальний кеш для великих тензорів, уникаючи повторних мережевих передач під час завантаження моделі |
| `--host` | IP-адреса для прив'язки RPC-сервера (`0.0.0.0` для всіх інтерфейсів) |

Щоб дізнатися про інші параметри, див. [документацію RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Крок 2: Запуск моделі (Machine 1)

Коли RPC-сервер запущено на Machine 2, запустіть інференс з Machine 1, використовуючи `llama-cli` або `llama-server`.
#### llama-cli

`llama-cli` надає термінальний інтерфейс для безпосередньої взаємодії з моделлю. Він ідеально підходить для бенчмаркінгу, налагодження та низькорівневих експериментів.

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
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.

<!-- @os:end -->

Після запуску `llama-cli` відображає перебіг завантаження моделі та відкриває інтерактивне запрошення, де ви можете спілкуватися з моделлю безпосередньо:

![llama-cli виконує GLM 4.7 на двох вузлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` надає доступ до того самого механізму інференсу через постійний серверний процес із вбудованим веб-інтерфейсом та HTTP API, сумісним із OpenAI. Це бажаний інтерфейс для розгортань із тривалою роботою, доступу кількох користувачів та інтеграції із зовнішніми інструментами.

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

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Виконайте цю команду в терміналі (Powershell).

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

> **Пошук `<RPC_WORKER_IP>`**: На Machine 2 виконайте `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

Після запуску відкрийте `http://<HOST_IP>:8081` у браузері, щоб отримати доступ до вбудованого веб-інтерфейсу. Він надає чат-інтерфейс на основі браузера для взаємодії з моделлю:

![веб-інтерфейс llama-server виконує GLM 4.7 на двох вузлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Пошук `<HOST_IP>`**: На Machine 1 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Пошук `<HOST_IP>`**: На Machine 1 виконайте `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

#### Довідник параметрів

| Прапорець | Призначення |
|------|---------|
| `-m` | Шлях до файлу моделі GGUF (використовуйте перший шард, `00001-of-00005`) |
| `-c` | Розмір контексту в токенах. Більші значення використовують більше пам'яті |
| `-fa on` | Вмикає rocWMMA Flash Attention для покращеної продуктивності на GPU AMD |
| `-ngl 999` | Вивантажує всі шари моделі на GPU |
| `-lm none` | Встановлює режим завантаження моделі `none`, вимикаючи мапування пам'яті для скорочення часу завантаження, коли розмір моделі перевищує обсяг системної RAM, але вміщується у VRAM |
| `--host` | IP-адреса для прив'язки `llama-server` (лише для `llama-server`) |
| `--port` | Порт для обслуговування HTTP API (лише для `llama-server`) |
| `--rpc` | Список кінцевих точок RPC-воркерів через кому (`IP:port`) |

Для повного опису параметрів зверніться до [документації llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) та [документації llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Наступні кроки

- **Підключення сторонніх застосунків**: `llama-server` надає API, сумісний із OpenAI. Спрямуйте будь-який застосунок, сумісний з OpenAI (наприклад, Open WebUI), на `http://<HOST_IP>:8081` із будь-яким заповнювачем API-ключа (наприклад, `none`), щоб підключитися до вашого кластера
- **Дослідження інших моделей**: Переглядайте квантизовані GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), щоб знайти моделі, які вміщуються в сукупну пам'ять GPU вашого кластера
- **Масштабування до чотирьох вузлів**: Додайте ще дві системи Ryzen AI Halo як додаткові RPC-воркери, щоб отримати доступ до моделей масштабу 1 трильйон параметрів. Передайте додаткові кінцеві точки в `--rpc` у вигляді списку через кому (наприклад, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)