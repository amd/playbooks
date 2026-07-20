<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten podręcznik wykorzystuje specjalne tagi, których GitHub nie potrafi wyświetlić. Odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę zawartość.
<!-- @github-only:end -->


## Przegląd

vLLM to wysokowydajny silnik wnioskowania zaprojektowany dla dużych modeli językowych (LLM). Zapewnia zoptymalizowane serwowanie z ciągłym batchowaniem (continuous batching) dla wysokiej przepustowości oraz API kompatybilne z OpenAI umożliwiające bezproblemową integrację z aplikacjami. Dzięki temu vLLM świetnie sprawdza się w środowiskach produkcyjnych, w których kluczowe znaczenie mają szybkość i efektywne wykorzystanie zasobów.

Ten podręcznik pokazuje, jak serwować modele LLM za pomocą skonteneryzowanego vLLM na zintegrowanym GPU oraz jak wchodzić w interakcję z modelami za pomocą OpenAI Python API.

## Czego się nauczysz

- Jak skonfigurować i uruchomić serwer vLLM z obsługą AMD ROCm™
- Jak wchodzić w interakcję z modelami za pomocą punktów końcowych API kompatybilnych z OpenAI
- Jak wysyłać prompty do lokalnego serwera za pomocą `vllm-prompt`

## Konfiguracja pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

Ten podręcznik wykorzystuje gotowy obraz kontenera, który zawiera vLLM, obsługę ROCm oraz skrypty pomocnicze niezbędne do uruchomienia serwera. Nie musisz ręcznie instalować PyTorch, vLLM ani lokalnych skryptów podręcznika.

Nie ma potrzeby instalacji vLLM po stronie hosta. Uruchom vLLM za pomocą:

```bash
vllm-launch
```

Launcher uruchamia kontener, kieruje go do zintegrowanego GPU i udostępnia lokalny serwer vLLM kompatybilny z OpenAI. Alternatywnie kliknij ikonę vLLM na pasku zadań.

## Szybki start

### 1. Potwierdź, że serwer vLLM działa

Uruchomienie `vllm-launch` może potrwać kilka minut, zanim wszystko zostanie zainicjalizowane. Po uruchomieniu serwer jest dostępny pod adresem `http://localhost:8001`. Pozostaw terminal uruchamiający otwarty, ponieważ serwer działa na pierwszym planie, a następnie otwórz osobny terminal, aby wykonać pozostałe kroki. Poniższe przykłady wykorzystują `Qwen/Qwen3-1.7B`; jeśli launcher jest skonfigurowany dla innego modelu, w żądaniach podaj identyfikator tego modelu.

### 2. Wyślij prompt

Użyj dostarczonego skryptu `vllm-prompt`, aby wysłać żądanie do lokalnego serwera vLLM kompatybilnego z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Rozmowa z modelem za pomocą OpenAI Python API

Ponieważ vLLM udostępnia API kompatybilne z OpenAI, możesz użyć pakietu Python `openai`, aby z nim współpracować.

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

Utwórz klienta `OpenAI` skierowanego na lokalny serwer vLLM zamiast na serwery OpenAI. `api_key` jest wymagany przez klienta, ale vLLM go nie waliduje, więc zadziała dowolny ciąg znaków:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Następnie wyślij żądanie chat completion. Wykorzystuje ono ten sam format wiadomości co API OpenAI — listę wiadomości z rolami takimi jak `"user"` i `"assistant"`. Ustawienie `stream=True` oznacza, że odpowiedź będzie napływać stopniowo, a nie od razu w całości:

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

Na koniec przejdź iteracyjnie przez strumieniowane fragmenty i wyświetlaj każdy fragment tekstu w miarę jego napływania:

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

W tym podręczniku nauczyłeś się, jak:

- Uruchomić skonteneryzowany vLLM z obsługą ROCm na zintegrowanym GPU
- Uruchomić serwer vLLM z punktami końcowymi API kompatybilnymi z OpenAI na porcie 8001
- Wysyłać prompty za pomocą `vllm-prompt`
- Wykonywać wywołania API do serwera vLLM zarówno w trybie strumieniowym, jak i niestrumieniowym
- Rozwiązywać typowe problemy związane z uruchamianiem serwera, pamięcią i połączeniami klientów

Masz teraz skonteneryzowane wdrożenie vLLM do serwowania dużych modeli językowych z zoptymalizowaną wydajnością na zintegrowanym GPU.

## Kolejne kroki

- **Wypróbuj różne modele** — Zmień model w konfiguracji `vllm-launch`, aby eksperymentować z różnymi modelami LLM i porównywać wydajność.
- **Zbuduj aplikację** — Wykorzystaj API kompatybilne z OpenAI, aby zintegrować vLLM z aplikacją Python, chatbotem lub przepływem automatyzacji.
- **Dostrajaj i serwuj** — Dostrój model za pomocą LoRA lub QLoRA, a następnie wdróż go za pomocą vLLM w celu zoptymalizowanego wnioskowania.

## Dodatkowe zasoby

- **[Oficjalna dokumentacja vLLM](https://docs.vllm.ai/)** — Kompleksowe przewodniki i dokumentacja API
- **[Repozytorium vLLM na GitHub](https://github.com/vllm-project/vllm)** — Kod źródłowy, zgłoszenia problemów i dyskusje społeczności