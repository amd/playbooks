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

Dezvoltatorii petrec mult timp în bucle mici și recurente: analizarea
pull request-urilor etichetate, răspunsul la comentarii GitHub, triajul
issue-urilor noi, transformarea firelor de discuție Slack în note de standup
sau follow-up-uri pentru incidente și urmărirea semnalelor de lansare sau de
cercetare. Fiecare buclă este familiară, dar necesită totuși discernământ:
adunarea contextului potrivit, decizia asupra a ceea ce contează și postarea
unei actualizări clare acolo unde echipa lucrează deja.

[Automatizările OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
transformă aceste bucle în conversații de agent programate sau declanșate de
evenimente: rulări în care un agent software AI poate citi context, poate
apela instrumente și poate produce o actualizare. Șabloanele de automatizare
partajate din catalogul de extensii OpenHands urmează acest tipar pentru
revizuirea pull request-urilor GitHub, monitorizarea repository-urilor,
triajul issue-urilor Linear, retrospectivele incidentelor, digestele de
standup Slack și rapoartele de cercetare: o automatizare se activează,
folosește integrări configurate precum GitHub sau Slack pentru a obține
context, raționează asupra acelui context cu un model de limbaj de mari
dimensiuni (LLM) și scrie înapoi un rezultat.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) este planul de
control local pentru construirea și testarea acestor automatizări. În acest
playbook, acesta rulează un OpenHands Agent Server, procesul back-end care
execută conversațiile agentului, și conectează agentul la servicii externe
precum GitHub și Slack.

Pentru a păstra fluxul de lucru pe sistemul dvs. AMD, agentul comunică cu un
model local servit de Lemonade Server. Lemonade expune acel model printr-un
API compatibil OpenAI, astfel încât Agent Canvas îl poate configura ca un
endpoint la distanță de tip OpenAI, în timp ce modelul, promptul și contextul
fluxului de lucru rămân locale.

În acest playbook, veți construi o automatizare concretă: un digest programat
de dezvoltare GitHub-către-Slack. Acesta folosește GitHub pentru a inspecta
activitatea recentă a repository-ului, Slack pentru a posta digestul, apeluri
API Agent Canvas pentru a configura și testa automatizarea, și Lemonade pentru
a rula LLM-ul local.

![Diagramă de arhitectură care arată GitHub MCP, automatizarea OpenHands, Lemonade Server și Slack MCP](assets/00-architecture-overview.png)

## Ce veți învăța

- Cum să porniți Lemonade Server și să verificați că un model local răspunde
  la solicitări de chat
- Cum să lansați Agent Canvas și să direcționați Agent Server-ul acestuia
  către un LLM local
- Cum să instalați serverele Model Context Protocol (MCP) pentru GitHub și
  Slack prin API-ul Agent Server
- Cum să creați și să dispatch-ați o automatizare OpenHands programată care
  postează un digest de dezvoltare pe Slack
- Cum să depanați cele mai frecvente erori legate de modelul local și de
  automatizare

## Concepte de bază

| Concept | Ce reprezintă | Unde se potrivește în acest playbook |
| --- | --- | --- |
| Lemonade Server | O platformă locală de servire LLM construită pentru hardware AMD, care expune un API compatibil OpenAI. Datele dvs. nu părăsesc niciodată mașina. | Rulează modelul care alimentează agentul. |
| OpenHands Agent Server | Procesul back-end care execută conversațiile agentului OpenHands. | Găzduiește agentul, profilul său LLM și serverele sale MCP. |
| Agent Canvas | Planul de control local pentru OpenHands care rulează Agent Server și o interfață pentru inspectarea rulărilor agentului. | Lansează back-end-urile și oferă API-ul pe care îl apelați. |
| Server MCP | Un server Model Context Protocol care oferă unui agent instrumente pentru un serviciu extern precum GitHub sau Slack. | Permite agentului să citească din GitHub și să scrie în Slack. |
| Automatizare OpenHands | O conversație de agent programată sau declanșată de evenimente care obține context, raționează asupra acestuia și scrie undeva un rezultat. | Digestul GitHub-către-Slack pe care îl construiți aici. |

<!-- @device:stx,krk -->
> [!NOTE]
> Fluxurile de lucru cu agenți de codare beneficiază de un model și o fereastră
> de context mai mari. Folosiți cel puțin 32 GB de memorie de sistem și
> preferați 64 GB sau mai mult pentru modele GGUF mai mari.
<!-- @device:end -->

## Cerințe preliminare

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Aveți nevoie de:

- Lemonade Server instalat urmând ghidul standard de
  [instalare Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 sau o versiune ulterioară și `npm`, folosite pentru a instala
  CLI-ul Agent Canvas publicat și pentru a rula servere MCP cu `npx`.
- Un pachet `@openhands/agent-canvas` publicat recent, cu setări de agent
  bazate pe schemă, `LLMSummarizingCondenserSettings.max_tokens` și suport
  pentru `custom_tokenizer` al LLM-ului.
- Pachetul Python `transformers` disponibil în mediul Agent Server. Este
  necesar pentru numărarea tokenilor pe baza șabloanelor de chat atunci când
  este setat `custom_tokenizer`.
- Un token GitHub cu acces de citire la repository-ul pe care doriți să-l
  rezumați.
- Un token de bot Slack (`xoxb-...`) cu `chat:write` și acces de citire la canal.
- Un ID de echipă Slack (`T...`).
- Un ID de canal Slack (`C...`) unde ar trebui postat digestul.

Invitați aplicația Slack în canalul țintă înainte de a testa automatizarea.

## Variabile folosite în acest playbook

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

Următoarele valori sunt introduse în interfața Agent Canvas la pașii
ulteriori. Setați-le aici, astfel încât să le puteți copia:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Folosiți o valoare explicită `owner/repo` pentru `GITHUB_REPO_FILTER`.
Wildcard-urile largi la nivel de organizație pot returna prea mult context MCP
pentru modelele locale.

## 1. Porniți Lemonade Server

Porniți modelul din CLI-ul Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade expune un API compatibil OpenAI la:

```text
http://127.0.0.1:13305/api/v1
```

Opțional: dacă Agent Canvas sau executorul de automatizare nu se află pe
aceeași mașină, publicați endpoint-ul Lemonade printr-un tunel securizat și
folosiți URL-ul HTTPS ca URL de bază pentru LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificați modelul local

Confirmați că Lemonade poate servi modelul selectat:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Apoi trimiteți o solicitare mică de chat:

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

Dacă aceasta returnează un array `choices`, Lemonade este pregătit pentru
Agent Canvas.
## 3. Pornirea Agent Canvas

Instalați pachetul Agent Canvas publicat și porniți întregul stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Dacă instalarea globală npm eșuează cu o eroare de permisiuni, consultați
secțiunea de depanare a permisiunilor npm de mai jos.

În mod implicit, Agent Canvas pornește la `http://localhost:8000`. Deschideți
această adresă URL în browser. Backend-ul local implicit ar trebui să apară ca
sănătos pe ecranul principal.

Comanda `agent-canvas` pornește împreună serverul de agenți, backend-ul de
automatizare și interfața web. Este nevoie doar de această singură comandă
pentru a rula OpenHands local. Restul acestui ghid configurează totul prin
interfața Agent Canvas din browser.

## 4. Configurarea LLM-ului local în interfață

La prima lansare, Agent Canvas deschide un flux de configurare inițială. În
acest flux:

1. Păstrați **OpenHands** selectat ca agent și faceți clic pe **Next**.
2. La **Set up your LLM**, selectați **Advanced**.
3. Păstrați **Authentication** setat la **API key**.
4. Setați **Custom Model** la valoarea `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Setați **Base URL** la `http://127.0.0.1:13305/api/v1`.
6. Pentru **API Key**, introduceți orice valoare de umplere ne-goală, precum
   `lemonade-local`. Lemonade nu necesită o cheie reală, dar clientul OpenHands
   are nevoie de o valoare pentru a o trimite.

Câmpurile de conexiune ar trebui să arate astfel. Câmpul cheii API este
mascat de interfață.

![Setări avansate LLM la prima utilizare a Agent Canvas cu modelul Lemonade și adresa URL locală de bază](assets/01-llm-advanced-settings.png)

Apoi selectați **All** și setați câmpurile suplimentare pentru modelul local:

1. Derulați până la **Custom Tokenizer** și setați-l la `Qwen/Qwen3.6-35B-A3B`.
2. Derulați până la **LiteLLM Extra Body** și setați-l la
   `{"enable_thinking": true}`.
3. Faceți clic pe **Next**.

![Fila All pentru LLM la prima utilizare a Agent Canvas cu tokenizatorul personalizat Qwen](assets/02-llm-all-tokenizer-settings.png)

![Fila All pentru LLM la prima utilizare a Agent Canvas cu corpul extra LiteLLM configurat](assets/03-llm-all-extra-body-settings.png)

Setările LLM ar trebui să arate astfel:

| Câmp | Valoare |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Prefixul `openai/` indică LiteLLM să utilizeze formatarea cererilor compatibilă
cu OpenAI pentru endpoint-ul Lemonade. Tokenizatorul personalizat este
tokenizatorul original Hugging Face pentru modelul GGUF; acesta permite
OpenHands să numere aceleași token-uri de șablon de chat pe care le vede
serverul local al modelului. Formularul actual LLM de la prima utilizare nu
afișează setările de condenser. Dacă versiunea dvs. de Agent Canvas expune mai
târziu setările de condenser sub **Settings > LLM**, utilizați
`llm_summarizing` și setați numărul maxim de token-uri sub fereastra de
context Lemonade, precum `56000`.

## 5. Instalarea serverelor MCP pentru GitHub și Slack

În interfața Agent Canvas, deschideți **Customize** (sau **Settings > MCP**)
pentru a adăuga serverele MCP care oferă agentului instrumente pentru GitHub
și Slack. Valorile token-urilor sunt trimise doar către Agent Server-ul local
și sunt persistate ca setări criptate.

### Serverul MCP GitHub

Adăugați un nou server MCP cu aceste setări:

| Câmp | Valoare |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = tokenul dvs. GitHub |

Utilizați un token GitHub cu acces de citire la depozitul pe care doriți să-l
rezumați.

### Serverul MCP Slack

Adăugați un al doilea server MCP cu aceste setări:

| Câmp | Valoare |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID-ul canalului dvs. de digest |

Setați `SLACK_CHANNEL_IDS` la ID-ul canalului de digest (aceeași valoare ca
`SLACK_DIGEST_CHANNEL`) astfel încât agentul să nu fie nevoit să parcurgă
fiecare canal Slack.

După adăugarea ambelor servere, utilizați butonul **Test** de pe fiecare
pentru a confirma că se conectează și anunță instrumentele disponibile.
Serverul GitHub ar trebui să listeze instrumente GitHub, iar serverul Slack ar
trebui să listeze instrumente Slack.

![Pagina MCP din Agent Canvas cu serverele GitHub și Slack instalate](assets/04-mcp-servers-installed.png)

## 6. Crearea automatizării de digest

În interfața Agent Canvas, deschideți pagina **Automations** și creați o nouă
automatizare:

1. Alegeți **Create automation** și selectați tipul **Prompt preset**.
2. Setați **Name** la `GitHub Development Digest to Slack`.
3. Setați **Prompt** la următorul text, înlocuind marcajele pentru depozit și
   canal cu valorile dvs.:

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

4. Setați **Trigger** la **Cron** cu programul `0 9 * * 1-5` (ora 9 dimineața
   în zilele lucrătoare) și setați **Timezone** la fusul dvs. orar, de
   exemplu `America/New_York`.
5. Setați **Timeout** la `900` secunde.
6. Salvați automatizarea.

Pagina de detalii a automatizării afișează noua automatizare împreună cu
declanșatorul cron și punctul de intrare generat pentru prompt-preset.

![Pagina de detalii a automatizării din Agent Canvas după creare](assets/05-automation-created.png)
## 7. Testarea automatizării

Din pagina de detalii a automatizării din interfața Agent Canvas UI:

1. Faceți clic pe **Run now** (sau **Dispatch**) pentru a rula automatizarea o dată, imediat.
2. Urmăriți lista de execuții din aceeași pagină. Ultima execuție ar trebui să treacă în starea
   `COMPLETED`.
3. Deschideți canalul Slack țintă. Ar trebui să conțină rezumatul generat.

Nu este nevoie să așteptați declanșarea programării cron—**Run now** declanșează o
execuție la cerere, astfel încât să puteți confirma că prompt-ul, conexiunile MCP și publicarea pe Slack
funcționează toate corect înainte de a vă baza pe programare.

![Execuție automatizare Agent Canvas finalizată cu succes](assets/06-automation-run-completed.png)

![Canal Slack afișând rezumatul OpenHands generat](assets/07-slackbot-message.png)

## Depanare

- **Lemonade este oprit:** reporniți-l cu comanda
  `lemonade run "${LEMONADE_MODEL}"` din pasul 1, apoi rulați din nou verificarea
  de sănătate.
- **`npm install -g` eșuează cu o eroare de permisiuni:** pe Linux sau WSL,
  configurați un director global npm deținut de utilizator, adăugați-l în fișierul de pornire
  al shell-ului, apoi instalați din nou Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Dacă folosiți `zsh`, adăugați aceeași linie `export PATH=...` în `~/.zshrc` în loc
  de `~/.bashrc`.
- **Agent Canvas respinge setările LLM după configurarea `custom_tokenizer`:**
  instalați `transformers` în mediul Python al Agent Server, reporniți Agent
  Canvas dacă este necesar și reîncercați salvarea setărilor LLM. OpenHands necesită
  Transformers pentru a încărca șablonul de chat al tokenizatorului atunci când este setat `custom_tokenizer`.
- **Agent Canvas nu poate ajunge la Lemonade:** verificați
  `curl -fsS "${LEMONADE_BASE_URL}/health"` și confirmați că URL-ul de bază introdus în
  formularul LLM de la prima utilizare sau în **Settings > LLM** corespunde
  endpoint-ului local activ sau tunelului HTTPS.
- **Setările LLM nu s-au salvat:** asigurați-vă că ați făcut clic pe **Next** după
  introducerea valorilor. Redeschideți **Settings > LLM** pentru a confirma că valorile
  au fost păstrate.
- **GitHub MCP nu poate vedea repository-urile private:** confirmați că tokenul GitHub are
  acces de citire la repository-ul țintă și că butonul **Test** din MCP din
  **Customize** afișează instrumentele GitHub.
- **Slack poate citi canalele, dar nu poate publica:** invitați aplicația Slack în
  canalul țintă și confirmați că bot-ul are `chat:write`.
- **Automatizarea listează prea multe canale Slack:** utilizați un ID de canal Slack și
  setați `SLACK_CHANNEL_IDS` pe serverul Slack MCP din **Customize**.
- **Execuția automatizării eșuează sau depășește contextul:** confirmați că Lemonade a fost pornit
  cu `ctx_size=65536`, confirmați că LLM-ul OpenHands are `custom_tokenizer` setat,
  și utilizați un repository explicit cu seturile de rezultate GitHub limitate la 3-5
  elemente. Dacă versiunea dumneavoastră de Agent Canvas expune setări de condensare, setați numărul maxim de token-uri al condensorului
  sub dimensiunea ferestrei de context Lemonade.

## Pași următori

- Adăugați un rezumat săptămânal doar pentru versiuni (release-only).
- Adăugați o automatizare declanșată de evenimente GitHub pentru alerte mai rapide privind PR-urile sau push-urile.
- Direcționați același rezumat către Notion, Linear sau un alt instrument bazat pe MCP.

## Resurse

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentația Lemonade Server](https://lemonade-server.ai/docs)
- [Repository-ul de extensii OpenHands](https://github.com/OpenHands/extensions)
- [Servere Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pachetul Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)