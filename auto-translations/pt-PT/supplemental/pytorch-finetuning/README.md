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

Este tutorial fornece exemplos passo a passo para o ajuste fino (fine-tuning) de um modelo de linguagem de grande dimensão (LLM) com PyTorch e ROCm. Abrange várias técnicas, desde o ajuste fino padrão até estratégias de ajuste fino eficiente em parâmetros (Parameter-Efficient Fine-Tuning, PEFT), com uso eficiente de memória, para que possa adaptar facilmente os modelos às suas necessidades.

**Modelo Utilizado**: google/gemma-3-4b-it (script QLoRA: openai/gpt-oss-20b)  *(ver [Ativar a autenticação HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) se for um modelo restrito)*  
**Hardware**: GPU AMD Radeon™ com suporte ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Nota:** 
> - O ajuste fino completo requer, no mínimo, **64 GB de RAM do sistema**, com pelo menos **32 GB disponíveis para a GPU** (os 32 GB fazem parte dos 64 GB, não são adicionais a estes).
> - Também pode experimentar outras arquiteturas de modelos, incluindo o **GPT-OSS-20B**, substituindo o modelo nos scripts de treino fornecidos.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Nota:** O ajuste fino com LoRA e QLoRA requer, no mínimo, **32 GB de RAM do sistema**, com pelo menos **16 GB disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, não são adicionais a estes).
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** O ajuste fino com LoRA requer, no mínimo, **32 GB de RAM do sistema**, com pelo menos **16 GB disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, não são adicionais a estes).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** O ajuste fino com LoRA e QLoRA requer uma placa gráfica com, pelo menos, **16 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treino é executado inteiramente na VRAM dedicada da placa gráfica.
> - Não recorre à memória de GPU partilhada (RAM do sistema) quando a VRAM se esgota.
> - As placas com menos de 16 GB de VRAM dedicada ficarão sem memória durante o treino no Linux, mesmo que o sistema tenha bastante RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** O ajuste fino com LoRA requer, no mínimo, **16 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total da GPU combina a VRAM dedicada da placa gráfica com a memória de GPU partilhada (retirada da RAM do sistema).
> - Assim, as placas com menos de 16 GB de VRAM dedicada ainda conseguem executar este manual de procedimentos, utilizando memória de GPU partilhada para compensar a diferença.
<!-- @os:end -->
<!-- @device:end -->

## O Que Vai Aprender

- Como ajustar um LLM utilizando LoRA, QLoRA e ajuste fino completo com PyTorch e ROCm
- Como guardar e implementar o seu modelo ajustado
- Como monitorizar o treino e depurar problemas comuns

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

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

#### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
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
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine sessão e volte a iniciá-la para que esta alteração tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
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
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Instalar as Dependências Básicas
<!-- @require:pytorch -->

#### Dependências Adicionais

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Aqui, apenas os pacotes principais foram testados e são suportados. **O bitsandbytes não é bem suportado no Windows**, pelo que a instalação no Windows o omite; utilize LoRA ou ajuste fino completo no Windows (o QLoRA requer o bitsandbytes e destina-se ao Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Ativar a autenticação HF (modelos restritos, personalizados ou não pré-instalados)

Neste exemplo, utilizamos o **google/gemma-3-4b-it**, que é um modelo **restrito** (gated). Tem de aceitar os termos do modelo no Hugging Face e, em seguida, autenticar-se para que os scripts de treino o possam transferir.

1. **Aceitar a licença:** Abra [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), inicie sessão (ou crie uma conta) e aceite a licença/termos na página do modelo (por exemplo, “Agree and access repository”).
2. **Instalar e iniciar sessão:** Instale a CLI do Hugging Face e execute depois o início de sessão padrão:

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

## Compreender as Técnicas

### O Que é o LoRA?

O **LoRA (Low-Rank Adaptation)** mantém o modelo base congelado e apenas treina pequenas matrizes "adaptadoras" que são adicionadas a determinadas camadas. 

- **A ideia principal**: em vez de atualizar uma matriz de pesos enorme com milhões de parâmetros, aprendemos uma atualização de baixa ordem (duas matrizes pequenas cujo produto tem muito menos parâmetros). Isto traduz-se numa grande redução dos parâmetros treináveis e da VRAM, mantendo a maior parte da qualidade do ajuste fino completo.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### O Que é o QLoRA?

O **QLoRA** combina a **quantização de 4 bits** com o **LoRA**. O modelo base é carregado em 4 bits (grande poupança de memória), e apenas os adaptadores LoRA são treinados com maior precisão. Assim, obtém a eficiência de parâmetros do LoRA, juntamente com uma VRAM muito mais reduzida, com uma pequena perda de qualidade em comparação com o LoRA de precisão total. Note que a quantização de 4 bits pode causar instabilidades numéricas (picos de perda ou NaNs), pelo que os utilizadores poderão preferir frequentemente o **LoRA** se houver VRAM suficiente disponível.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Nota**: Para modelos base MXFP4 como `openai/gpt-oss-20b`, recomendamos a utilização do **LoRA** (`train_lora.py`) em vez do QLoRA. O caminho de 4 bits do `bitsandbytes` utilizado no script QLoRA normalmente desquantiza os pesos MXFP4 para BF16, pelo que a execução se comporta como um LoRA padrão. O MXFP4 nativo requer que o `bitsandbytes` seja compilado a partir do código-fonte, juntamente com uma stack correspondente de Transformers/Triton/kernels. Consulte a [documentação MXFP4 do Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Escolha o seu Método

| Método | Memória | Velocidade | Qualidade | Mais Indicado Para |
|--------|--------|-------|---------|----------|
| **QLoRA** (apenas Linux) | 12-16GB | Mais rápido | 90-95% | Baixa Utilização de Memória |
| **LoRA** | 24-32GB | Rápido | 95-98% | Abordagem equilibrada |
| **Full** | 80GB+ | Mais lento | 100% | Qualidade máxima |

### 3. Executar o Treino

**Conjunto de dados e o que o modelo aprende**  
Os scripts transformam o conjunto de dados em exemplos de chat. Por exemplo, o script QLoRA utiliza **Abirate/english_quotes**: cada exemplo torna-se um par utilizador–assistente, como:

- **Utilizador:** “Dá-me uma citação sobre: &lt;tag&gt;”
- **Assistente:** “&lt;citação&gt; – &lt;autor&gt;”

O ajuste fino ensina o modelo a responder a pedidos de citações sobre um determinado tema e a devolvê-las no formato `<quote text> - <author>`. Os scripts de LoRA e de ajuste fino completo utilizam **databricks/databricks-dolly-15k** (pares genéricos de instrução/resposta), pelo que a tarefa exata varia consoante o script; a ideia é a mesma - adaptar o modelo ao conjunto de dados e formato escolhidos.

Segue-se um resumo dos métodos de treino disponíveis. Cada método inclui uma ligação para o respetivo script e uma breve descrição para ajudar a escolher a abordagem certa.

| Script                           | Método            | Descrição                                                                                                         | VRAM Típica | Recomendado Para                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Treina pequenas matrizes adaptadoras enquanto congela o modelo base. 3–5x mais rápido; ~95–98% da qualidade total.                         | 24–32GB      | Utilizadores avançados; múltiplos adaptadores; mais VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(apenas Linux)*             | **QLoRA**       | Quantização de 4 bits + adaptadores LoRA. Menor utilização de memória, mais rápido, ligeira perda de qualidade. Requer `bitsandbytes` (apenas Linux).                            | 12–16GB      | A maioria dos utilizadores; experiências rápidas; VRAM limitada      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Ajuste Fino Completo** | Atualiza todos os parâmetros do modelo. Qualidade máxima; maior utilização de memória e processamento.                                    | 40GB+        | Qualidade máxima; investigação; VRAM elevada           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** O ajuste fino completo (`train_full_finetuning.py`) pode exigir mais de 64GB de RAM do sistema e pode não ser viável neste dispositivo. Considere utilizar LoRA ou QLoRA em alternativa.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** O ajuste fino completo (`train_full_finetuning.py`) pode exigir mais de 64GB de RAM do sistema e pode não ser viável neste dispositivo. Considere utilizar LoRA em alternativa.
<!-- @os:end -->
<!-- @device:end -->

Basta selecionar o `Training method` pretendido, transferir o script correspondente e executá-lo através do comando, mantendo o seu ambiente virtual ativado: 

```python
python3 train_<method_name>.py.
```

## Utilizar o seu Modelo Ajustado

### Após o Ajuste Fino Completo

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

### Após o Treino com LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Fundir o Adaptador LoRA no Modelo Base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Nota:**  
- Certifique-se de que o nome do diretório do modelo (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) corresponde à sua pasta de saída real do treino.  
- Se tiver utilizado LoRA em vez de QLoRA, basta substituir o caminho em conformidade.  
- Alguns modelos Gemma exigem a especificação de `trust_remote_code=True` em `from_pretrained`; adicione-o se vir um aviso relacionado.

Para mais definições personalizadas (tokens de preenchimento, dispositivo, etc.), consulte o script que utilizou para o treino.

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
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guia de Personalização

### Utilizar o seu Próprio Conjunto de Dados

Todos os scripts utilizam o mesmo formato de conjunto de dados. Substitua a secção de carregamento:

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

**Formato do Conjunto de Dados para Ficheiro JSON/JSONL Local:**

Ao utilizar este método, certifique-se de que os seus ficheiros JSON estão corretamente estruturados para evitar erros de análise. 

Devem ser seguidas as seguintes diretrizes:
* **Formatação do Ficheiro:** Os ficheiros JSON devem ser formatados num Ambiente de Desenvolvimento Integrado (IDE) para garantir a estrutura e sintaxe corretas.
* **Chaves Obrigatórias:** O ficheiro JSON personalizado deve conter as chaves `instruction` e `response`. Estas chaves são essenciais para que o método funcione corretamente.
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
**Formato do Conjunto de Dados para Conjunto de Dados do Hugging Face Hub**

Ao utilizar conjuntos de dados do Hugging Face, certifique-se de que os seus conjuntos de dados estão corretamente estruturados para facilitar uma integração sem problemas. 

Devem ser seguidas as seguintes diretrizes:
* **Par Instrução-Resposta:** Centre-se em conjuntos de dados que incluam um par `instruction-response`. Esta estrutura é essencial para o funcionamento pretendido.
* **Modificação de Chaves Personalizadas:** Se o seu conjunto de dados não estiver em conformidade com a estrutura `instruction-response`, tem a opção de modificar a função `format_instruction()`. Isto permite-lhe adaptar chaves específicas conforme necessário.

Exemplo de Ajuste: Nos casos em que o resultado do conjunto de dados precise de ser ajustado, pode modificar a secção de resposta dentro da função format_instruction() para se adequar aos seus requisitos.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formato do Conjunto de Dados para Ficheiro CSV**

Para adaptar o script à utilização de um formato de ficheiro CSV, deve certificar-se de que o ficheiro CSV contém colunas denominadas `instruction` e `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Ajustar os Parâmetros de Treino

Edite o script de treino e altere as variáveis de acordo com os seus objetivos: **taxa de aprendizagem** (`LR`), **épocas** (`EPOCHS`), **tamanho do lote** (`BATCH_SIZE`), **acumulação de gradiente** (`GRAD_ACCUM_STEPS`) e, para LoRA/QLoRA, **rank** (`LORA_R`). Para execuções mais rápidas, utilize menos épocas e uma taxa de aprendizagem (LR) mais elevada; para melhor qualidade, utilize mais épocas e uma LR mais baixa. Reduza o tamanho do lote ou o comprimento da sequência se encontrar erros de falta de memória.
### Dicas de Otimização de Memória

Se encontrar erros de falta de memória:

**1. Reduzir o Tamanho do Lote:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reduzir o Comprimento da Sequência:**
```python
max_seq_length=256  # Instead of 512
```

**3. Utilizar uma Quantização Mais Agressiva:**
```
Full → LoRA → QLoRA
```

**4. Ativar o Gradient Checkpointing (apenas para ajuste fino completo):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorização e Depuração

### Observar a Memória da GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcional) Acompanhar Experiências com Weights & Biases

Para registar execuções e métricas no [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

No script de treino, defina `report_to="wandb"` e, opcionalmente, `run_name="your-experiment-name"` na configuração do trainer. Se preferir não utilizar o Wandb, deixe `report_to` com o valor predefinido ou defina-o como `"none"`.

### Problemas Comuns

#### Falta de Memória (OOM)

**Solução:** Reduza o tamanho do lote e/ou utilize QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### A Perda Não Diminui

**Solução:** Ajuste a taxa de aprendizagem
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Treino Lento

**Solução:** Aumente o tamanho do lote se a memória permitir
```python
BATCH_SIZE = 8
```
## Próximos Passos

Depois de concluir com sucesso o ajuste fino, considere os seguintes próximos passos para tirar mais partido do seu modelo:

1. **Avalie** minuciosamente em dados de teste reservados para medir a generalização e evitar o overfitting.
2. **Experimente** testando diferentes valores de hiperparâmetros para obter melhores compromissos entre precisão, velocidade e memória.
3. **Acompanhe** todas as suas experiências (e as métricas correspondentes) com o Weights & Biases para uma investigação reproduzível.
4. **Experimente** treinar com os seus próprios conjuntos de dados personalizados para adaptar o modelo especificamente ao seu caso de uso.
5. **Implemente** o seu modelo ajustado para inferência rápida utilizando back-ends eficientes como o vLLM em hardware compatível.
6. **Explore** técnicas avançadas, incluindo engenharia de prompts, precisão mista e comprimentos de sequência mais longos.
7. **Treine** múltiplos adaptadores LoRA para diferentes tarefas ou domínios e troque-os conforme necessário.

---