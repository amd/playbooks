<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

O software AMD ROCm™ e o stack PyTorch criam um ecossistema unificado para IA no dispositivo. Funciona tanto para Windows quanto para Linux, com suporte oficial para uma ampla gama de dispositivos, incluindo APUs Ryzen™ AI e GPUs Radeon™.

Este playbook vai ensinar você a executar tradução de fala para fala com baixa latência, expressiva e privada, inteiramente no edge.

## O Que Você Vai Aprender

- Como configurar o ambiente de fala para fala
- Como escrever código Python para carregar e usar modelos de fala para fala
- Como executar e experimentar com a interface Gradio

## Por que usar tradução de fala para fala em tempo real?

- Remove atritos entre tradução e barreiras de idioma
- Transmite tom, emoção e intenção sem pausas estranhas
- Permite colaboração global e tomada de decisão mais rápida

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software
> **Nota**: Se o VS Code não estiver instalado, você pode instalá-lo com o Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

### Criar um Ambiente Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
No Linux, abra um terminal e execute o seguinte comando para criar um venv com ROCm+PyTorch já instalados:

<!-- @test:id=create-venv timeout=120 -->
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
**Conceda ao seu usuário acesso aos dispositivos GPU** (faça logout e login novamente para que isso tenha efeito):

```bash
sudo usermod -aG render,video $LOGNAME
```

No Linux, abra um terminal e execute o seguinte comando para criar um venv:

<!-- @test:id=create-venv timeout=120 -->
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
No Windows, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv com ROCm+PyTorch já instalados:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Dica**: Usuários do Windows podem precisar modificar sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
No Windows, abra um terminal no diretório de sua escolha e siga os comandos para criar um venv:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **Dica**: Usuários do Windows podem precisar modificar sua Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.

<!-- @device:end -->
<!-- @os:end -->

### Instalando Dependências Básicas

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Dependências Adicionais

Instale as dependências do m4t usando pip:
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


## Configurar a demonstração de fala para fala

#### Saiba mais sobre o seamless-m4t-v2

Confira o [model card](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) no Hugging Face para mais informações.
Esta é a arquitetura técnica dos modelos de fala para fala:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Baixar Scripts

Este playbook inclui scripts prontos para uso. Baixe todos eles no mesmo diretório do ambiente que você criou.

| Script | Descrição | Uso |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Geração básica de texto por LLM | `python infer.py` |
| [input1.wav](assets/input1.wav) | Arquivo de áudio de exemplo | N/A |
| [lang_list.py](assets/lang_list.py) | Arquivo de suporte a idiomas | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Interface intuitiva para tradução de fala | `python gradio_demo.py --no-share` |


### Começando com infer.py

Para executar o script, execute 
```bash
python infer.py
```
> **Nota**: Você pode ver alguns avisos. Isso é esperado.
 
  
#### Explicando o Código
**Trecho 1: Importando as dependências necessárias**

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

**Trecho 2: Carregando os modelos do HuggingFace**

Esta função recebe um ID de modelo e baixa o modelo caso ainda não tenha sido baixado. Em seguida, ela retorna o processador e o modelo para a próxima função usar.
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

**Trecho 3: Entrada de um clipe de áudio .wav e seu pré-processamento**

Esta função carrega o clipe de áudio e o reamostra para a taxa desejada.
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

Esta função executa a inferência com o modelo e retorna a saída gerada.
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

**Trecho 5: Salvar o arquivo traduzido**

Esta função salva o array de áudio em um arquivo .WAV. 
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

### Executando a demonstração da interface Gradio:

Agora que você executou um exemplo básico de script, as instruções a seguir fornecem uma interface útil que se baseia no código que escrevemos e facilita a tradução de fala para fala em tempo real.

#### Executar o Gradio Localmente

```bash
python ./gradio_demo.py --no-share
```
Em seguida, abra seu navegador em `http://127.0.0.1:7860` para acessar a interface.


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


## Próximos Passos

- Combine dezenas de idiomas para tradução rápida. 
- Compartilhe sua demonstração com outras pessoas: adicione --share para criar um link público que qualquer pessoa possa acessar remotamente, ou implante de forma permanente usando o Hugging Face Spaces

## Recursos

Abaixo estão alguns recursos adicionais para saber mais sobre tradução de fala para fala:  
* O repositório está aqui https://huggingface.co/facebook/seamless-m4t-v2-large 
* Pesquisa acadêmica relacionada a "Seamless: Multilingual Expressive and Streaming Speech Translation"
* Compartilhamento e implantação do Gradio: [Guia de Compartilhamento do Seu App](https://www.gradio.app/guides/sharing-your-app) e [Implantar no Hugging Face Spaces](https://shafiqulai.github.io/blogs/blog_5.html)