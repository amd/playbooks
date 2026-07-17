<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para visualizar este conteúdo corretamente.
<!-- @github-only:end -->


## Visão Geral

vLLM é um motor de inferência de alto desempenho projetado para modelos de linguagem de grande escala (LLMs). Ele oferece serviço otimizado com batching contínuo para alto throughput e uma API compatível com OpenAI para integração perfeita com aplicações. Isso torna o vLLM excelente para implantações em produção onde velocidade e eficiência de recursos são críticas.

Este playbook ensina como servir LLMs usando vLLM em contêiner na GPU integrada e interagir com modelos por meio da API Python do OpenAI.

## O Que Você Aprenderá

- Como configurar e iniciar um servidor vLLM com suporte ao AMD ROCm™
- Como interagir com modelos via endpoints de API compatíveis com OpenAI
- Como enviar prompts ao servidor local com `vllm-prompt`

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

> **Nota**: Se o VS Code não estiver instalado, você pode instalá-lo com o AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando Pré-requisitos de Software

Este playbook usa uma imagem de contêiner pré-construída que inclui vLLM, suporte a ROCm e os scripts auxiliares necessários para iniciar o servidor. Você não precisa instalar PyTorch, vLLM ou scripts locais do playbook manualmente.

Não há etapa de instalação do vLLM no host. Inicie o vLLM com:

```bash
vllm-launch
```

O launcher inicia o contêiner, direciona para a GPU integrada e expõe um servidor vLLM local compatível com OpenAI. Alternativamente, clique no ícone do vLLM na barra de tarefas.

## Início Rápido

### 1. Confirmar que o Servidor vLLM Está em Execução

O `vllm-launch` pode levar alguns minutos para inicializar tudo. Uma vez iniciado, o servidor está disponível em `http://localhost:8001`. Mantenha o terminal de lançamento aberto porque o servidor é executado em primeiro plano, depois abra um terminal separado para as etapas restantes. Os exemplos abaixo usam `Qwen/Qwen3-1.7B`; se o seu launcher estiver configurado para um modelo diferente, substitua esse ID de modelo nas requisições.

### 2. Enviar um Prompt

Use o script `vllm-prompt` fornecido para enviar uma requisição ao servidor vLLM local compatível com OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Conversar com o modelo usando a API Python do OpenAI

Como o vLLM expõe uma API compatível com OpenAI, você pode usar o pacote Python `openai` para interagir com ele.

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

Crie um cliente `OpenAI` apontado para o servidor vLLM local em vez dos servidores do OpenAI. O `api_key` é exigido pelo cliente, mas o vLLM não o valida, portanto qualquer string funciona:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Em seguida, envie uma requisição de conclusão de chat. Isso usa o mesmo formato de mensagem da API do OpenAI — uma lista de mensagens com papéis como `"user"` e `"assistant"`. Definir `stream=True` significa que a resposta chegará de forma incremental em vez de tudo de uma vez:

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

Por fim, itere sobre os fragmentos transmitidos e imprima cada parte do texto conforme ela chega:

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

Neste playbook, você aprendeu como:

- Iniciar o vLLM em contêiner com suporte a ROCm na GPU integrada
- Iniciar um servidor vLLM com endpoints de API compatíveis com OpenAI na porta 8001
- Enviar prompts com `vllm-prompt`
- Fazer chamadas de API ao servidor vLLM usando requisições com e sem streaming
- Solucionar problemas comuns com inicialização do servidor, memória e conexões de cliente

Agora você tem uma implantação vLLM em contêiner para servir modelos de linguagem de grande escala com desempenho otimizado na GPU integrada.

## Próximos Passos

- **Experimente modelos diferentes** — Troque o modelo na configuração do `vllm-launch` para experimentar diferentes LLMs e comparar o desempenho.
- **Construa uma aplicação** — Use a API compatível com OpenAI para integrar o vLLM em um aplicativo Python, chatbot ou fluxo de trabalho de automação.
- **Ajuste fino e sirva** — Faça ajuste fino de um modelo usando LoRA ou QLoRA, depois implante-o com vLLM para inferência otimizada.

## Recursos Adicionais

- **[Documentação Oficial do vLLM](https://docs.vllm.ai/)** — Guias abrangentes e referências de API
- **[Repositório vLLM no GitHub](https://github.com/vllm-project/vllm)** — Código-fonte, issues e discussões da comunidade