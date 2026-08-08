<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Aplicaciones/Frameworks requeridos

### Windows/Linux

GAIA debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de instalación de GAIA](../../dependencies/gaia.md).

Lemonade Server debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de instalación de Lemonade](../../dependencies/lemonade.md).

## Modelos requeridos

### Windows/Linux

El Hardware Advisor Agent utiliza **Qwen3-Coder-30B** para el razonamiento del agente. Este modelo se descarga automáticamente durante `gaia init`. No se requieren descargas manuales de modelos.