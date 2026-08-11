<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Descripción general

vLLM es un motor de inferencia de alto rendimiento diseñado para modelos de lenguaje grandes (LLM). Ofrece servicio optimizado con batching continuo para alto throughput y una API compatible con OpenAI para una integración de aplicaciones sin inconvenientes. Esto hace que vLLM sea excelente para implementaciones de producción donde la velocidad y la eficiencia de recursos son fundamentales.

Este playbook te enseña cómo servir LLMs usando vLLM en contenedores en la GPU integrada e interactuar con modelos a través de la API de Python de OpenAI.

## Qué aprenderás

- Cómo configurar e iniciar un servidor vLLM con soporte de AMD ROCm™
- Cómo interactuar con modelos a través de endpoints de API compatibles con OpenAI
- Cómo enviar prompts al servidor local con `vllm-prompt`

## Configuración de memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

> **Nota**: Si VS Code no está instalado, puedes instalarlo con AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

vLLM se ejecuta en un contenedor prediseñado con ROCm y sus dependencias ya preconfiguradas. No se requiere instalación adicional.

No hay un paso de instalación de vLLM del lado del host. Inicia vLLM con:

```bash
vllm-launch
```

El iniciador arranca el contenedor, apunta a la GPU integrada y expone un servidor vLLM local compatible con OpenAI. Alternativamente, haz clic en el ícono de vLLM en la barra de tareas.

## Inicio rápido

### 1. Confirma que el servidor vLLM esté en ejecución

`vllm-launch` puede tardar un par de minutos en inicializar todo. Una vez que arranca, el servidor está disponible en `http://localhost:8001`. Mantén abierta la terminal de lanzamiento porque el servidor se ejecuta en primer plano, luego abre una terminal separada para los pasos restantes. Los ejemplos a continuación usan `Qwen/Qwen3-1.7B`; si tu iniciador está configurado para un modelo diferente, sustituye ese ID de modelo en las solicitudes.

### 2. Envía un prompt

Usa el script `vllm-prompt` proporcionado para enviar una solicitud al servidor local vLLM compatible con OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Conversa con el modelo usando la API de Python de OpenAI

Dado que vLLM expone una API compatible con OpenAI, puedes usar el paquete de Python `openai` para interactuar con ella.

Primero, crea un entorno virtual de Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Instala el paquete de OpenAI
```bash
pip install openai
```

Crea un cliente `OpenAI` apuntando al servidor local de vLLM en lugar de a los servidores de OpenAI. El cliente requiere `api_key`, pero vLLM no lo valida, por lo que cualquier cadena funciona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Luego, envía una solicitud de finalización de chat. Esto usa el mismo formato de mensajes que la API de OpenAI: una lista de mensajes con roles como `"user"` y `"assistant"`. Establecer `stream=True` significa que la respuesta llegará de forma incremental en lugar de toda a la vez:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Finalmente, itera sobre los fragmentos transmitidos e imprime cada fragmento de texto a medida que llega:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

El script incluido [chat_with_model.py](assets/chat_with_model.py) contiene el ejemplo completo y se puede descargar.


## Elección y configuración de un modelo

Por defecto, `vllm-launch` sirve `Qwen/Qwen3-1.7B` como modelo de prueba en el puerto `8001`. Puedes cambiar el modelo, el puerto y los parámetros de servicio de vLLM sin reconstruir ni editar el contenedor.

### Modelos probados por AMD

Los siguientes modelos están preconfigurados y validados por AMD:

| Modelo | Notas |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modelo predeterminado. Liviano y rápido de cargar. |
| `openai/gpt-oss-20b` | Modelo más grande para respuestas de mayor calidad. |

### Lanzar un modelo diferente

Pasa el ID del modelo con `--model` (o `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Cambiar el puerto

Pasa un puerto superior a 1024 con `--port` (o `-p`); el predeterminado es `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Si cambias el puerto, apunta el `base_url` de tu cliente al mismo puerto (por ejemplo, `http://localhost:8080/v1`).

### Pasar parámetros adicionales de vLLM

Cualquier argumento adicional se reenvía directamente a vLLM, por lo que puedes ajustar el comportamiento del servicio, como la longitud de contexto o el tipo de dato. Hay dos formas de proporcionarlos.

**En línea**, después de las opciones del iniciador:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**De forma persistente**, en un archivo de configuración en `~/.local/share/vLLM/vllm-launch.conf`. Este archivo no existe por defecto; créalo y agrega tus argumentos como un arreglo de Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Usa `+=` para agregar a los argumentos predeterminados en lugar de reemplazarlos:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Para ver todas las opciones del iniciador en cualquier momento, ejecuta:

```bash
vllm-launch --help
```

### Dónde se almacenan los modelos

`vllm-launch` busca modelos en dos ubicaciones:

| Ubicación | Ruta |
|----------|------|
| Modelos del sistema | `/var/cache/models` |
| Modelos del usuario | `~/.local/share/vLLM/models` |

Puedes colocar un modelo descargado en cualquiera de los directorios y lanzarlo pasando su ruta o ID a `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Nota**: Se espera que ejecutar tu propio modelo descargado de esta manera funcione una vez que el modelo se coloque en uno de los directorios anteriores, pero este flujo de trabajo aún no ha sido validado oficialmente por AMD.

## Solución de problemas

### Conexión rechazada

Asegúrate de que el servidor esté en ejecución:
```bash
curl http://localhost:8001/health
```

## Resumen

En este playbook, aprendiste a:

- Iniciar vLLM en contenedores con soporte de ROCm en la GPU integrada
- Iniciar un servidor vLLM con endpoints de API compatibles con OpenAI en el puerto 8001
- Enviar prompts con `vllm-prompt`
- Realizar llamadas a la API al servidor vLLM usando solicitudes tanto en streaming como sin streaming
- Solucionar problemas comunes con el inicio del servidor, la memoria y las conexiones de cliente

Ahora tienes una implementación de vLLM en contenedores para servir modelos de lenguaje grandes con rendimiento optimizado en la GPU integrada.

## Próximos pasos

- **Prueba diferentes modelos** — Usa `vllm-launch --model <model>` para experimentar con diferentes LLMs y comparar el rendimiento (consulta [Elección y configuración de un modelo](#choosing-and-configuring-a-model)).
- **Construye una aplicación** — Usa la API compatible con OpenAI para integrar vLLM en una aplicación de Python, chatbot o flujo de trabajo de automatización.
- **Ajusta y sirve** — Ajusta un modelo usando LoRA o QLoRA, luego impleméntalo con vLLM para inferencia optimizada.
## Recursos adicionales

- **[Documentación oficial de vLLM](https://docs.vllm.ai/)** — Guías completas y referencias de API
- **[Repositorio de vLLM en GitHub](https://github.com/vllm-project/vllm)** — Código fuente, problemas y debates de la comunidad