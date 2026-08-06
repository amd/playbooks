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

Este tutorial fornece exemplos passo a passo para fazer o fine-tuning de um modelo de linguagem grande (LLM) com PyTorch e ROCm. Ele aborda várias técnicas, desde o fine-tuning padrão até estratégias de Parameter-Efficient Fine-Tuning (PEFT) eficientes em memória, para que você possa adaptar facilmente os modelos às suas necessidades.

**Modelo Utilizado**: google/gemma-3-4b-it  *(consulte [Habilitar autenticação HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) se protegido por gating)*  
**Hardware**: GPU AMD Radeon™ com suporte a ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Observação:** 
> - O fine-tuning completo requer pelo menos **64 GB de RAM do sistema**, com pelo menos **32 GB disponíveis para a GPU** (os 32 GB fazem parte dos 64 GB, e não são adicionais a eles).
> - Você também pode experimentar outras arquiteturas de modelo, incluindo o **GPT-OSS-20B**, substituindo o modelo nos scripts de treinamento fornecidos.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Observação:** O fine-tuning com LoRA e QLoRA requer pelo menos **32 GB de RAM do sistema**, com pelo menos **16 GB disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, e não são adicionais a eles).
<!-- @os:end -->

<!-- @os:windows -->
> **Observação:** O fine-tuning com LoRA requer pelo menos **32 GB de RAM do sistema**, com pelo menos **16 GB disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, e não são adicionais a eles).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Observação:** O fine-tuning com LoRA e QLoRA requer uma placa gráfica com pelo menos **16 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treinamento é executado inteiramente na VRAM dedicada da placa gráfica.
> - Ele não recorre à memória de GPU compartilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 16 GB de VRAM dedicada ficarão sem memória durante o treinamento no Linux, mesmo que o sistema tenha bastante RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação:** O fine-tuning com LoRA requer pelo menos **16 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total de GPU combina a VRAM dedicada da placa gráfica com a memória de GPU compartilhada (emprestada da RAM do sistema).
> - Portanto, placas com menos de 16 GB de VRAM dedicada ainda podem executar este playbook usando memória de GPU compartilhada para compensar a diferença.
<!-- @os:end -->
<!-- @device:end -->

## O Que Você Vai Aprender

- Como fazer fine-tuning de um LLM usando LoRA, QLoRA e fine-tuning completo com PyTorch e ROCm
- Como salvar e implantar seu modelo com fine-tuning aplicado
- Como monitorar o treinamento e depurar problemas comuns

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Observação**: Se o VS Code não estiver instalado, você pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

#### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu usuário acesso aos dispositivos de GPU** (saia e entre novamente na sessão para que isso tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Instalando Dependências Básicas
<!-- @require:pytorch -->

#### Dependências Adicionais

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Somente os pacotes principais são testados e suportados aqui. **O bitsandbytes não é bem suportado no Windows**, portanto a instalação no Windows o omite; use LoRA ou fine-tuning completo no Windows (o QLoRA requer bitsandbytes e é destinado ao Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Habilitar autenticação HF (modelos protegidos por gating ou personalizados / não pré-instalados)

Neste exemplo, usamos o **google/gemma-3-4b-it**, que é um modelo **protegido por gating**. Você deve aceitar os termos do modelo no Hugging Face e, em seguida, autenticar-se para que os scripts de treinamento possam baixá-lo.

1. **Aceite a licença:** Abra [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), faça login (ou crie uma conta) e aceite a licença/termos na página do modelo (por exemplo, "Agree and access repository").
2. **Instale e faça login:** Instale o Hugging Face CLI e, em seguida, execute o login padrão:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Entendendo as Técnicas

### O Que É LoRA?

**LoRA (Low-Rank Adaptation)** mantém o modelo base congelado e treina apenas pequenas matrizes "adaptadoras" que são adicionadas a determinadas camadas. 

- **A ideia principal**: em vez de atualizar uma enorme matriz de pesos com milhões de parâmetros, aprendemos uma atualização de baixo posto (duas matrizes pequenas cujo produto tem muito menos parâmetros). Isso proporciona uma grande redução nos parâmetros treináveis e na VRAM, mantendo a maior parte da qualidade do fine-tuning completo.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### O Que É QLoRA?

**QLoRA** combina **quantização de 4 bits** com **LoRA**. O modelo base é carregado em 4 bits (grande economia de memória), e apenas os adaptadores LoRA são treinados em precisão mais alta. Assim, você obtém a eficiência de parâmetros do LoRA além de uma VRAM muito menor, com uma pequena perda de qualidade em comparação com o LoRA de precisão total. Observe que a quantização de 4 bits pode causar instabilidades numéricas (picos de perda ou NaNs), então os usuários podem frequentemente preferir o **LoRA** se houver VRAM suficiente disponível.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Observação**: Para modelos base MXFP4 como o `openai/gpt-oss-20b`, recomendamos usar **LoRA** (`train_lora.py`) em vez de QLoRA. O caminho de 4 bits do `bitsandbytes` no script QLoRA normalmente desquantiza os pesos MXFP4 para BF16, de forma que a execução se comporta como um LoRA padrão. O MXFP4 nativo requer o `bitsandbytes` compilado a partir do código-fonte, além de uma pilha compatível de Transformers/Triton/kernels. Consulte a [documentação MXFP4 do Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Escolha Seu Método

| Método | Memória | Velocidade | Qualidade | Melhor Para |
|--------|--------|-------|---------|----------|
| **QLoRA** (somente Linux) | 12-16GB | Mais rápido | 90-95% | Baixo Uso de Memória |
| **LoRA** | 24-32GB | Rápido | 95-98% | Abordagem equilibrada |
| **Full** | 80GB+ | Mais lento | 100% | Qualidade máxima |

### 3. Execute o Treinamento

**Dataset e o que o modelo aprende**  
Os scripts transformam o dataset em exemplos de chat. Por exemplo, o script QLoRA usa **Abirate/english_quotes**: cada exemplo se torna um par usuário-assistente como:

- **Usuário:** "Me dê uma citação sobre: &lt;tag&gt;"
- **Assistente:** "&lt;citação&gt; – &lt;autor&gt;"

O fine-tuning ensina o modelo a responder a prompts que pedem citações sobre um tópico e a retorná-las no formato `<quote text> - <author>`. Os scripts de LoRA e fine-tuning completo usam **databricks/databricks-dolly-15k** (pares gerais de instrução/resposta), então a tarefa exata varia de acordo com o script; a ideia é a mesma - adaptar o modelo ao dataset e formato escolhidos.

Abaixo está um resumo dos métodos de treinamento disponíveis. Cada método é vinculado ao seu script e fornece uma breve descrição para ajudar a escolher a abordagem certa.

| Script                           | Método            | Descrição                                                                                                         | VRAM Típica | Recomendado Para                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Treina pequenas matrizes adaptadoras congelando o modelo base. 3–5x mais rápido; ~95–98% da qualidade total.                         | 24–32GB      | Usuários avançados; múltiplos adaptadores; mais VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(somente Linux)*             | **QLoRA**       | Quantização de 4 bits + adaptadores LoRA. Menor uso de memória, mais rápido, pequena perda de qualidade. Requer `bitsandbytes` (somente Linux).                            | 12–16GB      | Maioria dos usuários; experimentos rápidos; VRAM limitada      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Fine-tuning Completo** | Atualiza todos os parâmetros do modelo. Qualidade máxima; maior uso de memória e computação.                                    | 40GB+        | Qualidade máxima; pesquisa; VRAM grande           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Observação:** O fine-tuning completo (`train_full_finetuning.py`) pode exigir mais de 64GB de RAM do sistema e pode não ser viável neste dispositivo. Considere usar LoRA ou QLoRA em vez disso.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação:** O fine-tuning completo (`train_full_finetuning.py`) pode exigir mais de 64GB de RAM do sistema e pode não ser viável neste dispositivo. Considere usar LoRA em vez disso.
<!-- @os:end -->
<!-- @device:end -->

Basta selecionar o `Training method` de sua preferência, baixar o script correspondente e executá-lo usando o comando mantendo seu ambiente virtual ativado: 

```python
python3 train_<method_name>.py.
```

## Usando Seu Modelo com Fine-Tuning

### Após o Fine-Tuning Completo

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Após o Treinamento LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Mesclar Adaptador LoRA no Modelo Base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Observação:**  
- Certifique-se de que o nome do diretório do modelo (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) corresponde à sua pasta de saída real do treinamento.  
- Se você usou LoRA em vez de QLoRA, basta substituir o caminho de acordo.  
- Alguns modelos Gemma exigem a especificação de `trust_remote_code=True` em `from_pretrained`; adicione se você ver um aviso relacionado.

Para configurações mais personalizadas (tokens de preenchimento, dispositivo, etc.), consulte o script que você usou para o treinamento.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guia de Personalização

### Use Seu Próprio Dataset

Todos os scripts usam o mesmo formato de dataset. Substitua a seção de carregamento:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Formato de Dataset para arquivo JSON/JSONL local:**

Ao usar este método, certifique-se de que seus arquivos JSON estejam estruturados corretamente para evitar erros de análise. 

As seguintes diretrizes devem ser seguidas:
* **Formatação de Arquivo:** Os arquivos JSON devem ser formatados dentro de um Ambiente de Desenvolvimento Integrado (IDE) para garantir estrutura e sintaxe adequadas.
* **Chaves Obrigatórias:** O arquivo JSON personalizado deve conter as chaves `instruction` e `response`. Essas chaves são essenciais para que o método funcione corretamente.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Formato de Dataset para dataset do Hugging Face Hub**

Ao utilizar datasets do Hugging Face, certifique-se de que seus datasets estejam estruturados corretamente para facilitar uma integração perfeita. 

As seguintes diretrizes devem ser seguidas:
* **Par Instrução-Resposta:** Concentre-se em datasets que incluam um par `instruction-response`. Essa estrutura é essencial para a funcionalidade pretendida.
* **Modificação de Chave Personalizada:** Se o seu dataset não estiver em conformidade com a estrutura `instruction-response`, você tem a opção de modificar a função `format_instruction()`. Isso permite que você acomode chaves específicas conforme necessário.

Exemplo de Ajuste: Em casos onde a saída do dataset precisa ser ajustada, você pode modificar a seção de resposta dentro da função format_instruction() para atender às suas necessidades.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formato de Dataset para arquivo CSV**

Para adaptar o script ao uso de um formato de arquivo CSV, você precisa garantir que o arquivo CSV contenha colunas chamadas `instruction` e `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Ajuste os Parâmetros de Treinamento

Edite o script de treinamento e altere as variáveis para corresponder aos seus objetivos: **taxa de aprendizado** (`LR`), **épocas** (`EPOCHS`), **tamanho do lote** (`BATCH_SIZE`), **acúmulo de gradiente** (`GRAD_ACCUM_STEPS`) e, para LoRA/QLoRA, **rank** (`LORA_R`). Para execuções mais rápidas, use menos épocas e uma taxa de aprendizado (LR) mais alta; para melhor qualidade, use mais épocas e uma LR mais baixa. Reduza o tamanho do lote ou o comprimento da sequência se você encontrar erros de falta de memória.
### Dicas de Otimização de Memória

Se você encontrar erros de falta de memória:

**1. Reduza o Tamanho do Lote:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reduza o Comprimento da Sequência:**
```python
max_seq_length=256  # Instead of 512
```

**3. Use uma Quantização Mais Agressiva:**
```
Full → LoRA → QLoRA
```

**4. Habilite o Gradient Checkpointing (apenas para fine-tuning completo):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoramento e Depuração

### Observe a Memória da GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcional) Acompanhe Experimentos com Weights & Biases

Para registrar execuções e métricas no [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

No script de treinamento, defina `report_to="wandb"` e, opcionalmente, `run_name="your-experiment-name"` na configuração do trainer. Se preferir não usar o Wandb, deixe `report_to` no valor padrão ou defina-o como `"none"`.

### Problemas Comuns

#### Falta de Memória (OOM)

**Solução:** Reduza o tamanho do lote e/ou use QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### A Perda Não Diminui

**Solução:** Ajuste a taxa de aprendizado
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Treinamento Lento

**Solução:** Aumente o tamanho do lote se a memória permitir
```python
BATCH_SIZE = 8
```
## Próximos Passos

Depois de concluir o fine-tuning com sucesso, considere os seguintes próximos passos para aproveitar ainda mais o seu modelo:

1. **Avalie** minuciosamente em dados de teste separados para medir a generalização e evitar overfitting.
2. **Experimente** testando diferentes valores de hiperparâmetros para obter melhores trade-offs de precisão, velocidade e memória.
3. **Acompanhe** todos os seus experimentos (e as métricas correspondentes) com o Weights & Biases para pesquisas reproduzíveis.
4. **Tente** treinar com seus próprios conjuntos de dados personalizados para adaptar o modelo especificamente ao seu caso de uso.
5. **Implante** seu modelo com fine-tuning para inferência rápida usando backends eficientes como o vLLM em hardware compatível.
6. **Explore** técnicas avançadas, incluindo engenharia de prompts, precisão mista e comprimentos de sequência maiores.
7. **Treine** múltiplos adaptadores LoRA para diferentes tarefas ou domínios e troque-os conforme necessário.

---