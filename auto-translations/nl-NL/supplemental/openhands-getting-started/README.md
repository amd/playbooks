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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) is een AI-softwareagent
die code kan schrijven, opdrachten kan uitvoeren, kan browsen op het web en bestanden kan bewerken in een echte
werkruimte. In plaats van suggesties uit een chatvenster te kopiëren, wijst u de
agent naar een projectmap en laat u deze het werk doen: een functie implementeren, een
bug oplossen, tests schrijven of een codebase uitleggen.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is de aanbevolen
browser-UI voor het uitvoeren van OpenHands. Eén enkele opdracht `agent-canvas` start
de agentserver, de automatiseringsbackend en de webfrontend samen, zodat u
een gesprek met de agent vanuit uw browser kunt voeren.

Om alles op uw AMD-systeem te houden, praat de agent met een lokaal model dat wordt geserveerd
door Lemonade Server. Lemonade stelt dat model beschikbaar via een OpenAI-compatibele
API, zodat Agent Canvas het kan configureren zoals elk ander OpenAI-achtig endpoint,
terwijl het model, uw code en de gespreksconteкst allemaal op uw
machine blijven.

In dit playbook start u een lokaal model, start u Agent Canvas, wijst u het
naar dat model en voert u uw eerste codeertaak uit op een echte projectmap.

## Wat u leert

- Hoe u Lemonade Server start en bevestigt dat een lokaal model chatverzoeken beantwoordt
- Hoe u Agent Canvas installeert en start vanuit het npm-pakket
- Hoe u Agent Canvas configureert om een lokaal Lemonade-model als de LLM te gebruiken
- Hoe u een OpenHands-gesprek start en toekijkt terwijl de agent bestanden bewerkt en
  opdrachten uitvoert in een werkruimte
- Hoe u beoordeelt wat de agent heeft gewijzigd en deze bijstuurt met vervolgberichten

## Kernconcepten

| Concept | Wat het is | Waar het past in dit playbook |
| --- | --- | --- |
| Lemonade Server | Een lokaal LLM-serveerplatform gebouwd voor AMD-hardware dat een OpenAI-compatibele API beschikbaar stelt. Uw gegevens verlaten nooit uw machine. | Voert het model uit dat de agent aandrijft. |
| OpenHands | Een AI-softwareagent die bestanden leest en bewerkt, shellopdrachten uitvoert en op het web browst binnen een werkruimte. | De agent die u vanuit de chat aanstuurt. |
| Agent Canvas | De browser-UI en backend die OpenHands-gesprekken uitvoert en tool-aanroepen en bestandswijzigingen toont. | Start de stack en host uw gesprek. |
| Workspace | De projectmap die de agent mag lezen en wijzigen. | Het doelwit van de bewerkingen en opdrachten van de agent. |

<!-- @device:stx,krk -->
> [!NOTE]
> Codeeragent-workflows profiteren van een groter model en contextvenster. Gebruik ten minste
> 32 GB systeemgeheugen, en geef de voorkeur aan 64 GB of meer voor grotere GGUF-modellen.
<!-- @device:end -->

## Vereisten

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

U hebt het volgende nodig:

- Lemonade Server geïnstalleerd en in staat om het onderstaande model te serveren.
- Node.js 22.12 of hoger en `npm` (gebruikt door de `agent-canvas` CLI).
- `uv`, de Python-pakketbeheerder die Agent Canvas gebruikt om de agentserver-
  omgeving te beheren. Als uw systeem dit nog niet heeft, installeer het dan vanuit
  de [uv-installatiegids](https://docs.astral.sh/uv/getting-started/installation/)
  voordat u Agent Canvas start.
- Een projectmap om in te werken. Dit kan elke lokale git-repository of codemap
  zijn waarin u de agent wilt laten werken.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Lemonade Server starten

Start het model vanuit de Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade stelt een OpenAI-compatibele API beschikbaar op:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Het lokale model verifiëren

Bevestig dat Lemonade het geselecteerde model kan serveren:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Stuur vervolgens een klein chatverzoek:

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

Als dit een `choices`-array retourneert, is Lemonade klaar voor Agent Canvas.

## 3. Agent Canvas installeren en starten

Installeer het gepubliceerde Agent Canvas-pakket globaal:

```bash
npm install -g @openhands/agent-canvas
```

Start vervolgens de volledige stack vanuit een terminal:

```bash
agent-canvas
```

Standaard start Agent Canvas op `http://localhost:8000`. Open die URL in
uw browser. Als poort 8000 al in gebruik is, geef dan `--port` (of `-p`) door wanneer u
Agent Canvas start:

```bash
agent-canvas --port 3000
```

Dezelfde opdracht werkt in PowerShell op Windows. Open dan
`http://localhost:3000` in plaats daarvan. De standaard lokale backend zou als
gezond moeten worden weergegeven op het startscherm.

De opdracht `agent-canvas` start de agentserver, de automatiseringsbackend en
de webfrontend samen. U hebt slechts deze ene opdracht nodig om OpenHands
lokaal uit te voeren.

## 4. De lokale LLM configureren

Bij de eerste keer opstarten opent Agent Canvas een onboarding-flow. In die flow:

1. Houd **OpenHands** geselecteerd als de agent en klik op **Next**.
2. Selecteer bij **Set up your LLM** de optie **Advanced**.
3. Houd **Authentication** ingesteld op **API key**.
4. Stel **Custom Model** in op `openai/Qwen3.6-35B-A3B-GGUF`.
5. Stel **Base URL** in op `http://127.0.0.1:13305/api/v1`.
6. Voer voor **API Key** een niet-lege placeholder in, zoals `lemonade-local`.
   Lemonade vereist geen echte sleutel, maar de OpenHands-client heeft een waarde
   nodig om te verzenden.
7. Klik op **Next**.

De voltooide Advanced-instellingen zouden er zo uit moeten zien. Het API-sleutelveld is
gemaskeerd door de UI.

![Agent Canvas-LLM Advanced-instellingen bij eerste gebruik met het Lemonade-model en lokale basis-URL](assets/01-llm-advanced-settings.png)

Agent Canvas slaat deze waarden op als een LLM-profiel. Als uw versie u vraagt om dat
profiel een naam te geven, gebruik dan een naam zonder spaties, zoals `lemonade-local`. Als u later
modellen wijzigt, open dan **Settings > LLM** en werk dezelfde Advanced-velden bij. U
kunt opgeslagen profielen wisselen vanuit de chatinvoer met de opdracht `/model`.

## 5. Een werkruimte openen

De agent kan alleen bestanden lezen en wijzigen binnen een werkruimte die u kiest. Voordat u
een taak start, wijst u Agent Canvas naar uw projectmap:

1. Kies vanaf het startscherm **Open Workspace**.
2. Selecteer de map die uw project bevat (bijvoorbeeld een git-repository
   waarin u de agent wilt laten werken).
3. Start een nieuw gesprek in die werkruimte.

Alles wat de agent doet—bestanden lezen, opdrachten uitvoeren, code bewerken—is
beperkt tot die werkruimte.

![Agent Canvas-startscherm na onboarding](assets/02-agent-canvas-home.png)
## 6. Voer uw eerste codeertaak uit

Nu de workspace is geopend en het lokale LLM is geselecteerd, typt u een concrete taak in de chat. Een goede eerste taak is klein en verifieerbaar, bijvoorbeeld:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Volg de tijdlijn van het gesprek. OpenHands zal:

- De workspace lezen om de indeling te begrijpen.
- `hello.py` aanmaken met de gevraagde functie en testblok.
- Optioneel `python3 hello.py` uitvoeren om de uitvoer te verifiëren.
- Rapporteren wat het heeft gedaan en eventuele opdrachtuitvoer in de chat.

U zou het nieuwe bestand moeten zien verschijnen in de workspace, en het laatste bericht van de agent zou de aangebrachte wijziging moeten beschrijven. Dit is het beloningsmoment: de agent heeft echte code geschreven en uitgevoerd in uw projectmap.

## 7. Beoordeel en stuur de agent bij

Nadat de agent een stap heeft voltooid, beoordeelt u het werk voordat u de volgende stap accepteert:

- **Bestandswijzigingen**: gebruik de bestandsbrowser van de workspace of de diff-weergave van de agent om precies te zien wat er is toegevoegd, gewijzigd of verwijderd.
- **Opdrachtuitvoer**: klap elke opdracht die de agent heeft uitgevoerd uit om stdout, stderr en de exitcode te zien.
- **Vervolgstappen**: als het resultaat niet is wat u wilde, reageert u in hetzelfde gesprek met een correctie. De agent behoudt de eerdere context en werkt verder aan dezelfde bestanden.

Als de test bijvoorbeeld niet de verwachte begroeting afdrukte, antwoordt u:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

De agent zal het bestand opnieuw lezen, de opdracht uitvoeren, het probleem diagnosticeren en het bestand opnieuw bewerken—allemaal binnen hetzelfde gesprek.

## Probleemoplossing

- **`agent-canvas` staat niet in het PATH:** installeer opnieuw met
  `npm install -g @openhands/agent-canvas` en controleer of de globale npm-binairenmap
  in uw PATH staat. Voer op Windows `npm config get prefix` uit; de
  geretourneerde map, vaak `%APPDATA%\npm` of `%USERPROFILE%\.npm-global`,
  moet in uw gebruikers-PATH staan voordat `agent-canvas` vanuit een nieuwe
  terminal kan worden gestart.
- **`npm install -g` mislukt met een machtigingsfout:** configureer een globale
  npm-map die eigendom is van de gebruiker, open vervolgens de terminal opnieuw en installeer Agent Canvas opnieuw.

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

  Om de wijziging van het Windows-PATH permanent te maken, voegt u `%USERPROFILE%\.npm-global` toe aan
  uw gebruikers-PATH via **Instellingen > Systeem > Over > Geavanceerde systeeminstellingen >
  Omgevingsvariabelen**, en opent u een nieuwe terminal.
  <!-- @os:end -->
- **De UI laadt, maar de backend geeft ongezond aan:** wacht enkele seconden totdat
  de agentserver klaar is met opstarten en vernieuw dan. Als het ongezond blijft, start
  `agent-canvas` opnieuw en controleer de terminaluitvoer op fouten.
- **Lemonade-chatverzoeken mislukken met een verbindingsfout:** controleer of
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` slaagt en of
  Lemonade het model nog steeds levert met `lemonade status`.
- **De agent geeft een foutmelding over contextlengte of tokenlimiet:** start
  Lemonade opnieuw met een grotere `ctx_size` (bijvoorbeeld `ctx_size=65536`), en start een
  nieuw gesprek zodat de agent geen te grote geschiedenis meedraagt.
- **De agent produceert bewerkingen van lage kwaliteit of onvolledige bewerkingen:** schakel over naar een groter
  model in Lemonade, of geef de agent een kleinere, concretere taak en laat deze
  afronden voordat u om de volgende wijziging vraagt.
- **`uv` ontbreekt:** installeer het vanuit
  [de installatiehandleiding voor uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas gebruikt `uv` om de Python-omgeving van de agentserver te beheren.

## Volgende stappen

- Probeer een grotere taak in dezelfde workspace, zoals het toevoegen van een unit-testbestand of
  het oplossen van een bekende bug, en beoordeel de diff van de agent voordat u de wijziging behoudt.
- Verbind een MCP-server zoals GitHub of Slack onder **Aanpassen** zodat
  de agent issues kan lezen of updates kan plaatsen tijdens het werk.
- Sla meerdere LLM-profielen op (een snel klein model en een sterker groot model) en
  wissel ertussen met `/model` halverwege een gesprek.
- Ga verder naar [OpenHands-automatiseringen](https://docs.openhands.dev/openhands/usage/automations/overview) om
  terugkerende ontwikkellussen om te zetten in geplande of gebeurtenisgestuurde agentuitvoeringen.

## Bronnen

- [OpenHands-documentatie](https://docs.openhands.dev/)
- [Overzicht van Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas instellen](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profielen en modelconfiguratie](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentatie van Lemonade Server](https://lemonade-server.ai/docs)