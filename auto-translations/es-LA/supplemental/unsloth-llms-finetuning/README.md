<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa etiquetas especiales que GitHub no puede renderizar. Visita [amd.com/playbooks](https://amd.com/playbooks) para previsualizar correctamente este contenido.
<!-- @github-only:end -->

## Descripción general

Este playbook muestra cómo ajustar (fine-tune) un modelo de lenguaje localmente con Unsloth en hardware AMD.

Utiliza un breve ejemplo de ajuste fino supervisado (Supervised Fine-Tuning, SFT) con adaptadores LoRA en `unsloth/gemma-4-E4B-it`, usando un subconjunto del conjunto de datos `mlabonne/FineTome-100k`. El objetivo es brindarte un flujo de trabajo simple de extremo a extremo que cubra la configuración, el entrenamiento, la inferencia y el guardado del resultado ajustado.

El ejemplo está diseñado para ser práctico y fácil de modificar, de modo que puedas usarlo como punto de partida para tus propios conjuntos de datos y modelos.

## Qué aprenderás

- Cómo configurar el entorno de Unsloth
- Cómo ajustar un LLM usando SFT con Unsloth
- Cómo guardar el resultado ajustado en almacenamiento local

<!-- @device:halo,stx,krk -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos 24 GB de memoria de GPU y 32 GB de RAM del sistema.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos 24 GB de memoria de GPU y 32 GB de RAM del sistema.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos 24 GB de memoria **dedicada** de GPU y 32 GB de RAM del sistema.
<!-- @os:end -->
<!-- @device:end -->

## ¿Por qué Unsloth?

Unsloth facilita la ejecución del ajuste fino de LLM en hardware local al reducir el uso de memoria y acelerar el entrenamiento en comparación con una configuración estándar.

En este playbook, usamos Unsloth junto con **SFT basado en LoRA**. Esto significa que el modelo base permanece mayormente congelado, mientras que se entrena un conjunto mucho más pequeño de pesos de adaptadores. Esto es adecuado para el desarrollo local porque es más liviano que el ajuste fino completo y más rápido de iterar.

Unsloth también admite otros enfoques de entrenamiento, incluyendo QLoRA y flujos de trabajo de aprendizaje por refuerzo. Este playbook se enfoca primero en el camino más simple: un pequeño ejemplo de ajuste fino con LoRA que los usuarios pueden ejecutar, entender y extender.

## Configurando la Configuración de Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Actualizaciones de Software
> **Nota**: Si VS Code no está instalado, puedes instalarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de Requisitos Previos de Software

### Crear un Entorno Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Abre una terminal y crea un venv con el software AMD ROCm™ y PyTorch ya instalados:
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
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Abre una terminal y crea un venv:
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
> **Nota:** Se requiere Python 3.13 para Windows.

<!-- @device:halo_box -->
Abre una terminal de PowerShell y crea un entorno virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Abre una terminal de PowerShell y crea un entorno virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalación de Dependencias Básicas
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

### Dependencias Adicionales

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

> **Nota:** Durante la importación, Unsloth puede sondear rutas de aceleración opcionales de `bitsandbytes`. En algunas versiones de ROCm, es posible que veas un mensaje como `bitsandbytes library load error: Configured ROCm binary not found`. Este playbook utiliza ajuste fino LoRA estándar con `optim="adamw_torch"`, por lo que no dependemos del optimizador `bitsandbytes` ni de QLoRA de 4 bits. Este mensaje se puede ignorar sin problema.

<!-- @os:windows -->
> **Nota:** En Windows ROCm, Unsloth imprimirá varias advertencias al inicio; consulta [Advertencias Conocidas](#known-warnings) más abajo. Todas se pueden ignorar sin problema; el entrenamiento funciona correctamente.
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

## Descargar el Script de Ajuste Fino de Unsloth

En lugar de ejecutar manualmente cada paso, este playbook proporciona un script limpio de extremo a extremo aquí: [test_unsloth.py](assets/test_unsloth.py).

Ejecuta el siguiente código para ejecutar el script:

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

El resto del playbook recorrerá conceptualmente cada paso principal del script. 

## Cómo Funciona

El script test_unsloth.py realiza los siguientes pasos:
* **Cargar Modelo**: Carga unsloth/gemma-4-E4B-it usando FastModel.
* **Preparar Datos**: Estandariza el conjunto de datos (por ejemplo, FineTome-100k) y aplica la plantilla de chat de Gemma-4.
* **Aplicar LoRA**: Agrega adaptadores a los módulos de lenguaje, atención y MLP para un entrenamiento eficiente.
* **Entrenar**: Usa SFTTrainer con enmascaramiento de pérdida solo en la respuesta.
* **Inferencia**: Ejecuta una prueba de generación rápida para verificar el rendimiento.
* **Guardar**: Exporta los adaptadores LoRA localmente.

## Configuración Clave

Puedes modificar las siguientes constantes para personalizar tu ejecución:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Ejemplo del mensaje de bienvenida de Unsloth y la salida al cargar los pesos del modelo:

![alt text](assets/welcome.png)

## Preparar el Conjunto de Datos

Usamos un subconjunto de:
```text
mlabonne/FineTome-100k
```
El conjunto de datos es: 
* Convertido a formato de chat
* Procesado usando la plantilla de chat de Gemma-4
* Limpiado para eliminar tokens BOS duplicados

## Entrenar el Modelo

El script ejecuta una breve demostración de entrenamiento, con los siguientes parámetros:
- ~50 pasos
- Tamaño de lote pequeño
- Acumulación de gradiente

Durante el entrenamiento, verás registros como los siguientes:

![alt text](assets/training.png)


## Guardado e Implementación

### Guardado Local (LoRA)

El script guarda automáticamente los adaptadores LoRA en el OUTPUT_DIR.
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
> **Nota:** vLLM no admite Windows. Para implementar tu modelo ajustado en Windows, usa llama.cpp (consulta [Exportar GGUF](#export-gguf-for-llamacpp) más abajo) o transfiere el modelo combinado a una máquina Linux que ejecute vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Para la implementación con vLLM, combina los adaptadores en un modelo completo:
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

Convierte directamente a GGUF para inferencia local:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Advertencias conocidas

Estas advertencias son impresas por Unsloth al iniciar en Windows ROCm y todas son seguras de ignorar:

| Advertencia | Motivo | ¿Segura de ignorar? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes no tiene una compilación para Windows ROCm | Sí — este playbook usa `adamw_torch`, no bnb |
| `No ROCm platform found for torch.distributed` | ROCm en Windows carece de entrenamiento distribuido | Sí — el entrenamiento con una sola GPU no se ve afectado |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth marca las compilaciones que no son de Linux | Sí — Windows ROCm funciona para SFT de una sola GPU |
| `triton is not available` | Triton no tiene una compilación para Windows | Sí — Unsloth recurre a los kernels de PyTorch |

El entrenamiento continuará correctamente a pesar de estas advertencias.
<!-- @os:end -->

## Próximos pasos
- Prueba [Unsloth Studio](https://unsloth.ai/docs/new/studio), una interfaz gráfica intuitiva para Unsloth
- Entrena con tus propios conjuntos de datos específicos
- Prueba el ajuste fino con diferentes hiperparámetros
- Implementa con vLLM o llama.cpp
- Prueba QLoRA para una configuración con menor uso de memoria

## Recursos

A continuación se presentan algunos recursos adicionales para aprender más sobre Unsloth y el ajuste fino:

* [Documentación de Unsloth](https://docs.unsloth.ai)

* [Unsloth en GitHub](https://github.com/unslothai/unsloth)

* [Guía de ajuste fino de Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)