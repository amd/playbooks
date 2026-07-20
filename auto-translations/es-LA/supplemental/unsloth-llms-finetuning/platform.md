# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Requisitos previos

PyTorch con soporte para ROCm viene preinstalado en la AMD Ryzen™ AI Halo Developer Platform. Para todos los demás dispositivos, los usuarios deben instalar PyTorch con soporte para ROCm manualmente. Consulta la sección correspondiente a tu sistema operativo:


### Windows

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


### Linux

| Componente     | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


## Modelos requeridos

Los siguientes modelos están probados y optimizados para tu plataforma:

| Modelo | Parámetros | Tamaño | Ubicación de descarga |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Descargar desde HF

Los modelos se descargarán automáticamente al directorio de caché de Hugging Face: `~/.cache/huggingface/hub/`

Asegúrate de tener al menos **20 GB de espacio libre** para el almacenamiento de modelos.

## Requisitos de red

La configuración inicial requiere acceso a internet para descargar los modelos desde Hugging Face. Después de la descarga, el playbook puede ejecutarse sin conexión.

- Las primeras descargas de modelos pueden tardar entre **5 y 10 minutos**, según el tamaño del modelo y la velocidad de conexión
- Los modelos se almacenan en caché localmente y no es necesario volver a descargarlos