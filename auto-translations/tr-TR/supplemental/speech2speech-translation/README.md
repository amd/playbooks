<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

## Genel Bakış

AMD ROCm™ yazılımı ve PyTorch yığını, cihaz üzerinde yapay zeka için birleşik bir ekosistem oluşturur. Ryzen™ AI APU'lar ve Radeon™ GPU'lar dahil geniş bir cihaz yelpazesi için resmi destekle hem Windows hem de Linux'ta çalışır.

Bu playbook, düşük gecikmeli, etkileyici ve gizli konuşmadan konuşmaya çeviriyi tamamen uç noktada nasıl çalıştıracağınızı öğretecektir.

## Neler Öğreneceksiniz

- Konuşmadan konuşmaya ortamı nasıl kurulur
- Konuşmadan konuşmaya modelleri yüklemek ve kullanmak için Python kodu nasıl yazılır
- Gradio kullanıcı arayüzü nasıl çalıştırılır ve deneyimlenir

## Neden gerçek zamanlı konuşmadan konuşmaya çeviri kullanılmalı?

- Çeviri ve dil engelleri arasındaki sürtünmeyi ortadan kaldırır
- Tonu, duyguyu ve niyeti garip duraklamalar olmadan iletir
- Küresel iş birliğini ve daha hızlı karar almayı mümkün kılar

## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme
> **Not**: VS Code yüklü değilse, Ryzen AI Developer Center ile yükleyebilirsiniz.

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarını Yükleme

### Sanal Ortam Oluşturma

<!-- @os:linux -->
<!-- @device:halo_box -->
Linux'ta bir terminal açın ve ROCm+PyTorch önceden yüklenmiş bir venv oluşturmak için aşağıdaki komutu çalıştırın:

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
**Kullanıcınıza GPU aygıtlarına erişim izni verin** (bunun geçerli olması için oturumu kapatıp yeniden açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

Linux'ta bir terminal açın ve bir venv oluşturmak için aşağıdaki komutu çalıştırın:

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
Windows'ta, seçtiğiniz dizinde bir terminal açın ve ROCm+PyTorch önceden yüklenmiş bir venv oluşturmak için komutları izleyin:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env --system-site-packages
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **İpucu**: Windows kullanıcılarının bazı PowerShell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmeleri gerekebilir (örneğin,
> RemoteSigned veya Unrestricted olarak ayarlamak).

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Windows'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için komutları izleyin:

<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv s2st-env
s2st-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="s2st-env\Scripts\activate" -->

> **İpucu**: Windows kullanıcılarının bazı PowerShell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmeleri gerekebilir (örneğin,
> RemoteSigned veya Unrestricted olarak ayarlamak).

<!-- @device:end -->
<!-- @os:end -->

### Temel Bağımlılıkları Yükleme

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:pytorch -->

### Ek Bağımlılıklar

m4t bağımlılıklarını pip kullanarak yükleyin:
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


## Konuşmadan konuşmaya demosunu kurma

#### seamless-m4t-v2 hakkında bilgi edinin

Daha fazla bilgi için Hugging Face üzerindeki [model kartına](https://huggingface.co/facebook/seamless-m4t-v2-large/tree/main) göz atın.
Bu, konuşmadan konuşmaya modellerinin teknik mimarisidir:
<p align="center">
  <img src="assets/seamlessm4t_arch.svg" alt="m4t arch" width="600"/>
</p>

#### Betikleri İndirin

Bu playbook, kullanıma hazır betikler içermektedir. Lütfen hepsini oluşturduğunuz ortamla aynı dizine indirin.

| Betik | Açıklama | Kullanım |
|--------|-------------|-------|
| [infer.py](assets/infer.py) | Temel LLM metin üretimi | `python infer.py` |
| [input1.wav](assets/input1.wav) | Örnek Ses Dosyası | N/A |
| [lang_list.py](assets/lang_list.py) | Dil Destek Dosyası | N/A |
| [gradio_demo.py](assets/gradio_demo.py) | Konuşma Çevirisi için Sezgisel Kullanıcı Arayüzü | `python gradio_demo.py --no-share` |


### infer.py ile Başlama

Betiği çalıştırmak için 
```bash
python infer.py
```
> **Not**: Bazı uyarılar görebilirsiniz. Bu beklenen bir durumdur.
 
  
#### Kodu Açıklama
**Parça 1: Gerekli bağımlılıkları içe aktarma**

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

**Parça 2: Modelleri HuggingFace'ten yükleme**

Bu fonksiyon bir model kimliği alır ve model henüz indirilmemişse indirir. Ardından bir sonraki fonksiyonun kullanması için işlemciyi ve modeli döndürür.
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

**Parça 3: Giriş ses klibi .wav dosyası ve ön işleme**

Bu fonksiyon ses klibini yükler ve hedef hıza yeniden örnekler.
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

**Parça 4: Çıkarım çalıştırma**

Bu fonksiyon model ile çıkarım çalıştırır ve üretilen çıktıyı döndürür.
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

**Parça 5: Çevrilen dosyayı kaydetme**

Bu fonksiyon ses dizisini bir .WAV dosyasına kaydeder. 
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

### Gradio kullanıcı arayüzü demosunu çalıştırma:

Temel bir betik örneği çalıştırdığınıza göre, aşağıdaki talimatlar yazdığımız kod üzerine inşa edilmiş ve canlı konuşmadan konuşmaya çeviriyi kolaylaştıran kullanışlı bir kullanıcı arayüzü sunmaktadır.

#### Gradio'yu Yerel Olarak Çalıştırma

```bash
python ./gradio_demo.py --no-share
```
Ardından, kullanıcı arayüzüne erişmek için web tarayıcınızı `http://127.0.0.1:7860` adresinde açın.


### Gradio kullanıcı arayüzü örneği:

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


## Sonraki Adımlar

- Hızlı çeviri için düzinelerce dil arasında karıştırıp eşleştirin.
- Demonuzu başkalarıyla paylaşın: Herkesin uzaktan erişebileceği bir genel bağlantı oluşturmak için --share ekleyin veya Hugging Face Spaces kullanarak kalıcı olarak dağıtın.

## Kaynaklar

Konuşmadan konuşmaya çeviri hakkında daha fazla bilgi edinmek için bazı ek kaynaklar aşağıda verilmiştir:  
* Depo burada: https://huggingface.co/facebook/seamless-m4t-v2-large 
* "Seamless: Multilingual Expressive and Streaming Speech Translation" ile ilgili akademik araştırmalar
* Gradio paylaşımı ve dağıtımı: [Uygulamanızı Paylaşma Kılavuzu](https://www.gradio.app/guides/sharing-your-app) ve [Hugging Face Spaces'e Dağıtım](https://shafiqulai.github.io/blogs/blog_5.html)