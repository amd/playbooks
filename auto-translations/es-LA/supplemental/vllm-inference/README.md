<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa etiquetas especiales que GitHub no puede renderizar. Visita [amd.com/playbooks](https://amd.com/playbooks) para previsualizar este contenido correctamente.
<!-- @github-only:end -->


## Descripción general

vLLM es un motor de inferencia de alto rendimiento diseñado para modelos de lenguaje grandes (LLMs). Proporciona servicio optimizado con procesamiento por lotes continuo para alto rendimiento y una API compatible con OpenAI para una integración fluida de aplicaciones. Esto hace que vLLM sea ideal para implementaciones en producción donde la velocidad y la eficiencia de recursos son críticas.

Este playbook te enseña cómo servir LLMs usando vLLM en contenedores sobre el GPU integrado e interactuar con modelos a través de la API de Python de OpenAI.

## Lo que aprenderás

- Cómo configurar e iniciar un servidor vLLM con soporte AMD ROCm™
- Cómo interactuar con modelos a través de endpoints de API compatibles con OpenAI
- Cómo enviar prompts al servidor local con `vllm-prompt`

## Configuración de memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

> **Nota**: Si VS Code no está instalado, puedes instalarlo con AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de requisitos previos de software

Este playbook usa una imagen de contenedor precompilada que incluye vLLM, soporte para ROCm y los scripts auxiliares necesarios para iniciar el servidor. No necesitas instalar PyTorch, vLLM ni los scripts locales del playbook manualmente.

No hay un paso de instalación de vLLM en el host. Inicia vLLM con:

```bash
vllm-launch
```

El lanzador inicia el contenedor, apunta al GPU integrado y expone un servidor vLLM local compatible con OpenAI. Alternativamente, haz clic en el ícono de vLLM en la barra de tareas.

## Inicio rápido

### 1. Confirmar que el servidor vLLM está en ejecución

El comando `vllm-launch` puede tardar un par de minutos en inicializar todo. Una vez que inicia, el servidor está disponible en `http://localhost:8001`. Mantén abierta la terminal de lanzamiento porque el servidor se ejecuta en primer plano, luego abre una terminal separada para los pasos restantes. Los ejemplos a continuación usan `Qwen/Qwen3-1.7B`; si tu lanzador está configurado para un modelo diferente, sustituye ese ID de modelo en las solicitudes.

### 2. Enviar un prompt

Usa el script `vllm-prompt` proporcionado para enviar una solicitud al servidor vLLM local compatible con OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatear con el modelo usando la API de Python de OpenAI

Dado que vLLM expone una API compatible con OpenAI, puedes usar el paquete de Python `openai` para interactuar con él.

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

Crea un cliente `OpenAI` apuntando al servidor vLLM local en lugar de los servidores de OpenAI. El `api_key` es requerido por el cliente, pero vLLM no lo valida, por lo que cualquier cadena de texto funciona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Luego, envía una solicitud de completado de chat. Esto usa el mismo formato de mensajes que la API de OpenAI — una lista de mensajes con roles como `"user"` y `"assistant"`. Establecer `stream=True` significa que la respuesta llegará de forma incremental en lugar de toda a la vez:

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

Finalmente, itera sobre los fragmentos transmitidos e imprime cada parte del texto a medida que llega:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

El script incluido [chat_with_model.py](assets/chat_with_model.py) contiene el ejemplo completo y puede descargarse.


## Solución de problemas

### Conexión rechazada

Asegúrate de que el servidor esté en ejecución:
```bash
curl http://localhost:8001/health
```

## Resumen

En este playbook, aprendiste cómo:

- Iniciar vLLM en contenedores con soporte ROCm en el GPU integrado
- Iniciar un servidor vLLM con endpoints de API compatibles con OpenAI en el puerto 8001
- Enviar prompts con `vllm-prompt`
- Realizar llamadas a la API del servidor vLLM usando solicitudes con y sin streaming
- Solucionar problemas comunes con el inicio del servidor, la memoria y las conexiones del cliente

Ahora tienes una implementación de vLLM en contenedores para servir modelos de lenguaje grandes con rendimiento optimizado en el GPU integrado.

## Próximos pasos

- **Prueba diferentes modelos** — Cambia el modelo en la configuración de `vllm-launch` para experimentar con diferentes LLMs y comparar el rendimiento.
- **Construye una aplicación** — Usa la API compatible con OpenAI para integrar vLLM en una aplicación de Python, un chatbot o un flujo de trabajo de automatización.
- **Ajusta fino y sirve** — Ajusta fino un modelo usando LoRA o QLoRA, luego impleméntalo con vLLM para inferencia optimizada.

## Recursos adicionales

- **[Documentación oficial de vLLM](https://docs.vllm.ai/)** — Guías completas y referencias de API
- **[Repositorio de vLLM en GitHub](https://github.com/vllm-project/vllm)** — Código fuente, problemas y discusiones de la comunidad