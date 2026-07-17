<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de Plataforma

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

| Tipo de Modelo | Cuantización | Tamaño | Ubicación |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalación de LM Studio

Consulte lmstudio.md (dentro de la carpeta de dependencias) para más detalles.

### Descarga de Modelos

Igual que en Windows.