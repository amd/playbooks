<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Descripción general

Este tutorial proporciona ejemplos paso a paso para el ajuste fino de un modelo de lenguaje grande (LLM) con PyTorch y ROCm. Cubre varias técnicas, desde el ajuste fino estándar hasta estrategias de ajuste fino eficiente en parámetros (PEFT) con uso eficiente de memoria, para que puedas adaptar modelos fácilmente según tus necesidades.

**Modelo utilizado**: google/gemma-3-4b-it  *(consulta [Habilitar autenticación de HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) si está restringido)*  
**Hardware**: AMD Radeon™ GPU con soporte ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Nota:** También puedes probar otras arquitecturas de modelos, incluido **GPT-OSS-20B**, sustituyendo el modelo en los scripts de entrenamiento proporcionados.
> El ajuste fino completo requiere al menos 32 GB de memoria GPU y 64 GB de RAM del sistema.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Nota:** El ajuste fino con LoRA y QLoRA requiere al menos 16 GB de memoria GPU y 32 GB de RAM del sistema.
<!-- @device:end -->

## Lo que aprenderás

- Cómo realizar el ajuste fino de un LLM usando LoRA, QLoRA y ajuste fino completo con PyTorch y ROCm
- Cómo guardar e implementar tu modelo con ajuste fino
- Cómo monitorear el entrenamiento y depurar problemas comunes

## Configuración de la memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar actualizaciones de software
> **Nota**: Si VS Code no está instalado, puedes instalarlo con el Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalación de requisitos previos de software

#### Crear un entorno virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Instalación de dependencias básicas
<!-- @require:pytorch -->

#### Dependencias adicionales

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Aquí solo se prueban y admiten los paquetes principales. **bitsandbytes no está bien soportado en Windows**, por lo que la instalación en Windows lo omite; usa LoRA o ajuste fino completo en Windows (QLoRA requiere bitsandbytes y está pensado para Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Habilitar autenticación de HF (modelos restringidos, personalizados o no preinstalados)

En este ejemplo usamos **google/gemma-3-4b-it**, que es un modelo **restringido**. Debes aceptar los términos del modelo en Hugging Face y luego autenticarte para que los scripts de entrenamiento puedan descargarlo.

1. **Acepta la licencia:** Abre [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), inicia sesión (o crea una cuenta) y acepta la licencia/términos en la página del modelo (por ejemplo, "Agree and access repository").
2. **Instala e inicia sesión:** Instala la CLI de Hugging Face y luego ejecuta el inicio de sesión estándar:

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

## Comprensión de las técnicas

### ¿Qué es LoRA?

**LoRA (Low-Rank Adaptation)** mantiene el modelo base congelado y solo entrena pequeñas matrices "adaptadoras" que se agregan a ciertas capas.

- **La idea clave**: en lugar de actualizar una enorme matriz de pesos con millones de parámetros, aprendemos una actualización de bajo rango (dos matrices pequeñas cuyo producto tiene muchos menos parámetros). Esto proporciona una gran reducción en los parámetros entrenables y en la VRAM, manteniendo la mayor parte de la calidad del ajuste fino completo.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### ¿Qué es QLoRA?

**QLoRA** combina **cuantización de 4 bits** con **LoRA**. El modelo base se carga en 4 bits (gran ahorro de memoria) y solo los adaptadores LoRA se entrenan con mayor precisión. Así obtienes la eficiencia de parámetros de LoRA más una VRAM mucho menor, con una pequeña pérdida de calidad en comparación con LoRA de precisión completa. Ten en cuenta que la cuantización de 4 bits puede causar inestabilidades numéricas (picos de pérdida o NaNs), por lo que los usuarios pueden preferir **LoRA** si disponen de suficiente VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Nota**: Para modelos base MXFP4 como `openai/gpt-oss-20b`, recomendamos usar **LoRA** (`train_lora.py`) en lugar de QLoRA. La ruta de 4 bits de `bitsandbytes` en el script QLoRA típicamente descuantiza los pesos MXFP4 a BF16, por lo que la ejecución se comporta como LoRA estándar. MXFP4 nativo requiere `bitsandbytes` compilado desde el código fuente más una pila compatible de Transformers/Triton/kernels. Consulta la [documentación de Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Elige tu método

| Método | Memoria | Velocidad | Calidad | Ideal para |
|--------|--------|-------|---------|----------|
| **QLoRA** (solo Linux) | 12-16GB | Más rápido | 90-95% | Uso de memoria reducido |
| **LoRA** | 24-32GB | Rápido | 95-98% | Enfoque equilibrado |
| **Completo** | 80GB+ | Más lento | 100% | Máxima calidad |

### 3. Ejecutar el entrenamiento

**Dataset y lo que aprende el modelo**  
Los scripts convierten el dataset en ejemplos de chat. Por ejemplo, el script QLoRA usa **Abirate/english_quotes**: cada ejemplo se convierte en un par usuario–asistente como:

- **Usuario:** "Dame una cita sobre: &lt;etiqueta&gt;"
- **Asistente:** "&lt;cita&gt; – &lt;autor&gt;"

El ajuste fino enseña al modelo a responder a indicaciones que solicitan citas sobre un tema y a devolverlas en el formato `<texto de la cita> - <autor>`. Los scripts de LoRA y ajuste fino completo usan **databricks/databricks-dolly-15k** (pares generales de instrucción/respuesta), por lo que la tarea exacta varía según el script; la idea es la misma: adaptar el modelo a tu dataset y formato elegidos.

A continuación se muestra un resumen de los métodos de entrenamiento disponibles. Cada método enlaza a su script y proporciona una breve descripción para elegir el enfoque adecuado.

| Script                           | Método            | Descripción                                                                                                         | VRAM típica | Recomendado para                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Entrena pequeñas matrices adaptadoras mientras congela el modelo base. 3–5x más rápido; ~95–98% de la calidad completa.                         | 24–32GB      | Usuarios avanzados; múltiples adaptadores; más VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(solo Linux)*             | **QLoRA**       | Cuantización de 4 bits + adaptadores LoRA. Menor uso de memoria, más rápido, pequeña pérdida de calidad. Requiere `bitsandbytes` (solo Linux).                            | 12–16GB      | La mayoría de usuarios; experimentos rápidos; VRAM limitada      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Ajuste fino completo** | Actualiza todos los parámetros del modelo. Máxima calidad; mayor uso de memoria y cómputo.                                    | 40GB+        | Máxima calidad; investigación; VRAM grande           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** El ajuste fino completo (`train_full_finetuning.py`) puede requerir más de 64 GB de RAM del sistema y puede no ser viable en este dispositivo. Considera usar LoRA o QLoRA en su lugar.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** El ajuste fino completo (`train_full_finetuning.py`) puede requerir más de 64 GB de RAM del sistema y puede no ser viable en este dispositivo. Considera usar LoRA en su lugar.
<!-- @os:end -->
<!-- @device:end -->

Simplemente selecciona tu `Método de entrenamiento` preferido, descarga el script correspondiente y ejecútalo con el siguiente comando manteniendo tu entorno virtual activado:

```python
python3 train_<method_name>.py.
```

## Uso de tu modelo con ajuste fino

### Después del ajuste fino completo

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

### Después del entrenamiento con LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Fusionar el adaptador LoRA en el modelo base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Nota:**  
- Asegúrate de que el nombre del directorio del modelo (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) coincida con tu carpeta de salida real del entrenamiento.  
- Si usaste LoRA en lugar de QLoRA, simplemente sustituye la ruta según corresponda.  
- Algunos modelos Gemma requieren especificar `trust_remote_code=True` en `from_pretrained`; agrégalo si ves una advertencia relacionada.

Para configuraciones más personalizadas (tokens de relleno, dispositivo, etc.), consulta el script que usaste para el entrenamiento.

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guía de personalización

### Usa tu propio dataset

Todos los scripts usan el mismo formato de dataset. Reemplaza la sección de carga:

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

**Formato de dataset para archivo JSON/JSONL local:**

Al usar este método, asegúrate de que tus archivos JSON estén correctamente estructurados para evitar errores de análisis.

Se deben seguir las siguientes pautas:
* **Formato del archivo:** Los archivos JSON deben formatearse dentro de un Entorno de Desarrollo Integrado (IDE) para garantizar una estructura y sintaxis correctas.
* **Claves requeridas:** El archivo JSON personalizado debe contener las claves `instruction` y `response`. Estas claves son esenciales para que el método funcione correctamente.
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
**Formato de dataset para dataset de Hugging Face Hub**

Al utilizar datasets de Hugging Face, asegúrate de que tus datasets estén estructurados correctamente para facilitar una integración fluida.

Se deben seguir las siguientes pautas:
* **Par instrucción-respuesta:** Enfócate en datasets que incluyan un par `instruction-response`. Esta estructura es esencial para la funcionalidad prevista.
* **Modificación de claves personalizadas:** Si tu dataset no se ajusta a la estructura `instruction-response`, tienes la opción de modificar la función `format_instruction()`. Esto te permite acomodar claves específicas según sea necesario.

Ejemplo de ajuste: En los casos en que la salida del dataset necesite ajustarse, puedes modificar la sección de respuesta dentro de la función `format_instruction()` para adaptarla a tus requisitos.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formato de dataset para archivo CSV**

Para adaptar el script al uso de un archivo CSV, debes asegurarte de que el archivo CSV contenga columnas llamadas `instruction` y `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Ajustar los parámetros de entrenamiento

Edita el script de entrenamiento y cambia las variables para que coincidan con tus objetivos: **tasa de aprendizaje** (`LR`), **épocas** (`EPOCHS`), **tamaño de lote** (`BATCH_SIZE`), **acumulación de gradientes** (`GRAD_ACCUM_STEPS`), y para LoRA/QLoRA el **rango** (`LORA_R`). Para ejecuciones más rápidas usa menos épocas y una tasa de aprendizaje (LR) más alta; para mejor calidad usa más épocas y una LR más baja. Reduce el tamaño de lote o la longitud de secuencia si encuentras errores de memoria insuficiente.

### Consejos para optimización de memoria

Si encuentras errores de memoria insuficiente:

**1. Reducir el tamaño de lote:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reducir la longitud de secuencia:**
```python
max_seq_length=256  # Instead of 512
```

**3. Usar cuantización más agresiva:**
```
Full → LoRA → QLoRA
```

**4. Habilitar la verificación de gradientes (solo ajuste fino completo):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoreo y depuración

### Observar la memoria GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcional) Rastrear experimentos con Weights & Biases

Para registrar ejecuciones y métricas en [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

En el script de entrenamiento, establece `report_to="wandb"` y opcionalmente `run_name="your-experiment-name"` en la configuración del entrenador. Si prefieres no usar Wandb, deja `report_to` en su valor predeterminado o establécelo en `"none"`.

### Problemas comunes

#### Memoria insuficiente (OOM)

**Solución:** Reduce el tamaño de lote y/o usa QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### La pérdida no disminuye

**Solución:** Ajusta la tasa de aprendizaje
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Entrenamiento lento

**Solución:** Aumenta el tamaño de lote si la memoria lo permite
```python
BATCH_SIZE = 8
```
## Próximos pasos

Después de completar exitosamente el ajuste fino, considera los siguientes pasos para aprovechar más tu modelo:

1. **Evalúa** exhaustivamente con datos de prueba reservados para medir la generalización y evitar el sobreajuste.
2. **Experimenta** probando diferentes valores de hiperparámetros para obtener mejores compromisos entre precisión, velocidad y memoria.
3. **Registra** todos tus experimentos (y las métricas correspondientes) con Weights & Biases para una investigación reproducible.
4. **Prueba** el entrenamiento con tus propios datasets personalizados para adaptar el modelo específicamente a tu caso de uso.
5. **Implementa** tu modelo con ajuste fino para inferencia rápida usando backends eficientes como vLLM en hardware compatible.
6. **Explora** técnicas avanzadas que incluyen ingeniería de prompts, precisión mixta y longitudes de secuencia más largas.
7. **Entrena** múltiples adaptadores LoRA para diferentes tareas o dominios e intercámbialos según sea necesario.

---