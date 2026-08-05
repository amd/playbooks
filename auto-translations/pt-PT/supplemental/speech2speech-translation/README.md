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

## Visão geral

O software AMD ROCm™ e a stack PyTorch criam um ecossistema unificado para IA no dispositivo. Funciona tanto em Windows como em Linux, com suporte oficial para uma vasta gama de dispositivos, incluindo APUs Ryzen™ AI e GPUs Radeon™.

Este manual vai ensinar-lhe como executar tradução voz-para-voz de baixa latência, expressiva e privada, inteiramente na periferia (edge).

## O que vai aprender

- Como configurar o ambiente de voz-para-voz
- Como escrever código Python para carregar e utilizar modelos de voz-para-voz
- Como executar e experimentar a interface Gradio

## Porquê utilizar tradução voz-para-voz em tempo real?

- Elimina o atrito entre a tradução e as barreiras linguísticas
- Transmite tom, emoção e intenção sem pausas estranhas
- Permite colaboração global e tomada de decisões mais rápida

## Configuração da memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar atualizações de software
> **Nota**: Se o VS Code não estiver instalado, pode instalá-lo através do Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalação dos pré-requisitos de software

### Criar um ambiente virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
No Linux, abra um terminal e execute o seguinte comando para criar um venv com o ROCm+Pytorch já instalado:

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env --system-site-packages
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Conceda ao seu utilizador acesso aos dispositivos GPU** (termine e reinicie sessão para que isto tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

No Linux, abra um terminal e execute o seguinte comando para criar um venv:

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv s2st-env
source s2st-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source s2st-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv com o ROCm+Pytorch já instalado:

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Dica**: Os utilizadores de Windows podem precisar de modificar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
No Windows, abra um terminal no diretório à sua escolha e siga os comandos para criar um venv:

<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Dica**: Os utilizadores de Windows podem precisar de modificar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @device:end -->
<!-- @os:end -->

### Instalação das dependências básicas

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Dependências adicionais

Instale as dependências do m4t utilizando o pip:
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 tiktoken==0.9.0 accelerate soundfile==0.13.1 sentencepiece protobuf gradio scipy==1.15.3 
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=300 setup=activate-venv hidden=True -->
```python
import importlib
import os
import sys

# Ensure local assets directory is importable
sys.path.insert(0, os.getcwd())

modules = [
    "torch",
    "torchaudio",
    "scipy",
    "soundfile",
    "gradio",
    "transformers",
    "safetensors",
    "sentencepiece",
    "accelerate",
    "tiktoken",
]

for module in modules:
    importlib.import_module(module)
    print(f"PASS: imported {module}")

from transformers import AutoProcessor, SeamlessM4Tv2Model
import lang_list
from lang_list import LANGUAGE_NAME_TO_CODE, ASR_TARGET_LANGUAGE_NAMES, S2ST_TARGET_LANGUAGE_NAMES

assert "English" in LANGUAGE_NAME_TO_CODE, "FAIL: English missing in LANGUAGE_NAME_TO_CODE"
assert len(S2ST_TARGET_LANGUAGE_NAMES) > 0, "FAIL: S2ST_TARGET_LANGUAGE_NAMES is empty"

print("PASS: imported local module lang_list")
print("PASS: key speech2speech imports work")
```
<!-- @test:end -->

<!-- @test:id=verify-scripts timeout=60 hidden=True -->
```python
import ast
import os
import sys

required_files = [
    "infer.py",
    "gradio_demo.py",
    "lang_list.py",
    "input1.wav",
]

missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: All required files exist")

for script in ["infer.py", "gradio_demo.py", "lang_list.py"]:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->


## Configurar a demonstração voz-para-voz

#### Saiba mais sobre o seamless-m4t-v2

Consulte a [ficha do modelo](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) no Hugging Face para mais informações.
Esta é a arquitetura técnica dos modelos voz-para-voz:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Transferir os scripts

Este manual inclui scripts prontos a utilizar. Transfira todos para o mesmo diretório do ambiente que criou.

| Script | Descrição | Utilização |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Geração básica de texto por LLM | `python infer.py` |
| [input1.wav](assets/input1.wav) | Ficheiro de áudio de exemplo | N/A |
| [lang_list.py](assets/lang_list.py) | Ficheiro de suporte de idiomas | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Interface intuitiva para tradução de voz | `python gradio_demo.py --no-share` |


### Começar com infer.py

Para executar o script, execute 
```bash
python infer.py
```
> **Nota**: Poderá ver alguns avisos. Isto é esperado.
 
  
#### Explicação do código
**Trecho 1: Importar as dependências necessárias**

```python 
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"

import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio

from transformers import AutoProcessor, SeamlessM4Tv2Model

# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"

INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"

# Automatically downloads + caches via Hugging Face
MODEL_ID = "facebook/seamless-m4t-v2-large"

TARGET_SAMPLE_RATE = 16_000
```

**Trecho 2: Carregar os modelos a partir do HuggingFace**

Esta função recebe um ID de modelo e transfere o modelo caso ainda não esteja transferido. De seguida, devolve o processador e o modelo para a próxima função utilizar.
```python
def load_model(model_id: str, device: torch.device):
    start = time.time()

    print("Loading model (downloads automatically on first run)...")

    processor = AutoProcessor.from_pretrained(model_id)

    dtype = torch.float16 if device.type == "cuda" else torch.float32

    model = SeamlessM4Tv2Model.from_pretrained(model_id, torch_dtype=dtype).to(device)

    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")

    return processor, model
```

**Trecho 3: Introduzir o clipe de áudio .wav e pré-processá-lo**

Esta função carrega o clipe de áudio e reamostra-o para a taxa pretendida.
```python
def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:

    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)

    # Convert to tensor [channels, samples]
    audio = torch.from_numpy(audio_np.T)

    # Resample if needed
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    # Convert stereo -> mono
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio
```

**Trecho 4: Executar a inferência**

Esta função executa a inferência com o modelo e devolve o resultado gerado.
```python
def run_inference(model, processor, audio: torch.Tensor, device: torch.device, target_lang: str = DEFAULT_TARGET_LANGUAGE):

    start = time.time()

    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    audio_inputs = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in audio_inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]

    audio_array = output.float().cpu().numpy().squeeze()

    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed
```

**Trecho 5: Guardar o ficheiro traduzido**

Esta função guarda o array de áudio num ficheiro .WAV. 
```python
def save_audio(audio_array: np.ndarray, output_path: str, sample_rate: int):
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0

        if max_abs > 1.0:
            audio_array = audio_array / max_abs

        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)

    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

    print(f"Output saved to: {output_path}")
```

<!-- @os:windows -->
<!-- @test:id=infer-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
Remove-Item .\out1.wav -Force -ErrorAction SilentlyContinue

if (-not (Test-Path .\input1.wav)) { throw "FAIL: input1.wav not found in current directory" }

python .\infer.py
if ($LASTEXITCODE -ne 0) { throw "infer.py failed" }

if (-not (Test-Path .\out1.wav)) { throw "FAIL: out1.wav was not created" }
$file = Get-Item .\out1.wav
if ($file.Length -le 0) { throw "FAIL: out1.wav is empty" }

Write-Host "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=infer-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail
rm -f ./out1.wav

if [ ! -f ./input1.wav ]; then
  echo "FAIL: input1.wav not found in current directory"
  exit 1
fi

python ./infer.py

if [ ! -f ./out1.wav ]; then
  echo "FAIL: out1.wav was not created"
  exit 1
fi
if [ ! -s ./out1.wav ]; then
  echo "FAIL: out1.wav is empty"
  exit 1
fi

echo "PASS: infer.py created out1.wav successfully"
```
<!-- @test:end --> 
<!-- @os:end -->

### Executar a demonstração da interface Gradio:

Agora que executou um exemplo de script básico, as instruções seguintes fornecem uma interface útil que se baseia no código que escrevemos e facilita a tradução voz-para-voz em direto.

#### Executar o Gradio localmente

```bash
python ./gradio_demo.py --no-share
```
Em seguida, abra o seu navegador web em `http://127.0.0.1:7860` para aceder à interface.


### Exemplo de interface Gradio:

<p align="center">
  <img src="assets/gradio.png" alt="gradio UI" width="600"/>
</p>

<!-- @os:windows -->
<!-- @test:id=gradio-ui-smoke-windows timeout=1800 setup=activate-venv hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
'@

$tempPy = Join-Path $env:TEMP "gradio_ui_smoke_ci.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy

if ($LASTEXITCODE -ne 0) {
  Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
  throw "gradio UI smoke test failed"
}

Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=gradio-ui-smoke-linux timeout=1800 setup=activate-venv hidden=True -->
```bash
set -euo pipefail

python - <<'PY'
import os
import sys
import gradio as gr

# Ensure current directory is importable so lang_list.py can be imported
sys.path.insert(0, os.getcwd())

import gradio_demo

called = {}

def fake_launch(self, *args, **kwargs):
    called["args"] = args
    called["kwargs"] = kwargs
    print(f"PASS: launch called with kwargs={kwargs}")
    return self

orig_launch = gr.Blocks.launch

def fake_runner(input_audio, target_language):
    return None, "OK"

try:
    demo = gradio_demo.build_ui(fake_runner)
    print(f"PASS: build_ui(fake_runner) returned {type(demo).__name__}")

    gr.Blocks.launch = fake_launch
    sys.argv = ["gradio_demo.py", "--no-share"]
    gradio_demo.main()

    kwargs = called.get("kwargs", {})
    assert kwargs.get("server_name") == "127.0.0.1", "FAIL: unexpected server_name"
    assert kwargs.get("server_port") == 7860, "FAIL: unexpected server_port"
    assert kwargs.get("share") is False, "FAIL: expected share=False by default/--no-share"

    print("PASS: gradio_demo main() reached launch() with expected settings")
finally:
    gr.Blocks.launch = orig_launch
PY
```
<!-- @test:end --> 
<!-- @os:end -->


## Próximos passos

- Combine e experimente dezenas de idiomas para tradução rápida. 
- Partilhe a sua demonstração com outras pessoas: Adicione --share para criar uma ligação pública que qualquer pessoa possa aceder remotamente, ou implemente de forma permanente utilizando o Hugging Face Spaces

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre tradução voz-para-voz:  
* O repositório está aqui https://huggingface.co/facebook/seamless-m4t-v2-large 
* Investigação académica relacionada com "Seamless: Multilingual Expressive and Streaming Speech Translation"
* Partilha e implementação do Gradio: [Guia de partilha da sua aplicação](https://www.gradio.app/guides/sharing-your-app) e [Implementar no Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)