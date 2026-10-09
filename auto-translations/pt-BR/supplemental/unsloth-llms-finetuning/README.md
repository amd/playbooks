<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão geral

Este playbook mostra como ajustar (fine-tune) localmente um modelo de linguagem com Unsloth em hardware AMD.

Ele usa um exemplo curto de Supervised Fine-Tuning (SFT) com adaptadores LoRA no `unsloth/gemma-4-E4B-it`, utilizando um subconjunto do dataset `mlabonne/FineTome-100k`. O objetivo é fornecer um fluxo de trabalho simples de ponta a ponta que abrange configuração, treinamento, inferência e salvamento do resultado ajustado.

O exemplo foi projetado para ser prático e fácil de modificar, para que você possa usá-lo como ponto de partida para seus próprios datasets e modelos.

## O que você vai aprender

- Como configurar o ambiente Unsloth
- Como ajustar um LLM usando SFT com Unsloth
- Como salvar o resultado do fine-tuning em armazenamento local

<!-- @device:halo,stx,krk -->
> **Observação:** As técnicas de fine-tuning descritas neste playbook exigem pelo menos **64 GB de RAM do sistema**, com pelo menos **24 GB disponíveis para a GPU** (os 24 GB fazem parte dos 64 GB, e não são adicionais a eles).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Observação:** As técnicas de fine-tuning descritas neste playbook exigem pelo menos **24 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total de GPU combina a VRAM dedicada da placa de vídeo com a memória de GPU compartilhada (emprestada da RAM do sistema).
> - Portanto, placas com menos de 24 GB de VRAM dedicada ainda podem executar este playbook usando memória de GPU compartilhada para compensar a diferença.
<!-- @os:end -->

<!-- @os:linux -->
> **Observação:** As técnicas de fine-tuning descritas neste playbook exigem uma placa de vídeo com pelo menos **24 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treinamento é executado inteiramente na VRAM dedicada da placa de vídeo.
> - Ele não recorre à memória de GPU compartilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 24 GB de VRAM dedicada ficarão sem memória durante o treinamento no Linux, mesmo que o sistema tenha bastante RAM.
<!-- @os:end -->
<!-- @device:end -->

## Por que usar o Unsloth?

O Unsloth facilita a execução do fine-tuning de LLMs em hardware local, reduzindo o uso de memória e acelerando o treinamento em comparação com uma configuração padrão.

Neste playbook, usamos o Unsloth em conjunto com **SFT baseado em LoRA**. Isso significa que o modelo base permanece em grande parte congelado, enquanto um conjunto muito menor de pesos de adaptador é treinado. Essa abordagem é ideal para desenvolvimento local, pois é mais leve do que um fine-tuning completo e permite iterações mais rápidas.

O Unsloth também oferece suporte a outras abordagens de treinamento, incluindo QLoRA e fluxos de trabalho de aprendizado por reforço. Este playbook foca primeiro no caminho mais simples: um pequeno exemplo de fine-tuning com LoRA que os usuários podem executar, entender e expandir.

<!-- @device:halo_box,halo,stx,krk -->
## Definindo a configuração de memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar atualizações de software
> **Observação**: Se o VS Code não estiver instalado, você pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os pré-requisitos de software

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Criar um ambiente virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Abra um terminal e crie um venv com o AMD ROCm™ software e o PyTorch já instalados:
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
**Conceda ao seu usuário acesso aos dispositivos de GPU** (saia e entre novamente na sessão para que isso tenha efeito):

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
> **Observação:** O Python 3.13 é obrigatório no Windows.

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

### Instalando dependências básicas
<!-- @require:driver -->

> **Importante:** O Unsloth ainda não oferece suporte ao build do PyTorch 2.13 que acompanha o ROCm 10. Para este playbook, instale o **ROCm 7.14 com PyTorch 2.12** usando os comandos abaixo. Não use os pacotes ROCm 10 / PyTorch 2.13.

**Instale o PyTorch com suporte ao AMD ROCm™ software** no ambiente virtual criado:

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

Para outros dispositivos, consulte a [documentação do ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) para instruções completas.

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

### Dependências adicionais

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

> **Observação:** Durante a importação, o Unsloth pode testar caminhos opcionais de aceleração do `bitsandbytes`. Em algumas versões do ROCm, você pode ver uma mensagem como `bitsandbytes library load error: Configured ROCm binary not found`. Este playbook usa fine-tuning padrão com LoRA e `optim="adamw_torch"`, portanto não dependemos do otimizador `bitsandbytes` nem do QLoRA de 4 bits. Essa mensagem pode ser ignorada com segurança.

<!-- @os:windows -->
> **Observação:** No Windows com ROCm, o Unsloth exibirá vários avisos na inicialização — veja [Avisos conhecidos](#known-warnings) abaixo. Todos podem ser ignorados com segurança; o treinamento funciona corretamente.
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

## Baixe o script de fine-tuning do Unsloth

Em vez de executar manualmente cada etapa, este playbook disponibiliza um script limpo e completo aqui: [test_unsloth.py](assets/test_unsloth.py).

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

O restante do playbook percorrerá conceitualmente cada etapa principal do script. 

## Como funciona

O script test_unsloth.py executa as seguintes etapas:
* **Carregar o modelo**: Carrega o unsloth/gemma-4-E4B-it usando o FastModel.
* **Preparar os dados**: Padroniza o dataset (por exemplo, FineTome-100k) e aplica o template de chat do Gemma-4.
* **Aplicar o LoRA**: Adiciona adaptadores aos módulos de linguagem, atenção e MLP para um treinamento eficiente.
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

Exemplo da mensagem de boas-vindas do Unsloth e da saída ao carregar os pesos do modelo:

![alt text](assets/welcome.png)

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

O script executa uma breve demonstração de treinamento, com os seguintes parâmetros:
- ~50 etapas
- Tamanho de lote pequeno
- Acúmulo de gradiente

Durante o treinamento, você verá logs como estes:

![alt text](assets/training.png)


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
> **Observação:** o vLLM não é compatível com Windows. Para implantar seu modelo ajustado no Windows, use o llama.cpp (consulte [Exportar GGUF](#export-gguf-for-llamacpp) abaixo) ou transfira o modelo mesclado para uma máquina Linux executando vLLM.
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
| `bitsandbytes library load error` | O bitsandbytes não possui build para Windows ROCm | Sim — este playbook usa `adamw_torch`, não o bnb |
| `No ROCm platform found for torch.distributed` | O ROCm no Windows não oferece suporte a treinamento distribuído | Sim — o treinamento com uma única GPU não é afetado |
| `Unsloth: WARNING! You are using an unsupported platform` | O Unsloth sinaliza builds não Linux | Sim — o Windows ROCm funciona para SFT com uma única GPU |
| `triton is not available` | O Triton não possui build para Windows | Sim — o Unsloth volta a usar os kernels do PyTorch |

O treinamento prosseguirá corretamente apesar desses avisos.
<!-- @os:end -->

## Próximos Passos
- Experimente o [Unsloth Studio](https://unsloth.ai/docs/new/studio), uma GUI intuitiva para o Unsloth
- Treine com seus próprios datasets específicos
- Experimente o ajuste fino com diferentes hiperparâmetros
- Implante com vLLM ou llama.cpp
- Experimente o QLoRA para uma configuração com menor uso de memória

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre o Unsloth e o ajuste fino:

* [Documentação do Unsloth](https://docs.unsloth.ai)

* [Unsloth no GitHub](https://github.com/unslothai/unsloth)

* [Guia de Ajuste Fino do Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)