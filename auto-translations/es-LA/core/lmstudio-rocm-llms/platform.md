<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la Plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Windows

### Instalación de LM Studio

LM Studio debe estar preinstalado:

| Componente | Versión | Ubicación |
|-----------|---------|----------|
| **LM Studio (Modelos + Misc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programa)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Caché)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Descarga de Modelos

Los siguientes modelos ya deben estar presentes en el directorio de modelos de LM Studio (`C:\Users\...\.lmstudio\models`):

| Dispositivo | Tipo de Modelo | Cuantización | Tamaño (GB) | Ubicación |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalación de LM Studio

Consulte [lmstudio.md](../../dependencies/lmstudio.md) para más detalles.

### Descarga de Modelos

Igual que en Windows.