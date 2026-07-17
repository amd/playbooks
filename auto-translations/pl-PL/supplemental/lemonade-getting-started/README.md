<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten poradnik używa specjalnych tagów, których GitHub nie może renderować. Odwiedź [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę zawartość.
<!-- @github-only:end -->

## Przegląd

🍋 **Lemonade** to otwartoźródłowy lokalny serwer AI, który pozwala uruchamiać duże modele językowe (LLM), generatory obrazów i modele audio bezpośrednio na własnym sprzęcie. Udostępnia modele przez standardowy branżowy **OpenAI API**, dzięki czemu każda aplikacja współpracująca z OpenAI może natychmiast działać z Lemonade. Po ukończeniu tego poradnika będziesz używać Lemonade do lokalnego uruchamiania modeli na swoim komputerze.

## Czego się nauczysz

Po ukończeniu tego poradnika będziesz potrafić:

* **Zainstalować Lemonade Server** i zweryfikować, że działa.
* **Pobrać model LLM i rozmawiać z nim** za pomocą jednego polecenia.
* **Eksplorować interfejs webowy** i wypróbować różne modalności, takie jak wizja, zamiana mowy na tekst i generowanie obrazów.
* **Przełączać backendy GPU** między Vulkan a AMD ROCm™ software.
* **Zbudować aplikację Python** zasilaną lokalnym modelem LLM przy użyciu API kompatybilnego z OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Uruchamiać modele na AMD Neural Processing Unit (NPU)** przy użyciu trybów wykonania Hybrid i FLM na sprzęcie AMD Ryzen™ AI.
<!-- @device:end -->

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

Przed rozpoczęciem upewnij się, że masz:

- Komputer z systemem **Windows 11** lub obsługiwaną dystrybucją **Linux** (Ubuntu 24.04+, Fedora, Debian)
- **16 GB RAM** jest zalecane dla modelu używanego w krokach 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 GB). **32 GB+** jest zalecane, jeśli chcesz używać większego modelu do generowania kodu w kroku 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 GB).
- **~4–30 GB wolnego miejsca na dysku**, w zależności od pobieranych modeli. Największy model w tym przewodniku waży około 20 GB.
- **Python 3.10–3.13** (używany w sekcji dotyczącej aplikacji Python)
- Połączenie z internetem (przewodowe lub bezprzewodowe)
<!-- @device:halo_box,halo,stx,krk -->
- [Opcjonalnie] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 series lub Z2 Extreme) z zainstalowanym najnowszym sterownikiem z [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), jeśli chcesz uruchamiać model na NPU.
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

Zanim uruchomimy model, warto zrozumieć *dlaczego* rzeczy są skonfigurowane w ten sposób. Lemonade to **lokalny serwer modeli** — proces, który ładuje modele AI do pamięci i udostępnia je aplikacjom przez HTTP, tak jak robiłaby to chmurowa usługa AI.

### Dlaczego serwer?

| Korzyść | Co to oznacza dla Ciebie |
|---------|----------------------|
| **Uproszczona integracja** | Aplikacje komunikują się z jednym API HTTP zamiast obsługiwać specyficzne dla sprzętu biblioteki C++ lub Python. |
| **Współdzielone modele** | Jeden załadowany model może obsługiwać wiele aplikacji jednocześnie — bez duplikatów pochłaniających RAM. |
| **Przenośność z chmury do lokalnego środowiska** | Kod napisany dla chmurowego API OpenAI działa z Lemonade po zmianie jednego adresu URL. |
| **Rozdzielenie odpowiedzialności** | Zarządzanie modelami, strumieniowanie i odporność na błędy są obsługiwane przez serwer, dzięki czemu programiści mogą skupić się na swojej aplikacji. |

### Standard OpenAI API

Lemonade implementuje **OpenAI API** — ten sam interfejs używany przez ChatGPT, Azure OpenAI i dziesiątki innych usług. Model konwersacji jest prosty:

| Rola | Kto mówi |
|------|---------------|
| **system** | Instrukcje dla modelu (persona, ograniczenia, dostępne narzędzia) |
| **user** | Wiadomości od człowieka (lub aplikacji) do modelu |
| **assistant** | Odpowiedzi generowane przez model |

Oznacza to, że każda biblioteka lub aplikacja obsługująca OpenAI może komunikować się z Lemonade, wskazując na `http://localhost:13305/api/v1` podczas działania Lemonade Server.

## Główna aktywność — Twój pierwszy lokalny czat z AI

Pobierzmy model LLM i porozmawiajmy z nim, uruchamiając AI całkowicie na własnym komputerze.

### Krok 1: Pobieranie i uruchamianie modelu

Lemonade jest dostarczany z wyselekcjonowaną biblioteką modeli. Zacznijmy od **Gemma-4-E2B-it** — wydajnego i kompaktowego modelu z obsługą wizji. Otwórz terminal i uruchom:

```
lemonade run Gemma-4-E2B-it-GGUF
```

To pojedyncze polecenie wykonuje trzy rzeczy:

1. **Pobiera** model (~3 GB) z Hugging Face, jeśli nie został jeszcze pobrany. (Może to chwilę potrwać)
2. **Uruchamia** proces Lemonade Server na porcie 13305.
3. **Otwiera Lemonade App**, abyś mógł rozpocząć rozmowę z modelem.


<!-- @os:windows -->
W systemie Windows aplikacja Lemonade App uruchamia się automatycznie i możesz od razu rozpocząć rozmowę. Jeśli zainstalowałeś pakiet `minimal.msi`, aplikacja nie jest dołączona. Aby rozpocząć rozmowę, otwórz przeglądarkę internetową i przejdź do `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
W systemie Linux otwórz przeglądarkę i przejdź do `http://localhost:13305`, aby uzyskać dostęp do aplikacji webowej.
<!-- @os:end -->

Spróbuj wpisać pytanie:

```
What are three fun facts about lemons?
```

Model odpowie bezpośrednio w oknie czatu. **Gratulacje! Uruchamiasz duży model językowy lokalnie.**

![Lemonade App z wyświetlonymi logami](../../dependencies/assets/ChatwithLogs.png)

W panelu logów serwera w Lemonade App możesz znaleźć dane telemetryczne dotyczące wydajności modelu po każdej odpowiedzi. Na przykład:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Krok 2: Eksplorowanie interfejsu webowego i różnych modalności

Lemonade zawiera wbudowany interfejs webowy, w którym możesz:

- **Wchodzić w interakcję** z załadowanym modelem w znajomym oknie czatu
- **Przeglądać modele** w zakładce Menedżer modeli
- **Pobierać nowe modele** jednym kliknięciem

Spróbuj przełączać się między różnymi modalnościami, używając zakładki **Model Manager** w interfejsie webowym, gdzie możesz przeglądać modele według przepisu lub kategorii:

1. **Wizja:** Model `Gemma-4-E2B-it-GGUF`, który już masz załadowany, obsługuje wizję. Wklej obraz do pola czatu i poproś model o jego opisanie.
2. **Generowanie obrazów:** W kategorii Image pobierz model obrazów, taki jak `SDXL-Turbo`, z Menedżera modeli, a następnie użyj generatora obrazów Lemonade, aby wpisać prompt i wygenerować obraz lokalnie.
3. **Audio:** W kategorii Audio pobierz model audio, taki jak `Whisper-Tiny`, który może wykonywać zamianę mowy na tekst. Dostarcz nagranie audio, aby je lokalnie transkrybować. Do zamiany tekstu na mowę wypróbuj jeden z modeli w kategorii Speech, na przykład `kokoro-v1`.

![Wiele modalności z Lemonade](../../dependencies/assets/multi_modality.png)

### Krok 3: Wypróbowanie modelu z innym backendem

Jeśli najedziesz kursorem na model w Lemonade App, zobaczysz ikonę koła zębatego. Kliknięcie jej pozwala wybrać opcje dla modelu, w tym wybrać żądany backend.

Domyślnie Lemonade używa Vulkan do akceleracji GPU. Jeśli masz obsługiwany dyskretny GPU AMD, możesz przełączyć się na ROCm.

![Lemonade — wybór backendu](../../dependencies/assets/lemonademodeloptions.png)

Aby zarządzać zainstalowanymi backendami, kliknij przycisk backendu w lewej kolumnie.

Alternatywnie możesz określić backend za pomocą następującego polecenia:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Możesz również ustawić domyślny backend za pomocą zmiennej środowiskowej `LEMONADE_LLAMACPP` z wartościami: `vulkan`, `rocm` lub `cpu`.

---

## Głębsze zanurzenie — budowanie aplikacji zasilanej AI w Python

Prawdziwa moc lokalnego serwera AI polega na tym, że każda aplikacja może się z nim połączyć za pomocą zaledwie kilku linii kodu. Aby to udowodnić, zbudujmy małą, ale funkcjonalną **aplikację do generowania fiszek**, w której podajesz temat, ona generuje fiszki, a Ty możesz się z nich interaktywnie uczyć.

### Krok 4: Uruchamianie serwera

Sprawdź, czy serwer Lemonade działa. Zazwyczaj uruchamia się automatycznie w tle po instalacji. Aby to zweryfikować, uruchom:

```
lemonade status
```

Powinieneś zobaczyć komunikat podobny do: `Server is running on port 13305`.

Jeśli serwer nie działa, uruchom go, otwierając aplikację Lemonade. Użyj domyślnego portu **13305** (możesz to potwierdzić lub wybrać z ikony w zasobniku systemowym).

### Krok 5: Instalowanie klienta Python OpenAI

W terminalu utwórz środowisko wirtualne i zainstaluj klienta Python OpenAI za pomocą następujących poleceń:
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

### Krok 6: Budowanie aplikacji do fiszek

Pobierzmy inny model do generowania kodu: `Qwen3.5-35B-A3B-GGUF`. Jest to duży (~20 GB) i wydajny model, najlepiej dostosowany do systemów z 32 GB+ RAM. Jeśli masz mniej dostępnej pamięci RAM, spróbuj zamiast tego `Qwen3.5-9B-GGUF` (~6 GB).

Możesz go pobrać z interfejsu użytkownika lub uruchomić następujące polecenie:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Wprowadź następujący prompt do interfejsu czatu Lemonade, aby wygenerować kod prostej aplikacji do fiszek.

Użyjemy Qwen3.5-35B-A3B-GGUF (większego modelu lepszego w pisaniu kodu) do wygenerowania naszej aplikacji Python, a sama aplikacja będzie wywoływać Gemma-4-E2B-it-GGUF (mniejszy model, który już pobrałeś) w czasie działania. Kod można następnie skopiować do wybranego pliku i uruchomić w Python.

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

> **Wskazówka**: Zastosowaliśmy standardowe praktyki inżynierskie poprzez staranne tworzenie promptów i użycie systemu dwóch modeli w celu optymalizacji zasobów i szybkości.

Dla Twojej wygody udostępniliśmy przykładowe dane wyjściowe w [`flashcards.py`](assets/flashcards.py). Możesz go pobrać do swojego katalogu. W każdym razie powinieneś teraz mieć plik Python gotowy do uruchomienia.

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


### Krok 7: Uruchamianie wygenerowanego kodu

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

W około 150 liniach kodu zbudowałeś w pełni funkcjonalne narzędzie do nauki zasilane lokalnym modelem LLM. Nie ma klucza API do zarządzania, żadnych kosztów użytkowania i żadne dane nigdy nie opuszczają Twojego komputera.

> **Kluczowa obserwacja:** Zauważ, że linia `client = OpenAI(base_url=...) ` to *jedyna* rzecz łącząca tę aplikację z Lemonade zamiast chmury OpenAI. Reszta kodu jest identyczna z tym, co napisałbyś dla dowolnej usługi kompatybilnej z OpenAI. Jeśli kiedykolwiek używałeś biblioteki Python OpenAI, już wiesz, jak budować aplikacje z Lemonade.

### Co to demonstruje

Ta mała aplikacja ćwiczy kilka rzeczywistych wzorców integracji:

| Wzorzec | Gdzie się pojawia |
|---------|-----------------|
| **Prompty systemowe** | Wiadomość `"system"` mówi modelowi LLM, aby generował ustrukturyzowany JSON |
| **Ustrukturyzowane dane wyjściowe** | Aplikacja analizuje odpowiedź modelu LLM jako JSON, aby budować fiszki |
| **Bezstanowe żądania** | Każde wywołanie `generate_flashcards()` jest niezależne |
| **Obsługa błędów** | Blok `try/except` elegancko obsługuje przypadki, gdy dane wyjściowe modelu LLM nie są prawidłowym JSON |

Te same wzorce skalują się do dowolnej aplikacji, takiej jak chatboty, asystenci kodu, generatory treści, narzędzia automatyzacji.

#### Dodatkowe wyzwanie

* Dla dodatkowego wyzwania spróbuj zaktualizować aplikację tak, aby fiszki były odczytywane użytkownikowi na głos, korzystając z przykładu dostępnego [tutaj](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Uruchamianie modeli na NPU (opcjonalnie)

Jeśli masz procesor z serii Ryzen AI 300/400/Max 300 lub Z2 Extreme, Twoje urządzenie ma wbudowany **Neural Processing Unit (NPU)** — dedykowany układ zaprojektowany specjalnie do zadań AI. Uruchamianie modeli na NPU jest bardziej energooszczędne niż używanie GPU, co czyni go idealnym do zadań AI działających w tle, dłuższych sesji i użytkowania na baterii.

Lemonade obsługuje trzy tryby wykonania NPU, wszystkie przezroczyste za tym samym OpenAI API:

| Tryb | Jak działa | Przepis | Przykładowe modele |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU przetwarza prompt, iGPU generuje tokeny | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Tylko NPU** | Całe wnioskowanie działa na NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Używa silnika FastFlowLM na NPU, zoptymalizowanego dla AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Wymagania

- Procesor **AMD Ryzen AI 300/400 series lub Z2 series**
- Dla modeli **FLM**: Środowisko uruchomieniowe FLM można zainstalować z poziomu aplikacji Lemonade lub Lemonade automatycznie zainstaluje środowisko uruchomieniowe FLM podczas uruchamiania modelu FLM. Aby dowiedzieć się więcej o FastFlowLM, zobacz [tutaj](https://fastflowlm.com/docs/).


### Krok 8: Uruchamianie modelu Hybrid

Modele Hybrid dzielą pracę między NPU i iGPU, zapewniając dobry balans między szybkością a wydajnością energetyczną. W Lemonade App wybierz model z listy `Ryzen AI LLM`, na przykład `Qwen3-4B-Hybrid`, lub uruchom go za pomocą następującego polecenia:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade automatycznie wykrywa Twój NPU i instaluje backend **Ryzen AI LLM**.

> **Co dzieje się pod spodem?** Gdy wysyłasz wiadomość, NPU przetwarza cały Twój prompt równolegle (nazywa się to „prefill"). Następnie iGPU przejmuje kontrolę, aby generować odpowiedź token po tokenie (nazywa się to „decode"). To hybrydowe podejście wykorzystuje mocne strony każdego układu.

### Krok 9: Uruchamianie modelu FLM

Modele FastFlowLM (FLM) są specjalnie zoptymalizowane dla architektury NPU AMD XDNA2 i mogą być bardzo szybkie jak na swój rozmiar. Na przykład wybierz `qwen3.5-4b-FLM` z listy `FastFlowLM NPU` lub użyj następującego polecenia:

<!-- @os:windows -->
Aby włączyć `FastFlowLM` w systemie Windows:

* Otwórz menu `Backends Manager`.
* Znajdź kategorię backendu `FastFlowLM NPU`.
* Kliknij Install NPU.
* Po zakończeniu instalacji w menu rozwijającym FFLM będzie dostępnych ~36 domyślnych modeli.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Gdy aplikacja `Lemonade` jest uruchamiana po raz pierwszy, backend `FastFlowNPU` nie jest domyślnie włączony.
Lokalna aplikacja otworzy stronę instalacji, aby przeprowadzić Cię przez konfigurację.

Aby włączyć `FastFlowLM` w systemie Linux:

* Otwórz aplikację `Lemonade`.
* Odwiedź [oficjalną dokumentację FLM](https://lemonade-server.ai/flm_npu_linux.html) i postępuj zgodnie z krokami instalacji FLM, wybierając swoją dystrybucję Linux.
* Włącz backporty zgodnie z instrukcjami na stronie instalacji.
* Pobierz najnowsze wydanie `v0.9.x` ze [strony tagów](https://github.com/FastFlowLM/FastFlowLM/tags).
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
Po pomyślnej instalacji powinieneś zobaczyć, że `flm:npu` zakończył się w **Menedżerze pobierania** wewnątrz **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Następnie możesz wybrać dowolny z dostępnych modeli FFLM i rozpocząć korzystanie z backendu NPU.

Dla konkretnego modelu pobierz żądany model ze [strony modeli](https://fastflowlm.com/docs/models/qwen/) i zweryfikuj go za pomocą polecenia Shell podanego w dokumentacji.
```
flm run qwen3.5-4b-FLM
```
lub przez 
```
lemonade run qwen3.5-4b-FLM
```

Modele FLM obejmują niektóre z najpopularniejszych architektur (Gemma 3, Qwen 3, Llama 3 i DeepSeek R1) i mają rozmiary od poniżej 1 GB do ponad 13 GB.
Lemonade automatycznie wykrywa Twój NPU i instaluje backend **FastFlowLM NPU**.

<!-- @os:windows -->
> **Wskazówka:** Aby uzyskać najlepszą wydajność NPU, włącz tryb turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Przełączanie modeli

Aplikacja do fiszek z kroku 6 działa również z modelami NPU — wystarczy zmienić nazwę modelu:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Kolejne kroki

Masz lokalny serwer AI działający na własnym sprzęcie — oto co możesz zrobić dalej:

1. **Połącz swoje ulubione aplikacje**: Lemonade działa od razu z [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) i [wieloma innymi](https://lemonade-server.ai/marketplace).

2. **Przeglądaj więcej modeli**: Eksploruj pełną [bibliotekę modeli](https://lemonade-server.ai/docs/server/server_models/), aby znaleźć modele zoptymalizowane do kodowania, rozumowania, wizji i nie tylko. Użyj Lemonade App lub `lemonade list`, aby zobaczyć, co jest dostępne.

3. **Odblokuj akcelerację GPU ROCm**: Jeśli masz obsługiwany GPU AMD, przełącz się na backend ROCm: `lemonade config set llamacpp.backend=rocm`. Zobacz [obsługiwane GPU AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Przeczytaj pełną specyfikację API**: Lemonade obsługuje uzupełnianie czatu, osadzenia, transkrypcję audio, generowanie obrazów, zamianę tekstu na mowę i wiele więcej. Zobacz [specyfikację serwera](https://lemonade-server.ai/docs/server/server_spec/) dla każdego punktu końcowego.

5. **Współtwórz**: Lemonade jest oprogramowaniem open source. Sprawdź [przewodnik po wkładzie](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) i poszukaj [dobrych pierwszych zadań](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).