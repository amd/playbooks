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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) è un agente software AI
in grado di scrivere codice, eseguire comandi, navigare sul web e modificare file in un vero e proprio
workspace. Invece di copiare suggerimenti da una finestra di chat, si indirizza
l'agente verso una cartella di progetto e lo si lascia lavorare: implementare una funzionalità, correggere
un bug, scrivere test o spiegare una codebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) è l'interfaccia utente
browser consigliata per eseguire OpenHands. Un unico comando `agent-canvas` avvia il
server dell'agente, il backend di automazione e il frontend web insieme, così è possibile
condurre una conversazione con l'agente dal browser.

Per mantenere tutto sul proprio sistema AMD, l'agente comunica con un modello locale servito
da Lemonade Server. Lemonade espone quel modello tramite un'API compatibile con OpenAI,
così Agent Canvas può configurarlo come qualsiasi altro endpoint in stile OpenAI
mentre il modello, il codice e il contesto della conversazione rimangono tutti sulla
propria macchina.

In questo playbook, avvierai un modello locale, lancerai Agent Canvas, lo punterai
verso quel modello ed eseguirai il tuo primo compito di programmazione su una cartella di progetto reale.

## Cosa imparerai

- Come avviare Lemonade Server e verificare che un modello locale risponda alle richieste di chat
- Come installare e lanciare Agent Canvas dal pacchetto npm
- Come configurare Agent Canvas per utilizzare un modello Lemonade locale come LLM
- Come avviare una conversazione OpenHands e osservare l'agente modificare file ed eseguire
  comandi in un workspace
- Come rivedere le modifiche apportate dall'agente e guidarlo con messaggi di follow-up

## Concetti fondamentali

| Concetto | Cos'è | Come si inserisce in questo playbook |
| --- | --- | --- |
| Lemonade Server | Una piattaforma di serving LLM locale costruita per hardware AMD che espone un'API compatibile con OpenAI. I tuoi dati non lasciano mai la tua macchina. | Esegue il modello che alimenta l'agente. |
| OpenHands | Un agente software AI che legge e modifica file, esegue comandi shell e naviga sul web all'interno di un workspace. | L'agente che guidi dalla chat. |
| Agent Canvas | L'interfaccia utente browser e il backend che esegue le conversazioni OpenHands e mostra le chiamate agli strumenti e le modifiche ai file. | Avvia lo stack e ospita la tua conversazione. |
| Workspace | La cartella di progetto che l'agente è autorizzato a leggere e modificare. | Il target delle modifiche e dei comandi dell'agente. |

<!-- @device:stx,krk -->
> [!NOTE]
> I flussi di lavoro degli agenti di programmazione beneficiano di un modello e di una finestra di contesto più ampi. Utilizza
> almeno 32 GB di memoria di sistema e preferisci 64 GB o più per modelli GGUF più grandi.
<!-- @device:end -->

## Prerequisiti

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Sono necessari:

- Lemonade Server installato e in grado di servire il modello riportato di seguito.
- Node.js 22.12 o versione successiva e `npm` (utilizzati dalla CLI `agent-canvas`).
- `uv`, il gestore di pacchetti Python utilizzato da Agent Canvas per gestire l'ambiente del
  server dell'agente. Se il sistema non lo possiede già, installalo dalla
  [guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/)
  prima di lanciare Agent Canvas.
- Una cartella di progetto su cui lavorare. Può essere qualsiasi repository git locale o directory
  di codice su cui vuoi far lavorare l'agente.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Avviare Lemonade Server

Avvia il modello dalla CLI di Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade espone un'API compatibile con OpenAI all'indirizzo:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Verificare il modello locale

Conferma che Lemonade possa servire il modello selezionato:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Quindi invia una piccola richiesta di chat:

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

Se questo restituisce un array `choices`, Lemonade è pronto per Agent Canvas.

## 3. Installare e lanciare Agent Canvas

Installa globalmente il pacchetto Agent Canvas pubblicato:

```bash
npm install -g @openhands/agent-canvas
```

Quindi avvia l'intero stack da un terminale:

```bash
agent-canvas
```

Per impostazione predefinita, Agent Canvas si avvia su `http://localhost:8000`. Apri quell'URL nel
tuo browser. Se la porta 8000 è già in uso, passa `--port` (o `-p`) quando
lanci Agent Canvas:

```bash
agent-canvas --port 3000
```

Lo stesso comando funziona in PowerShell su Windows. Quindi apri
`http://localhost:3000` al posto dell'altro URL. Il backend locale predefinito dovrebbe risultare
integro nella schermata iniziale.

Il comando `agent-canvas` avvia il server dell'agente, il backend di automazione e
il frontend web insieme. Ti serve solo questo unico comando per eseguire OpenHands
localmente.

## 4. Configurare l'LLM locale

Al primo avvio, Agent Canvas apre un flusso di onboarding. In quel flusso:

1. Mantieni **OpenHands** selezionato come agente e fai clic su **Next**.
2. In **Set up your LLM**, seleziona **Advanced**.
3. Mantieni **Authentication** impostato su **API key**.
4. Imposta **Custom Model** su `openai/Qwen3.6-35B-A3B-GGUF`.
5. Imposta **Base URL** su `http://127.0.0.1:13305/api/v1`.
6. Per **API Key**, inserisci un valore segnaposto non vuoto come `lemonade-local`.
   Lemonade non richiede una chiave reale, ma il client OpenHands necessita di un valore
   da inviare.
7. Fai clic su **Next**.

Le impostazioni Advanced completate dovrebbero avere questo aspetto. Il campo della chiave API è
mascherato dall'interfaccia utente.

![Impostazioni Advanced LLM al primo utilizzo di Agent Canvas con il modello Lemonade e l'URL di base locale](assets/01-llm-advanced-settings.png)

Agent Canvas salva questi valori come profilo LLM. Se la tua versione ti chiede di
assegnare un nome a quel profilo, usa un nome senza spazi come `lemonade-local`. Se in seguito cambi
modello, apri **Settings > LLM** e aggiorna gli stessi campi Advanced. Puoi
passare da un profilo salvato all'altro dall'input della chat con il comando `/model`.

## 5. Aprire un workspace

L'agente può leggere e modificare i file solo all'interno di un workspace che scegli tu. Prima di
avviare un compito, indirizza Agent Canvas verso la tua cartella di progetto:

1. Dalla schermata iniziale, scegli **Open Workspace**.
2. Seleziona la cartella che contiene il tuo progetto (ad esempio, un repository git
   su cui vuoi far lavorare l'agente).
3. Avvia una nuova conversazione in quel workspace.

Tutto ciò che l'agente fa — leggere file, eseguire comandi, modificare codice — è
limitato a quel workspace.

![Home di Agent Canvas dopo l'onboarding](assets/02-agent-canvas-home.png)
## 6. Esegui il tuo primo task di coding

Con lo workspace aperto e l'LLM locale selezionato, digita un task concreto nella chat. Un buon primo task è piccolo e verificabile, ad esempio:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Osserva la timeline della conversazione. OpenHands eseguirà queste azioni:

- Leggere il workspace per comprenderne la struttura.
- Creare `hello.py` con la funzione richiesta e il blocco di test.
- Facoltativamente, eseguire `python3 hello.py` per verificare l'output.
- Riportare in chat quanto fatto e l'eventuale output dei comandi.

Dovresti vedere apparire il nuovo file nel workspace, e il messaggio finale dell'agente dovrebbe descrivere la modifica apportata. Questo è il momento decisivo: l'agente ha scritto ed eseguito codice reale nella cartella del tuo progetto.

## 7. Rivedi e guida l'agente

Dopo che l'agente ha completato un passaggio, rivedi il suo lavoro prima di accettare quello successivo:

- **Modifiche ai file**: usa il browser dei file del workspace o la vista diff dell'agente per vedere esattamente cosa è stato aggiunto, modificato o eliminato.
- **Output dei comandi**: espandi qualsiasi comando eseguito dall'agente per vedere stdout, stderr ed exit code.
- **Follow-up**: se il risultato non è quello desiderato, rispondi nella stessa conversazione con una correzione. L'agente mantiene il contesto precedente e itera sugli stessi file.

Ad esempio, se il test non ha stampato il saluto atteso, rispondi:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

L'agente rileggerà il file, eseguirà il comando, diagnosticherà il problema e modificherà nuovamente il file, tutto nella stessa conversazione.

## Risoluzione dei problemi

- **`agent-canvas` non è nel PATH:** reinstalla con
  `npm install -g @openhands/agent-canvas` e verifica che la directory dei binari globali di npm sia nel tuo PATH. Su Windows, esegui `npm config get prefix`; la directory restituita, spesso `%APPDATA%\npm` o `%USERPROFILE%\.npm-global`, deve trovarsi nel PATH utente prima che `agent-canvas` possa essere avviato da un nuovo terminale.
- **`npm install -g` fallisce con un errore di permessi:** configura una directory globale npm di proprietà dell'utente, poi riapri il terminale e installa nuovamente Agent Canvas.

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

  Per rendere permanente la modifica al PATH di Windows, aggiungi `%USERPROFILE%\.npm-global` al tuo PATH utente da **Settings > System > About > Advanced system settings > Environment Variables**, e apri un nuovo terminale.
  <!-- @os:end -->
- **L'interfaccia si carica ma il backend risulta unhealthy:** attendi qualche secondo affinché il server dell'agente completi l'avvio, quindi ricarica la pagina. Se rimane unhealthy, riavvia `agent-canvas` e controlla l'output del terminale per eventuali errori.
- **Le richieste di chat a Lemonade falliscono con un errore di connessione:** verifica che `curl -fsS "http://127.0.0.1:13305/api/v1/health"` abbia esito positivo e che Lemonade stia ancora servendo il modello con `lemonade status`.
- **L'agente restituisce un errore relativo alla lunghezza del contesto o al limite di token:** riavvia Lemonade con un `ctx_size` maggiore (ad esempio `ctx_size=65536`), e avvia una nuova conversazione in modo che l'agente non porti con sé una cronologia eccessivamente grande.
- **L'agente produce modifiche di scarsa qualità o incomplete:** passa a un modello più grande in Lemonade, oppure assegna all'agente un task più piccolo e concreto e lascialo terminare prima di richiedere la modifica successiva.
- **`uv` manca:** installalo da
  [la guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas usa `uv` per gestire l'ambiente Python del server dell'agente.

## Prossimi passi

- Prova un task più grande nello stesso workspace, come aggiungere un file di unit test o correggere un bug noto, e rivedi il diff dell'agente prima di mantenere la modifica.
- Collega un server MCP come GitHub o Slack in **Customize** in modo che l'agente possa leggere issue o pubblicare aggiornamenti mentre lavora.
- Salva diversi profili LLM (un modello piccolo e veloce e un modello più grande e potente) e passa dall'uno all'altro con `/model` durante la conversazione.
- Passa a [automazioni di OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) per trasformare i cicli di sviluppo ricorrenti in esecuzioni dell'agente pianificate o attivate da eventi.

## Risorse

- [Documentazione di OpenHands](https://docs.openhands.dev/)
- [Panoramica di Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configurazione di Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profili LLM e configurazione dei modelli](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentazione di Lemonade Server](https://lemonade-server.ai/docs)