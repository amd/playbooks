<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Pregled

Razvijalci porabijo veliko časa za majhne ponavljajoče se cikle: pregledovanje
označenih pull requestov, odgovarjanje na komentarje GitHub, triažo novih
zadev, pretvarjanje niti Slack v zapiske za dnevne sestanke ali sledenje po
incidentih ter spremljanje signalov o izdajah ali raziskavah. Vsak cikel je
poznan, vendar še vedno zahteva presojo: zbrati pravi kontekst, odločiti, kaj
je pomembno, in objaviti jasno posodobitev tam, kjer ekipa že dela.

[Avtomatizacije OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
te cikle spremenijo v načrtovane ali z dogodki sprožene pogovore agenta: teke,
pri katerih lahko agent programske opreme AI prebere kontekst, kliče orodja in
ustvari posodobitev. Skupne predloge avtomatizacij v katalogu razširitev
OpenHands sledijo temu vzorcu za pregled pull requestov GitHub, spremljanje
repozitorijev, triažo zadev Linear, retrospektive incidentov, dnevne povzetke
Slack in raziskovalna poročila: avtomatizacija se prebudi, uporabi
konfigurirane integracije, kot sta GitHub ali Slack, za pridobitev konteksta,
sklepa o tem kontekstu z velikim jezikovnim modelom (LLM) ter zapiše rezultat
nazaj.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokalna nadzorna
ravnina za gradnjo in testiranje teh avtomatizacij. V tem priročniku poganja
strežnik OpenHands Agent Server, ozadnji proces, ki izvaja pogovore agenta, in
poveže agenta z zunanjimi storitvami, kot sta GitHub in Slack.

Da bi delovni tok ostal na vašem sistemu AMD, se agent pogovarja z lokalnim
modelom, ki ga strežnik Lemonade Server ponuja. Lemonade izpostavi ta model
prek API-ja, združljivega z OpenAI, tako da lahko Agent Canvas ta model
konfigurira kot oddaljeno končno točko v slogu OpenAI, medtem ko model, poziv
in kontekst delovnega toka ostanejo lokalni.

V tem priročniku boste zgradili eno konkretno avtomatizacijo: načrtovan
razvojni povzetek za Slack, ustvarjen iz GitHub. Uporablja GitHub za pregled
nedavne dejavnosti v repozitoriju, Slack za objavo povzetka, klice API-ja
Agent Canvas za konfiguracijo in testiranje avtomatizacije ter Lemonade za
lokalno izvajanje modela LLM.

![Diagram arhitekture, ki prikazuje GitHub MCP, avtomatizacijo OpenHands, Lemonade Server in Slack MCP](assets/00-architecture-overview.png)

## Kaj se boste naučili

- Kako zagnati Lemonade Server in preveriti, ali lokalni model odgovarja na zahteve za klepet
- Kako zagnati Agent Canvas in usmeriti njegov Agent Server na lokalni LLM
- Kako namestiti strežnike GitHub in Slack Model Context Protocol (MCP) prek
  API-ja strežnika Agent Server
- Kako ustvariti in razporediti načrtovano avtomatizacijo OpenHands, ki objavi
  razvojni povzetek v Slack
- Kako odpraviti najpogostejše napake lokalnega modela in avtomatizacije

## Osnovni pojmi

| Pojem | Kaj je to | Kje se umešča v ta priročnik |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za strežbo LLM, zgrajena za strojno opremo AMD, ki izpostavi API, združljiv z OpenAI. Vaši podatki nikoli ne zapustijo vaše naprave. | Poganja model, ki napaja agenta. |
| OpenHands Agent Server | Ozadnji proces, ki izvaja pogovore agenta OpenHands. | Gosti agenta, njegov profil LLM in njegove strežnike MCP. |
| Agent Canvas | Lokalna nadzorna ravnina za OpenHands, ki poganja Agent Server in uporabniški vmesnik za pregled tekov agenta. | Zažene ozadnje procese in ponudi API, ki ga kličete. |
| Strežnik MCP | Strežnik Model Context Protocol, ki agentu ponudi orodja za zunanjo storitev, kot sta GitHub ali Slack. | Agentu omogoči branje GitHub in pisanje v Slack. |
| Avtomatizacija OpenHands | Načrtovan ali z dogodki sprožen pogovor agenta, ki pridobi kontekst, sklepa o njem in nekje zapiše rezultat. | Povzetek za Slack, ustvarjen iz GitHub, ki ga zgradite tukaj. |

<!-- @device:stx,krk -->
> [!NOTE]
> Delovni tokovi kodirnih agentov imajo koristi od večjega modela in večjega
> kontekstnega okna. Uporabite vsaj 32 GB sistemskega pomnilnika, za večje
> modele GGUF pa raje 64 GB ali več.
<!-- @device:end -->

## Predpogoji

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrebujete:

- Nameščen Lemonade Server, ki ga namestite po standardnem
  [vodniku za namestitev Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ali novejši ter `npm`, ki se uporabljata za namestitev objavljenega
  vmesnika CLI Agent Canvas in zagon strežnikov MCP z `npx`.
- Nedaven objavljen paket `@openhands/agent-canvas` s
  shemsko vodenimi nastavitvami agenta, `LLMSummarizingCondenserSettings.max_tokens`,
  in podporo za `custom_tokenizer` LLM.
- Paket Python `transformers`, ki mora biti na voljo v okolju strežnika Agent Server.
  Zahtevan je za štetje žetonov predloge klepeta, kadar je nastavljen
  `custom_tokenizer`.
- Žeton GitHub z bralnim dostopom do repozitorija, ki ga želite povzeti.
- Žeton bota Slack (`xoxb-...`) s pravicami `chat:write` in bralnim dostopom do kanala.
- ID ekipe Slack (`T...`).
- ID kanala Slack (`C...`), kamor naj bo objavljen povzetek.

Preden preizkusite avtomatizacijo, povabite aplikacijo Slack v ciljni kanal.

## Spremenljivke, uporabljene v tem priročniku

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

Naslednje vrednosti so v poznejših korakih vnesene v uporabniški vmesnik Agent Canvas. Nastavite jih tukaj, da jih boste lahko kopirali:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Za `GITHUB_REPO_FILTER` uporabite izrecno vrednost `owner/repo`. Splošni nadomestni znaki za organizacijo lahko za lokalne modele vrnejo preveč konteksta MCP.

## 1. Zagon strežnika Lemonade Server

Zaženite model iz vmesnika CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade izpostavi API, združljiv z OpenAI, na naslovu:

```text
http://127.0.0.1:13305/api/v1
```

Neobvezno: če Agent Canvas ali zaganjalnik avtomatizacije ni v isti napravi,
objavite končno točko Lemonade prek varnega tunela in uporabite URL HTTPS kot
osnovni URL za LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Preverjanje lokalnega modela

Potrdite, da lahko Lemonade streže izbrani model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Nato pošljite majhno zahtevo za klepet:

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

Če to vrne polje `choices`, je Lemonade pripravljen za Agent Canvas.
## 3. Zaženite Agent Canvas

Namestite objavljen paket Agent Canvas in zaženite celoten sklad:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Če globalna namestitev npm ne uspe zaradi napake z dovoljenji, si oglejte
spodnji vnos za odpravljanje težav z dovoljenji npm.

Privzeto se Agent Canvas zažene na naslovu `http://localhost:8000`. Odprite
ta URL v brskalniku. Privzeto lokalno zaledje (backend) bi moralo biti na
domačem zaslonu prikazano kot zdravo.

Ukaz `agent-canvas` zažene strežnik agenta, avtomatizacijsko zaledje in
spletni vmesnik (frontend) skupaj. Za lokalni zagon OpenHands potrebujete
samo ta en ukaz. Preostanek tega vodnika konfigurira vse prek uporabniškega
vmesnika Agent Canvas v vašem brskalniku.

## 4. Konfigurirajte lokalni LLM v uporabniškem vmesniku

Ob prvem zagonu se v Agent Canvas odpre postopek uvajanja. V tem postopku:

1. Pustite **OpenHands** izbran kot agenta in kliknite **Next**.
2. Na zaslonu **Set up your LLM** izberite **Advanced**.
3. Pustite **Authentication** nastavljeno na **API key**.
4. Nastavite **Custom Model** na vrednost `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key** vnesite poljuben neprazen nadomestni niz, na primer
   `lemonade-local`. Lemonade ne zahteva pravega ključa, vendar odjemalec
   OpenHands potrebuje vrednost, ki jo pošlje.

Polja za povezavo bi morala izgledati takole. Polje za API-ključ je v
uporabniškem vmesniku zakrito.

![Nastavitve Agent Canvas ob prvi uporabi za LLM Advanced z modelom Lemonade in lokalnim osnovnim URL-jem](assets/01-llm-advanced-settings.png)

Nato izberite **All** in nastavite dodatna polja za lokalni model:

1. Pomaknite se do **Custom Tokenizer** in ga nastavite na
   `Qwen/Qwen3.6-35B-A3B`.
2. Pomaknite se do **LiteLLM Extra Body** in ga nastavite na
   `{"enable_thinking": true}`.
3. Kliknite **Next**.

![Zavihek Agent Canvas ob prvi uporabi za LLM All s prilagojenim tokenizatorjem Qwen](assets/02-llm-all-tokenizer-settings.png)

![Zavihek Agent Canvas ob prvi uporabi za LLM All s konfiguriranim LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Nastavitve LLM bi morale prikazovati:

| Polje | Vrednost |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Predpona `openai/` orodju LiteLLM sporoči, naj proti končni točki Lemonade
uporabi obliko zahtev, združljivo z OpenAI. Prilagojeni tokenizator je
izvirni tokenizator Hugging Face za model GGUF; omogoča, da OpenHands šteje
iste žetone predloge klepeta (chat-template), kot jih vidi lokalni strežnik
modela. Trenutni obrazec LLM ob prvi uporabi ne prikazuje nastavitev
kondenzatorja (condenser). Če vaša različica Agent Canvas pozneje prikazuje
nastavitve kondenzatorja pod **Settings > LLM**, uporabite
`llm_summarizing` in nastavite največje število žetonov pod velikostjo
kontekstnega okna Lemonade, na primer `56000`.

## 5. Namestite strežnika MCP za GitHub in Slack

V uporabniškem vmesniku Agent Canvas odprite **Customize** (ali
**Settings > MCP**), da dodate strežnike MCP, ki agentu omogočijo orodja za
GitHub in Slack. Vrednosti žetonov (token) se pošljejo samo vašemu lokalnemu
strežniku agenta in se shranijo kot šifrirane nastavitve.

### Strežnik MCP za GitHub

Dodajte nov strežnik MCP s temi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = vaš žeton GitHub |

Uporabite žeton GitHub z bralnim dostopom do skladišča, ki ga želite
povzeti.

### Strežnik MCP za Slack

Dodajte drugi strežnik MCP s temi nastavitvami:

| Polje | Vrednost |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašega kanala za povzetek |

Nastavite `SLACK_CHANNEL_IDS` na ID kanala za povzetek (enaka vrednost kot
`SLACK_DIGEST_CHANNEL`), da agentu ni treba prebrskati vsakega kanala Slack.

Ko dodate oba strežnika, uporabite gumb **Test** na vsakem od njiju, da
potrdite, da se poveže in oglašuje orodja. Strežnik GitHub bi moral
prikazati orodja za GitHub, strežnik Slack pa orodja za Slack.

![Stran MCP v Agent Canvas z nameščenima strežnikoma GitHub in Slack](assets/04-mcp-servers-installed.png)

## 6. Ustvarite avtomatizacijo za povzetek

V uporabniškem vmesniku Agent Canvas odprite stran **Automations** in
ustvarite novo avtomatizacijo:

1. Izberite **Create automation** in nato vrsto **Prompt preset**.
2. Nastavite **Name** na `GitHub Development Digest to Slack`.
3. Nastavite **Prompt** na naslednje besedilo, pri čemer nadomestne
   vrednosti za skladišče in kanal zamenjajte s svojimi:

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

4. Nastavite **Trigger** na **Cron** z urnikom `0 9 * * 1-5` (ob 9. uri
   ob delavnikih) in nastavite **Timezone** na svoj časovni pas, na primer
   `America/New_York`.
5. Nastavite **Timeout** na `900` sekund.
6. Shranite avtomatizacijo.

Stran s podrobnostmi avtomatizacije prikazuje novo avtomatizacijo z njenim
cron sprožilcem in ustvarjeno vstopno točko prednastavljenega poziva
(prompt-preset).

![Podrobnosti avtomatizacije Agent Canvas po ustvarjanju](assets/05-automation-created.png)
## 7. Testiranje avtomatizacije

Na strani s podrobnostmi avtomatizacije v uporabniškem vmesniku Agent Canvas:

1. Kliknite **Run now** (ali **Dispatch**), da avtomatizacijo takoj enkrat zaženete.
2. Spremljajte seznam zagonov na isti strani. Zadnji zagon bi moral preiti v stanje
   `COMPLETED`.
3. Odprite ciljni kanal Slack. V njem bi moral biti generiran povzetek.

Ni vam treba čakati na sprožitev urnika cron – **Run now** sproži zagon na
zahtevo, tako da lahko potrdite pravilnost poziva, povezav MCP in objavljanja
na Slack, preden se zanesete na urnik.

![Avtomatizacija Agent Canvas uspešno zaključena](assets/06-automation-run-completed.png)

![Kanal Slack s prikazanim generiranim povzetkom OpenHands](assets/07-slackbot-message.png)

## Odpravljanje težav

- **Lemonade ne deluje:** znova ga zaženite z ukazom
  `lemonade run "${LEMONADE_MODEL}"` iz koraka 1, nato ponovno zaženite preverjanje
  stanja.
- **`npm install -g` se ne izvede zaradi napake z dovoljenji:** v sistemu Linux ali WSL
  konfigurirajte uporabniško lasten globalni imenik npm, ga dodajte v zagonsko
  datoteko lupine, nato pa znova namestite Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Če uporabljate `zsh`, dodajte isto vrstico `export PATH=...` v `~/.zshrc`
  namesto v `~/.bashrc`.
- **Agent Canvas po nastavitvi `custom_tokenizer` zavrne nastavitve LLM:**
  namestite `transformers` v okolje Python strežnika agenta, po potrebi znova
  zaženite Agent Canvas in poskusite znova shraniti nastavitve LLM. OpenHands
  za nalaganje predloge klepeta tokenizatorja potrebuje Transformers, ko je
  nastavljen `custom_tokenizer`.
- **Agent Canvas ne more doseči Lemonade:** preverite
  `curl -fsS "${LEMONADE_BASE_URL}/health"` in potrdite, da se osnovni URL,
  vnesen v obrazcu LLM ob prvi uporabi ali v razdelku **Settings > LLM**,
  ujema z delujočo lokalno končno točko ali predorom HTTPS.
- **Nastavitve LLM se niso shranile:** preverite, ali ste po vnosu vrednosti
  kliknili **Next**. Znova odprite **Settings > LLM**, da potrdite, da so
  vrednosti ostale shranjene.
- **GitHub MCP ne vidi zasebnih repozitorijev:** preverite, ali ima žeton
  GitHub bralni dostop do ciljnega repozitorija in ali gumb **Test** za MCP
  v razdelku **Customize** prikaže orodja GitHub.
- **Slack lahko bere kanale, ne more pa objavljati:** povabite aplikacijo
  Slack v ciljni kanal in preverite, ali ima bot dovoljenje `chat:write`.
- **Avtomatizacija prikaže preveč kanalov Slack:** uporabite ID kanala Slack
  in nastavite `SLACK_CHANNEL_IDS` na strežniku Slack MCP v razdelku
  **Customize**.
- **Zagon avtomatizacije ne uspe ali preseže kontekst:** preverite, ali je bil
  Lemonade zagnan z `ctx_size=65536`, ali ima LLM OpenHands nastavljen
  `custom_tokenizer`, in uporabite izrecno določen repozitorij z rezultati
  GitHub, omejenimi na 3 do 5 elementov. Če vaša izdaja Agent Canvas prikazuje
  nastavitve kondenzatorja, nastavite največje število žetonov kondenzatorja
  pod velikostjo kontekstnega okna Lemonade.

## Naslednji koraki

- Dodajte tedenski povzetek samo za izdaje (release).
- Dodajte avtomatizacijo, sproženo z dogodkom GitHub, za hitrejša obvestila
  o PR-jih ali potiskih (push).
- Preusmerite isti povzetek v Notion, Linear ali drugo orodje, podprto z MCP.

## Viri

- [Priročniki AMD AI](https://developer.amd.com/playbooks/)
- [Dokumentacija strežnika Lemonade](https://lemonade-server.ai/docs)
- [Repozitorij razširitev OpenHands](https://github.com/OpenHands/extensions)
- [Strežniki Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Paket Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)