<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de Plataforma — Lemonade Local AI

Este documento describe el software preinstalado, las rutas de modelos y los requisitos previos específicos de la plataforma que asume este playbook.

## Software Preinstalado

| Software | Versión | Propósito |
|----------|---------|---------|
| Lemonade Server | Última versión | Servidor LLM local con API compatible con OpenAI |
| Python | 3.10–3.13 | Requerido para el ejemplo del cliente OpenAI en Python |

## Almacenamiento de Modelos Predeterminado

Los modelos descargados a través de Lemonade se almacenan utilizando la especificación de Hugging Face Hub:

| Plataforma | Ruta Predeterminada |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Para cambiar la ubicación de almacenamiento, configure la variable de entorno `HF_HOME`.

## Requisitos de Hardware

| Objetivo de Hardware | Requisitos |
|----------------|-------------|
| **CPU** | Cualquier procesador x86-64 moderno (AMD o Intel) |
| **GPU (Vulkan)** | Cualquier GPU con soporte de controlador Vulkan |
| **GPU (ROCm)** | AMD Radeon RX serie 7000/9000 o Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Procesador AMD Ryzen AI 300 series, Windows 11 |

## Requisitos de Red

- Se requiere conexión a Internet para la descarga inicial del modelo (1–25 GB según el modelo)
- No se requiere Internet después de que los modelos han sido descargados