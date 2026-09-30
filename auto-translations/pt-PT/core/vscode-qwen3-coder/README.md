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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este manual requer no mínimo **32 GB** de memória do sistema.
<!-- @device:end -->

## Visão geral

Os agentes de codificação são ferramentas poderosas que capacitam os programadores através da colaboração com agentes de IA suportados por Large Language Models (LLMs). Podem ser incorporados no ambiente de desenvolvimento, como o terminal ou o VS Code, permitindo uma integração perfeita no fluxo de trabalho de um programador.

Este tutorial demonstra como utilizar o Cline, o VS Code e o LM Studio para executar um agente de codificação inteiramente na sua máquina local.

## O que vai aprender

* Como executar o VS Code com o agente de codificação Cline para auxiliar em tarefas de engenharia de software.
* Como configurar o Cline para comunicar com o LM Studio para inferência local de agentes de codificação.
* Como utilizar agentes de codificação locais para resolver tarefas reais de engenharia de software. 

<!-- @device:halo_box,halo,stx,krk -->
## Definir a configuração de memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar atualizações de software
> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo através do Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os pré-requisitos de software

<!-- @require:lmstudio,vscode -->

## Iniciar e configurar o LM Studio

Vamos utilizar o LM Studio para disponibilizar o LLM que alimenta o agente de codificação.

- Na barra de pesquisa, procure por `LM Studio` e inicie a aplicação. Será recebido pela seguinte página.

![Ecrã Inicial do LM Studio](assets/initial-lm-studio.png)

Em seguida, temos de carregar o LLM no sistema. Vamos utilizar o modelo `Qwen3-Coder-30B-A3B` com um comprimento de contexto elevado. (Utilize o separador Model para o instalar, caso ainda não o tenha feito).
- Clique na barra de pesquisa na parte superior da janela do LM Studio ou prima `CTRL+L`. Clique no interruptor `Manually choose model load parameters` e depois clique no modelo Qwen3-Coder-30B-A3B.
- Altere o comprimento de contexto de `4096` para `32768` e certifique-se de que `GPU Offload` está no máximo. Depois, clique em `Load Model`

![A selecionar o modelo](assets/model-list-zoomed.png)

Utilizamos um comprimento de contexto elevado para que o agente possa processar bases de código extensas e recordar as alterações que foram efetuadas.

![A configurar o modelo](assets/selecting-model-zoomed.png)

Em seguida, temos de ativar o Servidor do LM Studio. 
- Clique no separador Developer ou prima `CTRL+2` no LM Studio, à esquerda.
- Verifique o interruptor de estado e certifique-se de que está definido como `Running`.

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

![Estado do Servidor](assets/lm-studio-server-status.png)

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Iniciar e configurar o VS Code

Vamos instalar a extensão Cline no VS Code e ligá-la ao servidor do LM Studio que acabámos de criar.
- Na barra de pesquisa, procure por `VS Code` e inicie a aplicação.
- Clique no ícone `Extensions` na coluna esquerda do VS Code e procure por `Cline`. Depois, clique no botão `Install`. 

![A instalar a extensão Cline](assets/installing-cline-vscode-extension.png)

- Deverá aparecer um ícone do Cline à esquerda. Clique nele para abrir o Cline. Aparecerá uma janela a perguntar `How will you use Cline?` Como vamos utilizar um LLM local em execução através do LM Studio, selecione `Bring my own API Key` e prima `Continue`. 

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Criação de conta](assets/cline-how-will-you-use-cline-zoomed.png)

Em seguida, temos de configurar o Cline para comunicar com o servidor do LM Studio que configurámos. 
- Defina o API Provider como `LM Studio` e o modelo como `Qwen3-Coder-30B-A3B-GGUF`. 

>**Dica**: Poderão estar disponíveis modelos mais recentes. Considere transferir e mudar para os modelos Qwen3.6, se desejar.


![Configuração do modelo](assets/cline-model-configuration-zoomed.png)

## Criar o seu primeiro projeto

Vamos utilizar o nosso agente local para criar um website! Abra o VS Code numa pasta à sua escolha, onde o Cline irá criar os ficheiros.
- Para tal, vá a `File -> Open Folder` no canto superior esquerdo do VS Code e escolha uma pasta como `Documents`.

![Pasta vazia do VS Code](assets/open-cline-test.png)

Agora estamos prontos para dar instruções ao agente de codificação local. 
- Clique na extensão Cline na coluna esquerda e introduza uma instrução para iniciar o agente. Como exemplo, vamos utilizar a seguinte instrução:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

O agente irá então começar a criar ficheiros de acordo com a instrução. Como utilizador, pode observar o código a ser gerado no VS Code, conforme mostrado abaixo. Poderá ter de clicar em `Save` sempre que o Cline quiser criar um ficheiro. 

![Geração de código do Cline](assets/cline-code-generation.png)

Após gerar o software, o agente termina e pode executar a aplicação. Neste caso, o agente escreveu em três ficheiros: `index.html`, `script.js` e `styles.css`. Ao fazer duplo clique no ficheiro HTML, podemos carregar e interagir com o website gerado.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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

## Próximos passos

Depois de gerar o website, pode continuar a trabalhar com o Cline para o melhorar. Duas melhorias possíveis são:

- **Documentação**: Basta pedir ao agente `Add a README` para que este gere um ficheiro `README.md` que documenta o website.
- **Animação**: Peça ao modelo `Add an animation that visually represents a large language model running on a laptop.` para gerar uma animação para o website.

Encorajamos o leitor a tentar gerar outras aplicações utilizando esta configuração. Abaixo estão alguns exemplos divertidos que experimentámos:

- **Jogos de arcada retro**: Experimente outras instruções. Também pode ser divertido para o agente criar jogos de estilo retro em Python, utilizando o pacote `PyGame`, com a seguinte instrução:

```code
Create a simple pong game using the PyGame python package.
```

- **Análise de dados**: Uma área onde os agentes de codificação são particularmente úteis é a de scripting e análise de dados. Esta é uma instrução para demonstrar a capacidade do modelo local de gerar software de análise de dados para visualização de preços de ações:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre Coding Agents, Cline e a execução de workloads em 

* Mais informações sobre a parceria e integração entre a AMD e o LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog da AMD que explica como executar o Cline em placas gráficas AMD Ryzen™ AI e Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog da Cline sobre a execução de agentes de codificação localmente em AI PCs: https://cline.bot/blog/local-models-amd