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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) er en AI-programvareagent
som kan skrive kode, kjøre kommandoer, surfe på nettet og redigere filer i et
ekte arbeidsområde. I stedet for å kopiere forslag ut av et chattevindu, peker
du agenten mot en prosjektmappe og lar den gjøre jobben: implementere en
funksjon, fikse en feil, skrive tester eller forklare en kodebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er det anbefalte
nettleser-grensesnittet for å kjøre OpenHands. Én enkelt `agent-canvas`-kommando
starter agentserveren, automatiseringsbakenden og webfrontenden sammen, slik
at du kan drive en samtale med agenten fra nettleseren din.

For å holde alt på AMD-systemet ditt, snakker agenten med en lokal modell som
serveres av Lemonade Server. Lemonade eksponerer den modellen gjennom et
OpenAI-kompatibelt API, slik at Agent Canvas kan konfigurere det som et hvilket
som helst annet OpenAI-stil-endepunkt, mens modellen, koden din og
samtalekonteksten alle forblir på maskinen din.

I denne oppskriften starter du en lokal modell, starter Agent Canvas, peker den
mot den modellen og kjører din første kodeoppgave mot en ekte prosjektmappe.

## Hva du vil lære

- Hvordan du starter Lemonade Server og bekrefter at en lokal modell svarer på
  chatteforespørsler
- Hvordan du installerer og starter Agent Canvas fra npm-pakken
- Hvordan du konfigurerer Agent Canvas til å bruke en lokal Lemonade-modell som
  LLM
- Hvordan du starter en OpenHands-samtale og ser agenten redigere filer og
  kjøre kommandoer i et arbeidsområde
- Hvordan du gjennomgår hva agenten endret og styrer den med
  oppfølgingsmeldinger

## Kjernebegreper

| Begrep | Hva det er | Hvor det passer inn i denne oppskriften |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform bygget for AMD-maskinvare som eksponerer et OpenAI-kompatibelt API. Dataene dine forlater aldri maskinen din. | Kjører modellen som driver agenten. |
| OpenHands | En AI-programvareagent som leser og redigerer filer, kjører skallkommandoer og surfer på nettet i et arbeidsområde. | Agenten du driver fra chatten. |
| Agent Canvas | Nettleser-grensesnittet og bakenden som kjører OpenHands-samtaler og viser verktøykall og filendringer. | Starter stacken og er vert for samtalen din. |
| Arbeidsområde | Prosjektmappen agenten har lov til å lese og endre. | Målet for agentens redigeringer og kommandoer. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodeagent-arbeidsflyter drar nytte av en større modell og et større
> kontekstvindu. Bruk minst 32 GB systemminne, og foretrekk 64 GB eller mer for
> større GGUF-modeller.
<!-- @device:end -->

## Forutsetninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du trenger:

- Lemonade Server installert og i stand til å servere modellen nedenfor.
- Node.js 22.12 eller nyere og `npm` (brukes av `agent-canvas`-CLI-en).
- `uv`, Python-pakkebehandleren som Agent Canvas bruker til å administrere
  agentservermiljøet. Hvis systemet ditt ikke allerede har den, installer den
  fra [uv-installasjonsveiledningen](https://docs.astral.sh/uv/getting-started/installation/)
  før du starter Agent Canvas.
- En prosjektmappe å jobbe i. Dette kan være et hvilket som helst lokalt
  git-repositorium eller en kodekatalog du vil at agenten skal jobbe på.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Start Lemonade Server

Start modellen fra Lemonade-CLI-en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade eksponerer et OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Bekreft den lokale modellen

Bekreft at Lemonade kan servere den valgte modellen:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Send deretter en liten chatteforespørsel:

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

Hvis dette returnerer et `choices`-array, er Lemonade klar for Agent Canvas.

## 3. Installer og start Agent Canvas

Installer den publiserte Agent Canvas-pakken globalt:

```bash
npm install -g @openhands/agent-canvas
```

Start deretter hele stacken fra en terminal:

```bash
agent-canvas
```

Som standard starter Agent Canvas på `http://localhost:8000`. Åpne den URL-en
i nettleseren din. Hvis port 8000 allerede er i bruk, send med `--port` (eller
`-p`) når du starter Agent Canvas:

```bash
agent-canvas --port 3000
```

Den samme kommandoen fungerer i PowerShell på Windows. Åpne deretter
`http://localhost:3000` i stedet. Standard lokal backend bør vises som
"healthy" på hjemmeskjermen.

Kommandoen `agent-canvas` starter agentserveren, automatiseringsbakenden og
webfrontenden sammen. Du trenger bare denne ene kommandoen for å kjøre
OpenHands lokalt.

## 4. Konfigurer den lokale LLM-en

Ved første oppstart åpner Agent Canvas en onboarding-flyt. I den flyten:

1. Behold **OpenHands** valgt som agent, og klikk **Next**.
2. Under **Set up your LLM**, velg **Advanced**.
3. Behold **Authentication** satt til **API key**.
4. Sett **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sett **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, angi en hvilken som helst ikke-tom plassholder, for
   eksempel `lemonade-local`. Lemonade krever ikke en ekte nøkkel, men
   OpenHands-klienten trenger en verdi å sende.
7. Klikk **Next**.

De fullførte Advanced-innstillingene skal se slik ut. API-nøkkel-feltet er
maskert av brukergrensesnittet.

![Agent Canvas første gangs LLM Advanced-innstillinger med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Agent Canvas lagrer disse verdiene som en LLM-profil. Hvis versjonen din ber
deg om å navngi den profilen, bruk et navn uten mellomrom, for eksempel
`lemonade-local`. Hvis du bytter modell senere, åpne **Settings > LLM** og
oppdater de samme Advanced-feltene. Du kan bytte mellom lagrede profiler fra
chattefeltet med kommandoen `/model`.

## 5. Åpne et arbeidsområde

Agenten kan bare lese og endre filer inne i et arbeidsområde du velger. Før du
starter en oppgave, pek Agent Canvas mot prosjektmappen din:

1. Fra hjemmeskjermen, velg **Open Workspace**.
2. Velg mappen som inneholder prosjektet ditt (for eksempel et
   git-repositorium du vil at agenten skal jobbe på).
3. Start en ny samtale i det arbeidsområdet.

Alt agenten gjør – lese filer, kjøre kommandoer, redigere kode – er avgrenset
til det arbeidsområdet.

![Agent Canvas-hjemmeside etter onboarding](assets/02-agent-canvas-home.png)
## 6. Kjør din første kodeoppgave

Med arbeidsområdet åpent og den lokale LLM-en valgt, skriv inn en konkret oppgave i
chatten. En god første oppgave er liten og verifiserbar, for eksempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Følg med på samtaleforløpet. OpenHands vil:

- Lese arbeidsområdet for å forstå oppsettet.
- Opprette `hello.py` med den forespurte funksjonen og testblokken.
- Eventuelt kjøre `python3 hello.py` for å verifisere resultatet.
- Rapportere hva den gjorde og eventuelle kommandoresultater i chatten.

Du bør se den nye filen dukke opp i arbeidsområdet, og agentens siste
melding bør beskrive endringen den gjorde. Dette er lønnsomøyeblikket: agenten skrev og kjørte
ekte kode i prosjektmappen din.

## 7. Gjennomgå og styr agenten

Etter at agenten har fullført et steg, gjennomgå arbeidet før du godtar det neste:

- **Filendringer**: bruk arbeidsområdets filutforsker eller agentens diff-visning for å
  se nøyaktig hva som ble lagt til, endret eller slettet.
- **Kommandoresultat**: utvid enhver kommando agenten kjørte for å se stdout, stderr,
  og avslutningskoden.
- **Oppfølginger**: hvis resultatet ikke er det du ønsket, svar i samme
  samtale med en korrigering. Agenten beholder den tidligere konteksten og
  itererer på de samme filene.

Hvis testen for eksempel ikke skrev ut den forventede hilsenen, svar:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten vil lese filen på nytt, kjøre kommandoen, diagnostisere problemet, og redigere
filen igjen—alt i samme samtale.

## Feilsøking

- **`agent-canvas` er ikke på PATH:** installer på nytt med
  `npm install -g @openhands/agent-canvas` og bekreft at npms globale binærkatalog
  er på PATH-en din. På Windows, kjør `npm config get prefix`; katalogen som
  returneres, ofte `%APPDATA%\npm` eller `%USERPROFILE%\.npm-global`,
  må være på brukerens PATH før `agent-canvas` kan startes fra en ny
  terminal.
- **`npm install -g` feiler med en tillatelsesfeil:** sett opp en brukereid
  global npm-katalog, åpne deretter terminalen på nytt og installer Agent Canvas igjen.

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

  For å gjøre Windows PATH-endringen permanent, legg til `%USERPROFILE%\.npm-global` til
  brukerens PATH fra **Innstillinger > System > Om > Avanserte systeminnstillinger >
  Miljøvariabler**, og åpne en ny terminal.
  <!-- @os:end -->
- **UI-en lastes, men backend viser usunn status:** vent noen sekunder til
  agentserveren er ferdig med å starte, og oppdater deretter. Hvis den fortsatt er usunn, start
  `agent-canvas` på nytt og sjekk terminalutdataen for feil.
- **Lemonade chat-forespørsler feiler med en tilkoblingsfeil:** bekreft at
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lykkes og at
  Lemonade fortsatt serverer modellen med `lemonade status`.
- **Agenten feiler med en melding om kontekstlengde eller tokengrense:** start Lemonade
  på nytt med en større `ctx_size` (for eksempel `ctx_size=65536`), og start en
  ny samtale slik at agenten ikke bærer med seg en for stor historikk.
- **Agenten produserer redigeringer av lav kvalitet eller ufullstendige redigeringer:** bytt til en større
  modell i Lemonade, eller gi agenten en mindre, mer konkret oppgave og la den
  fullføre før du ber om neste endring.
- **`uv` mangler:** installer den fra
  [uv-installasjonsveiledningen](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas bruker `uv` til å administrere Python-miljøet for agentserveren.

## Neste steg

- Prøv en større oppgave i det samme arbeidsområdet, for eksempel å legge til en enhetstestfil eller
  fikse en kjent feil, og gjennomgå agentens diff før du beholder endringen.
- Koble til en MCP-server som GitHub eller Slack under **Customize** slik at
  agenten kan lese saker eller poste oppdateringer mens den jobber.
- Lagre flere LLM-profiler (en rask liten modell og en sterkere stor modell) og
  bytt mellom dem med `/model` midt i en samtale.
- Gå videre til [OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) for å
  gjøre tilbakevendende utviklingssløyfer om til planlagte eller hendelsesutløste agentkjøringer.

## Ressurser

- [OpenHands-dokumentasjon](https://docs.openhands.dev/)
- [Oversikt over Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Oppsett av Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler og modellkonfigurasjon](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server-dokumentasjon](https://lemonade-server.ai/docs)