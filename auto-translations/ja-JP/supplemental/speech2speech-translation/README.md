<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

AMD ROCm™ ソフトウェアと PyTorch スタックは、オンデバイス AI のための統合されたエコシステムを構築します。Windows と Linux の両方で動作し、Ryzen™ AI APU や Radeon™ GPU を含む幅広いデバイスを公式にサポートしています。

このプレイブックでは、低レイテンシで表現力豊かなプライベートな音声対音声翻訳を、エッジ上で完結させて実行する方法を学びます。

## このプレイブックで学べること

- 音声対音声環境のセットアップ方法
- 音声対音声モデルを読み込んで使用するための Python コードの書き方
- Gradio UI の実行と実験の方法

## リアルタイム音声対音声翻訳を使用する理由

- 翻訳と言語の壁の間にある摩擦を取り除く
- ぎこちない間を取ることなく、トーン、感情、意図を伝える
- グローバルなコラボレーションとより迅速な意思決定を可能にする

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

### 仮想環境の作成

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux では、ターミナルを開き、以下のプロンプトを実行して、ROCm+PyTorch がすでにインストールされた venv を作成します。

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
**ユーザーに GPU デバイスへのアクセス権を付与します**（これを有効にするには、いったんログアウトして再度ログインしてください）:

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux では、ターミナルを開き、以下のプロンプトを実行して venv を作成します。

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
Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って、ROCm+PyTorch がすでにインストールされた venv を作成します。

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell 実行ポリシーを変更する必要がある場合があります（例: RemoteSigned または Unrestricted に設定する）。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell 実行ポリシーを変更する必要がある場合があります（例: RemoteSigned または Unrestricted に設定する）。

<!-- @device:end -->
<!-- @os:end -->

### 基本的な依存関係のインストール

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### 追加の依存関係

pip を使用して m4t の依存関係をインストールします:
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


## 音声対音声デモのセットアップ

#### seamless-m4t-v2 について学ぶ

詳細については、Hugging Face の[モデルカード](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main)をご覧ください。
以下は音声対音声モデルの技術アーキテクチャです:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### スクリプトのダウンロード

このプレイブックには、すぐに使用できるスクリプトが含まれています。これらすべてを、作成した環境と同じディレクトリにダウンロードしてください。

| スクリプト | 説明 | 使用方法 |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | 基本的な LLM テキスト生成 | `python infer.py` |
| [input1.wav](assets/input1.wav) | サンプル音声ファイル | N/A |
| [lang_list.py](assets/lang_list.py) | 言語サポートファイル | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | 音声翻訳のための直感的な UI | `python gradio_demo.py --no-share` |


### infer.py から始める

スクリプトを実行するには、以下を実行してください: 
```bash
python infer.py
```
> **注**: 警告が表示されることがありますが、これは想定内です。
 
  
#### コードの説明
**スニペット 1: 必要な依存関係をインポートする**

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

**スニペット 2: HuggingFace からモデルを読み込む**

この関数はモデル ID を受け取り、まだダウンロードされていない場合はモデルをダウンロードします。次に、次の関数で使用するためのプロセッサとモデルを返します。
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

**スニペット 3: 入力音声クリップの .wav ファイルを読み込み前処理する**

この関数は音声クリップを読み込み、対象のサンプルレートにリサンプリングします。
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

**スニペット 4: 推論の実行**

この関数はモデルで推論を実行し、生成された出力を返します。
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

**スニペット 5: 翻訳されたファイルを保存する**

この関数は音声配列を .WAV ファイルに保存します。
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

### Gradio UI デモの実行:

基本的なスクリプトの例を実行したところで、以下の手順では、これまでに書いたコードをベースにしたわかりやすい UI を使用して、ライブの音声対音声翻訳を簡単に行う方法を説明します。

#### Gradio をローカルで実行する

```bash
python ./gradio_demo.py --no-share
```
次に、Web ブラウザで `http://127.0.0.1:7860` を開き、UI にアクセスします。


### Gradio UI の例:

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


## 次のステップ

- 数十種類の言語を組み合わせて、素早く翻訳を行いましょう。
- デモを他の人と共有する: --share を追加すると、誰でもリモートでアクセスできる公開リンクを作成できます。また、Hugging Face Spaces を使用して永続的にデプロイすることもできます。

## リソース

音声対音声翻訳についてさらに詳しく学ぶための追加リソースを以下に示します:
* リポジトリはこちらです https://huggingface.co/facebook/seamless-m4t-v2-large
* 「Seamless: Multilingual Expressive and Streaming Speech Translation」に関連する研究論文
* Gradio の共有とデプロイ: [アプリの共有ガイド](https://www.gradio.app/guides/sharing-your-app) および [Hugging Face Spaces へのデプロイ](https://shafiqulai.github.io/blogs/blog_5.html)