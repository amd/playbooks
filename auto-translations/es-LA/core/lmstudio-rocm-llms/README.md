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

LM Studio es un potente wrapper basado en GUI para [llama.cpp](https://github.com/ggml-org/llama.cpp) y también ofrece un [endpoint compatible con OpenAI](https://lmstudio.ai/docs/developer/openai-compat) para el servicio local de modelos. LM Studio ofrece una interfaz simple pero potente para descargar e implementar modelos fácilmente. LM Studio ofrece backends (llamados runtimes) tanto de Vulkan como de AMD ROCm™ software para usuarios de AMD.


## Lo que aprenderás
- Cómo configurar y usar LM Studio para aprovechar tu hardware local
- Probar y administrar LLMs en un entorno completamente sin conexión
- Servir modelos a través de una API compatible con OpenAI para potenciar flujos de trabajo y aplicaciones personalizadas


## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @os:linux -->
> **Nota**: Puedes instalar VS Code a través de AMD Ryzen™ AI Developer Center. Para LM Studio, sigue las instrucciones de instalación a continuación.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Si VS Code o LM Studio no están instalados, puedes instalarlos desde AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Descarga de modelos

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Chateando con un LLM
Aprende a comenzar a chatear con un LLM de nivel ChatGPT completamente en local.  

1. Abre LMStudio. 
2. Presiona `Ctrl + L` para abrir el Model Loader, selecciona `Manually choose model load parameters`, y haz clic en `${model_name}`
3. Asegúrate de que "show advanced settings" esté marcado.  
4. Cambia `Context Length` según lo desees. Una longitud de contexto mayor significa más memoria del modelo, pero también más memoria del sistema utilizada. Se recomienda 4096 para este playbook.
5. Asegúrate de que `GPU Offload` esté configurado al máximo y que `Flash Attention` esté activado (Cache Quantizations puede permanecer desactivado)
6. Marca `Remember settings` y haz clic en `Load Model`.
7. Si no estás en la ventana de chat, presiona `Ctrl + 1` o haz clic en el botón 👾 en la parte superior izquierda de la pantalla.
8. ¡Envía un mensaje y comienza a interactuar con el modelo!

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Consejo**: La longitud de contexto se refiere a la memoria del modelo. Flash attention mejora la velocidad de procesamiento mientras reduce el uso de memoria. GPU Offload transfiere el cómputo a la tarjeta gráfica para obtener respuestas más rápidas.

## Servir LLMs a través de un endpoint compatible con OpenAI

LM Studio también ofrece un endpoint compatible con OpenAI en forma de LM Studio Server. Esto ya se ha demostrado en un flujo de trabajo de codificación agéntica con Cline [aquí](../playbooks/vscode-qwen3-coder). Otro caso de uso común es conectar LM Studio Server a cualquier aplicación web (React, Node.js, Python) enviando solicitudes HTTP estándar al endpoint de inferencia.

Para configurar LM Studio Server, usa las siguientes instrucciones:

1. En el lado izquierdo, haz clic en la pestaña `Developer` (ícono de línea de comandos) o presiona `Ctrl + 2` y luego haz clic en `Server Settings`.  
2. (Opcional): Si deseas servir el modelo a través de tu LAN, marca `Serve on Local Network`. Si deseas usarlo con un sitio web o llamadas extensivas dentro de VS Code, marca `Enable CORS`. 
3. En la esquina superior izquierda, asegúrate de que el servidor esté ejecutándose haciendo clic en el botón de alternancia frente a `Status`.
4. Ahora se ejecutará un endpoint compatible con OpenAI. La dirección normalmente está en http://127.0.0.1:1234  
5. Si un modelo aún no está cargado, puedes cargarlo haciendo clic en `Load Model` y siguiendo los pasos mencionados anteriormente. 

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


Este modelo ahora será accesible a través del endpoint de LM Studio Server y admitirá endpoints de OpenAI, incluyendo:

| Endpoint | Método | Documentación |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Ejemplo: Haciendo ping a tu Endpoint
Habiendo creado el endpoint compatible con OpenAI, veamos cómo integrar esto en un entorno de desarrollo Python (como VSCode) y usar tu sistema como un proveedor de API local. 

1. Crea un entorno virtual de Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    En Linux, abre una terminal en el directorio que prefieras y sigue los comandos para crear un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

    En Linux, abre una terminal en el directorio que prefieras y sigue los comandos para crear un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    En Windows, abre una terminal en el directorio que prefieras y sigue los comandos para crear un venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Consejo**: Es posible que los usuarios de Windows necesiten modificar su política de ejecución de PowerShell (por ejemplo,
    > configurarla como RemoteSigned o Unrestricted) antes de ejecutar algunos comandos de PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    En Windows, abre una terminal en el directorio que prefieras y sigue los comandos para crear un venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Consejo**: Es posible que los usuarios de Windows necesiten modificar su política de ejecución de PowerShell (por ejemplo,
    > configurarla como RemoteSigned o Unrestricted) antes de ejecutar algunos comandos de PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Instala el paquete de OpenAI
    ```bash
    pip install openai
    ```

3. Ejecuta el siguiente script para hacer ping al endpoint que acabamos de crear.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### (Opcional): Alternando entre Runtimes

1. Presiona `Ctrl + Shift + R` en tu teclado. Alternativamente, haz clic en la pestaña `Discover` (Lupa) en el lado izquierdo y luego haz clic en `Runtime` en la ventana emergente.   
2. Deberías ver entonces `Runtime Selections`, donde el menú desplegable se puede usar para cambiar el runtime.


## Próximos Pasos

- **Integración de Apps Personalizadas**: Integra tus propios scripts o aplicaciones de Python usando la API local compatible con OpenAI.
- **Frontends Avanzados**: Conecta interfaces potentes como Open WebUI a tu servidor para el historial de chat y la gestión de personas.

Para más documentación, por favor visita: https://lmstudio.ai/docs/developer