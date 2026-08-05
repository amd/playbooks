<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Översikt

Utvecklare lägger mycket tid på små återkommande arbetsflöden: granska
märkta pull requests, svara på GitHub-kommentarer, sortera nya ärenden,
omvandla Slack-trådar till standupanteckningar eller uppföljningar av
incidenter, samt hålla koll på release- eller forskningssignaler. Varje
arbetsflöde är bekant, men det kräver ändå ett omdöme: samla in rätt
kontext, avgöra vad som är viktigt och publicera en tydlig uppdatering där
teamet redan arbetar.

[OpenHands-automationer](https://docs.openhands.dev/openhands/usage/automations/overview)
omvandlar dessa arbetsflöden till schemalagda eller händelseutlösta
agentkonversationer: körningar där en AI-programvaruagent kan läsa kontext,
anropa verktyg och skapa en uppdatering. De delade automationsmallarna i
OpenHands utökningskatalog följer detta mönster för granskning av GitHub pull
requests, övervakning av repositorier, triage av Linear-ärenden,
incidentgenomgångar, Slack-standupsammanfattningar och forskningsöversikter:
en automation väcks, använder konfigurerade integrationer som GitHub eller
Slack för att hämta kontext, resonerar kring den kontexten med en stor
språkmodell (LLM) och skriver tillbaka ett resultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) är den lokala
kontrollplattformen för att bygga och testa dessa automationer. I den här
spelboken kör den en OpenHands Agent Server, backend-processen som utför
agentkonversationer, och kopplar agenten till externa tjänster som GitHub och
Slack.

För att hålla arbetsflödet på ditt AMD-system kommunicerar agenten med en
lokal modell som serveras av Lemonade Server. Lemonade exponerar den modellen
via ett OpenAI-kompatibelt API, så Agent Canvas kan konfigurera den som en
fjärransluten OpenAI-liknande slutpunkt medan modellen, prompten och
arbetsflödets kontext förblir lokala.

I den här spelboken bygger du en konkret automation: en schemalagd
GitHub-till-Slack-utvecklingssammanfattning. Den använder GitHub för att
granska den senaste repositorieaktiviteten, Slack för att publicera
sammanfattningen, Agent Canvas API-anrop för att konfigurera och testa
automationen, och Lemonade för att köra LLM:en lokalt.

![Arkitekturdiagram som visar GitHub MCP, OpenHands-automation, Lemonade Server och Slack MCP](assets/00-architecture-overview.png)

## Vad du kommer att lära dig

- Hur du startar Lemonade Server och verifierar att en lokal modell svarar på
  chattförfrågningar
- Hur du startar Agent Canvas och pekar dess Agent Server mot en lokal LLM
- Hur du installerar GitHub- och Slack-servrar för Model Context Protocol (MCP)
  via Agent Server-API:et
- Hur du skapar och startar en schemalagd OpenHands-automation som publicerar
  en utvecklingssammanfattning till Slack
- Hur du felsöker de vanligaste felen kring lokala modeller och automationer

## Grundläggande begrepp

| Begrepp | Vad det är | Var det passar in i den här spelboken |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform byggd för AMD-hårdvara som exponerar ett OpenAI-kompatibelt API. Din data lämnar aldrig din dator. | Kör modellen som driver agenten. |
| OpenHands Agent Server | Backend-processen som utför OpenHands-agentkonversationer. | Är värd för agenten, dess LLM-profil och dess MCP-servrar. |
| Agent Canvas | Den lokala kontrollplattformen för OpenHands som kör Agent Server och ett användargränssnitt för att granska agentkörningar. | Startar backendtjänsterna och tillhandahåller API:et du anropar. |
| MCP-server | En Model Context Protocol-server som ger en agent verktyg för en extern tjänst som GitHub eller Slack. | Låter agenten läsa GitHub och skriva till Slack. |
| OpenHands-automation | En schemalagd eller händelseutlöst agentkonversation som hämtar kontext, resonerar kring den och skriver ett resultat någonstans. | GitHub-till-Slack-sammanfattningen du bygger här. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodningsagentarbetsflöden gynnas av en större modell och ett större
> kontextfönster. Använd minst 32 GB systemminne, och föredra 64 GB eller mer
> för större GGUF-modeller.
<!-- @device:end -->

## Förkrav

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du behöver:

- Lemonade Server installerad genom att följa den vanliga
  [Lemonade-installationsguiden](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 eller senare samt `npm`, som används för att installera den
  publicerade Agent Canvas-CLI:n och köra MCP-servrar med `npx`.
- Ett nyligen publicerat `@openhands/agent-canvas`-paket med
  schemastyrda agentinställningar, `LLMSummarizingCondenserSettings.max_tokens`,
  och stöd för LLM `custom_tokenizer`.
- Python-paketet `transformers` tillgängligt i Agent Server-miljön.
  Det krävs för tokenräkning av chattmallar när `custom_tokenizer` är
  inställt.
- En GitHub-token med läsbehörighet till repositoriet du vill sammanfatta.
- En Slack-bot-token (`xoxb-...`) med `chat:write` och läsbehörighet för
  kanaler.
- Ett Slack-team-ID (`T...`).
- Ett Slack-kanal-ID (`C...`) där sammanfattningen ska publiceras.

Bjud in Slack-appen till målkanalen innan du testar automationen.

## Variabler som används i den här spelboken

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

Följande värden anges i Agent Canvas-användargränssnittet i senare steg. Ange
dem här så att du kan kopiera in dem:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Använd ett explicit `owner/repo`-värde för `GITHUB_REPO_FILTER`. Breda
jokertecken för organisationer kan returnera för mycket MCP-kontext för
lokala modeller.

## 1. Starta Lemonade Server

Starta modellen från Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade exponerar ett OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```

Valfritt: om Agent Canvas eller automationskörningen inte finns på samma
maskin, publicera Lemonade-slutpunkten via en säker tunnel och använd
HTTPS-URL:en som LLM-basadress:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifiera den lokala modellen

Bekräfta att Lemonade kan servera den valda modellen:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Skicka sedan en liten chattförfrågan:

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

Om detta returnerar en `choices`-array är Lemonade redo för Agent Canvas.
## 3. Starta Agent Canvas

Installera det publicerade Agent Canvas-paketet och starta hela stacken:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Om den globala npm-installationen misslyckas med ett behörighetsfel, se
felsökningsposten om npm-behörigheter nedan.

Som standard startar Agent Canvas på `http://localhost:8000`. Öppna den
webbadressen i din webbläsare. Standardbackend lokalt bör visas som frisk
(healthy) på startskärmen.

Kommandot `agent-canvas` startar agentservern, automationsbackenden och
webbfrontenden tillsammans. Du behöver bara detta enda kommando för att köra
OpenHands lokalt. Resten av denna spelbok konfigurerar allt via
Agent Canvas-gränssnittet i din webbläsare.

## 4. Konfigurera den lokala LLM:n i gränssnittet

Vid första start öppnar Agent Canvas ett introduktionsflöde. I det flödet:

1. Behåll **OpenHands** vald som agent och klicka på **Next**.
2. Under **Set up your LLM**, välj **Advanced**.
3. Behåll **Authentication** inställd på **API key**.
4. Ställ in **Custom Model** till värdet för `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ställ in **Base URL** till `http://127.0.0.1:13305/api/v1`.
6. För **API Key**, ange en godtycklig icke-tom platshållare, t.ex.
   `lemonade-local`. Lemonade kräver ingen riktig nyckel, men OpenHands-klienten
   behöver ett värde att skicka.

Anslutningsfälten bör se ut så här. API-nyckelfältet maskeras av
gränssnittet.

![Agent Canvas första körningens LLM Advanced-inställningar med Lemonade-modellen och lokal bas-URL](assets/01-llm-advanced-settings.png)

Välj sedan **All** och ställ in de extra fälten för lokal modell:

1. Bläddra till **Custom Tokenizer** och ställ in den till `Qwen/Qwen3.6-35B-A3B`.
2. Bläddra till **LiteLLM Extra Body** och ställ in det till
   `{"enable_thinking": true}`.
3. Klicka på **Next**.

![Agent Canvas första körningens LLM All-flik med den anpassade Qwen-tokeniseraren](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas första körningens LLM All-flik med konfigurerad LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM-inställningarna bör visa:

| Fält | Värde |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefixet `openai/` talar om för LiteLLM att använda OpenAI-kompatibel
förfrågningsformatering mot Lemonade-slutpunkten. Den anpassade tokeniseraren
är den ursprungliga Hugging Face-tokeniseraren för GGUF-modellen; den låter
OpenHands räkna samma chat-mall-tokens som den lokala modellservern ser. Det
nuvarande formuläret för första körningens LLM visar inte
kondensorinställningar (condenser settings). Om din Agent Canvas-version
senare exponerar kondensorinställningar under **Settings > LLM**, använd
`llm_summarizing` och ställ in max tokens under Lemonade-kontextfönstret,
till exempel `56000`.

## 5. Installera GitHub- och Slack-MCP-servrar

I Agent Canvas-gränssnittet, öppna **Customize** (eller **Settings > MCP**)
för att lägga till MCP-servrarna som ger agenten verktyg för GitHub och
Slack. Tokenvärden skickas endast till din lokala agentserver (Agent Server)
och sparas som krypterade inställningar.

### GitHub MCP-server

Lägg till en ny MCP-server med dessa inställningar:

| Fält | Värde |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = din GitHub-token |

Använd en GitHub-token med läsbehörighet till repositoryt du vill sammanfatta.

### Slack MCP-server

Lägg till en andra MCP-server med dessa inställningar:

| Fält | Värde |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ditt digest-kanal-ID |

Ställ in `SLACK_CHANNEL_IDS` till digest-kanalens ID (samma värde som
`SLACK_DIGEST_CHANNEL`) så att agenten inte behöver bläddra igenom varje
Slack-kanal.

När du har lagt till båda servrarna, använd **Test**-knappen på var och en
för att bekräfta att den ansluter och annonserar verktyg. GitHub-servern bör
lista GitHub-verktyg, och Slack-servern bör lista Slack-verktyg.

![Agent Canvas MCP-sida med GitHub- och Slack-servrar installerade](assets/04-mcp-servers-installed.png)

## 6. Skapa digest-automationen

I Agent Canvas-gränssnittet, öppna sidan **Automations** och skapa en ny
automation:

1. Välj **Create automation** och välj typen **Prompt preset**.
2. Ställ in **Name** till `GitHub Development Digest to Slack`.
3. Ställ in **Prompt** till följande text, och ersätt platshållarna för
   repository och kanal med dina värden:

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

4. Ställ in **Trigger** till **Cron** med schemat `0 9 * * 1-5` (kl. 9 på
   vardagar) och ställ in **Timezone** till din tidszon, till exempel
   `America/New_York`.
5. Ställ in **Timeout** till `900` sekunder.
6. Spara automationen.

Automationens detaljsida visar den nya automationen med dess cron-utlösare
och den genererade prompt-preset-ingångspunkten.

![Agent Canvas automationens detaljsida efter skapande](assets/05-automation-created.png)
## 7. Testa automatiseringen

Från automatiseringens detaljsida i Agent Canvas-gränssnittet:

1. Klicka på **Run now** (eller **Dispatch**) för att köra automatiseringen en gång direkt.
2. Bevaka körlistan på samma sida. Den senaste körningen bör övergå till
   `COMPLETED`.
3. Öppna din Slack-målkanal. Den bör innehålla det genererade sammandraget.

Du behöver inte vänta på att cron-schemat ska utlösas—**Run now** startar en
körning på begäran så att du kan bekräfta att prompten, MCP-anslutningarna och Slack-publiceringen
alla fungerar innan du förlitar dig på schemat.

![Agent Canvas-automatisering slutförd](assets/06-automation-run-completed.png)

![Slack-kanal som visar det genererade OpenHands-sammandraget](assets/07-slackbot-message.png)

## Felsökning

- **Lemonade är nere:** starta om det med
  kommandot `lemonade run "${LEMONADE_MODEL}"` från steg 1, och kör sedan
  hälsokontrollen igen.
- **`npm install -g` misslyckas med ett behörighetsfel:** på Linux eller WSL,
  konfigurera en användarägd global npm-katalog, lägg till den i din skals startfil,
  och installera sedan Agent Canvas igen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Om du använder `zsh`, lägg till samma `export PATH=...`-rad i `~/.zshrc` istället
  för `~/.bashrc`.
- **Agent Canvas avvisar LLM-inställningarna efter att `custom_tokenizer` har angetts:**
  installera `transformers` i Agent Server Python-miljön, starta om Agent
  Canvas om det behövs, och försök spara LLM-inställningarna igen. OpenHands kräver
  Transformers för att ladda tokenizerns chattmall när `custom_tokenizer` är
  angivet.
- **Agent Canvas kan inte nå Lemonade:** kontrollera
  `curl -fsS "${LEMONADE_BASE_URL}/health"` och bekräfta att bas-URL:en som angetts i
  formuläret för första användningens LLM eller **Settings > LLM** matchar den körande lokala
  slutpunkten eller HTTPS-tunneln.
- **LLM-inställningarna sparades inte:** se till att du klickade på **Next** efter
  att ha angett värdena. Öppna **Settings > LLM** igen för att bekräfta att värdena
  har sparats.
- **GitHub MCP kan inte se privata repositories:** bekräfta att GitHub-token har
  läsbehörighet till målrepositoryn och att MCP-knappen **Test** i
  **Customize** visar GitHub-verktyg.
- **Slack kan läsa kanaler men kan inte publicera:** bjud in Slack-appen till
  målkanalen och bekräfta att boten har `chat:write`.
- **Automatiseringen listar för många Slack-kanaler:** använd ett Slack-kanal-ID och
  ange `SLACK_CHANNEL_IDS` på Slack MCP-servern i **Customize**.
- **Automatiseringskörningen misslyckas eller överskrider kontexten:** bekräfta att Lemonade startades
  med `ctx_size=65536`, bekräfta att OpenHands LLM har `custom_tokenizer` angivet,
  och använd en explicit repository med GitHub-resultatuppsättningar begränsade till 3 till 5
  poster. Om din Agent Canvas-version exponerar condenser-inställningar, ställ in condenserns
  maximala antal tokens under Lemonades kontextfönster.

## Nästa steg

- Lägg till ett veckovis sammandrag enbart för utgåvor.
- Lägg till en GitHub-händelseutlöst automatisering för snabbare PR- eller push-aviseringar.
- Dirigera samma sammandrag till Notion, Linear eller ett annat MCP-baserat verktyg.

## Resurser

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)
- [OpenHands-tilläggsrepository](https://github.com/OpenHands/extensions)
- [Model Context Protocol-servrar](https://github.com/modelcontextprotocol/servers)
- [Slack MCP-paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)