<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Áttekintés

A fejlesztők sok időt töltenek kis, ismétlődő ciklusokkal: címkézett pull requestek átnézésével, GitHub megjegyzésekre való válaszadással, új problémák (issue) triázsával, Slack-szálak standup jegyzetekké vagy incidens-utókövetéssé alakításával, valamint a kiadási vagy kutatási jelzések nyomon követésével. Minden ciklus ismerős, de mégis megítélést igényel: össze kell gyűjteni a megfelelő kontextust, el kell dönteni, mi számít, és egyértelmű frissítést kell közzétenni ott, ahol a csapat már dolgozik.

Az [OpenHands automatizálások](https://docs.openhands.dev/openhands/usage/automations/overview)
ezeket a ciklusokat ütemezett vagy eseményindított ágens-beszélgetésekké alakítják: olyan futásokká, ahol egy AI szoftverügynök kontextust olvashat, eszközöket hívhat meg, és frissítést állíthat elő.
Az OpenHands extension katalógusban található megosztott automatizálási sablonok ezt a mintát követik GitHub pull request átnézéshez, repository monitorozáshoz, Linear
issue triázshoz, incidens-utóelemzéshez, Slack standup összefoglalókhoz és kutatási
összefoglalókhoz: egy automatizálás felébred, konfigurált integrációkat, például GitHub-ot vagy
Slacket használ a kontextus lekéréséhez, ezt a kontextust egy nagy nyelvi modellel (LLM) elemzi, majd visszaírja az eredményt.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) a helyi vezérlősík
ezen automatizálások felépítéséhez és teszteléséhez. Ebben a playbookban egy OpenHands Agent Servert futtat, azt a háttérfolyamatot, amely az ágens-beszélgetéseket végrehajtja,
és összeköti az ágenst külső szolgáltatásokkal, mint például a GitHub és a Slack.

Ahhoz, hogy a munkafolyamat az Ön AMD rendszerén maradjon, az ágens egy helyi modellel kommunikál, amelyet a Lemonade Server szolgál ki. A Lemonade ezt a modellt egy
OpenAI-kompatibilis API-n keresztül teszi elérhetővé, így az Agent Canvas úgy tudja konfigurálni, mintha egy távoli
OpenAI-stílusú végpont lenne, miközben a modell, a prompt és a munkafolyamat kontextusa helyben marad.

Ebben a playbookban egy konkrét automatizálást fogsz felépíteni: egy ütemezett
GitHub-ból Slackbe irányuló fejlesztési összefoglalót (digest). Ez GitHub-ot használ a legutóbbi repository tevékenység vizsgálatához, Slacket az összefoglaló közzétételéhez, Agent Canvas API-hívásokat az automatizálás konfigurálásához és
teszteléséhez, valamint Lemonade-t az LLM helyi futtatásához.

![Architektúra diagram, amely a GitHub MCP-t, az OpenHands automatizálást, a Lemonade Servert és a Slack MCP-t mutatja](assets/00-architecture-overview.png)

## Amit meg fogsz tanulni

- Hogyan indítsd el a Lemonade Servert, és hogyan ellenőrizd, hogy egy helyi modell válaszol-e a chat kérésekre
- Hogyan indítsd el az Agent Canvast, és hogyan irányítsd az Agent Serverét egy helyi LLM-re
- Hogyan telepíts GitHub és Slack Model Context Protocol (MCP) szervereket az
  Agent Server API-n keresztül
- Hogyan hozz létre és indíts el egy ütemezett OpenHands automatizálást, amely fejlesztési összefoglalót tesz közzé a Slackben
- Hogyan hárítsd el a leggyakoribb helyi modellel és automatizálással kapcsolatos hibákat

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe a playbookba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az Ön adatai soha nem hagyják el a gépét. | Futtatja az ágenst hajtó modellt. |
| OpenHands Agent Server | A háttérfolyamat, amely az OpenHands ágens-beszélgetéseket végrehajtja. | Otthont ad az ágensnek, annak LLM-profiljának és MCP-szervereinek. |
| Agent Canvas | Az OpenHands helyi vezérlősíkja, amely futtatja az Agent Servert és egy felhasználói felületet az ágensfutások vizsgálatához. | Elindítja a háttérrendszereket, és biztosítja az API-t, amelyet meghívsz. |
| MCP szerver | Egy Model Context Protocol szerver, amely eszközöket ad egy ágensnek egy külső szolgáltatáshoz, például GitHub-hoz vagy Slackhez. | Lehetővé teszi az ágens számára, hogy olvasson GitHub-ból és írjon Slackbe. |
| OpenHands automatizálás | Egy ütemezett vagy eseményindított ágens-beszélgetés, amely kontextust kér le, azon elemzést végez, és valahová eredményt ír. | Az itt felépített GitHub-Slack összefoglaló. |

<!-- @device:stx,krk -->
> [!NOTE]
> A kódolóágens (coding-agent) munkafolyamatok profitálnak egy nagyobb modellből és kontextusablakból. Használj
> legalább 32 GB rendszermemóriát, és nagyobb GGUF modellek esetén részesítsd előnyben a 64 GB-ot vagy annál többet.
<!-- @device:end -->

## Előfeltételek

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Szükséged lesz:

- A Lemonade Server telepítve, a szabványos
  [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) szerint.
- Node.js 22.12 vagy újabb és `npm`, amelyekkel telepítheted a publikált Agent Canvas
  CLI-t, és futtathatod az MCP szervereket `npx` segítségével.
- Egy friss, publikált `@openhands/agent-canvas` csomag, séma-alapú ágens-beállításokkal, `LLMSummarizingCondenserSettings.max_tokens`-szel,
  és LLM `custom_tokenizer` támogatással.
- A Python `transformers` csomag elérhető legyen az Agent Server környezetében.
  Ez szükséges a chat-sablon tokenszámláláshoz, ha a `custom_tokenizer`
  be van állítva.
- Egy GitHub token, olvasási hozzáféréssel az összefoglalni kívánt repositoryhoz.
- Egy Slack bot token (`xoxb-...`), `chat:write` és csatorna-olvasási hozzáféréssel.
- Egy Slack team ID (`T...`).
- Egy Slack csatorna ID (`C...`), ahová az összefoglalót közzé kell tenni.

Hívd meg a Slack alkalmazást a célcsatornába, mielőtt tesztelnéd az automatizálást.

## Az ebben a playbookban használt változók

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

A következő értékeket a későbbi lépésekben adod meg az Agent Canvas felhasználói felületén. Állítsd be itt őket, hogy később be tudd másolni:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Használj egyértelmű `owner/repo` értéket a `GITHUB_REPO_FILTER` számára. A túl tág szervezeti
helyettesítő karakterek (wildcard) túl sok MCP kontextust adhatnak vissza a helyi modellek számára.

## 1. A Lemonade Server elindítása

Indítsd el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé itt:

```text
http://127.0.0.1:13305/api/v1
```

Opcionális: ha az Agent Canvas vagy az automatizálás-futtató nem ugyanazon a gépen van, akkor
tedd elérhetővé a Lemonade végpontot egy biztonságos alagúton keresztül, és használd a HTTPS URL-t
LLM alap URL-ként:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. A helyi modell ellenőrzése

Erősítsd meg, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Ezután küldj egy kis chat kérést:

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

Ha ez egy `choices` tömböt ad vissza, a Lemonade készen áll az Agent Canvas számára.
## 3. Az Agent Canvas indítása

Telepítse a publikált Agent Canvas csomagot, és indítsa el a teljes stacket:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ha a globális npm install jogosultsági hiba miatt sikertelen, tekintse meg
az alábbi npm jogosultsági hibaelhárítási bejegyzést.

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyissa meg ezt az URL-t a böngészőjében. Az alapértelmezett helyi backendnek
egészségesként kell megjelennie a kezdőképernyőn.

Az `agent-canvas` parancs egyszerre indítja az agent szervert, az automatizálási
backendet és a webes frontendet. Csak erre az egyetlen parancsra van szükség
az OpenHands helyi futtatásához. A jelen útmutató további része az Agent
Canvas felhasználói felületén keresztül konfigurál mindent a böngészőjében.

## 4. A helyi LLM konfigurálása a felhasználói felületen

Az első indításkor az Agent Canvas egy bevezető folyamatot nyit meg. Ebben a
folyamatban:

1. Hagyja kiválasztva az **OpenHands** ügynököt, majd kattintson a **Next** gombra.
2. A **Set up your LLM** oldalon válassza az **Advanced** lehetőséget.
3. Hagyja az **Authentication** beállítást **API key** értéken.
4. Állítsa be a **Custom Model** mezőt az `OPENHANDS_LLM_MODEL` értékére,
   amely `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsa be a **Base URL** mezőt a `http://127.0.0.1:13305/api/v1` értékre.
6. Az **API Key** mezőbe írjon be egy tetszőleges, nem üres helyőrzőt, például
   `lemonade-local`. A Lemonade nem igényel valódi kulcsot, de az OpenHands
   kliensnek szüksége van egy értékre a küldéshez.

A kapcsolódási mezőknek így kell kinézniük. Az API kulcs mezőt a felhasználói
felület elrejti.

![Agent Canvas első használatakor megjelenő LLM Advanced beállítások a Lemonade modellel és a helyi base URL-lel](assets/01-llm-advanced-settings.png)

Ezután válassza az **All** lehetőséget, és állítsa be a további helyi
modellre vonatkozó mezőket:

1. Görgessen a **Custom Tokenizer** mezőhöz, és állítsa be
   `Qwen/Qwen3.6-35B-A3B` értékre.
2. Görgessen a **LiteLLM Extra Body** mezőhöz, és állítsa be
   `{"enable_thinking": true}` értékre.
3. Kattintson a **Next** gombra.

![Agent Canvas első használatakor megjelenő LLM All lap a Qwen egyéni tokenizálóval](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas első használatakor megjelenő LLM All lap a beállított LiteLLM extra body értékkel](assets/03-llm-all-extra-body-settings.png)

Az LLM beállításoknak a következőket kell mutatniuk:

| Mező | Érték |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Az `openai/` előtag jelzi a LiteLLM számára, hogy OpenAI-kompatibilis
kéréskialakítást használjon a Lemonade végponttal szemben. Az egyéni
tokenizáló a GGUF modell eredeti Hugging Face tokenizálója; ez lehetővé teszi
az OpenHands számára, hogy ugyanazokat a chat-sablon tokeneket számolja, mint
amelyeket a helyi modellszerver lát. A jelenlegi első használatra szolgáló
LLM űrlap nem jeleníti meg a condenser beállításokat. Ha az Ön Agent Canvas
buildje később megjeleníti a condenser beállításokat a **Settings > LLM**
alatt, használja az `llm_summarizing` értéket, és állítsa be a maximális
tokenszámot a Lemonade kontextusablak alatt, például `56000` értékre.

## 5. A GitHub és a Slack MCP szerverek telepítése

Az Agent Canvas felhasználói felületén nyissa meg a **Customize** (vagy
**Settings > MCP**) menüpontot, hogy hozzáadja azokat az MCP szervereket,
amelyek a GitHubhoz és a Slackhez kapcsolódó eszközöket biztosítják az
ügynök számára. A tokenértékek kizárólag a helyi Agent Serverre kerülnek
elküldésre, és titkosított beállításokként kerülnek mentésre.

### GitHub MCP szerver

Adjon hozzá egy új MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = az Ön GitHub tokene |

Használjon olyan GitHub tokent, amely olvasási jogosultsággal rendelkezik
az összegzendő tárolóhoz.

### Slack MCP szerver

Adjon hozzá egy második MCP szervert a következő beállításokkal:

| Mező | Érték |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = az Ön digest csatornaazonosítója |

Állítsa be a `SLACK_CHANNEL_IDS` értéket a digest csatorna azonosítójára
(ugyanarra az értékre, mint a `SLACK_DIGEST_CHANNEL`), hogy az ügynöknek ne
kelljen az összes Slack csatornát végignéznie.

Miután mindkét szervert hozzáadta, használja a **Test** gombot mindegyiken,
hogy megerősítse a kapcsolódást és az eszközök megjelenítését. A GitHub
szervernek GitHub eszközöket kell listáznia, a Slack szervernek pedig Slack
eszközöket.

![Agent Canvas MCP oldal a telepített GitHub és Slack szerverekkel](assets/04-mcp-servers-installed.png)

## 6. A Digest automatizálás létrehozása

Az Agent Canvas felhasználói felületén nyissa meg az **Automations** oldalt,
és hozzon létre egy új automatizálást:

1. Válassza a **Create automation** lehetőséget, majd a **Prompt preset**
   típust.
2. Állítsa be a **Name** mezőt `GitHub Development Digest to Slack` értékre.
3. Állítsa be a **Prompt** mezőt a következő szövegre, a tároló- és
   csatorna-helyőrzőket az Ön értékeire cserélve:

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

4. Állítsa be a **Trigger** mezőt **Cron** értékre, `0 9 * * 1-5` ütemezéssel
   (hétköznaponta 9 órakor), és állítsa be a **Timezone** mezőt az Ön
   időzónájára, például `America/New_York` értékre.
5. Állítsa be a **Timeout** mezőt `900` másodpercre.
6. Mentse el az automatizálást.

Az automatizálás részletező oldala megjeleníti az újonnan létrehozott
automatizálást a cron triggerével és a generált prompt-preset belépési
ponttal.

![Agent Canvas automatizálás részletei a létrehozás után](assets/05-automation-created.png)
## 7. Az automatizálás tesztelése

Az Agent Canvas UI automatizálás-részletező oldaláról:

1. Kattintson a **Run now** (vagy **Dispatch**) gombra az automatizálás azonnali, egyszeri futtatásához.
2. Figyelje a futtatások listáját ugyanazon az oldalon. A legutóbbi futásnak `COMPLETED` állapotba kell kerülnie.
3. Nyissa meg a célzott Slack csatornát. Tartalmaznia kell a generált digestet.

Nem kell megvárnia, hogy a cron ütemezés elinduljon — a **Run now** igény szerint indít egy futtatást, így megerősítheti, hogy a prompt, az MCP kapcsolatok és a Slack posztolás mind működnek, mielőtt az ütemezésre hagyatkozna.

![Az Agent Canvas automatizálás futtatása sikeresen befejeződött](assets/06-automation-run-completed.png)

![A Slack csatorna, amely a generált OpenHands digestet mutatja](assets/07-slackbot-message.png)

## Hibaelhárítás

- **A Lemonade nem működik:** indítsa újra a `lemonade run "${LEMONADE_MODEL}"` paranccsal az 1. lépésben, majd futtassa újra az állapotellenőrzést.
- **Az `npm install -g` jogosultsági hibával leáll:** Linuxon vagy WSL-en állítson be egy felhasználó tulajdonában lévő globális npm könyvtárat, adja hozzá a shell indítófájljához, majd telepítse újra az Agent Canvast:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Ha `zsh`-t használ, ugyanezt az `export PATH=...` sort adja hozzá a `~/.zshrc` fájlhoz a `~/.bashrc` helyett.
- **Az Agent Canvas elutasítja az LLM beállításokat a `custom_tokenizer` megadása után:** telepítse a `transformers` csomagot az Agent Server Python környezetében, szükség esetén indítsa újra az Agent Canvast, majd próbálja meg újra menteni az LLM beállításokat. Az OpenHandsnek szüksége van a Transformersre a tokenizáló chat sablonjának betöltéséhez, ha a `custom_tokenizer` be van állítva.
- **Az Agent Canvas nem éri el a Lemonade-et:** ellenőrizze a `curl -fsS "${LEMONADE_BASE_URL}/health"` parancsot, és győződjön meg róla, hogy az első használatkor megjelenő LLM űrlapon vagy a **Settings > LLM** menüben megadott alap URL megegyezik a futó helyi végponttal vagy HTTPS alagúttal.
- **Az LLM beállítások nem mentődtek el:** győződjön meg róla, hogy az értékek megadása után a **Next** gombra kattintott. Nyissa meg újra a **Settings > LLM** menüt, hogy megerősítse, az értékek megmaradtak.
- **A GitHub MCP nem látja a privát repókat:** ellenőrizze, hogy a GitHub token olvasási hozzáféréssel rendelkezik-e a célrepóhoz, és hogy a **Customize** menüben az MCP **Test** gombja jelzi-e a GitHub eszközöket.
- **A Slack tudja olvasni a csatornákat, de nem tud posztolni:** hívja meg a Slack alkalmazást a célcsatornába, és győződjön meg róla, hogy a botnak van `chat:write` jogosultsága.
- **Az automatizálás túl sok Slack csatornát listáz:** használjon Slack csatorna azonosítót, és állítsa be a `SLACK_CHANNEL_IDS` értéket a Slack MCP szerveren a **Customize** menüben.
- **Az automatizálás futtatása sikertelen, vagy meghaladja a kontextust:** győződjön meg róla, hogy a Lemonade `ctx_size=65536` beállítással indult, hogy az OpenHands LLM-en be van állítva a `custom_tokenizer`, és használjon konkrét repót, a GitHub eredményhalmazokat 3-5 elemre korlátozva. Ha az Ön Agent Canvas buildje kínál kondenzátor-beállításokat, állítsa a kondenzátor maximális tokenszámát a Lemonade kontextusablaka alá.

## Következő lépések

- Adjon hozzá egy heti, csak kiadásokra vonatkozó digestet.
- Adjon hozzá egy GitHub eseményindítású automatizálást a gyorsabb PR- vagy push-riasztásokhoz.
- Irányítsa ugyanazt a digestet a Notionba, Linearbe vagy más MCP-alapú eszközbe.

## Erőforrások

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server dokumentáció](https://lemonade-server.ai/docs)
- [OpenHands kiterjesztések repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol szerverek](https://github.com/modelcontextprotocol/servers)
- [Slack MCP csomag](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)