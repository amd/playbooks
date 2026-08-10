<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Přehled

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je softwarový AI agent,
který umí psát kód, spouštět příkazy, procházet web a upravovat soubory
v reálném pracovním prostoru. Místo kopírování návrhů z okna chatu nasměrujete
agenta na složku s projektem a necháte ho odvést práci: implementovat funkci,
opravit chybu, napsat testy nebo vysvětlit kódovou základnu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je doporučené
prohlížečové uživatelské rozhraní pro spouštění OpenHands. Jediný příkaz
`agent-canvas` spustí server agenta, backend pro automatizaci a webový
frontend společně, takže konverzaci s agentem můžete vést přímo z prohlížeče.

Aby vše zůstalo na vašem systému AMD, komunikuje agent s lokálním modelem
obsluhovaným serverem Lemonade Server. Lemonade zpřístupňuje tento model přes
API kompatibilní s OpenAI, takže Agent Canvas ho může nakonfigurovat stejně
jako kterýkoli jiný koncový bod ve stylu OpenAI, zatímco model, váš kód
a kontext konverzace zůstávají na vašem stroji.

V tomto playbooku spustíte lokální model, spustíte Agent Canvas, nasměrujete
ho na tento model a spustíte svůj první úkol pro psaní kódu na skutečné složce
s projektem.

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové
  požadavky
- Jak nainstalovat a spustit Agent Canvas z npm balíčku
- Jak nakonfigurovat Agent Canvas, aby jako LLM používal lokální model Lemonade
- Jak zahájit konverzaci OpenHands a sledovat, jak agent upravuje soubory
  a spouští příkazy v pracovním prostoru
- Jak zkontrolovat, co agent změnil, a nasměrovat ho pomocí navazujících zpráv

## Základní pojmy

| Pojem | Co to je | Kam v tomto playbooku zapadá |
| --- | --- | --- |
| Lemonade Server | Platforma pro lokální obsluhu LLM navržená pro hardware AMD, která zpřístupňuje API kompatibilní s OpenAI. Vaše data nikdy neopustí váš stroj. | Spouští model, který pohání agenta. |
| OpenHands | Softwarový AI agent, který čte a upravuje soubory, spouští příkazy shellu a prochází web v rámci pracovního prostoru. | Agent, kterého řídíte z chatu. |
| Agent Canvas | Prohlížečové uživatelské rozhraní a backend, které spouští konverzace OpenHands a zobrazuje volání nástrojů a změny souborů. | Spouští celý stack a hostuje vaši konverzaci. |
| Pracovní prostor | Složka projektu, kterou má agent povoleno číst a upravovat. | Cíl úprav a příkazů agenta. |

<!-- @device:stx,krk -->
> [!NOTE]
> Pracovní postupy s kódovacím agentem těží z většího modelu a kontextového
> okna. Použijte alespoň 32 GB systémové paměti a pro větší modely GGUF dejte
> přednost 64 GB nebo více.
<!-- @device:end -->

## Požadavky

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Budete potřebovat:

- Nainstalovaný Lemonade Server schopný obsluhovat níže uvedený model.
- Node.js 22.12 nebo novější a `npm` (používá je CLI `agent-canvas`).
- `uv`, správce balíčků Python, který Agent Canvas používá ke správě prostředí
  serveru agenta. Pokud jej váš systém ještě nemá, nainstalujte ho podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/)
  ještě před spuštěním Agent Canvas.
- Složku s projektem, na které se má pracovat. Může to být jakýkoli lokální
  git repozitář nebo adresář s kódem, na kterém má agent pracovat.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Spusťte Lemonade Server

Spusťte model z CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade zpřístupňuje API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Ověřte lokální model

Ověřte, že Lemonade dokáže obsluhovat vybraný model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Poté odešlete malý chatový požadavek:

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

Pokud tento požadavek vrátí pole `choices`, je Lemonade připraven pro Agent
Canvas.

## 3. Nainstalujte a spusťte Agent Canvas

Nainstalujte publikovaný balíček Agent Canvas globálně:

```bash
npm install -g @openhands/agent-canvas
```

Poté spusťte celý stack z terminálu:

```bash
agent-canvas
```

Ve výchozím nastavení se Agent Canvas spustí na adrese `http://localhost:8000`.
Otevřete tuto adresu URL ve svém prohlížeči. Pokud je port 8000 již obsazený,
předejte při spouštění Agent Canvas parametr `--port` (nebo `-p`):

```bash
agent-canvas --port 3000
```

Stejný příkaz funguje i v PowerShellu na Windows. Poté místo toho otevřete
`http://localhost:3000`. Výchozí lokální backend by měl být na domovské
obrazovce zobrazen jako funkční (healthy).

Příkaz `agent-canvas` spouští server agenta, backend pro automatizaci a webový
frontend společně. K lokálnímu spuštění OpenHands potřebujete jen tento jeden
příkaz.

## 4. Nakonfigurujte lokální LLM

Při prvním spuštění otevře Agent Canvas úvodní proces (onboarding). V rámci
tohoto procesu:

1. Ponechte jako agenta vybraný **OpenHands** a klikněte na **Next**.
2. Na obrazovce **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do pole **API Key** zadejte libovolný neprázdný zástupný text, například
   `lemonade-local`. Lemonade nevyžaduje skutečný klíč, ale klient OpenHands
   potřebuje nějakou hodnotu k odeslání.
7. Klikněte na **Next**.

Dokončené pokročilé (Advanced) nastavení by mělo vypadat takto. Pole s API
klíčem je v uživatelském rozhraní skryté hvězdičkami.

![Pokročilá nastavení LLM při prvním použití Agent Canvas s modelem Lemonade a lokální základní adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tyto hodnoty jako profil LLM. Pokud vás vaše verze požádá
o pojmenování tohoto profilu, použijte název bez mezer, například
`lemonade-local`. Pokud později změníte modely, otevřete **Settings > LLM**
a upravte stejná pokročilá pole. Uložené profily můžete přepínat přímo z pole
pro vkládání zpráv v chatu pomocí příkazu `/model`.

## 5. Otevřete pracovní prostor

Agent může číst a upravovat soubory pouze uvnitř pracovního prostoru, který
vyberete. Než zahájíte úkol, nasměrujte Agent Canvas na svou složku s
projektem:

1. Na domovské obrazovce zvolte **Open Workspace**.
2. Vyberte složku obsahující váš projekt (například git repozitář, na kterém
   má agent pracovat).
3. Zahajte v tomto pracovním prostoru novou konverzaci.

Vše, co agent dělá – čtení souborů, spouštění příkazů, úpravy kódu – je
omezeno na tento pracovní prostor.

![Domovská obrazovka Agent Canvas po dokončení onboardingu](assets/02-agent-canvas-home.png)
## 6. Spusťte svou první programovací úlohu

Po otevření pracovního prostoru a výběru lokálního LLM zadejte do chatu konkrétní úkol. Dobrým prvním úkolem je něco malého a snadno ověřitelného, například:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovou osu konverzace. OpenHands provede následující:

- Prohlédne pracovní prostor, aby pochopil jeho strukturu.
- Vytvoří soubor `hello.py` s požadovanou funkcí a testovacím blokem.
- Volitelně spustí `python3 hello.py`, aby ověřil výstup.
- V chatu popíše, co udělal, a případný výstup příkazu.

Měli byste vidět, jak se v pracovním prostoru objeví nový soubor, a závěrečná zpráva agenta by měla popisovat provedenou změnu. Toto je klíčový okamžik: agent napsal a spustil skutečný kód ve složce vašeho projektu.

## 7. Zkontrolujte agenta a usměrněte ho

Poté, co agent dokončí krok, zkontrolujte jeho práci, než přijmete další krok:

- **Změny souborů**: pomocí prohlížeče souborů v pracovním prostoru nebo zobrazení rozdílů (diff) agenta zjistíte přesně, co bylo přidáno, změněno nebo odstraněno.
- **Výstup příkazů**: rozbalte libovolný příkaz, který agent spustil, abyste viděli standardní výstup, chybový výstup a návratový kód.
- **Následné kroky**: pokud výsledek není takový, jaký jste chtěli, odpovězte ve stejné konverzaci s opravou. Agent si zachová předchozí kontext a bude pokračovat na stejných souborech.

Pokud například test nevypsal očekávaný pozdrav, odpovězte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent soubor znovu přečte, spustí příkaz, diagnostikuje problém a soubor znovu upraví – vše v rámci stejné konverzace.

## Řešení potíží

- **`agent-canvas` není v proměnné PATH:** přeinstalujte pomocí příkazu
  `npm install -g @openhands/agent-canvas` a ověřte, že adresář globálních binárních souborů npm je zahrnutý v proměnné PATH. Na Windows spusťte
  `npm config get prefix`; vrácený adresář, často
  `%APPDATA%\npm` nebo `%USERPROFILE%\.npm-global`, musí být zahrnutý v uživatelské proměnné PATH, než bude možné spustit `agent-canvas` z nového terminálu.
- **`npm install -g` selže s chybou oprávnění:** nakonfigurujte globální adresář npm vlastněný uživatelem, poté znovu otevřete terminál a nainstalujte Agent Canvas znovu.

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

  Abyste změnu proměnné PATH ve Windows provedli trvale, přidejte `%USERPROFILE%\.npm-global` do své uživatelské proměnné PATH v části **Nastavení > Systém > O systému > Upřesnit nastavení systému >
  Proměnné prostředí** a otevřete nový terminál.
  <!-- @os:end -->
- **Uživatelské rozhraní se načte, ale backend hlásí nesprávný stav:** počkejte několik sekund, než se dokončí spuštění serveru agenta, a poté obnovte stránku. Pokud stav zůstává nesprávný, restartujte `agent-canvas` a zkontrolujte výstup terminálu, zda neobsahuje chyby.
- **Chatové požadavky Lemonade selhávají s chybou připojení:** ověřte, že příkaz
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` je úspěšný a že Lemonade stále obsluhuje model – ověřte pomocí `lemonade status`.
- **Agentovi se zobrazí chyba týkající se délky kontextu nebo limitu tokenů:** restartujte Lemonade s větší hodnotou `ctx_size` (například `ctx_size=65536`) a začněte novou konverzaci, aby agent nepracoval s příliš velkou historií.
- **Agent vytváří nekvalitní nebo neúplné úpravy:** přepněte v Lemonade na větší model, nebo agentovi zadejte menší a konkrétnější úkol a nechte ho dokončit, než požádáte o další změnu.
- **Chybí `uv`:** nainstalujte ho podle
  [průvodce instalací uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používá `uv` ke správě prostředí Python pro server agenta.

## Další kroky

- Vyzkoušejte ve stejném pracovním prostoru rozsáhlejší úkol, například přidání souboru s jednotkovými testy nebo opravu známé chyby, a před přijetím změny zkontrolujte rozdíly (diff) vytvořené agentem.
- Připojte server MCP, například GitHub nebo Slack, v části **Customize**, aby agent mohl při práci číst issues nebo publikovat aktualizace.
- Uložte si více profilů LLM (rychlý malý model a výkonnější velký model) a přepínejte mezi nimi pomocí příkazu `/model` uprostřed konverzace.
- Pokračujte na [automatizace OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) a proměňte opakující se vývojové smyčky na plánované nebo událostmi spouštěné běhy agenta.

## Zdroje

- [Dokumentace OpenHands](https://docs.openhands.dev/)
- [Přehled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavení Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profily LLM a konfigurace modelu](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentace serveru Lemonade](https://lemonade-server.ai/docs)