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

Vývojári trávia veľa času malými opakujúcimi sa slučkami: kontrolou
označených pull requestov, odpovedaním na komentáre na GitHube, triedením
nových issues, prevádzaním vlákien zo Slacku na poznámky zo standupov alebo
následné kroky pri incidentoch a sledovaním signálov o vydaniach či
výskume. Každá slučka je známa, no napriek tomu vyžaduje úsudok: zhromaždiť
správny kontext, rozhodnúť, čo je dôležité, a uverejniť jasnú aktualizáciu
tam, kde tím už pracuje.

[Automatizácie OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
menia tieto slučky na naplánované alebo udalosťou spúšťané konverzácie
agenta: behy, v ktorých AI softvérový agent dokáže čítať kontext, volať
nástroje a vytvárať aktualizáciu. Zdieľané šablóny automatizácií v katalógu
rozšírení OpenHands nasledujú tento vzor pre kontrolu pull requestov na
GitHube, monitorovanie repozitárov, triedenie issues v Linear, retrospektívy
incidentov, denné súhrny zo Slacku a výskumné prehľady: automatizácia sa
prebudí, použije nakonfigurované integrácie ako GitHub alebo Slack na
získanie kontextu, uvažuje nad týmto kontextom pomocou veľkého jazykového
modelu (LLM) a zapíše späť výsledok.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokálna riadiaca
rovina na vytváranie a testovanie týchto automatizácií. V tomto playbooku
spúšťa OpenHands Agent Server, backendový proces, ktorý vykonáva konverzácie
agenta, a prepája agenta s externými službami, ako sú GitHub a Slack.

Aby pracovný postup zostal na vašom systéme AMD, agent komunikuje s lokálnym
modelom obsluhovaným cez Lemonade Server. Lemonade sprístupňuje tento model
prostredníctvom rozhrania API kompatibilného s OpenAI, takže ho Agent Canvas
môže nakonfigurovať ako vzdialený koncový bod v štýle OpenAI, pričom model,
prompt a kontext pracovného postupu zostávajú lokálne.

V tomto playbooku vytvoríte jednu konkrétnu automatizáciu: naplánovaný
vývojový súhrn z GitHubu do Slacku. Tá využíva GitHub na skúmanie nedávnej
aktivity v repozitári, Slack na uverejnenie súhrnu, volania API Agent Canvas
na konfiguráciu a testovanie automatizácie a Lemonade na lokálny beh LLM.

![Diagram architektúry zobrazujúci GitHub MCP, automatizáciu OpenHands, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Čo sa naučíte

- Ako spustiť Lemonade Server a overiť, že lokálny model odpovedá na
  chatové požiadavky
- Ako spustiť Agent Canvas a nasmerovať jeho Agent Server na lokálny LLM
- Ako nainštalovať servery Model Context Protocol (MCP) pre GitHub a Slack
  prostredníctvom API Agent Serveru
- Ako vytvoriť a spustiť naplánovanú automatizáciu OpenHands, ktorá
  uverejňuje vývojový súhrn na Slack
- Ako riešiť najčastejšie zlyhania lokálneho modelu a automatizácie

## Základné pojmy

| Pojem | Čo to je | Kde zapadá do tohto playbooku |
| --- | --- | --- |
| Lemonade Server | Lokálna platforma na obsluhu LLM vytvorená pre hardvér AMD, ktorá sprístupňuje rozhranie API kompatibilné s OpenAI. Vaše dáta nikdy neopustia váš počítač. | Spúšťa model, ktorý poháňa agenta. |
| OpenHands Agent Server | Backendový proces, ktorý vykonáva konverzácie agenta OpenHands. | Hostí agenta, jeho LLM profil a jeho MCP servery. |
| Agent Canvas | Lokálna riadiaca rovina pre OpenHands, ktorá spúšťa Agent Server a rozhranie na kontrolu behov agenta. | Spúšťa backendy a poskytuje API, ktoré voláte. |
| MCP server | Server Model Context Protocol, ktorý dáva agentovi nástroje pre externú službu, ako je GitHub alebo Slack. | Umožňuje agentovi čítať GitHub a zapisovať do Slacku. |
| Automatizácia OpenHands | Naplánovaná alebo udalosťou spúšťaná konverzácia agenta, ktorá získava kontext, uvažuje nad ním a niekam zapíše výsledok. | Súhrn z GitHubu do Slacku, ktorý tu vytvoríte. |

<!-- @device:stx,krk -->
> [!NOTE]
> Pracovné postupy s kódovacím agentom profitujú z väčšieho modelu a väčšieho
> kontextového okna. Použite aspoň 32 GB systémovej pamäte a pri väčších
> modeloch GGUF uprednostnite 64 GB alebo viac.
<!-- @device:end -->

## Predpoklady

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Budete potrebovať:

- Lemonade Server nainštalovaný podľa štandardného
  [sprievodcu inštaláciou Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 alebo novší a `npm`, ktoré sa použijú na inštaláciu publikovaného
  CLI nástroja Agent Canvas a na spúšťanie MCP serverov pomocou `npx`.
- Nedávno publikovaný balík `@openhands/agent-canvas` so schémou riadeným
  nastavením agenta, `LLMSummarizingCondenserSettings.max_tokens`
  a podporou `custom_tokenizer` pre LLM.
- Balík Python `transformers` dostupný v prostredí Agent Server.
  Je potrebný na počítanie tokenov chatovej šablóny, keď je nastavené
  `custom_tokenizer`.
- Token GitHub s právom na čítanie repozitára, ktorý chcete zhrnúť.
- Bot token Slacku (`xoxb-...`) s prístupom `chat:write` a právom na čítanie
  kanálov.
- ID tímu Slack (`T...`).
- ID kanála Slack (`C...`), kam sa má súhrn uverejniť.

Pred testovaním automatizácie pozvite aplikáciu Slack do cieľového kanála.

## Premenné použité v tomto playbooku

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

Nasledujúce hodnoty sa v ďalších krokoch zadávajú do používateľského
rozhrania Agent Canvas. Nastavte si ich tu, aby ste ich mohli neskôr
skopírovať:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Pre `GITHUB_REPO_FILTER` použite explicitnú hodnotu vo tvare `owner/repo`.
Široké zástupné znaky pre celú organizáciu môžu vrátiť pre lokálne modely
príliš veľa MCP kontextu.

## 1. Spustenie Lemonade Server

Spustite model z CLI nástroja Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade sprístupňuje rozhranie API kompatibilné s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

Voliteľné: ak Agent Canvas alebo spúšťač automatizácie nie sú na tom istom
počítači, publikujte koncový bod Lemonade cez zabezpečený tunel a ako
základnú adresu URL LLM použite adresu HTTPS:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Overenie lokálneho modelu

Overte, že Lemonade dokáže obsluhovať zvolený model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Potom odošlite malú chatovú požiadavku:

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

Ak sa vráti pole `choices`, Lemonade je pripravený pre Agent Canvas.
## 3. Spustenie Agent Canvas

Nainštalujte publikovaný balík Agent Canvas a spustite celý stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ak globálna inštalácia npm zlyhá s chybou oprávnení, pozrite si nižšie
uvedenú položku o riešení problémov s oprávneniami npm.

Agent Canvas sa v predvolenom nastavení spúšťa na `http://localhost:8000`.
Otvorte túto adresu URL vo svojom prehliadači. Predvolený lokálny backend by
sa mal na domovskej obrazovke zobrazovať ako zdravý.

Príkaz `agent-canvas` spúšťa agent server, automatizačný backend a webový
frontend spoločne. Na lokálne spustenie OpenHands potrebujete iba tento jeden
príkaz. Zvyšok tejto príručky konfiguruje všetko prostredníctvom rozhrania
Agent Canvas vo vašom prehliadači.

## 4. Konfigurácia lokálneho LLM v rozhraní

Pri prvom spustení Agent Canvas otvorí úvodný (onboarding) proces. V tomto
procese:

1. Ponechajte **OpenHands** vybraté ako agenta a kliknite na **Next**.
2. Na obrazovke **Set up your LLM** vyberte **Advanced**.
3. Ponechajte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na hodnotu `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do poľa **API Key** zadajte akýkoľvek neprázdny zástupný reťazec, napríklad
   `lemonade-local`. Lemonade nevyžaduje skutočný kľúč, ale klient OpenHands
   potrebuje nejakú hodnotu na odoslanie.

Polia pripojenia by mali vyzerať takto. Pole API kľúča je v rozhraní
maskované.

![Prvotné nastavenie LLM Advanced v Agent Canvas s modelom Lemonade a lokálnou základnou adresou URL](assets/01-llm-advanced-settings.png)

Následne vyberte **All** a nastavte ďalšie polia pre lokálny model:

1. Prejdite k položke **Custom Tokenizer** a nastavte ju na
   `Qwen/Qwen3.6-35B-A3B`.
2. Prejdite k položke **LiteLLM Extra Body** a nastavte ju na
   `{"enable_thinking": true}`.
3. Kliknite na **Next**.

![Karta LLM All pri prvom použití Agent Canvas s vlastným tokenizátorom Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta LLM All pri prvom použití Agent Canvas s nakonfigurovaným LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavenia LLM by mali zobrazovať:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` hovorí LiteLLM, aby voči koncovému bodu Lemonade použil
formátovanie požiadaviek kompatibilné s OpenAI. Vlastný tokenizátor je
pôvodný tokenizátor Hugging Face pre model GGUF; umožňuje OpenHands počítať
rovnaké tokeny chat-šablóny, aké vidí lokálny server modelu. Aktuálny
formulár LLM pri prvom použití nezobrazuje nastavenia condenser. Ak vaša
zostava Agent Canvas neskôr zobrazuje nastavenia condenser v časti
**Settings > LLM**, použite `llm_summarizing` a nastavte maximálny počet
tokenov pod kontextovým oknom Lemonade, napríklad `56000`.

## 5. Inštalácia MCP serverov pre GitHub a Slack

V rozhraní Agent Canvas otvorte **Customize** (alebo **Settings > MCP**) a
pridajte MCP servery, ktoré agentovi poskytnú nástroje pre GitHub a Slack.
Hodnoty tokenov sa odosielajú iba na váš lokálny Agent Server a sú uložené ako
šifrované nastavenia.

### MCP server pre GitHub

Pridajte nový MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš GitHub token |

Použite GitHub token s prístupom na čítanie do repozitára, ktorý chcete
zhrnúť.

### MCP server pre Slack

Pridajte druhý MCP server s týmito nastaveniami:

| Pole | Hodnota |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vášho kanálu pre súhrny |

Nastavte `SLACK_CHANNEL_IDS` na ID kanála pre súhrny (rovnaká hodnota ako
`SLACK_DIGEST_CHANNEL`), aby agent nemusel prechádzať každý kanál v Slacku.

Po pridaní oboch serverov použite tlačidlo **Test** pri každom z nich, aby ste
potvrdili, že sa pripája a ponúka nástroje. Server GitHub by mal vypísať
nástroje pre GitHub a server Slack by mal vypísať nástroje pre Slack.

![Stránka MCP v Agent Canvas s nainštalovanými servermi GitHub a Slack](assets/04-mcp-servers-installed.png)

## 6. Vytvorenie automatizácie súhrnu

V rozhraní Agent Canvas otvorte stránku **Automations** a vytvorte novú
automatizáciu:

1. Zvoľte **Create automation** a vyberte typ **Prompt preset**.
2. Nastavte **Name** na `GitHub Development Digest to Slack`.
3. Nastavte **Prompt** na nasledujúci text, pričom zástupné hodnoty
   repozitára a kanála nahraďte vlastnými hodnotami:

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

4. Nastavte **Trigger** na **Cron** s plánom `0 9 * * 1-5` (9:00 ráno v
   pracovné dni) a nastavte **Timezone** na vaše časové pásmo, napríklad
   `America/New_York`.
5. Nastavte **Timeout** na `900` sekúnd.
6. Uložte automatizáciu.

Stránka s podrobnosťami automatizácie zobrazuje novú automatizáciu s jej
cron spúšťačom a vygenerovaným vstupným bodom typu prompt preset.

![Podrobnosti automatizácie v Agent Canvas po vytvorení](assets/05-automation-created.png)
## 7. Otestovanie automatizácie

Na stránke s podrobnosťami automatizácie v používateľskom rozhraní Agent Canvas:

1. Kliknite na **Run now** (alebo **Dispatch**) na okamžité jednorazové spustenie automatizácie.
2. Sledujte zoznam behov na tej istej stránke. Najnovší beh by mal prejsť do stavu
   `COMPLETED`.
3. Otvorte cieľový kanál Slack. Mal by obsahovať vygenerovaný súhrn.

Nemusíte čakať na spustenie podľa plánu cron — **Run now** spustí beh
na požiadanie, aby ste si mohli overiť, či prompt, pripojenia MCP a
uverejňovanie na Slacku fungujú, ešte pred spoľahnutím sa na plánované spúšťanie.

![Automatizácia v Agent Canvas úspešne dokončila beh](assets/06-automation-run-completed.png)

![Kanál Slack zobrazujúci vygenerovaný súhrn OpenHands](assets/07-slackbot-message.png)

## Riešenie problémov

- **Lemonade nefunguje:** reštartujte ho príkazom
  `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a potom znova spustite kontrolu
  stavu.
- **`npm install -g` zlyhá s chybou oprávnení:** v systéme Linux alebo WSL
  nakonfigurujte globálny adresár npm vo vlastníctve používateľa, pridajte ho
  do štartovacieho súboru shellu a potom znova nainštalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Ak používate `zsh`, pridajte rovnaký riadok `export PATH=...` do súboru
  `~/.zshrc` namiesto `~/.bashrc`.
- **Agent Canvas odmietne nastavenia LLM po nastavení `custom_tokenizer`:**
  nainštalujte `transformers` do prostredia Python servera Agent Server,
  v prípade potreby reštartujte Agent Canvas a skúste nastavenia LLM znova
  uložiť. OpenHands vyžaduje knižnicu Transformers na načítanie šablóny chatu
  tokenizéra, keď je nastavený `custom_tokenizer`.
- **Agent Canvas sa nemôže pripojiť k Lemonade:** overte
  `curl -fsS "${LEMONADE_BASE_URL}/health"` a skontrolujte, či základná URL
  adresa zadaná vo formulári LLM pri prvom použití alebo v časti
  **Settings > LLM** zodpovedá spustenému lokálnemu koncovému bodu alebo
  HTTPS tunelu.
- **Nastavenia LLM sa neuložili:** uistite sa, že ste po zadaní hodnôt klikli
  na **Next**. Znova otvorte **Settings > LLM** a overte, či sa hodnoty
  zachovali.
- **GitHub MCP nevidí súkromné repozitáre:** overte, že token GitHub má
  prístup na čítanie k cieľovému repozitáru a že tlačidlo **Test** pre MCP
  v časti **Customize** zobrazuje nástroje GitHub.
- **Slack dokáže čítať kanály, ale nedokáže uverejňovať príspevky:** pozvite
  aplikáciu Slack do cieľového kanála a overte, či má bot oprávnenie
  `chat:write`.
- **Automatizácia vypisuje príliš veľa kanálov Slack:** použite ID kanála
  Slack a nastavte `SLACK_CHANNEL_IDS` na serveri Slack MCP v časti
  **Customize**.
- **Beh automatizácie zlyhá alebo prekročí kontext:** overte, že Lemonade bol
  spustený s `ctx_size=65536`, že LLM OpenHands má nastavený
  `custom_tokenizer`, a použite konkrétny repozitár s výsledkami GitHub
  obmedzenými na 3 až 5 položiek. Ak vaša zostava Agent Canvas obsahuje
  nastavenia kondenzátora, nastavte maximálny počet tokenov kondenzátora pod
  hranicu kontextového okna Lemonade.

## Ďalšie kroky

- Pridajte týždenný súhrn zameraný len na vydania.
- Pridajte automatizáciu spúšťanú udalosťami GitHub pre rýchlejšie upozornenia
  na PR alebo push.
- Presmerujte rovnaký súhrn do Notion, Linear alebo iného nástroja
  podporovaného MCP.

## Zdroje

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentácia Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitár rozšírení OpenHands](https://github.com/OpenHands/extensions)
- [Servery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Balík Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)