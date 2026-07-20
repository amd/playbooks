<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> W tym playbooku zastosowano specjalne tagi, których GitHub nie potrafi wyrenderować. Aby poprawnie wyświetlić tę zawartość, odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Przegląd

Ten playbook pokazuje, jak lokalnie dostroić model językowy za pomocą Unsloth na sprzęcie AMD.

Wykorzystuje krótki przykład nadzorowanego dostrajania (Supervised Fine-Tuning, SFT) z adapterami LoRA na modelu `unsloth/gemma-4-E4B-it`, przy użyciu podzbioru zestawu danych `mlabonne/FineTome-100k`. Celem jest przedstawienie prostego, kompleksowego przepływu pracy obejmującego konfigurację, trenowanie, wnioskowanie oraz zapis dostrojonego wyniku.

Przykład został zaprojektowany tak, aby był praktyczny i łatwy do modyfikacji, dzięki czemu można go wykorzystać jako punkt wyjścia dla własnych zestawów danych i modeli.

## Czego się nauczysz

- Jak skonfigurować środowisko Unsloth
- Jak dostroić model LLM za pomocą SFT z użyciem Unsloth
- Jak zapisać dostrojony wynik w pamięci lokalnej

<!-- @device:halo,stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB pamięci GPU oraz 32 GB pamięci RAM systemu.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB pamięci GPU oraz 32 GB pamięci RAM systemu.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB **dedykowanej** pamięci GPU oraz 32 GB pamięci RAM systemu.
<!-- @os:end -->
<!-- @device:end -->

## Dlaczego Unsloth?

Unsloth ułatwia uruchamianie dostrajania modeli LLM na lokalnym sprzęcie, zmniejszając zużycie pamięci i przyspieszając trenowanie w porównaniu ze standardową konfiguracją.

W tym playbooku wykorzystujemy Unsloth razem z **SFT opartym na LoRA**. Oznacza to, że model bazowy pozostaje w większości zamrożony, natomiast trenowany jest znacznie mniejszy zestaw wag adapterów. Jest to dobre rozwiązanie dla lokalnego rozwoju, ponieważ jest lżejsze niż pełne dostrajanie i pozwala szybciej iterować.

Unsloth obsługuje również inne podejścia do trenowania, w tym QLoRA oraz przepływy pracy uczenia ze wzmocnieniem. Ten playbook koncentruje się w pierwszej kolejności na najprostszej ścieżce: małym przykładzie dostrajania LoRA, który użytkownicy mogą uruchomić, zrozumieć i rozszerzyć.

## Konfiguracja pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz zainstalować go za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
Otwórz terminal i utwórz środowisko venv z już zainstalowanym oprogramowaniem AMD ROCm™ i PyTorch:
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
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (aby to zadziałało, wyloguj się i zaloguj ponownie):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otwórz terminal i utwórz środowisko venv:
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
> **Uwaga:** W systemie Windows wymagany jest Python 3.13.

<!-- @device:halo_box -->
Otwórz terminal PowerShell i utwórz środowisko wirtualne:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Otwórz terminal PowerShell i utwórz środowisko wirtualne:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalacja podstawowych zależności
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

### Dodatkowe zależności

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

> **Uwaga:** Podczas importu Unsloth może sprawdzać opcjonalne ścieżki akceleracji `bitsandbytes`. W niektórych wersjach ROCm może pojawić się komunikat taki jak `bitsandbytes library load error: Configured ROCm binary not found`. Ten playbook wykorzystuje standardowe dostrajanie LoRA z `optim="adamw_torch"`, więc nie korzystamy z optymalizatora `bitsandbytes` ani z 4-bitowego QLoRA. Ten komunikat można bezpiecznie zignorować.

<!-- @os:windows -->
> **Uwaga:** W środowisku Windows ROCm, Unsloth wyświetli przy uruchomieniu kilka ostrzeżeń — zobacz [Znane ostrzeżenia](#known-warnings) poniżej. Wszystkie z nich można bezpiecznie zignorować; trenowanie działa poprawnie.
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

## Pobierz skrypt dostrajania Unsloth

Zamiast ręcznie wykonywać każdy krok, ten playbook udostępnia gotowy, kompleksowy skrypt tutaj: [test_unsloth.py](assets/test_unsloth.py).

Uruchom poniższy kod, aby wykonać skrypt:

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

Pozostała część playbooka omówi koncepcyjnie każdy główny krok skryptu.

## Jak to działa

Skrypt test_unsloth.py wykonuje następujące kroki:
* **Wczytanie modelu**: Wczytuje unsloth/gemma-4-E4B-it za pomocą FastModel.
* **Przygotowanie danych**: Standaryzuje zestaw danych (np. FineTome-100k) i stosuje szablon czatu Gemma-4.
* **Zastosowanie LoRA**: Dodaje adaptery do modułów językowych, uwagi (attention) oraz MLP w celu efektywnego trenowania.
* **Trenowanie**: Wykorzystuje SFTTrainer z maskowaniem straty tylko dla odpowiedzi.
* **Wnioskowanie**: Uruchamia szybki test generowania w celu weryfikacji wydajności.
* **Zapis**: Eksportuje adaptery LoRA lokalnie.

## Kluczowa konfiguracja

Możesz zmodyfikować następujące stałe, aby dostosować swój przebieg:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Przykład komunikatu powitalnego Unsloth oraz danych wyjściowych podczas wczytywania wag modelu:

![tekst alternatywny](assets/welcome.png)

## Przygotowanie zestawu danych

Wykorzystujemy podzbiór:
```text
mlabonne/FineTome-100k
```
Zestaw danych jest:
* Konwertowany do formatu czatu
* Przetwarzany przy użyciu szablonu czatu Gemma-4
* Czyszczony w celu usunięcia zduplikowanych tokenów BOS

## Trenowanie modelu

Skrypt uruchamia krótką demonstrację trenowania, z następującymi parametrami:
- ~50 kroków
- Mały rozmiar wsadu (batch size)
- Akumulacja gradientu

Podczas trenowania zobaczysz logi takie jak:

![tekst alternatywny](assets/training.png)


## Zapisywanie i wdrażanie

### Zapis lokalny (LoRA)

Skrypt automatycznie zapisuje adaptery LoRA w katalogu OUTPUT_DIR.
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

### Zapisz scalony model (dla vLLM)

<!-- @os:windows -->
> **Uwaga:** vLLM nie obsługuje systemu Windows. Aby wdrożyć dostrojony model w systemie Windows, użyj llama.cpp (zobacz [Eksport GGUF](#export-gguf-for-llamacpp) poniżej) lub przenieś scalony model na maszynę z systemem Linux z uruchomionym vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Aby wdrożyć model za pomocą vLLM, scal adaptery w pełny model:
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

### Eksport GGUF (dla llama.cpp)

Przekonwertuj bezpośrednio do formatu GGUF na potrzeby lokalnego wnioskowania:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znane ostrzeżenia

Te ostrzeżenia są wyświetlane przez Unsloth podczas uruchamiania na Windows ROCm i wszystkie można bezpiecznie zignorować:

| Ostrzeżenie | Powód | Bezpieczne do zignorowania? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nie ma kompilacji dla Windows ROCm | Tak — ten poradnik używa `adamw_torch`, a nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nie obsługuje trenowania rozproszonego | Tak — trenowanie na pojedynczym GPU nie jest tym dotknięte |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth oznacza kompilacje inne niż Linux | Tak — Windows ROCm działa poprawnie przy SFT na pojedynczym GPU |
| `triton is not available` | Triton nie ma kompilacji dla Windows | Tak — Unsloth przełącza się na jądra PyTorch |

Trenowanie przebiegnie poprawnie mimo tych ostrzeżeń.
<!-- @os:end -->

## Kolejne kroki
- Wypróbuj [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuicyjny interfejs graficzny dla Unsloth
- Trenuj na własnych, dedykowanych zbiorach danych
- Wypróbuj dostrajanie z różnymi hiperparametrami
- Wdróż za pomocą vLLM lub llama.cpp
- Wypróbuj QLoRA dla konfiguracji zużywającej mniej pamięci

## Zasoby

Poniżej znajdują się dodatkowe zasoby, dzięki którym dowiesz się więcej o Unsloth i dostrajaniu modeli:

* [Dokumentacja Unsloth](https://docs.unsloth.ai)

* [Unsloth na GitHub](https://github.com/unslothai/unsloth)

* [Przewodnik po dostrajaniu Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)