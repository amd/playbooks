<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prehľad

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je softvérový agent
poháňaný AI, ktorý dokáže písať kód, spúšťať príkazy, prehliadať web a
upravovať súbory v reálnom pracovnom priestore. Namiesto kopírovania návrhov
z okna chatu nasmerujete agenta na priečinok projektu a necháte ho vykonať
prácu: implementovať funkciu, opraviť chybu, napísať testy alebo vysvetliť
kódovú bázu.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je odporúčané
používateľské rozhranie prehliadača na spúšťanie OpenHands. Jediný príkaz
`agent-canvas` spustí server agenta, automatizačný backend a webový frontend
spolu, takže konverzáciu s agentom môžete viesť priamo z prehliadača.

Aby všetko zostalo na vašom systéme AMD, agent komunikuje s lokálnym modelom
poskytovaným pomocou Lemonade Server. Lemonade sprístupňuje tento model cez
API kompatibilné s OpenAI, takže Agent Canvas ho môže nakonfigurovať ako
akýkoľvek iný koncový bod v štýle OpenAI, pričom model, váš kód a kontext
konverzácie zostávajú na vašom počítači.

V tomto playbooku spustíte lokálny model, spustíte Agent Canvas, nasmerujete
ho na tento model a spustíte svoju prvú úlohu kódovania na skutočnom priečinku
projektu.

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na chatové
  požiadavky
- Ako nainštalovať a spustiť Agent Canvas z npm balíčka
- Ako nakonfigurovať Agent Canvas na používanie lokálneho modelu Lemonade ako
  LLM
- Ako spustiť konverzáciu OpenHands a sledovať, ako agent upravuje súbory a
  spúšťa príkazy v pracovnom priestore
- Ako skontrolovať, čo agent zmenil, a nasmerovať ho ďalšími správami

## Základné pojmy

| Pojem | Čo to je | Kam zapadá v tomto playbooku |
| --- | --- | --- |
| Lemonade Server | Lokálna platforma na obsluhu LLM postavená pre hardvér AMD, ktorá sprístupňuje API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands | Softvérový agent poháňaný AI, ktorý číta a upravuje súbory, spúšťa príkazy shellu a prehliada web v rámci pracovného priestoru. | Agent, ktorý ovládate z chatu. |
| Agent Canvas | Rozhranie prehliadača a backend, ktorý spúšťa konverzácie OpenHands a zobrazuje volania nástrojov a zmeny súborov. | Spúšťa zásobník a hostí vašu konverzáciu. |
| Pracovný priestor | Priečinok projektu, ktorý má agent povolené čítať a upravovať. | Cieľ úprav a príkazov agenta. |

<!-- @device:stx,krk -->
> [!NOTE]
> Pracovné postupy kódovacích agentov profitujú z väčšieho modelu a väčšieho
> kontextového okna. Použite aspoň 32 GB systémovej pamäte a uprednostnite
> 64 GB alebo viac pri väčších GGUF modeloch.
<!-- @device:end -->

## Predpoklady

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrebujete:

- Nainštalovaný Lemonade Server schopný obsluhovať nižšie uvedený model.
- Node.js 22.12 alebo novší a `npm` (používa ho CLI nástroj `agent-canvas`).
- `uv`, správcu balíčkov Python, ktorý Agent Canvas používa na správu
  prostredia servera agenta. Ak ho váš systém ešte nemá, nainštalujte ho podľa
  [návodu na inštaláciu uv](https://docs.astral.sh/uv/getting-started/installation/)
  pred spustením Agent Canvas.
- Priečinok projektu, na ktorom sa má pracovať. Môže to byť akýkoľvek lokálny
  git repozitár alebo adresár s kódom, na ktorom má agent pracovať.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Spustite Lemonade Server

Spustite model z Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade sprístupňuje API kompatibilné s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Overte lokálny model

Overte, že Lemonade dokáže obsluhovať vybraný model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Potom odošlite malú chatovú požiadavku:

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

Ak sa vráti pole `choices`, Lemonade je pripravený pre Agent Canvas.

## 3. Nainštalujte a spustite Agent Canvas

Nainštalujte publikovaný balíček Agent Canvas globálne:

```bash
npm install -g @openhands/agent-canvas
```

Potom spustite celý zásobník z terminálu:

```bash
agent-canvas
```

Agent Canvas sa predvolene spustí na `http://localhost:8000`. Otvorte túto
adresu URL vo svojom prehliadači. Ak je port 8000 už používaný, pri spustení
Agent Canvas zadajte `--port` (alebo `-p`):

```bash
agent-canvas --port 3000
```

Rovnaký príkaz funguje aj v PowerShelli vo Windows. Potom namiesto toho
otvorte `http://localhost:3000`. Predvolený lokálny backend by mal byť na
domovskej obrazovke zobrazený ako zdravý (healthy).

Príkaz `agent-canvas` spúšťa server agenta, automatizačný backend a webový
frontend spolu. Na lokálne spustenie OpenHands potrebujete iba tento jeden
príkaz.

## 4. Nakonfigurujte lokálny LLM

Pri prvom spustení Agent Canvas otvorí úvodný proces (onboarding). V tomto
procese:

1. Ponechajte vybraté **OpenHands** ako agenta a kliknite na **Next**.
2. Na obrazovke **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do poľa **API Key** zadajte akýkoľvek nepovinný zástupný text, napríklad
   `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands
   potrebuje nejakú hodnotu na odoslanie.
7. Kliknite na **Next**.

Dokončené pokročilé nastavenia by mali vyzerať takto. Pole s API kľúčom je
v rozhraní skryté (maskované).

![Pokročilé nastavenia LLM pri prvom použití Agent Canvas s modelom Lemonade a lokálnou základnou adresou URL](assets/01-llm-advanced-settings.png)

Agent Canvas uloží tieto hodnoty ako profil LLM. Ak vás vaša verzia požiada o
pomenovanie tohto profilu, použite názov bez medzier, napríklad
`lemonade-local`. Ak neskôr zmeníte modely, otvorte **Settings > LLM** a
aktualizujte rovnaké pokročilé polia. Uložené profily môžete prepínať
z chatového vstupu pomocou príkazu `/model`.

## 5. Otvorte pracovný priestor

Agent môže čítať a upravovať súbory iba v rámci pracovného priestoru, ktorý
zvolíte. Pred spustením úlohy nasmerujte Agent Canvas na priečinok svojho
projektu:

1. Na domovskej obrazovke vyberte **Open Workspace**.
2. Vyberte priečinok obsahujúci váš projekt (napríklad git repozitár, na
   ktorom má agent pracovať).
3. Spustite v tomto pracovnom priestore novú konverzáciu.

Všetko, čo agent robí — čítanie súborov, spúšťanie príkazov, úprava kódu — je
obmedzené na tento pracovný priestor.

![Domovská obrazovka Agent Canvas po dokončení onboardingu](assets/02-agent-canvas-home.png)
## 6. Spustite svoju prvú úlohu kódovania

S otvoreným pracovným priestorom a vybraným lokálnym LLM zadajte do chatu konkrétnu úlohu. Dobrá prvá úloha je malá a overiteľná, napríklad:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Sledujte časovú os konverzácie. OpenHands vykoná nasledovné:

- Prečíta pracovný priestor, aby pochopil jeho štruktúru.
- Vytvorí súbor `hello.py` s požadovanou funkciou a testovacím blokom.
- Voliteľne spustí `python3 hello.py`, aby overil výstup.
- V chate oznámi, čo urobil, a prípadný výstup príkazu.

Mali by ste vidieť, ako sa v pracovnom priestore objaví nový súbor, a záverečná správa agenta by mala popisovať vykonanú zmenu. Toto je kľúčový moment – agent napísal a spustil skutočný kód vo vašom projektovom priečinku.

## 7. Skontrolujte prácu agenta a usmerňujte ho

Po dokončení kroku agentom si pred prijatím ďalšieho kroku prezrite jeho prácu:

- **Zmeny súborov**: použite prehliadač súborov pracovného priestoru alebo zobrazenie rozdielov (diff) agenta, aby ste presne videli, čo bolo pridané, zmenené alebo odstránené.
- **Výstup príkazov**: rozbaľte ľubovoľný príkaz, ktorý agent spustil, aby ste videli stdout, stderr a návratový kód.
- **Nadväzujúce kroky**: ak výsledok nie je taký, aký ste chceli, odpovedzte v rovnakej konverzácii s opravou. Agent si zachová predchádzajúci kontext a pokračuje v úprave rovnakých súborov.

Ak napríklad test nevytlačil očakávaný pozdrav, odpovedzte:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent súbor znova prečíta, spustí príkaz, diagnostikuje problém a znova upraví súbor – to všetko v rámci tej istej konverzácie.

## Riešenie problémov

- **`agent-canvas` nie je v PATH:** preinštalujte pomocou
  `npm install -g @openhands/agent-canvas` a overte, či je globálny adresár binárnych súborov npm zahrnutý vo vašej premennej PATH. V systéme Windows spustite
  `npm config get prefix`; vrátený adresár, často `%APPDATA%\npm` alebo `%USERPROFILE%\.npm-global`,
  musí byť v používateľskej premennej PATH, aby bolo možné spustiť `agent-canvas` z nového
  terminálu.
- **Príkaz `npm install -g` zlyhá s chybou oprávnení:** nakonfigurujte globálny adresár npm vo vlastníctve používateľa, potom znova otvorte terminál a znova nainštalujte Agent Canvas.

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

  Ak chcete zmenu premennej PATH v systéme Windows urobiť trvalou, pridajte `%USERPROFILE%\.npm-global` do
  svojej používateľskej premennej PATH cez **Settings > System > About > Advanced system settings >
  Environment Variables** a otvorte nový terminál.
  <!-- @os:end -->
- **Rozhranie sa načíta, ale backend zobrazuje stav unhealthy:** počkajte niekoľko sekúnd, kým sa server agenta dokončí spúšťanie, potom obnovte stránku. Ak stav unhealthy pretrváva, reštartujte
  `agent-canvas` a skontrolujte výstup v termináli, či sa nevyskytli chyby.
- **Požiadavky na chat Lemonade zlyhávajú s chybou pripojenia:** overte, že príkaz
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` je úspešný a že
  Lemonade stále poskytuje model pomocou príkazu `lemonade status`.
- **Agent hlási chybu súvisiacu s dĺžkou kontextu alebo limitom tokenov:** reštartujte
  Lemonade s väčšou hodnotou `ctx_size` (napríklad `ctx_size=65536`) a začnite
  novú konverzáciu, aby agent nepracoval s neúmerne veľkou históriou.
- **Agent vytvára nekvalitné alebo neúplné úpravy:** prepnite na väčší
  model v Lemonade, alebo zadajte agentovi menšiu, konkrétnejšiu úlohu a nechajte ho
  dokončiť ju pred zadaním ďalšej zmeny.
- **Chýba `uv`:** nainštalujte ho podľa
  [návodu na inštaláciu uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas používa `uv` na správu Python prostredia servera agenta.

## Ďalšie kroky

- Vyskúšajte väčšiu úlohu v rovnakom pracovnom priestore, napríklad pridanie súboru s jednotkovým testom alebo
  opravu známej chyby, a pred zachovaním zmeny si prezrite rozdiely (diff) agenta.
- Pripojte server MCP, napríklad GitHub alebo Slack, v sekcii **Customize**, aby
  agent mohol čítať problémy (issues) alebo zverejňovať aktualizácie počas svojej práce.
- Uložte si viacero profilov LLM (rýchly malý model a výkonnejší veľký model) a
  prepínajte medzi nimi pomocou `/model` počas konverzácie.
- Pokračujte na [automatizácie OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), aby ste
  premenili opakujúce sa vývojové cykly na naplánované alebo udalosťami spúšťané spustenia agenta.

## Zdroje

- [Dokumentácia OpenHands](https://docs.openhands.dev/)
- [Prehľad Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavenie Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profily LLM a konfigurácia modelov](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentácia Lemonade Server](https://lemonade-server.ai/docs)