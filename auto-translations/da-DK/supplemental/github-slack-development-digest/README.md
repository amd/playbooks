<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Oversigt

Udviklere bruger meget tid på små, tilbagevendende arbejdsgange: at gennemgå
mærkede pull requests, besvare GitHub-kommentarer, triagere nye issues, omdanne
Slack-tråde til standupnotater eller opfølgning på hændelser, og holde styr på
release- eller forskningssignaler. Hver arbejdsgang er velkendt, men kræver
stadig vurderingsevne: at indsamle den rette kontekst, beslutte hvad der er
vigtigt, og skrive en klar opdatering, hvor teamet allerede arbejder.

[OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview)
omdanner disse arbejdsgange til planlagte eller hændelsesudløste
agent-samtaler: kørsler hvor en AI-softwareagent kan læse kontekst, kalde
værktøjer og producere en opdatering. De delte automatiseringsskabeloner i
OpenHands-udvidelseskataloget følger dette mønster til GitHub pull request-
gennemgang, repository-overvågning, Linear issue-triage, hændelses-
retrospektiver, Slack standup-digest og forskningsopdateringer: en
automatisering vågner, bruger konfigurerede integrationer såsom GitHub eller
Slack til at hente kontekst, ræsonnerer over den kontekst med en stor
sprogmodel (LLM) og skriver et resultat tilbage.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det lokale
kontrolplan til at bygge og teste disse automatiseringer. I denne playbook
kører det en OpenHands Agent Server, backend-processen der udfører
agent-samtaler, og forbinder agenten til eksterne tjenester såsom GitHub og
Slack.

For at holde arbejdsgangen på dit AMD-system taler agenten med en lokal model,
der serveres af Lemonade Server. Lemonade eksponerer den model gennem en
OpenAI-kompatibel API, så Agent Canvas kan konfigurere den som et
fjern-OpenAI-lignende endpoint, mens modellen, prompten og
arbejdsgangskonteksten forbliver lokale.

I denne playbook bygger du én konkret automatisering: et planlagt
GitHub-til-Slack udviklingsdigest. Den bruger GitHub til at inspicere nylig
repository-aktivitet, Slack til at poste digesten, Agent Canvas API-kald til
at konfigurere og teste automatiseringen, og Lemonade til at køre LLM'en
lokalt.

![Arkitekturdiagram, der viser GitHub MCP, OpenHands-automatisering, Lemonade Server og Slack MCP](assets/00-architecture-overview.png)

## Hvad du vil lære

- Hvordan man starter Lemonade Server og bekræfter, at en lokal model besvarer
  chatanmodninger
- Hvordan man starter Agent Canvas og peger dens Agent Server mod en lokal LLM
- Hvordan man installerer GitHub- og Slack Model Context Protocol (MCP)-
  servere via Agent Server API'et
- Hvordan man opretter og afsender en planlagt OpenHands-automatisering, der
  poster en udviklingsdigest til Slack
- Hvordan man fejlfinder de mest almindelige fejl med lokale modeller og
  automatisering

## Grundlæggende begreber

| Begreb | Hvad det er | Hvor det passer ind i denne playbook |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplatform bygget til AMD-hardware, der eksponerer en OpenAI-kompatibel API. Dine data forlader aldrig din maskine. | Kører den model, der driver agenten. |
| OpenHands Agent Server | Backend-processen, der udfører OpenHands agent-samtaler. | Er vært for agenten, dens LLM-profil og dens MCP-servere. |
| Agent Canvas | Det lokale kontrolplan til OpenHands, der kører Agent Server og en UI til at inspicere agentkørsler. | Starter backends og stiller det API til rådighed, du kalder. |
| MCP-server | En Model Context Protocol-server, der giver en agent værktøjer til en ekstern tjeneste såsom GitHub eller Slack. | Lader agenten læse GitHub og skrive til Slack. |
| OpenHands-automatisering | En planlagt eller hændelsesudløst agent-samtale, der henter kontekst, ræsonnerer over den og skriver et resultat et sted hen. | Den GitHub-til-Slack-digest, du bygger her. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodningsagent-arbejdsgange drager fordel af en større model og
> kontekstvindue. Brug mindst 32 GB systemhukommelse, og foretræk 64 GB eller
> mere til større GGUF-modeller.
<!-- @device:end -->

## Forudsætninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du skal bruge:

- Lemonade Server installeret ved at følge den
  [standard Lemonade-installationsvejledning](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 eller nyere og `npm`, brugt til at installere den udgivne
  Agent Canvas CLI og køre MCP-servere med `npx`.
- En nylig udgivet `@openhands/agent-canvas`-pakke med skemadrevne
  agentindstillinger, `LLMSummarizingCondenserSettings.max_tokens`, og
  LLM `custom_tokenizer`-understøttelse.
- Python-pakken `transformers` tilgængelig i Agent Server-miljøet. Den er
  nødvendig til chat-template-tokentælling, når `custom_tokenizer` er sat.
- Et GitHub-token med læseadgang til det repository, du vil have opsummeret.
- Et Slack bot-token (`xoxb-...`) med `chat:write` og kanallæseadgang.
- Et Slack team-ID (`T...`).
- Et Slack kanal-ID (`C...`), hvor digesten skal postes.

Inviter Slack-appen til målkanalen, før du tester automatiseringen.

## Variabler brugt i denne playbook

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

De følgende værdier indtastes i Agent Canvas UI'et i senere trin. Angiv dem
her, så du kan kopiere dem ind:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Brug en eksplicit `owner/repo`-værdi for `GITHUB_REPO_FILTER`. Brede
organisations-wildcards kan returnere for meget MCP-kontekst til lokale
modeller.

## 1. Start Lemonade Server

Start modellen fra Lemonade CLI'en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade eksponerer en OpenAI-kompatibel API på:

```text
http://127.0.0.1:13305/api/v1
```

Valgfrit: hvis Agent Canvas eller automatiseringskøreren ikke er på den samme
maskine, kan du udgive Lemonade-endpointet gennem en sikker tunnel og bruge
HTTPS-URL'en som LLM-baseurl'en:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Bekræft den lokale model

Bekræft, at Lemonade kan servere den valgte model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Send derefter en lille chatanmodning:

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

Hvis dette returnerer et `choices`-array, er Lemonade klar til Agent Canvas.
## 3. Start Agent Canvas

Installer den udgivne Agent Canvas-pakke og start den samlede stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Hvis den globale npm install fejler med en tilladelsesfejl, se afsnittet om
fejlfinding af npm-tilladelser nedenfor.

Som standard starter Agent Canvas på `http://localhost:8000`. Åbn denne URL i
din browser. Standard-backenden lokalt bør fremstå som sund på startskærmen.

Kommandoen `agent-canvas` starter agent-serveren, automation-backenden og
web-frontenden sammen. Du behøver kun denne ene kommando for at køre OpenHands
lokalt. Resten af denne playbook konfigurerer alt gennem Agent
Canvas-brugerfladen i din browser.

## 4. Konfigurer den lokale LLM i brugerfladen

Ved første opstart åbner Agent Canvas et onboarding-forløb. I dette forløb:

1. Behold **OpenHands** valgt som agent, og klik på **Next**.
2. Under **Set up your LLM**, vælg **Advanced**.
3. Behold **Authentication** sat til **API key**.
4. Sæt **Custom Model** til værdien for `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sæt **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, indtast en vilkårlig ikke-tom pladsholder, f.eks.
   `lemonade-local`. Lemonade kræver ikke en rigtig nøgle, men
   OpenHands-klienten skal bruge en værdi at sende.

Forbindelsesfelterne skal se sådan ud. API-nøglefeltet er maskeret af
brugerfladen.

![Agent Canvas indstillinger for LLM Advanced ved første brug med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Vælg derefter **All**, og udfyld de ekstra felter for den lokale model:

1. Rul ned til **Custom Tokenizer**, og sæt den til `Qwen/Qwen3.6-35B-A3B`.
2. Rul ned til **LiteLLM Extra Body**, og sæt den til
   `{"enable_thinking": true}`.
3. Klik på **Next**.

![Agent Canvas fanen LLM All ved første brug med den brugerdefinerede Qwen-tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas fanen LLM All ved første brug med konfigureret LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM-indstillingerne bør vise:

| Felt | Værdi |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Præfikset `openai/` fortæller LiteLLM at bruge OpenAI-kompatibel
anmodningsformatering mod Lemonade-endpointet. Den brugerdefinerede tokenizer
er den originale Hugging Face-tokenizer for GGUF-modellen; den gør det muligt
for OpenHands at tælle de samme chat-template-tokens, som den lokale
modelserver ser. Den nuværende first-use LLM-formular viser ikke
condenser-indstillinger. Hvis din Agent Canvas-build eksponerer
condenser-indstillinger senere under **Settings > LLM**, brug
`llm_summarizing`, og sæt maks. antal tokens under Lemonade-kontekstvinduet,
f.eks. `56000`.

## 5. Installer GitHub- og Slack-MCP-servere

I Agent Canvas-brugerfladen, åbn **Customize** (eller **Settings > MCP**) for
at tilføje de MCP-servere, der giver agenten værktøjer til GitHub og Slack.
Token-værdier sendes kun til din lokale Agent Server og gemmes som krypterede
indstillinger.

### GitHub MCP-server

Tilføj en ny MCP-server med disse indstillinger:

| Felt | Værdi |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = dit GitHub-token |

Brug et GitHub-token med læseadgang til det repository, du vil have
opsummeret.

### Slack MCP-server

Tilføj en anden MCP-server med disse indstillinger:

| Felt | Værdi |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = dit digest-kanal-ID |

Sæt `SLACK_CHANNEL_IDS` til digest-kanalens ID (samme værdi som
`SLACK_DIGEST_CHANNEL`), så agenten ikke behøver at bladre gennem hver eneste
Slack-kanal.

Efter tilføjelse af begge servere, brug knappen **Test** på hver af dem for at
bekræfte, at den forbinder og annoncerer værktøjer. GitHub-serveren bør vise
en liste over GitHub-værktøjer, og Slack-serveren bør vise en liste over
Slack-værktøjer.

![Agent Canvas MCP-side med GitHub- og Slack-servere installeret](assets/04-mcp-servers-installed.png)

## 6. Opret digest-automatiseringen

I Agent Canvas-brugerfladen, åbn siden **Automations**, og opret en ny
automatisering:

1. Vælg **Create automation**, og vælg typen **Prompt preset**.
2. Sæt **Name** til `GitHub Development Digest to Slack`.
3. Sæt **Prompt** til følgende tekst, idet du erstatter pladsholderne for
   repository og kanal med dine egne værdier:

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

4. Sæt **Trigger** til **Cron** med tidsplanen `0 9 * * 1-5` (kl. 9 på
   hverdage), og sæt **Timezone** til din tidszone, f.eks.
   `America/New_York`.
5. Sæt **Timeout** til `900` sekunder.
6. Gem automatiseringen.

Automatiseringens detaljeside viser den nye automatisering med dens
cron-trigger og det genererede prompt-preset-entrypoint.

![Agent Canvas automatiserings-detaljer efter oprettelse](assets/05-automation-created.png)
## 7. Test automationen

Fra automationens detaljeside i Agent Canvas-brugerfladen:

1. Klik på **Run now** (eller **Dispatch**) for at køre automationen én gang med det samme.
2. Følg med i kørselslisten på samme side. Den seneste kørsel bør skifte til
   `COMPLETED`.
3. Åbn din valgte Slack-kanal. Den bør indeholde det genererede sammendrag.

Du behøver ikke vente på, at cron-tidsplanen udløser—**Run now** starter en
kørsel på forlangende, så du kan bekræfte, at prompten, MCP-forbindelserne og Slack-postningen
alle fungerer, før du regner med tidsplanen.

![Agent Canvas-automation kørt med succes](assets/06-automation-run-completed.png)

![Slack-kanal, der viser det genererede OpenHands-sammendrag](assets/07-slackbot-message.png)

## Fejlfinding

- **Lemonade er nede:** genstart den med
  kommandoen `lemonade run "${LEMONADE_MODEL}"` fra trin 1, og kør derefter sundhedstjekket igen.
- **`npm install -g` fejler med en tilladelsesfejl:** på Linux eller WSL,
  konfigurer en brugerejet global npm-mappe, tilføj den til din shell-startfil, og installer derefter Agent Canvas igen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Hvis du bruger `zsh`, skal du tilføje den samme `export PATH=...`-linje til `~/.zshrc` i stedet
  for `~/.bashrc`.
- **Agent Canvas afviser LLM-indstillingerne efter angivelse af `custom_tokenizer`:**
  installer `transformers` i Agent Server-Python-miljøet, genstart Agent
  Canvas om nødvendigt, og prøv igen at gemme LLM-indstillingerne. OpenHands kræver
  Transformers for at indlæse tokenizerens chatskabelon, når `custom_tokenizer` er
  angivet.
- **Agent Canvas kan ikke nå Lemonade:** bekræft
  `curl -fsS "${LEMONADE_BASE_URL}/health"`, og kontrollér, at base-URL'en angivet i
  LLM-formularen ved første brug eller under **Settings > LLM** matcher det kørende lokale
  endepunkt eller HTTPS-tunnel.
- **LLM-indstillingerne blev ikke gemt:** sørg for, at du klikkede på **Next** efter
  indtastning af værdierne. Genåbn **Settings > LLM** for at bekræfte, at værdierne
  blev gemt.
- **GitHub MCP kan ikke se private repositories:** bekræft, at GitHub-tokenet har
  læseadgang til det ønskede repository, og at MCP **Test**-knappen i
  **Customize** viser GitHub-værktøjer.
- **Slack kan læse kanaler, men kan ikke poste:** inviter Slack-appen til den
  ønskede kanal, og bekræft, at botten har `chat:write`.
- **Automationen viser for mange Slack-kanaler:** brug et Slack-kanal-ID, og
  angiv `SLACK_CHANNEL_IDS` på Slack MCP-serveren under **Customize**.
- **Automationskørslen fejler eller overskrider konteksten:** bekræft, at Lemonade blev startet
  med `ctx_size=65536`, bekræft, at OpenHands LLM'en har `custom_tokenizer` angivet,
  og brug et eksplicit repository med GitHub-resultatsæt begrænset til 3 til 5
  elementer. Hvis din Agent Canvas-build eksponerer condenser-indstillinger, skal du sætte condenserens
  maksimale antal tokens under Lemonades kontekstvindue.

## Næste skridt

- Tilføj et ugentligt sammendrag kun for udgivelser.
- Tilføj en GitHub-hændelsesudløst automation for hurtigere PR- eller push-advarsler.
- Send det samme sammendrag videre til Notion, Linear eller et andet MCP-baseret værktøj.

## Ressourcer

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)
- [OpenHands extensions-repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servere](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-pakke](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)