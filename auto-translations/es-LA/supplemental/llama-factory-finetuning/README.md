<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

## Descripción general

El ajuste fino eficiente es fundamental para adaptar los modelos de lenguaje grandes (LLM) a tareas específicas. LLaMA Factory es una plataforma de código abierto y fácil de usar que simplifica el entrenamiento y ajuste fino de modelos de lenguaje grandes y modelos multimodales. Permite a los usuarios personalizar cientos de modelos preentrenados de forma local con una mínima cantidad de código.

Este playbook te enseña cómo ajustar finamente los LLM usando LLaMA Factory en tu hardware AMD local.

<!-- @device:stx,krk -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos **32 GB de RAM del sistema**, con al menos **16 GB de esta disponibles para la GPU** (los 16 GB forman parte de los 32 GB, no son adicionales a ellos).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos **16 GB de memoria total de GPU** y **32 GB de RAM del sistema**.
> - En Windows, la memoria total de GPU combina la VRAM dedicada de la tarjeta gráfica con la memoria compartida de GPU (tomada de la RAM del sistema).
> - Por lo tanto, las tarjetas con menos de 16 GB de VRAM dedicada aún pueden ejecutar este playbook usando memoria compartida de GPU para compensar la diferencia.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren una tarjeta gráfica con al menos **16 GB de memoria de GPU dedicada** y **32 GB de RAM del sistema**.
> - En Linux, el entrenamiento se ejecuta completamente en la VRAM dedicada de la tarjeta gráfica.
> - No recurre a la memoria compartida de GPU (RAM del sistema) cuando se agota la VRAM.
> - Las tarjetas con menos de 16 GB de VRAM dedicada se quedarán sin memoria durante el entrenamiento en Linux, incluso si el sistema tiene abundante RAM.
<!-- @os:end -->
<!-- @device:end -->

## Qué aprenderás

- Cómo configurar LLaMA Factory con el software AMD ROCm™
- Cómo configurar los parámetros de ajuste fino de LLM (usando Qwen/Qwen3-4B-Instruct-2507 como ejemplo)
- Cómo ejecutar el ajuste fino con LLaMA Factory
- Cómo ejecutar la inferencia con el modelo ajustado finamente
- Cómo exportar el modelo ajustado finamente

## Tiempo estimado

- Duración: Ejecutar este playbook tomará aproximadamente 60 minutos (dependiendo del tamaño de tu modelo/conjunto de datos y la velocidad de la red).
- Consulta [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) para obtener más información.

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de requisitos previos de software

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

#### Crear un entorno virtual

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
**Otorga acceso a tu usuario a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

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

### Instalación de dependencias básicas

<!-- @require:pytorch,driver -->
 
### Instalación de dependencias adicionales

> **Nota**: Asegúrate de que la versión de Python sea 3.11, 3.12 o 3.13

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

### Instalar LLaMA Factory

LLaMA Factory depende de PyTorch. Ya deberías tenerlo instalado según los requisitos anteriores.

Descarga el código fuente desde el [repositorio oficial de LLaMA Factory en GitHub](https://github.com/hiyouga/LlamaFactory), e instala sus dependencias.

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

Verifica si `llamafactory-cli` es ejecutable.

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

Ejemplo de salida:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Habiendo instalado exitosamente LLaMA Factory, ejecutemos el ajuste fino en él.

## Uso de la CLI de LLaMA Factory para el ajuste fino

Esta sección abordará cómo preparar los conjuntos de datos para el ajuste fino, configurar los parámetros de LoRA/QLoRA y ejecutar el ajuste fino con LoRA.

### Preparación del conjunto de datos

LLaMA Factory admite conjuntos de datos para ajuste fino en formato Alpaca y formato ShareGPT. Todos los conjuntos de datos disponibles se han definido en [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Si estás usando un conjunto de datos personalizado, asegúrate de agregar una descripción del conjunto de datos en `dataset_info.json` y especificar el nombre del conjunto de datos antes del entrenamiento. Puedes encontrar más detalles en su documentación [aquí](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

En este playbook, usaremos los conjuntos de datos identity y alpaca_en_demo como ejemplo, y configuraremos la información del conjunto de datos en el siguiente paso.
### Configuración de parámetros de fine-tuning

LLaMA Factory admite múltiples esquemas de fine-tuning.

| Esquemas de fine-tuning | Ejemplos de LLaMA Factory |
|-----------|------|
| Parámetros completos    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning con LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning con QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Estos archivos de configuración de ejemplo especifican parámetros del modelo, parámetros del método de fine-tuning, parámetros del conjunto de datos, parámetros de evaluación y más. Puedes configurarlos según tus propias necesidades. En este playbook, usaremos [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Explicación de los parámetros clave:**
- `model_name_or_path` - Nombre del modelo en Hugging Face o ruta del archivo del modelo local.
- `stage` - Etapa de entrenamiento. Opciones: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true para entrenamiento, false para evaluación
- `finetuning_type` - Método de fine-tuning. Opciones: freeze, lora, full
- `lora_rank` - La dimensionalidad de la matriz de bajo rango utilizada en LoRA, valores típicos: 4, 6, 8, 16 (valores más pequeños = menos parámetros = fine-tuning más rápido; valores más grandes = mejor adaptación a la tarea, pero mayor uso de recursos).
- `lora_target` - Módulos objetivo para el método LoRA. Predeterminado: all.
- `dataset` - Conjunto(s) de datos a utilizar. Usa "," para separar varios conjuntos de datos
- `output_dir` - Ruta de salida del fine-tuning
- `logging_steps` - Intervalo de registro en pasos
- `save_steps` - Intervalo de guardado del checkpoint del modelo.
- `overwrite_output_dir` - Indica si se permite sobrescribir el directorio de salida.
- `per_device_train_batch_size` - Tamaño del lote de entrenamiento por dispositivo.
- `gradient_accumulation_steps` - Número de pasos de acumulación de gradiente.
- `learning_rate` - Tasa de aprendizaje
- `num_train_epochs` - Número de épocas de entrenamiento
- `lr_scheduler_type` - Programación de la tasa de aprendizaje. Opciones: linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Proporción de calentamiento de la tasa de aprendizaje

<!-- @os:linux -->
Modificaremos el valor predeterminado de `lora_rank` para ejecutar el fine-tuning en las GPU AMD Ryzen™ y AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Actualizaremos la configuración de fine-tuning con LoRA predeterminada para una mejor compatibilidad con las GPU AMD Ryzen™ y AMD Radeon™:
- Cambiar `lora_rank` de `8` a `6` para reducir el uso de memoria durante el fine-tuning.
- Usar `fp16` en lugar de `bf16` para una mayor compatibilidad con GPU AMD y un menor uso de memoria.
- Establecer `dataloader_num_workers` en `0` en Windows para evitar los errores de `"Can't pickle local object<>"` causados por la carga de datos con multiprocesamiento.

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

### Ejecutar el fine-tuning de LLaMA Factory 

**llamafactory-cli** es la herramienta oficial de interfaz de línea de comandos (CLI) para LLaMA Factory, desarrollada para simplificar los flujos de trabajo integrales de LLM (preparación de datos → fine-tuning → evaluación → implementación) sin necesidad de escribir código complejo.

Para el entrenamiento/fine-tuning, **llamafactory-cli train** es el subcomando principal de la CLI de LLaMA Factory. Abstrae los flujos de trabajo de fine-tuning (preprocesamiento de datos, ajuste de hiperparámetros, optimización de hardware) en un único comando de CLI, admite múltiples paradigmas de fine-tuning (LoRA/QLoRA/Fine-Tuning completo) y está optimizado para GPU de bajos recursos (por ejemplo, QLoRA en 16 GB de VRAM).

Puedes ejecutar el fine-tuning de LLaMA Factory usando el siguiente comando, que se basa en el archivo de configuración modificado del fine-tuning con Qwen3 LoRA.

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

Después de ejecutar el fine-tuning del LLM, todos los resultados generados se almacenan en "output_dir", incluidos los archivos de checkpoint del modelo, los archivos de configuración y las métricas de entrenamiento.

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

### Probar el modelo con fine-tuning 

**llamafactory-cli chat** está diseñado para el chat/inferencia interactivo con LLM (tanto modelos base como modelos con fine-tuning de LoRA). LLaMA Factory proporciona la configuración de ejemplo para ejecutar la inferencia de modelos con fine-tuning en [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). También puedes modificar esta configuración de ejemplo para cambiar los ajustes, como el backend de inferencia.

Usa el siguiente comando para probar el modelo Qwen3 con fine-tuning:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
A continuación se muestra un ejemplo de chat usando el modelo con fine-tuning:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportar el modelo con fine-tuning

Para casos de uso en producción, el modelo preentrenado y el adaptador LoRA deben fusionarse y exportarse en un solo modelo. Este modelo fusionado se puede usar como un archivo de modelo normal de Hugging Face. LLaMA Factory proporciona las configuraciones de ejemplo en [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Usa el siguiente comando para exportar el modelo Qwen3 con fine-tuning:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
A continuación se muestra el resultado de exportar el modelo con fine-tuning.

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
## Usando LLaMA Factory GUI

`LLaMA-Factory` también admite el ajuste fino de LLMs sin necesidad de código a través de una interfaz web en el navegador.

Utiliza el siguiente comando para abrirla:

```bash
llamafactory-cli webui
```
El `LlamaFactory Web UI` ofrece una interfaz simplificada para gestionar flujos de trabajo de aprendizaje automático, incluyendo entrenamiento, evaluación, predicción, chat y exportación de modelos. Aquí una breve introducción a cada pestaña:

* **Train**: Esta pestaña te permite seleccionar un modelo y un conjunto de datos, configurar los parámetros de entrenamiento e iniciar el proceso de entrenamiento. Es esencial comprender los parámetros obligatorios y opcionales para optimizar la configuración de entrenamiento.
* **Evaluate & Predict**: Después del entrenamiento, puedes evaluar el rendimiento del modelo y realizar predicciones usando esta pestaña. Proporciona información sobre la precisión y efectividad del modelo con nuevos datos.
* **Chat**: Una vez finalizado el entrenamiento, carga el modelo en la pestaña Chat para interactuar con él y ver los resultados de tu trabajo. Esta función permite la comunicación en tiempo real con el modelo entrenado.
* **Export**: Esta pestaña facilita la exportación de modelos entrenados para su implementación o uso posterior. Puedes guardar tus modelos en varios formatos adecuados para diferentes aplicaciones.

Para obtener una guía detallada, te recomendamos consultar la documentación oficial en el [repositorio de GitHub de LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) y en [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Además, el [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) ofrece información valiosa sobre la interfaz y sus funcionalidades.

## Próximos pasos
- Prueba diferentes modelos como `gpt-oss` y otros modelos de última generación.
- Experimenta con diferentes backends en el modelo ajustado

Para más documentación, visita: https://llamafactory.readthedocs.io/en/latest/