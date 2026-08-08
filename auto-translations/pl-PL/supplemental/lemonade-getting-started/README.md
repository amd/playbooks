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

🍋 **Lemonade** to otwartoźródłowy lokalny serwer AI, który umożliwia uruchamianie dużych modeli językowych (LLM), generatorów obrazów i modeli audio bezpośrednio na własnym sprzęcie. Udostępnia modele za pośrednictwem standardowego w branży **API OpenAI**, dzięki czemu każda aplikacja współpracująca z OpenAI może natychmiast współpracować z Lemonade. Pod koniec tego podręcznika będziesz korzystać z Lemonade do uruchamiania modeli lokalnie na swoim komputerze.

## Czego się nauczysz

Pod koniec tego podręcznika będziesz potrafić:

* **Zainstalować Lemonade Server** i zweryfikować, że działa.
* **Pobrać model LLM i rozmawiać z nim** za pomocą jednego polecenia.
* **Poznać interfejs webowy** i wypróbować różne modalności, takie jak rozpoznawanie obrazu, zamiana mowy na tekst oraz generowanie obrazów.
* **Przełączać backendy GPU** między Vulkan a oprogramowaniem AMD ROCm™.
* **Zbudować aplikację w Pythonie** wykorzystującą lokalny model LLM za pomocą API zgodnego z OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Uruchamiać modele na jednostce AMD Neural Processing Unit (NPU)** za pomocą trybów wykonania Hybrid i FLM na sprzęcie AMD Ryzen™ AI.
<!-- @device:end -->

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie dostępności aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

Zanim zaczniesz, upewnij się, że posiadasz:

- Komputer z systemem **Windows 11** lub obsługiwaną dystrybucją **Linuksa** (Ubuntu 24.04+, Fedora, Debian)
- **16 GB pamięci RAM** jest zalecane dla modelu środowiska uruchomieniowego używanego w krokach 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB lub więcej** jest zalecane, jeśli chcesz użyć większego modelu do generowania kodu w kroku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB wolnego miejsca na dysku**, w zależności od pobieranych modeli. Największy model w tym przewodniku ma około 20 GB.
- **Python 3.10–3.13** (używany w sekcji dotyczącej aplikacji w Pythonie)
- Połączenie internetowe (przewodowe lub bezprzewodowe)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcjonalnie] Jednostka NPU AMD XDNA 2 (seria Ryzen AI 300/400/Max 300 lub Z2 Extreme) z najnowszym sterownikiem zainstalowanym zgodnie z instrukcjami z [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jeśli chcesz uruchamiać model na NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## Podstawowe pojęcia — jak działają lokalne serwery AI

Zanim uruchomimy model, warto zrozumieć, *dlaczego* wszystko jest tak skonfigurowane. Lemonade jest **lokalnym serwerem modeli** — procesem, który ładuje modele AI do pamięci i udostępnia je aplikacjom za pośrednictwem HTTP, podobnie jak robiłaby to usługa AI działająca w chmurze.

### Dlaczego serwer?

| Korzyść | Co to dla Ciebie oznacza |
|---------|----------------------|
| **Uproszczona integracja** | Aplikacje komunikują się z jednym API HTTP zamiast korzystać z bibliotek C++ lub Python specyficznych dla sprzętu. |
| **Współdzielone modele** | Jeden załadowany model może obsługiwać wiele aplikacji jednocześnie, bez zbędnych kopii zajmujących pamięć RAM. |
| **Przenośność między chmurą a lokalnym środowiskiem** | Kod napisany dla API OpenAI działającego w chmurze współpracuje z Lemonade po zmianie tylko jednego adresu URL. |
| **Rozdzielenie odpowiedzialności** | Zarządzanie modelami, przesyłanie strumieniowe i odporność na błędy są obsługiwane przez serwer, dzięki czemu deweloperzy mogą skupić się na swojej aplikacji. |

### Standard API OpenAI

Lemonade implementuje **API OpenAI**, ten sam interfejs, który jest wykorzystywany przez ChatGPT, Azure OpenAI i wiele innych usług. Model konwersacji jest prosty:

| Rola | Kto mówi |
|------|---------------|
| **system** | Instrukcje dla modelu (persona, ograniczenia, dostępne narzędzia) |
| **user** | Wiadomości od człowieka (lub aplikacji) do modelu |
| **assistant** | Odpowiedzi generowane przez model |

Oznacza to, że każda biblioteka lub aplikacja obsługująca OpenAI może komunikować się z Lemonade, wskazując na `http://localhost:13305/api/v1`, gdy Lemonade Server jest uruchomiony.

## Główne ćwiczenie — Twoja pierwsza lokalna rozmowa z AI

Pobierzmy model LLM i przeprowadźmy z nim rozmowę, uruchamiając AI całkowicie na własnym komputerze.

### Krok 1: Pobieranie i uruchamianie modelu

Lemonade jest dostarczany z wyselekcjonowaną biblioteką modeli. Zacznijmy od **Gemma-4-E2B-it**, wydajnego i kompaktowego modelu, który obsługuje również rozpoznawanie obrazu. Otwórz terminal i uruchom:

```
lemonade run Gemma-4-E2B-it-GGUF
```

To pojedyncze polecenie wykonuje trzy czynności:

1. **Pobiera** model (~3 GB) z Hugging Face, jeśli nie został on jeszcze pobrany. (Może to chwilę potrwać)
2. **Uruchamia** proces Lemonade Server na porcie 13305.
3. **Otwiera Lemonade App**, dzięki czemu możesz od razu zacząć rozmawiać z modelem.


<!-- @os:windows -->
W systemie Windows aplikacja Lemonade App uruchamia się automatycznie i możesz od razu rozpocząć rozmowę. Jeśli zainstalowano pakiet `minimal.msi`, aplikacja nie jest w nim zawarta. Aby rozpocząć rozmowę, otwórz przeglądarkę internetową i przejdź pod adres `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
W systemie Linux otwórz przeglądarkę i przejdź pod adres `http://localhost:13305`, aby uzyskać dostęp do aplikacji webowej.
<!-- @os:end -->

Spróbuj wpisać pytanie:

```
What are three fun facts about lemons?
```

Model odpowie bezpośrednio w oknie czatu. **Gratulacje! Uruchamiasz duży model językowy lokalnie.**

![Aplikacja Lemonade z widocznymi logami](../../dependencies/assets/ChatwithLogs.png)

W panelu logów serwera w aplikacji Lemonade App możesz znaleźć dane telemetryczne dotyczące wydajności modelu po każdej odpowiedzi. Na przykład:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Krok 2: Poznaj interfejs webowy i różne modalności

Lemonade zawiera wbudowany interfejs webowy, w którym możesz:

- **Wchodzić w interakcję** z załadowanym modelem w znajomym oknie czatu
- **Przeglądać modele** w zakładce Model Manager
- **Pobierać nowe modele** jednym kliknięciem

Spróbuj przełączać się między różnymi modalnościami, korzystając z zakładki **Model Manager** w interfejsie webowym, gdzie możesz przeglądać modele według Recipe lub Category:

1. **Wizja:** Załadowany już przez Ciebie model `Gemma-4-E2B-it-GGUF` obsługuje wizję. Wklej obraz do okna czatu i poproś model o jego opisanie.
2. **Generowanie obrazów:** W kategorii Image pobierz model obrazu, taki jak `SDXL-Turbo`, z Model Manager, a następnie użyj Lemonade Image Generator, aby wpisać prompt i wygenerować obraz lokalnie.
3. **Dźwięk:** W kategorii Audio pobierz model audio, taki jak `Whisper-Tiny`, który potrafi zamieniać mowę na tekst. Podaj nagranie audio, aby przetranskrybować je lokalnie. Aby zamienić tekst na mowę, wypróbuj jeden z modeli w kategorii Speech, na przykład `kokoro-v1`.

![Multi-Modality with Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Wypróbuj model z innym backendem

Jeśli najedziesz kursorem na model w aplikacji Lemonade, zobaczysz ikonę koła zębatego. Kliknięcie jej pozwala wybrać opcje modelu, w tym wybrać żądany backend.

Domyślnie Lemonade używa Vulkan do akceleracji GPU. Jeśli masz obsługiwaną kartę graficzną dyskretną AMD, możesz przełączyć się na ROCm.

![Lemonade Select Backend](../../dependencies/assets/lemonademodeloptions.png)

Aby zarządzać zainstalowanymi backendami, kliknij przycisk backendu w skrajnie lewej kolumnie.

Alternatywnie możesz określić backend za pomocą następującego polecenia:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Możesz również ustawić domyślny backend za pomocą zmiennej środowiskowej `LEMONADE_LLAMACPP` z wartościami: `vulkan`, `rocm` lub `cpu`.

---

## Idąc dalej — zbuduj aplikację opartą na AI w Pythonie

Prawdziwa siła lokalnego serwera AI polega na tym, że każda aplikacja może się z nim połączyć za pomocą zaledwie kilku linii kodu. Aby to udowodnić, zbudujmy niewielki, ale funkcjonalny **generator fiszek do nauki**, w którym podajesz temat, a on generuje fiszki, dzięki którym możesz interaktywnie się sprawdzać.

### Krok 4: Uruchom serwer

Sprawdź, czy serwer Lemonade jest uruchomiony. Zazwyczaj uruchamia się automatycznie w tle po instalacji. Aby to sprawdzić, uruchom:

```
lemonade status
```

Powinieneś zobaczyć komunikat podobny do: `Server is running on port 13305`.

Jeśli serwer nie jest uruchomiony, uruchom go, otwierając aplikację Lemonade. Użyj domyślnego portu **13305** (możesz go potwierdzić lub wybrać z ikony w zasobniku systemowym).

### Krok 5: Zainstaluj klienta OpenAI Python

W terminalu utwórz środowisko venv i zainstaluj klienta OpenAI Python za pomocą następujących poleceń:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Krok 6: Zbuduj aplikację do fiszek

Pobierzmy inny model do generowania kodu: `Qwen3.5-35B-A3B-GGUF`. Jest to duży (~20 GB) i wydajny model, najlepiej dopasowany do systemów z 32 GB+ pamięci RAM. Jeśli masz mniej dostępnej pamięci RAM, wypróbuj zamiast niego `Qwen3.5-9B-GGUF` (~6 GB).

Możesz go pobrać z interfejsu użytkownika lub uruchomić:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Wprowadź poniższy prompt do interfejsu Lemonade Chat UI, aby wygenerować kod prostej aplikacji do fiszek. 

Użyjemy Qwen3.5-35B-A3B-GGUF (większego modelu, lepiej radzącego sobie z pisaniem kodu) do wygenerowania naszej aplikacji w Pythonie, a sama aplikacja będzie w czasie działania wywoływać Gemma-4-E2B-it-GGUF (mniejszy model, który już pobrałeś). Kod można następnie skopiować do wybranego przez siebie pliku, aby uruchomić go w Pythonie.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Wskazówka**: Zastosowaliśmy standardowe praktyki inżynierskie poprzez dokładne przygotowanie promptu oraz wykorzystanie systemu dwóch modeli w celu optymalizacji zasobów i szybkości.

Dla wygody dostarczyliśmy przykładowe wyjście w pliku [`flashcards.py`](assets/flashcards.py). Możesz pobrać go do swojego katalogu. Tak czy inaczej, powinieneś teraz mieć plik Python gotowy do uruchomienia.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Krok 7: Uruchom wygenerowany kod

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Oto co powinieneś zobaczyć:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

W około 150 liniach kodu zbudowałeś w pełni funkcjonalne narzędzie do nauki zasilane przez lokalny LLM. Nie ma klucza API do zarządzania, nie ma kosztów użytkowania, a żadne dane nigdy nie opuszczają Twojego komputera.

> **Kluczowa obserwacja:** Zauważ, że linia `client = OpenAI(base_url=...) ` jest *jedyną* rzeczą, która łączy tę aplikację z Lemonade zamiast z chmurą OpenAI. Reszta kodu jest identyczna z tym, co napisałbyś dla dowolnej usługi kompatybilnej z OpenAI. Jeśli kiedykolwiek korzystałeś z biblioteki OpenAI Python, już wiesz, jak budować aplikacje z Lemonade.

### Co to pokazuje

Ta niewielka aplikacja wykorzystuje kilka rzeczywistych wzorców integracji:

| Wzorzec | Gdzie występuje |
|---------|-----------------|
| **Prompty systemowe** | Wiadomość `"system"` informuje LLM, aby zwrócił ustrukturyzowany JSON |
| **Ustrukturyzowane wyjście** | Aplikacja parsuje odpowiedź LLM jako JSON, aby zbudować fiszki |
| **Żądania bezstanowe** | Każde wywołanie `generate_flashcards()` jest niezależne |
| **Obsługa błędów** | `try/except` w bezpieczny sposób obsługuje przypadki, gdy wyjście LLM nie jest poprawnym JSON-em |

Te same wzorce skalują się do dowolnych aplikacji, takich jak chatboty, asystenci kodu, generatory treści czy narzędzia do automatyzacji.

#### Wyzwanie dodatkowe

* Aby podnieść poprzeczkę, spróbuj zaktualizować aplikację tak, aby fiszki były odczytywane użytkownikowi, korzystając z przykładu dostępnego [tutaj](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Uruchamianie modeli na NPU (opcjonalnie)

Jeśli masz procesor Ryzen AI 300/400/Max 300 series lub Z2 Extreme, Twoje urządzenie posiada wbudowaną **jednostkę przetwarzania neuronowego (NPU)** — dedykowany układ zaprojektowany specjalnie pod kątem obciążeń AI. Uruchamianie modeli na NPU jest bardziej energooszczędne niż korzystanie z GPU, co czyni je idealnym rozwiązaniem do zadań AI działających w tle, dłuższych sesji oraz pracy na zasilaniu bateryjnym.

Lemonade obsługuje trzy tryby wykonywania na NPU, wszystkie w sposób przezroczysty za pośrednictwem tego samego API OpenAI:

| Tryb | Jak to działa | Recepta | Przykładowe modele |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU przetwarza prompt, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Tylko NPU** | Całe wnioskowanie odbywa się na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Wykorzystuje silnik FastFlowLM na NPU, zoptymalizowany pod AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Wymagania

- Procesor **AMD Ryzen AI 300/400 series lub Z2 series**
- Dla modeli **FLM**: środowisko uruchomieniowe FLM można zainstalować z poziomu aplikacji Lemonade, lub Lemonade automatycznie zainstaluje środowisko uruchomieniowe FLM podczas uruchamiania modelu FLM. Aby dowiedzieć się więcej o FastFlowLM, zobacz [tutaj](https://fastflowlm.com/docs/).


### Krok 8: Uruchom model hybrydowy

Modele hybrydowe rozdzielają pracę pomiędzy NPU i iGPU, zapewniając dobrą równowagę między szybkością a wydajnością energetyczną. W aplikacji Lemonade wybierz model z listy `Ryzen AI LLM`, na przykład `Qwen3-4B-Hybrid`, lub uruchom go za pomocą następującego polecenia:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automatycznie wykrywa Twoje NPU i instaluje backend **Ryzen AI LLM**.

> **Co się dzieje w tle?** Gdy wysyłasz wiadomość, NPU przetwarza cały Twój prompt równolegle (nazywa się to „prefill”). Następnie iGPU przejmuje zadanie generowania odpowiedzi token po tokenie (nazywa się to „decode”). To hybrydowe podejście wykorzystuje mocne strony każdego z układów.

### Krok 9: Uruchom model FLM

Modele FastFlowLM (FLM) są specjalnie zoptymalizowane pod architekturę NPU AMD XDNA2 i mogą działać bardzo szybko jak na swój rozmiar. Na przykład wybierz `qwen3.5-4b-FLM` z listy `FastFlowLM NPU` lub użyj następującego polecenia:

<!-- @os:windows -->
Aby włączyć `FastFlowLM` w systemie Windows:

* Otwórz menu `Backends Manager`.
* Znajdź kategorię backendu `FastFlowLM NPU`.
* Kliknij Install NPU.
* Po zakończeniu instalacji w menu rozwijanym FFLM będzie dostępnych ~36 domyślnych modeli.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Przy pierwszym uruchomieniu aplikacji `Lemonade` backend `FastFlowNPU` nie jest domyślnie włączony. 
Aplikacja lokalna otworzy stronę instalacji, aby przeprowadzić Cię przez proces konfiguracji.

Aby włączyć `FastFlowLM` w systemie Linux:

* Otwórz aplikację `Lemonade`.
* Odwiedź [oficjalną dokumentację FLM](https://lemonade-server.ai/flm_npu_linux.html) i wykonaj kroki instalacji FLM, wybierając swoją dystrybucję Linuksa.
* Włącz backports zgodnie z instrukcjami na stronie instalacji.
* Pobierz najnowsze wydanie `v0.9.x` ze [strony tagów](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
W przypadku AMD Halo Developer Platform, upewnij się, że wybrano Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Zainstaluj pobrany pakiet `.deb`.
* Zalecane: Zamknij aplikację `Lemonade App` i otwórz ją ponownie, aby zmiany zostały wykryte.
* Zalecane: Otwórz `Backends Manager` i kliknij Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Po pomyślnej instalacji powinieneś zobaczyć, że `flm:npu` zostało ukończone w **Menedżerze pobierania** wewnątrz **aplikacji Lemonade Desktop**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Następnie możesz wybrać dowolny z dostępnych modeli FFLM i rozpocząć korzystanie z backendu NPU.

Aby pobrać konkretny model, pobierz żądany model ze [strony modeli](https://fastflowlm.com/docs/models/qwen/) i zweryfikuj go za pomocą polecenia powłoki podanego w dokumentacji.
```
flm run qwen3.5-4b-FLM
```
lub przez 
```
lemonade run qwen3.5-4b-FLM
```

Modele FLM obejmują niektóre z najpopularniejszych architektur (Gemma 3, Qwen 3, Llama 3 i DeepSeek R1) i mają rozmiar od poniżej 1 GB do ponad 13 GB.
Lemonade automatycznie wykrywa Twoje NPU i instaluje backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Wskazówka:** Aby uzyskać najlepszą wydajność NPU, włącz tryb turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Zmiana modeli

Aplikacja z fiszkami z Kroku 6 działa również z modelami NPU, wystarczy zmienić nazwę modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Następne kroki

Masz teraz uruchomiony lokalny serwer AI na własnym sprzęcie, oto co możesz zrobić dalej:

1. **Połącz swoje ulubione aplikacje**: Lemonade działa od razu z [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) oraz [wieloma innymi](https://lemonade-server.ai/marketplace).

2. **Przeglądaj więcej modeli**: Zapoznaj się z pełną [biblioteką modeli](https://lemonade-server.ai/docs/server/server_models/), aby znaleźć modele zoptymalizowane pod kodowanie, wnioskowanie, przetwarzanie obrazu i inne. Użyj aplikacji Lemonade lub polecenia `lemonade list`, aby zobaczyć dostępne opcje.

3. **Odblokuj akcelerację GPU ROCm**: Jeśli posiadasz obsługiwane GPU AMD, przełącz się na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Zobacz [obsługiwane GPU AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Przeczytaj pełną specyfikację API**: Lemonade obsługuje uzupełnianie czatu, embeddingi, transkrypcję audio, generowanie obrazów, syntezę mowy i wiele więcej. Zobacz [Specyfikację serwera](https://lemonade-server.ai/docs/server/server_spec/), aby poznać wszystkie endpointy.

5. **Współtwórz projekt**: Lemonade jest projektem open source. Zapoznaj się z [przewodnikiem współtworzenia](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) i poszukaj [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->