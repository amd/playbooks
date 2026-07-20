<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Aplicaciones/Frameworks requeridos

### Windows/Linux

GAIA debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de instalación de GAIA](../../dependencies/gaia.md).

Lemonade Server debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de instalación de Lemonade](../../dependencies/lemonade.md).

## Modelos requeridos

### Windows/Linux

El Hardware Advisor Agent utiliza **Qwen3-Coder-30B** para el razonamiento del agente. Este modelo se descarga automáticamente durante `gaia init`. No se requieren descargas manuales de modelos.