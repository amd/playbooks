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

**AMD Sync** перетворює ваш ноутбук на віддалену кабіну керування для AMD Ryzen™ AI Halo. Пропустіть ручне налаштування SSH, ключів та IDE — встановіть AMD Sync і отримайте доступ в один клік до віддаленого терміналу, VS Code, JupyterLab та панелі моніторингу GPU/CPU/пам'яті в реальному часі на Ryzen AI Halo.

Ваш локальний комп'ютер залишається звичним; кожна команда, ноутбук і модель виконуються на Ryzen AI Halo.

> **Порада**: Ця сторінка міститиме всі нові оновлення для AMDSync. 

## Що ви дізнаєтеся

- Як увімкнути SSH на Ryzen AI Halo та підключитися до нього з AMD Sync
- Як запускати VS Code, Terminal, JupyterLab та Live Metrics для Ryzen AI Halo в один клік
- Як організувати віддалену роботу за допомогою керованих папок проєктів AMD Sync

---

## Основні поняття

AMD Sync має дві сторони: **клієнт** (ваш ноутбук, на якому працює застосунок AMD Sync) та **сервер** (Ryzen AI Halo, на якому працює SSH-сервер, до якого AMD Sync прокладає тунель). Усе, що ви запускаєте з AMD Sync — VS Code, термінал, ноутбук — відкривається локально, але виконується на Ryzen AI Halo.

> **Підтримувані клієнти:** Windows 11 та Linux. macOS не підтримується.

---

## Крок 1 — Увімкнення SSH на Ryzen AI Halo


> **Примітка:** У Windows Ryzen AI Halo постачається з SSH-сервером, *вимкненим за замовчуванням*. У Linux SSH-сервер постачається *увімкненим за замовчуванням*.

1. На Ryzen AI Halo відкрийте **AMD Ryzen™ AI Developer Center**.
2. Перейдіть на вкладку **Remote**.
3. Увімкніть перемикач **SSH Server**.
4. Занотуйте **IP Address**, **Port** та **Username**, показані в розділі **Server Information** — ви вставите їх у AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примітка:** Це AMD Developer Center для Windows. Версія для Linux може мати інший інтерфейс, але подібну функціональність віддаленого доступу.

> **Порада:** AMD Sync запитує **пароль входу в ОС** цього користувача, а не пароль з Developer Center.

---

## Крок 2 — Встановлення AMD Sync на клієнті

AMD Sync працює на Windows 11 та Linux. Завантажте інсталятор для вашої ОС, а потім виконайте наведені нижче кроки. Після встановлення натисніть **Accept & Install** на екрані **Get Started** — AMD Sync запуститься автоматично після завершення.

### Windows

[Завантажити AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Двічі клацніть на `AMDSyncInstaller.exe`.
2. Натисніть **Accept & Install**.

> Якщо Брандмауер Windows видасть запит, дозвольте AMD Sync мережевий доступ, щоб він міг з'єднуватися з Ryzen AI Halo через SSH.

### Linux

Натисніть посилання, щоб завантажити бажаний формат:

| Формат | Завантаження | Команда встановлення |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примітка:** Ubuntu App Center може позначити локально відкритий `.deb` як *"Potentially unsafe"*. Це стандартне попередження для будь-якого стороннього локального інсталятора. Якщо подвійне клацання на `.deb` не спрацює, скористайтеся наведеною вище командою терміналу.

---

## Крок 3 — Підключення до вашого Ryzen AI Halo

Під час першого запуску AMD Sync показує форму **Add a Remote Device**. Заповніть її, використовуючи значення з вкладки **Remote** у Developer Center.

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

Натисніть **Add Device**. Після короткого екрана завантаження ви побачите **"Connection Successful"** і потрапите на головний екран, який розташовується в системному треї. Клацніть поза вікном, щоб закрити його; AMD Sync продовжує працювати і доступний в один клік.

> **Якщо з'єднання не вдалося,** AMD Sync повертається до форми зі збереженими введеними значеннями. Зазвичай причиною є вимкнений SSH на Ryzen AI Halo, неправильний пароль або те, що обидва пристрої перебувають у різних мережах.

---

## Крок 4 — Запуск першого віддаленого інструмента

Головний екран пропонує п'ять компонентів, доступних в один клік — усі вони доступні незалежно від того, яку ОС використовують клієнт та Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Що він робить |
|-----------|--------------|
| **Directory** | Обирає папку на Ryzen AI Halo, в якій відкриватимуться VS Code, Terminal та JupyterLab. За замовчуванням — керована робоча область `Documents/AMD_Sync`. |
| **VS Code** | Відкриває VS Code локально з SSH-тунелем до обраної папки. |
| **Terminal** | Відкриває локальний термінал, підключений через SSH до Ryzen AI Halo, в обраній папці. |
| **JupyterLab** | Запускає проєкт-ноутбук, підключений через SSH до Ryzen AI Halo, у межах обраної папки. |
| **Live Metrics** | Перегляд у реальному часі використання GPU, пам'яті та CPU на Ryzen AI Halo. |

### Спробуйте VS Code

Для першого запуску спробуйте **VS Code**.

1. Залиште **Directory** зі значенням за замовчуванням `~/Documents/AMD_Sync`.
2. Натисніть **VS Code**.
3. AMD Sync створює `Documents/AMD_Sync/Project_1` на Ryzen AI Halo і відкриває VS Code локально, з тунелем до неї.

Тепер ви редагуєте файли, що зберігаються на Ryzen AI Halo, за допомогою вашого локального налаштування VS Code. Створіть `helloworld.py`, додайте `print("hello world")`, відкрийте вбудований термінал (`` Ctrl + ` ``) і запустіть його:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Рядок стану показує **SSH: Linux** — доказ того, що ваш код виконується на Ryzen AI Halo, а не на вашому ноутбуці.
### Спробуйте Термінал

Натисніть **Termina**l, щоб перейти до тієї ж папки через SSH, не відриваючи рук від клавіатури.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

У Windows типовим терміналом є **PowerShell** — перемкніться на **Windows Command Prompt** у меню Settings, якщо надаєте перевагу йому. У Linux AMD Sync використовує типовий системний термінал.

---

## Як працює каталог

Спадне меню **Directory** — це найважливіший елемент керування в AMD Sync: саме воно визначає, куди потрапляє кожен інструмент, який ви запускаєте на Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (типовий)** — запуск VS Code або JupyterLab звідси автоматично створює нову проєктну папку (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Наявні проєктні папки** — будь-яка безпосередня дочірня папка `AMD_Sync` (зокрема папки, які ви створюєте вручну на Ryzen AI Halo) з'являється у спадному меню. Остання використана папка стає типовою наступного разу.
- **Власні шляхи** — введіть будь-який абсолютний шлях, щоб відкрити папку в іншому місці на Ryzen AI Halo. AMD Sync лише *відкриває* її — вона не створює папки поза межами `AMD_Sync`, а власні шляхи не зберігаються між сеансами.

Якщо власний шлях не працює, AMD Sync повідомляє причину: некоректний синтаксис, папка не існує або шлях вказує на файл.

---

## Метрики в реальному часі та JupyterLab

- **Live Metrics** — панель показників GPU, пам'яті та CPU у реальному часі. Найшвидший спосіб переконатися, що віддалений процес навчання справді навантажує апаратне забезпечення.
- **JupyterLab** — повноцінний проєкт-блокнот, підключений через SSH до Ryzen AI Halo, з власним вбудованим терміналом для поєднання комірок блокнота та команд оболонки, не виходячи з інтерфейсу.

---

## Налаштування та кілька пристроїв

Меню **Settings** має три вкладки:

| Вкладка | Що охоплює |
|-----|----------------|
| **Devices** | Перелічує кожен Ryzen AI Halo, до якого ви успішно підключалися. Перепідключення, редагування облікових даних або додавання нового пристрою. |
| **Information** | Посилання на документацію та підтримку на форумі. |
| **Customize** | Переміщення застосунку на робочому столі, перемикання типу термінала (лише Windows) та перевірка оновлень AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип термінала (Windows)** — виберіть між **PowerShell** (типовий) та **Windows Command Prompt**.
- **Тип термінала (Linux)** — доступний лише типовий системний термінал.
- **Оновлення застосунку** — ця вкладка є правильним місцем для перевірки й встановлення нових версій AMD Sync прямо з інтерфейсу; окремий засіб оновлення не потрібен.

> Пристрій з'являється у розділі **Devices** лише після успішного першого підключення, тож невдалі спроби не захаращуватимуть список.

---

## Усунення несправностей

- **Підключення одразу не вдається** — переконайтеся, що SSH-сервер увімкнено на вкладці **Remote** Ryzen AI Halo в Developer Center.
- **Помилка неправильного пароля** — використовуйте **пароль входу в ОС** на Ryzen AI Halo, а не паролі з Developer Center.
- **Кнопка VS Code нічого не робить** — встановіть VS Code на клієнтському комп'ютері з [code.visualstudio.com](https://code.visualstudio.com).
- **Значок AMD Sync у треї відсутній (Linux/GNOME)** — встановіть і увімкніть розширення AppIndicator.
- **Файл `.deb` не відкривається з файлового менеджера** — використайте `sudo apt install ./AMDSyncInstaller.deb` у терміналі.
- **Налаштування з'являються знову при кожному запуску (Linux)**: розблокуйте зв'язку ключів входу або запустіть з `--password-store=gnome-libsecret`, а потім один раз повторіть налаштування.

---