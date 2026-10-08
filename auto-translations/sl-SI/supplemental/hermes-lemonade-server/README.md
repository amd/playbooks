<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Zagon agenta Hermes lokalno s strežnikom Lemonade

## Pregled

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) je samoizboljševalni agent umetne inteligence, ki ga je zgradil Nous Research. Ima vgrajeno zanko učenja, iz izkušenj ustvarja veščine, med sejami gradi trajen spomin o tem, kdo ste, in lahko v vašem imenu izvaja načrtovane avtomatizacije. Za razliko od preprostega klepetalnega asistenta Hermes dejansko izvaja dejanja: zaganja ukaze lupine, piše datoteke, brska po spletu in deli vzporedne delovne tokove na podagente.

[**Lemonade Server**](https://lemonade-server.ai/) je lokalni backend za sklepanje, ki poganja ta sistem. Gre za odprtokodni strežnik, ki modele GenAI zažene neposredno na vaši strojni opremi AMD in jih izpostavi prek standardnega API-ja OpenAI, uveljavljenega v panogi.

Skupaj tvorita popolnoma lokalen sklad agenta umetne inteligence: Lemonade obravnava sklepanje modela na vašem GPU-ju, Hermes pa zagotavlja zanko agenta, spomin, veščine in prehod za sporočanje.

> **Preden nadaljujete:** Hermes Agent je visoko avtonomen agent umetne inteligence. Omogočanje dostopa kateremu koli agentu umetne inteligence do vašega sistema lahko povzroči nepredvidljive ali nenamerne izide. Nadaljujte le, če razumete tveganja in vam je udobno z avtonomno programsko opremo, ki deluje v vašem imenu.

---

## Kaj se boste naučili

Ob koncu tega vodnika boste znali:

- **Namestiti Hermes Agent** in ga usmeriti na **Lemonade Server** kot svoj AI backend.
- **(Priporočeno) Omogočiti peskovnik Docker/Podman** za izolacijo dejanj agenta od gostiteljskega sistema.
- **Zagnati prehod Hermes** in potrditi, da je vaš agent pripravljen.
- **Povezati komunikacijski kanal** (Discord ali Telegram), da se boste lahko s svojim agentom pogovarjali iz katere koli naprave.

---

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

<!-- @os:linux -->
- Osebni računalnik z **Ubuntu 24.04+** ali združljivo distribucijo Linux na osnovi Debiana z `apt-get`
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- **~10–30 GB prostega prostora na disku** za uteži modela
- [Podman](https://podman.io/docs/installation) (izbirno, za peskovnik Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Osebni računalnik z **Windows 10/11**
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- **~10–30 GB prostega prostora na disku** za uteži modela
- Podman (izbirno, za peskovnik Hermes Agent). Namestite znotraj WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman je vnaprej nameščen na Halo Box in nastavitev ni potrebna
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Prenos in nalaganje priporočenega modela

Priporočeni model za ta vodnik je **Qwen3.6-35B-A3B-GGUF** podjetja Unsloth, zmogljiv model MoE z oknom konteksta 263k žetonov, ki je dobro primeren za delovne obremenitve agentov. Ta model uporablja kvantizacijo UD-Q4_K_XL. Prenesite ga zdaj:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Nato ga naložite z velikim oknom konteksta in to nastavitev shranite za prihodnje zagone:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Model ima privzeto dolžino konteksta 262.144 žetonov. Če naletite na napake zaradi pomanjkanja pomnilnika (OOM), razmislite o zmanjšanju okna konteksta.

> **Nasvet: Onemogočite razmišljanje za hitrejše odzive agenta:** Qwen3.6-35B-A3B privzeto deluje v načinu razmišljanja, kar pred vsakim odgovorom doda zakasnitev. Pri zankah agenta se ta dodatni čas hitro nabira. Repozitorij [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) ponuja pripravljeno konfiguracijo, ki onemogoči razmišljanje. Za uporabo prenesite datoteko in jo uvozite:
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

## Nastavitev WSL

Hermes Agent zaženemo znotraj WSL in ga povežemo z Lemonade, ki deluje izvorno na Windows. To vam omogoča okolje lupine Linux za Hermes, hkrati pa ohranja pospeševanje GPU-ja Lemonade na strani Windows.

### Namestitev WSL in Ubuntu

Odprite PowerShell kot skrbnik in namestite jedro WSL:

```powershell
wsl --install --no-distribution
```

Nato namestite Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogočanje systemd v WSL

Zaženite to znotraj terminala Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ponovno zaženite WSL:

```powershell
wsl --shutdown
wsl
```

### Premostitev Lemonade iz Windows v WSL

WSL2 deluje v navideznem omrežju. Lemonade na Windows se poveže na `127.0.0.1`, do katerega WSL ne more neposredno dostopati. Posredniški vmesnik za vrata v Windows posreduje promet z naslova prehoda WSL na lokalni gostitelj Windows.

**Poiščite naslov IP vašega prehoda WSL** (zaženite znotraj WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte posredniški vmesnik za vrata** (zaženite v PowerShell kot skrbnik, pri čemer `<WSL-Gateway-IP>` zamenjajte z naslovom IP vašega prehoda WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodajte pravilo požarnega zidu** (isti povišani PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Preverite iz WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Če ste v prejšnjem koraku že naložili model Qwen3.6-35B-A3B-GGUF, bi morali videti izhod JSON z izpisom vašega naloženega modela.

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

> Pravilo `netsh portproxy` preživi ponovne zagone, vendar se naslov IP prehoda WSL lahko spremeni po `wsl --shutdown`. Če Lemonade po ponovnem zagonu ni dosegljiv iz WSL, pridobite posodobljen naslov IP prehoda in posodobite posredniški vmesnik s tem novim naslovom.

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

## Namestitev Hermes Agent

<!-- @os:windows -->
> Ukaze v tem razdelku zaganjajte znotraj svojega terminala **WSL**, razen če je navedeno drugače.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Zastavica `--skip-setup` preskoči interaktivnega čarovnika za nastavitev, tako da lahko backend modela ročno konfigurirate v naslednjem koraku.

Ponovno naložite svojo lupino:

```bash
source ~/.bashrc
```

Potrdite namestitev:

```bash
hermes --version
```

Zaženite samodiagnostiko za preverjanje vseh odvisnosti:

```bash
hermes doctor
```

> **Nasvet:** Če po namestitvi vidite `command not found`, dodajte Hermes v svojo spremenljivko PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Za trajno nastavitev dodajte zgornjo vrstico v svoj `~/.bashrc` ali `~/.zshrc`.

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
## Konfigurirajte Hermes za uporabo Lemonade

Hermes shranjuje konfiguracijo modela v `~/.hermes/config.yaml`. Lahko uporabite interaktivni izbirnik `hermes model` ali pa konfiguracijo zapišete neposredno.

### Možnost 1: Interaktivni izbirnik

<!-- @os:windows -->
> Spodnji ukaz zaženite v svojem **WSL terminalu**.
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

Ko ste pozvani:

1. Izberite **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** uporabite IP naslov prehoda WSL: znotraj WSL zaženite `ip route show default | awk '{print $3}' | head -1`, da ga pridobite, nato vnesite `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** s seznama izberite `Qwen3.6-35B-A3B-GGUF`
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (ali poljubno ime po vaši izbiri)

`hermes model` shrani tako izbrani aktivni model kot poimenovan vnos `custom_providers`, ki skupaj s končno točko hrani tudi dolžino konteksta. Rezultat v `~/.hermes/config.yaml` je videti takole:

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

### Možnost 2: Neposreden zapis konfiguracije

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

Znotraj svojega WSL terminala pridobite IP naslov gostitelja Windows in zapišite konfiguracijo:

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

## (Priporočeno) Omogočite peskovnik Podman

Hermes Agent lahko vse operacije z lupino in datotekami agenta usmeri skozi izoliran vsebnik, namesto da jih izvaja neposredno na vašem gostitelju. To omeji domet morebitnega nenamernega dejanja na peskovnik, pri čemer datotečni sistem in omrežje vašega gostitelja ostaneta nedotaknjena.

Zgradite lahek vsebnik za peskovnik:

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
Odprite svoj WSL terminal:

```powershell
wsl -d Ubuntu-24.04
```

Nato zgradite lahek vsebnik za peskovnik:

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

Nato konfigurirajte Hermes za uporabo Podman kot izvajalnega okolja vsebnikov in nastavite zaledje terminala:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` je še vedno `docker`.
> `HERMES_DOCKER_BINARY` je tisto, kar Hermesu pove, naj namesto tega kot izvajalno okolje uporabi Podman.

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

Hermes bo zdaj zagnal trajen vsebnik peskovnika in skozenj usmeril vse klice orodij `terminal` in za delo z datotekami. Vsebnik si deli življenjsko dobo s procesom Hermes, se ponovno uporablja pri vseh klicih orodij in se uniči, ko se Hermes zapre.

> **Preverite, ali peskovnik deluje:** Zaženite Hermes (`hermes`) in ga prosite, naj `run hostname` - videti bi morali kratek ID vsebnika namesto imena gostitelja vašega računalnika. Prav tako ga lahko prosite, naj izvede `rm -rf <path-to-a-dummy-file/folder>`: Hermes bo potrdil izbris, mapa pa bo kljub temu ostala na vašem gostitelju. Ukaz je bil izveden znotraj izoliranega `$HOME` vsebnika, ne vašega.

> **Potrebujete močnejšo izolacijo?** Hermes ponuja tudi uradno Docker sliko (`nousresearch/hermes-agent`), ki celoten proces agenta zažene znotraj vsebnika - prehod, orodja in vse ostalo. Podrobnosti o namestitvi najdete v [dokumentaciji Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Priporočeno) Integracija Hermes s storitvami Firecrawl

Hermes lahko z vgrajenimi spletnimi orodji brska po spletnih mestih in iz njih pridobiva vsebino. Vendar številna sodobna spletna mesta uporabljajo sisteme za zaznavanje botov, ki blokirajo preproste zahteve HTTP in namesto dejanske vsebine vrnejo strani z izzivi. Posledično Hermes morda ne bo mogel zanesljivo pridobiti informacij s teh strani.

Za premagovanje te omejitve [Firecrawl](https://docs.firecrawl.dev/introduction) ponuja samostojno gostovano storitev spletnega pajkanja in pridobivanja vsebine, ki lahko obide te izzive in odklene polni potencial avtomatizacije Hermes.

V tej namestitvi Firecrawl deluje kot niz vsebnikov Docker, upravljanih s Podman. Za poenostavitev upravljanja življenjskega cikla in samodejnega zagona Firecrawl registriramo kot uporabniško storitev `systemd`, ki orkestrira osnovni sklad Podman Compose. To omogoča, da Hermes zaganja, ustavlja in preverja storitev Firecrawl s standardnimi ukazi `systemctl --user`, namesto da bi neposredno komunicarali z vsebniki.

Za preprostost smo celoten postopek razdelili na štiri korake:

---

### 1. Registracija sistemske storitve
Pomaknite se v mapo uporabniške konfiguracije systemd:
```bash
cd ~/.config/systemd/user
```
Ustvarite in odprite novo datoteko z imenom `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopirajte in prilepite naslednjo konfiguracijo:
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
Na tej točki je storitev definirana, vendar še ni registrirana v `systemd`. 
Poskrbite, da se ime datoteke natančno ujema s tistim, ki ste ga ustvarili zgoraj, nato zaženite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Če je uspešno, bi morali videti naslednji izpis:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` vsebuje simbolne povezave do storitev, ki so nastavljene za samodejni zagon.

### 2. Konfiguracija Firecrawl za vašo storitev

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealen za tiste, ki potrebujejo popoln nadzor nad svojim okoljem za pajkanje in obdelavo podatkov, vendar prinaša kompromis v obliki dodatnega vzdrževanja in konfiguracije.

Začnite s kloniranjem repozitorija:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Ustvarite `.env` v korenski mapi `/firecrawl`:
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
> Nastavite `BULL_AUTH_KEY` na močno skrivnost, še posebej pri kakršni koli namestitvi, dostopni iz nezaupanja vrednih omrežij.
### 3. Namestitev storitve Hermes prek Compose

Preden nadaljujete, se prepričajte, da ste povlekli najnovejšo Docker sliko Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Ko je to opravljeno, prenesite datoteko Compose za Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) in jo postavite v korenski imenik `/firecrawl`:

> Ta konvencija je potrebna, da lahko `systemd` pravilno najde in zažene storitev, kot je določeno v `WorkingDirectory=${HOME}/firecrawl`.

> Sklad lahko kadar koli razširite z dodajanjem dodatnih storitev Firecrawl po potrebi. Celoten seznam razpoložljivih storitev najdete v uradnem [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Zagon storitve Hermes prek Firecrawl

Preden prepustite nadzor `systemd`, preverite, ali vse deluje pravilno, tako da sklad zaženete ročno:
```bash
podman compose -f hermes-compose.yaml up -d
```
Če je vse pravilno nastavljeno, bi morali videti, da se vsebnik Hermes zažene, izhod ukazne vrstice pa bi moral izgledati približno takole:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Ko ste preverili, sklad znova zaustavite, preden nadaljujete:
```bash
podman compose -f hermes-compose.yaml down
```
Zdaj, ko je vse preverjeno, zaženite storitev prek `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) je dostopen znotraj interaktivnega vsebnika, spletna nadzorna plošča pa je na voljo na istem gostitelju in vratih na http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Za zaustavitev storitve zaženite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Zaženite interaktivno sejo CLI neposredno:

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

**Čestitamo, zgradili ste popolnoma lokalen sklad AI agenta.**

### Spletna nadzorna plošča

Hermes vključuje uporabniški vmesnik v brskalniku za upravljanje konfiguracije, API ključev, modelov, sej, pomnilnika in cron opravil. Medtem ko gateway ali CLI deluje, odprite drugi terminal in ga zaženite z:

```bash
hermes dashboard
```

S tem se zažene lokalni strežnik in v brskalniku odpre `http://127.0.0.1:9119`. Za celoten pregled funkcij glejte [dokumentacijo nadzorne plošče](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Izbirno: Povežite komunikacijski kanal

Ko gateway deluje, lahko do svojega lokalnega agenta dostopate iz katere koli naprave. Hermes podpira [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) in druge

---

### Discord

Discord zahteva strežnik, na katerem **imate skrbniški dostop**, da lahko dodate bota. Če si strežnike delite, vendar niste njihov lastnik, namesto tega uporabite Telegram.

#### Ustvarjanje Discord aplikacije in bota

1. Odprite [Discord Developer Portal](https://discord.com/developers/applications) in kliknite **New Application**. Vnesite ime (npr. »hermes-bot«).
2. V stranski vrstici kliknite **Bot**. Nastavite uporabniško ime bota.
3. Še vedno na strani Bot se pomaknite do **Privileged Gateway Intents** in omogočite:
   - **Message Content Intent** (obvezno)
   - **Server Members Intent** (priporočeno)
4. Pomaknite se nazaj navzgor in kliknite **Reset Token**, da ustvarite žeton bota. Kopirajte ga.

#### Dodajanje bota na svoj strežnik

1. V stranski vrstici kliknite **OAuth2 / URL Generator**.
2. Pod **Scopes** omogočite `bot` in `applications.commands`.
3. Pod **Bot Permissions** omogočite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte ustvarjeni URL, prilepite ga v brskalnik, izberite svoj strežnik in potrdite.

#### Pridobitev ID-jev in omogočanje zasebnih sporočil

Omogočite razvijalski način v Discordu (**User Settings / Advanced / Developer Mode**), nato:
- Z desnim klikom na ikono strežnika: **Copy Server ID**
- Z desnim klikom na lastni avatar: **Copy User ID**

Z desnim klikom na ikono strežnika / **Privacy Settings** / vklopite **Direct Messages**. To je potrebno za korak seznanjanja.

#### Konfiguracija Hermes za Discord

Dodajte naslednje v `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Nato zaženite gateway:

```bash
hermes gateway
```

Bot bi se moral v Discordu pojaviti kot povezan v nekaj sekundah. Pošljite mu sporočilo, bodisi zasebno sporočilo bodisi v kanalu, ki ga lahko vidi.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Ustvarjanje Telegram bota

1. Odprite Telegram in pošljite sporočilo **@BotFather**.
2. Pošljite `/newbot` in sledite navodilom. Shranite žeton bota, ki ga prejmete.

#### Konfiguracija Hermes za Telegram

Dodajte naslednje v `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Ne poznate svojega ID-ja uporabnika Telegram?** Pošljite sporočilo [@userinfobot](https://t.me/userinfobot) v Telegramu, odgovoril vam bo z vašim številčnim ID-jem.

Nato zaženite gateway:

```bash
hermes gateway
```

Za preizkus pošljite svojemu botu poljubno sporočilo v Telegramu. Zdaj se lahko s svojim agentom pogovarjate prek zasebnih sporočil Telegram. Za način webhook in napredne možnosti glejte [celoten vodnik za nastavitev Telegrama](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Naslednji koraki

Zdaj, ko lahko vaš agent prejema ukaze iz vašega telefona in deluje na vašem lokalnem računalniku, so tukaj tri smeri, ki jih velja raziskati:

1. **Samodejni povzetek raziskav**: Nastavite Hermes, naj vsako jutro prebrska splet za teme, ki vas zanimajo, povzame ugotovitve z vašim lokalnim modelom in pošlje povzetek na vaš telefon prek Telegrama ali Discorda, vse to pa deluje na vaši lastni strojni opremi brez stroškov v oblaku.

2. **Pregled kode na zahtevo**: Usmerite Hermes na repozitorij GitHub, prosite ga, naj pregleda odprte pull requeste, ter naj objavi komentarje ali povzetek nazaj v vaš klepet. Z zaledjem Docker terminala vse git operacije potekajo znotraj peskovnika, kar ohranja vaš gostiteljski sistem čist.

3. **Lokalni pomočnik za datoteke**: Omogočite Hermesu dostop do delovnega imenika in ga prosite, naj na zahtevo iz vašega telefona organizira, preimenuje, povzame ali pretvori datoteke. Ker zaledje Docker terminala omeji vsa pisanja na delovni prostor peskovnika, so morebitne nenamerne destruktivne operacije omejene.