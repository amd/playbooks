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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je AI softverski agent
koji može da piše kod, pokreće komande, pretražuje veb i uređuje fajlove u pravom
radnom okruženju. Umesto da kopirate predloge iz prozora za ćaskanje, usmerite
agenta na fasciklu projekta i pustite ga da obavi posao: implementira funkciju, popravi
grešku, napiše testove ili objasni bazu koda.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je preporučeni
korisnički interfejs u pregledaču za pokretanje OpenHands-a. Jedna komanda `agent-canvas`
pokreće server agenta, pozadinski sistem za automatizaciju i veb frontend zajedno, tako da možete
da vodite razgovor sa agentom iz svog pregledača.

Da bi sve ostalo na vašem AMD sistemu, agent komunicira sa lokalnim modelom koji opslužuje
Lemonade Server. Lemonade izlaže taj model kroz API kompatibilan sa OpenAI,
tako da Agent Canvas može da ga konfiguriše kao bilo koji drugi krajnji punkt u OpenAI stilu,
dok model, vaš kod i kontekst razgovora ostaju na
vašem računaru.

U ovom priručniku ćete pokrenuti lokalni model, pokrenuti Agent Canvas, usmeriti ga
na taj model i pokrenuti svoj prvi zadatak kodiranja nad pravom fasciklom projekta.

## Šta ćete naučiti

- Kako da pokrenete Lemonade Server i potvrdite da lokalni model odgovara na zahteve za ćaskanje
- Kako da instalirate i pokrenete Agent Canvas iz npm paketa
- Kako da konfigurišete Agent Canvas da koristi lokalni Lemonade model kao LLM
- Kako da pokrenete OpenHands razgovor i posmatrate kako agent uređuje fajlove i pokreće
  komande u radnom okruženju
- Kako da pregledate šta je agent promenio i usmerite ga naknadnim porukama

## Osnovni koncepti

| Koncept | Šta je to | Gde se uklapa u ovom priručniku |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za opsluživanje LLM-a napravljena za AMD hardver koja izlaže API kompatibilan sa OpenAI. Vaši podaci nikada ne napuštaju vaš računar. | Pokreće model koji pokreće agenta. |
| OpenHands | AI softverski agent koji čita i uređuje fajlove, pokreće komande ljuske i pretražuje veb unutar radnog okruženja. | Agent kojim upravljate iz ćaskanja. |
| Agent Canvas | Korisnički interfejs u pregledaču i pozadinski sistem koji pokreće OpenHands razgovore i prikazuje pozive alata i promene fajlova. | Pokreće sistem i ugošćuje vaš razgovor. |
| Radno okruženje | Fascikla projekta koju agent sme da čita i menja. | Cilj agentovih izmena i komandi. |

<!-- @device:stx,krk -->
> [!NOTE]
> Radni tokovi agenta za kodiranje imaju koristi od većeg modela i prozora konteksta. Koristite
> bar 32 GB sistemske memorije, a poželjno je 64 GB ili više za veće GGUF modele.
<!-- @device:end -->

## Preduslovi

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrebno vam je:

- Instaliran Lemonade Server koji može da opslužuje model naveden ispod.
- Node.js 22.12 ili noviji i `npm` (koje koristi `agent-canvas` CLI).
- `uv`, Python menadžer paketa koji Agent Canvas koristi za upravljanje okruženjem
  servera agenta. Ako vaš sistem to već nema, instalirajte ga iz
  [uv vodiča za instalaciju](https://docs.astral.sh/uv/getting-started/installation/)
  pre pokretanja Agent Canvas-a.
- Fascikla projekta u kojoj ćete raditi. To može biti bilo koji lokalni git repozitorijum ili
  direktorijum sa kodom na kome želite da agent radi.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Pokrenite Lemonade Server

Pokrenite model iz Lemonade CLI-ja:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade izlaže API kompatibilan sa OpenAI na:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Proverite lokalni model

Potvrdite da Lemonade može da opslužuje izabrani model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Zatim pošaljite mali zahtev za ćaskanje:

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

Ako ovo vrati niz `choices`, Lemonade je spreman za Agent Canvas.

## 3. Instalirajte i pokrenite Agent Canvas

Instalirajte objavljeni Agent Canvas paket globalno:

```bash
npm install -g @openhands/agent-canvas
```

Zatim pokrenite ceo sistem iz terminala:

```bash
agent-canvas
```

Podrazumevano, Agent Canvas se pokreće na `http://localhost:8000`. Otvorite tu adresu u
svom pregledaču. Ako je port 8000 već zauzet, prosledite `--port` (ili `-p`) prilikom
pokretanja Agent Canvas-a:

```bash
agent-canvas --port 3000
```

Ista komanda radi u PowerShell-u na Windows-u. Zatim otvorite
`http://localhost:3000` umesto toga. Podrazumevani lokalni backend bi trebalo da se
prikaže kao ispravan na početnom ekranu.

Komanda `agent-canvas` pokreće server agenta, pozadinski sistem za automatizaciju i
veb frontend zajedno. Potrebna vam je samo ova jedna komanda da biste pokrenuli OpenHands
lokalno.

## 4. Konfigurišite lokalni LLM

Pri prvom pokretanju, Agent Canvas otvara tok za uvođenje u rad. U tom toku:

1. Zadržite **OpenHands** izabran kao agenta i kliknite na **Next**.
2. Na **Set up your LLM**, izaberite **Advanced**.
3. Zadržite **Authentication** postavljeno na **API key**.
4. Postavite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Postavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key**, unesite bilo koji nepraznu zamensku vrednost, kao što je `lemonade-local`.
   Lemonade ne zahteva pravi ključ, ali OpenHands klijentu je potrebna vrednost
   koju će poslati.
7. Kliknite na **Next**.

Popunjena Advanced podešavanja bi trebalo da izgledaju ovako. Polje za API ključ je
maskirano od strane korisničkog interfejsa.

![Agent Canvas prvo korišćenje LLM Advanced podešavanja sa Lemonade modelom i lokalnom baznom adresom](assets/01-llm-advanced-settings.png)

Agent Canvas čuva ove vrednosti kao LLM profil. Ako vaša verzija traži da
nazovete taj profil, koristite naziv bez razmaka, kao što je `lemonade-local`. Ako kasnije
promenite modele, otvorite **Settings > LLM** i ažurirajte ista Advanced polja. Možete
da menjate sačuvane profile iz polja za unos u ćaskanju pomoću komande `/model`.

## 5. Otvorite radno okruženje

Agent može da čita i menja samo fajlove unutar radnog okruženja koje izaberete. Pre
pokretanja zadatka, usmerite Agent Canvas na svoju fasciklu projekta:

1. Sa početnog ekrana, izaberite **Open Workspace**.
2. Izaberite fasciklu koja sadrži vaš projekat (na primer, git repozitorijum
   na kome želite da agent radi).
3. Pokrenite novi razgovor u tom radnom okruženju.

Sve što agent radi—čitanje fajlova, pokretanje komandi, uređivanje koda—je
ograničeno na to radno okruženje.

![Agent Canvas početni ekran nakon uvođenja u rad](assets/02-agent-canvas-home.png)
## 6. Pokrenite svoj prvi zadatak kodiranja

Kada je radni prostor otvoren i izabran lokalni LLM, unesite konkretan zadatak u
ćaskanje. Dobar prvi zadatak je mali i proverljiv, na primer:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Pratite vremensku liniju konverzacije. OpenHands će:

- Pročitati radni prostor da razume raspored.
- Kreirati `hello.py` sa traženom funkcijom i test blokom.
- Opciono pokrenuti `python3 hello.py` da bi proverio izlaz.
- Prijaviti šta je uradio i bilo koji izlaz komande u ćaskanju.

Trebalo bi da vidite kako se pojavljuje novi fajl u radnom prostoru, a agentova
konačna poruka treba da opisuje izmenu koju je napravio. Ovo je trenutak isplate:
agent je napisao i pokrenuo pravi kod u vašem folderu projekta.

## 7. Pregledajte i usmerite agenta

Nakon što agent završi korak, pregledajte njegov rad pre nego što prihvatite sledeći:

- **Izmene fajla**: koristite pregledač fajlova u radnom prostoru ili agentov prikaz razlika
  da vidite tačno šta je dodato, promenjeno ili obrisano.
- **Izlaz komande**: proširite bilo koju komandu koju je agent pokrenuo da vidite stdout, stderr,
  i izlazni kod.
- **Praćenja**: ako rezultat nije ono što ste želeli, odgovorite u istoj
  konverzaciji sa ispravkom. Agent zadržava prethodni kontekst i
  iterira na istim fajlovima.

Na primer, ako test nije ispisao očekivani pozdrav, odgovorite:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent će ponovo pročitati fajl, pokrenuti komandu, dijagnostikovati problem i izmeniti
fajl ponovo—sve u istoj konverzaciji.

## Rešavanje problema

- **`agent-canvas` nije na PATH:** ponovo instalirajte pomoću
  `npm install -g @openhands/agent-canvas` i potvrdite da je globalni npm binarni
  direktorijum na vašem PATH-u. Na Windows-u, pokrenite `npm config get prefix`; vraćeni
  direktorijum, često `%APPDATA%\npm` ili `%USERPROFILE%\.npm-global`,
  mora biti na vašem korisničkom PATH-u pre nego što se `agent-canvas` može pokrenuti iz novog
  terminala.
- **`npm install -g` ne uspeva sa greškom dozvola:** konfigurišite korisnički vlasnički
  globalni npm direktorijum, zatim ponovo otvorite terminal i ponovo instalirajte Agent Canvas.

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

  Da biste trajno napravili promenu Windows PATH-a, dodajte `%USERPROFILE%\.npm-global` na
  vaš korisnički PATH iz **Settings > System > About > Advanced system settings >
  Environment Variables**, i otvorite novi terminal.
  <!-- @os:end -->
- **UI se učitava ali pozadinski deo prikazuje nezdravo stanje:** sačekajte nekoliko sekundi da
  agentov server završi pokretanje, zatim osvežite. Ako i dalje ostane nezdrav, ponovo pokrenite
  `agent-canvas` i proverite izlaz terminala za greške.
- **Lemonade zahtevi za ćaskanje ne uspevaju sa greškom u vezi:** potvrdite da
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` uspeva i da
  Lemonade i dalje servira model pomoću `lemonade status`.
- **Agent prijavljuje grešku sa dužinom konteksta ili ograničenjem tokena:** ponovo pokrenite
  Lemonade sa većim `ctx_size` (na primer `ctx_size=65536`), i započnite
  novu konverzaciju kako agent ne bi nosio prevelikitu istoriju.
- **Agent proizvodi izmene niskog kvaliteta ili nepotpune:** pređite na veći
  model u Lemonade, ili dajte agentu manji, konkretniji zadatak i pustite ga da
  završi pre nego što tražite sledeću izmenu.
- **`uv` nedostaje:** instalirajte ga sa
  [vodiča za instalaciju uv-a](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas koristi `uv` za upravljanje Python okruženjem agentovog servera.

## Sledeći koraci

- Probajte veći zadatak u istom radnom prostoru, kao što je dodavanje fajla jediničnog testa ili
  ispravljanje poznate greške, i pregledajte agentove razlike pre zadržavanja izmene.
- Povežite MCP server kao što je GitHub ili Slack pod **Customize** kako bi
  agent mogao da čita probleme ili objavljuje ažuriranja dok radi.
- Sačuvajte nekoliko LLM profila (brz mali model i jači veliki model) i
  prebacujte se između njih pomoću `/model` u toku konverzacije.
- Pređite na [OpenHands automatizacije](https://docs.openhands.dev/openhands/usage/automations/overview) da
  pretvorite ponavljajuće razvojne petlje u zakazana ili događajima pokrenuta pokretanja agenta.

## Resursi

- [OpenHands dokumentacija](https://docs.openhands.dev/)
- [Pregled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Podešavanje Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profili i konfiguracija modela](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacija Lemonade Server](https://lemonade-server.ai/docs)