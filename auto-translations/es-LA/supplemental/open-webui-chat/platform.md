<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe la configuración de plataforma esperada para ejecutar este playbook.

## Aplicaciones/Frameworks necesarios

### Windows/Linux
Lemonade debe estar preinstalado desde [aquí](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (aplicación web frontend)
- **Lemonade Server** (servidor de modelos backend)

> Este playbook ejecuta **Lemonade** (servidor/app de Lemonade) de forma **nativa**. **Open WebUI** se ejecuta como un **contenedor** en Linux (mediante Podman) y como un **paquete de Python** en Windows. El paquete de PyPI `open-webui` solo es compatible con Python ≤ 3.12, por lo que el contenedor de Linux evita tener que gestionar versiones anteriores de Python.  

## Modelos (en Lemonade)

Los modelos deben descargarse dentro de la **aplicación Lemonade** (usando el Model Manager integrado) o mediante los comandos de gestión de modelos de Lemonade (`lemonade pull <model_name>`). Este playbook asume que los modelos recomendados a continuación ya están descargados y aparecen en el endpoint de la lista de modelos.

Verificar la disponibilidad de los modelos:
- Abrir: `http://localhost:13305/api/v1/models`
- Los modelos descargados se listarán bajo `"data"`.

### Modelos recomendados

| Capacidad | ID del modelo | Notas |
|---|----|-----|
| LLM (Entrada de texto → Salida de texto) | `Qwen3-4B-Hybrid` (o similar) | Cualquier modelo LLM de Lemonade para chat, completado de texto, programación o razonamiento |
| VLM (Imagen → Texto) | `Qwen3.5-4B-GGUF` (o cualquier modelo de la categoría **Vision**) | Cualquier modelo multimodal/con capacidad de visión que pueda tomar imágenes como parte de su entrada |
| Generación de imágenes (Texto → Imagen) | `SDXL-Turbo` (o cualquier modelo de la categoría **Image**) | Cualquier modelo de Stable Diffusion que genere imágenes a partir de un prompt de texto |
| Audio (Voz → Texto) | `Whisper-Large-v3` (o cualquier modelo de la categoría **Audio**) | Cualquier modelo ASR que convierta audio en texto |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Puertos utilizados

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Si estos puertos ya están en uso en su sistema, cámbielos al iniciar el/los servidor(es).