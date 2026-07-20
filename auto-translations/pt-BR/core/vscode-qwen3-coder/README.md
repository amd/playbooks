<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para visualizar corretamente este conteúdo.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requer no mínimo **32GB** de memória do sistema.
<!-- @device:end -->

## Visão Geral

Agentes de codificação são ferramentas poderosas que capacitam desenvolvedores por meio da colaboração com agentes de IA baseados em Large Language Models (LLMs). Eles podem ser incorporados ao ambiente de desenvolvimento, como o terminal ou o VS Code, permitindo uma integração perfeita ao fluxo de trabalho de um desenvolvedor.

Este tutorial demonstra como usar Cline, VS Code e LM Studio para executar um agente de codificação inteiramente na sua máquina local.

## O Que Você Vai Aprender

* Como executar o VS Code com o agente de codificação Cline para auxiliar em tarefas de engenharia de software.
* Como configurar o Cline para se comunicar com o LM Studio para inferência local de agentes de codificação.
* Como usar agentes de codificação locais para resolver tarefas reais de engenharia de software. 

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, você pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

<!-- @require:lmstudio,vscode -->

## Iniciar e Configurar o LM Studio

Usaremos o LM Studio para servir o LLM que alimenta o agente de codificação.

- Na barra de pesquisa, procure por `LM Studio` e inicie a aplicação. Você será recebido pela seguinte página.

![LM Studio Initial Screen](assets/initial-lm-studio.png)

Em seguida, precisamos carregar o LLM no sistema. Vamos usar o modelo `Qwen3-Coder-30B-A3B` com um comprimento de contexto grande. (Use a aba Model para instalá-lo caso ainda não tenha feito isso).
- Clique na barra de pesquisa na parte superior da janela do LM Studio ou pressione `CTRL+L`. Clique na opção `Manually choose model load parameters` e depois clique no modelo Qwen3-Coder-30B-A3B.
- Altere o comprimento de contexto de `4096` para `32768`, e certifique-se de que `GPU Offload` esteja no máximo. Em seguida, clique em `Load Model`

![Selecting Model](assets/model-list-zoomed.png)

Usamos um comprimento de contexto grande para que o agente consiga processar bases de código grandes e lembrar das alterações que foram feitas.

![Configuring Model](assets/selecting-model-zoomed.png)

Em seguida, precisamos habilitar o Servidor do LM Studio. 
- Clique na aba Developer ou pressione `CTRL+2` no LM Studio à esquerda.
- Marque o alternador de status e certifique-se de que esteja definido como `Running`.

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

![Server Status](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Iniciar e Configurar o VS Code

Vamos instalar a extensão Cline no VS Code e conectá-la ao servidor LM Studio que acabamos de configurar.
- Na barra de pesquisa, procure por `VS Code` e inicie a aplicação.
- Clique no ícone `Extensions` na coluna esquerda do VS Code e procure por `Cline`. Em seguida, clique no botão `Install`. 

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- Um ícone do Cline deverá aparecer à esquerda. Clique nele para abrir o Cline. Aparecerá uma janela perguntando `How will you use Cline?` Como vamos usar um LLM local em execução via LM Studio, selecione `Bring my own API Key` e clique em `Continue`. 

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

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

Em seguida, precisamos configurar o Cline para se comunicar com o servidor LM Studio que configuramos. 
- Defina o API Provider como `LM Studio` e o modelo como `Qwen3-Coder-30B-A3B-GGUF`. 

>**Dica**: Modelos mais novos podem estar disponíveis. Considere baixar e mudar para os modelos Qwen3.6, se desejar.


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## Criando seu primeiro projeto

Vamos usar nosso agente local para criar um site! Abra o VSCode em um diretório de sua escolha onde o Cline criará os arquivos.
- Para fazer isso, vá em `File -> Open Folder` no canto superior esquerdo do VS Code e escolha uma pasta como `Documents`.

![VS Code Empty Folder](assets/open-cline-test.png)

Agora estamos prontos para instruir o agente de codificação local. 
- Clique na extensão Cline na coluna esquerda e digite um prompt para iniciar o agente. Como exemplo, vamos usar o seguinte prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

O agente então começará a criar arquivos de acordo com o prompt. Como usuário, você pode observar o código sendo gerado no VS Code, conforme mostrado abaixo. Talvez seja necessário clicar em `Save` toda vez que o Cline quiser criar um arquivo. 

![Cline Code Generation](assets/cline-code-generation.png)

Após gerar o software, o agente conclui a tarefa e você pode executar a aplicação. Neste caso, o agente escreveu em três arquivos: `index.html`, `script.js` e `styles.css`. Basta clicar duas vezes no arquivo HTML para carregar e interagir com o site gerado.

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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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

Depois de gerar o site, você pode continuar trabalhando com o Cline para aprimorar o site. Duas melhorias possíveis são:

- **Documentação**: Basta orientar o agente com `Add a README` para que o agente gere um arquivo `README.md` que documenta o site.
- **Animação**: Oriente o modelo com `Add an animation that visually represents a large language model running on a laptop.` para gerar uma animação para o site.

Incentivamos o leitor a tentar gerar outros aplicativos usando essa configuração. Abaixo estão alguns exemplos divertidos que já testamos:

- **Jogos retrô de fliperama**: Experimente outros prompts. Também pode ser divertido fazer o agente criar jogos em estilo retrô em Python usando o pacote `PyGame` com o seguinte prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Análise de dados**: Uma área em que agentes de codificação são particularmente úteis é a de scripting e análise de dados. Este é um prompt para demonstrar a capacidade do modelo local de gerar software de análise de dados para visualização de preços de ações:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre Agentes de Codificação, Cline e execução de cargas de trabalho em 

* Mais informações sobre a parceria e integração da AMD com o LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog da AMD apresentando como executar o Cline em placas gráficas AMD Ryzen™ AI e Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog do Cline sobre como executar agentes de codificação localmente em PCs de IA: https://cline.bot/blog/local-models-amd