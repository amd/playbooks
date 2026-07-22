<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y algunos pasos, comandos, descargas o disponibilidad de productos pueden variar según su idioma o región. Si algo no parece correcto, considere el playbook original en inglés como la fuente de verdad.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Aplicaciones/Frameworks requeridos

### Windows/Linux

- **Lemonade Server** debe estar instalado siguiendo la
  [guía de instalación de Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 o posterior** y `npm`, utilizados por la CLI de `agent-canvas`.
- **uv**, el administrador de paquetes de Python que Agent Canvas utiliza para gestionar el
  entorno del servidor de agentes. Instálalo desde la
  [guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modelos requeridos

### Windows/Linux

El siguiente modelo debe estar disponible en Lemonade Server antes de iniciar el
playbook.

| Tipo de modelo | ID del modelo | Notas |
| --- | --- | --- |
| Modelo de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servido por Lemonade Server en `http://127.0.0.1:13305/api/v1`. Utiliza un modelo GGUF más pequeño en dispositivos con menos de 32 GB de memoria. |

Inicia el modelo con:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
