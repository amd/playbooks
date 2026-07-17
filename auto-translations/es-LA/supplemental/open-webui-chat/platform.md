<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la Plataforma

Este documento describe la configuración de plataforma esperada para ejecutar este playbook.

## Aplicaciones/Frameworks Requeridos

### Windows/Linux
Lemonade debe estar preinstalado desde [aquí](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (aplicación web frontend)
- **Lemonade Server** (servidor de modelos backend)

> Este playbook ejecuta **Lemonade** (servidor/aplicación Lemonade) de forma **nativa**. **Open WebUI** se ejecuta como un **contenedor** en Linux (mediante Podman) y como un **paquete de Python** en Windows. El paquete `open-webui` de PyPI solo es compatible con Python ≤ 3.12, por lo que el contenedor de Linux evita tener que gestionar versiones anteriores de Python.

## Modelos (en Lemonade)

Los modelos deben descargarse dentro de la **aplicación Lemonade** (usando el Administrador de Modelos integrado) o mediante los comandos de gestión de modelos de Lemonade (`lemonade pull <model_name>`). Este playbook asume que los modelos recomendados a continuación están descargados y aparecen en el endpoint de lista de modelos.

Verificar disponibilidad de modelos:
- Abrir: `http://localhost:13305/api/v1/models`
- Los modelos descargados aparecerán listados bajo `"data"`.

### Modelos recomendados

| Capacidad | ID del Modelo | Notas |
|---|----|-----|
| LLM (Entrada de texto → Salida de texto) | `Qwen3-4B-Hybrid` (o similar) | Cualquier modelo LLM de Lemonade para chat, completado de texto, programación o razonamiento |
| VLM (Imagen → Texto) | `Qwen3.5-4B-GGUF` (o cualquier modelo en la categoría **Vision**) | Cualquier modelo multimodal/con capacidad de visión que pueda recibir imágenes como parte de su entrada |
| Generación de Imágenes (Texto → Imagen) | `SDXL-Turbo` (o cualquier modelo en la categoría **Image**) | Cualquier modelo Stable Diffusion que genere imágenes a partir de un prompt de texto |
| Audio (Voz → Texto) | `Whisper-Large-v3` (o cualquier modelo en la categoría **Audio**) | Cualquier modelo ASR que convierta audio en texto |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Puertos utilizados

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Si estos puertos ya están en uso en su sistema, cámbielos al iniciar el/los servidor(es).