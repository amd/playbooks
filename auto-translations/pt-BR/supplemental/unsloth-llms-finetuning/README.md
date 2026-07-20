<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para visualizar corretamente este conteúdo.
<!-- @github-only:end -->

## Visão Geral

Este playbook mostra como ajustar (fine-tune) um modelo de linguagem localmente com Unsloth em hardware AMD.

Ele usa um exemplo curto de Ajuste Fino Supervisionado (SFT) com adaptadores LoRA em `unsloth/gemma-4-E4B-it`, usando um subconjunto do dataset `mlabonne/FineTome-100k`. O objetivo é fornecer um fluxo de trabalho simples de ponta a ponta que abrange configuração, treinamento, inferência e salvamento do resultado ajustado.

O exemplo foi projetado para ser prático e fácil de modificar, para que você possa usá-lo como ponto de partida para seus próprios datasets e modelos.

## O Que Você Vai Aprender

- Como configurar o ambiente Unsloth
- Como ajustar um LLM usando SFT com Unsloth
- Como salvar o resultado ajustado no armazenamento local

<!-- @device:halo,stx,krk -->
> **Nota:** As técnicas de ajuste fino neste playbook exigem pelo menos 24 GB de memória de GPU e 32 GB de RAM do sistema.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** As técnicas de ajuste fino neste playbook exigem pelo menos 24 GB de memória de GPU e 32 GB de RAM do sistema.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** As técnicas de ajuste fino neste playbook exigem pelo menos 24 GB de memória de GPU **dedicada** e 32 GB de RAM do sistema.
<!-- @os:end -->
<!-- @device:end -->

## Por Que Unsloth?

O Unsloth facilita a execução do ajuste fino de LLMs em hardware local, reduzindo o uso de memória e acelerando o treinamento em comparação com uma configuração padrão.

Neste playbook, usamos o Unsloth junto com **SFT baseado em LoRA**. Isso significa que o modelo base permanece congelado na maior parte, enquanto um conjunto muito menor de pesos de adaptadores é treinado. Isso é adequado para desenvolvimento local porque é mais leve do que o ajuste fino completo e mais rápido para iterar.

O Unsloth também oferece suporte a outras abordagens de treinamento, incluindo QLoRA e fluxos de trabalho de aprendizado por reforço. Este playbook foca primeiro no caminho mais simples: um pequeno exemplo de ajuste fino LoRA que os usuários podem executar, entender e estender.

## Configurando a Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, você pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Abra um terminal e crie um venv com o software AMD ROCm™ e o PyTorch já instalados:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu usuário acesso aos dispositivos de GPU** (faça logout e login novamente para que isso tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

Abra um terminal e crie um venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** O Python 3.13 é necessário para Windows.

<!-- @device:halo_box -->
Abra um terminal do PowerShell e crie um ambiente virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Abra um terminal do PowerShell e crie um ambiente virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalando Dependências Básicas
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Dependências Adicionais

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Durante a importação, o Unsloth pode sondar caminhos opcionais de aceleração do `bitsandbytes`. Em algumas versões do ROCm, você pode ver uma mensagem como `bitsandbytes library load error: Configured ROCm binary not found`. Este playbook usa o ajuste fino LoRA padrão com `optim="adamw_torch"`, portanto, não dependemos do otimizador `bitsandbytes` nem do QLoRA de 4 bits. Essa mensagem pode ser ignorada com segurança.

<!-- @os:windows -->
> **Nota:** No ROCm para Windows, o Unsloth exibirá vários avisos na inicialização — veja [Avisos Conhecidos](#known-warnings) abaixo. Todos podem ser ignorados com segurança; o treinamento funciona corretamente.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Baixe o Script de Ajuste Fino do Unsloth

Em vez de executar manualmente cada etapa, este playbook fornece um script limpo e de ponta a ponta aqui: [test_unsloth.py](assets/test_unsloth.py).

Execute o código a seguir para rodar o script:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

O restante do playbook irá percorrer conceitualmente cada etapa principal do script. 

## Como Funciona

O script test_unsloth.py executa as seguintes etapas:
* **Carregar Modelo**: Carrega unsloth/gemma-4-E4B-it usando FastModel.
* **Preparar Dados**: Padroniza o dataset (por exemplo, FineTome-100k) e aplica o template de chat do Gemma-4.
* **Aplicar LoRA**: Adiciona adaptadores aos módulos de linguagem, atenção e MLP para treinamento eficiente.
* **Treinar**: Usa o SFTTrainer com mascaramento de perda apenas na resposta.
* **Inferência**: Executa um teste rápido de geração para verificar o desempenho.
* **Salvar**: Exporta os adaptadores LoRA localmente.

## Configuração Principal

Você pode modificar as seguintes constantes para personalizar sua execução:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemplo da mensagem de boas-vindas do Unsloth e saída ao carregar os pesos do modelo:

![texto alternativo](assets/welcome.png)

## Preparar o Dataset

Usamos um subconjunto de:
```text
mlabonne/FineTome-100k
```
O dataset é: 
* Convertido para o formato de chat
* Processado usando o template de chat do Gemma-4
* Limpo para remover tokens BOS duplicados

## Treinar o Modelo

O script executa uma pequena demonstração de treinamento, com os seguintes parâmetros:
- ~50 etapas
- Tamanho de lote pequeno
- Acumulação de gradiente

Durante o treinamento, você verá logs como:

![texto alternativo](assets/training.png)


## Salvamento e Implantação

### Salvamento Local (LoRA)

O script salva automaticamente os adaptadores LoRA no OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Salvar modelo mesclado (para vLLM) 

<!-- @os:windows -->
> **Nota:** O vLLM não é compatível com Windows. Para implantar seu modelo ajustado no Windows, use o llama.cpp (veja [Exportar GGUF](#export-gguf-for-llamacpp) abaixo) ou transfira o modelo mesclado para uma máquina Linux executando vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Para implantação com vLLM, mescle os adaptadores em um modelo completo:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Exportar GGUF (para llama.cpp)

Converta diretamente para GGUF para inferência local:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avisos Conhecidos

Estes avisos são exibidos pelo Unsloth na inicialização no Windows ROCm e todos podem ser ignorados com segurança:

| Aviso | Motivo | Seguro ignorar? |
|---|---|---|
| `bitsandbytes library load error` | O bitsandbytes não possui build para Windows ROCm | Sim — este playbook usa `adamw_torch`, não bnb |
| `No ROCm platform found for torch.distributed` | O ROCm no Windows não oferece suporte a treinamento distribuído | Sim — o treinamento em GPU única não é afetado |
| `Unsloth: WARNING! You are using an unsupported platform` | O Unsloth sinaliza builds que não são Linux | Sim — o Windows ROCm funciona para SFT em GPU única |
| `triton is not available` | O Triton não possui build para Windows | Sim — o Unsloth recorre aos kernels do PyTorch |

O treinamento prosseguirá corretamente apesar desses avisos.
<!-- @os:end -->

## Próximos Passos
- Experimente o [Unsloth Studio](https://unsloth.ai/docs/new/studio), uma GUI intuitiva para o Unsloth
- Treine com seus próprios conjuntos de dados específicos
- Experimente o ajuste fino com diferentes hiperparâmetros
- Implante com vLLM ou llama.cpp
- Experimente o QLoRA para uma configuração com menor uso de memória

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre o Unsloth e o ajuste fino:

* [Documentação do Unsloth](https://docs.unsloth.ai)

* [Unsloth no GitHub](https://github.com/unslothai/unsloth)

* [Guia de Ajuste Fino do Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)