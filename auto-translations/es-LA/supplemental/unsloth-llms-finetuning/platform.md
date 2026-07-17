# Configuración de la Plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Requisitos Previos

PyTorch con soporte para ROCm viene preinstalado en la AMD Ryzen™ AI Halo Developer Platform. Para todos los demás dispositivos, los usuarios deben instalar manualmente PyTorch con soporte para ROCm. Consulte la sección correspondiente a su sistema operativo:

### Windows

| Componente    | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


### Linux

| Componente    | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |


## Modelos Requeridos

Los siguientes modelos han sido probados y optimizados para su plataforma:

| Modelo | Parámetros | Tamaño | Ubicación de Descarga |
|--------|------------|--------|-----------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Descargar desde HF

Los modelos se descargarán automáticamente al directorio de caché de Hugging Face: `~/.cache/huggingface/hub/`

Asegúrese de contar con al menos **20 GB de espacio libre** para el almacenamiento de modelos.

## Requisitos de Red

La configuración inicial requiere acceso a internet para descargar modelos desde Hugging Face. Una vez descargados, el playbook puede ejecutarse sin conexión.

- Las primeras descargas de modelos pueden tardar **5 a 10 minutos** dependiendo del tamaño del modelo y la velocidad de conexión
- Los modelos se almacenan en caché localmente y no es necesario volver a descargarlos