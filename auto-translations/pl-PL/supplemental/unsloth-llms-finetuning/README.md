<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

Ten przewodnik pokazuje, jak lokalnie dostroić model językowy przy użyciu Unsloth na sprzęcie AMD.

Wykorzystuje krótki przykład Supervised Fine-Tuning (SFT) z adapterami LoRA na modelu `unsloth/gemma-4-E4B-it`, przy użyciu podzbioru zbioru danych `mlabonne/FineTome-100k`. Celem jest przedstawienie prostego, kompletnego przepływu pracy obejmującego konfigurację, trenowanie, wnioskowanie oraz zapisywanie dostrojonego wyniku.

Przykład został zaprojektowany tak, aby był praktyczny i łatwy do modyfikacji, dzięki czemu można go wykorzystać jako punkt wyjścia dla własnych zbiorów danych i modeli.

## Czego się nauczysz

- Jak skonfigurować środowisko Unsloth
- Jak dostroić model LLM przy użyciu SFT z Unsloth
- Jak zapisać dostrojony wynik w lokalnym magazynie danych

<!-- @device:halo,stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają co najmniej **64 GB pamięci RAM systemu**, z czego co najmniej **24 GB musi być dostępne dla GPU** (te 24 GB stanowi część 64 GB, a nie dodatkową ilość).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają co najmniej **24 GB całkowitej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Windows całkowita pamięć GPU łączy dedykowaną pamięć VRAM karty graficznej z współdzieloną pamięcią GPU (pożyczaną z pamięci RAM systemu).
> - Dzięki temu karty z mniej niż 24 GB dedykowanej pamięci VRAM mogą nadal uruchomić ten przewodnik, korzystając ze współdzielonej pamięci GPU w celu uzupełnienia różnicy.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają karty graficznej z co najmniej **24 GB dedykowanej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Linux trenowanie odbywa się wyłącznie w dedykowanej pamięci VRAM karty graficznej.
> - Nie korzysta z rezerwowej, współdzielonej pamięci GPU (pamięci RAM systemu) w przypadku wyczerpania VRAM.
> - Karty z mniej niż 24 GB dedykowanej pamięci VRAM wyczerpią pamięć podczas trenowania w systemie Linux, nawet jeśli system dysponuje dużą ilością pamięci RAM.
<!-- @os:end -->
<!-- @device:end -->

## Dlaczego Unsloth?

Unsloth ułatwia uruchamianie dostrajania modeli LLM na lokalnym sprzęcie, zmniejszając zużycie pamięci i przyspieszając trenowanie w porównaniu ze standardową konfiguracją.

W tym przewodniku wykorzystujemy Unsloth wraz z **SFT opartym na LoRA**. Oznacza to, że model bazowy pozostaje w większości zamrożony, podczas gdy trenowany jest znacznie mniejszy zestaw wag adapterów. Jest to dobre rozwiązanie do lokalnego rozwoju, ponieważ jest lżejsze niż pełne dostrajanie i szybsze w iteracji.

Unsloth obsługuje również inne podejścia do trenowania, w tym QLoRA oraz przepływy pracy uczenia ze wzmocnieniem. Ten przewodnik skupia się przede wszystkim na najprostszej ścieżce: małym przykładzie dostrajania LoRA, który użytkownicy mogą uruchomić, zrozumieć i rozbudować.

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
Otwórz terminal i utwórz środowisko venv z zainstalowanym już oprogramowaniem AMD ROCm™ oraz PyTorch:
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
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (aby zmiana zaczęła obowiązywać, wyloguj się i zaloguj ponownie):

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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Uwaga:** Podczas importu Unsloth może sprawdzać opcjonalne ścieżki przyspieszenia `bitsandbytes`. W niektórych wersjach ROCm może pojawić się komunikat taki jak `bitsandbytes library load error: Configured ROCm binary not found`. Ten przewodnik wykorzystuje standardowe dostrajanie LoRA z `optim="adamw_torch"`, więc nie korzystamy z optymalizatora `bitsandbytes` ani z 4-bitowego QLoRA. Ten komunikat można bezpiecznie zignorować.

<!-- @os:windows -->
> **Uwaga:** W systemie Windows z ROCm Unsloth wyświetli przy uruchomieniu kilka ostrzeżeń — zobacz [Znane ostrzeżenia](#known-warnings) poniżej. Wszystkie można bezpiecznie zignorować; trenowanie działa poprawnie.
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

Zamiast ręcznie wykonywać każdy krok, ten przewodnik udostępnia gotowy, kompletny skrypt tutaj: [test_unsloth.py](assets/test_unsloth.py).

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

Pozostała część przewodnika przedstawia koncepcyjnie każdy główny krok skryptu.

## Jak to działa

Skrypt test_unsloth.py wykonuje następujące kroki:
* **Ładowanie modelu**: Ładuje unsloth/gemma-4-E4B-it przy użyciu FastModel.
* **Przygotowanie danych**: Standaryzuje zbiór danych (np. FineTome-100k) i stosuje szablon czatu Gemma-4.
* **Zastosowanie LoRA**: Dodaje adaptery do modułów językowych, uwagi (attention) oraz MLP w celu efektywnego trenowania.
* **Trenowanie**: Wykorzystuje SFTTrainer z maskowaniem straty tylko dla odpowiedzi.
* **Wnioskowanie**: Uruchamia szybki test generowania, aby zweryfikować wydajność.
* **Zapisywanie**: Eksportuje adaptery LoRA lokalnie.

## Kluczowa konfiguracja

Możesz zmodyfikować następujące stałe, aby dostosować przebieg:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Przykład powitalnej wiadomości Unsloth oraz wyniku podczas ładowania wag modelu:

![alt text](assets/welcome.png)

## Przygotowanie zbioru danych

Wykorzystujemy podzbiór:
```text
mlabonne/FineTome-100k
```
Zbiór danych jest:
* Konwertowany do formatu czatu
* Przetwarzany przy użyciu szablonu czatu Gemma-4
* Czyszczony w celu usunięcia zduplikowanych tokenów BOS

## Trenowanie modelu

Skrypt uruchamia krótką demonstrację trenowania z następującymi parametrami:
- ~50 kroków
- Mały rozmiar wsadu (batch)
- Akumulacja gradientu

Podczas trenowania zobaczysz logi takie jak:

![alt text](assets/training.png)


## Zapisywanie i wdrażanie
### Zapisywanie lokalne (LoRA)

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

### Zapisz scalony model (dla vLLM) 

<!-- @os:windows -->
> **Uwaga:** vLLM nie obsługuje systemu Windows. Aby wdrożyć swój dostrojony model w systemie Windows, użyj llama.cpp (patrz [Eksport GGUF](#export-gguf-for-llamacpp) poniżej) lub przenieś scalony model na maszynę z systemem Linux z uruchomionym vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Aby wdrożyć za pomocą vLLM, scal adaptery w pełny model:
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

Konwertuj bezpośrednio do formatu GGUF na potrzeby lokalnego wnioskowania:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znane ostrzeżenia

Poniższe ostrzeżenia są wyświetlane przez Unsloth podczas uruchamiania na Windows ROCm i wszystkie można bezpiecznie zignorować:

| Ostrzeżenie | Przyczyna | Bezpieczne do zignorowania? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nie ma kompilacji dla Windows ROCm | Tak — w tym przewodniku używane jest `adamw_torch`, a nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nie obsługuje treningu rozproszonego | Tak — trening na pojedynczym GPU nie jest tym objęty |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth oznacza kompilacje inne niż Linux | Tak — Windows ROCm działa poprawnie dla SFT na pojedynczym GPU |
| `triton is not available` | Triton nie ma kompilacji dla Windows | Tak — Unsloth korzysta wtedy z jąder PyTorch |

Trening przebiegnie poprawnie mimo tych ostrzeżeń.
<!-- @os:end -->

## Kolejne kroki
- Wypróbuj [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuicyjny interfejs graficzny dla Unsloth
- Przeprowadź trening na własnych, specyficznych zbiorach danych
- Wypróbuj dostrajanie z różnymi hiperparametrami
- Wdróż za pomocą vLLM lub llama.cpp
- Wypróbuj QLoRA, aby uzyskać konfigurację zużywającą mniej pamięci

## Zasoby

Poniżej znajduje się kilka dodatkowych zasobów, aby dowiedzieć się więcej o Unsloth i dostrajaniu:

* [Dokumentacja Unsloth](https://docs.unsloth.ai)

* [Unsloth na GitHub](https://github.com/unslothai/unsloth)

* [Przewodnik po dostrajaniu Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)