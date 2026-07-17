<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la Plataforma

Este documento describe la configuración esperada de la plataforma para ejecutar este playbook.

## Aplicaciones / Frameworks Requeridos

| Componente      | Configuración Esperada               | Notas                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python con soporte `venv`          | Se usa para crear y activar `kernel-env`                                     |
| ROCm Python SDK | Familia de paquetes ROCm 7.13        | Instalado a través del flujo de dependencias del playbook                    |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Requerido para `torch.cuda`, el runtime HIP, compilación JIT y `CUDAExtension` |
| GPU Driver      | Controlador de AMD GPU con soporte ROCm/HIP | Requerido antes de que PyTorch pueda detectar la AMD GPU              |

> Nota: Si estás ejecutando en AMD Ryzen™ AI Halo Developer Platform, el software AMD ROCm™ y PyTorch vienen preinstalados.

## Requisitos Previos en Linux

Los siguientes paquetes del sistema son necesarios:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` es necesario para crear `kernel-env`.
* `build-essential`, `gcc` y `g++` son necesarios para los tutoriales de extensiones en C++.
* `amd-smi` se usa para verificar la visibilidad y utilización de la GPU en Linux.

Los ejemplos de extensiones en C++ compilan módulos `.so` nativos a partir de archivos `.cu` usando la ruta `CUDAExtension` de PyTorch.

## Requisitos Previos en Windows

Los ejecutores de Windows requieren:

* Python disponible a través de `python`
* Instalar la versión más reciente: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [una versión más reciente](https://visualstudio.microsoft.com/vs/community/) con la carga de trabajo **Desarrollo de escritorio con C++**

El entorno de C++ de Visual Studio debe proporcionar:
* `vcvars64.bat`
* `cl.exe`
* Rutas de inclusión y biblioteca del SDK de Windows

Los ejemplos de extensiones en C++ compilan módulos `.pyd` nativos a partir de archivos `.cu` usando la ruta `CUDAExtension` de PyTorch.