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

Ваш Ryzen™ AI Halo вже здатен локально запускати великі мовні моделі. Кластеризація розширює ці можливості, об'єднуючи пам'ять GPU кількох систем через локальну мережу, надаючи доступ до ще більших моделей з потужнішими можливостями міркування, кращою генерацією коду та глибшим розумінням багатьох мов — і все це повністю на вашому власному обладнанні.

У цьому посібнику ви навчитеся кластеризувати чотири системи Ryzen AI Halo за допомогою RPC-рушія llama.cpp та запускати Kimi K2.6 — велику модель mixture-of-experts — на всіх чотирьох машинах з прискоренням AMD ROCm™.

## Що ви дізнаєтеся

- Як розширити виділення VRAM на системах Ryzen AI Halo
- Встановлення llama.cpp з підтримкою ROCm та RPC
- Налаштування RPC-воркерів і запуск розподіленого інференсу на чотирьох вузлах
- Запуск моделі з 1 трлн параметрів на чотирьох об'єднаних у мережу системах Ryzen AI Halo

## Налаштування конфігурації пам'яті

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (з Машини 1 по Машину 4).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Запуск моделей, близьких до 128 ГБ або більших:** На системах AMD Ryzen™ AI Max 400 Series (Gorgon Halo) під керуванням Windows моделі, розмір яких наближається до 128 ГБ пам'яті або перевищує його, потребують додаткового налаштування для роботи без помилок. Перед завантаженням моделі дотримуйтесь [рекомендацій AMD Ryzen AI Max PRO 400 Series для Windows OS](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines).
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
У Windows для запуску більших моделей, що потребують більшого обсягу пам'яті, нам потрібно використати виділення AMD Variable Graphics Memory (VRAM iGPU).

Це можна зробити, відкривши панель керування AMD Software: Adrenalin Edition та перейшовши до: `Performance > Tuning > AMD Variable Graphics Memory`. Встановіть значення **96 ГБ**. Перезавантажте систему, щоб зміни набули чинності.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
У Linux ROCm використовує спільний пул системної пам'яті, і за замовчуванням цей пул налаштований на половину обсягу системної пам'яті.

Цей обсяг можна збільшити, змінивши налаштування сторінок Translation Table Manager (TTM) ядра, скориставшись наведеними нижче інструкціями. AMD рекомендує встановити мінімальний обсяг виділеної VRAM у BIOS (0.5 ГБ).

* Встановіть утиліту pipx і додайте шлях до встановлених нею wheel-пакетів у системний шлях пошуку.

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

* Переналаштуйте параметри спільної пам'яті на **120 ГБ**:
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

Для цього посібника потрібні чотири пристрої Ryzen AI Halo та один Ethernet-комутатор, з'єднані за топологією "зірка", де кожен пристрій підключено безпосередньо до комутатора.

| Компонент | Кількість | Опис |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Обчислювальні вузли, що формують кластер |
| 10-гігабітний Ethernet-комутатор | 1 | Центральний комутатор для забезпечення зв'язку між вузлами Ryzen AI Halo (щонайменше 4 порти) |
| Ethernet-кабель | 4 | З'єднує кожен пристрій Halo з комутатором (рекомендовано Cat 7 або вище) |

> **Примітка**: Для підключення чотирьох пристроїв Ryzen AI Halo потрібно чотири порти Ethernet-комутатора. Якщо ви звертаєтеся до моделі з окремого клієнтського комп'ютера, а не з одного з пристроїв Halo, знадобиться п'ятий порт.

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

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (з Машини 1 по Машину 4).

Підключіть кожен пристрій Ryzen AI Halo до Ethernet-комутатора за допомогою кабелю Cat 7 (або вище). Це забезпечить 10-гігабітний канал зв'язку, що використовується для високошвидкісної комунікації між вузлами.
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

Підтвердіть, що з'єднання активне та працює на повній швидкості, перевіривши швидкість вашого інтерфейсу:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Примітка**: Замініть `<IFNAME>` на назву вихідного інтерфейсу з розділу [1. Визначення мережевих інтерфейсів](#1-determine-network-interfaces)

Ви маєте побачити швидкість `10000Mb/s`:

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

Ваш Ethernet-інтерфейс має бути у стані `Up` та працювати зі швидкістю `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Примітка**: Якщо швидкість нижче `10 Gbps` або з'єднання не встановлюється, перевірте підключення кабелю та переконайтеся, що порт комутатора налаштовано на 10 Гбіт/с. Деякі комутатори вимагають вимкнення автоузгодження та ручного встановлення швидкості з'єднання; зверніться до документації вашого комутатора.

<!-- @os:end -->

## Встановлення llama.cpp

> **Примітка**: Виконайте цей крок на всіх чотирьох машинах (з Машини 1 по Машину 4).

Доступні два варіанти встановлення:

- [Варіант 1: Lemonade SDK (Рекомендовано)](#option-1-lemonade-sdk-recommended) — готові бінарні файли, найшвидше налаштування
- [Варіант 2: Ручна збірка з вихідного коду](#option-2-manual-source-build) — збірка з вихідного коду з повним контролем над параметрами збірки
### Варіант 1: Lemonade SDK (рекомендовано)

Lemonade SDK надає нічні збірки llama.cpp з прискоренням AMD ROCm 7, орієнтовані на такі GPU, як gfx1151 (Strix Halo / Ryzen AI Max+ 395), та інші сучасні архітектури Radeon.

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

Цей каталог тепер містить збірки `llama-cli.exe`, `llama-server.exe` та `ggml-rpc-server.exe` з підтримкою ROCm, скомпільовані для вашої системи Ryzen AI Halo.

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

Цей каталог тепер містить збірки `llama-cli`, `llama-server` та `rpc-server` з підтримкою ROCm, скомпільовані для вашої системи Ryzen AI Halo.

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
Після підготовки llama.cpp на кожному вузлі перейдіть до [Завантаження моделі](#downloading-the-model).

### Варіант 2: Збирання з вихідного коду вручну

<!-- @os:windows -->
#### Крок 1: Збирання llama.cpp

Відкрийте **x64 Native Tools Command Prompt** (встановлюється разом із Visual Studio Build Tools) і клонуйте репозиторій:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Додайте HIP до шляху та зберіть з підтримкою ROCm і RPC:

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
| `-G Ninja` | Використовує систему збирання Ninja |

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

#### Крок 3: Додавання HIP до шляху користувача

Наведений вище крок збирання встановив `%HIP_PATH%\bin` лише для поточного сеансу. Щоб зробити бібліотеки HIP доступними в будь-якому терміналі (а не лише в x64 Native Tools Command Prompt), додайте його до `PATH` користувача на постійній основі:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Після підготовки llama.cpp на кожному вузлі перейдіть до [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Крок 1: Збирання llama.cpp

Клонуйте репозиторій:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Зберіть з підтримкою ROCm і RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Прапорець збірки | Призначення |
|-----------|---------|
| `-DGGML_HIP=ON` | Вмикає програмний стек ROCm |
| `-DGGML_RPC=ON` | Вмикає RPC для розподіленого інференсу |
| `-DAMDGPU_TARGETS="gfx1151"` | Орієнтується на GPU Ryzen AI Halo (Radeon 8060s) |

Додаткові параметри збирання наведено в [документації зі збирання llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

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

Після підготовки llama.cpp на кожному вузлі перейдіть до [Завантаження моделі](#downloading-the-model).
<!-- @os:end -->

## Завантаження моделі

У цьому посібнику використовується [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) у квантизації `UD-Q2_K_XL` від [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Ця квантизація вкладається в сукупний обсяг пам'яті GPU чотирьох вузлів Ryzen AI Halo.

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

> **Примітка**: завантаження моделі має бути завершене на Machine 1 (контролері). Робочим вузлам RPC (Machines 2, 3 та 4) не потрібна локальна копія файлів моделі.

## Запуск моделі в кластері

Рушій llama.cpp RPC (Remote Procedure Call) дозволяє одному екземпляру llama.cpp передавати шари моделі віддаленим робочим вузлам через мережу. Одна машина виконує роль **контролера** (Machine 1), відповідаючи за токенізацію, планування та оркестрацію. Три інші машини виконують легковагий **RPC-сервер** (Machines 2, 3 та 4), який надає контролеру доступ до своєї пам'яті GPU та обчислювальних ресурсів.

Під час завантаження llama.cpp розподіляє модель на всі чотири вузли (шардинг). Після завантаження інференс виконується так, ніби все працює на одному прискорювачі. RPC непомітно для користувача обробляє передачу тензорів і синхронізацію.

### Крок 1: Запуск RPC-серверів (Machines 2, 3 та 4)

На кожній з Machines 2, 3 та 4 запустіть RPC-сервер, щоб надати контролеру доступ до ресурсів GPU:
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
| `-c` | Вмикає локальний кеш для великих тензорів, уникаючи повторних передач мережею під час завантаження моделі |
| `--host` | IP-адреса для прив'язки RPC-сервера (`0.0.0.0` для всіх інтерфейсів) |

Додаткові параметри наведено в [документації RPC llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Крок 2: Запуск моделі (Machine 1)

Після запуску RPC-серверів на Machines 2, 3 та 4 запустіть інференс з Machine 1 за допомогою `llama-cli` або `llama-server`.
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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на кожній з машин 2, 3 та 4 виконайте команду `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: виконайте цю команду в терміналі (Powershell).

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на кожній з машин 2, 3 та 4 виконайте команду `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.

<!-- @os:end -->

Після запуску `llama-cli` відображає прогрес завантаження моделі та переходить у режим інтерактивного запиту, де ви можете спілкуватися з моделлю напряму:

![llama-cli running Kimi K2.6 across four nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` надає доступ до того самого механізму інференсу через постійний серверний процес із вбудованим веб-інтерфейсом та HTTP API, сумісним з OpenAI. Це кращий варіант інтерфейсу для довготривалих розгортань, доступу кількох користувачів та інтеграції із зовнішніми інструментами.

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на кожній з машин 2, 3 та 4 виконайте команду `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: виконайте цю команду в терміналі (Powershell).

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

> **Пошук `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: на кожній з машин 2, 3 та 4 виконайте команду `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

Після запуску відкрийте `http://<HOST_IP>:8081` у браузері, щоб отримати доступ до вбудованого веб-інтерфейсу. Це надає чат-інтерфейс на основі браузера для взаємодії з моделлю:

![llama-server web UI running Kimi K2.6 across four nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **Пошук `<HOST_IP>`**: на машині 1 виконайте команду `hostname -I | awk '{print $1}'`, щоб знайти її локальну IP-адресу.
<!-- @os:end -->

<!-- @os:windows -->
> **Пошук `<HOST_IP>`**: на машині 1 виконайте команду `ipconfig | findstr /C:"IPv4"` у терміналі (Powershell), щоб знайти її локальну IP-адресу.
<!-- @os:end -->

#### Довідник параметрів

| Прапорець | Призначення |
|------|---------|
| `-m` | Шлях до файлу моделі GGUF (використовуйте перший фрагмент, `00001-of-00008`) |
| `-c` | Розмір контексту в токенах. Більші значення використовують більше пам'яті |
| `-fa on` | Вмикає rocWMMA Flash Attention для покращеної продуктивності на GPU AMD |
| `-ngl 999` | Вивантажує всі шари моделі на GPU |
| `-lm none` | Встановлює режим завантаження моделі на `none`, вимикаючи відображення пам'яті (memory-mapping) для скорочення часу завантаження, коли розмір моделі перевищує обсяг системної RAM, але вміщується у VRAM |
| `-b` | Логічний розмір пакета в токенах. Встановлення значення 4096 забезпечує баланс між пропускною здатністю та використанням пам'яті на вузлах |
| `-ub` | Фізичний (мікро)розмір пакета для обробки запиту. Відповідність значенню `-b` дозволяє уникнути зайвих накладних витрат на фрагментацію |
| `--host` | IP-адреса, до якої прив'язується `llama-server` (лише для `llama-server`) |
| `--port` | Порт для обслуговування HTTP API (лише для `llama-server`) |
| `--rpc` | Список кінцевих точок RPC-воркерів через кому (`IP:port`) |

Повну інформацію про використання параметрів дивіться в [документації llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) та [документації llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Подальші кроки

- **Підключення сторонніх застосунків**: `llama-server` надає API, сумісний з OpenAI. Направте будь-який сумісний з OpenAI застосунок (наприклад, Open WebUI) на `http://<HOST_IP>:8081` із будь-яким заповнювальним API-ключем (наприклад, `none`), щоб підключитися до вашого кластера
- **Вивчення інших моделей**: перегляньте квантизовані GGUF на [Hugging Face](https://huggingface.co/models?search=gguf), щоб знайти моделі, які вміщуються в загальний обсяг пам'яті GPU вашого кластера
- **Масштабування за межі чотирьох вузлів**: додайте інші системи Ryzen AI Halo як додаткові RPC-воркери, щоб отримати доступ до моделей масштабом понад 1 трильйон параметрів. Передайте додаткові кінцеві точки в `--rpc` у вигляді списку через кому (наприклад, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)