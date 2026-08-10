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

## Visão Geral

🍋 **Lemonade** é um servidor de IA local de código aberto que permite executar modelos de linguagem de grande dimensão (LLMs), geradores de imagem e modelos de áudio diretamente no seu próprio hardware. Expõe os modelos através da API padrão da indústria **OpenAI API**, pelo que qualquer aplicação que funcione com a OpenAI pode funcionar instantaneamente com o Lemonade. No final deste playbook, estará a utilizar o Lemonade para executar modelos localmente na sua máquina.

## O Que Vai Aprender

No final deste playbook, será capaz de:

* **Instalar o Lemonade Server** e verificar se está a funcionar.
* **Descarregar e conversar com um LLM** utilizando um único comando.
* **Explorar a interface web** e experimentar diferentes modalidades, como visão, conversão de voz em texto e geração de imagens.
* **Alternar entre backends de GPU**, entre Vulkan e o software AMD ROCm™.
* **Criar uma aplicação Python** alimentada por um LLM local, utilizando a API compatível com OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Executar modelos na Unidade de Processamento Neural (NPU) da AMD** utilizando os modos de execução Hybrid e FLM em hardware AMD Ryzen™ AI.
<!-- @device:end -->

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

Antes de começar, certifique-se de que tem:

- Um PC com **Windows 11** ou uma distribuição **Linux** suportada (Ubuntu 24.04+, Fedora, Debian)
- Recomendam-se **16 GB de RAM** para o modelo de runtime utilizado nos Passos 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Recomendam-se **32 GB+** se pretender utilizar o modelo de geração de código maior no Passo 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB de espaço livre em disco**, dependendo dos modelos que descarregar. O modelo maior neste guia tem cerca de 20 GB.
- **Python 3.10–3.13** (utilizado na secção da aplicação Python)
- Uma ligação à Internet (com fios ou sem fios)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcional] Uma NPU AMD XDNA 2 (série Ryzen AI 300/400/Max 300 ou Z2 Extreme) com o controlador mais recente instalado a partir das [Instruções de Instalação do Software Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), caso pretenda executar um modelo na NPU.
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
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
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

## Conceitos Fundamentais — Como Funcionam os Servidores de IA Locais

Antes de executarmos um modelo, vale a pena compreender *porque* é que as coisas estão configuradas desta forma. O Lemonade é um **servidor de modelo local**, um processo que carrega modelos de IA para a memória e os expõe a aplicações através de HTTP, tal como faria um serviço de IA na cloud.

### Porquê um Servidor?

| Benefício | O Que Significa Para Si |
|---------|----------------------|
| **Integração simplificada** | As aplicações comunicam com uma única API HTTP, em vez de lidarem com bibliotecas C++ ou Python específicas do hardware. |
| **Modelos partilhados** | Um único modelo carregado pode servir várias aplicações em simultâneo, sem cópias duplicadas a ocupar a sua RAM. |
| **Portabilidade da cloud para o local** | O código escrito para a API da cloud da OpenAI funciona com o Lemonade bastando alterar um URL. |
| **Separação de responsabilidades** | A gestão de modelos, o streaming e a tolerância a falhas são tratados pelo servidor, para que os programadores se possam concentrar na sua aplicação. |

### O Padrão da API OpenAI

O Lemonade implementa a **OpenAI API**, a mesma interface utilizada pelo ChatGPT, Azure OpenAI e dezenas de outros serviços. O modelo de conversação é simples:

| Função | Quem Está a Falar |
|------|---------------|
| **system** | Instruções para o modelo (persona, restrições, ferramentas disponíveis) |
| **user** | Mensagens do humano (ou aplicação) para o modelo |
| **assistant** | Respostas geradas pelo modelo |

Isto significa que qualquer biblioteca ou aplicação que suporte a OpenAI pode comunicar com o Lemonade, bastando apontá-la para `http://localhost:13305/api/v1` enquanto o Lemonade Server estiver em execução.

## Atividade Principal — O Seu Primeiro Chat de IA Local

Vamos descarregar um LLM e ter uma conversa com ele, executando a IA inteiramente na sua própria máquina.

### Passo 1: Descarregar e Executar um Modelo

O Lemonade inclui uma biblioteca de modelos selecionada. Vamos começar com o **Gemma-4-E2B-it**, um modelo capaz e compacto que inclui suporte para visão. Abra um terminal e execute:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Este único comando faz três coisas:

1. **Descarrega** o modelo (~3 GB) do Hugging Face, caso ainda não tenha sido descarregado. (Pode demorar algum tempo)
2. **Inicia** o processo do Lemonade Server na porta 13305.
3. **Abre a Lemonade App** para que possa começar a conversar com o modelo.


<!-- @os:windows -->
No Windows, a Lemonade App é iniciada automaticamente e pode começar a conversar de imediato. Se instalou o pacote `minimal.msi`, a aplicação não está incluída. Para começar a conversar, abra o seu navegador web e aceda a `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
No Linux, abra o seu navegador e navegue até `http://localhost:13305` para aceder à aplicação web.
<!-- @os:end -->

Experimente escrever uma pergunta:

```
What are three fun facts about lemons?
```

O modelo irá responder diretamente na janela de chat. **Parabéns! Está a executar um modelo de linguagem de grande dimensão localmente.**

![Lemonade App com Registos apresentados](../../dependencies/assets/ChatwithLogs.png)

No painel de Registos do Servidor na Lemonade App, pode encontrar dados de telemetria sobre o desempenho do modelo após cada resposta. Por exemplo:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Passo 2: Explorar a Interface Web e as Diferentes Modalidades

O Lemonade inclui uma interface web integrada onde pode:

- **Interagir** com o modelo carregado numa janela de conversação familiar
- **Procurar modelos** no separador Model Manager
- **Descarregar novos modelos** com um único clique

Experimente alternar entre diferentes modalidades utilizando o separador **Model Manager** na interface web, onde pode procurar modelos por Recipe ou por Category:

1. **Visão:** O modelo `Gemma-4-E2B-it-GGUF` que já tem carregado suporta visão. Cole uma imagem na caixa de conversação e peça ao modelo para a descrever.
2. **Geração de imagens:** Na categoria Image, descarregue um modelo de imagem como o `SDXL-Turbo` a partir do Model Manager e, em seguida, utilize o Lemonade Image Generator para escrever uma instrução e gerar uma imagem localmente.
3. **Áudio:** Na categoria Audio, descarregue um modelo de áudio como o `Whisper-Tiny`, que consegue converter fala em texto. Forneça uma gravação de áudio para a transcrever localmente. Para conversão de texto em fala, experimente um dos modelos na categoria Speech, como o `kokoro-v1`.

![Multi-Modalidade com o Lemonade](../../dependencies/assets/multi_modality.png)

### Passo 3: Experimentar um Modelo com um Backend Diferente

Se passar o cursor sobre um modelo na aplicação Lemonade, verá um ícone de engrenagem. Ao clicar nele, pode selecionar opções para o modelo, incluindo a escolha do backend pretendido.

Por predefinição, o Lemonade utiliza o Vulkan para aceleração por GPU. Se tiver uma GPU discreta AMD suportada, pode mudar para o ROCm.

![Selecionar Backend do Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Para gerir os seus backends instalados, clique no botão de backend na coluna mais à esquerda.

Em alternativa, pode especificar o backend utilizando o seguinte comando:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Também pode definir o seu backend predefinido utilizando a variável de ambiente `LEMONADE_LLAMACPP` com os valores: `vulkan`, `rocm`, ou `cpu`.

---

## Ir Mais Longe — Criar uma Aplicação com Tecnologia de IA em Python

O verdadeiro poder de um servidor de IA local reside no facto de qualquer aplicação se poder ligar a ele com apenas algumas linhas de código. Para o comprovar, vamos criar um pequeno mas funcional **gerador de flashcards de estudo**, onde indica um tópico, este gera flashcards, e pode testar-se a si próprio de forma interativa.

### Passo 4: Iniciar o Servidor

Verifique se o servidor Lemonade está em execução. Normalmente, inicia automaticamente em segundo plano após a instalação. Para verificar, execute:

```
lemonade status
```

Deverá ver uma mensagem semelhante a: `Server is running on port 13305`.

Se o servidor não estiver em execução, inicie-o abrindo a aplicação Lemonade. Utilize a porta predefinida **13305** (pode confirmar ou selecionar esta opção a partir do ícone da bandeja do sistema).

### Passo 5: Instalar o Cliente Python da OpenAI

Num terminal, crie um venv e instale o Cliente Python da OpenAI utilizando os seguintes comandos:
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

### Passo 6: Construir a Aplicação de Flashcards

Vamos descarregar um modelo diferente para gerar código: `Qwen3.5-35B-A3B-GGUF`. Este é um modelo grande (~20 GB) e de elevado desempenho, mais adequado a sistemas com 32 GB ou mais de RAM. Se tiver menos RAM disponível, experimente antes o `Qwen3.5-9B-GGUF` (~6 GB).

Pode descarregá-lo a partir da interface ou executar o seguinte:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Introduza a seguinte instrução na Interface de Conversação do Lemonade para gerar código para uma aplicação simples de Flashcards. 

Vamos utilizar o Qwen3.5-35B-A3B-GGUF (um modelo maior, mais apto para escrever código) para gerar a nossa aplicação Python, e a própria aplicação irá chamar o Gemma-4-E2B-it-GGUF (o modelo mais pequeno que já descarregou) em tempo de execução. O código pode depois ser copiado para um ficheiro à sua escolha para ser executado em Python.

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

> **Sugestão**: Seguimos boas práticas de engenharia através da criação cuidada de instruções e da utilização de um sistema de dois modelos para otimizar recursos e velocidade.

Para sua conveniência, fornecemos um exemplo de resultado em [`flashcards.py`](assets/flashcards.py). Sinta-se à vontade para o descarregar para o seu diretório. De qualquer das formas, deverá agora ter um ficheiro Python pronto a ser executado.

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


### Passo 7: Executar o Código Gerado

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Aqui está o que deverá ver:**

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

Em cerca de 150 linhas de código, construiu uma ferramenta de estudo totalmente funcional, com tecnologia de um LLM local. Não existe nenhuma chave de API para gerir, nenhum custo de utilização, e nenhum dado sai da sua máquina.

> **Ponto-chave:** Repare que a linha `client = OpenAI(base_url=...) ` é a *única* coisa que liga esta aplicação ao Lemonade em vez da cloud da OpenAI. O restante código é idêntico ao que escreveria para qualquer serviço compatível com a OpenAI. Se alguma vez utilizou a biblioteca Python da OpenAI, já sabe como criar aplicações com o Lemonade.

### O Que Isto Demonstra

Esta pequena aplicação exercita vários padrões de integração do mundo real:

| Padrão | Onde Aparece |
|---------|-----------------|
| **Instruções de sistema** | A mensagem `"system"` indica ao LLM para produzir JSON estruturado |
| **Saída estruturada** | A aplicação analisa a resposta do LLM como JSON para construir os flashcards |
| **Pedidos sem estado** | Cada chamada a `generate_flashcards()` é independente |
| **Tratamento de erros** | O `try/except` trata de forma controlada os casos em que a saída do LLM não é JSON válido |

Estes mesmos padrões são aplicáveis a qualquer aplicação, como chatbots, assistentes de código, geradores de conteúdo ou ferramentas de automação.

#### Desafio Extra

* Para um desafio adicional, experimente atualizar a aplicação para que os flashcards sejam lidos ao utilizador, consultando o exemplo disponível [aqui](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Executar Modelos na NPU (Opcional)

Se tiver um Ryzen AI 300/400/Max 300 series ou Z2 Extreme, o seu dispositivo tem uma **Neural Processing Unit (NPU)** incorporada, um chip dedicado concebido especificamente para cargas de trabalho de IA. Executar modelos na NPU é mais eficiente em termos energéticos do que utilizar a GPU, o que a torna ideal para tarefas de IA em segundo plano, sessões mais longas e utilização com bateria.

O Lemonade suporta três modos de execução na NPU, todos transparentes por trás da mesma API OpenAI:

| Modo | Como Funciona | Recipe | Modelos de Exemplo |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | A NPU processa o prompt, a iGPU gera tokens | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Apenas NPU** | Toda a inferência é executada na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Utiliza o motor FastFlowLM na NPU, otimizado para AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Requisitos

- Processador **AMD Ryzen AI 300/400 series ou Z2 series**
- Para modelos **FLM**: O runtime FLM pode ser instalado a partir da aplicação Lemonade ou o Lemonade instalará automaticamente o runtime FLM ao executar um modelo FLM. Para saber mais sobre o FastFlowLM, consulte [aqui](https://fastflowlm.com/docs/).


### Passo 8: Executar um Modelo Hybrid

Os modelos Hybrid dividem o trabalho entre a NPU e a iGPU para um bom equilíbrio entre velocidade e eficiência. Na Lemonade App, selecione um modelo da lista `Ryzen AI LLM`, por exemplo, `Qwen3-4B-Hybrid`, ou execute-o utilizando o seguinte comando:

```
lemonade run Qwen3-4B-Hybrid
```

O Lemonade deteta automaticamente a sua NPU e instala o backend **Ryzen AI LLM**.

> **O que está a acontecer nos bastidores?** Quando envia uma mensagem, a NPU processa todo o seu prompt em paralelo (a isto chama-se "prefill"). Depois, a iGPU assume o controlo para gerar a resposta um token de cada vez (a isto chama-se "decode"). Esta abordagem híbrida tira partido dos pontos fortes de cada chip.

### Passo 9: Executar um Modelo FLM

Os modelos FastFlowLM (FLM) são especificamente otimizados para a arquitetura NPU XDNA2 da AMD e podem ser muito rápidos para o seu tamanho. Por exemplo, selecione `qwen3.5-4b-FLM` na lista `FastFlowLM NPU` ou utilize o seguinte comando:

<!-- @os:windows -->
Para ativar o `FastFlowLM` no Windows:

* Abra o menu `Backends Manager`.
* Localize a categoria de backend `FastFlowLM NPU`.
* Clique em Install NPU.
* Após a conclusão da instalação, ~36 modelos predefinidos estarão disponíveis no menu suspenso FFLM.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Quando a aplicação `Lemonade` é iniciada pela primeira vez, o backend `FastFlowNPU` não está ativado por predefinição. 
A aplicação local abrirá a página de instalação para o guiar através da configuração.

Para ativar o `FastFlowLM` no Linux:

* Abra a aplicação `Lemonade`.
* Visite a documentação [official FLM](https://lemonade-server.ai/flm_npu_linux.html) e siga os passos de instalação do FLM selecionando a sua distribuição Linux.
* Ative os backports conforme indicado na página de instalação.
* Descarregue a versão mais recente `v0.9.x` a partir da [tags page](https://github.com/FastFlowLM/FastFlowLM/tags).'
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
* Instale o pacote `.deb` descarregado.
* Recomendado: Feche a `Lemonade App` e abra-a novamente para que as alterações sejam detetadas.
* Recomendado: Abra o `Backends Manager` e clique em Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Após uma instalação bem-sucedida, deverá ver que `flm:npu` foi concluído no **Download Manager** dentro da **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Pode então selecionar qualquer um dos modelos FFLM disponíveis e começar a utilizar o backend da NPU.

Para um modelo específico, descarregue o modelo pretendido a partir da [models page](https://fastflowlm.com/docs/models/qwen/) e valide-o utilizando o comando Shell fornecido na documentação.
```
flm run qwen3.5-4b-FLM
```
ou através de 
```
lemonade run qwen3.5-4b-FLM
```

Os modelos FLM incluem algumas das arquiteturas mais populares (Gemma 3, Qwen 3, Llama 3 e DeepSeek R1) e variam entre menos de 1 GB e mais de 13 GB.
O Lemonade deteta automaticamente a sua NPU e instala o backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Dica:** Para obter o melhor desempenho da NPU, ative o modo turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Trocar de Modelos

A aplicação de flashcards do Passo 6 também funciona com modelos NPU, basta alterar o nome do modelo:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Próximos Passos

Tem agora um servidor de IA local a funcionar no seu próprio hardware, eis para onde ir a seguir:

1. **Ligue as suas aplicações favoritas**: O Lemonade funciona de imediato com [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/), e [muitas mais](https://lemonade-server.ai/marketplace).

2. **Explore mais modelos**: Explore a [biblioteca de modelos](https://lemonade-server.ai/docs/server/server_models/) completa para encontrar modelos otimizados para programação, raciocínio, visão e muito mais. Utilize a Lemonade App ou `lemonade list` para ver o que está disponível.

3. **Desbloqueie a aceleração de GPU ROCm**: Se tiver uma GPU AMD suportada, mude para o backend ROCm: `lemonade config set llamacpp.backend=rocm`. Consulte as [GPUs AMD suportadas](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Leia a especificação completa da API**: O Lemonade suporta chat completions, embeddings, transcrição de áudio, geração de imagens, texto para voz e muito mais. Consulte a [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) para conhecer todos os endpoints.

5. **Contribua**: O Lemonade é open source. Consulte o [guia de contribuição](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) e procure por [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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