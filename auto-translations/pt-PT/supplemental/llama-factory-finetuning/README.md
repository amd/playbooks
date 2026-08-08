<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

## Visão Geral

O ajuste fino eficiente é fundamental para adaptar modelos de linguagem de grande dimensão (LLMs) a tarefas específicas. O LLaMA Factory é uma plataforma de código aberto e fácil de utilizar que simplifica o treino e o ajuste fino de modelos de linguagem de grande dimensão e de modelos multimodais. Permite aos utilizadores personalizar centenas de modelos pré-treinados localmente com um mínimo de programação.

Este playbook ensina-o a fazer o ajuste fino de LLMs utilizando o LLaMA Factory no seu hardware AMD local.

<!-- @device:stx,krk -->
> **Nota:** As técnicas de ajuste fino apresentadas neste playbook requerem, no mínimo, **32 GB de RAM do sistema**, dos quais pelo menos **16 GB devem estar disponíveis para a GPU** (os 16 GB fazem parte dos 32 GB, e não são adicionais a estes).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** As técnicas de ajuste fino apresentadas neste playbook requerem, no mínimo, **16 GB de memória total de GPU** e **32 GB de RAM do sistema**.
> - No Windows, a memória total da GPU combina a VRAM dedicada da placa gráfica com a memória de GPU partilhada (retirada da RAM do sistema).
> - Assim, placas com menos de 16 GB de VRAM dedicada ainda conseguem executar este playbook ao utilizar a memória de GPU partilhada para compensar a diferença.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** As técnicas de ajuste fino apresentadas neste playbook requerem uma placa gráfica com pelo menos **16 GB de memória de GPU dedicada** e **32 GB de RAM do sistema**.
> - No Linux, o treino é executado inteiramente na VRAM dedicada da placa gráfica.
> - Não recorre à memória de GPU partilhada (RAM do sistema) quando a VRAM se esgota.
> - Placas com menos de 16 GB de VRAM dedicada ficarão sem memória durante o treino no Linux, mesmo que o sistema tenha bastante RAM disponível.
<!-- @os:end -->
<!-- @device:end -->

## O Que Vai Aprender

- Como configurar o LLaMA Factory com o software AMD ROCm™
- Como configurar os parâmetros de ajuste fino de LLMs (utilizando o Qwen/Qwen3-4B-Instruct-2507 como exemplo)
- Como executar o ajuste fino com o LLaMA Factory
- Como executar inferência com o modelo ajustado
- Como exportar o modelo ajustado

## Tempo Estimado

- Duração: Executar este playbook demorará cerca de 60 minutos (dependendo do tamanho do seu modelo/conjunto de dados e da velocidade da rede).
- Consulte o [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) para mais informações.

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalação dos Pré-requisitos de Software

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
<!-- @test:id=create-venv timeout=300 -->
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
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine e reinicie a sessão para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
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

### Instalação das Dependências Básicas

<!-- @require:pytorch,driver -->
 
### Instalação de Dependências Adicionais

> **Nota**: Certifique-se de que a versão do Python é 3.11, 3.12 ou 3.13

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

O LLaMA Factory depende do PyTorch. Este já deverá estar instalado de acordo com os requisitos acima.

Transfira o código-fonte do [repositório oficial do LLaMA Factory no GitHub](https://github.com/hiyouga/LlamaFactory) e instale as respetivas dependências.

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

Verifique se o `llamafactory-cli` é executável.

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

Exemplo de resultado:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Após ter instalado com sucesso o LLaMA Factory, vamos agora executar o ajuste fino.

## Utilizar a CLI do LLaMA Factory para Ajuste Fino

Esta secção aborda como preparar conjuntos de dados para ajuste fino, configurar os parâmetros de LoRA/QLoRA e executar o ajuste fino com LoRA.

### Preparação do Conjunto de Dados

O LLaMA Factory suporta conjuntos de dados de ajuste fino nos formatos Alpaca e ShareGPT. Todos os conjuntos de dados disponíveis foram definidos em [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Se estiver a utilizar um conjunto de dados personalizado, certifique-se de que adiciona uma descrição do conjunto de dados em `dataset_info.json` e especifica o nome do conjunto de dados antes do treino. Pode encontrar mais detalhes na respetiva documentação [aqui](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Neste playbook, utilizaremos os conjuntos de dados identity e alpaca_en_demo como exemplo, e configuraremos a informação do conjunto de dados no passo seguinte.
### Configuração dos parâmetros de fine-tuning

O LLaMA Factory suporta vários esquemas de fine-tuning.

| Esquemas de Fine-Tuning | Exemplos do LLaMA Factory |
|-----------|------|
| Parâmetros completos (Full-Parameter)    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Estes ficheiros de configuração de exemplo têm parâmetros do modelo, parâmetros do método de fine-tuning, parâmetros do conjunto de dados, parâmetros de avaliação e outros já especificados. Pode configurá-los de acordo com as suas próprias necessidades. Neste manual, vamos utilizar o [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Explicação dos principais parâmetros:**
- `model_name_or_path` - Nome do modelo no Hugging Face ou caminho do ficheiro do modelo local.
- `stage` - Fase de treino. Opções: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true para treino, false para avaliação
- `finetuning_type` - Método de fine-tuning. Opções: freeze, lora, full
- `lora_rank` - A dimensionalidade da matriz de baixo posto (low-rank) utilizada no LoRA, valores típicos: 4, 6, 8, 16 (valores mais baixos = menos parâmetros = fine-tuning mais rápido; valores mais altos = melhor adaptação à tarefa, mas maior utilização de recursos).
- `lora_target` - Módulos-alvo para o método LoRA. Predefinição: all.
- `dataset` - Conjunto(s) de dados a utilizar. Utilize “,” para separar vários conjuntos de dados
- `output_dir` - Caminho de saída do fine-tuning
- `logging_steps` - Intervalo de registo (logging) em passos (steps)
- `save_steps` - Intervalo de gravação de checkpoints do modelo.
- `overwrite_output_dir` - Se é permitido substituir o diretório de saída.
- `per_device_train_batch_size` - Tamanho do batch de treino por dispositivo.
- `gradient_accumulation_steps` - Número de passos de acumulação de gradiente.
- `learning_rate` - Taxa de aprendizagem
- `num_train_epochs` - Número de épocas (epochs) de treino
- `lr_scheduler_type` - Programação da taxa de aprendizagem. Opções: linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Rácio de warmup da taxa de aprendizagem

<!-- @os:linux -->
Vamos alterar o valor predefinido de `lora_rank` para executar o fine-tuning em GPUs AMD Ryzen™ & AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vamos atualizar a configuração predefinida de fine-tuning LoRA para uma melhor compatibilidade com GPUs AMD Ryzen™ e AMD Radeon™:
- Alterar `lora_rank` de `8` para `6` para reduzir a utilização de memória durante o fine-tuning.
- Utilizar `fp16` em vez de `bf16` para uma compatibilidade mais ampla com GPUs AMD e menor utilização de memória.
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

### Executar o Fine-Tuning do LLaMA Factory 

**llamafactory-cli** é a ferramenta oficial de interface de linha de comandos (CLI) do LLaMA Factory, desenvolvida para simplificar os fluxos de trabalho completos de LLM (preparação de dados → fine-tuning → avaliação → implementação) sem necessidade de escrever código complexo.

Para treino/fine-tuning, **llamafactory-cli train** é o subcomando principal da CLI do LLaMA Factory. Este abstrai os fluxos de trabalho de fine-tuning (pré-processamento de dados, ajuste de hiperparâmetros, otimização de hardware) num único comando CLI, suportando vários paradigmas de fine-tuning (LoRA/QLoRA/Full Fine-Tuning) e é otimizado para GPUs com poucos recursos (por exemplo, QLoRA em 16GB de VRAM).

Pode executar o fine-tuning do LLaMA Factory utilizando o seguinte comando, com base no ficheiro de configuração modificado do fine-tuning LoRA do Qwen3.

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

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Depois de executar o fine-tuning do LLM, todos os resultados gerados são armazenados no "output_dir", incluindo ficheiros de checkpoint do modelo, ficheiros de configuração e métricas de treino.

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

### Testar o modelo com fine-tuning 

**llamafactory-cli chat** foi concebido para chat/inferência interativa com LLMs (tanto modelos base como modelos com fine-tuning LoRA). O LLaMA Factory fornece a configuração de exemplo para executar a inferência de modelos com fine-tuning em [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Também pode modificar esta configuração de exemplo para alterar definições, como o backend de inferência.

Utilize o seguinte comando para testar o modelo Qwen3 com fine-tuning:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Um exemplo de chat utilizando o modelo com fine-tuning é apresentado abaixo:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportar o modelo com fine-tuning

Para casos de utilização em produção, o modelo pré-treinado e o adaptador LoRA precisam de ser combinados e exportados para um único modelo. Este modelo combinado pode ser utilizado como um ficheiro de modelo Hugging Face normal. O LLaMA Factory fornece as configurações de exemplo em [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Utilize o seguinte comando para exportar o modelo Qwen3 com fine-tuning:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
O resultado da exportação do modelo com fine-tuning é apresentado abaixo.

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
## Utilizar a GUI do LLaMA Factory

O `LLaMA-Factory` também suporta o ajuste fino (fine-tuning) de LLMs sem código através de uma interface web no browser.

Utilize o seguinte comando para a abrir:

```bash
llamafactory-cli webui
```
O `LlamaFactory Web UI` oferece uma interface simplificada para gerir fluxos de trabalho de machine learning, incluindo treino, avaliação, previsão, conversação e exportação de modelos. Segue-se uma breve introdução a cada separador:

* **Train**: Este separador permite selecionar um modelo e um conjunto de dados, configurar os parâmetros de treino e iniciar o processo de treino. É essencial compreender os parâmetros obrigatórios e opcionais para otimizar a configuração de treino.
* **Evaluate & Predict**: Após o treino, pode avaliar o desempenho do modelo e fazer previsões através deste separador. Fornece informações sobre a precisão e a eficácia do modelo em novos dados.
* **Chat**: Assim que o treino estiver concluído, carregue o modelo no separador Chat para interagir com ele e ver os resultados do seu trabalho. Esta funcionalidade permite a comunicação em tempo real com o modelo treinado.
* **Export**: Este separador facilita a exportação de modelos treinados para implementação ou utilização posterior. Pode guardar os seus modelos em vários formatos adequados para diferentes aplicações.

Para obter orientações detalhadas, aconselhamo-lo a consultar a documentação oficial no [repositório GitHub do LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) e no [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Além disso, o [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) fornece informações valiosas sobre a interface e as suas funcionalidades.

## Próximos passos
- Experimente diferentes modelos, como o `gpt-oss` e outros modelos de última geração.
- Experimente diferentes backends no modelo ajustado (fine-tuned)
 
Para mais documentação, visite: https://llamafactory.readthedocs.io/en/latest/