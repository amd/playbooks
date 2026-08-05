<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Pregled

Programeri provode mnogo vremena na malim ponavljajućim ciklusima: pregledanje
označenih pull zahteva, odgovaranje na GitHub komentare, rangiranje novih
problema, pretvaranje Slack niti u beleške sa dnevnog sastanka ili praćenje
incidenata, kao i praćenje signala vezanih za izdanja ili istraživanja. Svaki
od ovih ciklusa je poznat, ali i dalje zahteva rasuđivanje: prikupljanje
odgovarajućeg konteksta, odlučivanje šta je važno i objavljivanje jasnog
ažuriranja na mestu gde tim već radi.

[OpenHands automatizacije](https://docs.openhands.dev/openhands/usage/automations/overview)
pretvaraju te cikluse u zakazane ili događajima pokrenute razgovore agenata:
pokretanja u kojima AI softverski agent može da čita kontekst, poziva alate i
izradi ažuriranje. Deljeni šabloni automatizacija u OpenHands katalogu
ekstenzija prate ovaj obrazac za pregled GitHub pull zahteva, praćenje
repozitorijuma, triažu Linear problema, retrospektive incidenata, dnevne
Slack rezimee i istraživačke izveštaje: automatizacija se aktivira, koristi
konfigurisane integracije poput GitHub-a ili Slack-a da dohvati kontekst,
rasuđuje o tom kontekstu pomoću velikog jezičkog modela (LLM) i zapisuje
rezultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je lokalna
kontrolna ravan za izgradnju i testiranje tih automatizacija. U ovoj knjizi
uputstava on pokreće OpenHands Agent Server, pozadinski proces koji izvršava
razgovore agenata, i povezuje agenta sa spoljnim servisima poput GitHub-a i
Slack-a.

Da bi tok rada ostao na vašem AMD sistemu, agent komunicira sa lokalnim
modelom koji se opslužuje preko Lemonade Server-a. Lemonade izlaže taj model
kroz API kompatibilan sa OpenAI, tako da Agent Canvas može da ga konfiguriše
kao udaljenu krajnju tačku u OpenAI stilu, dok model, upit i kontekst toka
rada ostaju lokalni.

U ovoj knjizi uputstava izgradićete jednu konkretnu automatizaciju: zakazani
razvojni rezime koji ide od GitHub-a ka Slack-u. Ona koristi GitHub za
ispitivanje nedavne aktivnosti repozitorijuma, Slack za objavljivanje rezimea,
Agent Canvas API pozive za konfigurisanje i testiranje automatizacije, kao i
Lemonade za lokalno pokretanje LLM-a.

![Dijagram arhitekture koji prikazuje GitHub MCP, OpenHands automatizaciju, Lemonade Server i Slack MCP](assets/00-architecture-overview.png)

## Šta ćete naučiti

- Kako da pokrenete Lemonade Server i proverite da li lokalni model odgovara na chat zahteve
- Kako da pokrenete Agent Canvas i usmerite njegov Agent Server ka lokalnom LLM-u
- Kako da instalirate GitHub i Slack Model Context Protocol (MCP) servere preko
  Agent Server API-ja
- Kako da napravite i pokrenete zakazanu OpenHands automatizaciju koja objavljuje
  razvojni rezime na Slack
- Kako da rešite najčešće greške vezane za lokalni model i automatizaciju

## Osnovni koncepti

| Koncept | Šta predstavlja | Gde se uklapa u ovu knjigu uputstava |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za opsluživanje LLM-a napravljena za AMD hardver koja izlaže API kompatibilan sa OpenAI. Vaši podaci nikada ne napuštaju vaš računar. | Pokreće model koji pokreće agenta. |
| OpenHands Agent Server | Pozadinski proces koji izvršava razgovore OpenHands agenata. | Ugošćuje agenta, njegov LLM profil i njegove MCP servere. |
| Agent Canvas | Lokalna kontrolna ravan za OpenHands koja pokreće Agent Server i korisnički interfejs za pregled pokretanja agenata. | Pokreće pozadinske sisteme i pruža API koji pozivate. |
| MCP server | Model Context Protocol server koji agentu daje alate za spoljni servis poput GitHub-a ili Slack-a. | Omogućava agentu da čita GitHub i piše na Slack. |
| OpenHands automatizacija | Zakazani ili događajima pokrenut razgovor agenta koji dohvata kontekst, rasuđuje o njemu i negde zapisuje rezultat. | Rezime od GitHub-a ka Slack-u koji ovde gradite. |

<!-- @device:stx,krk -->
> [!NOTE]
> Radni tokovi agenata za kodiranje imaju koristi od većeg modela i prozora
> konteksta. Koristite najmanje 32 GB sistemske memorije, a za veće GGUF
> modele preporučuje se 64 GB ili više.
<!-- @device:end -->

## Preduslovi

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrebno vam je:

- Lemonade Server instaliran prateći standardni
  [vodič za instalaciju Lemonade-a](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ili noviji i `npm`, koji se koriste za instalaciju objavljenog
  Agent Canvas CLI-ja i pokretanje MCP servera pomoću `npx`.
- Nedavno objavljen `@openhands/agent-canvas` paket sa
  podešavanjima agenta zasnovanim na šemi, `LLMSummarizingCondenserSettings.max_tokens`,
  i podrškom za LLM `custom_tokenizer`.
- Python paket `transformers` dostupan u okruženju Agent Server-a.
  Neophodan je za brojanje tokena chat šablona kada je postavljen
  `custom_tokenizer`.
- GitHub token sa pravom čitanja repozitorijuma koji želite da rezimirate.
- Slack bot token (`xoxb-...`) sa `chat:write` i pravom čitanja kanala.
- Slack ID tima (`T...`).
- Slack ID kanala (`C...`) na koji treba objaviti rezime.

Pozovite Slack aplikaciju u ciljni kanal pre testiranja automatizacije.

## Promenljive korišćene u ovoj knjizi uputstava

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

Sledeće vrednosti se unose u Agent Canvas korisnički interfejs u kasnijim
koracima. Podesite ih ovde kako biste mogli da ih kopirate:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Koristite eksplicitnu vrednost `owner/repo` za `GITHUB_REPO_FILTER`. Široki
džoker znaci organizacije mogu vratiti previše MCP konteksta za lokalne
modele.

## 1. Pokretanje Lemonade Server-a

Pokrenite model iz Lemonade CLI-ja:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade izlaže API kompatibilan sa OpenAI na:

```text
http://127.0.0.1:13305/api/v1
```

Opciono: ako Agent Canvas ili izvršilac automatizacije nisu na istom računaru,
objavite Lemonade krajnju tačku kroz bezbedni tunel i koristite HTTPS URL kao
osnovni URL za LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Provera lokalnog modela

Potvrdite da Lemonade može da opsluži izabrani model:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Zatim pošaljite mali chat zahtev:

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

Ako se vrati niz `choices`, Lemonade je spreman za Agent Canvas.
## 3. Pokretanje Agent Canvas

Instalirajte objavljeni Agent Canvas paket i pokrenite ceo stek:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Ako globalna npm instalacija ne uspe zbog greške u vezi sa dozvolama, pogledajte
odeljak o rešavanju problema sa npm dozvolama ispod.

Podrazumevano, Agent Canvas se pokreće na adresi `http://localhost:8000`. Otvorite
tu adresu u pregledaču. Podrazumevani lokalni bekend bi trebalo da se na
početnom ekranu prikaže kao ispravan (healthy).

Komanda `agent-canvas` pokreće agent server, automatizacioni bekend i veb
frontend zajedno. Potrebna vam je samo ova jedna komanda da biste pokrenuli
OpenHands lokalno. Ostatak ovog vodiča konfiguriše sve kroz Agent Canvas UI u
vašem pregledaču.

## 4. Konfigurisanje lokalnog LLM-a u UI-ju

Prilikom prvog pokretanja, Agent Canvas otvara tok uvođenja (onboarding). U tom
toku:

1. Zadržite **OpenHands** izabran kao agenta i kliknite na **Next**.
2. Na ekranu **Set up your LLM**, izaberite **Advanced**.
3. Zadržite **Authentication** postavljeno na **API key**.
4. Postavite **Custom Model** na vrednost promenljive `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Postavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key**, unesite bilo koju nepraznu placeholder vrednost, kao što je
   `lemonade-local`. Lemonade ne zahteva pravi ključ, ali OpenHands klijentu
   je potrebna vrednost koju šalje.

Polja za konekciju bi trebalo da izgledaju ovako. Polje za API ključ je
maskirano od strane UI-ja.

![Agent Canvas podešavanja LLM Advanced prilikom prvog korišćenja sa Lemonade modelom i lokalnim bazičnim URL-om](assets/01-llm-advanced-settings.png)

Zatim izaberite **All** i podesite dodatna polja za lokalni model:

1. Skrolujte do **Custom Tokenizer** i postavite ga na `Qwen/Qwen3.6-35B-A3B`.
2. Skrolujte do **LiteLLM Extra Body** i postavite ga na
   `{"enable_thinking": true}`.
3. Kliknite na **Next**.

![Agent Canvas kartica LLM All prilikom prvog korišćenja sa Qwen prilagođenim tokenizatorom](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas kartica LLM All prilikom prvog korišćenja sa konfigurisanim LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Podešavanja LLM-a bi trebalo da prikazuju:

| Polje | Vrednost |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefiks `openai/` govori LiteLLM-u da koristi OpenAI-kompatibilno formatiranje
zahteva prema Lemonade krajnjoj tački. Prilagođeni tokenizator je originalni
Hugging Face tokenizator za GGUF model; on omogućava OpenHands-u da broji iste
tokene chat-template koje vidi lokalni server modela. Trenutna forma za LLM
prilikom prvog korišćenja ne prikazuje podešavanja kondenzatora. Ako vaša
verzija Agent Canvas kasnije izloži podešavanja kondenzatora pod **Settings >
LLM**, koristite `llm_summarizing` i postavite maksimalan broj tokena ispod
Lemonade kontekstnog prozora, na primer `56000`.

## 5. Instaliranje GitHub i Slack MCP servera

U Agent Canvas UI-ju, otvorite **Customize** (ili **Settings > MCP**) da biste
dodali MCP servere koji agentu daju alate za GitHub i Slack. Vrednosti tokena
se šalju samo vašem lokalnom Agent Server-u i čuvaju se kao enkriptovana
podešavanja.

### GitHub MCP server

Dodajte novi MCP server sa sledećim podešavanjima:

| Polje | Vrednost |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = vaš GitHub token |

Koristite GitHub token sa pravom čitanja za repozitorijum koji želite da
sumirate.

### Slack MCP server

Dodajte drugi MCP server sa sledećim podešavanjima:

| Polje | Vrednost |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID vašeg kanala za digest |

Postavite `SLACK_CHANNEL_IDS` na ID kanala za digest (istu vrednost kao
`SLACK_DIGEST_CHANNEL`) kako agent ne bi morao da prolazi kroz svaki Slack
kanal.

Nakon dodavanja oba servera, koristite dugme **Test** na svakom od njih kako
biste potvrdili da se povezuju i oglašavaju alate. GitHub server bi trebalo da
prikaže listu GitHub alata, a Slack server listu Slack alata.

![Agent Canvas MCP stranica sa instaliranim GitHub i Slack serverima](assets/04-mcp-servers-installed.png)

## 6. Kreiranje digest automatizacije

U Agent Canvas UI-ju, otvorite stranicu **Automations** i kreirajte novu
automatizaciju:

1. Izaberite **Create automation** i tip **Prompt preset**.
2. Postavite **Name** na `GitHub Development Digest to Slack`.
3. Postavite **Prompt** na sledeći tekst, zamenjujući placeholder za
   repozitorijum i kanal svojim vrednostima:

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

4. Postavite **Trigger** na **Cron** sa rasporedom `0 9 * * 1-5` (9 časova
   ujutru radnim danima) i postavite **Timezone** na svoju vremensku zonu, na
   primer `America/New_York`.
5. Postavite **Timeout** na `900` sekundi.
6. Sačuvajte automatizaciju.

Stranica sa detaljima automatizacije prikazuje novu automatizaciju sa njenim
cron okidačem i generisanom ulaznom tačkom prompt-preset tipa.

![Agent Canvas stranica sa detaljima automatizacije nakon kreiranja](assets/05-automation-created.png)
## 7. Testiranje automatizacije

Sa stranice sa detaljima automatizacije u Agent Canvas UI:

1. Kliknite na **Run now** (ili **Dispatch**) da odmah pokrenete automatizaciju jednom.
2. Pratite listu pokretanja na istoj stranici. Poslednje pokretanje bi trebalo da pređe u stanje
   `COMPLETED`.
3. Otvorite ciljni Slack kanal. Trebalo bi da sadrži generisani digest.

Ne morate da čekate da se cron raspored aktivira—**Run now** pokreće
pokretanje na zahtev tako da možete da potvrdite da prompt, MCP konekcije i objavljivanje na Slack-u
sve rade pre nego što se oslonite na raspored.

![Uspešno završeno pokretanje Agent Canvas automatizacije](assets/06-automation-run-completed.png)

![Slack kanal koji prikazuje generisani OpenHands digest](assets/07-slackbot-message.png)

## Rešavanje problema

- **Lemonade ne radi:** ponovo ga pokrenite pomoću
  `lemonade run "${LEMONADE_MODEL}"` komande iz koraka 1, a zatim ponovo pokrenite proveru
  ispravnosti.
- **`npm install -g` ne uspeva zbog greške sa dozvolama:** na Linux-u ili WSL-u,
  podesite globalni npm direktorijum u vlasništvu korisnika, dodajte ga u datoteku za pokretanje shell-a,
  a zatim ponovo instalirajte Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Ako koristite `zsh`, dodajte istu `export PATH=...` liniju u `~/.zshrc` umesto
  u `~/.bashrc`.
- **Agent Canvas odbija podešavanja LLM-a nakon postavljanja `custom_tokenizer`:**
  instalirajte `transformers` u Python okruženju Agent Server-a, ponovo pokrenite Agent
  Canvas ako je potrebno, i pokušajte ponovo da sačuvate podešavanja LLM-a. OpenHands-u je potreban
  Transformers da učita chat šablon tokenizatora kada je `custom_tokenizer` postavljen.
- **Agent Canvas ne može da dosegne Lemonade:** proverite
  `curl -fsS "${LEMONADE_BASE_URL}/health"` i potvrdite da se osnovni URL unet u
  formularu za LLM prilikom prvog korišćenja ili u **Settings > LLM** poklapa sa pokrenutim lokalnim
  krajnjim tačkom ili HTTPS tunelom.
- **Podešavanja LLM-a nisu sačuvana:** proverite da li ste kliknuli na **Next** nakon
  unosa vrednosti. Ponovo otvorite **Settings > LLM** da potvrdite da su vrednosti
  sačuvane.
- **GitHub MCP ne može da vidi privatne repozitorijume:** potvrdite da GitHub token ima
  pristup za čitanje ciljnog repozitorijuma i da dugme **Test** za MCP u
  **Customize** prikazuje GitHub alate.
- **Slack može da čita kanale, ali ne može da objavljuje:** pozovite Slack aplikaciju u
  ciljni kanal i potvrdite da bot ima `chat:write`.
- **Automatizacija prikazuje previše Slack kanala:** koristite ID Slack kanala i
  podesite `SLACK_CHANNEL_IDS` na Slack MCP serveru u **Customize**.
- **Pokretanje automatizacije ne uspeva ili prevazilazi kontekst:** potvrdite da je Lemonade pokrenut
  sa `ctx_size=65536`, potvrdite da OpenHands LLM ima postavljen `custom_tokenizer`,
  i koristite eksplicitan repozitorijum sa GitHub skupovima rezultata ograničenim na 3 do 5
  stavki. Ako vaša verzija Agent Canvas-a izlaže podešavanja kondenzatora, postavite maksimalni broj tokena kondenzatora
  ispod granice Lemonade kontekstualnog prozora.

## Sledeći koraci

- Dodajte nedeljni digest samo za izdanja (release).
- Dodajte automatizaciju pokrenutu GitHub događajem za brža upozorenja o PR-ovima ili push-evima.
- Usmerite isti digest ka Notion-u, Linear-u ili nekom drugom alatu podržanom MCP-om.

## Resursi

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Dokumentacija za Lemonade Server](https://lemonade-server.ai/docs)
- [Repozitorijum OpenHands ekstenzija](https://github.com/OpenHands/extensions)
- [Serveri za Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Slack MCP paket](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)