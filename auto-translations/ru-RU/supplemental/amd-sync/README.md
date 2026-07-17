<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Удалённая разработка с AMD Sync

## Обзор

**AMD Sync** превращает ваш ноутбук в удалённый пульт управления AMD Ryzen™ AI Halo. Забудьте о ручной настройке SSH, ключей и IDE — установите AMD Sync и получите доступ в один клик к удалённому терминалу, VS Code, JupyterLab и живой панели мониторинга GPU/CPU/памяти на Ryzen AI Halo.

Ваша локальная машина остаётся привычной; каждая команда, ноутбук и модель выполняются на Ryzen AI Halo.

> **Совет**: На этой странице будут публиковаться все новые обновления AMDSync.

## Что вы узнаете

- Как включить SSH на Ryzen AI Halo и подключиться к нему из AMD Sync
- Как запустить VS Code, Terminal, JupyterLab и Live Metrics для Ryzen AI Halo одним кликом
- Как организовать удалённую работу с помощью управляемых папок проектов AMD Sync

---

## Основные концепции

AMD Sync состоит из двух частей: **клиент** (ваш ноутбук, на котором запущено приложение AMD Sync) и **сервер** (Ryzen AI Halo, на котором работает SSH-сервер, через который AMD Sync создаёт туннель). Всё, что вы запускаете из AMD Sync — VS Code, терминал, ноутбук — открывается локально, но выполняется на Ryzen AI Halo.

> **Поддерживаемые клиенты:** Windows 11 и Linux. macOS не поддерживается.

---

## Шаг 1 — Включение SSH на Ryzen AI Halo


> **Примечание:** В Windows Ryzen AI Halo поставляется с SSH-сервером, *отключённым по умолчанию*. В Linux он поставляется с SSH-сервером, *включённым по умолчанию*.

1. На Ryzen AI Halo откройте **AMD Ryzen™ AI Developer Center**.
2. Перейдите на вкладку **Remote**.
3. Включите переключатель **SSH Server**.
4. Запишите **IP-адрес**, **порт** и **имя пользователя**, отображаемые в разделе **Server Information** — они понадобятся для ввода в AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Примечание:** Это AMD Developer Center для Windows. Версия для Linux может иметь другой интерфейс, но аналогичную функциональность удалённого доступа.

> **Совет:** AMD Sync запрашивает **пароль входа в ОС** для этого пользователя, а не пароль из Developer Center.

---

## Шаг 2 — Установка AMD Sync на клиентской машине

AMD Sync работает на Windows 11 и Linux. Скачайте установщик для вашей ОС и следуйте инструкциям ниже. После установки нажмите **Accept & Install** на экране **Get Started** — AMD Sync запустится автоматически по завершении.

### Windows

[Скачать AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Дважды щёлкните `AMDSyncInstaller.exe`.
2. Нажмите **Accept & Install**.

> Если брандмауэр Windows выдаст запрос, разрешите AMD Sync доступ к сети, чтобы он мог подключаться к Ryzen AI Halo по SSH.

### Linux

Нажмите на ссылку, чтобы скачать предпочтительный формат:

| Формат | Скачать | Команда установки |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Примечание:** Ubuntu App Center может пометить локально открытый файл `.deb` как *«Potentially unsafe»*. Это стандартное предупреждение для любого стороннего локального установщика. Если двойной щелчок по файлу `.deb` не работает, воспользуйтесь командой в терминале, указанной выше.

---

## Шаг 3 — Подключение к Ryzen AI Halo

При первом запуске AMD Sync отображает форму **Add a Remote Device**. Заполните её, используя значения из вкладки **Remote** в Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Поле | Примечания |
|-------|-------|
| **Device Name** *(необязательно)* | Понятная метка, например `Ryzen AI Halo`. По умолчанию: `Device 1`, `Device 2`, … |
| **Hostname or IP** | Из вкладки Remote |
| **SSH Port** | Из вкладки Remote (только цифры) |
| **Username** | Имя вашей учётной записи ОС на Ryzen AI Halo |
| **Password** | Пароль входа в ОС — скрывается при вводе |

Нажмите **Add Device**. После короткого экрана загрузки вы увидите **«Connection Successful»** и попадёте на главный экран, который находится в системном трее. Щёлкните за пределами окна, чтобы закрыть его; AMD Sync продолжит работу и будет доступен в один клик.

> **Если подключение не удалось,** AMD Sync вернётся к форме с сохранёнными значениями. Обычные причины: SSH отключён на Ryzen AI Halo, неверный пароль или устройства находятся в разных сетях.

---

## Шаг 4 — Запуск первого удалённого инструмента

Главный экран предоставляет пять компонентов с запуском в один клик — все они доступны независимо от того, какую ОС используют клиент и Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Компонент | Что делает |
|-----------|--------------|
| **Directory** | Выбирает папку на Ryzen AI Halo, в которой будут открываться VS Code, Terminal и JupyterLab. По умолчанию — управляемое рабочее пространство `Documents/AMD_Sync`. |
| **VS Code** | Открывает VS Code локально с SSH-туннелем в выбранную папку. |
| **Terminal** | Открывает локальный терминал, подключённый по SSH к Ryzen AI Halo, в выбранной папке. |
| **JupyterLab** | Запускает проект с ноутбуками, подключённый по SSH к Ryzen AI Halo, в рамках выбранной папки. |
| **Live Metrics** | Отображение в реальном времени использования GPU, памяти и CPU на Ryzen AI Halo. |

### Попробуйте VS Code

Для первого запуска попробуйте **VS Code**.

1. Оставьте **Directory** на значении по умолчанию `~/Documents/AMD_Sync`.
2. Нажмите **VS Code**.
3. AMD Sync создаст `Documents/AMD_Sync/Project_1` на Ryzen AI Halo и откроет VS Code локально с туннелем в эту папку.

Теперь вы редактируете файлы, которые находятся на Ryzen AI Halo, используя локальную установку VS Code. Создайте `helloworld.py`, добавьте `print("hello world")`, откройте встроенный терминал (`` Ctrl + ` ``) и запустите его:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

В строке состояния отображается **SSH: Linux** — подтверждение того, что ваш код выполняется на Ryzen AI Halo, а не на вашем ноутбуке.

### Попробуйте Terminal

Нажмите **Terminal**, чтобы перейти в ту же папку по SSH, не отрываясь от клавиатуры.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

В Windows терминал по умолчанию — **PowerShell** — переключитесь на **Windows Command Prompt** в меню Settings, если предпочитаете его. В Linux AMD Sync использует системный терминал по умолчанию.

---

## Как работает Directory

Выпадающий список **Directory** — самый важный элемент управления в AMD Sync: он определяет, в какую папку на Ryzen AI Halo попадёт каждый запускаемый инструмент.

- **`~/Documents/AMD_Sync` (по умолчанию)** — При запуске VS Code или JupyterLab отсюда автоматически создаётся новая папка проекта (`Project_1`, `Project_2`, … для VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … для JupyterLab).
- **Существующие папки проектов** — Любая непосредственная дочерняя папка `AMD_Sync` (включая папки, созданные вручную на Ryzen AI Halo) отображается в выпадающем списке. Последняя использованная папка становится папкой по умолчанию при следующем запуске.
- **Пользовательские пути** — Введите любой абсолютный путь, чтобы открыть папку в другом месте на Ryzen AI Halo. AMD Sync только *открывает* её — папки за пределами `AMD_Sync` не создаются, а пользовательские пути не сохраняются между сессиями.

Если пользовательский путь не работает, AMD Sync сообщит причину: неверный синтаксис, папка не существует или путь указывает на файл.

---

## Live Metrics и JupyterLab

- **Live Metrics** — Живая панель мониторинга использования GPU, памяти и CPU. Самый быстрый способ убедиться, что удалённый процесс обучения действительно задействует оборудование.
- **JupyterLab** — Полноценный проект с ноутбуками, подключённый по SSH к Ryzen AI Halo, со встроенным терминалом для совмещения ячеек ноутбука и команд оболочки без выхода из интерфейса.

---

## Настройки и несколько устройств

Меню **Settings** содержит три вкладки:

| Вкладка | Что охватывает |
|-----|----------------|
| **Devices** | Список всех Ryzen AI Halo, к которым вы успешно подключались. Повторное подключение, редактирование учётных данных или добавление нового устройства. |
| **Information** | Ссылки на документацию и поддержку на форуме. |
| **Customize** | Изменение положения приложения на рабочем столе, выбор типа терминала (только Windows) и проверка обновлений AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Тип терминала (Windows)** — Выбор между **PowerShell** (по умолчанию) и **Windows Command Prompt**.
- **Тип терминала (Linux)** — Доступен только системный терминал по умолчанию.
- **Обновления приложения** — Эта вкладка предназначена для проверки и установки новых версий AMD Sync прямо из интерфейса; отдельный инструмент обновления не требуется.

> Устройство появляется в разделе **Devices** только после успешного первого подключения, поэтому неудачные попытки не засоряют список.

---

## Устранение неполадок

- **Подключение немедленно прерывается** — Убедитесь, что SSH-сервер включён на вкладке **Remote** в Developer Center на Ryzen AI Halo.
- **Ошибка неверного пароля** — Используйте **пароль входа в ОС** на Ryzen AI Halo, а не пароли из Developer Center.
- **Кнопка VS Code не реагирует** — Установите VS Code на клиентской машине с сайта [code.visualstudio.com](https://code.visualstudio.com).
- **Значок AMD Sync в трее отсутствует (Linux/GNOME)** — Установите и включите расширение AppIndicator.
- **Файл `.deb` не открывается из файлового менеджера** — Используйте команду `sudo apt install ./AMDSyncInstaller.deb` в терминале.

---