<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Prezentare generală

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Acest playbook necesită cel puțin **32 GB** de memorie de sistem.
<!-- @device:end -->

n8n este o platformă de automatizare a fluxurilor de lucru care vă permite să conectați aplicații și servicii folosind un editor vizual bazat pe noduri.

Acest playbook vă învață cum să configurați un sumarizator de știri financiare bazat pe AI, care preia cele mai recente titluri de știri de afaceri dintr-un flux RSS de știri și folosește un LLM local care rulează pe sistemul dvs. pentru a genera un rezumat orientat către investitori.

## Ce veți învăța

- Cum să instalați și să lansați n8n
- Importarea și configurarea unui flux de lucru pre-construit
- Conectarea la Lemonade folosind integrarea nativă n8n
- Înțelegerea nodurilor fluxului de lucru și a fluxului de date

## Ce este Lemonade?

[Lemonade](https://lemonade-server.ai) este o platformă locală de servire LLM construită pentru hardware AMD. Aceasta oferă un API compatibil OpenAI care rulează în întregime pe mașina dvs. — datele dvs. nu părăsesc niciodată dispozitivul.

În acest playbook, folosim Lemonade pentru a servi un LLM local la care n8n se conectează pentru sarcini bazate pe AI.

n8n include un **nod Lemonade nativ** (`Lemonade Chat Model`) care oferă o integrare de primă clasă - fără a fi nevoie de configurare manuală. Acest lucru face ca conectarea LLM-ului dvs. local la fluxurile de lucru de automatizare să fie simplă.

<!-- @device:halo_box,halo,stx,krk -->
## Setarea configurației de memorie

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificați actualizările software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare software
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## Instalarea n8n
<!-- @os:windows -->
Instalați n8n global folosind npm.

> **Notă**: Este posibil să vedeți câteva avertismente npm. Acest lucru este normal.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Sfat**: Utilizatorii Windows ar putea fi nevoiți să modifice Politica de executare PowerShell (de exemplu,
> setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problemă PATH**: Dacă `n8n --version` spune că comanda nu a fost găsită, asigurați-vă că directorul global npm bin se află în variabila `PATH` a utilizatorului. Calea obișnuită de instalare este la `C:\Users\<username>\AppData\Roaming\npm`. 
> Adăugați aceasta la calea utilizatorului (Editare variabile de mediu de sistem > Variabile de mediu > Editare Path utilizator) și reîncărcați terminalul. 

<!-- @os:end -->

<!-- @os:linux -->
Vom folosi acum serviciul Podman pentru a containeriza instalarea noastră n8n.

Vă rugăm să descărcați următorul fișier într-un director la alegere: [compose.yml](assets/compose.yml)

În acel director, rulați următoarea comandă:
```bash
podman compose up -d
```

Aceasta ar trebui să instaleze n8n și să scrie într-un spațiu de stocare persistent.

Lansați n8n tastând `localhost:5678` în bara de adrese a browserului dvs.
<!-- @os:end -->

<!-- @os:windows -->
## Lansarea n8n

Porniți n8n din terminal:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n pornește un server web local. Apăsați `'o'` sau deschideți browserul dvs. la `http://localhost:5678` pentru a accesa editorul.
<!-- @os:end -->


> **Sfat**: Păstrați fereastra terminalului deschisă în timp ce utilizați n8n. Închiderea acesteia ar putea opri serverul.

## Lansarea Lemonade

Lemonade este serverul local care va rula un model și se va conecta la n8n.

<!-- @os:linux -->
Deschideți interfața grafică Lemonade făcând clic pe pictograma Lemonade din bara de activități. Puteți naviga printre modele, backend-uri și încărca modelele preinstalate de aici.
<!-- @os:end -->

<!-- @os:windows -->
Deschideți interfața grafică Lemonade făcând clic pe pictograma Lemonade. Faceți clic dreapta pe pictograma din tava de sistem pentru a deschide aplicația. Apoi, puteți adăuga modele, backend-uri și încărca modelele preinstalate.
<!-- @os:end -->

>**Sfat**: Odată pornită, interfața grafică Lemonade este, de asemenea, accesibilă la http://localhost:13305

Alternativ, puteți deschide un terminal și rula `lemonade list` pentru a vedea ce modele sunt instalate. Apoi, rulați:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Configurarea fluxului de lucru

### Pasul 1: Înregistrați-vă sau conectați-vă la n8n

Când deschideți pentru prima dată n8n, vi se va solicita să creați un cont sau să vă conectați:

1. Deschideți `http://localhost:5678` în browserul dvs.
2. Creați un cont local nou cu adresa dvs. de e-mail, sau conectați-vă dacă aveți deja unul
3. După ce v-ați conectat, veți vedea tabloul de bord n8n

> **Sfat**: Dacă sunteți blocat în afara contului dvs., încercați `n8n user-management:reset`

### Pasul 2: Importați fluxul de lucru

Am furnizat un flux de lucru pre-construit pe care îl puteți importa direct:

1. Descărcați următorul fișier de flux de lucru: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Faceți clic pe **Start from Scratch** pentru a deschide editorul de fluxuri de lucru. Alternativ, faceți clic pe butonul + din stânga sus, apoi pe **Add workflow**.
3. Faceți clic pe meniul **...** (trei puncte) din bara din dreapta sus și selectați **Import from file**
4. Selectați fișierul descărcat `financial-news-workflow.json`
5. Fluxul de lucru va apărea pe canvas
### Pasul 3: Înțelegerea fluxului de lucru

Fluxul de lucru importat conține 8 noduri conectate:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nod | Scop |
|------|---------|
| **When clicking 'Execute workflow'** | Declanșator manual pentru a porni fluxul de lucru |
| **Fetch Financial News Feed** | Nod RSS Read care preia cele mai recente titluri de afaceri dintr-un feed RSS (implicit feed-ul NYT Business, nu necesită cheie API) |
| **Aggregate Headlines** | Nod Aggregate care colectează titlurile și rezumatele din fiecare element al feed-ului într-o singură listă |
| **Clean Extracted News Data** | Nod Set care combină toate titlurile într-un singur câmp de text |
| **AI Financial News Summarizer** | Agent AI care procesează știrile folosind un prompt de sistem specific unui analist financiar |
| **Lemonade Chat Model** | Se conectează la serverul tău local Lemonade care rulează LLM-ul |
| **Structured Output Parser** | Formatează rezultatul AI ca JSON structurat |
| **Convert to File** | Convertește rezumatul într-un fișier descărcabil |

> **Sugestie**: Pentru a folosi o altă sursă de știri, dă dublu clic pe nodul **Fetch Financial News Feed** și înlocuiește URL-ul cu orice feed RSS de afaceri sau de piețe pe care îl preferi.

### Pasul 4: Configurarea acreditărilor Lemonade

Înainte de a rula fluxul de lucru, trebuie să îl conectezi la serverul tău local Lemonade:

1. Dă dublu clic pe nodul **Lemonade Chat Model** în n8n
2. În meniul derulant **Credential to connect with** selectează **Create New Credential**
3. Introdu valorile din tabelul de mai jos și apasă save.
4. Alege modelul relevant pe care l-ai încărcat în Lemonade Server.

  | Câmp | Valoare |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Notă**: Înainte de a testa, rulează `lemonade status` într-un terminal pentru a confirma că serverul Lemonade rulează.
<!-- @device:halo_box -->
> Acest flux de lucru folosește GPT-OSS-120B, care este preinstalat în Lemonade. Poți schimba acest lucru cu alte modele încărcate din setările nodului Lemonade Chat Model.
<!-- @device:end -->

### Pasul 5: Testarea fluxului de lucru

1. Asigură-te că Lemonade rulează cu un model încărcat
2. Dă clic pe **Execute workflow** în partea de jos, centrul canvasului
3. Urmărește fiecare nod executându-se de la stânga la dreapta—devin verzi când sunt finalizate
4. Dă dublu clic pe nodul **AI Financial News Summarizer** pentru a vedea rezumatul generat în panoul de jos.
5. Dă dublu clic pe nodul **Convert to File** pentru a descărca fișierul text corespunzător din panoul de jos.

## Înțelegerea agentului AI

AI Financial News Summarizer folosește un prompt de sistem conceput pentru analiza financiară:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Agentul primește datele de știri curățate și generează un rezumat structurat împreună cu sentimentul pieței.

### Salvarea fluxului de lucru

Dă clic pe numele fluxului de lucru din partea de sus și redenumește-l dacă dorești. Fluxurile de lucru se salvează automat pe măsură ce lucrezi.

## Pașii următori

- **Programarea automatizării**: Înlocuiește Manual Trigger cu un **Schedule Trigger** pentru a rula zilnic
- **Trimiterea notificărilor**: Adaugă un nod **Discord**, **Slack** sau **Email** pentru a primi rezumate
- **Încearcă diferite modele**: Schimbă modelul din nodul Lemonade Chat Model pentru a experimenta cu diferite LLM-uri
- **Schimbă sursa de știri**: Îndreaptă nodul **Fetch Financial News Feed** către un alt feed RSS pentru a urmări alte secțiuni sau publicații
- **Încearcă alte backend-uri**: n8n suportă de asemenea [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio și alte backend-uri LLM locale

### Explorează șabloanele n8n

n8n are sute de șabloane de flux de lucru predefinite. Răsfoiește biblioteca oficială de șabloane la:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Caută „AI”, „LLM” sau „automation” pentru a găsi fluxuri de lucru pe care le poți importa și personaliza.

Pentru mai multe informații, consultă [Documentația n8n](https://docs.n8n.io/).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->