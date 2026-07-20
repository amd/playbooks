<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten przewodnik wykorzystuje specjalne znaczniki, których GitHub nie potrafi wyrenderować. Odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę treść.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ten przewodnik wymaga co najmniej **32 GB** pamięci systemowej.
<!-- @device:end -->

## Przegląd

Agenci kodujący to potężne narzędzia, które wzmacniają możliwości programistów poprzez współpracę z agentami AI opartymi na dużych modelach językowych (LLM). Można je osadzić bezpośrednio w środowisku programistycznym, takim jak terminal czy VS Code, co pozwala na płynną integrację z codzienną pracą programisty.

Ten samouczek pokazuje, jak używać Cline, VS Code i LM Studio do uruchomienia agenta kodującego całkowicie lokalnie na własnym komputerze.

## Czego się nauczysz

* Jak uruchomić VS Code z agentem kodującym Cline, aby wspomóc zadania z zakresu inżynierii oprogramowania.
* Jak skonfigurować Cline do komunikacji z LM Studio w celu lokalnego wnioskowania agentów kodujących.
* Jak wykorzystać lokalnych agentów kodujących do rozwiązywania rzeczywistych problemów inżynierii oprogramowania.

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

<!-- @require:lmstudio,vscode -->

## Uruchamianie i konfigurowanie LM Studio

Użyjemy LM Studio do udostępniania modelu LLM zasilającego agenta kodującego.

- W pasku wyszukiwania wpisz `LM Studio` i uruchom aplikację. Pojawi się następujący ekran.

![Ekran startowy LM Studio](assets/initial-lm-studio.png)

Następnie musimy załadować model LLM na system. Użyjemy modelu `Qwen3-Coder-30B-A3B` z dużą długością kontekstu. (Jeśli nie masz go jeszcze zainstalowanego, skorzystaj z zakładki Model, aby go zainstalować).
- Kliknij pasek wyszukiwania na górze okna LM Studio lub naciśnij `CTRL+L`. Kliknij przełącznik `Manually choose model load parameters`, a następnie kliknij model Qwen3-Coder-30B-A3B.
- Zmień długość kontekstu z `4096` na `32768` i upewnij się, że `GPU Offload` jest ustawione na maksimum. Następnie kliknij `Load Model`

![Wybieranie modelu](assets/model-list-zoomed.png)

Używamy dużej długości kontekstu, aby agent mógł przetwarzać duże bazy kodu i zapamiętywać wprowadzone zmiany.

![Konfigurowanie modelu](assets/selecting-model-zoomed.png)

Następnie musimy włączyć serwer LM Studio.
- Kliknij zakładkę Developer lub naciśnij `CTRL+2` w LM Studio po lewej stronie.
- Zaznacz przełącznik statusu i upewnij się, że jest ustawiony na `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Status serwera](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Uruchamianie i konfigurowanie VS Code

Zainstalujemy rozszerzenie Cline w VS Code i połączymy je z serwerem LM Studio, który właśnie uruchomiliśmy.
- W pasku wyszukiwania wpisz `VS Code` i uruchom aplikację.
- Kliknij ikonę `Extensions` w lewej kolumnie VS Code i wyszukaj `Cline`. Następnie kliknij przycisk `Install`.

![Instalowanie rozszerzenia Cline](assets/installing-cline-vscode-extension.png)

- Po lewej stronie powinna pojawić się ikona Cline. Kliknij ją, aby otworzyć Cline. Pojawi się okno z pytaniem `How will you use Cline?` Ponieważ będziemy korzystać z lokalnego modelu LLM uruchomionego przez LM Studio, wybierz `Bring my own API Key` i kliknij `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Tworzenie konta](assets/cline-how-will-you-use-cline-zoomed.png)

Następnie musimy skonfigurować Cline do komunikacji z serwerem LM Studio, który skonfigurowaliśmy.
- Ustaw API Provider na `LM Studio`, a model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Wskazówka**: Mogą być dostępne nowsze modele. Jeśli chcesz, rozważ pobranie i przełączenie się na modele Qwen3.6.


![Konfiguracja modelu](assets/cline-model-configuration-zoomed.png)

## Tworzenie pierwszego projektu

Wykorzystajmy naszego lokalnego agenta do stworzenia strony internetowej! Otwórz VSCode w wybranym katalogu, w którym Cline utworzy pliki.
- Aby to zrobić, przejdź do `File -> Open Folder` w lewym górnym rogu VS Code i wybierz folder, na przykład `Documents`.

![Pusty folder w VS Code](assets/open-cline-test.png)

Teraz jesteśmy gotowi, aby przekazać polecenie lokalnemu agentowi kodującemu.
- Kliknij rozszerzenie Cline w lewej kolumnie i wpisz polecenie, aby uruchomić agenta. Jako przykład użyjmy następującego polecenia:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent zacznie następnie tworzyć pliki zgodnie z poleceniem. Jako użytkownik możesz obserwować generowanie kodu w VS Code, jak pokazano poniżej. Może być konieczne kliknięcie `Save` za każdym razem, gdy Cline chce utworzyć plik.

![Generowanie kodu przez Cline](assets/cline-code-generation.png)

Po wygenerowaniu oprogramowania praca agenta jest zakończona i możesz uruchomić aplikację. W tym przypadku agent zapisał trzy pliki: `index.html`, `script.js` oraz `styles.css`. Wystarczy dwukrotnie kliknąć plik HTML, aby wczytać i wchodzić w interakcję z wygenerowaną stroną internetową.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->
## Kolejne kroki

Po wygenerowaniu strony internetowej możesz kontynuować pracę z Cline, aby ją ulepszyć. Dwie możliwe ulepszenia to:

- **Dokumentacja**: Wystarczy zachęcić agenta poleceniem `Add a README`, aby agent wygenerował plik `README.md` dokumentujący stronę internetową.
- **Animacja**: Poproś model poleceniem `Add an animation that visually represents a large language model running on a laptop.`, aby wygenerować animację do strony internetowej.

Zachęcamy czytelnika do samodzielnego generowania innych aplikacji przy użyciu tej konfiguracji. Poniżej znajduje się kilka ciekawych przykładów, które wypróbowaliśmy:

- **Gry Retro Arcade**: Wypróbuj inne polecenia. Zabawą dla agenta może być również tworzenie gier w stylu retro w Pythonie przy użyciu pakietu `PyGame` z następującym poleceniem:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza danych**: Jednym z obszarów, w których agenci kodujący są szczególnie przydatni, jest tworzenie skryptów i analiza danych. Oto polecenie prezentujące zdolność lokalnego modelu do generowania oprogramowania do analizy danych na potrzeby wizualizacji cen akcji:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zasoby

Poniżej znajduje się kilka dodatkowych zasobów, aby dowiedzieć się więcej o agentach kodujących, Cline i uruchamianiu obciążeń na

* Więcej informacji o partnerstwie i integracji AMD z LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD przedstawiający uruchamianie Cline na kartach graficznych AMD Ryzen™ AI i Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline na temat uruchamiania agentów kodujących lokalnie na komputerach AI PC: https://cline.bot/blog/local-models-amd