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

# Віддалена розробка за допомогою AMD Sync

## Огляд

**AMD Sync** перетворює ваш ноутбук на віддалену кабіну керування для AMD Ryzen™ AI Halo. Забудьте про ручне налаштування SSH, ключів та IDE — встановіть AMD Sync і отримайте доступ одним клацанням до віддаленого терміналу, VS Code, JupyterLab та панелі моніторингу GPU/CPU/пам'яті в реальному часі на Ryzen AI Halo.

Ваш локальний комп'ютер залишається звичним; кожна команда, блокнот і модель виконуються на Ryzen AI Halo.

> **Порада**: На цій сторінці буде розміщено всі нові оновлення AMDSync. 

## Чого ви навчитеся

- Вмикати SSH на Ryzen AI Halo та підключатися до нього з AMD Sync
- Запускати VS Code, Terminal, JupyterLab та Live Metrics на Ryzen AI Halo одним клацанням
- Організовувати віддалену роботу за допомогою керованих папок проєктів AMD Sync

---

## Основні поняття

AMD Sync має два боки: **клієнт** (ваш ноутбук, на якому працює застосунок AMD Sync) і **сервер** (Ryzen AI Halo, на якому працює SSH-сервер, до якого AMD Sync прокладає тунель). Усе, що ви запускаєте з AMD Sync — VS Code, термінал, блокнот — відкривається локально, але виконується на Ryzen AI Halo.

> **Підтримувані клієнти:** Windows 11 та Linux. macOS не підтримується.

---

## Крок 1 — Увімкнення SSH на Ryzen AI Halo


> **Примітка:** У Windows Ryzen AI Halo постачається з SSH-сервером, *вимкненим за замовчуванням*. У Linux SSH-сервер *увімкнено за замовчуванням*.

1. На Ryzen AI Halo відкрийте **AMD Ryzen™ AI Developer Center**.
2. Перейдіть на вкладку **Remote**.
3. Увімкніть перемикач **SSH Server**.
4. Запам'ятайте **IP Address**, **Port** та **Username**, показані в розділі **Server Information** — вам потрібно буде вставити їх в AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примітка:** Це AMD Developer Center для Windows. У версії для Linux інтерфейс може відрізнятися, але функціональність віддаленого доступу подібна.

> **Порада:** AMD Sync запитує **пароль для входу в ОС** цього користувача, а не пароль з Developer Center.

---

## Крок 2 — Встановлення AMD Sync на клієнтському пристрої

AMD Sync працює на Windows 11 та Linux. Завантажте інсталятор для вашої ОС, а потім виконайте наведені нижче кроки. Після встановлення натисніть **Accept & Install** на екрані **Get Started** — AMD Sync запуститься автоматично після завершення.

### Windows

[Завантажити AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Двічі клацніть на `AMDSyncInstaller.exe`.
2. Натисніть **Accept & Install**.

> Якщо брандмауер Windows запитає дозвіл, надайте AMD Sync доступ до мережі, щоб він міг підключатися до Ryzen AI Halo через SSH.

### Linux

Клацніть на посилання, щоб завантажити бажаний формат:

| Формат | Завантаження | Команда встановлення |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примітка:** Ubuntu App Center може позначити локально відкритий файл `.deb` як *«Potentially unsafe»*. Це стандартне попередження для будь-якого стороннього локального інсталятора. Якщо подвійне клацання на `.deb` не спрацьовує, скористайтеся наведеною вище командою терміналу.

---

## Крок 3 — Підключення до вашого Ryzen AI Halo

Під час першого запуску AMD Sync показує форму **Add a Remote Device**. Заповніть її, використовуючи значення з вкладки **Remote** в Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Поле | Примітки |
|-------|-------|
| **Device Name** *(необов'язково)* | Зручна назва, наприклад `Ryzen AI Halo`. За замовчуванням використовується `Device 1`, `Device 2`, … |
| **Hostname or IP** | З вкладки Remote |
| **SSH Port** | З вкладки Remote (лише цифри) |
| **Username** | Ім'я вашого облікового запису ОС на Ryzen AI Halo |
| **Password** | Пароль для входу в ОС — приховується під час введення |

Натисніть **Add Device**. Після короткого екрана завантаження ви побачите повідомлення **«Connection Successful»** і потрапите на домашню сторінку, яка розташована в системному треї. Клацніть за межами вікна, щоб закрити його; AMD Sync продовжить працювати у фоновому режимі й буде доступний одним клацанням.

> **Якщо з'єднання не вдалося,** AMD Sync повертається до форми зі збереженими введеними значеннями. Зазвичай причинами є вимкнений SSH на Ryzen AI Halo, неправильний пароль або те, що обидва пристрої перебувають у різних мережах.

---

## Крок 4 — Запуск першого віддаленого інструмента

Домашня сторінка надає п'ять компонентів для запуску одним клацанням — усі доступні незалежно від того, яку ОС використовують клієнт і Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Що він робить |
|-----------|--------------|
| **Directory** | Дозволяє вибрати папку на Ryzen AI Halo, у якій відкриватимуться VS Code, Terminal і JupyterLab. За замовчуванням використовується керована робоча область `Documents/AMD_Sync`. |
| **VS Code** | Відкриває VS Code локально з SSH-тунелем до вибраної папки. |
| **Terminal** | Відкриває локальний термінал, підключений через SSH до Ryzen AI Halo, у вибраній папці. |
| **JupyterLab** | Запускає проєкт блокнота, підключений через SSH до Ryzen AI Halo, в межах вибраної папки. |
| **Live Metrics** | Перегляд у реальному часі використання GPU, пам'яті та CPU на Ryzen AI Halo. |

### Спробуйте VS Code

Для першого запуску спробуйте **VS Code**. Наведені нижче інструкції стосуються Linux, але досвід у Windows подібний.

1. Залиште **Directory** зі значенням за замовчуванням `~/Documents/AMD_Sync`.
2. Натисніть **VS Code**.
3. AMD Sync створить папку `Documents/AMD_Sync/Project_1` на Ryzen AI Halo та відкриє VS Code локально, з тунелем до неї.

Тепер ви редагуєте файли, що знаходяться на Ryzen AI Halo, за допомогою вашого локального налаштування VS Code. Створіть файл `helloworld.py`, додайте `print("hello world")`, відкрийте вбудований термінал (`` Ctrl + ` ``) і запустіть його:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Рядок стану показує **SSH: Linux** — доказ того, що ваш код виконується на Ryzen AI Halo, а не на вашому ноутбуці.
### Спробуйте термінал

Натисніть **Terminal**, щоб підключитися через SSH до тієї самої папки, не відриваючи рук від клавіатури.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

У Windows типовим терміналом є **PowerShell** — за потреби перемкніться на **Windows Command Prompt** у меню налаштувань. У Linux AMD Sync використовує типовий системний термінал.

---

## Як працює каталог

Розкривний список **Directory** — це найважливіший елемент керування в AMD Sync: саме він визначає, куди потрапляє кожен інструмент, який ви запускаєте на Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (типовий)** — запуск VS Code або JupyterLab звідси автоматично створює нову папку проєкту (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Наявні папки проєктів** — будь-яка безпосередня підпапка `AMD_Sync` (зокрема й папки, які ви створили вручну на Ryzen AI Halo) з'являється у розкривному списку. Остання папка, яку ви використовували, стає типовою наступного разу.
- **Власні шляхи** — введіть будь-який абсолютний шлях, щоб відкрити папку в іншому місці на Ryzen AI Halo. AMD Sync лише *відкриває* її — вона не створює папки поза `AMD_Sync`, а власні шляхи не зберігаються між сеансами.

Якщо власний шлях не працює, AMD Sync повідомить причину: неправильний синтаксис, папка не існує або шлях вказує на файл.

---

## Live Metrics і JupyterLab

- **Live Metrics** — панель показників у реальному часі для GPU, пам'яті та CPU. Найшвидший спосіб переконатися, що віддалене навчання дійсно навантажує апаратне забезпечення.
- **JupyterLab** — повноцінний проєкт-блокнот, підключений по SSH до Ryzen AI Halo, з власним вбудованим терміналом для поєднання комірок блокнота та команд оболонки, не виходячи з інтерфейсу.

---

## Налаштування та кілька пристроїв

Меню **Settings** містить три вкладки:

| Вкладка | Що охоплює |
|-----|----------------|
| **Devices** | Список усіх пристроїв Ryzen AI Halo, з якими вдалося успішно з'єднатися. Повторне підключення, редагування облікових даних або додавання нового пристрою. |
| **Information** | Посилання на документацію та підтримку на форумі. |
| **Customize** | Переміщення застосунку на робочому столі, перемикання типу терміналу (лише для Windows) та перевірка оновлень AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип терміналу (Windows)** — виберіть між **PowerShell** (типово) та **Windows Command Prompt**.
- **Тип терміналу (Linux)** — доступний лише типовий системний термінал.
- **Оновлення застосунку** — на цій вкладці зручно перевіряти та встановлювати нові версії AMD Sync прямо з інтерфейсу; окремий інструмент оновлення не потрібен.

> Пристрій з'являється у списку **Devices** лише після успішного першого підключення, тож невдалі спроби не захаращують список.

---

## Усунення несправностей

- **З'єднання одразу не вдається** — переконайтеся, що SSH-сервер увімкнено на вкладці **Remote** в Developer Center на Ryzen AI Halo.
- **Помилка неправильного пароля** — використовуйте свій **пароль входу в ОС** на Ryzen AI Halo, а не паролі з Developer Center.
- **Кнопка VS Code нічого не робить** — встановіть VS Code на клієнтському комп'ютері з [code.visualstudio.com](https://code.visualstudio.com).
- **Відсутня піктограма AMD Sync у треї (Linux/GNOME)** — встановіть і ввімкніть розширення AppIndicator.
- **Файл `.deb` не відкривається з файлового менеджера** — скористайтеся командою `sudo apt install ./AMDSyncInstaller.deb` у терміналі.
- **Налаштування з'являється знову при кожному запуску (Linux)**: розблокуйте зв'язку ключів входу або запустіть з параметром `--password-store=gnome-libsecret`, після чого один раз повторіть налаштування.

---