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


Quer executar modelos de linguagem de IA avançados no seu próprio hardware? Este guia mostra-lhe como.
Este tutorial utiliza o PyTorch com tecnologia AMD ROCm™ para executar modelos que podem resumir documentos, responder a perguntas, gerar texto e muito mais, tudo localmente.

## O que vai aprender

- Executar LLMs como o gpt-oss-20b e o qwen3.5-4B localmente utilizando PyTorch e ROCm
- Criar uma ferramenta de resumo de documentos utilizando LLMs

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo através do Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalação dos Pré-requisitos de Software

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
No Linux, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv com ROCm+Pytorch já instalados.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine a sessão e volte a iniciá-la para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

No Linux, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv com ROCm+Pytorch já instalados.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Dica**: Os utilizadores do Windows podem precisar de modificar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @os:end -->

### Instalação das Dependências Básicas
<!-- @require:driver,pytorch -->

### Instalação de Dependências Adicionais

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Início Rápido com Scripts de Exemplo

Este manual inclui scripts prontos a utilizar. Clique neles para pré-visualizar e transferir para o mesmo diretório do ambiente que criou.

| Script | Descrição | Utilização |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Geração de texto básica com LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Resumidor de documentos com suporte para Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Ambos os scripts suportam:
- Seleção de modelo através da flag `--model`
- Formatação de modelo de chat para uma indução (prompting) adequada do modelo, especialmente útil para o resumo de documentos

## Carregar e Executar o Seu Primeiro LLM

O script incluído [run_llm.py](assets/run_llm.py) mostra como gerar texto com LLMs utilizando PyTorch e AMD ROCm.

> **Nota:** Quando carrega um modelo, o Hugging Face Transformers verifica primeiro a sua cache local (`~/.cache/huggingface/hub` no Linux, `C:\Users\<user>\.cache\huggingface\hub` no Windows). Se o modelo não estiver em cache, é transferido automaticamente a partir de huggingface.co. A primeira execução pode demorar alguns minutos, dependendo do tamanho do modelo e da velocidade da rede.

O excerto abaixo mostra como utilizar o modelo e personalizar as perguntas feitas.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Experimente o script transferido:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Criar um Resumidor de Documentos

Agora que já gerou resultados de um LLM local, pode continuar a partir daí criando um resumidor de documentos prático. Nesta secção, vai utilizar o script [summarizer.py](assets/summarizer.py) para introduzir um ficheiro .txt e gerar automaticamente um resumo conciso, tudo a ser executado localmente na sua GPU.

O script foi concebido para funcionar de imediato. Abra o script num editor para explorar o código, personalizar prompts e ajustar parâmetros como o comprimento e a temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Exemplos de Utilização

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Saiba mais sobre os Parâmetros de Geração

| Parâmetro | O que controla | Valores típicos |
|-----------|------------------|----------------|
| `max_new_tokens` | O comprimento máximo do resultado do LLM | Utilize 50–500 tokens para resumos. (1 token equivale a cerca de 0,75 palavras em inglês) |
| `temperature` | Criatividade. Valores baixos tornam-no focado, enquanto valores altos trazem mais imprevisibilidade | - **0,1–0,3**: Focado, determinístico (bom para resumos) <br> **0,5–0,7**: Equilibrado (utilização geral) <br> **0,8–1,0**: Criativo, variado (brainstorming) |
| `top_p` | Nucleus Sampling - Valores baixos limitam o modelo a resultados mais restritos | **0,1-0,5**: Estrito, previsível <br> **0,9-0,95**: (padrão, natural, conversacional) |


## Aplicações no Mundo Real

- **Análise de Artigos de Investigação**: Extraia conclusões-chave de publicações complexas para uma revisão rápida
- **Agregação de Notícias**: Resuma artigos de notícias em resumos diários breves ou destaques
- **Notas de Reuniões**: Condense transcrições em itens de ação e resumos concisos
- **Revisão de Documentos Jurídicos**: Extraia rapidamente cláusulas ou obrigações relevantes de textos jurídicos longos
- **Documentação de Código**: Gere resumos concisos de repositórios e explicações de funções

## Próximos Passos

- **Ajuste Fino (Fine-tuning)**: Adapte modelos ao seu campo ou terminologia específicos para maior precisão (consulte os Manuais de Ajuste Fino)
- **Sistemas RAG**: Combine LLMs com recuperação de documentos para respostas e pesquisas sensíveis ao contexto
- **Exploração de Modelos**: Experimente novos modelos como o Llama 3, Phi-3 ou Qwen para obter melhores resultados
- **Implementação em Produção**: Utilize ferramentas como o vLLM para servir LLMs de forma escalável em organizações

O seu sistema dá-lhe o poder de executar modelos de linguagem sofisticados localmente. Experimente diferentes modelos, prompts e parâmetros para descobrir o que funciona melhor para as suas aplicações.