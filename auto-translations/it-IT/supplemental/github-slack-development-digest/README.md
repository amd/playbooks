<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Panoramica

Gli sviluppatori dedicano molto tempo a piccoli cicli ricorrenti: revisionare pull request etichettate, rispondere a commenti GitHub, gestire il triage di nuovi issue, trasformare thread Slack in note di standup o follow-up di incidenti, e monitorare segnali di release o di ricerca. Ogni ciclo è familiare, ma richiede comunque discernimento: raccogliere il contesto giusto, decidere cosa conta e pubblicare un aggiornamento chiaro nel luogo in cui il team già lavora.

[Le automazioni OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
trasformano questi cicli in conversazioni agentiche pianificate o attivate da eventi: esecuzioni in cui un agente software AI può leggere il contesto, richiamare strumenti e produrre un aggiornamento. I template di automazione condivisi nel catalogo delle estensioni OpenHands seguono questo pattern per la revisione delle pull request GitHub, il monitoraggio dei repository, il triage degli issue Linear, i retrospettive sugli incidenti, i digest di standup Slack e i brief di ricerca: un'automazione si attiva, utilizza integrazioni configurate come GitHub o Slack per recuperare il contesto, ragiona su tale contesto con un modello linguistico di grandi dimensioni (LLM) e scrive un risultato.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) è il piano di controllo locale per creare e testare queste automazioni. In questo playbook esegue un OpenHands Agent Server, il processo back-end che esegue le conversazioni agentiche, e collega l'agente a servizi esterni come GitHub e Slack.

Per mantenere il workflow sul tuo sistema AMD, l'agente comunica con un modello locale servito da Lemonade Server. Lemonade espone tale modello tramite un'API compatibile con OpenAI, così Agent Canvas può configurarlo come un endpoint remoto in stile OpenAI, mentre il modello, il prompt e il contesto del workflow rimangono locali.

In questo playbook creerai un'automazione concreta: un digest di sviluppo programmato da GitHub a Slack. Utilizza GitHub per ispezionare l'attività recente del repository, Slack per pubblicare il digest, chiamate API di Agent Canvas per configurare e testare l'automazione, e Lemonade per eseguire l'LLM localmente.

![Diagramma dell'architettura che mostra GitHub MCP, l'automazione OpenHands, Lemonade Server e Slack MCP](assets/00-architecture-overview.png)

## Cosa Imparerai

- Come avviare Lemonade Server e verificare che un modello locale risponda alle richieste di chat
- Come avviare Agent Canvas e puntare il suo Agent Server verso un LLM locale
- Come installare i server GitHub e Slack Model Context Protocol (MCP) tramite l'API dell'Agent Server
- Come creare e distribuire un'automazione OpenHands programmata che pubblica un digest di sviluppo su Slack
- Come risolvere i problemi più comuni relativi al modello locale e all'automazione

## Concetti Fondamentali

| Concetto | Cos'è | Dove si inserisce in questo playbook |
| --- | --- | --- |
| Lemonade Server | Una piattaforma di serving LLM locale progettata per hardware AMD che espone un'API compatibile con OpenAI. I tuoi dati non lasciano mai la tua macchina. | Esegue il modello che alimenta l'agente. |
| OpenHands Agent Server | Il processo back-end che esegue le conversazioni agentiche di OpenHands. | Ospita l'agente, il suo profilo LLM e i suoi server MCP. |
| Agent Canvas | Il piano di controllo locale per OpenHands che esegue Agent Server e un'interfaccia utente per ispezionare le esecuzioni dell'agente. | Avvia i back-end e fornisce l'API che richiami. |
| Server MCP | Un server Model Context Protocol che fornisce a un agente strumenti per un servizio esterno come GitHub o Slack. | Consente all'agente di leggere da GitHub e scrivere su Slack. |
| Automazione OpenHands | Una conversazione agentica pianificata o attivata da eventi che recupera il contesto, ragiona su di esso e scrive un risultato da qualche parte. | Il digest da GitHub a Slack che crei qui. |

<!-- @device:stx,krk -->
> [!NOTE]
> I workflow degli agenti di coding beneficiano di un modello e di una finestra di contesto più ampi. Usa almeno 32 GB di memoria di sistema, e preferisci 64 GB o più per modelli GGUF più grandi.
<!-- @device:end -->

## Prerequisiti

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Ti occorrono:

- Lemonade Server installato seguendo la
  [guida di installazione standard di Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 o versione successiva e `npm`, utilizzati per installare la CLI pubblicata di Agent Canvas ed eseguire server MCP con `npx`.
- Un pacchetto `@openhands/agent-canvas` recente e pubblicato con
  impostazioni agente basate su schema, `LLMSummarizingCondenserSettings.max_tokens`,
  e supporto LLM `custom_tokenizer`.
- Il pacchetto Python `transformers` disponibile nell'ambiente dell'Agent Server.
  È necessario per il conteggio dei token del chat-template quando `custom_tokenizer` è
  impostato.
- Un token GitHub con accesso in lettura al repository che vuoi riassumere.
- Un token bot Slack (`xoxb-...`) con accesso in scrittura tramite `chat:write` e accesso in lettura al canale.
- Un ID team Slack (`T...`).
- Un ID canale Slack (`C...`) in cui deve essere pubblicato il digest.

Invita l'app Slack nel canale di destinazione prima di testare l'automazione.

## Variabili Utilizzate in Questo Playbook

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

I seguenti valori vengono inseriti nell'interfaccia utente di Agent Canvas nei passaggi successivi. Impostali qui in modo da poterli copiare in seguito:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Usa un valore esplicito `owner/repo` per `GITHUB_REPO_FILTER`. I wildcard ampi a livello di organizzazione possono restituire troppo contesto MCP per i modelli locali.

## 1. Avvia Lemonade Server

Avvia il modello dalla CLI di Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade espone un'API compatibile con OpenAI all'indirizzo:

```text
http://127.0.0.1:13305/api/v1
```

Opzionale: se Agent Canvas o l'esecutore dell'automazione non si trovano sulla stessa macchina, pubblica l'endpoint Lemonade tramite un tunnel sicuro e utilizza l'URL HTTPS come URL di base dell'LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifica il Modello Locale

Conferma che Lemonade possa servire il modello selezionato:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Quindi invia una piccola richiesta di chat:

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

Se questo restituisce un array `choices`, Lemonade è pronto per Agent Canvas.
## 3. Avvia Agent Canvas

Installa il pacchetto Agent Canvas pubblicato e avvia lo stack completo:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se l'installazione globale di npm fallisce con un errore di permessi, consulta
la voce sulla risoluzione dei problemi di permessi npm riportata di seguito.

Per impostazione predefinita, Agent Canvas si avvia su `http://localhost:8000`.
Apri quell'URL nel tuo browser. Il backend locale predefinito dovrebbe apparire
come sano (healthy) nella schermata principale.

Il comando `agent-canvas` avvia insieme il server dell'agente, il backend di
automazione e il frontend web. È necessario solo questo comando per eseguire
OpenHands localmente. Il resto di questa guida configura tutto tramite
l'interfaccia utente di Agent Canvas nel tuo browser.

## 4. Configura l'LLM locale nell'interfaccia utente

Al primo avvio, Agent Canvas apre un flusso di onboarding. In questo flusso:

1. Mantieni **OpenHands** selezionato come agente e fai clic su **Next**.
2. In **Set up your LLM**, seleziona **Advanced**.
3. Mantieni **Authentication** impostato su **API key**.
4. Imposta **Custom Model** sul valore di `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Imposta **Base URL** su `http://127.0.0.1:13305/api/v1`.
6. Per **API Key**, inserisci un valore segnaposto non vuoto come
   `lemonade-local`. Lemonade non richiede una chiave reale, ma il client
   OpenHands necessita di un valore da inviare.

I campi di connessione dovrebbero apparire così. Il campo della chiave API è
mascherato dall'interfaccia utente.

![Impostazioni avanzate LLM di Agent Canvas al primo utilizzo con il modello Lemonade e l'URL di base locale](assets/01-llm-advanced-settings.png)

Quindi seleziona **All** e imposta i campi aggiuntivi per il modello locale:

1. Scorri fino a **Custom Tokenizer** e impostalo su `Qwen/Qwen3.6-35B-A3B`.
2. Scorri fino a **LiteLLM Extra Body** e impostalo su
   `{"enable_thinking": true}`.
3. Fai clic su **Next**.

![Scheda All di Agent Canvas LLM al primo utilizzo con il tokenizer personalizzato Qwen](assets/02-llm-all-tokenizer-settings.png)

![Scheda All di Agent Canvas LLM al primo utilizzo con il corpo extra LiteLLM configurato](assets/03-llm-all-extra-body-settings.png)

Le impostazioni LLM dovrebbero mostrare:

| Campo | Valore |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Il prefisso `openai/` indica a LiteLLM di utilizzare la formattazione delle
richieste compatibile con OpenAI verso l'endpoint Lemonade. Il tokenizer
personalizzato è il tokenizer originale di Hugging Face per il modello GGUF;
consente a OpenHands di contare gli stessi token del chat-template visti dal
server del modello locale. L'attuale modulo LLM al primo utilizzo non mostra
le impostazioni del condenser. Se la tua build di Agent Canvas espone in
seguito le impostazioni del condenser in **Settings > LLM**, utilizza
`llm_summarizing` e imposta i token massimi al di sotto della finestra di
contesto di Lemonade, ad esempio `56000`.

## 5. Installa i server MCP di GitHub e Slack

Nell'interfaccia utente di Agent Canvas, apri **Customize** (o **Settings >
MCP**) per aggiungere i server MCP che forniscono all'agente gli strumenti per
GitHub e Slack. I valori dei token vengono inviati solo al tuo Agent Server
locale e vengono conservati come impostazioni crittografate.

### Server MCP di GitHub

Aggiungi un nuovo server MCP con queste impostazioni:

| Campo | Valore |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = il tuo token GitHub |

Utilizza un token GitHub con accesso in lettura al repository che vuoi
riassumere.

### Server MCP di Slack

Aggiungi un secondo server MCP con queste impostazioni:

| Campo | Valore |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = l'ID del tuo canale di digest |

Imposta `SLACK_CHANNEL_IDS` sull'ID del canale di digest (lo stesso valore di
`SLACK_DIGEST_CHANNEL`) in modo che l'agente non debba scorrere ogni canale
Slack.

Dopo aver aggiunto entrambi i server, usa il pulsante **Test** su ciascuno per
confermare che si connetta e pubblicizzi gli strumenti. Il server GitHub
dovrebbe elencare gli strumenti GitHub e il server Slack dovrebbe elencare gli
strumenti Slack.

![Pagina MCP di Agent Canvas con i server GitHub e Slack installati](assets/04-mcp-servers-installed.png)

## 6. Crea l'automazione del digest

Nell'interfaccia utente di Agent Canvas, apri la pagina **Automations** e crea
una nuova automazione:

1. Scegli **Create automation** e seleziona il tipo **Prompt preset**.
2. Imposta il **Name** su `GitHub Development Digest to Slack`.
3. Imposta il **Prompt** sul testo seguente, sostituendo i segnaposto del
   repository e del canale con i tuoi valori:

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

4. Imposta il **Trigger** su **Cron** con la pianificazione `0 9 * * 1-5`
   (ore 9 nei giorni feriali) e imposta il **Timezone** sul tuo fuso orario,
   ad esempio `America/New_York`.
5. Imposta il **Timeout** su `900` secondi.
6. Salva l'automazione.

La pagina dei dettagli dell'automazione mostra la nuova automazione con il suo
trigger cron e il punto di ingresso del prompt-preset generato.

![Dettaglio dell'automazione di Agent Canvas dopo la creazione](assets/05-automation-created.png)
## 7. Testare l'Automazione

Dalla pagina di dettaglio dell'automazione nell'interfaccia utente di Agent Canvas:

1. Fai clic su **Run now** (o **Dispatch**) per eseguire l'automazione una volta immediatamente.
2. Osserva l'elenco delle esecuzioni nella stessa pagina. L'ultima esecuzione dovrebbe passare allo stato
   `COMPLETED`.
3. Apri il tuo canale Slack di destinazione. Dovrebbe contenere il digest generato.

Non è necessario attendere che la pianificazione cron si attivi: **Run now** avvia
un'esecuzione su richiesta, così puoi verificare che il prompt, le connessioni MCP e la pubblicazione su Slack
funzionino tutti prima di affidarti alla pianificazione.

![Esecuzione dell'automazione di Agent Canvas completata con successo](assets/06-automation-run-completed.png)

![Canale Slack che mostra il digest OpenHands generato](assets/07-slackbot-message.png)

## Risoluzione dei problemi

- **Lemonade non è attivo:** riavvialo con il comando
  `lemonade run "${LEMONADE_MODEL}"` al passaggio 1, quindi riesegui il controllo
  dello stato.
- **`npm install -g` fallisce con un errore di autorizzazioni:** su Linux o WSL,
  configura una directory globale npm di proprietà dell'utente, aggiungila al file di
  avvio della shell, quindi installa di nuovo Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Se usi `zsh`, aggiungi la stessa riga `export PATH=...` a `~/.zshrc` invece
  che a `~/.bashrc`.
- **Agent Canvas rifiuta le impostazioni LLM dopo aver impostato `custom_tokenizer`:**
  installa `transformers` nell'ambiente Python di Agent Server, riavvia Agent
  Canvas se necessario, e riprova a salvare le impostazioni LLM. OpenHands richiede
  Transformers per caricare il template della chat del tokenizer quando `custom_tokenizer` è
  impostato.
- **Agent Canvas non riesce a raggiungere Lemonade:** verifica
  `curl -fsS "${LEMONADE_BASE_URL}/health"` e conferma che l'URL di base inserito nel
  modulo LLM al primo utilizzo o in **Settings > LLM** corrisponda all'endpoint
  locale in esecuzione o al tunnel HTTPS.
- **Le impostazioni LLM non sono state salvate:** assicurati di aver fatto clic su **Next** dopo
  aver inserito i valori. Riapri **Settings > LLM** per confermare che i valori
  siano stati salvati.
- **GitHub MCP non riesce a vedere i repository privati:** conferma che il token GitHub abbia
  accesso in lettura al repository di destinazione e che il pulsante **Test** di MCP in
  **Customize** mostri gli strumenti GitHub.
- **Slack riesce a leggere i canali ma non può pubblicare:** invita l'app Slack al
  canale di destinazione e conferma che il bot abbia `chat:write`.
- **L'automazione elenca troppi canali Slack:** usa un ID di canale Slack e
  imposta `SLACK_CHANNEL_IDS` sul server Slack MCP in **Customize**.
- **L'esecuzione dell'automazione fallisce o supera il contesto:** conferma che Lemonade sia stato avviato
  con `ctx_size=65536`, conferma che l'LLM di OpenHands abbia `custom_tokenizer` impostato,
  e usa un repository esplicito con i set di risultati GitHub limitati a 3-5
  elementi. Se la tua build di Agent Canvas espone le impostazioni del condenser, imposta il numero massimo di token del condenser al di sotto della finestra di contesto di Lemonade.

## Prossimi Passi

- Aggiungi un digest settimanale solo per le release.
- Aggiungi un'automazione attivata da eventi GitHub per avvisi più rapidi su PR o push.
- Indirizza lo stesso digest verso Notion, Linear o un altro strumento basato su MCP.

## Risorse

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentazione di Lemonade Server](https://lemonade-server.ai/docs)
- [Repository delle estensioni OpenHands](https://github.com/OpenHands/extensions)
- [Server Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacchetto Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)