<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Descripción general

Este playbook muestra cómo realizar un ajuste fino (fine-tuning) local de un modelo de lenguaje con Unsloth en hardware de AMD.

Utiliza un ejemplo breve de ajuste fino supervisado (Supervised Fine-Tuning, SFT) con adaptadores LoRA en `unsloth/gemma-4-E4B-it`, usando un subconjunto del dataset `mlabonne/FineTome-100k`. El objetivo es ofrecerte un flujo de trabajo simple de principio a fin que cubra la configuración, el entrenamiento, la inferencia y el guardado del resultado ajustado.

El ejemplo está diseñado para ser práctico y fácil de modificar, de modo que puedas usarlo como punto de partida para tus propios datasets y modelos.

## Qué aprenderás

- Cómo configurar el entorno de Unsloth
- Cómo ajustar finamente un LLM usando SFT con Unsloth
- Cómo guardar el resultado ajustado en almacenamiento local

<!-- @device:halo,stx,krk -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos **64 GB de RAM del sistema**, con al menos **24 GB disponibles para la GPU** (los 24 GB forman parte de los 64 GB, no se suman a ellos).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren al menos **24 GB de memoria total de GPU** y **32 GB de RAM del sistema**.
> - En Windows, la memoria total de GPU combina la VRAM dedicada de la tarjeta gráfica con la memoria de GPU compartida (tomada de la RAM del sistema).
> - Por lo tanto, las tarjetas con menos de 24 GB de VRAM dedicada aún pueden ejecutar este playbook utilizando memoria de GPU compartida para cubrir la diferencia.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Las técnicas de ajuste fino de este playbook requieren una tarjeta gráfica con al menos **24 GB de memoria de GPU dedicada** y **32 GB de RAM del sistema**.
> - En Linux, el entrenamiento se ejecuta completamente en la VRAM dedicada de la tarjeta gráfica.
> - No recurre a la memoria de GPU compartida (RAM del sistema) cuando se agota la VRAM.
> - Las tarjetas con menos de 24 GB de VRAM dedicada se quedarán sin memoria durante el entrenamiento en Linux, incluso si el sistema cuenta con abundante RAM.
<!-- @os:end -->
<!-- @device:end -->

## ¿Por qué Unsloth?

Unsloth facilita la ejecución del ajuste fino de LLM en hardware local al reducir el uso de memoria y acelerar el entrenamiento en comparación con una configuración estándar.

En este playbook, usamos Unsloth junto con **SFT basado en LoRA**. Esto significa que el modelo base permanece mayormente congelado, mientras que se entrena un conjunto mucho más pequeño de pesos de adaptadores. Esto resulta ideal para el desarrollo local, ya que es más liviano que el ajuste fino completo y permite iterar más rápido.

Unsloth también admite otros enfoques de entrenamiento, incluidos QLoRA y flujos de trabajo de aprendizaje por refuerzo. Este playbook se centra primero en el camino más simple: un pequeño ejemplo de ajuste fino con LoRA que los usuarios pueden ejecutar, comprender y ampliar.

<!-- @device:halo_box,halo,stx,krk -->
## Configuración de la memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software
> **Nota**: Si VS Code no está instalado, puedes instalarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de los requisitos previos de software

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Crear un entorno virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Abre una terminal y crea un venv con el software AMD ROCm™ y PyTorch ya instalados:
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
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Abre una terminal y crea un venv:
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

### Instalación de dependencias básicas
<!-- @require:driver -->

> **Importante:** Unsloth aún no es compatible con la versión de PyTorch 2.13 que viene con ROCm 10. Para este playbook, instala **ROCm 7.14 con PyTorch 2.12** usando los comandos a continuación. No uses los paquetes de ROCm 10 / PyTorch 2.13.

**Instala PyTorch con compatibilidad para el software AMD ROCm™** en el entorno virtual creado:

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

Para otros dispositivos, consulta la [documentación de ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) para obtener instrucciones completas.

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

### Dependencias adicionales

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

> **Nota:** Durante la importación, Unsloth puede probar rutas de aceleración opcionales de `bitsandbytes`. En algunas versiones de ROCm, es posible que veas un mensaje como `bitsandbytes library load error: Configured ROCm binary not found`. Este playbook utiliza ajuste fino LoRA estándar con `optim="adamw_torch"`, por lo que no dependemos del optimizador de `bitsandbytes` ni de QLoRA de 4 bits. Este mensaje se puede ignorar sin problema.

<!-- @os:windows -->
> **Nota:** En Windows ROCm, Unsloth imprimirá varias advertencias al iniciar; consulta [Advertencias conocidas](#known-warnings) a continuación. Todas son seguras de ignorar; el entrenamiento funciona correctamente.
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

## Descarga el script de ajuste fino de Unsloth

En lugar de ejecutar manualmente cada paso, este playbook ofrece un script limpio y completo aquí: [test_unsloth.py](assets/test_unsloth.py).

Ejecuta el siguiente código para correr el script:

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

## Cómo funciona

El script test_unsloth.py realiza los siguientes pasos:
* **Cargar modelo**: Carga unsloth/gemma-4-E4B-it usando FastModel.
* **Preparar datos**: Estandariza el dataset (p. ej., FineTome-100k) y aplica la plantilla de chat de Gemma-4.
* **Aplicar LoRA**: Agrega adaptadores a los módulos de lenguaje, atención y MLP para un entrenamiento eficiente.
* **Entrenar**: Usa SFTTrainer con enmascaramiento de pérdida solo en las respuestas.
* **Inferencia**: Ejecuta una prueba rápida de generación para verificar el rendimiento.
* **Guardar**: Exporta los adaptadores LoRA localmente.
## Configuración clave

Puede modificar las siguientes constantes para personalizar su ejecución:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Ejemplo del mensaje de bienvenida de Unsloth y la salida al cargar los pesos del modelo:

![alt text](assets/welcome.png)

## Preparar el conjunto de datos

Usamos un subconjunto de:
```text
mlabonne/FineTome-100k
```
El conjunto de datos es: 
* Convertido al formato de chat
* Procesado usando la plantilla de chat Gemma-4
* Limpiado para eliminar tokens BOS duplicados

## Entrenar el modelo

El script ejecuta una breve demostración de entrenamiento, con los siguientes parámetros:
- ~50 pasos
- Tamaño de lote pequeño
- Acumulación de gradiente

Durante el entrenamiento, verá registros como estos:

![alt text](assets/training.png)


## Guardado e implementación

### Guardado local (LoRA)

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

### Guardar modelo fusionado (para vLLM) 

<!-- @os:windows -->
> **Nota:** vLLM no es compatible con Windows. Para implementar su modelo ajustado en Windows, use llama.cpp (consulte [Exportar GGUF](#export-gguf-for-llamacpp) a continuación) o transfiera el modelo fusionado a una máquina Linux que ejecute vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Para la implementación con vLLM, fusione los adaptadores en un modelo completo:
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

Convierta directamente a GGUF para inferencia local:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Advertencias conocidas

Estas advertencias son impresas por Unsloth al iniciar en Windows ROCm y todas son seguras de ignorar:

| Advertencia | Razón | ¿Es seguro ignorarla? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes no tiene compilación para Windows ROCm | Sí — este playbook usa `adamw_torch`, no bnb |
| `No ROCm platform found for torch.distributed` | ROCm en Windows carece de entrenamiento distribuido | Sí — el entrenamiento con una sola GPU no se ve afectado |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth marca las compilaciones que no son de Linux | Sí — Windows ROCm funciona para SFT de una sola GPU |
| `triton is not available` | Triton no tiene compilación para Windows | Sí — Unsloth recurre a los kernels de PyTorch |

El entrenamiento continuará correctamente a pesar de estas advertencias.
<!-- @os:end -->

## Próximos pasos
- Pruebe [Unsloth Studio](https://unsloth.ai/docs/new/studio), una interfaz gráfica intuitiva para Unsloth
- Entrene con sus propios conjuntos de datos específicos
- Pruebe el ajuste fino con diferentes hiperparámetros
- Implemente con vLLM o llama.cpp
- Pruebe QLoRA para una configuración con menor uso de memoria

## Recursos

A continuación, se presentan algunos recursos adicionales para obtener más información sobre Unsloth y el ajuste fino:

* [Documentación de Unsloth](https://docs.unsloth.ai)

* [Unsloth en GitHub](https://github.com/unslothai/unsloth)

* [Guía de ajuste fino de Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)