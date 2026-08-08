<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversikt

Utviklere bruker mye tid på små tilbakevendende oppgaver: å gjennomgå merkede
pull-requester, svare på GitHub-kommentarer, triagere nye saker, gjøre om
Slack-tråder til statusnotater eller hendelsesoppfølginger, og følge med på
signaler om utgivelser eller forskning. Hver oppgave er kjent, men den krever
likevel vurdering: samle riktig kontekst, avgjøre hva som er viktig, og legge
ut en tydelig oppdatering der teamet allerede jobber.

[OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview)
gjør disse oppgavene om til planlagte eller hendelsesutløste agentsamtaler:
kjøringer der en AI-programvareagent kan lese kontekst, kalle verktøy og
produsere en oppdatering. De delte automatiseringsmalene i OpenHands
extensions-katalogen følger dette mønsteret for gjennomgang av GitHub
pull-requester, overvåking av repositorier, triagering av Linear-saker,
gjennomganger etter hendelser, Slack-statussammendrag og forskningsrapporter:
en automatisering våkner, bruker konfigurerte integrasjoner som GitHub eller
Slack til å hente kontekst, resonnerer over den konteksten med en stor
språkmodell (LLM), og skriver tilbake et resultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det lokale
kontrollplanet for å bygge og teste disse automatiseringene. I denne
oppskriften kjører det en OpenHands Agent Server, backend-prosessen som
utfører agentsamtaler, og kobler agenten til eksterne tjenester som GitHub og
Slack.

For å holde arbeidsflyten på AMD-systemet ditt, snakker agenten med en lokal
modell som betjenes av Lemonade Server. Lemonade eksponerer den modellen
gjennom et OpenAI-kompatibelt API, slik at Agent Canvas kan konfigurere den som
et eksternt OpenAI-lignende endepunkt, mens modellen, prompten og
arbeidsflytkonteksten forblir lokal.

I denne oppskriften bygger du én konkret automatisering: en planlagt
GitHub-til-Slack-utviklingssammendrag. Den bruker GitHub til å inspisere nylig
repositoraktivitet, Slack til å legge ut sammendraget, Agent Canvas
API-kall for å konfigurere og teste automatiseringen, og Lemonade til å kjøre
LLM-en lokalt.

![Arkitekturdiagram som viser GitHub MCP, OpenHands-automatisering, Lemonade Server og Slack MCP](assets/00-architecture-overview.png)

## Hva du vil lære

- Hvordan starte Lemonade Server og bekrefte at en lokal modell svarer på
  chat-forespørsler
- Hvordan starte Agent Canvas og peke Agent Server til en lokal LLM
- Hvordan installere GitHub- og Slack Model Context Protocol (MCP)-servere
  gjennom Agent Server-API-et
- Hvordan opprette og utløse en planlagt OpenHands-automatisering som legger
  ut et utviklingssammendrag til Slack
- Hvordan feilsøke de vanligste feilene knyttet til lokal modell og
  automatisering

## Kjernebegreper

| Begrep | Hva det er | Hvor det passer inn i denne oppskriften |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform bygget for AMD-maskinvare som eksponerer et OpenAI-kompatibelt API. Dataene dine forlater aldri maskinen din. | Kjører modellen som driver agenten. |
| OpenHands Agent Server | Backend-prosessen som utfører OpenHands-agentsamtaler. | Er vert for agenten, LLM-profilen og MCP-serverne. |
| Agent Canvas | Det lokale kontrollplanet for OpenHands som kjører Agent Server og et grensesnitt for å inspisere agentkjøringer. | Starter backendene og gir API-et du kaller. |
| MCP-server | En Model Context Protocol-server som gir en agent verktøy for en ekstern tjeneste som GitHub eller Slack. | Lar agenten lese GitHub og skrive til Slack. |
| OpenHands-automatisering | En planlagt eller hendelsesutløst agentsamtale som henter kontekst, resonnerer over den og skriver et resultat et sted. | GitHub-til-Slack-sammendraget du bygger her. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodende agent-arbeidsflyter drar nytte av en større modell og et større
> kontekstvindu. Bruk minst 32 GB systemminne, og foretrekk 64 GB eller mer
> for større GGUF-modeller.
<!-- @device:end -->

## Forutsetninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du trenger:

- Lemonade Server installert ved å følge den standard
  [Lemonade installasjonsveiledningen](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 eller nyere og `npm`, brukt til å installere den publiserte
  Agent Canvas CLI-en og kjøre MCP-servere med `npx`.
- En nylig publisert `@openhands/agent-canvas`-pakke med
  skjemadrevne agentinnstillinger, `LLMSummarizingCondenserSettings.max_tokens`,
  og LLM `custom_tokenizer`-støtte.
- Python-pakken `transformers` tilgjengelig i Agent Server-miljøet. Den kreves
  for tellling av tokener i chat-maler når `custom_tokenizer` er satt.
- En GitHub-token med lesetilgang til repositoriet du vil oppsummere.
- Et Slack-bottoken (`xoxb-...`) med `chat:write` og lesetilgang til kanaler.
- En Slack-team-ID (`T...`).
- En Slack-kanal-ID (`C...`) der sammendraget skal legges ut.

Inviter Slack-appen til målkanalen før du tester automatiseringen.

## Variabler brukt i denne oppskriften

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

Følgende verdier legges inn i Agent Canvas-grensesnittet i senere trinn. Sett
dem opp her slik at du kan kopiere dem inn:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Bruk en eksplisitt `owner/repo`-verdi for `GITHUB_REPO_FILTER`. Brede
organisasjons-jokertegn kan returnere for mye MCP-kontekst for lokale modeller.

## 1. Start Lemonade Server

Start modellen fra Lemonade CLI-en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade eksponerer et OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

Valgfritt: hvis Agent Canvas eller automatiseringskjøreren ikke er på samme
maskin, publiser Lemonade-endepunktet gjennom en sikker tunnel og bruk
HTTPS-URL-en som LLM-baseadresse:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Bekreft den lokale modellen

Bekreft at Lemonade kan betjene den valgte modellen:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Send deretter en liten chat-forespørsel:

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

Hvis dette returnerer en `choices`-array, er Lemonade klar for Agent Canvas.
## 3. Start Agent Canvas

Installer den publiserte Agent Canvas-pakken og start hele stakken:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Hvis den globale npm install feiler med en tillatelsesfeil, se
feilsøkingsoppføringen for npm-tillatelser nedenfor.

Som standard starter Agent Canvas på `http://localhost:8000`. Åpne den URL-en i
nettleseren din. Standard lokal backend bør vises som frisk («healthy») på
hjemmeskjermen.

Kommandoen `agent-canvas` starter agentserveren, automatiseringsbackenden og
webfronten sammen. Du trenger bare denne ene kommandoen for å kjøre OpenHands
lokalt. Resten av denne håndboken konfigurerer alt gjennom Agent
Canvas-brukergrensesnittet i nettleseren din.

## 4. Konfigurer den lokale LLM-en i brukergrensesnittet

Ved første oppstart åpner Agent Canvas en onboarding-flyt. I den flyten:

1. Behold **OpenHands** valgt som agent og klikk **Next**.
2. Under **Set up your LLM**, velg **Advanced**.
3. Behold **Authentication** satt til **API key**.
4. Sett **Custom Model** til verdien til `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sett **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, skriv inn en hvilken som helst ikke-tom plassholder som
   `lemonade-local`. Lemonade krever ikke en ekte nøkkel, men OpenHands-klienten
   trenger en verdi å sende.

Tilkoblingsfeltene skal se slik ut. API-nøkkelfeltet er maskert av
brukergrensesnittet.

![Agent Canvas-innstillinger for LLM Advanced ved første bruk med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Velg deretter **All** og angi de ekstra feltene for lokal modell:

1. Bla ned til **Custom Tokenizer** og sett den til `Qwen/Qwen3.6-35B-A3B`.
2. Bla ned til **LiteLLM Extra Body** og sett den til
   `{"enable_thinking": true}`.
3. Klikk **Next**.

![Agent Canvas-fane LLM All ved første bruk med Qwen egendefinert tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas-fane LLM All ved første bruk med LiteLLM extra body konfigurert](assets/03-llm-all-extra-body-settings.png)

LLM-innstillingene skal vise:

| Felt | Verdi |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefikset `openai/` forteller LiteLLM å bruke OpenAI-kompatibel
forespørselsformatering mot Lemonade-endepunktet. Den egendefinerte
tokenizeren er den opprinnelige Hugging Face-tokenizeren for GGUF-modellen;
den lar OpenHands telle de samme chat-mal-tokenene som den lokale
modellserveren ser. Det nåværende LLM-skjemaet for førstegangsbruk viser ikke
condenser-innstillinger. Hvis Agent Canvas-versjonen din senere viser
condenser-innstillinger under **Settings > LLM**, bruk `llm_summarizing` og
sett maks antall tokens under Lemonade-kontekstvinduet, for eksempel `56000`.

## 5. Installer GitHub- og Slack-MCP-servere

I Agent Canvas-brukergrensesnittet, åpne **Customize** (eller **Settings >
MCP**) for å legge til MCP-serverne som gir agenten verktøy for GitHub og
Slack. Tokenverdier sendes kun til din lokale Agent Server og lagres som
krypterte innstillinger.

### GitHub MCP-server

Legg til en ny MCP-server med disse innstillingene:

| Felt | Verdi |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = din GitHub-token |

Bruk en GitHub-token med lesetilgang til repositoriet du vil ha oppsummert.

### Slack MCP-server

Legg til en ny MCP-server med disse innstillingene:

| Felt | Verdi |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = din digest-kanal-ID |

Sett `SLACK_CHANNEL_IDS` til digest-kanal-IDen (samme verdi som
`SLACK_DIGEST_CHANNEL`) slik at agenten ikke trenger å bla gjennom hver eneste
Slack-kanal.

Etter at du har lagt til begge serverne, bruk **Test**-knappen på hver av dem
for å bekrefte at den kobler til og annonserer verktøy. GitHub-serveren skal
liste GitHub-verktøy, og Slack-serveren skal liste Slack-verktøy.

![Agent Canvas MCP-side med GitHub- og Slack-servere installert](assets/04-mcp-servers-installed.png)

## 6. Opprett digest-automatiseringen

I Agent Canvas-brukergrensesnittet, åpne **Automations**-siden og opprett en
ny automatisering:

1. Velg **Create automation** og velg typen **Prompt preset**.
2. Sett **Name** til `GitHub Development Digest to Slack`.
3. Sett **Prompt** til følgende tekst, og erstatt plassholderne for
   repositorium og kanal med dine egne verdier:

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

4. Sett **Trigger** til **Cron** med tidsplanen `0 9 * * 1-5` (klokken 9 på
   hverdager) og sett **Timezone** til din tidssone, for eksempel
   `America/New_York`.
5. Sett **Timeout** til `900` sekunder.
6. Lagre automatiseringen.

Detaljsiden for automatiseringen viser den nye automatiseringen med
cron-triggeren og det genererte prompt-preset-inngangspunktet.

![Agent Canvas-automatiseringsdetaljer etter opprettelse](assets/05-automation-created.png)
## 7. Test automatiseringen

Fra automatiseringens detaljside i Agent Canvas-brukergrensesnittet:

1. Klikk på **Run now** (eller **Dispatch**) for å kjøre automatiseringen én gang umiddelbart.
2. Følg med på kjørelisten på samme side. Den siste kjøringen skal gå over til
   `COMPLETED`.
3. Åpne målkanalen din i Slack. Den skal inneholde det genererte sammendraget.

Du trenger ikke å vente på at cron-planen skal utløses – **Run now** utløser en
kjøring på forespørsel, slik at du kan bekrefte at prompten, MCP-tilkoblingene og Slack-publiseringen
alle fungerer før du stoler på planen.

![Agent Canvas-automatisering fullført](assets/06-automation-run-completed.png)

![Slack-kanal som viser det genererte OpenHands-sammendraget](assets/07-slackbot-message.png)

## Feilsøking

- **Lemonade er nede:** start den på nytt med
  kommandoen `lemonade run "${LEMONADE_MODEL}"` fra trinn 1, og kjør deretter
  helsesjekken på nytt.
- **`npm install -g` mislykkes med en tillatelsesfeil:** på Linux eller WSL,
  konfigurer en brukereid, global npm-katalog, legg den til i shell-oppstartsfilen
  din, og installer deretter Agent Canvas på nytt:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Hvis du bruker `zsh`, legger du til den samme `export PATH=...`-linjen i `~/.zshrc` i stedet
  for `~/.bashrc`.
- **Agent Canvas avviser LLM-innstillingene etter at `custom_tokenizer` er angitt:**
  installer `transformers` i Python-miljøet til Agent Server, start Agent
  Canvas på nytt om nødvendig, og prøv å lagre LLM-innstillingene igjen. OpenHands krever
  Transformers for å laste tokenizer-chatmalen når `custom_tokenizer` er
  angitt.
- **Agent Canvas får ikke kontakt med Lemonade:** bekreft
  `curl -fsS "${LEMONADE_BASE_URL}/health"` og kontroller at grunn-URL-en som er angitt i
  LLM-skjemaet ved førstegangsbruk eller under **Settings > LLM** samsvarer med det kjørende lokale
  endepunktet eller HTTPS-tunnelen.
- **LLM-innstillingene ble ikke lagret:** kontroller at du klikket på **Next** etter
  at du har angitt verdiene. Åpne **Settings > LLM** på nytt for å bekrefte at verdiene
  ble lagret.
- **GitHub MCP kan ikke se private repositorier:** bekreft at GitHub-tokenet har
  lesetilgang til målrepositoriet, og at **Test**-knappen for MCP i
  **Customize** viser GitHub-verktøy.
- **Slack kan lese kanaler, men kan ikke publisere:** inviter Slack-appen til
  målkanalen, og bekreft at boten har `chat:write`.
- **Automatiseringen viser for mange Slack-kanaler:** bruk en Slack-kanal-ID og
  angi `SLACK_CHANNEL_IDS` på Slack MCP-serveren i **Customize**.
- **Automatiseringskjøringen mislykkes eller overskrider konteksten:** bekreft at Lemonade ble startet
  med `ctx_size=65536`, bekreft at OpenHands-LLM-en har `custom_tokenizer` angitt,
  og bruk et eksplisitt repositorium med GitHub-resultatsett begrenset til 3 til 5
  elementer. Hvis Agent Canvas-bygget ditt eksponerer condenser-innstillinger, angir du at
  maks antall token for condenser skal være lavere enn Lemonade-kontekstvinduet.

## Neste trinn

- Legg til et ukentlig sammendrag kun for utgivelser.
- Legg til en GitHub-hendelsesutløst automatisering for raskere varsler ved PR-er eller push.
- Rut det samme sammendraget til Notion, Linear eller et annet MCP-basert verktøy.

## Ressurser

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentasjon](https://lemonade-server.ai/docs)
- [OpenHands-utvidelsesrepositorium](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servere](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-pakke](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)