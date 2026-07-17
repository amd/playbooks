<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la Plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Aplicaciones/Frameworks Requeridos

### Windows/Linux

GAIA debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de Instalación de GAIA](../../dependencies/gaia.md).

Lemonade Server debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de Instalación de Lemonade](../../dependencies/lemonade.md).

## Modelos Requeridos

### Windows/Linux

El Agente Asesor de Hardware utiliza **Qwen3-Coder-30B** para el razonamiento del agente. Este modelo se descarga automáticamente durante `gaia init`. No se requieren descargas manuales de modelos.