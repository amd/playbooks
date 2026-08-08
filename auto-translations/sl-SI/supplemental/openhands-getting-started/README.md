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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) je programski agent z umetno inteligenco, ki lahko piše kodo, izvaja ukaze, brska po spletu in ureja datoteke v resničnem delovnem prostoru. Namesto kopiranja predlogov iz okna za klepet agenta usmerite na mapo projekta in mu prepustite delo: implementacijo funkcije, odpravo napake, pisanje testov ali razlago kodne baze.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je priporočeni uporabniški vmesnik v brskalniku za zagon OpenHands. En sam ukaz `agent-canvas` skupaj zažene strežnik agenta, avtomatizirano zaledje in spletno čelno stran, tako da lahko pogovor z agentom vodite iz svojega brskalnika.

Da vse ostane na vašem sistemu AMD, se agent pogovarja z lokalnim modelom, ki ga postreže Lemonade Server. Lemonade ta model izpostavi prek API-ja, združljivega z OpenAI, tako da lahko Agent Canvas nastavi njegovo konfiguracijo tako kot pri katerikoli drugi končni točki v slogu OpenAI, medtem ko model, vaša koda in kontekst pogovora ostanejo na vašem računalniku.

V tem priročniku boste zagnali lokalni model, zagnali Agent Canvas, ga usmerili na ta model in izvedli svojo prvo programersko nalogo v resnični mapi projekta.

## Kaj se boste naučili

- Kako zagnati Lemonade Server in potrditi, da lokalni model odgovarja na klepetalne zahteve
- Kako namestiti in zagnati Agent Canvas iz paketa npm
- Kako konfigurirati Agent Canvas za uporabo lokalnega modela Lemonade kot LLM
- Kako začeti pogovor OpenHands in opazovati, kako agent ureja datoteke ter izvaja ukaze v delovnem prostoru
- Kako pregledati, kaj je agent spremenil, in ga usmerjati z nadaljnjimi sporočili

## Ključni koncepti

| Koncept | Kaj je | Kje se umešča v ta priročnik |
| --- | --- | --- |
| Lemonade Server | Lokalna platforma za postrežbo LLM, zgrajena za strojno opremo AMD, ki izpostavi API, združljiv z OpenAI. Vaši podatki nikoli ne zapustijo vašega računalnika. | Poganja model, ki napaja agenta. |
| OpenHands | Programski agent z umetno inteligenco, ki bere in ureja datoteke, izvaja ukaze lupine in brska po spletu znotraj delovnega prostora. | Agent, ki ga usmerjate iz klepeta. |
| Agent Canvas | Uporabniški vmesnik v brskalniku in zaledje, ki poganja pogovore OpenHands ter prikazuje klice orodij in spremembe datotek. | Zažene sklad in gosti vaš pogovor. |
| Delovni prostor | Mapa projekta, ki jo sme agent brati in spreminjati. | Cilj agentovih urejanj in ukazov. |

<!-- @device:stx,krk -->

> [!NOTE]
> Potek dela s programerskim agentom ima koristi od večjega modela in večjega kontekstnega okna. Uporabite vsaj 32 GB pomnilnika sistema, za večje modele GGUF pa raje 64 GB ali več.

<!-- @device:end -->

## Predpogoji

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Potrebujete:

- Nameščen Lemonade Server, ki lahko postreže spodnji model.
- Node.js 22.12 ali novejši ter `npm` (ki ga uporablja CLI `agent-canvas`).
- `uv`, upravitelja paketov Python, ki ga Agent Canvas uporablja za upravljanje okolja strežnika agenta. Če ga vaš sistem še nima, ga namestite iz [vodnika za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/), preden zaženete Agent Canvas.
- Mapo projekta, v kateri boste delali. To je lahko katero koli lokalno skladišče git ali mapa s kodo, na kateri naj agent dela.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Zagon Lemonade Server

Zaženite model iz CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade izpostavi API, združljiv z OpenAI, na:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Preverjanje lokalnega modela

Potrdite, da lahko Lemonade postreže izbrani model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Nato pošljite majhno klepetalno zahtevo:

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

Če to vrne polje `choices`, je Lemonade pripravljen za Agent Canvas.

## 3. Namestitev in zagon Agent Canvas

Globalno namestite objavljeni paket Agent Canvas:

```bash
npm install -g @openhands/agent-canvas
```

Nato zaženite celoten sklad iz terminala:

```bash
agent-canvas
```

Privzeto se Agent Canvas zažene na `http://localhost:8000`. Odprite ta URL v svojem brskalniku. Če vrata 8000 že uporablja kaj drugega, ob zagonu Agent Canvas podajte `--port` (ali `-p`):

```bash
agent-canvas --port 3000
```

Enak ukaz deluje v PowerShellu v sistemu Windows. Nato namesto tega odprite `http://localhost:3000`. Privzeto lokalno zaledje bi se moralo na domačem zaslonu prikazati kot zdravo.

Ukaz `agent-canvas` skupaj zažene strežnik agenta, avtomatizirano zaledje in spletno čelno stran. Za lokalni zagon OpenHands potrebujete samo ta en ukaz.

## 4. Konfiguracija lokalnega LLM

Ob prvem zagonu Agent Canvas odpre potek uvajanja. V tem poteku:

1. Pustite izbran **OpenHands** kot agenta in kliknite **Next**.
2. Na zaslonu **Set up your LLM** izberite **Advanced**.
3. Pustite **Authentication** nastavljeno na **API key**.
4. Nastavite **Custom Model** na `openai/Qwen3.6-35B-A3B-GGUF`.
5. Nastavite **Base URL** na `http://127.0.0.1:13305/api/v1`.
6. Za **API Key** vnesite poljuben neprazen nadomestni niz, na primer `lemonade-local`. Lemonade ne zahteva pravega ključa, vendar odjemalec OpenHands potrebuje vrednost za pošiljanje.
7. Kliknite **Next**.

Dokončane napredne nastavitve bi morale izgledati takole. Polje za API-ključ je v uporabniškem vmesniku prikrito.

![Napredne nastavitve LLM ob prvi uporabi Agent Canvas z modelom Lemonade in lokalnim osnovnim URL-jem](assets/01-llm-advanced-settings.png)

Agent Canvas te vrednosti shrani kot profil LLM. Če vaša različica zahteva ime tega profila, uporabite ime brez presledkov, na primer `lemonade-local`. Če pozneje spremenite modele, odprite **Settings > LLM** in posodobite ista napredna polja. Med shranjenimi profili lahko preklapljate iz vnosnega polja klepeta z ukazom `/model`.

## 5. Odpiranje delovnega prostora

Agent lahko bere in spreminja samo datoteke znotraj delovnega prostora, ki ga izberete. Pred začetkom naloge usmerite Agent Canvas na mapo svojega projekta:

1. Na domačem zaslonu izberite **Open Workspace**.
2. Izberite mapo, ki vsebuje vaš projekt (na primer skladišče git, na katerem naj agent dela).
3. V tem delovnem prostoru začnite nov pogovor.

Vse, kar agent počne — branje datotek, izvajanje ukazov, urejanje kode — je omejeno na ta delovni prostor.

![Domači zaslon Agent Canvas po uvajanju](assets/02-agent-canvas-home.png)
## 6. Zaženite prvo kodirno opravilo

Ko je delovni prostor odprt in izbran lokalni LLM, v klepet vnesite konkretno nalogo. Dobra prva naloga je majhna in preverljiva, na primer:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Spremljajte časovnico pogovora. OpenHands bo:

- Prebral delovni prostor, da razume razporeditev.
- Ustvaril `hello.py` z zahtevano funkcijo in testnim blokom.
- Po možnosti zagnal `python3 hello.py`, da preveri izpis.
- V klepetu poročal, kaj je naredil, in izpis kakršnih koli ukazov.

Videli boste, da se v delovnem prostoru pojavi nova datoteka, agentovo končno sporočilo pa naj bi opisalo narejeno spremembo. To je trenutek izplačila: agent je napisal in zagnal pravo kodo v vaši projektni mapi.

## 7. Preglejte in usmerjajte agenta

Ko agent zaključi korak, pred sprejetjem naslednjega preglejte njegovo delo:

- **Spremembe datotek**: uporabite pregledovalnik datotek delovnega prostora ali agentov pogled razlik, da vidite točno, kaj je bilo dodano, spremenjeno ali izbrisano.
- **Izpis ukazov**: razširite kateri koli ukaz, ki ga je izvedel agent, da vidite stdout, stderr in izhodno kodo.
- **Nadaljnja dejanja**: če rezultat ni tak, kot ste želeli, v istem pogovoru odgovorite s popravkom. Agent ohrani predhodni kontekst in nadaljuje delo na istih datotekah.

Če na primer test ni izpisal pričakovanega pozdrava, odgovorite:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agent bo znova prebral datoteko, zagnal ukaz, diagnosticiral težavo in znova uredil datoteko — vse v istem pogovoru.

## Odpravljanje težav

- **`agent-canvas` ni na poti PATH:** ponovno namestite z
  `npm install -g @openhands/agent-canvas` in preverite, ali je mapa z globalnimi binarnimi datotekami npm na vaši poti PATH. V sistemu Windows zaženite `npm config get prefix`; vrnjena mapa, pogosto `%APPDATA%\npm` ali `%USERPROFILE%\.npm-global`, mora biti na vaši uporabniški poti PATH, preden je mogoče `agent-canvas` zagnati iz novega terminala.
- **`npm install -g` ne uspe zaradi napake dovoljenj:** konfigurirajte globalno mapo npm, ki je v lasti uporabnika, nato znova odprite terminal in ponovno namestite Agent Canvas.

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

  Za trajno spremembo poti PATH v sistemu Windows dodajte `%USERPROFILE%\.npm-global` na svojo uporabniško pot PATH prek **Nastavitve > Sistem > O sistemu > Napredne sistemske nastavitve > Spremenljivke okolja**, in odprite nov terminal.
  <!-- @os:end -->
- **Uporabniški vmesnik se naloži, vendar ozadje kaže kot nezdravo:** počakajte nekaj sekund, da se agentski strežnik zažene do konca, nato osvežite stran. Če ostane nezdravo, znova zaženite `agent-canvas` in preverite izpis terminala za napake.
- **Zahteve za klepet Lemonade ne uspejo z napako povezave:** preverite, ali `curl -fsS "http://127.0.0.1:13305/api/v1/health"` uspe in ali Lemonade še vedno streže model z ukazom `lemonade status`.
- **Agent javi napako v zvezi z dolžino konteksta ali omejitvijo tokenov:** znova zaženite Lemonade z večjim `ctx_size` (na primer `ctx_size=65536`) in začnite nov pogovor, da agent ne nosi prevelike zgodovine.
- **Agent proizvaja slabe ali nepopolne popravke:** preklopite na večji model v Lemonade ali agentu dodelite manjšo, bolj konkretno nalogo in počakajte, da jo dokonča, preden zahtevate naslednjo spremembo.
- **`uv` manjka:** namestite ga iz
  [vodnika za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas uporablja `uv` za upravljanje Python okolja agentskega strežnika.

## Naslednji koraki

- Poskusite z večjo nalogo v istem delovnem prostoru, na primer dodajanjem datoteke z enotskimi testi ali odpravljanjem znane napake, in pred ohranitvijo spremembe preglejte agentove razlike.
- Pod **Prilagodi** povežite strežnik MCP, kot je GitHub ali Slack, da lahko agent med delom bere zadeve (issues) ali objavlja posodobitve.
- Shranite več profilov LLM (hiter majhen model in zmogljivejši velik model) in med njimi preklapljajte z `/model` sredi pogovora.
- Nadaljujte na [avtomatizacije OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), da ponavljajoče se razvojne zanke spremenite v načrtovane ali dogodkovno sprožene zagone agenta.

## Viri

- [Dokumentacija OpenHands](https://docs.openhands.dev/)
- [Pregled Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Nastavitev Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profili LLM in konfiguracija modelov](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Dokumentacija Lemonade Server](https://lemonade-server.ai/docs)