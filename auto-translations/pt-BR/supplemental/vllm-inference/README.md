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

vLLM é um mecanismo de inferência de alto desempenho projetado para modelos de linguagem grandes (LLMs). Ele fornece serviço otimizado com batching contínuo para alta taxa de transferência e uma API compatível com o OpenAI para integração perfeita com aplicações. Isso torna o vLLM ótimo para implantações em produção onde velocidade e eficiência de recursos são fundamentais.

Este playbook ensina como servir LLMs usando o vLLM em contêiner na GPU integrada e interagir com modelos por meio da API Python do OpenAI.

## O Que Você Vai Aprender

- Como configurar e iniciar um servidor vLLM com suporte AMD ROCm™
- Como interagir com modelos por meio de endpoints de API compatíveis com o OpenAI
- Como enviar prompts para o servidor local com `vllm-prompt`

## Configurando a Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

> **Observação**: Se o VS Code não estiver instalado, você pode instalá-lo com o AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando Pré-requisitos de Software

O vLLM é executado em um contêiner pré-construído com o ROCm e suas dependências pré-combinadas. Nenhuma instalação adicional é necessária.

Não há etapa de instalação do vLLM no host. Inicie o vLLM com:

```bash
vllm-launch
```

O launcher inicia o contêiner, direciona para a GPU integrada e expõe um servidor vLLM local compatível com o OpenAI. Alternativamente, clique no ícone do vLLM na barra de tarefas.

## Início Rápido

### 1. Confirme que o Servidor vLLM Está em Execução

O `vllm-launch` pode levar alguns minutos para inicializar tudo. Assim que iniciar, o servidor estará disponível em `http://localhost:8001`. Mantenha o terminal de inicialização aberto, pois o servidor é executado em primeiro plano; então abra um terminal separado para as etapas restantes. Os exemplos abaixo usam `Qwen/Qwen3-1.7B`; se o seu launcher estiver configurado para um modelo diferente, substitua esse ID de modelo nas requisições.

### 2. Envie um Prompt

Use o script `vllm-prompt` fornecido para enviar uma requisição ao servidor local vLLM compatível com o OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Converse com o modelo usando a API Python do OpenAI

Como o vLLM expõe uma API compatível com o OpenAI, você pode usar o pacote Python `openai` para interagir com ela.

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

Em seguida, envie uma requisição de chat completion. Isso usa o mesmo formato de mensagem da API OpenAI — uma lista de mensagens com funções como `"user"` e `"assistant"`. Definir `stream=True` significa que a resposta chegará de forma incremental em vez de de uma só vez:

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

Por fim, itere sobre os blocos transmitidos e imprima cada trecho de texto conforme chega:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

O script incluído [chat_with_model.py](assets/chat_with_model.py) contém o exemplo completo e pode ser baixado.


## Escolhendo e Configurando um Modelo

Por padrão, `vllm-launch` serve `Qwen/Qwen3-1.7B` como modelo de teste na porta `8001`. Você pode alterar o modelo, a porta e os parâmetros de serviço do vLLM sem reconstruir ou editar o contêiner.

### Modelos testados pela AMD

Os seguintes modelos são pré-configurados e validados pela AMD:

| Modelo | Observações |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Modelo padrão. Leve e rápido para carregar. |
| `openai/gpt-oss-20b` | Modelo maior para respostas de qualidade superior. |

### Iniciando um modelo diferente

Informe o ID do modelo com `--model` (ou `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Alterando a porta

Informe uma porta acima de 1024 com `--port` (ou `-p`); o padrão é `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Se você alterar a porta, aponte o `base_url` do seu cliente para a mesma porta (por exemplo, `http://localhost:8080/v1`).

### Passando parâmetros extras do vLLM

Quaisquer argumentos adicionais são encaminhados diretamente ao vLLM, permitindo ajustar comportamentos de serviço, como o comprimento do contexto ou o tipo de dado. Há duas formas de fornecê-los.

**Inline**, após as opções do launcher:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**De forma persistente**, em um arquivo de configuração em `~/.local/share/vLLM/vllm-launch.conf`. Esse arquivo não existe por padrão — crie-o e adicione seus argumentos como um array Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Use `+=` para adicionar aos argumentos padrão em vez de substituí-los:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Para ver todas as opções do launcher a qualquer momento, execute:

```bash
vllm-launch --help
```

### Onde os modelos são armazenados

`vllm-launch` procura modelos em dois locais:

| Local | Caminho |
|----------|------|
| Modelos do sistema | `/var/cache/models` |
| Modelos do usuário | `~/.local/share/vLLM/models` |

Você pode colocar um modelo baixado em qualquer um dos diretórios e iniciá-lo informando seu caminho ou ID em `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Observação**: Espera-se que a execução do seu próprio modelo baixado dessa forma funcione assim que o modelo for colocado em um dos diretórios acima, mas esse fluxo de trabalho ainda não foi oficialmente validado pela AMD.

## Solução de Problemas

### Conexão recusada

Certifique-se de que o servidor está em execução:
```bash
curl http://localhost:8001/health
```

## Resumo

Neste playbook, você aprendeu a:

- Iniciar o vLLM em contêiner com suporte ROCm na GPU integrada
- Iniciar um servidor vLLM com endpoints de API compatíveis com o OpenAI na porta 8001
- Enviar prompts com `vllm-prompt`
- Fazer chamadas de API ao servidor vLLM usando requisições com e sem streaming
- Solucionar problemas comuns de inicialização do servidor, memória e conexões de cliente

Agora você tem uma implantação do vLLM em contêiner para servir modelos de linguagem grandes com desempenho otimizado na GPU integrada.

## Próximos Passos

- **Experimente modelos diferentes** — Use `vllm-launch --model <model>` para experimentar diferentes LLMs e comparar o desempenho (veja [Escolhendo e Configurando um Modelo](#choosing-and-configuring-a-model)).
- **Construa uma aplicação** — Use a API compatível com o OpenAI para integrar o vLLM a um aplicativo Python, chatbot ou fluxo de trabalho de automação.
- **Ajuste fino e sirva** — Faça o ajuste fino de um modelo usando LoRA ou QLoRA e depois implante-o com o vLLM para inferência otimizada.
## Recursos Adicionais

- **[Documentação Oficial do vLLM](https://docs.vllm.ai/)** — Guias abrangentes e referências de API
- **[Repositório GitHub do vLLM](https://github.com/vllm-project/vllm)** — Código-fonte, problemas e discussões da comunidade