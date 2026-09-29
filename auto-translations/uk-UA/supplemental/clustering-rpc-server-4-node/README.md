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

# Кластеризація чотирьох Ryzen™ AI Halo за допомогою RPC

## Огляд

Ваш Ryzen™ AI Halo вже здатен локально запускати великі мовні моделі. Кластеризація йде далі, об'єднуючи пам'ять GPU кількох систем через локальну мережу, надаючи доступ до ще більших моделей із потужнішим міркуванням, кращою генерацією коду та глибшим розумінням багатьох мов — і все це повністю на вашому власному обладнанні.

Цей посібник навчить вас кластеризувати чотири системи Ryzen AI Halo за допомогою RPC-рушія llama.cpp та запускати Kimi K2.6, велику модель типу mixture-of-experts, на всіх чотирьох машинах з прискоренням AMD ROCm™.

## Чого ви навчитеся

- Як розширити виділення VRAM на системах Ryzen AI Halo
- Встановлення llama.cpp з підтримкою ROCm та RPC
- Налаштування RPC-воркерів та запуск розподіленого інференсу на чотирьох вузлах
- Запуск моделі з 1 трлн параметрів на чотирьох системах Ryzen AI Halo, з'єднаних у мережу

## Налаштування конфігурації пам'яті

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (Машина 1 – Машина 4).

<!-- @os:windows -->
У Windows, щоб запускати більші моделі, які потребують більшого обсягу пам'яті, необхідно скористатися виділенням AMD Variable Graphics Memory (iGPU VRAM).

Це можна зробити, відкривши панель керування AMD Software: Adrenalin Edition та перейшовши до: `Performance > Tuning > AMD Variable Graphics Memory`. Встановіть значення **96 ГБ**. Перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
У Linux ROCm використовує спільний пул системної пам'яті, і за замовчуванням цей пул налаштовано на половину обсягу системної пам'яті.

Цей обсяг можна збільшити, змінивши налаштування сторінок Translation Table Manager (TTM) ядра, скориставшись наведеними нижче інструкціями. AMD рекомендує встановити мінімальний обсяг виділеної VRAM у BIOS (0,5 ГБ).

* Встановіть утиліту pipx та додайте шлях до встановлених через pipx wheel-файлів у системний шлях пошуку.

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

* Змініть налаштування спільної пам'яті на **120 ГБ**:
  ```bash
  amd-ttm --set 120
  ```

* Перезавантажте систему, щоб зміни набули чинності.


<!-- @os:end -->
<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->
## Обов'язкові вимоги

### Обладнання

Для цього посібника потрібні чотири блоки Ryzen AI Halo та один Ethernet-комутатор, з'єднані за топологією "зірка", де кожен блок підключено безпосередньо до комутатора.

| Компонент | Кількість | Опис |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Обчислювальні вузли, що утворюють кластер |
| Ethernet-комутатор 10 Гбіт/с | 1 | Центральний комутатор для забезпечення взаємодії кількох вузлів Ryzen AI Halo (не менше 4 портів) |
| Ethernet-кабель | 4 | З'єднує кожен блок Halo з комутатором (рекомендовано Cat 7 або вище) |

> **Примітка**: Для підключення чотирьох блоків Ryzen AI Halo потрібно чотири порти Ethernet-комутатора. Якщо ви звертаєтеся до моделі з окремої клієнтської машини, а не з одного з блоків Halo, потрібен п'ятий порт.

### Програмне забезпечення
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Будь ласка, встановіть:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) з навантаженням **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Фізичне налаштування обладнання

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (Машина 1 – Машина 4).

Підключіть кожен блок Ryzen AI Halo до Ethernet-комутатора за допомогою кабелю Cat 7 (або вищого класу). Це забезпечить з'єднання на швидкості 10 Гбіт/с, яке використовується для високошвидкісного зв'язку між вузлами.
<!-- @os:linux -->
### 1. Визначення мережевих інтерфейсів

На кожній машині визначте назву її мережевого інтерфейсу та занотуйте її (нижче вона позначатиметься як `IFNAME`). Виконайте:

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

> **Примітка**: Замініть `<IFNAME>` на назву вихідного інтерфейсу з розділу [1. Визначення мережевих інтерфейсів](#1-визначення-мережевих-інтерфейсів)

Ви повинні побачити швидкість `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Примітка**: Якщо швидкість нижче `10000Mb/s` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштовано на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

<!-- @os:windows -->
### Перевірка швидкості мережевого з'єднання

На кожній машині перевірте швидкість з'єднання ваших мережевих інтерфейсів:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ваш Ethernet-інтерфейс повинен бути в стані `Up` і працювати на швидкості `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примітка**: Якщо швидкість нижче `10 Gbps` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштовано на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

## Встановлення llama.cpp

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (Машина 1 – Машина 4).

Доступні два варіанти встановлення:

- [Варіант 1: Lemonade SDK (рекомендовано)](#option-1-lemonade-sdk-recommended) — готові бінарні файли, найшвидше налаштування
- [Варіант 2: Ручна збірка з вихідного коду](#option-2-manual-source-build) — збірка з вихідного коду з повним контролем над прапорцями збірки

### Варіант 1: Lemonade SDK (рекомендовано)

Lemonade SDK надає нічні збірки llama.cpp з прискоренням AMD ROCm 7, орієнтовані на GPU, такі як gfx1151 (Strix Halo / Ryzen AI Max+ 395) та інші сучасні архітектури Radeon.

<!-- @os:windows -->
#### Крок 1: Завантаження попередньо зібраних бінарних файлів

Перейдіть на сторінку останнього релізу та завантажте архів, що відповідає вашій платформі та цільовому GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Завантажте файл з іменем `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування бінарних файлів

Розпакуйте завантажений архів:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Тепер цей каталог містить збірки `llama-cli.exe`, `llama-server.exe` та `ggml-rpc-server.exe` з підтримкою ROCm, попередньо скомпільовані для вашої системи Ryzen AI Halo.

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

Завантажте файл з іменем `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (де `xxxx` — номер збірки).

#### Крок 2: Розпакування та підготовка бінарних файлів

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Тепер цей каталог містить збірки `llama-cli`, `llama-server` та `rpc-server` з підтримкою ROCm, попередньо скомпільовані для вашої системи Ryzen AI Halo.

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

### Варіант 2: Ручна збірка з вихідного коду

<!-- @os:windows -->
#### Крок 1: Збірка llama.cpp

Відкрийте **x64 Native Tools Command Prompt** (встановлений разом із Visual Studio Build Tools) і клонуйте репозиторій:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Додайте HIP до вашого шляху та зберіть проєкт із підтримкою ROCm і RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm/HIP |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DGPU_TARGETS=gfx1151` | Націлює на GPU Ryzen AI Halo (Radeon 8060s) |
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

Наведений вище крок збірки встановив `%HIP_PATH%\bin` лише для поточного сеансу. Щоб бібліотеки HIP були доступні в будь-якому терміналі (а не лише в x64 Native Tools Command Prompt), додайте його до вашого користувацького `PATH` на постійній основі:

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

Зберіть проєкт із підтримкою ROCm і RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DAMDGPU_TARGETS="gfx1151"` | Націлює на GPU Ryzen AI Halo (Radeon 8060s) |

Додаткові параметри збірки описано в [документації зі збірки llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

У цьому посібнику використовується [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) у квантизації `UD-Q2_K_XL` від [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ця квантизація вміщується у сукупну пам'ять GPU чотирьох вузлів Ryzen AI Halo.

Завантажте файли GGUF за допомогою Hugging Face CLI:
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

> **Примітка**: Завантаження моделі має бути виконано на Машині 1 (контролері). Робочим вузлам RPC (Машини 2, 3 та 4) не потрібна локальна копія файлів моделі.

## Запуск моделі в кластері

Механізм RPC (Remote Procedure Call) у llama.cpp дозволяє одному екземпляру llama.cpp вивантажувати шари моделі на віддалені робочі вузли через мережу. Одна машина виступає в ролі **контролера** (Машина 1), відповідаючи за токенізацію, планування та оркестрацію. Кожна з трьох інших машин запускає легкий **RPC-сервер** (Машини 2, 3 та 4), що надає свою пам'ять GPU та обчислювальні ресурси контролеру.

Під час завантаження llama.cpp розподіляє модель по всіх чотирьох вузлах. Після завантаження інференс виконується так, ніби він відбувається на одному прискорювачі. RPC приховано обробляє передачу тензорів та синхронізацію.

### Крок 1: Запуск RPC-серверів (Машини 2, 3 та 4)

На кожній із Машин 2, 3 та 4 запустіть RPC-сервер, щоб надати доступ до її ресурсів GPU контролеру:
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
| `-p` | Порт, на якому транслюється RPC-сервер |
| `-c` | Вмикає локальний кеш для великих тензорів, уникаючи повторної передачі даних мережею під час завантаження моделі |
| `--host` | IP-адреса, на якій прив'язується RPC-сервер (`0.0.0.0` для всіх інтерфейсів) |

Додаткові параметри описано в [документації RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Крок 2: Запуск моделі (Машина 1)

Коли RPC-сервери запущені на Машинах 2, 3 та 4, запустіть інференс з Машини 1, використовуючи `llama-cli` або `llama-server`.
#### llama-cli

`llama-cli` надає термінальний інтерфейс для прямої взаємодії з моделлю. Він ідеально підходить для бенчмаркінгу, налагодження та низькорівневих експериментів.

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: На кожній із Машин 2, 3 і 4 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Виконайте цю команду в Terminal (Powershell).

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: На кожній із Машин 2, 3 і 4 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.

<!-- @os:end -->

Після запуску `llama-cli` відображає прогрес завантаження моделі та переходить в інтерактивний режим, де ви можете спілкуватися з моделлю безпосередньо:

![llama-cli під час запуску Kimi K2.6 на чотирьох вузлах](assets/llama-cli-example.png)

#### llama-server

`llama-server` надає той самий рушій інференсу через постійний серверний процес із вбудованим веб-інтерфейсом та HTTP API, сумісним з OpenAI. Це кращий інтерфейс для тривалих розгортань, доступу кількох користувачів та інтеграції із зовнішнім інструментарієм.

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: На кожній із Машин 2, 3 і 4 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Виконайте цю команду в Terminal (Powershell).

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: На кожній із Машин 2, 3 і 4 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

Після запуску відкрийте `http://<HOST_IP>:8081` у браузері, щоб отримати доступ до вбудованого веб-інтерфейсу. Це надає браузерний чат-інтерфейс для взаємодії з моделлю:

![Веб-інтерфейс llama-server під час запуску Kimi K2.6 на чотирьох вузлах](assets/llama-server-example.png)

<!-- @os:linux -->
> **Пошук `<HOST_IP>`**: На Машині 1 виконайте `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Пошук `<HOST_IP>`**: На Машині 1 виконайте `ipconfig | findstr /C:"IPv4"` в Terminal (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

#### Довідник параметрів

| Прапорець | Призначення |
|------|---------|
| `-m` | Шлях до файлу моделі GGUF (використовуйте перший шард, `00001-of-00008`) |
| `-c` | Розмір контексту в токенах. Більші значення використовують більше пам'яті |
| `-fa on` | Вмикає rocWMMA Flash Attention для покращеної продуктивності на GPU AMD |
| `-ngl 999` | Вивантажує всі шари моделі на GPU |
| `-lm none` | Встановлює режим завантаження моделі на `none`, вимикаючи відображення пам'яті (memory-mapping) для скорочення часу завантаження, коли розмір моделі перевищує обсяг системної RAM, але вміщується у VRAM |
| `-b` | Логічний розмір пакета в токенах. Значення 4096 забезпечує баланс між пропускною здатністю та використанням пам'яті на всіх вузлах |
| `-ub` | Фізичний (мікро) розмір пакета для обробки промпту. Відповідність значенню `-b` дозволяє уникнути зайвих накладних витрат на розбиття на частини |
| `--host` | IP-адреса, до якої прив'язується `llama-server` (лише для `llama-server`) |
| `--port` | Порт для HTTP API (лише для `llama-server`) |
| `--rpc` | Список кінцевих точок RPC-воркерів через кому (`IP:port`) |

Повний опис параметрів наведено в [документації llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) та [документації llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Наступні кроки

- **Підключення сторонніх застосунків**: `llama-server` надає API, сумісний з OpenAI. Вкажіть будь-якому застосунку, сумісному з OpenAI (наприклад, Open WebUI), адресу `http://<HOST_IP>:8081` із будь-яким довільним API-ключем (наприклад, `none`), щоб підключитися до вашого кластера
- **Огляд інших моделей**: Перегляньте квантовані GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), щоб знайти моделі, які вміщуються в сукупну пам'ять GPU вашого кластера
- **Масштабування понад чотири вузли**: Додайте додаткові системи Ryzen AI Halo як додаткові RPC-воркери, щоб отримати доступ до моделей масштабом понад 1 трильйон параметрів. Передайте додаткові кінцеві точки в `--rpc` як список через кому (наприклад, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)