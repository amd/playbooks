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

vLLM to wysokowydajny silnik wnioskowania zaprojektowany dla dużych modeli językowych (LLM). Zapewnia zoptymalizowane serwowanie z ciągłym wsadowaniem (continuous batching) dla wysokiej przepustowości oraz API zgodne z OpenAI umożliwiające bezproblemową integrację z aplikacjami. Dzięki temu vLLM doskonale sprawdza się w środowiskach produkcyjnych, gdzie kluczowe znaczenie mają szybkość i efektywne wykorzystanie zasobów.

Ten poradnik uczy, jak serwować modele LLM za pomocą skonteneryzowanego vLLM na zintegrowanym GPU oraz jak wchodzić w interakcję z modelami poprzez API OpenAI Python.

## Czego się nauczysz

- Jak skonfigurować i uruchomić serwer vLLM z obsługą AMD ROCm™
- Jak wchodzić w interakcję z modelami za pomocą punktów końcowych API zgodnych z OpenAI
- Jak wysyłać zapytania do lokalnego serwera za pomocą `vllm-prompt`

## Konfiguracja pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

vLLM działa w gotowym kontenerze z wcześniej dopasowanymi ROCm i jego zależnościami. Nie jest wymagana dodatkowa instalacja.

Nie ma etapu instalacji vLLM po stronie hosta. Uruchom vLLM za pomocą:

```bash
vllm-launch
```

Program uruchamiający uruchamia kontener, wskazuje zintegrowane GPU i udostępnia lokalny serwer vLLM zgodny z OpenAI. Alternatywnie kliknij ikonę vLLM na pasku zadań.

## Szybki start

### 1. Sprawdź, czy serwer vLLM działa

Uruchomienie `vllm-launch` może potrwać kilka minut, zanim wszystko zostanie zainicjalizowane. Po uruchomieniu serwer jest dostępny pod adresem `http://localhost:8001`. Pozostaw otwarty terminal uruchomieniowy, ponieważ serwer działa na pierwszym planie, a następnie otwórz osobny terminal na potrzeby pozostałych kroków. Poniższe przykłady wykorzystują `Qwen/Qwen3-1.7B`; jeśli Twój program uruchamiający jest skonfigurowany dla innego modelu, zastąp go odpowiednim identyfikatorem modelu w zapytaniach.

### 2. Wyślij zapytanie

Użyj dostarczonego skryptu `vllm-prompt`, aby wysłać zapytanie do lokalnego serwera vLLM zgodnego z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Rozmowa z modelem za pomocą API OpenAI Python

Ponieważ vLLM udostępnia API zgodne z OpenAI, możesz użyć pakietu Python `openai`, aby z nim współpracować.

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

Utwórz klienta `OpenAI` wskazującego na lokalny serwer vLLM zamiast serwerów OpenAI. Klient wymaga podania `api_key`, ale vLLM go nie weryfikuje, więc zadziała dowolny ciąg znaków:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Następnie wyślij zapytanie chat completion. Wykorzystuje ono ten sam format wiadomości co API OpenAI — listę wiadomości z rolami takimi jak `"user"` i `"assistant"`. Ustawienie `stream=True` oznacza, że odpowiedź będzie napływać stopniowo, a nie od razu w całości:

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

Na koniec przejdź przez otrzymywane fragmenty strumienia i wypisuj każdy fragment tekstu w miarę jego napływania:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Dołączony skrypt [chat_with_model.py](assets/chat_with_model.py) zawiera cały przykład i można go pobrać.


## Wybór i konfiguracja modelu

Domyślnie `vllm-launch` serwuje `Qwen/Qwen3-1.7B` jako model testowy na porcie `8001`. Możesz zmienić model, port oraz parametry serwowania vLLM bez konieczności ponownego budowania lub edytowania kontenera.

### Modele przetestowane przez AMD

Poniższe modele są wstępnie skonfigurowane i zweryfikowane przez AMD:

| Model | Uwagi |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Domyślny model. Lekki i szybki do wczytania. |
| `openai/gpt-oss-20b` | Większy model zapewniający odpowiedzi wyższej jakości. |

### Uruchamianie innego modelu

Przekaż identyfikator modelu za pomocą `--model` (lub `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Zmiana portu

Przekaż port powyżej 1024 za pomocą `--port` (lub `-p`); domyślny to `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Jeśli zmienisz port, upewnij się, że `base_url` klienta wskazuje na ten sam port (na przykład `http://localhost:8080/v1`).

### Przekazywanie dodatkowych parametrów vLLM

Wszelkie dodatkowe argumenty są przekazywane bezpośrednio do vLLM, dzięki czemu możesz dostosować zachowanie serwowania, takie jak długość kontekstu czy typ danych. Istnieją dwa sposoby ich podania.

**W linii**, po opcjach programu uruchamiającego:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trwale**, w pliku konfiguracyjnym pod adresem `~/.local/share/vLLM/vllm-launch.conf`. Ten plik domyślnie nie istnieje — utwórz go i dodaj swoje argumenty jako tablicę Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Użyj `+=`, aby dodać argumenty do domyślnych, zamiast je zastępować:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Aby w dowolnym momencie wyświetlić wszystkie opcje programu uruchamiającego, uruchom:

```bash
vllm-launch --help
```

### Gdzie przechowywane są modele

`vllm-launch` wyszukuje modele w dwóch lokalizacjach:

| Lokalizacja | Ścieżka |
|----------|------|
| Modele systemowe | `/var/cache/models` |
| Modele użytkownika | `~/.local/share/vLLM/models` |

Możesz umieścić pobrany model w dowolnym z tych katalogów i uruchomić go, przekazując jego ścieżkę lub identyfikator do `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Uwaga**: Oczekuje się, że uruchamianie w ten sposób własnego pobranego modelu będzie działać po umieszczeniu modelu w jednym z powyższych katalogów, jednak ten sposób pracy nie został jeszcze oficjalnie zweryfikowany przez AMD.

## Rozwiązywanie problemów

### Połączenie odrzucone

Upewnij się, że serwer działa:
```bash
curl http://localhost:8001/health
```

## Podsumowanie

W tym poradniku nauczyłeś się, jak:

- Uruchomić skonteneryzowany vLLM z obsługą ROCm na zintegrowanym GPU
- Uruchomić serwer vLLM z punktami końcowymi API zgodnymi z OpenAI na porcie 8001
- Wysyłać zapytania za pomocą `vllm-prompt`
- Wykonywać wywołania API do serwera vLLM zarówno w trybie strumieniowym, jak i niestrumieniowym
- Rozwiązywać typowe problemy związane z uruchamianiem serwera, pamięcią i połączeniami klienta

Masz teraz skonteneryzowane wdrożenie vLLM do serwowania dużych modeli językowych z zoptymalizowaną wydajnością na zintegrowanym GPU.

## Kolejne kroki

- **Wypróbuj różne modele** — Użyj `vllm-launch --model <model>`, aby eksperymentować z różnymi modelami LLM i porównywać wydajność (zobacz [Wybór i konfiguracja modelu](#choosing-and-configuring-a-model)).
- **Zbuduj aplikację** — Użyj API zgodnego z OpenAI, aby zintegrować vLLM z aplikacją Python, chatbotem lub przepływem automatyzacji.
- **Dostrajanie i serwowanie** — Dostrój model za pomocą LoRA lub QLoRA, a następnie wdróż go za pomocą vLLM w celu zoptymalizowanego wnioskowania.
## Dodatkowe zasoby

- **[Oficjalna dokumentacja vLLM](https://docs.vllm.ai/)** — Kompleksowe przewodniki i dokumentacja API
- **[Repozytorium vLLM na GitHub](https://github.com/vllm-project/vllm)** — Kod źródłowy, zgłoszenia problemów i dyskusje społeczności