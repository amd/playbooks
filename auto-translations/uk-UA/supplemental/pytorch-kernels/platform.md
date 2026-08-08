<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Конфігурація платформи

Цей документ описує очікувану конфігурацію платформи для виконання цього playbook.

## Необхідні застосунки/фреймворки

| Компонент       | Очікувана конфігурація               | Примітки                                                                     |
| --------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| Python          | Python з підтримкою `venv`           | Використовується для створення та активації `kernel-env`                     |
| ROCm Python SDK | Родина пакетів ROCm 7.13             | Встановлюється через процес встановлення залежностей playbook                 |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Необхідно для `torch.cuda`, середовища виконання HIP, JIT-компіляції та `CUDAExtension` |
| GPU Driver      | Драйвер AMD GPU з підтримкою ROCm/HIP | Необхідно, перш ніж PyTorch зможе виявити AMD GPU                            |

> Примітка: Якщо ви працюєте на AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software та PyTorch вже попередньо встановлені.

## Передумови для Linux

Потрібні наступні системні пакети:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` потрібен для створення `kernel-env`.
* `build-essential`, `gcc` та `g++` потрібні для прикладів з розширеннями C++.
* `amd-smi` використовується для перевірки видимості/використання GPU в Linux.

Приклади розширень C++ збирають нативні модулі `.so` з файлів `.cu`, використовуючи шлях `CUDAExtension` PyTorch.

## Передумови для Windows

Для запуску на Windows потрібно:

* Python, доступний через `python`
* Встановіть останню версію: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) або [новішу версію](https://visualstudio.microsoft.com/vs/community/) з робочим навантаженням **Desktop development with C++**

Середовище Visual Studio C++ має надавати:
* `vcvars64.bat`
* `cl.exe`
* Шляхи до заголовкових файлів та бібліотек Windows SDK

Приклади розширень C++ збирають нативні модулі `.pyd` з файлів `.cu`, використовуючи шлях `CUDAExtension` PyTorch.