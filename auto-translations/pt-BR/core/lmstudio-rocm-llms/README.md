<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

LM Studio é um poderoso wrapper baseado em GUI para o [llama.cpp](https://github.com/ggml-org/llama.cpp) e também fornece um [endpoint compatível com OpenAI](https://lmstudio.ai/docs/developer/openai-compat) para veiculação de modelos locais. O LM Studio oferece uma interface simples, porém poderosa, para baixar e implantar modelos com facilidade. O LM Studio oferece backends (chamados de runtimes) tanto Vulkan quanto AMD ROCm™ software para usuários AMD.


## O Que Você Vai Aprender
- Como configurar e usar o LM Studio para aproveitar seu hardware local
- Testar e gerenciar LLMs em um ambiente completamente offline
- Servir modelos via API compatível com OpenAI para potencializar workflows e aplicativos personalizados


## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @os:linux -->
> **Observação**: Você pode instalar o VS Code através do AMD Ryzen™ AI Developer Center. Para o LM Studio, siga as instruções de instalação abaixo.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: Se o VS Code ou o LM Studio não estiverem instalados, você pode instalá-los a partir do AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Baixando Modelos

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

## Conversando com um LLM
Aprenda a começar a conversar com um LLM no nível do ChatGPT totalmente em modo local.  

1. Abra o LMStudio. 
2. Pressione `Ctrl + L` para abrir o Model Loader, selecione `Manually choose model load parameters` e clique em `${model_name}`
3. Certifique-se de que "show advanced settings" esteja marcado.  
4. Altere `Context Length` conforme desejado. Um comprimento de contexto maior significa mais memória do modelo, mas mais memória do sistema utilizada. O recomendado para este guia é 4096.
5. Certifique-se de que `GPU Offload` esteja definido no máximo e que `Flash Attention` esteja ativado (Cache Quantizations pode permanecer desativado)
6. Marque `Remember settings` e clique em `Load Model`.
7. Se não estiver na janela de chat, pressione `Ctrl + 1` ou clique no botão 👾 no canto superior esquerdo da tela.
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

> **Dica**: O comprimento de contexto se refere à memória do modelo. O flash attention melhora a velocidade de processamento e reduz o uso de memória. O GPU Offload transfere a computação para a placa de vídeo para respostas mais rápidas.

## Servindo LLMs através de um endpoint compatível com OpenAI

O LM Studio também oferece um endpoint compatível com OpenAI na forma do LM Studio Server. Isso já foi demonstrado em um workflow de codificação agêntica com Cline [aqui](../playbooks/vscode-qwen3-coder). Outro caso de uso comum é conectar o LM Studio Server a qualquer aplicativo web (React, Node.js, Python) enviando requisições HTTP padrão para o endpoint de inferência.

Para configurar o LM Studio Server, use as instruções a seguir:

1. No lado esquerdo, clique na aba `Developer` (ícone de linha de comando) ou pressione `Ctrl + 2` e, em seguida, clique em `Server Settings`.  
2. (Opcional): Se você quiser servir o modelo pela sua LAN, marque `Serve on Local Network`. Se quiser usar com um site ou realizar chamadas extensivas dentro do VS Code, marque `Enable CORS`. 
3. No canto superior esquerdo, certifique-se de que o servidor esteja em execução clicando no botão de alternância à frente de `Status`.
4. Um endpoint compatível com OpenAI estará agora em execução. O endereço geralmente é http://127.0.0.1:1234  
5. Se um modelo ainda não estiver carregado, você pode carregá-lo clicando em `Load Model` e seguindo as etapas mencionadas anteriormente. 

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


Esse modelo agora estará acessível através do endpoint do LM Studio Server e oferecerá suporte a endpoints OpenAI, incluindo:

| Endpoint | Método | Documentação |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Exemplo: Testando seu Endpoint
Tendo acabado de criar o endpoint compatível com OpenAI, vamos ver como integrar isso a um ambiente de desenvolvimento Python (como o VSCode) e usar seu sistema como um Provedor de API local.

1. Crie um ambiente virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    No Linux, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu usuário acesso aos dispositivos GPU** (faça logout e login novamente para que isso tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

    No Linux, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
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
    No Windows, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Dica**: Usuários do Windows podem precisar modificar sua Política de Execução do PowerShell (por exemplo,
    > definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    No Windows, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Dica**: Usuários do Windows podem precisar modificar sua Política de Execução do PowerShell (por exemplo,
    > definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Instale o pacote OpenAI
    ```bash
    pip install openai
    ```

3. Execute o script a seguir para testar o endpoint que acabamos de criar.
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

1. Pressione `Ctrl + Shift + R` no seu teclado. Alternativamente, clique na aba `Discover` (Lupa) no lado esquerdo e depois clique em `Runtime` na janela pop-up.
2. Você deverá então ver `Runtime Selections`, onde o menu suspenso pode ser usado para alterar o runtime.


## Próximos Passos

- **Integração de Aplicativo Personalizado**: Integre seus próprios scripts ou aplicativos Python usando a API local compatível com OpenAI.
- **Interfaces Avançadas**: Conecte interfaces poderosas como o Open WebUI ao seu servidor para histórico de conversas e gerenciamento de personas.

Para mais documentação, visite: https://lmstudio.ai/docs/developer