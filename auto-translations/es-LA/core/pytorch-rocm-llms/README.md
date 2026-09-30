<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Descripción general


¿Quieres ejecutar modelos de lenguaje de IA potentes en tu propio hardware? Esta guía te muestra cómo hacerlo.
Este tutorial usa PyTorch impulsado por el software AMD ROCm™ para ejecutar modelos que pueden resumir documentos, responder preguntas, generar texto y más, todo ejecutándose localmente.

## Lo que aprenderás

- Ejecutar LLM como gpt-oss-20b y qwen3.5-4B localmente usando PyTorch y ROCm
- Crear una herramienta de resumen de documentos usando LLM

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

### Crear un entorno virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
En Linux, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv con ROCm+Pytorch ya instalado.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Otorga a tu usuario acceso a los dispositivos GPU** (cierra sesión y vuelve a iniciarla para que esto surta efecto):

```bash
sudo usermod -aG render,video $LOGNAME
```

En Linux, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
En Windows, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv con ROCm+Pytorch ya instalado.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
En Windows, abre una terminal en el directorio de tu elección y sigue los comandos para crear un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Consejo**: Los usuarios de Windows podrían necesitar modificar su política de ejecución de PowerShell (por ejemplo,
> configurarla como RemoteSigned o Unrestricted) antes de ejecutar algunos comandos de Powershell.

<!-- @os:end -->

### Instalación de dependencias básicas
<!-- @require:driver,pytorch -->

### Instalación de dependencias adicionales

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Si el modelo no se carga o se queda sin memoria, intenta instalar el paquete `kernels` para cargar el modelo con cuantización optimizada.
>
> ```bash
> # Use this version which is compatible with the Transformers version
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Inicio rápido con scripts de ejemplo

Este playbook incluye scripts listos para usar. Haz clic en ellos para previsualizarlos y descargarlos en el mismo directorio que el entorno que creaste.

| Script | Descripción | Uso |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Generación básica de texto con LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Resumidor de documentos con soporte para Harmony | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Ambos scripts admiten:
- Selección de modelo mediante la opción `--model`
- Formateo de plantilla de chat para un correcto prompting del modelo, especialmente útil para el resumen de documentos

## Cargar y ejecutar tu primer LLM

El script incluido [run_llm.py](assets/run_llm.py) muestra cómo generar texto con LLM usando PyTorch y AMD ROCm.

> **Nota:** Cuando cargas un modelo, Hugging Face Transformers primero verifica su caché local (`~/.cache/huggingface/hub` en Linux, `C:\Users\<user>\.cache\huggingface\hub` en Windows). Si el modelo no está en caché, se descarga automáticamente desde huggingface.co. La primera ejecución puede tardar unos minutos dependiendo del tamaño del modelo y la velocidad de la red.

El siguiente fragmento muestra cómo usar el modelo y personalizar las preguntas realizadas.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Prueba el script descargado:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Creación de un resumidor de documentos

Ahora que has generado una salida de LLM local, puedes aprovechar eso creando un resumidor de documentos práctico. En esta sección, usarás el script [summarizer.py](assets/summarizer.py) para introducir un archivo .txt y generar automáticamente un resumen conciso, todo ejecutándose localmente en tu GPU.

El script está diseñado para funcionar de inmediato. Ábrelo en un editor para explorar el código, personalizar los prompts y ajustar parámetros como la longitud y la temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Ejemplos de uso

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Aprende sobre los parámetros de generación

| Parámetro | Qué controla | Valores típicos |
|-----------|------------------|----------------|
| `max_new_tokens` | La longitud máxima de la salida del LLM | Usa entre 50 y 500 tokens para resúmenes. (1 token equivale a aproximadamente 0.75 palabras en inglés) |
| `temperature` | Creatividad. Los valores bajos lo hacen enfocado, mientras que los valores altos generan mayor imprevisibilidad | - **0.1–0.3**: Enfocado, determinista (bueno para resúmenes) <br> **0.5–0.7**: Equilibrado (uso general) <br> **0.8–1.0**: Creativo, variado (lluvia de ideas) |
| `top_p` | Muestreo por núcleo (Nucleus Sampling): los valores bajos limitan al modelo a salidas más acotadas | **0.1-0.5**: Estricto, predecible <br> **0.9-0.95**: (estándar, natural, conversacional) |


## Aplicaciones en el mundo real

- **Análisis de artículos de investigación**: Extrae hallazgos clave de publicaciones complejas para una revisión rápida
- **Agregación de noticias**: Resume artículos de noticias en breves resúmenes diarios o destacados
- **Notas de reuniones**: Condensa transcripciones en elementos accionables y resúmenes concisos
- **Revisión de documentos legales**: Extrae rápidamente cláusulas u obligaciones relevantes de textos legales extensos
- **Documentación de código**: Genera descripciones generales concisas de repositorios y explicaciones de funciones
## Próximos pasos

- **Fine-tuning**: Adapta los modelos a tu campo o jerga específica para lograr mayor precisión (consulta las Guías de fine-tuning)
- **Sistemas RAG**: Combina LLMs con recuperación de documentos para obtener respuestas y búsquedas conscientes del contexto
- **Exploración de modelos**: Experimenta con nuevos modelos como Llama 3, Phi-3 o Qwen para obtener mejores resultados
- **Implementación en producción**: Usa herramientas como vLLM para el despliegue escalable de LLMs en organizaciones

Tu sistema te brinda el poder de ejecutar modelos de lenguaje sofisticados de forma local. Experimenta con diferentes modelos, prompts y parámetros para descubrir qué funciona mejor para tus aplicaciones.