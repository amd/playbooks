<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

Este guia demonstra como ajustar (fine-tune) um modelo de linguagem localmente com Unsloth em hardware AMD.

Utiliza um exemplo breve de Ajuste Fino Supervisionado (SFT) com adaptadores LoRA em `unsloth/gemma-4-E4B-it`, usando um subconjunto do conjunto de dados `mlabonne/FineTome-100k`. O objetivo é fornecer um fluxo de trabalho simples e completo que abrange a configuração, o treino, a inferência e a gravação do resultado ajustado.

O exemplo foi concebido para ser prático e fácil de modificar, para que possa ser utilizado como ponto de partida para os seus próprios conjuntos de dados e modelos.

## O Que Vai Aprender

- Como configurar o ambiente Unsloth
- Como ajustar um LLM utilizando SFT com Unsloth
- Como guardar o resultado ajustado em armazenamento local

<!-- @device:halo,stx,krk -->
> **Nota:** As técnicas de ajuste fino apresentadas neste guia requerem, no mínimo, **64 GB de RAM do sistema**, dos quais, pelo menos, **24 GB devem estar disponíveis para a GPU** (os 24 GB fazem parte dos 64 GB, não são adicionais).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** As técnicas de ajuste fino apresentadas neste guia requerem, no mínimo, **24 GB de memória total da GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total da GPU combina a VRAM dedicada da placa gráfica com a memória de GPU partilhada (obtida a partir da RAM do sistema).
> - Por este motivo, placas com menos de 24 GB de VRAM dedicada ainda conseguem executar este guia, utilizando memória de GPU partilhada para compensar a diferença.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** As técnicas de ajuste fino apresentadas neste guia requerem uma placa gráfica com, no mínimo, **24 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treino é executado inteiramente na VRAM dedicada da placa gráfica.
> - Não existe recurso a memória de GPU partilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 24 GB de VRAM dedicada ficarão sem memória durante o treino no Linux, mesmo que o sistema tenha bastante RAM disponível.
<!-- @os:end -->
<!-- @device:end -->

## Porquê Unsloth?

O Unsloth facilita a execução do ajuste fino de LLMs em hardware local, reduzindo a utilização de memória e acelerando o treino em comparação com uma configuração padrão.

Neste guia, utilizamos o Unsloth em conjunto com **SFT baseado em LoRA**. Isto significa que o modelo base permanece maioritariamente congelado, enquanto um conjunto muito mais pequeno de pesos de adaptador é treinado. Esta abordagem é adequada ao desenvolvimento local, pois é mais leve do que o ajuste fino completo e permite iterações mais rápidas.

O Unsloth também suporta outras abordagens de treino, incluindo QLoRA e fluxos de trabalho de aprendizagem por reforço. Este guia foca-se primeiro no caminho mais simples: um pequeno exemplo de ajuste fino com LoRA que os utilizadores podem executar, compreender e expandir.

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

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Abra um terminal e crie um venv com o software AMD ROCm™ e o PyTorch já instalados:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu utilizador acesso aos dispositivos GPU** (é necessário terminar sessão e voltar a iniciar sessão para que isto tenha efeito):

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
> **Nota:** O Python 3.13 é obrigatório no Windows.

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
<!-- @require:driver -->

> **Importante:** O Unsloth ainda não suporta a versão do PyTorch 2.13 fornecida com o ROCm 10. Para este guia, instale **ROCm 7.14 com PyTorch 2.12** utilizando os comandos abaixo. Não utilize os pacotes ROCm 10 / PyTorch 2.13.

**Instale o PyTorch com suporte para o software AMD ROCm™** no ambiente virtual criado:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Para outros dispositivos, consulte a [Documentação do ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) para obter instruções completas.

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Durante a importação, o Unsloth pode testar caminhos de aceleração opcionais do `bitsandbytes`. Em algumas versões do ROCm, poderá ver uma mensagem semelhante a `bitsandbytes library load error: Configured ROCm binary not found`. Este guia utiliza ajuste fino LoRA padrão com `optim="adamw_torch"`, pelo que não dependemos do otimizador `bitsandbytes` nem do QLoRA de 4 bits. Esta mensagem pode ser ignorada com segurança.

<!-- @os:windows -->
> **Nota:** No Windows ROCm, o Unsloth irá imprimir vários avisos no arranque — consulte [Avisos Conhecidos](#known-warnings) abaixo. Todos podem ser ignorados com segurança; o treino funciona corretamente.
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

Em vez de executar manualmente cada passo, este guia disponibiliza um script limpo e completo aqui: [test_unsloth.py](assets/test_unsloth.py).

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

O restante do guia percorrerá conceptualmente cada etapa principal do script.

## Como Funciona

O script test_unsloth.py executa os seguintes passos:
* **Carregar Modelo**: Carrega o unsloth/gemma-4-E4B-it utilizando FastModel.
* **Preparar Dados**: Normaliza o conjunto de dados (por exemplo, FineTome-100k) e aplica o modelo de conversação (chat template) do Gemma-4.
* **Aplicar LoRA**: Adiciona adaptadores aos módulos de linguagem, atenção e MLP para um treino eficiente.
* **Treinar**: Utiliza o SFTTrainer com mascaramento de perda apenas na resposta (response-only loss masking).
* **Inferência**: Executa um teste de geração rápido para verificar o desempenho.
* **Guardar**: Exporta os adaptadores LoRA localmente.
## Configuração Principal

Pode modificar as seguintes constantes para personalizar a sua execução:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemplo da mensagem de boas-vindas do Unsloth e da saída ao carregar os pesos do modelo:

![alt text](assets/welcome.png)

## Preparar o Conjunto de Dados

Utilizamos um subconjunto de:
```text
mlabonne/FineTome-100k
```
O conjunto de dados é: 
* Convertido para formato de chat
* Processado utilizando o modelo de chat Gemma-4
* Limpo para remover tokens BOS duplicados

## Treinar o Modelo

O script executa uma breve demonstração de treino, com os seguintes parâmetros:
- ~50 passos
- Tamanho de lote pequeno
- Acumulação de gradiente

Durante o treino, verá registos como:

![alt text](assets/training.png)


## Guardar e Implementar

### Guardar Localmente (LoRA)

O script guarda automaticamente os adaptadores LoRA na OUTPUT_DIR.
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

### Guardar modelo fundido (para vLLM) 

<!-- @os:windows -->
> **Nota:** o vLLM não suporta Windows. Para implementar o seu modelo ajustado no Windows, utilize o llama.cpp (consulte [Exportar GGUF](#export-gguf-for-llamacpp) abaixo) ou transfira o modelo fundido para uma máquina Linux com vLLM em execução.
<!-- @os:end -->

<!-- @os:linux -->
Para implementação com vLLM, funda os adaptadores num modelo completo:
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

Estes avisos são apresentados pelo Unsloth no arranque em Windows ROCm e podem ser todos ignorados em segurança:

| Aviso | Motivo | Seguro ignorar? |
|---|---|---|
| `bitsandbytes library load error` | o bitsandbytes não tem compilação para Windows ROCm | Sim — este manual utiliza `adamw_torch`, não bnb |
| `No ROCm platform found for torch.distributed` | o ROCm no Windows não suporta treino distribuído | Sim — o treino com uma única GPU não é afetado |
| `Unsloth: WARNING! You are using an unsupported platform` | o Unsloth assinala compilações não-Linux | Sim — o Windows ROCm funciona para SFT com uma única GPU |
| `triton is not available` | o Triton não tem compilação para Windows | Sim — o Unsloth recorre a kernels do PyTorch |

O treino prosseguirá corretamente apesar destes avisos.
<!-- @os:end -->

## Próximos Passos
- Experimente o [Unsloth Studio](https://unsloth.ai/docs/new/studio), uma interface gráfica intuitiva para o Unsloth
- Treine com os seus próprios conjuntos de dados específicos
- Experimente o ajuste fino com diferentes hiperparâmetros
- Implemente com vLLM ou llama.cpp
- Experimente o QLoRA para uma configuração com menor consumo de memória

## Recursos

Abaixo encontram-se alguns recursos adicionais para saber mais sobre o Unsloth e o ajuste fino:

* [Documentação do Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Guia de Ajuste Fino do Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)