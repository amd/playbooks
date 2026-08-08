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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) är en AI-programvaruagent
som kan skriva kod, köra kommandon, surfa på webben och redigera filer i en
riktig arbetsyta. Istället för att kopiera förslag från ett chattfönster pekar
du agenten mot en projektmapp och låter den utföra arbetet: implementera en
funktion, åtgärda en bugg, skriva tester eller förklara en kodbas.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) är det rekommenderade
webbläsargränssnittet för att köra OpenHands. Ett enda `agent-canvas`-kommando
startar agentservern, automationsbackend och webbfrontend tillsammans, så att
du kan driva en konversation med agenten från din webbläsare.

För att hålla allt på ditt AMD-system pratar agenten med en lokal modell som
körs via Lemonade Server. Lemonade exponerar den modellen genom ett
OpenAI-kompatibelt API, så Agent Canvas kan konfigurera den som vilken annan
OpenAI-liknande slutpunkt som helst, medan modellen, din kod och
konversationskontexten allt förblir på din maskin.

I den här spelboken startar du en lokal modell, startar Agent Canvas, pekar den
mot den modellen och kör din första kodningsuppgift mot en riktig projektmapp.

## Vad du kommer att lära dig

- Hur du startar Lemonade Server och bekräftar att en lokal modell svarar på chattförfrågningar
- Hur du installerar och startar Agent Canvas från npm-paketet
- Hur du konfigurerar Agent Canvas att använda en lokal Lemonade-modell som LLM
- Hur du startar en OpenHands-konversation och ser agenten redigera filer och köra
  kommandon i en arbetsyta
- Hur du granskar vad agenten ändrade och styr den med uppföljningsmeddelanden

## Grundläggande begrepp

| Begrepp | Vad det är | Var det passar in i den här spelboken |
| --- | --- | --- |
| Lemonade Server | En lokal LLM-serveringsplattform byggd för AMD-hårdvara som exponerar ett OpenAI-kompatibelt API. Dina data lämnar aldrig din maskin. | Kör modellen som driver agenten. |
| OpenHands | En AI-programvaruagent som läser och redigerar filer, kör skalkommandon och surfar på webben inom en arbetsyta. | Agenten du styr från chatten. |
| Agent Canvas | Webbläsargränssnittet och backend som kör OpenHands-konversationer och visar verktygsanrop och filändringar. | Startar stacken och hostar din konversation. |
| Arbetsyta | Projektmappen som agenten har tillåtelse att läsa och ändra. | Målet för agentens redigeringar och kommandon. |

<!-- @device:stx,krk -->
> [!NOTE]
> Kodningsagent-arbetsflöden gynnas av en större modell och kontextfönster.
> Använd minst 32 GB systemminne, och föredra 64 GB eller mer för större
> GGUF-modeller.
<!-- @device:end -->

## Förutsättningar

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Du behöver:

- Lemonade Server installerad och kapabel att köra modellen nedan.
- Node.js 22.12 eller senare och `npm` (används av `agent-canvas`-CLI:t).
- `uv`, Python-pakethanteraren som Agent Canvas använder för att hantera
  agentserverns miljö. Om ditt system inte redan har det, installera det från
  [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/)
  innan du startar Agent Canvas.
- En projektmapp att arbeta i. Detta kan vara vilket lokalt git-repository
  eller vilken kodkatalog som helst du vill att agenten ska arbeta på.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Starta Lemonade Server

Starta modellen från Lemonade-CLI:t:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade exponerar ett OpenAI-kompatibelt API på:

```text
http://127.0.0.1:13305/api/v1
```


## 2. Verifiera den lokala modellen

Bekräfta att Lemonade kan köra den valda modellen:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Skicka sedan en liten chattförfrågan:

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

Om detta returnerar en `choices`-array är Lemonade redo för Agent Canvas.

## 3. Installera och starta Agent Canvas

Installera det publicerade Agent Canvas-paketet globalt:

```bash
npm install -g @openhands/agent-canvas
```

Starta sedan hela stacken från en terminal:

```bash
agent-canvas
```

Som standard startar Agent Canvas på `http://localhost:8000`. Öppna den URL:en
i din webbläsare. Om port 8000 redan används, skicka med `--port` (eller `-p`)
när du startar Agent Canvas:

```bash
agent-canvas --port 3000
```

Samma kommando fungerar i PowerShell på Windows. Öppna sedan
`http://localhost:3000` istället. Standardbackenden för lokal drift bör visas
som frisk (healthy) på startskärmen.

Kommandot `agent-canvas` startar agentservern, automationsbackend och
webbfrontend tillsammans. Du behöver bara detta enda kommando för att köra
OpenHands lokalt.

## 4. Konfigurera den lokala LLM:en

Vid första starten öppnar Agent Canvas ett introduktionsflöde. I det flödet:

1. Behåll **OpenHands** markerad som agent och klicka på **Next**.
2. På **Set up your LLM**, välj **Advanced**.
3. Behåll **Authentication** inställt på **API key**.
4. Ställ in **Custom Model** till `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ställ in **Base URL** till `http://127.0.0.1:13305/api/v1`.
6. För **API Key**, ange en godtycklig icke-tom platshållare som
   `lemonade-local`. Lemonade kräver ingen riktig nyckel, men OpenHands-klienten
   behöver ett värde att skicka.
7. Klicka på **Next**.

De ifyllda Advanced-inställningarna bör se ut så här. API-nyckelfältet är
maskerat av gränssnittet.

![Agent Canvas första gångens LLM Advanced-inställningar med Lemonade-modellen och lokal bas-URL](assets/01-llm-advanced-settings.png)

Agent Canvas sparar dessa värden som en LLM-profil. Om din version ber dig
namnge den profilen, använd ett namn utan mellanslag som `lemonade-local`. Om
du byter modell senare, öppna **Settings > LLM** och uppdatera samma
Advanced-fält. Du kan växla mellan sparade profiler från chattinmatningen med
kommandot `/model`.

## 5. Öppna en arbetsyta

Agenten kan bara läsa och ändra filer inom en arbetsyta du väljer. Innan du
startar en uppgift, peka Agent Canvas mot din projektmapp:

1. Från startskärmen, välj **Open Workspace**.
2. Välj mappen som innehåller ditt projekt (till exempel ett git-repository
   du vill att agenten ska arbeta på).
3. Starta en ny konversation i den arbetsytan.

Allt agenten gör—läsa filer, köra kommandon, redigera kod—är begränsat till
den arbetsytan.

![Agent Canvas hemskärm efter introduktionen](assets/02-agent-canvas-home.png)
## 6. Kör din första kodningsuppgift

Med arbetsytan öppen och den lokala LLM:en vald, skriv en konkret uppgift i chatten. En bra första uppgift är liten och verifierbar, till exempel:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Följ konversationens tidslinje. OpenHands kommer att:

- Läsa arbetsytan för att förstå strukturen.
- Skapa `hello.py` med den begärda funktionen och testblocket.
- Eventuellt köra `python3 hello.py` för att verifiera resultatet.
- Rapportera vad den gjorde och eventuell kommandoutdata i chatten.

Du bör se den nya filen dyka upp i arbetsytan, och agentens slutmeddelande bör beskriva ändringen den gjorde. Detta är den avgörande stunden: agenten skrev och körde riktig kod i din projektmapp.

## 7. Granska och styr agenten

Efter att agenten har slutfört ett steg, granska dess arbete innan du godkänner nästa:

- **Filändringar**: använd arbetsytans filbläddrare eller agentens diff-vy för
  att se exakt vad som lades till, ändrades eller togs bort.
- **Kommandoutdata**: expandera valfritt kommando som agenten körde för att se stdout, stderr,
  och avslutningskoden.
- **Uppföljningar**: om resultatet inte blev vad du ville, svara i samma
  konversation med en rättelse. Agenten behåller den tidigare kontexten och
  itererar på samma filer.

Om testet till exempel inte skrev ut den förväntade hälsningen, svara:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agenten kommer att läsa om filen, köra kommandot, diagnostisera problemet och redigera
filen igen—allt i samma konversation.

## Felsökning

- **`agent-canvas` finns inte i PATH:** installera om med
  `npm install -g @openhands/agent-canvas` och bekräfta att npm:s globala binärkatalog
  finns i din PATH. På Windows, kör `npm config get prefix`; den
  returnerade katalogen, ofta `%APPDATA%\npm` eller `%USERPROFILE%\.npm-global`,
  måste finnas i din användar-PATH innan `agent-canvas` kan startas från en ny
  terminal.
- **`npm install -g` misslyckas med ett behörighetsfel:** konfigurera en användarägd
  global npm-katalog, öppna sedan om terminalen och installera Agent Canvas igen.

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

  För att göra ändringen av Windows PATH permanent, lägg till `%USERPROFILE%\.npm-global` i
  din användar-PATH från **Inställningar > System > Om > Avancerade systeminställningar >
  Miljövariabler**, och öppna en ny terminal.
  <!-- @os:end -->
- **Gränssnittet laddas men backend visar sig vara ohälsosam:** vänta några sekunder på att
  agentservern ska bli klar med att starta, uppdatera sedan. Om den förblir ohälsosam, starta om
  `agent-canvas` och kontrollera terminalens utdata för fel.
- **Lemonade-chattförfrågningar misslyckas med ett anslutningsfel:** bekräfta att
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` lyckas och att
  Lemonade fortfarande betjänar modellen med `lemonade status`.
- **Agenten ger felmeddelande om kontextlängd eller tokengräns:** starta om
  Lemonade med en större `ctx_size` (till exempel `ctx_size=65536`), och starta en
  ny konversation så att agenten inte bär med sig en alltför stor historik.
- **Agenten producerar redigeringar av låg kvalitet eller ofullständiga redigeringar:** byt till en större
  modell i Lemonade, eller ge agenten en mindre, mer konkret uppgift och låt den
  bli klar innan du ber om nästa ändring.
- **`uv` saknas:** installera det från
  [uv-installationsguiden](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas använder `uv` för att hantera agentserverns Python-miljö.

## Nästa steg

- Prova en större uppgift på samma arbetsyta, som att lägga till en enhetstestfil eller
  åtgärda en känd bugg, och granska agentens diff innan du behåller ändringen.
- Anslut en MCP-server som GitHub eller Slack under **Customize** så att
  agenten kan läsa ärenden eller posta uppdateringar medan den arbetar.
- Spara flera LLM-profiler (en snabb liten modell och en starkare stor modell) och
  växla mellan dem med `/model` mitt i konversationen.
- Gå vidare till [OpenHands-automatiseringar](https://docs.openhands.dev/openhands/usage/automations/overview) för att
  förvandla återkommande utvecklingsloopar till schemalagda eller händelseutlösta agentkörningar.

## Resurser

- [OpenHands-dokumentation](https://docs.openhands.dev/)
- [Agent Canvas översikt](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas-installation](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiler och modellkonfiguration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)