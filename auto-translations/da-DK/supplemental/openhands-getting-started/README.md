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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) er en AI-softwareagent,
der kan skrive kode, køre kommandoer, browse på internettet og redigere filer i et
rigtigt arbejdsområde. I stedet for at kopiere forslag ud af et chatvindue, peger du
agenten mod en projektmappe og lader den gøre arbejdet: implementere en funktion, rette
en fejl, skrive tests eller forklare en kodebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er den anbefalede
browser-UI til at køre OpenHands. En enkelt `agent-canvas`-kommando starter
agentserveren, automationsbackenden og webfrontenden sammen, så du kan
føre en samtale med agenten fra din browser.

For at holde alt på dit AMD-system taler agenten med en lokal model, der serveres
af Lemonade Server. Lemonade eksponerer den model gennem et OpenAI-kompatibelt
API, så Agent Canvas kan konfigurere det som ethvert andet OpenAI-lignende endpoint,
mens modellen, din kode og samtalekonteksten alle forbliver på din
maskine.

I denne playbook skal du starte en lokal model, starte Agent Canvas, pege den
mod den model og køre din første kodningsopgave mod en rigtig projektmappe.

## Hvad du vil lære

- Hvordan du starter Lemonade Server og bekræfter, at en lokal model svarer på chatanmodninger
- Hvordan du installerer og starter Agent Canvas fra npm-pakken
- Hvordan du konfigurerer Agent Canvas til at bruge en lokal Lemonade-model som LLM
- Hvordan du starter en OpenHands-samtale og ser agenten redigere filer og køre
  kommandoer i et arbejdsområde
- Hvordan du gennemgår, hvad agenten har ændret, og styrer den med opfølgende beskeder

## Grundlæggende koncepter

| Koncept | Hvad det er | Hvor det passer ind i denne playbook |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplatform bygget til AMD-hardware, der eksponerer et OpenAI-kompatibelt API. Dine data forlader aldrig din maskine. | Kører modellen, der driver agenten. |
| OpenHands | En AI-softwareagent, der læser og redigerer filer, kører shell-kommandoer og browser på internettet inde i et arbejdsområde. | Agenten du styrer fra chatten. |
| Agent Canvas | Browser-UI'en og backenden, der kører OpenHands-samtaler og viser toolkald og filændringer. | Starter stacken og hoster din samtale. |
| Arbejdsområde | Projektmappen, som agenten har tilladelse til at læse og ændre. | Målet for agentens redigeringer og kommandoer. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodningsagent-workflows drager fordel af en større model og et større kontekstvindue. Brug
> mindst 32 GB systemhukommelse, og foretræk 64 GB eller mere til større GGUF-modeller.
<!-- @device:end -->

## Forudsætninger

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du skal bruge:

- Lemonade Server installeret og i stand til at servere modellen nedenfor.
- Node.js 22.12 eller nyere og `npm` (bruges af `agent-canvas`-CLI'en).
- `uv`, den Python-pakkehåndtering som Agent Canvas bruger til at håndtere agent-serverens
  miljø. Hvis dit system ikke allerede har det, skal du installere det fra
  [uv-installationsvejledningen](https://docs.astral.sh/uv/getting-started/installation/)
  før du starter Agent Canvas.
- En projektmappe at arbejde i. Dette kan være ethvert lokalt git-repository eller kode-
  bibliotek, du vil have agenten til at arbejde på.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Start Lemonade Server

Start modellen fra Lemonade CLI'en:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade eksponerer et OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Bekræft den lokale model

Bekræft at Lemonade kan servere den valgte model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Send derefter en lille chatanmodning:

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

Hvis dette returnerer et `choices`-array, er Lemonade klar til Agent Canvas.

## 3. Installer og start Agent Canvas

Installer den udgivne Agent Canvas-pakke globalt:

```bash
npm install -g @openhands/agent-canvas
```

Start derefter hele stacken fra en terminal:

```bash
agent-canvas
```

Som standard starter Agent Canvas på `http://localhost:8000`. Åbn den URL i
din browser. Hvis port 8000 allerede er i brug, skal du angive `--port` (eller `-p`), når du
starter Agent Canvas:

```bash
agent-canvas --port 3000
```

Den samme kommando fungerer i PowerShell på Windows. Åbn derefter
`http://localhost:3000` i stedet. Den lokale standardbackend bør vises som
sund på startskærmen.

Kommandoen `agent-canvas` starter agentserveren, automationsbackenden og
webfrontenden sammen. Du behøver kun denne ene kommando for at køre OpenHands
lokalt.

## 4. Konfigurer den lokale LLM

Ved første start åbner Agent Canvas et onboarding-forløb. I det forløb:

1. Behold **OpenHands** valgt som agent, og klik på **Next**.
2. Under **Set up your LLM**, vælg **Advanced**.
3. Behold **Authentication** sat til **API key**.
4. Sæt **Custom Model** til `openai/Qwen3.6-35B-A3B-GGUF`.
5. Sæt **Base URL** til `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, indtast en vilkårlig ikke-tom pladsholder såsom `lemonade-local`.
   Lemonade kræver ikke en rigtig nøgle, men OpenHands-klienten skal bruge en værdi
   at sende.
7. Klik på **Next**.

De udfyldte Advanced-indstillinger bør se sådan ud. API-nøglefeltet er
maskeret af UI'en.

![Agent Canvas første brug LLM Advanced-indstillinger med Lemonade-modellen og lokal base-URL](assets/01-llm-advanced-settings.png)

Agent Canvas gemmer disse værdier som en LLM-profil. Hvis din version beder dig om at
navngive den profil, brug et navn uden mellemrum, såsom `lemonade-local`. Hvis du skifter
modeller senere, åbn **Settings > LLM** og opdater de samme Advanced-felter. Du
kan skifte mellem gemte profiler fra chat-inputfeltet med kommandoen `/model`.

## 5. Åbn et arbejdsområde

Agenten kan kun læse og ændre filer inde i et arbejdsområde, du vælger. Før du
starter en opgave, skal du pege Agent Canvas mod din projektmappe:

1. Fra startskærmen skal du vælge **Open Workspace**.
2. Vælg mappen, der indeholder dit projekt (for eksempel et git-repository,
   du vil have agenten til at arbejde på).
3. Start en ny samtale i det arbejdsområde.

Alt hvad agenten gør — læse filer, køre kommandoer, redigere kode — er
begrænset til det arbejdsområde.

![Agent Canvas-hjemmeside efter onboarding](assets/02-agent-canvas-home.png)
## 6. Kør din første kodningsopgave

Med workspacet åbent og den lokale LLM valgt, skal du skrive en konkret opgave
i chatten. En god første opgave er lille og verificerbar, for eksempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Følg samtaleforløbet. OpenHands vil:

- Læse workspacet for at forstå strukturen.
- Oprette `hello.py` med den ønskede funktion og testblok.
- Eventuelt køre `python3 hello.py` for at verificere output.
- Rapportere hvad den gjorde, og eventuelt kommandooutput i chatten.

Du bør se den nye fil dukke op i workspacet, og agentens afsluttende besked
bør beskrive den ændring, den har foretaget. Dette er den store belønning:
agenten skrev og kørte rigtig kode i din projektmappe.

## 7. Gennemgå og styr agenten

Når agenten har afsluttet et trin, skal du gennemgå dens arbejde, før du
accepterer det næste:

- **Filændringer**: brug workspacets filbrowser eller agentens diff-visning
  for at se præcis, hvad der blev tilføjet, ændret eller slettet.
- **Kommandooutput**: udvid enhver kommando, agenten kørte, for at se stdout,
  stderr og exit-koden.
- **Opfølgninger**: hvis resultatet ikke er, hvad du ønskede, kan du svare i
  samme samtale med en rettelse. Agenten bevarer den tidligere kontekst og
  itererer på de samme filer.

Hvis testen for eksempel ikke udskrev den forventede hilsen, kan du svare:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten vil læse filen igen, køre kommandoen, diagnosticere problemet og
redigere filen igen — alt sammen i den samme samtale.

## Fejlfinding

- **`agent-canvas` findes ikke i PATH:** geninstaller med
  `npm install -g @openhands/agent-canvas` og bekræft, at npms globale
  binærmappe er i din PATH. På Windows skal du køre `npm config get prefix`;
  den returnerede mappe, ofte `%APPDATA%\npm` eller
  `%USERPROFILE%\.npm-global`, skal være i din bruger-PATH, før
  `agent-canvas` kan startes fra en ny terminal.
- **`npm install -g` fejler med en tilladelsesfejl:** konfigurer en
  brugerejet global npm-mappe, genåbn derefter terminalen, og installer
  Agent Canvas igen.

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

  For at gøre ændringen af Windows PATH permanent skal du tilføje
  `%USERPROFILE%\.npm-global` til din bruger-PATH under **Indstillinger >
  System > Om > Avancerede systemindstillinger > Miljøvariabler** og åbne en
  ny terminal.
  <!-- @os:end -->
- **UI'et indlæses, men backend viser unhealthy:** vent et par sekunder på,
  at agentserveren bliver færdig med at starte, og opdater derefter. Hvis den
  forbliver unhealthy, skal du genstarte `agent-canvas` og tjekke
  terminaloutputtet for fejl.
- **Lemonade chat-anmodninger fejler med en forbindelsesfejl:** bekræft, at
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lykkes, og at Lemonade
  stadig serverer modellen med `lemonade status`.
- **Agenten fejler med en fejlmeddelelse om kontekstlængde eller
  token-grænse:** genstart Lemonade med en større `ctx_size` (for eksempel
  `ctx_size=65536`), og start en ny samtale, så agenten ikke bærer rundt på
  en for stor historik.
- **Agenten producerer redigeringer af lav kvalitet eller ufuldstændige
  redigeringer:** skift til en større model i Lemonade, eller giv agenten en
  mindre, mere konkret opgave, og lad den blive færdig, før du beder om den
  næste ændring.
- **`uv` mangler:** installer det fra
  [installationsguiden til uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas bruger `uv` til at administrere agentserverens
  Python-miljø.

## Næste skridt

- Prøv en større opgave i det samme workspace, såsom at tilføje en
  unit test-fil eller rette en kendt fejl, og gennemgå agentens diff, før du
  beholder ændringen.
- Tilslut en MCP-server såsom GitHub eller Slack under **Customize**, så
  agenten kan læse issues eller poste opdateringer, mens den arbejder.
- Gem flere LLM-profiler (en hurtig lille model og en stærkere stor model), og
  skift mellem dem med `/model` midt i en samtale.
- Gå videre til [OpenHands-automatiseringer](https://docs.openhands.dev/openhands/usage/automations/overview) for
  at omdanne tilbagevendende udviklingsforløb til planlagte eller
  hændelsesudløste agentkørsler.

## Ressourcer

- [OpenHands-dokumentation](https://docs.openhands.dev/)
- [Oversigt over Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Opsætning af Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler og modelkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentation til Lemonade Server](https://lemonade-server.ai/docs)