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

🍋 **Lemonade** é um servidor de IA local de código aberto que permite executar grandes modelos de linguagem (LLMs), geradores de imagem e modelos de áudio diretamente em seu próprio hardware. Ele expõe os modelos por meio da **OpenAI API**, padrão da indústria, de forma que qualquer aplicativo compatível com a OpenAI funcione instantaneamente com o Lemonade. Ao final deste guia, você estará usando o Lemonade para executar modelos localmente em sua máquina.

## O Que Você Vai Aprender

Ao final deste guia, você será capaz de:

* **Instalar o Lemonade Server** e verificar se ele está em execução.
* **Baixar e conversar com um LLM** usando um único comando.
* **Explorar a interface web** e experimentar diferentes modalidades, como visão, conversão de fala em texto e geração de imagens.
* **Alternar entre backends de GPU** entre Vulkan e o software AMD ROCm™.
* **Construir um aplicativo em Python** com um LLM local, usando a API compatível com a OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Executar modelos na Unidade de Processamento Neural (NPU) da AMD** usando os modos de execução Hybrid e FLM em hardware AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Definindo a Configuração de Memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificando Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

Antes de começar, certifique-se de que você tenha:

- Um PC executando **Windows 11** ou uma distribuição **Linux** compatível (Ubuntu 24.04+, Fedora, Debian)
- **16 GB de RAM** é o recomendado para o modelo de runtime usado nas Etapas 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** é recomendado se você quiser usar o modelo de geração de código maior na Etapa 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB de espaço livre em disco**, dependendo dos modelos que você baixar. O maior modelo neste guia tem cerca de 20 GB.
- **Python 3.10–3.13** (usado na seção do aplicativo Python)
- Uma conexão com a internet (com ou sem fio)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcional] Uma NPU AMD XDNA 2 (série Ryzen AI 300/400/Max 300 ou Z2 Extreme) com o driver mais recente instalado a partir das [Instruções de Instalação do Software Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), caso você queira executar um modelo na NPU.
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
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

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
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

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

Antes de executarmos um modelo, vale a pena entender *por que* as coisas são configuradas dessa forma. O Lemonade é um **servidor de modelo local**, um processo que carrega modelos de IA na memória e os expõe para aplicativos por HTTP, exatamente como um serviço de IA em nuvem faria.

### Por Que Usar um Servidor?

| Benefício | O Que Isso Significa para Você |
|---------|----------------------|
| **Integração simplificada** | Os aplicativos se comunicam com uma única API HTTP, em vez de lidar com bibliotecas C++ ou Python específicas de hardware. |
| **Modelos compartilhados** | Um único modelo carregado pode atender vários aplicativos ao mesmo tempo, sem cópias duplicadas consumindo sua RAM. |
| **Portabilidade da nuvem para o local** | Código escrito para a API em nuvem da OpenAI funciona com o Lemonade apenas alterando uma URL. |
| **Separação de responsabilidades** | O gerenciamento de modelos, o streaming e a tolerância a falhas são tratados pelo servidor, permitindo que os desenvolvedores se concentrem em seu aplicativo. |

### O Padrão da API da OpenAI

O Lemonade implementa a **OpenAI API**, a mesma interface usada pelo ChatGPT, Azure OpenAI e dezenas de outros serviços. O modelo de conversa é simples:

| Papel | Quem Está Falando |
|------|---------------|
| **system** | Instruções para o modelo (persona, restrições, ferramentas disponíveis) |
| **user** | Mensagens do humano (ou aplicativo) para o modelo |
| **assistant** | Respostas geradas pelo modelo |

Isso significa que qualquer biblioteca ou aplicativo compatível com a OpenAI pode se comunicar com o Lemonade apontando para `http://localhost:13305/api/v1` enquanto o Lemonade Server estiver em execução.

## Atividade Principal — Seu Primeiro Chat de IA Local

Vamos baixar um LLM e conversar com ele, executando a IA inteiramente em sua própria máquina.

### Etapa 1: Baixar e Executar um Modelo

O Lemonade vem com uma biblioteca de modelos selecionada. Vamos começar com o **Gemma-4-E2B-it**, um modelo compacto e capaz que inclui suporte a visão. Abra um terminal e execute:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Este único comando faz três coisas:

1. **Baixa** o modelo (~3 GB) do Hugging Face, caso ainda não tenha sido baixado. (Pode levar algum tempo)
2. **Inicia** o processo do Lemonade Server na porta 13305.
3. **Abre o Lemonade App** para que você possa começar a conversar com o modelo.


<!-- @os:windows -->
No Windows, o Lemonade App é iniciado automaticamente e você pode começar a conversar imediatamente. Se você instalou o pacote `minimal.msi`, o aplicativo não está incluído. Para começar a conversar, abra seu navegador da web e acesse `http://localhost:13305`.
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

### Passo 2: Explore a Interface Web e as Diferentes Modalidades

O Lemonade inclui uma interface web integrada onde você pode:

- **Interagir** com o modelo carregado em uma janela de chat familiar
- **Navegar por modelos** na aba Model Manager
- **Baixar novos modelos** com um clique

Experimente alternar entre diferentes modalidades usando a aba **Model Manager** na interface web, onde você pode navegar pelos modelos por Recipe ou por Category:

1. **Visão:** O modelo `Gemma-4-E2B-it-GGUF` que você já tem carregado é compatível com visão. Cole uma imagem na caixa de chat e peça ao modelo para descrevê-la.
2. **Geração de imagem:** Na categoria Image, baixe um modelo de imagem como o `SDXL-Turbo` no Model Manager e, em seguida, use o Lemonade Image Generator para digitar um prompt e gerar uma imagem localmente.
3. **Áudio:** Na categoria Audio, baixe um modelo de áudio como o `Whisper-Tiny`, que pode fazer conversão de fala em texto. Forneça uma gravação de áudio para transcrevê-la localmente. Para conversão de texto em fala, experimente um dos modelos na categoria Speech, como o `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Passo 3: Experimente um Modelo com um Backend Diferente

Se você passar o mouse sobre um modelo no Lemonade App, verá um ícone de engrenagem. Clicar nele permite selecionar opções para o modelo, incluindo a escolha do backend desejado.

Por padrão, o Lemonade usa Vulkan para aceleração de GPU. Se você tiver uma GPU discreta AMD compatível, pode alternar para ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Para gerenciar seus backends instalados, clique no botão de backend na coluna mais à esquerda.

Alternativamente, você pode especificar o backend usando o seguinte comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Você também pode definir seu backend padrão usando a variável de ambiente `LEMONADE_LLAMACPP` com os valores: `vulkan`, `rocm`, ou `cpu`.

---

## Indo Mais Fundo — Construa um App com IA em Python

O verdadeiro poder de um servidor de IA local é que qualquer aplicativo pode se conectar a ele usando apenas algumas linhas de código. Para comprovar isso, vamos construir um pequeno mas funcional **gerador de flashcards de estudo**, no qual você fornece um tópico, ele gera flashcards, e você pode testar seus conhecimentos de forma interativa.

### Passo 4: Inicie o Servidor

Verifique se o servidor Lemonade está em execução. Ele normalmente inicia automaticamente em segundo plano após a instalação. Para verificar, execute:

```
lemonade status
```

Você deverá ver uma mensagem como: `Server is running on port 13305`.

Se o servidor não estiver em execução, inicie-o abrindo o aplicativo Lemonade. Use a porta padrão **13305** (você pode confirmar ou selecioná-la a partir do ícone na bandeja do sistema).

### Passo 5: Instale o Cliente Python do OpenAI

Em um terminal, crie um venv e instale o Cliente Python do OpenAI usando os seguintes comandos:
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

### Passo 6: Construa o App de Flashcards

Vamos baixar um modelo diferente para gerar código: `Qwen3.5-35B-A3B-GGUF`. Este é um modelo grande (~20 GB) e de alto desempenho, mais indicado para sistemas com 32 GB ou mais de RAM. Se você tiver menos RAM disponível, experimente o `Qwen3.5-9B-GGUF` (~6 GB) em vez dele.

Você pode baixá-lo pela interface ou executar o seguinte:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Insira o seguinte prompt na Lemonade Chat UI para gerar código para um app simples de Flashcard.

Usaremos o Qwen3.5-35B-A3B-GGUF (um modelo maior, melhor para escrever código) para gerar nosso app Python, e o próprio app chamará o Gemma-4-E2B-it-GGUF (o modelo menor que você já baixou) em tempo de execução. O código pode então ser copiado para um arquivo de sua escolha para ser executado em Python.

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

> **Dica**: Seguimos práticas padrão de engenharia por meio da criação cuidadosa de prompts e do uso de um sistema com dois modelos para otimizar recursos e velocidade.

Para sua conveniência, fornecemos um exemplo de saída em [`flashcards.py`](assets/flashcards.py). Sinta-se à vontade para baixá-lo para o seu diretório. De qualquer forma, agora você deve ter um arquivo Python pronto para ser executado.

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


### Passo 7: Execute o Código Gerado

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

Em cerca de 150 linhas de código, você construiu uma ferramenta de estudo totalmente funcional, alimentada por um LLM local. Não há chave de API para gerenciar, nenhum custo de uso e nenhum dado sai da sua máquina.

> **Insight importante:** Observe que a linha `client = OpenAI(base_url=...) ` é a *única* coisa que conecta este app ao Lemonade em vez da nuvem do OpenAI. O restante do código é idêntico ao que você escreveria contra qualquer serviço compatível com OpenAI. Se você já usou a biblioteca Python do OpenAI, já sabe como construir aplicativos com o Lemonade.

### O Que Isso Demonstra

Este pequeno app exercita vários padrões de integração do mundo real:

| Padrão | Onde Aparece |
|---------|-----------------|
| **Prompts de sistema** | A mensagem `"system"` instrui o LLM a gerar JSON estruturado |
| **Saída estruturada** | O app analisa a resposta do LLM como JSON para construir os flashcards |
| **Requisições sem estado** | Cada chamada de `generate_flashcards()` é independente |
| **Tratamento de erros** | O `try/except` lida de forma adequada com casos em que a saída do LLM não é um JSON válido |

Esses mesmos padrões se aplicam a qualquer aplicativo, como chatbots, assistentes de código, geradores de conteúdo e ferramentas de automação.

#### Desafio Bônus

* Para um desafio adicional, tente atualizar o app para que os flashcards sejam lidos em voz alta para o usuário, consultando o exemplo fornecido [aqui](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Executando Modelos na NPU (Opcional)

Se você tem um Ryzen AI série 300/400/Max 300 ou Z2 Extreme, seu dispositivo possui uma **Unidade de Processamento Neural (NPU)** integrada, um chip dedicado projetado especificamente para cargas de trabalho de IA. Executar modelos na NPU é mais eficiente em termos de energia do que usar a GPU, o que a torna ideal para tarefas de IA em segundo plano, sessões mais longas e uso com bateria.

O Lemonade suporta três modos de execução na NPU, todos transparentes por trás da mesma API OpenAI:

| Modo | Como Funciona | Recipe | Modelos de Exemplo |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | A NPU processa o prompt, a iGPU gera os tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Somente NPU** | Toda a inferência é executada na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Usa o mecanismo FastFlowLM na NPU, otimizado para AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisitos

- Processador **AMD Ryzen AI série 300/400 ou série Z2**
- Para modelos **FLM**: O runtime FLM pode ser instalado diretamente no app Lemonade, ou o Lemonade instalará automaticamente o runtime FLM ao executar um modelo FLM. Para saber mais sobre o FastFlowLM, consulte [aqui](https://fastflowlm.com/docs/).


### Etapa 8: Executar um Modelo Hybrid

Os modelos Hybrid dividem o trabalho entre a NPU e a iGPU para um bom equilíbrio entre velocidade e eficiência. No app Lemonade, selecione um modelo na lista `Ryzen AI LLM`, por exemplo, `Qwen3-4B-Hybrid`, ou execute-o usando o seguinte comando:

```
lemonade run Qwen3-4B-Hybrid
```

O Lemonade detecta sua NPU automaticamente e instala o backend **Ryzen AI LLM**.

> **O que está acontecendo por trás dos panos?** Quando você envia uma mensagem, a NPU processa todo o seu prompt em paralelo (isso é chamado de "prefill"). Em seguida, a iGPU assume para gerar a resposta um token de cada vez (isso é chamado de "decode"). Essa abordagem híbrida explora os pontos fortes de cada chip.

### Etapa 9: Executar um Modelo FLM

Os modelos FastFlowLM (FLM) são especificamente otimizados para a arquitetura NPU XDNA2 da AMD e podem ser muito rápidos para o seu tamanho. Por exemplo, selecione `qwen3.5-4b-FLM` na lista `FastFlowLM NPU` ou use o seguinte comando:

<!-- @os:windows -->
Para ativar o `FastFlowLM` no Windows:

* Abra o menu `Backends Manager`.
* Localize a categoria de backend `FastFlowLM NPU`.
* Clique em Install NPU.
* Após a conclusão da instalação, cerca de 36 modelos padrão estarão disponíveis no menu suspenso FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Quando o app `Lemonade` é iniciado pela primeira vez, o backend `FastFlowNPU` não é ativado por padrão.
O app local abrirá a página de instalação para guiá-lo pelo processo de configuração.

Para ativar o `FastFlowLM` no Linux:

* Abra o app `Lemonade`.
* Visite a documentação [oficial do FLM](https://lemonade-server.ai/flm_npu_linux.html) e siga as etapas de instalação do FLM selecionando sua distribuição Linux.
* Ative os backports conforme instruído na página de instalação.
* Baixe a versão mais recente `v0.9.x` na [página de tags](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Para o AMD Halo Developer Platform, certifique-se de escolher o Debian 13.
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
Após uma instalação bem-sucedida, você deve ver que o `flm:npu` foi concluído no **Download Manager** dentro do **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Você pode então selecionar qualquer um dos modelos FFLM disponíveis e começar a usar o backend da NPU.

Para um modelo específico, baixe o modelo desejado na [página de modelos](https://fastflowlm.com/docs/models/qwen/) e valide-o usando o comando Shell fornecido na documentação.
```
flm run qwen3.5-4b-FLM
```
ou via 
```
lemonade run qwen3.5-4b-FLM
```

Os modelos FLM incluem algumas das arquiteturas mais populares (Gemma 3, Qwen 3, Llama 3 e DeepSeek R1) e variam de menos de 1 GB a mais de 13 GB.
O Lemonade detecta sua NPU automaticamente e instala o backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Dica:** Para o melhor desempenho da NPU, ative o modo turbo:
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

Você tem um servidor de IA local rodando no seu próprio hardware, aqui está para onde ir a seguir:

1. **Conecte seus aplicativos favoritos**: O Lemonade funciona imediatamente com [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) e [muitos outros](https://lemonade-server.ai/marketplace).

2. **Explore mais modelos**: Explore a [biblioteca de modelos](https://lemonade-server.ai/docs/server/server_models/) completa para encontrar modelos otimizados para codificação, raciocínio, visão e mais. Use o app Lemonade ou `lemonade list` para ver o que está disponível.

3. **Desbloqueie a aceleração de GPU ROCm**: Se você tiver uma GPU AMD suportada, mude para o backend ROCm: `lemonade config set llamacpp.backend=rocm`. Consulte as [GPUs AMD suportadas](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Leia a especificação completa da API**: O Lemonade suporta chat completions, embeddings, transcrição de áudio, geração de imagens, texto para fala e muito mais. Consulte a [Especificação do Servidor](https://lemonade-server.ai/docs/server/server_spec/) para conhecer todos os endpoints.

5. **Contribua**: O Lemonade é open source. Confira o [guia de contribuição](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) e procure por [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->