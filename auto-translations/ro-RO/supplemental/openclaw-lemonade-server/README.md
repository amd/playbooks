<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Rulează OpenClaw folosind Lemonade Server ca backend

## Prezentare generală

[**OpenClaw**](https://openclaw.ai/) este un agent AI autonom care poate scrie și rula cod, poate gestiona fișiere și poate parcurge sarcini complexe cu mai mulți pași în numele tău. Spre deosebire de un asistent de chat care doar răspunde la întrebări, OpenClaw efectuează acțiuni reale pe sistemul tău, ceea ce înseamnă că are nevoie de un backend AI rapid și capabil, care să țină pasul cu un ciclu de agent solicitant.

[**Lemonade Server**](https://lemonade-server.ai/) este acel backend. Este un server de inferență local, open-source, care rulează modele GenAI direct pe hardware-ul tău și le expune prin API-ul standard din industrie, OpenAI API.

Împreună, formează un stack complet local de AI cu agent: Lemonade se ocupă de inferența modelului, iar OpenClaw oferă ciclul de agent care transformă rezultatele modelului în acțiuni reale.

> **Înainte de a continua:** OpenClaw este un agent AI extrem de autonom. Oferirea accesului oricărui agent AI la sistemul tău poate duce la rezultate imprevizibile sau neintenționate. Continuă doar dacă înțelegi riscurile și te simți confortabil cu software autonom care acționează în numele tău.

---

## Ce vei învăța

Până la finalul acestui ghid vei putea:

- Afla despre **Lemonade Server**
- **Instala OpenClaw** și **îl vei configura să folosească Lemonade Server** ca backend AI.
- **Porni gateway-ul OpenClaw** și confirma că agentul tău este pregătit de lucru.
- **Conecta un canal de comunicare** (Discord sau Telegram) pentru a putea discuta cu agentul tău de pe orice dispozitiv.

---

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifică actualizările software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor prealabile de software

<!-- @os:linux -->
- Un PC care rulează **Ubuntu 24.04+** sau o distribuție Linux compatibilă bazată pe Debian, cu `apt-get`
- Cel puțin **12 GB de RAM** (se recomandă 64 GB+ pentru modele mai mari)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opțional, pentru izolarea (sandboxing) OpenClaw)
- **~10–30 GB de spațiu liber pe disc** pentru ponderile modelului
<!-- @os:end -->

<!-- @os:windows -->
- Un PC care rulează **Windows 10/11**
- Cel puțin **12 GB de RAM** (se recomandă 64 GB+ pentru modele mai mari)
- **~10–30 GB de spațiu liber pe disc** pentru ponderile modelului
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opțional, pentru izolarea (sandboxing) OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descarcă și încarcă modelul recomandat

Modelul recomandat pentru acest ghid este **Qwen3.6-35B-A3B-GGUF** de la Unsloth, un model MoE puternic, cu o fereastră de context de 263k token-uri, foarte potrivit pentru sarcinile de tip agent. Acest model folosește cuantizarea UD-Q4_K_XL. Descarcă-l acum:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Apoi încarcă-l cu o fereastră de context mare și salvează această setare pentru rulările viitoare:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelul are o lungime implicită de context de 262.144 de token-uri. Dacă întâmpini erori de tip out-of-memory (OOM), ia în considerare reducerea ferestrei de context. Totuși, deoarece Qwen3.6 folosește contextul extins pentru sarcini complexe, recomandăm menținerea unei lungimi de context de cel puțin 128K token-uri pentru a păstra capacitățile de gândire.

> **Sfat: dezactivează gândirea pentru răspunsuri mai rapide ale agentului:** Qwen3.6-35B-A3B rulează implicit în modul de gândire (thinking mode), ceea ce adaugă latență înainte de fiecare răspuns. Pentru ciclurile de agent, această încărcare suplimentară se acumulează rapid. Depozitul [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) oferă o configurație gata pregătită care dezactivează gândirea. Pentru a o folosi, descarcă fișierul și importă-l:
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

Rulăm OpenClaw în interiorul WSL (recomandat) și îl conectăm la Lemonade, care rulează nativ pe Windows. Astfel obții un mediu shell Linux pentru OpenClaw, păstrând în același timp accelerarea GPU a Lemonade pe partea Windows.

### Instalează WSL și Ubuntu

Deschide PowerShell ca administrator și instalează kernel-ul WSL:

```powershell
wsl --install --no-distribution
```

Apoi instalează Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Activează systemd în WSL

Rulează această comandă în terminalul Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ieși din WSL și repornește-l:

```powershell
exit
wsl --shutdown
wsl
```

### Realizează puntea (bridge) între Lemonade de pe Windows și WSL

WSL2 rulează într-o rețea virtuală. Lemonade, pe Windows, se leagă de `127.0.0.1`, adresă pe care WSL nu o poate accesa direct. Un proxy de port Windows redirecționează traficul de la adresa IP a gateway-ului WSL către localhost-ul Windows.

**Găsește adresa IP a gateway-ului WSL** (rulează în interiorul WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adaugă proxy-ul de port** (rulează în PowerShell ca administrator, înlocuind `<WSL-Gateway-IP>` cu adresa IP a gateway-ului tău WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Notă: Dacă întâmpini o eroare `netsh: command not found`, încearcă să folosești în schimb numele explicit al executabilului - `netsh.exe`

**Adaugă o regulă de firewall** (în aceeași fereastră PowerShell cu drepturi elevate):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifică din WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Dacă ai încărcat deja modelul Qwen3.6-35B-A3B-GGUF la pasul anterior, ar trebui să vezi un rezultat JSON asemănător cu acesta:

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

Regula `netsh portproxy` supraviețuiește repornirilor, dar IP-ul gateway-ului WSL se poate schimba după `wsl --shutdown` sau o repornire. Când se întâmplă asta, proxy-ul continuă să indice spre vechiul IP, iar Lemonade devine inaccesibil din WSL. Dacă se întâmplă acest lucru, folosiți una dintre opțiunile de mai jos.

**Opțiunea 1 (recomandată) — Repararea automată a punții.** Pentru a evita să faceți acest lucru manual de fiecare dată, folosiți o sarcină programată care verifică puntea la fiecare pornire și autentificare și o reconstruiește doar atunci când IP-ul gateway-ului s-a schimbat. Consultați [ghidul de auto-reparare a punții WSL Lemonade](assets/RepairLemonadeWslBridge.md).


**Opțiunea 2 — Repararea manuală a punții.** Mai întâi, obțineți IP-ul curent al gateway-ului WSL rulând acest lucru în interiorul WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copiați această valoare; o veți folosi în locul `<new-WSL-Gateway-IP>` mai jos.

Apoi, într-un **PowerShell cu drepturi elevate** (Rulare ca administrator), listați regulile existente, ștergeți doar regula Lemonade învechită și adăugați una nouă cu IP-ul curent:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

În rezultatul comenzii `show all`, regula Lemonade învechită este intrarea a cărei adresă de conectare este `127.0.0.1` pe portul `13305`; adresa sa de ascultare este `<old-WSL-Gateway-IP>`. Ștergerea după acea adresă elimină doar această regulă și lasă neatinsă orice altă regulă port-proxy de pe mașina dvs.

Regula de firewall pe care ați adăugat-o în timpul configurării este legată de portul `13305` (nu de IP), astfel încât continuă să funcționeze și nu trebuie recreată.

> **Recomandare:** Pentru a evita problemele de gateway, vă recomandăm cu tărie următoarea configurare de shell:
> - **Comenzile Windows** ar trebui executate în **PowerShell**
> - **Comenzile distribuției WSL** ar trebui executate într-un **Command Prompt** (rulat ca **Administrator**)

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

Flag-ul `--no-onboard` omite expertul de configurare interactivă, urmând să configurați manual backend-ul modelului la pasul următor, ceea ce vă oferă control precis asupra modelului și serverului utilizate.

Deschideți un terminal nou și confirmați instalarea:

```bash
openclaw --version
```

> **Sfat:** Dacă vedeți `command not found` după instalare, adăugați directorul global bin al npm la PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pentru a face acest lucru permanent, adăugați linia de mai sus în fișierul dvs. `~/.bashrc` sau `~/.zshrc`.

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


### Configurarea OpenClaw pentru a Folosi Lemonade

Rulați procesul de integrare neinteractiv al OpenClaw.
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

> **Dimensionarea ferestrei de context OpenClaw:** Compactarea OpenClaw se declanșează atunci când `contextTokens > contextWindow − reserveTokens`. `reserveTokensFloor` implicit este de 20.000 de tokeni, un prag minim care suprascrie `reserveTokens` atunci când acesta este mai mic, astfel încât orice context de model sub ~37k va declanșa o buclă infinită de compactare. Setați o rezervă mică și dezactivați pragul minim o singură dată în configurația dvs., iar acest lucru se va aplica fiecărui model, fără a fi nevoie de ajustări per-model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` este un *prag minim* (o gardă minimă), nu rezerva în sine, deci setarea doar a pragului minim nu are niciun efect. `reserveTokensFloor: 0` dezactivează garda, astfel încât valoarea mai mică `reserveTokens` este acceptată.
>
> **Când să aplicați acest lucru:** Folosiți această configurare dacă fereastra de context efectivă a modelului dvs. este sub ~37k, fie pentru că modelul este mic (de ex. 8k, 16k, 32k), fie pentru că ați limitat-o intenționat la o valoare mai mică (de ex. încărcați un model de 128k dar setați contextul la 16k în Lemonade). Fără acest lucru, OpenClaw intră într-o buclă infinită de compactare la pornire.
>
> **Modele cu context mare la context complet:** Puteți sări complet peste acest pas. Valorile implicite funcționează bine, compactarea se va declanșa cu mult înainte ca fereastra să se umple, iar modelul are spațiu suficient pentru a genera răspunsuri lungi. Dacă totuși aplicați acest lucru, rețineți că `reserveTokens: 4096` limitează lungimea răspunsului la ~4k tokeni, ceea ce poate întrerupe generarea de fișiere lungi sau planuri detaliate.
>
> **Unde să adăugați acest lucru:** Plasați blocul `compaction` în interiorul `agents.defaults` din fișierul dvs. `openclaw.json` (de obicei la `~/.openclaw/openclaw.json`):
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
> Restul configurației dvs. (gateway, canale, modele etc.) rămâne neschimbat, doar cheia `compaction` trebuie adăugată.
### (Recomandat) Activați Sandboxing-ul Docker

OpenClaw poate direcționa toate operațiunile de fișiere și cod ale agentului printr-un container Docker izolat, în loc să le ruleze direct pe gazda dumneavoastră. Acest lucru limitează raza de acțiune a oricărei acțiuni neintenționate la sandbox, lăsând sistemul de fișiere și rețeaua gazdei neatinse.

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

Rulați acest lucru pentru a adăuga cheia `sandbox` în blocul existent `agents.defaults` din `~/.openclaw/openclaw.json`:

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

Containerele sandbox **nu au acces la rețea** în mod implicit. Consultați [referința pentru sandboxing](https://docs.openclaw.ai/gateway/sandboxing) pentru montări bind și suprascrieri de rețea.

> #### Depanare: Permisiune Docker refuzată
> 
> Dacă primiți mesajul „permission denied” la rularea comenzilor Docker:
> 
> **Pasul 1: Adăugați utilizatorul dumneavoastră în grupul docker**
> 
> ```bash
> sudo groupadd docker                    # Creați grupul dacă este necesar
> sudo usermod -aG docker $USER           # Adăugați-vă în grup
> newgrp docker                           # Activați modificarea
> docker run hello-world                  # Testați
> ```
> 
> **Pasul 2: Dacă eroarea persistă, aplicați remedierea permanentă**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Apoi **reporniți** sistemul.
> 
> **Remediere rapidă temporară** (se resetează după repornire):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) oferă un serviciu de crawling web și extragere de conținut auto-găzduit, care poate ocoli aceste provocări și poate debloca întregul potențial al automatizării OpenClaw. 

În această configurație, OpenClaw rulează ca un set de containere Docker gestionate cu Podman. Pentru a simplifica gestionarea ciclului de viață și pornirea automată, înregistrăm Firecrawl ca serviciu `systemd` la nivel de utilizator, care orchestrează stiva Podman Compose subiacentă. Acest lucru permite OpenClaw să pornească gateway-ul, să oprească și să verifice serviciul Firecrawl folosind comenzi standard `systemctl --user`, în loc să interacționeze direct cu containerele. 

Pentru a păstra simplitatea, am împărțit întregul proces în patru pași:

---

### 1. Înregistrați serviciul de sistem
Navigați către directorul de configurare a utilizatorului systemd:
```bash
cd ~/.config/systemd/user
```
Creați și deschideți un fișier nou numit `firecrawl.service`.
```bash
nano firecrawl.service
```
Copiați și lipiți următoarea configurație:
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
În acest moment, serviciul a fost definit, dar nu este încă înregistrat cu `systemd`. 
Asigurați-vă că numele fișierului corespunde exact cu cel creat mai sus, apoi rulați:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Dacă operațiunea reușește, ar trebui să vedeți următorul rezultat:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` conține legături simbolice către serviciile configurate să pornească automat.

### 2. Configurați Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) este ideal pentru cei care au nevoie de control total asupra mediilor de scraping și procesare a datelor, dar vine cu compromisul unor eforturi suplimentare de întreținere și configurare.

Începeți prin a clona depozitul:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Creați `.env` în directorul rădăcină `/firecrawl`: 
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
După ce ați terminat, descărcați fișierul OpenClaw Compose [openclaw-compose.yaml](assets/openclaw-compose.yaml) și plasați-l în directorul rădăcină `/firecrawl`:

> Această convenție este necesară pentru ca `systemd` să localizeze și să pornească serviciul corect, așa cum este specificat în `WorkingDirectory=${HOME}/firecrawl`.

> Puteți extinde oricând stiva, adăugând servicii Firecrawl suplimentare, după cum este necesar. Lista completă a serviciilor disponibile poate fi găsită în [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) oficial al Firecrawl.

### 4. Lansați serviciul OpenClaw prin Firecrawl 

Înainte de a preda controlul către `systemd`, validați că totul funcționează corect rulând stiva manual:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Dacă totul este configurat corect, ar trebui să vedeți containerul OpenClaw pornind, iar rezultatul din linia de comandă ar trebui să arate similar cu acesta:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Odată verificat, opriți stiva înainte de a continua:
```bash
podman compose -f openclaw-compose.yaml down
```
Înainte de a porni serviciul, trebuie să vă asigurați că sunt setate proprietatea și permisiunile corecte pentru directorul `firecrawl` și fișierul `.env` al acestuia. 
Acest lucru este esențial pentru ca serviciul să vă scrie credențialele la pornire.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Acum că totul este validat, porniți serviciul prin `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Acțiunile OpenClaw](https://docs.openclaw.ai/) sunt accesibile din interiorul containerului interactiv, iar Tabloul de bord Web este disponibil pe aceeași gazdă și port la http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obținerea `OPENCLAW_GATEWAY_TOKEN`-ului dumneavoastră

Odată ce serviciul este pornit și funcțional, veți observa un director nou `.openclaw` creat în folderul dumneavoastră personal (~/.openclaw). Acest director este blocat în mod implicit, așa că va trebui să îl deblocați pentru a recupera token-ul de gateway.

1. Acordați acces la director:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Citiți token-ul de gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Localizați valoarea `OPENCLAW_GATEWAY_TOKEN` în rezultat.

3. Deschideți tabloul de bord al gateway-ului în browser la http://127.0.0.1:18789. Lipiți token-ul atunci când vi se solicită autentificarea.

Pentru a opri serviciul, rulați:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Pornirea gateway-ului OpenClaw

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

Pentru a deschide dashboard-ul, rulați următoarea comandă într-un al doilea terminal, în timp ce gateway-ul rulează încă:

```bash
openclaw dashboard
```

Deoarece gateway-ul se leagă de loopback, dashboard-ul se autentifică automat atunci când este deschis de pe același calculator, nu este nevoie de introducerea vreunui token sau de aprobarea dispozitivului pentru accesul local. Ar trebui să vedeți dashboard-ul OpenClaw cu modelul dumneavoastră Lemonade listat ca backend activ.

> Dacă ați activat izolarea în sandbox (sandboxing), puteți verifica acest lucru cerându-i agentului să execute `run hostname` din dashboard. Dacă vedeți un ID scurt de container în loc de numele de gazdă al calculatorului dumneavoastră, sandbox-ul funcționează.

**Felicitări, ați construit de la zero un stack de agent AI complet local.**

> **Aveți nevoie de token-ul gateway-ului?** Rulați `openclaw dashboard --no-open` pentru a afișa adresa URL a dashboard-ului cu token-ul inclus (aceasta încearcă, de asemenea, să îl copieze în clipboard). Alternativ, token-ul se află la `gateway.auth.token` în `~/.openclaw/openclaw.json`.

**Accesarea dashboard-ului de pe un alt dispozitiv (prin tunel SSH)**

Dacă OpenClaw rulează pe un calculator la distanță, puteți accesa dashboard-ul acestuia de pe calculatorul dumneavoastră local printr-un tunel SSH. Tunelul redirecționează portul gateway-ului (`18789`) astfel încât browserul dumneavoastră local să poată comunica cu gateway-ul de la distanță prin `127.0.0.1`.

1. De pe **calculatorul dumneavoastră local**, conectați-vă o dată la calculatorul de la distanță și acceptați solicitarea de amprentă (fingerprint) astfel încât gazda să fie adăugată la lista de gazde cunoscute:

   ```bash
   ssh user@<host-ip>
   ```

2. Tot pe **calculatorul dumneavoastră local**, deschideți tunelul SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Notă:** După ce introduceți parola, terminalul nu afișează niciun rezultat și pare să se blocheze. Acest lucru este normal: flag-ul `-N` îi spune SSH să nu ruleze nicio comandă la distanță, astfel încât acesta pur și simplu menține tunelul deschis. Lăsați acest terminal să ruleze.

3. Pe **calculatorul dumneavoastră local**, deschideți un browser și accesați `http://127.0.0.1:18789`.

4. Pe **calculatorul de la distanță**, afișați token-ul gateway-ului și inserați-l în browser pentru a vă autentifica:

   ```bash
   openclaw dashboard --no-open
   ```

   Aceasta afișează adresa URL a dashboard-ului cu token-ul inclus; copiați token-ul pentru a vă autentifica. (Token-ul este de asemenea stocat la `gateway.auth.token` în `~/.openclaw/openclaw.json`.)

> **Aprobarea unui dispozitiv la distanță:** Când deschideți dashboard-ul de pe un alt calculator sau telefon, browserul poate afișa un ID de solicitare. Pe **calculatorul de la distanță**, listați solicitările în așteptare:
> ```bash
> openclaw devices list
> ```
> Apoi aprobați solicitarea corespunzătoare:
> ```bash
> openclaw devices approve <requestId>
> ```
> Acest lucru este necesar doar pentru dispozitive la distanță sau secundare; accesul loopback de pe același calculator se autentifică automat. Consultați documentația [Remote Access](https://docs.openclaw.ai/gateway/remote) pentru detalii.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opțional: Conectarea unui canal de comunicare

Odată ce gateway-ul rulează, puteți accesa agentul dumneavoastră local de pe orice dispozitiv. Alegeți opțiunea potrivită configurației dumneavoastră. OpenClaw suportă [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), și alte canale, consultați lista completă la [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opțiunea A: Discord

Discord necesită un server pentru care **aveți acces de administrator** pentru a adăuga un bot. Dacă partajați servere dar nu dețineți unul, folosiți în schimb Opțiunea B (Telegram).

#### Crearea unui cont și a unui server Discord

Dacă nu aveți un cont Discord, înregistrați-vă la [discord.com](https://discord.com). De asemenea, aveți nevoie de un server pentru care sunteți administrator, creați unul făcând clic pe pictograma **+** din bara laterală Discord și selectând **Create My Own**. Un server privat este suficient.

#### Crearea unei aplicații și a unui bot Discord

1. Accesați [Discord Developer Portal](https://discord.com/developers/applications) și faceți clic pe **New Application**. Dați-i un nume (de ex. "openclaw-bot").
2. În bara laterală, faceți clic pe **Bot**. Setați un nume de utilizator pentru bot.
3. Tot pe pagina Bot, derulați până la **Privileged Gateway Intents** și activați:
   - **Message Content Intent** (obligatoriu)
   - **Server Members Intent** (recomandat)
4. Derulați înapoi în sus și faceți clic pe **Reset Token** pentru a genera token-ul botului. Copiați-l.

#### Adăugarea botului pe serverul dumneavoastră

1. În bara laterală, faceți clic pe **OAuth2/ URL Generator**.
2. Sub **Scopes**, activați `bot` și `applications.commands`.
3. Sub **Bot Permissions**, activați: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiați adresa URL generată, inserați-o în browser, selectați serverul dumneavoastră și confirmați. Botul ar trebui să apară acum în lista de membri a serverului dumneavoastră.

#### Colectarea ID-urilor dumneavoastră

Activați Developer Mode în Discord (**User Settings/ Advanced/ Developer Mode**), apoi:
- Faceți clic dreapta pe pictograma serverului dumneavoastră: **Copy Server ID**
- Faceți clic dreapta pe propriul avatar: **Copy User ID**

#### Permiterea mesajelor directe de la membrii serverului

Faceți clic dreapta pe pictograma serverului dumneavoastră/ **Privacy Settings**/ activați **Direct Messages**. Acest lucru permite botului să vă trimită mesaje directe, ceea ce este necesar pentru etapa de asociere (pairing).

#### Configurarea OpenClaw pentru Discord

Stocați token-ul botului dumneavoastră ca variabilă de mediu, apoi creați un singur fișier patch care activează Discord, face referire la token și adaugă serverul dumneavoastră pe lista permisă. Înlocuiți `<server_id>` și `<user_id>` cu ID-urile colectate mai sus.

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

> **Nu vă bazați pe solicitarea agentului să configureze acest lucru.** Când izolarea în sandbox este activată, agentul nu poate scrie în `~/.openclaw/openclaw.json` din interiorul sandbox-ului, folosiți în schimb comenzile CLI de mai sus pe gazdă.

Reporniți gateway-ul pentru ca acesta să preia noua configurație a canalului:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ar trebui să vedeți `logged in to discord as <bot-name>` în rezultatul gateway-ului în câteva secunde.
#### Asociați contul dvs. Discord

Trimiteți un mesaj privat bot-ului în Discord. Acesta va răspunde cu un cod scurt de asociere.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprobați-l pe mașina pe care rulează OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Codurile de asociere expiră după o oră.

Acum puteți discuta cu agentul dvs. direct din Discord și puteți delega sarcini către hardware-ul dvs. local.

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

Adăugați configurația canalului în `~/.openclaw/openclaw.json` (sau aplicați un patch prin dashboard):

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

Reporniți gateway-ul, apoi trimiteți bot-ului dvs. orice mesaj în Telegram. Aprobați asocierea:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Codurile de asociere expiră după o oră. Acum puteți discuta cu agentul dvs. prin mesaje private pe Telegram.

---

## Pași următori

Acum că agentul dvs. poate primi comenzi de pe telefonul dvs. și poate acționa pe mașina dvs. locală, iată trei direcții demne de explorat:

1. **Sumarizator pentru piața bursieră**: Programați OpenClaw să preia date de la API-uri financiare la un interval fix, să sumarizeze mișcările zilei cu modelul dvs. local și să trimită un rezumat pe telefonul dvs. în fiecare dimineață prin canalul ales de dvs.

2. **Monitor de fine-tuning**: Porniți o sarcină de antrenare de la distanță prin Telegram sau Discord, apoi puneți agentul să urmărească jurnalul de antrenare și să raporteze periodic valorile de pierdere (loss), utilizarea GPU și utilizarea discului înapoi pe telefonul dvs. Dacă rularea se blochează sau memoria VRAM crește brusc, aflați imediat, fără a fi nevoie să fiți la mașină.

3. **IOT cu un VLM local**: Îndreptați o cameră spre ușa din față, rulați un model de viziune pe Lemonade și puneți OpenClaw să analizeze cadrele la cerere sau la declanșarea unui declanșator. Întrebați "au sosit pachete azi?" de pe telefonul dvs. și obțineți un răspuns direct de la propriul dvs. hardware.

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