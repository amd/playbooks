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

Ten samouczek przedstawia przykłady krok po kroku dotyczące dostrajania dużego modelu językowego (LLM) z wykorzystaniem PyTorch i ROCm. Obejmuje on kilka technik, od standardowego dostrajania po strategie efektywnego pamięciowo dostrajania z wykorzystaniem niewielkiej liczby parametrów (Parameter-Efficient Fine-Tuning, PEFT), dzięki czemu łatwo dostosujesz modele do swoich potrzeb.

**Użyty model**: google/gemma-3-4b-it (skrypt QLoRA: openai/gpt-oss-20b)  *(zobacz [Włączanie uwierzytelniania HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), jeśli model jest zabezpieczony)*  
**Sprzęt**: GPU AMD Radeon™ z obsługą ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Uwaga:** 
> - Pełne dostrajanie wymaga co najmniej **64 GB pamięci RAM systemu**, z czego co najmniej **32 GB musi być dostępne dla GPU** (te 32 GB stanowi część 64 GB, a nie dodatek do nich).
> - Możesz także wypróbować inne architektury modeli, w tym **GPT-OSS-20B**, podstawiając model w dostarczonych skryptach treningowych.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Uwaga:** Dostrajanie LoRA i QLoRA wymaga co najmniej **32 GB pamięci RAM systemu**, z czego co najmniej **16 GB musi być dostępne dla GPU** (te 16 GB stanowi część 32 GB, a nie dodatek do nich).
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga:** Dostrajanie LoRA wymaga co najmniej **32 GB pamięci RAM systemu**, z czego co najmniej **16 GB musi być dostępne dla GPU** (te 16 GB stanowi część 32 GB, a nie dodatek do nich).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Uwaga:** Dostrajanie LoRA i QLoRA wymaga karty graficznej z co najmniej **16 GB dedykowanej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Linux trening odbywa się wyłącznie w dedykowanej pamięci VRAM karty graficznej.
> - Nie następuje przełączenie na współdzieloną pamięć GPU (RAM systemu), gdy zabraknie VRAM.
> - Karty z mniej niż 16 GB dedykowanej pamięci VRAM wyczerpią pamięć podczas treningu w systemie Linux, nawet jeśli system dysponuje dużą ilością RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga:** Dostrajanie LoRA wymaga co najmniej **16 GB łącznej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Windows łączna pamięć GPU łączy dedykowaną pamięć VRAM karty graficznej ze współdzieloną pamięcią GPU (pożyczaną z RAM systemu).
> - Dlatego karty z mniej niż 16 GB dedykowanej pamięci VRAM mogą nadal korzystać z tego przewodnika, wykorzystując współdzieloną pamięć GPU, aby uzupełnić różnicę.
<!-- @os:end -->
<!-- @device:end -->

## Czego się nauczysz

- Jak dostroić LLM za pomocą LoRA, QLoRA i pełnego dostrajania z wykorzystaniem PyTorch i ROCm
- Jak zapisać i wdrożyć dostrojony model
- Jak monitorować trening i debugować typowe problemy

<!-- @device:halo_box,halo,stx,krk -->
## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

#### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
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
**Przyznaj swojemu użytkownikowi dostęp do urządzeń GPU** (aby zmiana zaczęła obowiązywać, wyloguj się i zaloguj ponownie):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
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
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Instalowanie podstawowych zależności
<!-- @require:pytorch -->

#### Dodatkowe zależności

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Testowane i obsługiwane są tutaj wyłącznie podstawowe pakiety. **bitsandbytes nie jest dobrze obsługiwane w systemie Windows**, dlatego instalacja dla Windows je pomija; w systemie Windows korzystaj z LoRA lub pełnego dostrajania (QLoRA wymaga bitsandbytes i jest przeznaczone dla systemu Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Włączanie uwierzytelniania HF (zabezpieczone lub niestandardowe modele / niewbudowane fabrycznie)

W tym przykładzie używamy **google/gemma-3-4b-it**, który jest modelem **zabezpieczonym (gated)**. Musisz zaakceptować warunki modelu na Hugging Face, a następnie się uwierzytelnić, aby skrypty treningowe mogły go pobrać.

1. **Zaakceptuj licencję:** Otwórz [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), zaloguj się (lub utwórz konto) i zaakceptuj licencję/warunki na stronie modelu (np. „Agree and access repository”).
2. **Zainstaluj i zaloguj się:** Zainstaluj CLI Hugging Face, a następnie uruchom standardowe logowanie:

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

## Zrozumienie technik

### Czym jest LoRA?

**LoRA (Low-Rank Adaptation)** utrzymuje model bazowy zamrożony i trenuje jedynie niewielkie macierze „adapterów”, które są dodawane do określonych warstw. 

- **Kluczowa idea**: zamiast aktualizować ogromną macierz wag z milionami parametrów, uczymy się aktualizacji o niskim rzędzie (dwie małe macierze, których iloczyn ma znacznie mniej parametrów). Daje to znaczną redukcję liczby trenowalnych parametrów i zużycia VRAM, zachowując przy tym większość jakości pełnego dostrajania.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Czym jest QLoRA?

**QLoRA** łączy **kwantyzację 4-bitową** z **LoRA**. Model bazowy jest ładowany w formacie 4-bitowym (duże oszczędności pamięci), a tylko adaptery LoRA są trenowane z wyższą precyzją. Dzięki temu uzyskujesz efektywność parametrów LoRA oraz znacznie niższe zużycie VRAM, kosztem niewielkiego spadku jakości w porównaniu z pełnoprecyzyjnym LoRA. Należy pamiętać, że kwantyzacja 4-bitowa może powodować niestabilności numeryczne (skoki strat lub wartości NaN), dlatego użytkownicy często wolą **LoRA**, jeśli dostępna jest wystarczająca ilość VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Uwaga**: W przypadku modeli bazowych MXFP4, takich jak `openai/gpt-oss-20b`, zalecamy użycie **LoRA** (`train_lora.py`) zamiast QLoRA. Ścieżka 4-bitowa `bitsandbytes` w skrypcie QLoRA zazwyczaj dekwantyzuje wagi MXFP4 do formatu BF16, przez co uruchomienie zachowuje się jak standardowe LoRA. Natywny MXFP4 wymaga `bitsandbytes` zbudowanego ze źródeł wraz z dopasowanym stosem Transformers/Triton/kernels. Zobacz [dokumentację Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Wybierz metodę

| Metoda | Pamięć | Szybkość | Jakość | Najlepsza do |
|--------|--------|-------|---------|----------|
| **QLoRA** (tylko Linux) | 12-16GB | Najszybsza | 90-95% | Niskie zużycie pamięci |
| **LoRA** | 24-32GB | Szybka | 95-98% | Zrównoważone podejście |
| **Full** | 80GB+ | Najwolniejsza | 100% | Maksymalna jakość |

### 3. Uruchom trening

**Zbiór danych i czego uczy się model**  
Skrypty przekształcają zbiór danych w przykłady czatu. Na przykład skrypt QLoRA używa **Abirate/english_quotes**: każdy przykład staje się parą użytkownik–asystent, taką jak:

- **Użytkownik:** „Give me a quote about: &lt;tag&gt;”
- **Asystent:** „&lt;quote&gt; – &lt;author&gt;”

Dostrajanie uczy model odpowiadania na polecenia proszące o cytat na dany temat oraz zwracania ich w formacie `<quote text> - <author>`. Skrypty LoRA i pełnego dostrajania używają **databricks/databricks-dolly-15k** (ogólne pary instrukcja/odpowiedź), więc dokładne zadanie różni się w zależności od skryptu; idea jest taka sama – dostosowanie modelu do wybranego zbioru danych i formatu.

Poniżej znajduje się podsumowanie dostępnych metod treningu. Każda metoda zawiera link do swojego skryptu oraz krótki opis pomagający wybrać odpowiednie podejście.

| Skrypt                           | Metoda            | Opis                                                                                                         | Typowy VRAM | Zalecane dla                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trenuje małe macierze adaptera, zamrażając model bazowy. 3–5x szybciej; ~95–98% pełnej jakości.                         | 24–32GB      | Zaawansowani użytkownicy; wiele adapterów; więcej VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(tylko Linux)*             | **QLoRA**       | 4-bitowa kwantyzacja + adaptery LoRA. Najniższe zużycie pamięci, najszybsza, niewielki kompromis jakości. Wymaga `bitsandbytes` (tylko Linux).                            | 12–16GB      | Większość użytkowników; szybkie eksperymenty; ograniczony VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Pełne dostrajanie** | Aktualizuje wszystkie parametry modelu. Maksymalna jakość; najwyższe zużycie pamięci i mocy obliczeniowej.                                    | 40GB+        | Maksymalna jakość; badania; duży VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Uwaga:** Pełne dostrajanie (`train_full_finetuning.py`) może wymagać więcej niż 64GB pamięci RAM systemu i może być niewykonalne na tym urządzeniu. Rozważ użycie LoRA lub QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga:** Pełne dostrajanie (`train_full_finetuning.py`) może wymagać więcej niż 64GB pamięci RAM systemu i może być niewykonalne na tym urządzeniu. Rozważ użycie LoRA.
<!-- @os:end -->
<!-- @device:end -->

Po prostu wybierz preferowaną `Training method`, pobierz odpowiedni skrypt i uruchom go za pomocą polecenia, utrzymując aktywne środowisko wirtualne: 

```python
python3 train_<method_name>.py.
```

## Korzystanie z Twojego dostrojonego modelu

### Po pełnym dostrajaniu

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

### Po treningu LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Scalanie adaptera LoRA z modelem bazowym

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Uwaga:**  
- Upewnij się, że nazwa katalogu modelu (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) odpowiada rzeczywistemu folderowi wyjściowemu z treningu.  
- Jeśli użyto LoRA zamiast QLoRA, po prostu zamień ścieżkę odpowiednio.  
- Niektóre modele Gemma wymagają określenia `trust_remote_code=True` w `from_pretrained`; dodaj, jeśli pojawi się odpowiednie ostrzeżenie.

Aby uzyskać więcej niestandardowych ustawień (tokeny dopełniające, urządzenie itp.), zapoznaj się ze skryptem użytym do treningu.

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
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Przewodnik dostosowywania

### Użyj własnego zbioru danych

Wszystkie skrypty używają tego samego formatu zbioru danych. Zastąp sekcję wczytywania:

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

**Format zbioru danych dla lokalnego pliku JSON/JSONL:**

Korzystając z tej metody, upewnij się, że pliki JSON są poprawnie ustrukturyzowane, aby uniknąć błędów parsowania. 

Należy przestrzegać następujących wytycznych:
* **Formatowanie pliku:** Pliki JSON powinny być sformatowane w zintegrowanym środowisku programistycznym (IDE), aby zapewnić prawidłową strukturę i składnię.
* **Wymagane klucze:** Niestandardowy plik JSON musi zawierać klucze `instruction` i `response`. Te klucze są niezbędne do prawidłowego działania metody.
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
**Format zbioru danych dla zbioru danych z Hugging Face Hub**

Korzystając ze zbiorów danych z Hugging Face, upewnij się, że Twoje zbiory danych są poprawnie ustrukturyzowane, aby zapewnić płynną integrację. 

Należy przestrzegać następujących wytycznych:
* **Para instrukcja-odpowiedź:** Skup się na zbiorach danych zawierających parę `instruction-response`. Ta struktura jest niezbędna dla zamierzonej funkcjonalności.
* **Modyfikacja niestandardowego klucza:** Jeśli Twój zbiór danych nie jest zgodny ze strukturą `instruction-response`, masz możliwość zmodyfikowania funkcji `format_instruction()`. Pozwala to na dostosowanie do konkretnych kluczy w razie potrzeby.

Przykładowa modyfikacja: W przypadkach, gdy wynik zbioru danych wymaga dostosowania, możesz zmodyfikować sekcję odpowiedzi w funkcji format_instruction(), aby dopasować ją do swoich wymagań.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Format zbioru danych dla pliku CSV**

Aby dostosować skrypt do korzystania z formatu pliku CSV, musisz upewnić się, że plik CSV zawiera kolumny o nazwach `instruction` i `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Dostosuj parametry treningu

Edytuj skrypt treningowy i zmień zmienne, aby dopasować je do swoich celów: **współczynnik uczenia** (`LR`), **epoki** (`EPOCHS`), **rozmiar partii** (`BATCH_SIZE`), **akumulacja gradientu** (`GRAD_ACCUM_STEPS`), a dla LoRA/QLoRA **rank** (`LORA_R`). Aby uzyskać szybsze przebiegi, użyj mniejszej liczby epok i wyższego współczynnika uczenia (LR); aby uzyskać lepszą jakość, użyj większej liczby epok i niższego LR. Zmniejsz rozmiar partii lub długość sekwencji, jeśli wystąpią błędy braku pamięci.
### Wskazówki dotyczące optymalizacji pamięci

Jeśli napotkasz błędy braku pamięci:

**1. Zmniejsz rozmiar batcha:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Zmniejsz długość sekwencji:**
```python
max_seq_length=256  # Instead of 512
```

**3. Użyj bardziej agresywnej kwantyzacji:**
```
Full → LoRA → QLoRA
```

**4. Włącz Gradient Checkpointing (tylko dla pełnego dostrajania):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorowanie i debugowanie

### Monitorowanie pamięci GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcjonalnie) Śledzenie eksperymentów za pomocą Weights & Biases

Aby rejestrować przebiegi i metryki w [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

W skrypcie treningowym ustaw `report_to="wandb"` oraz opcjonalnie `run_name="your-experiment-name"` w konfiguracji trenera. Jeśli nie chcesz korzystać z Wandb, pozostaw `report_to` na wartości domyślnej lub ustaw je na `"none"`.

### Typowe problemy

#### Brak pamięci (OOM)

**Rozwiązanie:** Zmniejsz rozmiar batcha i/lub użyj QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Strata się nie zmniejsza

**Rozwiązanie:** Dostosuj współczynnik uczenia
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Wolny trening

**Rozwiązanie:** Zwiększ rozmiar batcha, jeśli pozwala na to pamięć
```python
BATCH_SIZE = 8
```
## Kolejne kroki

Po pomyślnym zakończeniu dostrajania rozważ poniższe kolejne kroki, aby w pełni wykorzystać potencjał swojego modelu:

1. **Ewaluuj** dokładnie na danych testowych wydzielonych ze zbioru, aby zmierzyć generalizację i uniknąć przeuczenia.
2. **Eksperymentuj**, testując różne wartości hiperparametrów, aby uzyskać lepszą dokładność, szybkość i kompromis w zakresie pamięci.
3. **Śledź** wszystkie swoje eksperymenty (i odpowiadające im metryki) za pomocą Weights & Biases, aby zapewnić powtarzalność badań.
4. **Wypróbuj** trening na własnych, niestandardowych zbiorach danych, aby dostosować model specjalnie do swojego przypadku użycia.
5. **Wdróż** swój dostrojony model do szybkiego wnioskowania, korzystając z wydajnych silników, takich jak vLLM, na zgodnym sprzęcie.
6. **Poznaj** zaawansowane techniki, w tym inżynierię promptów, precyzję mieszaną oraz dłuższe długości sekwencji.
7. **Wytrenuj** wiele adapterów LoRA dla różnych zadań lub dziedzin i wymieniaj je w razie potrzeby.