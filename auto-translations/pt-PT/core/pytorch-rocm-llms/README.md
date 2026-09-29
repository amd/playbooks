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


Quer executar modelos de linguagem de IA avançados no seu próprio hardware? Este guia mostra-lhe como fazê-lo.
Este tutorial utiliza o PyTorch, com tecnologia AMD ROCm™, para executar modelos que podem resumir documentos, responder a perguntas, gerar texto e muito mais, tudo localmente.

## O Que Vai Aprender

- Executar LLMs como o gpt-oss-20b e o qwen3.5-4B localmente utilizando PyTorch e ROCm
- Criar uma ferramenta de resumo de documentos utilizando LLMs

<!-- @device:halo_box,halo,stx,krk -->
## Definir a Configuração de Memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo através do Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
No Linux, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv com ROCm+Pytorch já instalado.
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
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine e volte a iniciar a sessão para que isto tenha efeito):

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
No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv com ROCm+Pytorch já instalado.
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

> **Dica**: Os utilizadores do Windows podem ter de alterar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.

<!-- @os:end -->

### Instalar Dependências Básicas
<!-- @require:driver,pytorch -->

### Instalar Dependências Adicionais

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Se o modelo não carregar ou ficar sem memória, tente instalar o pacote `kernels` para carregar o modelo com quantização otimizada.
>
> ```bash
> # Utilize esta versão, que é compatível com a versão do Transformers
> pip install "kernels==0.14.1" 
> ```
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
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Início Rápido com Scripts de Exemplo

Este manual inclui scripts prontos a utilizar. Clique neles para pré-visualizar e transferir para o mesmo diretório do ambiente que criou.

| Script | Descrição | Utilização |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Geração básica de texto com LLM | `python run_llm.py` |
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
- Formatação de modelo de chat para uma correta indicação de instruções ao modelo, especialmente útil para o resumo de documentos

## Carregar e Executar o Seu Primeiro LLM

O script incluído [run_llm.py](assets/run_llm.py) mostra como gerar texto com LLMs utilizando PyTorch e AMD ROCm.

> **Nota:** Quando carrega um modelo, o Hugging Face Transformers verifica primeiro a sua cache local (`~/.cache/huggingface/hub` no Linux, `C:\Users\<user>\.cache\huggingface\hub` no Windows). Se o modelo não estiver em cache, é descarregado automaticamente a partir de huggingface.co. A primeira execução pode demorar alguns minutos, dependendo do tamanho do modelo e da velocidade da rede.

O excerto abaixo mostra como utilizar o modelo e personalizar as perguntas colocadas.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
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
    device_map="auto",
    disable_mmap=True
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

Agora que já gerou resultados com um LLM local, pode aproveitar isso para criar um resumidor de documentos prático. Nesta secção, irá utilizar o script [summarizer.py](assets/summarizer.py) para carregar um ficheiro .txt e gerar automaticamente um resumo conciso, tudo em execução local na sua GPU.

O script foi concebido para funcionar de imediato. Abra o script num editor para explorar o código, personalizar os prompts e ajustar parâmetros como o comprimento e a temperatura.

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

## Conhecer os Parâmetros de Geração

| Parâmetro | O Que Controla | Valores Típicos |
|-----------|------------------|----------------|
| `max_new_tokens` | O comprimento máximo do resultado do LLM | Utilize 50–500 tokens para resumos. (1 token equivale a cerca de 0,75 palavras em inglês) |
| `temperature` | Criatividade. Valores baixos tornam-no mais focado, enquanto valores altos trazem mais imprevisibilidade | - **0,1–0,3**: Focado, determinístico (bom para resumos) <br> **0,5–0,7**: Equilibrado (uso geral) <br> **0,8–1,0**: Criativo, variado (brainstorming) |
| `top_p` | Amostragem por Núcleo (Nucleus Sampling) - Valores baixos limitam o modelo a resultados mais restritos | **0,1-0,5**: Estrito, previsível <br> **0,9-0,95**: (padrão, natural, conversacional) |


## Aplicações no Mundo Real

- **Análise de Artigos Científicos**: Extrair conclusões-chave de publicações complexas para revisão rápida
- **Agregação de Notícias**: Resumir artigos de notícias em resumos diários ou destaques breves
- **Notas de Reuniões**: Condensar transcrições em itens de ação e resumos concisos
- **Revisão de Documentos Jurídicos**: Extrair rapidamente cláusulas ou obrigações relevantes de textos jurídicos extensos
- **Documentação de Código**: Gerar descrições concisas de repositórios e explicações de funções
## Próximos passos

- **Fine-tuning**: Adapte modelos ao seu domínio específico ou jargão para obter melhor precisão (consulte os Manuais de Fine-tuning)
- **Sistemas RAG**: Combine LLMs com recuperação de documentos para respostas e pesquisas sensíveis ao contexto
- **Exploração de modelos**: Experimente novos modelos como Llama 3, Phi-3 ou Qwen para obter melhores resultados
- **Implementação em produção**: Utilize ferramentas como vLLM para disponibilizar LLMs de forma escalável em organizações

O seu sistema dá-lhe o poder de executar modelos de linguagem sofisticados localmente. Experimente diferentes modelos, prompts e parâmetros para descobrir o que funciona melhor para as suas aplicações.