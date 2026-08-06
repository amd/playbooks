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

vLLM é um motor de inferência de alto desempenho concebido para modelos de linguagem de grande dimensão (LLMs). Fornece um serviço otimizado com batching contínuo para elevado débito e uma API compatível com OpenAI para uma integração de aplicações sem interrupções. Isto torna o vLLM excelente para implementações em produção onde a velocidade e a eficiência de recursos são fundamentais.

Este manual ensina como servir LLMs utilizando vLLM em contentores na GPU integrada e interagir com modelos através da API Python da OpenAI.

## O que vai aprender

- Como configurar e iniciar um servidor vLLM com suporte AMD ROCm™
- Como interagir com modelos através de endpoints de API compatíveis com OpenAI
- Como enviar prompts para o servidor local com `vllm-prompt`

## Configurar a Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo com o AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

O vLLM é executado num contentor pré-criado com o ROCm e as respetivas dependências já compatibilizadas. Não é necessária qualquer instalação adicional.

Não existe um passo de instalação do vLLM no anfitrião. Inicie o vLLM com:

```bash
vllm-launch
```

O launcher inicia o contentor, direciona-o para a GPU integrada e expõe um servidor vLLM local compatível com OpenAI. Em alternativa, clique no ícone do vLLM na barra de tarefas.

## Início Rápido

### 1. Confirmar que o Servidor vLLM Está em Execução

O `vllm-launch` pode demorar alguns minutos a inicializar tudo. Assim que arranca, o servidor fica disponível em `http://localhost:8001`. Mantenha o terminal de arranque aberto porque o servidor é executado em primeiro plano; abra depois um terminal separado para os restantes passos. Os exemplos abaixo utilizam `Qwen/Qwen3-1.7B`; se o seu launcher estiver configurado para um modelo diferente, substitua esse ID de modelo nos pedidos.

### 2. Enviar um Prompt

Utilize o script `vllm-prompt` fornecido para enviar um pedido ao servidor local vLLM compatível com OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Conversar com o modelo utilizando a API Python da OpenAI

Uma vez que o vLLM expõe uma API compatível com OpenAI, pode utilizar o pacote Python `openai` para interagir com ele.

Primeiro, crie um ambiente virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Instale o pacote OpenAI
```bash
pip install openai
```

Crie um cliente `OpenAI` apontado para o servidor vLLM local em vez dos servidores da OpenAI. A `api_key` é exigida pelo cliente, mas o vLLM não a valida, pelo que qualquer cadeia de texto funciona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

De seguida, envie um pedido de conclusão de conversa (chat completion). Isto utiliza o mesmo formato de mensagens da API OpenAI — uma lista de mensagens com papéis como `"user"` e `"assistant"`. Definir `stream=True` significa que a resposta chegará de forma incremental em vez de tudo de uma vez:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Por fim, percorra os fragmentos transmitidos (streamed chunks) e imprima cada porção de texto à medida que chega:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

O script incluído [chat_with_model.py](assets/chat_with_model.py) contém o exemplo completo e pode ser transferido.


## Escolher e Configurar um Modelo

Por predefinição, o `vllm-launch` serve o `Qwen/Qwen3-1.7B` como modelo de teste na porta `8001`. Pode alterar o modelo, a porta e os parâmetros de serviço do vLLM sem reconstruir ou editar o contentor.

### Modelos testados pela AMD

Os seguintes modelos estão pré-configurados e validados pela AMD:

| Modelo | Notas |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modelo predefinido. Leve e rápido de carregar. |
| `openai/gpt-oss-20b` | Modelo maior para respostas de maior qualidade. |

### Iniciar um modelo diferente

Passe o ID do modelo com `--model` (ou `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Alterar a porta

Passe uma porta acima de 1024 com `--port` (ou `-p`); a predefinição é `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Se alterar a porta, aponte o `base_url` do seu cliente para a mesma porta (por exemplo, `http://localhost:8080/v1`).

### Passar parâmetros adicionais do vLLM

Quaisquer argumentos adicionais são reencaminhados diretamente para o vLLM, pelo que pode ajustar comportamentos de serviço como o comprimento de contexto ou o tipo de dados. Existem duas formas de os fornecer.

**Em linha**, depois das opções do launcher:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**De forma persistente**, num ficheiro de configuração em `~/.local/share/vLLM/vllm-launch.conf`. Este ficheiro não existe por predefinição — crie-o e adicione os seus argumentos como um array Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Utilize `+=` para adicionar aos argumentos predefinidos em vez de os substituir:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Para ver todas as opções do launcher a qualquer momento, execute:

```bash
vllm-launch --help
```

### Onde os modelos são armazenados

O `vllm-launch` procura modelos em dois locais:

| Localização | Caminho |
|----------|------|
| Modelos do sistema | `/var/cache/models` |
| Modelos do utilizador | `~/.local/share/vLLM/models` |

Pode colocar um modelo transferido em qualquer uma das pastas e iniciá-lo passando o respetivo caminho ou ID a `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Nota**: Executar o seu próprio modelo transferido desta forma deverá funcionar assim que o modelo for colocado numa das pastas acima, mas este fluxo de trabalho ainda não foi oficialmente validado pela AMD.

## Resolução de Problemas

### Ligação recusada

Certifique-se de que o servidor está em execução:
```bash
curl http://localhost:8001/health
```

## Resumo

Neste manual, aprendeu como:

- Iniciar o vLLM em contentores com suporte ROCm na GPU integrada
- Iniciar um servidor vLLM com endpoints de API compatíveis com OpenAI na porta 8001
- Enviar prompts com `vllm-prompt`
- Fazer chamadas de API ao servidor vLLM utilizando pedidos com e sem streaming
- Resolver problemas comuns relacionados com o arranque do servidor, a memória e as ligações do cliente

Tem agora uma implementação de vLLM em contentores para servir modelos de linguagem de grande dimensão com desempenho otimizado na GPU integrada.

## Próximos Passos

- **Experimente modelos diferentes** — Utilize `vllm-launch --model <model>` para experimentar diferentes LLMs e comparar o desempenho (consulte [Escolher e Configurar um Modelo](#choosing-and-configuring-a-model)).
- **Crie uma aplicação** — Utilize a API compatível com OpenAI para integrar o vLLM numa aplicação Python, chatbot ou fluxo de trabalho de automação.
- **Ajuste fino e sirva** — Faça o ajuste fino de um modelo utilizando LoRA ou QLoRA e, em seguida, implemente-o com o vLLM para inferência otimizada.
## Recursos Adicionais

- **[Documentação Oficial do vLLM](https://docs.vllm.ai/)** — Guias abrangentes e referências de API
- **[Repositório GitHub do vLLM](https://github.com/vllm-project/vllm)** — Código-fonte, problemas e discussões da comunidade