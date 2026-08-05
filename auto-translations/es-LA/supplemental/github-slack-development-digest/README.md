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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Descripción general

Los desarrolladores dedican mucho tiempo a pequeños ciclos recurrentes: revisar
solicitudes de extracción (pull requests) etiquetadas, responder comentarios de GitHub, clasificar
nuevos issues, convertir hilos de Slack en notas de standup o seguimientos de incidentes, y
hacer seguimiento de señales de release o investigación. Cada ciclo es familiar, pero aún
requiere criterio: reunir el contexto correcto, decidir qué es importante, y publicar una
actualización clara donde el equipo ya trabaja.

[Las automatizaciones de OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
convierten esos ciclos en conversaciones de agente programadas o activadas por eventos: ejecuciones
donde un agente de software con IA puede leer contexto, invocar herramientas, y producir una actualización.
Las plantillas de automatización compartidas en el catálogo de extensiones de OpenHands siguen
este patrón para la revisión de pull requests de GitHub, el monitoreo de repositorios, la clasificación
de issues de Linear, las retrospectivas de incidentes, los digests de standup de Slack, y los resúmenes
de investigación: una automatización se activa, usa integraciones configuradas como GitHub o
Slack para obtener contexto, razona sobre ese contexto con un modelo de lenguaje grande
(LLM), y escribe de vuelta un resultado.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) es el plano de control
local para construir y probar esas automatizaciones. En este playbook ejecuta un
OpenHands Agent Server, el proceso backend que ejecuta las conversaciones de agente,
y conecta el agente con servicios externos como GitHub y Slack.

Para mantener el flujo de trabajo en tu sistema AMD, el agente se comunica con un modelo local
servido por Lemonade Server. Lemonade expone ese modelo a través de una
API compatible con OpenAI, de modo que Agent Canvas puede configurarlo como un
endpoint remoto estilo OpenAI mientras el modelo, el prompt, y el contexto del flujo de trabajo permanecen locales.

En este playbook, construirás una automatización concreta: un digest de desarrollo
programado de GitHub a Slack. Utiliza GitHub para inspeccionar la actividad reciente del repositorio,
Slack para publicar el digest, llamadas a la API de Agent Canvas para configurar y
probar la automatización, y Lemonade para ejecutar el LLM localmente.

![Diagrama de arquitectura que muestra GitHub MCP, la automatización de OpenHands, Lemonade Server, y Slack MCP](assets/00-architecture-overview.png)

## Lo que aprenderás

- Cómo iniciar Lemonade Server y verificar que un modelo local responda a solicitudes de chat
- Cómo lanzar Agent Canvas y apuntar su Agent Server a un LLM local
- Cómo instalar servidores de Model Context Protocol (MCP) de GitHub y Slack a través de
  la API del Agent Server
- Cómo crear y ejecutar una automatización programada de OpenHands que publique un
  digest de desarrollo en Slack
- Cómo solucionar los fallos más comunes de modelo local y automatización

## Conceptos fundamentales

| Concepto | Qué es | Dónde encaja en este playbook |
| --- | --- | --- |
| Lemonade Server | Una plataforma de servicio de LLM local diseñada para hardware AMD que expone una API compatible con OpenAI. Tus datos nunca salen de tu máquina. | Ejecuta el modelo que impulsa al agente. |
| OpenHands Agent Server | El proceso backend que ejecuta las conversaciones de agente de OpenHands. | Aloja al agente, su perfil de LLM, y sus servidores MCP. |
| Agent Canvas | El plano de control local para OpenHands que ejecuta Agent Server y una interfaz de usuario para inspeccionar las ejecuciones del agente. | Lanza los backends y proporciona la API que invocas. |
| Servidor MCP | Un servidor de Model Context Protocol que le da a un agente herramientas para un servicio externo como GitHub o Slack. | Permite al agente leer de GitHub y escribir en Slack. |
| Automatización de OpenHands | Una conversación de agente programada o activada por eventos que obtiene contexto, razona sobre él, y escribe un resultado en algún lugar. | El digest de GitHub a Slack que construyes aquí. |

<!-- @device:stx,krk -->
> [!NOTE]
> Los flujos de trabajo de agentes de codificación se benefician de un modelo y una ventana de
> contexto más grandes. Usa al menos 32 GB de memoria del sistema, y preferiblemente 64 GB o
> más para modelos GGUF más grandes.
<!-- @device:end -->

## Requisitos previos

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Necesitas:

- Lemonade Server instalado siguiendo la
  [guía de instalación de Lemonade](https://lemonade-server.ai/docs/guide/install/) estándar.
- Node.js 22.12 o posterior y `npm`, utilizados para instalar la CLI publicada de Agent Canvas
  y ejecutar servidores MCP con `npx`.
- Un paquete `@openhands/agent-canvas` publicado y reciente con
  configuración de agente basada en esquemas, `LLMSummarizingCondenserSettings.max_tokens`,
  y soporte de `custom_tokenizer` para LLM.
- El paquete `transformers` de Python disponible en el entorno del Agent Server.
  Es necesario para el conteo de tokens de plantillas de chat cuando se configura
  `custom_tokenizer`.
- Un token de GitHub con acceso de lectura al repositorio que quieres resumir.
- Un token de bot de Slack (`xoxb-...`) con `chat:write` y acceso de lectura de canal.
- Un ID de equipo de Slack (`T...`).
- Un ID de canal de Slack (`C...`) donde debe publicarse el digest.

Invita a la aplicación de Slack al canal de destino antes de probar la automatización.

## Variables usadas en este playbook

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Los siguientes valores se ingresan en la interfaz de Agent Canvas en pasos posteriores. Configúralos
aquí para que puedas copiarlos después:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Usa un valor explícito `owner/repo` para `GITHUB_REPO_FILTER`. Los comodines amplios de
organización pueden devolver demasiado contexto de MCP para modelos locales.

## 1. Iniciar Lemonade Server

Inicia el modelo desde la CLI de Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade expone una API compatible con OpenAI en:

```text
http://127.0.0.1:13305/api/v1
```

Opcional: si Agent Canvas o el ejecutor de automatización no están en la misma máquina,
publica el endpoint de Lemonade a través de un túnel seguro y usa la URL HTTPS como
la URL base del LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificar el modelo local

Confirma que Lemonade puede servir el modelo seleccionado:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Luego envía una pequeña solicitud de chat:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Si esto devuelve un arreglo `choices`, Lemonade está listo para Agent Canvas.
## 3. Iniciar Agent Canvas

Instala el paquete Agent Canvas publicado e inicia el stack completo:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Si la instalación global de npm falla con un error de permisos, consulta la
entrada de solución de problemas de permisos de npm más abajo.

De forma predeterminada, Agent Canvas se inicia en `http://localhost:8000`. Abre esa URL en
tu navegador. El backend local predeterminado debería mostrarse como saludable en la pantalla
de inicio.

El comando `agent-canvas` inicia el servidor de agentes, el backend de automatización y
el frontend web en conjunto. Solo necesitas este comando para ejecutar OpenHands
de forma local. El resto de esta guía configura todo a través de la interfaz de
Agent Canvas en tu navegador.

## 4. Configurar el LLM local en la interfaz

En el primer inicio, Agent Canvas abre un flujo de incorporación. En ese flujo:

1. Mantén **OpenHands** seleccionado como el agente y haz clic en **Next**.
2. En **Set up your LLM**, selecciona **Advanced**.
3. Mantén **Authentication** configurado en **API key**.
4. Configura **Custom Model** con el valor de `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Configura **Base URL** en `http://127.0.0.1:13305/api/v1`.
6. Para **API Key**, ingresa cualquier marcador de posición no vacío, como `lemonade-local`.
   Lemonade no requiere una clave real, pero el cliente de OpenHands necesita un valor
   para enviar.

Los campos de conexión deberían verse así. El campo de la clave de API está enmascarado por
la interfaz.

![Configuración avanzada del LLM en el primer uso de Agent Canvas con el modelo Lemonade y la URL base local](assets/01-llm-advanced-settings.png)

Luego selecciona **All** y configura los campos adicionales del modelo local:

1. Desplázate hasta **Custom Tokenizer** y configúralo como `Qwen/Qwen3.6-35B-A3B`.
2. Desplázate hasta **LiteLLM Extra Body** y configúralo como
   `{"enable_thinking": true}`.
3. Haz clic en **Next**.

![Pestaña All del LLM en el primer uso de Agent Canvas con el tokenizador personalizado de Qwen](assets/02-llm-all-tokenizer-settings.png)

![Pestaña All del LLM en el primer uso de Agent Canvas con el cuerpo adicional de LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

La configuración del LLM debería mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

El prefijo `openai/` le indica a LiteLLM que use el formato de solicitud compatible
con OpenAI contra el endpoint de Lemonade. El tokenizador personalizado es el tokenizador
original de Hugging Face para el modelo GGUF; permite que OpenHands cuente los mismos
tokens de plantilla de chat que ve el servidor del modelo local. El formulario actual de LLM
de primer uso no muestra configuraciones de condensador. Si tu compilación de Agent Canvas
expone configuraciones de condensador más adelante en **Settings > LLM**, usa `llm_summarizing`
y establece el máximo de tokens por debajo de la ventana de contexto de Lemonade, como `56000`.

## 5. Instalar los servidores MCP de GitHub y Slack

En la interfaz de Agent Canvas, abre **Customize** (o **Settings > MCP**) para agregar
los servidores MCP que le dan al agente herramientas para GitHub y Slack. Los valores de
los tokens se envían solo a tu Agent Server local y se persisten como configuraciones cifradas.

### Servidor MCP de GitHub

Agrega un nuevo servidor MCP con estas configuraciones:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = tu token de GitHub |

Usa un token de GitHub con acceso de lectura al repositorio que deseas resumir.

### Servidor MCP de Slack

Agrega un segundo servidor MCP con estas configuraciones:

| Campo | Valor |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = el ID de tu canal de resumen |

Configura `SLACK_CHANNEL_IDS` con el ID del canal de resumen (el mismo valor que
`SLACK_DIGEST_CHANNEL`) para que el agente no necesite recorrer todos los canales
de Slack.

Después de agregar ambos servidores, usa el botón **Test** en cada uno para confirmar que
se conecta y anuncia herramientas. El servidor de GitHub debería listar herramientas de GitHub,
y el servidor de Slack debería listar herramientas de Slack.

![Página MCP de Agent Canvas con los servidores de GitHub y Slack instalados](assets/04-mcp-servers-installed.png)

## 6. Crear la automatización del resumen

En la interfaz de Agent Canvas, abre la página **Automations** y crea una nueva
automatización:

1. Elige **Create automation** y selecciona el tipo **Prompt preset**.
2. Configura el **Name** como `GitHub Development Digest to Slack`.
3. Configura el **Prompt** con el siguiente texto, reemplazando los marcadores
   de posición del repositorio y del canal con tus valores:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Configura el **Trigger** como **Cron** con el horario `0 9 * * 1-5` (9 a.m. en
   días de semana) y configura el **Timezone** con tu zona horaria, por ejemplo
   `America/New_York`.
5. Configura el **Timeout** en `900` segundos.
6. Guarda la automatización.

La página de detalle de la automatización muestra la nueva automatización con su
disparador cron y el punto de entrada de prompt preset generado.

![Detalle de la automatización de Agent Canvas después de la creación](assets/05-automation-created.png)
## 7. Prueba la automatización

Desde la página de detalles de la automatización en la Agent Canvas UI:

1. Haz clic en **Run now** (o **Dispatch**) para ejecutar la automatización una vez de inmediato.
2. Observa la lista de ejecuciones en la misma página. La última ejecución debería pasar a
   `COMPLETED`.
3. Abre tu canal de Slack de destino. Debería contener el resumen generado.

No necesitas esperar a que se active el cron schedule: **Run now** activa una
ejecución bajo demanda para que puedas confirmar que el prompt, las conexiones MCP y la publicación en Slack
funcionan correctamente antes de depender del cronograma.

![Ejecución de automatización de Agent Canvas completada exitosamente](assets/06-automation-run-completed.png)

![Canal de Slack mostrando el resumen de OpenHands generado](assets/07-slackbot-message.png)

## Solución de problemas

- **Lemonade está caído:** reinícialo con el comando
  `lemonade run "${LEMONADE_MODEL}"` del paso 1, luego vuelve a ejecutar la verificación
  de salud.
- **`npm install -g` falla con un error de permisos:** en Linux o WSL,
  configura un directorio global de npm propiedad del usuario, agrégalo al archivo de inicio de tu shell, luego instala Agent Canvas de nuevo:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Si usas `zsh`, agrega la misma línea `export PATH=...` a `~/.zshrc` en lugar
  de `~/.bashrc`.
- **Agent Canvas rechaza la configuración del LLM después de configurar `custom_tokenizer`:**
  instala `transformers` en el entorno Python del Agent Server, reinicia Agent
  Canvas si es necesario, y vuelve a intentar guardar la configuración del LLM. OpenHands requiere
  Transformers para cargar la plantilla de chat del tokenizer cuando `custom_tokenizer` está
  configurado.
- **Agent Canvas no puede conectarse con Lemonade:** verifica
  `curl -fsS "${LEMONADE_BASE_URL}/health"` y confirma que la URL base ingresada en
  el formulario de LLM de primer uso o en **Settings > LLM** coincida con el endpoint local en ejecución o con el túnel HTTPS.
- **La configuración del LLM no se guardó:** asegúrate de haber hecho clic en **Next** después de
  ingresar los valores. Vuelve a abrir **Settings > LLM** para confirmar que los valores
  se guardaron correctamente.
- **GitHub MCP no puede ver repositorios privados:** confirma que el token de GitHub tenga
  acceso de lectura al repositorio de destino y que el botón **Test** de MCP en
  **Customize** muestre las herramientas de GitHub.
- **Slack puede leer canales pero no puede publicar:** invita la app de Slack al
  canal de destino y confirma que el bot tenga `chat:write`.
- **La automatización lista demasiados canales de Slack:** usa un ID de canal de Slack y
  configura `SLACK_CHANNEL_IDS` en el servidor MCP de Slack en **Customize**.
- **La ejecución de la automatización falla o excede el contexto:** confirma que Lemonade se haya iniciado
  con `ctx_size=65536`, confirma que el LLM de OpenHands tenga configurado `custom_tokenizer`,
  y usa un repositorio explícito con conjuntos de resultados de GitHub limitados a 3 a 5
  elementos. Si tu versión de Agent Canvas expone configuraciones de condenser, configura el máximo de tokens del condenser por debajo de la ventana de contexto de Lemonade.

## Próximos pasos

- Agrega un resumen semanal exclusivo de releases.
- Agrega una automatización activada por eventos de GitHub para alertas más rápidas de PR o push.
- Enruta el mismo resumen hacia Notion, Linear u otra herramienta basada en MCP.

## Recursos

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentación de Lemonade Server](https://lemonade-server.ai/docs)
- [Repositorio de extensiones de OpenHands](https://github.com/OpenHands/extensions)
- [Servidores del Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paquete Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)