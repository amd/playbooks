<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Comienza a codificar con OpenHands y Agent Canvas

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Descripción general

[OpenHands](https://github.com/All-Hands-AI/OpenHands) es un agente de software con IA
que puede escribir código, ejecutar comandos, navegar la web y editar archivos en un espacio
de trabajo real. En lugar de copiar sugerencias desde una ventana de chat, apuntas al
agente hacia una carpeta de proyecto y dejas que haga el trabajo: implementar una función, corregir
un error, escribir pruebas o explicar una base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) es la interfaz de navegador
recomendada para ejecutar OpenHands. Un único comando `agent-canvas` inicia el
servidor del agente, el backend de automatización y el frontend web en conjunto, para que puedas
mantener una conversación con el agente desde tu navegador.

Para mantener todo en tu sistema AMD, el agente se comunica con un modelo local servido
por Lemonade Server. Lemonade expone ese modelo a través de una API compatible con OpenAI,
así que Agent Canvas puede configurarlo como cualquier otro endpoint de estilo OpenAI
mientras el modelo, tu código y el contexto de la conversación permanecen todos en tu
máquina.

En este playbook, iniciarás un modelo local, lanzarás Agent Canvas, lo apuntarás
a ese modelo y ejecutarás tu primera tarea de codificación en una carpeta de proyecto real.

## Qué aprenderás

- Cómo iniciar Lemonade Server y confirmar que un modelo local responde solicitudes de chat
- Cómo instalar y lanzar Agent Canvas desde el paquete npm
- Cómo configurar Agent Canvas para usar un modelo local de Lemonade como LLM
- Cómo iniciar una conversación de OpenHands y observar al agente editar archivos y ejecutar
  comandos en un espacio de trabajo
- Cómo revisar lo que el agente cambió y guiarlo con mensajes de seguimiento

## Conceptos clave

| Concepto | Qué es | Dónde encaja en este playbook |
| --- | --- | --- |
| Lemonade Server | Una plataforma local de servicio de LLM diseñada para hardware AMD que expone una API compatible con OpenAI. Tus datos nunca salen de tu máquina. | Ejecuta el modelo que impulsa al agente. |
| OpenHands | Un agente de software con IA que lee y edita archivos, ejecuta comandos de shell y navega la web dentro de un espacio de trabajo. | El agente que controlas desde el chat. |
| Agent Canvas | La interfaz de navegador y el backend que ejecuta las conversaciones de OpenHands y muestra las llamadas a herramientas y los cambios de archivos. | Lanza el stack y aloja tu conversación. |
| Workspace (espacio de trabajo) | La carpeta de proyecto que el agente tiene permitido leer y modificar. | El objetivo de las ediciones y comandos del agente. |

<!-- @device:stx,krk -->
> [!NOTE]
> Los flujos de trabajo de agentes de codificación se benefician de un modelo más grande y una ventana de contexto mayor. Usa al
> menos 32 GB de memoria del sistema, y prefiere 64 GB o más para modelos GGUF más grandes.
<!-- @device:end -->

## Requisitos previos

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Necesitas:

- Lemonade Server instalado y capaz de servir el modelo a continuación.
- Node.js 22.12 o posterior y `npm` (usado por la CLI de `agent-canvas`).
- `uv`, el administrador de paquetes de Python que Agent Canvas usa para gestionar el entorno
  del servidor del agente. Si tu sistema aún no lo tiene, instálalo desde la
  [guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/)
  antes de lanzar Agent Canvas.
- Una carpeta de proyecto en la cual trabajar. Puede ser cualquier repositorio git local o
  directorio de código en el que quieras que trabaje el agente.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Inicia Lemonade Server

Inicia el modelo desde la CLI de Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade expone una API compatible con OpenAI en:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Verifica el modelo local

Confirma que Lemonade puede servir el modelo seleccionado:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Luego envía una pequeña solicitud de chat:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Si esto devuelve un arreglo `choices`, Lemonade está listo para Agent Canvas.

## 3. Instala y lanza Agent Canvas

Instala el paquete publicado de Agent Canvas de forma global:

```bash
npm install -g @openhands/agent-canvas
```

Luego inicia el stack completo desde una terminal:

```bash
agent-canvas
```

Por defecto, Agent Canvas se inicia en `http://localhost:8000`. Abre esa URL en
tu navegador. Si el puerto 8000 ya está en uso, pasa `--port` (o `-p`) al
lanzar Agent Canvas:

```bash
agent-canvas --port 3000
```

El mismo comando funciona en PowerShell en Windows. Luego abre
`http://localhost:3000` en su lugar. El backend local predeterminado debería mostrarse como
saludable en la pantalla de inicio.

El comando `agent-canvas` inicia el servidor del agente, el backend de automatización y
el frontend web en conjunto. Solo necesitas este único comando para ejecutar OpenHands
localmente.

## 4. Configura el LLM local

En el primer inicio, Agent Canvas abre un flujo de incorporación. En ese flujo:

1. Deja **OpenHands** seleccionado como agente y haz clic en **Next**.
2. En **Set up your LLM**, selecciona **Advanced**.
3. Deja **Authentication** configurado en **API key**.
4. Configura **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Configura **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Para **API Key**, ingresa cualquier marcador de posición no vacío como `lemonade-local`.
   Lemonade no requiere una clave real, pero el cliente de OpenHands necesita un valor
   para enviar.
7. Haz clic en **Next**.

La configuración avanzada completada debería verse así. El campo de la clave de API está
enmascarado por la interfaz.

![Configuración avanzada del LLM en Agent Canvas al primer uso con el modelo de Lemonade y la URL base local](assets/01-llm-advanced-settings.png)

Agent Canvas guarda estos valores como un perfil de LLM. Si tu versión te pide
nombrar ese perfil, usa un nombre sin espacios como `lemonade-local`. Si cambias
de modelo más adelante, abre **Settings > LLM** y actualiza los mismos campos avanzados. Puedes
cambiar entre perfiles guardados desde la entrada de chat con el comando `/model`.

## 5. Abre un espacio de trabajo

El agente solo puede leer y modificar archivos dentro de un espacio de trabajo que elijas. Antes de
iniciar una tarea, apunta Agent Canvas hacia tu carpeta de proyecto:

1. Desde la pantalla de inicio, elige **Open Workspace**.
2. Selecciona la carpeta que contiene tu proyecto (por ejemplo, un repositorio git
   en el que quieras que trabaje el agente).
3. Inicia una nueva conversación en ese espacio de trabajo.

Todo lo que hace el agente —leer archivos, ejecutar comandos, editar código— queda
limitado a ese espacio de trabajo.

![Pantalla de inicio de Agent Canvas después de la incorporación](assets/02-agent-canvas-home.png)
## 6. Ejecuta tu primera tarea de codificación

Con el espacio de trabajo abierto y el LLM local seleccionado, escribe una tarea concreta en
el chat. Una buena primera tarea es pequeña y verificable, por ejemplo:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observa la línea de tiempo de la conversación. OpenHands hará lo siguiente:

- Leer el espacio de trabajo para entender su estructura.
- Crear `hello.py` con la función solicitada y un bloque de prueba.
- Opcionalmente, ejecutar `python3 hello.py` para verificar la salida.
- Informar qué hizo y cualquier salida de comandos en el chat.

Deberías ver el nuevo archivo aparecer en el espacio de trabajo, y el mensaje final del
agente debería describir el cambio que hizo. Este es el momento clave: el
agente escribió y ejecutó código real en la carpeta de tu proyecto.

## 7. Revisa y guía al agente

Después de que el agente termine un paso, revisa su trabajo antes de aceptar el siguiente:

- **Cambios de archivos**: usa el explorador de archivos del espacio de trabajo o la vista de diferencias del agente para
  ver exactamente qué se agregó, cambió o eliminó.
- **Salida de comandos**: expande cualquier comando que el agente haya ejecutado para ver stdout, stderr,
  y el código de salida.
- **Seguimiento**: si el resultado no es lo que querías, responde en la misma
  conversación con una corrección. El agente mantiene el contexto anterior y
  itera sobre los mismos archivos.

Por ejemplo, si la prueba no imprimió el saludo esperado, responde:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

El agente volverá a leer el archivo, ejecutará el comando, diagnosticará el problema, y editará
el archivo nuevamente, todo dentro de la misma conversación.

## Solución de problemas

- **`agent-canvas` no está en el PATH:** reinstálalo con
  `npm install -g @openhands/agent-canvas` y confirma que el directorio del binario global de npm
  esté en tu PATH. En Windows, ejecuta `npm config get prefix`; el
  directorio devuelto, a menudo `%APPDATA%\npm` o `%USERPROFILE%\.npm-global`,
  debe estar en el PATH de tu usuario antes de que `agent-canvas` pueda iniciarse desde una nueva
  terminal.
- **`npm install -g` falla con un error de permisos:** configura un directorio
  global de npm propiedad del usuario, luego vuelve a abrir la terminal e instala Agent Canvas nuevamente.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Para hacer permanente el cambio de PATH en Windows, agrega `%USERPROFILE%\.npm-global` a
  el PATH de tu usuario desde **Configuración > Sistema > Acerca de > Configuración avanzada del sistema >
  Variables de entorno**, y abre una nueva terminal.
  <!-- @os:end -->
- **La interfaz carga pero el backend se muestra como no saludable (unhealthy):** espera unos segundos para que
  el servidor del agente termine de iniciarse, luego actualiza la página. Si sigue sin estar saludable, reinicia
  `agent-canvas` y revisa la salida de la terminal en busca de errores.
- **Las solicitudes de chat de Lemonade fallan con un error de conexión:** confirma que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` se ejecute correctamente y que
  Lemonade todavía esté sirviendo el modelo con `lemonade status`.
- **El agente muestra un error de longitud de contexto o límite de tokens:** reinicia
  Lemonade con un `ctx_size` más grande (por ejemplo, `ctx_size=65536`), e inicia una
  conversación nueva para que el agente no cargue con un historial demasiado grande.
- **El agente produce ediciones de baja calidad o incompletas:** cambia a un modelo
  más grande en Lemonade, o dale al agente una tarea más pequeña y concreta y deja que la
  termine antes de pedirle el siguiente cambio.
- **Falta `uv`:** instálalo desde
  [la guía de instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas usa `uv` para administrar el entorno de Python del servidor del agente.

## Próximos pasos

- Prueba una tarea más grande en el mismo espacio de trabajo, como agregar un archivo de prueba unitaria o
  corregir un error conocido, y revisa las diferencias del agente antes de conservar el cambio.
- Conecta un servidor MCP como GitHub o Slack en **Customize** para que
  el agente pueda leer incidencias (issues) o publicar actualizaciones mientras trabaja.
- Guarda varios perfiles de LLM (un modelo pequeño y rápido, y un modelo grande y más potente) y
  cambia entre ellos con `/model` en medio de la conversación.
- Continúa con [las automatizaciones de OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) para
  convertir flujos de desarrollo recurrentes en ejecuciones de agentes programadas o activadas por eventos.

## Recursos

- [Documentación de OpenHands](https://docs.openhands.dev/)
- [Resumen de Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuración de Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Perfiles de LLM y configuración de modelos](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentación de Lemonade Server](https://lemonade-server.ai/docs)