<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Run OpenClaw with Lemonade Server as the backend

## Overview

[**OpenClaw**](https://openclaw.ai/) este un agent AI autonom care poate scrie și rula cod, gestiona fișiere și parcurge sarcini complexe în mai mulți pași în numele dumneavoastră. Spre deosebire de un asistent de chat care doar răspunde la întrebări, OpenClaw întreprinde acțiuni reale pe sistemul dumneavoastră, ceea ce înseamnă că are nevoie de un backend AI rapid și capabil, care să țină pasul cu un ciclu de agent solicitant.

[**Lemonade Server**](https://lemonade-server.ai/) este acel backend. Este un server de inferență local open-source care rulează modele GenAI direct pe hardware-ul dumneavoastră și le expune prin API-ul standard din industrie, OpenAI API.

Împreună, formează un stack AI agentic complet local: Lemonade se ocupă de inferența modelului, iar OpenClaw oferă ciclul de agent care transformă ieșirile modelului în acțiuni reale.

> **Înainte de a continua:** OpenClaw este un agent AI extrem de autonom. Acordarea accesului oricărui agent AI la sistemul dumneavoastră poate duce la rezultate imprevizibile sau neintenționate. Continuați doar dacă înțelegeți riscurile și sunteți confortabil cu faptul că un software autonom acționează în numele dumneavoastră.

---

## Ce veți învăța

Până la finalul acestui ghid veți putea să:

- Aflați despre **Lemonade Server**
- **Instalați OpenClaw** și să **îl configurați să folosească Lemonade Server** ca backend AI.
- **Porniți gateway-ul OpenClaw** și să confirmați că agentul dumneavoastră este pregătit de lucru.
- **Conectați un canal de comunicare** (Discord sau Telegram) pentru a putea discuta cu agentul dumneavoastră de pe orice dispozitiv.

---

<!-- @device:halo_box,halo,stx,krk -->
## Configurarea memoriei

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificați actualizările software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea prerechizitelor software

<!-- @os:linux -->
- Un PC care rulează **Ubuntu 24.04+** sau o distribuție Linux compatibilă bazată pe Debian, cu `apt-get`
- Cel puțin **12 GB RAM** (64 GB+ recomandat pentru modele mai mari)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opțional, pentru izolarea OpenClaw într-un mediu sandbox)
- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
<!-- @os:end -->

<!-- @os:windows -->
- Un PC care rulează **Windows 10/11**
- Cel puțin **12 GB RAM** (64 GB+ recomandat pentru modele mai mari)
- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opțional, pentru izolarea OpenClaw într-un mediu sandbox)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descărcați și încărcați modelul recomandat

Modelul recomandat pentru acest ghid este **Qwen3.6-35B-A3B-GGUF** de la Unsloth, un model MoE puternic cu o fereastră de context de 263k tokeni, foarte potrivit pentru sarcinile agentice. Acest model folosește cuantizarea UD-Q4_K_XL. Descărcați-l acum:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Apoi încărcați-l cu o fereastră de context mare și salvați această setare pentru rulările viitoare:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelul are o lungime de context implicită de 262.144 tokeni. Dacă întâmpinați erori de tip memorie insuficientă (OOM), luați în considerare reducerea ferestrei de context. Totuși, deoarece Qwen3.6 folosește contextul extins pentru sarcini complexe, vă recomandăm să mențineți o lungime de context de cel puțin 128K tokeni pentru a păstra capacitățile de „gândire”.

> **Sfat: Dezactivați modul de gândire pentru răspunsuri mai rapide ale agentului:** Qwen3.6-35B-A3B rulează implicit în modul de gândire, ceea ce adaugă latență înainte de fiecare răspuns. Pentru ciclurile de agent, această suprasolicitare se acumulează rapid. Depozitul [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) oferă o configurație gata pregătită care dezactivează modul de gândire. Pentru a o folosi, descărcați fișierul și importați-l:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
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
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## Configurarea WSL

Rulăm OpenClaw în interiorul WSL (Recomandat) și îl conectăm la Lemonade, care rulează nativ pe Windows. Astfel beneficiați de un mediu shell Linux pentru OpenClaw, păstrând în același timp accelerarea GPU a Lemonade pe partea de Windows.

### Instalați WSL și Ubuntu

Deschideți PowerShell ca Administrator și instalați kernelul WSL:

```powershell
wsl --install --no-distribution
```

Apoi instalați Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Activați systemd în WSL

Rulați această comandă în terminalul Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ieșiți din WSL și reporniți-l:

```powershell
exit
wsl --shutdown
wsl
```

### Conectați Lemonade de pe Windows în WSL

WSL2 rulează într-o rețea virtuală. Lemonade pe Windows se leagă la `127.0.0.1`, pe care WSL nu îl poate accesa direct. Un proxy de port Windows redirecționează traficul de la IP-ul gateway-ului WSL către localhost-ul Windows.

**Găsiți IP-ul gateway-ului WSL** (rulați în interiorul WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adăugați proxy-ul de port** (rulați în PowerShell ca Administrator, înlocuind `<WSL-Gateway-IP>` cu IP-ul gateway-ului dumneavoastră WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Notă: Dacă întâmpinați o eroare `netsh: command not found`, încercați să folosiți în schimb numele explicit al executabilului - `netsh.exe`

**Adăugați o regulă de firewall** (în același PowerShell cu drepturi elevate):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verificați din WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Dacă ați încărcat deja modelul Qwen3.6-35B-A3B-GGUF la pasul anterior, ar trebui să vedeți un rezultat JSON asemănător cu acesta:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### Menținerea Funcționării Punții După o Repornire

Regula `netsh portproxy` supraviețuiește repornirilor, dar adresa IP a gateway-ului WSL se poate schimba după `wsl --shutdown` sau o repornire. Când se întâmplă acest lucru, proxy-ul continuă să indice către vechea adresă IP, iar Lemonade devine inaccesibil din WSL. Dacă se întâmplă acest lucru, utilizați una dintre opțiunile de mai jos.

**Opțiunea 1 (recomandată) — Repararea automată a punții.** Pentru a evita să faceți acest lucru manual de fiecare dată, utilizați o sarcină programată care verifică puntea la fiecare pornire și autentificare și o reconstruiește doar atunci când adresa IP a gateway-ului s-a schimbat. Consultați [ghidul de reparare automată a punții WSL Lemonade](assets/RepairLemonadeWslBridge.md).


**Opțiunea 2 — Repararea manuală a punții.** Mai întâi, obțineți adresa IP curentă a gateway-ului WSL rulând acest lucru în WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copiați această valoare; o veți folosi în locul `<new-WSL-Gateway-IP>` mai jos.

Apoi, într-un **PowerShell cu privilegii elevate** (Run as administrator), listați regulile existente, ștergeți doar regula Lemonade învechită și adăugați una nouă cu adresa IP curentă:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

În rezultatul comenzii `show all`, regula Lemonade învechită este intrarea a cărei adresă de conectare este `127.0.0.1` pe portul `13305`; adresa sa de ascultare este vechea voastră `<old-WSL-Gateway-IP>`. Ștergerea după această adresă elimină doar această regulă și lasă neatinse orice alte reguli port-proxy de pe mașina voastră.

Regula de firewall pe care ați adăugat-o în timpul configurării este asociată portului `13305` (nu adresei IP), așa că aceasta continuă să funcționeze și nu trebuie recreată.

> **Recomandare:** Pentru a evita problemele legate de gateway, vă recomandăm cu tărie următoarea configurație de shell:
> - Comenzile **Windows** ar trebui executate în **PowerShell**
> - Comenzile distribuției **WSL** ar trebui executate într-un **Command Prompt** (executat ca **Administrator**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Instalarea și Configurarea OpenClaw

### Instalarea OpenClaw
<!-- @os:windows -->
> Rulați comenzile din această secțiune în interiorul **terminalului WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flagul `--no-onboard` omite expertul interactiv de configurare, veți configura backend-ul modelului manual în pasul următor, ceea ce vă oferă control precis asupra modelului și serverului utilizate.

Deschideți un terminal nou și confirmați instalarea:

```bash
openclaw --version
```

> **Sfat:** Dacă vedeți `command not found` după instalare, adăugați directorul bin global npm la PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pentru a face această modificare permanentă, adăugați linia de mai sus în fișierul `~/.bashrc` sau `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Configurarea OpenClaw pentru a Utiliza Lemonade

Rulați integrarea neinteractivă a OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Această comandă scrie configurația OpenClaw în `~/.openclaw/openclaw.json`.

> **Dimensionarea ferestrei de context OpenClaw:** Compactarea OpenClaw se declanșează atunci când `contextTokens > contextWindow − reserveTokens`. Valoarea implicită `reserveTokensFloor` este de 20.000 de tokeni, un prag minim care suprascrie `reserveTokens` atunci când este mai mic, astfel încât orice context de model sub ~37k va declanșa o buclă infinită de compactare. Setați o rezervă mică și dezactivați pragul minim o singură dată în configurația voastră, iar aceasta se aplică fiecărui model, fără a fi necesară reglarea per model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` este un *prag minim* (gardă minimă), nu rezerva propriu-zisă; setarea doar a pragului minim nu are niciun efect. `reserveTokensFloor: 0` dezactivează garda, astfel încât valoarea mai mică `reserveTokens` este acceptată.
>
> **Când să aplicați acest lucru:** Utilizați această configurație dacă fereastra de context efectivă a modelului vostru este sub ~37k, fie pentru că modelul este mic (de exemplu, 8k, 16k, 32k), fie pentru că ați limitat-o intenționat la o valoare mai mică (de exemplu, încărcând un model de 128k dar setând contextul la 16k în Lemonade). Fără aceasta, OpenClaw intră într-o buclă infinită de compactare la pornire.
>
> **Modele cu context mare la context complet:** Puteți omite complet acest lucru. Valorile implicite funcționează bine, compactarea se va activa cu mult înainte ca fereastra să se umple, iar modelul are spațiu suficient pentru a genera răspunsuri lungi. Dacă totuși aplicați acest lucru, rețineți că `reserveTokens: 4096` limitează lungimea răspunsului la ~4k tokeni, ceea ce poate întrerupe generarea de fișiere lungi sau planuri detaliate.
>
> **Unde să adăugați acest lucru:** Plasați blocul `compaction` în interiorul `agents.defaults` din fișierul vostru `openclaw.json` (de obicei la `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Restul configurației voastre (gateway, channels, models, etc.) rămâne neschimbat, doar cheia `compaction` trebuie adăugată.
### (Recomandat) Activați Docker Sandboxing

OpenClaw poate direcționa toate operațiunile de fișiere și cod ale agentului printr-un container Docker izolat, în loc să le execute direct pe gazda dumneavoastră. Acest lucru limitează raza de acțiune a oricărei acțiuni neintenționate la sandbox, lăsând sistemul de fișiere și rețeaua gazdei neatinse.

Construiți imaginea sandbox o singură dată (Docker trebuie să fie instalat):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Rulați aceasta pentru a adăuga cheia `sandbox` în blocul existent `agents.defaults` din `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Containerele sandbox nu au **acces la rețea** în mod implicit. Consultați [referința de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) pentru montări bind și suprascrieri de rețea.

> #### Depanare: Docker Permission Denied
> 
> Dacă primiți „permission denied” la rularea comenzilor Docker:
> 
> **Pasul 1: Adăugați utilizatorul în grupul docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Pasul 2: Dacă eroarea persistă, aplicați soluția permanentă**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Apoi **reporniți** sistemul.
> 
> **Soluție temporară rapidă** (se resetează după repornire):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Recomandat) Integrarea OpenClaw cu serviciile Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) oferă un serviciu de crawling web și extragere a conținutului găzduit propriu, care poate depăși aceste provocări și poate debloca întregul potențial al automatizării OpenClaw. 

În această configurație, OpenClaw rulează ca un set de containere Docker gestionate cu Podman. Pentru a simplifica gestionarea ciclului de viață și pornirea automată, înregistrăm Firecrawl ca serviciu `systemd` la nivel de utilizator, care orchestrează stiva Podman Compose subiacentă. Acest lucru permite OpenClaw să pornească gateway-ul, să-l oprească și să verifice serviciul Firecrawl folosind comenzi standard `systemctl --user`, în loc să interacționeze direct cu containerele. 

Pentru a păstra simplitatea, am împărțit întregul proces în patru pași:

---

### 1. Înregistrați serviciul de sistem
Navigați la directorul de configurare systemd al utilizatorului:
```bash
cd ~/.config/systemd/user
```
Creați și deschideți un fișier nou numit `firecrawl.service`.
```bash
nano firecrawl.service
```
Copiați și inserați următoarea configurație:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
În acest moment, serviciul a fost definit, dar nu a fost încă înregistrat la `systemd`. 
Asigurați-vă că numele fișierului se potrivește exact cu cel creat mai sus, apoi rulați:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Dacă reușiți, ar trebui să vedeți următorul rezultat:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` conține legături simbolice către serviciile configurate să pornească automat.

### 2. Configurați Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) este ideal pentru cei care au nevoie de control total asupra mediilor lor de scraping și procesare a datelor, dar vine cu costul unui efort suplimentar de întreținere și configurare.

Începeți prin clonarea repository-ului:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Creați un fișier `.env`, în directorul `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Implementați OpenClaw cu Podman Compose

Înainte de a continua, asigurați-vă că ați descărcat cea mai recentă imagine Docker OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
După ce ați terminat, descărcați fișierul Compose OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) și plasați-l în directorul rădăcină `/firecrawl`:

> Această convenție este necesară pentru ca `systemd` să localizeze și să pornească serviciul corect, conform specificației din `WorkingDirectory=${HOME}/firecrawl`.

> Puteți extinde oricând stiva adăugând servicii Firecrawl suplimentare, după cum este necesar. Lista completă a serviciilor disponibile se găsește în fișierul oficial [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Lansați serviciul OpenClaw prin Firecrawl 

Înainte de a preda controlul către `systemd`, verificați că totul funcționează corect rulând stiva manual:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Dacă totul este configurat corect, ar trebui să vedeți containerul OpenClaw pornind, iar rezultatul liniei de comandă ar trebui să arate similar cu acesta:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

După verificare, opriți stiva înainte de a continua:
```bash
podman compose -f openclaw-compose.yaml down
```
Înainte de a porni serviciul, trebuie să vă asigurați că proprietatea și permisiunile corecte sunt setate pe directorul `firecrawl` și pe fișierul său `.env`. 
Acest lucru este esențial pentru ca serviciul să vă scrie acreditările la pornire.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Acum că totul este validat, porniți serviciul prin `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Acțiunile OpenClaw](https://docs.openclaw.ai/) sunt accesibile din interiorul containerului interactiv, iar Panoul de control Web este disponibil pe aceeași gazdă și port la http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obținerea `OPENCLAW_GATEWAY_TOKEN`-ului dumneavoastră

Odată ce serviciul este pornit și funcționează, veți observa un nou director `.openclaw` creat în folderul dumneavoastră de acasă (~/.openclaw). Acest director este blocat în mod implicit, așa că va trebui să îl deblocați pentru a recupera token-ul dumneavoastră de gateway.

1. Acordați acces la director:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Citiți token-ul dumneavoastră de gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Localizați valoarea `OPENCLAW_GATEWAY_TOKEN` în rezultat.

3. Deschideți panoul de control al gateway-ului în browserul dumneavoastră http://127.0.0.1:18789. Inserați token-ul dumneavoastră când vi se solicită autentificarea.

Pentru a opri serviciul, rulați:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Pornirea Gateway-ului OpenClaw

Gateway-ul este procesul OpenClaw care gestionează bucla agentului și servește dashboard-ul:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Pentru a deschide dashboard-ul, rulați următoarea comandă într-un al doilea terminal, în timp ce gateway-ul rulează în continuare:

```bash
openclaw dashboard
```

Deoarece gateway-ul se leagă de loopback, dashboard-ul se autentifică automat atunci când este deschis de pe aceeași mașină, nu este nevoie de introducerea unui token sau de aprobarea dispozitivului pentru accesul local. Ar trebui să vedeți dashboard-ul OpenClaw cu modelul dvs. Lemonade afișat ca backend activ.

> Dacă ați activat sandboxing-ul, îl puteți verifica cerând agentului să `run hostname` din dashboard. Dacă vedeți un ID scurt de container în loc de hostname-ul mașinii dvs., sandbox-ul funcționează.

**Felicitări, ați construit o stivă de agent AI complet locală, de la zero.**

> **Aveți nevoie de token-ul gateway-ului?** Rulați `openclaw dashboard --no-open` pentru a afișa URL-ul dashboard-ului cu token-ul inclus (de asemenea, încearcă să îl copieze în clipboard). Alternativ, token-ul se află la `gateway.auth.token` în `~/.openclaw/openclaw.json`.

**Accesarea Dashboard-ului de pe Alt Dispozitiv (prin Tunel SSH)**

Dacă OpenClaw rulează pe o mașină la distanță, puteți accesa dashboard-ul acesteia de pe mașina dvs. locală printr-un tunel SSH. Tunelul redirecționează portul gateway-ului (`18789`) astfel încât browserul dvs. local să poată comunica cu gateway-ul de la distanță prin `127.0.0.1`.

1. De pe **mașina locală**, conectați-vă o dată la mașina de la distanță și acceptați solicitarea de amprentă, astfel încât gazda să fie adăugată în lista de gazde cunoscute:

   ```bash
   ssh user@<host-ip>
   ```

2. Rămânând pe **mașina locală**, deschideți tunelul SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Notă:** După ce introduceți parola, terminalul nu afișează nicio ieșire și pare blocat. Acest lucru este normal: steagul `-N` îi spune SSH să nu ruleze nicio comandă la distanță, astfel încât acesta doar menține tunelul deschis. Lăsați acest terminal să ruleze.

3. Pe **mașina locală**, deschideți un browser și accesați `http://127.0.0.1:18789`.

4. Pe **mașina de la distanță**, afișați token-ul gateway-ului și lipiți-l în browser pentru a vă autentifica:

   ```bash
   openclaw dashboard --no-open
   ```

   Aceasta afișează URL-ul dashboard-ului cu token-ul inclus; copiați token-ul pentru a vă autentifica. (Token-ul este, de asemenea, stocat la `gateway.auth.token` în `~/.openclaw/openclaw.json`.)

> **Aprobarea unui dispozitiv de la distanță:** Când deschideți dashboard-ul de pe o altă mașină sau telefon, browserul poate afișa un ID de solicitare. Pe **mașina de la distanță**, listați solicitările în așteptare:
> ```bash
> openclaw devices list
> ```
> Apoi aprobați solicitarea corespunzătoare:
> ```bash
> openclaw devices approve <requestId>
> ```
> Acest lucru este necesar doar pentru dispozitive de la distanță sau secundare; accesul loopback de pe aceeași mașină se autentifică automat. Consultați documentația [Remote Access](https://docs.openclaw.ai/gateway/remote) pentru detalii.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opțional: Conectarea unui Canal de Comunicare

Odată ce gateway-ul rulează, puteți accesa agentul local de pe orice dispozitiv. Alegeți opțiunea potrivită configurației dvs. OpenClaw acceptă [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) și alte canale; consultați lista completă la [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opțiunea A: Discord

Discord necesită un server pe care **aveți acces de administrator** pentru a adăuga un bot. Dacă partajați servere, dar nu dețineți unul, folosiți Opțiunea B (Telegram).

#### Crearea unui cont și server Discord

Dacă nu aveți un cont Discord, înregistrați-vă la [discord.com](https://discord.com). De asemenea, aveți nevoie de un server pe care sunteți administrator; creați unul făcând clic pe pictograma **+** din bara laterală Discord și selectând **Create My Own**. Un server privat este suficient.

#### Crearea unei aplicații și a unui bot Discord

1. Accesați [Discord Developer Portal](https://discord.com/developers/applications) și faceți clic pe **New Application**. Dați-i un nume (de ex. „openclaw-bot").
2. În bara laterală, faceți clic pe **Bot**. Setați un nume de utilizator pentru bot.
3. Rămânând pe pagina Bot, derulați la **Privileged Gateway Intents** și activați:
   - **Message Content Intent** (obligatoriu)
   - **Server Members Intent** (recomandat)
4. Derulați înapoi în sus și faceți clic pe **Reset Token** pentru a genera token-ul botului. Copiați-l.

#### Adăugarea botului pe serverul dvs.

1. În bara laterală, faceți clic pe **OAuth2/ URL Generator**.
2. Sub **Scopes**, activați `bot` și `applications.commands`.
3. Sub **Bot Permissions**, activați: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiați URL-ul generat, lipiți-l în browser, selectați serverul dvs. și confirmați. Botul ar trebui să apară acum în lista de membri a serverului dvs.

#### Colectarea ID-urilor dvs.

Activați Developer Mode în Discord (**User Settings/ Advanced/ Developer Mode**), apoi:
- Faceți clic dreapta pe pictograma serverului dvs.: **Copy Server ID**
- Faceți clic dreapta pe avatarul dvs.: **Copy User ID**

#### Permiterea mesajelor directe de la membrii serverului

Faceți clic dreapta pe pictograma serverului dvs./ **Privacy Settings**/ activați comutatorul **Direct Messages**. Acest lucru permite botului să vă trimită mesaje directe, fiind necesar pentru etapa de asociere.

#### Configurarea OpenClaw pentru Discord

Stocați token-ul botului dvs. ca variabilă de mediu, apoi creați un singur fișier de patch care activează Discord, face referire la token și adaugă serverul dvs. pe lista permisă. Înlocuiți `<server_id>` și `<user_id>` cu ID-urile colectate mai sus.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Nu vă bazați pe a cere agentului să configureze acest lucru.** Când sandboxing-ul este activat, agentul nu poate scrie în `~/.openclaw/openclaw.json` din interiorul sandbox-ului; folosiți în schimb comenzile CLI de mai sus pe gazdă.

Reporniți gateway-ul pentru ca acesta să preia noua configurație a canalului:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ar trebui să vedeți `logged in to discord as <bot-name>` în ieșirea gateway-ului în câteva secunde.
#### Asociați-vă contul Discord

Trimiteți un mesaj direct (DM) bot-ului în Discord. Acesta va răspunde cu un cod scurt de asociere.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprobați-l pe mașina pe care rulează OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Codurile de asociere expiră după o oră.

Acum puteți discuta cu agentul dumneavoastră direct din Discord și puteți delega sarcini către hardware-ul dumneavoastră local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opțiunea B: Telegram

Telegram este mai simplu decât Discord pentru majoritatea utilizatorilor, nu necesită server și nici acces de administrator.

#### Creați un bot Telegram

1. Deschideți Telegram și trimiteți un mesaj către **@BotFather**.
2. Trimiteți `/newbot` și urmați instrucțiunile. Salvați token-ul bot-ului pe care vi-l oferă.

#### Configurați OpenClaw pentru Telegram

Stocați token-ul ca variabilă de mediu:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adăugați configurația canalului în `~/.openclaw/openclaw.json` (sau aplicați un patch prin tabloul de bord):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Reporniți gateway-ul, apoi trimiteți bot-ului dumneavoastră orice mesaj în Telegram. Aprobați asocierea:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Codurile de asociere expiră după o oră. Acum puteți discuta cu agentul dumneavoastră prin DM pe Telegram.

---

## Pașii următori

Acum că agentul dumneavoastră poate primi comenzi de pe telefon și poate acționa pe mașina dumneavoastră locală, iată trei direcții care merită explorate:

1. **Sumarizator pentru piața de valori**: Programați OpenClaw să preia date de la API-uri financiare la un interval fix, să sumarizeze mișcările zilei cu modelul dumneavoastră local și să trimită un rezumat pe telefon în fiecare dimineață prin canalul ales.

2. **Monitor de fine-tuning**: Porniți o sarcină de antrenare de la distanță prin Telegram sau Discord, apoi lăsați agentul să urmărească jurnalul de antrenare și să raporteze periodic valorile pierderii (loss), utilizarea GPU-ului și utilizarea discului înapoi pe telefon. Dacă rularea se blochează sau VRAM-ul crește brusc, aflați imediat, fără a fi nevoie să fiți lângă mașină.

3. **IOT cu un VLM local**: Îndreptați o cameră spre ușa din față, rulați un model de viziune pe Lemonade și lăsați OpenClaw să analizeze cadrele la cerere sau la declanșare. Întrebați „au sosit colete azi?” de pe telefon și primiți un răspuns direct de la propriul dumneavoastră hardware.

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