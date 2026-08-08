<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# Конфигурация платформы

В этом документе описывается ожидаемая конфигурация платформы для запуска данного плейбука.

## Необходимые приложения и фреймворки

| Компонент       | Ожидаемая конфигурация               | Примечания                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python с поддержкой `venv`         | Используется для создания и активации `kernel-env`                                     |
| ROCm Python SDK | Семейство пакетов ROCm 7.13             | Устанавливается через процесс зависимостей плейбука                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Требуется для `torch.cuda`, среды выполнения HIP, JIT-компиляции и `CUDAExtension` |
| Драйвер GPU      | Драйвер AMD GPU с поддержкой ROCm/HIP | Требуется до того, как PyTorch сможет обнаружить AMD GPU                               |

> Примечание: при работе на AMD Ryzen™ AI Halo Developer Platform программное обеспечение AMD ROCm™ и PyTorch предустановлены.

## Требования для Linux

Требуются следующие системные пакеты:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` требуется для создания `kernel-env`.
* `build-essential`, `gcc` и `g++` требуются для примеров с расширениями на C++.
* `amd-smi` используется для проверки видимости и загрузки GPU в Linux.

Примеры расширений на C++ собирают нативные модули `.so` из файлов `.cu` с использованием механизма `CUDAExtension` из PyTorch.

## Требования для Windows

Для запуска на Windows требуется:

* Python, доступный через `python`
* Установите последнюю версию: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) или [более новую версию](https://visualstudio.microsoft.com/vs/community/) с нагрузкой **Desktop development with C++**

Среда Visual Studio C++ должна предоставлять:
* `vcvars64.bat`
* `cl.exe`
* Пути к заголовочным файлам и библиотекам Windows SDK

Примеры расширений на C++ собирают нативные модули `.pyd` из файлов `.cu` с использованием механизма `CUDAExtension` из PyTorch.