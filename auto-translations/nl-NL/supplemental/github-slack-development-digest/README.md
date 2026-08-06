<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Overzicht

Ontwikkelaars besteden veel tijd aan kleine, terugkerende lussen: het beoordelen
van gelabelde pull requests, het beantwoorden van GitHub-commentaren, het
triëren van nieuwe issues, het omzetten van Slack-threads in standupnotities
of incidentopvolgingen, en het volgen van release- of onderzoekssignalen. Elke
lus is bekend, maar vereist nog steeds inzicht: de juiste context verzamelen,
bepalen wat belangrijk is, en een duidelijke update plaatsen waar het team al
werkt.

[OpenHands-automatiseringen](https://docs.openhands.dev/openhands/usage/automations/overview)
zetten die lussen om in geplande of event-getriggerde agentgesprekken: runs
waarbij een AI-softwareagent context kan lezen, tools kan aanroepen en een
update kan produceren. De gedeelde automatiseringssjablonen in de
OpenHands-extensiescatalogus volgen dit patroon voor GitHub pull request
review, repositorybewaking, Linear issue triage, incidentretrospectieven,
Slack standup-digests en onderzoeksbriefings: een automatisering ontwaakt,
gebruikt geconfigureerde integraties zoals GitHub of Slack om context op te
halen, redeneert over die context met een large language model (LLM), en
schrijft een resultaat terug.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is het lokale
controlplatform voor het bouwen en testen van die automatiseringen. In dit
playbook draait het een OpenHands Agent Server, het backendproces dat
agentgesprekken uitvoert, en verbindt het de agent met externe diensten zoals
GitHub en Slack.

Om de workflow op uw AMD-systeem te houden, communiceert de agent met een
lokaal model dat wordt geserveerd door Lemonade Server. Lemonade stelt dat
model beschikbaar via een OpenAI-compatibele API, zodat Agent Canvas het kan
configureren als een extern OpenAI-achtig endpoint, terwijl het model, de
prompt en de workflowcontext lokaal blijven.

In dit playbook bouwt u één concrete automatisering: een geplande
GitHub-naar-Slack-ontwikkelingsdigest. Deze gebruikt GitHub om recente
repositoryactiviteit te inspecteren, Slack om de digest te plaatsen,
Agent Canvas API-aanroepen om de automatisering te configureren en te testen,
en Lemonade om de LLM lokaal uit te voeren.

![Architectuurdiagram met GitHub MCP, OpenHands-automatisering, Lemonade Server en Slack MCP](assets/00-architecture-overview.png)

## Wat u zult leren

- Hoe u Lemonade Server start en verifieert dat een lokaal model
  chatverzoeken beantwoordt
- Hoe u Agent Canvas start en de Agent Server richt op een lokale LLM
- Hoe u GitHub- en Slack Model Context Protocol (MCP)-servers installeert via
  de Agent Server API
- Hoe u een geplande OpenHands-automatisering aanmaakt en verzendt die een
  ontwikkelingsdigest naar Slack plaatst
- Hoe u de meest voorkomende storingen in lokale modellen en automatiseringen
  oplost

## Kernconcepten

| Concept | Wat het is | Waar het past in dit playbook |
| --- | --- | --- |
| Lemonade Server | Een lokaal LLM-serveerplatform gebouwd voor AMD-hardware dat een OpenAI-compatibele API beschikbaar stelt. Uw gegevens verlaten nooit uw machine. | Draait het model dat de agent aandrijft. |
| OpenHands Agent Server | Het backendproces dat OpenHands-agentgesprekken uitvoert. | Host de agent, diens LLM-profiel en diens MCP-servers. |
| Agent Canvas | Het lokale controlplatform voor OpenHands dat de Agent Server en een UI voor het inspecteren van agentruns uitvoert. | Start de backends en biedt de API die u aanroept. |
| MCP-server | Een Model Context Protocol-server die een agent tools geeft voor een externe dienst zoals GitHub of Slack. | Laat de agent GitHub lezen en naar Slack schrijven. |
| OpenHands-automatisering | Een gepland of event-getriggerd agentgesprek dat context ophaalt, erover redeneert en ergens een resultaat schrijft. | De GitHub-naar-Slack-digest die u hier bouwt. |

<!-- @device:stx,krk -->
> [!NOTE]
> Coding-agentworkflows profiteren van een groter model en contextvenster. Gebruik ten
> minste 32 GB systeemgeheugen, en geef de voorkeur aan 64 GB of meer voor grotere GGUF-modellen.
<!-- @device:end -->

## Vereisten

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

U heeft nodig:

- Lemonade Server geïnstalleerd door de standaard
  [Lemonade-installatiehandleiding](https://lemonade-server.ai/docs/guide/install/) te volgen.
- Node.js 22.12 of later en `npm`, gebruikt om de gepubliceerde Agent Canvas
  CLI te installeren en MCP-servers uit te voeren met `npx`.
- Een recent gepubliceerd `@openhands/agent-canvas`-pakket met
  schema-gestuurde agentinstellingen, `LLMSummarizingCondenserSettings.max_tokens`,
  en ondersteuning voor LLM `custom_tokenizer`.
- Het Python-pakket `transformers` beschikbaar in de Agent Server-omgeving.
  Dit is vereist voor het tellen van chat-template-tokens wanneer
  `custom_tokenizer` is ingesteld.
- Een GitHub-token met leestoegang tot de repository die u wilt samenvatten.
- Een Slack-bot-token (`xoxb-...`) met `chat:write`- en kanaal-leestoegang.
- Een Slack-team-ID (`T...`).
- Een Slack-kanaal-ID (`C...`) waar de digest moet worden geplaatst.

Nodig de Slack-app uit voor het doelkanaal voordat u de automatisering test.

## Variabelen die in dit playbook worden gebruikt

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

De volgende waarden worden in latere stappen in de Agent Canvas UI ingevoerd.
Stel ze hier in zodat u ze later kunt kopiëren:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Gebruik een expliciete `owner/repo`-waarde voor `GITHUB_REPO_FILTER`. Brede
organisatie-wildcards kunnen te veel MCP-context opleveren voor lokale
modellen.

## 1. Lemonade Server starten

Start het model vanuit de Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade stelt een OpenAI-compatibele API beschikbaar op:

```text
http://127.0.0.1:13305/api/v1
```

Optioneel: als Agent Canvas of de automatiseringsrunner niet op dezelfde
machine draait, publiceer dan het Lemonade-endpoint via een beveiligde tunnel
en gebruik de HTTPS-URL als de LLM-basis-URL:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Het lokale model verifiëren

Bevestig dat Lemonade het geselecteerde model kan serveren:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Stuur vervolgens een klein chatverzoek:

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

Als dit een `choices`-array retourneert, is Lemonade klaar voor Agent Canvas.
## 3. Start Agent Canvas

Installeer het gepubliceerde Agent Canvas-pakket en start de volledige stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Als de globale npm-installatie mislukt met een rechtenfout, raadpleeg dan het
onderdeel over npm-rechtenproblemen hieronder.

Standaard start Agent Canvas op `http://localhost:8000`. Open die URL in je
browser. De standaard lokale backend zou als gezond ("healthy") moeten
verschijnen op het startscherm.

Het commando `agent-canvas` start de agentserver, de automation-backend en de
webfrontend samen. Je hebt dit ene commando nodig om OpenHands lokaal uit te
voeren. De rest van dit playbook configureert alles via de Agent Canvas UI in
je browser.

## 4. Configureer de lokale LLM in de UI

Bij de eerste start opent Agent Canvas een onboardingflow. In die flow:

1. Houd **OpenHands** geselecteerd als agent en klik op **Next**.
2. Selecteer bij **Set up your LLM** de optie **Advanced**.
3. Houd **Authentication** ingesteld op **API key**.
4. Stel **Custom Model** in op de waarde van `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Stel **Base URL** in op `http://127.0.0.1:13305/api/v1`.
6. Voer bij **API Key** een willekeurige niet-lege placeholder in, zoals
   `lemonade-local`. Lemonade vereist geen echte sleutel, maar de OpenHands
   client heeft wel een waarde nodig om te verzenden.

De verbindingsvelden zouden er zo uit moeten zien. Het API-sleutelveld wordt
door de UI gemaskeerd.

![Agent Canvas eerste-gebruik LLM Advanced-instellingen met het Lemonade-model en lokale base URL](assets/01-llm-advanced-settings.png)

Selecteer vervolgens **All** en stel de extra velden voor het lokale model in:

1. Scroll naar **Custom Tokenizer** en stel deze in op `Qwen/Qwen3.6-35B-A3B`.
2. Scroll naar **LiteLLM Extra Body** en stel deze in op
   `{"enable_thinking": true}`.
3. Klik op **Next**.

![Agent Canvas eerste-gebruik LLM All-tab met de aangepaste Qwen-tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas eerste-gebruik LLM All-tab met geconfigureerde LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

De LLM-instellingen zouden het volgende moeten tonen:

| Veld | Waarde |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Het voorvoegsel `openai/` vertelt LiteLLM om OpenAI-compatibele
verzoekopmaak te gebruiken tegen het Lemonade-eindpunt. De aangepaste
tokenizer is de originele Hugging Face-tokenizer voor het GGUF-model; hiermee
kan OpenHands dezelfde chat-template-tokens tellen die de lokale
modelserver ziet. Het huidige eerste-gebruik LLM-formulier toont geen
condenser-instellingen. Als jouw Agent Canvas-build condenser-instellingen
later wel toont onder **Settings > LLM**, gebruik dan `llm_summarizing` en
stel het maximum aantal tokens in onder het Lemonade-contextvenster, zoals
`56000`.

## 5. Installeer GitHub- en Slack-MCP-servers

Open in de Agent Canvas UI **Customize** (of **Settings > MCP**) om de
MCP-servers toe te voegen die de agent tools geven voor GitHub en Slack.
Tokenwaarden worden alleen naar je lokale Agent Server verzonden en worden
opgeslagen als versleutelde instellingen.

### GitHub MCP-server

Voeg een nieuwe MCP-server toe met deze instellingen:

| Veld | Waarde |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = jouw GitHub-token |

Gebruik een GitHub-token met leestoegang tot de repository die je wilt
samenvatten.

### Slack MCP-server

Voeg een tweede MCP-server toe met deze instellingen:

| Veld | Waarde |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = jouw digest-kanaal-ID |

Stel `SLACK_CHANNEL_IDS` in op het digest-kanaal-ID (dezelfde waarde als
`SLACK_DIGEST_CHANNEL`) zodat de agent niet elk Slack-kanaal hoeft door te
bladeren.

Nadat je beide servers hebt toegevoegd, gebruik je de knop **Test** op elke
server om te bevestigen dat deze verbinding maakt en tools adverteert. De
GitHub-server zou GitHub-tools moeten weergeven en de Slack-server zou
Slack-tools moeten weergeven.

![Agent Canvas MCP-pagina met geïnstalleerde GitHub- en Slack-servers](assets/04-mcp-servers-installed.png)

## 6. Maak de digest-automatisering

Open in de Agent Canvas UI de pagina **Automations** en maak een nieuwe
automatisering aan:

1. Kies **Create automation** en selecteer het type **Prompt preset**.
2. Stel de **Name** in op `GitHub Development Digest to Slack`.
3. Stel de **Prompt** in op de volgende tekst, waarbij je de placeholders voor
   repository en kanaal vervangt door jouw waarden:

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

4. Stel de **Trigger** in op **Cron** met het schema `0 9 * * 1-5` (9 uur 's
   ochtends op weekdagen) en stel de **Timezone** in op jouw tijdzone,
   bijvoorbeeld `America/New_York`.
5. Stel de **Timeout** in op `900` seconden.
6. Sla de automatisering op.

De detailpagina van de automatisering toont de nieuwe automatisering met de
cron-trigger en het gegenereerde prompt-preset-entrypoint.

![Agent Canvas automatiseringsdetail na aanmaken](assets/05-automation-created.png)
## 7. Test de Automatisering

Vanaf de detailpagina van de automatisering in de Agent Canvas UI:

1. Klik op **Run now** (of **Dispatch**) om de automatisering onmiddellijk één keer uit te voeren.
2. Bekijk de runlijst op dezelfde pagina. De laatste run zou moeten overgaan naar
   `COMPLETED`.
3. Open het beoogde Slack-kanaal. Het zou de gegenereerde digest moeten bevatten.

Je hoeft niet te wachten tot het cron-schema afgaat—**Run now** activeert een
run op aanvraag, zodat je kunt bevestigen dat de prompt, MCP-verbindingen en het posten naar Slack
allemaal werken voordat je op het schema vertrouwt.

![Agent Canvas-automatiseringsrun succesvol voltooid](assets/06-automation-run-completed.png)

![Slack-kanaal met de gegenereerde OpenHands-digest](assets/07-slackbot-message.png)

## Probleemoplossing

- **Lemonade ligt eruit:** herstart het met het
  `lemonade run "${LEMONADE_MODEL}"`-commando uit stap 1 en voer daarna de health
  check opnieuw uit.
- **`npm install -g` mislukt met een permissiefout:** configureer op Linux of WSL
  een globale npm-map die eigendom is van de gebruiker, voeg deze toe aan je shell-startupbestand
  en installeer Agent Canvas opnieuw:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Als je `zsh` gebruikt, voeg dan dezelfde `export PATH=...`-regel toe aan `~/.zshrc` in plaats
  van `~/.bashrc`.
- **Agent Canvas wijst de LLM-instellingen af na het instellen van `custom_tokenizer`:**
  installeer `transformers` in de Python-omgeving van de Agent Server, herstart Agent
  Canvas indien nodig en probeer de LLM-instellingen opnieuw op te slaan. OpenHands vereist
  Transformers om de tokenizer chat template te laden wanneer `custom_tokenizer` is
  ingesteld.
- **Agent Canvas kan Lemonade niet bereiken:** controleer
  `curl -fsS "${LEMONADE_BASE_URL}/health"` en bevestig dat de basis-URL die is ingevoerd in
  het LLM-formulier bij eerste gebruik of onder **Settings > LLM** overeenkomt met het draaiende lokale
  eindpunt of de HTTPS-tunnel.
- **De LLM-instellingen zijn niet opgeslagen:** zorg ervoor dat je op **Next** hebt geklikt na
  het invoeren van de waarden. Open **Settings > LLM** opnieuw om te bevestigen dat de waarden
  behouden zijn gebleven.
- **GitHub MCP kan geen privérepositories zien:** bevestig dat de GitHub-token leestoegang heeft
  tot de doelrepository en dat de **Test**-knop van MCP in
  **Customize** GitHub-tools aankondigt.
- **Slack kan kanalen lezen maar niet posten:** nodig de Slack-app uit voor het
  doelkanaal en bevestig dat de bot `chat:write` heeft.
- **De automatisering geeft te veel Slack-kanalen weer:** gebruik een Slack-kanaal-ID en
  stel `SLACK_CHANNEL_IDS` in op de Slack MCP-server onder **Customize**.
- **De automatiseringsrun mislukt of overschrijdt de context:** bevestig dat Lemonade is gestart
  met `ctx_size=65536`, bevestig dat de OpenHands LLM `custom_tokenizer` heeft ingesteld,
  en gebruik een expliciete repository met GitHub-resultaatsets die beperkt zijn tot 3 tot 5
  items. Als je Agent Canvas-build condenser-instellingen biedt, stel dan het maximaal aantal condenser-tokens in
  onder het Lemonade-contextvenster.

## Volgende Stappen

- Voeg een wekelijkse, alleen-release-digest toe.
- Voeg een door GitHub-events geactiveerde automatisering toe voor snellere PR- of push-meldingen.
- Stuur dezelfde digest door naar Notion, Linear, of een andere MCP-ondersteunde tool.

## Bronnen

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-documentatie](https://lemonade-server.ai/docs)
- [OpenHands-extensierepository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servers](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-pakket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)