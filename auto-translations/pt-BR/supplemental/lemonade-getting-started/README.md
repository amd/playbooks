<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para visualizar este conteúdo corretamente.
<!-- @github-only:end -->

## Visão Geral

🍋 **Lemonade** é um servidor de IA local de código aberto que permite executar grandes modelos de linguagem (LLMs), geradores de imagens e modelos de áudio diretamente no seu próprio hardware. Ele expõe os modelos por meio da **OpenAI API** padrão do setor, portanto qualquer aplicativo que funcione com OpenAI pode funcionar instantaneamente com Lemonade. Ao final do playbook, você estará usando Lemonade para executar modelos localmente na sua máquina.

## O Que Você Vai Aprender

Ao final deste playbook você será capaz de:

* **Instalar o Lemonade Server** e verificar se ele está em execução.
* **Baixar e conversar com um LLM** usando um único comando.
* **Explorar a interface web** e experimentar diferentes modalidades, como visão, fala para texto e geração de imagens.
* **Alternar backends de GPU** entre Vulkan e AMD ROCm™ software.
* **Criar um aplicativo Python** alimentado por um LLM local usando a API compatível com OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Executar modelos na AMD Neural Processing Unit (NPU)** usando os modos de execução Hybrid e FLM em hardware AMD Ryzen™ AI.
<!-- @device:end -->

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando Pré-requisitos de Software

Antes de começar, certifique-se de ter:

- Um PC com **Windows 11** ou uma distribuição **Linux** compatível (Ubuntu 24.04+, Fedora, Debian)
- **16 GB de RAM** são recomendados para o modelo de tempo de execução usado nas Etapas 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** são recomendados se você quiser usar o modelo maior de geração de código na Etapa 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB de espaço livre em disco**, dependendo dos modelos que você baixar. O maior modelo neste guia tem cerca de 20 GB.
- **Python 3.10–3.13** (usado na seção de aplicativo Python)
- Uma conexão com a internet (com fio ou sem fio)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcional] Um NPU AMD XDNA 2 (Ryzen AI 300/400/Max 300 series ou Z2 Extreme) com o driver mais recente instalado a partir das [Instruções de Instalação do Ryzen AI Software](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) se você quiser executar um modelo no NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Conceitos Fundamentais — Como Funcionam os Servidores de IA Local

Antes de executarmos um modelo, vale a pena entender *por que* as coisas são configuradas dessa forma. Lemonade é um **servidor de modelos local**, um processo que carrega modelos de IA na memória e os expõe a aplicativos via HTTP, assim como um serviço de IA em nuvem faria.

### Por Que um Servidor?

| Benefício | O Que Significa para Você |
|---------|----------------------|
| **Integração simplificada** | Os aplicativos se comunicam com uma única API HTTP em vez de lidar com bibliotecas C++ ou Python específicas de hardware. |
| **Modelos compartilhados** | Um único modelo carregado pode atender a vários aplicativos ao mesmo tempo, sem cópias duplicadas consumindo sua RAM. |
| **Portabilidade da nuvem para o local** | Código escrito para a API em nuvem da OpenAI funciona com Lemonade apenas alterando uma URL. |
| **Separação de responsabilidades** | Gerenciamento de modelos, streaming e tolerância a falhas são tratados pelo servidor, para que os desenvolvedores possam se concentrar em seu aplicativo. |

### O Padrão OpenAI API

Lemonade implementa a **OpenAI API**, a mesma interface usada pelo ChatGPT, Azure OpenAI e dezenas de outros serviços. O modelo de conversa é simples:

| Papel | Quem Está Falando |
|------|---------------|
| **system** | Instruções para o modelo (persona, restrições, ferramentas disponíveis) |
| **user** | Mensagens do humano (ou aplicativo) para o modelo |
| **assistant** | Respostas geradas pelo modelo |

Isso significa que qualquer biblioteca ou aplicativo que suporte OpenAI pode se comunicar com Lemonade apontando para `http://localhost:13305/api/v1` enquanto o Lemonade Server estiver em execução.

## Atividade Principal — Seu Primeiro Chat de IA Local

Vamos baixar um LLM e ter uma conversa com ele, executando a IA inteiramente na sua própria máquina.

### Etapa 1: Baixar e Executar um Modelo

Lemonade vem com uma biblioteca de modelos curada. Vamos começar com **Gemma-4-E2B-it**, um modelo capaz e compacto que inclui suporte a visão. Abra um terminal e execute:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Este único comando faz três coisas:

1. **Baixa** o modelo (~3 GB) do Hugging Face, se ainda não tiver sido baixado. (Pode levar algum tempo)
2. **Inicia** o processo do Lemonade Server na porta 13305.
3. **Abre o Lemonade App** para que você possa começar a conversar com o modelo.


<!-- @os:windows -->
No Windows, o Lemonade App é iniciado automaticamente e você pode começar a conversar imediatamente. Se você instalou o pacote `minimal.msi`, o aplicativo não está incluído. Para começar a conversar, abra seu navegador e acesse `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
No Linux, abra seu navegador e acesse `http://localhost:13305` para acessar o aplicativo web.
<!-- @os:end -->

Tente digitar uma pergunta:

```
What are three fun facts about lemons?
```

O modelo responderá diretamente na janela de chat. **Parabéns! Você está executando um grande modelo de linguagem localmente.**

![Lemonade App com Logs exibidos](../../dependencies/assets/ChatwithLogs.png)

No painel de Logs do Servidor no Lemonade App, você pode encontrar dados de telemetria sobre o desempenho do modelo após cada resposta. Por exemplo:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Etapa 2: Explorar a Interface Web e Diferentes Modalidades

Lemonade inclui uma interface web integrada onde você pode:

- **Interagir** com o modelo carregado em uma janela de chat familiar
- **Navegar pelos modelos** na aba Model Manager
- **Baixar novos modelos** com um clique

Tente alternar entre diferentes modalidades usando a aba **Model Manager** na interface web, onde você pode navegar pelos modelos por Recipe ou por Category:

1. **Visão:** O modelo `Gemma-4-E2B-it-GGUF` que você já tem carregado suporta visão. Cole uma imagem na caixa de chat e peça ao modelo para descrevê-la.
2. **Geração de imagens:** Na categoria Image, baixe um modelo de imagem como `SDXL-Turbo` no Model Manager e use o Lemonade Image Generator para digitar um prompt e gerar uma imagem localmente.
3. **Áudio:** Na categoria Audio, baixe um modelo de áudio como `Whisper-Tiny`, que pode fazer fala para texto. Forneça uma gravação de áudio para transcrevê-la localmente. Para texto para fala, experimente um dos modelos na categoria Speech, como `kokoro-v1`.

![Multi-Modalidade com Lemonade](../../dependencies/assets/multi_modality.png)

### Etapa 3: Experimentar um Modelo com um Backend Diferente

Se você passar o mouse sobre um modelo no Lemonade App, verá um ícone de engrenagem. Clicar nele permite selecionar opções para o modelo, incluindo a escolha do backend desejado.

Por padrão, Lemonade usa Vulkan para aceleração de GPU. Se você tiver uma GPU discreta AMD compatível, pode alternar para ROCm.

![Lemonade Selecionar Backend](../../dependencies/assets/lemonademodeloptions.png)

Para gerenciar seus backends instalados, clique no botão de backend na coluna mais à esquerda.

Como alternativa, você pode especificar o backend usando o seguinte comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Você também pode definir seu backend padrão usando a variável de ambiente `LEMONADE_LLAMACPP` com os valores: `vulkan`, `rocm` ou `cpu`.

---

## Indo Mais Fundo — Crie um Aplicativo com IA em Python

O verdadeiro poder de um servidor de IA local é que qualquer aplicativo pode se conectar a ele usando apenas algumas linhas de código. Para provar isso, vamos criar um pequeno mas funcional **gerador de flashcards de estudo**, onde você fornece um tópico, ele gera os flashcards e você pode se testar interativamente.

### Etapa 4: Iniciar o Servidor

Verifique se o servidor Lemonade está em execução. Ele normalmente inicia automaticamente em segundo plano após a instalação. Para verificar, execute:

```
lemonade status
```

Você deverá ver uma mensagem como: `Server is running on port 13305`.

Se o servidor não estiver em execução, inicie-o abrindo o aplicativo Lemonade. Use a porta padrão **13305** (você pode confirmar ou selecionar isso no ícone da bandeja do sistema).

### Etapa 5: Instalar o Cliente Python OpenAI

Em um terminal, crie um venv e instale o Cliente Python OpenAI usando os seguintes comandos:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Etapa 6: Criar o Aplicativo de Flashcards

Vamos baixar um modelo diferente para gerar código: `Qwen3.5-35B-A3B-GGUF`. Este é um modelo grande (~20 GB) e de alto desempenho, mais adequado para sistemas com 32 GB+ de RAM. Se você tiver menos RAM disponível, experimente `Qwen3.5-9B-GGUF` (~6 GB).

Você pode baixá-lo pela interface ou executar o seguinte:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Insira o seguinte prompt na interface de Chat do Lemonade para gerar o código de um aplicativo simples de Flashcards.

Usaremos Qwen3.5-35B-A3B-GGUF (um modelo maior, melhor para escrever código) para gerar nosso aplicativo Python, e o próprio aplicativo chamará Gemma-4-E2B-it-GGUF (o modelo menor que você já baixou) em tempo de execução. O código pode então ser copiado para um arquivo de sua escolha para ser executado em Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Dica**: Seguimos práticas de engenharia padrão por meio de uma criação cuidadosa de prompts e usando um sistema de dois modelos para otimizar recursos e velocidade.

Para sua conveniência, fornecemos uma saída de exemplo em [`flashcards.py`](assets/flashcards.py). Sinta-se à vontade para baixá-lo para o seu diretório. De qualquer forma, você agora deve ter um arquivo Python que pode ser executado.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Etapa 7: Executar o Código Gerado

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Veja o que você deve ver:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

Em cerca de 150 linhas de código você criou uma ferramenta de estudo totalmente funcional alimentada por um LLM local. Não há chave de API para gerenciar, sem custos de uso e nenhum dado sai da sua máquina.

> **Insight principal:** Observe que a linha `client = OpenAI(base_url=...) ` é a *única* coisa que vincula este aplicativo ao Lemonade em vez da nuvem da OpenAI. O restante do código é idêntico ao que você escreveria para qualquer serviço compatível com OpenAI. Se você já usou a biblioteca Python da OpenAI, já sabe como criar aplicativos com Lemonade.

### O Que Isso Demonstra

Este pequeno aplicativo exercita vários padrões de integração do mundo real:

| Padrão | Onde Aparece |
|---------|-----------------|
| **Prompts de sistema** | A mensagem `"system"` instrui o LLM a produzir JSON estruturado |
| **Saída estruturada** | O aplicativo analisa a resposta do LLM como JSON para criar os flashcards |
| **Requisições sem estado** | Cada chamada `generate_flashcards()` é independente |
| **Tratamento de erros** | O `try/except` lida graciosamente com casos em que a saída do LLM não é um JSON válido |

Esses mesmos padrões se aplicam a qualquer aplicativo, como chatbots, assistentes de código, geradores de conteúdo e ferramentas de automação.

#### Desafio Bônus

* Para um desafio adicional, tente atualizar o aplicativo para que os flashcards sejam lidos para o usuário, referenciando o exemplo fornecido [aqui](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Executando Modelos no NPU (Opcional)

Se você tem um Ryzen AI 300/400/Max 300 series ou Z2 Extreme, seu dispositivo possui uma **Neural Processing Unit (NPU)** integrada, um chip dedicado projetado especificamente para cargas de trabalho de IA. Executar modelos no NPU é mais eficiente em termos de energia do que usar a GPU, o que o torna ideal para tarefas de IA em segundo plano, sessões mais longas e uso com bateria.

Lemonade suporta três modos de execução de NPU, todos transparentes por trás da mesma OpenAI API:

| Modo | Como Funciona | Recipe | Modelos de Exemplo |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU processa o prompt, iGPU gera tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Somente NPU** | Toda a inferência é executada no NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Usa o mecanismo FastFlowLM no NPU, otimizado para AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisitos

- Processador **AMD Ryzen AI 300/400 series ou Z2 series**
- Para modelos **FLM**: O runtime FLM pode ser instalado dentro do aplicativo Lemonade ou o Lemonade instalará automaticamente o runtime FLM ao executar um modelo FLM. Para saber mais sobre FastFlowLM, veja [aqui](https://fastflowlm.com/docs/).


### Etapa 8: Executar um Modelo Hybrid

Os modelos Hybrid dividem o trabalho entre o NPU e o iGPU para um bom equilíbrio entre velocidade e eficiência. No Lemonade App, selecione um modelo da lista `Ryzen AI LLM`, por exemplo, `Qwen3-4B-Hybrid`, ou execute-o usando o seguinte comando:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade detecta seu NPU automaticamente e instala o backend **Ryzen AI LLM**.

> **O que está acontecendo nos bastidores?** Quando você envia uma mensagem, o NPU processa todo o seu prompt em paralelo (isso é chamado de "prefill"). Em seguida, o iGPU assume para gerar a resposta um token por vez (isso é chamado de "decode"). Essa abordagem híbrida aproveita os pontos fortes de cada chip.

### Etapa 9: Executar um Modelo FLM

Os modelos FastFlowLM (FLM) são especificamente otimizados para a arquitetura NPU XDNA2 da AMD e podem ser muito rápidos para o seu tamanho. Por exemplo, selecione `qwen3.5-4b-FLM` da lista `FastFlowLM NPU` ou use o seguinte comando:

<!-- @os:windows -->
Para habilitar `FastFlowLM` no Windows:

* Abra o menu `Backends Manager`.
* Localize a categoria de backend `FastFlowLM NPU`.
* Clique em Install NPU.
* Após a conclusão da instalação, ~36 modelos padrão estarão disponíveis no menu suspenso FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Quando o aplicativo `Lemonade` é iniciado pela primeira vez, o backend `FastFlowNPU` não está habilitado por padrão.
O aplicativo local abrirá a página de instalação para guiá-lo durante a configuração.

Para habilitar `FastFlowLM` no Linux:

* Abra o aplicativo `Lemonade`.
* Visite a documentação [oficial do FLM](https://lemonade-server.ai/flm_npu_linux.html) e siga as etapas de instalação do FLM selecionando sua distribuição Linux.
* Habilite os backports conforme instruído na página de instalação.
* Baixe a versão mais recente `v0.9.x` da [página de tags](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Para a AMD Halo Developer Platform, certifique-se de escolher Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Instale o pacote `.deb` baixado.
* Recomendado: Feche o `Lemonade App` e abra-o novamente para que as alterações sejam detectadas.
* Recomendado: Abra o `Backends Manager` e clique em Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Após uma instalação bem-sucedida, você deverá ver que `flm:npu` foi concluído no **Download Manager** dentro do **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Você pode então selecionar qualquer um dos modelos FFLM disponíveis e começar a usar o backend NPU.

Para um modelo específico, baixe o modelo desejado da [página de modelos](https://fastflowlm.com/docs/models/qwen/) e valide-o usando o comando Shell fornecido na documentação.
```
flm run qwen3.5-4b-FLM
```
ou via 
```
lemonade run qwen3.5-4b-FLM
```

Os modelos FLM incluem algumas das arquiteturas mais populares (Gemma 3, Qwen 3, Llama 3 e DeepSeek R1) e variam de menos de 1 GB a mais de 13 GB.
Lemonade detecta seu NPU automaticamente e instala o backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Dica:** Para melhor desempenho do NPU, habilite o modo turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Alternando Modelos

O aplicativo de flashcards da Etapa 6 também funciona com modelos NPU, basta alterar o nome do modelo:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Próximos Passos

Você tem um servidor de IA local rodando no seu próprio hardware, veja onde ir a seguir:

1. **Conecte seus aplicativos favoritos**: Lemonade funciona imediatamente com [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) e [muito mais](https://lemonade-server.ai/marketplace).

2. **Explore mais modelos**: Explore a [biblioteca de modelos](https://lemonade-server.ai/docs/server/server_models/) completa para encontrar modelos otimizados para codificação, raciocínio, visão e muito mais. Use o Lemonade App ou `lemonade list` para ver o que está disponível.

3. **Desbloqueie a aceleração de GPU ROCm**: Se você tiver uma GPU AMD compatível, alterne para o backend ROCm: `lemonade config set llamacpp.backend=rocm`. Veja as [GPUs AMD compatíveis](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Leia a especificação completa da API**: Lemonade suporta completions de chat, embeddings, transcrição de áudio, geração de imagens, texto para fala e muito mais. Veja a [Especificação do Servidor](https://lemonade-server.ai/docs/server/server_spec/) para cada endpoint.

5. **Contribua**: Lemonade é de código aberto. Confira o [guia de contribuição](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) e procure por [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).