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

## Aplicaciones/frameworks requeridos

### Windows/Linux

- **Lemonade Server** debe estar instalado siguiendo la
  [guía de instalación de Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 o posterior** y `npm`, utilizados por la CLI de `agent-canvas` y los servidores
  MCP iniciados con `npx`.
- **uv**, el administrador de paquetes de Python que Agent Canvas utiliza para gestionar el entorno
  del servidor de agentes. Instálalo desde la
  [guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modelos requeridos

### Windows/Linux

El siguiente modelo debe estar disponible en Lemonade Server antes de iniciar el
playbook.

| Tipo de modelo | ID del modelo | Notas |
| --- | --- | --- |
| Modelo de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servido por Lemonade Server en `http://127.0.0.1:13305/api/v1`. Usa un modelo GGUF más pequeño en dispositivos con menos de 32 GB de memoria. |

Inicia el modelo con:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Credenciales externas

Este playbook requiere:

- Un token de GitHub con acceso de lectura al repositorio que se está resumiendo.
- Un token de bot de Slack con acceso de escritura (`chat:write`) y lectura de canales.
- Un ID de equipo de Slack y el ID del canal de Slack de destino.