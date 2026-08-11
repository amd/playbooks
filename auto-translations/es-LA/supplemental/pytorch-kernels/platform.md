<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe la configuración de plataforma esperada para ejecutar este playbook.

## Aplicaciones/frameworks requeridos

| Componente       | Configuración esperada               | Notas                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python con soporte para `venv`         | Se usa para crear y activar `kernel-env`                                     |
| ROCm Python SDK | Familia de paquetes ROCm 7.13             | Instalado a través del flujo de dependencias del playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Requerido para `torch.cuda`, el runtime de HIP, la compilación JIT y `CUDAExtension` |
| Controlador de GPU      | Controlador de GPU de AMD con soporte para ROCm/HIP | Requerido antes de que PyTorch pueda detectar la GPU de AMD                               |

> Nota: Si estás ejecutando en AMD Ryzen™ AI Halo Developer Platform, el software AMD ROCm™ y PyTorch vienen preinstalados.

## Requisitos previos para Linux

Se requieren los siguientes paquetes del sistema:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* Se requiere `python3-venv` para crear `kernel-env`.
* Se requieren `build-essential`, `gcc` y `g++` para las guías de extensiones en C++.
* `amd-smi` se usa para las comprobaciones de visibilidad/utilización de GPU en Linux.

Los ejemplos de extensiones en C++ compilan módulos nativos `.so` a partir de archivos `.cu` utilizando la ruta `CUDAExtension` de PyTorch.

## Requisitos previos para Windows

Los ejecutores de Windows requieren:

* Python disponible a través de `python`
* Instalar la última versión de: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [una versión más reciente](https://visualstudio.microsoft.com/vs/community/) con la carga de trabajo **Desarrollo para el escritorio con C++**

El entorno de Visual Studio C++ debe proporcionar:
* `vcvars64.bat`
* `cl.exe`
* Rutas de inclusión y bibliotecas del Windows SDK

Los ejemplos de extensiones en C++ compilan módulos nativos `.pyd` a partir de archivos `.cu` utilizando la ruta `CUDAExtension` de PyTorch.