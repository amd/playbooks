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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Przegląd

[OpenHands](https://github.com/All-Hands-AI/OpenHands) to agent oprogramowania AI,
który potrafi pisać kod, uruchamiać polecenia, przeglądać sieć i edytować pliki w rzeczywistej
przestrzeni roboczej. Zamiast kopiować sugestie z okna czatu, wskazujesz
agentowi folder projektu i pozwalasz mu wykonać pracę: zaimplementować funkcję, naprawić
błąd, napisać testy lub wyjaśnić bazę kodu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) to zalecany
interfejs przeglądarkowy do uruchamiania OpenHands. Pojedyncze polecenie `agent-canvas` uruchamia
serwer agenta, backend automatyzacji i frontend webowy razem, dzięki czemu możesz
prowadzić konwersację z agentem z poziomu przeglądarki.

Aby zachować wszystko na Twoim systemie AMD, agent komunikuje się z lokalnym modelem obsługiwanym
przez Lemonade Server. Lemonade udostępnia ten model przez API zgodne z OpenAI,
dzięki czemu Agent Canvas może go skonfigurować jak każdy inny punkt końcowy w stylu OpenAI,
podczas gdy model, Twój kod i kontekst konwersacji pozostają na Twojej
maszynie.

W tym poradniku uruchomisz lokalny model, uruchomisz Agent Canvas, skierujesz go
na ten model i uruchomisz swoje pierwsze zadanie programistyczne na rzeczywistym folderze projektu.

## Czego się nauczysz

- Jak uruchomić Lemonade Server i potwierdzić, że lokalny model odpowiada na żądania czatu
- Jak zainstalować i uruchomić Agent Canvas z pakietu npm
- Jak skonfigurować Agent Canvas do korzystania z lokalnego modelu Lemonade jako LLM
- Jak rozpocząć konwersację OpenHands i obserwować, jak agent edytuje pliki i uruchamia
  polecenia w przestrzeni roboczej
- Jak przejrzeć zmiany wprowadzone przez agenta i sterować nim za pomocą kolejnych wiadomości

## Podstawowe pojęcia

| Pojęcie | Czym jest | Gdzie pasuje w tym poradniku |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma serwująca LLM zbudowana dla sprzętu AMD, udostępniająca API zgodne z OpenAI. Twoje dane nigdy nie opuszczają Twojej maszyny. | Uruchamia model zasilający agenta. |
| OpenHands | Agent oprogramowania AI, który odczytuje i edytuje pliki, uruchamia polecenia powłoki i przegląda sieć w przestrzeni roboczej. | Agent, którym sterujesz z czatu. |
| Agent Canvas | Interfejs przeglądarkowy i backend, który uruchamia konwersacje OpenHands i pokazuje wywołania narzędzi oraz zmiany plików. | Uruchamia stos i obsługuje Twoją konwersację. |
| Przestrzeń robocza | Folder projektu, który agent może odczytywać i modyfikować. | Cel edycji i poleceń agenta. |

<!-- @device:stx,krk -->
> [!NOTE]
> Przepływy pracy agenta programistycznego korzystają z większego modelu i okna kontekstu. Użyj
> co najmniej 32 GB pamięci systemowej, a dla większych modeli GGUF preferuj 64 GB lub więcej.
<!-- @device:end -->

## Wymagania wstępne

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrzebujesz:

- Zainstalowanego Lemonade Server, zdolnego do obsługi poniższego modelu.
- Node.js 22.12 lub nowszego oraz `npm` (używanego przez CLI `agent-canvas`).
- `uv`, menedżera pakietów Python, którego Agent Canvas używa do zarządzania środowiskiem
  serwera agenta. Jeśli Twój system jeszcze go nie ma, zainstaluj go z
  [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/)
  przed uruchomieniem Agent Canvas.
- Folder projektu, w którym będziesz pracować. Może to być dowolne lokalne repozytorium git lub katalog kodu,
  nad którym ma pracować agent.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Uruchom Lemonade Server

Uruchom model z poziomu CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade udostępnia API zgodne z OpenAI pod adresem:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Zweryfikuj lokalny model

Potwierdź, że Lemonade może obsługiwać wybrany model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Następnie wyślij małe żądanie czatu:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Jeśli zwróci to tablicę `choices`, Lemonade jest gotowy dla Agent Canvas.

## 3. Zainstaluj i uruchom Agent Canvas

Zainstaluj opublikowany pakiet Agent Canvas globalnie:

```bash
npm install -g @openhands/agent-canvas
```

Następnie uruchom pełny stos z terminala:

```bash
agent-canvas
```

Domyślnie Agent Canvas uruchamia się pod adresem `http://localhost:8000`. Otwórz ten adres URL w
przeglądarce. Jeśli port 8000 jest już zajęty, przekaż `--port` (lub `-p`) podczas
uruchamiania Agent Canvas:

```bash
agent-canvas --port 3000
```

To samo polecenie działa w PowerShell w systemie Windows. Następnie otwórz
`http://localhost:3000` zamiast tego. Domyślny lokalny backend powinien pokazywać się jako
działający (healthy) na ekranie głównym.

Polecenie `agent-canvas` uruchamia razem serwer agenta, backend automatyzacji i
frontend webowy. Potrzebujesz tylko tego jednego polecenia, aby uruchomić OpenHands
lokalnie.

## 4. Skonfiguruj lokalny LLM

Przy pierwszym uruchomieniu Agent Canvas otwiera proces wprowadzający. W tym procesie:

1. Pozostaw **OpenHands** wybrane jako agent i kliknij **Next**.
2. Na ekranie **Set up your LLM** wybierz **Advanced**.
3. Pozostaw **Authentication** ustawione na **API key**.
4. Ustaw **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ustaw **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. W polu **API Key** wpisz dowolny niepusty symbol zastępczy, np. `lemonade-local`.
   Lemonade nie wymaga prawdziwego klucza, ale klient OpenHands potrzebuje jakiejś
   wartości do wysłania.
7. Kliknij **Next**.

Ukończone ustawienia Advanced powinny wyglądać tak. Pole klucza API jest
zamaskowane przez interfejs.

![Ustawienia Advanced LLM Agent Canvas przy pierwszym użyciu z modelem Lemonade i lokalnym adresem URL bazowym](assets/01-llm-advanced-settings.png)

Agent Canvas zapisuje te wartości jako profil LLM. Jeśli Twoja wersja poprosi Cię o
nazwanie tego profilu, użyj nazwy bez spacji, np. `lemonade-local`. Jeśli zmienisz
modele później, otwórz **Settings > LLM** i zaktualizuj te same pola Advanced. Możesz
przełączać zapisane profile z pola wprowadzania czatu za pomocą polecenia `/model`.

## 5. Otwórz przestrzeń roboczą

Agent może odczytywać i modyfikować pliki tylko w wybranej przez Ciebie przestrzeni roboczej. Przed
rozpoczęciem zadania wskaż Agent Canvas swój folder projektu:

1. Na ekranie głównym wybierz **Open Workspace**.
2. Wybierz folder zawierający Twój projekt (na przykład repozytorium git,
   nad którym ma pracować agent).
3. Rozpocznij nową konwersację w tej przestrzeni roboczej.

Wszystko, co agent robi — odczytywanie plików, uruchamianie poleceń, edytowanie kodu — jest
ograniczone do tej przestrzeni roboczej.

![Ekran główny Agent Canvas po wprowadzeniu](assets/02-agent-canvas-home.png)
## 6. Uruchom swoje pierwsze zadanie programistyczne

Po otwarciu przestrzeni roboczej i wybraniu lokalnego LLM wpisz konkretne zadanie na czacie. Dobrym pierwszym zadaniem jest coś małego i łatwego do zweryfikowania, na przykład:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Obserwuj oś czasu konwersacji. OpenHands wykona następujące czynności:

- Odczyta przestrzeń roboczą, aby zrozumieć jej strukturę.
- Utworzy plik `hello.py` z żądaną funkcją i blokiem testowym.
- Opcjonalnie uruchomi `python3 hello.py`, aby zweryfikować wynik.
- Zgłosi w czacie, co zrobił, oraz wynik ewentualnych poleceń.

Powinieneś zobaczyć nowy plik pojawiający się w przestrzeni roboczej, a końcowa wiadomość agenta powinna opisywać wprowadzoną zmianę. To jest kluczowy moment: agent napisał i uruchomił prawdziwy kod w folderze Twojego projektu.

## 7. Przeglądaj i kieruj pracą agenta

Po zakończeniu przez agenta danego kroku przejrzyj jego pracę, zanim zaakceptujesz kolejny:

- **Zmiany w plikach**: użyj przeglądarki plików przestrzeni roboczej lub widoku diff agenta, aby dokładnie zobaczyć, co zostało dodane, zmienione lub usunięte.
- **Wynik poleceń**: rozwiń dowolne polecenie uruchomione przez agenta, aby zobaczyć stdout, stderr oraz kod wyjścia.
- **Działania następcze**: jeśli wynik nie jest taki, jak oczekiwano, odpowiedz w tej samej konwersacji z poprawką. Agent zachowuje wcześniejszy kontekst i kontynuuje pracę na tych samych plikach.

Na przykład, jeśli test nie wypisał oczekiwanego powitania, odpowiedz:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent ponownie odczyta plik, uruchomi polecenie, zdiagnozuje problem i ponownie edytuje plik — wszystko w ramach tej samej konwersacji.

## Rozwiązywanie problemów

- **`agent-canvas` nie znajduje się w PATH:** zainstaluj ponownie za pomocą
  `npm install -g @openhands/agent-canvas` i upewnij się, że katalog globalnych plików binarnych npm znajduje się w PATH. W systemie Windows uruchom `npm config get prefix`; zwrócony katalog, często `%APPDATA%\npm` lub `%USERPROFILE%\.npm-global`,
  musi znajdować się w PATH użytkownika, zanim `agent-canvas` będzie można uruchomić z nowego terminala.
- **`npm install -g` kończy się błędem uprawnień:** skonfiguruj globalny katalog npm będący własnością użytkownika, następnie ponownie otwórz terminal i zainstaluj Agent Canvas jeszcze raz.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Aby zmiana PATH w systemie Windows była trwała, dodaj `%USERPROFILE%\.npm-global` do
  PATH użytkownika w **Settings > System > About > Advanced system settings >
  Environment Variables**, a następnie otwórz nowy terminal.
  <!-- @os:end -->
- **Interfejs użytkownika ładuje się, ale backend pokazuje status unhealthy:** poczekaj kilka sekund, aż serwer agenta zakończy uruchamianie, a następnie odśwież stronę. Jeśli status nadal pozostaje unhealthy, uruchom ponownie
  `agent-canvas` i sprawdź dane wyjściowe terminala pod kątem błędów.
- **Żądania czatu Lemonade kończą się błędem połączenia:** upewnij się, że
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` kończy się sukcesem oraz że
  Lemonade nadal obsługuje model, sprawdzając to poleceniem `lemonade status`.
- **Agent zgłasza błąd dotyczący długości kontekstu lub limitu tokenów:** uruchom ponownie
  Lemonade z większą wartością `ctx_size` (na przykład `ctx_size=65536`), i rozpocznij
  nową konwersację, aby agent nie przenosił zbyt dużej historii.
- **Agent generuje edycje niskiej jakości lub niekompletne:** przełącz się na większy
  model w Lemonade lub zleć agentowi mniejsze, bardziej konkretne zadanie i pozwól mu je
  ukończyć, zanim poprosisz o kolejną zmianę.
- **Brak `uv`:** zainstaluj je, korzystając z
  [przewodnika instalacji uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas korzysta z `uv` do zarządzania środowiskiem Python serwera agenta.

## Następne kroki

- Spróbuj wykonać większe zadanie w tej samej przestrzeni roboczej, na przykład dodanie pliku z testem jednostkowym lub naprawę znanego błędu, i przejrzyj diff agenta przed zaakceptowaniem zmiany.
- Podłącz serwer MCP, taki jak GitHub lub Slack, w sekcji **Customize**, aby
  agent mógł odczytywać zgłoszenia (issues) lub publikować aktualizacje podczas pracy.
- Zapisz kilka profili LLM (szybki mały model i mocniejszy duży model) i
  przełączaj się między nimi za pomocą `/model` w trakcie konwersacji.
- Przejdź do [automatyzacji OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), aby
  zamienić powtarzalne cykle programistyczne w zaplanowane lub uruchamiane zdarzeniami przebiegi agenta.

## Zasoby

- [Dokumentacja OpenHands](https://docs.openhands.dev/)
- [Przegląd Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Konfiguracja Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profile LLM i konfiguracja modeli](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacja Lemonade Server](https://lemonade-server.ai/docs)