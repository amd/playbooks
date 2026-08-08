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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) on tekoälypohjainen ohjelmistoagentti,
joka voi kirjoittaa koodia, suorittaa komentoja, selata verkkoa ja muokata tiedostoja aidossa
työtilassa. Sen sijaan, että kopioisit ehdotuksia keskusteluikkunasta, osoitat agentin
projektikansioon ja annat sen tehdä työn: toteuttaa ominaisuuden, korjata virheen, kirjoittaa
testejä tai selittää koodikannan.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) on suositeltu
selainkäyttöliittymä OpenHandsin ajamiseen. Yksi `agent-canvas`-komento käynnistää
agenttipalvelimen, automaatiotaustajärjestelmän ja verkkokäyttöliittymän yhdessä, joten voit
käydä keskustelua agentin kanssa selaimessasi.

Jotta kaikki pysyy AMD-järjestelmässäsi, agentti keskustelee paikallisen mallin kanssa, jota
Lemonade Server tarjoilee. Lemonade tuo tämän mallin saataville OpenAI-yhteensopivan
API:n kautta, joten Agent Canvas voi määrittää sen kuten minkä tahansa muun OpenAI-tyylisen
päätepisteen, samalla kun malli, koodisi ja keskustelun konteksti pysyvät kaikki
koneellasi.

Tässä ohjekirjassa käynnistät paikallisen mallin, käynnistät Agent Canvasin, osoitat sen
kyseiseen malliin ja suoritat ensimmäisen koodaustehtäväsi todellista projektikansiota vasten.

## Mitä opit

- Kuinka käynnistää Lemonade Server ja varmistaa, että paikallinen malli vastaa chat-pyyntöihin
- Kuinka asentaa ja käynnistää Agent Canvas npm-paketista
- Kuinka määrittää Agent Canvas käyttämään paikallista Lemonade-mallia LLM:nä
- Kuinka aloittaa OpenHands-keskustelu ja seurata, kun agentti muokkaa tiedostoja ja suorittaa
  komentoja työtilassa
- Kuinka tarkastella, mitä agentti muutti, ja ohjata sitä jatkoviesteillä

## Peruskäsitteet

| Käsite | Mitä se on | Missä se liittyy tähän ohjekirjaan |
| --- | --- | --- |
| Lemonade Server | AMD-laitteistolle rakennettu paikallinen LLM-tarjoilualusta, joka tuo saataville OpenAI-yhteensopivan API:n. Tietosi eivät koskaan poistu koneeltasi. | Ajaa mallia, joka toimii agentin voimanlähteenä. |
| OpenHands | Tekoälypohjainen ohjelmistoagentti, joka lukee ja muokkaa tiedostoja, suorittaa shell-komentoja ja selaa verkkoa työtilan sisällä. | Agentti, jota ohjaat chatista. |
| Agent Canvas | Selainkäyttöliittymä ja taustajärjestelmä, joka ajaa OpenHands-keskusteluja ja näyttää työkalukutsut ja tiedostomuutokset. | Käynnistää pinon ja isännöi keskusteluasi. |
| Työtila | Projektikansio, jota agentilla on lupa lukea ja muokata. | Agentin muokkausten ja komentojen kohde. |

<!-- @device:stx,krk -->
> [!NOTE]
> Koodausagentin työnkulut hyötyvät suuremmasta mallista ja kontekstiikkunasta. Käytä
> vähintään 32 Gt järjestelmämuistia ja suosi 64 Gt tai enemmän suuremmille GGUF-malleille.
<!-- @device:end -->

## Vaatimukset

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Tarvitset:

- Lemonade Server asennettuna ja kykenevänä tarjoilemaan alla olevaa mallia.
- Node.js 22.12 tai uudempi ja `npm` (jota `agent-canvas`-CLI käyttää).
- `uv`, Python-pakettienhallinta, jota Agent Canvas käyttää agenttipalvelimen ympäristön
  hallintaan. Jos järjestelmässäsi ei ole sitä jo, asenna se
  [uv-asennusoppaasta](https://docs.astral.sh/uv/getting-started/installation/)
  ennen Agent Canvasin käynnistämistä.
- Projektikansio, jossa työskennellä. Tämä voi olla mikä tahansa paikallinen git-repositorio tai
  koodihakemisto, jonka parissa haluat agentin työskentelevän.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Käynnistä Lemonade Server

Käynnistä malli Lemonade-CLI:stä:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade tuo saataville OpenAI-yhteensopivan API:n osoitteessa:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Vahvista paikallinen malli

Varmista, että Lemonade voi tarjoilla valittua mallia:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Lähetä sitten pieni chat-pyyntö:

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

Jos tämä palauttaa `choices`-taulukon, Lemonade on valmis Agent Canvasille.

## 3. Asenna ja käynnistä Agent Canvas

Asenna julkaistu Agent Canvas -paketti globaalisti:

```bash
npm install -g @openhands/agent-canvas
```

Käynnistä sitten koko pino päätteestä:

```bash
agent-canvas
```

Oletuksena Agent Canvas käynnistyy osoitteessa `http://localhost:8000`. Avaa kyseinen osoite
selaimessasi. Jos portti 8000 on jo käytössä, anna `--port` (tai `-p`), kun
käynnistät Agent Canvasin:

```bash
agent-canvas --port 3000
```

Sama komento toimii PowerShellissä Windowsilla. Avaa sitten
`http://localhost:3000` sen sijaan. Oletusarvoisen paikallisen taustajärjestelmän tulisi näkyä
terveenä aloitusnäytöllä.

`agent-canvas`-komento käynnistää agenttipalvelimen, automaatiotaustajärjestelmän ja
verkkokäyttöliittymän yhdessä. Tarvitset vain tämän yhden komennon OpenHandsin ajamiseen
paikallisesti.

## 4. Määritä paikallinen LLM

Ensimmäisellä käynnistyskerralla Agent Canvas avaa käyttöönottokulun. Tässä kulussa:

1. Pidä **OpenHands** valittuna agenttina ja napsauta **Next**.
2. Kohdassa **Set up your LLM** valitse **Advanced**.
3. Pidä **Authentication**-asetuksena **API key**.
4. Aseta **Custom Model**-arvoksi `openai/Qwen3.6-35B-A3B-GGUF`.
5. Aseta **Base URL**-arvoksi `http://127.0.0.1:13305/api/v1`.
6. Syötä **API Key**-kenttään mikä tahansa ei-tyhjä paikkamerkki, kuten `lemonade-local`.
   Lemonade ei vaadi todellista avainta, mutta OpenHands-asiakas tarvitsee arvon
   lähetettäväksi.
7. Napsauta **Next**.

Valmiiden Advanced-asetusten pitäisi näyttää tältä. API-avainkenttä on
peitetty käyttöliittymässä.

![Agent Canvasin ensikäytön LLM Advanced -asetukset Lemonade-mallilla ja paikallisella base URL:lla](assets/01-llm-advanced-settings.png)

Agent Canvas tallentaa nämä arvot LLM-profiiliksi. Jos versiosi pyytää nimeämään
tämän profiilin, käytä ilman välilyöntejä olevaa nimeä, kuten `lemonade-local`. Jos vaihdat
malleja myöhemmin, avaa **Settings > LLM** ja päivitä samat Advanced-kentät. Voit
vaihtaa tallennettuja profiileja chat-syötteestä `/model`-komennolla.

## 5. Avaa työtila

Agentti voi lukea ja muokata tiedostoja vain valitsemasi työtilan sisällä. Ennen
tehtävän aloittamista osoita Agent Canvas projektikansioosi:

1. Valitse aloitusnäytöltä **Open Workspace**.
2. Valitse kansio, joka sisältää projektisi (esimerkiksi git-repositorio,
   jonka parissa haluat agentin työskentelevän).
3. Aloita uusi keskustelu kyseisessä työtilassa.

Kaikki, mitä agentti tekee — tiedostojen lukeminen, komentojen suorittaminen, koodin muokkaaminen —
rajoittuu kyseiseen työtilaan.

![Agent Canvasin aloitusnäkymä käyttöönoton jälkeen](assets/02-agent-canvas-home.png)
## 6. Suorita ensimmäinen koodaustehtäväsi

Kun työtila on avattu ja paikallinen LLM valittu, kirjoita chattiin konkreettinen tehtävä. Hyvä ensimmäinen tehtävä on pieni ja helposti tarkistettavissa, esimerkiksi:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Seuraa keskustelun aikajanaa. OpenHands tekee seuraavaa:

- Lukee työtilan ymmärtääkseen sen rakenteen.
- Luo tiedoston `hello.py`, jossa on pyydetty funktio ja testilohko.
- Suorittaa halutessaan komennon `python3 hello.py` tuloksen tarkistamiseksi.
- Raportoi chatissa, mitä se teki, sekä mahdollisen komennon tulosteen.

Uuden tiedoston pitäisi ilmestyä työtilaan, ja agentin lopullisen viestin tulisi kuvata tehty muutos. Tämä on ratkaiseva hetki: agentti kirjoitti ja suoritti oikeaa koodia projektikansiossasi.

## 7. Tarkista ja ohjaa agenttia

Kun agentti on saanut vaiheen valmiiksi, tarkista sen työ ennen kuin hyväksyt seuraavan vaiheen:

- **Tiedostomuutokset**: käytä työtilan tiedostoselainta tai agentin diff-näkymää nähdäksesi tarkalleen, mitä lisättiin, muutettiin tai poistettiin.
- **Komennon tuloste**: laajenna mikä tahansa agentin suorittama komento nähdäksesi stdout-, stderr-tulosteet ja poistumiskoodin.
- **Jatkotoimet**: jos lopputulos ei ole toivotunlainen, vastaa samassa keskustelussa korjauksella. Agentti säilyttää aiemman kontekstin ja jatkaa samojen tiedostojen parissa.

Jos esimerkiksi testi ei tulostanut odotettua tervehdystä, vastaa:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agentti lukee tiedoston uudelleen, suorittaa komennon, diagnosoi ongelman ja muokkaa tiedostoa uudelleen — kaikki samassa keskustelussa.

## Vianmääritys

- **`agent-canvas` ei ole PATH-muuttujassa:** asenna uudelleen komennolla
  `npm install -g @openhands/agent-canvas` ja varmista, että npm:n globaalien binäärien
  hakemisto on PATH-muuttujassa. Aja Windowsissa `npm config get prefix`; palautetun
  hakemiston, usein `%APPDATA%\npm` tai `%USERPROFILE%\.npm-global`,
  täytyy olla käyttäjän PATH-muuttujassa, ennen kuin `agent-canvas` voidaan käynnistää
  uudesta terminaalista.
- **`npm install -g` epäonnistuu käyttöoikeusvirheeseen:** määritä käyttäjän omistama
  globaali npm-hakemisto, avaa sitten terminaali uudelleen ja asenna Agent Canvas uudelleen.

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

  Jotta Windowsin PATH-muutos säilyy pysyvästi, lisää `%USERPROFILE%\.npm-global`
  käyttäjän PATH-muuttujaan valitsemalla **Asetukset > Järjestelmä > Tietoja > Järjestelmän lisäasetukset >
  Ympäristömuuttujat**, ja avaa uusi terminaali.
  <!-- @os:end -->
- **Käyttöliittymä latautuu, mutta taustajärjestelmä näyttää epäterveeltä:** odota muutama
  sekunti agenttipalvelimen käynnistymisen loppuun saattamiseksi ja päivitä sitten sivu. Jos tila pysyy
  epäterveenä, käynnistä `agent-canvas` uudelleen ja tarkista terminaalin tuloste virheiden varalta.
- **Lemonade-chat-pyynnöt epäonnistuvat yhteysvirheeseen:** varmista, että
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` onnistuu ja että
  Lemonade tarjoilee edelleen mallia komennolla `lemonade status`.
- **Agentti antaa virheen kontekstin pituudesta tai token-rajasta:** käynnistä
  Lemonade uudelleen suuremmalla `ctx_size`-arvolla (esimerkiksi `ctx_size=65536`), ja aloita
  uusi keskustelu, jotta agentilla ei ole mukana liian suurta historiaa.
- **Agentti tuottaa laadultaan huonoja tai keskeneräisiä muokkauksia:** vaihda
  Lemonadessa suurempaan malliin tai anna agentille pienempi, konkreettisempi tehtävä ja anna
  sen valmistua ennen kuin pyydät seuraavaa muutosta.
- **`uv` puuttuu:** asenna se
  [uv:n asennusoppaasta](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas käyttää `uv`:tä agenttipalvelimen Python-ympäristön hallintaan.

## Seuraavat vaiheet

- Kokeile suurempaa tehtävää samassa työtilassa, kuten yksikkötestitiedoston lisäämistä tai
  tunnetun virheen korjaamista, ja tarkista agentin diff ennen muutoksen säilyttämistä.
- Yhdistä MCP-palvelin, kuten GitHub tai Slack, kohdassa **Customize**, jotta
  agentti voi lukea ongelmia tai julkaista päivityksiä työskennellessään.
- Tallenna useita LLM-profiileja (nopea pieni malli ja vahvempi suuri malli) ja
  vaihda niiden välillä komennolla `/model` kesken keskustelun.
- Siirry kohtaan [OpenHands-automaatiot](https://docs.openhands.dev/openhands/usage/automations/overview) ja
  muuta toistuvat kehityssilmukat ajastetuiksi tai tapahtumapohjaisiksi agenttiajoiksi.

## Resurssit

- [OpenHands-dokumentaatio](https://docs.openhands.dev/)
- [Agent Canvas -yleiskatsaus](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvasin asennus](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profiilit ja mallin määritykset](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server -dokumentaatio](https://lemonade-server.ai/docs)