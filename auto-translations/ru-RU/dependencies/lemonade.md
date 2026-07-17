<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Установка Lemonade

<!-- @os:windows -->
Загрузите последнюю версию установщика с [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) и запустите файл `.msi`.

После установки:
- CLI `lemonade` автоматически добавляется в системный PATH
- Ожидается, что сервер Lemonade будет автоматически работать в фоновом режиме

Также можно выполнить тихую установку из командной строки:
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

Для других дистрибутивов или установки из исходного кода см. [полный список вариантов установки](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Проверка установки Lemonade

Откройте терминал и выполните:
```bash
lemonade --version
```

Вы должны увидеть вывод следующего вида:
```
lemonade version x.y.z
```

Если отображается номер версии, Lemonade установлен корректно и готов к работе.

Для быстрого ознакомления ниже приведены распространённые команды CLI Lemonade:

| Команда | Что делает |
| --- | --- |
| `lemonade --help` | Отображает все доступные команды и флаги. |
| `lemonade --version` | Выводит установленную версию Lemonade. |
| `lemonade status` | Подтверждает, запущен ли сервер Lemonade и доступен ли он. URL-адрес базового API, совместимого с OpenAI, по умолчанию: `http://localhost:13305/api/v1`. |
| `lemonade list` | Выводит список моделей, доступных в вашей конфигурации Lemonade. |
| `lemonade pull <MODEL_NAME>` | Загружает модель без её запуска. |
| `lemonade run <MODEL_NAME>` | При необходимости загружает модель, затем запускает её для инференса/чата. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Запускает модель llama.cpp с бэкендом ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Запускает модель llama.cpp с бэкендом Vulkan. |
| `lemonade config` | Отображает текущие значения конфигурации Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Устанавливает бэкенд llama.cpp по умолчанию на ROCm. |

Актуальные параметры сервера Lemonade и сведения об устранении неполадок см. в [официальной документации Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).