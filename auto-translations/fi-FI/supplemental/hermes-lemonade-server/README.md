<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Hermes Agentin ajaminen paikallisesti Lemonade Serverin avulla

## Yleiskatsaus

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) on Nous Researchin rakentama itseään parantava tekoälyagentti. Siinä on sisäänrakennettu oppimissilmukka, se luo taitoja kokemuksesta, rakentaa pysyvän muistin siitä, kuka olet istuntojen välillä, ja voi suorittaa ajastettuja automaatioita puolestasi. Toisin kuin yksinkertainen chat-avustaja, Hermes tekee todellisia toimia: suorittaa komentotulkin komentoja, kirjoittaa tiedostoja, selaa verkkoa ja delegoi rinnakkaisia työnkulkuja aliagenteille.

[**Lemonade Server**](https://lemonade-server.ai/) on paikallinen päättelymoottori, joka toimii sen taustalla. Se on avoimen lähdekoodin palvelin, joka ajaa GenAI-malleja suoraan AMD-laitteistollasi ja tarjoaa niitä alan standardin mukaisen OpenAI API:n kautta.

Yhdessä ne muodostavat täysin paikallisen tekoälyagenttipinon: Lemonade huolehtii mallien päättelystä GPU:llasi, ja Hermes tarjoaa agenttisilmukan, muistin, taidot ja viestintäyhdyskäytävän.

> **Ennen kuin jatkat:** Hermes Agent on erittäin autonominen tekoälyagentti. Minkä tahansa tekoälyagentin päästäminen käsiksi järjestelmääsi voi johtaa arvaamattomiin tai tahattomiin lopputuloksiin. Jatka vain, jos ymmärrät riskit ja hyväksyt sen, että autonominen ohjelmisto toimii puolestasi.

---

## Mitä opit

Tämän oppaan lopussa osaat:

- **Asentaa Hermes Agentin** ja määrittää sen käyttämään **Lemonade Serveria** tekoälytaustajärjestelmänään.
- **(Suositeltu) Ottaa käyttöön Docker/Podman-hiekkalaatikoinnin**, jotta agentin toimet eristetään isäntäjärjestelmästäsi.
- **Käynnistää Hermes-yhdyskäytävän** ja varmistaa, että agenttisi on valmis.
- **Yhdistää viestintäkanavan** (Discord tai Telegram), jotta voit keskustella agenttisi kanssa mistä tahansa laitteesta.

---

## Muistin määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

<!-- @os:linux -->
- PC, jossa on **Ubuntu 24.04+** tai yhteensopiva Debian-pohjainen Linux-jakelu, jossa on `apt-get`
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- **Noin 10–30 Gt vapaata levytilaa** malliparametreille
- [Podman](https://podman.io/docs/installation) (valinnainen, Hermes Agentin hiekkalaatikointia varten)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- PC, jossa on **Windows 10/11**
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- **Noin 10–30 Gt vapaata levytilaa** malliparametreille
- Podman (valinnainen, Hermes Agentin hiekkalaatikointia varten). Asenna WSL:n sisällä:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman on esiasennettu Halo Boxiin, eikä sitä tarvitse erikseen asentaa
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Suositellun mallin lataaminen ja käyttöönotto

Tähän oppaaseen suositeltu malli on Unslothin **Qwen3.6-35B-A3B-GGUF**, vahva MoE-malli, jossa on 263 000 tokenin kontekstiikkuna ja joka soveltuu hyvin agenttityökuormiin. Tämä malli käyttää UD-Q4_K_XL-kvantisointia. Lataa se nyt:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Lataa se sitten suurella kontekstiikkunalla ja tallenna tämä asetus tulevia ajokertoja varten:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Mallin oletuskontekstipituus on 262 144 tokenia. Jos kohtaat muistin loppumiseen liittyviä (OOM) virheitä, harkitse kontekstiikkunan pienentämistä.

> **Vihje: Poista ajattelu käytöstä nopeampia agenttivastauksia varten:** Qwen3.6-35B-A3B toimii oletuksena ajattelutilassa, mikä lisää viivettä ennen jokaista vastausta. Agenttisilmukoissa tämä lisäkuormitus kertyy nopeasti. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) -tietovarastosta löytyy valmis konfiguraatio, joka poistaa ajattelun käytöstä. Käyttääksesi sitä, lataa tiedosto ja tuo se:
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

## WSL:n asettaminen

Ajamme Hermes Agentin WSL:n sisällä ja yhdistämme sen Windowsissa natiivisti ajettavaan Lemonadeen. Tämä tarjoaa sinulle Linux-komentotulkkiympäristön Hermesille säilyttäen samalla Lemonaden GPU-kiihdytyksen Windows-puolella.

### WSL:n ja Ubuntun asentaminen

Avaa PowerShell järjestelmänvalvojana ja asenna WSL-ydin:

```powershell
wsl --install --no-distribution
```

Asenna sitten Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Systemd:n ottaminen käyttöön WSL:ssä

Suorita tämä Ubuntu-terminaalin sisällä:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Käynnistä WSL uudelleen:

```powershell
wsl --shutdown
wsl
```

### Lemonaden sillan luominen Windowsista WSL:ään

WSL2 toimii virtuaalisessa verkossa. Windowsissa Lemonade sitoutuu osoitteeseen `127.0.0.1`, jota WSL ei voi tavoittaa suoraan. Windowsin porttivälityspalvelin (port proxy) välittää liikennettä WSL-yhdyskäytävän IP-osoitteesta Windowsin localhostiin.

**Etsi WSL-yhdyskäytävän IP-osoite** (suorita WSL:n sisällä):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lisää porttivälitys** (suorita PowerShellissä järjestelmänvalvojana, korvaa `<WSL-Gateway-IP>` WSL-yhdyskäytäväsi IP-osoitteella):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Lisää palomuurisääntö** (samassa korotetuin oikeuksin avatussa PowerShellissä):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vahvista WSL:stä**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jos olet jo ladannut Qwen3.6-35B-A3B-GGUF-mallin edellisessä vaiheessa, näet JSON-tulosteen, joka listaa ladatun mallisi.

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

> `netsh portproxy` -sääntö säilyy uudelleenkäynnistysten yli, mutta WSL-yhdyskäytävän IP-osoite voi muuttua `wsl --shutdown` -komennon jälkeen. Jos Lemonade ei ole tavoitettavissa WSL:stä uudelleenkäynnistyksen jälkeen, hae päivitetty yhdyskäytävän IP-osoite ja päivitä välityspalvelin uudella osoitteella.

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

## Hermes Agentin asentaminen

<!-- @os:windows -->
> Suorita tässä osiossa annetut komennot **WSL-terminaalissasi**, ellei toisin mainita.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup`-lippu ohittaa interaktiivisen asennusvelhon, jotta voit määrittää malliin liittyvän taustajärjestelmän manuaalisesti seuraavassa vaiheessa.

Lataa komentotulkkisi uudelleen:

```bash
source ~/.bashrc
```

Vahvista asennus:

```bash
hermes --version
```

Suorita itsediagnostiikka tarkistaaksesi kaikki riippuvuudet:

```bash
hermes doctor
```

> **Vihje:** Jos näet asennuksen jälkeen ilmoituksen `command not found`, lisää Hermes PATH-muuttujaasi:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Tehdäksesi tästä pysyvän, lisää yllä oleva rivi tiedostoosi `~/.bashrc` tai `~/.zshrc`.

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
## Määritä Hermes käyttämään Lemonadea

Hermes tallentaa mallikokoonpanonsa tiedostoon `~/.hermes/config.yaml`. Voit joko käyttää interaktiivista `hermes model`-valitsinta tai kirjoittaa kokoonpanon suoraan.

### Vaihtoehto 1: Interaktiivinen valitsin

<!-- @os:windows -->
> Suorita seuraava komento **WSL-päätteessä**.
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

Kun sinulta kysytään:

1. Valitse **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** käytä WSL:n yhdyskäytävän IP-osoitetta: aja `ip route show default | awk '{print $3}' | head -1` WSL:ssä saadaksesi sen, ja syötä sitten `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** valitse `Qwen3.6-35B-A3B-GGUF` listalta
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (tai mikä tahansa haluamasi nimi)

`hermes model` tallentaa sekä aktiivisen mallivalinnan että nimetyn `custom_providers`-merkinnän, joka säilyttää kontekstin pituuden yhdessä päätepisteen kanssa. Tulos tiedostossa `~/.hermes/config.yaml` näyttää tältä:

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

### Vaihtoehto 2: Kirjoita kokoonpano suoraan

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

Hae WSL-päätteessä Windows-isäntäkoneen IP-osoite ja kirjoita kokoonpano:

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

## (Suositeltu) Ota käyttöön Podman-hiekkalaatikointi

Hermes Agent voi reitittää kaikki agentin komentotulkki- ja tiedostotoiminnot eristetyn kontin kautta sen sijaan, että ne suoritettaisiin suoraan isäntäkoneella. Tämä rajoittaa mahdollisten tahattomien toimintojen vaikutusalueen hiekkalaatikkoon, jättäen isäntäkoneen tiedostojärjestelmän ja verkon koskemattomiksi.

Rakenna kevyt hiekkalaatikkokuva:

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
Siirry WSL-päätteeseen:

```powershell
wsl -d Ubuntu-24.04
```

Rakenna sitten kevyt hiekkalaatikkokuva:

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

Määritä sitten Hermes käyttämään Podmania konttien suoritusympäristönä ja aseta pääteohjelman taustajärjestelmä:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend`-asetus on edelleen `docker`.
> `HERMES_DOCKER_BINARY` on se, joka kertoo Hermekselle, että Podmania käytetään suoritusympäristönä Dockerin sijaan.

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

Hermes käynnistää nyt pysyvän hiekkalaatikkokontin ja reitittää kaikki `terminal`- ja tiedostotyökalukutsut sen kautta. Kontti jakaa Hermes-prosessin elinkaaren, sitä käytetään uudelleen kaikissa työkalukutsuissa, ja se tuhotaan, kun Hermes sammuu.

> **Varmista, että hiekkalaatikko toimii:** Käynnistä Hermes (`hermes`) ja pyydä sitä suorittamaan `run hostname` - sinun pitäisi nähdä lyhyt kontin tunniste koneesi isäntänimen sijaan. Voit myös pyytää sitä suorittamaan `rm -rf <path-to-a-dummy-file/folder>`: Hermes vahvistaa poiston, mutta kansio on edelleen isäntäkoneellasi. Komento suoritettiin kontin eristetyssä `$HOME`-kansiossa, ei sinun kansiossasi.

> **Tarvitsetko vahvempaa eristystä?** Hermes tarjoaa myös virallisen Docker-kuvan (`nousresearch/hermes-agent`), joka suorittaa koko agenttiprosessin kontin sisällä - yhdyskäytävän, työkalut ja kaiken muun. Katso lisätietoja asennuksesta [Hermeksen Docker-dokumentaatiosta](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Suositeltu) Hermeksen integrointi Firecrawl-palveluihin

Hermes voi selata ja poimia sisältöä verkkosivustoilta sisäänrakennettujen verkkotyökalujensa avulla. Monet nykyaikaiset verkkosivustot käyttävät kuitenkin bottien tunnistusjärjestelmiä, jotka estävät yksinkertaiset HTTP-pyynnöt ja palauttavat varsinaisen sisällön sijaan haastesivuja. Tämän seurauksena Hermes ei ehkä pysty luotettavasti poimimaan tietoa näiltä sivustoilta.

Tämän rajoituksen voittamiseksi [Firecrawl](https://docs.firecrawl.dev/introduction) tarjoaa itse isännöidyn verkkosisällön keräys- ja poimintapalvelun, joka voi ohittaa nämä haasteet ja vapauttaa Hermes-automaation koko potentiaalin.

Tässä asennuksessa Firecrawl toimii joukkona Docker-kontteja, joita hallitaan Podmanilla. Elinkaarenhallinnan ja automaattisen käynnistyksen yksinkertaistamiseksi rekisteröimme Firecrawlin käyttäjätason `systemd`-palveluna, joka orkestroi taustalla olevaa Podman Compose -pinoa. Tämä mahdollistaa sen, että Hermes voi käynnistää, pysäyttää ja tarkistaa Firecrawl-palvelun tavallisilla `systemctl --user`-komennoilla ilman suoraa vuorovaikutusta konttien kanssa.

Asian yksinkertaistamiseksi olemme jakaneet koko prosessin neljään vaiheeseen:

---

### 1. Rekisteröi järjestelmäpalvelu
Siirry systemd-käyttäjäkokoonpanon hakemistoon:
```bash
cd ~/.config/systemd/user
```
Luo ja avaa uusi tiedosto nimeltä `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopioi ja liitä seuraava kokoonpano:
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
Tässä vaiheessa palvelu on määritelty, mutta ei vielä rekisteröity `systemd`:lle.
Varmista, että tiedostonimi vastaa täsmälleen edellä luomaasi tiedostoa, ja suorita sitten:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Jos onnistut, näet seuraavan tulosteen:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/`-kansio sisältää symbolisia linkkejä palveluihin, jotka on määritetty käynnistymään automaattisesti.

### 2. Määritä Firecrawl palveluasi varten

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) sopii ihanteellisesti niille, jotka tarvitsevat täyden hallinnan kaavinta- ja tietojenkäsittely-ympäristöihinsä, mutta se vaatii vastineeksi lisää ylläpitoa ja määritystyötä.

Aloita kloonaamalla arkisto:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Luo `.env`-tiedosto juurihakemistoon `/firecrawl`:
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
> Aseta `BULL_AUTH_KEY` vahvaksi salaisuudeksi, erityisesti jos käyttöönotto on saavutettavissa epäluotettavista verkoista.
### 3. Hermeksen käyttöönotto Compose-määrittelyllä

Ennen kuin jatkat, varmista, että olet noutanut uusimman Hermes-Docker-imagen:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Kun tämä on tehty, lataa Hermeksen Compose-tiedosto [hermes-compose.yaml](assets/hermes-compose.yaml) ja sijoita se `/firecrawl`-juurihakemistoon:

> Tämä käytäntö on tarpeen, jotta `systemd` löytää palvelun ja pystyy käynnistämään sen oikein, kuten on määritetty kohdassa `WorkingDirectory=${HOME}/firecrawl`.

> Voit aina laajentaa pinoa lisäämällä tarvittaessa muita Firecrawl-palveluita. Täydellinen luettelo saatavilla olevista palveluista löytyy virallisesta [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) -tiedostosta.

### 4. Hermes-palvelun käynnistäminen Firecrawlin kautta 

Ennen kuin annat hallinnan `systemd`:lle, varmista manuaalisesti pinon käynnistämisellä, että kaikki toimii oikein:
```bash
podman compose -f hermes-compose.yaml up -d
```
Jos kaikki on määritetty oikein, näet Hermes-säiliön käynnistyvän, ja komentorivin tuloste näyttää suunnilleen tältä:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Kun olet tarkistanut tämän, sammuta pino ennen jatkamista:
```bash
podman compose -f hermes-compose.yaml down
```
Nyt kun kaikki on todennettu, käynnistä palvelu `systemd`:n kautta:
```bash
systemctl --user start firecrawl.service
```
[Hermes-API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) on käytettävissä interaktiivisen säiliön sisältä, ja verkkohallintapaneeli on saatavilla samalla isännällä ja portissa osoitteessa http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Pysäytä palvelu suorittamalla:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Käynnistä interaktiivinen komentorivi-istunto suoraan: 

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

**Onnittelut, olet rakentanut täysin paikallisen tekoälyagenttipinon.**

### Verkkohallintapaneeli

Hermes sisältää selainpohjaisen käyttöliittymän asetusten, API-avainten, mallien, istuntojen, muistin ja cron-tehtävien hallintaan. Avaa toinen pääte yhdyskäytävän tai CLI:n ollessa käynnissä ja käynnistä se komennolla:

```bash
hermes dashboard
```

Tämä käynnistää paikallisen palvelimen ja avaa osoitteen `http://127.0.0.1:9119` selaimessasi. Katso [hallintapaneelin dokumentaatio](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) täydellistä ominaisuusviittausta varten.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Valinnainen: Yhdistä viestintäkanava

Kun yhdyskäytävä on käynnissä, voit tavoittaa paikallisen agenttisi miltä tahansa laitteelta. Hermes tukee [Discordia](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegramia](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) ja muita

---

### Discord

Discord edellyttää palvelinta, jossa **sinulla on pääkäyttäjän oikeudet** botin lisäämiseksi. Jos olet vain jäsenenä palvelimilla mutta et omista yhtään, käytä sen sijaan Telegramia.

#### Luo Discord-sovellus ja botti

1. Siirry [Discordin kehittäjäportaaliin](https://discord.com/developers/applications) ja valitse **New Application**. Anna sille nimi (esim. "hermes-bot").
2. Napsauta sivupalkista **Bot**. Aseta botille käyttäjänimi.
3. Vieritä yhä Bot-sivulla kohtaan **Privileged Gateway Intents** ja ota käyttöön:
   - **Message Content Intent** (pakollinen)
   - **Server Members Intent** (suositeltu)
4. Vieritä takaisin ylös ja valitse **Reset Token** luodaksesi bottisi tunnuksen. Kopioi se.

#### Lisää botti palvelimellesi

1. Napsauta sivupalkista **OAuth2 / URL Generator**.
2. Kohdassa **Scopes** ota käyttöön `bot` ja `applications.commands`.
3. Kohdassa **Bot Permissions** ota käyttöön: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopioi luotu URL-osoite, liitä se selaimeesi, valitse palvelimesi ja vahvista.

#### Kerää tunnisteesi ja salli yksityisviestit

Ota käyttöön Discordin kehittäjätila (**User Settings / Advanced / Developer Mode**) ja tee sitten seuraavaa:
- Napsauta hiiren oikealla palvelimesi kuvaketta: **Copy Server ID**
- Napsauta hiiren oikealla omaa profiilikuvaasi: **Copy User ID**

Napsauta hiiren oikealla palvelimesi kuvaketta / **Privacy Settings** / kytke päälle **Direct Messages**. Tämä vaaditaan pariutusvaihetta varten.

#### Määritä Hermes Discordia varten

Lisää seuraava tiedostoon `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Käynnistä sitten yhdyskäytävä:

```bash
hermes gateway
```

Botin pitäisi tulla Discordissa verkkoon muutamassa sekunnissa. Lähetä sille viesti joko yksityisviestinä tai kanavalla, jonka se näkee.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Luo Telegram-botti

1. Avaa Telegram ja lähetä viesti käyttäjälle **@BotFather**.
2. Lähetä `/newbot` ja seuraa ohjeita. Tallenna botin tunnus, jonka se antaa.

#### Määritä Hermes Telegramia varten

Lisää seuraava tiedostoon `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Etkö tiedä Telegram-käyttäjätunnustasi?** Lähetä viesti käyttäjälle [@userinfobot](https://t.me/userinfobot) Telegramissa, se vastaa numeerisella tunnuksellasi.

Käynnistä sitten yhdyskäytävä:

```bash
hermes gateway
```

Testaa lähettämällä botillesi mikä tahansa viesti Telegramissa. Voit nyt keskustella agenttisi kanssa Telegram-yksityisviesteillä. Katso [täydellinen Telegram-määritysopas](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) webhook-tilaa ja lisäasetuksia varten.

---

## Seuraavat vaiheet

Nyt kun agenttisi voi vastaanottaa komentoja puhelimestasi ja toimia paikallisella koneellasi, tässä on kolme suuntaa, joita kannattaa tutkia:

1. **Automatisoitu tutkimuskooste**: Ajasta Hermes hakemaan verkosta tietoa sinua kiinnostavista aiheista joka aamu, tiivistämään löydökset paikallisella mallillasi ja lähettämään kooste puhelimeesi Telegramin tai Discordin kautta, kaikki toimien omalla laitteistollasi ilman pilvikustannuksia.

2. **Koodikatselmointi tarpeen mukaan**: Osoita Hermes GitHub-repositorioon, pyydä sitä katselmoimaan avoimet pull requestit ja anna sen lähettää kommentteja tai yhteenveto takaisin keskusteluusi. Docker-pääteohjelman ansiosta kaikki git-toiminnot suoritetaan hiekkalaatikossa, mikä pitää isäntäkoneesi puhtaana.

3. **Paikallinen tiedostoavustaja**: Anna Hermekselle pääsy työhakemistoon ja pyydä sitä järjestämään, nimeämään uudelleen, tiivistämään tai muuntamaan tiedostoja tarpeen mukaan puhelimestasi käsin. Koska Docker-pääteohjelma rajaa kaikki kirjoitustoiminnot hiekkalaatikkotyötilaan, vahingossa tapahtuvat tuhoisat toiminnot pysyvät hallinnassa.