<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

## Visão Geral

O ajuste fino eficiente é essencial para adaptar grandes modelos de linguagem (LLMs) a tarefas específicas. LLaMA Factory é uma plataforma de código aberto e fácil de usar que simplifica o treinamento e o ajuste fino de grandes modelos de linguagem e modelos multimodais. Ela permite que os usuários personalizem centenas de modelos pré-treinados localmente com codificação mínima.

Este playbook ensina como fazer o ajuste fino de LLMs usando o LLaMA Factory em seu hardware AMD local.

<!-- @device:stx,krk -->
> **Observação:** As técnicas de ajuste fino apresentadas neste playbook exigem pelo menos **32 GB de RAM do sistema**, com pelo menos **16 GB disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, não são adicionais a eles).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Observação:** As técnicas de ajuste fino apresentadas neste playbook exigem pelo menos **16 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total de GPU combina a VRAM dedicada da placa de vídeo com a memória de GPU compartilhada (emprestada da RAM do sistema).
> - Portanto, placas com menos de 16 GB de VRAM dedicada ainda podem executar este playbook usando memória de GPU compartilhada para compensar a diferença.
<!-- @os:end -->

<!-- @os:linux -->
> **Observação:** As técnicas de ajuste fino apresentadas neste playbook exigem uma placa de vídeo com pelo menos **16 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treinamento é executado inteiramente na VRAM dedicada da placa de vídeo.
> - Ele não recorre à memória de GPU compartilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 16 GB de VRAM dedicada ficarão sem memória durante o treinamento no Linux, mesmo que o sistema tenha bastante RAM.
<!-- @os:end -->
<!-- @device:end -->

## O Que Você Vai Aprender

- Como configurar o LLaMA Factory com o software AMD ROCm™
- Como configurar os parâmetros de ajuste fino de LLM (usando Qwen/Qwen3-4B-Instruct-2507 como exemplo)
- Como executar o ajuste fino no LLaMA Factory
- Como executar a inferência com o modelo ajustado
- Como exportar o modelo ajustado 

## Tempo Estimado

- Duração: Levará cerca de 60 minutos para executar este playbook (dependendo do tamanho do seu modelo/conjunto de dados e da velocidade da rede).
- Consulte o [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) para mais informações.

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificando Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
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
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### Instalando Dependências Básicas

<!-- @require:pytorch,driver -->
 
### Instalando Dependências Adicionais

> **Observação**: Certifique-se de que a versão do Python seja 3.11, 3.12 ou 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Instalar o LLaMA Factory

O LLaMA Factory depende do PyTorch. Você já deve tê-lo instalado conforme os requisitos acima.

Baixe o código-fonte do [repositório oficial do LLaMA Factory no GitHub](https://github.com/hiyouga/LlamaFactory) e instale suas dependências.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Verifique se `llamafactory-cli` é executável.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Exemplo de saída:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Tendo instalado com sucesso o LLaMA Factory, vamos executar o ajuste fino nele.

## Usando a CLI do LLaMA Factory para o Ajuste Fino 

Esta seção abordará como preparar conjuntos de dados de ajuste fino, configurar os parâmetros de LoRA/QLoRA e executar o ajuste fino com LoRA.

### Preparação do Conjunto de Dados

O LLaMA Factory oferece suporte a conjuntos de dados de ajuste fino nos formatos Alpaca e ShareGPT. Todos os conjuntos de dados disponíveis foram definidos no [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Se você estiver usando um conjunto de dados personalizado, certifique-se de adicionar uma descrição do conjunto de dados em `dataset_info.json` e especificar o nome do conjunto de dados antes do treinamento. Mais detalhes podem ser encontrados na documentação [aqui](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Neste playbook, usaremos os conjuntos de dados identity e alpaca_en_demo como exemplo, e configuraremos as informações do conjunto de dados na próxima etapa.
### Configuração de parâmetros de fine-tuning

O LLaMA Factory suporta diversos esquemas de fine-tuning.

| Esquemas de Fine-Tuning | Exemplos do LLaMA Factory |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning com LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning com QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Esses arquivos de configuração de exemplo já especificam parâmetros do modelo, parâmetros do método de fine-tuning, parâmetros do dataset, parâmetros de avaliação e muito mais. Você pode configurá-los de acordo com suas próprias necessidades. Neste playbook, usaremos o [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Principais parâmetros explicados:**
- `model_name_or_path` - Nome do modelo no Hugging Face ou caminho do arquivo de modelo local.
- `stage` - Etapa de treinamento. Opções: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true para treinamento, false para avaliação
- `finetuning_type` - Método de fine-tuning. Opções: freeze, lora, full
- `lora_rank` - A dimensionalidade da matriz de baixo posto (low-rank) usada no LoRA, valores típicos: 4, 6, 8, 16 (valores menores = menos parâmetros = fine-tuning mais rápido; valores maiores = melhor adaptação à tarefa, porém maior uso de recursos).
- `lora_target` - Módulos-alvo para o método LoRA. Padrão: all.
- `dataset` - Dataset(s) a ser(em) usado(s). Use "," para separar múltiplos datasets
- `output_dir` - Caminho de saída do fine-tuning
- `logging_steps` - Intervalo de registro de logs em steps
- `save_steps` - Intervalo de salvamento de checkpoint do modelo.
- `overwrite_output_dir` - Se deve permitir a sobrescrita do diretório de saída.
- `per_device_train_batch_size` - Tamanho do batch de treinamento por dispositivo.
- `gradient_accumulation_steps` - Número de passos de acumulação de gradiente.
- `learning_rate` - Taxa de aprendizado
- `num_train_epochs` - Número de épocas de treinamento
- `lr_scheduler_type` - Programação da taxa de aprendizado. Opções: linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Proporção de warmup da taxa de aprendizado

<!-- @os:linux -->
Vamos modificar o valor padrão de `lora_rank` para executar o fine-tuning em GPUs AMD Ryzen™ & AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vamos atualizar a configuração padrão de fine-tuning com LoRA para melhor compatibilidade com GPUs AMD Ryzen™ e AMD Radeon™:
- Alterar `lora_rank` de `8` para `6` para reduzir o uso de memória durante o fine-tuning.
- Usar `fp16` em vez de `bf16` para maior compatibilidade com GPUs AMD e menor uso de memória.
- Definir `dataloader_num_workers` como `0` no Windows para evitar erros do tipo `"Can't pickle local object<>"` causados pelo carregamento de dados com multiprocessamento.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### Executar o Fine-Tuning com LLaMA Factory 

**llamafactory-cli** é a ferramenta oficial de interface de linha de comando (CLI) do LLaMA Factory, desenvolvida para simplificar os fluxos de trabalho ponta a ponta de LLMs (preparação de dados → fine-tuning → avaliação → implantação) sem a necessidade de escrever código complexo.

Para treinamento/fine-tuning, **llamafactory-cli train** é o subcomando central da CLI do LLaMA Factory. Ele abstrai os fluxos de trabalho de fine-tuning (pré-processamento de dados, ajuste de hiperparâmetros, otimização de hardware) em um único comando de CLI, suportando múltiplos paradigmas de fine-tuning (LoRA/QLoRA/Full Fine-Tuning) e é otimizado para GPUs com recursos limitados (por exemplo, QLoRA em 16GB de VRAM).

Você pode executar o fine-tuning do LLaMA Factory usando o comando a seguir, baseado no arquivo de configuração modificado do fine-tuning com LoRA do Qwen3.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Após a execução do fine-tuning do LLM, todas as saídas geradas são armazenadas em "output_dir", incluindo arquivos de checkpoint do modelo, arquivos de configuração e métricas de treinamento.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### Testar o modelo com fine-tuning aplicado 

**llamafactory-cli chat** foi projetado para chat/inferência interativa com LLMs (tanto modelos base quanto modelos com fine-tuning via LoRA). O LLaMA Factory fornece a configuração de exemplo para executar inferência de modelos com fine-tuning em [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Você também pode modificar essa configuração de exemplo para alterar as definições, como o backend de inferência.

Use o comando a seguir para testar o modelo Qwen3 com fine-tuning aplicado:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Um exemplo de chat usando o modelo com fine-tuning aplicado é mostrado abaixo:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportar o modelo com fine-tuning aplicado

Para casos de uso em produção, o modelo pré-treinado e o adaptador LoRA precisam ser mesclados e exportados em um único modelo. Esse modelo mesclado pode ser usado como um arquivo de modelo Hugging Face normal. O LLaMA Factory fornece as configurações de exemplo em [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Use o comando a seguir para exportar o modelo Qwen3 com fine-tuning aplicado:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
O resultado da exportação do modelo com fine-tuning aplicado é mostrado abaixo.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end -->
## Usando a GUI do LLaMA Factory

O `LLaMA-Factory` também oferece suporte a ajuste fino de LLMs sem código por meio de uma interface web no navegador.

Use o seguinte comando para abri-la:

```bash
llamafactory-cli webui
```
A `LlamaFactory Web UI` oferece uma interface simplificada para gerenciar fluxos de trabalho de machine learning, incluindo treinamento, avaliação, previsão, chat e exportação de modelos. Aqui está uma breve introdução a cada aba:

* **Train**: esta aba permite selecionar um modelo e um conjunto de dados, configurar os parâmetros de treinamento e iniciar o processo de treinamento. É essencial entender os parâmetros obrigatórios e opcionais para otimizar a configuração do treinamento.
* **Evaluate & Predict**: após o treinamento, você pode avaliar o desempenho do modelo e fazer previsões usando esta aba. Ela oferece insights sobre a precisão e a eficácia do modelo em novos dados.
* **Chat**: assim que o treinamento estiver concluído, carregue o modelo na aba Chat para interagir com ele e ver os resultados do seu trabalho. Esse recurso permite a comunicação em tempo real com o modelo treinado.
* **Export**: esta aba facilita a exportação de modelos treinados para implantação ou uso posterior. Você pode salvar seus modelos em vários formatos adequados para diferentes aplicações.

Para obter orientações detalhadas, recomendamos consultar a documentação oficial no [repositório GitHub do LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) e no [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Além disso, o [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) fornece informações valiosas sobre a interface e suas funcionalidades.

## Próximas etapas
- Experimente diferentes modelos, como o `gpt-oss` e outros modelos de última geração.
- Experimente diferentes backends no modelo ajustado

Para mais documentação, visite: https://llamafactory.readthedocs.io/en/latest/