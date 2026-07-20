<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para pré-visualizar corretamente este conteúdo.
<!-- @github-only:end -->


## Visão Geral

vLLM é um mecanismo de inferência de alto desempenho projetado para grandes modelos de linguagem (LLMs). Ele fornece serviço otimizado com batching contínuo para alta taxa de transferência e uma API compatível com OpenAI para integração perfeita com aplicações. Isso torna o vLLM ótimo para implantações em produção onde velocidade e eficiência de recursos são críticas.

Este playbook ensina como servir LLMs usando o vLLM em contêiner na GPU integrada e interagir com modelos por meio da API Python da OpenAI.

## O Que Você Vai Aprender

- Como configurar e iniciar um servidor vLLM com suporte a AMD ROCm™
- Como interagir com modelos por meio de endpoints de API compatíveis com OpenAI
- Como enviar prompts ao servidor local com `vllm-prompt`

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

> **Nota**: Se o VS Code não estiver instalado, você pode instalá-lo com o AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

Este playbook usa uma imagem de contêiner pré-construída que inclui vLLM, suporte a ROCm e os scripts auxiliares necessários para iniciar o servidor. Você não precisa instalar o PyTorch, o vLLM ou os scripts locais do playbook manualmente.

Não há etapa de instalação do vLLM no host. Inicie o vLLM com:

```bash
vllm-launch
```

O launcher inicia o contêiner, direciona a GPU integrada e expõe um servidor vLLM local compatível com OpenAI. Como alternativa, clique no ícone do vLLM na barra de tarefas.

## Início Rápido

### 1. Confirme Que o Servidor vLLM Está em Execução

O `vllm-launch` pode levar alguns minutos para inicializar tudo. Assim que iniciar, o servidor estará disponível em `http://localhost:8001`. Mantenha o terminal de inicialização aberto, pois o servidor é executado em primeiro plano; em seguida, abra um terminal separado para as demais etapas. Os exemplos abaixo usam `Qwen/Qwen3-1.7B`; se o seu launcher estiver configurado para outro modelo, substitua pelo ID desse modelo nas requisições.

### 2. Envie um Prompt

Use o script `vllm-prompt` fornecido para enviar uma requisição ao servidor local vLLM compatível com OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Converse com o modelo usando a API Python da OpenAI

Como o vLLM expõe uma API compatível com OpenAI, você pode usar o pacote Python `openai` para interagir com ela.

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

Crie um cliente `OpenAI` apontando para o servidor vLLM local em vez dos servidores da OpenAI. A `api_key` é exigida pelo cliente, mas o vLLM não a valida, então qualquer string funciona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Em seguida, envie uma requisição de chat completion. Isso usa o mesmo formato de mensagens da API da OpenAI — uma lista de mensagens com papéis como `"user"` e `"assistant"`. Definir `stream=True` significa que a resposta chegará de forma incremental, em vez de tudo de uma vez:

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

Por fim, itere sobre os blocos transmitidos e imprima cada trecho de texto à medida que chega:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

O script incluído [chat_with_model.py](assets/chat_with_model.py) contém o exemplo completo e pode ser baixado.


## Solução de Problemas

### Conexão recusada

Certifique-se de que o servidor está em execução:
```bash
curl http://localhost:8001/health
```

## Resumo

Neste playbook, você aprendeu a:

- Iniciar o vLLM em contêiner com suporte a ROCm na GPU integrada
- Iniciar um servidor vLLM com endpoints de API compatíveis com OpenAI na porta 8001
- Enviar prompts com `vllm-prompt`
- Fazer chamadas de API ao servidor vLLM usando requisições em streaming e não streaming
- Solucionar problemas comuns relacionados à inicialização do servidor, memória e conexões de cliente

Agora você tem uma implantação de vLLM em contêiner para servir grandes modelos de linguagem com desempenho otimizado na GPU integrada.

## Próximos Passos

- **Experimente modelos diferentes** — Troque o modelo na configuração do `vllm-launch` para experimentar diferentes LLMs e comparar o desempenho.
- **Construa uma aplicação** — Use a API compatível com OpenAI para integrar o vLLM a um aplicativo Python, chatbot ou fluxo de automação.
- **Ajuste fino e sirva** — Faça o ajuste fino de um modelo usando LoRA ou QLoRA e, em seguida, implante-o com o vLLM para inferência otimizada.

## Recursos Adicionais

- **[Documentação Oficial do vLLM](https://docs.vllm.ai/)** — Guias abrangentes e referências de API
- **[Repositório GitHub do vLLM](https://github.com/vllm-project/vllm)** — Código-fonte, issues e discussões da comunidade