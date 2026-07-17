<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

Цей документ описує очікувану конфігурацію платформи для запуску цього посібника.

## Необхідні застосунки / фреймворки

| Компонент       | Очікувана конфігурація               | Примітки                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python з підтримкою `venv`         | Використовується для створення та активації `kernel-env`                                     |
| ROCm Python SDK | Пакетна сім'я ROCm 7.13             | Встановлюється через потік залежностей посібника                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Необхідний для `torch.cuda`, середовища виконання HIP, JIT-компіляції та `CUDAExtension` |
| GPU Driver      | Драйвер AMD GPU з підтримкою ROCm/HIP | Необхідний перед тим, як PyTorch зможе виявити AMD GPU                               |

> Примітка: Якщо ви працюєте на AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ та PyTorch попередньо встановлені.

## Передумови для Linux

Необхідні такі системні пакети:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` необхідний для створення `kernel-env`.
* `build-essential`, `gcc` та `g++` необхідні для покрокових прикладів розширень C++.
* `amd-smi` використовується для перевірки видимості та завантаженості GPU у Linux.

Приклади розширень C++ збирають нативні модулі `.so` з файлів `.cu` за допомогою шляху `CUDAExtension` у PyTorch.

## Передумови для Windows

Для запуску у Windows необхідно:

* Python, доступний через `python`
* Встановити останню версію: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) або [новішу версію](https://visualstudio.microsoft.com/vs/community/) з робочим навантаженням **Розробка для робочого столу на C++**

Середовище C++ у Visual Studio має надавати:
* `vcvars64.bat`
* `cl.exe`
* Шляхи до заголовних файлів та бібліотек Windows SDK

Приклади розширень C++ збирають нативні модулі `.pyd` з файлів `.cu` за допомогою шляху `CUDAExtension` у PyTorch.