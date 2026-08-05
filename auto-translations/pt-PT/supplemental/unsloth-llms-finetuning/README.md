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

Este manual mostra como ajustar (fine-tune) um modelo de linguagem localmente com Unsloth em hardware AMD.

Utiliza um exemplo curto de Ajuste Fino Supervisionado (SFT) com adaptadores LoRA em `unsloth/gemma-4-E4B-it`, usando um subconjunto do conjunto de dados `mlabonne/FineTome-100k`. O objetivo é fornecer-lhe um fluxo de trabalho simples e completo que abrange configuração, treino, inferência e gravação do resultado ajustado.

O exemplo foi concebido para ser prático e fácil de modificar, para que possa utilizá-lo como ponto de partida para os seus próprios conjuntos de dados e modelos.

## O Que Vai Aprender

- Como configurar o ambiente Unsloth
- Como ajustar um LLM usando SFT com Unsloth
- Como gravar o resultado ajustado em armazenamento local

<!-- @device:halo,stx,krk -->
> **Nota:** As técnicas de ajuste fino apresentadas neste manual requerem, no mínimo, **64 GB de RAM do sistema**, dos quais pelo menos **24 GB devem estar disponíveis para a GPU** (os 24 GB fazem parte dos 64 GB, não são adicionais).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** As técnicas de ajuste fino apresentadas neste manual requerem, no mínimo, **24 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total da GPU combina a VRAM dedicada da placa gráfica com a memória de GPU partilhada (emprestada da RAM do sistema).
> - Por isso, placas com menos de 24 GB de VRAM dedicada ainda podem executar este manual utilizando memória de GPU partilhada para compensar a diferença.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** As técnicas de ajuste fino apresentadas neste manual requerem uma placa gráfica com, no mínimo, **24 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treino é executado inteiramente na VRAM dedicada da placa gráfica.
> - Não recorre à memória de GPU partilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 24 GB de VRAM dedicada ficarão sem memória durante o treino no Linux, mesmo que o sistema tenha bastante RAM.
<!-- @os:end -->
<!-- @device:end -->

## Porquê Unsloth?

O Unsloth facilita a execução do ajuste fino de LLMs em hardware local, reduzindo o consumo de memória e acelerando o treino em comparação com uma configuração padrão.

Neste manual, utilizamos o Unsloth em conjunto com **SFT baseado em LoRA**. Isto significa que o modelo base permanece maioritariamente congelado, enquanto é treinado um conjunto muito mais pequeno de pesos de adaptadores. Isto é adequado para o desenvolvimento local, pois é mais leve do que o ajuste fino completo e permite iterar mais rapidamente.

O Unsloth também suporta outras abordagens de treino, incluindo QLoRA e fluxos de trabalho de aprendizagem por reforço. Este manual foca-se, em primeiro lugar, no caminho mais simples: um pequeno exemplo de ajuste fino LoRA que os utilizadores podem executar, compreender e expandir.

## Configurar a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

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
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine e reinicie a sessão para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

Abra um terminal e crie um venv:
<!-- @test:id=create-venv timeout=300 -->
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
> **Nota:** O Python 3.13 é obrigatório para Windows.

<!-- @device:halo_box -->
Abra um terminal PowerShell e crie um ambiente virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Abra um terminal PowerShell e crie um ambiente virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalar Dependências Básicas
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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Durante a importação, o Unsloth pode sondar caminhos de aceleração opcionais do `bitsandbytes`. Em algumas versões do ROCm, poderá ver uma mensagem como `bitsandbytes library load error: Configured ROCm binary not found`. Este manual utiliza o ajuste fino LoRA padrão com `optim="adamw_torch"`, pelo que não dependemos do otimizador `bitsandbytes` nem do QLoRA de 4 bits. Esta mensagem pode ser ignorada em segurança.

<!-- @os:windows -->
> **Nota:** No Windows ROCm, o Unsloth irá imprimir vários avisos no arranque — consulte [Avisos Conhecidos](#known-warnings) abaixo. Estes avisos podem ser todos ignorados em segurança; o treino funciona corretamente.
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

## Transferir o Script de Ajuste Fino do Unsloth

Em vez de executar manualmente cada etapa, este manual disponibiliza um script limpo e completo aqui: [test_unsloth.py](assets/test_unsloth.py).

Execute o seguinte código para correr o script:

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

O restante do manual irá percorrer conceptualmente cada etapa principal do script.

## Como Funciona

O script test_unsloth.py executa os seguintes passos:
* **Carregar Modelo**: Carrega o unsloth/gemma-4-E4B-it usando FastModel.
* **Preparar Dados**: Padroniza o conjunto de dados (por exemplo, FineTome-100k) e aplica o modelo de chat do Gemma-4.
* **Aplicar LoRA**: Adiciona adaptadores aos módulos de linguagem, atenção e MLP para um treino eficiente.
* **Treinar**: Utiliza o SFTTrainer com mascaramento de perda apenas nas respostas.
* **Inferência**: Executa um teste rápido de geração para verificar o desempenho.
* **Gravar**: Exporta os adaptadores LoRA localmente.

## Configuração Principal

Pode modificar as seguintes constantes para personalizar a sua execução:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemplo da mensagem de boas-vindas do Unsloth e da saída ao carregar os pesos do modelo:

![texto alternativo](assets/welcome.png)

## Preparar o Conjunto de Dados

Utilizamos um subconjunto de:
```text
mlabonne/FineTome-100k
```
O conjunto de dados é:
* Convertido para formato de chat
* Processado usando o modelo de chat do Gemma-4
* Limpo para remover tokens BOS duplicados

## Treinar o Modelo

O script executa uma breve demonstração de treino, com os seguintes parâmetros:
- ~50 passos
- Tamanho de lote reduzido
- Acumulação de gradiente

Durante o treino, verá registos como:

![texto alternativo](assets/training.png)


## Gravação e Implementação
### Guardar localmente (LoRA)

O script guarda automaticamente os adaptadores LoRA no OUTPUT_DIR.
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

### Guardar modelo combinado (para vLLM) 

<!-- @os:windows -->
> **Nota:** o vLLM não suporta Windows. Para implementar o seu modelo com fine-tuning no Windows, utilize o llama.cpp (consulte [Exportar GGUF](#export-gguf-for-llamacpp) abaixo) ou transfira o modelo combinado para uma máquina Linux com vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Para implementação com vLLM, combine os adaptadores num modelo completo:
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
## Avisos conhecidos

Estes avisos são apresentados pelo Unsloth no arranque no Windows ROCm e podem todos ser ignorados em segurança:

| Aviso | Motivo | Seguro ignorar? |
|---|---|---|
| `bitsandbytes library load error` | O bitsandbytes não tem build para Windows ROCm | Sim — este guia utiliza `adamw_torch`, não bnb |
| `No ROCm platform found for torch.distributed` | O ROCm no Windows não suporta treino distribuído | Sim — o treino com uma única GPU não é afetado |
| `Unsloth: WARNING! You are using an unsupported platform` | O Unsloth assinala builds não Linux | Sim — o Windows ROCm funciona para SFT com uma única GPU |
| `triton is not available` | O Triton não tem build para Windows | Sim — o Unsloth recorre a kernels PyTorch como alternativa |

O treino irá prosseguir corretamente apesar destes avisos.
<!-- @os:end -->

## Próximos passos
- Experimente o [Unsloth Studio](https://unsloth.ai/docs/new/studio), uma interface gráfica intuitiva para o Unsloth
- Treine com os seus próprios conjuntos de dados específicos
- Experimente fazer fine-tuning com diferentes hiperparâmetros
- Implemente com vLLM ou llama.cpp
- Experimente o QLoRA para uma configuração com menor consumo de memória

## Recursos

Segue-se um conjunto de recursos adicionais para saber mais sobre o Unsloth e o fine-tuning:

* [Documentação do Unsloth](https://docs.unsloth.ai)

* [Unsloth no GitHub](https://github.com/unslothai/unsloth)

* [Guia de Fine-tuning do Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)