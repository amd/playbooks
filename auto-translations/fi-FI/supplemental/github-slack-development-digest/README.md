<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Yleiskatsaus

Kehittäjät käyttävät paljon aikaa pieniin, toistuviin silmukoihin: merkittyjen pull requestien tarkistamiseen, GitHub-kommentteihin vastaamiseen, uusien ongelmien (issue) luokitteluun, Slack-keskusteluketjujen muuttamiseen standup-muistiinpanoiksi tai häiriön jälkitoimiksi sekä julkaisu- tai tutkimussignaalien seurantaan. Jokainen silmukka on tuttu, mutta se vaatii silti harkintaa: oikean kontekstin kerääminen, sen päättäminen, mikä on olennaista, ja selkeän päivityksen julkaiseminen paikassa, jossa tiimi jo työskentelee.

[OpenHands-automaatiot](https://docs.openhands.dev/openhands/usage/automations/overview)
muuttavat nämä silmukat ajastetuiksi tai tapahtumapohjaisiksi agenttikeskusteluiksi: ajoiksi, joissa tekoälypohjainen ohjelmistoagentti voi lukea kontekstia, kutsua työkaluja ja tuottaa päivityksen. OpenHands-laajennuskatalogin jaetut automaatiomallit noudattavat tätä mallia GitHubin pull request -tarkistuksessa, repositorion valvonnassa, Linear-ongelmien luokittelussa, häiriöiden jälkiarvioinneissa, Slack-standup-yhteenvedoissa ja tutkimusraporteissa: automaatio herää, käyttää määritettyjä integraatioita, kuten GitHubia tai Slackia, kontekstin hakemiseen, päättelee tämän kontekstin pohjalta suurella kielimallilla (LLM) ja kirjoittaa tuloksen takaisin.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) on paikallinen ohjaustaso näiden automaatioiden rakentamiseen ja testaamiseen. Tässä ohjekirjassa se ajaa OpenHands Agent Serveriä, taustaprosessia, joka suorittaa agenttikeskustelut, ja yhdistää agentin ulkoisiin palveluihin, kuten GitHubiin ja Slackiin.

Jotta työnkulku pysyy omalla AMD-järjestelmälläsi, agentti keskustelee paikallisen mallin kanssa, jota Lemonade Server tarjoaa. Lemonade tuo mallin saataville OpenAI-yhteensopivan API:n kautta, joten Agent Canvas voi määrittää sen kuin etä-OpenAI-tyylisen päätepisteen, kun taas malli, kehote ja työnkulun konteksti pysyvät paikallisina.

Tässä ohjekirjassa rakennat yhden konkreettisen automaation: ajastetun GitHubista Slackiin toimitettavan kehitysyhteenvedon. Se käyttää GitHubia repositorion viimeaikaisen toiminnan tarkasteluun, Slackia yhteenvedon julkaisemiseen, Agent Canvasin API-kutsuja automaation määrittämiseen ja testaamiseen sekä Lemonadea LLM:n ajamiseen paikallisesti.

![Arkkitehtuurikaavio, joka näyttää GitHub MCP:n, OpenHands-automaation, Lemonade Serverin ja Slack MCP:n](assets/00-architecture-overview.png)

## Mitä opit

- Kuinka käynnistää Lemonade Server ja varmistaa, että paikallinen malli vastaa keskustelupyyntöihin
- Kuinka käynnistää Agent Canvas ja ohjata sen Agent Server paikalliseen LLM:ään
- Kuinka asentaa GitHub- ja Slack-Model Context Protocol (MCP) -palvelimet Agent Server -API:n kautta
- Kuinka luoda ja käynnistää ajastettu OpenHands-automaatio, joka julkaisee kehitysyhteenvedon Slackiin
- Kuinka vianmäärittää yleisimpiä paikallisen mallin ja automaation virheitä

## Peruskäsitteet

| Käsite | Mitä se on | Missä se sijoittuu tähän ohjekirjaan |
| --- | --- | --- |
| Lemonade Server | Paikallinen LLM-tarjoiluympäristö, joka on rakennettu AMD-laitteistolle ja tuo saataville OpenAI-yhteensopivan API:n. Tietosi eivät koskaan poistu koneeltasi. | Ajaa mallia, joka toimii agentin taustavoimana. |
| OpenHands Agent Server | Taustaprosessi, joka suorittaa OpenHands-agenttikeskustelut. | Isännöi agenttia, sen LLM-profiilia ja sen MCP-palvelimia. |
| Agent Canvas | Paikallinen ohjaustaso OpenHandsille, joka ajaa Agent Serveriä ja käyttöliittymää agenttiajojen tarkasteluun. | Käynnistää taustajärjestelmät ja tarjoaa API:n, jota kutsut. |
| MCP-palvelin | Model Context Protocol -palvelin, joka antaa agentille työkaluja ulkoiseen palveluun, kuten GitHubiin tai Slackiin. | Antaa agentin lukea GitHubia ja kirjoittaa Slackiin. |
| OpenHands-automaatio | Ajastettu tai tapahtumapohjainen agenttikeskustelu, joka hakee kontekstia, päättelee sen pohjalta ja kirjoittaa tuloksen johonkin. | Tässä rakennettava GitHubista Slackiin -yhteenveto. |

<!-- @device:stx,krk -->
> [!NOTE]
> Koodausagentti-työnkulut hyötyvät suuremmasta mallista ja kontekstiikkunasta. Käytä vähintään 32 Gt järjestelmämuistia, ja suosi 64 Gt tai enemmän suuremmille GGUF-malleille.
<!-- @device:end -->

## Edellytykset

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Tarvitset:

- Lemonade Server asennettuna noudattamalla vakiomuotoista
  [Lemonade-asennusopasta](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 tai uudemman version sekä `npm`:n, joita käytetään julkaistun Agent Canvas -CLI:n asentamiseen ja MCP-palvelimien ajamiseen komennolla `npx`.
- Tuoreen julkaistun `@openhands/agent-canvas`-paketin, jossa on skeemapohjaiset agenttiasetukset, `LLMSummarizingCondenserSettings.max_tokens` sekä LLM:n `custom_tokenizer`-tuki.
- Python `transformers` -paketin, jonka on oltava saatavilla Agent Server -ympäristössä. Sitä tarvitaan chat-mallipohjan tokenlaskentaan, kun `custom_tokenizer` on asetettu.
- GitHub-tunnuksen, jolla on lukuoikeus yhteenvedettävään repositorioon.
- Slack-bottitunnuksen (`xoxb-...`), jolla on `chat:write`- ja kanavan lukuoikeudet.
- Slack-tiimitunnuksen (`T...`).
- Slack-kanavatunnuksen (`C...`), johon yhteenveto julkaistaan.

Kutsu Slack-sovellus kohdekanavaan ennen automaation testaamista.

## Tässä ohjekirjassa käytetyt muuttujat

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

Seuraavat arvot syötetään Agent Canvas -käyttöliittymään myöhemmissä vaiheissa. Aseta ne tässä, jotta voit kopioida ne myöhemmin:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Käytä yksiselitteistä `owner/repo`-arvoa kohdassa `GITHUB_REPO_FILTER`. Laajat organisaation jokerimerkit voivat palauttaa liikaa MCP-kontekstia paikallisille malleille.

## 1. Käynnistä Lemonade Server

Käynnistä malli Lemonade CLI:stä:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade tuo OpenAI-yhteensopivan API:n saataville osoitteessa:

```text
http://127.0.0.1:13305/api/v1
```

Valinnainen: jos Agent Canvas tai automaation suoritusympäristö ei ole samalla koneella, julkaise Lemonade-päätepiste suojatun tunnelin kautta ja käytä HTTPS-osoitetta LLM:n perusosoitteena:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Varmista paikallinen malli

Varmista, että Lemonade pystyy tarjoamaan valitun mallin:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Lähetä sitten pieni keskustelupyyntö:

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

Jos tämä palauttaa `choices`-taulukon, Lemonade on valmis Agent Canvasia varten.
## 3. Käynnistä Agent Canvas

Asenna julkaistu Agent Canvas -paketti ja käynnistä koko pino:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Jos globaali npm-asennus epäonnistuu käyttöoikeusvirheeseen, katso alla oleva
npm-käyttöoikeuksien vianmäärityskohta.

Oletusarvoisesti Agent Canvas käynnistyy osoitteessa `http://localhost:8000`.
Avaa kyseinen osoite selaimessasi. Oletusarvoisen paikallisen taustajärjestelmän
tulisi näkyä terveenä aloitusnäytöllä.

Komento `agent-canvas` käynnistää agenttipalvelimen, automaation
taustajärjestelmän ja verkkosovelluksen käyttöliittymän yhdessä. Tarvitset vain
tämän yhden komennon OpenHandsin ajamiseen paikallisesti. Tämän oppaan loppuosa
konfiguroi kaiken Agent Canvas -käyttöliittymän kautta selaimessasi.

## 4. Määritä paikallinen LLM käyttöliittymässä

Ensimmäisellä käynnistyskerralla Agent Canvas avaa käyttöönottoprosessin. Tee
siinä seuraavaa:

1. Pidä **OpenHands** valittuna agenttina ja napsauta **Next**.
2. Kohdassa **Set up your LLM** valitse **Advanced**.
3. Pidä **Authentication**-asetuksena **API key**.
4. Aseta **Custom Model** arvoon `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Aseta **Base URL** arvoon `http://127.0.0.1:13305/api/v1`.
6. Kohtaan **API Key** syötä mikä tahansa ei-tyhjä paikkamerkki, kuten
   `lemonade-local`. Lemonade ei vaadi oikeaa avainta, mutta OpenHands-asiakas
   tarvitsee jonkin arvon lähetettäväksi.

Yhteyskenttien tulisi näyttää tältä. Käyttöliittymä peittää API-avainkentän.

![Agent Canvasin ensikäytön LLM Advanced -asetukset Lemonade-mallilla ja paikallisella base-osoitteella](assets/01-llm-advanced-settings.png)

Valitse sitten **All** ja aseta lisäasetukset paikalliselle mallille:

1. Vieritä kohtaan **Custom Tokenizer** ja aseta se arvoon
   `Qwen/Qwen3.6-35B-A3B`.
2. Vieritä kohtaan **LiteLLM Extra Body** ja aseta se arvoon
   `{"enable_thinking": true}`.
3. Napsauta **Next**.

![Agent Canvasin ensikäytön LLM All-välilehti Qwen-mukautetulla tokenisoijalla](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvasin ensikäytön LLM All-välilehti LiteLLM extra body -asetuksella](assets/03-llm-all-extra-body-settings.png)

LLM-asetusten tulisi näyttää seuraavalta:

| Kenttä | Arvo |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/`-etuliite kertoo LiteLLM:lle, että pyynnöt Lemonade-päätepistettä
kohtaan tulee muotoilla OpenAI-yhteensopivasti. Mukautettu tokenisoija on
GGUF-mallin alkuperäinen Hugging Face -tokenisoija; sen avulla OpenHands osaa
laskea samat keskustelumallin (chat-template) tokenit kuin paikallinen
mallipalvelin näkee. Nykyinen ensikäytön LLM-lomake ei näytä
kondensoijan (condenser) asetuksia. Jos Agent Canvas -versiosi näyttää
kondensoijan asetukset myöhemmin kohdassa **Settings > LLM**, käytä
arvoa `llm_summarizing` ja aseta enimmäistokenimäärä Lemonade-kontekstiikkunaa
pienemmäksi, esimerkiksi `56000`.

## 5. Asenna GitHub- ja Slack-MCP-palvelimet

Avaa Agent Canvasin käyttöliittymässä **Customize** (tai
**Settings > MCP**) lisätäksesi MCP-palvelimet, jotka antavat agentille
työkalut GitHubia ja Slackia varten. Tokeniarvot lähetetään vain paikalliselle
Agent Serverillesi, ja ne tallennetaan salattuina asetuksina.

### GitHub-MCP-palvelin

Lisää uusi MCP-palvelin seuraavilla asetuksilla:

| Kenttä | Arvo |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = GitHub-tokenisi |

Käytä GitHub-tokenia, jolla on lukuoikeus yhteenvedettävään repositorioon.

### Slack-MCP-palvelin

Lisää toinen MCP-palvelin seuraavilla asetuksilla:

| Kenttä | Arvo |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = koostekanavasi tunnus |

Aseta `SLACK_CHANNEL_IDS` koostekanavan tunnukseksi (sama arvo kuin
`SLACK_DIGEST_CHANNEL`), jotta agentin ei tarvitse selata jokaista
Slack-kanavaa.

Kun olet lisännyt molemmat palvelimet, käytä kummankin kohdalla
**Test**-painiketta varmistaaksesi, että yhteys muodostuu ja työkalut
ilmoitetaan. GitHub-palvelimen tulisi luetella GitHub-työkaluja, ja
Slack-palvelimen tulisi luetella Slack-työkaluja.

![Agent Canvasin MCP-sivu, jossa GitHub- ja Slack-palvelimet on asennettu](assets/04-mcp-servers-installed.png)

## 6. Luo koosteautomaatio

Avaa Agent Canvasin käyttöliittymässä **Automations**-sivu ja luo uusi
automaatio:

1. Valitse **Create automation** ja tyypiksi **Prompt preset**.
2. Aseta **Name**-kenttään `GitHub Development Digest to Slack`.
3. Aseta **Prompt**-kenttään seuraava teksti korvaten repositorion ja kanavan
   paikkamerkit omilla arvoillasi:

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

4. Aseta **Trigger**-arvoksi **Cron** aikataululla `0 9 * * 1-5` (klo 9
   arkipäivisin) ja aseta **Timezone** omaan aikavyöhykkeeseesi, esimerkiksi
   `America/New_York`.
5. Aseta **Timeout**-arvoksi `900` sekuntia.
6. Tallenna automaatio.

Automaation tietosivu näyttää uuden automaation cron-liipaisimineen ja
luodun prompt-preset-aloituspisteen.

![Agent Canvasin automaation tietosivu luonnin jälkeen](assets/05-automation-created.png)
## 7. Testaa automaatio

Agent Canvas -käyttöliittymän automaation tarkastelusivulla:

1. Napsauta **Run now** (tai **Dispatch**) suorittaaksesi automaation kerran välittömästi.
2. Tarkkaile ajolistaa samalla sivulla. Uusimman ajon tilan pitäisi vaihtua muotoon
   `COMPLETED`.
3. Avaa kohde-Slack-kanavasi. Sen pitäisi sisältää luotu koonti.

Sinun ei tarvitse odottaa cron-aikataulun laukeamista—**Run now** käynnistää
ajon pyynnöstä, jotta voit varmistaa promptin, MCP-yhteydet ja Slack-julkaisun
toimivan ennen kuin luotat aikatauluun.

![Agent Canvas -automaation ajo suoritettiin onnistuneesti](assets/06-automation-run-completed.png)

![Slack-kanava, jossa näkyy luotu OpenHands-koonti](assets/07-slackbot-message.png)

## Vianmääritys

- **Lemonade ei toimi:** käynnistä se uudelleen komennolla
  `lemonade run "${LEMONADE_MODEL}"` vaiheessa 1 ja suorita terveystarkistus
  uudelleen.
- **`npm install -g` epäonnistuu käyttöoikeusvirheeseen:** määritä Linuxissa tai
  WSL:ssä käyttäjän omistama globaali npm-hakemisto, lisää se komentotulkkisi
  käynnistystiedostoon ja asenna Agent Canvas uudelleen:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Jos käytät `zsh`-komentotulkkia, lisää sama `export PATH=...` -rivi
  tiedostoon `~/.zshrc` `~/.bashrc`-tiedoston sijaan.
- **Agent Canvas hylkää LLM-asetukset `custom_tokenizer`-asetuksen jälkeen:**
  asenna `transformers` Agent Server -Python-ympäristöön, käynnistä Agent
  Canvas tarvittaessa uudelleen ja yritä tallentaa LLM-asetukset uudelleen.
  OpenHands tarvitsee Transformersia lataamaan tokenisoijan chat-mallipohjan,
  kun `custom_tokenizer` on asetettu.
- **Agent Canvas ei saa yhteyttä Lemonadeen:** varmista
  `curl -fsS "${LEMONADE_BASE_URL}/health"` ja tarkista, että ensimmäisen
  käyttökerran LLM-lomakkeeseen tai kohtaan **Settings > LLM** syötetty
  perusosoite vastaa käynnissä olevaa paikallista päätepistettä tai
  HTTPS-tunnelia.
- **LLM-asetukset eivät tallentuneet:** varmista, että napsautit **Next**
  arvojen syöttämisen jälkeen. Avaa **Settings > LLM** uudelleen ja tarkista,
  että arvot säilyivät.
- **GitHub MCP ei näe yksityisiä tietovarastoja:** varmista, että
  GitHub-tunnuksella on lukuoikeus kohdetietovarastoon ja että MCP:n **Test**-
  painike kohdassa **Customize** ilmoittaa GitHub-työkalut käytettävissä.
- **Slack pystyy lukemaan kanavia mutta ei julkaisemaan:** kutsu Slack-sovellus
  kohdekanavaan ja varmista, että botilla on `chat:write`-oikeus.
- **Automaatio listaa liian monta Slack-kanavaa:** käytä Slack-kanavan
  tunnusta ja aseta `SLACK_CHANNEL_IDS` Slack MCP -palvelimelle kohdassa
  **Customize**.
- **Automaation ajo epäonnistuu tai ylittää kontekstin:** varmista, että
  Lemonade käynnistettiin asetuksella `ctx_size=65536`, että OpenHands-LLM:lle
  on asetettu `custom_tokenizer`, ja käytä nimenomaista tietovarastoa, jossa
  GitHub-tulosjoukot on rajattu 3–5 kohteeseen. Jos Agent Canvas -versiosi
  tarjoaa tiivistimen (condenser) asetukset, aseta tiivistimen enimmäistokenit
  Lemonaden kontekstiikkunaa pienemmäksi.

## Seuraavat vaiheet

- Lisää viikoittainen, vain julkaisuihin keskittyvä koonti.
- Lisää GitHub-tapahtumien laukaisema automaatio nopeampia PR- tai
  push-hälytyksiä varten.
- Ohjaa sama koonti Notioniin, Lineariin tai muuhun MCP-pohjaiseen työkaluun.

## Resurssit

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server -dokumentaatio](https://lemonade-server.ai/docs)
- [OpenHands-laajennusten tietovarasto](https://github.com/OpenHands/extensions)
- [Model Context Protocol -palvelimet](https://github.com/modelcontextprotocol/servers)
- [Slack MCP -paketti](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)