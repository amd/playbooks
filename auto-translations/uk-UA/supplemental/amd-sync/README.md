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

# Віддалена розробка з AMD Sync

## Огляд

**AMD Sync** перетворює ваш ноутбук на віддалену кабіну керування для AMD Ryzen™ AI Halo. Пропустіть ручне налаштування SSH, ключів та IDE — встановіть AMD Sync і отримайте доступ в один клік до віддаленого терміналу, VS Code, JupyterLab та живої панелі моніторингу GPU/CPU/пам'яті на Ryzen AI Halo.

Ваш локальний пристрій залишається звичним; кожна команда, ноутбук і модель виконуються на Ryzen AI Halo.

> **Порада**: Ця сторінка міститиме всі нові оновлення для AMDSync.

## Що ви дізнаєтесь

- Увімкнути SSH на Ryzen AI Halo та підключитися до нього з AMD Sync
- Запускати VS Code, термінал, JupyterLab та Live Metrics для Ryzen AI Halo одним кліком
- Організовувати віддалену роботу за допомогою керованих папок проєктів AMD Sync

---

## Основні концепції

AMD Sync має дві сторони: **клієнт** (ваш ноутбук, на якому запущено застосунок AMD Sync) і **сервер** (Ryzen AI Halo, на якому запущено сервер SSH, до якого AMD Sync прокладає тунель). Усе, що ви запускаєте з AMD Sync — VS Code, термінал, ноутбук — відкривається локально, але виконується на Ryzen AI Halo.

> **Підтримувані клієнти:** Windows 11 та Linux. macOS не підтримується.

---

## Крок 1 — Увімкніть SSH на Ryzen AI Halo


> **Примітка:** На Windows Ryzen AI Halo постачається з сервером SSH, *вимкненим за замовчуванням*. На Linux сервер SSH *увімкнено за замовчуванням*.

1. На Ryzen AI Halo відкрийте **AMD Ryzen™ AI Developer Center**.
2. Перейдіть на вкладку **Remote**.
3. Увімкніть перемикач **SSH Server**.
4. Занотуйте **IP Address**, **Port** та **Username**, показані в розділі **Server Information** — ви вставите їх в AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примітка:** Це AMD Developer Center для Windows. Версія для Linux може мати інший інтерфейс, але схожий функціонал віддаленого доступу.

> **Порада:** AMD Sync запитує **пароль входу в ОС** цього користувача, а не пароль з Developer Center.

---

## Крок 2 — Встановіть AMD Sync на клієнтському пристрої

AMD Sync працює на Windows 11 та Linux. Завантажте інсталятор для вашої ОС, а потім виконайте кроки нижче. Після встановлення натисніть **Accept & Install** на екрані **Get Started** — AMD Sync запуститься автоматично після завершення.

### Windows

[Завантажити AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Двічі клацніть на `AMDSyncInstaller.exe`.
2. Натисніть **Accept & Install**.

> Якщо брандмауер Windows видасть запит, дозвольте AMD Sync мережевий доступ, щоб він міг з'єднатися з Ryzen AI Halo через SSH.

### Linux

Натисніть на посилання, щоб завантажити потрібний формат:

| Формат | Завантаження | Команда встановлення |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примітка:** Ubuntu App Center може позначити локально відкритий файл `.deb` як *"Potentially unsafe."* Це стандартне попередження для будь-якого стороннього локального інсталятора. Якщо подвійний клік на `.deb` не спрацьовує, скористайтеся командою терміналу вище.

---

## Крок 3 — Підключіться до вашого Ryzen AI Halo

При першому запуску AMD Sync відображає форму **Add a Remote Device**. Заповніть її значеннями з вкладки **Remote** Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Поле | Примітки |
|-------|-------|
| **Device Name** *(необов'язково)* | Зручна назва, наприклад `Ryzen AI Halo`. За замовчуванням `Device 1`, `Device 2`, … |
| **Hostname or IP** | З вкладки Remote |
| **SSH Port** | З вкладки Remote (лише цифри) |
| **Username** | Ім'я вашого облікового запису ОС на Ryzen AI Halo |
| **Password** | Ваш пароль входу в ОС — приховується під час введення |

Натисніть **Add Device**. Після короткого екрана завантаження ви побачите **"Connection Successful"** та потрапите на головний екран, який розташований у системному треї. Клацніть поза вікном, щоб закрити його; AMD Sync продовжує працювати і доступний одним кліком.

> **Якщо з'єднання не вдалося,** AMD Sync повертається до форми зі збереженими вашими значеннями. Зазвичай причина в тому, що SSH вимкнено на Ryzen AI Halo, введено неправильний пароль, або обидва пристрої знаходяться в різних мережах.

---

## Крок 4 — Запустіть свій перший віддалений інструмент

Головний екран надає п'ять компонентів для запуску в один клік — усі доступні незалежно від того, яка ОС встановлена на клієнті та Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Що він робить |
|-----------|--------------|
| **Directory** | Обирає папку на Ryzen AI Halo, у якій відкриватимуться VS Code, Terminal та JupyterLab. За замовчуванням — керована робоча область `Documents/AMD_Sync`. |
| **VS Code** | Відкриває VS Code локально з SSH-тунелем до обраної папки. |
| **Terminal** | Відкриває локальний термінал, підключений через SSH до Ryzen AI Halo, в обраній папці. |
| **JupyterLab** | Запускає проєкт ноутбука, підключений через SSH до Ryzen AI Halo, в межах обраної папки. |
| **Live Metrics** | Перегляд у реальному часі використання GPU, пам'яті та CPU на Ryzen AI Halo. |

### Спробуйте VS Code

Для першого запуску спробуйте **VS Code**.

1. Залиште **Directory** зі значенням за замовчуванням `~/Documents/AMD_Sync`.
2. Натисніть **VS Code**.
3. AMD Sync створює `Documents/AMD_Sync/Project_1` на Ryzen AI Halo та відкриває VS Code локально, з тунелем до цієї папки.

Тепер ви редагуєте файли, які знаходяться на Ryzen AI Halo, за допомогою вашого локального налаштування VS Code. Створіть `helloworld.py`, додайте `print("hello world")`, відкрийте вбудований термінал (`` Ctrl + ` ``) і запустіть його:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Рядок стану показує **SSH: Linux** — доказ того, що ваш код виконується на Ryzen AI Halo, а не на вашому ноутбуку.
### Спробуйте Termina

Натисніть **Terminal**, щоб потрапити в ту саму папку через SSH, не відриваючи рук від клавіатури.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

У Windows типовим терміналом є **PowerShell** — за потреби переключіться на **Windows Command Prompt** у меню налаштувань. У Linux AMD Sync використовує ваш системний термінал за замовчуванням.

---

## Як працює каталог

Розкривний список **Directory** — це найважливіший елемент керування в AMD Sync: він визначає, куди потрапляє кожен запущений вами інструмент на Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (за замовчуванням)** — Запуск VS Code або JupyterLab звідси автоматично створює нову папку проєкту (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Наявні папки проєктів** — У розкривному списку з'являється будь-яка безпосередня підпапка `AMD_Sync` (включно з папками, які ви створили вручну на Ryzen AI Halo). Останню використану папку буде запропоновано за замовчуванням наступного разу.
- **Власні шляхи** — Введіть будь-який абсолютний шлях, щоб відкрити папку в іншому місці на Ryzen AI Halo. AMD Sync лише *відкриває* її — вона не створює папки за межами `AMD_Sync`, і власні шляхи не зберігаються між сеансами.

Якщо власний шлях не працює, AMD Sync повідомляє причину: неправильний синтаксис, папка не існує або шлях вказує на файл.

---

## Live Metrics і JupyterLab

- **Live Metrics** — Панель моніторингу використання GPU, пам'яті та CPU у реальному часі. Найшвидший спосіб переконатися, що віддалене навчання дійсно навантажує апаратне забезпечення.
- **JupyterLab** — Повноцінний проєкт із блокнотами, підключений через SSH до Ryzen AI Halo, з власним інтегрованим терміналом для поєднання комірок блокнота та команд оболонки, не виходячи з інтерфейсу користувача.

---

## Налаштування та кілька пристроїв

Меню **Settings** має три вкладки:

| Вкладка | Що охоплює |
|-----|----------------|
| **Devices** | Перелічує всі Ryzen AI Halo, до яких ви успішно підключалися. Повторне підключення, редагування облікових даних або додавання нового пристрою. |
| **Information** | Посилання на документацію та підтримку на форумі. |
| **Customize** | Перемістіть застосунок на робочому столі, перемкніть тип терміналу (лише для Windows) і перевірте наявність оновлень AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип терміналу (Windows)** — Виберіть між **PowerShell** (за замовчуванням) та **Windows Command Prompt**.
- **Тип терміналу (Linux)** — Доступний лише системний термінал за замовчуванням.
- **Оновлення застосунку** — Ця вкладка — правильне місце для перевірки та встановлення нових версій AMD Sync прямо з інтерфейсу користувача; окремий засіб оновлення не потрібен.

> Пристрій з'являється у розділі **Devices** лише після успішного першого підключення, тому невдалі спроби не захаращуватимуть список.

---

## Усунення несправностей

- **Підключення одразу не вдається** — Переконайтеся, що сервер SSH увімкнено на вкладці **Remote** в Developer Center на Ryzen AI Halo.
- **Помилка неправильного пароля** — Використовуйте **пароль для входу в ОС** на Ryzen AI Halo, а не паролі з Developer Center.
- **Кнопка VS Code нічого не робить** — Встановіть VS Code на клієнтському комп'ютері з [code.visualstudio.com](https://code.visualstudio.com).
- **Значок AMD Sync у треї відсутній (Linux/GNOME)** — Встановіть і увімкніть розширення AppIndicator.
- **Файл `.deb` не відкривається з файлового менеджера** — Використайте `sudo apt install ./AMDSyncInstaller.deb` у терміналі.

---