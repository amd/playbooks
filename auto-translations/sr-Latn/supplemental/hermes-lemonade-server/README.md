<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Pokretanje Hermes Agent-a lokalno pomoću Lemonade Server-a

## Pregled

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) je AI agent koji se samostalno usavršava, izgrađen od strane Nous Research. Ima ugrađenu petlju učenja, kreira veštine na osnovu iskustva, gradi trajnu memoriju o tome ko ste vi kroz sesije, i može da pokreće zakazane automatizacije u vaše ime. Za razliku od jednostavnog chat asistenta, Hermes preduzima stvarne akcije: pokreće shell komande, piše fajlove, pretražuje veb i delegira paralelne radne tokove pomoćnim agentima.

[**Lemonade Server**](https://lemonade-server.ai/) je lokalni inferencijalni backend koji ga pokreće. To je open-source server koji pokreće GenAI modele direktno na vašem AMD hardveru i izlaže ih putem industrijskog standarda OpenAI API-ja.

Zajedno formiraju potpuno lokalan AI agent stek: Lemonade upravlja inferencijom modela na vašem GPU-u, a Hermes pruža petlju agenta, memoriju, veštine i gateway za razmenu poruka.

> **Pre nego što nastavite:** Hermes Agent je visoko autonoman AI agent. Davanje bilo kom AI agentu pristupa vašem sistemu može rezultovati nepredvidivim ili nenamernim ishodima. Nastavite samo ako razumete rizike i osećate se prijatno sa autonomnim softverom koji deluje u vaše ime.

---

## Šta ćete naučiti

Do kraja ovog priručnika bićete u mogućnosti da:

- **Instalirate Hermes Agent** i usmerite ga na **Lemonade Server** kao njegov AI backend.
- **(Preporučeno) Omogućite Docker/Podman sandboxing** kako biste izolovali akcije agenta od vašeg host sistema.
- **Pokrenete Hermes gateway** i potvrdite da je vaš agent spreman.
- **Povežete komunikacioni kanal** (Discord ili Telegram) kako biste mogli da ćaskate sa svojim agentom sa bilo kog uređaja.

---

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje softverskih preduslova

<!-- @os:linux -->
- PC koji koristi **Ubuntu 24.04+** ili kompatibilnu Debian-baziranu Linux distribuciju sa `apt-get`
- Najmanje **12 GB RAM-a** (64 GB+ preporučeno za veće modele)
- **~10–30 GB slobodnog prostora na disku** za težine modela
- [Podman](https://podman.io/docs/installation) (opciono, za sandboxing Hermes Agent-a)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- PC koji koristi **Windows 10/11**
- Najmanje **12 GB RAM-a** (64 GB+ preporučeno za veće modele)
- **~10–30 GB slobodnog prostora na disku** za težine modela
- Podman (opciono, za sandboxing Hermes Agent-a). Instalirajte unutar WSL-a:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman je unapred instaliran na Halo Box-u i nije potrebno dodatno podešavanje
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Preuzmite i učitajte preporučeni model

Preporučeni model za ovaj priručnik je **Qwen3.6-35B-A3B-GGUF** od Unsloth-a, snažan MoE model sa kontekstnim prozorom od 263k tokena koji je dobro prilagođen za radne tokove agenata. Ovaj model koristi UD-Q4_K_XL kvantizaciju. Preuzmite ga sada:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Zatim ga učitajte sa velikim kontekstnim prozorom i sačuvajte to podešavanje za buduća pokretanja:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model ima podrazumevanu dužinu konteksta od 262.144 tokena. Ako naiđete na greške zbog nedostatka memorije (OOM), razmotrite smanjenje kontekstnog prozora.

> **Savet: Onemogućite razmišljanje za brže odgovore agenta:** Qwen3.6-35B-A3B se podrazumevano pokreće u režimu razmišljanja, što dodaje kašnjenje pre svakog odgovora. Za petlje agenata ovo opterećenje se brzo gomila. Repozitorijum [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) pruža gotovu konfiguraciju koja onemogućava razmišljanje. Da biste je koristili, preuzmite fajl i uvezite ga:
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

## Podesite WSL

Hermes Agent pokrećemo unutar WSL-a i povezujemo ga sa Lemonade-om koji radi nativno na Windows-u. Ovo vam pruža Linux shell okruženje za Hermes uz istovremeno zadržavanje GPU akceleracije Lemonade-a na Windows strani.

### Instalirajte WSL i Ubuntu

Otvorite PowerShell kao administrator i instalirajte WSL kernel:

```powershell
wsl --install --no-distribution
```

Zatim instalirajte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogućite systemd u WSL-u

Pokrenite ovo unutar Ubuntu terminala:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ponovo pokrenite WSL:

```powershell
wsl --shutdown
wsl
```

### Premostite Lemonade sa Windows-a u WSL

WSL2 radi u virtuelnoj mreži. Lemonade na Windows-u se vezuje za `127.0.0.1`, do čega WSL ne može direktno da dopre. Windows port proxy prosleđuje saobraćaj sa WSL gateway IP adrese ka Windows localhost-u.

**Pronađite vašu WSL gateway IP adresu** (pokrenite unutar WSL-a):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte port proxy** (pokrenite u PowerShell-u kao administrator, zamenjujući `<WSL-Gateway-IP>` sa vašom WSL gateway IP adresom):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodajte pravilo firewall-a** (isti podignuti PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Proverite iz WSL-a**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ako ste već učitali model Qwen3.6-35B-A3B-GGUF u prethodnom koraku, trebalo bi da vidite JSON izlaz koji navodi vaš učitani model.

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

> Pravilo `netsh portproxy` opstaje nakon ponovnog pokretanja, ali WSL gateway IP adresa se može promeniti nakon `wsl --shutdown`. Ako Lemonade postane nedostupan iz WSL-a nakon ponovnog pokretanja, dobavite ažuriranu gateway IP adresu i ažurirajte proxy sa ovom novom IP adresom.

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

## Instalirajte Hermes Agent

<!-- @os:windows -->
> Pokrenite komande u ovom odeljku unutar vašeg **WSL terminala** osim ako nije drugačije naznačeno.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Oznaka `--skip-setup` preskače interaktivni čarobnjak za podešavanje kako biste mogli ručno da konfigurišete backend modela u sledećem koraku.

Ponovo učitajte vaš shell:

```bash
source ~/.bashrc
```

Potvrdite instalaciju:

```bash
hermes --version
```

Pokrenite samostalnu dijagnostiku da proverite sve zavisnosti:

```bash
hermes doctor
```

> **Savet:** Ako vidite `command not found` nakon instalacije, dodajte Hermes u vaš PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Da biste ovo učinili trajnim, dodajte gornju liniju u vaš `~/.bashrc` ili `~/.zshrc`.

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
## Konfigurisanje Hermes-a za korišćenje Lemonade-a

Hermes čuva konfiguraciju modela u `~/.hermes/config.yaml`. Možete koristiti ili interaktivni birač `hermes model` ili direktno napisati konfiguraciju.

### Opcija 1: Interaktivni birač

<!-- @os:windows -->
> Pokrenite sledeće unutar vašeg **WSL terminala**.
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

Kada budete upitani:

1. Izaberite **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** koristite WSL gateway IP: pokrenite `ip route show default | awk '{print $3}' | head -1` unutar WSL-a da ga dobijete, a zatim unesite `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** izaberite `Qwen3.6-35B-A3B-GGUF` sa liste
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (ili bilo koje ime po vašem izboru)

`hermes model` čuva i aktivni izbor modela i imenovani unos u `custom_providers` koji čuva dužinu konteksta zajedno sa endpoint-om. Rezultat u `~/.hermes/config.yaml` izgleda ovako:

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

### Opcija 2: Direktno pisanje konfiguracije

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

Unutar vašeg WSL terminala, dobijte IP adresu Windows hosta i upišite konfiguraciju:

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

## (Preporučeno) Omogućavanje Podman izolacije (sandboxing)

Hermes Agent može usmeriti sve operacije agenta nad shell-om i fajlovima kroz izolovan kontejner umesto da ih pokreće direktno na vašem hostu. Ovo ograničava domet svake neželjene akcije na sandbox, ostavljajući fajl sistem i mrežu vašeg hosta netaknutim.

Izgradite lagani sandbox image:

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
Uđite u vaš WSL terminal:

```powershell
wsl -d Ubuntu-24.04
```

Zatim izgradite lagani sandbox image:

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

Zatim konfigurišite Hermes da koristi Podman kao container runtime i podesite terminal backend:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` je i dalje `docker`.
> `HERMES_DOCKER_BINARY` je ono što govori Hermes-u da koristi Podman kao runtime umesto toga.

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

Hermes će sada pokrenuti trajni sandbox kontejner i usmeriti sve pozive `terminal` alata i alata za rad sa fajlovima kroz njega. Kontejner deli životni vek sa Hermes procesom, ponovo se koristi za sve pozive alata i uništava se kada se Hermes ugasi.

> **Proverite da li sandbox radi:** Pokrenite Hermes (`hermes`) i zatražite od njega da izvrši `run hostname` - trebalo bi da vidite kratak ID kontejnera umesto imena vaše mašine (hostname). Takođe možete tražiti da izvrši `rm -rf <path-to-a-dummy-file/folder>`: Hermes će potvrditi brisanje, ali fascikla će i dalje biti prisutna na vašem hostu. Komanda je izvršena unutar izolovanog `$HOME` kontejnera, a ne vašeg.

> **Potrebna vam je jača izolacija?** Hermes takođe pruža zvaničnu Docker sliku (`nousresearch/hermes-agent`) koja pokreće ceo proces agenta unutar kontejnera - gateway, alate i sve ostalo. Pogledajte [Hermes Docker dokumentaciju](https://hermes-agent.nousresearch.com/docs/user-guide/docker) za detalje podešavanja.

---

<!-- @os:linux -->
## (Preporučeno) Integracija Hermes-a sa Firecrawl uslugama

Hermes može da pretražuje i izdvaja sadržaj sa veb sajtova koristeći svoje ugrađene veb alate. Međutim, mnogi moderni veb sajtovi koriste sisteme za detekciju botova, koji blokiraju jednostavne HTTP zahteve i vraćaju stranice sa izazovima (challenge pages) umesto stvarnog sadržaja. Kao rezultat toga, Hermes možda neće moći pouzdano da izvuče informacije sa ovih sajtova.

Da bi se prevazišlo ovo ograničenje, [Firecrawl](https://docs.firecrawl.dev/introduction) pruža samostalno hostovanu (self-hosted) uslugu za pretraživanje veba i izdvajanje sadržaja koja može da zaobiđe ove izazove i otključa pun potencijal Hermes automatizacije.

U ovom podešavanju, Firecrawl radi kao skup Docker kontejnera kojima upravlja Podman. Da bismo pojednostavili upravljanje životnim ciklusom i automatsko pokretanje, registrujemo Firecrawl kao `systemd` uslugu na nivou korisnika koja orkestrira osnovni Podman Compose stack. Ovo omogućava Hermes-u da pokreće, zaustavlja i proverava Firecrawl uslugu koristeći standardne `systemctl --user` komande umesto direktne interakcije sa kontejnerima.

Da bismo pojednostavili stvari, podelili smo ceo proces na četiri koraka:

---

### 1. Registrovanje sistemske usluge
Navigirajte do direktorijuma za korisničku konfiguraciju systemd-a:
```bash
cd ~/.config/systemd/user
```
Napravite i otvorite novi fajl pod nazivom `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopirajte i nalepite sledeću konfiguraciju:
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
U ovom trenutku, usluga je definisana ali još nije registrovana kod `systemd`-a.
Uverite se da naziv fajla tačno odgovara onom koji ste napravili gore, a zatim pokrenite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ako je uspešno, trebalo bi da vidite sledeći izlaz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` sadrži simboličke linkove ka uslugama koje su konfigurisane da se pokreću automatski.

### 2. Konfigurisanje Firecrawl-a za vašu uslugu

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealan za one kojima je potrebna potpuna kontrola nad okruženjima za scraping i obradu podataka, ali dolazi sa kompromisom dodatnog održavanja i napora oko konfiguracije.

Počnite kloniranjem repozitorijuma:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Napravite `.env` u korenskom `/firecrawl` direktorijumu:
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
> Podesite `BULL_AUTH_KEY` na jaku tajnu vrednost, posebno na svakom razvojnom okruženju dostupnom iz nepoverljivih mreža.
### 3. Postavljanje Hermesa putem Compose-a

Pre nego što nastavite, proverite da li ste povukli najnoviju Docker sliku Hermesa:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Nakon što to uradite, preuzmite Compose fajl za Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) i postavite ga u koreni direktorijum `/firecrawl`:

> Ova konvencija je neophodna da bi `systemd` mogao da pronađe i pokrene servis ispravno, kao što je definisano u `WorkingDirectory=${HOME}/firecrawl`.

> Uvek možete proširiti stack dodavanjem dodatnih Firecrawl servisa po potrebi. Kompletna lista dostupnih servisa nalazi se u zvaničnom [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fajlu.

### 4. Pokretanje Hermes servisa putem Firecrawl-a

Pre nego što prepustite kontrolu `systemd`-u, proverite da li sve radi ispravno tako što ćete ručno pokrenuti stack:
```bash
podman compose -f hermes-compose.yaml up -d
```
Ako je sve ispravno podešeno, trebalo bi da vidite da se Hermes kontejner pokreće, a izlaz u komandnoj liniji trebalo bi da izgleda otprilike ovako:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Kada to potvrdite, ugasite stack pre nego što nastavite:
```bash
podman compose -f hermes-compose.yaml down
```
Sada kada je sve provereno, pokrenite servis putem `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) je dostupan iz interaktivnog kontejnera, a Web Dashboard je dostupan na istom hostu i portu na adresi http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Da biste zaustavili servis, pokrenite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Pokrenite interaktivnu CLI sesiju direktno:

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

**Čestitamo, izgradili ste potpuno lokalan AI agent stack.**

### Web Dashboard

Hermes uključuje korisnički interfejs zasnovan na pregledaču za upravljanje konfiguracijom, API ključevima, modelima, sesijama, memorijom i cron zadacima. Otvorite drugi terminal dok gateway ili CLI rade i pokrenite ga sa:

```bash
hermes dashboard
```

Ovo pokreće lokalni server i otvara `http://127.0.0.1:9119` u vašem pregledaču. Pogledajte [dokumentaciju dashboard-a](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) za kompletan pregled funkcionalnosti.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opciono: Povezivanje komunikacionog kanala

Kada gateway radi, možete pristupiti svom lokalnom agentu sa bilo kog uređaja. Hermes podržava [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) i druge

---

### Discord

Za Discord je potreban server na kojem **imate administratorski pristup** kako biste dodali bota. Ako delite servere ali nijedan ne posedujete, umesto toga koristite Telegram.

#### Kreiranje Discord aplikacije i bota

1. Idite na [Discord Developer Portal](https://discord.com/developers/applications) i kliknite na **New Application**. Dajte mu naziv (npr. "hermes-bot").
2. U bočnoj traci kliknite na **Bot**. Postavite korisničko ime za bota.
3. Na istoj stranici Bot, skrolujte do **Privileged Gateway Intents** i omogućite:
   - **Message Content Intent** (obavezno)
   - **Server Members Intent** (preporučeno)
4. Vratite se nazad i kliknite na **Reset Token** da biste generisali token bota. Kopirajte ga.

#### Dodavanje bota na vaš server

1. U bočnoj traci kliknite na **OAuth2 / URL Generator**.
2. Pod **Scopes**, omogućite `bot` i `applications.commands`.
3. Pod **Bot Permissions**, omogućite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte generisani URL, nalepite ga u pregledač, izaberite vaš server i potvrdite.

#### Prikupljanje ID-jeva i omogućavanje direktnih poruka

Omogućite Developer Mode u Discord-u (**User Settings / Advanced / Developer Mode**), a zatim:
- Kliknite desnim tasterom na ikonu vašeg servera: **Copy Server ID**
- Kliknite desnim tasterom na svoj avatar: **Copy User ID**

Kliknite desnim tasterom na ikonu vašeg servera / **Privacy Settings** / uključite **Direct Messages**. Ovo je neophodno za korak uparivanja.

#### Konfigurisanje Hermesa za Discord

Dodajte sledeće u `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Zatim pokrenite gateway:

```bash
hermes gateway
```

Bot bi trebalo da postane dostupan na Discord-u za nekoliko sekundi. Pošaljite mu poruku, bilo direktnu poruku ili u kanalu koji može da vidi.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Kreiranje Telegram bota

1. Otvorite Telegram i pošaljite poruku **@BotFather**.
2. Pošaljite `/newbot` i pratite uputstva. Sačuvajte token bota koji dobijete.

#### Konfigurisanje Hermesa za Telegram

Dodajte sledeće u `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Ne znate svoj Telegram korisnički ID?** Pošaljite poruku [@userinfobot](https://t.me/userinfobot) na Telegramu, odgovoriće vam sa vašim numeričkim ID-jem.

Zatim pokrenite gateway:

```bash
hermes gateway
```

Pošaljite botu bilo koju poruku na Telegramu da biste testirali. Sada možete da razgovarate sa svojim agentom putem Telegram direktnih poruka. Pogledajte [kompletan vodič za podešavanje Telegrama](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) za webhook režim i napredne opcije.

---

## Sledeći koraci

Sada kada vaš agent može da prima komande sa vašeg telefona i deluje na vašem lokalnom računaru, evo tri pravca koje vredi istražiti:

1. **Automatizovani izveštaj istraživanja**: Zakažite Hermes da svakog jutra pretražuje web za teme koje vas zanimaju, sumira nalaze pomoću vašeg lokalnog modela i pošalje izveštaj na vaš telefon putem Telegrama ili Discord-a, sve pokrenuto na vašem sopstvenom hardveru bez troškova za cloud.

2. **Pregled koda na zahtev**: Usmerite Hermes na GitHub repozitorijum, zamolite ga da pregleda otvorene pull request-ove i da objavi komentare ili sažetak nazad u vaš chat. Sa Docker terminal backend-om, sve git operacije se izvršavaju unutar sandbox-a, čime se vaš host čuva čistim.

3. **Lokalni asistent za fajlove**: Dajte Hermesu pristup radnom direktorijumu i zamolite ga da organizuje, preimenuje, sumira ili transformiše fajlove na zahtev sa vašeg telefona. Zbog toga što Docker terminal backend ograničava sva upisivanja na sandbox radni prostor, slučajne destruktivne operacije su ograničene.