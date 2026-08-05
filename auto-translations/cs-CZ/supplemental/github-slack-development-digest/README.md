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

Vývojáři tráví hodně času drobnými opakujícími se úlohami: kontrolou
označených pull requestů, odpovídáním na komentáře na GitHubu, tříděním
nových issues, přeměnou vláken ve Slacku na poznámky ze standupu nebo
následné kroky po incidentu a sledováním signálů o vydáních či výzkumu.
Každá z těchto úloh je dobře známá, přesto vyžaduje úsudek: shromáždit
správný kontext, rozhodnout, co je důležité, a zveřejnit srozumitelnou
aktualizaci tam, kde tým už pracuje.

[Automatizace OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
mění tyto opakující se úlohy na naplánované nebo událostmi spouštěné
konverzace agenta: běhy, ve kterých AI softwarový agent dokáže číst
kontext, volat nástroje a vytvořit aktualizaci. Sdílené šablony automatizací
v katalogu rozšíření OpenHands sledují tento vzor pro kontrolu pull requestů
na GitHubu, sledování repozitářů, třídění issues v Linear, retrospektivy
incidentů, souhrny standupů ve Slacku a výzkumné přehledy: automatizace se
„probudí“, pomocí nakonfigurovaných integrací, jako je GitHub nebo Slack,
načte kontext, tento kontext zpracuje pomocí velkého jazykového modelu (LLM)
a zapíše výsledek zpět.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokální řídicí
rovina pro vytváření a testování těchto automatizací. V tomto playbooku
spouští OpenHands Agent Server, backendový proces, který provádí konverzace
agenta, a propojuje agenta s externími službami, jako je GitHub a Slack.

Aby zůstal celý pracovní postup na vašem systému AMD, komunikuje agent s
lokálním modelem obsluhovaným pomocí Lemonade Server. Lemonade zpřístupňuje
tento model prostřednictvím rozhraní API kompatibilního s OpenAI, takže Agent
Canvas jej může nakonfigurovat stejně jako vzdálený koncový bod ve stylu
OpenAI, zatímco model, prompt a kontext pracovního postupu zůstávají lokální.

V tomto playbooku vytvoříte jednu konkrétní automatizaci: naplánovaný denní
přehled vývoje z GitHubu do Slacku. Ta využívá GitHub k prozkoumání nedávné
aktivity v repozitáři, Slack ke zveřejnění přehledu, volání API Agent Canvas
ke konfiguraci a testování automatizace a Lemonade ke spuštění LLM lokálně.

![Diagram architektury zobrazující GitHub MCP, automatizaci OpenHands, Lemonade Server a Slack MCP](assets/00-architecture-overview.png)

## Co se naučíte

- Jak spustit Lemonade Server a ověřit, že lokální model odpovídá na chatové požadavky
- Jak spustit Agent Canvas a nasměrovat jeho Agent Server na lokální LLM
- Jak nainstalovat servery Model Context Protocol (MCP) pro GitHub a Slack
  pomocí API Agent Serveru
- Jak vytvořit a spustit naplánovanou automatizaci OpenHands, která zveřejní
  přehled vývoje na Slacku
- Jak řešit nejčastější problémy s lokálním modelem a automatizacemi

## Základní pojmy

| Pojem | Co to je | Kde v tomto playbooku zapadá |
| --- | --- | --- |
| Lemonade Server | Lokální platforma pro obsluhu LLM postavená pro hardware AMD, která zpřístupňuje rozhraní API kompatibilní s OpenAI. Vaše data nikdy neopustí váš počítač. | Spouští model, který pohání agenta. |
| OpenHands Agent Server | Backendový proces, který provádí konverzace agenta OpenHands. | Hostuje agenta, jeho profil LLM a jeho servery MCP. |
| Agent Canvas | Lokální řídicí rovina pro OpenHands, která spouští Agent Server a uživatelské rozhraní pro kontrolu běhů agenta. | Spouští backendy a poskytuje API, které voláte. |
| Server MCP | Server Model Context Protocol, který dává agentovi nástroje pro externí službu, jako je GitHub nebo Slack. | Umožňuje agentovi číst GitHub a zapisovat do Slacku. |
| Automatizace OpenHands | Naplánovaná nebo událostmi spouštěná konverzace agenta, která načte kontext, zpracuje ho a někam zapíše výsledek. | Přehled z GitHubu do Slacku, který zde vytvoříte. |

<!-- @device:stx,krk -->
> [!NOTE]
> Pracovní postupy s kódovacím agentem těží z většího modelu a delšího
> kontextového okna. Použijte alespoň 32 GB systémové paměti a pro větší
> modely GGUF upřednostněte 64 GB nebo více.
<!-- @device:end -->

## Požadavky

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Budete potřebovat:

- Lemonade Server nainstalovaný podle standardního
  [instalačního průvodce Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 nebo novější a `npm`, které se používají k instalaci
  publikovaného CLI Agent Canvas a ke spouštění MCP serverů pomocí `npx`.
- Nedávno publikovaný balíček `@openhands/agent-canvas` se schématem řízeným
  nastavením agenta, s podporou `LLMSummarizingCondenserSettings.max_tokens`
  a podporou `custom_tokenizer` pro LLM.
- Balíček Pythonu `transformers` dostupný v prostředí Agent Serveru. Je
  vyžadován pro počítání tokenů podle šablony chatu, pokud je nastaveno
  `custom_tokenizer`.
- Token GitHubu s právem čtení k repozitáři, který chcete shrnout.
- Bot token Slacku (`xoxb-...`) s oprávněním `chat:write` a čtením kanálů.
- ID týmu Slacku (`T...`).
- ID kanálu Slacku (`C...`), kam má být přehled zveřejněn.

Než automatizaci otestujete, pozvěte aplikaci Slacku do cílového kanálu.

## Proměnné použité v tomto playbooku

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

Následující hodnoty se v dalších krocích zadávají do uživatelského rozhraní
Agent Canvas. Nastavte si je zde, abyste je odtud mohli zkopírovat:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Pro `GITHUB_REPO_FILTER` použijte explicitní hodnotu `owner/repo`. Široké
zástupné znaky pro celou organizaci mohou pro lokální modely vrátit příliš
mnoho kontextu MCP.

## 1. Spuštění Lemonade Server

Spusťte model z CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade zpřístupňuje rozhraní API kompatibilní s OpenAI na adrese:

```text
http://127.0.0.1:13305/api/v1
```

Volitelně: pokud Agent Canvas nebo spouštěč automatizací neběží na stejném
počítači, zveřejněte koncový bod Lemonade prostřednictvím zabezpečeného
tunelu a jako základní URL adresu LLM použijte adresu URL HTTPS:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Ověření lokálního modelu

Ověřte, že Lemonade dokáže obsloužit vybraný model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Poté odešlete malý chatový požadavek:

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

Pokud se vrátí pole `choices`, je Lemonade připraven pro Agent Canvas.
## 3. Spuštění Agent Canvas

Nainstalujte publikovaný balíček Agent Canvas a spusťte celý stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Pokud globální instalace npm selže s chybou oprávnění, podívejte se na
níže uvedenou položku o řešení problémů s oprávněními npm.

Ve výchozím nastavení se Agent Canvas spustí na `http://localhost:8000`. Otevřete tuto adresu URL v
prohlížeči. Výchozí lokální backend by se měl na domovské obrazovce zobrazovat jako zdravý.

Příkaz `agent-canvas` spustí agent server, automatizační backend a
webový frontend společně. K lokálnímu spuštění OpenHands potřebujete pouze
tento jeden příkaz. Zbytek této příručky konfiguruje vše prostřednictvím uživatelského
rozhraní Agent Canvas v prohlížeči.

## 4. Konfigurace lokálního LLM v uživatelském rozhraní

Při prvním spuštění otevře Agent Canvas úvodní proces (onboarding). V tomto procesu:

1. Ponechte vybraného agenta **OpenHands** a klikněte na **Next**.
2. Na obrazovce **Set up your LLM** vyberte **Advanced**.
3. Ponechte **Authentication** nastavené na **API key**.
4. Nastavte **Custom Model** na hodnotu proměnné `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavte **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Do pole **API Key** zadejte jakoukoli neprázdnou zástupnou hodnotu, například `lemonade-local`.
   Lemonade nevyžaduje skutečný klíč, ale klient OpenHands potřebuje nějakou hodnotu
   k odeslání.

Pole pro připojení by měla vypadat takto. Pole API klíče je v uživatelském rozhraní maskováno.

![Pokročilá nastavení LLM při prvním spuštění Agent Canvas s modelem Lemonade a lokální základní adresou URL](assets/01-llm-advanced-settings.png)

Poté vyberte **All** a nastavte další pole pro lokální model:

1. Přejděte na **Custom Tokenizer** a nastavte jej na `Qwen/Qwen3.6-35B-A3B`.
2. Přejděte na **LiteLLM Extra Body** a nastavte jej na
   `{"enable_thinking": true}`.
3. Klikněte na **Next**.

![Karta All nastavení LLM při prvním spuštění Agent Canvas s vlastním tokenizerem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Karta All nastavení LLM při prvním spuštění Agent Canvas s nakonfigurovaným extra body pro LiteLLM](assets/03-llm-all-extra-body-settings.png)

Nastavení LLM by měla zobrazovat:

| Pole | Hodnota |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Předpona `openai/` říká LiteLLM, aby proti koncovému bodu Lemonade použil
formátování požadavků kompatibilní s OpenAI. Vlastní tokenizer je původní
tokenizer Hugging Face pro model GGUF; umožňuje OpenHands počítat stejné
tokeny chat šablony (chat-template), jaké vidí lokální server modelu. Aktuální formulář LLM
pro první spuštění nezobrazuje nastavení condenseru. Pokud vaše sestavení Agent Canvas
později zobrazuje nastavení condenseru v části **Settings > LLM**, použijte `llm_summarizing` a
nastavte maximální počet tokenů pod hranicí kontextového okna Lemonade, například `56000`.

## 5. Instalace MCP serverů pro GitHub a Slack

V uživatelském rozhraní Agent Canvas otevřete **Customize** (nebo **Settings > MCP**) a přidejte
MCP servery, které agentovi poskytnou nástroje pro GitHub a Slack. Hodnoty tokenů
se odesílají pouze na váš lokální Agent Server a jsou ukládány jako zašifrovaná nastavení.

### MCP server pro GitHub

Přidejte nový MCP server s těmito nastaveními:

| Pole | Hodnota |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = váš GitHub token |

Použijte GitHub token s právem čtení k repozitáři, který chcete shrnout.

### MCP server pro Slack

Přidejte druhý MCP server s těmito nastaveními:

| Pole | Hodnota |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašeho kanálu pro souhrn |

Nastavte `SLACK_CHANNEL_IDS` na ID kanálu pro souhrn (stejnou hodnotu jako
`SLACK_DIGEST_CHANNEL`), aby agent nemusel procházet každý kanál
Slacku.

Po přidání obou serverů použijte u každého z nich tlačítko **Test**, abyste ověřili,
že se připojí a nabídne nástroje. Server GitHub by měl vypsat nástroje GitHub a
server Slack by měl vypsat nástroje Slacku.

![Stránka MCP v Agent Canvas s nainstalovanými servery GitHub a Slack](assets/04-mcp-servers-installed.png)

## 6. Vytvoření automatizace souhrnu

V uživatelském rozhraní Agent Canvas otevřete stránku **Automations** a vytvořte novou
automatizaci:

1. Zvolte **Create automation** a vyberte typ **Prompt preset**.
2. Nastavte **Name** na `GitHub Development Digest to Slack`.
3. Nastavte **Prompt** na následující text, přičemž zástupné hodnoty repozitáře a
   kanálu nahraďte svými hodnotami:

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

4. Nastavte **Trigger** na **Cron** s plánem `0 9 * * 1-5` (9:00 ve
   všední dny) a nastavte **Timezone** na vaše časové pásmo, například
   `America/New_York`.
5. Nastavte **Timeout** na `900` sekund.
6. Uložte automatizaci.

Stránka s podrobnostmi automatizace zobrazuje novou automatizaci s jejím cron triggerem a
vygenerovaným vstupním bodem typu prompt preset.

![Podrobnosti automatizace v Agent Canvas po vytvoření](assets/05-automation-created.png)
## 7. Otestujte automatizaci

Na stránce s podrobnostmi automatizace v uživatelském rozhraní Agent Canvas:

1. Klikněte na **Run now** (nebo **Dispatch**) a spusťte automatizaci jednou okamžitě.
2. Sledujte seznam běhů na stejné stránce. Nejnovější běh by měl přejít do stavu
   `COMPLETED`.
3. Otevřete cílový kanál Slack. Měl by obsahovat vygenerovaný digest.

Není nutné čekat na spuštění podle plánu cron – **Run now** spustí
běh na vyžádání, takže si můžete ověřit, že prompt, připojení MCP a odesílání
na Slack fungují ještě předtím, než se spolehnete na plánovač.

![Automatizace v Agent Canvas byla úspěšně spuštěna](assets/06-automation-run-completed.png)

![Slackový kanál zobrazující vygenerovaný digest OpenHands](assets/07-slackbot-message.png)

## Řešení potíží

- **Lemonade neběží:** restartujte ho příkazem
  `lemonade run "${LEMONADE_MODEL}"` z kroku 1 a poté znovu spusťte kontrolu
  stavu.
- **Příkaz `npm install -g` selže s chybou oprávnění:** v systému Linux nebo WSL
  nastavte globální adresář npm vlastněný uživatelem, přidejte ho do
  spouštěcího souboru shellu a poté znovu nainstalujte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Pokud používáte `zsh`, přidejte stejný řádek `export PATH=...` místo
  do `~/.bashrc` do souboru `~/.zshrc`.
- **Agent Canvas po nastavení `custom_tokenizer` odmítne nastavení LLM:**
  nainstalujte `transformers` do prostředí Python serveru Agent Server, v případě
  potřeby restartujte Agent Canvas a zkuste nastavení LLM znovu uložit. OpenHands
  vyžaduje Transformers k načtení šablony chatu tokenizéru, pokud je nastaveno
  `custom_tokenizer`.
- **Agent Canvas se nemůže připojit k Lemonade:** ověřte
  `curl -fsS "${LEMONADE_BASE_URL}/health"` a potvrďte, že základní URL zadaná
  ve formuláři LLM při prvním použití nebo v **Settings > LLM** odpovídá
  běžícímu místnímu koncovému bodu nebo tunelu HTTPS.
- **Nastavení LLM se neuložilo:** ujistěte se, že jste po zadání hodnot klikli
  na **Next**. Znovu otevřete **Settings > LLM** a ověřte, že se hodnoty
  uložily.
- **GitHub MCP nevidí soukromé repozitáře:** ověřte, že token GitHub má
  přístup ke čtení cílového repozitáře a že tlačítko **Test** MCP v sekci
  **Customize** hlásí dostupné nástroje GitHub.
- **Slack umí číst kanály, ale nemůže do nich zveřejňovat příspěvky:** pozvěte
  aplikaci Slack do cílového kanálu a ověřte, že bot má oprávnění `chat:write`.
- **Automatizace zobrazuje příliš mnoho slackových kanálů:** použijte ID
  kanálu Slack a nastavte `SLACK_CHANNEL_IDS` na serveru MCP pro Slack v sekci
  **Customize**.
- **Běh automatizace selže nebo překročí kontext:** ověřte, že Lemonade byl
  spuštěn s `ctx_size=65536`, ověřte, že má LLM OpenHands nastaveno
  `custom_tokenizer`, a použijte konkrétní repozitář s výsledky GitHubu
  omezenými na 3 až 5 položek. Pokud vaše sestavení Agent Canvas nabízí
  nastavení condenseru, nastavte maximální počet tokenů condenseru pod
  velikost kontextového okna Lemonade.

## Další kroky

- Přidejte týdenní digest zaměřený pouze na vydání.
- Přidejte automatizaci spouštěnou událostmi GitHubu pro rychlejší upozornění
  na PR nebo push.
- Nasměrujte stejný digest do Notionu, Linearu nebo jiného nástroje
  založeného na MCP.

## Zdroje

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentace Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitář rozšíření OpenHands](https://github.com/OpenHands/extensions)
- [Servery Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Balíček Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)