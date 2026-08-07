<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Rularea Hermes Agent local cu Lemonade Server

## Prezentare generală

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) este un agent AI care se auto-îmbunătățește, dezvoltat de Nous Research. Are o buclă de învățare integrată, creează abilități din experiență, construiește o memorie persistentă despre cine sunteți între sesiuni și poate rula automatizări programate în numele dumneavoastră. Spre deosebire de un simplu asistent de chat, Hermes întreprinde acțiuni reale: rulează comenzi shell, scrie fișiere, navighează pe web și delegă fluxuri de lucru paralele către subagenți.

[**Lemonade Server**](https://lemonade-server.ai/) este backend-ul de inferență local care îl alimentează. Este un server open-source care rulează modele GenAI direct pe hardware-ul dumneavoastră AMD și le expune prin API-ul standard din industrie OpenAI.

Împreună, formează un stack complet local de AI agentic: Lemonade se ocupă de inferența modelului pe GPU, iar Hermes furnizează bucla agentului, memoria, abilitățile și gateway-ul de mesagerie.

> **Înainte de a continua:** Hermes Agent este un agent AI extrem de autonom. Acordarea accesului oricărui agent AI la sistemul dumneavoastră poate duce la rezultate imprevizibile sau neintenționate. Continuați doar dacă înțelegeți riscurile și vă simțiți confortabil cu software autonom care acționează în numele dumneavoastră.

---

## Ce veți învăța

Până la finalul acestui ghid veți putea:

- **Instala Hermes Agent** și îl configura să folosească **Lemonade Server** ca backend AI.
- **(Recomandat) Activa sandboxing-ul Docker/Podman** pentru a izola acțiunile agentului de sistemul gazdă.
- **Porni gateway-ul Hermes** și confirma că agentul dumneavoastră este pregătit.
- **Conecta un canal de comunicare** (Discord sau Telegram) pentru a putea discuta cu agentul dumneavoastră de pe orice dispozitiv.

---

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările software-ului

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea condițiilor prealabile software

<!-- @os:linux -->
- Un PC cu **Ubuntu 24.04+** sau o distribuție Linux compatibilă bazată pe Debian cu `apt-get`
- Cel puțin **12 GB de RAM** (64 GB+ recomandat pentru modele mai mari)
- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
- [Podman](https://podman.io/docs/installation) (Opțional, pentru sandboxing-ul Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Un PC cu **Windows 10/11**
- Cel puțin **12 GB de RAM** (64 GB+ recomandat pentru modele mai mari)
- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
- Podman (Opțional, pentru sandboxing-ul Hermes Agent). Instalați în WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman este preinstalat pe Halo Box și nu este necesară nicio configurare
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descărcați și încărcați modelul recomandat

Modelul recomandat pentru acest ghid este **Qwen3.6-35B-A3B-GGUF** de la Unsloth, un model MoE puternic cu o fereastră de context de 263k token-uri, potrivit pentru sarcinile agentice. Acest model folosește cuantizarea UD-Q4_K_XL. Descărcați-l acum:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Apoi încărcați-l cu o fereastră de context mare și salvați această setare pentru rulările viitoare:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Modelul are o lungime de context implicită de 262.144 token-uri. Dacă întâmpinați erori de lipsă de memorie (OOM), luați în considerare reducerea ferestrei de context.

> **Sfat: Dezactivați modul de gândire pentru răspunsuri mai rapide ale agentului:** Qwen3.6-35B-A3B rulează implicit în modul de gândire, ceea ce adaugă latență înainte de fiecare răspuns. Pentru buclele agentice, acest overhead se acumulează rapid. Depozitul [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) oferă o configurație gata făcută care dezactivează modul de gândire. Pentru a o folosi, descărcați fișierul și importați-l:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

## Configurați WSL

Rulăm Hermes Agent în interiorul WSL și îl conectăm la Lemonade, care rulează nativ pe Windows. Astfel obțineți un mediu shell Linux pentru Hermes, păstrând în același timp accelerarea GPU a Lemonade pe partea Windows.

### Instalați WSL și Ubuntu

Deschideți PowerShell ca Administrator și instalați nucleul WSL:

```powershell
wsl --install --no-distribution
```

Apoi instalați Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Activați systemd în WSL

Rulați aceasta în terminalul Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Reporniți WSL:

```powershell
wsl --shutdown
wsl
```

### Conectați Lemonade de pe Windows în WSL

WSL2 rulează într-o rețea virtuală. Lemonade pe Windows se leagă la `127.0.0.1`, la care WSL nu poate ajunge direct. Un proxy de port Windows redirecționează traficul de la IP-ul gateway-ului WSL către localhost-ul Windows.

**Găsiți IP-ul gateway-ului WSL** (rulați în interiorul WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adăugați proxy-ul de port** (rulați în PowerShell ca Administrator, înlocuind `<WSL-Gateway-IP>` cu IP-ul gateway-ului dumneavoastră WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adăugați o regulă de firewall** (același PowerShell cu drepturi de administrator):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verificați din WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Dacă ați încărcat deja modelul Qwen3.6-35B-A3B-GGUF în pasul anterior, ar trebui să vedeți un rezultat JSON care listează modelul încărcat.

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

> Regula `netsh portproxy` supraviețuiește repornirilor, dar IP-ul gateway-ului WSL se poate schimba după `wsl --shutdown`. Dacă Lemonade devine inaccesibil din WSL după o repornire, obțineți noul IP al gateway-ului și actualizați proxy-ul cu acest IP nou.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Instalați Hermes Agent

<!-- @os:windows -->
> Rulați comenzile din această secțiune în interiorul terminalului **WSL**, cu excepția cazului în care se specifică altfel.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Flag-ul `--skip-setup` omite asistentul de configurare interactiv, astfel încât să puteți configura manual backend-ul modelului în pasul următor.

Reîncărcați shell-ul:

```bash
source ~/.bashrc
```

Confirmați instalarea:

```bash
hermes --version
```

Rulați un autodiagnostic pentru a verifica toate dependențele:

```bash
hermes doctor
```

> **Sfat:** Dacă vedeți `command not found` după instalare, adăugați Hermes la PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Pentru a face aceasta permanentă, adăugați linia de mai sus în fișierul dumneavoastră `~/.bashrc` sau `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Configurați Hermes să folosească Lemonade

Hermes își stochează configurația modelului în `~/.hermes/config.yaml`. Puteți fie să folosiți selectorul interactiv `hermes model`, fie să scrieți configurația direct.

### Opțiunea 1: Selector interactiv

<!-- @os:windows -->
> Rulați următoarea comandă în **terminalul WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Când vi se solicită:

1. Selectați **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** folosiți IP-ul gateway-ului WSL: rulați `ip route show default | awk '{print $3}' | head -1` în WSL pentru a-l obține, apoi introduceți `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** alegeți `Qwen3.6-35B-A3B-GGUF` din listă
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (sau orice nume preferați)

`hermes model` salvează atât selecția modelului activ, cât și o intrare `custom_providers` denumită, care stochează lungimea contextului împreună cu endpoint-ul. Rezultatul în `~/.hermes/config.yaml` arată astfel:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Opțiunea 2: Scrierea directă a configurației

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

În terminalul WSL, obțineți IP-ul gazdei Windows și scrieți configurația:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Recomandat) Activați izolarea Podman (sandboxing)

Hermes Agent poate direcționa toate operațiunile agentului legate de shell și fișiere printr-un container izolat, în loc să le execute direct pe gazda dvs. Acest lucru limitează raza de impact a oricărei acțiuni neintenționate la sandbox, lăsând sistemul de fișiere și rețeaua gazdei dvs. neatinse.

Construiți o imagine sandbox ușoară:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Intrați în terminalul WSL:

```powershell
wsl -d Ubuntu-24.04
```

Apoi, construiți o imagine sandbox ușoară:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Apoi configurați Hermes să folosească Podman ca runtime pentru containere și setați backend-ul terminalului:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` rămâne `docker`.
> `HERMES_DOCKER_BINARY` este cel care indică lui Hermes să folosească Podman ca runtime în locul acestuia.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes va porni acum un container sandbox persistent și va direcționa toate apelurile `terminal` și cele ale instrumentelor pentru fișiere prin acesta. Containerul are aceeași durată de viață ca procesul Hermes, este reutilizat pentru toate apelurile instrumentelor și este distrus la închiderea Hermes.

> **Verificați dacă sandbox-ul funcționează:** Porniți Hermes (`hermes`) și cereți-i să `run hostname` - ar trebui să vedeți un ID scurt de container în loc de numele de gazdă al mașinii dvs. Puteți, de asemenea, să îi cereți să `rm -rf <path-to-a-dummy-file/folder>`: Hermes va confirma ștergerea, dar folderul va rămâne pe gazda dvs. Comanda a rulat în interiorul `$HOME`-ului izolat al containerului, nu al dvs.

> **Aveți nevoie de o izolare mai puternică?** Hermes oferă de asemenea o imagine Docker oficială (`nousresearch/hermes-agent`) care rulează întregul proces al agentului în interiorul unui container - gateway, instrumente și tot restul. Consultați [documentația Docker pentru Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) pentru detalii de configurare.

---

<!-- @os:linux -->
## (Recomandat) Integrarea Hermes cu serviciile Firecrawl

Hermes poate naviga și extrage conținut de pe site-uri web folosind instrumentele sale web integrate. Totuși, multe site-uri web moderne folosesc sisteme de detectare a boților, care blochează cererile HTTP simple și returnează pagini de provocare (challenge pages) în locul conținutului real. Ca urmare, Hermes ar putea să nu poată extrage informații în mod fiabil de pe aceste site-uri.

Pentru a depăși această limitare, [Firecrawl](https://docs.firecrawl.dev/introduction) oferă un serviciu de crawling web și extragere a conținutului găzduit local, care poate ocoli aceste provocări și poate debloca întregul potențial al automatizării Hermes.

În această configurație, Firecrawl rulează ca un set de containere Docker gestionate cu Podman. Pentru a simplifica gestionarea ciclului de viață și pornirea automată, înregistrăm Firecrawl ca un serviciu `systemd` la nivel de utilizator, care orchestrează stiva Podman Compose subiacentă. Acest lucru permite Hermes să pornească, să oprească și să verifice serviciul Firecrawl folosind comenzi standard `systemctl --user`, în loc să interacționeze direct cu containerele.

Pentru a păstra lucrurile simple, am împărțit întregul proces în patru pași:

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
Copiați și lipiți următoarea configurație:
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
În acest moment, serviciul a fost definit, dar nu a fost încă înregistrat cu `systemd`. 
Asigurați-vă că numele fișierului corespunde exact cu cel creat mai sus, apoi rulați:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Dacă are succes, ar trebui să vedeți următorul rezultat:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` conține linkuri simbolice către serviciile configurate să pornească automat.

### 2. Configurați Firecrawl pentru serviciul dvs.

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) este ideal pentru cei care au nevoie de control total asupra mediilor lor de scraping și procesare a datelor, dar vine cu costul unor eforturi suplimentare de întreținere și configurare.

Începeți prin a clona repository-ul:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Creați `.env` în directorul rădăcină `/firecrawl`:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Setați `BULL_AUTH_KEY` la un secret puternic, mai ales pentru orice implementare accesibilă din rețele nesigure.
### 3. Implementarea Hermes prin Compose

Înainte de a continua, asigurați-vă că ați descărcat cea mai recentă imagine Docker Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
După ce ați terminat, descărcați fișierul Compose Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) și plasați-l în directorul rădăcină `/firecrawl`:

> Această convenție este necesară pentru ca `systemd` să localizeze și să pornească serviciul corect, conform specificațiilor din `WorkingDirectory=${HOME}/firecrawl`.

> Puteți extinde oricând stiva adăugând servicii Firecrawl suplimentare, după cum este necesar. Lista completă a serviciilor disponibile poate fi găsită în [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) oficial al Firecrawl.

### 4. Lansați serviciul Hermes prin Firecrawl 

Înainte de a preda controlul către `systemd`, validați că totul funcționează corect rulând stiva manual:
```bash
podman compose -f hermes-compose.yaml up -d
```
Dacă totul este configurat corect, ar trebui să vedeți containerul Hermes pornind, iar rezultatul din linia de comandă ar trebui să arate similar cu acesta:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Odată verificat, opriți stiva înainte de a continua:
```bash
podman compose -f hermes-compose.yaml down
```
Acum că totul a fost validat, porniți serviciul prin `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API-ul Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) este accesibil din interiorul containerului interactiv, iar Panoul de bord Web este disponibil pe același host și port la http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Pentru a opri serviciul, rulați:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Porniți o sesiune CLI interactivă direct: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Felicitări, ați construit o stivă de agent AI complet locală.**

### Panoul de bord Web

Hermes include o interfață bazată pe browser pentru gestionarea configurației, cheilor API, modelelor, sesiunilor, memoriei și sarcinilor cron. Deschideți un al doilea terminal în timp ce gateway-ul sau CLI-ul rulează și lansați-l cu:

```bash
hermes dashboard
```

Aceasta pornește un server local și deschide `http://127.0.0.1:9119` în browserul dumneavoastră. Consultați [documentația panoului de bord](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) pentru referința completă a funcționalităților.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opțional: Conectarea unui canal de comunicare

Odată ce gateway-ul rulează, puteți accesa agentul local de pe orice dispozitiv. Hermes acceptă [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) și altele

---

### Discord

Discord necesită un server unde **aveți acces de administrator** pentru a adăuga un bot. Dacă partajați servere, dar nu dețineți niciunul, folosiți Telegram în schimb.

#### Creați o aplicație Discord și un bot

1. Accesați [Discord Developer Portal](https://discord.com/developers/applications) și faceți clic pe **New Application**. Dați-i un nume (de exemplu, „hermes-bot”).
2. În bara laterală, faceți clic pe **Bot**. Setați un nume de utilizator pentru bot.
3. Rămânând pe pagina Bot, derulați până la **Privileged Gateway Intents** și activați:
   - **Message Content Intent** (obligatoriu)
   - **Server Members Intent** (recomandat)
4. Derulați înapoi în sus și faceți clic pe **Reset Token** pentru a genera token-ul botului dumneavoastră. Copiați-l.

#### Adăugați botul pe serverul dumneavoastră

1. În bara laterală, faceți clic pe **OAuth2 / URL Generator**.
2. La secțiunea **Scopes**, activați `bot` și `applications.commands`.
3. La secțiunea **Bot Permissions**, activați: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiați URL-ul generat, lipiți-l în browserul dumneavoastră, selectați serverul și confirmați.

#### Colectați ID-urile și permiteți mesajele directe

Activați Developer Mode în Discord (**User Settings / Advanced / Developer Mode**), apoi:
- Faceți clic dreapta pe pictograma serverului dumneavoastră: **Copy Server ID**
- Faceți clic dreapta pe propriul avatar: **Copy User ID**

Faceți clic dreapta pe pictograma serverului dumneavoastră / **Privacy Settings** / activați **Direct Messages**. Acest lucru este necesar pentru pasul de asociere.

#### Configurați Hermes pentru Discord

Adăugați următoarele în `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Apoi porniți gateway-ul:

```bash
hermes gateway
```

Botul ar trebui să apară online în Discord în câteva secunde. Trimiteți-i un mesaj, fie un mesaj direct, fie într-un canal pe care îl poate vedea.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Creați un bot Telegram

1. Deschideți Telegram și trimiteți un mesaj către **@BotFather**.
2. Trimiteți `/newbot` și urmați instrucțiunile. Salvați token-ul botului pe care vi-l oferă.

#### Configurați Hermes pentru Telegram

Adăugați următoarele în `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Nu vă cunoașteți ID-ul de utilizator Telegram?** Trimiteți un mesaj către [@userinfobot](https://t.me/userinfobot) în Telegram, vă va răspunde cu ID-ul dumneavoastră numeric.

Apoi porniți gateway-ul:

```bash
hermes gateway
```

Trimiteți botului dumneavoastră orice mesaj în Telegram pentru testare. Acum puteți discuta cu agentul dumneavoastră prin mesaje directe pe Telegram. Consultați [ghidul complet de configurare Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) pentru modul webhook și opțiuni avansate.

---

## Pașii următori

Acum că agentul dumneavoastră poate primi comenzi de pe telefon și poate acționa pe mașina locală, iată trei direcții care merită explorate:

1. **Rezumat automat de cercetare**: Programați Hermes să caute pe web subiecte care vă interesează în fiecare dimineață, să rezume rezultatele cu modelul dumneavoastră local și să trimită un rezumat pe telefon prin Telegram sau Discord, totul rulând pe propriul hardware, fără costuri în cloud.

2. **Revizuire de cod la cerere**: Îndreptați Hermes către un repository GitHub, cereți-i să revizuiască pull request-urile deschise și să posteze comentarii sau un rezumat înapoi în chat-ul dumneavoastră. Cu backend-ul de terminal Docker, toate operațiunile git rulează în interiorul sandbox-ului, păstrând sistemul gazdă curat.

3. **Asistent de fișiere local**: Oferiți Hermes acces la un director de lucru și cereți-i să organizeze, redenumească, rezume sau transforme fișiere la cerere de pe telefon. Deoarece backend-ul de terminal Docker restricționează toate operațiunile de scriere la spațiul de lucru sandbox, operațiunile accidentale distructive sunt izolate.