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

## Prerrequisitos

PyTorch con soporte ROCm viene preinstalado en la AMD Ryzen™ AI Halo Developer Platform. Para todos los demás dispositivos, los usuarios deben instalar manualmente PyTorch con soporte ROCm. Consulta la sección correspondiente a tu sistema operativo:


### Windows

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


### Linux

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


## Modelos requeridos

Los siguientes modelos han sido probados y optimizados para tu plataforma:

| Modelo | Parámetros | Tamaño | Ubicación de descarga |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Descargar desde HF

Los modelos se descargarán automáticamente al directorio de caché de Hugging Face: `~/.cache/huggingface/hub/`

Asegúrate de tener al menos **20GB de espacio libre** para el almacenamiento de modelos.

## Requisitos de red

La configuración inicial requiere acceso a internet para descargar los modelos desde Hugging Face. Después de la descarga, el playbook puede ejecutarse sin conexión.

- Las primeras descargas de modelos pueden tardar entre **5 y 10 minutos**, dependiendo del tamaño del modelo y de la velocidad de la conexión
- Los modelos quedan almacenados en caché localmente y no es necesario volver a descargarlos