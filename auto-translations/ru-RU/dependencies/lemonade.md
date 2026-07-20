<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Установка Lemonade

<!-- @os:windows -->
Загрузите последний установщик с [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) и запустите файл `.msi`.

После установки:
- CLI `lemonade` автоматически добавляется в системный PATH
- Сервер Lemonade автоматически запускается в фоновом режиме

Вы также можете выполнить тихую установку из командной строки:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Сведения о других дистрибутивах или установке из исходного кода см. в разделе [полные варианты установки](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Проверка установки Lemonade

Откройте терминал и выполните:
```bash
lemonade --version
```

Вы должны увидеть вывод, подобный следующему:
```
lemonade version x.y.z
```

Если отображается номер версии, значит Lemonade установлен правильно и готов к работе.

Для быстрого доступа ниже приведены распространённые команды CLI Lemonade:

| Команда | Что делает |
| --- | --- |
| `lemonade --help` | Показывает все доступные команды и флаги. |
| `lemonade --version` | Выводит установленную версию Lemonade. |
| `lemonade status` | Подтверждает, запущен ли сервер Lemonade и доступен ли он. Базовый URL-адрес API, совместимого с OpenAI, по умолчанию — `http://localhost:13305/api/v1`. |
| `lemonade list` | Выводит список моделей, доступных в вашей установке Lemonade. |
| `lemonade pull <MODEL_NAME>` | Загружает модель без её запуска. |
| `lemonade run <MODEL_NAME>` | При необходимости загружает модель, затем запускает её для инференса/чата. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Запускает модель llama.cpp с бэкендом ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Запускает модель llama.cpp с бэкендом Vulkan. |
| `lemonade config` | Отображает текущие значения конфигурации Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Задаёт бэкенд llama.cpp по умолчанию как ROCm. |

Актуальные сведения о параметрах сервера Lemonade и устранении неполадок см. в [официальной документации Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).