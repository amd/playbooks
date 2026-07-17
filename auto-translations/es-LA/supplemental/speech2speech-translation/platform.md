# Configuración de Plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Requisitos Previos

PyTorch con soporte para ROCm viene preinstalado en la AMD Ryzen™ AI Halo Developer Platform. Para todos los demás dispositivos, los usuarios deben instalar manualmente PyTorch con soporte para ROCm. Por favor, consulte la sección correspondiente a su sistema operativo:

### Windows

| Componente    | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 o más reciente | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

### Linux

| Componente    | Versión         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 o más reciente | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

## Modelos Requeridos

Los siguientes modelos han sido probados y optimizados para su plataforma:

| Modelo | Parámetros | Tamaño | Ubicación de Descarga |
|--------|------------|--------|-----------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Preinstalado en la AMD Ryzen AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |

Los modelos se descargarán automáticamente en el directorio de caché de Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Asegúrese de contar con al menos **20GB de espacio libre** para el almacenamiento de modelos.

## Requisitos de Red

La configuración inicial requiere acceso a internet para descargar modelos desde Hugging Face. Una vez descargados, el playbook puede ejecutarse sin conexión.

- Las primeras descargas de modelos pueden tardar **5 a 10 minutos** dependiendo del tamaño del modelo y la velocidad de conexión
- Los modelos se almacenan en caché localmente y no necesitan volver a descargarse