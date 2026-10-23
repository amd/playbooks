<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão geral

LM Studio é um wrapper poderoso baseado em GUI para [llama.cpp](https://github.com/ggml-org/llama.cpp) e também disponibiliza um [endpoint compatível com OpenAI](https://lmstudio.ai/docs/developer/openai-compat) para disponibilizar modelos localmente. O LM Studio oferece uma interface simples mas poderosa para transferir e implementar modelos com facilidade. O LM Studio oferece backends Vulkan e AMD ROCm™ software (designados runtimes) para utilizadores AMD.

<!-- @device:halo_box -->
> **Nota:** Alguns sistemas AMD Ryzen AI Halo já vêm com o modelo deste playbook pré-instalado, enquanto outros não. Ambos os casos são suportados. Quando chegar à secção **Downloading Models**, verifique se o modelo já está disponível no LM Studio — se estiver, pode saltar a transferência; se não estiver, siga os passos indicados aí para o transferir.
<!-- @device:end -->


## O que vai aprender
- Como configurar e utilizar o LM Studio para tirar partido do seu hardware local
- Testar e gerir LLMs num ambiente completamente offline
- Disponibilizar modelos através de uma API compatível com OpenAI para potenciar fluxos de trabalho e aplicações personalizadas


<!-- @device:halo_box,halo,stx,krk -->
## Definir a configuração de memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar atualizações de software

<!-- @os:linux -->
> **Nota**: Pode instalar o VS Code através do AMD Ryzen™ AI Developer Center. Para o LM Studio, siga as instruções de instalação abaixo.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Se o VS Code ou o LM Studio não estiverem instalados, pode instalá-los a partir do AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os pré-requisitos de software

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->
<!-- @prereq:lmstudio -->

## Transferir modelos

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @prereq:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @prereq:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Conversar com um LLM
Saiba como começar a conversar com um LLM de nível ChatGPT, de forma totalmente local.  

1. Abra o LMStudio. 
2. Prima `Ctrl + L` para abrir o Model Loader, selecione `Manually choose model load parameters` e clique em `${model_name}`
3. Certifique-se de que "show advanced settings" está marcado.  
4. Altere `Context Length` conforme pretendido. Um comprimento de contexto mais elevado significa mais memória do modelo, mas também mais memória do sistema utilizada. O recomendado para este playbook é 4096.
5. Certifique-se de que `GPU Offload` está definido para o máximo e que `Flash Attention` está ativado (as Cache Quantizations podem permanecer desativadas)
6. Marque `Remember settings` e clique em `Load Model`.
7. Se não estiver na janela de chat, prima `Ctrl + 1` ou clique no botão 👾 no canto superior esquerdo do ecrã.
8. Envie uma mensagem e comece a interagir com o modelo!

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
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y }
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
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y; }
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

> **Dica**: O comprimento de contexto refere-se à memória do modelo. O Flash Attention melhora a velocidade de processamento ao mesmo tempo que reduz o consumo de memória. O GPU Offload transfere o processamento para a placa gráfica para obter respostas mais rápidas.

## Disponibilizar LLMs através de um endpoint compatível com OpenAI

O LM Studio também disponibiliza um endpoint compatível com OpenAI sob a forma do LM Studio Server. Isto já foi demonstrado num fluxo de trabalho de codificação agêntica com Cline [aqui](../playbooks/vscode-qwen3-coder). Outro caso de uso comum é ligar o LM Studio Server a qualquer aplicação web (React, Node.js, Python) através do envio de pedidos HTTP padrão para o endpoint de inferência.

Para configurar o LM Studio Server, siga estas instruções:

1. No lado esquerdo, clique no separador `Developer` (ícone de linha de comandos) ou prima `Ctrl + 2` e depois clique em `Server Settings`.  
2. (Opcional): Se pretender disponibilizar o modelo através da sua LAN, marque `Serve on Local Network`. Se pretender utilizá-lo com um website ou com chamadas extensivas dentro do VS Code, marque `Enable CORS`. 
3. No canto superior esquerdo, certifique-se de que o servidor está em execução clicando no botão de alternância em frente a `Status`.
4. Um endpoint compatível com OpenAI estará agora em execução. O endereço é tipicamente http://127.0.0.1:1234  
5. Se um modelo ainda não estiver carregado, pode carregá-lo clicando em `Load Model` e seguindo os passos mencionados anteriormente. 

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


Este modelo estará agora acessível através do endpoint do LM Studio Server e irá suportar endpoints OpenAI, incluindo:

| Endpoint | Método | Documentação |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Exemplo: Fazer Ping ao seu Endpoint
Tendo acabado de criar o endpoint Compatível com OpenAI, vejamos como integrar isto num ambiente de desenvolvimento Python (como o VSCode) e utilizar o seu sistema como um Fornecedor de API local.

1. Crie um ambiente virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    No Linux, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine a sessão e inicie-a novamente para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

    No Linux, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
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
    No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Dica**: Os utilizadores de Windows poderão necessitar de modificar a sua Política de Execução do PowerShell (por exemplo,
    > definindo-a para RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Dica**: Os utilizadores de Windows poderão necessitar de modificar a sua Política de Execução do PowerShell (por exemplo,
    > definindo-a para RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Instale o pacote OpenAI
    ```bash
    pip install openai
    ```

3. Execute o seguinte script para fazer ping ao endpoint que acabámos de criar.
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

#### (Opcional): Alternar entre Runtimes

1. Prima `Ctrl + Shift + R` no seu teclado. Em alternativa, clique no separador `Discover` (Lupa) no lado esquerdo e depois clique em `Runtime` na janela pop-up.
2. Deverá então ver `Runtime Selections`, onde o menu suspenso pode ser utilizado para alterar o runtime.


## Próximos Passos

- **Integração de Aplicações Personalizadas**: Integre os seus próprios scripts ou aplicações Python utilizando a API local compatível com OpenAI.
- **Frontends Avançados**: Ligue interfaces poderosas como o Open WebUI ao seu servidor para histórico de conversas e gestão de personas.

Para mais documentação, visite: https://lmstudio.ai/docs/developer