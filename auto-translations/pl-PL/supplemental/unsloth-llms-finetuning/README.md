<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

Ten playbook pokazuje, jak przeprowadzić lokalne dostrajanie modelu językowego przy użyciu Unsloth na sprzęcie AMD.

Wykorzystuje krótki przykład Supervised Fine-Tuning (SFT) z adapterami LoRA na modelu `unsloth/gemma-4-E4B-it`, korzystając z podzbioru zbioru danych `mlabonne/FineTome-100k`. Celem jest zapewnienie prostego, kompleksowego przepływu pracy obejmującego konfigurację, trening, wnioskowanie i zapisanie dostrojonego modelu.

Przykład został zaprojektowany tak, aby był praktyczny i łatwy do modyfikacji, dzięki czemu możesz go używać jako punktu wyjścia dla własnych zbiorów danych i modeli.

## Czego się nauczysz

- Jak skonfigurować środowisko Unsloth
- Jak dostroić LLM przy użyciu SFT z Unsloth
- Jak zapisać dostrojony model w lokalnym magazynie

<!-- @device:halo,stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB pamięci GPU i 32 GB pamięci RAM systemu.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB pamięci GPU i 32 GB pamięci RAM systemu.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym playbooku wymagają co najmniej 24 GB **dedykowanej** pamięci GPU i 32 GB pamięci RAM systemu.
<!-- @os:end -->
<!-- @device:end -->

## Dlaczego Unsloth?

Unsloth ułatwia uruchamianie dostrajania LLM na lokalnym sprzęcie, zmniejszając zużycie pamięci i przyspieszając trening w porównaniu ze standardową konfiguracją.

W tym playbooku używamy Unsloth razem z **SFT opartym na LoRA**. Oznacza to, że model bazowy pozostaje w większości zamrożony, podczas gdy trenowany jest znacznie mniejszy zestaw wag adaptera. Jest to dobre rozwiązanie dla lokalnego programowania, ponieważ jest lżejsze niż pełne dostrajanie i szybsze w iteracji.

Unsloth obsługuje również inne podejścia do treningu, w tym QLoRA i przepływy pracy z uczeniem przez wzmacnianie. Ten playbook skupia się najpierw na najprostszej ścieżce: małym przykładzie dostrajania LoRA, który użytkownicy mogą uruchomić, zrozumieć i rozszerzyć.

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
Otwórz terminal i utwórz venv z oprogramowaniem AMD ROCm™ i PyTorch już zainstalowanym:
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
**Przyznaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiany weszły w życie):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otwórz terminal i utwórz venv:
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
> **Uwaga:** Python 3.13 jest wymagany dla systemu Windows.

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

### Instalowanie podstawowych zależności
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

> **Uwaga:** Podczas importu Unsloth może sprawdzać opcjonalne ścieżki akceleracji `bitsandbytes`. W niektórych wersjach ROCm może pojawić się komunikat taki jak `bitsandbytes library load error: Configured ROCm binary not found`. Ten playbook używa standardowego dostrajania LoRA z `optim="adamw_torch"`, więc nie polegamy na optymalizatorze `bitsandbytes` ani 4-bitowym QLoRA. Ten komunikat można bezpiecznie zignorować.

<!-- @os:windows -->
> **Uwaga:** W systemie Windows ROCm, Unsloth wyświetli kilka ostrzeżeń podczas uruchamiania — patrz [Znane ostrzeżenia](#known-warnings) poniżej. Wszystkie można bezpiecznie zignorować; trening działa poprawnie.
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

## Pobieranie skryptu dostrajania Unsloth

Zamiast ręcznie wykonywać każdy krok, ten playbook udostępnia czysty, kompleksowy skrypt: [test_unsloth.py](assets/test_unsloth.py).

Uruchom następujący kod, aby wykonać skrypt:

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

Pozostała część playbooka koncepcyjnie omówi każdy główny krok skryptu.

## Jak to działa

Skrypt test_unsloth.py wykonuje następujące kroki:
* **Ładowanie modelu**: Ładuje unsloth/gemma-4-E4B-it przy użyciu FastModel.
* **Przygotowanie danych**: Standaryzuje zbiór danych (np. FineTome-100k) i stosuje szablon czatu Gemma-4.
* **Zastosowanie LoRA**: Dodaje adaptery do modułów językowych, uwagi i MLP w celu efektywnego treningu.
* **Trening**: Używa SFTTrainer z maskowaniem straty tylko dla odpowiedzi.
* **Wnioskowanie**: Przeprowadza szybki test generowania w celu weryfikacji wydajności.
* **Zapisywanie**: Eksportuje adaptery LoRA lokalnie.

## Kluczowa konfiguracja

Możesz modyfikować następujące stałe, aby dostosować swoje uruchomienie:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Przykład komunikatu powitalnego Unsloth i danych wyjściowych podczas ładowania wag modelu:

![tekst alternatywny](assets/welcome.png)

## Przygotowanie zbioru danych

Używamy podzbioru:
```text
mlabonne/FineTome-100k
```
Zbiór danych jest:
* Konwertowany do formatu czatu
* Przetwarzany przy użyciu szablonu czatu Gemma-4
* Czyszczony w celu usunięcia zduplikowanych tokenów BOS

## Trenowanie modelu

Skrypt uruchamia krótkie demo treningu z następującymi parametrami:
- ~50 kroków
- Mały rozmiar wsadu
- Akumulacja gradientu

Podczas treningu zobaczysz logi takie jak:

![tekst alternatywny](assets/training.png)


## Zapisywanie i wdrażanie

### Lokalne zapisywanie (LoRA)

Skrypt automatycznie zapisuje adaptery LoRA do OUTPUT_DIR.
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

### Zapisywanie scalonego modelu (dla vLLM)

<!-- @os:windows -->
> **Uwaga:** vLLM nie obsługuje systemu Windows. Aby wdrożyć dostrojony model w systemie Windows, użyj llama.cpp (patrz [Eksport GGUF](#export-gguf-for-llamacpp) poniżej) lub przenieś scalony model na maszynę z systemem Linux z uruchomionym vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Aby wdrożyć z vLLM, scal adaptery z pełnym modelem:
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

Konwertuj bezpośrednio do GGUF dla lokalnego wnioskowania:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znane ostrzeżenia

Te ostrzeżenia są wyświetlane przez Unsloth podczas uruchamiania w systemie Windows ROCm i wszystkie można bezpiecznie zignorować:

| Ostrzeżenie | Przyczyna | Można bezpiecznie zignorować? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nie ma kompilacji dla Windows ROCm | Tak — ten playbook używa `adamw_torch`, nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm w systemie Windows nie obsługuje treningu rozproszonego | Tak — trening na jednym GPU nie jest naruszony |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth oznacza kompilacje inne niż Linux | Tak — Windows ROCm działa dla SFT na jednym GPU |
| `triton is not available` | Triton nie ma kompilacji dla systemu Windows | Tak — Unsloth przełącza się na jądra PyTorch |

Trening będzie przebiegał poprawnie pomimo tych ostrzeżeń.
<!-- @os:end -->

## Następne kroki
- Wypróbuj [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuicyjny interfejs graficzny dla Unsloth
- Trenuj na własnych, specyficznych zbiorach danych
- Wypróbuj dostrajanie z różnymi hiperparametrami
- Wdrażaj z vLLM lub llama.cpp
- Wypróbuj QLoRA dla konfiguracji z mniejszym zużyciem pamięci

## Zasoby

Poniżej znajdują się dodatkowe zasoby, aby dowiedzieć się więcej o Unsloth i dostrajaniu:

* [Dokumentacja Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Przewodnik po dostrajaniu Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)