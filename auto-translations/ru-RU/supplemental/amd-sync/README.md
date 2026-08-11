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

# Удалённая разработка с AMD Sync

## Обзор

**AMD Sync** превращает ваш ноутбук в удалённую кабину управления для AMD Ryzen™ AI Halo. Забудьте о ручной настройке SSH, ключей и IDE — установите AMD Sync и получите доступ в один клик к удалённому терминалу, VS Code, JupyterLab и панели мониторинга GPU/CPU/памяти в реальном времени на Ryzen AI Halo.

Ваша локальная машина остаётся привычной; каждая команда, ноутбук и модель выполняются на Ryzen AI Halo.

> **Совет**: На этой странице будут появляться все новые обновления AMDSync. 

## Что вы узнаете

- Как включить SSH на Ryzen AI Halo и подключиться к нему из AMD Sync
- Как запускать VS Code, Terminal, JupyterLab и Live Metrics для Ryzen AI Halo в один клик
- Как организовать удалённую работу с помощью управляемых папок проектов AMD Sync

---

## Основные концепции

AMD Sync состоит из двух сторон: **клиента** (ваш ноутбук, на котором запущено приложение AMD Sync) и **сервера** (Ryzen AI Halo, на котором запущен SSH-сервер, в который AMD Sync прокладывает туннель). Всё, что вы запускаете из AMD Sync — VS Code, терминал, ноутбук — открывается локально, но выполняется на Ryzen AI Halo.

> **Поддерживаемые клиенты:** Windows 11 и Linux. macOS не поддерживается.

---

## Шаг 1 — Включение SSH на Ryzen AI Halo


> **Примечание:** В Windows на Ryzen AI Halo SSH-сервер *отключён по умолчанию*. В Linux SSH-сервер *включён по умолчанию*.

1. На Ryzen AI Halo откройте **AMD Ryzen™ AI Developer Center**.
2. Перейдите на вкладку **Remote**.
3. Включите переключатель **SSH Server**.
4. Обратите внимание на **IP Address**, **Port** и **Username**, указанные в разделе **Server Information** — их нужно будет вставить в AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примечание:** Это AMD Developer Center для Windows. В версии для Linux интерфейс может отличаться, но функциональность удалённого доступа аналогична.

> **Совет:** AMD Sync запрашивает **пароль входа в ОС** для этого пользователя, а не пароль из Developer Center.

---

## Шаг 2 — Установка AMD Sync на клиентское устройство

AMD Sync работает на Windows 11 и Linux. Скачайте установщик для вашей ОС и выполните шаги, описанные ниже. После установки нажмите **Accept & Install** на экране **Get Started** — AMD Sync запустится автоматически по завершении.

### Windows

[Скачать AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Дважды щёлкните `AMDSyncInstaller.exe`.
2. Нажмите **Accept & Install**.

> Если брандмауэр Windows выдаст запрос, разрешите AMD Sync сетевой доступ, чтобы он мог подключаться к Ryzen AI Halo по SSH.

### Linux

Нажмите на ссылку, чтобы скачать нужный формат:

| Формат | Загрузка | Команда установки |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примечание:** Ubuntu App Center может пометить локально открытый файл `.deb` как *«Potentially unsafe»* (потенциально небезопасный). Это стандартное предупреждение для любого стороннего локального установщика. Если двойной щелчок по `.deb` не срабатывает, используйте команду терминала выше.

---

## Шаг 3 — Подключение к вашему Ryzen AI Halo

При первом запуске AMD Sync отображает форму **Add a Remote Device**. Заполните её, используя значения со вкладки **Remote** в Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Поле | Примечания |
|-------|-------|
| **Device Name** *(необязательно)* | Понятное название, например `Ryzen AI Halo`. По умолчанию `Device 1`, `Device 2`, … |
| **Hostname or IP** | Со вкладки Remote |
| **SSH Port** | Со вкладки Remote (только цифры) |
| **Username** | Имя вашей учётной записи ОС на Ryzen AI Halo |
| **Password** | Ваш пароль входа в ОС — скрывается при вводе |

Нажмите **Add Device**. После короткого экрана загрузки вы увидите сообщение **«Connection Successful»** и попадёте на главный экран, который находится в системном трее. Щёлкните за пределами окна, чтобы закрыть его; AMD Sync продолжит работать и будет доступен в один клик.

> **Если подключение не удалось,** AMD Sync вернётся к форме с сохранёнными введёнными значениями. Обычные причины — отключённый SSH на Ryzen AI Halo, неверный пароль или нахождение устройств в разных сетях.

---

## Шаг 4 — Запуск первого удалённого инструмента

Главный экран предоставляет пять компонентов с запуском в один клик — все они доступны независимо от того, какая ОС используется на клиенте и Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Что делает |
|-----------|--------------|
| **Directory** | Выбирает папку на Ryzen AI Halo, в которой будут открываться VS Code, Terminal и JupyterLab. По умолчанию — управляемое рабочее пространство `Documents/AMD_Sync`. |
| **VS Code** | Открывает VS Code локально с SSH-туннелем в выбранную папку. |
| **Terminal** | Открывает локальный терминал с SSH-подключением к Ryzen AI Halo в выбранной папке. |
| **JupyterLab** | Запускает проект ноутбука с SSH-подключением к Ryzen AI Halo в рамках выбранной папки. |
| **Live Metrics** | Отображение в реальном времени использования GPU, памяти и CPU на Ryzen AI Halo. |

### Попробуйте VS Code

Для первого запуска попробуйте **VS Code**.

1. Оставьте значение **Directory** по умолчанию — `~/Documents/AMD_Sync`.
2. Нажмите **VS Code**.
3. AMD Sync создаст `Documents/AMD_Sync/Project_1` на Ryzen AI Halo и откроет VS Code локально, с туннелем в эту папку.

Теперь вы редактируете файлы, находящиеся на Ryzen AI Halo, с помощью вашей локальной настройки VS Code. Создайте `helloworld.py`, добавьте `print("hello world")`, откройте встроенный терминал (`` Ctrl + ` ``) и запустите его:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Строка состояния показывает **SSH: Linux** — это подтверждает, что ваш код выполняется на Ryzen AI Halo, а не на вашем ноутбуке.
### Попробуйте терминал

Нажмите **Terminal**, чтобы попасть в ту же папку по SSH, не отрываясь от клавиатуры.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

В Windows терминалом по умолчанию является **PowerShell** — переключитесь на **Windows Command Prompt** в меню настроек, если предпочитаете его. В Linux AMD Sync использует системный терминал по умолчанию.

---

## Как работает Directory

Раскрывающийся список **Directory** — это самый важный элемент управления в AMD Sync: он определяет, куда попадает каждый запускаемый вами инструмент на Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (по умолчанию)** — запуск VS Code или JupyterLab из этой папки автоматически создаёт новую папку проекта (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Существующие папки проектов** — в списке появляется любая непосредственная дочерняя папка `AMD_Sync` (включая папки, которые вы создали вручную на Ryzen AI Halo). Последняя использованная папка становится значением по умолчанию в следующий раз.
- **Пользовательские пути** — введите любой абсолютный путь, чтобы открыть папку в другом месте на Ryzen AI Halo. AMD Sync только *открывает* её — она не создаёт папки за пределами `AMD_Sync`, а пользовательские пути не сохраняются между сеансами.

Если пользовательский путь не работает, AMD Sync сообщает причину: неверный синтаксис, папка не существует или путь указывает на файл.

---

## Live Metrics и JupyterLab

- **Live Metrics** — панель мониторинга в реальном времени, показывающая загрузку GPU, памяти и CPU. Самый быстрый способ убедиться, что удалённое обучение действительно задействует оборудование.
- **JupyterLab** — полноценный проект-блокнот, подключённый по SSH к Ryzen AI Halo, со встроенным терминалом для сочетания ячеек блокнота и команд оболочки без выхода из интерфейса.

---

## Настройки и несколько устройств

Меню **Settings** содержит три вкладки:

| Вкладка | Что охватывает |
|-----|----------------|
| **Devices** | Список всех Ryzen AI Halo, к которым вы успешно подключались. Переподключение, изменение учётных данных или добавление нового устройства. |
| **Information** | Ссылки на документацию и поддержку на форуме. |
| **Customize** | Перемещение приложения на рабочем столе, переключение типа терминала (только для Windows) и проверка обновлений AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип терминала (Windows)** — выбор между **PowerShell** (по умолчанию) и **Windows Command Prompt**.
- **Тип терминала (Linux)** — доступен только системный терминал по умолчанию.
- **Обновления приложения** — эта вкладка подходит для проверки и установки новых версий AMD Sync прямо из интерфейса; отдельный установщик обновлений не требуется.

> Устройство появляется во вкладке **Devices** только после успешного первого подключения, поэтому неудачные попытки не засоряют список.

---

## Устранение неполадок

- **Подключение сразу завершается ошибкой** — убедитесь, что SSH-сервер включён на вкладке **Remote** в Developer Center на Ryzen AI Halo.
- **Ошибка неверного пароля** — используйте **пароль входа в ОС** на Ryzen AI Halo, а не пароли из Developer Center.
- **Кнопка VS Code ничего не делает** — установите VS Code на клиентском компьютере с сайта [code.visualstudio.com](https://code.visualstudio.com).
- **Значок AMD Sync отсутствует в трее (Linux/GNOME)** — установите и включите расширение AppIndicator.
- **Файл `.deb` не открывается из файлового менеджера** — используйте команду `sudo apt install ./AMDSyncInstaller.deb` в терминале.

---