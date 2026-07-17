<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Віддалена розробка з AMD Sync

## Огляд

**AMD Sync** перетворює ваш ноутбук на віддалений пульт керування для AMD Ryzen™ AI Halo. Забудьте про ручне налаштування SSH, ключів та IDE — встановіть AMD Sync і отримайте доступ одним кліком до віддаленого термінала, VS Code, JupyterLab та живої панелі моніторингу GPU/CPU/пам'яті на Ryzen AI Halo.

Ваша локальна машина залишається звичною; кожна команда, ноутбук і модель виконуються на Ryzen AI Halo.

> **Порада**: На цій сторінці будуть розміщені всі нові оновлення AMDSync.

## Що ви дізнаєтесь

- Увімкнути SSH на Ryzen AI Halo та підключитися до нього з AMD Sync
- Запустити VS Code, Terminal, JupyterLab та Live Metrics для Ryzen AI Halo одним кліком
- Організувати віддалену роботу за допомогою керованих папок проєктів AMD Sync

---

## Основні концепції

AMD Sync має дві сторони: **клієнт** (ваш ноутбук, на якому запущено застосунок AMD Sync) та **сервер** (Ryzen AI Halo, на якому запущено SSH-сервер, до якого AMD Sync прокладає тунель). Усе, що ви запускаєте з AMD Sync — VS Code, термінал, ноутбук — відкривається локально, але виконується на Ryzen AI Halo.

> **Підтримувані клієнти:** Windows 11 та Linux. macOS не підтримується.

---

## Крок 1 — Увімкнення SSH на Ryzen AI Halo


> **Примітка:** У Windows SSH-сервер на Ryzen AI Halo *вимкнено за замовчуванням*. У Linux SSH-сервер *увімкнено за замовчуванням*.

1. На Ryzen AI Halo відкрийте **AMD Ryzen™ AI Developer Center**.
2. Перейдіть на вкладку **Remote**.
3. Увімкніть **SSH Server**.
4. Запишіть **IP Address**, **Port** та **Username**, що відображаються в розділі **Server Information** — ви вставите їх в AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примітка:** Це AMD Developer Center для Windows. Версія для Linux може мати інший інтерфейс, але схожу функціональність для віддаленої роботи.

> **Порада:** AMD Sync запитує **пароль входу в ОС** цього користувача, а не пароль з Developer Center.

---

## Крок 2 — Встановлення AMD Sync на клієнті

AMD Sync працює на Windows 11 та Linux. Завантажте інсталятор для вашої ОС, а потім виконайте наведені нижче кроки. Після встановлення натисніть **Accept & Install** на екрані **Get Started** — AMD Sync запуститься автоматично після завершення.

### Windows

[Завантажити AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Двічі клацніть `AMDSyncInstaller.exe`.
2. Натисніть **Accept & Install**.

> Якщо брандмауер Windows запитає дозвіл, надайте AMD Sync доступ до мережі, щоб він міг підключатися до Ryzen AI Halo через SSH.

### Linux

Натисніть посилання, щоб завантажити потрібний формат:

| Формат | Завантаження | Команда встановлення |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примітка:** Ubuntu App Center може позначити локально відкритий файл `.deb` як *«Potentially unsafe»*. Це стандартне попередження для будь-якого стороннього локального інсталятора. Якщо подвійне клацання на `.deb` не спрацьовує, скористайтеся командою в терміналі, наведеною вище.

---

## Крок 3 — Підключення до Ryzen AI Halo

Під час першого запуску AMD Sync відображає форму **Add a Remote Device**. Заповніть її, використовуючи значення з вкладки **Remote** у Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Поле | Примітки |
|-------|-------|
| **Device Name** *(необов'язково)* | Зручна мітка, наприклад `Ryzen AI Halo`. За замовчуванням: `Device 1`, `Device 2`, … |
| **Hostname or IP** | З вкладки Remote |
| **SSH Port** | З вкладки Remote (лише цифри) |
| **Username** | Ім'я вашого облікового запису ОС на Ryzen AI Halo |
| **Password** | Ваш пароль входу в ОС — відображається замаскованим під час введення |

Натисніть **Add Device**. Після короткого екрана завантаження ви побачите **«Connection Successful»** і потрапите на головний екран, який знаходиться в системному треї. Клацніть поза вікном, щоб закрити його; AMD Sync продовжує працювати і доступний одним кліком.

> **Якщо підключення не вдалося,** AMD Sync повертається до форми зі збереженими значеннями. Типові причини: SSH вимкнено на Ryzen AI Halo, неправильний пароль або два пристрої перебувають у різних мережах.

---

## Крок 4 — Запуск першого віддаленого інструменту

Головний екран надає п'ять компонентів з одним кліком — усі доступні незалежно від того, яку ОС використовують клієнт і Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Що робить |
|-----------|--------------|
| **Directory** | Вибирає папку на Ryzen AI Halo, в якій відкриватимуться VS Code, Terminal та JupyterLab. За замовчуванням — керований робочий простір `Documents/AMD_Sync`. |
| **VS Code** | Відкриває VS Code локально з SSH-тунелем до вибраної папки. |
| **Terminal** | Відкриває локальний термінал, підключений через SSH до Ryzen AI Halo, у вибраній папці. |
| **JupyterLab** | Запускає проєкт ноутбука, підключений через SSH до Ryzen AI Halo, в межах вибраної папки. |
| **Live Metrics** | Перегляд у реальному часі використання GPU, пам'яті та CPU на Ryzen AI Halo. |

### Спробуйте VS Code

Для першого запуску спробуйте **VS Code**.

1. Залиште **Directory** зі значенням за замовчуванням `~/Documents/AMD_Sync`.
2. Натисніть **VS Code**.
3. AMD Sync створить `Documents/AMD_Sync/Project_1` на Ryzen AI Halo та відкриє VS Code локально з тунелем до цієї папки.

Тепер ви редагуєте файли, що знаходяться на Ryzen AI Halo, за допомогою локального налаштування VS Code. Створіть `helloworld.py`, додайте `print("hello world")`, відкрийте вбудований термінал (`` Ctrl + ` ``) і запустіть його:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

У рядку стану відображається **SSH: Linux** — підтвердження того, що ваш код виконується на Ryzen AI Halo, а не на вашому ноутбуці.

### Спробуйте Terminal

Натисніть **Terminal**, щоб перейти до тієї самої папки через SSH без відриву від клавіатури.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

У Windows термінал за замовчуванням — **PowerShell** — перейдіть на **Windows Command Prompt** у меню Settings, якщо бажаєте. У Linux AMD Sync використовує стандартний системний термінал.

---

## Як працює Directory

Випадаючий список **Directory** — найважливіший елемент керування в AMD Sync: він визначає, де на Ryzen AI Halo відкриватиметься кожен запущений інструмент.

- **`~/Documents/AMD_Sync` (за замовчуванням)** — Запуск VS Code або JupyterLab звідси автоматично створює нову папку проєкту (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Існуючі папки проєктів** — Будь-який безпосередній дочірній елемент `AMD_Sync` (включно з папками, які ви створюєте вручну на Ryzen AI Halo) з'являється у випадаючому списку. Остання використана папка стає типовою наступного разу.
- **Власні шляхи** — Введіть будь-який абсолютний шлях, щоб відкрити папку в іншому місці на Ryzen AI Halo. AMD Sync лише *відкриває* її — він не створює папки поза `AMD_Sync`, і власні шляхи не зберігаються між сесіями.

Якщо власний шлях не працює, AMD Sync повідомить причину: неправильний синтаксис, папка не існує або шлях вказує на файл.

---

## Live Metrics та JupyterLab

- **Live Metrics** — Жива панель використання GPU, пам'яті та CPU. Найшвидший спосіб переконатися, що віддалений процес навчання дійсно задіює апаратне забезпечення.
- **JupyterLab** — Повноцінний проєкт ноутбука, підключений через SSH до Ryzen AI Halo, з власним вбудованим терміналом для поєднання комірок ноутбука та команд оболонки без виходу з інтерфейсу.

---

## Налаштування та кілька пристроїв

Меню **Settings** має три вкладки:

| Вкладка | Що охоплює |
|-----|----------------|
| **Devices** | Перелік усіх Ryzen AI Halo, до яких ви успішно підключалися. Повторне підключення, редагування облікових даних або додавання нового пристрою. |
| **Information** | Посилання на документацію та підтримку на форумі. |
| **Customize** | Зміна положення застосунку на робочому столі, вибір типу термінала (лише Windows) та перевірка оновлень AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип термінала (Windows)** — Виберіть між **PowerShell** (за замовчуванням) та **Windows Command Prompt**.
- **Тип термінала (Linux)** — Доступний лише стандартний системний термінал.
- **Оновлення застосунку** — Ця вкладка є правильним місцем для перевірки та встановлення нових версій AMD Sync з інтерфейсу; окремий інструмент оновлення не потрібен.

> Пристрій з'являється в розділі **Devices** лише після успішного першого підключення, тому невдалі спроби не засмічуватимуть список.

---

## Усунення несправностей

- **Підключення одразу не вдається** — Переконайтеся, що SSH-сервер увімкнено на вкладці **Remote** у Developer Center на Ryzen AI Halo.
- **Помилка неправильного пароля** — Використовуйте **пароль входу в ОС** на Ryzen AI Halo, а не паролі з Developer Center.
- **Кнопка VS Code не реагує** — Встановіть VS Code на клієнтській машині з [code.visualstudio.com](https://code.visualstudio.com).
- **Значок AMD Sync у треї відсутній (Linux/GNOME)** — Встановіть та увімкніть розширення AppIndicator.
- **`.deb` не відкривається з файлового менеджера** — Скористайтеся командою `sudo apt install ./AMDSyncInstaller.deb` у терміналі.

---