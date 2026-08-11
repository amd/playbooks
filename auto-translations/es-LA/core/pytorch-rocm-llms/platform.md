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

## Requisitos previos

PyTorch con soporte de ROCm viene preinstalado en la AMD Ryzen™ AI Halo Developer Platform. Para todos los demás dispositivos, los usuarios deben instalar manualmente PyTorch con soporte de ROCm. Consulta la sección correspondiente a tu sistema operativo:

### Windows

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o más reciente    | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

### Linux

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o más reciente    | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

## Modelos requeridos

Los siguientes modelos están probados y optimizados para tu plataforma:

| Modelo | Parámetros | Tamaño | Ubicación de descarga |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

Los modelos se descargarán automáticamente al directorio de caché de Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Asegúrate de contar con al menos **50GB de espacio libre** para el almacenamiento de modelos.

## Requisitos de red

La configuración inicial requiere acceso a internet para descargar los modelos desde Hugging Face. Después de la descarga, el playbook puede ejecutarse sin conexión.

- Las primeras descargas de modelos pueden tardar entre **5 y 10 minutos**, dependiendo del tamaño del modelo y la velocidad de conexión
- Los modelos quedan almacenados en caché localmente y no es necesario volver a descargarlos