<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten poradnik używa specjalnych tagów, których GitHub nie może renderować. Odwiedź [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę zawartość.
<!-- @github-only:end -->


## Przegląd

vLLM to wysokowydajny silnik wnioskowania zaprojektowany dla dużych modeli językowych (LLM). Zapewnia zoptymalizowane serwowanie z ciągłym przetwarzaniem wsadowym dla wysokiej przepustowości oraz interfejs API zgodny z OpenAI umożliwiający bezproblemową integrację aplikacji. Dzięki temu vLLM doskonale nadaje się do wdrożeń produkcyjnych, gdzie kluczowe są szybkość i efektywność zasobów.

Ten poradnik uczy, jak serwować LLM przy użyciu skonteneryzowanego vLLM na zintegrowanym GPU oraz jak komunikować się z modelami za pośrednictwem interfejsu API Python OpenAI.

## Czego się nauczysz

- Jak skonfigurować i uruchomić serwer vLLM z obsługą AMD ROCm™
- Jak komunikować się z modelami za pośrednictwem punktów końcowych API zgodnych z OpenAI
- Jak wysyłać zapytania do lokalnego serwera za pomocą `vllm-prompt`

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

Ten poradnik używa wstępnie zbudowanego obrazu kontenera zawierającego vLLM, obsługę ROCm oraz skrypty pomocnicze potrzebne do uruchomienia serwera. Nie musisz ręcznie instalować PyTorch, vLLM ani lokalnych skryptów poradnika.

Nie ma kroku instalacji vLLM po stronie hosta. Uruchom vLLM za pomocą:

```bash
vllm-launch
```

Program uruchamiający startuje kontener, wskazuje zintegrowany GPU i udostępnia lokalny serwer vLLM zgodny z OpenAI. Alternatywnie kliknij ikonę vLLM na pasku zadań.

## Szybki start

### 1. Potwierdź, że serwer vLLM działa

Inicjalizacja `vllm-launch` może potrwać kilka minut. Po uruchomieniu serwer jest dostępny pod adresem `http://localhost:8001`. Pozostaw terminal uruchamiający otwarty, ponieważ serwer działa na pierwszym planie, a następnie otwórz osobny terminal dla pozostałych kroków. Poniższe przykłady używają `Qwen/Qwen3-1.7B`; jeśli program uruchamiający jest skonfigurowany dla innego modelu, zastąp ten identyfikator modelu w żądaniach.

### 2. Wyślij zapytanie

Użyj dostarczonego skryptu `vllm-prompt`, aby wysłać żądanie do lokalnego serwera vLLM zgodnego z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Rozmawiaj z modelem przy użyciu interfejsu API Python OpenAI

Ponieważ vLLM udostępnia interfejs API zgodny z OpenAI, możesz użyć pakietu Python `openai` do komunikacji z nim.

Najpierw utwórz wirtualne środowisko Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Zainstaluj pakiet OpenAI
```bash
pip install openai
```

Utwórz klienta `OpenAI` wskazującego na lokalny serwer vLLM zamiast serwerów OpenAI. Parametr `api_key` jest wymagany przez klienta, ale vLLM go nie weryfikuje, więc działa dowolny ciąg znaków:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Następnie wyślij żądanie uzupełnienia czatu. Używa ono tego samego formatu wiadomości co interfejs API OpenAI — listy wiadomości z rolami takimi jak `"user"` i `"assistant"`. Ustawienie `stream=True` oznacza, że odpowiedź będzie przychodzić stopniowo, a nie wszystko naraz:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Na koniec iteruj po strumieniowanych fragmentach i wyświetlaj każdy fragment tekstu w miarę jego napływania:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Dołączony skrypt [chat_with_model.py](assets/chat_with_model.py) zawiera cały przykład i można go pobrać.


## Rozwiązywanie problemów

### Odmowa połączenia

Upewnij się, że serwer działa:
```bash
curl http://localhost:8001/health
```

## Podsumowanie

W tym poradniku nauczyłeś się, jak:

- Uruchamiać skonteneryzowany vLLM z obsługą ROCm na zintegrowanym GPU
- Uruchamiać serwer vLLM z punktami końcowymi API zgodnymi z OpenAI na porcie 8001
- Wysyłać zapytania za pomocą `vllm-prompt`
- Wykonywać wywołania API do serwera vLLM przy użyciu żądań strumieniowanych i niestrumieniowanych
- Rozwiązywać typowe problemy z uruchamianiem serwera, pamięcią i połączeniami klientów

Masz teraz skonteneryzowane wdrożenie vLLM do serwowania dużych modeli językowych ze zoptymalizowaną wydajnością na zintegrowanym GPU.

## Następne kroki

- **Wypróbuj różne modele** — Zamień model w konfiguracji `vllm-launch`, aby eksperymentować z różnymi LLM i porównywać wydajność.
- **Zbuduj aplikację** — Użyj interfejsu API zgodnego z OpenAI, aby zintegrować vLLM z aplikacją Python, chatbotem lub przepływem pracy automatyzacji.
- **Dostrajaj i serwuj** — Dostraj model przy użyciu LoRA lub QLoRA, a następnie wdróż go za pomocą vLLM w celu zoptymalizowanego wnioskowania.

## Dodatkowe zasoby

- **[Oficjalna dokumentacja vLLM](https://docs.vllm.ai/)** — Kompleksowe przewodniki i dokumentacja API
- **[Repozytorium vLLM na GitHub](https://github.com/vllm-project/vllm)** — Kod źródłowy, zgłoszenia i dyskusje społeczności