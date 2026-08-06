<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Prezentare generală

[OpenHands](https://github.com/All-Hands-AI/OpenHands) este un agent software AI
care poate scrie cod, poate rula comenzi, poate naviga pe web și poate edita fișiere într-un
spațiu de lucru real. În loc să copiați sugestii dintr-o fereastră de chat, îndreptați
agentul către un folder de proiect și îl lăsați să facă treaba: implementează o funcționalitate, remediază
o eroare, scrie teste sau explică o bază de cod.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) este interfața de utilizator
browser recomandată pentru rularea OpenHands. O singură comandă `agent-canvas` pornește
serverul agentului, backend-ul de automatizare și frontend-ul web împreună, astfel încât puteți
conduce o conversație cu agentul din browserul dvs.

Pentru a păstra totul pe sistemul dvs. AMD, agentul comunică cu un model local servit
de Lemonade Server. Lemonade expune acel model printr-un API compatibil cu
OpenAI, astfel încât Agent Canvas îl poate configura ca orice alt endpoint în stil OpenAI,
în timp ce modelul, codul dvs. și contextul conversației rămân toate pe
mașina dvs.

În acest playbook, veți porni un model local, veți lansa Agent Canvas, îl veți îndrepta
către acel model și veți rula prima sarcină de codare pe un folder de proiect real.

## Ce veți învăța

- Cum să porniți Lemonade Server și să confirmați că un model local răspunde la cererile de chat
- Cum să instalați și să lansați Agent Canvas din pachetul npm
- Cum să configurați Agent Canvas pentru a utiliza un model Lemonade local ca LLM
- Cum să porniți o conversație OpenHands și să urmăriți agentul editând fișiere și rulând
  comenzi într-un spațiu de lucru
- Cum să revizuiți ce a schimbat agentul și să îl direcționați cu mesaje ulterioare

## Concepte de bază

| Concept | Ce este | Unde se încadrează în acest playbook |
| --- | --- | --- |
| Lemonade Server | O platformă locală de servire LLM construită pentru hardware AMD care expune un API compatibil cu OpenAI. Datele dvs. nu părăsesc niciodată mașina dvs. | Rulează modelul care alimentează agentul. |
| OpenHands | Un agent software AI care citește și editează fișiere, rulează comenzi shell și navighează pe web în interiorul unui spațiu de lucru. | Agentul pe care îl conduceți din chat. |
| Agent Canvas | Interfața de utilizator browser și backend-ul care rulează conversații OpenHands și afișează apelurile de instrumente și modificările de fișiere. | Lansează stiva și găzduiește conversația dvs. |
| Spațiu de lucru | Folderul de proiect pe care agentul are voie să îl citească și să îl modifice. | Ținta editărilor și comenzilor agentului. |

<!-- @device:stx,krk -->
> [!NOTE]
> Fluxurile de lucru ale agenților de codare beneficiază de un model și o fereastră de context mai mari. Utilizați
> cel puțin 32 GB de memorie de sistem și preferați 64 GB sau mai mult pentru modele GGUF mai mari.
<!-- @device:end -->

## Cerințe preliminare

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Aveți nevoie de:

- Lemonade Server instalat și capabil să servească modelul de mai jos.
- Node.js 22.12 sau o versiune ulterioară și `npm` (utilizat de CLI-ul `agent-canvas`).
- `uv`, managerul de pachete Python pe care Agent Canvas îl utilizează pentru a gestiona mediul
  serverului agentului. Dacă sistemul dvs. nu îl are deja, instalați-l din
  [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/)
  înainte de a lansa Agent Canvas.
- Un folder de proiect în care să lucrați. Acesta poate fi orice depozit git local sau director de
  cod pe care doriți ca agentul să lucreze.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Porniți Lemonade Server

Porniți modelul din CLI-ul Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade expune un API compatibil cu OpenAI la:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Verificați modelul local

Confirmați că Lemonade poate servi modelul selectat:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Apoi trimiteți o cerere mică de chat:

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

Dacă aceasta returnează un array `choices`, Lemonade este pregătit pentru Agent Canvas.

## 3. Instalați și lansați Agent Canvas

Instalați global pachetul Agent Canvas publicat:

```bash
npm install -g @openhands/agent-canvas
```

Apoi porniți stiva completă dintr-un terminal:

```bash
agent-canvas
```

Implicit, Agent Canvas pornește la `http://localhost:8000`. Deschideți acel URL în
browserul dvs. Dacă portul 8000 este deja utilizat, transmiteți `--port` (sau `-p`) când
lansați Agent Canvas:

```bash
agent-canvas --port 3000
```

Aceeași comandă funcționează în PowerShell pe Windows. Apoi deschideți
`http://localhost:3000` în loc. Backend-ul local implicit ar trebui să apară ca
sănătos pe ecranul de pornire.

Comanda `agent-canvas` pornește serverul agentului, backend-ul de automatizare și
frontend-ul web împreună. Aveți nevoie doar de această singură comandă pentru a rula OpenHands
local.

## 4. Configurați LLM-ul local

La prima lansare, Agent Canvas deschide un flux de onboarding. În acel flux:

1. Păstrați **OpenHands** selectat ca agent și faceți clic pe **Next**.
2. La **Set up your LLM**, selectați **Advanced**.
3. Păstrați **Authentication** setat la **API key**.
4. Setați **Custom Model** la `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setați **Base URL** la `http://127.0.0.1:13305/api/v1`.
6. Pentru **API Key**, introduceți orice substituent non-gol, cum ar fi `lemonade-local`.
   Lemonade nu necesită o cheie reală, dar clientul OpenHands are nevoie de o valoare
   pentru a trimite.
7. Faceți clic pe **Next**.

Setările Advanced finalizate ar trebui să arate astfel. Câmpul cheii API este
mascat de interfața de utilizator.

![Setările LLM Advanced la prima utilizare Agent Canvas cu modelul Lemonade și URL-ul de bază local](assets/01-llm-advanced-settings.png)

Agent Canvas salvează aceste valori ca profil LLM. Dacă versiunea dvs. vă cere să
denumiți acel profil, utilizați un nume fără spații, cum ar fi `lemonade-local`. Dacă schimbați
modele mai târziu, deschideți **Settings > LLM** și actualizați aceleași câmpuri Advanced. Puteți
comuta profilurile salvate din câmpul de chat cu comanda `/model`.

## 5. Deschideți un spațiu de lucru

Agentul poate citi și modifica doar fișiere în interiorul unui spațiu de lucru pe care îl alegeți. Înainte de
a începe o sarcină, îndreptați Agent Canvas către folderul dvs. de proiect:

1. Din ecranul de pornire, alegeți **Open Workspace**.
2. Selectați folderul care conține proiectul dvs. (de exemplu, un depozit git
   pe care doriți ca agentul să lucreze).
3. Începeți o conversație nouă în acel spațiu de lucru.

Tot ceea ce face agentul—citirea fișierelor, rularea comenzilor, editarea codului—este
limitat la acel spațiu de lucru.

![Pagina de pornire Agent Canvas după onboarding](assets/02-agent-canvas-home.png)
## 6. Rulați prima sarcină de codare

Cu spațiul de lucru deschis și LLM-ul local selectat, introduceți o sarcină concretă în
chat. O primă sarcină bună este mică și verificabilă, de exemplu:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Urmăriți cronologia conversației. OpenHands va:

- Citi spațiul de lucru pentru a înțelege structura.
- Crea `hello.py` cu funcția solicitată și blocul de test.
- Opțional, rula `python3 hello.py` pentru a verifica rezultatul.
- Raporta ce a făcut și orice rezultat al comenzii în chat.

Ar trebui să vedeți fișierul nou apărând în spațiul de lucru, iar mesajul final al
agentului ar trebui să descrie modificarea făcută. Acesta este momentul de recompensă: agentul a scris și a rulat cod real în folderul proiectului dumneavoastră.

## 7. Revizuiți și ghidați agentul

După ce agentul finalizează un pas, revizuiți-i munca înainte de a accepta următorul pas:

- **Modificări de fișiere**: folosiți browserul de fișiere al spațiului de lucru sau vizualizarea diff a agentului pentru a
  vedea exact ce a fost adăugat, modificat sau șters.
- **Rezultatul comenzilor**: extindeți orice comandă rulată de agent pentru a vedea stdout, stderr
  și codul de ieșire.
- **Continuări**: dacă rezultatul nu este cel dorit, răspundeți în aceeași
  conversație cu o corecție. Agentul păstrează contextul anterior și
  iterează pe aceleași fișiere.

De exemplu, dacă testul nu a afișat salutul așteptat, răspundeți:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Agentul va reciti fișierul, va rula comanda, va diagnostica problema și va edita
din nou fișierul—toate în aceeași conversație.

## Depanare

- **`agent-canvas` nu se află în PATH:** reinstalați cu
  `npm install -g @openhands/agent-canvas` și confirmați că directorul binar
  global npm se află în PATH. Pe Windows, rulați `npm config get prefix`; directorul
  returnat, adesea `%APPDATA%\npm` sau `%USERPROFILE%\.npm-global`,
  trebuie să fie în PATH-ul utilizatorului înainte ca `agent-canvas` să poată fi lansat dintr-un terminal
  nou.
- **`npm install -g` eșuează cu o eroare de permisiuni:** configurați un director
  global npm deținut de utilizator, apoi redeschideți terminalul și instalați din nou Agent Canvas.

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

  Pentru a face permanentă modificarea PATH-ului pe Windows, adăugați `%USERPROFILE%\.npm-global` la
  PATH-ul utilizatorului din **Settings > System > About > Advanced system settings >
  Environment Variables**, și deschideți un terminal nou.
  <!-- @os:end -->
- **Interfața se încarcă, dar backend-ul arată ca nefiind sănătos (unhealthy):** așteptați câteva secunde pentru ca
  serverul agentului să termine pornirea, apoi reîmprospătați pagina. Dacă rămâne nesănătos, reporniți
  `agent-canvas` și verificați rezultatul terminalului pentru erori.
- **Cererile de chat Lemonade eșuează cu o eroare de conexiune:** confirmați că
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` reușește și că
  Lemonade încă servește modelul cu `lemonade status`.
- **Agentul returnează o eroare legată de lungimea contextului sau limita de token-uri:** reporniți
  Lemonade cu un `ctx_size` mai mare (de exemplu `ctx_size=65536`), și începeți o
  conversație nouă astfel încât agentul să nu poarte un istoric prea mare.
- **Agentul produce editări de calitate slabă sau incomplete:** treceți la un
  model mai mare în Lemonade, sau oferiți agentului o sarcină mai mică și mai concretă și lăsați-l
  să o finalizeze înainte de a cere următoarea modificare.
- **`uv` lipsește:** instalați-l din
  [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas folosește `uv` pentru a gestiona mediul Python al serverului agentului.

## Pașii următori

- Încercați o sarcină mai mare în același spațiu de lucru, cum ar fi adăugarea unui fișier de test unitar sau
  corectarea unei erori cunoscute, și revizuiți diff-ul agentului înainte de a păstra modificarea.
- Conectați un server MCP precum GitHub sau Slack sub **Customize** pentru ca
  agentul să poată citi issue-uri sau posta actualizări în timp ce lucrează.
- Salvați mai multe profiluri LLM (un model mic și rapid și un model mare și mai puternic) și
  comutați între ele cu `/model` în timpul conversației.
- Treceți la [automatizări OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) pentru a
  transforma buclele de dezvoltare recurente în execuții de agenți programate sau declanșate de evenimente.

## Resurse

- [Documentația OpenHands](https://docs.openhands.dev/)
- [Prezentare generală Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configurarea Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Profiluri LLM și configurarea modelului](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentația Lemonade Server](https://lemonade-server.ai/docs)