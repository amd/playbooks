<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma — Lemonade Local AI

Este documento describe el software preinstalado, las rutas de los modelos y los requisitos previos específicos de la plataforma que se asumen en este playbook.

## Software preinstalado

| Software | Versión | Propósito |
|----------|---------|-------------|
| Lemonade Server | Última versión | Servidor local de LLM con API compatible con OpenAI |
| Python | 3.10–3.13 | Necesario para el ejemplo del cliente de Python de OpenAI |

## Almacenamiento predeterminado de modelos

Los modelos descargados a través de Lemonade se almacenan siguiendo la especificación de Hugging Face Hub:

| Plataforma | Ruta predeterminada |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Para cambiar la ubicación de almacenamiento, configure la variable de entorno `HF_HOME`.

## Requisitos de hardware

| Objetivo de hardware | Requisitos |
|----------------|-------------|
| **CPU** | Cualquier procesador x86-64 moderno (AMD o Intel) |
| **GPU (Vulkan)** | Cualquier GPU con soporte de driver Vulkan |
| **GPU (ROCm)** | AMD Radeon serie RX 7000/9000 o Radeon PRO serie W7000; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesador AMD Ryzen AI serie 300, Windows 11 |

## Requisitos de red

- Se requiere conexión a internet para la descarga inicial del modelo (1–25 GB según el modelo)
- No se requiere internet después de descargar los modelos