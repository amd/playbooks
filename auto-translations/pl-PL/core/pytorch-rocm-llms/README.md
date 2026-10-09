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


Chcesz uruchomić zaawansowane modele językowe AI na własnym sprzęcie? Ten przewodnik pokazuje, jak to zrobić.
Ten samouczek wykorzystuje PyTorch zasilany przez oprogramowanie AMD ROCm™ do uruchamiania modeli, które potrafią streszczać dokumenty, odpowiadać na pytania, generować tekst i wiele więcej — wszystko działające lokalnie.

## Czego się nauczysz

- Uruchamianie modeli LLM, takich jak gpt-oss-20b i qwen3.5-4B, lokalnie przy użyciu PyTorch i ROCm
- Tworzenie narzędzia do streszczania dokumentów przy użyciu modeli LLM

<!-- @device:halo_box,halo,stx,krk -->
## Konfiguracja pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

### Tworzenie środowiska wirtualnego

<!-- @os:linux -->
<!-- @device:halo_box -->
W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć venv z już zainstalowanym ROCm+Pytorch.
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

W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć venv.
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
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć venv z już zainstalowanym ROCm+Pytorch.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania PowerShell
> (np. ustawić RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.

<!-- @os:end -->

### Instalacja podstawowych zależności
<!-- @require:driver,pytorch -->

### Instalacja dodatkowych zależności

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->
<!-- @device:halo,halo_box -->
<!-- @prereq:hf-models-gpt-oss-20b -->
<!-- @device:end -->
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:hf-models-qwen3-5-4b -->
<!-- @device:end -->

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

> **Uwaga:** Jeśli model nie wczyta się lub zabraknie pamięci, spróbuj zainstalować pakiet `kernels`, aby wczytać model z zoptymalizowaną kwantyzacją.
>
> ```bash
> # Użyj tej wersji, która jest zgodna z wersją Transformers
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

Ten przewodnik zawiera gotowe do użycia skrypty. Kliknij je, aby je podejrzeć i pobrać do tego samego katalogu, w którym znajduje się utworzone przez Ciebie środowisko.

| Skrypt | Opis | Użycie |
|--------|-------------|-------|
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
- Formatowanie szablonu czatu w celu prawidłowego podpowiadania modelowi, co jest szczególnie przydatne przy streszczaniu dokumentów

## Wczytywanie i uruchamianie pierwszego modelu LLM

Dołączony skrypt [run_llm.py](assets/run_llm.py) pokazuje, jak generować tekst za pomocą modeli LLM przy użyciu PyTorch i AMD ROCm.

> **Uwaga:** Podczas wczytywania modelu Hugging Face Transformers najpierw sprawdza lokalną pamięć podręczną (`~/.cache/huggingface/hub` w systemie Linux, `C:\Users\<user>\.cache\huggingface\hub` w systemie Windows). Jeśli model nie znajduje się w pamięci podręcznej, zostaje automatycznie pobrany z huggingface.co. Pierwsze uruchomienie może potrwać kilka minut, w zależności od rozmiaru modelu i szybkości sieci.

Poniższy fragment kodu pokazuje, jak używać modelu i dostosowywać zadawane pytania.

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


## Tworzenie narzędzia do streszczania dokumentów

Teraz, gdy wygenerowałeś lokalny wynik działania modelu LLM, możesz na tej podstawie zbudować praktyczne narzędzie do streszczania dokumentów. W tej sekcji użyjesz skryptu [summarizer.py](assets/summarizer.py), aby wczytać plik .txt i automatycznie wygenerować zwięzłe streszczenie, działające w całości lokalnie na Twoim GPU.

Skrypt został zaprojektowany tak, aby działał od razu po uruchomieniu. Otwórz skrypt w edytorze, aby zapoznać się z kodem, dostosować podpowiedzi (prompty) i zmodyfikować parametry, takie jak długość i temperatura.

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
| `max_new_tokens` | Maksymalną długość danych wyjściowych modelu LLM | Użyj 50–500 tokenów dla streszczeń. (1 token to około 0,75 angielskiego słowa) |
| `temperature` | Kreatywność. Niskie wartości sprawiają, że odpowiedź jest bardziej skoncentrowana, a wysokie — bardziej nieprzewidywalna | - **0,1–0,3**: skoncentrowana, deterministyczna (dobra do streszczeń) <br> **0,5–0,7**: zrównoważona (zastosowania ogólne) <br> **0,8–1,0**: kreatywna, zróżnicowana (burza mózgów) |
| `top_p` | Nucleus Sampling — niskie wartości ograniczają model do węższego zakresu wyników | **0,1–0,5**: ścisłe, przewidywalne <br> **0,9–0,95**: (standardowe, naturalne, konwersacyjne) |


## Zastosowania w praktyce

- **Analiza prac badawczych**: wyodrębnianie kluczowych wniosków ze złożonych publikacji w celu szybkiego przeglądu
- **Agregacja wiadomości**: streszczanie artykułów informacyjnych w krótkie codzienne podsumowania lub najważniejsze informacje
- **Notatki ze spotkań**: skracanie transkrypcji do listy działań i zwięzłych podsumowań
- **Przegląd dokumentów prawnych**: szybkie wyodrębnianie istotnych klauzul lub zobowiązań z długich tekstów prawnych
- **Dokumentacja kodu**: generowanie zwięzłych przeglądów repozytoriów i wyjaśnień funkcji
## Następne kroki

- **Dostrajanie (fine-tuning)**: Dostosuj modele do swojej konkretnej dziedziny lub terminologii, aby uzyskać lepszą dokładność (zobacz Fine-tuning Playbooks)
- **Systemy RAG**: Połącz LLM-y z wyszukiwaniem dokumentów, aby uzyskać odpowiedzi i wyszukiwanie uwzględniające kontekst
- **Eksploracja modeli**: Eksperymentuj z nowymi modelami, takimi jak Llama 3, Phi-3 czy Qwen, aby uzyskać lepsze wyniki
- **Wdrożenie produkcyjne**: Korzystaj z narzędzi takich jak vLLM do skalowalnego serwowania LLM-ów w organizacjach

Twój system daje Ci możliwość lokalnego uruchamiania zaawansowanych modeli językowych. Eksperymentuj z różnymi modelami, promptami i parametrami, aby odkryć, co najlepiej sprawdza się w Twoich zastosowaniach.