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


Chcesz uruchamiać zaawansowane modele językowe AI na własnym sprzęcie? Ten przewodnik pokazuje, jak to zrobić.
W tym samouczku wykorzystano PyTorch napędzany przez oprogramowanie AMD ROCm™ do uruchamiania modeli, które potrafią podsumowywać dokumenty, odpowiadać na pytania, generować tekst i wiele więcej — wszystko lokalnie.

## Czego się nauczysz

- Uruchamianie modeli LLM, takich jak gpt-oss-20b i qwen3.5-4B, lokalnie za pomocą PyTorch i ROCm
- Tworzenie narzędzia do podsumowywania dokumentów przy użyciu modeli LLM

<!-- @device:halo_box,halo,stx,krk -->
## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv z już zainstalowanym ROCm+Pytorch.
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
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiana zaczęła obowiązywać):

```bash
sudo usermod -aG render,video $LOGNAME
```

W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
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
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv z już zainstalowanym ROCm+Pytorch.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Wskazówka**: Użytkownicy systemu Windows mogą musieć zmodyfikować zasady wykonywania programu PowerShell (np.
> ustawić je na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń Powershell.

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

> **Uwaga:** Jeśli model nie ładuje się lub brakuje pamięci, spróbuj zainstalować pakiet `kernels`, aby załadować model z zoptymalizowaną kwantyzacją.
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

## Szybki start z przykładowymi skryptami

Ten przewodnik zawiera gotowe do użycia skrypty. Kliknij je, aby wyświetlić podgląd i pobrać do tego samego katalogu, w którym utworzono środowisko.

| Skrypt | Opis | Sposób użycia |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Podstawowe generowanie tekstu przez LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Narzędzie do podsumowywania dokumentów z obsługą Harmony | `python summarizer.py --file document.txt` |

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
- Formatowanie szablonu czatu w celu prawidłowego formułowania promptów dla modelu, co jest szczególnie przydatne przy podsumowywaniu dokumentów

## Ładowanie i uruchamianie pierwszego modelu LLM

Dołączony skrypt [run_llm.py](assets/run_llm.py) pokazuje, jak generować tekst za pomocą modeli LLM przy użyciu PyTorch i AMD ROCm.

> **Uwaga:** Podczas ładowania modelu Hugging Face Transformers najpierw sprawdza jego lokalną pamięć podręczną (`~/.cache/huggingface/hub` w systemie Linux, `C:\Users\<user>\.cache\huggingface\hub` w systemie Windows). Jeśli model nie znajduje się w pamięci podręcznej, zostaje automatycznie pobrany z huggingface.co. Pierwsze uruchomienie może potrwać kilka minut, w zależności od rozmiaru modelu i szybkości sieci.

Poniższy fragment pokazuje, jak korzystać z modelu i dostosowywać zadawane pytania.

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

Wypróbuj pobrany skrypt:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Tworzenie narzędzia do podsumowywania dokumentów

Skoro udało Ci się już wygenerować wynik za pomocą lokalnego modelu LLM, możesz rozwinąć tę wiedzę, tworząc praktyczne narzędzie do podsumowywania dokumentów. W tej sekcji użyjesz skryptu [summarizer.py](assets/summarizer.py), aby wczytać plik .txt i automatycznie wygenerować zwięzłe podsumowanie, całkowicie lokalnie na Twoim GPU.

Skrypt jest zaprojektowany tak, aby działał od razu po uruchomieniu. Otwórz go w edytorze, aby zapoznać się z kodem, dostosować prompty oraz zmodyfikować parametry, takie jak długość i temperatura.

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
|-----------|------------------|----------------|
| `max_new_tokens` | Maksymalna długość wyniku generowanego przez LLM | Użyj 50–500 tokenów dla podsumowań. (1 token to około 0,75 angielskiego słowa) |
| `temperature` | Kreatywność. Niskie wartości sprawiają, że model jest bardziej skoncentrowany, wysokie wprowadzają więcej nieprzewidywalności | - **0,1–0,3**: Skoncentrowane, deterministyczne (dobre do podsumowań) <br> **0,5–0,7**: Zrównoważone (użycie ogólne) <br> **0,8–1,0**: Kreatywne, zróżnicowane (burza mózgów) |
| `top_p` | Próbkowanie Nucleus – niskie wartości ograniczają model do węższego zakresu wyników | **0,1-0,5**: Ścisłe, przewidywalne <br> **0,9-0,95**: (standardowe, naturalne, konwersacyjne) |


## Zastosowania w praktyce

- **Analiza artykułów naukowych**: Wydobywanie kluczowych wniosków ze złożonych publikacji w celu szybkiego przeglądu
- **Agregacja wiadomości**: Podsumowywanie artykułów informacyjnych w krótkie, codzienne zestawienia lub najważniejsze informacje
- **Notatki ze spotkań**: Skracanie transkrypcji do konkretnych zadań i zwięzłych podsumowań
- **Przegląd dokumentów prawnych**: Szybkie wydobywanie odpowiednich klauzul lub zobowiązań z długich tekstów prawnych
- **Dokumentacja kodu**: Generowanie zwięzłych przeglądów repozytoriów i wyjaśnień funkcji
## Kolejne kroki

- **Dostrajanie**: Dostosuj modele do swojej konkretnej dziedziny lub terminologii, aby uzyskać lepszą dokładność (zobacz Fine-tuning Playbooks)
- **Systemy RAG**: Połącz LLM-y z wyszukiwaniem dokumentów, aby uzyskać odpowiedzi i wyszukiwanie uwzględniające kontekst
- **Eksploracja modeli**: Eksperymentuj z nowymi modelami, takimi jak Llama 3, Phi-3 czy Qwen, aby uzyskać lepsze wyniki
- **Wdrożenie produkcyjne**: Korzystaj z narzędzi takich jak vLLM do skalowalnego serwowania LLM-ów w organizacjach

Twój system daje Ci możliwość lokalnego uruchamiania zaawansowanych modeli językowych. Eksperymentuj z różnymi modelami, promptami i parametrami, aby odkryć, co najlepiej sprawdza się w Twoich zastosowaniach.