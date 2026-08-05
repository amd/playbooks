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

Deweloperzy poświęcają dużo czasu na drobne, powtarzające się czynności: przeglądanie oznaczonych etykietami pull requestów, odpowiadanie na komentarze na GitHub, triage nowych zgłoszeń, zamienianie wątków na Slacku w notatki ze standupu lub działania następcze po incydentach, a także śledzenie sygnałów dotyczących wydań lub badań. Każda z tych czynności jest znajoma, ale nadal wymaga oceny sytuacji: zebrania odpowiedniego kontekstu, zdecydowania, co jest istotne, i opublikowania jasnej aktualizacji tam, gdzie zespół już pracuje.

[Automatyzacje OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) zamieniają te czynności w zaplanowane lub wyzwalane zdarzeniami konwersacje agenta: uruchomienia, podczas których agent AI może odczytywać kontekst, wywoływać narzędzia i tworzyć aktualizację. Współdzielone szablony automatyzacji w katalogu rozszerzeń OpenHands stosują ten sam schemat w przypadku przeglądu pull requestów na GitHub, monitorowania repozytoriów, triage'u zgłoszeń Linear, retrospektyw incydentów, cyfrowych podsumowań standupów na Slacku oraz raportów badawczych: automatyzacja się aktywuje, korzysta ze skonfigurowanych integracji, takich jak GitHub czy Slack, aby pobrać kontekst, analizuje ten kontekst za pomocą dużego modelu językowego (LLM), a następnie zapisuje wynik.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) to lokalna płaszczyzna kontrolna do budowania i testowania takich automatyzacji. W tym playbooku uruchamia ona OpenHands Agent Server, proces backendowy wykonujący konwersacje agenta, i łączy agenta z zewnętrznymi usługami, takimi jak GitHub i Slack.

Aby cały przepływ pracy pozostał na Twoim systemie AMD, agent komunikuje się z lokalnym modelem obsługiwanym przez Lemonade Server. Lemonade udostępnia ten model poprzez API kompatybilne z OpenAI, dzięki czemu Agent Canvas może go skonfigurować tak, jakby był zdalnym punktem końcowym w stylu OpenAI, podczas gdy model, prompt i kontekst przepływu pracy pozostają lokalne.

W tym playbooku zbudujesz jedną konkretną automatyzację: zaplanowany cyfrowy digest rozwoju z GitHub na Slack. Wykorzystuje ona GitHub do sprawdzania niedawnej aktywności w repozytorium, Slack do publikowania digestu, wywołania API Agent Canvas do konfigurowania i testowania automatyzacji oraz Lemonade do lokalnego uruchamiania LLM.

![Diagram architektury pokazujący GitHub MCP, automatyzację OpenHands, Lemonade Server i Slack MCP](assets/00-architecture-overview.png)

## Czego się nauczysz

- Jak uruchomić Lemonade Server i sprawdzić, czy lokalny model odpowiada na żądania czatu
- Jak uruchomić Agent Canvas i skierować jego Agent Server na lokalny LLM
- Jak zainstalować serwery Model Context Protocol (MCP) dla GitHub i Slack za pomocą API Agent Server
- Jak utworzyć i uruchomić zaplanowaną automatyzację OpenHands, która publikuje digest rozwoju na Slacku
- Jak rozwiązywać najczęstsze problemy związane z lokalnym modelem i automatyzacją

## Podstawowe pojęcia

| Pojęcie | Czym jest | Gdzie pasuje w tym playbooku |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma serwująca LLM zbudowana dla sprzętu AMD, udostępniająca API kompatybilne z OpenAI. Twoje dane nigdy nie opuszczają Twojej maszyny. | Uruchamia model zasilający agenta. |
| OpenHands Agent Server | Proces backendowy wykonujący konwersacje agenta OpenHands. | Hostuje agenta, jego profil LLM oraz jego serwery MCP. |
| Agent Canvas | Lokalna płaszczyzna kontrolna dla OpenHands, uruchamiająca Agent Server oraz interfejs użytkownika do inspekcji uruchomień agenta. | Uruchamia backendy i udostępnia API, które wywołujesz. |
| Serwer MCP | Serwer Model Context Protocol, który udostępnia agentowi narzędzia dla zewnętrznej usługi, takiej jak GitHub lub Slack. | Pozwala agentowi odczytywać dane z GitHub i zapisywać na Slacku. |
| Automatyzacja OpenHands | Zaplanowana lub wyzwalana zdarzeniami konwersacja agenta, która pobiera kontekst, analizuje go i zapisuje wynik w określonym miejscu. | Digest z GitHub na Slack, który tworzysz w tym playbooku. |

<!-- @device:stx,krk -->
> [!NOTE]
> Przepływy pracy agenta kodującego korzystają z większego modelu i szerszego okna kontekstu. Użyj co najmniej 32 GB pamięci systemowej, a w przypadku większych modeli GGUF preferuj 64 GB lub więcej.
<!-- @device:end -->

## Wymagania wstępne

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrzebujesz:

- Zainstalowanego Lemonade Server zgodnie ze standardowym
  [przewodnikiem instalacji Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js w wersji 22.12 lub nowszej oraz `npm`, używanych do zainstalowania opublikowanego interfejsu CLI Agent Canvas i uruchamiania serwerów MCP za pomocą `npx`.
- Aktualnie opublikowanego pakietu `@openhands/agent-canvas` z ustawieniami agenta opartymi na schemacie, `LLMSummarizingCondenserSettings.max_tokens` oraz obsługą `custom_tokenizer` dla LLM.
- Pakietu Python `transformers` dostępnego w środowisku Agent Server. Jest on wymagany do liczenia tokenów na podstawie szablonu czatu, gdy ustawiono `custom_tokenizer`.
- Tokenu GitHub z uprawnieniami do odczytu repozytorium, które ma zostać podsumowane.
- Tokenu bota Slack (`xoxb-...`) z uprawnieniami `chat:write` i dostępem do odczytu kanału.
- Identyfikatora zespołu Slack (`T...`).
- Identyfikatora kanału Slack (`C...`), na którym ma zostać opublikowany digest.

Zaproś aplikację Slack do docelowego kanału przed przetestowaniem automatyzacji.

## Zmienne używane w tym playbooku

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Poniższe wartości są wprowadzane do interfejsu użytkownika Agent Canvas w dalszych krokach. Ustaw je tutaj, aby móc je później skopiować:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Użyj jawnej wartości `owner/repo` dla `GITHUB_REPO_FILTER`. Szerokie symbole wieloznaczne dla organizacji mogą zwrócić zbyt dużo kontekstu MCP dla lokalnych modeli.

## 1. Uruchom Lemonade Server

Uruchom model z poziomu interfejsu CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade udostępnia API kompatybilne z OpenAI pod adresem:

```text
http://127.0.0.1:13305/api/v1
```

Opcjonalnie: jeśli Agent Canvas lub program uruchamiający automatyzację nie znajduje się na tej samej maszynie, udostępnij punkt końcowy Lemonade za pośrednictwem bezpiecznego tunelu i użyj adresu URL HTTPS jako podstawowego adresu URL LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Zweryfikuj lokalny model

Potwierdź, że Lemonade może serwować wybrany model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Następnie wyślij niewielkie żądanie czatu:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Jeśli w odpowiedzi otrzymasz tablicę `choices`, oznacza to, że Lemonade jest gotowy do współpracy z Agent Canvas.
## 3. Uruchamianie Agent Canvas

Zainstaluj opublikowany pakiet Agent Canvas i uruchom pełny stos:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Jeśli globalna instalacja npm nie powiedzie się z powodu błędu uprawnień, zobacz
poniższy wpis dotyczący rozwiązywania problemów z uprawnieniami npm.

Domyślnie Agent Canvas uruchamia się pod adresem `http://localhost:8000`. Otwórz
ten adres URL w przeglądarce. Domyślny lokalny backend powinien być
wyświetlany jako sprawny na ekranie głównym.

Polecenie `agent-canvas` uruchamia jednocześnie serwer agenta, backend
automatyzacji oraz frontend webowy. Do lokalnego uruchomienia OpenHands
potrzebne jest tylko to jedno polecenie. Pozostała część tego przewodnika
konfiguruje wszystko za pomocą interfejsu Agent Canvas w przeglądarce.

## 4. Konfigurowanie lokalnego LLM w interfejsie

Przy pierwszym uruchomieniu Agent Canvas otwiera proces wdrożeniowy. W tym
procesie:

1. Pozostaw **OpenHands** wybrane jako agent i kliknij **Next**.
2. Na ekranie **Set up your LLM** wybierz **Advanced**.
3. Pozostaw **Authentication** ustawione na **API key**.
4. Ustaw **Custom Model** na wartość `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ustaw **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. W polu **API Key** wpisz dowolny niepusty tekst zastępczy, na przykład
   `lemonade-local`. Lemonade nie wymaga prawdziwego klucza, ale klient
   OpenHands potrzebuje jakiejś wartości do wysłania.

Pola połączenia powinny wyglądać następująco. Pole klucza API jest maskowane
przez interfejs.

![Ustawienia zaawansowane LLM Agent Canvas przy pierwszym użyciu z modelem Lemonade i lokalnym adresem bazowym](assets/01-llm-advanced-settings.png)

Następnie wybierz **All** i ustaw dodatkowe pola dla modelu lokalnego:

1. Przewiń do **Custom Tokenizer** i ustaw wartość `Qwen/Qwen3.6-35B-A3B`.
2. Przewiń do **LiteLLM Extra Body** i ustaw wartość
   `{"enable_thinking": true}`.
3. Kliknij **Next**.

![Karta All ustawień LLM Agent Canvas przy pierwszym użyciu z niestandardowym tokenizerem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta All ustawień LLM Agent Canvas przy pierwszym użyciu ze skonfigurowanym polem LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Ustawienia LLM powinny pokazywać:

| Pole | Wartość |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Przedrostek `openai/` informuje LiteLLM, aby używać formatowania żądań
zgodnego z OpenAI wobec punktu końcowego Lemonade. Niestandardowy tokenizer to
oryginalny tokenizer Hugging Face dla modelu GGUF; pozwala on OpenHands liczyć
te same tokeny szablonu czatu, które widzi lokalny serwer modelu. Obecny
formularz LLM przy pierwszym użyciu nie pokazuje ustawień condensera. Jeśli
Twoja wersja Agent Canvas udostępnia później ustawienia condensera w
**Settings > LLM**, użyj `llm_summarizing` i ustaw maksymalną liczbę tokenów
poniżej okna kontekstu Lemonade, na przykład `56000`.

## 5. Instalacja serwerów MCP dla GitHub i Slack

W interfejsie Agent Canvas otwórz **Customize** (lub **Settings > MCP**), aby
dodać serwery MCP zapewniające agentowi narzędzia do obsługi GitHub i Slack.
Wartości tokenów są wysyłane wyłącznie do lokalnego Agent Server i są
zapisywane jako zaszyfrowane ustawienia.

### Serwer MCP dla GitHub

Dodaj nowy serwer MCP z następującymi ustawieniami:

| Pole | Wartość |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = Twój token GitHub |

Użyj tokenu GitHub z dostępem do odczytu repozytorium, które ma być
podsumowywane.

### Serwer MCP dla Slack

Dodaj drugi serwer MCP z następującymi ustawieniami:

| Pole | Wartość |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID Twojego kanału podsumowań |

Ustaw `SLACK_CHANNEL_IDS` na ID kanału podsumowań (tę samą wartość co
`SLACK_DIGEST_CHANNEL`), aby agent nie musiał przeglądać wszystkich kanałów
Slack.

Po dodaniu obu serwerów użyj przycisku **Test** przy każdym z nich, aby
potwierdzić, że nawiązuje połączenie i udostępnia narzędzia. Serwer GitHub
powinien wyświetlić listę narzędzi GitHub, a serwer Slack — listę narzędzi
Slack.

![Strona MCP w Agent Canvas z zainstalowanymi serwerami GitHub i Slack](assets/04-mcp-servers-installed.png)

## 6. Tworzenie automatyzacji podsumowań

W interfejsie Agent Canvas otwórz stronę **Automations** i utwórz nową
automatyzację:

1. Wybierz **Create automation** i typ **Prompt preset**.
2. Ustaw **Name** na `GitHub Development Digest to Slack`.
3. Ustaw **Prompt** na poniższy tekst, zastępując symbole zastępcze
   repozytorium i kanału własnymi wartościami:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Ustaw **Trigger** na **Cron** z harmonogramem `0 9 * * 1-5` (9:00 w dni
   robocze) i ustaw **Timezone** na swoją strefę czasową, na przykład
   `America/New_York`.
5. Ustaw **Timeout** na `900` sekund.
6. Zapisz automatyzację.

Strona szczegółów automatyzacji pokazuje nowo utworzoną automatyzację wraz z
jej wyzwalaczem cron oraz wygenerowanym punktem wejścia typu prompt-preset.

![Strona szczegółów automatyzacji w Agent Canvas po utworzeniu](assets/05-automation-created.png)
## 7. Przetestuj automatyzację

Na stronie szczegółów automatyzacji w interfejsie Agent Canvas UI:

1. Kliknij **Run now** (lub **Dispatch**), aby uruchomić automatyzację jednorazowo, natychmiast.
2. Obserwuj listę uruchomień na tej samej stronie. Najnowsze uruchomienie powinno zmienić status na
   `COMPLETED`.
3. Otwórz docelowy kanał Slack. Powinien zawierać wygenerowany digest.

Nie musisz czekać na uruchomienie harmonogramu cron — **Run now** wyzwala
uruchomienie na żądanie, dzięki czemu możesz potwierdzić, że prompt, połączenia MCP i publikowanie na Slacku
działają poprawnie, zanim zaczniesz polegać na harmonogramie.

![Pomyślnie zakończone uruchomienie automatyzacji Agent Canvas](assets/06-automation-run-completed.png)

![Kanał Slack pokazujący wygenerowany digest OpenHands](assets/07-slackbot-message.png)

## Rozwiązywanie problemów

- **Lemonade nie działa:** uruchom go ponownie za pomocą polecenia
  `lemonade run "${LEMONADE_MODEL}"` z kroku 1, a następnie ponownie wykonaj kontrolę
  stanu (health check).
- **`npm install -g` kończy się błędem uprawnień:** w systemie Linux lub WSL
  skonfiguruj globalny katalog npm należący do użytkownika, dodaj go do pliku startowego powłoki,
  a następnie zainstaluj Agent Canvas ponownie:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Jeśli używasz `zsh`, dodaj tę samą linię `export PATH=...` do pliku `~/.zshrc`
  zamiast do `~/.bashrc`.
- **Agent Canvas odrzuca ustawienia LLM po ustawieniu `custom_tokenizer`:**
  zainstaluj `transformers` w środowisku Python Agent Server, w razie potrzeby uruchom ponownie Agent
  Canvas i spróbuj ponownie zapisać ustawienia LLM. OpenHands wymaga
  biblioteki Transformers do wczytania szablonu czatu tokenizera, gdy ustawiono `custom_tokenizer`.
- **Agent Canvas nie może połączyć się z Lemonade:** sprawdź
  `curl -fsS "${LEMONADE_BASE_URL}/health"` i upewnij się, że adres bazowy wprowadzony w
  formularzu LLM przy pierwszym użyciu lub w **Settings > LLM** odpowiada uruchomionemu lokalnemu
  punktowi końcowemu lub tunelowi HTTPS.
- **Ustawienia LLM nie zostały zapisane:** upewnij się, że kliknięto **Next** po
  wprowadzeniu wartości. Otwórz ponownie **Settings > LLM**, aby potwierdzić, że wartości
  zostały zachowane.
- **GitHub MCP nie widzi prywatnych repozytoriów:** potwierdź, że token GitHub ma
  dostęp do odczytu docelowego repozytorium oraz że przycisk **Test** MCP w
  **Customize** wyświetla narzędzia GitHub.
- **Slack może odczytywać kanały, ale nie może publikować:** zaproś aplikację Slack do
  docelowego kanału i upewnij się, że bot ma uprawnienie `chat:write`.
- **Automatyzacja wyświetla zbyt wiele kanałów Slack:** użyj identyfikatora kanału Slack i
  ustaw `SLACK_CHANNEL_IDS` na serwerze Slack MCP w **Customize**.
- **Uruchomienie automatyzacji kończy się niepowodzeniem lub przekracza kontekst:** upewnij się, że Lemonade zostało uruchomione
  z `ctx_size=65536`, że w LLM OpenHands ustawiono `custom_tokenizer`,
  oraz użyj konkretnego repozytorium z wynikami GitHub ograniczonymi do 3–5
  elementów. Jeśli Twoja wersja Agent Canvas udostępnia ustawienia kondensera (condenser), ustaw maksymalną liczbę tokenów kondensera
  poniżej okna kontekstu Lemonade.

## Następne kroki

- Dodaj cotygodniowy digest zawierający tylko wydania (release-only).
- Dodaj automatyzację wyzwalaną zdarzeniem GitHub, aby szybciej otrzymywać alerty o PR lub push.
- Skieruj ten sam digest do Notion, Linear lub innego narzędzia opartego na MCP.

## Zasoby

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentacja Lemonade Server](https://lemonade-server.ai/docs)
- [Repozytorium rozszerzeń OpenHands](https://github.com/OpenHands/extensions)
- [Serwery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pakiet Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)