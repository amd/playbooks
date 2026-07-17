<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

Этот документ описывает ожидаемую конфигурацию платформы для запуска данного сборника сценариев.

## Необходимые приложения / фреймворки

| Компонент       | Ожидаемая конфигурация               | Примечания                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python с поддержкой `venv`         | Используется для создания и активации `kernel-env`                                     |
| ROCm Python SDK | Семейство пакетов ROCm 7.13             | Устанавливается через поток зависимостей сборника сценариев                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Требуется для `torch.cuda`, среды выполнения HIP, JIT-компиляции и `CUDAExtension` |
| Драйвер GPU      | Драйвер AMD GPU с поддержкой ROCm/HIP | Требуется, прежде чем PyTorch сможет обнаружить AMD GPU                               |

> Примечание: Если вы работаете на AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ и PyTorch предустановлены.

## Предварительные требования для Linux

Необходимы следующие системные пакеты:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` требуется для создания `kernel-env`.
* `build-essential`, `gcc` и `g++` требуются для пошаговых руководств по расширениям C++.
* `amd-smi` используется для проверки видимости и загрузки GPU в Linux.

Примеры расширений C++ собирают нативные модули `.so` из файлов `.cu` с использованием пути `CUDAExtension` в PyTorch.

## Предварительные требования для Windows

Для запуска в Windows требуется:

* Python, доступный через `python`
* Установите последнюю версию: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) или [более новую версию](https://visualstudio.microsoft.com/vs/community/) с рабочей нагрузкой **Разработка классических приложений на C++**

Среда C++ в Visual Studio должна предоставлять:
* `vcvars64.bat`
* `cl.exe`
* Пути к заголовочным файлам и библиотекам Windows SDK

Примеры расширений C++ собирают нативные модули `.pyd` из файлов `.cu` с использованием пути `CUDAExtension` в PyTorch.