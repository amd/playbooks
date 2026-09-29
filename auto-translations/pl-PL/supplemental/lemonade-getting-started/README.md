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

🍋 **Lemonade** to otwarty, lokalny serwer AI, który umożliwia uruchamianie dużych modeli językowych (LLM), generatorów obrazów oraz modeli audio bezpośrednio na własnym sprzęcie. Udostępnia modele za pośrednictwem branżowego standardu **OpenAI API**, dzięki czemu każda aplikacja współpracująca z OpenAI może natychmiast współpracować z Lemonade. Na koniec tego przewodnika będziesz korzystać z Lemonade do uruchamiania modeli lokalnie na swoim komputerze.

## Czego się nauczysz

Po ukończeniu tego przewodnika będziesz w stanie:

* **Zainstalować Lemonade Server** i zweryfikować, że działa.
* **Pobrać i porozmawiać z LLM** za pomocą jednego polecenia.
* **Poznać interfejs webowy** i wypróbować różne modalności, takie jak rozpoznawanie obrazu, zamiana mowy na tekst oraz generowanie obrazów.
* **Przełączać backendy GPU** między Vulkan a oprogramowaniem AMD ROCm™.
* **Zbudować aplikację w Pythonie** wykorzystującą lokalny LLM za pomocą interfejsu API zgodnego z OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Uruchamiać modele na jednostce AMD Neural Processing Unit (NPU)** przy użyciu trybów wykonania Hybrid i FLM na sprzęcie AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacja wymaganego oprogramowania

Zanim zaczniesz, upewnij się, że posiadasz:

- Komputer z systemem **Windows 11** lub obsługiwaną dystrybucją **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Zalecane jest **16 GB pamięci RAM** dla modelu wykorzystywanego w krokach 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). Zalecane jest **32 GB+**, jeśli chcesz użyć większego modelu do generowania kodu w kroku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **Około 4–30 GB wolnego miejsca na dysku**, w zależności od pobieranych modeli. Największy model w tym przewodniku ma około 20 GB.
- **Python 3.10–3.13** (używany w sekcji dotyczącej aplikacji w Pythonie)
- Połączenie z internetem (przewodowe lub bezprzewodowe)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcjonalnie] NPU AMD XDNA 2 (Ryzen AI serii 300/400/Max 300 lub Z2 Extreme) z najnowszym sterownikiem zainstalowanym zgodnie z [instrukcjami instalacji oprogramowania Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jeśli chcesz uruchamiać model na NPU.
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
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
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

Zanim uruchomimy model, warto zrozumieć, *dlaczego* wszystko jest skonfigurowane w ten sposób. Lemonade jest **lokalnym serwerem modeli**, czyli procesem, który wczytuje modele AI do pamięci i udostępnia je aplikacjom poprzez HTTP, dokładnie tak, jak robiłaby to usługa AI działająca w chmurze.

### Dlaczego serwer?

| Korzyść | Co to oznacza dla Ciebie |
|---------|----------------------|
| **Uproszczona integracja** | Aplikacje komunikują się z jednym API HTTP zamiast korzystać ze specyficznych dla sprzętu bibliotek C++ lub Pythona. |
| **Współdzielone modele** | Jeden wczytany model może obsługiwać wiele aplikacji jednocześnie, bez duplikowania kopii zajmujących Twoją pamięć RAM. |
| **Przenośność między chmurą a lokalnym środowiskiem** | Kod napisany dla chmurowego API OpenAI działa z Lemonade po zmianie jednego adresu URL. |
| **Rozdzielenie odpowiedzialności** | Zarządzanie modelami, przesyłanie strumieniowe i tolerancja błędów są obsługiwane przez serwer, dzięki czemu programiści mogą skupić się na swojej aplikacji. |

### Standard OpenAI API

Lemonade implementuje **OpenAI API**, ten sam interfejs, którego używają ChatGPT, Azure OpenAI i wiele innych usług. Model konwersacji jest prosty:

| Rola | Kto się wypowiada |
|------|---------------|
| **system** | Instrukcje dla modelu (persona, ograniczenia, dostępne narzędzia) |
| **user** | Wiadomości od człowieka (lub aplikacji) do modelu |
| **assistant** | Odpowiedzi generowane przez model |

Oznacza to, że dowolna biblioteka lub aplikacja obsługująca OpenAI może komunikować się z Lemonade, wskazując na `http://localhost:13305/api/v1` podczas działania Lemonade Server.

## Główne ćwiczenie — Twój pierwszy lokalny czat AI

Pobierzmy LLM i porozmawiajmy z nim, uruchamiając AI w całości na własnym komputerze.

### Krok 1: Pobieranie i uruchamianie modelu

Lemonade jest dostarczane z wyselekcjonowaną biblioteką modeli. Zacznijmy od **Gemma-4-E2B-it**, kompaktowego i wydajnego modelu, który obsługuje również rozpoznawanie obrazu. Otwórz terminal i uruchom:

```
lemonade run Gemma-4-E2B-it-GGUF
```

To pojedyncze polecenie wykonuje trzy czynności:

1. **Pobiera** model (~3 GB) z Hugging Face, jeśli nie został jeszcze pobrany. (Może to chwilę potrwać)
2. **Uruchamia** proces Lemonade Server na porcie 13305.
3. **Otwiera Lemonade App**, dzięki czemu możesz od razu rozpocząć rozmowę z modelem.


<!-- @os:windows -->
W systemie Windows aplikacja Lemonade App uruchamia się automatycznie i możesz od razu rozpocząć rozmowę. Jeśli zainstalowano pakiet `minimal.msi`, aplikacja nie jest dołączona. Aby rozpocząć rozmowę, otwórz przeglądarkę internetową i przejdź do `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
W systemie Linux otwórz przeglądarkę i przejdź do `http://localhost:13305`, aby uzyskać dostęp do aplikacji webowej.
<!-- @os:end -->

Spróbuj wpisać pytanie:

```
What are three fun facts about lemons?
```

Model odpowie bezpośrednio w oknie czatu. **Gratulacje! Właśnie uruchomiłeś lokalnie duży model językowy.**

![Lemonade App z wyświetlonymi logami](../../dependencies/assets/ChatwithLogs.png)

W panelu logów serwera w aplikacji Lemonade App znajdziesz dane telemetryczne dotyczące wydajności modelu po każdej odpowiedzi. Na przykład:

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
- **Przeglądać modele** na karcie Model Manager
- **Pobierać nowe modele** jednym kliknięciem

Spróbuj przełączać się między różnymi modalnościami, korzystając z karty **Model Manager** w interfejsie webowym, gdzie możesz przeglądać modele według Recipe lub Category:

1. **Wizja:** Model `Gemma-4-E2B-it-GGUF`, który masz już załadowany, obsługuje wizję. Wklej obraz do okna czatu i poproś model o jego opisanie.
2. **Generowanie obrazów:** W kategorii Image pobierz model do generowania obrazów, taki jak `SDXL-Turbo`, z Model Manager, a następnie użyj Lemonade Image Generator, aby wpisać prompt i wygenerować obraz lokalnie.
3. **Dźwięk:** W kategorii Audio pobierz model audio, taki jak `Whisper-Tiny`, który potrafi zamieniać mowę na tekst. Podaj nagranie audio, aby przetranskrybować je lokalnie. Do zamiany tekstu na mowę wypróbuj jeden z modeli w kategorii Speech, na przykład `kokoro-v1`.

![Wielomodalność z Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Wypróbuj model z innym backendem

Jeśli najedziesz kursorem na model w aplikacji Lemonade, zobaczysz ikonę zębatki. Kliknięcie jej pozwala wybrać opcje modelu, w tym wybór żądanego backendu.

Domyślnie Lemonade używa Vulkan do akceleracji GPU. Jeśli masz obsługiwany dedykowany GPU AMD, możesz przełączyć się na ROCm.

![Wybór backendu Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Aby zarządzać zainstalowanymi backendami, kliknij przycisk backendu w skrajnie lewej kolumnie.

Alternatywnie możesz określić backend za pomocą następującego polecenia:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Możesz też ustawić domyślny backend za pomocą zmiennej środowiskowej `LEMONADE_LLAMACPP` z wartościami: `vulkan`, `rocm` lub `cpu`.

---

## Idąc dalej — zbuduj aplikację z AI w Pythonie

Prawdziwa siła lokalnego serwera AI polega na tym, że dowolna aplikacja może się z nim połączyć za pomocą zaledwie kilku linii kodu. Aby to udowodnić, zbudujmy niewielki, ale w pełni funkcjonalny **generator fiszek do nauki**, w którym podajesz temat, a on generuje fiszki, które możesz następnie interaktywnie przeglądać w formie quizu.

### Krok 4: Uruchom serwer

Sprawdź, czy serwer Lemonade jest uruchomiony. Zazwyczaj startuje automatycznie w tle po instalacji. Aby to sprawdzić, uruchom:

```
lemonade status
```

Powinieneś zobaczyć komunikat podobny do: `Server is running on port 13305`.

Jeśli serwer nie jest uruchomiony, uruchom go, otwierając aplikację Lemonade. Użyj domyślnego portu **13305** (możesz go potwierdzić lub wybrać z ikony w zasobniku systemowym).

### Krok 5: Zainstaluj klienta Python OpenAI

W terminalu utwórz venv i zainstaluj klienta Python OpenAI za pomocą następujących poleceń:
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

### Krok 6: Zbuduj aplikację z fiszkami

Pobierzmy inny model do generowania kodu: `Qwen3.5-35B-A3B-GGUF`. To duży (~20 GB) i wydajny model, najlepiej dopasowany do systemów z 32 GB+ pamięci RAM. Jeśli masz mniej dostępnej pamięci RAM, spróbuj zamiast tego `Qwen3.5-9B-GGUF` (~6 GB).

Możesz go pobrać z poziomu interfejsu użytkownika lub uruchomić następujące polecenie:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Wprowadź następujący prompt do interfejsu czatu Lemonade, aby wygenerować kod prostej aplikacji z fiszkami.

Użyjemy Qwen3.5-35B-A3B-GGUF (większego modelu, lepszego w pisaniu kodu) do wygenerowania naszej aplikacji w Pythonie, a sama aplikacja będzie w czasie działania wywoływać Gemma-4-E2B-it-GGUF (mniejszy model, który już pobrałeś). Kod można następnie skopiować do wybranego pliku, aby uruchomić go w Pythonie.

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

> **Wskazówka:** Zastosowaliśmy standardowe praktyki inżynierskie poprzez dokładne opracowanie promptu oraz wykorzystanie systemu dwóch modeli w celu optymalizacji zasobów i szybkości działania.

Dla wygody udostępniliśmy przykładowy wynik w pliku [`flashcards.py`](assets/flashcards.py). Możesz go pobrać do swojego katalogu. Tak czy inaczej, powinieneś teraz mieć plik Python gotowy do uruchomienia.

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

W około 150 liniach kodu zbudowałeś w pełni funkcjonalne narzędzie do nauki oparte na lokalnym LLM. Nie ma tu żadnego klucza API do zarządzania, żadnych kosztów użytkowania i żadne dane nigdy nie opuszczają Twojego komputera.

> **Kluczowa obserwacja:** Zwróć uwagę, że linia `client = OpenAI(base_url=...) ` jest *jedynym* elementem łączącym tę aplikację z Lemonade zamiast z chmurą OpenAI. Reszta kodu jest identyczna z tą, którą napisałbyś dla dowolnej usługi kompatybilnej z OpenAI. Jeśli kiedykolwiek korzystałeś z biblioteki Python OpenAI, już wiesz, jak budować aplikacje z Lemonade.

### Co to demonstruje

Ta niewielka aplikacja pokazuje kilka wzorców integracji spotykanych w rzeczywistych zastosowaniach:

| Wzorzec | Gdzie występuje |
|---------|-----------------|
| **Prompty systemowe** | Wiadomość `"system"` informuje LLM, aby zwrócił ustrukturyzowany JSON |
| **Ustrukturyzowane wyjście** | Aplikacja parsuje odpowiedź LLM jako JSON, aby zbudować fiszki |
| **Bezstanowe żądania** | Każde wywołanie `generate_flashcards()` jest niezależne |
| **Obsługa błędów** | `try/except` w elegancki sposób obsługuje przypadki, gdy odpowiedź LLM nie jest poprawnym JSON-em |

Te same wzorce skalują się do dowolnej aplikacji, takiej jak chatboty, asystenci kodowania, generatory treści czy narzędzia do automatyzacji.

#### Wyzwanie dodatkowe

* Dla dodatkowego wyzwania spróbuj zaktualizować aplikację tak, aby fiszki były odczytywane użytkownikowi na głos, korzystając z przykładu dostępnego [tutaj](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Uruchamianie modeli na NPU (opcjonalnie)

Jeśli posiadasz urządzenie z serii Ryzen AI 300/400/Max 300 lub Z2 Extreme, Twoje urządzenie ma wbudowany **Neural Processing Unit (NPU)** — dedykowany układ zaprojektowany specjalnie do obciążeń AI. Uruchamianie modeli na NPU jest bardziej energooszczędne niż korzystanie z GPU, co czyni go idealnym rozwiązaniem do zadań AI działających w tle, dłuższych sesji oraz pracy zasilanej z baterii.

Lemonade obsługuje trzy tryby wykonywania na NPU, wszystkie w sposób przezroczysty za pośrednictwem tego samego API OpenAI:

| Tryb | Jak to działa | Recipe | Przykładowe modele |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU przetwarza prompt, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Tylko NPU** | Cała inferencja odbywa się na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Wykorzystuje silnik FastFlowLM na NPU, zoptymalizowany pod AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Wymagania

- Procesor **AMD Ryzen AI serii 300/400 lub serii Z2**
- Dla modeli **FLM**: Środowisko uruchomieniowe FLM można zainstalować z poziomu aplikacji Lemonade, a Lemonade automatycznie zainstaluje środowisko uruchomieniowe FLM podczas uruchamiania modelu FLM. Aby dowiedzieć się więcej o FastFlowLM, zobacz [tutaj](https://fastflowlm.com/docs/).


### Krok 8: Uruchom model Hybrid

Modele Hybrid dzielą pracę między NPU i iGPU, zapewniając dobrą równowagę między szybkością a wydajnością energetyczną. W aplikacji Lemonade wybierz model z listy `Ryzen AI LLM`, na przykład `Qwen3-4B-Hybrid`, lub uruchom go za pomocą następującego polecenia:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automatycznie wykrywa Twoje NPU i instaluje backend **Ryzen AI LLM**.

> **Co dzieje się w tle?** Gdy wysyłasz wiadomość, NPU przetwarza cały Twój prompt równolegle (nazywa się to „prefill”). Następnie iGPU przejmuje kontrolę i generuje odpowiedź token po tokenie (nazywa się to „decode”). To hybrydowe podejście wykorzystuje mocne strony każdego z układów.

### Krok 9: Uruchom model FLM

Modele FastFlowLM (FLM) są specjalnie zoptymalizowane pod architekturę NPU AMD XDNA2 i mogą być bardzo szybkie jak na swój rozmiar. Na przykład wybierz `qwen3.5-4b-FLM` z listy `FastFlowLM NPU` lub użyj następującego polecenia:

<!-- @os:windows -->
Aby włączyć `FastFlowLM` w systemie Windows:

* Otwórz menu `Backends Manager`.
* Znajdź kategorię backendu `FastFlowLM NPU`.
* Kliknij Install NPU.
* Po zakończeniu instalacji, w menu rozwijanym FFLM będzie dostępnych ~36 domyślnych modeli.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Gdy aplikacja `Lemonade` jest uruchamiana po raz pierwszy, backend `FastFlowNPU` nie jest domyślnie włączony. 
Aplikacja lokalna otworzy stronę instalacji, która przeprowadzi Cię przez proces konfiguracji.

Aby włączyć `FastFlowLM` w systemie Linux:

* Otwórz aplikację `Lemonade`.
* Odwiedź [oficjalną dokumentację FLM](https://lemonade-server.ai/flm_npu_linux.html) i postępuj zgodnie z krokami instalacji FLM, wybierając swoją dystrybucję Linuksa.
* Włącz backports zgodnie z instrukcjami na stronie instalacji.
* Pobierz najnowsze wydanie `v0.9.x` ze [strony tagów](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Dla AMD Halo Developer Platform upewnij się, że wybierasz Debian 13.
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
Po pomyślnej instalacji powinieneś zobaczyć, że `flm:npu` zostało ukończone w **Download Manager** wewnątrz **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Możesz następnie wybrać dowolny z dostępnych modeli FFLM i zacząć korzystać z backendu NPU.

Dla konkretnego modelu pobierz żądany model ze [strony modeli](https://fastflowlm.com/docs/models/qwen/) i zweryfikuj go za pomocą polecenia powłoki podanego w dokumentacji.
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

Aplikacja fiszek z Kroku 6 działa również z modelami NPU, wystarczy zmienić nazwę modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Kolejne kroki

Masz uruchomiony lokalny serwer AI na własnym sprzęcie, oto co możesz zrobić dalej:

1. **Połącz swoje ulubione aplikacje**: Lemonade działa od razu po instalacji z [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) i [wieloma innymi](https://lemonade-server.ai/marketplace).

2. **Przeglądaj więcej modeli**: Zapoznaj się z pełną [biblioteką modeli](https://lemonade-server.ai/docs/server/server_models/), aby znaleźć modele zoptymalizowane pod kątem kodowania, wnioskowania, wizji i innych zastosowań. Użyj aplikacji Lemonade lub polecenia `lemonade list`, aby zobaczyć dostępne opcje.

3. **Odblokuj akcelerację GPU ROCm**: Jeśli posiadasz obsługiwane GPU AMD, przełącz się na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Zobacz [obsługiwane GPU AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Przeczytaj pełną specyfikację API**: Lemonade obsługuje uzupełnianie czatu, osadzenia (embeddings), transkrypcję audio, generowanie obrazów, syntezę mowy i wiele więcej. Zobacz [Specyfikację serwera](https://lemonade-server.ai/docs/server/server_spec/), aby poznać wszystkie punkty końcowe.

5. **Współtwórz projekt**: Lemonade jest open source. Zapoznaj się z [przewodnikiem współtworzenia](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) i poszukaj [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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