<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Встановлення Lemonade

<!-- @os:windows -->
Завантажте останній інсталятор з [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) та запустіть файл `.msi`. 

Після встановлення:
- CLI `lemonade` автоматично додається до системного PATH
- Сервер Lemonade автоматично запускається у фоновому режимі

Ви також можете встановити його безшумно з командного рядка:
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

Для інших дистрибутивів або встановлення з вихідного коду див. [повний перелік варіантів встановлення](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Перевірка встановлення Lemonade

Відкрийте термінал та виконайте:
```bash
lemonade --version
```

Ви повинні побачити вивід на кшталт:
```
lemonade version x.y.z
```

Якщо ви бачите номер версії, Lemonade встановлено правильно та готово до роботи.

Для швидкого довідника нижче наведено поширені команди Lemonade CLI:

| Команда | Що вона робить |
| --- | --- |
| `lemonade --help` | Показує всі доступні команди та прапорці. |
| `lemonade --version` | Виводить встановлену версію Lemonade. |
| `lemonade status` | Підтверджує, чи запущено сервер Lemonade та чи він доступний. Базова URL-адреса API, сумісного з OpenAI, за замовчуванням — `http://localhost:13305/api/v1`. |
| `lemonade list` | Показує список моделей, доступних у вашому налаштуванні Lemonade. |
| `lemonade pull <MODEL_NAME>` | Завантажує модель без її запуску. |
| `lemonade run <MODEL_NAME>` | Завантажує модель за потреби, а потім запускає її для інференсу/чату. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Запускає модель llama.cpp з бекендом ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Запускає модель llama.cpp з бекендом Vulkan. |
| `lemonade config` | Показує поточні значення конфігурації Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Встановлює бекенд llama.cpp за замовчуванням на ROCm. |

Щоб дізнатися про найновіші параметри сервера Lemonade або усунення несправностей, зверніться до [офіційної документації Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).