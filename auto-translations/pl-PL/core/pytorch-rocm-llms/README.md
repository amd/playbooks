<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd


Chcesz uruchamiać zaawansowane modele językowe AI na własnym sprzęcie? Ten przewodnik pokaże Ci, jak to zrobić.
Ten samouczek wykorzystuje PyTorch zasilany oprogramowaniem AMD ROCm™ do uruchamiania modeli, które potrafią streszczać dokumenty, odpowiadać na pytania, generować tekst i wiele więcej – wszystko działające lokalnie.

## Czego się nauczysz

- Uruchamiać modele LLM, takie jak gpt-oss-20b i qwen3.5-4B, lokalnie przy użyciu PyTorch i ROCm
- Tworzyć narzędzie do streszczania dokumentów z wykorzystaniem modeli LLM

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie dostępnych aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv z już zainstalowanym ROCm+PyTorch.
<!-- @test:id=create-venv timeout=120 -->
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
**Przyznaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiany weszły w życie):

```bash
sudo usermod -aG render,video $LOGNAME
```

W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
<!-- @test:id=create-venv timeout=120 -->
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
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv z już zainstalowanym ROCm+PyTorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania skryptów PowerShell (np.
> ustawić je na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.

<!-- @os:end -->

### Instalowanie podstawowych zależności
<!-- @require:driver,pytorch -->

### Instalowanie dodatkowych zależności

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Szybki start z przykładowymi skryptami

Ten playbook zawiera gotowe do użycia skrypty. Kliknij je, aby wyświetlić podgląd i pobrać je do tego samego katalogu, w którym utworzono środowisko.

| Skrypt | Opis | Użycie |
|--------|------|--------|
| [run_llm.py](assets/run_llm.py) | Podstawowe generowanie tekstu przez LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Narzędzie do streszczania dokumentów z obsługą Harmony | `python summarizer.py --file document.txt` |

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

Oba skrypty obsługują:
- Wybór modelu za pomocą flagi `--model`
- Formatowanie szablonu czatu dla właściwego promptowania modelu, szczególnie przydatne przy streszczaniu dokumentów

## Ładowanie i uruchamianie pierwszego modelu LLM

Dołączony skrypt [run_llm.py](assets/run_llm.py) pokazuje, jak generować tekst za pomocą modeli LLM przy użyciu PyTorch i AMD ROCm.

> **Uwaga:** Podczas ładowania modelu Hugging Face Transformers najpierw sprawdza lokalną pamięć podręczną (`~/.cache/huggingface/hub` w systemie Linux, `C:\Users\<user>\.cache\huggingface\hub` w systemie Windows). Jeśli model nie jest zapisany w pamięci podręcznej, zostanie automatycznie pobrany z huggingface.co. Pierwsze uruchomienie może potrwać kilka minut w zależności od rozmiaru modelu i prędkości sieci.

Poniższy fragment kodu pokazuje, jak korzystać z modelu i dostosowywać zadawane pytania.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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

Wypróbuj pobrany skrypt:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Budowanie narzędzia do streszczania dokumentów

Teraz, gdy udało Ci się wygenerować lokalne dane wyjściowe modelu LLM, możesz rozwinąć tę funkcjonalność, tworząc praktyczne narzędzie do streszczania dokumentów. W tej sekcji użyjesz skryptu [summarizer.py](assets/summarizer.py), aby podać plik .txt i automatycznie wygenerować zwięzłe podsumowanie – wszystko działające lokalnie na Twoim GPU.

Skrypt jest zaprojektowany tak, aby działać od razu po uruchomieniu. Otwórz go w edytorze, aby zapoznać się z kodem, dostosować prompty i dostroić parametry, takie jak długość i temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Przykłady użycia

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

## Poznaj parametry generowania

| Parametr | Co kontroluje | Typowe wartości |
|----------|---------------|-----------------|
| `max_new_tokens` | Maksymalna długość danych wyjściowych modelu LLM | Użyj 50–500 tokenów dla streszczeń. (1 token to około 0,75 słowa w języku angielskim) |
| `temperature` | Kreatywność. Niskie wartości sprawiają, że model jest bardziej skupiony, podczas gdy wysokie wartości wiążą się z większą nieprzewidywalnością | - **0.1–0.3**: Skupiony, deterministyczny (dobry do streszczeń) <br> **0.5–0.7**: Zrównoważony (ogólne zastosowanie) <br> **0.8–1.0**: Kreatywny, zróżnicowany (burza mózgów) |
| `top_p` | Próbkowanie jądrowe – niskie wartości ograniczają model do bardziej wąskich wyników | **0.1-0.5**: Ścisły, przewidywalny <br> **0.9-0.95**: (standardowy, naturalny, konwersacyjny) |


## Zastosowania w rzeczywistym świecie

- **Analiza artykułów naukowych**: Wyodrębnianie kluczowych wniosków ze złożonych publikacji do szybkiego przeglądu
- **Agregacja wiadomości**: Streszczanie artykułów prasowych w krótkie codzienne przeglądy lub najważniejsze informacje
- **Notatki ze spotkań**: Kondensowanie transkryptów do punktów działania i zwięzłych podsumowań
- **Przegląd dokumentów prawnych**: Szybkie wyodrębnianie istotnych klauzul lub zobowiązań z obszernych tekstów prawnych
- **Dokumentacja kodu**: Generowanie zwięzłych przeglądów repozytoriów i objaśnień funkcji

## Kolejne kroki

- **Dostrajanie**: Dostosowywanie modeli do swojej dziedziny lub żargonu w celu uzyskania lepszej dokładności (patrz playbooki dotyczące dostrajania)
- **Systemy RAG**: Łączenie modeli LLM z wyszukiwaniem dokumentów w celu uzyskania odpowiedzi uwzględniających kontekst i wyszukiwania
- **Eksploracja modeli**: Eksperymentowanie z nowymi modelami, takimi jak Llama 3, Phi-3 lub Qwen, w celu uzyskania lepszych wyników
- **Wdrożenie produkcyjne**: Używanie narzędzi takich jak vLLM do skalowalnego serwowania modeli LLM w organizacjach

Twój system daje Ci możliwość lokalnego uruchamiania zaawansowanych modeli językowych. Eksperymentuj z różnymi modelami, promptami i parametrami, aby odkryć, co najlepiej sprawdza się w Twoich zastosowaniach.